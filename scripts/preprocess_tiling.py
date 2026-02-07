#!/usr/bin/env python3
"""
Preprocess Tiling Script
========================

Splits large GeoTIFF (Geographic Tagged Image File Format) input maps into
smaller, manageable tiles (default 512x512) for processing by a Vision Language
Model (VLM). Preserves geospatial metadata for each tile by generating
accompanying World Files (.pgw) and Auxiliary Extensible Markup Language (XML)
files (.aux.xml).

Usage::

    python scripts/preprocess_tiling.py

Inputs:
    - Raster scans from ``inputs/rasters/*.tif``

Outputs:
    - Tiles in ``inputs/tiles/<map_name>/*.{png,pgw,png.aux.xml}``

Author: Shawn Ross, Adela Sobotkova
Licence: Apache 2.0
"""

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.windows import Window
from tqdm import tqdm

# Add parent directory to path so config module can be imported
sys.path.append(str(Path(__file__).parent.parent))
from config import RASTERS_DIR, STRIDE, TILE_SIZE, TILES_DIR  # noqa: E402


def tile_raster(input_path: Path) -> None:
    """
    Split a single GeoTIFF into tiles with geospatial sidecar files.

    Process:
        1. Reads the source GeoTIFF.
        2. Iterates through the raster using STRIDE spacing (TILE_SIZE - OVERLAP).
        3. Extracts the Red/Green/Blue (RGB) pixel data (converting single-band
           to RGB if necessary).
        4. Saves the tile as a Portable Network Graphics (PNG) file.
        5. Calculates the specific geotransform for that tile's top-left corner.
        6. Writes a World File (.pgw) and Aux XML (.png.aux.xml) to preserve
           Coordinate Reference System (CRS) and transform information.

    Args:
        input_path: Path to the source .tif file.
    """
    map_name = input_path.stem

    # Create output directory for this map
    map_output_dir = TILES_DIR / map_name
    map_output_dir.mkdir(parents=True, exist_ok=True)

    metadata: dict[str, list] = {}

    with rasterio.open(input_path) as src:
        height = src.height
        width = src.width

        # Generate tile windows using STRIDE (distance between tile origins).
        # Tiles at edges may extend beyond the raster boundary; rasterio's
        # boundless read handles this by padding with fill_value.
        windows = [
            (x, y, Window(x, y, TILE_SIZE, TILE_SIZE))
            for y in range(0, height, STRIDE)
            for x in range(0, width, STRIDE)
        ]

        print(f"Processing {len(windows)} tiles for {map_name}...")

        for x, y, window in tqdm(windows):
            # Read pixel data; boundless=True pads with 0 (black) beyond edges
            img_data = src.read(window=window, boundless=True, fill_value=0)

            # Rasterio reads as (bands, height, width); transpose to (H, W, B) for Pillow
            img_data = img_data.transpose(1, 2, 0)

            # Normalise to 3-band RGB
            if img_data.shape[2] == 1:
                img_data = np.dstack([img_data] * 3)
            elif img_data.shape[2] > 3:
                # Drop alpha channel or extra bands, keeping only RGB
                img_data = img_data[:, :, :3]

            img = Image.fromarray(img_data.astype(np.uint8), "RGB")

            tile_filename = f"{map_name}_x{x}_y{y}.png"
            tile_path = map_output_dir / tile_filename
            img.save(tile_path)

            # --- Spatial metadata sidecar files ---

            # Compute the affine transform for this tile's window
            window_transform = rasterio.windows.transform(window, src.transform)

            # World File (.pgw) expects the centre of the top-left pixel, not
            # its corner. Offset by half a pixel in each axis.
            res_x = window_transform.a
            res_y = window_transform.e  # Usually negative
            centre_x = window_transform.c + (res_x / 2.0)
            centre_y = window_transform.f + (res_y / 2.0)

            pgw_content = f"{res_x}\n0.0\n0.0\n{res_y}\n{centre_x}\n{centre_y}"
            tile_path.with_suffix(".pgw").write_text(pgw_content)

            # PAMDataset XML (.aux.xml) stores the CRS so that
            # Quantum GIS (QGIS) and Geospatial Data Abstraction Library (GDAL)
            # can recognise it automatically.
            crs_wkt = src.crs.to_wkt()
            aux_xml_content = (
                f"<PAMDataset>\n  <SRS>{crs_wkt}</SRS>\n</PAMDataset>"
            )
            tile_path.with_suffix(".png.aux.xml").write_text(aux_xml_content)

            # Store legacy metadata as backup (west bound, south bound, pixel resolution)
            west, south, _east, _north = rasterio.windows.bounds(window, src.transform)
            metadata[tile_filename] = [west, south, src.res[0], src.res[1]]

    # Write legacy metadata JSON (JavaScript Object Notation)
    metadata_path = map_output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    file_count = len(windows) * 3
    print(
        f"Finished tiling {map_name}. "
        f"Saved {file_count} files (PNG + PGW + aux.xml) to {map_output_dir}"
    )


def main() -> None:
    """Process all GeoTIFF files in the rasters input directory."""
    tif_files = list(RASTERS_DIR.glob("*.tif"))

    if not tif_files:
        print(f"No .tif files found in {RASTERS_DIR}")
        return

    for tif_path in tif_files:
        print(f"Starting {tif_path.name}...")
        try:
            tile_raster(tif_path)
        except Exception as exc:
            print(f"Error processing {tif_path.name}: {exc}")


if __name__ == "__main__":
    main()
