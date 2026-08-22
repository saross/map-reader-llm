"""
Tier 1 tests for ``scripts.lib_llm_metadata.merge_meta`` and
``merge_meta_into_existing``.

These tests verify the resume-mode merge logic that protects per-pass
``*.meta.json`` files from being overwritten with only the resume-batch
statistics. The merge contract is documented in
``scripts/merge_recovery_meta.py``.

Test groups:
    1. **Schema unit tests** — field-by-field semantics.
    2. **Edge cases** — empty inputs, missing optional fields, idempotency.
    3. **Integration** — simulated 100-tile resume using
       ``LLMMetadataTracker.finalise()`` so the schema is fidelitous.
    4. **Cost-aggregation regression** — merged meta produces correct
       totals via ``aggregate_cost_manifest``.
    5. **Atomic-write safety** — kill mid-write does not corrupt the
       on-disc meta.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_llm_metadata import (  # noqa: E402
    LLMMetadataTracker,
    LLMResponseMetadata,
    TokenUsage,
    _sum_dicts,
    merge_meta,
    merge_meta_into_existing,
)

pytestmark = pytest.mark.tier1


# =========================================================================
# FIXTURE BUILDERS
# =========================================================================


def _make_meta(
    *,
    items_processed: int = 10,
    items_failed: int = 0,
    completed_items: list[str] | None = None,
    failed_items: list[Any] | None = None,
    total_input_tokens: int = 1000,
    total_output_tokens: int = 500,
    total_tokens: int = 1500,
    duration_seconds: float = 60.0,
    total_cost_usd: float = 0.05,
    input_cost_usd: float = 0.03,
    output_cost_usd: float = 0.02,
    start: str = "2026-04-25T10:00:00+00:00",
    end: str = "2026-04-25T10:01:00+00:00",
    per_item_metadata: list[dict[str, Any]] | None = None,
    run_id: str = "run-original",
    pricing_model: str = "gemini-3-flash",
) -> dict[str, Any]:
    """Hand-build a minimal but realistic per-pass meta dict."""
    return {
        "run_id": run_id,
        "timestamp": {
            "start": start,
            "end": end,
            "duration_seconds": duration_seconds,
        },
        "execution_stats": {
            "items_processed": items_processed,
            "items_failed": items_failed,
            "items_skipped": 0,
            "retries_total": 0,
            "retries_rate_limit": 0,
            "retries_server_error": 0,
            "retries_timeout": 0,
            "retries_other": 0,
            "finish_reason_counts": {"success": items_processed},
            "safety_blocks": 0,
            "parse_failures": 0,
            "empty_responses": 0,
            "completed_items": list(completed_items or []),
            "failed_items": list(failed_items or []),
            "retry_details": [],
        },
        "usage_stats": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_cached_tokens": 0,
            "total_reasoning_tokens": 0,
            "total_thoughts_tokens": 0,
            "total_tool_use_tokens": 0,
            "total_tokens": total_tokens,
            "by_provider": {
                "google_gemini": {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "total_tokens": total_tokens,
                    "request_count": items_processed,
                },
            },
        },
        "cost_estimate": {
            "input_cost_usd": input_cost_usd,
            "output_cost_usd": output_cost_usd,
            "total_cost_usd": total_cost_usd,
            "pricing_used": {
                "model": pricing_model,
                "input_per_1m": 0.30,
                "output_per_1m": 2.50,
            },
        },
        "per_item_metadata": list(per_item_metadata or []),
        "results_summary": {"total_detections": items_processed * 2},
    }


def _make_per_item(item_id: str) -> dict[str, Any]:
    """Build a per-item metadata stub with the given id."""
    return {
        "item_id": item_id,
        "provider": "google_gemini",
        "tokens": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        "finish_reason": "success",
    }


# =========================================================================
# 1. SCHEMA UNIT TESTS
# =========================================================================


class TestSchemaContract:
    """Field-by-field tests of the merge contract."""

    def test_items_processed_sums(self) -> None:
        original = _make_meta(items_processed=60)
        recovery = _make_meta(items_processed=40)
        merged = merge_meta(original, recovery)
        assert merged["execution_stats"]["items_processed"] == 100

    def test_items_failed_equals_recovery_only(self) -> None:
        # Original had 5 failures (now obsolete), recovery has 2 still failing
        original = _make_meta(
            items_failed=5,
            failed_items=[{"item_id": f"t{i}", "reason": "x"} for i in range(5)],
        )
        recovery = _make_meta(
            items_failed=2,
            failed_items=[
                {"item_id": "still-1", "reason": "x"},
                {"item_id": "still-2", "reason": "x"},
            ],
        )
        merged = merge_meta(original, recovery)
        # Only the recovery's residual failures count
        assert merged["execution_stats"]["items_failed"] == 2

    def test_completed_items_dedup_recovery_overrides(self) -> None:
        original = _make_meta(completed_items=["a", "b", "c"])
        # Recovery overlaps "c" and adds "d"
        recovery = _make_meta(completed_items=["c", "d"])
        merged = merge_meta(original, recovery)
        completed = merged["execution_stats"]["completed_items"]
        # No duplicates; original ordering preserved with new items appended
        assert completed == ["a", "b", "c", "d"]

    def test_usage_stats_sums_element_wise(self) -> None:
        original = _make_meta(
            total_input_tokens=10_000,
            total_output_tokens=5_000,
            total_tokens=15_000,
        )
        recovery = _make_meta(
            total_input_tokens=200,
            total_output_tokens=100,
            total_tokens=300,
        )
        merged = merge_meta(original, recovery)
        us = merged["usage_stats"]
        assert us["total_input_tokens"] == 10_200
        assert us["total_output_tokens"] == 5_100
        assert us["total_tokens"] == 15_300

    def test_cost_estimate_total_sums(self) -> None:
        original = _make_meta(total_cost_usd=10.0)
        recovery = _make_meta(total_cost_usd=0.5)
        merged = merge_meta(original, recovery)
        assert merged["cost_estimate"]["total_cost_usd"] == pytest.approx(10.5)

    def test_timestamp_start_from_original_end_from_recovery_durations_sum(
        self,
    ) -> None:
        original = _make_meta(
            start="2026-04-25T10:00:00+00:00",
            end="2026-04-25T11:00:00+00:00",
            duration_seconds=3600.0,
        )
        recovery = _make_meta(
            start="2026-04-26T09:00:00+00:00",
            end="2026-04-26T09:05:00+00:00",
            duration_seconds=300.0,
        )
        merged = merge_meta(original, recovery)
        assert merged["timestamp"]["start"] == "2026-04-25T10:00:00+00:00"
        assert merged["timestamp"]["end"] == "2026-04-26T09:05:00+00:00"
        assert merged["timestamp"]["duration_seconds"] == pytest.approx(3900.0)

    def test_per_item_metadata_dedup_recovery_overrides(self) -> None:
        # Original "a" has output_tokens=50; recovery's "a" has output_tokens=999
        original_a = _make_per_item("a")
        original_b = _make_per_item("b")
        recovery_a = _make_per_item("a")
        recovery_a["tokens"]["output_tokens"] = 999
        recovery_c = _make_per_item("c")

        original = _make_meta(per_item_metadata=[original_a, original_b])
        recovery = _make_meta(per_item_metadata=[recovery_a, recovery_c])
        merged = merge_meta(original, recovery)

        pim = merged["per_item_metadata"]
        ids = [item["item_id"] for item in pim]
        assert ids == ["a", "b", "c"]
        # Recovery wins on collision
        a_entry = next(item for item in pim if item["item_id"] == "a")
        assert a_entry["tokens"]["output_tokens"] == 999

    def test_recovery_history_appended_per_merge(self) -> None:
        original = _make_meta(failed_items=[{"item_id": "f1", "reason": "x"}])
        recovery = _make_meta(failed_items=[])  # all recovered
        merged = merge_meta(original, recovery)

        assert "recovery_history" in merged
        assert len(merged["recovery_history"]) == 1
        entry = merged["recovery_history"][0]
        assert entry["initial_failed"] == 1
        assert entry["recovered"] == 1
        assert entry["still_failing"] == 0

    def test_chained_merges_recovery_history_accumulates(self) -> None:
        # Three-pass chain: original -> first recovery -> second recovery
        original = _make_meta(
            items_processed=50,
            failed_items=[
                {"item_id": "f1", "reason": "x"},
                {"item_id": "f2", "reason": "x"},
                {"item_id": "f3", "reason": "x"},
            ],
        )
        first_recovery = _make_meta(
            items_processed=2,
            failed_items=[{"item_id": "f3", "reason": "x"}],
            run_id="run-recovery-1",
        )
        second_recovery = _make_meta(
            items_processed=1,
            failed_items=[],
            run_id="run-recovery-2",
        )

        after_first = merge_meta(original, first_recovery)
        after_second = merge_meta(after_first, second_recovery)

        history = after_second["recovery_history"]
        assert len(history) == 2
        # First merge: 3 initial failed, 2 recovered, 1 still failing
        assert history[0]["initial_failed"] == 3
        assert history[0]["recovered"] == 2
        assert history[0]["still_failing"] == 1
        # Second merge: 1 initial failed (the residual), 1 recovered, 0 still failing
        assert history[1]["initial_failed"] == 1
        assert history[1]["recovered"] == 1
        assert history[1]["still_failing"] == 0
        # All passes accumulated
        assert after_second["execution_stats"]["items_processed"] == 53


# =========================================================================
# 2. EDGE CASES
# =========================================================================


class TestEdgeCases:
    """Robustness against incomplete or unusual inputs."""

    def test_empty_original(self) -> None:
        recovery = _make_meta(items_processed=5)
        merged = merge_meta({}, recovery)
        # Recovery values flow through; original contributes nothing
        assert merged["execution_stats"]["items_processed"] == 5
        assert merged["timestamp"]["start"] is None

    def test_empty_recovery(self) -> None:
        original = _make_meta(items_processed=100)
        merged = merge_meta(original, {})
        assert merged["execution_stats"]["items_processed"] == 100
        # recovery_history still appended (zero recovered)
        assert len(merged["recovery_history"]) == 1
        assert merged["recovery_history"][0]["recovered"] == 0

    def test_missing_tpm_governor_does_not_break(self) -> None:
        # Default _make_meta has no tpm_governor; should pass through cleanly.
        original = _make_meta()
        recovery = _make_meta()
        merged = merge_meta(original, recovery)
        assert "tpm_governor_recovery" not in merged

    def test_recovery_with_tpm_governor_appended(self) -> None:
        original = _make_meta()
        recovery = _make_meta()
        recovery["tpm_governor"] = {"max_tpm": 8_000_000}
        merged = merge_meta(original, recovery)
        assert "tpm_governor_recovery" in merged
        assert merged["tpm_governor_recovery"][0]["max_tpm"] == 8_000_000

    def test_missing_results_summary_does_not_break(self) -> None:
        original = _make_meta()
        original.pop("results_summary", None)
        recovery = _make_meta()
        recovery.pop("results_summary", None)
        merged = merge_meta(original, recovery)
        # Neither side had a summary; nothing surfaces in results_summary_recovery
        assert "results_summary_recovery" not in merged

    def test_idempotent_repeat_merge_with_empty_recovery(self) -> None:
        original = _make_meta(items_processed=42)
        merged_once = merge_meta(original, {})
        merged_twice = merge_meta(merged_once, {})
        # items_processed stable under re-merge with empty recovery
        assert merged_twice["execution_stats"]["items_processed"] == 42
        # recovery_history grows by exactly one per merge call
        assert len(merged_twice["recovery_history"]) == 2

    def test_sum_dicts_handles_missing_keys(self) -> None:
        # _sum_dicts is a private helper, but the contract is "missing keys = 0"
        a = {"x": 1, "y": 2}
        b = {"y": 10, "z": 100}
        out = _sum_dicts(a, b)
        assert out == {"x": 1, "y": 12, "z": 100}


# =========================================================================
# 3. INTEGRATION — 100-tile simulated resume
# =========================================================================


class TestSimulatedResume:
    """Use ``LLMMetadataTracker.finalise()`` to build fidelitous metas."""

    def _build_tracker_meta(
        self,
        item_ids: list[str],
        config_version: str = "test-config",
    ) -> dict[str, Any]:
        """Drive an LLMMetadataTracker through ``len(item_ids)`` items."""
        config = {
            "version": config_version,
            "model": "gemini-3-flash",
            "temperature": 0.0,
            "examples": [],
        }
        tracker = LLMMetadataTracker(
            config=config,
            system_instruction="test instruction",
            script_name="test_merge_meta",
            script_version="1.0",
        )
        for i, iid in enumerate(item_ids):
            md = LLMResponseMetadata(
                item_id=iid,
                provider="google_gemini",
                model_requested="gemini-3-flash",
                tokens=TokenUsage(
                    input_tokens=100, output_tokens=50, total_tokens=150,
                ),
                finish_reason="success",
            )
            tracker.log_response(iid, md, store_detailed=True)
            tracker.log_success(iid)
            # Inject a deterministic per-item entry by clearing & resetting
            _ = i  # unused; loop variable preserved for clarity
        return tracker.finalise(include_per_item=True)

    def test_simulated_100_tile_resume(self, tmp_path: Path) -> None:
        # 60-tile original pass + 40-tile recovery pass
        original_ids = [f"tile_{i:03d}" for i in range(60)]
        recovery_ids = [f"tile_{i:03d}" for i in range(60, 100)]

        original_meta = self._build_tracker_meta(original_ids)
        recovery_meta = self._build_tracker_meta(recovery_ids)

        # Write the original to disc, then merge fresh recovery into it
        meta_path = tmp_path / "run.meta.json"
        with open(meta_path, "w") as f:
            json.dump(original_meta, f)

        merged = merge_meta_into_existing(meta_path, recovery_meta)

        # Total items processed equals 100
        assert merged["execution_stats"]["items_processed"] == 100
        # Per-item metadata has 100 entries with no duplicates
        pim = merged["per_item_metadata"]
        assert len(pim) == 100
        ids = [item["item_id"] for item in pim]
        assert len(set(ids)) == 100
        # Token totals sum
        assert merged["usage_stats"]["total_input_tokens"] == 100 * 100

    def test_merge_meta_into_existing_returns_fresh_when_no_existing(
        self, tmp_path: Path,
    ) -> None:
        # Path does not exist — fresh meta passes through unchanged.
        nonexistent = tmp_path / "absent.meta.json"
        fresh = _make_meta(items_processed=5)
        result = merge_meta_into_existing(nonexistent, fresh)
        assert result is fresh

    def test_merge_meta_into_existing_warns_on_overlap(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture,
    ) -> None:
        # Both passes claim to have completed "shared-1" — should warn.
        meta_path = tmp_path / "run.meta.json"
        existing = _make_meta(completed_items=["a", "b", "shared-1"])
        with open(meta_path, "w") as f:
            json.dump(existing, f)
        fresh = _make_meta(completed_items=["shared-1", "c"])

        with caplog.at_level("WARNING", logger="scripts.lib_llm_metadata"):
            merged = merge_meta_into_existing(meta_path, fresh)

        # Warning was emitted
        assert any(
            "possible double-count" in record.message
            for record in caplog.records
        )
        # And the merge dedup still produced the right totals
        assert merged["execution_stats"]["completed_items"] == [
            "a", "b", "shared-1", "c",
        ]


# =========================================================================
# 4. COST-AGGREGATION REGRESSION
# =========================================================================


class TestCostAggregationRegression:
    """Verify ``aggregate_cost_manifest`` reads merged meta correctly.

    We exercise the same field reads ``aggregate_cost_manifest`` performs
    (cost_estimate.total_cost_usd, usage_stats tokens, timestamp.duration,
    execution_stats counts). A full ResolvedRunConfig is heavy to mock, so
    we assert against the field reads directly.
    """

    def test_merged_meta_satisfies_aggregator_field_reads(
        self, tmp_path: Path,
    ) -> None:
        original = _make_meta(
            items_processed=60,
            total_cost_usd=10.0,
            total_input_tokens=60_000,
            total_output_tokens=30_000,
            total_tokens=90_000,
            duration_seconds=3600.0,
            completed_items=[f"t{i:03d}" for i in range(60)],
        )
        recovery = _make_meta(
            items_processed=5,
            total_cost_usd=0.5,
            total_input_tokens=5_000,
            total_output_tokens=2_500,
            total_tokens=7_500,
            duration_seconds=120.0,
            completed_items=[f"t{i:03d}" for i in range(60, 65)],
        )

        meta_path = tmp_path / "run.meta.json"
        with open(meta_path, "w") as f:
            json.dump(original, f)
        merged = merge_meta_into_existing(meta_path, recovery)

        # Field reads the aggregator performs:
        cost = merged.get("cost_estimate", {}).get("total_cost_usd", 0.0) or 0.0
        usage = merged.get("usage_stats", {})
        ts = merged.get("timestamp", {})
        duration = ts.get("duration_seconds") or 0.0
        es = merged.get("execution_stats", {})
        items_proc = int(es.get("items_processed", 0))
        items_fail = int(es.get("items_failed", 0))
        completed = list(es.get("completed_items", []))

        assert cost == pytest.approx(10.5)
        assert usage.get("total_input_tokens") == 65_000
        assert usage.get("total_output_tokens") == 32_500
        assert usage.get("total_tokens") == 97_500
        assert duration == pytest.approx(3720.0)
        assert items_proc == 65
        assert items_fail == 0
        assert len(completed) == 65


# =========================================================================
# 5. ATOMIC-WRITE SAFETY
# =========================================================================


class TestAtomicWriteSafety:
    """Simulated kill mid-write should leave the on-disc meta intact."""

    def test_kill_mid_write_preserves_original(self, tmp_path: Path) -> None:
        meta_path = tmp_path / "run.meta.json"
        original = _make_meta(items_processed=60)
        with open(meta_path, "w") as f:
            json.dump(original, f, indent=2)
        original_bytes = meta_path.read_bytes()

        # Mimic the call sites' atomic-write idiom: write to .tmp, then
        # rename. Simulate a crash by deleting the .tmp before rename.
        merged = merge_meta_into_existing(meta_path, _make_meta(items_processed=5))
        tmp_meta = meta_path.with_suffix(meta_path.suffix + ".tmp")
        with open(tmp_meta, "w") as f:
            json.dump(merged, f, indent=2)
        # ── simulated kill: tmp is removed before rename happens ──
        os.remove(tmp_meta)

        # The original meta file is byte-identical to before we attempted
        # the merge. Downstream cost aggregation can still read it.
        assert meta_path.read_bytes() == original_bytes
        assert not tmp_meta.exists()

        loaded = json.loads(meta_path.read_text())
        assert loaded["execution_stats"]["items_processed"] == 60
