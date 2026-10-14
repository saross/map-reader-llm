#!/usr/bin/env python3
"""compare.py -- W2-13 fault-window re-check comparator (Session 164, 2026-10-14).

Compares a regenerated file with a committed one: first byte for byte (sha256),
then, if they differ, structurally -- JSON as a recursive leaf diff, CSV as a
cell diff, other text as a line diff -- ignoring ONLY the keys named with
--ignore-key (JSON key names, at any depth) or lines matching --ignore-line
(regex, text files).  Prints a one-line verdict and up to --max differences.

Usage:
    compare.py REGEN COMMITTED [--ignore-key K ...] [--ignore-line RE ...]
               [--max N] [--json-out PATH]
Exit status: 0 byte-identical or equal after ignores, 1 differs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path


def sha(path: Path) -> str:
    """Return the file's sha256 hex digest."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def leaf_diff(a, b, path: str, ignore: set[str], out: list) -> None:
    """Recursively record leaf differences between two parsed JSON values."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k in ignore:
                continue
            if k not in a or k not in b:
                out.append((f"{path}/{k}", a.get(k, "<absent>"), b.get(k, "<absent>")))
            else:
                leaf_diff(a[k], b[k], f"{path}/{k}", ignore, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((f"{path}#len", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            leaf_diff(x, y, f"{path}[{i}]", ignore, out)
    elif type(a) is not type(b) or a != b:
        out.append((path, a, b))


def main() -> int:
    """Compare and report."""
    ap = argparse.ArgumentParser()
    ap.add_argument("regen", type=Path)
    ap.add_argument("committed", type=Path)
    ap.add_argument("--ignore-key", action="append", default=[])
    ap.add_argument("--ignore-line", action="append", default=[])
    ap.add_argument("--max", type=int, default=20)
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()
    ra, rb = args.regen.read_bytes(), args.committed.read_bytes()
    result: dict = {
        "regen": str(args.regen),
        "committed": str(args.committed),
        "sha256_regen": sha(args.regen),
        "sha256_committed": sha(args.committed),
    }
    diffs: list = []
    if ra == rb:
        result["verdict"] = "BYTE-IDENTICAL"
    else:
        suffix = args.committed.suffix.lower()
        if suffix in (".json", ".geojson"):
            leaf_diff(json.loads(ra), json.loads(rb), "", set(args.ignore_key), diffs)
            mode = "json-leaf"
        elif suffix == ".csv":
            rows_a = list(csv.reader(io.StringIO(ra.decode())))
            rows_b = list(csv.reader(io.StringIO(rb.decode())))
            if len(rows_a) != len(rows_b):
                diffs.append(("#rows", len(rows_a), len(rows_b)))
            for i, (x, y) in enumerate(zip(rows_a, rows_b)):
                for j in range(max(len(x), len(y))):
                    u = x[j] if j < len(x) else "<absent>"
                    v = y[j] if j < len(y) else "<absent>"
                    if u != v:
                        diffs.append((f"r{i}c{j}", u, v))
            mode = "csv-cell"
        else:
            pats = [re.compile(p) for p in args.ignore_line]

            def keep(line: str) -> bool:
                return not any(p.search(line) for p in pats)

            lines_a = [(i, s) for i, s in enumerate(ra.decode(errors="replace").splitlines(), 1)
                       if keep(s)]
            lines_b = [(i, s) for i, s in enumerate(rb.decode(errors="replace").splitlines(), 1)
                       if keep(s)]
            if len(lines_a) != len(lines_b):
                diffs.append(("#lines", len(lines_a), len(lines_b)))
            for (i, x), (j, y) in zip(lines_a, lines_b):
                if x != y:
                    diffs.append((f"L{i}/L{j}", x, y))
            mode = "text-line"
        result["mode"] = mode
        result["ignored_keys"] = args.ignore_key
        result["ignored_line_patterns"] = args.ignore_line
        result["verdict"] = "EQUAL-AFTER-IGNORES" if not diffs else "DIFFERS"
    result["n_diffs"] = len(diffs)
    result["first_diffs"] = [[p, repr(x)[:300], repr(y)[:300]] for p, x, y in diffs[: args.max]]
    print(f"{result['verdict']:<20} n_diffs={result['n_diffs']:<6} {args.committed}")
    for p, x, y in result["first_diffs"]:
        print(f"    {p}: regen={x} committed={y}")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=1) + "\n")
    return 0 if result["verdict"] != "DIFFERS" else 1


if __name__ == "__main__":
    sys.exit(main())
