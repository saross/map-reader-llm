#!/usr/bin/env python3
"""
Author the GS Era-2 board's K-ladder membership file (PI ruling 2026-09-13).

Why this exists
---------------
The K-ladder review's Phase 2 and tier E work registered fifty verified
conditions that were scored, from the start, ON the Era-2 board frame
(``inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson``,
``test_set_id`` ``era2-b-487``). ``scripts/build_gs_era2_board.py`` refused all
fifty on two rules that are correct for the rows they were written for — a
committed evaluation on a frame other than the Era-2 or grid-common frame, and
the presence of a ``scope_override`` — but that here refuse the cohort for being
already on the board's own frame. The close-out report set the choice out as
three routes (``reports/k-ladder-closeout-deltas-2026-09-12.md`` § 8); the PI
ruled route (a) on 2026-09-13: a third membership source the main builder defers
to by condition id, BEFORE those two rules, exactly as it already defers to
``opmax/membership.json`` through ``opmax_owned()``.

This script writes that file. It is a derivation, not a transcription: the
cohort is read out of ``results/run-conditions.json`` by rule — a verified
condition whose committed ``eval_path`` lies under the K-ladder results
directory and whose ``scope_override.test_set_id`` is the board frame id — and
every member's committed evaluation is opened and checked to name the board
frame before it is written. A row that fails either check is refused with its
reason rather than admitted on trust.

Usage::

    python scripts/author_k_ladder_board_membership.py [--write]

Without ``--write`` it prints what it would write and changes nothing. Zero API.

Created: 2026-09-13 (K-ladder admission job)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_CONDITIONS = PROJECT_ROOT / "results/run-conditions.json"
BOARD_DIR = PROJECT_ROOT / "results/leaderboard/era2/gs-era2-verified-board-2026-09-10"
OUT = BOARD_DIR / "k-ladder/membership.json"

#: The K-ladder results tree. A condition whose committed evaluation lives here
#: was scored by the K-ladder campaign, which scored on the board frame.
K_LADDER_RESULTS = "results/k-ladder-2026-09-12/"
#: The board frame's test-set id and file name — both are checked.
FRAME_ID = "era2-b-487"
FRAME_BASENAME = "era2_b_intersection_bounds.geojson"
#: The controlling documents. Recorded in the file so a reader never has to ask
#: on whose authority fifty cells joined a signed board.
CARD = "planning/k-ladder-review-2026-09-11.md"
CLOSEOUT = "reports/k-ladder-closeout-deltas-2026-09-12.md"
RULING = ("PI ruling 2026-09-13 (morning), item 1: route (a) of "
          f"{CLOSEOUT} § 8 — a k-ladder/membership.json the main builder "
          "defers to by condition id before its frame and scope rules, so "
          "these cells join with their board-frame evaluations as-is.")

#: Which K-ladder cohort a run belongs to, for the per-member reason line.
COHORT = {
    "grid-2026-08-18": ("tier E", "the verified B-geometry K ladder tier E "
                        "bought (findings.md § 8.4)"),
    "pv-diag-384": ("Phase 2", "one of the fourteen Gemini 3 PV ladders "
                    "Phase 2 bought (findings.md § 7)"),
    "gemini37-screen-2026-08-28": ("Phase 2", "a Gemini 3.7 gold-standard "
                                   "text rung of Phase 2 (findings.md § 7.3 "
                                   "— tile-MCC withheld under the tile-join "
                                   "invariant)"),
}


def cohort_of(run_id: str) -> tuple[str, str]:
    """The cohort name and its one-line description for a run id."""
    return COHORT.get(run_id, ("K-ladder", "a registered K-ladder rung"))


def derive(dec: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """The cohort, by rule, with every candidate's frame claim verified.

    Args:
        dec: The register's ``decomposition`` mapping (run id -> run entry).

    Returns:
        ``(members, refused)``. A member carries its condition id, run id,
        label, the evaluation that admits it and a one-line reason; a refusal
        carries the condition id and why the rule did not admit it.
    """
    members: list[dict[str, Any]] = []
    refused: list[dict[str, Any]] = []
    for run_id, entry in sorted(dec.items()):
        for cond in entry.get("conditions", []):
            eval_path = cond.get("eval_path") or ""
            if not eval_path.startswith(K_LADDER_RESULTS):
                continue
            cid = f"{run_id}::{cond['label']}"
            if cond.get("aggregation") != "verified":
                refused.append({"condition_id": cid,
                                "reason": f"aggregation {cond.get('aggregation')!r}, "
                                          "not 'verified'"})
                continue
            scope = (cond.get("scope_override") or {}).get("test_set_id")
            if scope != FRAME_ID:
                refused.append({"condition_id": cid,
                                "reason": f"scope_override test_set_id {scope!r} "
                                          f"is not the board frame {FRAME_ID!r}"})
                continue
            doc_path = PROJECT_ROOT / eval_path
            if not doc_path.is_file():
                refused.append({"condition_id": cid,
                                "reason": "committed evaluation is missing on disk"})
                continue
            cli = (json.loads(doc_path.read_text(encoding="utf-8"))
                   .get("_metadata", {}).get("cli_args") or {})
            bounds = os.path.basename(cli.get("bounds") or "")
            if bounds != FRAME_BASENAME:
                refused.append({"condition_id": cid,
                                "reason": f"committed evaluation names {bounds!r}, "
                                          "not the board frame"})
                continue
            cohort, description = cohort_of(run_id)
            members.append({
                "condition_id": cid,
                "run_id": run_id,
                "label": cond["label"],
                "cohort": cohort,
                "eval_path": eval_path,
                "reason": (f"{cohort}: {description}; its committed evaluation is "
                           f"already on the board frame ({FRAME_ID}) with the "
                           "board's own recipe, so it joins as-is and is not "
                           "re-scored"),
            })
    members.sort(key=lambda m: m["condition_id"])
    return members, refused


def build() -> dict[str, Any]:
    """The membership document, ready to write."""
    dec = json.loads(RUN_CONDITIONS.read_text(encoding="utf-8"))["decomposition"]
    members, refused = derive(dec)
    from collections import Counter
    counts = Counter(m["cohort"] for m in members)
    return {
        "board_id": BOARD_DIR.name,
        "frame_id": FRAME_ID,
        "provenance": {
            "card": CARD,
            "closeout_report": CLOSEOUT,
            "ruling": RULING,
            "derivation": ("scripts/author_k_ladder_board_membership.py: every "
                           "verified registered condition whose committed "
                           f"eval_path is under {K_LADDER_RESULTS} and whose "
                           f"scope_override names {FRAME_ID}, with the "
                           "evaluation opened and its bounds checked"),
            "authored_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "n_members": len(members),
        "n_by_cohort": dict(sorted(counts.items())),
        "members": members,
        "refused": refused,
    }


def main(argv: list[str] | None = None) -> int:
    """Write (or preview) the K-ladder membership file."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--write", action="store_true",
                        help="Persist the file; without it, preview only.")
    args = parser.parse_args(argv)
    doc = build()
    print(f"{doc['n_members']} members {doc['n_by_cohort']}; "
          f"{len(doc['refused'])} refused")
    for m in doc["members"]:
        print(f"  {m['condition_id']:70s} {m['cohort']}")
    for r in doc["refused"]:
        print(f"  REFUSED {r['condition_id']}: {r['reason']}", file=sys.stderr)
    if not doc["members"]:
        print("REFUSED: no member derived; the register does not hold the "
              "cohort this file is for", file=sys.stderr)
        return 2
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        print(f"wrote {OUT.relative_to(PROJECT_ROOT)}")
    else:
        print("(preview only; pass --write to persist)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
