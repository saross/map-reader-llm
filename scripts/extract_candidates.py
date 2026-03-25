#!/usr/bin/env python3
"""
Candidate Extraction Script for H2 Two-Stage Pipeline
======================================================

Description:
    Extracts image crops around proposer detections for input to the verifier
    stage. This enables batch preparation of candidate images, decoupling the
    proposer and verifier stages for analysis and ablation studies.

Usage:
    python scripts/extract_candidates.py \\
        --proposer outputs/phase2/proposer_detections.geojson \\
        --rasters-dir inputs/rasters \\
        --output-dir outputs/phase3d/candidates \\
        --padding 75

    python scripts/extract_candidates.py \\
        --proposer outputs/merged_detections.geojson \\
        --output-dir outputs/candidates \\
        --dry-run

Inputs:
    - Proposer GeoJSON (Geographic JavaScript Object Notation) with detection
      geometries and "source_tile" property
    - Source GeoTIFF rasters in rasters directory (preferred)
    - Tiles directory containing georeferenced PNG tiles (fallback)

Outputs:
    - Cropped candidate images in output directory (always padding*2 × padding*2)
    - candidate_manifest.json mapping crop files to detection metadata

Note:
    E33 fix: Crops are now extracted from source GeoTIFF rasters instead of
    tile PNGs. This prevents edge-truncated crops when detections fall near
    tile boundaries. Falls back to tile PNGs if a raster is not found.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import sys
from pathlib import Path

import geojson
import numpy as np
import rasterio
from PIL import Image
from rasterio.windows import Window
from shapely.geometry import shape

# Script version
__version__ = "2.0.0"  # E33: crop from source raster instead of tile

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Default configuration
DEFAULT_PADDING = 75  # pixels of context around centroid
DEFAULT_TILES_DIR = PROJECT_ROOT / "inputs" / "tiles"
DEFAULT_RASTERS_DIR = PROJECT_ROOT / "inputs" / "rasters"


def tile_id_to_map_name(tile_id: str) -> str:
    """
    Extract the parent map name from a tile filename.

    Tile filenames follow the pattern ``{map_name}_x{origin_x}_y{origin_y}.png``.
    The map name corresponds to the source GeoTIFF filename (without extension).

    Args:
        tile_id: Tile filename (e.g., "K-35-052-4_32635_x1344_y1344.png").

    Returns:
        Map name (e.g., "K-35-052-4_32635").
    """
    # Split on the first "_x" followed by digits to separate map name from coords
    parts = tile_id.rsplit("_x", 1)
    return parts[0]


def resolve_raster_path(tile_id: str, rasters_dir: Path) -> Path | None:
    """
    Resolve a tile ID to its parent source GeoTIFF raster.

    Args:
        tile_id: Tile filename (e.g., "K-35-052-4_32635_x1344_y1344.png").
        rasters_dir: Directory containing source GeoTIFF rasters.

    Returns:
        Path to the source .tif file, or None if not found.
    """
    map_name = tile_id_to_map_name(tile_id)
    raster_path = rasters_dir / f"{map_name}.tif"
    if raster_path.exists():
        return raster_path

    # Try case-insensitive glob as fallback
    found = list(rasters_dir.glob(f"{map_name}.*tif*"))
    if found:
        return found[0]

    return None


def get_tile_path(tile_id: str, tiles_dir: Path) -> Path | None:
    """
    Resolve tile ID to absolute path.

    Searches for the tile in the tiles directory, handling both direct
    matches and subdirectory structures. Used as fallback when source
    rasters are unavailable.

    Args:
        tile_id: Tile filename (e.g., "K-35-052-4_32635_x1344_y1344.png").
        tiles_dir: Base directory containing tile subdirectories.

    Returns:
        Path to tile file, or None if not found.
    """
    # Try direct match in tiles_dir
    direct_path = tiles_dir / tile_id
    if direct_path.exists():
        return direct_path

    # Try subdirectories (map sheet folders)
    found = list(tiles_dir.glob(f"**/{tile_id}"))
    if found:
        return found[0]

    # Try adding PNG extension if not present
    if not tile_id.endswith(".png"):
        found = list(tiles_dir.glob(f"**/{tile_id}.png"))
        if found:
            return found[0]

    return None


def crop_region(
    raster_path: Path,
    centroid: tuple[float, float],
    padding: int,
    output_path: Path,
) -> bool:
    """
    Crop region around centroid from a georeferenced source raster.

    Reads from the full-resolution source GeoTIFF with ``boundless=True``,
    so crops are always exactly ``padding*2 × padding*2`` pixels regardless
    of where the detection falls. Rasterio pads beyond raster edges with
    fill_value=0 (black), avoiding any truncation.

    This was fixed in E33 — the original implementation read from tile PNGs,
    which caused edge-truncated crops for mounds near tile boundaries.

    Args:
        raster_path: Path to source GeoTIFF raster (NOT a tile PNG).
        centroid: Detection centroid in projected coordinates (x, y).
        padding: Number of pixels of context around centroid.
            Crop dimensions will be ``padding*2 × padding*2``.
        output_path: Path to save cropped image.

    Returns:
        True if crop was successful, False otherwise.
    """
    try:
        with rasterio.open(raster_path) as src:
            # Convert projected coordinates to pixel coordinates
            cx, cy = centroid
            row, col = src.index(cx, cy)

            # Build a window centred on the detection — no clamping needed
            # because boundless=True pads beyond raster edges with fill_value
            crop_size = padding * 2
            window = Window(
                col - padding,
                row - padding,
                crop_size,
                crop_size,
            )

            # Read with boundless=True — rasterio fills beyond-edge pixels
            # with 0 (black), guaranteeing exact crop dimensions
            arr = src.read(window=window, boundless=True, fill_value=0)
            if arr.shape[0] == 0:
                return False

            # Handle RGB, RGBA, and single-band rasters
            if arr.shape[0] >= 3:
                img_data = arr[:3].transpose(1, 2, 0)
            elif arr.shape[0] == 1:
                # Single-band: replicate to 3-band RGB
                grey = arr[0]
                img_data = np.stack([grey, grey, grey], axis=-1)
            else:
                img_data = arr.transpose(1, 2, 0)

            img = Image.fromarray(img_data)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, "PNG")
            return True

    except Exception as e:
        print(f"Error cropping from {raster_path}: {e}")
        return False


def extract_candidates(
    proposer_geojson: Path,
    tiles_dir: Path,
    output_dir: Path,
    rasters_dir: Path = DEFAULT_RASTERS_DIR,
    padding: int = DEFAULT_PADDING,
    dry_run: bool = False,
) -> Path | None:
    """
    Extract candidate regions from proposer detections.

    Reads a GeoJSON file containing proposer detections, crops image regions
    around each detection centroid from the source GeoTIFF rasters, and
    generates a manifest for verifier input.

    Crops are extracted from source rasters (not tile PNGs) to avoid
    edge-truncation when detections fall near tile boundaries (see E33).
    Falls back to tile PNGs if a source raster is not found.

    Args:
        proposer_geojson: Path to proposer output GeoJSON.
        tiles_dir: Directory containing source tiles (fallback for cropping).
        output_dir: Directory for cropped candidate images.
        rasters_dir: Directory containing source GeoTIFF rasters.
        padding: Pixels of context around detection centroid.
            Crop dimensions will be ``padding*2 × padding*2``.
        dry_run: If True, only validate inputs without extracting.

    Returns:
        Path to generated candidate_manifest.json, or None on failure.
    """
    proposer_geojson = Path(proposer_geojson)
    tiles_dir = Path(tiles_dir)
    output_dir = Path(output_dir)
    rasters_dir = Path(rasters_dir)

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

    # Normalise source_tiles (list) → source_tile (string).
    # merge_passes.py outputs "source_tiles" (plural, list) but
    # downstream code expects "source_tile" (singular, string).
    # Same pattern as 6_accuracy_report.py:_normalise_source_tile().
    for feat in features:
        props = feat.get("properties", {})
        if "source_tile" not in props and "source_tiles" in props:
            tiles_list = props["source_tiles"]
            props["source_tile"] = (
                tiles_list[0]
                if isinstance(tiles_list, list) and len(tiles_list) > 0
                else str(tiles_list)
            )

    print(f"Found {len(features)} detections")

    # Validate rasters directory — warn but don't fail (tiles fallback exists)
    if not rasters_dir.exists():
        print(f"Warning: Rasters directory not found: {rasters_dir}")
        print("  Will attempt fallback to tile PNGs (may produce truncated crops)")

    # Validate tiles directory (fallback source)
    if not tiles_dir.exists():
        print(f"Error: Tiles directory not found: {tiles_dir}")
        return None

    # Prepare output directory
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        crops_dir = output_dir / "crops"
        crops_dir.mkdir(exist_ok=True)

    # Cache resolved raster paths to avoid repeated filesystem lookups
    raster_cache: dict[str, Path | None] = {}

    # Process each detection
    manifest_entries = []
    successful = 0
    failed = 0
    missing_sources = set()
    raster_crops = 0
    tile_fallback_crops = 0

    for idx, feature in enumerate(features):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})

        # Extract source tile
        source_tile = props.get("source_tile")
        if not source_tile:
            print(f"Warning: Detection {idx} missing source_tile property")
            failed += 1
            continue

        # Resolve source raster (preferred) or fall back to tile PNG
        map_name = tile_id_to_map_name(source_tile)
        if map_name not in raster_cache:
            raster_cache[map_name] = resolve_raster_path(source_tile, rasters_dir)

        raster_path = raster_cache[map_name]
        crop_source = raster_path  # Will be the raster or tile path
        used_raster = raster_path is not None

        if not raster_path:
            # Fall back to tile PNG (pre-E33 behaviour, may truncate)
            crop_source = get_tile_path(source_tile, tiles_dir)
            if not crop_source:
                if source_tile not in missing_sources:
                    missing_sources.add(source_tile)
                    print(f"Warning: No raster or tile found for: {source_tile}")
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
                "cropped_from": "raster" if used_raster else "tile",
                "properties": props,
            })
            successful += 1
        else:
            # Extract crop from source raster (or tile fallback)
            crop_path = crops_dir / crop_filename
            if crop_region(crop_source, centroid, padding, crop_path):
                manifest_entries.append({
                    "candidate_id": idx,
                    "crop_file": f"crops/{crop_filename}",
                    "source_tile": source_tile,
                    "centroid_x": centroid[0],
                    "centroid_y": centroid[1],
                    "cropped_from": "raster" if used_raster else "tile",
                    "properties": props,
                })
                successful += 1
                if used_raster:
                    raster_crops += 1
                else:
                    tile_fallback_crops += 1
            else:
                failed += 1

    # Generate manifest
    manifest = {
        "version": "2.0",
        "source_geojson": str(proposer_geojson),
        "rasters_dir": str(rasters_dir),
        "tiles_dir": str(tiles_dir),
        "padding": padding,
        "crop_dimensions": f"{padding * 2}x{padding * 2}",
        "total_detections": len(features),
        "successful_extractions": successful,
        "failed_extractions": failed,
        "raster_crops": raster_crops,
        "tile_fallback_crops": tile_fallback_crops,
        "missing_sources": list(missing_sources),
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
    if not dry_run:
        print(f"  From rasters:     {raster_crops}")
        print(f"  From tiles (fallback): {tile_fallback_crops}")
    if missing_sources:
        print(f"  Missing sources:  {len(missing_sources)}")
    if tile_fallback_crops > 0:
        print(
            "  WARNING: Some crops used tile fallback — these may be "
            "truncated near tile edges (see E33)"
        )

    return manifest_path if not dry_run else None


def _write_empty_manifest(
    output_dir: Path,
    source_geojson: Path,
    padding: int,
) -> Path:
    """Write an empty manifest when the proposer input contains no features."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "2.0",
        "source_geojson": str(source_geojson),
        "padding": padding,
        "total_detections": 0,
        "successful_extractions": 0,
        "failed_extractions": 0,
        "missing_sources": [],
        "candidates": [],
    }
    manifest_path = output_dir / "candidate_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest_path


def main() -> None:
    """Parse command-line arguments and run candidate extraction."""
    parser = argparse.ArgumentParser(
        description="Extract candidate crops from proposer detections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract candidates with default settings
  python scripts/extract_candidates.py \\
      --proposer outputs/proposer_detections.geojson \\
      --output-dir outputs/candidates

  # Custom padding and rasters directory
  python scripts/extract_candidates.py \\
      --proposer outputs/merged.geojson \\
      --rasters-dir inputs/rasters \\
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
        "--rasters-dir",
        type=Path,
        default=DEFAULT_RASTERS_DIR,
        help=f"Directory containing source GeoTIFF rasters (default: {DEFAULT_RASTERS_DIR})",
    )
    parser.add_argument(
        "--tiles-dir",
        type=Path,
        default=DEFAULT_TILES_DIR,
        help=f"Directory containing source tiles — fallback if raster not found (default: {DEFAULT_TILES_DIR})",
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
        rasters_dir=args.rasters_dir,
        padding=args.padding,
        dry_run=args.dry_run,
    )

    sys.exit(0 if result or args.dry_run else 1)


if __name__ == "__main__":
    main()
