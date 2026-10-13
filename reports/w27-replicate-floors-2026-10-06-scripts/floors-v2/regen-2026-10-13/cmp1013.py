#!/usr/bin/env python3
"""
Compare one W2.7 floors-v2 regeneration run with a reference tree (scratch tool).

Written for the 2026-10-13 regeneration (D62 (1) after PR #44, with PR #33's
library via main). Each output file of a run (``out/1013-<run>/``) is paired
with its counterpart in a reference tree, and the pair is reported as
identical bytes, or as a row-level (CSV) or leaf-level (JSON) difference with
the largest numerical change. Gzipped references are decompressed first.

Usage::

    python cmp1013.py <run dir> <reference kind> <reference root> <json out>

Reference kinds:
    committed  the repository tree (``<root>`` = the clone), i.e. PR #38's
               committed files at e2a424fea (the merge of main left them alone)
    pr44       PR #44's r1 scratch tree (``<root>`` = .../origin-gap.../w27/r1)
    run        another run of this script's driver (``<root>`` = out/1013-r2)

Author: Claude Code (Opus 5.5) for Shawn Ross | Created: 2026-10-13 | Apache 2.0
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import sys
from pathlib import Path

W = "reports/w27-replicate-floors-2026-10-06-scripts"
F = f"{W}/floors-v2"

#: (run-relative path, committed path relative to the clone, PR #44 r1 path or None)
PAIRS = [
    ("w27/subset_cells.json", f"{W}/subset_cells.json", "w27/subset_cells.json"),
    ("w27/subset_pairs.csv", f"{W}/subset_pairs.csv", "w27/subset_pairs.csv"),
    ("w27/gates.json", f"{W}/gates.json", "w27/gates.json"),
    ("w27/verifier_provenance.json", f"{W}/verifier_provenance.json",
     "w27/verifier_provenance.json"),
    ("gate/scorer_gate.json", f"{F}/results/scorer_gate.json", "gate/scorer_gate.json"),
    ("gate/scorer_gate_cells.csv", f"{F}/results/scorer_gate_cells.csv",
     "gate/scorer_gate_cells.csv"),
    ("out55/subset_cells_all.csv", f"{F}/results/subset_cells_all.csv",
     "out55/subset_cells_all.csv"),
    ("out55/sim_cells.csv", f"{F}/results/sim_cells.csv.gz", "out55/sim_cells.csv"),
    ("out55/gates.json", f"{F}/results/gates55.json", "out55/gates.json"),
    ("outgs/gs_slice_cells.csv", f"{F}/results/gs_slice_cells.csv.gz", None),
    ("outgs/gates.json", f"{F}/results/gates_gs.json", None),
    ("rescreen.out", f"{F}/logs/rescreen.out", "rescreen.out"),
] + [
    (f"results/{n}", f"{F}/results/{n}", f"results/{n}")
    for n in (
        "cell_sds.csv", "extrapolation55.csv", "floors55_all.csv", "gs_k10_check.csv",
        "gs_k10_summary.csv", "gs_validation.csv", "gs_validation_summary.csv",
        "nested_rung55.csv", "nested_threshold55.csv", "propensity55.csv", "rescreen.csv",
        "results.json", "tables.md",
    )
]


def read(path: Path) -> bytes:
    """The file's bytes, decompressed if it is gzipped."""
    data = path.read_bytes()
    return gzip.decompress(data) if path.suffix == ".gz" else data


def num(x: str) -> float | None:
    """A cell as a float, or None if it is not numeric."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def csv_diff(a: bytes, b: bytes) -> dict:
    """Row-by-row difference of two CSVs (same order assumed; checked by row count)."""
    ra = list(csv.reader(io.StringIO(a.decode())))
    rb = list(csv.reader(io.StringIO(b.decode())))
    out: dict = {"rows_new": len(ra) - 1, "rows_ref": len(rb) - 1,
                 "header_same": ra[:1] == rb[:1]}
    if len(ra) != len(rb) or ra[:1] != rb[:1]:
        return out
    head = ra[0]
    diffs, max_abs, cols = [], 0.0, set()
    for i, (x, y) in enumerate(zip(ra[1:], rb[1:]), start=1):
        if x == y:
            continue
        changed = {}
        for h, u, v in zip(head, x, y):
            if u != v:
                cols.add(h)
                fu, fv = num(u), num(v)
                if fu is not None and fv is not None:
                    max_abs = max(max_abs, abs(fu - fv))
                changed[h] = [v, u]
        diffs.append({"row": i, "changed (ref -> new)": changed})
    out.update(rows_differ=len(diffs), columns_differ=sorted(cols), max_abs_numeric=max_abs,
               examples=diffs[:40])
    return out


def leaves(obj, prefix=""):
    """Flatten a JSON value to (path, leaf) pairs."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{prefix}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def json_diff(a: bytes, b: bytes) -> dict:
    """Leaf-level difference of two JSON documents."""
    la, lb = dict(leaves(json.loads(a))), dict(leaves(json.loads(b)))
    only_new = sorted(set(la) - set(lb))
    only_ref = sorted(set(lb) - set(la))
    changed, max_abs = [], 0.0
    for k in sorted(set(la) & set(lb)):
        if la[k] != lb[k]:
            u, v = la[k], lb[k]
            if isinstance(u, (int, float)) and isinstance(v, (int, float)) \
                    and not isinstance(u, bool) and not isinstance(v, bool):
                max_abs = max(max_abs, abs(u - v))
            changed.append({"leaf": k, "ref": v, "new": u})
    return {"leaves_changed": len(changed), "max_abs_numeric": max_abs,
            "only_in_new": only_new[:40], "only_in_ref": only_ref[:40],
            "changed": changed[:80]}


def main() -> int:
    """Compare every pair and write the summary."""
    run, kind, root, dest = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
    report: dict = {"run": str(run), "reference": kind, "root": str(root), "files": {}}
    for new_rel, committed_rel, pr44_rel in PAIRS:
        ref_rel = {"committed": committed_rel, "pr44": pr44_rel, "run": new_rel}[kind]
        if ref_rel is None:
            continue
        pn, pr = run / new_rel, root / ref_rel
        if not pn.exists() or not pr.exists():
            report["files"][new_rel] = {"missing": [str(p) for p in (pn, pr) if not p.exists()]}
            continue
        a, b = read(pn), read(pr)
        if a == b:
            report["files"][new_rel] = "identical bytes"
        elif new_rel.endswith(".csv"):
            report["files"][new_rel] = csv_diff(a, b)
        elif new_rel.endswith(".json"):
            report["files"][new_rel] = json_diff(a, b)
        else:
            report["files"][new_rel] = {"differs": True, "bytes_new": len(a), "bytes_ref": len(b)}
    dest.write_text(json.dumps(report, indent=1) + "\n")
    for k, v in report["files"].items():
        if v == "identical bytes":
            print(f"{k}: identical bytes")
        elif "rows_differ" in v:
            print(f"{k}: {v['rows_differ']} of {v['rows_new']} rows differ; "
                  f"columns {v['columns_differ']}; max |d| {v['max_abs_numeric']:.3g}")
        elif "leaves_changed" in v:
            print(f"{k}: {v['leaves_changed']} JSON leaves differ (max |d| "
                  f"{v['max_abs_numeric']:.3g}); only new {len(v['only_in_new'])}, "
                  f"only ref {len(v['only_in_ref'])}")
        else:
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
