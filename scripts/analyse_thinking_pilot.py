#!/usr/bin/env python3
"""
Thinking Level Pilot Analysis
==============================

Analyses results from the thinking level calibration pilot and generates
a report comparing F1 performance across minimal, low, and high reasoning depths.

Usage:
    python scripts/analyse_thinking_pilot.py
    python scripts/analyse_thinking_pilot.py --output results/thinking_pilot_report.md

Inputs:
    outputs/results/pilot_thinking-{level}/
        pilot_thinking-{level}_run{01-10}.geojson
        pilot_thinking-{level}_run{01-10}.meta.json

Outputs:
    Markdown report with:
    - Per-condition mean F1, SD, 95% CI
    - Pairwise comparisons (low vs high, minimal vs low)
    - Latency and token usage summaries
    - Recommendation for main experiment

Author: Shawn Ross, Claude Code
Version: 1.0.0
Licence: Apache 2.0
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import geopandas as gpd
import numpy as np
import pandas as pd

# Add scripts directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent))
from lib_advanced_metrics import calculate_f1_internal

# Script version
__version__ = "1.0.0"

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Pilot configuration
THINKING_LEVELS = ["minimal", "low", "high"]
K_RUNS = 10

# Decision thresholds (from spec)
LARGE_DIFFERENCE = 0.05  # high >> low
SMALL_DIFFERENCE = 0.03  # high ≈ low


class RunResult(NamedTuple):
    """Results from a single detection run."""

    thinking_level: str
    run_number: int
    precision: float
    recall: float
    f1: float
    latency_seconds: float | None
    input_tokens: int | None
    output_tokens: int | None


def find_result_files(thinking_level: str) -> list[tuple[Path, Path]]:
    """
    Find GeoJSON and meta.json pairs for a thinking level.

    Args:
        thinking_level: "minimal", "low", or "high"

    Returns:
        List of (geojson_path, meta_path) tuples
    """
    results_dir = PROJECT_ROOT / "outputs" / "results" / f"pilot_thinking-{thinking_level}"

    if not results_dir.exists():
        return []

    pairs = []
    for run_num in range(1, K_RUNS + 1):
        geojson_pattern = f"pilot_thinking-{thinking_level}_run{run_num:02d}*.geojson"
        matches = list(results_dir.glob(geojson_pattern))

        if matches:
            geojson_path = matches[0]
            meta_path = geojson_path.with_suffix(".meta.json")
            pairs.append((geojson_path, meta_path))

    return pairs


def extract_run_metrics(
    geojson_path: Path,
    meta_path: Path,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    thinking_level: str,
    run_number: int,
) -> RunResult | None:
    """
    Extract metrics from a single run's results.

    Args:
        geojson_path: Path to detection GeoJSON
        meta_path: Path to meta.json
        gdf_ref: Reference ground truth GeoDataFrame
        gdf_bounds: Tile bounds GeoDataFrame
        thinking_level: Thinking level name
        run_number: Run number (1-10)

    Returns:
        RunResult or None if files missing/invalid
    """
    try:
        # Load detections
        gdf_det = gpd.read_file(geojson_path)
        if gdf_det.crs != "EPSG:32635":
            if gdf_det.crs is None:
                gdf_det.set_crs("EPSG:32635", inplace=True)
            else:
                gdf_det = gdf_det.to_crs("EPSG:32635")

        # Calculate F1
        precision, recall, f1 = calculate_f1_internal(gdf_det, gdf_ref, gdf_bounds)

        # Extract operational metrics from meta.json
        latency = None
        input_tokens = None
        output_tokens = None

        if meta_path.exists():
            with open(meta_path, "r") as f:
                meta = json.load(f)

            # Extract duration
            if "timestamp" in meta:
                ts = meta["timestamp"]
                if "duration_seconds" in ts:
                    latency = ts["duration_seconds"]

            # Extract token usage
            if "usage_stats" in meta:
                usage = meta["usage_stats"]
                if "total" in usage:
                    total = usage["total"]
                    input_tokens = total.get("input_tokens")
                    output_tokens = total.get("output_tokens")

        return RunResult(
            thinking_level=thinking_level,
            run_number=run_number,
            precision=precision,
            recall=recall,
            f1=f1,
            latency_seconds=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    except Exception as e:
        print(f"Error processing {geojson_path}: {e}")
        return None


def calculate_condition_stats(results: list[RunResult]) -> dict:
    """
    Calculate aggregate statistics for a condition.

    Args:
        results: List of RunResult for one thinking level

    Returns:
        Dictionary with mean, SD, 95% CI for F1 and operational metrics
    """
    if not results:
        return {}

    f1_values = [r.f1 for r in results]
    precision_values = [r.precision for r in results]
    recall_values = [r.recall for r in results]

    # Calculate CI using t-distribution for small samples
    n = len(f1_values)
    f1_mean = np.mean(f1_values)
    f1_sd = np.std(f1_values, ddof=1) if n > 1 else 0

    # 95% CI: mean ± t * (sd / sqrt(n))
    # For n=10, t(0.975, 9) ≈ 2.262
    t_value = 2.262 if n == 10 else 1.96
    ci_margin = t_value * (f1_sd / np.sqrt(n)) if n > 1 else 0

    # Operational metrics
    latencies = [r.latency_seconds for r in results if r.latency_seconds is not None]
    input_tokens = [r.input_tokens for r in results if r.input_tokens is not None]
    output_tokens = [r.output_tokens for r in results if r.output_tokens is not None]

    return {
        "n": n,
        "f1": {
            "mean": f1_mean,
            "sd": f1_sd,
            "ci_lower": max(0, f1_mean - ci_margin),
            "ci_upper": min(1, f1_mean + ci_margin),
            "values": f1_values,
        },
        "precision": {
            "mean": np.mean(precision_values),
            "sd": np.std(precision_values, ddof=1) if n > 1 else 0,
        },
        "recall": {
            "mean": np.mean(recall_values),
            "sd": np.std(recall_values, ddof=1) if n > 1 else 0,
        },
        "latency": {
            "mean": np.mean(latencies) if latencies else None,
            "sd": np.std(latencies, ddof=1) if len(latencies) > 1 else None,
        },
        "tokens": {
            "input_mean": np.mean(input_tokens) if input_tokens else None,
            "output_mean": np.mean(output_tokens) if output_tokens else None,
        },
    }


def determine_recommendation(stats: dict[str, dict]) -> tuple[str, str]:
    """
    Determine recommended thinking level based on decision criteria.

    Args:
        stats: Dictionary mapping thinking level to stats

    Returns:
        Tuple of (recommended_level, reason)
    """
    if "high" not in stats or "low" not in stats:
        return "high", "Insufficient data; defaulting to Google's recommended setting"

    high_f1 = stats["high"]["f1"]["mean"]
    low_f1 = stats["low"]["f1"]["mean"]
    diff = high_f1 - low_f1

    # Check for overlapping CIs
    high_ci = (stats["high"]["f1"]["ci_lower"], stats["high"]["f1"]["ci_upper"])
    low_ci = (stats["low"]["f1"]["ci_lower"], stats["low"]["f1"]["ci_upper"])
    cis_overlap = high_ci[0] <= low_ci[1] and low_ci[0] <= high_ci[1]

    if diff > LARGE_DIFFERENCE:
        return "high", f"high >> low (F1 diff = {diff:.3f} > 0.05)"

    if diff <= SMALL_DIFFERENCE:
        # Check minimal vs low
        if "minimal" in stats:
            minimal_f1 = stats["minimal"]["f1"]["mean"]
            minimal_low_diff = low_f1 - minimal_f1
            if minimal_low_diff <= SMALL_DIFFERENCE:
                return "minimal", "minimal ≈ low ≈ high (max efficiency, F1 diff ≤ 0.03)"

        return "low", f"high ≈ low (F1 diff = {diff:.3f} ≤ 0.03; cost/latency savings)"

    if diff < 0:  # low > high
        return "low", f"low > high (F1 diff = {-diff:.3f}; task benefits from less reasoning)"

    # Ambiguous case
    if cis_overlap:
        return "high", "Ambiguous (0.03 < diff < 0.05, CIs overlap); defaulting to high"

    return "high", f"Ambiguous (diff = {diff:.3f}); defaulting to Google's recommended setting"


def generate_report(stats: dict[str, dict], recommendation: str, reason: str) -> str:
    """
    Generate markdown report from analysis results.

    Args:
        stats: Dictionary mapping thinking level to stats
        recommendation: Recommended thinking level
        reason: Explanation for recommendation

    Returns:
        Markdown report string
    """
    lines = [
        "## Thinking Level Pilot Results",
        "",
        f"**Date run:** {datetime.now().strftime('%Y-%m-%d')}",
        "**Model:** gemini-3-flash",
        "",
        "### Performance Summary",
        "",
        "| Thinking Level | Mean F1 | SD | 95% CI | Mean Latency | Notes |",
        "|----------------|---------|-----|--------|--------------|-------|",
    ]

    for level in THINKING_LEVELS:
        if level not in stats:
            lines.append(f"| {level} | — | — | — | — | No data |")
            continue

        s = stats[level]
        f1 = s["f1"]
        latency = s["latency"]

        latency_str = f"{latency['mean']:.1f}s" if latency["mean"] else "—"
        ci_str = f"[{f1['ci_lower']:.3f}, {f1['ci_upper']:.3f}]"

        lines.append(
            f"| {level} | {f1['mean']:.3f} | {f1['sd']:.3f} | {ci_str} | {latency_str} | n={s['n']} |"
        )

    lines.extend(
        [
            "",
            "### Precision and Recall",
            "",
            "| Thinking Level | Mean Precision | Mean Recall |",
            "|----------------|----------------|-------------|",
        ]
    )

    for level in THINKING_LEVELS:
        if level not in stats:
            continue
        s = stats[level]
        lines.append(f"| {level} | {s['precision']['mean']:.3f} | {s['recall']['mean']:.3f} |")

    # Token usage if available
    any_tokens = any(
        stats.get(l, {}).get("tokens", {}).get("input_mean") for l in THINKING_LEVELS
    )
    if any_tokens:
        lines.extend(
            [
                "",
                "### Token Usage",
                "",
                "| Thinking Level | Mean Input Tokens | Mean Output Tokens |",
                "|----------------|-------------------|-------------------|",
            ]
        )
        for level in THINKING_LEVELS:
            if level not in stats:
                continue
            t = stats[level].get("tokens", {})
            input_str = f"{t['input_mean']:.0f}" if t.get("input_mean") else "—"
            output_str = f"{t['output_mean']:.0f}" if t.get("output_mean") else "—"
            lines.append(f"| {level} | {input_str} | {output_str} |")

    lines.extend(
        [
            "",
            "### Pairwise Comparisons",
            "",
        ]
    )

    # High vs Low
    if "high" in stats and "low" in stats:
        diff = stats["high"]["f1"]["mean"] - stats["low"]["f1"]["mean"]
        lines.append(f"- **high vs low:** F1 difference = {diff:+.3f}")

    # Low vs Minimal
    if "low" in stats and "minimal" in stats:
        diff = stats["low"]["f1"]["mean"] - stats["minimal"]["f1"]["mean"]
        lines.append(f"- **low vs minimal:** F1 difference = {diff:+.3f}")

    lines.extend(
        [
            "",
            "---",
            "",
            f"**Recommendation:** Use `{recommendation}` for main experiment because {reason}.",
            "",
        ]
    )

    return "\n".join(lines)


def analyse_pilot(output_path: Path | None = None, verbose: bool = True) -> dict:
    """
    Run the full pilot analysis.

    Args:
        output_path: Optional path to write markdown report
        verbose: Print progress information

    Returns:
        Analysis results dictionary
    """
    if verbose:
        print("=" * 70)
        print("Thinking Level Pilot Analysis")
        print("=" * 70)
        print()

    # Load reference data directly (without needing a detection file)
    bounds_file = PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "calibration_bounds.geojson"
    if not bounds_file.exists():
        # Fall back to validation bounds
        bounds_file = PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "validation_bounds.geojson"

    try:
        gdf_bounds = gpd.read_file(bounds_file)
        if gdf_bounds.crs != "EPSG:32635":
            if gdf_bounds.crs is None:
                gdf_bounds.set_crs("EPSG:32635", inplace=True)
            else:
                gdf_bounds = gdf_bounds.to_crs("EPSG:32635")

        # Load reference vectors
        ref_files = list((PROJECT_ROOT / "inputs" / "vectors" / "references").glob("reference_*.geojson"))
        ref_gdfs = []
        for rf in ref_files:
            gdf = gpd.read_file(rf)
            gdf["Map"] = rf.stem.replace("reference_", "")
            ref_gdfs.append(gdf)

        if not ref_gdfs:
            print("ERROR: No reference vectors found")
            return {"error": "no_reference_data"}

        gdf_ref = pd.concat(ref_gdfs, ignore_index=True)
        if gdf_ref.crs != "EPSG:32635":
            if gdf_ref.crs is None:
                gdf_ref.set_crs("EPSG:32635", inplace=True)
            else:
                gdf_ref = gdf_ref.to_crs("EPSG:32635")

    except Exception as e:
        print(f"ERROR: Could not load reference data: {e}")
        return {"error": "no_reference_data"}

    # Filter bounds to calibration tiles
    calibration_manifest = PROJECT_ROOT / "inputs" / "tiles" / "calibration_manifest.json"
    if calibration_manifest.exists():
        with open(calibration_manifest, "r") as f:
            cal_tiles = json.load(f)
        # Extract tile names without extension
        cal_tile_names = [Path(t).stem for t in cal_tiles]
        gdf_bounds = gdf_bounds[gdf_bounds["tile_name"].isin(cal_tile_names)]

    if verbose:
        print(f"Reference mounds: {len(gdf_ref)}")
        print(f"Calibration tiles: {len(gdf_bounds)}")
        print()

    # Collect results by thinking level
    all_results: dict[str, list[RunResult]] = {level: [] for level in THINKING_LEVELS}

    for level in THINKING_LEVELS:
        pairs = find_result_files(level)
        if verbose:
            print(f"Found {len(pairs)} result files for {level}")

        for i, (geojson_path, meta_path) in enumerate(pairs, 1):
            result = extract_run_metrics(
                geojson_path, meta_path, gdf_ref, gdf_bounds, level, i
            )
            if result:
                all_results[level].append(result)

    # Calculate statistics
    stats = {}
    for level, results in all_results.items():
        if results:
            stats[level] = calculate_condition_stats(results)
            if verbose:
                s = stats[level]
                print(
                    f"  {level}: F1 = {s['f1']['mean']:.3f} ± {s['f1']['sd']:.3f} "
                    f"(n={s['n']})"
                )

    print()

    # Determine recommendation
    recommendation, reason = determine_recommendation(stats)

    if verbose:
        print(f"Recommendation: {recommendation}")
        print(f"Reason: {reason}")
        print()

    # Generate report
    report = generate_report(stats, recommendation, reason)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report)
        if verbose:
            print(f"Report written to: {output_path}")
    else:
        print(report)

    return {
        "stats": stats,
        "recommendation": recommendation,
        "reason": reason,
    }


def main():
    """Main entry point for thinking pilot analysis."""
    parser = argparse.ArgumentParser(
        description="Analyse thinking level pilot results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Path to write markdown report (default: print to stdout)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    results = analyse_pilot(output_path=args.output, verbose=not args.quiet)

    if results.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
