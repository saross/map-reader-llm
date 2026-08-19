#!/usr/bin/env python3
"""Phase 0.3 — re-score the 256 px and 384 px proposer-verifier cells on their
common evaluation footprint.

Why this exists
---------------
The premise that "256 px swamps the verifier" rests on a cross-scope comparison.
``pv-diag-256::verified-adv-text-consensus-5of5`` scores F1@20 m = 0.8558 on
scope ``px256-1032`` (1,032 tiles, 1,324.8 km², 431 reference mounds), while
``pv-diag-384::verified-adv-text-min-6of10`` scores 0.8835 on ``era-2-487``
(487 tiles, 1,415.8 km², 435 mounds). Different footprints, different
ground-truth denominators, and a gap of only 0.028. Session 136 corrected this
class of confound four separate times; it has never been corrected here, and the
premise currently constrains the recall-levers design.

What it does
------------
1. Intersects the two evaluation-bounds footprints.
2. Builds a carrier tile grid clipped to that intersection. Both the 256 px and
   the 384 px grids are used in turn, because the carrier determines which
   reference mounds are in scope and a conclusion that flips with the carrier is
   not a conclusion.
3. Clips both committed detection sets to the intersection.
4. Scores both with one scorer, at 20 m, with and without a uniform 20 m
   within-set deduplication pass (erratum E80: two scoring paths coexist, so a
   cross-architecture comparison must state which it used).

Honest boundary: this re-scores committed detections. It does not re-run the
verifier, so it answers "is the gap an artefact of scope?" and not "would the
verifier behave differently on a common footprint?".

Usage
-----
    python scripts/phase0_3_tilesize_common_footprint.py \
        --output-dir results/phase0-recall-levers/tilesize-premise
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (  # noqa: E402
    calculate_f1_internal,
    get_map_name,
    scope_references_to_tiles,
)
from scripts.merge_passes import deduplicate_within_pass  # noqa: E402
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BUFFER_M = 20
DEDUP_M = 20.0
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS = {
    256: PROJECT_ROOT / "inputs/vectors/bounds/256/full_evaluation_bounds.geojson",
    384: PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
}

#: The two committed cells, with the published figure each is being checked
#: against. ``detections`` is read from the condition's own ``cli_args`` in the
#: source evaluation, so the file scored here is the file that was scored then.
CELLS: dict[str, dict[str, Any]] = {
    "256px-pv-consensus-5of5": {
        "condition": "pv-diag-256::verified-adv-text-consensus-5of5",
        "tile_px": 256,
        "detections": "outputs/era1-pv-stage-d/256-consensus-text-5of5/pass_1/accepted_t0.2.geojson",
        "published_f1_at_20m": 0.8558,
        "published_scope": "px256-1032",
    },
    "384px-pv-min-6of10": {
        "condition": "pv-diag-384::verified-adv-text-min-6of10",
        "tile_px": 384,
        "detections": "results/verifier-robustness/min-thinking-sets/text-min-t07-10pass-6of10-n1-pt0.2.geojson",
        "published_f1_at_20m": 0.8835,
        "published_scope": "era-2-487",
    },
}


def build_common_scope(output_dir: Path) -> tuple[Any, dict[int, gpd.GeoDataFrame]]:
    """Intersect the two footprints and clip each carrier grid to the result.

    Args:
        output_dir: Directory the clipped bounds files are written to.

    Returns:
        Tuple of (common geometry, {tile_px: clipped carrier grid}).
    """
    grids = {px: gpd.read_file(path) for px, path in BOUNDS.items()}
    unions = {px: g.geometry.union_all() for px, g in grids.items()}
    common = unions[256].intersection(unions[384])

    clipped: dict[int, gpd.GeoDataFrame] = {}
    for px, grid in grids.items():
        g = grid.copy()
        g["geometry"] = g.geometry.intersection(common)
        g = g[g.geometry.notna() & ~g.geometry.is_empty]
        # Drop slivers: a tile clipped to a few square metres carries no
        # evaluation signal but would inflate the tile denominator.
        g = g[g.geometry.area > 1.0].copy()
        target = output_dir / "bounds" / f"common_carrier_{px}px.geojson"
        target.parent.mkdir(parents=True, exist_ok=True)
        g.to_file(target, driver="GeoJSON")
        clipped[px] = g

    logger.info(
        "footprints: 256 px %.1f km^2, 384 px %.1f km^2, common %.1f km^2 "
        "(%.1f%% of 256, %.1f%% of 384)",
        unions[256].area / 1e6, unions[384].area / 1e6, common.area / 1e6,
        100 * common.area / unions[256].area, 100 * common.area / unions[384].area,
    )
    for px, g in clipped.items():
        logger.info("  carrier %d px: %d tiles after clip (from %d)",
                    px, len(g), len(grids[px]))
    return common, clipped


def count_scoped_references(grid: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame) -> int:
    """Count reference mounds that fall inside a carrier grid, per map sheet."""
    total = 0
    for m in sorted({get_map_name(n) for n in grid["tile_name"]}):
        mb = grid[grid["tile_name"].str.startswith(m)]
        rs = gdf_ref[gdf_ref["Map"] == m]
        if not rs.empty:
            total += len(scope_references_to_tiles(rs, mb))
    return total


def load_detections(spec: dict, common: Any, dedup: bool) -> gpd.GeoDataFrame:
    """Read a cell's committed detections, clip to the common scope, optionally dedup.

    Args:
        spec: One entry of :data:`CELLS`.
        common: The common footprint geometry (EPSG:32635).
        dedup: Apply a uniform 20 m within-set deduplication (erratum E80).

    Returns:
        A GeoDataFrame of point detections in EPSG:32635. The ``source_tile``
        column is added later, per carrier, because a detection's scoring tile
        depends on which carrier grid it is booked against.
    """
    gdf = gpd.read_file(PROJECT_ROOT / spec["detections"]).to_crs("EPSG:32635")
    gdf = gdf[gdf.geometry.notna()].copy()
    gdf["geometry"] = gdf.geometry.centroid
    gdf = gdf[gdf.geometry.apply(lambda p: common.contains(Point(p.x, p.y)))].copy()

    if dedup:
        feats = [
            {"geometry": {"type": "Point", "coordinates": (g.x, g.y)}, "properties": {}}
            for g in gdf.geometry
        ]
        kept = deduplicate_within_pass(feats, distance_thresh=DEDUP_M)
        gdf = gpd.GeoDataFrame(
            geometry=[Point(*d["centroid"]) for d in kept], crs="EPSG:32635")
    return gdf.reset_index(drop=True)


def main() -> int:
    """Score both cells on the common footprint under both carriers.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="Re-score the 256 px premise on a common footprint.")
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results/phase0-recall-levers/tilesize-premise")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    common, carriers = build_common_scope(args.output_dir)
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    scoped_refs = {px: count_scoped_references(g, gdf_ref) for px, g in carriers.items()}
    for px, n in scoped_refs.items():
        logger.info("  carrier %d px: %d reference mounds in scope", px, n)

    rows: list[dict[str, Any]] = []
    for name, spec in CELLS.items():
        for dedup in (False, True):
            gdf = load_detections(spec, common, dedup)
            for px, grid in carriers.items():
                if gdf.empty:
                    p = r = f1 = 0.0
                else:
                    # Book each detection to one carrier tile by nearest tile
                    # centroid, the rule E79 settled and the same rule the
                    # evaluator applies to references. Assigning per carrier
                    # keeps detections and references on one tiling.
                    scored = gdf.copy()
                    scored["source_tile"] = assign_primary_tiles(scored, grid)
                    scored = scored[scored["source_tile"].notna()].copy()
                    p, r, f1 = calculate_f1_internal(
                        scored, gdf_ref, grid, buffer_metres=BUFFER_M)
                rows.append({
                    "cell": name,
                    "condition": spec["condition"],
                    "tile_px": spec["tile_px"],
                    "carrier_px": px,
                    "uniform_dedup_20m": dedup,
                    "n_detections": int(len(gdf)),
                    "n_detections_booked": int(len(scored)) if not gdf.empty else 0,
                    "n_reference_in_scope": scoped_refs[px],
                    "precision": p,
                    "recall": r,
                    "f1": f1,
                    "published_f1_at_20m": spec["published_f1_at_20m"],
                    "published_scope": spec["published_scope"],
                })
                logger.info(
                    "%-26s carrier=%dpx dedup=%-5s -> F1=%.4f (P=%.4f R=%.4f, n=%d)",
                    name, px, dedup, f1, p, r, len(gdf))

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "POST-HOC (E41-class) — a re-scoring of committed "
                          "detections on a corrected footprint, not a registered test.",
        "question": "Does the 0.028 F1 gap between the 256 px and 384 px "
                    "proposer-verifier cells survive a common evaluation footprint?",
        "scope": {
            "name": "256 px corpus INTERSECT 384 px corpus",
            "area_km2": common.area / 1e6,
            "buffer_metres": BUFFER_M,
            "dedup_metres": DEDUP_M,
            "carriers": {
                str(px): {"tiles": len(g), "reference_mounds": scoped_refs[px]}
                for px, g in carriers.items()
            },
        },
        "cells": rows,
    }
    out = args.output_dir / "tilesize_premise.json"
    out.write_text(json.dumps(payload, indent=2))
    logger.info("wrote %s", out)

    logger.info("--- gap, 384 px minus 256 px ---")
    for px in carriers:
        for dedup in (False, True):
            sel = {r["tile_px"]: r["f1"] for r in rows
                   if r["carrier_px"] == px and r["uniform_dedup_20m"] == dedup}
            logger.info("carrier=%dpx dedup=%-5s: %.4f - %.4f = %+.4f",
                        px, dedup, sel[384], sel[256], sel[384] - sel[256])
    return 0


if __name__ == "__main__":
    sys.exit(main())
