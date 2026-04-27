#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_recovery_meta.py — Merge a proposer recovery meta.json into the original
==============================================================================

.. note::

    New runs no longer need this script; resume-mode merging is automatic
    (see ``scripts.lib_llm_metadata.merge_meta_into_existing``, called from
    both ``4_detect_mounds_batch.py`` and ``lib_batch_api.py`` at write
    time). This CLI remains for already-corrupted historical runs.

Purpose
-------
After a single-round proposer recovery (resume against an existing GeoJSON),
the per-pass ``meta.json`` written by ``4_detect_mounds_batch.py`` contains
ONLY the recovery-run statistics (typically a handful of tiles), overwriting
the original 8541-tile run statistics. This breaks downstream cost
aggregation (``run_generalisation.py aggregate-cost``) which reads tokens,
duration, and cost from the per-pass meta files.

This script merges the recovery meta into the original (pre-recovery) meta:

- ``execution_stats``:
    - ``items_processed`` = original + recovery
    - ``items_failed``    = recovery (only what is still failing)
    - ``items_skipped``   = original + recovery
    - ``retries_*``        = original + recovery
    - ``finish_reason_counts`` = element-wise sum
    - ``safety_blocks``, ``parse_failures``, ``empty_responses`` = sum
    - ``completed_items`` = original + recovered
    - ``failed_items``    = recovery only (still-failing IDs)
    - ``retry_details``   = original + recovery

- ``usage_stats``:
    - ``total_*_tokens``  = original + recovery
    - ``by_provider``     = element-wise sum

- ``timestamp``:
    - ``start``               = original.start
    - ``end``                 = recovery.end
    - ``duration_seconds``    = original + recovery durations

- ``cost_estimate``:
    - all numeric fields   = original + recovery

- ``per_item_metadata``: original + recovery (recovered items have updated
  per-item entries; original failed items remain in original metadata).
  Duplicates by ``item_id`` are resolved to the recovery entry (latest).

- Other top-level fields (run_id, environment, configuration, results_summary,
  tpm_governor): kept from original. A ``recovery_history`` field is appended
  to track the merge (initial_failed, recovered, still_failing IDs, recovery
  cost, recovery timestamp).

Usage
-----
    python3 scripts/merge_recovery_meta.py \\
        --backup path/to/meta.json.pre-recovery-{ts}.backup \\
        --recovery path/to/meta.json  (the recovery-only meta written by 4_detect_mounds_batch.py) \\
        --output path/to/meta.json    (merged output, overwriting recovery)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure the project root is on sys.path so ``scripts`` is importable
# even when this file is invoked directly (``python3 scripts/...``).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# The merge logic now lives in the shared metadata module; this script
# is preserved as a thin CLI wrapper for repairing historical runs whose
# meta.json files were overwritten before the in-line merge was added.
from scripts.lib_llm_metadata import merge_meta  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--backup", required=True, type=Path,
        help="Path to the pre-recovery meta.json backup",
    )
    parser.add_argument(
        "--recovery", required=True, type=Path,
        help="Path to the recovery meta.json (post-resume)",
    )
    parser.add_argument(
        "--output", required=True, type=Path,
        help="Output path for the merged meta.json (typically same as recovery)",
    )
    args = parser.parse_args()

    with open(args.backup) as f:
        original = json.load(f)
    with open(args.recovery) as f:
        recovery = json.load(f)

    merged = merge_meta(original, recovery)

    # Atomic write
    tmp_path = args.output.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(merged, f, indent=2)
    tmp_path.rename(args.output)

    # Brief summary
    es = merged.get("execution_stats", {})
    ce = merged.get("cost_estimate", {})
    print(f"Merged → {args.output}")
    print(f"  items_processed: {es.get('items_processed')}")
    print(f"  items_failed:    {es.get('items_failed')}")
    print(f"  total_cost_usd:  {ce.get('total_cost_usd'):.4f}")
    rh = merged.get("recovery_history", [])
    if rh:
        latest = rh[-1]
        print(
            f"  recovery: initial={latest['initial_failed']}, "
            f"recovered={latest['recovered']}, "
            f"still_failing={latest['still_failing']}"
        )


if __name__ == "__main__":
    main()
