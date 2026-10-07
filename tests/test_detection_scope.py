"""
Tier-1 tests for the D50 detection scope (``scripts/lib_advanced_metrics.py``).

PI ruling D50 (2026-10-07, ``planning/pi-decisions-2026-09-20.md``): the
shared scorer scopes DETECTIONS per sheet by tile geometry, exactly as it
scopes references, attributing each detection to its ORIGIN sheet and never
re-keying it to another sheet; every evaluation records the counts.

The contract exercised here, on a synthetic two-sheet frame (sheet ``A``
tiles x 0-200, sheet ``B`` tiles x 190-390, so the sheets' padded tiles
overlap by 10 m):

* a detection named on a frame sheet but outside that sheet's tiles is
  dropped — neither a true nor a false positive — in the F1 point, the
  per-tile table and the tile confusion alike;
* a detection whose name is on sheet A but which lies only in B's tiles is
  dropped too, and counted as cross-sheet;
* a re-keyed ``source_tile`` never moves a detection off its recorded origin
  sheet, whichever serialisation records the origin (``origin_source_tile``,
  ``origin_tiles``, a list or the NumPy-array ``repr`` of ``source_tiles``);
* a cell with nothing out of frame receives exactly the rows it received
  before, in the same order (its numbers cannot move);
* the detection scope keeps exactly what the reference rule keeps;
* the materialisers' primary-tile assignment never crosses a sheet edge;
* ``evaluate_detections.py`` writes the counts into each evaluation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import lib_advanced_metrics as lam  # noqa: E402

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"


@pytest.fixture()
def frame() -> gpd.GeoDataFrame:
    """Two sheets of two 100 m tiles; B's first tile overlaps A's last by 10 m."""
    return gpd.GeoDataFrame(
        {"tile_name": ["A_x0_y0.png", "A_x100_y0.png", "B_x0_y0.png", "B_x100_y0.png"]},
        geometry=[box(0, 0, 100, 100), box(100, 0, 200, 100),
                  box(190, 0, 290, 100), box(290, 0, 390, 100)],
        crs=CRS,
    )


@pytest.fixture()
def refs() -> gpd.GeoDataFrame:
    """One reference per tile region: two on A, one on B."""
    return gpd.GeoDataFrame(
        {"Map": ["A", "A", "B"]},
        geometry=[Point(50, 50), Point(195, 50), Point(300, 50)],
        crs=CRS,
    )


def dets(rows: list[tuple[str | None, float, float]], **extra: list) -> gpd.GeoDataFrame:
    """Detections from ``(source_tile, x, y)`` rows plus any extra columns."""
    data: dict = {"source_tile": [r[0] for r in rows], **extra}
    return gpd.GeoDataFrame(
        data, geometry=[Point(r[1], r[2]) for r in rows], crs=CRS,
    )


# ── Scope and diagnostics ─────────────────────────────────────────────────


def test_out_of_frame_detection_is_dropped_not_a_false_positive(frame, refs):
    """The defect the ruling closes: before D50 this detection was an FP."""
    d = dets([("A_x0_y0.png", 51, 50), ("A_x100_y0.png", 196, 50),
              ("B_x100_y0.png", 301, 50), ("A_x900_y0.png", 50, 500)])
    scope = lam.scope_detections_to_frame(d, frame)
    assert scope.diagnostics["n_out_of_frame"] == 1
    assert scope.diagnostics["n_in_scope"] == 3
    assert list(scope.detections.index) == [0, 1, 2]
    assert lam.calculate_f1_internal(d, refs, frame, 20) == (1.0, 1.0, 1.0)


def test_cross_sheet_point_is_dropped_and_counted(frame, refs):
    """Named on A, lying only in B's tiles: outside its own sheet, so dropped."""
    d = dets([("A_x100_y0.png", 250, 50)])
    diag = lam.scope_detections_to_frame(d, frame).diagnostics
    assert diag["n_out_of_frame"] == 1
    assert diag["n_out_of_frame_cross_sheet"] == 1
    assert diag["n_in_scope"] == 0


def test_null_and_foreign_names_stay_unattributed_and_are_counted(frame):
    """Unattributed rows are not scored (as before) but the in-frame ones show."""
    d = dets([(None, 60, 60), ("Z_x0_y0.png", 60, 60), ("Z_x0_y0.png", 900, 900)])
    diag = lam.scope_detections_to_frame(d, frame).diagnostics
    assert diag["n_unattributed"] == 3
    assert diag["n_unattributed_in_frame"] == 2
    assert diag["n_in_scope"] == 0


def test_a_fully_in_frame_cell_receives_its_rows_unchanged(frame):
    """No out-of-frame row, no contradicting origin: same rows, same order."""
    d = dets([("B_x100_y0.png", 301, 50), ("A_x0_y0.png", 51, 50),
              ("A_x100_y0.png", 196, 50)])
    d.index = [7, 3, 5]
    scope = lam.scope_detections_to_frame(d, frame)
    assert list(scope.detections.index) == [7, 3, 5]
    assert list(scope.sheets) == ["B", "A", "A"]
    assert scope.on_sheet("A").index.tolist() == [3, 5]


def test_non_unique_index_is_handled_by_position(frame):
    """Concatenated passes can repeat index labels; rows must not conflate."""
    d = dets([("A_x0_y0.png", 51, 50), ("A_x0_y0.png", 50, 500)])
    d.index = [0, 0]
    scope = lam.scope_detections_to_frame(d, frame)
    assert len(scope.detections) == 1
    assert scope.diagnostics["n_out_of_frame"] == 1


def test_attribution_is_required_for_the_f1_scorer(frame, refs):
    """No source_tile and no origin: F1 cannot attribute a sheet, so it raises."""
    d = gpd.GeoDataFrame({"x": [1]}, geometry=[Point(50, 50)], crs=CRS)
    with pytest.raises(KeyError):
        lam.calculate_f1_internal(d, refs, frame, 20)
    relaxed = lam.scope_detections_to_frame(d, frame, require_attribution=False)
    assert relaxed.diagnostics["applied"] is False
    assert len(relaxed.detections) == 1


def test_detection_scope_keeps_exactly_what_the_reference_rule_keeps(frame):
    """Random points: the scope equals scope_references_to_tiles per sheet."""
    rng = np.random.default_rng(20261007)
    xy = rng.uniform(-50, 450, size=(400, 2)) * np.array([1, 0.4])
    names = rng.choice(["A_x0_y0.png", "B_x0_y0.png"], size=len(xy))
    d = dets([(n, x, y) for n, (x, y) in zip(names, xy)])
    kept = set(lam.scope_detections_to_frame(d, frame).detections.index)
    expected: set = set()
    for sheet in ("A", "B"):
        sheet_tiles = frame[frame["tile_name"].str.startswith(sheet)]
        on_sheet = d[d["source_tile"].str.startswith(sheet)]
        expected |= set(lam.scope_references_to_tiles(on_sheet, sheet_tiles).index)
    assert kept == expected


# ── Origin-sheet attribution (never re-key) ───────────────────────────────


@pytest.mark.parametrize("column, value", [
    ("origin_source_tile", "A_x100_y0.png"),
    ("origin_tiles", "A_x100_y0.png;A_x0_y0.png"),
    ("source_tiles", "['A_x100_y0.png' 'A_x0_y0.png'\n 'A_x0_y0.png']"),
    ("source_tiles", '["A_x100_y0.png"]'),
])
def test_a_rekeyed_detection_is_scored_on_its_origin_sheet(frame, refs, column, value):
    """Re-keyed onto B's overlapping tile, seen on A: it matches A's reference."""
    d = dets([("A_x0_y0.png", 51, 50), ("B_x0_y0.png", 196, 50),
              ("B_x100_y0.png", 301, 50)])
    origins = ["A_x0_y0.png", value, "B_x100_y0.png"]
    d[column] = origins
    assert lam.calculate_f1_internal(d, refs, frame, 20) == (1.0, 1.0, 1.0)
    diag = lam.scope_detections_to_frame(d, frame).diagnostics
    assert diag["n_origin_restored"] == 1
    # Without the origin record the re-key costs a TP: FP on B plus FN on A.
    rekeyed_only = d.drop(columns=[column])
    p, r, f = lam.calculate_f1_internal(rekeyed_only, refs, frame, 20)
    assert (round(p, 4), round(r, 4)) == (0.6667, 0.6667)


def test_a_cluster_seen_on_both_sheets_is_scored_on_its_first_origin(frame, refs):
    """Members on A and B; the first (the candidate's own tile) is on A.

    A re-key onto B must not stand merely because one member was seen on B:
    the candidate's tile before the re-key was its first member's, on A.
    """
    d = dets([("B_x0_y0.png", 196, 50)],
             source_tiles=["['A_x100_y0.png' 'B_x0_y0.png']"])
    scope = lam.scope_detections_to_frame(d, frame)
    assert list(scope.sheets) == ["A"]
    assert scope.diagnostics["n_origin_restored"] == 1
    p, r, f = lam.calculate_f1_internal(d, refs, frame, 20)
    assert (p, round(r, 4)) == (1.0, 0.3333)
    names, _diag = lam.assign_primary_tiles_on_origin_sheet(d, frame)
    assert names == ["A_x100_y0.png"]


def test_origin_naming_no_frame_sheet_falls_back_to_source_tile(frame):
    """An unrecognised origin is a naming difference, not a reason to drop."""
    d = dets([("A_x0_y0.png", 51, 50)], origin_tiles=["Q-99_x0_y0.png"])
    diag = lam.scope_detections_to_frame(d, frame).diagnostics
    assert diag["n_origin_unrecognised"] == 1
    assert diag["n_in_scope"] == 1


@pytest.mark.parametrize("value, expected", [
    ("['a_x0_y0.png' 'b_x0_y0.png'\n 'c_x0_y0.png']",
     ["a_x0_y0.png", "b_x0_y0.png", "c_x0_y0.png"]),
    ('["a", "b"]', ["a", "b"]),
    ("a;b; ;c", ["a", "b", "c"]),
    ("a", ["a"]),
    (["a", None, "b"], ["a", "b"]),
    (np.array(["a", "b"]), ["a", "b"]),
    (float("nan"), []),
    (None, []),
    ("", []),
])
def test_parse_tile_list_reads_every_serialisation(value, expected):
    """Lists, JSON, NumPy repr, ';'-joined, bare names and missing values."""
    assert lam.parse_tile_list(value) == expected


# ── One scope everywhere: per-tile table, tile confusion, engine ──────────


def test_per_tile_table_and_point_estimate_describe_the_same_detections(frame, refs):
    """An out-of-frame row joins neither the matching nor the booking."""
    d = dets([("A_x0_y0.png", 51, 50), ("A_x100_y0.png", 196, 50),
              ("B_x100_y0.png", 301, 50), ("A_x0_y0.png", 50, 500)])
    table = lam.compute_per_tile_tp_fp_fn(d, refs, frame, buffer_metres=20)
    assert int(table["tp"].sum()) == 3
    assert int(table["fp"].sum()) == 0
    assert int(table["fn"].sum()) == 0


def test_tile_confusion_does_not_book_an_out_of_frame_name_collision(frame, refs):
    """Before D50 an out-of-frame point carrying a frame tile's name was booked."""
    d = dets([("A_x0_y0.png", 51, 50), ("B_x0_y0.png", 900, 900)])
    result = lam.calculate_tile_classification(d, refs, frame)
    booked = {t["tile_name"] for t in result["tile_details"] if t["has_detections"]}
    assert booked == {"A_x0_y0.png"}
    assert result["detection_scope"]["n_out_of_frame"] == 1


def test_tile_confusion_keeps_rows_on_no_frame_sheet(refs):
    """The rule removes out-of-frame rows only; it never needed a sheet here.

    On a frame whose tile names carry no parseable sheet, and for a null
    name under a geometric join, the confusion books exactly what it booked
    before the ruling.
    """
    bare = gpd.GeoDataFrame({"tile_name": ["t1", "t2"]},
                            geometry=[box(0, 0, 100, 100), box(100, 0, 200, 100)], crs=CRS)
    d = dets([("t1", 50, 50), (None, 150, 50)])
    scope = lam.scope_detections_to_frame(d, bare, require_attribution=False)
    assert len(scope.retained) == 2 and len(scope.detections) == 0
    result = lam.calculate_tile_classification(
        d, refs, bare, tile_join=lam.TILE_JOIN_GEOMETRIC_CONTAINS)
    booked = {t["tile_name"] for t in result["tile_details"] if t["has_detections"]}
    assert booked == {"t1", "t2"}


def test_corrected_f1_engine_uses_the_library_scope(frame, refs):
    """The 55-map engine's per-sheet counts come from the shared loop now."""
    from scripts.compute_corrected_f1_multi_buffer import compute_counts_at_r

    student = refs.rename(columns={"Map": "source_map"})
    d = dets([("A_x0_y0.png", 51, 50), ("A_x0_y0.png", 50, 500)])
    tp, fp, fn, n_ref = compute_counts_at_r(d, student, frame, 20)
    assert (tp, fp, fn, n_ref) == (1, 0, 2, 3)


# ── Materialisers: the primary tile never crosses a sheet edge ────────────


def test_primary_tile_stays_on_the_origin_sheet(frame):
    """The legacy nearest-centroid rule would pick B's tile for x = 196."""
    d = dets([("A_x100_y0.png", 196, 50), ("A_x100_y0.png", 250, 50),
              ("A_x0_y0.png", 51, 50)])
    names, diag = lam.assign_primary_tiles_on_origin_sheet(d, frame)
    assert names == ["A_x100_y0.png", None, "A_x0_y0.png"]
    assert diag["n_cross_sheet_avoided"] == 1
    assert diag["n_outside_origin_sheet"] == 1


def test_primary_tile_without_origin_keeps_the_legacy_rule(frame):
    """Bare centroids have nothing to re-key from; the old rule stands."""
    d = gpd.GeoDataFrame(geometry=[Point(196, 50), Point(900, 900)], crs=CRS)
    names, diag = lam.assign_primary_tiles_on_origin_sheet(d, frame)
    assert names == ["B_x0_y0.png", None]
    assert diag["n_no_origin"] == 1
    assert diag["n_outside_frame"] == 1


def test_h13_assign_primary_tiles_delegates_to_the_origin_rule(frame):
    """prepare_h13_scoring.assign_primary_tiles reads origin_tiles itself."""
    from scripts.prepare_h13_scoring import assign_primary_tiles

    d = gpd.GeoDataFrame({"origin_tiles": ["A_x100_y0.png"]},
                         geometry=[Point(196, 50)], crs=CRS)
    assert assign_primary_tiles(d, frame) == ["A_x100_y0.png"]


# ── The evaluation records the counts ─────────────────────────────────────


def test_evaluation_records_the_detection_scope(frame, refs):
    """evaluate_single_run writes the block; the multi-run summary sums it."""
    from scripts.evaluate_detections import evaluate_multi_run_mean, evaluate_single_run

    d = dets([("A_x0_y0.png", 51, 50), ("A_x0_y0.png", 50, 500)])
    run = evaluate_single_run(d, refs, frame, buffers=[20], n_bootstrap=50, seed=1)
    block = run["detection_scope"]
    assert block["rule"] == lam.DETECTION_SCOPE_RULE
    assert block["n_detections"] == 2
    assert block["n_out_of_frame"] == 1
    summary = evaluate_multi_run_mean([run, run], label="x")
    assert summary["detection_scope"]["n_out_of_frame"] == 2
    assert summary["detection_scope"]["n_passes"] == 2


def test_scope_columns_are_not_required_beyond_the_attribution(frame, refs):
    """A string-typed pandas column with NA behaves like None."""
    d = dets([("A_x0_y0.png", 51, 50), (None, 60, 60)])
    d["source_tile"] = d["source_tile"].astype(pd.StringDtype())
    scope = lam.scope_detections_to_frame(d, frame)
    assert scope.diagnostics["n_in_scope"] == 1
    assert scope.diagnostics["n_unattributed"] == 1
