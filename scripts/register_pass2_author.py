#!/usr/bin/env python3
"""
Registration Pass 2: the final-board standardised cells + analyses.

Appends conditions for the final 23-cell board's non-committed cells
(PI-approved scope; rung ruling 2026-08-28) to their home runs:

- 15 A/B cells (N10/N5 carried + oracles, N3 carried post-hoc,
  N1/N3 oracles) → `stride-55map-2026-08-25`, `-standardised-gt`
  labels;
- the two incumbent oracles the standardised re-sweep MOVED
  (T03 (0.20, k3); TM (0.20, k3)) → their own runs. The coincident
  oracles (TH7, IM, uplift) are the already-registered k3/5of10
  conditions — nothing to add.

Plus two analysis rows (unsigned): the 23-cell final board and the
sensitivity/MDE appendix.

Everything is read programmatically from
`results/55map-final-board-2026-08-27/{cells_manifest.json,
final_board_50m.json, sweeps.json}`; existence-checked; refusal-gated
on duplicate labels.

Usage::

    python scripts/register_pass2_author.py [--write]

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FB = REPO / "results/55map-final-board-2026-08-27"

VF_CONFIG = {
    "variant": "v1",
    "instruction_file": "verify_adversarial.md",
    "model": "gemini-3-flash-preview",
    "thinking_level": "minimal",
    "temperature": 0.0,
}
STD_NOTE = ("Standardised-reference (ruling 21) evaluation on the "
            "shared 8,541-tile frame; final-board cell "
            "(results/55map-final-board-2026-08-27/). Carry-forward "
            "verifier; probabilities inherited from K=10 for N<10 "
            "rungs (GS-validated ±0.008).")

COINCIDENT = {"TH7-oracle", "IM-oracle", "UPL-oracle"}
INCUMBENT_HOME = {"T03-oracle": "55maps-text-high-t0-3-generalisation",
                  "TM-oracle": "55maps-text-min-generalisation"}
AB_CELL = {"A": "g384_ov128_55map", "B": "g384_ov192_55map"}


def parse_point(s: str) -> tuple[float, int]:
    m = re.match(r"\(([\d.]+), k(\d+)\)", s)
    return float(m.group(1)), int(m.group(2))


def build() -> tuple[dict[str, list[dict]], list[dict]]:
    cells = json.loads((FB / "cells_manifest.json").read_text())["cells"]
    board = {c["label"]: c for c in json.loads(
        (FB / "final_board_50m.json").read_text())["cells"]}
    additions: dict[str, list[dict]] = {}
    for m in cells:
        if m["committed_eval"] or m["label"] in COINCIDENT:
            continue
        label = m["label"]
        pt, pk = parse_point(m["point"])
        b = board[label]
        eval_path = f"results/55map-final-board-2026-08-27/cells/{label}/evaluation.json"
        det = m["det"]
        if label in INCUMBENT_HOME:
            run = INCUMBENT_HOME[label]
            n_passes = 5
            cond_label = f"verified-oracle-p{pt:.2f}-k{pk}-standardised-gt"
            note = (f"Standardised-reference deployment ORACLE re-derived "
                    f"by the final-board argmax sweep (moved from the "
                    f"S104 point; F1@50 {b['f1_50']:.4f}). " + STD_NOTE)
        else:
            fam, rung, basis = (label.split("-", 1)[0],
                                label.split("-")[1], label.split("-")[-1])
            run = "stride-55map-2026-08-25"
            n_passes = int(rung[1:])
            posthoc = "posthoc-" if "post-hoc" in m["basis"] else ""
            cond_label = (f"{AB_CELL[fam].replace('_','-')}-{rung.lower()}"
                          f"-{basis}-{posthoc}p{pt:.2f}-k{pk}"
                          "-standardised-gt")
            note = (f"Final-board cell {label} ({m['basis']}, "
                    f"F1@50 {b['f1_50']:.4f}, tier via "
                    f"final_board_50m.json). " + STD_NOTE)
            if posthoc:
                note += (" EMERGENT post-hoc nomination (PI-directed "
                         "2026-08-28): the GS-ladder-selected point, "
                         "evaluated after the N=3 oracle's frontier "
                         "position emerged — see the board's post-hoc "
                         "section.")
        additions.setdefault(run, []).append({
            "label": cond_label,
            "architecture": "proposer-verifier",
            "aggregation": "verified",
            "proposer_pool": (AB_CELL[label.split("-", 1)[0]]
                              if label not in INCUMBENT_HOME
                              else None),
            "n_passes": n_passes,
            "vote_threshold": pk,
            "prob_threshold": pt,
            "verifier_config": dict(VF_CONFIG),
            "eval_path": eval_path,
            "detections": det,
            "_note": note,
        })
    analyses = [
        {
            "analysis_id": "55map-final-board-2026-08-27",
            "type": "leaderboard",
            "_note": ("THE FINAL 55-map board (PI-declared final; card "
                      "planning/55map-final-board-2026-08-27.md, signed): "
                      "23 cells, every run at carried and oracle points, "
                      "standardised reference, the GS tile-swap chain "
                      "verbatim (10k/seed 42, BH q=0.05, greedy cliques + "
                      "compact letter display). Gates: G3 exact 8-cell "
                      "board reproduction (f1, 28 p-values, tiers); "
                      "coincidence gates; per-cell 0.003 mechanism bound; "
                      "argmax oracles re-derived on the board's own "
                      "reference (11/13 confirmed the original points). "
                      "Includes cost and $/mound efficiency framing and "
                      "the IM as-shipped ruling."),
            "_prereg_rationale": ("Post-hoc E41-class synthesis; the "
                                  "paper's deployment board."),
            "conditions_compared": ["(all 23 board cells; see "
                                    "final_board_50m.json)"],
            "hypothesis_refs": ["H13", "H3"],
            "preregistered": "post-hoc",
            "deviations": [],
            "predicted_outcome": "(none — synthesis board)",
            "outcome": ("209/253 pairs significant, 9 tiers. B owns "
                        "T1-T2 (sole T1 B-N10-oracle 0.8558; T2 all "
                        "four other B cells). Best carried cell "
                        "B-N5-carried 0.8502. B-N3-carried (post-hoc) "
                        "0.8476 T3, indistinguishable from B-N5/N10 "
                        "carried — B saturates at N=3; A does not "
                        "(A-N3-carried sig below A-N5). Best incumbent "
                        "carried T03-k4 T5. A single pass of A (T6, "
                        "~$21) ties the HIGH incumbent carried (~$207). "
                        "Obs 438."),
            "paper_section": "Results",
            "output_path": "results/55map-final-board-2026-08-27/"
                           "final_board_50m.json",
            "working_notes_obs": [
                "Obs 438 — the final board and the emergent N=3 rung: "
                "B saturates at N=3 carried; the GS-determinable $65 "
                "bargain step"],
            "manually_verified_at": None,
        },
        {
            "analysis_id": "sensitivity-mde-2026-08-28",
            "type": "diagnostic",
            "_note": ("Instrument-sensitivity appendix (PI-commissioned "
                      "2026-08-28; scripts/sensitivity_mde.py): MDEs from "
                      "committed permutation nulls per instrument (GS "
                      "consensus boards sigma~0.023 -> MDE80 0.063-0.065; "
                      "GS verified-set instrument 2.6x finer at 0.0087 -> "
                      "0.024; 55-map final board 0.0046 -> 0.013), plus "
                      "normal-approximation TOST over the seven H8 "
                      "contrasts (smallest passing margin 0.07) and the "
                      "P6/IP5 cross-scale calibration specimens. No "
                      "permutations re-run. Recommended equivalence "
                      "margins: 0.07 (GS composition nulls), 0.015 "
                      "(deployment nulls)."),
            "_prereg_rationale": ("Post-hoc methodological appendix "
                                  "qualifying the study's negative "
                                  "claims; avoids the observed-power "
                                  "fallacy by construction."),
            "conditions_compared": ["(instrument-level; harvests "
                                    "committed pairwise records)"],
            "hypothesis_refs": ["H8", "H9", "H10", "H12"],
            "preregistered": "post-hoc",
            "deviations": [],
            "predicted_outcome": "(none — measurement of the instruments)",
            "outcome": ("Two-tier design made explicit: GS = screening "
                        "(excludes effects >~0.065 at 80% power), 55-map "
                        "= resolution (0.013). H8 equivalence at "
                        "Delta=0.07. Verification sharpens GS ~2.6x."),
            "paper_section": "Appendix",
            "output_path": "results/sensitivity-mde-2026-08-28/"
                           "sensitivity.json",
            "working_notes_obs": [],
            "manually_verified_at": None,
        },
    ]
    return additions, analyses


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    additions, analyses = build()
    rc = json.loads((REPO / "results/run-conditions.json").read_text())
    ra = json.loads((REPO / "results/run-analyses.json").read_text())
    missing = []
    n = 0
    for run, conds in additions.items():
        have = {c["label"] for c in rc["decomposition"][run]["conditions"]}
        for c in conds:
            n += 1
            if c["label"] in have:
                raise SystemExit(f"REFUSED: {run}::{c['label']} exists")
            for f in ("eval_path", "detections"):
                if not (REPO / c[f]).exists():
                    missing.append(c[f])
    have_a = {r["analysis_id"] for r in ra["analyses"]}
    for a in analyses:
        if a["analysis_id"] in have_a:
            raise SystemExit(f"REFUSED: {a['analysis_id']} exists")
    if missing:
        raise SystemExit("REFUSED — missing artefacts:\n  "
                         + "\n  ".join(missing))
    print(f"{n} conditions across {len(additions)} runs + "
          f"{len(analyses)} analyses; artefacts verified.")
    for run, conds in additions.items():
        print(f"  {run}: " + ", ".join(c["label"] for c in conds))
    if not args.write:
        print("dry run — re-run with --write")
        return 0
    for run, conds in additions.items():
        rc["decomposition"][run]["conditions"].extend(conds)
    ra["analyses"].extend(analyses)
    (REPO / "results/run-conditions.json").write_text(
        json.dumps(rc, indent=1) + "\n")
    (REPO / "results/run-analyses.json").write_text(
        json.dumps(ra, indent=1) + "\n")
    print("WRITTEN — regenerate manifests next")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
