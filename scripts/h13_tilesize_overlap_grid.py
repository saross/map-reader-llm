#!/usr/bin/env python3
"""
Tile size x overlap: does 384 px stay the sweet spot once overlap is high?

The H13 Tier-0 sweep showed that 50 % overlap at 512 px, which is the
*worst* configuration on raw single-pass F1, becomes the best once a
precision filter is applied. That raises the question this script
answers: 384 px was the study's sweet spot at the standard 12.5 %
overlap, but tile size and overlap both trade precision for recall, so
they may not be additive. The comparison needs three existing cells and
one that does not exist yet:

===========  ==========  ================================================
Tile size    Overlap     Status
===========  ==========  ================================================
384 px       12.5 %      exists — pv-diag-384 MINIMAL text T = 1.0, K = 10
512 px       12.5 %      exists — H13 arm A, K = 3
512 px       50 %        exists — H13 arm C, K = 3
384 px       50 %        MISSING — needs an API run
===========  ==========  ================================================

This script scores the three existing cells like for like. Two things
make the naive comparison invalid, and both are handled here:

1. **Different evaluation footprints.** The 384 px corpus (era-2-487)
   covers 1415.8 km² holding 435 reference mounds; the H13 512 px common
   scope covers 1637.5 km² holding 538. Comparing F1 across them would
   compare different denominators over different ground. Every cell is
   therefore re-scored on the intersection of the two (~1367 km²),
   carried on the 512 px arm-A grid clipped to it.

2. **Different deduplication treatment.** The committed 384 px consensus
   numbers were produced without the within-pass cross-tile
   deduplication that the H13 chain applies. Every cell here is
   deduplicated identically, so the committed 384 px F1 values are NOT
   comparable with the numbers this script produces — the same caveat
   that applies to the committed arm-A values.

Each cell is swept over the same corroboration x consensus grid as the
Tier-0 analysis, and reported at matched K as well as at its own best K,
because consensus F1 depends on the number of passes.

Classification: POST-HOC (E41-class), as for the Tier-0 sweep.

Usage::

    python scripts/h13_tilesize_overlap_grid.py \\
        --output-dir results/h13-overlap-2026-08-18/tilesize-grid

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
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

from scripts.h13_aggregation_sweep import aggregate, write_cell  # noqa: E402
from scripts.lib_detection_paths import find_pass_geojsons  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    calculate_f1_internal,
    get_map_name,
    scope_references_to_tiles,
)
from scripts.merge_passes import deduplicate_within_pass  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BUFFER_M = 20
DEDUP_M = 20.0
CORROBORATION = (1, 2, 3)
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS_384 = PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
H13_SCORING = PROJECT_ROOT / "outputs/h13/scoring"
POOL_384 = PROJECT_ROOT / "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0"

#: The three existing cells. ``source`` is either a directory of run_N
#: subdirectories holding raw detections (384 px) or the prepared H13
#: deduplicated sets (512 px, already deduplicated by prepare_h13_scoring).
CELLS: dict[str, dict[str, Any]] = {
    "384px-12.5pct": {"tile_px": 384, "overlap": 0.125, "kind": "raw384"},
    "512px-12.5pct": {"tile_px": 512, "overlap": 0.125, "kind": "h13", "arm": "armA"},
    "512px-50pct": {"tile_px": 512, "overlap": 0.50, "kind": "h13", "arm": "armC"},
}


def build_common_scope(output_dir: Path) -> tuple[Path, Any, int]:
    """Build the carrier grid shared by the 384 px and 512 px corpora.

    Args:
        output_dir: Directory the bounds file is written to.

    Returns:
        Tuple of (bounds path, common geometry, ground-truth count in scope).
    """
    u384 = gpd.read_file(BOUNDS_384).geometry.union_all()
    u512 = gpd.read_file(
        H13_SCORING / "bounds" / "h13_common_bounds.geojson").geometry.union_all()
    common = u384.intersection(u512)

    grid = gpd.read_file(H13_SCORING / "bounds" / "h13_common_bounds.geojson").copy()
    grid["geometry"] = grid.geometry.intersection(common)
    grid = grid[grid.geometry.notna() & ~grid.geometry.is_empty]
    grid = grid[grid.geometry.area > 1.0].copy()

    target = output_dir / "bounds" / "tilesize_common_bounds.geojson"
    target.parent.mkdir(parents=True, exist_ok=True)
    grid.to_file(target, driver="GeoJSON")

    gdf_ref = gpd.read_file(GROUND_TRUTH)
    n_gt = 0
    for m in sorted({get_map_name(n) for n in grid["tile_name"]}):
        mb = grid[grid["tile_name"].str.startswith(m)]
        rs = gdf_ref[gdf_ref["Map"] == m]
        n_gt += len(scope_references_to_tiles(rs, mb)) if not rs.empty else 0

    logger.info(
        "common scope: %.1f km² (384 px corpus %.1f, H13 512 px %.1f), "
        "%d carrier tiles, %d ground-truth mounds",
        common.area / 1e6, u384.area / 1e6, u512.area / 1e6, len(grid), n_gt,
    )
    return target, common, n_gt


def load_cell_passes(spec: dict, common: Any) -> dict[str, list[dict]]:
    """Load one cell's passes, deduplicated and clipped to the common scope.

    Args:
        spec: One entry of :data:`CELLS`.
        common: The common footprint geometry.

    Returns:
        Mapping pass id -> detection dicts ready for :func:`aggregate`.
    """
    passes: dict[str, list[dict]] = {}

    if spec["kind"] == "raw384":
        run_dirs = sorted(POOL_384.glob("run_*"),
                          key=lambda p: int(p.name.split("_")[1]))
        for run_dir in run_dirs:
            files = find_pass_geojsons(run_dir)
            if not files:
                continue
            data = json.loads(files[0].read_text())
            deduped = deduplicate_within_pass(
                data.get("features", []), distance_thresh=DEDUP_M)
            passes[run_dir.name] = [
                d for d in deduped if common.contains(Point(d["centroid"]))
            ]
    else:
        arm = spec["arm"]
        for run in ("run_1", "run_2", "run_3"):
            path = H13_SCORING / "common" / arm / run / "detections_dedup.geojson"
            data = json.loads(path.read_text())
            dets = []
            for f in data["features"]:
                x, y = f["geometry"]["coordinates"]
                if not common.contains(Point(x, y)):
                    continue
                props = f["properties"]
                dets.append({
                    "centroid": (x, y),
                    "label": props.get("label", "mound"),
                    "source_tiles": (props.get("origin_tiles") or "").split(";"),
                    "cluster_size": int(props.get("cluster_size", 1)),
                })
            passes[run] = dets
    return passes


def main() -> int:
    """Score the three existing tile-size x overlap cells like for like.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="Tile size x overlap grid on a shared footprint.")
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results/h13-overlap-2026-08-18/tilesize-grid")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    bounds_path, common, n_gt = build_common_scope(args.output_dir)
    bounds = gpd.read_file(bounds_path)
    gdf_ref = gpd.read_file(GROUND_TRUTH)

    results: list[dict[str, Any]] = []
    for name, spec in CELLS.items():
        passes = load_cell_passes(spec, common)
        n_passes = len(passes)
        logger.info("%s: %d passes, %s detections/pass after dedup+clip",
                    name, n_passes,
                    round(sum(len(v) for v in passes.values()) / max(n_passes, 1)))

        # Matched K = 3 uses the first three passes, so every cell is
        # compared at the pass count the 512 px arms actually have.
        subsets = {"K3": dict(list(passes.items())[:3])}
        if n_passes > 3:
            subsets[f"K{n_passes}"] = passes

        for k_label, subset in subsets.items():
            kk = len(subset)
            for c in CORROBORATION:
                for k in range(1, kk + 1):
                    clusters = aggregate(subset, c, k)
                    gdf = write_cell(
                        clusters, bounds,
                        args.output_dir / "cells" / f"{name}_{k_label}_c{c}_k{k}.geojson")
                    if gdf.empty:
                        p = r = f1 = 0.0
                    else:
                        p, r, f1 = calculate_f1_internal(
                            gdf, gdf_ref, bounds, buffer_metres=BUFFER_M)
                    results.append({
                        "cell": name, "tile_px": spec["tile_px"],
                        "overlap_fraction": spec["overlap"],
                        "K": kk, "K_label": k_label,
                        "min_corroboration": c, "min_votes": k,
                        "n_detections": int(len(gdf)),
                        "precision": p, "recall": r, "f1": f1,
                    })

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "POST-HOC (E41-class); see the Tier-0 sweep.",
        "scope": {
            "name": "384 px corpus n H13 512 px common",
            "area_km2": common.area / 1e6,
            "carrier_tiles": len(bounds),
            "ground_truth": n_gt,
            "buffer_metres": BUFFER_M,
            "dedup_metres": DEDUP_M,
        },
        "cells": results,
    }
    (args.output_dir / "tilesize_grid.json").write_text(json.dumps(payload, indent=2))

    logger.info("--- best cell per (configuration, K) ---")
    for name in CELLS:
        for k_label in sorted({r["K_label"] for r in results if r["cell"] == name}):
            sel = [r for r in results if r["cell"] == name and r["K_label"] == k_label]
            best = max(sel, key=lambda x: x["f1"])
            logger.info(
                "%-16s %-4s best: c>=%d k>=%d -> F1=%.4f (P=%.4f R=%.4f, n=%d)",
                name, k_label, best["min_corroboration"], best["min_votes"],
                best["f1"], best["precision"], best["recall"], best["n_detections"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
