#!/usr/bin/env python3
"""
compare_trees.py — file-by-file comparison of two output trees (read only).

Each file present in either tree is reported as IDENTICAL (bytes), EQUAL-NORM
(JSON equal after dropping ignored keys anywhere and replacing path strings),
or DIFFER with every differing JSON path (up to a limit) or the first
differing lines of a text file. Missing files are reported.

Usage:
    compare_trees.py <tree_a> <tree_b> [--ignore k1,k2,...] [--sub OLD=NEW ...]
                     [--only REGEX] [--max N] [--json OUT]
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path


def norm(o, ignore, subs):
    """Drop ignored keys at any depth and apply string substitutions."""
    if isinstance(o, dict):
        return {k: norm(v, ignore, subs) for k, v in o.items() if k not in ignore}
    if isinstance(o, list):
        return [norm(x, ignore, subs) for x in o]
    if isinstance(o, str):
        for a, b in subs:
            o = o.replace(a, b)
        return o
    return o


def diffs(a, b, path="", out=None, limit=50):
    """Every JSON path at which a and b differ (NaN equals NaN)."""
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(f"{path}/{k}: only in B")
            elif k not in b:
                out.append(f"{path}/{k}: only in A")
            else:
                diffs(a[k], b[k], f"{path}/{k}", out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: list length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            diffs(x, y, f"{path}[{i}]", out, limit)
    else:
        same = a == b or (isinstance(a, float) and isinstance(b, float)
                          and math.isnan(a) and math.isnan(b))
        if not same:
            out.append(f"{path}: {str(a)[:80]!s} vs {str(b)[:80]!s}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--ignore", default="")
    ap.add_argument("--sub", action="append", default=[])
    ap.add_argument("--only", default=None)
    ap.add_argument("--max", type=int, default=12)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()
    ignore = {k for k in args.ignore.split(",") if k}
    subs = [tuple(s.split("=", 1)) for s in args.sub]
    files = sorted({p.relative_to(args.a).as_posix() for p in args.a.rglob("*") if p.is_file()}
                   | {p.relative_to(args.b).as_posix() for p in args.b.rglob("*") if p.is_file()})
    if args.only:
        files = [f for f in files if re.search(args.only, f)]
    record, counts = {}, {"IDENTICAL": 0, "EQUAL-NORM": 0, "DIFFER": 0, "MISSING": 0}
    for f in files:
        pa, pb = args.a / f, args.b / f
        if not pa.exists() or not pb.exists():
            status, detail = "MISSING", ["only in " + ("B" if not pa.exists() else "A")]
        elif pa.read_bytes() == pb.read_bytes():
            status, detail = "IDENTICAL", []
        elif f.endswith((".json", ".geojson")):
            ja, jb = json.loads(pa.read_text()), json.loads(pb.read_text())
            raw = diffs(ja, jb, limit=1000)
            d = diffs(norm(ja, ignore, subs), norm(jb, ignore, subs), limit=args.max)
            status = "EQUAL-NORM" if not d else "DIFFER"
            keys = {re.sub(r"\[\d+\]", "[]", x.split(":")[0]) for x in raw}
            detail = d if d else sorted(keys)[:args.max]
        else:
            la, lb = pa.read_text().splitlines(), pb.read_text().splitlines()
            na = [ln for ln in la]
            nb = [ln for ln in lb]
            for a_, b_ in subs:
                na = [ln.replace(a_, b_) for ln in na]
                nb = [ln.replace(a_, b_) for ln in nb]
            if na == nb:
                status, detail = "EQUAL-NORM", ["paths only"]
            else:
                status = "DIFFER"
                detail = [f"line {i + 1}: {x[:90]!r} vs {y[:90]!r}"
                          for i, (x, y) in enumerate(zip(na, nb)) if x != y][:args.max]
                if len(na) != len(nb):
                    detail.append(f"line count {len(na)} vs {len(nb)}")
        counts[status] += 1
        record[f] = {"status": status, "detail": detail}
        if status != "IDENTICAL":
            print(f"{status:10s} {f}")
            for x in detail:
                print(f"           {x}")
    print("SUMMARY", counts, "files", len(files))
    if args.json:
        args.json.write_text(json.dumps({"counts": counts, "files": record}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
