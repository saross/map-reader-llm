#!/usr/bin/env python3
"""
Proposer Consensus Analysis Script
==================================

Analyses the effect of proposer vote thresholds on detection performance.
Evaluates F1, precision, and recall at different voting thresholds (1--5)
to determine optimal consensus settings for Stage 1 of the two-stage
pipeline.

Usage:
    python scripts/8_analyse_proposer_consensus.py \\
        --union outputs/results/v4.1/union.geojson \\
        --bounds inputs/vectors/region_bounds.geojson \\
        --template inputs/vectors/ground_truth.geojson

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
from pathlib import Path

import geopandas as gpd

from scripts.lib_advanced_metrics import calculate_f1_internal, load_data

# Number of proposer models in the ensemble (votes range from 1 to this value)
MAX_PROPOSER_VOTES = 5


def analyse_proposer(
    union_path: Path | str,
    bounds_path: Path | str,
    template_path: Path | str,
    buffer_metres: float = 20,
) -> None:
    """Analyse proposer vote thresholds for Stage 1 of the pipeline.

    Iterates through vote thresholds 1--5 and calculates F1, precision,
    and recall for each threshold level to help identify optimal
    consensus settings.

    Args:
        union_path: Path to the union predictions GeoJSON file
            (must contain a ``proposer_votes`` column).
        bounds_path: Path to the tile bounds GeoJSON file.
        template_path: Path to the ground truth reference GeoJSON file.
        buffer_metres: Spatial matching tolerance in metres (default: 20).
    """
    print(f"Analysing Proposer Consensus: {union_path}")

    # Load ground truth reference data and tile bounds
    try:
        _, gdf_bounds, gdf_ref = load_data(template_path, bounds_path)
    except Exception as exc:
        print(f"Error loading ground truth: {exc}")
        return

    # Load union predictions and reproject to match reference Coordinate
    # Reference System (CRS)
    try:
        gdf_pred = gpd.read_file(union_path)
        if not gdf_pred.empty:
            from lib_consensus import ensure_utm_crs
            gdf_pred = ensure_utm_crs(
                gdf_pred, source_label=str(union_path),
            )
            if gdf_pred.crs != gdf_ref.crs:
                gdf_pred = gdf_pred.to_crs(gdf_ref.crs)

            # Filter rows with missing source_tile values
            valid_mask = gdf_pred["source_tile"].notna()
            gdf_pred = gdf_pred[valid_mask].copy()

    except Exception as exc:
        print(f"Error loading union: {exc}")
        return

    print(f"Total Candidates: {len(gdf_pred)}")

    # Print threshold-level metrics table
    header = (
        f"{'Votes':<10} | {'Recall':<10} | "
        f"{'Precision':<10} | {'F1 Score':<10} | {'Count':<10}"
    )
    print(f"\n{header}")
    print("-" * 60)

    best: dict[str, float | str | tuple[float, float, float]] = {
        "f1": 0.0,
        "desc": "",
        "metrics": (0.0, 0.0, 0.0),
    }

    for threshold in range(1, MAX_PROPOSER_VOTES + 1):
        subset = gdf_pred[
            gdf_pred["proposer_votes"] >= threshold
        ].copy()
        count = len(subset)

        if count == 0:
            print(
                f"{threshold:<10} | 0.0000     | "
                f"0.0000     | 0.0000     | 0"
            )
            continue

        precision, recall, f1 = calculate_f1_internal(
            subset, gdf_ref, gdf_bounds,
            buffer_metres=buffer_metres,
        )

        if f1 > best["f1"]:
            best = {
                "f1": f1,
                "desc": f"{threshold} Votes",
                "metrics": (precision, recall, f1),
            }

        marker = "*" if f1 > 0.7 else ""
        print(
            f"{threshold:<10} | {recall:.4f}     | "
            f"{precision:.4f}     | {f1:.4f} {marker}   | {count}"
        )

    # Summary of best threshold
    print("-" * 60)
    if best["f1"] > 0:
        bp, br, bf1 = best["metrics"]
        print(
            f"Best: {best['desc']} -> "
            f"F1 {bf1:.4f} (P {bp:.4f}, R {br:.4f})"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyse proposer vote thresholds on detection metrics.",
    )
    parser.add_argument("--union", required=True, help="Path to union GeoJSON")
    parser.add_argument("--bounds", required=True, help="Path to bounds GeoJSON")
    parser.add_argument("--template", required=True, help="Path to ground truth GeoJSON")
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

    analyse_proposer(
        args.union, args.bounds, args.template,
        buffer_metres=args.buffer_metres,
    )
