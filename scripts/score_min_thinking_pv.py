#!/usr/bin/env python3
# ============================================================================
# score_min_thinking_pv.py
# ----------------------------------------------------------------------------
# Session 111 ($0): score the MINIMAL-thinking n-of-5 / n-of-10 proposer +
# n=1 carry-forward verifier variants — the "min6" / "min11" rungs Shawn
# asked for when re-casting the Pareto frontier in COST rather than passes
# (a HIGH-thinking proposer pass costs ~3x a minimal one, so the previous
# "cheap6" rung — HIGH proposer — is not actually the cheap end in dollars).
#
# Pools (all on disk, all verified with the carry-forward gemini-3-flash
# adversarial-text minimal T=0.0 n=1 verifier; lineage verified from
# run.meta: gemini-3-flash, MINIMAL thinking, T=0.7, detect_brief-text.md —
# identical to the flash-high lineage except thinking level):
#   text-1of5            5-pass minimal union  (probs keyed by feature index)
#   text-1of10           10-pass minimal union (probs keyed by feature index)
#   flash-minimal-text-t07-1of5   first-5 of the n30 minimal study
#                                 (own candidate_manifest)
#
# Sweeps proposer k x prob_t (rule "mean": n=1 -> that iteration's prob),
# reports best F1@20m + MCC per pool, and writes each pool's best-op
# detection set to results/verifier-robustness/min-thinking-sets/ for the
# cost-weighted Pareto refresh.
#
# COST: $0 (on-disk re-score). Run on zbook per the project compute rule.
#
# Usage:
#   .venv/bin/python scripts/score_min_thinking_pv.py
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

VERIFIED = BASE_DIR / "outputs" / "h11" / "pv-diag-384" / "verified"
CONSENSUS = BASE_DIR / "outputs" / "h11" / "pv-diag-384" / "consensus"
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUT_DIR = BASE_DIR / "results" / "verifier-robustness" / "min-thinking-sets"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]

# Reference points for the comparison print-out (committed records).
HIGH6 = 0.8641   # flash-HIGH 5-prop + n=1 vf (4of5/pt0.15) — pareto "cheap6"
HIGH11 = 0.8769  # flash-HIGH 10-prop + n=1 vf (6of10/pt0.2)


def index_table(union_gj: Path, probs_path: Path) -> list[dict]:
    """Join verifier probs to a union geojson by feature index.

    Mirrors score_pro_pv.py: probabilities are keyed candidate_{i:05d}
    contiguously over the union's features (geometry EPSG:32635,
    properties.vote_count = proposer vote).
    """
    fc = json.loads(union_gj.read_text())
    results = json.loads(probs_path.read_text())["results"]
    table = []
    for i, f in enumerate(fc["features"]):
        val = results.get(f"candidate_{i:05d}")
        if not isinstance(val, dict):
            continue
        p = val.get("mound_probability")
        if not isinstance(p, (int, float)):
            continue
        x, y = f["geometry"]["coordinates"][:2]
        table.append({"cid": i, "x": float(x), "y": float(y),
                      "vote_count": int(f["properties"].get("vote_count", 0)),
                      "source_tile": f["properties"].get("source_tile", ""),
                      "iter_probs": [float(p)]})
    n_feat = len(fc["features"])
    if len(table) < n_feat:
        print(f"  NOTE: {n_feat - len(table)}/{n_feat} features lack a "
              f"verifier probability (join by index)", flush=True)
    return table


def sweep(label: str, table: list[dict], gdf_ref, gdf_bounds) -> dict:
    """Best k-of-N x prob_t (rule mean, n=1) with MCC; write the best-op set."""
    by_cid = {r["cid"]: r for r in table}
    max_pk = max(r["vote_count"] for r in table)
    print(f"\n=== {label}: {len(table)} candidates, proposer votes 1..{max_pk} ===",
          flush=True)
    best = {"f1": -1.0}
    for pk in range(1, max_pk + 1):
        bpk = {"f1": -1.0}
        for pt in PROB_TS:
            cids = accepted_cids(table, pk, "mean", pt)
            if not cids:
                continue
            sel = [by_cid[c] for c in sorted(cids)]
            gdf = gpd.GeoDataFrame(
                {"geometry": [Point(r["x"], r["y"]) for r in sel],
                 "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
            res = score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                                      compute_mcc=True)
            if res["f1"] > bpk["f1"]:
                bpk = {"f1": res["f1"], "mcc": res["mcc"], "pt": pt,
                       "cids": cids, "gdf": gdf}
        mcc = f"{bpk['mcc']:.3f}" if bpk.get("mcc") is not None else "NA"
        print(f"  {pk}of{max_pk}: bestF1={bpk['f1']:.4f}  MCC={mcc}  "
              f"prob_t={bpk.get('pt')}", flush=True)
        if bpk["f1"] > best["f1"]:
            best = {**bpk, "pk": pk, "max_pk": max_pk}

    gj = OUT_DIR / f"{label}-{best['pk']}of{best['max_pk']}-n1-pt{best['pt']}.geojson"
    best["gdf"].to_crs("EPSG:4326").to_file(gj, driver="GeoJSON")
    print(f"  >>> BEST {label}: F1@20m={best['f1']:.4f} MCC={best['mcc']:.3f} at "
          f"{best['pk']}of{best['max_pk']}, pt{best['pt']} "
          f"(n={len(best['cids'])}) -> {gj.relative_to(BASE_DIR)}", flush=True)
    return best


def main() -> int:
    """Score the three minimal-thinking PV pools and print the comparison."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)

    results = {}
    results["min5"] = sweep(
        "text-min-t07-5pass",
        index_table(CONSENSUS / "text-1of5.geojson",
                    VERIFIED / "text-1of5" / "probabilities.json"),
        gdf_ref, gdf_bounds)
    results["min10"] = sweep(
        "text-min-t07-10pass",
        index_table(CONSENSUS / "text-1of10.geojson",
                    VERIFIED / "text-1of10" / "probabilities.json"),
        gdf_ref, gdf_bounds)
    results["min5-n30lineage"] = sweep(
        "text-min-t07-5pass-n30lineage",
        load_candidate_table(
            VERIFIED / "flash-minimal-text-t07-1of5" / "candidate_manifest.json",
            VERIFIED / "flash-minimal-text-t07-1of5" / "probabilities.json"),
        gdf_ref, gdf_bounds)

    print("\n=== comparison (F1@20m, GS 384/487, curator GT) ===", flush=True)
    print(f"  min6  (5 MIN prop + 1 vf):  {results['min5']['f1']:.4f}  "
          f"(n30-lineage replicate {results['min5-n30lineage']['f1']:.4f})", flush=True)
    print(f"  high6 (5 HIGH prop + 1 vf): {HIGH6:.4f}  <- pareto 'cheap6'", flush=True)
    print(f"  min11 (10 MIN prop + 1 vf): {results['min10']['f1']:.4f}", flush=True)
    print(f"  high11(10 HIGH prop + 1 vf):{HIGH11:.4f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
