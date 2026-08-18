"""Tier-1 tests for the H13 overlap-arm scoring chain.

Covers the pure computational core of ``scripts/h13_overlap_analysis.py``
and ``scripts/prepare_h13_scoring.py``: micro-F1, the paired tile
bootstrap (determinism, pairing, p-value floor, behaviour on separable
and null synthetic contrasts), and the geometry helpers that decide
which scoring tile a detection is booked to. The live stages — loading
nine committed passes, generating bounds from tile metadata, and the
evaluator hand-off — are exercised by ``scripts/verify_h13_overlap.py``
against the real artefacts, not simulated here.
"""

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.h13_overlap_analysis import micro_f1, paired_bootstrap  # noqa: E402
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402

CRS = "EPSG:32635"


def _counts(tp, fp, fn):
    """Build the per-tile count dict the bootstrap consumes.

    Args:
        tp: True-positive array. fp: False-positive array. fn: False-negative array.

    Returns:
        Dict of float NumPy arrays keyed ``tp``/``fp``/``fn``.
    """
    return {
        "tp": np.asarray(tp, dtype=float),
        "fp": np.asarray(fp, dtype=float),
        "fn": np.asarray(fn, dtype=float),
    }


@pytest.mark.tier1
def test_micro_f1_known_values():
    """Micro-F1 matches hand-computed values and guards zero division."""
    assert micro_f1(0, 0, 0) == (0.0, 0.0, 0.0)
    assert micro_f1(10, 0, 0) == (1.0, 1.0, 1.0)
    p, r, f = micro_f1(10, 5, 2)
    assert abs(p - 10 / 15) < 1e-12
    assert abs(r - 10 / 12) < 1e-12
    # F1 = 2TP / (2TP + FP + FN)
    assert abs(f - 20 / 27) < 1e-12


@pytest.mark.tier1
def test_paired_bootstrap_deterministic():
    """The same seed and inputs give identical results."""
    rng = np.random.default_rng(0)
    a = _counts(rng.integers(0, 5, 60), rng.integers(0, 3, 60), rng.integers(0, 3, 60))
    b = _counts(rng.integers(0, 5, 60), rng.integers(0, 3, 60), rng.integers(0, 3, 60))
    r1 = paired_bootstrap(a, b, 200, seed=42)
    r2 = paired_bootstrap(a, b, 200, seed=42)
    assert r1 == r2


@pytest.mark.tier1
def test_paired_bootstrap_observed_delta_matches_pooled_f1():
    """The reported delta is the pooled micro-F1 difference, not a bootstrap mean."""
    a = _counts([4, 4], [1, 1], [1, 1])
    b = _counts([2, 2], [3, 3], [3, 3])
    res = paired_bootstrap(a, b, 100, seed=1)
    expected = micro_f1(8, 2, 2)[2] - micro_f1(4, 6, 6)[2]
    assert abs(res["delta"] - expected) < 1e-12


@pytest.mark.tier1
def test_paired_bootstrap_identical_arms_give_zero_delta():
    """Pairing is real: an arm resampled against itself has a degenerate null.

    If the two arms were resampled independently the difference would
    fluctuate; because one index draw is applied to both, every iteration
    differences identical numbers and the interval collapses onto zero.
    """
    rng = np.random.default_rng(7)
    a = _counts(rng.integers(0, 6, 80), rng.integers(0, 6, 80), rng.integers(0, 4, 80))
    res = paired_bootstrap(a, a, 300, seed=42)
    assert res["delta"] == 0.0
    assert res["ci_lower"] == 0.0
    assert res["ci_upper"] == 0.0
    assert not res["excludes_zero"]


@pytest.mark.tier1
def test_paired_bootstrap_separable_contrast_excludes_zero():
    """A uniformly better arm yields an interval clear of zero."""
    n = 120
    a = _counts(np.full(n, 5.0), np.full(n, 1.0), np.full(n, 1.0))
    b = _counts(np.full(n, 1.0), np.full(n, 5.0), np.full(n, 5.0))
    res = paired_bootstrap(a, b, 400, seed=42)
    assert res["delta"] > 0
    assert res["ci_lower"] > 0
    assert res["excludes_zero"]


@pytest.mark.tier1
def test_paired_bootstrap_p_value_floor():
    """The two-sided p-value never reports below the 1/B resolution floor."""
    n = 100
    a = _counts(np.full(n, 9.0), np.full(n, 1.0), np.full(n, 1.0))
    b = _counts(np.full(n, 1.0), np.full(n, 9.0), np.full(n, 9.0))
    res = paired_bootstrap(a, b, 250, seed=42)
    assert res["p_two_sided"] == pytest.approx(1 / 250)


@pytest.mark.tier1
def test_assign_primary_tiles_prefers_nearest_centroid():
    """A detection in an overlap zone is booked to the nearest-centroid tile.

    This mirrors the evaluator's reference-assignment rule, so detections
    and references land on the same tile in the per-tile TP/FP/FN table
    that the bootstrap resamples.
    """
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["t_left.png", "t_right.png"]},
        geometry=[box(0, 0, 100, 100), box(80, 0, 180, 100)],
        crs=CRS,
    )
    # x = 85 sits in both tiles but is far nearer t_left's centroid (50, 50)
    # than t_right's (130, 50).
    dets = gpd.GeoDataFrame(geometry=[Point(85, 50)], crs=CRS)
    assert assign_primary_tiles(dets, bounds) == ["t_left.png"]

    dets = gpd.GeoDataFrame(geometry=[Point(95, 50)], crs=CRS)
    assert assign_primary_tiles(dets, bounds) == ["t_right.png"]


@pytest.mark.tier1
def test_assign_primary_tiles_reports_unassigned():
    """A detection outside every tile is reported as unassigned, not dropped."""
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["t.png"]}, geometry=[box(0, 0, 10, 10)], crs=CRS,
    )
    dets = gpd.GeoDataFrame(geometry=[Point(5, 5), Point(500, 500)], crs=CRS)
    assert assign_primary_tiles(dets, bounds) == ["t.png", None]


@pytest.mark.tier1
def test_assign_primary_tiles_empty_input():
    """An empty detection frame yields an empty assignment list."""
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["t.png"]}, geometry=[box(0, 0, 10, 10)], crs=CRS,
    )
    empty = gpd.GeoDataFrame(geometry=[], crs=CRS)
    assert assign_primary_tiles(empty, bounds) == []
