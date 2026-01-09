#!/usr/bin/env python3
"""
Tile Size Pilot: Tile Generation Script
========================================

Description:
    Generates tiles at 3 sizes (1024, 512, 256) for each pilot region.
    All sizes cover the same geographic area with 12.5% overlap.

    For each region:
    - 1 large tile (1024×1024)
    - 4 medium tiles (512×512) in a 2×2 grid
    - 16 small tiles (256×256) in a 4×4 grid

Usage:
    python scripts/generate_pilot_tiles.py

Output:
    - inputs/pilot_tiles/1024/ (10 tiles)
    - inputs/pilot_tiles/512/ (40 tiles)
    - inputs/pilot_tiles/256/ (160 tiles)
    - inputs/pilot_tiles/{size}/ground_truth.json

Author: Shawn Ross, Adela Sobotkova
Licence: Apache 2.0
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Setup Project Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    import rasterio
    from rasterio.windows import Window
    import numpy as np
    from PIL import Image
    import geojson
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Run: pip install rasterio numpy pillow geojson")
    sys.exit(1)

# Configuration
RASTERS_DIR = BASE_DIR / "inputs" / "rasters"
PILOT_DIR = BASE_DIR / "inputs" / "pilot"
OUTPUT_DIR = BASE_DIR / "inputs" / "pilot_tiles"
VECTORS_DIR = BASE_DIR / "inputs" / "vectors"
GROUND_TRUTH_FILE = VECTORS_DIR / "mounds-reference.geojson"

# Tile sizes and their configurations
TILE_CONFIGS = {
    1024: {'overlap_fraction': 0.125, 'grid_size': 1},  # 1 tile
    512: {'overlap_fraction': 0.125, 'grid_size': 2},   # 2×2 = 4 tiles
    256: {'overlap_fraction': 0.125, 'grid_size': 4},   # 4×4 = 16 tiles
}


def load_region_manifest() -> List[Dict]:
    """Load the pilot region manifest."""
    manifest_path = PILOT_DIR / "pilot_region_manifest.json"
    with open(manifest_path, 'r') as f:
        return json.load(f)


def load_ground_truth() -> Dict[str, List[Dict]]:
    """
    Load ground truth mounds organised by map name.

    Returns:
        Dictionary mapping map names to lists of mound info dicts.
    """
    with open(GROUND_TRUTH_FILE, 'r') as f:
        gj = geojson.load(f)

    mounds_by_map: Dict[str, List[Dict]] = {}

    for feature in gj['features']:
        map_name = feature['properties'].get('Map', '')
        if not map_name:
            continue

        symbol = feature['properties'].get('Symbol', 'Unknown')

        # Handle MultiPoint geometry
        geom = feature['geometry']
        coords = []
        if geom['type'] == 'MultiPoint':
            coords = geom['coordinates']
        elif geom['type'] == 'Point':
            coords = [geom['coordinates']]

        for coord in coords:
            if map_name not in mounds_by_map:
                mounds_by_map[map_name] = []
            mounds_by_map[map_name].append({
                'geo_x': coord[0],
                'geo_y': coord[1],
                'symbol': symbol
            })

    return mounds_by_map


def geo_to_pixel(x: float, y: float, transform) -> Tuple[float, float]:
    """Convert geographic coordinates to pixel coordinates."""
    col, row = ~transform * (x, y)
    return col, row


def pixel_to_geo(col: float, row: float, transform) -> Tuple[float, float]:
    """Convert pixel coordinates to geographic coordinates."""
    x, y = transform * (col, row)
    return x, y


def generate_tile_grid(
    region_centre_px: Tuple[int, int],
    tile_size: int,
    grid_size: int,
    overlap_fraction: float
) -> List[Dict]:
    """
    Generate tile origins for a grid covering the region.

    Args:
        region_centre_px: Centre of the 1024×1024 region in pixels
        tile_size: Size of tiles to generate
        grid_size: Number of tiles per dimension (1, 2, or 4)
        overlap_fraction: Overlap as fraction of tile size

    Returns:
        List of tile info dicts with origin coordinates.
    """
    stride = int(tile_size * (1 - overlap_fraction))
    region_size = 1024  # Always cover 1024×1024 region

    # Calculate the total extent covered by the grid
    # For grid_size=2 (512px tiles with 12.5% overlap = 448px stride):
    #   Total = tile_size + (grid_size-1) * stride = 512 + 1*448 = 960
    # We need to center this within the 1024 region

    total_grid_extent = tile_size + (grid_size - 1) * stride

    # Offset to centre the grid within the region
    centre_col, centre_row = region_centre_px
    region_top_left_col = centre_col - region_size // 2
    region_top_left_row = centre_row - region_size // 2

    # Centre the tile grid within the region
    grid_offset = (region_size - total_grid_extent) // 2

    tiles = []
    for row_idx in range(grid_size):
        for col_idx in range(grid_size):
            origin_col = region_top_left_col + grid_offset + col_idx * stride
            origin_row = region_top_left_row + grid_offset + row_idx * stride

            tiles.append({
                'origin_px': (origin_col, origin_row),
                'tile_size': tile_size,
                'grid_position': (col_idx, row_idx)
            })

    return tiles


def extract_tile(
    raster_path: Path,
    origin_px: Tuple[int, int],
    tile_size: int
) -> Tuple[np.ndarray, Any]:
    """
    Extract a tile from the raster.

    Returns:
        Tuple of (image array, transform for the tile).
    """
    with rasterio.open(raster_path) as src:
        col, row = origin_px

        window = Window(col, row, tile_size, tile_size)

        # Read the data
        data = src.read(window=window)

        # Get the transform for this window
        tile_transform = src.window_transform(window)

        return data, tile_transform


def save_tile_with_worldfile(
    data: np.ndarray,
    output_path: Path,
    transform
):
    """
    Save tile as PNG with world file for georeferencing.

    Args:
        data: Image data array (bands, height, width)
        output_path: Path to save PNG
        transform: Affine transform for the tile
    """
    # Convert to PIL Image
    if data.shape[0] == 3:
        img_data = data.transpose(1, 2, 0)
    elif data.shape[0] == 4:
        img_data = data[:3].transpose(1, 2, 0)  # RGB only
    else:
        img_data = data[0]  # Grayscale

    img = Image.fromarray(img_data.astype(np.uint8))
    img.save(output_path)

    # Write world file (.pgw)
    worldfile_path = output_path.with_suffix('.pgw')
    with open(worldfile_path, 'w') as f:
        f.write(f"{transform.a}\n")   # Pixel size in x
        f.write(f"{transform.d}\n")   # Rotation (usually 0)
        f.write(f"{transform.b}\n")   # Rotation (usually 0)
        f.write(f"{transform.e}\n")   # Pixel size in y (negative)
        f.write(f"{transform.c}\n")   # X coordinate of upper-left corner
        f.write(f"{transform.f}\n")   # Y coordinate of upper-left corner


def compute_tile_ground_truth(
    tile_origin_px: Tuple[int, int],
    tile_size: int,
    mounds: List[Dict],
    raster_transform
) -> List[Dict]:
    """
    Compute which mounds fall within a tile.

    Returns:
        List of mounds with their pixel coordinates relative to tile.
    """
    col_origin, row_origin = tile_origin_px

    tile_mounds = []
    for mound in mounds:
        # Convert mound geo coords to pixel coords
        mound_col, mound_row = geo_to_pixel(
            mound['geo_x'], mound['geo_y'], raster_transform
        )

        # Check if within tile bounds
        if (col_origin <= mound_col < col_origin + tile_size and
            row_origin <= mound_row < row_origin + tile_size):
            # Convert to tile-relative coordinates
            rel_col = mound_col - col_origin
            rel_row = mound_row - row_origin

            tile_mounds.append({
                'pixel_x': rel_col,
                'pixel_y': rel_row,
                'symbol': mound['symbol']
            })

    return tile_mounds


def main():
    print("Loading region manifest...")
    regions = load_region_manifest()
    print(f"Found {len(regions)} regions")

    print("Loading ground truth...")
    mounds_by_map = load_ground_truth()
    total_mounds = sum(len(m) for m in mounds_by_map.values())
    print(f"Loaded {total_mounds} mounds across {len(mounds_by_map)} maps")

    # Create output directories
    for size in TILE_CONFIGS:
        (OUTPUT_DIR / str(size)).mkdir(parents=True, exist_ok=True)

    # Track ground truth per size
    ground_truth_by_size = {size: {} for size in TILE_CONFIGS}

    # Track tile counts
    tile_counts = {size: 0 for size in TILE_CONFIGS}

    for region in regions:
        region_id = region['region_id']
        map_name = region['map_name']
        centre_px = tuple(region['centre_px'])

        print(f"\nProcessing {region_id} ({map_name})...")

        # Find the raster file
        raster_path = RASTERS_DIR / f"{map_name}.tif"
        if not raster_path.exists():
            print(f"  Warning: Raster not found: {raster_path}")
            continue

        # Get raster transform
        with rasterio.open(raster_path) as src:
            raster_transform = src.transform

        # Get mounds for this map
        map_mounds = mounds_by_map.get(map_name, [])

        # Generate tiles at each size
        for size, config in TILE_CONFIGS.items():
            grid_size = config['grid_size']
            overlap_fraction = config['overlap_fraction']

            # Generate tile grid
            tiles = generate_tile_grid(
                centre_px, size, grid_size, overlap_fraction
            )

            output_dir = OUTPUT_DIR / str(size)

            for tile_info in tiles:
                origin_px = tile_info['origin_px']
                grid_pos = tile_info['grid_position']

                # Generate tile filename
                tile_name = (
                    f"{map_name}_{region_id}_"
                    f"x{origin_px[0]}_y{origin_px[1]}.png"
                )
                output_path = output_dir / tile_name

                # Extract and save tile
                try:
                    data, tile_transform = extract_tile(
                        raster_path, origin_px, size
                    )
                    save_tile_with_worldfile(data, output_path, tile_transform)
                    tile_counts[size] += 1

                    # Compute ground truth
                    tile_mounds = compute_tile_ground_truth(
                        origin_px, size, map_mounds, raster_transform
                    )

                    ground_truth_by_size[size][tile_name] = {
                        'region_id': region_id,
                        'map_name': map_name,
                        'origin_px': list(origin_px),
                        'tile_size': size,
                        'mound_count': len(tile_mounds),
                        'mounds': tile_mounds
                    }

                except Exception as e:
                    print(f"  Error extracting tile {tile_name}: {e}")

            print(f"  Generated {len(tiles)} tiles at {size}px")

    # Save ground truth files
    print("\nSaving ground truth files...")
    for size, gt_data in ground_truth_by_size.items():
        gt_path = OUTPUT_DIR / str(size) / "ground_truth.json"
        with open(gt_path, 'w') as f:
            json.dump(gt_data, f, indent=2)
        print(f"  {gt_path}: {len(gt_data)} tiles")

    # Print summary
    print("\nTile generation complete:")
    for size, count in tile_counts.items():
        print(f"  {size}px: {count} tiles")
    print(f"  Total: {sum(tile_counts.values())} tiles")


if __name__ == "__main__":
    main()
