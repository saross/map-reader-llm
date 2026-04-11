"""Tier 1 unit tests for select_calibration_tiles.py.

Tests calibration/test splitting, nested pool generation, output
writing, and metadata — using synthetic GeoDataFrames written to
temporary files. No real tile data or API calls.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from select_calibration_tiles import (  # noqa: E402
    select_and_split,
    write_outputs,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_data(tmp_path):
    """Create synthetic bounds + reference GeoJSONs on disk.

    4 maps, 40 tiles each (160 total), varying density:
    - MapA: 10 empty, 20 sparse, 10 dense (40 mounds total)
    - MapB: 15 empty, 15 sparse, 10 dense (45 mounds total)
    - MapC: 20 empty, 10 sparse, 10 dense (40 mounds total)
    - MapD: 5 empty, 15 sparse, 20 dense (95 mounds total)

    Reference points placed deterministically inside tile bounds.
    """
    tile_size = 100  # Simple 100m tiles, no overlap
    tiles_per_map = 40
    crs = "EPSG:32635"

    map_configs = {
        "MapA": {"empty": 10, "sparse": 20, "dense": 10},
        "MapB": {"empty": 15, "sparse": 15, "dense": 10},
        "MapC": {"empty": 20, "sparse": 10, "dense": 10},
        "MapD": {"empty": 5, "sparse": 15, "dense": 20},
    }

    bounds_rows = []
    ref_points = []
    map_base_y = {
        "MapA": 0, "MapB": 10000, "MapC": 20000, "MapD": 30000,
    }

    for map_name, densities in map_configs.items():
        base_y = map_base_y[map_name]
        tile_idx = 0
        for density, count in densities.items():
            mounds_per_tile = (
                0 if density == "empty"
                else 1 if density == "sparse"
                else 4
            )
            for _ in range(count):
                x = tile_idx * tile_size
                y = base_y
                tile_name = f"{map_name}_x{x}_y{y}.png"
                bounds_rows.append({
                    "tile_name": tile_name,
                    "geometry": box(x, y, x + tile_size, y + tile_size),
                })
                # Place reference mounds inside tile
                for m in range(mounds_per_tile):
                    from shapely.geometry import MultiPoint, Point
                    px = x + 20 + m * 15
                    py = y + 50
                    ref_points.append({
                        "Map": map_name,
                        "geometry": MultiPoint([Point(px, py)]),
                    })
                tile_idx += 1

    gdf_bounds = gpd.GeoDataFrame(bounds_rows, crs=crs)
    gdf_refs = gpd.GeoDataFrame(ref_points, crs=crs)

    bounds_path = tmp_path / "bounds.geojson"
    gdf_bounds.to_file(bounds_path, driver="GeoJSON")

    ref_path = tmp_path / "refs.geojson"
    gdf_refs.to_file(ref_path, driver="GeoJSON")

    return bounds_path, ref_path, len(gdf_bounds), len(gdf_refs)


# ---------------------------------------------------------------------------
# Tests: select_and_split
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestSelectAndSplit:
    """Tests for the core calibration/test splitting logic."""

    def test_correct_total(self, synthetic_data):
        """Calibration + test = total tiles."""
        bounds_path, ref_path, total, _ = synthetic_data
        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=40, seed=42,
        )
        n_cal = len(result["calibration"][40])
        n_test = len(result["test"])
        assert n_cal + n_test == total

    def test_disjoint_sets(self, synthetic_data):
        """Calibration and test tiles must not overlap."""
        bounds_path, ref_path, _, _ = synthetic_data
        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=40, seed=42,
        )
        cal_idx = set(result["calibration"][40].index)
        test_idx = set(result["test"].index)
        assert cal_idx.isdisjoint(test_idx)

    def test_calibration_size_matches_request(self, synthetic_data):
        """Calibration pool has exactly the requested number of tiles."""
        bounds_path, ref_path, _, _ = synthetic_data
        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=60, seed=42,
        )
        assert len(result["calibration"][60]) == 60

    def test_geographic_balance(self, synthetic_data):
        """Calibration tiles should be balanced across maps."""
        bounds_path, ref_path, _, _ = synthetic_data
        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=40, seed=42,
        )
        per_map = (
            result["calibration"][40]["map_name"].value_counts()
        )
        # 40 tiles / 4 maps = 10 each
        assert all(per_map == 10), (
            f"Expected 10 per map, got {per_map.to_dict()}"
        )

    def test_calibration_too_large_raises(self, synthetic_data):
        """Requesting all tiles for calibration raises ValueError."""
        bounds_path, ref_path, total, _ = synthetic_data
        with pytest.raises(ValueError, match="must be less than"):
            select_and_split(
                bounds_path, ref_path,
                calibration_size=total, seed=42,
            )

    def test_reproducibility(self, synthetic_data):
        """Same seed produces identical split."""
        bounds_path, ref_path, _, _ = synthetic_data
        r1 = select_and_split(
            bounds_path, ref_path,
            calibration_size=40, seed=123,
        )
        r2 = select_and_split(
            bounds_path, ref_path,
            calibration_size=40, seed=123,
        )
        t1 = sorted(r1["calibration"][40]["tile_name"].tolist())
        t2 = sorted(r2["calibration"][40]["tile_name"].tolist())
        assert t1 == t2


# ---------------------------------------------------------------------------
# Tests: nested pools
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestNestedPools:
    """Tests for nested sub-pool generation (H10)."""

    def test_nesting_invariant(self, synthetic_data):
        """A ⊂ B ⊂ C ⊂ D for nested pools."""
        bounds_path, ref_path, _, _ = synthetic_data
        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=80,
            seed=42,
            nested_sizes=[20, 40, 80],
        )
        pools = result["calibration"]

        idx_20 = set(pools[20].index)
        idx_40 = set(pools[40].index)
        idx_80 = set(pools[80].index)

        assert idx_20.issubset(idx_40), "Pool 20 not ⊂ pool 40"
        assert idx_40.issubset(idx_80), "Pool 40 not ⊂ pool 80"

    def test_nested_sizes_correct(self, synthetic_data):
        """Each nested pool has the exact requested size."""
        bounds_path, ref_path, _, _ = synthetic_data
        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=80,
            seed=42,
            nested_sizes=[20, 40, 80],
        )
        pools = result["calibration"]
        assert len(pools[20]) == 20
        assert len(pools[40]) == 40
        assert len(pools[80]) == 80

    def test_nested_all_disjoint_from_test(self, synthetic_data):
        """Every nested pool is disjoint from the test set."""
        bounds_path, ref_path, _, _ = synthetic_data
        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=80,
            seed=42,
            nested_sizes=[20, 40, 80],
        )
        test_idx = set(result["test"].index)
        for size, pool in result["calibration"].items():
            pool_idx = set(pool.index)
            assert pool_idx.isdisjoint(test_idx), (
                f"Pool {size} overlaps with test set"
            )

    def test_mismatched_largest_nested_raises(self, synthetic_data):
        """Largest nested size != calibration_size raises ValueError."""
        bounds_path, ref_path, _, _ = synthetic_data
        with pytest.raises(ValueError, match="must equal"):
            select_and_split(
                bounds_path, ref_path,
                calibration_size=80,
                seed=42,
                nested_sizes=[20, 40, 60],  # 60 != 80
            )


# ---------------------------------------------------------------------------
# Tests: write_outputs
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestWriteOutputs:
    """Tests for output file writing."""

    def test_creates_expected_files(self, synthetic_data, tmp_path):
        """All expected manifest, bounds, and metadata files created."""
        bounds_path, ref_path, _, _ = synthetic_data
        output_dir = tmp_path / "output"

        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=80,
            seed=42,
            nested_sizes=[20, 40, 80],
        )
        write_outputs(result, output_dir)

        expected = [
            "calibration_manifest_020.json",
            "calibration_manifest_040.json",
            "calibration_manifest_080.json",
            "calibration_bounds_020.geojson",
            "calibration_bounds_040.geojson",
            "calibration_bounds_080.geojson",
            "test_manifest.json",
            "test_bounds.geojson",
            "tile_selection_metadata.json",
        ]
        for fname in expected:
            assert (output_dir / fname).exists(), (
                f"Missing output file: {fname}"
            )

    def test_manifest_tile_counts(self, synthetic_data, tmp_path):
        """Manifest JSON arrays have correct tile counts."""
        bounds_path, ref_path, _, _ = synthetic_data
        output_dir = tmp_path / "output"

        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=40,
            seed=42,
        )
        write_outputs(result, output_dir)

        cal_manifest = json.loads(
            (output_dir / "calibration_manifest_040.json").read_text()
        )
        test_manifest = json.loads(
            (output_dir / "test_manifest.json").read_text()
        )
        assert len(cal_manifest) == 40
        assert len(test_manifest) == 120  # 160 total - 40 cal

    def test_metadata_has_provenance(self, synthetic_data, tmp_path):
        """Metadata file contains seed, paths, and pool details."""
        bounds_path, ref_path, _, _ = synthetic_data
        output_dir = tmp_path / "output"

        result = select_and_split(
            bounds_path, ref_path,
            calibration_size=40,
            seed=42,
        )
        write_outputs(result, output_dir)

        meta = json.loads(
            (output_dir / "tile_selection_metadata.json").read_text()
        )
        assert meta["parameters"]["seed"] == 42
        assert meta["parameters"]["calibration_size"] == 40
        assert "40" in meta["calibration_pools"]
        assert meta["test_set"]["n_tiles"] == 120
        # Verify mound count fields use explicit overlap-aware naming
        assert "mounds_per_tile_sum" in meta["calibration_pools"]["40"]
        assert "mounds_per_tile_sum" in meta["test_set"]
        assert "total_mounds_per_tile_sum" in meta["totals"]
