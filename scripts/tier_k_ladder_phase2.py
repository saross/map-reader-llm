#!/usr/bin/env python3
"""
Run the board's tile-swap instrument over the gold-standard K ladders
====================================================================

Description:
    `results/k-ladder-2026-09-12/findings.md` § 6.1 records that ruling R2's
    pairwise permutation testing was **not run** in Phase 1, names the one-line
    command that would run it for the gold-standard stride ladder, and explains
    why the seven 55-map ladders cannot go through the same instrument (their
    cells were scored by `compute_corrected_f1_multi_buffer.py`, which writes no
    `cli_args`, against an extended ground truth the tile-swap would not
    rebuild). That choice was put back to the PI and is still pending.

    This script closes the gold-standard half of that gap, and only that half:

    * it runs `scripts/era1_leaderboard_tiering.py` — round-robin tile-swap
      micro-F1 permutation, 10,000 permutations, seed 42, Benjamini-Hochberg
      q = 0.05, greedy-clique tiers, on the board frame's 487 tiles — over the
      **gold-standard ladders only**;
    * the ladders are the Phase-1 stride-A ladder (the § 6.1 command, run
      verbatim) and the fourteen four-rung ladders Phase 2 completed, each at
      its sweep-optimal operating point;
    * **no 55-map ladder is touched.** The instrument ruling is pending and
      this run does not pre-empt it.

    The instrument selects its board from an analysis row's
    ``conditions_compared``. Rather than author a row in the register — which
    would state a result this run is not authorised to state — each ladder gets
    a **scratch** input pair under ``tiering-input/<slug>/``, holding a copy of
    the register with one unsigned placeholder analysis whose ``outcome`` says
    it is a tiering input. That is the pattern Phase 1 established for
    ``tiering-input/gs-stride-a/``, reused unchanged.

Usage::

    python scripts/tier_k_ladder_phase2.py prepare
    python scripts/tier_k_ladder_phase2.py run --workers 6
    python scripts/tier_k_ladder_phase2.py collect

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.score_k_ladder_phase2_rungs import (  # noqa: E402
    BOARD_BOUNDS,
    GROUND_TRUTH,
    PHASE2,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

LADDER_ROOT = BASE_DIR / "results" / "k-ladder-2026-09-12"
TIERING_INPUT = LADDER_ROOT / "tiering-input"
TIERING_OUT = LADDER_ROOT / "tiering"
SUMMARY_JSON = PHASE2 / "tiering-summary.json"

RUN_CONDITIONS = BASE_DIR / "results" / "run-conditions.json"
RUN_ANALYSES = BASE_DIR / "results" / "run-analyses.json"

N_PERMUTATIONS = 10_000
SEED = 42

#: The Phase-1 gold-standard stride ladder, whose input pair is already
#: committed and whose command findings.md § 6.1 quotes.
GS_STRIDE_A = {
    "slug": "gs-stride-a",
    "analysis_id": "k-ladder-gs-stride-a-2026-09-12",
    "family": "GS stride A (g384 ov128), exact re-verification",
    "prebuilt": True,
}


def slugify(pool: str) -> str:
    """Turn a proposer-pool slug into a directory-safe ladder slug."""
    return pool.replace(".", "-").replace("_", "-").lower()


def phase2_ladders() -> list[dict[str, Any]]:
    """Return the Phase 2 ladders that have four scored opmax rungs.

    A ladder with fewer than three rungs is skipped: the instrument needs at
    least three cells for a tiering to say anything, and the review's bar is
    three of {1, 3, 5, 10} (`inventory.md` § 2).
    """
    with open(PHASE2 / "ladders.json") as handle:
        payload = json.load(handle)

    ladders: list[dict[str, Any]] = []
    for ladder in payload["ladders"]:
        refs: list[str] = []
        for rung in ladder["rungs"]:
            opmax = rung.get("opmax") or {}
            if opmax.get("f1_20") is None:
                continue
            # K = 1 and K = 3 are this run's rows; K = 5 and K = 10 are the
            # committed board cells (or, for the 3.7 family, cells derived at
            # US$0 and therefore NOT in the register — those cannot be tiered
            # by an instrument that resolves conditions through the register.
            condition_id = rung.get("condition_id")
            if condition_id is None and rung["source"].startswith("phase-2"):
                condition_id = (
                    f"{ladder['run_id']}::"
                    f"{rung['labels']['opmax']}"
                )
            if condition_id is None:
                continue
            refs.append(condition_id)
        if len(refs) < 3:
            logger.warning(
                "%s: only %d register-resolvable opmax rung(s) — not tiered",
                ladder["family"],
                len(refs),
            )
            continue
        ladders.append(
            {
                "slug": f"phase2-{slugify(ladder['proposer_pool'])}",
                "analysis_id": (
                    f"k-ladder-phase2-{slugify(ladder['proposer_pool'])}"
                    "-2026-09-12"
                ),
                "family": ladder["family"],
                "refs": refs,
                "prebuilt": False,
            }
        )
    return ladders


def write_input(ladder: dict[str, Any]) -> Path:
    """Write a scratch (conditions, analyses) pair for one ladder."""
    target = TIERING_INPUT / ladder["slug"]
    target.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(RUN_CONDITIONS, target / "run-conditions.json")

    with open(RUN_ANALYSES) as handle:
        analyses = json.load(handle)
    analyses["analyses"] = [
        analysis
        for analysis in analyses["analyses"]
        if analysis["analysis_id"] != ladder["analysis_id"]
    ]
    analyses["analyses"].append(
        {
            "analysis_id": ladder["analysis_id"],
            "type": "comparison",
            "_note": (
                "SCRATCH TIERING INPUT — not a registered analysis. Written by "
                "scripts/tier_k_ladder_phase2.py so "
                "scripts/era1_leaderboard_tiering.py can resolve this ladder's "
                "rungs; the register itself carries no such row, because this "
                "run is not authorised to author or sign an analysis "
                f"(K-ladder Phase 2). Ladder: {ladder['family']}."
            ),
            "conditions_compared": ladder["refs"],
            "hypothesis_refs": None,
            "preregistered": "post-hoc",
            "deviations": None,
            "predicted_outcome": None,
            "outcome": "PENDING: this is a tiering input, not a registered result",
            "tie_set": None,
            "paper_section": None,
            "working_notes_obs": None,
            "output_path": (
                f"results/k-ladder-2026-09-12/tiering/{ladder['slug']}"
            ),
            "manually_verified_at": None,
        }
    )
    with open(target / "run-analyses.json", "w") as handle:
        json.dump(analyses, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    return target


def command_for(ladder: dict[str, Any]) -> list[str]:
    """Build the tiering command for one ladder."""
    target = TIERING_INPUT / ladder["slug"]
    return [
        sys.executable,
        "scripts/era1_leaderboard_tiering.py",
        "--analysis-id",
        ladder["analysis_id"],
        "--conditions",
        str((target / "run-conditions.json").relative_to(BASE_DIR)),
        "--analyses",
        str((target / "run-analyses.json").relative_to(BASE_DIR)),
        "--ground-truth",
        GROUND_TRUTH,
        "--bounds",
        BOARD_BOUNDS,
        "--output-dir",
        str((TIERING_OUT / ladder["slug"]).relative_to(BASE_DIR)),
        "--n-permutations",
        str(N_PERMUTATIONS),
        "--seed",
        str(SEED),
    ]


def all_ladders() -> list[dict[str, Any]]:
    """The gold-standard ladders to tier: stride A plus the Phase 2 fourteen."""
    return [GS_STRIDE_A, *phase2_ladders()]


def cmd_prepare(args: argparse.Namespace) -> None:
    """Write the scratch input pairs and print the commands."""
    ladders = all_ladders()
    lines: list[str] = []
    for ladder in ladders:
        if not ladder["prebuilt"]:
            write_input(ladder)
        else:
            logger.info(
                "%s: input pair already committed (Phase 1) — reused as is",
                ladder["slug"],
            )
        lines.append(" ".join(command_for(ladder)).replace(sys.executable, "python"))
        logger.info(
            "%-44s %s  (%d rung(s))",
            ladder["slug"],
            ladder["family"],
            len(ladder.get("refs", [])) or 4,
        )
    jobs = PHASE2 / "tiering-jobs.txt"
    with open(jobs, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    logger.info(
        "%d ladder(s); commands -> %s", len(ladders), jobs.relative_to(BASE_DIR)
    )


def cmd_run(args: argparse.Namespace) -> None:
    """Run every ladder's tiering, in parallel processes."""
    ladders = all_ladders()

    def run_one(ladder: dict[str, Any]) -> tuple[str, int, str]:
        completed = subprocess.run(
            command_for(ladder),
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        tail = (completed.stdout[-800:] + completed.stderr[-1600:]).strip()
        return ladder["slug"], completed.returncode, tail

    failures = 0
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.workers
    ) as pool:
        for slug, code, tail in pool.map(run_one, ladders):
            if code == 0:
                logger.info("%-44s OK", slug)
            else:
                failures += 1
                logger.error("%-44s FAILED (%d)\n%s", slug, code, tail)
    if failures:
        logger.error("%d ladder(s) failed to tier", failures)
        sys.exit(9)


def cmd_collect(args: argparse.Namespace) -> None:
    """Read every tiering result into one summary JSON."""
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for ladder in all_ladders():
        path = TIERING_OUT / ladder["slug"] / "tiering_20m.json"
        if not path.exists():
            missing.append(str(path.relative_to(BASE_DIR)))
            continue
        with open(path) as handle:
            result = json.load(handle)
        cells = result.get("cells") or result.get("conditions") or []
        rows.append(
            {
                "slug": ladder["slug"],
                "family": ladder["family"],
                "analysis_id": ladder["analysis_id"],
                "n_cells": len(cells),
                "n_tiers": result.get("n_tiers")
                or (
                    len({cell.get("tier") for cell in cells})
                    if cells
                    else None
                ),
                "n_pairs": result.get("n_pairs"),
                "n_significant_pairs": result.get("n_significant_pairs"),
                "tie_set": result.get("tie_set"),
                "cells": [
                    {
                        key: cell.get(key)
                        for key in ("condition_id", "label", "f1", "tier")
                        if key in cell
                    }
                    for cell in cells
                ],
                "result_path": str(path.relative_to(BASE_DIR)),
            }
        )
        logger.info(
            "%-44s cells=%d tiers=%s significant=%s/%s",
            ladder["slug"],
            len(cells),
            rows[-1]["n_tiers"],
            rows[-1]["n_significant_pairs"],
            rows[-1]["n_pairs"],
        )

    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "script": "scripts/tier_k_ladder_phase2.py",
                "script_version": __version__,
                "instrument": (
                    "scripts/era1_leaderboard_tiering.py — round-robin "
                    "tile-swap micro-F1 permutation, BH q = 0.05, "
                    "greedy-clique tiers"
                ),
                "n_permutations": N_PERMUTATIONS,
                "seed": SEED,
                "bounds": BOARD_BOUNDS,
                "ground_truth": GROUND_TRUTH,
                "scope_note": (
                    "GOLD-STANDARD LADDERS ONLY. The seven 55-map ladders are "
                    "deliberately not tiered with this instrument: the "
                    "instrument ruling is pending with the PI "
                    "(findings.md § 6.1)"
                ),
                "n_ladders": len(rows),
                "n_missing": len(missing),
                "missing": missing,
                "ladders": rows,
            },
            handle,
            indent=2,
        )
        handle.write("\n")
    logger.info("-> %s", SUMMARY_JSON.relative_to(BASE_DIR))


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Run the board's tile-swap instrument over the gold-standard K "
            "ladders (US$0, no API calls; 55-map ladders excluded by design)"
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.set_defaults(func=cmd_prepare)

    run = subparsers.add_parser("run")
    run.add_argument("--workers", type=int, default=6)
    run.set_defaults(func=cmd_run)

    collect = subparsers.add_parser("collect")
    collect.set_defaults(func=cmd_collect)

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    args.func(args)


if __name__ == "__main__":
    main()
