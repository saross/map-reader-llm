"""Tier-1 tests for the empty-tile adjudication rules (card § 5b).

The class order and the exact binomial interval are the two pieces of
logic a reader would otherwise have to trust; both are checked here on
hand-built inputs, without touching the corpus files.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from scripts.empty_tile_adjudicate import (  # noqa: E402
    GT_ERROR_SYMBOL,
    classify,
    clopper_pearson,
    distinct_groups,
    edge_distance_m,
)


@pytest.mark.tier1
def test_edge_distance_is_the_nearest_side():
    """A 1,932 m tile: a point 10 m in from the south edge reports 10 m; the
    centre reports half the side; outside the bounds goes negative."""
    minx, miny, maxx, maxy = 0.0, 0.0, 1932.0, 1932.0
    assert edge_distance_m(500.0, 10.0, minx, miny, maxx, maxy) == pytest.approx(10.0)
    assert edge_distance_m(966.0, 966.0, minx, miny, maxx, maxy) == pytest.approx(966.0)
    assert edge_distance_m(1930.0, 5.0, minx, miny, maxx, maxy) == pytest.approx(2.0)
    assert edge_distance_m(-3.0, 500.0, minx, miny, maxx, maxy) < 0


@pytest.mark.tier1
def test_overlap_strip_duplicates_collapse_to_one_sighting():
    """Two marks of one symbol on adjacent tiles (a few metres apart) are one
    sighting; a mark 300 m away is another; chains link transitively."""
    xy = np.array([[0.0, 0.0], [2.5, 1.0],        # same symbol, two tiles
                   [300.0, 0.0],                  # a different mound
                   [10.0, 0.0], [20.0, 0.0]])     # chain: 0-10-20 links via 10 m steps
    labels = distinct_groups(xy, tol_m=15.0)
    assert labels[0] == labels[1] == labels[3] == labels[4]
    assert labels[2] != labels[0]
    assert len(set(labels)) == 2
    assert distinct_groups(np.empty((0, 2))) == []


@pytest.mark.tier1
def test_gt_error_flag_is_its_own_class_regardless_of_neighbours():
    """A GT-error flag never becomes a double-miss, even with nothing nearby."""
    far = {"gt": (591.0, "gt"), "dep": (340.0, "deployed"), "u": (60.0, "union")}
    assert classify(far, 50.0, GT_ERROR_SYMBOL) == "gt-error-flag"
    assert classify({"gt": (1.4, "gt")}, 50.0, GT_ERROR_SYMBOL) == "gt-error-flag"
    assert classify(far, 50.0, "Hairy brown circle") == "true-double-miss"


@pytest.mark.tier1
def test_class_order_gt_beats_deployed_beats_union():
    """A GT hit wins even when the model also found it; a union hit alone is filtered."""
    r = 50.0
    assert classify({"gt": (12.5, "gt"), "dep": (3.5, "deployed"), "u": (1.0, "union")}, r) \
        == "known-in-GT"
    assert classify({"gt": (591.0, "gt"), "dep": (3.5, "deployed"), "u": (1.0, "union")}, r) \
        == "detected"
    assert classify({"gt": (591.0, "gt"), "dep": (340.0, "deployed"), "u": (20.0, "union")}, r) \
        == "proposed-but-filtered"
    assert classify({"gt": (591.0, "gt"), "dep": (340.0, "deployed"), "u": (60.0, "union")}, r) \
        == "true-double-miss"


@pytest.mark.tier1
def test_radius_is_inclusive_at_the_boundary():
    """Exactly 50 m counts as within the radius (nearest neighbour AT 50 m)."""
    assert classify({"gt": (50.0, "gt")}, 50.0) == "known-in-GT"
    assert classify({"gt": (50.01, "gt")}, 50.0) == "true-double-miss"


@pytest.mark.tier1
def test_clopper_pearson_known_values():
    """Zero successes give a [0, 1-(alpha/2)^(1/n)] interval; a mid case matches tables."""
    lo, hi = clopper_pearson(0, 470)
    assert lo == 0.0
    assert hi == pytest.approx(1 - 0.025 ** (1 / 470), rel=1e-6)
    lo, hi = clopper_pearson(2, 150)
    assert lo == pytest.approx(0.00162, abs=2e-4)
    assert hi == pytest.approx(0.04734, abs=2e-4)
