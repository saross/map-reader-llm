"""
Tests for withholding — rather than aborting on — a refused tile join.

Until 2026-09-13 the tile-join invariant of
``reports/tile-mcc-geometric-join-2026-09-12.md`` § 3 was enforced by a bare
``raise`` inside ``lib_advanced_metrics.compute_per_tile_tp_fp_fn``. Because
``bootstrap_ci`` calls that function once per buffer, a refused cell took the
**whole** evaluation down with it, and the cell's F1 — a quantity a tile-join
refusal does not touch — could not be written to its ``evaluation.json`` at
all. That is what blocked repairing
``gemini37-screen-2026-08-28::g37-text-k3-verified-opmax`` after the
recovery-fragment fix moved its F1 (``reports/recovery-drop-fix-2026-09-13.md``
§ 6.3).

The PI's ruling of 2026-09-13 (Session 153, ruling 6) is that the name-based
``id`` join is the published tile-MCC convention, and that a cell the
invariant refuses has its **whole-frame F1 reported in full** and its
**per-tile statistics withheld**. These tests pin both halves of that, and
the boundary between them:

1. **A mismatched frame yields F1 and withholds the rest.** The point
   estimates are written; the tile-level Matthews Correlation Coefficient
   (MCC), the tile confusion, and every bootstrap confidence interval are
   ``None`` and marked withheld with the named reason, the shortfall counts,
   and both tile vocabularies. No withheld quantity is given a number, and
   the refusal appears in the JSON, the CSV and the Markdown.
2. **A matched frame is untouched.** The whole evaluation — summary dict,
   CSV and Markdown — reproduces a golden captured from the code as it stood
   *before* the change (commit ``35dd1f254``), byte for byte.

**Why the bootstrap is on the withheld side.** It is an interval on F1,
precision and recall, whose point estimates survive a refusal. But
``bootstrap_ci`` resamples **tiles** — the resampling unit fixed
pre-lodgement in Decision 10, recorded as
``_metadata.bootstrap.resampling_unit = "tile_level"`` in every committed
artefact — and the per-tile table it resamples is exactly what the invariant
refuses. There is therefore no interval to report, only a point.

Regenerating the golden
-----------------------

The golden under ``tests/fixtures/tile_join_withheld/`` is a regression
anchor and should only be regenerated deliberately, on sapphire, with a
reason recorded in the commit message::

    python -m tests.test_tile_join_withheld --regenerate-golden
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from scripts.evaluate_detections import (
    WITHHELD_DISPLAY,
    evaluate_single_run,
    write_outputs,
)
from scripts.generate_post_run_report import _fmt_mcc_cell, _metrics_from_eval
from scripts.generate_run_reports import NOT_SUPPLIED, WITHHELD, _mcc_cell
from scripts.lib_advanced_metrics import (
    CI_FLAG_BASIS_WITHHELD,
    COVERAGE_STATUS_WITHHELD,
    TILE_JOIN_ID,
    TILE_JOIN_REASON_DETECTION_SHORTFALL,
    TILE_JOIN_WITHHELD_QUANTITIES,
    describe_tile_join_refusal,
)

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"
ORIGIN_X = 500000.0
ORIGIN_Y = 4700000.0
TILE = 100.0

#: Where the golden lives, and the evaluation parameters that produced it.
#: Small on every axis so the whole thing runs in well under a second, but
#: large enough for a non-degenerate tile confusion (2 TP / 1 FN / 2 FP /
#: 2 TN tiles) and two buffers that disagree.
GOLDEN_DIR = Path(__file__).parent / "fixtures" / "tile_join_withheld"
GOLDEN_LABEL = "matched-cell-regression"
GOLDEN_BUFFERS = [20, 50]
GOLDEN_BOOTSTRAP = 200
GOLDEN_SEED = 42

#: The Markdown writer stamps a generation time, which cannot be a golden.
#: Everything else in the file is content.
_GENERATED_LINE = re.compile(r"^\*\*Generated\*\*: .*$", re.MULTILINE)


def _frame(n_tiles: int = 7) -> gpd.GeoDataFrame:
    """Build the scoring frame: a row of square, non-overlapping tiles.

    Non-overlapping on purpose. The project's real 384 px frames overlap on
    a 336 px stride, which is why there is no single geometric join (§ 0 of
    the join report) — but the question these tests ask is about the ``id``
    join's vocabulary, and an overlapping frame would add a second variable.

    Args:
        n_tiles: How many tiles to lay out along x.

    Returns:
        GeoDataFrame with ``tile_name`` and ``geometry`` in :data:`CRS`.
    """
    names = [f"f_x{i * int(TILE)}_y0.png" for i in range(n_tiles)]
    geometries = [
        box(
            ORIGIN_X + i * TILE,
            ORIGIN_Y,
            ORIGIN_X + (i + 1) * TILE,
            ORIGIN_Y + TILE,
        )
        for i in range(n_tiles)
    ]
    return gpd.GeoDataFrame(
        {"tile_name": names}, geometry=geometries, crs=CRS,
    )


def _tile_centre(index: int, dx: float = 0.0) -> tuple[float, float]:
    """Return the centre of tile ``index``, optionally shifted along x.

    Args:
        index: Tile position along the row.
        dx: Offset from the centre in metres, used to put a detection a
            known distance from its reference.

    Returns:
        An ``(x, y)`` pair in :data:`CRS`.
    """
    return (ORIGIN_X + index * TILE + TILE / 2 + dx, ORIGIN_Y + TILE / 2)


def _references() -> gpd.GeoDataFrame:
    """Three reference mounds, in tiles 0, 1 and 2.

    Tiles 3–6 hold none, which gives the tile confusion both populated and
    empty rows so its MCC is defined.

    Returns:
        GeoDataFrame with a ``Map`` column (the per-map scoping key) in
        :data:`CRS`.
    """
    coords = [_tile_centre(0), _tile_centre(1), _tile_centre(2)]
    return gpd.GeoDataFrame(
        {"Map": ["f"] * len(coords)},
        geometry=[Point(x, y) for x, y in coords],
        crs=CRS,
    )


def _detections(source_tiles: list[str]) -> gpd.GeoDataFrame:
    """Four detections, at fixed positions, under caller-chosen tile names.

    Positions are the same in both fixtures; only the recorded
    ``source_tile`` differs, which isolates the tile vocabulary as the one
    variable between the matched and mismatched cases:

    * tile 0, 5 m off the reference — a true positive at 20 m;
    * tile 2, 5 m off the reference — a second true positive;
    * tile 3, nowhere near a reference — a false positive;
    * tile 4, nowhere near a reference — a second false positive.

    Tile 1's reference is therefore a false negative, and tiles 5 and 6 are
    the empty-and-undetected rows.

    Args:
        source_tiles: One recorded tile name per detection, in the order
            above.

    Returns:
        GeoDataFrame with ``source_tile`` and ``Map`` in :data:`CRS`.
    """
    coords = [
        _tile_centre(0, dx=5.0),
        _tile_centre(2, dx=5.0),
        _tile_centre(3),
        _tile_centre(4),
    ]
    assert len(source_tiles) == len(coords)
    return gpd.GeoDataFrame(
        {"source_tile": source_tiles, "Map": ["f"] * len(coords)},
        geometry=[Point(x, y) for x, y in coords],
        crs=CRS,
    )


def matched_cell() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """The sound cell: every detection's name is one of the frame's.

    Returns:
        ``(detections, references, frame)``.
    """
    return (
        _detections([
            "f_x0_y0.png",
            "f_x200_y0.png",
            "f_x300_y0.png",
            "f_x400_y0.png",
        ]),
        _references(),
        _frame(),
    )


def mismatched_cell() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """The refused cell: the same points, named on a half-offset tiling.

    The offsets (``_x50_``, ``_x250_`` …) are not in the frame's vocabulary,
    so the ``id`` join books nothing — while the **map prefix** is still
    ``f``, which matters: the per-map-sheet scoping inside
    ``calculate_f1_internal`` is a ``source_tile`` string prefix (§ 5.1(a)
    of the join report), so a differently-prefixed fixture would lose its F1
    too and the test could not tell "F1 survives a refusal" from "F1 was
    never computed". The three real refused cells share their frame's map
    prefix for the same reason, which is why their F1 is sound.

    Returns:
        ``(detections, references, frame)``.
    """
    return (
        _detections([
            "f_x50_y0.png",
            "f_x250_y0.png",
            "f_x350_y0.png",
            "f_x450_y0.png",
        ]),
        _references(),
        _frame(),
    )


def _evaluate(
    cell: tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame],
) -> dict[str, Any]:
    """Run the golden recipe over one fixture cell.

    Args:
        cell: ``(detections, references, frame)``.

    Returns:
        The summary dict from :func:`evaluate_single_run`.
    """
    gdf_det, gdf_ref, gdf_bounds = cell
    return evaluate_single_run(
        gdf_det, gdf_ref, gdf_bounds,
        buffers=GOLDEN_BUFFERS,
        n_bootstrap=GOLDEN_BOOTSTRAP,
        seed=GOLDEN_SEED,
        label=GOLDEN_LABEL,
        compute_mcc=True,
        tile_join=TILE_JOIN_ID,
    )


def _strip_generated(markdown: str) -> str:
    """Remove the Markdown writer's timestamp line so the rest can be golden.

    Args:
        markdown: The rendered ``evaluation.md`` text.

    Returns:
        The same text with the ``**Generated**`` line blanked.
    """
    return _GENERATED_LINE.sub("**Generated**: <stamp>", markdown)


# --------------------------------------------------------------------------
# 1. A refused cell reports F1 and withholds every per-tile quantity
# --------------------------------------------------------------------------

def test_refused_cell_reports_f1_and_withholds_the_tile_block():
    """F1 survives a refusal; MCC is withheld, named, and never numeric."""
    result = _evaluate(mismatched_cell())

    # F1 is reported, in full, at every buffer.
    assert len(result["buffers"]) == len(GOLDEN_BUFFERS)
    for row in result["buffers"]:
        assert row["f1"] > 0.0, "the refusal must not deflate F1"
        assert row["precision"] > 0.0
        assert row["recall"] > 0.0

    # The refusal reproduces the sound cell's point estimates exactly: the
    # tile vocabulary is the ONLY difference between the two fixtures, and
    # F1 does not consult a tile. This is the test that would catch the
    # refusal quietly dropping detections from the F1 arm.
    sound = _evaluate(matched_cell())
    for refused_row, sound_row in zip(result["buffers"], sound["buffers"]):
        assert refused_row["f1"] == sound_row["f1"]
        assert refused_row["precision"] == sound_row["precision"]
        assert refused_row["recall"] == sound_row["recall"]

    # The tile block is withheld, with the reason named.
    tile = result["tile_classification"]
    assert tile["withheld"] is True
    assert tile["mcc"] is None
    assert tile["sensitivity"] is None
    assert tile["specificity"] is None
    assert "confusion" not in tile
    assert tile["withheld_reason"] == TILE_JOIN_REASON_DETECTION_SHORTFALL
    assert tile["withheld_detail"]
    assert tile["tile_join"] == TILE_JOIN_ID


def test_refused_cell_records_the_shortfall_and_both_vocabularies():
    """The cell-level record names the counts and the two tilings."""
    result = _evaluate(mismatched_cell())
    record = result["tile_join_withheld"]

    assert record["withheld"] is True
    assert record["reason"] == TILE_JOIN_REASON_DETECTION_SHORTFALL
    # All four detections lie inside the frame and none is booked.
    assert record["shortfall"]["axis"] == "detections"
    assert record["shortfall"]["n_inside_union"] == 4
    assert record["shortfall"]["n_booked"] == 0
    assert record["shortfall"]["shortfall"] == 4
    assert record["shortfall"]["n_outside_union"] == 0

    frame_vocab = record["vocabularies"]["frame"]
    det_vocab = record["vocabularies"]["detections"]
    assert frame_vocab["n_distinct_tile_names"] == 7
    assert det_vocab["n_distinct_tile_names"] == 4
    # The vocabularies share a map prefix and share no tile name — which is
    # precisely the real cells' situation.
    assert frame_vocab["map_prefixes"] == det_vocab["map_prefixes"] == ["f"]
    assert det_vocab["n_names_in_frame_vocabulary"] == 0

    assert record["withheld_quantities"] == list(
        TILE_JOIN_WITHHELD_QUANTITIES,
    )
    assert "f1_point" in record["reported_quantities"]


def test_refused_cell_withholds_every_bootstrap_interval():
    """No interval is reported, and no zero stands in for one."""
    result = _evaluate(mismatched_cell())
    for row in result["buffers"]:
        assert row["ci_withheld"] is True
        assert row["ci_withheld_reason"] == TILE_JOIN_REASON_DETECTION_SHORTFALL
        for key in (
            "f1_ci_lower", "f1_ci_upper", "f1_ci_method",
            "p_ci_lower", "p_ci_upper", "p_ci_method",
            "r_ci_lower", "r_ci_upper", "r_ci_method",
        ):
            assert row[key] is None, f"{key} must be null, not a number"
        # Coverage is read off the same refused table, so it is withheld
        # too — and says so rather than reading "normal".
        assert row["coverage"] is None
        assert row["coverage_status"] == COVERAGE_STATUS_WITHHELD
        assert row["ci_flag_basis"] == CI_FLAG_BASIS_WITHHELD
        # "There is no interval", not "the interval is untrustworthy".
        assert row["ci_unreliable"] is True
        assert row["ci_excludes_point"] is None
    assert result["coverage_status"] == COVERAGE_STATUS_WITHHELD


def test_refused_cell_names_the_refusal_in_every_artefact(tmp_path):
    """JSON, CSV and Markdown each carry the refusal, none carries a number."""
    result = _evaluate(mismatched_cell())
    write_outputs(result, None, tmp_path)

    written = json.loads((tmp_path / "evaluation.json").read_text())
    assert written["summary"]["tile_classification"]["withheld"] is True
    assert written["summary"]["tile_join_withheld"]["reason"] == (
        TILE_JOIN_REASON_DETECTION_SHORTFALL
    )
    assert written["summary"]["buffers"][0]["f1_ci_lower"] is None

    csv_text = (tmp_path / "evaluation.csv").read_text()
    header, first_row = csv_text.splitlines()[0], csv_text.splitlines()[1]
    columns = dict(zip(header.split(","), first_row.split(",")))
    # Empty cells, never zeros — the erratum-E81 rule, applied to a
    # withheld quantity rather than an undefined one.
    for column in (
        "f1_ci_lower", "f1_ci_upper", "mcc", "mcc_ci_lower", "mcc_ci_upper",
        "sensitivity", "specificity", "ci_zero_fraction", "ci_n_tiles",
    ):
        assert columns[column] == "", f"{column} should be an empty cell"
    assert float(columns["f1"]) > 0.0
    assert columns["coverage_status"] == COVERAGE_STATUS_WITHHELD

    md_text = (tmp_path / "evaluation.md").read_text()
    assert WITHHELD_DISPLAY in md_text
    assert "Per-tile statistics WITHHELD" in md_text
    assert TILE_JOIN_REASON_DETECTION_SHORTFALL in md_text
    # The footnote must give the shortfall and both vocabularies, and must
    # NOT be the sparse-coverage footnote wearing a different hat.
    assert "0 of 4" in md_text
    assert "resample TILES" in md_text
    assert "Bootstrap CI suppressed for sparse-coverage buffers" not in md_text
    assert "Undefined MCC" not in md_text


def test_refused_cell_projects_into_the_manifest_without_inventing_numbers():
    """The generated conditions-manifest row carries nulls and the reason."""
    result = _evaluate(mismatched_cell())
    metrics = _metrics_from_eval(result, {"resampling_unit": "tile_level"})

    for buffer_key in ("20", "50"):
        row = metrics["per_buffer"][buffer_key]
        assert row["f1"] > 0.0
        assert row["ci"] is None
        assert row["coverage"] is None
        assert row["ci_unreliable"] is True
        assert row["ci_withheld_reason"] == (
            TILE_JOIN_REASON_DETECTION_SHORTFALL
        )

    tile = metrics["tile_classification"]
    assert tile["mcc"] is None
    assert tile["tp"] is None and tile["tn"] is None
    assert tile["fp"] is None and tile["fn"] is None
    assert tile["tile_withheld_reason"] == TILE_JOIN_REASON_DETECTION_SHORTFALL
    # E81's "undefined MCC" explanation must not be attached to a metric
    # that was withheld rather than computed-and-degenerate.
    assert "mcc_undefined_reason" not in tile


def test_the_generated_markdown_says_withheld_not_undefined():
    """Both manifest renderers keep "withheld" apart from the other nulls.

    ``undefined`` is erratum E81's word for a metric that was computed and
    came out degenerate; ``not supplied`` means the evaluation does not
    carry it. Neither describes a metric the invariant refused, and a
    reader who met either would draw the wrong conclusion about the data.
    """
    withheld = {"mcc": None, "tile_withheld_reason": "tile_join_detection_shortfall"}
    undefined = {"mcc": None, "mcc_undefined_reason": "no populated tiles"}

    # results/conditions-manifest.md
    assert _fmt_mcc_cell(None, withheld) == "withheld"
    assert _fmt_mcc_cell(None, undefined) == "undefined"
    assert _fmt_mcc_cell(None) == "undefined"
    assert _fmt_mcc_cell(0.0) == 0.0

    # outputs/**/post_run_report.md
    assert _mcc_cell(withheld) == WITHHELD
    assert _mcc_cell(undefined) == NOT_SUPPLIED
    assert _mcc_cell({"mcc": 0.8139}) == "0.8139"
    assert _mcc_cell({"mcc": 0.0}) == "0.0000"


# --------------------------------------------------------------------------
# 2. The sound path is untouched — regression against a pre-change golden
# --------------------------------------------------------------------------

def test_sound_cell_is_not_refused():
    """The probe returns ``None`` and the cell carries no withheld record."""
    gdf_det, gdf_ref, gdf_bounds = matched_cell()
    assert describe_tile_join_refusal(
        gdf_det, gdf_ref, gdf_bounds, TILE_JOIN_ID,
    ) is None

    result = _evaluate(matched_cell())
    assert "tile_join_withheld" not in result
    assert result["tile_classification"].get("withheld") is None
    assert result["tile_classification"]["confusion"] == {
        "tp": 2, "tn": 2, "fp": 2, "fn": 1,
    }
    for row in result["buffers"]:
        assert "ci_withheld" not in row
        assert row["f1_ci_lower"] is not None
        assert row["f1_ci_method"] is not None


def test_sound_cell_reproduces_the_pre_change_golden(tmp_path):
    """A matched cell's whole evaluation is byte-identical to before.

    The golden was captured from ``scripts/evaluate_detections.py`` and
    ``scripts/lib_advanced_metrics.py`` as they stood at commit
    ``35dd1f254``, immediately before the withholding change. It covers the
    summary dict, the CSV and the Markdown, so a regression in the writers
    is caught as well as one in the metrics.
    """
    result = _evaluate(matched_cell())
    write_outputs(result, None, tmp_path)

    expected_summary = json.loads(
        (GOLDEN_DIR / "matched-cell-summary.json").read_text(),
    )
    written = json.loads((tmp_path / "evaluation.json").read_text())
    assert written["summary"] == expected_summary

    assert (tmp_path / "evaluation.csv").read_text() == (
        GOLDEN_DIR / "matched-cell-evaluation.csv"
    ).read_text()

    assert _strip_generated((tmp_path / "evaluation.md").read_text()) == (
        GOLDEN_DIR / "matched-cell-evaluation.md"
    ).read_text()


def _regenerate_golden() -> None:
    """Rewrite the golden fixture from the current code. Run deliberately."""
    import tempfile

    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    result = _evaluate(matched_cell())
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        write_outputs(result, None, out)
        (GOLDEN_DIR / "matched-cell-summary.json").write_text(
            json.dumps(
                json.loads((out / "evaluation.json").read_text())["summary"],
                indent=2,
            ) + "\n",
        )
        (GOLDEN_DIR / "matched-cell-evaluation.csv").write_text(
            (out / "evaluation.csv").read_text(),
        )
        (GOLDEN_DIR / "matched-cell-evaluation.md").write_text(
            _strip_generated((out / "evaluation.md").read_text()),
        )
    print(f"golden regenerated under {GOLDEN_DIR}")


if __name__ == "__main__":
    if "--regenerate-golden" in sys.argv:
        _regenerate_golden()
    else:
        raise SystemExit(
            "run under pytest, or pass --regenerate-golden deliberately",
        )
