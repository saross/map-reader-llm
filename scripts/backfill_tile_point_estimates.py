#!/usr/bin/env python3
"""Backfill observed tile-metric points into point-less evaluations (D30).

Forty-seven committed evaluations predate the ``point`` field in their
``tile_classification`` metric blocks, carrying only the bootstrap-resample
``mean`` beside the CI bounds. Every consumer that prefers the observed
statistic then falls back to the resample mean for exactly these files —
which is how 21 mean-valued cells re-entered a rebuilt batch roll-up during
the Session 137 audit remediation.

The observed values are recoverable exactly: each block's own committed
``confusion`` counts determine MCC, sensitivity, and specificity, and the
recomputation matches the stored ``point`` to 4 d.p. on all 1,391 committed
evaluations that carry both (verified during the Phase 5 migration). This
script inserts the recomputed ``point`` (rounded to 4 d.p., matching the
writer) into every summary and per-run metric block that has a ``mean`` but
no ``point`` and does carry a confusion matrix. A vanishing marginal yields
``point: None``, never 0 (erratum E81). ``archive/**`` is excluded, matching
the campaign's other migrations (E82 scope precedent).

Usage::

    python scripts/backfill_tile_point_estimates.py --dry-run
    python scripts/backfill_tile_point_estimates.py --write

$0 API; local; idempotent. Created 2026-08-20 (Session 138).
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

METRICS = ("mcc", "sensitivity", "specificity")


def points_from_confusion(conf: dict) -> dict[str, float | None]:
    """Observed MCC/sensitivity/specificity from a 2x2 confusion block.

    Any vanishing denominator yields ``None`` (erratum E81), never 0.
    """
    tp, tn = conf.get("tp"), conf.get("tn")
    fp, fn = conf.get("fp"), conf.get("fn")
    if None in (tp, tn, fp, fn):
        return {m: None for m in METRICS}
    denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    mcc = ((tp * tn - fp * fn) / math.sqrt(denom)) if denom > 0 else None
    sens = tp / (tp + fn) if (tp + fn) > 0 else None
    spec = tn / (tn + fp) if (tn + fp) > 0 else None
    r = lambda v: None if v is None else round(v, 4)  # noqa: E731
    return {"mcc": r(mcc), "sensitivity": r(sens), "specificity": r(spec)}


def backfill_block(tc: dict) -> int:
    """Insert missing ``point`` fields into one tile_classification block."""
    conf = tc.get("confusion")
    if not isinstance(conf, dict):
        return 0
    points = points_from_confusion(conf)
    n = 0
    for metric in METRICS:
        block = tc.get(metric)
        if isinstance(block, dict) and "mean" in block and "point" not in block:
            block["point"] = points[metric]
            n += 1
    return n


def backfill_doc(doc: dict) -> int:
    """Backfill every metric block in one evaluation document."""
    n = 0
    summary = doc.get("summary")
    if isinstance(summary, dict) and isinstance(
            summary.get("tile_classification"), dict):
        n += backfill_block(summary["tile_classification"])
    for run in doc.get("per_run") or []:
        if isinstance(run, dict) and isinstance(
                run.get("tile_classification"), dict):
            n += backfill_block(run["tile_classification"])
    return n


def main() -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = ap.parse_args()

    tracked = [
        rel for rel in subprocess.run(
            ["git", "ls-files", "*evaluation.json"],
            capture_output=True, text=True, check=True, cwd=PROJECT_ROOT,
        ).stdout.split()
        if not rel.startswith("archive/")
    ]
    n_files = n_fields = 0
    for rel in tracked:
        path = PROJECT_ROOT / rel
        original = path.read_text()
        doc = json.loads(original)
        n = backfill_doc(doc)
        if n:
            n_files += 1
            n_fields += n
            print(f"  {rel}: +{n} point field(s)")
            if args.write:
                trailing = "\n" if original.endswith("\n") else ""
                path.write_text(json.dumps(doc, indent=2) + trailing)
    print(f"files: {n_files}; point fields inserted: {n_fields}"
          f"{' (dry run)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
