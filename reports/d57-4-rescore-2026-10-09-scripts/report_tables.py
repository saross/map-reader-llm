"""Summarise the Phase 2 gate results as the S2 deltas tables (Markdown to stdout).

D57 (4) re-score, 2026-10-09 (Session 163). Read-only: reads ``gate.json``
(``gate_check.py``) and the tracked ``moved_new.csv`` (for condition ids).

Prints, per plan § 3.1 group and per directory family (the plan's
expected-moves table), the cell count, gate passes, and the NEW − OFF ranges of
F1 at 20 m and 50 m (full precision: OFF from ``rescore_b.jsonl``, NEW from the
replay); then every registered cell with its condition id(s) and OFF → NEW at
20 m and 50 m. Also writes the same records as JSON beside ``--gate``.

Usage::

    .venv/bin/python report_tables.py --repo ~/scratch/d57-4-rescore-2026-10-09/new \\
        --gate ~/scratch/d57-4-rescore-2026-10-09/out/gate.json
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

MOVED_CSV = "reports/scorer-frames-d50-d51-2026-10-08-scripts/out/summary/moved_new.csv"

#: Directory families of the plan's expected-moves table (§ 3.1), first match wins.
FAMILIES: tuple[tuple[str, str], ...] = (
    ("results/rescore-2026-06-05/", "results/rescore-2026-06-05"),
    ("results/phase3a-", "results/phase3a-{text,image}-matrix"),
    ("results/uplift-supplement/", "results/uplift-supplement"),
    ("results/null-exemplar-sensitivity-2026-09-13/cells/", "null-exemplar cells"),
    ("results/h13-overlap-2026-08-18/", "results/h13-overlap-2026-08-18"),
    ("results/pairwise/tile-size-30m/", "results/pairwise/tile-size-30m"),
    ("outputs/h11/consensus-384-UNINTENDED-T1.0/", "outputs/h11/consensus-384-UNINTENDED-T1.0"),
)


def family(rel: str) -> str:
    """The expected-moves family a cell belongs to ('others' when none)."""
    return next((name for prefix, name in FAMILIES if rel.startswith(prefix)), "others")


def delta(rec: dict[str, Any], buf: str) -> float | None:
    """NEW − OFF at one buffer, full precision, or None when either is absent."""
    d = (rec.get("deltas") or {}).get(buf) or {}
    if d.get("new") is None or d.get("off") is None:
        return None
    return d["new"] - d["off"]


def rng(values: list[float]) -> str:
    """'+a to +b' over the defined values, or '—'."""
    vals = [v for v in values if v is not None]
    if not vals:
        return "—"
    return f"{min(vals):+.4f} to {max(vals):+.4f}"


def table(recs: list[dict[str, Any]], key: Any, title: str) -> list[str]:
    """One summary table grouped by ``key``."""
    lines = [f"### {title}", "", "| Group | Cells (registered) | Gate pass | ΔF1@20 | ΔF1@50 |",
             "|---|---:|---:|---|---|"]
    groups: dict[str, list[dict[str, Any]]] = {}
    for r in recs:
        groups.setdefault(key(r), []).append(r)
    for g in sorted(groups):
        rs = groups[g]
        lines.append(f"| {g} | {len(rs)} ({sum(bool(r['registered']) for r in rs)}) | "
                     f"{sum(not r['fails'] for r in rs)} | {rng([delta(r, '20') for r in rs])} | "
                     f"{rng([delta(r, '50') for r in rs])} |")
    return lines + [""]


def main() -> int:
    """Print the tables and write their JSON."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--gate", type=Path, required=True)
    args = ap.parse_args()
    recs = json.loads(args.gate.read_text())["cells"]
    conds = {r["eval"]: r["conditions"] for r in csv.DictReader(
        (args.repo.expanduser() / MOVED_CSV).open())}
    out = table(recs, lambda r: r["group"], "By plan § 3.1 group")
    out += table(recs, lambda r: family(r["eval"]), "By directory family (plan § 3.1 table)")
    out += ["### Registered cells", "",
            "| Condition id(s) | F1@20 OFF → NEW | F1@50 OFF → NEW | MCC OFF → NEW | Gate |",
            "|---|---|---|---|---|"]
    reg = sorted((r for r in recs if r["registered"]), key=lambda r: conds.get(r["eval"], ""))
    rows = []
    for r in reg:
        d20, d50 = r["deltas"]["20"], r["deltas"]["50"]

        def fmt(d: dict[str, Any]) -> str:
            """Render one buffer's OFF → NEW F1 and its delta, or "not scored"."""
            if d.get("off") is None:
                return "not scored"
            return f"{d['off']:.4f} → {d['new']:.4f} ({d['new'] - d['off']:+.4f})"
        m = r.get("mcc") or {}
        mcc = ("—" if m.get("off") is None or m.get("new") is None
               else f"{m['off']:.4f} → {m['new']:.4f}")
        out.append(f"| {conds.get(r['eval'], '')} | {fmt(d20)} | {fmt(d50)} | {mcc} | "
                   f"{'pass' if not r['fails'] else 'FAIL'} |")
        rows.append({"eval": r["eval"], "conditions": conds.get(r["eval"], ""),
                     "f1_20": d20, "f1_50": d50, "mcc": m, "pass": not r["fails"]})
    print("\n".join(out))
    args.gate.with_name("registered_deltas.json").write_text(json.dumps(rows, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
