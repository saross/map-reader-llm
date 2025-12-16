import random
import argparse
from pathlib import Path
import sys

# Add local scripts to path
sys.path.append(str(Path(__file__).parent))

# Import the main detection function dynamically
import importlib.util
spec = importlib.util.spec_from_file_location("detect_mounds_module", Path(__file__).parent / "2_detect_mounds.py")
detect_mounds_module = importlib.util.module_from_spec(spec)
sys.modules["detect_mounds_module"] = detect_mounds_module
spec.loader.exec_module(detect_mounds_module)

from config import TILES_DIR

def run_random_extraction(map_name, count):
    map_tiles_dir = TILES_DIR / map_name
    
    if not map_tiles_dir.exists():
        print(f"Error: Directory {map_tiles_dir} does not exist.")
        # List available maps
        print("Available maps:")
        for d in TILES_DIR.iterdir():
            if d.is_dir():
                print(f" - {d.name}")
        return

    # Get all PNG tiles (excluding aux xmls)
    all_tiles = list(map_tiles_dir.glob("*.png"))
    
    if not all_tiles:
        print(f"No PNG tiles found in {map_tiles_dir}.")
        return

    if len(all_tiles) < count:
        print(f"Not enough tiles found in {map_tiles_dir}. Found {len(all_tiles)}, requested {count}.")
        selected_tiles = all_tiles
    else:
        selected_tiles = random.sample(all_tiles, count)
        
    print(f"Selected {len(selected_tiles)} tiles from {map_name} for processing:")
    for t in selected_tiles:
        print(f" - {t.name}")
        
    # Output name based on map and count
    output_filename = f"detections-{map_name}-random{len(selected_tiles)}.geojson"
    
    # Run Inference
    print(f"Running inference using {detect_mounds_module.MODEL_NAME}...")
    detect_mounds_module.detect_mounds(tile_list=selected_tiles, output_name=output_filename, export_bounds=args.export_bounds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run detection on random tiles from a map.")
    parser.add_argument("map_name", type=str, help="Name of the map directory in inputs (e.g., K-35-062-2_Rakovski)")
    parser.add_argument("--count", type=int, default=5, help="Number of random tiles to process (default: 5)")
    parser.add_argument("--export_bounds", action="store_true", help="Export a separate GeoJSON with tile bounding boxes")
    
    args = parser.parse_args()
    
    run_random_extraction(args.map_name, args.count)
