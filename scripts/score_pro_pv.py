#!/usr/bin/env python3
# ============================================================================
# score_pro_pv.py
# ----------------------------------------------------------------------------
# Session 110 ($0): re-score the on-disk Pro 3.1 proposer-verifier pools.
#
# The pro-high-text 5-pass proposer (gemini-3.1-pro-preview, HIGH thinking) 1-of-5
# union (504 candidates, EPSG:32635, vote_count 1..5) was already verified n=1 by
#   - the carry-forward FLASH minimal verifier  (pro-high-text-1of5-flash-minimal-verifier)
#   - a PRO verifier (gemini-3.1-pro, medium)    (pro-high-text-1of5-pro-verifier)
# Both probabilities.json are keyed candidate_00000..00503 (feature-index join to
# the union geojson, which carries geometry + vote_count). We sweep proposer-vote
# k-of-5 x prob_t and report the best F1@20m for each verifier — directly
# comparable (same 384px/487-tile GS scope, curator GT, 14-buffer scorer) to:
#   Flash 5-pass + verifier consensus  0.8739
#   Flash PV headline (16-of-30 + vf)  0.890
#   Pro consensus proposer-only        0.836
#
# Usage:  python scripts/score_pro_pv.py
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-10 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
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
)
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402

VERIFIED = BASE_DIR / "outputs/h11/pv-diag-384/verified"
UNION = BASE_DIR / "outputs/h11/pv-diag-384/consensus/pro-high-text-1of5.geojson"
POOLS = {
    "Pro-prop + Flash-vf (n=1)": VERIFIED / "pro-high-text-1of5-flash-minimal-verifier/probabilities.json",
    "Pro-prop + Pro-vf (n=1)": VERIFIED / "pro-high-text-1of5-pro-verifier/probabilities.json",
}
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]


def build_table(probs_path: Path) -> list[dict]:
    """Join the union geojson (geometry + vote_count, 32635) with verifier probs.

    candidate_id == union feature index (probabilities are keyed
    candidate_{i:05d} contiguously over the 504 features).
    """
    fc = json.loads(UNION.read_text())
    results = json.loads(probs_path.read_text())["results"]
    table = []
    for i, f in enumerate(fc["features"]):
        entry = results.get(f"candidate_{i:05d}")
        if not isinstance(entry, dict):
            continue
        p = entry.get("mound_probability")
        if not isinstance(p, (int, float)):
            continue
        x, y = f["geometry"]["coordinates"]
        table.append({"cid": i, "x": float(x), "y": float(y),
                      "vote_count": int(f["properties"].get("vote_count", 0)),
                      "source_tile": f["properties"].get("source_tile", ""),
                      "iter_probs": [float(p)]})
    return table


def main() -> int:
    """Sweep k-of-5 x prob_t for each Pro-proposer verifier pool; report best."""
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)

    def score(by_cid, cids):
        if not cids:
            return {"f1": 0.0, "mcc": None}
        sel = [by_cid[c] for c in cids]
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
        return score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                                   compute_mcc=True)

    for label, ppath in POOLS.items():
        table = build_table(ppath)
        by_cid = {r["cid"]: r for r in table}
        max_pk = max((r["vote_count"] for r in table), default=0)
        print(f"\n=== {label} | {len(table)} cands, max proposer vote {max_pk} ===",
              flush=True)
        best = {"f1": -1.0}
        for pk in range(1, max_pk + 1):
            bpk = {"f1": -1.0}
            for pt in PROB_TS:
                res = score(by_cid, accepted_cids(table, pk, "mean", pt))
                if res["f1"] > bpk["f1"]:
                    bpk = {"f1": res["f1"], "mcc": res["mcc"], "pt": pt}
            mcc = f"{bpk['mcc']:.3f}" if bpk["mcc"] is not None else "NA"
            print(f"  {pk}of5: bestF1={bpk['f1']:.4f}  MCC={mcc}  prob_t={bpk['pt']}",
                  flush=True)
            if bpk["f1"] > best["f1"]:
                best = {**bpk, "pk": pk}
        print(f"  >>> BEST {label}: F1@20m={best['f1']:.4f} at {best['pk']}-of-5, "
              f"prob_t={best['pt']}, MCC={best['mcc']}", flush=True)

    print("\nReference: Flash 5-pass+vf 0.8739 | Flash PV headline 0.890 | "
          "Pro consensus proposer-only 0.836", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
