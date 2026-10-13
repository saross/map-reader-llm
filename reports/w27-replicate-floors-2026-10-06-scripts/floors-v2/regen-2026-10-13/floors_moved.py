#!/usr/bin/env python3
"""
List the floors55_all.csv rows and § 6b cells that differ between two result trees.

Scratch tool for the 2026-10-13 W2.7 regeneration. Prints each moved floor row
(family, K, prob_t, k: floor before -> after, change) and the largest |change|
in the ``floor`` column, then summarises the moved § 6b cells by (family, K, k)
with the changes in detections, TP, FP, FN and the F1 range, and whether every
moved subset holds a given pass.

Usage::

    python floors_moved.py <new floors55_all.csv> <ref floors55_all.csv> \
        <new subset_cells_all.csv> <ref subset_cells_all.csv>

Author: Claude Code (Opus 5.5) for Shawn Ross | Created: 2026-10-13 | Apache 2.0
"""

from __future__ import annotations

import csv
import sys
from collections import Counter


def rows(path: str) -> list[dict]:
    """A CSV as a list of dicts."""
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    """Print the moved floors and cells."""
    fn, fr, cn, cr = sys.argv[1:5]
    key = ("family", "K", "prob_t", "k")
    a = {tuple(r[c] for c in key): r for r in rows(fn)}
    b = {tuple(r[c] for c in key): r for r in rows(fr)}
    assert set(a) == set(b)
    moved = [(k, float(b[k]["floor"]), float(a[k]["floor"])) for k in a if a[k] != b[k]]
    print(f"floors55_all.csv rows differing: {len(moved)}")
    for k, old, new in sorted(moved):
        print(f"  {k}: floor {old:.7f} -> {new:.7f} ({new - old:+.7f})")
    print(f"  max |d floor| {max((abs(n - o) for _, o, n in moved), default=0):.7f}")

    ck = ("family", "K", "subset", "prob_t", "k")
    a = {tuple(r[c] for c in ck): r for r in rows(cn)}
    b = {tuple(r[c] for c in ck): r for r in rows(cr)}
    assert set(a) == set(b)
    mc = [k for k in a if a[k] != b[k]]
    print(f"subset_cells_all.csv cells differing: {len(mc)} of {len(a)}")
    print("  by (family, K, k):", sorted(Counter((k[0], k[1], k[4]) for k in mc).items()))
    for col in ("n_det", "tp", "fp", "fn"):
        print(f"  d{col}:", sorted(Counter(int(a[k][col]) - int(b[k][col]) for k in mc).items()))
    d = [float(a[k]["f1"]) - float(b[k]["f1"]) for k in mc]
    if d:
        print(f"  dF1 range {min(d):+.6f} to {max(d):+.6f}")
    print("  prob_t values:", sorted(Counter(k[3] for k in mc).items()))
    print("  every moved subset holds pass 8:", all("8" in k[2].split("-") for k in mc))
    print("  subset sizes:", sorted(Counter(len(k[2].split("-")) for k in mc).items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
