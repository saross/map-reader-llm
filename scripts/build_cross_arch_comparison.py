#!/usr/bin/env python3
"""
Build cross-architecture comparison table at a fixed buffer
============================================================

For each (era, architecture) stratum, find the best-performing condition
at the target buffer (default 20 m), and emit a flat comparison table
showing how architectures stack up within each era.

Useful for the paper's "architecture choice matters" narrative.

Usage:
    .venv/bin/python scripts/build_cross_arch_comparison.py \\
        --root results/leaderboard/per-architecture \\
        --buffer 20 \\
        --output results/leaderboard/per-architecture/cross-architecture-20m.md

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

ARCHITECTURES = ["single-pass", "consensus", "single-pass+PV", "pv"]
ARCH_DISPLAY = {
    "single-pass": "Single-pass (raw)",
    "consensus": "Consensus (no PV)",
    "single-pass+PV": "Single-pass + PV",
    "pv": "Consensus + PV",
}
ERAS = [1, 2, 3]
ERA_DISPLAY = {
    1: "Era 1 — 512 px / 340 tiles",
    2: "Era 2 — 384 px / 487 tiles",
    3: "Era 3 — 384 px / 327 tiles",
}


def fmt_ci(lo, hi, ndigits=3, default="n/a"):
    if lo is None or hi is None:
        return default
    return f"[{lo:.{ndigits}f}, {hi:.{ndigits}f}]"


def fmt_val(x, ndigits=3, default="—"):
    if x is None:
        return default
    if isinstance(x, float):
        return f"{x:.{ndigits}f}"
    return str(x)


def find_best(stratum_json: Path, buffer_metres: int) -> dict | None:
    """Return the top-F1 row at the given buffer (tier-1, rank-1)."""
    if not stratum_json.is_file():
        return None
    data = json.loads(stratum_json.read_text())
    rows = data.get("rows", [])
    if not rows:
        return None
    # rank-1 row is the top of tier 1 because the upstream sort is by
    # F1 descending. Use the rank field to be safe.
    return min(rows, key=lambda r: r.get("rank", 999))


def build_cross_arch(root: Path, buffer_metres: int) -> tuple[list[dict], list[str]]:
    """Collect the top condition per (era, arch) stratum into one table."""
    rows: list[dict] = []
    for era in ERAS:
        for arch in ARCHITECTURES:
            stratum_json = (
                root / f"era{era}" / arch / f"leaderboard_rows_{buffer_metres}m.json"
            )
            best = find_best(stratum_json, buffer_metres)
            if best is None:
                rows.append(
                    {
                        "era": era,
                        "architecture": arch,
                        "condition_id": None,
                        "track": None,
                        "k": None,
                        "vote_t": None,
                        "prob_t": None,
                        "proposer": None,
                        "config_version": None,
                        "verifier_prompt": None,
                        "f1": None,
                        "f1_ci_lower": None,
                        "f1_ci_upper": None,
                        "precision": None,
                        "recall": None,
                        "mcc": None,
                        "tier": None,
                        "status": "empty",
                    }
                )
            else:
                rows.append({**best, "status": "ok"})

    lines: list[str] = []
    lines.append(
        f"# Cross-architecture comparison — {buffer_metres} m buffer"
    )
    lines.append("")
    lines.append(
        f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}"
    )
    lines.append("")
    lines.append(
        f"Each row shows the best-F1 condition within a (era, architecture) "
        f"stratum at the {buffer_metres} m buffer. The tier assignments "
        f"come from the per-stratum BH-FDR tiering (i.e., tier 1 = "
        f"statistically indistinguishable from the in-stratum top), NOT "
        f"from a cross-stratum pairwise comparison. Era 1 vs. Era 2/3 is "
        f"NOT tile-paired here — the tile grids differ (512 px vs 384 px)."
    )
    lines.append("")

    for era in ERAS:
        lines.append(f"## {ERA_DISPLAY[era]}")
        lines.append("")
        era_rows = [r for r in rows if r["era"] == era]
        if not any(r["status"] == "ok" for r in era_rows):
            lines.append("_No populated strata._")
            lines.append("")
            continue

        # Highlight the best-F1 architecture for the era.
        okish = [r for r in era_rows if r["status"] == "ok" and r.get("f1") is not None]
        if okish:
            leader = max(okish, key=lambda r: r["f1"])
            lines.append(
                f"**Era leader**: `{leader['condition_id']}` "
                f"({ARCH_DISPLAY[leader['architecture']]}, track={leader['track']}) "
                f"— F1 = {leader['f1']:.3f} "
                f"{fmt_ci(leader.get('f1_ci_lower'), leader.get('f1_ci_upper'))}."
            )
            lines.append("")
        lines.append(
            "| Architecture | Top condition | Track | K | Vote t | "
            "Verifier | Prob t | F1 | 95% CI | P | R | MCC |"
        )
        lines.append(
            "|:-------------|:--------------|:-----:|--:|:-----:|"
            ":--------:|:-----:|---:|:------:|---:|---:|---:|"
        )
        for r in era_rows:
            if r["status"] != "ok":
                lines.append(
                    f"| {ARCH_DISPLAY[r['architecture']]} | "
                    "— | — | — | — | — | — | — | — | — | — | — |"
                )
                continue
            vote_t = fmt_val(r.get("vote_t"), 0, "—")
            prob_t = fmt_val(r.get("prob_t"), 2, "—")
            f1_str = fmt_val(r.get("f1"), 3, "—")
            ci_str = fmt_ci(r.get("f1_ci_lower"), r.get("f1_ci_upper"))
            p_str = fmt_val(r.get("precision"), 3, "—")
            r_str = fmt_val(r.get("recall"), 3, "—")
            mcc_str = fmt_val(r.get("mcc"), 3, "—")
            lines.append(
                f"| {ARCH_DISPLAY[r['architecture']]} | "
                f"`{r['condition_id']}` | {r['track']} | "
                f"{r['k']} | {vote_t} | {r.get('verifier_prompt', '—')} | "
                f"{prob_t} | {f1_str} | {ci_str} | {p_str} | "
                f"{r_str} | {mcc_str} |"
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "Tiering methodology: within each (era, architecture) stratum, "
        "conditions are ranked by point-estimate F1 at 20 m and grouped "
        "into tiers via greedy-clique BH-FDR on tile-level paired "
        "permutation tests (10,000 permutations, seed 42) at q=0.05. "
        "CIs are stratified bootstrap (1,000 iterations). The top row in "
        "each stratum is always Tier 1 rank 1."
    )
    return rows, lines


def main() -> int:
    """Emit the cross-architecture comparison markdown + JSON."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT / "results/leaderboard/per-architecture",
    )
    parser.add_argument("--buffer", type=int, default=20)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output markdown path (default: <root>/cross-architecture-<buffer>m.md)",
    )
    args = parser.parse_args()

    out_md = args.output or (
        args.root / f"cross-architecture-{args.buffer}m.md"
    )
    out_json = out_md.with_suffix(".json")

    rows, lines = build_cross_arch(args.root, args.buffer)

    out_md.parent.mkdir(parents=True, exist_ok=True)
    # Ensure trailing newline so markdownlint MD047 passes.
    out_md.write_text("\n".join(lines) + "\n")
    out_json.write_text(
        json.dumps(
            {
                "script": "build_cross_arch_comparison.py",
                "generated": datetime.now(tz=timezone.utc).isoformat(),
                "buffer_m": args.buffer,
                "rows": rows,
            },
            indent=2,
        )
    )
    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
