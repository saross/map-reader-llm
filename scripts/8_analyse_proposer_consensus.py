"""
Proposer Consensus Analysis Script
==================================

Analyses the effect of proposer vote thresholds on detection performance.
Evaluates F1, precision, and recall at different voting thresholds (1-5)
to determine optimal consensus settings for Stage 1 of the two-stage pipeline.

Usage:
    python scripts/8_analyse_proposer_consensus.py \\
        --union outputs/results/v4.1/union.geojson \\
        --bounds inputs/vectors/region_bounds.geojson \\
        --template inputs/vectors/ground_truth.geojson

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import sys
from pathlib import Path

import geopandas as gpd

# Setup Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

try:
    from scripts.lib_advanced_metrics import calculate_f1_internal, load_data
except ImportError:
    print("Error importing scripts.lib_advanced_metrics.")
    sys.exit(1)


def analyse_proposer(union_path: Path | str, bounds_path: Path | str, template_path: Path | str) -> None:
    """
    Analyse proposer vote thresholds for the first stage of the pipeline.

    Iterates through vote thresholds 1-5 and calculates F1, precision, and recall
    for each threshold level to help identify optimal consensus settings.

    Args:
        union_path: Path to the union predictions GeoJSON (containing proposer_votes).
        bounds_path: Path to the tile bounds GeoJSON.
        template_path: Path to the ground truth reference GeoJSON.
    """
    print(f"Analysing Proposer Consensus: {union_path}")

    # Load Ground Truth
    try:
        _, gdf_bounds, gdf_ref = load_data(template_path, bounds_path)
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return

    # Load Union predictions
    try:
        gdf_pred = gpd.read_file(union_path)
        if not gdf_pred.empty:
            gdf_pred.set_crs("EPSG:32635", allow_override=True, inplace=True)
            if gdf_pred.crs != gdf_ref.crs:
                gdf_pred = gdf_pred.to_crs(gdf_ref.crs)

            # Filter NaNs in source_tile
            valid_mask = gdf_pred['source_tile'].notna()
            gdf_pred = gdf_pred[valid_mask].copy()

    except Exception as e:
        print(f"Error loading union: {e}")
        return

    print(f"Total Candidates: {len(gdf_pred)}")

    print(f"\n{'Votes':<10} | {'Recall':<10} | {'Precision':<10} | {'F1 Score':<10} | {'Count':<10}")
    print("-" * 60)

    best = {"f1": 0.0, "desc": "", "metrics": (0.0, 0.0, 0.0)}

    for vote_threshold in range(1, 6):
        subset = gdf_pred[gdf_pred['proposer_votes'] >= vote_threshold].copy()
        count = len(subset)

        if count == 0:
            print(f"{vote_threshold:<10} | 0.0000     | 0.0000     | 0.0000     | 0")
            continue

        p, r, f1 = calculate_f1_internal(subset, gdf_ref, gdf_bounds)

        if f1 > best["f1"]:
            best = {"f1": f1, "desc": f"{vote_threshold} Votes", "metrics": (p, r, f1)}

        best_mark = "*" if f1 > 0.7 else ""
        print(f"{vote_threshold:<10} | {r:.4f}     | {p:.4f}     | {f1:.4f} {best_mark}   | {count}")

    print("-" * 60)
    if best['f1'] > 0:
        p, r, f1 = best['metrics']
        print(f"Best: {best['desc']} -> F1 {f1:.4f} (P {p:.4f}, R {r:.4f})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--union", required=True)
    parser.add_argument("--bounds", required=True)
    parser.add_argument("--template", required=True)
    args = parser.parse_args()
    
    analyse_proposer(args.union, args.bounds, args.template)
