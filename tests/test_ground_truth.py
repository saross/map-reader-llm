"""
Tests for ground truth reference data integrity.

Tier 1 tests verifying that reference GeoJSON files exist, have the correct
schema, and use the expected coordinate reference system (CRS).

These tests ensure the foundational data required for F1 calculation is valid.
"""

import geopandas as gpd
import pytest

# Expected CRS for all ground truth data (UTM Zone 35N for Bulgaria)
EXPECTED_CRS = "EPSG:32635"
MINIMUM_REFERENCE_FILES = 4  # At least 4 map sheets


@pytest.mark.tier1
class TestGroundTruthFiles:
    """Tests for ground truth file existence and accessibility."""

    def test_ground_truth_files_exist(self, reference_files: list) -> None:
        """Verify that reference GeoJSON files exist in inputs/vectors/references/.

        The preregistration requires ground truth data for multiple map sheets.
        This test ensures the minimum number of reference files are present.
        """
        assert len(reference_files) >= MINIMUM_REFERENCE_FILES, (
            f"Expected at least {MINIMUM_REFERENCE_FILES} reference files, "
            f"found {len(reference_files)}"
        )

        # Verify files are not empty
        for ref_file in reference_files:
            assert ref_file.exists(), f"Reference file does not exist: {ref_file}"
            assert ref_file.stat().st_size > 0, f"Reference file is empty: {ref_file}"


@pytest.mark.tier1
class TestGroundTruthSchema:
    """Tests for ground truth data schema compliance."""

    def test_ground_truth_schema(self, reference_files: list) -> None:
        """Verify reference GeoJSON files have required columns.

        Required schema:
        - geometry: Point or Polygon geometries for mound locations
        - fid: Feature identifier (may also be 'id' or similar)
        """
        for ref_file in reference_files:
            gdf = gpd.read_file(ref_file)

            # Must have geometry column
            assert "geometry" in gdf.columns, (
                f"Missing 'geometry' column in {ref_file.name}"
            )

            # Must have some form of identifier
            id_columns = {"fid", "id", "FID", "ID", "OBJECTID"}
            has_id = bool(id_columns & set(gdf.columns))
            assert has_id, (
                f"Missing identifier column (fid/id) in {ref_file.name}. "
                f"Columns: {list(gdf.columns)}"
            )

            # Must have at least one feature
            assert len(gdf) > 0, f"Reference file has no features: {ref_file.name}"


@pytest.mark.tier1
class TestGroundTruthCRS:
    """Tests for ground truth coordinate reference system."""

    def test_ground_truth_crs(self, reference_files: list) -> None:
        """Verify all reference files use EPSG:32635 (UTM Zone 35N).

        The preregistration specifies EPSG:32635 as the standard CRS
        for all spatial data in this study. This ensures consistent
        distance calculations (metres) for spatial tolerance matching.
        """
        for ref_file in reference_files:
            gdf = gpd.read_file(ref_file)

            assert gdf.crs is not None, (
                f"Reference file has no CRS defined: {ref_file.name}"
            )

            # Compare EPSG codes (handles different CRS object representations)
            actual_epsg = gdf.crs.to_epsg()
            expected_epsg = 32635

            assert actual_epsg == expected_epsg, (
                f"CRS mismatch in {ref_file.name}: "
                f"expected EPSG:{expected_epsg}, got EPSG:{actual_epsg}"
            )
