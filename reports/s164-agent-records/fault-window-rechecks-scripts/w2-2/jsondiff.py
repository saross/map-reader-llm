#!/usr/bin/env python3
"""Recursive leaf diff of two JSON documents (W2-2 re-check helper).

Usage: jsondiff.py <a.json|commit:path> <b.json|commit:path> [--repo R]
                   [--ignore KEY ...] [--max N] [--out out.json]

A side written ``commit:path`` is read with ``git -C R show``. Every leaf
(scalar) whose value differs, and every key/index present on one side only,
is reported with its path. ``--ignore`` drops any dict key of that name at
any depth (used ONLY for timestamps/machine paths, and stated in the report).
Exit 0 when identical after ignores, 1 otherwise.
Author: Claude (Opus 5.5), Session 164 W2-2 re-check sub-agent, 2026-10-14.
"""
import argparse
import json
import os
import subprocess
import sys

ap = argparse.ArgumentParser()
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("--repo", default=".")
ap.add_argument("--ignore", nargs="*", default=[])
ap.add_argument("--max", type=int, default=40)
ap.add_argument("--out")
args = ap.parse_args()


def load(spec: str):
    """Load JSON from a file path, or from commit:path via git show."""
    if os.path.exists(spec):
        with open(spec) as fh:
            return json.load(fh)
    commit, path = spec.split(":", 1)
    r = subprocess.run(["git", "-C", args.repo, "show", f"{commit}:{path}"],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


diffs = []


def walk(a, b, path):
    """Append every differing leaf / one-sided key under path."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in args.ignore:
                continue
            if k not in a:
                diffs.append({"path": f"{path}.{k}", "a": "<absent>", "b": b[k]})
            elif k not in b:
                diffs.append({"path": f"{path}.{k}", "a": a[k], "b": "<absent>"})
            else:
                walk(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        for i in range(max(len(a), len(b))):
            if i >= len(a):
                diffs.append({"path": f"{path}[{i}]", "a": "<absent>", "b": b[i]})
            elif i >= len(b):
                diffs.append({"path": f"{path}[{i}]", "a": a[i], "b": "<absent>"})
            else:
                walk(a[i], b[i], f"{path}[{i}]")
    elif a != b or type(a) is not type(b):
        diffs.append({"path": path, "a": a, "b": b})


walk(load(args.a), load(args.b), "$")
print(f"{len(diffs)} differing leaves (ignored keys: {args.ignore or 'none'})")
for d in diffs[: args.max]:
    print("  ", json.dumps(d)[:300])
if args.out:
    with open(args.out, "w") as fh:
        json.dump({"a": args.a, "b": args.b, "ignored_keys": args.ignore,
                   "n_diffs": len(diffs), "diffs": diffs}, fh, indent=1)
sys.exit(0 if not diffs else 1)
