"""
Tier-1 tests for the tile-join option on a board's MCC family and MCC MCB.

The gold-standard (GS) Era-2 verified board reports a tile-level Matthews
Correlation Coefficient (MCC) permutation family and an MCC Multiple
Comparisons with the Best (MCB) admissible set beside its preregistered F1
tiering. Both were built under the published name-based (``id``) tile join
only (S153 ruling 6). The MCC robustness job of 2026-10-30
(``planning/paper-writeup-continuity.md``, part (b)) needs the same two
instruments under the two geometric joins, because the scoring frame overlaps
(384 px tiles on a 336 px stride) and the joins book a point to different
tiles there (``reports/tile-mcc-geometric-join-2026-09-12.md`` § 2).

These tests pin the two halves of that option:

1. **The default is unchanged.** With no join named, the per-tile
   classification, the cell loader, the MCC ordering and the MCB statistic
   behave exactly as before — the default call equals the explicit ``id``
   call, the committed-record gate still runs, no sensitivity key appears,
   and the MCB indicators are still derived from the F1 arm's counts.
2. **The option changes the confusion.** On a small overlapping frame where
   the three joins book points differently, naming a geometric join changes
   the per-tile labels, the gated aggregate, the MCC the family ranks on, and
   the MCB indicators — and the command lines refuse a non-default join where
   it would not change anything.

Everything runs on synthetic frames in ``tmp_path``; no committed board
artefact is read.

Author: Shawn Ross, Claude Code (Session 166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

from scripts import era1_leaderboard_tiering as t
from scripts import selection_aware_intervals as sai
from scripts.lib_advanced_metrics import (
    TILE_JOIN_DEFAULT,
    TILE_JOIN_GEOMETRIC_CONTAINS,
    TILE_JOIN_GEOMETRIC_PRIMARY,
    TILE_JOIN_ID,
    calculate_tile_classification,
)

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"
ORIGIN_X = 500000.0
ORIGIN_Y = 4700000.0
TILE = 100.0
STRIDE = 80.0

# --------------------------------------------------------------------------
# The fixture frame, and why the three joins disagree on it
# --------------------------------------------------------------------------
#
# Four tiles on an 80 m stride, 100 m wide, so neighbours overlap by 20 m:
#   T0 [0, 100]   centroid  50      T2 [160, 260] centroid 210
#   T1 [80, 180]  centroid 130      T3 [240, 340] centroid 290
#
# Cell "a" detections (each carrying the tile its proposer saw):
#   x =  95, source T0 — in T0 and T1; its nearest centroid is T1's.
#   x = 300, source T3 — in T3 only.
# References:
#   x =  20 — in T0 only.
#   x = 250 — in T2 and T3, equidistant from both centroids, so the primary
#             join's lexicographic tie-break books it to T2.
#
# Per-tile labels (T0, T1, T2, T3) and confusion (tp, tn, fp, fn):
#   id        TP TN FN TP  -> (2, 1, 0, 1), MCC +0.5774
#   primary   FN FP FN FP  -> (0, 0, 2, 2), MCC -1.0000
#   contains  TP FP FN TP  -> (2, 0, 1, 1), MCC -0.3333
# Cell "b" holds the x = 300 detection alone; under id it is (1, 1, 0, 2).

DET_A = [(95.0, 0), (300.0, 3)]
DET_B = [(300.0, 3)]
REFS = [20.0, 250.0]

EXPECTED_A = {
    TILE_JOIN_ID: {"tp": 2, "tn": 1, "fp": 0, "fn": 1},
    TILE_JOIN_GEOMETRIC_PRIMARY: {"tp": 0, "tn": 0, "fp": 2, "fn": 2},
    TILE_JOIN_GEOMETRIC_CONTAINS: {"tp": 2, "tn": 0, "fp": 1, "fn": 1},
}
EXPECTED_MCC_A = {
    TILE_JOIN_ID: 0.5774,
    TILE_JOIN_GEOMETRIC_PRIMARY: -1.0,
    TILE_JOIN_GEOMETRIC_CONTAINS: -0.3333,
}
EXPECTED_B_ID = {"tp": 1, "tn": 1, "fp": 0, "fn": 2}


def _frame() -> gpd.GeoDataFrame:
    """The four overlapping tiles, named in the project's sheet convention."""
    names, geometries = [], []
    for i in range(4):
        x0 = ORIGIN_X + i * STRIDE
        names.append(f"o_x{int(i * STRIDE)}_y0.png")
        geometries.append(box(x0, ORIGIN_Y, x0 + TILE, ORIGIN_Y + TILE))
    return gpd.GeoDataFrame({"tile_name": names}, geometry=geometries, crs=CRS)


def _detections(spec: list[tuple[float, int]]) -> gpd.GeoDataFrame:
    """Detections at ``(x offset, recorded tile index)``, mid-height."""
    names = list(_frame()["tile_name"])
    return gpd.GeoDataFrame(
        {"source_tile": [names[i] for _x, i in spec], "Map": ["o"] * len(spec)},
        geometry=[Point(ORIGIN_X + x, ORIGIN_Y + 50) for x, _i in spec],
        crs=CRS,
    )


def _references() -> gpd.GeoDataFrame:
    """The two reference mounds, on sheet ``o``."""
    return gpd.GeoDataFrame(
        {"Map": ["o"] * len(REFS)},
        geometry=[Point(ORIGIN_X + x, ORIGIN_Y + 50) for x in REFS],
        crs=CRS,
    )


def _confusion(arrays: tuple) -> dict[str, int]:
    """Sum the one-hot arrays of :func:`t.cell_per_tile_classification`."""
    tp, tn, fp, fn, _diag = arrays
    return {"tp": int(tp.sum()), "tn": int(tn.sum()),
            "fp": int(fp.sum()), "fn": int(fn.sum())}


def _write_board(tmp_path: Path) -> tuple[Path, Path]:
    """A two-cell board on disk, each cell committed under the ``id`` join.

    Returns:
        ``(conditions_path, analyses_path)``; the board's analysis id is
        ``board`` and its cells are ``r::a`` and ``r::b``.
    """
    bounds = tmp_path / "bounds.geojson"
    refs = tmp_path / "refs.geojson"
    _frame().to_file(bounds, driver="GeoJSON")
    _references().to_file(refs, driver="GeoJSON")
    conditions = []
    for label, spec, confusion, mcc in (
        ("a", DET_A, EXPECTED_A[TILE_JOIN_ID], EXPECTED_MCC_A[TILE_JOIN_ID]),
        ("b", DET_B, EXPECTED_B_ID, 0.3333),
    ):
        det = tmp_path / f"det_{label}.geojson"
        _detections(spec).to_file(det, driver="GeoJSON")
        evaluation = tmp_path / f"eval_{label}.json"
        evaluation.write_text(json.dumps({
            "_metadata": {"cli_args": {
                "detections": str(det), "bounds": str(bounds),
                "ground_truth": str(refs),
            }},
            "summary": {
                "buffers": [{"buffer_metres": 20, "f1": 0.5}],
                "tile_classification": {"confusion": confusion,
                                        "mcc": {"point": mcc}},
            },
        }))
        conditions.append({"label": label, "eval_path": str(evaluation),
                           "architecture": "proposer-verifier"})
    conditions_path = tmp_path / "run-conditions.json"
    conditions_path.write_text(json.dumps(
        {"decomposition": {"r": {"conditions": conditions}}}))
    analyses_path = tmp_path / "run-analyses.json"
    analyses_path.write_text(json.dumps({"analyses": [
        {"analysis_id": "board", "conditions_compared": ["r::a", "r::b"]}]}))
    return conditions_path, analyses_path


def _load(tmp_path: Path, **kwargs) -> list[dict]:
    """Load the fixture board with the MCC arm on."""
    conditions, analyses = _write_board(tmp_path)
    cells, _ref, _bounds, _order = t.load_cells(
        conditions, analyses, "board", None, None, want_mcc=True,
        withheld=[], **kwargs,
    )
    return cells


# --------------------------------------------------------------------------
# 1. The default path is unchanged
# --------------------------------------------------------------------------

def test_the_default_join_is_the_published_id_join():
    """The option's default is the library's default, which is ``id``."""
    assert TILE_JOIN_DEFAULT == TILE_JOIN_ID


def test_default_per_tile_classification_equals_the_explicit_id_call():
    """Naming no join gives exactly the arrays the ``id`` join gives."""
    frame, refs, dets = _frame(), _references(), _detections(DET_A)
    order = list(frame["tile_name"])
    default = t.cell_per_tile_classification(dets, refs, frame, order)
    explicit = t.cell_per_tile_classification(
        dets, refs, frame, order, tile_join=TILE_JOIN_ID)
    for got, want in zip(default[:4], explicit[:4], strict=True):
        np.testing.assert_array_equal(got, want)
    assert default[4] == explicit[4]
    assert _confusion(default) == EXPECTED_A[TILE_JOIN_ID]


def test_default_load_cells_gates_against_the_committed_record(tmp_path):
    """The default loader keeps the committed-record gate and adds no key."""
    cells = _load(tmp_path)
    for cell in cells:
        assert "mcc_join" not in cell
        assert "tile_join" not in cell["mcc_gate"]
        assert cell["mcc_gate"]["passed"] is True
    assert cells[0]["mcc_gate"]["confusion"] == EXPECTED_A[TILE_JOIN_ID]
    assert t.mcc_point(cells[0]) == pytest.approx(EXPECTED_MCC_A[TILE_JOIN_ID])


def test_default_load_cells_still_withholds_a_disagreeing_record(tmp_path):
    """A committed record the rebuild contradicts is still caught by default."""
    conditions, analyses = _write_board(tmp_path)
    evaluation = tmp_path / "eval_a.json"
    doc = json.loads(evaluation.read_text())
    doc["summary"]["tile_classification"]["confusion"]["tn"] += 1
    evaluation.write_text(json.dumps(doc))
    cells, *_rest = t.load_cells(conditions, analyses, "board", None, None,
                                 want_mcc=True, withheld=[])
    assert cells[0]["mcc_gate"]["passed"] is False
    assert "mcc_withheld" in cells[0]


def test_mcc_point_ignores_a_join_value_that_is_absent():
    """Without ``mcc_join`` the ordering reads the committed MCC as before."""
    cell = {"mcc": 0.5}
    assert t.mcc_point(cell) == 0.5
    cell["mcc_join"] = 0.7
    assert t.mcc_point(cell) == 0.7


def test_mcb_default_indicators_are_derived_from_the_f1_counts():
    """``has_det=None`` and the legacy derivation give identical MCB output."""
    rng = np.random.default_rng(0)
    counts = rng.integers(0, 2, size=(4, 30, 3)).astype(float)
    has_mounds = rng.random(30) < 0.5
    legacy = (counts[:, :, 0] + counts[:, :, 1]) > 0
    default = sai.run(counts, 50, 1.0, 42, has_mounds=has_mounds, metric="mcc")
    explicit = sai.run(counts, 50, 1.0, 42, has_mounds=has_mounds, metric="mcc",
                       has_det=legacy)
    # Compared as serialised JSON, which is what the CLI writes, so an
    # undefined (NaN) entry compares equal to itself.
    assert json.dumps(default, sort_keys=True) == json.dumps(explicit, sort_keys=True)


def test_board_indicators_under_id_match_the_default_derivation(tmp_path):
    """The join-aware builder, run under ``id``, reproduces the default path.

    This pins the builder's own derivation (predicted-populated = TP or FP,
    reference-populated = TP or FN) against the default path's (F1-arm
    TP + FP, references by intersection), so a geometric result differs from
    the published one because of the join and not because of the builder.
    """
    conditions, analyses = _write_board(tmp_path)
    specs, counts, occupancy = sai.build_board_tile_counts(
        "board", analyses_path=analyses, conditions_path=conditions)
    j_specs, j_counts, j_occupancy, j_has_det = sai.build_board_tile_classification(
        "board", TILE_JOIN_ID, analyses_path=analyses, conditions_path=conditions)
    assert j_specs == specs
    np.testing.assert_array_equal(j_counts, counts)
    np.testing.assert_array_equal(j_occupancy, occupancy)
    np.testing.assert_array_equal(
        j_has_det, (counts[:, :, 0] + counts[:, :, 1]) > 0)


# --------------------------------------------------------------------------
# 2. The option changes the confusion where the joins differ
# --------------------------------------------------------------------------

@pytest.mark.parametrize("join", sorted(EXPECTED_A))
def test_each_join_gives_its_own_confusion(join):
    """The per-tile labels follow the named join, matching the scorer's."""
    frame, refs, dets = _frame(), _references(), _detections(DET_A)
    arrays = t.cell_per_tile_classification(
        dets, refs, frame, list(frame["tile_name"]), tile_join=join)
    assert _confusion(arrays) == EXPECTED_A[join]
    aggregate = calculate_tile_classification(dets, refs, frame, tile_join=join)
    assert {k: aggregate[k] for k in ("tp", "tn", "fp", "fn")} == EXPECTED_A[join]


def test_the_three_joins_disagree_on_the_fixture():
    """The fixture really does separate the joins, or the tests prove nothing."""
    assert len({tuple(c.values()) for c in EXPECTED_A.values()}) == 3
    assert len(set(EXPECTED_MCC_A.values())) == 3


@pytest.mark.parametrize("join", [TILE_JOIN_GEOMETRIC_PRIMARY,
                                  TILE_JOIN_GEOMETRIC_CONTAINS])
def test_load_cells_under_a_geometric_join_ranks_on_that_join(tmp_path, join):
    """A geometric join is gated on its own aggregate and ranked on its MCC.

    The committed record holds the ``id`` confusion, so gating against it
    would fail every cell; the sensitivity gate compares with the scorer's
    aggregate under the same join instead, and records that it did.
    """
    cells = _load(tmp_path, tile_join=join)
    gate = cells[0]["mcc_gate"]
    assert gate["passed"] is True
    assert gate["tile_join"] == join
    assert gate["confusion"] == EXPECTED_A[join]
    assert cells[0]["mcc_join"] == pytest.approx(EXPECTED_MCC_A[join])
    assert t.mcc_point(cells[0]) == pytest.approx(EXPECTED_MCC_A[join])
    # The published MCC is kept beside it, untouched.
    assert cells[0]["mcc"] == pytest.approx(EXPECTED_MCC_A[TILE_JOIN_ID])
    # The F1 arm ignores the join.
    (tmp_path / "default").mkdir()
    default_cells = _load(tmp_path / "default")
    for k in ("tp", "fp", "fn"):
        np.testing.assert_array_equal(cells[0][k], default_cells[0][k])


def test_load_cells_rejects_an_unknown_join(tmp_path):
    """An unknown join name raises rather than falling back to ``id``."""
    conditions, analyses = _write_board(tmp_path)
    with pytest.raises(ValueError, match="tile_join must be one of"):
        t.load_cells(conditions, analyses, "board", None, None, want_mcc=True,
                     withheld=[], tile_join="nearest")


def test_board_indicators_follow_a_geometric_join(tmp_path):
    """The MCB builder reads the join's labels, not the F1 arm's."""
    conditions, analyses = _write_board(tmp_path)
    _specs, counts, occupancy = sai.build_board_tile_counts(
        "board", analyses_path=analyses, conditions_path=conditions)
    _j, _c, j_occupancy, j_has_det = sai.build_board_tile_classification(
        "board", TILE_JOIN_GEOMETRIC_PRIMARY, analyses_path=analyses,
        conditions_path=conditions)
    # References: intersection books T0, T2 and T3; primary books T0 and T2.
    np.testing.assert_array_equal(occupancy, [True, False, True, True])
    np.testing.assert_array_equal(j_occupancy, [True, False, True, False])
    # Cell a's detections: by name T0 and T3; by nearest centroid T1 and T3.
    np.testing.assert_array_equal(
        (counts[0, :, 0] + counts[0, :, 1]) > 0, [True, False, False, True])
    np.testing.assert_array_equal(j_has_det[0], [False, True, False, True])


def test_mcb_statistic_changes_with_the_indicators():
    """Supplying different indicators changes the MCB's apparent MCC."""
    # A four-tile pattern repeated ten times, so no resample of 40 tiles is
    # likely to lose a whole marginal.
    reps = 10
    has_mounds = np.tile([True, False, True, False], reps)
    block = np.zeros((2, 4, 3))
    block[0, 0, 0] = block[0, 2, 0] = 1          # derived: perfect classifier
    block[1, 0, 0] = block[1, 1, 1] = block[1, 2, 0] = 1
    counts = np.tile(block, (1, reps, 1))
    joined = np.tile([[True, True, False, False], [True, False, True, False]],
                     (1, reps))
    derived = sai.run(counts, 20, 1.0, 42, has_mounds=has_mounds, metric="mcc")
    supplied = sai.run(counts, 20, 1.0, 42, has_mounds=has_mounds, metric="mcc",
                       has_det=joined)
    assert derived["apparent_f1"] == pytest.approx(1.0)
    assert supplied["apparent_f1"] == pytest.approx(1.0)
    assert derived["selected_index"] == 0
    assert supplied["selected_index"] == 1


def test_mcb_rejects_indicators_of_the_wrong_shape():
    """A mis-shaped ``has_det`` raises rather than broadcasting silently."""
    counts = np.zeros((2, 4, 3))
    with pytest.raises(ValueError, match="has_det has shape"):
        sai.run(counts, 5, 1.0, 42, has_mounds=np.ones(4, dtype=bool),
                metric="mcc", has_det=np.ones((4,), dtype=bool))


# --------------------------------------------------------------------------
# 3. The command lines refuse a join where it would change nothing
# --------------------------------------------------------------------------

def test_tiering_cli_refuses_a_geometric_join_without_the_mcc_arm(
        tmp_path, monkeypatch):
    """``--tile-join`` alone would label an unchanged F1 tiering a sensitivity run."""
    monkeypatch.setattr(sys, "argv", [
        "era1_leaderboard_tiering.py", "--analysis-id", "board",
        "--output-dir", str(tmp_path), "--tile-join", TILE_JOIN_GEOMETRIC_PRIMARY,
    ])
    with pytest.raises(SystemExit) as raised:
        t.main()
    assert raised.value.code == 2


def test_mcb_cli_refuses_a_geometric_join_on_f1(tmp_path, monkeypatch):
    """The F1 MCB does not depend on the join, so naming one is refused."""
    monkeypatch.setattr(sys, "argv", [
        "selection_aware_intervals.py", "--board", "board", "--metric", "f1",
        "--tile-join", TILE_JOIN_GEOMETRIC_CONTAINS, "--out", str(tmp_path),
    ])
    with pytest.raises(SystemExit) as raised:
        sai.main()
    assert raised.value.code == 2
