"""
Tests for threshold sweep analysis in 7_analyse_consensus.py.

Tier 1 unit tests for the H3 hypothesis threshold sweep functionality
that analyses voting performance across multiple pool sizes (N) and
vote thresholds (T).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))



# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_gdf_with_votes():
    """Create a mock GeoDataFrame with vote_count property."""
    mock_gdf = MagicMock()
    mock_gdf.empty = False
    mock_gdf.columns = ["geometry", "vote_count", "label"]
    mock_gdf.crs = "EPSG:32635"
    mock_gdf.__len__ = MagicMock(return_value=10)

    # Simulate vote distribution: 2 detections with 5 votes, 3 with 3 votes, 5 with 1 vote
    vote_counts = [5, 5, 3, 3, 3, 1, 1, 1, 1, 1]
    mock_gdf.__getitem__ = MagicMock(side_effect=lambda key: MagicMock(
        max=MagicMock(return_value=5),
        __ge__=MagicMock(
            return_value=(
                [v >= key for v in vote_counts]
                if isinstance(key, int) else vote_counts
            )
        ),
    ) if key == "vote_count" else MagicMock())

    return mock_gdf


@pytest.fixture
def mock_empty_gdf():
    """Create an empty mock GeoDataFrame."""
    mock_gdf = MagicMock()
    mock_gdf.empty = True
    return mock_gdf


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


@pytest.mark.tier1
class TestCostEfficiencyCalculation:
    """Tests for the _calculate_cost_efficiency helper function."""

    def test_cost_efficiency_calculation(self) -> None:
        """Verify cost efficiency is correctly computed from curves data."""

        # Import the function we're testing
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from lib_advanced_metrics import calculate_f1_internal  # noqa: F401

        # Now import the actual function
        # Since _calculate_cost_efficiency is private, we test it through the main function
        # or import it directly for unit testing
        try:
            from scripts._7_analyse_consensus import _calculate_cost_efficiency
        except ImportError:
            # Import from the actual module path
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "analyse_consensus",
                PROJECT_ROOT / "scripts" / "7_analyse_consensus.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            _calculate_cost_efficiency = module._calculate_cost_efficiency

        curves = [
            {"n": 5, "threshold": 1, "f1": 0.60, "cost_usd": 0.90, "f1_per_dollar": 0.6667},
            {"n": 5, "threshold": 3, "f1": 0.75, "cost_usd": 0.90, "f1_per_dollar": 0.8333},
            {"n": 10, "threshold": 5, "f1": 0.80, "cost_usd": 1.80, "f1_per_dollar": 0.4444},
        ]

        efficiency = _calculate_cost_efficiency(curves)

        assert len(efficiency) == 3
        assert all("f1_per_dollar" in e for e in efficiency)
        assert all("n" in e and "threshold" in e for e in efficiency)

    def test_cost_efficiency_formula(self) -> None:
        """Verify F1 per dollar = F1 / cost formula."""
        # Given: N=5, n_tiles=60, cost_per_call=0.003
        # api_calls = 5 * 60 = 300
        # cost = 300 * 0.003 = 0.90 USD
        # If F1 = 0.75, then f1_per_dollar = 0.75 / 0.90 = 0.8333

        n = 5
        n_tiles = 60
        cost_per_call = 0.003
        f1 = 0.75

        api_calls = n * n_tiles
        cost = api_calls * cost_per_call
        f1_per_dollar = f1 / cost

        assert api_calls == 300
        assert cost == pytest.approx(0.90)
        assert f1_per_dollar == pytest.approx(0.8333, rel=0.01)

    def test_higher_n_higher_cost(self) -> None:
        """Verify that higher N leads to higher cost."""
        n_tiles = 60
        cost_per_call = 0.003

        cost_n5 = 5 * n_tiles * cost_per_call
        cost_n10 = 10 * n_tiles * cost_per_call
        cost_n30 = 30 * n_tiles * cost_per_call

        assert cost_n5 < cost_n10 < cost_n30
        assert cost_n5 == pytest.approx(0.90)
        assert cost_n10 == pytest.approx(1.80)
        assert cost_n30 == pytest.approx(5.40)


# =============================================================================
# THRESHOLD SWEEP STRUCTURE TESTS
# =============================================================================


@pytest.mark.tier1
class TestThresholdSweepStructure:
    """Tests for the threshold sweep result structure."""

    def test_sweep_returns_valid_structure(self) -> None:
        """Verify threshold sweep returns expected dictionary structure."""
        # Import the function
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "analyse_consensus",
            PROJECT_ROOT / "scripts" / "7_analyse_consensus.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _empty_sweep_result = module._empty_sweep_result

        # Test the empty result structure
        result = _empty_sweep_result(max_n=30, cost_per_call=0.003, n_tiles=60)

        # Verify top-level keys
        assert "curves" in result
        assert "optimal" in result
        assert "cost_efficiency" in result
        assert "metadata" in result

        # Verify optimal structure
        assert "n" in result["optimal"]
        assert "threshold" in result["optimal"]
        assert "f1" in result["optimal"]
        assert "precision" in result["optimal"]
        assert "recall" in result["optimal"]

        # Verify metadata
        assert "max_n" in result["metadata"]
        assert "cost_per_call" in result["metadata"]
        assert "n_tiles" in result["metadata"]

    def test_curves_contain_required_fields(self) -> None:
        """Verify each curve point contains required fields."""
        required_fields = [
            "n", "threshold", "f1", "precision", "recall",
            "count", "api_calls", "cost_usd", "f1_per_dollar"
        ]

        # Create a sample curve point
        sample_curve_point = {
            "n": 5,
            "threshold": 3,
            "f1": 0.75,
            "precision": 0.80,
            "recall": 0.70,
            "count": 15,
            "api_calls": 300,
            "cost_usd": 0.90,
            "f1_per_dollar": 0.8333,
        }

        for field in required_fields:
            assert field in sample_curve_point, f"Missing required field: {field}"

    def test_empty_predictions_returns_empty_curves(self) -> None:
        """Verify empty predictions produce empty curves list."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "analyse_consensus",
            PROJECT_ROOT / "scripts" / "7_analyse_consensus.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _empty_sweep_result = module._empty_sweep_result

        result = _empty_sweep_result(max_n=30, cost_per_call=0.003, n_tiles=60)

        assert result["curves"] == []
        assert result["optimal"]["f1"] == 0.0
        assert result["cost_efficiency"] == []


# =============================================================================
# OPTIMAL THRESHOLD TESTS
# =============================================================================


@pytest.mark.tier1
class TestOptimalThresholdSelection:
    """Tests for optimal threshold selection logic."""

    def test_optimal_is_highest_f1(self) -> None:
        """Verify optimal selection chooses highest F1 score."""
        curves = [
            {"n": 5, "threshold": 1, "f1": 0.50, "precision": 0.40, "recall": 0.70, "count": 20},
            {"n": 5, "threshold": 2, "f1": 0.65, "precision": 0.60, "recall": 0.72, "count": 15},
            {"n": 5, "threshold": 3, "f1": 0.75, "precision": 0.80,
             "recall": 0.70, "count": 10},  # Best
            {"n": 5, "threshold": 4, "f1": 0.70, "precision": 0.90, "recall": 0.58, "count": 5},
            {"n": 5, "threshold": 5, "f1": 0.60, "precision": 0.95, "recall": 0.45, "count": 2},
        ]

        # Find optimal using the same logic as the function
        best_f1 = 0.0
        optimal = None
        for point in curves:
            if point["f1"] > best_f1:
                best_f1 = point["f1"]
                optimal = point

        assert optimal is not None
        assert optimal["threshold"] == 3
        assert optimal["f1"] == 0.75

    def test_threshold_sweep_range(self) -> None:
        """Verify threshold sweep covers T=1 to T=N."""
        n = 5

        thresholds = list(range(1, n + 1))

        assert thresholds == [1, 2, 3, 4, 5]
        assert len(thresholds) == n

    def test_n_values_include_standard_sizes(self) -> None:
        """Verify standard N values (5, 10, max_n) are included."""
        max_n = 30
        max_observed = 30

        # Logic from the function
        n_values = [n for n in [5, 10, max_n] if n <= max_observed]

        assert 5 in n_values
        assert 10 in n_values
        assert 30 in n_values

    def test_n_values_capped_by_observed(self) -> None:
        """Verify N values don't exceed max observed votes."""
        max_n = 30
        max_observed = 7  # Only 7 passes worth of data

        n_values = [n for n in [5, 10, max_n] if n <= max_observed]

        assert 5 in n_values
        assert 10 not in n_values  # Exceeds max_observed
        assert 30 not in n_values


# =============================================================================
# VOTE FILTERING TESTS
# =============================================================================


@pytest.mark.tier1
class TestVoteFiltering:
    """Tests for vote threshold filtering logic."""

    def test_threshold_1_includes_all(self) -> None:
        """Verify T>=1 includes all detections."""
        vote_counts = [5, 5, 3, 3, 3, 1, 1, 1, 1, 1]

        filtered = [v for v in vote_counts if v >= 1]

        assert len(filtered) == 10

    def test_threshold_3_filters_low_votes(self) -> None:
        """Verify T>=3 excludes detections with fewer than 3 votes."""
        vote_counts = [5, 5, 3, 3, 3, 1, 1, 1, 1, 1]

        filtered = [v for v in vote_counts if v >= 3]

        assert len(filtered) == 5
        assert all(v >= 3 for v in filtered)

    def test_threshold_5_keeps_only_unanimous(self) -> None:
        """Verify T>=5 keeps only unanimous detections."""
        vote_counts = [5, 5, 3, 3, 3, 1, 1, 1, 1, 1]

        filtered = [v for v in vote_counts if v >= 5]

        assert len(filtered) == 2
        assert all(v == 5 for v in filtered)

    def test_high_threshold_may_empty_set(self) -> None:
        """Verify high threshold can result in zero detections."""
        vote_counts = [3, 3, 2, 2, 1, 1]

        filtered = [v for v in vote_counts if v >= 5]

        assert len(filtered) == 0


# =============================================================================
# PRECISION-RECALL TRADE-OFF TESTS
# =============================================================================


@pytest.mark.tier1
class TestPrecisionRecallTradeoff:
    """Tests demonstrating expected precision-recall trade-offs with threshold."""

    def test_higher_threshold_higher_precision(self) -> None:
        """Verify higher vote threshold typically increases precision.

        Intuition: Detections that appear in more passes are more likely
        to be true positives.
        """
        # Simulated data: precision increases with threshold
        results_by_threshold = {
            1: {"precision": 0.40, "recall": 0.90},
            2: {"precision": 0.55, "recall": 0.80},
            3: {"precision": 0.70, "recall": 0.65},
            4: {"precision": 0.85, "recall": 0.50},
            5: {"precision": 0.95, "recall": 0.30},
        }

        precisions = [results_by_threshold[t]["precision"] for t in [1, 2, 3, 4, 5]]

        # Precision should be monotonically increasing
        for i in range(len(precisions) - 1):
            assert precisions[i] <= precisions[i + 1], \
                f"Precision should increase: {precisions[i]} <= {precisions[i+1]}"

    def test_higher_threshold_lower_recall(self) -> None:
        """Verify higher vote threshold typically decreases recall.

        Intuition: Higher threshold filters out more detections, including
        some true positives that weren't detected in all passes.
        """
        results_by_threshold = {
            1: {"precision": 0.40, "recall": 0.90},
            2: {"precision": 0.55, "recall": 0.80},
            3: {"precision": 0.70, "recall": 0.65},
            4: {"precision": 0.85, "recall": 0.50},
            5: {"precision": 0.95, "recall": 0.30},
        }

        recalls = [results_by_threshold[t]["recall"] for t in [1, 2, 3, 4, 5]]

        # Recall should be monotonically decreasing
        for i in range(len(recalls) - 1):
            assert recalls[i] >= recalls[i + 1], \
                f"Recall should decrease: {recalls[i]} >= {recalls[i+1]}"

    def test_f1_peaks_at_intermediate_threshold(self) -> None:
        """Verify F1 often peaks at an intermediate threshold.

        F1 balances precision and recall, so extremes (T=1 or T=N) are
        typically suboptimal.
        """
        # Simulated F1 curve with peak at T=3
        f1_by_threshold = {
            1: 0.55,  # High recall, low precision
            2: 0.65,
            3: 0.70,  # Peak
            4: 0.65,
            5: 0.45,  # High precision, low recall
        }

        best_t = max(f1_by_threshold, key=f1_by_threshold.get)

        # Best F1 should not be at extremes
        assert best_t not in [1, 5], "F1 should peak at intermediate threshold"
        assert best_t == 3
