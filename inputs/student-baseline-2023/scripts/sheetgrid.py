#!/usr/bin/env python3
"""
Build a true, non-overlapping 1:50,000 Soviet-nomenclature sheet grid for K-35.

Why not the local rasters: every GeoTIFF in inputs/rasters/Russian1981_32635/ is a
north-up axis-aligned bounding box in EPSG:32635, so neighbouring sheet footprints
overlap by ~15 % (162 overlapping pairs, 3,296 sq km total). Assigning points to
sheets from those footprints mis-attributes every edge feature. The graticule below
tessellates exactly.

Nomenclature (verified against inputs/rasters/Russian1981_32635/K-35-055-1.tif,
whose EPSG:32635 bounds 499871..520391 E / 4705249..4723813 N correspond to
lon 27.00-27.25 E, lat 42.500-42.667 N):

  1:1M sheet K-35   : row K = 40-44 N; column 35 = 24-30 E
  1:100k sheet -NNN : 12 x 12 grid inside it, 30' lon x 20' lat,
                      numbered left-to-right then top-to-bottom
  1:50k quarter -q  : 1 NW, 2 NE, 3 SW, 4 SE; 15' lon x 10' lat
"""

from __future__ import annotations

import geopandas as gpd
from shapely.geometry import box

# 1:1M sheet K-35
LAT_TOP, LON_LEFT = 44.0, 24.0
H100, W100 = 20.0 / 60.0, 30.0 / 60.0   # 1:100k cell size, degrees
H50, W50 = H100 / 2.0, W100 / 2.0       # 1:50k quarter size, degrees


def cell_bounds(n100: int, quarter: int) -> tuple[float, float, float, float]:
    """Return (minx, miny, maxx, maxy) in EPSG:4326 for K-35-<n100>-<quarter>."""
    row, col = divmod(n100 - 1, 12)
    top = LAT_TOP - row * H100
    left = LON_LEFT + col * W100
    if quarter in (3, 4):
        top -= H50
    if quarter in (2, 4):
        left += W50
    return (left, top - H50, left + W50, top)


def build(n100_range=range(1, 145), quarters=(1, 2, 3, 4)) -> gpd.GeoDataFrame:
    """Build the full K-35 1:50k grid as an EPSG:4326 GeoDataFrame."""
    rows = []
    for n in n100_range:
        for q in quarters:
            minx, miny, maxx, maxy = cell_bounds(n, q)
            rows.append({"sheet": f"K-35-{n:03d}-{q}", "geometry": box(minx, miny, maxx, maxy)})
    return gpd.GeoDataFrame(rows, crs="EPSG:4326")
