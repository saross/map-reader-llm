"""
The perfect-detector test, made permanent (tile-join Wave 1, W1.2).

Standing rule (PI, 2026-11-01; ``docs/agent-guidance.md``): every scorer and
every metric gets a tier-1 test that feeds the ground truth back as the
prediction, in every shape the pipeline produces, and asserts the perfect
score. A metric that cannot give a flawless pipeline a perfect score is
measuring the scorer. The published tile join (``id``) gave a perfect merged
detector tile-MCC 0.8711 on the Era-2 frame (D72); PI rulings D72 and D73
replaced it with two sheet-specific joins, ``sheet-contains`` for tile
classification and ``sheet-primary`` for the per-tile count tables.

What this module pins (``planning/tile-join-wave-1-spec-2026-11-01.md``,
W1.2):

* the real Era-2 frame with the gold-standard (GS) references, as two named
  fixtures: ``historical_alphabetical`` (a merged point named for the
  alphabetically first containing tile, any sheet: the S167 construction)
  and ``sheet_preserving`` (each reference keeps its own sheet: 224
  reference-positive and 263 reference-negative tiles, MCC 1);
* synthetic overlapping frames with a sheet seam and padding, built once
  with references recording their sheet in ``Map`` and once in
  ``source_map``;
* merged, unmerged (with and without the real within-pass deduplication)
  and replicated shapes; count-table sums overall and per sheet;
* the edge cases, the unattributed-detection outcomes, tie-break and
  boundary, the replay and provenance regressions (the
  ``selection_aware_intervals.py`` MCC branch among them), and the legacy
  sentinel: ``id`` on the merged Era-2 input gives MCC 0.8711 (TP 196, FP 0,
  FN 33, TN 258) on both fixtures;
* Astra's consumer audit (2026-11-18): C1, the count-table rule reaching
  every leaf of the resampling helpers, both arms included; C3, both rules
  written into the corrected-F1 engine's own artefact.

Run: ``python -m pytest tests/test_perfect_detector.py -m tier1 -q``.

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-11-18 | Apache 2.0
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point, box

import scripts.lib_advanced_metrics as lam
from scripts.lib_advanced_metrics import (
    TILE_JOIN_CLASSIFICATION_DEFAULT,
    TILE_JOIN_COUNT_TABLE_DEFAULT,
    TILE_JOIN_REASON_DETECTION_SHORTFALL,
    TILE_JOIN_REASON_NO_SOURCE_TILE,
    TILE_JOIN_REASON_UNATTRIBUTED_DETECTION,
    TileJoinProvenanceError,
    TileJoinRefusalError,
    calculate_f1_internal,
    calculate_tile_classification,
    compute_per_tile_tp_fp_fn,
    frame_tile_sheets,
    per_sheet_confusion,
    recorded_tile_joins,
    scope_detections_to_frame,
    sheet_join_candidate_tiles,
    sheet_primary_tiles,
)

pytestmark = pytest.mark.tier1

REPO = Path(__file__).resolve().parent.parent
ERA2_BOUNDS = REPO / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
GS_REFERENCES = REPO / "inputs/vectors/references/mounds-reference.geojson"
CRS = "EPSG:32635"

#: Two real study sheet names (so ruling D50's catalogue knows them), used on
#: SYNTHETIC geometry. The geometry is invented; only the names are real.
SHEET_A = "K-35-052-4_32635"
SHEET_B = "K-35-053-3_Elenovo"


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _tile(sheet: str, x: int, y: int) -> str:
    """A tile name in the pipeline's ``<sheet>_x<N>_y<N>.png`` vocabulary."""
    return f"{sheet}_x{x}_y{y}.png"


def _counts(table: pd.DataFrame) -> dict[str, int]:
    """Total TP, FP and FN of a per-tile count table."""
    return {k: int(table[k].sum()) for k in ("tp", "fp", "fn")}


def _confusion(result: dict) -> tuple[int, int, int, int]:
    """(TP, FP, FN, TN) of a classification result."""
    return result["tp"], result["fp"], result["fn"], result["tn"]


def _positive_tiles(result: dict) -> set[str]:
    """The reference-positive tiles of a classification result."""
    return {d["tile_name"] for d in result["tile_details"] if d["has_mounds"]}


def _own_sheet_tiles(points: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
                     column: str) -> list[list[str]]:
    """Each point's containing tiles ON ITS OWN SHEET, computed in the test.

    Independent of the scorer: a tile is on a sheet when its name starts
    with the sheet name, and a point is in a tile when the polygon
    intersects it (shapely only).
    """
    out = []
    for geom, sheet in zip(points.geometry, points[column]):
        out.append(sorted(
            str(name) for name, poly in zip(bounds["tile_name"], bounds.geometry)
            if str(name).startswith(f"{sheet}_x") and poly.intersects(geom)
        ))
    return out


# ═══════════════════════════════════════════════════════════════════════════
# The synthetic frame: two sheets, a seam, and padding
# ═══════════════════════════════════════════════════════════════════════════
#
# 100 m tiles on an 80 m stride, so neighbouring tiles of one sheet overlap
# by 20 m. Sheet A's tiles start at x = 0; sheet B's at x = 200. A's
# ``x240`` tile is PADDING beyond A's map content: it overlaps B's tiles and
# holds no A reference. Row y = 0 holds the references; row y = 200 is empty
# on both sheets (true-negative tiles).
#
#   x:   0     80   100  160  180 200  240 260  280 300   340  380
#   A0   [----------]
#   A80        [----------]
#   A160            [----------]
#   A240 (padding)            [----------]
#   B200                    [----------]
#   B280                             [----------]

ORIGIN_X, ORIGIN_Y = 500_000.0, 4_700_000.0

SYN_TILES = [
    (SHEET_A, 0, 0), (SHEET_A, 80, 0), (SHEET_A, 160, 0), (SHEET_A, 240, 0),
    (SHEET_B, 200, 0), (SHEET_B, 280, 0),
    (SHEET_A, 0, 200), (SHEET_B, 280, 200),
]

#: (sheet, x, y) of each synthetic reference mound.
SYN_REFS = [
    (SHEET_A, 50, 50),    # in A0 only
    (SHEET_A, 90, 50),    # in A0 and A80: within-sheet overlap
    (SHEET_A, 170, 50),   # in A80 and A160
    (SHEET_B, 250, 50),   # in B200, and in A160 and A240 (cross-sheet contact)
    (SHEET_B, 330, 50),   # in B280, and in A240 (cross-sheet contact, padding)
]


def synthetic_bounds() -> gpd.GeoDataFrame:
    """The synthetic frame's tile polygons."""
    names, geoms = [], []
    for sheet, x, y in SYN_TILES:
        names.append(_tile(sheet, x, y))
        geoms.append(box(ORIGIN_X + x, ORIGIN_Y + y,
                         ORIGIN_X + x + 100, ORIGIN_Y + y + 100))
    return gpd.GeoDataFrame({"tile_name": names}, geometry=geoms, crs=CRS)


def synthetic_refs(column: str = "Map") -> gpd.GeoDataFrame:
    """The synthetic references, recording their sheet in ``column``."""
    return gpd.GeoDataFrame(
        {column: [s for s, _, _ in SYN_REFS]},
        geometry=[Point(ORIGIN_X + x, ORIGIN_Y + y) for _, x, y in SYN_REFS],
        crs=CRS,
    )


def merged_detections(refs: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
                      column: str = "Map") -> gpd.GeoDataFrame:
    """The perfect MERGED detector: one point per mound, on its own sheet.

    ``source_tiles`` lists the mound's own-sheet containing tiles (sorted,
    as ``merge_passes.py`` stores them) and ``source_tile`` is the first.
    """
    own = _own_sheet_tiles(refs, bounds, column)
    det = gpd.GeoDataFrame(geometry=list(refs.geometry), crs=refs.crs)
    det["source_tiles"] = [json.dumps(t) for t in own]
    det["source_tile"] = [t[0] for t in own]
    return det


def unmerged_detections(refs: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
                        column: str = "Map") -> gpd.GeoDataFrame:
    """The perfect UNMERGED detector: one point per (mound, own-sheet tile)."""
    rows = []
    for geom, tiles in zip(refs.geometry, _own_sheet_tiles(refs, bounds, column)):
        for name in tiles:
            rows.append({"geometry": geom, "source_tile": name})
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=refs.crs)


# ═══════════════════════════════════════════════════════════════════════════
# The real Era-2 frame: two named fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def era2() -> dict[str, Any]:
    """The Era-2 frame, the in-frame GS references and both merged fixtures.

    Both inputs are git-tracked (checked with ``git ls-files`` on
    2026-11-18), so this fixture never skips: a missing file is a failure.
    """
    bounds = gpd.read_file(ERA2_BOUNDS).to_crs(CRS)
    refs = gpd.read_file(GS_REFERENCES).to_crs(CRS)
    hits = gpd.sjoin(refs[["geometry"]].reset_index(),
                     bounds[["tile_name", "geometry"]], predicate="intersects")
    containing = hits.groupby("index")["tile_name"].apply(sorted)
    refs_in = refs.loc[containing.index].copy()

    # historical_alphabetical: the S167 construction — the alphabetically
    # first containing tile, of ANY sheet. Not a valid fixture under D50
    # (it re-keys 15 Elenovo mounds onto K-35-052-4), kept to prove the
    # classification defect.
    historical = refs_in.copy()
    historical["source_tile"] = containing.map(lambda names: names[0])
    # sheet_preserving: each mound's first containing tile ON ITS OWN SHEET,
    # with its own-sheet tiles as the recorded origins.
    preserving = merged_detections(refs_in, bounds, "Map")
    return {"bounds": bounds, "refs": refs_in, "containing": containing,
            "historical_alphabetical": historical,
            "sheet_preserving": preserving}


class TestRealFrame:
    """The GS references on the Era-2 frame (487 tiles)."""

    def test_sheet_preserving_is_perfect_under_the_defaults(self, era2):
        """224 positive and 263 negative tiles, MCC 1 (Astra's probe), and F1 1."""
        result = calculate_tile_classification(
            era2["sheet_preserving"], era2["refs"], era2["bounds"])
        assert result["tile_join"] == TILE_JOIN_CLASSIFICATION_DEFAULT
        assert _confusion(result) == (224, 0, 0, 263)
        assert result["mcc"] == pytest.approx(1.0)
        assert result["sensitivity"] == pytest.approx(1.0)
        assert result["specificity"] == pytest.approx(1.0)
        p, r, f1 = calculate_f1_internal(
            era2["sheet_preserving"], era2["refs"], era2["bounds"], 20)
        assert (p, r, f1) == (pytest.approx(1.0),) * 3

    @pytest.mark.parametrize("fixture", ["historical_alphabetical", "sheet_preserving"])
    def test_legacy_sentinel_id_gives_0_8711(self, era2, fixture):
        """The defect stays documented: ``id`` on merged output is not perfect."""
        result = calculate_tile_classification(
            era2[fixture], era2["refs"], era2["bounds"], tile_join="id")
        assert _confusion(result) == (196, 0, 33, 258)
        assert round(result["mcc"], 4) == 0.8711

    def test_historical_alphabetical_is_not_a_valid_d50_fixture(self, era2):
        """Re-keying 15 Elenovo mounds onto K-35-052-4 cannot score perfectly."""
        result = calculate_tile_classification(
            era2["historical_alphabetical"], era2["refs"], era2["bounds"])
        assert result["mcc"] < 1.0
        _, _, f1 = calculate_f1_internal(
            era2["historical_alphabetical"], era2["refs"], era2["bounds"], 20)
        assert f1 < 1.0

    def test_reference_positive_tiles_recomputed_independently(self, era2):
        """G1 item 4: positives = tiles holding one of their own sheet's mounds."""
        result = calculate_tile_classification(
            era2["sheet_preserving"], era2["refs"], era2["bounds"])
        expected = set()
        for name, poly in zip(era2["bounds"]["tile_name"], era2["bounds"].geometry):
            for geom, sheet in zip(era2["refs"].geometry, era2["refs"]["Map"]):
                if str(name).startswith(f"{sheet}_x") and poly.intersects(geom):
                    expected.add(str(name))
                    break
        assert _positive_tiles(result) == expected
        assert len(expected) == 224

    def test_k35_052_4_x4032_edge_tiles_not_positive_for_elenovo(self, era2):
        """Real-data regression: padding tiles do not become positive (D73 (2))."""
        frame_wide = calculate_tile_classification(
            era2["sheet_preserving"], era2["refs"], era2["bounds"],
            tile_join="geometric-contains")
        sheet = calculate_tile_classification(
            era2["sheet_preserving"], era2["refs"], era2["bounds"])
        only_frame_wide = _positive_tiles(frame_wide) - _positive_tiles(sheet)
        assert only_frame_wide, "the frame-wide join should reach the edge tiles"
        assert _positive_tiles(sheet) <= _positive_tiles(frame_wide)
        for name in only_frame_wide:
            assert name.startswith("K-35-052-4_32635_x4032_"), name
            poly = era2["bounds"].set_index("tile_name").loc[name].geometry
            inside = era2["refs"][era2["refs"].intersects(poly)]
            assert set(inside["Map"]) == {"K-35-053-3_Elenovo"}

    @pytest.mark.parametrize("fixture", ["historical_alphabetical", "sheet_preserving"])
    def test_sheet_primary_count_table_sums_overall_and_per_sheet(self, era2, fixture):
        """The count table decomposes the symbol totals, overall and per sheet."""
        det, refs, bounds = era2[fixture], era2["refs"], era2["bounds"]
        table = compute_per_tile_tp_fp_fn(det, refs, bounds, 20)
        assert table.attrs["count_table_join"] == TILE_JOIN_COUNT_TABLE_DEFAULT
        per_sheet = per_sheet_confusion(det, refs, bounds, 20)
        totals = np.sum(list(per_sheet.values()), axis=0)
        assert _counts(table) == dict(zip(("tp", "fp", "fn"), map(int, totals)))
        sheets = dict(zip(bounds["tile_name"].astype(str), frame_tile_sheets(bounds)))
        table["sheet"] = table["tile_name"].map(sheets)
        for sheet, (tp, fp, fn) in per_sheet.items():
            part = table[table["sheet"] == sheet]
            assert _counts(part) == {"tp": tp, "fp": fp, "fn": fn}, sheet

    def test_unmerged_is_perfect_tile_classification(self, era2):
        """One point per (mound, own-sheet tile): classification perfect."""
        det = unmerged_detections(era2["refs"], era2["bounds"], "Map")
        result = calculate_tile_classification(det, era2["refs"], era2["bounds"])
        assert _confusion(result) == (224, 0, 0, 263)


# ═══════════════════════════════════════════════════════════════════════════
# Synthetic frames, built with Map and with source_map
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(params=["Map", "source_map"])
def syn(request) -> dict[str, Any]:
    """The synthetic frame with references recording their sheet in one column."""
    column = request.param
    bounds = synthetic_bounds()
    refs = synthetic_refs(column)
    return {"bounds": bounds, "refs": refs, "column": column,
            "merged": merged_detections(refs, bounds, column)}


class TestSyntheticSeam:
    """Merged, unmerged and replicated perfect detectors at a seam."""

    def test_merged_perfect_under_defaults(self, syn):
        result = calculate_tile_classification(syn["merged"], syn["refs"], syn["bounds"])
        # Positive: A0, A80, A160, B200, B280. Negative: A240 (padding), the
        # two empty-row tiles.
        assert _confusion(result) == (5, 0, 0, 3)
        assert result["mcc"] == pytest.approx(1.0)
        assert _positive_tiles(result) == {
            _tile(SHEET_A, 0, 0), _tile(SHEET_A, 80, 0), _tile(SHEET_A, 160, 0),
            _tile(SHEET_B, 200, 0), _tile(SHEET_B, 280, 0)}
        p, r, f1 = calculate_f1_internal(syn["merged"], syn["refs"], syn["bounds"], 20)
        assert (p, r, f1) == (pytest.approx(1.0),) * 3

    def test_frame_wide_contains_makes_padding_positive(self, syn):
        """The defect the sheet join removes: A240 is positive frame-wide."""
        result = calculate_tile_classification(
            syn["merged"], syn["refs"], syn["bounds"], tile_join="geometric-contains")
        assert _tile(SHEET_A, 240, 0) in _positive_tiles(result)

    def test_cross_sheet_contacts_are_reported(self, syn):
        result = calculate_tile_classification(syn["merged"], syn["refs"], syn["bounds"])
        refs_diag = result["tile_join_diagnostics"]["references"]
        assert refs_diag["n_cross_sheet_contacts"] == 2
        assert refs_diag["n_sheet_scoped"] == refs_diag["n_assigned"] == 5

    def test_count_table_sums_overall_and_per_sheet(self, syn):
        table = compute_per_tile_tp_fp_fn(syn["merged"], syn["refs"], syn["bounds"], 20)
        assert _counts(table) == {"tp": 5, "fp": 0, "fn": 0}
        per_sheet = per_sheet_confusion(syn["merged"], syn["refs"], syn["bounds"], 20)
        assert per_sheet == {SHEET_A: (3, 0, 0), SHEET_B: (2, 0, 0)}
        a_rows = table[table["tile_name"].str.startswith(SHEET_A)]
        assert _counts(a_rows) == {"tp": 3, "fp": 0, "fn": 0}
        # The B mound in A's padding is booked to B, never to A240.
        assert int(table.set_index("tile_name").loc[_tile(SHEET_A, 240, 0), "tp"]) == 0

    def test_unmerged_classification_perfect_symbol_penalised(self, syn):
        det = unmerged_detections(syn["refs"], syn["bounds"], syn["column"])
        result = calculate_tile_classification(det, syn["refs"], syn["bounds"])
        assert result["mcc"] == pytest.approx(1.0)
        n_extra = len(det) - len(syn["refs"])
        assert n_extra > 0
        p, r, _ = calculate_f1_internal(det, syn["refs"], syn["bounds"], 20)
        assert r == pytest.approx(1.0)
        assert p == pytest.approx(len(syn["refs"]) / len(det))

    def test_unmerged_through_real_dedup_is_perfect(self, syn):
        """The real within-pass deduplication restores symbol F1 1.0."""
        from scripts.lib_consensus import deduplicate_within_pass

        det = unmerged_detections(syn["refs"], syn["bounds"], syn["column"])
        features = [{"geometry": {"type": "Point", "coordinates": [g.x, g.y]},
                     "properties": {"source_tile": t}}
                    for g, t in zip(det.geometry, det["source_tile"])]
        deduped = deduplicate_within_pass(features)
        merged = gpd.GeoDataFrame(
            {"source_tiles": [json.dumps(d["source_tiles"]) for d in deduped],
             "source_tile": [d["source_tiles"][0] for d in deduped]},
            geometry=[Point(*d["centroid"]) for d in deduped], crs=CRS)
        assert len(merged) == len(syn["refs"])
        p, r, f1 = calculate_f1_internal(merged, syn["refs"], syn["bounds"], 20)
        assert (p, r, f1) == (pytest.approx(1.0),) * 3
        result = calculate_tile_classification(merged, syn["refs"], syn["bounds"])
        assert result["mcc"] == pytest.approx(1.0)

    def test_replicated_runs(self, syn):
        """Per-run means, pooled counts and run_1's confusion, each tested."""
        from scripts.evaluate_detections import (
            evaluate_multi_run_mean,
            evaluate_single_run,
        )

        runs = [evaluate_single_run(
            syn["merged"].copy(), syn["refs"], syn["bounds"], buffers=[20],
            n_bootstrap=20, seed=42, label=f"run_{i}", compute_mcc=True)
            for i in (1, 2, 3)]
        for run in runs:
            assert run["buffers"][0]["f1"] == pytest.approx(1.0)
            assert run["tile_classification"]["confusion"] == {
                "tp": 5, "tn": 3, "fp": 0, "fn": 0}
        summary = evaluate_multi_run_mean(runs, label="replicated")
        assert summary["buffers"][0]["f1"] == pytest.approx(1.0)
        assert summary["buffers"][0]["count_table_join"] == TILE_JOIN_COUNT_TABLE_DEFAULT
        tile = summary["tile_classification"]
        assert tile["confusion_source"] == "run_1"
        assert tile["confusion"] == runs[0]["tile_classification"]["confusion"]
        assert tile["mcc"]["point"] == pytest.approx(1.0)
        assert tile["tile_join"] == TILE_JOIN_CLASSIFICATION_DEFAULT
        pooled = sum(_counts(compute_per_tile_tp_fp_fn(
            syn["merged"], syn["refs"], syn["bounds"], 20))["tp"] for _ in runs)
        assert pooled == 3 * len(syn["refs"])


def test_one_reference_two_identical_predictions():
    """Without deduplication: TP 1, FP 1, FN 0, precision 0.5, F1 2/3."""
    bounds = synthetic_bounds()
    refs = gpd.GeoDataFrame({"Map": [SHEET_A]},
                            geometry=[Point(ORIGIN_X + 50, ORIGIN_Y + 50)], crs=CRS)
    name = _tile(SHEET_A, 0, 0)
    det = gpd.GeoDataFrame({"source_tile": [name, name]},
                           geometry=[refs.geometry[0]] * 2, crs=CRS)
    assert per_sheet_confusion(det, refs, bounds, 20)[SHEET_A] == (1, 1, 0)
    p, r, f1 = calculate_f1_internal(det, refs, bounds, 20)
    assert (p, r, f1) == (pytest.approx(0.5), pytest.approx(1.0), pytest.approx(2 / 3))


# ═══════════════════════════════════════════════════════════════════════════
# Edge cases (Astra, S6)
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCases:

    def test_exact_tile_label_alignment(self):
        """Unmerged per-tile output: id and sheet-contains agree, both perfect."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = unmerged_detections(refs, bounds)
        by_id = calculate_tile_classification(det, refs, bounds, tile_join="id")
        by_sheet = calculate_tile_classification(det, refs, bounds)
        assert by_sheet["mcc"] == pytest.approx(1.0)
        named = set(det["source_tile"])

        def detected(result: dict) -> set[str]:
            return {d["tile_name"] for d in result["tile_details"] if d["has_detections"]}

        # Each label names exactly the tile the point lies in, so the name
        # rule and the sheet rule book the same detected tiles.
        assert detected(by_id) == detected(by_sheet) == named

    def test_permuted_input_order(self):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        order = list(range(len(det)))
        random.Random(7).shuffle(order)
        shuffled = det.iloc[order]
        bounds_rev = bounds.iloc[::-1]
        for a, b in ((det, shuffled),):
            ra = calculate_tile_classification(a, refs, bounds)
            rb = calculate_tile_classification(b, refs, bounds_rev)
            assert _confusion(ra) == _confusion(rb)
            ta = compute_per_tile_tp_fp_fn(a, refs, bounds, 20).set_index("tile_name")
            tb = compute_per_tile_tp_fp_fn(b, refs, bounds_rev, 20).set_index("tile_name")
            pd.testing.assert_frame_equal(ta.sort_index(), tb.sort_index())

    def test_differing_tile_vocabularies_withheld_to_valid(self):
        """A foreign vocabulary of the same sheet: id refuses, the sheet join scores."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds).drop(columns="source_tiles")
        # Same sheets, another tiling's offsets: no name is a frame tile.
        det["source_tile"] = [f"{s}_x{7 + i}_y{7 + i}.png"
                              for i, s in enumerate(refs["Map"])]
        by_id = calculate_tile_classification(det, refs, bounds, tile_join="id")
        assert by_id["reason"] == TILE_JOIN_REASON_DETECTION_SHORTFALL
        by_sheet = calculate_tile_classification(det, refs, bounds)
        assert by_sheet["mcc"] == pytest.approx(1.0)

    def test_withheld_to_valid_in_the_evaluator(self):
        from scripts.evaluate_detections import evaluate_single_run

        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds).drop(columns="source_tiles")
        det["source_tile"] = [f"{s}_x{7 + i}_y{7 + i}.png"
                              for i, s in enumerate(refs["Map"])]
        legacy = evaluate_single_run(det.copy(), refs, bounds, [20], n_bootstrap=20,
                                     compute_mcc=True, tile_join="id",
                                     count_table_join="id")
        assert legacy["tile_join_withheld"]["reason"] == TILE_JOIN_REASON_DETECTION_SHORTFALL
        assert legacy["tile_classification"]["withheld"] is True
        new = evaluate_single_run(det.copy(), refs, bounds, [20], n_bootstrap=20,
                                  compute_mcc=True)
        assert "tile_join_withheld" not in new
        assert new["tile_classification"]["mcc"]["point"] == pytest.approx(1.0)
        assert legacy["buffers"][0]["f1"] == new["buffers"][0]["f1"]

    def test_missing_origins_keep_d50_attribution(self):
        """No ``source_tiles`` list but a valid ``source_tile``: scored, no refusal."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds).drop(columns="source_tiles")
        result = calculate_tile_classification(det, refs, bounds)
        assert result["mcc"] == pytest.approx(1.0)
        compute_per_tile_tp_fp_fn(det, refs, bounds, 20)  # does not raise

    def test_cross_sheet_origin_books_on_the_origin_sheet(self):
        """A row re-keyed to A but seen on B is booked on B (D50 restores it)."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        b_row = 3  # the B mound at x = 250, inside A160 and A240 too
        det.loc[det.index[b_row], "source_tile"] = _tile(SHEET_A, 160, 0)
        scope = scope_detections_to_frame(det, bounds)
        assert scope.diagnostics["n_origin_restored"] == 1
        result = calculate_tile_classification(det, refs, bounds)
        assert result["mcc"] == pytest.approx(1.0)
        table = compute_per_tile_tp_fp_fn(det, refs, bounds, 20).set_index("tile_name")
        assert int(table.loc[_tile(SHEET_B, 200, 0), "tp"]) == 1

    def test_reduced_frame_with_parent(self):
        """A frame of sheet A alone, scored with its parent, is the parent's share."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        reduced = bounds[bounds["tile_name"].str.startswith(SHEET_A)]
        part = calculate_tile_classification(det, refs, reduced, parent_bounds=bounds)
        whole = calculate_tile_classification(det, refs, bounds)
        whole_a = {d["tile_name"]: d["classification"] for d in whole["tile_details"]
                   if d["tile_name"].startswith(SHEET_A)}
        assert {d["tile_name"]: d["classification"]
                for d in part["tile_details"]} == whole_a
        assert part["detection_scope"]["n_parent_elsewhere"] == 2

    def test_empty_detection_set(self):
        """No detections: every positive tile is FN; the evaluator skips MCC."""
        from scripts.evaluate_detections import evaluate_single_run

        bounds, refs = synthetic_bounds(), synthetic_refs()
        empty = gpd.GeoDataFrame({"source_tile": pd.Series([], dtype=object)},
                                 geometry=[], crs=CRS)
        result = calculate_tile_classification(empty, refs, bounds)
        assert _confusion(result) == (0, 0, 5, 3)
        assert result["mcc"] is None
        table = compute_per_tile_tp_fp_fn(empty, refs, bounds, 20)
        assert _counts(table) == {"tp": 0, "fp": 0, "fn": 5}
        run = evaluate_single_run(empty, refs, bounds, [20], n_bootstrap=20,
                                  compute_mcc=True)
        assert "tile_classification" not in run
        assert "count_table_join" not in run["buffers"][0]

    def test_degenerate_mcc_tn_plus_fn_zero(self):
        """Every tile predicted populated: TN + FN = 0, MCC undefined."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        centres = [g.centroid for g in bounds.geometry]
        det = gpd.GeoDataFrame({"source_tile": list(bounds["tile_name"])},
                               geometry=centres, crs=CRS)
        result = calculate_tile_classification(det, refs, bounds)
        assert result["tn"] + result["fn"] == 0
        assert result["mcc"] is None


# ═══════════════════════════════════════════════════════════════════════════
# Unattributed detections (W1.1; Astra, S2.1)
# ═══════════════════════════════════════════════════════════════════════════


class TestUnattributed:

    def _no_columns(self) -> tuple:
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = gpd.GeoDataFrame(geometry=list(refs.geometry), crs=CRS)
        return det, refs, bounds

    def test_no_origin_columns_refused_under_sheet_joins(self):
        det, refs, bounds = self._no_columns()
        result = calculate_tile_classification(det, refs, bounds)
        assert result["reason"] == TILE_JOIN_REASON_UNATTRIBUTED_DETECTION
        assert result["n_unattributed_in_frame"] == len(det)
        with pytest.raises(TileJoinRefusalError) as caught:
            compute_per_tile_tp_fp_fn(det, refs, bounds, 20)
        assert caught.value.reason == TILE_JOIN_REASON_UNATTRIBUTED_DETECTION
        record = lam.describe_tile_join_refusal(det, refs, bounds, "sheet-primary")
        assert record["reason"] == TILE_JOIN_REASON_UNATTRIBUTED_DETECTION
        assert record["tile_join"] == "sheet-primary"

    def test_no_origin_columns_keep_historical_behaviour(self):
        det, refs, bounds = self._no_columns()
        frame_wide = calculate_tile_classification(
            det, refs, bounds, tile_join="geometric-contains")
        assert "error" not in frame_wide  # booked by position, as before
        by_id = calculate_tile_classification(det, refs, bounds, tile_join="id")
        assert by_id["reason"] == TILE_JOIN_REASON_NO_SOURCE_TILE

    def test_null_source_tile_in_frame_refused(self):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds).drop(columns="source_tiles")
        det.loc[det.index[0], "source_tile"] = None
        result = calculate_tile_classification(det, refs, bounds)
        assert result["reason"] == TILE_JOIN_REASON_UNATTRIBUTED_DETECTION
        assert result["n_unattributed_in_frame"] == 1

    def test_d50_exclusion_is_not_a_refusal(self):
        """Seen only on a sheet the frame leaves out: excluded and named."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        reduced = bounds[bounds["tile_name"].str.startswith(SHEET_A)]
        det = merged_detections(refs, bounds)
        result = calculate_tile_classification(det, refs, reduced)
        assert "error" not in result
        excl = result["tile_join_diagnostics"]["detections"]["exclusions"]
        assert excl["n_origin_excluded"] == 2
        assert excl["n_unattributed_in_frame"] == 0

    def test_out_of_frame_for_own_sheet_is_not_a_refusal(self):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds).drop(columns="source_tiles")
        # A point attributed to A that lies only in B's tile B280.
        det.loc[det.index[4], "source_tile"] = _tile(SHEET_A, 0, 0)
        det.loc[det.index[4], "geometry"] = Point(ORIGIN_X + 370, ORIGIN_Y + 50)
        result = calculate_tile_classification(det, refs, bounds)
        assert "error" not in result
        excl = result["tile_join_diagnostics"]["detections"]["exclusions"]
        assert excl["n_out_of_frame"] == 1

    def test_parent_frame_exclusion_is_not_a_refusal(self):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        reduced = bounds[bounds["tile_name"].str.startswith(SHEET_A)]
        det = merged_detections(refs, bounds)
        result = calculate_tile_classification(det, refs, reduced, parent_bounds=bounds)
        assert "error" not in result
        excl = result["tile_join_diagnostics"]["detections"]["exclusions"]
        assert excl["n_parent_elsewhere"] == 2


# ═══════════════════════════════════════════════════════════════════════════
# Tie-break and boundary (W1.1; Astra, S2.3)
# ═══════════════════════════════════════════════════════════════════════════


class TestTieBreakAndBoundary:

    def test_tie_goes_to_smaller_tile_name_whatever_the_order(self):
        bounds = synthetic_bounds()
        sheet_a = bounds[bounds["tile_name"].str.startswith(SHEET_A)]
        point = gpd.GeoDataFrame(geometry=[Point(ORIGIN_X + 90, ORIGIN_Y + 50)], crs=CRS)
        expected = _tile(SHEET_A, 0, 0)
        assert sheet_primary_tiles(point, sheet_a) == [expected]
        assert sheet_primary_tiles(point, sheet_a.iloc[::-1]) == [expected]

    def test_point_on_shared_edge_is_candidate_for_both(self):
        bounds = gpd.GeoDataFrame(
            {"tile_name": [_tile(SHEET_A, 0, 0), _tile(SHEET_A, 100, 0)]},
            geometry=[box(0, 0, 100, 100), box(100, 0, 200, 100)], crs=CRS)
        point = gpd.GeoDataFrame(geometry=[Point(100, 50)], crs=CRS)
        assert sheet_join_candidate_tiles(point, SHEET_A, bounds, bounds) == [
            [_tile(SHEET_A, 0, 0), _tile(SHEET_A, 100, 0)]]

    def test_non_intersecting_tile_is_never_a_candidate(self):
        bounds = gpd.GeoDataFrame(
            {"tile_name": [_tile(SHEET_A, 0, 0), _tile(SHEET_A, 101, 0)]},
            geometry=[box(0, 0, 100, 100), box(101, 0, 110, 10)], crs=CRS)
        point = gpd.GeoDataFrame(geometry=[Point(99, 5)], crs=CRS)
        assert sheet_primary_tiles(point, bounds) == [_tile(SHEET_A, 0, 0)]


# ═══════════════════════════════════════════════════════════════════════════
# Replay and provenance regressions (Astra, round 2)
# ═══════════════════════════════════════════════════════════════════════════


class TestReplayAndProvenance:

    def test_tile_join_default_is_retired(self):
        assert not hasattr(lam, "TILE_JOIN_DEFAULT")
        with pytest.raises(ImportError):
            exec("from scripts.lib_advanced_metrics import TILE_JOIN_DEFAULT", {})

    def test_default_calls_use_the_new_rules(self):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        assert calculate_tile_classification(det, refs, bounds)["tile_join"] == (
            "sheet-contains")
        table = compute_per_tile_tp_fp_fn(det, refs, bounds, 20)
        assert table.attrs["count_table_join"] == "sheet-primary"
        ci = lam.bootstrap_ci(det, refs, bounds, n_iterations=20, random_seed=1)
        assert ci["count_table_join"] == "sheet-primary"

    def test_explicit_historical_calls_keep_historical_behaviour(self):
        """``id`` books TP/FP by name; a name off the frame is a shortfall."""
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        table = compute_per_tile_tp_fp_fn(det, refs, bounds, 20, tile_join="id")
        assert table.attrs["count_table_join"] == "id"
        by_name = table.set_index("tile_name")
        for name in det["source_tile"]:
            assert by_name.loc[name, "tp"] >= 1

    def test_containment_joins_refused_for_count_tables(self):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        for join in ("geometric-contains", "sheet-contains"):
            with pytest.raises(ValueError, match="D72 \\(2\\)"):
                compute_per_tile_tp_fp_fn(det, refs, bounds, 20, tile_join=join)

    def test_sheet_primary_refused_for_classification(self):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        with pytest.raises(ValueError, match="classification join"):
            calculate_tile_classification(
                merged_detections(refs, bounds), refs, bounds, tile_join="sheet-primary")

    def test_old_input_falls_back_to_legacy(self):
        old = {"summary": {"tile_classification": {"confusion": {}}},
               "_metadata": {"metadata_version": "1.4", "cli_args": {}}}
        rec = recorded_tile_joins(old)
        assert (rec["classification"], rec["count_table"]) == ("id", "id")
        assert rec["classification_source"] == "legacy-fallback"

    def test_mixed_old_and_new_inputs(self):
        old = {"summary": {}, "_metadata": {"metadata_version": "1.4",
                                            "cli_args": {"tile_join": "geometric-contains"}}}
        new = {"summary": {"tile_classification": {"tile_join": "sheet-contains"},
                           "buffers": [{"count_table_join": "sheet-primary"}]},
               "_metadata": {"metadata_version": "1.5",
                             "tile_joins": {"classification": "sheet-contains",
                                            "count_table": "sheet-primary"}}}
        assert recorded_tile_joins(old)["classification"] == "geometric-contains"
        assert recorded_tile_joins(old)["count_table"] == "id"
        assert recorded_tile_joins(new)["count_table"] == "sheet-primary"

    def test_contradictory_provenance_rejected(self):
        doc = {"summary": {"tile_classification": {"tile_join": "sheet-contains"}},
               "_metadata": {"cli_args": {"tile_join": "id"}}}
        with pytest.raises(TileJoinProvenanceError, match="contradictory"):
            recorded_tile_joins(doc)

    def test_new_output_missing_provenance_rejected(self):
        doc = {"summary": {}, "_metadata": {"metadata_version": "1.5", "cli_args": {}}}
        with pytest.raises(TileJoinProvenanceError, match="historical inputs only"):
            recorded_tile_joins(doc)

    def test_emitted_evaluation_records_both_rules(self, tmp_path):
        """Inspect the artefact evaluate_detections writes, not a return value."""
        from scripts.evaluate_detections import _evaluate_condition, write_outputs

        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        det_path = tmp_path / "detections.geojson"
        det.to_crs("EPSG:4326").to_file(det_path, driver="GeoJSON")
        metadata = {"metadata_version": "1.5", "cli_args": {
            "tile_join": "sheet-contains", "count_table_join": "sheet-primary"},
            "tile_joins": lam.tile_join_provenance("sheet-contains", "sheet-primary")}
        summary = _evaluate_condition(
            [det_path], refs, bounds, buffers=[20, 50], n_bootstrap=20, seed=42,
            label="perfect", output_dir=None, compute_mcc=True, metadata=metadata)
        write_outputs(summary, None, tmp_path / "out", metadata=metadata)
        doc = json.loads((tmp_path / "out" / "evaluation.json").read_text())
        assert all(b["count_table_join"] == "sheet-primary"
                   for b in doc["summary"]["buffers"])
        assert doc["summary"]["tile_classification"]["tile_join"] == "sheet-contains"
        rec = recorded_tile_joins(doc)
        assert (rec["classification"], rec["count_table"]) == (
            "sheet-contains", "sheet-primary")
        assert "D72" in doc["_metadata"]["tile_joins"]["rulings"]

    def test_evaluator_replay_under_id_records_id(self, tmp_path):
        from scripts.evaluate_detections import evaluate_single_run

        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        run = evaluate_single_run(det, refs, bounds, [20], n_bootstrap=20,
                                  compute_mcc=True, tile_join="id",
                                  count_table_join="id")
        assert run["buffers"][0]["count_table_join"] == "id"
        assert run["tile_classification"]["tile_join"] == "id"

    def test_selection_aware_board_mcc_comes_from_classification(
            self, tmp_path, monkeypatch):
        """The default board branch never labels count-arm indicators as MCC."""
        import scripts.selection_aware_intervals as sai

        calls: dict[str, Any] = {}
        counts = np.zeros((2, 3, 3))
        counts[0, 0, 0] = counts[1, 1, 0] = 1

        def fake_classification(board, tile_join, *args, **kwargs):
            calls["classification"] = (tile_join, kwargs.get("count_table_join"))
            has_mounds = np.array([True, True, False])
            has_det = np.array([[True, False, False], [True, True, False]])
            return [{"label": "a"}, {"label": "b"}], counts, has_mounds, has_det

        def fake_counts(*args, **kwargs):
            raise AssertionError("count-arm builder used for board MCC")

        monkeypatch.setattr(sai, "build_board_tile_classification", fake_classification)
        monkeypatch.setattr(sai, "build_board_tile_counts", fake_counts)
        monkeypatch.setattr("sys.argv", ["sai", "--board", "b1", "--metric", "mcc",
                                         "--bootstrap", "20", "--out", str(tmp_path)])
        assert sai.main() == 0
        assert calls["classification"] == ("sheet-contains", "sheet-primary")
        out = json.loads(next(tmp_path.glob("b1_mcc_b*_m1.json")).read_text())
        assert out["mcc_indicators"].startswith("classification arm under 'sheet-contains'")
        assert out["tile_joins"]["count_table"] == "sheet-primary"

    def test_selection_aware_count_arm_mcc_only_for_historical_pair(
            self, tmp_path, monkeypatch):
        import scripts.selection_aware_intervals as sai

        monkeypatch.setattr("sys.argv", ["sai", "--cell", "g512_ov064", "--metric", "mcc",
                                         "--out", str(tmp_path)])
        with pytest.raises(SystemExit):
            sai.main()


# ═══════════════════════════════════════════════════════════════════════════
# Astra's consumer audit: C1 (every leaf, both arms) and C3 (emitted artefact)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def leaf_spy(monkeypatch) -> list[str]:
    """Record the count-table join of every call to the count-table leaf."""
    seen: list[str] = []
    real = lam.compute_per_tile_tp_fp_fn

    def spy(*args, **kwargs):
        seen.append(kwargs.get("tile_join", "<default>"))
        return real(*args, **kwargs)

    monkeypatch.setattr(lam, "compute_per_tile_tp_fp_fn", spy)
    return seen


class TestCountTableReachesEveryLeaf:

    @pytest.mark.parametrize("join", ["id", "sheet-primary"])
    def test_single_run_route(self, leaf_spy, join):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        out = lam.bootstrap_ci(det, refs, bounds, n_iterations=20, random_seed=1,
                               count_table_join=join)
        assert leaf_spy == [join]
        assert out["count_table_join"] == join

    @pytest.mark.parametrize("join", ["id", "sheet-primary"])
    def test_paired_route_both_arms(self, leaf_spy, join):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        out = lam.bootstrap_effect_size_ci(det, bounds, det.iloc[:3], bounds, refs,
                                           n_iterations=20, random_seed=1,
                                           count_table_join=join)
        assert leaf_spy == [join, join]
        assert out["count_table_join"] == join

    @pytest.mark.parametrize("join", ["id", "sheet-primary"])
    def test_multi_run_routes(self, leaf_spy, join):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        runs = [(1, det), (2, det.iloc[:4])]
        out = lam.bootstrap_multi_run_ci(runs, refs, bounds, n_iterations=20,
                                         random_seed=1, count_table_join=join)
        assert leaf_spy == [join, join] and out["count_table_join"] == join
        leaf_spy.clear()
        eff = lam.bootstrap_multi_run_effect_size_ci(
            runs, runs[:1], refs, bounds, n_iterations=20, random_seed=1,
            count_table_join=join)
        assert leaf_spy == [join] * 3 and eff["count_table_join"] == join

    @pytest.mark.parametrize("join", ["id", "sheet-primary"])
    def test_interaction_route(self, leaf_spy, join):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        conditions = {(a, b): (det.iloc[: 2 + a + b], bounds)
                      for a in (0, 1) for b in (0, 1)}
        out = lam.bootstrap_interaction_ci(conditions, refs, n_iterations=20,
                                           random_seed=1, count_table_join=join)
        assert leaf_spy == [join] * 4
        assert out["count_table_join"] == join

    @pytest.mark.parametrize("join", ["id", "sheet-primary"])
    def test_generate_report_route(self, leaf_spy, monkeypatch, join):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        refs["Symbol"] = "burial mound"
        det = merged_detections(refs, bounds)
        det["subtype"] = "burial_mound"
        monkeypatch.setattr(lam, "load_data", lambda *a, **k: (det, bounds, refs))
        report = lam.generate_report("d", "b", bootstrap_iterations=20,
                                     count_table_join=join)
        assert leaf_spy == [join]
        assert report["tile_joins"]["count_table"] == join


class TestCorrectedF1EngineRecordsBothRules:

    @pytest.mark.parametrize("joins", [("sheet-contains", "sheet-primary"), ("id", "id")])
    def test_summary_json_records_both(self, tmp_path, joins):
        from scripts.compute_corrected_f1_multi_buffer import run

        tile_join, count_table_join = joins
        bounds, refs = synthetic_bounds(), synthetic_refs("source_map")
        det = merged_detections(refs, bounds, "source_map")
        paths = {}
        for name, gdf in (("det", det), ("gt", refs), ("bounds", bounds)):
            paths[name] = tmp_path / f"{name}.geojson"
            gdf.to_file(paths[name], driver="GeoJSON")
        ext = tmp_path / "ext.csv"
        ext.write_text(
            "candidate_id,x,y,map_name,symbol_type,confidence_grade,"
            "position_source,provenance,nearest_student_m\n"
            f"0,{ORIGIN_X + 50},{ORIGIN_Y + 250},{SHEET_A},burial_mound,"
            "directly_reviewed,own_mark,model_detection,200.0\n")
        run(verified_detections=paths["det"], student_gt=paths["gt"],
            bounds=paths["bounds"], output_dir=tmp_path / "out", buffers=[50],
            n_bootstrap=20, seed=42, compute_mcc=True, extension_csv=ext,
            tile_join=tile_join, count_table_join=count_table_join)
        doc = json.loads((tmp_path / "out" / "summary.json").read_text())
        assert doc["metadata"]["tile_joins"]["classification"] == tile_join
        assert doc["metadata"]["tile_joins"]["count_table"] == count_table_join
        row = doc["results"][0]
        assert row["count_table_join"] == count_table_join
        assert row["tile_classification"]["tile_join"] == tile_join

    def test_score_detection_set_records_both(self):
        bounds, refs = synthetic_bounds(), synthetic_refs()
        det = merged_detections(refs, bounds)
        out = lam.score_detection_set(det, refs, bounds)
        assert (out["tile_join"], out["count_table_join"]) == ("sheet-contains", None)
        assert out["mcc"] == pytest.approx(1.0)
        legacy = lam.score_detection_set(det, refs, bounds, tile_join="id")
        assert legacy["tile_join"] == "id"
