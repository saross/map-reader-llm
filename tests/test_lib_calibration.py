"""Tier 1 unit tests for lib_calibration.py.

Tests density categorisation, stratified sampling, nested subsampling,
and difficulty scoring — all with synthetic data. No file I/O or API.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, box

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from lib_advanced_metrics import get_map_name  # noqa: E402
from lib_calibration import (  # noqa: E402
    categorise_density,
    enrich_bounds_with_mound_counts,
    nested_subsample,
    score_difficulty_hn,
    score_difficulty_hp,
    stratified_sample,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def four_map_tiles():
    """Synthetic tile DataFrame: 4 maps, 40 tiles each, mixed density.

    Map A: 40 tiles (20 empty, 12 sparse, 8 dense)
    Map B: 40 tiles (15 empty, 15 sparse, 10 dense)
    Map C: 40 tiles (25 empty, 10 sparse, 5 dense)
    Map D: 40 tiles (10 empty, 10 sparse, 20 dense)
    Total: 160 tiles
    """
    rows = []
    configs = {
        "MapA": {"empty": 20, "sparse": 12, "dense": 8},
        "MapB": {"empty": 15, "sparse": 15, "dense": 10},
        "MapC": {"empty": 25, "sparse": 10, "dense": 5},
        "MapD": {"empty": 10, "sparse": 10, "dense": 20},
    }
    idx = 0
    for map_name, densities in configs.items():
        for density, count in densities.items():
            for _ in range(count):
                mound_count = (
                    0 if density == "empty"
                    else 1 if density == "sparse"
                    else 4
                )
                rows.append({
                    "tile_name": f"{map_name}_x{idx*336}_y0.png",
                    "map_name": map_name,
                    "density": density,
                    "mound_count": mound_count,
                })
                idx += 1
    return pd.DataFrame(rows)


@pytest.fixture
def spatial_bounds_and_refs():
    """Synthetic bounds + reference GeoDataFrames for enrichment tests.

    3 tiles in a row (0-100, 100-200, 200-300 on X axis, 0-100 on Y).
    Tile 0: 0 mounds (empty)
    Tile 1: 2 mounds at (120,50) and (180,50) (sparse)
    Tile 2: 4 mounds (dense)
    """
    bounds = gpd.GeoDataFrame(
        {
            "tile_name": [
                "test_map_x0_y0.png",
                "test_map_x100_y0.png",
                "test_map_x200_y0.png",
            ],
        },
        geometry=[
            box(0, 0, 100, 100),
            box(100, 0, 200, 100),
            box(200, 0, 300, 100),
        ],
        crs="EPSG:32635",
    )

    ref_points = [
        Point(120, 50), Point(180, 50),  # Tile 1 (sparse)
        Point(210, 20), Point(230, 40),   # Tile 2 (dense)
        Point(250, 60), Point(270, 80),   # Tile 2 (dense)
    ]
    refs = gpd.GeoDataFrame(
        {"Map": ["test_map"] * 6},
        geometry=ref_points,
        crs="EPSG:32635",
    )

    return bounds, refs


# ---------------------------------------------------------------------------
# Tests: categorise_density
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestCategoriseDensity:
    """Tests for density categorisation thresholds."""

    def test_zero_is_empty(self):
        assert categorise_density(0) == "empty"

    def test_one_is_sparse(self):
        assert categorise_density(1) == "sparse"

    def test_two_is_sparse(self):
        assert categorise_density(2) == "sparse"

    def test_three_is_dense(self):
        assert categorise_density(3) == "dense"

    def test_many_is_dense(self):
        assert categorise_density(50) == "dense"


# ---------------------------------------------------------------------------
# Tests: get_map_name
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestGetMapName:
    """Tests for map name extraction from tile filenames."""

    def test_standard_format(self):
        assert get_map_name("K-35-052-4_32635_x0_y0.png") == (
            "K-35-052-4_32635"
        )

    def test_long_map_name(self):
        assert get_map_name(
            "K-35-053-3_Elenovo_x336_y672.png"
        ) == "K-35-053-3_Elenovo"

    def test_no_match_returns_unknown(self):
        assert get_map_name("not_a_tile.txt") == "Unknown"


# ---------------------------------------------------------------------------
# Tests: enrich_bounds_with_mound_counts
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestEnrichBoundsWithMoundCounts:
    """Tests for tile enrichment via spatial join."""

    def test_correct_mound_counts(self, spatial_bounds_and_refs, tmp_path):
        """Spatial join assigns correct mound counts per tile."""
        bounds, refs = spatial_bounds_and_refs

        bounds_path = tmp_path / "bounds.geojson"
        bounds.to_file(bounds_path, driver="GeoJSON")
        ref_path = tmp_path / "refs.geojson"
        refs.to_file(ref_path, driver="GeoJSON")

        enriched = enrich_bounds_with_mound_counts(bounds_path, ref_path)

        counts = dict(zip(
            enriched["tile_name"], enriched["mound_count"]
        ))
        assert counts["test_map_x0_y0.png"] == 0
        assert counts["test_map_x100_y0.png"] == 2
        assert counts["test_map_x200_y0.png"] == 4

    def test_density_assigned(self, spatial_bounds_and_refs, tmp_path):
        """Density categories match the mound counts."""
        bounds, refs = spatial_bounds_and_refs
        bounds_path = tmp_path / "bounds.geojson"
        bounds.to_file(bounds_path, driver="GeoJSON")
        ref_path = tmp_path / "refs.geojson"
        refs.to_file(ref_path, driver="GeoJSON")

        enriched = enrich_bounds_with_mound_counts(bounds_path, ref_path)

        densities = dict(zip(
            enriched["tile_name"], enriched["density"]
        ))
        assert densities["test_map_x0_y0.png"] == "empty"
        assert densities["test_map_x100_y0.png"] == "sparse"
        assert densities["test_map_x200_y0.png"] == "dense"

    def test_map_name_extracted(self, spatial_bounds_and_refs, tmp_path):
        """Map name is extracted from tile_name."""
        bounds, refs = spatial_bounds_and_refs
        bounds_path = tmp_path / "bounds.geojson"
        bounds.to_file(bounds_path, driver="GeoJSON")
        ref_path = tmp_path / "refs.geojson"
        refs.to_file(ref_path, driver="GeoJSON")

        enriched = enrich_bounds_with_mound_counts(bounds_path, ref_path)
        assert all(enriched["map_name"] == "test_map")


# ---------------------------------------------------------------------------
# Tests: stratified_sample
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestStratifiedSample:
    """Tests for hierarchical stratified sampling."""

    def test_returns_correct_count(self, four_map_tiles):
        """Selected count matches requested n."""
        result = stratified_sample(four_map_tiles, 40, seed=42)
        assert len(result) == 40

    def test_geographic_balance(self, four_map_tiles):
        """With per_map_equal=True, each map gets ~equal share."""
        result = stratified_sample(four_map_tiles, 40, seed=42)
        per_map = result["map_name"].value_counts()
        # 40 tiles / 4 maps = 10 each
        assert all(per_map == 10), (
            f"Expected 10 per map, got {per_map.to_dict()}"
        )

    def test_density_representation(self, four_map_tiles):
        """All three density strata should be represented in output."""
        result = stratified_sample(four_map_tiles, 40, seed=42)
        densities = set(result["density"].unique())
        assert densities == {"empty", "sparse", "dense"}

    def test_reproducibility(self, four_map_tiles):
        """Same seed produces identical selection."""
        r1 = stratified_sample(four_map_tiles, 40, seed=123)
        r2 = stratified_sample(four_map_tiles, 40, seed=123)
        assert list(r1.index) == list(r2.index)

    def test_different_seeds_differ(self, four_map_tiles):
        """Different seeds produce different selections."""
        r1 = stratified_sample(four_map_tiles, 40, seed=1)
        r2 = stratified_sample(four_map_tiles, 40, seed=2)
        assert list(r1.index) != list(r2.index)

    def test_exceeding_available_raises(self, four_map_tiles):
        """Requesting more tiles than available raises ValueError."""
        with pytest.raises(ValueError, match="only.*available"):
            stratified_sample(four_map_tiles, 999, seed=42)

    def test_zero_returns_empty(self, four_map_tiles):
        """Requesting 0 tiles returns empty DataFrame."""
        result = stratified_sample(four_map_tiles, 0, seed=42)
        assert len(result) == 0

    def test_surplus_redistributed_when_map_too_small(self):
        """When one map has fewer tiles than allocated, surplus goes
        to other maps so the total still equals n."""
        # MapA: 3 tiles, MapB: 50 tiles — request 20 total
        # Equal allocation gives 10 each, but MapA has only 3.
        # Surplus (7) should go to MapB → MapA=3, MapB=17, total=20.
        rows = []
        for i in range(3):
            rows.append({
                "tile_name": f"MapA_x{i * 336}_y0.png",
                "map_name": "MapA",
                "density": "sparse",
                "mound_count": 1,
            })
        for i in range(50):
            rows.append({
                "tile_name": f"MapB_x{i * 336}_y0.png",
                "map_name": "MapB",
                "density": "dense" if i < 25 else "sparse",
                "mound_count": 4 if i < 25 else 1,
            })
        df = pd.DataFrame(rows)

        result = stratified_sample(df, 20, seed=42)
        assert len(result) == 20, (
            f"Expected 20 tiles after redistribution, got {len(result)}"
        )
        per_map = result["map_name"].value_counts()
        assert per_map["MapA"] == 3
        assert per_map["MapB"] == 17


# ---------------------------------------------------------------------------
# Tests: nested_subsample
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestNestedSubsample:
    """Tests for nested subsampling (H10 pool nesting)."""

    def test_child_is_subset_of_parent(self, four_map_tiles):
        """Child pool indices are a strict subset of parent."""
        parent = stratified_sample(four_map_tiles, 80, seed=42)
        child = nested_subsample(parent, 40, seed=43)

        assert set(child.index).issubset(set(parent.index))

    def test_nesting_chain(self, four_map_tiles):
        """Full nesting chain A ⊂ B ⊂ C ⊂ D holds."""
        d = stratified_sample(four_map_tiles, 160, seed=42)
        c = nested_subsample(d, 80, seed=43)
        b = nested_subsample(c, 40, seed=44)
        a = nested_subsample(b, 20, seed=45)

        assert len(d) == 160
        assert len(c) == 80
        assert len(b) == 40
        assert len(a) == 20

        assert set(a.index).issubset(set(b.index))
        assert set(b.index).issubset(set(c.index))
        assert set(c.index).issubset(set(d.index))

    def test_child_preserves_density(self, four_map_tiles):
        """Child pool should roughly preserve parent density ratios."""
        parent = stratified_sample(four_map_tiles, 80, seed=42)
        child = nested_subsample(parent, 40, seed=43)

        parent_ratios = parent["density"].value_counts(normalize=True)
        child_ratios = child["density"].value_counts(normalize=True)

        for density in parent_ratios.index:
            if density in child_ratios.index:
                diff = abs(
                    parent_ratios[density] - child_ratios[density]
                )
                assert diff < 0.20, (
                    f"Density '{density}' ratio diff {diff:.2f} > 0.20"
                )

    def test_exceeding_parent_raises(self, four_map_tiles):
        """Child larger than parent raises ValueError."""
        parent = stratified_sample(four_map_tiles, 40, seed=42)
        with pytest.raises(ValueError, match="exceeds parent"):
            nested_subsample(parent, 80, seed=43)

    def test_equal_size_returns_copy(self, four_map_tiles):
        """Child same size as parent returns full copy."""
        parent = stratified_sample(four_map_tiles, 40, seed=42)
        child = nested_subsample(parent, 40, seed=43)
        assert len(child) == len(parent)
        assert set(child.index) == set(parent.index)


# ---------------------------------------------------------------------------
# Tests: difficulty scoring
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestScoreDifficultyHP:
    """Tests for hard-positive difficulty scoring."""

    def test_range_zero_to_one(self):
        """Scores should always be in [0.0, 1.0]."""
        for vote in range(6):
            score = score_difficulty_hp(vote, 5, match_distance=10.0)
            assert 0.0 <= score <= 1.0, (
                f"vote={vote}: score={score} out of range"
            )

    def test_fn_scores_highest(self):
        """A mound never detected (0/5) should score highest."""
        fn = score_difficulty_hp(0, 5)
        borderline = score_difficulty_hp(2, 5)
        easy = score_difficulty_hp(5, 5)

        assert fn > borderline > easy

    def test_distance_increases_score(self):
        """Near-threshold match scores higher than close match."""
        close = score_difficulty_hp(3, 5, match_distance=2.0)
        far = score_difficulty_hp(3, 5, match_distance=18.0)

        assert far > close

    def test_zero_passes_returns_zero(self):
        """Edge case: k_passes=0 returns 0.0."""
        assert score_difficulty_hp(0, 0) == 0.0


@pytest.mark.tier1
class TestScoreDifficultyHN:
    """Tests for hard-negative difficulty scoring."""

    def test_range_zero_to_one(self):
        """Scores should always be in [0.0, 1.0]."""
        for vote in range(6):
            score = score_difficulty_hn(vote, 5, nearest_ref_distance=100)
            assert 0.0 <= score <= 1.0, (
                f"vote={vote}: score={score} out of range"
            )

    def test_consistent_fp_scores_highest(self):
        """An FP appearing every pass (5/5) should score highest."""
        consistent = score_difficulty_hn(5, 5, nearest_ref_distance=500)
        sporadic = score_difficulty_hn(2, 5, nearest_ref_distance=500)
        rare = score_difficulty_hn(1, 5, nearest_ref_distance=500)

        assert consistent > sporadic > rare

    def test_isolation_increases_score(self):
        """FP far from any GT mound scores higher than near-miss."""
        near = score_difficulty_hn(3, 5, nearest_ref_distance=10)
        far = score_difficulty_hn(3, 5, nearest_ref_distance=800)

        assert far > near

    def test_zero_passes_returns_zero(self):
        """Edge case: k_passes=0 returns 0.0."""
        assert score_difficulty_hn(0, 0) == 0.0
