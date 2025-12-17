
import json
import logging
from pathlib import Path
import geojson
import sys
import os

# Add parent to path to import scripts
sys.path.append(os.getcwd())
from scripts.4_detect_mounds_batch import detect_mounds_versioned
from config import BASE_DIR, TILES_DIR

def run_benchmark():
    # 1. Define Config
    config_path = "prompts/versions/v3.1_baseline.json"
    
    # 2. Load Calibration Manifest (The 20 "Gold Standard" tiles)
    manifest_path = "archive/results_phase_10_calibration_refined/detections-calibration-stratified_bounds.geojson"
    
    print(f"Loading calibration list from {manifest_path}...")
    
    try:
        with open(manifest_path, 'r') as f:
            data = geojson.load(f)
    except FileNotFoundError:
        print("Error: Calibration manifest not found in archive.")
        return

    # Extract unique tile names
    target_tiles = set()
    for feat in data.get("features", []):
         if "tile_name" in feat["properties"]:
             target_tiles.add(feat["properties"]["tile_name"])
    
    print(f"Found {len(target_tiles)} unique calibration tiles in manifest.")
    
    # 3. Resolve Paths
    resolved_paths = []
    # Pre-scan TILES_DIR to find paths quickly
    print("Resolving file paths...")
    # This might be slow if TILES_DIR is huge, but robust
    found_count = 0
    for map_dir in TILES_DIR.iterdir():
        if not map_dir.is_dir(): continue
        for tile_path in map_dir.glob("*.png"):
            if tile_path.name in target_tiles:
                resolved_paths.append(tile_path)
                target_tiles.remove(tile_path.name)
                found_count += 1
                if not target_tiles: break # Found all
        if not target_tiles: break

    if target_tiles:
        print(f"Warning: Could not find {len(target_tiles)} tiles: {target_tiles}")
    
    print(f"Starting Benchmark on {len(resolved_paths)} tiles...")
    print(f"Config: {config_path}")
    
    # 4. Run Detection
    output_name = "detections-v3.1-pro-benchmark.geojson"
    detect_mounds_versioned(
        config_path, 
        tile_list=resolved_paths, 
        output_name=output_name
    )

if __name__ == "__main__":
    run_benchmark()
