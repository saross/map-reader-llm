#!/usr/bin/env python3
"""Compare two directories of generated artefacts, file by file.

JSON files are compared after dropping keys whose name is in --drop-keys
(at any depth) and after replacing each --root prefix with "<ROOT>/" in
every string; other files are compared as text after the same root
replacement. Prints counts and, for each differing file, up to --show leaf
differences. With --files, only the listed relative paths are compared.

Usage: cmp_dirs.py <dir1> <dir2> [--root P ...] [--drop-keys k,k] [--show N]
       [--files list.txt] [--ignore-missing-in-2]
"""
import argparse
import json
from pathlib import Path


def norm(obj, drop, roots):
    """Return obj with dropped keys removed and run roots replaced."""
    if isinstance(obj, dict):
        return {k: norm(v, drop, roots) for k, v in obj.items() if k not in drop}
    if isinstance(obj, list):
        return [norm(v, drop, roots) for v in obj]
    if isinstance(obj, str):
        for r in roots:
            obj = obj.replace(r, "<ROOT>/")
        return obj
    return obj


def leaves(obj, path=""):
    """Yield (path, value) for every leaf."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, obj


ap = argparse.ArgumentParser()
ap.add_argument("d1", type=Path)
ap.add_argument("d2", type=Path)
ap.add_argument("--root", action="append", default=[])
ap.add_argument("--drop-keys", default="timestamp")
ap.add_argument("--show", type=int, default=6)
ap.add_argument("--files", type=Path)
args = ap.parse_args()
roots = [r.rstrip("/") + "/" for r in args.root]
drop = set(filter(None, args.drop_keys.split(",")))
if args.files:
    rels = [Path(x) for x in args.files.read_text().split()]
else:
    rels = sorted(p.relative_to(args.d1) for p in args.d1.rglob("*") if p.is_file())
same = diff = miss = byte_same = 0
for rel in rels:
    f1, f2 = args.d1 / rel, args.d2 / rel
    if not f2.exists() or not f1.exists():
        miss += 1
        print(f"MISSING {rel} ({'d2' if not f2.exists() else 'd1'})")
        continue
    if f1.read_bytes() == f2.read_bytes():
        byte_same += 1
        same += 1
        continue
    if rel.suffix == ".json":
        a = norm(json.loads(f1.read_text()), drop, roots)
        b = norm(json.loads(f2.read_text()), drop, roots)
        if a == b:
            same += 1
            continue
        diff += 1
        la, lb = dict(leaves(a)), dict(leaves(b))
        keys = sorted(set(la) | set(lb))
        d = [(k, la.get(k, "<absent>"), lb.get(k, "<absent>")) for k in keys
             if la.get(k, "<absent>") != lb.get(k, "<absent>")]
        print(f"DIFF {rel}: {len(d)} leaves")
        for k, x, y in d[: args.show]:
            print(f"    {k}: {x!r} -> {y!r}")
    else:
        a, b = f1.read_text(), f2.read_text()
        for r in roots:
            a, b = a.replace(r, "<ROOT>/"), b.replace(r, "<ROOT>/")
        if a == b:
            same += 1
            continue
        diff += 1
        la, lb = a.splitlines(), b.splitlines()
        d = [(i + 1, x, y) for i, (x, y) in enumerate(zip(la, lb)) if x != y]
        print(f"DIFF {rel}: {len(d)} lines differ (lengths {len(la)}/{len(lb)})")
        for i, x, y in d[: args.show]:
            print(f"    L{i}: {x[:110]!r}\n      -> {y[:110]!r}")
print(f"SUMMARY files={len(rels)} equal={same} (byte-identical {byte_same}) "
      f"differ={diff} missing={miss}")
