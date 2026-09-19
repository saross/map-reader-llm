"""The 2x2 interaction test (reports/image-2x2-tests-declaration-2026-09-19.md).

Synthetic tiles: under no interaction the arm effect is the same in both
rows and p is large; under a strong interaction p is small; the statistic is
antisymmetric in the rows and zero when both rows share the same cells.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gemini37_image_55map_r2 import did_test_f1, did_test_mcc  # noqa: E402

pytestmark = pytest.mark.tier1
N = 600


def _counts(rng, tp_rate, fp_rate):
    tp = (rng.random(N) < tp_rate).astype(float)
    fp = (rng.random(N) < fp_rate).astype(float)
    fn = 1.0 - tp
    return tp, fp, fn


def test_no_interaction_gives_a_large_p_on_f1():
    rng = np.random.default_rng(1)
    tp, fp, fn = {}, {}, {}
    for c, (t, f) in {"A1": (0.6, 0.3), "A2": (0.7, 0.2), "B1": (0.5, 0.4), "B2": (0.6, 0.3)}.items():
        tp[c], fp[c], fn[c] = _counts(rng, t, f)
    r = did_test_f1(tp, fp, fn, n_permutations=2000, seed=3)
    assert r["n_tiles"] == N and r["n_permutations"] == 2000
    assert r["p_value"] > 0.05


def test_a_strong_interaction_gives_a_small_p_on_f1():
    rng = np.random.default_rng(2)
    tp, fp, fn = {}, {}, {}
    # arm 2 helps row A a lot and hurts row B
    for c, (t, f) in {"A1": (0.5, 0.4), "A2": (0.9, 0.05), "B1": (0.7, 0.2), "B2": (0.5, 0.4)}.items():
        tp[c], fp[c], fn[c] = _counts(rng, t, f)
    r = did_test_f1(tp, fp, fn, n_permutations=2000, seed=3)
    assert r["observed_diff"] > 0.2
    assert r["p_value"] < 0.01


def test_identical_rows_give_zero_statistic():
    rng = np.random.default_rng(4)
    a1 = _counts(rng, 0.6, 0.3)
    a2 = _counts(rng, 0.7, 0.2)
    tp = {"A1": a1[0], "A2": a2[0], "B1": a1[0], "B2": a2[0]}
    fp = {"A1": a1[1], "A2": a2[1], "B1": a1[1], "B2": a2[1]}
    fn = {"A1": a1[2], "A2": a2[2], "B1": a1[2], "B2": a2[2]}
    r = did_test_f1(tp, fp, fn, n_permutations=500, seed=3)
    assert abs(r["observed_diff"]) < 1e-12
    assert r["p_value"] == 1.0


def test_swapping_the_rows_flips_the_sign_and_keeps_p():
    rng = np.random.default_rng(5)
    cells = {c: _counts(rng, t, f) for c, (t, f) in
             {"A1": (0.5, 0.4), "A2": (0.8, 0.1), "B1": (0.6, 0.3), "B2": (0.6, 0.3)}.items()}
    tp = {c: v[0] for c, v in cells.items()}
    fp = {c: v[1] for c, v in cells.items()}
    fn = {c: v[2] for c, v in cells.items()}
    r1 = did_test_f1(tp, fp, fn, n_permutations=1000, seed=3)
    swap = {"A1": "B1", "A2": "B2", "B1": "A1", "B2": "A2"}
    r2 = did_test_f1({k: tp[swap[k]] for k in tp}, {k: fp[swap[k]] for k in fp},
                     {k: fn[swap[k]] for k in fn}, n_permutations=1000, seed=3)
    assert abs(r1["observed_diff"] + r2["observed_diff"]) < 1e-12
    assert r1["p_value"] == r2["p_value"]


def test_mcc_interaction_detects_a_row_dependent_arm_effect():
    rng = np.random.default_rng(6)
    truth = rng.random(N) < 0.4

    def pred(hit, false):
        return np.where(truth, rng.random(N) < hit, rng.random(N) < false)

    p = {"A1": pred(0.6, 0.3), "A2": pred(0.95, 0.05), "B1": pred(0.7, 0.2), "B2": pred(0.6, 0.3)}
    r = did_test_mcc(p, truth, n_permutations=2000, seed=3)
    assert r["observed_diff"] > 0.2 and r["p_value"] < 0.01
    q = {"A1": pred(0.6, 0.3), "A2": pred(0.7, 0.2), "B1": pred(0.6, 0.3), "B2": pred(0.7, 0.2)}
    r0 = did_test_mcc(q, truth, n_permutations=2000, seed=3)
    assert r0["p_value"] > 0.05
