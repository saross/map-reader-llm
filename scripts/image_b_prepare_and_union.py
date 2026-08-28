#!/usr/bin/env python3
"""
Image-on-B GS cell: dedup passes and the K = 10 union (verifier input).

Applies the stride/grid scoring chain UNCHANGED (E80 within-pass 20 m
deduplication, E72 exact-coverage gates with additive recovery-fragment
merge, common-footprint carrier clip, c = 1 union with per-cluster
``vote_count``) to the image cell `outputs/image-b-gs-2026-08-28/
g384_ov192_image` — the like-for-like counterpart of the text-B union
the grid campaign materialised. Card: `planning/image-b-gs-2026-08-28.md`
§ 6 step 5.

Usage::

    python scripts/image_b_prepare_and_union.py           # gates + dry run
    python scripts/image_b_prepare_and_union.py --write

Zero API. Run on sapphire beside the outputs.

Created: 2026-08-28 (Session 143)
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_analysis import load_cell_passes  # noqa: E402
from scripts.grid_prepare_scoring import CoverageError, load_pass  # noqa: E402
from scripts.materialise_grid_unions import union_with_votes  # noqa: E402
from scripts.merge_passes import deduplicate_within_pass  # noqa: E402
from scripts.prepare_h13_scoring import write_dedup_geojson  # noqa: E402
from scripts.stride_prepare_and_union import (  # noqa: E402
    COMMON_BOUNDS,
    DEDUP_METRES,
    resolve_pass_paths,
)
from scripts.stride_prepare_and_union import K as DEFAULT_K  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = PROJECT_ROOT / "outputs/image-b-gs-2026-08-28"  # overridable via --root
MANIFEST = PROJECT_ROOT / "inputs/grid-2026-08-18/grid_384_ov192_manifest.json"
VF_CALL_USD = 0.000687


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--cell", default="g384_ov192_image",
                    help="Cell directory under the output root "
                         "(g384_ov192_image or g384_ov192_image_high).")
    ap.add_argument("--root", default=None,
                    help="Output root override (e.g. "
                         "outputs/gemini37-screen-2026-08-28).")
    ap.add_argument("--k", type=int, default=None,
                    help="Pass count override (default: the stride K=10).")
    args = ap.parse_args()
    CELL = args.cell  # noqa: N806 — keeps the original constant name in situ
    root = PROJECT_ROOT / args.root if args.root else ROOT
    k_total = args.k or DEFAULT_K

    common_gdf = gpd.read_file(COMMON_BOUNDS)
    common_tiles = sorted(common_gdf["tile_name"].tolist())
    common_geom = common_gdf.geometry.union_all()
    manifest = set(json.loads(MANIFEST.read_text()))
    cell_dir = root / CELL
    scoring = root / "scoring"

    for i in range(1, k_total + 1):
        run = f"run_{i}"
        paths = resolve_pass_paths(cell_dir, run)
        raw, processed = load_pass(paths)
        missing = manifest - processed
        extra = processed - manifest
        if missing or extra:
            raise CoverageError(
                f"{CELL}/{run}: {len(processed)} tiles vs {len(manifest)} "
                f"pinned ({len(missing)} missing, {len(extra)} extra)")
        deduped = deduplicate_within_pass(raw, distance_thresh=DEDUP_METRES)
        if args.write:
            write_dedup_geojson(
                deduped, common_gdf, common_tiles,
                scoring / "common" / CELL / run / "detections_dedup.geojson",
                clip_geom=common_geom)
        logger.info("%s %s: tiles %d%s, raw %d -> dedup %d", CELL, run,
                    len(processed),
                    " (+recovery)" if len(paths) > 1 else "",
                    len(raw), len(deduped))

    if not args.write:
        logger.info("dry run complete — re-run with --write")
        return 0
    passes = load_cell_passes(scoring, CELL)
    if len(passes) != k_total:
        raise CoverageError(f"{CELL}: loader returned {len(passes)} passes")
    gdf = union_with_votes(passes, common_gdf)
    votes = gdf["vote_count"].value_counts().sort_index().to_dict()
    dest = root / "verifier" / CELL / f"union_k{k_total}.geojson"
    dest.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
    written = len(json.loads(dest.read_text())["features"])
    if written != len(gdf):
        raise CoverageError(f"{CELL}: wrote {written} != built {len(gdf)}")
    logger.info("%s: union n=%d, votes %s | verifier flex est $%.2f -> %s",
                CELL, len(gdf), votes, len(gdf) * VF_CALL_USD,
                dest.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
