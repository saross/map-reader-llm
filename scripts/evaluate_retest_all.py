#!/usr/bin/env python3
"""
Comprehensive evaluation of all completed retest phases.

Evaluates every condition across Phases 2a–2e and 3a with:
  - F1, precision, recall (point estimates)
  - 95% bootstrap confidence intervals (1,000 iterations)
  - Pairwise bootstrap effect size CIs between conditions within each phase

For Phase 3a (consensus voting with K=30 runs), evaluates individual runs
and reports per-condition distributions.

Usage::

    python scripts/evaluate_retest_all.py
    python scripts/evaluate_retest_all.py --output results/retest/full-evaluation.json

Created: 2026-03-17
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib_advanced_metrics import (
    DEFAULT_CRS,
    bootstrap_ci,
    bootstrap_effect_size_ci,
    calculate_f1_internal,
    load_data,
)

# ── Paths ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
FULL_BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/full_evaluation_bounds.geojson"
RETEST_DIR = PROJECT_ROOT / "outputs/retest"

BOOTSTRAP_ITERATIONS = 1000
RANDOM_SEED = 42


def load_detections(path: Path) -> gpd.GeoDataFrame:
    """Load a detections GeoJSON and set Coordinate Reference System (CRS)."""
    gdf = gpd.read_file(path)
    if not gdf.empty:
        gdf.set_crs(DEFAULT_CRS, allow_override=True, inplace=True)
        if "source_tile" not in gdf.columns and "source_tiles" in gdf.columns:
            gdf["source_tile"] = gdf["source_tiles"].apply(
                lambda x: x[0] if hasattr(x, "__getitem__") and len(x) > 0
                else str(x)
            )
    return gdf



def evaluate_condition(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_runs: int = 1,
) -> dict:
    """Evaluate a single condition (possibly averaged across runs).

    For multi-run conditions, point estimates are computed per-run and
    averaged. Bootstrap CIs use a single representative run (run 1) to
    avoid inflating sample sizes.

    Args:
        gdf_det: Detections GeoDataFrame (single run for CI computation).
        gdf_ref: Ground truth GeoDataFrame.
        gdf_bounds: Bounds GeoDataFrame.
        n_runs: Number of runs (for informational reporting).

    Returns:
        Dictionary with F1, precision, recall, and bootstrap CIs.
    """
    p, r, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

    ci = bootstrap_ci(
        gdf_det, gdf_ref, gdf_bounds,
        n_iterations=BOOTSTRAP_ITERATIONS,
        random_seed=RANDOM_SEED,
    )

    return {
        "f1": f1,
        "precision": p,
        "recall": r,
        "n_runs": n_runs,
        "n_detections": len(gdf_det),
        "f1_ci": ci.get("f1", {}),
        "precision_ci": ci.get("precision", {}),
        "recall_ci": ci.get("recall", {}),
    }


def evaluate_multi_run_condition(
    run_gdfs: list[gpd.GeoDataFrame],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict:
    """Evaluate a condition with multiple independent runs.

    Computes per-run metrics and reports mean/std. Uses the first run
    for bootstrap CIs (representative sample).

    Args:
        run_gdfs: List of GeoDataFrames, one per run.
        gdf_ref: Ground truth GeoDataFrame.
        gdf_bounds: Bounds GeoDataFrame.

    Returns:
        Dictionary with per-run metrics, mean/std, and bootstrap CIs.
    """
    run_metrics = []
    for gdf in run_gdfs:
        p, r, f1 = calculate_f1_internal(gdf, gdf_ref, gdf_bounds)
        run_metrics.append({"f1": f1, "precision": p, "recall": r})

    f1s = [m["f1"] for m in run_metrics]
    ps = [m["precision"] for m in run_metrics]
    rs = [m["recall"] for m in run_metrics]

    # Bootstrap CI on first run (representative)
    ci = bootstrap_ci(
        run_gdfs[0], gdf_ref, gdf_bounds,
        n_iterations=BOOTSTRAP_ITERATIONS,
        random_seed=RANDOM_SEED,
    )

    return {
        "f1": float(np.mean(f1s)),
        "precision": float(np.mean(ps)),
        "recall": float(np.mean(rs)),
        "f1_std": float(np.std(f1s, ddof=1)) if len(f1s) > 1 else 0.0,
        "precision_std": float(np.std(ps, ddof=1)) if len(ps) > 1 else 0.0,
        "recall_std": float(np.std(rs, ddof=1)) if len(rs) > 1 else 0.0,
        "n_runs": len(run_gdfs),
        "n_detections": sum(len(g) for g in run_gdfs),
        "per_run": run_metrics,
        "f1_ci": ci.get("f1", {}),
        "precision_ci": ci.get("precision", {}),
        "recall_ci": ci.get("recall", {}),
    }


def find_condition_geojsons(phase_dir: Path) -> dict[str, list[Path]]:
    """Discover condition directories and their detection GeoJSON files.

    Expects structure: phase_dir/{condition_name}/run_{N}/detections_*.geojson

    Returns:
        Dictionary mapping condition name to list of GeoJSON paths (sorted
        by run number).
    """
    conditions = {}
    for child in sorted(phase_dir.iterdir()):
        if not child.is_dir():
            continue
        # Skip non-condition directories
        if child.name in ("checkpoint.json", "study_manifest.json", "batch_working"):
            continue

        geojsons = sorted(child.rglob("detections_*.geojson"))
        if geojsons:
            conditions[child.name] = geojsons
    return conditions


def pairwise_effect_sizes(
    condition_gdfs: dict[str, gpd.GeoDataFrame],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> list[dict]:
    """Compute pairwise bootstrap effect size CIs between conditions.

    Args:
        condition_gdfs: Dictionary mapping condition name to its
            representative GeoDataFrame (single run).
        gdf_ref: Ground truth GeoDataFrame.
        gdf_bounds: Bounds GeoDataFrame.

    Returns:
        List of dictionaries with pairwise comparison results.
    """
    results = []
    names = sorted(condition_gdfs.keys())
    for name_a, name_b in combinations(names, 2):
        gdf_a = condition_gdfs[name_a]
        gdf_b = condition_gdfs[name_b]

        effect = bootstrap_effect_size_ci(
            gdf_a, gdf_bounds,
            gdf_b, gdf_bounds,
            gdf_ref,
            n_iterations=BOOTSTRAP_ITERATIONS,
            random_seed=RANDOM_SEED,
        )

        f1_diff = effect.get("f1_difference", {})
        significant = (
            f1_diff.get("ci_lower", 0) > 0 or f1_diff.get("ci_upper", 0) < 0
        )

        results.append({
            "condition_a": name_a,
            "condition_b": name_b,
            "f1_difference": f1_diff,
            "precision_difference": effect.get("precision_difference", {}),
            "recall_difference": effect.get("recall_difference", {}),
            "significant": significant,
        })
    return results


def print_phase_results(
    phase_name: str,
    condition_results: dict[str, dict],
    pairwise: list[dict],
) -> None:
    """Print formatted results for a phase.

    Args:
        phase_name: Display name for the phase.
        condition_results: Dictionary mapping condition name to its
            evaluation results.
        pairwise: List of pairwise comparison results.
    """
    print(f"\n{'=' * 70}")
    print(f"  {phase_name}")
    print(f"{'=' * 70}")

    # Condition table
    print(f"\n  {'Condition':<25} {'F1':>8} {'Prec':>8} {'Rec':>8} "
          f"{'F1 95% CI':>20} {'Runs':>5}")
    print(f"  {'-' * 25} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 20} {'-' * 5}")

    for name in sorted(condition_results.keys()):
        r = condition_results[name]
        ci = r.get("f1_ci", {})
        ci_str = (
            f"[{ci.get('ci_lower', 0):.4f}, {ci.get('ci_upper', 0):.4f}]"
            if ci else "N/A"
        )
        print(
            f"  {name:<25} {r['f1']:>8.4f} {r['precision']:>8.4f} "
            f"{r['recall']:>8.4f} {ci_str:>20} {r.get('n_runs', 1):>5}"
        )

    # Pairwise comparisons
    if pairwise:
        print("\n  Pairwise F1 differences (A - B):")
        print(f"  {'A vs B':<40} {'Delta':>8} {'95% CI':>20} {'Sig?':>5}")
        print(f"  {'-' * 40} {'-' * 8} {'-' * 20} {'-' * 5}")
        for pw in pairwise:
            diff = pw["f1_difference"]
            ci_str = (
                f"[{diff.get('ci_lower', 0):+.4f}, {diff.get('ci_upper', 0):+.4f}]"
            )
            sig = "YES" if pw["significant"] else "no"
            label = f"{pw['condition_a']} vs {pw['condition_b']}"
            print(
                f"  {label:<40} {diff.get('mean', 0):>+8.4f} "
                f"{ci_str:>20} {sig:>5}"
            )


def evaluate_ofat_phase(
    phase_dir: Path,
    phase_name: str,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict:
    """Evaluate a single One-Factor-At-a-Time (OFAT) retest phase.

    Handles both single-run and multi-run conditions. For multi-run
    conditions (≥2 runs), reports mean metrics with standard deviation.
    Bootstrap CIs use the first run as representative sample.

    Args:
        phase_dir: Path to phase output directory.
        phase_name: Display name for printing.
        gdf_ref: Ground truth GeoDataFrame.
        gdf_bounds: Bounds GeoDataFrame.

    Returns:
        Dictionary with condition results and pairwise comparisons.
    """
    conditions = find_condition_geojsons(phase_dir)
    if not conditions:
        print(f"  No conditions found in {phase_dir}")
        return {}

    condition_results = {}
    # For pairwise: use first run's GeoDataFrame per condition
    representative_gdfs = {}

    for name, geojson_paths in sorted(conditions.items()):
        run_gdfs = [load_detections(p) for p in geojson_paths]
        run_gdfs = [g for g in run_gdfs if not g.empty]

        if not run_gdfs:
            continue

        if len(run_gdfs) == 1:
            result = evaluate_condition(
                run_gdfs[0], gdf_ref, gdf_bounds, n_runs=1,
            )
        else:
            result = evaluate_multi_run_condition(
                run_gdfs, gdf_ref, gdf_bounds,
            )

        representative_gdfs[name] = run_gdfs[0]
        condition_results[name] = result

    # Pairwise comparisons
    pw = pairwise_effect_sizes(representative_gdfs, gdf_ref, gdf_bounds)

    print_phase_results(phase_name, condition_results, pw)

    return {
        "conditions": condition_results,
        "pairwise": pw,
    }


def evaluate_phase3a(
    track_dir: Path,
    track_name: str,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> dict:
    """Evaluate Phase 3a consensus voting track (K=30 runs per temperature).

    For each temperature condition, evaluates all 30 runs individually
    and reports the distribution of F1/precision/recall across runs.

    Args:
        track_dir: Path to track output directory (e.g., track1-image/).
        track_name: Display name for printing.
        gdf_ref: Ground truth GeoDataFrame.
        gdf_bounds: Bounds GeoDataFrame.

    Returns:
        Dictionary with per-condition run distributions and pairwise
        comparisons.
    """
    conditions = find_condition_geojsons(track_dir)
    if not conditions:
        print(f"  No conditions found in {track_dir}")
        return {}

    condition_results = {}
    representative_gdfs = {}

    for name, geojson_paths in sorted(conditions.items()):
        run_gdfs = [load_detections(p) for p in geojson_paths]
        run_gdfs = [g for g in run_gdfs if not g.empty]

        if not run_gdfs:
            continue

        result = evaluate_multi_run_condition(run_gdfs, gdf_ref, gdf_bounds)
        condition_results[name] = result
        representative_gdfs[name] = run_gdfs[0]

    # Pairwise comparisons between temperature levels
    pw = pairwise_effect_sizes(representative_gdfs, gdf_ref, gdf_bounds)

    print_phase_results(track_name, condition_results, pw)

    return {
        "conditions": condition_results,
        "pairwise": pw,
    }


def main() -> None:
    """Run comprehensive evaluation of all completed retest phases."""
    parser = argparse.ArgumentParser(
        description="Comprehensive evaluation of all completed retest phases",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Export results to JSON file",
    )
    parser.add_argument(
        "--phase",
        type=str,
        help="Evaluate only this phase (e.g., 'phase2a', 'phase3a-track2')",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  Comprehensive Retest Evaluation")
    print("  340-tile full-corpus evaluation with bootstrap CIs")
    print("=" * 70)

    t_start = time.time()

    # Load shared data
    print("\nLoading ground truth and bounds...")
    _, gdf_bounds, gdf_ref = load_data(
        str(GROUND_TRUTH), str(FULL_BOUNDS),
    )
    if gdf_ref is None or gdf_bounds is None:
        print("  ERROR: Failed to load ground truth or bounds. Exiting.")
        sys.exit(1)
    print(f"  Reference mounds: {len(gdf_ref)}")
    print(f"  Evaluation tiles: {len(gdf_bounds)}")

    all_results = {}

    # ── Phase 2a: H1 Modality/Elaboration ──────────────────
    phase_dirs = [
        ("phase2a", "Phase 2a: H1 Modality/Elaboration"),
        ("phase2b/track1-image", "Phase 2b Track 1: H7 Temperature (Image)"),
        ("phase2b/track2-text", "Phase 2b Track 2: H7 Temperature (Text)"),
        ("phase2c/track1-image", "Phase 2c Track 1: H8 Library (Image)"),
        ("phase2c/track2-text", "Phase 2c Track 2: H8 Library (Text)"),
        ("phase2c/track1-image-exploratory",
         "Phase 2c Exploratory: Pure-Positive HP Scaling"),
        ("phase2d/track1-image",
         "Phase 2d Track 1: H5 Negative Text (Image)"),
        ("phase2d/track2-text",
         "Phase 2d Track 2: H5 Negative Text (Text)"),
        ("phase2e", "Phase 2e: H4 Example Ordering"),
    ]

    for subdir, name in phase_dirs:
        phase_key = subdir.replace("/", "-")
        if args.phase and args.phase != phase_key:
            continue
        d = RETEST_DIR / subdir
        if d.exists():
            print(f"\n  Evaluating {name}...")
            t0 = time.time()
            all_results[phase_key] = evaluate_ofat_phase(
                d, name, gdf_ref, gdf_bounds,
            )
            elapsed = time.time() - t0
            print(f"  [{elapsed:.1f}s]")

    # ── Phase 3a: H3 Consensus Voting ──────────────────────
    phase3a_tracks = [
        ("phase3a/track1-image",
         "Phase 3a Track 1: H3 Consensus Voting (Image, K=30)"),
        ("phase3a/track2-text",
         "Phase 3a Track 2: H3 Consensus Voting (Text, K=30)"),
    ]

    for subdir, name in phase3a_tracks:
        phase_key = subdir.replace("/", "-")
        if args.phase and args.phase not in (phase_key, "phase3a"):
            continue
        d = RETEST_DIR / subdir
        if d.exists():
            print(f"\n  Evaluating {name}...")
            t0 = time.time()
            all_results[phase_key] = evaluate_phase3a(
                d, name, gdf_ref, gdf_bounds,
            )
            elapsed = time.time() - t0
            print(f"  [{elapsed:.1f}s]")

    # ── Summary ────────────────────────────────────────────
    total_elapsed = time.time() - t_start
    print(f"\n{'=' * 70}")
    print(f"  Evaluation complete in {total_elapsed:.0f}s "
          f"({total_elapsed / 60:.1f} min)")
    print(f"{'=' * 70}")

    # Export results
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\n  Results exported to: {args.output}")


if __name__ == "__main__":
    main()
