#!/usr/bin/env python3
"""Calibration pipeline library — tile-size-agnostic utilities.

Provides shared functions for the generalised calibration pipeline:

- Tile enrichment: count ground-truth mounds per tile via spatial join
- Density stratification: classify tiles as empty / sparse / dense
- Stratified sampling: hierarchical three-level selection (geographic →
  density → random) with optional nested sub-pool generation
- Difficulty scoring: rank hard-positive and hard-negative candidates
  by run consistency and match distance

These functions underpin the automated calibration tile selector, hard-
case discovery, and example pool builder scripts.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import logging
import random
from pathlib import Path

import geopandas as gpd
import pandas as pd

from lib_advanced_metrics import get_map_name
from lib_consensus import ensure_utm_crs

logger = logging.getLogger(__name__)

# =========================================================================
# Constants
# =========================================================================

# Density strata threshold (from preregistration / select_tiles_phase2.py)
_SPARSE_MAX = 2  # 0 = empty, 1-2 = sparse, 3+ = dense

# =========================================================================
# Tile enrichment
# =========================================================================


def enrich_bounds_with_mound_counts(
    bounds_path: Path,
    reference_path: Path,
    target_crs: str = "EPSG:32635",
) -> gpd.GeoDataFrame:
    """Load bounds and count ground-truth mounds per tile.

    Performs a spatial join between tile boundary polygons and reference
    mound points to add ``mound_count``, ``density``, and ``map_name``
    columns. Works with any tile size because it operates on geographic
    polygons, not pixel coordinates.

    Args:
        bounds_path: Path to tile bounds GeoJSON (e.g.,
            ``full_evaluation_bounds.geojson``).
        reference_path: Path to ground-truth reference GeoJSON.
        target_crs: Target CRS for both datasets.

    Returns:
        GeoDataFrame with original columns plus ``mound_count``,
        ``density``, and ``map_name``.
    """
    gdf_bounds = gpd.read_file(bounds_path)
    gdf_bounds = ensure_utm_crs(
        gdf_bounds, target_crs=target_crs,
        source_label=str(bounds_path),
    )

    gdf_ref = gpd.read_file(reference_path)
    gdf_ref = ensure_utm_crs(
        gdf_ref, target_crs=target_crs,
        source_label=str(reference_path),
    )

    # Spatial join: each reference point matched to its containing tile
    joined = gpd.sjoin(
        gdf_ref, gdf_bounds, how="inner", predicate="intersects",
    )

    # Count mounds per tile (using the bounds index)
    counts = (
        joined.groupby("index_right")
        .size()
        .reindex(gdf_bounds.index, fill_value=0)
    )
    gdf_bounds["mound_count"] = counts.values
    gdf_bounds["density"] = gdf_bounds["mound_count"].apply(
        categorise_density
    )

    # Add map name from tile_name
    if "tile_name" in gdf_bounds.columns:
        gdf_bounds["map_name"] = gdf_bounds["tile_name"].apply(
            get_map_name
        )
    elif "tile_id" in gdf_bounds.columns:
        gdf_bounds["map_name"] = gdf_bounds["tile_id"].apply(
            get_map_name
        )
    else:
        logger.warning(
            "No tile_name or tile_id column found in bounds; "
            "map_name will be 'Unknown'"
        )
        gdf_bounds["map_name"] = "Unknown"

    # Report unique mound count (not per-tile sum, which inflates due
    # to tile overlap — 21% of mounds intersect 2-4 tiles at 384px)
    unique_mounds = len(joined.index.unique())

    logger.info(
        "Enriched %d tiles: %d unique mounds "
        "(per-tile sum=%d due to overlap), "
        "density: empty=%d, sparse=%d, dense=%d",
        len(gdf_bounds),
        unique_mounds,
        int(gdf_bounds["mound_count"].sum()),
        (gdf_bounds["density"] == "empty").sum(),
        (gdf_bounds["density"] == "sparse").sum(),
        (gdf_bounds["density"] == "dense").sum(),
    )

    return gdf_bounds


# =========================================================================
# Density stratification
# =========================================================================


def categorise_density(mound_count: int) -> str:
    """Categorise a tile by mound density.

    Thresholds match the preregistered design and
    ``select_tiles_phase2.py``:

    - **empty**: 0 mounds
    - **sparse**: 1–2 mounds
    - **dense**: 3+ mounds

    Args:
        mound_count: Number of ground-truth mounds in the tile.

    Returns:
        Density category string.
    """
    if mound_count == 0:
        return "empty"
    if mound_count <= _SPARSE_MAX:
        return "sparse"
    return "dense"


# =========================================================================
# Stratified sampling
# =========================================================================


def _redistribute_surplus(
    allocations: dict[str, int],
    tiles_df: pd.DataFrame,
) -> dict[str, int]:
    """Redistribute surplus when a map has fewer tiles than allocated.

    Iteratively moves surplus from over-allocated maps to under-
    allocated maps that still have capacity, preserving the total.

    Args:
        allocations: Map name → desired tile count.
        tiles_df: Full tile DataFrame with ``map_name`` column.

    Returns:
        Adjusted allocations where no map exceeds its tile count and
        the total is preserved (if enough tiles exist overall).
    """
    map_sizes = tiles_df.groupby("map_name").size().to_dict()
    adjusted = dict(allocations)

    # Iterative redistribution until stable
    for _ in range(len(adjusted)):
        surplus = 0
        for m in list(adjusted):
            available = map_sizes.get(m, 0)
            if adjusted[m] > available:
                surplus += adjusted[m] - available
                adjusted[m] = available

        if surplus == 0:
            break

        # Distribute surplus to maps with remaining capacity,
        # largest-first
        capacity = {
            m: map_sizes.get(m, 0) - adjusted[m]
            for m in adjusted if map_sizes.get(m, 0) - adjusted[m] > 0
        }
        if not capacity:
            break

        for m in sorted(capacity, key=capacity.get, reverse=True):
            give = min(surplus, capacity[m])
            adjusted[m] += give
            surplus -= give
            if surplus == 0:
                break

    return adjusted


def stratified_sample(
    tiles_df: pd.DataFrame,
    n: int,
    seed: int,
    per_map_equal: bool = True,
) -> pd.DataFrame:
    """Three-level hierarchical stratified sampling.

    Selects ``n`` tiles using the same strategy as the preregistered
    tile selection protocol:

    1. **Geographic** (Level 1): Equal allocation per map (or
       proportional if ``per_map_equal=False``).
    2. **Density** (Level 2): Proportional allocation within each map
       based on the density distribution of eligible tiles.
    3. **Random** (Level 3): Random selection within each density
       stratum.

    Args:
        tiles_df: DataFrame with at least ``tile_name``, ``map_name``,
            and ``density`` columns.
        n: Number of tiles to select.
        seed: Random seed for reproducibility.
        per_map_equal: If True, allocate equally across maps (rounding
            remainders to the largest maps). If False, allocate
            proportionally to each map's tile count.

    Returns:
        DataFrame subset of ``tiles_df`` containing the selected tiles.

    Raises:
        ValueError: If ``n`` exceeds the number of eligible tiles.
    """
    if n > len(tiles_df):
        raise ValueError(
            f"Requested {n} tiles but only {len(tiles_df)} available"
        )
    if n == 0:
        return tiles_df.iloc[0:0].copy()

    rng = random.Random(seed)
    maps = sorted(tiles_df["map_name"].unique())
    n_maps = len(maps)

    if n_maps == 0:
        raise ValueError("No maps found in tiles_df")

    # Level 1: Geographic allocation
    if per_map_equal:
        base_per_map = n // n_maps
        remainder = n % n_maps
        # Assign remainders to largest maps (most tiles)
        map_sizes = (
            tiles_df.groupby("map_name").size().sort_values(ascending=False)
        )
        allocations = {}
        for i, map_name in enumerate(map_sizes.index):
            allocations[map_name] = base_per_map + (
                1 if i < remainder else 0
            )
    else:
        # Proportional allocation
        total = len(tiles_df)
        allocations = {}
        assigned = 0
        for i, map_name in enumerate(maps):
            map_count = len(tiles_df[tiles_df["map_name"] == map_name])
            if i == n_maps - 1:
                allocations[map_name] = n - assigned
            else:
                alloc = round(n * map_count / total)
                allocations[map_name] = alloc
                assigned += alloc

    # Cap allocations at available tiles per map and redistribute
    # any surplus to maps that still have capacity.
    allocations = _redistribute_surplus(allocations, tiles_df)

    selected_indices: list[int] = []

    for map_name in maps:
        map_tiles = tiles_df[tiles_df["map_name"] == map_name]
        map_n = allocations.get(map_name, 0)

        if map_n == 0:
            continue

        # Level 2: Density-proportional allocation within map
        density_counts = map_tiles["density"].value_counts()
        density_allocs: dict[str, int] = {}
        assigned_in_map = 0

        densities = sorted(density_counts.index)
        for i, density in enumerate(densities):
            count = density_counts[density]
            if i == len(densities) - 1:
                # Last stratum gets the remainder
                density_allocs[density] = map_n - assigned_in_map
            else:
                alloc = round(map_n * count / len(map_tiles))
                # Ensure at least 1 if stratum is non-empty and we
                # still have budget
                if alloc == 0 and count > 0 and assigned_in_map < map_n:
                    alloc = 1
                density_allocs[density] = alloc
                assigned_in_map += alloc

        # Level 3: Random selection within each density stratum
        for density, d_n in density_allocs.items():
            stratum = map_tiles[map_tiles["density"] == density]
            d_n = min(d_n, len(stratum))
            if d_n > 0:
                chosen = rng.sample(list(stratum.index), d_n)
                selected_indices.extend(chosen)

    return tiles_df.loc[selected_indices].copy()


def nested_subsample(
    parent_df: pd.DataFrame,
    child_size: int,
    seed: int,
) -> pd.DataFrame:
    """Stratified subsample from a parent pool preserving density ratios.

    Used for H10 nesting: D(160) → C(80) → B(40) → A(20). The child
    is always a strict subset of the parent, and density proportions
    are maintained as closely as possible.

    Args:
        parent_df: Parent pool DataFrame (must have ``map_name`` and
            ``density`` columns).
        child_size: Number of tiles in the child pool.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame subset of ``parent_df`` containing the child pool.

    Raises:
        ValueError: If ``child_size`` exceeds parent size.
    """
    if child_size > len(parent_df):
        raise ValueError(
            f"Child size {child_size} exceeds parent size "
            f"{len(parent_df)}"
        )
    if child_size == len(parent_df):
        return parent_df.copy()

    return stratified_sample(parent_df, child_size, seed)


# =========================================================================
# Difficulty scoring
# =========================================================================


def score_difficulty_hp(
    vote_count: int,
    k_passes: int,
    match_distance: float | None = None,
    buffer_metres: float = 20.0,
) -> float:
    """Score difficulty for a hard positive candidate.

    Higher scores indicate harder cases (missed more often, matched
    at the boundary of the tolerance buffer).

    Components (weighted):
    - **Consistency** (70%): ``1 - vote_count / k_passes``. A mound
      detected 0/5 times scores 1.0; detected 4/5 scores 0.2.
    - **Distance penalty** (30%): ``match_distance / buffer_metres``,
      clamped to [0, 1]. Near-threshold matches are harder.

    Args:
        vote_count: Number of passes that detected this mound.
        k_passes: Total number of detection passes.
        match_distance: Distance to nearest detection in metres
            (None if unmatched / FN).
        buffer_metres: Matching tolerance in metres.

    Returns:
        Difficulty score in [0.0, 1.0].
    """
    if k_passes <= 0:
        return 0.0

    consistency = 1.0 - (vote_count / k_passes)

    if match_distance is not None and buffer_metres > 0:
        distance_penalty = min(match_distance / buffer_metres, 1.0)
    else:
        # Unmatched (FN) — maximum distance penalty
        distance_penalty = 1.0

    return 0.7 * consistency + 0.3 * distance_penalty


def score_difficulty_hn(
    vote_count: int,
    k_passes: int,
    nearest_ref_distance: float | None = None,
) -> float:
    """Score difficulty for a hard negative candidate.

    Higher scores indicate harder cases (false-alarmed more
    consistently, further from any ground-truth mound).

    Components (weighted):
    - **Consistency** (70%): ``vote_count / k_passes``. An FP
      appearing 5/5 times scores 1.0; appearing 1/5 scores 0.2.
    - **Isolation** (30%): ``min(distance / 1000, 1.0)``. FPs far
      from any GT mound are harder (not near-misses).

    Args:
        vote_count: Number of passes that produced this false alarm.
        k_passes: Total number of detection passes.
        nearest_ref_distance: Distance to nearest GT mound in metres
            (None if unknown).

    Returns:
        Difficulty score in [0.0, 1.0].
    """
    if k_passes <= 0:
        return 0.0

    consistency = vote_count / k_passes

    if nearest_ref_distance is not None:
        isolation = min(nearest_ref_distance / 1000.0, 1.0)
    else:
        isolation = 0.5  # Unknown — neutral

    return 0.7 * consistency + 0.3 * isolation
