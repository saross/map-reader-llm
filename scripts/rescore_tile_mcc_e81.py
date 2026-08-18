#!/usr/bin/env python3
"""
Surgical re-emission of the tile-level MCC block for erratum E81.

Erratum E81 (``docs/methodology/preregistration/protocol-errata.md``)
withdraws 13 committed tile-level Matthews Correlation Coefficient (MCC)
values: nine conditions published ``0.0`` where the metric is *undefined*
(degenerate tile confusion matrix, TN + FN = 0), and four more published a
mean that averaged an undefined pass in as if it were a measurement.

This script re-emits **only** the ``tile_classification`` block of each
affected ``evaluation.json``, splicing the recomputed block into the
committed file and regenerating the ``.md`` / ``.csv`` siblings from it.

**Why surgical rather than a full re-run.** Replaying
``evaluate_detections.py`` end-to-end against the recorded ``cli_args``
reproduces F1, precision, and recall bit-for-bit, but it *also* imports
every unrelated change made to the scorer since the cell was written —
most visibly the erratum E72 partial-coverage machinery, which flips
``coverage_status`` from ``normal`` to ``partial_coverage`` and sets
``ci_unreliable`` on cells whose detection set does not cover every tile.
Applying that to 13 of the 36 phase-2 cells would leave the board
internally inconsistent and would silently fold a second, unrelated
correction into an MCC-reporting fix. E81 is scoped to the MCC block, so
the re-emission is too: every F1 / precision / recall / coverage field is
carried through from the committed file untouched, and the script asserts
that it is.

Guards (all fatal):

1. The recomputed confusion matrix must equal the committed per-pass
   confusion matrix. This is the wrong-source tripwire — if the detection
   GeoJSONs behind a cell are not the ones that produced the committed
   numbers, the counts will not line up.
2. Every non-``tile_classification`` field of ``summary`` and of each
   ``per_run`` entry must be byte-identical before and after.
3. The pass count must match.

Usage::

    # Re-emit every condition listed in the E81 worklist
    python scripts/rescore_tile_mcc_e81.py --eval-root results/paper-eval/phase2/512px-14buf-mcc

    # Dry run — report what would change, write nothing
    python scripts/rescore_tile_mcc_e81.py --eval-root ... --dry-run

    # A subset
    python scripts/rescore_tile_mcc_e81.py --eval-root ... --cells p2b-text-t-0-3

Created: 2026-08-18 (Session 136, erratum E81)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import (  # noqa: E402
    aggregate_tile_classification,
    build_tile_classification_block,
    find_detection_files,
    load_geojson,
    write_batch_summary,
    write_outputs,
)
from scripts.lib_advanced_metrics import (  # noqa: E402
    bootstrap_tile_classification_ci,
    calculate_tile_classification,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# The 13 conditions withdrawn by E81, as directory names under the
# phase-2 evaluation root. Nine publish an undefined MCC as 0.0; four
# publish a mean contaminated by an undefined pass.
E81_CELLS: tuple[str, ...] = (
    # Four multi-run cells whose published mean averaged in an undefined pass
    "p2a-brief-text",
    "p2a-verbose-text",
    "p2b-text-t-0-3",
    "p2b-text-t-1-0",
    # Nine cells that publish an undefined MCC as exactly 0.0
    "p2b-text-t-0-0",
    "p2b-text-t-0-7",
    "p2c-image-exploratory-pure-positive-2hp",
    "p2c-text-canonical",
    "p2c-text-plus-hp",
    "p2c-text-pure-positive-canon",
    "p2c-text-scale-4",
    "p2c-text-scale-8",
    "p2d-text-terse",
)


def _strip_tile_classification(block: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy of ``block`` without its ``tile_classification``.

    Args:
        block: A ``summary`` or ``per_run`` entry from an
            ``evaluation.json``.

    Returns:
        A deep copy with the ``tile_classification`` key removed, for
        equality-checking everything the re-emission must not touch.
    """
    stripped = copy.deepcopy(block)
    stripped.pop("tile_classification", None)
    return stripped


def recompute_cell(
    eval_path: Path,
    project_root: Path,
) -> dict[str, Any]:
    """Recompute the tile-classification blocks for one evaluation cell.

    Args:
        eval_path: Path to the committed ``evaluation.json``.
        project_root: Repository root that the recorded ``cli_args``
            paths are relative to.

    Returns:
        A dict with keys ``document`` (the updated evaluation document),
        ``summary_before`` / ``summary_after`` (the old and new
        ``tile_classification`` blocks), and ``n_runs``.

    Raises:
        ValueError: If the recorded metadata is unusable, the pass count
            does not match, or a recomputed confusion matrix disagrees
            with the committed one.
    """
    document = json.loads(eval_path.read_text(encoding="utf-8"))
    metadata = document.get("_metadata") or {}
    cli_args = metadata.get("cli_args") or {}

    n_bootstrap = int(cli_args.get("bootstrap") or 1000)
    seed = cli_args.get("seed")
    gt_path = cli_args["ground_truth"]
    bounds_path = cli_args["bounds"]

    gdf_ref = load_geojson(project_root / gt_path)
    gdf_bounds = load_geojson(project_root / bounds_path)

    # Two recorded invocation shapes: a directory scanned with a glob
    # (multi-pass cells) and a single ``--detections`` file. Both appear
    # among the E81 cells — the duplicate single-buffer root at
    # ``results/paper-eval/mcc/512px/`` was written the second way.
    det_dir = cli_args.get("detections_dir")
    det_file = cli_args.get("detections")
    if det_dir:
        glob_pattern = cli_args.get("glob") or "*.geojson"
        det_files = find_detection_files(project_root / det_dir, glob_pattern)
        source = det_dir
    elif det_file:
        # ``--detections`` is ``nargs="+"``, so it round-trips into the
        # metadata as a list; older records store a bare string.
        listed = det_file if isinstance(det_file, list) else [det_file]
        det_files = [project_root / p for p in listed]
        source = ", ".join(str(p) for p in listed)
    else:
        raise ValueError(
            f"{eval_path}: neither detections_dir nor detections in "
            "_metadata.cli_args",
        )
    if not det_files or not all(p.exists() for p in det_files):
        raise ValueError(f"{eval_path}: detection files missing under {source}")

    committed_runs = document.get("per_run")
    is_multi_run = bool(committed_runs)
    if is_multi_run and len(committed_runs) != len(det_files):
        raise ValueError(
            f"{eval_path}: committed per_run has {len(committed_runs)} passes "
            f"but {len(det_files)} detection files were found",
        )
    if not is_multi_run and len(det_files) != 1:
        raise ValueError(
            f"{eval_path}: single-run cell but {len(det_files)} detection "
            "files were found",
        )

    new_blocks: list[dict[str, Any]] = []
    for index, det_file in enumerate(det_files):
        gdf_det = load_geojson(det_file)
        tile_class = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)
        tile_ci = bootstrap_tile_classification_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=n_bootstrap, random_seed=seed,
        )
        block = build_tile_classification_block(tile_class, tile_ci)

        # Guard 1: wrong-source tripwire.
        committed_block = (
            committed_runs[index]["tile_classification"] if is_multi_run
            else document["summary"]["tile_classification"]
        )
        committed_conf = committed_block.get("confusion", {})
        if block["confusion"] != committed_conf:
            raise ValueError(
                f"{eval_path} pass {index + 1}: recomputed confusion "
                f"{block['confusion']} != committed {committed_conf} — the "
                "detection source does not match the committed cell",
            )
        logger.info(
            "  pass %d (%s): MCC point %s -> %s",
            index + 1, det_file.name,
            committed_block.get("mcc", {}).get("point"),
            block["mcc"]["point"],
        )
        new_blocks.append(block)

    summary_before = copy.deepcopy(document["summary"]["tile_classification"])
    if is_multi_run:
        summary_after = aggregate_tile_classification(new_blocks)
    else:
        summary_after = new_blocks[0]

    # Guard 2: nothing outside tile_classification may move.
    frozen_summary_before = _strip_tile_classification(document["summary"])
    document["summary"]["tile_classification"] = summary_after
    if _strip_tile_classification(document["summary"]) != frozen_summary_before:
        raise ValueError(f"{eval_path}: summary changed outside the MCC block")
    if is_multi_run:
        for index, block in enumerate(new_blocks):
            frozen = _strip_tile_classification(committed_runs[index])
            committed_runs[index]["tile_classification"] = block
            if _strip_tile_classification(committed_runs[index]) != frozen:
                raise ValueError(
                    f"{eval_path}: per_run[{index}] changed outside the "
                    "MCC block",
                )

    return {
        "document": document,
        "summary_before": summary_before,
        "summary_after": summary_after,
        "n_runs": len(det_files),
    }


def rewrite_cell(cell_dir: Path, result: dict[str, Any]) -> None:
    """Write the re-emitted ``evaluation.{json,md,csv}`` for one cell.

    Regenerates all three siblings from the spliced document via
    :func:`evaluate_detections.write_outputs`, so the Markdown and CSV
    renderings of the undefined MCC come from the fixed renderers rather
    than being hand-patched.

    Args:
        cell_dir: The evaluation cell directory.
        result: The dict returned by :func:`recompute_cell`.
    """
    document = result["document"]
    metadata = document.get("_metadata")
    if metadata is not None:
        # Provenance for the re-emission itself: the original run record
        # is preserved and the correction is recorded beside it.
        metadata["e81_reemission"] = {
            "erratum": "E81",
            "scope": (
                "summary.tile_classification and per_run[*]."
                "tile_classification only; F1, precision, recall, "
                "coverage, and CI fields carried through unchanged"
            ),
            "script_path": "scripts/rescore_tile_mcc_e81.py",
        }
    write_outputs(
        results=document["summary"],
        run_results=document.get("per_run"),
        output_dir=cell_dir,
        metadata=metadata,
    )


def rebuild_batch_summary(eval_root: Path) -> int:
    """Regenerate an evaluation root's ``batch_summary.*`` from its cells.

    A batch root republishes every cell's MCC in ``batch_summary.json`` /
    ``.csv`` / ``.md``, so re-emitting the cells without refreshing the
    roll-up would leave the withdrawn values standing one directory up.
    The roll-up is rebuilt from the (already corrected) per-cell
    ``evaluation.json`` summaries through the same
    :func:`evaluate_detections.write_batch_summary` that wrote it, so no
    hand-editing is involved and the row ordering rule (F1 descending) is
    unchanged.

    Args:
        eval_root: Directory holding the per-condition cells and the
            ``batch_summary.*`` files.

    Returns:
        The number of condition summaries rolled up.
    """
    existing = eval_root / "batch_summary.json"
    metadata = None
    if existing.is_file():
        metadata = json.loads(
            existing.read_text(encoding="utf-8"),
        ).get("metadata")
    summaries = []
    for cell_dir in sorted(p for p in eval_root.iterdir() if p.is_dir()):
        eval_path = cell_dir / "evaluation.json"
        if not eval_path.is_file():
            continue
        summaries.append(
            json.loads(eval_path.read_text(encoding="utf-8"))["summary"],
        )
    write_batch_summary(summaries, eval_root, metadata=metadata)
    return len(summaries)


def main() -> int:
    """Parse arguments and re-emit the MCC block for each requested cell.

    Returns:
        Process exit code: 0 on success, 1 if any cell failed.
    """
    parser = argparse.ArgumentParser(
        description="Re-emit tile-level MCC blocks for erratum E81.",
    )
    parser.add_argument(
        "--eval-root", type=Path, required=True,
        help="Directory containing the per-condition evaluation cells.",
    )
    parser.add_argument(
        "--cells", nargs="*", default=None,
        help="Cell directory names (default: the 13 E81 conditions).",
    )
    parser.add_argument(
        "--project-root", type=Path, default=PROJECT_ROOT,
        help="Root the recorded cli_args paths are relative to.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Recompute and report, but write nothing.",
    )
    parser.add_argument(
        "--report", type=Path, default=None,
        help="Optional path for a JSON before/after report.",
    )
    parser.add_argument(
        "--rebuild-batch-summary", action="store_true",
        help=(
            "After re-emitting the cells, regenerate the evaluation "
            "root's batch_summary.{json,csv,md} roll-up from them."
        ),
    )
    args = parser.parse_args()

    cells = args.cells if args.cells else list(E81_CELLS)
    report: list[dict[str, Any]] = []
    failures = 0

    for cell in cells:
        cell_dir = args.eval_root / cell
        eval_path = cell_dir / "evaluation.json"
        if not eval_path.exists():
            logger.error("MISSING: %s", eval_path)
            failures += 1
            continue
        logger.info("Rescoring %s", cell)
        try:
            result = recompute_cell(eval_path, args.project_root)
        except (ValueError, KeyError, OSError) as exc:
            logger.error("FAILED %s: %s", cell, exc)
            failures += 1
            continue

        before, after = result["summary_before"], result["summary_after"]
        report.append({
            "cell": cell,
            "n_runs": result["n_runs"],
            "mcc_before": before.get("mcc"),
            "mcc_after": after.get("mcc"),
            "sensitivity_before": before.get("sensitivity"),
            "sensitivity_after": after.get("sensitivity"),
            "specificity_before": before.get("specificity"),
            "specificity_after": after.get("specificity"),
            "confusion": after.get("confusion"),
        })
        logger.info(
            "  summary MCC point %s -> %s (defined on %s of %s passes)",
            before.get("mcc", {}).get("point"),
            after.get("mcc", {}).get("point"),
            after.get("mcc", {}).get("n_runs_defined", "n/a"),
            after.get("mcc", {}).get("n_runs", result["n_runs"]),
        )
        if not args.dry_run:
            rewrite_cell(cell_dir, result)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8",
        )
        logger.info("Report written: %s", args.report)

    if args.rebuild_batch_summary and not args.dry_run:
        n_rolled = rebuild_batch_summary(args.eval_root)
        logger.info("Batch summary rebuilt from %d cells", n_rolled)

    logger.info(
        "Done: %d cells re-emitted, %d failures%s",
        len(report), failures, " (DRY RUN — nothing written)"
        if args.dry_run else "",
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
