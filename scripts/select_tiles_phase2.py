#!/usr/bin/env python3
"""
Tile Selection Script (Phase 2)

Selects calibration and holdout tile sets with documented provenance and
spatial separation. See docs/methodology/tile-selection-methodology.md
for full documentation.

Usage::

    python scripts/select_tiles_phase2.py [--seed SEED]

Output:
    inputs/tiles/calibration_manifest.json
        — JavaScript Object Notation (JSON) manifest of calibration tiles
    inputs/tiles/holdout_manifest.json
        — JSON manifest of holdout tiles
    inputs/tiles/tile_selection_metadata.json
        — JSON metadata recording selection parameters and provenance

Author: Shawn Ross, Claude Code
Version: 1.0.0
Licence: Apache 2.0
"""

import argparse
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    ADJACENCY_DISTANCE,
    MAX_BACKGROUND_PERCENT,
    OVERLAP,
    STRIDE,
    TILE_SIZE,
)

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

INPUTS_DIR = Path("inputs")
TILES_DIR = INPUTS_DIR / "tiles"
GROUND_TRUTH_PATH = INPUTS_DIR / "vectors" / "references" / "mounds-reference.geojson"

# Maps to process (excluding legend)
MAPS = [
    "K-35-052-4_32635",
    "K-35-053-3_Elenovo",
    "K-35-062-2_Rakovski",
    "K-35-078-1_Lesovo",
]

# Selection parameters
CALIBRATION_SAMPLES_PER_MAP = 5
HOLDOUT_SAMPLES_PER_MAP = 15  # Expanded from 5 to 15 for improved statistical power


# -----------------------------------------------------------------------------
# Tile Utilities
# -----------------------------------------------------------------------------

def parse_tile_coords(tile_name: str) -> tuple[int, int]:
    """
    Extract pixel coordinates from tile filename.

    Example: "K-35-062-2_Rakovski_x1792_y3136.png" -> (1792, 3136)
    """
    match = re.search(r"_x(\d+)_y(\d+)\.png$", tile_name)
    if match:
        return int(match.group(1)), int(match.group(2))
    raise ValueError(f"Could not parse coordinates from: {tile_name}")


def get_tile_grid_position(tile_name: str) -> tuple[int, int]:
    """
    Convert tile coordinates to grid position (tile indices).

    Note: Tile origins are spaced by STRIDE (448px), not TILE_SIZE (512px),
    due to overlap. So grid position = coords // STRIDE.

    Example: x=1792, y=3136 with STRIDE=448 -> (4, 7)
    """
    x, y = parse_tile_coords(tile_name)
    return x // STRIDE, y // STRIDE


def is_adjacent(tile1: str, tile2: str, distance: int = 1) -> bool:
    """
    Check if two tiles are within Manhattan distance (taxicab geometry) of each other.
    """
    gx1, gy1 = get_tile_grid_position(tile1)
    gx2, gy2 = get_tile_grid_position(tile2)
    return abs(gx1 - gx2) <= distance and abs(gy1 - gy2) <= distance


def check_tile_content(tile_path: Path, max_background: float) -> bool:
    """
    Check if tile has sufficiently low background content.

    Returns True if tile has ≤max_background proportion of black pixels.
    """
    try:
        img = Image.open(tile_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        data = np.array(img)

        # Count black pixels [0, 0, 0]
        black_mask = np.all(data == [0, 0, 0], axis=-1)
        black_ratio = np.sum(black_mask) / (data.shape[0] * data.shape[1])

        return black_ratio <= max_background
    except Exception as e:
        print(f"  Warning: Could not read {tile_path.name}: {e}")
        return False


# -----------------------------------------------------------------------------
# Ground Truth Loading
# -----------------------------------------------------------------------------

def load_ground_truth() -> dict[str, list[tuple[float, float]]]:
    """
    Load ground truth mounds and group by map.

    Returns:
        Dict mapping map_id to list of (x, y) coordinates
        (EPSG:32635 — European Petroleum Survey Group).
    """
    with open(GROUND_TRUTH_PATH) as f:
        data = json.load(f)

    mounds_by_map: dict[str, list[tuple[float, float]]] = {}

    for feature in data["features"]:
        map_id = feature["properties"]["Map"]
        geometry = feature["geometry"]
        map_list = mounds_by_map.setdefault(map_id, [])

        # Handle both Point and MultiPoint geometries
        if geometry["type"] == "MultiPoint":
            for coord in geometry["coordinates"]:
                map_list.append((coord[0], coord[1]))
        else:
            coords = geometry["coordinates"]
            map_list.append((coords[0], coords[1]))

    return mounds_by_map


def load_map_georef(map_id: str) -> dict | None:
    """
    Load georeferencing info for a map from its reference GeoJSON bounding box.

    Returns a dict with min_x, max_x, min_y, max_y, or None if unavailable.
    """
    ref_path = INPUTS_DIR / "vectors" / "references" / f"reference_{map_id}.geojson"
    if not ref_path.exists():
        return None

    with open(ref_path) as f:
        data = json.load(f)

    # Get bounding box from features
    all_coords = []
    for feature in data["features"]:
        coords = feature["geometry"]["coordinates"]
        if feature["geometry"]["type"] == "MultiPoint":
            all_coords.extend(coords)
        else:
            all_coords.append(coords)

    if not all_coords:
        return None

    xs = [c[0] for c in all_coords]
    ys = [c[1] for c in all_coords]

    return {
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
    }


def count_mounds_in_tile(
    tile_name: str,
    mounds: list[tuple[float, float]],
    georef: dict | None,
    map_pixel_width: int,
    map_pixel_height: int,
) -> int:
    """
    Count how many mounds fall within a tile's bounding box.

    This is approximate -- tile bounds are estimated from pixel coordinates
    and the map's geographic extent. Map origin is top-left (pixel y=0
    corresponds to max_y geographically).
    """
    if georef is None or not mounds:
        return 0

    px, py = parse_tile_coords(tile_name)

    # Scale factors: pixels to geographic units
    scale_x = (georef["max_x"] - georef["min_x"]) / map_pixel_width
    scale_y = (georef["max_y"] - georef["min_y"]) / map_pixel_height

    # Tile bounds in geographic coordinates
    tile_min_x = georef["min_x"] + px * scale_x
    tile_max_x = georef["min_x"] + (px + TILE_SIZE) * scale_x
    tile_max_y = georef["max_y"] - py * scale_y
    tile_min_y = georef["max_y"] - (py + TILE_SIZE) * scale_y

    return sum(
        1 for mx, my in mounds
        if tile_min_x <= mx <= tile_max_x and tile_min_y <= my <= tile_max_y
    )


def get_map_dimensions(map_id: str) -> tuple[int, int]:
    """Estimate map pixel dimensions from the maximum tile coordinates."""
    map_dir = TILES_DIR / map_id
    max_x, max_y = 0, 0

    for tile in map_dir.glob("*.png"):
        try:
            x, y = parse_tile_coords(tile.name)
            max_x = max(max_x, x + TILE_SIZE)
            max_y = max(max_y, y + TILE_SIZE)
        except ValueError:
            continue

    return max_x, max_y


# -----------------------------------------------------------------------------
# Selection Logic
# -----------------------------------------------------------------------------

def categorise_density(mound_count: int) -> str:
    """Categorise tile by mound density (empty / sparse / dense)."""
    if mound_count == 0:
        return "empty"
    if mound_count <= 2:
        return "sparse"
    return "dense"


def select_calibration_tiles(
    candidates: dict[str, list[dict]],
    samples_per_map: int,
) -> tuple[list[str], dict[str, list[str]]]:
    """
    Select calibration tiles with density stratification.

    Returns:
        - List of selected tile filenames
        - Dict of selections by map for debugging
    """
    selected = []
    by_map = {}

    for map_id, tiles in candidates.items():
        # Group by density
        by_density = {"empty": [], "sparse": [], "dense": []}
        for t in tiles:
            by_density[t["density"]].append(t)

        # Calculate target distribution
        total = len(tiles)
        if total == 0:
            print(f"  Warning: No valid tiles for {map_id}")
            by_map[map_id] = []
            continue

        # Proportional sampling from each stratum
        map_selected = []
        remaining = samples_per_map

        for density in ["dense", "sparse", "empty"]:  # Prioritise mound-containing tiles
            stratum = by_density[density]
            if not stratum or remaining <= 0:
                continue

            # Calculate proportional count (at least 1 if stratum non-empty)
            proportion = len(stratum) / total
            target = max(1, round(proportion * samples_per_map))
            take = min(target, len(stratum), remaining)

            random.shuffle(stratum)
            map_selected.extend(stratum[:take])
            remaining -= take

        # If we still need more, take from any stratum
        if remaining > 0:
            remaining_tiles = [t for t in tiles if t not in map_selected]
            random.shuffle(remaining_tiles)
            map_selected.extend(remaining_tiles[:remaining])

        selected.extend([t["filename"] for t in map_selected[:samples_per_map]])
        by_map[map_id] = [t["filename"] for t in map_selected[:samples_per_map]]

        print(f"  {map_id}: selected {len(by_map[map_id])} tiles")
        for density in ["dense", "sparse", "empty"]:
            count = sum(1 for t in map_selected[:samples_per_map] if t["density"] == density)
            if count > 0:
                print(f"    - {density}: {count}")

    return selected, by_map


def select_holdout_tiles(
    candidates: dict[str, list[dict]],
    calibration_tiles: list[str],
    samples_per_map: int,
    adjacency_distance: int,
) -> tuple[list[str], dict[str, list[str]], bool]:
    """
    Select holdout tiles with spatial separation from calibration tiles.

    Returns:
        - List of selected tile filenames
        - Dict of selections by map
        - Whether spatial separation was relaxed
    """
    calibration_set = set(calibration_tiles)
    selected = []
    by_map = {}
    relaxed = False

    for map_id, tiles in candidates.items():
        # Get calibration tiles for this map
        map_calibration = [t for t in calibration_tiles if map_id in t]

        # Filter out calibration tiles and adjacent tiles
        available = []
        for t in tiles:
            if t["filename"] in calibration_set:
                continue

            # Check adjacency to any calibration tile
            is_adjacent_to_calibration = any(
                is_adjacent(t["filename"], calib_tile, adjacency_distance)
                for calib_tile in map_calibration
            )

            if not is_adjacent_to_calibration:
                available.append(t)

        # If insufficient tiles with spatial separation, relax constraint
        if len(available) < samples_per_map:
            print(f"  Warning: Relaxing spatial separation for {map_id}")
            print(f"    Available with separation: {len(available)}, needed: {samples_per_map}")
            relaxed = True

            # Add back adjacent tiles (but not calibration tiles themselves)
            available = [t for t in tiles if t["filename"] not in calibration_set]

        # Try to match calibration density distribution
        calibration_densities = {}
        for t in tiles:
            if t["filename"] in map_calibration:
                calibration_densities[t["density"]] = calibration_densities.get(t["density"], 0) + 1

        # Select with similar density distribution
        map_selected = []
        remaining = samples_per_map

        for density in ["dense", "sparse", "empty"]:
            target = calibration_densities.get(density, 0)
            stratum = [t for t in available if t["density"] == density and t not in map_selected]

            if not stratum or target == 0:
                continue

            take = min(target, len(stratum), remaining)
            random.shuffle(stratum)
            map_selected.extend(stratum[:take])
            remaining -= take

        # Fill remaining from any available
        if remaining > 0:
            remaining_tiles = [t for t in available if t not in map_selected]
            random.shuffle(remaining_tiles)
            map_selected.extend(remaining_tiles[:remaining])

        selected.extend([t["filename"] for t in map_selected[:samples_per_map]])
        by_map[map_id] = [t["filename"] for t in map_selected[:samples_per_map]]

        print(f"  {map_id}: selected {len(by_map[map_id])} tiles")
        for density in ["dense", "sparse", "empty"]:
            count = sum(1 for t in map_selected[:samples_per_map] if t["density"] == density)
            if count > 0:
                print(f"    - {density}: {count}")

    return selected, by_map, relaxed


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> int:
    """Main entry point for Phase 2 tile selection."""
    parser = argparse.ArgumentParser(description="Select calibration and holdout tiles")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (default: current Coordinated Universal Time (UTC) timestamp)",
    )
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else int(
        datetime.now(timezone.utc).timestamp()
    )

    random.seed(seed)
    print(f"Random seed: {seed}")

    # Load ground truth
    print("\nLoading ground truth...")
    mounds_by_map = load_ground_truth()
    for map_id, mounds in mounds_by_map.items():
        print(f"  {map_id}: {len(mounds)} mounds")

    # Build candidate list with content filtering and mound counts
    print("\nBuilding candidate list...")
    candidates: dict[str, list[dict]] = {}

    for map_id in MAPS:
        map_dir = TILES_DIR / map_id
        if not map_dir.exists():
            print(f"  Warning: Map directory not found: {map_dir}")
            continue

        # Get map dimensions and georef
        map_width, map_height = get_map_dimensions(map_id)
        georef = load_map_georef(map_id)
        mounds = mounds_by_map.get(map_id, [])

        print(f"\n  Processing {map_id}...")
        print(f"    Map dimensions: {map_width}x{map_height} pixels")
        print(f"    Mounds in ground truth: {len(mounds)}")

        map_candidates = []
        tiles = list(map_dir.glob("*.png"))

        for tile_path in tiles:
            # Check content threshold
            if not check_tile_content(tile_path, MAX_BACKGROUND_PERCENT):
                continue

            # Count mounds in tile
            mound_count = count_mounds_in_tile(
                tile_path.name, mounds, georef, map_width, map_height,
            )

            density = categorise_density(mound_count)

            map_candidates.append({
                "filename": tile_path.name,
                "path": str(tile_path),
                "mound_count": mound_count,
                "density": density,
            })

        candidates[map_id] = map_candidates
        print(f"    Valid candidates: {len(map_candidates)} / {len(tiles)} tiles")

        # Print density distribution
        densities = {"empty": 0, "sparse": 0, "dense": 0}
        for c in map_candidates:
            densities[c["density"]] += 1
        print(f"    Density distribution: {densities}")

    # Select calibration tiles
    print("\n" + "=" * 60)
    print("Selecting CALIBRATION tiles (density-stratified random)...")
    print("=" * 60)
    calibration_tiles, calibration_by_map = select_calibration_tiles(
        candidates, CALIBRATION_SAMPLES_PER_MAP,
    )

    # Select holdout tiles
    print("\n" + "=" * 60)
    print("Selecting HOLDOUT tiles (spatially separated)...")
    print("=" * 60)
    holdout_tiles, holdout_by_map, spatial_relaxed = select_holdout_tiles(
        candidates,
        calibration_tiles,
        HOLDOUT_SAMPLES_PER_MAP,
        ADJACENCY_DISTANCE,
    )

    # Convert to sets for O(1) membership tests throughout
    calibration_set = set(calibration_tiles)
    holdout_set = set(holdout_tiles)

    # Verify no overlap between calibration and holdout sets
    overlap = calibration_set & holdout_set
    if overlap:
        print(f"\nERROR: Overlap detected between calibration and holdout: {overlap}")
        return 1

    # Build metadata
    # Note: In actual usage, calibration and holdout may be selected on different
    # dates with different seeds (per preregistration). When re-running, update
    # the seed/date in each section accordingly.
    selection_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    metadata = {
        "created": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "calibration_samples_per_map": CALIBRATION_SAMPLES_PER_MAP,
            "holdout_samples_per_map": HOLDOUT_SAMPLES_PER_MAP,
            "max_background_percent": MAX_BACKGROUND_PERCENT,
            "adjacency_distance": ADJACENCY_DISTANCE,
            "tile_size": TILE_SIZE,
            "tile_overlap": OVERLAP,
            "tile_stride": STRIDE,
        },
        "calibration": {
            "random_seed": seed,
            "selection_date": selection_date,
            "total_tiles": len(calibration_tiles),
            "by_map": calibration_by_map,
            "tiles": [],
        },
        "holdout": {
            "random_seed": seed,
            "selection_date": selection_date,
            "total_tiles": len(holdout_tiles),
            "by_map": holdout_by_map,
            "spatial_separation_relaxed": spatial_relaxed,
            "tiles": [],
        },
    }

    # Add tile details to metadata
    for map_id, map_cands in candidates.items():
        for c in map_cands:
            tile_detail = {
                "filename": c["filename"],
                "map": map_id,
                "mound_count": c["mound_count"],
                "density": c["density"],
            }
            if c["filename"] in calibration_set:
                metadata["calibration"]["tiles"].append(tile_detail)
            elif c["filename"] in holdout_set:
                metadata["holdout"]["tiles"].append(tile_detail)

    # Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs...")
    print("=" * 60)

    calibration_manifest_path = TILES_DIR / "calibration_manifest.json"
    # E73 (2026-08-02): aligned with the live pipeline, which reads
    # validation_manifest.json (generate_tile_bounds.py, preflight_check.py);
    # this script previously wrote holdout_manifest.json, so the documented
    # regeneration command did not produce the file the pipeline consumes.
    holdout_manifest_path = TILES_DIR / "validation_manifest.json"
    metadata_path = TILES_DIR / "tile_selection_metadata.json"

    with open(calibration_manifest_path, "w") as f:
        json.dump(sorted(calibration_tiles), f, indent=2)
    print(f"  Saved: {calibration_manifest_path}")

    with open(holdout_manifest_path, "w") as f:
        json.dump(sorted(holdout_tiles), f, indent=2)
    print(f"  Saved: {holdout_manifest_path}")

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved: {metadata_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Random seed: {seed}")
    print(f"Calibration tiles: {len(calibration_tiles)}")
    print(f"Holdout tiles: {len(holdout_tiles)}")
    print(f"Spatial separation relaxed: {spatial_relaxed}")

    # Density summary
    calibration_densities = {"empty": 0, "sparse": 0, "dense": 0}
    holdout_densities = {"empty": 0, "sparse": 0, "dense": 0}

    for t in metadata["calibration"]["tiles"]:
        calibration_densities[t["density"]] += 1
    for t in metadata["holdout"]["tiles"]:
        holdout_densities[t["density"]] += 1

    print(f"\nCalibration density: {calibration_densities}")
    print(f"Holdout density:     {holdout_densities}")

    calibration_mounds = sum(t["mound_count"] for t in metadata["calibration"]["tiles"])
    holdout_mounds = sum(t["mound_count"] for t in metadata["holdout"]["tiles"])
    print(f"\nTotal mounds in calibration tiles: {calibration_mounds}")
    print(f"Total mounds in holdout tiles:     {holdout_mounds}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
