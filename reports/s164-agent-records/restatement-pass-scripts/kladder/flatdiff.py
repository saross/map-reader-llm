#!/usr/bin/env python3
"""Flatten two JSON files and group their differing leaves.

Usage: flatdiff.py <a.json> <b.json> [--ignore KEY ...]
Prints the number of differing leaves, then groups keyed by the path with
list indices kept for the first two levels and the leaf name, with a count
and up to two examples (a value, b value) each.

Part of the S164 restatement pass (reports/s164-agent-records/
restatement-pass.md § 1.4, step 5).

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import json
import re
import sys
from collections import defaultdict


def flat(o, p=""):
    """Yield (path, leaf) pairs."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, f"{p}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from flat(v, f"{p}[{i}]")
    else:
        yield p, o


ign = set(sys.argv[sys.argv.index("--ignore") + 1:]) if "--ignore" in sys.argv else set()
a, b = (dict(flat(json.load(open(x)))) for x in sys.argv[1:3])
keys = [k for k in sorted(set(a) | set(b)) if a.get(k, "<absent>") != b.get(k, "<absent>")
        and not any(f"/{i}" in k for i in ign)]
print("differing leaves:", len(keys))
groups = defaultdict(list)
for k in keys:
    parts = re.split(r"(?=/)", k)
    head = "".join(parts[:2])
    leaf = re.sub(r"\[\d+\]", "[]", parts[-1])
    groups[(head, leaf)].append(k)
for (h, leaf), ks in sorted(groups.items()):
    ex = "; ".join(f"{a.get(k, '<absent>')} -> {b.get(k, '<absent>')}" for k in ks[:2])
    print(f"{len(ks):4d} {h} ...{leaf}: {ex}"[:260])
