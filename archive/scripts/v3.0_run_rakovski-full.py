
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

def run_rakovski_full():
    # Target Rakovski Map specifically
    map_dir = TILES_DIR / "K-35-062-2_Rakovski"
    
    if not map_dir.exists():
        print(f"Error: Map directory not found at {map_dir}")
        return

    # Gather all png tiles
    all_tiles = sorted(list(map_dir.glob("*.png")))
    
    if not all_tiles:
        print("No tiles found.")
        return
        
    print(f"Starting Full Run on {len(all_tiles)} tiles from {map_dir.name}...")

    # Run detection with specific output name
    detect_mounds_module.detect_mounds_visual(
        tile_list=all_tiles, 
        output_name="detections-rakovski-full-v3-robust.geojson",
        export_bounds=True
    )

if __name__ == "__main__":
    run_rakovski_full()
