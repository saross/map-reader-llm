#!/usr/bin/env python3
"""Author the H10 and H12-v2 analysis rows (S134 D17 reconciliation, Item 3).

Appends two new specs to results/run-analyses.json. Both hypotheses ran to
completion with scored conditions but were referenced by zero analyses —
the D17 inventory's 'invisible factors' defect. Outcomes are authored from
the committed analysis summaries (results/h10/analysis_summary.md,
results/h12-v2/analysis_summary.md), both NULL as the inventory records.

Run from the repo root after the vocabulary-v2 migration has landed.
"""

import json
from pathlib import Path

SIDECAR = Path("results/run-analyses.json")

NEW_ROWS = [
    {
        "analysis_id": "h10-pool-size",
        "type": "comparison",
        "_note": (
            "H10 v2 (calibration-pool size) — the registered nested pool "
            "design (20 ⊂ 40 ⊂ 80 ⊂ 160) under production carry-forward "
            "settings on the 327-tile Era 3 holdout. Authored S134 "
            "(2026-08-17) to discharge the D17 inventory's 'invisible "
            "factor' defect: the run and its scored conditions existed in "
            "the manifests but no analysis row referenced them. Source of "
            "truth: results/h10/analysis_summary.md (headline at § "
            "'Headline result — pool-size null under PV'; caveats § "
            "'Caveats'). The PV contrast is pool_020 vs pool_160 only "
            "(smaller pools consensus-indistinguishable, ΔF1 < 0.01, and "
            "not separately PV-swept — summary caveat 1)."
        ),
        "_prereg_rationale": (
            "registered-exploratory: H10 is registered exploratory Tier B "
            "(osf/preregistration.md:906); the registered nested-pool "
            "design (osf:912-926) executed with the registered pool sizes "
            "unchanged, under production carry-forward settings rather "
            "than the registered image-only baseline (E49) on the "
            "expanded 327-tile holdout (E50). Deviations set per D17 "
            "inventory d17-inventory-h9-h12.md § 6 recommendation."
        ),
        "conditions_compared": [
            "h10::greedy-pool-020",
            "h10::greedy-pool-040",
            "h10::greedy-pool-080",
            "h10::greedy-pool-160",
            "h10::verified-pool-160",
        ],
        "hypothesis_refs": ["H10"],
        "preregistered": "registered-exploratory",
        "deviations": ["E49", "E50", "E13", "E37", "E45"],
        "predicted_outcome": (
            "The registration expects larger calibration pools to surface "
            "more diverse or representative hard examples, improving the "
            "resulting library's effectiveness (osf/preregistration.md:908), "
            "characterised as F1 on holdout as a function of pool size with "
            "a diminishing-returns curve (osf:928-932)."
        ),
        "predicted_outcome_amended": None,
        "tie_set": [],
        "outcome": (
            "NULL under the production pipeline: four nested calibration "
            "pools (20 ⊂ 40 ⊂ 80 ⊂ 160) produce post-verifier F1s "
            "indistinguishable within sampling noise — pool_020 PV 0.727 vs "
            "pool_160 PV 0.722 (ΔF1 +0.005, p = 0.845). At consensus-only, "
            "pool_160 leads by +0.020 via a higher-precision operating "
            "point; the verifier compresses the lead to near zero by "
            "filtering pool_020's noisier consensus output. The three "
            "smaller pools are consensus-indistinguishable (ΔF1 < 0.01, "
            "Obs 236). CAVEAT (E49): this is a null for the production "
            "carry-forward pipeline, NOT for the registered image-only "
            "baseline — do not read it as 'pool size is null under the "
            "original prereg settings'. Part of the library-axis closure "
            "with H8 v2 and H12 v2 (45-pair cross-hypothesis matrix, zero "
            "significant pairs, min adj. p = 0.966 — Obs 240)."
        ),
        "paper_section": "Results",
        "output_path": "results/h10/analysis_summary.md",
        "working_notes_obs": [
            "Obs 236 — H10 pool size is a null: 20-tile calibration matches 160-tile under PV",
            "Obs 235 — formal retraction of the v1 H10/H12 probe findings (config-intent mismatch)",
        ],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "h12-v2-hp-hn-ratio",
        "type": "comparison",
        "_note": (
            "H12 v2 (hard-positive to hard-negative ratio) — the registered "
            "R1/R2/R3 condition matrix (2:6 / 4:4 / 6:2 at total hard = 8) "
            "at 384 px / T = 0.7 / HIGH thinking / K = 5 consensus on the "
            "327-tile Era 3 scope. Authored S134 (2026-08-17) to discharge "
            "the D17 inventory's 'invisible factor' defect. Source of "
            "truth: results/h12-v2/analysis_summary.md (§ 1 executive "
            "summary; § 2 headline; § 8 caveats). Greedy t = 4 is the "
            "primary aggregation per Decision 26 / E52 (PI preference "
            "2026-04-15), WBF variant C reported alongside. R2 (balanced) "
            "is byte-identical to H8 v2 Scale-8 pool_160_hp4hn4 — a shared "
            "anchor, not an independent replicate (§ 8.2)."
        ),
        "_prereg_rationale": (
            "registered-exploratory: H12 is registered exploratory Tier B "
            "(osf/preregistration.md:982); the exact registered condition "
            "matrix (osf:994-1000) was executed row for row and the "
            "registered primary and secondary analyses performed; the "
            "registered trigger (run if H8 shows library size matters, "
            "osf:1010) was deviated from — run despite the H8 null, "
            "disclosed in E52. Deviations set per D17 inventory "
            "d17-inventory-h9-h12.md § 6 recommendation."
        ),
        "conditions_compared": [
            "h12-v2::greedy-r1-hn-heavy",
            "h12-v2::greedy-r2-balanced",
            "h12-v2::greedy-r3-hp-heavy",
            "h12-v2::wbf-r1-hn-heavy",
            "h12-v2::wbf-r2-balanced",
            "h12-v2::wbf-r3-hp-heavy",
        ],
        "hypothesis_refs": ["H12"],
        "preregistered": "registered-exploratory",
        "deviations": ["E13", "E52", "E49", "E50", "E51", "E45"],
        "predicted_outcome": (
            "The registration expects ratio effects in both directions: "
            "higher HP:HN may improve recall (more positive guidance), "
            "lower HP:HN may improve precision (more exclusion examples), "
            "with the optimum possibly depending on library size or "
            "baseline error profile (osf/preregistration.md:986-990)."
        ),
        "predicted_outcome_amended": None,
        "tie_set": [
            "h12-v2::greedy-r1-hn-heavy",
            "h12-v2::greedy-r2-balanced",
            "h12-v2::greedy-r3-hp-heavy",
        ],
        "outcome": (
            "Three-way NULL after BH-FDR at q = 0.05: all three registered "
            "pairwise contrasts non-significant (adjusted p 0.500–0.717); "
            "condition F1s in a tight 0.688–0.717 band with fully "
            "overlapping 95% bootstrap CIs at the greedy t = 4 primary "
            "operating point. The registered directional prediction "
            "(higher HP:HN improves recall) is FALSIFIED, not merely "
            "unconfirmed: R3 (HP-heavy) recall 0.618 is not higher than R2 "
            "(0.624) or R1 (0.621); precision differences (R2 0.843 > R1 "
            "0.825 > R3 0.776) are within CI overlap. Trigger deviation: "
            "run without H8 showing library-size significance (E52) — the "
            "null is real, the preregistered-closure framing requires the "
            "E52 disclosure (analysis_summary.md § 8.1). Era 3 (327-tile) "
            "scope only. Closes the library-design axis with H8 v2 and "
            "H10 v2 (Obs 239, Obs 240)."
        ),
        "paper_section": "Results",
        "output_path": "results/h12-v2/analysis_summary.md",
        "working_notes_obs": [
            "Obs 239 — H12 v2 HP:HN ratio is a null: all three pairwise contrasts fail after BH-FDR",
            "Obs 240 — library-design axis definitively null: 45-pair cross-hypothesis matrix, zero significant",
        ],
        "manually_verified_at": None,
    },
]


def main() -> None:
    data = json.loads(SIDECAR.read_text())
    existing = {r["analysis_id"] for r in data["analyses"]}
    for row in NEW_ROWS:
        if row["analysis_id"] in existing:
            raise SystemExit(f"{row['analysis_id']} already present — refusing.")
    data["analyses"].extend(NEW_ROWS)
    SIDECAR.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(f"Added {len(NEW_ROWS)} rows; sidecar now {len(data['analyses'])} analyses.")


if __name__ == "__main__":
    main()
