#!/usr/bin/env python3
"""
Phase 3a-HIGH Text Track: Full Consensus Sweep Analysis
========================================================

Computes F1/precision/recall point estimates and bootstrap 95% CIs for all
135 consensus configurations (3 temperatures x [5+10+30] vote thresholds),
plus pairwise comparisons against minimal and Proposer-Verifier (PV) baselines.

Designed to run on sapphire (12C/24T AMD Ryzen 9 7900) with multiprocessing.

Pool sizes follow preregistration section 3.8 first-N convention:
  - N=5  uses runs 1-5,  vote thresholds 1..5
  - N=10 uses runs 1-10, vote thresholds 1..10
  - N=30 uses runs 1-30, vote thresholds 1..30

Consensus merging method:
  1. Load all N detection GeoJSONs
  2. Deduplicate within each run (20 m clustering)
  3. Cluster across runs (20 m spatial tolerance via scipy.spatial.cKDTree)
  4. Keep clusters where >= vote_threshold distinct runs contribute
  5. Build GeoDataFrame with source_tile column; CRS forced to EPSG:32635

Outputs:
  - phase3a-high-text-consensus-sweep.json: 135 configs with F1/CI/P/R
  - phase3a-high-text-pairwise.json: pairwise comparisons with effect sizes

Usage:
    python scripts/consensus-sweep-phase3a-high-text.py \\
        --data-dir /path/to/data \\
        --pv-dir /path/to/pv-data \\
        --output-dir /path/to/output \\
        --workers 10

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import logging
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point as ShapelyPoint

# ---------------------------------------------------------------------------
# Library imports
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_advanced_metrics import (  # noqa: E402
    bootstrap_ci,
    bootstrap_effect_size_ci,
    calculate_f1_internal,
)
from scripts.lib_consensus import (  # noqa: E402
    TARGET_CRS,
    build_pv_gdf,
    deduplicate_within_pass,
    generate_consensus_gdf,
    load_run_detections,
    load_shared_data,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(processName)s] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BUFFER_METRES = 20
BOOTSTRAP_ITERATIONS = 1000
BOOTSTRAP_SEED = 42

# Temperature directories
TEMPERATURES = ["T0.3", "T0.7", "T1.0"]

# Pool sizes and their vote threshold ranges (preregistration section 3.8)
POOL_CONFIGS = {
    5: list(range(1, 6)),       # N=5: thresholds 1..5
    10: list(range(1, 11)),     # N=10: thresholds 1..10
    30: list(range(1, 31)),     # N=30: thresholds 1..30
}


# ===================================================================
# Script-specific helpers
# ===================================================================

def get_run_dirs(base_dir: Path, temp: str, n_runs: int) -> list[Path]:
    """
    Get the first N run directories for a temperature (first-N convention).

    Args:
        base_dir: Base directory for the track (e.g., phase3a-high/track2-text/).
        temp: Temperature directory name (e.g., 'T0.7').
        n_runs: Number of runs to include.

    Returns:
        Sorted list of N run directory paths.
    """
    temp_dir = base_dir / temp
    all_runs = sorted(
        (p for p in temp_dir.iterdir() if p.is_dir() and "_" in p.name),
        key=lambda p: int(p.name.split("_")[1]),
    )
    return all_runs[:n_runs]


# ===================================================================
# Worker functions for multiprocessing
# ===================================================================

def compute_single_consensus(args: tuple) -> dict:
    """
    Compute F1/P/R point estimate and bootstrap CI for one consensus config.

    Args:
        args: Tuple of (temp, pool_size, threshold, high_base_dir,
              data_dir_str) for pickling across processes.

    Returns:
        Dict with configuration info, point estimates, and bootstrap CIs.
    """
    temp, pool_size, threshold, high_base_dir_str, data_dir_str = args
    high_base_dir = Path(high_base_dir_str)
    data_dir = Path(data_dir_str)

    # Load shared data
    gdf_ref, gdf_bounds = load_shared_data(data_dir)

    # Get run directories
    run_dirs = get_run_dirs(high_base_dir, temp, pool_size)

    # Generate consensus GeoDataFrame
    gdf_consensus = generate_consensus_gdf(run_dirs, threshold)

    n_detections = len(gdf_consensus)

    # Compute point estimates
    if n_detections == 0:
        precision, recall, f1 = 0.0, 0.0, 0.0
    else:
        precision, recall, f1 = calculate_f1_internal(
            gdf_consensus, gdf_ref, gdf_bounds, buffer_metres=BUFFER_METRES,
        )

    # Compute bootstrap CIs
    if n_detections == 0:
        ci = {
            "f1": {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0},
            "precision": {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0},
            "recall": {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0},
            "n_iterations": BOOTSTRAP_ITERATIONS,
        }
    else:
        ci = bootstrap_ci(
            gdf_consensus, gdf_ref, gdf_bounds,
            n_iterations=BOOTSTRAP_ITERATIONS,
            random_seed=BOOTSTRAP_SEED,
            buffer_metres=BUFFER_METRES,
        )

    config_key = f"{temp}_N{pool_size}_T{threshold}"
    logger.info(
        "Done: %s  F1=%.4f P=%.4f R=%.4f  (%d detections)",
        config_key, f1, precision, recall, n_detections,
    )

    return {
        "config_key": config_key,
        "temperature": temp,
        "pool_size": pool_size,
        "vote_threshold": threshold,
        "n_detections": n_detections,
        "point_estimates": {
            "f1": round(f1, 6),
            "precision": round(precision, 6),
            "recall": round(recall, 6),
        },
        "bootstrap_ci": ci,
    }


def compute_pairwise(args: tuple) -> dict:
    """
    Compute a single pairwise effect size comparison.

    Args:
        args: Tuple of (comparison_name, gdf_det_a_info, gdf_det_b_info,
              data_dir_str, pv_dir_str, high_base_dir_str, min_base_dir_str)

    Returns:
        Dict with comparison name and effect size results.
    """
    (
        comparison_name,
        condition_a_spec,
        condition_b_spec,
        data_dir_str,
        pv_dir_str,
        high_base_dir_str,
        min_base_dir_str,
    ) = args

    data_dir = Path(data_dir_str)
    pv_dir = Path(pv_dir_str)

    # Load shared data
    gdf_ref, gdf_bounds = load_shared_data(data_dir)

    # Build GeoDataFrames for each condition
    def _build_gdf(spec: dict) -> gpd.GeoDataFrame:
        """Build GeoDataFrame from a condition specification."""
        if spec["type"] == "consensus":
            run_dirs = get_run_dirs(
                Path(spec["base_dir"]), spec["temp"], spec["pool_size"],
            )
            return generate_consensus_gdf(run_dirs, spec["threshold"])
        elif spec["type"] == "single_run":
            run_dir = get_run_dirs(
                Path(spec["base_dir"]), spec["temp"], spec["run_num"],
            )[spec["run_num"] - 1]
            features = load_run_detections(run_dir)
            if not features:
                return gpd.GeoDataFrame(
                    columns=["geometry", "source_tile", "subtype"],
                    crs=TARGET_CRS,
                )
            deduped = deduplicate_within_pass(features)
            rows = []
            for det in deduped:
                source_tile = (
                    det["source_tiles"][0] if det["source_tiles"] else "unknown"
                )
                rows.append({
                    "geometry": ShapelyPoint(det["centroid"]),
                    "source_tile": source_tile,
                    "subtype": det["label"],
                })
            return gpd.GeoDataFrame(rows, crs=TARGET_CRS)
        elif spec["type"] == "pv":
            return build_pv_gdf(
                pv_dir / "results" / "phase2" / spec["results_subdir"],
                pv_dir / "crops" / spec["crops_subdir"],
                pv_dir / "sweeps" / "phase2" / spec["sweeps_subdir"],
            )
        else:
            raise ValueError(f"Unknown spec type: {spec['type']}")

    gdf_det_a = _build_gdf(condition_a_spec)
    gdf_det_b = _build_gdf(condition_b_spec)

    logger.info(
        "Pairwise: %s  A=%d dets, B=%d dets",
        comparison_name, len(gdf_det_a), len(gdf_det_b),
    )

    result = bootstrap_effect_size_ci(
        gdf_det_a, gdf_bounds,
        gdf_det_b, gdf_bounds,
        gdf_ref,
        n_iterations=BOOTSTRAP_ITERATIONS,
        random_seed=BOOTSTRAP_SEED,
        return_p_values=True,
    )

    # Also compute point estimates for both conditions
    if len(gdf_det_a) > 0:
        p_a, r_a, f1_a = calculate_f1_internal(
            gdf_det_a, gdf_ref, gdf_bounds,
        )
    else:
        p_a, r_a, f1_a = 0.0, 0.0, 0.0

    if len(gdf_det_b) > 0:
        p_b, r_b, f1_b = calculate_f1_internal(
            gdf_det_b, gdf_ref, gdf_bounds,
        )
    else:
        p_b, r_b, f1_b = 0.0, 0.0, 0.0

    logger.info(
        "  Result: %s  A(F1=%.4f) vs B(F1=%.4f)  deltaF1=%.4f",
        comparison_name, f1_a, f1_b,
        result.get("f1_difference", {}).get("mean", 0),
    )

    return {
        "comparison": comparison_name,
        "condition_a": condition_a_spec.get("label", "A"),
        "condition_b": condition_b_spec.get("label", "B"),
        "point_estimates_a": {
            "f1": round(f1_a, 6),
            "precision": round(p_a, 6),
            "recall": round(r_a, 6),
            "n_detections": len(gdf_det_a),
        },
        "point_estimates_b": {
            "f1": round(f1_b, 6),
            "precision": round(p_b, 6),
            "recall": round(r_b, 6),
            "n_detections": len(gdf_det_b),
        },
        "effect_size": result,
    }


# ===================================================================
# Main
# ===================================================================

def main():
    """Run the full consensus sweep and pairwise comparisons."""
    parser = argparse.ArgumentParser(
        description="Phase 3a-HIGH text consensus sweep analysis",
    )
    parser.add_argument(
        "--data-dir", type=Path, required=True,
        help="Base data directory (contains references/, bounds/, retest/)",
    )
    parser.add_argument(
        "--pv-dir", type=Path, required=True,
        help="PV data directory (contains crops/, results/, sweeps/)",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for JSON results",
    )
    parser.add_argument(
        "--workers", type=int, default=10,
        help="Number of parallel workers (default: 10)",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    high_base_dir = args.data_dir / "retest" / "phase3a-high" / "track2-text"
    min_base_dir = args.data_dir / "retest" / "phase3a" / "track2-text"

    # Validate data exists
    for temp in TEMPERATURES:
        temp_dir = high_base_dir / temp
        if not temp_dir.exists():
            logger.error("Missing HIGH directory: %s", temp_dir)
            sys.exit(1)
        n_runs = len(list(temp_dir.iterdir()))
        logger.info("HIGH %s: %d runs available", temp, n_runs)

    min_t07 = min_base_dir / "T0.7"
    if not min_t07.exists():
        logger.error("Missing minimal T0.7 directory: %s", min_t07)
        sys.exit(1)
    logger.info(
        "Minimal T0.7: %d runs available", len(list(min_t07.iterdir())),
    )

    # ---------------------------------------------------------------
    # Part 1: Full consensus sweep (135 configurations)
    # ---------------------------------------------------------------
    logger.info("=" * 70)
    logger.info("PART 1: Full consensus sweep (135 configurations)")
    logger.info("=" * 70)

    sweep_jobs = []
    for temp in TEMPERATURES:
        for pool_size, thresholds in POOL_CONFIGS.items():
            for threshold in thresholds:
                sweep_jobs.append((
                    temp, pool_size, threshold,
                    str(high_base_dir), str(args.data_dir),
                ))

    logger.info("Submitting %d consensus sweep jobs with %d workers",
                len(sweep_jobs), args.workers)

    sweep_results = []
    t0 = time.time()

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(compute_single_consensus, job): job
            for job in sweep_jobs
        }
        for i, future in enumerate(as_completed(futures), 1):
            try:
                result = future.result()
                sweep_results.append(result)
            except Exception as exc:
                job = futures[future]
                logger.error("Job %s failed: %s", job[:3], exc)

            if i % 10 == 0:
                elapsed = time.time() - t0
                logger.info(
                    "Progress: %d/%d (%.1f%%) in %.1fs",
                    i, len(sweep_jobs),
                    100 * i / len(sweep_jobs), elapsed,
                )

    elapsed = time.time() - t0
    logger.info("Sweep complete: %d results in %.1fs", len(sweep_results), elapsed)

    # Sort results for readability
    sweep_results.sort(key=lambda r: (
        r["temperature"], r["pool_size"], r["vote_threshold"],
    ))

    # Find best F1 per temperature and overall
    best_per_temp: dict[str, dict] = {}
    for r in sweep_results:
        temp = r["temperature"]
        f1 = r["point_estimates"]["f1"]
        if temp not in best_per_temp or f1 > best_per_temp[temp]["point_estimates"]["f1"]:
            best_per_temp[temp] = r

    if not sweep_results:
        logger.error("All sweep jobs failed — no results to analyse")
        sys.exit(1)

    overall_best = max(sweep_results, key=lambda r: r["point_estimates"]["f1"])

    summary = {
        "analysis": "Phase 3a-HIGH text track consensus sweep",
        "total_configurations": len(sweep_results),
        "temperatures": TEMPERATURES,
        "pool_sizes": list(POOL_CONFIGS.keys()),
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "best_per_temperature": {
            temp: {
                "config_key": r["config_key"],
                "pool_size": r["pool_size"],
                "vote_threshold": r["vote_threshold"],
                "f1": r["point_estimates"]["f1"],
                "precision": r["point_estimates"]["precision"],
                "recall": r["point_estimates"]["recall"],
                "n_detections": r["n_detections"],
                "f1_ci": r["bootstrap_ci"].get("f1", {}),
            }
            for temp, r in best_per_temp.items()
        },
        "overall_best": {
            "config_key": overall_best["config_key"],
            "temperature": overall_best["temperature"],
            "pool_size": overall_best["pool_size"],
            "vote_threshold": overall_best["vote_threshold"],
            "f1": overall_best["point_estimates"]["f1"],
            "precision": overall_best["point_estimates"]["precision"],
            "recall": overall_best["point_estimates"]["recall"],
            "n_detections": overall_best["n_detections"],
            "f1_ci": overall_best["bootstrap_ci"].get("f1", {}),
        },
        "results": sweep_results,
    }

    sweep_output = args.output_dir / "phase3a-high-text-consensus-sweep.json"
    with open(sweep_output, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    logger.info("Sweep results saved to %s", sweep_output)

    # Print summary
    logger.info("=" * 70)
    logger.info("SWEEP SUMMARY")
    logger.info("=" * 70)
    for temp in TEMPERATURES:
        if temp in best_per_temp:
            r = best_per_temp[temp]
            logger.info(
                "  %s best: N=%d threshold=%d  F1=%.4f P=%.4f R=%.4f "
                "[%.4f, %.4f] (%d dets)",
                temp, r["pool_size"], r["vote_threshold"],
                r["point_estimates"]["f1"],
                r["point_estimates"]["precision"],
                r["point_estimates"]["recall"],
                r["bootstrap_ci"].get("f1", {}).get("ci_lower", 0),
                r["bootstrap_ci"].get("f1", {}).get("ci_upper", 0),
                r["n_detections"],
            )
    logger.info(
        "  Overall best: %s  F1=%.4f",
        overall_best["config_key"],
        overall_best["point_estimates"]["f1"],
    )

    # ---------------------------------------------------------------
    # Part 2: Pairwise comparisons
    # ---------------------------------------------------------------
    logger.info("=" * 70)
    logger.info("PART 2: Pairwise comparisons")
    logger.info("=" * 70)

    # Also find best for each (temp, pool_size) combination
    best_by_temp_pool: dict[tuple, dict] = {}
    for r in sweep_results:
        key = (r["temperature"], r["pool_size"])
        f1 = r["point_estimates"]["f1"]
        if key not in best_by_temp_pool or f1 > best_by_temp_pool[key]["point_estimates"]["f1"]:
            best_by_temp_pool[key] = r

    # Build minimal consensus GDF specs (for N=30 and N=5 best-threshold)
    def _consensus_spec(
        base_dir: str, temp: str, pool_size: int, threshold: int, label: str,
    ) -> dict:
        """Build a consensus condition specification."""
        return {
            "type": "consensus",
            "base_dir": base_dir,
            "temp": temp,
            "pool_size": pool_size,
            "threshold": threshold,
            "label": label,
        }

    def _single_run_spec(
        base_dir: str, temp: str, run_num: int, label: str,
    ) -> dict:
        """Build a single-run condition specification."""
        return {
            "type": "single_run",
            "base_dir": base_dir,
            "temp": temp,
            "run_num": run_num,
            "label": label,
        }

    def _pv_spec(
        results_subdir: str, crops_subdir: str, sweeps_subdir: str, label: str,
    ) -> dict:
        """Build a PV condition specification."""
        return {
            "type": "pv",
            "results_subdir": results_subdir,
            "crops_subdir": crops_subdir,
            "sweeps_subdir": sweeps_subdir,
            "label": label,
        }

    # We need the best threshold for minimal N=30 and N=5 at T=0.7.
    # Run a quick local search to find those. But since minimal data
    # is only at T=0.7, we compute minimal best thresholds inline.
    # First, build the pairwise comparison list.

    pairwise_jobs = []

    # --- Group 1: HIGH vs Minimal at matched thresholds ---

    # HIGH T=0.7 N=30 best-threshold vs Minimal T=0.7 N=30 best-threshold
    high_t07_n30_best = best_by_temp_pool.get(("T0.7", 30), {})
    high_t07_n30_thresh = high_t07_n30_best.get("vote_threshold", 15)

    # For minimal, we need to find its best threshold too.
    # We'll use the same range and pick the best F1.
    # This is computed inside the pairwise worker, but we need the threshold
    # first. Let's pre-compute minimal best thresholds.
    # Actually, we don't know minimal best thresholds yet. We need to
    # compute them. Let's add a pre-sweep for minimal N=30 and N=5.

    # --- Pre-compute minimal best thresholds ---
    logger.info("Pre-computing minimal T=0.7 best thresholds...")

    # Load shared data once for minimal pre-computation
    gdf_ref_main, gdf_bounds_main = load_shared_data(args.data_dir)

    minimal_best_thresholds: dict[int, tuple[int, float]] = {}
    for pool_size in [5, 10, 30]:
        best_f1 = -1.0
        best_thresh = 1
        min_run_dirs = get_run_dirs(min_base_dir, "T0.7", pool_size)
        for thresh in range(1, pool_size + 1):
            gdf_c = generate_consensus_gdf(min_run_dirs, thresh)
            if len(gdf_c) > 0:
                _, _, f1 = calculate_f1_internal(
                    gdf_c, gdf_ref_main, gdf_bounds_main,
                )
            else:
                f1 = 0.0
            if f1 > best_f1:
                best_f1 = f1
                best_thresh = thresh
            logger.info(
                "  Minimal N=%d thresh=%d: F1=%.4f (%d dets)",
                pool_size, thresh, f1, len(gdf_c),
            )
        minimal_best_thresholds[pool_size] = (best_thresh, best_f1)
        logger.info(
            "  Minimal N=%d best: thresh=%d F1=%.4f",
            pool_size, best_thresh, best_f1,
        )

    # Now build the actual pairwise comparisons

    # 1a. HIGH T=0.7 N=30 best vs Minimal T=0.7 N=30 best
    min_n30_thresh, min_n30_f1 = minimal_best_thresholds[30]
    pairwise_jobs.append((
        "HIGH_T0.7_N30_best vs Minimal_T0.7_N30_best",
        _consensus_spec(
            str(high_base_dir), "T0.7", 30, high_t07_n30_thresh,
            f"HIGH T=0.7 N=30 thresh={high_t07_n30_thresh}",
        ),
        _consensus_spec(
            str(min_base_dir), "T0.7", 30, min_n30_thresh,
            f"Minimal T=0.7 N=30 thresh={min_n30_thresh}",
        ),
        str(args.data_dir), str(args.pv_dir),
        str(high_base_dir), str(min_base_dir),
    ))

    # 1b. HIGH T=0.7 N=5 best vs Minimal T=0.7 N=5 best
    high_t07_n5_best = best_by_temp_pool.get(("T0.7", 5), {})
    high_t07_n5_thresh = high_t07_n5_best.get("vote_threshold", 3)
    min_n5_thresh, min_n5_f1 = minimal_best_thresholds[5]
    pairwise_jobs.append((
        "HIGH_T0.7_N5_best vs Minimal_T0.7_N5_best",
        _consensus_spec(
            str(high_base_dir), "T0.7", 5, high_t07_n5_thresh,
            f"HIGH T=0.7 N=5 thresh={high_t07_n5_thresh}",
        ),
        _consensus_spec(
            str(min_base_dir), "T0.7", 5, min_n5_thresh,
            f"Minimal T=0.7 N=5 thresh={min_n5_thresh}",
        ),
        str(args.data_dir), str(args.pv_dir),
        str(high_base_dir), str(min_base_dir),
    ))

    # 1c. HIGH single run (T=0.7 run_1) vs Minimal single run (T=0.7 run_1)
    pairwise_jobs.append((
        "HIGH_T0.7_run1 vs Minimal_T0.7_run1",
        _single_run_spec(
            str(high_base_dir), "T0.7", 1, "HIGH T=0.7 run_1",
        ),
        _single_run_spec(
            str(min_base_dir), "T0.7", 1, "Minimal T=0.7 run_1",
        ),
        str(args.data_dir), str(args.pv_dir),
        str(high_base_dir), str(min_base_dir),
    ))

    # --- Group 2: Temperature effect within HIGH ---

    # Get best configs per temperature (use best across all pool sizes)
    temp_best_specs = {}
    for temp in TEMPERATURES:
        r = best_per_temp.get(temp, {})
        if r:
            temp_best_specs[temp] = _consensus_spec(
                str(high_base_dir), temp,
                r["pool_size"], r["vote_threshold"],
                f"HIGH {temp} N={r['pool_size']} thresh={r['vote_threshold']}",
            )

    # 2a. T=0.3 best vs T=0.7 best
    if "T0.3" in temp_best_specs and "T0.7" in temp_best_specs:
        pairwise_jobs.append((
            "HIGH_T0.3_best vs HIGH_T0.7_best",
            temp_best_specs["T0.3"],
            temp_best_specs["T0.7"],
            str(args.data_dir), str(args.pv_dir),
            str(high_base_dir), str(min_base_dir),
        ))

    # 2b. T=0.3 best vs T=1.0 best
    if "T0.3" in temp_best_specs and "T1.0" in temp_best_specs:
        pairwise_jobs.append((
            "HIGH_T0.3_best vs HIGH_T1.0_best",
            temp_best_specs["T0.3"],
            temp_best_specs["T1.0"],
            str(args.data_dir), str(args.pv_dir),
            str(high_base_dir), str(min_base_dir),
        ))

    # 2c. T=0.7 best vs T=1.0 best
    if "T0.7" in temp_best_specs and "T1.0" in temp_best_specs:
        pairwise_jobs.append((
            "HIGH_T0.7_best vs HIGH_T1.0_best",
            temp_best_specs["T0.7"],
            temp_best_specs["T1.0"],
            str(args.data_dir), str(args.pv_dir),
            str(high_base_dir), str(min_base_dir),
        ))

    # --- Group 3: HIGH consensus vs PV ---

    # 3a. HIGH N=30 best-F1 vs PV text 5-of-10 (F1=0.831)
    if overall_best:
        pairwise_jobs.append((
            "HIGH_best vs PV_text_5of10",
            _consensus_spec(
                str(high_base_dir),
                overall_best["temperature"],
                overall_best["pool_size"],
                overall_best["vote_threshold"],
                (
                    f"HIGH {overall_best['temperature']} "
                    f"N={overall_best['pool_size']} "
                    f"thresh={overall_best['vote_threshold']}"
                ),
            ),
            _pv_spec(
                "09-text-5of10", "09-text-5of10", "09-text-5of10",
                "PV text 5-of-10 (F1=0.831)",
            ),
            str(args.data_dir), str(args.pv_dir),
            str(high_base_dir), str(min_base_dir),
        ))

    # 3b. HIGH N=30 best-F1 vs PV text 3-of-10 (F1=0.823)
    if overall_best:
        pairwise_jobs.append((
            "HIGH_best vs PV_text_3of10",
            _consensus_spec(
                str(high_base_dir),
                overall_best["temperature"],
                overall_best["pool_size"],
                overall_best["vote_threshold"],
                (
                    f"HIGH {overall_best['temperature']} "
                    f"N={overall_best['pool_size']} "
                    f"thresh={overall_best['vote_threshold']}"
                ),
            ),
            _pv_spec(
                "08-text-3of10", "08-text-3of10", "08-text-3of10",
                "PV text 3-of-10 (F1=0.823)",
            ),
            str(args.data_dir), str(args.pv_dir),
            str(high_base_dir), str(min_base_dir),
        ))

    logger.info(
        "Submitting %d pairwise comparison jobs", len(pairwise_jobs),
    )

    pairwise_results = []
    t0 = time.time()

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(compute_pairwise, job): job
            for job in pairwise_jobs
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                pairwise_results.append(result)
            except Exception as exc:
                job = futures[future]
                logger.error("Pairwise job %s failed: %s", job[0], exc)

    elapsed = time.time() - t0
    logger.info(
        "Pairwise comparisons complete: %d results in %.1fs",
        len(pairwise_results), elapsed,
    )

    # Build pairwise output
    pairwise_output_data = {
        "analysis": "Phase 3a-HIGH text track pairwise comparisons",
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "minimal_best_thresholds": {
            str(k): {"threshold": v[0], "f1": round(v[1], 6)}
            for k, v in minimal_best_thresholds.items()
        },
        "comparisons": pairwise_results,
    }

    pairwise_output = args.output_dir / "phase3a-high-text-pairwise.json"
    with open(pairwise_output, "w", encoding="utf-8") as f:
        json.dump(pairwise_output_data, f, indent=2)
    logger.info("Pairwise results saved to %s", pairwise_output)

    # Print pairwise summary
    logger.info("=" * 70)
    logger.info("PAIRWISE SUMMARY")
    logger.info("=" * 70)
    for r in pairwise_results:
        effect = r["effect_size"]
        if "error" in effect:
            logger.warning(
                "  %s: ERROR — %s", r["comparison"], effect["error"],
            )
            continue
        f1_diff = effect.get("f1_difference", {})
        p_val = f1_diff.get("p_value", "N/A")
        sig = ""
        ci_lo = f1_diff.get("ci_lower", 0)
        ci_hi = f1_diff.get("ci_upper", 0)
        if ci_lo > 0 or ci_hi < 0:
            sig = " *"
        logger.info(
            "  %s: deltaF1=%.4f [%.4f, %.4f] p=%.4f%s",
            r["comparison"],
            f1_diff.get("mean", 0), ci_lo, ci_hi,
            p_val if isinstance(p_val, float) else 0,
            sig,
        )

    logger.info("=" * 70)
    logger.info("DONE. Output files:")
    logger.info("  %s", sweep_output)
    logger.info("  %s", pairwise_output)


if __name__ == "__main__":
    main()
