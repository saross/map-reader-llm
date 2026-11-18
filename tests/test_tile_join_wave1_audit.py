"""
Tier-1 tests for the G1 item 9 audit fix round (tile-join Wave 1).

The fresh-context audit of the Wave 1 code at ``02aea6ecd`` (lens A,
implementation; lens B, test adequacy), and Astra's interim reviews
(W1-C1 to W1-C3), found one real bug and several tests that could not fail.
Each test here is aimed at a named finding, and most at a named surviving
mutant of lens B's harness, so the mutant now dies. The record is
``reports/tile-join-wave-1/g1-audit.md``.

Fixtures are synthetic or the gold-standard (GS) frame; no 55-map data is
read. The synthetic seam frame comes from ``tests/test_perfect_detector.py``.

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-11-19 | Apache 2.0
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point, box

import scripts.lib_advanced_metrics as lam
from scripts.lib_advanced_metrics import (
    TILE_JOIN_REASON_DETECTION_SHORTFALL,
    TILE_JOIN_REASON_UNATTRIBUTED_DETECTION,
    TILE_JOIN_REASON_UNATTRIBUTED_REFERENCE,
    TileJoinProvenanceError,
    TileJoinRefusalError,
    calculate_f1_internal,
    calculate_tile_classification,
    compute_per_tile_tp_fp_fn,
    per_sheet_confusion,
    recorded_tile_joins,
)
from tests.test_perfect_detector import (
    CRS,
    ORIGIN_X,
    ORIGIN_Y,
    SHEET_A,
    SHEET_B,
    _tile,
    merged_detections,
    synthetic_bounds,
    synthetic_refs,
)

pytestmark = pytest.mark.tier1

REPO = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════════════════════════════════
# A fixture on which the two count tables, and the two classifications, differ
# ═══════════════════════════════════════════════════════════════════════════
#
# Merged detections named for the ALPHABETICALLY first own-sheet tile, with
# false positives in the overlaps. ``id`` books each by that name, while
# ``sheet-primary`` books it to the nearest centre (x = 95 is nearer A80's
# centre than A0's), so the per-tile tables, and the intervals resampled
# from them, differ. Measured on zbook before this test was written.

_DIFFER = [
    (50, 50, _tile(SHEET_A, 0, 0)), (90, 50, _tile(SHEET_A, 0, 0)),
    (170, 50, _tile(SHEET_A, 160, 0)), (250, 50, _tile(SHEET_B, 200, 0)),
    (95, 20, _tile(SHEET_A, 0, 0)), (97, 80, _tile(SHEET_A, 0, 0)),
    (165, 20, _tile(SHEET_A, 160, 0)), (290, 30, _tile(SHEET_B, 200, 0)),
    (40, 250, _tile(SHEET_A, 0, 200)),
]


def differing_detections() -> gpd.GeoDataFrame:
    """Detections whose ``id`` and ``sheet-primary`` count tables differ."""
    return gpd.GeoDataFrame(
        {"source_tile": [t for _, _, t in _DIFFER]},
        geometry=[Point(ORIGIN_X + x, ORIGIN_Y + y) for x, y, _ in _DIFFER], crs=CRS)


def _pt(x: float, y: float = 50.0) -> Point:
    return Point(ORIGIN_X + x, ORIGIN_Y + y)


def _write(gdf: gpd.GeoDataFrame, path: Path) -> Path:
    gdf.to_file(path, driver="GeoJSON")
    return path


# ═══════════════════════════════════════════════════════════════════════════
# B-C2, B-C3, B-M1: the evaluator, end to end through main()
# ═══════════════════════════════════════════════════════════════════════════


def _run_evaluator(tmp_path: Path, monkeypatch, name: str, extra: list[str]) -> dict:
    """Run ``evaluate_detections.main()`` through its real argument path."""
    from scripts import evaluate_detections as ed

    bounds = _write(synthetic_bounds(), tmp_path / "bounds.geojson")
    refs = _write(synthetic_refs(), tmp_path / "refs.geojson")
    det = _write(differing_detections(), tmp_path / "det.geojson")
    out = tmp_path / name
    monkeypatch.setattr(sys, "argv", [
        "evaluate_detections.py", "--detections", str(det), "--ground-truth", str(refs),
        "--bounds", str(bounds), "--buffers", "20", "--bootstrap", "200", "--seed", "42",
        "--mcc", "--output-dir", str(out), *extra])
    assert ed.main() == 0
    return json.loads((out / "evaluation.json").read_text())


class TestEvaluatorEndToEnd:

    @pytest.fixture
    def runs(self, tmp_path, monkeypatch) -> dict[str, dict]:
        return {
            "default": _run_evaluator(tmp_path, monkeypatch, "default", []),
            "id": _run_evaluator(tmp_path, monkeypatch, "id",
                                 ["--tile-join", "id", "--count-table-join", "id"]),
        }

    def test_point_estimates_identical_intervals_differ(self, runs):
        a, b = runs["default"]["summary"]["buffers"][0], runs["id"]["summary"]["buffers"][0]
        assert (a["f1"], a["precision"], a["recall"]) == (b["f1"], b["precision"], b["recall"])
        assert (a["p_ci_lower"], a["p_ci_upper"]) != (b["p_ci_lower"], b["p_ci_upper"])

    @pytest.mark.parametrize("which, ct", [("default", "sheet-primary"), ("id", "id")])
    def test_interval_values_are_the_named_count_tables(self, runs, which, ct):
        """The CLI's intervals equal the library's under the named rule (kills
        the mutants that drop count_table_join in _run_single_mode or at the
        bootstrap_ci call)."""
        row = runs[which]["summary"]["buffers"][0]
        ci = lam.bootstrap_ci(differing_detections(), synthetic_refs(), synthetic_bounds(),
                              n_iterations=200, random_seed=42, buffer_metres=20,
                              count_table_join=ct)
        assert row["count_table_join"] == ct
        for key, block in (("f1", "f1"), ("p", "precision"), ("r", "recall")):
            assert row[f"{key}_ci_lower"] == round(ci[block]["ci_lower"], 4)
            assert row[f"{key}_ci_upper"] == round(ci[block]["ci_upper"], 4)

    @pytest.mark.parametrize("which, join", [("default", "sheet-contains"), ("id", "id")])
    def test_mcc_interval_values_are_the_named_classification(self, runs, which, join):
        tile = runs[which]["summary"]["tile_classification"]
        ci = lam.bootstrap_tile_classification_ci(
            differing_detections(), synthetic_refs(), synthetic_bounds(),
            n_iterations=200, random_seed=42, tile_join=join)
        assert tile["tile_join"] == join
        assert tile["mcc"]["ci_lower"] == round(ci["mcc"]["ci_lower"], 4)
        assert tile["mcc"]["ci_upper"] == round(ci["mcc"]["ci_upper"], 4)

    def test_classifications_differ_on_the_fixture(self, runs):
        a = runs["default"]["summary"]["tile_classification"]["confusion"]
        b = runs["id"]["summary"]["tile_classification"]["confusion"]
        assert a != b

    @pytest.mark.parametrize("which, joins", [("default", ("sheet-contains", "sheet-primary")),
                                              ("id", ("id", "id"))])
    def test_metadata_records_the_command_line(self, runs, which, joins):
        """``_metadata`` reads the parsed arguments (kills meta_hardcoded)."""
        meta = runs[which]["_metadata"]
        assert (meta["tile_joins"]["classification"], meta["tile_joins"]["count_table"]) == joins
        assert meta["metadata_version"] == "1.5"
        rec = recorded_tile_joins(runs[which])
        assert (rec["classification"], rec["count_table"]) == joins


def test_unattributed_refusal_flows_through_the_evaluator():
    """F1 reported, intervals withheld with the reason, tile block withheld."""
    from scripts.evaluate_detections import evaluate_single_run

    bounds, refs = synthetic_bounds(), synthetic_refs()
    det = gpd.GeoDataFrame(geometry=list(refs.geometry), crs=CRS)
    det["source_tile"] = None
    run = evaluate_single_run(det, refs, bounds, [20], n_bootstrap=20, compute_mcc=True)
    assert run["tile_join_withheld"]["reason"] == TILE_JOIN_REASON_UNATTRIBUTED_DETECTION
    row = run["buffers"][0]
    assert row["ci_withheld"] is True and row["f1_ci_lower"] is None
    assert row["f1"] == 0.0  # the unattributed rows reach no sheet's matching
    assert run["tile_classification"]["withheld"] is True
    assert run["tile_classification"]["withheld_reason"] == (
        TILE_JOIN_REASON_UNATTRIBUTED_DETECTION)


def test_a_m1_id_count_table_keeps_the_historical_probe():
    """(geometric-contains, id) on a matched vocabulary is not over-withheld."""
    from scripts.evaluate_detections import evaluate_single_run

    bounds, refs = synthetic_bounds(), synthetic_refs()
    det = merged_detections(refs, bounds).drop(columns="source_tiles")
    det.loc[det.index[0], "source_tile"] = None  # in frame, no attribution
    run = evaluate_single_run(det, refs, bounds, [20], n_bootstrap=20, compute_mcc=True,
                              tile_join="geometric-contains", count_table_join="id")
    assert "tile_join_withheld" not in run
    assert run["buffers"][0]["f1_ci_lower"] is not None


# ═══════════════════════════════════════════════════════════════════════════
# B-C4: sheet-primary booking through the count table itself
# ═══════════════════════════════════════════════════════════════════════════


def _fp_table(points: list[tuple[float, float]], bounds: gpd.GeoDataFrame,
              name: str) -> pd.DataFrame:
    det = gpd.GeoDataFrame({"source_tile": [name] * len(points)},
                           geometry=[_pt(x, y) for x, y in points], crs=CRS)
    empty_refs = gpd.GeoDataFrame({"Map": pd.Series([], dtype=object)}, geometry=[], crs=CRS)
    return compute_per_tile_tp_fp_fn(det, empty_refs, bounds, 20).set_index("tile_name")


class TestSheetPrimaryBooking:

    def test_nearest_centre_wins_on_both_sides(self):
        """x = 85 is nearer A0's centre, x = 95 nearer A80's; detections (FP)
        and unmatched references (FN) are each booked there (kills the
        last-candidate mutant and the reference-side-only mutant)."""
        bounds = synthetic_bounds()
        det = gpd.GeoDataFrame({"source_tile": [_tile(SHEET_A, 0, 0)] * 2},
                               geometry=[_pt(85, 20), _pt(95, 20)], crs=CRS)
        refs = gpd.GeoDataFrame({"Map": [SHEET_A, SHEET_A]},
                                geometry=[_pt(85, 90), _pt(95, 90)], crs=CRS)
        table = compute_per_tile_tp_fp_fn(det, refs, bounds, 5).set_index("tile_name")
        a0, a80 = _tile(SHEET_A, 0, 0), _tile(SHEET_A, 80, 0)
        assert (table.loc[a0, "fp"], table.loc[a80, "fp"]) == (1, 1)
        assert (table.loc[a0, "fn"], table.loc[a80, "fn"]) == (1, 1)

    def test_a_tile_the_point_does_not_intersect_is_never_booked(self):
        """T2's centre is nearer the point, but the point is not in T2."""
        bounds = gpd.GeoDataFrame(
            {"tile_name": [_tile(SHEET_A, 0, 0), _tile(SHEET_A, 101, 0)]},
            geometry=[box(ORIGIN_X, ORIGIN_Y, ORIGIN_X + 100, ORIGIN_Y + 100),
                      box(ORIGIN_X + 101, ORIGIN_Y, ORIGIN_X + 110, ORIGIN_Y + 10)],
            crs=CRS)
        table = _fp_table([(99, 5)], bounds, _tile(SHEET_A, 0, 0))
        assert table.loc[_tile(SHEET_A, 0, 0), "fp"] == 1
        assert table.loc[_tile(SHEET_A, 101, 0), "fp"] == 0

    @pytest.mark.parametrize("order", ["sorted", "reversed", "shuffled"])
    def test_tie_goes_to_the_smaller_name_through_the_count_table(self, order):
        """x = 90 is equidistant from A0's and A80's centres. The bounds are
        given in an order that defeats any reliance on input order."""
        bounds = synthetic_bounds()
        if order == "reversed":
            bounds = bounds.iloc[::-1].reset_index(drop=True)
        elif order == "shuffled":
            bounds = bounds.sample(frac=1.0, random_state=3).reset_index(drop=True)
        table = _fp_table([(90, 50)], bounds, _tile(SHEET_A, 0, 0))
        assert table.loc[_tile(SHEET_A, 0, 0), "fp"] == 1
        assert table.loc[_tile(SHEET_A, 80, 0), "fp"] == 0

    def test_list_valued_source_tiles_as_lib_consensus_writes_them(self):
        """``source_tiles`` as a Python list (lib_consensus) and as JSON text
        (the materialised files) attribute identically."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        as_text = merged_detections(refs, bounds)
        as_list = as_text.copy()
        as_list["source_tiles"] = [json.loads(v) for v in as_text["source_tiles"]]
        a = compute_per_tile_tp_fp_fn(as_text, refs, bounds, 20)
        b = compute_per_tile_tp_fp_fn(as_list, refs, bounds, 20)
        pd.testing.assert_frame_equal(a, b)

    def test_a_cross_sheet_merged_point_books_on_one_sheet(self):
        """A merged point seen on both sheets is booked once, on the sheet D50
        attributes it to, under both sheet joins."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        b_row = det.index[3]  # the B mound at x = 250, inside A160 and A240 too
        det.loc[b_row, "source_tiles"] = json.dumps(
            [_tile(SHEET_A, 160, 0), _tile(SHEET_B, 200, 0)])
        det.loc[b_row, "source_tile"] = _tile(SHEET_A, 160, 0)
        scope = lam.scope_detections_to_frame(det, bounds)
        sheet = scope.sheets[list(scope.detections.index).index(b_row)]
        table = compute_per_tile_tp_fp_fn(det, refs, bounds, 20).set_index("tile_name")
        assert int(table["tp"].sum() + table["fp"].sum()) == len(det)
        booked = [t for t in table.index if table.loc[t, "tp"] + table.loc[t, "fp"] > 0
                  and abs(bounds.set_index("tile_name").loc[t].geometry.centroid.x
                          - (ORIGIN_X + 250)) < 60]
        assert all(t.startswith(sheet) for t in booked)


# ═══════════════════════════════════════════════════════════════════════════
# B-M2, A-M4: the provenance reader, every purpose and record location
# ═══════════════════════════════════════════════════════════════════════════


class TestProvenanceReader:

    def test_count_table_contradiction_is_rejected(self):
        doc = {"summary": {"buffers": [{"count_table_join": "sheet-primary"}]},
               "_metadata": {"cli_args": {"count_table_join": "id"}}}
        with pytest.raises(TileJoinProvenanceError, match="contradictory count_table"):
            recorded_tile_joins(doc)

    def test_per_run_records_are_read(self):
        doc = {"summary": {}, "per_run": [
            {"tile_classification": {"tile_join": "geometric-contains"},
             "buffers": [{"count_table_join": "geometric-primary"}]}]}
        rec = recorded_tile_joins(doc)
        assert (rec["classification"], rec["count_table"]) == (
            "geometric-contains", "geometric-primary")

    def test_per_run_contradiction_is_rejected(self):
        doc = {"summary": {"tile_classification": {"tile_join": "id"}},
               "per_run": [{"tile_classification": {"tile_join": "sheet-contains"}}]}
        with pytest.raises(TileJoinProvenanceError, match="contradictory classification"):
            recorded_tile_joins(doc)

    def test_buffer_rows_are_read(self):
        doc = {"summary": {"buffers": [{"count_table_join": "sheet-primary"},
                                       {"count_table_join": "sheet-primary"}]}}
        assert recorded_tile_joins(doc)["count_table"] == "sheet-primary"

    def test_metadata_block_is_read(self):
        doc = {"summary": {}, "_metadata": {"tile_joins": {
            "classification": "sheet-contains", "count_table": "id"}}}
        rec = recorded_tile_joins(doc)
        assert (rec["classification"], rec["count_table"]) == ("sheet-contains", "id")

    @pytest.mark.parametrize("missing", ["classification", "count_table"])
    def test_a_new_output_missing_one_rule_is_rejected(self, missing):
        block = {"classification": "sheet-contains", "count_table": "sheet-primary"}
        block.pop(missing)
        doc = {"summary": {}, "_metadata": {"metadata_version": "1.5", "tile_joins": block}}
        with pytest.raises(TileJoinProvenanceError, match=missing):
            recorded_tile_joins(doc)

    @pytest.mark.parametrize("block", [
        {"classification": "sheet-primary", "count_table": "sheet-contains"},
        {"classification": "bogus", "count_table": "id"},
        {"classification": "id", "count_table": "geometric-contains"},
    ])
    def test_a_name_of_the_wrong_purpose_is_rejected(self, block):
        """Audit A-M4."""
        with pytest.raises(TileJoinProvenanceError, match="invalid recorded tile join"):
            recorded_tile_joins({"summary": {}, "_metadata": {"tile_joins": block}})

    def test_recorded_join_flags(self):
        doc = {"summary": {"tile_classification": {"tile_join": "geometric-contains"}}}
        assert lam.recorded_join_flags(doc) == [
            "--tile-join", "geometric-contains", "--count-table-join", "id"]


# ═══════════════════════════════════════════════════════════════════════════
# B-M3: wrapper provenance
# ═══════════════════════════════════════════════════════════════════════════


def _stub_cells(n_tiles: int = 6) -> tuple[list[dict], list[str]]:
    rng = np.random.default_rng(0)
    tile_order = [f"S_x{i}_y0.png" for i in range(n_tiles)]
    cells = []
    for ref in ("r::a", "r::b"):
        tp, fp, fn = (rng.integers(0, 3, n_tiles).astype(float) for _ in range(3))
        cells.append({"ref": ref, "label": ref.split("::")[1], "kind": "consensus",
                      "tp": tp, "fp": fp, "fn": fn, "n_passes": 1, "eval_f1": 0.5,
                      "observed_micro_f1": 0.5, "f1_gap": 0.0, "mcc": None,
                      "validation": {"identity": {"status": "not recorded"}}})
    return cells, tile_order


class TestWrapperProvenance:

    def _run_era1(self, tmp_path, monkeypatch, extra: list[str]) -> int:
        from scripts import era1_leaderboard_tiering as t

        cells, order = _stub_cells()
        monkeypatch.setattr(t, "load_cells",
                            lambda *a, **k: (cells, None, None, order))
        monkeypatch.setattr(sys, "argv", [
            "era1_leaderboard_tiering.py", "--analysis-id", "x",
            "--output-dir", str(tmp_path), "--n-permutations", "20", *extra])
        return t.main()

    def test_era1_records_both_rules_and_validation(self, tmp_path, monkeypatch):
        assert self._run_era1(tmp_path, monkeypatch, []) == 0
        out = json.loads((tmp_path / "tiering_20m.json").read_text())
        assert out["tile_joins"]["classification"] == "sheet-contains"
        assert out["tile_joins"]["count_table"] == "sheet-primary"
        assert set(out["validation"]) == {"r::a", "r::b"}

    def test_era1_refuses_to_overwrite_another_rules_tiering(self, tmp_path, monkeypatch):
        """Audit A-L5: a legacy (id) tiering under the plain name is kept."""
        legacy = tmp_path / "tiering_20m.json"
        legacy.write_text(json.dumps({"ranking": []}))
        with pytest.raises(SystemExit, match="refusing to overwrite"):
            self._run_era1(tmp_path, monkeypatch, [])
        assert json.loads(legacy.read_text()) == {"ranking": []}
        assert self._run_era1(tmp_path, monkeypatch, ["--overwrite-other-joins"]) == 0

    def test_clipped_prepare_header_names_the_tierings(self):
        from scripts import k_ladder_clipped_cells as kcc

        args = argparse.Namespace(tile_join="id", count_table_join="id")
        header = kcc.prepare_header(args)
        assert header["tile_joins"]["classification"] == "id"
        assert kcc._tiering_file(header) == "tiering_20m_id_ct-id.json"
        default = kcc.prepare_header(argparse.Namespace(
            tile_join="sheet-contains", count_table_join="sheet-primary"))
        assert kcc._tiering_file(default) == "tiering_20m.json"

    def test_pareto_header_records_both(self):
        from scripts import build_pareto_v2 as bp

        assert bp.pareto_header("id", "sheet-primary")["tile_joins"] == {
            "classification": "id", "count_table": "sheet-primary",
            "rulings": lam.TILE_JOIN_RULINGS}

    def test_mcc_board_end_to_end_on_a_synthetic_frame(self, tmp_path, monkeypatch):
        """The board validates under the recorded join, computes under the
        requested one, records it, renders a null MCC (A-L2), reads a Track-2
        record's join (A-M2), and refuses an overwrite (A-L5)."""
        from scripts import mcc_tiering_55map as m

        bounds, refs = synthetic_bounds(), synthetic_refs("source_map")
        bounds_path = _write(bounds, tmp_path / "bounds.geojson")
        dets = {"a": merged_detections(refs, bounds, "source_map"),
                "b": merged_detections(refs, bounds, "source_map").iloc[:3]}
        # Cell b predicts every tile populated: a degenerate confusion under
        # the requested join (TN + FN = 0), whose MCC must be null (E81).
        centres = [g.centroid for g in bounds.geometry]
        dets["b"] = gpd.GeoDataFrame({"source_tile": list(bounds["tile_name"])},
                                     geometry=centres, crs=CRS)

        def load(cell_dir: Path):
            det = dets[cell_dir.name]
            rec = calculate_tile_classification(det, refs, bounds, tile_join="id")
            return det, {k: rec[k] for k in ("tp", "tn", "fp", "fn")} | {
                "mcc": rec["mcc"], "mcc_CI": None, "sensitivity": rec["sensitivity"],
                "specificity": rec["specificity"], "recorded_tile_join": "id"}

        monkeypatch.setattr(m, "BASE_DIR", tmp_path)
        monkeypatch.setattr(m, "OUT_DIR", tmp_path / "out")
        monkeypatch.setattr(m, "BOUNDS", bounds_path)
        monkeypatch.setattr(m, "TRACK2_R2", tmp_path / "r2")
        monkeypatch.setattr(m, "CELLS", {"a": "a", "b": "b"})
        monkeypatch.setattr(m, "r2_gt", lambda: refs)
        monkeypatch.setattr(m, "_load_cell_inputs", load)
        assert m.main(reference="r2") == 0
        out = json.loads((tmp_path / "out" / "55map-mcc-tiering-r2.json").read_text())
        assert out["tile_joins"]["classification"] == "sheet-contains"
        by_name = {c["name"]: c for c in out["cells"]}
        assert by_name["a"]["mcc"] == pytest.approx(1.0)
        assert by_name["b"]["mcc"] is None
        assert "undefined" in (tmp_path / "out" / "55map-mcc-tiering-r2.md").read_text()
        written = tmp_path / "out" / "55map-mcc-tiering-r2.json"
        doc = json.loads(written.read_text())
        doc["tile_joins"]["classification"] = "id"
        written.write_text(json.dumps(doc))
        with pytest.raises(SystemExit, match="refusing to overwrite"):
            m.main(reference="r2")
        # The Track-2 summary.json reader (A-M2).
        row = {"tile_classification": {"tile_join": "sheet-contains"}}
        assert m._track2_recorded_join({}, row) == "sheet-contains"
        assert m._track2_recorded_join({}, {"tile_classification": {}}) == "id"
        with pytest.raises(ValueError, match="contradictory"):
            m._track2_recorded_join(
                {"metadata": {"tile_joins": {"classification": "id"}}}, row)


# ═══════════════════════════════════════════════════════════════════════════
# B-M4: joins applied, not only recorded
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("join", ["id", "sheet-primary"])
def test_corrected_f1_intervals_use_the_named_count_table(monkeypatch, join):
    from scripts import compute_corrected_f1_multi_buffer as cc

    seen: list[str] = []
    real = cc.compute_per_tile_tp_fp_fn

    def spy(*args, **kwargs):
        seen.append(kwargs.get("tile_join"))
        return real(*args, **kwargs)

    monkeypatch.setattr(cc, "compute_per_tile_tp_fp_fn", spy)
    bounds, refs = synthetic_bounds(), synthetic_refs("source_map")
    cc.bootstrap_tile_level_ci(differing_detections(), refs, bounds, 20, 20, 1,
                               count_table_join=join)
    assert seen == [join]


def test_selection_aware_board_f1_threads_the_count_table(tmp_path, monkeypatch):
    import scripts.selection_aware_intervals as sai

    seen: dict[str, Any] = {}
    counts = np.zeros((2, 3, 3))
    counts[0, 0, 0] = counts[1, 1, 0] = counts[1, 2, 1] = 1

    def fake_counts(*args, count_table_join=None, **kwargs):
        seen["ct"] = count_table_join
        return [{"label": "a"}, {"label": "b"}], counts, np.array([True, True, False])

    monkeypatch.setattr(sai, "build_board_tile_counts", fake_counts)
    monkeypatch.setattr(sys, "argv", ["sai", "--board", "b1", "--count-table-join", "id",
                                      "--bootstrap", "20", "--out", str(tmp_path)])
    assert sai.main() == 0
    assert seen["ct"] == "id"


# ═══════════════════════════════════════════════════════════════════════════
# B-M5: every library call site names its join, or is allowed to inherit
# ═══════════════════════════════════════════════════════════════════════════

#: Join-bearing callables: (keyword, positional index or None).
_JOIN_CALLS: dict[str, list[tuple[str, int | None]]] = {
    "compute_per_tile_tp_fp_fn": [("tile_join", 4)],
    "calculate_tile_classification": [("tile_join", 3)],
    "bootstrap_tile_classification_ci": [("tile_join", 5)],
    "compute_per_tile_classification": [("tile_join", 3)],
    "bootstrap_tile_effect_size_ci": [("tile_join", 7)],
    "score_detection_set": [("tile_join", 5)],
    "describe_tile_join_refusal": [("tile_join", 3)],
    "bootstrap_ci": [("count_table_join", 8)],
    "bootstrap_effect_size_ci": [("count_table_join", 9)],
    "bootstrap_multi_run_ci": [("count_table_join", 6)],
    "bootstrap_multi_run_effect_size_ci": [("count_table_join", 8)],
    "bootstrap_interaction_ci": [("count_table_join", 8)],
    "generate_report": [("count_table_join", 4)],
}

#: Call sites that may inherit a default, each with its reason.
_ALLOWED: dict[tuple[str, str], str] = {
    ("scripts/lib_advanced_metrics.py", "generate_report"):
        "the library's own report helper; its callers choose the rule",
}


def _join_call_violations() -> list[str]:
    violations = []
    for path in sorted((REPO / "scripts").glob("*.py")):
        rel = str(path.relative_to(REPO))
        tree = ast.parse(path.read_text())
        defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name not in _JOIN_CALLS:
                continue
            if rel != "scripts/lib_advanced_metrics.py" and name in defined:
                continue  # a local function of the same name
            kws = {k.arg for k in node.keywords}
            if None in kws:
                continue  # **kwargs passes a join through explicitly
            if name == "score_detection_set" and any(
                    k.arg == "compute_mcc" and isinstance(k.value, ast.Constant)
                    and k.value.value is False for k in node.keywords):
                continue  # point estimates only: no table, no classification
            for kw, pos in _JOIN_CALLS[name]:
                if kw in kws or (pos is not None and len(node.args) > pos):
                    continue
                if (rel, name) in _ALLOWED:
                    continue
                violations.append(f"{rel}:{node.lineno} {name} without {kw}")
    return violations


def test_every_library_call_names_its_join():
    """Audit B-M5: a pinned site cannot quietly lose its pin."""
    assert _join_call_violations() == []


#: The launchers of W1-fixed tools pinned to history (dispositions file).
_PINNED_LAUNCHERS = [
    "build_gs_era2_board_opmax.py", "build_k1_gapfill_worklist.py",
    "build_verifier_pairing_worklist.py", "grid_materialise_conditions.py",
    "grid_verifier_analysis.py", "r2_score_cells.py", "recovery_reeval.py",
    "register_pass1_materialise.py", "rescore_conditions.py", "run_era1_pv_stage_d.py",
    "run_generalisation.py", "run_k_ladder_tier_e.py", "score_k_ladder_phase2_rungs.py",
    "tier_e_ladder_tiering.py", "run_bootstrap_10k.py", "stride55_score.py",
]


@pytest.mark.parametrize("name", _PINNED_LAUNCHERS)
def test_pinned_launchers_name_the_legacy_rules(name):
    """Audit A-M3 and the main session's launcher decision."""
    assert "*LEGACY_JOIN_FLAGS" in (REPO / "scripts" / name).read_text()


@pytest.mark.parametrize("name", ["rerun_bca_corpus.py", "rerun_evals_at_10k.py"])
def test_record_replay_launchers_use_the_recorded_rules(name):
    assert "*recorded_join_flags(doc)" in (REPO / "scripts" / name).read_text()


def test_shell_launcher_and_null_exemplar_are_pinned():
    sh = (REPO / "scripts/score-unscored-conditions-2026-05-30.sh").read_text()
    assert "--tile-join id --count-table-join id" in sh
    ne = (REPO / "scripts/analyse_null_exemplar_sensitivity.py").read_text()
    assert '"--tile-join", "id", "--count-table-join", "id"' in ne


def test_rerun_bca_corpus_command_carries_the_records_rules():
    from scripts import rerun_bca_corpus as rb

    doc = {"summary": {"tile_classification": {"tile_join": "geometric-contains"},
                       "buffers": [{"buffer_metres": 20}]},
           "_metadata": {"cli_args": {"detections": ["d.geojson"]}}}
    recipe = {"detections": ["d.geojson"], "ground_truth": "g", "bounds": "b"}
    cmd = rb.build_command(doc, recipe, Path("w"))
    i = cmd.index("--tile-join")
    assert cmd[i:i + 4] == ["--tile-join", "geometric-contains", "--count-table-join", "id"]


# ═══════════════════════════════════════════════════════════════════════════
# B-M6: replicated runs that differ, so the three quantities differ
# ═══════════════════════════════════════════════════════════════════════════


def test_replicated_runs_mean_pooled_and_run_1_are_distinct():
    from scripts.evaluate_detections import evaluate_multi_run_mean, evaluate_single_run

    bounds, refs = synthetic_bounds(), synthetic_refs()
    full = merged_detections(refs, bounds)
    runs_det = [full, full.iloc[:3], differing_detections()]
    runs = [evaluate_single_run(d.copy(), refs, bounds, [20], n_bootstrap=20, seed=42,
                                label=f"r{i}", compute_mcc=True)
            for i, d in enumerate(runs_det, 1)]
    summary = evaluate_multi_run_mean(runs, label="rep")
    f1s = [r["buffers"][0]["f1"] for r in runs]
    assert len(set(f1s)) == 3
    assert summary["buffers"][0]["f1"] == round(float(np.mean(f1s)), 4)
    assert summary["buffers"][0]["f1"] != f1s[0]
    tile = summary["tile_classification"]
    assert tile["confusion_source"] == "run_1"
    assert tile["confusion"] == runs[0]["tile_classification"]["confusion"]
    assert tile["confusion"] != runs[2]["tile_classification"]["confusion"]
    points = [r["tile_classification"]["mcc"]["point"] for r in runs]
    assert tile["mcc"]["point"] == round(float(np.mean(points)), 4)
    # Pooled counts: the symbol totals summed over passes, each pass's own.
    pooled = np.sum([np.sum(list(per_sheet_confusion(d, refs, bounds, 20).values()), axis=0)
                     for d in runs_det], axis=0)
    first = np.sum(list(per_sheet_confusion(full, refs, bounds, 20).values()), axis=0)
    assert tuple(pooled) != tuple(3 * first)
    tables = [compute_per_tile_tp_fp_fn(d, refs, bounds, 20) for d in runs_det]
    assert tuple(sum(t[["tp", "fp", "fn"]].to_numpy().sum(axis=0) for t in tables)) == \
        tuple(pooled)


# ═══════════════════════════════════════════════════════════════════════════
# Lows: mixing guards
# ═══════════════════════════════════════════════════════════════════════════


def test_passes_with_different_count_tables_cannot_be_averaged():
    from scripts.evaluate_detections import evaluate_multi_run_mean

    row = {"buffer_metres": 20, "f1": 0.5, "count_table_join": "id"}
    runs = [{"buffers": [dict(row)]}, {"buffers": [dict(row, count_table_join="sheet-primary")]}]
    with pytest.raises(ValueError, match="different count-table joins"):
        evaluate_multi_run_mean(runs)


def test_passes_with_different_classifications_cannot_be_averaged():
    from scripts.evaluate_detections import aggregate_tile_classification

    blocks = [{"tile_join": "id", "mcc": {"point": 0.5}},
              {"tile_join": "sheet-contains", "mcc": {"point": 0.5}}]
    with pytest.raises(ValueError, match="different classification joins"):
        aggregate_tile_classification(blocks)


# ═══════════════════════════════════════════════════════════════════════════
# References with no sheet (main-session decision on Astra's recommendation)
# ═══════════════════════════════════════════════════════════════════════════


class TestUnattributedReferences:

    def _refs_with_blank(self, value: Any) -> gpd.GeoDataFrame:
        refs = synthetic_refs()
        refs["Map"] = refs["Map"].astype(object)
        refs.loc[refs.index[0], "Map"] = value
        return refs

    @pytest.mark.parametrize("value", [None, "", "  "])
    def test_an_in_frame_reference_with_no_sheet_is_refused(self, value):
        bounds = synthetic_bounds()
        refs = self._refs_with_blank(value)
        det = merged_detections(synthetic_refs(), bounds)
        result = calculate_tile_classification(det, refs, bounds)
        assert result["reason"] == TILE_JOIN_REASON_UNATTRIBUTED_REFERENCE
        assert result["n_unattributed_references_in_frame"] == 1
        with pytest.raises(TileJoinRefusalError) as caught:
            compute_per_tile_tp_fp_fn(det, refs, bounds, 20)
        assert caught.value.reason == TILE_JOIN_REASON_UNATTRIBUTED_REFERENCE
        record = lam.describe_tile_join_refusal(det, refs, bounds, "sheet-primary")
        assert record["reason"] == TILE_JOIN_REASON_UNATTRIBUTED_REFERENCE

    def test_a_foreign_sheet_reference_is_an_exclusion(self):
        bounds = synthetic_bounds()
        refs = self._refs_with_blank("K-35-078-1_Lesovo")
        det = merged_detections(synthetic_refs(), bounds)
        result = calculate_tile_classification(det, refs, bounds)
        assert "error" not in result
        part = result["tile_join_diagnostics"]["references"]["exclusions"]["partition"]
        assert part["n_sheet_not_in_frame"] == 1

    def test_an_out_of_frame_reference_with_no_sheet_is_an_exclusion(self):
        bounds = synthetic_bounds()
        refs = self._refs_with_blank(None)
        refs.loc[refs.index[0], "geometry"] = _pt(-5000, -5000)
        det = merged_detections(synthetic_refs(), bounds)
        result = calculate_tile_classification(det, refs, bounds)
        assert "error" not in result
        part = result["tile_join_diagnostics"]["references"]["exclusions"]["partition"]
        assert part["n_no_sheet_outside_frame"] == 1

    def test_the_historical_joins_are_unchanged(self):
        bounds = synthetic_bounds()
        refs = self._refs_with_blank(None)
        det = merged_detections(synthetic_refs(), bounds)
        for join in ("id", "geometric-contains"):
            assert "error" not in calculate_tile_classification(
                det, refs, bounds, tile_join=join)

    def test_exclusion_partitions_reconcile(self):
        """Audit A-L3: the partition plus the population is the input."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        reduced = bounds[bounds["tile_name"].str.startswith(SHEET_A)]
        det = merged_detections(refs, bounds)
        result = calculate_tile_classification(det, refs, reduced, parent_bounds=bounds)
        for side in ("detections", "references"):
            d = result["tile_join_diagnostics"][side]
            assert d["n_sheet_scoped"] + sum(d["exclusions"]["partition"].values()) \
                == d["n_points"]


# ═══════════════════════════════════════════════════════════════════════════
# W1-C1: a cached MCC block is never relabelled
# ═══════════════════════════════════════════════════════════════════════════


class TestCachedMccProvenance:

    def _call(self, block: dict | None, monkeypatch):
        from scripts import compute_corrected_f1_multi_buffer as cc

        calls: list[str] = []
        monkeypatch.setattr(cc, "bootstrap_tile_level_ci",
                            lambda *a, **k: calls.append("ci") or
                            {"precision": (0, 1), "recall": (0, 1), "f1": (0, 1)})
        bounds, refs = synthetic_bounds(), synthetic_refs("source_map")
        res = cc.compute_at_buffer(
            merged_detections(refs, bounds, "source_map"), refs, bounds, None, None,
            50, 20, 1, compute_mcc=True,
            extension_gdf=gpd.GeoDataFrame(
                {"candidate_id": [0], "source_map": [SHEET_A], "nearest_student_m": [500.0]},
                geometry=[_pt(-5000, -5000)], crs=CRS),
            precomputed_mcc=block)
        return res, calls

    @pytest.mark.parametrize("block", [{"mcc": 0.25, "tile_tp": 1},
                                       {"mcc": 0.25, "tile_tp": 1, "tile_join": None},
                                       {"mcc": 0.25, "tile_tp": 1, "tile_join": "id"},
                                       {"mcc": 0.25, "tile_tp": 1, "tile_join": "bogus"}])
    def test_an_unlabelled_or_other_cache_is_refused_before_interval_work(
            self, block, monkeypatch):
        with pytest.raises(ValueError, match="precomputed MCC block"):
            self._call(block, monkeypatch)

    def test_a_matching_cache_is_used(self, monkeypatch):
        res, calls = self._call({"mcc": 0.25, "tile_tp": 1, "tile_join": "sheet-contains"},
                                monkeypatch)
        assert res.mcc == 0.25 and res.tile_join == "sheet-contains"
        assert calls == ["ci"]


# ═══════════════════════════════════════════════════════════════════════════
# W1-C2, W1-C3 (with A-L6): recorded arms validated first; drift is fatal
# ═══════════════════════════════════════════════════════════════════════════


def _write_board(tmp_path: Path, dets: dict[str, gpd.GeoDataFrame],
                 f1_override: dict[str, float] | None = None,
                 hashes: dict[str, str] | None = None,
                 pre_invariant: tuple[str, ...] = ()) -> tuple[Path, Path]:
    """A board on disk; each cell's evaluation is the legacy (id) record.

    A ``pre_invariant`` cell carries a confusion and no refusal record, as
    the evaluations scored before the tile-join invariant existed do (two of
    the three Gemini 3.7 board cells), although its replay now refuses.
    """
    bounds, refs = synthetic_bounds(), synthetic_refs()
    bpath = _write(bounds, tmp_path / "bounds.geojson")
    rpath = _write(refs, tmp_path / "refs.geojson")
    conditions = []
    for label, det in dets.items():
        dpath = _write(det, tmp_path / f"det_{label}.geojson")
        _, _, f1 = calculate_f1_internal(det, refs, bounds, 20)
        rec = calculate_tile_classification(det, refs, bounds, tile_join="id")
        if label in pre_invariant:
            tile = {"confusion": {"tp": 1, "tn": 2, "fp": 0, "fn": 4},
                    "mcc": {"point": 0.1337}}
        elif "error" not in rec:
            tile = {"confusion": {k: rec[k] for k in ("tp", "tn", "fp", "fn")},
                    "mcc": {"point": rec["mcc"]}}
        else:
            tile = {"withheld": True, "withheld_reason": rec["reason"]}
        meta: dict[str, Any] = {"cli_args": {"detections": str(dpath),
                                             "bounds": str(bpath),
                                             "ground_truth": str(rpath)}}
        if hashes:
            meta["input_git_state"] = {"blob_hashes": {str(dpath): hashes[label]}}
        ev = tmp_path / f"eval_{label}.json"
        ev.write_text(json.dumps({"_metadata": meta, "summary": {
            "buffers": [{"buffer_metres": 20,
                         "f1": round((f1_override or {}).get(label, f1), 4)}],
            "tile_classification": tile}}))
        conditions.append({"label": label, "eval_path": str(ev),
                           "architecture": "consensus"})
    cpath = tmp_path / "run-conditions.json"
    cpath.write_text(json.dumps({"decomposition": {"r": {"conditions": conditions}}}))
    apath = tmp_path / "run-analyses.json"
    apath.write_text(json.dumps({"analyses": [{"analysis_id": "board", "conditions_compared":
                                               [f"r::{k}" for k in dets]}]}))
    return cpath, apath


def _perfect() -> gpd.GeoDataFrame:
    return merged_detections(synthetic_refs(), synthetic_bounds())


def _foreign() -> gpd.GeoDataFrame:
    """Another tiling's names: the legacy id table refuses it."""
    det = _perfect().drop(columns="source_tiles")
    det["source_tile"] = [f"{s}_x{7 + i}_y{7 + i}.png" for i, s in enumerate(synthetic_refs()["Map"])]
    return det


class TestReplayOrder:

    def test_f1_only_replays_the_recorded_count_table_first(self, tmp_path, monkeypatch):
        from scripts import era1_leaderboard_tiering as t

        order: list[str] = []
        real = t.cell_per_tile

        def spy(cli, gdf_ref, gdf_bounds, tile_order, buffer_metres=20,
                count_table_join="sheet-primary"):
            order.append(count_table_join)
            return real(cli, gdf_ref, gdf_bounds, tile_order, buffer_metres, count_table_join)

        monkeypatch.setattr(t, "cell_per_tile", spy)
        c, a = _write_board(tmp_path, {"a": _perfect(), "b": differing_detections()})
        cells, *_ = t.load_cells(c, a, "board", None, None, withheld=[])
        assert order == ["id", "sheet-primary", "id", "sheet-primary"]
        for cell in cells:
            ct = cell["validation"]["count_table"]
            assert ct["recorded_join"] == "id" and ct["passed"] is True
            assert ct["replay_f1"] == pytest.approx(ct["eval_f1"], abs=5e-5)

    def test_count_table_drift_stops_the_run(self, tmp_path):
        from scripts import era1_leaderboard_tiering as t

        c, a = _write_board(tmp_path, {"a": _perfect()}, f1_override={"a": 0.5})
        with pytest.raises(t.ReproductionDriftError, match="micro-F1"):
            t.load_cells(c, a, "board", None, None, withheld=[])

    def test_an_unexpected_refusal_stops_the_run(self, tmp_path):
        """The legacy record holds intervals; its replay refuses."""
        from scripts import era1_leaderboard_tiering as t

        c, a = _write_board(tmp_path, {"a": _perfect(), "f": _foreign()},
                            pre_invariant=("f",))
        with pytest.raises(t.ReproductionDriftError, match="refused"):
            t.load_cells(c, a, "board", None, None, withheld=[])

    def test_a_verified_expected_refusal_lets_the_new_rule_score(self, tmp_path):
        from scripts import era1_leaderboard_tiering as t

        c, a = _write_board(tmp_path, {"a": _perfect(), "f": _foreign()},
                            pre_invariant=("f",))
        cells, *_ = t.load_cells(c, a, "board", None, None, withheld=[], want_mcc=True,
                                 expected_refusals={"r::f": TILE_JOIN_REASON_DETECTION_SHORTFALL})
        f = next(cell for cell in cells if cell["ref"] == "r::f")
        assert f["validation"]["count_table"]["expected_refusal"] == (
            TILE_JOIN_REASON_DETECTION_SHORTFALL)
        assert f["validation"]["classification"]["passed"] is True
        assert f["mcc"] == pytest.approx(1.0)

    def test_expected_refusals_from_a_tiering(self, tmp_path):
        from scripts import era1_leaderboard_tiering as t

        path = tmp_path / "tiering.json"
        path.write_text(json.dumps({"withheld_cells": [
            {"ref": "r::f", "reason": "x (tile_join_detection_shortfall) y"}]}))
        assert t.expected_refusals_from(path) == {
            "r::f": TILE_JOIN_REASON_DETECTION_SHORTFALL}

    def test_an_input_identity_mismatch_stops_the_run(self, tmp_path):
        from scripts import era1_leaderboard_tiering as t

        c, a = _write_board(tmp_path, {"a": _perfect()}, hashes={"a": "0" * 40})
        with pytest.raises(t.ReproductionDriftError, match="hashes"):
            t.load_cells(c, a, "board", None, None, withheld=[])

    def test_a_missing_historical_block_stops_a_new_join(self, tmp_path):
        from scripts import era1_leaderboard_tiering as t

        c, a = _write_board(tmp_path, {"a": _perfect()})
        ev = tmp_path / "eval_a.json"
        doc = json.loads(ev.read_text())
        del doc["summary"]["tile_classification"]
        ev.write_text(json.dumps(doc))
        with pytest.raises(t.ReproductionDriftError, match="no tile_classification"):
            t.load_cells(c, a, "board", None, None, withheld=[], want_mcc=True)


# ═══════════════════════════════════════════════════════════════════════════
# B-C1, A-L1, A-L7: the K-ladder drivers
# ═══════════════════════════════════════════════════════════════════════════


def test_k_ladder_mcb_id_replay_runs_through_the_real_run_mcb(tmp_path, monkeypatch):
    """Audit B-C1: ``--tile-join id --count-table-join id`` must not die on F1.

    ``run_mcb`` and its guard run for real; only the subprocess is replaced,
    by one that hands back the committed artefact for the call it receives.
    """
    import scripts.k_ladder_mcb as mcb

    committed_dir = mcb.BASE_DIR / mcb.K_LADDER_DIR / "mcb"
    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        board, metric = cmd[cmd.index("--board") + 1], cmd[cmd.index("--metric") + 1]
        buffer_m = int(cmd[cmd.index("--buffer") + 1])
        out = Path(cmd[cmd.index("--out") + 1])
        slug = out.name
        tj = cmd[cmd.index("--tile-join") + 1] if "--tile-join" in cmd else "sheet-contains"
        ct = cmd[cmd.index("--count-table-join") + 1]
        src = committed_dir / slug / mcb.artefact_name(board, metric, buffer_m)
        out.mkdir(parents=True, exist_ok=True)
        (out / mcb.artefact_name(board, metric, buffer_m, tj, ct)).write_text(src.read_text())

    monkeypatch.setattr(mcb.subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", [
        "k_ladder_mcb.py", "--only", "gs-stride-a", "--tile-join", "id",
        "--count-table-join", "id", "--bootstrap", "10000",
        "--output-dir", str(tmp_path / "out")])
    assert mcb.main() == 0
    f1 = next(c for c in calls if c[c.index("--metric") + 1] == "f1")
    mcc = next(c for c in calls if c[c.index("--metric") + 1] == "mcc")
    assert "--tile-join" not in f1 and f1[-2:] == ["--count-table-join", "id"]
    assert mcc[-4:] == ["--tile-join", "id", "--count-table-join", "id"]


def test_tiering_joins_refuses_contradictions():
    """Audit A-L7."""
    import scripts.k_ladder_mcb as mcb

    with pytest.raises(ValueError, match="contradictory classification"):
        mcb.tiering_joins({"tile_joins": {"classification": "id"},
                           "mcc_permutation": {"tile_join": "sheet-contains"}})
    with pytest.raises(ValueError, match="contradictory count_table"):
        mcb.tiering_joins({"tile_joins": {"count_table": "id"},
                           "count_table_join": "sheet-primary"})
    assert mcb.tiering_joins({}) == {"classification": "id", "count_table": "id"}
