"""
Tests for merge_passes.py voting algorithm.

Tier 1 unit tests for the consensus voting functions that implement
preregistration Section 8.5. Uses synthetic detections to verify correct
deduplication, clustering, and vote counting.
"""

import sys
from pathlib import Path

import pytest
from shapely.geometry import box, mapping

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.merge_passes import (
    apply_threshold,
    centroid_from_geometry,
    cluster_across_passes,
    deduplicate_within_pass,
    euclidean_distance,
)


def make_point_feature(
    x: float, y: float, subtype: str = "mound", source_tile: str = "tile_001"
) -> dict:
    """Create a GeoJSON Point feature for testing."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [x, y]},
        "properties": {
            "subtype": subtype,
            "source_tile": source_tile,
        },
    }


def make_box_feature(
    x: float, y: float, size: float = 10.0, subtype: str = "mound", source_tile: str = "tile_001"
) -> dict:
    """Create a GeoJSON box feature for testing (simulates detection bounding box)."""
    geom = box(x - size / 2, y - size / 2, x + size / 2, y + size / 2)
    return {
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": {
            "subtype": subtype,
            "source_tile": source_tile,
        },
    }


@pytest.mark.tier1
class TestCentroidFromGeometry:
    """Tests for centroid extraction from GeoJSON geometries."""

    def test_point_geometry(self) -> None:
        """Centroid of a Point should be the point itself."""
        geom = {"type": "Point", "coordinates": [500000.0, 4700000.0]}
        x, y = centroid_from_geometry(geom)

        assert x == 500000.0
        assert y == 4700000.0

    def test_polygon_geometry(self) -> None:
        """Centroid of a square polygon should be its centre."""
        # 100m × 100m square centred at (500000, 4700000)
        geom = {
            "type": "Polygon",
            "coordinates": [[
                [499950, 4699950],
                [500050, 4699950],
                [500050, 4700050],
                [499950, 4700050],
                [499950, 4699950],
            ]],
        }
        x, y = centroid_from_geometry(geom)

        assert abs(x - 500000.0) < 0.01
        assert abs(y - 4700000.0) < 0.01


@pytest.mark.tier1
class TestEuclideanDistance:
    """Tests for distance calculation."""

    def test_zero_distance(self) -> None:
        """Same point should have zero distance."""
        p1 = (500000.0, 4700000.0)
        p2 = (500000.0, 4700000.0)

        assert euclidean_distance(p1, p2) == 0.0

    def test_horizontal_distance(self) -> None:
        """Horizontal distance should match x difference."""
        p1 = (500000.0, 4700000.0)
        p2 = (500020.0, 4700000.0)

        assert euclidean_distance(p1, p2) == 20.0

    def test_diagonal_distance(self) -> None:
        """Diagonal distance follows Pythagorean theorem."""
        p1 = (0.0, 0.0)
        p2 = (3.0, 4.0)

        assert euclidean_distance(p1, p2) == 5.0


@pytest.mark.tier1
class TestDeduplicateWithinPass:
    """Tests for within-pass deduplication (preregistration Section 8.5 Step 1)."""

    def test_empty_input(self) -> None:
        """Empty input should return empty output."""
        result = deduplicate_within_pass([])
        assert result == []

    def test_single_detection(self) -> None:
        """Single detection should pass through unchanged."""
        features = [make_point_feature(500000, 4700000)]
        result = deduplicate_within_pass(features)

        assert len(result) == 1
        assert result[0]["centroid"] == (500000, 4700000)

    def test_distant_detections_preserved(self) -> None:
        """Detections >20m apart should both be preserved."""
        # Two detections 50m apart
        features = [
            make_point_feature(500000, 4700000),
            make_point_feature(500050, 4700000),
        ]
        result = deduplicate_within_pass(features)

        assert len(result) == 2, "Distant detections should not be merged"

    def test_close_detections_merged(self) -> None:
        """Detections ≤20m apart should be merged.

        Verifies preregistration Section 8.5 Step 1: within-pass deduplication
        prevents overlapping tiles from contributing multiple votes.
        """
        # Two detections 15m apart (within 20m threshold)
        features = [
            make_point_feature(500000, 4700000, source_tile="tile_001"),
            make_point_feature(500015, 4700000, source_tile="tile_002"),
        ]
        result = deduplicate_within_pass(features)

        assert len(result) == 1, "Close detections should be merged"

        # Centroid should be average
        expected_x = (500000 + 500015) / 2
        assert abs(result[0]["centroid"][0] - expected_x) < 0.01

        # Both source tiles should be recorded
        assert len(result[0]["source_tiles"]) == 2

    def test_threshold_boundary(self) -> None:
        """Detections exactly at threshold should be merged."""
        # Two detections exactly 20m apart
        features = [
            make_point_feature(500000, 4700000),
            make_point_feature(500020, 4700000),
        ]
        result = deduplicate_within_pass(features)

        assert len(result) == 1, "Detections at threshold should be merged"

    def test_majority_label(self) -> None:
        """Merged cluster should use majority label."""
        features = [
            make_point_feature(500000, 4700000, subtype="burial_mound"),
            make_point_feature(500010, 4700000, subtype="burial_mound"),
            make_point_feature(500005, 4700000, subtype="settlement_mound"),
        ]
        result = deduplicate_within_pass(features)

        assert len(result) == 1
        assert result[0]["label"] == "burial_mound", "Should use majority label"


@pytest.mark.tier1
class TestClusterAcrossPasses:
    """Tests for cross-pass clustering and vote counting (preregistration Section 8.5 Steps 2-5)."""

    def test_empty_input(self) -> None:
        """Empty input should return empty output."""
        result = cluster_across_passes({})
        assert result == []

    def test_single_pass_single_detection(self) -> None:
        """Single detection from one pass should have vote_count=1."""
        pass_detections = {
            "pass_01": [{"centroid": (500000, 4700000), "label": "mound"}],
        }
        result = cluster_across_passes(pass_detections)

        assert len(result) == 1
        assert result[0]["vote_count"] == 1
        assert result[0]["contributing_passes"] == ["pass_01"]

    def test_same_location_multiple_passes(self) -> None:
        """Same location detected in multiple passes should accumulate votes.

        Verifies preregistration Section 8.5: "Each mound detected by n (out of
        N) independent passes receives a vote count of n."
        """
        # Same location detected in 3 out of 5 passes
        pass_detections = {
            "pass_01": [{"centroid": (500000, 4700000), "label": "mound"}],
            "pass_02": [{"centroid": (500005, 4700005), "label": "mound"}],  # Within 20m
            "pass_03": [{"centroid": (500010, 4700000), "label": "mound"}],  # Within 20m
            # pass_04: no detection
            # pass_05: no detection
        }
        result = cluster_across_passes(pass_detections)

        assert len(result) == 1, "Should cluster into single detection"
        assert result[0]["vote_count"] == 3, "Should count 3 contributing passes"
        assert sorted(result[0]["contributing_passes"]) == ["pass_01", "pass_02", "pass_03"]

    def test_different_locations_separate_clusters(self) -> None:
        """Detections >20m apart should form separate clusters."""
        pass_detections = {
            "pass_01": [
                {"centroid": (500000, 4700000), "label": "mound"},
                {"centroid": (500100, 4700000), "label": "mound"},  # 100m away
            ],
        }
        result = cluster_across_passes(pass_detections)

        assert len(result) == 2, "Distant detections should form separate clusters"
        assert all(c["vote_count"] == 1 for c in result)

    def test_same_pass_multiple_detections_same_cluster(self) -> None:
        """Multiple detections from same pass in same cluster count as 1 vote.

        Important: If deduplicate_within_pass wasn't run, this tests that
        cluster_across_passes doesn't double-count.
        """
        pass_detections = {
            "pass_01": [
                {"centroid": (500000, 4700000), "label": "mound"},
                {"centroid": (500005, 4700000), "label": "mound"},  # Same pass, within 20m
            ],
        }
        result = cluster_across_passes(pass_detections)

        # Should form one cluster with vote_count=1 (same pass)
        assert len(result) == 1
        assert result[0]["vote_count"] == 1, "Same pass should contribute only 1 vote"
        assert result[0]["cluster_size"] == 2, "Both detections should be in cluster"


@pytest.mark.tier1
class TestApplyThreshold:
    """Tests for vote threshold application (preregistration Section 8.5 Step 6)."""

    def test_threshold_filters_correctly(self) -> None:
        """Clusters below threshold should be filtered out."""
        clusters = [
            {"centroid": (500000, 4700000), "label": "mound", "vote_count": 1,
             "contributing_passes": ["pass_01"], "source_tiles": [], "cluster_size": 1},
            {"centroid": (500100, 4700000), "label": "mound", "vote_count": 3,
             "contributing_passes": ["pass_01", "pass_02", "pass_03"],
             "source_tiles": [], "cluster_size": 3},
            {"centroid": (500200, 4700000), "label": "mound", "vote_count": 5,
             "contributing_passes": ["pass_01", "pass_02", "pass_03", "pass_04", "pass_05"],
             "source_tiles": [], "cluster_size": 5},
        ]

        # Threshold 3: should keep vote_count >= 3
        result = apply_threshold(clusters, threshold=3, total_passes=5)

        assert len(result["features"]) == 2, "Should retain only clusters with vote_count >= 3"

    def test_confidence_calculation(self) -> None:
        """Confidence should equal vote_count / total_passes.

        Verifies preregistration Section 8.5: confidence = votes/N
        """
        clusters = [
            {"centroid": (500000, 4700000), "label": "mound", "vote_count": 3,
             "contributing_passes": ["pass_01", "pass_02", "pass_03"],
             "source_tiles": [], "cluster_size": 3},
        ]

        result = apply_threshold(clusters, threshold=1, total_passes=5)

        assert len(result["features"]) == 1
        props = result["features"][0]["properties"]
        assert props["confidence"] == 0.6, "Confidence should be 3/5 = 0.6"
        assert props["vote_count"] == 3
        assert props["total_passes"] == 5

    def test_output_geometry_is_point(self) -> None:
        """Output should have Point geometry reprojected to EPSG:4326.

        Centroids are stored in EPSG:32635 (UTM) internally but
        reprojected to EPSG:4326 (lon/lat) for GeoJSON spec compliance.
        """
        clusters = [
            {"centroid": (500123.45, 4700678.90), "label": "mound", "vote_count": 3,
             "contributing_passes": ["pass_01", "pass_02", "pass_03"],
             "source_tiles": [], "cluster_size": 3},
        ]

        result = apply_threshold(clusters, threshold=1, total_passes=5)

        geom = result["features"][0]["geometry"]
        assert geom["type"] == "Point"
        # Coordinates should be in EPSG:4326 (lon/lat), not UTM
        lon, lat = geom["coordinates"]
        assert -180 <= lon <= 180, f"Longitude {lon} out of range"
        assert -90 <= lat <= 90, f"Latitude {lat} out of range"
        # Verify approximate location (Bulgaria, ~42°N, ~27°E)
        assert 20 < lon < 30, f"Expected longitude near Bulgaria, got {lon}"
        assert 40 < lat < 45, f"Expected latitude near Bulgaria, got {lat}"


@pytest.mark.tier1
class TestVotingIntegration:
    """Integration tests for the complete voting pipeline."""

    def test_full_pipeline_n5_t3(self) -> None:
        """Test N=5 passes with T≥3 threshold (preregistration default).

        Simulates 5 independent passes detecting the same mound with varying
        success, then applies majority voting.
        """
        # Simulate 5 passes with 3 detecting the mound
        pass_detections = {
            "pass_01": [
                {"centroid": (500000, 4700000), "label": "burial_mound",
                 "source_tiles": ["t1"]}],
            "pass_02": [],  # Missed
            "pass_03": [
                {"centroid": (500008, 4700005), "label": "burial_mound",
                 "source_tiles": ["t1"]}],
            "pass_04": [
                {"centroid": (500003, 4700002), "label": "burial_mound",
                 "source_tiles": ["t1"]}],
            "pass_05": [],  # Missed
        }

        # Step 1: Deduplicate within each pass (trivial here - one detection per pass max)
        deduped = {}
        for pass_id, features in pass_detections.items():
            if features:
                deduped[pass_id] = features  # Already deduplicated

        # Step 2-5: Cluster and count votes
        clusters = cluster_across_passes(deduped)

        assert len(clusters) == 1, "Should form single cluster"
        assert clusters[0]["vote_count"] == 3, "Should have 3 votes"

        # Step 6: Apply T≥3 threshold
        result = apply_threshold(clusters, threshold=3, total_passes=5)

        assert len(result["features"]) == 1, "Should retain detection with T≥3"
        assert result["features"][0]["properties"]["confidence"] == 0.6

    def test_false_positive_rejected(self) -> None:
        """Spurious detection appearing in only 1 pass should be filtered at T≥3."""
        pass_detections = {
            "pass_01": [{"centroid": (500000, 4700000), "label": "mound", "source_tiles": ["t1"]}],
            "pass_02": [],
            "pass_03": [],
            "pass_04": [],
            "pass_05": [],
        }

        deduped = {"pass_01": pass_detections["pass_01"]}
        clusters = cluster_across_passes(deduped)

        assert len(clusters) == 1
        assert clusters[0]["vote_count"] == 1

        # T≥3 should filter it out
        result = apply_threshold(clusters, threshold=3, total_passes=5)
        assert len(result["features"]) == 0, "Single-pass detection should be filtered"

    def test_unanimous_detection(self) -> None:
        """Detection in all passes should have confidence=1.0."""
        pass_detections = {
            f"pass_{i:02d}": [
                {"centroid": (500000 + i, 4700000),
                 "label": "mound", "source_tiles": []}]
            for i in range(1, 6)
        }

        clusters = cluster_across_passes(pass_detections)
        result = apply_threshold(clusters, threshold=1, total_passes=5)

        assert len(result["features"]) == 1
        assert result["features"][0]["properties"]["confidence"] == 1.0
        assert result["features"][0]["properties"]["vote_count"] == 5
