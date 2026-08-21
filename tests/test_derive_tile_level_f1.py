"""
Tier 1 unit tests for ``scripts/derive_tile_level_f1.py``.

Covers the two guarantees the supplemental tile-level F1 derivation rests on:

1. **Arithmetic** — precision, recall, F1, MCC, and prevalence computed from a
   synthetic confusion matrix match hand-worked values, and the MCC formula
   agrees with the canonical implementation used by the committed evaluations.
2. **Undefined-cell discipline** — a matrix with a vanishing marginal yields
   ``None`` (not ``0.0``) for the affected statistics, names the vanishing
   marginal, and is refused by the MCC reproduction gate rather than published.
"""

import math

import pytest

from scripts.derive_tile_level_f1 import (
    Confusion,
    build_report,
    check_mcc_gate,
    derive_comparator,
    marginal_report,
    prevalence,
    tile_f1,
    tile_mcc,
    tile_precision,
    tile_recall,
    vanishing_marginals,
)

pytestmark = pytest.mark.tier1


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def well_formed() -> Confusion:
    """A synthetic 100-tile matrix with all four marginals non-zero."""
    return Confusion(tp=40, fp=10, fn=20, tn=30)


@pytest.fixture
def no_predicted_negatives() -> Confusion:
    """A matrix where the model flagged every tile (``TN + FN == 0``).

    This is the degenerate shape the corpus actually contains — see erratum E81
    and ``docs/methodology/tile-mcc-explained.md`` trap 2.
    """
    return Confusion(tp=40, fp=60, fn=0, tn=0)


@pytest.fixture
def no_predicted_positives() -> Confusion:
    """A matrix where the model flagged nothing (``TP + FP == 0``)."""
    return Confusion(tp=0, fp=0, fn=40, tn=60)


# =============================================================================
# Arithmetic
# =============================================================================


def test_confusion_totals(well_formed: Confusion) -> None:
    """Totals and marginals are derived from the four cells."""
    assert well_formed.n_tiles == 100
    assert marginal_report(well_formed) == {
        "tp_plus_fp": 50,
        "tp_plus_fn": 60,
        "tn_plus_fp": 40,
        "tn_plus_fn": 50,
    }
    assert vanishing_marginals(well_formed) == []


def test_precision_recall_f1_arithmetic(well_formed: Confusion) -> None:
    """P, R, and F1 match hand-worked values on the synthetic matrix."""
    assert tile_precision(well_formed) == pytest.approx(40 / 50)
    assert tile_recall(well_formed) == pytest.approx(40 / 60)
    # 2*40 / (2*40 + 10 + 20) = 80 / 110
    assert tile_f1(well_formed) == pytest.approx(80 / 110)


def test_f1_is_the_harmonic_mean_of_precision_and_recall(well_formed: Confusion) -> None:
    """The count form of F1 agrees with the harmonic-mean form."""
    precision = tile_precision(well_formed)
    recall = tile_recall(well_formed)
    assert precision is not None and recall is not None
    harmonic = 2 * precision * recall / (precision + recall)
    assert tile_f1(well_formed) == pytest.approx(harmonic)


def test_mcc_arithmetic(well_formed: Confusion) -> None:
    """MCC matches the closed form used by ``calculate_tile_classification``."""
    expected = ((40 * 30) - (10 * 20)) / math.sqrt(50 * 60 * 40 * 50)
    assert tile_mcc(well_formed) == pytest.approx(expected)


def test_prevalence_is_the_reference_positive_tile_share(well_formed: Confusion) -> None:
    """Prevalence counts reference-positive tiles, not detections."""
    assert prevalence(well_formed) == pytest.approx(60 / 100)


def test_perfect_and_inverted_matrices() -> None:
    """MCC saturates at +1 for a perfect matrix and -1 for a fully inverted one."""
    assert tile_mcc(Confusion(tp=50, fp=0, fn=0, tn=50)) == pytest.approx(1.0)
    assert tile_mcc(Confusion(tp=0, fp=50, fn=50, tn=0)) == pytest.approx(-1.0)


def test_zero_true_positives_gives_defined_zero_f1() -> None:
    """With both marginals non-zero and ``TP == 0``, F1 is a defined 0.0."""
    cm = Confusion(tp=0, fp=10, fn=20, tn=70)
    assert tile_precision(cm) == 0.0
    assert tile_recall(cm) == 0.0
    assert tile_f1(cm) == 0.0
    assert vanishing_marginals(cm) == []


# =============================================================================
# Undefined-cell discipline
# =============================================================================


def test_undefined_when_no_predicted_negatives(no_predicted_negatives: Confusion) -> None:
    """``TN + FN == 0`` leaves MCC undefined while P, R, and F1 stay defined."""
    assert vanishing_marginals(no_predicted_negatives) == ["tn_plus_fn"]
    assert tile_mcc(no_predicted_negatives) is None
    # Precision and recall survive: both of their denominators are non-zero.
    assert tile_precision(no_predicted_negatives) == pytest.approx(0.4)
    assert tile_recall(no_predicted_negatives) == pytest.approx(1.0)
    assert tile_f1(no_predicted_negatives) is not None


def test_undefined_when_no_predicted_positives(no_predicted_positives: Confusion) -> None:
    """``TP + FP == 0`` makes precision and F1 undefined — null, never 0.0."""
    assert "tp_plus_fp" in vanishing_marginals(no_predicted_positives)
    assert tile_precision(no_predicted_positives) is None
    assert tile_f1(no_predicted_positives) is None
    assert tile_mcc(no_predicted_positives) is None
    # The distinction that matters: undefined is not the same object as zero.
    assert tile_f1(no_predicted_positives) is not tile_f1(
        Confusion(tp=0, fp=10, fn=20, tn=70)
    )


def test_undefined_recall_on_an_empty_reference() -> None:
    """``TP + FN == 0`` makes recall and F1 undefined."""
    cm = Confusion(tp=0, fp=25, fn=0, tn=75)
    assert tile_recall(cm) is None
    assert tile_f1(cm) is None
    assert tile_precision(cm) == 0.0


def test_prevalence_undefined_on_an_empty_grid() -> None:
    """An empty carrier grid has no prevalence."""
    assert prevalence(Confusion(tp=0, fp=0, fn=0, tn=0)) is None


# =============================================================================
# MCC reproduction gate
# =============================================================================


def test_gate_passes_on_a_four_decimal_committed_value() -> None:
    """A committed value stored at 4 dp passes when the recomputation rounds to it."""
    gate = check_mcc_gate(recomputed=0.7902523838362319, committed=0.7903)
    assert gate["passed"] is True
    assert gate["abs_delta"] < 1e-4


def test_gate_fails_on_a_material_discrepancy() -> None:
    """The 0.898-vs-0.790 trap-1 discrepancy is refused by the gate."""
    gate = check_mcc_gate(recomputed=0.8980, committed=0.7903)
    assert gate["passed"] is False
    assert gate["reason"]


def test_gate_fails_when_mcc_is_undefined() -> None:
    """An undefined MCC cannot verify a matrix, so the gate refuses it."""
    gate = check_mcc_gate(recomputed=None, committed=0.5)
    assert gate["passed"] is False
    assert gate["abs_delta"] is None


def test_gate_fails_just_outside_tolerance() -> None:
    """A discrepancy above 1e-4 fails even though it looks small."""
    gate = check_mcc_gate(recomputed=0.7901, committed=0.7903)
    assert gate["passed"] is False


# =============================================================================
# Comparator records and report assembly
# =============================================================================


def test_comparator_reproduces_a_published_f1() -> None:
    """The castles/GPT-4.1 comparator reproduces its published F1 of 67 %."""
    from scripts.derive_tile_level_f1 import COMPARATORS

    castles = next(c for c in COMPARATORS if c.key == "lk2025-castles-gpt41")
    record = derive_comparator(castles)
    assert record["tile_f1"] == pytest.approx(0.674, abs=5e-4)
    assert record["prevalence_reference_positive_tile_share"] == pytest.approx(
        379 / 1379
    )


def test_report_gate_summary_is_consistent(tmp_path) -> None:
    """With no artefacts present, every cell is reported missing, not silently ok."""
    report = build_report(tmp_path)
    assert report["validation_gate"]["n_passed"] == 0
    assert all(cell["status"] == "missing-artefact" for cell in report["cells"])
    assert "deferred to a Principal Investigator decision" in report["registration"]
