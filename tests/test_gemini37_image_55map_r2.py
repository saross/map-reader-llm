"""
Tier-1 tests for the pure logic of ``scripts/gemini37_image_55map_r2.py``.

The script's statistical mechanism is gated at run time against four committed
evaluations (``--stage selftest``), which is a stronger check than any fixture
could be and needs the real reference frames. What is tested here is the logic
that no committed artefact would catch: the operating-point predicate, the
achievable grid, the rule that forces a carried point into that grid even when
no candidate sits on it, and the rung labelling the stages round-trip through.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point

from scripts.gemini37_image_55map_r2 import (
    CARRIED,
    PROJECT_ROOT,
    achievable_points,
    engine_command,
    materialise,
    rung_label,
    with_carried,
)

pytestmark = pytest.mark.tier1


@pytest.fixture
def frame() -> gpd.GeoDataFrame:
    """Five candidates spanning three probabilities and three vote counts."""
    rows = [
        (1.0, 3),
        (0.88, 3),
        (0.88, 2),
        (0.2, 1),
        (0.0, 1),
    ]
    return gpd.GeoDataFrame(
        {
            "mound_probability": [p for p, _ in rows],
            "vote_count": [v for _, v in rows],
            "source_tile": ["t.png"] * len(rows),
        },
        geometry=[Point(400000 + i, 4700000) for i in range(len(rows))],
        crs="EPSG:32635",
    )


def test_the_predicate_is_inclusive_on_both_axes(frame: gpd.GeoDataFrame) -> None:
    """A candidate exactly at the threshold is kept, on probability and on votes."""
    kept = materialise(frame, 0.88, 2)
    assert len(kept) == 3, "1.0/k3, 0.88/k3 and 0.88/k2"
    assert set(kept["mound_probability"]) == {1.0, 0.88}


def test_a_vote_threshold_above_the_pool_retains_nothing(
    frame: gpd.GeoDataFrame,
) -> None:
    """An unreachable point yields an empty set rather than an error."""
    assert materialise(frame, 0.0, 9).empty


def test_zero_thresholds_retain_everything(frame: gpd.GeoDataFrame) -> None:
    """(0.0, k1) is the whole union — the sweep's left-hand anchor."""
    assert len(materialise(frame, 0.0, 1)) == len(frame)


def test_achievable_grid_is_zero_plus_observed_probabilities(
    frame: gpd.GeoDataFrame,
) -> None:
    """The grid is the board's: {0} union the observed values, crossed with k."""
    points = achievable_points(frame, 3)
    probs = sorted({p for p, _ in points})
    assert probs == [0.0, 0.2, 0.88, 1.0]
    assert sorted({v for _, v in points}) == [1, 2, 3]
    assert len(points) == len(probs) * 3


def test_a_k1_rung_sweeps_only_one_vote_threshold(frame: gpd.GeoDataFrame) -> None:
    """K = 1 cannot carry a vote threshold above 1."""
    assert {v for _, v in achievable_points(frame, 1)} == {1}


def test_the_carried_point_is_forced_into_the_grid(frame: gpd.GeoDataFrame) -> None:
    """arm1's 0.10 is observed nowhere here, and must still be swept."""
    grid = achievable_points(frame, 3)
    assert (CARRIED["arm1"], 3) not in grid
    forced = with_carried(grid, "arm1", 3)
    assert (CARRIED["arm1"], 3) in forced
    assert len(forced) == len(grid) + 1


def test_forcing_is_idempotent_when_the_point_is_already_reachable(
    frame: gpd.GeoDataFrame,
) -> None:
    """arm2's 0.88 is observed, so the grid is returned unchanged."""
    grid = achievable_points(frame, 3)
    assert with_carried(grid, "arm2", 3) == grid


def test_a_k1_rung_carries_the_probability_with_votes_collapsed(
    frame: gpd.GeoDataFrame,
) -> None:
    """Both carried points select unanimity, so k collapses to 1 at K = 1."""
    forced = with_carried(achievable_points(frame, 1), "arm1", 1)
    assert (CARRIED["arm1"], 1) in forced


@pytest.mark.parametrize(
    ("arm", "k", "expected"),
    [
        ("arm1", 1, "IMG-ARM1-K1"),
        ("arm1", 3, "IMG-ARM1-K3"),
        ("arm2", 1, "IMG-ARM2-K1"),
        ("arm2", 3, "IMG-ARM2-K3"),
    ],
)
def test_rung_labels_round_trip_to_their_pass_count(
    arm: str, k: int, expected: str
) -> None:
    """The stages recover K and the arm from the label, so both must survive it."""
    label = rung_label(arm, k)
    assert label == expected
    assert int(label.rsplit("K", 1)[1]) == k
    assert ("ARM1" in label) == (arm == "arm1")


#: A committed r2 board cell, whose own ``cli_args`` block is the recipe this
#: campaign must reproduce. Reading the recipe from the artefact rather than
#: from prose is the point: a board rebuild that changed it would fail here.
_COMMITTED_CELL = Path(
    "results/55map-final-board-r2-2026-09-06/cells/FOURTH-N1-oracle/evaluation.json"
)


def test_engine_command_reproduces_the_committed_recipe() -> None:
    """Every scoring parameter matches a committed r2 board cell's own record."""
    committed = json.loads((PROJECT_ROOT / _COMMITTED_CELL).read_text())
    want = committed["_metadata"]["cli_args"]
    cmd = engine_command("d.geojson", "out", "CELL", workers=5)

    def value_after(flag: str) -> str:
        return cmd[cmd.index(flag) + 1]

    assert value_after("--ground-truth") == want["ground_truth"]
    assert value_after("--bounds") == want["bounds"]
    assert int(value_after("--bootstrap")) == want["bootstrap"]
    assert int(value_after("--seed")) == want["seed"]
    assert "--mcc" in cmd
    assert "--require-clean-inputs" in cmd
    start = cmd.index("--buffers") + 1
    buffers = []
    for token in cmd[start:]:
        if token.startswith("--"):
            break
        buffers.append(int(token))
    assert buffers == want["buffers"]


# ---------------------------------------------------------------------------
# The scoring-frame tile assignment.
#
# Regression cover for the defect that the four original mechanism gates could
# not see: they all consume comparator detection sets, which already carry
# scoring-frame ``source_tile`` names, so none of them exercises a campaign
# rung whose names come from the proposer's 192 px-stride tiling. Under the
# published ``id`` join such a rung books almost nothing and the per-tile
# invariant refuses.
# ---------------------------------------------------------------------------


def test_assign_eval_frame_tiles_rewrites_onto_the_frame_and_keeps_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The rule replaces ``source_tile`` and preserves the proposer's tile."""
    from scripts import gemini37_image_55map_r2 as mod

    # Two proposer-vocabulary origins on one map; a stub index stands in for
    # the real 8,541-tile frame so the test stays tier-1 (no data files).
    monkeypatch.setattr(mod, "build_map_constrained_index", lambda: {"MAPA": {}})
    monkeypatch.setattr(
        mod, "assign_standard_tile",
        lambda index, origin, x, y: f"MAPA_x{int(x)}_y{int(y)}.png",
    )
    frame = gpd.GeoDataFrame(
        {
            "vote_count": [1, 3],
            "mound_probability": [0.9, 0.5],
            "source_tile": ["MAPA_x1152_y2880.png", "MAPA_x1344_y1344.png"],
        },
        geometry=[Point(10, 20), Point(30, 40)],
        crs="EPSG:32635",
    )

    out = mod.assign_eval_frame_tiles(frame)

    assert list(out["source_tile"]) == ["MAPA_x10_y20.png", "MAPA_x30_y40.png"]
    assert list(out["origin_source_tile"]) == [
        "MAPA_x1152_y2880.png",
        "MAPA_x1344_y1344.png",
    ]
    # The input is not mutated: the caller's frame must survive intact.
    assert list(frame["source_tile"]) == [
        "MAPA_x1152_y2880.png",
        "MAPA_x1344_y1344.png",
    ]
    assert "origin_source_tile" not in frame.columns


def test_assign_eval_frame_tiles_passes_the_origin_tile_for_the_map_constraint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The origin tile reaches the assigner, which needs it for the map.

    The map constraint is the part of the rule that matters most: the sheet
    rasters overlap, and an unconstrained nearest-centroid assignment flips
    about 10 per cent of candidates to the adjacent sheet.
    """
    from scripts import gemini37_image_55map_r2 as mod

    seen: list[str] = []

    def spy(index: object, origin: str, x: float, y: float) -> str:
        seen.append(origin)
        return "T.png"

    monkeypatch.setattr(mod, "build_map_constrained_index", lambda: {})
    monkeypatch.setattr(mod, "assign_standard_tile", spy)
    frame = gpd.GeoDataFrame(
        {
            "vote_count": [1],
            "mound_probability": [0.9],
            "source_tile": ["K-35-042-3_x1152_y2880.png"],
        },
        geometry=[Point(1, 2)],
        crs="EPSG:32635",
    )

    mod.assign_eval_frame_tiles(frame)

    assert seen == ["K-35-042-3_x1152_y2880.png"]


def test_assign_eval_frame_tiles_handles_an_empty_frame() -> None:
    """An operating point that retains nothing must not raise here."""
    from scripts import gemini37_image_55map_r2 as mod

    empty = gpd.GeoDataFrame(
        {"vote_count": [], "mound_probability": [], "source_tile": []},
        geometry=[],
        crs="EPSG:32635",
    )

    out = mod.assign_eval_frame_tiles(empty)

    assert len(out) == 0
    assert "origin_source_tile" in out.columns


# ---------------------------------------------------------------------------
# The campaign table (S155): one script, two pools of the image 2x2.
# ---------------------------------------------------------------------------


@pytest.fixture
def g37_restored():
    """Whatever a test selects, the module is left on the default pool."""
    from scripts import gemini37_image_55map_r2 as mod

    yield mod
    mod.select_campaign("g37")


def test_k5_carried_points_are_the_registered_gs_k5_cells(g37_restored) -> None:
    """K = 5 carries the GS K = 5 cells' points, NOT K = 3's: arm 2 moves from
    0.88 to 0.90 and both arms select unanimity of five."""
    mod = g37_restored
    assert mod.carried_point("arm1", 5) == (0.10, 5)
    assert mod.carried_point("arm2", 5) == (0.90, 5)
    assert mod.carried_point("arm2", 3) == (0.88, 3)
    assert mod.carried_point("arm2", 1) == (0.88, 1)


def test_with_carried_forces_the_k5_point(frame: gpd.GeoDataFrame, g37_restored) -> None:
    mod = g37_restored
    grid = mod.achievable_points(frame, 5)
    assert (0.90, 5) not in grid
    assert (0.90, 5) in mod.with_carried(grid, "arm2", 5)


def test_the_gemini3_campaign_carries_its_calibration_leg(g37_restored) -> None:
    """The Gemini 3 row's points are the 2026-09-18 GS calibration leg's
    image_best values; a K = 1 rung collapses votes to 1 as on the 3.7 row."""
    mod = g37_restored
    camp = mod.select_campaign("g3")
    assert mod.rung_label("arm1", 5) == "G3IMG-ARM1-K5"
    assert mod.RESULTS_HOME.name == "gemini3-image-55map-2026-09-16"
    assert mod.carried_point("arm1", 1) == (0.15, 1)
    assert mod.carried_point("arm1", 3) == (0.15, 3)
    assert mod.carried_point("arm1", 5) == (0.15, 5)
    assert mod.carried_point("arm2", 3) == (0.88, 3)
    assert mod.carried_point("arm2", 5) == (0.95, 5)
    assert mod.CARRIED == {"arm1": 0.15, "arm2": 0.88}
    for arm, path in camp.calibration_files.items():
        best = json.loads(Path(path).read_text())["image_best"]
        assert (best["prob_t"], best["min_votes"]) == mod.carried_point(arm, 3)
        assert best["n_detections"] == camp.gs_calibration[arm]["n"]
    mod.select_campaign("g37")
    assert mod.rung_label("arm1", 5) == "IMG-ARM1-K5"
    assert mod.CARRIED == {"arm1": 0.10, "arm2": 0.88}


def test_an_uncalibrated_campaign_refuses_to_sweep(g37_restored) -> None:
    """A campaign without carried points must refuse: a sweep at made-up
    points would look exactly like a real one."""
    mod = g37_restored
    blank = mod.Campaign(key="blank", prefix="X", root=mod.PROJECT_ROOT,
                         cell="c", results_home=mod.PROJECT_ROOT, rungs=(1,),
                         carried=None, gs_verifier=mod.PROJECT_ROOT,
                         gs_calibration=None)
    mod.CAMPAIGNS["blank"] = blank
    try:
        mod.select_campaign("blank")
        with pytest.raises(RuntimeError, match="not fixed"):
            mod.carried_point("arm1", 1)
    finally:
        del mod.CAMPAIGNS["blank"]
        mod.select_campaign("g37")


def test_g37_calibration_files_match_the_table(g37_restored) -> None:
    mod = g37_restored
    for arm, path in mod.G37.calibration_files.items():
        best = json.loads(Path(path).read_text())["image_best"]
        assert (best["prob_t"], best["min_votes"]) == mod.carried_point(arm, 3)
        assert best["n_detections"] == mod.G37.gs_calibration[arm]["n"]


def test_rung_filter_rejects_a_rung_the_campaign_does_not_carry(g37_restored) -> None:
    mod = g37_restored
    assert mod.parse_rungs(None) == (1, 3, 5)
    assert mod.parse_rungs("5") == (5,)
    assert mod.parse_rungs("1,3") == (1, 3)
    with pytest.raises(SystemExit):
        mod.parse_rungs("10")


# ---------------------------------------------------------------------------
# The MCC oracle, redefined 2026-09-20 (PI ruling): the tile-MCC optimum over
# prob_t at the rung's CARRIED vote count, not over the whole grid.
# ---------------------------------------------------------------------------


def _mcc_row(prob_t: float, votes: int, mcc: float | None,
             f1: float = 0.8) -> dict:
    """One sweep row, reduced to the keys the two selectors consult."""
    return {"prob_t": prob_t, "min_votes": votes, "tile_mcc": mcc,
            "micro_f1_50": f1}


def test_the_mcc_oracle_ignores_every_vote_count_but_the_carried_one() -> None:
    """The Gemini 3 pattern: the free optimum runs to a single vote.

    ``G3IMG-ARM2-K3``'s unconstrained optimum sat at (0.98, k1) with
    micro-F1 0.5772 against the carried-k choice's 0.8263 — the collapse
    the ruling removed.
    """
    from scripts import gemini37_image_55map_r2 as mod

    rows = [_mcc_row(0.98, 1, 0.7706, 0.5772), _mcc_row(0.30, 1, 0.74, 0.62),
            _mcc_row(0.96, 3, 0.7553, 0.8263), _mcc_row(0.30, 3, 0.73, 0.80)]
    assert mod.mcc_argmax_unconstrained(rows) == rows[0]
    assert mod.mcc_argmax_at_carried_k(rows, 3) == rows[2]


def test_the_two_selectors_share_the_boards_tie_break() -> None:
    """Lowest operating point wins a tie, as ``final_board_sweeps`` does."""
    from scripts import gemini37_image_55map_r2 as mod

    rows = [_mcc_row(0.90, 3, 0.70), _mcc_row(0.20, 3, 0.70),
            _mcc_row(0.50, 3, 0.70)]
    assert mod.mcc_argmax_unconstrained(rows)["prob_t"] == 0.20
    assert mod.mcc_argmax_at_carried_k(rows, 3)["prob_t"] == 0.20


def test_a_k1_rung_selects_the_same_point_either_way() -> None:
    """Every K = 1 rung carries k = 1, so the redefinition is a no-op there."""
    from scripts import gemini37_image_55map_r2 as mod

    rows = [_mcc_row(0.15, 1, 0.7523), _mcc_row(0.40, 1, 0.7401)]
    assert mod.mcc_argmax_at_carried_k(rows, 1) == mod.mcc_argmax_unconstrained(rows)


def test_the_selectors_return_none_when_no_row_is_scored() -> None:
    from scripts import gemini37_image_55map_r2 as mod

    assert mod.mcc_argmax_unconstrained([_mcc_row(0.1, 1, None)]) is None
    assert mod.mcc_argmax_at_carried_k([_mcc_row(0.1, 1, 0.7)], 3) is None
