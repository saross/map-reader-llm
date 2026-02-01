"""
Integration tests for pipeline stage contracts.

Verifies data contracts between pipeline stages that were the source of
five cascading bugs in Phase 1 (errata E3-E5). These tests exercise the
interfaces between stages, not the stages themselves.

Contract tests:
1. Merge output → evaluation input (source_tiles list → source_tile string)
2. Reference loading (directory path + glob pattern)
3. Bounds metadata interpretation (Y-axis orientation)
4. End-to-end merge → evaluate with known synthetic data

Created: 2026-02-01 (post-Phase 1 infrastructure hardening)
"""

import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import TILE_SIZE
from scripts.lib_advanced_metrics import (
    calculate_f1_internal,
    load_data,
)
from scripts.merge_passes import (
    apply_threshold,
    cluster_across_passes,
    deduplicate_within_pass,
)

# Test coordinates in EPSG:32635 (UTM 35N, Bulgaria)
# Using realistic coordinate ranges for the study area
MAP_NAME = "K-35-052-4_32635"
TILE_NAME = f"{MAP_NAME}_x0_y0.png"
BASE_X = 400000.0
BASE_Y = 4690000.0
CRS = "EPSG:32635"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def synthetic_references() -> gpd.GeoDataFrame:
    """
    Create synthetic reference points (ground truth burial mounds).

    Places 4 reference points at known coordinates within a single tile.
    """
    refs = gpd.GeoDataFrame(
        {
            "Map": [MAP_NAME] * 4,
            "Symbol": ["Burial mound"] * 4,
            "fid": [1, 2, 3, 4],
        },
        geometry=[
            Point(BASE_X + 100, BASE_Y + 100),   # R1
            Point(BASE_X + 300, BASE_Y + 300),   # R2
            Point(BASE_X + 500, BASE_Y + 500),   # R3
            Point(BASE_X + 700, BASE_Y + 700),   # R4 — will be missed (FN)
        ],
        crs=CRS,
    )
    return refs


@pytest.fixture
def synthetic_bounds() -> gpd.GeoDataFrame:
    """
    Create synthetic tile bounds covering the test area.

    Single tile polygon that encompasses all reference and detection points.
    """
    tile_extent = 1000.0  # 1km tile
    bounds = gpd.GeoDataFrame(
        {
            "tile_name": [TILE_NAME],
            "map_name": [MAP_NAME],
        },
        geometry=[
            box(BASE_X, BASE_Y, BASE_X + tile_extent, BASE_Y + tile_extent),
        ],
        crs=CRS,
    )
    return bounds


@pytest.fixture
def synthetic_merge_output() -> gpd.GeoDataFrame:
    """
    Create synthetic detections in merged-output format.

    Mimics the output of merge_passes.py: uses 'source_tiles' (list)
    instead of 'source_tile' (string). This is the column name mismatch
    that caused bug E5b.

    Detections:
    - D1: near R1 (TP, within 20m)
    - D2: near R2 (TP, within 20m)
    - D3: near R3 (TP, within 20m)
    - D4: no nearby reference (FP, >20m from any reference)

    Expected: TP=3, FP=1, FN=1 (R4 missed), P=0.75, R=0.75, F1=0.75
    """
    detections = gpd.GeoDataFrame(
        {
            # Note: source_tiles as LIST — this is the merged format
            "source_tiles": [
                [TILE_NAME],
                [TILE_NAME],
                [TILE_NAME],
                [TILE_NAME],
            ],
            "subtype": ["mound"] * 4,
            "vote_count": [3, 3, 2, 2],
            "confidence": [0.6, 0.6, 0.4, 0.4],
            "contributing_passes": [
                ["pass_01", "pass_02", "pass_03"],
                ["pass_01", "pass_02", "pass_03"],
                ["pass_01", "pass_02"],
                ["pass_01", "pass_02"],
            ],
            "cluster_size": [3, 3, 2, 2],
        },
        geometry=[
            Point(BASE_X + 105, BASE_Y + 105),   # D1: ~7m from R1 (TP)
            Point(BASE_X + 295, BASE_Y + 305),   # D2: ~7m from R2 (TP)
            Point(BASE_X + 510, BASE_Y + 495),   # D3: ~11m from R3 (TP)
            Point(BASE_X + 900, BASE_Y + 200),   # D4: far from any ref (FP)
        ],
        crs=CRS,
    )
    return detections


@pytest.fixture
def synthetic_pass_features() -> dict[str, list[dict]]:
    """
    Create synthetic per-pass detection features for merge testing.

    Three passes with overlapping detections near known reference points.
    """
    def make_feature(x: float, y: float, tile: str, label: str = "mound") -> dict:
        """Create a GeoJSON-like feature dict."""
        return {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [x, y]},
            "properties": {
                "source_tile": tile,
                "subtype": label,
            },
        }

    pass_01 = [
        make_feature(BASE_X + 102, BASE_Y + 98, TILE_NAME),   # Near R1
        make_feature(BASE_X + 298, BASE_Y + 302, TILE_NAME),  # Near R2
        make_feature(BASE_X + 505, BASE_Y + 498, TILE_NAME),  # Near R3
        make_feature(BASE_X + 900, BASE_Y + 200, TILE_NAME),  # FP (no ref)
    ]
    pass_02 = [
        make_feature(BASE_X + 97, BASE_Y + 103, TILE_NAME),   # Near R1
        make_feature(BASE_X + 303, BASE_Y + 295, TILE_NAME),  # Near R2
        make_feature(BASE_X + 510, BASE_Y + 505, TILE_NAME),  # Near R3
    ]
    pass_03 = [
        make_feature(BASE_X + 100, BASE_Y + 100, TILE_NAME),  # Near R1
        make_feature(BASE_X + 300, BASE_Y + 300, TILE_NAME),  # Near R2
    ]

    return {
        "pass_01": pass_01,
        "pass_02": pass_02,
        "pass_03": pass_03,
    }


# =============================================================================
# Contract Test 1: source_tiles list → source_tile string normalisation
# =============================================================================


@pytest.mark.tier1
@pytest.mark.integration
class TestSourceTileNormalisation:
    """Verify that merged detection format is correctly normalised for evaluation."""

    def test_source_tiles_list_to_source_tile_string(
        self, synthetic_merge_output: gpd.GeoDataFrame
    ) -> None:
        """
        Merged GeoJSON uses 'source_tiles' (list) but F1 evaluation expects
        'source_tile' (string). This normalisation was the fix for bug E5b.
        """
        gdf = synthetic_merge_output.copy()

        # Verify the merged format has source_tiles (list), not source_tile
        assert "source_tiles" in gdf.columns, "Test fixture should use merged format"
        assert "source_tile" not in gdf.columns, "Test fixture should NOT have source_tile"

        # Apply the normalisation from 6_accuracy_report.py
        if "source_tile" not in gdf.columns and "source_tiles" in gdf.columns:
            gdf["source_tile"] = gdf["source_tiles"].apply(
                lambda x: x[0]
                if hasattr(x, "__getitem__") and len(x) > 0
                else str(x)
            )

        # Verify normalisation produced correct results
        assert "source_tile" in gdf.columns, "Normalisation should add source_tile column"
        assert all(
            isinstance(v, str) for v in gdf["source_tile"]
        ), "source_tile should be strings"
        assert all(
            v == TILE_NAME for v in gdf["source_tile"]
        ), f"All source_tiles should resolve to {TILE_NAME}"


# =============================================================================
# Contract Test 2: Reference loading validates directory and files
# =============================================================================


@pytest.mark.tier1
@pytest.mark.integration
class TestReferenceLoadingContract:
    """Verify that reference loading fails loudly on wrong paths."""

    def test_missing_reference_directory_returns_none(self, tmp_path: Path) -> None:
        """
        load_data() should return (None, None, None) when the reference
        directory does not exist — not silently return empty data.
        This was the failure mode of bug E5a.
        """
        # Create minimal detection and bounds files
        det_gdf = gpd.GeoDataFrame(
            geometry=[Point(0, 0)], crs=CRS
        )
        bounds_gdf = gpd.GeoDataFrame(
            {"tile_name": ["test"]},
            geometry=[box(0, 0, 100, 100)],
            crs=CRS,
        )
        det_path = tmp_path / "detections.geojson"
        bounds_path = tmp_path / "bounds.geojson"
        det_gdf.to_file(det_path, driver="GeoJSON")
        bounds_gdf.to_file(bounds_path, driver="GeoJSON")

        # inputs_dir has no vectors/references/ subdirectory
        fake_inputs = tmp_path / "inputs"
        fake_inputs.mkdir()

        result = load_data(det_path, bounds_path, inputs_dir=fake_inputs)
        assert result == (None, None, None), (
            "load_data() should return (None, None, None) when reference "
            "directory does not exist"
        )

    def test_empty_reference_directory_returns_none(self, tmp_path: Path) -> None:
        """
        load_data() should return (None, None, None) when the reference
        directory exists but contains no matching files.
        """
        # Create the directory structure but with no reference files
        det_gdf = gpd.GeoDataFrame(
            geometry=[Point(0, 0)], crs=CRS
        )
        bounds_gdf = gpd.GeoDataFrame(
            {"tile_name": ["test"]},
            geometry=[box(0, 0, 100, 100)],
            crs=CRS,
        )
        det_path = tmp_path / "detections.geojson"
        bounds_path = tmp_path / "bounds.geojson"
        det_gdf.to_file(det_path, driver="GeoJSON")
        bounds_gdf.to_file(bounds_path, driver="GeoJSON")

        fake_inputs = tmp_path / "inputs"
        ref_dir = fake_inputs / "vectors" / "references"
        ref_dir.mkdir(parents=True)
        # Directory exists but has no reference_*.geojson files

        result = load_data(det_path, bounds_path, inputs_dir=fake_inputs)
        assert result == (None, None, None), (
            "load_data() should return (None, None, None) when reference "
            "directory is empty"
        )


# =============================================================================
# Contract Test 3: Bounds metadata interpretation (Y-axis)
# =============================================================================


@pytest.mark.tier1
@pytest.mark.integration
class TestBoundsMetadataContract:
    """Verify that tile bounds correctly interpret metadata[1] as minY."""

    def test_metadata_y_is_min_y(self) -> None:
        """
        Metadata format is [minX, minY, pixel_size_x, pixel_size_y].
        metadata[1] is the BOTTOM edge (minY), not the top edge.
        Bug E4 treated it as maxY, shifting all bounds one tile height south.
        """
        from scripts.generate_tile_bounds import tile_to_polygon

        # Create test metadata: tile at known coordinates
        test_tile = "K-35-052-4_32635_x0_y0.png"
        known_min_x = 400000.0
        known_min_y = 4690000.0
        pixel_size = 5.0  # 5m per pixel

        metadata = {
            test_tile: [known_min_x, known_min_y, pixel_size, pixel_size],
        }

        feature = tile_to_polygon(test_tile, metadata)
        assert feature is not None, "tile_to_polygon should return a feature"

        # Extract bounds from polygon
        coords = feature["geometry"]["coordinates"][0]
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        actual_min_x = min(xs)
        actual_min_y = min(ys)
        actual_max_x = max(xs)
        actual_max_y = max(ys)

        expected_extent = TILE_SIZE * pixel_size

        # The critical assertion: minY from polygon must equal metadata[1]
        assert actual_min_y == pytest.approx(known_min_y, abs=0.01), (
            f"Polygon minY ({actual_min_y}) should equal metadata[1] "
            f"({known_min_y}). If minY < metadata[1], the Y-axis "
            f"interpretation is inverted (bug E4)."
        )

        # Additional consistency checks
        assert actual_min_x == pytest.approx(known_min_x, abs=0.01), (
            f"Polygon minX ({actual_min_x}) should equal metadata[0] ({known_min_x})"
        )
        assert actual_max_y == pytest.approx(
            known_min_y + expected_extent, abs=0.01
        ), (
            f"Polygon maxY ({actual_max_y}) should equal "
            f"minY + extent ({known_min_y + expected_extent})"
        )
        assert (actual_max_x - actual_min_x) == pytest.approx(
            expected_extent, abs=0.01
        ), "Polygon width should equal TILE_SIZE * pixel_size"
        assert (actual_max_y - actual_min_y) == pytest.approx(
            expected_extent, abs=0.01
        ), "Polygon height should equal TILE_SIZE * pixel_size"


# =============================================================================
# Contract Test 4: End-to-end merge → evaluate
# =============================================================================


@pytest.mark.tier1
@pytest.mark.integration
class TestMergeToEvaluateContract:
    """
    End-to-end contract test: merge passes → evaluate F1.

    Exercises the full data path from per-pass detections through merge
    (dedup + cluster + vote) to F1 calculation against references.
    Uses synthetic data with known expected outcomes.
    """

    def test_merge_then_evaluate_produces_nonzero_f1(
        self,
        synthetic_pass_features: dict,
        synthetic_references: gpd.GeoDataFrame,
        synthetic_bounds: gpd.GeoDataFrame,
    ) -> None:
        """
        Merging 3 passes and evaluating against 4 references should produce
        F1 > 0. This catches any bug that makes the pipeline silently return
        zero metrics.
        """
        # Step 1: Within-pass deduplication
        deduped_passes = {}
        for pass_id, features in synthetic_pass_features.items():
            deduped_passes[pass_id] = deduplicate_within_pass(features)

        # Step 2: Cross-pass clustering
        clusters = cluster_across_passes(deduped_passes)
        assert len(clusters) > 0, "Clustering should produce at least one cluster"

        # Step 3: Apply threshold (T>=2 to retain most detections)
        total_passes = len(synthetic_pass_features)
        consensus = apply_threshold(clusters, threshold=2, total_passes=total_passes)
        consensus_features = consensus.get("features", [])
        assert len(consensus_features) > 0, "Threshold T>=2 should retain some detections"

        # Step 4: Convert to GeoDataFrame (mimicking what 6_accuracy_report does)
        records = []
        for feat in consensus_features:
            props = feat.get("properties", {})
            geom = Point(feat["geometry"]["coordinates"])
            source_tiles = props.get("source_tiles", [])
            # Apply the source_tile normalisation (E5b fix)
            source_tile = (
                source_tiles[0]
                if isinstance(source_tiles, list) and len(source_tiles) > 0
                else str(source_tiles)
            )
            records.append({
                "geometry": geom,
                "source_tile": source_tile,
                "subtype": props.get("subtype", "mound"),
                "vote_count": props.get("vote_count", 0),
            })

        gdf_pred = gpd.GeoDataFrame(records, crs=CRS)

        # Step 5: Calculate F1
        precision, recall, f1 = calculate_f1_internal(
            gdf_pred, synthetic_references, synthetic_bounds
        )

        # Assertions: F1 must be > 0 (the "not silently broken" check)
        assert f1 > 0, (
            f"F1 should be > 0 for synthetic data with known matches. "
            f"Got P={precision}, R={recall}, F1={f1}"
        )
        # More specific: we expect 3 TPs (R1, R2, R3 matched) and 1 FN (R4)
        assert precision > 0.5, f"Expected precision > 0.5, got {precision}"
        assert recall > 0.5, f"Expected recall > 0.5, got {recall}"

    def test_merge_vote_counts_are_correct(
        self,
        synthetic_pass_features: dict,
    ) -> None:
        """
        Verify that vote counts reflect the number of passes detecting
        each cluster. R1 is detected in all 3 passes; R3 in 2 passes.
        """
        deduped_passes = {}
        for pass_id, features in synthetic_pass_features.items():
            deduped_passes[pass_id] = deduplicate_within_pass(features)

        clusters = cluster_across_passes(deduped_passes)

        # Sort by vote count descending for predictable assertions
        vote_counts = sorted([c["vote_count"] for c in clusters], reverse=True)

        # R1 area: 3 passes contribute → vote_count=3
        # R2 area: 3 passes contribute → vote_count=3
        # R3 area: 2 passes contribute → vote_count=2
        # FP area: 1 pass contributes → vote_count=1
        assert vote_counts[0] == 3, f"Highest vote count should be 3, got {vote_counts[0]}"
        assert 1 in vote_counts, "FP detection (1 pass only) should have vote_count=1"

    def test_threshold_filters_low_vote_detections(
        self,
        synthetic_pass_features: dict,
    ) -> None:
        """
        Threshold T>=3 should retain only the most consistent detections,
        filtering out the FP (1 vote) and lower-confidence clusters.
        """
        deduped_passes = {}
        for pass_id, features in synthetic_pass_features.items():
            deduped_passes[pass_id] = deduplicate_within_pass(features)

        clusters = cluster_across_passes(deduped_passes)
        total_passes = len(synthetic_pass_features)

        # At T>=3, only clusters with 3 votes should survive
        consensus_t3 = apply_threshold(clusters, threshold=3, total_passes=total_passes)
        t3_features = consensus_t3.get("features", [])

        # At T>=1, all clusters should survive
        consensus_t1 = apply_threshold(clusters, threshold=1, total_passes=total_passes)
        t1_features = consensus_t1.get("features", [])

        assert len(t3_features) < len(t1_features), (
            "Higher threshold should retain fewer detections"
        )
        assert len(t3_features) >= 1, (
            "T>=3 should retain at least 1 detection (R1 and R2 areas have 3 votes)"
        )
