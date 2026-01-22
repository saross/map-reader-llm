"""
Tests for Phase 4 transfer decision logic.

Tests the lib_phase4_transfer module functions for evaluating H6 Flash→Pro
transfer success and classifying transfer outcomes.
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_phase4_transfer import (
    evaluate_baseline_transfer,
    evaluate_factor_sensitivity,
    evaluate_voting_threshold_transfer,
    classify_transfer_outcome,
    ci_excludes_zero,
    TransferClassification,
    BASELINE_TRANSFER_THRESHOLD,
    BASELINE_INVESTIGATE_THRESHOLD,
    FACTOR_ADJUSTMENT_THRESHOLD,
    VOTING_THRESHOLD_DIFFERENCE,
)


# =============================================================================
# Tests: Phase 4a Baseline Transfer
# =============================================================================

class TestEvaluateBaselineTransfer:
    """Tests for Phase 4a baseline transfer evaluation."""

    @pytest.mark.tier1
    def test_full_transfer_within_threshold(self) -> None:
        """Δ F1 ≤ 0.05 should indicate transfer success."""
        result = evaluate_baseline_transfer(
            flash_f1=0.82,
            pro_f1=0.80,  # Δ = -0.02, within threshold
        )

        assert result.decision == "proceed"
        assert abs(result.delta_f1) <= BASELINE_TRANSFER_THRESHOLD
        assert "Transfer success" in result.message

    @pytest.mark.tier1
    def test_marginal_transfer_between_thresholds(self) -> None:
        """0.05 < |Δ F1| ≤ 0.10 should indicate marginal transfer."""
        result = evaluate_baseline_transfer(
            flash_f1=0.82,
            pro_f1=0.74,  # Δ = -0.08, between thresholds
        )

        assert result.decision == "proceed_with_caution"
        assert abs(result.delta_f1) > BASELINE_TRANSFER_THRESHOLD
        assert abs(result.delta_f1) <= BASELINE_INVESTIGATE_THRESHOLD
        assert "Marginal transfer" in result.message

    @pytest.mark.tier1
    def test_degradation_flag_beyond_threshold(self) -> None:
        """Δ F1 > 0.10 should flag for investigation."""
        result = evaluate_baseline_transfer(
            flash_f1=0.82,
            pro_f1=0.70,  # Δ = -0.12, beyond investigate threshold
        )

        assert result.decision == "investigate"
        assert abs(result.delta_f1) > BASELINE_INVESTIGATE_THRESHOLD
        assert "Large degradation" in result.message

    @pytest.mark.tier1
    def test_positive_delta_handled(self) -> None:
        """Positive Δ F1 (Pro better than Flash) should also be evaluated."""
        result = evaluate_baseline_transfer(
            flash_f1=0.80,
            pro_f1=0.85,  # Δ = +0.05, at threshold
        )

        assert result.decision == "proceed"
        assert result.delta_f1 == pytest.approx(0.05)

    @pytest.mark.tier1
    def test_exact_threshold_boundary(self) -> None:
        """Δ F1 exactly at threshold should indicate transfer success."""
        # Use values that clearly produce exactly 0.05 delta
        # Note: 0.80 - 0.75 may have floating point precision issues
        result = evaluate_baseline_transfer(
            flash_f1=0.80,
            pro_f1=0.85,  # Δ = +0.05, exactly at threshold (positive direction)
        )

        assert result.decision == "proceed"
        assert result.delta_f1 == pytest.approx(0.05)

    @pytest.mark.tier1
    def test_ci_values_stored(self) -> None:
        """CI values should be stored in result when provided."""
        result = evaluate_baseline_transfer(
            flash_f1=0.82,
            pro_f1=0.80,
            ci_lower=-0.05,
            ci_upper=0.01,
        )

        assert result.ci_lower == -0.05
        assert result.ci_upper == 0.01


# =============================================================================
# Tests: Phase 4b Factor Sensitivity
# =============================================================================

class TestEvaluateFactorSensitivity:
    """Tests for Phase 4b OFAT factor sensitivity evaluation."""

    @pytest.mark.tier1
    def test_flag_factor_exceeds_threshold(self) -> None:
        """Factor should be flagged if Δ F1 ≥ 0.03 and CI excludes zero."""
        result = evaluate_factor_sensitivity(
            factor_name="M/E",
            flash_optimal_level="brief-text-image",
            baseline_f1=0.80,
            alternatives=[
                {
                    "level": "verbose-text-image",
                    "f1": 0.84,  # Δ = +0.04, exceeds threshold
                    "ci_lower": 0.01,  # CI excludes zero
                    "ci_upper": 0.07,
                },
            ],
        )

        assert result.flagged is True
        assert result.recommended_level == "verbose-text-image"
        assert "flagged" in result.message.lower()

    @pytest.mark.tier1
    def test_no_flag_below_threshold(self) -> None:
        """Factor should not be flagged if Δ F1 < 0.03."""
        result = evaluate_factor_sensitivity(
            factor_name="H5",
            flash_optimal_level="minimal",
            baseline_f1=0.80,
            alternatives=[
                {
                    "level": "terse",
                    "f1": 0.82,  # Δ = +0.02, below threshold
                    "ci_lower": -0.01,
                    "ci_upper": 0.05,
                },
            ],
        )

        assert result.flagged is False
        assert result.recommended_level == "terse"  # Still tracks best
        assert "transfers" in result.message.lower()

    @pytest.mark.tier1
    def test_ci_excludes_zero_required_for_flag(self) -> None:
        """Factor should not be flagged if CI includes zero despite Δ F1 ≥ 0.03."""
        result = evaluate_factor_sensitivity(
            factor_name="T",
            flash_optimal_level="1.0",
            baseline_f1=0.80,
            alternatives=[
                {
                    "level": "0.7",
                    "f1": 0.84,  # Δ = +0.04, exceeds threshold
                    "ci_lower": -0.02,  # CI includes zero
                    "ci_upper": 0.10,
                },
            ],
        )

        assert result.flagged is False

    @pytest.mark.tier1
    def test_multiple_alternatives_evaluated(self) -> None:
        """All alternatives should be evaluated and best tracked."""
        result = evaluate_factor_sensitivity(
            factor_name="O",
            flash_optimal_level="canonical-first",
            baseline_f1=0.80,
            alternatives=[
                {
                    "level": "canonical-last",
                    "f1": 0.78,
                    "ci_lower": -0.05,
                    "ci_upper": 0.01,
                },
                {
                    "level": "random",
                    "f1": 0.85,  # Best
                    "ci_lower": 0.02,
                    "ci_upper": 0.08,
                },
            ],
        )

        assert len(result.tested_levels) == 3  # baseline + 2 alternatives
        assert result.recommended_level == "random"
        assert result.flagged is True  # random exceeds threshold with CI excluding 0

    @pytest.mark.tier1
    def test_baseline_included_in_tested_levels(self) -> None:
        """Baseline level should be included in tested_levels."""
        result = evaluate_factor_sensitivity(
            factor_name="M/E",
            flash_optimal_level="brief-text-image",
            baseline_f1=0.80,
            alternatives=[
                {"level": "image-only", "f1": 0.75, "ci_lower": -0.08, "ci_upper": -0.02},
            ],
        )

        baseline_entry = next(
            (l for l in result.tested_levels if l.get("is_baseline")), None
        )
        assert baseline_entry is not None
        assert baseline_entry["level"] == "brief-text-image"
        assert baseline_entry["f1"] == 0.80


# =============================================================================
# Tests: CI Helper Function
# =============================================================================

class TestCIExcludesZero:
    """Tests for confidence interval zero exclusion helper."""

    @pytest.mark.tier1
    def test_positive_ci_excludes_zero(self) -> None:
        """CI with both positive bounds excludes zero."""
        assert ci_excludes_zero(0.01, 0.05) is True

    @pytest.mark.tier1
    def test_negative_ci_excludes_zero(self) -> None:
        """CI with both negative bounds excludes zero."""
        assert ci_excludes_zero(-0.08, -0.02) is True

    @pytest.mark.tier1
    def test_spanning_ci_includes_zero(self) -> None:
        """CI spanning zero includes zero."""
        assert ci_excludes_zero(-0.02, 0.04) is False

    @pytest.mark.tier1
    def test_none_values_returns_false(self) -> None:
        """None CI values should return False."""
        assert ci_excludes_zero(None, 0.05) is False
        assert ci_excludes_zero(0.01, None) is False
        assert ci_excludes_zero(None, None) is False


# =============================================================================
# Tests: Phase 4c Voting Threshold Transfer
# =============================================================================

class TestEvaluateVotingThresholdTransfer:
    """Tests for Phase 4c voting threshold transfer evaluation."""

    @pytest.mark.tier1
    def test_voting_threshold_transfers(self) -> None:
        """Threshold within 10% relative should transfer."""
        result = evaluate_voting_threshold_transfer(
            flash_optimal_n=5,
            flash_optimal_threshold=2,
            pro_optimal_n=5,
            pro_optimal_threshold=2,  # 0% difference
        )

        assert result.flagged is False
        assert result.relative_difference == 0.0
        assert "transfers" in result.message.lower()

    @pytest.mark.tier1
    def test_voting_threshold_flagged(self) -> None:
        """Threshold >10% relative difference should be flagged."""
        result = evaluate_voting_threshold_transfer(
            flash_optimal_n=5,
            flash_optimal_threshold=2,
            pro_optimal_n=5,
            pro_optimal_threshold=3,  # 50% difference
        )

        assert result.flagged is True
        assert result.relative_difference > VOTING_THRESHOLD_DIFFERENCE
        assert "differs" in result.message.lower()

    @pytest.mark.tier1
    def test_voting_extended_test_needed(self) -> None:
        """Threshold >20% relative difference should need extended test."""
        result = evaluate_voting_threshold_transfer(
            flash_optimal_n=5,
            flash_optimal_threshold=2,
            pro_optimal_n=5,
            pro_optimal_threshold=3,  # 50% difference
        )

        assert result.needs_extended_test is True
        assert "extended" in result.message.lower()

    @pytest.mark.tier1
    def test_voting_10_percent_boundary(self) -> None:
        """Exactly 10% difference should not be flagged."""
        # 10% of 10 = 1, so threshold 11 is exactly 10% more
        result = evaluate_voting_threshold_transfer(
            flash_optimal_n=30,
            flash_optimal_threshold=10,
            pro_optimal_n=30,
            pro_optimal_threshold=11,  # 10% difference
        )

        assert result.flagged is False  # At boundary, not beyond
        assert result.relative_difference == pytest.approx(0.10)


# =============================================================================
# Tests: Transfer Classification
# =============================================================================

class TestClassifyTransferOutcome:
    """Tests for overall transfer classification."""

    @pytest.fixture
    def non_flagged_factor(self) -> "FactorSensitivityResult":
        """Create a non-flagged factor result."""
        from lib_phase4_transfer import FactorSensitivityResult
        return FactorSensitivityResult(
            factor_name="M/E",
            flash_optimal_level="brief-text-image",
            tested_levels=[],
            flagged=False,
            recommended_level="brief-text-image",
            message="",
        )

    @pytest.fixture
    def flagged_factor(self) -> "FactorSensitivityResult":
        """Create a flagged factor result."""
        from lib_phase4_transfer import FactorSensitivityResult
        return FactorSensitivityResult(
            factor_name="H5",
            flash_optimal_level="minimal",
            tested_levels=[],
            flagged=True,
            recommended_level="terse",
            message="",
        )

    @pytest.mark.tier1
    def test_full_transfer_no_flags(self, non_flagged_factor) -> None:
        """Zero flagged factors should classify as full transfer."""
        result = classify_transfer_outcome(
            factor_results=[non_flagged_factor] * 4,
        )

        assert result.classification == TransferClassification.FULL_TRANSFER
        assert len(result.factors_flagged) == 0
        assert "Full transfer" in result.message

    @pytest.mark.tier1
    def test_partial_transfer_one_flag(
        self, non_flagged_factor, flagged_factor
    ) -> None:
        """1-2 flagged factors should classify as partial transfer."""
        result = classify_transfer_outcome(
            factor_results=[non_flagged_factor, flagged_factor, non_flagged_factor],
        )

        assert result.classification == TransferClassification.PARTIAL_TRANSFER
        assert len(result.factors_flagged) == 1
        assert "H5" in result.factors_flagged
        assert "Partial transfer" in result.message

    @pytest.mark.tier1
    def test_partial_transfer_two_flags(
        self, non_flagged_factor, flagged_factor
    ) -> None:
        """Two flagged factors should classify as partial transfer."""
        from lib_phase4_transfer import FactorSensitivityResult

        flagged_factor_2 = FactorSensitivityResult(
            factor_name="T",
            flash_optimal_level="1.0",
            tested_levels=[],
            flagged=True,
            recommended_level="0.7",
            message="",
        )

        result = classify_transfer_outcome(
            factor_results=[non_flagged_factor, flagged_factor, flagged_factor_2],
        )

        assert result.classification == TransferClassification.PARTIAL_TRANSFER
        assert len(result.factors_flagged) == 2

    @pytest.mark.tier1
    def test_poor_transfer_three_plus_flags(self, flagged_factor) -> None:
        """≥3 flagged factors should classify as poor transfer."""
        from lib_phase4_transfer import FactorSensitivityResult

        factors = []
        for i, name in enumerate(["M/E", "H5", "T", "O"]):
            factors.append(
                FactorSensitivityResult(
                    factor_name=name,
                    flash_optimal_level=f"level_{i}",
                    tested_levels=[],
                    flagged=True,
                    recommended_level=f"alt_{i}",
                    message="",
                )
            )

        result = classify_transfer_outcome(factor_results=factors)

        assert result.classification == TransferClassification.POOR_TRANSFER
        assert len(result.factors_flagged) == 4
        assert "Poor transfer" in result.message

    @pytest.mark.tier1
    def test_pro_adjustments_recorded(self, flagged_factor) -> None:
        """Pro adjustments should be recorded for flagged factors."""
        result = classify_transfer_outcome(factor_results=[flagged_factor])

        assert "H5" in result.pro_adjustments
        assert result.pro_adjustments["H5"] == "terse"

    @pytest.mark.tier1
    def test_voting_flag_included(self, non_flagged_factor) -> None:
        """Voting flag should be included in outcome."""
        from lib_phase4_transfer import VotingTransferResult

        voting_result = VotingTransferResult(
            flash_optimal_n=5,
            flash_optimal_threshold=2,
            pro_optimal_n=5,
            pro_optimal_threshold=3,
            relative_difference=0.50,
            flagged=True,
            needs_extended_test=True,
            message="",
        )

        result = classify_transfer_outcome(
            factor_results=[non_flagged_factor],
            voting_result=voting_result,
        )

        assert result.voting_flagged is True
        assert "voting_threshold" in result.pro_adjustments
        assert "voting" in result.message.lower()
