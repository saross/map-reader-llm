#!/usr/bin/env python3
"""Rebuild committed batch_summary roll-ups from their cells' evaluations.

Two roll-up families went stale (Session 137 audit remediation, defect D30):

* ``results/paper-eval/mcc/{384px,512px}`` — the per-cell evaluations were
  re-emitted (BCa migration, then the B = 10,000 standardisation) and the
  roll-up never was, so its cells match neither the current mean nor the
  current point of its own sub-directory evaluations.
* ``results/paper-eval/n1/384px-14buf-mcc`` and ``.../pro-rerun`` — the
  Phase 5 corpus migration rewrote ``batch_summary.csv`` to the observed
  point but the sibling ``batch_summary.{json,md}`` were out of that
  migration's remit, leaving one directory internally inconsistent.

Rather than patch cells, this driver rebuilds each roll-up through the
canonical writer (``evaluate_detections.write_batch_summary``) from the
committed per-cell ``evaluation.json`` summaries, preserving the roll-up's
own metadata block. The writer publishes observed points with the resample
means in explicit ``*_boot_mean`` columns (D30).

Usage::

    python scripts/rebuild_batch_summaries.py [--dirs DIR ...]

$0 API; local; deterministic given the committed evaluations.
Created 2026-08-20 (Session 138, audit remediation).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import write_batch_summary  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_DIRS = [
    "results/paper-eval/n1/384px-14buf-mcc",
    "results/paper-eval/n1/384px-14buf-mcc/pro-rerun",
    "results/paper-eval/mcc/384px",
    "results/paper-eval/mcc/512px",
]


def rebuild(batch_dir: Path) -> int:
    """Rebuild one directory's roll-up; returns the number of cells used."""
    old_json = batch_dir / "batch_summary.json"
    metadata = None
    if old_json.exists():
        metadata = json.loads(old_json.read_text()).get("metadata")

    summaries = []
    for cell in sorted(batch_dir.iterdir()):
        eval_path = cell / "evaluation.json"
        if not cell.is_dir() or not eval_path.exists():
            continue
        doc = json.loads(eval_path.read_text())
        summary = doc.get("summary")
        if not isinstance(summary, dict):
            logger.warning("no summary in %s; skipped", eval_path)
            continue
        summary = dict(summary)
        summary.setdefault("label", cell.name)
        summaries.append(summary)

    if not summaries:
        raise SystemExit(f"no cell evaluations under {batch_dir}")
    write_batch_summary(summaries, batch_dir, metadata=metadata)
    logger.info("%s: rebuilt from %d cells", batch_dir, len(summaries))
    return len(summaries)


def main() -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dirs", nargs="*", default=DEFAULT_DIRS,
                    help="Batch directories to rebuild (repo-relative).")
    args = ap.parse_args()
    for rel in args.dirs:
        rebuild(PROJECT_ROOT / rel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
