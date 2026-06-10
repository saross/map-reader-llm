#!/usr/bin/env python3
# ============================================================================
# materialise_vr_condition_sets.py
# ----------------------------------------------------------------------------
# Session 111 ($0): materialise the five best-operating-point detection sets
# still missing for the verifier-robustness manifest registration (the other
# nine condition sets already exist under matrix-sets/, opmax-sets/, pareto/,
# and the registered headline).
#
#   1. vr-256-union-t0-0-n5     5of5 / mean / pt0.15          -> 0.8637
#   2. vr-256-ge3of5-t0-3-n5    5of5 / consensus_vt2 / pt0.2  -> 0.8582
#   3. medium-vf-4of5           4of5 / n=1 / best prob_t      -> 0.8545
#   4. pro-flash-vf-3of5        3of5 / n=1 / pt0.15           -> 0.8491
#   5. pro-pro-vf-3of5          3of5 / n=1 / pt0.15           -> 0.8506
#
# Each set is scored in-process and GATED against the recorded F1@20 m
# (4 d.p.; sources: robustness_summary_T0.0.json, robustness_summary_T0.3.json,
# high_thinking_prior.log, pro_pv.log) before the geojson is written to
# results/verifier-robustness/condition-sets/. The Pro pools join the
# probabilities to the union geojson by feature index, exactly mirroring
# scripts/score_pro_pv.py.
#
# COST: $0 (on-disk re-score). Run on zbook per the project compute rule.
#
# Usage:
#   .venv/bin/python scripts/materialise_vr_condition_sets.py
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
    BOUNDS_BY_SIZE,
    EVAL_CRS,
    GROUND_TRUTH,
    accepted_cids,
    load_candidate_table,
)
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402

VR = BASE_DIR / "outputs" / "verifier-robustness"
VERIFIED = BASE_DIR / "outputs" / "h11" / "pv-diag-384" / "verified"
PRO_UNION = BASE_DIR / "outputs/h11/pv-diag-384/consensus/pro-high-text-1of5.geojson"
OUT_DIR = BASE_DIR / "results" / "verifier-robustness" / "condition-sets"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]

# (out name, tile size, manifest, probabilities, proposer_k, rule, prob_t or
#  None to sweep, expected F1@20m). prob_t=None sweeps PROB_TS and keeps the
#  best — used for the medium-vf cell whose committed log records only the
#  band-best F1, not the prob_t.
CELLS = [
    ("vr-256-union-t0-0-n5", 256,
     VR / "256-text-1of5-union/crops/candidate_manifest.json",
     VR / "256-text-1of5-union/T0.0/verified/probabilities.json",
     5, "mean", 0.15, 0.8637),
    ("vr-256-ge3of5-t0-3-n5", 256,
     VR / "256-text-ge3of5/crops/candidate_manifest.json",
     VR / "256-text-ge3of5/T0.3/verified/probabilities.json",
     5, "consensus_vt2", 0.2, 0.8582),
    ("medium-vf-4of5", 384,
     VERIFIED / "flash-high-text-medium-vf-1of5/candidate_manifest.json",
     VERIFIED / "flash-high-text-medium-vf-1of5/probabilities.json",
     4, "mean", None, 0.8545),
]
PRO_CELLS = [
    ("pro-flash-vf-3of5",
     VERIFIED / "pro-high-text-1of5-flash-minimal-verifier/probabilities.json",
     3, 0.15, 0.8491),
    ("pro-pro-vf-3of5",
     VERIFIED / "pro-high-text-1of5-pro-verifier/probabilities.json",
     3, 0.15, 0.8506),
]


def pro_table(probs_path: Path) -> list[dict]:
    """Join Pro verifier probabilities to the union geojson by feature index.

    Mirrors scripts/score_pro_pv.py: probabilities are keyed
    candidate_{i:05d} contiguously over the union's 504 features, whose
    properties carry the proposer vote_count and whose coordinates are
    already EPSG:32635.
    """
    fc = json.loads(PRO_UNION.read_text())
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
    return table


def score_and_write(name: str, table: list[dict], pk: int, rule: str,
                    prob_t: float | None, expect: float,
                    gdf_ref, gdf_bounds) -> None:
    """Apply the operating point, gate against the record, write the geojson."""
    by_cid = {r["cid"]: r for r in table}

    def f1_of(pt):
        cids = accepted_cids(table, pk, rule, pt)
        if not cids:
            return -1.0, cids
        sel = [by_cid[c] for c in sorted(cids)]
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
        return score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                                   compute_mcc=False)["f1"], cids

    if prob_t is None:
        best = max((f1_of(pt) + (pt,) for pt in PROB_TS), key=lambda t: t[0])
        f1, cids, prob_t = best
    else:
        f1, cids = f1_of(prob_t)

    if round(f1, 4) != expect:
        sys.exit(f"GATE FAIL ({name}): F1@20m={f1:.4f}, expected {expect}")

    sel = [by_cid[c] for c in sorted(cids)]
    gj = OUT_DIR / f"{name}.geojson"
    gpd.GeoDataFrame(
        {"geometry": [Point(r["x"], r["y"]) for r in sel],
         "source_tile": [r["source_tile"] for r in sel]},
        crs=EVAL_CRS).to_crs("EPSG:4326").to_file(gj, driver="GeoJSON")
    print(f"  gate ok: {name} F1@20m={f1:.4f} (pk{pk}/{rule}/pt{prob_t}, "
          f"n={len(cids)}) -> {gj.relative_to(BASE_DIR)}", flush=True)


def main() -> int:
    """Materialise and gate the five missing condition sets."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf_ref = load_geojson(GROUND_TRUTH)
    bounds = {size: load_geojson(BOUNDS_BY_SIZE[size]) for size in (256, 384)}

    for name, size, mpath, ppath, pk, rule, pt, expect in CELLS:
        table = load_candidate_table(mpath, ppath)
        score_and_write(name, table, pk, rule, pt, expect, gdf_ref, bounds[size])

    for name, ppath, pk, pt, expect in PRO_CELLS:
        score_and_write(name, pro_table(ppath), pk, "mean", pt, expect,
                        gdf_ref, bounds[384])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
