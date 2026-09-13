"""
Tests for ``scripts/audit_proposer_cost.py``.

The script exists because a run's own ``cost_estimate`` cannot be used at a
budget gate, so these tests pin the three things that made that figure wrong:
the Gemini 3.7 rate card, the cache read's exemption from the tier discount,
and the inclusion of thinking tokens at the output rate.

The headline guard is :func:`test_reproduces_committed_gs_figure`, which
reproduces the committed Gold Standard (GS) leg total of US$22.50 from its
recorded token aggregates — the figure in
``reports/gemini37-image-55map-costing-2026-09-10.md`` and
``results/gemini37-image-gs-2026-09-01/findings.md``. It uses the aggregates as
literals rather than reading the run directory, so it stays tier-1 hermetic.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.tier1

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_module():
    """Import the script by path, since ``scripts/`` is not a package."""
    path = BASE_DIR / "scripts" / "audit_proposer_cost.py"
    spec = importlib.util.spec_from_file_location("audit_proposer_cost", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_proposer_cost"] = module
    spec.loader.exec_module(module)
    return module


apc = _load_module()


#: Token aggregates summed over the ten committed fragments of
#: ``outputs/gemini37-image-gs-2026-09-01/g384_ov192_g37img`` (five passes plus
#: their recovery fragments), read 2026-09-13.
GS_USAGE = {
    "total_input_tokens": 139_925_820,
    "total_cached_tokens": 111_214_884,
    "total_output_tokens": 557_418,
    "total_thoughts_tokens": 1_252_014,
}
GS_TILE_PASSES = 6_990


class TestRateCard:
    """The rate card and the tier discount."""

    def test_gemini_37_lists_higher_than_gemini_3(self):
        """3.7 lists at 0.75 / 3.75, not the 0.50 / 3.00 the metas stamp."""
        assert apc.RATE_CARDS["gemini-3.7-flash"]["input"] == 0.75
        assert apc.RATE_CARDS["gemini-3.7-flash"]["output"] == 3.75
        assert apc.RATE_CARDS["gemini-3-flash"]["input"] == 0.50
        assert apc.RATE_CARDS["gemini-3-flash"]["output"] == 3.00

    def test_flex_halves_input_and_output(self):
        """Flex bills at half of list on the input and output axes."""
        rate = apc.rates("gemini-3.7-flash", "flex")
        assert rate["input"] == pytest.approx(0.375 / 1e6)
        assert rate["output"] == pytest.approx(1.875 / 1e6)

    def test_cache_read_is_not_tier_discounted(self):
        """Context caching costs the same at every tier (token-load audit s2).

        Discounting it understates a cache-heavy image leg by about 19 per
        cent, which is how a first implementation of this script returned
        US$18.33 where the committed figure is US$22.50.
        """
        flex = apc.rates("gemini-3.7-flash", "flex")
        standard = apc.rates("gemini-3.7-flash", "standard")
        assert flex["cache"] == standard["cache"]
        assert flex["cache"] == pytest.approx(0.075 / 1e6)

    def test_unknown_model_raises_rather_than_guessing(self):
        """Guessing a rate card is the error this script exists to correct."""
        with pytest.raises(apc.RateCardError):
            apc.rates("gemini-9-flash", "flex")


class TestAuditedCost:
    """The costing rule itself."""

    def test_reproduces_committed_gs_figure(self):
        """The GS leg totals US$22.50, or US$0.00322 per tile-pass."""
        rate = apc.rates("gemini-3.7-flash", "flex")
        total = apc.audited_cost(GS_USAGE, rate)
        assert total == pytest.approx(22.50, abs=0.01)
        assert total / GS_TILE_PASSES == pytest.approx(0.00322, abs=1e-5)

    def test_thinking_tokens_are_billed_at_the_output_rate(self):
        """Omitting thinking is one of the meta's three errors."""
        rate = apc.rates("gemini-3.7-flash", "flex")
        without = dict(GS_USAGE, total_thoughts_tokens=0)
        delta = apc.audited_cost(GS_USAGE, rate) - apc.audited_cost(without, rate)
        assert delta == pytest.approx(
            GS_USAGE["total_thoughts_tokens"] * rate["output"]
        )

    def test_cached_input_is_cheaper_than_fresh_input(self):
        """Cache-blind pricing is the meta's dominant error at 79 % cached."""
        rate = apc.rates("gemini-3.7-flash", "flex")
        all_fresh = dict(GS_USAGE, total_cached_tokens=0)
        assert apc.audited_cost(GS_USAGE, rate) < apc.audited_cost(all_fresh, rate)

    def test_missing_thinking_key_is_tolerated(self):
        """Older metas predate ``total_thoughts_tokens``; treat it as zero."""
        rate = apc.rates("gemini-3-flash", "flex")
        usage = {
            "total_input_tokens": 1_000_000,
            "total_cached_tokens": 0,
            "total_output_tokens": 1_000_000,
        }
        expected = 1_000_000 * rate["input"] + 1_000_000 * rate["output"]
        assert apc.audited_cost(usage, rate) == pytest.approx(expected)
