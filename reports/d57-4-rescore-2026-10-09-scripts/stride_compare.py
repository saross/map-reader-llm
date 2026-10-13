"""Compare the 55-map stride sweeps and ladders: OLD with committed, NEW with committed.

D57 (4) re-score, 2026-10-09 (Session 163); plan § 3.2 and § 7 row 2 (d).
Read-only; writes ``--out``.

``scripts/stride55_sweep_oracle.py`` and ``scripts/stride55_ladder.py`` were
run in the OLD tree (``git archive b3c52591d``; each writes into that tree's
own copy of ``results/stride55-2026-08-27``) and in the NEW worktree (in
place). This compares, per cell:

* OLD with committed (``HEAD``): files byte-identical, which is the plan's
  "OLD must reproduce the committed artefact";
* NEW with committed: rows whose ``corrected_f1`` moves by more than 1e-9 and
  by at least 0.001, their ``prob_t`` values, rows whose counts change, and the
  ``sweep_oracle.json`` / ``ladder.json`` keys that change;
* NEW with the 2026-10-08 expected rows (``stride55_new.json``): every row's
  ``corrected_f1`` to 1e-9 and its TP, FP and FN exactly.

Usage (on sapphire)::

    .venv/bin/python stride_compare.py --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --old-tree ~/scratch/d57-4-rescore-2026-10-09/old \\
        --out ~/scratch/d57-4-rescore-2026-10-09/out/stride_compare.json
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d57_common as dc  # noqa: E402

BASE = "results/stride55-2026-08-27"
CELLS = ("g384_ov128_55map", "g384_ov192_55map")
EXPECTED = "reports/scorer-frames-d50-d51-2026-10-08-scripts/out/stride55_new.json"


def rows_of(text: str, keys: tuple[str, ...]) -> dict[tuple, dict[str, str]]:
    """Index a sweep CSV's rows by ``keys``."""
    return {tuple(r[k] for k in keys): r for r in csv.DictReader(io.StringIO(text))}


def compare_csv(old_text: str, new_text: str, keys: tuple[str, ...]) -> dict[str, Any]:
    """Row-level comparison of two sweep CSVs."""
    a, b = rows_of(old_text, keys), rows_of(new_text, keys)
    moved, moved_big, counts = [], [], []
    for k in sorted(set(a) & set(b)):
        d = abs(float(b[k]["corrected_f1"]) - float(a[k]["corrected_f1"]))
        if d > dc.EPS:
            moved.append({"key": k, "committed": float(a[k]["corrected_f1"]),
                          "new": float(b[k]["corrected_f1"]), "delta": d})
        if d >= 0.001:
            moved_big.append(k)
        if any(a[k][c] != b[k][c] for c in ("n_detections", "tp", "fp", "fn")):
            counts.append(k)
    moved_keys = {m["key"] for m in moved} | set(counts)
    text_differs = [k for k in sorted(set(a) & set(b)) if a[k] != b[k]]
    return {"rows_committed": len(a), "rows_new": len(b),
            "keys_only_committed": len(set(a) - set(b)), "keys_only_new": len(set(b) - set(a)),
            "rows_text_differing": len(text_differs),
            "unmoved_rows_text_differing": len([k for k in text_differs
                                                if k not in moved_keys]),
            "moved_gt_1e-9": len(moved), "moved_ge_0.001": len(moved_big),
            "moved_prob_t": sorted({m["key"][keys.index("prob_t")] for m in moved}),
            "rows_with_count_change": len(counts), "moved": moved,
            "byte_identical": old_text == new_text}


def json_diff(a: Any, b: Any, path: str = "") -> list[str]:
    """Paths whose values differ between two JSON documents."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += json_diff(a.get(k), b.get(k), f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += json_diff(x, y, f"{path}[{i}]")
        return out
    if isinstance(a, float) and isinstance(b, float) and abs(a - b) <= dc.EPS:
        return []
    return [] if a == b else [f"{path}: {str(a)[:50]} -> {str(b)[:50]}"]


def main() -> int:
    """Compare and write the record."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--old-tree", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    old_tree = args.old_tree.expanduser().resolve()
    expected = json.loads((repo / EXPECTED).read_text())["rows"]
    report: dict[str, Any] = {"cells": {}}
    for cell in CELLS:
        rec: dict[str, Any] = {}
        for name, keys in (("sweep_50m.csv", ("cell", "prob_t", "min_votes")),
                           ("ladder_sweep_50m.csv", ("cell", "N", "prob_t", "min_votes"))):
            rel = f"{BASE}/{cell}/{name}"
            # Raw bytes, decoded without newline translation: the sweep writers
            # use csv's CRLF terminator, which ``read_text`` would rewrite.
            committed = dc.git_show_bytes(repo, "HEAD", rel).decode()
            old = (old_tree / rel).read_bytes().decode()
            new = (repo / rel).read_bytes().decode()
            rec[name] = {"old_vs_committed": compare_csv(committed, old, keys),
                         "new_vs_committed": compare_csv(committed, new, keys)}
        new_rows = rows_of((repo / f"{BASE}/{cell}/sweep_50m.csv").read_bytes().decode(),
                           ("cell", "prob_t", "min_votes"))
        misses = []
        for e in (x for x in expected if x["cell"] == cell):
            key = (cell, str(e["prob_t"]), str(e["min_votes"]))
            got = new_rows.get(key)
            if got is None:
                misses.append(f"{key}: absent")
                continue
            if abs(float(got["corrected_f1"]) - e["corrected_f1"]) > dc.EPS or any(
                    int(got[c]) != e[c] for c in ("tp", "fp", "fn")):
                misses.append(f"{key}: new {got['corrected_f1']} expected {e['corrected_f1']}")
        rec["new_vs_expected"] = {"rows_compared": sum(x["cell"] == cell for x in expected),
                                  "misses": misses}
        report["cells"][cell] = rec
    for name in ("sweep_oracle.json", "ladder.json"):
        rel = f"{BASE}/{name}"
        committed = json.loads(dc.git_show_bytes(repo, "HEAD", rel))
        old_text = (old_tree / rel).read_bytes().decode()
        report[name] = {
            "old_byte_identical": old_text == dc.git_show_bytes(repo, "HEAD", rel).decode(),
            "old_vs_committed": json_diff(committed, json.loads(old_text)),
            "new_vs_committed": json_diff(committed, json.loads((repo / rel).read_text()))}
    args.out.write_text(json.dumps(report, indent=1, default=str) + "\n")
    brief = {c: {n: {"old_identical": r[n]["old_vs_committed"]["byte_identical"],
                     "new_moved_gt_1e-9": r[n]["new_vs_committed"]["moved_gt_1e-9"],
                     "new_moved_ge_0.001": r[n]["new_vs_committed"]["moved_ge_0.001"],
                     "prob_t": r[n]["new_vs_committed"]["moved_prob_t"],
                     "new_text_rows": r[n]["new_vs_committed"]["rows_text_differing"],
                     "unmoved_text_rows": r[n]["new_vs_committed"]
                     ["unmoved_rows_text_differing"],
                     "count_changes": r[n]["new_vs_committed"]["rows_with_count_change"]}
                 for n in ("sweep_50m.csv", "ladder_sweep_50m.csv")}
             | {"expected_misses": len(r["new_vs_expected"]["misses"])}
             for c, r in report["cells"].items()}
    brief["json"] = {n: {"old_identical": report[n]["old_byte_identical"],
                         "old_diffs": len(report[n]["old_vs_committed"]),
                         "new_diffs": report[n]["new_vs_committed"][:12]}
                     for n in ("sweep_oracle.json", "ladder.json")}
    print(json.dumps(brief, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
