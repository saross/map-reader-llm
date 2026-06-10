#!/usr/bin/env python3
# ============================================================================
# score_zero_diversity_anchor.py
# ----------------------------------------------------------------------------
# Session 111 ($0): score the ZERO-DIVERSITY proposer-verifier reference
# cell — ONE minimal-thinking T=0.0 text proposer pass fed through the
# carry-forward n=1 verifier (the on-disk h11 `text-baseline` material).
# Its F1@20m anchors the diversity analysis in pool_recall_ceilings.json:
# the gap to the 5-pass T=0.7 result (0.8708) is what temperature-sampled
# multi-pass diversity buys under PV.
#
# Lineage verified from the on-disk meta files (2026-06-10):
#   proposer  detections_text-t0.0_run01.meta.json — gemini-3-flash,
#             detect_brief-text.md, MINIMAL thinking, T=0.0, text-only
#             examples; 487-tile scope (486 completed, 1 failed:
#             K-35-052-4_32635_x0_y2352.png), 1047 detections.
#   verifier  verified/text-baseline/run.meta.json — gemini-3-flash,
#             verify_adversarial-text, MINIMAL thinking, T=0.0;
#             probabilities.json iterations=1, total_results=1047.
#
# Join: crops/text-baseline/candidate_manifest.json (cids 0..1046,
# centroids EPSG:32635) <-> probabilities keyed candidate_{i:05d}, via
# analyse_verifier_robustness.load_candidate_table (bare key -> iter 1).
#
# Sweeps prob_t (rule "mean": n=1 -> that iteration's prob), reports
# F1@20m + MCC per threshold, the pool's recall ceiling at 20 m, writes
# the best-op set to results/verifier-robustness/min-thinking-sets/ and
# a JSON summary to results/verifier-robustness/zero_diversity_anchor.json.
#
# COST: $0 (on-disk re-score). Run on zbook per the project compute rule.
#
# Usage:
#   .venv/bin/python scripts/score_zero_diversity_anchor.py
#
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
    load_candidate_table,
)
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402

PV_DIAG = BASE_DIR / "outputs" / "h11" / "pv-diag-384"
MANIFEST = PV_DIAG / "crops" / "text-baseline" / "candidate_manifest.json"
PROBS = PV_DIAG / "verified" / "text-baseline" / "probabilities.json"
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
SETS_DIR = BASE_DIR / "results" / "verifier-robustness" / "min-thinking-sets"
OUT_JSON = BASE_DIR / "results" / "verifier-robustness" / "zero_diversity_anchor.json"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]

# Reference points for the comparison print-out (committed records:
# min_thinking_pv.log / pool_recall_ceilings.json).
MIN5_F1 = 0.8708    # 5 MIN T=0.7 props + n=1 vf (n30-lineage 4of5/pt0.15)
MIN5_CEIL = 0.9195  # that pool's recall ceiling at 20 m
MIN10_F1 = 0.8835   # 10 MIN T=0.7 props + n=1 vf (6of10/pt0.2)


def main() -> int:
    """Score the zero-diversity (1-pass T=0.0) PV anchor and write outputs."""
    SETS_DIR.mkdir(parents=True, exist_ok=True)
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)

    # Candidate table: manifest centroids joined to n=1 verifier probs.
    table = load_candidate_table(MANIFEST, PROBS)
    n_manifest = len(json.loads(MANIFEST.read_text())["candidates"])
    n_probs = len(json.loads(PROBS.read_text())["results"])
    print(f"manifest candidates={n_manifest}  probability results={n_probs}  "
          f"joined={len(table)}", flush=True)
    if len(table) < n_manifest:
        print(f"  NOTE: {n_manifest - len(table)}/{n_manifest} candidates "
              f"lack a verifier probability", flush=True)

    # CRS guard (Obs 350 trap): manifest centroids must be projected metres.
    if abs(table[0]["x"]) <= 180:
        raise SystemExit("centroids look geographic, expected EPSG:32635")

    # Single proposer pass: every candidate carries exactly one proposer
    # vote. The manifest properties have no vote_count (no consensus step),
    # so load_candidate_table defaults it to 0 — normalise to 1 so the
    # shared accepted_cids(proposer_k=1, ...) filter behaves correctly.
    for r in table:
        r["vote_count"] = 1
    by_cid = {r["cid"]: r for r in table}

    def gdf_of(cids: frozenset[int]) -> gpd.GeoDataFrame:
        sel = [by_cid[c] for c in sorted(cids)]
        return gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)

    # Pool recall ceiling: score the full 1-pass pool, read recall.
    pool = score_detection_set(gdf_of(frozenset(by_cid)), gdf_ref, gdf_bounds,
                               buffer_metres=20, compute_mcc=False)
    ceil = pool["recall"]
    f1max = 2 * ceil / (1 + ceil)  # ceiling F1 at perfect precision
    print(f"\npool: n={len(table)}  recall ceiling@20m={ceil:.4f}  "
          f"F1max={f1max:.4f}", flush=True)

    # prob_t sweep (rule "mean": single iteration -> that probability).
    print("\n=== zero-diversity anchor sweep (1 pass, n=1 verifier) ===",
          flush=True)
    sweep_rows = []
    best = {"f1": -1.0}
    for pt in PROB_TS:
        cids = accepted_cids(table, 1, "mean", pt)
        if not cids:
            print(f"  pt{pt}: no candidates accepted", flush=True)
            continue
        gdf = gdf_of(cids)
        res = score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                                  compute_mcc=True)
        mcc = f"{res['mcc']:.3f}" if res.get("mcc") is not None else "NA"
        print(f"  pt{pt}: F1={res['f1']:.4f}  MCC={mcc}  "
              f"P={res['precision']:.4f}  R={res['recall']:.4f}  "
              f"n={len(cids)}", flush=True)
        sweep_rows.append({"prob_t": pt, "f1": round(res["f1"], 4),
                           "mcc": round(res["mcc"], 4) if res["mcc"] is not None else None,
                           "precision": round(res["precision"], 4),
                           "recall": round(res["recall"], 4),
                           "n_accepted": len(cids)})
        if res["f1"] > best["f1"]:
            best = {"f1": res["f1"], "mcc": res["mcc"], "pt": pt,
                    "n": len(cids), "gdf": gdf,
                    "precision": res["precision"], "recall": res["recall"]}

    gj = SETS_DIR / f"text-baseline-1pass-n1-pt{best['pt']}.geojson"
    best["gdf"].to_crs("EPSG:4326").to_file(gj, driver="GeoJSON")
    print(f"\n>>> BEST zero-diversity anchor: F1@20m={best['f1']:.4f} "
          f"MCC={best['mcc']:.3f} at pt{best['pt']} (n={best['n']}) "
          f"-> {gj.relative_to(BASE_DIR)}", flush=True)

    print("\n=== diversity dividend (F1@20m, GS 384/487, curator GT) ===",
          flush=True)
    print(f"  anchor (1 MIN T=0.0 prop + 1 vf):  {best['f1']:.4f}  "
          f"(ceiling {ceil:.4f}, n={len(table)})", flush=True)
    print(f"  min6   (5 MIN T=0.7 props + 1 vf): {MIN5_F1:.4f}  "
          f"(ceiling {MIN5_CEIL:.4f})", flush=True)
    print(f"  min11  (10 MIN T=0.7 props + 1 vf):{MIN10_F1:.4f}", flush=True)
    print(f"  dividend (min6 - anchor): {MIN5_F1 - best['f1']:+.4f}",
          flush=True)

    OUT_JSON.write_text(json.dumps({
        "scope": "GS 384px / 487 tiles / curator GT / 20 m",
        "cell": "zero-diversity anchor: 1x minimal-thinking T=0.0 text "
                "proposer + n=1 carry-forward adversarial-text verifier",
        "proposer": {
            "model": "gemini-3-flash",
            "config": "detect_brief-text",
            "thinking_level": "minimal",
            "temperature": 0.0,
            "passes": 1,
            "tile_scope": "487 tiles (486 completed, 1 failed: "
                          "K-35-052-4_32635_x0_y2352.png)",
            "detections_geojson": "outputs/h11/pv-diag-384/text-baseline/"
                                  "text-t0.0/run_1/detections_text-t0.0_run01.geojson",
        },
        "verifier": {
            "model": "gemini-3-flash",
            "config": "verify_adversarial-text",
            "thinking_level": "minimal",
            "temperature": 0.0,
            "iterations": 1,
            "probabilities": "outputs/h11/pv-diag-384/verified/text-baseline/"
                             "probabilities.json",
        },
        "candidate_manifest": "outputs/h11/pv-diag-384/crops/text-baseline/"
                              "candidate_manifest.json",
        "pool": {"n": len(table), "recall_ceiling_20m": round(ceil, 4),
                 "f1_max_at_ceiling": round(f1max, 4)},
        "sweep": sweep_rows,
        "best": {"prob_t": best["pt"], "f1_20m": round(best["f1"], 4),
                 "mcc": round(best["mcc"], 4) if best["mcc"] is not None else None,
                 "precision": round(best["precision"], 4),
                 "recall": round(best["recall"], 4),
                 "n_accepted": best["n"],
                 "geojson": str(gj.relative_to(BASE_DIR))},
        "comparison": {
            "min6_5pass_t07_f1": MIN5_F1, "min6_pool_ceiling": MIN5_CEIL,
            "min11_10pass_t07_f1": MIN10_F1,
            "diversity_dividend_min6_minus_anchor":
                round(MIN5_F1 - best["f1"], 4),
        },
    }, indent=2) + "\n")
    print(f"\nWrote {OUT_JSON.relative_to(BASE_DIR)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
