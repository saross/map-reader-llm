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
