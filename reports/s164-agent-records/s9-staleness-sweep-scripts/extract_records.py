#!/usr/bin/env python3
"""Extract the S9 staleness sweep's committed records from its run outputs (S164).

Purpose
-------
Joins the inventory (``inventory.py``) with every comparison
(``compare.py`` on the full and points runs, ``engine_replay.py`` on the
adapter cells) and writes the small, reviewable records committed beside
the report:

* ``coverage.csv``: one row per live evaluation: group, lineage, whether
  it was replayed (full, points, engine), and each result;
* ``movers.json``: every evaluation whose points move in any replay, with
  committed and today's values, the D50 scope counts, both runs'
  agreement, and lineage (signed analyses, claim rows);
* ``counts.json``: results by group and replay kind.

Inputs are the JSON files under ``--root`` named on the command line; the
script computes nothing new.

Usage::

    python extract_records.py --root <scratch root> --out <records dir> \\
        --full runs/s1-A runs/s2-A --full-b runs/s1-B runs/s2-B \\
        --points runs/pts-A --points-b runs/pts-B --engine runs/eng-A --engine-b runs/eng-B

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_compare(root: Path, run: str, points: bool) -> dict[str, dict[str, Any]]:
    """Load ``records/compare-<run>.json`` written by ``compare.py`` for one run."""
    tag = Path(run).name
    path = root / "records" / f"compare-{tag}.json"
    doc = json.loads(path.read_text())
    return {c["eval"]: c for c in doc["cells"]}


def merge(runs: list[dict[str, dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """Merge several runs' comparison records into one map (later runs add cells)."""
    out: dict[str, dict[str, Any]] = {}
    for r in runs:
        out.update(r)
    return out


def main() -> int:
    """Write coverage.csv, movers.json and counts.json."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--full", nargs="+", default=[])
    ap.add_argument("--full-b", nargs="+", default=[])
    ap.add_argument("--points", nargs="+", default=[])
    ap.add_argument("--points-b", nargs="+", default=[])
    ap.add_argument("--engine", default=None)
    ap.add_argument("--engine-b", default=None)
    args = ap.parse_args()
    root = args.root.expanduser().resolve()
    inv = json.loads((root / "inventory/inventory.json").read_text())
    cells = {c["eval"]: c for c in inv["cells"]}
    full = merge([load_compare(root, r, False) for r in args.full])
    full_b = merge([load_compare(root, r, False) for r in args.full_b])
    pts = merge([load_compare(root, r, True) for r in args.points])
    pts_b = merge([load_compare(root, r, True) for r in args.points_b])
    eng: dict[str, dict[str, Any]] = {}
    eng_b: dict[str, dict[str, Any]] = {}
    if args.engine:
        eng = {c["eval"]: c for c in json.loads(
            (root / args.engine / "engine.json").read_text())["cells"]}
    if args.engine_b and (root / args.engine_b / "engine.json").is_file():
        eng_b = {c["eval"]: c for c in json.loads(
            (root / args.engine_b / "engine.json").read_text())["cells"]}

    def eng_result(rec: dict[str, Any] | None) -> str:
        """``identical`` / ``points`` / ``replay-failed`` / '' for an engine record."""
        if not rec:
            return ""
        if rec.get("rc") != 0:
            return "replay-failed"
        return "identical" if rec.get("identical_points") else "points"

    rows: list[dict[str, Any]] = []
    movers: list[dict[str, Any]] = []
    counts: Counter = Counter()
    for rel, c in sorted(cells.items()):
        f, fb = full.get(rel), full_b.get(rel)
        p, pb = pts.get(rel), pts_b.get(rel)
        e, eb = eng.get(rel), eng_b.get(rel)
        lineage = bool(c["signed_analyses"] or c["claim_rows"])
        row = {
            "eval": rel, "group": c["group"], "d50_scored": c["d50_scored"],
            "lineage": lineage, "signed_analyses": ";".join(c["signed_analyses"]),
            "claim_rows": ";".join(sorted(c["claim_rows"])),
            "last_commit": c["last_commit"], "last_commit_date": c["last_commit_date"][:10],
            "full_A": (f or {}).get("result", ""), "full_B": (fb or {}).get("result", ""),
            "points_A": (p or {}).get("result", ""), "points_B": (pb or {}).get("result", ""),
            "engine_A": eng_result(e), "engine_B": eng_result(eb),
        }
        rows.append(row)
        scope = "pre-D50" if not c["d50_scored"] else "D50-scored"
        for kind, val in (("full", row["full_A"]), ("points", row["points_A"]),
                          ("engine", row["engine_A"])):
            if val:
                counts[f"{kind}|{scope}|{c['group']}|lineage={lineage}|{val}"] += 1
        if not (f or p or e):
            counts[f"not-replayed|{scope}|{c['group']}|lineage={lineage}"] += 1
        moved = [x for x in (f, p) if x and x.get("result") == "points"]
        if moved or (e and eng_result(e) == "points"):
            src = moved[0] if moved else None
            movers.append({
                "eval": rel, "group": c["group"], "d50_scored": c["d50_scored"],
                "last_commit": c["last_commit"], "last_commit_date": c["last_commit_date"],
                "script_git_commit": c["script_git_commit"],
                "generated_at_utc": c["generated_at_utc"],
                "census_disposition": c["census_disposition"],
                "conditions": c["conditions"], "analyses": c["analyses"],
                "analyses_by_dir": c["analyses_by_dir"],
                "signed_analyses": c["signed_analyses"], "claim_rows": c["claim_rows"],
                "full_A": row["full_A"], "full_B": row["full_B"],
                "points_A": row["points_A"], "points_B": row["points_B"],
                "engine_A": row["engine_A"], "engine_B": row["engine_B"],
                "at20": (src or {}).get("at20"), "at50": (src or {}).get("at50"),
                "unrounded20": (src or {}).get("unrounded20"),
                "mcc_point": (src or {}).get("mcc_point"),
                "n_det": (src or {}).get("n_det"),
                "max_abs_df1_any_buffer": (src or {}).get("max_abs_df1_any_buffer"),
                "scope": (src or {}).get("scope"),
                "engine_diffs": (e or {}).get("diffs"),
            })
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "coverage.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (args.out / "movers.json").write_text(json.dumps(movers, indent=1, sort_keys=True) + "\n")
    (args.out / "counts.json").write_text(json.dumps(dict(sorted(counts.items())), indent=1)
                                          + "\n")
    print(f"{len(rows)} cells; {len(movers)} movers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
