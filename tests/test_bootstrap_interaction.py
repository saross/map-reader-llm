"""
Tests for bootstrap interaction CI function.

Tier 1 unit tests for the bootstrap_interaction_ci() function in
lib_advanced_metrics.py. Uses synthetic GeoDataFrames to verify correct
detection of two-way interaction effects via difference-of-differences
bootstrap.

These tests support preregistration Section 5.5 (M/E × H5 interaction
analysis), which uses bootstrap interaction testing instead of two-way
ANOVA.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import bootstrap_interaction_ci

# Standard CRS used throughout the project (UTM Zone 35N)
CRS = "EPSG:32635"


def _make_tile_bounds(n_tiles: int) -> gpd.GeoDataFrame:
    """Create n_tiles non-overlapping tile bounds in a row.

    Each tile is a 100m x 100m square, spaced 200m apart to avoid any
    ambiguity about tile membership. Uses the K-35-052-4_32635 map prefix
    so that get_map_name() recognises the tiles (required by
    calculate_f1_internal).

    Args:
        n_tiles: Number of tiles to create.

    Returns:
        GeoDataFrame with tile_name and geometry columns.
    """
    base_x, base_y = 500000, 4700000
    tiles = []
    names = []
    for i in range(n_tiles):
        x = base_x + i * 200
        tiles.append(box(x, base_y, x + 100, base_y + 100))
        names.append(f"K-35-052-4_32635_tile_{i:03d}")
    return gpd.GeoDataFrame(
        {"tile_name": names}, geometry=tiles, crs=CRS
    )


def _make_references(n_tiles: int) -> gpd.GeoDataFrame:
    """Create one reference mound at the centre of each tile.

    Includes a 'Map' column matching the map prefix used in tile names,
    as required by calculate_f1_internal for spatial scoping.

    Args:
        n_tiles: Number of tiles (one mound per tile).

    Returns:
        GeoDataFrame with Point geometries at tile centres and Map column.
    """
    base_x, base_y = 500000, 4700000
    points = []
    for i in range(n_tiles):
        x = base_x + i * 200 + 50  # Centre of the 100m tile
        points.append(Point(x, base_y + 50))
    # Map column must match get_map_name() output for the tile prefix
    return gpd.GeoDataFrame(
        {"Map": ["K-35-052-4_32635"] * n_tiles},
        geometry=points,
        crs=CRS,
    )


def _make_detections(
    n_tiles: int,
    hit_tiles: list[int],
) -> gpd.GeoDataFrame:
    """Create detections that match references in specified tiles.

    For each tile index in hit_tiles, places a detection within 5m of
    the reference mound (well within 20m tolerance). Other tiles get
    no detections.

    Args:
        n_tiles: Total number of tiles.
        hit_tiles: Indices of tiles where the model detects the mound.

    Returns:
        GeoDataFrame with source_tile column and Point geometries.
    """
    base_x, base_y = 500000, 4700000
    points = []
    tile_names = []
    for i in hit_tiles:
        x = base_x + i * 200 + 55  # 5m offset from reference
        points.append(Point(x, base_y + 50))
        tile_names.append(f"K-35-052-4_32635_tile_{i:03d}")

    if not points:
        return gpd.GeoDataFrame(
            {"source_tile": []},
            geometry=[],
            crs=CRS,
        )

    return gpd.GeoDataFrame(
        {"source_tile": tile_names},
        geometry=points,
        crs=CRS,
    )


def _build_conditions(
    n_tiles: int,
    hit_map: dict[tuple, list[int]],
) -> dict:
    """Build a conditions dict from a hit map.

    Args:
        n_tiles: Total number of tiles.
        hit_map: Maps (factor_a, factor_b) to list of tile indices
            where the model correctly detects the mound.

    Returns:
        Dict mapping (factor_a, factor_b) to (gdf_det, gdf_bounds).
    """
    bounds = _make_tile_bounds(n_tiles)
    conditions = {}
    for key, hits in hit_map.items():
        dets = _make_detections(n_tiles, hits)
        conditions[key] = (dets, bounds.copy())
    return conditions


@pytest.mark.tier1
class TestBootstrapInteractionCi:
    """Tests for the bootstrap_interaction_ci() function."""

    def test_no_interaction_detected(self) -> None:
        """When factor_b has the same effect at both factor_a levels,
        no interaction should be detected.

        Setup (20 tiles, 1 mound each):
        - (A1, B1): hits tiles 0-15 → recall 16/20 = 0.80
        - (A1, B2): hits tiles 0-9  → recall 10/20 = 0.50
        - (A2, B1): hits tiles 0-15 → recall 16/20 = 0.80
        - (A2, B2): hits tiles 0-9  → recall 10/20 = 0.50
        Simple effect of B at A1 = same as at A2 → no interaction.
        """
        n_tiles = 20
        hit_map = {
            ("A1", "B1"): list(range(16)),
            ("A1", "B2"): list(range(10)),
            ("A2", "B1"): list(range(16)),
            ("A2", "B2"): list(range(10)),
        }
        conditions = _build_conditions(n_tiles, hit_map)
        gdf_ref = _make_references(n_tiles)

        result = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            factor_a_name="M/E",
            factor_b_name="H5",
            metric="f1",
            n_iterations=500,
            random_seed=42,
        )

        assert "error" not in result
        assert result["interaction_detected"] is False
        assert len(result["interaction_contrasts"]) == 1

        # The difference-of-differences should be near zero
        dod = result["interaction_contrasts"][0]["difference_of_differences"]
        assert abs(dod["mean"]) < 0.05, (
            f"Expected near-zero interaction, got {dod['mean']:.3f}"
        )

    def test_interaction_detected(self) -> None:
        """When factor_b has a large effect at A1 but no effect at A2,
        interaction should be detected.

        Setup (20 tiles, 1 mound each):
        - (A1, B1): hits tiles 0-17 → recall 18/20 = 0.90
        - (A1, B2): hits tiles 0-3  → recall 4/20  = 0.20
        - (A2, B1): hits tiles 0-17 → recall 18/20 = 0.90
        - (A2, B2): hits tiles 0-17 → recall 18/20 = 0.90
        Simple effect of B at A1 = -0.70, at A2 = 0.0 → strong interaction.
        """
        n_tiles = 20
        hit_map = {
            ("A1", "B1"): list(range(18)),
            ("A1", "B2"): list(range(4)),
            ("A2", "B1"): list(range(18)),
            ("A2", "B2"): list(range(18)),
        }
        conditions = _build_conditions(n_tiles, hit_map)
        gdf_ref = _make_references(n_tiles)

        result = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            factor_a_name="M/E",
            factor_b_name="H5",
            metric="f1",
            n_iterations=500,
            random_seed=42,
        )

        assert "error" not in result
        assert result["interaction_detected"] is True

        # The difference-of-differences should be substantially negative
        # (A1 effect is negative, A2 effect is zero, so A1 - A2 < 0)
        dod = result["interaction_contrasts"][0]["difference_of_differences"]
        assert dod["ci_upper"] < 0 or dod["ci_lower"] > 0, (
            "Expected CI to exclude zero for strong interaction"
        )

    def test_three_by_three_design(self) -> None:
        """Test with a 3×3 factorial (matching H5's 3 M/E × 3 H5 design).

        With 3 factor_a levels, there should be 3 pairwise interaction
        contrasts (A1-A2, A1-A3, A2-A3).
        """
        n_tiles = 20
        all_tiles = list(range(n_tiles))
        hit_map = {
            ("M1", "H5_min"): all_tiles[:16],
            ("M1", "H5_terse"): all_tiles[:14],
            ("M1", "H5_verbose"): all_tiles[:12],
            ("M2", "H5_min"): all_tiles[:16],
            ("M2", "H5_terse"): all_tiles[:14],
            ("M2", "H5_verbose"): all_tiles[:12],
            ("M3", "H5_min"): all_tiles[:16],
            ("M3", "H5_terse"): all_tiles[:14],
            ("M3", "H5_verbose"): all_tiles[:12],
        }
        conditions = _build_conditions(n_tiles, hit_map)
        gdf_ref = _make_references(n_tiles)

        result = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            factor_a_name="M/E",
            factor_b_name="H5",
            metric="f1",
            n_iterations=200,
            random_seed=42,
        )

        assert "error" not in result
        # 3 factor_a levels → C(3,2) = 3 pairwise contrasts
        assert len(result["interaction_contrasts"]) == 3
        assert result["factor_a_levels"] == ["M1", "M2", "M3"]
        assert result["factor_b_levels"] == ["H5_min", "H5_terse", "H5_verbose"]
        # No interaction (all levels have same effect)
        assert result["interaction_detected"] is False

    def test_precision_metric(self) -> None:
        """Function should work with precision metric, not just F1."""
        n_tiles = 20
        hit_map = {
            ("A1", "B1"): list(range(16)),
            ("A1", "B2"): list(range(10)),
            ("A2", "B1"): list(range(16)),
            ("A2", "B2"): list(range(10)),
        }
        conditions = _build_conditions(n_tiles, hit_map)
        gdf_ref = _make_references(n_tiles)

        result = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            metric="precision",
            n_iterations=100,
            random_seed=42,
        )

        assert "error" not in result
        assert result["metric"] == "precision"

    def test_error_single_factor_a_level(self) -> None:
        """Should return error if only one factor_a level provided."""
        n_tiles = 10
        hit_map = {
            ("A1", "B1"): list(range(8)),
            ("A1", "B2"): list(range(5)),
        }
        conditions = _build_conditions(n_tiles, hit_map)
        gdf_ref = _make_references(n_tiles)

        result = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            n_iterations=100,
            random_seed=42,
        )

        assert "error" in result

    def test_error_single_factor_b_level(self) -> None:
        """Should return error if only one factor_b level provided."""
        n_tiles = 10
        hit_map = {
            ("A1", "B1"): list(range(8)),
            ("A2", "B1"): list(range(5)),
        }
        conditions = _build_conditions(n_tiles, hit_map)
        gdf_ref = _make_references(n_tiles)

        result = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            n_iterations=100,
            random_seed=42,
        )

        assert "error" in result

    def test_error_invalid_metric(self) -> None:
        """Should return error for unknown metric name."""
        n_tiles = 10
        hit_map = {
            ("A1", "B1"): list(range(8)),
            ("A1", "B2"): list(range(5)),
            ("A2", "B1"): list(range(8)),
            ("A2", "B2"): list(range(5)),
        }
        conditions = _build_conditions(n_tiles, hit_map)
        gdf_ref = _make_references(n_tiles)

        result = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            metric="mcc",
            n_iterations=100,
            random_seed=42,
        )

        assert "error" in result

    def test_simple_effects_returned(self) -> None:
        """Simple effects should be returned for each factor_a level."""
        n_tiles = 20
        hit_map = {
            ("A1", "B1"): list(range(16)),
            ("A1", "B2"): list(range(10)),
            ("A2", "B1"): list(range(16)),
            ("A2", "B2"): list(range(10)),
        }
        conditions = _build_conditions(n_tiles, hit_map)
        gdf_ref = _make_references(n_tiles)

        result = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            n_iterations=200,
            random_seed=42,
        )

        assert "simple_effects" in result
        assert "A1" in result["simple_effects"]
        assert "A2" in result["simple_effects"]

        for level in ["A1", "A2"]:
            effect = result["simple_effects"][level]
            assert "mean" in effect
            assert "ci_lower" in effect
            assert "ci_upper" in effect
            # B2 has fewer hits than B1, so simple effect should be negative
            assert effect["mean"] < 0, (
                f"Expected negative simple effect at {level}, "
                f"got {effect['mean']:.3f}"
            )

    def test_reproducibility_with_seed(self) -> None:
        """Same seed should produce identical results."""
        n_tiles = 20
        hit_map = {
            ("A1", "B1"): list(range(16)),
            ("A1", "B2"): list(range(10)),
            ("A2", "B1"): list(range(14)),
            ("A2", "B2"): list(range(10)),
        }
        conditions = _build_conditions(n_tiles, hit_map)
        gdf_ref = _make_references(n_tiles)

        result1 = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            n_iterations=100,
            random_seed=123,
        )
        result2 = bootstrap_interaction_ci(
            conditions=conditions,
            gdf_ref=gdf_ref,
            n_iterations=100,
            random_seed=123,
        )

        dod1 = result1["interaction_contrasts"][0]["difference_of_differences"]
        dod2 = result2["interaction_contrasts"][0]["difference_of_differences"]
        assert dod1["mean"] == dod2["mean"]
        assert dod1["ci_lower"] == dod2["ci_lower"]
        assert dod1["ci_upper"] == dod2["ci_upper"]
