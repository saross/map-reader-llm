#!/usr/bin/env python3
"""
Select tiles by geographic area overlap with a reference tile set.

Identifies tiles from a new tiling grid (e.g., 384×384) whose geographic
extents overlap the validation area defined by an existing tile set
(e.g., the 60 validation tiles at 512×512). This enables fair comparison
across tile sizes by ensuring both evaluate the same geographic region
against the same ground truth.

Usage::

    # Select 384 tiles covering the 512 validation area
    python scripts/select_tiles_by_area.py \\
        --reference-bounds outputs/results/validation_bounds.geojson \\
        --new-tiles-dir inputs/tiles_384 \\
        --tile-size 384 \\
        --output-dir inputs/tiles_384

    # Dry run to preview selection without writing files
    python scripts/select_tiles_by_area.py \\
        --reference-bounds outputs/results/validation_bounds.geojson \\
        --new-tiles-dir inputs/tiles_384 \\
        --tile-size 384 \\
        --output-dir inputs/tiles_384 \\
        --dry-run

Inputs:
    - Reference bounds GeoJSON (e.g., ``validation_bounds.geojson``)
    - New tiles directory with per-map ``metadata.json`` files

Outputs:
    - ``validation_manifest.json`` — list of tile filenames for the new grid
    - ``tile_selection_metadata.json`` — selection parameters and statistics

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from shapely.geometry import box, shape
from shapely.ops import unary_union

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Map sheet directories (same across all tile sizes)
TILE_DIRS = [
    "K-35-052-4_32635",
    "K-35-053-3_Elenovo",
    "K-35-062-2_Rakovski",
    "K-35-078-1_Lesovo",
]


def load_reference_bounds(bounds_path: Path) -> list:
    """Load reference tile bounds from a GeoJSON file.

    Args:
        bounds_path: Path to the reference bounds GeoJSON
            (e.g., ``validation_bounds.geojson``).

    Returns:
        List of Shapely geometry objects representing tile extents.
    """
    with open(bounds_path) as f:
        data = json.load(f)

    geometries = []
    for feature in data.get("features", []):
        geom = shape(feature["geometry"])
        geometries.append(geom)

    return geometries


def load_tile_metadata(tiles_dir: Path) -> dict[str, list[float]]:
    """Load metadata.json from each map directory.

    Args:
        tiles_dir: Directory containing map subdirectories with metadata.json.

    Returns:
        Dict mapping tile filenames to [min_x, min_y, pixel_size_x, pixel_size_y].
    """
    all_metadata: dict[str, list[float]] = {}
    for map_name in TILE_DIRS:
        metadata_path = tiles_dir / map_name / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
                all_metadata.update(metadata)
        else:
            print(f"  Warning: No metadata found for {map_name}")
    return all_metadata


def tile_extent(
    filename: str,
    metadata: dict[str, list[float]],
    tile_size: int,
) -> box | None:
    """Compute the geographic extent of a tile as a Shapely box.

    Args:
        filename: Tile filename.
        metadata: Tile georeferencing metadata.
        tile_size: Tile dimension in pixels.

    Returns:
        Shapely box geometry, or None if tile not in metadata.
    """
    if filename not in metadata:
        return None

    meta = metadata[filename]
    min_x = meta[0]
    min_y = meta[1]
    pixel_size = meta[2]

    extent = tile_size * pixel_size
    max_x = min_x + extent
    max_y = min_y + extent

    return box(min_x, min_y, max_x, max_y)


def select_overlapping_tiles(
    reference_geometries: list,
    new_metadata: dict[str, list[float]],
    tile_size: int,
    min_overlap: float = 0.0,
) -> list[str]:
    """Select tiles from the new grid that overlap the reference area.

    Computes the union of all reference tile extents, then checks each
    tile in the new grid for intersection with that union. Tiles whose
    overlap fraction is below ``min_overlap`` are discarded — this trims
    peripheral tiles that barely touch the reference area, reducing the
    excess geographic footprint.

    Args:
        reference_geometries: List of Shapely geometries from the reference set.
        new_metadata: Metadata for all tiles in the new grid.
        tile_size: Tile dimension in pixels for the new grid.
        min_overlap: Minimum fraction of tile area that must overlap
            the reference area (0.0–1.0). Tiles below this threshold
            are excluded. Default 0.0 (any overlap).

    Returns:
        Sorted list of tile filenames that overlap the reference area.
    """
    # Build union of reference area
    reference_union = unary_union(reference_geometries)
    print(f"  Reference area bounds: {reference_union.bounds}")
    print(f"  Reference area: {reference_union.area:.1f} sq metres")

    # Check each new tile for overlap, applying minimum overlap threshold
    selected = []
    skipped_below_threshold = 0
    for filename in sorted(new_metadata.keys()):
        extent = tile_extent(filename, new_metadata, tile_size)
        if extent is not None and extent.intersects(reference_union):
            if min_overlap > 0:
                overlap_frac = extent.intersection(reference_union).area / extent.area
                if overlap_frac < min_overlap:
                    skipped_below_threshold += 1
                    continue
            selected.append(filename)

    if skipped_below_threshold > 0:
        print(f"  Skipped {skipped_below_threshold} tiles below "
              f"{min_overlap:.0%} overlap threshold")

    return selected


def main() -> None:
    """Parse arguments and select tiles by geographic area overlap."""
    parser = argparse.ArgumentParser(
        description="Select tiles from a new grid that cover the same area as a reference tile set",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Select 384 tiles covering the 512 validation area
  python scripts/select_tiles_by_area.py \\
      --reference-bounds outputs/results/validation_bounds.geojson \\
      --new-tiles-dir inputs/tiles_384 \\
      --tile-size 384 \\
      --output-dir inputs/tiles_384

  # Preview selection without writing
  python scripts/select_tiles_by_area.py \\
      --reference-bounds outputs/results/validation_bounds.geojson \\
      --new-tiles-dir inputs/tiles_384 \\
      --tile-size 384 \\
      --output-dir inputs/tiles_384 \\
      --dry-run
        """,
    )

    parser.add_argument(
        "--reference-bounds",
        type=Path,
        required=True,
        help="Path to reference bounds GeoJSON (e.g., validation_bounds.geojson)",
    )
    parser.add_argument(
        "--new-tiles-dir",
        type=Path,
        required=True,
        help="Directory containing new-grid tiles with per-map metadata.json",
    )
    parser.add_argument(
        "--tile-size",
        type=int,
        required=True,
        help="Tile dimension in pixels for the new grid (e.g., 384)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write validation_manifest.json and selection metadata",
    )
    parser.add_argument(
        "--min-overlap",
        type=float,
        default=0.0,
        help="Minimum fraction of tile area overlapping the reference area "
        "(0.0–1.0). Tiles below this threshold are excluded. Default: 0.0 "
        "(any overlap). Use 0.10 to trim peripheral tiles.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview selection without writing output files",
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.reference_bounds.exists():
        print(f"Error: Reference bounds not found: {args.reference_bounds}")
        sys.exit(1)

    if not args.new_tiles_dir.exists():
        print(f"Error: New tiles directory not found: {args.new_tiles_dir}")
        sys.exit(1)

    # Load reference bounds
    print(f"Loading reference bounds: {args.reference_bounds}")
    reference_geometries = load_reference_bounds(args.reference_bounds)
    print(f"  Reference tiles: {len(reference_geometries)}")

    if not reference_geometries:
        print("Error: No features in reference bounds GeoJSON")
        sys.exit(1)

    # Load new tile metadata
    print(f"\nLoading new tile metadata: {args.new_tiles_dir}")
    new_metadata = load_tile_metadata(args.new_tiles_dir)
    print(f"  Total tiles in new grid: {len(new_metadata)}")

    if not new_metadata:
        print("Error: No tile metadata found in new tiles directory")
        sys.exit(1)

    # Select overlapping tiles
    print(f"\nSelecting tiles at {args.tile_size}×{args.tile_size} "
          f"that overlap the reference area...")
    selected_tiles = select_overlapping_tiles(
        reference_geometries, new_metadata, args.tile_size,
        min_overlap=args.min_overlap,
    )

    # Count tiles per map
    map_counts: dict[str, int] = {}
    for tile in selected_tiles:
        map_name = tile.rsplit("_x", 1)[0]
        map_counts[map_name] = map_counts.get(map_name, 0) + 1

    # Summary
    print("\nSelection results:")
    print(f"  Selected tiles: {len(selected_tiles)}")
    print("  By map:")
    for map_name, count in sorted(map_counts.items()):
        print(f"    {map_name}: {count}")

    if args.dry_run:
        print("\n[DRY RUN] No files written.")
        return

    # Write outputs
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Write validation manifest (same format as existing 512 manifest)
    manifest_path = args.output_dir / "validation_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(selected_tiles, f, indent=2)
    print(f"\nValidation manifest written: {manifest_path}")

    # Write selection metadata
    selection_metadata = {
        "created": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "reference_bounds": str(args.reference_bounds),
            "new_tiles_dir": str(args.new_tiles_dir),
            "tile_size": args.tile_size,
            "selection_method": "geographic_overlap",
            "min_overlap": args.min_overlap,
        },
        "reference_tiles": len(reference_geometries),
        "total_new_tiles": len(new_metadata),
        "selected_tiles": len(selected_tiles),
        "by_map": map_counts,
        "validation": {
            "tiles": [
                {"filename": t, "mound_count": 0, "density": "unknown"}
                for t in selected_tiles
            ],
        },
    }

    metadata_path = args.output_dir / "tile_selection_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(selection_metadata, f, indent=2)
    print(f"Selection metadata written: {metadata_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
