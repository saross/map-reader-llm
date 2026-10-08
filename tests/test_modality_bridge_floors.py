"""
Tests for ``scripts/modality_bridge_floors.py`` — Run B's items 4, 6 and 7.

The script's heavy steps (subset rungs, scoring) are gated against committed
results when it runs; these tests pin the pure functions those steps rest on:
the vote path, the finite-population-corrected SD and its jackknife, the
K-scaling fits and § 6b's carry-to-K = N rules, the floor arithmetic, the
same-tile flip counts, the interaction arm order, and candidate inheritance.
All synthetic; nothing is read from disk.
"""

from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_permutation import paired_interaction_permutation  # noqa: E402
from scripts.modality_bridge_floors import (  # noqa: E402
    FIT_KMAX,
    VERIFIER_BAND,
    Z,
    contrast_floor,
    disjoint_pairs,
    fit_extrapolate,
    fpc_sd,
    full_rung_sd,
    inherit_index,
    interaction_arms,
    jackknife_se,
    k_path,
    s3_floor_as_sd,
    tile_flips,
)
from scripts.n1_baseline_leaderboard_tiering import micro_f1  # noqa: E402

pytestmark = pytest.mark.tier1


# --------------------------------------------------------------------------- #
# Vote path.
# --------------------------------------------------------------------------- #


def test_k_path_rounds_half_up_and_never_below_one():
    """k9 of 10 maps to k5 at five passes (4.5 rounds up) and k1 at one."""
    assert [k_path(0.9, n) for n in range(1, 11)] == [1, 2, 3, 4, 5, 5, 6, 7, 8, 9]
    assert [k_path(1.0, n) for n in (1, 5, 10)] == [1, 5, 10]
    assert k_path(0.01, 3) == 1


# --------------------------------------------------------------------------- #
# The finite-population-corrected SD and its jackknife.
# --------------------------------------------------------------------------- #


def test_fpc_sd_is_exact_for_a_mean_over_passes():
    """For a K-pass mean the estimator equals sqrt(s² / K), s² the unbiased pass variance."""
    rng = np.random.default_rng(0)
    x = rng.normal(0.8, 0.02, size=10)
    for k in (1, 3, 5, 9):
        subs = list(itertools.combinations(range(10), k))
        vals = [x[list(s)].mean() for s in subs]
        assert fpc_sd(vals, 10, k) == pytest.approx(math.sqrt(np.var(x, ddof=1) / k))


def test_fpc_sd_refuses_k_at_or_above_n():
    """K = N has no subset spread; the estimator is undefined there."""
    with pytest.raises(ValueError):
        fpc_sd([0.5], 5, 5)


def test_jackknife_se_nan_without_replicates_and_zero_on_constant_values():
    """No replicate exists when N − 1 <= K; constant values have no spread to resample."""
    subs = list(itertools.combinations(range(5), 4))
    assert math.isnan(jackknife_se(subs, [0.9] * len(subs), 5, 4))
    subs3 = list(itertools.combinations(range(5), 3))
    assert jackknife_se(subs3, [0.9] * len(subs3), 5, 3) == pytest.approx(0.0)


def test_jackknife_se_positive_on_varied_values():
    """A pass that moves the statistic gives the jackknife something to see."""
    x = np.array([0.80, 0.81, 0.79, 0.85, 0.80, 0.78])
    subs = list(itertools.combinations(range(6), 2))
    vals = [x[list(s)].mean() for s in subs]
    assert jackknife_se(subs, vals, 6, 2) > 0


def test_disjoint_pairs():
    """Only subsets sharing no pass are paired, each pair once."""
    subs = [(0, 1), (2, 3), (1, 2), (3, 4)]
    assert disjoint_pairs(subs) == [(0, 1), (0, 3), (2, 3)]
    assert len(disjoint_pairs(list(itertools.combinations(range(10), 5)))) == 126


# --------------------------------------------------------------------------- #
# Fits and § 6b's carry to K = N.
# --------------------------------------------------------------------------- #


def test_fit_extrapolate_recovers_exact_power_law_and_hyperbola():
    """Noise-free data are read back exactly by the matching fit."""
    ks = [1, 2, 3, 4, 5]
    power = fit_extrapolate(ks, [0.004 * k ** -0.25 for k in ks], 10)
    assert power["power"] == pytest.approx(0.004 * 10 ** -0.25)
    assert power["power_exp"] == pytest.approx(-0.25)
    hyper = fit_extrapolate(ks, [0.002 + 0.003 / k for k in ks], 10)
    assert hyper["hyper"] == pytest.approx(0.002 + 0.0003)


def test_fit_extrapolate_power_undefined_on_a_zero_sd():
    """A zero SD has no logarithm; the hyperbola still fits."""
    fit = fit_extrapolate([1, 2, 3], [0.0, 0.002, 0.003], 5)
    assert math.isnan(fit["power"])
    assert math.isfinite(fit["hyper"])


def test_full_rung_sd_ten_passes_takes_the_largest_of_fits_and_flat():
    """Ten passes: max(power, hyperbola, SD at K' = 5); upper adds the fits' jackknife."""
    sd_by_k = {k: 0.003 for k in range(1, 10)}
    sd_by_k[FIT_KMAX] = 0.0031
    fit = {"power": 0.0025, "hyper": 0.0028}
    out = full_rung_sd(10, sd_by_k, {}, fit, {"power": 0.0005, "hyper": 0.0001})
    assert out["sd"] == pytest.approx(0.0031)
    assert out["sd_upper"] == pytest.approx(max(0.0031, 0.0025 + Z * 0.0005, 0.0028 + Z * 0.0001))


def test_full_rung_sd_five_passes_uses_direct_three_and_four():
    """Five passes: max(fits, SD at K' = 3, SD at K' = 4); upper adds K' = 3's jackknife."""
    sd_by_k = {1: 0.002, 2: 0.002, 3: 0.0035, 4: 0.003}
    fit = {"power": 0.0021, "hyper": float("nan")}
    out = full_rung_sd(5, sd_by_k, {3: 0.001, 4: float("nan")}, fit, {})
    assert out["sd"] == pytest.approx(0.0035)
    assert out["sd_upper"] == pytest.approx(0.0035 + Z * 0.001)


# --------------------------------------------------------------------------- #
# Floors.
# --------------------------------------------------------------------------- #


def test_contrast_floor_adds_the_band_once_per_contrast():
    """Two cells and one band; four cells and two bands."""
    assert contrast_floor([0.003, 0.004], 1) == pytest.approx(Z * 0.005 + VERIFIER_BAND)
    four = contrast_floor([0.002] * 4, 2)
    assert four == pytest.approx(Z * 0.004 + 2 * VERIFIER_BAND)


def test_s3_floor_round_trips_through_a_pairwise_contrast():
    """A pairwise floor, read as a per-cell SD, gives itself back for two cells."""
    floor = 0.0253
    sd = s3_floor_as_sd(floor)
    assert contrast_floor([sd, sd], 1, band=0.0) == pytest.approx(floor)


# --------------------------------------------------------------------------- #
# Same-tile flips.
# --------------------------------------------------------------------------- #


def test_tile_flips_counts_discordance_and_direction():
    """Tile 0 fixed, tile 1 broken, tile 2 changed but still in error, tile 3 unchanged."""
    a = {"tp": np.array([1., 1., 0., 2.]), "fp": np.array([1., 0., 1., 0.]),
         "fn": np.array([0., 0., 0., 0.])}
    b = {"tp": np.array([1., 0., 0., 2.]), "fp": np.array([0., 0., 2., 0.]),
         "fn": np.array([0., 1., 0., 0.])}
    out = tile_flips(a, b)
    assert out["n_tiles"] == 4
    assert out["discordant"] == 3
    assert out["discordant_rate"] == pytest.approx(0.75)
    assert (out["fixed"], out["broken"]) == (1, 1)
    assert out["error_flip_rate"] == pytest.approx(0.5)
    assert (out["d_tp"], out["d_fp"], out["d_fn"]) == (-1.0, 0.0, 1.0)


def test_tile_flips_identical_outputs():
    """Identical outputs flip nothing."""
    a = {"tp": np.ones(3), "fp": np.zeros(3), "fn": np.ones(3)}
    out = tile_flips(a, {k: v.copy() for k, v in a.items()})
    assert out["discordant"] == 0 and out["error_flip_rate"] == 0.0


# --------------------------------------------------------------------------- #
# The interaction's arm order.
# --------------------------------------------------------------------------- #


def _counts(rng: np.random.Generator, n: int, p_fp: float) -> dict[str, np.ndarray]:
    """Synthetic per-tile counts."""
    return {"tp": rng.integers(0, 3, n).astype(float),
            "fp": rng.binomial(1, p_fp, n).astype(float),
            "fn": rng.binomial(1, 0.2, n).astype(float)}


def _f1(c: dict[str, np.ndarray]) -> float:
    return micro_f1(c["tp"].sum(), c["fp"].sum(), c["fn"].sum())


def test_interaction_arms_order_and_statistic():
    """Both arrangements give (T37 − I37) − (T3 − I3); the order is as documented."""
    assert interaction_arms(1, 2, 3, 4) == (1, 2, 3, 4)
    assert interaction_arms(1, 2, 3, 4, swap="family") == (1, 3, 2, 4)
    with pytest.raises(ValueError):
        interaction_arms(1, 2, 3, 4, swap="tile")
    rng = np.random.default_rng(1)
    t37, i37, t3, i3 = (_counts(rng, 60, p) for p in (0.1, 0.1, 0.1, 0.4))
    expected = (_f1(t37) - _f1(i37)) - (_f1(t3) - _f1(i3))
    for swap in ("modality", "family"):
        res = paired_interaction_permutation(*interaction_arms(t37, t3, i37, i3, swap=swap),
                                             n_permutations=200)
        assert res["observed"] == pytest.approx(expected)


def test_modality_swap_is_inert_when_text_equals_image_in_both_families():
    """Swapping text with image changes nothing when they are identical: p = 1."""
    rng = np.random.default_rng(2)
    fam37, fam3 = _counts(rng, 40, 0.1), _counts(rng, 40, 0.3)
    res = paired_interaction_permutation(*interaction_arms(fam37, fam3, fam37, fam3),
                                         n_permutations=200)
    assert res["observed"] == 0.0
    assert res["null_std"] == 0.0
    assert res["p_value"] == 1.0


# --------------------------------------------------------------------------- #
# Inheritance.
# --------------------------------------------------------------------------- #


def test_inherit_index_nearest_within_tolerance():
    """Each cluster takes its nearest union candidate; beyond 10 m it is unmatched."""
    union = np.array([[0.0, 0.0], [100.0, 0.0]])
    rung = np.array([[3.0, 4.0], [100.0, 9.0], [50.0, 0.0]])
    d, idx, matched = inherit_index(rung, union)
    assert idx.tolist() == [0, 1, 0]
    assert d[:2].tolist() == pytest.approx([5.0, 9.0])
    assert matched.tolist() == [True, True, False]


def test_inherit_index_empty_rung():
    """An empty rung inherits nothing."""
    d, idx, matched = inherit_index(np.zeros((0, 2)), np.array([[0.0, 0.0]]))
    assert len(d) == len(idx) == len(matched) == 0
