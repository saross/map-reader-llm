#!/usr/bin/env python3
"""
Generate per-architecture headline summary at an arbitrary buffer.

Reads the buffer-specific F1 tier table
(`leaderboard_tiers_<buffer>m.json`) and the (buffer-invariant) MCC
tier table for each populated stratum. Produces a markdown file
listing the top-3 conditions per stratum at the requested buffer for
both metrics. Output mirrors the structure of
`headlines.md` (which is the 20 m primary).

Companion to `summarise_per_arch_headlines.py`, which is hardcoded to
20 m and reads a different (now-stale) row schema. This script reads
the current tier-JSON schema directly and supports any buffer for
which a tier table has been built (20, 30, 40, 50, or 100 m).

Usage::

    .venv/bin/python scripts/summarise_per_arch_headlines_at_buffer.py \\
        --buffer 50

Outputs (where `<N>` is the buffer):

- `results/leaderboard/per-architecture/headlines_<N>m.md`
- `results/leaderboard/per-architecture/headlines_<N>m.json`

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-26 (Session 79 — parallel 50 / 100 m headlines)
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT = REPO_ROOT / "results/leaderboard/per-architecture"

ERAS = [1, 2, 3]
ARCHITECTURES = ["single-pass", "consensus", "single-pass+PV", "pv"]


def find_eval_at_buffer(condition: dict, buffer_m: int) -> dict | None:
    """Return the per-buffer evaluation dict for buffer_m, or None.

    The `evaluations` field is a dict keyed by stringified buffer
    (e.g. "20", "30", "40", "50", "100"), each value being a dict
    with f1 / f1_ci_lower / f1_ci_upper / precision / recall / etc.
    """
    evals = condition.get("evaluations", {})
    if isinstance(evals, dict):
        return evals.get(str(buffer_m))
    # Backward-compat fallback: array of dicts with buffer_metres field.
    for ev in evals:
        if isinstance(ev, dict) and ev.get("buffer_metres") == buffer_m:
            return ev
    return None


def load_tier_top_n(
    era: int, arch: str, metric: str, buffer_m: int, n: int = 3
) -> list[dict] | None:
    """Return the top-n conditions in tier 1 of the requested table.

    metric: "f1" or "mcc". For F1, reads
    leaderboard_tiers_<buffer>m.json (buffer-specific tiering per
    Obs 279). For MCC, the test statistic is buffer-independent (per
    Obs 280) — the per-buffer agent generated only `.md` copies at
    30/40/50/100 m and the canonical MCC JSON lives at 20 m. We fall
    back to the 20 m MCC JSON for any buffer.
    """
    if metric == "mcc":
        # MCC tier assignment is buffer-invariant per Obs 280;
        # canonical JSON is at 20 m.
        p = ROOT / f"era{era}" / arch / "leaderboard_tiers_mcc_20m.json"
    else:
        p = ROOT / f"era{era}" / arch / f"leaderboard_tiers_{buffer_m}m.json"
    if not p.is_file():
        return None
    data = json.loads(p.read_text())
    tiers = data.get("tiers", [])
    if not tiers:
        return None
    tier1 = tiers[0].get("conditions", [])
    return tier1[:n]


def format_f1_table(rows: list[dict], buffer_m: int) -> list[str]:
    """Return markdown lines for the F1 top-3 table."""
    lines = [
        f"| # | Condition | F1 [95% CI] | P | R |",
        "|--:|:---|:---|---:|---:|",
    ]
    for i, c in enumerate(rows, start=1):
        ev = find_eval_at_buffer(c, buffer_m) or {}
        f1 = ev.get("f1")
        lo = ev.get("f1_ci_lower")
        hi = ev.get("f1_ci_upper")
        p = ev.get("precision")
        r = ev.get("recall")
        ci = (
            f"[{lo:.3f}, {hi:.3f}]"
            if lo is not None and hi is not None
            else "n/a"
        )
        f1_str = f"{f1:.3f}" if f1 is not None else "—"
        p_str = f"{p:.3f}" if p is not None else "—"
        r_str = f"{r:.3f}" if r is not None else "—"
        lines.append(
            f"| {i} | `{c.get('label', '?')}` | {f1_str} {ci} | "
            f"{p_str} | {r_str} |"
        )
    return lines


def format_mcc_table(rows: list[dict], buffer_m: int) -> list[str]:
    """Return markdown lines for the MCC top-3 table."""
    lines = [
        f"| # | Condition | MCC | F1@{buffer_m}m |",
        "|--:|:---|---:|---:|",
    ]
    for i, c in enumerate(rows, start=1):
        mcc = c.get("tile_mcc")
        ev = find_eval_at_buffer(c, buffer_m) or {}
        f1 = ev.get("f1")
        mcc_str = f"{mcc:+.3f}" if mcc is not None else "—"
        f1_str = f"{f1:.3f}" if f1 is not None else "—"
        lines.append(
            f"| {i} | `{c.get('label', '?')}` | {mcc_str} | {f1_str} |"
        )
    return lines


def main() -> int:
    """Write headlines_<buffer>m.{md,json}."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--buffer",
        type=int,
        required=True,
        choices=[20, 30, 40, 50, 100],
        help="Buffer in metres to extract headlines for.",
    )
    args = ap.parse_args()
    buf = args.buffer

    matrix: dict = {}
    lines: list[str] = []
    lines.append(f"# Headlines — top-3 per stratum @ {buf} m buffer")
    lines.append("")
    lines.append(
        f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}"
    )
    lines.append("")
    lines.append(
        f"Top-3 conditions in Tier 1 of each populated (era, architecture) "
        f"stratum at q=0.05, separately for F1 and MCC. **Buffer = {buf} m** "
        "for F1; MCC is buffer-invariant by methodology (per Obs 280) but "
        f"the F1@{buf}m column shows the same condition's F1 value at this "
        "buffer for cross-reference."
    )
    lines.append("")
    lines.append(
        f"For the primary (20 m) headline summary, see `headlines.md`. "
        "For the methodology reference, see `README.md` and "
        "`docs/notes/reflections/working-notes.md` Obs 279 + 280."
    )
    lines.append("")

    for era in ERAS:
        matrix[era] = {}
        for arch in ARCHITECTURES:
            f1_rows = load_tier_top_n(era, arch, "f1", buf)
            mcc_rows = load_tier_top_n(era, arch, "mcc", buf)
            if f1_rows is None and mcc_rows is None:
                matrix[era][arch] = {"populated": False}
                lines.append(f"## Era {era} / {arch}")
                lines.append("")
                lines.append("_(empty stratum)_")
                lines.append("")
                continue

            matrix[era][arch] = {
                "populated": True,
                "f1_top3": [
                    {
                        "label": r.get("label"),
                        "f1": (find_eval_at_buffer(r, buf) or {}).get("f1"),
                    }
                    for r in (f1_rows or [])
                ],
                "mcc_top3": [
                    {
                        "label": r.get("label"),
                        "mcc": r.get("tile_mcc"),
                    }
                    for r in (mcc_rows or [])
                ],
            }
            lines.append(f"## Era {era} / {arch}")
            lines.append("")
            lines.append(f"### F1 ({buf} m)")
            lines.append("")
            if f1_rows:
                lines.extend(format_f1_table(f1_rows, buf))
            else:
                lines.append("_(no F1 tier table at this buffer)_")
            lines.append("")
            lines.append("### MCC")
            lines.append("")
            if mcc_rows:
                lines.extend(format_mcc_table(mcc_rows, buf))
            else:
                lines.append("_(no MCC tier table)_")
            lines.append("")

    out_md = ROOT / f"headlines_{buf}m.md"
    out_json = ROOT / f"headlines_{buf}m.json"
    out_md.write_text("\n".join(lines))
    out_json.write_text(json.dumps(matrix, indent=2))
    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
