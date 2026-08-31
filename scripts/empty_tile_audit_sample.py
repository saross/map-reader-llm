#!/usr/bin/env python3
"""
Empty-tile audit: build the nested stratified sample manifest.

Card § 5 of `planning/student-baseline-2026-08-31.md` (PI-approved
2026-08-31): estimate the double-miss floor — mounds missed by BOTH
the student digitisers and the model — by human review of a sample of
"empty" evaluation tiles.

**Empty** means: no canonical-GT point, no reviewed-student point, no
detection from either the arm-2 carried set (all-3.7 stack) or the
B-N5 carried incumbent. Computed over the 8,541-tile evaluation grid;
expected count 4,676 (Session 145 derivation — the script warns if
the recomputation drifts).

**Nested design**: a 20 % per-sheet proportional draw (seeded), whose
per-sheet first half is the 10 % subsample. The manifest is ordered
so ALL 10 %-tier tiles come first (shuffled across sheets), then the
20 %-tier remainder — the reviewer stops at the tier boundary for the
default audit, or keeps going for the pre-agreed escalation.

Each manifest row carries the tile's world bounds (EPSG:32635, from
the evaluation-bounds polygons) so the review app can convert clicks
to world coordinates without needing the rasters.

Outputs (``--out-dir``, default ``results/empty-tile-audit``):

- ``audit_manifest.csv`` — order_index, tile_name, map_name, tier,
  minx, miny, maxx, maxy, px_m.
- ``tile_filelist.txt`` — ``<map>/<tile>`` paths relative to the tile
  root (``inputs/tiles_384_55maps``), for rsync to the review machine.
- ``sample_summary.json`` — per-sheet counts and the gate record.

Usage::

    python scripts/empty_tile_audit_sample.py

Zero API. Run on sapphire (the tile tree lives there; the sjoin is
light). Deterministic at ``--seed`` (default 42).

Created: 2026-08-31 (Session 145)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
CANONICAL_GT = PROJECT_ROOT / "inputs/vectors/references/canonical-gt-55maps-r50.geojson"
STUDENT_GT = PROJECT_ROOT / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
DETECTION_SETS = (
    PROJECT_ROOT / "results/gemini37-55map-2026-08-31/arm2"
    "/g384_ov192_55map_g37/primary/verified_detections.geojson",
    PROJECT_ROOT / "results/55map-final-board-2026-08-27"
    "/cells/B-N5-carried/detections.geojson",
)
TILE_PX = 384
EXPECTED_EMPTY = 4676


def map_of(tile_name: str) -> str:
    """Sheet name from a tile name (``K-35-042-3_x1536_y0.png``)."""
    return tile_name.rsplit("_x", 1)[0]


def compute_empty_tiles(bounds: gpd.GeoDataFrame,
                        point_layers: list[gpd.GeoDataFrame],
                        detection_tiles: set[str]) -> set[str]:
    """Tiles with no reference point and no detection.

    Args:
        bounds: Evaluation-grid tile polygons with a ``tile_name`` column.
        point_layers: Point GeoDataFrames whose presence occupies a tile.
        detection_tiles: ``source_tile`` names from detection sets.

    Returns:
        The set of empty tile names.
    """
    occupied = set(detection_tiles)
    frame = bounds[["tile_name", "geometry"]]
    for layer in point_layers:
        joined = gpd.sjoin(layer, frame, how="inner", predicate="within")
        occupied |= set(joined["tile_name"])
    return set(bounds["tile_name"]) - occupied


def nested_sample(empty: set[str], frac_outer: float, frac_inner: float,
                  seed: int) -> list[dict]:
    """Per-sheet proportional nested draw, ordered inner tier first.

    Args:
        empty: Empty tile names.
        frac_outer: Outer (escalation) sampling fraction, e.g. 0.20.
        frac_inner: Inner (default) fraction; inner draw ⊂ outer draw.
        seed: Random seed for the whole procedure.

    Returns:
        Manifest rows (dicts) with ``order_index`` assigned: all inner-
        tier tiles shuffled across sheets, then the outer-tier rest.
    """
    rng = np.random.default_rng(seed)
    by_sheet: dict[str, list[str]] = {}
    for name in sorted(empty):
        by_sheet.setdefault(map_of(name), []).append(name)

    inner_rows: list[dict] = []
    outer_rows: list[dict] = []
    for sheet in sorted(by_sheet):
        names = by_sheet[sheet]
        n_outer = round(frac_outer * len(names))
        n_inner = min(round(frac_inner * len(names)), n_outer)
        draw = list(rng.choice(names, size=n_outer, replace=False))
        for i, name in enumerate(draw):
            row = {"tile_name": name, "map_name": sheet,
                   "tier": "10pct" if i < n_inner else "20pct"}
            (inner_rows if i < n_inner else outer_rows).append(row)
    rng.shuffle(inner_rows)
    rng.shuffle(outer_rows)
    rows = inner_rows + outer_rows
    for i, row in enumerate(rows):
        row["order_index"] = i
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--out-dir", default="results/empty-tile-audit")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--frac-outer", type=float, default=0.20)
    ap.add_argument("--frac-inner", type=float, default=0.10)
    args = ap.parse_args()

    bounds = gpd.read_file(BOUNDS)
    layers = [gpd.read_file(p).to_crs(bounds.crs)
              for p in (CANONICAL_GT, STUDENT_GT)]
    det_tiles: set[str] = set()
    for path in DETECTION_SETS:
        det = json.loads(path.read_text())
        det_tiles |= {f["properties"]["source_tile"]
                      for f in det["features"]}

    empty = compute_empty_tiles(bounds, layers, det_tiles)
    logger.info("empty tiles: %d of %d", len(empty), len(bounds))
    if len(empty) != EXPECTED_EMPTY:
        logger.warning("empty-tile count %d != expected %d — inputs have "
                       "moved since the card was drafted; sample is still "
                       "valid but update the card", len(empty),
                       EXPECTED_EMPTY)

    rows = nested_sample(empty, args.frac_outer, args.frac_inner, args.seed)
    n_inner = sum(1 for r in rows if r["tier"] == "10pct")
    logger.info("sample: %d tiles (%d inner tier + %d escalation)",
                len(rows), n_inner, len(rows) - n_inner)

    # World bounds per tile, for click-to-coordinate conversion in the app.
    geom = {r.tile_name: r.geometry.bounds
            for r in bounds.itertuples() if r.tile_name in
            {row["tile_name"] for row in rows}}
    for row in rows:
        minx, miny, maxx, maxy = geom[row["tile_name"]]
        row.update({"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy,
                    "px_m": (maxx - minx) / TILE_PX})

    out_dir = PROJECT_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    fields = ["order_index", "tile_name", "map_name", "tier",
              "minx", "miny", "maxx", "maxy", "px_m"]
    with (out_dir / "audit_manifest.csv").open("w", newline="") as fh:
        w = csvmod.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows({k: r[k] for k in fields} for r in rows)
    (out_dir / "tile_filelist.txt").write_text("".join(
        f"{r['map_name']}/{r['tile_name']}\n" for r in rows))
    (out_dir / "sample_summary.json").write_text(json.dumps({
        "seed": args.seed, "frac_outer": args.frac_outer,
        "frac_inner": args.frac_inner, "n_empty": len(empty),
        "n_expected_empty": EXPECTED_EMPTY, "n_sampled": len(rows),
        "n_inner": n_inner,
        "per_sheet": {s: sum(1 for r in rows if r["map_name"] == s)
                      for s in sorted({r["map_name"] for r in rows})},
    }, indent=2) + "\n")
    logger.info("manifest -> %s", out_dir.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
