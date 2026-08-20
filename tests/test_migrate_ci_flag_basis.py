"""Tests for scripts/migrate_ci_flag_basis.py and the generator's basis copy.

Phase 2 of the Session 137 audit remediation (defect D28): the committed
corpus's ``ci_unreliable`` flags are migrated from the retired sparse-coverage
heuristic to the measured rule, and the manifest generator copies the
``ci_flag_basis`` vintage marker instead of dropping it.
"""

from __future__ import annotations

import pytest

from scripts.generate_post_run_report import _metrics_from_eval
from scripts.migrate_ci_flag_basis import (
    BASIS_EXCLUSION_ONLY,
    BASIS_FULL,
    migrate_buffer_row,
    migrate_doc,
)

pytestmark = pytest.mark.tier1


def _scorer_row(**overrides) -> dict:
    """An old-vintage scorer buffer row: sparse-flagged, containing CIs."""
    row = {
        "buffer_metres": 20,
        "f1": 0.6, "f1_ci_lower": 0.55, "f1_ci_upper": 0.65,
        "precision": 0.5, "p_ci_lower": 0.45, "p_ci_upper": 0.55,
        "recall": 0.7, "r_ci_lower": 0.65, "r_ci_upper": 0.75,
        "coverage_status": "sparse_cross_grid",
        "ci_unreliable": True,  # the retired heuristic's verdict
    }
    row.update(overrides)
    return row


def test_sparse_only_flag_is_retired():
    """A sparse-flagged row whose CIs contain their points flips to False."""
    row = _scorer_row()
    rec = migrate_buffer_row(row)
    assert rec is not None and rec["old_flag"] is True
    assert row["ci_unreliable"] is False
    assert row["ci_excludes_point"] is False
    assert row["sparse_coverage"] is True  # descriptive, retained
    assert row["ci_flag_basis"] == BASIS_FULL


def test_measured_exclusion_stays_flagged():
    """A CI genuinely excluding its point keeps the flag — now truthfully."""
    row = _scorer_row(f1=0.9)  # outside [0.55, 0.65]
    migrate_buffer_row(row)
    assert row["ci_unreliable"] is True
    assert row["ci_excludes_point"] is True


def test_partial_coverage_stays_flagged():
    """E72 partial coverage flags unconditionally under the measured rule."""
    row = _scorer_row(coverage_status="partial_coverage")
    migrate_buffer_row(row)
    assert row["ci_unreliable"] is True
    assert row["ci_excludes_point"] is False


def test_adapter_row_gets_exclusion_only_basis():
    """Rows with no coverage_status must not claim the E72 ground was run."""
    row = {
        "buffer_metres": 50,
        "f1": 0.8, "f1_ci_lower": 0.78, "f1_ci_upper": 0.82,
        "precision": 0.8, "recall": 0.8,
        "f1_ci_method": "percentile",
        "ci_unreliable": False,
    }
    migrate_buffer_row(row)
    assert row["ci_flag_basis"] == BASIS_EXCLUSION_ONLY
    assert "sparse_coverage" not in row  # unknowable without coverage_status


def test_migration_is_idempotent():
    row = _scorer_row()
    assert migrate_buffer_row(row) is not None
    assert migrate_buffer_row(row) is None  # second pass: nothing to do


def test_rollup_recomputed_from_buffers():
    doc = {
        "summary": {
            "buffers": [_scorer_row(), _scorer_row(buffer_metres=30)],
            "ci_unreliable_any_buffer": True,
        },
        "per_run": [],
    }
    changes = migrate_doc(doc)
    assert doc["summary"]["ci_unreliable_any_buffer"] is False
    assert any(c.get("field") == "ci_unreliable_any_buffer" for c in changes)


def test_generator_copies_basis_when_present_omits_when_absent():
    """_metrics_from_eval propagates ci_flag_basis and never invents it."""
    summary = {
        "buffers": [
            {"buffer_metres": 20, "f1": 0.6, "precision": 0.5, "recall": 0.7,
             "f1_ci_lower": 0.55, "f1_ci_upper": 0.65,
             "ci_unreliable": False, "ci_flag_basis": BASIS_FULL},
            {"buffer_metres": 30, "f1": 0.6, "precision": 0.5, "recall": 0.7,
             "f1_ci_lower": 0.55, "f1_ci_upper": 0.65,
             "ci_unreliable": False},
        ],
        "tile_classification": {"mcc": {"point": 0.5}, "confusion":
                                {"tp": 1, "tn": 1, "fp": 1, "fn": 1}},
    }
    metrics = _metrics_from_eval(summary)
    assert metrics["per_buffer"]["20"]["ci_flag_basis"] == BASIS_FULL
    assert "ci_flag_basis" not in metrics["per_buffer"]["30"]
