#!/usr/bin/env python3
"""
W2-1: structured diff of the later (post-generation) edits to a manifest or
sweeps record, between consecutive commits, keyed by cell label / rung.

Lists, per transition, every cell added or removed and every field that
changed, so a reader can see whether an edit is a relabel, a re-point, or a
change of computed value. For sweeps.json it also tests whether the later
version equals the earlier one under a pure key rename.

Usage::

    python later_edits_diff.py --tree <repo> --path <file> --commits c1 c2 ... \
        [--rename old=new] --out result.json

Zero API; read-only.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load(tree: Path, commit: str, path: str):
    """Parse ``commit:path`` as JSON."""
    return json.loads(subprocess.run(["git", "-C", str(tree), "show", f"{commit}:{path}"],
                                     check=True, capture_output=True, text=True).stdout)


def flat(x, p=""):
    """Flatten JSON to {path: leaf}."""
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            out.update(flat(v, f"{p}/{k}"))
        return out
    if isinstance(x, list):
        out = {}
        for i, v in enumerate(x):
            out.update(flat(v, f"{p}[{i}]"))
        return out
    return {p: x}


def rename_keys(x, mapping):
    """Recursively rename dict keys."""
    if isinstance(x, dict):
        return {mapping.get(k, k): rename_keys(v, mapping) for k, v in x.items()}
    if isinstance(x, list):
        return [rename_keys(v, mapping) for v in x]
    return x


def main() -> int:
    """Diff consecutive versions and write the record."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tree", required=True, type=Path)
    ap.add_argument("--path", required=True)
    ap.add_argument("--commits", nargs="+", required=True)
    ap.add_argument("--rename", action="append", default=[])
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    mapping = dict(r.split("=", 1) for r in args.rename)
    out = {"path": args.path, "transitions": []}
    for a, b in zip(args.commits, args.commits[1:]):
        A, B = load(args.tree, a, args.path), load(args.tree, b, args.path)
        t = {"from": a, "to": b}
        if isinstance(A, dict) and "cells" in A and isinstance(A["cells"], list):
            ca = {c["label"]: c for c in A["cells"]}
            cb = {c["label"]: c for c in B["cells"]}
            t["cells_added"] = sorted(set(cb) - set(ca))
            t["cells_removed"] = sorted(set(ca) - set(cb))
            changed = {}
            for lab in sorted(set(ca) & set(cb)):
                fa, fb = flat(ca[lab]), flat(cb[lab])
                d = {k: {"from": fa.get(k, "<absent>"), "to": fb.get(k, "<absent>")}
                     for k in sorted(set(fa) | set(fb))
                     if fa.get(k, "<absent>") != fb.get(k, "<absent>")}
                if d:
                    changed[lab] = d
            t["cells_changed"] = changed
            t["added_cells_content"] = {lab: cb[lab] for lab in t["cells_added"]}
            ta = {k: v for k, v in A.items() if k != "cells"}
            tb = {k: v for k, v in B.items() if k != "cells"}
            t["top_level_equal"] = ta == tb
        else:
            fa, fb = flat(A), flat(B)
            t["leaves_added"] = len(set(fb) - set(fa))
            t["leaves_removed"] = len(set(fa) - set(fb))
            t["leaves_changed"] = sum(1 for k in set(fa) & set(fb) if fa[k] != fb[k])
            if mapping:
                t["equal_under_rename"] = rename_keys(A, mapping) == B
                t["rename"] = mapping
        out["transitions"].append(t)
        print(json.dumps({k: v for k, v in t.items() if k != "added_cells_content"},
                         indent=1)[:3000])
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
