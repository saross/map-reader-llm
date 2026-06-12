#!/usr/bin/env python3
# ============================================================================
# build_pareto_v2.py
# ----------------------------------------------------------------------------
# Session 112 ($0): Pareto v2 — the cost-weighted frontier (Shawn, S111:
# "high thinking isn't really 'cheap6'"). Supersedes the passes-axis board
# (results/verifier-robustness/pareto/, kept as the v1 record) with:
#   - proposer-centric rung names (cheap6 -> high6);
#   - the minimal-thinking rungs min6 (TRUE make-up cell) and min11;
#   - an ESTIMATED FLEX-COST axis;
#   - a refreshed C(7,2)=21 round-robin + BH-FDR + greedy-clique tiers.
#
# COST MODEL (token-load audit, 2026-06-12 — see
# reports/token-load-audit-2026-06-12.md; supersedes the 2026-06-11
# manifest-derived calibration, which was built on a 2x double-counted
# cost manifest and a "3x minimal" HIGH extrapolation):
#   - F3 verifier call: $0.000693 measured (opmax run per-meta recompute:
#     $2.5257 / 3,645 calls; deployment verifiers 0.000684-0.000698).
#   - F3 MINIMAL proposer pass: $0.266 at GS scale — ten measured 55-map
#     minimal passes (1,502 in + ~114 out tokens/tile, zero thinking,
#     flex $4.66/8,541-tile pass) scaled by 487/8541.
#   - F3 HIGH proposer pass: $2.29 at GS scale — five measured 55-map
#     T0.7 HIGH passes (adds ~2,693 thinking tokens/tile billed at the
#     $1.50/M output rate => flex $40.19/8,541-tile pass) scaled by
#     487/8541; inside the GS-measured bracket [T1.0 $2.15, T0.3 $2.64].
#     True min:HIGH ratio is 8.6x, not the previous 3x.
#   - Verifier leg cost scales with the pool's CROP COUNT (per-rung below).
#
# Usage (zbook):  .venv/bin/python scripts/build_pareto_v2.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
from scripts.analyse_verifier_robustness import GROUND_TRUTH  # noqa: E402
from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.consensus_vs_baseline_tiering import consensus_per_tile  # noqa: E402
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    greedy_clique_tiers,
    permutation_test_float,
)

BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUT_DIR = BASE_DIR / "results/verifier-robustness/pareto"
MIN_PASS_USD = 0.266  # ten measured 55-map minimal passes, scaled by 487/8541 (audit 2026-06-12)
HIGH_PASS_USD = 2.29  # five measured 55-map T0.7 HIGH passes incl. thinking tokens, scaled
VF_CALL_USD = 0.000693
# 55-map production scaling (Shawn, 2026-06-11): the real-world costing is a
# deployment over the 8,541-tile generalisation corpus. Both cost components
# scale with the tile factor (proposer passes by tiles; verifier crops by
# candidate density x tiles), so the frontier SHAPE is unchanged — only the
# dollar axis scales. Crops/tile is taken from the GS pools; the 55-map
# corpus is sparser (0.60 GT mounds/tile vs 0.89 on GS), so these are
# slightly conservative (upper-bound) estimates. Flex pricing == batch
# pricing on Gemini 3 (both 50% of standard), so the figures hold for
# either execution mode.
TILES_GS = 487
TILES_55 = 8541
SCALE_55 = TILES_55 / TILES_GS

# (rung, F1@20m record, geojson, proposer passes x cost, verifier crops x N)
RUNGS = [
    ("min6", 0.8784,
     "results/verifier-robustness/min-thinking-sets/text-min-t07-TRUE-5pass-3of5-n1-pt0.15.geojson",
     5, MIN_PASS_USD, 1586, 1),
    ("min11", 0.8835,
     "results/verifier-robustness/min-thinking-sets/text-min-t07-10pass-6of10-n1-pt0.2.geojson",
     10, MIN_PASS_USD, 1939, 1),
    ("high6", 0.8641,
     "results/verifier-robustness/pareto/cheap6-4of5-n1-pt0.15.geojson",
     5, HIGH_PASS_USD, 3736, 1),
    ("high5+5vf", 0.8739,
     "results/verifier-robustness/matrix-sets/min-T0.3.geojson",
     5, HIGH_PASS_USD, 855, 5),
    ("high11", 0.8769,
     "results/verifier-robustness/pareto/nof10-6of10-n1-pt0.2.geojson",
     10, HIGH_PASS_USD, 5866, 1),
    ("high31", 0.8902,
     "outputs/era1-pv-stage-d/384-consensus-text-high/pass_1/accepted_t0.2.geojson",
     30, HIGH_PASS_USD, 729, 1),
    ("high35", 0.8951,
     "results/verifier-robustness/opmax-sets/opmax-16of30-N5minT0.3-vt3-pt0.15.geojson",
     30, HIGH_PASS_USD, 729, 5),
]


def main() -> int:
    """Score, tier, and plot the cost-weighted frontier."""
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)
    tile_order = sorted(gdf_bounds["tile_name"].tolist())

    cells = []
    print("=== rungs (gates vs committed records) ===", flush=True)
    for name, expect, gj, np_, ppc, crops, nvf in RUNGS:
        tp, fp, fn = consensus_per_tile(Path(gj), gdf_ref, gdf_bounds, tile_order)
        f1 = (2 * tp.sum()) / (2 * tp.sum() + fp.sum() + fn.sum())
        if abs(f1 - expect) > 0.0005:
            sys.exit(f"GATE FAIL {name}: board F1 {f1:.4f} vs record {expect}")
        cost = np_ * ppc + crops * nvf * VF_CALL_USD
        cost_55 = cost * SCALE_55
        cells.append({"rung": name, "f1": round(float(f1), 4),
                      "passes": np_ + nvf, "est_cost_usd": round(cost, 2),
                      "est_cost_55map_usd": round(cost_55, 2),
                      "proposer": f"{np_}x{'MIN' if ppc == MIN_PASS_USD else 'HIGH'}",
                      "verifier": f"n={nvf} over {crops} crops",
                      "tp": tp, "fp": fp, "fn": fn})
        print(f"  {name:<10} F1={f1:.4f} (record {expect})  GS ${cost:.2f}  "
              f"55-map production ~${cost_55:.0f}", flush=True)

    print("\n=== round-robin (21 pairs, 10k, seed 42) ===", flush=True)
    pairs, significant = [], {}
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            a, b = cells[i], cells[j]
            r = permutation_test_float(a["tp"], a["fp"], a["fn"],
                                       b["tp"], b["fp"], b["fn"],
                                       n_permutations=10000, seed=42)
            pairs.append({"a": a["rung"], "b": b["rung"], **r})
    adjusted = apply_bh_correction([p["p_value"] for p in pairs], q=0.05)
    for p, adj in zip(pairs, adjusted):
        p["bh_adjusted_p"] = round(adj, 6)
        p["significant"] = bool(adj < 0.05)
        significant[frozenset({p["a"], p["b"]})] = p["significant"]
    ordered = sorted(cells, key=lambda c: -c["f1"])
    tiers = greedy_clique_tiers([c["rung"] for c in ordered], significant)
    tier_of = {r: t for t, members in enumerate(tiers, 1) for r in members}
    n_sig = sum(1 for p in pairs if p["significant"])
    print(f"{n_sig}/21 significant -> {len(tiers)} tier(s): {tiers}", flush=True)

    # Pareto-efficient set on (cost, F1): no other rung is cheaper AND better.
    eff = [c["rung"] for c in cells
           if not any(o["est_cost_usd"] <= c["est_cost_usd"] and o["f1"] > c["f1"]
                      for o in cells if o is not c)]

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 5.5))
    front = sorted([c for c in cells if c["rung"] in eff],
                   key=lambda c: c["est_cost_usd"])
    ax.plot([c["est_cost_usd"] for c in front], [c["f1"] for c in front],
            "-", color="#1f77b4", lw=1.2, zorder=2, label="Pareto frontier")
    for c in cells:
        on = c["rung"] in eff
        ax.scatter([c["est_cost_usd"]], [c["f1"]], s=60, zorder=3,
                   color="#1f77b4" if on else "#aaaaaa")
        ax.annotate(f"{c['rung']} (T{tier_of[c['rung']]})\n{c['f1']:.4f}",
                    (c["est_cost_usd"], c["f1"]), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=8,
                    color="black" if on else "#777777")
    ax.set_xscale("log")
    ax.set_xlabel("estimated cost per full run (flex USD, log scale)")
    ax.set_ylabel("F1@20 m (best operating point)")
    ax.set_title("Cost-weighted Pareto frontier — GS 384 px proposer-verifier")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "pareto_v2.png", dpi=150)

    (OUT_DIR / "pareto_v2.json").write_text(json.dumps({
        "cost_model": {"min_pass_usd": MIN_PASS_USD, "high_pass_usd": HIGH_PASS_USD,
                       "vf_call_usd": VF_CALL_USD,
                       "production_scale": {"tiles_gs": TILES_GS, "tiles_55map": TILES_55,
                                            "factor": round(SCALE_55, 2),
                                            "note": "crops/tile from GS pools; 55-map "
                                                    "corpus sparser -> slight upper bound; "
                                                    "flex == batch pricing on Gemini 3"},
                       "basis": "token-load audit 2026-06-12 "
                                "(reports/token-load-audit-2026-06-12.md): all three "
                                "rates measured from per-item metadata at F3 flex "
                                "rates with thinking billed at the output rate; "
                                "MIN/HIGH from the 55-map deployment passes scaled "
                                "by 487/8541 (replaces the manifest-derived MIN, "
                                "which was 2x double-counted, and the 'HIGH = 3x "
                                "minimal' extrapolation, which under-priced "
                                "proposer thinking 1.4x)"},
        "tiers": tiers, "pareto_efficient": eff,
        "rungs": [{k: v for k, v in c.items() if k not in ("tp", "fp", "fn")}
                  | {"tier": tier_of[c["rung"]]} for c in ordered],
        "pairwise": pairs}, indent=2) + "\n")
    print(f"Pareto-efficient set: {eff}", flush=True)
    print(f"Wrote {OUT_DIR.relative_to(BASE_DIR)}/pareto_v2.{{json,png}}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
