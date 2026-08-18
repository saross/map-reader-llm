#!/usr/bin/env python3
"""
Rebuild the gitignored leaderboard ``.cache/`` from committed artefacts.

``scripts/build_tiered_leaderboard.py`` memoises two expensive stages under
``<output-dir>/.cache/``: per-condition evaluations and pairwise permutation
tests. That directory is excluded by ``.gitignore`` (``results/leaderboard/**/
.cache/``), so a checkout cannot re-run the board without redoing ~4,278
permutation tests at 10,000 permutations each.

Both stages are, however, *fully recoverable* from artefacts that **are**
committed beside the board:

* ``leaderboard_all_evaluations.json`` — the complete condition x threshold x
  buffer evaluation sweep, including each pass's ``tile_classification`` block.
* ``leaderboard_tiers_<metric>.json`` — carries a ``pairwise_tests`` list whose
  entries are byte-identical to the per-pair cache files.

This script writes those artefacts back into the cache layout the builder
expects, so the board can be regenerated with ``--skip-evaluation
--skip-pairwise`` and no recomputation.

It also implements the erratum E81 correction, via ``--null-undefined-mcc``:
any cached ``tile_classification`` whose 2 x 2 tile confusion matrix is
degenerate — that is, where ``(TP+FP)(TP+FN)(TN+FP)(TN+FN) == 0``, so the
Matthews Correlation Coefficient (MCC) denominator vanishes — has its MCC
fields rewritten from the imputed ``0.0`` to ``null``. Without the flag the
cache is reconstructed verbatim, which is what makes a
reproduce-then-correct check possible: rebuild the board from the unpatched
cache and confirm it matches the committed board, then rebuild from the
patched cache and attribute every difference to E81.

Usage::

    # Faithful reconstruction (verification baseline)
    python scripts/rebuild_leaderboard_cache_from_committed.py \\
        --board-dir results/leaderboard/combined/era1 \\
        --metric mcc --buffer 20

    # E81-corrected reconstruction
    python scripts/rebuild_leaderboard_cache_from_committed.py \\
        --board-dir results/leaderboard/combined/era1 \\
        --metric mcc --buffer 20 --null-undefined-mcc

Created: 2026-08-18 (Session 136, erratum E81)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    """Convert a condition label to the cache's directory name.

    Mirrors ``build_tiered_leaderboard.slugify`` exactly; duplicated here
    so this utility does not import the builder (which is itself under
    active revision).

    Args:
        text: The condition label.

    Returns:
        A lowercase, hyphen-separated slug.

    Examples:
        >>> slugify("h8-track2-text-scale-4")
        'h8-track2-text-scale-4'
    """
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def is_degenerate(confusion: dict[str, Any]) -> bool:
    """Report whether a tile confusion matrix leaves the MCC undefined.

    The MCC denominator is ``sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))``; it
    vanishes — and the metric is undefined — whenever any row or column
    marginal is zero.

    Args:
        confusion: Dict with integer ``tp`` / ``tn`` / ``fp`` / ``fn``.

    Returns:
        ``True`` when the MCC is undefined for this matrix.

    Examples:
        >>> is_degenerate({"tp": 204, "tn": 0, "fp": 136, "fn": 0})
        True
        >>> is_degenerate({"tp": 204, "tn": 1, "fp": 135, "fn": 0})
        False
    """
    tp = confusion.get("tp", 0)
    tn = confusion.get("tn", 0)
    fp = confusion.get("fp", 0)
    fn = confusion.get("fn", 0)
    return (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn) == 0


def write_evaluation_cache(
    board_dir: Path,
    buffer_metres: int,
    null_undefined_mcc: bool,
) -> tuple[int, int]:
    """Reconstruct ``.cache/evaluations/`` from the committed sweep.

    Args:
        board_dir: Directory holding the committed board artefacts.
        buffer_metres: The buffer whose cache files to write.
        null_undefined_mcc: Apply the E81 correction when ``True``.

    Returns:
        ``(n_files_written, n_blocks_nulled)``.
    """
    src = board_dir / "leaderboard_all_evaluations.json"
    payload = json.loads(src.read_text(encoding="utf-8"))
    evaluations = payload["evaluations"]
    cache_root = board_dir / ".cache" / "evaluations"

    n_written = 0
    n_nulled = 0
    for label, thresholds in evaluations.items():
        for threshold, result in thresholds.items():
            buffers = {b["buffer_metres"]: b for b in result.get("buffers", [])}
            if buffer_metres not in buffers:
                continue
            buf_data: dict[str, Any] = dict(buffers[buffer_metres])
            buf_data["n_detections"] = result.get("n_detections", 0)
            tile_class = result.get("tile_classification")
            if tile_class is not None:
                tile_class = json.loads(json.dumps(tile_class))
                if (
                    null_undefined_mcc
                    and is_degenerate(tile_class.get("confusion", {}))
                ):
                    mcc = tile_class.setdefault("mcc", {})
                    for key in ("point", "mean", "ci_lower", "ci_upper"):
                        if key in mcc:
                            mcc[key] = None
                    mcc["method"] = "undefined"
                    n_nulled += 1
                    logger.info(
                        "  E81: MCC nulled for %s (threshold %s) — %s",
                        label, threshold, tile_class.get("confusion"),
                    )
                buf_data["__tile_classification__"] = tile_class
            out = (
                cache_root / slugify(label)
                / f"t{threshold}_{buffer_metres}m.json"
            )
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(buf_data, indent=2), encoding="utf-8")
            n_written += 1
    return n_written, n_nulled


def write_pairwise_cache(
    board_dir: Path,
    metric: str,
    buffer_metres: int,
) -> int:
    """Reconstruct ``.cache/pairwise_<metric>/`` from the committed board.

    Args:
        board_dir: Directory holding the committed board artefacts.
        metric: ``"mcc"`` or ``"f1"``.
        buffer_metres: Buffer, used only for the F1 cache directory name
            (F1 permutation tests are buffer-dependent; MCC is not).

    Returns:
        The number of per-pair cache files written.
    """
    src = board_dir / f"leaderboard_tiers_{metric}.json"
    if not src.is_file():
        src = board_dir / f"leaderboard_tiers_{metric}_{buffer_metres}m.json"
    payload = json.loads(src.read_text(encoding="utf-8"))
    tests = payload.get("pairwise_tests") or []
    subdir = (
        f"pairwise_f1_{buffer_metres}m" if metric == "f1"
        else f"pairwise_{metric}"
    )
    cache_root = board_dir / ".cache" / subdir
    cache_root.mkdir(parents=True, exist_ok=True)

    for test in tests:
        a, b = sorted([slugify(test["label_a"]), slugify(test["label_b"])])
        out = cache_root / f"{a}_vs_{b}.json"
        out.write_text(json.dumps(test, indent=2), encoding="utf-8")
    return len(tests)


def main() -> int:
    """Parse arguments and rebuild the requested cache.

    Returns:
        Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild a leaderboard .cache/ from committed artefacts, "
            "optionally applying the erratum E81 undefined-MCC correction."
        ),
    )
    parser.add_argument("--board-dir", type=Path, required=True)
    parser.add_argument("--metric", default="mcc", choices=["mcc", "f1"])
    parser.add_argument("--buffer", type=int, default=20)
    parser.add_argument(
        "--null-undefined-mcc", action="store_true",
        help=(
            "Rewrite the MCC of every degenerate tile confusion matrix "
            "from the imputed 0.0 to null (erratum E81)."
        ),
    )
    args = parser.parse_args()

    n_eval, n_nulled = write_evaluation_cache(
        args.board_dir, args.buffer, args.null_undefined_mcc,
    )
    n_pairs = write_pairwise_cache(args.board_dir, args.metric, args.buffer)
    logger.info(
        "Cache rebuilt: %d evaluation files (%d MCC blocks nulled), "
        "%d pairwise files",
        n_eval, n_nulled, n_pairs,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
