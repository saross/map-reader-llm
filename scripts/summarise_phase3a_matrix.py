#!/usr/bin/env python3
"""Compile Phase 3a image matrix evaluation results into summary tables.

Reads evaluation JSONs from results/phase3a-image-matrix/ and produces
a comprehensive summary markdown + all-evaluations JSON.

Usage::

    python scripts/summarise_phase3a_matrix.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "phase3a-image-matrix"


def load_eval(eval_dir: Path) -> list[dict]:
    """Load all evaluation JSONs from a directory (including subdirs).

    Each threshold evaluation lives in its own subdirectory
    (e.g., ``high-t0-3-4of10/evaluation.json``).
    """
    results = []
    # Search subdirectories for evaluation.json files
    for f in sorted(eval_dir.rglob("evaluation.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            summary = data.get("summary", data)
            if "buffers" in summary:
                results.append(summary)
        except (json.JSONDecodeError, KeyError):
            pass
    return results


def extract_best(evals: list[dict], buffer_m: int) -> dict | None:
    """Find the evaluation with the best F1 at the given buffer."""
    best = None
    best_f1 = -1.0
    for ev in evals:
        for buf in ev.get("buffers", []):
            if buf.get("buffer_metres") == buffer_m and buf.get("f1", 0) > best_f1:
                best_f1 = buf["f1"]
                best = {"label": ev.get("label", ""), **buf}
                break
    return best


def main() -> None:
    """Build summary tables from evaluation results."""
    results_dir = RESULTS_DIR
    if not results_dir.is_dir():
        print(f"Results directory not found: {results_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect all results
    matrix: dict[str, list[dict]] = {}
    for thinking_dir in sorted(results_dir.iterdir()):
        if not thinking_dir.is_dir():
            continue
        for pool_dir in sorted(thinking_dir.iterdir()):
            if not pool_dir.is_dir():
                continue
            evals = load_eval(pool_dir)
            if evals:
                key = f"{thinking_dir.name}/{pool_dir.name}"
                matrix[key] = evals

    # Write comprehensive JSON
    all_results: dict[str, list[dict]] = {}
    for key, evals in matrix.items():
        all_results[key] = []
        for ev in evals:
            entry: dict = {"label": ev.get("label", "")}
            for buf in ev.get("buffers", []):
                bm = buf.get("buffer_metres", 0)
                entry[f"f1_{bm}m"] = buf.get("f1", 0)
                entry[f"f1_ci_lo_{bm}m"] = buf.get("f1_ci_lower", 0)
                entry[f"f1_ci_hi_{bm}m"] = buf.get("f1_ci_upper", 0)
                entry[f"p_{bm}m"] = buf.get("precision", 0)
                entry[f"r_{bm}m"] = buf.get("recall", 0)
            all_results[key].append(entry)

    json_path = results_dir / "all-evaluations.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # Build summary markdown
    lines: list[str] = []
    lines.append("# Phase 3a Image Track: Consensus Analysis Summary")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}")
    lines.append("**Scope**: 384 px, 487 tiles (Era 2 full evaluation)")
    lines.append("**Config**: library_plus-hp (13 examples, 4HP 0HN)")
    lines.append("**Model**: Gemini 3 Flash")
    lines.append("")

    # Best operating point per condition
    lines.append("## Best operating point per condition (20m buffer)")
    lines.append("")
    lines.append(
        "| Thinking | T | N | Best t | F1 | 95% CI | P | R |"
    )
    lines.append(
        "|----------|---:|--:|-------:|---:|:------:|---:|---:|"
    )

    for key in sorted(matrix.keys()):
        evals = matrix[key]
        best = extract_best(evals, 20)
        if not best:
            continue

        parts = key.split("/")
        thinking_temp = parts[0]
        pool = parts[1] if len(parts) > 1 else "?"
        thinking = thinking_temp.split("-")[0].upper()
        temp = thinking_temp.split("-", 1)[1] if "-" in thinking_temp else "?"

        label = best.get("label", "")
        t_str = "?"
        m = re.search(r"-(\d+)of", label)
        if m:
            t_str = m.group(1)

        f1 = best.get("f1", 0)
        ci_lo = best.get("f1_ci_lower", 0)
        ci_hi = best.get("f1_ci_upper", 0)
        p = best.get("precision", 0)
        r = best.get("recall", 0)

        lines.append(
            f"| {thinking} | {temp} | {pool} | {t_str} | "
            f"{f1:.3f} | [{ci_lo:.3f}, {ci_hi:.3f}] | "
            f"{p:.3f} | {r:.3f} |"
        )

    lines.append("")

    # HIGH vs MINIMAL comparison
    lines.append("## HIGH vs MINIMAL comparison (20m, best operating point per N)")
    lines.append("")
    lines.append(
        "| T | N | HIGH F1 | HIGH CI | MIN F1 | MIN CI | \u0394 F1 |"
    )
    lines.append(
        "|---:|--:|--------:|:-------:|-------:|:------:|-----:|"
    )

    for temp in ["t0.3", "t0.7", "t1.0"]:
        for pool in ["n5", "n10"]:
            high_key = f"high-{temp}/{pool}"
            min_key = f"minimal-{temp}/{pool}"
            high_best = extract_best(matrix.get(high_key, []), 20)
            min_best = extract_best(matrix.get(min_key, []), 20)
            if high_best and min_best:
                hf1 = high_best.get("f1", 0)
                h_lo = high_best.get("f1_ci_lower", 0)
                h_hi = high_best.get("f1_ci_upper", 0)
                mf1 = min_best.get("f1", 0)
                m_lo = min_best.get("f1_ci_lower", 0)
                m_hi = min_best.get("f1_ci_upper", 0)
                delta = hf1 - mf1
                lines.append(
                    f"| {temp} | {pool} | {hf1:.3f} | "
                    f"[{h_lo:.3f}, {h_hi:.3f}] | "
                    f"{mf1:.3f} | [{m_lo:.3f}, {m_hi:.3f}] | "
                    f"{delta:+.3f} |"
                )

    lines.append("")

    # Full threshold sweep tables at 20m
    lines.append("## Full threshold sweep (20m buffer)")
    lines.append("")

    for key in sorted(matrix.keys()):
        evals = matrix[key]
        lines.append(f"### {key}")
        lines.append("")
        lines.append("| t | F1 | 95% CI | P | R |")
        lines.append("|--:|---:|:------:|---:|---:|")
        for ev in evals:
            label = ev.get("label", "")
            for buf in ev.get("buffers", []):
                if buf.get("buffer_metres") == 20:
                    f1 = buf.get("f1", 0)
                    ci_lo = buf.get("f1_ci_lower", 0)
                    ci_hi = buf.get("f1_ci_upper", 0)
                    p = buf.get("precision", 0)
                    r = buf.get("recall", 0)
                    t_str = "?"
                    if "of" in label:
                        t_str = label.rsplit("-", 1)[-1].split("of")[0]
                    lines.append(
                        f"| {t_str} | {f1:.3f} | "
                        f"[{ci_lo:.3f}, {ci_hi:.3f}] | "
                        f"{p:.3f} | {r:.3f} |"
                    )
        lines.append("")

    # Buffer sensitivity
    lines.append("## Buffer sensitivity (best F1 per condition)")
    lines.append("")
    lines.append("| Condition | 20m | 30m | 40m | 50m |")
    lines.append("|-----------|----:|----:|----:|----:|")

    for key in sorted(matrix.keys()):
        evals = matrix[key]
        vals = []
        for bm in [20, 30, 40, 50]:
            best = extract_best(evals, bm)
            vals.append(f"{best['f1']:.3f}" if best else "\u2014")
        joined = " | ".join(vals)
        lines.append(f"| {key} | {joined} |")

    lines.append("")
    lines.append(
        f"*Generated: {datetime.now(tz=timezone.utc).isoformat()}*"
    )

    md_path = results_dir / "consensus-analysis-summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Summary: {md_path}")
    print(f"Evaluations JSON: {json_path}")
    print(f"Conditions analysed: {len(matrix)}")
    print(f"Total evaluations: {sum(len(v) for v in matrix.values())}")


if __name__ == "__main__":
    main()
