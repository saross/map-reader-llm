import sys
from pathlib import Path
import importlib.util

# Add local scripts to path
sys.path.append(str(Path(__file__).parent))

# Import the main detection function dynamically
spec = importlib.util.spec_from_file_location("detect_mounds_module", Path(__file__).parent / "2_detect_mounds.py")
detect_mounds_module = importlib.util.module_from_spec(spec)
sys.modules["detect_mounds_module"] = detect_mounds_module
spec.loader.exec_module(detect_mounds_module)

from config import TILES_DIR

def run_retest():
    map_name = "K-35-062-2_Rakovski"
    map_tiles_dir = TILES_DIR / map_name
    
    # Specific tiles from the V2.3 validation run
    tile_names = [
        "K-35-062-2_Rakovski_x3136_y448.png",
        "K-35-062-2_Rakovski_x3584_y3584.png",
        "K-35-062-2_Rakovski_x3584_y2688.png",
        "K-35-062-2_Rakovski_x4032_y3136.png",
        "K-35-062-2_Rakovski_x2688_y3136.png"
    ]
    
    selected_tiles = []
    for name in tile_names:
        tile_path = map_tiles_dir / name
        if tile_path.exists():
            selected_tiles.append(tile_path)
        else:
            print(f"Warning: Tile {name} not found.")
            
    if not selected_tiles:
        print("No tiles found to process.")
        return

    print(f"Retesting {len(selected_tiles)} tiles with V2.4 prompt...")
    
    # Run Inference
    output_filename = "detections-v2.4-retest.geojson"
    detect_mounds_module.detect_mounds(tile_list=selected_tiles, output_name=output_filename, export_bounds=False)

if __name__ == "__main__":
    run_retest()
