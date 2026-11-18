#!/usr/bin/env python3
"""
Sheet-boundary check of the 55-map ground truth (tile-join Wave 1, W1.0).

The parent record's § 2.6 (``planning/tile-join-resolution-2026-11-01.md``)
owes, before Wave 2, the 55-map equivalent of the Era-2 check in
``planning/tile-join-resolution-2026-11-01-scripts/sheet_boundary_check.py``.
Sheet-specific scoring (D73 (2)) is safe only if no reference meets another
sheet's tile on map content: if adjacent sheets print the same mound and
only one copy was digitised, a correct detection on the other sheet would
score as a false positive. This script answers three questions for each
tracked 55-map reference file, on the 55-map frame:

1. **Cross-sheet reference pairs.** Every pair of references recorded on
   different sheets (``source_map``) lying within 500 m of each other,
   with counts at 50, 100, 200, 500, and 1,000 m.
2. **Cross-sheet point–tile contacts.** Every reference lying inside a
   frame tile of a sheet other than its own, with its pixel position in
   that tile, read from the tile's ESRI world file (``.pgw``).
3. **What the pixels show at each contact** (only with ``--pixels``). The
   tile image is read and measured, not judged by eye: the fraction of
   near-black (no-data) pixels in a window around the point, the extent of
   non-black content along the point's row and column, and the colour at
   the point. A crop of each contact is saved for inspection.

Geometry (questions 1 and 2) uses only the standard library and imports
nothing from the project's scorer, as the Era-2 script does, so its answer
does not depend on the code under review. A tile's sheet is the frame's
own reading of its name: the text before ``_x<digits>_y<digits>``, which is
the scorer's ``get_map_name`` rule (``scripts/lib_advanced_metrics.py:959``)
and equals each tile's ``map_name`` property on this frame. Question 3
needs an image reader (Pillow and NumPy, from the reference environment);
it reads pixels only.

Usage (zbook, from a checkout of the branch; tiles are gitignored and are
read from the main checkout by ``--tile-dir``)::

    ~/Code/map-reader-llm/.venv/bin/python \\
        reports/tile-join-wave-1/scripts/sheet_check_55map.py \\
        --tile-dir ~/Code/map-reader-llm/inputs/tiles_384_55maps \\
        --pixels --crop-dir ~/scratch/wave1/w10/sheet-check/crops \\
        --json-out reports/tile-join-wave-1/scripts/sheet_check_55map.json \\
        > reports/tile-join-wave-1/scripts/sheet_check_55map.txt

Created: 2026-11-18 (tile-join Wave 1, W1.0, amd-tower / zbook)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
#: Every tracked 55-map reference file (``git ls-files inputs/vectors/references``).
REFERENCE_FILES = (
    "inputs/vectors/references/best-available-gt-55maps-r2.geojson",
    "inputs/vectors/references/best-available-gt-55maps.geojson",
    "inputs/vectors/references/canonical-gt-55maps-r50.geojson",
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson",
    "inputs/vectors/references/student-mounds-55maps.geojson",
)
#: The scorer's tile-name rule (``lib_advanced_metrics._MAP_NAME_RE``), restated.
MAP_NAME_RE = re.compile(r"^(.+?)_x\d+_y\d+(?:\.png)?$")
PAIR_LIMIT_M = 500.0
PAIR_COUNT_LIMITS = (50, 100, 200, 500, 1000)
#: A pixel is "near-black" (no-data padding) if every channel is at or below this.
NEAR_BLACK_MAX = 20
#: Half-width of the measurement window around a point, in pixels.
WINDOW_HALF = 8
#: Half-width of the saved crop, in pixels, and its enlargement factor.
CROP_HALF = 48
CROP_SCALE = 3

Ring = list[tuple[float, float]]


def sheet_of_tile(name: str) -> str:
    """Return a tile's sheet by the scorer's name rule.

    Args:
        name: A tile name such as ``K-35-042-3_x0_y0.png``.

    Returns:
        The text before ``_x<digits>_y<digits>``, or ``"Unknown"``.
    """
    match = MAP_NAME_RE.match(name)
    return match.group(1) if match else "Unknown"


def load_tiles(path: Path) -> list[dict[str, Any]]:
    """Read the frame's tiles with their rings, bounding boxes, and sheets.

    Args:
        path: GeoJSON of tile polygons with ``tile_name`` (and ``map_name``).

    Returns:
        One dictionary per tile: name, sheet, map_name, ring, bbox.
    """
    data = json.loads(path.read_text())
    tiles = []
    for feature in data["features"]:
        geometry = feature["geometry"]
        coords = geometry["coordinates"]
        ring = coords[0] if geometry["type"] == "Polygon" else coords[0][0]
        ring = [(float(p[0]), float(p[1])) for p in ring]
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        name = feature["properties"]["tile_name"]
        tiles.append({
            "name": name,
            "sheet": sheet_of_tile(name),
            "map_name": feature["properties"].get("map_name"),
            "ring": ring,
            "bbox": (min(xs), min(ys), max(xs), max(ys)),
        })
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


def load_references(path: Path) -> list[tuple[str, str, float, float]]:
    """Read references as (sheet, id, x, y), the sheet from ``source_map``.

    Args:
        path: A 55-map reference GeoJSON in the frame's projected system.

    Returns:
        One tuple per point (MultiPoint members flattened).
    """
    data = json.loads(path.read_text())
    out = []
    for index, feature in enumerate(data["features"]):
        props = feature["properties"]
        ident = str(props.get("gt_id") or props.get("uuid") or index)
        geometry = feature["geometry"]
        points = ([geometry["coordinates"]] if geometry["type"] == "Point"
                  else geometry["coordinates"])
        for point in points:
            out.append((props["source_map"], ident, float(point[0]), float(point[1])))
    return out


def cross_sheet_pairs(points: list[tuple[str, str, float, float]]) -> list[tuple]:
    """Every pair on different sheets within the widest count limit.

    Sorted by easting, so each point is compared only with the points whose
    easting is within the limit.

    Args:
        points: (sheet, id, x, y) tuples.

    Returns:
        (distance, sheet_a, id_a, sheet_b, id_b) tuples, nearest first.
    """
    limit = max(PAIR_COUNT_LIMITS)
    ordered = sorted(points, key=lambda p: p[2])
    pairs = []
    for i, (s1, f1, x1, y1) in enumerate(ordered):
        for s2, f2, x2, y2 in ordered[i + 1:]:
            if x2 - x1 > limit:
                break
            if s1 == s2:
                continue
            distance = math.hypot(x1 - x2, y1 - y2)
            if distance <= limit:
                pairs.append((distance, s1, f1, s2, f2))
    pairs.sort()
    return pairs


def nearest_cross_sheet(points: list[tuple[str, str, float, float]]) -> tuple | None:
    """The closest pair of references on different sheets, at any distance.

    Args:
        points: (sheet, id, x, y) tuples.

    Returns:
        (distance, sheet_a, id_a, sheet_b, id_b), or None if one sheet only.
    """
    ordered = sorted(points, key=lambda p: p[2])
    best: tuple | None = None
    for i, (s1, f1, x1, y1) in enumerate(ordered):
        for s2, f2, x2, y2 in ordered[i + 1:]:
            if best is not None and x2 - x1 > best[0]:
                break
            if s1 == s2:
                continue
            distance = math.hypot(x1 - x2, y1 - y2)
            if best is None or distance < best[0]:
                best = (distance, s1, f1, s2, f2)
    return best


def pixel_position(tile_dir: Path, tile: dict[str, Any], x: float,
                   y: float) -> tuple[float, float] | None:
    """Convert a map coordinate to (column, row) in a tile image.

    Args:
        tile_dir: Directory holding ``<sheet>/<stem>.pgw``.
        tile: Tile record from :func:`load_tiles`.
        x: Easting.
        y: Northing.

    Returns:
        (column, row) in pixels, or None if the world file is absent.
    """
    stem = tile["name"].removesuffix(".png")
    world = tile_dir / tile["sheet"] / f"{stem}.pgw"
    if not world.exists():
        return None
    a, _d, _b, e, c, f = (float(v) for v in world.read_text().split())
    return (x - c) / a, (y - f) / e


def content_span(mask_line: Any) -> tuple[int, int] | None:
    """First and last index of non-black content along one line of pixels.

    Args:
        mask_line: Boolean array, True where the pixel is content.

    Returns:
        (first, last), or None if the line holds no content.
    """
    import numpy as np  # noqa: PLC0415 (pixel stage only)

    idx = np.flatnonzero(mask_line)
    if idx.size == 0:
        return None
    return int(idx[0]), int(idx[-1])


def measure_pixels(png: Path, col: float, row: float, crop_path: Path | None
                   ) -> dict[str, Any]:
    """Measure whether a point in a tile lies on map content or padding.

    Args:
        png: Tile image.
        col: Point's column (may be fractional).
        row: Point's row.
        crop_path: Where to save an enlarged crop with the point marked, or
            None to skip.

    Returns:
        Measurements: the colour at the point, the near-black fraction of
        the window, the content span along the point's row and column, and
        whether the point lies inside each span.
    """
    import numpy as np  # noqa: PLC0415
    from PIL import Image, ImageDraw  # noqa: PLC0415

    with Image.open(png) as image:
        mode = image.mode
        rgba = np.asarray(image.convert("RGBA"))
    height, width = rgba.shape[:2]
    rgb = rgba[..., :3].astype(int)
    transparent = rgba[..., 3] == 0
    black = (rgb.max(axis=2) <= NEAR_BLACK_MAX) | transparent
    content = ~black
    c, r = int(math.floor(col)), int(math.floor(row))
    c_clamped = min(max(c, 0), width - 1)
    r_clamped = min(max(r, 0), height - 1)
    r0, r1 = max(r - WINDOW_HALF, 0), min(r + WINDOW_HALF + 1, height)
    c0, c1 = max(c - WINDOW_HALF, 0), min(c + WINDOW_HALF + 1, width)
    window = black[r0:r1, c0:c1]
    row_span = content_span(content[r_clamped, :])
    col_span = content_span(content[:, c_clamped])
    result = {
        "image_mode": mode,
        "image_size": [width, height],
        "pixel_in_image": 0 <= col < width and 0 <= row < height,
        "rgb_at_point": [int(v) for v in rgb[r_clamped, c_clamped]],
        "window_px": [int(c1 - c0), int(r1 - r0)],
        "window_near_black_fraction": round(float(window.mean()), 4),
        "row_content_span": row_span,
        "col_content_span": col_span,
        "inside_row_span": bool(row_span and row_span[0] <= c <= row_span[1]),
        "inside_col_span": bool(col_span and col_span[0] <= r <= col_span[1]),
        "tile_near_black_fraction": round(float(black.mean()), 4),
    }
    if crop_path is not None:
        crop_path.parent.mkdir(parents=True, exist_ok=True)
        box = (c - CROP_HALF, r - CROP_HALF, c + CROP_HALF, r + CROP_HALF)
        with Image.open(png) as image:
            crop = image.convert("RGB").crop(box)
        crop = crop.resize((crop.width * CROP_SCALE, crop.height * CROP_SCALE),
                           Image.NEAREST)
        draw = ImageDraw.Draw(crop)
        centre = CROP_HALF * CROP_SCALE
        draw.ellipse((centre - 9, centre - 9, centre + 9, centre + 9),
                     outline=(255, 0, 0), width=2)
        crop.save(crop_path)
        result["crop"] = str(crop_path)
    return result


def classify(measure: dict[str, Any]) -> str:
    """Name what the point lies on, from the measurements alone.

    ``padding`` needs both a window that is at least 95 % near-black and a
    point outside the content span of its row or column; ``map-content``
    needs a window under 50 % near-black with the point inside both spans.
    Anything else is ``ambiguous`` and is reported as such.

    Args:
        measure: The output of :func:`measure_pixels`.

    Returns:
        ``padding``, ``map-content``, or ``ambiguous``.
    """
    frac = measure["window_near_black_fraction"]
    outside = not (measure["inside_row_span"] and measure["inside_col_span"])
    if frac >= 0.95 and outside:
        return "padding"
    if frac < 0.5 and not outside:
        return "map-content"
    return "ambiguous"


def main() -> None:
    """Run the checks for every reference file and print the results."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tile-dir", type=Path,
                        default=PROJECT_ROOT / "inputs/tiles_384_55maps")
    parser.add_argument("--pixels", action="store_true",
                        help="measure the tile pixels at every contact")
    parser.add_argument("--crop-dir", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    tiles = load_tiles(BOUNDS)
    frame_sheets = sorted({t["sheet"] for t in tiles})
    mismatched = sum(1 for t in tiles if t["map_name"] != t["sheet"])
    print(f"frame: {BOUNDS.relative_to(PROJECT_ROOT)}: {len(tiles)} tiles, "
          f"{len(frame_sheets)} sheets; tiles whose map_name differs from the "
          f"name rule: {mismatched}")
    report: dict[str, Any] = {"frame": str(BOUNDS.relative_to(PROJECT_ROOT)),
                              "n_tiles": len(tiles), "n_sheets": len(frame_sheets),
                              "map_name_mismatches": mismatched, "references": {}}

    for ref_name in REFERENCE_FILES:
        points = load_references(PROJECT_ROOT / ref_name)
        sheets = sorted({p[0] for p in points})
        foreign_sheets = [s for s in sheets if s not in frame_sheets]
        print(f"\n=== {ref_name}: {len(points)} points on {len(sheets)} sheets; "
              f"sheets not in the frame: {foreign_sheets or 'none'}")
        entry: dict[str, Any] = {"n_points": len(points), "n_sheets": len(sheets),
                                 "sheets_not_in_frame": foreign_sheets}

        pairs = cross_sheet_pairs(points)
        counts = {limit: sum(1 for p in pairs if p[0] <= limit)
                  for limit in PAIR_COUNT_LIMITS}
        print("check 1: cross-sheet reference pairs within")
        for limit, n in counts.items():
            print(f"  {limit:>5} m: {n}")
        best = nearest_cross_sheet(points)
        if best:
            print(f"  closest cross-sheet pair: {best[0]:.1f} m "
                  f"({best[1]} {best[2]} / {best[3]} {best[4]})")
        within = [p for p in pairs if p[0] <= PAIR_LIMIT_M]
        for d, s1, f1, s2, f2 in within:
            print(f"    {d:7.1f} m  {s1} {f1}  /  {s2} {f2}")
        entry["pair_counts"] = counts
        entry["closest_pair"] = best
        entry["pairs_within_500m"] = within

        contacts = []
        for sheet, ident, x, y in points:
            for tile in tiles:
                x0, y0, x1, y1 = tile["bbox"]
                if not (x0 <= x <= x1 and y0 <= y <= y1):
                    continue
                if tile["sheet"] == sheet or not inside(x, y, tile["ring"]):
                    continue
                pos = pixel_position(args.tile_dir, tile, x, y)
                record: dict[str, Any] = {
                    "ref_sheet": sheet, "ref_id": ident, "x": x, "y": y,
                    "tile": tile["name"], "tile_sheet": tile["sheet"],
                    "col": None if pos is None else round(pos[0], 1),
                    "row": None if pos is None else round(pos[1], 1),
                }
                if args.pixels and pos is not None:
                    stem = tile["name"].removesuffix(".png")
                    crop = None
                    if args.crop_dir is not None:
                        safe_ref = Path(ref_name).stem
                        crop = (args.crop_dir / safe_ref
                                / f"{ident}__{stem}.png")
                    measure = measure_pixels(
                        args.tile_dir / tile["sheet"] / f"{stem}.png",
                        pos[0], pos[1], crop)
                    record["pixels"] = measure
                    record["verdict"] = classify(measure)
                contacts.append(record)
        refs_in_contact = {(c["ref_sheet"], c["ref_id"], c["x"], c["y"]) for c in contacts}
        print(f"check 2: point-tile contacts with another sheet's tile: "
              f"{len(contacts)} (references involved: {len(refs_in_contact)})")
        verdicts: dict[str, int] = {}
        for c in contacts:
            line = (f"  {c['ref_sheet']} {c['ref_id']} in {c['tile']}: "
                    f"col {c['col']}, row {c['row']}")
            if "pixels" in c:
                m = c["pixels"]
                verdicts[c["verdict"]] = verdicts.get(c["verdict"], 0) + 1
                line += (f"; window black {m['window_near_black_fraction']:.3f}; "
                         f"rgb {m['rgb_at_point']}; row content {m['row_content_span']}; "
                         f"col content {m['col_content_span']}; -> {c['verdict']}")
            print(line)
        if verdicts:
            print(f"  verdicts: {verdicts}")
        entry["contacts"] = contacts
        entry["n_contacts"] = len(contacts)
        entry["n_refs_in_contact"] = len(refs_in_contact)
        entry["verdicts"] = verdicts
        report["references"][ref_name] = entry

    if args.json_out is not None:
        args.json_out.write_text(json.dumps(report, indent=1, default=list) + "\n")


if __name__ == "__main__":
    main()
