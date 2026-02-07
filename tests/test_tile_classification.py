"""
Tests for tile-level classification functions in lib_advanced_metrics.py.

Tier 1 unit tests for Matthews Correlation Coefficient (MCC) calculation and
tile-level discrimination as specified in preregistration Section 4.2. Uses
synthetic GeoDataFrames to verify correct classification of tiles as empty
vs populated.
"""

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from scripts.lib_advanced_metrics import (
    bootstrap_tile_classification_ci,
    calculate_tile_classification,
)


def _make_tile_bounds(
    tile_names: list[str],
    origin_x: float = 500000,
    origin_y: float = 4700000,
    tile_size: float = 100,
    crs: str = "EPSG:32635",
) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame of tile boundaries for testing.

    Args:
        tile_names: List of tile name strings.
        origin_x: X coordinate of first tile origin.
        origin_y: Y coordinate of first tile origin.
        tile_size: Size of each tile in metres.
        crs: Coordinate reference system.

    Returns:
        GeoDataFrame with tile_name and geometry columns.
    """
    geometries = [
        box(origin_x + i * tile_size, origin_y,
            origin_x + i * tile_size + tile_size, origin_y + tile_size)
        for i in range(len(tile_names))
    ]
    return gpd.GeoDataFrame(
        {"tile_name": tile_names},
        geometry=geometries,
        crs=crs,
    )


def _make_detections(
    source_tiles: list[str],
    coords: list[tuple[float, float]] | None = None,
    crs: str = "EPSG:32635",
) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame of detections for testing.

    Args:
        source_tiles: List of source tile names for each detection.
        coords: Optional list of (x, y) coordinates. If None, generates
            default coords at the centre of each tile (assuming 100m tiles).
        crs: Coordinate reference system.

    Returns:
        GeoDataFrame with source_tile and geometry columns.
    """
    if coords is None:
        coords = [(500050 + i * 100, 4700050) for i in range(len(source_tiles))]
    points = [Point(x, y) for x, y in coords]
    return gpd.GeoDataFrame(
        {"source_tile": source_tiles},
        geometry=points,
        crs=crs,
    )


def _make_references(
    coords: list[tuple[float, float]],
    crs: str = "EPSG:32635",
) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame of reference mounds for testing.

    Args:
        coords: List of (x, y) coordinates for reference mounds.
        crs: Coordinate reference system.

    Returns:
        GeoDataFrame with geometry column.
    """
    if not coords:
        return gpd.GeoDataFrame(geometry=[], crs=crs)
    points = [Point(x, y) for x, y in coords]
    return gpd.GeoDataFrame(geometry=points, crs=crs)


def _make_empty_detections(crs: str = "EPSG:32635") -> gpd.GeoDataFrame:
    """Create an empty detections GeoDataFrame with the expected schema."""
    return gpd.GeoDataFrame(
        {"source_tile": []},
        geometry=[],
        crs=crs,
    )


@pytest.mark.tier1
class TestCalculateTileClassification:
    """Tests for tile-level MCC classification (preregistration Section 4.2)."""

    def test_all_true_positives(self) -> None:
        """All tiles have mounds and detections -> all TP.

        Scenario: 3 tiles, each with reference mounds and at least one detection.
        Expected: TP=3, TN=0, FP=0, FN=0, MCC=undefined (no negatives).
        """
        tile_names = ["tile_001", "tile_002", "tile_003"]
        gdf_bounds = _make_tile_bounds(tile_names)
        gdf_det = _make_detections(tile_names)
        ref_coords = [(500050, 4700050), (500150, 4700050), (500250, 4700050)]
        gdf_ref = _make_references(ref_coords)

        result = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)

        assert result["tp"] == 3
        assert result["tn"] == 0
        assert result["fp"] == 0
        assert result["fn"] == 0
        assert result["sensitivity"] == 1.0
        assert result["specificity"] is None  # No empty tiles
        assert result["n_populated"] == 3
        assert result["n_empty"] == 0

    def test_all_true_negatives(self) -> None:
        """All tiles are empty with no detections -> all TN.

        Scenario: 3 tiles, none have mounds, none have detections.
        Expected: TP=0, TN=3, FP=0, FN=0, MCC=undefined (no positives).
        """
        tile_names = ["tile_001", "tile_002", "tile_003"]
        gdf_bounds = _make_tile_bounds(tile_names)
        gdf_det = _make_empty_detections()
        gdf_ref = _make_references([])

        result = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)

        assert result["tp"] == 0
        assert result["tn"] == 3
        assert result["fp"] == 0
        assert result["fn"] == 0
        assert result["sensitivity"] is None  # No populated tiles
        assert result["specificity"] == 1.0
        assert result["n_populated"] == 0
        assert result["n_empty"] == 3

    def test_all_false_positives(self) -> None:
        """Empty tiles with spurious detections -> all FP (hallucinations).

        Scenario: 3 tiles, none have mounds, but all have detections.
        Expected: TP=0, TN=0, FP=3, FN=0.
        """
        tile_names = ["tile_001", "tile_002", "tile_003"]
        gdf_bounds = _make_tile_bounds(tile_names)
        gdf_det = _make_detections(tile_names)
        gdf_ref = _make_references([])

        result = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)

        assert result["tp"] == 0
        assert result["tn"] == 0
        assert result["fp"] == 3
        assert result["fn"] == 0
        assert result["sensitivity"] is None  # No populated tiles
        assert result["specificity"] == 0.0  # Detected in all empty tiles

    def test_all_false_negatives(self) -> None:
        """Populated tiles with no detections -> all FN (missed mounds).

        Scenario: 3 tiles, all have mounds, but no detections.
        Expected: TP=0, TN=0, FP=0, FN=3.
        """
        tile_names = ["tile_001", "tile_002", "tile_003"]
        gdf_bounds = _make_tile_bounds(tile_names)
        gdf_det = _make_empty_detections()
        ref_coords = [(500050, 4700050), (500150, 4700050), (500250, 4700050)]
        gdf_ref = _make_references(ref_coords)

        result = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)

        assert result["tp"] == 0
        assert result["tn"] == 0
        assert result["fp"] == 0
        assert result["fn"] == 3
        assert result["sensitivity"] == 0.0  # Missed all populated tiles
        assert result["specificity"] is None  # No empty tiles

    def test_mixed_classification(self) -> None:
        """Mixed scenario with all four classification types.

        Scenario:
        - tile_001: Has mounds, has detection -> TP
        - tile_002: Has mounds, no detection -> FN
        - tile_003: No mounds, has detection -> FP
        - tile_004: No mounds, no detection -> TN

        Expected: TP=1, TN=1, FP=1, FN=1.
        """
        tile_names = ["tile_001", "tile_002", "tile_003", "tile_004"]
        gdf_bounds = _make_tile_bounds(tile_names)

        gdf_det = _make_detections(
            ["tile_001", "tile_003"],
            coords=[(500050, 4700050), (500250, 4700050)],
        )
        ref_coords = [(500050, 4700050), (500150, 4700050)]
        gdf_ref = _make_references(ref_coords)

        result = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)

        assert result["tp"] == 1
        assert result["tn"] == 1
        assert result["fp"] == 1
        assert result["fn"] == 1

        # MCC = (1*1 - 1*1) / sqrt((1+1)(1+1)(1+1)(1+1)) = 0 / 4 = 0
        assert result["mcc"] == pytest.approx(0.0, abs=0.001)
        # Sensitivity = TP / (TP + FN) = 1 / 2 = 0.5
        assert result["sensitivity"] == pytest.approx(0.5, abs=0.001)
        # Specificity = TN / (TN + FP) = 1 / 2 = 0.5
        assert result["specificity"] == pytest.approx(0.5, abs=0.001)

    def test_perfect_mcc(self) -> None:
        """Perfect classification should yield MCC = 1.0.

        Scenario: 2 populated tiles with detections, 2 empty tiles without.
        """
        tile_names = ["tile_001", "tile_002", "tile_003", "tile_004"]
        gdf_bounds = _make_tile_bounds(tile_names)

        gdf_det = _make_detections(
            ["tile_001", "tile_002"],
            coords=[(500050, 4700050), (500150, 4700050)],
        )
        ref_coords = [(500050, 4700050), (500150, 4700050)]
        gdf_ref = _make_references(ref_coords)

        result = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)

        assert result["tp"] == 2
        assert result["tn"] == 2
        assert result["fp"] == 0
        assert result["fn"] == 0
        assert result["mcc"] == pytest.approx(1.0, abs=0.001)
        assert result["sensitivity"] == 1.0
        assert result["specificity"] == 1.0

    def test_empty_bounds(self) -> None:
        """Empty bounds should return error."""
        gdf_bounds = gpd.GeoDataFrame(
            {"tile_name": []},
            geometry=[],
            crs="EPSG:32635",
        )
        gdf_det = _make_detections([], coords=[])
        gdf_ref = _make_references([])

        result = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)

        assert "error" in result

    def test_tile_details_populated(self) -> None:
        """Tile details should be populated with per-tile information."""
        tile_names = ["tile_001", "tile_002"]
        gdf_bounds = _make_tile_bounds(tile_names)
        gdf_det = _make_detections(["tile_001"], coords=[(500050, 4700050)])
        gdf_ref = _make_references([(500050, 4700050)])

        result = calculate_tile_classification(gdf_det, gdf_ref, gdf_bounds)

        assert "tile_details" in result
        assert len(result["tile_details"]) == 2

        tile_001 = next(t for t in result["tile_details"] if t["tile_name"] == "tile_001")
        assert tile_001["has_mounds"] is True
        assert tile_001["has_detections"] is True
        assert tile_001["classification"] == "TP"


@pytest.mark.tier1
class TestBootstrapTileClassificationCi:
    """Tests for bootstrap confidence intervals on tile classification."""

    def test_bootstrap_with_fixed_seed(self) -> None:
        """Bootstrap with fixed seed should be reproducible."""
        tile_names = ["tile_001", "tile_002", "tile_003", "tile_004"]
        gdf_bounds = _make_tile_bounds(tile_names)

        gdf_det = _make_detections(
            ["tile_001", "tile_002"],
            coords=[(500050, 4700050), (500150, 4700050)],
        )
        ref_coords = [(500050, 4700050), (500150, 4700050)]
        gdf_ref = _make_references(ref_coords)

        result1 = bootstrap_tile_classification_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=100,
            random_seed=42,
        )
        result2 = bootstrap_tile_classification_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=100,
            random_seed=42,
        )

        assert result1["mcc"]["mean"] == result2["mcc"]["mean"]
        assert result1["mcc"]["ci_lower"] == result2["mcc"]["ci_lower"]

    def test_bootstrap_returns_valid_structure(self) -> None:
        """Bootstrap should return expected dict structure."""
        tile_names = ["tile_001", "tile_002"]
        gdf_bounds = _make_tile_bounds(tile_names)
        gdf_det = _make_detections(["tile_001"], coords=[(500050, 4700050)])
        gdf_ref = _make_references([(500050, 4700050)])

        result = bootstrap_tile_classification_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=50,
            random_seed=42,
        )

        assert "mcc" in result
        assert "sensitivity" in result
        assert "specificity" in result
        assert "n_iterations" in result
        assert result["n_iterations"] == 50

        for metric in ["mcc", "sensitivity", "specificity"]:
            assert "mean" in result[metric]
            assert "ci_lower" in result[metric]
            assert "ci_upper" in result[metric]

    def test_bootstrap_empty_bounds_error(self) -> None:
        """Empty bounds should return error."""
        gdf_bounds = gpd.GeoDataFrame(
            {"tile_name": []},
            geometry=[],
            crs="EPSG:32635",
        )
        gdf_det = _make_detections([], coords=[])
        gdf_ref = _make_references([])

        result = bootstrap_tile_classification_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=10,
        )

        assert "error" in result
