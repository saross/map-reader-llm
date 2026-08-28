#!/usr/bin/env python3
"""
Registration Pass 3: the image campaign and the H7 escalation.

Adds two runs, four conditions, three analyses (unsigned), and two
facts entries:

- `image-b-gs-2026-08-28`: image-MINIMAL and image-HIGH proposer pools
  (K = 10 each) + their union verifications; conditions = the two
  verified best cells; analyses = the modality head-to-head (IP1–IP5)
  and the thinking pair (HP1–HP5), both registered-by-commit.
- `h7-escalation-2026-08-28`: the T=1.6 / T=2.0 pools (3 replicates
  each); conditions = the two replicate-mean cells (phase2b grain);
  analysis = the escalation discharge (registered-exploratory — the
  preregistration's own trigger clause names it exploratory).

Refusal-gated; every artefact path existence-checked.

Usage::

    python scripts/register_pass3_author.py [--write]

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

VF_CONFIG = {
    "variant": "v1",
    "instruction_file": "verify_adversarial.md",
    "model": "gemini-3-flash-preview",
    "thinking_level": "minimal",
    "temperature": 0.0,
}
IB = "image-b-gs-2026-08-28"
H7 = "h7-escalation-2026-08-28"
CARD = "planning/image-b-gs-2026-08-28.md"

REGISTRY_ROWS = [
    {"run_id": IB, "directory_path": "outputs/image-b-gs-2026-08-28",
     "status": "active",
     "notes": ("Image on the leading geometry (card " + CARD + "): "
               "MINIMAL and HIGH cells, K=10 each on the text-B GS "
               "tiling, explicit context caching; pricing probes in "
               "probe/ and probe-high/. Registered S143 (Pass 3).")},
    {"run_id": H7, "directory_path": "outputs/h7-escalation-2026-08-28",
     "status": "active",
     "notes": ("H7 temperature-escalation discharge (prereg osf:731; "
               "card planning/run-predictions/h7-escalation-t1.6.md): "
               "T=1.6 and T=2.0, three replicates each, era-1-340. "
               "Registered S143 (Pass 3).")},
]

DECOMPOSITIONS = {
    IB: {
        "_note": ("Both cells byte-matched to the committed text-B "
                  "anchor except the declared bundles (modality; one "
                  "thinking flag). Predictions IP1-IP5 and HP1-HP5 "
                  "registered by commit before each launch (card "
                  + CARD + "). Findings: results/image-b-gs-2026-08-28/"
                  "findings.md."),
        "proposer_pools": {
            "g384_ov192_image": {"modality": "image",
                                 "path": "g384_ov192_image"},
            "g384_ov192_image_high": {"modality": "image",
                                      "path": "g384_ov192_image_high"},
        },
        "verifier_passes": {
            "g384_ov192_image-union-k10-verify":
                {"modality": "text",
                 "path": "verifier/g384_ov192_image/verify"},
            "g384_ov192_image_high-union-k10-verify":
                {"modality": "text",
                 "path": "verifier/g384_ov192_image_high/verify"},
        },
        "conditions": [
            {"label": "g384-ov192-image-min-k10-verified-p0.15-k9",
             "architecture": "proposer-verifier",
             "aggregation": "verified",
             "proposer_pool": "g384_ov192_image",
             "n_passes": 10, "vote_threshold": 9, "prob_threshold": 0.15,
             "verifier_config": dict(VF_CONFIG),
             "eval_path": "results/image-b-gs-2026-08-28/best-eval/"
                          "evaluation.json",
             "detections": "results/image-b-gs-2026-08-28/"
                           "verified_best_20m.geojson",
             "_note": ("Image-MINIMAL verified best (F1@20 0.8412, "
                       "tile-MCC 0.7985; union 4,065). Text beats it "
                       "+0.0549 @20m p=0.0010 with MCC parity — the "
                       "modality verdict (IP1-IP4 confirmed).")},
            {"label": "g384-ov192-image-high-k10-verified-p0.20-k8",
             "architecture": "proposer-verifier",
             "aggregation": "verified",
             "proposer_pool": "g384_ov192_image_high",
             "n_passes": 10, "vote_threshold": 8, "prob_threshold": 0.20,
             "verifier_config": dict(VF_CONFIG),
             "eval_path": "results/image-b-gs-2026-08-28/high/best-eval/"
                          "evaluation.json",
             "detections": "results/image-b-gs-2026-08-28/high/"
                           "verified_best_20m.geojson",
             "_note": ("Image-HIGH verified best (F1@20 0.8333; union "
                       "9,189, +126% over MINIMAL). HP1 confirmed: the "
                       "verifier absorbs the thinking dividend "
                       "(-0.0079 vs MINIMAL, p=0.62, at 2.91x cost).")},
        ],
    },
    H7: {
        "_note": ("Discharges the fired H7 escalation trigger at the "
                  "letter (both registered levels; PI-approved "
                  "2026-08-28; ~$1.37 flex). Replication gate: the "
                  "committed T1.0-vs-T1.3 check reproduced exactly "
                  "before any new comparison. Outcome recorded in the "
                  "prediction card and the hypothesis ledger."),
        "proposer_pools": {
            "T1.6": {"modality": "text", "path": "T1.6"},
            "T2.0": {"modality": "text", "path": "T2.0"},
        },
        "verifier_passes": {},
        "conditions": [
            {"label": "text-t1.6",
             "architecture": "single-pass", "aggregation": "none",
             "proposer_pool": "T1.6",
             "n_passes": 3, "vote_threshold": None,
             "prob_threshold": None, "verifier_config": None,
             "eval_path": "results/h7-escalation-2026-08-28/eval-T16/"
                          "evaluation.json",
             "detections": "outputs/h7-escalation-2026-08-28/T1.6",
             "_note": ("Replicate-mean F1@20 ~0.474 (phase2b grain); "
                       "per-run 0.4806/0.4884/0.4524, all below their "
                       "T=1.3 counterparts.")},
            {"label": "text-t2.0",
             "architecture": "single-pass", "aggregation": "none",
             "proposer_pool": "T2.0",
             "n_passes": 3, "vote_threshold": None,
             "prob_threshold": None, "verifier_config": None,
             "eval_path": "results/h7-escalation-2026-08-28/eval-T20/"
                          "evaluation.json",
             "detections": "outputs/h7-escalation-2026-08-28/T2.0",
             "_note": ("Replicate-mean F1@20 ~0.474; per-run 0.4752/"
                       "0.4714/0.4765, all significantly below T=1.3 "
                       "(p=0.0013-0.0064). The degraded plateau.")},
        ],
    },
}

FACTS = {
    IB: {
        "primary_hypothesis": None, "also_informs": ["H1"],
        "purpose": ("Image variant of the leading configuration on the "
                    "GS corpus: the modality head-to-head under matched "
                    "everything (vs the committed text-B anchor), plus "
                    "the first matched MINIMAL-vs-HIGH image thinking "
                    "pair. Card " + CARD + "."),
        "tile_size_px": 384, "corpus": "4-map-gs",
        "gt_reference": "curator",
        "scope": {"test_set_id": "grid-common-487",
                  "bounds_path": "outputs/grid-2026-08-18/scoring/bounds/"
                                 "grid_common_bounds.geojson",
                  "n_test_tiles": 487, "calibration_set_id": None,
                  "n_calibration_tiles": None},
        "headline_condition_id":
            f"{IB}::g384-ov192-image-min-k10-verified-p0.15-k9",
        "headline_rationale": ("The modality comparison's image side at "
                               "MINIMAL — the like-for-like cell the "
                               "paper claim rests on."),
        "historical_aliases": [], "_scope_confidence": "HIGH",
        "_scope_source": "empirical",
        "_flags": ["Explicit context caching (~94% of input tokens); "
                   "live estimator over-records ~3.3x on cached tokens "
                   "— audited basis in the card and findings."],
    },
    H7: {
        "primary_hypothesis": "H7", "also_informs": [],
        "purpose": ("Discharge of the H7 temperature-escalation trigger "
                    "(osf:731): T=1.6 and T=2.0 at the optimal "
                    "configuration, characterising the upper bound of "
                    "the temperature-performance curve."),
        "tile_size_px": 512, "corpus": "4-map-gs",
        "gt_reference": "curator",
        "scope": {"test_set_id": "era-1-340",
                  "bounds_path": "inputs/vectors/bounds/"
                                 "full_evaluation_bounds.geojson",
                  "n_test_tiles": 340, "calibration_set_id": None,
                  "n_calibration_tiles": None},
        "headline_condition_id": f"{H7}::text-t1.6",
        "headline_rationale": ("The first registered escalation level; "
                               "the monotone-decline verdict."),
        "historical_aliases": [], "_scope_confidence": "HIGH",
        "_scope_source": "empirical",
        "_flags": ["Real-time flex where the registered H7 ran Batch "
                   "API — both bill 50% of list; execution "
                   "infrastructure, not a parameter."],
    },
}

ANALYSES = [
    {
        "analysis_id": "image-b-modality-2026-08-28",
        "type": "comparison",
        "_note": ("The modality head-to-head on the leading "
                  "configuration (scripts/image_b_analysis.py): join + "
                  "reassignment gates; anchor gate (text-B re-scored "
                  "through the analysis path reproduces its registered "
                  "0.8961 exactly); full sweep at 20 m; buffer curves; "
                  "board-chain paired tile-swap (10k/seed 42, 487-tile "
                  "common footprint); first-N ladder with inherited "
                  "verification. Findings: results/image-b-gs-2026-08-28/"
                  "findings.md."),
        "_prereg_rationale": ("Predictions IP1-IP5 registered by commit "
                              "before launch (card " + CARD + " § 3)."),
        "conditions_compared": [
            f"{IB}::g384-ov192-image-min-k10-verified-p0.15-k9",
            "grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10",
        ],
        "hypothesis_refs": ["H1"],
        "preregistered": "registered-exploratory",
        "deviations": [],
        "predicted_outcome": ("IP1 text > image at <=30m; IP2 gap "
                              "narrows monotonically to 75m; IP3 MCC "
                              "within ±0.02; IP4 prob in {0.15,0.20}; "
                              "IP5 image saturates slower."),
        "outcome": ("IP1-IP4 CONFIRMED (text +0.0549 @20m p=0.0010; "
                    "gap 0.0549->0.0258; MCC 0.7985 vs 0.7965; prob "
                    "0.15). IP5 indeterminate at GS power (N3-N10 "
                    "-0.0159 p=0.069 — the GS indeterminate zone per "
                    "the sensitivity appendix). Image N=1 collapses "
                    "(0.6974); needs near-unanimity consensus. "
                    "Obs 439."),
        "paper_section": "Results",
        "output_path": "results/image-b-gs-2026-08-28/analysis.json",
        "working_notes_obs": [
            "Obs 439 — image campaign: text stronger for localisation "
            "with MCC parity; the verifier absorbs the thinking "
            "dividend on the image track"],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "image-b-thinking-pair-2026-08-28",
        "type": "comparison",
        "_note": ("The first matched MINIMAL-vs-HIGH image pair "
                  "(scripts/image_b_pair.py; one CLI flag differs): "
                  "paired tile-swap at verified bests, union growth, "
                  "MCC delta, lattice check, audited-rate cost "
                  "reconciliation. Card § 5a records the outcome and "
                  "the probe's thinking-volume under-estimate "
                  "correction ($59.07 audited proposer, not ~$37)."),
        "_prereg_rationale": ("Predictions HP1-HP5 registered at "
                              "approval (card " + CARD + " § 5a)."),
        "conditions_compared": [
            f"{IB}::g384-ov192-image-min-k10-verified-p0.15-k9",
            f"{IB}::g384-ov192-image-high-k10-verified-p0.20-k8",
        ],
        "hypothesis_refs": ["H1"],
        "preregistered": "registered-exploratory",
        "deviations": [],
        "predicted_outcome": ("HP1 HIGH~MIN within 0.03 at verified "
                              "best; HP2 union >=+20%; HP3 MCC ±0.02; "
                              "HP4 lattice; HP5 cost 3.0-3.5x."),
        "outcome": ("HP1-HP4 CONFIRMED (HIGH -0.0079 p=0.62; union "
                    "+126%; MCC +0.0008; (0.20,k8)); HP5 narrow miss "
                    "(2.91x). The verifier absorbs the thinking "
                    "dividend — the S111/Obs 359 recall-ceiling "
                    "mechanism reproduced on the image track. "
                    "Obs 439."),
        "paper_section": "Results",
        "output_path": "results/image-b-gs-2026-08-28/high/"
                       "pair_verdicts.json",
        "working_notes_obs": [
            "Obs 439 — image campaign: text stronger for localisation "
            "with MCC parity; the verifier absorbs the thinking "
            "dividend on the image track"],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "h7-escalation-2026-08-28",
        "type": "comparison",
        "_note": ("Discharge of the fired H7 escalation trigger at the "
                  "letter (both registered levels; the prediction card "
                  "planning/run-predictions/h7-escalation-t1.6.md "
                  "committed 2026-07-28, outcome recorded 2026-08-28). "
                  "Replication gate: the committed T1.0-vs-T1.3 check "
                  "reproduced exactly (dF1 -0.036229, p=0.247, 340 "
                  "tiles) before any new comparison. Instrument: "
                  "pairwise_permutation_test.py, same-replicate "
                  "pairing, era-1-340 frame."),
        "_prereg_rationale": ("The preregistration's own trigger clause "
                              "(osf:731) names this exploratory testing "
                              "— registered-exploratory."),
        "conditions_compared": [
            f"{H7}::text-t1.6", f"{H7}::text-t2.0",
            "retest-phase2b::text-t1.3", "retest-phase2b::text-t1.0",
        ],
        "hypothesis_refs": ["H7"],
        "preregistered": "registered-exploratory",
        "deviations": ["Era-1 340-tile corpus per E36 (registered H7 "
                       "ran the 60-tile holdout); real-time flex vs "
                       "Batch (both 50% of list)."],
        "predicted_outcome": ("Card: T=1.6 below T=1.3 (0.50-0.54), "
                              "differences ns, precision falls faster "
                              "than recall."),
        "outcome": ("Primary CONFIRMED and exceeded (T=1.6 0.452-0.488, "
                    "below the predicted band's floor); secondary WRONG "
                    "informatively (five of six comparisons significant, "
                    "p=0.0002-0.0064 — the curve separates at 1.6 as no "
                    "adjacent pair below did); tertiary confirmed. "
                    "Degraded plateau ~0.47 at 1.6-2.0; no benefit "
                    "above the vendor default; obligation discharged. "
                    "Obs 440."),
        "paper_section": "Appendix",
        "output_path": "results/h7-escalation-2026-08-28",
        "working_notes_obs": [
            "Obs 440 — the preregistration compliance audit: believe "
            "the artefacts; the last obligation discharged with data"],
        "manually_verified_at": None,
    },
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    rc = json.loads((REPO / "results/run-conditions.json").read_text())
    rr = json.loads((REPO / "results/run-registry.json").read_text())
    rf = json.loads((REPO / "results/run-facts.json").read_text())
    ra = json.loads((REPO / "results/run-analyses.json").read_text())
    for key in DECOMPOSITIONS:
        if key in rc["decomposition"] or key in rf["facts"] or any(
                r["run_id"] == key for r in rr["registry"]):
            raise SystemExit(f"REFUSED: {key} already registered")
    for a in ANALYSES:
        if a["analysis_id"] in {r["analysis_id"] for r in ra["analyses"]}:
            raise SystemExit(f"REFUSED: {a['analysis_id']} exists")
    missing = []
    for key, d in DECOMPOSITIONS.items():
        run_dir = REPO / dict((r["run_id"], r["directory_path"])
                              for r in REGISTRY_ROWS)[key]
        for c in d["conditions"]:
            for f in ("eval_path", "detections"):
                if not (REPO / c[f]).exists():
                    missing.append(c[f])
        for _, spec in {**d["proposer_pools"],
                        **d["verifier_passes"]}.items():
            if not (run_dir / spec["path"]).exists():
                missing.append(str((run_dir / spec["path"])
                                   .relative_to(REPO)))
    if missing:
        raise SystemExit("REFUSED — missing artefacts:\n  "
                         + "\n  ".join(missing))
    n_c = sum(len(d["conditions"]) for d in DECOMPOSITIONS.values())
    print(f"2 runs, {n_c} conditions, {len(ANALYSES)} analyses; "
          "artefacts verified.")
    if not args.write:
        print("dry run — re-run with --write")
        return 0
    rc["decomposition"].update(DECOMPOSITIONS)
    rr["registry"].extend(REGISTRY_ROWS)
    rf["facts"].update(FACTS)
    ra["analyses"].extend(ANALYSES)
    (REPO / "results/run-conditions.json").write_text(
        json.dumps(rc, indent=1) + "\n")
    (REPO / "results/run-registry.json").write_text(
        json.dumps(rr, indent=1) + "\n")
    (REPO / "results/run-facts.json").write_text(
        json.dumps(rf, indent=1) + "\n")
    (REPO / "results/run-analyses.json").write_text(
        json.dumps(ra, indent=1) + "\n")
    print("WRITTEN — regenerate manifests next")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
