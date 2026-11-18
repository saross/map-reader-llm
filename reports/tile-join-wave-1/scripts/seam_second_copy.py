#!/usr/bin/env python3
"""
Seam second-copy measurement for the 55-map stop (tile-join Wave 1, W1.0).

The W1.0 sheet check (``sheet_check_55map.py``) found references on one
sheet lying on the map content of a neighbouring sheet's tile, where the
neighbouring sheet prints the same mound
(``reports/tile-join-wave-1/stop-2026-11-18-55map-seams.md``). The PI is
asked how sheet-specific scoring should treat such mounds (stop record
§ 4, options (a)–(d)). This script measures, read-only and without any
model output, what the ruling needs:

1. For every **map-content** and **ambiguous** contact (a reference on
   sheet A inside a tile of sheet B): is a reference recorded on sheet B
   within 20 m and within 50 m of the point, i.e. is the second printed
   copy already digitised? Its id, layer, provenance, and whether it is a
   ``phantom:*`` reference are reported.
2. The number of distinct contacted tiles.
3. For each option, how many 55-map frame tiles would change
   reference-positive status relative to plain sheet-specific containment
   (a tile is positive iff a reference recorded on the tile's own sheet
   lies inside it):

   - (a) add the second copy as a reference on sheet B, at the contact
     point, for every contact with no sheet-B reference within 50 m;
   - (b) seam exception: a sheet-B tile is also positive if a sheet-A
     reference lies on its map content (each contact in scope);
   - (c) frame-wide containment for the 55-map corpus (a tile is positive
     if any reference of any sheet lies inside it; all contacts, padding
     included, can move tiles);
   - (d) exclude the contacted tiles on both sheets: the contacted sheet-B
     tile and every sheet-A tile containing the reference; reported as
     tiles removed, and of those, how many were positive.

   Each count is given twice: contacts measured as map content only, and
   map content plus ambiguous.
4. The canonical r50 lead: are its student–phantom cross-sheet pairs
   within 50 m the same mounds as its map-content contacts?

Geometry is standard library only, and nothing is imported from the scorer.
Contacts and their pixel verdicts are read from the committed output of the
sheet check, so the pixel measurement is not repeated.

Usage (zbook, from a checkout of the branch)::

    ~/Code/map-reader-llm/.venv/bin/python \\
        reports/tile-join-wave-1/scripts/seam_second_copy.py \\
        --json-out reports/tile-join-wave-1/scripts/out/seam_second_copy.json \\
        > reports/tile-join-wave-1/scripts/out/seam_second_copy.txt

Created: 2026-11-18 (tile-join Wave 1, W1.0, resumed after the seam stop)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sheet_check_55map import (  # noqa: E402
    BOUNDS,
    PROJECT_ROOT,
    REFERENCE_FILES,
    inside,
    load_tiles,
)

SUMMARY = HERE / "out" / "sheet_check_55map_summary.json"
RADII_M = (20.0, 50.0)
GRID_M = 2000.0
IN_SCOPE = {"map-content": ("map-content",),
            "map-content+ambiguous": ("map-content", "ambiguous")}


class TileIndex:
    """A coarse grid index over tile bounding boxes, for fast containment."""

    def __init__(self, tiles: list[dict[str, Any]]) -> None:
        """Bucket every tile into each grid cell its bounding box touches.

        Args:
            tiles: Tile records from ``sheet_check_55map.load_tiles``.
        """
        self.tiles = tiles
        self.cells: dict[tuple[int, int], list[int]] = defaultdict(list)
        for i, tile in enumerate(tiles):
            x0, y0, x1, y1 = tile["bbox"]
            for gx in range(int(x0 // GRID_M), int(x1 // GRID_M) + 1):
                for gy in range(int(y0 // GRID_M), int(y1 // GRID_M) + 1):
                    self.cells[(gx, gy)].append(i)

    def containing(self, x: float, y: float) -> list[int]:
        """Indices of the tiles whose polygon contains the point.

        Args:
            x: Easting.
            y: Northing.

        Returns:
            Tile indices.
        """
        out = []
        for i in self.cells.get((int(x // GRID_M), int(y // GRID_M)), []):
            x0, y0, x1, y1 = self.tiles[i]["bbox"]
            if x0 <= x <= x1 and y0 <= y <= y1 and inside(x, y, self.tiles[i]["ring"]):
                out.append(i)
        return out


def load_refs_full(path: Path) -> list[dict[str, Any]]:
    """Read references with their sheet, id, layer, provenance, and position.

    Args:
        path: A 55-map reference GeoJSON (projected, Point geometries).

    Returns:
        One record per point.
    """
    data = json.loads(path.read_text())
    refs = []
    for index, feature in enumerate(data["features"]):
        props = feature["properties"]
        geometry = feature["geometry"]
        points = ([geometry["coordinates"]] if geometry["type"] == "Point"
                  else geometry["coordinates"])
        ident = str(props.get("gt_id") or props.get("uuid") or index)
        for point in points:
            refs.append({
                "sheet": props["source_map"], "id": ident,
                "layer": props.get("layer"), "provenance": props.get("provenance"),
                "x": float(point[0]), "y": float(point[1]),
            })
    return refs


def nearest_on_sheet(refs_by_sheet: dict[str, list[dict]], sheet: str, x: float,
                     y: float) -> tuple[float, dict] | None:
    """The nearest reference recorded on ``sheet`` to a point.

    Args:
        refs_by_sheet: References grouped by sheet.
        sheet: The sheet to search.
        x: Easting.
        y: Northing.

    Returns:
        (distance, reference) or None if the sheet has no references.
    """
    best = None
    for ref in refs_by_sheet.get(sheet, []):
        d = math.hypot(ref["x"] - x, ref["y"] - y)
        if best is None or d < best[0]:
            best = (d, ref)
    return best


def positives(index: TileIndex, refs: list[dict], same_sheet: bool) -> set[int]:
    """Reference-positive tiles under sheet-specific or frame-wide containment.

    Args:
        index: Tile index of the frame.
        refs: References.
        same_sheet: True for sheet-specific containment (the reference's
            sheet must equal the tile's), False for frame-wide.

    Returns:
        Indices of positive tiles.
    """
    pos: set[int] = set()
    for ref in refs:
        for i in index.containing(ref["x"], ref["y"]):
            if not same_sheet or index.tiles[i]["sheet"] == ref["sheet"]:
                pos.add(i)
    return pos


def main() -> None:
    """Measure every reference file and print the tables."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    tiles = load_tiles(BOUNDS)
    index = TileIndex(tiles)
    by_name = {t["name"]: i for i, t in enumerate(tiles)}
    summary = json.loads(SUMMARY.read_text())
    report: dict[str, Any] = {"frame": str(BOUNDS.relative_to(PROJECT_ROOT)),
                              "references": {}}

    for ref_name in REFERENCE_FILES:
        refs = load_refs_full(PROJECT_ROOT / ref_name)
        refs_by_sheet: dict[str, list[dict]] = defaultdict(list)
        for ref in refs:
            refs_by_sheet[ref["sheet"]].append(ref)
        base = positives(index, refs, same_sheet=True)
        frame_wide = positives(index, refs, same_sheet=False)
        contacts = summary["references"][ref_name]["non_padding_contacts"]
        entry: dict[str, Any] = {"n_points": len(refs),
                                 "n_baseline_positive_tiles": len(base)}
        print(f"\n=== {ref_name}: {len(refs)} points; sheet-specific positive "
              f"tiles {len(base)} of {len(tiles)}")

        # (i) second copy already digitised?
        rows = []
        for c in contacts:
            near = nearest_on_sheet(refs_by_sheet, c["tile_sheet"], c["x"], c["y"])
            d, other = near if near else (None, None)
            rows.append({
                "verdict": c["verdict"], "ref_sheet": c["ref_sheet"],
                "ref_id": c["ref_id"], "tile": c["tile"],
                "tile_sheet": c["tile_sheet"],
                "nearest_other_sheet_ref_m": None if d is None else round(d, 1),
                "nearest_id": other["id"] if other else None,
                "nearest_layer": other["layer"] if other else None,
                "nearest_provenance": other["provenance"] if other else None,
                "nearest_is_phantom": bool(other and other["id"].startswith("phantom")),
                "within_20m": d is not None and d <= RADII_M[0],
                "within_50m": d is not None and d <= RADII_M[1],
            })
        entry["contacts"] = rows
        print("  (i) contacts by verdict: second copy on the contacted sheet "
              "within 20 m / 50 m (of which phantom)")
        for verdict in ("map-content", "ambiguous"):
            sel = [r for r in rows if r["verdict"] == verdict]
            w20 = [r for r in sel if r["within_20m"]]
            w50 = [r for r in sel if r["within_50m"]]
            print(f"    {verdict}: {len(sel)} contacts; within 20 m {len(w20)} "
                  f"(phantom {sum(r['nearest_is_phantom'] for r in w20)}); "
                  f"within 50 m {len(w50)} "
                  f"(phantom {sum(r['nearest_is_phantom'] for r in w50)})")
        for r in rows:
            print(f"      [{r['verdict']}] {r['ref_sheet']} {r['ref_id']} in "
                  f"{r['tile']}: nearest {r['tile_sheet']} ref "
                  f"{r['nearest_id']} at {r['nearest_other_sheet_ref_m']} m "
                  f"(layer {r['nearest_layer']}, provenance {r['nearest_provenance']})")

        # (ii) and (iii) per scope.
        entry["options"] = {}
        for scope, verdicts in IN_SCOPE.items():
            sel = [c for c in contacts if c["verdict"] in verdicts]
            sel_rows = [r for r in rows if r["verdict"] in verdicts]
            contacted = {by_name[c["tile"]] for c in sel}
            # (a) a second copy at the contact point on sheet B, where none
            # lies within 50 m: every sheet-B tile containing the point.
            added: set[int] = set()
            for c, r in zip(sel, sel_rows):
                if r["within_50m"]:
                    continue
                for i in index.containing(c["x"], c["y"]):
                    if tiles[i]["sheet"] == c["tile_sheet"]:
                        added.add(i)
            a_changed = added - base
            # (b) the contacted tile itself becomes positive.
            b_changed = contacted - base
            # (d) contacted tiles on both sheets removed.
            removed = set(contacted)
            for c in sel:
                for i in index.containing(c["x"], c["y"]):
                    if tiles[i]["sheet"] == c["ref_sheet"]:
                        removed.add(i)
            result = {
                "n_contacts": len(sel),
                "n_distinct_contacted_tiles": len(contacted),
                "a_tiles_turning_positive": len(a_changed),
                "a_references_added": sum(1 for r in sel_rows if not r["within_50m"]),
                "b_tiles_turning_positive": len(b_changed),
                "d_tiles_removed": len(removed),
                "d_removed_baseline_positive": len(removed & base),
                "d_removed_baseline_negative": len(removed - base),
            }
            entry["options"][scope] = result
            print(f"  scope {scope}: {result}")
        c_changed = frame_wide - base
        entry["c_tiles_turning_positive_frame_wide"] = len(c_changed)
        entry["c_tiles_turning_positive_on_map_content_contacts"] = len(
            c_changed & {by_name[c["tile"]] for c in contacts
                         if c["verdict"] == "map-content"})
        print(f"  (c) frame-wide: {len(c_changed)} tiles turn positive "
              f"(frame-wide positives {len(frame_wide)}); of these, map-content "
              f"contacted tiles {entry['c_tiles_turning_positive_on_map_content_contacts']}")

        # The phantom lead (canonical r50 carries phantoms).
        phantoms = [r for r in refs if r["id"].startswith("phantom")]
        if phantoms:
            mc = {(c["ref_sheet"], c["ref_id"], c["tile_sheet"]) for c in contacts
                  if c["verdict"] == "map-content"}
            amb = {(c["ref_sheet"], c["ref_id"], c["tile_sheet"]) for c in contacts
                   if c["verdict"] == "ambiguous"}
            pairs = []
            for p in phantoms:
                for s in refs:
                    if s["id"].startswith("phantom") or s["sheet"] == p["sheet"]:
                        continue
                    d = math.hypot(s["x"] - p["x"], s["y"] - p["y"])
                    if d <= RADII_M[1]:
                        key = (s["sheet"], s["id"], p["sheet"])
                        pairs.append({
                            "student_sheet": s["sheet"], "student_id": s["id"],
                            "phantom_sheet": p["sheet"], "phantom_id": p["id"],
                            "distance_m": round(d, 1),
                            "student_contact": ("map-content" if key in mc else
                                                "ambiguous" if key in amb else
                                                "padding-or-no-contact"),
                        })
            pairs.sort(key=lambda q: q["distance_m"])
            entry["phantom_pairs_within_50m"] = pairs
            tally: dict[str, int] = defaultdict(int)
            for q in pairs:
                tally[q["student_contact"]] += 1
            print(f"  phantom lead: {len(pairs)} student-phantom cross-sheet "
                  f"pairs within 50 m; student reference's contact with the "
                  f"phantom's sheet: {dict(tally)}")
            for q in pairs:
                print(f"    {q['distance_m']:6.1f} m  {q['student_sheet']} "
                      f"{q['student_id']} / {q['phantom_sheet']} {q['phantom_id']}"
                      f"  -> {q['student_contact']}")
        report["references"][ref_name] = entry

    if args.json_out is not None:
        args.json_out.write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
