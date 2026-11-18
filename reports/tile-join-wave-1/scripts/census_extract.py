#!/usr/bin/env python3
"""
Census extraction for the tile-join Wave 1 worklist (W1.0, step 4).

Reads every tracked evaluation file (``git ls-files``: files named exactly
``evaluation.json`` plus ``results/retest/*-evaluation.json``) and writes
one JSON line per file with the facts the worklist classifies on: the
frame, the reference, the detection inputs, whether a tile block is
present and which join it records, single or replicated, bootstrap
settings, and the writing script. Read-only; standard library only.

Usage (zbook, from the branch worktree)::

    python3 reports/tile-join-wave-1/scripts/census_extract.py \\
        > ~/scratch/wave1/w10/census/census.jsonl

Created: 2026-11-18 (tile-join Wave 1, W1.0)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]


def tracked_evaluations() -> list[str]:
    """List the tracked evaluation files, by the census's two definitions.

    Returns:
        Repository-relative paths, sorted.
    """
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.splitlines()
    named = [p for p in out if p == "evaluation.json" or p.endswith("/evaluation.json")]
    retest = [p for p in out if p.startswith("results/retest/")
              and p.endswith("-evaluation.json")]
    return sorted(named + retest)


def facts(path: str) -> dict[str, Any]:
    """Extract the classifying facts of one evaluation file.

    Args:
        path: Repository-relative path.

    Returns:
        A flat dictionary; ``error`` is set if the file cannot be parsed.
    """
    rec: dict[str, Any] = {"path": path}
    try:
        data = json.loads((ROOT / path).read_text())
    except (OSError, ValueError) as exc:
        rec["error"] = repr(exc)
        return rec
    if not isinstance(data, dict):
        rec["error"] = f"top level is {type(data).__name__}"
        return rec
    rec["top_keys"] = sorted(data.keys())
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    meta = data.get("_metadata") if isinstance(data.get("_metadata"), dict) else {}
    cli = meta.get("cli_args") if isinstance(meta.get("cli_args"), dict) else {}
    inf = meta.get("input_files") if isinstance(meta.get("input_files"), dict) else {}
    boot = meta.get("bootstrap") if isinstance(meta.get("bootstrap"), dict) else {}
    tc = summary.get("tile_classification")
    rec.update({
        "has_tile_classification": isinstance(tc, dict),
        "tile_join_summary": tc.get("tile_join") if isinstance(tc, dict) else None,
        "tile_withheld": bool(isinstance(tc, dict) and tc.get("withheld")),
        "tile_join_cli": cli.get("tile_join"),
        "count_table_join": (tc or {}).get("count_table_join") if isinstance(tc, dict) else None,
        "bounds": cli.get("bounds") or inf.get("bounds"),
        "ground_truth": cli.get("ground_truth") or inf.get("ground_truth"),
        "detections": cli.get("detections") or inf.get("detections"),
        "detections_dir": cli.get("detections_dir"),
        "batch": cli.get("batch"),
        "glob": cli.get("glob"),
        "label": summary.get("label"),
        "n_runs": summary.get("n_runs"),
        "n_per_run": len(data["per_run"]) if isinstance(data.get("per_run"), list) else None,
        "n_detections": summary.get("n_detections"),
        "has_buffers": isinstance(summary.get("buffers"), list),
        "boot_seed": boot.get("seed", cli.get("seed")),
        "boot_n": boot.get("n_iterations", cli.get("bootstrap")),
        "script_path": meta.get("script_path"),
        "script_commit": meta.get("script_git_commit"),
        "metadata_version": meta.get("metadata_version"),
        "has_metadata": bool(meta),
        "has_tile_join_withheld": "tile_join_withheld" in summary,
        "mcc_flag": cli.get("mcc"),
        "version": data.get("version"),
    })
    if not summary and "summary" not in data:
        rec["shape"] = "no-summary"
    return rec


def main() -> None:
    """Print one JSON line per tracked evaluation file."""
    for path in tracked_evaluations():
        sys.stdout.write(json.dumps(facts(path)) + "\n")


if __name__ == "__main__":
    main()
