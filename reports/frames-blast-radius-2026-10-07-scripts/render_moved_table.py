"""Render the moved-cell table of the blast-radius report from ``moved_grouped.csv``.

Frames blast-radius measurement, Session 163 (2026-10-07). Reads
``out/summary/moved_grouped.csv`` and replaces the line ``<!-- MOVED_TABLE -->`` in the
report with a Markdown table, so no number in that table is transcribed by hand.

Usage::

    python render_moved_table.py --csv out/summary/moved_grouped.csv \
        --report ../frames-blast-radius-2026-10-07.md
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

MARKER = "<!-- MOVED_TABLE -->"
ORDER = (
    "3.7 GS K-ladder rungs",
    "null-exemplar reduced-frame re-scores",
    "512 px cells scored on the 384 px Era-2 frame",
    "GS grid-common K = 1 gap-fill",
    "55-map stride pairing twins",
    "55-map stride K = 1 gap-fill",
    "archived copies",
)


def fmt(value: str, signed: bool = False) -> str:
    """Four-decimal rendering; blank for a missing value."""
    if value in ("", None):
        return "—"
    v = float(value)
    return f"{v:+.4f}" if signed else f"{v:.4f}"


def mcc(row: dict[str, str]) -> str:
    """MCC OFF / ON, with a refused value shown as 'refused'."""
    off = fmt(row["off_mcc"]) if row["off_mcc"] else "refused"
    on = fmt(row["on_mcc"]) if row["on_mcc"] else "refused"
    if row["committed_mcc"] in ("", "None") and not row["off_mcc"] and not row["on_mcc"]:
        return "—"
    return f"{off} / {on}"


def main() -> int:
    """Build the table and splice it into the report."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    rows = list(csv.DictReader(args.csv.open()))
    rows.sort(key=lambda r: (ORDER.index(r["group"]), r["eval"]))
    lines = [
        "| # | Group | Cell (evaluation directory) | Register | Detections | Out of frame "
        "| F1@20 OFF → ON | ΔP@20 | ΔR@20 | ΔF1@50 | MCC OFF / ON |",
        "|---:|---|---|---|---:|---:|---|---:|---:|---:|---|",
    ]
    for i, r in enumerate(rows, 1):
        cell = r["eval"].rsplit("/", 2)[-2]
        lines.append(
            f"| {i} | {r['group']} | `{cell}` | {r['register_status']} | "
            f"{r['n_detections'].replace(';', ' + ')} | {r['n_out_of_frame']} | "
            f"{fmt(r['off_f1_20'])} → {fmt(r['on_f1_20'])} | {fmt(r['d_p_20'], True)} | "
            f"{fmt(r['d_r_20'], True)} | {fmt(r['d_f1_50'], True)} | {mcc(r)} |"
        )
    text = args.report.read_text()
    if MARKER not in text:
        raise SystemExit(f"marker {MARKER!r} not found in {args.report}")
    args.report.write_text(text.replace(MARKER, "\n".join(lines)))
    print(f"spliced {len(rows)} rows into {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
