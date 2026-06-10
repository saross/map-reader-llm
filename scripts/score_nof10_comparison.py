#!/usr/bin/env python3
# ============================================================================
# score_nof10_comparison.py
# ----------------------------------------------------------------------------
# Session 110 ($0): equal-cost apples-to-apples comparison —
#   5-pass proposer + N=5 verifier consensus (10 passes; current leader 0.8739)
#   vs the best 10-pass proposer + n=1 single-pass verifier (11 passes).
#
# Scores the flash-high-text-1of10 union (5,866 cands, vote_count 1..10,
# carry-forward verifier gemini-3-flash T=0.0 minimal n=1) by sweeping the
# proposer vote threshold k-of-10 x prob_t, reporting the best F1@20m. Same
# scope (384px/487-tile, curator GT), same verifier, same 14-buffer scorer as
# the 5-pass work, so the numbers are directly comparable.
#
# Usage:  python scripts/score_nof10_comparison.py
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-10 | Apache 2.0
# ============================================================================
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.analyse_verifier_robustness import (  # noqa: E402
    EVAL_CRS,
    GROUND_TRUTH,
    accepted_cids,
    load_candidate_table,
)
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402

POOL = BASE_DIR / "outputs/h11/pv-diag-384/verified/flash-high-text-1of10"
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
FIVE_PASS_LEADER = 0.8739  # 5 proposer + N=5 verifier consensus, T=0.3 mean-prob


def main() -> int:
    """Sweep k-of-10 proposer x prob_t (n=1 verifier); report the best F1@20m."""
    table = load_candidate_table(POOL / "candidate_manifest.json",
                                 POOL / "probabilities.json")
    by_cid = {r["cid"]: r for r in table}
    max_pk = max((r["vote_count"] for r in table), default=0)
    print(f"flash-high-text-1of10 union: {len(table)} candidates, "
          f"max proposer vote {max_pk}", flush=True)

    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)

    def score(cids):
        if not cids:
            return {"f1": 0.0, "mcc": None}
        sel = [by_cid[c] for c in cids]
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
        return score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                                   compute_mcc=True)

    print("\n=== 10-pass proposer (k-of-10) + n=1 carry-forward verifier ===",
          flush=True)
    best = {"f1": -1.0}
    for pk in range(1, max_pk + 1):
        bpk = {"f1": -1.0}
        for pt in PROB_TS:
            # n=1 verifier -> "mean" over one iteration is that iteration's prob.
            res = score(accepted_cids(table, pk, "mean", pt))
            if res["f1"] > bpk["f1"]:
                bpk = {"f1": res["f1"], "mcc": res["mcc"], "pt": pt}
        mcc = f"{bpk['mcc']:.3f}" if bpk["mcc"] is not None else "NA"
        print(f"  {pk}of10: bestF1={bpk['f1']:.4f}  MCC={mcc}  prob_t={bpk['pt']}",
              flush=True)
        if bpk["f1"] > best["f1"]:
            best = {**bpk, "pk": pk}

    print(f"\n>>> BEST 10-pass proposer + n=1 verifier (11 passes): "
          f"F1@20m={best['f1']:.4f} at {best['pk']}-of-10, prob_t={best['pt']}",
          flush=True)
    print(f">>> 5-pass proposer + N=5 verifier (10 passes):           "
          f"F1@20m={FIVE_PASS_LEADER:.4f}", flush=True)
    print(f">>> delta (10-prop+1-vf) - (5-prop+5-vf) = "
          f"{best['f1'] - FIVE_PASS_LEADER:+.4f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
