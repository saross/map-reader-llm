#!/usr/bin/env python3
# ============================================================================
# analyse_flash35_2x2.py
# ----------------------------------------------------------------------------
# Session 111/112 ($0): the 2 x 2 x 2 analysis of the Flash 3.5 tranche —
# proposer model (F3/F3.5) x verifier model (F3/F3.5) x n in {5, 10} — all
# text track, 384 px, 487 tiles, minimal thinking, T=0.7 proposer / T=0.0
# n=1 verifier, F1@20m + tile-MCC at each cell's best (k, prob_t).
#
# METHOD-MATCHED n=5 (per first5of10-validation): every n=5 cell is derived
# post-hoc from its verified 10-pass union by restricting votes to passes
# 1-5 via contributing_passes — BOTH models, so the small systematic
# derivation effect cancels in cross-model comparisons.
#
# Cells skip gracefully when their tranche outputs are not yet on disk
# (--smoke additionally restricts to one scoring per cell for a fast
# join-logic check).
#
# Usage (zbook):
#   .venv/bin/python scripts/analyse_flash35_2x2.py [--smoke]
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.analyse_verifier_robustness import (  # noqa: E402
    EVAL_CRS,
    GROUND_TRUTH,
    load_candidate_table,
)
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402

T2 = BASE_DIR / "outputs" / "flash35-pv-2x2"
PVD = BASE_DIR / "outputs" / "h11" / "pv-diag-384"
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUT_DIR = BASE_DIR / "results" / "flash35-2x2"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
FIRST5 = {f"run_{i}" for i in range(1, 6)}

F3_UNION = T2 / "consensus/f3-min-text-1of10-with-passes.geojson"
F3_UNION_FALLBACK = (BASE_DIR / "results/verifier-robustness/first5of10-validation"
                     / "text-n10-1of10-remerged.geojson")
F35_UNION = T2 / "consensus/flash35-min-text-1of10.geojson"


def to_32635(path: Path) -> gpd.GeoDataFrame:
    """Read a geojson, magnitude-detect undeclared CRS, return EPSG:32635."""
    g = gpd.read_file(path)
    crs = "EPSG:32635" if abs(g.geometry.x.iloc[0]) > 180 else "EPSG:4326"
    return g.set_crs(crs, allow_override=True).to_crs("EPSG:32635")


def passes_lookup(union: gpd.GeoDataFrame):
    """KD-tree over union centroids -> contributing_passes per query point."""
    tree = cKDTree(np.c_[union.geometry.x, union.geometry.y])

    def lookup(x: float, y: float) -> list[str] | None:
        d, j = tree.query([x, y])
        if d > 1.0:
            return None
        cp = union["contributing_passes"].iloc[int(j)]
        return json.loads(cp.replace("'", '"')) if isinstance(cp, str) else list(cp)
    return lookup


def attach_first5(table: list[dict], union: gpd.GeoDataFrame, label: str) -> list[dict]:
    """Attach first-5 vote counts to a candidate table via the union NN join."""
    lookup = passes_lookup(union)
    unmatched = 0
    for r in table:
        cp = lookup(r["x"], r["y"])
        if cp is None:
            unmatched += 1
            r["first5_votes"] = 0
        else:
            r["first5_votes"] = sum(1 for p in cp if p in FIRST5)
    if unmatched:
        print(f"  WARNING [{label}]: {unmatched}/{len(table)} candidates "
              f"unmatched in the passes join", flush=True)
    return table


def committed_f3_table() -> list[dict]:
    """The F3 10-pool with its committed carry-forward verifier probs.

    text-1of10 has no candidate manifest; probabilities key candidate_{i}
    by feature index over the committed union geojson (974-pattern).
    """
    fc = json.loads((PVD / "consensus/text-1of10.geojson").read_text())
    results = json.loads(
        (PVD / "verified/text-1of10/probabilities.json").read_text())["results"]
    table = []
    for i, f in enumerate(fc["features"]):
        val = results.get(f"candidate_{i:05d}")
        p = val.get("mound_probability") if isinstance(val, dict) else None
        if not isinstance(p, (int, float)):
            continue
        x, y = f["geometry"]["coordinates"][:2]
        table.append({"cid": i, "x": float(x), "y": float(y),
                      "vote_count": int(f["properties"].get("vote_count", 0)),
                      "source_tile": f["properties"].get("source_tile", ""),
                      "iter_probs": [float(p)]})
    return table


def sweep(table, ks, vote_field, gdf_ref, gdf_bounds, smoke=False,
          prob_ts=None) -> dict:
    """Best F1@20m (+MCC) over k x prob_t with the n=1 'mean' rule."""
    prob_ts = prob_ts or PROB_TS
    if smoke:
        ks, prob_ts = ks[:1], (prob_ts[2:3] or prob_ts[:1])
    best = {"f1": -1.0}
    per_k = {}
    for k in ks:
        bk = {"f1": -1.0}
        for pt in prob_ts:
            sel = [r for r in table if r[vote_field] >= k and r["iter_probs"][0] >= pt]
            if not sel:
                continue
            gdf = gpd.GeoDataFrame(
                {"geometry": [Point(r["x"], r["y"]) for r in sel],
                 "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
            res = score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                                      compute_mcc=True)
            if res["f1"] > bk["f1"]:
                bk = {"f1": res["f1"], "mcc": res["mcc"], "pt": pt, "n": len(sel)}
        per_k[k] = {k2: (round(v, 4) if isinstance(v, float) else v)
                    for k2, v in bk.items()}
        if bk["f1"] > best["f1"]:
            best = {**bk, "k": k}
    return {"best": {k2: (round(v, 4) if isinstance(v, float) else v)
                     for k2, v in best.items()}, "per_k": per_k}


def bare_sweep(union, ks, vote_field, gdf_ref, gdf_bounds, smoke=False) -> dict:
    """Bare-consensus sweep (no verifier): vote threshold only."""
    table = [{"x": g.x, "y": g.y, "source_tile": st, "vote_count": vc,
              "first5_votes": fv, "iter_probs": [1.0]}
             for g, st, vc, fv in zip(union.geometry, union["source_tile_"],
                                      union["vote_count"], union["first5_votes"])]
    return sweep(table, ks, vote_field, gdf_ref, gdf_bounds, smoke,
                 prob_ts=[0.0])


def main() -> int:
    """Run every available cell of the 2x2x2 + bare-consensus rows."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="one scoring per cell (join-logic check)")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)

    f3_union_path = F3_UNION if F3_UNION.exists() else F3_UNION_FALLBACK
    f3_union = to_32635(f3_union_path)
    f35_union = to_32635(F35_UNION) if F35_UNION.exists() else None

    # (cell label, table builder, union for the passes join)
    def cell_specs():
        yield ("f3prop-f3vf", committed_f3_table, f3_union)
        m2, p2 = T2 / "min-f3-crops/candidate_manifest.json", \
            T2 / "min-f3-verified-f35vf/probabilities.json"
        if m2.exists() and p2.exists():
            yield ("f3prop-f35vf", lambda: load_candidate_table(m2, p2), f3_union)
        m3, p3 = T2 / "crops/candidate_manifest.json", \
            T2 / "verified-f3vf/probabilities.json"
        if m3.exists() and p3.exists() and f35_union is not None:
            yield ("f35prop-f3vf", lambda: load_candidate_table(m3, p3), f35_union)
        p4 = T2 / "verified-f35vf/probabilities.json"
        if m3.exists() and p4.exists() and f35_union is not None:
            yield ("f35prop-f35vf", lambda: load_candidate_table(m3, p4), f35_union)

    out = {"smoke": args.smoke, "cells": {}}
    for label, build, union in cell_specs():
        print(f"=== {label} ===", flush=True)
        table = attach_first5(build(), union, label)
        n10 = sweep(table, list(range(1, 11)), "vote_count",
                    gdf_ref, gdf_bounds, args.smoke)
        n5 = sweep(table, list(range(1, 6)), "first5_votes",
                   gdf_ref, gdf_bounds, args.smoke)
        out["cells"][label] = {"n_candidates": len(table),
                               "n10": n10, "n5_derived": n5}
        print(f"  n10 best: {n10['best']}", flush=True)
        print(f"  n5  best: {n5['best']}", flush=True)

    # Bare-consensus rows (proposer-only) for each union with vote data.
    for label, union in [("f3prop-bare", f3_union), ("f35prop-bare", f35_union)]:
        if union is None:
            continue
        print(f"=== {label} (no verifier) ===", flush=True)
        u = union.copy()

        def first_tile(v) -> str:
            """First contributing tile from a source_tiles list (or its string form)."""
            if isinstance(v, (list, tuple)):
                return v[0] if v else ""
            if isinstance(v, str):
                return v.strip("[] ").split(",")[0].strip("'\" ")
            return ""
        col = "source_tiles" if "source_tiles" in u.columns else "source_tile"
        u["source_tile_"] = [first_tile(v) for v in u[col]]
        lookup = passes_lookup(union)
        u["first5_votes"] = [
            sum(1 for p in (lookup(g.x, g.y) or []) if p in FIRST5)
            for g in u.geometry]
        n10 = bare_sweep(u, list(range(1, 11)), "vote_count",
                         gdf_ref, gdf_bounds, args.smoke)
        n5 = bare_sweep(u, list(range(1, 6)), "first5_votes",
                        gdf_ref, gdf_bounds, args.smoke)
        out["cells"][label] = {"n_candidates": len(u), "n10": n10, "n5_derived": n5}
        print(f"  n10 best: {n10['best']}", flush=True)
        print(f"  n5  best: {n5['best']}", flush=True)

    suffix = "smoke" if args.smoke else "full"
    (OUT_DIR / f"analysis-{suffix}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nWrote {OUT_DIR.relative_to(BASE_DIR)}/analysis-{suffix}.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
