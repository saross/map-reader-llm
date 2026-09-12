#!/usr/bin/env python3
"""
Sweep, materialise and score the K-ladder Phase 2 rungs (US$0, no API calls)
===========================================================================

Description:
    Step 4 of the K-ladder Phase 2 run. For each rung whose verifier pass has
    landed, this script reproduces the family's registered recipe:

    1. **Sweep** the (vote_t, prob_t) grid with
       ``scripts/sweep_f1_greedy_pv.py`` on BOTH gold-standard 487-tile
       frames — the Era-2 frame ``full_evaluation_bounds.geojson`` the
       committed ``-opmax`` cells' optima were selected on, and the board frame
       ``era2_b_intersection_bounds.geojson`` that ruling R2 tiers on. Running
       both costs nothing and settles, per rung, whether the two frames' optima
       coincide (the board's note says they do for twenty of the twenty-one
       committed pv cells).
    2. **Pick two operating points**: the sweep-optimal (``-opmax``, argmax of
       F1@20 on the board frame, per R2) and the **carried** point
       (prob_t fixed, vote_t = K), which R2 asks for as the transfer-tax
       column.
    3. **Materialise** each point with ``scripts/materialise_pv_geojson.py``
       (union feature *i* joined to ``probabilities.json`` key
       ``candidate_{i:05d}``; keep where ``vote_count >= vote_t`` and
       ``mound_probability >= prob_t``).
    4. **Emit one evaluation job per materialised cell** — 14 buffers, the
       curator reference, the board frame, 10,000 BCa draws, seed 42, MCC —
       into a jobs file for ``xargs -P``, because 10,000-draw bootstraps over
       56 cells are worth parallelising.
    5. **Collect** the finished evaluations into a scores JSON the findings
       document and the deltas report are written from.

    Tie-break rule for the argmax, stated because the project has never fixed
    one: highest F1@20, then the LOWEST ``vote_t``, then the LOWEST ``prob_t``
    — the least-thresholded of the tied points, so a tie resolves towards
    recall rather than towards whichever row the file happens to end on.

Usage::

    # Sweep + materialise + write the evaluation jobs file
    python scripts/score_k_ladder_phase2_rungs.py prepare --tier A

    # Then, on sapphire:
    xargs -P 8 -I CMD bash -c CMD \
        < results/k-ladder-2026-09-12/phase2/score-jobs.txt

    # Read the finished evaluations back
    python scripts/score_k_ladder_phase2_rungs.py collect

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.run_k_ladder_phase2_verifier import (  # noqa: E402
    LEDGER_JSON,
    UNIONS_JSON,
    resolve_paths,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

PHASE2_DIR = BASE_DIR / "results" / "k-ladder-2026-09-12" / "phase2"
MATERIALISED_DIR = PHASE2_DIR / "materialised"
CELLS_DIR = PHASE2_DIR / "cells"
JOBS_FILE = PHASE2_DIR / "score-jobs.txt"
POINTS_JSON = PHASE2_DIR / "operating-points.json"
SCORES_JSON = PHASE2_DIR / "scores.json"

GROUND_TRUTH = "inputs/vectors/references/mounds-reference.geojson"
#: The board frame R2 tiers on (`era2-b-487`).
BOARD_BOUNDS = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
#: The Era-2 frame the committed `-opmax` optima were selected on.
ERA2_BOUNDS = "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

BUFFERS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]
SWEEP_BUFFERS = [20, 30, 40, 50]
BOOTSTRAP = 10000
SEED = 42
HEADLINE_BUFFER = 20

#: Carried prob_t by run: the point committed before this evaluation. The
#: Gemini 3 families carry 0.15 (R2); the 3.7 GS screen's committed K = 5 and
#: K = 10 rungs carry 0.10, so its new rungs carry 0.10 too or the ladder
#: would not be a ladder.
CARRIED_PROB_BY_RUN: dict[str, float] = {
    "pv-diag-384": 0.15,
    "gemini37-screen-2026-08-28": 0.10,
}

#: Condition label stems for the 3.7 family follow its own convention
#: (`g37-text-k<K>-verified-carried-p0.10-k<K>`), the others the pv-diag-384
#: convention (`<stem>-n<K>-opmax`).
def condition_labels(rung: dict[str, Any], carried_prob: float) -> dict[str, str]:
    """Return the ``-opmax`` and carried condition labels for one rung.

    Args:
        rung: One rung of ``unions.json``.
        carried_prob: The family's carried probability threshold.

    Returns:
        ``{"opmax": label, "carried": label}``.
    """
    k = rung["n_passes"]
    if rung["run_id"] == "gemini37-screen-2026-08-28":
        return {
            "opmax": f"g37-text-k{k}-verified-opmax",
            "carried": (
                f"g37-text-k{k}-verified-carried-p{carried_prob:.2f}-k{k}"
            ),
        }
    return {
        "opmax": f"{rung['label_stem']}-n{k}-opmax",
        "carried": (
            f"{rung['label_stem']}-n{k}-carried-p{carried_prob:.2f}-k{k}"
        ),
    }


def cell_dir_name(run_id: str, label: str) -> str:
    """Board convention: ``<run_id>__<label with dots as underscores>``."""
    return f"{run_id}__{label.replace('.', '_')}"


def selected_rungs(
    tiers: list[str] | None, rows: list[int] | None
) -> list[dict[str, Any]]:
    """Return the rungs whose verifier pass has landed, tier-ordered."""
    with open(UNIONS_JSON) as handle:
        rungs = [
            rung
            for rung in json.load(handle)["rungs"]
            if rung["verdict"] == "OK"
        ]
    if tiers:
        rungs = [rung for rung in rungs if rung["tier"] in set(tiers)]
    if rows:
        rungs = [rung for rung in rungs if rung["row"] in set(rows)]
    rungs.sort(key=lambda rung: ("ABCD".index(rung["tier"]), rung["row"]))

    kept = []
    for rung in rungs:
        paths = resolve_paths(rung)
        probabilities = BASE_DIR / paths["verify_dir"] / "probabilities.json"
        if not probabilities.exists():
            logger.warning(
                "row %d: no probabilities.json yet (%s) — skipping",
                rung["row"],
                paths["verify_dir"],
            )
            continue
        rung = dict(rung)
        rung["paths"] = paths
        kept.append(rung)
    return kept


def run_sweep(rung: dict[str, Any], *, bounds: str, out_name: str) -> Path:
    """Run ``sweep_f1_greedy_pv.py`` for one rung on one frame.

    Args:
        rung: A rung with its resolved ``paths``.
        bounds: Evaluation bounds GeoJSON, relative to the repository root.
        out_name: Filename for the sweep inside the verify directory.

    Returns:
        Path to the written sweep JSON.

    Raises:
        SystemExit: if the sweep fails.
    """
    paths = rung["paths"]
    output = BASE_DIR / paths["verify_dir"] / out_name
    command = [
        sys.executable,
        "scripts/sweep_f1_greedy_pv.py",
        "--config",
        f"{rung['pool_slug']}-n{rung['n_passes']}",
        "--crops-dir",
        paths["crops_dir"],
        "--verified-dir",
        paths["verify_dir"],
        "--output",
        str(output.relative_to(BASE_DIR)),
        "--bounds",
        bounds,
        "--buffer-m",
        *[str(buffer) for buffer in SWEEP_BUFFERS],
    ]
    completed = subprocess.run(
        command, cwd=BASE_DIR, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        logger.error(
            "sweep failed for row %d on %s:\n%s",
            rung["row"],
            bounds,
            completed.stderr[-2000:],
        )
        sys.exit(5)
    return output


def argmax_at_headline(sweep_path: Path) -> dict[str, Any]:
    """Pick the F1@20 argmax of a sweep, with the documented tie-break.

    Args:
        sweep_path: A ``sweep_2d.json`` (a bare list of rows).

    Returns:
        The winning row.
    """
    with open(sweep_path) as handle:
        rows = [
            row
            for row in json.load(handle)
            if row["buffer_m"] == HEADLINE_BUFFER
        ]
    best = max(rows, key=lambda row: (row["f1"], -row["vote_t"], -row["prob_t"]))
    ties = [
        row
        for row in rows
        if row["f1"] == best["f1"]
        and (row["vote_t"], row["prob_t"]) != (best["vote_t"], best["prob_t"])
    ]
    return {**best, "n_ties": len(ties)}


def materialise(
    rung: dict[str, Any], *, vote_t: int, prob_t: float, output: Path
) -> int:
    """Materialise one operating point's detections.

    Returns:
        The feature count of the written GeoJSON.

    Raises:
        SystemExit: if materialisation fails.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "scripts/materialise_pv_geojson.py",
        "--consensus",
        f"{rung['consensus_dir']}/consensus_t1.geojson",
        "--probabilities",
        f"{rung['paths']['verify_dir']}/probabilities.json",
        "--vote-t",
        str(vote_t),
        "--prob-t",
        str(prob_t),
        "--output",
        str(output.relative_to(BASE_DIR)),
    ]
    completed = subprocess.run(
        command, cwd=BASE_DIR, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        logger.error(
            "materialise failed for row %d at (%s, %s):\n%s",
            rung["row"],
            vote_t,
            prob_t,
            completed.stderr[-2000:],
        )
        sys.exit(6)
    with open(output) as handle:
        return len(json.load(handle).get("features", []))


def eval_command(detections: Path, cell: str, label: str) -> str:
    """Build the board-frame evaluation command line for one cell."""
    return " ".join(
        [
            "python",
            "scripts/evaluate_detections.py",
            "--detections",
            str(detections.relative_to(BASE_DIR)),
            "--ground-truth",
            GROUND_TRUTH,
            "--bounds",
            BOARD_BOUNDS,
            "--buffers",
            *[str(buffer) for buffer in BUFFERS],
            "--bootstrap",
            str(BOOTSTRAP),
            "--seed",
            str(SEED),
            "--mcc",
            "--output-dir",
            f"results/k-ladder-2026-09-12/phase2/cells/{cell}",
            "--label",
            label,
        ]
    )


def cmd_prepare(args: argparse.Namespace) -> None:
    """Sweep, choose operating points, materialise, and write the jobs file."""
    rungs = selected_rungs(args.tier, args.row)
    logger.info("%d rung(s) with a verifier output", len(rungs))

    points: list[dict[str, Any]] = []
    jobs: list[str] = []

    for rung in rungs:
        carried_prob = CARRIED_PROB_BY_RUN[rung["run_id"]]
        labels = condition_labels(rung, carried_prob)

        board_sweep = run_sweep(
            rung, bounds=BOARD_BOUNDS, out_name="sweep_2d_era2b.json"
        )
        era2_sweep = run_sweep(
            rung, bounds=ERA2_BOUNDS, out_name="sweep_2d.json"
        )
        board_best = argmax_at_headline(board_sweep)
        era2_best = argmax_at_headline(era2_sweep)
        frames_agree = (board_best["vote_t"], board_best["prob_t"]) == (
            era2_best["vote_t"],
            era2_best["prob_t"],
        )

        entry: dict[str, Any] = {
            "row": rung["row"],
            "tier": rung["tier"],
            "family": rung["family"],
            "run_id": rung["run_id"],
            "pool_slug": rung["pool_slug"],
            "n_passes": rung["n_passes"],
            "candidates": rung["measured_candidates"],
            "verifier_stage": rung["paths"]["verifier_stage"],
            "verify_dir": rung["paths"]["verify_dir"],
            "union": f"{rung['consensus_dir']}/consensus_t1.geojson",
            "sweep_board_frame": str(board_sweep.relative_to(BASE_DIR)),
            "sweep_era2_frame": str(era2_sweep.relative_to(BASE_DIR)),
            "opmax_selected_on": "era2-b-487 (board frame, per R2)",
            "opmax": {
                "vote_t": board_best["vote_t"],
                "prob_t": board_best["prob_t"],
                "sweep_f1_20": board_best["f1"],
                "sweep_n": board_best["n"],
                "n_ties_at_argmax": board_best["n_ties"],
            },
            "opmax_on_era2_frame": {
                "vote_t": era2_best["vote_t"],
                "prob_t": era2_best["prob_t"],
                "sweep_f1_20": era2_best["f1"],
                "sweep_n": era2_best["n"],
            },
            "frames_agree_on_argmax": frames_agree,
            "carried": {
                "vote_t": rung["n_passes"],
                "prob_t": carried_prob,
            },
            "labels": labels,
        }

        for point in ("opmax", "carried"):
            label = labels[point]
            detections = MATERIALISED_DIR / f"{label}.geojson"
            count = materialise(
                rung,
                vote_t=entry[point]["vote_t"],
                prob_t=entry[point]["prob_t"],
                output=detections,
            )
            cell = cell_dir_name(rung["run_id"], label)
            entry[point]["detections"] = str(detections.relative_to(BASE_DIR))
            entry[point]["n_detections"] = count
            entry[point]["cell"] = cell
            entry[point]["eval_path"] = (
                f"results/k-ladder-2026-09-12/phase2/cells/{cell}/"
                "evaluation.json"
            )
            jobs.append(eval_command(detections, cell, label))

        if not frames_agree:
            logger.warning(
                "row %d: the two 487-tile frames disagree on the argmax — "
                "board (%d, %.2f) F1 %.4f vs Era-2 (%d, %.2f) F1 %.4f. "
                "R2 says tier on the board frame, so the board frame's point "
                "is used and the disagreement is reported.",
                rung["row"],
                board_best["vote_t"],
                board_best["prob_t"],
                board_best["f1"],
                era2_best["vote_t"],
                era2_best["prob_t"],
                era2_best["f1"],
            )
        if board_best["n_ties"]:
            logger.warning(
                "row %d: %d point(s) tie with the argmax at F1 %.4f; the "
                "tie-break (lowest vote_t, then lowest prob_t) chose "
                "(%d, %.2f)",
                rung["row"],
                board_best["n_ties"],
                board_best["f1"],
                board_best["vote_t"],
                board_best["prob_t"],
            )

        logger.info(
            "row %2d %-40s K=%d  opmax (%d, %.2f) n=%d  carried (%d, %.2f) "
            "n=%d  frames agree: %s",
            rung["row"],
            rung["family"],
            rung["n_passes"],
            entry["opmax"]["vote_t"],
            entry["opmax"]["prob_t"],
            entry["opmax"]["n_detections"],
            entry["carried"]["vote_t"],
            entry["carried"]["prob_t"],
            entry["carried"]["n_detections"],
            frames_agree,
        )
        points.append(entry)

    PHASE2_DIR.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, Any]] = []
    if POINTS_JSON.exists() and not args.fresh:
        with open(POINTS_JSON) as handle:
            existing = [
                entry
                for entry in json.load(handle)["rungs"]
                if entry["row"] not in {point["row"] for point in points}
            ]
    merged = sorted(existing + points, key=lambda entry: entry["row"])
    with open(POINTS_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "script": "scripts/score_k_ladder_phase2_rungs.py",
                "script_version": __version__,
                "headline_buffer_m": HEADLINE_BUFFER,
                "tie_break": (
                    "highest F1@20, then lowest vote_t, then lowest prob_t"
                ),
                "board_bounds": BOARD_BOUNDS,
                "era2_bounds": ERA2_BOUNDS,
                "rungs": merged,
            },
            handle,
            indent=2,
        )
        handle.write("\n")

    with open(JOBS_FILE, "w") as handle:
        handle.write("\n".join(jobs) + "\n")
    logger.info(
        "%d evaluation job(s) -> %s ; operating points -> %s",
        len(jobs),
        JOBS_FILE.relative_to(BASE_DIR),
        POINTS_JSON.relative_to(BASE_DIR),
    )


def cmd_collect(args: argparse.Namespace) -> None:
    """Read the finished board-frame evaluations into one scores JSON."""
    with open(POINTS_JSON) as handle:
        points = json.load(handle)

    ledger: dict[str, Any] = {"rungs": {}}
    if LEDGER_JSON.exists():
        with open(LEDGER_JSON) as handle:
            ledger = json.load(handle)
    spend_by_row = {
        entry["row"]: entry for entry in ledger.get("rungs", {}).values()
    }

    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for rung in points["rungs"]:
        record: dict[str, Any] = {
            key: rung[key]
            for key in (
                "row",
                "tier",
                "family",
                "run_id",
                "pool_slug",
                "n_passes",
                "candidates",
                "verifier_stage",
                "frames_agree_on_argmax",
                "labels",
            )
        }
        spend = spend_by_row.get(rung["row"], {})
        record["verifier_flex_usd"] = spend.get("flex_usd")
        record["verifier_calls"] = spend.get("items_processed")
        record["verifier_wall_seconds"] = spend.get("wall_seconds")

        for point in ("opmax", "carried"):
            eval_path = BASE_DIR / rung[point]["eval_path"]
            if not eval_path.exists():
                missing.append(rung[point]["eval_path"])
                continue
            with open(eval_path) as handle:
                evaluation = json.load(handle)
            summary = evaluation["summary"]
            buffers = {
                int(entry["buffer_metres"]): entry
                for entry in summary["buffers"]
            }
            headline = buffers[HEADLINE_BUFFER]
            mcc = (summary.get("tile_classification") or {}).get("mcc") or {}
            record[point] = {
                "vote_t": rung[point]["vote_t"],
                "prob_t": rung[point]["prob_t"],
                "n_detections": rung[point]["n_detections"],
                "f1_20": headline.get("f1"),
                "precision_20": headline.get("precision"),
                "recall_20": headline.get("recall"),
                "f1_20_ci": headline.get("f1_ci"),
                "tile_mcc": mcc.get("point"),
                "tile_mcc_ci": [mcc.get("ci_lower"), mcc.get("ci_upper")]
                if mcc
                else None,
                "eval_path": rung[point]["eval_path"],
                "detections": rung[point]["detections"],
            }
        rows.append(record)

    with open(SCORES_JSON, "w") as handle:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "script": "scripts/score_k_ladder_phase2_rungs.py",
                "script_version": __version__,
                "recipe": {
                    "bounds": BOARD_BOUNDS,
                    "ground_truth": GROUND_TRUTH,
                    "buffers": BUFFERS,
                    "headline_buffer_m": HEADLINE_BUFFER,
                    "bootstrap": BOOTSTRAP,
                    "seed": SEED,
                    "mcc": True,
                },
                "n_rungs": len(rows),
                "n_missing_evaluations": len(missing),
                "missing_evaluations": missing,
                "rungs": rows,
            },
            handle,
            indent=2,
        )
        handle.write("\n")

    logger.info(
        "collected %d rung(s); %d evaluation(s) still missing -> %s",
        len(rows),
        len(missing),
        SCORES_JSON.relative_to(BASE_DIR),
    )
    if missing and args.strict:
        sys.exit(7)


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Sweep, materialise and score the K-ladder Phase 2 rungs (US$0)"
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser(
        "prepare", help="Sweep, pick operating points, materialise, write jobs"
    )
    prepare.add_argument("--tier", action="append", choices=["A", "B", "C", "D"])
    prepare.add_argument("--row", action="append", type=int)
    prepare.add_argument(
        "--fresh",
        action="store_true",
        help="Discard operating points from previous invocations",
    )
    prepare.set_defaults(func=cmd_prepare)

    collect = subparsers.add_parser(
        "collect", help="Read the finished evaluations into scores.json"
    )
    collect.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any evaluation is missing",
    )
    collect.set_defaults(func=cmd_collect)

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    args.func(args)


if __name__ == "__main__":
    main()
