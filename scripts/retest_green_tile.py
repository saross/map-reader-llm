
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import BASE_DIR, TILES_DIR

# Import the main logic from the V3 script (I'll need to make sure I can import it)
# Since the script is 3_detect_mounds_visual.py, importing might be tricky if it has dashes or starts with number.
# Using importlib to be safe.
import importlib.util

def load_v3_module():
    spec = importlib.util.spec_from_file_location("detect_mounds_visual", str(BASE_DIR / "scripts/3_detect_mounds_visual.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules["detect_mounds_visual"] = module
    spec.loader.exec_module(module)
    return module

def retest_tile():
    v3_module = load_v3_module()
    
    # Target Tile
    tile_name = "K-35-053-3_Elenovo_x1344_y1792.png"
    # Find full path
    # Search in all map dirs
    tile_path = None
    for map_dir in TILES_DIR.iterdir():
        candidate = map_dir / tile_name
        if candidate.exists():
            tile_path = candidate
            break
            
    if not tile_path:
        print(f"Could not find tile {tile_name}")
        return

    print(f"--- Retesting Tile: {tile_name} ---")
    print("Using V3 Prompt (Refined Few-Shot Library)")
    
    output_filename = "detections_verification_green_tile.geojson"
    
    # Run
    v3_module.detect_mounds_visual(tile_list=[tile_path], output_name=output_filename)

if __name__ == "__main__":
    retest_tile()
