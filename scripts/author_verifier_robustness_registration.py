#!/usr/bin/env python3
# ============================================================================
# author_verifier_robustness_registration.py
# ----------------------------------------------------------------------------
# Session 111 ($0): first-class manifest registration of the verifier-
# robustness programme (Shawn-approved form, 2026-06-10: full decomposition,
# NO new champion — the carry-forward headline pv-diag-384::
# verified-adv-text-consensus-16of30 (0.890) stands).
#
# Authors, into the four hand-authored generator inputs:
#   - results/run-registry.json    : run #29 'verifier-robustness'
#   - results/run-facts.json       : its facts (scope era-2-487; two 256-scope
#                                    conditions carry scope_override)
#   - results/run-conditions.json  : 8 verifier-robustness conditions + 6
#                                    pv-diag-384 additions (the on-disk n=1
#                                    cells the S110/111 boards cite)
#   - results/run-analyses.json    : 2 leaderboard analyses
#                                    (verifier-robustness-matrix,
#                                     pass-budget-pareto)
#
# VALIDATION GATES (the script refuses to write if any fails):
#   1. every detections geojson + eval_path evaluation.json exists;
#   2. each evaluation's F1@20m (summary.buffers[3], the 20 m row) reproduces
#      the committed record to 4 d.p.;
#   3. each evaluation's n_detections equals the geojson feature count
#      (the Session-77 cross-check rule);
#   4. no condition_id collision with the existing manifest.
#
# DRY-RUN BY DEFAULT (project convention) — pass --execute to write. After
# executing, run: generate_post_run_report.py --all, then the drift-check.
#
# Usage:
#   .venv/bin/python scripts/author_verifier_robustness_registration.py
#   .venv/bin/python scripts/author_verifier_robustness_registration.py --execute
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-10 | Apache 2.0
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
EVALS = "results/verifier-robustness/evals"

# Verifier config building blocks. The instruction file and variant mirror the
# registered headline condition; iterations/consensus_rule extend the object
# (the schema leaves verifier_config free-form).
FLASH_VF = {"variant": "v1", "instruction_file": "verify_adversarial.md",
            "model": "gemini-3-flash-preview"}
PRO_VF = {"variant": "v1", "instruction_file": "verify_adversarial.md",
          "model": "gemini-3.1-pro-preview"}
SCOPE_256 = {"test_set_id": "px256-1032",
             "bounds_path": "inputs/vectors/bounds/256/full_evaluation_bounds.geojson",
             "n_test_tiles": 1032, "calibration_set_id": None,
             "n_calibration_tiles": None}


def vf(base: dict, thinking: str, temp: float, n: int, rule: str | None) -> dict:
    """Assemble a verifier_config object."""
    out = {**base, "thinking_level": thinking, "temperature": temp, "iterations": n}
    if rule:
        out["consensus_rule"] = rule
    return out


# --- the 8 verifier-robustness conditions -----------------------------------
# (label, proposer_pool, source_run, n_passes, vote_t, prob_t, verifier_config,
#  detections, expected F1@20m, scope_override)
VR_CONDITIONS = [
    ("verified-384-union-t0-0-n5", "flash-high-text-1of5", "pv-diag-384",
     5, 4, 0.15, vf(FLASH_VF, "minimal", 0.0, 5, "consensus_vt1"),
     "results/verifier-robustness/matrix-sets/min-T0.0.geojson", 0.8722, None),
    ("verified-256-union-t0-0-n5", "text-1of5", "pv-diag-256",
     5, 5, 0.15, vf(FLASH_VF, "minimal", 0.0, 5, "mean"),
     "results/verifier-robustness/condition-sets/vr-256-union-t0-0-n5.geojson",
     0.8637, SCOPE_256),
    ("verified-256-ge3of5-t0-3-n5", "text-1of5", "pv-diag-256",
     5, 5, 0.2, vf(FLASH_VF, "minimal", 0.3, 5, "consensus_vt2"),
     "results/verifier-robustness/condition-sets/vr-256-ge3of5-t0-3-n5.geojson",
     0.8582, SCOPE_256),
    ("verified-384-ge3of5-t0-3-n5", "flash-high-text-1of5", "pv-diag-384",
     5, 4, 0.15, vf(FLASH_VF, "minimal", 0.3, 5, "mean"),
     "results/verifier-robustness/matrix-sets/min-T0.3.geojson", 0.8739, None),
    ("verified-384-ge3of5-t0-7-n5", "flash-high-text-1of5", "pv-diag-384",
     5, 4, 0.2, vf(FLASH_VF, "minimal", 0.7, 5, "consensus_vt2"),
     "results/verifier-robustness/matrix-sets/min-T0.7.geojson", 0.8709, None),
    ("verified-384-ge3of5-t0-3-high-n5", "flash-high-text-1of5", "pv-diag-384",
     5, 4, 0.3, vf(FLASH_VF, "high", 0.3, 5, "consensus_vt5"),
     "results/verifier-robustness/matrix-sets/high-T0.3.geojson", 0.8764, None),
    ("verified-384-ge3of5-t0-7-high-n5", "flash-high-text-1of5", "pv-diag-384",
     5, 4, 0.4, vf(FLASH_VF, "high", 0.7, 5, "consensus_vt5"),
     "results/verifier-robustness/matrix-sets/high-T0.7.geojson", 0.8739, None),
    ("verified-384-16of30-t0-3-n5-opmax", "flash-high-text-consensus-16of30",
     "pv-diag-384", 1, None, 0.15, vf(FLASH_VF, "minimal", 0.3, 5, "consensus_vt3"),
     "results/verifier-robustness/opmax-sets/opmax-16of30-N5minT0.3-vt3-pt0.15.geojson",
     0.8951, None),
]

# --- the 6 pv-diag-384 additions ---------------------------------------------
PVD_CONDITIONS = [
    ("verified-adv-text-4of5", "flash-high-text-1of5",
     5, 4, 0.15, vf(FLASH_VF, "minimal", 0.0, 1, None),
     "results/verifier-robustness/pareto/cheap6-4of5-n1-pt0.15.geojson", 0.8641),
    ("verified-adv-text-6of10", "flash-high-text-1of10",
     10, 6, 0.2, vf(FLASH_VF, "minimal", 0.0, 1, None),
     "results/verifier-robustness/pareto/nof10-6of10-n1-pt0.2.geojson", 0.8769),
    ("verified-adv-text-high-vf-4of5", "flash-high-text-1of5",
     5, 4, 0.5, vf(FLASH_VF, "high", 0.0, 1, None),
     "results/verifier-robustness/matrix-sets/high-T0.0.geojson", 0.8519),
    ("verified-adv-text-medium-vf-4of5", "flash-high-text-1of5",
     5, 4, 0.2, vf(FLASH_VF, "medium", 0.0, 1, None),
     "results/verifier-robustness/condition-sets/medium-vf-4of5.geojson", 0.8545),
    ("verified-adv-pro-text-flash-vf-3of5", "pro-high-text-1of5",
     5, 3, 0.15, vf(FLASH_VF, "minimal", 0.0, 1, None),
     "results/verifier-robustness/condition-sets/pro-flash-vf-3of5.geojson", 0.8491),
    ("verified-adv-pro-text-pro-vf-3of5", "pro-high-text-1of5",
     5, 3, 0.15, vf(PRO_VF, "medium", 0.0, 1, None),
     "results/verifier-robustness/condition-sets/pro-pro-vf-3of5.geojson", 0.8506),
]

REGISTRY_ENTRY = {
    "run_id": "verifier-robustness",
    "directory_path": "outputs/verifier-robustness",
    "status": "active",
    "notes": ("Verifier-robustness programme (Sessions 109-110, ~$53 flex): "
              "Stage 1 N=5 determinism on the 384/256 1-of-5 unions (T=0.0), "
              "Stage 2 temperature snowball (ge3of5 band, stalled at T=0.3), "
              "Stage 3 thinking x temperature matrix + the 16of30 operational "
              "maximum. Verifier-only API run; ALL proposer pools are "
              "cross-run (pv-diag-384 / pv-diag-256, recorded per-condition "
              "via source_run). Findings: "
              "results/verifier-robustness/verifier-robustness-findings.md."),
}

FACTS_ENTRY = {
    "primary_hypothesis": "H2",
    "also_informs": ["H3"],
    "purpose": ("Verifier-robustness programme: determinism (n=1 vindicated), "
                "proposer-input band, temperature/thinking matrix, model roles, "
                "compute allocation, operational maximum, pass-budget Pareto. "
                "Meta-rule: on a within-noise tie, take the cheaper config."),
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
        "Deliberately none — NO new champion. The carry-forward headline "
        "pv-diag-384::verified-adv-text-consensus-16of30 (0.890) stands: the "
        "operational maximum here (verified-384-16of30-t0-3-n5-opmax, 0.8951) "
        "is NOT significant over it (paired tile-swap permutation p=0.363, "
        "results/verifier-robustness/opmax_vs_headline_permutation.json), so "
        "per the cost meta-rule (Obs 357) it is a numerical high only."),
    "historical_aliases": [],
    "_scope_confidence": "HIGH",
    "_scope_source": ("scripts in repo: 384 cells score against "
                      "bounds/384/full_evaluation_bounds.geojson (era-2-487); "
                      "the two 256 cells carry scope_override px256-1032"),
    "_flags": [
        "mixed tile-size run: 6 conditions at 384/487 tiles, 2 at 256/1032 (scope_override)",
        "verifier-only API run — all proposer pools cross-run (source_run per condition)",
        "S110 opmax run initially clobbered robustness_{grid,summary}_T0.3.json; "
        "repaired + re-homed to -16of30 names, --out-suffix guard added (commit 7d85b00ef)",
    ],
}

MATRIX_ANALYSIS = {
    "analysis_id": "verifier-robustness-matrix",
    "type": "leaderboard",
    "_note": ("Stage 3 of the verifier-robustness programme: thinking (minimal/high) x "
              "temperature (0.0/0.3/0.7) matrix over the 384 ge3of5 proposer band, each "
              "config at its own best F1@20m operating point. Board machinery: "
              "scripts/tier_verifier_matrix.py (round-robin tile-swap permutation, 10k, "
              "seed 42, BH-FDR q=0.05, greedy-clique tiers). Citable write-up: "
              "results/verifier-robustness/verifier-robustness-findings.md SS 8-10."),
    "conditions_compared": [
        "verifier-robustness::verified-384-union-t0-0-n5",
        "verifier-robustness::verified-384-ge3of5-t0-3-n5",
        "verifier-robustness::verified-384-ge3of5-t0-7-n5",
        "verifier-robustness::verified-384-ge3of5-t0-3-high-n5",
        "verifier-robustness::verified-384-ge3of5-t0-7-high-n5",
        "pv-diag-384::verified-adv-text-high-vf-4of5",
    ],
    "hypothesis_refs": ["H2"],
    "preregistered": "exploratory",
    "deviations": [],
    "predicted_outcome": (
        "Open robustness question (S109 carry-forward): does verifier temperature or "
        "thinking level matter once the verifier runs at N=5? The proposer-side "
        "diversity dividend (Obs 141) suggests higher temperature/thinking might add "
        "useful diversity; the Stage-2 snowball stall suggested not."),
    "tie_set": [
        "verifier-robustness::verified-384-ge3of5-t0-3-high-n5",
        "verifier-robustness::verified-384-ge3of5-t0-3-n5",
        "verifier-robustness::verified-384-ge3of5-t0-7-high-n5",
        "verifier-robustness::verified-384-union-t0-0-n5",
        "verifier-robustness::verified-384-ge3of5-t0-7-n5",
    ],
    "outcome": (
        "ALL FIVE N=5 configs are ONE statistical tier (0/10 pairs significant among "
        "them; F1@20m 0.8709-0.8764): neither temperature nor thinking moves F1 at "
        "N=5. Only the single-pass HIGH-thinking prior drops to Tier 2 (0.8519; all 5 "
        "significant pairs involve it) — high thinking HURTS a single verifier pass "
        "(min n=1 0.8659 > medium 0.8545 > high 0.8519 at the 4of5 input) and merely "
        "reaches parity under consensus, buying +0.018 MCC (0.789 vs 0.771) at ~3x "
        "cost. Aggregation refinement: a PERMISSIVE consensus (vt1 union at T=0.0, "
        "mean-probability at T=0.3) beats the expected single pass by ~+0.012; "
        "strict/unanimous voting hurts. Per the cost meta-rule the production "
        "carry-forward (minimal, T=0.0, n=1) stays optimal. Source: "
        "results/verifier-robustness/matrix_tiering.json."),
    "paper_section": "Results",
    "output_path": "results/verifier-robustness",
    "working_notes_obs": [
        "Obs 354 — verifier T=0.0 determinism negligible at F1 (n=1 vindicated)",
        "Obs 356 — higher-T consensus verifier does not help (snowball stall)",
        "Obs 357 — the cost meta-rule: on a within-noise tie, take the cheaper config",
    ],
    "manually_verified_at": None,
}

PARETO_ANALYSIS = {
    "analysis_id": "pass-budget-pareto",
    "type": "leaderboard",
    "_note": ("The passes-vs-F1@20m Pareto board for the GS 384px proposer-verifier "
              "architecture (S111): five Flash-ladder rungs from 6 to 35 total passes, "
              "each at its own best operating point, full C(5,2)=10 round-robin "
              "tile-swap permutation + BH-FDR + greedy-clique tiers "
              "(scripts/build_pareto_leaderboard.py). Includes the Shawn-flagged "
              "targeted pair: opmax (0.8951) vs the registered headline (0.8902). "
              "Citable write-up: verifier-robustness-findings.md SS 11-12 + figure "
              "results/verifier-robustness/pareto/pareto_leaderboard.png."),
    "conditions_compared": [
        "pv-diag-384::verified-adv-text-4of5",
        "verifier-robustness::verified-384-ge3of5-t0-3-n5",
        "pv-diag-384::verified-adv-text-6of10",
        "pv-diag-384::verified-adv-text-consensus-16of30",
        "verifier-robustness::verified-384-16of30-t0-3-n5-opmax",
    ],
    "hypothesis_refs": ["H2", "H3"],
    "preregistered": "exploratory",
    "deviations": [],
    "predicted_outcome": (
        "S110 continuity: adjacent pass-budget rungs are 'almost certainly NOT' "
        "significantly separated; the opmax +0.005 over the headline sits at ~1.15x "
        "the single-run SD and was flagged for a targeted permutation test rather "
        "than pre-judged."),
    "tie_set": [
        "verifier-robustness::verified-384-16of30-t0-3-n5-opmax",
        "pv-diag-384::verified-adv-text-consensus-16of30",
        "pv-diag-384::verified-adv-text-6of10",
        "verifier-robustness::verified-384-ge3of5-t0-3-n5",
        "pv-diag-384::verified-adv-text-4of5",
    ],
    "outcome": (
        "The full Flash ladder (6 -> 35 total passes; 0.8641 / 0.8739 / 0.8769 / "
        "0.8902 / 0.8951) is ONE statistical tier: 0/10 round-robin pairs significant "
        "after BH-FDR q=0.05. The targeted opmax-vs-headline pair: +0.0049, p=0.363 — "
        "verifier consensus does NOT lift the 30-pass proposer; 0.890 stays the "
        "practical ceiling. The largest span (cheap6 vs opmax35, +0.031) has raw "
        "p=0.012 but BH 0.096 — suggestive that the 30-pass rungs lead, unprovable on "
        "the 487-tile instrument (GS-plateau resolving power, Obs 347). Budget "
        "recommendation per the cost meta-rule: the 6-pass cheap end (0.8641) is "
        "~97% of the numerical maximum at ~17% of the pass budget. Sources: "
        "results/verifier-robustness/pareto/pareto_leaderboard.json, "
        "results/verifier-robustness/opmax_vs_headline_permutation.json."),
    "paper_section": "Results",
    "output_path": "results/verifier-robustness/pareto",
    "working_notes_obs": [
        "Obs 357 — the cost meta-rule: on a within-noise tie, take the cheaper config",
        "Obs 347 — GS-plateau resolving-power heuristics (invoked by the span caveat)",
    ],
    "manually_verified_at": None,
}


def build_condition(label: str, pool: str, n_passes: int, vote_t, prob_t,
                    vconf: dict, detections: str, source_run: str | None,
                    scope_override: dict | None) -> dict:
    """Assemble one run-conditions sidecar entry."""
    cond = {
        "label": label,
        "architecture": "proposer-verifier",
        "aggregation": "verified",
        "proposer_pool": pool,
        "n_passes": n_passes,
        "vote_threshold": vote_t,
        "prob_threshold": prob_t,
        "verifier_config": vconf,
        "eval_path": f"{EVALS}/{label}/evaluation.json",
        "detections": detections,
    }
    if source_run:
        cond["source_run"] = source_run
    if scope_override:
        cond["scope_override"] = scope_override
    return cond


def gate(cond: dict, expect_f1: float) -> list[str]:
    """Validate one condition's artefacts; return a list of failures."""
    fails = []
    det = BASE_DIR / cond["detections"]
    ev = BASE_DIR / cond["eval_path"]
    if not det.exists():
        return [f"{cond['label']}: detections MISSING ({cond['detections']})"]
    if not ev.exists():
        return [f"{cond['label']}: evaluation MISSING ({cond['eval_path']})"]
    n_feat = len(json.loads(det.read_text())["features"])
    summary = json.loads(ev.read_text())["summary"]
    b20 = next(b for b in summary["buffers"] if b["buffer_metres"] == 20)
    if round(b20["f1"], 4) != expect_f1:
        fails.append(f"{cond['label']}: eval F1@20m {b20['f1']:.4f} != {expect_f1}")
    if summary["n_detections"] != n_feat:
        fails.append(f"{cond['label']}: n_detections {summary['n_detections']} "
                     f"!= geojson features {n_feat}")
    return fails


def main() -> int:
    """Validate, then author the four generator inputs (dry-run by default)."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", action="store_true",
                    help="Write the four sidecar files (default: dry-run).")
    args = ap.parse_args()

    registry = json.loads(REG.read_text())
    facts = json.loads(FACTS.read_text())
    conds = json.loads(CONDS.read_text())
    analyses = json.loads(ANALYSES.read_text())

    # -- assemble ------------------------------------------------------------
    vr_conds = [build_condition(label, pool, n, vt, pt, vc, det, src, scope)
                for label, pool, src, n, vt, pt, vc, det, f1, scope in VR_CONDITIONS]
    pvd_conds = [build_condition(label, pool, n, vt, pt, vc, det, None, None)
                 for label, pool, n, vt, pt, vc, det, f1 in PVD_CONDITIONS]

    # -- gates ---------------------------------------------------------------
    failures = []
    if any(e["run_id"] == "verifier-robustness" for e in registry["registry"]):
        failures.append("registry already has run 'verifier-robustness'")
    if "verifier-robustness" in facts["facts"]:
        failures.append("run-facts already has 'verifier-robustness'")
    existing_pvd = {c["label"] for c in conds["decomposition"]["pv-diag-384"]["conditions"]}
    for c, spec in zip(vr_conds, VR_CONDITIONS):
        failures.extend(gate(c, spec[8]))  # expected F1 (10-tuple: ..., f1, scope)
    for c, spec in zip(pvd_conds, PVD_CONDITIONS):
        failures.extend(gate(c, spec[7]))  # expected F1 (8-tuple: ..., f1)
    for c in pvd_conds:
        if c["label"] in existing_pvd:
            failures.append(f"pv-diag-384 already has condition '{c['label']}'")
    existing_ids = {a["analysis_id"] for a in analyses["analyses"]}
    for a in (MATRIX_ANALYSIS, PARETO_ANALYSIS):
        if a["analysis_id"] in existing_ids:
            failures.append(f"analysis '{a['analysis_id']}' already exists")

    if failures:
        print("VALIDATION FAILURES:", flush=True)
        for f in failures:
            print(f"  - {f}", flush=True)
        return 1

    print(f"All gates pass: {len(vr_conds)} verifier-robustness conditions, "
          f"{len(pvd_conds)} pv-diag-384 additions, 2 analyses.", flush=True)
    if not args.execute:
        print("\nDRY-RUN (no files written). Re-run with --execute to author.",
              flush=True)
        return 0

    # -- write ---------------------------------------------------------------
    registry["registry"].append(REGISTRY_ENTRY)
    facts["facts"]["verifier-robustness"] = FACTS_ENTRY
    conds["decomposition"]["verifier-robustness"] = {
        "_note": ("Verifier-only run: re-verifies pv-diag-384 / pv-diag-256 proposer "
                  "pools under varied verifier configs (S109-110). One citable "
                  "condition per verifier config at its best F1@20m operating point "
                  "(the settled decomposition pattern); the full sweeps live in "
                  "results/verifier-robustness/robustness_grid_*.json. NO new "
                  "champion (see run-facts headline_rationale)."),
        "proposer_pools": {},
        "verifier_passes": {
            "384-union-t0-0": {"modality": "text", "path": "384-flash-high-text-1of5-union/T0.0"},
            "256-union-t0-0": {"modality": "text", "path": "256-text-1of5-union/T0.0"},
            "384-ge3of5-t0-3": {"modality": "text", "path": "384-flash-high-text-ge3of5/T0.3"},
            "256-ge3of5-t0-3": {"modality": "text", "path": "256-text-ge3of5/T0.3"},
            "384-ge3of5-t0-7": {"modality": "text", "path": "384-flash-high-text-ge3of5/T0.7"},
            "384-ge3of5-t0-3-high": {"modality": "text",
                                     "path": "384-flash-high-text-ge3of5/T0.3-high"},
            "384-ge3of5-t0-7-high": {"modality": "text",
                                     "path": "384-flash-high-text-ge3of5/T0.7-high"},
            "384-16of30-t0-3": {"modality": "text", "path": "384-flash-high-text-16of30/T0.3"},
        },
        "conditions": vr_conds,
    }
    conds["decomposition"]["pv-diag-384"]["conditions"].extend(pvd_conds)
    analyses["analyses"].extend([MATRIX_ANALYSIS, PARETO_ANALYSIS])

    REG.write_text(json.dumps(registry, indent=2) + "\n")
    FACTS.write_text(json.dumps(facts, indent=2) + "\n")
    CONDS.write_text(json.dumps(conds, indent=2) + "\n")
    ANALYSES.write_text(json.dumps(analyses, indent=2) + "\n")
    print("Wrote run-registry.json, run-facts.json, run-conditions.json, "
          "run-analyses.json.\nNext: scripts/generate_post_run_report.py --all, "
          "then the drift-check.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
