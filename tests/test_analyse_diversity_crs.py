"""
Regression tests pinning the CRS contract across the diversity-analysis
consensus path (``merge_passes.apply_threshold`` →
``analyse_diversity.consensus_to_gdf``).

Context
-------
``apply_threshold`` reprojects clustered centroids from EPSG:32635 (UTM
Zone 35N, the project's analysis CRS) to EPSG:4326 (lon/lat) at output
time, per RFC 7946 (commit ``8c8e101fc``). Its downstream consumer
``consensus_to_gdf`` must therefore treat the incoming points as 4326 and
reproject them back to the analysis CRS before spatially joining against
the UTM tile bounds — otherwise every consensus detection is tagged
``source_tile = "unknown"`` and the per-map F1 scoring collapses to zero.

These tests pin both halves of that contract so the mislabel investigated
in ``reports/diversity-crs-mislabel-investigation-2026-06-08.md`` cannot
silently regress.

All four tests assert the correct CRS contract and pass against the
fixed ``analyse_diversity.consensus_to_gdf`` (the 2026-06-08 Stage-0 fix:
it now declares ``apply_threshold``'s 4326 output honestly and reprojects
to the analysis CRS before the spatial join). They previously carried
``xfail(strict=True)`` markers against the unfixed code; those were removed
when the fix landed.

See the investigation report for the full git archaeology and the
inertness analysis.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

# Add project root to path for sibling-module imports (mirrors the pattern
# used by the other analysis-script tests in this suite).
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.merge_passes import apply_threshold  # noqa: E402

# Import the diversity module via its package-free name so the relative
# sibling imports inside it resolve (it does ``sys.path.insert`` on its own
# directory and imports ``merge_passes`` etc. without a package prefix).
import analyse_diversity as ad  # noqa: E402

TARGET_CRS = "EPSG:32635"

# A representative UTM (EPSG:32635) centroid in the Bulgarian study area,
# taken from a real condition-A run centroid observed during the 2026-06-08
# investigation (``outputs/retest/phase3c/track2-text/h9-A-p1/run_1``).
_UTM_EASTING = 397541.86553450004
_UTM_NORTHING = 4705060.8391695


def _make_cluster(centroid: tuple[float, float], vote_count: int = 3) -> dict:
    """Build a minimal cluster dict accepted by ``apply_threshold``.

    Args:
        centroid: (easting, northing) in EPSG:32635.
        vote_count: Number of contributing passes (>= threshold to retain).

    Returns:
        A cluster dict with the keys ``apply_threshold`` reads.
    """
    return {
        "centroid": centroid,
        "label": "burial_mound",
        "vote_count": vote_count,
        "contributing_passes": [f"p{i}" for i in range(vote_count)],
        "source_tiles": ["tile_001"],
        "cluster_size": vote_count,
    }


def _bounds_around_utm(
    easting: float,
    northing: float,
    half_size: float = 500.0,
    tile_name: str = "K-35-052-4_32635_x0_y0",
) -> gpd.GeoDataFrame:
    """Return a one-tile UTM bounds GeoDataFrame enclosing the given point.

    Args:
        easting: UTM easting the tile must contain.
        northing: UTM northing the tile must contain.
        half_size: Half the tile side length in metres.
        tile_name: ``tile_name`` value (must start with a plausible map
            name so per-map scoping downstream behaves realistically).

    Returns:
        Single-row GeoDataFrame in ``TARGET_CRS`` with a ``tile_name``
        column and a square polygon geometry.
    """
    poly = box(
        easting - half_size,
        northing - half_size,
        easting + half_size,
        northing + half_size,
    )
    return gpd.GeoDataFrame(
        {"tile_name": [tile_name]},
        geometry=[poly],
        crs=TARGET_CRS,
    )


@pytest.mark.tier1
class TestApplyThresholdOutputCRS:
    """Pin the EPSG:4326 output contract of ``apply_threshold``.

    This is the upstream half of the contract: ``consensus_to_gdf`` relies
    on these points being 4326. If a future change reverts ``apply_threshold``
    to emit UTM (or any other CRS), this test catches it so the consumer can
    be updated in lockstep.
    """

    def test_output_is_geographic_lonlat(self) -> None:
        """Output coordinates must be EPSG:4326 lon/lat in the Bulgaria bbox."""
        fc = apply_threshold(
            [_make_cluster((_UTM_EASTING, _UTM_NORTHING))],
            threshold=1,
            total_passes=5,
        )
        assert len(fc["features"]) == 1
        lon, lat = fc["features"][0]["geometry"]["coordinates"]
        # Geographic ranges (a UTM easting/northing would blow these out).
        assert -180.0 <= lon <= 180.0, f"lon {lon} not geographic"
        assert -90.0 <= lat <= 90.0, f"lat {lat} not geographic"
        # Bulgaria: ~25-26 E, ~42 N.
        assert 24.0 < lon < 27.0, f"lon {lon} not in study area"
        assert 41.0 < lat < 43.0, f"lat {lat} not in study area"


@pytest.mark.tier1
class TestConsensusToGdfCRSContract:
    """Pin the CRS behaviour of ``consensus_to_gdf``.

    These assert the contract honoured by the fixed code: the 4326 points
    from ``apply_threshold`` are reprojected to the analysis CRS (EPSG:32635)
    before the spatial join, so detections inside a tile are matched (not
    tagged "unknown") and the returned geometry is genuine UTM. They guard
    against a regression of the 2026-06-08 mislabel.
    """

    def test_detection_inside_tile_gets_real_source_tile(self) -> None:
        """A detection inside a known tile must be assigned that tile.

        This is the invariant the mislabel violates: with the points
        mislabelled, the intersects-join matches nothing and ``source_tile``
        becomes ``"unknown"`` for every detection.
        """
        fc = apply_threshold(
            [_make_cluster((_UTM_EASTING, _UTM_NORTHING))],
            threshold=1,
            total_passes=5,
        )
        gdf_bounds = _bounds_around_utm(_UTM_EASTING, _UTM_NORTHING)

        result = ad.consensus_to_gdf(fc, gdf_bounds)

        assert len(result) == 1
        assert result.iloc[0]["source_tile"] != "unknown", (
            "Detection inside the tile should be matched, not 'unknown' — "
            "indicates the consensus points were not reprojected to the "
            "bounds CRS before the spatial join."
        )

    def test_output_geometry_is_genuine_utm(self) -> None:
        """Returned geometry must be in genuine UTM (easting > 100 000).

        ``consensus_to_gdf`` advertises EPSG:32635 output. A genuine UTM
        easting in this study area is ~3-4 x 10^5; a 4326 longitude would be
        ~25. This catches the label/coordinate mismatch directly.
        """
        fc = apply_threshold(
            [_make_cluster((_UTM_EASTING, _UTM_NORTHING))],
            threshold=1,
            total_passes=5,
        )
        gdf_bounds = _bounds_around_utm(_UTM_EASTING, _UTM_NORTHING)

        result = ad.consensus_to_gdf(fc, gdf_bounds)

        assert str(result.crs).upper().endswith("32635")
        easting = result.geometry.iloc[0].x
        assert easting > 100_000.0, (
            f"Easting {easting} looks like a 4326 longitude, not UTM — "
            "coordinates were not reprojected to match the advertised CRS."
        )
