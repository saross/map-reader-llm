"""
Tests for scripts/marking_campaign_gates.py — the persisted closing-gate
battery of the 2026-08 point-marking campaign.

Tier 1: synthetic states exercising each gate's detection logic — a gate
that cannot fail is not a gate, so every tier-1 case here manufactures
the defect its gate exists to catch (plus the legitimate case it must
NOT flag, where the distinction is load-bearing).

Tier 2: the full battery against the committed campaign layers must be
8/8 green. This is the insurance the battery was persisted for: if a
ruling-21 edit ever mutates a layer the gates read, this test fails.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from marking_campaign_gates import (  # noqa: E402
    _DEFAULT_GT_DIR,
    _DEFAULT_STUDENT_GT,
    gate_1_completeness,
    gate_3_red_partners,
    gate_4_double_claims,
    gate_5_no_claims_of_removed,
    gate_6_partnered_conflations,
    gate_8_unreviewed_cyan,
    load_marks,
    load_queue,
    load_student_points,
    run_gates,
)


# ---------------------------------------------------------------------------
# Synthetic-state helpers
# ---------------------------------------------------------------------------

_MARK_DEFAULTS = {
    "item_type": "phantom",
    "verdict": "distinct",
    "uncertain": False,
    "skipped": False,
    "x_marked": np.nan,
    "y_marked": np.nan,
    "resolved_partner_layer": np.nan,
    "resolved_partner_m": np.nan,
    "resolved_partner_x": np.nan,
    "resolved_partner_y": np.nan,
}


def make_marks(rows: list[dict]) -> pd.DataFrame:
    """Build a marks frame from partial row dicts, filling defaults."""
    return pd.DataFrame([{**_MARK_DEFAULTS, **row} for row in rows])


def make_queue(rows: list[dict]) -> pd.DataFrame:
    """Build a queue frame from partial row dicts."""
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Gate 1 — completeness
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_gate_1_detects_missing_and_orphan_marks() -> None:
    queue = make_queue([
        {"resolved_item_id": "promoted_phantom:1"},
        {"resolved_item_id": "promoted_phantom:2"},
    ])
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1"},
        {"resolved_item_id": "promoted_phantom:99"},
    ])
    result = gate_1_completeness(queue, marks)
    assert not result.passed
    assert any("never marked" in v for v in result.violations)
    assert any("no queue item" in v for v in result.violations)


@pytest.mark.tier1
def test_gate_1_detects_indecisive_verdicts() -> None:
    queue = make_queue([{"resolved_item_id": "promoted_phantom:1"}])
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1", "verdict": "uncertain",
         "uncertain": True},
    ])
    result = gate_1_completeness(queue, marks)
    assert not result.passed
    assert any("indecisive" in v for v in result.violations)


@pytest.mark.tier1
def test_gate_1_detects_tally_drift() -> None:
    """A complete queue with the wrong verdict mix is still a failure."""
    queue = make_queue([{"resolved_item_id": "promoted_phantom:1"}])
    marks = make_marks([{"resolved_item_id": "promoted_phantom:1"}])
    result = gate_1_completeness(queue, marks)
    assert not result.passed
    assert any("fingerprint" in v for v in result.violations)


# ---------------------------------------------------------------------------
# Gate 3 — red partners
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_gate_3_flags_a_second_red_claimant() -> None:
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:389", "verdict": "same_as_neighbour",
         "resolved_partner_layer": "superseded_premerge"},
        {"resolved_item_id": "promoted_phantom:7", "verdict": "same_as_neighbour",
         "resolved_partner_layer": "superseded_premerge"},
    ])
    assert not gate_3_red_partners(marks).passed


@pytest.mark.tier1
def test_gate_3_accepts_the_single_legal_claimant() -> None:
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:389", "verdict": "same_as_neighbour",
         "resolved_partner_layer": "superseded_premerge"},
    ])
    assert gate_3_red_partners(marks).passed


# ---------------------------------------------------------------------------
# Gate 4 — double claims
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_gate_4_accepts_co_located_shared_claims() -> None:
    """Two records of one mound marked at the same centre share a partner."""
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1", "verdict": "same_as_neighbour",
         "resolved_partner_layer": "corrected_student",
         "resolved_partner_x": 100.0, "resolved_partner_y": 200.0,
         "x_marked": 10.0, "y_marked": 20.0},
        {"resolved_item_id": "promoted_phantom:2", "verdict": "same_as_neighbour",
         "resolved_partner_layer": "corrected_student",
         "resolved_partner_x": 100.0, "resolved_partner_y": 200.0,
         "x_marked": 12.0, "y_marked": 20.0},
    ])
    assert gate_4_double_claims(marks).passed


@pytest.mark.tier1
def test_gate_4_flags_conflicting_double_claims() -> None:
    """The same partner claimed from marks 30 m apart is a contradiction."""
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1", "verdict": "same_as_neighbour",
         "resolved_partner_layer": "corrected_student",
         "resolved_partner_x": 100.0, "resolved_partner_y": 200.0,
         "x_marked": 10.0, "y_marked": 20.0},
        {"resolved_item_id": "promoted_phantom:2", "verdict": "same_as_neighbour",
         "resolved_partner_layer": "corrected_student",
         "resolved_partner_x": 100.0, "resolved_partner_y": 200.0,
         "x_marked": 40.0, "y_marked": 20.0},
    ])
    result = gate_4_double_claims(marks)
    assert not result.passed
    assert "30.0 m apart" in result.violations[0]


# ---------------------------------------------------------------------------
# Gate 5 — claims of removed records
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_gate_5_detects_claim_of_an_x_ed_record() -> None:
    queue = make_queue([
        {"resolved_item_id": "corrected_student:5", "source_layer": "corrected_student",
         "source_index": 5, "x": 100.0, "y": 200.0},
        {"resolved_item_id": "promoted_phantom:1", "source_layer": "promoted_phantom",
         "source_index": 1, "x": 300.0, "y": 400.0},
    ])
    marks = make_marks([
        {"resolved_item_id": "corrected_student:5", "verdict": "not_a_mound"},
        {"resolved_item_id": "promoted_phantom:1", "verdict": "same_as_neighbour",
         "resolved_partner_layer": "corrected_student",
         "resolved_partner_x": 100.0, "resolved_partner_y": 200.0},
    ])
    result = gate_5_no_claims_of_removed(queue, marks)
    assert not result.passed
    assert "corrected_student:5" in result.violations[0]


# ---------------------------------------------------------------------------
# Gate 6 — partner-less conflations
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_gate_6_detects_partner_less_conflation() -> None:
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1", "verdict": "same_as_neighbour"},
    ])
    result = gate_6_partnered_conflations(marks)
    assert not result.passed
    assert "promoted_phantom:1" in result.violations[0]


@pytest.mark.tier1
def test_gate_6_accepts_coordinate_less_legacy_claims() -> None:
    """Layer + distance without coordinates is a pre-fix mark, not a defect."""
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1", "verdict": "same_as_neighbour",
         "resolved_partner_layer": "corrected_student", "resolved_partner_m": 12.0},
    ])
    assert gate_6_partnered_conflations(marks).passed


# ---------------------------------------------------------------------------
# Gate 8 — unreviewed cyan
# ---------------------------------------------------------------------------

_STUDENT_POINTS = np.array([
    [100.0, 200.0],   # 0: queued
    [110.0, 200.0],   # 1: out of queue, near the marks below
    [900.0, 900.0],   # 2: out of queue, far away
])

_QUEUE_ONE_STUDENT = [
    {"resolved_item_id": "corrected_student:0", "source_layer": "corrected_student",
     "source_index": 0, "x": 100.0, "y": 200.0},
]


@pytest.mark.tier1
def test_gate_8_flags_unclaimed_cyan_inside_the_floor() -> None:
    queue = make_queue(_QUEUE_ONE_STUDENT)
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1", "verdict": "same_as_neighbour",
         "x_marked": 112.0, "y_marked": 200.0,
         "resolved_partner_layer": "corrected_student",
         "resolved_partner_x": 100.0, "resolved_partner_y": 200.0},
    ])
    result = gate_8_unreviewed_cyan(queue, marks, _STUDENT_POINTS)
    assert not result.passed
    assert "student #1" in result.violations[0]


@pytest.mark.tier1
def test_gate_8_accepts_the_claimed_partner() -> None:
    queue = make_queue(_QUEUE_ONE_STUDENT)
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1", "verdict": "same_as_neighbour",
         "x_marked": 112.0, "y_marked": 200.0,
         "resolved_partner_layer": "corrected_student",
         "resolved_partner_x": 110.0, "resolved_partner_y": 200.0},
    ])
    assert gate_8_unreviewed_cyan(queue, marks, _STUDENT_POINTS).passed


@pytest.mark.tier1
def test_gate_8_resolves_legacy_claims_by_distance() -> None:
    """A pre-fix claim carrying only layer + distance resolves to its cyan."""
    queue = make_queue(_QUEUE_ONE_STUDENT)
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1", "verdict": "same_as_neighbour",
         "x_marked": 112.0, "y_marked": 200.0,
         "resolved_partner_layer": "corrected_student",
         "resolved_partner_m": 2.0},
    ])
    assert gate_8_unreviewed_cyan(queue, marks, _STUDENT_POINTS).passed


@pytest.mark.tier1
def test_gate_8_ignores_distinct_and_fp_marks() -> None:
    """d is an explicit adjudication; a click left on an x asserts nothing."""
    queue = make_queue(_QUEUE_ONE_STUDENT)
    marks = make_marks([
        {"resolved_item_id": "promoted_phantom:1", "verdict": "distinct",
         "x_marked": 112.0, "y_marked": 200.0},
        {"resolved_item_id": "promoted_phantom:2", "verdict": "not_a_mound",
         "x_marked": 111.0, "y_marked": 200.0},
    ])
    assert gate_8_unreviewed_cyan(queue, marks, _STUDENT_POINTS).passed


# ---------------------------------------------------------------------------
# Tier 2 — the battery against the committed campaign state
# ---------------------------------------------------------------------------


@pytest.mark.tier2
def test_battery_is_green_on_the_committed_state() -> None:
    """All eight gates pass on the campaign layers as committed.

    This is the persistence rationale: ruling-21 application mutates
    reference artefacts derived FROM these layers, never the layers
    themselves (the marking app's output contract). Any edit that
    touches them breaks this test.
    """
    gt_dir = PROJECT_ROOT / _DEFAULT_GT_DIR
    student_gt = PROJECT_ROOT / _DEFAULT_STUDENT_GT
    if not gt_dir.exists() or not student_gt.exists():
        pytest.skip("campaign layers not present in this checkout")
    queue = load_queue(gt_dir / "marking-queue.csv")
    marks = load_marks(gt_dir / "marked-centres.csv")
    student_points = load_student_points(student_gt)
    results = run_gates(queue, marks, student_points)
    failed = [r.name for r in results if not r.passed]
    assert not failed, f"gates failed: {failed}"
