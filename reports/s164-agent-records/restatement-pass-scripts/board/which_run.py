#!/usr/bin/env python3
"""Classify each modified worktree file by which board run it equals.

Usage: which_run.py <wt> <runA> <runB> <path-list-file>
Prints counts per class and up to 15 example paths per non-raw class.

Part of the S164 restatement pass (reports/s164-agent-records/
restatement-pass.md § 1.3, the Era-2 board lane).

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

WT, A, B = (Path(p) for p in sys.argv[1:4])
paths = Path(sys.argv[4]).read_text().split()
ROOTS = sorted({str(A), str(B), str(WT), "/home/shawn/Code/map-reader-llm"}, key=len, reverse=True)
TS = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(\+00:00|Z)?")


def norm(text: str) -> str:
    """Replace run roots and ISO timestamps."""
    for r in ROOTS:
        text = text.replace(r, "<ROOT>")
    return TS.sub("<TS>", text)


cls = defaultdict(list)
for p in paths:
    w = (WT / p).read_bytes()
    out = []
    for tag, base in (("A", A), ("B", B)):
        f = base / p
        if not f.exists():
            out.append(f"{tag}:missing")
            continue
        o = f.read_bytes()
        if o == w:
            out.append(f"{tag}:raw")
        else:
            try:
                eq = norm(o.decode()) == norm(w.decode())
            except UnicodeDecodeError:
                eq = False
            out.append(f"{tag}:{'norm' if eq else 'DIFF'}")
    cls[" ".join(out)].append(p)
for k, v in sorted(cls.items()):
    print(len(v), k)
    if "raw A:raw" not in k or "B:raw" not in k:
        for p in v[:15]:
            print("   ", p)
