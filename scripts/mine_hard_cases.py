"""
Hard Case Miner
===============

Extracts image crops for false positive and false negative detections to build
a hard example library for model training and analysis.

Usage:
    python scripts/mine_hard_cases.py <fp_path> <fn_path> <output_dir> [bounds_path]

Arguments:
    fp_path: Path to false positives GeoJSON file
    fn_path: Path to false negatives GeoJSON file
    output_dir: Output directory for cropped images
    bounds_path: Optional path to tile bounds GeoJSON for spatial lookup

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import sys
from pathlib import Path
from typing import Optional

import geopandas as gpd
import rasterio
from PIL import Image
from rasterio.windows import Window
from shapely.geometry import shape

# Setup Path to import config
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    from config import CONTEXT_SIZE, TILES_DIR
except ImportError:
    print("Error: config.py not found.")
    sys.exit(1)


def get_tile_path(tile_id: str) -> Optional[Path]:
    """
    Resolve tile ID to absolute file path.

    Searches the tiles directory for a matching tile file, trying both
    exact match and with .png extension.

    Args:
        tile_id: The tile identifier (with or without extension).

    Returns:
        Path to the tile file if found, None otherwise.
    """
    found = list(TILES_DIR.glob(f"**/{tile_id}"))
    if not found:
        found = list(TILES_DIR.glob(f"**/{tile_id}.png"))

    return found[0] if found else None


def crop_candidate(raster_path: Path, geom, context_px: int = CONTEXT_SIZE) -> Optional[Image.Image]:
    """
    Crop a region around the candidate geometry from a raster tile.

    Args:
        raster_path: Path to the source raster file.
        geom: Geometry object defining the detection location.
        context_px: Size of the crop region in pixels.

    Returns:
        PIL Image of the cropped region, or None if cropping fails.
    """
    with rasterio.open(raster_path) as src:
        bounds = shape(geom).bounds
        cx = (bounds[0] + bounds[2]) / 2
        cy = (bounds[1] + bounds[3]) / 2

        row, col = src.index(cx, cy)
        half_size = context_px // 2
        window = Window(col - half_size, row - half_size, context_px, context_px)

        try:
            arr = src.read(window=window)
            if arr.shape[0] == 0:
                return None
            img_data = arr.transpose(1, 2, 0)
            return Image.fromarray(img_data)
        except Exception:
            return None


def mine_crops(
    geojson_path: Path | str,
    output_dir: Path | str,
    label: str,
    bounds_path: Optional[Path | str] = None
) -> None:
    """
    Extract image crops for detections in a GeoJSON file.

    Args:
        geojson_path: Path to input GeoJSON with detection features.
        output_dir: Base output directory for cropped images.
        label: Label prefix for output files (e.g., 'hard_negative_fp').
        bounds_path: Optional path to tile bounds for spatial lookup fallback.
    """
    print(f"Mining {label} from {geojson_path}")

    try:
        gdf = gpd.read_file(geojson_path)
    except Exception as e:
        print(f"Error reading {geojson_path}: {e}")
        return

    print(f"Loaded {len(gdf)} features.")

    # Load bounds for spatial lookup fallback
    gdf_bounds = None
    if bounds_path:
        try:
            gdf_bounds = gpd.read_file(bounds_path)
        except Exception as e:
            print(f"Error loading bounds {bounds_path}: {e}")

    out_path = Path(output_dir) / label
    out_path.mkdir(parents=True, exist_ok=True)

    saved = 0
    for idx, row in gdf.iterrows():
        tile_id = row.get('source_tile')

        # Fallback: Spatial lookup using tile bounds
        if not tile_id and gdf_bounds is not None:
            query_geom = row.geometry.centroid
            match = gdf_bounds[gdf_bounds.contains(query_geom)]
            if not match.empty:
                tile_id = match.iloc[0]['tile_name']

        if not tile_id:
            continue

        tile_path = get_tile_path(tile_id)
        if not tile_path:
            continue

        img = crop_candidate(tile_path, row['geometry'])
        if img:
            fname = f"{label}_{idx}_{tile_id}.png"
            img.save(out_path / fname)
            saved += 1

    print(f"Saved {saved} {label} crops to {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python mine_hard_cases.py <fp_path> <fn_path> <output_dir> [bounds_path]")
        sys.exit(1)
        
    fp_path = sys.argv[1]
    fn_path = sys.argv[2]
    out_dir = sys.argv[3]
    bounds_path = sys.argv[4] if len(sys.argv) > 4 else None
    
    mine_crops(fp_path, out_dir, "hard_negative_fp", bounds_path)
    mine_crops(fn_path, out_dir, "hard_positive_fn", bounds_path)
