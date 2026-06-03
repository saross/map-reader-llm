"""
Tier 1 tests for ``scripts.n1_baseline_leaderboard_tiering`` — the
round-robin permutation + Benjamini-Hochberg FDR + greedy-clique tiering
that produces the ``n1-baseline-matrix-384`` leaderboard ``tie_set``.

These pin the three pure-logic pieces that carry the statistical
conclusion, so a regression in any of them would be caught:

1. ``micro_f1`` — must stay byte-identical to the canonical
   ``pairwise_permutation_test._compute_f1`` on integer counts (the float
   extension is the only intended difference), including the documented
   edge cases (``tp == 0`` and zero-denominator -> 0.0).
2. ``permutation_test_float`` — the float tile-swap permutation must be
   deterministic for a fixed seed, antisymmetric in its observed
   difference, return p == 1.0 for identical conditions, and a small p
   for a cleanly separated pair. The swap operating on float (pass-mean)
   per-tile counts is the one bespoke deviation from the canonical
   integer test, so it is pinned directly.
3. ``greedy_clique_tiers`` — the tie_set is ``tiers[0]``; the clique
   algorithm (mirroring ``build_tiered_leaderboard.apply_fdr_and_tier``)
   must collapse an all-indistinguishable set to one tier, split an
   all-significant set into singletons, and recover a known leader clique.

All tests use synthetic in-memory data — no network or filesystem I/O.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    greedy_clique_tiers,
    micro_f1,
    permutation_test_float,
)
from scripts.pairwise_permutation_test import _compute_f1  # noqa: E402


# --------------------------------------------------------------------------- #
# 1. micro_f1 — parity with the canonical _compute_f1 + edge cases
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
@pytest.mark.parametrize(
    "tp, fp, fn",
    [
        (0, 0, 0),  # tp == 0 -> 0.0
        (0, 5, 5),  # tp == 0 with activity -> 0.0
        (10, 0, 0),  # perfect -> 1.0
        (5, 5, 5),  # balanced
        (179, 12, 50),  # the real pro-text-medium-t-0-0 confusion block
        (228, 257, 1),  # an over-detector (flash-text-minimal)
        (1, 0, 9),  # precision 1, low recall
    ],
)
def test_micro_f1_matches_canonical_on_integers(tp: int, fp: int, fn: int) -> None:
    """micro_f1 must equal the canonical _compute_f1 on integer counts."""
    assert micro_f1(tp, fp, fn) == pytest.approx(_compute_f1(tp, fp, fn))


@pytest.mark.tier1
def test_micro_f1_edge_cases() -> None:
    """tp == 0 and zero-denominator inputs both return 0.0."""
    assert micro_f1(0, 0, 0) == 0.0
    assert micro_f1(0, 10, 10) == 0.0
    assert micro_f1(10, 0, 0) == 1.0


@pytest.mark.tier1
def test_micro_f1_accepts_float_means() -> None:
    """Float (pass-averaged) counts are handled; F1-of-mean is well defined."""
    # Two passes with tp = {0, 1}, fp = {0, 0}, fn = {1, 0} -> means 0.5/0/0.5.
    val = micro_f1(0.5, 0.0, 0.5)
    # precision = 0.5/0.5 = 1.0, recall = 0.5/1.0 = 0.5 -> F1 = 2/3.
    assert val == pytest.approx(2 / 3)


# --------------------------------------------------------------------------- #
# 2. permutation_test_float — determinism, antisymmetry, edge behaviour
# --------------------------------------------------------------------------- #


def _two_conditions() -> tuple[np.ndarray, ...]:
    """Return a small synthetic pair of per-tile (float) count arrays."""
    tp_a = np.array([2.0, 3.0, 0.0, 1.0, 4.0])
    fp_a = np.array([0.0, 1.0, 0.0, 0.0, 1.0])
    fn_a = np.array([1.0, 0.0, 2.0, 0.0, 0.0])
    tp_b = np.array([0.0, 1.0, 0.0, 1.0, 1.0])
    fp_b = np.array([3.0, 2.0, 0.0, 2.0, 3.0])
    fn_b = np.array([2.0, 2.0, 2.0, 1.0, 2.0])
    return tp_a, fp_a, fn_a, tp_b, fp_b, fn_b


@pytest.mark.tier1
def test_permutation_is_deterministic_for_fixed_seed() -> None:
    """Same arrays + same seed -> identical p-value and observed diff."""
    args = _two_conditions()
    r1 = permutation_test_float(*args, n_permutations=2000, seed=42)
    r2 = permutation_test_float(*args, n_permutations=2000, seed=42)
    assert r1["p_value"] == r2["p_value"]
    assert r1["observed_diff"] == r2["observed_diff"]


@pytest.mark.tier1
def test_permutation_observed_diff_is_antisymmetric() -> None:
    """Swapping A and B negates the observed difference; p is unchanged."""
    tp_a, fp_a, fn_a, tp_b, fp_b, fn_b = _two_conditions()
    fwd = permutation_test_float(tp_a, fp_a, fn_a, tp_b, fp_b, fn_b, n_permutations=2000)
    rev = permutation_test_float(tp_b, fp_b, fn_b, tp_a, fp_a, fn_a, n_permutations=2000)
    assert fwd["observed_diff"] == pytest.approx(-rev["observed_diff"])
    # The two-sided p-value uses |observed|, so it is swap-invariant.
    assert fwd["p_value"] == rev["p_value"]


@pytest.mark.tier1
def test_permutation_identical_conditions_give_p_one() -> None:
    """Identical conditions -> zero observed diff and every null diff zero."""
    tp = np.array([2.0, 0.0, 3.0, 1.0])
    fp = np.array([1.0, 0.0, 0.0, 2.0])
    fn = np.array([0.0, 1.0, 1.0, 0.0])
    res = permutation_test_float(tp, fp, fn, tp, fp, fn, n_permutations=1000)
    assert res["observed_diff"] == 0.0
    assert res["p_value"] == 1.0


@pytest.mark.tier1
def test_permutation_separated_pair_has_small_p() -> None:
    """A clearly stronger condition A yields a small two-sided p-value."""
    n = 40
    # A: every tile a clean TP. B: every tile a pure FP (no TPs at all).
    tp_a = np.ones(n)
    fp_a = np.zeros(n)
    fn_a = np.zeros(n)
    tp_b = np.zeros(n)
    fp_b = np.ones(n)
    fn_b = np.ones(n)
    res = permutation_test_float(tp_a, fp_a, fn_a, tp_b, fp_b, fn_b, n_permutations=5000)
    assert res["observed_diff"] > 0.9  # F1_a = 1.0, F1_b = 0.0
    assert res["p_value"] < 0.05


# --------------------------------------------------------------------------- #
# 3. greedy_clique_tiers — tie_set = tiers[0]
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_clique_all_indistinguishable_is_one_tier() -> None:
    """No significant pair -> a single tier containing every condition."""
    refs = ["a", "b", "c"]
    significant: dict[frozenset, bool] = {}  # nothing significant
    tiers = greedy_clique_tiers(refs, significant)
    assert tiers == [["a", "b", "c"]]


@pytest.mark.tier1
def test_clique_all_significant_is_singletons() -> None:
    """Every pair significant -> one singleton tier per condition, in order."""
    refs = ["a", "b", "c"]
    significant = {
        frozenset({"a", "b"}): True,
        frozenset({"a", "c"}): True,
        frozenset({"b", "c"}): True,
    }
    tiers = greedy_clique_tiers(refs, significant)
    assert tiers == [["a"], ["b"], ["c"]]


@pytest.mark.tier1
def test_clique_recovers_leader_pair_then_rest() -> None:
    """A leader clique {a, b} indistinguishable, both clear of {c, d}.

    Mirrors the real result: Tier 1 = the two tied leaders (tie_set),
    everything below significantly separated.
    """
    refs = ["a", "b", "c", "d"]
    significant = {
        frozenset({"a", "b"}): False,  # leaders tied
        frozenset({"a", "c"}): True,
        frozenset({"a", "d"}): True,
        frozenset({"b", "c"}): True,
        frozenset({"b", "d"}): True,
        frozenset({"c", "d"}): False,  # c and d tied to each other
    }
    tiers = greedy_clique_tiers(refs, significant)
    assert tiers[0] == ["a", "b"]  # the tie_set
    assert tiers[1] == ["c", "d"]
