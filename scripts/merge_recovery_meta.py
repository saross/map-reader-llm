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


#: A recovery meta sharing more than this share of the original's completed
#: items is cumulative, not a recovery.
CUMULATIVE_OVERLAP = 0.5

#: Verifier metas name their items ``candidate_NNNNN``; proposer metas name tiles.
VERIFIER_ITEM_PREFIX = "candidate_"


def refuse_cumulative(original: dict, recovery: dict) -> None:
    """Refuse a "recovery" meta that already contains the original run.

    Since ``1ce1a982d`` (2026-04-27) a resume merges its usage into the
    existing meta automatically, so the meta a resume leaves behind is
    CUMULATIVE. Merging it into the pre-recovery backup again adds the
    original run twice: the 2026-05-02 recovery merge did exactly that and
    doubled every token class in the TH7 and IM metas
    (``reports/token-load-audit-2026-06-12.md`` §§ 3.2, 3.4). A genuine
    recovery-only meta holds just the re-sent tiles, so it shares almost no
    completed items with the original, and it carries its own ``run_id``
    (the automatic resume merge keeps the original's, so a shared ``run_id``
    means the meta already holds the original run).

    The script is for PROPOSER metas only. A verifier leg's cleanup merges
    itself (``run_pv.py cleanup`` through ``merge_cleanup_meta``), and its
    items are candidates, not tiles, so a verifier meta is refused.

    Args:
        original: The pre-recovery meta.
        recovery: The meta to merge in.

    Raises:
        SystemExit: When either meta is a verifier's, when the two share a
            ``run_id``, or when the recovery meta repeats more than half of
            the original's completed items.
    """
    done = set((original.get("execution_stats") or {}).get("completed_items") or [])
    again = set((recovery.get("execution_stats") or {}).get("completed_items") or [])
    for meta in (original, recovery):
        es = meta.get("execution_stats") or {}
        items = list(es.get("completed_items") or []) + list(es.get("failed_items") or [])
        if any(str(i).startswith(VERIFIER_ITEM_PREFIX) for i in items):
            raise SystemExit(
                "merge_recovery_meta: these are verifier metas (candidate items). The script "
                "merges proposer recoveries only; a verifier cleanup merges itself "
                "(run_pv.py cleanup).")
    run_id = original.get("run_id")
    if run_id and recovery.get("run_id") == run_id:
        raise SystemExit(
            f"merge_recovery_meta: the recovery meta carries the original's run_id ({run_id}), "
            "so it is cumulative (resume has merged automatically since 1ce1a982d). Merging "
            "it would count the original run twice; there is nothing to merge.")
    if done and len(done & again) > CUMULATIVE_OVERLAP * len(done):
        raise SystemExit(
            f"merge_recovery_meta: the recovery meta already holds {len(done & again):,} of "
            f"the original's {len(done):,} completed items, so it is cumulative (resume has "
            "merged automatically since 1ce1a982d). Merging it would count the original "
            "run twice; there is nothing to merge.")


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

    refuse_cumulative(original, recovery)
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
    from scripts.lib_cost import fmt_usd
    print(f"  total_cost_usd:  {fmt_usd(ce.get('total_cost_usd'))}")
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
