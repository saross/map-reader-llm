#!/usr/bin/env python3
"""
Candidate Extraction Script for H2 Two-Stage Pipeline
======================================================

Description:
    Extracts image crops around proposer detections for input to the verifier
    stage. This enables batch preparation of candidate images, decoupling the
    proposer and verifier stages for analysis and ablation studies.

Usage:
    python scripts/extract_candidates.py \
        --proposer outputs/phase2/proposer_detections.geojson \
        --tiles-dir inputs/tiles \
        --output-dir outputs/phase3d/candidates \
        --padding 75

    python scripts/extract_candidates.py \
        --proposer outputs/merged_detections.geojson \
        --output-dir outputs/candidates \
        --dry-run

Inputs:
    - Proposer GeoJSON with detection geometries and 'source_tile' property
    - Tiles directory containing georeferenced PNG tiles

Outputs:
    - Cropped candidate images in output directory
    - candidate_manifest.json mapping crop files to detection metadata

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import sys
from pathlib import Path

import geojson
import rasterio
from PIL import Image
from rasterio.windows import Window
from shapely.geometry import shape

# Script version
__version__ = "1.0.0"

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Default configuration
DEFAULT_PADDING = 75  # pixels of context around centroid
DEFAULT_TILES_DIR = PROJECT_ROOT / "inputs" / "tiles"


def get_tile_path(tile_id: str, tiles_dir: Path) -> Path | None:
    """
    Resolve tile ID to absolute path.

    Searches for the tile in the tiles directory, handling both direct
    matches and subdirectory structures.

    Args:
        tile_id: Tile filename (e.g., 'K-35-052-4_32635_x1344_y1344.png')
        tiles_dir: Base directory containing tile subdirectories

    Returns:
        Path to tile file, or None if not found
    """
    # Try direct match in tiles_dir
    direct_path = tiles_dir / tile_id
    if direct_path.exists():
        return direct_path

    # Try subdirectories (map sheet folders)
    found = list(tiles_dir.glob(f"**/{tile_id}"))
    if found:
        return found[0]

    # Try adding .png extension if not present
    if not tile_id.endswith(".png"):
        found = list(tiles_dir.glob(f"**/{tile_id}.png"))
        if found:
            return found[0]

    return None


def crop_region(
    tile_path: Path,
    centroid: tuple[float, float],
    padding: int,
    output_path: Path,
) -> bool:
    """
    Crop region around centroid from georeferenced tile.

    Uses rasterio to handle coordinate transformation from projected
    coordinates (in the GeoJSON) to pixel coordinates in the tile.

    Args:
        tile_path: Path to georeferenced PNG tile
        centroid: Detection centroid in projected coordinates (x, y)
        padding: Number of pixels of context around centroid
        output_path: Path to save cropped image

    Returns:
        True if crop was successful, False otherwise
    """
    try:
        with rasterio.open(tile_path) as src:
            # Convert projected coordinates to pixel coordinates
            cx, cy = centroid
            row, col = src.index(cx, cy)

            # Calculate window bounds
            half_size = padding
            col_start = max(0, col - half_size)
            row_start = max(0, row - half_size)

            # Ensure window doesn't exceed tile bounds
            col_end = min(src.width, col + half_size)
            row_end = min(src.height, row + half_size)

            window_width = col_end - col_start
            window_height = row_end - row_start

            if window_width <= 0 or window_height <= 0:
                return False

            window = Window(col_start, row_start, window_width, window_height)

            # Read and transpose to RGB
            arr = src.read(window=window)
            if arr.shape[0] == 0:
                return False

            # Handle both RGB and RGBA
            if arr.shape[0] >= 3:
                img_data = arr[:3].transpose(1, 2, 0)
            else:
                img_data = arr.transpose(1, 2, 0)

            # Save as PNG
            img = Image.fromarray(img_data)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, "PNG")
            return True

    except Exception as e:
        print(f"Error cropping from {tile_path}: {e}")
        return False


def extract_candidates(
    proposer_geojson: Path,
    tiles_dir: Path,
    output_dir: Path,
    padding: int = DEFAULT_PADDING,
    dry_run: bool = False,
) -> Path | None:
    """
    Extract candidate regions from proposer detections.

    Reads a GeoJSON file containing proposer detections, crops image regions
    around each detection centroid, and generates a manifest for verifier input.

    Args:
        proposer_geojson: Path to proposer output GeoJSON
        tiles_dir: Directory containing source tiles
        output_dir: Directory for cropped candidate images
        padding: Pixels of context around detection centroid
        dry_run: If True, only validate inputs without extracting

    Returns:
        Path to generated candidate_manifest.json, or None on failure
    """
    proposer_geojson = Path(proposer_geojson)
    tiles_dir = Path(tiles_dir)
    output_dir = Path(output_dir)

    # Load proposer detections
    print(f"Loading proposer detections: {proposer_geojson}")
    try:
        with open(proposer_geojson) as f:
            data = geojson.load(f)
    except Exception as e:
        print(f"Error loading proposer GeoJSON: {e}")
        return None

    features = data.get("features", [])
    if not features:
        print("Warning: No features in proposer GeoJSON")
        return _write_empty_manifest(output_dir, proposer_geojson, padding)

    print(f"Found {len(features)} detections")

    # Validate tiles directory
    if not tiles_dir.exists():
        print(f"Error: Tiles directory not found: {tiles_dir}")
        return None

    # Prepare output directory
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        crops_dir = output_dir / "crops"
        crops_dir.mkdir(exist_ok=True)

    # Process each detection
    manifest_entries = []
    successful = 0
    failed = 0
    missing_tiles = set()

    for idx, feature in enumerate(features):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})

        # Extract source tile
        source_tile = props.get("source_tile")
        if not source_tile:
            print(f"Warning: Detection {idx} missing source_tile property")
            failed += 1
            continue

        # Find tile path
        tile_path = get_tile_path(source_tile, tiles_dir)
        if not tile_path:
            if source_tile not in missing_tiles:
                missing_tiles.add(source_tile)
                print(f"Warning: Tile not found: {source_tile}")
            failed += 1
            continue

        # Calculate centroid
        try:
            geom_shape = shape(geom)
            centroid = (geom_shape.centroid.x, geom_shape.centroid.y)
        except Exception as e:
            print(f"Warning: Cannot compute centroid for detection {idx}: {e}")
            failed += 1
            continue

        # Generate output filename
        crop_filename = f"candidate_{idx:05d}.png"

        if dry_run:
            # Validate but don't extract
            manifest_entries.append({
                "candidate_id": idx,
                "crop_file": crop_filename,
                "source_tile": source_tile,
                "centroid_x": centroid[0],
                "centroid_y": centroid[1],
                "properties": props,
            })
            successful += 1
        else:
            # Extract crop
            crop_path = crops_dir / crop_filename
            if crop_region(tile_path, centroid, padding, crop_path):
                manifest_entries.append({
                    "candidate_id": idx,
                    "crop_file": f"crops/{crop_filename}",
                    "source_tile": source_tile,
                    "centroid_x": centroid[0],
                    "centroid_y": centroid[1],
                    "properties": props,
                })
                successful += 1
            else:
                failed += 1

    # Generate manifest
    manifest = {
        "version": "1.0",
        "source_geojson": str(proposer_geojson),
        "tiles_dir": str(tiles_dir),
        "padding": padding,
        "total_detections": len(features),
        "successful_extractions": successful,
        "failed_extractions": failed,
        "missing_tiles": list(missing_tiles),
        "candidates": manifest_entries,
    }

    manifest_path = output_dir / "candidate_manifest.json"
    if not dry_run:
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"\nManifest written to: {manifest_path}")
    else:
        print(f"\n[DRY RUN] Would write manifest to: {manifest_path}")

    # Summary
    print("\nExtraction Summary:")
    print(f"  Total detections: {len(features)}")
    print(f"  Successful:       {successful}")
    print(f"  Failed:           {failed}")
    if missing_tiles:
        print(f"  Missing tiles:    {len(missing_tiles)}")

    return manifest_path if not dry_run else None


def _write_empty_manifest(
    output_dir: Path, source_geojson: Path, padding: int
) -> Path:
    """Write an empty manifest for empty proposer input."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "1.0",
        "source_geojson": str(source_geojson),
        "padding": padding,
        "total_detections": 0,
        "successful_extractions": 0,
        "failed_extractions": 0,
        "missing_tiles": [],
        "candidates": [],
    }
    manifest_path = output_dir / "candidate_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest_path


def main():
    """Main entry point for candidate extraction."""
    parser = argparse.ArgumentParser(
        description="Extract candidate crops from proposer detections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract candidates with default settings
  python scripts/extract_candidates.py \\
      --proposer outputs/proposer_detections.geojson \\
      --output-dir outputs/candidates

  # Custom padding and tiles directory
  python scripts/extract_candidates.py \\
      --proposer outputs/merged.geojson \\
      --tiles-dir inputs/tiles \\
      --output-dir outputs/candidates \\
      --padding 100

  # Validate inputs without extracting
  python scripts/extract_candidates.py \\
      --proposer outputs/detections.geojson \\
      --output-dir outputs/candidates \\
      --dry-run
        """,
    )
    parser.add_argument(
        "--proposer",
        type=Path,
        required=True,
        help="Path to proposer output GeoJSON",
    )
    parser.add_argument(
        "--tiles-dir",
        type=Path,
        default=DEFAULT_TILES_DIR,
        help=f"Directory containing source tiles (default: {DEFAULT_TILES_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for cropped candidate images and manifest",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=DEFAULT_PADDING,
        help=f"Pixels of context around centroid (default: {DEFAULT_PADDING})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without extracting crops",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    result = extract_candidates(
        proposer_geojson=args.proposer,
        tiles_dir=args.tiles_dir,
        output_dir=args.output_dir,
        padding=args.padding,
        dry_run=args.dry_run,
    )

    sys.exit(0 if result or args.dry_run else 1)


if __name__ == "__main__":
    main()
