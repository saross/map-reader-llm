#!/usr/bin/env python3
"""
W2-1 comparison tool: regenerated file versus the committed blob.

For each (path, commit) pair, reads the regenerated file from a replay tree
and the reference from ``git show <commit>:<path>`` (in the same repository),
compares SHA-256 first, and on a mismatch falls back to a structured diff:
JSON -> recursive leaf diff (key order ignored, every differing leaf listed),
CSV -> cell diff, other text -> first differing line. Nothing is ignored
unless ``--ignore-key`` names it; ignored keys are reported in the output.

Usage::

    python compare_files.py --tree <replay tree> --out <result.json> \
        --pair <commit>:<path> [--pair ...] [--ignore-key timestamp]

Zero API; read-only on the repository.
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


def git_blob(tree: Path, commit: str, path: str) -> bytes:
    """Return the bytes of ``commit:path`` in ``tree``'s repository."""
    return subprocess.run(["git", "-C", str(tree), "show", f"{commit}:{path}"],
                          check=True, capture_output=True).stdout


def leaf_diff(a, b, path="", ignore=(), out=None, limit=200):
    """Recursive leaf diff of two JSON values; returns a list of differences."""
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in ignore:
                continue
            p = f"{path}/{k}"
            if k not in a:
                out.append({"path": p, "regen": "<missing>", "committed": b[k]})
            elif k not in b:
                out.append({"path": p, "regen": a[k], "committed": "<missing>"})
            else:
                leaf_diff(a[k], b[k], p, ignore, out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append({"path": path, "regen_len": len(a), "committed_len": len(b)})
        for i, (x, y) in enumerate(zip(a, b)):
            leaf_diff(x, y, f"{path}[{i}]", ignore, out, limit)
    elif a != b or type(a) is not type(b):
        d = {"path": path, "regen": a, "committed": b}
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            d["abs_diff"] = abs(a - b)
        out.append(d)
    return out


def key_order_equal(a, b) -> bool:
    """True when every dict in the two JSON values lists its keys in the same order."""
    if isinstance(a, dict) and isinstance(b, dict):
        return list(a) == list(b) and all(key_order_equal(a[k], b[k]) for k in a if k in b)
    if isinstance(a, list) and isinstance(b, list):
        return all(key_order_equal(x, y) for x, y in zip(a, b))
    return True


def compare(tree: Path, commit: str, path: str, ignore: tuple[str, ...]) -> dict:
    """Compare one regenerated file against its committed blob."""
    regen_path = tree / path
    res = {"path": path, "commit": commit}
    if not regen_path.exists():
        res["verdict"] = "MISSING-REGEN"
        return res
    regen = regen_path.read_bytes()
    ref = git_blob(tree, commit, path)
    res["sha256_regen"] = hashlib.sha256(regen).hexdigest()
    res["sha256_committed"] = hashlib.sha256(ref).hexdigest()
    res["bytes_regen"], res["bytes_committed"] = len(regen), len(ref)
    if regen == ref:
        res["verdict"] = "BYTE-IDENTICAL"
        return res
    if path.endswith(".json"):
        a, b = json.loads(regen), json.loads(ref)
        diffs = leaf_diff(a, b, ignore=ignore)
        res["ignored_keys"] = list(ignore)
        res["n_leaf_diffs"] = len(diffs)
        res["leaf_diffs"] = diffs[:50]
        res["key_order_equal"] = key_order_equal(a, b)
        res["verdict"] = "FIELD-IDENTICAL" if not diffs else "DIFFERS"
    elif path.endswith(".csv"):
        ra = list(csv.reader(io.StringIO(regen.decode())))
        rb = list(csv.reader(io.StringIO(ref.decode())))
        cells = []
        if len(ra) != len(rb):
            cells.append({"rows_regen": len(ra), "rows_committed": len(rb)})
        for i, (x, y) in enumerate(zip(ra, rb)):
            for j, (u, v) in enumerate(zip(x, y)):
                if u != v:
                    cells.append({"row": i, "col": rb[0][j] if j < len(rb[0]) else j,
                                  "regen": u, "committed": v})
        res["n_cell_diffs"] = len(cells)
        res["cell_diffs"] = cells[:50]
        res["verdict"] = "CELL-IDENTICAL" if not cells else "DIFFERS"
    else:
        la, lb = (regen.decode(errors="replace").splitlines(),
                  ref.decode(errors="replace").splitlines())
        first = next((i for i, (x, y) in enumerate(zip(la, lb)) if x != y), min(len(la), len(lb)))
        res["first_diff_line"] = first
        res["lines_regen"], res["lines_committed"] = len(la), len(lb)
        res["verdict"] = "DIFFERS"
    return res


def main() -> int:
    """Parse arguments, compare every pair, write the JSON result."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tree", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--pair", action="append", required=True,
                    help="<commit>:<repo-relative path>")
    ap.add_argument("--ignore-key", action="append", default=[])
    args = ap.parse_args()
    results = []
    for pair in args.pair:
        commit, path = pair.split(":", 1)
        results.append(compare(args.tree, commit, path, tuple(args.ignore_key)))
    args.out.write_text(json.dumps(results, indent=2) + "\n")
    for r in results:
        print(f"{r['verdict']:16s} {r['commit'][:9]} {r['path']}")
    return 0 if all(r["verdict"] in ("BYTE-IDENTICAL",) for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
