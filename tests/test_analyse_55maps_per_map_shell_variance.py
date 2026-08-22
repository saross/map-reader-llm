"""
Tier 1 tests for ``scripts.analyse_55maps_per_map_shell_variance``.

These tests exercise the script's pure helpers against deterministic
synthetic inputs. They do NOT load the full 55-map review CSVs, write
outputs, or run the bootstrap on real data. They verify that:

1. ``per_map_shell_rates`` correctly bins detections into the
   half-open (50, 75] m shell using a KDTree against a reference set.
2. Maps absent from the candidate frame are still listed in the
   per-map output with ``n_detections = 0`` and a NaN rate.
3. ``bootstrap_4map_sample`` produces a detection-weighted mean
   (i.e. weights by total detections per sample, not by per-map
   rate) and is reproducible under a seeded RNG.
4. ``summarise_distribution`` handles all-NaN and single-value
   distributions without crashing.

Run with:

    pytest tests/test_analyse_55maps_per_map_shell_variance.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.spatial import cKDTree

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# pylint: disable=wrong-import-position
from scripts.analyse_55maps_per_map_shell_variance import (  # noqa: E402
    SHELL_INNER_M,
    SHELL_OUTER_M,
    bootstrap_4map_sample,
    per_map_shell_rates,
    summarise_distribution,
)

pytestmark = pytest.mark.tier1


# =========================================================================
# 1. per_map_shell_rates — KDTree binning into (50, 75]
# =========================================================================


def _build_simple_reference() -> cKDTree:
    """Single reference point at the origin."""
    return cKDTree(np.array([[0.0, 0.0]]))


def test_per_map_shell_rates_in_shell_bin() -> None:
    """A detection at 60 m falls in the (50, 75] shell."""
    cands = pd.DataFrame(
        {
            "x": [60.0],
            "y": [0.0],
            "map_name": ["map_A"],
        }
    )
    tree = _build_simple_reference()
    out = per_map_shell_rates(cands, tree, ["map_A"])
    row = out.iloc[0]
    assert row["map_name"] == "map_A"
    assert row["n_detections"] == 1
    assert row["n_in_shell"] == 1
    assert row["shell_rate"] == pytest.approx(1.0)


def test_per_map_shell_rates_below_shell() -> None:
    """A detection at 40 m (< 50) falls below the (50, 75] shell."""
    cands = pd.DataFrame(
        {
            "x": [40.0],
            "y": [0.0],
            "map_name": ["map_A"],
        }
    )
    tree = _build_simple_reference()
    out = per_map_shell_rates(cands, tree, ["map_A"])
    row = out.iloc[0]
    assert row["n_detections"] == 1
    assert row["n_in_shell"] == 0
    assert row["shell_rate"] == pytest.approx(0.0)


def test_per_map_shell_rates_above_shell() -> None:
    """A detection at 100 m (> 75) falls above the (50, 75] shell."""
    cands = pd.DataFrame(
        {
            "x": [100.0],
            "y": [0.0],
            "map_name": ["map_A"],
        }
    )
    tree = _build_simple_reference()
    out = per_map_shell_rates(cands, tree, ["map_A"])
    row = out.iloc[0]
    assert row["n_detections"] == 1
    assert row["n_in_shell"] == 0
    assert row["shell_rate"] == pytest.approx(0.0)


def test_per_map_shell_rates_half_open_lower_edge() -> None:
    """A detection exactly at 50 m falls just BELOW (50, 75] (half-open)."""
    cands = pd.DataFrame(
        {
            "x": [50.0],
            "y": [0.0],
            "map_name": ["map_A"],
        }
    )
    tree = _build_simple_reference()
    out = per_map_shell_rates(cands, tree, ["map_A"])
    row = out.iloc[0]
    assert row["n_in_shell"] == 0  # 50.0 fails (d > 50) test


def test_per_map_shell_rates_half_open_upper_edge() -> None:
    """A detection exactly at 75 m falls INSIDE (50, 75] (half-open)."""
    cands = pd.DataFrame(
        {
            "x": [75.0],
            "y": [0.0],
            "map_name": ["map_A"],
        }
    )
    tree = _build_simple_reference()
    out = per_map_shell_rates(cands, tree, ["map_A"])
    row = out.iloc[0]
    assert row["n_in_shell"] == 1


def test_per_map_shell_rates_two_maps() -> None:
    """Two maps with different rates — verify per-map grouping."""
    cands = pd.DataFrame(
        {
            "x": [60.0, 40.0, 70.0, 100.0],
            "y": [0.0, 0.0, 0.0, 0.0],
            "map_name": ["map_A", "map_A", "map_B", "map_B"],
        }
    )
    tree = _build_simple_reference()
    out = per_map_shell_rates(cands, tree, ["map_A", "map_B"]).set_index("map_name")
    # map_A: 1 of 2 in shell; map_B: 1 of 2 in shell
    assert out.loc["map_A", "shell_rate"] == pytest.approx(0.5)
    assert out.loc["map_B", "shell_rate"] == pytest.approx(0.5)


def test_per_map_shell_rates_absent_map_kept_with_zero_count() -> None:
    """A map in the universe but with no candidates → n=0, rate=NaN."""
    cands = pd.DataFrame(
        {
            "x": [60.0],
            "y": [0.0],
            "map_name": ["map_A"],
        }
    )
    tree = _build_simple_reference()
    out = per_map_shell_rates(
        cands, tree, ["map_A", "map_B"]
    ).set_index("map_name")
    assert out.loc["map_B", "n_detections"] == 0
    assert out.loc["map_B", "n_in_shell"] == 0
    assert pd.isna(out.loc["map_B", "shell_rate"])


# =========================================================================
# 2. bootstrap_4map_sample — detection-weighted, reproducible
# =========================================================================


def test_bootstrap_detection_weighted_not_unweighted() -> None:
    """
    With one map carrying all the in-shell detections and a disparate
    detection count, the weighted mean across a 2-map sample including
    that map equals (in_total / det_total), not (rate_A + rate_B) / 2.
    """
    pm = pd.DataFrame(
        {
            "map_name": ["A", "B"],
            "n_detections": [100, 1],
            "n_in_shell": [50, 1],
            "shell_rate": [0.5, 1.0],
        }
    )
    rng = np.random.default_rng(42)
    out = bootstrap_4map_sample(pm, rng, n_iter=1, sample_size=2)
    # Both maps are always sampled (sample_size=2 from 2);
    # weighted mean = 51 / 101
    assert out[0] == pytest.approx(51.0 / 101.0)


def test_bootstrap_reproducible_under_seed() -> None:
    """Same RNG seed → identical bootstrap distribution."""
    pm = pd.DataFrame(
        {
            "map_name": [f"map_{i}" for i in range(10)],
            "n_detections": [10, 20, 5, 30, 15, 8, 12, 18, 25, 9],
            "n_in_shell": [1, 2, 0, 5, 3, 1, 0, 2, 4, 1],
            "shell_rate": [0.1, 0.1, 0.0, 1 / 6, 0.2, 0.125, 0, 1 / 9, 4 / 25, 1 / 9],
        }
    )
    rng_a = np.random.default_rng(2026)
    rng_b = np.random.default_rng(2026)
    out_a = bootstrap_4map_sample(pm, rng_a, n_iter=100, sample_size=4)
    out_b = bootstrap_4map_sample(pm, rng_b, n_iter=100, sample_size=4)
    assert np.array_equal(out_a, out_b)


def test_bootstrap_zero_detection_sample_returns_nan() -> None:
    """If all sampled maps have 0 detections, weighted mean is NaN."""
    pm = pd.DataFrame(
        {
            "map_name": ["A", "B"],
            "n_detections": [0, 0],
            "n_in_shell": [0, 0],
            "shell_rate": [np.nan, np.nan],
        }
    )
    rng = np.random.default_rng(0)
    out = bootstrap_4map_sample(pm, rng, n_iter=5, sample_size=2)
    assert np.all(np.isnan(out))


# =========================================================================
# 3. summarise_distribution edge cases
# =========================================================================


def test_summarise_distribution_basic() -> None:
    """Smoke test on a small distribution."""
    out = summarise_distribution(np.array([0.0, 0.5, 1.0]))
    assert out["n"] == 3
    assert out["mean"] == pytest.approx(0.5)
    assert out["median"] == pytest.approx(0.5)
    assert out["min"] == 0.0
    assert out["max"] == 1.0


def test_summarise_distribution_skips_nan() -> None:
    """NaN entries are dropped; stats reflect the remaining values."""
    out = summarise_distribution(np.array([0.1, np.nan, 0.3, np.nan]))
    assert out["n"] == 2
    assert out["mean"] == pytest.approx(0.2)


def test_summarise_distribution_all_nan_returns_nones() -> None:
    """All-NaN input returns a structured {n:0, ...None} dict."""
    out = summarise_distribution(np.array([np.nan, np.nan]))
    assert out["n"] == 0
    assert out["mean"] is None
    assert out["sd"] is None


# =========================================================================
# 4. Module-level constants documentation
# =========================================================================


def test_shell_constants_match_obs296_spec() -> None:
    """Shell is (50, 75] m as documented in Obs 296 / task spec."""
    assert SHELL_INNER_M == 50
    assert SHELL_OUTER_M == 75
