#!/usr/bin/env python3
"""
Add a re-score note to the Era-2 board's pending re-signature block
===================================================================

Description:
    The PI ruled on 2026-09-13 that the recovery-fragment fix must NOT trigger a
    board rebuild or a re-tiering: the next rebuild — which also adds the
    tile-Matthews Correlation Coefficient (MCC) permutation family — picks the
    corrected cells up. What the board must carry in the meantime is a note
    naming the four affected cells with their before → after F1.

    The board's ``provenance.json`` already carries a ``re_sign_pending`` block
    and it is unresolved (``status`` begins ``PENDING``), so a second top-level
    key of that name is impossible. This script therefore nests a
    ``cells_pending_rescore`` array INSIDE the existing block, shaped like
    ``tiering.withheld_cells`` so it matches an established schema in the same
    file.

    Nothing else is touched. Every signature field is asserted byte-equal
    afterwards: ``signed_at``, ``signature_history``, ``gates.G1.pi_ruling``,
    ``_carried_forward``, and the block's own ``status``,
    ``signed_outcome`` and ``signed_n_conditions_compared``. The file is
    rewritten with ``json.dumps(..., indent=1) + "\\n"``, which is what
    ``build_gs_era2_board.finalise`` uses, so the diff is confined to the
    inserted key.

Usage::

    python add_board_note.py --provenance <path> [--check]

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

#: The four cells the rebuild touched, with F1@20 on the board frame measured
#: before and after. Source: results/k-ladder-2026-09-12/recovery-fix-2026-09-13/.
CELLS: list[dict[str, Any]] = [
    {
        "ref": "gemini37-screen-2026-08-28::g37-text-k1-verified-opmax",
        "label": "g37-text-k1-verified-opmax",
        "eval_f1_before": 0.8495,
        "eval_f1_after": 0.8495,
        "delta_f1": 0.0,
        "reason": (
            "consensus-n1 rebuilt with recovery fragments folded in; the union "
            "holds the same 640 candidates and this cell's 502 detections are "
            "unchanged, so F1@20 does not move (it moves only at 5 m, 0.4781 "
            "-> 0.4760, where one cluster centroid's 3.026 m shift crosses the "
            "match radius)."
        ),
    },
    {
        "ref": "gemini37-screen-2026-08-28::g37-text-k1-verified-carried-p0.10-k1",
        "label": "g37-text-k1-verified-carried-p0.10-k1",
        "eval_f1_before": 0.8338,
        "eval_f1_after": 0.8338,
        "delta_f1": 0.0,
        "reason": (
            "same rebuilt consensus-n1 union at the carried operating point; "
            "558 detections unchanged, F1@20 unchanged (5 m moves 0.4693 -> "
            "0.4673)."
        ),
    },
    {
        "ref": "gemini37-screen-2026-08-28::g37-text-k3-verified-opmax",
        "label": "g37-text-k3-verified-opmax",
        "eval_f1_before": 0.8870,
        "eval_f1_after": 0.8860,
        "delta_f1": -0.001,
        "reason": (
            "consensus-n3 rebuilt 757 -> 759 candidates; candidate_00049 is "
            "promoted 2 -> 3 votes by a recovery fragment and clears the rung's "
            "vote >= 3 gate at probability 1.0, adding one FALSE POSITIVE, so "
            "detections go 494 -> 495 and precision falls 0.8340 -> 0.8323 "
            "while recall holds at 0.9471. THE ONLY CELL IN THE REPOSITORY "
            "WHOSE F1 MOVES."
        ),
    },
    {
        "ref": "grid-2026-08-18::g384-ov192-k5-verified-opmax",
        "label": "g384-ov192-k5-verified-opmax",
        "eval_f1_before": 0.8905,
        "eval_f1_after": 0.8905,
        "delta_f1": 0.0,
        "reason": (
            "consensus-n5 T5 rebuilt 1,168 -> 1,169; the promoted candidate_01335 "
            "carries probability 0.10 against this rung's prob >= 0.15 gate so it "
            "does not enter, and the re-evaluation is dict-identical to the "
            "committed one on every arm including tile-MCC 0.8139 and the "
            "193/248/10/36 confusion. THE ONLY ONE OF THE FOUR THAT IS TIERED "
            "(rank 9, tier 2, MCB-admissible); the other three are already in "
            "tiering.withheld_cells."
        ),
    },
]

#: Keys that only the PI sets. Asserted byte-equal before and after.
SIGNATURE_PATHS: tuple[tuple[str, ...], ...] = (
    ("signed_at",),
    ("signature_history",),
    ("_carried_forward",),
    ("finalised_at_utc",),
    ("gates", "G1", "pi_ruling"),
    ("re_sign_pending", "status"),
    ("re_sign_pending", "reason"),
    ("re_sign_pending", "signed_outcome"),
    ("re_sign_pending", "proposed_outcome"),
    ("re_sign_pending", "signed_n_conditions_compared"),
    ("re_sign_pending", "proposed_n_conditions_compared"),
    ("re_sign_pending", "tiering_membership_source"),
    ("re_sign_pending", "untouched_fields"),
    ("re_sign_pending", "previous_resolved"),
    ("tiering",),
    ("membership",),
)


def dig(document: Any, path: tuple[str, ...]) -> Any:
    """Return the value at a dotted key path, or a sentinel if absent.

    Args:
        document: The loaded provenance document.
        path: Tuple of successive keys.

    Returns:
        The value found, or the string ``"<<ABSENT>>"``.
    """
    node = document
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return "<<ABSENT>>"
        node = node[key]
    return node


def main() -> int:
    """Insert the note, asserting every signature field is untouched."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report what would change and write nothing",
    )
    args = parser.parse_args()

    raw = args.provenance.read_text()
    before = json.loads(raw)
    after = copy.deepcopy(before)

    block = after.get("re_sign_pending")
    if not isinstance(block, dict):
        print("re_sign_pending is absent or not an object — refusing", file=sys.stderr)
        return 1
    if not str(block.get("status", "")).startswith("PENDING"):
        print(
            "re_sign_pending is not PENDING; a resolved block must not be "
            "extended by hand — refusing",
            file=sys.stderr,
        )
        return 1

    note = {
        "status": (
            "NOTE ONLY — no rebuild, no re-tiering, no signature change"
        ),
        "raised": "2026-09-13",
        "trigger": (
            "the recovery-fragment fix 75d7c8d4cd55b6ec8d2a40abff70a31f62b67725 "
            "rebuilt five committed merge_passes.py consensus unions that these "
            "four cells read; measured in "
            "results/k-ladder-2026-09-12/recovery-fix-2026-09-13/"
        ),
        "pi_ruling": (
            "PI ruling 2026-09-13: do NOT rebuild the board or re-tier for this. "
            "The next board rebuild, which also adds the tile-MCC permutation "
            "family, picks these cells up. This note records the pending "
            "numbers; no signature field is touched."
        ),
        "n_cells": len(CELLS),
        "n_cells_with_moved_f1": sum(1 for cell in CELLS if cell["delta_f1"]),
        "metric": "F1 at 20 m on the era2-b-487 board frame",
        "blocked_artefact": (
            "g37-text-k3-verified-opmax's own evaluation.json could NOT be "
            "regenerated: the tile-join invariant refuses its per-tile table at "
            "HEAD and the F1 bootstrap resamples tiles, so the whole evaluation "
            "aborts. Its conditions-manifest.json row therefore still reads "
            "0.8870 / 494 and is stale by -0.0010 / -1 detection until the "
            "tile-join question is ruled on "
            "(reports/tile-mcc-geometric-join-2026-09-12.md)."
        ),
        "cells": CELLS,
    }

    # Insert before ``previous_resolved`` so the resolved history stays last.
    rebuilt: dict[str, Any] = {}
    for key, value in block.items():
        if key == "previous_resolved":
            rebuilt["cells_pending_rescore"] = note
        rebuilt[key] = value
    if "cells_pending_rescore" not in rebuilt:
        rebuilt["cells_pending_rescore"] = note
    after["re_sign_pending"] = rebuilt

    # --- the guard: every signature field byte-equal -------------------
    violations = []
    for path in SIGNATURE_PATHS:
        if json.dumps(dig(before, path), sort_keys=True) != json.dumps(
            dig(after, path), sort_keys=True
        ):
            violations.append(".".join(path))
    if violations:
        print(f"REFUSING — these fields changed: {violations}", file=sys.stderr)
        return 1

    if list(before.keys()) != list(after.keys()):
        print("REFUSING — top-level key order or set changed", file=sys.stderr)
        return 1

    text = json.dumps(after, indent=1) + "\n"
    if args.check:
        print("would insert re_sign_pending.cells_pending_rescore")
        print(f"  cells: {[cell['label'] for cell in CELLS]}")
        print(f"  signature fields verified untouched: {len(SIGNATURE_PATHS)}")
        print(f"  bytes {len(raw)} -> {len(text)}")
        return 0

    args.provenance.write_text(text)
    print("inserted re_sign_pending.cells_pending_rescore")
    print(f"  signature fields verified untouched: {len(SIGNATURE_PATHS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
