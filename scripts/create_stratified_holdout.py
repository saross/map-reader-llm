import json
import random
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# Configuration
INPUTS_DIR = Path("inputs")
TILES_DIR = INPUTS_DIR / "tiles"
TRAINING_MANIFEST = INPUTS_DIR / "target_tiles_manifest.json"
OUTPUT_MANIFEST = INPUTS_DIR / "holdout_manifest.json"
SAMPLES_PER_MAP = 5
MAX_BLACK_PERCENT = 0.70

def is_tile_filled(path):
    """
    Returns True if the tile has less than MAX_BLACK_PERCENT black pixels.
    Assumes Black [0,0,0] is the background.
    """
    try:
        img = Image.open(path)
        data = np.array(img)
        
        # Check for RGB mode
        if img.mode != 'RGB':
            img = img.convert('RGB')
            data = np.array(img)
            
        # Count black pixels [0,0,0]
        # np.all(data == [0,0,0], axis=2) creates a boolean mask
        black_pixels = np.sum(np.all(data == [0,0,0], axis=-1))
        total_pixels = data.shape[0] * data.shape[1]
        
        black_ratio = black_pixels / total_pixels
        
        if black_ratio > MAX_BLACK_PERCENT:
            # print(f"Skipping {path.name}: {black_ratio:.1%} Black")
            return False
            
        return True
    except Exception as e:
        print(f"Error checking {path.name}: {e}")
        return False

def main():
    print(f"--- Generating Stratified Holdout Set ---")
    
    # 1. Load Training Set (Exclusion List)
    with open(TRAINING_MANIFEST) as f:
        training_files = set(json.load(f))
    print(f"Loaded {len(training_files)} training tiles to exclude.")
    
    # 2. Scan and Group Tiles
    map_candidates = {} # map_name -> list of paths
    
    # We assume structure: inputs/tiles/MAP_NAME/TILE.png
    # But files might be flat or nested differently. The finding logic in other scripts suggests strict structure.
    # Let's use recursive glob but group by parent folder name which corresponds to Map ID.
    
    all_tiles = list(TILES_DIR.rglob("*.png"))
    print(f"Found {len(all_tiles)} total png files.")
    
    for p in all_tiles:
        if p.name in training_files:
            continue
            
        # Parent directory is the Map ID
        map_id = p.parent.name
        if map_id == "legend":
            continue
            
        if map_id not in map_candidates:
            map_candidates[map_id] = []
        map_candidates[map_id].append(p)
        
    print(f"Found {len(map_candidates)} maps with candidates.")
    
    # 3. Select Stratified Samples
    final_selection = []
    
    for map_id, candidates in map_candidates.items():
        print(f"\nProcessing Map: {map_id}")
        print(f"  Total Candidates: {len(candidates)}")
        
        # Shuffle candidates to randomize the check order (efficiency)
        random.shuffle(candidates)
        
        selected_for_map = []
        checked_count = 0
        
        for cand in candidates:
            if len(selected_for_map) >= SAMPLES_PER_MAP:
                break
                
            # Check content constraint
            if is_tile_filled(cand):
                selected_for_map.append(cand.name)
            
            checked_count += 1
            
        if len(selected_for_map) < SAMPLES_PER_MAP:
            print(f"  Warning: Only found {len(selected_for_map)} valid tiles for {map_id} (Wanted {SAMPLES_PER_MAP})")
        else:
            print(f"  Selected {len(selected_for_map)} tiles (Checked {checked_count})")
            
        final_selection.extend(selected_for_map)
        
    # 4. Save Manifest
    print(f"\nTotal Selection: {len(final_selection)}")
    if len(final_selection) > 0:
        final_selection.sort()
        with open(OUTPUT_MANIFEST, "w") as f:
            json.dump(final_selection, f, indent=2)
        print(f"Saved to {OUTPUT_MANIFEST}")
    else:
        print("Error: No tiles selected.")

if __name__ == "__main__":
    main()
