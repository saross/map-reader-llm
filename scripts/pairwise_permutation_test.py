#!/usr/bin/env python3
"""Generalised paired permutation test for detection condition comparison.

Compares two detection conditions using a paired permutation test at tile
level. Supports three input modes:

- **pv**: Proposer-Verifier results (probabilities.json + manifest + threshold)
- **consensus**: Consensus voting study directories (study dir + config string)
- **geojson**: Arbitrary detection GeoJSON files with source_tile property

All modes normalise inputs to GeoDataFrames with ``source_tile`` and
``geometry`` columns, then run the same paired permutation test.

Usage — PV mode (verifier comparison):

    python scripts/pairwise_permutation_test.py \\
        --mode pv \\
        --probabilities-a outputs/.../probabilities.json \\
        --manifest-a outputs/.../candidate_manifest.json \\
        --threshold-a 0.25 \\
        --label-a "Flash HIGH text 4-of-5 + Pro vf" \\
        --probabilities-b outputs/.../probabilities.json \\
        --manifest-b outputs/.../candidate_manifest.json \\
        --threshold-b 0.15 \\
        --label-b "Flash HIGH text 4-of-5 + Flash min vf" \\
        --output-dir results/pairwise/pro-vs-flash-verifier

Usage — Consensus mode:

    python scripts/pairwise_permutation_test.py \\
        --mode consensus \\
        --study-dir-a outputs/h11/pv-diag-384/flash-high-text-n5 \\
        --config-a "text-t0.7,5,5" \\
        --label-a "Flash HIGH text 5-of-5" \\
        --study-dir-b outputs/h11/pv-diag-384/flash-minimal-text-n30-t07 \\
        --config-b "text-t0.7,5,5" \\
        --label-b "Flash MINIMAL T=0.7 5-of-5" \\
        --output-dir results/pairwise/high-vs-minimal

Usage — GeoJSON mode:

    python scripts/pairwise_permutation_test.py \\
        --mode geojson \\
        --geojson-a outputs/.../detections_a.geojson \\
        --label-a "Condition A" \\
        --geojson-b outputs/.../detections_b.geojson \\
        --label-b "Condition B" \\
        --output-dir results/pairwise/custom

Output:
    - ``pairwise_permutation_result.json`` — full results with per-tile data
    - Console summary with test statistics

FAIR4RS Compliance:
    - Findable: Versioned, descriptive filename, comprehensive metadata
    - Accessible: Standalone CLI with three input modes
    - Interoperable: JSON output compatible with existing pairwise results
    - Reusable: Fully parameterised, mode-independent core, documented args

Author: Shawn Ross & Claude (Anthropic)
Version: 1.0.0
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

# Ensure scripts/ is on the path for sibling imports
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_classification,
    compute_per_tile_tp_fp_fn,
)

__version__ = "1.0.0"

logger = logging.getLogger(__name__)

# Default paths
BASE_DIR = _SCRIPT_DIR.parent
_VECTORS_DIR = BASE_DIR / "inputs" / "vectors"
_BOUNDS_PATH = _VECTORS_DIR / "bounds" / "384" / "full_evaluation_bounds.geojson"
_REF_PATH = _VECTORS_DIR / "references" / "mounds-reference.geojson"
_TARGET_CRS = "EPSG:32635"


# -----------------------------------------------
# Input loaders — one per mode
# -----------------------------------------------

def load_pv_detections(
    probabilities_path: Path,
    manifest_path: Path,
    threshold: float,
) -> gpd.GeoDataFrame:
    """Load PV verifier results and filter by probability threshold.

    Args:
        probabilities_path: Path to probabilities.json.
        manifest_path: Path to candidate_manifest.json.
        threshold: Minimum mound_probability for acceptance.

    Returns:
        GeoDataFrame with source_tile and geometry columns.
    """
    from evaluate_pv_results import build_candidate_gdf, load_probabilities

    probabilities = load_probabilities(probabilities_path)
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    gdf = build_candidate_gdf(manifest, probabilities, threshold)
    logger.info(
        "PV: %d detections at threshold %.2f from %s",
        len(gdf), threshold, probabilities_path.parent.name,
    )
    return gdf


def load_consensus_detections(
    study_dir: Path,
    config_str: str,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Load consensus voting results and apply vote threshold.

    Args:
        study_dir: Path to condition output directory.
        config_str: Comma-separated "temperature,pool_size,threshold"
            (e.g., "text-t0.7,5,5" or "T0.7,30,22").
        gdf_bounds: Tile boundary GeoDataFrame for source_tile assignment.

    Returns:
        GeoDataFrame with source_tile and geometry columns.
    """
    from analyse_consensus_sweep import consensus_to_gdf, precompute_clusters
    from paired_permutation_consensus import apply_threshold

    parts = config_str.split(",")
    if len(parts) != 3:
        msg = (
            f"Config must be 'temperature,pool_size,threshold', "
            f"got '{config_str}'"
        )
        raise ValueError(msg)

    temperature = parts[0].strip()
    pool_size = int(parts[1].strip())
    threshold = int(parts[2].strip())

    clusters_dict = precompute_clusters(
        study_dir,
        temperatures=[temperature],
        pool_sizes=[pool_size],
    )

    clusters = clusters_dict.get((temperature, pool_size), [])
    if not clusters:
        logger.error(
            "No clusters for %s N=%d in %s",
            temperature, pool_size, study_dir,
        )
        return gpd.GeoDataFrame(
            columns=["source_tile", "geometry"],
            geometry="geometry",
            crs=_TARGET_CRS,
        )

    consensus_fc = apply_threshold(clusters, threshold, pool_size)
    gdf = consensus_to_gdf(consensus_fc, gdf_bounds)
    logger.info(
        "Consensus: %d detections at %s N=%d x=%d from %s",
        len(gdf), temperature, pool_size, threshold, study_dir.name,
    )
    return gdf


def load_geojson_detections(
    geojson_path: Path,
) -> gpd.GeoDataFrame:
    """Load detections from a GeoJSON file.

    The GeoJSON must contain a ``source_tile`` property on each feature.
    If absent, the script will attempt to assign tiles via spatial join
    with the evaluation bounds.

    Single-pass+PV repair: when the file has a ``verified`` column and
    contains coordinates that look projected (UTM-magnitude — values
    in the hundreds of thousands rather than degrees), filter to
    ``verified=True`` and override the CRS to EPSG:32635 instead of
    transforming. This repairs the
    ``outputs/h11/proposer-verifier-384/verified-*.geojson`` files
    which lack a CRS declaration but carry already-projected
    coordinates. See ``build_tiered_leaderboard._evaluate_single_threshold``
    for the matching logic on the F1 evaluation path.

    Args:
        geojson_path: Path to detection GeoJSON file.

    Returns:
        GeoDataFrame with source_tile and geometry columns.
    """
    gdf = gpd.read_file(geojson_path)

    # Single-pass+PV repair: detect via the ``verified`` column and
    # UTM-magnitude coordinates (any X coord > 1e5 with EPSG:4326
    # default is the signature of a UTM-mislabelled file).
    repair_pv = (
        not gdf.empty
        and "verified" in gdf.columns
        and gdf.crs is not None
        and gdf.crs.to_epsg() == 4326
        and gdf.geometry.iloc[0].centroid.x > 1e5
    )
    if repair_pv:
        gdf = gdf.set_crs(_TARGET_CRS, allow_override=True)
        gdf = gdf[gdf["verified"] == True].copy()  # noqa: E712
        gdf["geometry"] = gdf.geometry.centroid
        logger.info(
            "PV repair: %d verified detections retained from %s "
            "(CRS overridden to EPSG:32635, polygons → centroids)",
            len(gdf), geojson_path.name,
        )
    elif gdf.crs is None:
        gdf = gdf.set_crs(_TARGET_CRS)
    elif gdf.crs.to_epsg() != 32635:
        gdf = gdf.to_crs(_TARGET_CRS)

    if "source_tile" not in gdf.columns:
        logger.warning(
            "GeoJSON lacks source_tile — will assign via spatial join"
        )

    logger.info(
        "GeoJSON: %d detections from %s",
        len(gdf), geojson_path.name,
    )
    return gdf


def assign_source_tiles(
    gdf: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Assign source_tile via spatial join if not already present.

    Args:
        gdf: Detection GeoDataFrame.
        gdf_bounds: Tile boundary GeoDataFrame with tile_name column.

    Returns:
        GeoDataFrame with source_tile column guaranteed.
    """
    if "source_tile" in gdf.columns and gdf["source_tile"].notna().all():
        return gdf

    joined = gpd.sjoin(gdf, gdf_bounds, predicate="intersects", how="left")
    if "tile_name" in joined.columns:
        # Only fill NaN source_tile values — preserve existing assignments
        if "source_tile" in joined.columns:
            joined["source_tile"] = joined["source_tile"].fillna(
                joined["tile_name"]
            )
        else:
            joined["source_tile"] = joined["tile_name"]
    joined = joined.drop_duplicates(subset=joined.geometry.name)
    # Drop sjoin artefact columns
    for col in ["index_right", "tile_name"]:
        if col in joined.columns:
            joined = joined.drop(columns=[col])

    n_assigned = joined["source_tile"].notna().sum()
    logger.info(
        "Assigned source_tile to %d/%d detections via spatial join",
        n_assigned, len(joined),
    )
    return joined


# -----------------------------------------------
# Core permutation test — mode-independent
# -----------------------------------------------

def _compute_f1(tp: int, fp: int, fn: int) -> float:
    """Compute F1 from aggregate counts, returning 0.0 for edge cases."""
    if tp == 0:
        return 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def run_permutation_test(
    gdf_a: gpd.GeoDataFrame,
    gdf_b: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int = 20,
    n_permutations: int = 10_000,
    seed: int = 42,
) -> dict:
    """Run paired tile-swap permutation test comparing two detection sets.

    Uses **micro-average F1** (aggregate TP/FP/FN then compute F1) as the
    test statistic, matching the project's standard F1 reporting. For each
    permutation, independently swaps per-tile TP/FP/FN assignments between
    conditions with probability 0.5, then re-aggregates.

    This is a proper permutation test under the null hypothesis that
    condition labels are exchangeable within each tile. See protocol
    erratum E45 for the rationale for using micro-average rather than
    macro-average (per-tile F1 differences).

    Args:
        gdf_a: Detection GeoDataFrame for condition A.
        gdf_b: Detection GeoDataFrame for condition B.
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Evaluation tile boundaries.
        buffer_metres: Spatial matching tolerance in metres.
        n_permutations: Number of permutation iterations.
        seed: Random seed for reproducibility.

    Returns:
        Dict with observed difference, p-value, win/loss counts,
        null distribution statistics, and per-tile details.
    """
    # Pre-compute per-tile metrics
    tm_a = compute_per_tile_tp_fp_fn(
        gdf_a, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )
    tm_b = compute_per_tile_tp_fp_fn(
        gdf_b, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )

    # Get all tiles and build aligned arrays of per-tile counts
    tiles = gdf_bounds["tile_name"].unique()
    n_tiles = len(tiles)

    # Build aligned per-tile count arrays (tp, fp, fn for each condition)
    tp_a_arr = np.zeros(n_tiles, dtype=int)
    fp_a_arr = np.zeros(n_tiles, dtype=int)
    fn_a_arr = np.zeros(n_tiles, dtype=int)
    tp_b_arr = np.zeros(n_tiles, dtype=int)
    fp_b_arr = np.zeros(n_tiles, dtype=int)
    fn_b_arr = np.zeros(n_tiles, dtype=int)

    # Index tile_metrics by tile_name for fast lookup
    tm_a_idx = tm_a.set_index("tile_name")
    tm_b_idx = tm_b.set_index("tile_name")

    # Single pass: populate per-tile counts, F1, and win/loss/tie
    per_tile_details = []
    wins = losses = ties = 0

    for i, tile in enumerate(tiles):
        if tile in tm_a_idx.index:
            row = tm_a_idx.loc[tile]
            tp_a_arr[i] = int(row["tp"])
            fp_a_arr[i] = int(row["fp"])
            fn_a_arr[i] = int(row["fn"])
        if tile in tm_b_idx.index:
            row = tm_b_idx.loc[tile]
            tp_b_arr[i] = int(row["tp"])
            fp_b_arr[i] = int(row["fp"])
            fn_b_arr[i] = int(row["fn"])

        # Per-tile metrics (for reporting and win/loss counting)
        ta, fa_val, fb_val = tp_a_arr[i], fp_a_arr[i], fn_a_arr[i]
        tb, fb_fp, fb_fn = tp_b_arr[i], fp_b_arr[i], fn_b_arr[i]
        f1_tile_a = _compute_f1(ta, fa_val, fb_val)
        f1_tile_b = _compute_f1(tb, fb_fp, fb_fn)
        p_tile_a = ta / (ta + fa_val) if (ta + fa_val) > 0 else 0.0
        r_tile_a = ta / (ta + fb_val) if (ta + fb_val) > 0 else 0.0
        p_tile_b = tb / (tb + fb_fp) if (tb + fb_fp) > 0 else 0.0
        r_tile_b = tb / (tb + fb_fn) if (tb + fb_fn) > 0 else 0.0

        per_tile_details.append({
            "tile_name": tile,
            "f1_a": round(f1_tile_a, 6),
            "precision_a": round(p_tile_a, 6),
            "recall_a": round(r_tile_a, 6),
            "tp_a": int(ta), "fp_a": int(fa_val), "fn_a": int(fb_val),
            "f1_b": round(f1_tile_b, 6),
            "precision_b": round(p_tile_b, 6),
            "recall_b": round(r_tile_b, 6),
            "tp_b": int(tb), "fp_b": int(fb_fp), "fn_b": int(fb_fn),
        })

        if f1_tile_a > f1_tile_b:
            wins += 1
        elif f1_tile_a < f1_tile_b:
            losses += 1
        else:
            ties += 1

    # Global micro-average F1 (observed)
    total_tp_a = int(tp_a_arr.sum())
    total_fp_a = int(fp_a_arr.sum())
    total_fn_a = int(fn_a_arr.sum())
    total_tp_b = int(tp_b_arr.sum())
    total_fp_b = int(fp_b_arr.sum())
    total_fn_b = int(fn_b_arr.sum())

    f1_a = _compute_f1(total_tp_a, total_fp_a, total_fn_a)
    f1_b = _compute_f1(total_tp_b, total_fp_b, total_fn_b)
    observed_diff = f1_a - f1_b

    # Tile-swap permutation test using micro-average F1
    # For each permutation, independently swap condition A/B counts
    # for each tile with probability 0.5, then re-aggregate.
    rng = np.random.default_rng(seed)
    null_diffs = np.empty(n_permutations)

    for i in range(n_permutations):
        # Boolean mask: True = swap this tile's counts
        swap = rng.random(n_tiles) < 0.5

        # Swapped counts for condition A
        perm_tp_a = np.where(swap, tp_b_arr, tp_a_arr)
        perm_fp_a = np.where(swap, fp_b_arr, fp_a_arr)
        perm_fn_a = np.where(swap, fn_b_arr, fn_a_arr)
        perm_tp_b = np.where(swap, tp_a_arr, tp_b_arr)
        perm_fp_b = np.where(swap, fp_a_arr, fp_b_arr)
        perm_fn_b = np.where(swap, fn_a_arr, fn_b_arr)

        # Micro-average F1 for each permuted condition
        perm_f1_a = _compute_f1(
            int(perm_tp_a.sum()),
            int(perm_fp_a.sum()),
            int(perm_fn_a.sum()),
        )
        perm_f1_b = _compute_f1(
            int(perm_tp_b.sum()),
            int(perm_fp_b.sum()),
            int(perm_fn_b.sum()),
        )
        null_diffs[i] = perm_f1_a - perm_f1_b

    # Two-sided p-value
    p_value = float(np.mean(np.abs(null_diffs) >= np.abs(observed_diff)))

    # Compute precision and recall from aggregated counts
    p_a = total_tp_a / (total_tp_a + total_fp_a) if (total_tp_a + total_fp_a) > 0 else 0.0
    r_a = total_tp_a / (total_tp_a + total_fn_a) if (total_tp_a + total_fn_a) > 0 else 0.0
    p_b = total_tp_b / (total_tp_b + total_fp_b) if (total_tp_b + total_fp_b) > 0 else 0.0
    r_b = total_tp_b / (total_tp_b + total_fn_b) if (total_tp_b + total_fn_b) > 0 else 0.0

    return {
        "global_a": {
            "f1": round(f1_a, 6),
            "precision": round(p_a, 6),
            "recall": round(r_a, 6),
            "n_detections": len(gdf_a),
            "tp": total_tp_a,
            "fp": total_fp_a,
            "fn": total_fn_a,
        },
        "global_b": {
            "f1": round(f1_b, 6),
            "precision": round(p_b, 6),
            "recall": round(r_b, 6),
            "n_detections": len(gdf_b),
            "tp": total_tp_b,
            "fp": total_fp_b,
            "fn": total_fn_b,
        },
        "permutation_test": {
            "observed_f1_diff": round(observed_diff, 6),
            "p_value": round(p_value, 4),
            "n_permutations": n_permutations,
            "n_tiles": n_tiles,
            "wins_a": wins,
            "losses_a": losses,
            "ties": ties,
            "null_distribution": {
                "mean": round(float(np.mean(null_diffs)), 6),
                "std": round(float(np.std(null_diffs)), 6),
                "percentile_2.5": round(
                    float(np.percentile(null_diffs, 2.5)), 6,
                ),
                "percentile_97.5": round(
                    float(np.percentile(null_diffs, 97.5)), 6,
                ),
            },
        },
        "per_tile": per_tile_details,
    }


# -----------------------------------------------
# MCC tile-classification permutation test
# -----------------------------------------------

def _compute_mcc(tp: int, tn: int, fp: int, fn: int) -> float:
    """Compute Matthews Correlation Coefficient, 0.0 when undefined.

    **Resampling-kernel convention.** Returns 0.0 when the denominator
    is zero (any row/column sum is zero) — the ``sklearn.metrics``
    convention. Inside the permutation null of
    :func:`run_permutation_test_mcc` a degenerate resample must yield
    *some* number for the null distribution to be computable, and 0.0
    (the centre of the MCC scale) is the standard choice. The value
    never leaves the kernel as a published measurement.

    Erratum E81 (2026-08-18) forbids publishing that 0.0 as a *result*:
    an undefined coefficient is not a chance-level one. Anything that
    reports, ranks, or gates on an observed MCC must therefore call
    :func:`compute_mcc_or_none` instead, and render or propagate the
    ``None``.

    Args:
        tp: True positive count.
        tn: True negative count.
        fp: False positive count.
        fn: False negative count.

    Returns:
        MCC in [-1.0, 1.0], or 0.0 when undefined (zero denominator).
    """
    numerator = (tp * tn) - (fp * fn)
    denom_parts = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    if denom_parts <= 0:
        return 0.0
    return float(numerator / np.sqrt(denom_parts))


def compute_mcc_or_none(
    tp: int, tn: int, fp: int, fn: int,
) -> float | None:
    """Compute Matthews Correlation Coefficient, ``None`` when undefined.

    The reporting counterpart of :func:`_compute_mcc`. Use this
    wherever the result is published, ranked, compared, or used to gate
    a run: erratum E81 (2026-08-18) requires an undefined coefficient
    to stay distinguishable from a measured 0.0, which § 4.2 of the
    preregistration reads as "random".

    Args:
        tp: True positive count.
        tn: True negative count.
        fp: False positive count.
        fn: False negative count.

    Returns:
        MCC in [-1.0, 1.0], or ``None`` when the 2 x 2 table is
        degenerate so that sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes.

    Examples:
        >>> compute_mcc_or_none(0, 0, 0, 0) is None
        True
        >>> compute_mcc_or_none(1, 1, 1, 1)
        0.0
    """
    denom_parts = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    if denom_parts <= 0:
        return None
    return float(((tp * tn) - (fp * fn)) / np.sqrt(denom_parts))


def run_permutation_test_mcc(
    gdf_a: gpd.GeoDataFrame,
    gdf_b: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_permutations: int = 10_000,
    seed: int = 42,
) -> dict:
    """Tile-classification paired permutation test for MCC.

    Per-tile classification is one of {TP, TN, FP, FN} (binary
    presence-of-detection vs presence-of-reference). For each tile, the
    classification 4-tuple is independently swapped between conditions
    A and B with probability 0.5; the global MCC is recomputed each
    iteration to build a null distribution of ΔMCC.

    Important — buffer-independence: tile classification depends on
    ``gdf_det['source_tile']`` and ``gdf_ref.intersects(tile_geom)``
    only — there is no spatial buffer in the matching. MCC is
    therefore buffer-invariant in this codebase. The function does
    not take a buffer argument; callers should produce a single tier
    table per stratum (the same MCC tiering, repeated across the 5
    F1-buffer files for symmetry with F1).

    Args:
        gdf_a: Detection GeoDataFrame for condition A (must have
            ``source_tile``).
        gdf_b: Detection GeoDataFrame for condition B (must have
            ``source_tile``).
        gdf_ref: Ground-truth reference GeoDataFrame.
        gdf_bounds: Evaluation tile boundaries (must have
            ``tile_name``).
        n_permutations: Number of permutation iterations.
        seed: Random seed for reproducibility.

    Returns:
        Dict with observed MCC for each condition, ΔMCC, two-sided
        p-value, win/loss/tie counts, and null distribution
        statistics. Schema matches ``run_permutation_test`` (the F1
        sibling) but with ``observed_mcc_diff`` in place of
        ``observed_f1_diff``.
    """
    # Pre-compute per-tile (TP, TN, FP, FN) one-hot encoding for both
    # conditions. Each tile contributes exactly one 1 to one of the
    # four columns and 0 to the others.
    pt_a = compute_per_tile_classification(gdf_a, gdf_ref, gdf_bounds)
    pt_b = compute_per_tile_classification(gdf_b, gdf_ref, gdf_bounds)

    tiles = gdf_bounds["tile_name"].unique()
    n_tiles = len(tiles)

    # Aligned arrays per tile (4 columns × n_tiles)
    pt_a_idx = pt_a.set_index("tile_name") if not pt_a.empty else pt_a
    pt_b_idx = pt_b.set_index("tile_name") if not pt_b.empty else pt_b

    tp_a_arr = np.zeros(n_tiles, dtype=int)
    tn_a_arr = np.zeros(n_tiles, dtype=int)
    fp_a_arr = np.zeros(n_tiles, dtype=int)
    fn_a_arr = np.zeros(n_tiles, dtype=int)
    tp_b_arr = np.zeros(n_tiles, dtype=int)
    tn_b_arr = np.zeros(n_tiles, dtype=int)
    fp_b_arr = np.zeros(n_tiles, dtype=int)
    fn_b_arr = np.zeros(n_tiles, dtype=int)

    wins = losses = ties = 0
    per_tile_details: list[dict] = []
    for i, tile in enumerate(tiles):
        if not pt_a_idx.empty and tile in pt_a_idx.index:
            row = pt_a_idx.loc[tile]
            tp_a_arr[i] = int(row["tp"])
            tn_a_arr[i] = int(row["tn"])
            fp_a_arr[i] = int(row["fp"])
            fn_a_arr[i] = int(row["fn"])
        if not pt_b_idx.empty and tile in pt_b_idx.index:
            row = pt_b_idx.loc[tile]
            tp_b_arr[i] = int(row["tp"])
            tn_b_arr[i] = int(row["tn"])
            fp_b_arr[i] = int(row["fp"])
            fn_b_arr[i] = int(row["fn"])

        # Per-tile win/loss using directional informedness
        # (TP=1, TN=1 = correct; FP=1, FN=1 = wrong).
        a_correct = bool(tp_a_arr[i] or tn_a_arr[i])
        b_correct = bool(tp_b_arr[i] or tn_b_arr[i])
        if a_correct and not b_correct:
            wins += 1
        elif b_correct and not a_correct:
            losses += 1
        else:
            ties += 1
        per_tile_details.append({
            "tile_name": tile,
            "class_a": (
                "TP" if tp_a_arr[i] else "TN" if tn_a_arr[i]
                else "FP" if fp_a_arr[i] else "FN"
            ),
            "class_b": (
                "TP" if tp_b_arr[i] else "TN" if tn_b_arr[i]
                else "FP" if fp_b_arr[i] else "FN"
            ),
        })

    # Observed aggregate confusion + MCC
    tp_a, tn_a = int(tp_a_arr.sum()), int(tn_a_arr.sum())
    fp_a, fn_a = int(fp_a_arr.sum()), int(fn_a_arr.sum())
    tp_b, tn_b = int(tp_b_arr.sum()), int(tn_b_arr.sum())
    fp_b, fn_b = int(fp_b_arr.sum()), int(fn_b_arr.sum())
    mcc_a = _compute_mcc(tp_a, tn_a, fp_a, fn_a)
    mcc_b = _compute_mcc(tp_b, tn_b, fp_b, fn_b)
    observed_diff = mcc_a - mcc_b

    # Tile-swap permutation null. For each iteration, independently
    # swap each tile's full (TP, TN, FP, FN) 4-tuple between A and B
    # with probability 0.5, then recompute aggregate MCC.
    rng = np.random.default_rng(seed)
    null_diffs = np.empty(n_permutations)
    for i in range(n_permutations):
        swap = rng.random(n_tiles) < 0.5
        perm_tp_a = np.where(swap, tp_b_arr, tp_a_arr)
        perm_tn_a = np.where(swap, tn_b_arr, tn_a_arr)
        perm_fp_a = np.where(swap, fp_b_arr, fp_a_arr)
        perm_fn_a = np.where(swap, fn_b_arr, fn_a_arr)
        perm_tp_b = np.where(swap, tp_a_arr, tp_b_arr)
        perm_tn_b = np.where(swap, tn_a_arr, tn_b_arr)
        perm_fp_b = np.where(swap, fp_a_arr, fp_b_arr)
        perm_fn_b = np.where(swap, fn_a_arr, fn_b_arr)

        perm_mcc_a = _compute_mcc(
            int(perm_tp_a.sum()), int(perm_tn_a.sum()),
            int(perm_fp_a.sum()), int(perm_fn_a.sum()),
        )
        perm_mcc_b = _compute_mcc(
            int(perm_tp_b.sum()), int(perm_tn_b.sum()),
            int(perm_fp_b.sum()), int(perm_fn_b.sum()),
        )
        null_diffs[i] = perm_mcc_a - perm_mcc_b

    p_value = float(np.mean(np.abs(null_diffs) >= np.abs(observed_diff)))

    return {
        "global_a": {
            "mcc": round(mcc_a, 6),
            "n_detections": len(gdf_a),
            "tp": tp_a, "tn": tn_a, "fp": fp_a, "fn": fn_a,
        },
        "global_b": {
            "mcc": round(mcc_b, 6),
            "n_detections": len(gdf_b),
            "tp": tp_b, "tn": tn_b, "fp": fp_b, "fn": fn_b,
        },
        "permutation_test": {
            "observed_mcc_diff": round(observed_diff, 6),
            "p_value": round(p_value, 4),
            "n_permutations": n_permutations,
            "n_tiles": n_tiles,
            "wins_a": wins,
            "losses_a": losses,
            "ties": ties,
            "null_distribution": {
                "mean": round(float(np.mean(null_diffs)), 6),
                "std": round(float(np.std(null_diffs)), 6),
                "percentile_2.5": round(
                    float(np.percentile(null_diffs, 2.5)), 6,
                ),
                "percentile_97.5": round(
                    float(np.percentile(null_diffs, 97.5)), 6,
                ),
            },
        },
        "per_tile": per_tile_details,
    }


# -----------------------------------------------
# Source metadata builders — for output provenance
# -----------------------------------------------

def _pv_source_metadata(args: argparse.Namespace, suffix: str) -> dict:
    """Build source metadata dict for PV mode."""
    return {
        "mode": "pv",
        "probabilities": str(
            getattr(args, f"probabilities_{suffix}").resolve()
        ),
        "manifest": str(getattr(args, f"manifest_{suffix}").resolve()),
        "threshold": getattr(args, f"threshold_{suffix}"),
    }


def _consensus_source_metadata(
    args: argparse.Namespace, suffix: str,
) -> dict:
    """Build source metadata dict for consensus mode."""
    config_str = getattr(args, f"config_{suffix}")
    parts = config_str.split(",")
    return {
        "mode": "consensus",
        "study_dir": str(getattr(args, f"study_dir_{suffix}").resolve()),
        "temperature": parts[0].strip(),
        "pool_size": int(parts[1].strip()),
        "threshold": int(parts[2].strip()),
    }


def _geojson_source_metadata(
    args: argparse.Namespace, suffix: str,
) -> dict:
    """Build source metadata dict for GeoJSON mode."""
    return {
        "mode": "geojson",
        "geojson": str(getattr(args, f"geojson_{suffix}").resolve()),
    }


# -----------------------------------------------
# Main
# -----------------------------------------------

def main() -> None:
    """Run generalised paired permutation test."""
    parser = argparse.ArgumentParser(
        description=(
            "Paired permutation test comparing two detection conditions. "
            "Supports PV verifier results, consensus voting, and raw "
            "GeoJSON inputs."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--mode", required=True,
        choices=["pv", "consensus", "geojson"],
        help="Input data mode",
    )

    # --- Common arguments ---
    parser.add_argument(
        "--label-a", type=str, default="Condition A",
        help="Human-readable label for condition A",
    )
    parser.add_argument(
        "--label-b", type=str, default="Condition B",
        help="Human-readable label for condition B",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for results JSON",
    )
    parser.add_argument(
        "--bounds", type=Path, default=_BOUNDS_PATH,
        help=f"Evaluation bounds GeoJSON (default: {_BOUNDS_PATH.name})",
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=_REF_PATH,
        help=f"Ground truth GeoJSON (default: {_REF_PATH.name})",
    )
    parser.add_argument(
        "--buffer-metres", type=int, default=20,
        help=(
            "Spatial matching tolerance in metres for F1 evaluation "
            "(default: 20)"
        ),
    )
    parser.add_argument(
        "--n-permutations", type=int, default=10_000,
        help="Number of permutation iterations (default: 10,000)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress console output",
    )

    # --- PV mode arguments ---
    parser.add_argument("--probabilities-a", type=Path)
    parser.add_argument("--probabilities-b", type=Path)
    parser.add_argument("--manifest-a", type=Path)
    parser.add_argument("--manifest-b", type=Path)
    parser.add_argument("--threshold-a", type=float)
    parser.add_argument("--threshold-b", type=float)

    # --- Consensus mode arguments ---
    parser.add_argument("--study-dir-a", type=Path)
    parser.add_argument("--study-dir-b", type=Path)
    parser.add_argument(
        "--config-a", type=str,
        help="Consensus config: 'temperature,pool_size,threshold'",
    )
    parser.add_argument(
        "--config-b", type=str,
        help="Consensus config: 'temperature,pool_size,threshold'",
    )

    # --- GeoJSON mode arguments ---
    parser.add_argument("--geojson-a", type=Path)
    parser.add_argument("--geojson-b", type=Path)

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Validate mode-specific arguments
    if args.mode == "pv":
        for attr in [
            "probabilities_a", "probabilities_b",
            "manifest_a", "manifest_b",
            "threshold_a", "threshold_b",
        ]:
            if getattr(args, attr) is None:
                parser.error(
                    f"--{attr.replace('_', '-')} is required in PV mode"
                )
    elif args.mode == "consensus":
        for attr in [
            "study_dir_a", "study_dir_b", "config_a", "config_b",
        ]:
            if getattr(args, attr) is None:
                parser.error(
                    f"--{attr.replace('_', '-')} is required in "
                    f"consensus mode"
                )
    elif args.mode == "geojson":
        for attr in ["geojson_a", "geojson_b"]:
            if getattr(args, attr) is None:
                parser.error(
                    f"--{attr.replace('_', '-')} is required in "
                    f"GeoJSON mode"
                )

    # Load reference data (enforce CRS for consistent spatial matching)
    logger.info("Loading ground truth: %s", args.ground_truth)
    gdf_ref = gpd.read_file(args.ground_truth).to_crs(_TARGET_CRS)
    logger.info("Loading bounds: %s", args.bounds)
    gdf_bounds = gpd.read_file(args.bounds).to_crs(_TARGET_CRS)
    if "tile_name" not in gdf_bounds.columns:
        parser.error(
            f"Bounds GeoJSON must have a 'tile_name' column, "
            f"got: {list(gdf_bounds.columns)}"
        )
    logger.info(
        "Reference: %d mounds, %d tiles",
        len(gdf_ref), len(gdf_bounds),
    )

    # Load detections for each condition
    if args.mode == "pv":
        gdf_a = load_pv_detections(
            args.probabilities_a, args.manifest_a, args.threshold_a,
        )
        gdf_b = load_pv_detections(
            args.probabilities_b, args.manifest_b, args.threshold_b,
        )
        source_a = _pv_source_metadata(args, "a")
        source_b = _pv_source_metadata(args, "b")
    elif args.mode == "consensus":
        gdf_a = load_consensus_detections(
            args.study_dir_a, args.config_a, gdf_bounds,
        )
        gdf_b = load_consensus_detections(
            args.study_dir_b, args.config_b, gdf_bounds,
        )
        source_a = _consensus_source_metadata(args, "a")
        source_b = _consensus_source_metadata(args, "b")
    else:  # geojson
        gdf_a = load_geojson_detections(args.geojson_a)
        gdf_b = load_geojson_detections(args.geojson_b)
        gdf_a = assign_source_tiles(gdf_a, gdf_bounds)
        gdf_b = assign_source_tiles(gdf_b, gdf_bounds)
        source_a = _geojson_source_metadata(args, "a")
        source_b = _geojson_source_metadata(args, "b")

    # Warn if either condition produced zero detections
    if len(gdf_a) == 0:
        logger.warning(
            "Condition A (%s) has 0 detections — check inputs",
            args.label_a,
        )
    if len(gdf_b) == 0:
        logger.warning(
            "Condition B (%s) has 0 detections — check inputs",
            args.label_b,
        )

    # Run permutation test
    logger.info(
        "Running permutation test: %s vs %s (%d permutations)",
        args.label_a, args.label_b, args.n_permutations,
    )
    result = run_permutation_test(
        gdf_a, gdf_b, gdf_ref, gdf_bounds,
        buffer_metres=args.buffer_metres,
        n_permutations=args.n_permutations,
        seed=args.seed,
    )

    # Build output
    output = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "script": "pairwise_permutation_test.py",
            "version": __version__,
            "mode": args.mode,
            "buffer_metres": args.buffer_metres,
            "n_permutations": args.n_permutations,
            "seed": args.seed,
        },
        "condition_a": {
            "label": args.label_a,
            "source": source_a,
            **result["global_a"],
        },
        "condition_b": {
            "label": args.label_b,
            "source": source_b,
            **result["global_b"],
        },
        "permutation_test": result["permutation_test"],
        "per_tile": result["per_tile"],
    }

    # Write output
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / "pairwise_permutation_result.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logger.info("Results written: %s", out_path)

    # Console summary
    test = result["permutation_test"]
    sig = (
        "***" if test["p_value"] < 0.001
        else "**" if test["p_value"] < 0.01
        else "*" if test["p_value"] < 0.05
        else "ns"
    )
    print(
        f"\n{args.label_a} vs {args.label_b}\n"
        f"  A: F1={result['global_a']['f1']:.4f} "
        f"(P={result['global_a']['precision']:.3f}, "
        f"R={result['global_a']['recall']:.3f}, "
        f"n={result['global_a']['n_detections']})\n"
        f"  B: F1={result['global_b']['f1']:.4f} "
        f"(P={result['global_b']['precision']:.3f}, "
        f"R={result['global_b']['recall']:.3f}, "
        f"n={result['global_b']['n_detections']})\n"
        f"  ΔF1={test['observed_f1_diff']:+.4f}, "
        f"p={test['p_value']:.4f} {sig}\n"
        f"  Wins/Losses/Ties: {test['wins_a']}/{test['losses_a']}"
        f"/{test['ties']}\n"
        f"  95% null CI: [{test['null_distribution']['percentile_2.5']:.4f}"
        f", {test['null_distribution']['percentile_97.5']:.4f}]"
    )


if __name__ == "__main__":
    main()
