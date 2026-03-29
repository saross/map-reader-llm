#!/usr/bin/env python3
"""Compare VLM burial mound detection results across different tile sizes.

Tile grids at different resolutions (e.g. 512px vs 384px) do not align
spatially, so standard tile-level permutation tests are invalid. This
script uses two complementary approaches:

1. **Per-mound McNemar test** — For each ground truth mound, determine
   whether each condition detected it (nearest-neighbour within buffer).
   Construct a 2x2 concordance table and run McNemar's exact test to
   assess whether the *discordant* pairs differ significantly.

2. **Per-map-sheet F1 breakdown** — Evaluate each condition independently
   on each of the 4 map sheets using Hungarian matching, reporting F1,
   precision, and recall per map.

Usage — single pair:

    python scripts/compare_tile_sizes.py \\
        --detections-512 outputs/.../detections_512.geojson \\
        --detections-384 outputs/.../detections_384.geojson \\
        --label-512 "512px Image T=0.0" \\
        --label-384 "384px Image T=0.0" \\
        --output-dir results/pairwise/tile-size-30m/mcnemar-image-t0

Usage — batch mode:

    python scripts/compare_tile_sizes.py \\
        --batch configs/tile-size-comparison.yaml \\
        --output-dir results/pairwise/tile-size-mcnemar-30m

FAIR4RS Compliance:
    - Findable: Versioned, descriptive filename, comprehensive metadata
    - Accessible: Standalone CLI with single-pair and batch modes
    - Interoperable: JSON + Markdown output compatible with project tooling
    - Reusable: Fully parameterised, documented arguments

Created: 2026-03-28
Author: Shawn Ross & Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import yaml
from scipy.spatial import cKDTree
from scipy.stats import binomtest
from shapely.ops import unary_union

# ---------------------------------------------------------------------------
# Path setup for sibling imports
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib_advanced_metrics import (  # noqa: E402
    DEFAULT_CRS,
    match_detections_to_references,
    scope_references_to_tiles,
)

__version__ = "1.0.0"

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------
_BASE_DIR = _SCRIPT_DIR.parent
_VECTORS_DIR = _BASE_DIR / "inputs" / "vectors"
_DEFAULT_GROUND_TRUTH = _VECTORS_DIR / "references" / "mounds-reference.geojson"
_DEFAULT_COMMON_BOUNDS = (
    _VECTORS_DIR / "bounds" / "384" / "full_evaluation_bounds.geojson"
)
_TARGET_CRS = DEFAULT_CRS  # EPSG:32635


# ===================================================================
# Data loading helpers
# ===================================================================

def load_geojson(
    path: Path,
    target_crs: str = _TARGET_CRS,
) -> gpd.GeoDataFrame:
    """Load a GeoJSON file and reproject to the target CRS.

    Args:
        path: Path to GeoJSON file.
        target_crs: Target Coordinate Reference System (CRS).

    Returns:
        GeoDataFrame in the target CRS.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON not found: {path}")
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs(target_crs)
    elif str(gdf.crs) != target_crs:
        gdf = gdf.to_crs(target_crs)
    return gdf


def reassign_source_tiles(
    gdf: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Force-reassign source_tile by spatial join with new bounds.

    Unlike ``assign_source_tiles`` in ``pairwise_permutation_test.py``
    which preserves existing assignments, this function always overwrites
    source_tile. Needed when 512px detections carry 512px tile names but
    must be evaluated against the 384px grid.

    Args:
        gdf: Detection GeoDataFrame (any existing source_tile is dropped).
        gdf_bounds: Tile boundary GeoDataFrame with ``tile_name`` column.

    Returns:
        GeoDataFrame with source_tile reassigned from the bounds grid.
    """
    # Work on a copy to avoid mutating the caller's data
    gdf = gdf.copy()

    # Drop old source_tile if present — we want the new grid's names
    if "source_tile" in gdf.columns:
        gdf = gdf.drop(columns=["source_tile"])

    # Spatial join: assign each detection to the tile polygon it falls within
    joined = gpd.sjoin(
        gdf, gdf_bounds[["tile_name", "geometry"]],
        predicate="intersects", how="left",
    )

    # Rename tile_name → source_tile for downstream compatibility
    if "tile_name" in joined.columns:
        joined = joined.rename(columns={"tile_name": "source_tile"})

    # Deduplicate: a point near a tile boundary may match multiple tiles
    joined = joined.drop_duplicates(subset=joined.geometry.name)

    # Clean up spatial join artefact columns
    for col in ["index_right"]:
        if col in joined.columns:
            joined = joined.drop(columns=[col])

    n_assigned = joined["source_tile"].notna().sum()
    logger.info(
        "Reassigned source_tile: %d/%d detections matched to bounds grid",
        n_assigned, len(joined),
    )
    return joined


def scope_to_common_area(
    gdf: gpd.GeoDataFrame,
    common_union: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Spatially filter a GeoDataFrame to the common evaluation area.

    Uses point-in-polygon (or intersects) against the union of common
    bounds polygons. This is a spatial filter on coordinates, NOT on
    source_tile name — essential when detection source_tile names come
    from a different grid.

    Args:
        gdf: GeoDataFrame of points to filter.
        common_union: A single-geometry GeoDataFrame (or Shapely geometry)
            representing the common evaluation area.

    Returns:
        Subset of gdf that falls within the common area.
    """
    if gdf.empty:
        return gdf
    # Filter: keep points that intersect the common area polygon
    mask = gdf.geometry.intersects(common_union)
    result = gdf[mask].copy()
    logger.info(
        "Scoped to common area: %d/%d features retained",
        len(result), len(gdf),
    )
    return result


# ===================================================================
# Step 2: Per-mound McNemar test
# ===================================================================

def build_concordance_table(
    gdf_ref: gpd.GeoDataFrame,
    gdf_det_512: gpd.GeoDataFrame,
    gdf_det_384: gpd.GeoDataFrame,
    buffer_metres: float,
) -> dict:
    """Build a 2x2 concordance table for McNemar's test.

    For each ground truth mound, determine whether it was detected by
    each condition (512px and 384px) using nearest-neighbour search
    within the specified buffer distance.

    Uses ``scipy.spatial.cKDTree`` for efficient nearest-neighbour
    queries in projected (metric) coordinates.

    Args:
        gdf_ref: Ground truth reference mounds (in common area).
        gdf_det_512: Detections from 512px condition (in common area).
        gdf_det_384: Detections from 384px condition (in common area).
        buffer_metres: Maximum distance for a mound to count as detected.

    Returns:
        Dict with keys: 'a' (both detect), 'b' (512 only), 'c' (384 only),
        'd' (neither), 'n_ref', 'per_mound' (list of per-mound results).
    """
    # Extract reference mound centroids as coordinate arrays
    ref_coords = np.array(
        [[geom.centroid.x, geom.centroid.y] for geom in gdf_ref.geometry]
    )
    n_ref = len(ref_coords)

    # Build cKDTrees for each detection set (if non-empty)
    def nearest_distances(
        det_gdf: gpd.GeoDataFrame,
        ref_coords: np.ndarray,
    ) -> np.ndarray:
        """Return nearest-detection distance for each reference point.

        Args:
            det_gdf: Detection GeoDataFrame.
            ref_coords: Nx2 array of reference point coordinates.

        Returns:
            Array of distances; np.inf where no detections exist.
        """
        if det_gdf.empty:
            return np.full(len(ref_coords), np.inf)
        det_coords = np.array(
            [[g.centroid.x, g.centroid.y] for g in det_gdf.geometry]
        )
        tree = cKDTree(det_coords)
        distances, _ = tree.query(ref_coords)
        return distances

    dist_512 = nearest_distances(gdf_det_512, ref_coords)
    dist_384 = nearest_distances(gdf_det_384, ref_coords)

    # Classify each mound
    detected_512 = dist_512 <= buffer_metres
    detected_384 = dist_384 <= buffer_metres

    # 2x2 concordance table
    #              384_yes  384_no
    # 512_yes        a        b
    # 512_no         c        d
    a = int(np.sum(detected_512 & detected_384))      # Both detect
    b = int(np.sum(detected_512 & ~detected_384))     # 512 only
    c = int(np.sum(~detected_512 & detected_384))     # 384 only
    d = int(np.sum(~detected_512 & ~detected_384))    # Neither

    # Per-mound detail for full transparency
    per_mound = []
    for i in range(n_ref):
        per_mound.append({
            "ref_index": int(gdf_ref.index[i]),
            "x": float(ref_coords[i, 0]),
            "y": float(ref_coords[i, 1]),
            "dist_512": round(float(dist_512[i]), 2),
            "dist_384": round(float(dist_384[i]), 2),
            "detected_512": bool(detected_512[i]),
            "detected_384": bool(detected_384[i]),
        })

    return {
        "a": a,
        "b": b,
        "c": c,
        "d": d,
        "n_ref": n_ref,
        "per_mound": per_mound,
    }


def run_mcnemar_test(concordance: dict) -> dict:
    """Run McNemar's exact test on the concordance table.

    Uses the exact binomial test (appropriate for small cell counts)
    rather than the chi-squared approximation. The null hypothesis is
    that the discordant pairs (b and c) are equally likely under
    either condition.

    Test statistic: min(b, c) successes in b + c Bernoulli trials
    with p = 0.5 (two-sided).

    Args:
        concordance: Dict with keys 'a', 'b', 'c', 'd' from
            ``build_concordance_table``.

    Returns:
        Dict with McNemar test results including p-value, direction,
        and interpretation.
    """
    b = concordance["b"]  # 512 detected, 384 missed
    c = concordance["c"]  # 384 detected, 512 missed
    n_discordant = b + c

    if n_discordant == 0:
        # No discordant pairs — the conditions are identical on all mounds
        return {
            "b_512_only": b,
            "c_384_only": c,
            "n_discordant": 0,
            "p_value": 1.0,
            "direction": "identical",
            "interpretation": (
                "No discordant pairs — both conditions detected "
                "exactly the same mounds."
            ),
        }

    # Exact binomial test: is min(b, c) surprisingly small
    # given b + c trials at p = 0.5?
    result = binomtest(min(b, c), n_discordant, 0.5)
    p_value = result.pvalue

    # Determine direction
    if b > c:
        direction = "512px detects more unique mounds"
    elif c > b:
        direction = "384px detects more unique mounds"
    else:
        direction = "equal discordant counts"

    # Significance flag
    if p_value < 0.001:
        sig = "***"
    elif p_value < 0.01:
        sig = "**"
    elif p_value < 0.05:
        sig = "*"
    else:
        sig = "ns"

    return {
        "b_512_only": b,
        "c_384_only": c,
        "n_discordant": n_discordant,
        "p_value": round(p_value, 6),
        "significance": sig,
        "direction": direction,
        "interpretation": (
            f"Of {n_discordant} discordant mounds, {b} detected only "
            f"by 512px and {c} detected only by 384px. "
            f"McNemar p = {p_value:.4f} ({sig})."
        ),
    }


# ===================================================================
# Step 3: Per-map-sheet F1 breakdown
# ===================================================================

def evaluate_per_map(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: float,
    label: str,
) -> list[dict]:
    """Evaluate detection performance per map sheet.

    For each map sheet (identified by the ``map_name`` column in bounds),
    spatially filter detections and references, then run Hungarian
    matching to compute F1, precision, and recall.

    Detections are filtered spatially (point-in-polygon against the
    map's bounds union) rather than by source_tile prefix, ensuring
    correct behaviour when detections originate from a different grid.

    Args:
        gdf_det: Detection GeoDataFrame (source_tile should be
            reassigned to the common bounds grid).
        gdf_ref: Ground truth reference GeoDataFrame with ``Map`` column.
        gdf_bounds: Tile boundary GeoDataFrame with ``map_name`` column.
        buffer_metres: Spatial matching tolerance in metres.
        label: Human-readable label for this condition.

    Returns:
        List of dicts, one per map sheet, with F1/P/R and counts.
    """
    map_names = sorted(gdf_bounds["map_name"].unique())
    results = []

    for map_name in map_names:
        # Get this map's tile bounds
        map_bounds = gdf_bounds[gdf_bounds["map_name"] == map_name]
        map_union = unary_union(map_bounds.geometry)

        # Spatially filter detections to this map's area
        if not gdf_det.empty:
            det_mask = gdf_det.geometry.intersects(map_union)
            det_map = gdf_det[det_mask]
        else:
            det_map = gdf_det.iloc[0:0]

        # Filter references by Map column (canonical assignment)
        ref_map = gdf_ref[gdf_ref["Map"] == map_name]
        # Further scope to tiles that are actually in our bounds
        if not ref_map.empty:
            ref_map = scope_references_to_tiles(ref_map, map_bounds)

        n_det = len(det_map)
        n_ref = len(ref_map)

        if n_det == 0 and n_ref == 0:
            results.append({
                "map_name": map_name,
                "label": label,
                "n_detections": 0,
                "n_references": 0,
                "tp": 0, "fp": 0, "fn": 0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
            })
            continue

        if n_det == 0:
            results.append({
                "map_name": map_name,
                "label": label,
                "n_detections": 0,
                "n_references": n_ref,
                "tp": 0, "fp": 0, "fn": n_ref,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
            })
            continue

        if n_ref == 0:
            results.append({
                "map_name": map_name,
                "label": label,
                "n_detections": n_det,
                "n_references": 0,
                "tp": 0, "fp": n_det, "fn": 0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
            })
            continue

        # Hungarian matching
        det_geoms = list(det_map.geometry)
        ref_geoms = list(ref_map.geometry)
        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(
                det_geoms, ref_geoms, buffer_metres,
            )
        )

        tp = len(matched_det)
        fp = len(unmatched_det)
        fn = len(unmatched_ref)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0 else 0.0
        )

        results.append({
            "map_name": map_name,
            "label": label,
            "n_detections": n_det,
            "n_references": n_ref,
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        })

    return results


# ===================================================================
# Single comparison runner
# ===================================================================

def run_comparison(
    detections_512_path: Path,
    detections_384_path: Path,
    label_512: str,
    label_384: str,
    ground_truth_path: Path,
    common_bounds_path: Path,
    buffer_metres: float,
    seed: int,
) -> dict:
    """Run a single tile-size comparison (McNemar + per-map F1).

    This is the core comparison function, called once per matched pair.

    Args:
        detections_512_path: Path to 512px detection GeoJSON.
        detections_384_path: Path to 384px detection GeoJSON.
        label_512: Human-readable label for 512px condition.
        label_384: Human-readable label for 384px condition.
        ground_truth_path: Path to ground truth GeoJSON.
        common_bounds_path: Path to common evaluation bounds GeoJSON
            (384px grid = smaller footprint = common area).
        buffer_metres: Spatial matching tolerance in metres.
        seed: Random seed (reserved for future bootstrap extensions).

    Returns:
        Dict with McNemar results, per-map breakdown, and metadata.
    """
    logger.info("Loading data...")
    logger.info("  Ground truth: %s", ground_truth_path)
    logger.info("  Common bounds: %s", common_bounds_path)
    logger.info("  512px detections: %s", detections_512_path)
    logger.info("  384px detections: %s", detections_384_path)

    # Step 1: Load data
    gdf_ref = load_geojson(ground_truth_path)
    gdf_bounds = load_geojson(common_bounds_path)
    gdf_det_512 = load_geojson(detections_512_path)
    gdf_det_384 = load_geojson(detections_384_path)

    # Compute common area as the union of all 384px tile bounds
    common_area = unary_union(gdf_bounds.geometry)

    # Scope ground truth to common area (per-tile intersection, not union)
    # This ensures we only evaluate mounds that fall within the 384px grid
    gdf_ref_scoped = scope_references_to_tiles(gdf_ref, gdf_bounds)
    logger.info(
        "Ground truth: %d total, %d in common area",
        len(gdf_ref), len(gdf_ref_scoped),
    )

    # Scope detections to common area — spatial filter on coordinates
    gdf_det_512_scoped = scope_to_common_area(gdf_det_512, common_area)
    gdf_det_384_scoped = scope_to_common_area(gdf_det_384, common_area)
    logger.info(
        "512px detections: %d total, %d in common area",
        len(gdf_det_512), len(gdf_det_512_scoped),
    )
    logger.info(
        "384px detections: %d total, %d in common area",
        len(gdf_det_384), len(gdf_det_384_scoped),
    )

    # Reassign 512px source_tile names to the 384px grid for per-map eval
    # (the existing source_tile values reference the 512px tiling scheme)
    gdf_det_512_reassigned = reassign_source_tiles(
        gdf_det_512_scoped, gdf_bounds,
    )
    # Also ensure 384px detections have correct source_tile assignments
    # (they should already, but reassign for consistency)
    gdf_det_384_reassigned = reassign_source_tiles(
        gdf_det_384_scoped, gdf_bounds,
    )

    # Step 2: McNemar test on per-mound concordance
    logger.info(
        "Running McNemar test (buffer = %d m)...", buffer_metres,
    )
    concordance = build_concordance_table(
        gdf_ref_scoped,
        gdf_det_512_scoped,
        gdf_det_384_scoped,
        buffer_metres,
    )
    mcnemar_result = run_mcnemar_test(concordance)

    # Step 3: Per-map-sheet F1 breakdown
    logger.info("Computing per-map F1 breakdown...")
    per_map_512 = evaluate_per_map(
        gdf_det_512_reassigned, gdf_ref_scoped, gdf_bounds,
        buffer_metres, label_512,
    )
    per_map_384 = evaluate_per_map(
        gdf_det_384_reassigned, gdf_ref_scoped, gdf_bounds,
        buffer_metres, label_384,
    )

    # Compute global F1 for each condition (aggregate across all maps)
    def _aggregate_metrics(
        per_map: list[dict],
    ) -> dict:
        """Sum TP/FP/FN across maps and compute global F1/P/R."""
        tp = sum(m["tp"] for m in per_map)
        fp = sum(m["fp"] for m in per_map)
        fn = sum(m["fn"] for m in per_map)
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        return {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
        }

    global_512 = _aggregate_metrics(per_map_512)
    global_384 = _aggregate_metrics(per_map_384)

    return {
        "labels": {
            "condition_512": label_512,
            "condition_384": label_384,
        },
        "scoping": {
            "n_ref_total": len(gdf_ref),
            "n_ref_in_common_area": len(gdf_ref_scoped),
            "n_det_512_total": len(gdf_det_512),
            "n_det_512_in_common_area": len(gdf_det_512_scoped),
            "n_det_384_total": len(gdf_det_384),
            "n_det_384_in_common_area": len(gdf_det_384_scoped),
        },
        "mcnemar": {
            "concordance_table": {
                "both_detect": concordance["a"],
                "512_only": concordance["b"],
                "384_only": concordance["c"],
                "neither": concordance["d"],
            },
            "test": mcnemar_result,
        },
        "global_512": global_512,
        "global_384": global_384,
        "f1_difference": round(
            global_512["f1"] - global_384["f1"], 4,
        ),
        "per_map_512": per_map_512,
        "per_map_384": per_map_384,
    }


# ===================================================================
# Output formatting
# ===================================================================

def format_markdown_summary(
    result: dict,
    label: str | None = None,
) -> str:
    """Format a single comparison result as a Markdown summary.

    Args:
        result: Dict from ``run_comparison``.
        label: Optional heading label for the comparison.

    Returns:
        Markdown-formatted string.
    """
    lines = []
    heading = label or (
        f"{result['labels']['condition_512']} vs "
        f"{result['labels']['condition_384']}"
    )
    lines.append(f"## {heading}")
    lines.append("")

    # Scoping summary
    sc = result["scoping"]
    lines.append(
        f"**Scoping**: {sc['n_ref_in_common_area']} reference mounds "
        f"in common area (of {sc['n_ref_total']} total)"
    )
    lines.append("")
    lines.append(
        f"- 512px: {sc['n_det_512_in_common_area']} detections "
        f"(of {sc['n_det_512_total']} total)"
    )
    lines.append(
        f"- 384px: {sc['n_det_384_in_common_area']} detections "
        f"(of {sc['n_det_384_total']} total)"
    )
    lines.append("")

    # McNemar table
    mc = result["mcnemar"]
    ct = mc["concordance_table"]
    lines.append("**McNemar concordance table** (per-mound detection):")
    lines.append("")
    lines.append(
        "| | 384px detected | 384px missed |"
    )
    lines.append("| --- | ---: | ---: |")
    lines.append(
        f"| **512px detected** | {ct['both_detect']} | "
        f"{ct['512_only']} |"
    )
    lines.append(
        f"| **512px missed** | {ct['384_only']} | "
        f"{ct['neither']} |"
    )
    lines.append("")

    # McNemar test result
    test = mc["test"]
    lines.append(
        f"**McNemar test**: b={test['b_512_only']}, "
        f"c={test['c_384_only']}, "
        f"p={test['p_value']:.4f} "
        f"({test.get('significance', 'ns')})"
    )
    lines.append("")
    lines.append(f"- Direction: {test['direction']}")
    lines.append("")

    # Global F1 comparison
    g512 = result["global_512"]
    g384 = result["global_384"]
    lines.append("**Global F1** (Hungarian matching on common area):")
    lines.append("")
    lines.append("| Condition | F1 | Precision | Recall | TP | FP | FN |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    lines.append(
        f"| {result['labels']['condition_512']} | "
        f"{g512['f1']:.4f} | {g512['precision']:.4f} | "
        f"{g512['recall']:.4f} | {g512['tp']} | "
        f"{g512['fp']} | {g512['fn']} |"
    )
    lines.append(
        f"| {result['labels']['condition_384']} | "
        f"{g384['f1']:.4f} | {g384['precision']:.4f} | "
        f"{g384['recall']:.4f} | {g384['tp']} | "
        f"{g384['fp']} | {g384['fn']} |"
    )
    lines.append("")
    lines.append(
        f"**Delta F1** (512 - 384): {result['f1_difference']:+.4f}"
    )
    lines.append("")

    # Per-map breakdown
    lines.append("**Per-map-sheet breakdown**:")
    lines.append("")
    lines.append(
        "| Map | Condition | F1 | P | R | TP | FP | FN | "
        "Det | Ref |"
    )
    lines.append(
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | "
        "---: | ---: |"
    )
    for m512, m384 in zip(
        result["per_map_512"], result["per_map_384"],
    ):
        # Short map name for readability
        short = m512["map_name"].split("_")[0]
        lines.append(
            f"| {short} | 512px | {m512['f1']:.4f} | "
            f"{m512['precision']:.4f} | {m512['recall']:.4f} | "
            f"{m512['tp']} | {m512['fp']} | {m512['fn']} | "
            f"{m512['n_detections']} | {m512['n_references']} |"
        )
        lines.append(
            f"| {short} | 384px | {m384['f1']:.4f} | "
            f"{m384['precision']:.4f} | {m384['recall']:.4f} | "
            f"{m384['tp']} | {m384['fp']} | {m384['fn']} | "
            f"{m384['n_detections']} | {m384['n_references']} |"
        )
    lines.append("")

    return "\n".join(lines)


def print_console_summary(result: dict) -> None:
    """Print a concise console summary of the comparison.

    Args:
        result: Dict from ``run_comparison``.
    """
    l512 = result["labels"]["condition_512"]
    l384 = result["labels"]["condition_384"]
    g512 = result["global_512"]
    g384 = result["global_384"]
    mc = result["mcnemar"]["test"]

    print(f"\n{'=' * 60}")
    print(f"  {l512}  vs  {l384}")
    print(f"{'=' * 60}")
    print(
        f"  512px: F1={g512['f1']:.4f} "
        f"(P={g512['precision']:.3f}, "
        f"R={g512['recall']:.3f})"
    )
    print(
        f"  384px: F1={g384['f1']:.4f} "
        f"(P={g384['precision']:.3f}, "
        f"R={g384['recall']:.3f})"
    )
    print(
        f"  Delta F1 (512 - 384): "
        f"{result['f1_difference']:+.4f}"
    )
    print()
    ct = result["mcnemar"]["concordance_table"]
    print(
        f"  McNemar: both={ct['both_detect']}, "
        f"512-only={ct['512_only']}, "
        f"384-only={ct['384_only']}, "
        f"neither={ct['neither']}"
    )
    print(
        f"  p={mc['p_value']:.4f} "
        f"({mc.get('significance', 'ns')}), "
        f"{mc['direction']}"
    )

    # Compact per-map table
    print()
    print(
        f"  {'Map':<20} {'512 F1':>7} {'384 F1':>7} "
        f"{'Delta':>7}"
    )
    print(f"  {'-' * 41}")
    for m512, m384 in zip(
        result["per_map_512"], result["per_map_384"],
    ):
        delta = m512["f1"] - m384["f1"]
        short = m512["map_name"].split("_")[0]
        print(
            f"  {short:<20} {m512['f1']:>7.4f} "
            f"{m384['f1']:>7.4f} {delta:>+7.4f}"
        )
    print()


# ===================================================================
# CLI and main
# ===================================================================

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Compare VLM detection results across different tile sizes "
            "using per-mound McNemar test and per-map F1 breakdown."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )

    # --- Single-pair mode ---
    parser.add_argument(
        "--detections-512", type=Path,
        help="Path to 512px detection GeoJSON",
    )
    parser.add_argument(
        "--detections-384", type=Path,
        help="Path to 384px detection GeoJSON",
    )
    parser.add_argument(
        "--label-512", type=str, default="512px",
        help="Label for 512px condition (default: '512px')",
    )
    parser.add_argument(
        "--label-384", type=str, default="384px",
        help="Label for 384px condition (default: '384px')",
    )

    # --- Batch mode ---
    parser.add_argument(
        "--batch", type=Path,
        help="Path to YAML config for batch comparisons",
    )

    # --- Common arguments ---
    parser.add_argument(
        "--ground-truth", type=Path,
        default=_DEFAULT_GROUND_TRUTH,
        help=(
            "Ground truth reference GeoJSON "
            f"(default: {_DEFAULT_GROUND_TRUTH.name})"
        ),
    )
    parser.add_argument(
        "--common-bounds", type=Path,
        default=_DEFAULT_COMMON_BOUNDS,
        help=(
            "Common evaluation bounds GeoJSON — the smaller grid "
            f"(default: {_DEFAULT_COMMON_BOUNDS.name})"
        ),
    )
    parser.add_argument(
        "--buffer-metres", type=float, default=20,
        help=(
            "Spatial matching tolerance in metres for detection "
            "matching (default: 20)"
        ),
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for results",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress console output",
    )

    args = parser.parse_args()

    # Validate: either batch or single-pair must be specified
    if args.batch is None:
        if args.detections_512 is None or args.detections_384 is None:
            parser.error(
                "Either --batch or both --detections-512 and "
                "--detections-384 are required"
            )

    return args


def run_batch(
    config_path: Path,
    output_dir: Path,
    ground_truth_override: Path | None = None,
    common_bounds_override: Path | None = None,
    buffer_metres_override: float | None = None,
    seed: int = 42,
    quiet: bool = False,
) -> list[dict]:
    """Run batch comparisons from a YAML configuration file.

    Args:
        config_path: Path to YAML batch config.
        output_dir: Root output directory.
        ground_truth_override: Override ground truth path from CLI.
        common_bounds_override: Override common bounds path from CLI.
        buffer_metres_override: Override buffer from CLI.
        seed: Random seed.
        quiet: Suppress console output.

    Returns:
        List of result dicts, one per comparison.
    """
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    defaults = config.get("defaults", {})
    comparisons = config.get("comparisons", [])

    if not comparisons:
        logger.error("No comparisons defined in %s", config_path)
        return []

    # Resolve defaults (CLI overrides take precedence)
    gt_path = (
        ground_truth_override
        or Path(defaults.get("ground_truth", str(_DEFAULT_GROUND_TRUTH)))
    )
    bounds_path = (
        common_bounds_override
        or Path(defaults.get(
            "common_bounds", str(_DEFAULT_COMMON_BOUNDS),
        ))
    )
    buffer_m = (
        buffer_metres_override
        or defaults.get("buffer_metres", 30)
    )

    all_results = []
    for i, comp in enumerate(comparisons, 1):
        label = comp.get("label", f"Comparison {i}")
        # Derive condition labels
        label_512 = comp.get("label_512", f"512px {label}")
        label_384 = comp.get("label_384", f"384px {label}")

        det_512_path = Path(comp["detections_512"])
        det_384_path = Path(comp["detections_384"])

        # Per-comparison overrides
        comp_gt = Path(comp["ground_truth"]) if "ground_truth" in comp else gt_path
        comp_bounds = (
            Path(comp["common_bounds"])
            if "common_bounds" in comp
            else bounds_path
        )
        comp_buffer = comp.get("buffer_metres", buffer_m)

        logger.info(
            "\n[%d/%d] %s", i, len(comparisons), label,
        )

        result = run_comparison(
            detections_512_path=det_512_path,
            detections_384_path=det_384_path,
            label_512=label_512,
            label_384=label_384,
            ground_truth_path=comp_gt,
            common_bounds_path=comp_bounds,
            buffer_metres=comp_buffer,
            seed=seed,
        )

        if not quiet:
            print_console_summary(result)

        all_results.append({"label": label, "result": result})

    return all_results


def main() -> None:
    """Run tile-size comparison (single pair or batch)."""
    args = parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.batch:
        # ---- Batch mode ----
        logger.info("Batch mode: %s", args.batch)
        all_results = run_batch(
            config_path=args.batch,
            output_dir=args.output_dir,
            ground_truth_override=(
                args.ground_truth
                if args.ground_truth != _DEFAULT_GROUND_TRUTH
                else None
            ),
            common_bounds_override=(
                args.common_bounds
                if args.common_bounds != _DEFAULT_COMMON_BOUNDS
                else None
            ),
            buffer_metres_override=(
                args.buffer_metres
                if args.buffer_metres != 30
                else None
            ),
            seed=args.seed,
            quiet=args.quiet,
        )

        # Write combined JSON output
        output = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "script": "compare_tile_sizes.py",
                "version": __version__,
                "batch_config": str(args.batch.resolve()),
                "buffer_metres": args.buffer_metres,
                "seed": args.seed,
            },
            "comparisons": all_results,
        }
        json_path = args.output_dir / "tile_size_comparison.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        logger.info("JSON results: %s", json_path)

        # Write combined Markdown summary
        md_lines = [
            "# Tile Size Comparison: 512px vs 384px",
            "",
            f"Generated: "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            f"Buffer: {args.buffer_metres} m",
            "",
        ]
        for entry in all_results:
            md_lines.append(
                format_markdown_summary(
                    entry["result"], label=entry["label"],
                )
            )
        md_path = args.output_dir / "tile_size_comparison.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        logger.info("Markdown summary: %s", md_path)

        # Print batch summary table
        if not args.quiet:
            print(f"\n{'=' * 70}")
            print("  BATCH SUMMARY")
            print(f"{'=' * 70}")
            print(
                f"  {'Comparison':<25} {'512 F1':>7} "
                f"{'384 F1':>7} {'Delta':>7} "
                f"{'McNemar p':>10} {'Sig':>4}"
            )
            print(f"  {'-' * 63}")
            for entry in all_results:
                r = entry["result"]
                mc = r["mcnemar"]["test"]
                print(
                    f"  {entry['label']:<25} "
                    f"{r['global_512']['f1']:>7.4f} "
                    f"{r['global_384']['f1']:>7.4f} "
                    f"{r['f1_difference']:>+7.4f} "
                    f"{mc['p_value']:>10.4f} "
                    f"{mc.get('significance', 'ns'):>4}"
                )
            print()

    else:
        # ---- Single-pair mode ----
        result = run_comparison(
            detections_512_path=args.detections_512,
            detections_384_path=args.detections_384,
            label_512=args.label_512,
            label_384=args.label_384,
            ground_truth_path=args.ground_truth,
            common_bounds_path=args.common_bounds,
            buffer_metres=args.buffer_metres,
            seed=args.seed,
        )

        if not args.quiet:
            print_console_summary(result)

        # Write JSON output
        output = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "script": "compare_tile_sizes.py",
                "version": __version__,
                "detections_512": str(
                    args.detections_512.resolve(),
                ),
                "detections_384": str(
                    args.detections_384.resolve(),
                ),
                "ground_truth": str(args.ground_truth.resolve()),
                "common_bounds": str(args.common_bounds.resolve()),
                "buffer_metres": args.buffer_metres,
                "seed": args.seed,
            },
            "result": result,
        }
        json_path = args.output_dir / "tile_size_comparison.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        logger.info("JSON results: %s", json_path)

        # Write Markdown summary
        md_path = args.output_dir / "tile_size_comparison.md"
        md_content = format_markdown_summary(result)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.info("Markdown summary: %s", md_path)

    print(f"Results written to: {args.output_dir}")


if __name__ == "__main__":
    main()
