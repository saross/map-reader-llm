"""
Tests for error taxonomy and symbol normalisation in lib_advanced_metrics.py.

Tier 1 unit tests for the error categorisation functions that classify false
positives and false negatives by symbol type.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (
    normalise_ref_class,
    error_taxonomy,
)


@pytest.mark.tier1
class TestNormaliseRefClass:
    """Tests for reference symbol class normalisation."""

    def test_burial_mound_variants(self) -> None:
        """Various burial mound symbols should normalise to 'burial_mound'."""
        assert normalise_ref_class("Burial Mound") == "burial_mound"
        assert normalise_ref_class("burial mound") == "burial_mound"
        assert normalise_ref_class("BURIAL MOUND") == "burial_mound"
        assert normalise_ref_class("Kurgan") == "burial_mound"
        assert normalise_ref_class("kurgan") == "burial_mound"

    def test_benchmark_mound(self) -> None:
        """Benchmark on mound should normalise to 'benchmark_mound'."""
        assert normalise_ref_class("Bench Mark on Mound") == "benchmark_mound"
        assert normalise_ref_class("bench mark") == "benchmark_mound"
        assert normalise_ref_class("BENCH MARK") == "benchmark_mound"

    def test_triangulation_mound(self) -> None:
        """Triangulation on mound should normalise to 'triangulation_mound'."""
        assert normalise_ref_class("Triangulation Point on Mound") == "triangulation_mound"
        assert normalise_ref_class("triangulation") == "triangulation_mound"
        assert normalise_ref_class("TRIANGULATION") == "triangulation_mound"

    def test_settlement_mound(self) -> None:
        """Settlement mound should normalise to 'settlement_mound'."""
        assert normalise_ref_class("Settlement Mound") == "settlement_mound"
        assert normalise_ref_class("settlement") == "settlement_mound"

    def test_unknown_symbol(self) -> None:
        """Unrecognised symbols should return 'unknown'."""
        assert normalise_ref_class("Church") == "unknown"
        assert normalise_ref_class("River") == "unknown"
        assert normalise_ref_class("") == "unknown"

    def test_none_handling(self) -> None:
        """None values should be handled safely."""
        assert normalise_ref_class(None) == "unknown"

    def test_numeric_handling(self) -> None:
        """Numeric values should be handled safely."""
        assert normalise_ref_class(123) == "unknown"


def create_tile_bounds(
    tile_names: list[str],
    origin_x: float = 500000,
    origin_y: float = 4700000,
    tile_size: float = 100,
    crs: str = "EPSG:32635",
) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame of tile boundaries for testing."""
    geometries = []
    for i, name in enumerate(tile_names):
        x = origin_x + i * tile_size
        y = origin_y
        geom = box(x, y, x + tile_size, y + tile_size)
        geometries.append(geom)

    return gpd.GeoDataFrame(
        {"tile_name": tile_names},
        geometry=geometries,
        crs=crs,
    )


def create_detections(
    source_tiles: list[str],
    coords: list[tuple[float, float]],
    subtypes: list[str] | None = None,
    crs: str = "EPSG:32635",
) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame of detections for testing."""
    points = [Point(x, y) for x, y in coords]
    data = {"source_tile": source_tiles}
    if subtypes:
        data["subtype"] = subtypes
    return gpd.GeoDataFrame(data, geometry=points, crs=crs)


def create_references(
    coords: list[tuple[float, float]],
    symbols: list[str],
    crs: str = "EPSG:32635",
) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame of reference mounds for testing."""
    if not coords:
        return gpd.GeoDataFrame({"Symbol": []}, geometry=[], crs=crs)

    points = [Point(x, y) for x, y in coords]
    return gpd.GeoDataFrame({"Symbol": symbols}, geometry=points, crs=crs)


@pytest.mark.tier1
class TestErrorTaxonomy:
    """Tests for false positive/negative categorisation."""

    def test_empty_inputs(self) -> None:
        """Empty detections and references should return empty taxonomy."""
        gdf_bounds = create_tile_bounds(["tile_001"])
        gdf_det = gpd.GeoDataFrame(
            {"source_tile": [], "subtype": []},
            geometry=[],
            crs="EPSG:32635",
        )
        gdf_ref = create_references([], [])

        result = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

        assert result["false_positives"] == {}
        assert result["false_negatives"] == {}

    def test_all_detections_matched(self) -> None:
        """No false positives when all detections match references."""
        gdf_bounds = create_tile_bounds(["tile_001"])

        # Detection at same location as reference
        gdf_det = create_detections(
            ["tile_001"],
            coords=[(500050, 4700050)],
            subtypes=["burial_mound"],
        )
        gdf_ref = create_references(
            [(500050, 4700050)],
            ["Burial Mound"],
        )

        result = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

        assert result["false_positives"] == {}
        assert result["false_negatives"] == {}

    def test_false_positives_categorised_by_subtype(self) -> None:
        """False positives should be categorised by detection subtype."""
        gdf_bounds = create_tile_bounds(["tile_001", "tile_002"])

        # Detections with no matching references
        gdf_det = create_detections(
            ["tile_001", "tile_001", "tile_002"],
            coords=[(500050, 4700050), (500060, 4700050), (500150, 4700050)],
            subtypes=["burial_mound", "burial_mound", "benchmark_mound"],
        )
        gdf_ref = create_references([], [])

        result = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

        # Should have 2 burial_mound FPs and 1 benchmark_mound FP
        assert result["false_positives"].get("burial_mound") == 2
        assert result["false_positives"].get("benchmark_mound") == 1
        assert result["false_negatives"] == {}

    def test_false_negatives_categorised_by_class(self) -> None:
        """False negatives should be categorised by normalised reference class."""
        gdf_bounds = create_tile_bounds(["tile_001", "tile_002"])

        # No detections
        gdf_det = gpd.GeoDataFrame(
            {"source_tile": [], "subtype": []},
            geometry=[],
            crs="EPSG:32635",
        )

        # References that will all be missed
        gdf_ref = create_references(
            [(500050, 4700050), (500060, 4700050), (500150, 4700050)],
            ["Burial Mound", "Kurgan", "Bench Mark on Mound"],
        )

        result = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

        assert result["false_positives"] == {}
        # Two burial mounds (Burial Mound + Kurgan) and one benchmark
        assert result["false_negatives"].get("burial_mound") == 2
        assert result["false_negatives"].get("benchmark_mound") == 1

    def test_mixed_fps_and_fns(self) -> None:
        """Scenario with both false positives and false negatives."""
        gdf_bounds = create_tile_bounds(["tile_001", "tile_002", "tile_003"])

        # Detection in tile_001 (matches ref), detection in tile_002 (no ref = FP)
        gdf_det = create_detections(
            ["tile_001", "tile_002"],
            coords=[(500050, 4700050), (500150, 4700050)],
            subtypes=["burial_mound", "settlement_mound"],
        )

        # Reference in tile_001 (matched) and tile_003 (missed = FN)
        gdf_ref = create_references(
            [(500050, 4700050), (500250, 4700050)],
            ["Burial Mound", "Triangulation Point on Mound"],
        )

        result = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

        # One FP (settlement_mound detection in tile_002)
        assert result["false_positives"].get("settlement_mound") == 1
        assert "burial_mound" not in result["false_positives"]

        # One FN (triangulation_mound in tile_003)
        assert result["false_negatives"].get("triangulation_mound") == 1
        assert "burial_mound" not in result["false_negatives"]

    def test_references_outside_bounds_excluded(self) -> None:
        """References outside tile bounds should not count as false negatives."""
        # Only one tile
        gdf_bounds = create_tile_bounds(["tile_001"])

        # No detections
        gdf_det = gpd.GeoDataFrame(
            {"source_tile": [], "subtype": []},
            geometry=[],
            crs="EPSG:32635",
        )

        # Reference inside bounds and one far outside
        gdf_ref = create_references(
            [(500050, 4700050), (600000, 4800000)],  # Second is far outside
            ["Burial Mound", "Burial Mound"],
        )

        result = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

        # Only the reference inside bounds should be counted as FN
        assert result["false_negatives"].get("burial_mound") == 1

    def test_spatial_tolerance_respected(self) -> None:
        """Detections within 20m tolerance should match (not be FPs)."""
        gdf_bounds = create_tile_bounds(["tile_001"])

        # Detection 15m away from reference (within 20m tolerance)
        gdf_det = create_detections(
            ["tile_001"],
            coords=[(500050, 4700050)],
            subtypes=["burial_mound"],
        )
        gdf_ref = create_references(
            [(500065, 4700050)],  # 15m away
            ["Burial Mound"],
        )

        result = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

        # Should match, so no FPs or FNs
        assert result["false_positives"] == {}
        assert result["false_negatives"] == {}

    def test_detection_outside_tolerance_is_fp(self) -> None:
        """Detections >20m from references should be false positives."""
        gdf_bounds = create_tile_bounds(["tile_001"])

        # Detection 30m away from reference (outside 20m tolerance)
        gdf_det = create_detections(
            ["tile_001"],
            coords=[(500050, 4700050)],
            subtypes=["burial_mound"],
        )
        gdf_ref = create_references(
            [(500080, 4700050)],  # 30m away
            ["Burial Mound"],
        )

        result = error_taxonomy(gdf_det, gdf_ref, gdf_bounds)

        # Detection is FP (too far), reference is FN (not matched)
        assert result["false_positives"].get("burial_mound") == 1
        assert result["false_negatives"].get("burial_mound") == 1
