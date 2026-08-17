#!/usr/bin/env python3
# ============================================================================
# author_second_wave_registration.py
# ----------------------------------------------------------------------------
# Session 113 ($0): second-wave manifest registration of the Session 111-112
# discoveries (the S113 continuity cell list; follows the S111 author/gate
# pattern of author_verifier_robustness_registration.py).
#
# Authors, into the four hand-authored generator inputs:
#   - results/run-registry.json    : runs #30 'flash35-pv-2x2' and #31
#                                    '55maps-text-min-n10-uplift'
#   - results/run-facts.json       : their facts
#   - results/run-conditions.json  : 6 pv-diag-384 additions (the min6 family,
#                                    min11, the T0.3 GS cell, the GS image PV
#                                    cell, the Pro-verifier cell) + 4 flash35
#                                    conditions + the uplift condition
#   - results/run-analyses.json    : 4 analyses (min-vs-high-thinking-pv,
#                                    pass-budget-pareto-v2, flash35-model-roles,
#                                    unswept-pools-completeness); a fifth —
#                                    55map-canonical-leaderboard-50m — is
#                                    authored by --board-analysis AFTER the
#                                    55-map board refresh, composed from
#                                    results/55map-leaderboard/55map_leaderboard_50m.json.
#
# VALIDATION GATES (the script refuses to write if any fails):
#   1. every detections geojson + eval_path evaluation.json exists;
#   2. each evaluation's F1 at its gate buffer reproduces the committed record
#      (GS cells: 20 m, 4 d.p. exact; the uplift cell: 50 m within 0.003 — the
#      55-map board's mechanism-equivalence tolerance, since the Track-2
#      corrected-F1 engine and the board scorer are different machinery);
#   3. each evaluation's n_detections equals the geojson feature count
#      (the Session-77 cross-check rule);
#   4. no run/condition/analysis ID collision with the existing manifest.
#
# DRY-RUN BY DEFAULT (project convention) — pass --execute to write. After
# executing: generate_post_run_report.py --all --write, then the drift-check
# (verify_run_conditions.py).
#
# Usage:
#   .venv/bin/python scripts/author_second_wave_registration.py
#   .venv/bin/python scripts/author_second_wave_registration.py --execute
#   .venv/bin/python scripts/author_second_wave_registration.py --board-analysis [--execute]
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REG = BASE_DIR / "results" / "run-registry.json"
FACTS = BASE_DIR / "results" / "run-facts.json"
CONDS = BASE_DIR / "results" / "run-conditions.json"
ANALYSES = BASE_DIR / "results" / "run-analyses.json"
BOARD_JSON = BASE_DIR / "results" / "55map-leaderboard" / "55map_leaderboard_50m.json"

VR = "results/verifier-robustness"
F35 = "results/flash35-2x2"

# Verifier config building blocks (mirror the S111 registration).
FLASH_VF = {"variant": "v1", "instruction_file": "verify_adversarial.md",
            "model": "gemini-3-flash-preview"}
PRO_VF = {"variant": "v1", "instruction_file": "verify_adversarial.md",
          "model": "gemini-3.1-pro-preview"}
F35_VF = {"variant": "v1", "instruction_file": "verify_adversarial.md",
          "model": "gemini-3.5-flash"}


def vf(base: dict, thinking: str, temp: float, n: int) -> dict:
    """Assemble a verifier_config object (all second-wave cells are n=1)."""
    return {**base, "thinking_level": thinking, "temperature": temp, "iterations": n}


# --- the 6 pv-diag-384 additions ---------------------------------------------
# (label, proposer_pool, n_passes, vote_t, prob_t, verifier_config, detections,
#  eval_path, expected F1@20m, _note)
PVD_CONDITIONS = [
    ("verified-adv-text-min-true-3of5", "text-min-t07-true-1of5",
     5, 3, 0.15, vf(FLASH_VF, "minimal", 0.0, 1),
     f"{VR}/min-thinking-sets/text-min-t07-TRUE-5pass-3of5-n1-pt0.15.geojson",
     f"{F35}/evals/min6-true/evaluation.json", 0.8784,
     "min6 (TRUE merge): first-5 union of the text-n10 minimal lineage, "
     "re-cropped and re-verified after the stale partial-coverage text-1of5 "
     "union was excluded (make-up run ~$1.11, S112; min6_true_makeup.json). "
     "Pareto v2 'min6' efficient rung ($3.81)."),
    ("verified-adv-text-min-n30lineage-4of5", "flash-minimal-text-t07-1of5",
     5, 4, 0.15, vf(FLASH_VF, "minimal", 0.0, 1),
     f"{VR}/min-thinking-sets/text-min-t07-5pass-n30lineage-4of5-n1-pt0.15.geojson",
     f"{F35}/evals/min6-n30lineage/evaluation.json", 0.8708,
     "min6 (n30 lineage): first-5 of the 30-pass minimal study; the min6 "
     "stand-in in min_vs_high_permutations.json (p=0.656 vs high6)."),
    ("verified-adv-text-min-6of10", "text-1of10",
     10, 6, 0.2, vf(FLASH_VF, "minimal", 0.0, 1),
     f"{VR}/min-thinking-sets/text-min-t07-10pass-6of10-n1-pt0.2.geojson",
     f"{F35}/evals/min11/evaluation.json", 0.8835,
     "min11: 10-pass minimal union + carry-forward verifier. Best tile-MCC "
     "on the PV board (0.807); Pareto v2 'min11' efficient rung ($6.75); the "
     "F3xF3 corner of the Flash 3.5 2x2x2 (harness self-validation)."),
    ("verified-adv-text-t03-4of5", "flash-high-text-t03-1of5",
     5, 4, 0.2, vf(FLASH_VF, "minimal", 0.0, 1),
     f"{VR}/condition-sets/t03-4of5-n1-pt0.2.geojson",
     f"{VR}/evals/verified-adv-text-t03-4of5/evaluation.json", 0.8783,
     "Run A ($2.06, S112): GS characterisation of the deployment champion's "
     "proposer (text HIGH T=0.3) — completes the GS-vs-55map transfer table "
     "(0.9045 @ 50 m; results/working-precision/gs-t03-pv-cell.json)."),
    ("verified-adv-image-3of5", "flash-high-image-1of5",
     5, 3, 0.15, vf(FLASH_VF, "minimal", 0.0, 1),
     f"{VR}/condition-sets/image-3of5-n1-pt0.15.geojson",
     f"{VR}/evals/verified-adv-image-3of5/evaluation.json", 0.7778,
     "GS image PV cell (HIGH T=0.7 5-pass + carry-forward verifier): the "
     "image row of the transfer table (0.8771 @ 50 m) and the image-modality "
     "75 m plateau material (Obs 360; "
     "results/working-precision/gs-image-pv-cell.json)."),
    ("verified-adv-text-pro-vf-4of5", "flash-high-text-1of5",
     5, 4, 0.25, vf(PRO_VF, "medium", 0.0, 1),
     f"{VR}/min-thinking-sets/high6-PRO-vf-4of5-pt0.25.geojson",
     f"{VR}/evals/verified-adv-text-pro-vf-4of5/evaluation.json", 0.8792,
     "Completeness-sweep discovery (Obs 363): the Pro verifier over the "
     "Flash-HIGH 5-pass union — +0.015 vs the Flash verifier on the same "
     "pool (raw p=0.019, post-hoc), ns vs the headline (p=0.41) and min11 "
     "(p=0.76). Refines Obs 359's 'verifier model barely matters' to "
     "high-recall pools; dominated by min11 on cost."),
]

# --- run #30: flash35-pv-2x2 -------------------------------------------------
F35_REGISTRY = {
    "run_id": "flash35-pv-2x2",
    "directory_path": "outputs/flash35-pv-2x2",
    "status": "active",
    "notes": ("Flash 3.5 model-role 2x2x2 (Sessions 111-112, ~$34 flex): "
              "10 gemini-3.5-flash MINIMAL-thinking T=0.7 detect_brief-text "
              "proposer passes on the GS 487 (384 px), three verifier legs "
              "(F3 vf over the F3.5 pool; F3.5 vf over the F3.5 pool; F3.5 vf "
              "over the cross-run F3 minimal pool), n in {5,10} via the "
              "verify-once shortcut (n=5 method-matched derivations are "
              "analysis-internal). Verdict: Flash 3.5 wins in NO role at the "
              "minimal operating point — the all-Flash-3 stack stands. "
              "Analysis: results/flash35-2x2/; findings "
              "verifier-robustness-findings.md SS 14; runbook "
              "scripts/run_flash35_tranche1.sh."),
}

F35_FACTS = {
    "primary_hypothesis": None,
    "also_informs": ["flash-vs-flash35", "pv-strategy"],
    "purpose": ("Model-role 2x2x2: is Flash 3.5 a better bare proposer, PV "
                "proposer, or verifier than Flash 3 at the minimal operating "
                "point? (The S110 parking note: bare proposer was the only "
                "angle a stronger model might win.)"),
    "tile_size_px": 384,
    "corpus": "4-map-gs",
    "gt_reference": "curator",
    "scope": {
        "test_set_id": "era-2-487",
        "bounds_path": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
        "n_test_tiles": 487,
        "calibration_set_id": None,
        "n_calibration_tiles": None,
    },
    "headline_condition_id": None,
    "headline_rationale": (
        "Deliberately none — a model comparison, not a champion search: "
        "Flash 3.5 wins in NO role (bare-proposer numerical tie 0.6196 vs "
        "0.6204; PV proposer -0.0355, p=0.035 targeted tile-swap — the one "
        "resolved role gap; verifier -0.012..-0.015, within-noise ties, at "
        "3x the price). The all-Flash-3 production stack stands "
        "(findings SS 14; results/flash35-2x2/flash35_permutations.json)."),
    "historical_aliases": [],
    "_scope_confidence": "HIGH",
    "_scope_source": ("scripts in repo: all evals score against "
                      "bounds/384/full_evaluation_bounds.geojson (era-2-487)"),
    "_flags": [
        "verify-once-at-n10: the n=5 cells are method-matched first-5 derivations "
        "(results/verifier-robustness/first5of10-validation/) — analysis-internal, "
        "not registered (systematically +0.005..+0.011 high vs a true 5-pass merge)",
        "pass 1 lost tiles to transient JSON-parse failures; resume x4 policy "
        "enforced a 485/487 floor per pass (outputs/flash35-pv-2x2/tranche-full.log)",
        "the f3prop pool is cross-run (pv-diag-384 text-n10 minimal lineage), "
        "re-cropped in-run under min-f3-crops/ (source_run per condition)",
    ],
}

# (label, architecture, aggregation, pool, n_passes, vote_t, prob_t, vconf,
#  detections, eval_path, expected F1@20m, source_run)
F35_CONDITIONS = [
    ("f35prop-bare-10of10", "consensus", "consensus", "flash35-min-text-1of10",
     10, 10, None, None,
     f"{F35}/best-op-sets/f35prop-bare-n10-10of10.geojson",
     f"{F35}/evals/f35prop-bare-n10-10of10/evaluation.json", 0.6196, None),
    ("f35prop-f3vf-4of10", "proposer-verifier", "verified", "flash35-min-text-1of10",
     10, 4, 0.15, vf(FLASH_VF, "minimal", 0.0, 1),
     f"{F35}/best-op-sets/f35prop-f3vf-n10-4of10-pt0.15.geojson",
     f"{F35}/evals/f35prop-f3vf-n10-4of10-pt0.15/evaluation.json", 0.8480, None),
    ("f35prop-f35vf-4of10", "proposer-verifier", "verified", "flash35-min-text-1of10",
     10, 4, 0.25, vf(F35_VF, "minimal", 0.0, 1),
     f"{F35}/best-op-sets/f35prop-f35vf-n10-4of10-pt0.25.geojson",
     f"{F35}/evals/f35prop-f35vf-n10-4of10-pt0.25/evaluation.json", 0.8362, None),
    ("f3prop-f35vf-6of10", "proposer-verifier", "verified", "f3-min-text-1of10",
     10, 6, 0.25, vf(F35_VF, "minimal", 0.0, 1),
     f"{F35}/best-op-sets/f3prop-f35vf-n10-6of10-pt0.25.geojson",
     f"{F35}/evals/f3prop-f35vf-n10-6of10-pt0.25/evaluation.json", 0.8689,
     "pv-diag-384"),
]

F35_DECOMPOSITION_NOTE = (
    "Flash 3.5 2x2x2 at the n=10 grain: one citable condition per registered "
    "corner at its best (k, prob_t) operating point (the settled decomposition "
    "pattern). The F3-proposer x F3-verifier corner is NOT duplicated here — it "
    "is pv-diag-384::verified-adv-text-min-6of10 (min11, 0.8835), which the "
    "tranche reproduced exactly (harness self-validation). The n=5 cells are "
    "method-matched first-5 derivations, analysis-internal "
    "(results/flash35-2x2/analysis-full.json). The f3prop pool is cross-run "
    "(pv-diag-384 text-n10 minimal lineage)."
)

# --- run #31: 55maps-text-min-n10-uplift -------------------------------------
UPLIFT_REGISTRY = {
    "run_id": "55maps-text-min-n10-uplift",
    "directory_path": "outputs/55maps-text-min-n10-uplift",
    "status": "active",
    "notes": ("Run B (Session 112-113, ~$60 flex, Shawn-approved): the min11 "
              "deployment uplift — 10 gemini-3-flash MINIMAL-thinking T=0.7 "
              "detect_brief-text proposer passes over the 55-map corpus "
              "(8,541 tiles), the >=3-of-10 band cropped (16,482 candidates) "
              "+ the carry-forward n=1 verifier. Answers Obs 362's open "
              "question: pass count closes about HALF the deployment thinking "
              "gap (Obs 364). Scored vs the canonical extended GT at 50 m "
              "(results/55map-leaderboard/min11_uplift_cell.json; Track-2 "
              "eval results/55maps-extended-gt-2026-06-07/TM-n10-k5/)."),
}

UPLIFT_FACTS = {
    "primary_hypothesis": None,
    "also_informs": ["deployment-uplift", "pass-budget"],
    "purpose": ("Run B: does PASS COUNT close the -0.030 deployment thinking "
                "gap (Obs 362)? 10 minimal passes + band verifier vs TM-k3 "
                "and TH7-k3 at the canonical 50 m buffer."),
    "tile_size_px": 384,
    "corpus": "55-map",
    # 'combined' is the schema vocabulary for the canonical extended GT
    # (reviewed student GT + adjudicated phantoms); detail in _flags.
    "gt_reference": "combined",
    "scope": {
        "test_set_id": "55maps-8541",
        "bounds_path": "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson",
        "n_test_tiles": 8541,
        "calibration_set_id": None,
        "n_calibration_tiles": None,
    },
    "headline_condition_id": None,
    "headline_rationale": (
        "Single-condition run; the citable cell is verified-5of10-canonical-gt "
        "(0.8290 @ 50 m, 5of10/pt0.15): significantly above TM-k3 (+0.0163, "
        "p<1e-4) and significantly below TH7-k3 (-0.0134, p=0.0026) — a priced "
        "cost/quality trade, not a tie (Obs 364)."),
    "historical_aliases": [],
    "_scope_confidence": "HIGH",
    "_scope_source": ("empirical: proposer ran the 55-map corpus; scored against "
                      "bounds/384/55maps_evaluation_bounds.geojson (8,541 tiles)"),
    "_flags": [
        "gt_reference is the CANONICAL EXTENDED GT (Track-2, S105: reviewed "
        "student GT + 773 per-buffer-gated phantoms) — this run has NO Track-1 "
        "reviewed-student-GT scoring",
        "only the >=3-of-10 band was cropped/verified (16,482 candidates); "
        "sub-3-vote operating points are not reachable from the verified band",
        "outputs/55maps-text-min-n10-uplift/proposer-all/ is an untracked "
        "symlink farm (regenerable merge scaffolding) — deliberate",
    ],
}

UPLIFT_CONDITION = {
    "label": "verified-5of10-canonical-gt",
    "architecture": "proposer-verifier",
    "aggregation": "verified",
    "proposer_pool": "detect_brief-text-min-n10",
    "n_passes": 10,
    "vote_threshold": 5,
    "prob_threshold": 0.15,
    "verifier_config": vf(FLASH_VF, "minimal", 0.0, 1),
    "eval_path": "results/55maps-extended-gt-2026-06-07/TM-n10-k5/evaluation.json",
    "detections": "results/55map-leaderboard/min11-uplift-5of10-pt0.15.geojson",
    "_note": ("min11 uplift, vote 5-of-10 (prob>=0.15), vs canonical extended "
              "GT; best deployment op sat looser than the GS-best 6of10 — the "
              "k3 lesson recurring at n=10 (Obs 364)"),
}
UPLIFT_EXPECT_F1_50 = 0.829028  # committed sweep value (min11_uplift_cell.json)
UPLIFT_GATE_TOL = 0.003         # the 55-map board's mechanism-equivalence tol

UPLIFT_DECOMPOSITION = {
    "_note": ("Run B uplift: one citable condition at the best deployment "
              "operating point (5of10/pt0.15) vs the canonical extended GT. "
              "MIXED-PROVENANCE POOL (the n-passes-over WARN is the honest "
              "by-design signal, per the S106 settled position): passes 1-5 "
              "are the 55maps-text-min-generalisation deployment passes; "
              "passes 6-10 are this run's (proposer/run_6..run_10; "
              "uplift-full.log Stage P). The k(3..10) x prob_t sweep lives in "
              "results/55map-leaderboard/min11-uplift-score.log and "
              "min11_uplift_cell.json."),
    "proposer_pools": {
        "detect_brief-text-min-n10": {"modality": "text", "path": "proposer"},
    },
    "verifier_passes": {
        "verified-3of10": {"modality": "text", "path": "verified-3of10"},
    },
    "conditions": [UPLIFT_CONDITION],
}

# --- analyses ----------------------------------------------------------------
MIN_VS_HIGH_ANALYSIS = {
    "analysis_id": "min-vs-high-thinking-pv",
    "type": "leaderboard",
    "_note": ("Targeted paired tile-swap permutations (10k, seed 42, two-sided; "
              "scripts/score_min_thinking_pv.py; "
              "results/verifier-robustness/min_vs_high_permutations.json + "
              "min6_true_makeup.json) comparing MINIMAL- vs HIGH-thinking "
              "proposer pools at equal pass budget under the carry-forward n=1 "
              "verifier — the dollar-axis question behind Pareto v2. NOT a full "
              "round-robin board: five targeted pairs. Citable write-up: "
              "verifier-robustness-findings.md SS 13."),
    "conditions_compared": [
        "pv-diag-384::verified-adv-text-min-true-3of5",
        "pv-diag-384::verified-adv-text-min-n30lineage-4of5",
        "pv-diag-384::verified-adv-text-min-6of10",
        "pv-diag-384::verified-adv-text-4of5",
        "pv-diag-384::verified-adv-text-6of10",
        "pv-diag-384::verified-adv-text-consensus-16of30",
        "verifier-robustness::verified-384-16of30-t0-3-n5-opmax",
    ],
    "hypothesis_refs": ["H2", "H3"],
    "preregistered": "post-hoc",
    "deviations": [],
    "predicted_outcome": (
        "The consensus-era diversity dividend (Obs 141: HIGH-thinking pass "
        "diversity lifts consensus F1; confirmed for consensus-only "
        "architectures in the phase3a decomposition) predicts HIGH > MINIMAL "
        "at equal pass count under the proposer-verifier architecture too."),
    "tie_set": [
        "pv-diag-384::verified-adv-text-min-n30lineage-4of5",
        "pv-diag-384::verified-adv-text-min-6of10",
        "pv-diag-384::verified-adv-text-4of5",
        "pv-diag-384::verified-adv-text-6of10",
        "pv-diag-384::verified-adv-text-consensus-16of30",
        "verifier-robustness::verified-384-16of30-t0-3-n5-opmax",
    ],
    "outcome": (
        "REJECTED on the GS instrument — at equal pass count under PV, MINIMAL "
        "reaches statistical parity with HIGH: min6 (n30-lineage, 0.8708) vs "
        "high6 (0.8641) p=0.656; min11 (0.8835) vs high11 (0.8769) p=0.591; "
        "min11 vs the 31-pass headline (0.8902) p=0.562; min11 vs opmax35 "
        "(0.8951) p=0.324; min6 vs min11 p=0.271. The TRUE min6 merge (0.8784) "
        "sits numerically above its permuted n30-lineage stand-in. Mechanism "
        "(pool_recall_ceilings.json, zero_diversity_anchor.json): the verifier "
        "shifts the binding constraint to POOL RECALL; minimal T=0.7 sampling "
        "saturates Flash's reachable recall in ~5 passes (0.9195 — the 10-pass "
        "lineage adds zero new GT mounds), while HIGH thinking adds volume "
        "(union/pass 2.46 vs 1.44) but only +0.023 ceiling. The zero-diversity "
        "anchor (1 x T=0.0 pass + n=1 vf) scores 0.8142 with the board's "
        "second-best tile-MCC (0.833); min11 holds the best (0.807). The "
        "consensus-era dividend (Obs 141) is real for consensus-only "
        "architectures and OBSOLETE under PV (Obs 359). SCOPE: GS-characterised "
        "only — the parity REVERSED at 55-map deployment (TM-k3 0.8127 T3 vs "
        "TH7-k3 0.8425 T1; Obs 362); deployment evidence overrides this "
        "characterisation tie."),
    "paper_section": "Results",
    "output_path": "results/verifier-robustness",
    "working_notes_obs": [
        "Obs 359 — the diversity dividend does not survive the verifier "
        "(pool recall ceiling binds)",
        "Obs 362 — the GS min~high tie reversed at deployment (scope qualification)",
        "Obs 141 — the consensus-era diversity dividend (the prior this rejects under PV)",
    ],
    "manually_verified_at": None,
}

PARETO_V2_ANALYSIS = {
    "analysis_id": "pass-budget-pareto-v2",
    "type": "leaderboard",
    "_note": ("The COST-weighted successor to pass-budget-pareto (v1, passes "
              "axis): seven Flash-ladder rungs priced from the TM run's "
              "MEASURED token load at June-2026 flex rates (verifier "
              "$0.000697/call; HIGH proposer pass ~3x minimal; flex = batch "
              "pricing on Gemini 3), full C(7,2)=21 round-robin tile-swap + "
              "BH-FDR q=0.05 + greedy-clique tiers "
              "(scripts/build_pareto_v2.py). v1's artefacts "
              "(pareto_leaderboard.{json,png}) are kept as the record; CITE V2 "
              "ONLY (pareto/pareto_v2.{json,png}). Citable write-up: findings "
              "SS 15."),
    "conditions_compared": [
        "pv-diag-384::verified-adv-text-min-true-3of5",
        "pv-diag-384::verified-adv-text-min-6of10",
        "pv-diag-384::verified-adv-text-4of5",
        "verifier-robustness::verified-384-ge3of5-t0-3-n5",
        "pv-diag-384::verified-adv-text-6of10",
        "pv-diag-384::verified-adv-text-consensus-16of30",
        "verifier-robustness::verified-384-16of30-t0-3-n5-opmax",
    ],
    "hypothesis_refs": ["H2", "H3"],
    "preregistered": "post-hoc",
    "deviations": [],
    "predicted_outcome": (
        "S111's v1 found the five-rung passes ladder one statistical tier; the "
        "cost recast (Shawn, S111: a HIGH pass costs ~3x a minimal one, so "
        "v1's 'cheap6' is not the cheap end in dollars) asks whether the "
        "dollar-axis frontier collapses onto the minimal-thinking rungs."),
    "tie_set": [
        "verifier-robustness::verified-384-16of30-t0-3-n5-opmax",
        "pv-diag-384::verified-adv-text-consensus-16of30",
        "pv-diag-384::verified-adv-text-min-6of10",
        "pv-diag-384::verified-adv-text-min-true-3of5",
        "pv-diag-384::verified-adv-text-6of10",
        "verifier-robustness::verified-384-ge3of5-t0-3-n5",
        "pv-diag-384::verified-adv-text-4of5",
    ],
    "outcome": (
        "All seven rungs remain ONE statistical tier (0/21 pairs significant "
        "after BH-FDR) — extra spend cannot be shown to buy F1 on this "
        "instrument. Pareto-efficient set: min6 $3.81/0.8784, min11 "
        "$6.75/0.8835, high31 $48.81/0.8902, high35 $50.84/0.8951; DOMINATED: "
        "high6 ($10.65/0.8641 — v1's 'cheap6' is in fact the third most "
        "expensive way to buy ~0.87), high5+5vf ($11.03/0.8739), high11 "
        "($20.19/0.8769). 55-map production column (tile factor 8541/487, "
        "crops/tile from the GS pools — slight upper bounds): min6 ~$67, min11 "
        "~$118, high31 ~$856, high35 ~$892. Costs recalibrated 2026-06-11 to "
        "measured tokens (~$9.40 per 8,541-tile minimal pass at flex; the "
        "smoke-derived model under-priced proposer passes 1.8x) — the "
        "efficient set was unchanged by the recalibration. SCOPE (Obs 362): "
        "the F1 column is GS-characterised; at deployment the minimal rungs "
        "degrade hardest (transfer deltas HIGH-T0.7 -0.048 < HIGH-T0.3 -0.057 "
        "< image -0.078 < MIN -0.087), so the min rungs are NOT production "
        "recommendations without the findings SS 16 qualification."),
    "paper_section": "Results",
    "output_path": "results/verifier-robustness/pareto",
    "working_notes_obs": [
        "Obs 357 — the cost meta-rule (the frontier's decision rule)",
        "Obs 359 — minimal-thinking parity (why the min rungs exist)",
        "Obs 362 — deployment reversal (the scope qualification on the F1 column)",
    ],
    "manually_verified_at": None,
}

FLASH35_ANALYSIS = {
    "analysis_id": "flash35-model-roles",
    "type": "leaderboard",
    "_note": ("The Flash 3.5 2x2x2 (proposer model x verifier model x n in "
              "{5,10}; ~$34 flex) at the minimal-thinking operating point. "
              "n=5 cells are method-matched first-5 derivations "
              "(first5of10-validation/), analysis-internal; the n10 grid is "
              "registered (run flash35-pv-2x2; the F3xF3 corner is "
              "pv-diag-384::verified-adv-text-min-6of10). Targeted role "
              "permutations (S113, three raw p-values — multiplicity caveat in "
              "outcome): results/flash35-2x2/flash35_permutations.json. "
              "Citable write-up: findings SS 14; dossier "
              "reports/session-111-discoveries.md SS 11."),
    "conditions_compared": [
        "flash35-pv-2x2::f35prop-bare-10of10",
        "flash35-pv-2x2::f35prop-f3vf-4of10",
        "flash35-pv-2x2::f35prop-f35vf-4of10",
        "flash35-pv-2x2::f3prop-f35vf-6of10",
        "pv-diag-384::verified-adv-text-min-6of10",
    ],
    "hypothesis_refs": ["H2"],
    "preregistered": "post-hoc",
    "deviations": [],
    "predicted_outcome": (
        "S110 parking note: a bare-proposer comparison is the ONLY angle a "
        "stronger model might win, since the PV architecture disadvantages "
        "precise proposers (findings SS 9, the Pro pattern)."),
    "tie_set": [
        "pv-diag-384::verified-adv-text-min-6of10",
        "flash35-pv-2x2::f3prop-f35vf-6of10",
    ],
    "outcome": (
        "Flash 3.5 wins in NO role at the minimal operating point. As a bare "
        "proposer it ties Flash 3 (0.6196 vs 0.6204 at 10of10 consensus — the "
        "predicted only-winnable angle closes). As a PV proposer it loses "
        "-0.0355 under the same F3 verifier (0.8480 vs min11's 0.8835, "
        "p=0.035 targeted tile-swap — the ONE statistically resolved role "
        "gap, though marginal under a BH correction across the three role "
        "tests): its 10-pass union is 1,132 candidates vs Flash 3's 1,939 "
        "with 53% at 10/10 votes (union/pass 1.32) — the Pro pattern of "
        "consistency-without-coverage, and PV needs coverage (the Obs 359 "
        "recall-ceiling mechanism). As a verifier it loses on both pools "
        "(-0.0117 on its own pool, p=0.17; -0.0146 on the F3 pool, p=0.10 — "
        "within-noise ties) at 3x the price, so the carry-forward F3 verifier "
        "wins per the cost meta-rule (Obs 357). The all-Flash-3 stack stands; "
        "harness self-validated (the F3xF3 corner reproduces the committed "
        "min11 exactly, 0.8835 at 6of10/pt0.2)."),
    "paper_section": "Results",
    "output_path": "results/flash35-2x2",
    "working_notes_obs": [
        "Obs 357 — the cost meta-rule (decides the within-noise verifier role)",
        "Obs 359 — pool recall ceiling (the proposer-role mechanism)",
    ],
    "manually_verified_at": None,
}

UNSWEPT_ANALYSIS = {
    "analysis_id": "unswept-pools-completeness",
    "type": "sweep",
    "_note": ("Completeness sweep (S112-113 / Obs 363): all 18 never-PV-swept "
              "proposer pools under outputs/h11/pv-diag-384 scored at their "
              "best (proposer-k x prob_t) operating points "
              "(scripts/sweep_unswept_pools.py; "
              "results/verifier-robustness/unswept_pools_sweep.json, "
              "pro_vf_permutations.json). TWO sweep cells are minted as "
              "citable conditions (verified-adv-text-pro-vf-4of5 and "
              "verified-adv-image-3of5); the remaining 16 stay "
              "analysis-internal PENDING Shawn's citability decision (S113 "
              "continuity). Like pv-diag-384-consensus-calibration, this "
              "registers calibration/completeness material, not a finding "
              "board."),
    "conditions_compared": [
        "pv-diag-384::verified-adv-text-pro-vf-4of5",
        "pv-diag-384::verified-adv-image-3of5",
    ],
    "hypothesis_refs": ["H2", "H11"],
    "preregistered": "post-hoc",
    "deviations": [],
    "predicted_outcome": (
        "A completeness check on the registered headline: no never-swept pool "
        "should beat 0.8902 at its own best operating point; the 30-pass "
        "union's global optimum should be the registered 16of30 cell."),
    "tie_set": [],
    "outcome": (
        "The headline SURVIVES the global-optimum check: the full 30-pass "
        "union's best PV operating point IS the registered 16of30 headline "
        "(0.8902 at k=16/pt0.2 over all 11,771 candidates) — restricting the "
        "S108 Stage-D verification to the 729-crop 16of30 subset lost "
        "nothing. One discovery: the PRO verifier over the Flash-HIGH 5-pass "
        "union scores 0.8792 (4of5/pt0.25) — +0.015 over the Flash verifier "
        "on the same pool (raw p=0.019, POST-HOC, not multiplicity-"
        "controlled), ns vs the headline (p=0.41) and vs min11 (p=0.76): "
        "refines Obs 359's 'verifier model barely matters' (measured on the "
        "low-headroom Pro pool) to high-recall pools where verification is "
        "the binding stage — while min11 dominates it on cost. The image "
        "rows populate the transfer table (image PV 0.7778 @ 20 m / 0.8771 "
        "@ 50 m)."),
    "paper_section": "Results",
    "output_path": "results/verifier-robustness",
    "working_notes_obs": [
        "Obs 363 — the completeness sweep (this analysis)",
        "Obs 359 — verifier-model scope refinement",
    ],
    "manually_verified_at": None,
}

NEW_ANALYSES = [MIN_VS_HIGH_ANALYSIS, PARETO_V2_ANALYSIS, FLASH35_ANALYSIS,
                UNSWEPT_ANALYSIS]

BOARD_NAME_BY_CID = {
    # board display name -> condition_id is carried in the board JSON itself;
    # this constant only documents the uplift's display name for the _note.
    "TM-n10-k5 (uplift)": "55maps-text-min-n10-uplift::verified-5of10-canonical-gt",
}


def build_condition(label: str, arch: str, agg: str, pool: str, n_passes: int,
                    vote_t, prob_t, vconf, detections: str, eval_path: str,
                    note: str | None, source_run: str | None) -> dict:
    """Assemble one run-conditions sidecar entry."""
    cond = {
        "label": label,
        "architecture": arch,
        "aggregation": agg,
        "proposer_pool": pool,
        "n_passes": n_passes,
        "vote_threshold": vote_t,
        "prob_threshold": prob_t,
        "verifier_config": vconf,
        "eval_path": eval_path,
        "detections": detections,
    }
    if note:
        cond["_note"] = note
    if source_run:
        cond["source_run"] = source_run
    return cond


def gate(cond: dict, expect_f1: float, buffer_m: int = 20,
         tol: float = 0.0) -> list[str]:
    """Validate one condition's artefacts; return a list of failures.

    GS cells gate at 20 m with 4-d.p. equality (tol=0); the uplift cell gates
    at 50 m within the board's 0.003 mechanism-equivalence tolerance.
    """
    fails = []
    det = BASE_DIR / cond["detections"]
    ev = BASE_DIR / cond["eval_path"]
    if not det.exists():
        return [f"{cond['label']}: detections MISSING ({cond['detections']})"]
    if not ev.exists():
        return [f"{cond['label']}: evaluation MISSING ({cond['eval_path']})"]
    n_feat = len(json.loads(det.read_text())["features"])
    summary = json.loads(ev.read_text())["summary"]
    b = next(x for x in summary["buffers"] if x["buffer_metres"] == buffer_m)
    if tol == 0.0:
        if round(b["f1"], 4) != expect_f1:
            fails.append(f"{cond['label']}: eval F1@{buffer_m}m {b['f1']:.4f} "
                         f"!= {expect_f1}")
    elif abs(b["f1"] - expect_f1) > tol:
        fails.append(f"{cond['label']}: eval F1@{buffer_m}m {b['f1']:.6f} vs "
                     f"{expect_f1:.6f} (|delta| > {tol})")
    if summary["n_detections"] != n_feat:
        fails.append(f"{cond['label']}: n_detections {summary['n_detections']} "
                     f"!= geojson features {n_feat}")
    return fails


def author_board_analysis(analyses: dict, execute: bool) -> int:
    """Stage 2 (--board-analysis): compose the 55-map board analysis entry
    from the refreshed leaderboard JSON and append it."""
    if not BOARD_JSON.exists():
        print(f"BOARD JSON MISSING: {BOARD_JSON} — run the board refresh first.")
        return 1
    board = json.loads(BOARD_JSON.read_text())
    cells = board["cells"]
    tiers = board["tiers"]
    pairs = board["pairwise"]
    n_sig = sum(1 for p in pairs if p["significant"])
    cids = [c["condition_id"] for c in cells]
    uplift_cid = "55maps-text-min-n10-uplift::verified-5of10-canonical-gt"
    if uplift_cid not in cids:
        print(f"BOARD JSON STALE: {uplift_cid} not on the board — refresh first.")
        return 1
    tier_of = {n: t for t, members in enumerate(tiers, 1) for n in members}
    name_of = {c["condition_id"]: c["name"] for c in cells}
    tier1 = [c["condition_id"] for c in cells if tier_of[c["name"]] == 1]
    ladder = "; ".join(f"{c['name']} {c['f1_50']:.4f} (T{tier_of[c['name']]})"
                       for c in cells)
    entry = {
        "analysis_id": "55map-canonical-leaderboard-50m",
        "type": "leaderboard",
        "_note": ("The 55-map deployment board at the canonical 50 m working "
                  "buffer (Obs 360 derivation) vs the canonical extended GT: "
                  "the seven S105 two-reference cells + the S113 min11 uplift, "
                  f"round-robin C({len(cells)},2)={len(pairs)} tile-swap "
                  "permutation (10k, seed 42) + BH-FDR q=0.05 + greedy-clique "
                  "tiers (scripts/build_55map_leaderboard.py). Citable "
                  "write-up: results/55map-leaderboard/55map-leaderboard-50m.md "
                  "+ gs-vs-55map-transfer.md; findings SS 16."),
        "conditions_compared": cids,
        "hypothesis_refs": [],
        "preregistered": "post-hoc",
        "deviations": [],
        "predicted_outcome": (
            "S113 continuity: tiers likely become 6 with the uplift cell "
            "inserted between TM-k3 and TH7-k3 (Obs 364: both pairwise steps "
            "resolve, so the uplift should occupy its own tier on the "
            "instrument that resolves)."),
        "tie_set": tier1,
        "outcome": (f"{len(tiers)} tiers, {n_sig}/{len(pairs)} pairs "
                    f"significant after BH-FDR. Board (F1@50, tier): {ladder}. "
                    "The uplift (TM-n10-k5) confirms Obs 364 on the full "
                    "board: pass count closes about half the deployment "
                    "thinking gap — significantly above TM-k3, significantly "
                    "below TH7-k3 — making minimal-thinking deployment a "
                    "priced cost/quality trade rather than a tie."),
        "paper_section": "Results",
        "output_path": "results/55map-leaderboard",
        "working_notes_obs": [
            "Obs 358 — the 55-map 50 m board (threshold-transfer failure)",
            "Obs 362 — the deployment reversal (scope-qualifies the cost meta-rule)",
            "Obs 364 — the min11 uplift (pass count closes half the thinking gap)",
        ],
        "manually_verified_at": None,
    }
    existing = {a["analysis_id"] for a in analyses["analyses"]}
    if entry["analysis_id"] in existing:
        print(f"analysis '{entry['analysis_id']}' already exists")
        return 1
    print(f"board analysis assembled: {len(cells)} cells, {len(tiers)} tiers, "
          f"{n_sig}/{len(pairs)} sig pairs; tie_set (T1) = "
          f"{[name_of[c] for c in tier1]}")
    if not execute:
        print("\nDRY-RUN (no files written). Re-run with --execute to author.")
        return 0
    analyses["analyses"].append(entry)
    ANALYSES.write_text(json.dumps(analyses, indent=2) + "\n")
    print("Wrote run-analyses.json. Next: generate_post_run_report.py --all "
          "--write, then the drift-check.")
    return 0


def main() -> int:
    """Validate, then author the four generator inputs (dry-run by default)."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", action="store_true",
                    help="Write the sidecar files (default: dry-run).")
    ap.add_argument("--board-analysis", action="store_true",
                    help="Stage 2: author the 55-map board analysis from the "
                         "refreshed leaderboard JSON (run AFTER the board "
                         "refresh).")
    args = ap.parse_args()

    analyses = json.loads(ANALYSES.read_text())
    if args.board_analysis:
        return author_board_analysis(analyses, args.execute)

    registry = json.loads(REG.read_text())
    facts = json.loads(FACTS.read_text())
    conds = json.loads(CONDS.read_text())

    # -- assemble --------------------------------------------------------
    pvd_conds = [build_condition(label, "proposer-verifier", "verified", pool,
                                 n, vt, pt, vc, det, ev, note, None)
                 for label, pool, n, vt, pt, vc, det, ev, f1, note
                 in PVD_CONDITIONS]
    f35_conds = [build_condition(label, arch, agg, pool, n, vt, pt, vc, det,
                                 ev, None, src)
                 for label, arch, agg, pool, n, vt, pt, vc, det, ev, f1, src
                 in F35_CONDITIONS]

    # -- gates -----------------------------------------------------------
    failures = []
    for run_id in ("flash35-pv-2x2", "55maps-text-min-n10-uplift"):
        if any(e["run_id"] == run_id for e in registry["registry"]):
            failures.append(f"registry already has run '{run_id}'")
        if run_id in facts["facts"]:
            failures.append(f"run-facts already has '{run_id}'")
        if run_id in conds["decomposition"]:
            failures.append(f"run-conditions already has '{run_id}'")
    existing_pvd = {c["label"]
                    for c in conds["decomposition"]["pv-diag-384"]["conditions"]}
    for c, spec in zip(pvd_conds, PVD_CONDITIONS):
        failures.extend(gate(c, spec[8]))
        if c["label"] in existing_pvd:
            failures.append(f"pv-diag-384 already has condition '{c['label']}'")
    for c, spec in zip(f35_conds, F35_CONDITIONS):
        failures.extend(gate(c, spec[10]))
    failures.extend(gate(UPLIFT_CONDITION, UPLIFT_EXPECT_F1_50, buffer_m=50,
                         tol=UPLIFT_GATE_TOL))
    existing_ids = {a["analysis_id"] for a in analyses["analyses"]}
    for a in NEW_ANALYSES:
        if a["analysis_id"] in existing_ids:
            failures.append(f"analysis '{a['analysis_id']}' already exists")

    if failures:
        print("VALIDATION FAILURES:", flush=True)
        for f in failures:
            print(f"  - {f}", flush=True)
        return 1

    print(f"All gates pass: {len(pvd_conds)} pv-diag-384 additions, "
          f"{len(f35_conds)} flash35-pv-2x2 conditions, 1 uplift condition, "
          f"{len(NEW_ANALYSES)} analyses, 2 new runs.", flush=True)
    if not args.execute:
        print("\nDRY-RUN (no files written). Re-run with --execute to author.",
              flush=True)
        return 0

    # -- write -----------------------------------------------------------
    registry["registry"].extend([F35_REGISTRY, UPLIFT_REGISTRY])
    facts["facts"]["flash35-pv-2x2"] = F35_FACTS
    facts["facts"]["55maps-text-min-n10-uplift"] = UPLIFT_FACTS
    conds["decomposition"]["pv-diag-384"]["conditions"].extend(pvd_conds)
    conds["decomposition"]["flash35-pv-2x2"] = {
        "_note": F35_DECOMPOSITION_NOTE,
        "proposer_pools": {
            "flash35-min-text-1of10": {"modality": "text", "path": "proposer"},
            "f3-min-text-1of10": {
                "modality": "text",
                "path": "consensus/f3-min-text-1of10-with-passes.geojson"},
        },
        "verifier_passes": {
            "verified-f3vf": {"modality": "text", "path": "verified-f3vf"},
            "verified-f35vf": {"modality": "text", "path": "verified-f35vf"},
            "min-f3-verified-f35vf": {"modality": "text",
                                      "path": "min-f3-verified-f35vf"},
        },
        "conditions": f35_conds,
    }
    conds["decomposition"]["55maps-text-min-n10-uplift"] = UPLIFT_DECOMPOSITION
    analyses["analyses"].extend(NEW_ANALYSES)

    REG.write_text(json.dumps(registry, indent=2) + "\n")
    FACTS.write_text(json.dumps(facts, indent=2) + "\n")
    CONDS.write_text(json.dumps(conds, indent=2) + "\n")
    ANALYSES.write_text(json.dumps(analyses, indent=2) + "\n")
    print("Wrote run-registry.json, run-facts.json, run-conditions.json, "
          "run-analyses.json.\nNext: generate_post_run_report.py --all "
          "--write, then the drift-check; board refresh; then "
          "--board-analysis.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
