#!/usr/bin/env python3
"""
Tile Selection Script (Phase 4)

Selects a 20-tile stratified subset from the 60 validation tiles for Phase 4
(H6: Flash→Pro Transfer Testing). Preserves the density distribution
(empty/sparse/dense ratio) from the full validation set.

Usage:
    python scripts/select_tiles_phase4.py [--seed SEED]
    python scripts/select_tiles_phase4.py --dry-run  # Show selection without saving

Output:
    inputs/tiles/phase4_validation_manifest.json
    inputs/vectors/bounds/phase4_validation_bounds.geojson
"""

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

INPUTS_DIR = Path("inputs")
TILES_DIR = INPUTS_DIR / "tiles"
VECTORS_DIR = INPUTS_DIR / "vectors"

VALIDATION_MANIFEST_PATH = TILES_DIR / "validation_manifest.json"
TILE_METADATA_PATH = TILES_DIR / "tile_selection_metadata.json"
VALIDATION_BOUNDS_PATH = VECTORS_DIR / "bounds" / "validation_bounds.geojson"

OUTPUT_MANIFEST_PATH = TILES_DIR / "phase4_validation_manifest.json"
OUTPUT_BOUNDS_PATH = VECTORS_DIR / "bounds" / "phase4_validation_bounds.geojson"

# Target subset size
PHASE4_SUBSET_SIZE = 20


# -----------------------------------------------------------------------------
# Selection Logic
# -----------------------------------------------------------------------------

def load_validation_with_metadata() -> list[dict]:
    """
    Load validation tiles with their density metadata.

    Returns list of dicts with keys: filename, map, mound_count, density
    """
    # Load manifest
    with open(VALIDATION_MANIFEST_PATH) as f:
        validation_tiles = set(json.load(f))

    # Load metadata
    with open(TILE_METADATA_PATH) as f:
        metadata = json.load(f)

    # Extract validation tile details
    tiles = []
    for tile_info in metadata.get("validation", {}).get("tiles", []):
        if tile_info["filename"] in validation_tiles:
            tiles.append(tile_info)

    return tiles


def select_stratified_subset(
    tiles: list[dict],
    target_size: int,
    seed: Optional[int] = None,
) -> list[dict]:
    """
    Select a stratified subset that preserves density distribution.

    Args:
        tiles: List of tile dicts with 'density' key
        target_size: Number of tiles to select
        seed: Random seed for reproducibility

    Returns:
        List of selected tile dicts
    """
    if seed is not None:
        random.seed(seed)

    # Group by density
    by_density = {"empty": [], "sparse": [], "dense": []}
    for tile in tiles:
        density = tile.get("density", "empty")
        by_density[density].append(tile)

    # Calculate proportional targets
    total = len(tiles)
    if total == 0:
        return []

    selected = []

    for density in ["dense", "sparse", "empty"]:
        stratum = by_density[density]
        if not stratum:
            continue

        # Calculate proportional count (at least 1 if stratum non-empty)
        proportion = len(stratum) / total
        target = max(1, round(proportion * target_size))

        # Don't exceed what's available
        take = min(target, len(stratum))

        # Random shuffle and select
        stratum_copy = stratum.copy()
        random.shuffle(stratum_copy)
        selected.extend(stratum_copy[:take])

    # If we have too many, trim from largest stratum
    while len(selected) > target_size:
        # Find which stratum has most selected
        selected_densities = {}
        for tile in selected:
            d = tile.get("density", "empty")
            selected_densities[d] = selected_densities.get(d, 0) + 1

        largest = max(selected_densities, key=selected_densities.get)

        # Remove one from largest stratum
        for i, tile in enumerate(selected):
            if tile.get("density") == largest:
                selected.pop(i)
                break

    # If we have too few, add more from any stratum
    if len(selected) < target_size:
        remaining_tiles = [t for t in tiles if t not in selected]
        random.shuffle(remaining_tiles)
        selected.extend(remaining_tiles[: target_size - len(selected)])

    return selected[:target_size]


def create_bounds_geojson(
    selected_tiles: list[dict],
    source_bounds_path: Path,
) -> dict:
    """
    Create a bounds GeoJSON containing only the selected tiles.

    Args:
        selected_tiles: List of selected tile dicts
        source_bounds_path: Path to full validation bounds GeoJSON

    Returns:
        GeoJSON dict for the subset bounds
    """
    # Load source bounds
    with open(source_bounds_path) as f:
        source = json.load(f)

    # Get selected filenames
    selected_names = {t["filename"] for t in selected_tiles}

    # Filter features
    filtered_features = []
    for feature in source.get("features", []):
        tile_name = feature.get("properties", {}).get("tile_name")
        if tile_name in selected_names:
            filtered_features.append(feature)

    # Build output GeoJSON
    output = {
        "type": "FeatureCollection",
        "name": "phase4_validation_bounds",
        "crs": source.get("crs"),
        "features": filtered_features,
    }

    return output


def get_density_distribution(tiles: list[dict]) -> dict[str, int]:
    """Get counts by density category."""
    distribution = {"empty": 0, "sparse": 0, "dense": 0}
    for tile in tiles:
        density = tile.get("density", "empty")
        # Only count known density categories
        if density in distribution:
            distribution[density] += 1
    return distribution


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Select 20-tile stratified subset for Phase 4"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (default: current timestamp)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show selection without saving files",
    )
    args = parser.parse_args()

    # Check input files exist
    if not VALIDATION_MANIFEST_PATH.exists():
        print(f"Error: Validation manifest not found: {VALIDATION_MANIFEST_PATH}")
        return 1

    if not TILE_METADATA_PATH.exists():
        print(f"Error: Tile metadata not found: {TILE_METADATA_PATH}")
        return 1

    # Set random seed
    if args.seed is None:
        seed = int(datetime.now(timezone.utc).timestamp())
    else:
        seed = args.seed

    print(f"Random seed: {seed}")

    # Load validation tiles with metadata
    print("\nLoading validation tiles...")
    tiles = load_validation_with_metadata()
    print(f"  Found {len(tiles)} validation tiles")

    original_distribution = get_density_distribution(tiles)
    print(f"  Original distribution: {original_distribution}")

    # Select stratified subset
    print(f"\nSelecting {PHASE4_SUBSET_SIZE}-tile stratified subset...")
    selected = select_stratified_subset(tiles, PHASE4_SUBSET_SIZE, seed)
    print(f"  Selected {len(selected)} tiles")

    selected_distribution = get_density_distribution(selected)
    print(f"  Subset distribution: {selected_distribution}")

    # Check proportions preserved
    print("\nDensity proportion check:")
    for density in ["dense", "sparse", "empty"]:
        orig_prop = original_distribution[density] / len(tiles) if tiles else 0
        sel_prop = selected_distribution[density] / len(selected) if selected else 0
        diff = abs(orig_prop - sel_prop)
        status = "✓" if diff <= 0.15 else "⚠"  # Allow 15% deviation
        print(f"  {density}: {orig_prop:.1%} → {sel_prop:.1%} ({status})")

    # Show selected tiles by map
    print("\nSelected tiles by map:")
    by_map: dict[str, list[str]] = {}
    for tile in selected:
        map_id = tile.get("map", "unknown")
        if map_id not in by_map:
            by_map[map_id] = []
        by_map[map_id].append(tile["filename"])

    for map_id, tile_names in sorted(by_map.items()):
        print(f"  {map_id}: {len(tile_names)} tiles")

    if args.dry_run:
        print("\n[Dry run - no files saved]")
        return 0

    # Save manifest
    print("\nSaving outputs...")
    manifest_data = sorted([t["filename"] for t in selected])

    OUTPUT_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MANIFEST_PATH, "w") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"  Saved: {OUTPUT_MANIFEST_PATH}")

    # Save bounds GeoJSON
    if VALIDATION_BOUNDS_PATH.exists():
        bounds_geojson = create_bounds_geojson(selected, VALIDATION_BOUNDS_PATH)
        OUTPUT_BOUNDS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_BOUNDS_PATH, "w") as f:
            json.dump(bounds_geojson, f, indent=2)
        print(f"  Saved: {OUTPUT_BOUNDS_PATH}")
    else:
        print(f"  Warning: Source bounds not found: {VALIDATION_BOUNDS_PATH}")
        print(f"  Skipped: {OUTPUT_BOUNDS_PATH}")

    # Save metadata for provenance
    metadata = {
        "created": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "source_manifest": str(VALIDATION_MANIFEST_PATH),
        "target_size": PHASE4_SUBSET_SIZE,
        "actual_size": len(selected),
        "original_distribution": original_distribution,
        "selected_distribution": selected_distribution,
        "tiles": selected,
    }

    metadata_path = TILES_DIR / "phase4_selection_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved: {metadata_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Random seed: {seed}")
    print(f"Selected tiles: {len(selected)} / {PHASE4_SUBSET_SIZE} target")
    total_mounds = sum(t.get("mound_count", 0) for t in selected)
    print(f"Total mounds in subset: {total_mounds}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
