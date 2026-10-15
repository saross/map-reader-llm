#!/usr/bin/env python3
"""Account for every file in w2-3b's scope list, from the comparison records.

Fault-window re-check W2-3, part B (sub-agent w2-3b), 2026-10-15.

Reads the scope list (``files.tsv``: path, last-changing commit, date, author)
and every ``cmp-*.json`` this sub-agent wrote, and assigns each scoped file one
verdict:

* VERIFIED: a comparison record covers it at its generating commit and its
  status is BYTE-IDENTICAL, BYTE-IDENTICAL-AFTER-SUBSTITUTION or
  EQUAL-AFTER-IGNORES;
* DIFFERS: a comparison record covers it and its status is anything else;
* CENSUS: a cell evaluation (``evaluation.{json,csv,md}``) the census replayed;
* NOT CHECKABLE: a real-time verifier output (``probabilities.json`` or
  ``run.meta.json``) with no raw responses kept;
* PROSE: a hand-written document that only quotes numbers;
* UNACCOUNTED: none of the above (the tally fails).

Usage: python tally_coverage.py --files-tsv F --cmp-dir D --out OUT.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

OK_STATUSES = {"BYTE-IDENTICAL", "BYTE-IDENTICAL-AFTER-SUBSTITUTION",
               "EQUAL-AFTER-IGNORES"}
PROSE = {"results/k-ladder-2026-09-12/tier-e/pre_launch_audit.md"}


def main() -> int:
    """Classify every scoped file and write the tally."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--files-tsv", type=Path, required=True)
    ap.add_argument("--cmp-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    covered: dict[tuple[str, str], tuple[str, str]] = {}
    for cmp_file in sorted(args.cmp_dir.glob("cmp-*.json")):
        report = json.loads(cmp_file.read_text())
        for rec in report["files"]:
            covered[(rec["path"], report["commit"])] = (rec["status"], cmp_file.name)

    rows = []
    for line in args.files_tsv.read_text().splitlines():
        path, commit = line.split("\t")[:2]
        hit = covered.get((path, commit))
        if hit is not None:
            verdict = "VERIFIED" if hit[0] in OK_STATUSES else "DIFFERS"
            how = f"{hit[0]} ({hit[1]})"
        elif path.rsplit("/", 1)[-1] in ("evaluation.json", "evaluation.csv",
                                          "evaluation.md"):
            verdict, how = "CENSUS", "cell evaluation replayed by the census"
        elif path.endswith(("probabilities.json", "run.meta.json")):
            verdict, how = "NOT CHECKABLE", "real-time verifier output, no raw responses"
        elif path in PROSE:
            verdict, how = "PROSE", "hand-written audit document"
        else:
            verdict, how = "UNACCOUNTED", ""
        rows.append({"path": path, "commit": commit, "verdict": verdict, "how": how})

    by_commit: dict[str, Counter] = {}
    for row in rows:
        by_commit.setdefault(row["commit"], Counter())[row["verdict"]] += 1
    tally = {"n_files": len(rows),
             "verdicts": dict(Counter(r["verdict"] for r in rows)),
             "by_commit": {c: dict(v) for c, v in sorted(by_commit.items())},
             "files": rows}
    args.out.write_text(json.dumps(tally, indent=2) + "\n")
    print(json.dumps({k: tally[k] for k in ("n_files", "verdicts", "by_commit")},
                     indent=2))
    return 0 if tally["verdicts"].get("UNACCOUNTED", 0) == 0 and \
        tally["verdicts"].get("DIFFERS", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
