#!/usr/bin/env python3
"""Cell-by-cell comparison of the Markdown tables two board documents share.

Usage: mdtables.py <a.md|commit:path> <b.md|commit:path> [--repo R]
                   [--ignore-col NAME ...]

Each pipe table is keyed by its header row. For every header present in both
documents, rows are compared cell by cell (columns named in --ignore-col are
skipped). Reports tables present on one side only, row-count mismatches and
every differing cell. Exit 0 when every shared table matches.
Author: Claude (Opus 5.5), Session 164 W2-2 re-check sub-agent, 2026-10-14.
"""
import argparse
import os
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("--repo", default=".")
ap.add_argument("--ignore-col", nargs="*", default=[])
args = ap.parse_args()


def load(spec):
    """Text from a file, or from commit:path via git show."""
    if os.path.exists(spec):
        return open(spec).read()
    c, p = spec.split(":", 1)
    return subprocess.run(["git", "-C", args.repo, "show", f"{c}:{p}"],
                          capture_output=True, text=True, check=True).stdout


def tables(text):
    """Map header line -> list of data rows (lists of cells)."""
    out, lines, i = {}, text.split("\n"), 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) \
                and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            head = lines[i]
            rows, j = [], i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            out[head] = rows
            i = j
        else:
            i += 1
    return out


ta, tb = tables(load(args.a)), tables(load(args.b))
bad = 0
for h in ta:
    if h not in tb:
        print(f"ONLY IN A: {h[:100]}")
        continue
    cols = [c.strip() for c in h.strip().strip("|").split("|")]
    keep = [k for k, c in enumerate(cols) if c not in args.ignore_col]
    ra, rb = ta[h], tb[h]
    nd = 0
    if len(ra) != len(rb):
        print(f"ROWS {len(ra)} vs {len(rb)}: {h[:100]}")
        nd += 1
    for r, (x, y) in enumerate(zip(ra, rb)):
        for k in keep:
            if (x[k] if k < len(x) else None) != (y[k] if k < len(y) else None):
                nd += 1
                print(f"  row {r} col {cols[k]!r}: {x[k] if k < len(x) else None!r}"
                      f" vs {y[k] if k < len(y) else None!r}")
    print(f"{'MATCH' if nd == 0 else 'DIFF '} {len(ra)} rows, ignoring "
          f"{[cols[k] for k in range(len(cols)) if k not in keep]}: {h[:90]}")
    bad += nd
for h in tb:
    if h not in ta:
        print(f"ONLY IN B: {h[:100]}")
sys.exit(0 if bad == 0 else 1)
