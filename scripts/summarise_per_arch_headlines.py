#!/usr/bin/env python3
"""
Extract headline statistics from per-architecture leaderboards.

Inspects each populated stratum's enriched-row JSON and emits a
short-form summary with:

- Best F1 per stratum (Tier 1 rank 1) + CI, condition id, track.
- Tier-1 size per stratum (how many conditions clustered at the top?).
- Inter-stratum deltas (how much does PV beat consensus in Era 2?).

Output: `results/leaderboard/per-architecture/headlines.md` and
`headlines.json`.

Usage:
    .venv/bin/python scripts/summarise_per_arch_headlines.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT = REPO_ROOT / "results/leaderboard/per-architecture"

ERAS = [1, 2, 3]
ARCHITECTURES = ["single-pass", "consensus", "single-pass+PV", "pv"]


def load_stratum(era: int, arch: str, buffer_m: int) -> dict | None:
    """Load one stratum's enriched rows JSON if present."""
    p = ROOT / f"era{era}" / arch / f"leaderboard_rows_{buffer_m}m.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text())


def summarise_stratum(data: dict) -> dict:
    """Return a short stat dict for one stratum."""
    rows = data.get("rows", [])
    if not rows:
        return {"populated": False}
    top = min(rows, key=lambda r: r.get("rank", 999))
    tier1_rows = [r for r in rows if r.get("tier") == 1]
    return {
        "populated": True,
        "n_conditions": len(rows),
        "n_tier1": len(tier1_rows),
        "top": {
            "condition_id": top.get("condition_id"),
            "track": top.get("track"),
            "f1": top.get("f1"),
            "f1_ci_lower": top.get("f1_ci_lower"),
            "f1_ci_upper": top.get("f1_ci_upper"),
            "precision": top.get("precision"),
            "recall": top.get("recall"),
            "mcc": top.get("mcc"),
            "vote_t": top.get("vote_t"),
            "prob_t": top.get("prob_t"),
            "verifier_prompt": top.get("verifier_prompt"),
            "config_version": top.get("config_version"),
        },
    }


def main() -> int:
    """Write headlines.md + headlines.json."""
    matrix: dict = {}
    for era in ERAS:
        matrix[era] = {}
        for arch in ARCHITECTURES:
            data = load_stratum(era, arch, 20)
            matrix[era][arch] = summarise_stratum(data) if data else {"populated": False}

    # Compute some deltas
    deltas: list[str] = []
    if matrix[2]["consensus"].get("populated") and matrix[2]["pv"].get("populated"):
        c_top = matrix[2]["consensus"]["top"]["f1"]
        pv_top = matrix[2]["pv"]["top"]["f1"]
        deltas.append(
            f"Era 2: PV Tier-1 top ({pv_top:.3f}) vs Consensus Tier-1 top "
            f"({c_top:.3f}) → ΔF1 = {pv_top - c_top:+.3f}"
        )

    if matrix[2]["single-pass"].get("populated") and matrix[2]["consensus"].get("populated"):
        sp_top = matrix[2]["single-pass"]["top"]["f1"]
        c_top = matrix[2]["consensus"]["top"]["f1"]
        deltas.append(
            f"Era 2: Consensus Tier-1 top ({c_top:.3f}) vs Single-pass Tier-1 "
            f"top ({sp_top:.3f}) → ΔF1 = {c_top - sp_top:+.3f} (K-pass benefit)"
        )

    if matrix[2]["single-pass+PV"].get("populated") and matrix[2]["single-pass"].get("populated"):
        sppv_top = matrix[2]["single-pass+PV"]["top"]["f1"]
        sp_top = matrix[2]["single-pass"]["top"]["f1"]
        deltas.append(
            f"Era 2: Single-pass + PV Tier-1 top ({sppv_top:.3f}) vs "
            f"Single-pass (raw) Tier-1 top ({sp_top:.3f}) → "
            f"ΔF1 = {sppv_top - sp_top:+.3f} (verifier benefit @ K=1)"
        )

    # Build markdown
    lines: list[str] = []
    lines.append("# Per-architecture headline statistics @ 20 m")
    lines.append("")
    lines.append(
        f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}"
    )
    lines.append("")
    lines.append(
        "Tier-1 top per stratum + overall counts. All numbers are at 20 m "
        "buffer. CIs are stratified bootstrap (1,000 iterations, seed 42)."
    )
    lines.append("")

    lines.append("## Tier-1 top per (era, architecture)")
    lines.append("")
    lines.append(
        "| Era | Architecture | Top condition | Track | F1 | 95% CI | "
        "Vote t | Verifier | Prob t | #Tier-1 | #Total |"
    )
    lines.append(
        "|:---:|:-------------|:--------------|:-----:|---:|:------:|"
        ":-----:|:---------|:-----:|---:|---:|"
    )
    for era in ERAS:
        for arch in ARCHITECTURES:
            s = matrix[era][arch]
            if not s.get("populated"):
                lines.append(
                    f"| {era} | {arch} | _(empty stratum)_ | — | — | — | "
                    "— | — | — | 0 | 0 |"
                )
                continue
            t = s["top"]
            ci = (
                f"[{t.get('f1_ci_lower', 0):.3f}, {t.get('f1_ci_upper', 0):.3f}]"
                if t.get("f1_ci_lower") is not None
                else "n/a"
            )
            prob_t = (
                f"{t['prob_t']:.2f}" if isinstance(t.get("prob_t"), float) else "—"
            )
            vote_t_str = str(t["vote_t"]) if t.get("vote_t") is not None else "—"
            verifier = t.get("verifier_prompt") or "—"
            lines.append(
                f"| {era} | {arch} | `{t['condition_id']}` | {t['track']} | "
                f"{t.get('f1', 0):.3f} | {ci} | "
                f"{vote_t_str} | {verifier} | {prob_t} | "
                f"{s.get('n_tier1', 0)} | {s.get('n_conditions', 0)} |"
            )

    lines.append("")
    lines.append("## Architecture deltas (within Era 2)")
    lines.append("")
    for d in deltas:
        lines.append(f"- {d}")
    if not deltas:
        lines.append("_No deltas computable (missing strata)._")
    lines.append("")

    out_md = ROOT / "headlines.md"
    out_json = ROOT / "headlines.json"
    out_md.write_text("\n".join(lines))
    out_json.write_text(json.dumps(matrix, indent=2))
    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
