#!/usr/bin/env python3
"""
55-map portfolio: dedup passes and K = 10 unions (verifier inputs).

The deployment analogue of `stride_prepare_and_union.py`, adapted to the
55-map protocol: no carrier clip (the corpus is scored full-extent by the
corrected-F1 machinery later), coverage gated against the committed
portfolio manifests with additive recovery-fragment merge, E80 within-pass
20 m deduplication, K = 10 c = 1 unions with per-cluster ``vote_count`` and
a ``source_tile`` taken from each cluster's first contributing origin tile
(sufficient for `run_pv.py extract`, which crops from the rasters by
centroid).

Gates: every pass must cover its manifest exactly after recovery merge
(E72); union internal count consistency on write. Union sizes are printed
with flex pricing at the measured $0.000687/call so the overnight ceiling
rule (card § 4b: total ≤ $50 → launch both; else Run A only) can be
applied mechanically.

Usage::

    python scripts/stride55_prepare_and_union.py           # gates + pricing
    python scripts/stride55_prepare_and_union.py --write

Zero API. Run on sapphire.

Created: 2026-08-26 (Session 142 overnight)
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
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_analysis import CRS  # noqa: E402
from scripts.grid_prepare_scoring import CoverageError, load_pass  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.merge_passes import deduplicate_within_pass  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OUTROOT = PROJECT_ROOT / "outputs/stride-55map-2026-08-25"
MANDIR = PROJECT_ROOT / "inputs/stride-55map-2026-08-25"
K = 10
DEDUP_METRES = 20.0
VF_CALL_USD = 0.000687

CELLS = {
    "g384_ov128_55map": "g384_ov128_55map_manifest.json",
    "g384_ov192_55map": "g384_ov192_55map_manifest.json",
}


def resolve_pass_paths(cell_dir: Path, run: str) -> list[Path]:
    """One pass's detection file(s): main plus any recovery fragment(s)."""
    main = sorted((cell_dir / run).glob("detections-*.geojson"))
    if len(main) != 1:
        raise FileNotFoundError(
            f"{cell_dir / run}: expected one detections geojson, found {len(main)}")
    paths = list(main)
    for frag in sorted(cell_dir.glob(f"{run}_recovery*")):
        paths.extend(sorted(frag.glob("detections-*.geojson")))
    return paths


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--root", default=None,
                    help="Output root override (e.g. "
                         "outputs/gemini37-55map-2026-08-29).")
    ap.add_argument("--cell", default=None,
                    help="Single cell override; requires --manifest.")
    ap.add_argument("--manifest", default=None,
                    help="Manifest path for the --cell override.")
    ap.add_argument("--k", type=int, default=None,
                    help="Pass-count override (default: the campaign K=10).")
    args = ap.parse_args()
    outroot = PROJECT_ROOT / args.root if args.root else OUTROOT
    k_total = args.k or K
    if args.cell:
        if not args.manifest:
            ap.error("--cell requires --manifest")
        cells = {args.cell: args.manifest}
    else:
        cells = CELLS

    total_cands = 0
    per_cell: dict[str, int] = {}
    for cell, manifest_name in cells.items():
        man_path = (PROJECT_ROOT / manifest_name if args.cell
                    else MANDIR / manifest_name)
        manifest = set(json.loads(man_path.read_text()))
        cell_dir = outroot / cell
        deduped_passes: list[list[dict]] = []
        for i in range(1, k_total + 1):
            run = f"run_{i}"
            raw, processed = load_pass(resolve_pass_paths(cell_dir, run))
            missing = manifest - processed
            extra = processed - manifest
            if missing or extra:
                raise CoverageError(
                    f"{cell}/{run}: {len(processed)} tiles vs {len(manifest)} "
                    f"pinned ({len(missing)} missing, {len(extra)} extra). "
                    f"Missing: {sorted(missing)[:5]}")
            deduped = deduplicate_within_pass(raw, distance_thresh=DEDUP_METRES)
            # deduplicate_within_pass already returns the cluster dicts the
            # cross-pass clusterer consumes: centroid, label, source_tiles,
            # cluster_size (verified against a live pass, 2026-08-26).
            if deduped and "centroid" not in deduped[0]:
                raise CoverageError(
                    f"{cell}/{run}: unexpected dedup item shape "
                    f"{sorted(deduped[0])}")
            deduped_passes.append(deduped)
            logger.info("%s %s: tiles %d, raw %d -> dedup %d",
                        cell, run, len(processed), len(raw), len(deduped))

        centroids, votes = cluster_votes(deduped_passes, 1)
        # First contributing origin tile per cluster, for the extract stage.
        tiles_flat = []
        for p in deduped_passes:
            tiles_flat.extend(d["source_tiles"][0] for d in p)
        gdf = gpd.GeoDataFrame(
            {"vote_count": votes},
            geometry=[Point(xy) for xy in centroids], crs=CRS)
        # cluster_votes returns clusters over the pooled detections in pool
        # order; recover a representative source tile by nearest pooled point.
        import numpy as np
        from scipy.spatial import cKDTree
        pooled = np.asarray(
            [d["centroid"] for p in deduped_passes for d in p], dtype=float)
        _, idx = cKDTree(pooled).query(
            np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
        gdf["source_tile"] = [tiles_flat[i] for i in idx]

        per_cell[cell] = len(gdf)
        total_cands += len(gdf)
        cost = len(gdf) * VF_CALL_USD
        logger.info("%s: union n=%d, verifier flex $%.2f", cell, len(gdf), cost)

        if args.write:
            dest = outroot / "verifier" / cell / f"union_k{k_total}.geojson"
            dest.parent.mkdir(parents=True, exist_ok=True)
            gdf.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
            written = len(json.loads(dest.read_text())["features"])
            if written != len(gdf):
                raise CoverageError(f"{cell}: wrote {written} != {len(gdf)}")
            logger.info("wrote %s", dest.relative_to(PROJECT_ROOT))

    logger.info("TOTAL candidates %d -> verifier flex $%.2f "
                "(overnight ceiling $50; card § 4b rule applies)",
                total_cands, total_cands * VF_CALL_USD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
