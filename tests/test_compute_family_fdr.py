"""Tier-1 tests for ``scripts/compute_family_fdr.py`` (the registered family
BH-FDR correction).

Covers the pure arithmetic only — the monotone Benjamini–Hochberg step-up,
its tie rule, and the F1-from-counts helper. The bootstrap itself is
validated at run time by the script's own Gates A and B against committed
artefacts (no 10 000-iteration compute belongs in tier 1).
"""

from __future__ import annotations

import pytest

from scripts.compute_family_fdr import bh_step_up, f1_from_counts


@pytest.mark.tier1
def test_bh_step_up_known_example():
    # Seven inputs mirroring the family's shape; hand-computed expectation:
    # thresholds k/7*0.05 = .00714, .0143, .0214, .0286, .0357, .0429, .05;
    # p=(1e-4, 1e-4, .001, .01, .12, .75, .83) rejects the first four.
    inputs = [
        {"hypothesis": "H2", "numeric_p": 1e-4},
        {"hypothesis": "H3", "numeric_p": 1e-4},
        {"hypothesis": "H7", "numeric_p": 0.001},
        {"hypothesis": "H1", "numeric_p": 0.01},
        {"hypothesis": "H4", "numeric_p": 0.12},
        {"hypothesis": "H5", "numeric_p": 0.75},
        {"hypothesis": "H8", "numeric_p": 0.83},
    ]
    ranked = bh_step_up(inputs, q=0.05)
    rejected = [r["hypothesis"] for r in ranked if r["rejected"]]
    assert rejected == ["H2", "H3", "H7", "H1"]
    # Tie rule: H2 ranks before H3 at the shared floor.
    assert [r["hypothesis"] for r in ranked[:2]] == ["H2", "H3"]
    # Monotone adjusted p-values, clipped at 1.
    adj = [r["adjusted_p"] for r in ranked]
    assert adj == sorted(adj)
    assert all(0 < a <= 1 for a in adj)
    # Tied floor inputs share an adjusted p.
    assert ranked[0]["adjusted_p"] == ranked[1]["adjusted_p"]


@pytest.mark.tier1
def test_bh_step_up_gap_rule():
    # A p below threshold AFTER one above it still rejects everything up to
    # the LARGEST passing rank (step-up, not step-down).
    inputs = [
        {"hypothesis": "A", "numeric_p": 0.004},
        {"hypothesis": "B", "numeric_p": 0.02},   # above 2/4*.05=.025? no, passes
        {"hypothesis": "C", "numeric_p": 0.03},   # 3/4*.05=.0375 -> passes
        {"hypothesis": "D", "numeric_p": 0.9},
    ]
    ranked = bh_step_up(inputs, q=0.05)
    rejected = [r["hypothesis"] for r in ranked if r["rejected"]]
    assert rejected == ["A", "B", "C"]


@pytest.mark.tier1
def test_f1_from_counts():
    assert f1_from_counts(0, 0, 0) == 0.0
    assert f1_from_counts(10, 0, 0) == 1.0
    assert abs(f1_from_counts(5, 5, 5) - 0.5) < 1e-12


def _mats(rng, scale_text: float = 1.0, scale_image: float = 1.0) -> dict:
    """Five conditions x 3 runs x 40 tiles of synthetic TP/FP/FN counts."""
    import numpy as np

    from scripts.compute_family_fdr import IMAGE_GROUP, TEXT_GROUP

    out = {}
    for cond in TEXT_GROUP + IMAGE_GROUP:
        scale = scale_text if cond in TEXT_GROUP else scale_image
        tp = rng.poisson(1.5 * scale, (3, 40))
        fp = rng.poisson(0.8 / scale, (3, 40))
        fn = rng.poisson(0.6, (3, 40))
        out[cond] = np.stack([tp, fp, fn], axis=-1).astype(float)
    return out


@pytest.mark.tier1
def test_h1_label_permutation_identical_conditions_give_p_one():
    """D42: five identical conditions give observed 0 and p = 1."""
    import numpy as np

    from scripts.compute_family_fdr import (
        ALL_CONDITIONS,
        h1_label_permutation,
        pooled_delta,
    )

    rng = np.random.default_rng(0)
    one = _mats(rng)["brief-text"]
    mats = {c: one.copy() for c in ALL_CONDITIONS}
    point = pooled_delta(mats, np.arange(40))
    res = h1_label_permutation(mats, point)
    assert res["observed"] == 0.0
    assert res["p_value"] == 1.0


@pytest.mark.tier1
def test_h1_label_permutation_detects_a_group_difference():
    """A text group far better than the image group gives a small p."""
    import numpy as np

    from scripts.compute_family_fdr import h1_label_permutation, pooled_delta

    rng = np.random.default_rng(1)
    mats = _mats(rng, scale_text=2.5, scale_image=0.6)
    point = pooled_delta(mats, np.arange(40))
    res = h1_label_permutation(mats, point)
    assert res["observed"] == pytest.approx(point, abs=1e-12)
    assert res["observed"] > 0
    assert res["p_value"] < 0.01
