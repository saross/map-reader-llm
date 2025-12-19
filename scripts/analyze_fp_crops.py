
import json
import geopandas as gpd
import pandas as pd
from pathlib import Path
from shapely.geometry import box, shape
from PIL import Image
import numpy as np

# Configuration
RESULTS_DIR = Path("outputs/results/v3.5_n5_stats")
BOUNDS_FILE = Path("outputs/results/v3.5_clean/v3.5_n5_stats_run_01_bounds.geojson")
TILES_DIR = Path("inputs/tiles") 
OUTPUT_DIR = Path("outputs/crops")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def calculate_iou(boxA, boxB):
    # box: [ymin, xmin, ymax, xmax] (Pixels)
    # OR [minx, miny, maxx, maxy] (Geo) - Logic is same for IOU
    b1 = box(boxA[0], boxA[1], boxA[2], boxA[3])
    b2 = box(boxB[0], boxB[1], boxB[2], boxB[3])
    if not b1.intersects(b2): return 0.0
    return b1.intersection(b2).area / b1.union(b2).area

def geo_to_pixel(geo_bounds, tile_bounds, img_size):
    """
    Transform geocoords to pixel coords.
    geo_bounds: (minx, miny, maxx, maxy)
    tile_bounds: (minx, miny, maxx, maxy)
    img_size: (width, height)
    """
    g_minx, g_miny, g_maxx, g_maxy = geo_bounds
    t_minx, t_miny, t_maxx, t_maxy = tile_bounds
    w, h = img_size
    
    scale_x = w / (t_maxx - t_minx)
    scale_y = h / (t_maxy - t_miny)
    
    # X is standard
    px_minx = (g_minx - t_minx) * scale_x
    px_maxx = (g_maxx - t_minx) * scale_x
    
    # Y is inverted (Map Y goes Up, Image Y goes Down)
    # y_pixel = (tile_max_y - y_geo) * scale
    px_miny = (t_maxy - g_maxy) * scale_y
    px_maxy = (t_maxy - g_miny) * scale_y
    
    return [px_minx, px_miny, px_maxx, px_maxy]

def extract_crops():
    print("--- Analyzing False Positives ---")
    
    # 1. Load Bounds
    print(f"Loading bounds from {BOUNDS_FILE}...")
    try:
        bounds_gdf = gpd.read_file(BOUNDS_FILE)
        # Create dict: tile_name -> bounds tuple (minx, miny, maxx, maxy)
        tile_bounds_map = {}
        for _, row in bounds_gdf.iterrows():
            tile_bounds_map[row['tile_name']] = row.geometry.bounds
    except Exception as e:
        print(f"Error loading bounds: {e}")
        return

    # 2. Load all FP files
    fp_files = list(RESULTS_DIR.glob("*_fp.geojson"))
    print(f"Found {len(fp_files)} FP files.")
    
    all_fps = []
    
    for f in fp_files:
        run_id = f.stem.replace("_fp", "")
        gdf = gpd.read_file(f)
        
        for _, row in gdf.iterrows():
            all_fps.append({
                "geo_bounds": row.geometry.bounds, # minx, miny, maxx, maxy
                "source_tile": row.get("source_tile", ""),
                "run_id": run_id
            })
            
    print(f"Total FPs loaded: {len(all_fps)}")
    
    # 3. Cluster FPs (Using Geo IOU)
    clusters = []
    used_indices = set()
    
    for i, det in enumerate(all_fps):
        if i in used_indices: continue
        
        current_cluster = [det]
        used_indices.add(i)
        
        for j, candidate in enumerate(all_fps):
            if j in used_indices: continue
            if candidate["source_tile"] != det["source_tile"]: continue
            
            # Simple Geo IOU
            if calculate_iou(det["geo_bounds"], candidate["geo_bounds"]) > 0.5:
                current_cluster.append(candidate)
                used_indices.add(j)
        
        clusters.append(current_cluster)
        
    print(f"Unique Clusters: {len(clusters)}")
    
    # 4. Sort by Recurrence
    cluster_stats = []
    for cl in clusters:
        unique_runs = len(set(c["run_id"] for c in cl))
        cluster_stats.append({
            "count": unique_runs,
            "tile": cl[0]["source_tile"],
            "geo_bounds": cl[0]["geo_bounds"]
        })
        
    sorted_clusters = sorted(cluster_stats, key=lambda x: x["count"], reverse=True)
    
    # 5. Extract Top 2
    top_n = sorted_clusters[:2]
    
    generated_crops = []
    
    for i, item in enumerate(top_n):
        rank = i + 1
        count = item["count"]
        tile_name = item["tile"]
        geo_b = item["geo_bounds"]
        
        print(f"Rank {rank}: {tile_name} (In {count} runs)")
        
        # Load Image
        tile_path = next(TILES_DIR.rglob(f"{tile_name}"), None)
        if not tile_path:
             tile_path = next(TILES_DIR.rglob(f"{tile_name}.png"), None)
             
        if not tile_path:
            print(f"Could not find image for {tile_name}")
            continue
            
        try:
            with Image.open(tile_path) as img:
                # Transform coords
                t_bounds = tile_bounds_map.get(tile_name)
                if not t_bounds:
                    # Try usually the tile name in manifest might be slightly diff? 
                    # Try looking for partial match
                    print("Bounds not found for exact name, trying fallback...")
                    continue
                    
                px_bounds = geo_to_pixel(geo_b, t_bounds, img.size)
                
                # Expand box by margin (e.g. 50px)
                margin = 50
                p_minx, p_miny, p_maxx, p_maxy = px_bounds
                
                crop_minx = max(0, int(p_minx) - margin)
                crop_miny = max(0, int(p_miny) - margin)
                crop_maxx = min(img.width, int(p_maxx) + margin)
                crop_maxy = min(img.height, int(p_maxy) + margin)
                
                crop = img.crop((crop_minx, crop_miny, crop_maxx, crop_maxy))
                
                out_name = f"hard_negative_{rank}_{tile_name}.png"
                out_path = OUTPUT_DIR / out_name
                crop.save(out_path)
                print(f"Saved crop to {out_path}")
                generated_crops.append(str(out_path))
                
        except Exception as e:
            print(f"Error processing image: {e}")
            import traceback
            traceback.print_exc()
            
    return generated_crops

if __name__ == "__main__":
    extract_crops()
