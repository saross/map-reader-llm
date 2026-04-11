#!/usr/bin/env python3
"""Hard-case discovery from K detection passes.

Runs per-map Hungarian matching for each detection pass against ground
truth, then classifies each spatial location by difficulty:

- **consistent_tp**: GT mound detected in all K passes (easy positive)
- **borderline_tp**: GT mound detected in some passes (hard positive)
- **consistent_fn**: GT mound never detected (hardest positive)
- **consistent_fp**: False alarm appearing in ≥3 passes (hard negative)
- **sporadic_fp**: False alarm appearing in 1-2 passes (soft negative)

Outputs a scored register of all locations for downstream example pool
building.

Usage:
    # Analyse existing detection outputs:
    python scripts/discover_hard_cases.py \\
        --detections-dir outputs/h10/calibration-runs/pool_160/ \\
        --bounds inputs/calibration/h10-384/calibration_bounds_160.geojson \\
        --reference inputs/vectors/references/mounds-reference.geojson \\
        --k-passes 5 --buffer 20 \\
        --output-dir outputs/h10/hard-cases/pool_160/

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from lib_advanced_metrics import (  # noqa: E402
    get_map_name,
    match_detections_to_references,
    scope_references_to_tiles,
)
from lib_calibration import (  # noqa: E402
    score_difficulty_hn,
    score_difficulty_hp,
)
from lib_consensus import (  # noqa: E402
    cluster_across_passes,
    deduplicate_within_pass,
    ensure_utm_crs,
    load_run_detections,
)

logger = logging.getLogger(__name__)

# =========================================================================
# Constants
# =========================================================================

# Classification: FP is "consistent" if it appears in ≥60% of passes
# (minimum 2 passes). With K=5 this gives ≥3; with K=2 it gives ≥2.
_FP_CONSISTENT_FRACTION = 0.6
_FP_CONSISTENT_FLOOR = 2


# =========================================================================
# Core analysis
# =========================================================================


def analyse_detections(
    detection_dirs: list[Path],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int = 20,
) -> dict:
    """Analyse K detection passes against ground truth.

    For each GT mound in scope, records which passes detected it and
    at what distance. For false-positive detections, clusters across
    passes to find persistent false alarms.

    Args:
        detection_dirs: List of run directories, each containing
            ``detections_*.geojson`` files (one directory per pass).
        gdf_ref: GeoDataFrame of ground-truth reference mounds.
        gdf_bounds: GeoDataFrame of evaluation tile boundaries.
        buffer_metres: Maximum matching distance in metres.

    Returns:
        Dict with keys:
            - ``mound_register``: List of per-GT-mound dicts with vote
              counts, match distances, classification, and score.
            - ``fp_register``: List of per-FP-cluster dicts with vote
              counts, nearest GT distance, classification, and score.
            - ``k_passes``: Number of passes analysed.
            - ``summary``: Aggregate counts per classification.
    """
    k_passes = len(detection_dirs)
    if k_passes == 0:
        raise ValueError("No detection directories provided")

    # Detect reference map column
    ref_map_col = _detect_ref_map_col(gdf_ref)

    # Get maps from bounds
    processed_maps = {
        get_map_name(n) for n in gdf_bounds["tile_name"].unique()
    }
    processed_maps.discard("Unknown")

    # Scope references to evaluation tiles
    scoped_refs = {}
    for map_name in sorted(processed_maps):
        map_bounds = gdf_bounds[
            gdf_bounds["tile_name"].str.startswith(map_name)
        ]
        ref_scope = gdf_ref[gdf_ref[ref_map_col] == map_name]
        if not ref_scope.empty:
            ref_scope = scope_references_to_tiles(ref_scope, map_bounds)
        scoped_refs[map_name] = ref_scope

    total_refs = sum(len(r) for r in scoped_refs.values())
    logger.info(
        "Scoped %d reference mounds across %d maps",
        total_refs, len(scoped_refs),
    )

    # ---------------------------------------------------------------
    # Per-pass matching: track which passes detect each GT mound
    # ---------------------------------------------------------------
    # mound_votes[map_name][ref_local_idx] = list of (pass_idx, distance)
    mound_votes: dict[str, dict[int, list[tuple[int, float]]]] = {
        m: {i: [] for i in range(len(refs))}
        for m, refs in scoped_refs.items()
        if not refs.empty
    }

    # Collect all unmatched detections for FP clustering
    all_unmatched_features: dict[str, list[dict]] = {}

    for pass_idx, run_dir in enumerate(detection_dirs):
        pass_id = run_dir.name
        features = load_run_detections(run_dir)
        if not features:
            logger.warning("No features in %s", run_dir)
            continue

        # Deduplicate within pass (consistent with consensus pipeline)
        deduped = deduplicate_within_pass(features)

        # Convert to GeoDataFrame for per-map matching
        gdf_det = _deduped_to_gdf(deduped, gdf_bounds.crs)

        for map_name, ref_scope in scoped_refs.items():
            if ref_scope.empty:
                continue

            det_scope = gdf_det[
                gdf_det["source_tile"].str.startswith(map_name)
            ]

            if det_scope.empty:
                # All refs in this map are FNs for this pass
                continue

            det_geoms = list(det_scope.geometry)
            ref_geoms = list(ref_scope.geometry)

            matched_det, matched_ref, unmatched_det, _ = (
                match_detections_to_references(
                    det_geoms, ref_geoms, buffer_metres,
                )
            )

            # Record matches for this pass
            for d_idx, r_idx in zip(matched_det, matched_ref):
                det_pt = det_geoms[d_idx].centroid
                ref_pt = ref_geoms[r_idx].centroid
                dist = det_pt.distance(ref_pt)
                if map_name in mound_votes:
                    mound_votes[map_name][r_idx].append(
                        (pass_idx, dist)
                    )

            # Collect unmatched detections as FP candidates
            for d_idx in unmatched_det:
                det_row = det_scope.iloc[d_idx]
                centroid = det_row.geometry.centroid
                fp_feat = {
                    "centroid": (centroid.x, centroid.y),
                    "label": det_row.get("subtype", "unknown"),
                    "source_tile": det_row.get("source_tile", "unknown"),
                    "source_tiles": [
                        det_row.get("source_tile", "unknown")
                    ],
                }
                if pass_id not in all_unmatched_features:
                    all_unmatched_features[pass_id] = []
                all_unmatched_features[pass_id].append(fp_feat)

        logger.info(
            "Pass %d/%d (%s): %d features processed",
            pass_idx + 1, k_passes, pass_id, len(features),
        )

    # ---------------------------------------------------------------
    # Build mound register
    # ---------------------------------------------------------------
    mound_register = _build_mound_register(
        mound_votes, scoped_refs, k_passes, buffer_metres,
    )

    # ---------------------------------------------------------------
    # Cluster FPs across passes and build FP register
    # ---------------------------------------------------------------
    fp_register = _build_fp_register(
        all_unmatched_features, scoped_refs, k_passes,
    )

    # Summary counts
    summary = _build_summary(mound_register, fp_register)

    logger.info(
        "Discovery complete: %d GT mounds (%d consistent_tp, "
        "%d borderline_tp, %d consistent_fn), "
        "%d FP clusters (%d consistent, %d sporadic)",
        len(mound_register),
        summary["consistent_tp"],
        summary["borderline_tp"],
        summary["consistent_fn"],
        len(fp_register),
        summary["consistent_fp"],
        summary["sporadic_fp"],
    )

    return {
        "mound_register": mound_register,
        "fp_register": fp_register,
        "k_passes": k_passes,
        "summary": summary,
    }


# =========================================================================
# Internal helpers
# =========================================================================


def _detect_ref_map_col(gdf_ref: gpd.GeoDataFrame) -> str:
    """Detect the map column name in the reference GeoDataFrame."""
    if "Map" in gdf_ref.columns:
        return "Map"
    if "source_map" in gdf_ref.columns:
        return "source_map"
    raise ValueError(
        f"Reference has no 'Map' or 'source_map' column. "
        f"Columns: {list(gdf_ref.columns)}"
    )


def _deduped_to_gdf(
    deduped: list[dict],
    crs: str | object,
) -> gpd.GeoDataFrame:
    """Convert deduplicated detection dicts to a GeoDataFrame.

    Args:
        deduped: List of dicts from ``deduplicate_within_pass``, each
            with ``centroid`` (x, y) tuple and ``source_tiles`` list.
        crs: Target CRS.

    Returns:
        GeoDataFrame with ``source_tile``, ``subtype``, and Point
        geometry.
    """
    from shapely.geometry import Point

    rows = []
    geoms = []
    for det in deduped:
        cx, cy = det["centroid"]
        source_tiles = det.get("source_tiles", [])
        rows.append({
            "source_tile": source_tiles[0] if source_tiles else "unknown",
            "subtype": det.get("label", "unknown"),
        })
        geoms.append(Point(cx, cy))

    # Validate: detection coordinates should be in projected CRS (UTM).
    # If they look geographic (lon/lat range), warn — matching will fail.
    if geoms and abs(geoms[0].x) <= 180 and abs(geoms[0].y) <= 90:
        logger.warning(
            "Detection coordinates appear geographic (x=%.1f, y=%.1f) "
            "but expected projected (UTM). Matching distances will be "
            "wrong. Check upstream detection GeoJSON CRS.",
            geoms[0].x, geoms[0].y,
        )

    if not rows:
        return gpd.GeoDataFrame(
            columns=["source_tile", "subtype", "geometry"],
            geometry="geometry",
            crs=crs,
        )

    return gpd.GeoDataFrame(rows, geometry=geoms, crs=crs)


def _build_mound_register(
    mound_votes: dict[str, dict[int, list[tuple[int, float]]]],
    scoped_refs: dict[str, gpd.GeoDataFrame],
    k_passes: int,
    buffer_metres: int,
) -> list[dict]:
    """Build the per-GT-mound register with classifications and scores.

    Args:
        mound_votes: Per-map, per-ref-index list of (pass_idx, distance)
            matches.
        scoped_refs: Per-map scoped reference GeoDataFrames.
        k_passes: Total number of passes.
        buffer_metres: Matching buffer in metres.

    Returns:
        List of mound register dicts.
    """
    register = []

    for map_name, ref_votes in mound_votes.items():
        ref_gdf = scoped_refs[map_name]
        for local_idx, votes in ref_votes.items():
            ref_row = ref_gdf.iloc[local_idx]
            ref_pt = ref_row.geometry.centroid
            vote_count = len(votes)

            # Mean match distance (for scored matches only)
            if votes:
                distances = [d for _, d in votes]
                mean_distance = float(np.mean(distances))
                min_distance = float(np.min(distances))
            else:
                mean_distance = None
                min_distance = None

            # Classify
            if vote_count == k_passes:
                classification = "consistent_tp"
            elif vote_count == 0:
                classification = "consistent_fn"
            else:
                classification = "borderline_tp"

            # Score difficulty
            score = score_difficulty_hp(
                vote_count, k_passes,
                match_distance=mean_distance,
                buffer_metres=float(buffer_metres),
            )

            register.append({
                "map_name": map_name,
                "ref_index": int(ref_gdf.index[local_idx]),
                "x": float(ref_pt.x),
                "y": float(ref_pt.y),
                "vote_count": vote_count,
                "k_passes": k_passes,
                "mean_match_distance": (
                    round(mean_distance, 2) if mean_distance is not None
                    else None
                ),
                "min_match_distance": (
                    round(min_distance, 2) if min_distance is not None
                    else None
                ),
                "classification": classification,
                "difficulty_score": round(score, 4),
            })

    return register


def _build_fp_register(
    all_unmatched_features: dict[str, list[dict]],
    scoped_refs: dict[str, gpd.GeoDataFrame],
    k_passes: int,
) -> list[dict]:
    """Cluster FP detections across passes and score.

    Args:
        all_unmatched_features: Per-pass lists of unmatched detection
            dicts (in the format expected by ``cluster_across_passes``).
        scoped_refs: Per-map scoped reference GeoDataFrames.
        k_passes: Total number of passes.

    Returns:
        List of FP register dicts.
    """
    if not all_unmatched_features:
        return []

    # Cluster across passes using existing consensus infrastructure
    fp_clusters = cluster_across_passes(all_unmatched_features)

    # Build a combined reference for nearest-GT distance calculation
    all_refs = []
    for ref_gdf in scoped_refs.values():
        if not ref_gdf.empty:
            all_refs.append(ref_gdf)

    combined_refs = (
        gpd.GeoDataFrame(pd.concat(all_refs, ignore_index=True))
        if all_refs
        else gpd.GeoDataFrame()
    )

    register = []
    for cluster in fp_clusters:
        cx, cy = cluster["centroid"]
        vote_count = cluster["vote_count"]
        source_tiles = cluster.get("source_tiles", [])

        # Compute distance to nearest GT mound
        nearest_ref_dist = None
        if not combined_refs.empty:
            from shapely.geometry import Point
            fp_point = Point(cx, cy)
            distances = combined_refs.geometry.apply(
                lambda g: fp_point.distance(g.centroid)
            )
            nearest_ref_dist = float(distances.min())

        # Classify — threshold is relative to k_passes
        fp_threshold = max(
            _FP_CONSISTENT_FLOOR,
            int(k_passes * _FP_CONSISTENT_FRACTION + 0.5),
        )
        if vote_count >= fp_threshold:
            classification = "consistent_fp"
        else:
            classification = "sporadic_fp"

        # Derive map name from source tile
        map_name = "Unknown"
        if source_tiles:
            map_name = get_map_name(source_tiles[0])

        score = score_difficulty_hn(
            vote_count, k_passes,
            nearest_ref_distance=nearest_ref_dist,
        )

        register.append({
            "map_name": map_name,
            "x": float(cx),
            "y": float(cy),
            "vote_count": vote_count,
            "k_passes": k_passes,
            "nearest_ref_distance": (
                round(nearest_ref_dist, 2)
                if nearest_ref_dist is not None else None
            ),
            "source_tiles": source_tiles,
            "subtype": cluster.get("label", "unknown"),
            "classification": classification,
            "difficulty_score": round(score, 4),
        })

    return register


def _build_summary(
    mound_register: list[dict],
    fp_register: list[dict],
) -> dict:
    """Build aggregate counts per classification."""
    mound_classes = [m["classification"] for m in mound_register]
    fp_classes = [f["classification"] for f in fp_register]

    return {
        "total_gt_mounds": len(mound_register),
        "consistent_tp": mound_classes.count("consistent_tp"),
        "borderline_tp": mound_classes.count("borderline_tp"),
        "consistent_fn": mound_classes.count("consistent_fn"),
        "total_fp_clusters": len(fp_register),
        "consistent_fp": fp_classes.count("consistent_fp"),
        "sporadic_fp": fp_classes.count("sporadic_fp"),
        "hp_candidates": (
            mound_classes.count("borderline_tp")
            + mound_classes.count("consistent_fn")
        ),
        "hn_candidates": fp_classes.count("consistent_fp"),
    }


# =========================================================================
# Output writing
# =========================================================================


def write_outputs(
    result: dict,
    output_dir: Path,
) -> None:
    """Write discovery outputs to disk.

    Args:
        result: Dict from ``analyse_detections``.
        output_dir: Target directory (created if needed).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full register
    register_path = output_dir / "hard_cases_register.json"
    register_path.write_text(
        json.dumps({
            "mound_register": result["mound_register"],
            "fp_register": result["fp_register"],
            "k_passes": result["k_passes"],
            "summary": result["summary"],
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote %s", register_path)

    # Ranked HP candidates (borderline_tp + consistent_fn, sorted by
    # difficulty descending)
    hp_candidates = [
        m for m in result["mound_register"]
        if m["classification"] in ("borderline_tp", "consistent_fn")
    ]
    hp_candidates.sort(key=lambda m: m["difficulty_score"], reverse=True)
    hp_path = output_dir / "hard_positive_candidates.json"
    hp_path.write_text(
        json.dumps(hp_candidates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote %s (%d candidates)", hp_path, len(hp_candidates))

    # Ranked HN candidates (consistent_fp, sorted by difficulty
    # descending)
    hn_candidates = [
        f for f in result["fp_register"]
        if f["classification"] == "consistent_fp"
    ]
    hn_candidates.sort(key=lambda f: f["difficulty_score"], reverse=True)
    hn_path = output_dir / "hard_negative_candidates.json"
    hn_path.write_text(
        json.dumps(hn_candidates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote %s (%d candidates)", hn_path, len(hn_candidates))

    # Summary
    summary_path = output_dir / "discovery_summary.json"
    summary_path.write_text(
        json.dumps(result["summary"], indent=2) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote %s", summary_path)


# =========================================================================
# CLI
# =========================================================================


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hard-case discovery from K detection passes.",
    )
    parser.add_argument(
        "--detections-dir", type=Path, required=True,
        help="Directory containing run_1/, run_2/, ... subdirectories "
             "with detections_*.geojson files",
    )
    parser.add_argument(
        "--bounds", type=Path, required=True,
        help="Path to calibration bounds GeoJSON",
    )
    parser.add_argument(
        "--reference", type=Path, required=True,
        help="Path to ground-truth reference GeoJSON",
    )
    parser.add_argument(
        "--k-passes", type=int, default=5,
        help="Number of detection passes to analyse (default: 5)",
    )
    parser.add_argument(
        "--buffer", type=int, default=20,
        help="Matching tolerance in metres (default: 20)",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for discovery results",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Discover run directories
    run_dirs = sorted(
        d for d in args.detections_dir.iterdir()
        if d.is_dir() and d.name.startswith("run_")
    )
    if len(run_dirs) < args.k_passes:
        logger.warning(
            "Found %d run directories but --k-passes=%d; "
            "using all %d found",
            len(run_dirs), args.k_passes, len(run_dirs),
        )
    run_dirs = run_dirs[:args.k_passes]

    if not run_dirs:
        parser.error(
            f"No run_* directories found in {args.detections_dir}"
        )

    # Load spatial data
    gdf_ref = gpd.read_file(args.reference)
    gdf_ref = ensure_utm_crs(gdf_ref, source_label=str(args.reference))

    gdf_bounds = gpd.read_file(args.bounds)
    gdf_bounds = ensure_utm_crs(
        gdf_bounds, source_label=str(args.bounds),
    )

    # Run analysis
    result = analyse_detections(
        run_dirs, gdf_ref, gdf_bounds,
        buffer_metres=args.buffer,
    )

    # Write outputs
    write_outputs(result, args.output_dir)

    # Console summary
    s = result["summary"]
    print(f"\nHard-case discovery complete ({result['k_passes']} passes)")
    print(f"  GT mounds: {s['total_gt_mounds']}")
    print(f"    consistent_tp: {s['consistent_tp']}")
    print(f"    borderline_tp: {s['borderline_tp']}")
    print(f"    consistent_fn: {s['consistent_fn']}")
    print(f"  FP clusters: {s['total_fp_clusters']}")
    print(f"    consistent_fp: {s['consistent_fp']}")
    print(f"    sporadic_fp:   {s['sporadic_fp']}")
    print(f"  HP candidates: {s['hp_candidates']}")
    print(f"  HN candidates: {s['hn_candidates']}")
    print(f"  Output: {args.output_dir}")


if __name__ == "__main__":
    main()
