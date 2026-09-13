#!/usr/bin/env python3
"""
Resolve the board note's ``blocked_artefact`` claim, now that it is unblocked
============================================================================

Description:
    ``add_board_note.py`` inserted a ``cells_pending_rescore`` block into the
    Era-2 board's ``re_sign_pending``, and recorded inside it that the K = 3
    cell's own ``evaluation.json`` **could not be regenerated**: the tile-join
    invariant refused its per-tile table and, because the F1 bootstrap
    resamples tiles, the refusal aborted the whole evaluation. That claim was
    true on 2026-09-13 and is now false — the invariant withholds the per-tile
    statistics and lets the F1 arm through (checklist item 6a), the cell has
    been re-scored, and its ``conditions-manifest.json`` row reads 0.8860 / 495.

    A note that states a blockage which no longer exists is worse than no note,
    so this script replaces ``blocked_artefact`` with a ``resolved`` record. It
    changes nothing else, and in particular it does **not** touch
    ``proposed_outcome``, which still quotes the K = 3 cell's F1@20 as 0.8870:
    that text is signature-bearing and is the PI's to restate at the rebuild
    that picks these cells up. The discrepancy is named inside the resolved
    record instead of being quietly corrected.

    The block remains NOTE ONLY. No rebuild, no re-tiering, no signature field.
    Every one of the sixteen signature-bearing paths ``add_board_note.py``
    guards is asserted byte-equal before and after, and the file is rewritten
    with ``json.dumps(..., indent=1) + "\\n"`` — what
    ``build_gs_era2_board.finalise`` uses — so the diff is confined to the one
    key.

Usage::

    python resolve_board_note_block.py --provenance <path>
    python resolve_board_note_block.py --provenance <path> --check

Outputs:
    The provenance file, rewritten in place (or, with ``--check``, an exit
    status saying whether it already carries the resolved record).

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from add_board_note import SIGNATURE_PATHS, dig  # noqa: E402

#: What replaces the stale ``blocked_artefact`` string.
RESOLVED: dict[str, Any] = {
    "was": (
        "g37-text-k3-verified-opmax's own evaluation.json could NOT be "
        "regenerated: the tile-join invariant refused its per-tile table at "
        "HEAD and the F1 bootstrap resamples tiles, so the whole evaluation "
        "aborted. Its conditions-manifest.json row therefore read 0.8870 / "
        "494 and was stale by -0.0010 / -1 detection."
    ),
    "resolved_on": "2026-09-13",
    "resolved_by": (
        "planning/documentation-foundation-checklist-2026-09-13.md item 6a: "
        "the invariant now WITHHOLDS the per-tile table, tile confusion, "
        "tile-MCC and every bootstrap interval of a refused cell — with the "
        "reason, the shortfall counts and both tile vocabularies recorded in "
        "the artefact — and lets the buffer-matched F1, precision and recall "
        "point estimates proceed, per PI ruling 2026-09-13 (S153 ruling 6)."
    ),
    "artefact_state": (
        "The cell was re-scored on its recorded recipe (curator reference, "
        "era2_b_intersection_bounds, 14 buffers, 10,000 BCa draws, seed 42, "
        "--mcc) from a clean tree. Its evaluation.json, evaluation.csv and "
        "evaluation.md now read F1@20 0.8860, precision 0.8323, recall "
        "0.9471, 495 detections, with the tile block and every confidence "
        "interval marked WITHHELD "
        "(tile_join_detection_shortfall: 20 of 467 in-frame detections "
        "booked, shortfall 447). results/conditions-manifest.json's row "
        "matches, and is no longer stale."
    ),
    "still_pending_for_the_pi": (
        "re_sign_pending.proposed_outcome above quotes this cell's "
        "whole-frame F1 as 0.8870, which is the pre-fix figure. That text is "
        "signature-bearing and was deliberately NOT edited here; the PI "
        "restates it at the rebuild that picks these cells up. The current "
        "value is 0.8860. The bootstrap confidence interval this cell "
        "previously carried is withdrawn rather than superseded: it was "
        "resampled from a per-tile table the invariant refuses."
    ),
    "board_impact": (
        "None. This cell is one of tiering.withheld_cells — ranked and tested "
        "nowhere, its whole-frame F1 quoted as reference — so no rank, tier, "
        "pairwise test, BH family or MCB admissible set depends on it."
    ),
}


def main() -> None:
    """Replace ``blocked_artefact`` with ``resolved``, guarding signatures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report whether the resolved record is present; write nothing",
    )
    args = parser.parse_args()

    text = args.provenance.read_text(encoding="utf-8")
    before = json.loads(text)
    after = copy.deepcopy(before)

    block = after.get("re_sign_pending", {}).get("cells_pending_rescore")
    if block is None:
        raise SystemExit(
            "re_sign_pending.cells_pending_rescore is absent — run "
            "add_board_note.py first"
        )

    if args.check:
        has = "resolved" in block and "blocked_artefact" not in block
        print("RESOLVED" if has else "NOT RESOLVED")
        raise SystemExit(0 if has else 1)

    if "resolved" in block and "blocked_artefact" not in block:
        print("already resolved; nothing written")
        return

    block.pop("blocked_artefact", None)
    block["resolved"] = RESOLVED

    violations = [
        ".".join(path)
        for path in SIGNATURE_PATHS
        if json.dumps(dig(before, path), sort_keys=True)
        != json.dumps(dig(after, path), sort_keys=True)
    ]
    if violations:
        raise SystemExit(
            "refusing to write — signature-bearing path(s) changed: "
            + ", ".join(violations)
        )

    # ``indent=1`` and the default ``ensure_ascii=True`` are what
    # ``build_gs_era2_board.finalise`` and ``add_board_note.py`` both use, so
    # the diff stays confined to the one key rather than re-encoding every
    # em dash in the document.
    args.provenance.write_text(
        json.dumps(after, indent=1) + "\n", encoding="utf-8",
    )
    print(
        f"resolved; {len(SIGNATURE_PATHS)} signature-bearing path(s) asserted "
        "byte-equal"
    )


if __name__ == "__main__":
    main()
