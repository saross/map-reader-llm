"""The batch verifier path books its usage and keeps its raw results.

Before 2026-09-18 ``_verify_batch`` recorded no token usage (the Batch API
reports usage per response, which the path never read) and discarded the raw
results, so a batch verifier stage could not be cost-audited. These tests pin
the repair: raw results persisted, usage summed in real-time field naming.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib_llm_metadata import AggregatedUsage, ExecutionStats  # noqa: E402
from scripts.run_pv import record_batch_usage  # noqa: E402

pytestmark = pytest.mark.tier1


class _Tracker:
    """The two attributes ``record_batch_usage`` touches."""

    def __init__(self) -> None:
        self.usage = AggregatedUsage()
        self.stats = ExecutionStats()
        self.results_summary: dict = {}


def _result(key: str, prompt: int, cached: int, out: int, thoughts: int) -> dict:
    return {"key": key, "response": {
        "usageMetadata": {"promptTokenCount": prompt,
                          "cachedContentTokenCount": cached,
                          "candidatesTokenCount": out,
                          "thoughtsTokenCount": thoughts,
                          "totalTokenCount": prompt + out + thoughts},
        "candidates": [{"content": {"parts": [{"text": "{}"}]}}]}}


def test_usage_is_summed_into_the_tracker_in_realtime_naming(tmp_path):
    tracker = _Tracker()
    results = [_result("candidate_00000", 1000, 900, 10, 50),
               _result("candidate_00001", 1000, 900, 12, 60)]
    usage = record_batch_usage(tracker, results, tmp_path)
    assert tracker.usage.total_input_tokens == 2000
    assert tracker.usage.total_cached_tokens == 1800
    assert tracker.usage.total_output_tokens == 22
    assert tracker.usage.total_thoughts_tokens == 110
    assert tracker.usage.total_tokens == 2132
    assert usage["n_responses_with_usage"] == 2
    assert tracker.results_summary["batch_usage"]["n_results"] == 2
    assert round(tracker.results_summary["batch_usage"]["cached_share"], 4) == 0.9


def test_raw_results_are_persisted_verbatim(tmp_path):
    tracker = _Tracker()
    results = [_result("candidate_00000", 5, 0, 1, 0)]
    record_batch_usage(tracker, results, tmp_path)
    raw = tmp_path / "batch_results.jsonl"
    assert raw.exists()
    assert [json.loads(line) for line in raw.read_text().splitlines()] == results
    assert tracker.results_summary["batch_usage"]["raw_results"] == "batch_results.jsonl"


def test_responses_without_usage_are_counted_not_hidden(tmp_path):
    """A partial report must be distinguishable from a complete one."""
    tracker = _Tracker()
    results = [_result("candidate_00000", 100, 0, 1, 0),
               {"key": "candidate_00001", "response": {"candidates": []}}]
    usage = record_batch_usage(tracker, results, tmp_path)
    assert usage["n_responses_with_usage"] == 1
    assert tracker.results_summary["batch_usage"]["n_results"] == 2
    assert tracker.usage.total_input_tokens == 100


def test_no_usage_at_all_is_absent_not_zero(tmp_path):
    tracker = _Tracker()
    usage = record_batch_usage(
        tracker, [{"key": "candidate_00000", "response": {}}], tmp_path)
    assert usage["cached_share"] is None
    assert usage["usage_source"].startswith("ABSENT")


def test_matched_count_is_booked_as_items_processed(tmp_path):
    """The auditor reads execution_stats.items_processed as the stage's
    item count; the batch path booked none, so its per-candidate rate read
    n/a on the first audited batch verifier leg (2026-09-18)."""
    tracker = _Tracker()
    results = [_result("candidate_00000", 5, 0, 1, 0),
               _result("candidate_00001", 5, 0, 1, 0)]
    record_batch_usage(tracker, results, tmp_path, n_processed=2)
    assert tracker.stats.items_processed == 2
    tracker2 = _Tracker()
    record_batch_usage(tracker2, results, tmp_path)
    assert tracker2.stats.items_processed == 0
