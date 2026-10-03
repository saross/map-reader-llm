#!/usr/bin/env python3
"""
Re-price a published 55-map final board's cost axis, without re-tiering it.

Why this script exists
----------------------
The board's tiers and its pairwise family are SIGNED: they were computed
over exactly the board's cells, and ``scripts/final_board_build.py`` is the
only thing that may write them (it re-runs 10,000 permutations per pair and
rewrites the whole document, banner and changelog included). The cost axis
is separate from the tiering: each cell's ``cost_usd`` and the "Cost
efficiency" section derive from the family costs alone. When the cost basis
changes (WP4b, PI ruling D19 amended 2026-10-04: every configuration priced
at one uniform tier from the register), this script refreshes exactly that:

* ``final_board_50m.json``: each tiered cell's ``cost_usd`` and
  ``cost_basis``, and a top-level ``cost_axis`` block. Tiers, groups,
  pairwise results and the addendum are not touched.
* ``final-board-50m.md``: the ranked table's cost column, the sentence
  saying what ``cost`` is, and the "Cost efficiency" section (heading to the
  next ``##``). The banner and the changelog are NOT touched: they are the
  human-written revision trail the document revision policy asks for.

A dry run (the default) prints every family's cost before and after and the
efficiency frontier's membership before and after, which is what the PI is
shown before a signed board's costs move (the signature policy: a re-pricing
is recorded as a dated signature note, never silently).

Usage::

    python scripts/final_board_cost_refresh.py                 # dry run, r2
    python scripts/final_board_cost_refresh.py --write

Zero API, seconds of compute.

Created: 2026-10-04 (WP4b of the cost accounting plan)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import scripts.final_board_build as fbb  # noqa: E402

#: The board's cost sentence before WP4b (two lines of its prose).
OLD_SENTENCE = ("cannot. `cost` is the run's audited all-in flex spend (full",
                "basis); a run's carried and oracle cells share it. See")

EFFICIENCY_HEADING = "## Cost efficiency: what a dollar buys"


def board_paths(reference: str) -> tuple[Path, Path]:
    """The board's JSON and markdown for a reference vintage (the builder's home)."""
    out = fbb.board_home(reference)
    return out / "final_board_50m.json", out / "final-board-50m.md"


def frontier_inputs(board: dict) -> tuple[list, dict, dict, list]:
    """``paper_rows``, ``by_label``, ``tier_of`` and the Tier-1 labels, from the board JSON."""
    by_label = {c["label"]: c for c in board["cells"]}
    tier_of = {lbl: i for i, tier in enumerate(board["tiers"], 1) for lbl in tier}
    paper_rows = [(n, c, o) for n, c, o in fbb.PAPER_ROWS
                  if (c is None or c in by_label) and (o is None or o in by_label)]
    return paper_rows, by_label, tier_of, board["tiers"][0]


def membership(rows: list[dict]) -> list[str]:
    """The frontier's run names, cheapest first."""
    return [r["name"] for r in rows if r["frontier"] is True]


def refresh_markdown(md: str, board: dict, eff_rows: list[dict]) -> str:
    """The document with its cost column, cost sentence and efficiency section re-priced.

    Raises:
        SystemExit: When a section the refresh must replace is not found
            exactly once, so a document of another shape is never half-edited.
    """
    lines = md.split("\n")
    # 1. The ranked table: "| rank | cell | basis | tier | group | cost | ...".
    labels = {c["label"] for c in board["cells"]}
    replaced = 0
    for i, line in enumerate(lines):
        cells = line.split(" | ")
        if line.startswith("| ") and len(cells) > 6 and cells[1] in labels \
                and cells[0][2:].isdigit():
            cells[5] = fbb.fmt_cost(fbb.cost_of(cells[1]), fbb.cost_completed(cells[1]))
            lines[i] = " | ".join(cells)
            replaced += 1
    if replaced != len(labels):
        raise SystemExit(f"cost column: {replaced} ranked rows found for {len(labels)} cells")
    # 2. The cost sentence (two lines, replaced by the builder's current text).
    text = "\n".join(lines)
    old = "\n".join(OLD_SENTENCE)
    new = "\n".join(fbb.COST_SENTENCE)
    if text.count(old) == 1:
        text = text.replace(old, new)
    elif text.count(new) != 1:
        raise SystemExit("the cost sentence was not found in either form")
    # 3. The efficiency section: its heading up to the next "## " heading.
    if text.count(EFFICIENCY_HEADING) != 1:
        raise SystemExit("the cost-efficiency section was not found exactly once")
    head, rest = text.split(EFFICIENCY_HEADING, 1)
    nxt = rest.find("\n## ")
    if nxt < 0:
        raise SystemExit("no section follows the cost-efficiency section")
    section = "\n".join(fbb.render_efficiency(eff_rows))
    return head + section + "\n" + rest[nxt:]


def main(argv: list[str] | None = None) -> int:
    """Report, and with ``--write`` apply, the board's re-priced cost axis."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    # r2 only: the r1 board is superseded and read-only by policy.
    parser.add_argument("--reference", default="r2", choices=("r2",))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    json_path, md_path = board_paths(args.reference)
    board = json.loads(json_path.read_text(encoding="utf-8"))
    paper_rows, by_label, tier_of, tier1 = frontier_inputs(board)

    old_cost = {c["label"]: c.get("cost_usd") for c in board["cells"]}
    before = fbb.efficiency_rows(paper_rows, by_label, tier_of, tier1,
                                 cost_fn=old_cost.get, completed_fn=lambda _: False)
    after = fbb.efficiency_rows(paper_rows, by_label, tier_of, tier1)

    print(f"{'family':12} {'before':>9} {'after':>9}  basis")
    seen = set()
    for c in board["cells"]:
        fam = fbb.family_of(c["label"])
        if fam in seen:
            continue
        seen.add(fam)
        prior = old_cost[c["label"]]
        cost = fbb.family_cost(fam)
        print(f"{fam:12} {('$%.2f' % prior) if prior is not None else '—':>9} "
              f"${cost.usd:8.2f}  {cost.basis}")
    print("\nfrontier before:", " -> ".join(membership(before)))
    print("frontier after: ", " -> ".join(membership(after)))

    md = refresh_markdown(md_path.read_text(encoding="utf-8"), board, after)
    if not args.write:
        print("\n(dry run: nothing written; --write applies it)")
        return 0
    for c in board["cells"]:
        c["cost_usd"] = fbb.cost_of(c["label"])
        c["cost_basis"] = fbb.family_cost(fbb.family_of(c["label"])).basis
    board["cost_axis"] = fbb.COST_AXIS
    json_path.write_text(json.dumps(board, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    print(f"\nwrote {json_path.relative_to(PROJECT_ROOT)} and {md_path.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
