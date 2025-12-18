import numpy as np
from PIL import Image
import os
import sys

# Paths to the specific failed tiles from the log
failed_tiles = [
    "inputs/tiles/K-35-052-4_32635/K-35-052-4_32635_x3584_y448.png",
    "inputs/tiles/K-35-053-3_Elenovo/K-35-053-3_Elenovo_x1344_y3584.png",
    "inputs/tiles/K-35-053-3_Elenovo/K-35-053-3_Elenovo_x1792_y3136.png",
    "inputs/tiles/K-35-053-3_Elenovo/K-35-053-3_Elenovo_x1792_y896.png",
    "inputs/tiles/K-35-053-3_Elenovo/K-35-053-3_Elenovo_x2240_y448.png"
]

def check_variance(path):
    try:
        if not os.path.exists(path):
            print(f"[MISSING] {path}")
            return
            
        img = Image.open(path).convert('L') # Greyscale
        arr = np.array(img)
        variance = np.var(arr)
        print(f"[file: {os.path.basename(path)}] Variance: {variance:.2f} | Shape: {arr.shape}")
        
    except Exception as e:
        print(f"[ERROR] {path}: {e}")

if __name__ == "__main__":
    print("Checking variance of failed tiles (Low variance < 5 implies 'White Void')...")
    for tile in failed_tiles:
        check_variance(tile)
