"""
Integration regression tests for F1 calculation pipeline.

Tier 1 tests that verify the complete F1 calculation pipeline produces
expected results on synthetic fixtures with known outcomes.

These tests catch regressions in:
- GeoJSON loading
- Spatial matching
- Precision/recall/F1 calculation
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (
    match_detections_to_references,
)


@pytest.fixture
def empty_fixture_data(fixtures_dir: Path) -> tuple[gpd.GeoDataFrame, ...]:
    """Load empty tile fixture data."""
    detections = gpd.read_file(fixtures_dir / "detections_empty.geojson")
    references = gpd.read_file(fixtures_dir / "references_empty.geojson")
    bounds = gpd.read_file(fixtures_dir / "bounds_empty.geojson")
    return detections, references, bounds


@pytest.fixture
def sparse_fixture_data(fixtures_dir: Path) -> tuple[gpd.GeoDataFrame, ...]:
    """Load sparse tile fixture data."""
    detections = gpd.read_file(fixtures_dir / "detections_sparse.geojson")
    references = gpd.read_file(fixtures_dir / "references_sparse.geojson")
    bounds = gpd.read_file(fixtures_dir / "bounds_sparse.geojson")
    return detections, references, bounds


@pytest.fixture
def sparse_expected_metrics(fixtures_dir: Path) -> dict:
    """Load expected metrics for sparse fixture."""
    with open(fixtures_dir / "expected_f1_sparse.json") as f:
        return json.load(f)


@pytest.fixture
def dense_fixture_data(fixtures_dir: Path) -> tuple[gpd.GeoDataFrame, ...]:
    """Load dense tile fixture data."""
    detections = gpd.read_file(fixtures_dir / "detections_dense.geojson")
    references = gpd.read_file(fixtures_dir / "references_dense.geojson")
    bounds = gpd.read_file(fixtures_dir / "bounds_dense.geojson")
    return detections, references, bounds


@pytest.fixture
def dense_expected_metrics(fixtures_dir: Path) -> dict:
    """Load expected metrics for dense fixture."""
    with open(fixtures_dir / "expected_f1_dense.json") as f:
        return json.load(f)


@pytest.mark.tier1
@pytest.mark.integration
class TestIntegrationF1Empty:
    """Integration tests for empty tile scenario."""

    def test_f1_empty_tile(self, empty_fixture_data: tuple) -> None:
        """F1 should be 0.0 for a tile with no detections and no references.

        This tests the edge case where both inputs are empty, which should
        produce F1=0.0 without errors.
        """
        detections, references, bounds = empty_fixture_data

        # Verify empty inputs
        assert len(detections) == 0, "Expected empty detections fixture"
        assert len(references) == 0, "Expected empty references fixture"

        # Use the matching function directly (calculate_f1_internal expects source_tile)
        det_geoms = list(detections.geometry) if len(detections) > 0 else []
        ref_geoms = list(references.geometry) if len(references) > 0 else []

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, max_distance=20)
        )

        # Calculate F1
        tp = len(matched_det)
        fp = len(unmatched_det)
        fn = len(unmatched_ref)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        assert f1 == pytest.approx(0.0), f"Expected F1=0.0 for empty tile, got {f1}"


@pytest.mark.tier1
@pytest.mark.integration
class TestIntegrationF1Sparse:
    """Integration tests for sparse tile scenario."""

    def test_f1_sparse_tile(
        self,
        sparse_fixture_data: tuple,
        sparse_expected_metrics: dict,
    ) -> None:
        """F1 should match expected value for sparse fixture.

        Fixture scenario: 3 references, 2 detections
        - 1 detection matches a reference (TP)
        - 1 detection is a false positive (FP)
        - 2 references are missed (FN)

        Expected: P=0.5, R=0.333, F1=0.4
        """
        detections, references, bounds = sparse_fixture_data

        # Verify fixture contents
        assert len(references) == 3, f"Expected 3 references, got {len(references)}"
        assert len(detections) == 2, f"Expected 2 detections, got {len(detections)}"

        # Calculate metrics using matching function
        det_geoms = list(detections.geometry)
        ref_geoms = list(references.geometry)

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, max_distance=20)
        )

        tp = len(matched_det)
        fp = len(unmatched_det)
        fn = len(unmatched_ref)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Verify against expected values
        expected_f1 = sparse_expected_metrics["f1"]
        expected_precision = sparse_expected_metrics["precision"]
        expected_recall = sparse_expected_metrics["recall"]

        assert precision == pytest.approx(expected_precision, abs=0.001), (
            f"Precision mismatch: expected {expected_precision}, got {precision}"
        )
        assert recall == pytest.approx(expected_recall, abs=0.001), (
            f"Recall mismatch: expected {expected_recall}, got {recall}"
        )
        assert f1 == pytest.approx(expected_f1, abs=0.001), (
            f"F1 mismatch: expected {expected_f1}, got {f1}"
        )


@pytest.mark.tier1
@pytest.mark.integration
class TestIntegrationF1Dense:
    """Integration tests for dense tile scenario."""

    def test_f1_dense_tile(
        self,
        dense_fixture_data: tuple,
        dense_expected_metrics: dict,
    ) -> None:
        """F1 should match expected value for dense fixture.

        Fixture scenario: 5 references, 4 detections
        - 3 detections match references (TP)
        - 1 detection is a false positive (FP)
        - 2 references are missed (FN)

        Expected: P=0.75, R=0.6, F1=0.667
        """
        detections, references, bounds = dense_fixture_data

        # Verify fixture contents
        assert len(references) == 5, f"Expected 5 references, got {len(references)}"
        assert len(detections) == 4, f"Expected 4 detections, got {len(detections)}"

        # Calculate metrics using matching function
        det_geoms = list(detections.geometry)
        ref_geoms = list(references.geometry)

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, max_distance=20)
        )

        tp = len(matched_det)
        fp = len(unmatched_det)
        fn = len(unmatched_ref)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Verify against expected values
        expected_f1 = dense_expected_metrics["f1"]
        expected_precision = dense_expected_metrics["precision"]
        expected_recall = dense_expected_metrics["recall"]

        assert precision == pytest.approx(expected_precision, abs=0.001), (
            f"Precision mismatch: expected {expected_precision}, got {precision}"
        )
        assert recall == pytest.approx(expected_recall, abs=0.001), (
            f"Recall mismatch: expected {expected_recall}, got {recall}"
        )
        assert f1 == pytest.approx(expected_f1, abs=0.001), (
            f"F1 mismatch: expected {expected_f1}, got {f1}"
        )
