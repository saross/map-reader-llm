#!/usr/bin/env python3
"""
Tile Size Pilot: Region Selection Script
=========================================

Description:
    Selects 10 regions for the tile size pilot experiment, stratified by
    mound density. Each region is defined by a centre point that can
    accommodate a 1024×1024 tile (512px from edges).

Usage:
    python scripts/select_pilot_tiles.py [--seed SEED]

Output:
    - inputs/pilot/pilot_region_manifest.json
    - inputs/pilot/pilot_selection_metadata.json

Author: Shawn Ross, Adela Sobotkova
Licence: Apache 2.0
"""

import sys
import json
import random
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any

# Setup Project Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    import rasterio
    import geojson
    from shapely.geometry import Point, box
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Run: pip install rasterio geojson shapely")
    sys.exit(1)

# Configuration
RASTERS_DIR = BASE_DIR / "inputs" / "rasters"
VECTORS_DIR = BASE_DIR / "inputs" / "vectors"
PILOT_DIR = BASE_DIR / "inputs" / "pilot"
GROUND_TRUTH_FILE = VECTORS_DIR / "mounds-reference.geojson"

# Target counts per density category
TARGET_EMPTY = 3   # 0 mounds
TARGET_SPARSE = 4  # 1-2 mounds
TARGET_DENSE = 3   # 3+ mounds
TOTAL_REGIONS = TARGET_EMPTY + TARGET_SPARSE + TARGET_DENSE

# Tile size for boundary calculations
LARGE_TILE_SIZE = 1024
MARGIN = LARGE_TILE_SIZE // 2  # 512px from edges


def load_ground_truth() -> Dict[str, List[Tuple[float, float]]]:
    """
    Load ground truth mounds and organise by map name.

    Returns:
        Dictionary mapping map names to lists of (x, y) coordinates in CRS units.
    """
    with open(GROUND_TRUTH_FILE, 'r') as f:
        gj = geojson.load(f)

    mounds_by_map: Dict[str, List[Tuple[float, float]]] = {}

    for feature in gj['features']:
        map_name = feature['properties'].get('Map', '')
        if not map_name:
            continue

        # Handle MultiPoint geometry
        geom = feature['geometry']
        if geom['type'] == 'MultiPoint':
            for coord in geom['coordinates']:
                if map_name not in mounds_by_map:
                    mounds_by_map[map_name] = []
                mounds_by_map[map_name].append((coord[0], coord[1]))
        elif geom['type'] == 'Point':
            if map_name not in mounds_by_map:
                mounds_by_map[map_name] = []
            mounds_by_map[map_name].append((geom['coordinates'][0], geom['coordinates'][1]))

    return mounds_by_map


def get_raster_info(raster_path: Path) -> Dict[str, Any]:
    """
    Get raster metadata including dimensions and transform.

    Returns:
        Dictionary with width, height, transform, and bounds.
    """
    with rasterio.open(raster_path) as src:
        return {
            'width': src.width,
            'height': src.height,
            'transform': src.transform,
            'bounds': src.bounds,
            'crs': src.crs
        }


def geo_to_pixel(x: float, y: float, transform) -> Tuple[int, int]:
    """Convert geographic coordinates to pixel coordinates."""
    col, row = ~transform * (x, y)
    return int(col), int(row)


def pixel_to_geo(col: int, row: int, transform) -> Tuple[float, float]:
    """Convert pixel coordinates to geographic coordinates."""
    x, y = transform * (col, row)
    return x, y


def count_mounds_in_region(
    centre_px: Tuple[int, int],
    tile_size: int,
    mounds: List[Tuple[float, float]],
    transform
) -> int:
    """
    Count mounds within a tile region.

    Args:
        centre_px: Centre point in pixel coordinates (col, row)
        tile_size: Size of tile in pixels
        mounds: List of mound coordinates in CRS units
        transform: Rasterio transform for coordinate conversion

    Returns:
        Number of mounds within the tile bounds.
    """
    half = tile_size // 2
    col, row = centre_px

    # Tile bounds in pixel coordinates
    min_col = col - half
    max_col = col + half
    min_row = row - half
    max_row = row + half

    count = 0
    for mx, my in mounds:
        mcol, mrow = geo_to_pixel(mx, my, transform)
        if min_col <= mcol < max_col and min_row <= mrow < max_row:
            count += 1

    return count


def classify_density(mound_count: int) -> str:
    """Classify region by mound density."""
    if mound_count == 0:
        return "empty"
    elif mound_count <= 2:
        return "sparse"
    else:
        return "dense"


def generate_candidate_regions(
    raster_info: Dict,
    mounds: List[Tuple[float, float]],
    step: int = 256
) -> List[Dict]:
    """
    Generate candidate region centre points with mound counts.

    Args:
        raster_info: Raster metadata
        mounds: List of mound coordinates
        step: Spacing between candidate points in pixels

    Returns:
        List of candidate regions with centre, mound_count, density.
    """
    width = raster_info['width']
    height = raster_info['height']
    transform = raster_info['transform']

    candidates = []

    # Valid range for centre points (512px margin for 1024 tile)
    for row in range(MARGIN, height - MARGIN, step):
        for col in range(MARGIN, width - MARGIN, step):
            mound_count = count_mounds_in_region(
                (col, row), LARGE_TILE_SIZE, mounds, transform
            )

            # Convert centre to geographic coordinates
            geo_x, geo_y = pixel_to_geo(col, row, transform)

            candidates.append({
                'centre_px': (col, row),
                'centre_geo': (geo_x, geo_y),
                'mound_count': mound_count,
                'density': classify_density(mound_count)
            })

    return candidates


def select_stratified_regions(
    all_candidates: Dict[str, List[Dict]],
    seed: int
) -> List[Dict]:
    """
    Select stratified regions across all maps.

    Args:
        all_candidates: Dictionary mapping map names to candidate lists
        seed: Random seed for reproducibility

    Returns:
        List of 10 selected regions.
    """
    random.seed(seed)

    # Collect candidates by density across all maps
    by_density = {'empty': [], 'sparse': [], 'dense': []}

    for map_name, candidates in all_candidates.items():
        for cand in candidates:
            cand['map_name'] = map_name
            by_density[cand['density']].append(cand)

    # Shuffle each category
    for density in by_density:
        random.shuffle(by_density[density])

    # Select required number from each category
    selected = []

    # Select empty regions
    if len(by_density['empty']) < TARGET_EMPTY:
        print(f"Warning: Only {len(by_density['empty'])} empty regions available "
              f"(need {TARGET_EMPTY})")
    selected.extend(by_density['empty'][:TARGET_EMPTY])

    # Select sparse regions
    if len(by_density['sparse']) < TARGET_SPARSE:
        print(f"Warning: Only {len(by_density['sparse'])} sparse regions available "
              f"(need {TARGET_SPARSE})")
    selected.extend(by_density['sparse'][:TARGET_SPARSE])

    # Select dense regions
    if len(by_density['dense']) < TARGET_DENSE:
        print(f"Warning: Only {len(by_density['dense'])} dense regions available "
              f"(need {TARGET_DENSE})")
    selected.extend(by_density['dense'][:TARGET_DENSE])

    return selected


def main():
    parser = argparse.ArgumentParser(
        description="Select regions for tile size pilot experiment"
    )
    parser.add_argument(
        '--seed', type=int, default=None,
        help="Random seed (default: timestamp-based)"
    )
    args = parser.parse_args()

    # Generate seed from timestamp if not provided
    if args.seed is None:
        seed = int(datetime.now().timestamp())
    else:
        seed = args.seed

    print(f"Random seed: {seed}")
    print(f"Loading ground truth from {GROUND_TRUTH_FILE}...")

    # Load ground truth
    mounds_by_map = load_ground_truth()
    print(f"Loaded mounds for {len(mounds_by_map)} maps:")
    for map_name, mounds in mounds_by_map.items():
        print(f"  {map_name}: {len(mounds)} mounds")

    # Generate candidates for each map
    all_candidates = {}

    for raster_file in RASTERS_DIR.glob("*.tif"):
        map_name = raster_file.stem
        print(f"\nProcessing {map_name}...")

        raster_info = get_raster_info(raster_file)
        print(f"  Dimensions: {raster_info['width']}×{raster_info['height']}")

        mounds = mounds_by_map.get(map_name, [])
        candidates = generate_candidate_regions(raster_info, mounds)
        all_candidates[map_name] = candidates

        # Count by density
        density_counts = {}
        for c in candidates:
            d = c['density']
            density_counts[d] = density_counts.get(d, 0) + 1
        print(f"  Candidates: {len(candidates)} total "
              f"(empty: {density_counts.get('empty', 0)}, "
              f"sparse: {density_counts.get('sparse', 0)}, "
              f"dense: {density_counts.get('dense', 0)})")

    # Select stratified regions
    print(f"\nSelecting {TOTAL_REGIONS} regions...")
    selected = select_stratified_regions(all_candidates, seed)

    # Verify selection
    density_counts = {}
    for r in selected:
        d = r['density']
        density_counts[d] = density_counts.get(d, 0) + 1

    print(f"Selected {len(selected)} regions:")
    print(f"  Empty: {density_counts.get('empty', 0)}")
    print(f"  Sparse: {density_counts.get('sparse', 0)}")
    print(f"  Dense: {density_counts.get('dense', 0)}")

    # Create output directory
    PILOT_DIR.mkdir(parents=True, exist_ok=True)

    # Prepare manifest
    manifest = []
    for i, region in enumerate(selected):
        manifest.append({
            'region_id': f'pilot_region_{i:02d}',
            'map_name': region['map_name'],
            'centre_px': list(region['centre_px']),
            'centre_geo': list(region['centre_geo']),
            'mound_count': region['mound_count'],
            'density': region['density']
        })

    # Save manifest
    manifest_path = PILOT_DIR / "pilot_region_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nSaved manifest to {manifest_path}")

    # Save metadata
    metadata = {
        'created': datetime.now(timezone.utc).isoformat(),
        'random_seed': seed,
        'parameters': {
            'large_tile_size': LARGE_TILE_SIZE,
            'margin': MARGIN,
            'target_empty': TARGET_EMPTY,
            'target_sparse': TARGET_SPARSE,
            'target_dense': TARGET_DENSE
        },
        'selection_summary': {
            'total_regions': len(selected),
            'empty': density_counts.get('empty', 0),
            'sparse': density_counts.get('sparse', 0),
            'dense': density_counts.get('dense', 0)
        },
        'reproducibility_note': (
            'This pilot selection can be reproduced by running this script '
            f'with --seed {seed}'
        )
    }

    metadata_path = PILOT_DIR / "pilot_selection_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to {metadata_path}")

    # Print selected regions
    print("\nSelected regions:")
    for r in manifest:
        print(f"  {r['region_id']}: {r['map_name']} "
              f"centre=({r['centre_px'][0]}, {r['centre_px'][1]}) "
              f"mounds={r['mound_count']} ({r['density']})")


if __name__ == "__main__":
    main()
