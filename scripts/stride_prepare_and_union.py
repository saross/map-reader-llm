#!/usr/bin/env python3
"""
Stride-programme scoring preparation: dedup passes and K = 10 unions.

Applies the grid's exact scoring chain (E80 within-pass 20 m deduplication,
E72 coverage gates, common-footprint clip) to the five overnight stride
cells — Phase B's g512_ov176 / g384_ov128 / g256_ov064 / g512_ov320 and
Phase C's g384_ov240 — then materialises each cell's K = 10 union
(c = 1, k >= 1, per-cluster ``vote_count``) as the verifier's input, in the
same shape `materialise_grid_unions.py` produced for the grid.

Per pass: the main detections file is merged with its additive
``run_<N>_recovery`` fragment where one exists, the coverage record is
asserted EXACTLY equal to the cell's pinned manifest (E72; a short pass
would turn missing tiles' ground truth into artificial false negatives),
the pass is deduplicated at 20 m, and the deduped set is written in the
common scope (the grid's four-way-intersection carrier, the programme's
fixed reference footprint).

Unlike the grid's union materialisation there are no documented external
counts to gate against (these cells are new); the gates are internal:
full pass resolution (10/10), exact coverage, and cluster-count
consistency between the sweep-side loader and the written union.

Usage::

    python scripts/stride_prepare_and_union.py          # gates + dry run
    python scripts/stride_prepare_and_union.py --write

Zero API. Run on sapphire beside the outputs.

Created: 2026-08-25 (Session 142 overnight)
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

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

COMMON_BOUNDS = (
    PROJECT_ROOT / "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson")
MANDIR = PROJECT_ROOT / "inputs/stride-phaseb-2026-08-25"
K = 10
DEDUP_METRES = 20.0

#: Cell -> (output root, manifest filename). Phase C's cell lives under its
#: own root; everything else under the Phase B root.
CELLS: dict[str, tuple[str, str]] = {
    "g512_ov176": ("outputs/stride-phaseb-2026-08-25", "g512_ov176_manifest.json"),
    "g384_ov128": ("outputs/stride-phaseb-2026-08-25", "g384_ov128_manifest.json"),
    "g256_ov064": ("outputs/stride-phaseb-2026-08-25", "g256_ov064_manifest.json"),
    "g512_ov320": ("outputs/stride-phaseb-2026-08-25", "g512_ov320_manifest.json"),
    "g384_ov240": ("outputs/stride-phasec-2026-08-25", "g384_ov240_manifest.json"),
}


def resolve_pass_paths(cell_dir: Path, run: str) -> list[Path]:
    """Return one pass's detection file(s): main plus any recovery fragment.

    Args:
        cell_dir: The cell's run root.
        run: Run directory name (``run_1`` .. ``run_10``).

    Returns:
        Paths in merge order (main first).

    Raises:
        FileNotFoundError: If the main pass file is absent or ambiguous.
    """
    main = sorted((cell_dir / run).glob("detections-*.geojson"))
    if len(main) != 1:
        raise FileNotFoundError(
            f"{cell_dir / run}: expected exactly one detections geojson, "
            f"found {len(main)}")
    paths = list(main)
    recovery = sorted((cell_dir / f"{run}_recovery").glob("detections-*.geojson"))
    if len(recovery) > 1:
        raise FileNotFoundError(
            f"{cell_dir / run}_recovery: multiple recovery files")
    paths.extend(recovery)
    return paths


def main() -> int:
    """Prepare all five cells and (with ``--write``) materialise the unions.

    Returns:
        Process exit status (0 on success).
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="Write dedup passes and unions after gates pass.")
    args = ap.parse_args()

    common_gdf = gpd.read_file(COMMON_BOUNDS)
    common_tiles = sorted(common_gdf["tile_name"].tolist())
    common_geom = common_gdf.geometry.union_all()
    logger.info("common carrier: %d tiles", len(common_gdf))

    union_counts: dict[str, int] = {}
    for cell, (root, manifest_name) in CELLS.items():
        cell_dir = PROJECT_ROOT / root / cell
        scoring = PROJECT_ROOT / root / "scoring"
        manifest = set(json.loads((MANDIR / manifest_name).read_text()))

        for i in range(1, K + 1):
            run = f"run_{i}"
            paths = resolve_pass_paths(cell_dir, run)
            raw, processed = load_pass(paths)
            missing = manifest - processed
            extra = processed - manifest
            if missing or extra:
                raise CoverageError(
                    f"{cell}/{run}: {len(processed)} tiles vs {len(manifest)} "
                    f"pinned ({len(missing)} missing, {len(extra)} extra). "
                    f"Missing: {sorted(missing)[:5]}")
            deduped = deduplicate_within_pass(raw, distance_thresh=DEDUP_METRES)
            if args.write:
                write_dedup_geojson(
                    deduped, common_gdf, common_tiles,
                    scoring / "common" / cell / run / "detections_dedup.geojson",
                    clip_geom=common_geom,
                )
            logger.info(
                "%s %s: tiles %d%s, raw %d -> dedup %d (-%.1f %%)",
                cell, run, len(processed),
                " (+recovery)" if len(paths) > 1 else "",
                len(raw), len(deduped),
                100 * (len(raw) - len(deduped)) / len(raw) if raw else 0.0,
            )

        if not args.write:
            continue
        passes = load_cell_passes(scoring, cell)
        if len(passes) != K:
            raise CoverageError(f"{cell}: loader returned {len(passes)} passes")
        gdf = union_with_votes(passes, common_gdf)
        votes = gdf["vote_count"].value_counts().sort_index().to_dict()
        dest = PROJECT_ROOT / root / "verifier" / cell / "union_k10.geojson"
        dest.parent.mkdir(parents=True, exist_ok=True)
        gdf.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
        written = len(json.loads(dest.read_text())["features"])
        if written != len(gdf):
            raise CoverageError(
                f"{cell}: wrote {written} features, built {len(gdf)}")
        union_counts[cell] = len(gdf)
        logger.info("%s: union n=%d, votes %s -> %s",
                    cell, len(gdf), votes, dest.relative_to(PROJECT_ROOT))

    if union_counts:
        total = sum(union_counts.values())
        logger.info("TOTAL union candidates: %d (verifier flex estimate "
                    "$%.2f at $0.000687/call)", total, total * 0.000687)
    return 0


if __name__ == "__main__":
    sys.exit(main())
