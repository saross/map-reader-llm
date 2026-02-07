#!/usr/bin/env python3
"""
Hard Case Miner
===============

Extracts image crops for false positive (FP) and false negative (FN) detections
to build a hard example library for model training and analysis.

Reads detection features from GeoJSON (Geographic JavaScript Object Notation) files,
locates the corresponding raster tiles, and saves cropped Portable Network Graphics
(PNG) images centred on each detection.

Usage::

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

import geopandas as gpd
import rasterio
from PIL import Image
from rasterio.windows import Window
from shapely.geometry import shape

# Resolve project root as parent of the scripts/ directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

try:
    from config import CONTEXT_SIZE, TILES_DIR
except ImportError:
    print("Error: config.py not found. Ensure config.py exists at the project root.")
    sys.exit(1)


def get_tile_path(tile_id: str) -> Path | None:
    """
    Resolve a tile identifier to its absolute file path.

    Searches the tiles directory for a matching tile file, trying both
    an exact match and with a .png extension appended.

    Args:
        tile_id: The tile identifier (with or without extension).

    Returns:
        Path to the tile file if found, None otherwise.
    """
    found = list(TILES_DIR.glob(f"**/{tile_id}"))
    if not found:
        found = list(TILES_DIR.glob(f"**/{tile_id}.png"))

    return found[0] if found else None


def crop_candidate(
    raster_path: Path,
    geom,
    context_px: int = CONTEXT_SIZE,
) -> Image.Image | None:
    """
    Crop a region centred on the candidate geometry from a raster tile.

    Computes the centroid of the geometry bounding box, converts to pixel
    coordinates, and extracts a square window of ``context_px`` pixels.

    Args:
        raster_path: Path to the source raster file.
        geom: Geometry object defining the detection location.
        context_px: Size of the square crop region in pixels.

    Returns:
        PIL (Python Imaging Library) Image of the cropped region, or None
        if the read window falls outside the raster or contains no bands.
    """
    with rasterio.open(raster_path) as src:
        geom_bounds = shape(geom).bounds
        centroid_x = (geom_bounds[0] + geom_bounds[2]) / 2
        centroid_y = (geom_bounds[1] + geom_bounds[3]) / 2

        row, col = src.index(centroid_x, centroid_y)
        half_size = context_px // 2
        window = Window(col - half_size, row - half_size, context_px, context_px)

        try:
            arr = src.read(window=window)
            if arr.shape[0] == 0:
                return None
            # Rasterio returns (bands, rows, cols); transpose to (rows, cols, bands)
            img_data = arr.transpose(1, 2, 0)
            return Image.fromarray(img_data)
        except Exception:
            return None


def mine_crops(
    geojson_path: Path | str,
    output_dir: Path | str,
    label: str,
    bounds_path: Path | str | None = None,
) -> None:
    """
    Extract image crops for detections in a GeoJSON file.

    For each feature in the input GeoJSON, resolves the source tile (via
    the ``source_tile`` property or spatial lookup against tile bounds),
    crops a context window centred on the detection, and saves the result
    as a PNG file.

    Args:
        geojson_path: Path to input GeoJSON with detection features.
        output_dir: Base output directory for cropped images.
        label: Label prefix for output files (e.g., "hard_negative_fp").
        bounds_path: Optional path to tile bounds GeoJSON for spatial
            lookup when ``source_tile`` is missing from features.
    """
    print(f"Mining {label} from {geojson_path}")

    try:
        gdf = gpd.read_file(geojson_path)
    except Exception as exc:
        print(f"Error reading {geojson_path}: {exc}")
        return

    print(f"Loaded {len(gdf)} features.")

    # Load tile bounds for spatial lookup fallback
    gdf_bounds = None
    if bounds_path:
        try:
            gdf_bounds = gpd.read_file(bounds_path)
        except Exception as exc:
            print(f"Error loading bounds {bounds_path}: {exc}")

    crop_dir = Path(output_dir) / label
    crop_dir.mkdir(parents=True, exist_ok=True)

    saved = 0
    for idx, row in gdf.iterrows():
        tile_id = row.get("source_tile")

        # Fallback: spatial lookup using tile bounds
        if not tile_id and gdf_bounds is not None:
            query_geom = row.geometry.centroid
            match = gdf_bounds[gdf_bounds.contains(query_geom)]
            if not match.empty:
                tile_id = match.iloc[0]["tile_name"]

        if not tile_id:
            continue

        tile_path = get_tile_path(tile_id)
        if not tile_path:
            continue

        img = crop_candidate(tile_path, row["geometry"])
        if img:
            fname = f"{label}_{idx}_{tile_id}.png"
            img.save(crop_dir / fname)
            saved += 1

    print(f"Saved {saved} {label} crops to {crop_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: python mine_hard_cases.py"
            " <fp_path> <fn_path> <output_dir> [bounds_path]"
        )
        sys.exit(1)

    fp_path = sys.argv[1]
    fn_path = sys.argv[2]
    out_dir = sys.argv[3]
    bounds = sys.argv[4] if len(sys.argv) > 4 else None

    mine_crops(fp_path, out_dir, "hard_negative_fp", bounds)
    mine_crops(fn_path, out_dir, "hard_positive_fn", bounds)
