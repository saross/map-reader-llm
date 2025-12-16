
import json
import random
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import TILES_DIR, INPUTS_DIR
from PIL import Image
import numpy as np

def is_valid_tile(tile_path, variance_threshold=5.0):
    """
    Checks if a tile has sufficient information density to be a valid map area.
    Rejects tiles that are mostly solid color (padding/void).
    Criteria: Standard Deviation of pixel values > threshold.
    """
    try:
        with Image.open(tile_path) as img:
            # Convert to greyscale for simple variance check
            img_gray = img.convert('L')
            # Calculate standard deviation
            stat = np.std(img_gray)
            if stat < variance_threshold:
                return False, stat
            return True, stat
    except Exception as e:
        print(f"Error checking valid tile {tile_path}: {e}")
        return False, 0.0

        return False, 0.0

def select_calibration_tiles():
    # 1. Rakovski: Use Fixed Set
    rakovski_fixed = [
        "K-35-062-2_Rakovski_x1792_y1792.png",
        "K-35-062-2_Rakovski_x2240_y1344.png",
        "K-35-062-2_Rakovski_x0_y2240.png",
        "K-35-062-2_Rakovski_x3584_y3584.png",
        "K-35-062-2_Rakovski_x3136_y2240.png"
    ]
    
    # 2. Others: Random 5
    maps = {
        "K-35-062-2_Rakovski": rakovski_fixed,
        "K-35-052-4_32635": [],
        "K-35-053-3_Elenovo": [],
        "K-35-078-1_Lesovo": []
    }
    
    manifest = []
    
    for map_name, fixed_tiles in maps.items():
        map_dir = TILES_DIR / map_name
        if not map_dir.exists():
            print(f"Warning: Map directory {map_name} not found.")
            continue
            
        all_tiles = sorted(list(map_dir.glob("*.png")))
        
        if fixed_tiles:
            # Validate fixed tiles exist (We don't density check fixed set, user chose them)
            selected = []
            for t_name in fixed_tiles:
                t_path = map_dir / t_name
                if t_path.exists():
                    selected.append(str(t_path))
                else:
                    print(f"Warning: Fixed tile {t_name} not found.")
        else:
            # Random selection with Density Check
            # Iterate through random shuffle until we find 5 good ones
            valid_candidates = []
            shuffled_tiles = all_tiles[:]
            random.shuffle(shuffled_tiles)
            
            print(f"Screening tiles for {map_name} (Total: {len(shuffled_tiles)})...")
            
            for p in shuffled_tiles:
                is_valid, score = is_valid_tile(p)
                if is_valid:
                    valid_candidates.append(str(p))
                
                if len(valid_candidates) >= 5:
                    break
            
            if len(valid_candidates) < 5:
                print(f"Warning: Could not find 5 valid tiles for {map_name} (Found {len(valid_candidates)}). Taking what we have.")
            
            selected = valid_candidates
        
        manifest.extend(selected)
        print(f"Selected {len(selected)} tiles for {map_name}")
        for s in selected:
            print(f"  - {Path(s).name}")

    # Save Manifest
    manifest_path = INPUTS_DIR / "calibration_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nSaved master calibration manifest to {manifest_path}")

if __name__ == "__main__":
    select_calibration_tiles()
