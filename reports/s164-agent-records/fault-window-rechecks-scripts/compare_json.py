#!/usr/bin/env python3
"""Compare a regenerated file with a git blob: bytes first, then leaves.

Written for the 2026-10-15 fault-window re-checks (rows W2-3, W2-4, W2-7,
W2-8). Prints one JSON record per pair: byte equality, and for JSON or CSV
files the leaves (or cells) that differ, after setting aside only the keys
named with ``--ignore`` (matched against the last path component of a JSON
leaf, or a CSV column name).

Usage:
    compare_json.py --repo <git dir> [--ignore KEY] [--ignore KEY ...] \
        <commit>:<path>=<regenerated file> [...]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def leaves(obj: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten a JSON value into ``{path: scalar}``."""
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        if not obj:
            out[prefix] = {}
        for key, value in obj.items():
            out.update(leaves(value, f"{prefix}/{key}"))
    elif isinstance(obj, list):
        if not obj:
            out[prefix] = []
        for index, value in enumerate(obj):
            out.update(leaves(value, f"{prefix}[{index}]"))
    else:
        out[prefix] = obj
    return out


def last_key(path: str) -> str:
    """Return the final key of a flattened JSON path (list indices removed)."""
    tail = path.rsplit("/", 1)[-1]
    return tail.split("[", 1)[0]


def compare(old: bytes, new: bytes, suffix: str, ignore: set[str]) -> dict[str, Any]:
    """Compare two byte strings structurally where the format allows."""
    record: dict[str, Any] = {
        "sha256_committed": hashlib.sha256(old).hexdigest(),
        "sha256_regenerated": hashlib.sha256(new).hexdigest(),
        "bytes_equal": old == new,
    }
    if old == new:
        return record
    if suffix in {".json", ".geojson"}:
        a, b = leaves(json.loads(old)), leaves(json.loads(new))
        keys = set(a) | set(b)
        differing = sorted(k for k in keys if a.get(k, "<absent>") != b.get(k, "<absent>"))
        ignored = [k for k in differing if last_key(k) in ignore]
        real = [k for k in differing if last_key(k) not in ignore]
        record.update({
            "leaves": len(keys), "differing": len(differing), "ignored": len(ignored),
            "ignored_keys": sorted({last_key(k) for k in ignored}),
            "real_differences": len(real),
            "examples": [{"leaf": k, "committed": a.get(k, "<absent>"),
                          "regenerated": b.get(k, "<absent>")} for k in real[:12]],
            "key_order_equal": list(a) == list(b),
        })
    elif suffix == ".csv":
        ra = list(csv.DictReader(io.StringIO(old.decode())))
        rb = list(csv.DictReader(io.StringIO(new.decode())))
        diffs = []
        for index, (x, y) in enumerate(zip(ra, rb)):
            for col in sorted(set(x) | set(y)):
                if col not in ignore and x.get(col) != y.get(col):
                    diffs.append({"row": index, "col": col, "committed": x.get(col),
                                  "regenerated": y.get(col)})
        record.update({"rows_committed": len(ra), "rows_regenerated": len(rb),
                       "real_differences": len(diffs) + abs(len(ra) - len(rb)),
                       "examples": diffs[:12]})
    else:
        record["real_differences"] = "not structured; bytes differ"
    return record


def main() -> int:
    """Entry point."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--ignore", action="append", default=[],
                    help="a key or column to set aside; repeat for several")
    ap.add_argument("pairs", nargs="+")
    args = ap.parse_args()
    bad = 0
    for pair in args.pairs:
        spec, regenerated = pair.split("=", 1)
        old = subprocess.run(["git", "-C", str(args.repo), "show", spec],
                             capture_output=True, check=True).stdout
        new = Path(regenerated).read_bytes()
        record = {"committed": spec, "regenerated": regenerated,
                  **compare(old, new, Path(regenerated).suffix, set(args.ignore))}
        if not record["bytes_equal"] and record.get("real_differences") not in (0,):
            bad += 1
        print(json.dumps(record))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
