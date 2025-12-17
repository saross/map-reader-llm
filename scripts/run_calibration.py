
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import INPUTS_DIR

# Import the V3 visual detection function
import importlib.util
spec = importlib.util.spec_from_file_location("detect_mounds_visual", "scripts/3_detect_mounds_visual.py")
detect_mounds_module = importlib.util.module_from_spec(spec)
sys.modules["detect_mounds_visual"] = detect_mounds_module
spec.loader.exec_module(detect_mounds_module)

def run_calibration():
    manifest_path = INPUTS_DIR / "calibration_manifest.json"
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        return

    with open(manifest_path, 'r') as f:
        tile_paths = json.load(f)
    
    # Convert strings to Path objects
    tile_list = [Path(p) for p in tile_paths]
    
    print(f"Starting Calibration Run on {len(tile_list)} stratified tiles...")

    # Run detection
    detect_mounds_module.detect_mounds_visual(
        tile_list=tile_list, 
        output_name="detections-calibration-stratified.geojson",
        export_bounds=True
    )

if __name__ == "__main__":
    run_calibration()
