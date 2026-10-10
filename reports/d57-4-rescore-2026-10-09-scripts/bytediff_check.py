"""Byte-diff check (a): cells that should not move, replayed into scratch under NEW.

D57 (4) re-score, 2026-10-09 (Session 163); plan § 7 row 2 (a). Every cell
where the D50 scope restored a detection but no metric moved, plus 50 random
unchanged cells, is replayed into scratch with its recipe exactly as recorded
(``run_replays.py`` with ``bytediff_cells.json``). This compares each replay
with its committed evaluation. Read-only; writes ``--out``.

Pass rule per cell: the metric blocks (``summary`` and every ``per_run``
entry) are identical to the committed ones apart from ``detection_scope``.
Differences are classified as:

* ``value`` — a key both carry, with different values (a FAIL);
* ``removed`` — a key the committed block has and the replay lacks (a FAIL);
* ``added`` — a key only the replay carries (reported: a newer scorer's
  schema addition, not a metric change).

The ``_metadata`` differences and the CSV and Markdown byte-identity are
reported, not gated (the plan expects ``generated_at_utc`` and
``script_git_commit`` to differ; other metadata keys are listed).
``detection_scope`` must carry every count key with ``n_origin_switched == 0``,
and ``n_origin_restored`` must equal the expected row's.

Usage (on sapphire)::

    .venv/bin/python bytediff_check.py --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --rescore-b ~/scratch/source-tile-gap-2026-10-08/out/rescore_b.jsonl \\
        --cells ~/scratch/d57-4-rescore-2026-10-09/out/bytediff_cells.json \\
        --sidecars ~/scratch/d57-4-rescore-2026-10-09/out/bytediff-sidecars \\
        --out ~/scratch/d57-4-rescore-2026-10-09/out/bytediff.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d57_common as dc  # noqa: E402
from run_replays import slug  # noqa: E402

#: Keys excluded from the metric-block comparison (plan § 7 row 2 (a)).
EXCLUDED = {"detection_scope"}


def walk(new: Any, old: Any, path: str, out: dict[str, list[str]]) -> None:
    """Recursively classify differences between a replayed and a committed block."""
    if isinstance(new, dict) and isinstance(old, dict):
        for k in sorted(set(new) | set(old)):
            if k in EXCLUDED:
                continue
            p = f"{path}/{k}"
            if k not in old:
                out["added"].append(p)
            elif k not in new:
                out["removed"].append(p)
            else:
                walk(new[k], old[k], p, out)
    elif isinstance(new, list) and isinstance(old, list) and len(new) == len(old):
        for i, (a, b) in enumerate(zip(new, old)):
            walk(a, b, f"{path}[{i}]", out)
    elif new != old:
        out["value"].append(f"{path}: {str(old)[:60]} -> {str(new)[:60]}")


def strip_generic(path: str) -> str:
    """Collapse list indices so added-key paths can be tallied."""
    out, depth = [], 0
    for ch in path:
        if ch == "[":
            depth += 1
            out.append("[]")
        elif ch == "]":
            depth -= 1
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def check_one(repo: Path, cell: dict[str, Any], side: dict[str, Any],
              row: dict[str, Any]) -> dict[str, Any]:
    """Compare one scratch replay with its committed evaluation."""
    rel = cell["eval"]
    rec: dict[str, Any] = {"eval": rel, "kind": cell["kind"], "fails": []}
    if side.get("rc") != 0:
        rec["fails"].append(f"replay rc={side.get('rc')} {side.get('error', '')}")
        return rec
    out_dir = Path(cell["output_dir"])
    new = json.loads((out_dir / "evaluation.json").read_text())
    old = dc.committed_eval(repo, rel) or {}
    diffs: dict[str, list[str]] = {"added": [], "removed": [], "value": []}
    walk(new.get("summary"), old.get("summary"), "summary", diffs)
    if "per_run" in new or "per_run" in old:
        walk(new.get("per_run"), old.get("per_run"), "per_run", diffs)
    rec["added"] = sorted({strip_generic(p) for p in diffs["added"]})
    rec["removed"], rec["value"] = diffs["removed"], diffs["value"]
    if diffs["removed"] or diffs["value"]:
        rec["fails"].append(f"metric blocks differ: {len(diffs['value'])} values, "
                            f"{len(diffs['removed'])} removed")
    nm, om = new.get("_metadata") or {}, old.get("_metadata") or {}
    rec["metadata_keys_differing"] = sorted(k for k in set(nm) | set(om)
                                            if nm.get(k) != om.get(k))
    ncli, ocli = nm.get("cli_args") or {}, om.get("cli_args") or {}
    rec["cli_keys_differing"] = sorted(k for k in set(ncli) | set(ocli)
                                       if ncli.get(k) != ocli.get(k))
    for ext in ("csv", "md"):
        a = (out_dir / f"evaluation.{ext}").read_bytes()
        b = dc.git_show_bytes(repo, "HEAD", str(Path(rel).with_name(f"evaluation.{ext}")))
        rec[f"{ext}_identical"] = a == b
    scope = (new.get("summary") or {}).get("detection_scope")
    if scope is None:
        rec["fails"].append("no detection_scope")
    else:
        missing = [k for k in dc.SCOPE_COUNT_KEYS if k not in scope]
        if missing:
            rec["fails"].append(f"detection_scope lacks {missing}")
        if scope.get("n_origin_switched", 0) != 0:
            rec["fails"].append("n_origin_switched != 0 (STOP)")
        want = (row.get("new_scope") or {}).get("n_origin_restored")
        if scope.get("n_origin_restored") != want:
            rec["fails"].append(f"n_origin_restored {scope.get('n_origin_restored')} "
                                f"expected {want}")
        rec["n_origin_restored"] = scope.get("n_origin_restored")
    return rec


def main() -> int:
    """Check every listed scratch replay and summarise."""
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
    recs = []
    for cell in json.loads(args.cells.read_text()):
        p = args.sidecars / f"{slug(cell['eval'])}.json"
        side = json.loads(p.read_text()) if p.is_file() else {"rc": None}
        recs.append(check_one(repo, cell, side, rows[cell["eval"]]))
    summary = {
        "n": len(recs),
        "by_kind": {k: {"n": sum(r["kind"] == k for r in recs),
                        "pass": sum(r["kind"] == k and not r["fails"] for r in recs)}
                    for k in sorted({r["kind"] for r in recs})},
        "added_key_tally": dict(Counter(a for r in recs for a in r.get("added", []))),
        "metadata_keys_differing": dict(Counter(
            k for r in recs for k in r.get("metadata_keys_differing", []))),
        "cli_keys_differing": dict(Counter(
            k for r in recs for k in r.get("cli_keys_differing", []))),
        "csv_identical": sum(bool(r.get("csv_identical")) for r in recs),
        "md_identical": sum(bool(r.get("md_identical")) for r in recs),
        "failures": [{"eval": r["eval"], "fails": r["fails"], "value": r.get("value", [])[:4]}
                     for r in recs if r["fails"]],
    }
    args.out.write_text(json.dumps({"summary": summary, "cells": recs}, indent=1,
                                   default=str) + "\n")
    print(json.dumps(summary, indent=1, default=str)[:6000])
    return 0 if not summary["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
