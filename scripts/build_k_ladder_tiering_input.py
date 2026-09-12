#!/usr/bin/env python3
"""
Write the tiering inputs for one K ladder, without touching the register.

``scripts/era1_leaderboard_tiering.py`` is the project's canonical tiering
instrument — round-robin tile-swap micro-F1 permutation, Benjamini–Hochberg at
q = 0.05, greedy-clique tiers, MCC carried as a reported column — and it reads
its cell set from a named analysis row's ``conditions_compared`` and each cell's
own ``evaluation.json``. Reusing it verbatim on a ladder therefore needs two
things the register does not hold:

1. **An analysis row naming the ladder's rungs.** The ladder is its own analysis
   (the "ladder, then board" principle), and its row is authored UNSIGNED at the
   end of the run — but the tiering has to run before the row can state an
   outcome. A local input file breaks that circularity without minting a
   placeholder row into the register.
2. **Each rung's evaluation ON THE LADDER'S FRAME.** The gold-standard stride
   rungs are committed on grid-common; ruling R2 tiers on the board frame. The
   frame swap is a re-score, not a re-run, and its evaluations live under the
   ladder's own results directory — so the rungs' ``eval_path`` must point there
   for the instrument to read the right F1 and MCC.

Both substitutions land in ``<out-dir>/`` as copies clearly marked as INPUTS.
Neither ``results/run-conditions.json`` nor ``results/run-analyses.json`` is
modified, and the copies must never be written back over them.

Usage::

    python scripts/build_k_ladder_tiering_input.py \\
        --analysis-id k-ladder-gs-stride-a-2026-09-12 \\
        --rung stride-phaseb-2026-08-25::g384-ov128-ladder-n1-verified-p0.15-k1=\\
results/k-ladder-2026-09-12/board-frame/stride-phaseb__g384-ov128-ladder-n1/evaluation.json \\
        --rung ... \\
        --out-dir results/k-ladder-2026-09-12/tiering-input/gs-stride-a

Zero API.

Created: 2026-09-12 (Session 154, K-ladder Phase 1 step 5)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_CONDITIONS = PROJECT_ROOT / "results/run-conditions.json"
RUN_ANALYSES = PROJECT_ROOT / "results/run-analyses.json"


def parse_rung(spec: str) -> tuple[str, str | None]:
    """Split a ``condition_id[=eval_path]`` rung specification."""
    if "=" in spec:
        condition_id, eval_path = spec.split("=", 1)
        return condition_id.strip(), eval_path.strip()
    return spec.strip(), None


def build(analysis_id: str, rungs: list[tuple[str, str | None]],
          note: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """The two input documents.

    Args:
        analysis_id: The ladder's analysis id.
        rungs: ``(condition_id, eval_path or None)`` in ladder order.
        note: One line describing the ladder, for the analysis row.

    Returns:
        ``(conditions_doc, analyses_doc)``.

    Raises:
        KeyError: If a rung's condition is not registered.
        FileNotFoundError: If a substituted evaluation path does not exist.
    """
    conditions = json.loads(RUN_CONDITIONS.read_text(encoding="utf-8"))
    analyses = json.loads(RUN_ANALYSES.read_text(encoding="utf-8"))
    dec = conditions["decomposition"]

    substituted = []
    for condition_id, eval_path in rungs:
        run_id, label = condition_id.split("::", 1)
        entry = dec.get(run_id)
        row = next((c for c in (entry or {}).get("conditions", [])
                    if c["label"] == label), None)
        if row is None:
            raise KeyError(f"{condition_id} is not a registered condition")
        if eval_path is None:
            continue
        if not (PROJECT_ROOT / eval_path).is_file():
            raise FileNotFoundError(
                f"{condition_id}: substituted evaluation {eval_path} does not exist")
        substituted.append({"condition_id": condition_id,
                            "registered_eval_path": row.get("eval_path"),
                            "input_eval_path": eval_path})
        row["eval_path"] = eval_path

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conditions["_tiering_input_note"] = (
        f"TIERING INPUT ONLY — NOT THE REGISTER. Built {stamp} by "
        f"scripts/build_k_ladder_tiering_input.py for analysis {analysis_id}. "
        f"{len(substituted)} condition row(s) have their eval_path substituted so "
        f"the instrument reads the ladder's own frame; every other field, and the "
        f"whole of results/run-conditions.json on disk, is unchanged. Never copy "
        f"this file over the register.")
    conditions["_tiering_input_substitutions"] = substituted

    rows = analyses["analyses"] if isinstance(analyses, dict) else analyses
    if any(r["analysis_id"] == analysis_id for r in rows):
        raise KeyError(
            f"{analysis_id} already exists in the register; this script is for "
            "a ladder whose row is authored after the tiering runs")
    rows.append({
        "analysis_id": analysis_id,
        "type": "comparison",
        "_note": (f"TIERING INPUT ROW — NOT REGISTERED. {note} Built {stamp} by "
                  "scripts/build_k_ladder_tiering_input.py so "
                  "scripts/era1_leaderboard_tiering.py can tier the ladder with "
                  "the board instrument verbatim before the ladder's real "
                  "analysis row is authored."),
        "conditions_compared": [cid for cid, _ in rungs],
        "hypothesis_refs": ["H3"],
        "outcome": "PENDING: this is a tiering input, not a registered result",
        "paper_section": "Results",
        "output_path": None,
        "working_notes_obs": [],
        "preregistered": "post-hoc",
        "deviations": [],
    })
    return conditions, analyses


def main(argv: list[str] | None = None) -> int:
    """Write the ladder's conditions and analyses inputs."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--analysis-id", required=True)
    parser.add_argument("--rung", action="append", required=True,
                        help="condition_id[=eval_path]; repeat in ladder order.")
    parser.add_argument("--note", default="A fixed-parameter K ladder.",
                        help="One line describing the ladder.")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        conditions, analyses = build(
            args.analysis_id, [parse_rung(r) for r in args.rung], args.note)
    except (KeyError, FileNotFoundError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "run-conditions.json").write_text(
        json.dumps(conditions, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.out_dir / "run-analyses.json").write_text(
        json.dumps(analyses, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir}/run-conditions.json and run-analyses.json "
          f"for {args.analysis_id} with {len(args.rung)} rung(s); "
          f"{len(conditions['_tiering_input_substitutions'])} eval_path "
          f"substitution(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
