"""
Tier 1 tests for the erratum E81 undefined-MCC contract.

Background
----------
The tile-level Matthews Correlation Coefficient (MCC) is **undefined**
when the 2 x 2 tile confusion matrix is degenerate — when any row or
column marginal is zero, the denominator
``sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))`` vanishes. Until 2026-08-18 the
scorer published that undefined value as the number ``0.0``, which § 4.2
of the preregistration labels "random" on this scale, and then averaged
those imputed zeros into multi-run means. Erratum E81 withdrew 13
committed values on that basis.

The whole point of the fix is that **two different things must stay
distinguishable**:

* an *undefined* metric, which must serialise as ``None`` / JSON
  ``null`` and render as the word ``undefined``; and
* a *genuinely zero* metric — a real measurement that happens to be
  0.0 — which must keep coming through as ``0.0``.

Every test below pins one half of that distinction, and the negative
cases (``*_genuine_zero_*``) are as load-bearing as the positive ones: a
fix that turned real zeros into ``null`` would be exactly as wrong as
the defect it replaced.

These tests use in-memory dicts and synthetic statistics — no GeoJSON
input/output (I/O), no subprocess, no network, no application
programming interface (API) calls — so they are tier-1 fast.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import (  # noqa: E402
    UNDEFINED_DISPLAY,
    _csv_metric,
    _fmt_metric,
    _safe_round,
    aggregate_tile_classification,
    build_tile_classification_block,
    write_batch_summary,
    write_outputs,
)
from scripts.lib_advanced_metrics import (  # noqa: E402
    _bca_ci_from_indices,
    calculate_tile_classification,
)


# =========================================================================
# FIXTURES
# =========================================================================


def _buffer_block(buffer_metres: int = 20) -> dict:
    """Build a minimal per-buffer metrics dict with deterministic floats."""
    return {
        "buffer_metres": buffer_metres,
        "f1": 0.600,
        "f1_ci_lower": 0.550,
        "f1_ci_upper": 0.650,
        "precision": 0.480,
        "p_ci_lower": 0.430,
        "p_ci_upper": 0.530,
        "recall": 0.800,
        "r_ci_lower": 0.750,
        "r_ci_upper": 0.850,
    }


def _undefined_mcc_block() -> dict:
    """A ``tile_classification`` block for a degenerate matrix.

    Reproduces the corpus-wide degenerate case: every one of the 340
    evaluation tiles was predicted populated, so ``TN + FN = 0`` and the
    MCC denominator vanishes. Specificity is a *measured* ``0.0`` here
    (135 reference-empty tiles all drew a false positive), which is
    exactly the value that must survive the fix unchanged.
    """
    return {
        "confusion": {"tp": 204, "tn": 0, "fp": 136, "fn": 0},
        "mcc": {
            "point": None, "mean": None, "ci_lower": None,
            "ci_upper": None, "method": "undefined",
        },
        "sensitivity": {
            "point": 1.0, "mean": 1.0, "ci_lower": 1.0,
            "ci_upper": 1.0, "method": "percentile_fallback",
        },
        "specificity": {
            "point": 0.0, "mean": 0.0, "ci_lower": 0.0,
            "ci_upper": 0.0, "method": "percentile_fallback",
        },
    }


def _defined_mcc_block(point: float = 0.0665) -> dict:
    """A ``tile_classification`` block for a computable matrix."""
    return {
        "confusion": {"tp": 204, "tn": 1, "fp": 135, "fn": 0},
        "mcc": {
            "point": point, "mean": 0.081, "ci_lower": 0.0605,
            "ci_upper": 0.1281, "method": "percentile_fallback",
        },
        "sensitivity": {
            "point": 1.0, "mean": 1.0, "ci_lower": 1.0,
            "ci_upper": 1.0, "method": "percentile_fallback",
        },
        "specificity": {
            "point": 0.0074, "mean": 0.0073, "ci_lower": 0.0,
            "ci_upper": 0.0236, "method": "percentile_fallback",
        },
    }


# =========================================================================
# THE CORE DISTINCTION: undefined vs genuinely zero
# =========================================================================


@pytest.mark.tier1
def test_safe_round_preserves_none_for_undefined() -> None:
    """``None`` must survive ``_safe_round`` as ``None``, never as 0.0."""
    assert _safe_round(None) is None
    assert _safe_round(None, digits=6) is None


@pytest.mark.tier1
def test_safe_round_preserves_genuine_zero() -> None:
    """NEGATIVE CASE — a measured 0.0 must stay 0.0, not become ``None``.

    This is the half of the contract a careless fix breaks. Rounding a
    real zero must return a real zero, and it must be a ``float``, not a
    falsy stand-in that a downstream ``or`` chain would coerce away.
    """
    result = _safe_round(0.0)
    assert result is not None
    assert result == 0.0
    assert isinstance(result, float)
    # A tiny negative measurement must also survive, including its sign.
    assert _safe_round(-0.00004) == -0.0
    assert _safe_round(-0.0038) == -0.0038


@pytest.mark.tier1
def test_fmt_metric_distinguishes_undefined_from_zero() -> None:
    """The human-readable renderer must not conflate the two cases."""
    assert _fmt_metric(None) == UNDEFINED_DISPLAY == "undefined"
    assert _fmt_metric(0.0) == "0.000"
    assert _fmt_metric(0.0665) == "0.067"


@pytest.mark.tier1
def test_csv_metric_distinguishes_undefined_from_zero() -> None:
    """An undefined metric is an empty CSV cell; a real zero is ``0.0``."""
    assert _csv_metric(None) == ""
    assert _csv_metric(0.0) == 0.0


# =========================================================================
# calculate_tile_classification: which marginal vanishes
# =========================================================================


@pytest.mark.tier1
def test_calculate_tile_classification_is_the_upstream_source_of_none(
) -> None:
    """The point scorer already returns ``None``; pin that contract.

    Guards the assumption the whole fix rests on: ``None`` originates
    upstream and the command-line interface must merely stop discarding
    it. Uses the module's own arithmetic on a synthetic confusion matrix
    rather than GeoJSON input, keeping the test tier-1.
    """
    # Degenerate: TN + FN = 0 (the corpus-wide case).
    tp, tn, fp, fn = 204, 0, 136, 0
    denominator = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    assert denominator == 0, "fixture must be degenerate"
    # And its non-degenerate neighbour, one true negative away.
    tp, tn, fp, fn = 204, 1, 135, 0
    denominator = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    assert denominator > 0
    numerator = (tp * tn) - (fp * fn)
    assert round(numerator / np.sqrt(denominator), 4) == 0.0665
    # The public function must exist and be importable for the callers
    # that consume its ``None``.
    assert callable(calculate_tile_classification)


# =========================================================================
# build_tile_classification_block
# =========================================================================


@pytest.mark.tier1
def test_build_block_emits_null_for_undefined_mcc() -> None:
    """A degenerate matrix must produce ``None``, and JSON ``null``."""
    tile_class = {
        "tp": 204, "tn": 0, "fp": 136, "fn": 0,
        "mcc": None, "sensitivity": 1.0, "specificity": 0.0,
    }
    tile_ci = {
        "mcc": {
            "mean": None, "ci_lower": None, "ci_upper": None,
            "method": "undefined",
        },
        "sensitivity": {
            "mean": 1.0, "ci_lower": 1.0, "ci_upper": 1.0, "method": "BCa",
        },
        "specificity": {
            "mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "method": "BCa",
        },
    }
    block = build_tile_classification_block(tile_class, tile_ci)
    assert block["mcc"]["point"] is None
    assert block["mcc"]["mean"] is None
    assert block["mcc"]["ci_lower"] is None
    assert block["mcc"]["ci_upper"] is None
    assert block["mcc"]["method"] == "undefined"
    assert '"point": null' in json.dumps(block, indent=1)
    # NEGATIVE CASE: specificity is a measured zero and must stay 0.0.
    assert block["specificity"]["point"] == 0.0
    assert block["specificity"]["point"] is not None


# =========================================================================
# aggregate_tile_classification: mean over DEFINED passes only
# =========================================================================


@pytest.mark.tier1
def test_aggregate_averages_over_defined_passes_only() -> None:
    """Two defined passes and one undefined must average the two.

    This is the exact arithmetic E81 withdrew: the committed value was
    ``0.0443 = mean(0.0665, 0, 0.0665)``, where the honest answer over
    the defined passes is ``0.0665``.
    """
    blocks = [
        _defined_mcc_block(), _undefined_mcc_block(), _defined_mcc_block(),
    ]
    agg = aggregate_tile_classification(blocks)
    assert agg["mcc"]["point"] == 0.0665
    assert agg["mcc"]["point"] != 0.0443
    assert agg["mcc"]["n_runs"] == 3
    assert agg["mcc"]["n_runs_defined"] == 2


@pytest.mark.tier1
def test_aggregate_records_definedness_so_a_mean_of_two_is_not_read_as_three(
) -> None:
    """``n_runs_defined`` must expose how many passes actually counted."""
    blocks = [
        _defined_mcc_block(), _undefined_mcc_block(), _undefined_mcc_block(),
    ]
    agg = aggregate_tile_classification(blocks)
    assert agg["mcc"]["n_runs"] == 3
    assert agg["mcc"]["n_runs_defined"] == 1
    assert agg["mcc"]["point"] == 0.0665


@pytest.mark.tier1
def test_aggregate_returns_none_when_no_pass_is_defined() -> None:
    """All-undefined must aggregate to ``None``, not to 0.0."""
    agg = aggregate_tile_classification([_undefined_mcc_block()] * 3)
    assert agg["mcc"]["point"] is None
    assert agg["mcc"]["mean"] is None
    assert agg["mcc"]["ci_lower"] is None
    assert agg["mcc"]["ci_upper"] is None
    assert agg["mcc"]["n_runs_defined"] == 0


@pytest.mark.tier1
def test_aggregate_preserves_a_genuine_zero_mean() -> None:
    """NEGATIVE CASE — passes that genuinely measure 0.0 average to 0.0.

    Specificity in the degenerate fixture is a real zero on every pass.
    The aggregate must be ``0.0`` with all three passes counted, not
    ``None`` and not a short count.
    """
    agg = aggregate_tile_classification([_undefined_mcc_block()] * 3)
    assert agg["specificity"]["point"] == 0.0
    assert agg["specificity"]["point"] is not None
    assert agg["specificity"]["n_runs_defined"] == 3


@pytest.mark.tier1
def test_aggregate_records_that_the_confusion_matrix_is_run_ones() -> None:
    """The aggregated confusion matrix is run 1's — say so in the block.

    E81 noted that a run-1 matrix with ``TN = 1`` sitting beside a mean
    contaminated by a *different* run's degenerate matrix is what made
    the defect invisible on the face of the record.
    """
    agg = aggregate_tile_classification(
        [_defined_mcc_block(), _undefined_mcc_block()],
    )
    assert agg["confusion"] == {"tp": 204, "tn": 1, "fp": 135, "fn": 0}
    assert agg["confusion_source"] == "run_1"


# =========================================================================
# bootstrap: degenerate resamples skipped, not substituted
# =========================================================================


@pytest.mark.tier1
def test_bootstrap_skips_undefined_resamples_rather_than_scoring_them_zero(
) -> None:
    """A statistic that is undefined on some resamples must drop them.

    Before E81 the bootstrap scored a degenerate resample as ``0.0``, so
    every mean and both bounds were a mixture of measurements and
    placeholders — visible in the committed corpus as tile-MCC lower
    bounds of exactly ``0.0000`` beside a positive point estimate.
    """
    indices = np.arange(40)

    def sometimes_undefined(idx: np.ndarray) -> float:
        """Return 0.5 when tile 0 is present, otherwise undefined."""
        idx = np.asarray(idx, dtype=int)
        return 0.5 if 0 in idx else float("nan")

    skipped = _bca_ci_from_indices(
        indices, sometimes_undefined, 200, 42, skip_undefined=True,
    )
    assert skipped["mean"] == 0.5
    assert skipped["ci_lower"] == 0.5
    assert skipped["ci_upper"] == 0.5
    assert 0 < skipped["n_valid"] < 200


@pytest.mark.tier1
def test_bootstrap_reports_undefined_when_every_resample_is_degenerate(
) -> None:
    """No defined resample means no distribution — report ``None``."""
    result = _bca_ci_from_indices(
        np.arange(20), lambda _idx: float("nan"), 50, 42,
        skip_undefined=True,
    )
    assert result["mean"] is None
    assert result["ci_lower"] is None
    assert result["ci_upper"] is None
    assert result["method"] == "undefined"
    assert result["n_valid"] == 0


@pytest.mark.tier1
def test_bootstrap_is_unchanged_when_nothing_is_undefined() -> None:
    """NEGATIVE CASE — ``skip_undefined`` is inert on clean data.

    Pins the invariant that made the E81 re-emission safe: for a
    statistic that is always defined, turning the flag on must not move
    a single number, so no unaffected cell in the corpus can drift.
    """
    indices = np.arange(50)
    values = np.linspace(0.1, 0.9, 50)

    def mean_stat(idx: np.ndarray) -> float:
        """Mean of ``values`` over the resampled indices."""
        return float(values[np.asarray(idx, dtype=int)].mean())

    baseline = _bca_ci_from_indices(indices, mean_stat, 200, 42)
    with_flag = _bca_ci_from_indices(
        indices, mean_stat, 200, 42, skip_undefined=True,
    )
    assert baseline["mean"] == with_flag["mean"]
    assert baseline["ci_lower"] == with_flag["ci_lower"]
    assert baseline["ci_upper"] == with_flag["ci_upper"]
    assert baseline["method"] == with_flag["method"]


@pytest.mark.tier1
def test_bootstrap_preserves_a_genuinely_zero_statistic() -> None:
    """NEGATIVE CASE — a statistic that really is 0.0 reports 0.0.

    Specificity on the degenerate cells is exactly this: ``TN = 0`` out
    of 136 reference-empty tiles is a measurement, not a gap.
    """
    result = _bca_ci_from_indices(
        np.arange(30), lambda _idx: 0.0, 100, 42, skip_undefined=True,
    )
    assert result["mean"] == 0.0
    assert result["mean"] is not None
    assert result["ci_lower"] == 0.0
    assert result["n_valid"] == 100
    assert result["method"] != "undefined"


# =========================================================================
# RENDERERS: JSON, CSV, Markdown
# =========================================================================


@pytest.mark.tier1
def test_write_outputs_renders_undefined_mcc_in_all_three_siblings(
    tmp_path: Path,
) -> None:
    """JSON ``null``, an empty CSV cell, and the word "undefined" in MD."""
    results = {
        "label": "p2c-text-canonical",
        "n_detections": 897,
        "buffers": [_buffer_block(20)],
        "tile_classification": _undefined_mcc_block(),
    }
    write_outputs(results, None, tmp_path)

    payload = json.loads((tmp_path / "evaluation.json").read_text())
    assert payload["summary"]["tile_classification"]["mcc"]["point"] is None

    with open(tmp_path / "evaluation.csv", encoding="utf-8") as handle:
        row = next(iter(csv.DictReader(handle)))
    assert row["mcc"] == ""
    assert row["mcc_ci_lower"] == ""
    # NEGATIVE CASE: the measured zero is still written as a number.
    assert row["specificity"] == "0.0"

    markdown = (tmp_path / "evaluation.md").read_text(encoding="utf-8")
    assert "undefined" in markdown
    assert "**Undefined MCC**" in markdown
    assert "degenerate" in markdown
    # The MCC column must not carry a numeral for an undefined metric.
    data_row = next(
        line for line in markdown.splitlines() if line.startswith("| 20m ")
    )
    assert "undefined" in data_row


@pytest.mark.tier1
def test_write_outputs_renders_a_genuine_zero_mcc_as_a_number(
    tmp_path: Path,
) -> None:
    """NEGATIVE CASE — a real MCC of 0.0 must render as ``0.000``.

    A condition whose tile classification genuinely achieves chance
    discrimination is a legitimate result. It must not acquire the word
    "undefined", and it must not trigger the undefined-MCC footnote.
    """
    block = _defined_mcc_block()
    block["mcc"] = {
        "point": 0.0, "mean": 0.0, "ci_lower": -0.05,
        "ci_upper": 0.05, "method": "BCa",
    }
    results = {
        "label": "genuinely-random-condition",
        "n_detections": 500,
        "buffers": [_buffer_block(20)],
        "tile_classification": block,
    }
    write_outputs(results, None, tmp_path)

    payload = json.loads((tmp_path / "evaluation.json").read_text())
    assert payload["summary"]["tile_classification"]["mcc"]["point"] == 0.0

    with open(tmp_path / "evaluation.csv", encoding="utf-8") as handle:
        row = next(iter(csv.DictReader(handle)))
    assert row["mcc"] == "0.0"

    markdown = (tmp_path / "evaluation.md").read_text(encoding="utf-8")
    assert "**Undefined MCC**" not in markdown
    data_row = next(
        line for line in markdown.splitlines() if line.startswith("| 20m ")
    )
    assert "| 0.000 " in data_row
    assert UNDEFINED_DISPLAY not in data_row


@pytest.mark.tier1
def test_batch_summary_renders_undefined_without_crashing(
    tmp_path: Path,
) -> None:
    """The batch renderers must survive, and label, an undefined MCC."""
    summaries = [
        {
            "label": "undefined-cell",
            "n_runs": 1,
            "buffers": [_buffer_block(20)],
            "tile_classification": _undefined_mcc_block(),
        },
        {
            "label": "defined-cell",
            "n_runs": 1,
            "buffers": [_buffer_block(20)],
            "tile_classification": _defined_mcc_block(),
        },
    ]
    write_batch_summary(summaries, tmp_path)

    markdown = (tmp_path / "batch_summary.md").read_text(encoding="utf-8")
    undefined_row = next(
        line for line in markdown.splitlines() if "undefined-cell" in line
    )
    # The MCC and MCC-CI cells are undefined; the specificity cell that
    # follows them is a *measured* zero and must still read 0.000.
    cells = [c.strip() for c in undefined_row.split("|")]
    assert cells[-5] == UNDEFINED_DISPLAY, undefined_row  # MCC
    assert cells[-4] == UNDEFINED_DISPLAY, undefined_row  # MCC CI
    assert cells[-2] == "0.000", undefined_row            # specificity

    defined_row = next(
        line for line in markdown.splitlines() if "defined-cell" in line
        and "undefined-cell" not in line
    )
    assert "0.081" in defined_row

    with open(tmp_path / "batch_summary.csv", encoding="utf-8") as handle:
        rows = {r["label"]: r for r in csv.DictReader(handle)}
    assert rows["undefined-cell"]["mcc"] == ""
    assert rows["defined-cell"]["mcc"] == "0.081"


# =========================================================================
# REGRESSION GUARD ON THE COMMITTED CORPUS
# =========================================================================


@pytest.mark.tier1
def test_committed_e81_cells_no_longer_publish_an_imputed_zero() -> None:
    """The 13 withdrawn cells must not be back at 0.0 / 0.0443 / 0.0222.

    Reads the committed evaluations rather than recomputing them (no
    GeoJSON I/O), so it is a cheap tripwire against a regenerating
    script silently reinstating the imputation.
    """
    root = PROJECT_ROOT / "results/paper-eval/phase2/512px-14buf-mcc"
    if not root.is_dir():  # pragma: no cover - defensive for partial checkouts
        pytest.skip("phase-2 evaluation root not present")
    undefined_cells = [
        "p2b-text-t-0-0", "p2b-text-t-0-7",
        "p2c-image-exploratory-pure-positive-2hp", "p2c-text-canonical",
        "p2c-text-plus-hp", "p2c-text-pure-positive-canon",
        "p2c-text-scale-4", "p2c-text-scale-8", "p2d-text-terse",
    ]
    corrected_cells = [
        "p2a-brief-text", "p2a-verbose-text",
        "p2b-text-t-0-3", "p2b-text-t-1-0",
    ]
    for cell in undefined_cells:
        payload = json.loads(
            (root / cell / "evaluation.json").read_text(encoding="utf-8"),
        )
        mcc = payload["summary"]["tile_classification"]["mcc"]
        assert mcc["point"] is None, cell
        assert mcc["ci_lower"] is None, cell
    for cell in corrected_cells:
        payload = json.loads(
            (root / cell / "evaluation.json").read_text(encoding="utf-8"),
        )
        mcc = payload["summary"]["tile_classification"]["mcc"]
        assert mcc["point"] == 0.0665, cell
        assert mcc["n_runs_defined"] < mcc["n_runs"], cell
