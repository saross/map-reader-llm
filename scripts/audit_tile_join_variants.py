#!/usr/bin/env python3
"""
Audit every committed evaluation's tile confusion against all three tile joins.
==============================================================================

Description:
    The tile confusion matrix behind tile-level Matthews Correlation
    Coefficient (MCC) used to book detections to evaluation-frame tiles by
    the ``source_tile`` **string** while booking reference mounds by
    geometry (``scripts/lib_advanced_metrics.py``, before 2026-09-12). A
    cell scored on a frame whose tile vocabulary is not the one its
    proposer ran on therefore got a meaningless confusion beside a correct
    F1, and nothing warned.

    This script answers the two questions that follow from the fix, over
    any set of committed evaluations, by recomputation rather than by
    assumption:

    1. **Is the refactor behaviour-preserving?** Re-running the legacy
       ``id`` join must reproduce each committed evaluation's confusion and
       MCC exactly. Anything else is a regression in the refactor, not a
       finding about the data.
    2. **Was any published MCC wrong?** The new invariant — every point
       inside the frame's tile union must be booked to some tile — refuses
       the confusion where the join does not describe the frame. Cells the
       invariant refuses are cells whose published MCC should never have
       been a number.

    It also reports what the two geometric joins would give, because the
    project's 384 px frames **overlap** (336 px stride; on
    ``era2_b_intersection_bounds.geojson`` the tile areas sum to 1.2783x
    the union area and about 35 % of detections lie in more than one
    tile). The three joins therefore disagree even where the vocabulary
    matches, and choosing between them is a methodological decision rather
    than a bug fix. Quantifying the disagreement is this script's third
    job.

    Nothing is written back into any committed evaluation. The output is a
    side report.

Usage::

    # Every cell of the signed Era-2 board
    python scripts/audit_tile_join_variants.py \\
        --evaluation-glob 'results/leaderboard/era2/gs-era2-verified-board-2026-09-10/cells/*/evaluation.json' \\
        --json-out results/tile-join-audit/board-era2.json \\
        --markdown-out results/tile-join-audit/board-era2.md

    # A directory of materialised cells against one frame, with no
    # committed evaluation to compare against
    python scripts/audit_tile_join_variants.py \\
        --detections-glob 'results/k-ladder-2026-09-12/phase2/materialised/*.geojson' \\
        --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \\
        --ground-truth inputs/vectors/references/mounds-reference.geojson \\
        --json-out results/tile-join-audit/k-ladder-phase2.json

Verdicts (the ``id`` reproduction column):
    ``EXACT``     confusion and MCC reproduce the committed evaluation.
    ``DRIFT``     they do not — investigate before trusting anything else.
    ``REFUSED``   the invariant refuses the join for this frame; the
                  committed MCC, if it is a number, is not interpretable.
    ``NO-BASELINE`` no committed evaluation was supplied to compare against.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import glob as globmod
import json
import logging
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402

from scripts.lib_advanced_metrics import (  # noqa: E402
    TILE_JOIN_GEOMETRIC_CONTAINS,
    TILE_JOIN_GEOMETRIC_PRIMARY,
    TILE_JOIN_ID,
    calculate_tile_classification,
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

#: Joins reported for every cell, legacy first so the reproduction check
#: reads left to right.
JOINS: tuple[str, ...] = (
    TILE_JOIN_ID,
    TILE_JOIN_GEOMETRIC_PRIMARY,
    TILE_JOIN_GEOMETRIC_CONTAINS,
)

#: MCC is committed rounded to four decimals, so the reproduction check
#: compares at that precision. The confusion counts are integers and are
#: compared exactly.
MCC_DECIMALS = 4


def _load_cached(cache: dict[str, Any], path: Path, crs: Any = None):
    """Read a GeoJSON once per process, reprojecting to ``crs`` if given."""
    key = f"{path}|{crs}"
    if key not in cache:
        gdf = gpd.read_file(path)
        if crs is not None and gdf.crs is not None and gdf.crs != crs:
            gdf = gdf.to_crs(crs)
        cache[key] = gdf
    return cache[key]


def jobs_from_evaluations(patterns: list[str]) -> list[dict[str, Any]]:
    """
    Build audit jobs from committed ``evaluation.json`` files.

    Each evaluation records the detections, ground truth and bounds it was
    produced from under ``_metadata.input_files``, plus the confusion and
    MCC it published under ``summary.tile_classification``. That is
    everything needed to re-score it and compare.

    Args:
        patterns: Glob patterns matching ``evaluation.json`` files.

    Returns:
        One job dict per evaluation that names a bounds file and at least
        one detections file. Evaluations with no ``tile_classification``
        (scored without ``--mcc``) are included with no baseline, because
        the invariant question applies to them too.
    """
    jobs: list[dict[str, Any]] = []
    for pattern in patterns:
        for hit in sorted(globmod.glob(pattern)):
            path = Path(hit)
            with open(path) as handle:
                doc = json.load(handle)
            meta = doc.get("_metadata", {})
            files = meta.get("input_files", {})
            detections = files.get("detections") or []
            bounds = files.get("bounds")
            ground_truth = files.get("ground_truth")
            if not detections or not bounds or not ground_truth:
                logger.warning("skipping %s — incomplete input_files", path)
                continue
            summary = doc.get("summary", {})
            jobs.append({
                "label": summary.get("label") or path.parent.name,
                "evaluation": str(path),
                "detections": [str(d) for d in detections],
                "bounds": str(bounds),
                "ground_truth": str(ground_truth),
                "baseline": summary.get("tile_classification"),
                "n_detections_committed": summary.get("n_detections"),
            })
    return jobs


def jobs_from_detections(
    patterns: list[str], bounds: str, ground_truth: str,
) -> list[dict[str, Any]]:
    """
    Build audit jobs from raw detection GeoJSONs against one frame.

    Used for cells that have been materialised but whose evaluations are
    not the artefact of interest — the K-ladder Phase 2 materialised set,
    for instance.

    Args:
        patterns: Glob patterns matching detection GeoJSONs.
        bounds: Evaluation frame bounds GeoJSON.
        ground_truth: Reference mounds GeoJSON.

    Returns:
        One baseline-free job per detection file.
    """
    jobs: list[dict[str, Any]] = []
    for pattern in patterns:
        for hit in sorted(globmod.glob(pattern)):
            jobs.append({
                "label": Path(hit).stem,
                "evaluation": None,
                "detections": [hit],
                "bounds": bounds,
                "ground_truth": ground_truth,
                "baseline": None,
                "n_detections_committed": None,
            })
    return jobs


def _baseline_confusion(baseline: dict[str, Any] | None) -> dict[str, int] | None:
    """Pull the committed tp/tn/fp/fn out of a tile_classification block."""
    if not baseline:
        return None
    confusion = baseline.get("confusion")
    if not isinstance(confusion, dict):
        return None
    try:
        return {k: int(confusion[k]) for k in ("tp", "tn", "fp", "fn")}
    except (KeyError, TypeError, ValueError):
        return None


def _baseline_mcc(baseline: dict[str, Any] | None) -> float | None:
    """Pull the committed point MCC out of a tile_classification block."""
    if not baseline:
        return None
    mcc = baseline.get("mcc")
    if isinstance(mcc, dict):
        point = mcc.get("point")
    else:
        point = mcc
    return None if point is None else float(point)


def audit_job(job: dict[str, Any], cache: dict[str, Any]) -> dict[str, Any]:
    """
    Re-score one cell under every tile join and compare with what it published.

    Args:
        job: A job dict from :func:`jobs_from_evaluations` or
            :func:`jobs_from_detections`.
        cache: Process-wide GeoDataFrame cache, so a frame and a reference
            set shared by 100 cells are read once.

    Returns:
        The job's row: per-join confusion, MCC and diagnostics, plus the
        ``id`` reproduction verdict against the committed baseline.
    """
    bounds = _load_cached(cache, Path(job["bounds"]))
    ref = _load_cached(cache, Path(job["ground_truth"]), bounds.crs)

    frames = []
    for det_path in job["detections"]:
        gdf = gpd.read_file(det_path)
        if gdf.crs is not None and gdf.crs != bounds.crs:
            gdf = gdf.to_crs(bounds.crs)
        frames.append(gdf)
    det = (
        frames[0] if len(frames) == 1
        else gpd.GeoDataFrame(
            pd.concat(frames, ignore_index=True), crs=bounds.crs,
        )
    )

    row: dict[str, Any] = {
        "label": job["label"],
        "evaluation": job["evaluation"],
        "detections": job["detections"],
        "bounds": job["bounds"],
        "n_detections": len(det),
        "n_frame_tiles": int(bounds["tile_name"].nunique()),
        "joins": {},
    }

    for join in JOINS:
        result = calculate_tile_classification(det, ref, bounds, tile_join=join)
        if "error" in result:
            row["joins"][join] = {
                "refused": True,
                "reason": result.get("reason"),
                "detail": result["error"],
                "diagnostics": result.get("tile_join_diagnostics"),
            }
        else:
            row["joins"][join] = {
                "refused": False,
                "confusion": {
                    k: int(result[k]) for k in ("tp", "tn", "fp", "fn")
                },
                "mcc": (
                    None if result["mcc"] is None
                    else round(float(result["mcc"]), MCC_DECIMALS)
                ),
                "diagnostics": result.get("tile_join_diagnostics"),
            }

    # The reproduction verdict: does the legacy join still give exactly
    # what the committed evaluation published?
    baseline_confusion = _baseline_confusion(job["baseline"])
    baseline_mcc = _baseline_mcc(job["baseline"])
    legacy = row["joins"][TILE_JOIN_ID]

    if legacy["refused"]:
        verdict = "REFUSED"
    elif baseline_confusion is None:
        verdict = "NO-BASELINE"
    else:
        confusion_ok = legacy["confusion"] == baseline_confusion
        mcc_ok = (
            baseline_mcc is None
            or legacy["mcc"] is None
            or abs(legacy["mcc"] - round(baseline_mcc, MCC_DECIMALS)) < 1e-9
        )
        verdict = "EXACT" if (confusion_ok and mcc_ok) else "DRIFT"

    row["baseline_confusion"] = baseline_confusion
    row["baseline_mcc"] = (
        None if baseline_mcc is None else round(baseline_mcc, MCC_DECIMALS)
    )
    row["id_reproduction"] = verdict
    return row


def write_markdown(rows: list[dict[str, Any]], counts: dict[str, int],
                   target: Path) -> None:
    """Render the audit as a markdown table with a short preamble."""
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Tile-join audit",
        "",
        "Every cell re-scored under all three tile joins; nothing rewritten.",
        "`id` is the legacy string join, whose reproduction of the committed "
        "confusion is the refactor's regression test. The two geometric "
        "columns are what the same cell would score under each geometric "
        "rule — they differ from `id`, and from each other, because the "
        "evaluation frames overlap.",
        "",
        "| verdict | count |",
        "|---|---:|",
    ]
    for verdict in ("EXACT", "DRIFT", "REFUSED", "NO-BASELINE"):
        if verdict in counts:
            lines.append(f"| {verdict} | {counts[verdict]} |")
    lines += [
        "",
        "| cell | n det | committed MCC | id MCC | verdict | "
        "geometric-primary MCC | geometric-contains MCC |",
        "|---|---:|---:|---:|---|---:|---:|",
    ]

    def fmt(value: Any) -> str:
        if value is None:
            return "—"
        return f"{value:.4f}" if isinstance(value, float) else str(value)

    for row in sorted(rows, key=lambda r: r["label"]):
        legacy = row["joins"][TILE_JOIN_ID]
        primary = row["joins"][TILE_JOIN_GEOMETRIC_PRIMARY]
        contains = row["joins"][TILE_JOIN_GEOMETRIC_CONTAINS]
        lines.append(
            f"| {row['label']} | {row['n_detections']} | "
            f"{fmt(row['baseline_mcc'])} | "
            f"{'REFUSED' if legacy['refused'] else fmt(legacy.get('mcc'))} | "
            f"{row['id_reproduction']} | "
            f"{'REFUSED' if primary['refused'] else fmt(primary.get('mcc'))} | "
            f"{'REFUSED' if contains['refused'] else fmt(contains.get('mcc'))} |"
        )
    target.write_text("\n".join(lines) + "\n")
    logger.info("-> %s", target)


def main() -> int:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Re-score committed evaluations under every tile join, to "
            "check the refactor reproduces published numbers and to find "
            "cells whose tile join does not describe their frame"
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--evaluation-glob", action="append", default=[],
        help="Glob of committed evaluation.json files to audit",
    )
    parser.add_argument(
        "--detections-glob", action="append", default=[],
        help="Glob of detection GeoJSONs to audit (needs --bounds)",
    )
    parser.add_argument(
        "--bounds", type=str, default=None,
        help="Frame bounds GeoJSON, for --detections-glob",
    )
    parser.add_argument(
        "--ground-truth", type=str,
        default="inputs/vectors/references/mounds-reference.geojson",
        help="Reference mounds GeoJSON, for --detections-glob",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    jobs = jobs_from_evaluations(args.evaluation_glob)
    if args.detections_glob:
        if not args.bounds:
            parser.error("--detections-glob requires --bounds")
        jobs += jobs_from_detections(
            args.detections_glob, args.bounds, args.ground_truth,
        )
    if not jobs:
        logger.error("no cells to audit")
        return 2

    logger.info("auditing %d cell(s) under %d join(s)", len(jobs), len(JOINS))
    cache: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for index, job in enumerate(jobs, start=1):
        row = audit_job(job, cache)
        rows.append(row)
        counts[row["id_reproduction"]] = counts.get(row["id_reproduction"], 0) + 1
        if row["id_reproduction"] in ("DRIFT", "REFUSED"):
            logger.warning(
                "%-10s %s (committed MCC %s)",
                row["id_reproduction"], row["label"], row["baseline_mcc"],
            )
        if index % 20 == 0:
            logger.info("  %d/%d", index, len(jobs))

    for verdict in ("EXACT", "DRIFT", "REFUSED", "NO-BASELINE"):
        if verdict in counts:
            logger.info("%-12s %d", verdict, counts[verdict])

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_out, "w") as handle:
            json.dump({
                "n_cells": len(rows),
                "joins": list(JOINS),
                "counts": counts,
                "mechanism": (
                    "calculate_tile_classification books points to frame "
                    "tiles under a named rule; 'id' is the legacy string "
                    "join, the two geometric rules use the frame's polygons"
                ),
                "cells": rows,
            }, handle, indent=2)
            handle.write("\n")
        logger.info("-> %s", args.json_out)

    if args.markdown_out:
        write_markdown(rows, counts, args.markdown_out)

    # A DRIFT is a refactor regression and must fail the run. A REFUSED is
    # a finding about the data, reported but not fatal.
    return 3 if counts.get("DRIFT") else 0


if __name__ == "__main__":
    raise SystemExit(main())
