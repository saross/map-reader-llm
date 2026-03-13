#!/usr/bin/env python3
"""
Generate GeoJSON bounds files for calibration and validation tile sets.

Creates Geographic JavaScript Object Notation (GeoJSON) polygon features for
each tile showing its geographic extent, useful for visualisation and spatial
analysis of tile coverage.

Usage::

    python scripts/generate_tile_bounds.py
    python scripts/generate_tile_bounds.py --tiles-dir inputs/tiles --output-dir outputs/results

Inputs:
    - Tile manifests: inputs/tiles/calibration_manifest.json,
      inputs/tiles/validation_manifest.json
    - Selection metadata: inputs/tiles/tile_selection_metadata.json
    - Per-map metadata: inputs/tiles/{map_name}/metadata.json

Outputs:
    - calibration_bounds.geojson  - Polygon bounds for calibration tiles
    - validation_bounds.geojson   - Polygon bounds for validation tiles

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

# Map sheet directories containing tile metadata
TILE_DIRS = [
    "K-35-052-4_32635",
    "K-35-053-3_Elenovo",
    "K-35-062-2_Rakovski",
    "K-35-078-1_Lesovo",
]

# All map sheets use Universal Transverse Mercator (UTM) zone 35N
# European Petroleum Survey Group (EPSG) code 32635
CRS_URN = "urn:ogc:def:crs:EPSG::32635"


def get_map_from_filename(filename: str) -> str:
    """Extract map name from tile filename.

    Splits on the ``_x`` separator that precedes the pixel coordinate portion
    of the filename.

    Args:
        filename: Tile filename like ``K-35-052-4_32635_x1344_y2240.png``.

    Returns:
        Map name like ``K-35-052-4_32635``.
    """
    parts = filename.rsplit("_x", 1)
    return parts[0]


def load_metadata(tiles_dir: Path) -> dict[str, list[float]]:
    """Load all tile metadata from map directories.

    Each map directory contains a ``metadata.json`` mapping tile filenames to
    lists of ``[min_x, min_y, pixel_size_x, pixel_size_y]``.

    Args:
        tiles_dir: Path to tiles directory.

    Returns:
        Dictionary mapping tile filenames to their georeferencing parameters.
    """
    all_metadata: dict[str, list[float]] = {}
    for map_name in TILE_DIRS:
        metadata_path = tiles_dir / map_name / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
                all_metadata.update(metadata)
    return all_metadata


def tile_to_polygon(
    filename: str,
    metadata: dict[str, list[float]],
    tile_size: int = TILE_SIZE,
) -> dict | None:
    """Convert tile metadata to a GeoJSON polygon feature.

    Constructs a rectangular polygon whose corners are derived from the tile's
    geographic origin and the tile dimensions in map units.

    Args:
        filename: Tile filename.
        metadata: All tile georeferencing metadata.
        tile_size: Tile dimension in pixels (default: TILE_SIZE from config).

    Returns:
        GeoJSON Feature dict, or ``None`` if tile not found in metadata.
    """
    if filename not in metadata:
        print(f"  Warning: {filename} not found in metadata")
        return None

    # Metadata format: [min_x, min_y, pixel_size_x, pixel_size_y]
    # min_y is the bottom edge (southernmost extent) of the tile
    meta = metadata[filename]
    min_x = meta[0]
    min_y = meta[1]
    pixel_size = meta[2]

    # Calculate tile extent (each tile is tile_size pixels square)
    extent = tile_size * pixel_size
    max_x = min_x + extent
    max_y = min_y + extent

    map_name = get_map_from_filename(filename)

    return {
        "type": "Feature",
        "properties": {
            "tile_name": filename,
            "map_name": map_name,
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [min_x, max_y],
                [max_x, max_y],
                [max_x, min_y],
                [min_x, min_y],
                [min_x, max_y],
            ]],
        },
    }


def create_bounds_geojson(
    tile_filenames: list[str],
    metadata: dict[str, list[float]],
    selection_metadata: dict,
    set_type: str,
    tile_size: int = TILE_SIZE,
) -> dict:
    """Create a GeoJSON FeatureCollection for a set of tiles.

    Builds polygon features for every tile in *tile_filenames* and enriches
    each feature with mound count and density from the selection metadata
    when available.

    Args:
        tile_filenames: List of tile filenames.
        metadata: Tile georeferencing metadata.
        selection_metadata: Tile selection metadata with mound counts.
        set_type: ``"calibration"`` or ``"validation"``.
        tile_size: Tile dimension in pixels (default: TILE_SIZE from config).

    Returns:
        GeoJSON FeatureCollection dict.
    """
    # Build lookup from selection metadata
    tile_info: dict[str, dict] = {}
    if set_type in selection_metadata:
        for tile in selection_metadata[set_type].get("tiles", []):
            tile_info[tile["filename"]] = {
                "mound_count": tile.get("mound_count", 0),
                "density": tile.get("density", "unknown"),
            }

    features: list[dict] = []
    for filename in tile_filenames:
        feature = tile_to_polygon(filename, metadata, tile_size=tile_size)
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
            "properties": {"name": CRS_URN},
        },
        "features": features,
    }


def validate_bounds(
    geojson_data: dict,
    metadata: dict[str, list[float]],
    n_samples: int = 3,
    tile_size: int = TILE_SIZE,
) -> bool:
    """Validate generated bounds against tile metadata.

    Spot-checks tiles by verifying that polygon corners match the expected
    values from metadata. Catches Y-axis inversions (E4) and other
    metadata misinterpretation bugs.

    The check verifies:

    - Polygon minX == metadata[0] (origin X)
    - Polygon minY == metadata[1] (origin Y, the BOTTOM edge)
    - Polygon width and height == tile_size * pixel_size

    Args:
        geojson_data: Generated GeoJSON FeatureCollection.
        metadata: Tile georeferencing metadata dict.
        n_samples: Number of tiles to spot-check.
        tile_size: Tile dimension in pixels (default: TILE_SIZE from config).

    Returns:
        True if all checks pass, False if any fail.
    """
    features = geojson_data.get("features", [])
    if not features:
        print("  Validation skipped: no features to check")
        return True

    checked = 0
    failed = False
    # Sub-millimetre tolerance for floating-point comparison
    tol = 0.001

    for feature in features[:n_samples]:
        tile_name = feature["properties"]["tile_name"]
        if tile_name not in metadata:
            continue

        meta = metadata[tile_name]
        expected_min_x = meta[0]
        expected_min_y = meta[1]  # This is minY (bottom edge), NOT maxY
        pixel_size = meta[2]
        expected_extent = tile_size * pixel_size

        # Extract polygon bounds from generated feature
        coords = feature["geometry"]["coordinates"][0]  # Outer ring
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        actual_min_x = min(xs)
        actual_max_x = max(xs)
        actual_min_y = min(ys)
        actual_max_y = max(ys)

        # Check origin matches metadata
        if abs(actual_min_x - expected_min_x) > tol:
            print(f"  FAIL: {tile_name} minX={actual_min_x}, expected {expected_min_x}")
            failed = True
        if abs(actual_min_y - expected_min_y) > tol:
            print(
                f"  FAIL: {tile_name} minY={actual_min_y}, expected {expected_min_y} "
                f"(Y-axis inversion?)"
            )
            failed = True

        # Check dimensions
        actual_width = actual_max_x - actual_min_x
        actual_height = actual_max_y - actual_min_y
        if abs(actual_width - expected_extent) > tol:
            print(f"  FAIL: {tile_name} width={actual_width}, expected {expected_extent}")
            failed = True
        if abs(actual_height - expected_extent) > tol:
            print(f"  FAIL: {tile_name} height={actual_height}, expected {expected_extent}")
            failed = True

        checked += 1

    if checked == 0:
        print("  Validation skipped: no tiles matched metadata")
        return True

    if failed:
        print(f"  Bounds validation FAILED ({checked} tiles checked)")
        return False

    print(f"  Bounds validation passed ({checked} tiles checked)")
    return True


def _generate_and_save_bounds(
    set_type: str,
    tile_filenames: list[str],
    metadata: dict[str, list[float]],
    selection_metadata: dict,
    outputs_dir: Path,
    tile_size: int = TILE_SIZE,
) -> None:
    """Generate, save, and validate a GeoJSON bounds file for one tile set.

    Args:
        set_type: ``"calibration"`` or ``"validation"``.
        tile_filenames: List of tile filenames for this set.
        metadata: Tile georeferencing metadata.
        selection_metadata: Tile selection metadata with mound counts.
        outputs_dir: Directory to write the GeoJSON output file.
        tile_size: Tile dimension in pixels (default: TILE_SIZE from config).

    Raises:
        SystemExit: If bounds validation fails.
    """
    print(f"\nGenerating {set_type} bounds GeoJSON...")
    geojson_data = create_bounds_geojson(
        tile_filenames, metadata, selection_metadata, set_type,
        tile_size=tile_size,
    )

    output_path = outputs_dir / f"{set_type}_bounds.geojson"
    with open(output_path, "w") as f:
        json.dump(geojson_data, f, indent=2)
    print(f"  Saved: {output_path}")
    print(f"  Features: {len(geojson_data['features'])}")

    if not validate_bounds(geojson_data, metadata, tile_size=tile_size):
        print(f"ERROR: {set_type.capitalize()} bounds validation failed. "
              f"Check metadata interpretation.")
        sys.exit(1)


def main() -> None:
    """Generate bounds GeoJSON files for calibration and validation tile sets."""
    parser = argparse.ArgumentParser(
        description="Generate GeoJSON bounds files for calibration and validation tile sets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Use default paths (inputs/tiles and outputs/results)
    python scripts/generate_tile_bounds.py

    # Specify custom paths
    python scripts/generate_tile_bounds.py \\
        --tiles-dir /path/to/tiles \\
        --output-dir /path/to/output

    # Generate bounds for 384×384 tiles
    python scripts/generate_tile_bounds.py \\
        --tiles-dir inputs/tiles_384 \\
        --tile-size 384 \\
        --output-dir outputs/results

Output Files:
    calibration_bounds.geojson  - Polygon bounds for calibration tiles
    validation_bounds.geojson   - Polygon bounds for validation tiles
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
    parser.add_argument(
        "--tile-size",
        type=int,
        default=None,
        help=f"Override tile size for extent calculation (default: {TILE_SIZE} from config)",
    )

    args = parser.parse_args()

    tiles_dir = args.tiles_dir
    outputs_dir = args.output_dir
    effective_tile_size = args.tile_size if args.tile_size is not None else TILE_SIZE

    print(f"Tile size for extent calculation: {effective_tile_size}")

    # Ensure output directory exists
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Validate required input files exist before loading
    print("Loading manifests...")
    manifest_paths = {
        "calibration": (tiles_dir / "calibration_manifest.json", "calibration manifest"),
        "validation": (tiles_dir / "validation_manifest.json", "validation manifest"),
        "selection": (tiles_dir / "tile_selection_metadata.json", "tile selection metadata"),
    }
    for path, description in manifest_paths.values():
        if not path.exists():
            print(f"ERROR: Required file not found: {path}")
            print(f"  Missing: {description}")
            sys.exit(1)

    with open(manifest_paths["calibration"][0]) as f:
        calibration_tiles = json.load(f)
    print(f"  Calibration tiles: {len(calibration_tiles)}")

    with open(manifest_paths["validation"][0]) as f:
        validation_tiles = json.load(f)
    print(f"  Validation tiles: {len(validation_tiles)}")

    with open(manifest_paths["selection"][0]) as f:
        selection_metadata = json.load(f)

    # Load tile georeferencing metadata
    print("\nLoading tile metadata...")
    metadata = load_metadata(tiles_dir)
    print(f"  Total tiles with metadata: {len(metadata)}")

    # Generate, save, and validate bounds for each tile set
    for set_type, tile_filenames in [
        ("calibration", calibration_tiles),
        ("validation", validation_tiles),
    ]:
        _generate_and_save_bounds(
            set_type, tile_filenames, metadata, selection_metadata, outputs_dir,
            tile_size=effective_tile_size,
        )

    print("\nDone!")


if __name__ == "__main__":
    main()
