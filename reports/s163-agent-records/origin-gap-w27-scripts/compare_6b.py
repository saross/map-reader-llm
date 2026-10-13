#!/usr/bin/env python3
"""
Which § 6b cells (and simulated cells) the W2.7 origin fix moves.

D62 (1) workstream ``origin-gap-h13-copies`` (2026-10-13), step 3. Compares
a run's ``subset_cells_all.csv`` (and, if given, ``sim_cells.csv``) with PR
#38's, row by row on (family, K, subset, prob_t, k[, model, draw]), and
summarises the moved rows: count by family, K and k, the change in
detections, TP, FP, FN, and F1, and every moved row.

Usage::

    python compare_6b.py <new csv> <old csv> <json out>

Author: Claude Code (Opus 5.5) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

KEYS = ("family", "K", "subset", "prob_t", "k", "model", "draw")
VALS = ("n_det", "tp", "fp", "fn", "f1")


def rows(path: Path) -> dict[tuple, dict]:
    """Index a cells CSV by its key columns."""
    with open(path, newline="") as fh:
        out = {}
        for r in csv.DictReader(fh):
            out[tuple(r.get(k, "") for k in KEYS)] = r
        return out


def main() -> int:
    """Write the comparison and print its summary."""
    new, old, dest = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    a, b = rows(new), rows(old)
    assert set(a) == set(b), (len(set(a) - set(b)), len(set(b) - set(a)))
    moved = []
    for key, r in a.items():
        o = b[key]
        if any(r[v] != o[v] for v in VALS):
            moved.append({
                **dict(zip(KEYS, key)),
                **{f"d_{v}": (float(r[v]) - float(o[v])) for v in VALS},
                "f1_old": float(o["f1"]), "f1_new": float(r["f1"]),
            })
    by = Counter((m["family"], m["K"], m["k"], m["model"]) for m in moved)
    summary = {
        "rows": len(a), "moved": len(moved),
        "by_family_K_k_model": {"|".join(k): v for k, v in sorted(by.items())},
        "d_fp_values": sorted(Counter(m["d_fp"] for m in moved).items()),
        "d_tp_values": sorted(Counter(m["d_tp"] for m in moved).items()),
        "d_n_det_values": sorted(Counter(m["d_n_det"] for m in moved).items()),
        "d_f1_min": min((m["d_f1"] for m in moved), default=0.0),
        "d_f1_max": max((m["d_f1"] for m in moved), default=0.0),
        "rows_moved": moved,
    }
    dest.write_text(json.dumps(summary, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in summary.items() if k != "rows_moved"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
