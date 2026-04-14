#!/usr/bin/env python3
"""
Compare WBF vs Greedy-Ball Consensus Across All Leaderboard Conditions
======================================================================

For each leaderboard condition that uses multi-pass consensus:

1. Load raw per-pass detection GeoJSON files
2. Run greedy-ball consensus (merge_passes algorithm) at all vote thresholds
3. Run WBF fusion (lib_fusion) at all vote thresholds
4. Score both against ground truth at 20m buffer
5. Report optimal thresholds and F1/P/R comparison

**Zero API cost** — all computation is local geometric processing.

Usage:
    python scripts/compare_wbf_greedy_all_conditions.py
    python scripts/compare_wbf_greedy_all_conditions.py --bounds h10_test
    python scripts/compare_wbf_greedy_all_conditions.py --output results/wbf-comparison

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

# Ensure project root is on the path for script imports
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

from lib_advanced_metrics import calculate_f1_internal  # noqa: E402
from lib_fusion import Box, fuse_detections  # noqa: E402
from merge_passes import (  # noqa: E402
    cluster_across_passes,
    deduplicate_within_pass,
    load_pass_detections,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Constants
# ============================================================================

GT_PATH = _PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
FULL_BOUNDS_PATH = (
    _PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
)
H10_TEST_BOUNDS_PATH = (
    _PROJECT_ROOT / "inputs/vectors/bounds/384/h10_test_bounds.geojson"
)

DEFAULT_BUFFER_M = 20
DEFAULT_OUTPUT_DIR = _PROJECT_ROOT / "results" / "wbf-greedy-comparison"


# ============================================================================
# Condition definitions
# ============================================================================


@dataclass
class Condition:
    """A leaderboard consensus condition to evaluate."""

    name: str
    short_name: str
    data_dir: str  # Relative to project root
    n_passes: int  # How many passes to use (may be less than total available)
    track: str  # "text" or "image"
    model: str  # "flash" or "pro"
    thinking: str  # "high" or "minimal"
    leaderboard_f1: float  # Published greedy-ball F1 at 20m for reference
    leaderboard_threshold: int  # Published optimal vote threshold


# All consensus conditions from the annotated 20m leaderboard.
# PV conditions are included at their consensus stage (pre-verifier).
# Data paths are relative to project root.
CONDITIONS = [
    # --- Flash HIGH text (30-run bank) ---
    Condition(
        name="FH text 16/30 (consensus stage of PV)",
        short_name="FH-text-16of30",
        data_dir="outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
        n_passes=30,
        track="text",
        model="flash",
        thinking="high",
        leaderboard_f1=0.890,  # PV result; consensus-only will differ
        leaderboard_threshold=16,
    ),
    Condition(
        name="FH text 26/30 (consensus only)",
        short_name="FH-text-26of30",
        data_dir="outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
        n_passes=30,
        track="text",
        model="flash",
        thinking="high",
        leaderboard_f1=0.814,
        leaderboard_threshold=26,
    ),
    # --- Flash HIGH text (10-run subset) ---
    Condition(
        name="FH text 9/10 (consensus stage of PV)",
        short_name="FH-text-9of10",
        data_dir="outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
        n_passes=10,
        track="text",
        model="flash",
        thinking="high",
        leaderboard_f1=0.856,  # PV result
        leaderboard_threshold=9,
    ),
    Condition(
        name="FH text 9/10 (consensus only)",
        short_name="FH-text-9of10-cons",
        data_dir="outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
        n_passes=10,
        track="text",
        model="flash",
        thinking="high",
        leaderboard_f1=0.797,
        leaderboard_threshold=9,
    ),
    # --- Flash HIGH text (5-run subset) ---
    Condition(
        name="FH text 4/5 (consensus stage of PV)",
        short_name="FH-text-4of5",
        data_dir="outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
        n_passes=5,
        track="text",
        model="flash",
        thinking="high",
        leaderboard_f1=0.864,  # PV result
        leaderboard_threshold=4,
    ),
    Condition(
        name="FH text 5/5 (consensus only)",
        short_name="FH-text-5of5-cons",
        data_dir="outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
        n_passes=5,
        track="text",
        model="flash",
        thinking="high",
        leaderboard_f1=0.779,
        leaderboard_threshold=5,
    ),
    # --- Flash HIGH image ---
    Condition(
        name="FH image 3/5 (consensus stage of PV)",
        short_name="FH-image-3of5",
        data_dir="outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
        n_passes=5,
        track="image",
        model="flash",
        thinking="high",
        leaderboard_f1=0.778,  # PV result
        leaderboard_threshold=3,
    ),
    Condition(
        name="FH image 3/5 (consensus only)",
        short_name="FH-image-3of5-cons",
        data_dir="outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
        n_passes=5,
        track="image",
        model="flash",
        thinking="high",
        leaderboard_f1=0.727,
        leaderboard_threshold=3,
    ),
    Condition(
        name="FH image 7/10 (consensus only)",
        short_name="FH-image-7of10-cons",
        data_dir="outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
        n_passes=10,
        track="image",
        model="flash",
        thinking="high",
        leaderboard_f1=0.750,
        leaderboard_threshold=7,
    ),
    # --- Pro HIGH text ---
    Condition(
        name="Pro H text 3/5 (consensus stage of PV)",
        short_name="Pro-text-3of5",
        data_dir="outputs/h11/pv-diag-384/pro-high-text-n5/text-t0.7",
        n_passes=5,
        track="text",
        model="pro",
        thinking="high",
        leaderboard_f1=0.849,  # PV result
        leaderboard_threshold=3,
    ),
    Condition(
        name="Pro H text 3/5 (consensus only)",
        short_name="Pro-text-3of5-cons",
        data_dir="outputs/h11/pv-diag-384/pro-high-text-n5/text-t0.7",
        n_passes=5,
        track="text",
        model="pro",
        thinking="high",
        leaderboard_f1=0.840,
        leaderboard_threshold=3,
    ),
    Condition(
        name="Pro H text 6/10 (consensus only)",
        short_name="Pro-text-6of10-cons",
        data_dir="outputs/h11/pv-diag-384/pro-high-text-n5/text-t0.7",
        n_passes=10,
        track="text",
        model="pro",
        thinking="high",
        leaderboard_f1=0.837,
        leaderboard_threshold=6,
    ),
    # --- Pro HIGH image ---
    Condition(
        name="Pro H image 3/5 (consensus only)",
        short_name="Pro-image-3of5-cons",
        data_dir="outputs/h11/pv-diag-384/pro-high-image-n5/image-t0.7",
        n_passes=5,
        track="image",
        model="pro",
        thinking="high",
        leaderboard_f1=0.700,
        leaderboard_threshold=3,
    ),
    # --- Flash MINIMAL text (30-run bank) ---
    Condition(
        name="FM text T=0.7 29/30 (consensus only)",
        short_name="FM-text-29of30",
        data_dir="outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
        n_passes=30,
        track="text",
        model="flash",
        thinking="minimal",
        leaderboard_f1=0.661,
        leaderboard_threshold=29,
    ),
    Condition(
        name="FM text T=0.7 5/5 (consensus only)",
        short_name="FM-text-5of5",
        data_dir="outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
        n_passes=5,
        track="text",
        model="flash",
        thinking="minimal",
        leaderboard_f1=0.640,
        leaderboard_threshold=5,
    ),
    Condition(
        name="FM text T=0.7 10/10 (consensus only)",
        short_name="FM-text-10of10",
        data_dir="outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
        n_passes=10,
        track="text",
        model="flash",
        thinking="minimal",
        leaderboard_f1=0.633,
        leaderboard_threshold=10,
    ),
    # --- Flash MINIMAL image (30-run bank, from phase3a) ---
    Condition(
        name="FM image 4/5 (consensus only)",
        short_name="FM-image-4of5",
        data_dir="outputs/phase3a/track1-image/T0.7",
        n_passes=5,
        track="image",
        model="flash",
        thinking="minimal",
        leaderboard_f1=0.664,
        leaderboard_threshold=4,
    ),
    Condition(
        name="FM image 8/10 (consensus only)",
        short_name="FM-image-8of10",
        data_dir="outputs/phase3a/track1-image/T0.7",
        n_passes=10,
        track="image",
        model="flash",
        thinking="minimal",
        leaderboard_f1=0.680,
        leaderboard_threshold=8,
    ),
]


# ============================================================================
# Box loading (generic, not tied to H10 configs)
# ============================================================================


def features_to_boxes(
    features: list[dict], pass_id: str
) -> list[Box]:
    """Convert GeoJSON features (Polygon bboxes in EPSG:32635) to Box objects.

    Extracts the bounding box from each polygon geometry. Skips features
    that are not parseable as polygons.

    Args:
        features: GeoJSON feature dicts with Polygon geometry.
        pass_id: Pass identifier (e.g. 'run_1').

    Returns:
        List of Box objects.
    """
    boxes = []
    for feat in features:
        geom = feat.get("geometry") or {}
        if geom.get("type") != "Polygon":
            continue
        rings = geom.get("coordinates") or []
        if not rings:
            continue
        ring = rings[0]
        if len(ring) < 4:
            continue

        xs = [pt[0] for pt in ring]
        ys = [pt[1] for pt in ring]
        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)
        if x1 == x2 or y1 == y2:
            continue

        props = feat.get("properties") or {}
        boxes.append(
            Box(
                x1=float(x1),
                y1=float(y1),
                x2=float(x2),
                y2=float(y2),
                confidence=1.0,
                pass_id=pass_id,
                source_tile=str(props.get("source_tile") or ""),
                subtype=str(props.get("subtype") or "burial_mound"),
            )
        )
    return boxes


def load_all_boxes(
    data_dir: Path, n_passes: int
) -> tuple[list[Box], dict[str, int]]:
    """Load raw per-pass bounding boxes from run directories.

    Args:
        data_dir: Directory containing run_1/, run_2/, ... subdirectories.
        n_passes: Number of passes to load (uses runs 1..n_passes).

    Returns:
        Tuple of (all_boxes, per_pass_counts).
    """
    pass_filter = list(range(1, n_passes + 1))
    all_boxes: list[Box] = []
    per_pass_counts: dict[str, int] = {}

    run_dirs = sorted(data_dir.glob("run_*"))
    for run_dir in run_dirs:
        try:
            run_num = int(run_dir.name.split("_")[1])
        except (ValueError, IndexError):
            continue
        if run_num not in pass_filter:
            continue

        pass_id = run_dir.name
        geojsons = sorted(run_dir.glob("detections*.geojson"))
        if not geojsons:
            per_pass_counts[pass_id] = 0
            continue

        feats = json.loads(geojsons[0].read_text()).get("features", [])
        boxes = features_to_boxes(feats, pass_id=pass_id)
        all_boxes.extend(boxes)
        per_pass_counts[pass_id] = len(boxes)

    return all_boxes, per_pass_counts


# ============================================================================
# Scoring helpers
# ============================================================================


def clusters_to_gdf(
    centroids: list[tuple[float, float]],
    source_tiles: list[str],
) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame of detection points from centroids.

    Args:
        centroids: List of (easting, northing) in EPSG:32635.
        source_tiles: List of source tile names (one per centroid).

    Returns:
        GeoDataFrame with Point geometry and source_tile column.
    """
    geoms = [Point(x, y) for x, y in centroids]
    return gpd.GeoDataFrame(
        {"source_tile": source_tiles},
        geometry=geoms,
        crs="EPSG:32635",
    )


def score_greedy_at_threshold(
    clusters: list[dict],
    threshold: int,
    gt: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
    buffer_m: int = DEFAULT_BUFFER_M,
) -> dict:
    """Score greedy-ball consensus at a specific vote threshold.

    Args:
        clusters: Output of cluster_across_passes().
        threshold: Minimum vote count to retain.
        gt: Ground truth GeoDataFrame.
        bounds: Bounds GeoDataFrame.
        buffer_m: Matching buffer in metres.

    Returns:
        Dict with threshold, n, precision, recall, f1.
    """
    filtered = [c for c in clusters if c["vote_count"] >= threshold]
    if not filtered:
        return {"threshold": threshold, "n": 0, "p": 0.0, "r": 0.0, "f1": 0.0}

    centroids = [c["centroid"] for c in filtered]
    tiles = [c["source_tiles"][0] if c["source_tiles"] else "unknown" for c in filtered]
    det_gdf = clusters_to_gdf(centroids, tiles)

    p, r, f1 = calculate_f1_internal(det_gdf, gt, bounds, buffer_metres=buffer_m)
    return {"threshold": threshold, "n": len(filtered), "p": p, "r": r, "f1": f1}


def score_wbf_at_threshold(
    clusters: list,
    threshold: int,
    gt: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
    buffer_m: int = DEFAULT_BUFFER_M,
) -> dict:
    """Score WBF fusion results at a specific vote threshold.

    Args:
        clusters: List of FusedCluster objects from fuse_detections().
        threshold: Minimum vote count to retain.
        gt: Ground truth GeoDataFrame.
        bounds: Bounds GeoDataFrame.
        buffer_m: Matching buffer in metres.

    Returns:
        Dict with threshold, n, precision, recall, f1.
    """
    filtered = [c for c in clusters if c.vote_count >= threshold]
    if not filtered:
        return {"threshold": threshold, "n": 0, "p": 0.0, "r": 0.0, "f1": 0.0}

    centroids = [c.centroid for c in filtered]
    tiles = [
        c.source_tiles[0] if c.source_tiles else "unknown" for c in filtered
    ]
    det_gdf = clusters_to_gdf(centroids, tiles)

    p, r, f1 = calculate_f1_internal(det_gdf, gt, bounds, buffer_metres=buffer_m)
    return {"threshold": threshold, "n": len(filtered), "p": p, "r": r, "f1": f1}


# ============================================================================
# Per-condition comparison
# ============================================================================


def compare_condition(
    condition: Condition,
    gt: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
    buffer_m: int = DEFAULT_BUFFER_M,
) -> dict:
    """Run greedy-ball and WBF consensus and compare F1 for one condition.

    Args:
        condition: Condition definition.
        gt: Ground truth GeoDataFrame.
        bounds: Bounds GeoDataFrame.
        buffer_m: Matching buffer in metres.

    Returns:
        Comparison results dict.
    """
    data_dir = _PROJECT_ROOT / condition.data_dir
    if not data_dir.exists():
        logger.warning("Data dir not found: %s — skipping %s", data_dir, condition.name)
        return {"condition": condition.name, "error": f"Data dir not found: {data_dir}"}

    logger.info("=" * 70)
    logger.info("Condition: %s", condition.name)
    logger.info("Data dir: %s", data_dir)
    logger.info("Passes: %d", condition.n_passes)

    t_start = time.time()
    pass_filter = list(range(1, condition.n_passes + 1))

    # ── Greedy-ball consensus ──
    logger.info("Running greedy-ball consensus...")
    raw_passes = load_pass_detections(data_dir, pass_filter=pass_filter)
    if not raw_passes:
        return {"condition": condition.name, "error": "No passes loaded"}

    actual_passes = len(raw_passes)
    total_raw = sum(len(feats) for feats in raw_passes.values())
    logger.info("  Loaded %d passes, %d raw detections", actual_passes, total_raw)

    # Within-pass dedup
    deduped_passes: dict[str, list[dict]] = {}
    for pass_id, features in raw_passes.items():
        deduped_passes[pass_id] = deduplicate_within_pass(features)

    # Cross-pass clustering
    greedy_clusters = cluster_across_passes(deduped_passes)
    logger.info("  Greedy clusters: %d", len(greedy_clusters))

    # ── WBF consensus ──
    logger.info("Running WBF consensus...")
    all_boxes, per_pass_counts = load_all_boxes(data_dir, condition.n_passes)
    logger.info("  Loaded %d raw boxes across %d passes",
                len(all_boxes), len(per_pass_counts))

    wbf_clusters, wbf_diag = fuse_detections(
        all_boxes,
        iou_threshold=0.25,
        min_separation_m=60.0,
        anchor_vote_threshold=None,
    )
    logger.info("  WBF clusters: %d (rejected by size: %d, merged by min-sep: %d)",
                len(wbf_clusters),
                wbf_diag["n_rejected_by_size_filter"],
                wbf_diag["n_merged_by_min_separation"])

    # ── Threshold sweep ──
    max_t = actual_passes
    thresholds = list(range(1, max_t + 1))

    greedy_sweep = []
    wbf_sweep = []
    for t in thresholds:
        greedy_sweep.append(
            score_greedy_at_threshold(greedy_clusters, t, gt, bounds, buffer_m)
        )
        wbf_sweep.append(
            score_wbf_at_threshold(wbf_clusters, t, gt, bounds, buffer_m)
        )

    # Find optima
    greedy_best = max(greedy_sweep, key=lambda r: r["f1"])
    wbf_best = max(wbf_sweep, key=lambda r: r["f1"])

    elapsed = time.time() - t_start
    logger.info("  Greedy best: T=%d, F1=%.4f (P=%.4f, R=%.4f, n=%d)",
                greedy_best["threshold"], greedy_best["f1"],
                greedy_best["p"], greedy_best["r"], greedy_best["n"])
    logger.info("  WBF best:    T=%d, F1=%.4f (P=%.4f, R=%.4f, n=%d)",
                wbf_best["threshold"], wbf_best["f1"],
                wbf_best["p"], wbf_best["r"], wbf_best["n"])
    logger.info("  Delta F1 (WBF - greedy): %+.4f",
                wbf_best["f1"] - greedy_best["f1"])
    logger.info("  Elapsed: %.1f s", elapsed)

    # ── Matched-threshold comparison ──
    # Compare at the leaderboard's published threshold for a fair apple-to-apple
    leaderboard_t = condition.leaderboard_threshold
    greedy_at_pub = score_greedy_at_threshold(
        greedy_clusters, leaderboard_t, gt, bounds, buffer_m
    )
    wbf_at_pub = score_wbf_at_threshold(
        wbf_clusters, leaderboard_t, gt, bounds, buffer_m
    )

    return {
        "condition": condition.name,
        "short_name": condition.short_name,
        "track": condition.track,
        "model": condition.model,
        "thinking": condition.thinking,
        "n_passes": actual_passes,
        "n_raw_detections": total_raw,
        "n_raw_boxes": len(all_boxes),
        "n_greedy_clusters": len(greedy_clusters),
        "n_wbf_clusters": len(wbf_clusters),
        "wbf_diagnostics": wbf_diag,
        "greedy_sweep": greedy_sweep,
        "wbf_sweep": wbf_sweep,
        "greedy_optimal": greedy_best,
        "wbf_optimal": wbf_best,
        "delta_f1_optimal": round(wbf_best["f1"] - greedy_best["f1"], 6),
        "at_published_threshold": {
            "threshold": leaderboard_t,
            "greedy": greedy_at_pub,
            "wbf": wbf_at_pub,
            "delta_f1": round(
                wbf_at_pub["f1"] - greedy_at_pub["f1"], 6
            ),
        },
        "leaderboard_f1_reference": condition.leaderboard_f1,
        "elapsed_s": round(elapsed, 1),
    }


# ============================================================================
# Main
# ============================================================================


def print_summary_table(results: list[dict]) -> None:
    """Print a concise comparison table to stdout."""
    print()
    print("=" * 100)
    print("WBF vs GREEDY-BALL COMPARISON — CONSENSUS-ONLY F1 AT 20m BUFFER")
    print("=" * 100)
    print()
    header = (
        f"{'Condition':<35} {'N':>3} "
        f"{'Greedy T':>8} {'Greedy F1':>9} "
        f"{'WBF T':>6} {'WBF F1':>7} "
        f"{'ΔF1':>7} {'Time':>6}"
    )
    print(header)
    print("-" * len(header))

    for r in results:
        if "error" in r:
            print(f"{r['condition']:<35} SKIPPED: {r['error']}")
            continue

        g = r["greedy_optimal"]
        w = r["wbf_optimal"]
        delta = r["delta_f1_optimal"]
        sign = "+" if delta >= 0 else ""
        print(
            f"{r['short_name']:<35} {r['n_passes']:>3} "
            f"{g['threshold']:>8} {g['f1']:>9.4f} "
            f"{w['threshold']:>6} {w['f1']:>7.4f} "
            f"{sign}{delta:>6.4f} {r['elapsed_s']:>5.1f}s"
        )

    print()
    # Summary statistics
    valid = [r for r in results if "error" not in r]
    if valid:
        deltas = [r["delta_f1_optimal"] for r in valid]
        print(f"Conditions evaluated: {len(valid)}")
        print(f"Mean ΔF1 (WBF - greedy): {np.mean(deltas):+.4f}")
        print(f"Median ΔF1: {np.median(deltas):+.4f}")
        print(f"Range: [{min(deltas):+.4f}, {max(deltas):+.4f}]")
        wbf_wins = sum(1 for d in deltas if d > 0.005)
        greedy_wins = sum(1 for d in deltas if d < -0.005)
        ties = len(deltas) - wbf_wins - greedy_wins
        print(f"WBF wins (>+0.005): {wbf_wins}, "
              f"Greedy wins (>+0.005): {greedy_wins}, "
              f"Ties (±0.005): {ties}")
    print()


def main() -> None:
    """Run the full WBF vs greedy comparison."""
    parser = argparse.ArgumentParser(
        description="Compare WBF vs greedy-ball consensus across leaderboard conditions"
    )
    parser.add_argument(
        "--bounds",
        choices=["full", "h10_test"],
        default="full",
        help="Bounds file to use: 'full' (487 tiles) or 'h10_test' (327 tiles)",
    )
    parser.add_argument(
        "--buffer",
        type=int,
        default=DEFAULT_BUFFER_M,
        help=f"F1 matching buffer in metres (default: {DEFAULT_BUFFER_M})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--conditions",
        type=str,
        default=None,
        help="Comma-separated short names to run (default: all)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose logging",
    )
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    # Load evaluation data
    bounds_path = FULL_BOUNDS_PATH if args.bounds == "full" else H10_TEST_BOUNDS_PATH
    logger.info("Loading ground truth from %s", GT_PATH)
    gt = gpd.read_file(GT_PATH)
    if gt.crs != "EPSG:32635":
        gt = gt.to_crs("EPSG:32635")

    logger.info("Loading bounds from %s (%s)", bounds_path, args.bounds)
    bounds = gpd.read_file(bounds_path)
    if bounds.crs != "EPSG:32635":
        bounds = bounds.to_crs("EPSG:32635")
    logger.info("  %d tiles in evaluation bounds", len(bounds))

    # Filter conditions if requested
    conditions = CONDITIONS
    if args.conditions:
        requested = {s.strip() for s in args.conditions.split(",")}
        conditions = [c for c in CONDITIONS if c.short_name in requested]
        if not conditions:
            logger.error("No matching conditions found for: %s", args.conditions)
            sys.exit(1)
        logger.info("Running %d of %d conditions", len(conditions), len(CONDITIONS))

    # Run comparisons
    results = []
    total_start = time.time()
    for i, cond in enumerate(conditions, 1):
        logger.info("[%d/%d] Processing %s...", i, len(conditions), cond.short_name)
        result = compare_condition(cond, gt, bounds, args.buffer)
        results.append(result)

    total_elapsed = time.time() - total_start
    logger.info("Total elapsed: %.1f s", total_elapsed)

    # Print summary table
    print_summary_table(results)

    # Save full results
    args.output.mkdir(parents=True, exist_ok=True)
    bounds_tag = args.bounds
    output_file = args.output / f"wbf_vs_greedy_{bounds_tag}_{args.buffer}m.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "bounds": args.bounds,
                "bounds_file": str(bounds_path),
                "buffer_m": args.buffer,
                "n_conditions": len(results),
                "total_elapsed_s": round(total_elapsed, 1),
                "conditions": results,
            },
            f,
            indent=2,
        )
    logger.info("Full results saved to %s", output_file)

    # Also save a markdown summary table
    md_file = args.output / f"wbf_vs_greedy_{bounds_tag}_{args.buffer}m.md"
    with open(md_file, "w") as f:
        f.write("# WBF vs Greedy-Ball Consensus Comparison\n\n")
        f.write(f"**Bounds**: {args.bounds} ({len(bounds)} tiles)\n")
        f.write(f"**Buffer**: {args.buffer}m\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("## Optimal-threshold comparison\n\n")
        f.write("| Condition | N | Greedy T | Greedy F1 | WBF T | WBF F1 | ΔF1 |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for r in results:
            if "error" in r:
                f.write(f"| {r['condition']} | — | — | — | — | — | SKIP |\n")
                continue
            g = r["greedy_optimal"]
            w = r["wbf_optimal"]
            delta = r["delta_f1_optimal"]
            f.write(
                f"| {r['short_name']} | {r['n_passes']} "
                f"| {g['threshold']} | {g['f1']:.4f} "
                f"| {w['threshold']} | {w['f1']:.4f} "
                f"| {delta:+.4f} |\n"
            )
        f.write("\n")

        # Published-threshold comparison
        f.write("## Matched-threshold comparison (at leaderboard threshold)\n\n")
        f.write("| Condition | T | Greedy F1 | WBF F1 | ΔF1 |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        for r in results:
            if "error" in r:
                continue
            pub = r["at_published_threshold"]
            f.write(
                f"| {r['short_name']} | {pub['threshold']} "
                f"| {pub['greedy']['f1']:.4f} "
                f"| {pub['wbf']['f1']:.4f} "
                f"| {pub['delta_f1']:+.4f} |\n"
            )

    logger.info("Markdown summary saved to %s", md_file)


if __name__ == "__main__":
    main()
