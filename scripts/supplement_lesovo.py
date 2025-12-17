
import random
import numpy as np
from PIL import Image
from pathlib import Path
import sys
import geopandas as gpd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import TILES_DIR, RESULTS_DIR
# from scripts import detect_mounds_visual_module

# We need to import the detect function. Since 3_detect_mounds_visual.py has numbers, it's annoying to import.
# I will use the `runpy` or just verify if I can import it. The user moved it to scripts/3_detect_mounds_visual.py.
# Python imports don't like starting with numbers.
# I'll just use subprocess or renamed import if needed, or better:
# actually, I can just use `import importlib.util`

def import_module_from_path(module_name, file_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

detect_module = import_module_from_path("detect_viz", "scripts/3_detect_mounds_visual.py")

def is_valid_content(tile_path, coverage_threshold=0.30):
    """
    Checks if tile has at least 30% non-white content.
    Assumes white/near-white is padding.
    """
    try:
        with Image.open(tile_path) as img:
            # Convert to greyscale
            arr = np.array(img.convert('L'))
            # Count pixels that are NOT white (allow some noise, say < 250)
            non_white_pixels = np.sum(arr < 250)
            total_pixels = arr.size
            ratio = non_white_pixels / total_pixels
            return ratio >= coverage_threshold, ratio
    except Exception as e:
        print(f"Error checking {tile_path}: {e}")
        return False, 0.0

def supplement_lesovo():
    map_name = "K-35-078-1_Lesovo"
    map_dir = TILES_DIR / map_name
    
    # Check existing successful tiles
    bounds_file = RESULTS_DIR / "detections-calibration-stratified_bounds.geojson"
    existing_tiles = set()
    
    if bounds_file.exists():
        try:
            gdf = gpd.read_file(bounds_file)
            # Filter for this map
            lesovo_bounds = gdf[gdf['tile_name'].str.contains(map_name)]
            existing_tiles = set(lesovo_bounds['tile_name'].tolist())
            print(f"Found {len(existing_tiles)} existing successful tiles for {map_name}.")
        except Exception as e:
            print(f"Error reading bounds file: {e}")
    
    target_count = 5
    needed = target_count - len(existing_tiles)
    
    if needed <= 0:
        print("Lesovo already has 5 successful tiles. No action needed.")
        return

    print(f"Need {needed} more tiles to reach target of {target_count}.")
    
    # Find candidates
    all_tiles = list(map_dir.glob("*.png"))
    shuffled = all_tiles[:]
    random.shuffle(shuffled)
    
    new_selection = []
    
    print("Screening candidates...")
    for t_path in shuffled:
        if t_path.name in existing_tiles:
            continue
            
        is_good, ratio = is_valid_content(t_path)
        if is_good:
            print(f"  Selected: {t_path.name} (Content: {ratio:.1%})")
            new_selection.append(t_path)
        
        if len(new_selection) >= needed:
            break
            
    if len(new_selection) < needed:
        print(f"Warning: Could only find {len(new_selection)} valid tiles.")
    
    if not new_selection:
        print("No new tiles selected.")
        return

    # Run Detection
    print(f"Starting detection on {len(new_selection)} new tiles...")
    detect_module.detect_mounds_visual(
        tile_list=new_selection,
        output_name="detections-calibration-stratified.geojson",
        export_bounds=True
    )
    print("Done.")

if __name__ == "__main__":
    supplement_lesovo()
