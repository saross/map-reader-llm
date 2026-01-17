#!/usr/bin/env python3
"""
Analyse False Positives/Negatives and Extract Crops for Hard Example Library
=============================================================================

Clusters FP/FN detections from multiple runs using distance-based matching (20m)
to align with F1 evaluation spatial tolerance, then extracts image crops for
the most recurrent errors to build a hard example library.

Usage:
    python scripts/analyse_fp_crops.py \\
        --input outputs/results/v4.2_temp_0_7_train/run_01_fn.geojson \\
        --output_dir outputs/hard-examples \\
        --mode fn \\
        --manifest inputs/tiles/calibration_manifest.json

Author: Shawn Ross, Claude Code
License: Apache 2.0
"""

import json
import geopandas as gpd
import math
import sys
from pathlib import Path
from shapely.geometry import box
from PIL import Image
import argparse

# Add project root to path for config import
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import project config for consistent paths
import config

# Constants for clustering and cropping
DISTANCE_THRESHOLD_METRES = 20.0  # Aligns with F1 evaluation spatial tolerance
DEFAULT_CROP_LIMIT = 10  # Maximum number of hard examples to extract
CROP_MARGIN_PX = 60  # Pixel margin around detection for context


def get_centroid(geom_bounds):
    """Get centroid coordinates from geometry bounds [minx, miny, maxx, maxy]."""
    minx, miny, maxx, maxy = geom_bounds
    return ((minx + maxx) / 2, (miny + maxy) / 2)


def centroid_distance(bounds_a, bounds_b):
    """
    Calculate Euclidean distance between centroids of two bounding boxes.

    Returns distance in coordinate units (metres for EPSG:32635).
    """
    cx_a, cy_a = get_centroid(bounds_a)
    cx_b, cy_b = get_centroid(bounds_b)
    return math.sqrt((cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2)

def geo_to_pixel(geo_bounds, tile_bounds, img_size):
    """
    Convert geographic bounds to pixel coordinates.

    Args:
        geo_bounds: Geographic bounds [minx, miny, maxx, maxy]
        tile_bounds: Tile geographic bounds [minx, miny, maxx, maxy]
        img_size: Image dimensions (width, height)

    Returns:
        Pixel bounds [px_minx, px_miny, px_maxx, px_maxy]

    Raises:
        ValueError: If tile bounds have zero width or height
    """
    g_minx, g_miny, g_maxx, g_maxy = geo_bounds
    t_minx, t_miny, t_maxx, t_maxy = tile_bounds
    w, h = img_size

    # Guard against degenerate tile bounds
    tile_width = t_maxx - t_minx
    tile_height = t_maxy - t_miny
    if tile_width == 0 or tile_height == 0:
        raise ValueError(f"Degenerate tile bounds: width={tile_width}, height={tile_height}")

    scale_x = w / tile_width
    scale_y = h / tile_height
    px_minx = (g_minx - t_minx) * scale_x
    px_maxx = (g_maxx - t_minx) * scale_x
    px_miny = (t_maxy - g_maxy) * scale_y
    px_maxy = (t_maxy - g_miny) * scale_y
    return [px_minx, px_miny, px_maxx, px_maxy]

def extract_crops(args):
    input_file = Path(args.input)
    results_dir = input_file.parent
    mode_suffix = "_fn.geojson" if args.mode == "fn" else "_fp.geojson"
    
    print(f"--- Analysing {args.mode.upper()}s ---")
    
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
    
    # 3. Cluster using distance-based matching
    # Aligns with F1 evaluation spatial tolerance for consistency
    distance_thresh = DISTANCE_THRESHOLD_METRES
    clusters = []
    used_indices = set()

    for i, det in enumerate(all_dets):
        if i in used_indices:
            continue
        current_cluster = [det]
        used_indices.add(i)
        for j, candidate in enumerate(all_dets):
            if j in used_indices:
                continue
            if candidate["source_tile"] != det["source_tile"]:
                continue
            # Use centroid distance for consistency with F1 evaluation
            dist = centroid_distance(det["geo_bounds"], candidate["geo_bounds"])
            if dist <= distance_thresh:
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

    # Build tile lookup: tile stem (without extension) -> full path in TILES_DIR
    # Manifest contains filenames like "K-35-052-4_32635_x1344_y2240.png"
    # Files are stored in subdirectories: TILES_DIR/{map_name}/{tile_name}.png
    tiles_dir = config.TILES_DIR
    tile_lookup = {}
    for tile_filename in manifest:
        tile_stem = Path(tile_filename).stem
        # Extract map name from tile filename (everything before _x{N}_y{N})
        # e.g., "K-35-052-4_32635_x1344_y2240" -> "K-35-052-4_32635"
        parts = tile_stem.rsplit("_x", 1)
        if len(parts) == 2:
            map_name = parts[0]
            tile_path = tiles_dir / map_name / tile_filename
            if tile_path.exists():
                tile_lookup[tile_stem] = tile_path
            else:
                # Try alternative locations
                found = list(tiles_dir.rglob(tile_filename))
                if found:
                    tile_lookup[tile_stem] = found[0]

    print(f"Built tile lookup with {len(tile_lookup)} entries from manifest")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract top N hard examples
    limit = DEFAULT_CROP_LIMIT
    extracted_count = 0
    
    for i, item in enumerate(sorted_clusters):
        if extracted_count >= limit:
            break

        # Only take items that appeared in at least 2 runs (if available), else top
        # For FN mining, ANY miss is interesting, but recurring misses are critical.
        if item["count"] < 1:
            continue

        rank = i + 1
        tile_name = item["tile"]
        print(f"Processing Rank {rank}: {tile_name} (Count: {item['count']})")

        # Normalise tile name (remove .png if present for lookup)
        tile_stem = tile_name.replace(".png", "")

        # Find image using manifest lookup first, then fallback to search
        tile_path = tile_lookup.get(tile_stem)

        if not tile_path:
            # Fallback: search in tiles_dir by exact filename
            tile_path = next(tiles_dir.rglob(f"{tile_stem}.png"), None)

        if not tile_path:
            # Try constructing path from tile name pattern
            # Tile name format: {map_name}_x{N}_y{N}
            parts = tile_stem.rsplit("_x", 1)
            if len(parts) == 2:
                map_name = parts[0]
                tile_path = tiles_dir / map_name / f"{tile_stem}.png"
                if not tile_path.exists():
                    tile_path = None

        if not tile_path:
            print(f"Tile image not found for {tile_name}")
            continue
            
        try:
            # Identify correct sub-tile by checking containment
            t_bounds = None
            img_path_resolved = None
            
            geo_b = item["geo_bounds"]
            
            # Check if exact match exists (try with and without .png extension)
            if tile_stem in tile_bounds_map:
                t_bounds = tile_bounds_map[tile_stem]
                img_path_resolved = tile_path
            elif f"{tile_stem}.png" in tile_bounds_map:
                t_bounds = tile_bounds_map[f"{tile_stem}.png"]
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
                
                # Expand crop area with margin for context
                margin = CROP_MARGIN_PX
                p_minx, p_miny, p_maxx, p_maxy = px_bounds
                
                crop_minx = max(0, int(p_minx) - margin)
                crop_miny = max(0, int(p_miny) - margin)
                crop_maxx = min(img.width, int(p_maxx) + margin)
                crop_maxy = min(img.height, int(p_maxy) + margin)
                
                crop = img.crop((crop_minx, crop_miny, crop_maxx, crop_maxy))
                
                # Save with informative name
                # hard_positive_rank_tile.png
                type_prefix = "hard_positive" if args.mode == "fn" else "hard_negative"
                out_name = f"{type_prefix}_{rank}_{tile_stem}.png"
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
