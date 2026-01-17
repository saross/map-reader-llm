"""
Tests for F1 score calculation functions.

Tier 1 unit tests for the core metrics calculation in lib_advanced_metrics.py.
Uses synthetic GeoDataFrames to verify correct precision, recall, and F1
calculation under controlled conditions.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import match_detections_to_references

# Standard spatial tolerance from preregistration (metres)
SPATIAL_TOLERANCE = 20


def create_point_gdf(coords: list[tuple[float, float]], crs: str = "EPSG:32635") -> gpd.GeoDataFrame:
    """Create a GeoDataFrame of points from coordinate tuples.

    Args:
        coords: List of (x, y) coordinate tuples in the specified CRS.
        crs: Coordinate reference system (default EPSG:32635).

    Returns:
        GeoDataFrame with Point geometries.
    """
    if not coords:
        return gpd.GeoDataFrame(geometry=[], crs=crs)

    points = [Point(x, y) for x, y in coords]
    return gpd.GeoDataFrame(geometry=points, crs=crs)


@pytest.mark.tier1
class TestMatchDetectionsToReferences:
    """Tests for the Hungarian algorithm matching function."""

    def test_f1_perfect_match(self) -> None:
        """F1 should be 1.0 when detections exactly match references.

        Creates 3 detections at the same locations as 3 references.
        All should match (3 TP, 0 FP, 0 FN) -> F1 = 1.0
        """
        # Reference points (in metres, UTM coordinates)
        ref_coords = [(500000, 4700000), (500050, 4700050), (500100, 4700100)]

        # Detection points at exact same locations
        det_coords = [(500000, 4700000), (500050, 4700050), (500100, 4700100)]

        det_geoms = create_point_gdf(det_coords).geometry.tolist()
        ref_geoms = create_point_gdf(ref_coords).geometry.tolist()

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, SPATIAL_TOLERANCE)
        )

        # All 3 should match
        assert len(matched_det) == 3, f"Expected 3 matched detections, got {len(matched_det)}"
        assert len(matched_ref) == 3, f"Expected 3 matched references, got {len(matched_ref)}"
        assert len(unmatched_det) == 0, f"Expected 0 unmatched detections, got {len(unmatched_det)}"
        assert len(unmatched_ref) == 0, f"Expected 0 unmatched references, got {len(unmatched_ref)}"

        # Calculate F1 from matching results
        tp = len(matched_det)
        fp = len(unmatched_det)
        fn = len(unmatched_ref)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        assert f1 == pytest.approx(1.0), f"Expected F1=1.0, got {f1}"

    def test_f1_no_matches(self) -> None:
        """F1 should be 0.0 when all detections are too far from references.

        Creates detections >20m away from all references.
        None should match (0 TP, 2 FP, 3 FN) -> F1 = 0.0
        """
        # Reference points
        ref_coords = [(500000, 4700000), (500050, 4700050), (500100, 4700100)]

        # Detection points far away (>20m from all references)
        det_coords = [(500200, 4700200), (500250, 4700250)]

        det_geoms = create_point_gdf(det_coords).geometry.tolist()
        ref_geoms = create_point_gdf(ref_coords).geometry.tolist()

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, SPATIAL_TOLERANCE)
        )

        # None should match
        assert len(matched_det) == 0, f"Expected 0 matched detections, got {len(matched_det)}"
        assert len(matched_ref) == 0, f"Expected 0 matched references, got {len(matched_ref)}"
        assert len(unmatched_det) == 2, f"Expected 2 unmatched detections, got {len(unmatched_det)}"
        assert len(unmatched_ref) == 3, f"Expected 3 unmatched references, got {len(unmatched_ref)}"

        # Calculate F1
        tp = len(matched_det)
        fp = len(unmatched_det)
        fn = len(unmatched_ref)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        assert f1 == pytest.approx(0.0), f"Expected F1=0.0, got {f1}"

    def test_f1_empty_inputs(self) -> None:
        """F1 should be 0.0 when inputs are empty.

        Tests edge case with no detections and no references.
        """
        det_geoms = []
        ref_geoms = []

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, SPATIAL_TOLERANCE)
        )

        assert len(matched_det) == 0
        assert len(matched_ref) == 0
        assert len(unmatched_det) == 0
        assert len(unmatched_ref) == 0

        # Calculate F1 (0/0 case should yield 0)
        tp = len(matched_det)
        fp = len(unmatched_det)
        fn = len(unmatched_ref)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        assert f1 == pytest.approx(0.0), f"Expected F1=0.0 for empty inputs, got {f1}"

    def test_f1_partial_match(self) -> None:
        """F1 should be approximately 0.571 for partial matching scenario.

        Scenario:
        - 3 references
        - 2 detections: 1 matches a reference, 1 is a false positive

        Expected:
        - TP = 1 (one correct match)
        - FP = 1 (one detection doesn't match any reference)
        - FN = 2 (two references not detected)

        Precision = 1/2 = 0.5
        Recall = 1/3 = 0.333...
        F1 = 2 * (0.5 * 0.333) / (0.5 + 0.333) = 0.4 (approximately 0.4)

        Wait, let me recalculate based on the plan which says P=0.5, R=0.667, F1~0.571
        That would require:
        - TP = 2
        - FP = 2 (precision = 2/4 = 0.5)
        - FN = 1 (recall = 2/3 = 0.667)
        F1 = 2 * 0.5 * 0.667 / (0.5 + 0.667) = 0.571
        """
        # 3 references
        ref_coords = [(500000, 4700000), (500050, 4700050), (500100, 4700100)]

        # 4 detections: 2 match references, 2 are false positives
        det_coords = [
            (500000, 4700000),    # Matches ref 0
            (500050, 4700050),    # Matches ref 1
            (500200, 4700200),    # False positive (too far)
            (500250, 4700250),    # False positive (too far)
        ]

        det_geoms = create_point_gdf(det_coords).geometry.tolist()
        ref_geoms = create_point_gdf(ref_coords).geometry.tolist()

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, SPATIAL_TOLERANCE)
        )

        # Verify matching results
        assert len(matched_det) == 2, f"Expected 2 matched detections, got {len(matched_det)}"
        assert len(matched_ref) == 2, f"Expected 2 matched references, got {len(matched_ref)}"
        assert len(unmatched_det) == 2, f"Expected 2 unmatched detections, got {len(unmatched_det)}"
        assert len(unmatched_ref) == 1, f"Expected 1 unmatched reference, got {len(unmatched_ref)}"

        # Calculate metrics
        tp = len(matched_det)  # 2
        fp = len(unmatched_det)  # 2
        fn = len(unmatched_ref)  # 1

        precision = tp / (tp + fp)  # 2/4 = 0.5
        recall = tp / (tp + fn)  # 2/3 = 0.667
        f1 = 2 * (precision * recall) / (precision + recall)

        assert precision == pytest.approx(0.5, abs=0.001), f"Expected precision=0.5, got {precision}"
        assert recall == pytest.approx(0.667, abs=0.001), f"Expected recall=0.667, got {recall}"
        assert f1 == pytest.approx(0.571, abs=0.01), f"Expected F1~0.571, got {f1}"
