"""Tier-2 tests: the tile-presence cost stage run for real (D29, D30).

``collect_costs`` is the wiring from the passes register through
``price_stage`` to each leg's record, its cross-check against the published
figure, and the refusal a disagreement causes. Until 2026-10-04 every test
stubbed it away (audit lens B). These run it against the committed register
and pin it to the committed ``verifier-costs.json``. Tier 2 because they read
the 3 MB register and take seconds (``tests/README.md``).
"""

from __future__ import annotations

import pytest

from scripts import build_tile_presence_board as tp

pytestmark = pytest.mark.tier2

COMMITTED_COSTS = tp.OUT / tp.COSTS


@pytest.fixture(scope="module")
def priced():
    """``collect_costs`` run for real once (a few seconds, zero API)."""
    return tp.collect_costs()


def test_the_committed_costs_regenerate_exactly(priced) -> None:
    costs, n_legs, disagreements = priced
    assert disagreements == []
    text = tp.costs_payload(costs)[tp.OUT / tp.COSTS]
    assert text == COMMITTED_COSTS.read_text(encoding="utf-8")
    assert n_legs == 22 and len(costs) == 35
    assert {r["basis"] for r in costs.values()} == {"measured", "completed"}, (
        "a verifier leg is UNPRICED: run --stage costs, read the UNPRICED block, and "
        "recover it by hand WITH THE PI before quoting its costs (ruling 2026-10-04)")
    assert tp.unpriced_legs(costs) == []


def test_a_two_stage_leg_sums_both_stages(priced) -> None:
    from scripts.lib_frontier_cost import FrontierCoster
    costs, _, _ = priced
    coster = FrontierCoster()
    main_stage, vote3 = tp.LEGS["TH7"]
    main = coster.leg_cost("55maps-text-high-generalisation", "verified")
    increment = coster.stage_leg_cost(vote3, complete=True)
    record = costs["TH7"]
    assert record["usd"] == pytest.approx(main.usd + increment.usd, abs=1e-9)
    assert record["candidates"] == (coster.leg("55maps-text-high-generalisation",
                                               "verified").verifications
                                    + coster.stage_leg(vote3, complete=True).verifications)
    assert record["stages_outside_register"] == [vote3]
    assert costs["TM"]["basis"] == "completed"  # its main leg is a floor
    assert costs["T03"]["basis"] == "measured"


def _with_published(monkeypatch, config: str, **change) -> None:
    table = {k: dict(v) for k, v in tp.PUBLISHED_LEG_COST.items()}
    table[config].update(change)
    monkeypatch.setattr(tp, "PUBLISHED_LEG_COST", table)


def test_a_measured_leg_must_agree_to_the_cent(monkeypatch, priced) -> None:
    # SENTINEL: a measured leg two cents off its report is a disagreement
    # (one tolerance for every leg would have let five cents through).
    usd = priced[0]["G3IMG-ARM1-K1"]["usd"]
    _with_published(monkeypatch, "G3IMG-ARM1-K1", usd=usd + 0.02)
    _, _, disagreements = tp.collect_costs()
    assert [d.split(":")[0] for d in disagreements] == ["G3IMG-ARM1-K1"]


def test_a_completed_leg_has_the_d30_tolerance(monkeypatch, priced) -> None:
    usd = priced[0]["IMG-ARM2-K1"]["usd"]
    assert priced[0]["IMG-ARM2-K1"]["basis"] == "completed"
    _with_published(monkeypatch, "IMG-ARM2-K1", usd=usd - 0.049)
    assert tp.collect_costs()[2] == []                      # within US$0.05
    _with_published(monkeypatch, "IMG-ARM2-K1", usd=usd - 0.051)
    assert [d.split(":")[0] for d in tp.collect_costs()[2]] == ["IMG-ARM2-K1"]


def test_a_published_leg_over_other_candidates_is_a_disagreement(monkeypatch) -> None:
    _with_published(monkeypatch, "IMG-ARM1-K5", candidates=9172)
    assert [d.split(":")[0] for d in tp.collect_costs()[2]] == ["IMG-ARM1-K5"]


def test_a_disagreement_refuses_the_write_and_fails_the_check(
        tmp_path, monkeypatch, priced) -> None:
    monkeypatch.setattr(tp, "OUT", tmp_path)
    _with_published(monkeypatch, "G3IMG-ARM1-K1", usd=priced[0]["G3IMG-ARM1-K1"]["usd"] + 1)
    assert tp.main(["--stage", "costs"]) == 1
    assert not (tmp_path / tp.COSTS).exists()
    # The check path: a file byte-identical to what this very run produces, so
    # nothing but the disagreement can fail it.
    costs, _, disagreements = tp.collect_costs()
    assert disagreements
    (tmp_path / tp.COSTS).write_text(tp.costs_payload(costs)[tmp_path / tp.COSTS],
                                     encoding="utf-8")
    assert tp.main(["--stage", "costs", "--check"]) == 1


def test_an_unpriced_published_leg_is_a_disagreement(monkeypatch) -> None:
    """A leg its report prices that this stage cannot is a lost cost: it keeps
    its cross-check and refuses the write (re-audit, 2026-10-04)."""
    lost = tp.LEGS["IMG-ARM1-K5"][0]
    real = tp.price_stage

    def failing(coster, stage, key, index, board_families):
        if stage == lost:
            raise tp.FrontierCostError("simulated: no rule prices this stage")
        return real(coster, stage, key, index, board_families)
    monkeypatch.setattr(tp, "price_stage", failing)
    costs, _, disagreements = tp.collect_costs()
    record = costs["IMG-ARM1-K5"]
    assert record["basis"] == "unpriced" and record["usd"] is None
    assert record["cross_check"]["published_usd"] == tp.PUBLISHED_LEG_COST["IMG-ARM1-K5"]["usd"]
    assert record["cross_check"]["within_tolerance"] is False
    assert [d.split(":")[0] for d in disagreements] == ["IMG-ARM1-K5"]
