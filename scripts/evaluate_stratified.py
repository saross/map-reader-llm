
import json
import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd
import sys
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import INPUTS_DIR

def get_map_name(tile_filename):
    # Extracts map name from tile filename
    # Format: {MAP_NAME}_x{...}_y{...}.png
    # But MAP_NAME can contain underscores.
    # We know the specific map names, so we can match them.
    known_maps = [
        "K-35-062-2_Rakovski",
        "K-35-052-4_32635",
        "K-35-053-3_Elenovo",
        "K-35-078-1_Lesovo"
    ]
    for m in known_maps:
        if tile_filename.startswith(m):
            return m
    # Fallback/Guess if unknown format
    return "Unknown"

def evaluate_stratified(detection_file, bounds_file=None, buffer_meters=20, edge_exclusion=0):
    print(f"--- Stratified Evaluation ---")
    print(f"Detections: {detection_file}")
    if bounds_file:
        print(f"Bounds: {bounds_file}")

    # Load Detections
    try:
        gdf_det = gpd.read_file(detection_file)
        print(f"Loaded {len(gdf_det)} detections.")
    except Exception as e:
        print(f"Error loading detections: {e}")
        return

    # Load Bounds if provided
    gdf_bounds = None
    if bounds_file:
        try:
            gdf_bounds = gpd.read_file(bounds_file)
            print(f"Loaded {len(gdf_bounds)} tile bounds.")
        except Exception as e:
            print(f"Error loading bounds: {e}")
            return

    # Infer Map name for each detection
    gdf_det['Map'] = gdf_det['source_tile'].apply(get_map_name)

    # Load all Reference Maps
    ref_files = list(INPUTS_DIR.glob("reference_*.geojson"))
    ref_gdfs = []
    for rf in ref_files:
        gdf = gpd.read_file(rf)
        # Ensure CRS
        if gdf.crs != "EPSG:32635":
            gdf = gdf.to_crs("EPSG:32635")
        
        # Ensure Map Name is consistent (extracted from filename or properties)
        # The file is 'reference_{MAP_NAME}.geojson'
        map_name_from_file = rf.stem.replace("reference_", "")
        gdf['Map'] = map_name_from_file 
        # Note: The 'Map' property inside GeoJSON might be there too, but this is safer for grouping.
        
        # Buffer geometries
        gdf['geometry'] = gdf.geometry.buffer(buffer_meters)
        
        ref_gdfs.append(gdf)
    
    if not ref_gdfs:
        print("No reference files found!")
        return
        
    gdf_ref_all = pd.concat(ref_gdfs, ignore_index=True)
    print(f"Loaded {len(gdf_ref_all)} reference mounds across {len(ref_files)} maps.")
    
    # Ensure Det CRS
    target_crs = "EPSG:32635"
    if gdf_det.crs != target_crs:
        gdf_det = gdf_det.to_crs(target_crs)

    # We evaluate Per Map
    unique_maps = gdf_det['Map'].unique()
    
    global_tp = 0
    global_fp = 0
    global_fn = 0
    
    print("\n--- Per-Map Results ---")
    
    # Iterate over KNOWN maps (not just detected ones, to catch Empty maps/100% False Negatives)
    all_known_maps = [
        "K-35-062-2_Rakovski",
        "K-35-052-4_32635",
        "K-35-053-3_Elenovo",
        "K-35-078-1_Lesovo"
    ]
    
    results = []
    
    for map_name in all_known_maps:
        # Subset Detections
        det_subset = gdf_det[gdf_det['Map'] == map_name].copy()
        
        # Subset References
        ref_subset = gdf_ref_all[gdf_ref_all['Map'] == map_name].copy()
        
        # Skip if no references on this map? No, Lesovo has few but >0.
        if len(ref_subset) == 0:
            print(f"[{map_name}] No reference data found. Skipping.")
            continue
            
        # However! The Reference Subset is the FULL map.
        # But we only ran detections on 5 TILES.
        # We must NOT count False Negatives for mounds outside those 5 tiles!
        # This is CRITICAL.
        # We need to filter the Reference Mounds to ONLY those that fall within the bounds of the processed tiles.
        
        # Strategy:
        # 1. Calculate the union of the bounding boxes of the 5 processed tiles for this map.
        # 2. Clip the Reference Mounds to this union area.
        # 3. THEN calculate FN.
        
        # To get the tile bounds:
        # We can read the calibration manifest to know which tiles were processed.
        # Then calculate their bounds (x, y + 448...).
        # Or simpler: The detections themselves give us a hint? No, detections might be empty.
        # We MUST read the manifest.
        pass # Placeholder comment
    
    # Re-implmenting loop with Manifest support
    # Load Manifest
    manifest_path = INPUTS_DIR / "calibration_manifest.json"
    with open(manifest_path, 'r') as f:
        manifest_files = json.load(f)
    
    # Bounding Box Logic
    # Filename format: {MAP}_x{X}_y{Y}.png
    # Tile Size: 448x448 (No! It's 448 pixels?)
    # Wait, what is the spatial size?
    # We need the geotransform.
    # This is getting complex.
    # ALTERNATIVE: Use the `export_bounds` feature I added to `3_detect_mounds_visual.py`.
    # It saves the bounds of processed tiles into the GeoJSON detections as a separate layer?
    # No, currently `3_detect_mounds_visual.py` Logic:
    # "if export_bounds: ... save bounds to SEPARATE file?"
    # Let's check `3_detect_mounds_visual.py`.
    
    # It appends to `all_features`.
    # "properties": {"type": "processed_tile_bounds", ...}
    # AHA! The detection GeoJSON contains the bounds of the tiles we processed!
    # Excellent.
    
    # So:
    # 1. Extract "processed_tile_bounds" features from `gdf_det` OR loaded bounds file.
    # 2. Use them to clip the Reference Set.
    
    tile_bounds_features = None
    
    if gdf_bounds is not None:
         tile_bounds_features = gdf_bounds
    else:
         # Try to find in detections
         if 'label' in gdf_det.columns:
             tile_bounds_features = gdf_det[gdf_det['label'] == 'processed_tile_bounds']
    
    if tile_bounds_features is None or len(tile_bounds_features) == 0:
        print("Warning: No processed tile bounds found. Cannot compute valid False Negatives (FN).")
        print("Assuming entire map was searched (which is WRONG for calibration run).")
        # Fallback to empty geo series?
        tile_bounds_features = gpd.GeoDataFrame(geometry=[], crs=gdf_det.crs)

    # Filter detections to exclude bounds if they are in there
    actual_detections = gdf_det
    if 'label' in gdf_det.columns:
        actual_detections = gdf_det[gdf_det['label'] != 'processed_tile_bounds']
    
    for map_name in all_known_maps:
        # 1. Get processed bounds for this map
        # Identify bounds by 'tile_name' property which contains the filename
        # Format: {MAP}_x...
        map_bounds = tile_bounds_features[tile_bounds_features['tile_name'].str.startswith(map_name)]
        
        if len(map_bounds) == 0:
             print(f"[{map_name}] No tile bounds found.")
             continue
        
        # Create a unified geometry of the searched area
        searched_area = map_bounds.geometry.union_all()
        
        # Apply Edge Exclusion if requested
        # Erode the searched area to ignore mounds sitting on the cut-off boundary
        if edge_exclusion > 0:
            searched_area = searched_area.buffer(-edge_exclusion)
        
        if searched_area.is_empty:
            print(f"[{map_name}] No searched area found (checked {len(map_bounds)} tile bounds).")
            # If we processed it but it's not in detections file, maybe we really had 0 detections?
            # But `export_bounds` should write regardless of detections?
            # Let's verify `3_detect_mounds_visual.py` later. Assuming it works.
            continue
            
        # 2. Filter Reference Mounds to Searched Area
        ref_on_map = gdf_ref_all[gdf_ref_all['Map'] == map_name]
        # Check intersection with searched area (using centroids of mounds before buffering? or buffered?)
        # Strictly: The mound centroid must be inside the tile.
        # But we buffered the refs. Let's use the original unbuffered centroid?
        # `ref_on_map` already has buffered geometry.
        # Let's just use `within` or `intersects`.
        # `ref_on_map.geometry.centroid` might not work if geometry is Polygon (buffer).
        # We can reconstruct centroids or just check intersection.
        ref_in_scope = ref_on_map[ref_on_map.intersects(searched_area)]
        
        # 3. Filter Detections to this Map (and ignore "label"='processed_tile_bounds')
        # (Already separated into `actual_detections`)
        det_on_map = actual_detections[actual_detections['Map'] == map_name]
        
        # consistency check: Filter Detections to Searched Area (Eroded)
        # using centroids or intersection
        if edge_exclusion > 0 and not det_on_map.empty:
             # Keep detections whose centroid is within the valid area
             det_on_map = det_on_map[det_on_map.geometry.centroid.within(searched_area)]
        
        # 4. Calculate Stats
        # TP: Join Detections -> Ref Scope
        join_right = gpd.sjoin(det_on_map, ref_in_scope, how='right', predicate='intersects')
        tp = len(join_right[join_right.index_left.notnull()].index.unique())
        fn = len(ref_in_scope) - tp
        
        # FP: Join Detections -> Ref Scope
        join_left = gpd.sjoin(det_on_map, ref_in_scope, how='left', predicate='intersects')
        # Only count FP if it is INSIDE the searched area?
        # Yes, detections outside searched area (edge effects?) should be ignored or flagged.
        # But `det_on_map` are by definition from the tiles we processed, so they are inside (mostly).
        matched_det_indices = join_left[join_left.index_right.notnull()].index.unique()
        fp = len(det_on_map) - len(matched_det_indices)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"[{map_name}] F1: {f1:.4f} | Prec: {precision:.2f} | Rec: {recall:.2f} | TP: {tp}, FP: {fp}, FN: {fn} (Scope: {len(ref_in_scope)} refs)")
        
        global_tp += tp
        global_fp += fp
        global_fn += fn
        
        results.append({
            "Map": map_name, "Precision": precision, "Recall": recall, "F1": f1
        })
        
    # Global
    g_prec = global_tp / (global_tp + global_fp) if (global_tp + global_fp) > 0 else 0
    g_rec = global_tp / (global_tp + global_fn) if (global_tp + global_fn) > 0 else 0
    g_f1 = 2 * (g_prec * g_rec) / (g_prec + g_rec) if (g_prec + g_rec) > 0 else 0
    
    print(f"\n--- Global Stratified Results ---")
    print(f"F1 Score:  {g_f1:.4f}")
    print(f"Precision: {g_prec:.4f}")
    print(f"Recall:    {g_rec:.4f}")
    print(f"Counts:    TP={global_tp}, FP={global_fp}, FN={global_fn}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--detections", type=str, required=True, help="Path to detection GeoJSON")
    parser.add_argument("--bounds", type=str, required=False, help="Path to bounds GeoJSON")
    parser.add_argument("--edge_exclusion", type=float, default=0, help="Margin in meters to exclude from search area edges (to ignore cut-off mounds)")
    args = parser.parse_args()
    
    evaluate_stratified(args.detections, args.bounds, edge_exclusion=args.edge_exclusion)
