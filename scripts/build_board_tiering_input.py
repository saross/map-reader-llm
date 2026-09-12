#!/usr/bin/env python3
"""
Write a board-local copy of ``run-analyses.json`` carrying a board's full
membership, so the tiering instrument can be re-run without amending a SIGNED
analysis row.

Why this exists
---------------
``scripts/era1_leaderboard_tiering.py`` reads a board's membership from the named
analysis row's ``conditions_compared`` — the single source of truth, by design.
The GS Era-2 board's row is PI-SIGNED (``manually_verified_at``
2026-09-10T12:34:56Z, ``_signature_note`` recording the PI's approval), and
amending a signed row's membership, note or outcome is the PI's call, not an
agent's: the precedent is ``reports/r7-gaps-deltas-2026-09-11.md`` § 5.1, which
reported the figures for an amendment rather than making it.

So when PI ruling R3 (2026-09-12) enlarged the board from 79 cells to 103, the
membership had to reach the instrument some other way. This script writes
``<board>/tiering-input/run-analyses.json``: a byte-for-byte copy of the register
with **one** field changed — the named row's ``conditions_compared``, replaced by
the current membership of the two builders — plus a ``_tiering_input_note`` saying
what was substituted and why. The tiering is then run with
``--analyses <that file>``, and the register on disk is untouched.

The file is an INPUT, not a register: it is committed so the tiering is
reproducible, and it must never be copied back over ``results/run-analyses.json``.

Usage::

    python scripts/build_board_tiering_input.py \\
        --board results/leaderboard/era2/gs-era2-verified-board-2026-09-10 \\
        --analysis-id gs-era2-verified-board-2026-09-10

Then::

    python scripts/era1_leaderboard_tiering.py \\
        --analysis-id gs-era2-verified-board-2026-09-10 \\
        --analyses <board>/tiering-input/run-analyses.json \\
        --output-dir <board>

Zero API.

Created: 2026-09-12 (Session 154, K-ladder Phase 1 step 4)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_ANALYSES = PROJECT_ROOT / "results/run-analyses.json"

#: Condition-label suffix the main board builder mints for its members.
ERA2B_SUFFIX = "-era2b"


def membership_condition_ids(board: Path) -> tuple[list[str], dict[str, int]]:
    """The board's full membership as condition ids, from both builders.

    Args:
        board: The board directory.

    Returns:
        ``(ids, counts)`` — every member's condition id (the main builder's
        members as their ``-era2b`` rows, the opmax builder's as its own
        ``condition_id``), and a count per source.

    Raises:
        FileNotFoundError: If either membership file is missing; a partial
            membership would silently tier a smaller board.
    """
    main_path = board / "membership.json"
    opmax_path = board / "opmax" / "membership.json"
    for path in (main_path, opmax_path):
        if not path.is_file():
            raise FileNotFoundError(
                f"{path} is absent; derive both memberships before building the "
                "tiering input, or the board would be tiered short")
    main = json.loads(main_path.read_text(encoding="utf-8"))
    opmax = json.loads(opmax_path.read_text(encoding="utf-8"))
    era2b = [m["condition_id"] + ERA2B_SUFFIX for m in main["members"]]
    opmax_ids = [m["condition_id"] for m in opmax["members"] if m.get("on_board")]
    return era2b + opmax_ids, {"era2b": len(era2b), "opmax": len(opmax_ids)}


def build(board: Path, analysis_id: str) -> dict[str, Any]:
    """The register with one row's ``conditions_compared`` substituted."""
    doc = json.loads(RUN_ANALYSES.read_text(encoding="utf-8"))
    rows = doc["analyses"] if isinstance(doc, dict) else doc
    row = next((r for r in rows if r["analysis_id"] == analysis_id), None)
    if row is None:
        raise KeyError(f"no analysis row {analysis_id} in {RUN_ANALYSES}")
    ids, counts = membership_condition_ids(board)
    signed_n = len(row.get("conditions_compared") or [])
    row["conditions_compared"] = ids
    row["_tiering_input_note"] = (
        f"TIERING INPUT ONLY — NOT THE REGISTER. Built "
        f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} by "
        f"scripts/build_board_tiering_input.py. The register's own row holds "
        f"{signed_n} conditions_compared and is PI-SIGNED; this copy substitutes "
        f"the board's current membership ({len(ids)} cells: {counts['era2b']} "
        f"'-era2b' rows from membership.json and {counts['opmax']} '-opmax' rows "
        f"from opmax/membership.json) so scripts/era1_leaderboard_tiering.py can "
        f"tier the board PI ruling R3 enlarged, without amending a signed row. "
        f"Never copy this file over results/run-analyses.json.")
    return doc


def main(argv: list[str] | None = None) -> int:
    """Write ``<board>/tiering-input/run-analyses.json``."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--board", type=Path, required=True,
                        help="The board directory.")
    parser.add_argument("--analysis-id", required=True,
                        help="The analysis row whose membership is substituted.")
    args = parser.parse_args(argv)
    try:
        doc = build(args.board, args.analysis_id)
    except (FileNotFoundError, KeyError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2
    out_dir = args.board / "tiering-input"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "run-analyses.json"
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    rows = doc["analyses"] if isinstance(doc, dict) else doc
    row = next(r for r in rows if r["analysis_id"] == args.analysis_id)
    print(f"wrote {out} with {len(row['conditions_compared'])} conditions_compared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
