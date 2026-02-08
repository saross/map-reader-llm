#!/usr/bin/env python3
"""
Phase 2 Multi-Condition Analysis Script
========================================

Analyses Phase 2 sub-phase results across multiple conditions using
bootstrapped confidence intervals with Benjamini-Hochberg FDR correction.

Aligned with preregistration Section 3.5:
- Bootstrapped 95% CIs for absolute metrics and effect sizes
- FDR correction at q=0.05 for multiple pairwise comparisons
- Significance criterion: 95% CI excludes zero after FDR adjustment

Usage:
    python scripts/analyse_phase2_results.py \\
        --study-dir outputs/phase2a \\
        --ground-truth inputs/vectors/references/mounds-reference.geojson \\
        --bounds inputs/vectors/bounds/validation_bounds.geojson \\
        --conditions image-only brief-text brief-text-image verbose-text verbose-text-image

    python scripts/analyse_phase2_results.py --help

Author: Shawn Ross, Claude Code
Version: 1.0.0
Licence: Apache 2.0
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

# Add scripts directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent))
from lib_advanced_metrics import (
    bootstrap_multi_run_ci,
    bootstrap_multi_run_effect_size_ci,
    calculate_f1_internal,
)

# Script version
__version__ = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_N_BOOTSTRAP = 1000
DEFAULT_FDR_Q = 0.05
DEFAULT_BUFFER_M = 20


def load_condition_results(
    study_dir: Path,
    condition: str,
) -> list[tuple[int, gpd.GeoDataFrame]]:
    """
    Load per-run detection results for a single condition.

    Iterate run_* directories under {study_dir}/{condition}/ and load
    detection files from each. Detection files are identified by matching
    'detections_*' filenames while excluding '.meta.json', '_fp.*', and
    '_fn.*' suffixes. Files may or may not have a .geojson extension.

    Errata E21: Removed stale 'passes' parameter and pass_N subdirectory
    iteration -- the actual structure is run_K/ with no pass level (single
    pass per run, per preregistration section 3.8).

    Args:
        study_dir: Base output directory for the phase.
        condition: Condition name (e.g., 'image-only').

    Returns:
        List of (run_number, GeoDataFrame) tuples, sorted by run number.
        Return an empty list if no detection files are found.
    """
    condition_dir = study_dir / condition

    if not condition_dir.exists():
        logger.warning("Condition directory not found: %s", condition_dir)
        return []

    per_run_results: list[tuple[int, gpd.GeoDataFrame]] = []

    # Iterate run_* directories
    run_dirs = sorted(condition_dir.glob("run_*"))

    if not run_dirs:
        logger.warning("No run_* directories found for condition: %s", condition)
        return []

    for run_dir in run_dirs:
        if not run_dir.is_dir():
            continue

        # Extract run number from directory name (e.g., 'run_1' → 1)
        try:
            run_num = int(run_dir.name.split("_", 1)[1])
        except (IndexError, ValueError):
            logger.warning("Cannot parse run number from: %s", run_dir.name)
            continue

        # Find detection files: match 'detections_*' but exclude
        # .meta.json, .tiles.json, _fp.*, and _fn.* files
        detection_files = []
        for f in run_dir.iterdir():
            if not f.name.startswith("detections_"):
                continue
            if f.name.endswith((".meta.json", ".tiles.json")):
                continue
            if "_fp." in f.name or "_fn." in f.name:
                continue
            # Skip _fp or _fn suffixes without extension
            stem = f.stem if "." in f.name else f.name
            if stem.endswith(("_fp", "_fn")):
                continue
            detection_files.append(f)

        if not detection_files:
            logger.warning(
                "No detection files in %s (found %d files total)",
                run_dir,
                len(list(run_dir.iterdir())),
            )
            continue

        # Load the detection file (should be exactly one per run)
        if len(detection_files) > 1:
            logger.warning(
                "Multiple detection files in %s, using first: %s",
                run_dir,
                [f.name for f in detection_files],
            )

        det_file = detection_files[0]
        try:
            gdf = gpd.read_file(det_file)
            gdf["run"] = run_num
            per_run_results.append((run_num, gdf))
            logger.info(
                "Loaded run %d: %s (%d features)",
                run_num,
                det_file.name,
                len(gdf),
            )
        except Exception as e:
            logger.warning("Error loading %s: %s", det_file, e)

    logger.info(
        "Condition '%s': loaded %d runs with %d total features",
        condition,
        len(per_run_results),
        sum(len(gdf) for _, gdf in per_run_results),
    )
    return per_run_results


def apply_fdr_correction(
    pairwise_results: list[dict],
    q: float = 0.05,
) -> list[dict]:
    """
    Apply Benjamini-Hochberg FDR correction to pairwise comparisons.

    The B-H procedure controls the expected proportion of false discoveries
    among rejected hypotheses at level q.

    Args:
        pairwise_results: List of pairwise comparison dictionaries,
            each containing 'f1_difference' with 'ci_lower' and 'ci_upper'.
        q: FDR control level (default 0.05).

    Returns:
        Updated pairwise_results with 'fdr_significant' field added.
    """
    if not pairwise_results:
        return pairwise_results

    # Determine which comparisons are initially significant (CI excludes 0)
    # and compute pseudo-p-values based on CI position
    comparisons_with_pvalues = []

    for i, result in enumerate(pairwise_results):
        f1_diff = result.get("f1_difference", {})
        ci_lower = f1_diff.get("ci_lower", 0)
        ci_upper = f1_diff.get("ci_upper", 0)

        # Compute pseudo-p-value based on distance from zero
        # If CI contains 0, p > 0.05; otherwise scale by CI width
        if ci_lower > 0:
            # Positive effect: p-value inversely related to distance from 0
            # Approximation: smaller CI lower bound (closer to 0) = higher p-value
            pseudo_p = max(0.001, 0.05 - ci_lower)
        elif ci_upper < 0:
            # Negative effect: similar logic with absolute upper bound
            pseudo_p = max(0.001, 0.05 - abs(ci_upper))
        else:
            # CI contains 0: not significant at α=0.05
            pseudo_p = 1.0

        comparisons_with_pvalues.append({
            "index": i,
            "pseudo_p": pseudo_p,
            "initially_significant": ci_lower > 0 or ci_upper < 0,
        })

    # Sort by pseudo-p-value
    sorted_comparisons = sorted(comparisons_with_pvalues, key=lambda x: x["pseudo_p"])

    # Apply B-H procedure
    m = len(sorted_comparisons)  # Total number of comparisons
    fdr_significant_indices = set()

    for rank, comp in enumerate(sorted_comparisons, start=1):
        # B-H critical value: (rank / m) * q
        bh_critical = (rank / m) * q

        if comp["pseudo_p"] <= bh_critical:
            fdr_significant_indices.add(comp["index"])
        else:
            # Once a comparison fails, all subsequent also fail
            break

    # Update results with FDR significance
    for i, result in enumerate(pairwise_results):
        f1_diff = result.get("f1_difference", {})
        ci_lower = f1_diff.get("ci_lower", 0)
        ci_upper = f1_diff.get("ci_upper", 0)

        result["initially_significant"] = ci_lower > 0 or ci_upper < 0
        result["fdr_significant"] = i in fdr_significant_indices

    return pairwise_results


def analyse_phase_results(
    study_dir: Path,
    conditions: list[str],
    ground_truth_path: Path,
    bounds_path: Path,
    n_bootstrap: int = DEFAULT_N_BOOTSTRAP,
    fdr_q: float = DEFAULT_FDR_Q,
    random_seed: int = 42,
) -> dict:
    """
    Analyse results across multiple conditions.

    Compute per-condition metrics (F1, precision, recall) with bootstrapped
    95% CIs, all pairwise comparisons with effect sizes and CIs,
    FDR-corrected significance determinations, and a recommendation for the
    optimal condition.

    Args:
        study_dir: Base output directory for the phase.
        conditions: List of condition names to compare.
        ground_truth_path: Path to ground truth GeoJSON.
        bounds_path: Path to evaluation bounds GeoJSON.
        n_bootstrap: Number of bootstrap iterations.
        fdr_q: FDR control level (q-value).
        random_seed: Seed for reproducibility.

    Returns:
        Analysis results dictionary.
    """
    logger.info("Starting multi-condition analysis")
    logger.info("Study directory: %s", study_dir)
    logger.info("Conditions: %s", conditions)
    logger.info("Bootstrap iterations: %d", n_bootstrap)
    logger.info("FDR q-value: %.3f", fdr_q)

    # Load ground truth
    if not ground_truth_path.exists():
        return {"error": f"Ground truth not found: {ground_truth_path}"}

    gdf_ref = gpd.read_file(ground_truth_path)
    logger.info("Loaded ground truth: %d reference features", len(gdf_ref))

    # Load common bounds
    if not bounds_path.exists():
        return {"error": f"Bounds not found: {bounds_path}"}

    gdf_bounds_common = gpd.read_file(bounds_path)
    logger.info("Loaded bounds: %d tiles", len(gdf_bounds_common))

    # Standardise CRS
    target_crs = "EPSG:32635"
    if gdf_ref.crs != target_crs:
        gdf_ref = gdf_ref.to_crs(target_crs)
    if gdf_bounds_common.crs != target_crs:
        gdf_bounds_common = gdf_bounds_common.to_crs(target_crs)

    # Load and analyse each condition (per-run evaluation — errata E22)
    per_condition_metrics = {}
    condition_data = {}  # Store per-run GeoDataFrames for pairwise comparisons
    per_run_metrics_rows = []  # For intermediate CSV output

    for condition in conditions:
        logger.info("Analysing condition: %s", condition)

        run_results = load_condition_results(study_dir, condition)

        if not run_results:
            logger.warning("Skipping condition %s: no data found", condition)
            per_condition_metrics[condition] = {"error": "No data found"}
            continue

        # Standardise CRS for each run's GeoDataFrame
        standardised_runs: list[tuple[int, gpd.GeoDataFrame]] = []
        for run_num, gdf in run_results:
            if gdf.crs != target_crs:
                gdf = gdf.to_crs(target_crs)
            standardised_runs.append((run_num, gdf))

        # Store per-run data for pairwise comparisons
        condition_data[condition] = {
            "runs": standardised_runs,
            "bounds": gdf_bounds_common,
        }

        # Compute F1 per run independently
        run_f1s = []
        run_precisions = []
        run_recalls = []
        n_total_detections = 0

        for run_num, gdf_det in standardised_runs:
            n_total_detections += len(gdf_det)
            precision, recall, f1 = calculate_f1_internal(
                gdf_det, gdf_ref, gdf_bounds_common,
                buffer_metres=DEFAULT_BUFFER_M,
            )
            run_f1s.append(f1)
            run_precisions.append(precision)
            run_recalls.append(recall)

            # Record for intermediate CSV
            per_run_metrics_rows.append({
                "condition": condition,
                "run": run_num,
                "f1": round(f1, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "n_detections": len(gdf_det),
            })

            logger.info(
                "  Run %d: F1=%.4f, P=%.4f, R=%.4f (%d features)",
                run_num, f1, precision, recall, len(gdf_det),
            )

        # Mean across runs (point estimate)
        mean_f1 = float(np.mean(run_f1s))
        mean_precision = float(np.mean(run_precisions))
        mean_recall = float(np.mean(run_recalls))

        # Multi-run bootstrap CIs (tile as resampling unit, averaged
        # across K runs — see bootstrap_multi_run_ci docstring)
        ci_results = bootstrap_multi_run_ci(
            run_gdfs=standardised_runs,
            gdf_ref=gdf_ref,
            gdf_bounds=gdf_bounds_common,
            n_iterations=n_bootstrap,
            random_seed=random_seed,
        )

        per_condition_metrics[condition] = {
            "n_runs": len(standardised_runs),
            "n_detections_total": n_total_detections,
            "per_run_f1": [round(f, 4) for f in run_f1s],
            "point_estimate": {
                "f1": round(mean_f1, 4),
                "precision": round(mean_precision, 4),
                "recall": round(mean_recall, 4),
            },
            "bootstrap_ci": ci_results,
        }

        logger.info(
            "  Mean F1=%.4f [%.4f, %.4f], P=%.4f, R=%.4f (%d runs)",
            mean_f1,
            ci_results.get("f1", {}).get("ci_lower", 0),
            ci_results.get("f1", {}).get("ci_upper", 0),
            mean_precision,
            mean_recall,
            len(standardised_runs),
        )

    # Save per-run metrics CSV
    if per_run_metrics_rows:
        csv_path = study_dir / "per_run_metrics.csv"
        df_metrics = pd.DataFrame(per_run_metrics_rows)
        df_metrics.to_csv(csv_path, index=False)
        logger.info("Saved per-run metrics to: %s", csv_path)

    # Compute all pairwise comparisons using multi-run bootstrap
    pairwise_comparisons = []
    valid_conditions = [c for c in conditions if c in condition_data]

    for cond_a, cond_b in combinations(valid_conditions, 2):
        logger.info("Computing effect size: %s vs %s", cond_a, cond_b)

        effect = bootstrap_multi_run_effect_size_ci(
            run_gdfs_a=condition_data[cond_a]["runs"],
            run_gdfs_b=condition_data[cond_b]["runs"],
            gdf_ref=gdf_ref,
            gdf_bounds=gdf_bounds_common,
            n_iterations=n_bootstrap,
            random_seed=random_seed,
        )

        pairwise_comparisons.append({
            "condition_a": cond_a,
            "condition_b": cond_b,
            **effect,
        })

    # Apply FDR correction
    pairwise_comparisons = apply_fdr_correction(pairwise_comparisons, q=fdr_q)

    # Determine optimal condition (highest mean F1)
    best_condition = None
    best_f1 = -1

    for condition, metrics in per_condition_metrics.items():
        if "error" in metrics:
            continue
        mean_f1 = metrics.get("bootstrap_ci", {}).get("f1", {}).get("mean", 0)
        if mean_f1 > best_f1:
            best_f1 = mean_f1
            best_condition = condition

    # Count significant differences
    n_comparisons = len(pairwise_comparisons)
    n_initially_sig = sum(1 for p in pairwise_comparisons if p.get("initially_significant"))
    n_fdr_sig = sum(1 for p in pairwise_comparisons if p.get("fdr_significant"))

    # Build recommendation
    recommendation = f"Optimal condition: {best_condition} (mean F1 = {best_f1:.4f})"
    if n_fdr_sig > 0:
        recommendation += (
            f"\n{n_fdr_sig}/{n_comparisons} pairwise differences"
            f" significant after FDR correction."
        )
    else:
        recommendation += f"\nNo pairwise differences significant after FDR correction (q={fdr_q})."

    return {
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "study_dir": str(study_dir),
        "n_conditions": len(conditions),
        "n_bootstrap": n_bootstrap,
        "fdr_q": fdr_q,
        "per_condition_metrics": per_condition_metrics,
        "pairwise_comparisons": pairwise_comparisons,
        "n_comparisons": n_comparisons,
        "n_initially_significant": n_initially_sig,
        "n_fdr_significant": n_fdr_sig,
        "optimal_condition": best_condition,
        "optimal_f1": best_f1,
        "recommendation": recommendation,
    }


def generate_markdown_summary(results: dict) -> str:
    """
    Generate a markdown summary of the analysis results.

    Args:
        results: Analysis results dictionary.

    Returns:
        Markdown-formatted summary string.
    """
    lines = [
        "# Phase 2 Analysis Summary",
        "",
        f"**Generated**: {results.get('analysis_timestamp', 'N/A')}",
        f"**Study Directory**: `{results.get('study_dir', 'N/A')}`",
        f"**Bootstrap Iterations**: {results.get('n_bootstrap', 'N/A')}",
        f"**FDR q-value**: {results.get('fdr_q', 'N/A')}",
        "",
        "## Per-Condition Metrics",
        "",
        "| Condition | F1 | 95% CI | Precision | Recall |",
        "|-----------|---:|:------:|----------:|-------:|",
    ]

    for condition, metrics in results.get("per_condition_metrics", {}).items():
        if "error" in metrics:
            lines.append(f"| {condition} | - | Error: {metrics['error']} | - | - |")
            continue

        point = metrics.get("point_estimate", {})
        ci = metrics.get("bootstrap_ci", {}).get("f1", {})
        ci_str = f"[{ci.get('ci_lower', 0):.3f}, {ci.get('ci_upper', 0):.3f}]"

        lines.append(
            f"| {condition} | {point.get('f1', 0):.4f} | {ci_str} | "
            f"{point.get('precision', 0):.4f} | {point.get('recall', 0):.4f} |"
        )

    lines.extend([
        "",
        "## Pairwise Comparisons",
        "",
        "| Comparison | ΔF1 | 95% CI | Initial Sig | FDR Sig |",
        "|------------|----:|:------:|:-----------:|:-------:|",
    ])

    for comp in results.get("pairwise_comparisons", []):
        cond_a = comp.get("condition_a", "?")
        cond_b = comp.get("condition_b", "?")
        f1_diff = comp.get("f1_difference", {})
        mean_diff = f1_diff.get("mean", 0)
        ci_str = f"[{f1_diff.get('ci_lower', 0):+.3f}, {f1_diff.get('ci_upper', 0):+.3f}]"
        init_sig = "✓" if comp.get("initially_significant") else ""
        fdr_sig = "✓" if comp.get("fdr_significant") else ""

        lines.append(
            f"| {cond_a} vs {cond_b} | {mean_diff:+.4f} | {ci_str} | {init_sig} | {fdr_sig} |"
        )

    lines.extend([
        "",
        "## Summary Statistics",
        "",
        f"- **Total comparisons**: {results.get('n_comparisons', 0)}",
        f"- **Initially significant**: {results.get('n_initially_significant', 0)}",
        f"- **FDR significant**: {results.get('n_fdr_significant', 0)}",
        "",
        "## Recommendation",
        "",
        results.get("recommendation", "No recommendation available."),
        "",
    ])

    return "\n".join(lines)


def print_summary(results: dict) -> None:
    """Print a formatted console summary of the analysis results to stdout."""
    print("\n" + "=" * 70)
    print(" Phase 2 Multi-Condition Analysis Results")
    print("=" * 70)

    print(f"\nStudy directory: {results.get('study_dir', 'N/A')}")
    print(f"Bootstrap iterations: {results.get('n_bootstrap', 'N/A')}")
    print(f"FDR q-value: {results.get('fdr_q', 'N/A')}")

    # Per-condition metrics
    print("\n" + "-" * 70)
    print(" Per-Condition Metrics")
    print("-" * 70)
    print(f"  {'Condition':<25} {'F1':>8} {'95% CI':>20} {'P':>8} {'R':>8}")
    print(f"  {'-'*25} {'-'*8} {'-'*20} {'-'*8} {'-'*8}")

    for condition, metrics in results.get("per_condition_metrics", {}).items():
        if "error" in metrics:
            print(f"  {condition:<25} ERROR: {metrics['error']}")
            continue

        point = metrics.get("point_estimate", {})
        ci = metrics.get("bootstrap_ci", {}).get("f1", {})
        ci_str = f"[{ci.get('ci_lower', 0):.3f}, {ci.get('ci_upper', 0):.3f}]"

        # Mark optimal condition
        marker = " *" if condition == results.get("optimal_condition") else ""

        print(
            f"  {condition:<25} {point.get('f1', 0):>8.4f} {ci_str:>20} "
            f"{point.get('precision', 0):>8.4f} {point.get('recall', 0):>8.4f}{marker}"
        )

    print("\n  * = Optimal condition (highest mean F1)")

    # Pairwise comparisons
    print("\n" + "-" * 70)
    print(" Pairwise Comparisons (FDR-corrected)")
    print("-" * 70)
    print(f"  {'Comparison':<35} {'ΔF1':>8} {'95% CI':>20} {'Sig':>6}")
    print(f"  {'-'*35} {'-'*8} {'-'*20} {'-'*6}")

    for comp in results.get("pairwise_comparisons", []):
        cond_a = comp.get("condition_a", "?")
        cond_b = comp.get("condition_b", "?")
        comparison_name = f"{cond_a} vs {cond_b}"

        f1_diff = comp.get("f1_difference", {})
        mean_diff = f1_diff.get("mean", 0)
        ci_str = f"[{f1_diff.get('ci_lower', 0):+.3f}, {f1_diff.get('ci_upper', 0):+.3f}]"

        sig = "*" if comp.get("fdr_significant") else ""

        print(f"  {comparison_name:<35} {mean_diff:>+8.4f} {ci_str:>20} {sig:>6}")

    # Summary
    print("\n" + "-" * 70)
    print(" Summary")
    print("-" * 70)
    print(f"  Total comparisons: {results.get('n_comparisons', 0)}")
    print(f"  Initially significant (α=0.05): {results.get('n_initially_significant', 0)}")
    fdr_q = results.get('fdr_q', 0.05)
    n_fdr_sig = results.get('n_fdr_significant', 0)
    print(f"  FDR significant (q={fdr_q}): {n_fdr_sig}")

    print("\n" + "-" * 70)
    print(" Recommendation")
    print("-" * 70)
    for line in results.get("recommendation", "").split("\n"):
        print(f"  {line}")

    print("\n" + "=" * 70 + "\n")


def main() -> int:
    """Run the Phase 2 multi-condition analysis from command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyse Phase 2 results across multiple conditions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyse Phase 2a (H1 Modality/Elaboration)
  python scripts/analyse_phase2_results.py \\
      --study-dir outputs/phase2a \\
      --ground-truth inputs/vectors/references/mounds-reference.geojson \\
      --bounds inputs/vectors/bounds/validation_bounds.geojson \\
      --conditions image-only brief-text brief-text-image verbose-text verbose-text-image

  # Analyse Phase 2b (H7 Temperature)
  python scripts/analyse_phase2_results.py \\
      --study-dir outputs/phase2b \\
      --conditions T0.0 T0.3 T0.7 T1.0 T1.3

  # Use fewer bootstrap iterations for quick testing
  python scripts/analyse_phase2_results.py \\
      --study-dir outputs/phase2a \\
      --conditions image-only brief-text \\
      --bootstrap 100
        """,
    )

    parser.add_argument(
        "--study-dir",
        type=Path,
        required=True,
        help="Base output directory for the phase (e.g., outputs/phase2a)",
    )
    parser.add_argument(
        "--ground-truth",
        type=Path,
        default=Path("inputs/vectors/references/mounds-reference.geojson"),
        help="Path to ground truth GeoJSON",
    )
    parser.add_argument(
        "--bounds",
        type=Path,
        default=Path("inputs/vectors/bounds/validation_bounds.geojson"),
        help="Path to evaluation bounds GeoJSON",
    )
    parser.add_argument(
        "--conditions",
        nargs="+",
        required=True,
        help="List of condition names to compare",
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=DEFAULT_N_BOOTSTRAP,
        help=f"Number of bootstrap iterations (default: {DEFAULT_N_BOOTSTRAP})",
    )
    parser.add_argument(
        "--fdr-q",
        type=float,
        default=DEFAULT_FDR_Q,
        help=f"FDR q-value for multiple comparison correction (default: {DEFAULT_FDR_Q})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file for detailed results (optional)",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        help="Output markdown summary file (optional)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Run analysis
    results = analyse_phase_results(
        study_dir=args.study_dir,
        conditions=args.conditions,
        ground_truth_path=args.ground_truth,
        bounds_path=args.bounds,
        n_bootstrap=args.bootstrap,
        fdr_q=args.fdr_q,
        random_seed=args.seed,
    )

    # Check for errors
    if "error" in results:
        logger.error("Analysis failed: %s", results["error"])
        sys.exit(1)

    # Print console summary
    if not args.quiet:
        print_summary(results)

    # Save JSON output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logger.info("Saved JSON results to: %s", args.output)

    # Save markdown summary
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        md_content = generate_markdown_summary(results)
        with open(args.markdown, "w") as f:
            f.write(md_content)
        logger.info("Saved markdown summary to: %s", args.markdown)

    # Default output locations if not specified
    if not args.output and not args.markdown:
        default_json = args.study_dir / "analysis_report.json"
        default_md = args.study_dir / "analysis_summary.md"

        default_json.parent.mkdir(parents=True, exist_ok=True)

        with open(default_json, "w") as f:
            json.dump(results, f, indent=2)
        logger.info("Saved JSON results to: %s", default_json)

        with open(default_md, "w") as f:
            f.write(generate_markdown_summary(results))
        logger.info("Saved markdown summary to: %s", default_md)

    return 0


if __name__ == "__main__":
    sys.exit(main())
