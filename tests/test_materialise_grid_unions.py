"""Tests for the grid K = 10 union materialiser (PI stop rule, 2026-08-24)."""
from __future__ import annotations

import geopandas as gpd
import pytest
from shapely.geometry import box

from scripts.materialise_grid_unions import EXPECTED, union_with_votes

pytestmark = pytest.mark.tier1


def _bounds() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"tile_name": ["t1"]}, geometry=[box(0, 0, 100, 100)],
        crs="EPSG:32635")


def test_union_carries_votes_through_tile_filter():
    """Clusters keep their pass-vote counts; off-carrier clusters drop."""
    passes = [
        [{"centroid": (10.0, 10.0), "cluster_size": 1},
         {"centroid": (500.0, 500.0), "cluster_size": 1}],   # off-carrier
        [{"centroid": (12.0, 10.0), "cluster_size": 1}],      # same cluster
        [{"centroid": (80.0, 80.0), "cluster_size": 1}],
    ]
    gdf = union_with_votes(passes, _bounds())
    assert len(gdf) == 2                       # off-carrier cluster dropped
    votes = sorted(gdf["vote_count"].tolist())
    assert votes == [1, 2]                     # two-pass cluster keeps 2

    assert (gdf["source_tile"] == "t1").all()


def test_expected_counts_are_the_documented_four():
    """The gate constants match the findings' verifier-costing table."""
    assert EXPECTED == {"g512_ov064": 1402, "g512_ov256": 2585,
                       "g384_ov048": 1827, "g384_ov192": 3319}
    assert sum(EXPECTED.values()) == 9133


def test_union_records_members_and_keeps_each_cluster_on_its_sheet():
    """D62 (1): a cluster seen on sheet A is booked on A in the sheets' overlap.

    Two one-tile sheets overlap on x in [90, 110]. A two-pass cluster at
    x = 105 is nearer sheet B's tile centroid, so the legacy rule booked it
    to B; seen only on A, it now stays on A and records its members' tiles.
    """
    tile_a = "K-35-001-1_32635_x0_y0.png"
    tile_b = "K-35-001-2_32635_x0_y0.png"
    bounds = gpd.GeoDataFrame(
        {"tile_name": [tile_a, tile_b]},
        geometry=[box(-10, 0, 110, 100), box(90, 0, 210, 100)], crs="EPSG:32635")
    passes = [
        [{"centroid": (105.0, 50.0), "cluster_size": 1, "source_tiles": [tile_a]}],
        [{"centroid": (106.0, 50.0), "cluster_size": 1, "source_tiles": [tile_a]},
         {"centroid": (180.0, 50.0), "cluster_size": 1, "source_tiles": [tile_b]}],
    ]
    gdf = union_with_votes(passes, bounds)
    assert gdf["vote_count"].tolist() == [2, 1]
    assert gdf["origin_tiles"].tolist() == [tile_a, tile_b]
    assert gdf["source_tile"].tolist() == [tile_a, tile_b]
