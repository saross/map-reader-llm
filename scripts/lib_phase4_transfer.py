"""
Phase 4 Transfer Decision Logic

Provides decision logic functions for H6 Flash→Pro transfer testing.
These functions evaluate whether Flash-optimal parameters transfer to Pro
and classify the transfer outcome.

Usage:
    from lib_phase4_transfer import (
        evaluate_baseline_transfer,
        evaluate_factor_sensitivity,
        evaluate_voting_threshold_transfer,
        classify_transfer_outcome,
    )
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# =============================================================================
# Constants (from preregistration)
# =============================================================================

# Phase 4a: Baseline transfer thresholds
BASELINE_TRANSFER_THRESHOLD = 0.05  # |Δ F1| ≤ 0.05 → transfer success
BASELINE_INVESTIGATE_THRESHOLD = 0.10  # |Δ F1| > 0.10 → investigate

# Phase 4b: OFAT factor sensitivity threshold
FACTOR_ADJUSTMENT_THRESHOLD = 0.03  # Δ F1 ≥ 0.03 AND CI excludes 0 → flag

# Phase 4c: Voting threshold transfer
VOTING_THRESHOLD_DIFFERENCE = 0.10  # >10% relative difference → flag
VOTING_EXTENDED_TEST_THRESHOLD = 0.20  # >20% → run extended N=30 test


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class BaselineTransferResult:
    """Result of Phase 4a baseline transfer evaluation."""

    flash_f1: float
    pro_f1: float
    delta_f1: float
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    decision: str = ""  # "proceed", "proceed_with_caution", "investigate"
    message: str = ""


@dataclass
class FactorSensitivityResult:
    """Result of Phase 4b OFAT factor sensitivity evaluation."""

    factor_name: str
    flash_optimal_level: str
    tested_levels: list[dict]  # [{level, f1, ci_lower, ci_upper, delta, flagged}]
    flagged: bool = False
    recommended_level: str = ""
    message: str = ""


@dataclass
class VotingTransferResult:
    """Result of Phase 4c voting threshold transfer evaluation."""

    flash_optimal_n: int
    flash_optimal_threshold: int
    pro_optimal_n: int
    pro_optimal_threshold: int
    relative_difference: float
    flagged: bool = False
    needs_extended_test: bool = False
    message: str = ""


class TransferClassification(Enum):
    """Transfer outcome classification."""

    FULL_TRANSFER = "full_transfer"
    PARTIAL_TRANSFER = "partial_transfer"
    POOR_TRANSFER = "poor_transfer"


@dataclass
class TransferOutcome:
    """Overall Phase 4 transfer outcome."""

    classification: TransferClassification
    factors_flagged: list[str]
    voting_flagged: bool
    pro_adjustments: dict  # factor -> recommended adjustment
    message: str


# =============================================================================
# Phase 4a: Baseline Transfer Evaluation
# =============================================================================

def evaluate_baseline_transfer(
    flash_f1: float,
    pro_f1: float,
    ci_lower: Optional[float] = None,
    ci_upper: Optional[float] = None,
) -> BaselineTransferResult:
    """
    Evaluate Phase 4a baseline transfer.

    Determines whether Pro at Flash-optimal configuration achieves similar
    performance to Flash.

    Args:
        flash_f1: Flash F1 score (from Phase 2-3)
        pro_f1: Pro F1 score at Flash-optimal configuration
        ci_lower: Lower bound of 95% CI for delta (optional)
        ci_upper: Upper bound of 95% CI for delta (optional)

    Returns:
        BaselineTransferResult with decision and message
    """
    delta_f1 = pro_f1 - flash_f1
    abs_delta = abs(delta_f1)

    if abs_delta <= BASELINE_TRANSFER_THRESHOLD:
        decision = "proceed"
        message = (
            f"Transfer success: Pro F1 ({pro_f1:.3f}) within {BASELINE_TRANSFER_THRESHOLD} "
            f"of Flash F1 ({flash_f1:.3f}). Δ F1 = {delta_f1:+.3f}"
        )
    elif abs_delta <= BASELINE_INVESTIGATE_THRESHOLD:
        decision = "proceed_with_caution"
        message = (
            f"Marginal transfer: Pro F1 ({pro_f1:.3f}) differs from Flash F1 ({flash_f1:.3f}) "
            f"by {abs_delta:.3f}. Δ F1 = {delta_f1:+.3f}. Proceed but document."
        )
    else:
        decision = "investigate"
        message = (
            f"Large degradation: Pro F1 ({pro_f1:.3f}) differs from Flash F1 ({flash_f1:.3f}) "
            f"by {abs_delta:.3f}. Δ F1 = {delta_f1:+.3f}. Investigate before continuing."
        )

    return BaselineTransferResult(
        flash_f1=flash_f1,
        pro_f1=pro_f1,
        delta_f1=delta_f1,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        decision=decision,
        message=message,
    )


# =============================================================================
# Phase 4b: Factor Sensitivity Evaluation
# =============================================================================

def evaluate_factor_sensitivity(
    factor_name: str,
    flash_optimal_level: str,
    baseline_f1: float,
    alternatives: list[dict],
) -> FactorSensitivityResult:
    """
    Evaluate Phase 4b OFAT factor sensitivity.

    Determines whether any alternative level outperforms Flash-optimal
    by the flagging threshold.

    Args:
        factor_name: Name of the factor (e.g., "M/E", "H5", "T", "O")
        flash_optimal_level: Flash-optimal level name
        baseline_f1: Pro F1 at Flash-optimal level
        alternatives: List of dicts with keys:
            - level: Level name
            - f1: F1 score at this level
            - ci_lower: Lower bound of 95% CI
            - ci_upper: Upper bound of 95% CI

    Returns:
        FactorSensitivityResult with flagging decision
    """
    tested_levels = []
    flagged = False
    best_level = flash_optimal_level
    best_f1 = baseline_f1

    # Add baseline to tested levels
    tested_levels.append({
        "level": flash_optimal_level,
        "f1": baseline_f1,
        "ci_lower": None,
        "ci_upper": None,
        "delta": 0.0,
        "flagged": False,
        "is_baseline": True,
    })

    for alt in alternatives:
        level = alt["level"]
        f1 = alt["f1"]
        ci_lower = alt.get("ci_lower")
        ci_upper = alt.get("ci_upper")

        delta = f1 - baseline_f1

        # Check flagging criteria: Δ F1 ≥ threshold AND CI excludes zero
        ci_excludes_zero = False
        if ci_lower is not None and ci_upper is not None:
            # CI for the difference (delta)
            # If both bounds are positive, CI excludes zero (positive effect)
            # If both bounds are negative, CI excludes zero (negative effect)
            # For flagging, we want positive delta with CI excluding zero
            ci_excludes_zero = ci_lower > 0 or ci_upper < 0

        is_flagged = delta >= FACTOR_ADJUSTMENT_THRESHOLD and ci_excludes_zero

        tested_levels.append({
            "level": level,
            "f1": f1,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "delta": delta,
            "flagged": is_flagged,
            "is_baseline": False,
        })

        if is_flagged:
            flagged = True

        # Track best level
        if f1 > best_f1:
            best_f1 = f1
            best_level = level

    if flagged:
        message = (
            f"Factor {factor_name} flagged: Alternative level(s) outperform "
            f"Flash-optimal by ≥{FACTOR_ADJUSTMENT_THRESHOLD}. "
            f"Recommended: {best_level} (F1={best_f1:.3f})"
        )
    else:
        message = (
            f"Factor {factor_name} transfers: Flash-optimal level ({flash_optimal_level}) "
            f"remains optimal for Pro."
        )

    return FactorSensitivityResult(
        factor_name=factor_name,
        flash_optimal_level=flash_optimal_level,
        tested_levels=tested_levels,
        flagged=flagged,
        recommended_level=best_level,
        message=message,
    )


def ci_excludes_zero(ci_lower: float, ci_upper: float) -> bool:
    """
    Check if a confidence interval excludes zero.

    Args:
        ci_lower: Lower bound of CI
        ci_upper: Upper bound of CI

    Returns:
        True if CI excludes zero (both bounds same sign)
    """
    if ci_lower is None or ci_upper is None:
        return False
    return (ci_lower > 0 and ci_upper > 0) or (ci_lower < 0 and ci_upper < 0)


# =============================================================================
# Phase 4c: Voting Threshold Transfer Evaluation
# =============================================================================

def evaluate_voting_threshold_transfer(
    flash_optimal_n: int,
    flash_optimal_threshold: int,
    pro_optimal_n: int,
    pro_optimal_threshold: int,
) -> VotingTransferResult:
    """
    Evaluate Phase 4c voting threshold transfer.

    Determines whether Flash-optimal voting threshold transfers to Pro.

    Args:
        flash_optimal_n: Flash-optimal voting pool size (N)
        flash_optimal_threshold: Flash-optimal vote threshold (T)
        pro_optimal_n: Pro-optimal voting pool size
        pro_optimal_threshold: Pro-optimal vote threshold

    Returns:
        VotingTransferResult with flagging decision
    """
    # Calculate relative difference for threshold
    # Use Flash threshold as baseline
    if flash_optimal_threshold == 0:
        relative_difference = 1.0 if pro_optimal_threshold > 0 else 0.0
    else:
        relative_difference = abs(
            pro_optimal_threshold - flash_optimal_threshold
        ) / flash_optimal_threshold

    flagged = relative_difference > VOTING_THRESHOLD_DIFFERENCE
    needs_extended_test = relative_difference > VOTING_EXTENDED_TEST_THRESHOLD

    if not flagged:
        message = (
            f"Voting threshold transfers: Pro optimal T={pro_optimal_threshold} "
            f"within {VOTING_THRESHOLD_DIFFERENCE:.0%} of Flash T={flash_optimal_threshold}."
        )
    elif needs_extended_test:
        message = (
            f"Large voting difference: Pro T={pro_optimal_threshold} differs from "
            f"Flash T={flash_optimal_threshold} by {relative_difference:.0%}. "
            f"Run extended N=30 test for stability."
        )
    else:
        message = (
            f"Voting threshold differs: Pro T={pro_optimal_threshold} differs from "
            f"Flash T={flash_optimal_threshold} by {relative_difference:.0%}. "
            f"Document Pro-specific threshold."
        )

    return VotingTransferResult(
        flash_optimal_n=flash_optimal_n,
        flash_optimal_threshold=flash_optimal_threshold,
        pro_optimal_n=pro_optimal_n,
        pro_optimal_threshold=pro_optimal_threshold,
        relative_difference=relative_difference,
        flagged=flagged,
        needs_extended_test=needs_extended_test,
        message=message,
    )


# =============================================================================
# Overall Transfer Classification
# =============================================================================

def classify_transfer_outcome(
    factor_results: list[FactorSensitivityResult],
    voting_result: Optional[VotingTransferResult] = None,
) -> TransferOutcome:
    """
    Classify overall transfer outcome based on Phase 4b-4c results.

    Args:
        factor_results: List of FactorSensitivityResult from Phase 4b
        voting_result: Optional VotingTransferResult from Phase 4c

    Returns:
        TransferOutcome with classification and adjustments
    """
    flagged_factors = [r.factor_name for r in factor_results if r.flagged]
    num_flagged = len(flagged_factors)

    # Build adjustments dict
    pro_adjustments = {}
    for result in factor_results:
        if result.flagged:
            pro_adjustments[result.factor_name] = result.recommended_level

    voting_flagged = voting_result.flagged if voting_result else False
    if voting_flagged and voting_result:
        pro_adjustments["voting_threshold"] = voting_result.pro_optimal_threshold

    # Classify
    if num_flagged == 0:
        classification = TransferClassification.FULL_TRANSFER
        message = (
            "Full transfer: All factors transfer from Flash to Pro. "
            "Use Flash-optimal configuration for Pro."
        )
    elif num_flagged <= 2:
        classification = TransferClassification.PARTIAL_TRANSFER
        message = (
            f"Partial transfer: {num_flagged} factor(s) flagged for adjustment "
            f"({', '.join(flagged_factors)}). Document Pro-specific recommendations."
        )
    else:
        classification = TransferClassification.POOR_TRANSFER
        message = (
            f"Poor transfer: {num_flagged} factors flagged ({', '.join(flagged_factors)}). "
            f"Consider Pro-specific optimisation (out of scope for this study)."
        )

    if voting_flagged:
        message += f" Voting threshold also differs."

    return TransferOutcome(
        classification=classification,
        factors_flagged=flagged_factors,
        voting_flagged=voting_flagged,
        pro_adjustments=pro_adjustments,
        message=message,
    )
