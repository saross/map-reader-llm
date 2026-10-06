"""Tier-1 tests for the tile-presence builder (PI ruling 2026-09-21).

``scripts/build_tile_presence_board.py`` takes the "MCC oracle" off the main
boards and presents it separately, with the two things that make it readable
rather than misleading: the **vote count** as a column, and the **verifier
pool** the point would need, priced. Four pieces can silently go wrong, and
each of them would be invisible in the rendered table:

* the Pareto front — dominated points sneaking in would turn the frontier
  from "the trade" into "every point we swept";
* the pool size — it is read off the sweep's own zero-threshold row, so a
  fallback to the wrong row would price the wrong pool;
* the cost arithmetic — and in particular the two flags that say whether the
  point is reachable at all (``pool_exceeds_verified``) or is inheriting a
  bigger verification (``inherits_larger_leg``);
* the verifier-leg lookup, which must resolve LONGEST prefix first or
  ``IMG-ARM2-K3`` silently takes another configuration's rate card.

Everything here runs over synthetic sweep rows or stub costers in memory and
writes nothing. The cost stage's wiring run for real against the committed
register (register -> price_stage -> record -> cross-check -> refusal) is in
``tests/test_tile_presence_board_committed.py`` (tier 2: it reads the 3 MB
register).
"""

from __future__ import annotations

import json

import pytest

from scripts import build_tile_presence_board as tp

pytestmark = pytest.mark.tier1


def _row(prob_t: float, k: int, f1: float | None, mcc: float | None,
         n: int = 100) -> dict:
    """One sweep row, reduced to the keys the builder consults."""
    return {"prob_t": prob_t, "min_votes": k, "n_detections": n,
            "micro_f1_50": f1, "tile_mcc": mcc}


# --- The Pareto front -------------------------------------------------------

def test_the_front_drops_a_dominated_point() -> None:
    """A point beaten on both metrics is not a trade-off."""
    rows = [_row(0.1, 1, 0.80, 0.70), _row(0.2, 1, 0.70, 0.60),
            _row(0.3, 1, 0.60, 0.75)]
    front = tp.pareto_front(rows)
    assert [(r["prob_t"], r["min_votes"]) for r in front] == [(0.1, 1),
                                                              (0.3, 1)]


def test_the_front_is_sorted_by_f1_descending() -> None:
    rows = [_row(0.3, 1, 0.60, 0.75), _row(0.1, 1, 0.80, 0.70),
            _row(0.2, 1, 0.70, 0.72)]
    assert [r["micro_f1_50"] for r in tp.pareto_front(rows)] == [
        0.80, 0.70, 0.60]


def test_an_equal_point_does_not_dominate_its_twin() -> None:
    """Ties are a duplicate coordinate, not a domination; one survives."""
    rows = [_row(0.1, 1, 0.80, 0.70), _row(0.9, 5, 0.80, 0.70)]
    front = tp.pareto_front(rows)
    assert len(front) == 1
    assert (front[0]["prob_t"], front[0]["min_votes"]) == (0.1, 1)


def test_a_point_better_on_one_metric_only_stays() -> None:
    """Equal on F1 and better on MCC dominates; the reverse is kept."""
    rows = [_row(0.1, 1, 0.80, 0.70), _row(0.2, 1, 0.80, 0.75)]
    assert [r["tile_mcc"] for r in tp.pareto_front(rows)] == [0.75]


def test_unscored_rows_are_ignored_not_treated_as_zero() -> None:
    """A point that retained nothing has null metrics, not bad ones."""
    rows = [_row(0.1, 1, 0.80, 0.70), _row(1.0, 5, None, None, n=0)]
    front = tp.pareto_front(rows)
    assert len(front) == 1 and front[0]["micro_f1_50"] == 0.80


def test_an_empty_sweep_has_an_empty_front() -> None:
    assert tp.pareto_front([]) == []


# --- The pool the point needs -----------------------------------------------

def test_the_pool_is_the_zero_threshold_row_at_that_vote_count() -> None:
    """k = 1 admits everything; k = 3 admits only the unanimous."""
    rows = [_row(0.0, 1, 0.5, 0.5, n=8337), _row(0.5, 1, 0.6, 0.6, n=5000),
            _row(0.0, 3, 0.7, 0.7, n=5593), _row(0.5, 3, 0.8, 0.8, n=4000)]
    assert tp.pool_at_vote(rows, 1) == 8337
    assert tp.pool_at_vote(rows, 3) == 5593


def test_the_pool_is_none_when_the_grid_has_no_zero_threshold_row() -> None:
    """A grid built only from observed probabilities may not reach 0.0."""
    assert tp.pool_at_vote([_row(0.15, 3, 0.8, 0.7)], 3) is None


def test_sweep_row_at_tolerates_float_representation() -> None:
    rows = [_row(0.15, 3, 0.8380, 0.6792)]
    assert tp.sweep_row_at(rows, 0.15, 3)["tile_mcc"] == 0.6792
    assert tp.sweep_row_at(rows, 0.20, 3) is None


# --- The cost block ---------------------------------------------------------

LEG = {"stages": ["outputs/x/verify"], "basis": "measured", "usd": 9.2650,
       "candidates": 8337}

#: A leg no rule prices whole (D29): it has no usable cost.
UNPRICED_LEG = {"stages": ["outputs/x/verify"], "basis": "unpriced",
                "usd": None, "candidates": None,
                "note": "no uniform-tier cost: lower bound only (cleanup-overwrite)"}


def test_the_rate_is_the_legs_usd_per_candidate() -> None:
    block = tp.cost_block(8337, LEG)
    assert block["verifier_cost_basis"] == "measured"
    assert block["verifier_usd_per_candidate"] == pytest.approx(
        9.2650 / 8337)
    assert block["pool_verifier_usd"] == pytest.approx(9.2650, abs=1e-4)


def test_a_completed_leg_prices_the_pool_too() -> None:
    """A floor completed from comparable legs (D19) is a cost, labelled so."""
    leg = {**LEG, "basis": "completed"}
    assert tp.cost_block(8337, leg)["pool_verifier_usd"] == pytest.approx(
        9.2650, abs=1e-4)


def test_a_lower_bound_is_never_multiplied_into_a_cost() -> None:
    """The one arithmetic this builder must refuse to do.

    A lower bound times a pool size is a number that looks like a cost and
    is not, so an unpriced leg prices nothing and says why.
    """
    block = tp.cost_block(8337, UNPRICED_LEG)
    assert block["verifier_cost_basis"] == "unpriced"
    assert block["verifier_usd_per_candidate"] is None
    assert block["pool_verifier_usd"] is None
    assert "cleanup-overwrite" in block["verifier_cost_note"]


def test_an_unmapped_leg_is_distinguished_from_an_unpriced_one() -> None:
    assert tp.cost_block(100, None)["verifier_cost_basis"] == "unmapped"


def test_a_smaller_pool_is_flagged_as_inheriting_a_larger_leg() -> None:
    """An A/B rung inherits probabilities from the K = 10 union's leg."""
    block = tp.cost_block(4000, LEG)
    assert block["inherits_larger_leg"] is True
    assert block["pool_exceeds_verified"] is False
    assert block["pool_verifier_usd"] == pytest.approx(
        4000 * 9.2650 / 8337, abs=1e-4)


def test_a_larger_pool_is_flagged_as_unreachable() -> None:
    """The point asks for candidates the leg never verified."""
    block = tp.cost_block(12000, LEG)
    assert block["pool_exceeds_verified"] is True
    assert block["inherits_larger_leg"] is False


def test_an_exact_pool_is_neither_inherited_nor_short() -> None:
    block = tp.cost_block(8337, LEG)
    assert block["inherits_larger_leg"] is False
    assert block["pool_exceeds_verified"] is False


def test_a_missing_leg_prices_nothing_rather_than_guessing() -> None:
    block = tp.cost_block(8337, None)
    assert block["verifier_usd_per_candidate"] is None
    assert block["pool_verifier_usd"] is None
    assert block["pool_exceeds_verified"] is None


def test_a_missing_pool_prices_nothing() -> None:
    assert tp.cost_block(None, LEG)["pool_verifier_usd"] is None


# --- The verifier-leg lookup ------------------------------------------------

def test_the_longest_prefix_wins() -> None:
    """``IMG-ARM2-K3`` must not fall through to a shorter family prefix."""
    assert tp.leg_for("IMG-ARM2-K3") == tp.LEGS["IMG-ARM2-K3"]
    assert tp.leg_for("G3IMG-ARM1-K5") == tp.LEGS["G3IMG-ARM1-K5"]


def test_board_rungs_share_their_unions_leg() -> None:
    """Every A rung inherits from run A's one carry-forward verifier leg."""
    for rung in ("A-N1", "A-N3", "A-N5", "A-N10"):
        assert tp.leg_for(rung) == tp.LEGS["A-"]
    for rung in ("FOURTH-N1", "FOURTH-N10"):
        assert tp.leg_for(rung) == tp.LEGS["FOURTH-"]


def test_the_two_pass_text_legs_carry_both_stages() -> None:
    """The vote-3 increment is a second pass of the same leg, and is summed."""
    for family in ("TH7", "T03", "TM"):
        assert len(tp.leg_for(family)) == 2
        assert any("vote3-verify" in s for s in tp.leg_for(family))


def test_an_unmapped_configuration_returns_none() -> None:
    assert tp.leg_for("NOT-A-FAMILY") is None


class _StubCoster:
    """Records which pricing route each stage took; prices nothing real."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def leg_cost(self, run_id, pool, comparables):
        self.calls.append(("register", run_id, pool, comparables))
        return tp.Priced(1.0, (f"{run_id}::{pool}::run1",))

    def leg(self, run_id, pool):
        return type("L", (), {"verifications": 10})()

    def stage_leg_cost(self, stage, *, complete, comparables=None):
        self.calls.append(("stage", stage, complete, comparables))
        return tp.Priced(2.0, (f"stage:{stage}",), "measured" if complete else "completed")

    def stage_leg(self, stage, *, complete):
        return type("L", (), {"verifications": 20})()


BOARD_FAMILIES = {"TM": {"verifier": {"comparables": [{"run_id": "c", "pool": "p"}]}}}


def test_a_register_floor_takes_the_boards_nominated_comparables() -> None:
    coster = _StubCoster()
    row = {"pass_id": "r::v::run1", "run_id": "r", "proposer_pool": "v",
           "cost_source": {"fragments": [{"meta": "outputs/r/v/run.meta.json"}]}}
    cost, calls, inside = tp.price_stage(coster, "outputs/r/v", "TM",
                                         {"outputs/r/v": [row]}, BOARD_FAMILIES)
    assert coster.calls == [("register", "r", "v", [{"run_id": "c", "pool": "p"}])]
    assert (calls, inside) == (10, True)


def test_a_register_row_whose_first_fragment_is_elsewhere_is_refused() -> None:
    # The leg's calls are counted beside its first fragment: a row indexed
    # under this stage by a later source file must not be priced here.
    row = {"pass_id": "r::v::run1", "run_id": "r", "proposer_pool": "v",
           "cost_source": {"fragments": [{"meta": "outputs/r/elsewhere/run.meta.json"}]}}
    with pytest.raises(tp.FrontierCostError, match="first fragment is not in"):
        tp.price_stage(_StubCoster(), "outputs/r/v", "TM", {"outputs/r/v": [row]},
                       BOARD_FAMILIES)


def test_a_published_row_is_completed_from_its_d30_nominee() -> None:
    coster = _StubCoster()
    row = {"pass_id": "g::k1::run1", "run_id": "g", "proposer_pool": "k1",
           "cost_basis": "published", "cost_source": None}
    cost, calls, inside = tp.price_stage(coster, "outputs/g/k1", "IMG-ARM2-K1",
                                         {"outputs/g/k1": [row]}, BOARD_FAMILIES)
    assert coster.calls == [("stage", "outputs/g/k1", False,
                             tp.PUBLISHED_COMPARABLES["IMG-ARM2-K1"])]
    assert cost.basis == "completed" and inside is True


def test_a_published_row_without_a_nominee_is_refused() -> None:
    # SENTINEL: a published figure is never silently re-priced as the
    # leg's own tokens, nor passed through unchecked.
    row = {"pass_id": "g::k9::run1", "run_id": "g", "proposer_pool": "k9",
           "cost_source": {}}
    with pytest.raises(tp.FrontierCostError, match="no comparable is nominated"):
        tp.price_stage(_StubCoster(), "outputs/g/k9", "IMG-ARM2-K9",
                       {"outputs/g/k9": [row]}, BOARD_FAMILIES)


def test_a_stage_outside_the_register_is_priced_from_its_meta_and_marked() -> None:
    coster = _StubCoster()
    cost, calls, inside = tp.price_stage(coster, "results/v3/verified", "TH7", {},
                                         BOARD_FAMILIES)
    assert coster.calls == [("stage", "results/v3/verified", True, None)]
    assert (calls, inside) == (20, False)


def test_two_rows_claiming_one_stage_are_refused_when_it_is_asked_for(tmp_path) -> None:
    # Shared stages exist elsewhere in the register (outputs/h11/...): the
    # index keeps them, and only a mapped leg asking for one is refused.
    rows = [{"pass_id": f"r::v::run{i}", "n_candidates_verified": 5,
             "provenance": {"source_files": [f"outputs/r/v/m{i}.meta.json"]}} for i in (1, 2)]
    path = tmp_path / "register.json"
    path.write_text(json.dumps({"passes": rows}))
    index = tp.register_index(path)
    assert [r["pass_id"] for r in index["outputs/r/v"]] == ["r::v::run1", "r::v::run2"]
    with pytest.raises(tp.FrontierCostError, match="is claimed by"):
        tp.price_stage(_StubCoster(), "outputs/r/v", "B-", index, BOARD_FAMILIES)


def test_every_committed_leg_resolves_to_the_register_or_a_named_gap() -> None:
    """Drift guard over the committed register (D30): every stage of every
    mapped leg is a register stage. The three vote-3 increments were the
    named gap until the S160 repair extracted them (D32: rows of their
    parent runs), so the gap is now empty; a new outside stage turns this
    red."""
    index = tp.register_index()
    assert all(len(index[s]) == 1 for stages in tp.LEGS.values() for s in stages if s in index)
    outside = sorted(s for stages in tp.LEGS.values() for s in stages if s not in index)
    assert outside == []
    published = sorted(k for k, stages in tp.LEGS.items()
                       if not (index[stages[0]][0].get("cost_source") or {}).get("fragments"))
    assert published == sorted(tp.PUBLISHED_COMPARABLES)


def test_the_vote3_increments_price_the_same_through_their_register_rows() -> None:
    """D30's drift test: the increments priced through their new register
    rows (D32) equal their own metas priced directly, as WP4 priced them
    while they were outside the register (US$2.97, US$2.74, US$1.51)."""
    coster = tp.FrontierCoster()
    index = tp.register_index()
    stages = [s for f in ("TH7", "T03", "TM") for s in tp.LEGS[f] if "vote3-verify" in s]
    assert len(stages) == 3
    for stage in stages:
        (row,) = index[stage]
        assert row["proposer_pool"] == "vote3-increment"
        via_row = coster.leg_cost(row["run_id"], row["proposer_pool"], None).usd
        direct = coster.stage_leg_cost(stage, complete=True).usd
        assert via_row == pytest.approx(direct, abs=5e-7), stage


def test_every_mapped_leg_is_a_repository_relative_path() -> None:
    """An absolute path here would audit whatever happened to be there."""
    for stages in tp.LEGS.values():
        for stage in stages:
            assert not stage.startswith("/")
            assert stage.startswith(("outputs/", "results/"))


# --- Ranking ----------------------------------------------------------------

def test_rank_is_by_tile_mcc_descending_and_one_based() -> None:
    rows = [{"config": "lo", "tile_mcc": 0.70},
            {"config": "hi", "tile_mcc": 0.78},
            {"config": "mid", "tile_mcc": 0.74}]
    ranked = tp.rank_by_tile_mcc(rows)
    assert [r["config"] for r in ranked] == ["hi", "mid", "lo"]
    assert [r["rank"] for r in ranked] == [1, 2, 3]


# --- The table's own contract -----------------------------------------------

def test_every_rendered_row_says_ORACLE_and_shows_its_vote_count() -> None:
    """The two things the ruling asks the table never to leave implicit."""
    row = {"rank": 1, "config": "ARM2-N5", "track": "board", "basis": "ORACLE",
           "min_votes": 1, "prob_t": 0.96, "n_detections": 5924,
           "tile_mcc": 0.7487, "micro_f1_50": 0.8055,
           "carried_point": [0.80, 5], "carried_tile_mcc": 0.7076,
           "tile_mcc_over_carried": 0.0411, "pool_n_at_vote": 12715,
           "verifier_leg_items": 12715,
           "verifier_usd_per_candidate": 0.000699,
           "pool_verifier_usd": 8.89, "pool_exceeds_verified": False}
    line = tp.render_row(row)
    assert "| ORACLE |" in line
    assert "**k1**" in line
    assert "(0.80, k5)" in line


def test_an_unreachable_pool_is_marked_in_the_table() -> None:
    row = {"rank": 1, "config": "X", "track": "board", "basis": "ORACLE",
           "min_votes": 1, "prob_t": 0.5, "n_detections": 10,
           "tile_mcc": 0.7, "micro_f1_50": 0.6, "carried_point": None,
           "carried_tile_mcc": None, "tile_mcc_over_carried": None,
           "pool_n_at_vote": 99, "verifier_leg_items": 10,
           "verifier_usd_per_candidate": None, "pool_verifier_usd": None,
           "pool_exceeds_verified": True}
    assert "99 ⚠" in tp.render_row(row)
    assert "| — |" in tp.render_row(row)


# --- --check: the drift guard -----------------------------------------------

def _ranked_rows() -> list[dict]:
    """Two complete leaderboard rows, as build_rows would rank them."""
    base = {"track": "board", "basis": "ORACLE", "prob_t": 0.5,
            "n_detections": 10, "tile_tp": 1, "tile_tn": 1, "tile_fp": 1,
            "tile_fn": 1, "micro_f1_50": 0.6, "carried_point": None,
            "carried_tile_mcc": None, "carried_micro_f1_50": None,
            "tile_mcc_over_carried": None, "micro_f1_50_vs_carried": None,
            "pool_n_at_vote": 10, "verifier_leg_items": 10,
            "verifier_usd_per_candidate": None, "pool_verifier_usd": None,
            "pool_exceeds_verified": False, "inherits_larger_leg": False,
            "verifier_cost_basis": "unmapped", "verifier_cost_note": None,
            "verifier_leg_paths": None, "verifier_leg_usd": None,
            "sweep_csv": "x.csv"}
    return tp.rank_by_tile_mcc([
        {**base, "config": "A-N1", "min_votes": 1, "tile_mcc": 0.7},
        {**base, "config": "B-N3", "min_votes": 3, "tile_mcc": 0.8},
    ])


def test_report_drift_names_a_differing_and_a_missing_file(tmp_path) -> None:
    same = tmp_path / "same.txt"
    same.write_text("same")
    differs = tmp_path / "differs.txt"
    differs.write_text("old")
    missing = tmp_path / "missing.txt"
    stale = tp.report_drift({same: "same", differs: "new", missing: "x"})
    assert stale == [str(differs), f"{missing} (missing)"]


def test_leaderboard_payload_is_pure_and_carries_every_row() -> None:
    """The payload is the same two files the stage writes, from rows alone."""
    rows = _ranked_rows()
    payload = tp.leaderboard_payload(rows)
    assert set(p.name for p in payload) == {"leaderboard.json", "leaderboard.md"}
    record = json.loads(payload[tp.OUT / "leaderboard.json"])
    assert record["n_configurations"] == 2
    assert [r["config"] for r in record["rows"]] == ["B-N3", "A-N1"]
    assert payload[tp.OUT / "leaderboard.md"] == tp.leaderboard_markdown(rows)


def test_check_writes_nothing_and_fails_until_the_files_match(
        tmp_path, monkeypatch) -> None:
    """--check is a comparison, never a write: stale -> 1, matching -> 0."""
    monkeypatch.setattr(tp, "OUT", tmp_path)
    (tmp_path / tp.COSTS).write_text(json.dumps({"legs": {}}))
    monkeypatch.setattr(tp, "build_rows", lambda costs: _ranked_rows())
    assert tp.main(["--stage", "leaderboard", "--check"]) == 1
    assert not (tmp_path / "leaderboard.md").exists()
    assert not (tmp_path / "leaderboard.json").exists()
    assert tp.main(["--stage", "leaderboard"]) == 0
    assert tp.main(["--stage", "leaderboard", "--check"]) == 0
    (tmp_path / "leaderboard.md").write_text("edited by hand\n")
    assert tp.main(["--stage", "leaderboard", "--check"]) == 1
    assert (tmp_path / "leaderboard.md").read_text() == "edited by hand\n"


def test_check_does_not_apply_to_relabel(monkeypatch, capsys) -> None:
    """argparse rejects the pair (exit 2) before any manifest is touched."""
    monkeypatch.setattr(tp, "MANIFESTS", ())
    monkeypatch.setattr(tp, "CAMPAIGN_SWEEPS", ())
    with pytest.raises(SystemExit) as exc:
        tp.main(["--stage", "relabel", "--check"])
    assert exc.value.code == 2
    assert "does not apply to --stage relabel" in capsys.readouterr().err


def test_report_drift_sees_a_trailing_newline(tmp_path) -> None:
    """The contract is byte for byte: a missing final newline is drift."""
    f = tmp_path / "f.md"
    f.write_text("same")
    assert tp.report_drift({f: "same\n"}) == [str(f)]
    assert tp.report_drift({f: "same"}) == []


def test_leaderboard_payload_states_its_reference_and_basis() -> None:
    """The JSON header is content, not routing: reference, buffer, the warning."""
    record = json.loads(tp.leaderboard_payload(_ranked_rows())[tp.OUT / "leaderboard.json"])
    assert record["reference"] == "r2"
    assert record["buffer_m"] == tp.BUFFER_M
    assert "EVERY ROW IS AN ORACLE" in record["_README"]
    assert record["generated_by"] == "scripts/build_tile_presence_board.py"


def _real_shaped_track(tmp_path) -> tp.Track:
    """One campaign-style track on disk: sweeps.json plus one sweep CSV."""
    home = tmp_path / "campaign"
    home.mkdir()
    header = ("rung,prob_t,min_votes,n_detections,tp,fp,fn,micro_f1_50,tile_mcc,"
              "tile_tp,tile_tn,tile_fp,tile_fn\n")
    rows = [
        # (prob_t, k, n, f1, mcc): the k1 zero-threshold row sizes the pool
        ("X-K3", 0.0, 1, 100, 0.50, 0.60),
        ("X-K3", 0.9, 1, 40, 0.70, 0.80),   # the unconstrained optimum
        ("X-K3", 0.0, 3, 60, 0.55, 0.62),
        ("X-K3", 0.5, 3, 30, 0.75, 0.70),   # the carried point
    ]
    (home / "sweep_X-K3.csv").write_text(header + "".join(
        f"{r},{p},{k},{n},1,1,1,{f1},{mcc},1,1,1,1\n" for r, p, k, n, f1, mcc in rows))
    (home / "sweeps.json").write_text(json.dumps({"rungs": {"X-K3": {
        "carried_point": [0.5, 3],
        "mcc_argmax_unconstrained": {
            "prob_t": 0.9, "min_votes": 1, "n_detections": 40,
            "micro_f1_50": 0.70, "tile_mcc": 0.80,
            "tile_tp": 1, "tile_tn": 1, "tile_fp": 1, "tile_fn": 1},
    }}}))
    return tp.Track("t", "a track", home, "rungs", "mcc_argmax_unconstrained")


def test_build_rows_reads_the_carried_point_and_prices_the_pool(
        tmp_path, monkeypatch) -> None:
    """The real path: sweep record + CSV + costs -> one row, every derived field."""
    monkeypatch.setattr(tp, "TRACKS", (_real_shaped_track(tmp_path),))
    monkeypatch.setattr(tp, "BOARD_HOME", tmp_path / "no-board")
    costs = {"X-K3": {"basis": "measured", "usd": 2.0, "candidates": 80,
                      "stages": ["outputs/leg"], "note": None}}
    [row] = tp.build_rows(costs)
    assert (row["config"], row["rank"], row["min_votes"], row["prob_t"]) == ("X-K3", 1, 1, 0.9)
    assert row["carried_point"] == [0.5, 3]
    assert row["carried_tile_mcc"] == 0.70
    assert row["carried_micro_f1_50"] == 0.75
    assert row["tile_mcc_over_carried"] == pytest.approx(0.80 - 0.70)
    assert row["micro_f1_50_vs_carried"] == pytest.approx(0.70 - 0.75)
    assert row["pool_n_at_vote"] == 100          # the k1 row at prob_t 0.0
    assert row["pool_exceeds_verified"] is True  # 100 > 80 verified
    assert row["pool_verifier_usd"] == pytest.approx(100 * 2.0 / 80)
    assert row["verifier_leg_paths"] == ["outputs/leg"]
    assert row["sweep_csv"].endswith("campaign/sweep_X-K3.csv")


def _stub_fronts() -> tuple[dict, list, dict]:
    fronts = {"X-K3": {"track": "t", "n_sweep_points": 2, "n_non_dominated": 2,
                       "carried_point": [0.5, 3], "f1_oracle_point": None,
                       "mcc_optimum_point": [0.9, 1],
                       "front": [{"prob_t": 0.9, "min_votes": 1, "n_detections": 40,
                                  "micro_f1_50": 0.7, "tile_mcc": 0.8}]}}
    return fronts, [("X-K3", 2)], {"X-K3": {"carried_row": None, "f1_best": None}}


def test_check_frontier_draws_no_figure_and_fails_on_drift(
        tmp_path, monkeypatch) -> None:
    """The frontier guard: --check compares the two text files and never draws."""
    monkeypatch.setattr(tp, "OUT", tmp_path)
    monkeypatch.setattr(tp, "compute_fronts", _stub_fronts)
    drawn = tmp_path / "frontier" / "drawn.marker"

    def fake_draw(fronts, marks):
        drawn.parent.mkdir(parents=True, exist_ok=True)
        drawn.write_text("png")
    monkeypatch.setattr(tp, "draw_frontier_figures", fake_draw)
    assert tp.main(["--stage", "frontier", "--check"]) == 1
    assert not (tmp_path / "frontier").exists()
    assert tp.main(["--stage", "frontier"]) == 0
    assert drawn.exists() and (tmp_path / "frontier" / "frontier.md").exists()
    drawn.unlink()
    assert tp.main(["--stage", "frontier", "--check"]) == 0
    assert not drawn.exists()
    (tmp_path / "frontier" / "frontier.json").write_text("{}\n")
    assert tp.main(["--stage", "frontier", "--check"]) == 1


def test_check_costs_fails_on_drift_and_writes_nothing(tmp_path, monkeypatch) -> None:
    """The costs guard: the priced records are compared, not written."""
    monkeypatch.setattr(tp, "OUT", tmp_path)
    records = {"X-K3": {"basis": "measured", "usd": 2.0, "candidates": 80}}
    monkeypatch.setattr(tp, "collect_costs", lambda: (records, 1, []))
    assert tp.main(["--stage", "costs", "--check"]) == 1
    assert not (tmp_path / tp.COSTS).exists()
    assert tp.main(["--stage", "costs"]) == 0
    assert tp.main(["--stage", "costs", "--check"]) == 0
    (tmp_path / tp.COSTS).write_text("{}\n")
    assert tp.main(["--stage", "costs", "--check"]) == 1


def test_a_cost_disagreement_blocks_the_write_and_the_check(
        tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(tp, "OUT", tmp_path)
    monkeypatch.setattr(tp, "collect_costs",
                        lambda: ({"X": {"basis": "measured"}}, 1, ["X: off by 1"]))
    assert tp.main(["--stage", "costs"]) == 1
    assert not (tmp_path / tp.COSTS).exists()


def test_check_all_compares_every_stage_before_deciding(
        tmp_path, monkeypatch, caplog) -> None:
    """One run names every stale file; a stale first stage still yields 1."""
    monkeypatch.setattr(tp, "OUT", tmp_path)
    records = {"X-K3": {"basis": "measured", "usd": 2.0, "candidates": 80}}
    monkeypatch.setattr(tp, "collect_costs", lambda: (records, 1, []))
    monkeypatch.setattr(tp, "build_rows", lambda costs: _ranked_rows())
    monkeypatch.setattr(tp, "compute_fronts", _stub_fronts)
    monkeypatch.setattr(tp, "draw_frontier_figures", lambda fronts, marks: None)
    assert tp.main(["--stage", "all"]) == 0
    assert tp.main(["--stage", "all", "--check"]) == 0
    # Only the FIRST stage stale: a later match must not mask it. The stale
    # file stays well-formed so the leaderboard stage can still read it.
    (tmp_path / tp.COSTS).write_text(json.dumps({"legs": {}}) + "\n")
    assert tp.main(["--stage", "all", "--check"]) == 1
    # Two stages stale: both are named, so the run did not stop at the first.
    (tmp_path / "leaderboard.md").write_text("edited\n")
    caplog.clear()
    with caplog.at_level("ERROR"):
        assert tp.main(["--stage", "all", "--check"]) == 1
    stale = [r.getMessage() for r in caplog.records if "STALE" in r.getMessage()]
    assert any(tp.COSTS in m for m in stale)
    assert any("leaderboard.md" in m for m in stale)


def test_a_missing_costs_file_is_drift_under_check_and_an_error_when_writing(
        tmp_path, monkeypatch, caplog) -> None:
    monkeypatch.setattr(tp, "OUT", tmp_path)
    with caplog.at_level("ERROR"):
        assert tp.main(["--stage", "leaderboard", "--check"]) == 1
    assert any("(missing)" in r.getMessage() for r in caplog.records)
    with pytest.raises(SystemExit, match="run --stage costs first"):
        tp.main(["--stage", "leaderboard"])


def test_a_configuration_name_shared_by_two_tracks_is_refused(
        tmp_path, monkeypatch) -> None:
    track = _real_shaped_track(tmp_path)
    monkeypatch.setattr(tp, "TRACKS", (track, tp.Track("u", "twin", track.home,
                                                       "rungs", "mcc_argmax_unconstrained")))
    monkeypatch.setattr(tp, "BOARD_HOME", tmp_path / "no-board")
    with pytest.raises(RuntimeError, match="shared by tracks"):
        tp.compute_fronts()


def test_an_unreadable_costs_file_is_drift_under_check(tmp_path, monkeypatch, caplog) -> None:
    """No key, a list where an object should be, bad JSON, bad bytes: all drift."""
    monkeypatch.setattr(tp, "OUT", tmp_path)
    for payload in (b"{}\n", b'{"legs": []}\n', b"[1]\n", b"not json", b"\xff\xfe{}"):
        (tmp_path / tp.COSTS).write_bytes(payload)
        caplog.clear()
        with caplog.at_level("ERROR"):
            assert tp.main(["--stage", "leaderboard", "--check"]) == 1, payload
        assert any("unreadable" in r.getMessage() for r in caplog.records), payload
    (tmp_path / tp.COSTS).write_text("{}\n")
    with pytest.raises(SystemExit, match="unreadable"):
        tp.main(["--stage", "leaderboard"])


def test_an_unpriced_leg_is_written_listed_and_reported(tmp_path, monkeypatch, caplog) -> None:
    """PI ruling 2026-10-04: the write goes ahead, but an unpriced leg is listed
    in the file and logged as an ERROR block, so it reaches the PI."""
    monkeypatch.setattr(tp, "OUT", tmp_path)
    records = {
        "X-K3": {"basis": "measured", "usd": 2.0, "candidates": 80, "stages": ["outputs/x"],
                 "configs": ["X-K3"]},
        "Y-K1": {"basis": "unpriced", "usd": None, "candidates": None,
                 "stages": ["outputs/y"], "configs": ["Y-K1"], "note": "no rule prices it"},
    }
    monkeypatch.setattr(tp, "collect_costs", lambda: (records, 2, []))
    with caplog.at_level("ERROR"):
        assert tp.main(["--stage", "costs"]) == 0          # kept as is: not blocked
    written = json.loads((tmp_path / tp.COSTS).read_text())
    assert written["unpriced_legs"] == [{"stages": ["outputs/y"], "configs": ["Y-K1"],
                                         "note": "no rule prices it"}]
    errors = [r.getMessage() for r in caplog.records if r.levelname == "ERROR"]
    assert any("UNPRICED" in m and "WITH THE PI" in m for m in errors)
    assert any("outputs/y" in m and "Y-K1" in m for m in errors)


def test_a_fully_priced_run_reports_nothing_unpriced(tmp_path, monkeypatch, caplog) -> None:
    monkeypatch.setattr(tp, "OUT", tmp_path)
    records = {"X-K3": {"basis": "measured", "usd": 2.0, "candidates": 80,
                        "stages": ["outputs/x"], "configs": ["X-K3"]}}
    monkeypatch.setattr(tp, "collect_costs", lambda: (records, 1, []))
    with caplog.at_level("ERROR"):
        assert tp.main(["--stage", "costs"]) == 0
    assert json.loads((tmp_path / tp.COSTS).read_text())["unpriced_legs"] == []
    assert not any("UNPRICED" in r.getMessage() for r in caplog.records)
