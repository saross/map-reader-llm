"""
Tier-1 tests for ``scripts/lib_cost.py``, the project's one cost function.

Each test is a red sentinel for a defect class the cost accounting plan
(``planning/cost-accounting-fix-plan-2026-09-21.md``) found in the code it
replaces: cached input priced at the fresh rate, the cache read priced at
the wrong tier for 3.7, the tier chosen at the call site, a silent default
for an unknown model, thinking omitted, dollars summed on merge, and a
confident zero where nothing was recorded.
"""

from __future__ import annotations

import json
from datetime import date

import pytest

from scripts import lib_cost as lc

pytestmark = pytest.mark.tier1

FLEX37 = {"model": "gemini-3.7-flash", "tier": "flex", "at": "2026-09-20"}


def usage(**kw) -> dict:
    base = {"total_input_tokens": 0, "total_cached_tokens": 0,
            "total_output_tokens": 0, "total_thoughts_tokens": 0}
    base.update(kw)
    return base


# --- The card itself --------------------------------------------------------

def test_the_card_of_record_is_complete_and_dated() -> None:
    card = lc.load_rate_card()
    assert card["tiers"] == list(lc.TIERS)
    for name, entry in card["models"].items():
        rows = entry["rows"]
        assert rows, name
        starts = [date.fromisoformat(r["valid_from"]) for r in rows]
        assert starts == sorted(starts), f"{name}: rows out of order"
        for prev, nxt in zip(rows, rows[1:]):
            assert prev["valid_to"] is not None, f"{name}: an open row is not the last"
            assert date.fromisoformat(prev["valid_to"]) < date.fromisoformat(nxt["valid_from"])
        for row in rows:
            for tier in lc.TIERS:
                for cls in ("input_fresh", "input_cached", "output"):
                    assert row["rates"][tier][cls] > 0, (name, tier, cls)
            assert row["source"]["url"].startswith("https://")
            assert row["source"]["retrieved"]
    aliases = [a for e in card["models"].values() for a in e.get("aliases", [])]
    assert len(aliases) == len(set(aliases))
    assert not set(aliases) & set(card["models"])


def test_the_current_37_row_is_invoice_confirmed_and_the_2027_row_is_not() -> None:
    now = lc.rate_row("gemini-3.7-flash", "2026-09-21")
    later = lc.rate_row("gemini-3.7-flash", "2027-01-02")
    assert now["invoice_confirmations"] and not later["invoice_confirmations"]
    assert later["rates"]["flex"]["input_fresh"] == 2 * now["rates"]["flex"]["input_fresh"]


# --- Model resolution -------------------------------------------------------

def test_an_alias_resolves_and_a_prefix_does_not() -> None:
    assert lc.resolve_model("gemini-3-flash") == "gemini-3-flash-preview"
    assert lc.resolve_model("GEMINI-3.1-PRO") == "gemini-3.1-pro-preview"
    with pytest.raises(lc.UnknownModelError):
        lc.resolve_model("gemini-3")            # a prefix once selected a default
    with pytest.raises(lc.UnknownModelError):
        lc.resolve_model("gemini-3.7-flash-preview")  # not an alias on the card
    with pytest.raises(lc.UnknownModelError):
        lc.resolve_model("")


def test_an_unknown_tier_and_a_date_before_any_row_are_refused() -> None:
    with pytest.raises(lc.RateCardError, match="tier"):
        lc.rates_for("gemini-3.7-flash", "priority", "2026-09-20")
    with pytest.raises(lc.RateCardError, match="no rate card row"):
        lc.rates_for("gemini-3.7-flash", "flex", "2026-01-01")


# --- The three classes ------------------------------------------------------

def test_cached_input_is_priced_at_the_cache_rate_not_the_input_rate() -> None:
    """The register's 2.5x: prompt_token_count includes cached tokens."""
    u = usage(total_input_tokens=1_000_000, total_cached_tokens=800_000)
    block = lc.price_usage(u, **FLEX37)
    assert block["tokens_billed"] == {"input_fresh": 200_000, "input_cached": 800_000,
                                      "output": 0, "thinking": 0}
    assert block["input_cost_usd"] == pytest.approx(0.2 * 0.375)
    assert block["cached_input_cost_usd"] == pytest.approx(0.8 * 0.0375)
    assert block["total_cost_usd"] == pytest.approx(0.2 * 0.375 + 0.8 * 0.0375)
    assert block["total_cost_usd"] < 0.375  # a whole-at-input-rate price would be 0.375


def test_the_cache_read_tier_depends_on_the_model() -> None:
    """3.7 halves the cache read on flex; Gemini 3 Flash Preview does not."""
    u = usage(total_input_tokens=1_000_000, total_cached_tokens=1_000_000)
    g37 = lc.price_usage(u, "gemini-3.7-flash", "flex", at="2026-09-01")
    g3 = lc.price_usage(u, "gemini-3-flash-preview", "flex", at="2026-09-01")
    assert g37["cached_input_cost_usd"] == pytest.approx(0.0375)
    assert g3["cached_input_cost_usd"] == pytest.approx(0.05)
    assert lc.price_usage(u, "gemini-3-flash-preview", "standard", at="2026-09-01")[
        "cached_input_cost_usd"] == pytest.approx(0.05)


def test_thinking_is_billed_at_the_output_rate() -> None:
    plain = lc.price_usage(usage(total_output_tokens=1_000_000), **FLEX37)
    thinking = lc.price_usage(usage(total_output_tokens=1_000_000,
                                    total_thoughts_tokens=1_000_000), **FLEX37)
    assert plain["output_cost_usd"] == pytest.approx(1.875)
    assert thinking["output_cost_usd"] == pytest.approx(3.75)
    assert thinking["pricing_used"]["thinking_tokens_billed_as_output"] == 1_000_000


def test_the_tier_is_the_callers_and_batch_equals_flex_on_this_card() -> None:
    u = usage(total_input_tokens=1_000_000, total_output_tokens=100_000)
    std = lc.price_usage(u, "gemini-3.7-flash", "standard", at="2026-09-20")
    flex = lc.price_usage(u, "gemini-3.7-flash", "flex", at="2026-09-20")
    batch = lc.price_usage(u, "gemini-3.7-flash", "batch", at="2026-09-20")
    assert flex["total_cost_usd"] == pytest.approx(std["total_cost_usd"] / 2)
    assert batch["total_cost_usd"] == pytest.approx(flex["total_cost_usd"])
    assert std["pricing_used"]["discount"] == 1.0 and flex["pricing_used"]["discount"] == 0.5
    assert flex["list_total_cost_usd"] == pytest.approx(std["total_cost_usd"])
    assert flex["pricing_used"]["tier"] == "flex"


def test_the_block_adds_up_and_names_its_card() -> None:
    u = usage(total_input_tokens=491_642_080, total_cached_tokens=397_093_752,
              total_output_tokens=1_469_579, total_thoughts_tokens=7_428_304)
    b = lc.price_usage(u, "gemini-3.7-flash", "flex", at="2026-09-13", tier_source="cli")
    assert b["schema"] == "cost/2" and b["cost_basis"] == "audited"
    assert b["input_cost_usd"] + b["cached_input_cost_usd"] + b["output_cost_usd"] == \
        pytest.approx(b["total_cost_usd"], abs=2e-6)
    rc = b["pricing_used"]["rate_card"]
    assert len(rc["sha256"]) == 64 and rc["version"] and rc["row_valid_from"] == "2026-08-01"
    assert rc["path"] == "data/pricing/gemini-rate-card.json"
    assert b["pricing_used"]["tier_source"] == "cli"


# --- Reproduction of a committed figure ------------------------------------

def test_reproduces_the_arm2_replicate_leg_to_the_cent() -> None:
    """verify_k5_arm2_replicate-batch-2026-09-20: audited US$10.2033 (no cache)."""
    u = usage(total_input_tokens=16_438_016, total_cached_tokens=0,
              total_output_tokens=1_146_082, total_thoughts_tokens=1_008_083)
    b = lc.price_usage(u, "gemini-3.7-flash", "batch", at="2026-09-20")
    assert b["total_cost_usd"] == pytest.approx(10.2033, abs=5e-5)


def test_the_2027_step_prices_at_the_new_row() -> None:
    u = usage(total_input_tokens=1_000_000)
    assert lc.price_usage(u, "gemini-3.7-flash", "flex", at="2026-12-31")[
        "input_cost_usd"] == pytest.approx(0.375)
    assert lc.price_usage(u, "gemini-3.7-flash", "flex", at="2027-01-02")[
        "input_cost_usd"] == pytest.approx(0.75)


# --- Null, not zero ----------------------------------------------------------

def test_nothing_recorded_prices_to_null_and_a_real_zero_to_zero() -> None:
    empty = lc.price_usage(usage(), **FLEX37)
    assert empty["cost_basis"] == "unrecorded"
    assert empty["total_cost_usd"] is None and empty["input_cost_usd"] is None
    real_zero = lc.price_usage(usage(), n_responses_with_usage=3, **FLEX37)
    assert real_zero["cost_basis"] == "audited" and real_zero["total_cost_usd"] == 0.0
    inline = lc.price_usage({**usage(), "n_responses_with_usage": 2}, **FLEX37)
    assert inline["cost_basis"] == "audited"


def test_cached_tokens_never_exceed_the_input_total() -> None:
    classes = lc.token_classes(usage(total_input_tokens=10, total_cached_tokens=50))
    assert classes == {"input_fresh": 0, "input_cached": 10, "output": 0, "thinking": 0}


# --- Merges re-price ---------------------------------------------------------

def test_a_merge_reprices_summed_tokens_at_the_blocks_own_terms() -> None:
    a = usage(total_input_tokens=1_000_000, total_cached_tokens=500_000)
    b = usage(total_input_tokens=3_000_000, total_cached_tokens=2_500_000,
              total_thoughts_tokens=10_000)
    block_a = lc.price_usage(a, **FLEX37)
    merged_usage = {k: a[k] + b[k] for k in a}
    merged = lc.reprice_block(block_a, merged_usage)
    direct = lc.price_usage(merged_usage, **FLEX37)
    assert merged["total_cost_usd"] == pytest.approx(direct["total_cost_usd"])
    assert merged["pricing_used"]["tier"] == "flex"
    assert merged["pricing_used"]["priced_at"] == "2026-09-20"
    # The additive shortcut is wrong whenever cached shares differ per part.
    additive = block_a["total_cost_usd"] + lc.price_usage(b, **FLEX37)["total_cost_usd"]
    assert additive == pytest.approx(direct["total_cost_usd"])  # here it happens to agree…
    # …but a legacy block with no tier cannot be re-priced without a fallback.
    with pytest.raises(lc.RateCardError):
        lc.reprice_block({"total_cost_usd": 1.0, "pricing_used": {"model": "gemini-3.7-flash"}},
                         merged_usage)
    ok = lc.reprice_block({"total_cost_usd": 1.0, "pricing_used": {"model": "gemini-3.7-flash"}},
                          merged_usage, fallback_tier="flex")
    assert ok["cost_basis"] == "audited"


def test_an_alternative_card_is_honoured_and_stamped(tmp_path) -> None:
    card = json.loads(lc.DEFAULT_RATE_CARD.read_text())
    card["version"] = "test"
    card["models"]["gemini-3.7-flash"]["rows"][0]["rates"]["flex"]["input_fresh"] = 9.0
    p = tmp_path / "card.json"
    p.write_text(json.dumps(card))
    b = lc.price_usage(usage(total_input_tokens=1_000_000), "gemini-3.7-flash", "flex",
                       at="2026-09-20", card_path=p)
    assert b["input_cost_usd"] == pytest.approx(9.0)
    assert b["pricing_used"]["rate_card"]["version"] == "test"
