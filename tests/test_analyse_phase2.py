"""
Tests for Phase 2 multi-condition analysis functionality.

Tier 1 unit tests for the analyse_phase2_results.py script, focusing on
the Benjamini-Hochberg FDR correction for multiple pairwise comparisons.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from analyse_phase2_results import apply_fdr_correction


@pytest.mark.tier1
class TestApplyFdrCorrection:
    """Tests for the Benjamini-Hochberg FDR correction function."""

    def test_empty_list_returns_empty(self) -> None:
        """Empty pairwise results should return empty list."""
        result = apply_fdr_correction([])
        assert result == []

    def test_single_significant_comparison(self) -> None:
        """Single significant comparison should remain significant after FDR."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {
                    "mean": 0.05,
                    "ci_lower": 0.02,  # CI excludes zero
                    "ci_upper": 0.08,
                },
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        assert len(result) == 1
        assert result[0]["initially_significant"] is True
        assert result[0]["fdr_significant"] is True

    def test_single_non_significant_comparison(self) -> None:
        """Single non-significant comparison should remain non-significant."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {
                    "mean": 0.01,
                    "ci_lower": -0.02,  # CI includes zero
                    "ci_upper": 0.04,
                },
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        assert len(result) == 1
        assert result[0]["initially_significant"] is False
        assert result[0]["fdr_significant"] is False

    def test_negative_significant_effect(self) -> None:
        """Negative significant effect (B better than A) should be detected."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {
                    "mean": -0.05,
                    "ci_lower": -0.08,  # CI entirely negative
                    "ci_upper": -0.02,
                },
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        assert result[0]["initially_significant"] is True
        assert result[0]["fdr_significant"] is True

    def test_multiple_all_significant_preserved(self) -> None:
        """Multiple significant comparisons should mostly be preserved with FDR."""
        # All comparisons are strongly significant (CI far from zero)
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.10, "ci_lower": 0.07, "ci_upper": 0.13},
            },
            {
                "condition_a": "A",
                "condition_b": "C",
                "f1_difference": {"mean": 0.08, "ci_lower": 0.05, "ci_upper": 0.11},
            },
            {
                "condition_a": "B",
                "condition_b": "C",
                "f1_difference": {"mean": 0.06, "ci_lower": 0.03, "ci_upper": 0.09},
            },
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # All should be initially significant
        assert all(r["initially_significant"] for r in result)

        # Most should survive FDR (at least the strongest ones)
        n_fdr_sig = sum(1 for r in result if r["fdr_significant"])
        assert n_fdr_sig >= 1, "At least one comparison should survive FDR"

    def test_multiple_none_significant(self) -> None:
        """Multiple non-significant comparisons should all remain non-significant."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.01, "ci_lower": -0.02, "ci_upper": 0.04},
            },
            {
                "condition_a": "A",
                "condition_b": "C",
                "f1_difference": {"mean": -0.01, "ci_lower": -0.04, "ci_upper": 0.02},
            },
            {
                "condition_a": "B",
                "condition_b": "C",
                "f1_difference": {"mean": 0.00, "ci_lower": -0.03, "ci_upper": 0.03},
            },
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # None should be significant
        assert not any(r["initially_significant"] for r in result)
        assert not any(r["fdr_significant"] for r in result)

    def test_fdr_reduces_false_positives(self) -> None:
        """FDR correction should reduce the number of significant results.

        When many comparisons are borderline significant, FDR should
        be more conservative than uncorrected significance.
        """
        # Create 10 comparisons, some borderline significant
        pairwise = []
        for i in range(10):
            # Alternate between barely significant and barely non-significant
            if i % 2 == 0:
                # Barely significant (CI just excludes zero)
                ci_lower = 0.001  # Just above zero
            else:
                # Barely non-significant
                ci_lower = -0.001

            pairwise.append({
                "condition_a": f"A{i}",
                "condition_b": f"B{i}",
                "f1_difference": {
                    "mean": 0.02,
                    "ci_lower": ci_lower,
                    "ci_upper": 0.04,
                },
            })

        result = apply_fdr_correction(pairwise, q=0.05)

        n_initially_sig = sum(1 for r in result if r["initially_significant"])
        n_fdr_sig = sum(1 for r in result if r["fdr_significant"])

        # FDR should be equal or more conservative
        assert n_fdr_sig <= n_initially_sig, \
            "FDR should not increase number of significant results"

    def test_q_value_affects_threshold(self) -> None:
        """Higher q-value should allow more comparisons to pass FDR."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.03, "ci_lower": 0.001, "ci_upper": 0.06},
            },
            {
                "condition_a": "A",
                "condition_b": "C",
                "f1_difference": {"mean": 0.02, "ci_lower": 0.001, "ci_upper": 0.04},
            },
        ]

        result_strict = apply_fdr_correction(pairwise.copy(), q=0.01)
        result_lenient = apply_fdr_correction(pairwise.copy(), q=0.10)

        n_strict = sum(1 for r in result_strict if r["fdr_significant"])
        n_lenient = sum(1 for r in result_lenient if r["fdr_significant"])

        # Lenient q should allow at least as many
        assert n_lenient >= n_strict

    def test_preserves_original_fields(self) -> None:
        """FDR correction should preserve all original fields in results."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.05, "ci_lower": 0.02, "ci_upper": 0.08},
                "precision_difference": {"mean": 0.03, "ci_lower": 0.01, "ci_upper": 0.05},
                "recall_difference": {"mean": 0.07, "ci_lower": 0.04, "ci_upper": 0.10},
                "n_tiles": 60,
                "n_iterations": 1000,
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # All original fields should be preserved
        assert result[0]["condition_a"] == "A"
        assert result[0]["condition_b"] == "B"
        assert result[0]["precision_difference"]["mean"] == 0.03
        assert result[0]["recall_difference"]["mean"] == 0.07
        assert result[0]["n_tiles"] == 60
        assert result[0]["n_iterations"] == 1000

    def test_adds_significance_fields(self) -> None:
        """FDR correction should add initially_significant and fdr_significant fields."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.05, "ci_lower": 0.02, "ci_upper": 0.08},
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        assert "initially_significant" in result[0]
        assert "fdr_significant" in result[0]
        assert isinstance(result[0]["initially_significant"], bool)
        assert isinstance(result[0]["fdr_significant"], bool)


@pytest.mark.tier1
class TestApplyFdrCorrectionEdgeCases:
    """Edge case tests for FDR correction."""

    def test_missing_f1_difference_key(self) -> None:
        """Should handle missing f1_difference gracefully."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                # Missing f1_difference
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # Should not crash, should be marked non-significant
        assert len(result) == 1
        assert result[0]["initially_significant"] is False
        assert result[0]["fdr_significant"] is False

    def test_missing_ci_bounds(self) -> None:
        """Should handle missing CI bounds gracefully."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.05},  # Missing ci_lower/ci_upper
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # Should not crash
        assert len(result) == 1

    def test_ci_exactly_at_zero(self) -> None:
        """CI bound exactly at zero should not be significant."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {
                    "mean": 0.02,
                    "ci_lower": 0.0,  # Exactly at zero
                    "ci_upper": 0.04,
                },
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # CI touching zero should not be significant
        assert result[0]["initially_significant"] is False

    def test_very_large_number_of_comparisons(self) -> None:
        """Should handle large number of comparisons efficiently."""
        # 100 comparisons (e.g., 15 conditions = 105 pairwise)
        pairwise = []
        for i in range(100):
            # Half significant, half not
            if i < 50:
                ci_lower = 0.01 + i * 0.001  # Increasingly significant
            else:
                ci_lower = -0.01  # Not significant

            pairwise.append({
                "condition_a": f"A{i}",
                "condition_b": f"B{i}",
                "f1_difference": {
                    "mean": 0.03,
                    "ci_lower": ci_lower,
                    "ci_upper": 0.05,
                },
            })

        result = apply_fdr_correction(pairwise, q=0.05)

        assert len(result) == 100
        # FDR should be conservative - not more than initially significant
        n_initially_sig = sum(1 for r in result if r["initially_significant"])
        n_fdr_sig = sum(1 for r in result if r["fdr_significant"])
        assert n_fdr_sig <= n_initially_sig, "FDR should not increase significant count"
        # All results should have the significance fields
        assert all("initially_significant" in r for r in result)
        assert all("fdr_significant" in r for r in result)


# Import check
def test_import_apply_fdr_correction() -> None:
    """Verify that apply_fdr_correction can be imported."""
    from analyse_phase2_results import apply_fdr_correction as imported_fn
    assert callable(imported_fn)
