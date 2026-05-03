#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_meta_failed_items.py — Retrospective cleanup of stale ``failed_items[]``
==============================================================================

Purpose
-------
Some per-pass ``*.meta.json`` files written by ``4_detect_mounds_batch.py``
contain stale entries in ``execution_stats.failed_items[]`` — items that were
recovered out-of-band (i.e., not via ``scripts.lib_llm_metadata.merge_meta``)
and therefore appear in BOTH ``completed_items`` and ``failed_items``. Future
audits that sum ``failed_items`` across per-pass metas to estimate outstanding
failures are misled by this drift.

This script reconciles the two lists. It treats ``completed_items`` as the
canonical "currently processed" record and rewrites ``failed_items`` to
contain only the truly-outstanding tiles (those NOT in ``completed_items``).
Any entries removed from ``failed_items`` are recorded in
``recovery_history[]`` as a synthetic retrospective-cleanup entry, preserving
the audit trail per the project's "preserve, don't discard" heuristic.

Cleanup contract
----------------
For each meta:

1. ``failed_items[]`` (post-cleanup) = subset of the ORIGINAL
   ``failed_items[]`` whose ``item_id`` does NOT appear in
   ``completed_items`` — i.e., truly-outstanding failures.
2. ``items_failed`` is updated to ``len(new failed_items)``.
3. Stale entries (those in both lists) are appended to
   ``recovery_history[]`` as a single new entry tagged
   ``source: "retrospective_cleanup"`` listing the recovered IDs.
4. **Cumulative-historical fields** (``parse_failures``, ``empty_responses``,
   ``finish_reason_counts``, ``safety_blocks``, ``retries_*``) are NOT
   mutated — they reflect the API-call history, not current item state.
5. **Idempotent**: if there is no overlap, the script is a no-op (no
   backup written, no fields modified, ``recovery_history`` not appended).
6. A per-file backup is written before any in-place edit using the
   project convention ``*.pre-meta-cleanup-<TIMESTAMP>.backup``.

Usage
-----
Single file::

    python3 scripts/clean_meta_failed_items.py path/to/meta.json

Recursive directory cleanup (all ``*.meta.json`` under root)::

    python3 scripts/clean_meta_failed_items.py outputs/some-corpus/proposer/

Dry-run audit (report only, no writes)::

    python3 scripts/clean_meta_failed_items.py --dry-run outputs/

Author: Claude Code (worktree-isolated cleanup task)
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Marker tag so future invocations can recognise their own work and stay idempotent.
RETROSPECTIVE_CLEANUP_SOURCE = "retrospective_cleanup"
BACKUP_TAG = "pre-meta-cleanup"


def _failed_item_id(entry: Any) -> str | None:
    """Return the ``item_id`` for a ``failed_items`` entry.

    The entry can be either a dict (the canonical schema) or a bare string
    (legacy/edge-case). Returns ``None`` if no identifier can be extracted.
    """
    if isinstance(entry, dict):
        return entry.get("item_id")
    if isinstance(entry, str):
        return entry
    return None


def clean_meta(
    meta: dict[str, Any],
    *,
    now_iso: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a cleaned copy of ``meta`` plus a per-file summary.

    Args:
        meta: The loaded meta dict (mutated copy returned, not the input).
        now_iso: Override ISO-8601 timestamp for the synthetic
            ``recovery_history`` entry. Useful for deterministic tests.

    Returns:
        A two-tuple of:

        - The cleaned meta dict. If no overlap exists the input is returned
          unchanged (same object reference; no copy made — the caller can
          rely on identity to detect a no-op).
        - A summary dict with keys: ``original_failed`` (int),
          ``stale_recovered`` (int), ``truly_outstanding`` (int),
          ``recovered_ids`` (list[str]), and ``noop`` (bool).
    """
    es = meta.get("execution_stats", {})
    original_failed = list(es.get("failed_items", []))
    completed = set(es.get("completed_items", []) or [])

    # Partition: stale (in completed) vs outstanding (not in completed).
    stale: list[dict[str, Any]] = []
    outstanding: list[dict[str, Any]] = []
    stale_ids: list[str] = []
    for entry in original_failed:
        item_id = _failed_item_id(entry)
        if item_id is not None and item_id in completed:
            stale.append(entry)
            stale_ids.append(item_id)
        else:
            outstanding.append(entry)

    summary = {
        "original_failed": len(original_failed),
        "stale_recovered": len(stale),
        "truly_outstanding": len(outstanding),
        "recovered_ids": sorted(set(stale_ids)),
        "noop": len(stale) == 0,
    }

    # Idempotent no-op: nothing to clean, return input unmodified.
    if not stale:
        return meta, summary

    # Deep-ish copy of the parts we mutate. Other top-level keys are shared
    # (they're not modified), keeping memory use proportional to changes.
    cleaned = dict(meta)
    cleaned_es = dict(es)
    cleaned_es["failed_items"] = outstanding
    cleaned_es["items_failed"] = len(outstanding)
    cleaned["execution_stats"] = cleaned_es

    # Append a synthetic recovery_history entry capturing the cleanup.
    iso = now_iso or datetime.now(timezone.utc).isoformat()
    history = list(cleaned.get("recovery_history", []) or [])
    history.append({
        "timestamp": iso,
        "source": RETROSPECTIVE_CLEANUP_SOURCE,
        "initial_failed": len(original_failed),
        "recovered": len(stale),
        "still_failing": len(outstanding),
        "recovered_ids": sorted(set(stale_ids)),
        "still_failing_ids": sorted(
            _failed_item_id(e) or "" for e in outstanding
        ),
        "note": (
            "Cleaned by scripts/clean_meta_failed_items.py — historical "
            "drift between failed_items[] and completed_items[]; no new "
            "API calls were made. Cumulative-historical counters "
            "(parse_failures, empty_responses, finish_reason_counts, "
            "safety_blocks, retries_*) intentionally unchanged."
        ),
    })
    cleaned["recovery_history"] = history

    return cleaned, summary


def _backup_path(meta_path: Path, ts: str) -> Path:
    """Return the per-file backup path using the project convention."""
    return meta_path.with_suffix(f".json.{BACKUP_TAG}-{ts}.backup")


def process_meta_file(
    meta_path: Path,
    *,
    dry_run: bool = False,
    backup_ts: str | None = None,
) -> dict[str, Any]:
    """Load, clean, and (unless ``dry_run``) write back a single meta file.

    Returns the per-file summary from :func:`clean_meta` augmented with the
    ``path`` (str) and ``backup_path`` (str | None when no-op or dry-run).
    """
    with open(meta_path) as f:
        meta = json.load(f)

    cleaned, summary = clean_meta(meta)
    summary = dict(summary)
    summary["path"] = str(meta_path)
    summary["backup_path"] = None

    if summary["noop"] or dry_run:
        return summary

    # Write backup, then atomic rewrite of the meta.
    ts = backup_ts or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup = _backup_path(meta_path, ts)
    with open(backup, "w") as f:
        json.dump(meta, f, indent=2)
    summary["backup_path"] = str(backup)

    tmp_path = meta_path.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(cleaned, f, indent=2)
    tmp_path.rename(meta_path)

    return summary


def discover_meta_files(root: Path) -> list[Path]:
    """Return all ``*.meta.json`` files at or beneath ``root``.

    If ``root`` is itself a meta file, return ``[root]``.
    """
    if root.is_file():
        return [root]
    return sorted(root.rglob("*.meta.json"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths", nargs="+", type=Path,
        help="One or more meta files OR directories to recurse into.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report what would change without writing any files.",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress per-file output; print only the aggregate summary.",
    )
    args = parser.parse_args(argv)

    # Single timestamp shared across the run so all backups in one pass agree.
    backup_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    targets: list[Path] = []
    for p in args.paths:
        targets.extend(discover_meta_files(p))

    if not targets:
        print("No *.meta.json files found.", file=sys.stderr)
        return 1

    aggregate = {
        "files_scanned": 0,
        "files_changed": 0,
        "items_recovered_total": 0,
        "items_still_outstanding_total": 0,
    }

    for mp in targets:
        try:
            s = process_meta_file(mp, dry_run=args.dry_run, backup_ts=backup_ts)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"  SKIP (read error): {mp} — {exc}", file=sys.stderr)
            continue

        aggregate["files_scanned"] += 1
        aggregate["items_still_outstanding_total"] += s["truly_outstanding"]
        if not s["noop"]:
            aggregate["files_changed"] += 1
            aggregate["items_recovered_total"] += s["stale_recovered"]

        if not args.quiet:
            tag = "NOOP" if s["noop"] else ("DRYRUN" if args.dry_run else "WROTE")
            print(
                f"  [{tag}] {mp}: original_failed={s['original_failed']} "
                f"stale_recovered={s['stale_recovered']} "
                f"truly_outstanding={s['truly_outstanding']}"
            )

    print()
    print("Aggregate:")
    print(f"  files_scanned:                   {aggregate['files_scanned']}")
    print(f"  files_changed:                   {aggregate['files_changed']}")
    print(f"  items_recovered_total:           {aggregate['items_recovered_total']}")
    print(f"  items_still_outstanding_total:   {aggregate['items_still_outstanding_total']}")
    if args.dry_run:
        print("  (dry-run — no files were modified)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
