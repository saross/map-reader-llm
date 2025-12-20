from PIL import Image
import numpy as np
import sys
from pathlib import Path

def inspect(path):
    p = Path(path)
    if not p.exists():
        print(f"File not found: {path}")
        return

    img = Image.open(p)
    print(f"Image: {p.name}")
    print(f"Mode: {img.mode}")
    
    data = np.array(img)
    
    if img.mode == 'RGBA':
        # Check alpha
        alpha = data[:, :, 3]
        filled = np.count_nonzero(alpha)
        total = alpha.size
        print(f"Filled (Non-Transparent): {filled}/{total} ({filled/total:.2%})")
    else:
        # Check for pure white or pure black
        # Flatten to count unique colors
        colors, counts = np.unique(data.reshape(-1, data.shape[2]), axis=0, return_counts=True)
        # Sort by count
        sorted_indices = np.argsort(-counts)
        print("Top 5 Colors:")
        for i in sorted_indices[:5]:
            print(f"  Color {colors[i]}: {counts[i]} pixels ({counts[i]/data.size*3:.2%})")

if __name__ == "__main__":
    inspect("inputs/tiles/K-35-052-4_32635/K-35-052-4_32635_x3584_y3584.png")
