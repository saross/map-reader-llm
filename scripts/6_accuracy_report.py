#!/usr/bin/env python3
"""
Accuracy Report Generator
=========================

Generates accuracy reports comparing Vision Language Model (VLM) detections
against ground truth.  Calculates symbol-level metrics (precision, recall,
F1) and tile-level classification metrics (Matthews Correlation Coefficient
(MCC), sensitivity, specificity).

Usage:
    python scripts/6_accuracy_report.py \\
        --pred outputs/results/v4.1/verified.geojson \\
        --bounds inputs/vectors/region_bounds.geojson \\
        --template inputs/vectors/ground_truth.geojson

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
from pathlib import Path

import geopandas as gpd

from scripts.lib_advanced_metrics import (
    DEFAULT_CRS,
    bootstrap_tile_classification_ci,
    calculate_f1_internal,
    calculate_tile_classification,
    load_data,
    scope_references_to_tiles,
)


def _normalise_source_tile(gdf: gpd.GeoDataFrame) -> None:
    """
    Normalise the source tile column name in-place.

    Merged GeoJSON files use ``source_tiles`` (list), while per-pass
    GeoJSON files use ``source_tile`` (string).  Downstream code
    expects ``source_tile``.
    """
    if "source_tile" not in gdf.columns and "source_tiles" in gdf.columns:
        gdf["source_tile"] = gdf["source_tiles"].apply(
            lambda x: x[0] if hasattr(x, "__getitem__") and len(x) > 0
            else str(x)
        )


def validate_file(
    pred_path: Path | str,
    bounds_path: Path | str,
    template_det_path: Path | str,
    target_crs: str = DEFAULT_CRS,
    buffer_metres: float = 20,
) -> None:
    """
    Validate detection predictions against ground truth and print an accuracy report.

    Computes symbol-level metrics (precision, recall, F1), tile-level
    classification (MCC, sensitivity, specificity), and writes False
    Positive (FP) / False Negative (FN) GeoJSON files alongside the
    predictions.

    Args:
        pred_path: Path to the predicted detections GeoJSON file.
        bounds_path: Path to the tile bounds GeoJSON file.
        template_det_path: Path to the ground truth reference GeoJSON.
        target_crs: Coordinate Reference System (CRS) for all datasets
            (default: EPSG:32635).
        buffer_metres: Spatial matching tolerance in metres (default: 20).
    """
    print(f"Validating: {pred_path}")

    # 1. Load ground truth via the template path.
    # load_data() returns (gdf_det, gdf_bounds, gdf_ref); we discard gdf_det.
    try:
        _, gdf_bounds, gdf_ref = load_data(template_det_path, bounds_path)
    except Exception as e:
        print(f"Error loading ground truth: {e}")
        return

    # Validate references loaded successfully (catches path bugs like E5a)
    if gdf_ref is None:
        print("FATAL: Failed to load ground truth references. Cannot evaluate.")
        print("Check that inputs/vectors/references/ contains reference_*.geojson files.")
        return
    if len(gdf_ref) == 0:
        print("FATAL: Ground truth references loaded but contain 0 features.")
        return
    if gdf_bounds is None or gdf_bounds.empty:
        print("FATAL: Failed to load tile bounds. Cannot scope evaluation.")
        return

    print(
        f"Loaded Ref: {len(gdf_ref)} features. "
        f"Maps: {gdf_ref['Map'].unique()}"
    )
    sample_tile = (
        gdf_bounds.iloc[0]["tile_name"] if not gdf_bounds.empty else "None"
    )
    print(
        f"Loaded Bounds: {len(gdf_bounds)} tiles. "
        f"Sample Tile: {sample_tile}"
    )

    # 2. Load predictions
    try:
        gdf_pred = gpd.read_file(pred_path)
        if not gdf_pred.empty:
            # Force CRS because coordinates are clearly UTM;
            # defaulting to WGS84 causes reprojection errors
            gdf_pred.set_crs(target_crs, allow_override=True, inplace=True)

            _normalise_source_tile(gdf_pred)

            sample_source = gdf_pred.iloc[0].get(
                "source_tile", "Missing",
            )
            print(
                f"Loaded Pred: {len(gdf_pred)} candidates. "
                f"Sample Source: {sample_source}"
            )
            print(f"Ref Bounds: {gdf_ref.total_bounds}")
            print(f"Pred Bounds: {gdf_pred.total_bounds}")
            print(f"Ref CRS: {gdf_ref.crs} | Pred CRS: {gdf_pred.crs}")
    except Exception as e:
        print(f"Error loading predictions: {e}")
        return

    print(f"Total Candidates: {len(gdf_pred)}")

    # 3. Filter for verified detections
    if "verified" in gdf_pred.columns:
        gdf_verified = gdf_pred[gdf_pred["verified"]]
    else:
        print(
            "Warning: 'verified' column not found. "
            "Assuming all are verified."
        )
        gdf_verified = gdf_pred

    print(f"Verified Candidates: {len(gdf_verified)}")

    if len(gdf_verified) == 0:
        print("No verified candidates found.")
        return

    # 4. Calculate F1 — ensure CRS match first
    if gdf_verified.crs != gdf_ref.crs:
        gdf_verified = gdf_verified.to_crs(gdf_ref.crs)

    p, r, f1 = calculate_f1_internal(
        gdf_verified, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )

    print("\n=== Validation Results (Symbol-Level) ===")
    print(f"Precision: {p:.4f}")
    print(f"Recall:    {r:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("==========================================")

    # 5. Calculate tile-level MCC (preregistration Section 4.2)
    tile_results = calculate_tile_classification(
        gdf_verified, gdf_ref, gdf_bounds,
    )
    tile_ci = bootstrap_tile_classification_ci(
        gdf_verified, gdf_ref, gdf_bounds,
    )

    print("\n=== Tile-Level Classification (MCC) ===")
    mcc = tile_results.get("mcc")
    sens = tile_results.get("sensitivity")
    spec = tile_results.get("specificity")
    mcc_ci = tile_ci.get("mcc", {})

    if mcc is not None:
        ci_str = ""
        if mcc_ci.get("ci_lower") is not None:
            ci_str = (
                f" (95% CI: {mcc_ci['ci_lower']:.4f}"
                f"-{mcc_ci['ci_upper']:.4f})"
            )
        print(f"MCC:         {mcc:.4f}{ci_str}")
    else:
        print("MCC:         undefined")

    if sens is not None:
        print(f"Sensitivity: {sens:.4f}")
    else:
        print("Sensitivity: undefined")
    if spec is not None:
        print(f"Specificity: {spec:.4f}")
    else:
        print("Specificity: undefined")
    print(
        f"Tiles: {tile_results['n_populated']} populated, "
        f"{tile_results['n_empty']} empty"
    )
    print("========================================")

    # 6. Save FP / FN GeoJSON files for error mining
    print("\nGenerating FP/FN files...")

    # Buffer references for spatial matching (FP/FN identification)
    gdf_ref_buf = gdf_ref.copy()
    gdf_ref_buf["geometry"] = gdf_ref_buf.geometry.buffer(buffer_metres)

    # Identify FPs: verified candidates that do not intersect any reference
    join_fp = gpd.sjoin(
        gdf_verified, gdf_ref_buf, how="left", predicate="intersects",
    )
    fps = join_fp[join_fp.index_right.isna()].copy()

    # Identify FNs: references not hit by any verified candidate.
    # Scope unbuffered references per-tile (not union -- see E7).
    refs_in_scope_unbuf = scope_references_to_tiles(gdf_ref, gdf_bounds)
    # Select only the buffered versions of in-scope references for matching
    refs_in_scope = gdf_ref_buf.loc[
        gdf_ref_buf.index.isin(refs_in_scope_unbuf.index)
    ].copy()

    join_fn = gpd.sjoin(
        refs_in_scope, gdf_verified, how="left", predicate="intersects",
    )
    fns = join_fn[join_fn.index_right.isna()].copy()

    # Recover original (unbuffered) geometry for FN output
    fns = fns.merge(
        gdf_ref[["geometry"]],
        left_index=True,
        right_index=True,
        how="left",
        suffixes=("_buf", ""),
    )
    fns.set_geometry("geometry", inplace=True)
    if "geometry_buf" in fns.columns:
        fns.drop(columns=["geometry_buf"], inplace=True)

    base_name = Path(pred_path).stem
    parent_dir = Path(pred_path).parent

    fp_path = parent_dir / f"{base_name}_fp.geojson"
    fn_path = parent_dir / f"{base_name}_fn.geojson"

    # Columns that cause serialisation errors in GeoJSON output
    drop_cols = ["index_right", "Map_left", "Map_right"]

    if not fps.empty:
        for col in drop_cols:
            if col in fps.columns:
                fps.drop(columns=[col], inplace=True)
        fps.to_file(fp_path, driver="GeoJSON")
        print(f"Saved {len(fps)} False Positives to {fp_path}")

    if not fns.empty:
        for col in drop_cols:
            if col in fns.columns:
                fns.drop(columns=[col], inplace=True)
        fns.to_file(fn_path, driver="GeoJSON")
        print(f"Saved {len(fns)} False Negatives to {fn_path}")

    # 7. Compare with unfiltered (base) predictions
    print("\n--- Comparison (Unfiltered Input) ---")
    gdf_all = gpd.read_file(pred_path)
    if not gdf_all.empty:
        gdf_all.set_crs(target_crs, allow_override=True, inplace=True)
        _normalise_source_tile(gdf_all)
    if gdf_all.crs != gdf_ref.crs:
        gdf_all = gdf_all.to_crs(gdf_ref.crs)
    p_base, r_base, f1_base = calculate_f1_internal(
        gdf_all, gdf_ref, gdf_bounds, buffer_metres=buffer_metres,
    )
    print(f"Base Precision: {p_base:.4f}")
    print(f"Base Recall:    {r_base:.4f}")
    print(f"Base F1:        {f1_base:.4f}")

    # Delta: improvement from verification filtering
    print(f"\nDelta Precision: {p - p_base:+.4f}")
    print(f"Delta Recall:    {r - r_base:+.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate accuracy report comparing detections "
            "against ground truth."
        ),
    )
    parser.add_argument(
        "--pred", required=True,
        help="Path to predicted detections GeoJSON",
    )
    parser.add_argument(
        "--bounds", required=True,
        help="Path to tile bounds GeoJSON",
    )
    parser.add_argument(
        "--template", required=True,
        help="Path to ground truth reference GeoJSON",
    )
    parser.add_argument(
        "--crs",
        default=DEFAULT_CRS,
        help=f"Target CRS for all datasets (default: {DEFAULT_CRS})",
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

    validate_file(
        args.pred, args.bounds, args.template, target_crs=args.crs,
        buffer_metres=args.buffer_metres,
    )
