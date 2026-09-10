"""Tier-1 tests for ``scripts/materialise_era2_b_frame.py`` (GS Era-2 board card § 2).

The frame is the Era-2 carrier tiles clipped to the B tiling's union: a tile
fully inside the mask is kept whole, a tile straddling it is clipped, and a
tile entirely outside is a refusal (the frame must remain the 487 carriers).
"""

from __future__ import annotations

import geopandas as gpd
import pytest
from shapely.geometry import box

from scripts import materialise_era2_b_frame as m

pytestmark = pytest.mark.tier1


def _tiles(boxes: list[tuple[float, float, float, float]], prefix: str = "t") -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"tile_name": [f"{prefix}{i}" for i in range(len(boxes))],
         "map_name": ["K-35-052-4"] * len(boxes),
         "geometry": [box(*b) for b in boxes]},
        crs=m.TARGET_CRS,
    )


def test_inside_tile_kept_whole_and_straddling_tile_clipped():
    era2 = _tiles([(0, 0, 100, 100), (100, 0, 200, 100)])
    mask = _tiles([(0, 0, 150, 100)], prefix="b")  # covers tile 0 fully, half of tile 1
    frame, stats = m.build_frame(era2, mask)
    assert stats["n_frame_tiles"] == 2 and stats["n_dropped_empty"] == 0
    assert stats["n_identical"] == 1 and stats["n_clipped"] == 1
    assert frame.iloc[0].geometry.area == pytest.approx(100 * 100)
    assert frame.iloc[1].geometry.area == pytest.approx(50 * 100)
    assert list(frame.columns) == ["tile_name", "map_name", "geometry"]


def test_tile_outside_the_mask_is_dropped_and_counted():
    era2 = _tiles([(0, 0, 100, 100), (500, 500, 600, 600)])
    mask = _tiles([(0, 0, 100, 100)], prefix="b")
    frame, stats = m.build_frame(era2, mask)
    assert stats["n_frame_tiles"] == 1 and stats["n_dropped_empty"] == 1


def test_reference_counts_use_the_frame_union():
    era2 = _tiles([(0, 0, 100, 100), (100, 0, 200, 100)])
    mask = _tiles([(0, 0, 150, 100)], prefix="b")
    frame, _ = m.build_frame(era2, mask)
    ref = gpd.GeoDataFrame(geometry=gpd.points_from_xy([10, 120, 180], [10, 10, 10]), crs=m.TARGET_CRS)
    counts = m.reference_counts(frame, era2, ref)
    assert counts == {"reference_total": 3, "reference_in_era2_frame": 3, "reference_in_frame": 2}
