
import json
import geopandas as gpd
import pandas as pd
from pathlib import Path
from shapely.geometry import box
from PIL import Image
import argparse

def calculate_iou(boxA, boxB):
    b1 = box(boxA[0], boxA[1], boxA[2], boxA[3])
    b2 = box(boxB[0], boxB[1], boxB[2], boxB[3])
    if not b1.intersects(b2): return 0.0
    return b1.intersection(b2).area / b1.union(b2).area

def geo_to_pixel(geo_bounds, tile_bounds, img_size):
    g_minx, g_miny, g_maxx, g_maxy = geo_bounds
    t_minx, t_miny, t_maxx, t_maxy = tile_bounds
    w, h = img_size
    scale_x = w / (t_maxx - t_minx)
    scale_y = h / (t_maxy - t_miny)
    px_minx = (g_minx - t_minx) * scale_x
    px_maxx = (g_maxx - t_minx) * scale_x
    px_miny = (t_maxy - g_maxy) * scale_y
    px_maxy = (t_maxy - g_miny) * scale_y
    return [px_minx, px_miny, px_maxx, px_maxy]

def extract_crops(args):
    input_file = Path(args.input)
    results_dir = input_file.parent
    mode_suffix = "_fn.geojson" if args.mode == "fn" else "_fp.geojson"
    
    print(f"--- Analyzing {args.mode.upper()}s ---")
    
    # 1. Load Bounds
    # Assuming bounds file is in the same results tree or provided via arg? 
    # For now, let's try to infer from the run name or use a known location if possible.
    # Hack: Look for the corresponding bounds file in the same dir as the input file
    run_id = input_file.stem.replace("_fn", "").replace("_fp", "")
    bounds_file = results_dir / f"{run_id}_bounds.geojson"
    
    print(f"Loading bounds from {bounds_file}...")
    if not bounds_file.exists():
        print(f"Bounds file not found: {bounds_file}")
        # Try finding ANY bounds file in that dir
        bounds_file = next(results_dir.glob("*_bounds.geojson"), None)
        if not bounds_file:
            print("No bounds file found. filtering.")
            return

    tile_bounds_map = {}
    try:
        bounds_gdf = gpd.read_file(bounds_file)
        for _, row in bounds_gdf.iterrows():
            tile_bounds_map[row['tile_name']] = row.geometry.bounds
        print(f"Loaded {len(tile_bounds_map)} tiles from bounds: {list(tile_bounds_map.keys())[:5]}")
    except Exception as e:
        print(f"Error loading bounds: {e}")
        return

    # 2. Load all matching files (FP or FN) in the directory
    # If mode is FN, look for *_fn.geojson
    files = list(results_dir.glob(f"*{mode_suffix}"))
    print(f"Found {len(files)} {args.mode.upper()} files.")
    
    all_dets = []
    
    for f in files:
        rid = f.stem.replace(mode_suffix.replace(".geojson",""), "")
        try:
            gdf = gpd.read_file(f)
            for _, row in gdf.iterrows():
                all_dets.append({
                    "geo_bounds": row.geometry.bounds,
                    "source_tile": row.get("source_tile") or row.get("Map", ""),
                    "run_id": rid
                })
        except Exception as e:
            print(f"Skipping {f}: {e}")
            
    print(f"Total entries loaded: {len(all_dets)}")
    
    # 3. Cluster
    clusters = []
    used_indices = set()
    
    for i, det in enumerate(all_dets):
        if i in used_indices: continue
        current_cluster = [det]
        used_indices.add(i)
        for j, candidate in enumerate(all_dets):
            if j in used_indices: continue
            if candidate["source_tile"] != det["source_tile"]: continue
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
    
    # 5. Extract
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}")
        return

    with open(manifest_path) as f:
        manifest = json.load(f)
        # Map tile name (w/o ext) to file path
        # Actually manifest is list of filenames?
        # Let's assume input tiles dir
        pass

    tiles_dir = Path("inputs/tiles") # Hardcoded for now based on project struct
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract top N
    limit = 10
    extracted_count = 0
    
    for i, item in enumerate(sorted_clusters):
        if extracted_count >= limit: break
        
        # Only take items that appeared in at least 2 runs (if available), else top 
        # For FN mining, ANY miss is interesting, but recurring misses are critical.
        if item["count"] < 1: continue 

        rank = i + 1
        tile_name = item["tile"]
        print(f"Processing Rank {rank}: {tile_name} (Count: {item['count']})")
        
        # Find image
        # Priority: tile_name.png, recurisve search for tile_name.png
        tile_path = next(tiles_dir.rglob(f"{tile_name}.png"), None)
        
        if not tile_path:
             # Try exact match but ensure file
             candidate = next(tiles_dir.rglob(f"{tile_name}"), None)
             if candidate and candidate.is_file():
                 tile_path = candidate
        
        if not tile_path:
            # Try appending suffix if not present
             tile_path = next(tiles_dir.rglob(f"{tile_name}*.png"), None)

        if not tile_path:
            print(f"Tile image not found for {tile_name}")
            continue
            
        try:
            # Identify correct sub-tile by checking containment
            t_bounds = None
            img_path_resolved = None
            
            geo_b = item["geo_bounds"]
            
            # Check if exact match exists
            if tile_name in tile_bounds_map:
                t_bounds = tile_bounds_map[tile_name]
                img_path_resolved = tile_path
            else:
                # Search for any tile in bounds map that starts with tile_name (prefix match)
                # And actually contains the detection center
                det_box = box(*geo_b)
                det_center = det_box.centroid
                
                for b_name, b_coords in tile_bounds_map.items():
                    # Check spatial containment first
                    b_box = box(*b_coords)
                    if b_box.contains(det_center):
                        # Found the sub-tile that contains this FN
                        t_bounds = b_coords
                        # Now find this specific image file
                        possible_path = next(tiles_dir.rglob(b_name), None) 
                        if not possible_path:
                            possible_path = next(tiles_dir.rglob(f"{b_name}.png"), None)
                        
                        if possible_path:
                            img_path_resolved = possible_path
                            print(f"Resolved {tile_name} -> {b_name}")
                            break
            
            if not t_bounds or not img_path_resolved:
                print(f"Could not resolve bounds/image for {tile_name}")
                continue
                
            # Open the correct sub-tile image
            with Image.open(img_path_resolved) as img:
                px_bounds = geo_to_pixel(item["geo_bounds"], t_bounds, img.size)
                
                # Expand
                margin = 60 # Slightly larger for context
                p_minx, p_miny, p_maxx, p_maxy = px_bounds
                
                crop_minx = max(0, int(p_minx) - margin)
                crop_miny = max(0, int(p_miny) - margin)
                crop_maxx = min(img.width, int(p_maxx) + margin)
                crop_maxy = min(img.height, int(p_maxy) + margin)
                
                crop = img.crop((crop_minx, crop_miny, crop_maxx, crop_maxy))
                
                # Save with informative name
                # hard_positive_rank_tile.png
                type_prefix = "hard_positive" if args.mode == "fn" else "hard_negative"
                out_name = f"{type_prefix}_{rank}_{tile_name}.png"
                crop.save(output_dir / out_name)
                print(f"Saved {out_name}")
                extracted_count += 1
                
        except Exception as e:
            print(f"Error cropping: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to one input geojson file (to locate directory)")
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--mode", choices=["fp", "fn"], required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    
    extract_crops(args)
