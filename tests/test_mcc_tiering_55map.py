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
4. ``render_md`` — the numbers in the citable board come from the
   payload verbatim, and the methodological notes are actually emitted.
5. The gate verdict is DERIVED from ``CELLS`` and from the per-cell
   comparisons that ran, not written as the fixed string "8/8" (defect
   D37, audit finding F17d); the two committed boards still render
   byte-identically from their committed JSON.
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
from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    ATTRIBUTION_RESOLUTION_NOTE,
    PAIRED_CI_NOTE,
)
from scripts.mcc_tiering_55map import (  # noqa: E402
    CELLS,
    count_word,
    mcc_from_confusion,
    permutation_test_mcc,
    render_md,
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


# --------------------------------------------------------------------------- #
# 4. render_md — the markdown renderer split out from the compute path so the
#    citable board can be re-rendered from the committed JSON (--rebuild-md).
#    These pin that the numbers in the table come from the payload verbatim and
#    that the two methodological notes are actually emitted.
# --------------------------------------------------------------------------- #

_PAYLOAD = {
    "n_permutations": 10_000,
    "seed": 42,
    "n_significant": 1,
    "n_pairs": 1,
    "tiers": [["A"], ["B"]],
    "cells": [
        {"name": "A", "tier": 1, "mcc": 0.7104, "mcc_ci": [0.697, 0.723],
         "sensitivity": 0.705, "specificity": 0.964,
         "confusion": {"tp": 2483, "fp": 181, "fn": 1041, "tn": 4836}},
        {"name": "B", "tier": 2, "mcc": 0.6903, "mcc_ci": None,
         "sensitivity": 0.699, "specificity": 0.953,
         "confusion": {"tp": 2462, "fp": 235, "fn": 1062, "tn": 4782}},
    ],
    "pairwise": [{"a": "A", "b": "B", "observed_diff": 0.0201,
                  "p_value": 0.0036, "bh_adjusted_p": 0.0056,
                  "significant": True}],
}


@pytest.mark.tier1
def test_render_md_emits_payload_numbers_verbatim():
    """Table cells are formatted from the payload, not recomputed."""
    doc = render_md(_PAYLOAD)
    assert "| 1 | A | 1 | 0.7104 | [0.697, 0.723] | 0.705 | 0.964 | 2483/181/1041/4836 |" in doc
    # A cell with no CI on disk renders an em-dash rather than crashing.
    assert "| 2 | B | 2 | 0.6903 | — |" in doc
    assert "| A vs B | +0.0201 | 0.0036 | 0.0056 | yes |" in doc
    assert "1/1 pairs significant -> 2 tier(s)" in doc


@pytest.mark.tier1
def test_render_md_carries_both_methodological_notes():
    """The paired-CI and attribution-resolution notes reach the citable doc.

    These guard the sign-off caveats: a reader must be able to see why
    overlapping marginal CIs coexist with significant paired tests, and that
    the extended GT collapses to the student GT below R = 50 m.
    """
    doc = render_md(_PAYLOAD)
    assert PAIRED_CI_NOTE in doc
    assert ATTRIBUTION_RESOLUTION_NOTE in doc
    assert "below R = 50 m the\nextended ground truth reduces to the reviewed student ground truth" in doc


@pytest.mark.tier1
def test_render_md_is_deterministic():
    """Same payload -> byte-identical document (no timestamps, no ordering churn)."""
    assert render_md(_PAYLOAD) == render_md(_PAYLOAD)


# --------------------------------------------------------------------------- #
# 5. The gate verdict is derived, not asserted (defect D37, finding F17d).
#    Both the JSON ``gate`` string and the markdown's "(8/8)" used to be fixed
#    text, decoupled from ``CELLS`` and from the per-cell comparisons that
#    actually ran — so adding or removing a cell would have left the committed
#    board claiming a verification it never performed.
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_count_word_spells_small_cardinals_and_falls_back_to_digits() -> None:
    assert count_word(2) == "two"
    assert count_word(8) == "eight"
    assert count_word(13) == "13"


@pytest.mark.tier1
def test_render_md_derives_board_size_and_gate_from_the_payload() -> None:
    """A two-cell payload must say "two" and "(2/2)", never "eight"/"8/8"."""
    doc = render_md(_PAYLOAD)
    assert "for the two canonical-GT cells" in doc
    assert "reproduce the committed evaluations exactly (2/2)" in doc
    assert "eight" not in doc
    assert "8/8" not in doc


@pytest.mark.tier1
def test_render_md_prefers_the_recorded_gate_tally() -> None:
    """When the compute path recorded a tally, the renderer uses it."""
    payload = dict(_PAYLOAD, gate_cells_verified=7, gate_cells_total=8)
    doc = render_md(payload)
    assert "exactly (7/8)" in doc
    # Board size still comes from the cell list, which is a different count.
    assert "for the two canonical-GT cells" in doc


@pytest.mark.tier1
def test_render_md_falls_back_to_the_cell_list_for_older_json() -> None:
    """``--rebuild-md`` on a pre-fix JSON must still render truthfully.

    Every cell in ``cells`` passed the gate — the compute path exits on
    the first failure — so the cell count is the honest fallback.
    """
    payload = {k: v for k, v in _PAYLOAD.items()
               if not k.startswith("gate_cells")}
    assert "exactly (2/2)" in render_md(payload)


@pytest.mark.tier1
def test_committed_boards_still_render_byte_identically() -> None:
    """The derivation must not perturb the two citable committed boards.

    They are NOT regenerated by this fix; this pins that a future
    ``--rebuild-md`` reproduces them exactly from the committed JSON.
    """
    import json as _json

    board_dir = PROJECT_ROOT / "results" / "metric-leaderboards"
    for stem in ("55map-mcc-tiering", "55map-mcc-tiering-standardised"):
        json_path = board_dir / f"{stem}.json"
        md_path = board_dir / f"{stem}.md"
        if not (json_path.is_file() and md_path.is_file()):  # pragma: no cover
            pytest.skip(f"{stem} not present in this checkout")
        payload = _json.loads(json_path.read_text(encoding="utf-8"))
        assert render_md(payload) + "\n" == md_path.read_text(encoding="utf-8")


@pytest.mark.tier1
def test_committed_gate_strings_agree_with_the_current_cell_list() -> None:
    """The published tally must match ``len(CELLS)``.

    This is the tripwire the fixed string could not provide: change
    ``CELLS`` without re-running the boards and this fails.
    """
    import json as _json

    board_dir = PROJECT_ROOT / "results" / "metric-leaderboards"
    expected = f"(exact), {len(CELLS)}/{len(CELLS)}"
    for stem in ("55map-mcc-tiering", "55map-mcc-tiering-standardised"):
        json_path = board_dir / f"{stem}.json"
        if not json_path.is_file():  # pragma: no cover
            pytest.skip(f"{stem} not present in this checkout")
        payload = _json.loads(json_path.read_text(encoding="utf-8"))
        assert payload["gate"].endswith(expected), stem
        assert len(payload["cells"]) == len(CELLS), stem
