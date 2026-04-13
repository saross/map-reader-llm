#!/usr/bin/env python3
# ============================================================================
# sweep_f1_wbf.py
# ----------------------------------------------------------------------------
# F1 sweep over (vote_t, prob_t) for a WBF-fused candidate set.
#
# Matches the format of results/h10/sweep_results.json (which was built for
# the greedy-ball H10/H12 output) so the WBF result can be compared directly
# against the 0.885 baseline.
#
# Inputs (--crops-dir / --verified-dir pair):
#   <crops-dir>/candidate_manifest.json   — WBF candidates with vote_count
#   <verified-dir>/probabilities.json     — verifier mound_probability per candidate
#
# Ground truth (hard-coded defaults):
#   inputs/vectors/references/mounds-reference.geojson  — 569 GT mounds
#   inputs/calibration/h10-384/test_bounds.geojson      — 327 test tiles
#
# Outputs (--output):
#   A JSON file with one row per (vote_t, prob_t) combination, schema:
#     {config, vote_t, prob_t, n, p, r, f1}
#
# Usage::
#
#     python scripts/sweep_f1_wbf.py \
#         --config pool_160_hp4hn4_variant_c \
#         --crops-dir outputs/h10/wbf/pool_160_hp4hn4_variant_c/crops \
#         --verified-dir outputs/h10/wbf/pool_160_hp4hn4_variant_c/verified \
#         --output results/h10/wbf/sweep_results_pool_160_hp4hn4_variant_c.json
# ============================================================================

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import MultiPoint, Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_advanced_metrics import calculate_f1_internal

TARGET_CRS = "EPSG:32635"

DEFAULT_GT = BASE_DIR / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
DEFAULT_BOUNDS = BASE_DIR / "inputs" / "calibration" / "h10-384" / "test_bounds.geojson"

#: Vote thresholds to sweep. Matches the range used in the original H10
#: greedy-ball sweep (results/h10/sweep_results.json).
VOTE_THRESHOLDS = list(range(2, 11))  # 2..10 inclusive

#: Probability thresholds to sweep. Same grid as the original H10 run so
#: the optimum rows are directly comparable.
PROB_THRESHOLDS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60]


def load_candidates_as_gdf(
    manifest_path: Path,
    probabilities_path: Path,
) -> gpd.GeoDataFrame:
    """Load a WBF candidate manifest + verifier probabilities into a GeoDataFrame.

    Each row represents one fused candidate with the columns:
        candidate_id, source_tile, vote_count, mound_probability, geometry
    """
    manifest = json.loads(manifest_path.read_text())
    probs = json.loads(probabilities_path.read_text())["results"]

    rows = []
    for c in manifest["candidates"]:
        cid = c["candidate_id"]
        key = f"candidate_{cid:05d}"
        prob_entry = probs.get(key)
        if prob_entry is None:
            # Skip unverified candidates — downstream treats them as FPs.
            continue
        props = c.get("properties", {})
        rows.append({
            "candidate_id": cid,
            "source_tile": c.get("source_tile", ""),
            "vote_count": int(props.get("vote_count", 0)),
            "mound_probability": float(prob_entry["mound_probability"]),
            "geometry": Point(float(c["centroid_x"]), float(c["centroid_y"])),
        })

    gdf = gpd.GeoDataFrame(rows, crs=TARGET_CRS)
    return gdf


def load_ground_truth() -> gpd.GeoDataFrame:
    """Load the mound reference dataset, normalised to single-point geometry."""
    gt = gpd.read_file(DEFAULT_GT).to_crs(TARGET_CRS)
    def to_point(g):
        if isinstance(g, MultiPoint):
            return list(g.geoms)[0]
        return g
    gt = gt.copy()
    gt["geometry"] = gt.geometry.apply(to_point)
    return gt


def load_bounds() -> gpd.GeoDataFrame:
    return gpd.read_file(DEFAULT_BOUNDS).to_crs(TARGET_CRS)


def run_sweep(
    config_name: str,
    candidates_gdf: gpd.GeoDataFrame,
    gt_gdf: gpd.GeoDataFrame,
    bounds_gdf: gpd.GeoDataFrame,
    buffer_m: int = 20,
) -> list[dict]:
    """Evaluate every (vote_t, prob_t) combination and return the result rows."""
    rows: list[dict] = []
    for vt in VOTE_THRESHOLDS:
        for pt in PROB_THRESHOLDS:
            sub = candidates_gdf[
                (candidates_gdf["vote_count"] >= vt)
                & (candidates_gdf["mound_probability"] >= pt)
            ]
            n = len(sub)
            if n == 0:
                rows.append({
                    "config": config_name,
                    "vote_t": vt,
                    "prob_t": pt,
                    "n": 0,
                    "p": 0.0,
                    "r": 0.0,
                    "f1": 0.0,
                })
                continue
            p, r, f1 = calculate_f1_internal(
                sub, gt_gdf, bounds_gdf, buffer_metres=buffer_m,
            )
            rows.append({
                "config": config_name,
                "vote_t": vt,
                "prob_t": pt,
                "n": n,
                "p": round(p, 4),
                "r": round(r, 4),
                "f1": round(f1, 4),
            })
    return rows


def summarise(rows: list[dict]) -> None:
    """Print a human-readable summary: optimal (vote_t, prob_t) and top-10 rows."""
    if not rows:
        print("No sweep rows!")
        return
    best = max(rows, key=lambda r: r["f1"])
    print(f"\nOptimal: vote_t={best['vote_t']}  prob_t={best['prob_t']:.2f}  "
          f"n={best['n']}  P={best['p']:.4f}  R={best['r']:.4f}  "
          f"F1={best['f1']:.4f}")

    top = sorted(rows, key=lambda r: -r["f1"])[:10]
    print("\nTop-10 rows by F1:")
    print(f"  {'vote_t':<8}{'prob_t':<8}{'n':<8}{'P':<8}{'R':<8}{'F1':<8}")
    for r in top:
        print(f"  {r['vote_t']:<8}{r['prob_t']:<8.2f}{r['n']:<8}"
              f"{r['p']:<8.4f}{r['r']:<8.4f}{r['f1']:<8.4f}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True,
                        help="Config label (for the output rows)")
    parser.add_argument("--crops-dir", type=Path, required=True,
                        help="Directory with WBF candidate_manifest.json")
    parser.add_argument("--verified-dir", type=Path, required=True,
                        help="Directory with verifier probabilities.json")
    parser.add_argument("--output", type=Path, required=True,
                        help="Output JSON path for sweep rows")
    parser.add_argument("--buffer-m", type=int, default=20,
                        help="Hungarian matching buffer in metres (default 20)")
    args = parser.parse_args()

    manifest = args.crops_dir / "candidate_manifest.json"
    probs = args.verified_dir / "probabilities.json"
    if not manifest.exists():
        print(f"Error: manifest not found: {manifest}", file=sys.stderr)
        return 1
    if not probs.exists():
        print(f"Error: probabilities not found: {probs}", file=sys.stderr)
        return 1

    print(f"Loading candidates + probabilities...")
    cands = load_candidates_as_gdf(manifest, probs)
    print(f"  {len(cands)} candidates (with verifier probability)")

    print(f"Loading GT + bounds...")
    gt = load_ground_truth()
    bounds = load_bounds()
    print(f"  {len(gt)} GT mounds, {len(bounds)} test tiles")

    print(f"Running sweep...")
    rows = run_sweep(args.config, cands, gt, bounds, buffer_m=args.buffer_m)
    print(f"  {len(rows)} sweep rows")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2))
    print(f"Wrote {args.output}")

    summarise(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
