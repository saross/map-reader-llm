"""Tests for the IM-k4 derivation filter (PI ruling 2026-08-23)."""
from __future__ import annotations

import geopandas as gpd
import pytest
from shapely.geometry import Point

from scripts.derive_im_k4_verified import filter_k4

pytestmark = pytest.mark.tier1


def _gdf(votes: list[int]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"candidate_id": [f"c{i}" for i in range(len(votes))],
         "vote_count": votes},
        geometry=[Point(i, i) for i in range(len(votes))],
        crs="EPSG:32635",
    )


def test_filter_keeps_only_votes_at_or_above_four():
    out = filter_k4(_gdf([3, 4, 5, 3, 4]))
    assert list(out["candidate_id"]) == ["c1", "c2", "c4"]
    assert (out["vote_count"] >= 4).all()


def test_filter_preserves_columns_and_order():
    out = filter_k4(_gdf([5, 3, 4]))
    assert list(out.columns) == ["candidate_id", "vote_count", "geometry"]
    assert list(out["candidate_id"]) == ["c0", "c2"]


def test_filter_refuses_missing_vote_count():
    gdf = _gdf([4, 4]).drop(columns=["vote_count"])
    with pytest.raises(ValueError, match="vote_count"):
        filter_k4(gdf)
