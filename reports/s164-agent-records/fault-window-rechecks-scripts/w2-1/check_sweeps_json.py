#!/usr/bin/env python3
"""
W2-1: validate a sweeps.json version against the sweep CSV rows it summarises.

Every block in a rung entry of ``sweeps.json`` (``carried``, ``f1_oracle``,
``mcc_oracle`` / ``mcc_argmax_at_carried_k``, ``mcc_argmax_unconstrained``)
is one row of that rung's ``sweep_<rung>.csv``, chosen by a documented rule
(``scripts/gemini37_image_55map_r2.py``: Python ``max`` over rows sorted by
``(prob_t, min_votes)``, so the lowest point wins a tie). Once the CSVs are
verified by regeneration, this check verifies the JSON's every leaf without
recomputation: each block must equal, leaf for leaf, the row its rule picks.

Rules applied per key:
  carried                   row at carried_point
  f1_oracle                 argmax micro_f1_50 over all rows
  mcc_oracle (pre-09-20)    argmax tile_mcc over all rows        [--mcc-rule free]
  mcc_oracle (09-20 on)     argmax tile_mcc at carried min_votes [--mcc-rule carried]
  mcc_argmax_at_carried_k   argmax tile_mcc at carried min_votes
  mcc_argmax_unconstrained  argmax tile_mcc over all rows
  oracle (inheritance)      argmax micro_f1_50 over all rows

Usage::

    python check_sweeps_json.py --tree <repo> --json <commit>:<path> \
        --csv-commit <commit> --csv-dir <dir> [--mcc-rule free|carried] \
        [--rungs-key rungs] --out result.json

Zero API; read-only.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
import sys
from pathlib import Path


def blob(tree: Path, spec: str) -> str:
    """Return ``git show <spec>`` as text."""
    return subprocess.run(["git", "-C", str(tree), "show", spec], check=True,
                          capture_output=True, text=True).stdout


def rows_for(tree: Path, commit: str, csv_path: str) -> list[dict[str, str]]:
    """The CSV rows, as strings, in file order."""
    return list(csv.DictReader(io.StringIO(blob(tree, f"{commit}:{csv_path}"))))


def typed_equal(block: dict, row: dict[str, str]) -> list[str]:
    """Leaf differences between a JSON block and a CSV row (typed by the JSON)."""
    diffs = []
    if set(block) != set(row):
        diffs.append(f"key sets differ: json-only {sorted(set(block) - set(row))}, "
                     f"csv-only {sorted(set(row) - set(block))}")
    for k, v in block.items():
        if k not in row:
            continue
        if v is None:
            ok = row[k] == ""
        elif isinstance(v, bool):
            ok = str(v) == row[k]
        elif isinstance(v, int):
            ok = int(row[k]) == v
        elif isinstance(v, float):
            ok = float(row[k]) == v
        else:
            ok = str(v) == row[k]
        if not ok:
            diffs.append(f"{k}: json {v!r} csv {row[k]!r}")
    return diffs


def argmax(rows, key, votes=None):
    """First maximum over rows sorted by (prob_t, min_votes), as the driver does."""
    pool = [r for r in rows if votes is None or int(r["min_votes"]) == votes]
    pool = sorted(pool, key=lambda r: (float(r["prob_t"]), int(r["min_votes"])))
    return max(pool, key=lambda r: float(r[key]))


def main() -> int:
    """Check every rung entry; write and print the outcome."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tree", required=True, type=Path)
    ap.add_argument("--json", required=True, help="<commit>:<path> of the sweeps record")
    ap.add_argument("--csv-commit", required=True)
    ap.add_argument("--csv-dir", required=True)
    ap.add_argument("--csv-suffix", default="")
    ap.add_argument("--mcc-rule", choices=("free", "carried"), default="free")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    doc = json.loads(blob(args.tree, args.json))
    rungs = doc.get("rungs") or {
        f"{arm}-K{k}": rec for arm, by_k in doc.get("arms", {}).items()
        for k, rec in by_k.items()}
    report = {"json": args.json, "csv_commit": args.csv_commit,
              "mcc_rule": args.mcc_rule, "rungs": {}}
    all_ok = True
    for label, info in rungs.items():
        csv_label = info.get("carried", {}).get("rung", label) if isinstance(
            info.get("carried"), dict) else label
        rows = rows_for(args.tree, args.csv_commit,
                        f"{args.csv_dir}/sweep_{csv_label}{args.csv_suffix}.csv")
        cp, cv = info["carried_point"]
        checks = {}
        checks["n_sweep_points"] = ([] if info["n_sweep_points"] == len(rows)
                                    else [f"{info['n_sweep_points']} != {len(rows)}"])
        carried_row = next(r for r in rows if abs(float(r["prob_t"]) - cp) < 1e-9
                           and int(r["min_votes"]) == cv)
        checks["carried"] = typed_equal(info["carried"], carried_row)
        for key in ("f1_oracle", "oracle"):
            if key in info:
                checks[key] = typed_equal(info[key], argmax(rows, "micro_f1_50"))
        if "mcc_oracle" in info:
            want = argmax(rows, "tile_mcc", cv if args.mcc_rule == "carried" else None)
            checks["mcc_oracle"] = typed_equal(info["mcc_oracle"], want)
        if "mcc_argmax_at_carried_k" in info:
            checks["mcc_argmax_at_carried_k"] = typed_equal(
                info["mcc_argmax_at_carried_k"], argmax(rows, "tile_mcc", cv))
        if "mcc_argmax_unconstrained" in info:
            checks["mcc_argmax_unconstrained"] = typed_equal(
                info["mcc_argmax_unconstrained"], argmax(rows, "tile_mcc"))
        unchecked = sorted(set(info) - set(checks) - {"carried_point"})
        ok = all(not v for v in checks.values())
        all_ok &= ok
        report["rungs"][label] = {"ok": ok, "n_rows": len(rows), "checks": checks,
                                  "keys_not_checked": unchecked}
        print(f"{'OK ' if ok else 'BAD'} {label}: rows {len(rows)}, checked "
              f"{sorted(checks)}, not checked {unchecked}")
    report["all_ok"] = all_ok
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
