#!/usr/bin/env python3
"""
Register the Gemini 3.7 arc and the Gemini 3.8 Arm V cell.

Authors the rows agreed in ``planning/gemini37-register-rows-proposal-2026-09-03.md``
as amended by the Principal Investigator's (PI) rulings of 2026-09-06, into the four
hand-authored generator inputs:

- ``results/run-registry.json``  : three new runs (screen, 55-map, image-GS).
- ``results/run-facts.json``     : their facts.
- ``results/run-conditions.json``: three new decompositions plus additions to the two
  existing decompositions that own the fourth cell's proposer pools
  (``grid-2026-08-18``; ``stride-55map-2026-08-25``), per PI ruling 6.
- ``results/run-analyses.json``  : six analysis rows (R1-R5 of the proposal plus the
  Gemini 3.8 Arm V verifier-seat row).

PI rulings applied (2026-09-06)
-------------------------------
1. ``preregistered`` is ``post-hoc`` on every 3.7/3.8 analysis row; each campaign
   card's pre-commitments are quoted verbatim (with file:line) in
   ``predicted_outcome``.
2. The image row carries ``hypothesis_refs: ["H1"]``.
3. Both 55-map chains are registered per cell (``-canonical-gt`` /
   ``-standardised-gt``). The canonical B N = 5 incumbent companion row is
   **NOT** authored: see ``CANONICAL_BN5_GAP`` below — no canonical evaluation with a
   tile confusion matrix exists on disk for that cell, and the conditions schema
   requires integer ``tp``/``tn``/``fp``/``fn``. The gap is recorded in R2's outcome.
4. Tier B (oracles, the N = 1 / N = 3 rungs, and the Gold Standard (GS) ladder rungs
   A4-A6) is deferred to the r2 recompute chain
   (``planning/reference-revision-2026-09-06.md``); the analysis rows describe those
   rungs as "re-derived; registration pending materialisation".
5. The image-GS cells (A7, A8) register: the unmet escalation trigger governed spend,
   not registration.
6. Fourth-cell conditions live under the runs that own the proposer pools.
7. A1, A2, A3, A7, A8, A9 register now; A4-A6 defer with the other rungs.
8. The H14 / H15 dispositions are untouched.
9. The 3.8 Arm V cell registers as a GS condition under ``gemini37-screen-2026-08-28``
   (it re-verifies that run's K = 5 union), plus one analysis row.

Canonical-chain adapter
-----------------------
The three canonical 55-map cells are scored by the corrected-F1 engine, which writes
``summary.json`` rather than the generator-shape ``evaluation.json``. This script
applies the same deterministic transform ``scripts/register_pass1_adapt.py`` used for
the Pass-1 stride-55map cells: nothing is recomputed, the tile classification is
pinned to the 50 m headline row, and the Confidence Interval (CI) method is recorded
as ``percentile`` because that is what the engine produces.

Validation gates (the script refuses to write if any fails)
-----------------------------------------------------------
1. No run / condition / analysis identifier collides with the existing register.
2. Every ``eval_path``, ``detections`` path, proposer-pool directory and verifier-pass
   directory named below exists on disk.
3. Every condition's evaluation reproduces its committed F1 at its gate buffer.
4. Every condition's ``summary.n_detections`` equals its GeoJSON feature count (the
   Session-77 cross-check rule).

Dry run by default (project convention) — pass ``--write`` to author. After writing::

    python scripts/generate_post_run_report.py --all --write

Usage::

    python scripts/register_gemini37_author.py
    python scripts/register_gemini37_author.py --write

Created: 2026-09-06 (Session 149)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------- #
# Identifiers
# --------------------------------------------------------------------------- #

SCREEN = "gemini37-screen-2026-08-28"
M55 = "gemini37-55map-2026-08-29"
IMG = "gemini37-image-gs-2026-09-01"
GRID = "grid-2026-08-18"          # existing — owns the fourth cell's GS proposer pool
STRIDE = "stride-55map-2026-08-25"  # existing — owns the fourth cell's 55-map pool

CARD_SCREEN = "planning/gemini37-screen-2026-08-28.md"
CARD_55MAP = "planning/gemini37-55map-2026-08-29.md"
CARD_IMAGE = "planning/gemini37-image-gs-2026-08-30.md"
CARD_38 = "planning/gemini38-screen-2026-09-04.md"

# --------------------------------------------------------------------------- #
# Verifier configurations — read from configuration.{model,thinking_level,
# temperature} of every verify*/run.meta.json under the trees named below. All three
# share system_instruction_hash 2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25…
# --------------------------------------------------------------------------- #

VF_G3 = {"variant": "v1", "instruction_file": "verify_adversarial.md",
         "model": "gemini-3-flash-preview", "thinking_level": "minimal",
         "temperature": 0.0, "iterations": 1}
VF_37 = {"variant": "v1", "instruction_file": "verify_adversarial.md",
         "model": "gemini-3.7-flash", "thinking_level": "low",
         "temperature": 0.0, "iterations": 1}
VF_38 = {"variant": "v1", "instruction_file": "verify_adversarial.md",
         "model": "gemini-3.8-flash", "thinking_level": "low",
         "temperature": 0.0, "iterations": 1}

# --------------------------------------------------------------------------- #
# Canonical-chain adapter inputs: (eval_dir, detections) relative to the repository.
# --------------------------------------------------------------------------- #

CANONICAL_CELLS = [
    ("results/gemini37-55map-2026-08-31/arm1/g384_ov192_55map_g37/primary/eval",
     "results/gemini37-55map-2026-08-31/arm1/g384_ov192_55map_g37/primary/"
     "verified_detections.geojson"),
    ("results/gemini37-55map-2026-08-31/arm2/g384_ov192_55map_g37/primary/eval",
     "results/gemini37-55map-2026-08-31/arm2/g384_ov192_55map_g37/primary/"
     "verified_detections.geojson"),
    ("results/gemini37-fourth-cell/55map/g384_ov192_55map/primary/eval",
     "results/gemini37-fourth-cell/55map/g384_ov192_55map/primary/"
     "verified_detections.geojson"),
]
HEADLINE_BUFFER_M = 50

#: The one PI-ruled row this script cannot author. The arm-2 / D1 comparator — the
#: Gemini-3 B first-5 union under the Gemini-3 verifier at its carried (0.15, k5)
#: point — has a committed canonical corrected-F1@50 of 0.8437752627324171
#: (``results/stride55-2026-08-27/ladder.json`` → runs.g384_ov192_55map.N.5.carried;
#: reproduced in ``results/gemini37-55map-2026-08-31/sweeps/sweep_oracle.json`` →
#: incumbents.BN5) and 4,736 materialised detections
#: (``results/55map-final-board-2026-08-27/cells/B-N5-carried/detections.geojson``),
#: but NO canonical evaluation with a tile confusion matrix: the ladder records
#: detection-level tp/fp/fn only (4175 / 561 / 985), and the conditions schema
#: requires integer tile-level tp/tn/fp/fn. Its standardised sibling
#: ``stride-55map-2026-08-25::g384-ov192-55map-n5-carried-p0.15-k5-standardised-gt``
#: IS registered and carries a tile matrix; borrowing it would assert a
#: cross-instrument identity that holds on four other cells but has not been measured
#: on this one, so it is not borrowed. Recorded in R2's outcome instead; the canonical
#: scoring belongs to the r2 recompute chain.
CANONICAL_BN5_GAP = (
    "canonical B N=5 incumbent: F1@50 0.8437752627324171 committed, no tile matrix"
)

# --------------------------------------------------------------------------- #
# Run registry rows
# --------------------------------------------------------------------------- #

REGISTRY_ROWS = [
    {"run_id": SCREEN, "directory_path": "outputs/gemini37-screen-2026-08-28",
     "status": "active",
     "notes": ("Gemini 3.7 Flash GS screen (card " + CARD_SCREEN + "; predictions "
               "G1-G4 committed at PI go): detect_brief-text on the leading 384/50% "
               "geometry, K=5 then an approved escalation to K=10, plus two "
               "verifier-role swaps over the same K=5 union (gemini-3.7-flash, and "
               "gemini-3.8-flash under card " + CARD_38 + "). Registered S149.")},
    {"run_id": M55, "directory_path": "outputs/gemini37-55map-2026-08-29",
     "status": "active",
     "notes": ("Gemini 3.7 Flash 55-map deployment arms (card " + CARD_55MAP + "; "
               "predictions D1-D7 committed before any deployment scoring): one K=5 "
               "proposer pool, two verifier arms (carried Gemini-3; all-3.7). "
               "Results tree is results/gemini37-55map-2026-08-31/ — the "
               "run-directory/results-directory skew is deliberate and "
               "directory_path carries the truth. Registered S149.")},
    {"run_id": IMG, "directory_path": "outputs/gemini37-image-gs-2026-09-01",
     "status": "active",
     "notes": ("Gemini 3.7 Flash image-GS screen (card " + CARD_IMAGE + "; "
               "predictions I1-I5 committed at PI go): detect_brief-text-image on "
               "the same geometry and reference as the text screen, two verifier "
               "arms. The escalation trigger was NOT met and no 55-map image "
               "extension followed; the negative decision is itself the registered "
               "outcome. Registered S149.")},
]

# --------------------------------------------------------------------------- #
# Decompositions — new runs
# --------------------------------------------------------------------------- #

_SCREEN_NOTE = (
    "GS screen on the 487-tile common footprint, curator reference, 20 m primary. "
    "The proposer config is the committed text-B anchor's detect_brief-text, "
    "byte-identical but for two command-line overrides (--model gemini-3.7-flash "
    "--thinking-level low). Four verifier passes over two unions: verify (K=5, 791 "
    "candidates) and verify_k10 (K=10, 913) with the carried gemini-3-flash-preview "
    "verifier; verify_swap37 and verify_swap38 re-verify the SAME 791-candidate K=5 "
    "union with gemini-3.7-flash and gemini-3.8-flash. Disclosed deviation (card "
    + CARD_SCREEN + " changelog): the K=10 escalation re-verified the FULL union "
    "rather than increment-stitching the new candidates. GOTCHA: these are TEXT "
    "cells whose best operating point sits under the JSON key 'image_best' — the "
    "campaign reused scripts/image_b_analysis.py; the key name is not a modality "
    "claim. The N=1/3/5 ladder rungs in k10/analysis.json are NOT registered (no "
    "materialised detections; deferred to the r2 recompute chain per PI ruling 4)."
)

_IMG_NOTE = (
    "Image variant of the 3.7 GS screen on the same geometry, footprint and "
    "reference (detect_brief-text-image; K=5; 674-candidate union). Two verifier "
    "arms over that one union: arm 1 the carried gemini-3-flash-preview, arm 2 "
    "gemini-3.7-flash. GOTCHA: scripts/image_b_analysis.py:79 hard-codes "
    "ANCHOR_F1_20 = 0.8961, so the built-in head_to_head_20m blocks in "
    "arm{1,2}/analysis.json pair a 3.7 IMAGE cell against a GEMINI-3 TEXT cell and "
    "mix the family step into the modality contrast — never quote them as a "
    "modality delta; results/gemini37-image-gs-2026-09-01/gap_test.json is the "
    "instrument. Both arms' sweep argmaxes are ties the analysis JSON does not "
    "flag (arm 2: prob_t 0.90 and 0.95 give identical F1 0.9308323563892146 and 425 "
    "detections in arm2/sweep_20m.csv)."
)

_M55_NOTE = (
    "55-map deployment arms for the Gemini 3.7 proposer (card " + CARD_55MAP + "). "
    "One K=5 proposer pool (union 12,715 candidates), two verifier arms over it, "
    "both carried operating points committed on the card at :140-141 before any "
    "deployment scoring. TWO INSTRUMENTS, one row each per cell (Obs 444 § (b); "
    "results/gemini37-55map-2026-08-31/findings.md § 'Reference instruments'): the "
    "canonical adjudicated extended Ground Truth (5,160 references at 50 m, "
    "corrected-F1 engine, the campaign's committed primary) and the ruling-21 "
    "standardised reference inputs/vectors/references/best-available-gt-55maps.geojson "
    "(5,010 references, scripts/evaluate_detections.py). The canonical eval_paths "
    "point at evaluation.json files written by this script's adapter from the "
    "engine's summary.json (deterministic transform; nothing recomputed). Nothing "
    "here is scored against the r2 reference. The 16-cell grid board's oracle and "
    "N=1/N=3 rungs are NOT registered (no materialised detections or evaluations; "
    "deferred to the r2 recompute chain per PI ruling 4)."
)

DECOMPOSITIONS = {
    SCREEN: {
        "_note": _SCREEN_NOTE,
        "proposer_pools": {
            "g384_ov192_g37": {"modality": "text", "path": "g384_ov192_g37"},
        },
        "verifier_passes": {
            "g384_ov192_g37-union-k5-verify":
                {"modality": "text", "path": "verifier/g384_ov192_g37/verify"},
            "g384_ov192_g37-union-k10-verify":
                {"modality": "text", "path": "verifier/g384_ov192_g37/verify_k10"},
            "g384_ov192_g37-union-k5-verify-swap37":
                {"modality": "text", "path": "verifier/g384_ov192_g37/verify_swap37"},
            "g384_ov192_g37-union-k5-verify-swap38":
                {"modality": "text", "path": "verifier/g384_ov192_g37/verify_swap38"},
        },
        "conditions": [
            {"label": "g37-text-k5-verified-carried-p0.10-k5",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_g37", "n_passes": 5,
             "vote_threshold": 5, "prob_threshold": 0.10,
             "verifier_config": dict(VF_G3), "n_candidates": 791,
             "eval_path": "results/gemini37-screen-2026-08-28/best-eval/"
                          "evaluation.json",
             "detections": "results/gemini37-screen-2026-08-28/"
                           "verified_best_20m.geojson",
             "_note": ("A1 — the standalone K=5 screen best (F1@20 0.913892, "
                       "tile-MCC 0.7797, 443 detections) on the K=5 union's own "
                       "791-item verification. Distinct from the K=10-vintage "
                       "ladder N=5 rung (0.913094, 435 detections), which reads "
                       "the same five passes through the 913-item "
                       "re-verification and is not registered (PI ruling 4/7).")},
            {"label": "g37-text-k10-verified-carried-p0.10-k10",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_g37", "n_passes": 10,
             "vote_threshold": 10, "prob_threshold": 0.10,
             "verifier_config": dict(VF_G3), "n_candidates": 913,
             "eval_path": "results/gemini37-screen-2026-08-28/k10/best-eval/"
                          "evaluation.json",
             "detections": "results/gemini37-screen-2026-08-28/k10/"
                           "verified_best_20m.geojson",
             "_note": ("A2 — the approved K=10 escalation (F1@20 0.914219, "
                       "tile-MCC 0.7817, 423 detections). Five extra proposer "
                       "passes (~$5.4 billed) bought +0.0003; the ladder's own "
                       "N5-N10 contrast is -0.0011 at p = 0.7928.")},
            {"label": "g37-text-k5-verified-swap37-p0.80-k5",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_g37", "n_passes": 5,
             "vote_threshold": 5, "prob_threshold": 0.80,
             "verifier_config": dict(VF_37), "n_candidates": 791,
             "eval_path": "results/gemini37-screen-2026-08-28/swap37/best-eval/"
                          "evaluation.json",
             "detections": "results/gemini37-screen-2026-08-28/swap37/"
                           "verified_best_20m.geojson",
             "_note": ("A3 — the all-3.7 stack: the SAME 791 candidates "
                       "re-verified with gemini-3.7-flash (F1@20 0.926488, "
                       "P 0.9254 / R 0.9276, tile-MCC 0.8078, 429 detections) "
                       "for ~$0.9 token-basis. The study's first GS-resolvable "
                       "model-swap margin (+0.0304 vs the 0.8961 anchor, "
                       "p = 0.0105). The sweep argmax is a TIE the analysis JSON "
                       "does not flag: prob_t 0.80 and 0.85 give identical F1 "
                       "and 429 detections in swap37/sweep_20m.csv; the card "
                       "commits (0.80, k5).")},
            {"label": "g37-text-k5-verified-swap38-p0.88-k5",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_g37", "n_passes": 5,
             "vote_threshold": 5, "prob_threshold": 0.88,
             "verifier_config": dict(VF_38), "n_candidates": 791,
             "eval_path": "results/gemini38-screen-2026-09-04/armV/best-eval/"
                          "evaluation.json",
             "detections": "results/gemini38-screen-2026-09-04/armV/"
                           "verified_best_20m.geojson",
             "_note": ("Gemini 3.8 Arm V (card " + CARD_38 + "; PI ruling 9): the "
                       "SAME 791-candidate K=5 union re-verified with "
                       "gemini-3.8-flash at thinking=low (F1@20 0.9258, "
                       "P 0.9335 / R 0.9182, tile-MCC 0.8218, 421 detections) for "
                       "~$0.85 flex token-basis. Registered under this run "
                       "because it re-verifies this run's union; the campaign "
                       "tree outputs/gemini38-screen-2026-09-04/ holds only the "
                       "proposer probe, and the verification itself lives at "
                       "outputs/gemini37-screen-2026-08-28/verifier/"
                       "g384_ov192_g37/verify_swap38/. Obs 448.")},
        ],
    },
    IMG: {
        "_note": _IMG_NOTE,
        "proposer_pools": {
            "g384_ov192_g37img": {"modality": "image", "path": "g384_ov192_g37img"},
        },
        "verifier_passes": {
            "g384_ov192_g37img-union-k5-verify-arm1":
                {"modality": "text",
                 "path": "verifier/g384_ov192_g37img/verify_arm1"},
            "g384_ov192_g37img-union-k5-verify-arm2":
                {"modality": "text",
                 "path": "verifier/g384_ov192_g37img/verify_arm2"},
        },
        "conditions": [
            {"label": "g37-image-k5-verified-carried-p0.10-k5",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_g37img", "n_passes": 5,
             "vote_threshold": 5, "prob_threshold": 0.10,
             "verifier_config": dict(VF_G3), "n_candidates": 674,
             "eval_path": "results/gemini37-image-gs-2026-09-01/arm1/best-eval/"
                          "evaluation.json",
             "detections": "results/gemini37-image-gs-2026-09-01/arm1/"
                           "verified_best_20m.geojson",
             "_note": ("A7 — image under the carried Gemini-3 verifier (F1@20 "
                       "0.925408, tile-MCC 0.8192, 430 detections), +0.0842 over "
                       "the 0.8412 Gemini-3 image anchor. Its within-family text "
                       "pair is A1: (text - image) = -0.0115, p = 0.2533 "
                       "(gap_test.json).")},
            {"label": "g37-image-k5-verified-swap37-p0.90-k5",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_g37img", "n_passes": 5,
             "vote_threshold": 5, "prob_threshold": 0.90,
             "verifier_config": dict(VF_37), "n_candidates": 674,
             "eval_path": "results/gemini37-image-gs-2026-09-01/arm2/best-eval/"
                          "evaluation.json",
             "detections": "results/gemini37-image-gs-2026-09-01/arm2/"
                           "verified_best_20m.geojson",
             "_note": ("A8 — the all-3.7 image stack (F1@20 0.930832, tile-MCC "
                       "0.8322, 425 detections), the highest F1@20 in the 3.7 "
                       "arc, +0.0896 over the Gemini-3 image anchor. Its "
                       "within-family text pair is A3: (text - image) = -0.0043, "
                       "p = 0.6767. Sweep argmax tie at prob_t 0.90 / 0.95.")},
        ],
    },
    M55: {
        "_note": _M55_NOTE,
        "proposer_pools": {
            "g384_ov192_55map_g37": {"modality": "text",
                                     "path": "g384_ov192_55map_g37"},
        },
        "verifier_passes": {
            "g384_ov192_55map_g37-union-k5-verify-arm1":
                {"modality": "text",
                 "path": "verifier/g384_ov192_55map_g37/verify_arm1"},
            "g384_ov192_55map_g37-union-k5-verify-arm2":
                {"modality": "text",
                 "path": "verifier/g384_ov192_55map_g37/verify_arm2"},
        },
        "conditions": [
            {"label": "arm1-n5-carried-p0.10-k5-canonical-gt",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_55map_g37", "n_passes": 5,
             "vote_threshold": 5, "prob_threshold": 0.10,
             "verifier_config": dict(VF_G3), "n_candidates": 12715,
             "eval_path": "results/gemini37-55map-2026-08-31/arm1/"
                          "g384_ov192_55map_g37/primary/eval/evaluation.json",
             "detections": "results/gemini37-55map-2026-08-31/arm1/"
                           "g384_ov192_55map_g37/primary/"
                           "verified_detections.geojson",
             "_note": ("B1 — arm 1 (3.7 proposer + carried Gemini-3 verifier) at "
                       "its committed carried point, CANONICAL chain: "
                       "corrected-F1@50 0.849360 [0.841013, 0.857383], P 0.8438 "
                       "/ R 0.8550, tile-MCC 0.6665, 5,229 detections. Against "
                       "the canonical B N=5 incumbent 0.8438 this is +0.0056, "
                       "p = 0.3488 — below the 55-map MDE80 of 0.013, which is "
                       "D1's pre-named informative failure.")},
            {"label": "arm1-n5-carried-p0.10-k5-standardised-gt",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_55map_g37", "n_passes": 5,
             "vote_threshold": 5, "prob_threshold": 0.10,
             "verifier_config": dict(VF_G3), "n_candidates": 12715,
             "eval_path": "results/gemini37-55map-2026-08-31/arm1/"
                          "g384_ov192_55map_g37/standardised-ref/evaluation.json",
             "detections": "results/gemini37-55map-2026-08-31/arm1/"
                           "g384_ov192_55map_g37/primary/"
                           "verified_detections.geojson",
             "_note": ("B2 — the same detections on the ruling-21 STANDARDISED "
                       "reference: F1@50 0.8550 [0.8465, 0.8630], P 0.8371 / "
                       "R 0.8737. The tile confusion matrix is identical to the "
                       "canonical chain's 50 m row (2533/4632/385/991), so the "
                       "two rows share one tile-MCC.")},
            {"label": "arm2-n5-carried-p0.80-k5-canonical-gt",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_55map_g37", "n_passes": 5,
             "vote_threshold": 5, "prob_threshold": 0.80,
             "verifier_config": dict(VF_37), "n_candidates": 12715,
             "eval_path": "results/gemini37-55map-2026-08-31/arm2/"
                          "g384_ov192_55map_g37/primary/eval/evaluation.json",
             "detections": "results/gemini37-55map-2026-08-31/arm2/"
                           "g384_ov192_55map_g37/primary/"
                           "verified_detections.geojson",
             "_note": ("B3 — arm 2 (all-3.7) at its committed carried point, "
                       "CANONICAL chain: corrected-F1@50 0.876316 [0.868574, "
                       "0.883690], P 0.8901 / R 0.8630, tile-MCC 0.7073, 5,003 "
                       "detections. The campaign headline: +0.0270 over arm 1 "
                       "(p = 0.0001, BH-significant) — the family gain sits in "
                       "the verifier seat. Also the model arm of the "
                       "student-baseline programme "
                       "(planning/student-baseline-2026-08-31.md).")},
            {"label": "arm2-n5-carried-p0.80-k5-standardised-gt",
             "architecture": "proposer-verifier", "aggregation": "verified",
             "proposer_pool": "g384_ov192_55map_g37", "n_passes": 5,
             "vote_threshold": 5, "prob_threshold": 0.80,
             "verifier_config": dict(VF_37), "n_candidates": 12715,
             "eval_path": "results/gemini37-55map-2026-08-31/arm2/"
                          "g384_ov192_55map_g37/standardised-ref/evaluation.json",
             "detections": "results/gemini37-55map-2026-08-31/arm2/"
                           "g384_ov192_55map_g37/primary/"
                           "verified_detections.geojson",
             "_note": ("B4 — the same detections on the STANDARDISED reference: "
                       "F1@50 0.8825 [0.8746, 0.8897], P 0.8831 / R 0.8818 — "
                       "above the entire 2026-08-27 final board including its "
                       "oracles (ceiling B-N10-oracle 0.8558). Tile matrix "
                       "identical to the canonical 50 m row "
                       "(2516/4798/219/1008).")},
        ],
    },
}

# --------------------------------------------------------------------------- #
# Additions to the two existing decompositions (PI ruling 6)
# --------------------------------------------------------------------------- #

GRID_VERIFIER_ADD = {
    "g384_ov192-union-k10-verify37":
        {"modality": "text", "path": "verifier/g384_ov192/verify_37"},
}

GRID_CONDITION_ADD = [
    {"label": "g384-ov192-k10-verified37-p0.98-k10",
     "architecture": "proposer-verifier", "aggregation": "verified",
     "proposer_pool": "brief-text", "n_passes": 10,
     "vote_threshold": 10, "prob_threshold": 0.98,
     "verifier_config": dict(VF_37), "n_candidates": 3319,
     "eval_path": "results/gemini37-fourth-cell/gs-leg/best-eval/evaluation.json",
     "detections": "results/gemini37-fourth-cell/gs-leg/verified_best_20m.geojson",
     "_note": ("A9 — the fourth cell's GS calibration leg (~$3; card "
               + CARD_55MAP + ":201, which commits (0.98, k10) as the 55-map "
               "fourth cell's carried point BEFORE any deployment scoring). This "
               "run's own Gemini-3 g384_ov192 K=10 union (3,319 candidates) "
               "re-verified with gemini-3.7-flash: F1@20 0.914005, P 0.9637 / "
               "R 0.8692, tile-MCC 0.8239, 386 detections; +0.0179 over the "
               "0.8961 text-B anchor at p = 0.0563. Registered here rather than "
               "under a 3.7 run because the condition belongs to the run that "
               "owns its proposer pool (PI ruling 6); the verification lives at "
               "outputs/grid-2026-08-18/verifier/g384_ov192/verify_37/. GOTCHA: "
               "this is a TEXT cell whose best point sits under the 'image_best' "
               "key of results/gemini37-fourth-cell/gs-leg/analysis.json. The "
               "verifier_config variant is recorded as 'v1' (the 3.7-arc "
               "convention) while this run's Gemini-3 siblings say "
               "'adversarial-text'; same instruction file, same hash.")},
]

STRIDE_VERIFIER_ADD = {
    "g384_ov192_55map-union-k10-verify37":
        {"modality": "text", "path": "verifier/g384_ov192_55map/verify_37"},
}

STRIDE_CONDITION_ADD = [
    {"label": "g384-ov192-55map-k10-verified37-p0.98-k10-canonical-gt",
     "architecture": "proposer-verifier", "aggregation": "verified",
     "proposer_pool": "g384_ov192_55map", "n_passes": 10,
     "vote_threshold": 10, "prob_threshold": 0.98,
     "verifier_config": dict(VF_37), "n_candidates": 57482,
     "eval_path": "results/gemini37-fourth-cell/55map/g384_ov192_55map/primary/"
                  "eval/evaluation.json",
     "detections": "results/gemini37-fourth-cell/55map/g384_ov192_55map/primary/"
                   "verified_detections.geojson",
     "_note": ("B5 — the 2x2 grid's fourth cell (this run's Gemini-3 K=10 union, "
               "57,482 candidates, re-verified with gemini-3.7-flash), CANONICAL "
               "chain: corrected-F1@50 0.865618 [0.857387, 0.873612], P 0.9588 / "
               "R 0.7890, tile-MCC 0.7268, 4,246 detections — the grid's "
               "precision and tile-MCC crowns. +0.0234 over this run's own K=10 "
               "carried incumbent (p = 0.0001, BH-significant), the second "
               "verifier-axis test. Carried point (0.98, k10) fixed by the GS "
               "calibration leg (grid-2026-08-18::"
               "g384-ov192-k10-verified37-p0.98-k10) before deployment scoring. "
               "Registered here per PI ruling 6.")},
    {"label": "g384-ov192-55map-k10-verified37-p0.98-k10-standardised-gt",
     "architecture": "proposer-verifier", "aggregation": "verified",
     "proposer_pool": "g384_ov192_55map", "n_passes": 10,
     "vote_threshold": 10, "prob_threshold": 0.98,
     "verifier_config": dict(VF_37), "n_candidates": 57482,
     "eval_path": "results/gemini37-fourth-cell/55map/g384_ov192_55map/"
                  "standardised-ref/evaluation.json",
     "detections": "results/gemini37-fourth-cell/55map/g384_ov192_55map/primary/"
                   "verified_detections.geojson",
     "_note": ("B6 — the same detections on the ruling-21 STANDARDISED "
               "reference: F1@50 0.8732 [0.8649, 0.8810], P 0.9517 / R 0.8066. "
               "Tile matrix identical to the canonical 50 m row "
               "(2358/4985/32/1166).")},
]

# --------------------------------------------------------------------------- #
# Run facts
# --------------------------------------------------------------------------- #

GS_SCOPE = {
    "test_set_id": "grid-common-487",
    "bounds_path": "outputs/grid-2026-08-18/scoring/bounds/"
                   "grid_common_bounds.geojson",
    "n_test_tiles": 487,
    "calibration_set_id": None,
    "n_calibration_tiles": None,
}

M55_SCOPE = {
    "test_set_id": "55maps-8541",
    "bounds_path": "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson",
    "n_test_tiles": 8541,
    "calibration_set_id": None,
    "n_calibration_tiles": None,
}

COST_FLAG = (
    "The live cost estimator prices the 3.7 SKU at Gemini-3 list rates and excluded "
    "thinking tokens until commit 73658c579, so every cost_estimate on a 3.7 run "
    "under-states; any cost figure in this register's rows is token-basis, computed "
    "from recorded token counts at the 3.7/3.8 rates."
)

META_FLAG = (
    "Verifier cost provenance is partly lost: run_pv.py cleanup overwrote "
    "run.meta.json on the swap passes (verify_swap37 records items_processed 2; the "
    "grid and stride verify_37 metas record 1 and 29), so item counts come from "
    "probabilities.json total_results instead. The condition rows are unaffected; "
    "only cost provenance is."
)

FACTS = {
    SCREEN: {
        "primary_hypothesis": None,
        "also_informs": ["H13"],
        "purpose": ("Gemini 3.7 Flash screen on the leading 384 px / 50 % geometry: "
                    "does a within-vendor model-family step clear the Gemini-3 GS "
                    "plateau, and in which seat? Predictions G1-G4 committed at PI "
                    "go (card " + CARD_SCREEN + "). Escalated to K=10 and to two "
                    "verifier-role swaps (3.7, then 3.8 under card " + CARD_38
                    + ")."),
        "tile_size_px": 384,
        "corpus": "4-map-gs",
        "gt_reference": "curator",
        "scope": dict(GS_SCOPE),
        "headline_condition_id": f"{SCREEN}::g37-text-k5-verified-swap37-p0.80-k5",
        "headline_rationale": ("The all-3.7 stack (F1@20 0.9265, tile-MCC 0.8078) — "
                               "the study's first GS-resolvable model-swap margin "
                               "(+0.0304 vs the anchor, p = 0.0105) and the only "
                               "cell in the arc beating the anchor on F1 and MCC "
                               "together."),
        "historical_aliases": [],
        "_scope_confidence": "HIGH",
        "_scope_source": "empirical",
        "_flags": [
            COST_FLAG,
            META_FLAG,
            "Model and thinking level stay confounded: 3.7 at thinking=low emits "
            "~276 thinking tokens per tile against Gemini-3 MINIMAL's zero.",
        ],
    },
    IMG: {
        "primary_hypothesis": None,
        "also_informs": ["H1"],
        "purpose": ("Image variant of the 3.7 GS screen under matched everything, "
                    "for the difference-in-differences against the Gemini-3 "
                    "modality contrast (image-b-gs-2026-08-28). Predictions I1-I5 "
                    "committed at PI go (card " + CARD_IMAGE + "). The escalation "
                    "trigger was not met; no 55-map image extension followed."),
        "tile_size_px": 384,
        "corpus": "4-map-gs",
        "gt_reference": "curator",
        "scope": dict(GS_SCOPE),
        "headline_condition_id": f"{IMG}::g37-image-k5-verified-swap37-p0.90-k5",
        "headline_rationale": ("The all-3.7 image stack (F1@20 0.9308, tile-MCC "
                               "0.8322) — the highest F1@20 anywhere in the 3.7 "
                               "arc, and the cell that makes the modality gap "
                               "vanish."),
        "historical_aliases": [],
        "_scope_confidence": "HIGH",
        "_scope_source": "empirical",
        "_flags": [
            COST_FLAG,
            "Implicit caching engaged at 79.5 % of input against a registered "
            ">= 90 % bar (I5, an informative failure); the probe measurement is "
            "warm-up-confounded (16 % cold-parallel, 54 % sequential).",
            "scripts/image_b_analysis.py:79 hard-codes ANCHOR_F1_20 = 0.8961, so "
            "the analysis JSONs' head_to_head_20m blocks are mis-anchored for a "
            "modality reading — use gap_test.json.",
        ],
    },
    M55: {
        "primary_hypothesis": None,
        "also_informs": ["H13"],
        "purpose": ("Does the 3.7 GS gain transfer to 55-map deployment, and in "
                    "which seat? One K=5 3.7 proposer pool, two verifier arms "
                    "(carried Gemini-3; all-3.7), both carried points committed "
                    "before deployment scoring. With the fourth cell (registered "
                    "under stride-55map-2026-08-25) this completes the proposer x "
                    "verifier 2x2. Predictions D1-D7, card " + CARD_55MAP + "."),
        "tile_size_px": 384,
        "corpus": "55-map",
        "gt_reference": "combined",
        "scope": dict(M55_SCOPE),
        "headline_condition_id": f"{M55}::arm2-n5-carried-p0.80-k5-canonical-gt",
        "headline_rationale": ("Arm 2, the all-3.7 stack at its committed carried "
                               "point (canonical corrected-F1@50 0.8763): the "
                               "campaign's headline and the diagonal that reads "
                               "+0.0325 over the canonical B N=5 incumbent "
                               "(p = 0.0001)."),
        "historical_aliases": [],
        "_scope_confidence": "HIGH",
        "_scope_source": "empirical",
        "_flags": [
            "TWO INSTRUMENTS: canonical adjudicated extended GT (5,160 references "
            "at 50 m; the committed primary) and the ruling-21 standardised "
            "reference (5,010). Every delta must name its chain; Session 144's "
            "interim headlines mixed them and were corrected (Obs 444 § (b)).",
            "gt_reference 'combined' = the canonical adjudicated extended GT, the "
            "schema's combined class.",
            "The 2x2 is NOT square in pass count: the Gemini-3 row is K=10, the "
            "3.7 row K=5, which is why the two proposer-axis tests use different "
            "comparators.",
            COST_FLAG,
            "The proposer tiling is an overlapping custom grid; evaluation is on "
            "the standard 8,541-tile frame.",
        ],
    },
}

# --------------------------------------------------------------------------- #
# Analyses
# --------------------------------------------------------------------------- #

_LADDER_DEFERRAL = (
    "The N=1/3/5 ladder rungs are re-derived here and NOT registered as conditions: "
    "they have no materialised detections, and their materialisation is folded into "
    "the r2 recompute chain (planning/reference-revision-2026-09-06.md), where they "
    "will be registered — re-derived; registration pending materialisation."
)

ANALYSES = [
    {
        "analysis_id": SCREEN,
        "type": "comparison",
        "_note": ("The Gemini 3.7 GS screen and its two approved escalations "
                  "(scripts/image_b_analysis.py over each cell; paired tile-swap "
                  "permutation, 10,000 draws, seed 42, 487-tile common footprint; "
                  "anchor gate reproduces the registered 0.8961 exactly). Every "
                  "cell's best point sits under the JSON key 'image_best' although "
                  "all three are TEXT cells — the campaign reused the image "
                  "harness. The swap37 argmax is a tie (prob_t 0.80 and 0.85, "
                  "identical F1 and 429 detections) that analysis.json does not "
                  "flag. " + _LADDER_DEFERRAL),
        "_prereg_rationale": ("Post-registration campaign with card-committed "
                              "predictions: the preregistration registers no "
                              "hypothesis about model version, so the S134 sorting "
                              "rule makes this post-hoc (the flash35-model-roles "
                              "precedent, the direct ancestor of this design). The "
                              "foresight is evidenced in predicted_outcome, which "
                              "is write-once. PI ruling 1, 2026-09-06."),
        "conditions_compared": [
            f"{SCREEN}::g37-text-k5-verified-carried-p0.10-k5",
            f"{SCREEN}::g37-text-k10-verified-carried-p0.10-k10",
            f"{SCREEN}::g37-text-k5-verified-swap37-p0.80-k5",
            "grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10",
        ],
        "hypothesis_refs": [],
        "preregistered": "post-hoc",
        "deviations": [],
        "predicted_outcome": (
            "Committed at PI go, " + CARD_SCREEN + ":38-41 — \"G1 | Verified best "
            "@20 m | 3.7 at-or-below the Gemini 3 plateau (<= 0.8934 + GS "
            "resolution)\"; \"G2 | Operating lattice | prob in {0.15, 0.20}, "
            "mid-to-high k\"; \"G3 | Cost | proposer $5.5-16 flex "
            "(thinking-volume-dependent; 3.7 rates 1.5x/1.25x Gemini 3)\"; \"G4 | "
            "Thinking at `low` | nonzero but < HIGH-class volumes (< 1,000 "
            "t/tile)\". Pre-named informative outcome, " + CARD_SCREEN + ":43-44: "
            "\"3.7 ABOVE the plateau (verified best > 0.8961 + resolution)\"."),
        "tie_set": [],
        "outcome": (
            "G1's pre-named informative outcome FIRED and G2 is falsified. The "
            "carried-verifier K=5 cell reaches 0.9139 @20 m at (0.10, k5) on a "
            "791-candidate union, nominally above every Gemini-3 cell on this "
            "corpus, but the paired tile-swap permutation (10,000 draws, 487 tiles) "
            "returns +0.0178 at p = 0.1697 against a null SD of 0.0129 — below the "
            "GS instrument's resolution, so the screen can name the direction and "
            "not the size. K=10 adds +0.0003 (0.9142, p = 0.2076) and the ladder's "
            "own N5-N10 contrast is -0.0011 at p = 0.7928: saturated by N = 5, the "
            "Gemini-3 shape exactly (0.8588 / 0.9018 / 0.9131 / 0.9142 at "
            "N = 1/3/5/10). The headline is the role swap: re-verifying the SAME "
            "791 candidates with gemini-3.7-flash reaches 0.9265 @20 m at "
            "(0.80, k5), P 0.9254 / R 0.9276 / tile-MCC 0.8078 — +0.0304 vs the "
            "anchor, p = 0.0105, the study's first GS-resolvable model-swap margin "
            "and the only cell in the arc beating the anchor on F1 and MCC "
            "together. The mechanism is calibration, not judgement: the 3.7 "
            "verifier's mean mound_probability is 0.687 against the carried "
            "verifier's 0.587 on identical candidates (" + CARD_SCREEN + ":110), so "
            "its optimum migrates four rungs up a lattice that has sat at 0.10-0.20 "
            "across every model the study has run — G2 falsified, and the portable "
            "claim is that a verifier's operating threshold does not transfer "
            "across verifier models. Cost ordering is the practitioner lesson: five "
            "extra passes cost ~$5.4 and bought +0.0003; the role swap cost ~$0.9 "
            "token-basis and bought +0.0126 over the same union. Caveats: both "
            "sides of every contrast are sweep-selected argmaxes scored on the same "
            "reference; this is a single comparison with no family correction "
            "across four GS sheets; and 3.7-`low` emits ~276 thinking tokens per "
            "tile against Gemini-3 MINIMAL's zero, so model and thinking stay "
            "confounded. The K=10 escalation re-verified the full union rather than "
            "increment-stitching — disclosed on the card, cheaper than the "
            "matching-error risk, and it gives single-vintage probabilities. The "
            "ladder rungs are re-derived; registration pending materialisation. "
            "Obs 441."),
        "paper_section": "Results",
        "output_path": "results/gemini37-screen-2026-08-28",
        "working_notes_obs": [
            "Obs 441 — Gemini 3.7 Flash clears the Gemini 3 plateau but resolves "
            "only in the verifier role"],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "gemini37-55map-grid-2026-08-31",
        "type": "comparison",
        "_note": ("The complete proposer x verifier 2x2 at 55-map deployment and "
                  "its declared five-test family (scripts/gemini37_sweep_oracle.py; "
                  "results/gemini37-55map-2026-08-31/sweeps/sweep_oracle.json): "
                  "per-sheet paired sign-swap permutation, 10,000 draws, seed 42, "
                  "BH-FDR at q = 0.05 over exactly five tests. CANONICAL chain "
                  "throughout for the tests; the standardised chain is reported "
                  "alongside. FOREIGN-KEY GAP: the D1 comparator — the canonical B "
                  "N=5 incumbent, corrected-F1@50 0.8437752627324171, source "
                  "results/stride55-2026-08-27/ladder.json (runs.g384_ov192_55map."
                  "N.5.carried) and results/gemini37-55map-2026-08-31/sweeps/"
                  "sweep_oracle.json (incumbents.BN5), 4,736 detections at "
                  "results/55map-final-board-2026-08-27/cells/B-N5-carried/"
                  "detections.geojson — has NO canonical evaluation with a tile "
                  "confusion matrix, so no condition row can be authored for it "
                  "(the schema requires integer tile tp/tn/fp/fn and the ladder "
                  "records detection-level counts only). Its STANDARDISED sibling "
                  "is registered and is listed in conditions_compared as the "
                  "nearest available key; the canonical scoring belongs to the r2 "
                  "recompute chain. Do NOT read findings.md's 'ladder.json' pointer "
                  "as the campaign's own ladder/ladder.json — 0.843775 lives in "
                  "results/stride55-2026-08-27/ladder.json."),
        "_prereg_rationale": ("Post-registration campaign with card-committed "
                              "predictions D1-D7; PI ruling 1, 2026-09-06."),
        "conditions_compared": [
            f"{M55}::arm1-n5-carried-p0.10-k5-canonical-gt",
            f"{M55}::arm1-n5-carried-p0.10-k5-standardised-gt",
            f"{M55}::arm2-n5-carried-p0.80-k5-canonical-gt",
            f"{M55}::arm2-n5-carried-p0.80-k5-standardised-gt",
            f"{STRIDE}::g384-ov192-55map-k10-verified37-p0.98-k10-canonical-gt",
            f"{STRIDE}::g384-ov192-55map-k10-verified37-p0.98-k10-standardised-gt",
            f"{STRIDE}::g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt",
            f"{STRIDE}::g384-ov192-55map-n5-carried-p0.15-k5-standardised-gt",
        ],
        "hypothesis_refs": [],
        "preregistered": "post-hoc",
        "deviations": [],
        "predicted_outcome": (
            "Committed before any deployment scoring, " + CARD_55MAP + ":41-45 — "
            "\"D1 | Headline vs B-Gemini-3 | 3.7 carried ABOVE B-N5-carried 0.8502 "
            "by >= MDE80 0.013 — a resolvable win\"; \"D2 | Direction of the gain | "
            "recall-led (screen: R 0.9299 vs 0.8668 at slight precision cost)\"; "
            "\"D3 | Operating lattice | prob_t in {0.10, 0.15}, k4-k5; the carried "
            "(0.10, k5) on the 55-map plateau\"; \"D4 | Thinking volume | ~ the "
            "GS-measured 276 t/tile on 55-map content (probe gate)\"; \"D5 | Cost | "
            "within § 4's envelope at the probe-measured rate\". Pre-named "
            "informative failure, :47-48: \"3.7 ~ Gemini 3 at deployment (|delta| < "
            "MDE80 against B-N5-carried)\". Addendum registered at the same commit, "
            ":152-153 — \"D6 | Arm 2 vs arm 1 at deployment | arm 2 ahead by ~ "
            "+0.013 — at the MDE80 boundary, direction positive\"; \"D7 | Arm-2 "
            "lattice | oracle prob_t stays high (>= 0.6) — the calibration shift "
            "transfers\". The fourth cell's carried point (0.98, k10) was committed "
            "at :201 from a separate ~$3 GS calibration leg."),
        "tie_set": [],
        "outcome": (
            "The complete proposer x verifier 2x2, every corner at an operating "
            "point committed before any deployment scoring. Canonical chain, "
            "corrected-F1 @50 m against the adjudicated extended GT (5,160 "
            "references), per-sheet paired sign-swap permutation (10,000 draws, "
            "seed 42) with BH-FDR at q = 0.05 over the declared five-test family: "
            "arm 1 (3.7 proposer + carried Gemini-3 verifier) 0.8494, arm 2 "
            "(all-3.7) 0.8763, fourth cell (Gemini-3 K=10 union + 3.7 verifier) "
            "0.8656, against incumbents B N=5 0.8438 and B K=10 0.8422. The family "
            "gain lives in the verifier seat on the complete grid, not on one "
            "diagonal: both verifier-axis tests are BH-significant (arm 2 - arm 1 "
            "+0.0270, p = 0.0001; fourth - B K=10 +0.0234, p = 0.0001) and neither "
            "proposer-axis test is (arm 1 - B N=5 +0.0056, p = 0.3488; arm 2 - "
            "fourth +0.0107, p = 0.0738); the all-3.7 diagonal reads +0.0325, "
            "p = 0.0001. D1 is the pre-named informative failure — the GS "
            "proposer-seat gain (+0.018) did not transfer as a resolvable "
            "deployment win against a 55-map MDE80 of 0.013 — while D6 is confirmed "
            "at twice its predicted magnitude; D2, D3 and D7 are confirmed, D4 is "
            "confirmed at 265-277 t/call, and D5 is a provisional token-basis pass "
            "(proposer $144 against a $93-150 envelope; verifier arms $12.54 and "
            "$14.31), pending billed-versus-token reconciliation. The fourth cell "
            "takes the grid's precision (0.9588) and tile-MCC (0.7268) crowns: the "
            "discriminating 3.7 verifier trades recall for precision hard on a "
            "noisy pool, which is the calibration story pointed the other way. On "
            "the board's own standardised instrument arm 2 reads 0.8825 [0.8746, "
            "0.8897] — above the entire 2026-08-27 final board including its "
            "oracles (ceiling B-N10-oracle 0.8558) — the fourth cell 0.8732, and "
            "arm 1 0.8550 against B-N5-carried 0.8502 with overlapping CIs; the "
            "instrument offset is a roughly uniform +0.005-0.006, which is why "
            "nothing substantive moves between chains, and the tile confusion "
            "matrix is byte-identical across the two chains on all three cells. "
            "Caveats: the grid is NOT square in pass count (the Gemini-3 row is "
            "K=10, the 3.7 row K=5), which is why the two proposer-axis tests use "
            "different comparators; and the canonical B N=5 comparator has no "
            "condition row of its own (no canonical tile matrix exists on disk — "
            "its standardised sibling stands in as the foreign key, and the "
            "canonical scoring is queued with the r2 recompute chain). Obs 444."),
        "paper_section": "Results",
        "output_path": "results/gemini37-55map-2026-08-31",
        "working_notes_obs": [
            "Obs 444 — the complete proposer x verifier 2x2: the family gain lives "
            "in the verifier seat"],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "gemini37-55map-gridboard-2026-08-31",
        "type": "leaderboard",
        "_note": ("The 16-cell grid board on the CANONICAL chain "
                  "(results/gemini37-55map-2026-08-31/grid-board/grid_board.json): "
                  "all 120 pairs by per-sheet paired sign-swap permutation (10,000 "
                  "draws, seed 42), BH q = 0.05 across all pairs, greedy-clique "
                  "tiers, plus 15 named contrasts of which seven are "
                  "carried-versus-oracle. Separable from the 2x2 row because it is "
                  "a leaderboard and because most of its cells cannot yet carry "
                  "condition rows. " + _LADDER_DEFERRAL + " The tie_set records the "
                  "only board tier with more than one REGISTERED member (tier 4 of "
                  "six, which also contains the two unregistered cells BN5-carried "
                  "and arm2-N1-carried)."),
        "_prereg_rationale": ("The board was not pre-registered as a prediction; the "
                              "card's queued-oracle question is asked, not bet on. "
                              "PI ruling 1, 2026-09-06."),
        "conditions_compared": [
            f"{M55}::arm1-n5-carried-p0.10-k5-canonical-gt",
            f"{M55}::arm2-n5-carried-p0.80-k5-canonical-gt",
            f"{STRIDE}::g384-ov192-55map-k10-verified37-p0.98-k10-canonical-gt",
            f"{STRIDE}::g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt",
        ],
        "hypothesis_refs": [],
        "preregistered": "post-hoc",
        "deviations": [],
        "predicted_outcome": None,
        "tie_set": [
            f"{M55}::arm1-n5-carried-p0.10-k5-canonical-gt",
            f"{STRIDE}::g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt",
        ],
        "outcome": (
            "120 pairs, 89 BH-significant, six greedy-clique tiers on the canonical "
            "chain. All seven carried-to-oracle contrasts are BH-significant, "
            "including arm 2's +0.0043 (adjusted p = 0.000162) — threshold-transfer "
            "costs are sheet-consistent real effects at every scale, even where "
            "practically negligible — and the gap shrinks with N in both arms (arm 1 "
            "+0.0544 / +0.0227 / +0.0168, arm 2 +0.0142 / +0.0046 / +0.0043 at "
            "N = 1/3/5), so consensus partially substitutes for a correctly "
            "calibrated probability threshold, while the cross-model arm pays "
            "roughly four times the same-model arm's tax at every rung. Saturation "
            "at N = 3 is now tested and arm-specific: arm 2's N3-to-N5 is "
            "non-significant on both bases (carried adjusted p = 0.258824, oracle "
            "0.335192) and the fourth cell's independent ladder saturates "
            "identically (N = 3 0.8688 against N = 5 0.8697, oracle prob_t pinned "
            "at 0.96 on every rung), whereas arm 1's carried N3-to-N5 IS significant "
            "at +0.0076 (adjusted p = 0.000162). Tier structure: Tier 1 is arm 2's "
            "N5 and N3 oracles alone; Tier 2 holds arm2-N5-carried, "
            "fourth-N10-oracle and arm2-N3-carried at 3/5 the proposer spend; both "
            "Gemini-3 incumbents sit in Tier 4 of six, tied with arm1-N5-carried. "
            "The N = 1 economy is an ORACLE statement — a single 3.7 pass under the "
            "3.7 verifier reaches 0.8563 at its rung oracle, beating the canonical "
            "five-pass incumbent 0.8438 on about one-fifth the proposer spend, but "
            "the honest carried N = 1 reads 0.8421, a Tier 4 tie with the very "
            "incumbents it is set against, and rung oracles below N = 5 are "
            "descriptive by the screening protocol. Eleven of the sixteen cells "
            "(every oracle and every N=1/N=3 rung) are re-derived here; "
            "registration pending materialisation. Obs 444 §§ (c)-(d)."),
        "paper_section": "Results",
        "output_path": "results/gemini37-55map-2026-08-31/grid-board",
        "working_notes_obs": [
            "Obs 444 — the complete proposer x verifier 2x2: the family gain lives "
            "in the verifier seat"],
        "manually_verified_at": None,
    },
    {
        "analysis_id": IMG,
        "type": "comparison",
        "_note": ("The modality difference-in-differences one model generation on "
                  "from image-b-modality-2026-08-28: one geometry, one reference, "
                  "two within-family text/image pairs "
                  "(results/gemini37-image-gs-2026-09-01/gap_test.json; paired "
                  "tile-swap, 10,000 draws, seed 42, 487 tiles). WARNING: the "
                  "head_to_head_20m blocks inside arm1/analysis.json (-0.029273, "
                  "p = 0.0235) and arm2/analysis.json (-0.034697, p = 0.0065) are "
                  "mis-anchored for a modality reading — scripts/image_b_analysis."
                  "py:79 hard-codes ANCHOR_F1_20 = 0.8961, a GEMINI-3 TEXT cell, so "
                  "they mix the family step into the modality contrast. Never quote "
                  "them as a modality delta."),
        "_prereg_rationale": ("Post-registration campaign with card-committed "
                              "predictions I1-I5; post-hoc under the S134 sorting "
                              "rule (PI ruling 1) even though it carries H1, which "
                              "a post-hoc row may do — the flash35-model-roles "
                              "precedent is post-hoc with H2. Its Gemini-3 sibling "
                              "image-b-modality-2026-08-28 is registered-exploratory; "
                              "the difference is deliberate."),
        "conditions_compared": [
            f"{IMG}::g37-image-k5-verified-carried-p0.10-k5",
            f"{IMG}::g37-image-k5-verified-swap37-p0.90-k5",
            f"{SCREEN}::g37-text-k5-verified-carried-p0.10-k5",
            f"{SCREEN}::g37-text-k5-verified-swap37-p0.80-k5",
            "image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9",
            "grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10",
        ],
        "hypothesis_refs": ["H1"],
        "preregistered": "post-hoc",
        "deviations": [],
        "predicted_outcome": (
            "Committed at PI go, " + CARD_IMAGE + ":44-48 — \"I1 | Family gain on "
            "image | 3.7-image verified best ABOVE the G3 image anchor 0.8412\"; "
            "\"I2 | The gap | (text - image) within 3.7 NARROWER than 0.0549 by more "
            "than the resolution — i.e. gap < ~0.031\"; \"I3 | Lattices | "
            "carried-verifier arm optimum at prob in {0.10-0.20}, mid-to-high k; "
            "3.7-verifier arm optimum at prob_t >= 0.6 (the calibration shift "
            "replicates on image candidates)\"; \"I4 | Thinking at `low` on image "
            "prompts | nonzero, < 1,000 t/tile, ~ the text screen's 276\"; \"I5 | "
            "Cost and caching | implicit caching engages as on G3 (cached fraction "
            ">= 90 % of input); all-in within § Cost envelope\". I2 names its own "
            "informative outcomes at :45: \"gap unchanged (vision gain is "
            "modality-neutral) or WIDER (text benefited more)\"."),
        "tie_set": [],
        "outcome": (
            "The modality gap is eliminated at Gemini 3.7. A "
            "difference-in-differences on one geometry and one reference: "
            "(text - image) within Gemini 3 was +0.0549 at p = 0.001; within 3.7 it "
            "is -0.0115 (p = 0.2533) on the carried-verifier pair and -0.0043 "
            "(p = 0.6767) on the all-3.7 pair — a gap change of -0.059 to -0.066, "
            "roughly 2.5x the GS verified-set resolution (MDE80 ~ 0.024), so a "
            "resolved change and not instrument noise. The honest claim is PARITY, "
            "not inversion: image leads nominally in both pairs and neither sign "
            "flip is close to significant. I2 predicted the gap would land below "
            "~0.031 and the outcome overshot to zero. I1 is confirmed at about five "
            "times the text-side family gain — 3.7-image reaches 0.9254 (carried "
            "verifier) and 0.9308 (3.7 verifier) against the 0.8412 Gemini-3 image "
            "anchor, gains of +0.0842 / +0.0896 where the same family step on text "
            "was +0.018 — so the gap closed because image caught up, not because "
            "text regressed, and the 3-to-3.7 step delivers most of its value where "
            "pixels are read. I3 is confirmed exactly at (0.10, k5) and (0.90, k5): "
            "the 3.7 verifier's high-probability calibration shift replicates on "
            "image candidates, a second instrument for the "
            "non-transferring-threshold claim. I4 is confirmed and lighter than "
            "predicted (88-157 t/call). I5 is an informative failure — implicit "
            "caching engaged at 79.5 % of input against a registered >= 90 % bar, "
            "with the probe warm-up-confounded (16 % cold-parallel, 54 % "
            "sequential), yet the proposer side cost $22.50 token-basis against a "
            "$32-36 projection. The escalation trigger is NOT met: all-3.7 image "
            "0.9308 against the all-3.7 text swap 0.9265 is +0.0043 at p = 0.677, "
            "far inside MDE80, no resolvable new high, so the 55-map image "
            "extension does not proceed — a registered negative decision, not an "
            "absence. Obliges the paper: the study's 'text examples beat image "
            "examples' claim must be reframed as Gemini-3-specific. Obs 447."),
        "paper_section": "Results",
        "output_path": "results/gemini37-image-gs-2026-09-01",
        "working_notes_obs": [
            "Obs 447 — the modality gap is eliminated at Gemini 3.7"],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "gemini37-fourth-cell-gs-leg-2026-08-31",
        "type": "diagnostic",
        "_note": ("The ~$3 GS calibration leg run BEFORE the 55-map fourth cell so "
                  "that cell's operating point would be a carry-forward rather than "
                  "an argmax (results/gemini37-fourth-cell/gs-leg/analysis.json; "
                  "paired tile-swap, 10,000 draws, seed 42, 487 tiles). A TEXT cell "
                  "whose best point sits under the 'image_best' key. Its outcome "
                  "fixed the carried point recorded at " + CARD_55MAP + ":201."),
        "_prereg_rationale": ("A calibration step, not a bet: predicted_outcome is "
                              "null rather than a retrospective quotation. PI ruling "
                              "1, 2026-09-06."),
        "conditions_compared": [
            "grid-2026-08-18::g384-ov192-k10-verified37-p0.98-k10",
            "grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10",
        ],
        "hypothesis_refs": [],
        "preregistered": "post-hoc",
        "deviations": [],
        "predicted_outcome": None,
        "tie_set": [],
        "outcome": (
            "A ~$3 GS calibration leg: the Gemini-3 grid g384_ov192 K=10 union "
            "(3,319 candidates) re-verified with the 3.7 verifier reaches 0.9140 "
            "@20 m at (0.98, k10), P 0.9637 / R 0.8692 / tile-MCC 0.8239 against the "
            "0.8961 text-B anchor (+0.0179, p = 0.0563 on 10,000 permutations over "
            "487 tiles). The lattice moves the whole way to the top of the scale: "
            "the 3.7 verifier's mean probability is 0.209 on the noisy Gemini-3 pool "
            "against 0.687 on its own union (" + CARD_55MAP + ":200), so the same "
            "verifier calibrates DIFFERENTLY AGAINST DIFFERENT CANDIDATE POOLS — the "
            "threshold-transfer claim extended from model to pool. (0.98, k10) was "
            "committed as the 55-map fourth cell's carried point at " + CARD_55MAP
            + ":201 before any deployment scoring. Obs 444 § (e)."),
        "paper_section": "Methods",
        "output_path": "results/gemini37-fourth-cell/gs-leg",
        "working_notes_obs": [
            "Obs 444 — the complete proposer x verifier 2x2: the family gain lives "
            "in the verifier seat"],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "gemini38-screen-armv-2026-09-04",
        "type": "comparison",
        "_note": ("Gemini 3.8 Arm V — the verifier seat at zero proposer cost (card "
                  + CARD_38 + "): the 3.7 screen's own 791-candidate K=5 union "
                  "re-verified with gemini-3.8-flash and scored through the same "
                  "harness. Round-robin paired tile-swap, 10,000 draws, seed 42, 487 "
                  "tiles (results/gemini38-screen-2026-09-04/armV/pair_test.json). "
                  "Arm P (3.8 proposer) and Arm S were NOT run: the PI ruled STOP "
                  "after Arm V on 2026-09-04. E2 is therefore untested, and the "
                  "screen closes with the family ladder stopping at 3.7."),
        "_prereg_rationale": ("Post-registration campaign with card-committed "
                              "predictions E1-E4; PI ruling 1 and ruling 9, "
                              "2026-09-06."),
        "conditions_compared": [
            f"{SCREEN}::g37-text-k5-verified-swap38-p0.88-k5",
            f"{SCREEN}::g37-text-k5-verified-swap37-p0.80-k5",
            f"{SCREEN}::g37-text-k5-verified-carried-p0.10-k5",
        ],
        "hypothesis_refs": [],
        "preregistered": "post-hoc",
        "deviations": [],
        "predicted_outcome": (
            "Committed at PI go, " + CARD_38 + ":69-72 — \"E1 | Arm V, verified best "
            "@20 m | tie with 0.9265 (within GS resolution)\"; \"E2 | Arm P, "
            "carried-vf best @20 m | tie with 0.9139\"; \"E3 | Thinking volume at "
            "`low` | above 3.7's 275 t/tile, 1.5-3x\"; \"E4 | Verifier operating "
            "point | 3.8's prob_t optimum differs from 3.7's 0.80/0.85 and G3's "
            "0.15/0.20\". Pre-named informative outcome, :74-76: \"Arm V or Arm S "
            "above 0.9265 plus GS resolution\", which would be the second family "
            "gain in the verifier seat and would reopen the verifier-model policy "
            "for the 55-map board."),
        "tie_set": [
            f"{SCREEN}::g37-text-k5-verified-swap38-p0.88-k5",
            f"{SCREEN}::g37-text-k5-verified-swap37-p0.80-k5",
        ],
        "outcome": (
            "The family ladder stops at 3.7. On the identical 791-candidate union, "
            "the 3.8 verifier reaches 0.9258 @20 m at (0.88, k5), P 0.9335 / R "
            "0.9182 / tile-MCC 0.8218 on 421 detections: against the all-3.7 stack "
            "that is dF1 -0.0007 at p = 0.7769, and against the carried Gemini-3 "
            "verifier +0.0119 at p = 0.0969. E1 CONFIRMED — a tie, and the "
            "pre-named informative outcome did not fire, so the verifier-model "
            "policy stays shut and the 55-map board is untouched. The tie is not "
            "flat on every axis: 3.8 buys +0.0140 of tile-MCC over 3.7 (0.8218 vs "
            "0.8078) while losing 0.0007 of F1, precision-led as its point implies. "
            "E3 is FALSIFIED in the opposite direction — 76 thinking tokens per "
            "candidate in the verifier seat against the 3.7 verifier's 106, and only "
            "1.1x in the proposer probe (307 vs 275 t/tile), so 'newer' bought LESS "
            "thinking, not more. E4 is only partly confirmed, and the check that "
            "settles it also corrects the campaign's first reading: the argmax does "
            "sit at 0.88 rather than at 3.7's 0.80/0.85 or Gemini-3's 0.15/0.20, but "
            "the surface is flat — every k=5 point from prob_t 0.20 to 0.92 lies "
            "within 0.0022 of the best — AND the 3.7 verifier is equally flat on the "
            "same union (0.9243-0.9265 over that band, spread 0.0022, "
            "swap37/sweep_20m.csv), whereas the carried Gemini-3 verifier is sharply "
            "peaked (0.8446-0.8942, spread 0.0497). Threshold insensitivity is "
            "therefore a 3.7/3.8-generation property, not a 3.8 novelty. E2 is "
            "untested: the PI ruled STOP after Arm V, so Arm P (~$9.6) and Arm S "
            "(~$1) were not run; total spend was ~$0.85 flex token-basis. Gotchas "
            "recorded on the card: run_pv.py verify stamps cost_basis 'list' with "
            "discount 1.0 even under --service-tier flex; the verify path counts "
            "each retried server error as a parse failure (803 = retries_total); and "
            "cleanup overwrote run.meta.json again, the main-run meta surviving as "
            "run.meta.main-2026-09-04.json. Obs 448."),
        "paper_section": "Results",
        "output_path": "results/gemini38-screen-2026-09-04/armV",
        "working_notes_obs": [
            "Obs 448 — Gemini 3.8 Flash ties the 3.7 stack in the verifier seat"],
        "manually_verified_at": None,
    },
]

# --------------------------------------------------------------------------- #
# Gates: committed metrics each condition's evaluation must reproduce.
# label → (gate buffer in metres, committed F1, tolerance, expected n_detections)
# --------------------------------------------------------------------------- #

GATES = {
    "g37-text-k5-verified-carried-p0.10-k5": (20, 0.9138920780711826, 1e-4, 443),
    "g37-text-k10-verified-carried-p0.10-k10": (20, 0.9142185663924794, 1e-4, 423),
    "g37-text-k5-verified-swap37-p0.80-k5": (20, 0.9264877479579929, 1e-4, 429),
    "g37-text-k5-verified-swap38-p0.88-k5": (20, 0.9257950530035335, 1e-4, 421),
    "g37-image-k5-verified-carried-p0.10-k5": (20, 0.9254079254079255, 1e-4, 430),
    "g37-image-k5-verified-swap37-p0.90-k5": (20, 0.9308323563892146, 1e-4, 425),
    "g384-ov192-k10-verified37-p0.98-k10": (20, 0.9140049140049139, 1e-4, 386),
    "arm1-n5-carried-p0.10-k5-canonical-gt": (50, 0.8493598998941189, 1e-9, 5229),
    "arm1-n5-carried-p0.10-k5-standardised-gt": (50, 0.8550, 1e-9, 5229),
    "arm2-n5-carried-p0.80-k5-canonical-gt": (50, 0.8763160484109023, 1e-9, 5003),
    "arm2-n5-carried-p0.80-k5-standardised-gt": (50, 0.8825, 1e-9, 5003),
    "g384-ov192-55map-k10-verified37-p0.98-k10-canonical-gt":
        (50, 0.8656176908356368, 1e-9, 4246),
    "g384-ov192-55map-k10-verified37-p0.98-k10-standardised-gt":
        (50, 0.8732, 1e-9, 4246),
}


# --------------------------------------------------------------------------- #
# Canonical-chain adapter (the register_pass1_adapt.py transform)
# --------------------------------------------------------------------------- #

def adapt_canonical(eval_dir: Path, detections: Path) -> str:
    """Write the generator-shape ``evaluation.json`` beside a corrected-F1 summary.

    A pure deterministic transform of the engine's ``summary.json``: per-``R_m`` rows
    become ``summary.buffers`` entries with the engine's percentile CI, and
    ``summary.tile_classification`` is pinned to the 50 m headline row. Nothing is
    recomputed and no metric is invented.

    Args:
        eval_dir: directory holding the engine's ``summary.json``.
        detections: the scored detections GeoJSON, for the feature count.

    Returns:
        A one-line report of what was written.
    """
    summary = json.loads((eval_dir / "summary.json").read_text())
    buffers = []
    headline_tc = None
    for row in summary["results"]:
        excludes = not (row["F1_CI"][0] <= row["F1"] <= row["F1_CI"][1])
        buffers.append({
            "buffer_metres": row["R_m"], "f1": row["F1"],
            "precision": row["precision"], "recall": row["recall"],
            "f1_ci_lower": row["F1_CI"][0], "f1_ci_upper": row["F1_CI"][1],
            "f1_ci_method": "percentile",
            "ci_unreliable": excludes,
            "ci_excludes_point": excludes,
            "ci_flag_basis": "measured-exclusion-only",
        })
        if row["R_m"] == HEADLINE_BUFFER_M:
            tc = row.get("tile_classification", {})
            headline_tc = {
                "mcc": tc.get("mcc"),
                "sensitivity": tc.get("sensitivity"),
                "specificity": tc.get("specificity"),
                "confusion": {"tp": tc.get("tp"), "tn": tc.get("tn"),
                              "fp": tc.get("fp"), "fn": tc.get("fn")},
            }
    n_det = len(json.loads(detections.read_text())["features"])
    # input_files is COPIED from the engine's own metadata.input_paths (absolute
    # paths, made repository-relative), never inferred. Without it the register's
    # drift check (scripts/verify_run_conditions.py) cannot link the eval to the
    # detections it scored and reports eval-detections-mismatch plus
    # scope-uncheckable — which is exactly what the four Pass-1 canonical rows
    # written by scripts/register_pass1_adapt.py still do.
    input_paths = (summary.get("metadata") or {}).get("input_paths") or {}
    input_files: dict[str, object] = {}
    if input_paths.get("detections"):
        input_files["detections"] = [
            str(Path(input_paths["detections"]).relative_to(REPO))]
    if input_paths.get("bounds"):
        input_files["bounds"] = str(Path(input_paths["bounds"]).relative_to(REPO))
    if input_paths.get("student_gt"):
        input_files["ground_truth"] = str(
            Path(input_paths["student_gt"]).relative_to(REPO))
    out = {
        "summary": {"buffers": buffers, "tile_classification": headline_tc,
                    "n_detections": n_det},
        "_metadata": {
            "adapted_by": "scripts/register_gemini37_author.py",
            "source": str((eval_dir / "summary.json").relative_to(REPO)),
            "input_files": input_files,
            "note": ("Deterministic transform of the corrected-F1 engine summary "
                     "(S105 adapter pattern, as scripts/register_pass1_adapt.py); "
                     "tile_classification pinned to the 50 m headline row; nothing "
                     "recomputed. input_files is copied verbatim from the engine's "
                     "metadata.input_paths so the register's drift check can link "
                     "this eval to the detections and bounds it actually scored."),
        },
    }
    (eval_dir / "evaluation.json").write_text(json.dumps(out, indent=1) + "\n")
    b50 = next(b for b in buffers if b["buffer_metres"] == HEADLINE_BUFFER_M)
    return (f"  {eval_dir.relative_to(REPO)}: F1@50 {b50['f1']:.6f} n={n_det} "
            f"tc={'ok' if headline_tc and headline_tc['confusion']['tp'] else 'MISSING'}")


# --------------------------------------------------------------------------- #
# Gates
# --------------------------------------------------------------------------- #

def _all_condition_specs() -> list[tuple[str, dict]]:
    """Return every ``(run_id, spec)`` pair this script authors."""
    pairs: list[tuple[str, dict]] = []
    for run_id, dec in DECOMPOSITIONS.items():
        pairs.extend((run_id, c) for c in dec["conditions"])
    pairs.extend((GRID, c) for c in GRID_CONDITION_ADD)
    pairs.extend((STRIDE, c) for c in STRIDE_CONDITION_ADD)
    return pairs


def check_artefacts(tolerate: set[str] | None = None) -> list[str]:
    """Existence-check every path this script names. Returns a list of problems.

    Args:
        tolerate: paths whose absence is expected (the canonical ``evaluation.json``
            files the adapter writes, when running as a dry run).
    """
    tolerate = tolerate or set()
    missing: list[str] = []
    dirs = {r["run_id"]: r["directory_path"] for r in REGISTRY_ROWS}
    dirs[GRID] = "outputs/grid-2026-08-18"
    dirs[STRIDE] = "outputs/stride-55map-2026-08-25"
    for run_id, dec in DECOMPOSITIONS.items():
        run_dir = REPO / dirs[run_id]
        if not run_dir.exists():
            missing.append(dirs[run_id])
        for spec in {**dec["proposer_pools"], **dec["verifier_passes"]}.values():
            if not (run_dir / spec["path"]).exists():
                missing.append(f"{dirs[run_id]}/{spec['path']}")
    for run_id, adds in ((GRID, GRID_VERIFIER_ADD), (STRIDE, STRIDE_VERIFIER_ADD)):
        for spec in adds.values():
            if not (REPO / dirs[run_id] / spec["path"]).exists():
                missing.append(f"{dirs[run_id]}/{spec['path']}")
    for _run_id, spec in _all_condition_specs():
        for key in ("eval_path", "detections"):
            if spec[key] not in tolerate and not (REPO / spec[key]).exists():
                missing.append(spec[key])
    return missing


def check_gates() -> list[str]:
    """Re-read each evaluation and confirm it reproduces its committed record."""
    problems: list[str] = []
    for _run_id, spec in _all_condition_specs():
        label = spec["label"]
        if label not in GATES:
            problems.append(f"{label}: no committed gate declared")
            continue
        buffer_m, committed, tol, n_expected = GATES[label]
        doc = json.loads((REPO / spec["eval_path"]).read_text())
        summary = doc.get("summary", {})
        row = next((b for b in summary.get("buffers", [])
                    if b["buffer_metres"] == buffer_m), None)
        if row is None:
            problems.append(f"{label}: no {buffer_m} m row in {spec['eval_path']}")
            continue
        if abs(row["f1"] - committed) > tol:
            problems.append(
                f"{label}: F1@{buffer_m} {row['f1']} != committed {committed} "
                f"(tolerance {tol})")
        tc = summary.get("tile_classification") or {}
        conf = tc.get("confusion") or {}
        if any(conf.get(k) is None for k in ("tp", "tn", "fp", "fn")):
            problems.append(f"{label}: incomplete tile confusion matrix")
        n_eval = summary.get("n_detections")
        n_geo = len(json.loads((REPO / spec["detections"]).read_text())["features"])
        if n_eval != n_geo or n_geo != n_expected:
            problems.append(
                f"{label}: n_detections eval={n_eval} geojson={n_geo} "
                f"expected={n_expected}")
    return problems


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> int:
    """Gate, then (with ``--write``) author the register rows."""
    ap = argparse.ArgumentParser(description="Author the Gemini 3.7/3.8 register rows.")
    ap.add_argument("--write", action="store_true",
                    help="Author the rows (default is a dry run).")
    args = ap.parse_args()

    rc = json.loads((REPO / "results/run-conditions.json").read_text())
    rr = json.loads((REPO / "results/run-registry.json").read_text())
    rf = json.loads((REPO / "results/run-facts.json").read_text())
    ra = json.loads((REPO / "results/run-analyses.json").read_text())

    # --- gate 1: identifier collisions -------------------------------------- #
    for run_id in DECOMPOSITIONS:
        if (run_id in rc["decomposition"] or run_id in rf["facts"]
                or any(r["run_id"] == run_id for r in rr["registry"])):
            raise SystemExit(f"REFUSED: run {run_id} already registered")
    existing_labels = {
        (run_id, c["label"])
        for run_id, dec in rc["decomposition"].items() for c in dec["conditions"]
    }
    for run_id, spec in _all_condition_specs():
        if (run_id, spec["label"]) in existing_labels:
            raise SystemExit(f"REFUSED: condition {run_id}::{spec['label']} exists")
    existing_analyses = {a["analysis_id"] for a in ra["analyses"]}
    for a in ANALYSES:
        if a["analysis_id"] in existing_analyses:
            raise SystemExit(f"REFUSED: analysis {a['analysis_id']} exists")
    for run_id, adds in ((GRID, GRID_VERIFIER_ADD), (STRIDE, STRIDE_VERIFIER_ADD)):
        for key in adds:
            if key in rc["decomposition"][run_id]["verifier_passes"]:
                raise SystemExit(f"REFUSED: verifier pass {run_id}/{key} exists")

    # --- the canonical adapter must run before the artefact/gate checks ----- #
    print("=== canonical-chain adapter (deterministic transform) ===")
    if args.write:
        for eval_dir, det in CANONICAL_CELLS:
            print(adapt_canonical(REPO / eval_dir, REPO / det))
    else:
        for eval_dir, _det in CANONICAL_CELLS:
            state = "exists" if (REPO / eval_dir / "evaluation.json").exists() else "TO WRITE"
            print(f"  {eval_dir}/evaluation.json — {state}")

    # --- gate 2: artefacts --------------------------------------------------- #
    pending = set() if args.write else {
        f"{d}/evaluation.json" for d, _ in CANONICAL_CELLS
        if not (REPO / d / "evaluation.json").exists()
    }
    missing = check_artefacts(pending)
    if missing:
        raise SystemExit("REFUSED — missing artefacts:\n  " + "\n  ".join(missing))

    # --- gates 3 and 4: committed metrics + detection counts ----------------- #
    if args.write or all((REPO / d / "evaluation.json").exists()
                         for d, _ in CANONICAL_CELLS):
        problems = check_gates()
        if problems:
            raise SystemExit("REFUSED — gate failures:\n  " + "\n  ".join(problems))
        print("gates: every evaluation reproduces its committed F1 and "
              "detection count.")
    else:
        print("gates: SKIPPED in dry run (canonical evaluation.json not yet "
              "written); re-run with --write.")

    n_conditions = len(_all_condition_specs())
    print(f"\n{len(REGISTRY_ROWS)} runs, {n_conditions} conditions "
          f"({len(GRID_CONDITION_ADD) + len(STRIDE_CONDITION_ADD)} into existing "
          f"decompositions), {len(ANALYSES)} analyses.")
    print(f"NOT authored (PI ruling 3, schema-blocked): {CANONICAL_BN5_GAP}")

    if not args.write:
        print("dry run — re-run with --write")
        return 0

    rc["decomposition"].update(DECOMPOSITIONS)
    rc["decomposition"][GRID]["verifier_passes"].update(GRID_VERIFIER_ADD)
    rc["decomposition"][GRID]["conditions"].extend(GRID_CONDITION_ADD)
    rc["decomposition"][STRIDE]["verifier_passes"].update(STRIDE_VERIFIER_ADD)
    rc["decomposition"][STRIDE]["conditions"].extend(STRIDE_CONDITION_ADD)
    rr["registry"].extend(REGISTRY_ROWS)
    rf["facts"].update(FACTS)
    ra["analyses"].extend(ANALYSES)

    (REPO / "results/run-conditions.json").write_text(json.dumps(rc, indent=1) + "\n")
    (REPO / "results/run-registry.json").write_text(json.dumps(rr, indent=1) + "\n")
    (REPO / "results/run-facts.json").write_text(json.dumps(rf, indent=1) + "\n")
    (REPO / "results/run-analyses.json").write_text(json.dumps(ra, indent=1) + "\n")
    print("WRITTEN — now run: python scripts/generate_post_run_report.py --all --write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
