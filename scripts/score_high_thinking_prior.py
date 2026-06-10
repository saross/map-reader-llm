#!/usr/bin/env python3
# ============================================================================
# score_high_thinking_prior.py
# ----------------------------------------------------------------------------
# Session 110 ($0, free prior): the verifier-robustness THINKING axis at T=0.0.
#
# Three verifier pools on disk differ ONLY in thinking_level (model
# gemini-3-flash, verify_adversarial.md, T=0.0, text-only, examples=0 all held):
#   minimal -> the Stage-1 carry-forward union (N=5; we read its single passes
#              AND its consensus)
#   medium  -> outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-1of5 (n=1)
#   high    -> outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-1of5    (n=1)
#
# Each pool is self-contained (its own candidate_manifest.json carries geometry +
# vote_count; its probabilities.json carries the verifier probs), so we score
# each INDEPENDENTLY at the >=3-of-5 band per proposer level — no cross-pool
# join. Comparison is at the F1 level (aggregate), which needs no candidate
# alignment between pools.
#
# Fair thinking comparison is at the SAME n: minimal-n1 vs medium-n1 vs high-n1
# (all a single verifier pass). minimal's best CONSENSUS (5-pass) is reported
# alongside as the production reference. The medium/high pools are n=1, so a
# higher-thinking CONSENSUS would be a separate (cheap) gated run — warranted
# only if a single higher-thinking pass already beats minimal.
#
# Usage:  python scripts/score_high_thinking_prior.py
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-06-10
# Licence: Apache 2.0
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

VERIFIED = BASE_DIR / "outputs/h11/pv-diag-384/verified"
POOLS = {
    "minimal": (BASE_DIR / "outputs/verifier-robustness/384-flash-high-text-1of5-union/crops/candidate_manifest.json",
                BASE_DIR / "outputs/verifier-robustness/384-flash-high-text-1of5-union/T0.0/verified/probabilities.json",
                5),
    "medium": (VERIFIED / "flash-high-text-medium-vf-1of5/candidate_manifest.json",
               VERIFIED / "flash-high-text-medium-vf-1of5/probabilities.json", 1),
    "high": (VERIFIED / "flash-high-text-high-vf-1of5/candidate_manifest.json",
             VERIFIED / "flash-high-text-high-vf-1of5/probabilities.json", 1),
}
BOUNDS_384 = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]


def main() -> int:
    """Score each thinking level per proposer level and tabulate."""
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS_384)

    def score(table, by_cid, pk, rule, pt):
        cids = accepted_cids(table, pk, rule, pt)
        if not cids:
            return 0.0
        sel = [by_cid[c] for c in cids]
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
        return score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                                   compute_mcc=False)["f1"]

    # Per (thinking level, proposer_k): best single-pass F1 and (minimal only)
    # best consensus F1, each over the prob_t sweep.
    rows = {}
    for level, (mpath, ppath, n_iter) in POOLS.items():
        table = load_candidate_table(mpath, ppath)
        by_cid = {r["cid"]: r for r in table}
        print(f"{level}: {len(table)} candidates, n_iter={n_iter}", flush=True)
        for pk in (3, 4, 5):
            n1 = max(score(table, by_cid, pk, "iter1", pt) for pt in PROB_TS)
            cons = None
            if n_iter > 1:
                cons = max(score(table, by_cid, pk, f"consensus_vt{v}", pt)
                           for v in range(1, n_iter + 1) for pt in PROB_TS)
            rows[(level, pk)] = (n1, cons)

    print("\n=== THINKING axis at T=0.0 (>=3of5 band, best F1@20m over prob_t) ===",
          flush=True)
    print(f"{'proposer':<10}{'minimal_n1':>12}{'medium_n1':>11}{'high_n1':>10}"
          f"{'minimal_cons':>14}", flush=True)
    for pk in (3, 4, 5):
        mn1 = rows[("minimal", pk)][0]
        med = rows[("medium", pk)][0]
        hi = rows[("high", pk)][0]
        mcons = rows[("minimal", pk)][1]
        print(f"{str(pk)+'of5':<10}{mn1:>12.4f}{med:>11.4f}{hi:>10.4f}{mcons:>14.4f}",
              flush=True)
    print("\n(n=1 columns are a single verifier pass — fair thinking comparison; "
          "minimal_cons is the 5-pass consensus production reference.)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
