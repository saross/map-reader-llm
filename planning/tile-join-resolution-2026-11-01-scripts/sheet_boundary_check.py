#!/usr/bin/env python3
"""
Sheet-boundary check for the tile-join decision record (gate R, R2).

Answers two questions that decide whether tile-level metrics should be
scored per sheet or across a geographic mosaic of sheets (D73 (2)):

1. **Is the gold standard (GS) digitised per sheet or per mound?** If a
   mound printed on two overlapping sheets had been digitised on both, the
   GS would hold pairs of references from different sheets a few metres to
   a few hundred metres apart. The script reports the nearest
   different-sheet reference for every reference.
2. **Where do references meet another sheet's tiles?** For every reference
   lying inside a tile of a sheet other than its own ``Map``, it reports
   that tile and the reference's pixel position in the tile image, read
   from the tile's ESRI world file (``.pgw``), so the image can be checked
   for map content at that position.

It deliberately imports nothing from the project's scorer and nothing
outside the standard library, so its answer does not depend on the scorer
under review or on the machine's virtual environment (D70). Tiles are
treated as polygons and tested with a ray-casting point-in-polygon rule.

Usage::

    python planning/tile-join-resolution-2026-11-01-scripts/sheet_boundary_check.py \
        > planning/tile-join-resolution-2026-11-01-scripts/sheet_boundary_check.txt

Created: 2026-11-18 (S168, amd-tower)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REFERENCES = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
TILE_DIR = PROJECT_ROOT / "inputs/tiles_384"

Ring = list[tuple[float, float]]


def load_tiles(path: Path) -> list[tuple[str, Ring]]:
    """Read the frame's tiles as (tile_name, exterior ring) pairs.

    Args:
        path: GeoJSON of tile polygons with a ``tile_name`` property.

    Returns:
        One (name, ring) pair per tile, ring as (x, y) tuples.
    """
    data = json.loads(path.read_text())
    tiles: list[tuple[str, Ring]] = []
    for feature in data["features"]:
        geometry = feature["geometry"]
        coords = geometry["coordinates"]
        ring = coords[0] if geometry["type"] == "Polygon" else coords[0][0]
        tiles.append((feature["properties"]["tile_name"],
                      [(float(p[0]), float(p[1])) for p in ring]))
    return tiles


def inside(x: float, y: float, ring: Ring) -> bool:
    """Ray-casting point-in-polygon test (boundary points may go either way).

    Args:
        x: Easting of the point.
        y: Northing of the point.
        ring: Polygon exterior ring.

    Returns:
        True if the point lies inside the ring.
    """
    result = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            result = not result
    return result


def sheet_of(tile_name: str) -> str:
    """Return the sheet prefix of a tile name (the text before ``_x``)."""
    return tile_name.split("_x")[0]


def pixel_position(tile_name: str, x: float, y: float) -> tuple[float, float] | None:
    """Convert a map coordinate to (column, row) in a tile image.

    Args:
        tile_name: Tile name, with or without the ``.png`` suffix.
        x: Easting in the frame's coordinate reference system.
        y: Northing in the same system.

    Returns:
        (column, row) in pixels, or None if the world file is absent.
    """
    stem = tile_name.removesuffix(".png")
    world = TILE_DIR / sheet_of(stem) / f"{stem}.pgw"
    if not world.exists():
        return None
    a, _d, _b, e, c, f = (float(v) for v in world.read_text().split())
    return (x - c) / a, (y - f) / e


def main() -> None:
    """Print both checks' results."""
    refs = json.loads(REFERENCES.read_text())["features"]
    points = [(r["properties"]["Map"], r["properties"]["fid"],
               float(r["geometry"]["coordinates"][0][0]),
               float(r["geometry"]["coordinates"][0][1])) for r in refs]
    print(f"references: {len(points)} in {REFERENCES.relative_to(PROJECT_ROOT)}")
    per_sheet: dict[str, int] = {}
    for sheet, *_ in points:
        per_sheet[sheet] = per_sheet.get(sheet, 0) + 1
    for sheet, n in sorted(per_sheet.items()):
        print(f"  {sheet}: {n}")

    # Check 1: nearest reference on a different sheet, for every reference.
    nearest = []
    for sheet, fid, x, y in points:
        best = min((math.hypot(x - x2, y - y2), s2, f2)
                   for s2, f2, x2, y2 in points if s2 != sheet)
        nearest.append((best[0], sheet, fid, best[1], best[2]))
    nearest.sort()
    print("\ncheck 1: references with a different-sheet reference within")
    for limit in (50, 100, 200, 500, 1000):
        print(f"  {limit:>5} m: {sum(1 for n in nearest if n[0] <= limit)}")
    d, s1, f1, s2, f2 = nearest[0]
    print(f"  closest cross-sheet pair: {d:.1f} m ({s1} fid {f1} / {s2} fid {f2})")

    # Check 2: references inside another sheet's tile, with pixel positions.
    tiles = load_tiles(BOUNDS)
    print(f"\ncheck 2: {len(tiles)} tiles in {BOUNDS.relative_to(PROJECT_ROOT)}")
    count = 0
    for sheet, fid, x, y in points:
        containing = [name for name, ring in tiles if inside(x, y, ring)]
        foreign = [name for name in containing if sheet_of(name) != sheet]
        if not foreign:
            continue
        count += 1
        for name in foreign:
            pos = pixel_position(name, x, y)
            where = "no world file" if pos is None else f"col {pos[0]:.1f}, row {pos[1]:.1f}"
            offset = re.search(r"_x\d+_y\d+", name)
            print(f"  fid {fid:>4} ({sheet}) in {sheet_of(name)}"
                  f"{offset.group(0) if offset else ''}: {where}")
    print(f"  references inside another sheet's tile: {count}")


if __name__ == "__main__":
    main()
