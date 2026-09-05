"""Tier-1 tests for the empty-tile adjudication rules (card § 5b).

The class order and the exact binomial interval are the two pieces of
logic a reader would otherwise have to trust; both are checked here on
hand-built inputs, without touching the corpus files.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.empty_tile_adjudicate import classify, clopper_pearson  # noqa: E402


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
