#!/usr/bin/env python3
# ============================================================================
# tier_verifier_matrix.py
# ----------------------------------------------------------------------------
# Session 110 ($0): round-robin permutation leaderboard of the SIX verifier
# configurations from the thinking x temperature matrix, over the 384px >=3-of-5
# proposer band. Decides which verifier config to apply to other proposer
# outputs — with statistical tiers, not just point F1s.
#
# The six configs (each at its OWN best operating point, best-F1@20m, E56
# in-sample-by-design test-tile characterisation):
#   minimal T0.0 / T0.3 / T0.7   (N=5 consensus)
#   high    T0.0 (n=1 prior) / T0.3 / T0.7   (N=5 consensus; T0.0 is single-pass)
#
# Method (project-canonical, reused verbatim): materialise each config's
# best-operating-point detection set, compute per-tile TP/FP/FN, run the
# C(6,2)=15 round-robin tile-swap micro-F1 permutation tests (10k, seed 42,
# two-sided), BH-FDR at q=0.05, then greedy-clique tiers.
#
# COST: $0 (re-score of on-disk verifier outputs). Permutation sweep is CPU —
# run on zbook (<=14 workers rule N/A, single process).
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
sys.path.insert(0, str(BASE_DIR / "scripts"))  # consensus_vs_baseline uses bare imports
from scripts.analyse_verifier_robustness import (  # noqa: E402
    EVAL_CRS,
    GROUND_TRUTH,
    accepted_cids,
    load_candidate_table,
)
from scripts.consensus_vs_baseline_tiering import consensus_per_tile, run_round_robin  # noqa: E402
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import greedy_clique_tiers  # noqa: E402
from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402

VR = BASE_DIR / "outputs" / "verifier-robustness" / "384-flash-high-text-ge3of5"
UNION = BASE_DIR / "outputs" / "verifier-robustness" / "384-flash-high-text-1of5-union"
HIGHVF = BASE_DIR / "outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-1of5"
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUT_DIR = BASE_DIR / "results" / "verifier-robustness" / "matrix-sets"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]

# (label, manifest, probabilities, n_iter)
CONFIGS = [
    ("min-T0.0", UNION / "crops/candidate_manifest.json", UNION / "T0.0/verified/probabilities.json", 5),
    ("min-T0.3", VR / "crops/candidate_manifest.json", VR / "T0.3/verified/probabilities.json", 5),
    ("min-T0.7", VR / "crops/candidate_manifest.json", VR / "T0.7/verified/probabilities.json", 5),
    ("high-T0.0", HIGHVF / "candidate_manifest.json", HIGHVF / "probabilities.json", 1),
    ("high-T0.3", VR / "crops/candidate_manifest.json", VR / "T0.3-high/verified/probabilities.json", 5),
    ("high-T0.7", VR / "crops/candidate_manifest.json", VR / "T0.7-high/verified/probabilities.json", 5),
]


def best_op(table: list[dict], by_cid: dict, n_iter: int, gdf_ref, gdf_bounds) -> dict:
    """Find the best-F1@20m operating point: reproducible rules for N>1
    (consensus_vt*/mean), single pass for n=1."""
    rules = (["mean"] + [f"consensus_vt{v}" for v in range(1, n_iter + 1)]
             if n_iter > 1 else ["mean"])
    max_pk = max((r["vote_count"] for r in table), default=0)
    best = {"f1": -1.0}
    for pk in range(1, max_pk + 1):
        for rule in rules:
            for pt in PROB_TS:
                cids = accepted_cids(table, pk, rule, pt)
                f1 = _score(cids, by_cid, gdf_ref, gdf_bounds)
                if f1 > best["f1"]:
                    best = {"f1": f1, "pk": pk, "rule": rule, "pt": pt, "cids": cids}
    return best


def _score(cids, by_cid, gdf_ref, gdf_bounds) -> float:
    if not cids:
        return 0.0
    gdf = _gdf(cids, by_cid)
    return score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                               compute_mcc=False)["f1"]


def _gdf(cids, by_cid) -> gpd.GeoDataFrame:
    sel = [by_cid[c] for c in cids]
    return gpd.GeoDataFrame(
        {"geometry": [Point(r["x"], r["y"]) for r in sel],
         "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)


def main() -> int:
    """Materialise the 6 best-op sets, run the round-robin, tier, and report."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)
    tile_order = sorted(gdf_bounds["tile_name"].tolist())

    cells = []
    print("=== materialising best-op detection sets ===", flush=True)
    for label, mpath, ppath, n_iter in CONFIGS:
        table = load_candidate_table(mpath, ppath)
        by_cid = {r["cid"]: r for r in table}
        bo = best_op(table, by_cid, n_iter, gdf_ref, gdf_bounds)
        gj = OUT_DIR / f"{label}.geojson"
        _gdf(bo["cids"], by_cid).to_crs("EPSG:4326").to_file(gj, driver="GeoJSON")
        tp, fp, fn = consensus_per_tile(gj.relative_to(BASE_DIR), gdf_ref, gdf_bounds, tile_order)
        cells.append({"ref": label, "label": label, "tp": tp, "fp": fp, "fn": fn,
                      "eval_f1": bo["f1"], "op": f"{bo['pk']}of5/{bo['rule']}/pt{bo['pt']}"})
        print(f"  {label}: F1@20m={bo['f1']:.4f}  ({bo['pk']}of5, {bo['rule']}, "
              f"pt{bo['pt']}, n_acc={len(bo['cids'])})", flush=True)

    print("\n=== round-robin tile-swap permutation (15 pairs, 10k, seed 42) ===", flush=True)
    pairwise = run_round_robin(cells, n_permutations=10000, seed=42)
    raw_p = [r["p_value"] for r in pairwise]
    adjusted = apply_bh_correction(raw_p, q=0.05)
    significant = {}
    for r, adj in zip(pairwise, adjusted):
        r["bh_adjusted_p"] = round(adj, 6)
        r["significant"] = bool(adj < 0.05)
        significant[frozenset({r["ref_a"], r["ref_b"]})] = r["significant"]

    ordered = sorted(cells, key=lambda c: c["eval_f1"], reverse=True)
    tiers = greedy_clique_tiers([c["ref"] for c in ordered], significant)
    tier_of = {ref: t for t, members in enumerate(tiers, 1) for ref in members}
    n_sig = sum(1 for r in pairwise if r["significant"])

    print(f"\nFDR: {n_sig}/{len(pairwise)} pairs significant at q=0.05 -> {len(tiers)} tier(s)",
          flush=True)
    print(f"\n{'rank':<5}{'config':<12}{'F1@20m':>9}{'tier':>6}  operating point", flush=True)
    for i, c in enumerate(ordered, 1):
        print(f"{i:<5}{c['ref']:<12}{c['eval_f1']:>9.4f}{tier_of[c['ref']]:>6}  {c['op']}", flush=True)

    print("\n=== significant pairs (BH q<0.05) ===", flush=True)
    sigpairs = [r for r in pairwise if r["significant"]]
    if not sigpairs:
        print("  NONE — all six configurations are statistically tied.", flush=True)
    for r in sorted(sigpairs, key=lambda r: r["bh_adjusted_p"]):
        print(f"  {r['ref_a']} vs {r['ref_b']}: diff={r.get('observed_diff', r.get('diff')):+.4f} "
              f"p={r['p_value']:.4f} bh={r['bh_adjusted_p']:.4f}", flush=True)

    (BASE_DIR / "results/verifier-robustness/matrix_tiering.json").write_text(json.dumps(
        {"tiers": tiers, "ranked": [{"ref": c["ref"], "f1": c["eval_f1"],
         "tier": tier_of[c["ref"]], "op": c["op"]} for c in ordered],
         "pairwise": pairwise}, indent=2))
    print("\nWrote results/verifier-robustness/matrix_tiering.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
