#!/usr/bin/env python3
# ============================================================================
# fuse_detections_wbf.py
# ----------------------------------------------------------------------------
# Run Weighted Boxes Fusion over the raw per-pass VLM detections for one
# H10 pool config. Replaces the greedy-ball output produced by the current
# ``cluster_across_passes`` / 7_analyse_consensus.py pipeline (see Obs 228
# for background).
#
# Inputs
# ------
#   outputs/h10/evaluation/<config>/run_<N>/detections-*.geojson
#   (one geojson per pass, containing axis-aligned polygon detections
#    in EPSG:32635)
#
# Outputs (written under --output-dir, default outputs/h10/wbf/<config>/)
#   wbf_candidates.geojson         — fused boxes as geojson features
#                                    (for QGIS / visual inspection)
#   wbf_candidates.json            — candidate manifest compatible with
#                                    downstream verifier-crop extraction
#                                    (schema matches candidate_manifest.json)
#   wbf_diagnostics.json           — stage counts, parameters, and a
#                                    brief comparison to the existing
#                                    consensus output for the same config
#
# Usage:
#     python scripts/fuse_detections_wbf.py --config pool_160_hp4hn4
#     python scripts/fuse_detections_wbf.py --config pool_160_hp4hn4 \\
#         --iou-threshold 0.25 --min-separation-m 60
# ============================================================================

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.lib_fusion import (
    DEFAULT_IOU_THRESHOLD,
    DEFAULT_MAX_AREA_M2,
    DEFAULT_MAX_DIMENSION_M,
    DEFAULT_MIN_AREA_M2,
    DEFAULT_MIN_DIMENSION_M,
    DEFAULT_MIN_SEPARATION_M,
    Box,
    FusedCluster,
    fuse_detections,
)

H10_ROOT = Path("outputs/h10")
EVAL_ROOT = H10_ROOT / "evaluation"
DEFAULT_OUTPUT_ROOT = H10_ROOT / "wbf"

#: Mapping of special config names to raw per-pass detection directories.
#: Used to support non-H10 configs (e.g. the H11 production run).
SPECIAL_CONFIGS = {
    "e47-propose-brief-n5": {
        "pass_files": [
            "outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_1/detections_propose_brief-text_run01.geojson",
            "outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_2/detections_propose_brief-text_run02.geojson",
            "outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_3/detections_propose_brief-text_run03.geojson",
            "outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_4/detections-propose_brief-text-3-flash-2026-04-09.geojson",
            "outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_5/detections-propose_brief-text-3-flash-2026-04-09.geojson",
        ],
        "default_output_dir": "outputs/h11/wbf/e47-propose-brief-n5",
    },
    # FH text N=5 (Flash HIGH, T=0.7): PV proposer consensus stage.
    # Leaderboard #2: FH text 4/5 + PV (min vf) = F1 0.864.
    "fh-text-n5": {
        "pass_files": [
            f"outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/run_{i}/detections_text-t0.7_run{i:02d}.geojson"
            for i in range(1, 6)
        ],
        "default_output_dir": "outputs/h11/wbf/fh-text-n5",
    },
    # FH text N=30 (Flash HIGH, T=0.7): PV proposer consensus stage.
    # Leaderboard #1: FH text 16/30 + PV (min vf) = F1 0.890.
    "fh-text-n30": {
        "pass_files": [
            f"outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/run_{i}/detections_text-t0.7_run{i:02d}.geojson"
            for i in range(1, 31)
        ],
        "default_output_dir": "outputs/h11/wbf/fh-text-n30",
    },
    # Canonical 4-map production pipeline (detect_brief-text, HIGH, T=0.7, K=5,
    # library 8580ecb2..., matches 55-map generalisation config). Obs 233 /
    # Priority 1 canonical WBF vs greedy comparison.
    "gold-standard-v2-detect": {
        "pass_files": [
            "outputs/h11/gold-standard-v2/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-10.geojson",
            "outputs/h11/gold-standard-v2/proposer/detect_brief-text/run_2/detections-detect_brief-text-3-flash-2026-04-10.geojson",
            "outputs/h11/gold-standard-v2/proposer/detect_brief-text/run_3/detections-detect_brief-text-3-flash-2026-04-10.geojson",
            "outputs/h11/gold-standard-v2/proposer/detect_brief-text/run_4/detections-detect_brief-text-3-flash-2026-04-10.geojson",
            "outputs/h11/gold-standard-v2/proposer/detect_brief-text/run_5/detections-detect_brief-text-3-flash-2026-04-10.geojson",
        ],
        "default_output_dir": "outputs/h11/wbf/gold-standard-v2-detect",
    },
    # H8 v2 library-composition re-run (7 conditions, 384 px tiles, production
    # carry-forward: T=0.7, thinking=high, detect_brief-text-image.md, K=5).
    # Raw detections live at outputs/h8-v2/<cond>/run_{1..5}/
    # detections-detect_h8_<cond>_v2-3-flash-2026-04-15.geojson. See study
    # YAML (studies/h8-v2-library.yaml) and protocol-errata E51.
    **{
        f"h8v2-{cond}": {
            "pass_files": [
                f"outputs/h8-v2/{cond}/run_{i}/detections-detect_h8_{cond}_v2-3-flash-2026-04-15.geojson"
                for i in range(1, 6)
            ],
            "default_output_dir": f"outputs/h8-v2/wbf/{cond}",
        }
        for cond in (
            "pure-positive-canon",
            "canonical",
            "plus-hp",
            "scale-4",
            "scale-8",
            "scale-16",
            "scale-32",
        )
    },
    # H12 v2 HP:HN ratio experiment (3 conditions; R2 reuses the H10 v2
    # pool_160_hp4hn4 run per errata E52). Raw detections for the two new
    # conditions live at outputs/h12-v2/{r1-hn-heavy,r3-hp-heavy}/run_{1..5}/.
    # See studies/h12-v2-ratio.yaml and protocol-errata E52.
    "h12v2-r1-hn-heavy": {
        "pass_files": [
            f"outputs/h12-v2/r1-hn-heavy/run_{i}/detections-detect_h12_r1-hn-heavy_v2-3-flash-2026-04-15.geojson"
            for i in range(1, 6)
        ],
        "default_output_dir": "outputs/h12-v2/wbf/r1-hn-heavy",
    },
    "h12v2-r2-balanced": {
        "pass_files": [
            f"outputs/h10/evaluation-v2/pool_160_hp4hn4/run_{i}/detections-detect_pool_160_hp4hn4_v2-3-flash-2026-04-15.geojson"
            for i in range(1, 6)
        ],
        "default_output_dir": "outputs/h12-v2/wbf/r2-balanced",
    },
    "h12v2-r3-hp-heavy": {
        "pass_files": [
            f"outputs/h12-v2/r3-hp-heavy/run_{i}/detections-detect_h12_r3-hp-heavy_v2-3-flash-2026-04-15.geojson"
            for i in range(1, 6)
        ],
        "default_output_dir": "outputs/h12-v2/wbf/r3-hp-heavy",
    },
}


# ----------------------------------------------------------------------------
# Loaders
# ----------------------------------------------------------------------------


def polygon_to_box(feature: dict, pass_id: str) -> Box | None:
    """Convert an axis-aligned GeoJSON Polygon feature to a ``Box``.

    Returns ``None`` if the polygon is not axis-aligned (e.g. rotated)
    or if the geometry is malformed. The VLM proposer emits only
    axis-aligned boxes in the current pipeline, so this should be a rare
    defensive path.
    """
    geom = feature.get("geometry") or {}
    if geom.get("type") != "Polygon":
        return None
    rings = geom.get("coordinates") or []
    if not rings:
        return None
    ring = rings[0]
    if len(ring) < 4:
        return None

    xs = [pt[0] for pt in ring]
    ys = [pt[1] for pt in ring]
    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)
    if x1 == x2 or y1 == y2:
        return None

    props = feature.get("properties") or {}
    return Box(
        x1=float(x1),
        y1=float(y1),
        x2=float(x2),
        y2=float(y2),
        confidence=1.0,
        pass_id=pass_id,
        source_tile=str(props.get("source_tile") or ""),
        subtype=str(props.get("subtype") or "burial_mound"),
    )


def load_pass_boxes(config: str) -> tuple[list[Box], dict]:
    """Load all raw per-pass boxes for the given config.

    Supports both H10 configs (under outputs/h10/evaluation/) and the
    SPECIAL_CONFIGS registry for non-H10 configs such as the H11
    production run.

    Returns the flat list of boxes tagged with their pass_id, plus a
    dict of per-pass counts for the diagnostic output.
    """
    if config in SPECIAL_CONFIGS:
        return _load_special_config_boxes(config)

    config_dir = EVAL_ROOT / config
    if not config_dir.exists():
        raise FileNotFoundError(f"Config dir not found: {config_dir}")

    per_pass_counts: dict[str, int] = {}
    all_boxes: list[Box] = []

    run_dirs = sorted(
        [d for d in config_dir.iterdir() if d.is_dir() and d.name.startswith("run_")],
        key=lambda d: int(d.name.split("_")[1]),
    )
    for run_dir in run_dirs:
        pass_id = run_dir.name
        geojsons = sorted(run_dir.glob("detections-*.geojson"))
        if not geojsons:
            per_pass_counts[pass_id] = 0
            continue
        feats = json.loads(geojsons[0].read_text()).get("features", [])
        kept = 0
        for f in feats:
            box = polygon_to_box(f, pass_id=pass_id)
            if box is not None:
                all_boxes.append(box)
                kept += 1
        per_pass_counts[pass_id] = kept

    return all_boxes, {
        "config": config,
        "per_pass_box_counts": per_pass_counts,
        "total_raw_boxes": len(all_boxes),
    }


def _load_special_config_boxes(config: str) -> tuple[list[Box], dict]:
    """Load raw per-pass boxes for a special (non-H10) config."""
    cfg = SPECIAL_CONFIGS[config]
    per_pass_counts: dict[str, int] = {}
    all_boxes: list[Box] = []

    for i, path in enumerate(cfg["pass_files"], start=1):
        pass_id = f"run_{i}"
        p = Path(path)
        if not p.exists():
            per_pass_counts[pass_id] = 0
            continue
        feats = json.loads(p.read_text()).get("features", [])
        kept = 0
        for f in feats:
            box = polygon_to_box(f, pass_id=pass_id)
            if box is not None:
                all_boxes.append(box)
                kept += 1
        per_pass_counts[pass_id] = kept

    return all_boxes, {
        "config": config,
        "per_pass_box_counts": per_pass_counts,
        "total_raw_boxes": len(all_boxes),
    }


# ----------------------------------------------------------------------------
# Writers
# ----------------------------------------------------------------------------


def clusters_to_geojson(
    clusters: list[FusedCluster],
    total_passes: int,
) -> dict:
    """Render the fused clusters as a GeoJSON FeatureCollection.

    Each feature is a polygon ring of the fused bounding box with
    properties matching the format used downstream (vote_count,
    contributing_passes, source_tiles, cluster_size, total_passes).
    """
    features = []
    for i, c in enumerate(clusters):
        b = c.fused_box
        ring = [
            [b.x1, b.y1],
            [b.x2, b.y1],
            [b.x2, b.y2],
            [b.x1, b.y2],
            [b.x1, b.y1],
        ]
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [ring],
            },
            "properties": {
                "candidate_id": i,
                "subtype": b.subtype,
                "confidence": 1.0,
                "vote_count": c.vote_count,
                "total_passes": total_passes,
                "contributing_passes": c.contributing_passes,
                "source_tiles": c.source_tiles,
                "cluster_size": c.cluster_size,
                "centroid_x": c.fused_box.centroid[0],
                "centroid_y": c.fused_box.centroid[1],
            },
        })
    return {
        "type": "FeatureCollection",
        "features": features,
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:EPSG::32635"},
        },
    }


def clusters_to_manifest(
    clusters: list[FusedCluster],
    total_passes: int,
    config: str,
) -> dict:
    """Render the fused clusters in the downstream-compatible manifest format.

    Matches the schema of ``outputs/h10/verifier-crops/*/candidate_manifest.json``
    except that ``crop_file`` is left as an empty string until crop
    extraction is re-run. The downstream verifier crop extraction step
    reads the centroid coordinates and the source tile, both of which
    are populated here.
    """
    manifest_candidates: list[dict[str, Any]] = []
    for i, c in enumerate(clusters):
        cx, cy = c.fused_box.centroid
        primary_tile = c.source_tiles[0] if c.source_tiles else ""
        manifest_candidates.append({
            "candidate_id": i,
            "crop_file": "",
            "source_tile": primary_tile,
            "centroid_x": cx,
            "centroid_y": cy,
            "cropped_from": None,
            "properties": {
                "subtype": c.fused_box.subtype,
                "confidence": 1.0,
                "vote_count": c.vote_count,
                "total_passes": total_passes,
                "contributing_passes": c.contributing_passes,
                "source_tiles": c.source_tiles,
                "cluster_size": c.cluster_size,
                "source_tile": primary_tile,
                "fused_box": {
                    "x1": c.fused_box.x1,
                    "y1": c.fused_box.y1,
                    "x2": c.fused_box.x2,
                    "y2": c.fused_box.y2,
                },
            },
        })

    return {
        "version": "2.0-wbf",
        "source_config": config,
        "source": "weighted_boxes_fusion",
        "rasters_dir": "inputs/rasters",
        "tiles_dir": "inputs/tiles_384",
        "padding": 75,
        "crop_dimensions": "150x150",
        "total_detections": len(manifest_candidates),
        "successful_extractions": 0,
        "failed_extractions": 0,
        "raster_crops": 0,
        "tile_fallback_crops": 0,
        "missing_sources": [],
        "candidates": manifest_candidates,
    }


def compare_to_existing_consensus(
    clusters: list[FusedCluster],
    config: str,
) -> dict:
    """Quick comparison of WBF output against the current consensus output."""
    if config in SPECIAL_CONFIGS:
        # Non-H10 configs: no automatic greedy baseline lookup
        return {"available": False, "note": "special config, use external comparison"}
    consensus_manifest = H10_ROOT / "verifier-crops" / config / "candidate_manifest.json"
    if not consensus_manifest.exists():
        return {"available": False}

    current = json.loads(consensus_manifest.read_text())
    current_n = len(current["candidates"])
    wbf_n = len(clusters)

    current_votes = [
        c["properties"].get("vote_count", 0) for c in current["candidates"]
    ]
    wbf_votes = [c.vote_count for c in clusters]

    def mean(xs: list[int]) -> float:
        return float(sum(xs) / len(xs)) if xs else 0.0

    return {
        "available": True,
        "current_consensus_candidate_count": current_n,
        "wbf_candidate_count": wbf_n,
        "delta": wbf_n - current_n,
        "current_mean_vote_count": mean(current_votes),
        "wbf_mean_vote_count": mean(wbf_votes),
        "current_high_vote_count": int(sum(1 for v in current_votes if v >= 6)),
        "wbf_high_vote_count": int(sum(1 for v in wbf_votes if v >= 6)),
    }


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True,
                        help="H10 pool config name, e.g. pool_160_hp4hn4")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output directory (default: outputs/h10/wbf/<config>)")
    parser.add_argument("--iou-threshold", type=float,
                        default=DEFAULT_IOU_THRESHOLD)
    parser.add_argument("--min-separation-m", type=float,
                        default=DEFAULT_MIN_SEPARATION_M,
                        help="Set to 0 to disable the min-separation step.")
    parser.add_argument("--anchor-vote-threshold", type=int, default=None,
                        help="If set, the min-separation step is vote-aware: "
                             "pairs within min_separation_m are merged only "
                             "if at least one cluster has vote_count >= this "
                             "threshold. Leave unset for unconditional merging.")
    parser.add_argument("--min-dim", type=float, default=DEFAULT_MIN_DIMENSION_M)
    parser.add_argument("--max-dim", type=float, default=DEFAULT_MAX_DIMENSION_M)
    parser.add_argument("--min-area", type=float, default=DEFAULT_MIN_AREA_M2)
    parser.add_argument("--max-area", type=float, default=DEFAULT_MAX_AREA_M2)
    args = parser.parse_args()

    if args.output_dir is not None:
        output_dir = args.output_dir
    elif args.config in SPECIAL_CONFIGS:
        output_dir = Path(SPECIAL_CONFIGS[args.config]["default_output_dir"])
    else:
        output_dir = DEFAULT_OUTPUT_ROOT / args.config
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading raw per-pass detections for {args.config}...")
    boxes, load_diag = load_pass_boxes(args.config)
    total_passes = len(
        [p for p, n in load_diag["per_pass_box_counts"].items() if n > 0]
    )
    print(f"  {load_diag['total_raw_boxes']} raw boxes across "
          f"{total_passes} passes")
    for pid, n in sorted(load_diag["per_pass_box_counts"].items(),
                         key=lambda kv: int(kv[0].split('_')[1])):
        print(f"    {pid}: {n}")

    min_sep_desc = f"min_sep={args.min_separation_m} m"
    if args.anchor_vote_threshold is not None:
        min_sep_desc += f", anchor_vote>={args.anchor_vote_threshold}"
    print(f"\nRunning fusion (IoU={args.iou_threshold}, {min_sep_desc})...")
    clusters, fuse_diag = fuse_detections(
        boxes,
        iou_threshold=args.iou_threshold,
        min_separation_m=args.min_separation_m,
        anchor_vote_threshold=args.anchor_vote_threshold,
        min_dim=args.min_dim,
        max_dim=args.max_dim,
        min_area=args.min_area,
        max_area=args.max_area,
    )
    for k, v in fuse_diag.items():
        print(f"  {k}: {v}")

    # Write GeoJSON
    gj = clusters_to_geojson(clusters, total_passes=total_passes)
    gj_path = output_dir / "wbf_candidates.geojson"
    gj_path.write_text(json.dumps(gj, indent=2))
    print(f"\nWrote {gj_path}  ({len(clusters)} features)")

    # Write manifest (for downstream crop extraction / verifier run)
    manifest = clusters_to_manifest(
        clusters, total_passes=total_passes, config=args.config,
    )
    mf_path = output_dir / "wbf_candidates.json"
    mf_path.write_text(json.dumps(manifest, indent=2))
    print(f"Wrote {mf_path}")

    # Write diagnostics, including comparison to the existing consensus
    comparison = compare_to_existing_consensus(clusters, args.config)
    diag = {
        "config": args.config,
        "parameters": {
            "iou_threshold": args.iou_threshold,
            "min_separation_m": args.min_separation_m,
            "anchor_vote_threshold": args.anchor_vote_threshold,
            "min_dim": args.min_dim,
            "max_dim": args.max_dim,
            "min_area": args.min_area,
            "max_area": args.max_area,
        },
        "loader": load_diag,
        "fusion": fuse_diag,
        "comparison_to_existing_consensus": comparison,
    }
    diag_path = output_dir / "wbf_diagnostics.json"
    diag_path.write_text(json.dumps(diag, indent=2))
    print(f"Wrote {diag_path}")

    if comparison.get("available"):
        print("\nComparison with current consensus output:")
        print(f"  current: {comparison['current_consensus_candidate_count']} "
              f"candidates, mean vote count "
              f"{comparison['current_mean_vote_count']:.2f}")
        print(f"  wbf    : {comparison['wbf_candidate_count']} "
              f"candidates, mean vote count "
              f"{comparison['wbf_mean_vote_count']:.2f}")
        print(f"  delta  : {comparison['delta']:+d} candidates")
        print(f"  current vote>=6: {comparison['current_high_vote_count']}")
        print(f"  wbf     vote>=6: {comparison['wbf_high_vote_count']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
