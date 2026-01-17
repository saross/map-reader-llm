"""
Tests for preregistration compliance.

Tier 1 tests verifying that experimental parameters match the preregistered
values. These tests act as methodology flags - a failing test indicates a
potential deviation from the registered study protocol.

Preregistration reference: OSF registration (see docs/methodology/preregistration/)
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import match_detections_to_references
from shapely.geometry import Point

# =============================================================================
# PREREGISTERED VALUES
# =============================================================================
# These values are locked by the preregistration. Tests enforce compliance.

PREREGISTERED_SEED = 1766464625  # Random seed for tile selection
PREREGISTERED_CRS = 32635  # EPSG code for UTM Zone 35N (Bulgaria)
PREREGISTERED_TILE_SIZE = 512  # Tile dimensions in pixels
PREREGISTERED_STRIDE = 448  # Distance between tile origins (TILE_SIZE - OVERLAP)
PREREGISTERED_SPATIAL_TOLERANCE = 20  # Metres for F1 matching


@pytest.mark.tier1
@pytest.mark.compliance
class TestTileSelectionSeed:
    """Tests for tile selection random seed compliance."""

    def test_calibration_seed_matches_preregistration(
        self, tile_selection_metadata: dict
    ) -> None:
        """Verify calibration tile selection used the preregistered random seed.

        The random seed ensures reproducible tile selection. The preregistration
        documents two separate selection events:
        - Calibration tiles: seed 1766464625, selected 2025-12-23
        - Holdout tiles: seed 1767425239, selected 2026-01-03

        This test verifies the calibration seed matches the preregistered value.
        """
        calibration = tile_selection_metadata.get("calibration", {})
        actual_seed = calibration.get("random_seed")

        assert actual_seed == PREREGISTERED_SEED, (
            f"Calibration tile selection seed mismatch:\n"
            f"  Preregistered: {PREREGISTERED_SEED}\n"
            f"  Actual:        {actual_seed}\n"
            f"  This is a methodology compliance issue that needs investigation."
        )


@pytest.mark.tier1
@pytest.mark.compliance
class TestGroundTruthCRSCompliance:
    """Tests for coordinate reference system compliance."""

    def test_ground_truth_crs_matches_preregistration(
        self, reference_files: list
    ) -> None:
        """Verify all reference data uses preregistered CRS (EPSG:32635).

        EPSG:32635 (UTM Zone 35N) is specified in the preregistration
        for Bulgaria study area. This ensures distance calculations
        are in metres and spatially consistent.
        """
        for ref_file in reference_files:
            gdf = gpd.read_file(ref_file)
            actual_epsg = gdf.crs.to_epsg() if gdf.crs else None

            assert actual_epsg == PREREGISTERED_CRS, (
                f"CRS mismatch in {ref_file.name}:\n"
                f"  Preregistered: EPSG:{PREREGISTERED_CRS}\n"
                f"  Actual:        EPSG:{actual_epsg}"
            )


@pytest.mark.tier1
@pytest.mark.compliance
class TestTileConfigCompliance:
    """Tests for tile configuration compliance."""

    def test_config_has_tile_size(self) -> None:
        """Verify config.py defines correct TILE_SIZE and STRIDE.

        Preregistration specifies:
        - TILE_SIZE = 512 pixels (tile dimensions)
        - STRIDE = 448 pixels (distance between tile origins)

        These must match to ensure consistent tile processing.
        """
        from config import TILE_SIZE, STRIDE

        assert TILE_SIZE == PREREGISTERED_TILE_SIZE, (
            f"TILE_SIZE mismatch:\n"
            f"  Preregistered: {PREREGISTERED_TILE_SIZE}\n"
            f"  Actual:        {TILE_SIZE}"
        )

        assert STRIDE == PREREGISTERED_STRIDE, (
            f"STRIDE mismatch:\n"
            f"  Preregistered: {PREREGISTERED_STRIDE}\n"
            f"  Actual:        {STRIDE}"
        )


@pytest.mark.tier1
@pytest.mark.compliance
class TestSpatialToleranceCompliance:
    """Tests for spatial tolerance compliance in F1 calculation."""

    def test_f1_uses_correct_spatial_tolerance(self) -> None:
        """Verify F1 matching respects the 20m spatial tolerance threshold.

        Preregistration specifies 20 metres as the maximum distance for
        a detection to be considered a match to a reference. This test
        verifies the matching function correctly applies this threshold.

        Test cases:
        - Detection at 19m from reference -> should match (within tolerance)
        - Detection at 21m from reference -> should NOT match (outside tolerance)
        """
        # Create reference at origin
        ref_point = Point(500000, 4700000)
        ref_geoms = [ref_point]

        # Detection 19m away (should match)
        det_19m = Point(500019, 4700000)  # 19m east
        det_geoms_19m = [det_19m]

        matched_det, matched_ref, _, _ = match_detections_to_references(
            det_geoms_19m, ref_geoms, PREREGISTERED_SPATIAL_TOLERANCE
        )
        assert len(matched_det) == 1, (
            f"Detection at 19m should match (within {PREREGISTERED_SPATIAL_TOLERANCE}m tolerance)"
        )

        # Detection 21m away (should NOT match)
        det_21m = Point(500021, 4700000)  # 21m east
        det_geoms_21m = [det_21m]

        matched_det, matched_ref, _, _ = match_detections_to_references(
            det_geoms_21m, ref_geoms, PREREGISTERED_SPATIAL_TOLERANCE
        )
        assert len(matched_det) == 0, (
            f"Detection at 21m should NOT match (outside {PREREGISTERED_SPATIAL_TOLERANCE}m tolerance)"
        )
