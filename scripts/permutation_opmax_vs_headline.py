#!/usr/bin/env python3
# ============================================================================
# permutation_opmax_vs_headline.py
# ----------------------------------------------------------------------------
# Session 111 ($0): the single targeted pairwise permutation test flagged by
# Shawn in Session 110 — is the operational-maximum lift REAL?
#
#   A (opmax):    16-of-30 flash-high-text proposer + N=5 MINIMAL T=0.3
#                 verifier majority consensus (consensus_vt3, prob_t 0.15,
#                 423 accepted) — F1@20m 0.8951 (results/verifier-robustness/
#                 robustness_summary_T0.3.json, commit 1271b98a3).
#   B (headline): the SAME 16-of-30 proposer pool + the production n=1
#                 carry-forward verifier (T=0.0, minimal, prob_t 0.2,
#                 412 accepted) — the registered project headline
#                 pv-diag-384::verified-adv-text-consensus-16of30,
#                 F1@20m 0.8902 / MCC 0.790.
#
# The +0.005 difference sits at ~1.15x the opmax single-run SD (0.0044), so it
# cannot be pre-judged either way. Decision rule (continuity, S110): if NOT
# significant, the cost rule applies — 30-prop + n=1 verifier (0.890) stays the
# practical ceiling and 0.8951 is a numerical high only; if significant,
# 0.8951 is a genuine new ceiling bought for ~$2.5 of verifier consensus.
#
# Method (project-canonical, reused verbatim from tier_verifier_matrix.py):
# materialise both detection sets, compute per-tile TP/FP/FN (Hungarian per
# map, 20 m, fixed 487-tile order), then the float tile-swap micro-F1
# permutation test (10k, seed 42, two-sided). ONE preregistered pair — no
# multiple-comparison correction applies.
#
# Verification gates (script aborts if either fails):
#   1. opmax set reproduces n_accepted=423 and F1@20m 0.8951 (4 d.p.).
#   2. headline geojson carries 412 features and F1@20m 0.8902 (4 d.p.).
#
# COST: $0 (on-disk re-score). Single process, a few seconds — run on zbook
# per the project compute rule.
#
# Usage:
#   .venv/bin/python scripts/permutation_opmax_vs_headline.py
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
from scripts.consensus_vs_baseline_tiering import consensus_per_tile  # noqa: E402
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import permutation_test_float  # noqa: E402

OPMAX_DIR = BASE_DIR / "outputs" / "verifier-robustness" / "384-flash-high-text-16of30"
OPMAX_MANIFEST = OPMAX_DIR / "crops" / "candidate_manifest.json"
OPMAX_PROBS = OPMAX_DIR / "T0.3" / "verified" / "probabilities.json"
# The opmax best operating point recorded in robustness_summary_T0.3.json.
# proposer_k=1 is equivalent to proposer>=16-of-30: the pool is the
# pre-filtered >=16 subset (vote_count 16..30), so any k<=16 is a no-op.
OPMAX_RULE = "consensus_vt3"
OPMAX_PROB_T = 0.15
OPMAX_EXPECT_N = 423
OPMAX_EXPECT_F1 = 0.8951

HEADLINE_GJ = (BASE_DIR / "outputs" / "era1-pv-stage-d" / "384-consensus-text-high"
               / "pass_1" / "accepted_t0.2.geojson")
HEADLINE_EXPECT_N = 412
HEADLINE_EXPECT_F1 = 0.8902

BOUNDS = BASE_DIR / "inputs" / "vectors" / "bounds" / "384" / "full_evaluation_bounds.geojson"
OUT_DIR = BASE_DIR / "results" / "verifier-robustness" / "opmax-sets"
OUT_JSON = BASE_DIR / "results" / "verifier-robustness" / "opmax_vs_headline_permutation.json"

N_PERMUTATIONS = 10000
SEED = 42


def materialise_opmax(gdf_ref: gpd.GeoDataFrame,
                      gdf_bounds: gpd.GeoDataFrame) -> tuple[Path, dict]:
    """Materialise the opmax accepted set and verify it reproduces the record.

    Args:
        gdf_ref: Ground-truth references (EPSG:32635).
        gdf_bounds: 384 px evaluation tile boundaries (EPSG:32635).

    Returns:
        Tuple of (written geojson path, scoring dict with f1/mcc/n_accepted).

    Raises:
        SystemExit: If the accepted count or F1@20m fails to reproduce the
            values recorded in robustness_summary_T0.3.json.
    """
    table = load_candidate_table(OPMAX_MANIFEST, OPMAX_PROBS)
    by_cid = {r["cid"]: r for r in table}
    cids = accepted_cids(table, 1, OPMAX_RULE, OPMAX_PROB_T)
    sel = [by_cid[c] for c in sorted(cids)]
    gdf = gpd.GeoDataFrame(
        {"geometry": [Point(r["x"], r["y"]) for r in sel],
         "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
    res = score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20, compute_mcc=True)

    if len(cids) != OPMAX_EXPECT_N or round(res["f1"], 4) != OPMAX_EXPECT_F1:
        sys.exit(f"GATE FAIL (opmax): n_accepted={len(cids)} (expect {OPMAX_EXPECT_N}), "
                 f"F1@20m={res['f1']:.4f} (expect {OPMAX_EXPECT_F1})")
    print(f"  gate ok: opmax reproduces n={len(cids)}, F1@20m={res['f1']:.4f}, "
          f"MCC={res['mcc']:.4f}", flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gj = OUT_DIR / "opmax-16of30-N5minT0.3-vt3-pt0.15.geojson"
    gdf.to_crs("EPSG:4326").to_file(gj, driver="GeoJSON")
    return gj, {"f1": res["f1"], "mcc": res["mcc"], "n_accepted": len(cids)}


def verify_headline(gdf_ref: gpd.GeoDataFrame, gdf_bounds: gpd.GeoDataFrame) -> dict:
    """Verify the on-disk headline set reproduces its registered evaluation.

    Args:
        gdf_ref: Ground-truth references (EPSG:32635).
        gdf_bounds: 384 px evaluation tile boundaries (EPSG:32635).

    Returns:
        Scoring dict with f1/mcc/n_detections.

    Raises:
        SystemExit: If the feature count or F1@20m fails to reproduce the
            registered condition (feature-count cross-check rule).
    """
    gdf = gpd.read_file(HEADLINE_GJ)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    gdf = gdf.to_crs(EVAL_CRS)
    res = score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20, compute_mcc=True)

    if len(gdf) != HEADLINE_EXPECT_N or round(res["f1"], 4) != HEADLINE_EXPECT_F1:
        sys.exit(f"GATE FAIL (headline): n={len(gdf)} (expect {HEADLINE_EXPECT_N}), "
                 f"F1@20m={res['f1']:.4f} (expect {HEADLINE_EXPECT_F1})")
    print(f"  gate ok: headline reproduces n={len(gdf)}, F1@20m={res['f1']:.4f}, "
          f"MCC={res['mcc']:.4f}", flush=True)
    return {"f1": res["f1"], "mcc": res["mcc"], "n_detections": len(gdf)}


def main() -> int:
    """Run the opmax-vs-headline paired tile-swap permutation test."""
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)
    tile_order = sorted(gdf_bounds["tile_name"].tolist())

    print("=== verification gates ===", flush=True)
    opmax_gj, opmax_eval = materialise_opmax(gdf_ref, gdf_bounds)
    headline_eval = verify_headline(gdf_ref, gdf_bounds)

    print("\n=== per-tile counts (Hungarian per map, 20 m) ===", flush=True)
    tp_a, fp_a, fn_a = consensus_per_tile(opmax_gj, gdf_ref, gdf_bounds, tile_order)
    tp_b, fp_b, fn_b = consensus_per_tile(HEADLINE_GJ, gdf_ref, gdf_bounds, tile_order)

    print(f"=== tile-swap permutation ({N_PERMUTATIONS}, seed {SEED}, two-sided) ===",
          flush=True)
    res = permutation_test_float(tp_a, fp_a, fn_a, tp_b, fp_b, fn_b,
                                 n_permutations=N_PERMUTATIONS, seed=SEED)

    significant = res["p_value"] < 0.05
    verdict = (
        "SIGNIFICANT - 0.8951 is a genuine new ceiling (16of30 + N=5 verifier, ~$2.5)"
        if significant else
        "NOT significant - cost rule applies: 30-prop + n=1 verifier (0.890) stays the "
        "practical ceiling; 0.8951 is a numerical high only"
    )

    print(f"\n  opmax    (A): F1@20m={res['f1_a']:.4f}  (eval {opmax_eval['f1']:.4f}, "
          f"MCC {opmax_eval['mcc']:.4f}, n={opmax_eval['n_accepted']})", flush=True)
    print(f"  headline (B): F1@20m={res['f1_b']:.4f}  (eval {headline_eval['f1']:.4f}, "
          f"MCC {headline_eval['mcc']:.4f}, n={headline_eval['n_detections']})", flush=True)
    print(f"  observed diff: {res['observed_diff']:+.4f}   p={res['p_value']:.4f}   "
          f"(null SD {res['null_std']:.4f}, {res['n_tiles']} tiles)", flush=True)
    print(f"\n  VERDICT: {verdict}", flush=True)

    OUT_JSON.write_text(json.dumps({
        "question": "is the opmax +0.005 lift over the 0.890 n=1-verifier headline real?",
        "cell_a": {"label": "opmax-16of30-N5minT0.3", "geojson": str(opmax_gj.relative_to(
            BASE_DIR)), "op": f"proposer>=16of30 / {OPMAX_RULE} / pt{OPMAX_PROB_T}",
            **opmax_eval},
        "cell_b": {"label": "headline-16of30-n1T0.0",
                   "geojson": str(HEADLINE_GJ.relative_to(BASE_DIR)),
                   "op": "proposer>=16of30 / n=1 / pt0.2",
                   "condition": "pv-diag-384::verified-adv-text-consensus-16of30",
                   **headline_eval},
        "test": res, "significant_at_0.05": significant, "verdict": verdict,
        "method": "float tile-swap micro-F1 permutation (permutation_test_float), "
                  "single preregistered pair, no FDR correction",
    }, indent=2) + "\n")
    print(f"\nWrote {OUT_JSON.relative_to(BASE_DIR)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
