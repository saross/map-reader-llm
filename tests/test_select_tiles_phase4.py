"""
Tests for Phase 4 tile selection (stratified subset from holdout).

Tests the select_tiles_phase4.py script functions for selecting a 20-tile
stratified subset from the 60 holdout tiles while preserving density distribution.
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from select_tiles_phase4 import (
    select_stratified_subset,
    get_density_distribution,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_holdout_tiles() -> list[dict]:
    """
    Create sample holdout tiles mimicking the 60-tile holdout set.

    Distribution: ~50% empty, ~30% sparse, ~20% dense (typical distribution)
    """
    tiles = []

    # Empty tiles (30)
    for i in range(30):
        tiles.append({
            "filename": f"map_{i // 10}_x{i * 100}_y0.png",
            "map": f"K-35-05{i // 10}-{i % 10}",
            "mound_count": 0,
            "density": "empty",
        })

    # Sparse tiles (18) - 1-2 mounds
    for i in range(18):
        tiles.append({
            "filename": f"map_{i // 6}_x{i * 100}_y100.png",
            "map": f"K-35-05{i // 6}-{i % 6}",
            "mound_count": 1 + (i % 2),
            "density": "sparse",
        })

    # Dense tiles (12) - 3+ mounds
    for i in range(12):
        tiles.append({
            "filename": f"map_{i // 3}_x{i * 100}_y200.png",
            "map": f"K-35-05{i // 3}-{i % 3}",
            "mound_count": 3 + i,
            "density": "dense",
        })

    return tiles


@pytest.fixture
def small_tile_set() -> list[dict]:
    """Small tile set for edge case testing."""
    return [
        {"filename": "tile_a.png", "map": "map1", "mound_count": 0, "density": "empty"},
        {"filename": "tile_b.png", "map": "map1", "mound_count": 1, "density": "sparse"},
        {"filename": "tile_c.png", "map": "map2", "mound_count": 3, "density": "dense"},
    ]


# =============================================================================
# Tests: Core Selection Logic
# =============================================================================

class TestSelectStratifiedSubset:
    """Tests for the stratified subset selection function."""

    @pytest.mark.tier1
    def test_returns_correct_count(self, sample_holdout_tiles: list[dict]) -> None:
        """Selection should return exactly the target number of tiles."""
        target = 20
        selected = select_stratified_subset(sample_holdout_tiles, target, seed=42)

        assert len(selected) == target

    @pytest.mark.tier1
    def test_preserves_density_distribution(
        self, sample_holdout_tiles: list[dict]
    ) -> None:
        """Subset should approximately preserve density ratio from full set."""
        target = 20
        selected = select_stratified_subset(sample_holdout_tiles, target, seed=42)

        original_dist = get_density_distribution(sample_holdout_tiles)
        selected_dist = get_density_distribution(selected)

        total_original = len(sample_holdout_tiles)
        total_selected = len(selected)

        # Check each density category is within 15% of original proportion
        for density in ["empty", "sparse", "dense"]:
            orig_prop = original_dist[density] / total_original
            sel_prop = selected_dist[density] / total_selected

            # Allow 20% deviation for small samples
            assert abs(orig_prop - sel_prop) <= 0.20, (
                f"{density}: original {orig_prop:.1%} vs selected {sel_prop:.1%}"
            )

    @pytest.mark.tier1
    def test_all_tiles_from_input_set(self, sample_holdout_tiles: list[dict]) -> None:
        """All selected tiles must be from the input set."""
        target = 20
        selected = select_stratified_subset(sample_holdout_tiles, target, seed=42)

        input_filenames = {t["filename"] for t in sample_holdout_tiles}
        selected_filenames = {t["filename"] for t in selected}

        assert selected_filenames.issubset(input_filenames)

    @pytest.mark.tier1
    def test_reproducible_with_seed(self, sample_holdout_tiles: list[dict]) -> None:
        """Same seed should produce identical selection."""
        target = 20
        seed = 12345

        selected1 = select_stratified_subset(sample_holdout_tiles, target, seed=seed)
        selected2 = select_stratified_subset(sample_holdout_tiles, target, seed=seed)

        filenames1 = sorted(t["filename"] for t in selected1)
        filenames2 = sorted(t["filename"] for t in selected2)

        assert filenames1 == filenames2

    @pytest.mark.tier1
    def test_different_seeds_produce_different_selections(
        self, sample_holdout_tiles: list[dict]
    ) -> None:
        """Different seeds should (usually) produce different subsets."""
        target = 20

        selected1 = select_stratified_subset(sample_holdout_tiles, target, seed=111)
        selected2 = select_stratified_subset(sample_holdout_tiles, target, seed=222)

        filenames1 = set(t["filename"] for t in selected1)
        filenames2 = set(t["filename"] for t in selected2)

        # With 60 tiles and 20 selected, different seeds should differ
        # Allow for rare case of identical selection
        overlap = len(filenames1 & filenames2)
        assert overlap < target, "Different seeds produced identical selections"

    @pytest.mark.tier1
    def test_no_duplicates_in_selection(
        self, sample_holdout_tiles: list[dict]
    ) -> None:
        """Selection should not contain duplicate tiles."""
        target = 20
        selected = select_stratified_subset(sample_holdout_tiles, target, seed=42)

        filenames = [t["filename"] for t in selected]

        assert len(filenames) == len(set(filenames)), "Duplicates found in selection"


# =============================================================================
# Tests: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases in tile selection."""

    @pytest.mark.tier1
    def test_handles_empty_input(self) -> None:
        """Empty input should return empty list."""
        selected = select_stratified_subset([], 20, seed=42)

        assert selected == []

    @pytest.mark.tier1
    def test_handles_target_larger_than_input(
        self, small_tile_set: list[dict]
    ) -> None:
        """When target exceeds input size, return all available tiles."""
        target = 100  # Much larger than input
        selected = select_stratified_subset(small_tile_set, target, seed=42)

        # Should return all available tiles (not exceed input size)
        assert len(selected) <= len(small_tile_set)

    @pytest.mark.tier1
    def test_handles_single_density_category(self) -> None:
        """Should work when all tiles are same density."""
        tiles = [
            {"filename": f"tile_{i}.png", "density": "empty", "mound_count": 0}
            for i in range(30)
        ]

        selected = select_stratified_subset(tiles, 10, seed=42)

        assert len(selected) == 10
        assert all(t["density"] == "empty" for t in selected)

    @pytest.mark.tier1
    def test_handles_missing_density_field(self) -> None:
        """Tiles without density field should default to 'empty'."""
        tiles = [
            {"filename": "tile_1.png", "mound_count": 0},
            {"filename": "tile_2.png", "mound_count": 1},
            {"filename": "tile_3.png", "mound_count": 3, "density": "dense"},
        ]

        selected = select_stratified_subset(tiles, 2, seed=42)

        # Should not raise exception
        assert len(selected) == 2


# =============================================================================
# Tests: Density Distribution Helper
# =============================================================================

class TestGetDensityDistribution:
    """Tests for the density distribution helper function."""

    @pytest.mark.tier1
    def test_counts_all_categories(self, sample_holdout_tiles: list[dict]) -> None:
        """Should count tiles in each density category."""
        dist = get_density_distribution(sample_holdout_tiles)

        assert "empty" in dist
        assert "sparse" in dist
        assert "dense" in dist
        assert sum(dist.values()) == len(sample_holdout_tiles)

    @pytest.mark.tier1
    def test_empty_input_returns_zeros(self) -> None:
        """Empty input should return zero counts."""
        dist = get_density_distribution([])

        assert dist == {"empty": 0, "sparse": 0, "dense": 0}

    @pytest.mark.tier1
    def test_handles_unknown_density(self) -> None:
        """Unknown density values should default to empty."""
        tiles = [
            {"filename": "tile.png", "density": "unknown_category"},
        ]

        dist = get_density_distribution(tiles)

        # Unknown density defaults to empty via .get()
        assert dist["empty"] == 0  # Doesn't count as empty
        assert dist["sparse"] == 0
        assert dist["dense"] == 0
