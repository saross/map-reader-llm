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
  one full-frame scoring that sum to it, while a reduced frame's blind spot
  is counted apart from an unknown tile vocabulary (finding 2).
"""

from __future__ import annotations

import json
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


@pytest.mark.parametrize("origin_column, origin_value, source_tile", [
    # Single origin: seen on A only, re-keyed to B's overlapping tile.
    ("origin_tiles", "A_x0_y0.png", "B_x0_y0.png"),
    # Several origins: seen on A and on B; the materialiser named A first.
    ("source_tiles", '["A_x0_y0.png", "B_x0_y0.png"]', "A_x0_y0.png"),
])
def test_per_sheet_results_are_partitions_of_the_full_frame(
    wide_frame, two_sheet_refs, origin_column, origin_value, source_tile,
):
    """Finding 2: per-sheet counts sum to the full frame's; reduced frames do not.

    Astra's counterexample (single origin) and its two-sheet cluster twin.
    The full frame scores the detection on A: a TP on A and an FN on B.
    Scoring each sheet on its own tiles scores it on A AND on B: two TPs.
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

    # The hazard the partitions avoid, kept visible: each reduced frame
    # scores the detection on its own sheet, so the sheets over-count.
    reduced = {}
    for sheet in ("A", "B"):
        reduced.update(lam.per_sheet_confusion(
            d, two_sheet_refs, _sheet(wide_frame, sheet), 20))
    assert reduced == {"A": (1, 0, 0), "B": (1, 0, 0)}
    assert _total(reduced) != _total(full)


def test_a_reduced_frame_counts_an_excluded_origin_apart(wide_frame):
    """Finding 2's diagnostics: an excluded sheet is not an unknown vocabulary.

    On B's tiles alone: a row seen only on A (single origin) falls back to
    ``source_tile`` and is counted as excluded; a row seen on A and B is
    attributed to B and counted as partly excluded; a row whose origin is in
    a vocabulary the catalogue does not know stays merely unrecognised.
    """
    d = dets([("B_x0_y0.png", 195, 50), ("A_x0_y0.png", 195, 50),
              ("B_x0_y0.png", 300, 50)],
             source_tiles=['["A_x0_y0.png"]', '["A_x0_y0.png", "B_x0_y0.png"]',
                           '["Q-99_x0_y0.png"]'])
    only_b = _sheet(wide_frame, "B")
    diag = lam.scope_detections_to_frame(
        d, only_b, sheet_catalogue=["A", "B"]).diagnostics
    assert (diag["n_origin_unrecognised"], diag["n_origin_excluded"],
            diag["n_origin_partly_excluded"], diag["n_origin_only"]) == (2, 1, 1, 1)
    # The full frame excludes nothing.
    full = lam.scope_detections_to_frame(
        d, wide_frame, sheet_catalogue=["A", "B"]).diagnostics
    assert (full["n_origin_excluded"], full["n_origin_partly_excluded"]) == (0, 0)
    assert full["n_origin_unrecognised"] == 1


def test_the_catalogue_changes_only_the_diagnostics(wide_frame):
    """sheet_catalogue never moves a row: same rows, sheets and retained set."""
    d = dets([("B_x0_y0.png", 195, 50), ("A_x0_y0.png", 195, 50)],
             source_tiles=['["A_x0_y0.png"]', '["A_x0_y0.png", "B_x0_y0.png"]'])
    only_b = _sheet(wide_frame, "B")
    with_catalogue = lam.scope_detections_to_frame(d, only_b, sheet_catalogue=["A", "B"])
    without = lam.scope_detections_to_frame(d, only_b, sheet_catalogue=[])
    assert with_catalogue.detections.index.tolist() == without.detections.index.tolist()
    assert list(with_catalogue.sheets) == list(without.sheets)
    assert with_catalogue.retained.index.tolist() == without.retained.index.tolist()
    assert without.diagnostics["n_origin_excluded"] == 0
    assert with_catalogue.diagnostics["n_origin_excluded"] == 1


def test_the_default_catalogue_is_the_study_sheets():
    """A 55-map neighbour of a gold-standard sheet is identified; a variant name is not."""
    gs = gpd.GeoDataFrame({"tile_name": ["K-35-052-4_32635_x0_y0.png"]},
                          geometry=[box(0, 0, 100, 100)], crs=CRS)
    d = dets([("K-35-052-4_32635_x0_y0.png", 50, 50)] * 2,
             origin_tiles=["K-35-052-3_x0_y0.png", "K-35-052-4_x0_y0.png"])
    diag = lam.scope_detections_to_frame(d, gs).diagnostics
    assert (diag["n_origin_unrecognised"], diag["n_origin_excluded"]) == (2, 1)
    assert diag["n_in_scope"] == 2


def test_primary_tiles_count_an_excluded_origin_apart(wide_frame):
    """The materialiser's legacy fallback carries the same distinction."""
    d = gpd.GeoDataFrame(
        {"origin_tiles": ["A_x0_y0.png", "Q-99_x0_y0.png", None,
                          "A_x0_y0.png;B_x0_y0.png"]},
        geometry=[Point(195, 50)] * 4, crs=CRS)
    names, diag = lam.assign_primary_tiles_on_origin_sheet(
        d, _sheet(wide_frame, "B"), sheet_catalogue=["A", "B"])
    assert names == ["B_x0_y0.png"] * 4
    assert (diag["n_no_origin"], diag["n_origin_unrecognised"],
            diag["n_origin_excluded"], diag["n_origin_partly_excluded"]) == (3, 2, 1, 1)
    _, full = lam.assign_primary_tiles_on_origin_sheet(
        d, wide_frame, sheet_catalogue=["A", "B"])
    assert (full["n_origin_excluded"], full["n_origin_partly_excluded"]) == (0, 0)


def test_the_evaluation_rolls_up_the_excluded_counts(wide_frame, two_sheet_refs):
    """evaluate_single_run writes the new counts; the multi-run summary sums them."""
    from scripts.evaluate_detections import evaluate_multi_run_mean, evaluate_single_run

    d = dets([("B_x0_y0.png", 195, 50)], origin_tiles=["K-35-052-3_x0_y0.png"])
    run = evaluate_single_run(d, two_sheet_refs, wide_frame, buffers=[20],
                              n_bootstrap=50, seed=1)
    assert run["detection_scope"]["n_origin_excluded"] == 1
    summary = evaluate_multi_run_mean([run, run], label="x")
    assert summary["detection_scope"]["n_origin_excluded"] == 2
    assert summary["detection_scope"]["n_origin_partly_excluded"] == 0

