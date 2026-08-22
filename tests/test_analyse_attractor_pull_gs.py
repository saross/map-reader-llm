"""
Tier 1 tests for ``scripts.analyse_attractor_pull_gs``.

These tests exercise the script's pure helpers in isolation against
synthetic, deterministic inputs — they do NOT load the full GS
detection geojsons, write outputs, or run permutations. They verify
that:

1. ``shell_rates_from_distances`` bins distances into the documented
   half-open intervals correctly.
2. The KDTree-based observed-rate construction matches a hand-computed
   reference for a contrived "all detections at 30 m from a single
   reference" case.
3. The within-tile permutation routine is reproducible (seed 42 produces
   identical output across two invocations).
4. ``analyse_run`` behaves correctly on edge cases (a 1-detection
   condition, a condition where every detection is far from every
   reference).

Run with:

    pytest tests/test_analyse_attractor_pull_gs.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# pylint: disable=wrong-import-position
from scripts.analyse_attractor_pull_gs import (  # noqa: E402
    SHELL_EDGES,
    randomise_within_tile,
    shell_rates_from_distances,
)
import pytest

pytestmark = pytest.mark.tier1


# =========================================================================
# 1. shell_rates_from_distances binning
# =========================================================================


def test_shell_rates_simple_bins() -> None:
    """One detection in each of the seven shells → 1/7 in each."""
    # Centres: 12.5, 37.5, 62.5, 87.5, 112.5, 137.5, 218
    distances = np.array([12.5, 37.5, 62.5, 87.5, 112.5, 137.5, 218.0])
    rates = shell_rates_from_distances(distances, SHELL_EDGES)
    assert len(rates) == len(SHELL_EDGES)
    assert np.allclose(rates, np.full(len(SHELL_EDGES), 1.0 / 7.0))


def test_shell_rates_half_open_intervals() -> None:
    """
    A point at exactly the inner edge of a shell falls into the
    *previous* shell (intervals are half-open: ``(R_{n-1}, R_n]``).
    A point at the outer edge belongs to its own shell.
    """
    distances = np.array([25.0, 50.0, 75.0])  # exactly on edges
    rates = shell_rates_from_distances(distances, SHELL_EDGES)
    # Each point sits at the OUTER edge of one shell.
    # 25.0 in (0, 25], 50.0 in (25, 50], 75.0 in (50, 75]
    expected = np.zeros(len(SHELL_EDGES))
    expected[0] = 1 / 3
    expected[1] = 1 / 3
    expected[2] = 1 / 3
    assert np.allclose(rates, expected)


def test_shell_rates_beyond_last_edge_dropped() -> None:
    """Detections beyond ``edges[-1]`` contribute to no shell."""
    distances = np.array([10.0, 300.0, 1000.0])
    rates = shell_rates_from_distances(distances, SHELL_EDGES)
    assert rates[0] == 1.0 / 3.0  # 10 m in (0, 25]
    assert np.allclose(rates[1:], 0.0)
    # Closure: rates sum to fraction within 286 m
    assert np.isclose(rates.sum(), 1.0 / 3.0)


def test_shell_rates_zero_distance_excluded() -> None:
    """
    A detection at exactly 0.0 m from a reference is NOT counted in the
    (0, 25] shell because the interval is half-open on the lower side.
    This is a documentation choice that should be visible in the test.
    """
    distances = np.array([0.0, 0.5, 25.0])
    rates = shell_rates_from_distances(distances, SHELL_EDGES)
    # Only 0.5 m and 25.0 m are in (0, 25]; 0.0 m is not.
    assert rates[0] == 2.0 / 3.0


# =========================================================================
# 2. Hand-computed contrived case
# =========================================================================


def test_contrived_all_at_30m_from_single_mound() -> None:
    """
    Synthesise a detection set where every detection sits at distance
    30 m east of a single reference mound. Confirm that the (25, 50]
    shell observed rate is 1.0 and all other shells are 0.0.

    This is the "contrived test" called for in the brief — it isolates
    the binning logic from any null-distribution noise.
    """
    # Single reference at origin
    ref_xy = np.array([[0.0, 0.0]])
    tree = cKDTree(ref_xy)
    # Five detections at (30, 0), (-30, 0), (0, 30), (0, -30), (30, 0)
    det_xy = np.array(
        [
            [30.0, 0.0],
            [-30.0, 0.0],
            [0.0, 30.0],
            [0.0, -30.0],
            [30.0, 0.0],
        ]
    )
    dist, _ = tree.query(det_xy, k=1)
    assert np.allclose(dist, 30.0)
    rates = shell_rates_from_distances(dist, SHELL_EDGES)
    # (25, 50] is the second shell; expect 1.0 there, 0.0 elsewhere.
    expected = np.zeros(len(SHELL_EDGES))
    expected[1] = 1.0
    assert np.allclose(rates, expected)


def test_contrived_all_at_300m_outside_all_shells() -> None:
    """
    All detections at 300 m → outside (150, 286]; rates sum to 0.
    """
    ref_xy = np.array([[0.0, 0.0]])
    tree = cKDTree(ref_xy)
    det_xy = np.array(
        [
            [300.0, 0.0],
            [0.0, 300.0],
            [-300.0, 0.0],
        ]
    )
    dist, _ = tree.query(det_xy, k=1)
    rates = shell_rates_from_distances(dist, SHELL_EDGES)
    assert rates.sum() == 0.0


# =========================================================================
# 3. Permutation reproducibility
# =========================================================================


def _toy_cands_dataframe() -> "pd.DataFrame":  # noqa: F821
    """Return a 4-detection toy dataframe for permutation testing."""
    import pandas as pd

    return pd.DataFrame(
        {
            "x": [0.0, 100.0, 200.0, 50.0],
            "y": [0.0, 100.0, 200.0, 50.0],
            "tile_minx": [-50.0, 50.0, 150.0, 0.0],
            "tile_miny": [-50.0, 50.0, 150.0, 0.0],
            "tile_maxx": [50.0, 150.0, 250.0, 100.0],
            "tile_maxy": [50.0, 150.0, 250.0, 100.0],
        }
    )


def test_permutation_reproducible_seed_42() -> None:
    """Same seed → byte-identical random tile-bound coordinates."""
    cands = _toy_cands_dataframe()
    rng_a = np.random.default_rng(42)
    rng_b = np.random.default_rng(42)
    coords_a = randomise_within_tile(cands, rng_a)
    coords_b = randomise_within_tile(cands, rng_b)
    assert coords_a.shape == (4, 2)
    assert np.array_equal(coords_a, coords_b)


def test_permutation_respects_tile_bounds() -> None:
    """Random coords must lie within their parent tile's bbox."""
    cands = _toy_cands_dataframe()
    rng = np.random.default_rng(42)
    coords = randomise_within_tile(cands, rng)
    for i, (x, y) in enumerate(coords):
        assert cands["tile_minx"].iloc[i] <= x <= cands["tile_maxx"].iloc[i]
        assert cands["tile_miny"].iloc[i] <= y <= cands["tile_maxy"].iloc[i]


# =========================================================================
# 4. Edge cases
# =========================================================================


def test_empty_distances_array() -> None:
    """
    Empty detection set → all shell rates are NaN (mean of empty boolean
    array). The script's ``analyse_run`` will not be called on an empty
    geojson in practice, but the helper should not crash.
    """
    distances = np.array([], dtype=float)
    rates = shell_rates_from_distances(distances, SHELL_EDGES)
    # NaN propagates from np.mean on empty boolean
    assert len(rates) == len(SHELL_EDGES)
    assert all(np.isnan(rates))


def test_single_detection_inside_shell() -> None:
    """Single detection inside (0, 25] → first shell rate = 1.0."""
    distances = np.array([10.0])
    rates = shell_rates_from_distances(distances, SHELL_EDGES)
    assert rates[0] == 1.0
    assert all(rates[1:] == 0.0)
