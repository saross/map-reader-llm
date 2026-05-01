#!/usr/bin/env python3
"""
Generate trapezoidal active-area bounds for the four GS map sheets.

Background
----------
The four gold-standard (GS) sheets are Russian/Soviet 1:50,000 topographic
sheets. Their cartographic content (the "active area") is a **graticule
quadrangle** — a region of the Earth bounded by parallels (lines of constant
latitude) and meridians (lines of constant longitude). When projected to
the WGS84 / UTM-35N (EPSG:32635) projected CRS used by this corpus, the
quadrangle becomes a **slightly tilted trapezoid**, not a rectangle.

The pre-existing ``inputs/vectors/bounds/gs-4maps-sheet-bounds.geojson``
records the **rectangular envelope** of each raster (i.e., the GeoTIFF
bounding box). This envelope is wider than the active area because the
rasters include a black collar / tilted-corner padding outside the
cartographic neat-line. False-positive (FP) features that fall in this
collar are not on the map and should be excluded from confusion-matrix
analysis.

This script computes the trapezoidal active area from the sheet IDs
themselves, using the deterministic Russian 1:50,000 sheet-numbering
arithmetic.

Sheet-numbering arithmetic
--------------------------
Sheet IDs of the form ``<row>-<col>-<sub>-<quad>`` (e.g., ``K-35-062-2``):

- ``<row>`` letter (A=0, B=1, ..., K=10): south-edge latitude is
  ``4° × row_index``; the 1:1,000,000 sheet covers 4° of latitude.
- ``<col>`` integer 1–60: west-edge longitude is ``(col − 31) × 6°``;
  the 1:1M sheet covers 6° of longitude.
- ``<sub>`` integer 1–144: 1 of 144 sub-sheets (12×12 grid),
  numbered left-to-right top-to-bottom (``sub_row = (sub-1) // 12`` from
  the north; ``sub_col = (sub-1) % 12`` from the west). Each sub covers
  20' lat × 30' lon.
- ``<quad>`` integer 1–4: 1=NW, 2=NE, 3=SW, 4=SE. Each quad covers
  10' lat × 15' lon.

Datum
-----
The corners are interpreted in **Pulkovo-1942 (S-42, EPSG:4284)**, the
geodetic datum used by Soviet/Russian topographic mapping. Re-projecting
to WGS84 EPSG:32635 produces a tilted trapezoid that aligns with the
rasters to within ~5–8 m. (Interpreting the corners in WGS84 EPSG:4326
produces an offset of ~130 m, which is incorrect.)

Usage
-----
::

    .venv/bin/python scripts/generate_gs4maps_active_area_bounds.py

Outputs
-------
- ``inputs/vectors/bounds/gs-4maps-active-area-bounds.geojson``
  with a ``sheet_id`` column matching ``gs-4maps-sheet-bounds.geojson``.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
from shapely.geometry import Polygon

# Source datum for the graticule corners. Russian 1:50k sheets are
# defined on Pulkovo-1942 (S-42) — re-projecting from EPSG:4284 to
# EPSG:32635 aligns the trapezoid with the GeoTIFF rasters within
# ~5–8 m. Using WGS84 (EPSG:4326) instead introduces a ~130 m offset.
GRATICULE_SOURCE_CRS = "EPSG:4284"
TARGET_CRS = "EPSG:32635"

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "inputs/vectors/bounds/gs-4maps-active-area-bounds.geojson"

# Map sheet-ID short form (matching the parsing convention) to the
# full ID used elsewhere in the project.
SHEET_ID_FULL: dict[str, str] = {
    "K-35-052-4": "K-35-052-4_32635",
    "K-35-053-3": "K-35-053-3_Elenovo",
    "K-35-062-2": "K-35-062-2_Rakovski",
    "K-35-078-1": "K-35-078-1_Lesovo",
}


def parse_sheet_id_to_quad_corners(sheet_id_short: str) -> tuple[float, float, float, float]:
    """
    Compute the (south, north, west, east) corners of a 1:50,000 sheet
    in degrees, from its short ID (e.g., ``K-35-062-2``).

    Args:
        sheet_id_short: Soviet/Russian sheet ID, e.g., ``"K-35-062-2"``.
            Format: ``<row letter>-<col int>-<sub int 1..144>-<quad int 1..4>``.

    Returns:
        Tuple ``(south_lat, north_lat, west_lon, east_lon)`` in degrees,
        in the Pulkovo-1942 / WGS84 lat-lon convention.

    Raises:
        ValueError: If the sheet-ID format is malformed.
    """
    parts = sheet_id_short.split("-")
    if len(parts) != 4:
        raise ValueError(f"Expected 4 hyphen-separated parts in {sheet_id_short!r}")
    row_letter, col_str, sub_str, quad_str = parts

    # 1:1M sheet (4° lat × 6° lon).
    row_idx = ord(row_letter.upper()) - ord("A")
    col_num = int(col_str)
    # south_1m is the southern edge of the 1:1M sheet; not needed downstream
    # because sub_north is computed by subtracting from north_1m. The 4° span
    # of the 1:1M sheet is implicit in the 12 × 20' = 4° sub-row arithmetic.
    north_1m = 4.0 * row_idx + 4.0
    west_1m = (col_num - 31) * 6.0

    # 1:100k sub-sheet (20' lat × 30' lon, 12×12 grid, north-to-south,
    # west-to-east).
    sub = int(sub_str)
    if not 1 <= sub <= 144:
        raise ValueError(f"sub must be 1–144, got {sub}")
    sub_row = (sub - 1) // 12  # 0 = northernmost
    sub_col = (sub - 1) % 12   # 0 = westernmost
    sub_north = north_1m - sub_row * (20.0 / 60.0)
    sub_south = sub_north - (20.0 / 60.0)
    sub_west = west_1m + sub_col * (30.0 / 60.0)
    sub_east = sub_west + (30.0 / 60.0)

    # 1:50k quadrant (10' lat × 15' lon).
    quad = int(quad_str)
    half_lat = 10.0 / 60.0
    half_lon = 15.0 / 60.0
    if quad == 1:    # NW
        q_north, q_south = sub_north, sub_north - half_lat
        q_west, q_east = sub_west, sub_west + half_lon
    elif quad == 2:  # NE
        q_north, q_south = sub_north, sub_north - half_lat
        q_west, q_east = sub_west + half_lon, sub_east
    elif quad == 3:  # SW
        q_north, q_south = sub_north - half_lat, sub_south
        q_west, q_east = sub_west, sub_west + half_lon
    elif quad == 4:  # SE
        q_north, q_south = sub_north - half_lat, sub_south
        q_west, q_east = sub_west + half_lon, sub_east
    else:
        raise ValueError(f"quad must be 1–4, got {quad}")
    return q_south, q_north, q_west, q_east


def build_active_area_gdf() -> gpd.GeoDataFrame:
    """
    Build a GeoDataFrame of trapezoidal active areas in EPSG:32635.

    Each polygon is the 1:50k graticule quadrangle of the corresponding
    sheet, defined by parallels and meridians on the Pulkovo-1942 datum
    and re-projected to UTM-35N (WGS84). The resulting polygon is a
    tilted trapezoid in projected coordinates.

    Returns:
        GeoDataFrame with columns ``sheet_id`` and ``geometry``.
    """
    records = []
    for sheet_id_short, sheet_id_full in SHEET_ID_FULL.items():
        south, north, west, east = parse_sheet_id_to_quad_corners(sheet_id_short)
        # Polygon in lon-lat order (geopandas convention is (x=lon, y=lat)).
        # Vertices: NW, NE, SE, SW, closing at NW.
        poly = Polygon(
            [
                (west, north),
                (east, north),
                (east, south),
                (west, south),
                (west, north),
            ]
        )
        records.append({"sheet_id": sheet_id_full, "geometry": poly})

    gdf_geo = gpd.GeoDataFrame(records, crs=GRATICULE_SOURCE_CRS)
    return gdf_geo.to_crs(TARGET_CRS)


def main() -> None:
    """Compute trapezoidal bounds and write the GeoJSON file."""
    gdf = build_active_area_gdf()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(OUTPUT_PATH, driver="GeoJSON")
    print(f"Wrote {OUTPUT_PATH}")
    print(f"CRS: {gdf.crs}; {len(gdf)} sheets:")
    for _, row in gdf.iterrows():
        b = row.geometry.bounds
        print(
            f"  {row.sheet_id}: bounds "
            f"({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f})"
        )


if __name__ == "__main__":
    main()
