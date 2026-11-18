#!/usr/bin/env python3
"""
Sheet-boundary check of every gold-standard (GS) frame (tile-join Wave 1).

The Wave 2 specification draft (precondition P4) notes that the sheet
check has been run only on the Era-2 frame (parent record § 2.6) and the
55-map frame (``sheet_check_55map.py``). This script runs the same check
on every distinct GS frame that a tile-bearing evaluation in the W1.0
census uses (``reports/tile-join-wave-1/worklist.json``), with the GS
references (``inputs/vectors/references/mounds-reference.geojson``, sheet
in ``Map``):

1. cross-sheet reference pairs within 500 m (counts at 50–1,000 m), among
   the references inside the frame's union;
2. every cross-sheet point–tile contact, with its pixel position and the
   pixel verdict (padding / ambiguous / map content) of
   ``sheet_check_55map.measure_pixels`` and ``classify``, unchanged
   thresholds.

**Which image is the tile's.** Tile names repeat across tilings (``…_x0_y0``
exists at 256, 384, and 512 px), so the image is found by footprint: among
the candidate tile directories, the PNG whose world file and pixel size
reproduce the frame polygon's bounds within 1 m. If none does, the frame's
own tile is **unavailable** and the contact is reported so. A substitute
verdict is then measured on any available image of the same sheet whose
footprint contains the point, and labelled as a substitute: content versus
padding at a point is a property of the sheet's scan, but it is not the
frame's own tile.

Geometry is standard library (imports from ``sheet_check_55map``); pixels
use Pillow and NumPy from the reference environment.

Usage (zbook; ``--list-needed`` prints the contacted tiles with no image,
for copying from another machine into ``--extra-tile-dir``)::

    ~/Code/map-reader-llm/.venv/bin/python \\
        reports/tile-join-wave-1/scripts/sheet_check_gs_frames.py \\
        --data-root ~/Code/map-reader-llm \\
        --extra-tile-dir ~/scratch/wave1/w10/gs-frames/tiles_256 \\
        --crop-dir ~/scratch/wave1/w10/gs-frames/crops \\
        --json-out reports/tile-join-wave-1/scripts/out/sheet_check_gs_frames.json \\
        > reports/tile-join-wave-1/scripts/out/sheet_check_gs_frames.txt

Created: 2026-11-19 (tile-join Wave 1, W1.0 follow-up)
Modified: 2026-11-19 (pixel positions through the shared, corrected helper)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sheet_check_55map import (  # noqa: E402
    PAIR_COUNT_LIMITS,
    PAIR_LIMIT_M,
    classify,
    cross_sheet_pairs,
    inside,
    load_tiles,
    measure_pixels,
    read_world_file,
    world_to_pixel,
)

PROJECT_ROOT = HERE.parents[2]
GS_REFERENCES = "inputs/vectors/references/mounds-reference.geojson"
#: The GS frames tile-bearing evaluations use (worklist.json, 2026-11-18).
GS_FRAMES = (
    "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
    "inputs/vectors/bounds/full_evaluation_bounds.geojson",
    "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson",
    "results/null-exemplar-sensitivity-2026-09-13/bounds/era2-b-487_minus_null_overlap.geojson",
    "results/null-exemplar-sensitivity-2026-09-13/bounds/era1-full-340_minus_null_overlap.geojson",
    "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson",
    "inputs/vectors/bounds/384/h10_test_bounds.geojson",
    "inputs/vectors/bounds/256/full_evaluation_bounds.geojson",
    "outputs/h13/scoring/bounds/h13_common_bounds.geojson",
    "outputs/h13/scoring/bounds/h13_armA_bounds.geojson",
    "outputs/h13/scoring/bounds/h13_armB_bounds.geojson",
    "outputs/h13/scoring/bounds/h13_armC_bounds.geojson",
)
TILE_DIRS = ("inputs/tiles", "inputs/tiles_384", "inputs/tiles_256",
             "inputs/tiles_512_ov128", "inputs/tiles_512_ov256")
MATCH_TOL_M = 1.0


def png_size(path: Path) -> tuple[int, int]:
    """Width and height from a PNG's IHDR chunk (standard library)."""
    with path.open("rb") as fh:
        head = fh.read(24)
    return struct.unpack(">II", head[16:24])


def index_images(dirs: list[Path]) -> dict[str, list[dict[str, Any]]]:
    """Every tile image with a world file, by file name.

    Args:
        dirs: Candidate tile directories (``<dir>/<sheet>/<name>.png``).

    Returns:
        ``{name: [{png, a, e, c, f, w, h, bbox}, ...]}``.
    """
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for d in dirs:
        if not d.is_dir():
            continue
        for pgw in d.glob("*/*.pgw"):
            png = pgw.with_suffix(".png")
            if not png.exists():
                continue
            a, e, c, f = read_world_file(pgw)
            w, h = png_size(png)
            # Footprints under both readings of the world file's origin (the
            # first pixel's centre, as the ESRI definition and the project's
            # tiler have it, or its corner); a frame polygon built either way
            # is matched. Pixel positions use the centre reading only
            # (``world_to_pixel``; before 2026-11-19 they mixed the two).
            boxes = []
            for x0, y1 in ((c - a / 2, f - e / 2), (c, f)):
                boxes.append((x0, y1 + e * h, x0 + a * w, y1))
            out[png.name].append({"png": png, "a": a, "e": e, "c": c, "f": f,
                                  "w": w, "h": h, "bboxes": boxes,
                                  "bbox": boxes[0]})
    return out


def own_image(images: dict, tile: dict[str, Any]) -> dict[str, Any] | None:
    """The image whose footprint reproduces the frame tile's bounds."""
    tb = tile["bbox"]
    for img in images.get(tile["name"], []):
        for box in img["bboxes"]:
            if all(abs(p - q) <= MATCH_TOL_M for p, q in zip(box, tb)):
                return img
    return None


def substitute_image(images: dict, sheet: str, x: float, y: float) -> dict | None:
    """Any available image of ``sheet`` whose footprint contains the point."""
    for name, imgs in images.items():
        if not name.startswith(sheet + "_x"):
            continue
        for img in imgs:
            x0, y0, x1, y1 = img["bbox"]
            if x0 <= x <= x1 and y0 <= y <= y1:
                return img
    return None


def pixel(img: dict[str, Any], x: float, y: float) -> tuple[float, float]:
    """Point to edge-indexed (column, row), by ``sheet_check_55map.world_to_pixel``.

    The containing pixel is the floor of each coordinate (convention fixed
    2026-11-19; the helper's docstring gives the derivation).
    """
    return world_to_pixel((img["a"], img["e"], img["c"], img["f"]), x, y)


def load_gs(path: Path) -> list[tuple[str, str, float, float]]:
    """GS references as (sheet, fid, x, y), sheet from ``Map``."""
    data = json.loads(path.read_text())
    out = []
    for feat in data["features"]:
        geom = feat["geometry"]
        pts = [geom["coordinates"]] if geom["type"] == "Point" else geom["coordinates"]
        for p in pts:
            out.append((feat["properties"]["Map"], str(feat["properties"].get("fid")),
                        float(p[0]), float(p[1])))
    return out


def main() -> None:
    """Run the check on every GS frame."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--extra-tile-dir", type=Path, action="append", default=[])
    parser.add_argument("--crop-dir", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--list-needed", action="store_true")
    args = parser.parse_args()

    images = index_images([args.data_root / d for d in TILE_DIRS] + args.extra_tile_dir)
    refs = load_gs(PROJECT_ROOT / GS_REFERENCES)
    report: dict[str, Any] = {"references": GS_REFERENCES, "n_points": len(refs),
                              "frames": {}}
    needed: set[str] = set()
    print(f"GS references: {len(refs)} points; image index: "
          f"{sum(len(v) for v in images.values())} images")
    all_pairs = cross_sheet_pairs(refs)
    print("whole GS, cross-sheet pairs within "
          + ", ".join(f"{lim} m: {sum(1 for p in all_pairs if p[0] <= lim)}"
                      for lim in PAIR_COUNT_LIMITS))

    for frame in GS_FRAMES:
        path = args.data_root / frame
        if not path.exists():
            print(f"\n=== {frame}: FRAME FILE ABSENT")
            report["frames"][frame] = {"error": "frame file absent"}
            continue
        tiles = load_tiles(path)
        in_frame = [r for r in refs
                    if any(t["bbox"][0] <= r[2] <= t["bbox"][2]
                           and t["bbox"][1] <= r[3] <= t["bbox"][3]
                           and inside(r[2], r[3], t["ring"]) for t in tiles)]
        pairs = cross_sheet_pairs(in_frame)
        counts = {lim: sum(1 for p in pairs if p[0] <= lim) for lim in PAIR_COUNT_LIMITS}
        n_own = sum(1 for t in tiles if own_image(images, t))
        print(f"\n=== {frame}: {len(tiles)} tiles ({n_own} with their own image); "
              f"{len(in_frame)} references inside; pairs {counts}")
        contacts = []
        for sheet, fid, x, y in refs:
            for t in tiles:
                x0, y0, x1, y1 = t["bbox"]
                if not (x0 <= x <= x1 and y0 <= y <= y1):
                    continue
                if t["sheet"] == sheet or not inside(x, y, t["ring"]):
                    continue
                rec: dict[str, Any] = {"ref_sheet": sheet, "fid": fid, "x": x, "y": y,
                                       "tile": t["name"], "tile_sheet": t["sheet"]}
                img = own_image(images, t)
                basis = "own tile"
                if img is None:
                    needed.add(t["name"])
                    img = substitute_image(images, t["sheet"], x, y)
                    basis = "SUBSTITUTE (own tile unavailable)" if img else None
                rec["image_basis"] = basis or "tiles unavailable"
                if img is not None:
                    col, row = pixel(img, x, y)
                    crop = None
                    if args.crop_dir is not None:
                        crop = (args.crop_dir / Path(frame).stem
                                / f"fid{fid}__{img['png'].stem}.png")
                    m = measure_pixels(img["png"], col, row, crop)
                    rec.update({"image": str(img["png"]), "col": round(col, 1),
                                "row": round(row, 1), "pixels": m, "verdict": classify(m)})
                else:
                    rec["verdict"] = "tiles unavailable"
                contacts.append(rec)
        tally: dict[str, int] = defaultdict(int)
        for c in contacts:
            key = c["verdict"] if c["image_basis"] == "own tile" else (
                f"{c['verdict']} [{c['image_basis']}]")
            tally[key] += 1
            m = c.get("pixels") or {}
            print(f"  {c['ref_sheet']} fid {c['fid']} in {c['tile']}: "
                  f"col {c.get('col')}, row {c.get('row')}; "
                  f"window black {m.get('window_near_black_fraction')}; "
                  f"-> {c['verdict']} ({c['image_basis']})")
        print(f"  contacts {len(contacts)} "
              f"(references {len({(c['ref_sheet'], c['fid']) for c in contacts})}); "
              f"verdicts {dict(tally)}")
        report["frames"][frame] = {
            "n_tiles": len(tiles), "n_tiles_with_own_image": n_own,
            "n_refs_inside": len(in_frame), "pair_counts": counts,
            "pairs_within_500m": [p for p in pairs if p[0] <= PAIR_LIMIT_M],
            "n_contacts": len(contacts),
            "n_refs_in_contact": len({(c["ref_sheet"], c["fid"]) for c in contacts}),
            "verdicts": dict(tally), "contacts": contacts,
        }
    if args.list_needed:
        print("\nNEEDED " + " ".join(sorted(needed)))
    if args.json_out is not None:
        args.json_out.write_text(json.dumps(report, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
