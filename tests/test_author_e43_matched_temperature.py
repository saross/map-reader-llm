"""Tier-1 tests for ``scripts/author_e43_matched_temperature.py``.

The script files the E72 matched-temperature remediation: one registered
analysis over the four ALREADY-registered ``pv-diag-384`` conditions, plus
``_ignored_evals`` waivers for the independent 14-buffer + MCC reproduction
under ``results/e43-matched-temperature/paper-eval/``. These are integration
tests against the committed source-of-truth files, so they are deterministic
and fast (no application programming interface (API) calls, no bootstrap).

Asserts:

- every validation gate passes against the committed artefacts (14 buffers,
  MCC present, F1@20 m reproduces the findings document, ``n_detections``
  matches the GeoJSON, registered sibling agrees to 1e-9);
- the four ``conditions_compared`` foreign keys resolve to real, registered
  ``pv-diag-384`` conditions, and no duplicate ``matched-temp-*`` condition
  was minted;
- the generated analysis spec builds into a row that validates against the
  analyses-manifest JSON Schema;
- ``predicted_outcome`` is null — a post-hoc remediation must not back-fill
  the write-once prediction field;
- applying the change twice is a no-op the second time (idempotency);
- the hand-authored sidecars keep their on-disk JSON formatting (indent 1, no
  trailing newline), so a four-line edit stays a four-line diff;
- ``_mcc`` reads every ``tile_classification.mcc`` shape in the committed
  corpus without raising, and preserves a legitimate MCC of 0.0 (defect D37 /
  audit finding F15b — the bare-float AttributeError and the E81 falsy-zero).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts.author_e43_matched_temperature import (
    ANALYSIS_ID,
    BUFFERS_STANDARD,
    CELLS,
    RUN_ID,
    _json_style,
    _mcc,
    apply,
    build_analysis_spec,
    check_gates,
    condition_ids,
    eval_rel,
    ignored_eval_paths,
    plan,
)
from scripts.generate_post_run_report import (
    build_analyses,
    load_schema_registry,
    validate_row,
)

REPO = Path(__file__).resolve().parent.parent


@pytest.mark.tier1
def test_all_gates_pass_against_committed_artefacts() -> None:
    """The full gate battery is clean on the committed tree."""
    assert check_gates() == []


@pytest.mark.tier1
def test_reproduction_evals_carry_the_house_grain() -> None:
    """Each reproduction eval has the 14 standard buffers and an MCC block."""
    for cell, _arm, _n, _thr, expect_f1, _det, _sib in CELLS:
        summary = json.loads((REPO / eval_rel(cell)).read_text())["summary"]
        buffers = tuple(b["buffer_metres"] for b in summary["buffers"])
        assert buffers == BUFFERS_STANDARD, cell
        assert summary["tile_classification"]["mcc"]["point"] is not None, cell
        f20 = next(b["f1"] for b in summary["buffers"] if b["buffer_metres"] == 20)
        assert round(f20, 4) == pytest.approx(expect_f1, abs=5e-4), cell


@pytest.mark.tier1
def test_compared_conditions_are_registered_and_not_duplicated() -> None:
    """The four foreign keys resolve, and no parallel ``matched-temp-*`` exists."""
    decomposition = json.loads(
        (REPO / "results/run-conditions.json").read_text()
    )["decomposition"]
    labels = {c["label"] for c in decomposition[RUN_ID]["conditions"]}
    for cid in condition_ids():
        run_id, label = cid.split("::", 1)
        assert run_id == RUN_ID
        assert label in labels, f"{cid} is not a registered condition"
    assert not [lbl for lbl in labels if lbl.startswith("matched-temp-")]


@pytest.mark.tier1
def test_analysis_row_validates_against_the_schema() -> None:
    """The built analysis row conforms to analyses-manifest.schema.json."""
    schema_reg, _ = load_schema_registry()
    rows = build_analyses([build_analysis_spec()], at="2026-08-02T00:00:00Z")
    assert len(rows) == 1
    assert validate_row("analyses", rows[0], schema_reg) == []
    assert rows[0]["analysis_id"] == ANALYSIS_ID
    assert rows[0]["conditions_compared"] == condition_ids()


@pytest.mark.tier1
def test_prediction_field_is_not_back_filled() -> None:
    """``predicted_outcome`` stays null — nothing was predicted before the fact."""
    assert build_analysis_spec()["predicted_outcome"] is None


@pytest.mark.tier1
def test_ignored_eval_paths_exist_on_disk() -> None:
    """Every waived path names a real evaluation.json (no stale waivers)."""
    paths = ignored_eval_paths()
    assert len(paths) == len(CELLS)
    for rel in paths:
        assert (REPO / rel).is_file(), rel


@pytest.mark.tier1
def test_json_style_round_trips_the_real_sidecars() -> None:
    """The measured style reproduces each sidecar byte-for-byte.

    This is the guard that a write touches only the lines it means to: if the
    indent, the trailing newline, or the non-ASCII escaping were assumed rather
    than measured, this equality fails and the re-serialisation would rewrite
    thousands of untouched lines.
    """
    for name in ("run-conditions.json", "run-analyses.json"):
        raw = (REPO / "results" / name).read_text()
        indent, trailing, ensure_ascii = _json_style(raw)
        assert indent >= 1, name
        rebuilt = json.dumps(
            json.loads(raw), indent=indent, ensure_ascii=ensure_ascii
        ) + trailing
        assert rebuilt == raw, name


@pytest.mark.tier1
def test_apply_preserves_sidecar_formatting(tmp_path: Path) -> None:
    """A four-line edit must not reindent the whole sidecar."""
    (tmp_path / "results").mkdir()
    for name in ("run-conditions.json", "run-analyses.json"):
        shutil.copy(REPO / "results" / name, tmp_path / "results" / name)
    before = {
        name: _json_style((tmp_path / "results" / name).read_text())
        for name in ("run-conditions.json", "run-analyses.json")
    }
    apply(tmp_path)
    for name, style in before.items():
        assert _json_style((tmp_path / "results" / name).read_text()) == style, name


@pytest.mark.tier1
def test_apply_is_idempotent(tmp_path: Path) -> None:
    """A second apply() writes nothing new: analysis skipped, no waivers added."""
    (tmp_path / "results").mkdir()
    for name in ("run-conditions.json", "run-analyses.json"):
        shutil.copy(REPO / "results" / name, tmp_path / "results" / name)

    first = apply(tmp_path)
    second = apply(tmp_path)
    assert second["analysis"] == "skip"
    assert second["ignored_evals_added"] == []
    assert plan(tmp_path) == {"analysis": "skip", "ignored_evals_added": []}

    analyses = json.loads((tmp_path / "results/run-analyses.json").read_text())
    ids = [a["analysis_id"] for a in analyses["analyses"]]
    assert ids.count(ANALYSIS_ID) == 1

    entry = json.loads(
        (tmp_path / "results/run-conditions.json").read_text()
    )["decomposition"][RUN_ID]
    assert set(ignored_eval_paths()) <= set(entry["_ignored_evals"])
    assert entry["_note"].count("E72 remediation (2026-08-02)") == 1
    # The first apply is the one that did the work (unless the tree already
    # carried the filing, in which case both runs are no-ops).
    assert first["analysis"] in {"add", "skip"}


# ---------------------------------------------------------------------------
# _mcc — the MCC-block shape guard (defect D37 / audit finding F15b)
# ---------------------------------------------------------------------------
# Five ``tile_classification.mcc`` shapes exist across the committed corpus.
# The retired one-line ``or {}`` chain raised ``AttributeError`` on the bare
# float the Track-2 adapters write, and coerced a legitimate MCC of 0.0 to
# ``None`` — the falsy-zero defect erratum E81 removed elsewhere.


@pytest.mark.tier1
def test_mcc_reads_the_point_from_the_modern_dict_shape() -> None:
    """The 1,357-cell majority shape: dict with point + CI + mean."""
    summary = {"tile_classification": {"mcc": {
        "point": 0.7104, "mean": 0.7099,
        "ci_lower": 0.697, "ci_upper": 0.723, "method": "BCa",
    }}}
    assert _mcc(summary) == pytest.approx(0.7104)


@pytest.mark.tier1
def test_mcc_returns_none_for_a_dict_without_a_point() -> None:
    """45 committed evaluations carry CI + mean but no point estimate.

    ``mean`` must NOT stand in: it is a different statistic, and gate 5
    compares reproduction against sibling at 1e-9. Returning ``None``
    lets gate 2 report the absence and refuse to write.
    """
    summary = {"tile_classification": {"mcc": {
        "mean": 0.7099, "ci_lower": 0.697, "ci_upper": 0.723,
    }}}
    assert _mcc(summary) is None


@pytest.mark.tier1
def test_mcc_accepts_the_bare_float_adapter_shape() -> None:
    """16 committed evaluations store the MCC as a bare float.

    The regression: ``(... or {}).get("point")`` raised AttributeError.
    """
    assert _mcc({"tile_classification": {"mcc": 0.6903}}) == pytest.approx(
        0.6903
    )


@pytest.mark.tier1
def test_mcc_preserves_a_legitimate_zero_in_both_shapes() -> None:
    """MCC = 0.0 is a measurement (no better than chance), not absence."""
    assert _mcc({"tile_classification": {"mcc": 0.0}}) == 0.0
    assert _mcc({"tile_classification": {"mcc": {"point": 0.0}}}) == 0.0
    # And it must be distinguishable from a missing block.
    assert _mcc({"tile_classification": {"mcc": {"point": 0.0}}}) is not None


@pytest.mark.tier1
def test_mcc_preserves_a_legitimate_negative_value() -> None:
    """Negative MCC (anti-correlated predictions) survives the guard."""
    assert _mcc({"tile_classification": {"mcc": -0.25}}) == pytest.approx(-0.25)


@pytest.mark.tier1
@pytest.mark.parametrize("summary", [
    {},                                                   # no block
    {"tile_classification": None},                        # null block
    {"tile_classification": "not measured"},              # prose block
    {"tile_classification": {}},                          # no mcc key
    {"tile_classification": {"mcc": None}},               # null mcc
    {"tile_classification": {"mcc": "undefined"}},        # sentinel string
    {"tile_classification": {"mcc": {"point": None}}},    # null point
    {"tile_classification": {"mcc": {"point": "n/a"}}},   # non-numeric point
    {"tile_classification": {"mcc": True}},               # corrupt boolean
    {"tile_classification": {"mcc": {"point": False}}},   # corrupt boolean
])
def test_mcc_returns_none_for_unusable_shapes(summary: dict) -> None:
    """Every unusable shape degrades to ``None`` — never an exception."""
    assert _mcc(summary) is None


@pytest.mark.tier1
def test_mcc_handles_every_shape_in_the_committed_corpus() -> None:
    """Sweep the real evaluations: no exception, and a float or None.

    A shape census tripwire — if a sixth shape lands in ``results/``,
    this fails here rather than in a gate that publishes an artefact.
    """
    seen_float = seen_none = 0
    for path in sorted((REPO / "results").rglob("evaluation.json")):
        try:
            summary = json.loads(path.read_text(encoding="utf-8"))["summary"]
        except (json.JSONDecodeError, KeyError):  # pragma: no cover
            continue
        value = _mcc(summary)
        assert value is None or isinstance(value, float), path
        seen_float += value is not None
        seen_none += value is None
    # Both branches are genuinely exercised by the committed corpus.
    assert seen_float > 0 and seen_none > 0
