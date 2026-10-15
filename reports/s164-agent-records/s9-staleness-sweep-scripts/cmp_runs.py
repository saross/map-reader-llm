#!/usr/bin/env python3
"""Integrity check: two independent replay runs must agree apart from timestamps.

Purpose
-------
The S9 staleness sweep (S164, 2026-10-14) runs every replay twice, in fresh
processes and separate output directories. This compares run A's ``cells/``
tree with run B's, file by file, and the two runs' sidecar points:

* ``evaluation.json``: equal after removing ``timestamp`` and
  ``_metadata.generated_at_utc`` and replacing each run's own root path;
* ``evaluation.md``: equal after removing the ``**Generated**`` line and the
  root path;
* anything else (``evaluation.csv``): byte-equal after the root path.

A file counts as byte-identical when no normalisation was needed. Output:
counts and every difference, to ``--out``.

Usage::

    python cmp_runs.py --a runs/s1-A --b runs/s1-B --out records/integrity-s1.json

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VOLATILE_TOP = {"timestamp"}
VOLATILE_META = {"generated_at_utc"}


def norm_json(text: str, root: str) -> Any:
    """Parse an evaluation document with its run root and timestamps removed."""
    doc = json.loads(text.replace(root, "<RUN>"))
    for k in VOLATILE_TOP:
        doc.pop(k, None)
    meta = doc.get("_metadata")
    if isinstance(meta, dict):
        for k in VOLATILE_META:
            meta.pop(k, None)
    return doc


def norm_md(text: str, root: str) -> str:
    """Drop the ``**Generated**`` line and the run root from a rendering."""
    return "\n".join(ln for ln in text.replace(root, "<RUN>").splitlines()
                     if not ln.startswith("**Generated**"))


def main() -> int:
    """Compare the two runs and write the record."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", type=Path, required=True)
    ap.add_argument("--b", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    ra, rb = args.a.resolve(), args.b.resolve()
    files_a = {p.relative_to(ra / "cells") for p in (ra / "cells").rglob("*") if p.is_file()}
    files_b = {p.relative_to(rb / "cells") for p in (rb / "cells").rglob("*") if p.is_file()}
    res: dict[str, Any] = {"only_a": sorted(map(str, files_a - files_b)),
                           "only_b": sorted(map(str, files_b - files_a)),
                           "byte_identical": 0, "identical_after_norm": 0, "differ": []}
    for rel in sorted(files_a & files_b):
        ta = (ra / "cells" / rel).read_bytes()
        tb = (rb / "cells" / rel).read_bytes()
        if ta == tb:
            res["byte_identical"] += 1
            continue
        sa, sb = ta.decode(), tb.decode()
        if rel.suffix == ".json":
            same = norm_json(sa, str(ra)) == norm_json(sb, str(rb))
        elif rel.suffix == ".md":
            same = norm_md(sa, str(ra)) == norm_md(sb, str(rb))
        else:
            same = sa.replace(str(ra), "<RUN>") == sb.replace(str(rb), "<RUN>")
        if same:
            res["identical_after_norm"] += 1
        else:
            res["differ"].append(str(rel))
    # Sidecar points (unrounded) must be equal too.
    pts_diff = []
    sides_a = {p.name: p for p in (ra / "sidecars").glob("*.json")}
    sides_b = {p.name: p for p in (rb / "sidecars").glob("*.json")}
    for name in sorted(set(sides_a) & set(sides_b)):
        pa = json.loads(sides_a[name].read_text()).get("point")
        pb = json.loads(sides_b[name].read_text()).get("point")
        if pa != pb:
            pts_diff.append(name)
    res.update({"n_files_a": len(files_a), "n_files_b": len(files_b),
                "n_sidecars_common": len(set(sides_a) & set(sides_b)),
                "sidecar_points_differ": pts_diff})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in res.items()}))
    return 0 if not res["differ"] and not pts_diff and not res["only_a"] \
        and not res["only_b"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
