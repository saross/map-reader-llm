
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from pathlib import Path
import rasterio
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import TILES_DIR, INPUTS_DIR

def evaluate_full():
    det_path = "outputs/results/detections-visual-2025-12-17-3-pro.geojson"
    if not Path(det_path).exists():
        print("Detections file not found.")
        return

    print("Loading detections...")
    det_gdf = gpd.read_file(det_path)
    print(f"Total Raw Detections: {len(det_gdf)}")
    
    # 1. Edge Exclusion Filter (50m)
    print("Applying 50m Edge Exclusion...")
    
    # Cache tile geometries to speed up
    # We need to parse 'source_tile' to get bounds
    # Tile filename format: K-35-052-4_32635_x0_y0.png
    # But we also have the TILE files in TILES_DIR. We can read their bounds.
    
    # Group by tile to minimize file I/O
    keep_indices = []
    
    for tile_name, group in det_gdf.groupby('source_tile'):
        # Find tile limits
        # Extract x, y from filename or read file?
        # Reading file is safer but slower. 
        # Filename: ..._x{min_x}_y{min_y}.png
        # Wait, the filenames in TILES_DIR are just name.png.
        # But 'source_tile' in the geojson is the filanem.
        # Note: preprocess_tiling.py writes tiles as {map_name}_x{col}_y{row}.png
        # These are pixel offsets.
        # BUT the detections are already in EPSG:32635 (Projected).
        # So we need the projected bounds of the tile.
        
        # Fast way: Read the tile using rasterio
        # Search for tile in TILES_DIR (recursive)
        # Or assumes we know where they are.
        # analyze_partial used a finder loop.
        
        # Let's try to assume map name implies directory.
        map_name_mapping = {
            "32635": "K-35-052-4_32635",
            "Elenovo": "K-35-053-3_Elenovo",
            "Rakovski": "K-35-062-2_Rakovski", 
            "Lesovo": "K-35-078-1_Lesovo"
        }
        
        # Find map key
        map_key = None
        for k, v in map_name_mapping.items():
            if k in tile_name:
                map_key = v
                break
        
        if not map_key:
            print(f"Could not map tile {tile_name} to a folder.")
            continue
            
        tile_path = TILES_DIR / map_key / tile_name
        if not tile_path.exists():
            # Try raw TILES_DIR (if flat structure? No, listing showed subdirs)
            # Find it
            found = list(TILES_DIR.glob(f"**/{tile_name}"))
            if found:
                tile_path = found[0]
            else:
                print(f"Tile file {tile_name} not found.")
                continue
                
        # Get bounds
        with rasterio.open(tile_path) as src:
            bounds = src.bounds
            tile_poly = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
            
        # Check distances
        # Vectorized check
        # Geopandas distance to boundary
        # boundary is linestring
        boundary = tile_poly.boundary
        
        group_distances = group.geometry.centroid.distance(boundary)
        valid_mask = group_distances >= 50
        keep_indices.extend(group.loc[valid_mask].index.tolist())

    filtered_gdf = det_gdf.loc[keep_indices].copy()
    print(f"Detections after Edge Exclusion: {len(filtered_gdf)}")
    
    # 2. Deduplication (Merge Overlaps)
    # Simple strategy: Buffer centroids by small amount, dissolve?
    # Better: If IoU > 0.5?
    # Or strict spatial clustering.
    # Since these are mounds (small points), if two detections are within X meters, they are the same.
    # Average mound size ~20-50m.
    # If centroids are within 20m, merge.
    
    print("Deduplicating...")
    # Buffer by 10m -> Interact -> Dissolve -> Centroid
    # This merges points within 20m of each other.
    buf = filtered_gdf.geometry.centroid.buffer(10)
    merged = gpd.GeoDataFrame(geometry=buf, crs=filtered_gdf.crs).unary_union
    
    # Explode back to individual polygons
    if merged.geom_type == 'MultiPolygon':
        merged_polys = list(merged.geoms)
    else:
        merged_polys = [merged]
        
    deduped_gdf = gpd.GeoDataFrame(geometry=[p.centroid for p in merged_polys], crs=filtered_gdf.crs)
    print(f"Final Deduplicated Count: {len(deduped_gdf)}")
    
    # 3. Evaluation against Reference
    # Load References
    ref_files = list(INPUTS_DIR.glob("reference_*.geojson"))
    
    print("\n--- RESULTS BY MAP ---")
    
    for ref_file in ref_files:
        ref_name = ref_file.stem.replace("reference_", "") # K-35-052-4_32635
        
        # Load Ref
        ref_gdf = gpd.read_file(ref_file)
        if ref_gdf.crs != "EPSG:32635": ref_gdf = ref_gdf.to_crs("EPSG:32635")
        
        # Filter De-duped detections to this map area
        # We can use the Reference Convex Hull as the map area? 
        # Or just spatially join.
        
        # Filter Detections by spatial intersection with Full Map Ref Bounds (buffered by large amount to catch outliers)
        map_boundary = ref_gdf.unary_union.envelope.buffer(2000) 
        det_on_map = deduped_gdf[deduped_gdf.intersects(map_boundary)]
        
        if len(det_on_map) == 0:
            print(f"[{ref_name}] No detections found (or map not processed).")
            continue
            
        # TP/FP/FN Logic
        # Buffer refs by 20m (Evaluation standard)
        ref_eval_geom = ref_gdf.geometry.buffer(20)
        ref_eval_gdf = gpd.GeoDataFrame(geometry=ref_eval_geom, crs=ref_gdf.crs)
        
        # TP: Detection intersects buffered Ref
        # Join Det -> Ref
        join_tp = gpd.sjoin(det_on_map, ref_eval_gdf, how='inner', predicate='intersects')
        tp_count = len(join_tp.index.unique())
        
        # FP: Detection NOT intersect buffered Ref
        fp_count = len(det_on_map) - tp_count
        
        # FN: Ref NOT intersected by Detection
        # Join Ref -> Det (Buffer Det or Point-in-Poly?)
        # Evaluator usually buffers Ref.
        # Check which Refs were hit.
        hit_refs = join_tp['index_right'].unique()
        fn_count = len(ref_gdf) - len(hit_refs)
        
        precision = tp_count / (tp_count + fp_count) if (tp_count + fp_count) > 0 else 0
        recall = tp_count / (tp_count + fn_count) if (tp_count + fn_count) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\nMAP: {ref_name}")
        print(f"  TP: {tp_count}")
        print(f"  FP: {fp_count}")
        print(f"  FN: {fn_count}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1 Score:  {f1:.4f}")

if __name__ == "__main__":
    evaluate_full()
