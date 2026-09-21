"""
Tier-1 tests: ``scripts/run_generalisation.py`` prices through the rate card
at the run's own tier and the pass's own date, and its entry point never
writes a manifest on the legacy ``recorded`` basis.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import run_generalisation as rg
from scripts.lib_cost import RateCardError

pytestmark = pytest.mark.tier1


def test_the_manifest_tier_is_the_runs_own_and_never_recorded() -> None:
    assert rg.manifest_pricing_tier(SimpleNamespace(global_opts={"service_tier": "batch"})) == "batch"
    assert rg.manifest_pricing_tier(SimpleNamespace(global_opts={})) == "flex"
    with pytest.raises(RateCardError):
        rg.manifest_pricing_tier(SimpleNamespace(global_opts={"service_tier": "recorded"}))
    src = (Path(__file__).resolve().parent.parent / "scripts" / "run_generalisation.py").read_text()
    body = src[src.index("def cmd_all("):]
    assert "aggregate_cost_manifest(rcfg, pricing_tier=manifest_pricing_tier(rcfg))" in body
    assert not re.search(r"aggregate_cost_manifest\(rcfg\)\n", body)


def test_the_top_level_service_tier_key_reaches_the_run_config() -> None:
    """Committed run configs carry service_tier at the top level, not per stage."""
    assert rg.run_service_tier({"service_tier": "batch", "proposer": {}}) == "batch"
    assert rg.run_service_tier({"proposer": {"service_tier": "standard"},
                                "service_tier": "batch"}) == "standard"
    assert rg.run_service_tier({}) == "flex"
    src = (Path(__file__).resolve().parent.parent / "scripts" / "run_generalisation.py").read_text()
    assert '"service_tier": run_service_tier(config),' in src


def test_price_tokens_uses_the_pass_date() -> None:
    tokens = {"input_tokens": 1_000_000, "cached_tokens": 0, "output_tokens": 0,
              "thinking_tokens": 0}
    before = rg._price_tokens(tokens, "gemini-3.7-flash", "flex", at="2026-09-13")
    after = rg._price_tokens(tokens, "gemini-3.7-flash", "flex", at="2027-02-01")
    assert before["total_cost_usd"] == pytest.approx(0.375)
    assert after["total_cost_usd"] == pytest.approx(0.75)
    src = (Path(__file__).resolve().parent.parent / "scripts" / "run_generalisation.py").read_text()
    assert src.count('at=(meta.get("timestamp") or {}).get("end")') == 1
    assert src.count('at=(verifier_meta.get("timestamp") or {}).get("end")') == 1


def test_the_manifest_records_the_card() -> None:
    ident = rg._rate_card_identity()
    assert ident["path"] == "data/pricing/gemini-rate-card.json" and len(ident["sha256"]) == 64
