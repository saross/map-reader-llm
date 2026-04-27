#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_recovery_meta.py — Merge a proposer recovery meta.json into the original
==============================================================================

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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _sum_dicts(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Element-wise sum two dicts of numeric values; missing keys treated as 0."""
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict):
            out[k] = _sum_dicts(out.get(k, {}), v)
        else:
            out[k] = (out.get(k, 0) or 0) + (v or 0)
    return out


def merge_meta(original: dict[str, Any], recovery: dict[str, Any]) -> dict[str, Any]:
    """Merge a recovery meta.json into an original meta.json.

    See module docstring for field-by-field semantics.

    Args:
        original: The pre-recovery meta.json contents.
        recovery: The post-recovery meta.json contents (only the recovery run).

    Returns:
        Merged meta dict.
    """
    merged = dict(original)  # shallow copy at top level

    # ---- timestamp: start from original, end from recovery, durations sum ----
    o_ts = original.get("timestamp", {})
    r_ts = recovery.get("timestamp", {})
    merged["timestamp"] = {
        "start": o_ts.get("start"),
        "end": r_ts.get("end") or o_ts.get("end"),
        "duration_seconds": (
            (o_ts.get("duration_seconds") or 0.0)
            + (r_ts.get("duration_seconds") or 0.0)
        ),
    }

    # ---- execution_stats ----
    o_es = original.get("execution_stats", {})
    r_es = recovery.get("execution_stats", {})
    o_completed = list(o_es.get("completed_items", []))
    r_completed = list(r_es.get("completed_items", []))
    # Combine completed items, dedup by ID (recovery wins on duplicate)
    seen = set()
    combined_completed: list[str] = []
    for item in o_completed + r_completed:
        if item not in seen:
            combined_completed.append(item)
            seen.add(item)

    # The recovery-run's failed_items represents the residual still-failing
    # tiles. The original's failed_items is now obsolete (most/all recovered).
    r_failed = list(r_es.get("failed_items", []))

    merged["execution_stats"] = {
        "items_processed": (
            (o_es.get("items_processed") or 0)
            + (r_es.get("items_processed") or 0)
        ),
        "items_failed": len(r_failed),
        "items_skipped": (
            (o_es.get("items_skipped") or 0)
            + (r_es.get("items_skipped") or 0)
        ),
        "retries_total": (
            (o_es.get("retries_total") or 0)
            + (r_es.get("retries_total") or 0)
        ),
        "retries_rate_limit": (
            (o_es.get("retries_rate_limit") or 0)
            + (r_es.get("retries_rate_limit") or 0)
        ),
        "retries_server_error": (
            (o_es.get("retries_server_error") or 0)
            + (r_es.get("retries_server_error") or 0)
        ),
        "retries_timeout": (
            (o_es.get("retries_timeout") or 0)
            + (r_es.get("retries_timeout") or 0)
        ),
        "retries_other": (
            (o_es.get("retries_other") or 0)
            + (r_es.get("retries_other") or 0)
        ),
        "finish_reason_counts": _sum_dicts(
            o_es.get("finish_reason_counts", {}),
            r_es.get("finish_reason_counts", {}),
        ),
        "safety_blocks": (
            (o_es.get("safety_blocks") or 0)
            + (r_es.get("safety_blocks") or 0)
        ),
        "parse_failures": (
            (o_es.get("parse_failures") or 0)
            + (r_es.get("parse_failures") or 0)
        ),
        "empty_responses": (
            (o_es.get("empty_responses") or 0)
            + (r_es.get("empty_responses") or 0)
        ),
        "completed_items": combined_completed,
        "failed_items": r_failed,
        "retry_details": (
            list(o_es.get("retry_details", []))
            + list(r_es.get("retry_details", []))
        ),
    }

    # ---- usage_stats: sum tokens ----
    o_us = original.get("usage_stats", {})
    r_us = recovery.get("usage_stats", {})
    merged["usage_stats"] = _sum_dicts(o_us, r_us)
    # _sum_dicts may have inadvertently summed numeric fields inside
    # by_provider — that's correct behaviour for token counts and request counts.

    # ---- cost_estimate: sum numeric fields, keep pricing_used from original ----
    o_ce = original.get("cost_estimate", {}) or {}
    r_ce = recovery.get("cost_estimate", {}) or {}
    merged["cost_estimate"] = {
        "input_cost_usd": (
            (o_ce.get("input_cost_usd") or 0.0)
            + (r_ce.get("input_cost_usd") or 0.0)
        ),
        "output_cost_usd": (
            (o_ce.get("output_cost_usd") or 0.0)
            + (r_ce.get("output_cost_usd") or 0.0)
        ),
        "total_cost_usd": (
            (o_ce.get("total_cost_usd") or 0.0)
            + (r_ce.get("total_cost_usd") or 0.0)
        ),
        "pricing_used": o_ce.get("pricing_used") or r_ce.get("pricing_used"),
    }

    # ---- per_item_metadata: combine, recovery wins on duplicate item_id ----
    o_pim = original.get("per_item_metadata", []) or []
    r_pim = recovery.get("per_item_metadata", []) or []
    # Build dict by item_id; recovery overwrites original
    combined_pim: dict[str, dict[str, Any]] = {}
    for item in o_pim:
        iid = item.get("item_id")
        if iid:
            combined_pim[iid] = item
    for item in r_pim:
        iid = item.get("item_id")
        if iid:
            combined_pim[iid] = item
    # Preserve original ordering, append new items at the end
    merged_pim: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in o_pim:
        iid = item.get("item_id")
        if iid:
            merged_pim.append(combined_pim[iid])
            seen_ids.add(iid)
    for iid, item in combined_pim.items():
        if iid not in seen_ids:
            merged_pim.append(item)
    merged["per_item_metadata"] = merged_pim

    # ---- recovery_history: track the merge operation ----
    initial_failed_ids = sorted(
        fi["item_id"] if isinstance(fi, dict) else fi
        for fi in o_es.get("failed_items", [])
    )
    still_failing_ids = sorted(
        fi["item_id"] if isinstance(fi, dict) else fi
        for fi in r_failed
    )
    recovered_ids = sorted(set(initial_failed_ids) - set(still_failing_ids))

    history = list(merged.get("recovery_history", []))
    history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "initial_failed": len(initial_failed_ids),
        "recovered": len(recovered_ids),
        "still_failing": len(still_failing_ids),
        "still_failing_ids": still_failing_ids,
        "recovered_ids": recovered_ids,
        "recovery_cost_usd": r_ce.get("total_cost_usd"),
        "recovery_duration_seconds": r_ts.get("duration_seconds"),
        "recovery_run_id": recovery.get("run_id"),
    })
    merged["recovery_history"] = history

    # tpm_governor: keep original (recovery's small run governor stats not
    # meaningful at scale). If recovery has one, append as a list.
    if "tpm_governor" in recovery:
        merged.setdefault("tpm_governor_recovery", []).append(
            recovery["tpm_governor"],
        )

    # results_summary: keep original (recovery may overwrite or be empty)
    if recovery.get("results_summary"):
        # Element-wise merge would be domain-specific; keep originals and
        # store the recovery summary alongside if non-empty.
        merged.setdefault("results_summary_recovery", []).append(
            recovery["results_summary"],
        )

    return merged


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
