"""
Tests for consensus voting logic in 7_analyse_consensus.py.

Tier 1 unit tests for the two-stage pipeline voting threshold logic.
Tests verify correct filtering by proposer_votes and verifier_votes thresholds,
and the check_first_pass helper function.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_first_pass(row: pd.Series) -> bool:
    """
    Check if the first verifier pass returned verified=True.

    Extracted from 7_analyse_consensus.py for testing.

    Args:
        row: DataFrame row with 'verifier_results' column.

    Returns:
        True if first verifier pass verified the detection.
    """
    res = row.get("verifier_results")
    if not res or not isinstance(res, list) or len(res) == 0:
        return False
    return res[0].get("verified", False)


def create_predictions_gdf(
    records: list[dict],
    crs: str = "EPSG:32635",
) -> gpd.GeoDataFrame:
    """
    Create a GeoDataFrame of predictions for testing.

    Args:
        records: List of dicts with prediction attributes.
            Required keys: x, y, proposer_votes, verifier_votes
            Optional: verifier_results

    Returns:
        GeoDataFrame with prediction geometries and attributes.
    """
    if not records:
        return gpd.GeoDataFrame(
            {
                "proposer_votes": [],
                "verifier_votes": [],
                "verifier_results": [],
                "source_tile": [],
            },
            geometry=[],
            crs=crs,
        )

    data = {
        "proposer_votes": [r.get("proposer_votes", 1) for r in records],
        "verifier_votes": [r.get("verifier_votes", 0) for r in records],
        "verifier_results": [r.get("verifier_results", []) for r in records],
        "source_tile": [r.get("source_tile", "tile_001") for r in records],
    }
    points = [Point(r.get("x", 500000), r.get("y", 4700000)) for r in records]

    return gpd.GeoDataFrame(data, geometry=points, crs=crs)


@pytest.mark.tier1
class TestCheckFirstPass:
    """Tests for the check_first_pass helper function."""

    def test_verified_true_first_pass(self) -> None:
        """First pass verified=True should return True."""
        row = pd.Series({
            "verifier_results": [{"verified": True, "confidence": 0.9}],
        })
        assert check_first_pass(row) is True

    def test_verified_false_first_pass(self) -> None:
        """First pass verified=False should return False."""
        row = pd.Series({
            "verifier_results": [{"verified": False, "confidence": 0.1}],
        })
        assert check_first_pass(row) is False

    def test_multiple_passes_uses_first(self) -> None:
        """Only the first pass result should be checked."""
        # First pass False, second pass True -> should return False
        row = pd.Series({
            "verifier_results": [
                {"verified": False, "confidence": 0.1},
                {"verified": True, "confidence": 0.9},
            ],
        })
        assert check_first_pass(row) is False

        # First pass True, second pass False -> should return True
        row2 = pd.Series({
            "verifier_results": [
                {"verified": True, "confidence": 0.9},
                {"verified": False, "confidence": 0.1},
            ],
        })
        assert check_first_pass(row2) is True

    def test_empty_results_list(self) -> None:
        """Empty verifier_results should return False."""
        row = pd.Series({"verifier_results": []})
        assert check_first_pass(row) is False

    def test_none_results(self) -> None:
        """None verifier_results should return False."""
        row = pd.Series({"verifier_results": None})
        assert check_first_pass(row) is False

    def test_missing_results(self) -> None:
        """Missing verifier_results key should return False."""
        row = pd.Series({"other_field": "value"})
        assert check_first_pass(row) is False

    def test_non_list_results(self) -> None:
        """Non-list verifier_results should return False."""
        row = pd.Series({"verifier_results": "invalid"})
        assert check_first_pass(row) is False

    def test_missing_verified_key_in_result(self) -> None:
        """Missing 'verified' key in result dict should return False."""
        row = pd.Series({
            "verifier_results": [{"confidence": 0.9}],  # No 'verified' key
        })
        assert check_first_pass(row) is False


@pytest.mark.tier1
class TestProposerVotesFiltering:
    """Tests for filtering predictions by proposer_votes threshold."""

    def test_filter_by_proposer_threshold(self) -> None:
        """Predictions below threshold should be filtered out."""
        records = [
            {"x": 500000, "y": 4700000, "proposer_votes": 1, "verifier_votes": 5},
            {"x": 500100, "y": 4700000, "proposer_votes": 2, "verifier_votes": 5},
            {"x": 500200, "y": 4700000, "proposer_votes": 3, "verifier_votes": 5},
            {"x": 500300, "y": 4700000, "proposer_votes": 4, "verifier_votes": 5},
            {"x": 500400, "y": 4700000, "proposer_votes": 5, "verifier_votes": 5},
        ]
        gdf_pred = create_predictions_gdf(records)

        # Filter for proposer_votes >= 3
        filtered = gdf_pred[gdf_pred["proposer_votes"] >= 3]

        assert len(filtered) == 3
        assert all(filtered["proposer_votes"] >= 3)

    def test_filter_proposer_threshold_edge_cases(self) -> None:
        """Edge cases for proposer vote thresholds."""
        records = [
            {"x": 500000, "y": 4700000, "proposer_votes": 1, "verifier_votes": 5},
            {"x": 500100, "y": 4700000, "proposer_votes": 5, "verifier_votes": 5},
        ]
        gdf_pred = create_predictions_gdf(records)

        # Threshold = 1 should include all
        filtered_1 = gdf_pred[gdf_pred["proposer_votes"] >= 1]
        assert len(filtered_1) == 2

        # Threshold = 5 should include only unanimous
        filtered_5 = gdf_pred[gdf_pred["proposer_votes"] >= 5]
        assert len(filtered_5) == 1

        # Threshold = 6 should include none
        filtered_6 = gdf_pred[gdf_pred["proposer_votes"] >= 6]
        assert len(filtered_6) == 0


@pytest.mark.tier1
class TestVerifierVotesFiltering:
    """Tests for filtering predictions by verifier_votes threshold."""

    def test_filter_by_verifier_threshold(self) -> None:
        """Predictions below verifier threshold should be filtered out."""
        records = [
            {"x": 500000, "y": 4700000, "proposer_votes": 5, "verifier_votes": 1},
            {"x": 500100, "y": 4700000, "proposer_votes": 5, "verifier_votes": 2},
            {"x": 500200, "y": 4700000, "proposer_votes": 5, "verifier_votes": 3},
            {"x": 500300, "y": 4700000, "proposer_votes": 5, "verifier_votes": 4},
            {"x": 500400, "y": 4700000, "proposer_votes": 5, "verifier_votes": 5},
        ]
        gdf_pred = create_predictions_gdf(records)

        # Filter for verifier_votes >= 3
        filtered = gdf_pred[gdf_pred["verifier_votes"] >= 3]

        assert len(filtered) == 3
        assert all(filtered["verifier_votes"] >= 3)

    def test_combined_proposer_verifier_filtering(self) -> None:
        """Combined filtering by both proposer and verifier thresholds.

        This tests the 2D grid search logic used in analyse_consensus.
        """
        records = [
            # Low proposer, low verifier (should be filtered by both)
            {"x": 500000, "y": 4700000, "proposer_votes": 1, "verifier_votes": 1},
            # High proposer, low verifier (filtered by verifier)
            {"x": 500100, "y": 4700000, "proposer_votes": 5, "verifier_votes": 1},
            # Low proposer, high verifier (filtered by proposer)
            {"x": 500200, "y": 4700000, "proposer_votes": 1, "verifier_votes": 5},
            # High proposer, high verifier (should pass both)
            {"x": 500300, "y": 4700000, "proposer_votes": 5, "verifier_votes": 5},
            # Moderate both (should pass moderate thresholds)
            {"x": 500400, "y": 4700000, "proposer_votes": 3, "verifier_votes": 3},
        ]
        gdf_pred = create_predictions_gdf(records)

        # P>=3, V>=3 should return 2 records
        p_thresh = 3
        v_thresh = 3
        subset = gdf_pred[gdf_pred["proposer_votes"] >= p_thresh]
        subset = subset[subset["verifier_votes"] >= v_thresh]

        assert len(subset) == 2

    def test_unanimous_consensus_filtering(self) -> None:
        """Unanimous consensus (P=5, V=5) is the strictest threshold."""
        records = [
            {"x": 500000, "y": 4700000, "proposer_votes": 4, "verifier_votes": 5},
            {"x": 500100, "y": 4700000, "proposer_votes": 5, "verifier_votes": 4},
            {"x": 500200, "y": 4700000, "proposer_votes": 5, "verifier_votes": 5},
        ]
        gdf_pred = create_predictions_gdf(records)

        # Only unanimous (5,5) should pass
        subset = gdf_pred[
            (gdf_pred["proposer_votes"] >= 5) & (gdf_pred["verifier_votes"] >= 5)
        ]

        assert len(subset) == 1
        assert subset.iloc[0]["proposer_votes"] == 5
        assert subset.iloc[0]["verifier_votes"] == 5


@pytest.mark.tier1
class TestSinglePassVerifierSimulation:
    """Tests for single-pass verifier filtering (simulated v4.5 strategy)."""

    def test_filter_by_first_pass_verified(self) -> None:
        """Filter predictions where first verifier pass was True."""
        records = [
            # First pass verified
            {
                "x": 500000,
                "y": 4700000,
                "proposer_votes": 3,
                "verifier_votes": 3,
                "verifier_results": [{"verified": True}],
            },
            # First pass not verified
            {
                "x": 500100,
                "y": 4700000,
                "proposer_votes": 3,
                "verifier_votes": 3,
                "verifier_results": [{"verified": False}],
            },
            # Multiple passes, first True
            {
                "x": 500200,
                "y": 4700000,
                "proposer_votes": 3,
                "verifier_votes": 3,
                "verifier_results": [{"verified": True}, {"verified": False}],
            },
        ]
        gdf_pred = create_predictions_gdf(records)

        # Apply check_first_pass filter
        verified_mask = gdf_pred.apply(check_first_pass, axis=1)
        filtered = gdf_pred[verified_mask]

        assert len(filtered) == 2  # Records 0 and 2

    def test_proposer_then_first_pass_filtering(self) -> None:
        """Filter by proposer votes first, then by first pass verification.

        This matches the experiment in analyse_consensus:
        'Proposer Consensus + Single-Pass Verifier (v4.5)'
        """
        records = [
            # P=2 (filtered by proposer), first pass True
            {
                "x": 500000,
                "y": 4700000,
                "proposer_votes": 2,
                "verifier_votes": 1,
                "verifier_results": [{"verified": True}],
            },
            # P=3 (passes proposer), first pass False
            {
                "x": 500100,
                "y": 4700000,
                "proposer_votes": 3,
                "verifier_votes": 1,
                "verifier_results": [{"verified": False}],
            },
            # P=3 (passes proposer), first pass True
            {
                "x": 500200,
                "y": 4700000,
                "proposer_votes": 3,
                "verifier_votes": 1,
                "verifier_results": [{"verified": True}],
            },
        ]
        gdf_pred = create_predictions_gdf(records)

        # Step 1: Filter by proposer threshold (P>=3)
        subset_p = gdf_pred[gdf_pred["proposer_votes"] >= 3]
        assert len(subset_p) == 2  # Records 1 and 2

        # Step 2: Filter by first pass verification
        subset_verified = subset_p[subset_p.apply(check_first_pass, axis=1)]
        assert len(subset_verified) == 1  # Only record 2
