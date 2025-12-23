from pathlib import Path
import sys

# Add parent directory to path to import config and scripts
sys.path.append(str(Path(__file__).parent.parent))

from config import TILES_DIR
# The specific challenging tile identified
target_tile_rel_path = "K-35-062-2_Rakovski/K-35-062-2_Rakovski_x2688_y3136.png"
target_tile_path = TILES_DIR / target_tile_rel_path

if not target_tile_path.exists():
    print(f"Error: Tile not found at {target_tile_path}")
    # Try one other variant if the first fails, just in case
    # checking directory listing...
    pass

print(f"Running detection on single tile: {target_tile_path}")

# Run detection
# We need to import the function. In 2_detect_mounds.py it is `detect_mounds`.
# However, 2_detect_mounds.py is a script, so importing it might run main if not careful.
# It has `if __name__ == "__main__":`, so it should be safe to import.
# Note: I need to import it as a module.

import importlib.util
spec = importlib.util.spec_from_file_location("detect_mounds_visual", "scripts/3_detect_mounds_visual.py")
detect_mounds_module = importlib.util.module_from_spec(spec)
sys.modules["detect_mounds_visual"] = detect_mounds_module
spec.loader.exec_module(detect_mounds_module)

detect_mounds_module.detect_mounds_visual(
    tile_list=[target_tile_path], 
    output_name="debug_v3_visual_single_tile.geojson",
    export_bounds=True
)
