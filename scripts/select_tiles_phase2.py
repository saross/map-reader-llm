#!/usr/bin/env python3
"""
Tile Selection Script (Phase 2)

Selects training and holdout tile sets with documented provenance and
spatial separation. See docs/methodology/tile-selection-methodology.md
for full documentation.

Usage:
    python scripts/select_tiles_phase2.py [--seed SEED]

Output:
    inputs/training_manifest.json
    inputs/holdout_manifest.json
    inputs/tile_selection_metadata.json
"""

import argparse
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np
from PIL import Image

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    TILE_SIZE,
    OVERLAP,
    STRIDE,
    MAX_BACKGROUND_PERCENT,
    ADJACENCY_DISTANCE,
)

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

INPUTS_DIR = Path("inputs")
TILES_DIR = INPUTS_DIR / "tiles"
GROUND_TRUTH_PATH = INPUTS_DIR / "vectors" / "mounds-reference.geojson"
OUTPUT_DIR = INPUTS_DIR

# Maps to process (excluding legend)
MAPS = [
    "K-35-052-4_32635",
    "K-35-053-3_Elenovo",
    "K-35-062-2_Rakovski",
    "K-35-078-1_Lesovo",
]

# Selection parameters
TRAINING_SAMPLES_PER_MAP = 5
HOLDOUT_SAMPLES_PER_MAP = 15  # Expanded from 5 to 15 for improved statistical power
# TILE_SIZE, OVERLAP, STRIDE, MAX_BACKGROUND_PERCENT, ADJACENCY_DISTANCE imported from config.py

# Density strata thresholds
DENSITY_EMPTY = 0
DENSITY_SPARSE = (1, 2)
DENSITY_DENSE = 3  # 3 or more


# -----------------------------------------------------------------------------
# Tile Utilities
# -----------------------------------------------------------------------------

def parse_tile_coords(tile_name: str) -> Tuple[int, int]:
    """
    Extract pixel coordinates from tile filename.

    Example: "K-35-062-2_Rakovski_x1792_y3136.png" -> (1792, 3136)
    """
    match = re.search(r"_x(\d+)_y(\d+)\.png$", tile_name)
    if match:
        return int(match.group(1)), int(match.group(2))
    raise ValueError(f"Could not parse coordinates from: {tile_name}")


def get_tile_grid_position(tile_name: str) -> Tuple[int, int]:
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
    Check if two tiles are within Manhattan distance of each other.
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

def load_ground_truth() -> Dict[str, List[Tuple[float, float]]]:
    """
    Load ground truth mounds and group by map.

    Returns dict: map_id -> list of (x, y) coordinates (EPSG:32635)
    """
    with open(GROUND_TRUTH_PATH) as f:
        data = json.load(f)

    mounds_by_map: Dict[str, List[Tuple[float, float]]] = {}

    for feature in data["features"]:
        map_id = feature["properties"]["Map"]
        coords = feature["geometry"]["coordinates"]

        # Handle MultiPoint geometry
        if feature["geometry"]["type"] == "MultiPoint":
            for coord in coords:
                if map_id not in mounds_by_map:
                    mounds_by_map[map_id] = []
                mounds_by_map[map_id].append((coord[0], coord[1]))
        else:
            if map_id not in mounds_by_map:
                mounds_by_map[map_id] = []
            mounds_by_map[map_id].append((coords[0], coords[1]))

    return mounds_by_map


def load_map_georef(map_id: str) -> Dict:
    """
    Load georeferencing info for a map to convert pixel coords to geographic.

    We'll compute this from the reference geojson bounding box.
    """
    ref_path = INPUTS_DIR / "vectors" / f"reference_{map_id}.geojson"
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
    map_id: str,
    mounds: List[Tuple[float, float]],
    georef: Dict,
    map_pixel_width: int,
    map_pixel_height: int,
) -> int:
    """
    Count how many mounds fall within a tile's bounding box.

    This is approximate — we estimate tile bounds from pixel coordinates
    and the map's geographic extent.
    """
    if georef is None or not mounds:
        return 0

    # Get tile pixel coordinates
    px, py = parse_tile_coords(tile_name)

    # Calculate geographic extent of tile
    # Assuming map origin is top-left, y increases downward in pixels but
    # upward in geographic coordinates
    geo_width = georef["max_x"] - georef["min_x"]
    geo_height = georef["max_y"] - georef["min_y"]

    # Scale factors
    scale_x = geo_width / map_pixel_width
    scale_y = geo_height / map_pixel_height

    # Tile bounds in geographic coordinates
    # Note: pixel y=0 is at top, which corresponds to max_y geographically
    tile_min_x = georef["min_x"] + px * scale_x
    tile_max_x = georef["min_x"] + (px + TILE_SIZE) * scale_x
    tile_max_y = georef["max_y"] - py * scale_y
    tile_min_y = georef["max_y"] - (py + TILE_SIZE) * scale_y

    # Count mounds within tile bounds
    count = 0
    for mx, my in mounds:
        if tile_min_x <= mx <= tile_max_x and tile_min_y <= my <= tile_max_y:
            count += 1

    return count


def get_map_dimensions(map_id: str) -> Tuple[int, int]:
    """
    Estimate map dimensions by finding the maximum tile coordinates.
    """
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
    """Categorise tile by mound density."""
    if mound_count == 0:
        return "empty"
    elif mound_count <= 2:
        return "sparse"
    else:
        return "dense"


def select_training_tiles(
    candidates: Dict[str, List[dict]],
    samples_per_map: int,
) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Select training tiles with density stratification.

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
    candidates: Dict[str, List[dict]],
    training_tiles: List[str],
    samples_per_map: int,
    adjacency_distance: int,
) -> Tuple[List[str], Dict[str, List[str]], bool]:
    """
    Select holdout tiles with spatial separation from training tiles.

    Returns:
        - List of selected tile filenames
        - Dict of selections by map
        - Whether spatial separation was relaxed
    """
    training_set = set(training_tiles)
    selected = []
    by_map = {}
    relaxed = False

    for map_id, tiles in candidates.items():
        # Get training tiles for this map
        map_training = [t for t in training_tiles if map_id in t]

        # Filter out training tiles and adjacent tiles
        available = []
        for t in tiles:
            if t["filename"] in training_set:
                continue

            # Check adjacency to any training tile
            is_adjacent_to_training = any(
                is_adjacent(t["filename"], train_tile, adjacency_distance)
                for train_tile in map_training
            )

            if not is_adjacent_to_training:
                available.append(t)

        # If insufficient tiles with spatial separation, relax constraint
        if len(available) < samples_per_map:
            print(f"  Warning: Relaxing spatial separation for {map_id}")
            print(f"    Available with separation: {len(available)}, needed: {samples_per_map}")
            relaxed = True

            # Add back adjacent tiles (but not training tiles themselves)
            available = [t for t in tiles if t["filename"] not in training_set]

        # Try to match training density distribution
        training_densities = {}
        for t in tiles:
            if t["filename"] in map_training:
                training_densities[t["density"]] = training_densities.get(t["density"], 0) + 1

        # Select with similar density distribution
        map_selected = []
        remaining = samples_per_map

        for density in ["dense", "sparse", "empty"]:
            target = training_densities.get(density, 0)
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

def main():
    parser = argparse.ArgumentParser(description="Select training and holdout tiles")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (default: current timestamp)",
    )
    args = parser.parse_args()

    # Set random seed
    if args.seed is None:
        seed = int(datetime.now(timezone.utc).timestamp())
    else:
        seed = args.seed

    random.seed(seed)
    print(f"Random seed: {seed}")

    # Load ground truth
    print("\nLoading ground truth...")
    mounds_by_map = load_ground_truth()
    for map_id, mounds in mounds_by_map.items():
        print(f"  {map_id}: {len(mounds)} mounds")

    # Build candidate list with content filtering and mound counts
    print("\nBuilding candidate list...")
    candidates: Dict[str, List[dict]] = {}

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
                tile_path.name,
                map_id,
                mounds,
                georef,
                map_width,
                map_height,
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

    # Select training tiles
    print("\n" + "=" * 60)
    print("Selecting TRAINING tiles (density-stratified random)...")
    print("=" * 60)
    training_tiles, training_by_map = select_training_tiles(candidates, TRAINING_SAMPLES_PER_MAP)

    # Select holdout tiles
    print("\n" + "=" * 60)
    print("Selecting HOLDOUT tiles (spatially separated)...")
    print("=" * 60)
    holdout_tiles, holdout_by_map, spatial_relaxed = select_holdout_tiles(
        candidates,
        training_tiles,
        HOLDOUT_SAMPLES_PER_MAP,
        ADJACENCY_DISTANCE,
    )

    # Verify no overlap
    overlap = set(training_tiles) & set(holdout_tiles)
    if overlap:
        print(f"\nERROR: Overlap detected between training and holdout: {overlap}")
        return 1

    # Build metadata
    metadata = {
        "created": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "parameters": {
            "training_samples_per_map": TRAINING_SAMPLES_PER_MAP,
            "holdout_samples_per_map": HOLDOUT_SAMPLES_PER_MAP,
            "max_background_percent": MAX_BACKGROUND_PERCENT,
            "adjacency_distance": ADJACENCY_DISTANCE,
            "tile_size": TILE_SIZE,
            "tile_overlap": OVERLAP,
            "tile_stride": STRIDE,
        },
        "training": {
            "total_tiles": len(training_tiles),
            "by_map": training_by_map,
            "tiles": [],
        },
        "holdout": {
            "total_tiles": len(holdout_tiles),
            "by_map": holdout_by_map,
            "spatial_separation_relaxed": spatial_relaxed,
            "tiles": [],
        },
    }

    # Add tile details to metadata
    for map_id, map_cands in candidates.items():
        for c in map_cands:
            if c["filename"] in training_tiles:
                metadata["training"]["tiles"].append({
                    "filename": c["filename"],
                    "map": map_id,
                    "mound_count": c["mound_count"],
                    "density": c["density"],
                })
            elif c["filename"] in holdout_tiles:
                metadata["holdout"]["tiles"].append({
                    "filename": c["filename"],
                    "map": map_id,
                    "mound_count": c["mound_count"],
                    "density": c["density"],
                })

    # Save outputs
    print("\n" + "=" * 60)
    print("Saving outputs...")
    print("=" * 60)

    training_manifest_path = OUTPUT_DIR / "training_manifest.json"
    holdout_manifest_path = OUTPUT_DIR / "holdout_manifest.json"
    metadata_path = OUTPUT_DIR / "tile_selection_metadata.json"

    with open(training_manifest_path, "w") as f:
        json.dump(sorted(training_tiles), f, indent=2)
    print(f"  Saved: {training_manifest_path}")

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
    print(f"Training tiles: {len(training_tiles)}")
    print(f"Holdout tiles: {len(holdout_tiles)}")
    print(f"Spatial separation relaxed: {spatial_relaxed}")

    # Density summary
    train_densities = {"empty": 0, "sparse": 0, "dense": 0}
    holdout_densities = {"empty": 0, "sparse": 0, "dense": 0}

    for t in metadata["training"]["tiles"]:
        train_densities[t["density"]] += 1
    for t in metadata["holdout"]["tiles"]:
        holdout_densities[t["density"]] += 1

    print(f"\nTraining density: {train_densities}")
    print(f"Holdout density:  {holdout_densities}")

    train_mounds = sum(t["mound_count"] for t in metadata["training"]["tiles"])
    holdout_mounds = sum(t["mound_count"] for t in metadata["holdout"]["tiles"])
    print(f"\nTotal mounds in training tiles: {train_mounds}")
    print(f"Total mounds in holdout tiles:  {holdout_mounds}")

    return 0


if __name__ == "__main__":
    exit(main())
