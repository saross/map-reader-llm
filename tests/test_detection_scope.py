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
* ``evaluate_detections.py`` writes the counts into each evaluation;
* (the D50 review, Astra, 2026-10-09) one tile-to-sheet assignment serves
  references, detections and each sheet's tiles even when one sheet name is
  a prefix of another (finding 3), and per-sheet results are partitions of
  one full-frame scoring that sum to it (finding 2);
* (PI decision, 2026-10-10) a reduced frame counts a detection if and only
  if its parent frame attributes it to one of the reduced frame's sheets:
  an origin seen only on a study sheet the frame leaves out is excluded,
  not re-keyed; one seen across the frame's edge is refused unless the
  parent frame is given (``parent_bounds``), which then governs; an unknown
  tile vocabulary keeps the ``source_tile`` fallback but warns. Astra's
  three counterexamples are regression tests below, and any partition of a
  frame into whole sheets sums exactly to it.
"""

from __future__ import annotations

import json
import logging
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


def test_a_cluster_seen_on_both_sheets_keeps_its_scoring_sheet(frame):
    """Members on A and B, scored on B: seen on B, so not a re-key.

    ``merge_passes.py`` sorts ``source_tiles``, so the first entry (A here)
    is alphabetical, not first-seen; privileging it would re-attribute the
    cluster arbitrarily. Only a sheet the detection was never seen on is a
    re-key.
    """
    d = dets([("B_x0_y0.png", 196, 50)],
             source_tiles=["['A_x100_y0.png' 'B_x0_y0.png']"])
    scope = lam.scope_detections_to_frame(d, frame)
    assert list(scope.sheets) == ["B"]
    assert scope.diagnostics["n_origin_restored"] == 0
    names, diag = lam.assign_primary_tiles_on_origin_sheet(d, frame)
    assert names == ["B_x0_y0.png"]
    assert diag["n_cross_sheet_avoided"] == 0


def test_a_cluster_named_on_a_sheet_that_does_not_hold_it_is_scored_where_it_lies(frame):
    """Members on A and B, named on A (first, alphabetical), lying only in B's tiles.

    ``materialise_pv_geojson.py`` writes ``source_tiles[0]`` into
    ``source_tile``. The cluster was seen on B and lies in B's tiles, so it
    is scored on B: neither out of frame nor a re-key.
    """
    d = dets([("A_x100_y0.png", 205, 50)],
             source_tiles=[["A_x100_y0.png", "B_x0_y0.png"]])
    scope = lam.scope_detections_to_frame(d, frame)
    assert list(scope.sheets) == ["B"]
    diag = scope.diagnostics
    assert (diag["n_origin_switched"], diag["n_out_of_frame"],
            diag["n_origin_restored"]) == (1, 0, 0)
    ref_b = gpd.GeoDataFrame({"Map": ["B"]}, geometry=[Point(206, 50)], crs=CRS)
    assert lam.calculate_f1_internal(d, ref_b, frame, 20) == (1.0, 1.0, 1.0)
    # The tile confusion keeps the row (it removes only out-of-frame rows).
    assert len(scope.retained) == 1


def test_a_single_origin_sheet_outside_its_tiles_is_not_switched(frame):
    """Seen only on A, lying only in B's tiles: out of frame, never moved to B."""
    d = dets([("A_x100_y0.png", 250, 50)], source_tiles=[["A_x100_y0.png"]])
    diag = lam.scope_detections_to_frame(d, frame).diagnostics
    assert (diag["n_origin_switched"], diag["n_out_of_frame"],
            diag["n_out_of_frame_cross_sheet"]) == (0, 1, 1)


def test_a_cluster_in_both_sheets_tiles_keeps_its_named_sheet(frame):
    """In the overlap band both origin sheets hold it: ``source_tile`` stands."""
    d = dets([("A_x100_y0.png", 195, 50)],
             source_tiles=[["A_x100_y0.png", "B_x0_y0.png"]])
    scope = lam.scope_detections_to_frame(d, frame)
    assert list(scope.sheets) == ["A"]
    assert scope.diagnostics["n_origin_switched"] == 0


def test_a_repr_origin_survives_a_geojson_round_trip(frame, refs, tmp_path):
    """Tier E's case end to end: the repr STRING property, written and read back.

    geopandas returns such a property as a one-element array holding the
    whole repr; the origin must still be parsed out of it.
    """
    path = tmp_path / "cell.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": [{
        "type": "Feature", "geometry": {"type": "Point", "coordinates": [196, 50]},
        "properties": {"source_tile": "B_x0_y0.png",
                       "source_tiles": "['A_x0_y0.png' 'A_x100_y0.png'\n 'A_x100_y0.png']"},
    }]}))
    d = gpd.read_file(path).set_crs(CRS, allow_override=True)
    assert lam.parse_tile_list(d["source_tiles"].iloc[0])[0] == "A_x0_y0.png"
    scope = lam.scope_detections_to_frame(d, frame)
    assert scope.diagnostics["n_origin_restored"] == 1
    assert list(scope.sheets) == ["A"]


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
    # Missing values of every spelling (PR #26 review, finding 2): pd.NA
    # used to read as the name '<NA>' and a NaN element as 'nan'.
    (pd.NA, []),
    (np.float64("nan"), []),
    (["a", float("nan"), pd.NA, "b"], ["a", "b"]),
    (np.array(["a", None, np.nan], dtype=object), ["a"]),
    ('["a", null, NaN]', ["a"]),
    ("[]", []),
    ("['']", []),
])
def test_parse_tile_list_reads_every_serialisation(value, expected):
    """Lists, JSON, NumPy repr, ';'-joined, bare names and missing values."""
    assert lam.parse_tile_list(value) == expected


@pytest.mark.parametrize("value, error", [
    ({"A_x0_y0.png"}, TypeError),                  # a set
    ({"a": "A_x0_y0.png"}, TypeError),             # a dict
    (7, TypeError),                                # a number
    (b"A_x0_y0.png", TypeError),                   # bytes
    (["A_x0_y0.png", 7], TypeError),               # a number inside a list
    ("[A_x0_y0.png, A_x100_y0.png]", ValueError),  # list text, unquoted
    ("[1, 2]", ValueError),                        # JSON, but not names
])
def test_parse_tile_list_refuses_what_no_serialisation_produces(value, error):
    """Never a bogus name, never a silent empty list (PR #26 review, finding 2)."""
    with pytest.raises(error, match="tile[- ]list"):
        lam.parse_tile_list(value)


def test_a_missing_origin_moves_the_search_to_the_next_column(frame, refs):
    """pd.NA in the first origin column is missing: the next column decides.

    Before the hardening it parsed as the name '<NA>', the search stopped
    there, the row counted as an unrecognised origin, and the re-key to B
    stood: one TP became an FP on B and an FN on A.
    """
    d = dets([("A_x0_y0.png", 51, 50), ("B_x0_y0.png", 196, 50),
              ("B_x100_y0.png", 301, 50)])
    d["origin_source_tile"] = pd.array([pd.NA, pd.NA, pd.NA], dtype="string")
    d["source_tiles"] = ['["A_x0_y0.png"]', '["A_x100_y0.png"]', '["B_x100_y0.png"]']
    diag = lam.scope_detections_to_frame(d, frame).diagnostics
    assert (diag["n_origin_restored"], diag["n_origin_unrecognised"]) == (1, 0)
    assert lam.calculate_f1_internal(d, refs, frame, 20) == (1.0, 1.0, 1.0)


def test_an_unparseable_origin_refuses_and_names_the_column_and_row(frame):
    """The scorer refuses a file it cannot read, and says where to look."""
    d = dets([("A_x0_y0.png", 51, 50), ("A_x0_y0.png", 52, 50)],
             origin_tiles=["A_x0_y0.png", "[A_x0_y0.png, A_x100_y0.png]"])
    with pytest.raises(ValueError, match="column 'origin_tiles', row 1"):
        lam.scope_detections_to_frame(d, frame)
    with pytest.raises(ValueError, match="column 'origin_tiles', row 1"):
        lam.origin_tiles_of(d)


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


def test_tier_e_regeneration_keeps_every_member_sheet(frame, tmp_path, monkeypatch):
    """Regenerating a tier E cell must not privilege the first member.

    PR #26 review, finding 3. A cluster seen on A's tile x200 (outside the
    frame) and B's tile x0 lies only in B's frame tile.
    ``materialise_pv_geojson.py`` promotes the alphabetically first member
    (A's) to ``source_tile``, and ``reassign_carrier_tiles`` used to copy it
    into ``origin_source_tile``, which is read first: the re-key then found
    no A tile holding the point and nulled it, and the scorer dropped the
    detection as out of frame. Under the any-member rule the report
    measured (§ 7 item 1) it is kept on B and matches B's reference. A row
    with no member list still keeps its single origin tile.
    """
    from scripts import run_k_ladder_tier_e as tier_e

    bounds = tmp_path / "bounds.geojson"
    frame.to_file(bounds, driver="GeoJSON")
    monkeypatch.setattr(tier_e, "BOARD_BOUNDS", str(bounds))

    def feature(x: float, source_tile: str, source_tiles: list | None) -> dict:
        """One materialised feature, as materialise_pv_geojson.py writes it."""
        return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [x, 50]},
                "properties": {"source_tile": source_tile, "source_tiles": source_tiles}}

    cell = tmp_path / "cell.geojson"
    cell.write_text(json.dumps({
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}},
        "features": [feature(251, "A_x200_y0.png", ["A_x200_y0.png", "B_x0_y0.png"]),
                     feature(51, "A_x0_y0.png", None)],
    }))
    assert tier_e.reassign_carrier_tiles(cell) == 2
    out = gpd.read_file(cell)
    assert list(out["source_tile"]) == ["B_x0_y0.png", "A_x0_y0.png"]
    assert out["origin_source_tile"].isna().tolist() == [True, False]
    assert out["origin_source_tile"].iloc[1] == "A_x0_y0.png"
    both = gpd.GeoDataFrame({"Map": ["B", "A"]},
                            geometry=[Point(250, 50), Point(50, 50)], crs=CRS)
    assert lam.scope_detections_to_frame(out, frame).diagnostics["n_out_of_frame"] == 0
    assert lam.calculate_f1_internal(out, both, frame, 20) == (1.0, 1.0, 1.0)


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
    # The switch counter is written per pass and summed like the others.
    assert block["n_origin_switched"] == 0
    assert summary["detection_scope"]["n_origin_switched"] == 0


def test_scope_columns_are_not_required_beyond_the_attribution(frame, refs):
    """A string-typed pandas column with NA behaves like None."""
    d = dets([("A_x0_y0.png", 51, 50), (None, 60, 60)])
    d["source_tile"] = d["source_tile"].astype(pd.StringDtype())
    scope = lam.scope_detections_to_frame(d, frame)
    assert scope.diagnostics["n_in_scope"] == 1
    assert scope.diagnostics["n_unattributed"] == 1


# ── The D50 review: prefix collisions and reduced frames ──────────────────


@pytest.fixture()
def prefix_frame() -> gpd.GeoDataFrame:
    """Sheet A's tile at x 0-100 and sheet AB's at x 200-300 (review, finding 3)."""
    return gpd.GeoDataFrame(
        {"tile_name": ["A_x0_y0.png", "AB_x0_y0.png"]},
        geometry=[box(0, 0, 100, 100), box(200, 0, 300, 100)],
        crs=CRS,
    )


def test_a_sheet_prefix_does_not_claim_the_longer_sheets_tiles(prefix_frame):
    """Finding 3: both sides use the longest-prefix assignment for sheet A's tiles.

    An A reference and an A-origin detection at (250, 50), inside AB's tile.
    The detection scope gives that tile to AB, so the detection is out of
    A's frame. ``iter_sheet_scopes`` used to select A's tiles with a bare
    ``startswith("A")``, which also took AB's tile, so the A reference
    stayed in scope as a false negative the detection side could never meet.
    """
    assert list(lam.frame_tile_sheets(prefix_frame)) == ["A", "AB"]
    refs = gpd.GeoDataFrame({"Map": ["A", "A", "AB"]},
                            geometry=[Point(50, 50), Point(250, 50), Point(260, 50)],
                            crs=CRS)
    d = dets([("A_x0_y0.png", 51, 50), ("A_x0_y0.png", 250, 50),
              ("AB_x0_y0.png", 261, 50)])
    scopes = {s: (det, ref, b) for s, det, ref, b in
              lam.iter_sheet_scopes(d, refs, prefix_frame)}
    det_a, ref_a, bounds_a = scopes["A"]
    assert bounds_a["tile_name"].tolist() == ["A_x0_y0.png"]
    assert det_a.index.tolist() == [0] and ref_a.index.tolist() == [0]
    det_ab, ref_ab, bounds_ab = scopes["AB"]
    assert bounds_ab["tile_name"].tolist() == ["AB_x0_y0.png"]
    assert det_ab.index.tolist() == [2] and ref_ab.index.tolist() == [2]
    diag = lam.scope_detections_to_frame(d, prefix_frame).diagnostics
    assert (diag["n_out_of_frame"], diag["n_out_of_frame_cross_sheet"]) == (1, 1)
    assert lam.per_sheet_confusion(d, refs, prefix_frame, 20) == {
        "A": (1, 0, 0), "AB": (1, 0, 0)}
    # Under the bare-prefix selection A scored (1, 0, 1): the A reference
    # in AB's tile was a false negative.
    assert lam.calculate_f1_internal(d, refs, prefix_frame, 20) == (1.0, 1.0, 1.0)


def test_frame_tile_sheets_selects_what_startswith_selected_without_collisions(frame):
    """Prefix-free sheet names: the canonical assignment is the old selection."""
    sheets = lam.frame_tile_sheets(frame)
    for sheet in lam.frame_sheets(frame):
        old = frame[frame["tile_name"].str.startswith(sheet)]
        new = frame[sheets == sheet]
        assert new.index.tolist() == old.index.tolist()


def test_study_sheet_names_are_prefix_free():
    """No study sheet is a prefix of another, so committed frames select as before."""
    names = sorted(lam.STUDY_SHEETS)
    assert len(names) == 59
    clashes = [(a, b) for a in names for b in names if a != b and b.startswith(a)]
    assert clashes == []


@pytest.fixture()
def two_sheet_refs() -> gpd.GeoDataFrame:
    """One reference on A and one on B, at the same point in the overlap band."""
    return gpd.GeoDataFrame({"Map": ["A", "B"]},
                            geometry=[Point(195, 50), Point(195, 50)], crs=CRS)


@pytest.fixture()
def wide_frame() -> gpd.GeoDataFrame:
    """Astra's frame: A's tile x 0-200 and B's tile x 190-390."""
    return gpd.GeoDataFrame(
        {"tile_name": ["A_x0_y0.png", "B_x0_y0.png"]},
        geometry=[box(0, 0, 200, 100), box(190, 0, 390, 100)],
        crs=CRS,
    )


def _sheet(frame_: gpd.GeoDataFrame, sheet: str) -> gpd.GeoDataFrame:
    """One sheet's tiles: a REDUCED frame."""
    return frame_[lam.frame_tile_sheets(frame_) == sheet]


def _total(counts: dict[str, tuple[int, int, int]]) -> tuple[int, int, int]:
    """Sum per-sheet (tp, fp, fn) triples."""
    return tuple(sum(c[i] for c in counts.values()) for i in range(3))


#: Astra's two cases (the D50 review, 2026-10-09): a detection seen only on
#: A and re-keyed to B's overlapping tile, and a cluster seen on A and B
#: that the materialiser named on A (the first, alphabetical, member).
ASTRA_CASES = [
    pytest.param("origin_tiles", "A_x0_y0.png", "B_x0_y0.png", id="single-origin"),
    pytest.param("source_tiles", '["A_x0_y0.png", "B_x0_y0.png"]', "A_x0_y0.png",
                 id="multi-origin"),
]


@pytest.mark.parametrize("origin_column, origin_value, source_tile", ASTRA_CASES)
def test_per_sheet_results_are_partitions_of_the_full_frame(
    wide_frame, two_sheet_refs, origin_column, origin_value, source_tile,
):
    """Finding 2: the full frame's per-sheet counts sum to its score.

    The full frame scores the detection on A: a TP on A and an FN on B.
    """
    d = dets([(source_tile, 195, 50)], **{origin_column: [origin_value]})
    full = lam.per_sheet_confusion(d, two_sheet_refs, wide_frame, 20)
    assert full == {"A": (1, 0, 0), "B": (0, 0, 1)}
    p, r, f = lam.calculate_f1_internal(d, two_sheet_refs, wide_frame, 20)
    assert _total(full) == (1, 0, 1)
    assert (p, r) == (1.0, 0.5)
    # The same per-sheet figures from a scope computed once and reused.
    scope = lam.scope_detections_to_frame(d, wide_frame)
    assert lam.per_sheet_confusion(scope, two_sheet_refs, wide_frame, 20) == full


@pytest.mark.parametrize("origin_column, origin_value, source_tile", ASTRA_CASES)
def test_reduced_frames_given_the_parent_sum_to_it(
    wide_frame, two_sheet_refs, origin_column, origin_value, source_tile,
):
    """The contract: a reduced frame counts a detection iff the parent puts it there.

    Astra's regression (``reduced_frames_partition``): scored on each
    sheet's tiles alone, the detection used to count on A AND on B. Given
    the full frame as ``parent_bounds``, each reduced frame scores exactly
    its partition of the full frame, for one origin and for several.
    """
    d = dets([(source_tile, 195, 50)], **{origin_column: [origin_value]})
    full = lam.scope_detections_to_frame(d, wide_frame)
    counts = []
    reduced: dict[str, tuple[int, int, int]] = {}
    for sheet in ("A", "B"):
        part = _sheet(wide_frame, sheet)
        scope = lam.scope_detections_to_frame(d, part, parent_bounds=wide_frame)
        counts.append(len(scope.detections))
        reduced.update(lam.per_sheet_confusion(
            d, two_sheet_refs, part, 20, parent_bounds=wide_frame))
        assert lam.calculate_f1_internal(
            d, two_sheet_refs, part, 20, parent_bounds=wide_frame,
        ) == lam.precision_recall_f1(*reduced[sheet])
    assert counts == [1, 0]
    assert sum(counts) == len(full.detections) == 1
    assert reduced == lam.per_sheet_confusion(d, two_sheet_refs, wide_frame, 20)
    only_b = lam.scope_detections_to_frame(
        d, _sheet(wide_frame, "B"), parent_bounds=wide_frame).diagnostics
    assert (only_b["n_parent_elsewhere"], only_b["n_parent_sheets"]) == (1, 2)
    assert only_b["n_in_scope"] == 0


@pytest.mark.parametrize("a, b, catalogue", [
    pytest.param("A", "B", ["A", "B"], id="synthetic-explicit-catalogue"),
    pytest.param("K-35-052-3", "K-35-052-4_32635", None, id="study-sheets-default"),
])
def test_an_out_of_frame_origin_is_excluded_not_rekeyed(a, b, catalogue):
    """Rule 1 (PI decision, 2026-10-10): no ``source_tile`` fallback for a real sheet.

    Astra's single-origin case on B's tiles alone: the detection was seen
    only on A, a catalogue sheet the frame leaves out, so it is excluded
    and counted, and the two reduced frames sum to the full frame. With
    real study sheets the default catalogue (:data:`STUDY_SHEETS`) applies.
    """
    bounds = gpd.GeoDataFrame(
        {"tile_name": [f"{a}_x0_y0.png", f"{b}_x0_y0.png"]},
        geometry=[box(0, 0, 200, 100), box(190, 0, 390, 100)], crs=CRS)
    d = dets([(f"{b}_x0_y0.png", 195, 50)], origin_tiles=[f"{a}_x0_y0.png"])
    full = lam.scope_detections_to_frame(d, bounds, sheet_catalogue=catalogue)
    on_a = lam.scope_detections_to_frame(
        d, _sheet(bounds, a), sheet_catalogue=catalogue)
    on_b = lam.scope_detections_to_frame(
        d, _sheet(bounds, b), sheet_catalogue=catalogue)
    assert [len(on_a.detections), len(on_b.detections)] == [1, 0]
    assert len(full.detections) == 1 and list(full.sheets) == [a]
    diag = on_b.diagnostics
    assert (diag["n_origin_excluded"], diag["n_origin_unrecognised"]) == (1, 1)
    assert (diag["n_in_scope"], diag["n_unattributed"], diag["n_out_of_frame"]) == (0, 0, 0)
    # Every row is accounted for exactly once.
    assert diag["n_detections"] == (diag["n_in_scope"] + diag["n_out_of_frame"]
                                    + diag["n_unattributed"] + diag["n_origin_excluded"])
    # The tile confusion still books the row (it is on no frame sheet).
    assert on_b.retained.index.tolist() == [0]


@pytest.mark.parametrize("a, b, catalogue", [
    pytest.param("A", "B", ["A", "B"], id="synthetic-explicit-catalogue"),
    pytest.param("K-35-052-3", "K-35-052-4_32635", None, id="study-sheets-default"),
])
def test_origins_across_the_frame_edge_are_refused_without_the_parent(
    a, b, catalogue, two_sheet_refs,
):
    """Rule 2: a cluster seen on both sides of the frame's edge is not guessed.

    Astra's multi-origin case: which sheet the full frame scores it on
    depends on the other sheet's tiles, which a reduced frame lacks. Every
    scoring entry point refuses, naming ``parent_bounds``; given the
    parent, the reduced frames sum to it.
    """
    bounds = gpd.GeoDataFrame(
        {"tile_name": [f"{a}_x0_y0.png", f"{b}_x0_y0.png"]},
        geometry=[box(0, 0, 200, 100), box(190, 0, 390, 100)], crs=CRS)
    refs = two_sheet_refs.assign(Map=[a, b])
    d = dets([(f"{a}_x0_y0.png", 195, 50)],
             origin_tiles=[f"{a}_x0_y0.png;{b}_x0_y0.png"])
    for sheet, other in ((a, b), (b, a)):
        part = _sheet(bounds, sheet)
        with pytest.raises(lam.ReducedFrameRefusalError, match="parent_bounds=") as err:
            lam.scope_detections_to_frame(d, part, sheet_catalogue=catalogue)
        assert (err.value.n_rows, err.value.positions) == (1, [0])
        assert err.value.sheets_left_out == [other]
        assert err.value.within_parent is False
        with pytest.raises(lam.ReducedFrameRefusalError):
            lam.calculate_f1_internal(d, refs, part, 20, sheet_catalogue=catalogue)
        with pytest.raises(lam.ReducedFrameRefusalError):
            lam.per_sheet_confusion(d, refs, part, 20, sheet_catalogue=catalogue)
        with pytest.raises(lam.ReducedFrameRefusalError):
            list(lam.iter_sheet_scopes(d, refs, part, sheet_catalogue=catalogue))
    counts = [
        len(lam.scope_detections_to_frame(
            d, _sheet(bounds, s), sheet_catalogue=catalogue,
            parent_bounds=bounds).detections)
        for s in (a, b)
    ]
    assert counts == [1, 0]
    governed = lam.scope_detections_to_frame(
        d, _sheet(bounds, a), sheet_catalogue=catalogue, parent_bounds=bounds,
    ).diagnostics
    # Seen across this frame's edge too; the parent decided.
    assert governed["n_origin_partly_excluded"] == 1


def test_a_parent_that_itself_leaves_a_sheet_out_is_refused(wide_frame):
    """The parent is only as good as its own sheets: it must not cut a cluster either."""
    d = dets([("A_x0_y0.png", 195, 50)],
             origin_tiles=["A_x0_y0.png;B_x0_y0.png;C_x0_y0.png"])
    with pytest.raises(lam.ReducedFrameRefusalError, match="FULL") as err:
        lam.scope_detections_to_frame(d, _sheet(wide_frame, "A"),
                                      sheet_catalogue=["A", "B", "C"],
                                      parent_bounds=wide_frame)
    assert err.value.within_parent is True and err.value.sheets_left_out == ["C"]


@pytest.fixture()
def three_sheet_frame() -> gpd.GeoDataFrame:
    """Sheets A, B and C, two tiles each; padded tiles overlap at each edge."""
    return gpd.GeoDataFrame(
        {"tile_name": ["A_x0_y0.png", "A_x100_y0.png", "B_x0_y0.png",
                       "B_x100_y0.png", "C_x0_y0.png", "C_x100_y0.png"]},
        geometry=[box(0, 0, 100, 100), box(100, 0, 200, 100),
                  box(190, 0, 290, 100), box(290, 0, 390, 100),
                  box(380, 0, 480, 100), box(480, 0, 580, 100)],
        crs=CRS,
    )


def test_every_sheet_partition_sums_to_the_parent(three_sheet_frame):
    """The contract as a property: any partition into whole sheets sums exactly.

    A mixed detection set: in-frame rows, re-keyed rows, clusters seen on
    two sheets (in each overlap band, named on either), a switch, a row
    out of frame, an unattributed row, and an unknown tile vocabulary.
    """
    rows = [
        ("A_x0_y0.png", 50, 50, None),                      # plain, on A
        ("B_x0_y0.png", 195, 50, "A_x100_y0.png"),          # re-keyed to B
        ("A_x100_y0.png", 195, 50, "A_x100_y0.png;B_x0_y0.png"),  # seen on A and B
        ("B_x0_y0.png", 195, 50, "A_x100_y0.png;B_x0_y0.png"),    # named on B
        ("B_x100_y0.png", 385, 50, "B_x100_y0.png;C_x0_y0.png"),  # seen on B and C
        ("A_x100_y0.png", 250, 50, "A_x100_y0.png;B_x0_y0.png"),  # switched to B
        ("C_x100_y0.png", 700, 50, None),                   # out of frame
        (None, 300, 50, None),                              # unattributed
        ("C_x0_y0.png", 450, 50, "Q-99_x0_y0.png"),         # unknown vocabulary
    ]
    d = dets([(s, x, y) for s, x, y, _ in rows], origin_tiles=[o for *_, o in rows])
    refs = gpd.GeoDataFrame(
        {"Map": ["A", "A", "B", "B", "C", "C"]},
        geometry=[Point(50, 50), Point(195, 50), Point(196, 50), Point(385, 50),
                  Point(386, 50), Point(450, 50)], crs=CRS)
    full = lam.per_sheet_confusion(d, refs, three_sheet_frame, 20)
    full_scope = lam.scope_detections_to_frame(d, three_sheet_frame)
    sheets = lam.frame_tile_sheets(three_sheet_frame)
    for partition in ([["A"], ["B"], ["C"]], [["A", "B"], ["C"]], [["A"], ["B", "C"]]):
        reduced: dict[str, tuple[int, int, int]] = {}
        kept: list[int] = []
        for group in partition:
            part = three_sheet_frame[np.isin(sheets.astype(str), group)]
            reduced.update(lam.per_sheet_confusion(
                d, refs, part, 20, parent_bounds=three_sheet_frame))
            scope = lam.scope_detections_to_frame(d, part, parent_bounds=three_sheet_frame)
            kept += scope.detections.index.tolist()
            for sheet in group:
                assert scope.on_sheet(sheet).index.tolist() == \
                    full_scope.on_sheet(sheet).index.tolist()
        assert reduced == full, partition
        assert sorted(kept) == sorted(full_scope.detections.index.tolist())


def test_the_full_frame_as_its_own_parent_changes_nothing(frame):
    """Passing the full frame as its own parent reproduces the plain scope exactly."""
    d = dets([("A_x0_y0.png", 50, 50), ("B_x0_y0.png", 195, 50),
              ("A_x100_y0.png", 500, 50), (None, 300, 50)],
             origin_tiles=[None, "A_x100_y0.png", None, None])
    plain = lam.scope_detections_to_frame(d, frame)
    governed = lam.scope_detections_to_frame(d, frame, parent_bounds=frame)
    assert governed.detections.index.tolist() == plain.detections.index.tolist()
    assert list(governed.sheets) == list(plain.sheets)
    assert governed.retained.index.tolist() == plain.retained.index.tolist()
    extra = {"n_parent_sheets": 2, "n_parent_elsewhere": 0}
    assert governed.diagnostics == {**plain.diagnostics, **extra}


def test_a_parent_must_contain_the_frame(wide_frame, frame):
    """A frame that is not part of the given parent is refused, not trusted."""
    d = dets([("A_x0_y0.png", 50, 50)])
    with pytest.raises(ValueError, match="not tiles of the parent"):
        lam.scope_detections_to_frame(d, frame, parent_bounds=wide_frame)
    moved = wide_frame.copy()
    moved.loc[moved.index[0], "geometry"] = box(0, 0, 150, 100)
    with pytest.raises(ValueError, match="different polygons"):
        lam.scope_detections_to_frame(d, _sheet(wide_frame, "A"), parent_bounds=moved)
    twice = pd.concat([wide_frame, wide_frame.iloc[[0]]])
    with pytest.raises(ValueError, match="repeat"):
        lam.scope_detections_to_frame(d, _sheet(wide_frame, "A"), parent_bounds=twice)
    scope = lam.scope_detections_to_frame(d, wide_frame)
    with pytest.raises(ValueError, match="already"):
        list(lam.iter_sheet_scopes(scope, gpd.GeoDataFrame(
            {"Map": []}, geometry=[], crs=CRS), wide_frame, parent_bounds=wide_frame))


def test_an_unknown_vocabulary_keeps_the_fallback_but_warns(wide_frame, caplog):
    """Rule 3: where the catalogue cannot see, the scorer says so.

    With synthetic sheets the default catalogue knows neither A nor B, so
    on B's tiles alone Astra's detection still falls back to ``source_tile``
    (the unknown-vocabulary rule the PI kept): the warning names the
    argument that would prevent a double count.
    """
    d = dets([("B_x0_y0.png", 195, 50)], origin_tiles=["A_x0_y0.png"])
    with caplog.at_level(logging.WARNING):
        scope = lam.scope_detections_to_frame(d, _sheet(wide_frame, "B"))
    assert len(scope.detections) == 1
    assert scope.diagnostics["n_origin_unrecognised"] == 1
    assert scope.diagnostics["n_origin_excluded"] == 0
    assert any("parent_bounds=" in r.getMessage() for r in caplog.records
               if r.levelno == logging.WARNING)
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        lam.scope_detections_to_frame(d, wide_frame)
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]


def test_the_catalogue_decides_excluded_versus_unknown(wide_frame):
    """The catalogue now moves rows: an identified sheet is excluded, an unknown one is not."""
    d = dets([("B_x0_y0.png", 195, 50)], source_tiles=['["A_x0_y0.png"]'])
    only_b = _sheet(wide_frame, "B")
    with_catalogue = lam.scope_detections_to_frame(d, only_b, sheet_catalogue=["A", "B"])
    without = lam.scope_detections_to_frame(d, only_b, sheet_catalogue=[])
    assert with_catalogue.detections.index.tolist() == []
    assert without.detections.index.tolist() == [0]
    assert with_catalogue.diagnostics["n_origin_excluded"] == 1
    assert without.diagnostics["n_origin_excluded"] == 0
    assert (with_catalogue.diagnostics["n_origin_unrecognised"]
            == without.diagnostics["n_origin_unrecognised"] == 1)


def test_the_default_catalogue_is_the_study_sheets():
    """A 55-map neighbour of a gold-standard sheet is excluded; a variant name is not."""
    gs = gpd.GeoDataFrame({"tile_name": ["K-35-052-4_32635_x0_y0.png"]},
                          geometry=[box(0, 0, 100, 100)], crs=CRS)
    d = dets([("K-35-052-4_32635_x0_y0.png", 50, 50)] * 2,
             origin_tiles=["K-35-052-3_x0_y0.png", "K-35-052-4_x0_y0.png"])
    diag = lam.scope_detections_to_frame(d, gs).diagnostics
    assert (diag["n_origin_unrecognised"], diag["n_origin_excluded"]) == (2, 1)
    # The K-35-052-3 row is excluded; the variant name falls back and stays.
    assert diag["n_in_scope"] == 1


@pytest.mark.parametrize("a, b, catalogue", [
    pytest.param("A", "B", ["A", "B"], id="synthetic-explicit-catalogue"),
    pytest.param("K-35-052-3", "K-35-052-4_32635", None, id="study-sheets-default"),
])
def test_the_materialiser_does_not_rekey_an_excluded_origin(a, b, catalogue):
    """Astra's ``materialiser_no_rekey``: an A-origin point gets no B tile on B alone.

    The full frame gives it A's tile. On B's tiles alone it gets ``None``,
    by rule 1 or by following the parent; a cluster seen on A and B is
    refused without the parent and follows it with one.
    """
    bounds = gpd.GeoDataFrame(
        {"tile_name": [f"{a}_x0_y0.png", f"{b}_x0_y0.png"]},
        geometry=[box(0, 0, 200, 100), box(190, 0, 390, 100)], crs=CRS)
    only_b = _sheet(bounds, b)
    point = gpd.GeoDataFrame({"origin_tiles": [f"{a}_x0_y0.png"]},
                             geometry=[Point(195, 50)], crs=CRS)
    full, _ = lam.assign_primary_tiles_on_origin_sheet(
        point, bounds, sheet_catalogue=catalogue)
    assert full == [f"{a}_x0_y0.png"]
    names, diag = lam.assign_primary_tiles_on_origin_sheet(
        point, only_b, sheet_catalogue=catalogue)
    assert names == [None]
    assert (diag["n_origin_excluded"], diag["n_assigned"]) == (1, 0)
    names, diag = lam.assign_primary_tiles_on_origin_sheet(
        point, only_b, sheet_catalogue=catalogue, parent_bounds=bounds)
    assert names == [None] and diag["n_parent_elsewhere"] == 1

    cluster = point.assign(origin_tiles=[f"{a}_x0_y0.png;{b}_x0_y0.png"])
    with pytest.raises(lam.ReducedFrameRefusalError, match="parent_bounds="):
        lam.assign_primary_tiles_on_origin_sheet(
            cluster, only_b, sheet_catalogue=catalogue)
    full, _ = lam.assign_primary_tiles_on_origin_sheet(
        cluster, bounds, sheet_catalogue=catalogue)
    parts = [
        lam.assign_primary_tiles_on_origin_sheet(
            cluster, _sheet(bounds, s), sheet_catalogue=catalogue,
            parent_bounds=bounds)[0][0]
        for s in (a, b)
    ]
    assert [t for t in parts if t is not None] == full


def test_primary_tiles_count_an_excluded_origin_apart(wide_frame):
    """The materialiser's counts: excluded (no tile), unknown (legacy), none (legacy)."""
    d = gpd.GeoDataFrame(
        {"origin_tiles": ["A_x0_y0.png", "Q-99_x0_y0.png", None]},
        geometry=[Point(195, 50)] * 3, crs=CRS)
    names, diag = lam.assign_primary_tiles_on_origin_sheet(
        d, _sheet(wide_frame, "B"), sheet_catalogue=["A", "B"])
    assert names == [None, "B_x0_y0.png", "B_x0_y0.png"]
    assert (diag["n_no_origin"], diag["n_origin_unrecognised"],
            diag["n_origin_excluded"], diag["n_origin_partly_excluded"],
            diag["n_assigned"]) == (3, 2, 1, 0, 2)
    _, full = lam.assign_primary_tiles_on_origin_sheet(
        d, wide_frame, sheet_catalogue=["A", "B"])
    assert (full["n_origin_excluded"], full["n_origin_partly_excluded"]) == (0, 0)


def test_the_h13_wrapper_warns_and_leaves_an_excluded_point_unassigned(caplog):
    """prepare_h13_scoring.assign_primary_tiles: no tile, and a WARNING, on a reduced frame."""
    from scripts import prepare_h13_scoring as h13

    bounds = gpd.GeoDataFrame(
        {"tile_name": ["K-35-052-3_x0_y0.png", "K-35-052-4_32635_x0_y0.png"]},
        geometry=[box(0, 0, 200, 100), box(190, 0, 390, 100)], crs=CRS)
    point = gpd.GeoDataFrame({"origin_tiles": ["K-35-052-3_x0_y0.png"]},
                             geometry=[Point(195, 50)], crs=CRS)
    with caplog.at_level(logging.WARNING):
        assigned = h13.assign_primary_tiles(point, bounds.iloc[[1]])
    assert assigned == [None]
    assert any("leaves out" in r.getMessage() for r in caplog.records
               if r.levelno == logging.WARNING)


def test_restoring_the_origin_can_lower_a_score(wide_frame):
    """Astra's non-monotonic example (passing): D50 is not an upward-only rule.

    Only a B reference. Without the recorded origin the detection is
    attributed by ``source_tile`` to B, as the pre-D50 named-sheet scorer
    attributed it, and matches: F1 1 (Astra ran the scorer at
    ``b3c52591d`` on this input and got (1.0, 1.0, 1.0)). With its origin
    restored to A it is an A false positive and the B reference a false
    negative: F1 0. The real corpus's direction is an empirical question.
    """
    refs = gpd.GeoDataFrame({"Map": ["B"]}, geometry=[Point(195, 50)], crs=CRS)
    named_only = dets([("B_x0_y0.png", 195, 50)])
    restored = dets([("B_x0_y0.png", 195, 50)], origin_tiles=["A_x0_y0.png"])
    assert lam.calculate_f1_internal(named_only, refs, wide_frame, 20) == (1.0, 1.0, 1.0)
    assert lam.calculate_f1_internal(restored, refs, wide_frame, 20) == (0, 0, 0)
    assert lam.per_sheet_confusion(restored, refs, wide_frame, 20) == {
        "A": (0, 1, 0), "B": (0, 0, 1)}


def test_the_evaluation_rolls_up_the_excluded_counts(wide_frame, two_sheet_refs):
    """evaluate_single_run writes the new counts; the multi-run summary sums them."""
    from scripts.evaluate_detections import evaluate_multi_run_mean, evaluate_single_run

    d = dets([("B_x0_y0.png", 195, 50)], origin_tiles=["K-35-052-3_x0_y0.png"])
    run = evaluate_single_run(d, two_sheet_refs, wide_frame, buffers=[20],
                              n_bootstrap=50, seed=1)
    assert run["detection_scope"]["n_origin_excluded"] == 1
    # Rule 1: seen only on a study sheet this frame leaves out, so excluded
    # (before 2026-10-10 it fell back to B and was scored there).
    assert run["detection_scope"]["n_in_scope"] == 0
    summary = evaluate_multi_run_mean([run, run], label="x")
    assert summary["detection_scope"]["n_origin_excluded"] == 2
    assert summary["detection_scope"]["n_origin_partly_excluded"] == 0


def test_heterogeneity_per_map_figures_decompose_the_full_frame(
    wide_frame, two_sheet_refs,
):
    """The 55-map per-map table reads partitions: B scores an FN, not a TP."""
    from scripts.analyse_55maps_heterogeneity import evaluate_per_map

    d = dets([("B_x0_y0.png", 195, 50)], origin_tiles=["A_x0_y0.png"])
    rows = {m.map_name: m for m in evaluate_per_map(d, two_sheet_refs, wide_frame, (20,))}
    assert (rows["A"].f1, rows["A"].n_dets) == (1.0, 1)
    # Scored on B's tiles alone this was F1 1.0 with one detection.
    assert (rows["B"].f1, rows["B"].recall, rows["B"].n_dets) == (0, 0, 0)


@pytest.mark.parametrize("module", ["analyse_secondary_effects",
                                    "analyse_secondary_effects_text"])
def test_secondary_effects_per_map_figures_decompose_the_full_frame(
    wide_frame, two_sheet_refs, monkeypatch, module,
):
    """Analysis 6 reads the same partitions in both secondary-effects scripts."""
    import importlib

    mod = importlib.import_module(f"scripts.{module}")
    d = dets([("B_x0_y0.png", 195, 50)], origin_tiles=["A_x0_y0.png"])
    monkeypatch.setattr(mod, "load_consensus_geojson", lambda _path, _bounds: d)
    out = mod.analyse_per_map_sheet({"c": {"consensus_dir": "unused"}}, {"c": 3},
                                    two_sheet_refs, wide_frame, buffer_m=20)
    assert out[0]["per_map"] == {"A": 1.0, "B": 0}


# ── Common-footprint bootstraps: each condition's frame is the parent ────


def test_the_common_footprint_bootstraps_follow_each_conditions_frame():
    """A footprint smaller than a condition's frame is scored with that frame as parent.

    Condition A is scored on two study sheets, condition B on the first
    alone, so the common footprint is a reduced frame of A's frame. A
    cluster seen on both sheets (rule 2) refuses there without the parent;
    with A's frame as parent the footprint's counts are A's partition of
    the full scoring, and every common-footprint bootstrap runs.
    """
    a, b = "K-35-052-3", "K-35-052-4_32635"
    bounds = gpd.GeoDataFrame(
        {"tile_name": [f"{a}_x0_y0.png", f"{b}_x0_y0.png"]},
        geometry=[box(0, 0, 200, 100), box(190, 0, 390, 100)], crs=CRS)
    only_a = _sheet(bounds, a)
    refs = gpd.GeoDataFrame({"Map": [a, b]}, geometry=[Point(195, 50)] * 2, crs=CRS)
    cluster = dets([(f"{a}_x0_y0.png", 195, 50)],
                   origin_tiles=[f"{a}_x0_y0.png;{b}_x0_y0.png"])
    plain = dets([(f"{a}_x0_y0.png", 195, 50)])
    with pytest.raises(lam.ReducedFrameRefusalError):
        lam.compute_per_tile_tp_fp_fn(cluster, refs, only_a)
    table = lam.compute_per_tile_tp_fp_fn(cluster, refs, only_a, parent_bounds=bounds)
    assert tuple(int(table[c].sum()) for c in ("tp", "fp", "fn")) == \
        lam.per_sheet_confusion(cluster, refs, bounds, 20)[a] == (1, 0, 0)
    assert lam._parent_of_cut(bounds, bounds) is None
    assert lam._parent_of_cut(bounds, only_a) is bounds
    effect = lam.bootstrap_effect_size_ci(cluster, bounds, plain, only_a, refs,
                                          n_iterations=20, random_seed=1)
    assert "error" not in effect and effect["f1_difference"]["mean"] == 0
    tile_effect = lam.bootstrap_tile_effect_size_ci(cluster, bounds, plain, only_a, refs,
                                                    n_iterations=20, random_seed=1)
    assert "error" not in tile_effect
    interaction = lam.bootstrap_interaction_ci(
        {("x", "1"): (cluster, bounds), ("x", "2"): (plain, only_a),
         ("y", "1"): (cluster, bounds), ("y", "2"): (plain, only_a)},
        refs, n_iterations=20, random_seed=1)
    assert "error" not in interaction
