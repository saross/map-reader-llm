#!/usr/bin/env python3
"""Show the census row behind every cell-evaluation file in w2-3b's scope.

Fault-window re-check W2-3, part B (sub-agent w2-3b), 2026-10-15. The scope's
cell evaluations (``evaluation.{json,csv,md}``) are not re-scored here: the
census (``~/scratch/d57-4-rescore-2026-10-09/census-old/out/census_cells.csv``)
replayed each cell's ``evaluation.json``. This prints, per CENSUS file in
``coverage-tally.json``, the census disposition and reproduction flags of the
sibling ``evaluation.json``, and fails if any has none.

Usage: python census_lookup.py --tally coverage-tally.json --census CSV
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path


def main() -> int:
    """Join the tally's CENSUS files to the census rows."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tally", type=Path, required=True)
    ap.add_argument("--census", type=Path, required=True)
    args = ap.parse_args()
    rows = {r["eval"]: r for r in csv.DictReader(args.census.open())}
    tally = json.loads(args.tally.read_text())
    seen: Counter = Counter()
    missing = []
    for rec in tally["files"]:
        if rec["verdict"] != "CENSUS":
            continue
        sibling = rec["path"].rsplit("/", 1)[0] + "/evaluation.json"
        row = rows.get(sibling)
        if row is None:
            missing.append(rec["path"])
            continue
        key = (row["disposition"], row["reproduces"], row["points_reproduce"],
               row["intervals_reproduce"], row["script_git_commit"])
        seen[key] += 1
    print(f"{sum(seen.values())} CENSUS files; their evaluation.json census rows:")
    for key, n in sorted(seen.items()):
        print(f"  {n:3d}  disposition={key[0]} reproduces={key[1]} points={key[2]} "
              f"intervals={key[3]} scorer_commit={key[4]}")
    if missing:
        print("NO CENSUS ROW:", missing)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
