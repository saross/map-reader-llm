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
        """``build_pareto_v2`` reads committed run outputs at import, so its
        header function is compiled from source alone, and the payload is
        checked to spread it."""
        source = (REPO / "scripts/build_pareto_v2.py").read_text()
        tree = ast.parse(source)
        fn = next(n for n in tree.body
                  if isinstance(n, ast.FunctionDef) and n.name == "pareto_header")
        namespace = {"tile_join_provenance": lam.tile_join_provenance}
        exec(compile(ast.Module([fn], []), "build_pareto_v2", "exec"), namespace)
        assert namespace["pareto_header"]("id", "sheet-primary")["tile_joins"] == {
            "classification": "id", "count_table": "sheet-primary",
            "rulings": lam.TILE_JOIN_RULINGS}
        assert "**pareto_header(args.tile_join, args.count_table_join)" in source

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
    "build_gs_era2_board.py", "gemini37_image_55map_r2.py",
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
    sheets = synthetic_refs()["Map"]
    det["source_tile"] = [f"{s}_x{7 + i}_y{7 + i}.png" for i, s in enumerate(sheets)]
    return det


class TestReplayOrder:

    def test_f1_only_replays_the_recorded_count_table_first(self, tmp_path, monkeypatch):
        from scripts import era1_leaderboard_tiering as t

        order: list[str] = []
        real = t.cell_per_tile

        def spy(cli, gdf_ref, gdf_bounds, tile_order, buffer_metres=20,
                count_table_join="sheet-primary", **kwargs):
            order.append(count_table_join)
            return real(cli, gdf_ref, gdf_bounds, tile_order, buffer_metres,
                        count_table_join, **kwargs)

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


# ═══════════════════════════════════════════════════════════════════════════
# Astra W1-C4: a recorded refusal reproduces in every count it records
# ═══════════════════════════════════════════════════════════════════════════

_G37 = ("results/k-ladder-2026-09-12/phase2/cells/"
        "gemini37-screen-2026-08-28__g37-text-k1-verified-carried-p0_10-k1/evaluation.json")


@pytest.mark.parametrize("n_assigned, reproduces", [(22, True), (525, False)])
def test_w1_c4_recorded_refusal_checked_count_by_count(monkeypatch, n_assigned, reproduces):
    """The real committed refusal block (22 of 526 booked under ``id``), with
    only the replay's response varied: the same reason with other counts is
    drift, not a reproduction."""
    from scripts import era1_leaderboard_tiering as t

    evaluation = json.loads((REPO / _G37).read_text())
    block = evaluation["summary"]["tile_classification"]
    diag = json.loads(json.dumps(block["tile_join_diagnostics"]))
    diag["detections"]["n_assigned"] = n_assigned
    replay = {"error": "refused", "reason": block["withheld_reason"],
              "tile_join_diagnostics": diag}
    monkeypatch.setattr(t, "calculate_tile_classification", lambda *a, **k: replay)
    if reproduces:
        record = t.validate_recorded_classification("g37", None, None, None, evaluation, "id")
        assert record["expected_refusal"] == "tile_join_detection_shortfall"
        assert "tile_join_diagnostics.detections.n_assigned" in record["compared"]
        assert "tile_join_diagnostics.references.n_inside_union" in record["compared"]
    else:
        with pytest.raises(t.ReproductionDriftError, match="n_assigned: recorded 22"):
            t.validate_recorded_classification("g37", None, None, None, evaluation, "id")


def test_compare_present_is_strict_on_the_replay_and_lenient_on_the_record():
    """Astra R2-1: a field the record holds and the replay lacks is a
    mismatch (the previous test asserted the opposite); a field the record
    holds as null is listed as not comparable; a field only the replay has
    is never invented into the record."""
    from scripts.era1_leaderboard_tiering import compare_present

    compared, mismatches, not_comparable = compare_present(
        {"a": 1, "b": None, "c": 2}, {"a": 1, "d": 9})
    assert compared == ["a"]
    assert mismatches == ["c: recorded 2, the replay lacks this field"]
    assert not_comparable == ["b"]


@pytest.mark.parametrize("replay, message", [
    ({"x": {"n": 2, "m": 1}}, "x.n: recorded 1, replay 2"),           # changed value
    ({"x": {"m": 1}}, "x.n: recorded 1, the replay lacks this field"),  # removed field
    ({}, "x: recorded {'n': 1, 'm': 1}, the replay lacks this field"),  # removed block
    ({"x": None}, "x: the replay has no block here"),                  # emptied block
])
def test_compare_present_catches_each_kind_of_replay_loss(replay, message):
    from scripts.era1_leaderboard_tiering import compare_present

    _, mismatches, _ = compare_present({"x": {"n": 1, "m": 1}}, replay)
    assert mismatches == [message]


def test_compare_present_honours_an_explicit_schema_translation(monkeypatch):
    from scripts import era1_leaderboard_tiering as t

    monkeypatch.setattr(t, "REPLAY_SCHEMA_TRANSLATIONS", {"x.old": "x.new"})
    compared, mismatches, _ = t.compare_present({"x": {"old": 3}}, {"x": {"new": 3}})
    assert compared == ["x.old"] and mismatches == []
    _, mismatches, _ = t.compare_present({"x": {"old": 3}}, {"x": {"new": 4}})
    assert mismatches == ["x.old: recorded 3, replay 4"]
    _, mismatches, _ = t.compare_present({"x": {"old": 3}}, {"x": {}})
    assert mismatches and "translation x.new" in mismatches[0]


def test_no_schema_translation_is_in_force():
    """The table ships empty: every entry must be added deliberately."""
    from scripts.era1_leaderboard_tiering import REPLAY_SCHEMA_TRANSLATIONS

    assert REPLAY_SCHEMA_TRANSLATIONS == {}


@pytest.mark.parametrize("mode", ["removed_field", "removed_block", "no_diagnostics"])
def test_r2_1_a_replay_that_drops_recorded_refusal_counts_stops(monkeypatch, mode):
    """Astra R2-1, on the real committed refusal block: a replay that no
    longer emits a count the record holds (one field, or the whole
    diagnostics block) is a reproduction failure, not a pass with fewer
    fields compared."""
    from scripts import era1_leaderboard_tiering as t

    evaluation = json.loads((REPO / _G37).read_text())
    block = evaluation["summary"]["tile_classification"]
    diag = json.loads(json.dumps(block["tile_join_diagnostics"]))
    replay: dict[str, Any] = {"error": "refused", "reason": block["withheld_reason"]}
    if mode == "removed_field":
        del diag["detections"]["n_assigned"]
        replay["tile_join_diagnostics"] = diag
    elif mode == "removed_block":
        del diag["references"]
        replay["tile_join_diagnostics"] = diag
    monkeypatch.setattr(t, "calculate_tile_classification", lambda *a, **k: replay)
    with pytest.raises(t.ReproductionDriftError, match="the replay lacks|no block here"):
        t.validate_recorded_classification("g37", None, None, None, evaluation, "id")


def test_r2_1_an_old_refusal_record_without_diagnostics_is_listed(monkeypatch):
    """A record that predates the diagnostics has nothing to compare; it is
    listed as not comparable, never reported as compared."""
    from scripts import era1_leaderboard_tiering as t

    evaluation = json.loads((REPO / _G37).read_text())
    block = evaluation["summary"]["tile_classification"]
    replay = {"error": "refused", "reason": block["withheld_reason"],
              "tile_join_diagnostics": block["tile_join_diagnostics"]}
    del block["tile_join_diagnostics"]
    monkeypatch.setattr(t, "calculate_tile_classification", lambda *a, **k: replay)
    record = t.validate_recorded_classification("g37", None, None, None, evaluation, "id")
    assert record["compared"] == []
    assert record["not_comparable"] == ["tile_join_diagnostics"]


def test_the_two_refusal_paths_emit_different_fields():
    """Pinned and documented (Astra's review; audit A-M1): under (X, id) with
    X geometric, the probe asks the classification join (as before Wave 1)
    and the id table's own refusal is caught later, so the record is the
    late path's (``detected_by``, no vocabularies); under (id, id) the probe
    refuses up front and the record carries both vocabularies."""
    from scripts.evaluate_detections import evaluate_single_run

    bounds, refs = synthetic_bounds(), synthetic_refs()
    det = _foreign()
    late = evaluate_single_run(det.copy(), refs, bounds, [20], n_bootstrap=20,
                               compute_mcc=True, tile_join="geometric-contains",
                               count_table_join="id")["tile_join_withheld"]
    early = evaluate_single_run(det.copy(), refs, bounds, [20], n_bootstrap=20,
                                compute_mcc=True, tile_join="id",
                                count_table_join="id")["tile_join_withheld"]
    assert late["detected_by"] == "per_tile_table_not_preflight_probe"
    assert late["vocabularies"] is None and late["shortfall"]["n_outside_union"] is None
    assert "detected_by" not in early and isinstance(early["vocabularies"], dict)
    assert late["reason"] == early["reason"] == TILE_JOIN_REASON_DETECTION_SHORTFALL


class TestReferenceAttributionEdges:

    def test_an_absent_sheet_column_is_refused_in_frame(self):
        bounds = synthetic_bounds()
        refs = synthetic_refs().drop(columns="Map")
        det = merged_detections(synthetic_refs(), bounds)
        result = calculate_tile_classification(det, refs, bounds)
        assert result["reason"] == TILE_JOIN_REASON_UNATTRIBUTED_REFERENCE
        assert result["n_unattributed_references_in_frame"] == len(refs)
        with pytest.raises(TileJoinRefusalError):
            compute_per_tile_tp_fp_fn(det, refs, bounds, 20)

    def test_an_empty_reference_set_is_not_refused(self):
        bounds = synthetic_bounds()
        refs = gpd.GeoDataFrame(geometry=[], crs=CRS)
        det = merged_detections(synthetic_refs(), bounds)
        result = calculate_tile_classification(det, refs, bounds)
        assert "error" not in result
        assert result["tp"] == 0 and result["fp"] == 5
        table = compute_per_tile_tp_fp_fn(det, refs, bounds, 20)
        assert int(table["fp"].sum()) == len(det) and int(table["fn"].sum()) == 0


# ═══════════════════════════════════════════════════════════════════════════
# Second fix pass: mutants that survived the first fix round's tests
# ═══════════════════════════════════════════════════════════════════════════

#: The W1-fixed command-line tools a launcher may run.
_W1_TOOLS = ("evaluate_detections.py", "era1_leaderboard_tiering.py",
             "compute_corrected_f1_multi_buffer.py", "selection_aware_intervals.py",
             "k_ladder_mcb.py", "k_ladder_mcc_test.py", "mcc_tiering_55map.py")

#: Files that name a W1-fixed tool in a bare string literal but launch nothing.
_NOT_LAUNCHERS: dict[str, str] = {
    "dedup_tiering_rerun.py": "records the tools' paths as source_script metadata",
    "register_pass1_adapt.py": "records the tool's path as script_path metadata",
}

#: Text that shows a file names its rules on the command lines it builds.
_PINS = ("LEGACY_JOIN_FLAGS", "recorded_join_flags", "--tile-join")


def test_every_launcher_names_its_rules():
    """A static scan for launchers (the first dispositions file missed two
    that it judged prose-only): any ``scripts/*.py`` holding a space-free
    string literal that ends in a W1-fixed tool's file name must carry a pin
    or sit on :data:`_NOT_LAUNCHERS` with its reason."""
    unpinned = []
    for path in sorted((REPO / "scripts").glob("*.py")):
        text = path.read_text()
        literals = {n.value.strip() for n in ast.walk(ast.parse(text))
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and " " not in n.value.strip()}
        if not any(s.endswith(tool) for s in literals for tool in _W1_TOOLS):
            continue
        if path.name in _NOT_LAUNCHERS or any(pin in text for pin in _PINS):
            continue
        unpinned.append(path.name)
    assert unpinned == []


def test_a_m1_a_sheet_count_table_probes_its_own_join():
    """(id, sheet-primary): ``id`` refuses this frame (a detection names a
    tile outside it) but the sheet-primary table does not, so the F1
    intervals stand and only the tile block is withheld (kills the mutant
    that probes the classification join whatever the count table)."""
    from scripts.evaluate_detections import evaluate_single_run

    bounds, refs = synthetic_bounds(), synthetic_refs()
    det = merged_detections(refs, bounds).drop(columns="source_tiles")
    det.loc[det.index[0], "source_tile"] = f"{SHEET_A}_32635_x999_y999.png"
    assert lam.describe_tile_join_refusal(det, refs, bounds, "id") is not None
    assert lam.describe_tile_join_refusal(det, refs, bounds, "sheet-primary") is None
    run = evaluate_single_run(det, refs, bounds, [20], n_bootstrap=20, compute_mcc=True,
                              tile_join="id", count_table_join="sheet-primary")
    assert "tile_join_withheld" not in run
    assert run["buffers"][0]["f1_ci_lower"] is not None
    assert run["tile_classification"]["withheld_reason"] == (
        TILE_JOIN_REASON_DETECTION_SHORTFALL)


@pytest.mark.parametrize("join", ["id", "sheet-primary"])
def test_compute_at_buffer_passes_the_count_table_to_its_intervals(monkeypatch, join):
    """B-M4 at the call site: ``compute_at_buffer`` hands its count-table
    join to ``bootstrap_tile_level_ci`` (kills corrected_ci_ct_dropped)."""
    from scripts import compute_corrected_f1_multi_buffer as cc

    seen: list[str | None] = []

    def spy(*args, **kwargs):
        seen.append(kwargs.get("count_table_join"))
        return {"precision": (0, 1), "recall": (0, 1), "f1": (0, 1)}

    monkeypatch.setattr(cc, "bootstrap_tile_level_ci", spy)
    bounds, refs = synthetic_bounds(), synthetic_refs("source_map")
    cc.compute_at_buffer(
        merged_detections(refs, bounds, "source_map"), refs, bounds, None, None, 50, 20, 1,
        extension_gdf=gpd.GeoDataFrame(
            {"candidate_id": [0], "source_map": [SHEET_A], "nearest_student_m": [500.0]},
            geometry=[_pt(-5000, -5000)], crs=CRS),
        count_table_join=join)
    assert seen == [join]


@pytest.mark.parametrize("block, message", [
    ({"mcc": 0.25}, "records no tile_join"),
    ({"mcc": 0.25, "tile_join": None}, "records no tile_join"),
    ({"mcc": 0.25, "tile_join": "bogus"}, "not a classification join"),
    ({"mcc": 0.25, "tile_join": "id"}, "is under 'id', not 'sheet-contains'"),
])
def test_cached_mcc_refusals_name_their_reason(block, message):
    """W1-C1: each refusal says why (kills w1c1_relabel, whose unlabelled
    cache was still refused, but as an invalid name)."""
    from scripts.compute_corrected_f1_multi_buffer import _check_precomputed_mcc

    with pytest.raises(ValueError, match=message):
        _check_precomputed_mcc(block, "sheet-contains")


class TestTieBreakDefeatsInputOrder:
    """Audit Low: ``sjoin`` returns candidates in spatial order, which on the
    first fixture was also name order. Here the spatially first tile (x80)
    has the LARGER name (``x80`` sorts after ``x160``)."""

    A80, A160 = _tile(SHEET_A, 80, 0), _tile(SHEET_A, 160, 0)

    def test_candidates_are_sorted_by_name(self):
        bounds = synthetic_bounds()
        sheet = bounds[bounds["tile_name"].str.startswith(SHEET_A)]
        pts = gpd.GeoDataFrame(geometry=[_pt(170, 50)], crs=CRS)
        assert lam.sheet_join_candidate_tiles(pts, SHEET_A, sheet, bounds) == [
            [self.A160, self.A80]]

    def test_an_equidistant_point_books_to_the_smaller_name(self):
        """x = 170 is 40 m from both centres (130 and 210)."""
        table = _fp_table([(170, 50)], synthetic_bounds(), self.A160)
        assert table.loc[self.A160, "fp"] == 1
        assert table.loc[self.A80, "fp"] == 0

    def test_unsorted_candidates_passed_in(self):
        """The helper's own contract: whatever order the caller passes."""
        bounds = synthetic_bounds()
        pts = gpd.GeoDataFrame(geometry=[_pt(170, 50)], crs=CRS)
        assert lam.sheet_primary_tiles(pts, bounds, [[self.A80, self.A160]]) == [self.A160]


def test_w1_c4_point_values_must_reproduce(monkeypatch):
    """The expected-refusal route also reproduces the unaffected F1,
    precision and recall (W1.4); a drift in one stops the run (kills
    w1c4_no_point_check)."""
    from scripts import era1_leaderboard_tiering as t

    evaluation = {"summary": {"buffers": [
        {"buffer_metres": 20, "f1": 0.5, "precision": 0.5, "recall": 0.5}]}}
    monkeypatch.setattr(t, "cell_detections", lambda cli, bounds: None)
    monkeypatch.setattr(t, "calculate_f1_internal", lambda *a, **k: (0.5, 0.5, 0.5))
    out = t._reproduce_refused_cell("c", {"detections": "d"}, None, None, 20,
                                    evaluation, "id", "id")
    assert sorted(out["point_compared"]) == ["point.f1", "point.precision", "point.recall"]
    monkeypatch.setattr(t, "calculate_f1_internal", lambda *a, **k: (0.5, 0.6, 0.5))
    with pytest.raises(t.ReproductionDriftError, match="recall"):
        t._reproduce_refused_cell("c", {"detections": "d"}, None, None, 20,
                                  evaluation, "id", "id")


def test_a_l1_a_rung_the_validation_run_withholds_is_recorded(tmp_path, monkeypatch):
    """K-ladder MCC test, (id, sheet-primary): the (id, id) validation run
    withholds a rung, so the pair has no committed p-value. The gate records
    the reproduced refusal instead of raising a bare KeyError (A-L1)."""
    import scripts.k_ladder_mcc_test as kmt

    rungs = [{"K": 1, "condition_id": "run::a", "eval_path": "e", "f1_headline": 0.8,
              "tile_mcc": 0.5},
             {"K": 3, "condition_id": "run::b", "eval_path": "e", "f1_headline": 0.9,
              "tile_mcc": 0.6}]
    inventory = tmp_path / "ladders.json"
    inventory.write_text(json.dumps({"ladders": [{
        "slug": "x", "family_base": "X", "run_id": "run", "proposer_pool": "p",
        "corpus": "c", "reference_file": "r.geojson", "frame_file": "f.geojson",
        "headline_buffer_m": 20, "rungs": rungs}]}))
    pair = {"ref_a": "run::a", "ref_b": "run::b", "p_value": 0.5, "bh_adjusted_p": 0.5,
            "significant": False}
    requested = {"pairwise": [{**pair, "observed_diff": -0.1}], "fdr_q": 0.05,
                 "n_permutations": 10, "seed": 1, "n_tiles": 4,
                 "mcc_permutation": {"pairwise": [{**pair, "observed_mcc_diff": -0.1}],
                                     "gates": []}}
    validation = {"pairwise": [], "withheld_cells": [
        {"ref": "run::a", "reason": TILE_JOIN_REASON_DETECTION_SHORTFALL}]}

    def fake_tiering(*args: Any) -> dict:
        return validation if args[-2:] == ("id", "id") else requested

    monkeypatch.setattr(kmt, "run_tiering", fake_tiering)
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["k_ladder_mcc_test.py", "--ladders", str(inventory),
                                      "--output-dir", str(out), "--tile-join", "id",
                                      "--count-table-join", "sheet-primary"])
    kmt.main()
    gate = json.loads((out / "x.json").read_text())["gate"]
    assert gate["n_pairs_gated"] == 0
    (entry,) = gate["pairs"]
    assert entry["expected_refusal"] is True and entry["available"] is False
    assert entry["withheld"] == {"run::a": TILE_JOIN_REASON_DETECTION_SHORTFALL}


def test_a_l4_the_describer_books_the_sheet_scoped_population():
    """Audit A-L4: with one D50 exclusion that lies IN the frame (attributed
    to A, inside only B's tile B280) and one unattributed in-frame row, the
    describer's ``n_booked`` is the sheet-scoped population (3), not the
    in-frame count less the unattributed rows (4)."""
    bounds, refs = synthetic_bounds(), synthetic_refs()
    det = merged_detections(refs, bounds).drop(columns="source_tiles")
    det.loc[det.index[4], "source_tile"] = _tile(SHEET_A, 0, 0)
    det.loc[det.index[4], "geometry"] = _pt(370, 50)
    det.loc[det.index[0], "source_tile"] = None
    refusal = lam.describe_tile_join_refusal(det, refs, bounds, "sheet-primary")
    assert refusal["reason"] == TILE_JOIN_REASON_UNATTRIBUTED_DETECTION
    assert refusal["shortfall"] == {
        "axis": "detections", "n_booked": 3, "n_inside_union": 4, "n_outside_union": 1,
        "n_multi_tile": None, "shortfall": 1}


# ═══════════════════════════════════════════════════════════════════════════
# Astra's re-review (R2-2 to R2-6)
# ═══════════════════════════════════════════════════════════════════════════


def test_r2_2_classification_drift_stops_a_count_table_only_change(tmp_path, monkeypatch):
    """Recorded (id, id), requested (id, sheet-primary): the classification
    join is unchanged, but the historical confusion is still validated in
    step 1, so its drift STOPS the run before any table is built under the
    new count-table rule, instead of surfacing as an MCC withholding."""
    from scripts import era1_leaderboard_tiering as t

    c, a = _write_board(tmp_path, {"a": _perfect()})
    ev = tmp_path / "eval_a.json"
    doc = json.loads(ev.read_text())
    doc["summary"]["tile_classification"]["confusion"]["tp"] += 1
    ev.write_text(json.dumps(doc))
    order: list[str] = []
    real = t.cell_per_tile

    def spy(*args, **kwargs):
        order.append(args[5] if len(args) > 5 else kwargs.get("count_table_join"))
        return real(*args, **kwargs)

    monkeypatch.setattr(t, "cell_per_tile", spy)
    with pytest.raises(t.ReproductionDriftError, match="reproduction drift"):
        t.load_cells(c, a, "board", None, None, withheld=[], want_mcc=True,
                     tile_join="id", count_table_join="sheet-primary")
    assert order == ["id"]  # the historical replay only; nothing new computed


def test_r2_2_a_matching_record_still_scores_the_new_count_table(tmp_path):
    from scripts import era1_leaderboard_tiering as t

    c, a = _write_board(tmp_path, {"a": _perfect()})
    (cell,) = t.load_cells(c, a, "board", None, None, withheld=[], want_mcc=True,
                           tile_join="id", count_table_join="sheet-primary")[0]
    assert cell["validation"]["classification"]["passed"] is True
    assert cell["mcc_gate"]["validation"]["recorded_join"] == "id"
    # The id join's committed MCC stands (a merged perfect detector scores
    # below 1 under id: the D72 defect, which the classification join fixes).
    recorded = json.loads((tmp_path / "eval_a.json").read_text())
    assert cell["mcc"] == pytest.approx(
        recorded["summary"]["tile_classification"]["mcc"]["point"], abs=5e-5)


def _write_replicate_board(tmp_path: Path, passes: list[gpd.GeoDataFrame], *,
                           per_run_f1: list[float] | None = None,
                           mean_f1: float | None = None,
                           writer: str | None = "scripts/evaluate_detections.py",
                           per_run: bool = True) -> tuple[Path, Path]:
    """A one-cell board whose cell is a replicate mean over ``passes``.

    The record is what ``evaluate_detections.py`` writes for several runs:
    each pass's F1 (rounded to 4 dp) in ``per_run``, and their mean in the
    summary. ``per_run_f1`` / ``mean_f1`` override the recorded values.
    """
    bounds, refs = synthetic_bounds(), synthetic_refs()
    bpath = _write(bounds, tmp_path / "bounds.geojson")
    rpath = _write(refs, tmp_path / "refs.geojson")
    pool = tmp_path / "pool"
    f1s = []
    for i, det in enumerate(passes, start=1):
        (pool / f"rep_{i}").mkdir(parents=True)
        _write(det, pool / f"rep_{i}" / "consensus.geojson")
        f1s.append(round(calculate_f1_internal(det, refs, bounds, 20)[2], 4))
    f1s = per_run_f1 or f1s
    rec = calculate_tile_classification(passes[0], refs, bounds, tile_join="id")
    meta: dict[str, Any] = {"cli_args": {"detections_dir": str(pool),
                                         "glob": "rep_*/consensus.geojson",
                                         "bounds": str(bpath), "ground_truth": str(rpath)}}
    if writer is not None:
        meta["script_path"] = writer
    doc: dict[str, Any] = {"_metadata": meta, "summary": {
        "n_runs": len(passes),
        "buffers": [{"buffer_metres": 20,
                     "f1": mean_f1 if mean_f1 is not None else round(float(np.mean(f1s)), 4)}],
        "tile_classification": {"confusion": {k: rec[k] for k in ("tp", "tn", "fp", "fn")},
                                "mcc": {"point": rec["mcc"]}}}}
    if per_run:
        doc["per_run"] = [{"label": "consensus",
                           "buffers": [{"buffer_metres": 20, "f1": f}]} for f in f1s]
    ev = tmp_path / "eval_rep.json"
    ev.write_text(json.dumps(doc))
    cpath = tmp_path / "run-conditions.json"
    cpath.write_text(json.dumps({"decomposition": {"r": {"conditions": [
        {"label": "rep", "eval_path": str(ev), "architecture": "consensus"}]}}}))
    apath = tmp_path / "run-analyses.json"
    apath.write_text(json.dumps({"analyses": [{"analysis_id": "board",
                                               "conditions_compared": ["r::rep"]}]}))
    return cpath, apath


class TestReplicateMeanReplay:
    """Astra R2-3: a replicate-mean cell's committed F1 is the mean of its
    per-pass F1s; each pass and the mean are reconstructed and compared,
    for two passes as for one."""

    def _passes(self) -> list[gpd.GeoDataFrame]:
        return [_perfect(), differing_detections()]

    def test_a_faithful_record_passes_pass_by_pass(self, tmp_path):
        from scripts import era1_leaderboard_tiering as t

        c, a = _write_replicate_board(tmp_path, self._passes())
        (cell,) = t.load_cells(c, a, "board", None, None, withheld=[])[0]
        ct = cell["validation"]["count_table"]
        assert ct["n_passes"] == 2
        assert len(ct["per_pass_eval_f1"]) == 2
        assert ct["per_pass_replay_f1"] == pytest.approx(ct["per_pass_eval_f1"], abs=5e-5)
        assert ct["replay_mean_f1"] == pytest.approx(ct["eval_f1"], abs=1e-4)
        assert "not applicable" not in ct["f1_check"]

    def test_a_changed_pass_f1_is_caught_with_two_passes(self, tmp_path):
        from scripts import era1_leaderboard_tiering as t

        bounds, refs = synthetic_bounds(), synthetic_refs()
        f1s = [round(calculate_f1_internal(d, refs, bounds, 20)[2], 4)
               for d in self._passes()]
        wrong = [f1s[0], round(f1s[1] - 0.05, 4)]
        c, a = _write_replicate_board(tmp_path, self._passes(), per_run_f1=wrong,
                                      mean_f1=round(float(np.mean(f1s)), 4))
        with pytest.raises(t.ReproductionDriftError, match="1 of 2 passes' F1"):
            t.load_cells(c, a, "board", None, None, withheld=[])

    def test_a_changed_mean_is_caught_with_two_passes(self, tmp_path):
        from scripts import era1_leaderboard_tiering as t

        c, a = _write_replicate_board(tmp_path, self._passes(), mean_f1=0.1)
        with pytest.raises(t.ReproductionDriftError, match="mean of the replayed"):
            t.load_cells(c, a, "board", None, None, withheld=[])

    def test_a_different_pass_count_is_drift(self, tmp_path):
        from scripts import era1_leaderboard_tiering as t

        bounds, refs = synthetic_bounds(), synthetic_refs()
        f1 = round(calculate_f1_internal(_perfect(), refs, bounds, 20)[2], 4)
        c, a = _write_replicate_board(tmp_path, self._passes(), per_run_f1=[f1, f1, f1])
        with pytest.raises(t.ReproductionDriftError, match="averages 3 passes"):
            t.load_cells(c, a, "board", None, None, withheld=[])

    @pytest.mark.parametrize("kwargs, message", [
        ({"writer": "scripts/register_pass1_adapt.py"}, "register_pass1_adapt"),
        ({"writer": None}, "written by None"),
        ({"per_run": False}, "no per_run block"),
    ])
    def test_a_record_this_replay_cannot_rebuild_is_held(self, tmp_path, kwargs, message):
        from scripts import era1_leaderboard_tiering as t

        c, a = _write_replicate_board(tmp_path, self._passes(), **kwargs)
        with pytest.raises(t.ReplayRouteUnsupportedError, match=message):
            t.load_cells(c, a, "board", None, None, withheld=[])


@pytest.mark.parametrize("withheld_cells, message", [
    ([], "withheld: none"),                                               # no refusal at all
    ([{"ref": "other::x", "reason": TILE_JOIN_REASON_DETECTION_SHORTFALL}],
     "other::x"),                                                         # an unrelated cell
    ([{"ref": "run::a", "reason": "some refusal"}], "run::a"),            # unrecognised reason
])
def test_r2_4_an_unexplained_missing_pair_stops(withheld_cells, message):
    """Astra R2-4: a pair missing from the validation run is an expected
    refusal only when a MEMBER of the pair is withheld with a recognised
    refusal code; otherwise the run stops instead of reporting a gate pass."""
    import scripts.k_ladder_mcc_test as kmt
    from scripts.era1_leaderboard_tiering import ReproductionDriftError

    with pytest.raises(ReproductionDriftError, match=message):
        kmt.missing_pair_gate("K1-vs-K3", ("run::a", "run::b"),
                              {"pairwise": [], "withheld_cells": withheld_cells})


def test_r2_4_a_member_refusal_is_recorded_with_its_code():
    import scripts.k_ladder_mcc_test as kmt

    reason = f"refused ({TILE_JOIN_REASON_DETECTION_SHORTFALL}) under id"
    gate = kmt.missing_pair_gate("K1-vs-K3", ("run::a", "run::b"), {"withheld_cells": [
        {"ref": "run::b", "reason": reason}, {"ref": "other::x", "reason": reason}]})
    assert gate["available"] is False and gate["expected_refusal"] is True
    assert gate["withheld"] == {"run::b": reason}
    assert gate["refusal_codes"] == {"run::b": TILE_JOIN_REASON_DETECTION_SHORTFALL}


@pytest.mark.parametrize("withheld_cells", [
    [], [{"ref": "unrelated-cell", "reason": "some refusal"}]])
def test_r2_4_the_driver_stops_rather_than_passing_the_gate(tmp_path, monkeypatch,
                                                            withheld_cells):
    """End to end through ``main``: Astra's two probe cases no longer end in
    ``gate_pass: true``; they stop before anything is written."""
    import scripts.k_ladder_mcc_test as kmt
    from scripts.era1_leaderboard_tiering import ReproductionDriftError

    rungs = [{"K": 1, "condition_id": "run::a", "eval_path": "e", "f1_headline": 0.8,
              "tile_mcc": 0.5},
             {"K": 3, "condition_id": "run::b", "eval_path": "e", "f1_headline": 0.9,
              "tile_mcc": 0.6}]
    inventory = tmp_path / "ladders.json"
    inventory.write_text(json.dumps({"ladders": [{
        "slug": "x", "family_base": "X", "run_id": "run", "proposer_pool": "p",
        "corpus": "c", "reference_file": "r.geojson", "frame_file": "f.geojson",
        "headline_buffer_m": 20, "rungs": rungs}]}))
    pair = {"ref_a": "run::a", "ref_b": "run::b", "p_value": 0.5, "bh_adjusted_p": 0.5,
            "significant": False}
    requested = {"pairwise": [{**pair, "observed_diff": -0.1}], "fdr_q": 0.05,
                 "n_permutations": 10, "seed": 1, "n_tiles": 4,
                 "mcc_permutation": {"pairwise": [{**pair, "observed_mcc_diff": -0.1}],
                                     "gates": []}}
    validation = {"pairwise": [], "withheld_cells": withheld_cells}
    monkeypatch.setattr(kmt, "run_tiering", lambda *args: (
        validation if args[-2:] == ("id", "id") else requested))
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["k_ladder_mcc_test.py", "--ladders", str(inventory),
                                      "--output-dir", str(out), "--tile-join", "id",
                                      "--count-table-join", "sheet-primary"])
    with pytest.raises(ReproductionDriftError, match="unexplained absence"):
        kmt.main()
    assert not (out / "x.json").exists()


# R2-5: a launcher's ``scripts`` import must follow its sys.path set-up.

def _path_setup_violations(path: Path) -> str | None:
    """The first top-level ``scripts`` import that precedes the file's
    top-level ``sys.path`` set-up, or ``None``."""
    body = ast.parse(path.read_text()).body

    def is_path_setup(node: ast.stmt) -> bool:
        return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and ast.unparse(node.value.func) in ("sys.path.insert", "sys.path.append"))

    def is_scripts_import(node: ast.stmt) -> bool:
        if isinstance(node, ast.ImportFrom):
            return (node.module or "").split(".")[0] == "scripts" and node.level == 0
        return isinstance(node, ast.Import) and any(
            a.name.split(".")[0] == "scripts" for a in node.names)

    setup = next((i for i, n in enumerate(body) if is_path_setup(n)), None)
    if setup is None:
        return None
    early = next((n for n in body[:setup] if is_scripts_import(n)), None)
    return None if early is None else f"{path.name}:{early.lineno}"


def test_r2_5_no_launcher_imports_scripts_before_its_path_setup():
    """Static, over every script: the defect R2-5 found in
    ``stride55_score.py`` (an import placed above the set-up it needs)."""
    violations = [v for f in sorted((REPO / "scripts").glob("*.py"))
                  if (v := _path_setup_violations(f))]
    assert violations == []


def test_r2_5_the_check_sees_the_reviewed_defect(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("import sys\nfrom scripts.lib_advanced_metrics import X\n"
                   "sys.path.insert(0, '.')\n")
    assert _path_setup_violations(bad) == "bad.py:2"


_STANDALONE_LAUNCHERS = ["stride55_score.py", "6_accuracy_report.py",
                         "analyse_study_effects.py", "verify_phase2a_metrics.py"]


@pytest.mark.parametrize("name", _STANDALONE_LAUNCHERS)
def test_r2_5_launcher_prelude_runs_in_a_clean_interpreter(tmp_path, name):
    """Each launcher's module prelude (everything but ``main``) runs under
    ``python -I`` from an unrelated directory: no PYTHONPATH, no user site,
    no script directory on the path, so ``scripts`` resolves only through
    the launcher's own set-up."""
    import subprocess

    code = ("import runpy, sys; "
            "runpy.run_path(sys.argv[1], run_name='__prelude_check__')")
    done = subprocess.run([sys.executable, "-I", "-c", code, str(REPO / "scripts" / name)],
                          cwd=tmp_path, capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stderr[-2000:]


def test_r2_5_stride55_help_runs_standalone(tmp_path):
    """The documented form, ``python scripts/stride55_score.py``, with
    ``--help`` so nothing is scored."""
    import subprocess

    done = subprocess.run([sys.executable, "-I", str(REPO / "scripts/stride55_score.py"),
                           "--help"], cwd=tmp_path, capture_output=True, text=True,
                          timeout=120)
    assert done.returncode == 0, done.stderr[-2000:]
    assert "usage" in done.stdout.lower()


# R2-6: the nullable string dtype's missing value is a blank sheet.

@pytest.mark.parametrize("value", [None, float("nan"), pd.NA, pd.NaT, "", "  "])
def test_r2_6_every_scalar_null_is_a_blank_sheet(value):
    assert lam._blank_sheet(value) is True


def test_r2_6_a_named_sheet_is_not_blank():
    assert lam._blank_sheet(SHEET_A) is False


def test_r2_6_an_all_missing_nullable_string_sheet_column_is_refused():
    """``pd.Series([None, ...], dtype="string")`` holds ``pd.NA``. Every
    in-frame reference then records no sheet, so the count is the in-frame
    population, not zero, and the named refusal follows."""
    bounds, refs = synthetic_bounds(), synthetic_refs()
    refs["Map"] = pd.Series([None] * len(refs), dtype="string", index=refs.index)
    assert refs["Map"].isna().all() and refs["Map"].iloc[0] is pd.NA
    n = lam.unattributed_references_in_frame(refs, bounds)
    assert n == lam._n_in_frame_union(refs, bounds) > 0
    det = merged_detections(synthetic_refs(), bounds)
    result = calculate_tile_classification(det, refs, bounds)
    assert result["reason"] == TILE_JOIN_REASON_UNATTRIBUTED_REFERENCE
