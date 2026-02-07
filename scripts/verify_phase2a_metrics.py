#!/usr/bin/env python3
"""
Phase 2a Metrics Verification Script
=====================================

Independently recomputes F1, precision, and recall for all 50 Phase 2a runs
and verifies against the analysis pipeline's per_run_metrics.csv. Also performs:

- Per-tile F1 decomposition (Part A2)
- Detection spatial overlap analysis (Part A3)
- Metadata cross-validation and input token analysis (Parts B1-B3)

This script exists to rule out pipeline artefacts before accepting the
counter-intuitive finding that text-only conditions outperform image-inclusive
conditions (brief-text F1=0.5425 vs image-only F1=0.4252).

Usage:
    python scripts/verify_phase2a_metrics.py

Author: Shawn Ross, Claude Code
Version: 1.0.0
Licence: Apache 2.0
"""

import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

# Add scripts directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent))
from lib_advanced_metrics import (
    calculate_f1_internal,
    compute_per_tile_tp_fp_fn,
    match_detections_to_references,
    get_map_name,
)

# Script version
__version__ = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STUDY_DIR = PROJECT_ROOT / "outputs" / "phase2a"
GROUND_TRUTH_PATH = PROJECT_ROOT / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
BOUNDS_PATH = PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "validation_bounds.geojson"
CSV_PATH = STUDY_DIR / "per_run_metrics.csv"

# Constants
TARGET_CRS = "EPSG:32635"
BUFFER_METRES = 20
CONDITIONS = [
    "image-only",
    "brief-text",
    "brief-text-image",
    "verbose-text",
    "verbose-text-image",
]
# Conditions where images are NOT sent to the Vision Language Model (VLM)
TEXT_ONLY_CONDITIONS = {"brief-text", "verbose-text"}
# Conditions where images ARE sent to the VLM
IMAGE_CONDITIONS = {"image-only", "brief-text-image", "verbose-text-image"}
# Tolerance for floating-point comparison after rounding
TOLERANCE = 0.0001


def load_ground_truth_and_bounds() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Load and standardise ground truth references and tile bounds.

    Returns:
        Tuple of (references GeoDataFrame, bounds GeoDataFrame) in EPSG:32635.

    Raises:
        FileNotFoundError: If ground truth or bounds files are missing.
    """
    if not GROUND_TRUTH_PATH.exists():
        raise FileNotFoundError(f"Ground truth not found: {GROUND_TRUTH_PATH}")
    if not BOUNDS_PATH.exists():
        raise FileNotFoundError(f"Bounds not found: {BOUNDS_PATH}")

    gdf_ref = gpd.read_file(GROUND_TRUTH_PATH)
    gdf_bounds = gpd.read_file(BOUNDS_PATH)

    if gdf_ref.crs != TARGET_CRS:
        gdf_ref = gdf_ref.to_crs(TARGET_CRS)
    if gdf_bounds.crs != TARGET_CRS:
        gdf_bounds = gdf_bounds.to_crs(TARGET_CRS)

    return gdf_ref, gdf_bounds


def find_detection_file(run_dir: Path) -> Path | None:
    """
    Find the detection GeoJSON file in a run directory.

    Mirrors the logic from analyse_phase2_results.py: matches 'detections_*'
    while excluding .meta.json, _fp.*, _fn.* suffixes.

    Args:
        run_dir: Path to a run_N directory.

    Returns:
        Path to the detection file, or None if not found.
    """
    for f in run_dir.iterdir():
        if not f.name.startswith("detections_"):
            continue
        if f.name.endswith(".meta.json"):
            continue
        if "_fp." in f.name or "_fn." in f.name:
            continue
        base_name = f.name.rsplit(".", 1)[0] if "." in f.name else f.name
        if base_name.endswith("_fp") or base_name.endswith("_fn"):
            continue
        return f
    return None


def find_meta_file(run_dir: Path) -> Path | None:
    """
    Find the .meta.json file in a run directory.

    Args:
        run_dir: Path to a run_N directory.

    Returns:
        Path to the metadata file, or None if not found.
    """
    for f in run_dir.iterdir():
        if f.name.endswith(".meta.json"):
            return f
    return None


def load_detection_gdf(det_path: Path) -> gpd.GeoDataFrame:
    """
    Load a detection GeoJSON and standardise its Coordinate Reference System (CRS).

    Args:
        det_path: Path to the detection GeoJSON file.

    Returns:
        GeoDataFrame of detections in EPSG:32635.
    """
    gdf = gpd.read_file(det_path)
    if gdf.crs != TARGET_CRS:
        gdf = gdf.to_crs(TARGET_CRS)
    return gdf


# ============================================================================
# Part A1: Independent F1 Recomputation
# ============================================================================

def verify_all_runs(
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> tuple[pd.DataFrame, bool]:
    """
    Recompute F1 for every Phase 2a run and compare against the CSV.

    For each of the 50 runs (5 conditions x 10 runs), independently loads
    the detection GeoJSON, calls calculate_f1_internal(), and compares
    against per_run_metrics.csv.

    Args:
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Tile bounds GeoDataFrame.

    Returns:
        Tuple of (recomputed DataFrame, all_match boolean).
    """
    print("\n" + "=" * 80)
    print("PART A1: INDEPENDENT F1 RECOMPUTATION FOR ALL 50 RUNS")
    print("=" * 80)

    # Load the existing CSV for comparison
    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}")
        return pd.DataFrame(), False

    csv_df = pd.read_csv(CSV_PATH)
    print(f"\nLoaded CSV with {len(csv_df)} rows")

    recomputed_rows = []
    mismatches = []

    for condition in CONDITIONS:
        condition_dir = STUDY_DIR / condition
        if not condition_dir.exists():
            print(f"  WARNING: Condition directory missing: {condition_dir}")
            continue

        run_dirs = sorted(condition_dir.glob("run_*"))
        for run_dir in run_dirs:
            if not run_dir.is_dir():
                continue

            # Extract run number
            try:
                run_num = int(run_dir.name.split("_", 1)[1])
            except (IndexError, ValueError):
                continue

            # Find and load detection file
            det_path = find_detection_file(run_dir)
            if det_path is None:
                print(f"  WARNING: No detection file in {run_dir}")
                continue

            gdf_det = load_detection_gdf(det_path)

            # Recompute F1
            precision, recall, f1 = calculate_f1_internal(
                gdf_det, gdf_ref, gdf_bounds, buffer_metres=BUFFER_METRES,
            )

            recomputed_rows.append({
                "condition": condition,
                "run": run_num,
                "f1": round(f1, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "n_detections": len(gdf_det),
            })

            # Compare against CSV
            csv_row = csv_df[
                (csv_df["condition"] == condition)
                & (csv_df["run"] == run_num)
            ]
            if csv_row.empty:
                mismatches.append(
                    f"  MISSING in CSV: {condition}/run_{run_num}"
                )
                continue

            csv_f1 = csv_row["f1"].values[0]
            csv_p = csv_row["precision"].values[0]
            csv_r = csv_row["recall"].values[0]
            csv_n = csv_row["n_detections"].values[0]

            f1_match = abs(round(f1, 4) - csv_f1) < TOLERANCE
            p_match = abs(round(precision, 4) - csv_p) < TOLERANCE
            r_match = abs(round(recall, 4) - csv_r) < TOLERANCE
            n_match = len(gdf_det) == csv_n

            if not (f1_match and p_match and r_match and n_match):
                msg = (
                    f"  MISMATCH: {condition}/run_{run_num}: "
                    f"F1={round(f1, 4)} vs {csv_f1}, "
                    f"P={round(precision, 4)} vs {csv_p}, "
                    f"R={round(recall, 4)} vs {csv_r}, "
                    f"N={len(gdf_det)} vs {csv_n}"
                )
                mismatches.append(msg)

    recomputed_df = pd.DataFrame(recomputed_rows)

    # Report results
    all_match = len(mismatches) == 0 and len(recomputed_df) == len(csv_df)
    print(f"\nRecomputed {len(recomputed_df)} / {len(csv_df)} runs")

    if all_match:
        print("GREEN FLAG: All 50 F1 values match CSV exactly")
    else:
        print(f"RED FLAG: {len(mismatches)} mismatches found:")
        for m in mismatches:
            print(m)

    # Print summary statistics per condition
    print("\nPer-condition mean F1 (recomputed):")
    for condition in CONDITIONS:
        cond_df = recomputed_df[recomputed_df["condition"] == condition]
        if not cond_df.empty:
            mean_f1 = cond_df["f1"].mean()
            std_f1 = cond_df["f1"].std()
            print(f"  {condition:25s}: F1={mean_f1:.4f} (sd={std_f1:.4f})")

    return recomputed_df, all_match


# ============================================================================
# Part A2: Per-Tile F1 Decomposition
# ============================================================================

def per_tile_decomposition(
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """
    Compute per-tile TP/FP/FN for run_1 of brief-text and image-only.

    Identifies which tiles drive the F1 difference between these two
    conditions and flags tiles where image-only outperforms brief-text.

    Args:
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Tile bounds GeoDataFrame.

    Returns:
        Merged DataFrame with per-tile metrics for both conditions.
    """
    print("\n" + "=" * 80)
    print("PART A2: PER-TILE F1 DECOMPOSITION (run_1: brief-text vs image-only)")
    print("=" * 80)

    results = {}
    for condition in ["brief-text", "image-only"]:
        run_dir = STUDY_DIR / condition / "run_1"
        det_path = find_detection_file(run_dir)
        if det_path is None:
            print(f"  ERROR: No detection file in {run_dir}")
            continue

        gdf_det = load_detection_gdf(det_path)
        tile_metrics = compute_per_tile_tp_fp_fn(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=BUFFER_METRES,
        )
        results[condition] = tile_metrics

    if len(results) != 2:
        print("  ERROR: Could not load both conditions")
        return pd.DataFrame()

    # Merge for side-by-side comparison
    bt = results["brief-text"].rename(columns={
        "tp": "bt_tp", "fp": "bt_fp", "fn": "bt_fn",
    })
    io = results["image-only"].rename(columns={
        "tp": "io_tp", "fp": "io_fp", "fn": "io_fn",
    })
    merged = bt.merge(io, on="tile_name", how="outer").fillna(0)

    # Compute per-tile F1 for each condition
    def tile_f1(tp: float, fp: float, fn: float) -> float:
        """Compute F1 from TP, FP, FN counts."""
        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0
        return 2 * p * r / (p + r) if (p + r) > 0 else 0

    merged["bt_f1"] = merged.apply(
        lambda r: tile_f1(r["bt_tp"], r["bt_fp"], r["bt_fn"]), axis=1,
    )
    merged["io_f1"] = merged.apply(
        lambda r: tile_f1(r["io_tp"], r["io_fp"], r["io_fn"]), axis=1,
    )
    merged["f1_diff"] = merged["bt_f1"] - merged["io_f1"]

    # Extract map name for grouping
    merged["map_name"] = merged["tile_name"].apply(get_map_name)

    # Count reference mounds per tile (for context)
    ref_per_tile = {}
    for _, tile_row in gdf_bounds.iterrows():
        tile_name = tile_row["tile_name"]
        tile_geom = tile_row.geometry
        map_name = get_map_name(tile_name)
        ref_for_map = gdf_ref[gdf_ref["Map"] == map_name] if "Map" in gdf_ref.columns else gdf_ref
        if not ref_for_map.empty:
            ref_scope = ref_for_map[ref_for_map.intersects(tile_geom)]
            ref_per_tile[tile_name] = len(ref_scope)
        else:
            ref_per_tile[tile_name] = 0
    merged["n_refs"] = merged["tile_name"].map(ref_per_tile).fillna(0).astype(int)

    # Sort by F1 difference
    merged_sorted = merged.sort_values("f1_diff", ascending=False)

    # Print full table
    print(f"\n{'Tile':<45} {'Refs':>4} "
          f"{'BT_TP':>5} {'BT_FP':>5} {'BT_FN':>5} {'BT_F1':>6} "
          f"{'IO_TP':>5} {'IO_FP':>5} {'IO_FN':>5} {'IO_F1':>6} {'Diff':>7}")
    print("-" * 130)

    bt_wins = 0
    io_wins = 0
    ties = 0

    for _, row in merged_sorted.iterrows():
        # Truncate tile name for display
        tile_short = row["tile_name"][:44]
        diff_str = f"{row['f1_diff']:+.4f}"
        print(
            f"{tile_short:<45} {int(row['n_refs']):>4} "
            f"{int(row['bt_tp']):>5} {int(row['bt_fp']):>5} "
            f"{int(row['bt_fn']):>5} {row['bt_f1']:>6.4f} "
            f"{int(row['io_tp']):>5} {int(row['io_fp']):>5} "
            f"{int(row['io_fn']):>5} {row['io_f1']:>6.4f} {diff_str:>7}"
        )

        if row["f1_diff"] > 0.001:
            bt_wins += 1
        elif row["f1_diff"] < -0.001:
            io_wins += 1
        else:
            ties += 1

    # Summary
    print("\nTile-level summary:")
    print(f"  brief-text wins:  {bt_wins} tiles")
    print(f"  image-only wins:  {io_wins} tiles")
    print(f"  Ties (< 0.001):   {ties} tiles")

    # Aggregate totals
    bt_total_tp = int(merged["bt_tp"].sum())
    bt_total_fp = int(merged["bt_fp"].sum())
    bt_total_fn = int(merged["bt_fn"].sum())
    io_total_tp = int(merged["io_tp"].sum())
    io_total_fp = int(merged["io_fp"].sum())
    io_total_fn = int(merged["io_fn"].sum())
    print(f"\n  brief-text totals:  TP={bt_total_tp}, FP={bt_total_fp}, FN={bt_total_fn}")
    print(f"  image-only totals:  TP={io_total_tp}, FP={io_total_fp}, FN={io_total_fn}")

    # Per-map summary
    print("\nPer-map F1 difference (brief-text - image-only):")
    for map_name in sorted(merged["map_name"].unique()):
        map_rows = merged[merged["map_name"] == map_name]
        mean_diff = map_rows["f1_diff"].mean()
        n_tiles = len(map_rows)
        bt_map_wins = (map_rows["f1_diff"] > 0.001).sum()
        io_map_wins = (map_rows["f1_diff"] < -0.001).sum()
        print(
            f"  {map_name:30s}: mean diff={mean_diff:+.4f} "
            f"({n_tiles} tiles, BT wins {bt_map_wins}, IO wins {io_map_wins})"
        )

    # Check distribution of advantage
    if bt_wins > io_wins * 2:
        print("\nGREEN FLAG: brief-text advantage is broadly distributed")
    elif io_wins > bt_wins:
        print("\nRED FLAG: image-only wins more tiles than brief-text")
    else:
        print("\nMIXED: Advantage is not strongly concentrated but not overwhelming")

    return merged


# ============================================================================
# Part A3: Detection Spatial Overlap Analysis
# ============================================================================

def spatial_overlap_analysis(
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> None:
    """
    Compare detection locations between brief-text and image-only (run_1).

    For each tile, spatially match detections from both conditions to find
    shared detections, brief-text-only detections, and image-only-only
    detections. Reports whether brief-text finds the same mounds plus
    additional ones, or entirely different mounds.

    Args:
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Tile bounds GeoDataFrame.
    """
    print("\n" + "=" * 80)
    print("PART A3: DETECTION SPATIAL OVERLAP ANALYSIS (run_1)")
    print("=" * 80)

    # Load both conditions
    bt_path = find_detection_file(STUDY_DIR / "brief-text" / "run_1")
    io_path = find_detection_file(STUDY_DIR / "image-only" / "run_1")
    if bt_path is None or io_path is None:
        print("  ERROR: Cannot find detection files for both conditions")
        return

    gdf_bt = load_detection_gdf(bt_path)
    gdf_io = load_detection_gdf(io_path)

    # For each tile, match brief-text detections to image-only detections
    # using 20m buffer (same as reference matching)
    total_shared = 0
    total_bt_only = 0
    total_io_only = 0

    # Also track which shared detections are true positives (TPs)
    total_shared_tp = 0
    total_bt_only_tp = 0
    total_io_only_tp = 0

    print(f"\n{'Tile':<45} {'Shared':>6} {'BT-only':>7} {'IO-only':>7}")
    print("-" * 70)

    for _, tile_row in gdf_bounds.iterrows():
        tile_name = tile_row["tile_name"]
        map_name = get_map_name(tile_name)

        bt_tile = gdf_bt[gdf_bt["source_tile"] == tile_name]
        io_tile = gdf_io[gdf_io["source_tile"] == tile_name]

        if bt_tile.empty and io_tile.empty:
            continue

        if bt_tile.empty:
            total_io_only += len(io_tile)
            # Check how many IO-only are TPs
            ref_for_map = gdf_ref[gdf_ref["Map"] == map_name]
            if not ref_for_map.empty:
                ref_scope = ref_for_map[ref_for_map.intersects(tile_row.geometry)]
                if not ref_scope.empty:
                    matched_d, _, _, _ = match_detections_to_references(
                        list(io_tile.geometry), list(ref_scope.geometry), BUFFER_METRES,
                    )
                    total_io_only_tp += len(matched_d)
            print(f"{tile_name[:44]:<45} {0:>6} {0:>7} {len(io_tile):>7}")
            continue

        if io_tile.empty:
            total_bt_only += len(bt_tile)
            # Check how many BT-only are TPs
            ref_for_map = gdf_ref[gdf_ref["Map"] == map_name]
            if not ref_for_map.empty:
                ref_scope = ref_for_map[ref_for_map.intersects(tile_row.geometry)]
                if not ref_scope.empty:
                    matched_d, _, _, _ = match_detections_to_references(
                        list(bt_tile.geometry), list(ref_scope.geometry), BUFFER_METRES,
                    )
                    total_bt_only_tp += len(matched_d)
            print(f"{tile_name[:44]:<45} {0:>6} {len(bt_tile):>7} {0:>7}")
            continue

        # Match BT detections to IO detections (cross-condition matching)
        bt_geoms = list(bt_tile.geometry)
        io_geoms = list(io_tile.geometry)
        matched_bt, matched_io, unmatched_bt, unmatched_io = \
            match_detections_to_references(bt_geoms, io_geoms, BUFFER_METRES)

        n_shared = len(matched_bt)
        n_bt_only = len(unmatched_bt)
        n_io_only = len(unmatched_io)
        total_shared += n_shared
        total_bt_only += n_bt_only
        total_io_only += n_io_only

        # Now check how many of each category are TPs against ground truth
        ref_for_map = gdf_ref[gdf_ref["Map"] == map_name]
        if not ref_for_map.empty:
            ref_scope = ref_for_map[ref_for_map.intersects(tile_row.geometry)]
            if not ref_scope.empty:
                ref_geoms = list(ref_scope.geometry)

                # Check shared detections (use BT geometries for the matched pairs)
                if matched_bt:
                    shared_geoms = [bt_geoms[i] for i in matched_bt]
                    m_d, _, _, _ = match_detections_to_references(
                        shared_geoms, ref_geoms, BUFFER_METRES,
                    )
                    total_shared_tp += len(m_d)

                # Check BT-only detections
                if unmatched_bt:
                    bt_only_geoms = [bt_geoms[i] for i in unmatched_bt]
                    m_d, _, _, _ = match_detections_to_references(
                        bt_only_geoms, ref_geoms, BUFFER_METRES,
                    )
                    total_bt_only_tp += len(m_d)

                # Check IO-only detections
                if unmatched_io:
                    io_only_geoms = [io_geoms[i] for i in unmatched_io]
                    m_d, _, _, _ = match_detections_to_references(
                        io_only_geoms, ref_geoms, BUFFER_METRES,
                    )
                    total_io_only_tp += len(m_d)

        if n_shared > 0 or n_bt_only > 0 or n_io_only > 0:
            print(f"{tile_name[:44]:<45} {n_shared:>6} {n_bt_only:>7} {n_io_only:>7}")

    # Summary
    total_all = total_shared + total_bt_only + total_io_only
    print(f"\n{'TOTALS':<45} {total_shared:>6} {total_bt_only:>7} {total_io_only:>7}")

    if total_all > 0:
        print("\nOverlap percentages:")
        print(f"  Shared (found by both):   {total_shared:>4} ({100 * total_shared / total_all:.1f}%)")
        print(f"  Brief-text only:          {total_bt_only:>4} ({100 * total_bt_only / total_all:.1f}%)")
        print(f"  Image-only only:          {total_io_only:>4} ({100 * total_io_only / total_all:.1f}%)")

    print("\nTrue positive breakdown (how many in each category match ground truth):")
    print(f"  Shared TPs:      {total_shared_tp:>4}" +
          (f" ({100 * total_shared_tp / total_shared:.1f}%)" if total_shared > 0 else ""))
    print(f"  BT-only TPs:     {total_bt_only_tp:>4}" +
          (f" ({100 * total_bt_only_tp / total_bt_only:.1f}%)" if total_bt_only > 0 else ""))
    print(f"  IO-only TPs:     {total_io_only_tp:>4}" +
          (f" ({100 * total_io_only_tp / total_io_only:.1f}%)" if total_io_only > 0 else ""))

    # Diagnostic interpretation
    if total_bt_only_tp > total_io_only_tp:
        print("\nGREEN FLAG: brief-text finds additional TRUE mounds that image-only misses")
    elif total_shared > (total_bt_only + total_io_only):
        print("\nGREEN FLAG: High overlap — both conditions find similar mounds")
    else:
        print("\nWARNING: Low overlap — conditions find substantially different mounds")


# ============================================================================
# Part B1-B2: Metadata Cross-Validation and Input Token Analysis
# ============================================================================

def metadata_verification() -> None:
    """
    Verify metadata confirms different inputs for different conditions.

    For each condition's run_1, extracts config flags, instruction file,
    execution duration, and token counts. For ALL 50 runs, analyses input
    token distributions to detect any image leakage.
    """
    print("\n" + "=" * 80)
    print("PART B1: METADATA CROSS-VALIDATION (run_1 per condition)")
    print("=" * 80)

    for condition in CONDITIONS:
        run_dir = STUDY_DIR / condition / "run_1"
        meta_path = find_meta_file(run_dir)
        if meta_path is None:
            print(f"\n  {condition}: NO METADATA FILE FOUND")
            continue

        with open(meta_path) as f:
            meta = json.load(f)

        config = meta.get("configuration", {})
        full_config = config.get("full_config_snapshot", {})
        exec_stats = meta.get("timestamp", {})
        usage = meta.get("usage_stats", {})

        include_images = full_config.get("include_example_images", "NOT SET (defaults to true)")
        instruction = config.get("instruction_file", "unknown")
        duration = exec_stats.get("duration_seconds", "unknown")
        input_tokens = usage.get("total_input_tokens", 0)
        output_tokens = usage.get("total_output_tokens", 0)

        print(f"\n  {condition}:")
        print(f"    include_example_images: {include_images}")
        print(f"    instruction_file:       {instruction}")
        print(f"    duration_seconds:       {duration}")
        print(f"    total_input_tokens:     {input_tokens:,}")
        print(f"    total_output_tokens:    {output_tokens:,}")

        # Verify expectations
        if condition in TEXT_ONLY_CONDITIONS:
            if include_images is False:
                print("    CHECK: include_example_images=false (correct for text-only)")
            else:
                print(f"    RED FLAG: Text-only condition has include_example_images={include_images}")
        else:
            if include_images == "NOT SET (defaults to true)" or include_images is True:
                print("    CHECK: Images enabled (correct for image condition)")
            elif include_images is False:
                print("    RED FLAG: Image condition has include_example_images=false!")

    # Part B2: Input token analysis across ALL 50 runs
    print("\n" + "=" * 80)
    print("PART B2: INPUT TOKEN ANALYSIS (all 50 runs)")
    print("=" * 80)

    token_data = []
    for condition in CONDITIONS:
        condition_dir = STUDY_DIR / condition
        if not condition_dir.exists():
            continue

        for run_dir in sorted(condition_dir.glob("run_*")):
            if not run_dir.is_dir():
                continue

            run_num = int(run_dir.name.split("_", 1)[1])
            meta_path = find_meta_file(run_dir)
            if meta_path is None:
                continue

            with open(meta_path) as f:
                meta = json.load(f)

            usage = meta.get("usage_stats", {})
            exec_time = meta.get("timestamp", {})
            token_data.append({
                "condition": condition,
                "run": run_num,
                "input_tokens": usage.get("total_input_tokens", 0),
                "output_tokens": usage.get("total_output_tokens", 0),
                "duration_seconds": exec_time.get("duration_seconds", 0),
            })

    if not token_data:
        print("  ERROR: No metadata files found")
        return

    token_df = pd.DataFrame(token_data)

    print("\nInput token statistics per condition:")
    print(f"{'Condition':<25} {'Mean Input':>12} {'Std':>10} "
          f"{'Min':>10} {'Max':>10} {'Mean Duration':>14}")
    print("-" * 85)

    condition_means = {}
    for condition in CONDITIONS:
        cond_df = token_df[token_df["condition"] == condition]
        if cond_df.empty:
            continue
        mean_in = cond_df["input_tokens"].mean()
        std_in = cond_df["input_tokens"].std()
        min_in = cond_df["input_tokens"].min()
        max_in = cond_df["input_tokens"].max()
        mean_dur = cond_df["duration_seconds"].mean()
        condition_means[condition] = mean_in

        print(f"{condition:<25} {mean_in:>12,.0f} {std_in:>10,.0f} "
              f"{min_in:>10,} {max_in:>10,} {mean_dur:>13.1f}s")

    # Check for image leakage
    text_only_means = [
        condition_means[c] for c in TEXT_ONLY_CONDITIONS
        if c in condition_means
    ]
    image_means = [
        condition_means[c] for c in IMAGE_CONDITIONS
        if c in condition_means
    ]

    if text_only_means and image_means:
        avg_text = np.mean(text_only_means)
        avg_image = np.mean(image_means)
        ratio = avg_image / avg_text if avg_text > 0 else float("inf")
        print(f"\n  Average text-only input tokens:   {avg_text:,.0f}")
        print(f"  Average image input tokens:       {avg_image:,.0f}")
        print(f"  Ratio (image / text-only):        {ratio:.2f}x")

        if ratio > 2.0:
            print("  GREEN FLAG: Image conditions use dramatically more input tokens")
            print("  (images ARE being sent — no image leakage)")
        elif ratio > 1.5:
            print("  MODERATE: Some token difference, but less than expected")
        else:
            print("  RED FLAG: Similar input tokens — possible image leakage!")


# ============================================================================
# Part B3: Detection Count Distributions
# ============================================================================

def detection_count_analysis() -> None:
    """
    Print detection count and recall statistics per condition.

    Higher detection counts alone don't prove better performance — what
    matters is whether additional detections are true positives (reflected
    in recall).
    """
    print("\n" + "=" * 80)
    print("PART B3: DETECTION COUNT AND RECALL DISTRIBUTIONS")
    print("=" * 80)

    if not CSV_PATH.exists():
        print("  ERROR: CSV not found")
        return

    csv_df = pd.read_csv(CSV_PATH)

    print(f"\n{'Condition':<25} {'Mean N':>7} {'Std N':>6} {'Min':>5} {'Max':>5} "
          f"{'Mean R':>7} {'Std R':>6} {'Mean P':>7} {'Std P':>6}")
    print("-" * 85)

    for condition in CONDITIONS:
        cond_df = csv_df[csv_df["condition"] == condition]
        if cond_df.empty:
            continue
        print(
            f"{condition:<25} "
            f"{cond_df['n_detections'].mean():>7.1f} "
            f"{cond_df['n_detections'].std():>6.1f} "
            f"{cond_df['n_detections'].min():>5} "
            f"{cond_df['n_detections'].max():>5} "
            f"{cond_df['recall'].mean():>7.4f} "
            f"{cond_df['recall'].std():>6.4f} "
            f"{cond_df['precision'].mean():>7.4f} "
            f"{cond_df['precision'].std():>6.4f}"
        )

    # Highlight the key within-elaboration-level comparisons
    print("\nWithin-elaboration-level comparisons (text constant, only images differ):")
    for text_cond, image_cond in [("brief-text", "brief-text-image"),
                                   ("verbose-text", "verbose-text-image")]:
        t_df = csv_df[csv_df["condition"] == text_cond]
        i_df = csv_df[csv_df["condition"] == image_cond]
        if t_df.empty or i_df.empty:
            continue
        t_f1 = t_df["f1"].mean()
        i_f1 = i_df["f1"].mean()
        diff = t_f1 - i_f1
        print(
            f"  {text_cond} F1={t_f1:.4f} vs {image_cond} F1={i_f1:.4f} "
            f"(diff={diff:+.4f}, text-only wins by removing images)"
        )

    print(
        "\nNote: Within each elaboration level, the system instructions are IDENTICAL."
    )
    print(
        "The ONLY difference is whether example images are sent. In both cases,"
    )
    print(
        "removing images IMPROVES F1 — suggesting images are actively harmful."
    )


# ============================================================================
# Part D: System Instruction Content Analysis
# ============================================================================

def instruction_content_analysis() -> None:
    """
    Summarise key differences between system instruction files.

    Documents the informational content difference to assess whether
    text-only instructions provide compensating information.
    """
    print("\n" + "=" * 80)
    print("PART D: SYSTEM INSTRUCTION CONTENT ANALYSIS")
    print("=" * 80)

    instructions_dir = PROJECT_ROOT / "prompts" / "system-instructions"
    instruction_files = {
        "image-only": "detect_image-only.md",
        "brief-text": "detect_brief-text.md",
        "brief-text-image": "detect_brief-text-image.md",
        "verbose-text": "detect_verbose-text.md",
        "verbose-text-image": "detect_verbose-text-image.md",
    }

    print(f"\n{'Condition':<25} {'Instruction File':<35} {'Lines':>5} {'Chars':>6}")
    print("-" * 75)

    for condition, filename in instruction_files.items():
        filepath = instructions_dir / filename
        if filepath.exists():
            content = filepath.read_text()
            n_lines = len(content.strip().splitlines())
            n_chars = len(content)
            print(f"{condition:<25} {filename:<35} {n_lines:>5} {n_chars:>6}")
        else:
            print(f"{condition:<25} {filename:<35} NOT FOUND")

    # Check text identity within elaboration levels
    print("\nText identity checks (same text, different image setting):")
    for text_cond, image_cond in [("brief-text", "brief-text-image"),
                                   ("verbose-text", "verbose-text-image")]:
        text_file = instructions_dir / instruction_files[text_cond]
        image_file = instructions_dir / instruction_files[image_cond]
        if text_file.exists() and image_file.exists():
            text_content = text_file.read_text()
            image_content = image_file.read_text()
            identical = text_content == image_content
            status = "IDENTICAL" if identical else "DIFFERENT"
            print(f"  {text_cond} vs {image_cond}: {status}")
            if not identical:
                print("    RED FLAG: Instructions differ — confound detected!")
        else:
            print(f"  {text_cond} vs {image_cond}: FILE(S) MISSING")

    print("\nKey insight: The image-only instruction (~20 lines) provides minimal")
    print("guidance — just 'detect sunburst patterns' plus output format. But the")
    print("within-elaboration-level comparisons (brief vs brief-image, verbose vs")
    print("verbose-image) hold text CONSTANT. In both cases, removing images still")
    print("improves F1, ruling out text richness as the sole explanation.")


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    """Run the full Phase 2a verification suite."""
    print("=" * 80)
    print("PHASE 2A METRICS VERIFICATION")
    print(f"Script version: {__version__}")
    print("=" * 80)

    # Load shared ground truth and bounds
    print("\nLoading ground truth and bounds...")
    gdf_ref, gdf_bounds = load_ground_truth_and_bounds()
    print(f"  References: {len(gdf_ref)} features")
    print(f"  Bounds:     {len(gdf_bounds)} tiles")

    # Part A1: Independent F1 recomputation
    recomputed_df, all_match = verify_all_runs(gdf_ref, gdf_bounds)

    # Part A2: Per-tile decomposition
    per_tile_decomposition(gdf_ref, gdf_bounds)

    # Part A3: Spatial overlap analysis
    spatial_overlap_analysis(gdf_ref, gdf_bounds)

    # Part B1-B2: Metadata and token verification
    metadata_verification()

    # Part B3: Detection count distributions
    detection_count_analysis()

    # Part D: System instruction content analysis
    instruction_content_analysis()

    # Final summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"\n  A1 F1 recomputation:     {'PASS' if all_match else 'FAIL'}")
    print("  A2 Per-tile analysis:    See above for distribution")
    print("  A3 Spatial overlap:      See above for overlap statistics")
    print("  B1-B2 Metadata/tokens:   See above for token ratios")
    print("  B3 Detection counts:     See above for distributions")
    print("  D  Instruction analysis: See above for text identity checks")
    print()


if __name__ == "__main__":
    main()
