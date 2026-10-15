#!/usr/bin/env python3
"""
Compare two output trees file by file, ignoring timestamps and run roots.

Usage: python cmp_tree.py <dir_a> <dir_b> [--roots ROOT ...] [--ignore KEY ...]

Every file present in either tree is compared. A byte mismatch is re-checked
after (a) dropping JSON keys whose name is in --ignore (default: timestamp,
generated_at_utc, generated_at) at any depth and (b) replacing each --roots
prefix with "<ROOT>" in every string, so two runs that read the same files
from different checkouts compare equal, and (c) for Markdown, dropping the
"**Generated**" line a rendered evaluation.md stamps (S164 restatement pass
addition). Anything else that differs is listed
with up to 20 of its differing JSON leaves. Exit 1 on any mismatch.

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import argparse
import json
import sys
from pathlib import Path


def norm(obj, roots, ignore):
    """Drop ignored keys; replace run roots in strings."""
    if isinstance(obj, dict):
        return {k: norm(v, roots, ignore) for k, v in obj.items() if k not in ignore}
    if isinstance(obj, list):
        return [norm(v, roots, ignore) for v in obj]
    if isinstance(obj, str):
        for r in roots:
            obj = obj.replace(r, "<ROOT>")
        return obj
    return obj


def leaves(obj, prefix=""):
    """Flatten JSON into {path: value}."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out.update(leaves(v, f"{prefix}/{k}"))
        return out
    if isinstance(obj, list):
        out = {}
        for i, v in enumerate(obj):
            out.update(leaves(v, f"{prefix}[{i}]"))
        return out
    return {prefix: obj}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--roots", nargs="*", default=[])
    ap.add_argument("--ignore", nargs="*",
                    default=["timestamp", "generated_at_utc", "generated_at"])
    args = ap.parse_args()
    roots = sorted(args.roots, key=len, reverse=True)
    ignore = set(args.ignore)
    files = sorted({p.relative_to(args.a) for p in args.a.rglob("*") if p.is_file()}
                   | {p.relative_to(args.b) for p in args.b.rglob("*") if p.is_file()})
    same_bytes = same_norm = 0
    bad = []
    for rel in files:
        pa, pb = args.a / rel, args.b / rel
        if not pa.exists() or not pb.exists():
            bad.append((f"missing in {'a' if not pa.exists() else 'b'}: {rel}", []))
            continue
        ba, bb = pa.read_bytes(), pb.read_bytes()
        if ba == bb:
            same_bytes += 1
            continue
        if rel.suffix in (".json", ".geojson"):
            ja, jb = norm(json.loads(ba), roots, ignore), norm(json.loads(bb), roots, ignore)
            if ja == jb:
                same_norm += 1
                continue
            la, lb = leaves(ja), leaves(jb)
            keys = sorted(k for k in set(la) | set(lb)
                          if la.get(k, "<absent>") != lb.get(k, "<absent>"))
            bad.append((f"differs: {rel} ({len(keys)} leaves)",
                        [f"{k}: {la.get(k, '<absent>')!r} | {lb.get(k, '<absent>')!r}"
                         for k in keys[:20]]))
            continue
        ta, tb = ba.decode(errors="replace"), bb.decode(errors="replace")
        for r in roots:
            ta, tb = ta.replace(r, "<ROOT>"), tb.replace(r, "<ROOT>")
        if rel.suffix == ".md":
            # A rendered evaluation.md stamps its generation time on one line.
            ta = "\n".join(x for x in ta.splitlines()
                           if not x.startswith("**Generated**"))
            tb = "\n".join(x for x in tb.splitlines()
                           if not x.startswith("**Generated**"))
        if ta == tb:
            same_norm += 1
            continue
        bad.append((f"differs (text): {rel}", []))
    print(f"{len(files)} files: {same_bytes} byte-identical, {same_norm} identical after "
          f"normalising, {len(bad)} mismatched")
    for head, lines in bad:
        print("  " + head)
        for line in lines:
            print("      " + line)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
