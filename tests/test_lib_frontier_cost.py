"""Tier-1 tests for ``scripts/lib_frontier_cost.py`` and the frontier mapping.

The frontier cost axis prices each configuration's own register tokens at
one uniform discounted tier (PI ruling D19, amended 2026-10-04). These tests
pin each rule with a sentinel for the defect it prevents, then check the
committed mapping (``data/pricing/frontier-configurations.json``) against
the register and the committed ladders:

- a pass is re-priced at the uniform tier whatever it was billed at (IM's
  explicit-cache passes billed standard; the frontier must not see that);
- a pass with an unpriceable fragment is refused, never priced short;
- a leg's verifications come from its results file, retries in the cost;
- a floor is completed only from nominated legs with complete tokens and an
  identical verifier configuration (effective temperature included);
- where nothing was missing, the register reproduces the hand-entered June
  figures within 1 %.

Unit cases build a register and metas in ``tmp_path``; integration cases
read the committed register, mapping and ladders.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.lib_frontier_cost import FrontierCoster, FrontierCostError, Priced

REPO = Path(__file__).resolve().parents[1]
MAPPING = REPO / "data/pricing/frontier-configurations.json"

#: 1 M input (none cached), 100 k output, 200 k thinking on gemini-3-flash-preview:
#: flex 0.25 + 0.45 = US$0.70; standard 0.50 + 0.90 = US$1.40.
USAGE = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
         "total_output_tokens": 100_000, "total_thoughts_tokens": 200_000,
         "total_tokens": 1_300_000, "n_responses_with_usage": 10}
FLEX_USD, STANDARD_USD = 0.70, 1.40

#: A verifier configuration (the Gemini 3 Flash adversarial verifier).
G3 = {"model": "gemini-3-flash-preview", "temperature": 0.0, "thinking_level": "minimal",
      "system_instruction_hash": "abc", "version": "verify_adversarial-text"}


class Repo:
    """A throwaway repository: a register plus the metas it cites."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.rows: list[dict] = []

    def _write(self, rel: str, doc: dict) -> str:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc), encoding="utf-8")
        return rel

    def proposer(self, run: str, pool: str, n: int, *, usage: dict | None = USAGE,
                 billed: float = STANDARD_USD) -> None:
        """``n`` proposer passes, each one fragment with ``usage``."""
        for i in range(1, n + 1):
            meta = self._write(f"outputs/{run}/{pool}/run_{i}/d.meta.json",
                               {"usage_stats": usage or {}})
            self.rows.append({
                "pass_id": f"{run}::{pool}::run{i}", "run_id": run, "proposer_pool": pool,
                "pass_n": i, "n_candidates_verified": None, "cost_basis": "audited",
                "cost_usd": billed,
                "cost_source": {"fragments": [{
                    "meta": meta, "model_recorded": "gemini-3-flash-preview",
                    "model": "gemini-3-flash-preview", "priced_at": "2026-05-20"}]}})

    def leg(self, run: str, pool: str, *, results: int, iterations: int = 1,
            usage: dict | None = USAGE, basis: str = "audited", config: dict | None = None,
            ) -> None:
        """A verifier leg: a meta, its probabilities file, and its register row."""
        meta = self._write(f"outputs/{run}/{pool}/run.meta.json",
                           {"usage_stats": usage or {}, "configuration": config or G3})
        self._write(f"outputs/{run}/{pool}/probabilities.json",
                    {"iterations": iterations,
                     "results": {f"candidate_{i:05d}": [0.9] for i in range(results)}})
        self.rows.append({
            "pass_id": f"{run}::{pool}::run1", "run_id": run, "proposer_pool": pool,
            "pass_n": 1, "n_candidates_verified": results, "cost_basis": basis,
            "cost_usd": FLEX_USD,
            "cost_source": {"fragments": [{
                "meta": meta, "model_recorded": "gemini-3-flash-preview",
                "model": "gemini-3-flash-preview", "priced_at": "2026-05-20"}]}})

    def coster(self) -> FrontierCoster:
        path = self.root / "register.json"
        path.write_text(json.dumps({"passes": self.rows}), encoding="utf-8")
        return FrontierCoster(register_path=path, repo_root=self.root)


@pytest.fixture
def repo(tmp_path) -> Repo:
    return Repo(tmp_path)


# ---------------------------------------------------------------------------
# Units.
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_a_pass_is_priced_at_the_uniform_tier_whatever_it_was_billed(repo):
    # SENTINEL (D19): the register billed this pass at standard (US$1.40);
    # the frontier prices the same tokens at flex.
    repo.proposer("r", "p", 1, billed=STANDARD_USD)
    assert repo.coster().pass_usd("r::p::run1") == pytest.approx(FLEX_USD)


@pytest.mark.tier1
def test_a_rung_of_n_passes_is_n_mean_passes(repo):
    repo.proposer("r", "p", 4)
    coster = repo.coster()
    assert coster.proposer_unit("r", "p").usd == pytest.approx(FLEX_USD)
    assert coster.proposer_cost("r", "p", 3).usd == pytest.approx(3 * FLEX_USD)
    assert coster.proposer_cost("r", "p").usd == pytest.approx(4 * FLEX_USD)  # all passes
    assert len(coster.proposer_cost("r", "p", 1).sources) == 4  # the mean cites every pass
    for bad in (0, 5):
        with pytest.raises(FrontierCostError, match="has 4 passes"):
            coster.proposer_cost("r", "p", bad)


@pytest.mark.tier1
@pytest.mark.parametrize("usage", [None, {"total_input_tokens": 0, "total_output_tokens": 0,
                                          "n_responses_with_usage": 0}])
def test_a_pass_with_an_unrecorded_fragment_is_refused_not_priced_short(repo, usage):
    # Both a missing block and a block of zeros (the "empty batch records" of
    # the GS T0.7 pools) are unrecorded, never free.
    repo.proposer("r", "p", 1, usage=usage)
    with pytest.raises(FrontierCostError, match="no priceable usage"):
        repo.coster().pass_usd("r::p::run1")


@pytest.mark.tier1
def test_a_legs_unit_is_its_cost_over_its_verifications(repo):
    # 1,000 results x 2 iterations; the cost includes any retries.
    repo.leg("r", "v", results=1000, iterations=2)
    unit = repo.coster().candidate_unit("r", "v")
    assert unit.usd == pytest.approx(FLEX_USD / 2000)
    assert unit.basis == "measured" and unit.sources == ("r::v::run1",)


@pytest.mark.tier1
def test_a_leg_without_a_results_file_is_refused(repo):
    repo.leg("r", "v", results=10)
    (repo.root / "outputs/r/v/probabilities.json").unlink()
    with pytest.raises(FrontierCostError, match="no probabilities.json"):
        repo.coster().leg("r", "v")


# ---------------------------------------------------------------------------
# Floors (D19): completed from nominated, comparable legs only.
# ---------------------------------------------------------------------------


def _floor_and_comparable(repo: Repo, comparable_config: dict | None = None,
                          comparable_basis: str = "audited") -> None:
    repo.leg("r", "floor", results=500, usage=None, basis="audited-lower-bound")
    repo.leg("c", "whole", results=1000, basis=comparable_basis,
             config=comparable_config or G3)


@pytest.mark.tier1
def test_a_floor_is_completed_from_its_nominees(repo):
    _floor_and_comparable(repo)
    cost = repo.coster().leg_cost("r", "floor", [{"run_id": "c", "pool": "whole"}])
    assert cost.usd == pytest.approx(500 * FLEX_USD / 1000)
    assert cost.basis == "completed"
    assert cost.sources == ("r::floor::run1", "c::whole::run1")


@pytest.mark.tier1
def test_a_floor_without_nominees_is_refused(repo):
    # SENTINEL: a floor must never be priced at its own (partial) tokens.
    _floor_and_comparable(repo)
    with pytest.raises(FrontierCostError, match="nominate comparable legs"):
        repo.coster().leg_cost("r", "floor")


@pytest.mark.tier1
@pytest.mark.parametrize(("change", "reason"), [
    ({"thinking_level": "low"}, "has configuration"),
    ({"model": "gemini-3.7-flash"}, "has configuration"),
    ({"temperature_effective": 0.5}, "has configuration"),  # E55: the run's real temperature
    ({"system_instruction_hash": "other"}, "has configuration"),
])
def test_a_nominee_with_another_configuration_is_refused(repo, change, reason):
    _floor_and_comparable(repo, comparable_config={**G3, **change})
    with pytest.raises(FrontierCostError, match=reason):
        repo.coster().leg_cost("r", "floor", [{"run_id": "c", "pool": "whole"}])


@pytest.mark.tier1
def test_a_model_alias_is_the_same_configuration(repo):
    # Negative: "gemini-3-flash" is "gemini-3-flash-preview" on the rate card.
    _floor_and_comparable(repo, comparable_config={**G3, "model": "gemini-3-flash"})
    repo.coster().leg_cost("r", "floor", [{"run_id": "c", "pool": "whole"}])


@pytest.mark.tier1
def test_a_nominee_that_is_itself_a_floor_is_refused(repo):
    _floor_and_comparable(repo, comparable_basis="audited-lower-bound")
    with pytest.raises(FrontierCostError, match="is itself a floor"):
        repo.coster().leg_cost("r", "floor", [{"run_id": "c", "pool": "whole"}])


@pytest.mark.tier1
def test_an_upper_bound_leg_is_complete(repo):
    # Its only unknown is the billed tier, which the uniform tier ignores.
    _floor_and_comparable(repo, comparable_basis="audited-upper-bound")
    repo.coster().leg_cost("r", "floor", [{"run_id": "c", "pool": "whole"}])


@pytest.mark.tier1
def test_nominees_pool_cost_over_verifications(repo):
    repo.leg("r", "floor", results=100, usage=None, basis="audited-lower-bound")
    repo.leg("c", "a", results=1000)                                    # 0.70 / 1,000
    repo.leg("c", "b", results=3000, usage={**USAGE, "total_input_tokens": 3_000_000,
                                            "total_output_tokens": 300_000,
                                            "total_thoughts_tokens": 600_000})  # 2.10 / 3,000
    unit = repo.coster().candidate_unit("r", "floor", [{"run_id": "c", "pool": "a"},
                                                       {"run_id": "c", "pool": "b"}])
    assert unit.usd == pytest.approx((0.70 + 2.10) / 4000)  # pooled, not a mean of units


# ---------------------------------------------------------------------------
# Configurations.
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_a_rung_and_a_full_run_are_costed_by_their_spec(repo):
    repo.proposer("r", "p", 10)
    repo.leg("r", "v", results=1000)
    coster = repo.coster()
    rung = coster.configuration_cost({
        "proposer": [{"run_id": "r", "pool": "p", "passes": 3}],
        "verifier": {"unit_from": {"run_id": "r", "pool": "v"}, "candidates": 400}})
    assert rung.usd == pytest.approx(3 * FLEX_USD + 400 * FLEX_USD / 1000)
    full = coster.configuration_cost({
        "proposer": [{"run_id": "r", "pool": "p"}],
        "verifier": {"leg": {"run_id": "r", "pool": "v"}}})
    assert full.usd == pytest.approx(10 * FLEX_USD + FLEX_USD)
    assert isinstance(full, Priced) and full.basis == "measured"


@pytest.mark.tier1
def test_an_empty_spec_is_refused(repo):
    repo.proposer("r", "p", 1)
    with pytest.raises(FrontierCostError, match="neither proposer nor verifier"):
        repo.coster().configuration_cost({})


# ---------------------------------------------------------------------------
# The committed mapping, register and ladders.
# ---------------------------------------------------------------------------

#: The hand-entered figures the mapping replaced (``scripts/final_board_build.py``
#: before 2026-10-04): the reproduction anchors where nothing was missing.
JUNE_FIGURES = {"A-N1": 20.53, "A-N3": 41.22, "A-N5": 59.75, "A-N10": 103.91,
                "B-N1": 30.99, "B-N3": 65.48, "B-N5": 97.22, "B-N10": 173.59,
                "TH7": 207.4, "T03": 261.0, "UPL": 57.87}


@pytest.fixture(scope="module")
def committed():
    doc = json.loads(MAPPING.read_text(encoding="utf-8"))
    coster = FrontierCoster()
    return doc, coster, {k: coster.configuration_cost(v)
                         for k, v in doc["board_families"].items()}


@pytest.mark.tier1
def test_every_board_family_prices_from_register_rows(committed):
    doc, coster, costs = committed
    assert doc["uniform_tier"] == "flex"
    assert len(costs) == 23
    for family, cost in costs.items():
        assert cost.usd > 0, family
        assert all(src in coster.rows for src in cost.sources), family


@pytest.mark.tier1
def test_every_rung_candidate_count_is_its_committed_ladders(committed):
    doc, _, _ = committed
    for family, spec in doc["board_families"].items():
        ver = spec["verifier"]
        if "candidates" not in ver:
            continue
        value = json.loads((REPO / ver["candidates_source"]["file"]).read_text())
        for key in ver["candidates_source"]["keys"]:
            value = value[key]
        assert ver["candidates"] == value, family


@pytest.mark.tier1
def test_the_register_reproduces_the_june_figures_where_nothing_was_missing(committed):
    _, _, costs = committed
    for family, june in JUNE_FIGURES.items():
        assert costs[family].usd == pytest.approx(june, rel=0.01), family


@pytest.mark.tier1
def test_im_is_priced_at_the_uniform_tier_not_as_billed(committed):
    # IM's proposer billed at standard (the cached-path defect, US$359.65 in
    # the register); at the uniform tier it is the June audit's US$195.35.
    _, coster, costs = committed
    proposer = coster.proposer_cost("55maps-image-generalisation", "library_plus-hp")
    assert proposer.usd == pytest.approx(195.35, rel=0.002)
    assert costs["IM"].basis == "completed"  # its verifier leg is a floor


@pytest.mark.tier1
def test_the_four_floors_are_completed_and_nothing_else_is(committed):
    _, _, costs = committed
    completed = {k for k, v in costs.items() if v.basis == "completed"}
    assert completed == {"A-N1", "A-N3", "A-N5", "A-N10", "FOURTH-N1", "FOURTH-N3",
                         "FOURTH-N5", "FOURTH-N10", "TM", "IM"}


@pytest.mark.tier1
def test_flex_equals_batch_on_the_rate_card():
    # The premise of writing the uniform tier as "flex": for every model,
    # flex and batch input and output rates are equal (D19, amended).
    card = json.loads((REPO / "data/pricing/gemini-rate-card.json").read_text())
    for model, spec in card["models"].items():
        if model.startswith("_"):
            continue
        for row in spec["rows"]:
            for usage_class in ("input_fresh", "output"):
                assert row["rates"]["flex"][usage_class] == row["rates"]["batch"][usage_class], \
                    (model, usage_class)


# ---------------------------------------------------------------------------
# The K-ladder builders (WP4b, 2026-10-04).
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_the_fourth_cells_ladder_is_not_priced_as_stride_b():
    # SENTINEL for the Phase 1 defect found 2026-10-04: the cost lookup was
    # keyed by pool alone, and stride B's union was verified twice (Gemini 3,
    # family B; Gemini 3.7, the fourth cell), so the fourth cell's ladder
    # carried B's Gemini 3 verifier costs.
    from scripts.build_k_ladder_tables import board_family
    assert board_family("g384_ov192_55map", "gemini-3.7-flash", "n1-verified37") == "FOURTH"
    assert board_family("g384_ov192_55map", "gemini-3-flash-preview", "n1") == "B"
    assert board_family("g384_ov192_55map_g37", "gemini-3-flash-preview", "arm1-n1") == "ARM1"
    assert board_family("g384_ov192_55map_g37", "gemini-3.7-flash", "arm2-n1") == "ARM2"
    assert board_family("g384_ov128", "gemini-3-flash-preview", "x") is None  # GS: own section


@pytest.mark.tier1
def test_the_gs_stride_a_ladder_reproduces_its_measured_figures(committed):
    doc, coster, _ = committed
    old = {"1": 1.38, "3": 2.64, "5": 3.81, "10": 6.56}  # results/stride-2026-08-25/findings.md
    for n, figure in old.items():
        cost = coster.configuration_cost(doc["k_ladder_phase1_gs_stride_a"][n])
        assert cost.usd == pytest.approx(figure, abs=0.02), n
        assert cost.basis == "measured"


@pytest.mark.tier1
def test_each_phase2_family_is_priced_at_its_own_passes_where_recorded():
    # PI ruling 2026-10-04: own measured GS passes, not a unit borrowed from
    # another family. The MINIMAL image families had borrowed the MINIMAL
    # text unit (0.266) at less than half their measured pass.
    from scripts.lib_frontier_cost import gs_units, phase2_pass_units
    units, named = phase2_pass_units(), gs_units()
    assert len(units) == 14
    for family, (unit, anchor) in units.items():
        if anchor == "own-gs-measured":
            assert all(family in src for src in unit.sources), family
            assert len(unit.sources) == 10, family
    image_min, anchor = units["image-n5-image-t0.3"]
    assert anchor == "own-gs-measured"
    assert image_min.usd > 2 * named["min_pass"].usd
    # T0.7 text: the 55-map measurement of the same configuration, scaled.
    assert units["flash-minimal-text-n30-t07-text-t0.7"] == (named["min_pass"],
                                                              "t07-55map-measured")
    # T0.7 image: the mean of the family's own T0.3 and T1.0 passes.
    mid, anchor = units["flash-high-image-n5-image-t0.7"]
    lo, hi = sorted(units[f"flash-high-image-n5-image-t{t}"][0].usd for t in ("0.3", "1.0"))
    assert anchor == "t07-interpolated" and lo < mid.usd < hi
