"""Tier 1 unit tests for build_example_pool.py.

Tests diversity-optimised selection logic and output writing.
No real rasters or file I/O beyond tmp_path.
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from build_example_pool import (  # noqa: E402
    _get_source_tile,
    select_diverse_examples,
    write_outputs,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def hp_candidates():
    """10 HP candidates on 2 maps, varying difficulty and location."""
    return [
        {"x": 100, "y": 100, "difficulty_score": 0.95,
         "map_name": "MapA", "ref_index": 0, "classification": "consistent_fn"},
        {"x": 120, "y": 110, "difficulty_score": 0.90,
         "map_name": "MapA", "ref_index": 1, "classification": "consistent_fn"},
        {"x": 5000, "y": 5000, "difficulty_score": 0.85,
         "map_name": "MapB", "ref_index": 2, "classification": "borderline_tp"},
        {"x": 200, "y": 200, "difficulty_score": 0.80,
         "map_name": "MapA", "ref_index": 3, "classification": "borderline_tp"},
        {"x": 5100, "y": 5100, "difficulty_score": 0.75,
         "map_name": "MapB", "ref_index": 4, "classification": "borderline_tp"},
        {"x": 300, "y": 300, "difficulty_score": 0.70,
         "map_name": "MapA", "ref_index": 5, "classification": "borderline_tp"},
        {"x": 5200, "y": 5200, "difficulty_score": 0.65,
         "map_name": "MapB", "ref_index": 6, "classification": "borderline_tp"},
        {"x": 400, "y": 400, "difficulty_score": 0.60,
         "map_name": "MapA", "ref_index": 7, "classification": "borderline_tp"},
        {"x": 5300, "y": 5300, "difficulty_score": 0.55,
         "map_name": "MapB", "ref_index": 8, "classification": "borderline_tp"},
        {"x": 500, "y": 500, "difficulty_score": 0.50,
         "map_name": "MapA", "ref_index": 9, "classification": "borderline_tp"},
    ]


@pytest.fixture
def hn_candidates():
    """6 HN candidates with source_tiles."""
    return [
        {"x": 800, "y": 800, "difficulty_score": 0.88,
         "map_name": "MapA", "source_tiles": ["MapA_x0_y0.png"],
         "classification": "consistent_fp"},
        {"x": 810, "y": 810, "difficulty_score": 0.82,
         "map_name": "MapA", "source_tiles": ["MapA_x0_y0.png"],
         "classification": "consistent_fp"},
        {"x": 6000, "y": 6000, "difficulty_score": 0.76,
         "map_name": "MapB", "source_tiles": ["MapB_x0_y0.png"],
         "classification": "consistent_fp"},
        {"x": 900, "y": 900, "difficulty_score": 0.70,
         "map_name": "MapA", "source_tiles": ["MapA_x336_y0.png"],
         "classification": "consistent_fp"},
        {"x": 6100, "y": 6100, "difficulty_score": 0.64,
         "map_name": "MapB", "source_tiles": ["MapB_x336_y0.png"],
         "classification": "consistent_fp"},
        {"x": 1000, "y": 1000, "difficulty_score": 0.58,
         "map_name": "MapA", "source_tiles": ["MapA_x672_y0.png"],
         "classification": "consistent_fp"},
    ]


# ---------------------------------------------------------------------------
# Tests: select_diverse_examples
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestSelectDiverseExamples:
    """Tests for diversity-optimised selection."""

    def test_returns_correct_count(self, hp_candidates):
        """Selected count matches requested."""
        result = select_diverse_examples(hp_candidates, 4, seed=42)
        assert len(result) == 4

    def test_returns_fewer_if_insufficient(self, hp_candidates):
        """Returns all available if fewer than requested."""
        result = select_diverse_examples(hp_candidates, 20, seed=42)
        assert len(result) == 10

    def test_empty_candidates_returns_empty(self):
        """Empty input → empty output."""
        result = select_diverse_examples([], 5, seed=42)
        assert result == []

    def test_zero_count_returns_empty(self, hp_candidates):
        """Zero requested → empty output."""
        result = select_diverse_examples(hp_candidates, 0, seed=42)
        assert result == []

    def test_highest_scored_selected_first(self, hp_candidates):
        """First selected should be the highest difficulty score."""
        result = select_diverse_examples(hp_candidates, 1, seed=42)
        assert result[0]["difficulty_score"] == 0.95

    def test_spatial_penalty_spreads_selection(self, hp_candidates):
        """Nearby candidates should be deprioritised.

        Candidates at (100,100) and (120,110) are ~28m apart (within
        500m penalty radius). After selecting (100,100), the (120,110)
        candidate should be penalised and less likely to be next.
        """
        result = select_diverse_examples(hp_candidates, 4, seed=42)
        # The second selected should NOT be (120,110) despite it being
        # the second-highest scorer — spatial penalty should push it down
        second = result[1]
        assert not (second["x"] == 120 and second["y"] == 110), (
            "Second selection should not be the spatially adjacent "
            "candidate due to diversity penalty"
        )

    def test_same_tile_heavily_penalised(self, hn_candidates):
        """Two HNs from the same tile should rarely both be selected.

        Candidates at (800,800) and (810,810) are on the same tile
        (MapA_x0_y0.png). The second should be heavily penalised
        after the first is selected.
        """
        result = select_diverse_examples(hn_candidates, 3, seed=42)
        tiles = [_get_source_tile(r) for r in result]
        # With 3 selections from 3+ tiles, we shouldn't see the same
        # tile twice
        assert len(set(tiles)) == len(tiles), (
            f"Expected unique tiles in top-3, got {tiles}"
        )

    def test_no_internal_fields_in_output(self, hp_candidates):
        """Internal _adj_score and _source_tile stripped from output."""
        result = select_diverse_examples(hp_candidates, 3, seed=42)
        for r in result:
            assert "_adj_score" not in r
            assert "_source_tile" not in r


# ---------------------------------------------------------------------------
# Tests: _get_source_tile
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestGetSourceTile:
    """Tests for source tile extraction."""

    def test_from_source_tiles_list(self):
        assert _get_source_tile(
            {"source_tiles": ["MapA_x0_y0.png"]}
        ) == "MapA_x0_y0.png"

    def test_fallback_to_grid_id(self):
        """HP candidates without source_tiles get a grid-based ID."""
        result = _get_source_tile(
            {"map_name": "MapA", "x": 500, "y": 1000}
        )
        # Should include map name and grid coordinates, not just map
        assert "MapA" in result
        assert result != "MapA"  # More specific than just map name

    def test_empty_source_tiles_uses_grid(self):
        """Empty source_tiles falls back to grid ID, not map name."""
        result = _get_source_tile(
            {"source_tiles": [], "map_name": "MapB", "x": 0, "y": 0}
        )
        assert "MapB" in result
        assert result != "MapB"

    def test_same_grid_cell_same_id(self):
        """Two candidates in the same grid cell get the same ID."""
        id_a = _get_source_tile(
            {"map_name": "M", "x": 100, "y": 100}
        )
        id_b = _get_source_tile(
            {"map_name": "M", "x": 200, "y": 200}
        )
        assert id_a == id_b  # Both in grid cell (0, 0)

    def test_different_grid_cell_different_id(self):
        """Candidates in different grid cells get different IDs."""
        id_a = _get_source_tile(
            {"map_name": "M", "x": 100, "y": 100}
        )
        id_b = _get_source_tile(
            {"map_name": "M", "x": 5000, "y": 5000}
        )
        assert id_a != id_b


# ---------------------------------------------------------------------------
# Tests: write_outputs
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestWriteOutputs:
    """Tests for output file writing."""

    def test_creates_expected_files(self, tmp_path):
        """Both output files should be created."""
        write_outputs(
            hp_selected=[{"x": 1, "y": 2, "difficulty_score": 0.9}],
            hn_selected=[{"x": 3, "y": 4, "difficulty_score": 0.8}],
            output_dir=tmp_path,
            metadata={"seed": 42},
        )
        assert (tmp_path / "selected_examples.json").exists()
        assert (tmp_path / "pool_metadata.json").exists()

    def test_examples_json_structure(self, tmp_path):
        """Examples JSON should have hard_positives and hard_negatives."""
        hp = [{"x": 1, "y": 2, "difficulty_score": 0.9}]
        hn = [{"x": 3, "y": 4, "difficulty_score": 0.8}]
        write_outputs(hp, hn, tmp_path, {"seed": 42})

        data = json.loads(
            (tmp_path / "selected_examples.json").read_text()
        )
        assert len(data["hard_positives"]) == 1
        assert len(data["hard_negatives"]) == 1
