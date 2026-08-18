"""Tier-1 tests for cost-basis recording and failure attribution.

Both behaviours were defects found in Session 136 while auditing run
metadata, and both had the same shape: a number that looked authoritative,
was wrong, and had nothing in the record to say so.

* Real-time runs priced at list rates while actually billing at the flex
  discount, so every recorded cost overstated the bill by 2x and disagreed
  with the audited ``pareto_v2.json`` model by exactly that factor.
* A tile lost to a JSON-parse failure was recorded with
  ``parse_failures: 0`` and ``finish_reason_counts`` reporting unbroken
  success, because the parse counter was driven by the API envelope rather
  than by the failure that actually occurred.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib_llm_metadata import (  # noqa: E402
    BATCH_API_DISCOUNT,
    FLEX_DISCOUNT,
    AggregatedUsage,
    LLMMetadataTracker,
    estimate_cost,
)


def _tracker() -> LLMMetadataTracker:
    """Build a tracker with the minimum viable config.

    Returns:
        An LLMMetadataTracker suitable for exercising failure accounting.
    """
    return LLMMetadataTracker(
        config={"version": "test", "model": "gemini-3-flash-preview"},
        system_instruction="test instruction",
        script_name="test",
        script_version="1.0",
    )


def _usage(input_tokens: int = 1_000_000, output_tokens: int = 1_000_000) -> AggregatedUsage:
    """Build an AggregatedUsage with round token counts.

    Args:
        input_tokens: Total input tokens. output_tokens: Total output tokens.

    Returns:
        A populated AggregatedUsage.
    """
    usage = AggregatedUsage()
    usage.total_input_tokens = input_tokens
    usage.total_output_tokens = output_tokens
    usage.total_tokens = input_tokens + output_tokens
    return usage


@pytest.mark.tier1
def test_list_price_is_recorded_when_no_discount_applies():
    """With no discount, billed equals list and the basis says so."""
    cost = estimate_cost(_usage(), "google_gemini", "gemini-3-flash-preview")
    assert cost["total_cost_usd"] == pytest.approx(3.50)  # 0.50 in + 3.00 out
    assert cost["list_total_cost_usd"] == pytest.approx(3.50)
    assert cost["cost_basis"] == "list"
    assert cost["pricing_used"]["discount"] == 1.0


@pytest.mark.tier1
def test_flex_discount_halves_the_billed_cost_and_keeps_list_price():
    """total_cost_usd must be the BILL; list price is retained beside it."""
    cost = estimate_cost(_usage(), "google_gemini", "gemini-3-flash-preview",
                         discount=FLEX_DISCOUNT, discount_reason="flex")
    assert cost["total_cost_usd"] == pytest.approx(1.75)
    assert cost["list_total_cost_usd"] == pytest.approx(3.50)
    assert cost["cost_basis"] == "billed"
    assert cost["pricing_used"]["discount"] == 0.5
    assert cost["pricing_used"]["discount_reason"] == "flex"


@pytest.mark.tier1
def test_flex_and_batch_discounts_agree():
    """The two commercial terms are equal in size; the constants must match.

    They are separate constants because they are separate terms and may
    diverge — but while they are equal, a run priced either way must cost the
    same, or a batch-versus-flex comparison would be measuring the bookkeeping.
    """
    flex = estimate_cost(_usage(), "google_gemini", "gemini-3-flash-preview",
                         discount=FLEX_DISCOUNT)
    batch = estimate_cost(_usage(), "google_gemini", "gemini-3-flash-preview",
                          discount=BATCH_API_DISCOUNT)
    assert flex["total_cost_usd"] == batch["total_cost_usd"]


@pytest.mark.tier1
def test_parse_failure_increments_the_parse_counter():
    """A JSON-parse failure must show up in parse_failures.

    This is the grid-run defect: the API envelope parsed fine, so the
    envelope-driven counter stayed at zero while a tile was genuinely lost.
    """
    tracker = _tracker()
    tracker.log_failure("tile_a.png", "JSON Parse Error: boom", category="parse")

    assert tracker.stats.parse_failures == 1
    assert tracker.stats.items_failed == 1
    assert tracker.stats.failed_items[0]["category"] == "parse"


@pytest.mark.tier1
def test_non_parse_failures_do_not_inflate_the_parse_counter():
    """The negative. Without this, 'increment always' would pass.

    An API-exhaustion failure and an unclassified failure are both real
    failures, and neither is a parse failure.
    """
    tracker = _tracker()
    tracker.log_failure("tile_b.png", "Retries exhausted", category="api")
    tracker.log_failure("tile_c.png", "something else")

    assert tracker.stats.items_failed == 2
    assert tracker.stats.parse_failures == 0
    assert tracker.stats.failed_items[1]["category"] is None
