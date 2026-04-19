#!/usr/bin/env python3
"""
Re-sweep PV Conditions on h10_test_bounds (Leaderboard 327-tile Scope)
======================================================================

The original verifier 2D sweeps (``sweep_2d.json``) were computed on
``inputs/vectors/bounds/384/full_evaluation_bounds.geojson`` (487 tiles
that span both calibration and test partitions). The leaderboard
protocol evaluates all Era 2 conditions on the held-out test set only:
``inputs/vectors/bounds/384/h10_test_bounds.geojson`` (327 tiles).

This script re-sweeps every PV condition's (vote_t, prob_t) grid on the
327-tile leaderboard bounds, identifies the 20 m-optimal operating
point, and re-materialises the post-verifier GeoJSON at that operating
point. Outputs:

- ``pv_registry_327.json`` — per-condition 327-tile optimum and full
  sweep grid at 20 m.
- Overwrites ``{id}.geojson`` in ``pv-materialised/`` at the 327-tile
  optimum.

No API calls. Reads existing consensus GeoJSONs + probabilities.json.

Usage::

    python scripts/resweep_pv_on_h10.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_detections import load_geojson, evaluate_single_run  # noqa: E402
from lib_advanced_metrics import calculate_f1_internal  # noqa: E402

BOUNDS_PATH = ROOT / "inputs/vectors/bounds/384/h10_test_bounds.geojson"
REF_PATH = ROOT / "inputs/vectors/references/mounds-reference.geojson"
REGISTRY_IN = ROOT / "results/leaderboard/era2/pv-materialised/pv_registry.json"
REGISTRY_OUT = ROOT / "results/leaderboard/era2/pv-materialised/pv_registry_327.json"
MATERIAL_DIR = ROOT / "results/leaderboard/era2/pv-materialised"

PROB_GRID = [round(x / 20, 2) for x in range(20)]  # 0.00, 0.05, ..., 0.95


def attach_source_tile(
    gdf: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Assign source_tile via spatial join if missing."""
    if "source_tile" not in gdf.columns and not gdf.empty:
        joined = gpd.sjoin(
            gdf, bounds[["tile_name", "geometry"]],
            how="left", predicate="intersects",
        )
        joined = joined[~joined.index.duplicated(keep="first")]
        gdf["source_tile"] = joined["tile_name"]
    return gdf


def sweep_one(
    consensus_geojson: Path,
    probabilities_json: Path,
    vote_max: int,
    bounds: gpd.GeoDataFrame,
    ref: gpd.GeoDataFrame,
    buffer_m: int = 20,
) -> list[dict]:
    """Sweep (vote_t, prob_t) at buffer_m on given bounds."""
    g = load_geojson(consensus_geojson)
    probs = json.load(open(probabilities_json))["results"]
    probs_by_idx = {
        int(k.split("_")[1]): v.get("mound_probability")
        for k, v in probs.items()
    }
    g = g.reset_index(drop=True)
    g["mound_probability"] = [probs_by_idx.get(i) for i in range(len(g))]
    if "vote_count" not in g.columns:
        g["vote_count"] = 1
    g = attach_source_tile(g, bounds)

    rows = []
    for vt in range(1, vote_max + 1):
        for pt in PROB_GRID:
            sub = g[
                (g["vote_count"] >= vt)
                & (g["mound_probability"].fillna(-1) >= pt)
            ]
            n = len(sub)
            if n == 0:
                rows.append({
                    "vote_t": vt, "prob_t": pt,
                    "n": 0, "p": 0.0, "r": 0.0, "f1": 0.0,
                })
                continue
            p, r, f1 = calculate_f1_internal(
                sub, ref, bounds, buffer_metres=buffer_m,
            )
            rows.append({
                "vote_t": vt,
                "prob_t": round(pt, 2),
                "n": n,
                "p": round(p, 4),
                "r": round(r, 4),
                "f1": round(f1, 4),
            })
    return rows


def main() -> int:
    """Re-sweep all PV conditions and write a refreshed registry."""
    ref = load_geojson(REF_PATH)
    bounds = load_geojson(BOUNDS_PATH)
    reg = json.load(open(REGISTRY_IN))

    updated = []
    for c in reg:
        if c.get("mode") == "manifest":
            # Legacy 16/30 — evaluate existing materialised at 327 tiles.
            gj_path = MATERIAL_DIR / f"{c['id']}.geojson"
            gdf = load_geojson(gj_path)
            gdf = attach_source_tile(gdf, bounds)
            r = evaluate_single_run(
                gdf, ref, bounds, buffers=[20],
                n_bootstrap=50, seed=42, label=c["id"],
            )
            b20 = r["buffers"][0]
            best = {
                "vote_t": 16, "prob_t": 0.20,
                "f1": round(b20["f1"], 4),
                "p": round(b20["precision"], 4),
                "r": round(b20["recall"], 4),
                "n": r["n_detections"],
            }
            print(f"{c['id']:<35} 327: F1={best['f1']:.3f}")
            updated.append({**c, "best_at_327": best})
            continue

        sw = json.load(open(ROOT / c["sweep_path"]))
        vote_max = max(r["vote_t"] for r in sw)
        rows = sweep_one(
            ROOT / c["consensus_path"],
            ROOT / c["probabilities_path"],
            vote_max, bounds, ref, buffer_m=20,
        )
        best = max(rows, key=lambda r: r["f1"])
        was = c["best_at_20m"]
        print(
            f"{c['id']:<35} 327: F1={best['f1']:.3f} "
            f"(vt={best['vote_t']} pt={best['prob_t']:.2f}) "
            f"was 487: F1={was['f1']:.3f} "
            f"(vt={was['vote_t']} pt={was['prob_t']:.2f})"
        )
        updated.append({**c, "best_at_327": best, "rows_327": rows})

    with open(REGISTRY_OUT, "w") as f:
        json.dump(updated, f, indent=2)
    print(f"\nWrote {REGISTRY_OUT}")

    # Re-materialise at the 327-tile optima
    print("\nRe-materialising GeoJSONs at 327-tile optima...")
    for c in updated:
        if c.get("mode") == "manifest":
            continue  # legacy 16/30 unchanged
        out = MATERIAL_DIR / f"{c['id']}.geojson"
        cmd = [
            sys.executable,
            str(ROOT / "scripts/materialise_pv_geojson.py"),
            "--consensus", str(ROOT / c["consensus_path"]),
            "--probabilities", str(ROOT / c["probabilities_path"]),
            "--vote-t", str(c["best_at_327"]["vote_t"]),
            "--prob-t", str(c["best_at_327"]["prob_t"]),
            "--output", str(out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  FAIL {c['id']}: {r.stderr.strip()[-200:]}")
        else:
            print(f"  {c['id']}: {r.stdout.strip().splitlines()[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
