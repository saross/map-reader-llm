#!/usr/bin/env python3
# ============================================================================
# score_high_thinking_prior.py
# ----------------------------------------------------------------------------
# Session 110 ($0, free prior): score the on-disk HIGH-thinking verifier pool to
# answer the verifier-robustness THINKING axis at T=0.0.
#
# The pool outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-high-verifier
# is the 384 flash-high-text 1-of-5 union verified by a verifier IDENTICAL to the
# carry-forward EXCEPT thinking_level: high (vs minimal), T=0.0, n=1 (confirmed
# from run.meta). So scoring it gives a clean minimal-vs-high comparison at n=1.
#
# It carries NO vote_count in its own manifest, so we source the proposer-vote
# from the Stage-1 union manifest (which preserved vote_count) joined by
# candidate_id, guarded by a centroid-alignment assertion (both extractions are
# of the same union geojson, so candidate_id i is the same feature in both).
#
# Scoring reuses the audited point scorer (lib_advanced_metrics.score_detection_set)
# at the >=3-of-5 band, swept over prob_t, per proposer level — directly
# comparable to the Stage-1 minimal-verifier numbers.
#
# Usage:  python scripts/score_high_thinking_prior.py
# Compute: light (zbook; <=14 workers rule N/A — single process).
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-06-10
# Licence: Apache 2.0
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

HIGH_VF = BASE_DIR / "outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-high-verifier"
# Stage-1 union manifest — has candidate_id -> centroid + properties.vote_count.
STAGE1_MANIFEST = (BASE_DIR / "outputs/verifier-robustness/384-flash-high-text-1of5-union"
                   / "crops/candidate_manifest.json")
BOUNDS_384 = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
# Stage-1 minimal-verifier reference (>=3of5 band, T=0.0), from the published grid.
STAGE1_MINIMAL = {  # proposer_k: (best_consensus_F1, single_run_mean_F1 ["n=1"])
    3: (0.8588, 0.8472), 4: (0.8722, 0.8601), 5: (0.8440, 0.8339),
}


def assert_alignment(stage1_manifest: dict, highvf_manifest: dict) -> None:
    """Assert candidate_id i is the same physical candidate in both extractions.

    Both manifests extract the SAME 1-of-5 union geojson, so candidate_id i must
    share a centroid (to ~1 m) across the two. Aborts loudly if not — the
    vote_count join would otherwise be silently wrong.
    """
    s1 = {c["candidate_id"]: (c["centroid_x"], c["centroid_y"])
          for c in stage1_manifest["candidates"]}
    hv = {c["candidate_id"]: (c["centroid_x"], c["centroid_y"])
          for c in highvf_manifest["candidates"]}
    common = sorted(set(s1) & set(hv))
    if not common:
        raise SystemExit("ABORT: no shared candidate_id between the two manifests.")
    mism = [cid for cid in common
            if abs(s1[cid][0] - hv[cid][0]) > 1.0 or abs(s1[cid][1] - hv[cid][1]) > 1.0]
    frac = len(mism) / len(common)
    print(f"alignment: {len(common)} shared ids, {len(mism)} centroid mismatches "
          f"({100 * frac:.2f}%)", flush=True)
    if frac > 0.001:
        raise SystemExit(f"ABORT: {100 * frac:.1f}% of candidate_ids misalign — "
                         f"the vote_count join would be wrong.")


def main() -> int:
    """Score the high-thinking (n=1) verifier per proposer level and compare."""
    stage1_manifest = json.loads(STAGE1_MANIFEST.read_text())
    highvf_manifest = json.loads((HIGH_VF / "candidate_manifest.json").read_text())
    assert_alignment(stage1_manifest, highvf_manifest)

    # Join Stage-1 geometry+vote_count (manifest) with high-thinking probs.
    table = load_candidate_table(STAGE1_MANIFEST, HIGH_VF / "probabilities.json")
    by_cid = {r["cid"]: r for r in table}
    print(f"joined candidates (geometry+vote_count + high-thinking prob): {len(table)}",
          flush=True)

    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS_384)

    def score(cids) -> tuple[float, float | None]:
        if not cids:
            return 0.0, None
        sel = [by_cid[c] for c in cids]
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
        res = score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20, compute_mcc=True)
        return res["f1"], res["mcc"]

    print("\n=== HIGH-thinking verifier (n=1, T=0.0) vs Stage-1 MINIMAL ===", flush=True)
    print(f"{'proposer':<10}{'high_n1_F1':>11}{'high_MCC':>10}{'best_pt':>9}"
          f"{'min_n1_F1':>11}{'min_cons_F1':>13}", flush=True)
    for pk in (3, 4, 5):
        best = {"f1": -1.0}
        for pt in PROB_TS:
            # n=1 -> the single high-thinking pass; "mean" of one value == that value.
            f1, mcc = score(accepted_cids(table, pk, "mean", pt))
            if f1 > best["f1"]:
                best = {"f1": f1, "mcc": mcc, "pt": pt}
        mn1, mcons = STAGE1_MINIMAL[pk][1], STAGE1_MINIMAL[pk][0]
        mcc_s = f"{best['mcc']:.3f}" if best["mcc"] is not None else "NA"
        print(f"{str(pk)+'of5':<10}{best['f1']:>11.4f}{mcc_s:>10}{best['pt']:>9}"
              f"{mn1:>11.4f}{mcons:>13.4f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
