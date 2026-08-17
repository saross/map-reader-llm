"""Tier-1 tests for scripts/e45_bootstrap_pairings.py.

Covers the pure computational core: micro-F1, the paired tile
bootstrap (determinism, p-value floor, CI behaviour on separable and
null synthetic contrasts), and the reproduction gate's pass/fail
semantics. The loader stages (H2 re-run JSON, H3 tiering loaders) are
exercised by the block's live run and its gates, not simulated here.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from e45_bootstrap_pairings import (  # noqa: E402
    _run_gate,
    micro_f1,
    paired_bootstrap,
)


@pytest.mark.tier1
def test_micro_f1_known_values():
    """Micro-F1 matches hand-computed values and guards zero division."""
    assert micro_f1(0, 0, 0) == 0.0
    assert micro_f1(10, 0, 0) == 1.0
    # P = 10/15, R = 10/12 -> F1 = 2*10 / (2*10 + 5 + 2)
    assert abs(micro_f1(10, 5, 2) - (20 / 27)) < 1e-12


@pytest.mark.tier1
def test_paired_bootstrap_deterministic():
    """Same seed and inputs give byte-identical results."""
    rng = np.random.default_rng(0)
    tp_a = rng.integers(0, 5, 50).astype(float)
    fp_a = rng.integers(0, 3, 50).astype(float)
    fn_a = rng.integers(0, 3, 50).astype(float)
    tp_b = rng.integers(0, 5, 50).astype(float)
    fp_b = rng.integers(0, 3, 50).astype(float)
    fn_b = rng.integers(0, 3, 50).astype(float)
    r1 = paired_bootstrap(tp_a, fp_a, fn_a, tp_b, fp_b, fn_b, 200, seed=42)
    r2 = paired_bootstrap(tp_a, fp_a, fn_a, tp_b, fp_b, fn_b, 200, seed=42)
    assert r1 == r2


@pytest.mark.tier1
def test_paired_bootstrap_separable_contrast():
    """A clearly better arm A yields a positive CI excluding zero and a
    floored p-value."""
    n = 100
    tp_a = np.full(n, 8.0)
    fp_a = np.full(n, 1.0)
    fn_a = np.full(n, 1.0)
    tp_b = np.full(n, 2.0)
    fp_b = np.full(n, 6.0)
    fn_b = np.full(n, 6.0)
    res = paired_bootstrap(tp_a, fp_a, fn_a, tp_b, fp_b, fn_b, 1000, seed=42)
    assert res["ci95"]["lower"] > 0
    assert res["ci_excludes_zero"] is True
    assert res["p_value"] == pytest.approx(1 / 1000)
    assert res["p_at_floor"] is True
    # Observed delta equals the point difference of the full arrays.
    expected = micro_f1(800, 100, 100) - micro_f1(200, 600, 600)
    assert res["observed_delta"] == pytest.approx(expected, abs=1e-6)


@pytest.mark.tier1
def test_paired_bootstrap_null_contrast():
    """Identical arms give a degenerate all-zero delta distribution.

    The 2*min-tail convention clamps p to the floor on an all-zero
    distribution (prop_gt_zero = 0), so `ci_excludes_zero` — not the
    p-value — is the operative null indicator here. Documented
    behaviour, inherited from the family-FDR H1 conventions.
    """
    n = 60
    tp = np.full(n, 4.0)
    fp = np.full(n, 2.0)
    fn = np.full(n, 2.0)
    res = paired_bootstrap(tp, fp, fn, tp, fp, fn, 500, seed=42)
    assert res["observed_delta"] == 0.0
    assert res["ci95"]["lower"] == 0.0 and res["ci95"]["upper"] == 0.0
    assert res["ci_excludes_zero"] is False
    # All deltas are exactly zero -> prop_le_zero = 1, p clamps to 1-ish
    # via 2*min(1, 0) floored at 1/B; min tail is prop_gt_zero = 0.
    assert res["p_value"] == pytest.approx(1 / 500)


@pytest.mark.tier1
def test_paired_bootstrap_is_actually_paired():
    """The pairing guard the S135 audit demonstrated was missing (H-3).

    Arms share huge per-tile variation but differ by a constant +1 TP
    per tile, so the PAIRED delta distribution is nearly degenerate
    (narrow CI). An unpaired resampler (independent index sets per
    arm) mixes unrelated tiles and produces a CI several times wider
    — the audit measured 70 % wider on the real H2 table. The width
    bound below kills that mutant class.
    """
    rng = np.random.default_rng(7)
    tp_b = rng.integers(0, 40, 200).astype(float)
    fp = rng.integers(0, 10, 200).astype(float)
    fn = rng.integers(0, 10, 200).astype(float)
    tp_a = tp_b + 1.0
    res = paired_bootstrap(tp_a, fp, fn, tp_b, fp, fn, 500, seed=42)
    width = res["ci95"]["upper"] - res["ci95"]["lower"]
    # Empirically ~0.002 when paired; an unpaired mutant on these
    # arrays yields > 0.05. The bound sits an order of magnitude
    # inside the mutant's reach.
    assert width < 0.01, f"CI width {width} — pairing appears broken"
    assert res["ci95"]["lower"] > 0


@pytest.mark.tier1
def test_paired_bootstrap_rejects_mismatched_lengths():
    """Unequal arm lengths must raise, never silently truncate (L-7)."""
    a = np.ones(10)
    b = np.ones(9)
    with pytest.raises(ValueError):
        paired_bootstrap(a, a, a, b, b[:9], b, 100, seed=42)


@pytest.mark.tier1
def test_run_gate_passes_within_tolerance():
    """Gate passes at exactly the committed values and records fields."""
    rec = _run_gate("T", {"f1_a": (0.890201, 0.890201),
                          "n_tiles": (487, 487)})
    assert rec["f1_a"]["pass"] and rec["n_tiles"]["pass"]


@pytest.mark.tier1
def test_run_gate_fails_beyond_tolerance():
    """Gate exits (block-plan stop state) on a mismatch beyond 1e-6."""
    with pytest.raises(SystemExit):
        _run_gate("T", {"f1_a": (0.890201, 0.890215)})
