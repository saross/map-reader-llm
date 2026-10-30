#!/usr/bin/env python3
# ============================================================================
# compare_board_outputs.py
# ----------------------------------------------------------------------------
# Compare two output trees of scripts/regen_e43_board.py file by file, after
# normalising the three things that legitimately differ between runs of the
# same inputs: every JSON "timestamp" value, every JSON "git_commit" value, and
# the commit hash in summary.md's "from repository commit `...`" phrase.
# Everything else — every number, label, table row and sentence — must match
# byte for byte.
#
# Used for the reproduce gate of the E72 regeneration (record:
# reports/s166-agent-records/e72-group7.md § 2): the adapted script, run with
# --revision 2026-08-02 on the inputs at commit bc45133b4, against the outputs
# committed in 2f3ef020a.
#
# Usage:
#   python compare_board_outputs.py <expected-dir> <actual-dir>
# Exit status 0 when every file matches and neither tree has extra files.
# ============================================================================
"""Compare two E72 board output trees, ignoring timestamps and commit hashes."""

from __future__ import annotations

import re
import sys
from pathlib import Path

TIMESTAMP = re.compile(r'"timestamp": "[^"]*"')
GIT_COMMIT = re.compile(r'("git_commit": ")[^"]*(")')
PRODUCED_COMMIT = re.compile(r"from repository commit `[^`]*`")


def normalise(text: str) -> str:
    """Blank the run-specific fields of an output file.

    Args:
        text: The file's text.

    Returns:
        The text with timestamps and commit hashes replaced by placeholders.
    """
    text = TIMESTAMP.sub('"timestamp": "<TS>"', text)
    text = GIT_COMMIT.sub(r"\1<GC>\2", text)
    return PRODUCED_COMMIT.sub("from repository commit `<GC>`", text)


def main(expected: Path, actual: Path) -> int:
    """Report per-file agreement between two output trees.

    Args:
        expected: The committed outputs.
        actual: The outputs under test.

    Returns:
        0 if the trees agree after normalisation, else 1.
    """
    files_e = {p.relative_to(expected) for p in expected.rglob("*") if p.is_file()}
    files_a = {p.relative_to(actual) for p in actual.rglob("*") if p.is_file()}
    print("only in expected:", sorted(map(str, files_e - files_a)))
    print("only in actual:", sorted(map(str, files_a - files_e)))
    mismatched = 0
    for rel in sorted(files_e & files_a):
        same = normalise((expected / rel).read_text()) == normalise((actual / rel).read_text())
        mismatched += not same
        print("same" if same else "DIFF", rel)
    print(f"{len(files_e & files_a)} compared, {mismatched} mismatched")
    return 0 if not mismatched and files_e == files_a else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
