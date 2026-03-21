"""
Tests for evaluate_pv_results.py — PV pipeline evaluation.

Tier 1 unit tests for the candidate GeoDataFrame builder and
threshold sweep logic.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_pv_results import build_candidate_gdf


# =========================================================================
# FIXTURES
# =========================================================================


@pytest.fixture
def sample_manifest() -> dict:
    """A minimal candidate manifest with 4 candidates."""
    return {
        "version": "2.0",
        "padding": 75,
        "total_detections": 4,
        "successful_extractions": 4,
        "candidates": [
            {
                "candidate_id": 0,
                "crop_file": "crops/candidate_00000.png",
                "source_tile": "K-35-052-4_32635_x0_y0.png",
                "centroid_x": 398626.96,
                "centroid_y": 4704824.84,
            },
            {
                "candidate_id": 1,
                "crop_file": "crops/candidate_00001.png",
                "source_tile": "K-35-052-4_32635_x336_y0.png",
                "centroid_x": 398750.00,
                "centroid_y": 4704800.00,
            },
            {
                "candidate_id": 2,
                "crop_file": "crops/candidate_00002.png",
                "source_tile": "K-35-053-3_Elenovo_x0_y0.png",
                "centroid_x": 430100.00,
                "centroid_y": 4710200.00,
            },
            {
                "candidate_id": 3,
                "crop_file": "crops/candidate_00003.png",
                "source_tile": "K-35-062-2_Rakovski_x0_y0.png",
                "centroid_x": 420000.00,
                "centroid_y": 4690000.00,
            },
        ],
    }


@pytest.fixture
def sample_probabilities() -> dict[str, dict]:
    """Probabilities for the 4 sample candidates."""
    return {
        "candidate_00000": {
            "mound_probability": 0.9,
            "reasoning": "Clear mound",
        },
        "candidate_00001": {
            "mound_probability": 0.3,
            "reasoning": "Likely not",
        },
        "candidate_00002": {
            "mound_probability": 0.5,
            "reasoning": "Borderline",
        },
        "candidate_00003": {
            "mound_probability": 0.1,
            "reasoning": "Not a mound",
        },
    }


# =========================================================================
# BUILD CANDIDATE GDF
# =========================================================================


@pytest.mark.tier1
class TestBuildCandidateGdf:
    """Tests for build_candidate_gdf."""

    def test_threshold_filters_candidates(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """Only candidates at or above threshold are included."""
        gdf = build_candidate_gdf(
            sample_manifest, sample_probabilities, threshold=0.5,
        )
        # candidate_00000 (0.9) and candidate_00002 (0.5) pass
        assert len(gdf) == 2
        probs = sorted(gdf["mound_probability"].tolist())
        assert probs == [0.5, 0.9]

    def test_threshold_zero_includes_all(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """Threshold 0.0 includes all candidates."""
        gdf = build_candidate_gdf(
            sample_manifest, sample_probabilities, threshold=0.0,
        )
        assert len(gdf) == 4

    def test_threshold_one_strict_filter(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """Threshold 1.0 excludes all candidates below 1.0."""
        gdf = build_candidate_gdf(
            sample_manifest, sample_probabilities, threshold=1.0,
        )
        assert len(gdf) == 0

    def test_boundary_threshold_includes_exact_match(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """Probability exactly at threshold is included (>= not >)."""
        # threshold=0.3: candidates 0.9, 0.3, 0.5 pass; 0.1 excluded
        gdf = build_candidate_gdf(
            sample_manifest, sample_probabilities, threshold=0.3,
        )
        assert len(gdf) == 3
        probs = sorted(gdf["mound_probability"].tolist())
        assert probs == [0.3, 0.5, 0.9]

    def test_has_source_tile_column(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """GeoDataFrame includes source_tile column."""
        gdf = build_candidate_gdf(
            sample_manifest, sample_probabilities, threshold=0.0,
        )
        assert "source_tile" in gdf.columns

    def test_all_geometries_are_points(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """All rows have Point geometries from centroids."""
        gdf = build_candidate_gdf(
            sample_manifest, sample_probabilities, threshold=0.0,
        )
        assert (gdf.geometry.geom_type == "Point").all()

    def test_correct_crs(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """GeoDataFrame has EPSG:32635 CRS."""
        gdf = build_candidate_gdf(
            sample_manifest, sample_probabilities, threshold=0.0,
        )
        assert gdf.crs.to_epsg() == 32635

    def test_empty_manifest(
        self,
        sample_probabilities: dict,
    ) -> None:
        """Empty manifest produces empty GeoDataFrame."""
        gdf = build_candidate_gdf(
            {"candidates": []}, sample_probabilities, threshold=0.0,
        )
        assert len(gdf) == 0
        assert "source_tile" in gdf.columns

    def test_missing_probability_skips_candidate(
        self,
        sample_manifest: dict,
    ) -> None:
        """Candidates without probability entries are skipped."""
        # Only provide probability for candidate_00000
        partial_probs = {
            "candidate_00000": {"mound_probability": 0.9},
        }
        gdf = build_candidate_gdf(
            sample_manifest, partial_probs, threshold=0.0,
        )
        assert len(gdf) == 1
        # Verify the surviving candidate is specifically candidate_00000
        assert gdf["mound_probability"].iloc[0] == pytest.approx(0.9)

    def test_coordinates_match_manifest(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """Point coordinates match manifest centroid values."""
        gdf = build_candidate_gdf(
            sample_manifest, sample_probabilities, threshold=0.9,
        )
        # Only candidate_00000 passes (0.9 >= 0.9)
        assert len(gdf) == 1
        point = gdf.geometry.iloc[0]
        assert point.x == pytest.approx(398626.96)
        assert point.y == pytest.approx(4704824.84)

    def test_missing_candidates_key(
        self,
        sample_probabilities: dict,
    ) -> None:
        """Manifest without 'candidates' key returns empty GeoDataFrame."""
        gdf = build_candidate_gdf(
            {}, sample_probabilities, threshold=0.0,
        )
        assert len(gdf) == 0
        assert "source_tile" in gdf.columns

    def test_empty_probabilities(
        self,
        sample_manifest: dict,
    ) -> None:
        """Empty probabilities dict returns empty GeoDataFrame."""
        gdf = build_candidate_gdf(
            sample_manifest, {}, threshold=0.0,
        )
        assert len(gdf) == 0

    def test_malformed_candidate_skipped(self) -> None:
        """Candidate missing required fields is skipped, not crashed."""
        manifest = {
            "candidates": [
                {"candidate_id": 0},  # Missing centroid_x/y
                {
                    "candidate_id": 1,
                    "centroid_x": 400000.0,
                    "centroid_y": 4700000.0,
                    "source_tile": "tile.png",
                },
            ],
        }
        probs = {
            "candidate_00000": {"mound_probability": 0.9},
            "candidate_00001": {"mound_probability": 0.8},
        }
        gdf = build_candidate_gdf(manifest, probs, threshold=0.0)
        # Only candidate_00001 survives (candidate_00000 missing coords)
        assert len(gdf) == 1
        # Verify the correct candidate survived
        assert gdf["source_tile"].iloc[0] == "tile.png"
        assert gdf["mound_probability"].iloc[0] == pytest.approx(0.8)

    def test_missing_mound_probability_defaults_to_zero(self) -> None:
        """Result entry without mound_probability defaults to 0.0."""
        manifest = {
            "candidates": [{
                "candidate_id": 0,
                "centroid_x": 400000.0,
                "centroid_y": 4700000.0,
                "source_tile": "tile.png",
            }],
        }
        # Result exists but lacks mound_probability
        probs = {"candidate_00000": {"reasoning": "no score"}}
        gdf = build_candidate_gdf(manifest, probs, threshold=0.0)
        # Default 0.0 >= 0.0, so candidate is included
        assert len(gdf) == 1
        assert gdf["mound_probability"].iloc[0] == 0.0

    def test_custom_crs(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """Custom CRS parameter is applied."""
        gdf = build_candidate_gdf(
            sample_manifest, sample_probabilities,
            threshold=0.0, crs="EPSG:4326",
        )
        assert gdf.crs.to_epsg() == 4326


# =========================================================================
# CMD_SWEEP INTEGRATION (lightweight, no real bootstrap)
# =========================================================================


@pytest.mark.tier1
class TestCmdSweepIntegration:
    """Lightweight tests for cmd_sweep data flow.

    Test the results-key unwrapping and threshold generation
    without running the full bootstrap (which needs spatial data).
    """

    def test_results_key_unwrapping(
        self,
        sample_manifest: dict,
        sample_probabilities: dict,
    ) -> None:
        """build_candidate_gdf works with data unwrapped from 'results' key.

        Tests that probabilities extracted via ``.get("results", {})`` —
        the same unwrapping that ``load_probabilities`` performs — produce
        valid GeoDataFrame output. This is a unit test of the data format
        contract, not an integration test of ``load_probabilities`` itself.
        """
        # Simulate the real probabilities.json structure
        prob_data = {
            "version": "1.0",
            "mode": "realtime",
            "verifier_config": "test",
            "iterations": 1,
            "total_results": 4,
            "results": sample_probabilities,
        }
        unwrapped = prob_data.get("results", {})
        gdf = build_candidate_gdf(
            sample_manifest, unwrapped, threshold=0.5,
        )
        assert len(gdf) == 2
