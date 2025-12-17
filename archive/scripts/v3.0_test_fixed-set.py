
import sys
from pathlib import Path
import geojson

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import TILES_DIR, RESULTS_DIR

# Import the V3 visual detection function
import importlib.util
spec = importlib.util.spec_from_file_location("detect_mounds_visual", "scripts/3_detect_mounds_visual.py")
detect_mounds_module = importlib.util.module_from_spec(spec)
sys.modules["detect_mounds_visual"] = detect_mounds_module
spec.loader.exec_module(detect_mounds_module)

# Monkey patch the save frequency in the module or execution?
# The function `detect_mounds_visual` has `save_frequency = 5` hardcoded.
# We can't easily change it without editing the file or copy-pasting code.
# Ideally, we edit `3_detect_mounds_visual.py` to default `save_frequency=1` for safety, 
# or accept an argument.
# For now, I'll just change the hardcoded value in `3_detect_mounds_visual.py` separately 
# because it's good practice anyway.

def test_fixed_set():
    tile_names = [
        "K-35-062-2_Rakovski_x1792_y1792.png",
        "K-35-062-2_Rakovski_x2240_y1344.png",
        "K-35-062-2_Rakovski_x0_y2240.png",
        "K-35-062-2_Rakovski_x3584_y3584.png",
        "K-35-062-2_Rakovski_x3136_y2240.png"
    ]
    
    map_dir = TILES_DIR / "K-35-062-2_Rakovski"
    selected_tiles = [map_dir / t for t in tile_names]
    
    print(f"Retesting {len(selected_tiles)} specific tiles...")

    # Run detection
    detect_mounds_module.detect_mounds_visual(
        tile_list=selected_tiles, 
        output_name="detections-rakovski-v3-random5-retry.geojson",
        export_bounds=True
    )

if __name__ == "__main__":
    test_fixed_set()
