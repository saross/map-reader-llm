#!/usr/bin/env python3
"""
Register the reference-revision-r2 analysis rows (r2 chain steps 6/7; PI-signed).

Every 55-map figure the paper cites was re-measured on reference r2
(``planning/reference-revision-2026-09-06.md``). The register records each
re-measurement as an analysis row in ``results/run-analyses.json`` whose
``conditions_compared`` are ``-r2-gt`` condition ids (7a), so the manifests
and the paper's citation sites resolve to files. This script authors those
rows -- one per re-measured analysis -- with the OUTCOME fields filled from
the committed artefacts, so the PI reviews facts rather than blanks, and
``manually_verified_at`` left ``None`` for the PI's signature.

Rows (analysis_id → output_path):

* ``55map-final-board-r2-2026-09-06`` → the 35-cell r2 final board
* ``55map-r2-leaderboard-50m`` / ``55map-r2-leaderboard-mcc-50m`` → the
  8-cell r2 leaderboard and MCC board
* ``obs280-shared-reference-r2`` → the divergence re-measured on r2
* ``tile-level-f1-r2`` → the eight 55-map cells' tile-level P/R/F1 on r2
* ``estimated-correction-r2`` → the estimated-correction column (step 6)
* ``student-baseline-r2`` → the corpus-level student baseline (step 9)
* ``sensitivity-mde-r2`` → the MDE appendix's r2 instrument row

Dry-run by default; ``--write`` persists idempotently (existing ids are
skipped), preserving the file's serialisation. The single manifest
regeneration (``generate_post_run_report.py --all --write``) follows.

Usage::

    python scripts/register_r2_analyses.py            # plan
    python scripts/register_r2_analyses.py --write

Created: 2026-09-07 (Session 149-c)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUN_ANALYSES = REPO / "results/run-analyses.json"
RUN_CONDITIONS = REPO / "results/run-conditions.json"
R2_BOARD = REPO / "results/55map-final-board-r2-2026-09-06"
R2_SCORING = "results/55maps-r2-ref-2026-09-06"
CARD = "planning/reference-revision-2026-09-06.md"

#: The GS-corpus cells the r1 tile-level-f1 analysis compared (unchanged on r2).
TILE_LEVEL_GS_CELLS = [
    "pv-diag-384::verified-adv-text-consensus-16of30",
    "pv-diag-384::verified-adv-image-baseline-pro-vf",
]


def r2_condition_ids(dec: dict) -> tuple[list[str], list[str]]:
    """(board-cell ids, scoring-home ids) of the -r2-gt rows."""
    board, scoring = [], []
    for run_id, run in dec.items():
        for c in run["conditions"]:
            if not c.get("label", "").endswith("-r2-gt"):
                continue
            cid = f"{run_id}::{c['label']}"
            if str(c.get("eval_path", "")).startswith(str(R2_BOARD.relative_to(REPO))):
                board.append(cid)
            elif str(c.get("eval_path", "")).startswith(R2_SCORING):
                scoring.append(cid)
    return sorted(board), sorted(scoring)


def board_facts() -> dict:
    b = json.loads((R2_BOARD / "final_board_50m.json").read_text())
    n_sig = sum(1 for p in b["pairwise"] if p["significant"])
    top = [(c["label"], c["f1_50"]) for c in b["cells"][:4]]
    return {"n_cells": len(b["cells"]), "n_pairs": len(b["pairwise"]), "n_sig": n_sig,
            "n_tiers": len(b["tiers"]), "top": top}


def leaderboard_facts(kind: str) -> dict:
    if kind == "f1":
        b = json.loads((REPO / "results/55map-leaderboard/55map_leaderboard_50m_r2.json").read_text())
        return {"n_sig": sum(1 for p in b["pairwise"] if p["significant"]), "n_pairs": len(b["pairwise"]),
                "n_tiers": len(b["tiers"]), "leader": b["cells"][0]["name"], "f1": b["cells"][0]["f1_50"]}
    b = json.loads((REPO / "results/metric-leaderboards/55map-mcc-tiering-r2.json").read_text())
    return {"n_sig": b["n_significant"], "n_pairs": b["n_pairs"], "n_tiers": len(b["tiers"]),
            "leader": b["cells"][0]["name"], "mcc": b["cells"][0]["mcc"]}


def build_rows(dec: dict) -> list[dict]:
    board_ids, scoring_ids = r2_condition_ids(dec)
    # The board's 35 cells: 28 authored board-home rows + the four carried
    # incumbents (k4 scoring rows) + the three coincident oracles, whose r2
    # argmax landed on a committed set and are registered by that set's row
    # (TH7-k3, IM-k3, TM-n10-k5) -- exactly as on r1.
    incumbents = [i for i in scoring_ids if i.endswith("verified-k4-r2-gt")]
    coincident = [i for i in scoring_ids if i.endswith(("text-high-generalisation::verified-k3-r2-gt",
                                                          "image-generalisation::verified-k3-r2-gt",
                                                          "verified-5of10-r2-gt"))]
    board_all = sorted(board_ids + incumbents + coincident)
    # The leaderboard's eight cells (NAMES): every scoring row except IM-k4.
    leaderboard = [i for i in scoring_ids if not i.endswith("image-generalisation::verified-k4-r2-gt")]
    assert len(board_all) == 35 and len(leaderboard) == 8, (len(board_all), len(leaderboard))
    fb = board_facts()
    lf = leaderboard_facts("f1")
    lm = leaderboard_facts("mcc")
    obs = json.loads((REPO / R2_SCORING / "obs280-shared-reference-r2.json").read_text())
    tlf = json.loads((REPO / "results/tile-level-f1-r2/tile_level_f1.json").read_text())
    est = json.loads((R2_BOARD / "estimated-correction.json").read_text())
    sb = json.loads((REPO / "results/student-baseline-2026-09-01/reestimate-r2.json").read_text())
    mde = json.loads((REPO / "results/sensitivity-mde-2026-08-28/sensitivity-r2.json").read_text())
    mde_r2 = next(r for r in mde["mde_table"] if "final board r2" in r["instrument"])
    common = {"preregistered": "post-hoc", "deviations": [], "manually_verified_at": None,
              "_prereg_rationale": ("Re-measurement of a registered analysis on reference r2 "
                                    f"({CARD}); the reference changed after the registered "
                                    "analyses ran — disclosed by erratum (step 8)."),
              "predicted_outcome": ("card § 4: r1 → r2 deltas inside the 0.005 band; the "
                                    "estimated column wider than the tiers")}
    top_txt = "; ".join(f"{lab} {f1:.4f}" for lab, f1 in fb["top"])
    return [
        {"analysis_id": "55map-final-board-r2-2026-09-06", "type": "leaderboard",
         "_note": (f"The final 55-map board on reference r2: {fb['n_cells']} cells (the 23 r1 cells "
                   "+ the 3.7 campaign's arm 1, arm 2 and fourth cell with their N=1/N=3 rungs, per the "
                   "membership ruling 2026-09-06), the GS tile-swap chain verbatim (10k / seed 42, BH "
                   "q=0.05, greedy cliques + compact letters). Gates: G3 exact r1 reproduction on r1; "
                   "coincidence 3/3 enforced; per-cell mechanism bound 0.003; all sweep gates pinned to r1."),
         "conditions_compared": board_all,
         "hypothesis_refs": ["H13", "H3"],
         "outcome": (f"{fb['n_sig']}/{fb['n_pairs']} pairs significant, {fb['n_tiers']} tiers. Top: "
                     f"{top_txt}. The 23 r1 cells keep their tier structure (each r1 tier maps to one "
                     "r2 tier); max |dF1@50| over them 0.0009."),
         "paper_section": "Results", "output_path": str((R2_BOARD / "final_board_50m.json").relative_to(REPO)),
         "working_notes_obs": [], **common},
        {"analysis_id": "55map-r2-leaderboard-50m", "type": "leaderboard",
         "_note": "The 8-cell 55-map leaderboard on reference r2 (build_55map_leaderboard.py --reference r2).",
         "conditions_compared": leaderboard, "hypothesis_refs": ["H13"],
         "outcome": (f"{lf['n_sig']}/{lf['n_pairs']} pairs significant, {lf['n_tiers']} tiers, identical tier "
                     f"structure to the r1 standardised board; leader {lf['leader']} {lf['f1']:.4f}."),
         "paper_section": "Results", "output_path": "results/55map-leaderboard/55map_leaderboard_50m_r2.json",
         "working_notes_obs": [], **common},
        {"analysis_id": "55map-r2-leaderboard-mcc-50m", "type": "leaderboard",
         "_note": "The 8-cell 55-map tile-MCC board on reference r2 (mcc_tiering_55map.py --reference r2).",
         "conditions_compared": leaderboard, "hypothesis_refs": ["H13"],
         "outcome": (f"{lm['n_sig']}/{lm['n_pairs']} pairs significant, {lm['n_tiers']} tiers; leader "
                     f"{lm['leader']} MCC {lm['mcc']:.4f}."),
         "paper_section": "Results", "output_path": "results/metric-leaderboards/55map-mcc-tiering-r2.json",
         "working_notes_obs": [], **common},
        {"analysis_id": "obs280-shared-reference-r2", "type": "comparison",
         "_note": "The Obs 280/292 F1-vs-MCC divergence re-measured on reference r2 (analyse_obs280_shared_reference.py --reference r2).",
         "conditions_compared": leaderboard, "hypothesis_refs": ["H13"],
         "outcome": (f"F1 rank {obs['comparison']['f1_rank_standardised']}; MCC rank "
                     f"{obs['comparison']['mcc_rank_standardised']}; the divergence holds on r2."),
         "paper_section": "Results", "output_path": f"{R2_SCORING}/obs280-shared-reference-r2.json",
         "working_notes_obs": [], **common},
        {"analysis_id": "tile-level-f1-r2", "type": "comparison",
         "_note": "Tile-level P/R/F1 beside MCC for the eight 55-map cells on reference r2 (derive_tile_level_f1.py --reference r2); GS cells unchanged.",
         "conditions_compared": TILE_LEVEL_GS_CELLS + leaderboard, "hypothesis_refs": ["H13"],
         "outcome": (f"MCC reproduction gate {tlf['validation_gate']['n_passed']}/"
                     f"{tlf['validation_gate']['n_cells']}."),
         "paper_section": "Appendix", "output_path": "results/tile-level-f1-r2/tile_level_f1.json",
         "working_notes_obs": [], **common},
        {"analysis_id": "estimated-correction-r2", "type": "diagnostic",
         "_note": ("The estimated-correction column (card § 2): the reference error the audits did not see, "
                   "propagated by Monte Carlo through the r2 board; beside the point estimate, never a re-tiering."),
         "conditions_compared": board_all, "hypothesis_refs": ["H13"],
         "outcome": (f"Expected terms M {est['expected_terms_point']['M_unseen_missed']:.1f}, E_err "
                     f"{est['expected_terms_point']['E_err']:.1f}, E_om {est['expected_terms_point']['E_om']:.1f}; "
                     "F1-hat sits 0.0005–0.0007 below the r2 point with ±0.005 intervals."),
         "paper_section": "Results", "output_path": str((R2_BOARD / "estimated-correction.json").relative_to(REPO)),
         "working_notes_obs": [], **common},
        {"analysis_id": "student-baseline-r2", "type": "diagnostic",
         "_note": "The student (novice) baseline re-estimated at 55-map corpus level on r2 (card § 2b).",
         "conditions_compared": ["(corpus-level; the reference layers and the audit rates, not a condition)"],
         "hypothesis_refs": ["H13"],
         "outcome": (f"P {sb['rows'][0]['precision']['mean']:.3f} / R {sb['rows'][0]['recall']['mean']:.3f} / "
                     f"F1 {sb['rows'][0]['f1']['mean']:.3f} (without extrapolated terms R "
                     f"{sb['rows'][1]['recall']['mean']:.3f} / F1 {sb['rows'][1]['f1']['mean']:.3f}); "
                     "GS-4 direct 1.000 / 0.947 / 0.973."),
         "paper_section": "Discussion", "output_path": "results/student-baseline-2026-09-01/reestimate-r2.json",
         "working_notes_obs": [], **common},
        {"analysis_id": "sensitivity-mde-r2", "type": "diagnostic",
         "_note": "The MDE appendix with the r2 final board's tile-swap instrument added (sensitivity_mde.py --reference r2).",
         "conditions_compared": ["(instrument-level; harvests the r2 board's committed pairwise records)"],
         "hypothesis_refs": ["H8", "H9", "H10", "H12"],
         "outcome": (f"55-map r2 board null SD {mde_r2['null_sd_median']:.4f} over {mde_r2['n_comparisons']} pairs; "
                     f"MDE80 {mde_r2['mde_80pc_power']:.3f} — resolution unchanged by r2."),
         "paper_section": "Appendix", "output_path": "results/sensitivity-mde-2026-08-28/sensitivity-r2.json",
         "working_notes_obs": [], **common},
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    dec = json.loads(RUN_CONDITIONS.read_text())["decomposition"]
    doc = json.loads(RUN_ANALYSES.read_text())
    existing = {a["analysis_id"] for a in doc["analyses"]}
    rows = build_rows(dec)
    for r in rows:
        status = "present" if r["analysis_id"] in existing else "add"
        print(f"  {status:8s} {r['analysis_id']:36s} {len(r['conditions_compared']):3d} conditions -> {r['output_path']}")
        print(f"           outcome: {r['outcome'][:150]}")
    to_add = [r for r in rows if r["analysis_id"] not in existing]
    if not args.write:
        print(f"{len(to_add)} row(s) to add — dry run; pass --write to persist")
        return 0
    doc["analyses"].extend(to_add)
    raw = RUN_ANALYSES.read_text()
    trailing = "\n" if raw.endswith("\n") else ""
    RUN_ANALYSES.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + trailing)
    print(f"wrote {len(to_add)} row(s) -> {RUN_ANALYSES.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
