#!/usr/bin/env python3
"""
Final-check manifest for the cluster census: one tile per edge-safety mark.

The reviewer marks a mound that straddles a tile edge "to be safe"; the
adjudication (`empty_tile_adjudicate.py --mode census`) classes such a
mark known-in-GT and lists it under ``edge_safety_marks``. For the final
check the reviewer wants to see each such mark together with the
pre-existing reference points, on the evaluation tile where the point
lies FARTHEST from any edge (usually the neighbouring tile, which shows
the whole symbol). This script builds that review set:

- ``manifest.csv`` — one row per edge-safety mark, in census order:
  order_index, tile_name (the best tile), map_name, tier='final-check',
  minx/miny/maxx/maxy, px_m, plus ``source_tile``, ``source_position``,
  ``gt_id``, ``gt_m``, ``edge_m_source``, ``edge_m_here``.
- ``overlay.json`` — tile_name → {"known": [[x_px, y_px], …],
  "review": [[x_px, y_px], …]}: the standardised reference points inside
  the tile (drawn yellow by the review app) and the reviewer's own mark
  (drawn magenta).
- ``tile_filelist.txt`` — ``<map>/<tile>`` paths for rsync from the
  ``inputs/tiles_384_55maps`` tree on sapphire.

Review with::

    streamlit run scripts/review_empty_tiles_app.py -- \
        --manifest results/cluster-audit/final-check/manifest.csv \
        --tiles-dir inputs/cluster-audit-tiles \
        --output results/cluster-audit/final-check/verdicts.csv \
        --overlay results/cluster-audit/final-check/overlay.json

Usage::

    python scripts/final_check_manifest.py [--adjudication PATH] [--out-dir DIR]

Zero API, seconds.

Created: 2026-09-06 (Session 148)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.empty_tile_adjudicate import GT_FILES, edge_distance_m  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
TILE_PX = 384


def to_px(x: float, y: float, t: dict) -> list[float]:
    """World (metres) to tile pixel coordinates (origin top-left)."""
    return [round((x - t["minx"]) / t["px_m"], 1), round((t["maxy"] - y) / t["px_m"], 1)]


def main() -> int:
    """Build the final-check manifest, overlay, and file list."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--adjudication", default="results/cluster-audit/adjudication.json")
    ap.add_argument("--out-dir", default="results/cluster-audit/final-check")
    args = ap.parse_args()

    adj = json.loads((PROJECT_ROOT / args.adjudication).read_text())
    marks = {(r["tile_name"]): r for r in adj["per_mark"] if r["class"] == "known-in-GT"}
    edge_list = adj["census"]["edge_safety_marks"]
    logger.info("edge-safety marks: %d (reference %s)", len(edge_list), adj["reference"])

    bounds = gpd.read_file(BOUNDS)
    gt = gpd.read_file(PROJECT_ROOT / GT_FILES[adj["reference"]]).to_crs(bounds.crs)

    rows, overlay, files = [], {}, []
    for k, e in enumerate(sorted(edge_list, key=lambda r: r["position"])):
        m = marks[e["tile_name"]]
        pt = Point(m["x_world"], m["y_world"])
        # Every evaluation tile containing the mark; keep the one where it
        # sits farthest from an edge (the source tile is always a candidate).
        cands = bounds[bounds.geometry.contains(pt)]
        best, best_edge = None, -1.0
        for rec in cands.itertuples():
            minx, miny, maxx, maxy = rec.geometry.bounds
            d = edge_distance_m(pt.x, pt.y, minx, miny, maxx, maxy)
            if d > best_edge:
                best, best_edge = rec, d
        if best is None:
            raise RuntimeError(f"{e['tile_name']}: mark falls in no evaluation tile")
        minx, miny, maxx, maxy = best.geometry.bounds
        t = {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy,
             "px_m": (maxx - minx) / TILE_PX}
        rows.append({"order_index": k, "tile_name": best.tile_name,
                     "map_name": best.tile_name.rsplit("_x", 1)[0], "tier": "final-check",
                     **t, "source_tile": e["tile_name"], "source_position": e["position"],
                     "gt_id": e["gt_id"], "gt_m": e["gt_m"],
                     "edge_m_source": e["edge_m"], "edge_m_here": round(best_edge, 1)})
        inside = gt[gt.geometry.within(best.geometry)]
        overlay[best.tile_name] = {
            "known": [to_px(g.x, g.y, t) for g in inside.geometry],
            "review": [to_px(pt.x, pt.y, t)],
        }
        files.append(f"{rows[-1]['map_name']}/{best.tile_name}")
        logger.info("%3d %-42s -> %-42s edge %5.1f -> %5.1f m (%d known)", e["position"],
                    e["tile_name"], best.tile_name, e["edge_m"], best_edge, len(inside))

    out = PROJECT_ROOT / args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "manifest.csv", index=False)
    (out / "overlay.json").write_text(json.dumps(overlay) + "\n")
    (out / "tile_filelist.txt").write_text("".join(f + "\n" for f in dict.fromkeys(files)))
    logger.info("final-check manifest -> %s (%d tiles, %d distinct)", out, len(rows),
                len(set(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
