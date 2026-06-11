#!/usr/bin/env python3
# ============================================================================
# score_min11_uplift.py
# ----------------------------------------------------------------------------
# Session 112 ($0): score the min6 -> min11 production uplift (Run B) and
# answer Obs 362's open question — does PASS COUNT close the -0.030
# thinking gap at deployment?
#
# Sweeps k(3..10) x prob_t over the verified >=3-of-10 band of the 10-pass
# minimal union (16,482 crops, 0 failures) against the canonical GT at the
# 50 m operational buffer, then runs targeted tile-swap permutations of the
# best operating point vs TM-k3 (the 5-pass minimal cell) and TH7-k3 (the
# HIGH-thinking Tier-1 cell). Threshold status is matched: the k3 board
# cells are themselves post-hoc threshold choices (S104).
#
# Usage (zbook):  .venv/bin/python scripts/score_min11_uplift.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
from scripts.analyse_verifier_robustness import (  # noqa: E402
    EVAL_CRS,
    accepted_cids,
    load_candidate_table,
)
from scripts.build_55map_leaderboard import canonical_gt_at  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
    score_detection_set,
)
from scripts.n1_baseline_leaderboard_tiering import permutation_test_float  # noqa: E402
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402

UP = BASE_DIR / "outputs/55maps-text-min-n10-uplift"
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
OUT = BASE_DIR / "results/55map-leaderboard/min11_uplift_cell.json"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
BUFFER_M = 50
COMPARATORS = {
    "TM-k3": "results/deployment-oracle-2026-06-06/k3-scoring/"
             "55maps-text-min-generalisation/k3_verified.geojson",
    "TH7-k3": "results/deployment-oracle-2026-06-06/k3-scoring/"
              "55maps-text-high-generalisation/k3_verified.geojson",
}


def per_tile(gdf, gdf_ref, gdf_bounds, tile_order):
    """Per-tile TP/FP/FN at 50 m, aligned to the fixed tile order."""
    gdf = assign_source_tiles(gdf, gdf_bounds)
    tm = compute_per_tile_tp_fp_fn(gdf, gdf_ref, gdf_bounds, buffer_metres=BUFFER_M)
    idx = {t: i for i, t in enumerate(tile_order)}
    tp = np.zeros(len(tile_order)); fp = np.zeros(len(tile_order))  # noqa: E702
    fn = np.zeros(len(tile_order))
    for _, row in tm.iterrows():
        i = idx.get(row["tile_name"])
        if i is not None:
            tp[i], fp[i], fn[i] = float(row["tp"]), float(row["fp"]), float(row["fn"])
    return tp, fp, fn


def main() -> int:
    """Sweep, pick best op, permute vs the k3 comparators, report."""
    gdf_bounds = gpd.read_file(BOUNDS)
    if gdf_bounds.crs is None:
        gdf_bounds = gdf_bounds.set_crs("EPSG:4326")
    gdf_bounds = gdf_bounds.to_crs("EPSG:32635")
    tile_order = sorted(gdf_bounds["tile_name"].tolist())
    gdf_ref = canonical_gt_at(BUFFER_M)
    table = load_candidate_table(UP / "crops-3of10/candidate_manifest.json",
                                 UP / "verified-3of10/probabilities.json")
    by = {r["cid"]: r for r in table}
    print(f"uplift band: {len(table)} candidates", flush=True)

    best = {"f1": -1.0}
    for k in range(3, 11):
        bk = {"f1": -1.0}
        for pt in PROB_TS:
            cids = accepted_cids(table, k, "mean", pt)
            if not cids:
                continue
            sel = [by[c] for c in sorted(cids)]
            g = gpd.GeoDataFrame(
                {"geometry": [Point(r["x"], r["y"]) for r in sel],
                 "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
            f1 = score_detection_set(g, gdf_ref, gdf_bounds, buffer_metres=BUFFER_M,
                                     compute_mcc=False)["f1"]
            if f1 > bk["f1"]:
                bk = {"f1": f1, "pt": pt, "sel": sel}
        print(f"  {k}of10: bestF1@50={bk['f1']:.4f} pt={bk.get('pt')}", flush=True)
        if bk["f1"] > best["f1"]:
            best = {**bk, "k": k}

    g_best = gpd.GeoDataFrame(
        {"geometry": [Point(r["x"], r["y"]) for r in best["sel"]],
         "source_tile": [r["source_tile"] for r in best["sel"]]}, crs=EVAL_CRS)
    full = score_detection_set(g_best, gdf_ref, gdf_bounds, buffer_metres=BUFFER_M,
                               compute_mcc=True)
    print(f"\nBEST uplift: F1@50={full['f1']:.4f} P={full['precision']:.4f} "
          f"R={full['recall']:.4f} MCC={full['mcc']:.4f} "
          f"({best['k']}of10/pt{best['pt']}, n={len(best['sel'])})", flush=True)

    pt_up = per_tile(g_best, gdf_ref, gdf_bounds, tile_order)
    pairs = {}
    for name, rel in COMPARATORS.items():
        det = gpd.read_file(BASE_DIR / rel)
        crs = "EPSG:32635" if abs(det.geometry.x.iloc[0]) > 180 else "EPSG:4326"
        det = det.set_crs(crs, allow_override=True).to_crs("EPSG:32635")
        r = permutation_test_float(*pt_up, *per_tile(det, gdf_ref, gdf_bounds, tile_order),
                                   n_permutations=10000, seed=42)
        pairs[name] = r
        print(f"uplift vs {name}: {r['f1_a']:.4f} vs {r['f1_b']:.4f} "
              f"diff={r['observed_diff']:+.4f} p={r['p_value']:.4f}", flush=True)

    OUT.write_text(json.dumps({
        "cell": "min11-uplift (10x minimal T0.7 passes + n=1 carry-forward vf, "
                ">=3of10 band)",
        "best_op": f"{best['k']}of10/pt{best['pt']}", "n": len(best["sel"]),
        "f1_50": round(full["f1"], 4), "p_50": round(full["precision"], 4),
        "r_50": round(full["recall"], 4), "mcc": round(float(full["mcc"]), 4),
        "permutations": pairs}, indent=2, default=float) + "\n")
    print(f"Wrote {OUT.relative_to(BASE_DIR)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
