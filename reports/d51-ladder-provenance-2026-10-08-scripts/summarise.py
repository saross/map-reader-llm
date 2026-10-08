"""Render the report's tables from the JSON outputs (no hand transcription).

Reads ``out/gate_survey.json``, ``out/clip_cost.json``,
``out/rebuild_pools.json``, ``out/t07_tilings.json`` and
``out/red_sentinel.json`` and writes ``out/summary.md``: the gate statuses
before and after, the PR #26 survey for comparison, the rebuild verdicts,
the validation and cross-check counts, and Task C's tables.

Usage (any machine; small JSON only)::

    python summarise.py --out-dir out

Created: 2026-10-08 (D57 (2), (3), Session 163 follow-up)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PR26_SURVEY = Path(__file__).resolve().parent.parent / \
    "scorer-frames-d50-d51-2026-10-08-scripts" / "out" / "ladders_new.json"


def f4(value: Any) -> str:
    """Four decimal places, or an em dash for a missing value."""
    return "—" if value is None else f"{value:.4f}"


def signed(value: float | None) -> str:
    """A signed four-decimal difference."""
    return "—" if value is None else f"{value:+.4f}"


def status_cell(row: dict[str, Any]) -> str:
    """Status with the excess area when refused."""
    if row["status"] == "refused":
        return f"refused, {row['max_excess_km2']:.4f} km²"
    return str(row["status"])


def survey_table(gate: dict[str, Any]) -> list[str]:
    """Before → after, with PR #26's committed survey alongside."""
    pr26 = {r["pool"]: r for r in json.loads(PR26_SURVEY.read_text())["phase2_gate_survey"]}
    before = {r["pool"]: r for r in gate["before"]}
    lines = ["| Ladder (proposer pool) | PR #26 survey | Before (this branch, base declarations) "
             "| After | Rung methods after (K = 1 / 3 / 5 / 10) |",
             "|---|---|---|---|---|"]
    for row in gate["after"]:
        methods = " / ".join(p["method"] for p in row["pools"])
        lines.append(f"| `{row['pool']}` | {status_cell(pr26[row['pool']])} | "
                     f"{status_cell(before[row['pool']])} | {status_cell(row)} | {methods} |")
    return lines


def rebuild_table(rebuild: dict[str, Any]) -> list[str]:
    """Per pool: exact under the April merger, the current merger."""
    lines = ["| Ladder | K | Role | April merger (name order) | Current merger "
             "(numeric order) | Recorded provenance agrees |", "|---|---:|---|---|---|---|"]
    for row in rebuild["table"]:
        agree = row["recorded_provenance_agrees"]
        lines.append(f"| `{row['pool']}` | {row['K']} | {row['role']} | "
                     f"{'exact' if row['april'] else 'DIFFERS'} | "
                     f"{'exact' if row['current'] else 'differs'} | "
                     f"{'—' if agree is None else ('yes' if agree else 'NO')} |")
    return lines


def clip_tables(clip: dict[str, Any], point: str) -> list[str]:
    """Task C: one table of all rungs, and one of the gains, at one point."""
    lines = [f"Point: `{point}`.", "",
             "| Ladder | K | Gap mounds found | F1 (i) / (ii) / (iii) | P (i) / (ii) / (iii) "
             "| R (i) / (ii) / (iii) | Tile MCC (i) / (ii) / (iii) | ΔF1 (ii) − (i): "
             "estimate / measured |", "|---|---:|---:|---|---|---|---|---|"]
    gains = ["| Ladder | Gain | (i) unclipped | (ii) clipped | (iii) gap removed |",
             "|---|---|---:|---:|---:|"]
    for lad in clip["ladders"]:
        by_k = {}
        for rung in lad["rungs"]:
            p = rung["points"].get(point)
            if p is None:
                continue
            by_k[rung["K"]] = p
            i, ii, iii = p["unclipped"], p["clipped"], p["gap_removed"]
            lines.append(
                f"| `{lad['pool']}` | {rung['K']} | {i['gap_mounds_found']} of "
                f"{lad['gap_reference_mounds']} | {f4(i['f1'])} / {f4(ii['f1'])} / "
                f"{f4(iii['f1'])} | {f4(i['precision'])} / {f4(ii['precision'])} / "
                f"{f4(iii['precision'])} | {f4(i['recall'])} / {f4(ii['recall'])} / "
                f"{f4(iii['recall'])} | {f4(i['tile_mcc'])} / {f4(ii['tile_mcc'])} / "
                f"{f4(iii['tile_mcc'])} | {signed(p['estimate']['linear_delta_f1'])} / "
                f"{signed(ii['f1'] - i['f1'])} |")
        for hi in (3, 10):
            if 1 in by_k and hi in by_k:
                cells = [signed(by_k[hi][m]["f1"] - by_k[1][m]["f1"])
                         for m in ("unclipped", "clipped", "gap_removed")]
                gains.append(f"| `{lad['pool']}` | K = 1 → K = {hi} | " + " | ".join(cells) + " |")
    return lines + [""] + gains


def gap_table(clip: dict[str, Any]) -> list[str]:
    """Each refused ladder's gap: tiles, area, reference mounds."""
    lines = ["| Ladder | Gate (after) | Common area (km²) | Gap (km²) | Gap tile(s) | "
             "Reference mounds in the gap |", "|---|---|---:|---:|---|---:|"]
    for lad in clip["ladders"]:
        lines.append(f"| `{lad['pool']}` | {lad['gate_status']} | {lad['common_area_km2']:.4f} | "
                     f"{lad['gap_km2']:.4f} | {', '.join(f'`{t}`' for t in lad['gap_tiles'])} | "
                     f"{lad['gap_reference_mounds']} |")
    return lines


def main() -> int:
    """Write out/summary.md."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    d = args.out_dir
    gate = json.loads((d / "gate_survey.json").read_text())
    clip = json.loads((d / "clip_cost.json").read_text())
    rebuild = json.loads((d / "rebuild_pools.json").read_text())
    tilings = json.loads((d / "t07_tilings.json").read_text())
    sentinel = json.loads((d / "red_sentinel.json").read_text())
    april = [r for r in rebuild["rows"] if r["merger"] == "april"]
    current = [r for r in rebuild["rows"] if r["merger"] == "current"]
    lines = [
        "# Summary tables (generated by summarise.py)", "",
        "## Gate survey", "", *survey_table(gate), "",
        f"Validation: {sum(v['reproduces'] for v in gate['validation'])} of "
        f"{len(gate['validation'])} declared-route areas reproduce the recorded-route "
        f"area; independent cross-check: "
        f"{sum(r['agrees'] for r in gate['independent'])} of {len(gate['independent'])} "
        f"rung areas agree.", "",
        "## Rebuilds", "",
        f"April merger: {sum(r['exact'] for r in april)} of {len(april)} pools exact; "
        f"{sum(r['n_files_bytes_identical'] for r in april)} of "
        f"{sum(len(r['files_committed']) for r in april)} threshold files byte-identical. "
        f"Current merger: {sum(r['exact'] for r in current)} of {len(current)} exact "
        f"({sum(r['exact'] for r in current if r['K'] == 10)} of "
        f"{sum(1 for r in current if r['K'] == 10)} at K = 10).", "",
        *rebuild_table(rebuild), "",
        "## Tilings", "",
        f"T 0.7 passes checked: {sum(len(v['passes']) for v in tilings['t07'].values())}; "
        f"validation passes agreeing: "
        f"{sum(r['agrees'] for rows in tilings['validation'].values() for r in rows)} of "
        f"{sum(len(rows) for rows in tilings['validation'].values())}.", "",
        "## Red sentinel", "",
        f"Head {sentinel['head']}, {sentinel['symlinks_in_copy']} symlinks in the copy; green "
        f"{sentinel['green']['summary']}; restored {sentinel['restored']['summary']}.", "",
        *[f"- {m['mutation']}: {'bites' if m['bites'] else 'DOES NOT BITE'} "
          f"({len(m['failed'])} test(s) red)" for m in sentinel["mutations"]], "",
        "## Task C: gaps", "", *gap_table(clip), "",
        "## Task C: opmax", "", *clip_tables(clip, "opmax"), "",
        "## Task C: stride-shell carried (where distinct from opmax)", "",
        *clip_tables(clip, "carried-stride-shell"), "",
    ]
    (d / "summary.md").write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
