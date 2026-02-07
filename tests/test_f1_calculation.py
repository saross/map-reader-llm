"""
Tests for F1 score calculation functions.

Tier 1 unit tests for the core metrics calculation in lib_advanced_metrics.py.
Uses synthetic GeoDataFrames to verify correct precision, recall, and F1
calculation under controlled conditions.
"""

import geopandas as gpd
import pytest
from shapely.geometry import Point

from scripts.lib_advanced_metrics import match_detections_to_references

# Standard spatial tolerance from preregistration (metres)
SPATIAL_TOLERANCE = 20


def _make_point_gdf(
    coords: list[tuple[float, float]],
    crs: str = "EPSG:32635",
) -> gpd.GeoDataFrame:
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


def _compute_f1(matched_det: list, unmatched_det: list, unmatched_ref: list) -> float:
    """Compute F1 score from matching results.

    Centralises the precision/recall/F1 formula used across multiple tests
    to avoid repetition.

    Args:
        matched_det: Matched detection geometries (true positives).
        unmatched_det: Unmatched detection geometries (false positives).
        unmatched_ref: Unmatched reference geometries (false negatives).

    Returns:
        F1 score in [0, 1], or 0 when undefined.
    """
    tp = len(matched_det)
    fp = len(unmatched_det)
    fn = len(unmatched_ref)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    if (precision + recall) == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


@pytest.mark.tier1
class TestMatchDetectionsToReferences:
    """Tests for the Hungarian algorithm matching function."""

    def test_f1_perfect_match(self) -> None:
        """F1 should be 1.0 when detections exactly match references.

        3 detections at the same locations as 3 references.
        All should match (3 TP, 0 FP, 0 FN) -> F1 = 1.0.
        """
        ref_coords = [(500000, 4700000), (500050, 4700050), (500100, 4700100)]
        det_coords = [(500000, 4700000), (500050, 4700050), (500100, 4700100)]

        det_geoms = _make_point_gdf(det_coords).geometry.tolist()
        ref_geoms = _make_point_gdf(ref_coords).geometry.tolist()

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, SPATIAL_TOLERANCE)
        )

        assert len(matched_det) == 3, f"Expected 3 matched detections, got {len(matched_det)}"
        assert len(matched_ref) == 3, f"Expected 3 matched references, got {len(matched_ref)}"
        assert len(unmatched_det) == 0, f"Expected 0 unmatched detections, got {len(unmatched_det)}"
        assert len(unmatched_ref) == 0, f"Expected 0 unmatched references, got {len(unmatched_ref)}"

        f1 = _compute_f1(matched_det, unmatched_det, unmatched_ref)
        assert f1 == pytest.approx(1.0), f"Expected F1=1.0, got {f1}"

    def test_f1_no_matches(self) -> None:
        """F1 should be 0.0 when all detections are too far from references.

        Detections >20m away from all references.
        None should match (0 TP, 2 FP, 3 FN) -> F1 = 0.0.
        """
        ref_coords = [(500000, 4700000), (500050, 4700050), (500100, 4700100)]
        det_coords = [(500200, 4700200), (500250, 4700250)]

        det_geoms = _make_point_gdf(det_coords).geometry.tolist()
        ref_geoms = _make_point_gdf(ref_coords).geometry.tolist()

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, SPATIAL_TOLERANCE)
        )

        assert len(matched_det) == 0, f"Expected 0 matched detections, got {len(matched_det)}"
        assert len(matched_ref) == 0, f"Expected 0 matched references, got {len(matched_ref)}"
        assert len(unmatched_det) == 2, f"Expected 2 unmatched detections, got {len(unmatched_det)}"
        assert len(unmatched_ref) == 3, f"Expected 3 unmatched references, got {len(unmatched_ref)}"

        f1 = _compute_f1(matched_det, unmatched_det, unmatched_ref)
        assert f1 == pytest.approx(0.0), f"Expected F1=0.0, got {f1}"

    def test_f1_empty_inputs(self) -> None:
        """F1 should be 0.0 when inputs are empty (0/0 case)."""
        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references([], [], SPATIAL_TOLERANCE)
        )

        assert len(matched_det) == 0
        assert len(matched_ref) == 0
        assert len(unmatched_det) == 0
        assert len(unmatched_ref) == 0

        f1 = _compute_f1(matched_det, unmatched_det, unmatched_ref)
        assert f1 == pytest.approx(0.0), f"Expected F1=0.0 for empty inputs, got {f1}"

    def test_f1_partial_match(self) -> None:
        """F1 should be ~0.571 for a partial matching scenario.

        Scenario: 3 references, 4 detections (2 match, 2 false positives).
        TP=2, FP=2, FN=1 -> P=0.5, R=0.667, F1~0.571.
        """
        ref_coords = [(500000, 4700000), (500050, 4700050), (500100, 4700100)]
        det_coords = [
            (500000, 4700000),    # Matches ref 0
            (500050, 4700050),    # Matches ref 1
            (500200, 4700200),    # False positive (too far)
            (500250, 4700250),    # False positive (too far)
        ]

        det_geoms = _make_point_gdf(det_coords).geometry.tolist()
        ref_geoms = _make_point_gdf(ref_coords).geometry.tolist()

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(det_geoms, ref_geoms, SPATIAL_TOLERANCE)
        )

        assert len(matched_det) == 2, f"Expected 2 matched detections, got {len(matched_det)}"
        assert len(matched_ref) == 2, f"Expected 2 matched references, got {len(matched_ref)}"
        assert len(unmatched_det) == 2, f"Expected 2 unmatched detections, got {len(unmatched_det)}"
        assert len(unmatched_ref) == 1, f"Expected 1 unmatched reference, got {len(unmatched_ref)}"

        tp = len(matched_det)
        fp = len(unmatched_det)
        fn = len(unmatched_ref)

        precision = tp / (tp + fp)  # 2/4 = 0.5
        recall = tp / (tp + fn)  # 2/3 = 0.667
        f1 = _compute_f1(matched_det, unmatched_det, unmatched_ref)

        assert precision == pytest.approx(0.5, abs=0.001), f"Expected precision=0.5, got {precision}"
        assert recall == pytest.approx(0.667, abs=0.001), f"Expected recall=0.667, got {recall}"
        assert f1 == pytest.approx(0.571, abs=0.01), f"Expected F1~0.571, got {f1}"
