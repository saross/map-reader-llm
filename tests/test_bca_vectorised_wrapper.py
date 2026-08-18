"""Tier-1 tests for the scipy ``vectorized=True`` adapter in ``_bca_ci_from_indices``.

Regression cover for defect D15 (``reports/bca-axis-defect-2026-08-18.md``):
the adapter in ``scripts/lib_advanced_metrics._bca_ci_from_indices`` used to
transpose scipy's resample batch, so a ``(B, n)`` batch produced ``n``
statistics of ``B`` draws each instead of ``B`` statistics of ``n`` draws
each. ``scipy.stats.bootstrap`` performs **no** length check on a vectorised
statistic's return value, so the fault was silent: it changed only interval
width, by a factor of ``sqrt(n / B)``.

The tests here pin the two properties that make that impossible to
reintroduce:

1. the returned bootstrap distribution has length ``B``; and
2. every call to the user-supplied statistic sees ``n`` resampled indices
   (``n - 1`` for the BCa jackknife batch, which is what a leave-one-out
   resample is).

:func:`test_transposed_wrapper_is_rejected_by_these_assertions` is the
negative control: it drives scipy with the *old* wrapper and asserts that it
fails both properties, so a mutation back to the defective form cannot pass
this module. :func:`test_matches_scipy_unvectorised_reference` pins the fixed
adapter against scipy's own ``vectorized=False`` path, which calls the
statistic once per resample and therefore cannot carry this defect.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Callable

import numpy as np
import pytest
from scipy.stats import bootstrap as scipy_bootstrap

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lib_advanced_metrics import _bca_ci_from_indices  # noqa: E402

#: Sample size and resample count for the shape assertions. ``B`` is kept
#: deliberately larger than ``N`` so a transposed adapter produces a visibly
#: wrong length rather than a coincidentally plausible one.
N_TILES = 60
N_RESAMPLES = 400
SEED = 42


def _make_statistic(values: np.ndarray) -> Callable[[np.ndarray], float]:
    """Build a per-index statistic over ``values``.

    Args:
        values: 1-D array of per-unit observations to be indexed.

    Returns:
        A callable taking a 1-D array of indices and returning the mean of
        the indexed observations — smooth, always defined, and with a
        sampling spread that scales as ``1 / sqrt(sample size)``, which is
        what makes the axis defect measurable.
    """

    def statistic(idx: np.ndarray) -> float:
        return float(values[np.asarray(idx, dtype=int)].mean())

    return statistic


def _transposed_wrapper(
    statistic: Callable[[np.ndarray], float],
) -> Callable[..., np.ndarray]:
    """Return the pre-fix (defective) adapter, verbatim, for use as a control.

    Args:
        statistic: The per-index statistic to adapt.

    Returns:
        The adapter as it stood before the D15 fix: it moves ``axis`` to the
        front and iterates, which transposes scipy's resample batch.
    """

    def _vectorised(idx_array: np.ndarray, axis: int = -1) -> np.ndarray:
        idx_array = np.asarray(idx_array, dtype=int)
        if idx_array.ndim == 1:
            return float(statistic(idx_array))
        return np.array(
            [statistic(row) for row in np.moveaxis(idx_array, axis, 0)]
        )

    return _vectorised


@pytest.fixture
def sample_values() -> np.ndarray:
    """Deterministic per-unit observations for the fixtures below."""
    return np.random.default_rng(0).normal(loc=1.0, scale=0.5, size=N_TILES)


@pytest.mark.tier1
def test_bootstrap_distribution_has_length_b(sample_values: np.ndarray) -> None:
    """The returned distribution holds ``n_iterations`` values, not ``n``."""
    result = _bca_ci_from_indices(
        np.arange(N_TILES),
        _make_statistic(sample_values),
        n_iterations=N_RESAMPLES,
        random_seed=SEED,
    )
    assert result["method"] == "BCa"
    assert len(result["bootstrap_distribution"]) == N_RESAMPLES
    # Guard the specific wrong answer the defect produced.
    assert len(result["bootstrap_distribution"]) != N_TILES


@pytest.mark.tier1
def test_every_statistic_call_sees_n_indices(sample_values: np.ndarray) -> None:
    """Each statistic call receives one resample of ``n`` units.

    scipy makes exactly three kinds of call for a one-sample BCa bootstrap:
    one point-estimate call of ``n`` indices, ``B`` resample calls of ``n``
    indices, and ``n`` leave-one-out jackknife calls of ``n - 1`` indices.
    Any other call-length profile means the batch has been transposed.
    """
    statistic = _make_statistic(sample_values)
    seen: Counter[int] = Counter()

    def recording(idx: np.ndarray) -> float:
        seen[len(np.asarray(idx))] += 1
        return statistic(idx)

    _bca_ci_from_indices(
        np.arange(N_TILES), recording,
        n_iterations=N_RESAMPLES, random_seed=SEED,
    )

    assert set(seen) == {N_TILES, N_TILES - 1}, (
        f"unexpected call lengths: {dict(seen)}"
    )
    assert seen[N_TILES] == N_RESAMPLES + 1  # resamples + the point estimate
    assert seen[N_TILES - 1] == N_TILES  # the BCa jackknife batch


@pytest.mark.tier1
def test_matches_scipy_unvectorised_reference(sample_values: np.ndarray) -> None:
    """The adapter reproduces scipy's ``vectorized=False`` path exactly.

    ``vectorized=False`` makes scipy call the statistic once per resample
    through its own ``_vectorize_statistic`` shim, so it cannot carry the
    axis defect. Driven from the same seed, scipy draws the same resample
    indices either way, so the two intervals must agree to floating-point
    equality — the strongest available check on the adapter.
    """
    statistic = _make_statistic(sample_values)
    fixed = _bca_ci_from_indices(
        np.arange(N_TILES), statistic,
        n_iterations=N_RESAMPLES, random_seed=SEED,
    )
    reference = scipy_bootstrap(
        (np.arange(N_TILES),), statistic, n_resamples=N_RESAMPLES,
        method="BCa", confidence_level=0.95, rng=SEED, vectorized=False,
    )
    assert fixed["ci_lower"] == pytest.approx(
        float(reference.confidence_interval.low), abs=1e-12,
    )
    assert fixed["ci_upper"] == pytest.approx(
        float(reference.confidence_interval.high), abs=1e-12,
    )


@pytest.mark.tier1
def test_width_matches_hand_rolled_percentile_bootstrap(
    sample_values: np.ndarray,
) -> None:
    """Interval width agrees with a hand-rolled bootstrap that uses no scipy.

    An independent reference that shares no code with ``scipy.stats``: draw
    ``B`` resamples of ``n`` indices, take the 2.5/97.5 percentiles. For a
    smooth, near-symmetric statistic the BCa and percentile widths agree
    closely, so a large disagreement means the resample size is wrong. Under
    the defect the width was off by ``sqrt(B / n)`` (here ~2.6x), far outside
    the tolerance below.
    """
    statistic = _make_statistic(sample_values)
    fixed = _bca_ci_from_indices(
        np.arange(N_TILES), statistic,
        n_iterations=N_RESAMPLES, random_seed=SEED,
    )
    rng = np.random.default_rng(SEED)
    draws = np.array([
        statistic(rng.integers(0, N_TILES, N_TILES))
        for _ in range(N_RESAMPLES)
    ])
    reference_width = float(
        np.percentile(draws, 97.5) - np.percentile(draws, 2.5)
    )
    fixed_width = fixed["ci_upper"] - fixed["ci_lower"]
    assert fixed_width == pytest.approx(reference_width, rel=0.15)


@pytest.mark.tier1
def test_transposed_wrapper_is_rejected_by_these_assertions(
    sample_values: np.ndarray,
) -> None:
    """Negative control: the pre-fix adapter fails both pinned properties.

    Without this, a mutation restoring ``np.moveaxis(idx_array, axis, 0)``
    could in principle still satisfy a weakly written assertion. Here the
    defective adapter is driven through scipy directly and shown to (a)
    yield a distribution of length ``n`` rather than ``B``, (b) hand the
    statistic ``B`` indices per call, and (c) produce an interval narrower
    than the correct one by roughly ``sqrt(B / n)``.
    """
    statistic = _make_statistic(sample_values)
    seen: Counter[int] = Counter()

    def recording(idx: np.ndarray) -> float:
        seen[len(np.asarray(idx))] += 1
        return statistic(idx)

    broken = scipy_bootstrap(
        (np.arange(N_TILES),), _transposed_wrapper(recording),
        n_resamples=N_RESAMPLES, method="BCa", confidence_level=0.95,
        rng=SEED, vectorized=True,
    )
    # (a) scipy accepts the wrong length silently.
    assert len(broken.bootstrap_distribution) == N_TILES
    # (b) the statistic saw B indices per resample call.
    assert N_RESAMPLES in seen

    fixed = _bca_ci_from_indices(
        np.arange(N_TILES), statistic,
        n_iterations=N_RESAMPLES, random_seed=SEED,
    )
    broken_width = float(
        broken.confidence_interval.high - broken.confidence_interval.low
    )
    fixed_width = fixed["ci_upper"] - fixed["ci_lower"]
    # (c) the width ratio tracks sqrt(B / n) — the defect's signature.
    assert fixed_width / broken_width == pytest.approx(
        np.sqrt(N_RESAMPLES / N_TILES), rel=0.25,
    )
