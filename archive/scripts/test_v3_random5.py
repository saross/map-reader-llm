
import random
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import TILES_DIR

# Import the V3 visual detection function
import importlib.util
spec = importlib.util.spec_from_file_location("detect_mounds_visual", "scripts/3_detect_mounds_visual.py")
detect_mounds_module = importlib.util.module_from_spec(spec)
sys.modules["detect_mounds_visual"] = detect_mounds_module
spec.loader.exec_module(detect_mounds_module)

def test_random_rakovski_v3():
    # Target specific map directory
    map_dir = TILES_DIR / "K-35-062-2_Rakovski"
    
    if not map_dir.exists():
        print(f"Error: Map directory not found at {map_dir}")
        return

    # Gather all png tiles
    all_tiles = list(map_dir.glob("*.png"))
    
    if not all_tiles:
        print("No tiles found.")
        return
        
    # Select 5 random
    selected_tiles = random.sample(all_tiles, min(5, len(all_tiles)))
    
    print(f"Selected {len(selected_tiles)} random tiles for V3 testing:")
    for t in selected_tiles:
        print(f" - {t.name}")

    # Run detection
    detect_mounds_module.detect_mounds_visual(
        tile_list=selected_tiles, 
        output_name="detections-rakovski-v3-random5.geojson",
        export_bounds=True
    )

if __name__ == "__main__":
    test_random_rakovski_v3()
