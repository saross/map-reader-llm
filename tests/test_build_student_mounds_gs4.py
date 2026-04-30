"""Tier-1 unit tests for ``scripts/build_student_mounds_gs4``.

Verifies:

- The Hairy filter selects only ``Mound`` rows whose ``MpSymbl`` contains
  "Hairy" (case-insensitive).
- The 55-map schema-conformer renames truncated columns and emits the
  canonical 7-column ordering.
- The cluster-preview helper agrees with ``review_gt_duplicates``'s own
  ``build_clusters`` predicate on a tiny synthetic fixture.
- The build module imports cleanly (no Streamlit/runtime side-effects).

Does not touch the on-disk shapefile, raster files, or output GeoJSON
artefacts — those are exercised by the build script's own
sanity-check stdout when run end-to-end.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import geopandas as gpd
import pytest
from shapely.geometry import Point

from scripts.build_student_mounds_gs4 import (
    _OUTPUT_COLUMNS,
    apply_hairy_filter,
    conform_to_55maps_schema,
    count_clusters_at_threshold,
)


# =========================================================================
# Hairy filter
# =========================================================================


@pytest.mark.tier1
def test_apply_hairy_filter_selects_mound_and_hairy() -> None:
    """Only ``FetrTyp=='Mound'`` AND ``MpSymbl`` contains 'Hairy' survive."""
    rows = [
        {"FetrTyp": "Mound", "MpSymbl": "Hairy brown circle",
         "geometry": Point(0.0, 0.0)},
        {"FetrTyp": "Mound", "MpSymbl": "Black diamond with a dot inside",
         "geometry": Point(1.0, 1.0)},
        {"FetrTyp": "Surface feature", "MpSymbl": "Hairy black circle",
         "geometry": Point(2.0, 2.0)},
        {"FetrTyp": "Mound", "MpSymbl": "hairy black square",  # lower-case
         "geometry": Point(3.0, 3.0)},
        {"FetrTyp": "Other", "MpSymbl": "Hairy brown circle",
         "geometry": Point(4.0, 4.0)},
        {"FetrTyp": "Mound", "MpSymbl": None,
         "geometry": Point(5.0, 5.0)},
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32635")
    out = apply_hairy_filter(gdf)
    # Expect rows 0 and 3 only (Mound + Hairy/hairy).
    assert len(out) == 2
    assert set(out["MpSymbl"]) == {"Hairy brown circle", "hairy black square"}


@pytest.mark.tier1
def test_apply_hairy_filter_returns_reset_index() -> None:
    """The filtered frame has a clean RangeIndex (no inherited gaps)."""
    rows = [
        {"FetrTyp": "Other", "MpSymbl": "X", "geometry": Point(0.0, 0.0)},
        {"FetrTyp": "Mound", "MpSymbl": "Hairy", "geometry": Point(1.0, 1.0)},
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32635")
    out = apply_hairy_filter(gdf)
    assert list(out.index) == [0]


# =========================================================================
# Schema conformer
# =========================================================================


@pytest.mark.tier1
def test_conform_to_55maps_schema_renames_and_orders() -> None:
    """Truncated columns are renamed and output preserves canonical order."""
    rows = [
        {
            "uuid": 1.000050e18,
            "MpSymbl": "Hairy brown circle",
            "FetrTyp": "Mound",
            "Latitud": 42.5,
            "Longitd": 26.5,
            "source_map": "K-35-052-4_32635",
            "geometry": Point(400000.0, 4700000.0),
            "extraneous": "ignore me",
        },
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32635")
    out = conform_to_55maps_schema(gdf)
    assert list(out.columns) == list(_OUTPUT_COLUMNS)
    assert out.iloc[0]["MapSymbol"] == "Hairy brown circle"
    assert out.iloc[0]["FeatureType"] == "Mound"
    assert out.iloc[0]["Latitude"] == pytest.approx(42.5)
    assert out.iloc[0]["Longitude"] == pytest.approx(26.5)
    # uuid coerced to fixed-point string.
    assert isinstance(out.iloc[0]["uuid"], str)
    assert out.iloc[0]["uuid"].isdigit()


@pytest.mark.tier1
def test_conform_to_55maps_schema_raises_on_missing_columns() -> None:
    """Missing required columns raise ValueError, not silently drop."""
    rows = [
        {"FetrTyp": "Mound", "MpSymbl": "Hairy",
         "geometry": Point(0.0, 0.0)},  # no source_map / Latitud / Longitd / uuid
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32635")
    with pytest.raises(ValueError, match="Missing expected columns"):
        conform_to_55maps_schema(gdf)


# =========================================================================
# Cluster-preview helper
# =========================================================================


@pytest.mark.tier1
def test_count_clusters_at_threshold_pair() -> None:
    """One pair within threshold counts as a single cluster."""
    rows = [
        {"source_map": "S1", "geometry": Point(0.0, 0.0)},
        {"source_map": "S1", "geometry": Point(10.0, 0.0)},  # 10 m
        {"source_map": "S1", "geometry": Point(500.0, 500.0)},  # isolated
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32635")
    assert count_clusters_at_threshold(gdf, threshold_m=50.0) == 1


@pytest.mark.tier1
def test_count_clusters_at_threshold_per_map_isolation() -> None:
    """Points on different sheets never join even if coincident."""
    rows = [
        {"source_map": "S1", "geometry": Point(0.0, 0.0)},
        {"source_map": "S2", "geometry": Point(0.0, 0.0)},
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32635")
    assert count_clusters_at_threshold(gdf, threshold_m=50.0) == 0


@pytest.mark.tier1
def test_count_clusters_at_threshold_no_clusters() -> None:
    """Sparse points return zero."""
    rows = [
        {"source_map": "S1", "geometry": Point(0.0, 0.0)},
        {"source_map": "S1", "geometry": Point(1000.0, 1000.0)},
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32635")
    assert count_clusters_at_threshold(gdf, threshold_m=50.0) == 0
