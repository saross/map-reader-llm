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
# EXTENDED 2026-09-12 (the PI's ruling that the Pareto gains a tile-MCC
# column, K-ladder § 4.1 campaign): every rung now carries the tile-level
# Matthews Correlation Coefficient (MCC) of its committed evaluation on the
# same Era-2 frame (487 tiles, `full_evaluation_bounds.geojson`) the F1 column
# is scored on, plus a second Pareto frontier computed on (cost, MCC).
#   - Each rung declares the REGISTERED condition it is, and the script gates
#     that its `detections` path in `results/run-conditions.json` is the same
#     geojson this script scores. A rung whose register entry disagrees aborts
#     the build, so the MCC cannot be read off the wrong cell.
#   - The MCC is then read from that condition's own `evaluation.json`
#     (`summary.tile_classification`) and GATED by recomputing the per-tile
#     classification from the same geojson through the house definition
#     (`lib_advanced_metrics.compute_per_tile_classification`): the rebuilt
#     confusion cells must equal the recorded ones exactly.
#   - The C(7,2) round-robin now runs on MCC as well as F1, through
#     `pairwise_permutation_test.permutation_test_mcc_arrays` — the MCC
#     sibling of `permutation_test_float`, drawing the same per-tile swap
#     masks from the same seed — with its own Benjamini-Hochberg family.
#   - MCC is buffer-invariant in this codebase (tile truth is intersection
#     with any reference, tile prediction is any detection assigned to the
#     tile; no matching tolerance enters), so "MCC at 20 m" and "MCC at 50 m"
#     are the same number. The F1 axis remains F1@20 m.
# The cost model, the F1 column and the F1 tiering are untouched.
#
# Usage (sapphire):  .venv/bin/python scripts/build_pareto_v2.py
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
from scripts.lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_classification,
)
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    greedy_clique_tiers,
    permutation_test_float,
)
from scripts.pairwise_permutation_test import (  # noqa: E402
    assign_source_tiles,
    compute_mcc_or_none,
    permutation_test_mcc_arrays,
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

#: The register row this board IS. Its `conditions_compared` list is the
#: single source of truth for which seven cells the Pareto tabulates, and the
#: `cond_ref` on each rung below must be a member of it.
ANALYSIS_ID = "pass-budget-pareto-v2"
RUN_CONDITIONS = BASE_DIR / "results/run-conditions.json"
RUN_ANALYSES = BASE_DIR / "results/run-analyses.json"

# (rung, F1@20m record, geojson, proposer passes x cost, verifier crops x N,
#  registered condition ref)
RUNGS = [
    ("min6", 0.8784,
     "results/verifier-robustness/min-thinking-sets/text-min-t07-TRUE-5pass-3of5-n1-pt0.15.geojson",
     5, MIN_PASS_USD, 1586, 1,
     "pv-diag-384::verified-adv-text-min-true-3of5"),
    ("min11", 0.8835,
     "results/verifier-robustness/min-thinking-sets/text-min-t07-10pass-6of10-n1-pt0.2.geojson",
     10, MIN_PASS_USD, 1939, 1,
     "pv-diag-384::verified-adv-text-min-6of10"),
    ("high6", 0.8641,
     "results/verifier-robustness/pareto/cheap6-4of5-n1-pt0.15.geojson",
     5, HIGH_PASS_USD, 3736, 1,
     "pv-diag-384::verified-adv-text-4of5"),
    ("high5+5vf", 0.8739,
     "results/verifier-robustness/matrix-sets/min-T0.3.geojson",
     5, HIGH_PASS_USD, 855, 5,
     "verifier-robustness::verified-384-ge3of5-t0-3-n5"),
    ("high11", 0.8769,
     "results/verifier-robustness/pareto/nof10-6of10-n1-pt0.2.geojson",
     10, HIGH_PASS_USD, 5866, 1,
     "pv-diag-384::verified-adv-text-6of10"),
    ("high31", 0.8902,
     "outputs/era1-pv-stage-d/384-consensus-text-high/pass_1/accepted_t0.2.geojson",
     30, HIGH_PASS_USD, 729, 1,
     "pv-diag-384::verified-adv-text-consensus-16of30"),
    ("high35", 0.8951,
     "results/verifier-robustness/opmax-sets/opmax-16of30-N5minT0.3-vt3-pt0.15.geojson",
     30, HIGH_PASS_USD, 729, 5,
     "verifier-robustness::verified-384-16of30-t0-3-n5-opmax"),
]


class RegisterGateError(RuntimeError):
    """A rung disagrees with the register, or with its committed evaluation."""


def resolve_registered_cell(cond_ref: str, geojson: str) -> tuple[Path, dict]:
    """Verify a rung against the register and return its evaluation.

    Two hard checks before an MCC is read, so the column cannot be filled from
    the wrong cell:

    1. ``cond_ref`` must be a member of the ``pass-budget-pareto-v2`` row's
       ``conditions_compared`` — the board membership the analysis registers.
    2. The condition's own ``detections`` path must be the geojson this script
       scores for that rung, so the F1 and the MCC describe one detection set.

    Args:
        cond_ref: A ``<run>::<label>`` register reference.
        geojson: The repo-relative geojson this script scores for the rung.

    Returns:
        ``(eval_path, evaluation_json)``.

    Raises:
        RegisterGateError: on either disagreement, or a missing evaluation.
    """
    board = next(a for a in json.loads(RUN_ANALYSES.read_text())["analyses"]
                 if a["analysis_id"] == ANALYSIS_ID)
    if cond_ref not in board["conditions_compared"]:
        raise RegisterGateError(
            f"{cond_ref} is not in {ANALYSIS_ID}.conditions_compared")
    run, label = cond_ref.split("::", 1)
    decomposition = json.loads(RUN_CONDITIONS.read_text())["decomposition"]
    cond = next(c for c in decomposition[run]["conditions"]
                if c["label"] == label)
    if cond.get("detections") != geojson:
        raise RegisterGateError(
            f"{cond_ref}: register detections {cond.get('detections')!r} != "
            f"board geojson {geojson!r}")
    eval_path = BASE_DIR / cond["eval_path"]
    if not eval_path.exists():
        raise RegisterGateError(f"{cond_ref}: {eval_path} not found")
    return eval_path, json.loads(eval_path.read_text())


def rung_tile_classification(geojson: Path, gdf_ref, gdf_bounds,
                             tile_order: list[str], evaluation: dict,
                             rung: str) -> tuple[tuple, dict, float]:
    """Per-tile one-hot classification for one rung, gated against its record.

    Args:
        geojson: The rung's detection set.
        gdf_ref: Ground-truth references.
        gdf_bounds: Evaluation tile boundaries.
        tile_order: Fixed tile order the arrays are aligned to.
        evaluation: The rung's committed ``evaluation.json``.
        rung: Rung name, for the error message.

    Returns:
        ``((tp, tn, fp, fn) arrays, recorded_confusion, mcc_point)``.

    Raises:
        RegisterGateError: if the rebuilt confusion or MCC disagrees with the
            committed ``tile_classification`` block.
    """
    import numpy as np

    gdf_det = assign_source_tiles(load_geojson(geojson), gdf_bounds)
    per_tile = compute_per_tile_classification(gdf_det, gdf_ref, gdf_bounds)
    index = {t: i for i, t in enumerate(tile_order)}
    arrays = {k: np.zeros(len(tile_order), dtype=int)
              for k in ("tp", "tn", "fp", "fn")}
    for _, row in per_tile.iterrows():
        i = index.get(row["tile_name"])
        if i is None:
            continue
        for k in arrays:
            arrays[k][i] = int(row[k])
    rebuilt = {k: int(v.sum()) for k, v in arrays.items()}

    tc = evaluation["summary"].get("tile_classification") or {}
    recorded = tc.get("confusion")
    if not isinstance(recorded, dict):
        raise RegisterGateError(f"{rung}: evaluation records no tile confusion")
    recorded = {k: int(recorded[k]) for k in ("tp", "tn", "fp", "fn")}
    if rebuilt != recorded:
        raise RegisterGateError(
            f"{rung}: rebuilt tile confusion {rebuilt} != recorded {recorded}")
    mcc_block = tc.get("mcc")
    mcc_recorded = (mcc_block.get("point") if isinstance(mcc_block, dict)
                    else mcc_block)
    mcc_rebuilt = compute_mcc_or_none(**rebuilt)
    if mcc_recorded is not None and mcc_rebuilt is not None \
            and abs(float(mcc_rebuilt) - float(mcc_recorded)) > 5e-5:
        raise RegisterGateError(
            f"{rung}: rebuilt MCC {mcc_rebuilt:.6f} != recorded {mcc_recorded}")
    return ((arrays["tp"], arrays["tn"], arrays["fp"], arrays["fn"]),
            recorded, float(mcc_recorded))


def main() -> int:
    """Score, tier, and plot the cost-weighted frontier."""
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)
    tile_order = sorted(gdf_bounds["tile_name"].tolist())

    cells = []
    print("=== rungs (gates vs committed records) ===", flush=True)
    for name, expect, gj, np_, ppc, crops, nvf, cond_ref in RUNGS:
        tp, fp, fn = consensus_per_tile(Path(gj), gdf_ref, gdf_bounds, tile_order)
        f1 = (2 * tp.sum()) / (2 * tp.sum() + fp.sum() + fn.sum())
        if abs(f1 - expect) > 0.0005:
            sys.exit(f"GATE FAIL {name}: board F1 {f1:.4f} vs record {expect}")
        # The MCC column: resolve the rung to its REGISTERED condition, then
        # rebuild its per-tile classification and gate it against that cell's
        # committed tile_classification block.
        eval_path, evaluation = resolve_registered_cell(cond_ref, gj)
        cls, confusion, mcc = rung_tile_classification(
            BASE_DIR / gj, gdf_ref, gdf_bounds, tile_order, evaluation, name)
        cost = np_ * ppc + crops * nvf * VF_CALL_USD
        cost_55 = cost * SCALE_55
        cells.append({"rung": name, "f1": round(float(f1), 4),
                      "mcc": round(float(mcc), 4),
                      "tile_confusion": confusion,
                      "condition_ref": cond_ref,
                      "eval_path": str(eval_path.relative_to(BASE_DIR)),
                      "passes": np_ + nvf, "est_cost_usd": round(cost, 2),
                      "est_cost_55map_usd": round(cost_55, 2),
                      "proposer": f"{np_}x{'MIN' if ppc == MIN_PASS_USD else 'HIGH'}",
                      "verifier": f"n={nvf} over {crops} crops",
                      "tp": tp, "fp": fp, "fn": fn,
                      "tp_c": cls[0], "tn_c": cls[1],
                      "fp_c": cls[2], "fn_c": cls[3]})
        print(f"  {name:<10} F1={f1:.4f} (record {expect})  "
              f"MCC={mcc:.4f} (gated vs {eval_path.parent.name})  "
              f"GS ${cost:.2f}  55-map production ~${cost_55:.0f}", flush=True)

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

    # The same round-robin on tile-MCC, through the MCC sibling of the F1
    # kernel: same seed, same tile order, therefore the same swap masks. Its
    # own BH family — the F1 tiering above is unchanged.
    print("\n=== round-robin on tile-MCC (21 pairs, 10k, seed 42) ===",
          flush=True)
    pairs_mcc, significant_mcc = [], {}
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            a, b = cells[i], cells[j]
            r = permutation_test_mcc_arrays(
                a["tp_c"], a["tn_c"], a["fp_c"], a["fn_c"],
                b["tp_c"], b["tn_c"], b["fp_c"], b["fn_c"],
                n_permutations=10000, seed=42)
            pairs_mcc.append({"a": a["rung"], "b": b["rung"], **r})
    adjusted_mcc = apply_bh_correction([q["p_value"] for q in pairs_mcc], q=0.05)
    for q_row, adj in zip(pairs_mcc, adjusted_mcc):
        q_row["bh_adjusted_p"] = round(adj, 6)
        q_row["significant"] = bool(adj < 0.05)
        significant_mcc[frozenset({q_row["a"], q_row["b"]})] = q_row["significant"]
    ordered_mcc = sorted(cells, key=lambda c: -c["mcc"])
    tiers_mcc = greedy_clique_tiers([c["rung"] for c in ordered_mcc],
                                    significant_mcc)
    tier_of_mcc = {r: t for t, members in enumerate(tiers_mcc, 1) for r in members}
    n_sig_mcc = sum(1 for q_row in pairs_mcc if q_row["significant"])
    print(f"{n_sig_mcc}/21 significant -> {len(tiers_mcc)} MCC tier(s): "
          f"{tiers_mcc}", flush=True)

    # Pareto-efficient set on (cost, F1): no other rung is cheaper AND better.
    eff = [c["rung"] for c in cells
           if not any(o["est_cost_usd"] <= c["est_cost_usd"] and o["f1"] > c["f1"]
                      for o in cells if o is not c)]
    # The same test on (cost, tile-MCC) — the second frontier the PI's ruling
    # asks for. It is computed, not asserted: whether it coincides with the F1
    # frontier is the question the column exists to answer.
    eff_mcc = [c["rung"] for c in cells
               if not any(o["est_cost_usd"] <= c["est_cost_usd"]
                          and o["mcc"] > c["mcc"]
                          for o in cells if o is not c)]

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def draw_panel(ax, metric: str, metric_eff: list[str],
                   tiers_by_rung: dict[str, int], ylabel: str,
                   title: str) -> None:
        """Draw one cost-versus-metric frontier panel.

        Args:
            ax: Target axes.
            metric: Cell key to plot on the y axis (``f1`` or ``mcc``).
            metric_eff: Rung names on that metric's efficient set.
            tiers_by_rung: Rung -> tier index for that metric's tiering.
            ylabel: Y-axis label.
            title: Panel title.
        """
        front = sorted([c for c in cells if c["rung"] in metric_eff],
                       key=lambda c: c["est_cost_usd"])
        ax.plot([c["est_cost_usd"] for c in front],
                [c[metric] for c in front],
                "-", color="#1f77b4", lw=1.2, zorder=2,
                label="Pareto frontier")
        for c in cells:
            on = c["rung"] in metric_eff
            ax.scatter([c["est_cost_usd"]], [c[metric]], s=60, zorder=3,
                       color="#1f77b4" if on else "#aaaaaa")
            ax.annotate(
                f"{c['rung']} (T{tiers_by_rung[c['rung']]})\n{c[metric]:.4f}",
                (c["est_cost_usd"], c[metric]), textcoords="offset points",
                xytext=(0, 9), ha="center", fontsize=8,
                color="black" if on else "#777777")
        ax.set_xscale("log")
        ax.set_xlabel("estimated cost per full run (flex USD, log scale)")
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=10)
        ax.grid(alpha=0.3)
        ax.legend(loc="lower right", fontsize=8)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.8))
    draw_panel(axes[0], "f1", eff, tier_of, "F1@20 m (best operating point)",
               "(a) localisation — F1 @ 20 m")
    draw_panel(axes[1], "mcc", eff_mcc, tier_of_mcc,
               "tile-level MCC (buffer-invariant)",
               "(b) tile discrimination — tile-level MCC")
    fig.suptitle("Cost-weighted Pareto frontiers — GS 384 px "
                 "proposer-verifier", fontsize=12)
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
        "mcc": {
            "statistic": "tile-level MCC from each rung's committed "
                         "evaluation, gated by rebuilding the per-tile "
                         "classification through the house definition",
            "frame": "Era-2, 487 tiles "
                     "(inputs/vectors/bounds/384/full_evaluation_bounds.geojson)",
            "buffer_invariance": "tile truth is intersection with any "
                                 "reference and tile prediction is any "
                                 "detection assigned to the tile, so no "
                                 "matching tolerance enters: this MCC is the "
                                 "same number at every F1 buffer",
            "kernel": "pairwise_permutation_test.permutation_test_mcc_arrays "
                      "(same seed, same tile order, therefore the same swap "
                      "masks as the F1 round-robin)",
            "tiers": tiers_mcc,
            "pareto_efficient": eff_mcc,
            "n_significant": n_sig_mcc,
            "pairwise": pairs_mcc,
        },
        "rungs": [{k: v for k, v in c.items()
                   if k not in ("tp", "fp", "fn",
                                "tp_c", "tn_c", "fp_c", "fn_c")}
                  | {"tier": tier_of[c["rung"]],
                     "tier_mcc": tier_of_mcc[c["rung"]]} for c in ordered],
        "pairwise": pairs}, indent=2) + "\n")
    print(f"Pareto-efficient set (F1):  {eff}", flush=True)
    print(f"Pareto-efficient set (MCC): {eff_mcc}", flush=True)
    print(f"Wrote {OUT_DIR.relative_to(BASE_DIR)}/pareto_v2.{{json,png}}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
