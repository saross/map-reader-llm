"""
Tier-1 tests for ``scripts.clean_meta_failed_items`` and the defensive
cleanup baked into ``scripts.lib_llm_metadata.merge_meta``.

These tests guard the post-recovery contract that:

1. ``failed_items[]`` reflects ONLY truly-outstanding failures (item_ids
   not in ``completed_items``).
2. Stale entries (item_id present in BOTH lists) are moved into
   ``recovery_history[]`` so the audit trail is preserved.
3. Cumulative-historical counters (``parse_failures``, ``empty_responses``,
   ``finish_reason_counts``, ``safety_blocks``, ``retries_*``) are NOT
   mutated by the cleanup — they reflect API-call history.
4. Cleanup is idempotent: running it twice produces the same result and
   the second run is a no-op.

See also:
    - ``tests/test_merge_meta.py`` — the field-by-field merge contract.
    - ``scripts/clean_meta_failed_items.py`` — the cleanup module docstring.
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

# Project root on path so the ``scripts.`` package imports cleanly.
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.clean_meta_failed_items import (  # noqa: E402
    RETROSPECTIVE_CLEANUP_SOURCE,
    clean_meta,
    process_meta_file,
)
from scripts.lib_llm_metadata import merge_meta  # noqa: E402


# =========================================================================
# FIXTURE BUILDERS
# =========================================================================


def _failed_entry(item_id: str, reason: str = "JSON parse error") -> dict[str, Any]:
    """Construct a single ``failed_items`` entry in the canonical shape."""
    return {
        "item_id": item_id,
        "reason": reason,
        "timestamp": "2026-04-18T10:15:24+00:00",
    }


def _make_meta(
    *,
    completed_items: list[str],
    failed_items: list[dict[str, Any]],
    parse_failures: int = 7,
    empty_responses: int = 3,
    finish_reason_counts: dict[str, int] | None = None,
    safety_blocks: int = 1,
    retries_total: int = 42,
) -> dict[str, Any]:
    """Build a meta dict with the minimum fields needed by the cleanup.

    Cumulative-historical counters carry deliberately non-zero default
    values so we can assert they survive cleanup unchanged.
    """
    return {
        "run_id": "fixture-run",
        "execution_stats": {
            "items_processed": len(completed_items),
            "items_failed": len(failed_items),
            "items_skipped": 0,
            "retries_total": retries_total,
            "retries_rate_limit": 0,
            "retries_server_error": 0,
            "retries_timeout": 0,
            "retries_other": retries_total,
            "finish_reason_counts": (
                finish_reason_counts
                if finish_reason_counts is not None
                else {"success": len(completed_items)}
            ),
            "safety_blocks": safety_blocks,
            "parse_failures": parse_failures,
            "empty_responses": empty_responses,
            "completed_items": list(completed_items),
            "failed_items": list(failed_items),
            "retry_details": [],
        },
    }


# =========================================================================
# 1. CLEANUP CONTRACT
# =========================================================================


@pytest.mark.tier1
class TestCleanMetaContract:
    """Field-by-field tests of the cleanup contract."""

    def test_all_failed_items_recovered_clears_list(self) -> None:
        # All three failed_items appear in completed_items → all stale.
        meta = _make_meta(
            completed_items=["a", "b", "c"],
            failed_items=[_failed_entry("a"), _failed_entry("b"), _failed_entry("c")],
        )
        cleaned, summary = clean_meta(meta, now_iso="2026-05-03T00:00:00+00:00")

        assert summary["original_failed"] == 3
        assert summary["stale_recovered"] == 3
        assert summary["truly_outstanding"] == 0
        assert summary["noop"] is False

        es = cleaned["execution_stats"]
        assert es["failed_items"] == []
        assert es["items_failed"] == 0
        # completed_items is untouched.
        assert es["completed_items"] == ["a", "b", "c"]

    def test_some_failed_items_recovered_keeps_truly_outstanding(self) -> None:
        # "a" and "b" recovered; "x" still missing.
        meta = _make_meta(
            completed_items=["a", "b", "c"],
            failed_items=[_failed_entry("a"), _failed_entry("b"), _failed_entry("x")],
        )
        cleaned, summary = clean_meta(meta)

        assert summary["original_failed"] == 3
        assert summary["stale_recovered"] == 2
        assert summary["truly_outstanding"] == 1

        es = cleaned["execution_stats"]
        outstanding_ids = [fi["item_id"] for fi in es["failed_items"]]
        assert outstanding_ids == ["x"]
        assert es["items_failed"] == 1

    def test_no_failed_items_is_noop(self) -> None:
        # Empty failed_items → no work to do.
        meta = _make_meta(completed_items=["a", "b"], failed_items=[])
        cleaned, summary = clean_meta(meta)

        assert summary["noop"] is True
        # Same object reference signals true no-op.
        assert cleaned is meta
        # No recovery_history added.
        assert "recovery_history" not in cleaned

    def test_no_overlap_is_noop(self) -> None:
        # Failed items truly outstanding (not in completed) → no-op.
        meta = _make_meta(
            completed_items=["a", "b"],
            failed_items=[_failed_entry("zzz")],
        )
        cleaned, summary = clean_meta(meta)

        assert summary["noop"] is True
        assert cleaned is meta

    def test_recovery_history_appended_with_cleanup_source(self) -> None:
        # Cleanup must tag its synthetic entry so audit code can identify
        # retrospective vs API-driven recoveries.
        meta = _make_meta(
            completed_items=["a"],
            failed_items=[_failed_entry("a")],
        )
        cleaned, _ = clean_meta(meta, now_iso="2026-05-03T00:00:00+00:00")

        history = cleaned["recovery_history"]
        assert len(history) == 1
        entry = history[0]
        assert entry["source"] == RETROSPECTIVE_CLEANUP_SOURCE
        assert entry["initial_failed"] == 1
        assert entry["recovered"] == 1
        assert entry["still_failing"] == 0
        assert entry["recovered_ids"] == ["a"]
        assert entry["timestamp"] == "2026-05-03T00:00:00+00:00"
        assert "note" in entry

    def test_cumulative_historical_counters_unchanged(self) -> None:
        # parse_failures, empty_responses, finish_reason_counts,
        # safety_blocks, retries_* must NEVER be mutated by cleanup.
        meta = _make_meta(
            completed_items=["a", "b"],
            failed_items=[_failed_entry("a"), _failed_entry("b")],
            parse_failures=11,
            empty_responses=4,
            finish_reason_counts={"success": 95, "error": 5},
            safety_blocks=2,
            retries_total=37,
        )
        cleaned, _ = clean_meta(meta)
        es = cleaned["execution_stats"]

        assert es["parse_failures"] == 11
        assert es["empty_responses"] == 4
        assert es["finish_reason_counts"] == {"success": 95, "error": 5}
        assert es["safety_blocks"] == 2
        assert es["retries_total"] == 37

    def test_idempotent_repeat_cleanup_is_noop(self) -> None:
        # Running cleanup twice must be a no-op the second time.
        meta = _make_meta(
            completed_items=["a", "b"],
            failed_items=[_failed_entry("a"), _failed_entry("b")],
        )
        cleaned_once, summary_once = clean_meta(meta)
        cleaned_twice, summary_twice = clean_meta(cleaned_once)

        assert summary_once["noop"] is False
        assert summary_twice["noop"] is True
        # No new recovery_history entry on the second pass.
        assert len(cleaned_twice["recovery_history"]) == 1

    def test_handles_bare_string_failed_items(self) -> None:
        # Some legacy metas store failed_items as bare strings, not dicts.
        meta = _make_meta(
            completed_items=["a", "b"],
            failed_items=[],
        )
        # Override with strings (not dicts).
        meta["execution_stats"]["failed_items"] = ["a", "b"]
        cleaned, summary = clean_meta(meta)

        assert summary["stale_recovered"] == 2
        assert cleaned["execution_stats"]["failed_items"] == []


# =========================================================================
# 2. FILE-LEVEL PROCESSING (process_meta_file)
# =========================================================================


@pytest.mark.tier1
class TestProcessMetaFile:
    """Tests for the file-level read/write path with backup creation."""

    def _write_meta(self, path: Path, meta: dict[str, Any]) -> None:
        with open(path, "w") as f:
            json.dump(meta, f, indent=2)

    def test_writes_backup_and_cleans_in_place(self, tmp_path: Path) -> None:
        meta_path = tmp_path / "x.meta.json"
        meta = _make_meta(
            completed_items=["a"],
            failed_items=[_failed_entry("a")],
        )
        original_bytes = json.dumps(meta, indent=2).encode()
        self._write_meta(meta_path, meta)

        summary = process_meta_file(meta_path)

        assert summary["noop"] is False
        backup = Path(summary["backup_path"])
        assert backup.exists()
        # Backup matches original byte-for-byte.
        assert backup.read_bytes() == original_bytes

        # On-disc meta is now cleaned.
        with open(meta_path) as f:
            cleaned = json.load(f)
        assert cleaned["execution_stats"]["items_failed"] == 0

    def test_dry_run_makes_no_writes(self, tmp_path: Path) -> None:
        meta_path = tmp_path / "x.meta.json"
        meta = _make_meta(
            completed_items=["a"],
            failed_items=[_failed_entry("a")],
        )
        self._write_meta(meta_path, meta)

        original_mtime = meta_path.stat().st_mtime
        summary = process_meta_file(meta_path, dry_run=True)

        assert summary["noop"] is False
        assert summary["stale_recovered"] == 1
        # No backup file created in dry-run.
        assert summary["backup_path"] is None
        # File untouched on disc.
        assert meta_path.stat().st_mtime == original_mtime
        backups = list(tmp_path.glob("*.backup"))
        assert backups == []

    def test_noop_writes_no_backup(self, tmp_path: Path) -> None:
        meta_path = tmp_path / "x.meta.json"
        meta = _make_meta(completed_items=["a"], failed_items=[])
        self._write_meta(meta_path, meta)

        summary = process_meta_file(meta_path)

        assert summary["noop"] is True
        assert summary["backup_path"] is None
        backups = list(tmp_path.glob("*.backup"))
        assert backups == []


# =========================================================================
# 3. PROSPECTIVE FIX — defensive cleanup inside merge_meta
# =========================================================================


@pytest.mark.tier1
class TestMergeMetaDefensiveCleanup:
    """``merge_meta`` should drop stale failed_items defensively."""

    def _bare_meta(
        self,
        *,
        completed_items: list[str],
        failed_items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        # A trimmed meta sufficient for merge_meta — minimal usage_stats etc.
        return {
            "run_id": "x",
            "timestamp": {
                "start": "2026-04-18T10:00:00+00:00",
                "end": "2026-04-18T11:00:00+00:00",
                "duration_seconds": 3600.0,
            },
            "execution_stats": {
                "items_processed": len(completed_items),
                "items_failed": len(failed_items),
                "items_skipped": 0,
                "retries_total": 0,
                "retries_rate_limit": 0,
                "retries_server_error": 0,
                "retries_timeout": 0,
                "retries_other": 0,
                "finish_reason_counts": {"success": len(completed_items)},
                "safety_blocks": 0,
                "parse_failures": 0,
                "empty_responses": 0,
                "completed_items": list(completed_items),
                "failed_items": list(failed_items),
                "retry_details": [],
            },
            "usage_stats": {},
            "cost_estimate": {"total_cost_usd": 0.0},
        }

    def test_merge_drops_failed_item_already_in_combined_completed(self) -> None:
        # Original failed: t1, t2. Recovery completed t1 and t2 successfully,
        # but recovery's failed_items[] still lists t2 (stale). After merge,
        # t2 should NOT appear in failed_items because t2 is in combined
        # completed_items.
        original = self._bare_meta(
            completed_items=["other-1", "other-2"],
            failed_items=[_failed_entry("t1"), _failed_entry("t2")],
        )
        recovery = self._bare_meta(
            completed_items=["t1", "t2"],
            failed_items=[_failed_entry("t2")],  # stale
        )
        merged = merge_meta(deepcopy(original), deepcopy(recovery))

        es = merged["execution_stats"]
        outstanding_ids = [fi["item_id"] for fi in es["failed_items"]]
        # t2 is in combined completed_items → defensively dropped.
        assert outstanding_ids == []
        assert es["items_failed"] == 0

        # Audit trail: the synthetic recovery_history entry must record
        # the defensive recovery.
        rh = merged["recovery_history"]
        assert len(rh) == 1
        entry = rh[0]
        assert entry["defensively_recovered"] == 1
        assert entry["defensively_recovered_ids"] == ["t2"]

    def test_merge_keeps_truly_outstanding_failures(self) -> None:
        # Recovery still has a genuinely-failed tile not in any completed list.
        original = self._bare_meta(
            completed_items=["other"],
            failed_items=[_failed_entry("t1")],
        )
        recovery = self._bare_meta(
            completed_items=["t1"],
            failed_items=[_failed_entry("z-genuinely-broken")],
        )
        merged = merge_meta(deepcopy(original), deepcopy(recovery))
        es = merged["execution_stats"]
        outstanding = [fi["item_id"] for fi in es["failed_items"]]
        assert outstanding == ["z-genuinely-broken"]
        # No defensive recovery happened this time.
        rh_entry = merged["recovery_history"][0]
        assert "defensively_recovered" not in rh_entry

    def test_merge_no_defensive_action_when_no_stale_overlap(self) -> None:
        # Clean recovery: failed_items in recovery is disjoint from
        # combined_completed.
        original = self._bare_meta(
            completed_items=["a"],
            failed_items=[_failed_entry("b")],
        )
        recovery = self._bare_meta(
            completed_items=[],
            failed_items=[_failed_entry("b")],
        )
        merged = merge_meta(deepcopy(original), deepcopy(recovery))
        rh_entry = merged["recovery_history"][0]
        assert "defensively_recovered" not in rh_entry
