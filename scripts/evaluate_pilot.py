#!/usr/bin/env python3
"""
Comprehensive pilot evaluation for the 340-tile production retest.

Runs all verification checks from the plan (Steps 8.3, 8.6, 8.7):
  1. Basic metrics: F1, precision, recall on full 340-tile set
  2. Bootstrap CIs: symbol-level F1 with 95% CIs (1,000 iterations)
  3. Tile-level classification: MCC, sensitivity, specificity
  4. Regression check: extract the 60-tile validation subset and compare
     against historical Phase 2c Track 2 plus-hp F1

Usage::

    python scripts/evaluate_pilot.py <detections_geojson>

    # Example:
    python scripts/evaluate_pilot.py \\
        outputs/retest/phase2c/track2-text/plus-hp/run_1/*.geojson

Created: 2026-03-15
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib_advanced_metrics import (
    DEFAULT_CRS,
    bootstrap_ci,
    calculate_f1_internal,
    calculate_tile_classification,
    bootstrap_tile_classification_ci,
    load_data,
)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
FULL_BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/full_evaluation_bounds.geojson"
VALIDATION_BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/validation_bounds.geojson"

# Historical reference: Phase 2c Track 2 plus-hp F1 on 60 validation tiles
# From Phase 2c results (K=10 average, T=0.0, detect_brief-text config)
HISTORICAL_F1 = 0.609  # Phase 2c Track 1 plus-hp (image-using)
# Note: Track 2 text-only plus-hp may differ; this is a directional check


def load_detections(pred_path: Path, target_crs: str = DEFAULT_CRS) -> gpd.GeoDataFrame:
    """Load and prepare detection GeoDataFrame.

    Args:
        pred_path: Path to detections GeoJSON file.
        target_crs: Target Coordinate Reference System (CRS).

    Returns:
        GeoDataFrame of detections with CRS set.
    """
    gdf = gpd.read_file(pred_path)
    if not gdf.empty:
        gdf.set_crs(target_crs, allow_override=True, inplace=True)

        # Normalise source_tile column
        if "source_tile" not in gdf.columns and "source_tiles" in gdf.columns:
            gdf["source_tile"] = gdf["source_tiles"].apply(
                lambda x: x[0] if hasattr(x, "__getitem__") and len(x) > 0
                else str(x)
            )
    return gdf


def evaluate_on_bounds(
    gdf_det: gpd.GeoDataFrame,
    bounds_path: Path,
    label: str,
) -> dict:
    """Evaluate detections against ground truth within specified bounds.

    Computes symbol-level metrics (F1, precision, recall), bootstrap CIs,
    and tile-level classification (MCC).

    Args:
        gdf_det: Detection GeoDataFrame.
        bounds_path: Path to bounds GeoJSON.
        label: Label for this evaluation (e.g., '340-tile' or '60-tile').

    Returns:
        Dictionary with all computed metrics.
    """
    # Load ground truth and bounds
    _, gdf_bounds, gdf_ref = load_data(str(GROUND_TRUTH), str(bounds_path))

    if gdf_ref is None or gdf_bounds is None:
        print(f"  ERROR: Failed to load data for {label}")
        return {}

    # Ensure CRS match
    if gdf_det.crs != gdf_ref.crs:
        gdf_det = gdf_det.to_crs(gdf_ref.crs)

    # Scope detections to tiles within bounds (prevents cross-tile leakage
    # when evaluating a subset like the 60-tile validation set)
    tile_names_in_bounds = set(gdf_bounds["tile_name"].tolist())
    if "source_tile" in gdf_det.columns:
        gdf_det_scoped = gdf_det[
            gdf_det["source_tile"].isin(tile_names_in_bounds)
        ].copy()
    else:
        # Fallback: spatial join
        det_joined = gpd.sjoin(
            gdf_det, gdf_bounds, how="inner", predicate="intersects",
        )
        gdf_det_scoped = gdf_det.loc[det_joined.index.unique()].copy()

    n_det = len(gdf_det_scoped)

    print(f"\n{'=' * 60}")
    print(f"  {label} Evaluation")
    print(f"{'=' * 60}")
    print(f"  Tiles: {len(gdf_bounds)}")
    print(f"  Detections in scope: {n_det}")

    # Symbol-level metrics (using scoped detections only)
    p, r, f1 = calculate_f1_internal(gdf_det_scoped, gdf_ref, gdf_bounds)
    print("\n  Symbol-Level Metrics (point estimates):")
    print(f"    Precision: {p:.4f}")
    print(f"    Recall:    {r:.4f}")
    print(f"    F1:        {f1:.4f}")

    # Bootstrap CIs (symbol-level)
    print("\n  Computing bootstrap CIs (1,000 iterations)...")
    ci_results = bootstrap_ci(
        gdf_det_scoped, gdf_ref, gdf_bounds,
        n_iterations=1000,
        random_seed=42,
    )

    f1_ci = ci_results.get("f1", {})
    p_ci = ci_results.get("precision", {})
    r_ci = ci_results.get("recall", {})

    print("  Symbol-Level Metrics (with 95% CIs):")
    print(
        f"    F1:        {f1_ci.get('mean', 0):.4f} "
        f"[{f1_ci.get('ci_lower', 0):.4f}, {f1_ci.get('ci_upper', 0):.4f}]"
    )
    print(
        f"    Precision: {p_ci.get('mean', 0):.4f} "
        f"[{p_ci.get('ci_lower', 0):.4f}, {p_ci.get('ci_upper', 0):.4f}]"
    )
    print(
        f"    Recall:    {r_ci.get('mean', 0):.4f} "
        f"[{r_ci.get('ci_lower', 0):.4f}, {r_ci.get('ci_upper', 0):.4f}]"
    )
    ci_width = f1_ci.get('ci_upper', 0) - f1_ci.get('ci_lower', 0)
    print(f"    CI width:  {ci_width:.4f}")

    # Tile-level classification
    tile_results = calculate_tile_classification(
        gdf_det_scoped, gdf_ref, gdf_bounds,
    )
    tile_ci = bootstrap_tile_classification_ci(
        gdf_det_scoped, gdf_ref, gdf_bounds,
        n_iterations=1000,
        random_seed=42,
    )

    mcc = tile_results.get("mcc")
    mcc_ci = tile_ci.get("mcc", {})
    print("\n  Tile-Level Classification:")
    if mcc is not None:
        print(
            f"    MCC:         {mcc:.4f} "
            f"[{mcc_ci.get('ci_lower', 0):.4f}, "
            f"{mcc_ci.get('ci_upper', 0):.4f}]"
        )
    print(f"    Sensitivity: {tile_results.get('sensitivity', 0):.4f}")
    print(f"    Specificity: {tile_results.get('specificity', 0):.4f}")
    print(
        f"    Tiles: {tile_results.get('n_populated', 0)} populated, "
        f"{tile_results.get('n_empty', 0)} empty"
    )

    return {
        "label": label,
        "n_tiles": len(gdf_bounds),
        "n_detections": n_det,
        "f1": f1,
        "precision": p,
        "recall": r,
        "f1_ci": f1_ci,
        "precision_ci": p_ci,
        "recall_ci": r_ci,
        "ci_width": ci_width,
        "mcc": mcc,
        "tile_results": tile_results,
    }


def main() -> None:
    """Run comprehensive pilot evaluation."""
    parser = argparse.ArgumentParser(
        description="Comprehensive pilot evaluation for 340-tile retest",
    )
    parser.add_argument(
        "detections",
        type=Path,
        help="Path to detections GeoJSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Export results to JSON file",
    )
    args = parser.parse_args()

    if not args.detections.exists():
        print(f"Error: Detections file not found: {args.detections}")
        sys.exit(1)

    print("=" * 60)
    print("  Production Retest Pilot Evaluation")
    print("=" * 60)
    print(f"  Detections: {args.detections}")
    print(f"  Ground truth: {GROUND_TRUTH}")

    # Load detections
    gdf_det = load_detections(args.detections)
    print(f"  Total detections loaded: {len(gdf_det)}")

    # 1. Full 340-tile evaluation
    full_results = evaluate_on_bounds(
        gdf_det, FULL_BOUNDS, "340-tile Full Corpus",
    )

    # 2. 60-tile validation subset (regression check)
    subset_results = evaluate_on_bounds(
        gdf_det, VALIDATION_BOUNDS, "60-tile Validation Subset (Regression)",
    )

    # 3. Regression comparison
    print(f"\n{'=' * 60}")
    print("  Regression Check")
    print(f"{'=' * 60}")

    if subset_results:
        subset_f1 = subset_results["f1"]
        subset_ci = subset_results.get("f1_ci", {})
        ci_lower = subset_ci.get("ci_lower", 0)
        ci_upper = subset_ci.get("ci_upper", 0)

        print(f"  60-tile subset F1:  {subset_f1:.4f} [{ci_lower:.4f}, {ci_upper:.4f}]")
        print(f"  Historical F1:      ~{HISTORICAL_F1:.3f} (Phase 2c T1 plus-hp)")
        print()

        # Check if historical F1 falls within the new CI
        if ci_lower <= HISTORICAL_F1 <= ci_upper:
            print("  PASS: Historical F1 falls within new 95% CI.")
            print("  Model drift is negligible — results are consistent.")
        else:
            delta = subset_f1 - HISTORICAL_F1
            print(f"  WARNING: Historical F1 outside new 95% CI (delta={delta:+.4f})")
            print("  Possible model drift — review before proceeding.")

    # 4. Power improvement summary
    if full_results and subset_results:
        print(f"\n{'=' * 60}")
        print("  Power Improvement Summary")
        print(f"{'=' * 60}")
        full_width = full_results.get("ci_width", 0)
        subset_width = subset_results.get("ci_width", 0)
        if subset_width > 0:
            improvement = subset_width / full_width
            print(f"  60-tile CI width:  {subset_width:.4f}")
            print(f"  340-tile CI width: {full_width:.4f}")
            print(f"  Improvement:       {improvement:.1f}x narrower")

    # Export results
    if args.output:
        export = {
            "full_corpus": full_results,
            "validation_subset": subset_results,
        }
        with open(args.output, "w") as f:
            json.dump(export, f, indent=2, default=str)
        print(f"\n  Results exported to: {args.output}")

    print(f"\n{'=' * 60}")
    print("  Pilot evaluation complete.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
