
import rasterio
from pathlib import Path
import sys

# Find a tile
try:
    tile_path = next(Path("inputs/tiles").glob("**/*.png"))
    with rasterio.open(tile_path) as src:
        print(f"Tile: {tile_path}")
        print(f"Transform: {src.transform}")
        print(f"Resolution (x, y): {src.res}")
except Exception as e:
    print(e)
