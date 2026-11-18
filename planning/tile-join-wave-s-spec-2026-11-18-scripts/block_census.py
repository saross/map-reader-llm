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
4. an **arithmetic consistency check**: the block computed from the pixel
   offsets in the tile's name, and again from the same offsets mapped into
   metres through the sheet's origin and pixel size. The origin and pixel
   size cancel, so this checks only the floating-point arithmetic of the
   block rule. It is NOT a geometry check: a tile whose footprint has been
   displaced passes it (Astra, wave S review S2);
5. an **independent geometry and name check**, for every frame whose tile
   rasters are tracked with world files: each tile's nominal footprint is
   read from its own raster (the ``.pgw`` world file beside the tracked
   PNG, and the PNG's width and height), never from the bounds file or the
   name. Then (a) the name is checked against the raster: the sheet origin
   implied by every tile (``west - x * res``, ``north + y * res``) must be
   one point per sheet, and the tile must sit in its ``map_name``'s raster
   directory; (b) the bounds geometry is checked against the nominal
   footprint, with clipping treated explicitly: an unclipped polygon must
   equal the footprint, and a clipped one must lie inside it and keep at
   least two of its edges; (c) the block is computed again from the
   raster's nominal centre through the sheet origin, and from an unclipped
   polygon's own centre, and both must equal the name route. A clipped
   polygon's centroid is never used for membership; the script counts how
   often it would have moved a tile to another block;
6. a **red sentinel** for check 5: one unclipped footprint displaced by a
   stride, and again by 10 m, without changing its name, and one tile's
   ``map_name`` changed to another sheet. Each mutation must fail check 5,
   and the arithmetic check of item 4 is shown passing the displaced
   footprint.

Frames whose rasters are not tracked (the 256 px frame and the 55-map
frame; ``.gitignore`` ignores ``inputs/tiles_256/*/`` and
``inputs/tiles_384_55maps/``) are reported as unchecked here; wave S's S.0
runs check 5 on them where their rasters are kept.

The block rule is the specification's § 3.2: square blocks laid on each
sheet's own raster grid, origin at the north-west corner of the sheet's pixel
(0, 0), sides along the raster's columns and rows (UTM easting and southing),
side ``S`` sheet pixels; a tile belongs to the block holding the centre of its
nominal (unclipped) pixel window. Partial blocks at a sheet's east and south
edges, and blocks thinned by holes in a frame, are kept as they fall.

It reads only the bounds GeoJSON files and the tracked tile rasters' world
files and PNG headers, and imports nothing beyond the standard library, so
it does not depend on the scorer or on the machine's virtual environment
(D70). No detection, reference, or model output is read.

Usage::

    python planning/tile-join-wave-s-spec-2026-11-18-scripts/block_census.py \
        > planning/tile-join-wave-s-spec-2026-11-18-scripts/block_census.txt

Created: 2026-11-18 (drafting for S169, amd-tower)
Revised: 2026-11-18 (Astra's round 1, S2: route relabelled; checks 5 and 6)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import re
import statistics
import struct
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

#: Tracked raster directory (one subdirectory per sheet, holding each
#: tile's PNG and ``.pgw`` world file) for each frame whose rasters are in
#: git. Frames absent from this map are reported as unchecked.
RASTER_DIRS: dict[str, str] = {
    "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson": "inputs/tiles_384",
    "inputs/vectors/bounds/384/full_evaluation_bounds.geojson": "inputs/tiles_384",
    "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson": "inputs/tiles_384",
    "inputs/vectors/bounds/384/h10_test_bounds.geojson": "inputs/tiles_384",
    "inputs/vectors/bounds/full_evaluation_bounds.geojson": "inputs/tiles",
    "outputs/h13/scoring/bounds/h13_common_bounds.geojson": "inputs/tiles",
}

#: Tolerance (metres) for "the same edge" and "the same sheet origin". The
#: observed agreement is far tighter; a displacement of one sheet pixel
#: (about 5 m) is 500 times this.
GEOMETRY_TOL_M = 0.01

#: The primary block side, used by the clipping diagnostics of check 5.
PRIMARY_SIDE_PX = 1344


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
    """Block of a tile from its name's offsets mapped into metres.

    This is an ARITHMETIC CONSISTENCY CHECK, not an independent route. The
    centre is the name's pixel window ``[xpx, xpx + T)`` mapped through the
    sheet's origin and pixel size, and the block index then subtracts the
    same origin and divides by the same pixel size, so the result reduces
    algebraically to :func:`block_by_index`. Agreement shows only that the
    floating-point arithmetic of the block rule is sound; it cannot detect
    a footprint that disagrees with its name (Astra, wave S review S2).
    The independent check is :func:`geometry_check`.
    """
    m = mpp[tile["sheet"]]
    x0, y0 = origins[tile["sheet"]]
    centre_e = x0 + (tile["xpx"] + tile_px / 2) * m
    centre_n = y0 - (tile["ypx"] + tile_px / 2) * m
    side_m = side_px * m
    return (tile["sheet"], int((centre_e - x0) // side_m), int((y0 - centre_n) // side_m))


def png_size(path: Path) -> tuple[int, int]:
    """Width and height of a PNG, read from its IHDR chunk.

    Args:
        path: A PNG file.

    Returns:
        ``(width, height)`` in pixels.

    Raises:
        ValueError: If the file is not a PNG (for example a Git Large File
            Storage pointer).
    """
    with path.open("rb") as handle:
        head = handle.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a PNG: {path}")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def nominal_footprint(raster_dir: Path, tile: dict) -> dict | None:
    """A tile's nominal footprint, read from its own raster only.

    The world file gives the pixel size and the centre of the raster's
    upper-left pixel; the PNG header gives the raster's size. Neither the
    bounds file nor the tile name's offsets enter.

    Args:
        raster_dir: The frame's tracked raster directory.
        tile: Output of :func:`load_tiles`; its ``sheet`` picks the
            subdirectory, so a wrong ``map_name`` finds no raster.

    Returns:
        ``{"w", "e", "s", "n", "res", "rotated", "width", "height"}`` in
        EPSG:32635 metres, or ``None`` if the sheet's directory has no
        raster of that name.
    """
    png = raster_dir / tile["sheet"] / tile["name"]
    world = png.with_suffix(".pgw")
    if not (png.is_file() and world.is_file()):
        return None
    a, d, b, e, c, f = (float(v) for v in world.read_text().split())
    width, height = png_size(png)
    west, north = c - a / 2, f - e / 2
    return {"w": west, "n": north, "e": west + width * a, "s": north + height * e,
            "res": a, "res_y": -e, "rotated": d != 0.0 or b != 0.0,
            "width": width, "height": height}


def geometry_check(tiles: list[dict], raster_dir: Path, tile_px: int,
                   stride: int) -> dict:
    """Check every tile's name and bounds geometry against its own raster.

    Args:
        tiles: Output of :func:`load_tiles`.
        raster_dir: The frame's tracked raster directory.
        tile_px: The frame's tile size in pixels.
        stride: The frame's stride in pixels.

    Returns:
        A summary dict: counts of unclipped and clipped tiles, the clip
        classes, failures of each kind (with up to five names each), the
        largest edge deviation of an unclipped tile, and the clipping
        diagnostics against the primary block side.
    """
    fails: dict[str, list[str]] = defaultdict(list)
    feet: dict[str, dict] = {}
    implied: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for t in tiles:
        if not t["name"].startswith(t["sheet"] + "_x"):
            fails["name does not carry its map_name"].append(t["name"])
        foot = nominal_footprint(raster_dir, t)
        if foot is None:
            fails["no raster for (map_name, tile_name)"].append(t["name"])
            continue
        if foot["rotated"] or abs(foot["res"] - foot["res_y"]) > 1e-9:
            fails["raster rotated or pixels not square"].append(t["name"])
        if (foot["width"], foot["height"]) != (tile_px, tile_px):
            fails["raster size is not the tile size"].append(t["name"])
        feet[t["name"]] = foot
        implied[t["sheet"]].append((foot["w"] - t["xpx"] * foot["res"],
                                    foot["n"] + t["ypx"] * foot["res"]))
    origin = {s: (statistics.median(x for x, _ in v), statistics.median(y for _, y in v))
              for s, v in implied.items()}
    unclipped, clipped, max_dev = 0, Counter(), 0.0
    centre_outside, centroid_moves = 0, 0
    tol = GEOMETRY_TOL_M
    for t in tiles:
        foot = feet.get(t["name"])
        if foot is None:
            continue
        res = foot["res"]
        ox, oy = origin[t["sheet"]]
        # (a) the name against the raster: one sheet origin for every tile.
        if (abs(foot["w"] - t["xpx"] * res - ox) > tol
                or abs(foot["n"] + t["ypx"] * res - oy) > tol):
            fails["name offsets disagree with the raster"].append(t["name"])
        # (b) the bounds geometry against the nominal footprint.
        delta = {k: t[k] - foot[k] for k in ("w", "e", "s", "n")}
        inside = (delta["w"] > -tol and delta["e"] < tol
                  and delta["s"] > -tol and delta["n"] < tol)
        kept = [k for k, v in delta.items() if abs(v) <= tol]
        if len(kept) == 4:
            unclipped += 1
            max_dev = max(max_dev, max(abs(v) for v in delta.values()))
        elif inside and len(kept) >= 2 and t["e"] > t["w"] and t["n"] > t["s"]:
            clipped["clipped " + "+".join(k for k in "wesn" if k not in kept)] += 1
            # Clipping diagnostics: the nominal centre may fall outside the
            # clipped polygon, and the clipped centroid may sit in another
            # block. Membership always uses the nominal centre.
            cx = foot["w"] + tile_px / 2 * res
            cy = foot["n"] - tile_px / 2 * res
            if not (t["w"] <= cx <= t["e"] and t["s"] <= cy <= t["n"]):
                centre_outside += 1
            side_m = PRIMARY_SIDE_PX * res
            nominal_block = (int((cx - ox) // side_m), int((oy - cy) // side_m))
            gx, gy = (t["w"] + t["e"]) / 2, (t["s"] + t["n"]) / 2
            if (int((gx - ox) // side_m), int((oy - gy) // side_m)) != nominal_block:
                centroid_moves += 1
        else:
            fails["bounds polygon is not the nominal footprint or a clip of it"].append(
                t["name"])
            continue
        # (c) block from the raster's nominal centre, and from an unclipped
        # polygon's own centre, both through the raster's sheet origin.
        for side in SIDES_PX:
            side_m = side * res
            by_name = block_by_index(t, tile_px, side)[1:]
            cx = foot["w"] + tile_px / 2 * res
            cy = foot["n"] - tile_px / 2 * res
            if (int((cx - ox) // side_m), int((oy - cy) // side_m)) != by_name:
                fails[f"raster-centre block differs from name block (side {side})"].append(
                    t["name"])
            if len(kept) == 4:
                gx, gy = (t["w"] + t["e"]) / 2, (t["s"] + t["n"]) / 2
                if (int((gx - ox) // side_m), int((oy - gy) // side_m)) != by_name:
                    fails[f"bounds-centre block differs from name block (side {side})"].append(
                        t["name"])
    return {"checked": len(feet), "unclipped": unclipped, "clipped": clipped,
            "max_dev_m": max_dev, "fails": fails, "centre_outside": centre_outside,
            "centroid_moves": centroid_moves, "stride": stride}


def print_geometry(result: dict, label: str) -> None:
    """Print one :func:`geometry_check` summary."""
    n_fail = sum(len(v) for v in result["fails"].values())
    clips = ", ".join(f"{k} {v}" for k, v in sorted(result["clipped"].items())) or "none"
    print(f"{label}: tiles checked {result['checked']}; unclipped {result['unclipped']} "
          f"(largest edge deviation {result['max_dev_m']:.1e} m); clipped "
          f"{sum(result['clipped'].values())} ({clips}); failures {n_fail}")
    if result["clipped"]:
        print(f"    clipped tiles whose nominal centre lies outside the clipped polygon "
              f"{result['centre_outside']}; whose clipped centroid would fall in another "
              f"primary block {result['centroid_moves']} (membership uses the nominal centre)")
    for kind, names in sorted(result["fails"].items()):
        print(f"    FAIL {kind}: {len(names)} (e.g. {', '.join(names[:5])})")


def red_sentinel(tiles: list[dict], raster_dir: Path, tile_px: int, stride: int,
                 mpp: dict[str, float], origins: dict[str, tuple[float, float]]) -> None:
    """Show that the geometry check fails on displaced or relabelled tiles.

    Mutates copies of one unclipped tile (the first by name): its bounds
    footprint moved east by one stride, then by 10 m, with its name
    unchanged; and its ``map_name`` changed to another sheet. Each must make
    :func:`geometry_check` report a failure. The arithmetic check of
    :func:`block_by_metres` is shown passing the stride-displaced tile.
    """
    baseline = geometry_check(tiles, raster_dir, tile_px, stride)
    target = None
    for t in sorted(tiles, key=lambda u: u["name"]):
        foot = nominal_footprint(raster_dir, t)
        if foot and all(abs(t[k] - foot[k]) <= GEOMETRY_TOL_M for k in ("w", "e", "s", "n")):
            target = t
            break
    if target is None:
        print("red sentinel: no unclipped tile to displace")
        return
    others = sorted({t["sheet"] for t in tiles} - {target["sheet"]})
    stride_m = stride * mpp[target["sheet"]]
    mutations = {
        f"footprint moved one stride ({stride_m:.1f} m) east, name unchanged":
            {"w": target["w"] + stride_m, "e": target["e"] + stride_m},
        "footprint moved 10 m east, name unchanged":
            {"w": target["w"] + 10.0, "e": target["e"] + 10.0},
        f"map_name changed to {others[0]}": {"sheet": others[0]},
    }
    n_base = sum(len(v) for v in baseline["fails"].values())
    print(f"red sentinel on {target['name']} (baseline failures {n_base}):")
    for label, change in mutations.items():
        mutated = [dict(t, **change) if t is target else t for t in tiles]
        result = geometry_check(mutated, raster_dir, tile_px, stride)
        n_fail = sum(len(v) for v in result["fails"].values())
        kinds = "; ".join(sorted(result["fails"]))
        print(f"    {label}: geometry-check failures {n_fail} -> "
              f"{'RED (caught)' if n_fail > n_base else 'GREEN (MISSED)'} [{kinds}]")
    moved = dict(target, w=target["w"] + stride_m, e=target["e"] + stride_m)
    same = all(block_by_index(moved, tile_px, s) == block_by_metres(moved, tile_px, s, mpp,
                                                                       origins)
               for s in SIDES_PX)
    print(f"    the arithmetic consistency check on the stride-displaced tile: "
          f"{'passes (it cannot see geometry)' if same else 'fails'}")


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
              f"{side_m[1] / 1000:.2f} km | arithmetic routes disagree on {len(disagree)} tiles | "
              f"blocks {len(sizes)} (per sheet {min(per_sheet.values())}-"
              f"{max(per_sheet.values())}) | tiles per block min/median/max "
              f"{sizes[0]}/{statistics.median(sizes):g}/{sizes[-1]} | blocks under 4 tiles "
              f"{sum(1 for s in sizes if s < 4)} | tiles overlapping another block: "
              f"same sheet {len(same)} ({100 * len(same) / n:.1f} %), other sheet "
              f"{len(other)} ({100 * len(other) / n:.1f} %)")
        for name in disagree[:5]:
            print(f"    disagreement: {name} index {by_index[name]} metres {by_metres[name]}")
    print(f"sheet blocks: {len(sheet_sizes)}")
    raster_text = RASTER_DIRS.get(path_text)
    if raster_text is None:
        print("independent geometry check: not run here (this frame's rasters are not "
              "tracked; S.0 runs it where they are kept)")
        return
    raster_dir = REPO / raster_text
    print_geometry(geometry_check(tiles, raster_dir, tile_px, stride),
                   f"independent geometry check against {raster_text}")
    if path_text == FRAMES[0]:
        red_sentinel(tiles, raster_dir, tile_px, stride, mpp, origins)


def main() -> None:
    """Report every frame."""
    print("Block census for wave S (design information; no detection or reference read).")
    print("'arithmetic routes' is a consistency check of the block arithmetic, not a "
          "geometry check; the independent geometry check follows each frame.")
    for frame in FRAMES:
        report(frame)


if __name__ == "__main__":
    main()
