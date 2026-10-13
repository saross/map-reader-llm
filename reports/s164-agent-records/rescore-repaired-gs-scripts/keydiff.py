#!/usr/bin/env python3
"""
Compare two extract JSONs key by key (exactly), over the keys they share.

Usage: python keydiff.py <a.json> <b.json> [--only-prefix P ...]

Prints the count of shared keys, keys only in one side, and every shared key
whose value differs (exact JSON equality). Used for run A = run B integrity,
ORIGIN against PR #42's reported "after" extract, and ORIGIN against COMMITTED.

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import argparse
import json

ap = argparse.ArgumentParser()
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("--only-prefix", nargs="*", default=None)
args = ap.parse_args()
a, b = json.load(open(args.a)), json.load(open(args.b))
if args.only_prefix:
    keep = lambda k: any(k.startswith(p) for p in args.only_prefix)  # noqa: E731
    a = {k: v for k, v in a.items() if keep(k)}
    b = {k: v for k, v in b.items() if keep(k)}
shared = sorted(set(a) & set(b))
diff = [k for k in shared if a[k] != b[k]]
print(f"shared {len(shared)}, only-a {len(set(a) - set(b))}, only-b {len(set(b) - set(a))}, "
      f"differing {len(diff)}")
for k in sorted(set(a) - set(b)):
    print(f"  only-a: {k}")
for k in sorted(set(b) - set(a)):
    print(f"  only-b: {k}")
for k in diff:
    print(f"  {k}: {json.dumps(a[k])[:300]}  |  {json.dumps(b[k])[:300]}")
