"""Tests for the D30 observed-statistic fixes and the CSV/MD migration.

Phase 5 of the Session 137 audit remediation. Defect D30 (finding F6): the
CSV and Markdown writers published the bootstrap resample mean under the
column names ``mcc`` / ``sensitivity`` / ``specificity``, and the legacy
tiered leaderboard RANKED its MCC boards on the same quantity. Defect D36
(finding F12): ``"BCa"`` was asserted where the computation was percentile
or unrecorded.

Covers the writer fix, the leaderboard ranking key, the migration
functions (point substitution, confusion recompute, E81 ``None`` handling,
idempotency, and the safety gate), and the manifest generator's omission of
a method it was never told.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.evaluate_detections import (
    _observed_metric,
    collect_ci_methods,
    with_measured_bootstrap_method,
    write_batch_summary,
    write_outputs,
)
from scripts.generate_post_run_report import _metrics_from_eval
from scripts.migrate_csv_mcc_point import (
    cell_is_migratable,
    metrics_from_confusion,
    migrate_csv_text,
    migrate_md_text,
    observed_triple,
    render_cell,
    resample_means,
)

pytestmark = pytest.mark.tier1


# --------------------------------------------------------------------------
# Fixtures — the shapes the corpus actually contains
# --------------------------------------------------------------------------


def _tile_block(point: float | None = 0.6924) -> dict:
    """A modern ``tile_classification`` block: point and mean both present."""
    return {
        "confusion": {"tp": 2394, "tn": 4891, "fp": 270, "fn": 986},
        "mcc": {"point": point, "mean": 0.6925, "ci_lower": 0.6784,
                "ci_upper": 0.7062, "method": "BCa"},
        "sensitivity": {"point": 0.7083, "mean": 0.7084, "ci_lower": 0.6941,
                        "ci_upper": 0.722, "method": "BCa"},
        "specificity": {"point": 0.9477, "mean": 0.9478, "ci_lower": 0.942,
                        "ci_upper": 0.9532, "method": "BCa"},
    }


def _legacy_tile_block() -> dict:
    """A pre-``point`` block: only the resample mean, plus the counts.

    Reproduces the 47 committed evaluations the audit found (finding F15a)
    whose MCC block carries no ``point`` key. The counts below are the
    committed matrix of
    ``results/paper-eval/mcc/384px/flash-image-high-t-0-7``.
    """
    return {
        "confusion": {"tp": 225, "tn": 153, "fp": 105, "fn": 4},
        "mcc": {"mean": 0.6021, "ci_lower": 0.5903, "ci_upper": 0.6125},
        "sensitivity": {"mean": 0.993, "ci_lower": 0.9906, "ci_upper": 0.995},
        "specificity": {"mean": 0.5597, "ci_lower": 0.5462, "ci_upper": 0.5731},
    }


def _buffer_row(buffer_metres: int = 20) -> dict:
    """A minimal buffer row of the shape the writers consume."""
    return {
        "buffer_metres": buffer_metres,
        "f1": 0.508, "f1_ci_lower": 0.4946, "f1_ci_upper": 0.5213,
        "precision": 0.5115, "p_ci_lower": 0.4971, "p_ci_upper": 0.5259,
        "recall": 0.5045, "r_ci_lower": 0.4901, "r_ci_upper": 0.519,
        "f1_ci_method": "BCa", "p_ci_method": "BCa", "r_ci_method": "BCa",
    }


# --------------------------------------------------------------------------
# The writer fix (D30)
# --------------------------------------------------------------------------


def test_observed_metric_prefers_point() -> None:
    """``point`` wins whenever the key exists, mean only as legacy fallback."""
    assert _observed_metric({"point": 0.6924, "mean": 0.6925}) == 0.6924
    assert _observed_metric({"mean": 0.6925}) == 0.6925


def test_observed_metric_keeps_undefined_undefined() -> None:
    """E81: a present-but-``None`` point is undefined, not the mean."""
    assert _observed_metric({"point": None, "mean": 0.31}) is None
    assert _observed_metric(None) is None


def test_csv_writer_publishes_point_and_keeps_the_mean(tmp_path: Path) -> None:
    """The bare columns carry the point; the mean gets its own columns."""
    results = {
        "label": "c1", "n_detections": 10,
        "buffers": [_buffer_row()],
        "tile_classification": _tile_block(),
    }
    write_outputs(results, None, tmp_path)

    with open(tmp_path / "evaluation.csv", encoding="utf-8") as handle:
        row = next(iter(csv.DictReader(handle)))
    assert row["mcc"] == "0.6924"
    assert row["sensitivity"] == "0.7083"
    assert row["specificity"] == "0.9477"
    assert row["mcc_boot_mean"] == "0.6925"
    assert row["sensitivity_boot_mean"] == "0.7084"
    assert row["specificity_boot_mean"] == "0.9478"


def test_csv_writer_leaves_an_undefined_metric_empty(tmp_path: Path) -> None:
    """E81 survives the D30 fix: undefined is an empty cell, never ``0``."""
    results = {
        "label": "c1", "n_detections": 10,
        "buffers": [_buffer_row()],
        "tile_classification": _tile_block(point=None),
    }
    write_outputs(results, None, tmp_path)

    with open(tmp_path / "evaluation.csv", encoding="utf-8") as handle:
        row = next(iter(csv.DictReader(handle)))
    assert row["mcc"] == ""
    assert row["mcc_boot_mean"] == "0.6925"


def test_markdown_table_renders_the_point(tmp_path: Path) -> None:
    """The MCC column of ``evaluation.md`` is the observed statistic."""
    results = {
        "label": "c1", "n_detections": 10,
        "buffers": [_buffer_row()],
        "tile_classification": _tile_block(point=0.6),
    }
    write_outputs(results, None, tmp_path)
    body = next(
        line for line in (tmp_path / "evaluation.md").read_text().splitlines()
        if line.startswith("| 20m ")
    )
    cells = [c.strip() for c in body.split("|")]
    assert cells[8] == "0.600"  # not 0.693, the resample mean


def test_batch_summary_publishes_point_and_boot_mean(tmp_path: Path) -> None:
    """The batch roll-up follows the same rule as the per-condition CSV."""
    write_batch_summary(
        [{"label": "c1", "n_runs": 1, "buffers": [_buffer_row()],
          "tile_classification": _tile_block()}],
        tmp_path,
    )
    with open(tmp_path / "batch_summary.csv", encoding="utf-8") as handle:
        row = next(iter(csv.DictReader(handle)))
    assert row["mcc"] == "0.6924"
    assert row["mcc_boot_mean"] == "0.6925"


# --------------------------------------------------------------------------
# The leaderboard ranking key (D30)
# --------------------------------------------------------------------------


def test_tiered_leaderboard_scores_on_the_point() -> None:
    """``get_condition_score`` must rank MCC boards on the observed value."""
    from scripts.build_tiered_leaderboard import (
        METRIC_MCC,
        SelectedCondition,
        get_condition_score,
    )

    cond = SelectedCondition(
        label="c1", geojson_path=Path("x.geojson"), best_threshold=15,
        era=2, track="text", category="single-pass", k=1,
        evaluations={20: {"f1": 0.8}}, tile_mcc=0.6924,
    )
    assert get_condition_score(cond, 20, METRIC_MCC) == 0.6924


def test_tiered_leaderboard_lifts_point_not_mean() -> None:
    """``lift_tile_mcc`` reads ``point`` on every committed block shape."""
    from scripts.build_tiered_leaderboard import lift_tile_mcc

    assert lift_tile_mcc({"tile_classification": _tile_block()}) == 0.6924
    # Pre-``point`` block: the mean is the only value it has.
    assert lift_tile_mcc(
        {"tile_classification": _legacy_tile_block()}) == 0.6021
    # E81: an undefined point stays undefined and must not fall back.
    assert lift_tile_mcc(
        {"tile_classification": _tile_block(point=None)}) is None
    assert lift_tile_mcc({}) is None


# --------------------------------------------------------------------------
# The migration functions (D30)
# --------------------------------------------------------------------------


def test_metrics_from_confusion_matches_the_committed_point() -> None:
    """Recomputation reproduces the observed triple from the counts alone."""
    triple = metrics_from_confusion({"tp": 225, "tn": 153, "fp": 105, "fn": 4})
    assert triple == {"mcc": 0.6146, "sensitivity": 0.9825,
                      "specificity": 0.593}


def test_metrics_from_confusion_is_none_when_a_denominator_vanishes() -> None:
    """E81: a vanishing denominator yields ``None``, never ``0``."""
    triple = metrics_from_confusion({"tp": 204, "tn": 0, "fp": 136, "fn": 0})
    assert triple["mcc"] is None          # (tn + fn) == 0
    assert triple["sensitivity"] == 1.0   # measured, not degenerate
    assert triple["specificity"] == 0.0   # measured zero: 0 of 136


def test_observed_triple_prefers_point_over_confusion() -> None:
    """A block carrying ``point`` is read, not recomputed."""
    triple, source = observed_triple(_tile_block())
    assert source == "point"
    assert triple["mcc"] == 0.6924


def test_observed_triple_falls_back_to_confusion() -> None:
    """A pre-``point`` block is recovered from its own committed counts."""
    triple, source = observed_triple(_legacy_tile_block())
    assert source == "confusion"
    assert triple["mcc"] == 0.6146
    assert triple["mcc"] != _legacy_tile_block()["mcc"]["mean"]


def test_observed_triple_gives_up_without_point_or_confusion() -> None:
    """No point and no counts means no honest substitution is possible."""
    assert observed_triple({"mcc": {"mean": 0.5}}) is None
    assert observed_triple({}) is None


def _csv_text(mcc: str = "0.6925", sens: str = "0.7084",
              spec: str = "0.9478") -> str:
    """A two-row CSV in the committed dialect (CRLF, minimal quoting)."""
    return (
        "label,buffer_metres,f1,mcc,sensitivity,specificity\r\n"
        f"c1,20,0.508,{mcc},{sens},{spec}\r\n"
        f"c1,30,0.6886,{mcc},{sens},{spec}\r\n"
    )


def test_migrate_csv_replaces_only_the_metric_cells() -> None:
    """Every other cell, the header, and the line endings are preserved."""
    triple, _ = observed_triple(_tile_block())
    new_text, cells, reason = migrate_csv_text(
        _csv_text(), {"": triple}, {"": resample_means(_tile_block())}, None,
    )
    assert reason is None
    assert cells == 6  # 2 rows x 3 metrics
    assert new_text == (
        "label,buffer_metres,f1,mcc,sensitivity,specificity\r\n"
        "c1,20,0.508,0.6924,0.7083,0.9477\r\n"
        "c1,30,0.6886,0.6924,0.7083,0.9477\r\n"
    )


def test_migrate_csv_is_idempotent() -> None:
    """A second pass over a migrated file changes nothing."""
    tile = _tile_block()
    triple, _ = observed_triple(tile)
    once, _, _ = migrate_csv_text(
        _csv_text(), {"": triple}, {"": resample_means(tile)}, None)
    twice, cells, reason = migrate_csv_text(
        once, {"": triple}, {"": resample_means(tile)}, None)
    assert reason is None
    assert cells == 0
    assert twice == once


def test_migrate_csv_writes_an_empty_cell_for_an_undefined_metric() -> None:
    """E81 at the migration layer: ``None`` is empty, never ``0``."""
    tile = _tile_block(point=None)
    triple, _ = observed_triple(tile)
    new_text, cells, reason = migrate_csv_text(
        _csv_text(), {"": triple}, {"": resample_means(tile)}, None)
    assert reason is None
    assert ",,0.7083,0.9477" in new_text
    assert cells == 6


def test_migrate_csv_skips_a_file_whose_cells_are_unaccounted_for() -> None:
    """A stale roll-up is left alone rather than half-corrected.

    Reproduces ``results/paper-eval/mcc/384px/batch_summary.csv``, whose
    per-condition evaluations were re-emitted at B = 10,000 without the
    roll-up being refreshed: its cells are neither the current mean nor
    the current point.
    """
    tile = _tile_block()
    triple, _ = observed_triple(tile)
    new_text, cells, reason = migrate_csv_text(
        _csv_text(mcc="0.5000"), {"": triple}, {"": resample_means(tile)},
        None,
    )
    assert reason == "cell_is_neither_mean_nor_point:mcc"
    assert cells == 0
    assert new_text == _csv_text(mcc="0.5000")


def test_migrate_csv_keys_batch_rows_by_label() -> None:
    """Each batch row takes the triple of its own condition."""
    text = (
        "label,buffer_metres,mcc,sensitivity,specificity\r\n"
        "cond-a,20,0.6925,0.7084,0.9478\r\n"
        "cond-b,20,0.6021,0.993,0.5597\r\n"
    )
    triple_a, _ = observed_triple(_tile_block())
    triple_b, _ = observed_triple(_legacy_tile_block())
    new_text, cells, reason = migrate_csv_text(
        text,
        {"cond-a": triple_a, "cond-b": triple_b},
        {"cond-a": resample_means(_tile_block()),
         "cond-b": resample_means(_legacy_tile_block())},
        "label",
    )
    assert reason is None
    assert "cond-a,20,0.6924,0.7083,0.9477" in new_text
    assert "cond-b,20,0.6146,0.9825,0.593" in new_text
    assert cells == 6


def test_migrate_csv_refuses_a_row_with_no_evaluation() -> None:
    """An unmatched label is a skip, not a guess."""
    text = ("label,buffer_metres,mcc,sensitivity,specificity\r\n"
            "cond-z,20,0.6925,0.7084,0.9478\r\n")
    triple, _ = observed_triple(_tile_block())
    _, cells, reason = migrate_csv_text(
        text, {"cond-a": triple}, {"cond-a": resample_means(_tile_block())},
        "label",
    )
    assert cells == 0
    assert reason == "no_evaluation_json_for_row:cond-z"


def _md_text(mcc: str = "0.693", sens: str = "0.708",
             spec: str = "0.948") -> str:
    """An ``evaluation.md`` table of the committed shape."""
    return (
        "# Evaluation: c1\n\n"
        "| Buffer | F1 | F1 CI | P | P CI | R | R CI "
        "| MCC | MCC CI | Sens | Spec |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
        f"| 20m | 0.508 | [0.495, 0.521] | 0.512 | [0.497, 0.526] "
        f"| 0.505 | [0.490, 0.519] | {mcc} | [0.678, 0.706] "
        f"| {sens} | {spec} |\n"
    )


def test_migrate_md_replaces_only_the_three_value_cells() -> None:
    """Pipes, padding, and every other cell are preserved byte for byte."""
    tile = _tile_block(point=0.6)
    triple, _ = observed_triple(tile)
    new_text, cells, reason = migrate_md_text(
        _md_text(), triple, resample_means(tile))
    assert reason is None
    assert cells == 1  # only the MCC cell moves at 3 d.p.
    assert new_text == _md_text(mcc="0.600")


def test_migrate_md_renders_undefined_not_zero() -> None:
    """E81 in the Markdown layer."""
    tile = _tile_block(point=None)
    triple, _ = observed_triple(tile)
    new_text, _, reason = migrate_md_text(
        _md_text(), triple, resample_means(tile))
    assert reason is None
    assert "| undefined |" in new_text.replace(" |", " |")
    assert "| 0.000 " not in new_text


def test_migrate_md_skips_an_unrecognised_table() -> None:
    """A table without the writer's header is not this migration's business."""
    _, cells, reason = migrate_md_text(
        "| Buffer | F1 |\n|---|---|\n| 20m | 0.5 |\n",
        {"mcc": 0.1, "sensitivity": 0.2, "specificity": 0.3},
        {"mcc": 0.1, "sensitivity": 0.2, "specificity": 0.3},
    )
    assert cells == 0
    assert reason == "no_mcc_table_header"


def test_cell_gate_accepts_mean_and_point_and_nothing_else() -> None:
    """The gate is what makes the migration safe AND idempotent."""
    assert cell_is_migratable("0.6925", 0.6925, 0.6924)
    assert cell_is_migratable("0.6924", 0.6925, 0.6924)
    assert cell_is_migratable("", 0.6925, 0.6924)
    assert not cell_is_migratable("0.7457", 0.7467, 0.7466)
    assert not cell_is_migratable("n/a", 0.6925, 0.6924)


def test_render_cell_matches_the_csv_module() -> None:
    """Values render exactly as the writer's ``csv`` module renders them."""
    assert render_cell(0.6924) == "0.6924"
    assert render_cell(0.593) == "0.593"
    assert render_cell(None) == ""


# --------------------------------------------------------------------------
# CI-method honesty (D36)
# --------------------------------------------------------------------------


def test_generator_omits_a_method_the_source_never_declared() -> None:
    """An absent ``f1_ci_method`` must not become a ``BCa`` claim."""
    summary = {
        "buffers": [
            {"buffer_metres": 20, "f1": 0.6, "precision": 0.5, "recall": 0.7,
             "f1_ci_lower": 0.55, "f1_ci_upper": 0.65,
             "f1_ci_method": "percentile"},
            {"buffer_metres": 30, "f1": 0.6, "precision": 0.5, "recall": 0.7,
             "f1_ci_lower": 0.55, "f1_ci_upper": 0.65},
        ],
        "tile_classification": _tile_block(),
    }
    metrics = _metrics_from_eval(summary)
    assert metrics["per_buffer"]["20"]["ci"]["method"] == "percentile"
    assert "method" not in metrics["per_buffer"]["30"]["ci"]


def test_bootstrap_method_is_measured_not_asserted() -> None:
    """``bootstrap.method`` reports what ran; the literal is the intent."""
    metadata = {"bootstrap": {"n_iterations": 10000, "seed": 42,
                              "method_requested": "BCa"}}
    results = {"buffers": [_buffer_row()],
               "tile_classification": _tile_block()}
    updated = with_measured_bootstrap_method(metadata, results)
    assert updated["bootstrap"]["method"] == "BCa"
    assert updated["bootstrap"]["methods_measured"] == ["BCa"]
    assert updated["bootstrap"]["method_requested"] == "BCa"
    # The caller's dict is untouched — one metadata block serves every
    # condition of a batch.
    assert "method" not in metadata["bootstrap"]


def test_bootstrap_method_reports_mixed_when_metrics_disagree() -> None:
    """A run that fell back on some metrics may not call itself BCa."""
    tile = _tile_block()
    tile["specificity"]["method"] = "percentile_fallback"
    results = {"buffers": [_buffer_row()], "tile_classification": tile}
    updated = with_measured_bootstrap_method({"bootstrap": {}}, results)
    assert updated["bootstrap"]["method"] == "mixed"
    assert updated["bootstrap"]["methods_measured"] == [
        "BCa", "percentile_fallback",
    ]


def test_bootstrap_method_omitted_when_nothing_was_measured() -> None:
    """No observation means no key — an absent parameter is not evidence."""
    results = {"buffers": [{"buffer_metres": 20, "f1": 0.6}]}
    updated = with_measured_bootstrap_method(
        {"bootstrap": {"method_requested": "BCa"}}, results)
    assert "method" not in updated["bootstrap"]
    assert "methods_measured" not in updated["bootstrap"]


def test_collect_ci_methods_reads_buffers_and_tile_blocks() -> None:
    """Both carriers of a measured method are censused."""
    tile = _tile_block()
    tile["mcc"]["method"] = "undefined"
    results = {"buffers": [_buffer_row()], "tile_classification": tile}
    assert collect_ci_methods(results) == {"BCa", "undefined"}
