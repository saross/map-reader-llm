"""Compare two trees' chain outputs file by file, listing every differing JSON leaf.

Usage: python integrity_diff.py <tree_a> <tree_b|git:REF:REPO> [--ignore KEY ...]

Byte-identical files are reported as such. For JSON files that differ, every
differing leaf path is listed (so timestamps and paths can be told apart from
numbers); other differing files are listed whole. ``git:REF:REPO`` compares
against the committed blobs at REF in REPO instead of a second tree.
"""
import argparse
import json
import subprocess
from pathlib import Path

DIRS = ["results/grid-2026-08-18", "results/stride-2026-08-25",
        "results/image-b-gs-2026-08-28"]


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


def read_b(spec, rel):
    if spec.startswith("git:"):
        _, ref, repo = spec.split(":", 2)
        proc = subprocess.run(["git", "-C", repo, "show", f"{ref}:{rel}"],
                              capture_output=True, check=False)
        return proc.stdout if proc.returncode == 0 else None
    p = Path(spec) / rel
    return p.read_bytes() if p.exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--ignore", nargs="*", default=[])
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    root = Path(args.a)
    n_same = 0
    for d in DIRS:
        for p in sorted((root / d).rglob("*")):
            if not p.is_file():
                continue
            rel = str(p.relative_to(root))
            if args.only and not any(rel.startswith(o) for o in args.only):
                continue
            a = p.read_bytes()
            b = read_b(args.b, rel)
            if b is None:
                print(f"ONLY-A {rel}")
                continue
            if a == b:
                n_same += 1
                continue
            if rel.endswith(".json"):
                try:
                    la, lb = leaves(json.loads(a)), leaves(json.loads(b))
                except json.JSONDecodeError:
                    print(f"DIFF(bytes, bad json) {rel}")
                    continue
                keys = sorted(set(la) | set(lb))
                diffs = [k for k in keys if la.get(k, "<absent>") != lb.get(k, "<absent>")
                         and not any(ig in k for ig in args.ignore)]
                if not diffs:
                    print(f"SAME-EXCEPT-IGNORED {rel}")
                    n_same += 1
                    continue
                print(f"DIFF {rel}: {len(diffs)} leaves")
                for k in diffs[:40]:
                    print(f"    {k}: {lb.get(k, '<absent>')!r} -> {la.get(k, '<absent>')!r}")
                if len(diffs) > 40:
                    print(f"    ... {len(diffs) - 40} more")
            else:
                print(f"DIFF(bytes) {rel} ({len(b)} -> {len(a)} bytes)")
    print(f"identical (or identical except ignored keys): {n_same}")


if __name__ == "__main__":
    main()
