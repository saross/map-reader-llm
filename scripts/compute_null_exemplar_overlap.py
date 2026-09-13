#!/usr/bin/env python3
"""Compute the evaluation tiles whose windows overlap a few-shot null exemplar.

Three "null" (empty) exemplar tiles in the few-shot library
(``inputs/examples/null-tiles/``) were never excluded from the Gold-Standard
evaluation frames, so any image-bearing configuration showed the model those
pixels labelled "no mounds here" and was then scored on them. This script
lists, for each Gold-Standard frame, every tile whose WINDOW overlaps any
null exemplar window, so those tiles can be dropped for a leak sensitivity
analysis.

Geometry
--------
A tile file name encodes the top-left PIXEL offset of its window on the named
map sheet: ``<map>_x<X>_y<Y>.png``. Exposure to the leak is a property of the
window the model was shown, not of the (sometimes clipped) polygon the scorer
credits detections inside, so the overlap test is run on windows.

Windows are compared in pixel space on the same sheet, which is exact:

    x_tile < x_null + 512  and  x_tile + size > x_null   (and likewise in y)

That is only valid if both frames are cut from the same source raster at the
same resolution with the same origin, so the script DERIVES a per-sheet
affine (origin, metres per pixel) from the 512 px frame — asserting that one
resolution and one origin fit all 85 of that sheet's tiles exactly — and then
asserts that every tile of every other frame is either exactly its nominal
window under that same affine or a CLIPPED subset of it. Each overlap verdict
is then cross-checked in ground space against the null window's projected
envelope.

Because the Era-2 board frame is the Era-2 carrier tiles clipped to the B
tiling's union, 32 of its 487 tiles carry a clipped polygon. For those the
record also reports whether the clipped polygon still intersects the null
window — informational, not a criterion: a tile is exposed if its window was.

Usage:
    python scripts/compute_null_exemplar_overlap.py \
        --out results/null-exemplar-sensitivity-2026-09-13/overlap_tiles.json \
        --reduced-bounds-dir results/null-exemplar-sensitivity-2026-09-13/bounds

Created: 2026-09-13
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

NULL_TILE_MANIFEST = BASE_DIR / "inputs/examples/null-tiles/null_tiles_manifest.json"
NULL_WINDOW_PX = 512

#: The frame the per-sheet affine is derived from: unclipped, one tile size.
AFFINE_FRAME = "inputs/vectors/bounds/full_evaluation_bounds.geojson"
AFFINE_FRAME_TILE_PX = 512

#: The frames under test: (frame_id, bounds path, tile size px, step px).
FRAMES: list[tuple[str, str, int, int]] = [
    ("era2-b-487",
     "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson", 384, 336),
    ("era1-full-340", AFFINE_FRAME, 512, 448),
]

TILE_NAME_RE = re.compile(r"^(?P<map>.+)_x(?P<x>\d+)_y(?P<y>\d+)\.png$")

#: Tolerance in metres for the affine assertions (coordinates are ~1e6 m).
TOL_M = 1e-3


def parse_tile_name(name: str) -> tuple[str, int, int]:
    """Split a tile file name into (map sheet, x pixel offset, y pixel offset).

    Args:
        name: A tile file name such as ``K-35-052-4_32635_x896_y1792.png``.

    Returns:
        ``(map_name, x_px, y_px)``.

    Raises:
        ValueError: if the name does not carry the ``_x<X>_y<Y>.png`` suffix.
    """
    match = TILE_NAME_RE.match(name)
    if match is None:
        raise ValueError(f"tile name does not encode a pixel window: {name!r}")
    return match["map"], int(match["x"]), int(match["y"])


def read_frame(path: Path) -> dict[str, tuple[float, float, float, float]]:
    """Read a bounds GeoJSON into ``{tile_name: (minx, miny, maxx, maxy)}``.

    Only the axis-aligned envelope is needed: every committed bound polygon is
    a rectangle, or (for a clipped tile) contained in one.

    Args:
        path: Absolute path to a bounds GeoJSON with ``tile_name`` properties.

    Returns:
        Mapping from tile name to its projected envelope.
    """
    payload = json.loads(path.read_text())
    envelopes: dict[str, tuple[float, float, float, float]] = {}
    for feature in payload["features"]:
        ring = feature["geometry"]["coordinates"][0]
        xs = [pt[0] for pt in ring]
        ys = [pt[1] for pt in ring]
        envelopes[feature["properties"]["tile_name"]] = (
            min(xs), min(ys), max(xs), max(ys)
        )
    return envelopes


def derive_sheet_affines(
    envelopes: dict[str, tuple[float, float, float, float]],
    tile_px: int,
) -> dict[str, tuple[float, float, float]]:
    """Derive one (resolution, origin x, origin y-top) per map sheet.

    The pixel grid's y axis runs downward while the projected northing runs
    upward, so the origin is the sheet's TOP-left corner: a tile at pixel
    ``(x, y)`` has ``minx = origin_x + x * res`` and
    ``maxy = origin_y_top - y * res``.

    Args:
        envelopes: Tile envelopes of an unclipped, single-tile-size frame.
        tile_px: That frame's tile side length in pixels.

    Returns:
        ``{map_name: (metres_per_pixel, origin_x, origin_y_top)}``.

    Raises:
        AssertionError: if a sheet's tiles do not share one resolution and one
            origin exactly — the assumption the pixel-space overlap test rests on.
    """
    per_sheet: dict[str, list[tuple[int, int, tuple[float, ...]]]] = {}
    for name, envelope in envelopes.items():
        map_name, x_px, y_px = parse_tile_name(name)
        per_sheet.setdefault(map_name, []).append((x_px, y_px, envelope))

    affines: dict[str, tuple[float, float, float]] = {}
    for map_name, rows in sorted(per_sheet.items()):
        resolutions = set()
        for _x, _y, (minx, miny, maxx, maxy) in rows:
            resolutions.add(round((maxx - minx) / tile_px, 9))
            resolutions.add(round((maxy - miny) / tile_px, 9))
        assert len(resolutions) == 1, (
            f"{map_name}: tiles disagree on resolution ({sorted(resolutions)})"
        )
        res = resolutions.pop()
        origins_x = {round(minx - x_px * res, 4)
                     for x_px, _y, (minx, _a, _b, _c) in rows}
        origins_y = {round(maxy + y_px * res, 4)
                     for _x, y_px, (_a, _b, _c, maxy) in rows}
        assert len(origins_x) == 1 and len(origins_y) == 1, (
            f"{map_name}: tiles disagree on the sheet origin "
            f"(x={sorted(origins_x)}, y={sorted(origins_y)})"
        )
        affines[map_name] = (res, origins_x.pop(), origins_y.pop())
        print(f"  {map_name}: {res:.9f} m/px, origin "
              f"({affines[map_name][1]:.4f}, {affines[map_name][2]:.4f}), "
              f"{len(rows)} tiles")
    return affines


def nominal_window(affines: dict[str, tuple[float, float, float]],
                   map_name: str, x_px: int, y_px: int,
                   size_px: int) -> tuple[float, float, float, float]:
    """Project a pixel window to its nominal ground envelope.

    Args:
        affines: Per-sheet ``(res, origin_x, origin_y_top)``.
        map_name: The sheet the window sits on.
        x_px: Window's top-left x pixel offset.
        y_px: Window's top-left y pixel offset.
        size_px: Window side length in pixels.

    Returns:
        ``(minx, miny, maxx, maxy)`` in the frame's projected CRS.
    """
    res, origin_x, origin_y_top = affines[map_name]
    minx = origin_x + x_px * res
    maxy = origin_y_top - y_px * res
    return (minx, maxy - size_px * res, minx + size_px * res, maxy)


def windows_overlap(a_x: int, a_y: int, a_size: int,
                    b_x: int, b_y: int, b_size: int) -> bool:
    """Return True when two axis-aligned pixel windows share positive area.

    Args:
        a_x: First window's top-left x pixel offset.
        a_y: First window's top-left y pixel offset.
        a_size: First window's side length in pixels.
        b_x: Second window's top-left x pixel offset.
        b_y: Second window's top-left y pixel offset.
        b_size: Second window's side length in pixels.

    Returns:
        True when the two windows intersect with strictly positive area.
    """
    return (a_x < b_x + b_size and a_x + a_size > b_x
            and a_y < b_y + b_size and a_y + a_size > b_y)


def envelopes_overlap(a: tuple[float, float, float, float],
                      b: tuple[float, float, float, float],
                      tol: float = TOL_M) -> bool:
    """Return True when two projected envelopes share positive area.

    Args:
        a: First envelope ``(minx, miny, maxx, maxy)``.
        b: Second envelope ``(minx, miny, maxx, maxy)``.
        tol: Slack in metres, so a shared edge does not read as an overlap.

    Returns:
        True when the envelopes intersect with strictly positive area.
    """
    return (a[0] < b[2] - tol and a[2] > b[0] + tol
            and a[1] < b[3] - tol and a[3] > b[1] + tol)


def main() -> int:
    """CLI entry point: compute the overlap sets and write the JSON record."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True,
                        help="Where the overlap record JSON is written.")
    parser.add_argument("--reduced-bounds-dir", type=Path, default=None,
                        help="Optional directory to write frame-minus-overlap "
                             "bounds GeoJSONs into (one per frame).")
    args = parser.parse_args()

    # ── The three null exemplar windows ───────────────────────────────
    manifest = json.loads(NULL_TILE_MANIFEST.read_text())
    nulls: list[dict[str, Any]] = []
    for entry in manifest["tiles"]:
        map_name, x_px, y_px = parse_tile_name(entry["filename"])
        assert map_name == entry["map"], (map_name, entry["map"])
        nulls.append({
            "tile_name": entry["filename"],
            "map_name": map_name,
            "x_px": x_px,
            "y_px": y_px,
            "size_px": NULL_WINDOW_PX,
        })
    null_names = {n["tile_name"] for n in nulls}
    print(f"{len(nulls)} null exemplar window(s):")
    for null in nulls:
        print(f"  {null['tile_name']}  pixel ({null['x_px']}, {null['y_px']}) "
              f"{null['size_px']} px")

    # ── One affine per sheet, derived from the unclipped 512 px frame ──
    print(f"Deriving per-sheet affines from {AFFINE_FRAME} ...")
    affine_envelopes = read_frame(BASE_DIR / AFFINE_FRAME)
    affines = derive_sheet_affines(affine_envelopes, AFFINE_FRAME_TILE_PX)
    for null in nulls:
        null["ground_envelope"] = nominal_window(
            affines, null["map_name"], null["x_px"], null["y_px"],
            null["size_px"])

    frames_out: list[dict[str, Any]] = []
    for frame_id, rel_bounds, size_px, step_px in FRAMES:
        bounds_path = BASE_DIR / rel_bounds
        envelopes = read_frame(bounds_path)
        names = sorted(envelopes)

        # ── Assert every tile is its nominal window, or clipped inside it ──
        n_exact = n_clipped = 0
        for name in names:
            map_name, x_px, y_px = parse_tile_name(name)
            nominal = nominal_window(affines, map_name, x_px, y_px, size_px)
            got = envelopes[name]
            if all(abs(g - n) < TOL_M for g, n in zip(got, nominal)):
                n_exact += 1
                continue
            assert (got[0] >= nominal[0] - TOL_M and got[1] >= nominal[1] - TOL_M
                    and got[2] <= nominal[2] + TOL_M
                    and got[3] <= nominal[3] + TOL_M), (
                f"{frame_id}/{name}: committed polygon {got} is neither its "
                f"nominal window {nominal} nor contained in it — the frames do "
                f"not share a pixel grid and the overlap test is invalid"
            )
            n_clipped += 1
        print(f"{frame_id}: {n_exact} tile(s) exactly their nominal window, "
              f"{n_clipped} clipped inside it")

        overlaps: list[dict[str, Any]] = []
        for name in names:
            map_name, x_px, y_px = parse_tile_name(name)
            hits = sorted(n["tile_name"] for n in nulls
                          if n["map_name"] == map_name
                          and windows_overlap(x_px, y_px, size_px,
                                              n["x_px"], n["y_px"], n["size_px"]))
            # Ground-space cross-check of the same verdict on every null.
            nominal = nominal_window(affines, map_name, x_px, y_px, size_px)
            geo_hits = sorted(n["tile_name"] for n in nulls
                              if n["map_name"] == map_name
                              and envelopes_overlap(nominal, n["ground_envelope"]))
            assert hits == geo_hits, (
                f"{frame_id}/{name}: pixel-space overlap {hits} disagrees with "
                f"ground-space overlap {geo_hits}"
            )
            if not hits:
                continue
            overlaps.append({
                "tile_name": name,
                "map_name": map_name,
                "x_px": x_px,
                "y_px": y_px,
                "overlaps_null": hits,
                "is_null_window_itself": name in null_names,
                "committed_polygon_also_intersects": sorted(
                    n["tile_name"] for n in nulls
                    if n["map_name"] == map_name
                    and envelopes_overlap(envelopes[name], n["ground_envelope"])
                ),
            })

        print(f"{frame_id}: {len(overlaps)} of {len(names)} tiles overlap a null "
              f"window ({size_px} px on a {step_px} px step)")
        frames_out.append({
            "frame_id": frame_id,
            "bounds": rel_bounds,
            "n_tiles": len(names),
            "tile_size_px": size_px,
            "tile_step_px": step_px,
            "n_tiles_exact_window": n_exact,
            "n_tiles_clipped": n_clipped,
            "n_overlap": len(overlaps),
            "n_reduced": len(names) - len(overlaps),
            "overlap_tiles": [o["tile_name"] for o in overlaps],
            "overlap_detail": overlaps,
        })

        if args.reduced_bounds_dir is not None:
            args.reduced_bounds_dir.mkdir(parents=True, exist_ok=True)
            drop = {o["tile_name"] for o in overlaps}
            payload = json.loads(bounds_path.read_text())
            payload["features"] = [f for f in payload["features"]
                                   if f["properties"]["tile_name"] not in drop]
            assert len(payload["features"]) == len(names) - len(drop)
            out = args.reduced_bounds_dir / f"{frame_id}_minus_null_overlap.geojson"
            out.write_text(json.dumps(payload) + "\n")
            rel_out = out.resolve().relative_to(BASE_DIR)
            frames_out[-1]["reduced_bounds"] = str(rel_out)
            print(f"  wrote {rel_out} ({len(payload['features'])} tiles)")

    record = {
        "_README": (
            "Evaluation tiles whose windows overlap a few-shot null exemplar "
            "window. Produced by scripts/compute_null_exemplar_overlap.py for "
            "the null-exemplar leak sensitivity analysis of 2026-09-13."
        ),
        "generated_by": "scripts/compute_null_exemplar_overlap.py",
        "null_exemplars": nulls,
        "null_window_px": NULL_WINDOW_PX,
        "geometry": {
            "method": ("axis-aligned overlap of tile WINDOWS in pixel space on "
                       "the same map sheet, cross-checked in ground space"),
            "tile_name_encodes": ("<map>_x<X>_y<Y>.png gives the window's "
                                  "top-left PIXEL offset on that sheet"),
            "overlap_rule": ("x_tile < x_null + 512 and x_tile + size > x_null, "
                             "and likewise in y (strictly positive area)"),
            "exposure_is_the_window": (
                "exposure to the leak is a property of the window the model "
                "was shown, so a tile counts as exposed when its window "
                "overlaps, whether or not its committed (clipped) scoring "
                "polygon does"
            ),
            "affine_source": AFFINE_FRAME,
            "affine_per_sheet": {k: {"m_per_px": v[0], "origin_x": v[1],
                                     "origin_y_top": v[2]}
                                 for k, v in affines.items()},
            "validity": (
                "one resolution and one origin fit all 85 tiles of each sheet "
                "in the 512 px frame exactly (asserted), and every tile of "
                "every frame under test is either exactly its nominal window "
                "under that same affine or a clipped subset of it (asserted), "
                "so the frames share one pixel grid and the pixel-space test "
                "is exact"
            ),
        },
        "frames": frames_out,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n")
    print(f"wrote {args.out.resolve().relative_to(BASE_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
