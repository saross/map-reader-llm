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

import geopandas as gpd
import pytest
from shapely.geometry import Point

from scripts.gemini37_image_55map_r2 import (
    CARRIED,
    achievable_points,
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
