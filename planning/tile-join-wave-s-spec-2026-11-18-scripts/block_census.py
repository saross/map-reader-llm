#!/usr/bin/env python3
"""
Block census for the wave S specification (design information, not a result).

Wave S (``planning/tile-join-wave-s-spec-2026-11-18.md``) resamples blocks of
contiguous tiles instead of single tiles. Its block sizes must be fixed, and
their consequences known, before any block statistic exists. This script
supplies the consequences: for every frame behind a signed tile-MCC row
(``planning/tile-join-resolution-2026-11-01-scripts/frame_census.txt``) and
for every candidate block side, it reports

1. the tiling (tile size, stride, overlap, metres per sheet pixel) measured
   from the frame itself;
2. how many blocks the side produces, per frame and per sheet, and how many
   tiles each holds;
3. how many tiles overlap a tile of a *different* block, within their own
   sheet and across sheets (the dependence that blocks cannot remove);
4. whether two independent routes to a tile's block agree: one from the
   tile's position in metres (EPSG:32635), one from the pixel offsets in its
   name. Any disagreement is printed.

The block rule is the specification's § 3.2: square blocks laid on each
sheet's own raster grid, origin at the north-west corner of the sheet's pixel
(0, 0), sides along the raster's columns and rows (UTM easting and southing),
side ``S`` sheet pixels; a tile belongs to the block holding the centre of its
nominal (unclipped) pixel window. Partial blocks at a sheet's east and south
edges, and blocks thinned by holes in a frame, are kept as they fall.

It reads only the bounds GeoJSON files and imports nothing beyond the
standard library, so it does not depend on the scorer or on the machine's
virtual environment (D70). No detection, reference, or model output is read.

Usage::

    python planning/tile-join-wave-s-spec-2026-11-18-scripts/block_census.py \
        > planning/tile-join-wave-s-spec-2026-11-18-scripts/block_census.txt

Created: 2026-11-18 (drafting for S169, amd-tower)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import re
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: The eight frames of the parent record's § 2.4, in its order.
FRAMES: tuple[str, ...] = (
    "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson",
    "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
    "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson",
    "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson",
    "inputs/vectors/bounds/full_evaluation_bounds.geojson",
    "outputs/h13/scoring/bounds/h13_common_bounds.geojson",
    "inputs/vectors/bounds/384/h10_test_bounds.geojson",
    "inputs/vectors/bounds/256/full_evaluation_bounds.geojson",
)

#: Candidate block sides in sheet pixels. 1,344 px is the least common
#: multiple of the three strides in use (224, 336, and 448 px).
SIDES_PX: tuple[int, ...] = (672, 1008, 1344, 2016, 2688)

#: Stride (px) -> tile size (px) for the three tilings in the corpus.
TILE_SIZE_BY_STRIDE: dict[int, int] = {224: 256, 336: 384, 448: 512}

TILE_NAME_RE = re.compile(r"_x(\d+)_y(\d+)\.png$")

#: Spatial-hash cell for the overlap search, in metres (larger than a tile).
HASH_CELL_M = 3000.0


def load_tiles(path: Path) -> list[dict]:
    """Read a bounds file into tile records.

    Args:
        path: A bounds GeoJSON whose features carry ``tile_name`` and
            ``map_name`` and whose geometry is one polygon ring.

    Returns:
        One dict per tile: name, sheet, pixel offsets, bounding box in
        metres, and whether every polygon edge is axis-parallel.
    """
    tiles = []
    for feature in json.loads(path.read_text())["features"]:
        props = feature["properties"]
        match = TILE_NAME_RE.search(props["tile_name"])
        if match is None:
            raise ValueError(f"unparseable tile name {props['tile_name']!r}")
        ring = feature["geometry"]["coordinates"][0]
        xs = [c[0] for c in ring]
        ys = [c[1] for c in ring]
        axis_parallel = all(
            abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6
            for a, b in zip(ring, ring[1:], strict=False)
        )
        tiles.append({
            "name": props["tile_name"], "sheet": props["map_name"],
            "xpx": int(match.group(1)), "ypx": int(match.group(2)),
            "w": min(xs), "e": max(xs), "s": min(ys), "n": max(ys),
            "axis_parallel": axis_parallel,
        })
    return tiles


def measure_tiling(tiles: list[dict]) -> tuple[int, int, dict[str, float]]:
    """Measure the stride, tile size, and metres per pixel of each sheet.

    The stride is the most common gap between a sheet's distinct x pixel
    offsets. Metres per pixel is the most common tile width in the sheet
    divided by the tile size (clipped tiles are a minority in every frame).

    Args:
        tiles: Output of :func:`load_tiles`.

    Returns:
        ``(stride_px, tile_px, metres_per_px_by_sheet)``.
    """
    offsets: dict[str, set[int]] = defaultdict(set)
    for t in tiles:
        offsets[t["sheet"]].add(t["xpx"])
    gaps: Counter[int] = Counter()
    for values in offsets.values():
        ordered = sorted(values)
        gaps.update(b - a for a, b in zip(ordered, ordered[1:], strict=False))
    stride = gaps.most_common(1)[0][0]
    tile_px = TILE_SIZE_BY_STRIDE[stride]
    mpp = {}
    for sheet in offsets:
        widths = Counter(round(t["e"] - t["w"], 3) for t in tiles if t["sheet"] == sheet)
        mpp[sheet] = widths.most_common(1)[0][0] / tile_px
    return stride, tile_px, mpp


def sheet_origins(tiles: list[dict], mpp: dict[str, float]) -> dict[str, tuple[float, float]]:
    """Locate each sheet's raster origin (NW corner of pixel (0, 0)) in metres.

    Estimated from every unclipped tile as ``west - xpx * m`` and
    ``north + ypx * m``; the median is taken so that clipped polygons (whose
    west or north edge is not the nominal one) cannot move it.

    Args:
        tiles: Output of :func:`load_tiles`.
        mpp: Metres per pixel by sheet.

    Returns:
        ``{sheet: (x0, y0)}`` in EPSG:32635 metres.
    """
    xs: dict[str, list[float]] = defaultdict(list)
    ys: dict[str, list[float]] = defaultdict(list)
    for t in tiles:
        m = mpp[t["sheet"]]
        xs[t["sheet"]].append(t["w"] - t["xpx"] * m)
        ys[t["sheet"]].append(t["n"] + t["ypx"] * m)
    return {s: (statistics.median(xs[s]), statistics.median(ys[s])) for s in xs}


def block_by_index(tile: dict, tile_px: int, side_px: int) -> tuple[str, int, int]:
    """Block of a tile from the pixel offsets in its name."""
    return (tile["sheet"], (tile["xpx"] + tile_px // 2) // side_px,
            (tile["ypx"] + tile_px // 2) // side_px)


def block_by_metres(tile: dict, tile_px: int, side_px: int, mpp: dict[str, float],
                    origins: dict[str, tuple[float, float]]) -> tuple[str, int, int]:
    """Block of a tile from its nominal centre in metres.

    The nominal centre is the tile's pixel window ``[xpx, xpx + T)`` mapped
    through the sheet's origin and pixel size, so a clipped frame polygon does
    not move the tile.
    """
    m = mpp[tile["sheet"]]
    x0, y0 = origins[tile["sheet"]]
    centre_e = x0 + (tile["xpx"] + tile_px / 2) * m
    centre_n = y0 - (tile["ypx"] + tile_px / 2) * m
    side_m = side_px * m
    return (tile["sheet"], int((centre_e - x0) // side_m), int((y0 - centre_n) // side_m))


def cross_block_overlaps(tiles: list[dict], block: dict[str, tuple]) -> tuple[set, set]:
    """Tiles whose footprint overlaps (positive area) a tile of another block.

    Args:
        tiles: Output of :func:`load_tiles`.
        block: Tile name -> block identity.

    Returns:
        ``(same_sheet, other_sheet)``: names of tiles that overlap a tile of
        a different block in their own sheet, and in another sheet.
    """
    grid: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for t in tiles:
        for gx in range(int(t["w"] // HASH_CELL_M), int(t["e"] // HASH_CELL_M) + 1):
            for gy in range(int(t["s"] // HASH_CELL_M), int(t["n"] // HASH_CELL_M) + 1):
                grid[(gx, gy)].append(t)
    same, other = set(), set()
    for members in grid.values():
        for a, b in combinations(members, 2):
            if block[a["name"]] == block[b["name"]]:
                continue
            dx = min(a["e"], b["e"]) - max(a["w"], b["w"])
            dy = min(a["n"], b["n"]) - max(a["s"], b["s"])
            if dx > 1e-6 and dy > 1e-6:
                (same if a["sheet"] == b["sheet"] else other).update((a["name"], b["name"]))
    return same, other


def report(path_text: str) -> None:
    """Print the tiling and the block census of one frame."""
    tiles = load_tiles(REPO / path_text)
    stride, tile_px, mpp = measure_tiling(tiles)
    origins = sheet_origins(tiles, mpp)
    n = len(tiles)
    sheet_sizes = Counter(t["sheet"] for t in tiles)
    print(f"\n## {path_text}")
    print(f"tiles {n}; sheets {len(sheet_sizes)}; tile {tile_px} px; stride {stride} px; "
          f"overlap {tile_px - stride} px; metres per sheet pixel "
          f"{min(mpp.values()):.4f}-{max(mpp.values()):.4f}; every polygon axis-parallel: "
          f"{all(t['axis_parallel'] for t in tiles)}")
    print(f"tiles per sheet min/median/max {min(sheet_sizes.values())}/"
          f"{statistics.median(sheet_sizes.values()):g}/{max(sheet_sizes.values())}")
    for side in SIDES_PX:
        by_index = {t["name"]: block_by_index(t, tile_px, side) for t in tiles}
        by_metres = {t["name"]: block_by_metres(t, tile_px, side, mpp, origins) for t in tiles}
        disagree = sorted(k for k in by_index if by_index[k] != by_metres[k])
        sizes = sorted(Counter(by_index.values()).values())
        per_sheet = Counter(b[0] for b in set(by_index.values()))
        same, other = cross_block_overlaps(tiles, by_index)
        side_m = (side * min(mpp.values()), side * max(mpp.values()))
        print(f"side {side} px = {side / stride:g} strides = {side_m[0] / 1000:.2f}-"
              f"{side_m[1] / 1000:.2f} km | routes disagree on {len(disagree)} tiles | "
              f"blocks {len(sizes)} (per sheet {min(per_sheet.values())}-"
              f"{max(per_sheet.values())}) | tiles per block min/median/max "
              f"{sizes[0]}/{statistics.median(sizes):g}/{sizes[-1]} | blocks under 4 tiles "
              f"{sum(1 for s in sizes if s < 4)} | tiles overlapping another block: "
              f"same sheet {len(same)} ({100 * len(same) / n:.1f} %), other sheet "
              f"{len(other)} ({100 * len(other) / n:.1f} %)")
        for name in disagree[:5]:
            print(f"    disagreement: {name} index {by_index[name]} metres {by_metres[name]}")
    print(f"sheet blocks: {len(sheet_sizes)}")


def main() -> None:
    """Report every frame."""
    print("Block census for wave S (design information; no detection or reference read).")
    for frame in FRAMES:
        report(frame)


if __name__ == "__main__":
    main()
