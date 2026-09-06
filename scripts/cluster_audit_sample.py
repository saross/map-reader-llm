#!/usr/bin/env python3
"""
Cluster audit: build the necropolis census manifest (Phase 2b).

Card § 5c of `planning/student-baseline-2026-08-31.md`: full census
of evaluation tiles intersecting known mound clusters — 2+
canonical-GT mounds single-linkage-chained at ≤ 125 m — with the
known mounds baked into the manifest so the review app can overlay
them and the reviewer marks only ADDITIONAL, unrecorded symbols.

Ordering: cluster-by-cluster within sheet (necropolis by
necropolis), so consecutive tiles share context. Every tile row
carries its world bounds and the tile-pixel positions of all
canonical-GT mounds within it.

Outputs (``--out-dir``, default ``results/cluster-audit``):

- ``census_manifest.csv`` — order_index, tile_name, map_name,
  cluster_id, tier='census', minx/miny/maxx/maxy, px_m.
- ``overlay.json`` — tile_name → [[x_px, y_px], …] for canonical-GT
  points inside the tile.
- ``tile_filelist.txt`` — rsync list.
- ``census_summary.json`` — cluster/tile counts and parameters.

Usage::

    python scripts/cluster_audit_sample.py [--gt PATH]

Reference (``--gt``): defaults to the Ruling-21 STANDARDISED reference
(`inputs/vectors/references/best-available-gt-55maps.geojson`, 4,731
student + 279 extension) since 2026-09-06. The first census build
(2026-09-01) used the canonical r50 file, whose 415 phantoms include
~150 that Ruling 21 had already removed as duplicates; 151 of them fell
on census tiles and the reviewer began flagging them by hand (Session
148). That build is kept under `results/cluster-audit/
superseded-canonical-r50-2026-09-01/`.

Zero API, seconds. Reads only the bounds and the reference; the tile
tree is not needed (fetch tiles afterwards with the file list).

Created: 2026-09-01 (Session 145)
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
from scipy.cluster.hierarchy import DisjointSet
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
CANONICAL_GT = PROJECT_ROOT / "inputs/vectors/references/canonical-gt-55maps-r50.geojson"
STANDARDISED_GT = PROJECT_ROOT / "inputs/vectors/references/best-available-gt-55maps.geojson"
TILE_PX = 384
CHAIN_M = 125.0   # single-linkage chaining distance (card § 5c)
BUFFER_M = 50.0   # cluster footprint buffer before tile intersection


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--out-dir", default="results/cluster-audit")
    ap.add_argument("--gt", default=str(STANDARDISED_GT.relative_to(PROJECT_ROOT)),
                    help="Reference point file (default: the Ruling-21 standardised "
                         "reference; pass the canonical r50 file to reproduce the "
                         "2026-09-01 build).")
    args = ap.parse_args()

    bounds = gpd.read_file(BOUNDS)
    gt_path = PROJECT_ROOT / args.gt
    gt = gpd.read_file(gt_path).to_crs(bounds.crs)
    logger.info("reference: %s (%d points; layers %s)", args.gt, len(gt),
                gt["layer"].value_counts().to_dict() if "layer" in gt else "n/a")
    xy = np.c_[gt.geometry.x, gt.geometry.y]
    tree = cKDTree(xy)

    ds = DisjointSet(range(len(xy)))
    for i, j in tree.query_pairs(CHAIN_M):
        ds.merge(i, j)
    clusters = sorted((s for s in ds.subsets() if len(s) >= 2),
                      key=lambda s: -len(s))
    logger.info("clusters (>=2 at %.0f m): %d covering %d mounds",
                CHAIN_M, len(clusters), sum(len(s) for s in clusters))

    # Tiles per cluster (50 m-buffered hull), census-ordered by
    # (sheet, cluster); a tile touching two clusters keeps its first.
    rows: list[dict] = []
    seen: set[str] = set()
    cluster_of: list[tuple[str, int, list[int]]] = []
    for cid, members in enumerate(clusters):
        pts = gt.iloc[sorted(members)]
        sheet = pts.iloc[0]["source_map"]
        cluster_of.append((sheet, cid, sorted(members)))
    cluster_of.sort(key=lambda t: (t[0], t[1]))

    for sheet, cid, members in cluster_of:
        pts = gt.iloc[members]
        buf = pts.buffer(BUFFER_M).union_all()
        tiles = bounds[bounds.geometry.intersects(buf)]
        for rec in tiles.itertuples():
            if rec.tile_name in seen:
                continue
            seen.add(rec.tile_name)
            minx, miny, maxx, maxy = rec.geometry.bounds
            rows.append({"tile_name": rec.tile_name,
                         "map_name": rec.tile_name.rsplit("_x", 1)[0],
                         "cluster_id": cid, "tier": "census",
                         "minx": minx, "miny": miny, "maxx": maxx,
                         "maxy": maxy, "px_m": (maxx - minx) / TILE_PX})
    for i, row in enumerate(rows):
        row["order_index"] = i
    logger.info("census tiles: %d", len(rows))

    # Overlay: canonical-GT tile-pixel positions per census tile.
    overlay: dict[str, list[list[float]]] = {}
    tile_geom = {r["tile_name"]: r for r in rows}
    joined = gpd.sjoin(
        gt, bounds[bounds["tile_name"].isin(seen)][["tile_name", "geometry"]],
        how="inner", predicate="within")
    for rec in joined.itertuples():
        t = tile_geom[rec.tile_name]
        x_px = (rec.geometry.x - t["minx"]) / t["px_m"]
        y_px = (t["maxy"] - rec.geometry.y) / t["px_m"]
        overlay.setdefault(rec.tile_name, []).append(
            [round(x_px, 1), round(y_px, 1)])

    out_dir = PROJECT_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    fields = ["order_index", "tile_name", "map_name", "cluster_id", "tier",
              "minx", "miny", "maxx", "maxy", "px_m"]
    with (out_dir / "census_manifest.csv").open("w", newline="") as fh:
        w = csvmod.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows({k: r[k] for k in fields} for r in rows)
    (out_dir / "overlay.json").write_text(json.dumps(overlay) + "\n")
    (out_dir / "tile_filelist.txt").write_text("".join(
        f"{r['map_name']}/{r['tile_name']}\n" for r in rows))
    (out_dir / "census_summary.json").write_text(json.dumps({
        "reference": args.gt, "n_reference_points": int(len(gt)),
        "chain_m": CHAIN_M, "buffer_m": BUFFER_M,
        "n_clusters": len(clusters),
        "n_mounds_in_clusters": int(sum(len(s) for s in clusters)),
        "n_census_tiles": len(rows),
        "n_overlay_tiles": len(overlay),
    }, indent=2) + "\n")
    logger.info("census manifest -> %s", out_dir.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
