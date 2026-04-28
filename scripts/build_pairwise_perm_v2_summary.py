#!/usr/bin/env python3
"""Build the cross-pair summary Markdown for ``55maps-pairwise-permutation-v2``.

Consumes the three per-pair ``summary.json`` files produced by
``paired_permutation_corrected_55maps.py`` (one per pair) and writes a
single Markdown report with three tables (rows = buffers, cols = the
relevant statistics) plus an interpretation block flagging which contrasts
survive Benjamini-Hochberg FDR correction within each pair.

The script is read-only on the per-pair JSON outputs — it does not
re-run any permutations — so it can be invoked locally even if the heavy
compute was performed on sapphire.

Usage:

    python scripts/build_pairwise_perm_v2_summary.py \\
        --base-dir results/55maps-pairwise-permutation-v2

Author: Shawn Ross & Claude (Anthropic)
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

PAIR_DIRS = (
    ("paired-t0.3-vs-t0.7", "T=0.3", "T=0.7"),
    ("paired-t0.3-vs-image", "T=0.3", "image"),
    ("paired-t0.7-vs-image", "T=0.7", "image"),
    ("paired-t0.3-vs-tmin", "T=0.3", "T=MIN"),
    ("paired-t0.7-vs-tmin", "T=0.7", "T=MIN"),
    ("paired-image-vs-tmin", "image", "T=MIN"),
)


def fmt_p(p: float) -> str:
    """Format a p-value compactly (3 decimals, < 0.001 as '<0.001')."""
    if p < 0.001:
        return "<0.001"
    return f"{p:.3f}"


def fmt_delta_with_ci(
    delta: float, lo: float, hi: float,
) -> str:
    """Format ΔF1 with bracketed 95 % CI."""
    return f"{delta:+.4f} [{lo:+.4f}, {hi:+.4f}]"


def render_pair_table(summary: dict, label_a: str, label_b: str) -> str:
    """Render the buffer × statistics Markdown table for one pair."""
    rows = ["| R (m) | F1 A | F1 B | ΔF1 (A−B) [95 % CI] | p (raw) | p (BH) | sig (q=0.05) | W/L/T |",
            "|------:|-----:|-----:|--------------------:|--------:|-------:|:------------:|------:|"]
    for r in summary["per_buffer"]:
        sig = "**\\***" if r["significant_at_q"] else "ns"
        rows.append(
            f"| {r['buffer_metres']:>4} "
            f"| {r['f1_a']:.4f} | {r['f1_b']:.4f} "
            f"| {fmt_delta_with_ci(r['delta_f1'], r['delta_f1_ci_lower'], r['delta_f1_ci_upper'])} "
            f"| {fmt_p(r['p_raw'])} | {fmt_p(r['p_bh'])} "
            f"| {sig} "
            f"| {r['wins_a']}/{r['losses_a']}/{r['ties']} |"
        )
    return "\n".join(rows)


def headline_at_50m(summary: dict, label_a: str, label_b: str) -> str:
    """Render a one-line headline at the canonical R = 50 m operating buffer."""
    row50 = next(
        (r for r in summary["per_buffer"] if r["buffer_metres"] == 50),
        None,
    )
    if row50 is None:
        return (
            f"- **{label_a} vs {label_b}**: R = 50 m row missing from summary."
        )
    sig = "significant" if row50["significant_at_q"] else "ns"
    return (
        f"- **{label_a} vs {label_b}** at R = 50 m: ΔF1 = "
        f"{fmt_delta_with_ci(row50['delta_f1'], row50['delta_f1_ci_lower'], row50['delta_f1_ci_upper'])}; "
        f"raw p = {fmt_p(row50['p_raw'])}, BH-FDR p = {fmt_p(row50['p_bh'])} "
        f"({sig} at q = 0.05 within pair)."
    )


def collect_significant_buffers(summary: dict) -> list[int]:
    """Return list of buffer Rs surviving BH-FDR correction within the pair."""
    return [
        r["buffer_metres"] for r in summary["per_buffer"]
        if r["significant_at_q"]
    ]


def render_summary(base_dir: Path) -> str:
    """Render the full cross-pair summary Markdown."""
    timestamp = datetime.now(timezone.utc).isoformat()

    pair_blocks: list[str] = []
    headlines: list[str] = []
    sig_lines: list[str] = []

    for sub, label_a, label_b in PAIR_DIRS:
        path = base_dir / sub / "summary.json"
        if not path.exists():
            pair_blocks.append(
                f"## {label_a} vs {label_b}\n\n"
                f"_Summary file missing: `{path}`_\n"
            )
            continue

        with open(path, encoding="utf-8") as f:
            summary = json.load(f)

        table = render_pair_table(summary, label_a, label_b)
        pair_blocks.append(
            f"## {label_a} vs {label_b}\n\n"
            f"Detection sets:\n\n"
            f"- A ({label_a}): `{summary['condition_a']['detections']}`\n"
            f"- B ({label_b}): `{summary['condition_b']['detections']}`\n\n"
            f"{table}\n\n"
            f"Notes — wins / losses / ties are tile-level "
            f"comparisons (per-tile F1_A vs F1_B); ΔF1 is the aggregate "
            f"micro-average difference; CI is a 10 000-iteration tile-level "
            f"paired bootstrap."
        )
        headlines.append(headline_at_50m(summary, label_a, label_b))
        sig_buffers = collect_significant_buffers(summary)
        if sig_buffers:
            sig_lines.append(
                f"- **{label_a} vs {label_b}**: "
                f"significant after BH-FDR (q = 0.05) at R ∈ "
                f"{{{', '.join(f'{b} m' for b in sig_buffers)}}}."
            )
        else:
            sig_lines.append(
                f"- **{label_a} vs {label_b}**: no buffer survives BH-FDR "
                f"(q = 0.05) within pair."
            )

    md = f"""# Pairwise paired-permutation tests — 55-map corrected detection sets

**Timestamp**: {timestamp}
**Pairs**: {", ".join(f"{a} vs {b}" for _, a, b in PAIR_DIRS)}
**Buffers**: 20, 25, 30, 35, 40, 45, 50, 75, 100, 125 m
**Permutations**: 10 000 per cell, seed = 42, two-sided
**Bootstrap CI**: 10 000 tile-level paired iterations, seed = 42
**FDR correction**: Benjamini-Hochberg within each pair, q = 0.05
**Methodology**: Approach B — extended-GT-at-R Hungarian matching; per-side
extended GT identical to each run's `corrected-f1-multi-buffer/summary.json`.
**Test statistic**: aggregate (micro-average) F1 difference; tile-swap
permutations preserve pairing across the 8 541 evaluation tiles.

## Headline at canonical R = 50 m

{chr(10).join(headlines)}

## Buffers surviving BH-FDR correction (q = 0.05) within pair

{chr(10).join(sig_lines)}

{(chr(10) + chr(10)).join(pair_blocks)}

## Reproducibility

- Driver: `scripts/paired_permutation_corrected_55maps.py`
- Summary builder: `scripts/build_pairwise_perm_v2_summary.py`
- Per-pair JSON outputs in `paired-<a>-vs-<b>/permutation-R<R>m.json`
- Per-pair summary in `paired-<a>-vs-<b>/summary.json`
- Detection inputs are unchanged from each run's
  `outputs/<run>/verified/verified_detections.geojson`; the corrected
  ground truth is rebuilt at each R from the run's review CSVs.
"""
    return md


def main() -> None:
    """Parse args, render the summary, and write summary.md to disk."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--base-dir", type=Path,
        default=Path("results/55maps-pairwise-permutation-v2"),
        help="Directory containing the three paired-<x>-vs-<y> sub-dirs.",
    )
    p.add_argument(
        "--output", type=Path, default=None,
        help="Output Markdown path (default: <base-dir>/summary.md).",
    )
    args = p.parse_args()

    md = render_summary(args.base_dir)
    out = args.output or (args.base_dir / "summary.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
