"""Tier-1 drift guards: every committed frontier output carries today's costs.

WP4b (2026-10-04) derives the cost axis of three signed frontiers from the
passes register through ``scripts/lib_frontier_cost.py`` and
``data/pricing/frontier-configurations.json``. A change to the mapping, the
register or the library that is not followed by regenerating the outputs
would leave a published frontier on stale costs; these tests turn red when
that happens. They recompute each committed figure independently of the
builder that wrote it:

- the GS Pareto v2 (``results/verifier-robustness/pareto/pareto_v2.json``);
- the K-ladder Phase 1 (``results/k-ladder-2026-09-12/ladders.json``);
- the K-ladder Phase 2 (``results/k-ladder-2026-09-12/phase2/ladders.json``).

The r2 final board has its own guards in ``tests/test_final_board_cost_refresh.py``.
A legitimate register or mapping change is expected to turn these red until
the outputs are regenerated on sapphire.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.lib_frontier_cost import (
    TILES_55MAP,
    TILES_GS,
    default_coster,
    gs_units,
    phase2_pass_units,
)

REPO = Path(__file__).resolve().parents[1]
PARETO = REPO / "results/verifier-robustness/pareto/pareto_v2.json"
PHASE1 = REPO / "results/k-ladder-2026-09-12/ladders.json"
PHASE2 = REPO / "results/k-ladder-2026-09-12/phase2/ladders.json"


@pytest.mark.tier1
def test_the_gs_units_reproduce_the_june_audit():
    # Each unit independently anchored (a swapped unit name, a mean of units
    # for the pooled verifier, or a mistyped tile count moves one of these).
    units = gs_units()
    assert units["min_pass"].usd == pytest.approx(0.266, rel=0.003)
    assert units["high_pass"].usd == pytest.approx(2.29, rel=0.003)
    assert units["g37_pass"].usd == pytest.approx(1.714, rel=0.005)
    assert units["vf_call"].usd == pytest.approx(0.000693, rel=0.005)
    assert (TILES_GS, TILES_55MAP) == (487, 8541)


@pytest.mark.tier1
def test_pareto_v2_carries_todays_units_and_rung_costs():
    from scripts import build_pareto_v2 as pv2
    doc = json.loads(PARETO.read_text(encoding="utf-8"))
    units = gs_units()
    model = doc["cost_model"]
    assert model["min_pass_usd"] == pytest.approx(units["min_pass"].usd, abs=1e-12)
    assert model["high_pass_usd"] == pytest.approx(units["high_pass"].usd, abs=1e-12)
    assert model["vf_call_usd"] == pytest.approx(units["vf_call"].usd, abs=1e-15)
    rungs = {r["rung"]: r for r in doc["rungs"]}
    assert set(rungs) == {spec[0] for spec in pv2.RUNGS}
    for name, _f1, _gj, np_, ppc, crops, nvf, _ref in pv2.RUNGS:
        unit = units["min_pass"].usd if ppc == pv2.MIN_PASS_USD else units["high_pass"].usd
        cost = np_ * unit + crops * nvf * units["vf_call"].usd
        assert rungs[name]["est_cost_usd"] == pytest.approx(round(cost, 2), abs=1e-9), name
        assert rungs[name]["est_cost_55map_usd"] == pytest.approx(
            round(cost * TILES_55MAP / TILES_GS, 2), abs=1e-9), name


@pytest.mark.tier1
def test_phase2_ladders_carry_each_familys_own_unit():
    from scripts import build_k_ladder_phase2_tables as tables
    doc = json.loads(PHASE2.read_text(encoding="utf-8"))
    units, named = phase2_pass_units(), gs_units()
    vf = named["vf_call"].usd
    for field, name in (("vf_call_usd", "vf_call"), ("min_pass_usd", "min_pass"),
                        ("high_pass_usd", "high_pass"), ("g37_pass_usd", "g37_pass")):
        assert doc["cost_model"][field] == pytest.approx(named[name].usd, abs=1e-12), field
    assert "passes register" in doc["cost_model"]["basis"]
    assert len(doc["ladders"]) == len(units) == 14
    for ladder in doc["ladders"]:
        unit, anchor = units[ladder["proposer_pool"]]
        assert ladder["pass_usd"] == pytest.approx(unit.usd, abs=1e-6), ladder["family"]
        assert ladder["pass_usd_anchor"] == tables.PASS_ANCHORS[anchor], ladder["family"]
        for rung in ladder["rungs"]:
            assert rung["proposer_flex_usd"] == pytest.approx(
                round(rung["K"] * unit.usd, 4), abs=1e-4), (ladder["family"], rung["K"])
            if rung["source"].startswith("committed") and rung["candidates"]:
                assert rung["verifier_flex_usd"] == pytest.approx(
                    round(rung["candidates"] * vf, 4), abs=1e-9), (ladder["family"], rung["K"])
                assert rung["verifier_usd_basis"] == \
                    f"priced at VF_CALL_USD {vf:.7f} (register, D19)"


@pytest.mark.tier1
def test_phase1_ladders_carry_todays_costs_and_the_fourth_cells_own():
    # Rebuild in memory (zero API, seconds) and compare every rung's cost.
    from scripts import build_k_ladder_tables as phase1
    committed = json.loads(PHASE1.read_text(encoding="utf-8"))
    rebuilt = phase1.build()
    assert len(rebuilt["ladders"]) == len(committed["ladders"])
    fourth = []
    for new, old in zip(rebuilt["ladders"], committed["ladders"], strict=True):
        assert new["family"] == old["family"]
        for rn, ro in zip(new["rungs"], old["rungs"], strict=True):
            assert rn["condition_id"] == ro["condition_id"]
            for key in ("usd", "register_rows", "basis"):
                assert (rn["cost"] or {}).get(key) == (ro["cost"] or {}).get(key), \
                    (rn["condition_id"], key)
            assert rn.get("projection_55map_usd") == ro.get("projection_55map_usd")
        if new["verifier"]["model"].startswith("gemini-3.7") and \
                new["proposer_pool"] == "g384_ov192_55map":
            fourth.append(new)
    # The fourth cell's ladder is priced as FOURTH, not as stride B (the
    # defect a pool-only key caused): its K = 10 rungs cost FOURTH-N10.
    assert fourth, "no fourth-cell ladder found"
    spec = json.loads((REPO / "data/pricing/frontier-configurations.json").read_text())
    expected = round(default_coster().configuration_cost(
        spec["board_families"]["FOURTH-N10"]).usd, 4)
    for ladder in fourth:
        tens = [r for r in ladder["rungs"] if r["K"] == 10]
        assert tens and all(r["cost"]["usd"] == expected for r in tens)



@pytest.mark.tier1
def test_the_phase2_builder_prices_each_family_at_its_mapped_unit():
    # The builder's own family table, not only its committed output: a
    # builder that fell back to the borrowed unit would regenerate wrong.
    from scripts import build_k_ladder_phase2_tables as tables
    units = phase2_pass_units()
    for family, meta in tables.FAMILIES.items():
        unit, anchor = units[family]
        assert meta["pass_usd"] == unit.usd, family
        assert meta["pass_anchor"] == anchor, family
