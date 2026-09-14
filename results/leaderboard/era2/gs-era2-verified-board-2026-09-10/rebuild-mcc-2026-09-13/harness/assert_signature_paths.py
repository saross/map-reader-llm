#!/usr/bin/env python3
"""Assert that a board rebuild left every signature-bearing path byte-equal.

Why this exists
---------------
``scripts/build_gs_era2_board.py finalise`` rebuilds ``provenance.json`` from
the gate artefacts. Three fields have no gate artefact behind them and are the
PI's alone — ``signed_at``, ``signature_history`` and ``gates.G1.pi_ruling`` —
so ``finalise`` carries them forward instead. Carrying them forward is a claim,
and a claim about a signature has to be checked rather than trusted: the
2026-09-13 note-only amendment asserted sixteen paths byte-equal before and
after (``results/k-ladder-2026-09-12/recovery-fix-2026-09-13/harness/
resolve_board_note_block.py``), and this is the rebuild's equivalent.

What it checks, and what it deliberately does NOT
-------------------------------------------------
A REBUILD is expected to move ``tiering``, ``membership``, ``finalised_at_utc``
and the whole fresh ``re_sign_pending`` block — that is what a rebuild is for —
so those are not in the guard. What must not move is:

* ``provenance.json`` → ``signed_at``, ``signed_by``, ``signature_history``,
  ``gates.G1.pi_ruling``;
* ``provenance.json`` → ``re_sign_pending.previous_pending``, which must hold
  the PREVIOUS pending block verbatim (its own ``previous_resolved`` included),
  because a rebuild that lands on a pending block must nest the record rather
  than erase it;
* every field of the board's SIGNED analysis row in ``results/run-analyses.json``
  — ``manually_verified_at``, ``_signature_note``, ``conditions_compared``,
  ``outcome`` — which ``finalise --no-analysis-row`` must not write at all. The
  whole register file is compared byte for byte as well, since nothing in this
  job has any business touching it.

Usage::

    python3 assert_signature_paths.py --before <before.json> \\
        --after  <board>/provenance.json \\
        --register-before <before-run-analyses.json> \\
        --register-after results/run-analyses.json \\
        --out <job>/signature-paths.json

Exits non-zero, and names every offending path, if anything moved.

Author: Shawn Ross & Claude (Anthropic)
Created: 2026-09-13 (Session 154, checklist item 6)
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ABSENT = "<<ABSENT>>"

#: The board id whose analysis row carries the signature.
BOARD_ID = "gs-era2-verified-board-2026-09-10"

#: Paths in ``provenance.json`` a rebuild must leave byte-equal. Every one of
#: them is either the PI's signature, the PI's ruling, or the record of a
#: previous proposal; none is derivable from a gate artefact.
PROVENANCE_PATHS: tuple[tuple[str, ...], ...] = (
    ("signed_at",),
    ("signed_by",),
    ("signature_history",),
    ("gates", "G1", "pi_ruling"),
)

#: Fields of the SIGNED analysis row that ``--no-analysis-row`` must not write.
ROW_FIELDS: tuple[str, ...] = (
    "manually_verified_at",
    "_signature_note",
    "conditions_compared",
    "outcome",
)


def dig(document: Any, path: tuple[str, ...]) -> Any:
    """Return the value at a key path, or :data:`ABSENT` if it is not there.

    Args:
        document: The loaded document.
        path: Successive keys.

    Returns:
        The value found, or :data:`ABSENT`.
    """
    node = document
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return ABSENT
        node = node[key]
    return node


def canonical(value: Any) -> str:
    """A comparison form that is insensitive to key order but not to content."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def board_row(register: dict[str, Any] | list[Any]) -> dict[str, Any] | None:
    """The board's analysis row from a loaded register."""
    rows = register["analyses"] if isinstance(register, dict) else register
    for row in rows:
        if row.get("analysis_id") == BOARD_ID:
            return row
    return None


def main() -> int:
    """Compare before and after, report, and exit non-zero on any change."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--before", type=Path, required=True,
                    help="provenance.json as it stood before the rebuild.")
    ap.add_argument("--after", type=Path, required=True,
                    help="provenance.json as the rebuild left it.")
    ap.add_argument("--register-before", type=Path, required=True)
    ap.add_argument("--register-after", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None,
                    help="Write the verdict here as JSON.")
    args = ap.parse_args()

    before = json.loads(args.before.read_text(encoding="utf-8"))
    after = json.loads(args.after.read_text(encoding="utf-8"))
    reg_before_text = args.register_before.read_text(encoding="utf-8")
    reg_after_text = args.register_after.read_text(encoding="utf-8")

    checked: list[dict[str, Any]] = []
    violations: list[str] = []

    for path in PROVENANCE_PATHS:
        name = "provenance." + ".".join(path)
        lhs, rhs = canonical(dig(before, path)), canonical(dig(after, path))
        equal = lhs == rhs
        checked.append({"path": name, "byte_equal": equal,
                        "value": dig(after, path) if equal else None,
                        "before": None if equal else dig(before, path),
                        "after": None if equal else dig(after, path)})
        if not equal:
            violations.append(name)

    # The previous PENDING block must be nested verbatim, not summarised away.
    prior_pending = dig(before, ("re_sign_pending",))
    nested = dig(after, ("re_sign_pending", "previous_pending"))
    if prior_pending is not ABSENT and str(
            (prior_pending or {}).get("status", "")).startswith("PENDING"):
        equal = canonical(prior_pending) == canonical(nested)
        checked.append({"path": "provenance.re_sign_pending.previous_pending",
                        "byte_equal": equal,
                        "note": ("the previous PENDING block, nested verbatim "
                                 "rather than overwritten")})
        if not equal:
            violations.append("provenance.re_sign_pending.previous_pending")

    # The register: the whole file, and then each signed field by name, so a
    # failure says WHICH field moved rather than only that the file did.
    file_equal = reg_before_text == reg_after_text
    checked.append({"path": "results/run-analyses.json (whole file)",
                    "byte_equal": file_equal})
    if not file_equal:
        violations.append("results/run-analyses.json (whole file)")
    row_before = board_row(json.loads(reg_before_text)) or {}
    row_after = board_row(json.loads(reg_after_text)) or {}
    for field in ROW_FIELDS:
        name = f"run-analyses[{BOARD_ID}].{field}"
        equal = canonical(row_before.get(field, ABSENT)) == canonical(
            row_after.get(field, ABSENT))
        checked.append({"path": name, "byte_equal": equal})
        if not equal:
            violations.append(name)

    verdict = {
        "board_id": BOARD_ID,
        "n_paths_checked": len(checked),
        "n_violations": len(violations),
        "violations": violations,
        "passed": not violations,
        "paths": checked,
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(verdict, indent=1) + "\n",
                            encoding="utf-8")
    if violations:
        print(f"FAIL — {len(violations)} signature-bearing path(s) moved: "
              f"{violations}", file=sys.stderr)
        return 1
    print(f"PASS — {len(checked)} signature-bearing path(s) byte-equal before "
          f"and after the rebuild")
    return 0


if __name__ == "__main__":
    sys.exit(main())
