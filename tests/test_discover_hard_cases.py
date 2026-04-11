"""Tier 1 unit tests for discover_hard_cases.py.

Tests hard-case classification, mound register construction, FP
clustering, difficulty scoring, and output writing — all with synthetic
spatial data. No real detection files or API calls.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import MultiPoint, Point, box

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from discover_hard_cases import (  # noqa: E402
    _build_fp_register,
    _build_mound_register,
    _build_summary,
    _deduped_to_gdf,
    _detect_ref_map_col,
    write_outputs,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


CRS = "EPSG:32635"


@pytest.fixture
def simple_refs():
    """3 reference mounds on one map, scoped to one tile."""
    return gpd.GeoDataFrame(
        {"Map": ["TestMap"] * 3},
        geometry=[
            MultiPoint([Point(100, 100)]),
            MultiPoint([Point(200, 200)]),
            MultiPoint([Point(300, 300)]),
        ],
        crs=CRS,
    )


@pytest.fixture
def simple_bounds():
    """Single tile covering the reference area."""
    return gpd.GeoDataFrame(
        {"tile_name": ["TestMap_x0_y0.png"]},
        geometry=[box(0, 0, 500, 500)],
        crs=CRS,
    )


@pytest.fixture
def mound_votes_all_detected():
    """All 3 mounds detected in all 5 passes (consistent TPs)."""
    return {
        "TestMap": {
            0: [(i, 5.0) for i in range(5)],  # R0: 5/5, 5m away
            1: [(i, 3.0) for i in range(5)],  # R1: 5/5, 3m away
            2: [(i, 8.0) for i in range(5)],  # R2: 5/5, 8m away
        },
    }


@pytest.fixture
def mound_votes_mixed():
    """R0: consistent TP (5/5), R1: borderline (2/5), R2: FN (0/5)."""
    return {
        "TestMap": {
            0: [(i, 5.0) for i in range(5)],
            1: [(0, 12.0), (3, 15.0)],
            2: [],
        },
    }


@pytest.fixture
def scoped_refs(simple_refs):
    """Scoped references keyed by map name."""
    return {"TestMap": simple_refs}


# ---------------------------------------------------------------------------
# Tests: _detect_ref_map_col
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestDetectRefMapCol:
    """Tests for reference map column detection."""

    def test_detects_map_column(self, simple_refs):
        assert _detect_ref_map_col(simple_refs) == "Map"

    def test_detects_source_map(self):
        gdf = gpd.GeoDataFrame(
            {"source_map": ["M1"]},
            geometry=[Point(0, 0)],
            crs=CRS,
        )
        assert _detect_ref_map_col(gdf) == "source_map"

    def test_missing_column_raises(self):
        gdf = gpd.GeoDataFrame(
            {"other": ["x"]},
            geometry=[Point(0, 0)],
            crs=CRS,
        )
        with pytest.raises(ValueError, match="no 'Map'"):
            _detect_ref_map_col(gdf)


# ---------------------------------------------------------------------------
# Tests: _deduped_to_gdf
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestDedupedToGdf:
    """Tests for converting deduplicated dicts to GeoDataFrame."""

    def test_converts_correctly(self):
        deduped = [
            {
                "centroid": (100.0, 200.0),
                "label": "burial_mound",
                "source_tiles": ["tile_x0_y0.png"],
            },
        ]
        gdf = _deduped_to_gdf(deduped, CRS)
        assert len(gdf) == 1
        assert gdf.iloc[0]["source_tile"] == "tile_x0_y0.png"
        assert gdf.geometry.iloc[0].x == 100.0

    def test_empty_returns_empty_gdf(self):
        gdf = _deduped_to_gdf([], CRS)
        assert len(gdf) == 0
        assert "source_tile" in gdf.columns


# ---------------------------------------------------------------------------
# Tests: _build_mound_register
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestBuildMoundRegister:
    """Tests for mound register classification."""

    def test_all_consistent_tp(
        self, mound_votes_all_detected, scoped_refs,
    ):
        """All mounds detected in all passes → consistent_tp."""
        register = _build_mound_register(
            mound_votes_all_detected, scoped_refs,
            k_passes=5, buffer_metres=20,
        )
        assert len(register) == 3
        assert all(
            m["classification"] == "consistent_tp" for m in register
        )

    def test_mixed_classifications(
        self, mound_votes_mixed, scoped_refs,
    ):
        """Mixed votes → correct classification per mound."""
        register = _build_mound_register(
            mound_votes_mixed, scoped_refs,
            k_passes=5, buffer_metres=20,
        )
        classes = {m["ref_index"]: m["classification"] for m in register}
        # R0: 5/5 → consistent_tp
        # R1: 2/5 → borderline_tp
        # R2: 0/5 → consistent_fn
        assert classes[0] == "consistent_tp"
        assert classes[1] == "borderline_tp"
        assert classes[2] == "consistent_fn"

    def test_difficulty_ordering(
        self, mound_votes_mixed, scoped_refs,
    ):
        """Harder cases should have higher difficulty scores."""
        register = _build_mound_register(
            mound_votes_mixed, scoped_refs,
            k_passes=5, buffer_metres=20,
        )
        scores = {m["ref_index"]: m["difficulty_score"] for m in register}
        # FN (0/5) > borderline (2/5) > consistent TP (5/5)
        assert scores[2] > scores[1] > scores[0]

    def test_vote_counts_correct(
        self, mound_votes_mixed, scoped_refs,
    ):
        """Vote counts match the input data."""
        register = _build_mound_register(
            mound_votes_mixed, scoped_refs,
            k_passes=5, buffer_metres=20,
        )
        votes = {m["ref_index"]: m["vote_count"] for m in register}
        assert votes[0] == 5
        assert votes[1] == 2
        assert votes[2] == 0

    def test_coordinates_from_reference(
        self, mound_votes_mixed, scoped_refs,
    ):
        """Coordinates should come from reference mound locations."""
        register = _build_mound_register(
            mound_votes_mixed, scoped_refs,
            k_passes=5, buffer_metres=20,
        )
        r0 = next(m for m in register if m["ref_index"] == 0)
        assert r0["x"] == 100.0
        assert r0["y"] == 100.0


# ---------------------------------------------------------------------------
# Tests: _build_fp_register
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestBuildFpRegister:
    """Tests for FP cluster register construction."""

    def test_empty_unmatched_returns_empty(self, scoped_refs):
        """No unmatched features → empty register."""
        result = _build_fp_register({}, scoped_refs, 5)
        assert result == []

    def test_consistent_fp_classified(self, scoped_refs):
        """FP appearing in ≥3 passes → consistent_fp."""
        # Same location from 4 passes
        unmatched = {}
        for i in range(4):
            unmatched[f"run_{i+1}"] = [{
                "centroid": (400.0, 400.0),
                "label": "burial_mound",
                "source_tiles": ["TestMap_x0_y0.png"],
            }]

        result = _build_fp_register(
            unmatched, scoped_refs, 5,
        )
        assert len(result) >= 1
        # The FP cluster should have vote_count=4
        fp = result[0]
        assert fp["vote_count"] == 4
        assert fp["classification"] == "consistent_fp"

    def test_sporadic_fp_classified(self, scoped_refs):
        """FP appearing in 1 pass → sporadic_fp."""
        unmatched = {
            "run_1": [{
                "centroid": (450.0, 450.0),
                "label": "unknown",
                "source_tiles": ["TestMap_x0_y0.png"],
            }],
        }
        result = _build_fp_register(
            unmatched, scoped_refs, 5,
        )
        assert len(result) == 1
        assert result[0]["classification"] == "sporadic_fp"

    def test_nearest_ref_distance_computed(self, scoped_refs):
        """Nearest GT distance should be computed for FPs."""
        unmatched = {
            "run_1": [{
                "centroid": (400.0, 400.0),
                "label": "mound",
                "source_tiles": ["TestMap_x0_y0.png"],
            }],
        }
        result = _build_fp_register(
            unmatched, scoped_refs, 5,
        )
        assert result[0]["nearest_ref_distance"] is not None
        # Nearest GT is at (300, 300), distance = √(100² + 100²) ≈ 141m
        assert 140 < result[0]["nearest_ref_distance"] < 143


# ---------------------------------------------------------------------------
# Tests: _build_summary
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestBuildSummary:
    """Tests for summary construction."""

    def test_counts_correct(self):
        mounds = [
            {"classification": "consistent_tp"},
            {"classification": "consistent_tp"},
            {"classification": "borderline_tp"},
            {"classification": "consistent_fn"},
        ]
        fps = [
            {"classification": "consistent_fp"},
            {"classification": "sporadic_fp"},
            {"classification": "sporadic_fp"},
        ]
        summary = _build_summary(mounds, fps)
        assert summary["total_gt_mounds"] == 4
        assert summary["consistent_tp"] == 2
        assert summary["borderline_tp"] == 1
        assert summary["consistent_fn"] == 1
        assert summary["total_fp_clusters"] == 3
        assert summary["consistent_fp"] == 1
        assert summary["sporadic_fp"] == 2
        assert summary["hp_candidates"] == 2  # borderline + fn
        assert summary["hn_candidates"] == 1  # consistent_fp only


# ---------------------------------------------------------------------------
# Tests: write_outputs
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestWriteOutputs:
    """Tests for output file writing."""

    def test_creates_all_files(self, tmp_path):
        """All expected output files are created."""
        result = {
            "mound_register": [
                {
                    "map_name": "M", "ref_index": 0,
                    "x": 100, "y": 100, "vote_count": 3,
                    "k_passes": 5, "mean_match_distance": 5.0,
                    "min_match_distance": 3.0,
                    "classification": "borderline_tp",
                    "difficulty_score": 0.58,
                },
            ],
            "fp_register": [
                {
                    "map_name": "M", "x": 400, "y": 400,
                    "vote_count": 4, "k_passes": 5,
                    "nearest_ref_distance": 100.0,
                    "source_tiles": ["t1"],
                    "subtype": "mound",
                    "classification": "consistent_fp",
                    "difficulty_score": 0.59,
                },
            ],
            "k_passes": 5,
            "summary": _build_summary(
                [{"classification": "borderline_tp"}],
                [{"classification": "consistent_fp"}],
            ),
        }
        write_outputs(result, tmp_path)

        expected = [
            "hard_cases_register.json",
            "hard_positive_candidates.json",
            "hard_negative_candidates.json",
            "discovery_summary.json",
        ]
        for fname in expected:
            assert (tmp_path / fname).exists(), f"Missing: {fname}"

    def test_hp_sorted_by_difficulty(self, tmp_path):
        """HP candidates should be sorted hardest-first."""
        result = {
            "mound_register": [
                {
                    "classification": "borderline_tp",
                    "difficulty_score": 0.3,
                    "map_name": "M", "ref_index": 0,
                    "x": 0, "y": 0, "vote_count": 3,
                    "k_passes": 5, "mean_match_distance": 5.0,
                    "min_match_distance": 3.0,
                },
                {
                    "classification": "consistent_fn",
                    "difficulty_score": 0.9,
                    "map_name": "M", "ref_index": 1,
                    "x": 0, "y": 0, "vote_count": 0,
                    "k_passes": 5, "mean_match_distance": None,
                    "min_match_distance": None,
                },
            ],
            "fp_register": [],
            "k_passes": 5,
            "summary": _build_summary(
                [
                    {"classification": "borderline_tp"},
                    {"classification": "consistent_fn"},
                ],
                [],
            ),
        }
        write_outputs(result, tmp_path)

        hp = json.loads(
            (tmp_path / "hard_positive_candidates.json").read_text()
        )
        assert len(hp) == 2
        # Hardest first
        assert hp[0]["difficulty_score"] > hp[1]["difficulty_score"]
