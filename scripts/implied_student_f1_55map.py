#!/usr/bin/env python3
"""
Phase 0b: the implied 55-map student F1, propagated honestly.

Card § 3 item 0b (`planning/student-baseline-2026-08-31.md`): a
defensible interval for novice-cohort F1 on the 55-map corpus against
the canonical reference, replacing the informal "P=1, R~0.89 →
F1~0.94" reading with an interval that carries:

1. The headline FN rate's bootstrap uncertainty (0.0887, CI
   0.0692–0.1135; `results/student-gt-fn-rate-analysis/
   bootstrap_summary.json`).
2. The VLM-recall adjustment (highest-recall corrected run, R =
   0.7958, CI 0.7836–0.8077) WITH a miss-correlation factor k: the
   standard adjustment assumes the model finds student-missed mounds
   at its average recall; Obs 361 measured miss-correlation 1.5–1.7×
   on GS (double-misses cluster), so P(model finds | student missed)
   = 1 − k(1 − R). k is drawn uniform on [1.0, 1.7] — from
   "independence holds" to the GS-measured upper factor.
3. The review-derived precision bound (targeted review demoted ~0.5%
   of touched points; genuine demotions rarer still — Obs 443):
   precision drawn uniform on [0.995, 1.0].

Under near-zero FPs the student-anchored FN rate ≈ the truth-anchored
rate (truth ≈ GT + FN), so cohort recall ≈ 1 − corrected FN rate.

Monte Carlo (100,000 draws, seed 42): FN_headline ~ Normal(0.0887,
sd from CI/3.92) truncated ≥ 0; FN_true = FN_headline / (1 − k(1−R));
F1 from (P, 1 − FN_true).

CAVEATS carried in the output: (a) circularity — the canonical
reference is 92% the students' own layer, so this is generosity-
bounded above; (b) the double-miss floor (mounds missed by students
AND model) is excluded by construction — the empty-tile audit
(card § 5) measures it; (c) the FN evidence is 2017+2018 pooled
while per-student rates vary 4x (Obs 443).

Usage::

    python scripts/implied_student_f1_55map.py

Zero API, seconds, local.

Created: 2026-09-01 (Session 145)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BOOTSTRAP = PROJECT_ROOT / "results/student-gt-fn-rate-analysis/bootstrap_summary.json"
OUT_DIR = PROJECT_ROOT / "results/student-baseline-2026-09-01/implied-55map-interval"

N_DRAWS = 100_000
SEED = 42
VLM_RECALL = (0.7958, 0.7836, 0.8077)   # highest-recall corrected run
K_RANGE = (1.0, 1.7)                    # miss-correlation factor (Obs 361)
P_RANGE = (0.995, 1.0)                  # review-derived precision bound
MODEL_ANCHORS = {"arm2-carried-canonical": 0.8763,
                 "arm2-standardised": 0.8825}


def main() -> int:
    boot = json.loads(BOOTSTRAP.read_text())
    headline = boot["strata"]["headline"]
    fn_mean = float(headline["point_estimate"])
    fn_lo = float(headline["ci_low"])
    fn_hi = float(headline["ci_high"])
    fn_sd = (fn_hi - fn_lo) / 3.92

    rng = np.random.default_rng(SEED)
    fn_headline = np.clip(rng.normal(fn_mean, fn_sd, N_DRAWS), 0, None)
    r_mean, r_lo, r_hi = VLM_RECALL
    vlm_r = np.clip(rng.normal(r_mean, (r_hi - r_lo) / 3.92, N_DRAWS),
                    0.01, 0.999)
    k = rng.uniform(*K_RANGE, N_DRAWS)
    p_find = np.clip(1 - k * (1 - vlm_r), 0.05, 1.0)
    fn_true = np.clip(fn_headline / p_find, 0, 0.9)
    recall = 1 - fn_true
    precision = rng.uniform(*P_RANGE, N_DRAWS)
    f1 = 2 * precision * recall / (precision + recall)

    def q(a, p):
        return float(np.percentile(a, p))

    summary = {
        "n_draws": N_DRAWS, "seed": SEED,
        "inputs": {"fn_headline": [fn_mean, fn_lo, fn_hi],
                   "vlm_recall": list(VLM_RECALL),
                   "k_miss_correlation": list(K_RANGE),
                   "precision_bound": list(P_RANGE)},
        "fn_true": {"median": q(fn_true, 50),
                    "ci95": [q(fn_true, 2.5), q(fn_true, 97.5)]},
        "recall": {"median": q(recall, 50),
                   "ci95": [q(recall, 2.5), q(recall, 97.5)]},
        "implied_f1": {"median": q(f1, 50),
                       "ci95": [q(f1, 2.5), q(f1, 97.5)]},
        "model_anchors": MODEL_ANCHORS,
        "gap_to_arm2_canonical": {
            "median": q(f1 - MODEL_ANCHORS["arm2-carried-canonical"], 50),
            "ci95": [q(f1 - MODEL_ANCHORS["arm2-carried-canonical"], 2.5),
                     q(f1 - MODEL_ANCHORS["arm2-carried-canonical"], 97.5)],
            "p_model_at_or_above_students": float(
                (f1 <= MODEL_ANCHORS["arm2-carried-canonical"]).mean())},
        "caveats": [
            "circularity: canonical reference is 92% the students' own "
            "layer — interval is generosity-bounded above",
            "double-miss floor excluded by construction (empty-tile "
            "audit measures it; both recall estimates fall if nonzero)",
            "cohort-pooled; per-student weighted FN rates vary ~4x "
            "(Obs 443)",
        ],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "analysis.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    logger.info("implied 55-map student F1: median %.4f, 95%% [%.4f, %.4f]",
                summary["implied_f1"]["median"],
                *summary["implied_f1"]["ci95"])
    logger.info("gap to arm2 canonical 0.8763: median %+.4f [%+.4f, %+.4f]; "
                "P(model >= students) = %.3f",
                summary["gap_to_arm2_canonical"]["median"],
                *summary["gap_to_arm2_canonical"]["ci95"],
                summary["gap_to_arm2_canonical"]
                ["p_model_at_or_above_students"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
