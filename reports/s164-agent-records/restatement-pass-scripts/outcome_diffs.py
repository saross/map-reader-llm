#!/usr/bin/env python3
"""
Render drafted outcome texts and their word-level diffs for the record.

Part of the S164 restatement pass (``reports/s164-agent-records/
restatement-pass.md`` § 4). For each analysis in the drafted-outcomes file,
reads the register's current ``outcome`` (which the pass never changes) and
the drafted text, and writes a Markdown block: the drafted text in a fenced
block, then a word-level diff in ``[-old-]{+new+}`` form (the convention of
``git diff --word-diff=plain``), computed with ``difflib`` on whitespace
tokens. Wrapped at 72 columns inside the fences for reading.

Usage: python outcome_diffs.py <repo_root> <drafted.json> <out.md> [<heading_prefix>]

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import difflib
import json
import sys
import textwrap
from pathlib import Path

root, drafted_path, out_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
prefix = sys.argv[4] if len(sys.argv) > 4 else "4"
rows = {r["analysis_id"]: r for r in
        json.loads((root / "results/run-analyses.json").read_text())["analyses"]}
drafted = json.loads(drafted_path.read_text())


def word_diff(old: str, new: str) -> str:
    """``[-removed-]{+added+}`` over whitespace tokens."""
    a, b = old.split(), new.split()
    out: list[str] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "equal":
            out.extend(a[i1:i2])
            continue
        if i2 > i1:
            out.append("[-" + " ".join(a[i1:i2]) + "-]")
        if j2 > j1:
            out.append("{+" + " ".join(b[j1:j2]) + "+}")
    return " ".join(out)


def fence(text: str) -> list[str]:
    return ["```text", *textwrap.wrap(text, 72, break_on_hyphens=False), "```"]


lines: list[str] = []
for n, (aid, new) in enumerate(drafted.items(), start=1):
    old = rows[aid]["outcome"]
    lines += [f"### {prefix}.{n} `{aid}`", "",
              f"Signature: **{rows[aid]['signature']['status']}**. "
              "Drafted outcome, for the PI's approval (not applied):", "",
              *fence(new), "", "Word-level diff against the current outcome "
              "(`[-removed-]{+added+}`):", "", *fence(word_diff(old, new)), ""]
out_path.write_text("\n".join(lines))
print(f"wrote {len(drafted)} blocks to {out_path}")
