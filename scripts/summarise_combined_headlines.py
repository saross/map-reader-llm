#!/usr/bin/env python3
"""
Summarise headline statistics from the combined / cross-architecture
leaderboards.

For each Era × metric × q-level (and for F1, primary buffer), reports
the top-3 conditions in Tier 1 and the architecture composition of
Tier 1.

Inputs:
    results/leaderboard/combined/era<N>/leaderboard_tiers_f1_<B>m.json
    results/leaderboard/combined/era<N>/leaderboard_tiers_mcc.json
    (and the q01 sensitivity variants)

Outputs:
    results/leaderboard/combined/headlines.md
    results/leaderboard/combined/headlines.json

Usage:
    .venv/bin/python scripts/summarise_combined_headlines.py
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMBINED_ROOT = REPO_ROOT / "results" / "leaderboard" / "combined"
ERAS = [1, 2, 3]
F1_BUFFERS = [20, 30, 40, 50, 100]


def _load(path: Path) -> dict | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _arch_label(cond: dict) -> str:
    """Return a short architecture label for one condition."""
    arch = cond.get("category") or cond.get("architecture") or ""
    if arch == "pv":
        return "PV"
    if arch == "single-pass+PV":
        return "1pass+PV"
    if arch == "consensus":
        return "cons"
    if arch == "single-pass":
        return "1pass"
    return arch or "?"


def _tier1(payload: dict) -> list[dict]:
    """Return the list of Tier-1 condition dicts from a tier JSON."""
    tiers = payload.get("tiers", [])
    if not tiers:
        return []
    return tiers[0].get("conditions", [])


def _summarise_tier1(payload: dict, metric: str, buffer_m: int | None) -> dict:
    """Summarise Tier 1 for one tier JSON."""
    if payload is None:
        return {"populated": False}
    conds = _tier1(payload)
    n_total = sum(len(t.get("conditions", [])) for t in payload.get("tiers", []))

    # Architecture composition
    arch_counts = Counter(_arch_label(c) for c in conds)

    # Top-3 entries: read score from condition's evaluations.
    def _score(c: dict) -> float:
        if metric == "f1":
            ev = c.get("evaluations", {}).get(str(buffer_m), {})
            return float(ev.get("f1", 0) or 0)
        # MCC (buffer-independent — read 20 m or tile_mcc).
        return float(
            c.get("tile_mcc")
            or c.get("evaluations", {}).get("20", {}).get("mcc", 0)
            or 0,
        )

    sorted_conds = sorted(conds, key=_score, reverse=True)
    top3 = []
    for c in sorted_conds[:3]:
        ev = c.get("evaluations", {}).get(str(buffer_m or 20), {})
        top3.append({
            "label": c.get("label"),
            "architecture": _arch_label(c),
            "score": _score(c),
            "f1": ev.get("f1"),
            "f1_ci_lower": ev.get("f1_ci_lower"),
            "f1_ci_upper": ev.get("f1_ci_upper"),
            "precision": ev.get("precision"),
            "recall": ev.get("recall"),
            "mcc": ev.get("mcc") or c.get("tile_mcc"),
        })
    return {
        "populated": True,
        "n_total": n_total,
        "n_tier1": len(conds),
        "tier1_arch_composition": dict(arch_counts),
        "top3": top3,
    }


def main() -> int:
    """Build combined headlines.md + headlines.json."""
    out: dict = {
        "generated": datetime.now(tz=timezone.utc).isoformat(),
        "scope": "combined / cross-architecture leaderboards",
        "eras": {},
    }

    for era in ERAS:
        era_dir = COMBINED_ROOT / f"era{era}"
        if not era_dir.is_dir():
            out["eras"][str(era)] = {"present": False}
            continue
        era_summary: dict = {"present": True, "f1": {}, "mcc": {}}
        for q_tag, q_label in [("", "0.05"), ("_q01", "0.01")]:
            era_summary["f1"][q_label] = {}
            for buf in F1_BUFFERS:
                p = era_dir / f"leaderboard_tiers_f1{q_tag}_{buf}m.json"
                era_summary["f1"][q_label][str(buf)] = _summarise_tier1(
                    _load(p), metric="f1", buffer_m=buf,
                )
            mp = era_dir / f"leaderboard_tiers_mcc{q_tag}.json"
            era_summary["mcc"][q_label] = _summarise_tier1(
                _load(mp), metric="mcc", buffer_m=None,
            )
        out["eras"][str(era)] = era_summary

    # Write JSON
    json_path = COMBINED_ROOT / "headlines.json"
    json_path.write_text(json.dumps(out, indent=2) + "\n")

    # Write markdown
    lines: list[str] = []
    lines.append("# Combined / cross-architecture leaderboard headlines")
    lines.append("")
    lines.append(f"**Generated**: {out['generated']}")
    lines.append("")
    lines.append(
        "Top-3 Tier-1 conditions per Era × metric × (q-level, buffer), "
        "drawn from the combined / cross-architecture tier tables. The "
        "architecture composition of Tier 1 is reported alongside; "
        "abbreviations: `cons` = consensus, `PV` = proposer–verifier, "
        "`1pass` = single-pass, `1pass+PV` = single-pass + PV.",
    )
    lines.append("")

    for era in ERAS:
        era_data = out["eras"].get(str(era), {})
        if not era_data.get("present"):
            continue
        lines.append(f"## Era {era}")
        lines.append("")
        # F1: q=0.05, all buffers; q=0.01 summary
        for q_label in ("0.05", "0.01"):
            lines.append(f"### F1 (q = {q_label})")
            lines.append("")
            lines.append(
                "| Buffer | Tier 1 N | Composition | "
                "Top-3 (label, arch, F1 [95% CI]) |",
            )
            lines.append("|---:|---:|---|---|")
            for buf in F1_BUFFERS:
                s = era_data["f1"][q_label].get(str(buf), {})
                if not s.get("populated"):
                    continue
                comp = s.get("tier1_arch_composition", {})
                comp_str = ", ".join(
                    f"{a}:{n}" for a, n in sorted(comp.items())
                )
                top3 = s.get("top3", [])
                top_strs = []
                for t in top3:
                    f1 = t.get("f1")
                    lo = t.get("f1_ci_lower")
                    hi = t.get("f1_ci_upper")
                    f1_str = f"{f1:.3f}" if f1 is not None else "—"
                    ci_str = (
                        f" [{lo:.3f}, {hi:.3f}]"
                        if lo is not None and hi is not None
                        else ""
                    )
                    top_strs.append(
                        f"`{t['label']}` ({t['architecture']}) "
                        f"{f1_str}{ci_str}",
                    )
                top_md = "<br>".join(
                    f"{i+1}. {ts}" for i, ts in enumerate(top_strs)
                )
                lines.append(
                    f"| {buf} m | {s['n_tier1']} / {s['n_total']} | "
                    f"{comp_str} | {top_md} |",
                )
            lines.append("")

        # MCC
        for q_label in ("0.05", "0.01"):
            lines.append(f"### MCC (q = {q_label})")
            lines.append("")
            s = era_data["mcc"][q_label]
            if not s.get("populated"):
                lines.append("_(no tier file)_")
                lines.append("")
                continue
            comp = s.get("tier1_arch_composition", {})
            comp_str = ", ".join(
                f"{a}:{n}" for a, n in sorted(comp.items())
            )
            lines.append(f"- Tier 1 N: {s['n_tier1']} / {s['n_total']}")
            lines.append(f"- Composition: {comp_str}")
            lines.append("")
            lines.append("| # | Condition | Arch | MCC | F1@20m |")
            lines.append("|--:|:---|:---|---:|---:|")
            for i, t in enumerate(s.get("top3", []), 1):
                mcc = t.get("score") or t.get("mcc")
                f1 = t.get("f1")
                mcc_str = f"{mcc:+.3f}" if mcc is not None else "—"
                f1_str = f"{f1:.3f}" if f1 is not None else "—"
                lines.append(
                    f"| {i} | `{t['label']}` | {t['architecture']} | "
                    f"{mcc_str} | {f1_str} |",
                )
            lines.append("")

    md_path = COMBINED_ROOT / "headlines.md"
    md_path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {md_path} and {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
