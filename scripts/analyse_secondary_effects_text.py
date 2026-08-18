#!/usr/bin/env python3
"""
Secondary Effects Analysis for Phase 3a Text Track Matrix
==========================================================

Comprehensive analysis of secondary effects across the 2×4 thinking ×
temperature matrix (HIGH/MINIMAL × T=0.0/0.3/0.7/1.0) for the text
track at 384 px on 487 tiles.

Mirrors ``analyse_secondary_effects.py`` (image track) exactly — same
sub-analyses, same bootstrap parameters, same output format — so image
and text findings can be compared side-by-side. The only difference is
the condition registry (text-track output paths).

Looks beyond F1 for effects the primary leaderboard analysis misses:
precision/recall trade-offs, run-to-run variability, tile-level
discrimination, spatial precision, threshold robustness, per-map and
per-subtype breakdowns, thinking × temperature interactions, consensus
convergence, vote distributions, cost-performance trade-offs, and
spatial clustering of errors.

Usage::

    python scripts/analyse_secondary_effects.py \\
        --output-dir results/secondary-effects/

Inputs:
    - Detection runs: outputs/h11/pv-diag-384/*/
    - Consensus GeoJSONs: */consensus/consensus_t*.geojson
    - Ground truth: inputs/vectors/references/mounds-reference.geojson
    - Bounds: inputs/vectors/bounds/384/full_evaluation_bounds.geojson

Outputs:
    - secondary_effects.json — comprehensive results
    - secondary_effects_autogen.md — auto-generated tables + boilerplate
                                      (hand-authored `secondary_effects.md`
                                      is the paper-citation source; do NOT
                                      overwrite — Session 75 guardrail 6)

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-17
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np

__version__ = "1.0.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from lib_advanced_metrics import (  # noqa: E402
    bootstrap_interaction_ci,
    bootstrap_tile_classification_ci,
    calculate_f1_internal,
    calculate_tile_classification,
    compute_per_tile_tp_fp_fn,
    normalise_ref_class,
    spatial_tolerance_curve,
)
from evaluate_detections import load_geojson  # noqa: E402
from lib_detection_paths import resolve_pool_passes  # noqa: E402

logger = logging.getLogger(__name__)

# Rendered wherever a tile-level metric is not computable (erratum E81).
# Matches ``evaluate_detections.UNDEFINED_DISPLAY``.
UNDEFINED_DISPLAY = "undefined"


def fmt_metric(val: float | None, digits: int = 3) -> str:
    """Format a possibly-undefined tile metric for a table or log line.

    Args:
        val: The metric, or ``None`` when it is undefined — the 2 x 2
            tile confusion matrix is degenerate, so the Matthews
            Correlation Coefficient (MCC) has no value (erratum E81).
        digits: Decimal places for the numeric case.

    Returns:
        The formatted number, or :data:`UNDEFINED_DISPLAY`. A genuine
        zero still renders as ``'0.000'``; only a non-measurement gets
        the word.
    """
    return UNDEFINED_DISPLAY if val is None else f"{val:.{digits}f}"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BOUNDS = (
    PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
)
DEFAULT_GT = (
    PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
)
DEFAULT_SEED = 42
DEFAULT_BOOTSTRAP = 1000

# Condition registry: 8 text-track conditions (no scale-4 equivalent for text)
# Note: T=0.7 has K=30 but we use the full consensus/ dir (threshold sweep over
# all 30 passes) as the primary; consensus-n10 and consensus-n5 subsets exist
# separately for the verifier matrix.
CONDITION_REGISTRY = {
    "HIGH-T0.0": {
        "thinking": "HIGH", "temperature": 0.0, "K": 3,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0",
        "consensus_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/consensus",
    },
    "HIGH-T0.3": {
        "thinking": "HIGH", "temperature": 0.3, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3",
        "consensus_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3/consensus",
    },
    "HIGH-T0.7": {
        "thinking": "HIGH", "temperature": 0.7, "K": 30,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
        "consensus_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/consensus",
    },
    "HIGH-T1.0": {
        "thinking": "HIGH", "temperature": 1.0, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0",
        "consensus_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0/consensus",
    },
    "MIN-T0.0": {
        "thinking": "MINIMAL", "temperature": 0.0, "K": 3,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.0",
        "consensus_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.0/consensus",
    },
    "MIN-T0.3": {
        "thinking": "MINIMAL", "temperature": 0.3, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3",
        "consensus_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3/consensus",
    },
    "MIN-T0.7": {
        "thinking": "MINIMAL", "temperature": 0.7, "K": 30,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
        "consensus_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/consensus",
    },
    "MIN-T1.0": {
        "thinking": "MINIMAL", "temperature": 1.0, "K": 10,
        "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0",
        "consensus_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0/consensus",
    },
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def assign_source_tile(gdf_det: gpd.GeoDataFrame, gdf_bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Assign source_tile to detections via spatial join with bounds.

    Consensus GeoJSONs have 'source_tiles' (plural list) but the
    evaluation library requires 'source_tile' (singular string).
    This function assigns each detection to the nearest tile centroid.
    """
    if "source_tile" in gdf_det.columns:
        return gdf_det
    if gdf_det.empty:
        gdf_det["source_tile"] = []
        return gdf_det
    # Spatial join: assign each detection to the nearest intersecting tile.
    # Use "intersects" (not "within") because overlapping tiles mean a point
    # can intersect multiple tiles. Keep the first match per detection.
    # This matches the pattern in evaluate_detections.py lines 770-782.
    joined = gpd.sjoin(
        gdf_det, gdf_bounds[["tile_name", "geometry"]],
        how="left", predicate="intersects",
    )
    # Deduplicate: keep first matching tile per detection
    joined = joined[~joined.index.duplicated(keep="first")]
    gdf_det["source_tile"] = joined["tile_name"]
    return gdf_det


def load_consensus_geojson(path: Path, gdf_bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Load a consensus GeoJSON and assign source_tile."""
    gdf = load_geojson(path)
    if gdf.empty:
        return gdf
    return assign_source_tile(gdf, gdf_bounds)


def find_optimal_threshold(consensus_dir: Path, gdf_ref, gdf_bounds, buffer_m=20):
    """Find the consensus threshold that maximises F1 at the given buffer."""
    best_t, best_f1 = 1, -1.0
    for gj in sorted(consensus_dir.glob("consensus_t*.geojson")):
        m = re.search(r"consensus_t(\d+)", gj.stem)
        if not m:
            continue
        t = int(m.group(1))
        gdf_det = load_consensus_geojson(gj, gdf_bounds)
        if gdf_det.empty:
            continue
        _, _, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_m)
        if f1 > best_f1:
            best_f1 = f1
            best_t = t
    return best_t, best_f1


def load_run_geojsons(run_dir: Path) -> list[tuple[str, Path]]:
    """Find all per-run detection GeoJSON files, sorted by run number.

    Resolution is delegated to ``lib_detection_paths.resolve_pool_passes``,
    which walks the pool's numeric ``run_<N>`` directories in run order and
    expands BOTH per-pass naming conventions. The tolerant local glob this
    function carried (any ``*.geojson`` lacking ``.meta`` / ``.tiles``) was a
    workaround for the convention-A-only loader in ``lib_consensus``; that
    loader now uses the same resolver, so the workaround is obsolete.

    Args:
        run_dir: Pool directory holding ``run_<N>`` subdirectories.

    Returns:
        List of ``(run directory name, pass GeoJSON path)`` pairs in run order.
    """
    # One file per run directory, as before: ``setdefault`` keeps the first
    # pass file of each run and dict insertion order preserves run order.
    # (Exactly one directory in the corpus holds two candidates — a complete
    # re-run superseding an incomplete attempt — and taking both would change
    # the replicate count.)
    first_per_run: dict[str, Path] = {}
    for path in resolve_pool_passes(run_dir, allow_multiple=True):
        first_per_run.setdefault(path.parent.name, path)
    return list(first_per_run.items())


def _compute_single_run_f1(
    geojson_path: Path, ref_path: Path, bounds_path: Path, buffer_m: int,
) -> dict:
    """Worker: compute F1/P/R for a single run. For ProcessPoolExecutor."""
    gdf_det = load_geojson(geojson_path)
    gdf_ref = load_geojson(ref_path)
    gdf_bounds = load_geojson(bounds_path)
    p, r, f1 = calculate_f1_internal(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_m,
    )
    return {
        "path": str(geojson_path),
        "f1": round(f1, 4), "precision": round(p, 4), "recall": round(r, 4),
        "n_detections": len(gdf_det),
    }


# ---------------------------------------------------------------------------
# Sub-analyses
# ---------------------------------------------------------------------------


def analyse_pr_decomposition(conditions, optimal_thresholds, gdf_ref, gdf_bounds, buffer_m=20):
    """Analysis 1: P/R decomposition at optimal threshold."""
    logger.info("=== Analysis 1: P/R decomposition ===")
    results = []
    n_ref = len(gdf_ref)
    for cid, cfg in conditions.items():
        t = optimal_thresholds[cid]
        gj = PROJECT_ROOT / cfg["consensus_dir"] / f"consensus_t{t}.geojson"
        gdf_det = load_consensus_geojson(gj, gdf_bounds)
        p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_m)
        n = len(gdf_det)
        pr_ratio = round(p / r, 3) if r > 0 else float("inf")
        strategy = "balanced"
        if p - r > 0.10:
            strategy = "precision-dominant"
        elif r - p > 0.10:
            strategy = "recall-dominant"
        results.append({
            "condition": cid, "threshold": t,
            "f1": round(f1, 4), "precision": round(p, 4), "recall": round(r, 4),
            "pr_ratio": pr_ratio, "n_detections": n,
            "detection_density": round(n / n_ref, 2) if n_ref else 0,
            "strategy": strategy,
        })
        logger.info("  %s t=%d: F1=%.3f P=%.3f R=%.3f n=%d (%s)",
                     cid, t, f1, p, r, n, strategy)
    return results


def analyse_run_variability(
    conditions, ref_path, bounds_path, buffer_m=20, workers=4,
):
    """Analysis 2: Run-to-run variability (per-run single-pass F1)."""
    logger.info("=== Analysis 2: Run-to-run variability ===")
    results = []

    # Build task list
    tasks = []  # (cid, run_name, geojson_path)
    for cid, cfg in conditions.items():
        run_dir = PROJECT_ROOT / cfg["run_dir"]
        runs = load_run_geojsons(run_dir)
        for run_name, gj_path in runs:
            tasks.append((cid, run_name, gj_path))

    logger.info("  Computing %d single-run F1 values (%d workers)...", len(tasks), workers)

    # Execute in parallel
    run_f1s: dict[str, list[dict]] = {cid: [] for cid in conditions}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(
                _compute_single_run_f1, gj, ref_path, bounds_path, buffer_m,
            ): (cid, run_name)
            for cid, run_name, gj in tasks
        }
        for fut in as_completed(future_map):
            cid, run_name = future_map[fut]
            try:
                result = fut.result()
                result["run"] = run_name
                run_f1s[cid].append(result)
            except Exception as exc:
                logger.error("  %s %s failed: %s", cid, run_name, exc)

    # Compute statistics per condition
    from scipy.stats import levene as levene_test

    all_groups = []
    for cid, cfg in conditions.items():
        f1_vals = [r["f1"] for r in sorted(run_f1s[cid], key=lambda x: x["run"])]
        if not f1_vals:
            continue
        mean_f1 = round(np.mean(f1_vals), 4)
        sd = round(np.std(f1_vals, ddof=1), 4) if len(f1_vals) > 1 else 0.0
        cv = round(sd / mean_f1, 4) if mean_f1 > 0 else 0.0
        results.append({
            "condition": cid, "K": cfg["K"],
            "mean_f1": mean_f1, "sd": sd, "cv": cv,
            "min": round(min(f1_vals), 4), "max": round(max(f1_vals), 4),
            "range": round(max(f1_vals) - min(f1_vals), 4),
            "per_run": f1_vals,
        })
        if len(f1_vals) >= 3:
            all_groups.append(f1_vals)
        logger.info("  %s: mean=%.3f SD=%.4f CV=%.3f (K=%d)",
                     cid, mean_f1, sd, cv, cfg["K"])

    # Levene's test across conditions with K >= 3
    levene_result = None
    if len(all_groups) >= 2:
        stat, p = levene_test(*all_groups)
        levene_result = {"statistic": round(stat, 4), "p_value": round(p, 4)}
        logger.info("  Levene's test: W=%.3f p=%.4f", stat, p)

    return {"per_condition": results, "levene_test": levene_result, "raw": run_f1s}


def analyse_tile_mcc(conditions, optimal_thresholds, gdf_ref, gdf_bounds, n_bootstrap=1000, seed=42):
    """Analysis 3: Tile-level MCC, sensitivity, specificity."""
    logger.info("=== Analysis 3: Tile-level MCC ===")
    results = []
    for cid, cfg in conditions.items():
        t = optimal_thresholds[cid]
        gj = PROJECT_ROOT / cfg["consensus_dir"] / f"consensus_t{t}.geojson"
        gdf_det = load_consensus_geojson(gj, gdf_bounds)
        tc = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)
        ci = bootstrap_tile_classification_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=n_bootstrap, random_seed=seed,
        )
        def _safe_round(val, digits=4):
            return round(val, digits) if val is not None else None

        entry = {
            "condition": cid, "threshold": t,
            "mcc": _safe_round(tc["mcc"]),
            "sensitivity": _safe_round(tc["sensitivity"]),
            "specificity": _safe_round(tc["specificity"]),
            "tp": tc["tp"], "tn": tc["tn"], "fp": tc["fp"], "fn": tc["fn"],
        }
        if ci["mcc"]["mean"] is not None:
            entry["mcc_ci"] = [round(ci["mcc"]["ci_lower"], 4), round(ci["mcc"]["ci_upper"], 4)]
        results.append(entry)
        # Erratum E81: ``tc["mcc"] or 0`` logged an undefined MCC as
        # 0.000 (and would have done the same to a real 0.0). Any of
        # the three tile metrics can be undefined on a degenerate
        # matrix, so all three go through ``fmt_metric``.
        logger.info("  %s: MCC=%s Sens=%s Spec=%s",
                     cid, fmt_metric(tc["mcc"]),
                     fmt_metric(tc["sensitivity"]),
                     fmt_metric(tc["specificity"]))
    return results


def analyse_buffer_sensitivity(conditions, optimal_thresholds, gdf_ref, gdf_bounds):
    """Analysis 4: Buffer sensitivity curve at fixed threshold."""
    logger.info("=== Analysis 4: Buffer sensitivity ===")
    buffers = [10, 15, 20, 25, 30, 40, 50]
    results = []
    for cid, cfg in conditions.items():
        t = optimal_thresholds[cid]
        gj = PROJECT_ROOT / cfg["consensus_dir"] / f"consensus_t{t}.geojson"
        gdf_det = load_consensus_geojson(gj, gdf_bounds)
        curve = spatial_tolerance_curve(gdf_det, gdf_ref, gdf_bounds, buffers=buffers)
        f1_20 = next((c["f1"] for c in curve if c["buffer"] == 20), 0)
        f1_50 = next((c["f1"] for c in curve if c["buffer"] == 50), 0)
        slope = round((f1_50 - f1_20) / 30, 5) if f1_20 > 0 else 0
        elasticity = round((f1_50 - f1_20) / f1_20 * 100, 1) if f1_20 > 0 else 0
        results.append({
            "condition": cid, "threshold": t,
            "curve": curve, "slope": slope, "elasticity_pct": elasticity,
            "f1_20m": f1_20, "f1_50m": f1_50,
        })
        logger.info("  %s: F1@20m=%.3f F1@50m=%.3f slope=%.5f elasticity=%.1f%%",
                     cid, f1_20, f1_50, slope, elasticity)
    return results


def analyse_threshold_robustness(conditions, gdf_ref, gdf_bounds, buffer_m=20):
    """Analysis 5: Threshold sensitivity / robustness."""
    logger.info("=== Analysis 5: Threshold robustness ===")
    results = []
    for cid, cfg in conditions.items():
        consensus_dir = PROJECT_ROOT / cfg["consensus_dir"]
        sweep = []
        for gj in sorted(consensus_dir.glob("consensus_t*.geojson")):
            m = re.search(r"consensus_t(\d+)", gj.stem)
            if not m:
                continue
            t = int(m.group(1))
            gdf_det = load_consensus_geojson(gj, gdf_bounds)
            _, _, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_m)
            sweep.append({"t": t, "f1": round(f1, 4)})

        if not sweep:
            continue
        best = max(sweep, key=lambda x: x["f1"])
        plateau = [s for s in sweep if s["f1"] >= best["f1"] - 0.02]
        f1_range = round(max(s["f1"] for s in sweep) - min(s["f1"] for s in sweep), 4)

        # Drop at adjacent thresholds
        sorted_sweep = sorted(sweep, key=lambda x: x["t"])
        best_idx = next(i for i, s in enumerate(sorted_sweep) if s["t"] == best["t"])
        drop_minus = round(best["f1"] - sorted_sweep[best_idx - 1]["f1"], 4) if best_idx > 0 else None
        drop_plus = round(best["f1"] - sorted_sweep[best_idx + 1]["f1"], 4) if best_idx < len(sorted_sweep) - 1 else None

        results.append({
            "condition": cid, "optimal_t": best["t"], "optimal_f1": best["f1"],
            "plateau_width": len(plateau), "f1_range": f1_range,
            "drop_at_t_minus_1": drop_minus, "drop_at_t_plus_1": drop_plus,
            "sweep": sweep,
        })
        logger.info("  %s: optimal t=%d F1=%.3f plateau=%d range=%.3f",
                     cid, best["t"], best["f1"], len(plateau), f1_range)
    return results


def analyse_per_map_sheet(conditions, optimal_thresholds, gdf_ref, gdf_bounds, buffer_m=20):
    """Analysis 6: Per-map-sheet F1."""
    logger.info("=== Analysis 6: Per-map-sheet F1 ===")
    # Get map names from bounds
    maps = sorted(gdf_bounds["tile_name"].apply(
        lambda t: "_".join(t.split("_")[:2]) if "_" in t else t
    ).unique())
    logger.info("  Maps: %s", maps)

    results = []
    for cid, cfg in conditions.items():
        t = optimal_thresholds[cid]
        gj = PROJECT_ROOT / cfg["consensus_dir"] / f"consensus_t{t}.geojson"
        gdf_det = load_consensus_geojson(gj, gdf_bounds)

        per_map = {}
        for map_name in maps:
            map_bounds = gdf_bounds[gdf_bounds["tile_name"].str.startswith(map_name)]
            if map_bounds.empty:
                continue
            p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, map_bounds, buffer_metres=buffer_m)
            per_map[map_name] = round(f1, 4)

        f1_vals = list(per_map.values())
        results.append({
            "condition": cid, "per_map": per_map,
            "range": round(max(f1_vals) - min(f1_vals), 4) if f1_vals else 0,
            "sd": round(np.std(f1_vals, ddof=1), 4) if len(f1_vals) > 1 else 0,
        })
        logger.info("  %s: %s range=%.3f",
                     cid, {k: f"{v:.3f}" for k, v in per_map.items()},
                     results[-1]["range"])
    return results


def analyse_per_subtype_recall(conditions, optimal_thresholds, gdf_ref, gdf_bounds, buffer_m=20):
    """Analysis 7: Per-subtype recall."""
    logger.info("=== Analysis 7: Per-subtype recall ===")

    # Classify references by subtype
    subtypes = {}
    for _, row in gdf_ref.iterrows():
        st = normalise_ref_class(row.get("Symbol", ""))
        if st not in subtypes:
            subtypes[st] = []
        subtypes[st].append(row)
    logger.info("  Subtypes: %s", {k: len(v) for k, v in subtypes.items()})

    results = []
    for cid, cfg in conditions.items():
        t = optimal_thresholds[cid]
        gj = PROJECT_ROOT / cfg["consensus_dir"] / f"consensus_t{t}.geojson"
        gdf_det = load_consensus_geojson(gj, gdf_bounds)

        per_subtype = {}
        for st, refs in subtypes.items():
            gdf_ref_sub = gpd.GeoDataFrame(refs, crs=gdf_ref.crs)
            _, r, _ = calculate_f1_internal(gdf_det, gdf_ref_sub, gdf_bounds, buffer_metres=buffer_m)
            per_subtype[st] = round(r, 4)

        results.append({"condition": cid, "per_subtype": per_subtype})
        logger.info("  %s: %s", cid, per_subtype)
    return results


def analyse_thinking_temp_interaction(conditions, optimal_thresholds, gdf_ref, gdf_bounds, seed=42):
    """Analysis 8: Comprehensive thinking × temperature interaction."""
    logger.info("=== Analysis 8: Thinking × temperature interaction ===")

    # Build 2×4 matrix of F1, P, R at optimal thresholds
    matrix = {}
    for cid, cfg in conditions.items():
        if cfg.get("library") == "scale-4":
            continue  # Exclude scale-4 from interaction (different library)
        t = optimal_thresholds[cid]
        gj = PROJECT_ROOT / cfg["consensus_dir"] / f"consensus_t{t}.geojson"
        gdf_det = load_consensus_geojson(gj, gdf_bounds)
        p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds, buffer_metres=20)
        matrix[cid] = {
            "thinking": cfg["thinking"], "temperature": cfg["temperature"],
            "threshold": t, "f1": round(f1, 4),
            "precision": round(p, 4), "recall": round(r, 4),
            "n_detections": len(gdf_det),
        }

    # Compute HIGH advantage at each temperature
    advantages = {}
    for temp in [0.0, 0.3, 0.7, 1.0]:
        high_key = f"HIGH-T{temp}"
        min_key = f"MIN-T{temp}"
        if high_key in matrix and min_key in matrix:
            advantages[f"T{temp}"] = {
                "delta_f1": round(matrix[high_key]["f1"] - matrix[min_key]["f1"], 4),
                "delta_p": round(matrix[high_key]["precision"] - matrix[min_key]["precision"], 4),
                "delta_r": round(matrix[high_key]["recall"] - matrix[min_key]["recall"], 4),
                "delta_n": matrix[high_key]["n_detections"] - matrix[min_key]["n_detections"],
            }

    # Formal interaction test: (HIGH-T0.7 - MIN-T0.7) vs (HIGH-T0.0 - MIN-T0.0)
    # Using bootstrap_interaction_ci for F1, P, R
    interaction_tests = {}
    for metric in ["f1", "precision", "recall"]:
        # Build conditions dict for pairs that have both thinking levels
        int_conditions = {}
        for temp in [0.0, 0.3, 0.7, 1.0]:
            high_key = f"HIGH-T{temp}"
            min_key = f"MIN-T{temp}"
            if high_key not in conditions or min_key not in conditions:
                continue
            if conditions[high_key].get("library") == "scale-4":
                continue
            for think_key, think_label in [(high_key, "HIGH"), (min_key, "MINIMAL")]:
                t = optimal_thresholds[think_key]
                gj = PROJECT_ROOT / conditions[think_key]["consensus_dir"] / f"consensus_t{t}.geojson"
                gdf_det = load_consensus_geojson(gj, gdf_bounds)
                int_conditions[(think_label, f"T{temp}")] = (gdf_det, gdf_bounds)

        if len(int_conditions) >= 4:
            try:
                result = bootstrap_interaction_ci(
                    int_conditions, gdf_ref,
                    factor_a_name="thinking", factor_b_name="temperature",
                    metric=metric, n_iterations=1000, random_seed=seed,
                )
                interaction_tests[metric] = result
                logger.info("  Interaction test (%s): %s",
                             metric, "significant" if result.get("any_significant") else "not significant")
            except Exception as exc:
                logger.warning("  Interaction test (%s) failed: %s", metric, exc)
                interaction_tests[metric] = {"error": str(exc)}

    return {
        "matrix": matrix,
        "high_advantage": advantages,
        "interaction_tests": interaction_tests,
    }


def analyse_consensus_convergence(
    conditions, ref_path, bounds_path, buffer_m=20, workers=4,
):
    """Analysis 9: Consensus convergence curves (F1 vs N)."""
    logger.info("=== Analysis 9: Consensus convergence ===")
    # For each condition with K=10, compute consensus at N=1..10
    # N=1 is just the single-pass F1 for run_1
    # N=2..10 requires building consensus from first N runs

    # This is expensive — we use the per-run F1 values from analysis 2
    # as the N=1 data point, and the consensus sweeps for N=K data points.
    # For intermediate N, we'd need to rebuild consensus — skip for now
    # and use N=1 (single-pass mean) and N=K (from threshold sweep).

    # Actually, we have N=5 and N=10 consensus already built.
    # Report F1 at: single-pass mean, N=5 optimal, N=10 optimal.
    # Load shared data once
    gdf_ref_local = load_geojson(ref_path)
    gdf_bounds_local = load_geojson(bounds_path)

    results = []
    for cid, cfg in conditions.items():
        entry = {"condition": cid, "K": cfg["K"], "points": []}

        # N=10 (or N=K) optimal — already computed
        consensus_dir = PROJECT_ROOT / cfg["consensus_dir"]
        if consensus_dir.exists():
            _, best_f1 = find_optimal_threshold(consensus_dir, gdf_ref_local, gdf_bounds_local, buffer_m)
            entry["points"].append({"N": cfg["K"], "f1": round(best_f1, 4), "source": "consensus"})

        # N=5 if available
        n5_dir = consensus_dir.parent / "consensus-n5"
        if n5_dir.exists() and cfg["K"] >= 5:
            _, f1_n5 = find_optimal_threshold(n5_dir, gdf_ref_local, gdf_bounds_local, buffer_m)
            entry["points"].append({"N": 5, "f1": round(f1_n5, 4), "source": "consensus-n5"})

        entry["points"].sort(key=lambda x: x["N"])
        results.append(entry)
        pts = ", ".join(f"N={p['N']}:{p['f1']:.3f}" for p in entry["points"])
        logger.info("  %s: %s", cid, pts)
    return results


def analyse_vote_distribution(conditions):
    """Analysis 10: Vote distribution / agreement analysis."""
    logger.info("=== Analysis 10: Vote distribution ===")
    results = []
    for cid, cfg in conditions.items():
        summary_path = PROJECT_ROOT / cfg["consensus_dir"] / "voting_summary.json"
        if not summary_path.exists():
            continue
        with open(summary_path, encoding="utf-8") as f:
            vs = json.load(f)
        total_passes = vs.get("total_passes", 0)
        thresholds = vs.get("thresholds", {})

        # Convert to distribution: how many detections at each vote level
        t1 = thresholds.get("1", thresholds.get(1, 0))
        distribution = {}
        for t in range(1, total_passes + 1):
            count_at_t = thresholds.get(str(t), thresholds.get(t, 0))
            count_next = thresholds.get(str(t + 1), thresholds.get(t + 1, 0))
            exact_at_t = count_at_t - count_next
            distribution[t] = exact_at_t

        # Fraction unanimous (vote = total_passes)
        unanimous = distribution.get(total_passes, 0)
        frac_unanimous = round(unanimous / t1, 3) if t1 > 0 else 0
        # Fraction contentious (vote = 1)
        contentious = distribution.get(1, 0)
        frac_contentious = round(contentious / t1, 3) if t1 > 0 else 0
        # Mean vote count
        total_votes = sum(t * n for t, n in distribution.items())
        mean_vote = round(total_votes / t1, 2) if t1 > 0 else 0

        results.append({
            "condition": cid, "total_passes": total_passes,
            "total_candidates": t1,
            "frac_unanimous": frac_unanimous,
            "frac_contentious": frac_contentious,
            "mean_vote_count": mean_vote,
            "distribution": distribution,
        })
        logger.info("  %s: %d candidates, %.1f%% unanimous, %.1f%% contentious, mean=%.1f",
                     cid, t1, frac_unanimous * 100, frac_contentious * 100, mean_vote)
    return results


def analyse_cost_pareto(conditions, optimal_thresholds, pr_results):
    """Analysis 11: Cost-performance Pareto frontier."""
    logger.info("=== Analysis 11: Cost-performance Pareto ===")
    # Estimate cost per run from thinking level
    # HIGH: ~$2/run at Flex (with thinking tokens)
    # MINIMAL: ~$0.75/run at Flex
    cost_per_run = {"HIGH": 2.0, "MINIMAL": 0.75}

    results = []
    for entry in pr_results:
        cid = entry["condition"]
        cfg = conditions[cid]
        thinking = cfg["thinking"]
        k = cfg["K"]
        cost = k * cost_per_run.get(thinking, 1.0)
        results.append({
            "condition": cid, "f1": entry["f1"],
            "K": k, "thinking": thinking,
            "estimated_cost_usd": round(cost, 2),
            "f1_per_dollar": round(entry["f1"] / cost, 4) if cost > 0 else 0,
        })

    # Identify Pareto-optimal points (max F1 at each cost level)
    results.sort(key=lambda x: x["estimated_cost_usd"])
    pareto = []
    best_f1 = -1
    for r in results:
        if r["f1"] > best_f1:
            pareto.append(r["condition"])
            best_f1 = r["f1"]
    for r in results:
        r["pareto_optimal"] = r["condition"] in pareto

    logger.info("  Pareto-optimal: %s", pareto)
    return results


def analyse_spatial_clustering(conditions, optimal_thresholds, gdf_ref, gdf_bounds, buffer_m=20):
    """Analysis 12: FP/FN spatial clustering across tiles."""
    logger.info("=== Analysis 12: Spatial clustering of errors ===")
    results = []
    # Track per-tile FP and FN across conditions to find problem tiles
    all_tile_fps = {}
    all_tile_fns = {}

    for cid, cfg in conditions.items():
        t = optimal_thresholds[cid]
        gj = PROJECT_ROOT / cfg["consensus_dir"] / f"consensus_t{t}.geojson"
        gdf_det = load_consensus_geojson(gj, gdf_bounds)
        tile_metrics = compute_per_tile_tp_fp_fn(gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_m)

        fps = tile_metrics["fp"].values
        fns = tile_metrics["fn"].values
        fp_cv = round(np.std(fps) / np.mean(fps), 3) if np.mean(fps) > 0 else 0
        fn_cv = round(np.std(fns) / np.mean(fns), 3) if np.mean(fns) > 0 else 0

        results.append({
            "condition": cid,
            "fp_mean": round(np.mean(fps), 3), "fp_sd": round(np.std(fps), 3), "fp_cv": fp_cv,
            "fn_mean": round(np.mean(fns), 3), "fn_sd": round(np.std(fns), 3), "fn_cv": fn_cv,
            "fp_max_tile": tile_metrics.loc[tile_metrics["fp"].idxmax(), "tile_name"] if len(fps) > 0 else "",
            "fn_max_tile": tile_metrics.loc[tile_metrics["fn"].idxmax(), "tile_name"] if len(fns) > 0 else "",
        })

        # Accumulate for cross-condition problem tile analysis
        for _, row in tile_metrics.iterrows():
            tn = row["tile_name"]
            all_tile_fps[tn] = all_tile_fps.get(tn, 0) + row["fp"]
            all_tile_fns[tn] = all_tile_fns.get(tn, 0) + row["fn"]

    # Top problem tiles (highest cumulative FP or FN across all conditions)
    top_fp_tiles = sorted(all_tile_fps.items(), key=lambda x: -x[1])[:10]
    top_fn_tiles = sorted(all_tile_fns.items(), key=lambda x: -x[1])[:10]

    logger.info("  Top FP tiles: %s", [(t, c) for t, c in top_fp_tiles[:3]])
    logger.info("  Top FN tiles: %s", [(t, c) for t, c in top_fn_tiles[:3]])
    return {
        "per_condition": results,
        "top_fp_tiles": [{"tile": t, "cumulative_fp": c} for t, c in top_fp_tiles],
        "top_fn_tiles": [{"tile": t, "cumulative_fn": c} for t, c in top_fn_tiles],
    }


def analyse_thinking_tokens(conditions):
    """Analysis 13: Thinking token efficiency (from .meta.json)."""
    logger.info("=== Analysis 13: Thinking token efficiency ===")
    results = []
    for cid, cfg in conditions.items():
        run_dir = PROJECT_ROOT / cfg["run_dir"]
        for run_path in sorted(run_dir.glob("run_*")):
            metas = list(run_path.glob("*.meta.json"))
            if not metas:
                continue
            with open(metas[0], encoding="utf-8") as f:
                meta = json.load(f)
            usage = meta.get("usage_stats", {})
            thinking_tokens = usage.get("total_thoughts_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            results.append({
                "condition": cid, "run": run_path.name,
                "thinking_tokens": thinking_tokens,
                "total_tokens": total_tokens,
                "thinking_fraction": round(thinking_tokens / total_tokens, 3) if total_tokens > 0 else 0,
            })

    # Summarise by condition
    from collections import defaultdict
    by_cond = defaultdict(list)
    for r in results:
        by_cond[r["condition"]].append(r["thinking_tokens"])
    summary = []
    for cid, tokens in sorted(by_cond.items()):
        mean_t = round(np.mean(tokens)) if tokens else 0
        summary.append({"condition": cid, "mean_thinking_tokens": mean_t, "n_runs": len(tokens)})
        logger.info("  %s: mean thinking tokens = %d (%d runs)", cid, mean_t, len(tokens))

    return {"per_run": results, "summary": summary}


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_markdown(all_results, output_path, conditions):
    """Write formatted markdown report."""
    lines = []
    lines.append("# Secondary Effects Analysis: Phase 3a Text Track")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}")
    lines.append(f"**Conditions**: {len(conditions)}")
    lines.append("**Scope**: 384 px, 487 tiles (Era 2)")
    lines.append("")

    # 1. P/R decomposition
    pr = all_results.get("pr_decomposition", [])
    if pr:
        lines.append("## 1. Precision / Recall Decomposition (20m)")
        lines.append("")
        lines.append("| Condition | t | F1 | P | R | P/R | n_det | Strategy |")
        lines.append("|-----------|--:|---:|--:|--:|----:|------:|----------|")
        for r in sorted(pr, key=lambda x: -x["f1"]):
            lines.append(
                f"| {r['condition']} | {r['threshold']} | {r['f1']:.3f} | "
                f"{r['precision']:.3f} | {r['recall']:.3f} | {r['pr_ratio']:.2f} | "
                f"{r['n_detections']} | {r['strategy']} |"
            )
        lines.append("")

    # 2. Run-to-run variability
    var = all_results.get("run_variability", {})
    if var.get("per_condition"):
        lines.append("## 2. Run-to-Run Variability")
        lines.append("")
        lines.append("| Condition | K | Mean F1 | SD | CV | Min | Max | Range |")
        lines.append("|-----------|--:|--------:|---:|---:|----:|----:|------:|")
        for r in var["per_condition"]:
            lines.append(
                f"| {r['condition']} | {r['K']} | {r['mean_f1']:.3f} | "
                f"{r['sd']:.4f} | {r['cv']:.3f} | {r['min']:.3f} | "
                f"{r['max']:.3f} | {r['range']:.3f} |"
            )
        if var.get("levene_test"):
            lt = var["levene_test"]
            lines.append(f"\nLevene's test: W={lt['statistic']:.3f}, p={lt['p_value']:.4f}")
        lines.append("")

    # 3. Tile-level MCC
    mcc = all_results.get("tile_mcc", [])
    if mcc:
        lines.append("## 3. Tile-Level MCC / Sensitivity / Specificity")
        lines.append("")
        lines.append("| Condition | MCC | 95% CI | Sens | Spec | TP | TN | FP | FN |")
        lines.append("|-----------|----:|:------:|-----:|-----:|---:|---:|---:|---:|")
        # Erratum E81: rank the conditions whose MCC is defined, and
        # list the undefined ones after them UNRANKED. The old key,
        # ``-(x["mcc"] or 0)``, sorted an undefined MCC into the
        # position of a chance-level result (and did the same to a
        # legitimate 0.0).
        ranked = sorted(
            (r for r in mcc if r["mcc"] is not None),
            key=lambda x: -x["mcc"],
        )
        ranked += [r for r in mcc if r["mcc"] is None]
        for r in ranked:
            mcc_val = fmt_metric(r["mcc"])
            ci = f"[{r['mcc_ci'][0]:.3f}, {r['mcc_ci'][1]:.3f}]" if "mcc_ci" in r else "—"
            lines.append(
                f"| {r['condition']} | {mcc_val} | {ci} | "
                f"{fmt_metric(r['sensitivity'])} | "
                f"{fmt_metric(r['specificity'])} | "
                f"{r['tp']} | {r['tn']} | {r['fp']} | {r['fn']} |"
            )
        lines.append("")

    # 4. Buffer sensitivity
    buf = all_results.get("buffer_sensitivity", [])
    if buf:
        lines.append("## 4. Buffer Sensitivity (spatial precision)")
        lines.append("")
        lines.append("| Condition | F1@20m | F1@50m | Slope | Elasticity |")
        lines.append("|-----------|-------:|-------:|------:|-----------:|")
        for r in sorted(buf, key=lambda x: x["slope"]):
            lines.append(
                f"| {r['condition']} | {r['f1_20m']:.3f} | {r['f1_50m']:.3f} | "
                f"{r['slope']:.5f} | {r['elasticity_pct']:.1f}% |"
            )
        lines.append("")

    # 5. Threshold robustness
    rob = all_results.get("threshold_robustness", [])
    if rob:
        lines.append("## 5. Threshold Robustness")
        lines.append("")
        lines.append("| Condition | Opt t | Opt F1 | Plateau | Range | Drop t-1 | Drop t+1 |")
        lines.append("|-----------|------:|-------:|--------:|------:|---------:|---------:|")
        for r in sorted(rob, key=lambda x: -x["plateau_width"]):
            dm = f"{r['drop_at_t_minus_1']:.3f}" if r["drop_at_t_minus_1"] is not None else "—"
            dp = f"{r['drop_at_t_plus_1']:.3f}" if r["drop_at_t_plus_1"] is not None else "—"
            lines.append(
                f"| {r['condition']} | {r['optimal_t']} | {r['optimal_f1']:.3f} | "
                f"{r['plateau_width']} | {r['f1_range']:.3f} | {dm} | {dp} |"
            )
        lines.append("")

    # 6. Per-map-sheet F1
    pms = all_results.get("per_map_sheet", [])
    if pms:
        lines.append("## 6. Per-Map-Sheet F1 (20m)")
        lines.append("")
        # Get map names from first entry
        maps = sorted(pms[0]["per_map"].keys()) if pms else []
        header = "| Condition | " + " | ".join(maps) + " | Range | SD |"
        sep = "|-----------|" + "|".join(["-----:" for _ in maps]) + "|------:|---:|"
        lines.append(header)
        lines.append(sep)
        for r in pms:
            vals = " | ".join(f"{r['per_map'].get(m, 0):.3f}" for m in maps)
            lines.append(
                f"| {r['condition']} | {vals} | {r['range']:.3f} | {r['sd']:.3f} |"
            )
        lines.append("")

    # 7. Per-subtype recall
    psr = all_results.get("per_subtype_recall", [])
    if psr:
        lines.append("## 7. Per-Subtype Recall (20m)")
        lines.append("")
        subtypes = sorted(psr[0]["per_subtype"].keys()) if psr else []
        header = "| Condition | " + " | ".join(subtypes) + " |"
        sep = "|-----------|" + "|".join(["-----:" for _ in subtypes]) + "|"
        lines.append(header)
        lines.append(sep)
        for r in psr:
            vals = " | ".join(f"{r['per_subtype'].get(s, 0):.3f}" for s in subtypes)
            lines.append(f"| {r['condition']} | {vals} |")
        lines.append("")

    # 8. Thinking × temperature interaction
    interact = all_results.get("thinking_temp_interaction", {})
    if interact.get("high_advantage"):
        lines.append("## 8. Thinking × Temperature Interaction")
        lines.append("")
        lines.append("### HIGH advantage by temperature")
        lines.append("")
        lines.append("| T | \u0394 F1 | \u0394 P | \u0394 R | \u0394 n_det |")
        lines.append("|---:|------:|-----:|-----:|--------:|")
        for temp, adv in sorted(interact["high_advantage"].items()):
            lines.append(
                f"| {temp} | {adv['delta_f1']:+.3f} | {adv['delta_p']:+.3f} | "
                f"{adv['delta_r']:+.3f} | {adv['delta_n']:+d} |"
            )
        lines.append("")
        if interact.get("interaction_tests"):
            lines.append("### Interaction tests (bootstrap)")
            lines.append("")
            for metric, result in interact["interaction_tests"].items():
                if "error" in result:
                    lines.append(f"- **{metric}**: error — {result['error']}")
                else:
                    sig = "significant" if result.get("any_significant") else "not significant"
                    lines.append(f"- **{metric}**: {sig}")
            lines.append("")

    # 9. Consensus convergence
    conv = all_results.get("consensus_convergence", [])
    if conv:
        lines.append("## 9. Consensus Convergence (F1 vs N)")
        lines.append("")
        lines.append("| Condition | K | N=5 F1 | N=K F1 | Gain (N5→NK) |")
        lines.append("|-----------|--:|-------:|-------:|-------------:|")
        for r in conv:
            pts = {p["N"]: p["f1"] for p in r["points"]}
            f1_5 = pts.get(5, None)
            f1_k = pts.get(r["K"], None)
            f1_5_str = f"{f1_5:.3f}" if f1_5 is not None else "—"
            f1_k_str = f"{f1_k:.3f}" if f1_k is not None else "—"
            gain = f"{f1_k - f1_5:+.3f}" if f1_5 is not None and f1_k is not None else "—"
            lines.append(
                f"| {r['condition']} | {r['K']} | {f1_5_str} | {f1_k_str} | {gain} |"
            )
        lines.append("")

    # 10. Vote distribution
    vote = all_results.get("vote_distribution", [])
    if vote:
        lines.append("## 10. Vote Distribution / Agreement")
        lines.append("")
        lines.append("| Condition | Candidates | Unanimous | Contentious | Mean vote |")
        lines.append("|-----------|----------:|---------:|-----------:|----------:|")
        for r in vote:
            lines.append(
                f"| {r['condition']} | {r['total_candidates']} | "
                f"{r['frac_unanimous']:.1%} | {r['frac_contentious']:.1%} | "
                f"{r['mean_vote_count']:.1f} |"
            )
        lines.append("")

    # 11. Cost-performance
    cost = all_results.get("cost_pareto", [])
    if cost:
        lines.append("## 11. Cost-Performance")
        lines.append("")
        lines.append("| Condition | F1 | K | Cost ($) | F1/$ | Pareto? |")
        lines.append("|-----------|---:|--:|--------:|-----:|:-------:|")
        for r in sorted(cost, key=lambda x: -x["f1"]):
            pareto = "\u2713" if r["pareto_optimal"] else ""
            lines.append(
                f"| {r['condition']} | {r['f1']:.3f} | {r['K']} | "
                f"${r['estimated_cost_usd']:.2f} | {r['f1_per_dollar']:.3f} | {pareto} |"
            )
        lines.append("")

    # 12. Spatial clustering
    spatial = all_results.get("spatial_clustering", {})
    if spatial.get("per_condition"):
        lines.append("## 12. Spatial Clustering of Errors")
        lines.append("")
        lines.append("| Condition | FP mean | FP CV | FN mean | FN CV |")
        lines.append("|-----------|--------:|------:|--------:|------:|")
        for r in spatial["per_condition"]:
            lines.append(
                f"| {r['condition']} | {r['fp_mean']:.2f} | {r['fp_cv']:.2f} | "
                f"{r['fn_mean']:.2f} | {r['fn_cv']:.2f} |"
            )
        lines.append("")
        if spatial.get("top_fp_tiles"):
            lines.append("**Top FP tiles** (cumulative across all conditions):")
            lines.append("")
            for t in spatial["top_fp_tiles"][:5]:
                lines.append(f"- {t['tile']}: {t['cumulative_fp']} FPs")
            lines.append("")
        if spatial.get("top_fn_tiles"):
            lines.append("**Top FN tiles** (cumulative across all conditions):")
            lines.append("")
            for t in spatial["top_fn_tiles"][:5]:
                lines.append(f"- {t['tile']}: {t['cumulative_fn']} FNs")
            lines.append("")

    # 13. Thinking tokens
    tokens = all_results.get("thinking_tokens", {})
    if tokens.get("summary"):
        lines.append("## 13. Thinking Token Usage")
        lines.append("")
        lines.append("| Condition | Mean thinking tokens | Runs |")
        lines.append("|-----------|---------------------:|-----:|")
        for r in tokens["summary"]:
            lines.append(
                f"| {r['condition']} | {r['mean_thinking_tokens']:,} | {r['n_runs']} |"
            )
        lines.append("")

    lines.append(f"\n*Generated: {datetime.now(tz=timezone.utc).isoformat()}*")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Markdown report: %s", output_path)


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------


def main() -> int:
    """Run all secondary-effects analyses."""
    parser = argparse.ArgumentParser(
        description="Secondary effects analysis for Phase 3a text matrix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bounds", type=Path, default=DEFAULT_BOUNDS)
    parser.add_argument("--ground-truth", type=Path, default=DEFAULT_GT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--bootstrap", type=int, default=DEFAULT_BOOTSTRAP)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    logger.info("analyse_secondary_effects.py v%s", __version__)
    start_time = time.monotonic()

    # Load shared data
    logger.info("Loading shared data...")
    gdf_ref = load_geojson(args.ground_truth)
    gdf_bounds = load_geojson(args.bounds)
    logger.info("  %d references, %d tiles", len(gdf_ref), len(gdf_bounds))

    conditions = CONDITION_REGISTRY

    # Find optimal thresholds for each condition
    logger.info("Finding optimal thresholds...")
    optimal_thresholds = {}
    for cid, cfg in conditions.items():
        consensus_dir = PROJECT_ROOT / cfg["consensus_dir"]
        t, f1 = find_optimal_threshold(consensus_dir, gdf_ref, gdf_bounds)
        optimal_thresholds[cid] = t
        logger.info("  %s: t=%d F1=%.3f", cid, t, f1)

    # Run all analyses
    all_results = {}

    all_results["pr_decomposition"] = analyse_pr_decomposition(
        conditions, optimal_thresholds, gdf_ref, gdf_bounds)

    all_results["run_variability"] = analyse_run_variability(
        conditions, args.ground_truth, args.bounds, workers=args.workers)

    all_results["tile_mcc"] = analyse_tile_mcc(
        conditions, optimal_thresholds, gdf_ref, gdf_bounds,
        n_bootstrap=args.bootstrap, seed=args.seed)

    all_results["buffer_sensitivity"] = analyse_buffer_sensitivity(
        conditions, optimal_thresholds, gdf_ref, gdf_bounds)

    all_results["threshold_robustness"] = analyse_threshold_robustness(
        conditions, gdf_ref, gdf_bounds)

    all_results["per_map_sheet"] = analyse_per_map_sheet(
        conditions, optimal_thresholds, gdf_ref, gdf_bounds)

    all_results["per_subtype_recall"] = analyse_per_subtype_recall(
        conditions, optimal_thresholds, gdf_ref, gdf_bounds)

    all_results["thinking_temp_interaction"] = analyse_thinking_temp_interaction(
        conditions, optimal_thresholds, gdf_ref, gdf_bounds, seed=args.seed)

    all_results["consensus_convergence"] = analyse_consensus_convergence(
        conditions, args.ground_truth, args.bounds, workers=args.workers)

    all_results["vote_distribution"] = analyse_vote_distribution(conditions)

    all_results["cost_pareto"] = analyse_cost_pareto(
        conditions, optimal_thresholds, all_results["pr_decomposition"])

    all_results["spatial_clustering"] = analyse_spatial_clustering(
        conditions, optimal_thresholds, gdf_ref, gdf_bounds)

    all_results["thinking_tokens"] = analyse_thinking_tokens(conditions)

    # Write outputs
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # JSON (convert numpy types for serialisation)
    json_path = args.output_dir / "secondary_effects.json"

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, cls=NumpyEncoder)
    logger.info("JSON: %s", json_path)

    # Markdown — Session 76 guardrail: write to _autogen.md sibling so the
    # hand-authored secondary_effects.md is protected against overwrite.
    md_path = args.output_dir / "secondary_effects_autogen.md"
    write_markdown(all_results, md_path, conditions)

    elapsed = time.monotonic() - start_time
    logger.info("Complete in %.1fs", elapsed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
