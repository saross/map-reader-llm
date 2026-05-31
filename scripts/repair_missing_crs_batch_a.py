#!/usr/bin/env python3
"""Repair detection GeoJSONs written in UTM Zone 35N metres with NO ``crs`` member.

Context
-------
Some detection GeoJSONs in the Batch A re-scoring worklist were written in
UTM Zone 35N metres (EPSG:32635) — coordinates like ``[416963.2, 4687963.6]`` —
but with **no** top-level ``crs`` member. GeoPandas/GDAL default a ``crs``-less
GeoJSON to EPSG:4326 (the GeoJSON spec default), so the scorer's ``load_geojson``
(``scripts/evaluate_detections.py``) treats these metre coordinates as WGS84
degrees and mis-reprojects them far off the tile grid. The detections then match
no ground-truth mound at any buffer → F1 = 0 at every buffer.

Working sibling runs store WGS84 **degrees** (e.g. ``[25.76, 42.44]``) with no
``crs`` member, which GeoPandas reads as EPSG:4326 and the scorer reprojects to
EPSG:32635 correctly.

The repair (replicates commit 6427e410)
---------------------------------------
For each defective file: reproject every coordinate from EPSG:32635 to EPSG:4326
(``pyproj.Transformer``, ``always_xy=True`` — verified bit-exact against the
6427e410 repair) and write the file back in WGS84 degrees, matching the working
sibling convention (degrees, no ``crs`` member needed).

The repair operates on the **parsed JSON dict**, mutating only coordinate
numbers, then re-serialising with ``json.dumps`` default separators (verified to
round-trip byte-exact for every target). This preserves ALL properties (incl.
``source_tiles``) byte-faithfully; only the coordinate numbers change.

Defect detection (per file, drives the repair — not a hard-coded list)
----------------------------------------------------------------------
A file is defective iff the magnitude of its first coordinate's X (longitude /
easting) is > 180 **and** the file has no top-level ``crs`` member. WGS84-degrees
files (|X| ≤ 180) and files with an explicit ``crs`` member are skipped. The check
is idempotent: a repaired (degrees) file will never re-match.

Originals are archived to ``archive/data-repairs/<run>-missing-crs/<sub-path>``
before being overwritten (project rule: archive, never delete).

Usage
-----
    # dry-run: classify every worklist file, change nothing
    python scripts/repair_missing_crs_batch_a.py --worklist <worklist.json>

    # execute the repair
    python scripts/repair_missing_crs_batch_a.py --worklist <worklist.json> --execute
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from pyproj import Transformer

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Source CRS of the defective coordinates (UTM Zone 35N, Bulgaria) and the target
#: WGS84 geographic CRS. ``always_xy=True`` forces (lon, lat) / (easting, northing)
#: axis order, matching the GeoJSON coordinate convention and commit 6427e410.
SOURCE_CRS = "EPSG:32635"
TARGET_CRS = "EPSG:4326"

#: A first-coordinate X magnitude above this (degrees) cannot be WGS84 longitude,
#: so it must be projected metres — the defect signature.
DEGREE_MAX = 180.0

_TRANSFORMER = Transformer.from_crs(SOURCE_CRS, TARGET_CRS, always_xy=True)


def _first_coord(geometry: dict[str, Any]) -> list[float]:
    """Return the first (x, y) coordinate pair of a geometry, any nesting depth."""
    coords = geometry["coordinates"]
    while isinstance(coords, list) and coords and isinstance(coords[0], list):
        coords = coords[0]
    return coords


def is_defective(geojson: dict[str, Any]) -> bool:
    """True iff the GeoJSON is UTM-metres-without-crs (the repair target signature).

    Args:
        geojson: Parsed GeoJSON FeatureCollection.

    Returns:
        True if the file has no top-level ``crs`` member AND its first coordinate's
        X magnitude exceeds 180 (so it is projected metres, not WGS84 degrees).
    """
    if "crs" in geojson:
        return False
    features = geojson.get("features", [])
    if not features:
        return False
    first_x = _first_coord(features[0]["geometry"])[0]
    return abs(first_x) > DEGREE_MAX


def _reproject_coords(node: Any) -> Any:
    """Recursively reproject every [x, y(, z...)] coordinate pair EPSG:32635→4326.

    A coordinate pair is a list whose first element is a number; any other list is
    a container of coordinates / rings and is recursed into. Non-list nodes are
    returned unchanged. Only the X and Y are transformed; any extra ordinates
    (rare) are preserved.

    Args:
        node: A coordinates value at any nesting depth (pair, ring, polygon, ...).

    Returns:
        The same structure with X/Y reprojected to WGS84 degrees.
    """
    if isinstance(node, list) and node and isinstance(node[0], (int, float)):
        lon, lat = _TRANSFORMER.transform(node[0], node[1])
        return [lon, lat, *node[2:]]
    if isinstance(node, list):
        return [_reproject_coords(child) for child in node]
    return node


def repair_geojson(geojson: dict[str, Any]) -> dict[str, Any]:
    """Reproject all feature geometries 32635→4326 in place; return the dict.

    Only ``feature['geometry']['coordinates']`` are touched; every property
    (incl. ``source_tiles``) and key order are left untouched.
    """
    for feature in geojson["features"]:
        geom = feature.get("geometry")
        if geom and "coordinates" in geom:
            geom["coordinates"] = _reproject_coords(geom["coordinates"])
    return geojson


def _archive_path(detections: Path) -> Path:
    """Compute the archive destination for an original, keyed by run name.

    ``outputs/h11/<run>/<sub-path>.geojson`` →
    ``archive/data-repairs/<run>-missing-crs/<sub-path>.geojson``. The run is the
    path component immediately under the top-level output bucket (``h11``,
    ``retest``, ...).
    """
    rel = detections.relative_to(REPO_ROOT)
    parts = rel.parts
    # parts[0]='outputs', parts[1]= bucket (h11/retest), parts[2]= run name.
    run = parts[2]
    sub = Path(*parts[3:])
    return REPO_ROOT / "archive" / "data-repairs" / f"{run}-missing-crs" / sub


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worklist", required=True, type=Path)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply the repair. Without this flag, only classify (dry-run).",
    )
    args = parser.parse_args()

    worklist = json.loads(args.worklist.read_text())
    entries = worklist["entries"]

    repaired: list[Path] = []
    skipped: list[Path] = []

    for entry in entries:
        det = (REPO_ROOT / entry["detections"]).resolve()
        if not det.exists():
            print(f"  MISSING  {entry['detections']}")
            continue

        raw = det.read_bytes()
        geojson = json.loads(raw)

        if not is_defective(geojson):
            skipped.append(det)
            continue

        repaired.append(det)
        if not args.execute:
            print(f"  WOULD REPAIR  {entry['detections']}")
            continue

        # Archive the original, byte-for-byte, before overwriting.
        archive_dest = _archive_path(det)
        archive_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(det, archive_dest)

        # Reproject and re-serialise with DEFAULT separators (verified byte-exact
        # round-trip for every Batch A target) so only coordinates change.
        repaired_geojson = repair_geojson(geojson)
        det.write_text(json.dumps(repaired_geojson))
        print(
            f"  REPAIRED  {entry['detections']}  "
            f"(archived → {archive_dest.relative_to(REPO_ROOT)})"
        )

    verb = "Repaired" if args.execute else "Would repair"
    print(
        f"\n{verb} {len(repaired)} defective file(s); "
        f"skipped {len(skipped)} OK file(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
