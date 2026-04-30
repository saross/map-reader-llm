"""
Tier 1 tests for MCC column rendering in ``evaluation.csv`` /
``evaluation.md`` (single-mode) and ``batch_summary.md`` (batch-mode).

Background
----------
Until 2026-04-27, ``--mcc`` propagated the Matthews Correlation
Coefficient (MCC), sensitivity, and specificity into ``evaluation.json``
only — the CSV and Markdown emitters silently dropped them. Batch CSV
already gated on ``has_mcc``, but batch Markdown also omitted MCC.

These tests pin the additive fix so that the legacy 7-column CSV and
Markdown header are preserved when ``tile_classification`` is absent
(backwards-compatibility regression guard) and the wider header / row
cells appear when it is present.

The tests invoke the writers directly via in-memory dicts — no
subprocess, no GeoJSON I/O, no network — so they are tier-1 fast.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import (  # noqa: E402
    write_batch_summary,
    write_outputs,
)


# =========================================================================
# FIXTURES
# =========================================================================


def _buffer_block(buffer_metres: int = 20) -> dict:
    """Build a minimal per-buffer metrics dict.

    Mirrors the shape produced by ``evaluate_single_run`` /
    ``evaluate_multi_run_mean`` for one buffer entry, with deterministic
    floats so emitted text can be asserted exactly when needed.
    """
    return {
        "buffer_metres": buffer_metres,
        "f1": 0.800,
        "f1_ci_lower": 0.750,
        "f1_ci_upper": 0.850,
        "precision": 0.820,
        "p_ci_lower": 0.770,
        "p_ci_upper": 0.870,
        "recall": 0.780,
        "r_ci_lower": 0.730,
        "r_ci_upper": 0.830,
    }


def _tile_classification_block() -> dict:
    """Build a minimal ``tile_classification`` block.

    Matches the schema produced by ``calculate_tile_classification`` +
    ``bootstrap_tile_classification_ci`` (mean + CI for MCC,
    sensitivity, specificity; plus a confusion sub-dict that the writers
    do not emit).
    """
    return {
        "mcc": {"mean": 0.715, "ci_lower": 0.658, "ci_upper": 0.772},
        "sensitivity": {
            "mean": 0.738,
            "ci_lower": 0.681,
            "ci_upper": 0.797,
        },
        "specificity": {
            "mean": 0.954,
            "ci_lower": 0.924,
            "ci_upper": 0.977,
        },
        "confusion": {"tp": 100, "fp": 5, "fn": 35, "tn": 1000},
    }


def _results_with_mcc() -> dict:
    """Single-mode results dict with MCC populated."""
    return {
        "label": "high-t0.7-n30-t26",
        "n_runs": 30,
        "n_detections": 123,
        "buffers": [_buffer_block(20)],
        "tile_classification": _tile_classification_block(),
    }


def _results_without_mcc() -> dict:
    """Single-mode results dict with no MCC block (legacy shape)."""
    return {
        "label": "legacy-condition",
        "n_runs": 1,
        "n_detections": 42,
        "buffers": [_buffer_block(20)],
    }


# =========================================================================
# SINGLE-MODE TESTS
# =========================================================================


def _buffer_block_with_sparse_coverage(buffer_metres: int = 30) -> dict:
    """Build a buffer block flagged as sparse (Mitigation 3 trigger).

    Mirrors the shape produced by ``evaluate_single_run`` for a buffer
    where the coverage check fired (zero-fraction > 50 %). Used to test
    the CI-suppression rendering pathway in
    :func:`scripts.evaluate_detections.write_outputs`.
    """
    return {
        "buffer_metres": buffer_metres,
        "f1": 0.571,
        "f1_point": 0.571,
        "f1_ci_lower": 0.205,
        "f1_ci_upper": 0.514,
        "f1_ci_method": "BCa",
        "precision": 0.445,
        "p_point": 0.445,
        "p_ci_lower": 0.150,
        "p_ci_upper": 0.450,
        "p_ci_method": "BCa",
        "recall": 0.795,
        "r_point": 0.795,
        "r_ci_lower": 0.300,
        "r_ci_upper": 0.700,
        "r_ci_method": "BCa",
        "coverage": {
            "n_tiles": 487,
            "n_zero_count_tiles": 393,
            "zero_fraction": 0.807,
            "threshold": 0.5,
            "coverage_status": "sparse_cross_grid",
        },
        "coverage_status": "sparse_cross_grid",
        "ci_unreliable": True,
    }


@pytest.mark.tier1
class TestSingleModeMccRendering:
    """``write_outputs`` emits MCC columns iff ``tile_classification``."""

    def test_single_mode_mcc_columns_in_csv_and_md(
        self,
        tmp_path: Path,
    ) -> None:
        """CSV header gains MCC fields; Markdown header gains MCC + Sens.

        Asserts both headers AND that the buffer row carries the MCC
        mean (formatted to .3f), so a regression that emits the wider
        header but forgets the cells would still fail.
        """
        write_outputs(
            results=_results_with_mcc(),
            run_results=None,
            output_dir=tmp_path,
        )

        csv_text = (tmp_path / "evaluation.csv").read_text(encoding="utf-8")
        # Header row must contain the additive columns in order.
        first_line = csv_text.splitlines()[0]
        assert (
            "mcc,mcc_ci_lower,mcc_ci_upper,sensitivity,specificity"
            in first_line
        )
        # Body row must carry the MCC mean to 4 decimal places (csv
        # writer does not reformat — it stringifies the dict value).
        assert "0.715" in csv_text

        md_text = (tmp_path / "evaluation.md").read_text(encoding="utf-8")
        # Markdown header gains MCC, MCC CI, Sens, Spec.
        assert "| MCC |" in md_text
        assert "| Sens |" in md_text
        assert "| Spec |" in md_text
        # Body row carries the .3f-formatted MCC mean.
        assert "0.715" in md_text

    def test_sparse_coverage_suppresses_md_ci(
        self,
        tmp_path: Path,
    ) -> None:
        """Sparse-coverage rows get ``N/A *`` in MD; footnote is emitted.

        Mitigation 3 (commit ``feat(bootstrap): replace percentile method
        with BCa``): when ``ci_unreliable=True`` the Markdown writer
        replaces the numeric CI cells with ``N/A *`` and appends a
        footnote at the bottom of the table. The point estimate
        (``f1``, ``precision``, ``recall``) is preserved.
        """
        results = {
            "label": "sparse-cell-512px-image-t0",
            "n_runs": 1,
            "n_detections": 50,
            "buffers": [_buffer_block_with_sparse_coverage(30)],
        }
        write_outputs(
            results=results,
            run_results=None,
            output_dir=tmp_path,
        )

        md_text = (tmp_path / "evaluation.md").read_text(encoding="utf-8")
        # CI cells suppressed.
        assert "N/A *" in md_text
        # Numeric bounds NOT in the rendered table (they are still in JSON).
        assert "[0.205, 0.514]" not in md_text
        # Point estimate preserved (rendered to .3f).
        assert "0.571" in md_text
        # Footnote present.
        assert "Bootstrap CI suppressed" in md_text
        assert "80.7%" in md_text or "80.7 %" in md_text

    def test_sparse_coverage_csv_keeps_numeric_bounds(
        self,
        tmp_path: Path,
    ) -> None:
        """Sparse-coverage rows keep numeric CI bounds in CSV.

        The CSV is the machine-readable contract for downstream tooling;
        we add a ``ci_unreliable`` boolean column so consumers can
        filter, but we do NOT remove the numeric CI bounds (some
        consumers may want them despite the warning). The header gains
        the new diagnostics columns.
        """
        results = {
            "label": "sparse-cell-512px-image-t0",
            "n_runs": 1,
            "n_detections": 50,
            "buffers": [_buffer_block_with_sparse_coverage(30)],
        }
        write_outputs(
            results=results,
            run_results=None,
            output_dir=tmp_path,
        )

        csv_text = (tmp_path / "evaluation.csv").read_text(encoding="utf-8")
        first_line = csv_text.splitlines()[0]
        # New diagnostics columns appended.
        assert "coverage_status" in first_line
        assert "ci_unreliable" in first_line
        assert "ci_zero_fraction" in first_line
        assert "ci_n_tiles" in first_line
        # Numeric CI bounds still present in the body.
        assert "0.205" in csv_text
        # Status flag value present in the body.
        assert "sparse_cross_grid" in csv_text

    def test_dense_coverage_no_md_footnote(
        self,
        tmp_path: Path,
    ) -> None:
        """Dense (non-sparse) buffers => no footnote, no ``N/A *``.

        Regression guard for the legacy rendering path: a result dict
        without the ``ci_unreliable`` flag must render exactly as it did
        before the commit. The footnote is only emitted when at least
        one row trips the flag.
        """
        # Use the legacy block (no coverage_status / ci_unreliable keys).
        write_outputs(
            results=_results_with_mcc(),
            run_results=None,
            output_dir=tmp_path,
        )
        md_text = (tmp_path / "evaluation.md").read_text(encoding="utf-8")
        assert "N/A *" not in md_text
        assert "Bootstrap CI suppressed" not in md_text

    def test_single_mode_no_mcc_unchanged(
        self,
        tmp_path: Path,
    ) -> None:
        """Legacy results dict yields the original 7-column header.

        Backwards-compatibility regression guard: any change to the
        without-MCC code path that adds MCC columns to legacy outputs
        would fail this test.
        """
        write_outputs(
            results=_results_without_mcc(),
            run_results=None,
            output_dir=tmp_path,
        )

        csv_text = (tmp_path / "evaluation.csv").read_text(encoding="utf-8")
        first_line = csv_text.splitlines()[0]
        # Legacy CSV header has exactly 11 columns and NO MCC fields.
        assert first_line == (
            "label,buffer_metres,"
            "f1,f1_ci_lower,f1_ci_upper,"
            "precision,p_ci_lower,p_ci_upper,"
            "recall,r_ci_lower,r_ci_upper"
        )
        assert "mcc" not in first_line
        assert "sensitivity" not in first_line

        md_text = (tmp_path / "evaluation.md").read_text(encoding="utf-8")
        # Legacy Markdown header is the original 7-column form.
        assert (
            "| Buffer | F1 | F1 CI | P | P CI | R | R CI |\n" in md_text
        )
        assert "MCC" not in md_text
        assert "Sens" not in md_text


# =========================================================================
# BATCH-MODE TESTS
# =========================================================================


@pytest.mark.tier1
class TestBatchModeMccRendering:
    """``write_batch_summary`` markdown gains MCC cells when populated."""

    def test_batch_mode_md_has_mcc(self, tmp_path: Path) -> None:
        """Batch markdown header AND row carry MCC when one supplies it.

        ``write_batch_summary`` already gated CSV on ``has_mcc``; this
        test pins the same gating for the markdown emitter.
        """
        summary = {
            "label": "demo-condition",
            "n_runs": 30,
            "n_detections": 100,
            "buffers": [_buffer_block(20)],
            "tile_classification": _tile_classification_block(),
        }
        write_batch_summary(
            all_summaries=[summary],
            output_dir=tmp_path,
            metadata={"description": "MCC rendering smoke test"},
        )

        md_text = (tmp_path / "batch_summary.md").read_text(
            encoding="utf-8",
        )
        # Header gains MCC, MCC CI, Sens, Spec columns.
        assert "| MCC |" in md_text
        assert "| MCC CI |" in md_text
        assert "| Sens |" in md_text
        assert "| Spec |" in md_text
        # Body row carries the .3f-formatted MCC mean.
        assert "0.715" in md_text

        # CSV gating was already correct; cross-check it here so this
        # module is the canonical home for the MCC-rendering invariant.
        csv_text = (tmp_path / "batch_summary.csv").read_text(
            encoding="utf-8",
        )
        first_line = csv_text.splitlines()[0]
        assert "mcc" in first_line
        assert "sensitivity" in first_line
        assert "specificity" in first_line
