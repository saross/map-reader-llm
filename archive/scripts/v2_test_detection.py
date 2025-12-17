import sys
from pathlib import Path
import importlib.util

# Adjust python path
sys.path.append(str(Path(__file__).parent.parent))
from config import BASE_DIR, TILES_DIR

def run_v2_test():
    # Define the specific tile
    map_name = "K-35-062-2_Rakovski"
    # Tile to process (Specific "Problem Tile" from validation set)
    tile_filename = "K-35-062-2_Rakovski_x2688_y3136.png"
    
    # Note: TILES_DIR is configured in config.py, we trust it points to outputs/tiles or inputs/tiles as appropriate
    # My search found it at outputs/tiles/...
    tile_path = TILES_DIR / map_name / tile_filename
    
    if not tile_path.exists():
        print(f"Error: Tile not found at {tile_path}")
        return

    print(f"Testing V2 Prompt on: {tile_path}")
    
    # Dynamic import of detect_mounds to ensure we get the latest version
    module_name = "detect_mounds_module"
    spec = importlib.util.spec_from_file_location(module_name, Path(__file__).parent / "2_detect_mounds.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    output_filename = "test_v2.5_x2688_y3136.geojson"
    
    # Run detection
    module.detect_mounds(
        tile_list=[tile_path], 
        output_name=output_filename,
        export_bounds=True # Might as well export bounds to verify that too
    )

if __name__ == "__main__":
    run_v2_test()
