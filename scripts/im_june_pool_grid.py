#!/usr/bin/env python3
"""
The June 2026 image pool's threshold-by-votes grid on the r2 reference.

Why this script exists
----------------------
The image 2x2 of September 2026 compared its rebuilt Gemini 3 image pool
against ``IM-k3`` — the single committed cell of the June 2026 image
generalisation run (``outputs/55maps-image-generalisation``), materialised at
one operating point (probability >= 0.15, votes >= 3). One point is not a
comparison: the rebuilt pool was swept over its whole achievable space and
then read at its oracle, so the June run was being judged at a point it never
chose while the September run was judged at its best.

This script builds the fullest grid the June run's own data can support, at
zero API cost, so the two pools can be read side by side. It is deliberately
thin: every primitive — the operating-point predicate, the tile re-stamp, the
per-tile arrays, the micro-F1 and tile-MCC mechanism, the engine recipe — is
**imported** from ``scripts/gemini37_image_55map_r2.py``, the instrument the
2x2 itself used. Nothing about the measurement is re-implemented here, so a
difference between the two pools cannot be an artefact of two scorers.

What the grid can and cannot cover
----------------------------------
The June verifier saw only the 3-of-5 consensus union: its crop manifest holds
7,878 candidates, all with ``vote_count`` in {3, 4, 5} (2,896 / 2,159 / 2,823).
Candidates carrying one or two votes were never verified, so they have no
probability and cannot be scored at any threshold. The grid therefore covers
``min_votes`` in {3, 4, 5} only, and the June pool's votes 1-2 rows of the
rebuilt pool's sweep have **no** June counterpart. That is a limit of the June
run's design, not of this script.

The reproduction gate
---------------------
``--stage sweep`` refuses to write anything unless the grid's carried point
(0.15, k3) reproduces the committed ``IM-k3`` evaluation — micro-F1 @ 50 m
0.8008 and tile-MCC 0.7110
(``results/55maps-r2-ref-2026-09-06/IM-k3/evaluation.json``) — to within
0.003. The gate is what makes the rest of the grid readable as IM-k3's
neighbourhood rather than as an unanchored set of numbers.

The tile re-stamp
-----------------
The June proposer ran on the scoring frame's own tiling (its 4,583 distinct
``source_tile`` values are all names of the 8,541-tile evaluation frame), so
unlike the September pool it needs no vocabulary change. It is re-stamped all
the same, by ``assign_eval_frame_tiles`` — nearest standard-grid tile centroid
within the origin raster's own map — because every other 55-map cell on the r2
board went through that writer, and IM-k3's committed file did not (it
reproduces the writer at 83.65 %, ``results/run-facts.json`` § IM-k3 CAVEAT).
``--stage gate`` reports the carried point both ways so the size of that
convention difference is on the record rather than assumed.

Usage::

    python scripts/im_june_pool_grid.py --stage gate
    python scripts/im_june_pool_grid.py --stage sweep --workers 12
    python scripts/im_june_pool_grid.py --stage materialise
    # commit the materialised detections, then:
    python scripts/im_june_pool_grid.py --stage score --workers 5 --jobs 4

Zero API. Run on sapphire: each sweep point is a Hungarian match over 8,541
tiles, and the scoring stage is a 10,000-draw BCa bootstrap per cell.

Created: 2026-09-20
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts import gemini37_image_55map_r2 as r2  # noqa: E402
from scripts.final_board_sweeps import load_manifest_probs  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The June run's own outputs. ``crops`` holds the 3-of-5 union's candidate
#: manifest; ``verified`` holds the verifier's probabilities for every one of
#: them and the committed IM-k3 detection set.
JUNE_ROOT = PROJECT_ROOT / "outputs/55maps-image-generalisation"

#: Where the grid, its cells and the findings note live.
RESULTS_HOME = PROJECT_ROOT / "results/im-june-pool-grid-2026-09-20"

#: The grid's single rung label, written into every CSV row so the file reads
#: like the 2x2's sweep CSVs.
RUNG = "IM-5pass"

#: The vote thresholds the June pool can reach. Votes 1 and 2 were never
#: verified — see the module docstring.
MIN_VOTES = (3, 4, 5)

#: The June run's own operating point, from its ``resolved_config.yaml``
#: (``evaluate.prob_threshold: 0.15``) and its consensus vote threshold of 3.
CARRIED: tuple[float, int] = (0.15, 3)

#: The committed IM-k3 numbers on the r2 reference, read from
#: ``results/55maps-r2-ref-2026-09-06/IM-k3/evaluation.json`` (buffer 50 m
#: ``f1``; ``tile_classification.mcc.point``).
COMMITTED_IM_K3 = {"micro_f1_50": 0.8008, "tile_mcc": 0.7110}

#: The board's own agreement tolerance for a reproduction claim.
GATE_TOL = 0.003

#: The four cells this campaign materialises and scores on the full recipe.
#: ``oracle`` bases are resolved from the swept grid; ``carried`` bases are
#: fixed points. The k5 carried point is IM-k3's probability read at
#: unanimity, which is the June pool's nearest analogue to the rebuilt pool's
#: K = 5 unanimity cell.
CELL_SPECS: tuple[dict[str, Any], ...] = (
    {"label": "IM-5pass-k3-f1-oracle", "min_votes": 3, "basis": "f1-oracle"},
    {"label": "IM-5pass-k3-mcc-oracle", "min_votes": 3, "basis": "mcc-oracle"},
    {"label": "IM-5pass-k5-carried", "min_votes": 5, "basis": "carried",
     "prob_t": 0.15},
    {"label": "IM-5pass-k5-f1-oracle", "min_votes": 5, "basis": "f1-oracle"},
)

#: The 2x2's sweep CSV columns, in its own order, so the two files can be
#: concatenated without reordering.
CSV_FIELDS = (
    "rung", "prob_t", "min_votes", "n_detections", "tp", "fp", "fn",
    "micro_f1_50", "tile_mcc", "tile_tp", "tile_tn", "tile_fp", "tile_fn",
)


# ---------------------------------------------------------------------------
# The June pool's candidate frame.
# ---------------------------------------------------------------------------


def june_frame(restamp: bool = True) -> gpd.GeoDataFrame:
    """The June pool's 7,878 verified candidates as a scorable frame.

    Args:
        restamp: Re-stamp ``source_tile`` onto the scoring frame's vocabulary
            with ``assign_eval_frame_tiles``. True is the board's writer and
            the convention every other r2 cell uses; False reproduces the
            committed IM-k3 file's own convention and exists only so
            :func:`stage_gate` can measure the difference.

    Returns:
        A GeoDataFrame in EPSG:32635 with ``vote_count``,
        ``mound_probability`` and ``source_tile``.
    """
    raw = load_manifest_probs(JUNE_ROOT / "crops", JUNE_ROOT / "verified")
    return r2.assign_eval_frame_tiles(raw) if restamp else raw


def achievable_points(frame: gpd.GeoDataFrame) -> list[tuple[float, int]]:
    """Every operating point the June pool can reach.

    The ladder is ``final_board_sweeps.py``', by way of
    ``gemini37_image_55map_r2.achievable_points``: zero plus each distinct
    observed probability rounded to four places. It is crossed here with
    :data:`MIN_VOTES` rather than with ``range(1, k + 1)``, because the pool's
    one- and two-vote candidates were never verified.

    Args:
        frame: The June candidate frame.

    Returns:
        ``(prob_t, min_votes)`` pairs, sorted, including :data:`CARRIED`.
    """
    thresholds = sorted(
        {0.0} | {round(float(v), 4) for v in frame["mound_probability"]})
    points = [(p, votes) for p in thresholds for votes in MIN_VOTES]
    if CARRIED not in points:
        points = sorted([*points, CARRIED])
    return points


# ---------------------------------------------------------------------------
# Stages.
# ---------------------------------------------------------------------------


def _score_one(frame: gpd.GeoDataFrame, point: tuple[float, int]) -> dict[str, Any]:
    """Score a single point in-process, through the r2 worker.

    Args:
        frame: The candidate frame to read the point on.
        point: ``(prob_t, min_votes)``.

    Returns:
        The r2 sweep row for that point.
    """
    ref, bounds, tile_index = r2.load_frames()
    r2._init(ref, bounds, tile_index, {RUNG: frame})
    return r2._score_point((RUNG, point[0], point[1]))


def stage_gate() -> int:
    """Report the carried point under both tile conventions.

    Neither result is written anywhere: this stage exists so the choice of
    convention, and its cost in F1 and MCC, is measured before the grid is
    built on it.

    Returns:
        0 if the re-stamped carried point clears :data:`GATE_TOL` against the
        committed IM-k3 numbers, 1 otherwise.
    """
    rows = {}
    for restamp in (True, False):
        row = _score_one(june_frame(restamp=restamp), CARRIED)
        rows["restamped" if restamp else "as-committed"] = row
        logger.info(
            "carried (%.2f, k%d) %-13s n=%d  F1@50 %.4f  tile-MCC %.4f",
            CARRIED[0], CARRIED[1], "re-stamped" if restamp else "as committed",
            row["n_detections"], row["micro_f1_50"], row["tile_mcc"])
    ok = _gate_verdict(rows["restamped"])
    for key, row in rows.items():
        logger.info(
            "%-13s deltas vs committed IM-k3: F1 %+0.4f  MCC %+0.4f", key,
            row["micro_f1_50"] - COMMITTED_IM_K3["micro_f1_50"],
            row["tile_mcc"] - COMMITTED_IM_K3["tile_mcc"])
    return 0 if ok else 1


def _gate_verdict(row: dict[str, Any]) -> bool:
    """Whether a carried-point row reproduces the committed IM-k3 numbers.

    Args:
        row: The sweep row at :data:`CARRIED`.

    Returns:
        True when both metrics agree within :data:`GATE_TOL`.
    """
    df1 = abs(row["micro_f1_50"] - COMMITTED_IM_K3["micro_f1_50"])
    dmcc = abs(row["tile_mcc"] - COMMITTED_IM_K3["tile_mcc"])
    ok = df1 <= GATE_TOL and dmcc <= GATE_TOL
    logger.log(
        logging.INFO if ok else logging.ERROR,
        "reproduction gate %s: |dF1| = %.4f, |dMCC| = %.4f (tolerance %.3f)",
        "PASS" if ok else "FAIL", df1, dmcc, GATE_TOL)
    return ok


def stage_sweep(workers: int) -> int:
    """Sweep every achievable point; write the CSV and the oracle record.

    The gate is applied before anything is written, so a failed reproduction
    leaves no half-trusted artefact behind.

    Args:
        workers: Sweep parallelism.

    Returns:
        A process exit status.
    """
    frame = june_frame(restamp=True)
    logger.info("%s: %d candidates, votes %s", RUNG, len(frame),
                dict(sorted(frame["vote_count"].value_counts().items())))
    ref, bounds, tile_index = r2.load_frames()
    points = achievable_points(frame)
    tasks = [(RUNG, p, v) for p, v in points]
    logger.info("sweeping %d points (%d workers)", len(tasks), workers)
    with Pool(workers, initializer=r2._init,
              initargs=(ref, bounds, tile_index, {RUNG: frame})) as pool:
        rows = pool.map(r2._score_point, tasks, chunksize=2)

    rows = [r for r in rows if r["micro_f1_50"] is not None]
    rows.sort(key=lambda r: (r["prob_t"], r["min_votes"]))
    carried = next(
        (r for r in rows
         if abs(r["prob_t"] - CARRIED[0]) < 1e-9 and r["min_votes"] == CARRIED[1]),
        None)
    if carried is None:
        logger.error("carried point %s absent from the swept grid", CARRIED)
        return 2
    if not _gate_verdict(carried):
        logger.error(
            "NOT writing the grid: the carried point does not reproduce the "
            "committed IM-k3 cell, so the rest of the grid cannot be read as "
            "its neighbourhood.")
        return 3

    RESULTS_HOME.mkdir(parents=True, exist_ok=True)
    dest = RESULTS_HOME / f"sweep_{RUNG}.csv"
    with dest.open("w", newline="") as fh:
        writer = csvmod.DictWriter(fh, fieldnames=list(CSV_FIELDS))
        writer.writeheader()
        writer.writerows({k: r[k] for k in CSV_FIELDS} for r in rows)
    logger.info("wrote %s (%d points)", dest.relative_to(PROJECT_ROOT), len(rows))

    per_votes = {}
    for votes in MIN_VOTES:
        block = [r for r in rows if r["min_votes"] == votes]
        per_votes[str(votes)] = {
            "n_points": len(block),
            "f1_oracle": max(block, key=lambda r: r["micro_f1_50"]),
            "mcc_oracle": max(block, key=lambda r: r["tile_mcc"]),
        }
        logger.info(
            "votes >= %d: F1 oracle %.4f at p%.2f | MCC oracle %.4f at p%.2f",
            votes, per_votes[str(votes)]["f1_oracle"]["micro_f1_50"],
            per_votes[str(votes)]["f1_oracle"]["prob_t"],
            per_votes[str(votes)]["mcc_oracle"]["tile_mcc"],
            per_votes[str(votes)]["mcc_oracle"]["prob_t"])

    (RESULTS_HOME / "grid.json").write_text(json.dumps({
        "rung": RUNG,
        "buffer_m": r2.BUFFER_M,
        "reference": r2.REFERENCE,
        "pool": str(JUNE_ROOT.relative_to(PROJECT_ROOT)),
        "source_tile_convention": "re-stamped by stride55_score.assign_standard_tile",
        "min_votes_covered": list(MIN_VOTES),
        "min_votes_unverified": [1, 2],
        "n_candidates": int(len(frame)),
        "n_sweep_points": len(rows),
        "carried_point": list(CARRIED),
        "carried": carried,
        "committed_im_k3": COMMITTED_IM_K3,
        "gate_tolerance": GATE_TOL,
        "gate": {
            "micro_f1_50_delta": carried["micro_f1_50"] - COMMITTED_IM_K3["micro_f1_50"],
            "tile_mcc_delta": carried["tile_mcc"] - COMMITTED_IM_K3["tile_mcc"],
            "passed": True,
        },
        "per_min_votes": per_votes,
    }, indent=2) + "\n")
    logger.info("wrote %s", (RESULTS_HOME / "grid.json").relative_to(PROJECT_ROOT))
    return 0


def resolve_cell_points(grid: dict[str, Any]) -> list[dict[str, Any]]:
    """Turn :data:`CELL_SPECS` into concrete operating points.

    Args:
        grid: The record written by :func:`stage_sweep`.

    Returns:
        One dict per cell with ``label``, ``prob_t``, ``min_votes`` and
        ``basis``.

    Raises:
        KeyError: If a spec names a vote threshold the grid does not carry.
    """
    out = []
    for spec in CELL_SPECS:
        votes = int(spec["min_votes"])
        if spec["basis"] == "carried":
            prob_t = float(spec["prob_t"])
        else:
            key = "f1_oracle" if spec["basis"] == "f1-oracle" else "mcc_oracle"
            prob_t = float(grid["per_min_votes"][str(votes)][key]["prob_t"])
        out.append({"label": spec["label"], "prob_t": prob_t,
                    "min_votes": votes, "basis": spec["basis"]})
    return out


def stage_materialise() -> int:
    """Write one ``detections.geojson`` per cell, plus the cell manifest.

    Returns:
        A process exit status.
    """
    grid = json.loads((RESULTS_HOME / "grid.json").read_text())
    frame = june_frame(restamp=True)
    cells = []
    for cell in resolve_cell_points(grid):
        sub = r2.materialise(frame, cell["prob_t"], cell["min_votes"])
        dest = RESULTS_HOME / "cells" / cell["label"] / "detections.geojson"
        dest.parent.mkdir(parents=True, exist_ok=True)
        sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
        cells.append({
            **cell,
            "point": f"({cell['prob_t']:.2f}, k{cell['min_votes']})",
            "n_detections": int(len(sub)),
            "det": str(dest.relative_to(PROJECT_ROOT)),
        })
        logger.info("%-24s n=%5d -> %s", cell["label"], len(sub),
                    dest.relative_to(PROJECT_ROOT))
    (RESULTS_HOME / "cells_manifest.json").write_text(json.dumps({
        "buffer_m": r2.BUFFER_M,
        "reference": r2.REFERENCE,
        "rung": RUNG,
        "cells": cells,
    }, indent=2) + "\n")
    logger.info("wrote %s (%d cells)",
                (RESULTS_HOME / "cells_manifest.json").relative_to(PROJECT_ROOT),
                len(cells))
    return 0


def stage_score(workers: int, jobs: int) -> int:
    """Score every materialised cell with the engine, on the r2 board's recipe.

    The recipe is ``gemini37_image_55map_r2.engine_command`` verbatim, so these
    cells are scored by the same invocation as the 2x2's.

    Args:
        workers: Engine parallelism per cell.
        jobs: Cells scored concurrently.

    Returns:
        A process exit status.
    """
    manifest = json.loads((RESULTS_HOME / "cells_manifest.json").read_text())
    cells = manifest["cells"]
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", *[c["det"] for c in cells]],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip()
    if dirty:
        logger.error(
            "detections not committed — the engine's --require-clean-inputs "
            "would refuse them. Commit these first:\n%s", dirty)
        return 4

    def run_one(cell: dict[str, Any]) -> tuple[str, int]:
        out_dir = str((RESULTS_HOME / "cells" / cell["label"]).relative_to(PROJECT_ROOT))
        cmd = r2.engine_command(cell["det"], out_dir, cell["label"], workers)
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                              text=True, check=False)
        (RESULTS_HOME / "cells" / cell["label"] / "score.log").write_text(
            proc.stdout + proc.stderr)
        return cell["label"], proc.returncode

    failed = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for label, rc in pool.map(run_one, cells):
            logger.info("scored %-24s rc=%d", label, rc)
            if rc != 0:
                failed.append(label)
    if failed:
        logger.error("scoring FAILED for %s — see each cell's score.log", failed)
        return 1
    logger.info("scored %d cells", len(cells))
    return 0


def main() -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--stage", required=True,
                        choices=("gate", "sweep", "materialise", "score"))
    parser.add_argument("--workers", type=int, default=12,
                        help="sweep parallelism, or engine parallelism per cell")
    parser.add_argument("--jobs", type=int, default=4,
                        help="cells scored concurrently in --stage score")
    args = parser.parse_args()
    if args.stage == "gate":
        return stage_gate()
    if args.stage == "sweep":
        return stage_sweep(args.workers)
    if args.stage == "materialise":
        return stage_materialise()
    return stage_score(args.workers, args.jobs)


if __name__ == "__main__":
    raise SystemExit(main())
