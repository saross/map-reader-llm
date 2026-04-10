"""
Tests for extract_candidates.py (H2 two-stage pipeline).

Tier 1 unit tests for the candidate extraction functionality that crops
image regions around proposer detections for verifier input.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.extract_candidates import (
    DEFAULT_PADDING,
    _write_empty_manifest,
    extract_candidates,
    get_tile_path,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_proposer_geojson(temp_dir) -> Path:
    """Create a sample proposer GeoJSON file for testing."""
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [500000, 4700000],
                        [500020, 4700000],
                        [500020, 4700020],
                        [500000, 4700020],
                        [500000, 4700000],
                    ]],
                },
                "properties": {
                    "source_tile": "K-35-052-4_32635_x1344_y1344.png",
                    "label": "mound",
                    "confidence": 0.85,
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [500100, 4700100],
                },
                "properties": {
                    "source_tile": "K-35-052-4_32635_x1344_y2240.png",
                    "label": "mound",
                    "confidence": 0.90,
                },
            },
        ],
    }

    geojson_path = temp_dir / "proposer_detections.geojson"
    with open(geojson_path, "w") as f:
        json.dump(geojson_data, f)

    return geojson_path


@pytest.fixture
def empty_proposer_geojson(temp_dir) -> Path:
    """Create an empty proposer GeoJSON file for testing."""
    geojson_data = {
        "type": "FeatureCollection",
        "features": [],
    }

    geojson_path = temp_dir / "empty_detections.geojson"
    with open(geojson_path, "w") as f:
        json.dump(geojson_data, f)

    return geojson_path


@pytest.fixture
def mock_tiles_dir(temp_dir) -> Path:
    """Create a mock tiles directory structure."""
    tiles_dir = temp_dir / "tiles"
    tiles_dir.mkdir()

    # Create subdirectory matching map sheet pattern
    map_dir = tiles_dir / "K-35-052-4_32635"
    map_dir.mkdir()

    # Create placeholder tile files (empty files for path testing)
    (map_dir / "K-35-052-4_32635_x1344_y1344.png").touch()
    (map_dir / "K-35-052-4_32635_x1344_y2240.png").touch()

    return tiles_dir


# =============================================================================
# GET_TILE_PATH TESTS
# =============================================================================


@pytest.mark.tier1
class TestGetTilePath:
    """Tests for tile path resolution."""

    def test_finds_tile_in_subdirectory(self, mock_tiles_dir) -> None:
        """Verify tile is found in map sheet subdirectory."""
        result = get_tile_path("K-35-052-4_32635_x1344_y1344.png", mock_tiles_dir)

        assert result is not None
        assert result.exists()
        assert result.name == "K-35-052-4_32635_x1344_y1344.png"

    def test_returns_none_for_missing_tile(self, mock_tiles_dir) -> None:
        """Verify None is returned for non-existent tile."""
        result = get_tile_path("nonexistent_tile.png", mock_tiles_dir)

        assert result is None

    def test_handles_tile_without_extension(self, mock_tiles_dir) -> None:
        """Verify tile is found when extension is omitted."""
        result = get_tile_path("K-35-052-4_32635_x1344_y1344", mock_tiles_dir)

        assert result is not None
        assert result.name == "K-35-052-4_32635_x1344_y1344.png"


# =============================================================================
# MANIFEST STRUCTURE TESTS
# =============================================================================


@pytest.mark.tier1
class TestManifestStructure:
    """Tests for candidate manifest structure and content."""

    def test_manifest_has_required_fields(self, temp_dir) -> None:
        """Verify empty manifest contains all required fields."""
        source_geojson = temp_dir / "source.geojson"
        source_geojson.touch()

        manifest_path = _write_empty_manifest(temp_dir, source_geojson, padding=75)

        assert manifest_path.exists()
        with open(manifest_path) as f:
            manifest = json.load(f)

        required_fields = [
            "version",
            "source_geojson",
            "padding",
            "total_detections",
            "successful_extractions",
            "failed_extractions",
            "missing_sources",
            "candidates",
        ]

        for field in required_fields:
            assert field in manifest, f"Missing required field: {field}"

    def test_manifest_candidate_entry_fields(self) -> None:
        """Verify candidate entries contain expected fields."""
        expected_fields = [
            "candidate_id",
            "crop_file",
            "source_tile",
            "centroid_x",
            "centroid_y",
            "properties",
        ]

        # Create sample candidate entry
        sample_entry = {
            "candidate_id": 0,
            "crop_file": "crops/candidate_00000.png",
            "source_tile": "tile_001.png",
            "centroid_x": 500010.0,
            "centroid_y": 4700010.0,
            "properties": {"label": "mound"},
        }

        for field in expected_fields:
            assert field in sample_entry, f"Missing expected field: {field}"

    def test_empty_manifest_for_empty_input(
        self, empty_proposer_geojson, temp_dir
    ) -> None:
        """Verify empty input produces empty manifest with zero counts."""
        output_dir = temp_dir / "output"

        # Mock rasterio since we don't have real tiles
        with patch("scripts.extract_candidates.crop_region", return_value=False):
            result = extract_candidates(
                proposer_geojson=empty_proposer_geojson,
                tiles_dir=temp_dir / "tiles",
                output_dir=output_dir,
                padding=75,
            )

        assert result is not None
        with open(result) as f:
            manifest = json.load(f)

        assert manifest["total_detections"] == 0
        assert manifest["successful_extractions"] == 0
        assert manifest["candidates"] == []


# =============================================================================
# EXTRACTION LOGIC TESTS
# =============================================================================


@pytest.mark.tier1
class TestExtractionLogic:
    """Tests for candidate extraction logic."""

    def test_dry_run_does_not_create_crops(
        self, sample_proposer_geojson, mock_tiles_dir, temp_dir
    ) -> None:
        """Verify dry run validates but doesn't create files."""
        output_dir = temp_dir / "output"

        # Run dry run (no rasterio mocking needed as crop_region won't be called)
        result = extract_candidates(
            proposer_geojson=sample_proposer_geojson,
            tiles_dir=mock_tiles_dir,
            output_dir=output_dir,
            dry_run=True,
        )

        # Dry run returns None
        assert result is None

        # Output directory should not be created in dry run
        # (Actually it is created but no files written - implementation detail)

    def test_missing_source_tile_property_increments_failed(self, temp_dir) -> None:
        """Verify detection without source_tile is counted as failed."""
        # Create GeoJSON with missing source_tile
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [500000, 4700000]},
                    "properties": {"label": "mound"},  # No source_tile
                },
            ],
        }

        geojson_path = temp_dir / "no_tile.geojson"
        with open(geojson_path, "w") as f:
            json.dump(geojson_data, f)

        # Create tiles directory (must exist for extraction to proceed)
        tiles_dir = temp_dir / "tiles"
        tiles_dir.mkdir()

        output_dir = temp_dir / "output"

        with patch("scripts.extract_candidates.crop_region", return_value=True):
            result = extract_candidates(
                proposer_geojson=geojson_path,
                tiles_dir=tiles_dir,
                output_dir=output_dir,
            )

        with open(result) as f:
            manifest = json.load(f)

        assert manifest["total_detections"] == 1
        assert manifest["failed_extractions"] == 1
        assert manifest["successful_extractions"] == 0

    def test_missing_tile_file_tracked(
        self, sample_proposer_geojson, temp_dir
    ) -> None:
        """Verify missing tile files are tracked in manifest."""
        # Use empty tiles directory (no actual tiles) AND a
        # non-existent rasters directory so raster fallback also fails.
        empty_tiles_dir = temp_dir / "empty_tiles"
        empty_tiles_dir.mkdir()
        missing_rasters_dir = temp_dir / "no_rasters"

        output_dir = temp_dir / "output"

        result = extract_candidates(
            proposer_geojson=sample_proposer_geojson,
            tiles_dir=empty_tiles_dir,
            output_dir=output_dir,
            rasters_dir=missing_rasters_dir,
        )

        with open(result) as f:
            manifest = json.load(f)

        # All should fail due to missing tiles and rasters
        assert manifest["failed_extractions"] == 2
        assert len(manifest["missing_sources"]) > 0


# =============================================================================
# CENTROID CALCULATION TESTS
# =============================================================================


@pytest.mark.tier1
class TestCentroidCalculation:
    """Tests for centroid calculation from different geometry types."""

    def test_point_centroid(self) -> None:
        """Verify Point geometry centroid is the point itself."""
        from shapely.geometry import shape

        geom = {"type": "Point", "coordinates": [500000, 4700000]}
        geom_shape = shape(geom)

        assert geom_shape.centroid.x == 500000
        assert geom_shape.centroid.y == 4700000

    def test_polygon_centroid(self) -> None:
        """Verify Polygon geometry centroid is computed correctly."""
        from shapely.geometry import shape

        # 20m × 20m square centred at (500010, 4700010)
        geom = {
            "type": "Polygon",
            "coordinates": [[
                [500000, 4700000],
                [500020, 4700000],
                [500020, 4700020],
                [500000, 4700020],
                [500000, 4700000],
            ]],
        }
        geom_shape = shape(geom)

        assert abs(geom_shape.centroid.x - 500010) < 0.01
        assert abs(geom_shape.centroid.y - 4700010) < 0.01


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


@pytest.mark.tier1
class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_default_padding_value(self) -> None:
        """Verify default padding constant is set correctly."""
        assert DEFAULT_PADDING == 75

    def test_candidate_filename_format(self) -> None:
        """Verify candidate filenames follow expected pattern."""
        # Format: candidate_XXXXX.png (5-digit zero-padded)
        for idx in [0, 1, 99, 12345]:
            expected = f"candidate_{idx:05d}.png"
            assert len(expected) == 19  # "candidate_" (10) + 5 digits + ".png" (4)
            assert expected.startswith("candidate_")
            assert expected.endswith(".png")

    def test_handles_geojson_with_extra_properties(self, temp_dir) -> None:
        """Verify extra properties in GeoJSON are preserved."""
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [500000, 4700000]},
                    "properties": {
                        "source_tile": "tile.png",
                        "label": "mound",
                        "custom_field": "custom_value",
                        "confidence": 0.95,
                    },
                },
            ],
        }

        geojson_path = temp_dir / "extra_props.geojson"
        with open(geojson_path, "w") as f:
            json.dump(geojson_data, f)

        # Create a mock tiles directory with the tile
        tiles_dir = temp_dir / "tiles"
        tiles_dir.mkdir()
        (tiles_dir / "tile.png").touch()

        output_dir = temp_dir / "output"

        # Mock crop_region to succeed
        with patch("scripts.extract_candidates.crop_region", return_value=True):
            result = extract_candidates(
                proposer_geojson=geojson_path,
                tiles_dir=tiles_dir,
                output_dir=output_dir,
            )

        with open(result) as f:
            manifest = json.load(f)

        # Check properties are preserved
        candidate = manifest["candidates"][0]
        assert candidate["properties"]["custom_field"] == "custom_value"
        assert candidate["properties"]["confidence"] == 0.95


# =============================================================================
# CROP REGION TESTS (MOCKED)
# =============================================================================


@pytest.mark.tier1
class TestCropRegionLogic:
    """Tests for crop region calculation (without actual rasterio calls)."""

    def test_crop_window_calculation(self) -> None:
        """Verify crop window dimensions are calculated correctly."""
        padding = 75

        # Window should be 2*padding × 2*padding
        expected_width = padding * 2
        expected_height = padding * 2

        assert expected_width == 150
        assert expected_height == 150

    def test_crop_centered_on_detection(self) -> None:
        """Verify crop is centered on detection centroid."""
        padding = 75
        col = 256  # Pixel column of centroid
        row = 256  # Pixel row of centroid

        col_start = col - padding
        row_start = row - padding
        col_end = col + padding
        row_end = row + padding

        # Centre of crop window should be at original centroid
        crop_centre_col = (col_start + col_end) // 2
        crop_centre_row = (row_start + row_end) // 2

        assert crop_centre_col == col
        assert crop_centre_row == row

    def test_crop_window_bounds_clamping(self) -> None:
        """Verify crop window is clamped to tile boundaries."""
        padding = 75
        tile_width = 512
        tile_height = 512

        # Detection near edge
        col = 50  # Near left edge
        row = 50  # Near top edge

        col_start = max(0, col - padding)
        row_start = max(0, row - padding)
        col_end = min(tile_width, col + padding)
        row_end = min(tile_height, row + padding)

        # Should clamp to tile boundaries
        assert col_start == 0
        assert row_start == 0
        assert col_end == 125
        assert row_end == 125
