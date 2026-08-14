"""
Tests for ``scripts/analyse_obs280_shared_reference.py`` (Session 132,
queue item 4).

Tier 1: the rank helper (the only non-trivial pure logic — a reversed
sort would silently invert every rank claim in the artefact).
Tier 2: the real committed artefacts still produce the registered
finding shape (divergence survives; four carried cells ranked on both
metrics) — committed-state insurance in the marking-campaign-gates
style.
"""

import json

import pytest

import scripts.analyse_obs280_shared_reference as mod


@pytest.mark.tier1
def test_rank_orders_best_first():
    """rank() must sort best-first; a reversed sort inverts every claim."""
    values = {"a": 0.1, "b": 0.9, "c": 0.5}
    assert mod.rank(values) == ["b", "c", "a"]


@pytest.mark.tier2
def test_real_artefacts_reproduce_registered_finding(tmp_path, monkeypatch):
    """Running against the committed board reproduces the item-4 result:
    the F1 and MCC leaders differ on the shared reference."""
    out_dir = tmp_path / "std"
    out_dir.mkdir()
    # Redirect only the OUTPUT json; inputs stay the committed artefacts.
    real_base = mod.STD_BASE
    monkeypatch.setattr(
        mod, "STD_BASE", real_base,  # explicit: inputs are the real base
    )
    payload_path = real_base / "obs280-shared-reference.json"
    before = payload_path.read_text() if payload_path.exists() else None
    mod.main()
    payload = json.loads(payload_path.read_text())
    assert payload["comparison"]["divergence_survives"] is True
    assert payload["comparison"]["f1_leader_standardised"] == "T03-k4"
    assert payload["comparison"]["mcc_leader_standardised"] == "IM-k3"
    assert len(payload["comparison"]["f1_rank_standardised"]) == 4
    # Deterministic: rerun reproduces the committed artefact byte-for-byte.
    if before is not None:
        assert payload_path.read_text() == before
