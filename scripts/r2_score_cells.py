#!/usr/bin/env python3
"""
Score the r2 recompute chain's cells with one engine, resumably.

Steps 3 and 4b of ``planning/reference-revision-2026-09-06.md`` produce
40 of the chain's 41 evaluation files, and until Session 149-b there was
no driver for either: the r1 stage-2 scoring was an ad-hoc shell loop
(audit-2 MAJOR 7). This script is that driver. It runs
``scripts/evaluate_detections.py`` -- the IM-k4 template, the chain's
single engine -- once per cell, with the exact recipe every committed
evaluation on this corpus used (14 buffers, ``--mcc``, tile-level BCa
bootstrap 10,000 / seed 42), against reference revision r2.

Two stages, two homes (contract § 4a § 1 (3)):

* ``--stage fixed`` (step 3): the nine fixed-detection cells -- the
  eight leaderboard cells of ``build_55map_leaderboard.NAMES`` plus IM-k4,
  i.e. ``final_board_build.COMMITTED_CARRIED`` -- into the r2 SCORING home
  ``results/55maps-r2-ref-2026-09-06/<cell>/``. The set is derived from
  those two tables and asserted equal to the contract's nine.
* ``--stage board`` (step 4b): every materialised cell of the r2 board's
  ``cells_manifest.json`` (``committed_eval: false``) into the r2 BOARD
  home ``results/55map-final-board-r2-2026-09-06/cells/<label>/`` --
  exactly where ``final_board_build.py --reference r2`` reads. Runs after
  4a (sweep) and 4c (N = 3 carried), which write those detections.

Resumable: a cell with an ``evaluation.json`` is skipped, so a halted
stage resumes; the plan and its counts print before anything runs
(``--dry-run`` stops there). Provenance: ``--require-clean-inputs`` is ON
by default, so an evaluation whose detections are uncommitted refuses to
score -- commit the 4a/4c outputs first (they are gated, deterministic
artefacts and are committed by policy anyway). ``--allow-dirty`` drops the
flag for a deliberate exception. After each run the written evaluation
is checked: its ground truth is the r2 file, every input is ``clean`` or
``ignored``, and its 50 m row exists.

Usage (sapphire)::

    python scripts/r2_score_cells.py --stage fixed --dry-run
    python scripts/r2_score_cells.py --stage fixed --jobs 3 --workers 4
    python scripts/r2_score_cells.py --stage board --jobs 4 --workers 2

Zero API. Each cell takes minutes on sapphire (the 10,000-draw tile
bootstrap dominates); ``--jobs`` runs cells concurrently, ``--workers``
is the engine's own per-cell parallelism. The pre-flight of Session 149-b
reproduced a workers=1 evaluation exactly with workers=8, so neither
setting changes a number.

Created: 2026-09-07 (Session 149-b)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_55map_leaderboard import (  # noqa: E402
    BOARD_HOME_BY_REFERENCE,
    NAMES,
    R2_REFERENCE,
)
from scripts.final_board_build import COMMITTED_CARRIED  # noqa: E402
from scripts.register_standardised_gt_conditions import (  # noqa: E402
    OUT_BASE_BY_VINTAGE,
)
from scripts.score_55maps_standardised_reference import CELLS as TRACK2_CELLS  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ENGINE = PROJECT_ROOT / "scripts/evaluate_detections.py"
BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
BUFFERS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]
BOOTSTRAP = 10_000
SEED = 42
HEADLINE_M = 50
SCORING_HOME = OUT_BASE_BY_VINTAGE["r2"]
BOARD_HOME = BOARD_HOME_BY_REFERENCE["r2"]

#: The contract's nine fixed-detection cells (§ 4 step 3). Asserted against
#: the derived set at run time so the prose cannot drift from the code.
CONTRACT_FIXED = {"IM-k3", "IM-k4", "TH7-k3", "TH7-k4", "T03-k3", "T03-k4",
                  "TM-k3", "TM-k4", "TM-n10-k5"}


@dataclass
class Job:
    """One cell to score."""

    label: str
    detections: Path
    out_dir: Path
    eval_label: str

    @property
    def done(self) -> bool:
        return (self.out_dir / "evaluation.json").exists()


def fixed_jobs() -> list[Job]:
    """Step 3: the nine fixed-detection cells, derived from the two tables."""
    dets: dict[str, str] = {}
    for cell in TRACK2_CELLS:
        dets[cell["label"]] = cell["det"]
    for label, det, _ev in COMMITTED_CARRIED:
        dets.setdefault(label, det)
    leaderboard = {name.split(" ")[0] for name in NAMES.values()}
    wanted = leaderboard | {label for label, _d, _e in COMMITTED_CARRIED}
    if wanted != CONTRACT_FIXED:
        raise RuntimeError(f"derived fixed set {sorted(wanted)} != contract "
                           f"{sorted(CONTRACT_FIXED)} -- amend one or the other")
    missing = wanted - set(dets)
    if missing:
        raise RuntimeError(f"no detections path known for {sorted(missing)}")
    return [Job(label, PROJECT_ROOT / dets[label], SCORING_HOME / label,
                f"{label}-r2-gt") for label in sorted(wanted)]


def board_jobs() -> list[Job]:
    """Step 4b: every materialised cell of the r2 board manifest."""
    manifest_path = BOARD_HOME / "cells_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"{manifest_path} does not exist: "
                         f"run steps 4a (final_board_sweeps.py --reference r2) and 4c "
                         f"(final_board_n3_carried.py --reference r2) first")
    cells = json.loads(manifest_path.read_text())["cells"]
    jobs = [Job(m["label"], PROJECT_ROOT / m["det"], BOARD_HOME / "cells" / m["label"],
                f"{m['label']}-final-board-r2")
            for m in cells if not m.get("committed_eval")]
    absent = [j.label for j in jobs if not j.detections.exists()]
    if absent:
        raise SystemExit(f"manifest cells without detections on disk: {absent}")
    return jobs


def engine_command(job: Job, workers: int, require_clean: bool) -> list[str]:
    """The IM-k4 template, verbatim, against r2."""
    cmd = [sys.executable, str(ENGINE),
           "--detections", str(job.detections.relative_to(PROJECT_ROOT)),
           "--buffers", *map(str, BUFFERS),
           "--ground-truth", str(R2_REFERENCE.relative_to(PROJECT_ROOT)),
           "--bounds", str(BOUNDS.relative_to(PROJECT_ROOT)),
           "--bootstrap", str(BOOTSTRAP), "--seed", str(SEED),
           "--output-dir", str(job.out_dir.relative_to(PROJECT_ROOT)),
           "--label", job.eval_label, "--mcc", "--workers", str(workers)]
    if require_clean:
        cmd.append("--require-clean-inputs")
    return cmd


def check_output(job: Job) -> str:
    """Post-run gate on the written evaluation; returns the 50 m summary."""
    ev = json.loads((job.out_dir / "evaluation.json").read_text())
    meta = ev["_metadata"]
    gt = str((meta.get("input_files") or {}).get("ground_truth"))
    if Path(gt).name != R2_REFERENCE.name:
        raise RuntimeError(f"{job.label}: scored against {gt}, not r2")
    states = (meta.get("input_git_state") or {}).get("inputs") or {}
    dirty = {p: s for p, s in states.items() if s not in ("clean", "ignored")}
    if dirty:
        raise RuntimeError(f"{job.label}: inputs not clean at scoring time: {dirty}")
    row = next(b for b in ev["summary"]["buffers"] if b["buffer_metres"] == HEADLINE_M)
    mcc = ev["summary"].get("tile_classification", {}).get("mcc")
    mcc = mcc.get("point") if isinstance(mcc, dict) else mcc
    return (f"F1@50 {row['f1']:.4f} [{row['f1_ci_lower']:.4f}, {row['f1_ci_upper']:.4f}] "
            f"MCC {mcc} n={ev['summary']['n_detections']}")


def run_job(job: Job, workers: int, require_clean: bool) -> tuple[Job, str]:
    """Score one cell; raise on any failure."""
    job.out_dir.mkdir(parents=True, exist_ok=True)
    cmd = engine_command(job, workers, require_clean)
    log_path = job.out_dir / "score.log"
    with log_path.open("w", encoding="utf-8") as log:
        res = subprocess.run(cmd, cwd=PROJECT_ROOT, stdout=log, stderr=subprocess.STDOUT,
                             text=True, check=False)
    if res.returncode != 0:
        tail = log_path.read_text()[-1500:]
        raise RuntimeError(f"{job.label}: engine exit {res.returncode}\n{tail}")
    return job, check_output(job)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("fixed", "board"), required=True,
                    help="fixed = step 3 (scoring home); board = step 4b (board home).")
    ap.add_argument("--jobs", type=int, default=2, help="Cells scored concurrently.")
    ap.add_argument("--workers", type=int, default=1, help="Engine workers per cell.")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="Drop --require-clean-inputs (a deliberate exception; the "
                         "evaluation records the dirty state either way).")
    ap.add_argument("--dry-run", action="store_true", help="Print the plan and stop.")
    args = ap.parse_args()

    jobs = fixed_jobs() if args.stage == "fixed" else board_jobs()
    todo = [j for j in jobs if not j.done]
    logger.info("stage %s: %d cells in the derived set, %d already scored, %d to run",
                args.stage, len(jobs), len(jobs) - len(todo), len(todo))
    for j in jobs:
        logger.info("  %-22s %s  <- %s", j.label, "done" if j.done else "TODO",
                    j.detections.relative_to(PROJECT_ROOT))
    if args.dry_run or not todo:
        return 0

    failures = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run_job, j, args.workers, not args.allow_dirty): j
                   for j in todo}
        for fut in as_completed(futures):
            try:
                job, summary = fut.result()
                logger.info("scored %-22s %s", job.label, summary)
            except Exception as exc:  # noqa: BLE001 -- report every failure, then exit 1
                failures += 1
                logger.error("%s", exc)
    remaining = [j.label for j in jobs if not j.done]
    logger.info("stage %s: %d/%d evaluations present%s", args.stage,
                len(jobs) - len(remaining), len(jobs),
                f"; missing {remaining}" if remaining else "")
    return 1 if failures or remaining else 0


if __name__ == "__main__":
    sys.exit(main())
