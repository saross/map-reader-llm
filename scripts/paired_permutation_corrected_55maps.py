#!/usr/bin/env python3
"""Paired permutation test for 55-map corrected detection sets.

Pairs two condition-specific detection runs at multiple buffer radii against
each side's **own** extended ground truth (Approach B — extended-GT-at-R
Hungarian matching, identical to ``compute_corrected_f1_multi_buffer.py``).

This is the corrected analogue of ``pairwise_permutation_test.py``: the
verified detection sets (``verified_detections.geojson``) are unchanged, but
the per-side reference is the **extended GT at R** for that side, built by
adding reviewer-promoted phantom mounds (``human_label == 'mound'``) within
R from that side's review CSV(s).

Each side's per-tile TP / FP / FN is therefore evaluated against the extended
GT that the side's own corrected-F1 report was computed against — ensuring
the paired test's per-side global F1 matches the published corrected-F1
numbers exactly.

Test statistic: aggregate (micro-average) F1 difference. Per-tile TP / FP /
FN counts are independently swapped between conditions A and B with
probability 0.5 in each permutation; aggregate F1 is then re-computed and
the null distribution of ΔF1 built. Two-sided p-value is the proportion of
permutations with ``|ΔF1| >= |observed|``.

Usage:

    python scripts/paired_permutation_corrected_55maps.py \\
        --label-a t0.7 \\
        --detections-a outputs/55maps-text-high-generalisation/verified/verified_detections.geojson \\
        --review-yesterday-a /tmp/empty-review-yesterday.csv \\
        --review-today-a results/55maps-text-high-generalisation/human-review-multi-buffer.csv \\
        --label-b t0.3 \\
        --detections-b outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson \\
        --review-yesterday-b /tmp/empty-review-yesterday.csv \\
        --review-today-b results/55maps-text-high-t0.3-generalisation/human-review-multi-buffer.csv \\
        --output-dir results/55maps-pairwise-permutation-v2/paired-t0.7-vs-t0.3 \\
        --buffers 20 25 30 35 40 45 50 75 100 125

Outputs:
    For each buffer R, writes ``permutation-R{R}m.json`` with full per-tile
    detail and aggregate test statistics. Also writes a ``summary.json``
    with the buffer × test-stat table and Benjamini-Hochberg FDR-corrected
    q-values within the pair (10 buffers → q* = 0.05).

Author: Shawn Ross & Claude (Anthropic)
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

# Ensure scripts/ is on sys.path before sibling imports
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from compute_corrected_f1_multi_buffer import (  # noqa: E402
    SENTINEL_BUFFER_EXCLUDED,
    build_extended_gt,
    build_phantom_gdf,
)
from lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
)

__version__ = "1.0.0"

logger = logging.getLogger(__name__)

DEFAULT_CRS = "EPSG:32635"
DEFAULT_BUFFERS = (20, 25, 30, 35, 40, 45, 50, 75, 100, 125)


# -----------------------------------------------
# Bootstrap CI for paired ΔF1 (tile-level resampling)
# -----------------------------------------------

def bootstrap_paired_delta_f1_ci(
    tp_a: np.ndarray,
    fp_a: np.ndarray,
    fn_a: np.ndarray,
    tp_b: np.ndarray,
    fp_b: np.ndarray,
    fn_b: np.ndarray,
    n_iterations: int = 10_000,
    seed: int = 42,
) -> tuple[float, float]:
    """Tile-level paired bootstrap 95 % CI for ΔF1 = F1_A − F1_B.

    Same tiles are resampled for both conditions on each iteration so the
    CI reflects pairing — i.e. this is a paired bootstrap that controls for
    between-tile variance.

    Args:
        tp_a, fp_a, fn_a: Per-tile counts for condition A (aligned arrays).
        tp_b, fp_b, fn_b: Per-tile counts for condition B (aligned arrays).
        n_iterations: Number of bootstrap iterations (default 10,000).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (lower 2.5 percentile, upper 97.5 percentile) for ΔF1.
    """
    n_tiles = len(tp_a)
    rng = np.random.default_rng(seed)

    delta_samples = np.empty(n_iterations)
    for i in range(n_iterations):
        sample_idx = rng.integers(0, n_tiles, size=n_tiles)
        mult = np.bincount(sample_idx, minlength=n_tiles)

        # Aggregate counts for this bootstrap sample
        tp_a_sum = int(mult @ tp_a)
        fp_a_sum = int(mult @ fp_a)
        fn_a_sum = int(mult @ fn_a)
        tp_b_sum = int(mult @ tp_b)
        fp_b_sum = int(mult @ fp_b)
        fn_b_sum = int(mult @ fn_b)

        f1_a = _f1(tp_a_sum, fp_a_sum, fn_a_sum)
        f1_b = _f1(tp_b_sum, fp_b_sum, fn_b_sum)
        delta_samples[i] = f1_a - f1_b

    return (
        float(np.percentile(delta_samples, 2.5)),
        float(np.percentile(delta_samples, 97.5)),
    )


# -----------------------------------------------
# Core helpers
# -----------------------------------------------

def _f1(tp: int, fp: int, fn: int) -> float:
    """Compute F1 from aggregate counts (zero-safe)."""
    if tp == 0:
        return 0.0
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def git_commit_hash() -> str:
    """Return current HEAD SHA, or ``unknown`` on failure."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
        ).decode("ascii").strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def load_reviews(review_yesterday: Path, review_today: Path) -> tuple[
    pd.DataFrame, pd.DataFrame, int,
]:
    """Load review CSVs and count today's excluded sentinels.

    Args:
        review_yesterday: Path to yesterday's single-buffer review CSV.
            Pass an empty CSV (with the same columns) if no yesterday data.
        review_today: Path to today's multi-buffer review CSV.

    Returns:
        Tuple of (yesterday DataFrame, today DataFrame, excluded sentinel count).
    """
    review_y = pd.read_csv(review_yesterday)
    review_t = pd.read_csv(review_today)

    excluded = int(
        (
            (review_t["human_label"] == "mound")
            & (review_t["buffer_metres"] == SENTINEL_BUFFER_EXCLUDED)
        ).sum()
    )
    return review_y, review_t, excluded


def get_per_tile_counts(
    gdf_det: gpd.GeoDataFrame,
    gdf_ext_gt: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute aligned per-tile (TP, FP, FN) arrays.

    Wraps ``lib_advanced_metrics.compute_per_tile_tp_fp_fn`` and re-indexes
    the result against the canonical tile ordering from ``gdf_bounds`` so
    permutation indexing is identical between conditions.

    Args:
        gdf_det: Detection GeoDataFrame with ``source_tile`` column.
        gdf_ext_gt: Extended GT GeoDataFrame with ``source_map`` column.
        gdf_bounds: Tile bounds with ``tile_name`` column.
        buffer_metres: Hungarian matching tolerance.

    Returns:
        Tuple of (tp_arr, fp_arr, fn_arr), each int64 numpy arrays of
        length ``len(gdf_bounds['tile_name'].unique())``.
    """
    pt = compute_per_tile_tp_fp_fn(
        gdf_det, gdf_ext_gt, gdf_bounds, buffer_metres=buffer_metres,
    )
    tiles = gdf_bounds["tile_name"].unique()
    indexed = pt.set_index("tile_name")
    tp_arr = indexed.reindex(tiles)["tp"].fillna(0).to_numpy(dtype=np.int64)
    fp_arr = indexed.reindex(tiles)["fp"].fillna(0).to_numpy(dtype=np.int64)
    fn_arr = indexed.reindex(tiles)["fn"].fillna(0).to_numpy(dtype=np.int64)
    return tp_arr, fp_arr, fn_arr


# -----------------------------------------------
# Permutation test (vectorised, micro-F1)
# -----------------------------------------------

def paired_permutation_microf1(
    tp_a: np.ndarray, fp_a: np.ndarray, fn_a: np.ndarray,
    tp_b: np.ndarray, fp_b: np.ndarray, fn_b: np.ndarray,
    n_permutations: int = 10_000,
    seed: int = 42,
) -> dict:
    """Tile-swap paired permutation test on micro-average F1.

    For each permutation iteration, each tile's (TP, FP, FN) triple is
    independently swapped between conditions A and B with probability 0.5.
    The aggregate micro-F1 is then recomputed, and the null distribution
    of ΔF1 is built. Two-sided p-value is computed as the proportion of
    permutations with ``|ΔF1| >= |observed|``.

    Matches the algorithm in ``pairwise_permutation_test.run_permutation_test``
    so corrected and uncorrected results are directly comparable.

    Args:
        tp_a, fp_a, fn_a: Per-tile counts for condition A.
        tp_b, fp_b, fn_b: Per-tile counts for condition B.
        n_permutations: Number of permutation iterations (default 10,000).
        seed: Random seed for reproducibility.

    Returns:
        Dict with observed_f1_diff, p_value, wins/losses/ties, null
        distribution summary, and per-condition global F1 / P / R / counts.
    """
    n_tiles = len(tp_a)

    # Per-tile F1 for win/loss/tie counts
    wins = losses = ties = 0
    for i in range(n_tiles):
        f1a = _f1(int(tp_a[i]), int(fp_a[i]), int(fn_a[i]))
        f1b = _f1(int(tp_b[i]), int(fp_b[i]), int(fn_b[i]))
        if f1a > f1b:
            wins += 1
        elif f1a < f1b:
            losses += 1
        else:
            ties += 1

    # Aggregate (observed) micro-F1
    total_tp_a = int(tp_a.sum())
    total_fp_a = int(fp_a.sum())
    total_fn_a = int(fn_a.sum())
    total_tp_b = int(tp_b.sum())
    total_fp_b = int(fp_b.sum())
    total_fn_b = int(fn_b.sum())

    f1_a = _f1(total_tp_a, total_fp_a, total_fn_a)
    f1_b = _f1(total_tp_b, total_fp_b, total_fn_b)
    p_a = (
        total_tp_a / (total_tp_a + total_fp_a)
        if (total_tp_a + total_fp_a) > 0 else 0.0
    )
    r_a = (
        total_tp_a / (total_tp_a + total_fn_a)
        if (total_tp_a + total_fn_a) > 0 else 0.0
    )
    p_b = (
        total_tp_b / (total_tp_b + total_fp_b)
        if (total_tp_b + total_fp_b) > 0 else 0.0
    )
    r_b = (
        total_tp_b / (total_tp_b + total_fn_b)
        if (total_tp_b + total_fn_b) > 0 else 0.0
    )
    observed_diff = f1_a - f1_b

    # Permutation null
    rng = np.random.default_rng(seed)
    null_diffs = np.empty(n_permutations)
    for i in range(n_permutations):
        swap = rng.random(n_tiles) < 0.5
        perm_tp_a = np.where(swap, tp_b, tp_a)
        perm_fp_a = np.where(swap, fp_b, fp_a)
        perm_fn_a = np.where(swap, fn_b, fn_a)
        perm_tp_b = np.where(swap, tp_a, tp_b)
        perm_fp_b = np.where(swap, fp_a, fp_b)
        perm_fn_b = np.where(swap, fn_a, fn_b)

        perm_f1_a = _f1(
            int(perm_tp_a.sum()), int(perm_fp_a.sum()), int(perm_fn_a.sum()),
        )
        perm_f1_b = _f1(
            int(perm_tp_b.sum()), int(perm_fp_b.sum()), int(perm_fn_b.sum()),
        )
        null_diffs[i] = perm_f1_a - perm_f1_b

    p_value = float(np.mean(np.abs(null_diffs) >= np.abs(observed_diff)))

    return {
        "global_a": {
            "f1": round(f1_a, 6),
            "precision": round(p_a, 6),
            "recall": round(r_a, 6),
            "tp": total_tp_a, "fp": total_fp_a, "fn": total_fn_a,
        },
        "global_b": {
            "f1": round(f1_b, 6),
            "precision": round(p_b, 6),
            "recall": round(r_b, 6),
            "tp": total_tp_b, "fp": total_fp_b, "fn": total_fn_b,
        },
        "permutation_test": {
            "observed_f1_diff": round(observed_diff, 6),
            "p_value": round(p_value, 6),
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
    }


# -----------------------------------------------
# Per-buffer driver
# -----------------------------------------------

def run_buffer(
    *,
    buffer_r: int,
    gdf_det_a: gpd.GeoDataFrame,
    gdf_det_b: gpd.GeoDataFrame,
    gdf_student: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    review_y_a: pd.DataFrame,
    review_t_a: pd.DataFrame,
    review_y_b: pd.DataFrame,
    review_t_b: pd.DataFrame,
    n_permutations: int,
    n_bootstrap: int,
    seed: int,
    label_a: str,
    label_b: str,
) -> dict:
    """Run the paired permutation test for a single buffer R.

    Builds extended GT separately for A and B (each side scored against its
    own reviewer-promoted phantoms within R), computes per-tile TP / FP /
    FN, runs the test, and assembles the buffer-level result dict.

    Args:
        buffer_r: Buffer radius in metres.
        gdf_det_a, gdf_det_b: Detection GeoDataFrames for A, B.
        gdf_student: Original student ground truth.
        gdf_bounds: Tile bounds.
        review_y_a, review_t_a: Yesterday/today review CSVs for A.
        review_y_b, review_t_b: Yesterday/today review CSVs for B.
        n_permutations: Permutation count.
        n_bootstrap: Bootstrap iterations for paired ΔF1 95 % CI.
        seed: Random seed (used for both permutation and bootstrap).
        label_a, label_b: Human-readable condition labels.

    Returns:
        Per-buffer result dict suitable for JSON serialisation.
    """
    logger.info("--- R = %d m ---", buffer_r)

    # Build extended GT for each side
    phantoms_a = build_phantom_gdf(
        review_y_a, review_t_a, buffer_r, crs=DEFAULT_CRS,
    )
    phantoms_b = build_phantom_gdf(
        review_y_b, review_t_b, buffer_r, crs=DEFAULT_CRS,
    )
    ext_gt_a = build_extended_gt(gdf_student, phantoms_a)
    ext_gt_b = build_extended_gt(gdf_student, phantoms_b)
    logger.info(
        "  phantoms: A=%d B=%d  ext_GT: A=%d B=%d",
        len(phantoms_a), len(phantoms_b),
        len(ext_gt_a), len(ext_gt_b),
    )

    # Per-tile TP / FP / FN against each side's own extended GT
    tp_a, fp_a, fn_a = get_per_tile_counts(
        gdf_det_a, ext_gt_a, gdf_bounds, buffer_r,
    )
    tp_b, fp_b, fn_b = get_per_tile_counts(
        gdf_det_b, ext_gt_b, gdf_bounds, buffer_r,
    )

    # Run permutation test
    result = paired_permutation_microf1(
        tp_a, fp_a, fn_a, tp_b, fp_b, fn_b,
        n_permutations=n_permutations, seed=seed,
    )

    # Tile-level paired bootstrap CI for ΔF1
    delta_lo, delta_hi = bootstrap_paired_delta_f1_ci(
        tp_a, fp_a, fn_a, tp_b, fp_b, fn_b,
        n_iterations=n_bootstrap, seed=seed,
    )

    test = result["permutation_test"]
    sig = (
        "***" if test["p_value"] < 0.001
        else "**" if test["p_value"] < 0.01
        else "*" if test["p_value"] < 0.05
        else "ns"
    )
    logger.info(
        "  F1: %s=%.4f vs %s=%.4f  ΔF1=%+.4f [%+.4f, %+.4f]  p=%.4f %s  W/L/T=%d/%d/%d",
        label_a, result["global_a"]["f1"],
        label_b, result["global_b"]["f1"],
        test["observed_f1_diff"], delta_lo, delta_hi,
        test["p_value"], sig,
        test["wins_a"], test["losses_a"], test["ties"],
    )

    # Augment buffer-level dict with extended-GT meta and ΔF1 CI
    return {
        "buffer_metres": buffer_r,
        "n_phantoms_a": len(phantoms_a),
        "n_phantoms_b": len(phantoms_b),
        "n_ref_extended_a": len(ext_gt_a),
        "n_ref_extended_b": len(ext_gt_b),
        "delta_f1_ci": {
            "lower": round(delta_lo, 6),
            "upper": round(delta_hi, 6),
            "n_bootstrap": n_bootstrap,
        },
        **result,
    }


# -----------------------------------------------
# BH-FDR correction (within pair)
# -----------------------------------------------

def bh_fdr(pvals: list[float], q: float = 0.05) -> list[dict]:
    """Apply Benjamini-Hochberg FDR correction.

    Args:
        pvals: List of raw two-sided p-values.
        q: False discovery rate (default 0.05).

    Returns:
        List of dicts ``{rank, p_raw, p_bh, significant_at_q}`` in the
        original input order.
    """
    n = len(pvals)
    indexed = sorted(enumerate(pvals), key=lambda kv: kv[1])
    bh_thresh = [(k + 1) / n * q for k in range(n)]

    # Adjusted p-values: q_i = min over j >= i of n/j * p_(j)
    sorted_p = [kv[1] for kv in indexed]
    adj = [0.0] * n
    running_min = 1.0
    for j in range(n - 1, -1, -1):
        candidate = sorted_p[j] * n / (j + 1)
        running_min = min(running_min, candidate)
        adj[j] = min(running_min, 1.0)

    # Determine which are significant at q (largest k such that p_(k) <= k/n*q)
    significant_indices: set[int] = set()
    for k in range(n - 1, -1, -1):
        if sorted_p[k] <= bh_thresh[k]:
            for j in range(k + 1):
                significant_indices.add(indexed[j][0])
            break

    # Re-order to original input order
    out = [None] * n
    for sorted_rank, (orig_idx, _) in enumerate(indexed):
        out[orig_idx] = {
            "rank": sorted_rank + 1,
            "p_raw": pvals[orig_idx],
            "p_bh": round(adj[sorted_rank], 6),
            "significant_at_q": orig_idx in significant_indices,
        }
    return out  # type: ignore[return-value]


# -----------------------------------------------
# Main driver
# -----------------------------------------------

def run(
    *,
    label_a: str,
    detections_a: Path,
    review_yesterday_a: Path,
    review_today_a: Path,
    label_b: str,
    detections_b: Path,
    review_yesterday_b: Path,
    review_today_b: Path,
    student_gt: Path,
    bounds: Path,
    output_dir: Path,
    buffers: tuple[int, ...],
    n_permutations: int,
    n_bootstrap: int,
    seed: int,
    fdr_q: float,
) -> None:
    """End-to-end driver: load inputs, sweep buffers, write outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading detections, student GT, bounds...")
    gdf_det_a = gpd.read_file(detections_a)
    gdf_det_b = gpd.read_file(detections_b)
    gdf_student = gpd.read_file(student_gt)
    gdf_bounds = gpd.read_file(bounds)

    # Enforce CRS — match compute_corrected_f1_multi_buffer.run() conventions
    for gdf, name in (
        (gdf_det_a, f"detections [{label_a}]"),
        (gdf_det_b, f"detections [{label_b}]"),
        (gdf_student, "student_gt"),
        (gdf_bounds, "bounds"),
    ):
        if gdf.crs is None:
            logger.warning("%s had no CRS; assuming %s", name, DEFAULT_CRS)
            gdf.set_crs(DEFAULT_CRS, inplace=True)
        elif str(gdf.crs) != DEFAULT_CRS:
            logger.info("Reprojecting %s to %s", name, DEFAULT_CRS)
            gdf.to_crs(DEFAULT_CRS, inplace=True)

    logger.info(
        "  detections: A=%d B=%d  student GT=%d  tiles=%d",
        len(gdf_det_a), len(gdf_det_b),
        len(gdf_student), len(gdf_bounds),
    )

    review_y_a, review_t_a, excluded_a = load_reviews(
        review_yesterday_a, review_today_a,
    )
    review_y_b, review_t_b, excluded_b = load_reviews(
        review_yesterday_b, review_today_b,
    )
    logger.info(
        "  review A: yesterday=%d today=%d sentinels=%d",
        len(review_y_a), len(review_t_a), excluded_a,
    )
    logger.info(
        "  review B: yesterday=%d today=%d sentinels=%d",
        len(review_y_b), len(review_t_b), excluded_b,
    )

    # Sweep buffers
    buffer_results: list[dict] = []
    for r in buffers:
        result = run_buffer(
            buffer_r=r,
            gdf_det_a=gdf_det_a, gdf_det_b=gdf_det_b,
            gdf_student=gdf_student, gdf_bounds=gdf_bounds,
            review_y_a=review_y_a, review_t_a=review_t_a,
            review_y_b=review_y_b, review_t_b=review_t_b,
            n_permutations=n_permutations,
            n_bootstrap=n_bootstrap,
            seed=seed,
            label_a=label_a, label_b=label_b,
        )
        buffer_results.append(result)

        # Write per-buffer JSON
        per_buffer_payload = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "script": "paired_permutation_corrected_55maps.py",
                "version": __version__,
                "git_commit": git_commit_hash(),
                "buffer_metres": r,
                "n_permutations": n_permutations,
                "n_bootstrap": n_bootstrap,
                "seed": seed,
                "methodology": (
                    "Approach B — extended-GT-at-R Hungarian matching, "
                    "tile-swap paired permutation test on micro-average F1"
                ),
            },
            "condition_a": {
                "label": label_a,
                "detections": str(detections_a),
                "review_yesterday": str(review_yesterday_a),
                "review_today": str(review_today_a),
                "n_detections": len(gdf_det_a),
            },
            "condition_b": {
                "label": label_b,
                "detections": str(detections_b),
                "review_yesterday": str(review_yesterday_b),
                "review_today": str(review_today_b),
                "n_detections": len(gdf_det_b),
            },
            **result,
        }
        out_path = output_dir / f"permutation-R{r}m.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(per_buffer_payload, f, indent=2)

    # Build summary across buffers with BH-FDR within this pair
    pvals = [br["permutation_test"]["p_value"] for br in buffer_results]
    bh = bh_fdr(pvals, q=fdr_q)

    summary_rows = []
    for br, bh_row in zip(buffer_results, bh, strict=True):
        summary_rows.append({
            "buffer_metres": br["buffer_metres"],
            "f1_a": br["global_a"]["f1"],
            "f1_b": br["global_b"]["f1"],
            "delta_f1": br["permutation_test"]["observed_f1_diff"],
            "delta_f1_ci_lower": br["delta_f1_ci"]["lower"],
            "delta_f1_ci_upper": br["delta_f1_ci"]["upper"],
            "p_raw": br["permutation_test"]["p_value"],
            "p_bh": bh_row["p_bh"],
            "significant_at_q": bh_row["significant_at_q"],
            "wins_a": br["permutation_test"]["wins_a"],
            "losses_a": br["permutation_test"]["losses_a"],
            "ties": br["permutation_test"]["ties"],
            "n_phantoms_a": br["n_phantoms_a"],
            "n_phantoms_b": br["n_phantoms_b"],
        })

    summary_payload = {
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit_hash(),
        "methodology": (
            "Approach B — extended-GT-at-R Hungarian matching, "
            "tile-swap paired permutation test on micro-average F1; "
            f"Benjamini-Hochberg FDR correction within pair (q={fdr_q})"
        ),
        "n_permutations": n_permutations,
        "n_bootstrap": n_bootstrap,
        "seed": seed,
        "fdr_q": fdr_q,
        "condition_a": {
            "label": label_a,
            "detections": str(detections_a),
        },
        "condition_b": {
            "label": label_b,
            "detections": str(detections_b),
        },
        "buffers": list(buffers),
        "per_buffer": summary_rows,
    }
    summary_path = output_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)
    logger.info("Wrote %s", summary_path)


# -----------------------------------------------
# CLI
# -----------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )
    p.add_argument("--label-a", required=True, help="Condition A label")
    p.add_argument("--detections-a", type=Path, required=True)
    p.add_argument("--review-yesterday-a", type=Path, required=True)
    p.add_argument("--review-today-a", type=Path, required=True)
    p.add_argument("--label-b", required=True, help="Condition B label")
    p.add_argument("--detections-b", type=Path, required=True)
    p.add_argument("--review-yesterday-b", type=Path, required=True)
    p.add_argument("--review-today-b", type=Path, required=True)
    p.add_argument(
        "--student-gt", type=Path,
        default=Path(
            "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
        ),
    )
    p.add_argument(
        "--bounds", type=Path,
        default=Path(
            "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
        ),
    )
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument(
        "--buffers", nargs="+", type=int, default=list(DEFAULT_BUFFERS),
        help=f"Buffer radii in metres (default: {list(DEFAULT_BUFFERS)})",
    )
    p.add_argument("--n-permutations", type=int, default=10_000)
    p.add_argument(
        "--n-bootstrap", type=int, default=10_000,
        help=(
            "Bootstrap iterations for tile-level paired delta-F1 95 %% CI "
            "(default: 10,000)."
        ),
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--fdr-q", type=float, default=0.05,
        help="Benjamini-Hochberg FDR rate within pair (default: 0.05).",
    )
    return p.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    run(
        label_a=args.label_a,
        detections_a=args.detections_a,
        review_yesterday_a=args.review_yesterday_a,
        review_today_a=args.review_today_a,
        label_b=args.label_b,
        detections_b=args.detections_b,
        review_yesterday_b=args.review_yesterday_b,
        review_today_b=args.review_today_b,
        student_gt=args.student_gt,
        bounds=args.bounds,
        output_dir=args.output_dir,
        buffers=tuple(args.buffers),
        n_permutations=args.n_permutations,
        n_bootstrap=args.n_bootstrap,
        seed=args.seed,
        fdr_q=args.fdr_q,
    )


if __name__ == "__main__":
    main()
