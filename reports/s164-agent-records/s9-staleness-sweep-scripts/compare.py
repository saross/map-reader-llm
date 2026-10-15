#!/usr/bin/env python3
"""Compare replayed evaluations with their committed files (S9 staleness sweep, S164).

Purpose
-------
For every sidecar a ``run_sweep.py`` run wrote, read the committed
``evaluation.json`` (the checkout is clean at ``HEAD``) and the replay, and
compare the ``summary`` and every ``per_run`` block leaf by leaf, exactly.
``detection_scope`` is excluded from the comparison (only the D50 scorer
writes it, so every pre-D50 cell would differ by its presence) but its counts
are carried into the record, since they say why a cell moved: rows restored
to their origin sheet, rows dropped out of frame, rows switched.

Each differing leaf is classed as:

* ``points``: F1, precision, recall (and their ``*_point`` twins), counts;
* ``intervals``: interval bounds, methods, and bootstrap means;
* ``tile``: anything under ``tile_classification`` (MCC, confusion, ...);
* ``flags``: coverage and interval-reliability flags;
* ``label``: ``tile_classification.tile_join``, which the current scorer
  records and older files lack (no number changes);
* ``format``: any other leaf present on one side only (for example the
  ``f1_point`` aliases older files lack); a value present on both sides
  and different is never ``format``;
* ``other``.

Output: one JSON with a record per cell and the counts by result, written to
``--out``. Nothing else is written.

Usage::

    python compare.py --repo <wt> --inventory <inventory.json> --run <runs/s1-A> \\
        --out <records/compare-s1-A.json>

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

IGNORE = {"detection_scope"}
POINT_LEAVES = {"f1", "f1_point", "precision", "p_point", "recall", "r_point",
                "n_detections", "tp", "fp", "fn", "label"}
FLAG_LEAVES = {"coverage_status", "ci_unreliable", "ci_unreliable_any_buffer",
               "ci_excludes_point", "sparse_coverage", "ci_flag_basis", "coverage_source",
               "n_zero_count_tiles", "zero_fraction", "n_tiles", "threshold",
               "n_processed_tiles", "n_unprocessed_tiles", "coverage_detail"}


def leaves(obj: Any, path: str = "") -> dict[str, Any]:
    """Flatten a JSON value to ``{dotted.path: leaf}``, skipping ignored keys."""
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in IGNORE:
                continue
            out.update(leaves(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(leaves(v, f"{path}[{i}]"))
    else:
        out[path] = obj
    return out


def kind(path: str) -> str:
    """Class one differing leaf path."""
    if path.endswith("tile_classification.tile_join"):
        # The current scorer records which tile join it used; older files lack
        # the key. A label, not a value (D57 (4) S2 record, flag 4).
        return "label"
    if "tile_classification" in path:
        return "tile"
    last = path.rsplit(".", 1)[-1]
    if last in POINT_LEAVES:
        return "points"
    if "ci_" in last or last.endswith("_method") or last == "mean" or "boot" in last:
        return "intervals"
    if last in FLAG_LEAVES or "coverage" in path:
        return "flags"
    return "other"


def at_buffer(summary: dict[str, Any], buffer: int) -> dict[str, Any]:
    """F1, P, R at one buffer from a summary block (four decimals as written)."""
    for b in summary.get("buffers") or []:
        if b.get("buffer_metres") == buffer:
            return {k: b.get(k) for k in ("f1", "precision", "recall")}
    return {}


def tile_mcc(summary: dict[str, Any]) -> Any:
    """The tile-MCC point, or the refusal reason, from a summary block."""
    tc = summary.get("tile_classification") or {}
    if "error" in tc or tc.get("refused"):
        return f"refused:{tc.get('reason') or tc.get('error')}"
    m = tc.get("mcc")
    return m.get("point") if isinstance(m, dict) else m


def scope_counts(doc: dict[str, Any]) -> dict[str, Any]:
    """Sum the replay's ``detection_scope`` counts over its runs (or its summary)."""
    blocks = [r.get("detection_scope") for r in doc.get("per_run") or []]
    blocks = [b for b in blocks if b] or [((doc.get("summary") or {}).get("detection_scope"))]
    out: Counter = Counter()
    cols: set[str] = set()
    for b in blocks:
        if not b:
            continue
        for k, v in b.items():
            if k.startswith("n_") and isinstance(v, int):
                out[k] += v
        cols.update(b.get("origin_columns") or [])
    return dict(out) | {"origin_columns": sorted(cols)}


def is_point_leaf(path: str) -> bool:
    """True for a leaf a reduced-bootstrap replay reproduces (points, counts, MCC point)."""
    last = path.rsplit(".", 1)[-1]
    if "tile_classification" in path:
        return (".confusion." in path or path.endswith((".mcc.point", ".sensitivity.point",
                                                         ".specificity.point"))
                or last in ("mcc", "error", "reason", "refused"))
    return last in POINT_LEAVES - {"label"}


def compare_cell(committed: dict[str, Any], replay: dict[str, Any],
                 points_only: bool = False) -> dict[str, Any]:
    """Diff two evaluation documents (summary and per-run blocks).

    With ``points_only`` the comparison keeps only point leaves
    (:func:`is_point_leaf`), for replays run with a reduced bootstrap.
    """
    a = leaves({"summary": committed.get("summary"), "per_run": committed.get("per_run")})
    b = leaves({"summary": replay.get("summary"), "per_run": replay.get("per_run")})
    if points_only:
        a = {k: v for k, v in a.items() if is_point_leaf(k)}
        b = {k: v for k, v in b.items() if is_point_leaf(k)}
    diffs = sorted(k for k in set(a) | set(b) if a.get(k, "<absent>") != b.get(k, "<absent>"))

    def kind_of(k: str) -> str:
        """``format`` when the leaf exists on one side only, else :func:`kind`."""
        if k not in a or k not in b:
            return "label" if kind(k) == "label" else "format"
        return kind(k)

    kinds = Counter(kind_of(k) for k in diffs)
    cs, rs = committed.get("summary") or {}, replay.get("summary") or {}
    pts_moved = [k for k in diffs if kind_of(k) == "points" and not k.endswith(".label")]
    max_df1 = 0.0
    for bc in cs.get("buffers") or []:
        br = next((x for x in rs.get("buffers") or []
                   if x.get("buffer_metres") == bc.get("buffer_metres")), None)
        if br and isinstance(bc.get("f1"), (int, float)) and isinstance(br.get("f1"),
                                                                          (int, float)):
            max_df1 = max(max_df1, abs(br["f1"] - bc["f1"]))
    return {
        "identical": not diffs,
        "kinds": dict(kinds),
        "n_diffs": len(diffs),
        "examples": [[k, a.get(k, "<absent>"), b.get(k, "<absent>")] for k in diffs[:12]],
        "points_move": bool(pts_moved),
        "tile_moves": kinds.get("tile", 0) > 0,
        "diff_kinds_by_leaf": {k: kind_of(k) for k in diffs[:40]},
        "mcc_point": [tile_mcc(cs), tile_mcc(rs)],
        "at20": [at_buffer(cs, 20), at_buffer(rs, 20)],
        "at50": [at_buffer(cs, 50), at_buffer(rs, 50)],
        "n_det": [cs.get("n_detections"), rs.get("n_detections")],
        "max_abs_df1_any_buffer": round(max_df1, 6),
        "scope": scope_counts(replay),
    }


def main() -> int:
    """Compare every replayed cell of one run and write the record."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--points-only", action="store_true",
                    help="Compare point leaves only (for points_cell.py replays).")
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    inv = {c["eval"]: c for c in json.loads(args.inventory.read_text())["cells"]}
    recs: list[dict[str, Any]] = []
    for side_path in sorted((args.run / "sidecars").glob("*.json")):
        side = json.loads(side_path.read_text())
        rel = side["eval"]
        rec: dict[str, Any] = {"eval": rel, "rc": side.get("rc"),
                               "error": side.get("error"),
                               "group": (inv.get(rel) or {}).get("group")}
        rep_path = args.run / "cells" / rel
        if side.get("rc") == 0 and rep_path.is_file():
            committed = json.loads((repo / rel).read_text())
            replay = json.loads(rep_path.read_text())
            rec.update(compare_cell(committed, replay, args.points_only))
            pt = (side.get("point") or {}).get("per_buffer", {}).get("20") or {}
            rec["unrounded20"] = pt
            rec["unrounded_mcc"] = (side.get("point") or {}).get("mcc")
            rec["result"] = ("identical" if rec["identical"]
                             else "label-only" if set(rec["kinds"]) <= {"label", "format"}
                             else "points" if rec["points_move"]
                             else "tile" if rec["tile_moves"]
                             else "+".join(sorted(rec["kinds"])))
        else:
            rec["result"] = "replay-failed"
        recs.append(rec)
    counts = Counter((r["group"], r["result"]) for r in recs)
    doc = {"run": str(args.run), "n": len(recs),
           "counts": {f"{g}|{res}": n for (g, res), n in sorted(counts.items())},
           "cells": recs}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=1, sort_keys=True, default=str) + "\n")
    for k, v in doc["counts"].items():
        print(f"{v:5d}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
