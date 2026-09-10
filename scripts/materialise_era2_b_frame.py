#!/usr/bin/env python3
"""Materialise the Era-2 ∩ B-union evaluation frame for the GS Era-2 verified board.

Card: ``planning/gs-era2-verified-board-2026-09-08.md`` § 2, PI ruling
2026-09-09 (frame option (a)). A board's frame is the intersection of its
members' dispatched coverage. The Gemini 3 incumbents were dispatched on the
Era-2 frame (``inputs/vectors/bounds/384/full_evaluation_bounds.geojson``, 487
whole 384 px tiles); every 3.7, 3.8, image-B, and grid / stride B-geometry cell
was dispatched on the B tiling (``outputs/grid-2026-08-18/scoring/bounds/grid_g384_ov192_bounds.geojson``,
1,398 tiles at 384 px / 50 % overlap), whose union covers the Era-2 frame
except a 13.4 km² edge strip. This script clips the 487 Era-2 carrier tiles to
the B union, exactly as the grid campaign clipped them to its four-way
intersection to make ``grid_common_bounds.geojson``, and writes the result with
a provenance sidecar (inputs, areas, reference-mound counts, git commit).

Outputs
-------
``inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson``
    487 polygons (``tile_name``, ``map_name`` carried over; a tile is kept
    whole where the B union covers it and clipped otherwise; none is dropped
    unless the clip is empty, which the sidecar would record).
``inputs/vectors/bounds/384/era2_b_intersection_bounds.provenance.json``
    The construction record; ``test_set_id`` ``era2-b-487`` is the frame id
    the register's ``scope_override`` and the uplift supplement's strata use.

Zero API. Pure local geometry (a few seconds).

Usage
-----
    python scripts/materialise_era2_b_frame.py            # write both files
    python scripts/materialise_era2_b_frame.py --check    # rebuild in memory, compare
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd

REPO_ROOT = Path(__file__).resolve().parent.parent
ERA2_BOUNDS = REPO_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
B_BOUNDS = REPO_ROOT / "outputs/grid-2026-08-18/scoring/bounds/grid_g384_ov192_bounds.geojson"
REFERENCE = REPO_ROOT / "inputs/vectors/references/mounds-reference.geojson"
OUT_BOUNDS = REPO_ROOT / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
OUT_PROV = REPO_ROOT / "inputs/vectors/bounds/384/era2_b_intersection_bounds.provenance.json"
TEST_SET_ID = "era2-b-487"
TARGET_CRS = "EPSG:32635"


def build_frame(era2: gpd.GeoDataFrame, b_tiles: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    """Clip the Era-2 carrier tiles to the B tiling's union.

    Args:
        era2: The 487 Era-2 tiles (``tile_name``, ``map_name``, polygons).
        b_tiles: The B-geometry tiles whose union is the clipping mask.

    Returns:
        ``(frame, stats)`` — the clipped tiles in ``TARGET_CRS`` and a summary
        (tile counts, areas in km², how many tiles were clipped or dropped).
    """
    era2 = era2.to_crs(TARGET_CRS)
    mask = b_tiles.to_crs(TARGET_CRS).geometry.union_all()
    clipped = era2.copy()
    clipped["geometry"] = era2.geometry.intersection(mask)
    kept = clipped[~clipped.geometry.is_empty].copy()
    n_clipped = int((kept.geometry.area < era2.loc[kept.index].geometry.area - 1.0).sum())
    stats = {
        "n_era2_tiles": int(len(era2)),
        "n_frame_tiles": int(len(kept)),
        "n_dropped_empty": int(len(era2) - len(kept)),
        "n_clipped": n_clipped,
        "n_identical": int(len(kept) - n_clipped),
        "area_km2_era2_union": round(era2.geometry.union_all().area / 1e6, 2),
        "area_km2_frame_union": round(kept.geometry.union_all().area / 1e6, 2),
        "area_km2_era2_outside_b": round(era2.geometry.union_all().difference(mask).area / 1e6, 2),
    }
    return kept[["tile_name", "map_name", "geometry"]], stats


def reference_counts(frame: gpd.GeoDataFrame, era2: gpd.GeoDataFrame, reference: gpd.GeoDataFrame) -> dict:
    """Reference mounds inside the Era-2 union and inside the frame union."""
    ref = reference.to_crs(TARGET_CRS)
    return {
        "reference_total": int(len(ref)),
        "reference_in_era2_frame": int(ref.within(era2.to_crs(TARGET_CRS).geometry.union_all()).sum()),
        "reference_in_frame": int(ref.within(frame.geometry.union_all()).sum()),
    }


def _git_commit() -> str:
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="Rebuild in memory and compare with the committed frame; write nothing.")
    args = parser.parse_args(argv)

    era2 = gpd.read_file(ERA2_BOUNDS)
    b_tiles = gpd.read_file(B_BOUNDS)
    frame, stats = build_frame(era2, b_tiles)
    stats.update(reference_counts(frame, era2, gpd.read_file(REFERENCE)))
    if stats["n_dropped_empty"]:
        print(f"REFUSED: {stats['n_dropped_empty']} Era-2 tile(s) fall entirely outside the "
              "B union; the frame would not be the 487 carrier tiles", file=sys.stderr)
        return 2

    if args.check:
        committed = gpd.read_file(OUT_BOUNDS).to_crs(TARGET_CRS)
        same = len(committed) == len(frame) and all(
            a.equals_exact(b, 0.01) for a, b in zip(committed.geometry, frame.geometry))
        print(json.dumps(stats, indent=1))
        print("committed frame matches rebuild" if same else "MISMATCH: committed frame differs")
        return 0 if same else 1

    OUT_BOUNDS.parent.mkdir(parents=True, exist_ok=True)
    frame.to_file(OUT_BOUNDS, driver="GeoJSON")
    provenance = {
        "test_set_id": TEST_SET_ID,
        "bounds_path": str(OUT_BOUNDS.relative_to(REPO_ROOT)),
        "construction": "Era-2 carrier tiles clipped to the union of the B tiling "
                        "(384 px / 50 % overlap), tile by tile; the same operation "
                        "the grid campaign used for grid_common_bounds.geojson",
        "inputs": {
            "era2_bounds": str(ERA2_BOUNDS.relative_to(REPO_ROOT)),
            "b_bounds": str(B_BOUNDS.relative_to(REPO_ROOT)),
            "reference": str(REFERENCE.relative_to(REPO_ROOT)),
        },
        "crs": TARGET_CRS,
        "card": "planning/gs-era2-verified-board-2026-09-08.md",
        "ruling": "PI, 2026-09-09: frame option (a)",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git_commit(),
        **stats,
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=1))
    print(f"wrote {OUT_BOUNDS.relative_to(REPO_ROOT)} and its provenance sidecar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
