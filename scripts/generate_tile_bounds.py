#!/usr/bin/env python3
"""
Generate GeoJSON bounds files for calibration and holdout tile sets.

Creates polygon features for each tile showing its geographic extent,
useful for visualisation and spatial analysis of tile coverage.

Usage:
    python scripts/generate_tile_bounds.py
    python scripts/generate_tile_bounds.py --tiles-dir inputs/tiles --output-dir outputs/results

Created: 2025-12-23
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TILE_SIZE


# Constants (TILE_SIZE imported from config.py)
TILE_DIRS = [
    "K-35-052-4_32635",
    "K-35-053-3_Elenovo",
    "K-35-062-2_Rakovski",
    "K-35-078-1_Lesovo"
]

# CRS mapping based on map sheet names
MAP_CRS = {
    "K-35-052-4_32635": "EPSG:32635",
    "K-35-053-3_Elenovo": "EPSG:32635",
    "K-35-062-2_Rakovski": "EPSG:32635",
    "K-35-078-1_Lesovo": "EPSG:32635"
}


def get_map_from_filename(filename: str) -> str:
    """
    Extract map name from tile filename.

    Args:
        filename: Tile filename like 'K-35-052-4_32635_x1344_y2240.png'

    Returns:
        Map name like 'K-35-052-4_32635'
    """
    parts = filename.rsplit('_x', 1)
    return parts[0]


def load_metadata(tiles_dir: Path) -> dict:
    """
    Load all tile metadata from map directories.

    Args:
        tiles_dir: Path to tiles directory

    Returns:
        Dictionary mapping tile filenames to [minX, maxY, pixel_size_x, pixel_size_y]
    """
    all_metadata = {}
    for map_name in TILE_DIRS:
        metadata_path = tiles_dir / map_name / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
                all_metadata.update(metadata)
    return all_metadata


def tile_to_polygon(filename: str, metadata: dict) -> dict | None:
    """
    Convert tile metadata to a GeoJSON polygon feature.

    Args:
        filename: Tile filename
        metadata: All tile metadata

    Returns:
        GeoJSON feature dict or None if tile not found in metadata
    """
    if filename not in metadata:
        print(f"  Warning: {filename} not found in metadata")
        return None

    # Metadata format: [minX, minY, pixel_size_x, pixel_size_y]
    # minY is the bottom edge (southernmost extent) of the tile
    meta = metadata[filename]
    min_x = meta[0]
    min_y = meta[1]
    pixel_size = meta[2]

    # Calculate tile extent (each tile is TILE_SIZE pixels square)
    max_x = min_x + (TILE_SIZE * pixel_size)
    max_y = min_y + (TILE_SIZE * pixel_size)

    # Extract mound info from the selection metadata if available
    map_name = get_map_from_filename(filename)

    return {
        "type": "Feature",
        "properties": {
            "tile_name": filename,
            "map_name": map_name
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [min_x, max_y],
                [max_x, max_y],
                [max_x, min_y],
                [min_x, min_y],
                [min_x, max_y]
            ]]
        }
    }


def create_bounds_geojson(
    tile_filenames: list,
    metadata: dict,
    selection_metadata: dict,
    set_type: str
) -> dict:
    """
    Create a GeoJSON FeatureCollection for a set of tiles.

    Args:
        tile_filenames: List of tile filenames
        metadata: Tile georeferencing metadata
        selection_metadata: Tile selection metadata with mound counts
        set_type: 'calibration' or 'holdout'

    Returns:
        GeoJSON FeatureCollection dict
    """
    # Build lookup from selection metadata
    tile_info = {}
    if set_type in selection_metadata:
        for tile in selection_metadata[set_type].get("tiles", []):
            tile_info[tile["filename"]] = {
                "mound_count": tile.get("mound_count", 0),
                "density": tile.get("density", "unknown")
            }

    features = []
    for filename in tile_filenames:
        feature = tile_to_polygon(filename, metadata)
        if feature:
            # Add selection metadata to properties
            if filename in tile_info:
                feature["properties"]["mound_count"] = tile_info[filename]["mound_count"]
                feature["properties"]["density"] = tile_info[filename]["density"]
            features.append(feature)

    return {
        "type": "FeatureCollection",
        "name": f"{set_type}_tile_bounds",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:EPSG::32635"
            }
        },
        "features": features
    }


def main():
    """Generate bounds GeoJSONs for calibration and holdout tile sets."""
    parser = argparse.ArgumentParser(
        description="Generate GeoJSON bounds files for calibration and holdout tile sets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Use default paths (inputs/tiles and outputs/results)
    python scripts/generate_tile_bounds.py

    # Specify custom paths
    python scripts/generate_tile_bounds.py \\
        --tiles-dir /path/to/tiles \\
        --output-dir /path/to/output

Output Files:
    calibration_bounds.geojson  - Polygon bounds for calibration tiles
    holdout_bounds.geojson      - Polygon bounds for holdout tiles
        """,
    )

    base_dir = Path(__file__).parent.parent

    parser.add_argument(
        "--tiles-dir",
        type=Path,
        default=base_dir / "inputs" / "tiles",
        help="Path to tiles directory containing manifests and metadata (default: inputs/tiles)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=base_dir / "outputs" / "results",
        help="Path to output directory for GeoJSON files (default: outputs/results)",
    )

    args = parser.parse_args()

    tiles_dir = args.tiles_dir
    outputs_dir = args.output_dir

    # Ensure output directory exists
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Load manifests
    print("Loading manifests...")
    calibration_path = tiles_dir / "calibration_manifest.json"
    holdout_path = tiles_dir / "holdout_manifest.json"
    selection_path = tiles_dir / "tile_selection_metadata.json"

    # Validate manifest files exist before loading
    required_files = [
        (calibration_path, "calibration manifest"),
        (holdout_path, "holdout manifest"),
        (selection_path, "tile selection metadata"),
    ]
    for path, description in required_files:
        if not path.exists():
            print(f"ERROR: Required file not found: {path}")
            print(f"  Missing: {description}")
            sys.exit(1)

    with open(calibration_path) as f:
        calibration_tiles = json.load(f)
    print(f"  Calibration tiles: {len(calibration_tiles)}")

    with open(holdout_path) as f:
        holdout_tiles = json.load(f)
    print(f"  Holdout tiles: {len(holdout_tiles)}")

    with open(selection_path) as f:
        selection_metadata = json.load(f)

    # Load tile georeferencing metadata
    print("\nLoading tile metadata...")
    metadata = load_metadata(tiles_dir)
    print(f"  Total tiles with metadata: {len(metadata)}")

    # Generate calibration bounds
    print("\nGenerating calibration bounds GeoJSON...")
    calibration_geojson = create_bounds_geojson(
        calibration_tiles, metadata, selection_metadata, "calibration"
    )
    calibration_output = outputs_dir / "calibration_bounds.geojson"
    with open(calibration_output, 'w') as f:
        json.dump(calibration_geojson, f, indent=2)
    print(f"  Saved: {calibration_output}")
    print(f"  Features: {len(calibration_geojson['features'])}")

    # Generate holdout bounds
    print("\nGenerating holdout bounds GeoJSON...")
    holdout_geojson = create_bounds_geojson(
        holdout_tiles, metadata, selection_metadata, "holdout"
    )
    holdout_output = outputs_dir / "holdout_bounds.geojson"
    with open(holdout_output, 'w') as f:
        json.dump(holdout_geojson, f, indent=2)
    print(f"  Saved: {holdout_output}")
    print(f"  Features: {len(holdout_geojson['features'])}")

    print("\nDone!")


if __name__ == "__main__":
    main()
