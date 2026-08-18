#!/usr/bin/env python3
"""
Evaluate Pro HIGH text N=10 consensus conditions.

Computes F1/P/R with bootstrap CIs at 20/30/40/50m buffers, plus
tile-level MCC with bootstrap CIs, for Pro N=10 at multiple consensus
thresholds. Outputs CSV suitable for merging into metrics_master.csv.

Run on sapphire:
    python scripts/evaluate-pro-n10.py

Author: Shawn Ross, Claude Code
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib_advanced_metrics import (
    bootstrap_ci,
)
from evaluate_tile_mcc import (
    calculate_tile_classification,
    bootstrap_tile_classification_ci,
)
from lib_detection_paths import find_pass_geojsons

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────

PROJECT = Path(__file__).parent.parent
STUDY_DIR = PROJECT / "outputs/h11/pv-diag-384/pro-high-text-n5"
GROUND_TRUTH = PROJECT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS = PROJECT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUTPUT_DIR = PROJECT / "results/paper-eval/pro-n10"

BUFFERS = [20, 30, 40, 50]
POOL_SIZES = [5, 10]
BOOTSTRAP = 1000
SEED = 42
CONDITION_NAME = "text-t0.7"

# Rendered wherever a tile-level metric is not computable (erratum
# E81). Matches ``evaluate_detections.UNDEFINED_DISPLAY``.
UNDEFINED_DISPLAY = "undefined"


def _safe_round(val: float | None, digits: int = 4) -> float | None:
    """Round a possibly-undefined tile metric, preserving ``None``.

    Args:
        val: The metric, or ``None`` when it is undefined (degenerate
            2 x 2 tile confusion matrix — erratum E81).
        digits: Decimal places.

    Returns:
        The rounded float, or ``None``. ``csv.DictWriter`` renders
        ``None`` as an empty cell, which is the only honest CSV
        representation of a metric that was not computable; a genuine
        0.0 still comes through as ``0.0``.
    """
    return None if val is None else round(val, digits)


def _fmt_metric(val: float | None, digits: int = 3) -> str:
    """Format a possibly-undefined tile metric for console output.

    Args:
        val: The metric, or ``None`` when it is undefined.
        digits: Decimal places for the numeric case.

    Returns:
        The formatted number, or :data:`UNDEFINED_DISPLAY`.
    """
    return UNDEFINED_DISPLAY if val is None else f"{val:.{digits}f}"

# ── Consensus clustering (from analyse_consensus_sweep.py) ──────────


def load_runs(
    study_dir: Path,
    condition: str,
    max_runs: int | None = None,
) -> list[gpd.GeoDataFrame]:
    """Load individual run detection GeoJSONs.

    Per-pass files are resolved through
    ``lib_detection_paths.find_pass_geojsons``, which expands both naming
    conventions; the previous single-convention glob under-read any pool
    holding real-time passes (defect D6).

    Args:
        study_dir: Study output directory holding condition subdirectories.
        condition: Condition name (a subdirectory of ``study_dir``).
        max_runs: Optional cap on the number of run directories loaded.

    Returns:
        One GeoDataFrame per run, tagged with a ``run_id`` column.
    """
    condition_dir = study_dir / condition
    run_dirs = sorted(condition_dir.glob("run_*"))
    if max_runs:
        run_dirs = run_dirs[:max_runs]

    gdfs = []
    for run_dir in run_dirs:
        geojsons = find_pass_geojsons(run_dir)
        if not geojsons:
            log.warning("No GeoJSON in %s", run_dir)
            continue
        gdf = gpd.read_file(geojsons[0])
        gdf["run_id"] = run_dir.name
        gdfs.append(gdf)
        log.info(
            "  %s: %d detections",
            run_dir.name,
            len(gdf),
        )

    return gdfs


def cluster_detections(
    gdfs: list[gpd.GeoDataFrame],
    eps_metres: float = 30.0,
    min_samples: int = 1,
) -> gpd.GeoDataFrame:
    """
    Cluster detections from multiple runs using DBSCAN.

    Returns a GeoDataFrame with one row per cluster, including
    vote_count (how many runs contributed to that cluster).
    """
    from sklearn.cluster import DBSCAN

    # Combine all detections
    combined = gpd.GeoDataFrame(
        pd.concat(gdfs, ignore_index=True),
        crs=gdfs[0].crs,
    )

    # Get centroids for clustering
    centroids = np.column_stack([
        combined.geometry.centroid.x,
        combined.geometry.centroid.y,
    ])

    # DBSCAN clustering
    clustering = DBSCAN(
        eps=eps_metres,
        min_samples=min_samples,
        metric="euclidean",
    ).fit(centroids)

    combined["cluster_id"] = clustering.labels_

    # Aggregate: one detection per cluster
    clusters = []
    for cid in sorted(combined["cluster_id"].unique()):
        if cid == -1:
            continue  # noise points
        members = combined[combined["cluster_id"] == cid]
        # Use centroid of cluster as detection location
        cx = members.geometry.centroid.x.mean()
        cy = members.geometry.centroid.y.mean()
        vote_count = members["run_id"].nunique()
        # Inherit source_tile from the most central member
        source_tile = members.iloc[0].get("source_tile", "")
        clusters.append({
            "geometry": gpd.points_from_xy([cx], [cy])[0],
            "vote_count": vote_count,
            "source_tile": source_tile,
            "n_members": len(members),
        })

    result = gpd.GeoDataFrame(clusters, crs=gdfs[0].crs)
    log.info(
        "  Clustered %d detections into %d clusters",
        len(combined),
        len(result),
    )
    return result


def apply_threshold(
    clustered: gpd.GeoDataFrame,
    threshold: int,
) -> gpd.GeoDataFrame:
    """Filter consensus detections by vote threshold."""
    return clustered[clustered["vote_count"] >= threshold].copy()


# ── Main ─────────────────────────────────────────────────────────────

import pandas as pd


def main() -> None:
    """Run the complete Pro N=10 evaluation."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load ground truth and bounds
    log.info("Loading ground truth: %s", GROUND_TRUTH)
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    log.info("Loading bounds: %s", BOUNDS)
    gdf_bounds = gpd.read_file(BOUNDS)
    log.info(
        "Reference: %d mounds, %d tiles",
        len(gdf_ref),
        len(gdf_bounds),
    )

    # Ensure same CRS
    target_crs = gdf_bounds.crs
    if gdf_ref.crs != target_crs:
        gdf_ref = gdf_ref.to_crs(target_crs)

    # Load all 10 runs
    log.info("Loading runs from %s/%s", STUDY_DIR, CONDITION_NAME)
    all_runs = load_runs(STUDY_DIR, CONDITION_NAME)
    log.info("Loaded %d runs", len(all_runs))

    # Cluster all detections
    log.info("Clustering detections (eps=30m)...")
    clustered = cluster_detections(all_runs)
    if clustered.crs != target_crs:
        clustered = clustered.to_crs(target_crs)

    # Results table
    results = []

    for pool_size in POOL_SIZES:
        log.info("=== Pool size N=%d ===", pool_size)

        # For N=5, use runs 1-5; for N=10, use all
        if pool_size < len(all_runs):
            subset_runs = all_runs[:pool_size]
            subset_clustered = cluster_detections(subset_runs)
            if subset_clustered.crs != target_crs:
                subset_clustered = subset_clustered.to_crs(target_crs)
        else:
            subset_clustered = clustered

        # Evaluate each threshold
        max_threshold = pool_size
        for threshold in range(1, max_threshold + 1):
            detections = apply_threshold(subset_clustered, threshold)
            n_det = len(detections)

            if n_det == 0:
                log.info(
                    "  %d-of-%d: 0 detections, skipping",
                    threshold,
                    pool_size,
                )
                continue

            log.info(
                "  %d-of-%d: %d detections",
                threshold,
                pool_size,
                n_det,
            )

            # Evaluate at each buffer
            for buffer_m in BUFFERS:
                # F1/P/R with bootstrap CIs
                ci_result = bootstrap_ci(
                    detections,
                    gdf_ref,
                    gdf_bounds,
                    buffer_metres=buffer_m,
                    n_iterations=BOOTSTRAP,
                    random_seed=SEED,
                )

                row = {
                    "condition_type": "consensus",
                    "condition_label": "pro-high-text",
                    "pool_size": pool_size,
                    "buffer_metres": buffer_m,
                    "config_details": (
                        f"N={pool_size}, "
                        f"{threshold}-of-{pool_size}"
                    ),
                    "f1": round(ci_result["f1"]["mean"], 4),
                    "f1_ci_lower": round(
                        ci_result["f1"]["ci_lower"], 4,
                    ),
                    "f1_ci_upper": round(
                        ci_result["f1"]["ci_upper"], 4,
                    ),
                    "precision": round(
                        ci_result["precision"]["mean"], 4,
                    ),
                    "p_ci_lower": round(
                        ci_result["precision"]["ci_lower"], 4,
                    ),
                    "p_ci_upper": round(
                        ci_result["precision"]["ci_upper"], 4,
                    ),
                    "recall": round(
                        ci_result["recall"]["mean"], 4,
                    ),
                    "r_ci_lower": round(
                        ci_result["recall"]["ci_lower"], 4,
                    ),
                    "r_ci_upper": round(
                        ci_result["recall"]["ci_upper"], 4,
                    ),
                    "n_detections": n_det,
                }

                results.append(row)

            # MCC at primary buffer (20m) — tile-level
            tile_class = calculate_tile_classification(
                detections, gdf_ref, gdf_bounds,
            )
            tile_ci = bootstrap_tile_classification_ci(
                detections, gdf_ref, gdf_bounds,
                n_iterations=BOOTSTRAP,
                random_seed=SEED,
            )

            # Attach MCC to the 20m row
            for r in results:
                if (
                    r["pool_size"] == pool_size
                    and r["config_details"]
                    == f"N={pool_size}, {threshold}-of-{pool_size}"
                    and r["buffer_metres"] == 20
                ):
                    # Erratum E81 (2026-08-18): these used to read
                    # ``round(x or 0, 4)``, which published an
                    # *undefined* tile metric — the 2 x 2 tile
                    # confusion matrix is degenerate, so MCC has no
                    # value — as 0.0, indistinguishable from the
                    # chance-level result § 4.2 of the preregistration
                    # says 0 means. ``_safe_round`` keeps ``None``,
                    # which csv.DictWriter renders as an empty cell.
                    r["mcc"] = _safe_round(tile_class.get("mcc"))
                    mcc_ci = tile_ci.get("mcc", {})
                    r["mcc_ci_lower"] = _safe_round(mcc_ci.get("ci_lower"))
                    r["mcc_ci_upper"] = _safe_round(mcc_ci.get("ci_upper"))
                    r["sensitivity"] = _safe_round(
                        tile_class.get("sensitivity"),
                    )
                    r["specificity"] = _safe_round(
                        tile_class.get("specificity"),
                    )
                    r["tp"] = tile_class.get("tp", 0)
                    r["tn"] = tile_class.get("tn", 0)
                    r["fp"] = tile_class.get("fp", 0)
                    r["fn"] = tile_class.get("fn", 0)

            log.info(
                "    20m: F1=%.3f P=%.3f R=%.3f MCC=%s",
                [
                    r
                    for r in results
                    if r["buffer_metres"] == 20
                    and r["config_details"]
                    == f"N={pool_size}, {threshold}-of-{pool_size}"
                ][0]["f1"],
                [
                    r
                    for r in results
                    if r["buffer_metres"] == 20
                    and r["config_details"]
                    == f"N={pool_size}, {threshold}-of-{pool_size}"
                ][0]["precision"],
                [
                    r
                    for r in results
                    if r["buffer_metres"] == 20
                    and r["config_details"]
                    == f"N={pool_size}, {threshold}-of-{pool_size}"
                ][0]["recall"],
                # Erratum E81: the word, not a numeral, when the tile
                # MCC is not computable for this configuration.
                _fmt_metric(
                    [
                        r
                        for r in results
                        if r["buffer_metres"] == 20
                        and r["config_details"]
                        == f"N={pool_size}, {threshold}-of-{pool_size}"
                    ][0].get("mcc"),
                ),
            )

    # Write results CSV
    output_csv = OUTPUT_DIR / "pro_n10_consensus_results.csv"
    fieldnames = [
        "condition_type",
        "condition_label",
        "pool_size",
        "buffer_metres",
        "config_details",
        "f1",
        "f1_ci_lower",
        "f1_ci_upper",
        "precision",
        "p_ci_lower",
        "p_ci_upper",
        "recall",
        "r_ci_lower",
        "r_ci_upper",
        "n_detections",
        "mcc",
        "mcc_ci_lower",
        "mcc_ci_upper",
        "sensitivity",
        "specificity",
        "tp",
        "tn",
        "fp",
        "fn",
    ]
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(results)

    log.info("Results written to %s", output_csv)

    # Print summary: best threshold at 20m for each pool size
    print("\n" + "=" * 70)
    print("SUMMARY: Best consensus threshold at 20m for each pool size")
    print("=" * 70)
    for pool_size in POOL_SIZES:
        pool_rows = [
            r
            for r in results
            if r["pool_size"] == pool_size
            and r["buffer_metres"] == 20
        ]
        if pool_rows:
            best = max(pool_rows, key=lambda r: r["f1"])
            print(
                f"  N={pool_size}: {best['config_details']} "
                f"F1={best['f1']:.3f} "
                f"[{best['f1_ci_lower']:.3f}, "
                f"{best['f1_ci_upper']:.3f}] "
                f"P={best['precision']:.3f} "
                f"R={best['recall']:.3f} "
                f"MCC={_fmt_metric(best.get('mcc'))}"
            )

    # Write metadata
    meta = {
        "script": "evaluate-pro-n10.py",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "study_dir": str(STUDY_DIR),
        "n_runs": len(all_runs),
        "pool_sizes": POOL_SIZES,
        "buffers": BUFFERS,
        "bootstrap": BOOTSTRAP,
        "seed": SEED,
        "n_results": len(results),
    }
    with open(OUTPUT_DIR / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)


if __name__ == "__main__":
    main()
