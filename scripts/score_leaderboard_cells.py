#!/usr/bin/env python3
# ============================================================================
# score_leaderboard_cells.py
# ----------------------------------------------------------------------------
# Universal scorer for leaderboard cells. Given a candidate manifest (greedy,
# WBF, or any other aggregation output) and a matching verifier probabilities
# file, emit F1/P/R cells over a sweep of (vote_t, prob_t, buffer_m) on a
# specified tile-set universe.
#
# Designed for the 2026-04-13 leaderboard rebuild, which uses the
# 327-tile H10-clean test universe as the common evaluation denominator
# (see inputs/vectors/bounds/384/h10_test_bounds.geojson).
#
# Key detail vs calculate_f1_internal: this scorer pre-filters detections
# to the bounds tile set before computing F1, so configurations whose
# manifests cover a superset of the bounds universe (e.g. gold-standard-v2
# at 487 tiles being scored on the 327-tile H10-clean subset) are not
# penalised for FPs in tiles outside the evaluation universe.
#
# Supports four manifest schemas:
#   - greedy post-consensus manifests (vote_count + source_tile)
#   - WBF post-fusion manifests (vote_count + contributing_passes + source_tile)
#   - e47-style manifests (proposer_votes legacy field)
#   - any other schema with the same core fields
#
# Usage:
#     python scripts/score_leaderboard_cells.py \\
#         --manifest outputs/h10/verifier-crops/pool_160_hp4hn4/candidate_manifest.json \\
#         --probs outputs/h10/verified/pool_160_hp4hn4/probabilities.json \\
#         --bounds inputs/vectors/bounds/384/h10_test_bounds.geojson \\
#         --label "pool_160_hp4hn4--flash-adv-v1" \\
#         --output results/leaderboard/cells/pool_160_hp4hn4.json
# ============================================================================

from __future__ import annotations

import argparse
import json
import sys
from itertools import product
from pathlib import Path
from typing import Iterable

import geopandas as gpd
from shapely.geometry import MultiPoint, Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_advanced_metrics import calculate_f1_internal  # noqa: E402

TARGET_CRS = "EPSG:32635"
DEFAULT_GT = BASE_DIR / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
DEFAULT_BOUNDS = BASE_DIR / "inputs" / "vectors" / "bounds" / "384" / "h10_test_bounds.geojson"

DEFAULT_VOTE_THRESHOLDS = [2, 3, 4, 5, 6, 7, 8, 9, 10]
DEFAULT_PROB_THRESHOLDS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60]
DEFAULT_BUFFERS = [20, 30, 40, 50]


def load_candidates_with_probs(
    manifest_path: Path,
    probs_path: Path,
    tile_allowlist: set[str] | None = None,
) -> gpd.GeoDataFrame:
    """Load a candidate manifest + verifier probabilities into a GeoDataFrame.

    Auto-detects legacy ``proposer_votes`` vs current ``vote_count`` field.
    Auto-detects ``contributing_passes`` if present (used for x-of-5 subset
    filtering in the H10 10-pass bank).

    If ``tile_allowlist`` is provided, only candidates whose ``source_tile``
    appears in the allowlist are retained. This is the 327-tile restriction.
    """
    manifest = json.loads(manifest_path.read_text())
    probs = json.loads(probs_path.read_text()).get("results", {})

    rows = []
    for c in manifest.get("candidates", []):
        cid = c["candidate_id"]
        key = f"candidate_{cid:05d}"
        prob_entry = probs.get(key)
        if prob_entry is None:
            continue

        props = c.get("properties", {})
        vc = props.get("vote_count")
        if vc is None:
            vc = props.get("proposer_votes", 0)
        contributing = props.get("contributing_passes") or []

        source_tile = c.get("source_tile") or props.get("source_tile") or ""
        if tile_allowlist is not None and source_tile not in tile_allowlist:
            continue

        rows.append({
            "candidate_id": cid,
            "source_tile": source_tile,
            "vote_count": int(vc),
            "contributing_passes": tuple(contributing),
            "mound_probability": float(prob_entry["mound_probability"]),
            "geometry": Point(float(c["centroid_x"]), float(c["centroid_y"])),
        })

    return gpd.GeoDataFrame(rows, crs=TARGET_CRS)


def subset_by_pass_ids(
    gdf: gpd.GeoDataFrame,
    allowed_passes: Iterable[str] | None,
) -> gpd.GeoDataFrame:
    """For x-of-5 scoring on 10-pass banks: recompute vote_count using only
    the subset of contributing passes that fall within ``allowed_passes``.

    Candidates with zero contributing passes in the subset are dropped.

    If ``allowed_passes`` is None, returns the input unchanged (x-of-N mode
    where N matches the full pass count, e.g. x-of-10 on a 10-pass bank).
    """
    if allowed_passes is None:
        return gdf
    allowed = set(allowed_passes)
    rows = []
    for _, r in gdf.iterrows():
        cp = [p for p in r["contributing_passes"] if p in allowed]
        if not cp:
            continue
        new = r.copy()
        new["vote_count"] = len(cp)
        rows.append(new)
    if not rows:
        return gdf.iloc[0:0]
    return gpd.GeoDataFrame(rows, crs=gdf.crs)


def load_gt(path: Path) -> gpd.GeoDataFrame:
    g = gpd.read_file(path).to_crs(TARGET_CRS)

    def to_point(geom):
        if isinstance(geom, MultiPoint):
            return list(geom.geoms)[0]
        return geom

    g = g.copy()
    g["geometry"] = g.geometry.apply(to_point)
    return g


def load_bounds(path: Path) -> gpd.GeoDataFrame:
    return gpd.read_file(path).to_crs(TARGET_CRS)


def run_sweep(
    cands: gpd.GeoDataFrame,
    gt: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
    label: str,
    vote_thresholds: list[int],
    prob_thresholds: list[float],
    buffers: list[int],
) -> list[dict]:
    """Run the full (vote_t × prob_t × buffer_m) sweep.

    Returns a list of rows, one per cell. Each row contains label, thresholds,
    candidate count, precision, recall, F1.
    """
    rows: list[dict] = []
    for vt in vote_thresholds:
        sub_vt = cands[cands["vote_count"] >= vt]
        for pt in prob_thresholds:
            sub = sub_vt[sub_vt["mound_probability"] >= pt].reset_index(drop=True)
            n = len(sub)
            for bm in buffers:
                if n == 0:
                    rows.append({
                        "label": label,
                        "vote_t": vt, "prob_t": pt, "buffer_m": bm,
                        "n": 0, "p": 0.0, "r": 0.0, "f1": 0.0,
                    })
                    continue
                p, r, f1 = calculate_f1_internal(sub, gt, bounds, buffer_metres=bm)
                rows.append({
                    "label": label,
                    "vote_t": vt, "prob_t": pt, "buffer_m": bm,
                    "n": int(n),
                    "p": round(p, 4), "r": round(r, 4), "f1": round(f1, 4),
                })
    return rows


def find_optima_per_buffer(
    rows: list[dict], buffers: list[int],
) -> dict[int, dict]:
    """Return the best (vote_t, prob_t) row per buffer."""
    out: dict[int, dict] = {}
    for bm in buffers:
        sub = [r for r in rows if r["buffer_m"] == bm]
        if not sub:
            continue
        out[bm] = max(sub, key=lambda r: r["f1"])
    return out


def score_config(
    manifest: Path,
    probs: Path,
    bounds: Path,
    gt_path: Path,
    label: str,
    vote_thresholds: list[int],
    prob_thresholds: list[float],
    buffers: list[int],
    allowed_passes: list[str] | None = None,
    track: str = "unknown",
    aggregation: str = "unknown",
    verifier: str = "unknown",
) -> dict:
    """Score a single configuration on the given bounds universe.

    Pre-filters detections to the tile set in ``bounds`` and, optionally, to
    a subset of contributing passes (for x-of-5 scoring on 10-pass banks).

    Returns a dict with metadata, full sweep rows, and per-buffer optima.
    """
    bounds_gdf = load_bounds(bounds)
    tile_allowlist = set(bounds_gdf["tile_name"].tolist())

    cands = load_candidates_with_probs(manifest, probs, tile_allowlist=tile_allowlist)
    if allowed_passes is not None:
        cands = subset_by_pass_ids(cands, allowed_passes)

    gt = load_gt(gt_path)

    rows = run_sweep(
        cands, gt, bounds_gdf, label,
        vote_thresholds, prob_thresholds, buffers,
    )
    optima = find_optima_per_buffer(rows, buffers)

    return {
        "label": label,
        "track": track,
        "aggregation": aggregation,
        "verifier": verifier,
        "bounds_file": str(bounds),
        "n_bounds_tiles": len(tile_allowlist),
        "n_candidates_loaded": int(len(cands)),
        "allowed_passes": list(allowed_passes) if allowed_passes is not None else None,
        "parameters": {
            "vote_thresholds": vote_thresholds,
            "prob_thresholds": prob_thresholds,
            "buffers": buffers,
        },
        "sweep": rows,
        "optima_per_buffer": optima,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--probs", type=Path, required=True)
    parser.add_argument("--bounds", type=Path, default=DEFAULT_BOUNDS)
    parser.add_argument("--gt", type=Path, default=DEFAULT_GT)
    parser.add_argument("--label", type=str, required=True)
    parser.add_argument("--track", type=str, default="unknown",
                        choices=["text", "image", "mixed", "unknown"])
    parser.add_argument("--aggregation", type=str, default="greedy",
                        choices=["greedy", "wbf", "raw-consensus", "unknown"])
    parser.add_argument("--verifier", type=str, default="unknown")
    parser.add_argument("--allowed-passes", type=str, default=None,
                        help="Comma-separated list of pass IDs to keep (e.g. "
                             "'run_1,run_2,run_3,run_4,run_5' for x-of-5 on a "
                             "10-pass bank). Default: no filter.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--vote-thresholds", type=str, default=None,
                        help="Comma-separated override of default vote thresholds")
    parser.add_argument("--prob-thresholds", type=str, default=None,
                        help="Comma-separated override of default prob thresholds")
    parser.add_argument("--buffers", type=str, default=None,
                        help="Comma-separated override of default buffers")
    args = parser.parse_args()

    vote_thresholds = (
        [int(x) for x in args.vote_thresholds.split(",")]
        if args.vote_thresholds is not None else DEFAULT_VOTE_THRESHOLDS
    )
    prob_thresholds = (
        [float(x) for x in args.prob_thresholds.split(",")]
        if args.prob_thresholds is not None else DEFAULT_PROB_THRESHOLDS
    )
    buffers = (
        [int(x) for x in args.buffers.split(",")]
        if args.buffers is not None else DEFAULT_BUFFERS
    )
    allowed_passes = (
        args.allowed_passes.split(",")
        if args.allowed_passes is not None else None
    )

    result = score_config(
        manifest=args.manifest,
        probs=args.probs,
        bounds=args.bounds,
        gt_path=args.gt,
        label=args.label,
        vote_thresholds=vote_thresholds,
        prob_thresholds=prob_thresholds,
        buffers=buffers,
        allowed_passes=allowed_passes,
        track=args.track,
        aggregation=args.aggregation,
        verifier=args.verifier,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, default=str))

    print(f"Scored {args.label}")
    print(f"  n_bounds_tiles={result['n_bounds_tiles']}")
    print(f"  n_candidates_loaded={result['n_candidates_loaded']}")
    print()
    print(f"  Optima per buffer:")
    for bm, r in result["optima_per_buffer"].items():
        print(f"    {bm:>3} m | vote≥{r['vote_t']} prob≥{r['prob_t']:.2f} | "
              f"n={r['n']:>4} P={r['p']:.4f} R={r['r']:.4f} F1={r['f1']:.4f}")
    print(f"\nWrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
