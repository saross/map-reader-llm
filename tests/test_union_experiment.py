"""
Tests for Cross-Modal Union Proposer Experiment
================================================

Tier 1 unit tests using synthetic data. No API, file, or network
dependencies.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import pytest

# Mark all tests in this module as tier1
pytestmark = pytest.mark.tier1


# ---------------------------------------------------------------------------
# Helpers for building synthetic detection dicts
# ---------------------------------------------------------------------------

def make_detection(
    run_id: str,
    source_tile: str,
    minx: float,
    miny: float,
    maxx: float,
    maxy: float,
) -> dict:
    """
    Build a detection dict matching the format produced by
    cluster_detections() from generate_union_candidates.py.

    The 'box' field uses the legacy format (ymin, xmin, ymax, xmax),
    and 'geom_bounds' uses shapely order (minx, miny, maxx, maxy).
    """
    return {
        "box": [miny, minx, maxy, maxx],
        "geom_bounds": (minx, miny, maxx, maxy),
        "label": "mound",
        "source_tile": source_tile,
        "run_id": run_id,
        "original": {
            "type": "Feature",
            "properties": {"source_tile": source_tile},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [minx, miny], [maxx, miny],
                    [maxx, maxy], [minx, maxy],
                    [minx, miny],
                ]],
            },
        },
    }


def make_cluster(detections: list[dict]) -> list[dict]:
    """Wrap detections into a cluster (list of detection dicts)."""
    return detections


# ---------------------------------------------------------------------------
# Import the function under test
# ---------------------------------------------------------------------------

import sys
from pathlib import Path

# Add scripts dir to path for direct import
sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "scripts")
)

from run_union_experiment import (
    build_union_features,
    get_provenance_category,
)


# ---------------------------------------------------------------------------
# Tests: build_union_features
# ---------------------------------------------------------------------------

class TestBuildUnionFeaturesSingleTrack:
    """Test that single-track clusters record correct provenance."""

    def test_image_only_cluster(self):
        """Cluster from image track records source_tracks correctly."""
        det = make_detection(
            "track1-image", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        clusters = [make_cluster([det])]
        features = build_union_features(clusters)

        assert len(features) == 1
        props = features[0]["properties"]
        assert props["source_tracks"] == ["track1-image"]
        assert props["proposer_votes"] == 1
        assert props["cluster_size"] == 1
        assert props["source_tile"] == "tile_A"

    def test_text_only_cluster(self):
        """Cluster from text track records source_tracks correctly."""
        det = make_detection(
            "track2-text", "tile_B", 300.0, 400.0, 310.0, 410.0
        )
        clusters = [make_cluster([det])]
        features = build_union_features(clusters)

        assert len(features) == 1
        props = features[0]["properties"]
        assert props["source_tracks"] == ["track2-text"]
        assert props["proposer_votes"] == 1


class TestBuildUnionFeaturesBothTracks:
    """Test that multi-track clusters record both source tracks."""

    def test_both_tracks_recorded(self):
        """Cluster with detections from both tracks records both."""
        det_img = make_detection(
            "track1-image", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        det_txt = make_detection(
            "track2-text", "tile_A", 102.0, 202.0, 112.0, 212.0
        )
        clusters = [make_cluster([det_img, det_txt])]
        features = build_union_features(clusters)

        assert len(features) == 1
        props = features[0]["properties"]
        assert props["source_tracks"] == ["track1-image", "track2-text"]
        assert props["proposer_votes"] == 2
        assert props["cluster_size"] == 2

    def test_tracks_are_sorted(self):
        """Source tracks list is sorted regardless of input order."""
        det_txt = make_detection(
            "track2-text", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        det_img = make_detection(
            "track1-image", "tile_A", 102.0, 202.0, 112.0, 212.0
        )
        # Text first, then image — should still be sorted
        clusters = [make_cluster([det_txt, det_img])]
        features = build_union_features(clusters)

        assert (
            features[0]["properties"]["source_tracks"]
            == ["track1-image", "track2-text"]
        )


class TestBuildUnionFeaturesAveragedCentroid:
    """Test that multi-member clusters produce averaged geometry."""

    def test_two_member_average(self):
        """Two detections in cluster produce averaged coordinates."""
        det_a = make_detection(
            "track1-image", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        det_b = make_detection(
            "track2-text", "tile_A", 120.0, 220.0, 130.0, 230.0
        )
        clusters = [make_cluster([det_a, det_b])]
        features = build_union_features(clusters)

        geom = features[0]["geometry"]
        coords = geom["coordinates"][0]

        # Expected averages:
        # minx = (100+120)/2 = 110, miny = (200+220)/2 = 210
        # maxx = (110+130)/2 = 120, maxy = (210+230)/2 = 220
        expected_minx, expected_miny = 110.0, 210.0
        expected_maxx, expected_maxy = 120.0, 220.0

        # coords[0] = [minx, miny] (bottom-left corner)
        assert coords[0][0] == pytest.approx(expected_minx)
        assert coords[0][1] == pytest.approx(expected_miny)
        # coords[2] = [maxx, maxy] (top-right corner)
        assert coords[2][0] == pytest.approx(expected_maxx)
        assert coords[2][1] == pytest.approx(expected_maxy)

    def test_single_member_unchanged(self):
        """Single-member cluster produces original coordinates."""
        det = make_detection(
            "track1-image", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        clusters = [make_cluster([det])]
        features = build_union_features(clusters)

        coords = features[0]["geometry"]["coordinates"][0]
        assert coords[0] == [100.0, 200.0]  # minx, miny
        assert coords[2] == [110.0, 210.0]  # maxx, maxy


class TestBuildUnionFeaturesMemberCentroids:
    """Test that member_centroids are stored for evaluation."""

    def test_single_member_has_one_centroid(self):
        """Single-member cluster stores one member centroid."""
        det = make_detection(
            "track1-image", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        clusters = [make_cluster([det])]
        features = build_union_features(clusters)

        centroids = features[0]["properties"]["member_centroids"]
        assert len(centroids) == 1
        # Centroid of (100, 200, 110, 210) = (105, 205)
        assert centroids[0] == pytest.approx([105.0, 205.0])

    def test_two_members_have_two_centroids(self):
        """Two-member cluster stores both original centroids."""
        det_a = make_detection(
            "track1-image", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        det_b = make_detection(
            "track2-text", "tile_A", 120.0, 220.0, 130.0, 230.0
        )
        clusters = [make_cluster([det_a, det_b])]
        features = build_union_features(clusters)

        centroids = features[0]["properties"]["member_centroids"]
        assert len(centroids) == 2
        # Centroid of det_a = (105, 205), det_b = (125, 225)
        assert centroids[0] == pytest.approx([105.0, 205.0])
        assert centroids[1] == pytest.approx([125.0, 225.0])


class TestBuildUnionFeaturesGeojsonStructure:
    """Test that output features are valid GeoJSON."""

    def test_feature_type(self):
        """Each output has correct GeoJSON Feature type."""
        det = make_detection(
            "track1-image", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        clusters = [make_cluster([det])]
        features = build_union_features(clusters)

        assert features[0]["type"] == "Feature"
        assert features[0]["geometry"]["type"] == "Polygon"

    def test_polygon_is_closed(self):
        """Polygon coordinates form a closed ring."""
        det = make_detection(
            "track1-image", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        clusters = [make_cluster([det])]
        features = build_union_features(clusters)

        coords = features[0]["geometry"]["coordinates"][0]
        assert len(coords) == 5
        assert coords[0] == coords[-1]  # closed ring

    def test_empty_clusters(self):
        """Empty cluster list produces empty feature list."""
        features = build_union_features([])
        assert features == []


class TestBuildUnionFeaturesMultipleClusters:
    """Test correct handling of multiple clusters."""

    def test_multiple_clusters_produce_multiple_features(self):
        """Each cluster produces exactly one feature."""
        det_a = make_detection(
            "track1-image", "tile_A", 100.0, 200.0, 110.0, 210.0
        )
        det_b = make_detection(
            "track2-text", "tile_B", 500.0, 600.0, 510.0, 610.0
        )
        clusters = [make_cluster([det_a]), make_cluster([det_b])]
        features = build_union_features(clusters)

        assert len(features) == 2
        assert (
            features[0]["properties"]["source_tile"] == "tile_A"
        )
        assert (
            features[1]["properties"]["source_tile"] == "tile_B"
        )


# ---------------------------------------------------------------------------
# Tests: get_provenance_category
# ---------------------------------------------------------------------------

class TestProvenanceBreakdown:
    """Test classification of candidates into provenance categories."""

    def test_image_only(self):
        assert get_provenance_category(["track1-image"]) == "image-only"

    def test_text_only(self):
        assert get_provenance_category(["track2-text"]) == "text-only"

    def test_both_tracks(self):
        result = get_provenance_category(
            ["track1-image", "track2-text"]
        )
        assert result == "both"

    def test_empty_list(self):
        assert get_provenance_category([]) == "unknown"

    def test_unknown_track(self):
        assert get_provenance_category(["other-track"]) == "unknown"


# ---------------------------------------------------------------------------
# Tests: cluster_detections integration (same-tile constraint)
# ---------------------------------------------------------------------------

class TestSameTileConstraint:
    """
    Verify that detections on different tiles don't merge, even if
    within 20 m distance. Tests the inherited behaviour from
    cluster_detections() in generate_union_candidates.py.
    """

    def test_different_tiles_no_merge(self):
        """Nearby detections on different tiles stay separate."""
        from generate_union_candidates import cluster_detections

        # Two detections 5 m apart but on different tiles
        feat_a = {
            "type": "Feature",
            "properties": {"source_tile": "tile_A"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [100.0, 200.0], [110.0, 200.0],
                    [110.0, 210.0], [100.0, 210.0],
                    [100.0, 200.0],
                ]],
            },
        }
        feat_b = {
            "type": "Feature",
            "properties": {"source_tile": "tile_B"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [103.0, 203.0], [113.0, 203.0],
                    [113.0, 213.0], [103.0, 213.0],
                    [103.0, 203.0],
                ]],
            },
        }

        all_dets = {
            "track1-image": [feat_a],
            "track2-text": [feat_b],
        }
        clusters = cluster_detections(all_dets)
        assert len(clusters) == 2  # separate clusters

    def test_same_tile_merges(self):
        """Nearby detections on the same tile do merge."""
        from generate_union_candidates import cluster_detections

        feat_a = {
            "type": "Feature",
            "properties": {"source_tile": "tile_A"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [100.0, 200.0], [110.0, 200.0],
                    [110.0, 210.0], [100.0, 210.0],
                    [100.0, 200.0],
                ]],
            },
        }
        feat_b = {
            "type": "Feature",
            "properties": {"source_tile": "tile_A"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [103.0, 203.0], [113.0, 203.0],
                    [113.0, 213.0], [103.0, 213.0],
                    [103.0, 203.0],
                ]],
            },
        }

        all_dets = {
            "track1-image": [feat_a],
            "track2-text": [feat_b],
        }
        clusters = cluster_detections(all_dets)
        assert len(clusters) == 1  # merged


# ---------------------------------------------------------------------------
# Tests: deduplication count
# ---------------------------------------------------------------------------

class TestDedupCount:
    """Verify deduplication produces expected cluster count."""

    def test_known_overlap_reduction(self):
        """
        Synthetic scenario: 6 detections (3 per track), 2 pairs overlap
        → expect 4 clusters.
        """
        from generate_union_candidates import cluster_detections

        # Overlapping pair 1 (tile_A, ~5 m apart)
        feat_a1 = {
            "type": "Feature",
            "properties": {"source_tile": "tile_A"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [100, 200], [110, 200],
                    [110, 210], [100, 210], [100, 200],
                ]],
            },
        }
        feat_b1 = {
            "type": "Feature",
            "properties": {"source_tile": "tile_A"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [103, 203], [113, 203],
                    [113, 213], [103, 213], [103, 203],
                ]],
            },
        }
        # Overlapping pair 2 (tile_A, ~7 m apart)
        feat_a2 = {
            "type": "Feature",
            "properties": {"source_tile": "tile_A"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [500, 600], [510, 600],
                    [510, 610], [500, 610], [500, 600],
                ]],
            },
        }
        feat_b2 = {
            "type": "Feature",
            "properties": {"source_tile": "tile_A"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [505, 605], [515, 605],
                    [515, 615], [505, 615], [505, 605],
                ]],
            },
        }
        # Non-overlapping (tile_B, far apart)
        feat_a3 = {
            "type": "Feature",
            "properties": {"source_tile": "tile_B"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [900, 900], [910, 900],
                    [910, 910], [900, 910], [900, 900],
                ]],
            },
        }
        feat_b3 = {
            "type": "Feature",
            "properties": {"source_tile": "tile_B"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [1500, 1500], [1510, 1500],
                    [1510, 1510], [1500, 1510], [1500, 1500],
                ]],
            },
        }

        all_dets = {
            "track1-image": [feat_a1, feat_a2, feat_a3],
            "track2-text": [feat_b1, feat_b2, feat_b3],
        }
        clusters = cluster_detections(all_dets)

        # 6 detections → 2 merged pairs + 2 singletons = 4 clusters
        assert len(clusters) == 4

        # Verify merged clusters have 2 members each
        merged = [c for c in clusters if len(c) == 2]
        singletons = [c for c in clusters if len(c) == 1]
        assert len(merged) == 2
        assert len(singletons) == 2


# ---------------------------------------------------------------------------
# Tests: generate_report
# ---------------------------------------------------------------------------

class TestGenerateReport:
    """Test report generation produces valid Markdown."""

    def test_report_contains_comparison_table(self):
        """Report includes the comparison table header."""
        from run_union_experiment import generate_report

        results = {
            "unfiltered": {
                "f1": 0.5, "precision": 0.4, "recall": 0.7, "n": 187,
            },
            "optimal_result": {
                "f1": 0.82, "precision": 0.80, "recall": 0.84,
                "n_kept": 100,
            },
            "optimal_threshold": 0.15,
            "threshold_results": [],
            "provenance_breakdown": {},
            "n_candidates": 187,
            "n_references": 97,
        }
        report = generate_report(results)

        assert "## Comparison Table" in report
        assert "Union + adversarial" in report
        assert "0.820" in report  # optimal F1

    def test_report_contains_baselines(self):
        """Report includes single-track baseline rows."""
        from run_union_experiment import generate_report

        results = {
            "unfiltered": {"f1": 0.5, "precision": 0.4, "recall": 0.7,
                           "n": 187},
            "optimal_result": {"f1": 0.8, "precision": 0.8,
                               "recall": 0.8, "n_kept": 100},
            "optimal_threshold": 0.15,
            "threshold_results": [],
            "provenance_breakdown": {},
            "n_candidates": 187,
            "n_references": 97,
        }
        report = generate_report(results)

        assert "Image single-track" in report
        assert "Text single-track" in report
        assert "0.711" in report  # image baseline F1
        assert "0.796" in report  # text baseline F1
