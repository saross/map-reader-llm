#!/usr/bin/env python3
# ============================================================================
# permute_flash35_pairs.py
# ----------------------------------------------------------------------------
# Session 113 ($0): the significance tests the Flash 3.5 2x2x2 dossier left
# "pending (morning, $0)" (reports/session-111-discoveries.md § 11). Three
# targeted paired tile-swap permutations on the GS 384/487 instrument,
# F1@20m, curator GT — one per model-role claim in findings § 14:
#
#   proposer-role:     f35prop-f3vf  (0.8480) vs min11        (0.8835)
#                      (same F3 carry-forward verifier; pools differ)
#   verifier-on-F35:   f35prop-f35vf (0.8362) vs f35prop-f3vf (0.8480)
#   verifier-on-F3:    f3prop-f35vf  (0.8689) vs min11        (0.8835)
#
# (The bare-proposer pair, 0.6196 vs 0.6204, is a numerical dead tie and the
# F3 bare 10of10 comparator set is not materialised — left untested.)
#
# GATES: each set's feature count + micro-F1@20m must reproduce its committed
# evaluation (results/flash35-2x2/evals/, results/flash35-2x2/evals/min11)
# before any test runs. Machinery: consensus_per_tile (Hungarian per map,
# 20 m) + permutation_test_float (10k, seed 42, two-sided) — identical to
# permutation_opmax_vs_headline.py.
#
# Usage (sapphire):  .venv/bin/python scripts/permute_flash35_pairs.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))  # consensus_vs_baseline uses bare imports
from scripts.analyse_verifier_robustness import GROUND_TRUTH  # noqa: E402
from scripts.consensus_vs_baseline_tiering import consensus_per_tile  # noqa: E402
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    micro_f1,
    permutation_test_float,
)

F35 = BASE_DIR / "results" / "flash35-2x2"
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUT_JSON = F35 / "flash35_permutations.json"
N_PERMUTATIONS = 10000
SEED = 42

# label -> (detections geojson, evaluation.json with the committed F1@20m)
CELLS = {
    "f35prop-f3vf": (F35 / "best-op-sets/f35prop-f3vf-n10-4of10-pt0.15.geojson",
                     F35 / "evals/f35prop-f3vf-n10-4of10-pt0.15/evaluation.json"),
    "f35prop-f35vf": (F35 / "best-op-sets/f35prop-f35vf-n10-4of10-pt0.25.geojson",
                      F35 / "evals/f35prop-f35vf-n10-4of10-pt0.25/evaluation.json"),
    "f3prop-f35vf": (F35 / "best-op-sets/f3prop-f35vf-n10-6of10-pt0.25.geojson",
                     F35 / "evals/f3prop-f35vf-n10-6of10-pt0.25/evaluation.json"),
    "min11": (BASE_DIR / "results/verifier-robustness/min-thinking-sets/"
                         "text-min-t07-10pass-6of10-n1-pt0.2.geojson",
              F35 / "evals/min11/evaluation.json"),
}

# (question, cell A, cell B)
PAIRS = [
    ("proposer-role: F3.5 pool vs F3 pool under the same F3 verifier",
     "f35prop-f3vf", "min11"),
    ("verifier-role on the F3.5 pool: F3.5 verifier vs F3 verifier",
     "f35prop-f35vf", "f35prop-f3vf"),
    ("verifier-role on the F3 pool: F3.5 verifier vs F3 verifier",
     "f3prop-f35vf", "min11"),
]


def main() -> int:
    """Gate each set against its committed eval, then run the three pairs."""
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)
    tile_order = sorted(gdf_bounds["tile_name"].tolist())

    print("=== gates (feature count + micro-F1@20m vs committed evals) ===",
          flush=True)
    per_tile = {}
    for label, (det, ev_path) in CELLS.items():
        summary = json.loads(ev_path.read_text())["summary"]
        b20 = next(b for b in summary["buffers"] if b["buffer_metres"] == 20)
        n_feat = len(json.loads(det.read_text())["features"])
        if n_feat != summary["n_detections"]:
            sys.exit(f"GATE FAIL {label}: geojson n={n_feat} != eval "
                     f"n_detections {summary['n_detections']}")
        tp, fp, fn = consensus_per_tile(det, gdf_ref, gdf_bounds, tile_order)
        f1 = micro_f1(tp.sum(), fp.sum(), fn.sum())
        if abs(f1 - b20["f1"]) > 0.003:
            sys.exit(f"GATE FAIL {label}: per-tile micro-F1 {f1:.4f} != "
                     f"eval {b20['f1']:.4f}")
        per_tile[label] = (tp, fp, fn)
        print(f"  {label:<14} n={n_feat}  F1@20m={f1:.4f} (eval {b20['f1']:.4f}) ok",
              flush=True)

    print(f"\n=== tile-swap permutations ({N_PERMUTATIONS}, seed {SEED}, "
          f"two-sided) ===", flush=True)
    results = []
    for question, a, b in PAIRS:
        r = permutation_test_float(*per_tile[a], *per_tile[b],
                                   n_permutations=N_PERMUTATIONS, seed=SEED)
        results.append({"question": question, "a": a, "b": b, **r})
        print(f"  {a} vs {b}: {r['f1_a']:.4f} vs {r['f1_b']:.4f}  "
              f"diff={r['observed_diff']:+.4f}  p={r['p_value']:.4f}", flush=True)

    OUT_JSON.write_text(json.dumps({
        "method": "float tile-swap micro-F1 permutation (permutation_test_float), "
                  "Hungarian per map at 20 m, curator GT, 487 tiles",
        "n_permutations": N_PERMUTATIONS, "seed": SEED,
        "pairs": results}, indent=2, default=float) + "\n")
    print(f"\nWrote {OUT_JSON.relative_to(BASE_DIR)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
