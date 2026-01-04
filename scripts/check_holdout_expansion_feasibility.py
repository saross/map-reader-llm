#!/usr/bin/env python3
"""
Holdout Expansion Feasibility Check

Determines whether expanding the holdout set from 20 to 60 tiles is feasible
given the constraints:
- Not adjacent to training tiles (Manhattan distance ≤ 1)
- Content threshold: ≤75% background
- Holdout-to-holdout adjacency is allowed

This script does NOT modify any data; it reports feasibility only.

Usage:
    python scripts/check_holdout_expansion_feasibility.py
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np
from PIL import Image

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

INPUTS_DIR = Path("inputs")
TILES_DIR = INPUTS_DIR / "tiles"
METADATA_PATH = INPUTS_DIR / "tile_selection_metadata.json"
GROUND_TRUTH_PATH = INPUTS_DIR / "vectors" / "mounds-reference.geojson"

# Maps to process
MAPS = [
    "K-35-052-4_32635",
    "K-35-053-3_Elenovo",
    "K-35-062-2_Rakovski",
    "K-35-078-1_Lesovo",
]

# Constraints
MAX_BACKGROUND_PERCENT = 0.75
TILE_SIZE = 448
ADJACENCY_DISTANCE = 1

# Target
TARGET_HOLDOUT_PER_MAP = 15


# -----------------------------------------------------------------------------
# Tile Utilities (from select_tiles_phase2.py)
# -----------------------------------------------------------------------------

def parse_tile_coords(tile_name: str) -> Tuple[int, int]:
    """Extract pixel coordinates from tile filename."""
    match = re.search(r"_x(\d+)_y(\d+)\.png$", tile_name)
    if match:
        return int(match.group(1)), int(match.group(2))
    raise ValueError(f"Could not parse coordinates from: {tile_name}")


def get_tile_grid_position(tile_name: str) -> Tuple[int, int]:
    """Convert tile coordinates to grid position (tile indices)."""
    x, y = parse_tile_coords(tile_name)
    return x // TILE_SIZE, y // TILE_SIZE


def is_adjacent(tile1: str, tile2: str, distance: int = 1) -> bool:
    """Check if two tiles are within Manhattan distance of each other."""
    gx1, gy1 = get_tile_grid_position(tile1)
    gx2, gy2 = get_tile_grid_position(tile2)
    return abs(gx1 - gx2) <= distance and abs(gy1 - gy2) <= distance


def check_tile_content(tile_path: Path, max_background: float) -> bool:
    """Check if tile has sufficiently low background content."""
    try:
        img = Image.open(tile_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        data = np.array(img)
        black_mask = np.all(data == [0, 0, 0], axis=-1)
        black_ratio = np.sum(black_mask) / (data.shape[0] * data.shape[1])
        return black_ratio <= max_background
    except Exception:
        return False


def categorise_density(mound_count: int) -> str:
    """Categorise tile by mound density."""
    if mound_count == 0:
        return "empty"
    elif mound_count <= 2:
        return "sparse"
    else:
        return "dense"


# -----------------------------------------------------------------------------
# Ground Truth Loading
# -----------------------------------------------------------------------------

def load_ground_truth() -> Dict[str, List[Tuple[float, float]]]:
    """Load ground truth mounds and group by map."""
    with open(GROUND_TRUTH_PATH) as f:
        data = json.load(f)

    mounds_by_map: Dict[str, List[Tuple[float, float]]] = {}

    for feature in data["features"]:
        map_id = feature["properties"]["Map"]
        coords = feature["geometry"]["coordinates"]

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
    """Load georeferencing info for a map."""
    ref_path = INPUTS_DIR / "vectors" / f"reference_{map_id}.geojson"
    if not ref_path.exists():
        return None

    with open(ref_path) as f:
        data = json.load(f)

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


def get_map_dimensions(map_id: str) -> Tuple[int, int]:
    """Estimate map dimensions by finding the maximum tile coordinates."""
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


def count_mounds_in_tile(
    tile_name: str,
    map_id: str,
    mounds: List[Tuple[float, float]],
    georef: Dict,
    map_pixel_width: int,
    map_pixel_height: int,
) -> int:
    """Count how many mounds fall within a tile's bounding box."""
    if georef is None or not mounds:
        return 0

    px, py = parse_tile_coords(tile_name)
    geo_width = georef["max_x"] - georef["min_x"]
    geo_height = georef["max_y"] - georef["min_y"]
    scale_x = geo_width / map_pixel_width
    scale_y = geo_height / map_pixel_height

    tile_min_x = georef["min_x"] + px * scale_x
    tile_max_x = georef["min_x"] + (px + TILE_SIZE) * scale_x
    tile_max_y = georef["max_y"] - py * scale_y
    tile_min_y = georef["max_y"] - (py + TILE_SIZE) * scale_y

    count = 0
    for mx, my in mounds:
        if tile_min_x <= mx <= tile_max_x and tile_min_y <= my <= tile_max_y:
            count += 1

    return count


# -----------------------------------------------------------------------------
# Feasibility Check
# -----------------------------------------------------------------------------

def main():
    """Run feasibility check for holdout expansion."""
    print("=" * 70)
    print("HOLDOUT EXPANSION FEASIBILITY CHECK")
    print("Target: 60 holdout tiles (15 per map)")
    print("=" * 70)

    # Load existing metadata
    with open(METADATA_PATH) as f:
        metadata = json.load(f)

    training_tiles = set()
    for map_id, tiles in metadata["training"]["by_map"].items():
        training_tiles.update(tiles)

    existing_holdout = set()
    for map_id, tiles in metadata["holdout"]["by_map"].items():
        existing_holdout.update(tiles)

    print(f"\nExisting training tiles: {len(training_tiles)}")
    print(f"Existing holdout tiles: {len(existing_holdout)}")

    # Load ground truth for mound counting
    print("\nLoading ground truth...")
    mounds_by_map = load_ground_truth()

    # Analyse each map
    results = {}
    total_available = 0
    total_needed = TARGET_HOLDOUT_PER_MAP * len(MAPS)

    for map_id in MAPS:
        print(f"\n{'=' * 50}")
        print(f"Map: {map_id}")
        print("=" * 50)

        map_dir = TILES_DIR / map_id
        if not map_dir.exists():
            print(f"  ERROR: Directory not found")
            continue

        # Get training tiles for this map
        map_training = [t for t in training_tiles if map_id in t]
        map_existing_holdout = [t for t in existing_holdout if map_id in t]

        # Get georef and dimensions
        georef = load_map_georef(map_id)
        map_width, map_height = get_map_dimensions(map_id)
        mounds = mounds_by_map.get(map_id, [])

        # Analyse all tiles
        all_tiles = list(map_dir.glob("*.png"))
        passed_content = []
        passed_content_and_separation = []
        tile_details = []

        for tile_path in all_tiles:
            tile_name = tile_path.name

            # Skip training tiles
            if tile_name in training_tiles:
                continue

            # Content check
            if not check_tile_content(tile_path, MAX_BACKGROUND_PERCENT):
                continue

            passed_content.append(tile_name)

            # Mound count
            mound_count = count_mounds_in_tile(
                tile_name, map_id, mounds, georef, map_width, map_height
            )
            density = categorise_density(mound_count)

            # Adjacency check (not adjacent to training tiles)
            is_adjacent_to_training = any(
                is_adjacent(tile_name, train_tile, ADJACENCY_DISTANCE)
                for train_tile in map_training
            )

            if not is_adjacent_to_training:
                passed_content_and_separation.append(tile_name)
                tile_details.append({
                    "filename": tile_name,
                    "mound_count": mound_count,
                    "density": density,
                    "is_existing_holdout": tile_name in map_existing_holdout,
                })

        # Report
        print(f"\n  Total tiles: {len(all_tiles)}")
        print(f"  Training tiles (excluded): {len(map_training)}")
        print(f"  Pass content filter (≤75% background): {len(passed_content)}")
        print(f"  Pass content + not adjacent to training: {len(passed_content_and_separation)}")
        print(f"  Existing holdout tiles: {len(map_existing_holdout)}")
        print(f"\n  TARGET: {TARGET_HOLDOUT_PER_MAP} holdout tiles")
        print(f"  AVAILABLE: {len(passed_content_and_separation)} tiles")

        feasible = len(passed_content_and_separation) >= TARGET_HOLDOUT_PER_MAP
        print(f"  FEASIBLE: {'YES ✓' if feasible else 'NO ✗'}")

        # Density breakdown
        densities = {"empty": 0, "sparse": 0, "dense": 0}
        total_mounds = 0
        for t in tile_details:
            densities[t["density"]] += 1
            total_mounds += t["mound_count"]

        print(f"\n  Available tiles by density:")
        print(f"    Empty (0 mounds):   {densities['empty']}")
        print(f"    Sparse (1-2 mounds): {densities['sparse']}")
        print(f"    Dense (3+ mounds):  {densities['dense']}")
        print(f"    Total mounds in available tiles: {total_mounds}")

        results[map_id] = {
            "total_tiles": len(all_tiles),
            "passed_content": len(passed_content),
            "passed_content_and_separation": len(passed_content_and_separation),
            "target": TARGET_HOLDOUT_PER_MAP,
            "feasible": feasible,
            "densities": densities,
            "total_mounds": total_mounds,
            "tile_details": tile_details,
        }

        total_available += len(passed_content_and_separation)

    # Overall summary
    print("\n" + "=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)

    all_feasible = all(r["feasible"] for r in results.values())

    print(f"\nTotal available tiles (all maps): {total_available}")
    print(f"Total needed: {total_needed}")
    print(f"\nFEASIBLE: {'YES ✓' if all_feasible else 'NO ✗'}")

    if all_feasible:
        # Calculate projected density distribution
        total_densities = {"empty": 0, "sparse": 0, "dense": 0}
        total_mounds = 0

        for map_id, r in results.items():
            # Estimate: select 15 from each map proportionally
            available = r["passed_content_and_separation"]
            if available >= TARGET_HOLDOUT_PER_MAP:
                # Proportional density (simplified)
                for density, count in r["densities"].items():
                    proportion = count / available if available > 0 else 0
                    estimated = round(proportion * TARGET_HOLDOUT_PER_MAP)
                    total_densities[density] += estimated

        print(f"\nProjected density distribution (approximate):")
        print(f"  Empty:  ~{total_densities['empty']}")
        print(f"  Sparse: ~{total_densities['sparse']}")
        print(f"  Dense:  ~{total_densities['dense']}")

        # Estimate mound count
        all_details = []
        for r in results.values():
            all_details.extend(r["tile_details"])

        # Sort by mound count descending to estimate max mounds achievable
        by_density = sorted(all_details, key=lambda x: -x["mound_count"])

        # If we take best 60 tiles across all maps
        top_60 = by_density[:60]
        max_mounds = sum(t["mound_count"] for t in top_60)
        print(f"\nMaximum possible mounds (if selecting densest tiles): {max_mounds}")

        # Estimate with proportional selection
        est_mounds_per_map = []
        for map_id, r in results.items():
            if r["total_mounds"] > 0 and r["passed_content_and_separation"] > 0:
                avg_mounds = r["total_mounds"] / r["passed_content_and_separation"]
                est = avg_mounds * TARGET_HOLDOUT_PER_MAP
                est_mounds_per_map.append(est)

        if est_mounds_per_map:
            est_total = sum(est_mounds_per_map)
            print(f"Estimated mounds with proportional selection: ~{int(est_total)}")
    else:
        # Report which maps fail
        print("\nMaps failing feasibility:")
        for map_id, r in results.items():
            if not r["feasible"]:
                shortfall = TARGET_HOLDOUT_PER_MAP - r["passed_content_and_separation"]
                print(f"  {map_id}: need {shortfall} more tiles")

    print("\n" + "=" * 70)

    return 0 if all_feasible else 1


if __name__ == "__main__":
    exit(main())
