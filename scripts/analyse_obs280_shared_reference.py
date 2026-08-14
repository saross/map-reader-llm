#!/usr/bin/env python3
"""Re-measure the Obs 280/292 F1-vs-MCC divergence on the shared reference.

Queue item 4 of ``reports/verification/reference-standardisation-queue.md``
(ruling 20(a)): the original divergence finding — text wins F1, image wins
MCC (Obs 280, 2026-04-26; Obs 292, 2026-04-27; consolidated in
``results/55maps-mcc-v2-summary/report.md``) — was measured across metrics
that did NOT share a reference: corrected F1 against per-run extended
ground truth (GT), tile MCC against the student layer alone. An unknown
share of the divergence could therefore have been reference effect.
Queue items 2–3 put both metrics on the ruling-21 standardised reference
(``results/55maps-standardised-ref-2026-08-14/``); this script re-measures
the divergence there and decomposes the reference effect.

Reads committed artefacts only; NO recompute, NO API, US$0. All values
are lifted from:

- ``results/55maps-standardised-ref-2026-08-14/<cell>/evaluation.json``
  — the shared-reference board (F1 @ 50 m + buffer-invariant MCC, CIs);
- ``results/55maps-extended-gt-2026-06-07/<cell>/summary.json``
  — the legacy canonical-extended reference (F1 and MCC @ 50 m);
- ``results/55maps-standardised-ref-2026-08-14/legacy-baseline/<cell>/
  summary.json`` — legacy reference on the current engine (A1);
- the four student-only MCC anchors hardcoded below from
  ``results/55maps-mcc-v2-summary/report.md`` § 2 (post-recovery rows,
  same detection inputs as the board cells).

Outputs ``obs280-shared-reference.json`` beside the board artefacts and
prints the comparison tables.

Usage::

    python scripts/analyse_obs280_shared_reference.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from scipy.stats import spearmanr

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from score_55maps_standardised_reference import CELLS, REPO  # noqa: E402

STD_BASE = REPO / "results/55maps-standardised-ref-2026-08-14"
LEGACY_BASE = REPO / "results/55maps-extended-gt-2026-06-07"

# The four config cells Obs 292 / mcc-v2 compared (deployment operating
# points, one per configuration), in mcc-v2 § 2 row order.
CARRIED = ["T03-k4", "TH7-k4", "IM-k3", "TM-k4"]

# Student-only tile MCC, results/55maps-mcc-v2-summary/report.md § 2
# (post-recovery 2026-05-03 rows; detection inputs identical to the
# board cells: 4,350 / 4,164 / 4,680 / 3,865).
STUDENT_ONLY_MCC = {
    "T03-k4": 0.6538,
    "TH7-k4": 0.6476,
    "IM-k3": 0.6924,
    "TM-k4": 0.6260,
}


def std_cell(label: str) -> dict:
    """F1 @ 50 m + MCC (buffer-invariant) from the standardised board."""
    with open(STD_BASE / label / "evaluation.json", encoding="utf-8") as fh:
        ev = json.load(fh)["summary"]
    b50 = next(b for b in ev["buffers"] if b["buffer_metres"] == 50)
    tc = ev["tile_classification"]
    return {
        "f1": b50["f1"],
        "f1_ci": [b50["f1_ci_lower"], b50["f1_ci_upper"]],
        "mcc": tc["mcc"],
    }


def legacy_cell(label: str) -> dict:
    """F1 and MCC @ 50 m from the legacy canonical-extended reference."""
    with open(LEGACY_BASE / label / "summary.json", encoding="utf-8") as fh:
        s = json.load(fh)
    row = next(r for r in s["results"] if r["R_m"] == 50)
    return {
        "f1": row["F1"],
        "mcc": (row.get("tile_classification") or {}).get("mcc"),
    }


def a1_cell(label: str) -> float:
    """Legacy-reference F1 @ 50 m on the current engine (A1)."""
    path = STD_BASE / "legacy-baseline" / label / "summary.json"
    with open(path, encoding="utf-8") as fh:
        s = json.load(fh)
    return next(r for r in s["results"] if r["R_m"] == 50)["F1"]


def rank(values: dict[str, float]) -> list[str]:
    """Cell labels sorted best-first by value."""
    return sorted(values, key=lambda k: values[k], reverse=True)


def main() -> None:
    """Compute the re-measurement and write the JSON artefact."""
    std = {c["label"]: std_cell(c["label"]) for c in CELLS}
    legacy = {lb: legacy_cell(lb) for lb in CARRIED}
    a1 = {lb: a1_cell(lb) for lb in CARRIED}

    # --- The carried-cell (Obs 292) comparison on each reference -------
    f1_std = {lb: std[lb]["f1"] for lb in CARRIED}
    mcc_std = {lb: std[lb]["mcc"] for lb in CARRIED}
    f1_legacy = {lb: a1[lb] for lb in CARRIED}
    mcc_legacy_ext = {lb: legacy[lb]["mcc"] for lb in CARRIED}

    text_leader = rank(f1_std)[0]
    comparison = {
        "f1_rank_standardised": rank(f1_std),
        "mcc_rank_standardised": rank(mcc_std),
        "f1_rank_legacy_extended_a1": rank(f1_legacy),
        "mcc_rank_student_only": rank(STUDENT_ONLY_MCC),
        "mcc_rank_legacy_extended": rank(mcc_legacy_ext),
        "divergence_survives": (
            rank(f1_std)[0] != rank(mcc_std)[0]
        ),
        "f1_leader_standardised": text_leader,
        "mcc_leader_standardised": rank(mcc_std)[0],
    }

    # --- Gap decomposition: image's MCC lead over the F1 leader --------
    img = "IM-k3"
    mcc_gap = {
        "student_only_legacy": (
            STUDENT_ONLY_MCC[img] - STUDENT_ONLY_MCC[text_leader]
        ),
        "extended_legacy": (
            mcc_legacy_ext[img] - mcc_legacy_ext[text_leader]
        ),
        "standardised": mcc_std[img] - mcc_std[text_leader],
    }
    f1_gap = {
        "extended_legacy_a1": f1_legacy[text_leader] - f1_legacy[img],
        "standardised": f1_std[text_leader] - f1_std[img],
    }

    # --- Full-board rank correlation on the shared reference ------------
    all_cells = [c["label"] for c in CELLS]
    f1_all = [std[lb]["f1"] for lb in all_cells]
    mcc_all = [std[lb]["mcc"] for lb in all_cells]
    rho, p = spearmanr(f1_all, mcc_all)

    # --- Best-text-vs-image contrast (strongest form) -------------------
    best_text = rank({
        lb: std[lb]["f1"] for lb in all_cells if lb != img
    })[0]
    strongest = {
        "best_text_cell": best_text,
        "f1_deficit_image": std[img]["f1"] - std[best_text]["f1"],
        "mcc_lead_image": std[img]["mcc"] - std[best_text]["mcc"],
    }

    payload = {
        "generated_at_note": (
            "Deterministic lift from committed artefacts; regenerate by "
            "re-running scripts/analyse_obs280_shared_reference.py"
        ),
        "question": (
            "Does the Obs 280/292 F1-vs-MCC divergence survive when both "
            "metrics share the standardised reference (ruling 20a)?"
        ),
        "carried_cells": CARRIED,
        "standardised_values": {
            lb: {"f1_50m": std[lb]["f1"], "f1_ci": std[lb]["f1_ci"],
                 "mcc": std[lb]["mcc"]}
            for lb in all_cells
        },
        "student_only_mcc_legacy": STUDENT_ONLY_MCC,
        "extended_legacy_50m": {
            lb: legacy[lb] for lb in CARRIED
        },
        "legacy_a1_f1_50m": a1,
        "comparison": comparison,
        "mcc_gap_image_minus_f1_leader": mcc_gap,
        "f1_gap_f1_leader_minus_image": f1_gap,
        "full_board_spearman": {"rho": rho, "p": p, "n": len(all_cells)},
        "strongest_contrast": strongest,
    }
    out = STD_BASE / "obs280-shared-reference.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out.relative_to(REPO)}\n")

    print("Carried cells — F1@50 / MCC by reference:")
    print(f"{'cell':8s} {'F1 std':>8s} {'F1 A1':>8s} "
          f"{'MCC std':>8s} {'MCC ext-leg':>11s} {'MCC stud':>9s}")
    for lb in CARRIED:
        print(
            f"{lb:8s} {f1_std[lb]:8.4f} {f1_legacy[lb]:8.4f} "
            f"{mcc_std[lb]:8.4f} {mcc_legacy_ext[lb]:11.4f} "
            f"{STUDENT_ONLY_MCC[lb]:9.4f}"
        )
    print(f"\nF1 rank (standardised):  {comparison['f1_rank_standardised']}")
    print(f"MCC rank (standardised): {comparison['mcc_rank_standardised']}")
    print(f"MCC gap (image - {text_leader}): {mcc_gap}")
    print(f"F1 gap ({text_leader} - image): {f1_gap}")
    print(f"Full-board Spearman (8 cells): rho={rho:.3f} p={p:.3f}")
    print(f"Strongest contrast vs {best_text}: {strongest}")


if __name__ == "__main__":
    main()
