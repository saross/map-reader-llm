#!/usr/bin/env python3
"""
Consensus Analysis & Scoring Script
===================================

Description:
    Analytical tools for consensus voting analysis of Vision Language
    Model (VLM) burial mound detections:

    1. Two-Stage Pipeline Analysis (analyse_consensus):
       Analyses the Proposer + Verifier pipeline with 2D grid search
       over proposer and verifier vote thresholds.

    2. Single-Stage Threshold Sweep (analyse_threshold_sweep):
       Sweeps vote thresholds across multiple pool sizes (N=5, 10, 30)
       to find the optimal (N, T) combination. Used for H3 hypothesis
       testing.

Usage:
    # Two-stage pipeline analysis
    python scripts/7_analyse_consensus.py \\
        --pred outputs/results/verified.geojson \\
        --bounds inputs/vectors/bounds/validation_bounds.geojson \\
        --template inputs/vectors/references/mounds-reference.geojson \\
        --iterations 5

    # Single-stage threshold sweep (H3)
    python scripts/7_analyse_consensus.py \\
        --pred outputs/phase3a/merged_detections.geojson \\
        --bounds inputs/vectors/bounds/validation_bounds.geojson \\
        --template inputs/vectors/references/mounds-reference.geojson \\
        --threshold-sweep \\
        --max-n 30 \\
        --output outputs/phase3a/threshold_sweep.json

Arguments:
    --pred: Path to the predicted GeoJSON.
    --bounds: GeoJSON defining the valid study area.
    --template: Ground truth GeoJSON.
    --iterations: Max verifier iterations for two-stage analysis
        (default: 5).
    --threshold-sweep: Enable single-stage threshold sweep mode.
    --max-n: Maximum N for threshold sweep (default: 30).
    --output: Output path for threshold sweep results
        (JavaScript Object Notation (JSON)).
    --cost-per-call: Cost per Application Programming Interface (API)
        call in USD for efficiency calculation (default: 0.003).

Methodology:
    Uses lib_advanced_metrics for one-to-one detection matching via
    the Hungarian algorithm with a 20 m spatial tolerance (centroid
    distance), ensuring consistency with F1 evaluation.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

from scripts.lib_advanced_metrics import calculate_f1_internal, load_data


def _check_first_pass(row: pd.Series) -> bool:
    """Check whether the first verifier pass returned verified=True.

    Args:
        row: A DataFrame row expected to contain a "verifier_results"
            column holding a list of result dicts.

    Returns:
        True if the first verifier result has verified=True.
    """
    res = row.get("verifier_results")
    if not res or not isinstance(res, list) or len(res) == 0:
        return False
    return res[0].get("verified", False)


def analyse_consensus(
    pred_path: Path | str,
    bounds_path: Path | str,
    template_path: Path | str,
    iterations: int = 5,
    buffer_metres: float = 20,
) -> None:
    """Analyse consensus voting thresholds for the two-stage pipeline.

    Performs a 2D grid search over proposer vote thresholds (1-5) and
    verifier vote thresholds (1-iterations) to find optimal consensus
    settings.

    Args:
        pred_path: Path to the union predictions GeoJSON (containing
            proposer_votes and verifier_votes).
        bounds_path: Path to the tile bounds GeoJSON.
        template_path: Path to the ground truth reference GeoJSON.
        iterations: Maximum number of verifier iterations to simulate
            (default: 5).
        buffer_metres: Spatial matching tolerance in metres (default: 20).
    """
    print(f"Analysing Consensus: {pred_path}")

    # 1. Load ground truth
    try:
        _, gdf_bounds, gdf_ref = load_data(template_path, bounds_path)
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return

    # 2. Load consensus predictions
    try:
        gdf_pred = gpd.read_file(pred_path)
        # Standardise Coordinate Reference System (CRS)
        if not gdf_pred.empty:
            gdf_pred.set_crs(
                "EPSG:32635", allow_override=True, inplace=True,
            )
            if gdf_pred.crs != gdf_ref.crs:
                gdf_pred = gdf_pred.to_crs(gdf_ref.crs)
    except Exception as e:
        print(f"Error loading predictions: {e}")
        return

    print(f"Total Union Candidates: {len(gdf_pred)}")

    # 3. Simulate vote thresholds (2D grid)
    # Proposer threshold (1-5) x Verifier threshold (1-5)
    header = (
        f"{'Prop Votes':<10} | {'Verif Votes':<10} | "
        f"{'Recall':<10} | {'Precision':<10} | "
        f"{'F1 Score':<10} | {'Count':<10}"
    )
    print(f"\n{header}")
    print("-" * 80)

    # Analyse "Proposer Consensus" against "Single-Pass Verifier" (simulated).
    # This answers: "Does Proposer 2-of-5 -> Standard Verifier improve?"
    print(
        "\n--- Experiment: Proposer Consensus + "
        "Single-Pass Verifier (v4.5) ---"
    )
    exp_header = (
        f"{'Prop Votes':<10} | {'Strategy':<15} | "
        f"{'Recall':<10} | {'Precision':<10} | "
        f"{'F1 Score':<10} | {'Count':<10}"
    )
    print(exp_header)

    for p_thresh in range(1, 6):
        # Filter by proposer votes
        subset_p = gdf_pred[
            gdf_pred["proposer_votes"] >= p_thresh
        ].copy()
        if subset_p.empty:
            continue

        # Simulate single-pass verifier (verified=True in first result)
        subset_verified = subset_p[
            subset_p.apply(_check_first_pass, axis=1)
        ].copy()

        count = len(subset_verified)
        p, r, f1 = 0.0, 0.0, 0.0
        if count > 0:
            p, r, f1 = calculate_f1_internal(
                subset_verified, gdf_ref, gdf_bounds,
                buffer_metres=buffer_metres,
            )

        label = "1-Pass Verifier"
        best_mark = "*" if f1 > 0.7 else ""
        print(
            f"{p_thresh:<10} | {label:<15} | {r:.4f}     | "
            f"{p:.4f}     | {f1:.4f} {best_mark}   | {count}"
        )

    print(
        "\n--- Experiment: Full Consensus Matrix "
        "(Proposer x Verifier Votes) ---"
    )
    matrix_header = (
        f"{'Prop Votes':<10} | {'Verif Votes':<10} | "
        f"{'Recall':<10} | {'Precision':<10} | "
        f"{'F1 Score':<10} | {'Count':<10}"
    )
    print(matrix_header)
    print("-" * 80)

    best_overall: dict = {"f1": 0, "desc": ""}

    for p_thresh in range(1, 6):
        # Filter by proposer consensus first
        subset_p = gdf_pred[
            gdf_pred["proposer_votes"] >= p_thresh
        ].copy()

        if subset_p.empty:
            continue

        for v_thresh in range(1, iterations + 1):
            # Filter by verifier consensus
            subset_pv = subset_p[
                subset_p["verifier_votes"] >= v_thresh
            ].copy()
            count = len(subset_pv)

            label = f"P>={p_thresh} V>={v_thresh}"

            p, r, f1 = 0.0, 0.0, 0.0
            if count > 0:
                p, r, f1 = calculate_f1_internal(
                    subset_pv, gdf_ref, gdf_bounds,
                    buffer_metres=buffer_metres,
                )

            if f1 > best_overall["f1"]:
                best_overall = {
                    "f1": f1,
                    "desc": label,
                    "p_thresh": p_thresh,
                    "v_thresh": v_thresh,
                    "metrics": (p, r, f1),
                }

            # Print compelling rows (F1 > 0.7)
            if f1 > 0.7:
                best_mark = "*" if f1 == best_overall["f1"] else ""
                print(
                    f"{p_thresh:<10} | {v_thresh:<10} | "
                    f"{r:.4f}     | {p:.4f}     | "
                    f"{f1:.4f} {best_mark}   | {count}"
                )

    print("-" * 80)
    print("Optimisation Result:")
    print(
        f"Global Best: {best_overall['desc']} -> "
        f"F1 {best_overall['f1']:.4f}"
    )
    if best_overall["f1"] > 0:
        p, r, f1 = best_overall["metrics"]
        print(f"Precision: {p:.4f}")
        print(f"Recall:    {r:.4f}")


def analyse_threshold_sweep(
    pred_path: Path | str,
    bounds_path: Path | str,
    template_path: Path | str,
    max_n: int = 30,
    cost_per_call: float = 0.003,
    n_tiles: int = 60,
    output_path: Path | str | None = None,
    buffer_metres: float = 20,
) -> dict:
    """Perform threshold sweep analysis across voting pool sizes.

    Supports H3 hypothesis testing by analysing how F1 varies with vote
    threshold T for different voting pool sizes N. Computes cost-efficiency
    metrics to identify optimal (N, T) combinations.

    The input GeoJSON must contain a "vote_count" property per detection
    (typically output from merge_passes.py). The function sweeps thresholds
    T=1, 2, ..., N for each pool size N in [5, 10, max_n].

    Args:
        pred_path: Path to merged predictions GeoJSON with
            "vote_count" property.
        bounds_path: Path to the tile bounds GeoJSON.
        template_path: Path to the ground truth reference GeoJSON.
        max_n: Maximum voting pool size to analyse (default: 30).
        cost_per_call: Cost per API call in USD (default: 0.003
            for Gemini Flash).
        n_tiles: Number of tiles per pass (default: 60 for the
            validation set).
        output_path: Optional path to write JSON results.
        buffer_metres: Spatial matching tolerance in metres (default: 20).

    Returns:
        Dictionary with keys:
        - "curves": list of {n, threshold, f1, precision, recall,
          count} dicts.
        - "optimal": Best (N, T) combination by F1.
        - "cost_efficiency": F1 per dollar at each (N, T).
        - "metadata": Analysis parameters.
    """
    pred_path = Path(pred_path)
    bounds_path = Path(bounds_path)
    template_path = Path(template_path)

    print(f"Threshold Sweep Analysis: {pred_path}")

    # 1. Load ground truth (bounds and references)
    target_crs = "EPSG:32635"
    try:
        gdf_bounds = gpd.read_file(bounds_path)
        gdf_ref = gpd.read_file(template_path)

        # Standardise CRS to UTM zone 35N
        if gdf_bounds.crs is None:
            gdf_bounds.set_crs(target_crs, inplace=True)
        elif gdf_bounds.crs != target_crs:
            gdf_bounds = gdf_bounds.to_crs(target_crs)

        if gdf_ref.crs is None:
            gdf_ref.set_crs(target_crs, inplace=True)
        elif gdf_ref.crs != target_crs:
            gdf_ref = gdf_ref.to_crs(target_crs)

    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return {}

    # 2. Load predictions with vote_count
    try:
        gdf_pred = gpd.read_file(pred_path)
        if gdf_pred.empty:
            print("Warning: Empty predictions file")
            return _empty_sweep_result(max_n, cost_per_call, n_tiles)

        gdf_pred.set_crs(
            target_crs, allow_override=True, inplace=True,
        )
        if gdf_pred.crs != gdf_ref.crs:
            gdf_pred = gdf_pred.to_crs(gdf_ref.crs)
    except Exception as e:
        print(f"Error loading predictions: {e}")
        return {}

    # Validate required vote_count column
    if "vote_count" not in gdf_pred.columns:
        print(
            "Error: Predictions must contain 'vote_count' property\n"
            "       (Use merge_passes.py to generate merged detections)"
        )
        return {}

    max_observed_votes = int(gdf_pred["vote_count"].max())
    print(f"Total detections: {len(gdf_pred)}")
    print(f"Max observed vote count: {max_observed_votes}")

    # 3. Define pool sizes (N) to analyse
    n_values = [
        n for n in [5, 10, max_n] if n <= max_observed_votes
    ]
    if not n_values:
        n_values = [max_observed_votes]
    print(f"Analysing N values: {n_values}")

    # 4. Sweep thresholds
    curves: list[dict] = []
    best_f1 = 0.0
    optimal: dict = {
        "n": 0,
        "threshold": 0,
        "f1": 0.0,
        "precision": 0.0,
        "recall": 0.0,
        "count": 0,
    }

    for n in n_values:
        print(f"\n--- N={n} ---")
        for threshold in range(1, n + 1):
            # Filter by vote threshold
            subset = gdf_pred[
                gdf_pred["vote_count"] >= threshold
            ].copy()
            count = len(subset)

            # Calculate metrics
            precision, recall, f1 = 0.0, 0.0, 0.0
            if count > 0:
                precision, recall, f1 = calculate_f1_internal(
                    subset, gdf_ref, gdf_bounds,
                    buffer_metres=buffer_metres,
                )

            # Calculate cost
            api_calls = n * n_tiles
            cost = api_calls * cost_per_call
            f1_per_dollar = f1 / cost if cost > 0 else 0.0

            curves.append({
                "n": n,
                "threshold": threshold,
                "f1": round(f1, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "count": count,
                "api_calls": api_calls,
                "cost_usd": round(cost, 2),
                "f1_per_dollar": round(f1_per_dollar, 4),
            })

            # Track best
            if f1 > best_f1:
                best_f1 = f1
                optimal = {
                    "n": n,
                    "threshold": threshold,
                    "f1": round(f1, 4),
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "count": count,
                }

            # Print notable rows
            marker = "*" if f1 == best_f1 and f1 > 0 else ""
            if f1 >= 0.5 or threshold == 1 or threshold == n:
                print(
                    f"  T>={threshold}: F1={f1:.4f}, "
                    f"P={precision:.4f}, "
                    f"R={recall:.4f}, n={count} {marker}"
                )

    # 5. Build result
    result = {
        "curves": curves,
        "optimal": optimal,
        "cost_efficiency": _calculate_cost_efficiency(curves),
        "metadata": {
            "pred_path": str(pred_path),
            "bounds_path": str(bounds_path),
            "template_path": str(template_path),
            "max_n": max_n,
            "n_values_analysed": n_values,
            "max_observed_votes": max_observed_votes,
            "cost_per_call": cost_per_call,
            "n_tiles": n_tiles,
        },
    }

    # 6. Print summary
    print("\n" + "=" * 60)
    print("THRESHOLD SWEEP SUMMARY")
    print("=" * 60)
    print(
        f"Optimal: N={optimal['n']}, "
        f"T>={optimal['threshold']}"
    )
    print(f"  F1:        {optimal['f1']:.4f}")
    print(f"  Precision: {optimal['precision']:.4f}")
    print(f"  Recall:    {optimal['recall']:.4f}")
    print(f"  Detections: {optimal['count']}")

    # Best cost efficiency
    if result["cost_efficiency"]:
        best_eff = max(
            result["cost_efficiency"],
            key=lambda x: x["f1_per_dollar"],
        )
        print(
            f"\nBest cost efficiency: N={best_eff['n']}, "
            f"T>={best_eff['threshold']}"
        )
        print(f"  F1/dollar: {best_eff['f1_per_dollar']:.4f}")

    # 7. Write output if requested
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults written to: {output_path}")

    return result


def _empty_sweep_result(
    max_n: int,
    cost_per_call: float,
    n_tiles: int,
) -> dict:
    """Return an empty result structure for empty predictions.

    Args:
        max_n: Maximum voting pool size.
        cost_per_call: Cost per API call in USD.
        n_tiles: Number of tiles per pass.

    Returns:
        Dictionary with empty curves, zeroed optimal, and metadata.
    """
    return {
        "curves": [],
        "optimal": {
            "n": 0,
            "threshold": 0,
            "f1": 0.0,
            "precision": 0.0,
            "recall": 0.0,
        },
        "cost_efficiency": [],
        "metadata": {
            "max_n": max_n,
            "cost_per_call": cost_per_call,
            "n_tiles": n_tiles,
            "note": "Empty predictions",
        },
    }


def _calculate_cost_efficiency(curves: list[dict]) -> list[dict]:
    """Calculate cost efficiency metrics for each (N, T) point.

    Args:
        curves: List of curve-point dicts, each containing "cost_usd"
            and "f1_per_dollar" keys.

    Returns:
        List of dicts with n, threshold, f1, cost_usd, and
        f1_per_dollar for points with non-zero cost.
    """
    efficiency = []
    for point in curves:
        if point["cost_usd"] > 0:
            efficiency.append({
                "n": point["n"],
                "threshold": point["threshold"],
                "f1": point["f1"],
                "cost_usd": point["cost_usd"],
                "f1_per_dollar": point["f1_per_dollar"],
            })
    return efficiency


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Consensus voting analysis for detection pipelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Two-stage pipeline analysis
  python scripts/7_analyse_consensus.py \\
      --pred outputs/verified.geojson \\
      --bounds inputs/vectors/bounds/validation_bounds.geojson \\
      --template inputs/vectors/references/mounds-reference.geojson

  # Single-stage threshold sweep (H3)
  python scripts/7_analyse_consensus.py \\
      --pred outputs/merged_detections.geojson \\
      --bounds inputs/vectors/bounds/validation_bounds.geojson \\
      --template inputs/vectors/references/mounds-reference.geojson \\
      --threshold-sweep \\
      --output outputs/threshold_sweep.json
        """,
    )
    parser.add_argument(
        "--pred",
        required=True,
        help="Path to predictions GeoJSON",
    )
    parser.add_argument(
        "--bounds",
        required=True,
        help="Path to bounds GeoJSON",
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Path to ground truth GeoJSON",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Max verifier iterations for two-stage analysis (default: 5)",
    )
    parser.add_argument(
        "--threshold-sweep",
        action="store_true",
        help="Enable single-stage threshold sweep mode (H3)",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=30,
        help="Maximum N for threshold sweep (default: 30)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for threshold sweep results (JSON)",
    )
    parser.add_argument(
        "--cost-per-call",
        type=float,
        default=0.003,
        help="Cost per API call in USD (default: 0.003)",
    )
    parser.add_argument(
        "--n-tiles",
        type=int,
        default=60,
        help="Number of tiles per pass (default: 60)",
    )
    parser.add_argument(
        "--buffer-metres",
        type=float,
        default=20,
        help=(
            "Spatial matching tolerance in metres for F1 evaluation"
            " \u2014 how close a detection must be to ground truth to"
            " count as a true positive (default: 20)."
        ),
    )

    args = parser.parse_args()

    if args.threshold_sweep:
        analyse_threshold_sweep(
            args.pred,
            args.bounds,
            args.template,
            max_n=args.max_n,
            cost_per_call=args.cost_per_call,
            n_tiles=args.n_tiles,
            output_path=args.output,
            buffer_metres=args.buffer_metres,
        )
    else:
        analyse_consensus(
            args.pred, args.bounds, args.template, args.iterations,
            buffer_metres=args.buffer_metres,
        )
