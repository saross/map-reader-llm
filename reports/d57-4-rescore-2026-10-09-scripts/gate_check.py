"""Gate every regenerated Phase 2 cell against the expected values and the plan's checks.

D57 (4) re-score, 2026-10-09 (Session 163). Read-only: reads the regenerated
``evaluation.json`` files in the NEW worktree, their committed versions from
``HEAD``, the replay sidecars, and ``rescore_b.jsonl``; writes ``--out``.

Gates per cell (plan § 3.1 and § 7):

A. **Inverted point gate.** Every F1, P and R at every buffer the expected row
   carries equals the sidecar's full-precision value (the scorer's own
   unrounded point, captured during the replay) to 1e-9.
B. **MCC or its refusal** equals the expected value (1e-9) or refusal reason.
C. **File agrees with the sidecar.** The regenerated file's four-decimal F1, P
   and R are the scorer's rounding of the sidecar values (``round(x, 4)`` for
   one run; ``round(mean(round(x_i, 4)), 4)`` for a multi-run mean), and its
   MCC point is within the same rounding.
D. **Detection scope.** The summary (and every per-run block) carries
   ``detection_scope`` with every ``_DETECTION_SCOPE_COUNTS`` key;
   ``n_origin_switched == 0``; ``n_out_of_frame`` and ``n_origin_restored``
   equal the expected row's ``new_scope``.
E. **Feature counts unchanged.** ``n_detections`` (per run where multi-run)
   equals the committed value.
F. **Recipe.** The regenerated ``cli_args`` equal the committed ones apart from
   ``require_clean_inputs`` (added by plan) and keys the newer scorer records
   by default (``tile_join``); any other difference fails.

Also records, per cell, the deltas the S2 report needs: OFF (the jsonl's old
scorer values) and NEW (the sidecar) at full precision, and the committed and
regenerated four-decimal F1 at 20 m and 50 m.

Usage (on sapphire)::

    .venv/bin/python gate_check.py --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --rescore-b ~/scratch/source-tile-gap-2026-10-08/out/rescore_b.jsonl \\
        --cells ~/scratch/d57-4-rescore-2026-10-09/out/phase2_cells.json \\
        --sidecars ~/scratch/d57-4-rescore-2026-10-09/out/sidecars \\
        --out ~/scratch/d57-4-rescore-2026-10-09/out/gate.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d57_common as dc  # noqa: E402
from run_replays import slug  # noqa: E402

#: Keys the newer scorer records in ``cli_args`` by default, absent from older cells.
DEFAULT_ADDED_CLI_KEYS = {"tile_join": "id", "require_clean_inputs": False}


def file_point(ev: dict[str, Any]) -> tuple[dict[str, dict[str, float]], float | None]:
    """Four-decimal per-buffer values and MCC point from a regenerated file."""
    return dc.per_buffer_committed(ev), dc.committed_mcc(ev)


def expected_file_value(runs: list[dict[str, Any]], buf: str, m: str) -> float:
    """What the scorer writes for one metric: its rounding of the unrounded value(s)."""
    vals = [0.0 if r["n_det"] == 0 else r["per_buffer"][buf][m] for r in runs]
    if len(vals) == 1:
        return round(vals[0], 4)
    return round(float(np.mean([round(v, 4) for v in vals])), 4)


def gate_one(repo: Path, cell: dict[str, Any], side: dict[str, Any],
             row: dict[str, Any]) -> dict[str, Any]:
    """Run gates A–F for one cell."""
    rel = cell["eval"]
    rec: dict[str, Any] = {"eval": rel, "group": cell.get("group"),
                           "registered": cell.get("registered"), "fails": [], "notes": []}
    fails: list[str] = rec["fails"]
    if side.get("rc") != 0:
        fails.append(f"replay rc={side.get('rc')} {side.get('error', '')}")
        return rec
    out_dir = Path(cell["output_dir"]) if cell.get("output_dir") else repo / Path(rel).parent
    new_ev = json.loads((out_dir / "evaluation.json").read_text())
    old_ev = dc.committed_eval(repo, rel) or {}
    got, exp = side["point"], row.get("new") or {}

    # A. inverted point gate, full precision
    worst, n_cmp = 0.0, 0
    for buf, vals in (exp.get("per_buffer") or {}).items():
        g = (got.get("per_buffer") or {}).get(buf)
        if g is None:
            fails.append(f"A: buffer {buf} not scored")
            continue
        for m in dc.METRICS:
            d = abs(g[m] - vals[m])
            n_cmp += 1
            worst = max(worst, d)
            if d > dc.EPS:
                fails.append(f"A: {m}@{buf} new {g[m]!r} expected {vals[m]!r}")
    rec["A_values_compared"], rec["A_worst"] = n_cmp, worst
    rec["ungated_buffers"] = sorted(set(got.get("per_buffer") or {})
                                    - set(exp.get("per_buffer") or {}), key=int)

    # B. MCC or its refusal
    if isinstance(exp.get("mcc"), (int, float)):
        if not isinstance(got.get("mcc"), (int, float)):
            fails.append(f"B: MCC expected {exp['mcc']} got {got.get('mcc_refused')}")
        elif abs(got["mcc"] - exp["mcc"]) > dc.EPS:
            fails.append(f"B: MCC {got['mcc']!r} expected {exp['mcc']!r}")
        rec["B"] = "mcc"
    elif exp.get("mcc_refused"):
        if got.get("mcc_refused") != exp["mcc_refused"]:
            fails.append(f"B: refusal {got.get('mcc_refused')!r} expected "
                         f"{exp['mcc_refused']!r}")
        rec["B"] = "refusal"
    else:
        rec["B"] = "not in expected"
        if got.get("mcc") is not None or got.get("mcc_refused"):
            rec["notes"].append(f"B: replay has MCC {got.get('mcc')} / refusal "
                                f"{got.get('mcc_refused')} the expected row does not carry")

    # C. file agrees with the sidecar (scorer rounding)
    fpb, fmcc = file_point(new_ev)
    for buf in got.get("per_buffer") or {}:
        f = fpb.get(buf)
        if f is None:
            fails.append(f"C: file lacks buffer {buf}")
            continue
        for m in dc.METRICS:
            want = expected_file_value(side["runs"], buf, m)
            if f[m] is None or abs(f[m] - want) > 1e-12:
                fails.append(f"C: file {m}@{buf} {f[m]} vs scorer rounding {want}")
    if isinstance(got.get("mcc"), (int, float)):
        tol = 5.0001e-5 if len(side["runs"]) == 1 else 1.0001e-4
        if fmcc is None or abs(fmcc - got["mcc"]) > tol:
            fails.append(f"C: file MCC {fmcc} vs sidecar {got['mcc']}")

    # D. detection scope
    keys = list(dc.SCOPE_COUNT_KEYS)
    if side.get("scope_count_keys") != keys:
        fails.append(f"D: scorer _DETECTION_SCOPE_COUNTS {side.get('scope_count_keys')}")
    blocks = [("summary", (new_ev.get("summary") or {}).get("detection_scope"))]
    blocks += [(f"per_run[{i}]", r.get("detection_scope"))
               for i, r in enumerate(new_ev.get("per_run") or [])]
    for where, block in blocks:
        if block is None:
            fails.append(f"D: {where} carries no detection_scope")
            continue
        missing = [k for k in keys if k not in block]
        if missing:
            fails.append(f"D: {where} detection_scope lacks {missing}")
        if block.get("n_origin_switched", 0) != 0:
            fails.append(f"D: {where} n_origin_switched {block['n_origin_switched']} (STOP)")
    scope = (new_ev.get("summary") or {}).get("detection_scope") or {}
    want_scope = row.get("new_scope") or {}
    for k in ("n_out_of_frame", "n_origin_restored"):
        if scope.get(k) != want_scope.get(k):
            fails.append(f"D: {k} {scope.get(k)} expected {want_scope.get(k)}")
    rec["scope"] = {k: scope.get(k) for k in keys}

    # E. feature counts unchanged
    if dc.committed_counts(new_ev) != dc.committed_counts(old_ev):
        fails.append(f"E: n_detections {dc.committed_counts(new_ev)} vs committed "
                     f"{dc.committed_counts(old_ev)}")

    # F. recipe
    new_cli = dict((new_ev.get("_metadata") or {}).get("cli_args") or {})
    old_cli = dict((old_ev.get("_metadata") or {}).get("cli_args") or {})
    diffs = []
    for k in sorted(set(new_cli) | set(old_cli)):
        if new_cli.get(k) == old_cli.get(k):
            continue
        if k == "require_clean_inputs" and new_cli.get(k) and cell.get("add_require_clean"):
            continue
        if k not in old_cli and DEFAULT_ADDED_CLI_KEYS.get(k) == new_cli.get(k):
            continue
        diffs.append(f"{k}: {old_cli.get(k)!r} -> {new_cli.get(k)!r}")
    if diffs:
        fails.append(f"F: recipe differs: {diffs}")
    meta = new_ev.get("_metadata") or {}
    rec["script_git_commit"] = meta.get("script_git_commit")
    rec["script_git_status"] = meta.get("script_git_status")

    # deltas for the report
    off = row.get("blast_off") or {}
    cpb = dc.per_buffer_committed(old_ev)
    rec["deltas"] = {
        b: {"off": (off.get("per_buffer") or {}).get(b, {}).get("f1"),
            "new": (got.get("per_buffer") or {}).get(b, {}).get("f1"),
            "committed_4dp": (cpb.get(b) or {}).get("f1"),
            "regenerated_4dp": (fpb.get(b) or {}).get("f1")}
        for b in ("20", "50")}
    rec["mcc"] = {"off": off.get("mcc"), "new": got.get("mcc"),
                  "committed": dc.committed_mcc(old_ev), "regenerated": fmcc}
    rec["wall_seconds"] = side.get("wall_seconds")
    return rec


def main() -> int:
    """Gate every listed cell and summarise."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rescore-b", type=Path, required=True)
    ap.add_argument("--cells", type=Path, required=True)
    ap.add_argument("--sidecars", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    rows = {r["eval"]: r for r in dc.load_jsonl(args.rescore_b.expanduser())}
    cells = json.loads(args.cells.read_text())
    recs = []
    for cell in cells:
        side_path = args.sidecars / f"{slug(cell['eval'])}.json"
        side = json.loads(side_path.read_text()) if side_path.is_file() else {"rc": None}
        recs.append(gate_one(repo, cell, side, rows[cell["eval"]]))
    summary = {
        "n_cells": len(recs),
        "n_pass": sum(not r["fails"] for r in recs),
        "n_fail": sum(bool(r["fails"]) for r in recs),
        "by_group": {g: {"n": sum(r["group"] == g for r in recs),
                         "pass": sum(r["group"] == g and not r["fails"] for r in recs)}
                     for g in sorted({r["group"] for r in recs})},
        "values_compared": sum(r.get("A_values_compared", 0) for r in recs),
        "worst_A": max((r.get("A_worst", 0.0) for r in recs), default=0.0),
        "ungated_buffer_cells": sum(bool(r.get("ungated_buffers")) for r in recs),
        "B_kinds": dict(Counter(r.get("B") for r in recs)),
        "script_git_commit": dict(Counter(r.get("script_git_commit") for r in recs)),
        "script_git_status": dict(Counter(r.get("script_git_status") for r in recs)),
        "fail_kinds": dict(Counter(f.split(":")[0] for r in recs for f in r["fails"])),
        "failures": [{"eval": r["eval"], "fails": r["fails"][:5]} for r in recs if r["fails"]],
    }
    args.out.write_text(json.dumps({"summary": summary, "cells": recs}, indent=1,
                                   default=str) + "\n")
    print(json.dumps(summary, indent=1, default=str)[:5000])
    return 0 if not summary["n_fail"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
