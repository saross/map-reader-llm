#!/usr/bin/env python3
"""
Compare two output trees file by file, and JSON files leaf by leaf.

D62 (1) workstream ``origin-gap-h13-copies`` (2026-10-13). Used for the
integrity check (two independent runs must agree byte for byte, ignoring
only named timestamp keys) and for the before/after tables (every leaf
that differs, with both values).

For each relative path present in either tree the verdict is one of:
``identical`` (same bytes), ``identical-ignoring`` (same after dropping
JSON keys named exactly as an ``--ignore-key``), ``differs`` (with the
differing leaves when both sides parse as JSON), or ``only-a``/``only-b``.

Usage::

    python compare_trees.py <dir_a> <dir_b> [--ignore-key generated_at_utc]
        [--json-out diff.json] [--max-leaves 40]

Exit status 0 when every file is identical or identical-ignoring, 1
otherwise.

Author: Claude Code (Opus 5.5) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def drop_keys(obj: Any, keys: set[str]) -> Any:
    """Return ``obj`` with every dict key in ``keys`` removed, recursively.

    Args:
        obj: A parsed JSON value.
        keys: Key names to drop.

    Returns:
        The pruned value.
    """
    if isinstance(obj, dict):
        return {k: drop_keys(v, keys) for k, v in obj.items() if k not in keys}
    if isinstance(obj, list):
        return [drop_keys(v, keys) for v in obj]
    return obj


def leaves(obj: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten a JSON value to ``{path: scalar}``.

    Args:
        obj: A parsed JSON value.
        prefix: Path so far.

    Returns:
        Mapping of slash-joined paths to scalar leaves.
    """
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(leaves(v, f"{prefix}/{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(leaves(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def load_json(path: Path) -> Any | None:
    """Parse a file as JSON, or return ``None`` if it is not JSON.

    Args:
        path: File path.

    Returns:
        The parsed value, or ``None``.
    """
    try:
        return json.loads(path.read_text())
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def main() -> int:
    """Compare the trees and print one line per file.

    Returns:
        0 when everything matches (ignoring the named keys), else 1.
    """
    parser = argparse.ArgumentParser(description="Compare two output trees.")
    parser.add_argument("a", type=Path)
    parser.add_argument("b", type=Path)
    parser.add_argument("--ignore-key", action="append", default=[])
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--max-leaves", type=int, default=40)
    args = parser.parse_args()
    ignore = set(args.ignore_key)

    def files(root: Path) -> set[str]:
        """Relative paths of every file under ``root`` (or the file itself)."""
        if root.is_file():
            return {""}
        return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}

    rel = sorted(files(args.a) | files(args.b))
    report: dict[str, Any] = {}
    ok = True
    counts: dict[str, int] = {}
    for r in rel:
        pa, pb = (args.a / r if r else args.a), (args.b / r if r else args.b)
        if not pa.exists() or not pb.exists():
            verdict, detail = ("only-b" if not pa.exists() else "only-a"), None
        elif pa.read_bytes() == pb.read_bytes():
            verdict, detail = "identical", None
        else:
            ja, jb = load_json(pa), load_json(pb)
            if ja is None or jb is None:
                verdict, detail = "differs", "not JSON"
            elif drop_keys(ja, ignore) == drop_keys(jb, ignore):
                verdict, detail = "identical-ignoring", None
            else:
                la, lb = leaves(drop_keys(ja, ignore)), leaves(drop_keys(jb, ignore))
                diff = {
                    k: [la.get(k, "<absent>"), lb.get(k, "<absent>")]
                    for k in sorted(set(la) | set(lb)) if la.get(k, "<absent>")
                    != lb.get(k, "<absent>")
                }
                verdict, detail = "differs", diff
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict not in ("identical", "identical-ignoring"):
            ok = False
        report[r or args.a.name] = {"verdict": verdict, "leaves": detail}
        n = len(detail) if isinstance(detail, dict) else 0
        print(f"{verdict:20s} {r or args.a.name}" + (f"  ({n} leaves)" if n else ""))
        if isinstance(detail, dict):
            for k in list(detail)[: args.max_leaves]:
                print(f"    {k}: {detail[k][0]!r} -> {detail[k][1]!r}")
    print("SUMMARY", json.dumps(counts, sort_keys=True))
    if args.json_out:
        args.json_out.write_text(json.dumps(
            {"a": str(args.a), "b": str(args.b), "ignored_keys": sorted(ignore),
             "counts": counts, "files": report}, indent=1, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
