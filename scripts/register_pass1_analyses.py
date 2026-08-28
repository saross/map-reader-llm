#!/usr/bin/env python3
"""
Registration Pass 1: author the five analysis rows.

Appends to `results/run-analyses.json` (refuses existing ids); rows
enter UNSIGNED (`manually_verified_at: null`) for the PI's interactive
walk, per the hand-verified registry discipline. Sweep-interior points
are governed by these rows (PI ruling 2026-08-28), promoted to
condition rows on citation.

Usage::

    python scripts/register_pass1_analyses.py [--write]

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RA = REPO / "results/run-analyses.json"

PB = "stride-phaseb-2026-08-25"
PC = "stride-phasec-2026-08-25"
S55 = "stride-55map-2026-08-25"
GRID = "grid-2026-08-18"

ROWS = [
    {
        "analysis_id": "stride-plateau-2026-08-25",
        "type": "board",
        "_note": ("The stride programme's three $0 follow-ups "
                  "(scripts/stride_plateau_analyses.py, sapphire): the "
                  "13-cell tiered board (9 geometry cells' verified bests "
                  "+ 4 incumbents; round-robin tile-swap 10k/seed 42, "
                  "BH q=0.05, greedy cliques), the k-of-10 curves, and "
                  "the free first-N ladder with validated probability "
                  "inheritance. Artefact: results/stride-2026-08-25/"
                  "plateau_analyses.json; prose: results/stride-2026-08-25/"
                  "findings.md. Sweep interiors are governed here "
                  "(PI ruling 2026-08-28)."),
        "_prereg_rationale": ("Post-hoc E41-class geometry exploration; "
                              "extends H13's registered single-pass "
                              "overlap design into the K-pass regime."),
        "conditions_compared": [
            f"{PB}::g512-ov176-k10-verified-p0.15-k6",
            f"{PB}::g384-ov128-k10-verified-p0.15-k8",
            f"{PB}::g256-ov064-k10-verified-p0.15-k8",
            f"{PB}::g512-ov320-k10-verified-p0.15-k10",
            f"{PC}::g384-ov240-k10-verified-p0.15-k10",
            f"{GRID}::g512-ov064-k10-verified-p0.15-k5",
            f"{GRID}::g512-ov256-k10-verified-p0.15-k9",
            f"{GRID}::g384-ov048-k10-verified-p0.20-k7",
            f"{GRID}::g384-ov192-k10-verified-p0.15-k10",
        ],
        "hypothesis_refs": ["H13"],
        "preregistered": False,
        "deviations": [],
        "predicted_outcome": ("Open question as commissioned: plateau or "
                              "winner; where is the interior stride "
                              "optimum?"),
        "tie_set": None,
        "outcome": ("PLATEAU-NOT-WINNER: 12 of 13 cells one statistical "
                    "tier; only g512_ov064 (12.5% overlap) drops. 384 px "
                    "at-or-above at every stride; interior optimum strides "
                    "192-256. Obs 435."),
        "paper_section": "R-geometry",
        "output_path": "results/stride-2026-08-25/plateau_analyses.json",
        "working_notes_obs": [435],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "stride-winner-ladder-exact-2026-08-25",
        "type": "comparison",
        "_note": ("Exact re-verification of the winner cell's first-N "
                  "unions (N in {1,3,5}; ~$3.4 flex, PI-approved "
                  "2026-08-25) — replaces inheritance with real verifier "
                  "calls on the full unions incl. inheritance-unmatched "
                  "clusters. Verifier passes nested under "
                  "stride-phaseb-2026-08-25 (verify_k1/k3/k5); condition "
                  "rows registered for all three rungs. Artefact: "
                  "plateau_analyses.json winner_ladder_exact."),
        "_prereg_rationale": ("Validates the free-ladder inheritance "
                              "method with exact measurement at the "
                              "deployment-decision rungs."),
        "conditions_compared": [
            f"{PB}::g384-ov128-ladder-n1-verified-p0.15-k1",
            f"{PB}::g384-ov128-ladder-n3-verified-p0.15-k3",
            f"{PB}::g384-ov128-ladder-n5-verified-p0.15-k4",
            f"{PB}::g384-ov128-k10-verified-p0.15-k8",
        ],
        "hypothesis_refs": ["H13", "H3"],
        "preregistered": False,
        "deviations": [],
        "predicted_outcome": ("Inheritance-estimated rungs within ~0.008 "
                              "of exact (the GS validation bound)."),
        "tie_set": None,
        "outcome": ("Exact rungs: N=1 0.8677; N=3 0.8911 (~$2.64 "
                    "all-in); N=5 0.8856. N=3 within noise of K=10 "
                    "(0.8982) at GS scale — the pass-count saturation "
                    "the 55-map ladders later confirmed at deployment. "
                    "Obs 436."),
        "paper_section": "R-geometry",
        "output_path": "results/stride-2026-08-25/plateau_analyses.json",
        "working_notes_obs": [436],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "stride55-sweep-oracle-2026-08-27",
        "type": "comparison",
        "_note": ("The portfolio card's § 3 secondary item 1 "
                  "(scripts/stride55_sweep_oracle.py, sapphire, $0): full "
                  "(prob_t x k) sweeps at 50 m vs the canonical extended "
                  "GT, 1e-6 replication gates against the committed "
                  "primaries, deployment oracles, paired A-vs-B "
                  "(per-sheet sign-swap 10k/seed 42). Artefacts: "
                  "results/stride55-2026-08-27/sweep_oracle.json + "
                  "per-cell sweep_50m.csv. Sweep interiors governed "
                  "here (PI ruling 2026-08-28); the oracle points are "
                  "registered as conditions."),
        "_prereg_rationale": ("Registered-by-commit predictions P1/P3/P5/"
                              "P6/P8 (card § 3b, committed before "
                              "launch)."),
        "conditions_compared": [
            f"{S55}::g384-ov128-55map-verified-carried-p0.15-k8-canonical-gt",
            f"{S55}::g384-ov128-55map-verified-oracle-p0.15-k7-canonical-gt",
            f"{S55}::g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt",
            f"{S55}::g384-ov192-55map-verified-oracle-p0.20-k9-canonical-gt",
        ],
        "hypothesis_refs": ["H13"],
        "preregistered": False,
        "deviations": [],
        "predicted_outcome": ("P1: A optimum (0.15,k8), drift only "
                              "downward (6-7). P3: B (0.15,k10), likely "
                              "break downward (8-9). P5: headlines "
                              "0.80-0.85, neither sig below 0.8152. "
                              "P6: A~B tie. P8: prob 0.15 everywhere."),
        "tie_set": None,
        "outcome": ("P1 PASS (oracle (0.15,k7)); P3 PASS-on-k ((0.20,"
                    "k9)); P5 PASS (0.8326/0.8422, both ABOVE the "
                    "incumbent); P6 FAIL — the pre-named informative "
                    "failure: B beats A (primaries -0.0096 p=0.0147; "
                    "oracles -0.0141 p=0.0001; BH-robust). P8 fail-by-"
                    "letter (B argmax 0.20 by +0.0009). Transfer taxes "
                    "+0.0036/+0.0081 vs the incumbent's +0.0324 — the "
                    "tax COLLAPSED. Findings: results/stride55-2026-08-27/"
                    "findings.md; Obs 437."),
        "paper_section": "R-deployment",
        "output_path": "results/stride55-2026-08-27/sweep_oracle.json",
        "working_notes_obs": [437],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "stride55-ladder-2026-08-27",
        "type": "comparison",
        "_note": ("Card § 3 secondary item 2 (scripts/stride55_ladder.py, "
                  "sapphire, $0): first-N rungs N in {1,3,5} for both "
                  "runs, K=10 verifier inheritance (GS-validated "
                  "±0.008), gates = exact union rebuild + 1e-6 primary "
                  "reproduction; P7 saturation permutations at carried "
                  "and oracle points. Artefacts: results/stride55-"
                  "2026-08-27/ladder.json + per-cell ladder_sweep_50m.csv. "
                  "Rung interiors governed here; the deployment-cited "
                  "rungs were later promoted to condition rows via the "
                  "final board (Pass 2) per the PI's rung ruling."),
        "_prereg_rationale": ("Registered-by-commit predictions P2/P4/P7 "
                              "(card § 3b)."),
        "conditions_compared": [
            f"{S55}::g384-ov128-55map-verified-carried-p0.15-k8-canonical-gt",
            f"{S55}::g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt",
        ],
        "hypothesis_refs": ["H13", "H3"],
        "preregistered": False,
        "deviations": [],
        "predicted_outcome": ("P2: A N=5 optimum (0.15,k4). P4: B N=5 "
                              "(0.15,k5). P7: N=5 within noise of N=10, "
                              "both runs."),
        "tie_set": None,
        "outcome": ("P2 PASS EXACT (rung oracle = the GS-carried point). "
                    "P4 PASS-on-k (k5 exact; prob argmax 0.20 by "
                    "+0.0012). P7 PASS at the carried points (A -0.0004 "
                    "p=0.82; B +0.0016 p=0.32 — B's N=5 carried ABOVE "
                    "its N=10 carried); small real oracle residue "
                    "(-0.0040 p=0.0131 / -0.0053 p=0.0003, BH-sig). "
                    "B saturates at N=3 (final-board follow-up). "
                    "Obs 437/438."),
        "paper_section": "R-deployment",
        "output_path": "results/stride55-2026-08-27/ladder.json",
        "working_notes_obs": [437, 438],
        "manually_verified_at": None,
    },
    {
        "analysis_id": "stride55-a5-vs-b5-2026-08-27",
        "type": "comparison",
        "_note": ("PI-requested post-hoc (2026-08-28, interactive; "
                  "scripts/stride55_a5_vs_b5.py): paired A-vs-B at the "
                  "N=5 carried points — the deployment-recommendation "
                  "rung the card's declared family did not cover. Gates: "
                  "per-map totals reproduce the ladder carried F1s to "
                  "1e-6. Labelled outside the declared six-test family; "
                  "BH re-run over seven in the findings doc."),
        "_prereg_rationale": ("Post-hoc addition at PI request; clearly "
                              "labelled as such in the findings doc's "
                              "BH treatment."),
        "conditions_compared": [
            f"{S55}::g384-ov128-55map-verified-carried-p0.15-k8-canonical-gt",
            f"{S55}::g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt",
        ],
        "hypothesis_refs": ["H13"],
        "preregistered": False,
        "deviations": ["Post-hoc to the card's declared comparison "
                       "family; BH-adjusted within the expanded "
                       "seven-test family (survives, rank 3)."],
        "predicted_outcome": None,
        "tie_set": None,
        "outcome": ("B N=5 carried beats A N=5 carried: dF1 -0.0116, "
                    "p=0.0042 (10k sign-swap, seed 42) — the ~$37 "
                    "A-to-B step at N=5 buys a real ~0.012. Artefact: "
                    "results/stride55-2026-08-27/a5_vs_b5.json."),
        "paper_section": "R-deployment",
        "output_path": "results/stride55-2026-08-27/a5_vs_b5.json",
        "working_notes_obs": [437],
        "manually_verified_at": None,
    },
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    doc = json.loads(RA.read_text())
    have = {r["analysis_id"] for r in doc["analyses"]}
    for r in ROWS:
        if r["analysis_id"] in have:
            raise SystemExit(f"REFUSED: {r['analysis_id']} exists")
    print(f"{len(ROWS)} analysis rows ready:")
    for r in ROWS:
        print(f"  {r['analysis_id']} ({r['type']}) -> {r['output_path']}")
    if not args.write:
        print("dry run — re-run with --write")
        return 0
    doc["analyses"].extend(ROWS)
    RA.write_text(json.dumps(doc, indent=1) + "\n")
    print("WRITTEN: run-analyses.json (+5, all unsigned)")
    return 0


if __name__ == "__main__":
    return_code = main()
    raise SystemExit(return_code)
