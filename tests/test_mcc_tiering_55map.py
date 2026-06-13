"""
Tests for ``scripts.mcc_tiering_55map`` — the alternate-metric (tile-MCC)
permutation tiering for the 55-map canonical board (Session 114).

The BH-FDR and greedy-clique machinery are imported VERBATIM from the
F1 boards and covered by their own suites. What is new here, and pinned
below (all tier 1, synthetic, no I/O):

1. ``mcc_from_confusion`` — matches the hand formula and the
   ``calculate_tile_classification`` engine on the same counts.
2. ``permutation_test_mcc`` — self-vs-self gives observed_diff 0 and
   p = 1.0; a constructed strong difference is detected (small p);
   the seeded run is deterministic.
3. ``tile_vectors`` — reproduces ``calculate_tile_classification``'s
   confusion matrix on a synthetic grid INCLUDING a reference point on
   a shared tile boundary (the intersects-counts-for-both semantics).
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import calculate_tile_classification  # noqa: E402
from scripts.mcc_tiering_55map import (  # noqa: E402
    mcc_from_confusion,
    permutation_test_mcc,
    tile_vectors,
)


# --------------------------------------------------------------------------- #
# 1. mcc_from_confusion
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_mcc_from_confusion_matches_hand_formula() -> None:
    """tp=2, tn=2, fp=1, fn=1 -> (4-1)/sqrt(3*3*3*3) = 1/3."""
    assert mcc_from_confusion(2, 2, 1, 1) == pytest.approx(1 / 3)


@pytest.mark.tier1
def test_mcc_from_confusion_zero_denominator_is_zero() -> None:
    """A zero row/column sum yields 0.0 (vectorised analogue of None)."""
    assert mcc_from_confusion(0, 5, 0, 0) == 0.0


@pytest.mark.tier1
def test_mcc_from_confusion_is_vectorised() -> None:
    """Array inputs return aligned array outputs."""
    out = mcc_from_confusion(
        np.array([2, 0]), np.array([2, 5]), np.array([1, 0]), np.array([1, 0])
    )
    assert out.shape == (2,)
    assert out[0] == pytest.approx(1 / 3)
    assert out[1] == 0.0


# --------------------------------------------------------------------------- #
# 2. permutation_test_mcc
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_permutation_self_vs_self_is_null() -> None:
    """Identical predictions: zero observed difference, p = 1.0."""
    rng = np.random.default_rng(0)
    truth = rng.random(200) < 0.4
    pred = rng.random(200) < 0.5
    r = permutation_test_mcc(pred, pred.copy(), truth, n_permutations=500, seed=42)
    assert r["observed_diff"] == 0.0
    assert r["p_value"] == 1.0


@pytest.mark.tier1
def test_permutation_detects_strong_difference() -> None:
    """A perfect cell vs an inverted cell is resolved at small p."""
    rng = np.random.default_rng(0)
    truth = rng.random(200) < 0.4
    r = permutation_test_mcc(truth.copy(), ~truth, truth, n_permutations=500, seed=42)
    assert r["mcc_a"] == pytest.approx(1.0)
    assert r["p_value"] < 0.01


@pytest.mark.tier1
def test_permutation_is_seed_deterministic() -> None:
    """Two runs with the same seed return identical results."""
    rng = np.random.default_rng(1)
    truth = rng.random(150) < 0.4
    pred_a = rng.random(150) < 0.5
    pred_b = rng.random(150) < 0.5
    r1 = permutation_test_mcc(pred_a, pred_b, truth, n_permutations=300, seed=42)
    r2 = permutation_test_mcc(pred_a, pred_b, truth, n_permutations=300, seed=42)
    assert r1 == r2


# --------------------------------------------------------------------------- #
# 3. tile_vectors equivalence with calculate_tile_classification
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_tile_vectors_reproduces_engine_confusion() -> None:
    """The vectorised per-tile labelling matches the engine's loop,
    including a reference point sitting ON a shared tile boundary
    (intersects -> counts for both tiles)."""
    crs = "EPSG:32635"
    bounds = gpd.GeoDataFrame(
        {
            "tile_name": ["t00", "t01", "t10", "t11"],
            "geometry": [
                box(0, 0, 10, 10), box(10, 0, 20, 10),
                box(0, 10, 10, 20), box(10, 10, 20, 20),
            ],
        },
        crs=crs,
    )
    refs = gpd.GeoDataFrame(
        geometry=[
            Point(5, 5),     # interior of t00
            Point(10, 5),    # ON the t00/t01 boundary — both tiles populated
        ],
        crs=crs,
    )
    dets = gpd.GeoDataFrame(
        {
            "source_tile": ["t00", "t11", "not-a-tile"],
            "geometry": [Point(2, 2), Point(15, 15), Point(1, 1)],
        },
        crs=crs,
    )

    engine = calculate_tile_classification(dets, refs, bounds)
    tiles, truth, pred = tile_vectors(dets, refs, bounds)

    rebuilt = {
        "tp": int((pred & truth).sum()),
        "tn": int((~pred & ~truth).sum()),
        "fp": int((pred & ~truth).sum()),
        "fn": int((~pred & truth).sum()),
    }
    assert rebuilt == {k: engine[k] for k in ("tp", "tn", "fp", "fn")}
    # Pin the boundary semantics explicitly: t00 TP, t01 FN (populated via
    # the boundary point, no detections), t10 TN, t11 FP.
    assert rebuilt == {"tp": 1, "tn": 1, "fp": 1, "fn": 1}
