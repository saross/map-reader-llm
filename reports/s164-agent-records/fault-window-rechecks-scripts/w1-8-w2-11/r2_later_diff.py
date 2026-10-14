#!/usr/bin/env python3
"""
Structured diff of the r2 board files: generating commit 7894b5b5a vs head.

Fault-window re-check (2026-10-14), row W2-11. 24 of the 55 files 7894b5b5a
wrote were changed later (2026-09-13 and 2026-09-20: the fourth cell's K = 5
rung, the tile-MCC re-sweeps, the MCC-oracle and carried-analogue cells). For
each, this reports what the later commits did to the 7894b5b5a content:
sweep CSVs — columns added, and whether every 7894b5b5a column keeps every
value on the same (prob_t, min_votes) row; JSON — leaves added, removed and
changed (first few changed shown).

Usage: python r2_later_diff.py REPO HEAD OUT_JSON

Author: Claude (Opus 5.5) for Shawn Ross; Licence: Apache 2.0
"""
from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from pathlib import Path

C = "7894b5b5a"
HOME = "results/55map-final-board-r2-2026-09-06"


def show(repo: str, rev: str, path: str) -> str:
    """Text of rev:path."""
    return subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                          capture_output=True, text=True, check=True).stdout


def leaves(o, p=""):
    """Flatten JSON to {path: leaf}."""
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(leaves(v, f"{p}.{k}" if p else k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(leaves(v, f"{p}[{i}]"))
    else:
        out[p] = o
    return out


def main() -> int:
    """Diff each later-changed file."""
    repo, head, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    files = subprocess.run(["git", "-C", repo, "show", "--name-only", "--format=", C, "--", HOME],
                           capture_output=True, text=True, check=True).stdout.split()
    rows = []
    for f in sorted(files):
        a, b = show(repo, C, f), show(repo, head, f)
        if a == b:
            continue
        if f.endswith(".csv"):
            ra = list(csv.DictReader(io.StringIO(a)))
            rb = list(csv.DictReader(io.StringIO(b)))
            key = lambda r: (r["prob_t"], r["min_votes"])  # noqa: E731
            ib = {key(r): r for r in rb}
            cols_a = list(ra[0].keys())
            changed = sum(1 for r in ra for c in cols_a
                          if key(r) not in ib or ib[key(r)].get(c) != r[c])
            rows.append({"file": f, "kind": "csv", "rows": [len(ra), len(rb)],
                         "columns_added": [c for c in rb[0] if c not in cols_a],
                         "columns_removed": [c for c in cols_a if c not in rb[0]],
                         "original_cells_changed": changed,
                         "original_content_preserved": changed == 0})
        else:
            la, lb = leaves(json.loads(a)), leaves(json.loads(b))
            chg = [k for k in la if k in lb and la[k] != lb[k]]
            rows.append({"file": f, "kind": "json", "leaves": [len(la), len(lb)],
                         "added": len(set(lb) - set(la)), "removed": len(set(la) - set(lb)),
                         "changed": len(chg),
                         "first_changed": [{"leaf": k, "7894b5b5a": la[k], "head": lb[k]}
                                           for k in chg[:8]]})
    out.write_text(json.dumps(rows, indent=1) + "\n")
    for r in rows:
        if r["kind"] == "csv":
            print(f"{r['file'].split('/')[-1]}: +cols {r['columns_added']}, original cells "
                  f"changed {r['original_cells_changed']}, rows {r['rows']}")
        else:
            print(f"{r['file'].split('/')[-1]}: leaves {r['leaves']}, added {r['added']}, "
                  f"removed {r['removed']}, changed {r['changed']}")
            for c in r["first_changed"][:4]:
                print("    ", c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
