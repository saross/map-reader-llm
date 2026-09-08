#!/usr/bin/env python3
"""Render the § R7.2 family-compressed final-board table from the r2 board JSON.

PI ruling 2026-09-08 (Session 151): the 35-cell r2 final board
(``results/55map-final-board-r2-2026-09-06/final_board_50m.json``) is reported
in ``docs/paper/results-draft.md`` § R7.2 as one row per run family showing
its best CARRIED cell and its best ORACLE cell at 50 m, with the full board
in supplement S2. This script derives that table from the board JSON so that
no figure in the paper table is transcribed by hand.

Families are the board's runs (its "Runs: as run versus theoretical maximum"
table), keyed by cell-label prefix. The image family follows the PI ruling of
2026-08-28: the "as shipped" cell is the k3 point (which coincides with the
standardised-reference argmax), and the E82 k4 comparability derivation is
noted, not tabled.

Usage
-----
    python scripts/render_r7_family_table.py            # Markdown table on stdout
    python scripts/render_r7_family_table.py --facts    # plus the derived facts used in prose
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
BOARD = REPO_ROOT / "results" / "55map-final-board-r2-2026-09-06" / "final_board_50m.json"

#: (display name, label prefix) in the order the table is rendered: the
#: Gemini 3 incumbents, the stride geometries, then the Gemini 3.7 campaign.
FAMILIES: tuple[tuple[str, str], ...] = (
    ("Gemini 3 text HIGH T0.7, K = 5 (the carry-forward)", "TH7-"),
    ("Gemini 3 text HIGH T0.3, K = 5", "T03-"),
    ("Gemini 3 text MIN, K = 5", "TM-"),
    ("Gemini 3 text MIN uplift, K = 10", "UPL-"),
    ("Gemini 3 image HIGH, K = 5", "IM-"),
    ("A: Gemini 3 text MIN, 384 px / 33 % overlap, K = 10", "A-"),
    ("B: Gemini 3 text MIN, 384 px / 50 % overlap, K = 10", "B-"),
    ("3.7 arm 1: 3.7 proposer + Gemini 3 verifier, K = 5", "ARM1-"),
    ("3.7 arm 2: all-3.7 stack, K = 5", "ARM2-"),
    ("fourth cell: B K = 10 union + 3.7 verifier", "FOURTH-"),
)


def load_board(path: Path = BOARD) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Return the board's cells and a label -> tier-number map."""
    board = json.loads(path.read_text(encoding="utf-8"))
    cells = board["cells"]
    tiers = board["tiers"]
    label_tier: dict[str, int] = {}
    if isinstance(tiers, dict):
        for tier_no, members in tiers.items():
            for label in members:
                label_tier[label] = int(tier_no)
    else:  # list of lists, or list of {tier, members}
        for idx, entry in enumerate(tiers, start=1):
            members = entry.get("members", entry.get("cells", [])) if isinstance(entry, dict) else entry
            tier_no = int(entry.get("tier", idx)) if isinstance(entry, dict) else idx
            for label in members:
                label_tier[label] = tier_no
    return cells, label_tier


def family_rows(cells: list[dict[str, Any]], label_tier: dict[str, int]) -> list[dict[str, Any]]:
    """Pick each family's best carried and best oracle cell by F1 at 50 m."""
    rows = []
    for name, prefix in FAMILIES:
        members = [c for c in cells if c["label"].startswith(prefix)]
        oracles = [c for c in members if c["basis"] == "oracle"]
        carried = [c for c in members if c["basis"].startswith("carried")]
        best_oracle = max(oracles, key=lambda c: c["f1_50"]) if oracles else None
        best_carried = max(carried, key=lambda c: c["f1_50"]) if carried else None
        note = ""
        if prefix == "IM-":  # PI ruling 2026-08-28: as shipped = k3 (= the argmax cell)
            best_carried = best_oracle
            note = "as shipped (k3); the E82 k4 comparability cell (0.7398, T12) is not tabled"
        elif best_carried is not None and best_carried["basis"] != "carried":
            note = best_carried["basis"]
        rows.append({"family": name, "carried": best_carried, "oracle": best_oracle,
                     "note": note, "tier": label_tier})
    return rows


def fmt_cell(cell: dict[str, Any] | None, label_tier: dict[str, int], with_point: bool) -> str:
    if cell is None:
        return "none"
    tier = label_tier.get(cell["label"], "?")
    out = f"{cell['f1_50']:.4f} (T{tier})"
    if with_point:
        out += f" at {cell['point']}"
    return out


def render(rows: list[dict[str, Any]], label_tier: dict[str, int]) -> str:
    lines = [
        "| run family | carried: F1@50 (tier) | tile-MCC | cost (flex, full) | oracle: F1@50 (tier) at (prob, k) | note |",
        "|---|---:|---:|---:|---|---|",
    ]
    for r in rows:
        c, o = r["carried"], r["oracle"]
        mcc = f"{c['mcc']:.3f}" if c else "none"
        cost = f"${c['cost_usd']:.0f}" if c and c.get("cost_usd") else "not supplied"
        lines.append(
            f"| {r['family']} | {fmt_cell(c, label_tier, False)} | {mcc} | {cost} | "
            f"{fmt_cell(o, label_tier, True)} | {r['note']} |")
    return "\n".join(lines)


def facts(cells: list[dict[str, Any]], label_tier: dict[str, int]) -> str:
    carried = [c for c in cells if c["basis"].startswith("carried")]
    top_mcc_carried = max(carried, key=lambda c: c["mcc"])
    top_mcc_all = max(cells, key=lambda c: c["mcc"])
    top_f1 = max(cells, key=lambda c: c["f1_50"])
    top_carried = max(carried, key=lambda c: c["f1_50"])
    g3 = [c for c in cells if not c["label"].startswith(("ARM", "FOURTH"))]
    top_g3 = max(g3, key=lambda c: c["f1_50"])
    top_g3_carried = max([c for c in g3 if c["basis"].startswith("carried")], key=lambda c: c["f1_50"])
    n_tiers = max(label_tier.values())
    return "\n".join([
        f"cells={len(cells)} tiers={n_tiers}",
        f"top F1: {top_f1['label']} {top_f1['f1_50']:.4f} (T{label_tier[top_f1['label']]})",
        f"top carried: {top_carried['label']} {top_carried['f1_50']:.4f} (T{label_tier[top_carried['label']]})",
        f"top Gemini-3 cell: {top_g3['label']} {top_g3['f1_50']:.4f} (T{label_tier[top_g3['label']]}); "
        f"top Gemini-3 carried: {top_g3_carried['label']} {top_g3_carried['f1_50']:.4f} (T{label_tier[top_g3_carried['label']]})",
        f"top MCC (all): {top_mcc_all['label']} {top_mcc_all['mcc']:.3f}; top MCC (carried): "
        f"{top_mcc_carried['label']} {top_mcc_carried['mcc']:.3f} (P {top_mcc_carried['precision_50']:.3f} / R {top_mcc_carried['recall_50']:.3f})",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--facts", action="store_true", help="Also print the derived facts used in the prose.")
    args = parser.parse_args(argv)
    cells, label_tier = load_board()
    rows = family_rows(cells, label_tier)
    print(render(rows, label_tier))
    if args.facts:
        print()
        print(facts(cells, label_tier))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
