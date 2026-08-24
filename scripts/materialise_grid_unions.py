#!/usr/bin/env python3
"""Materialise the four grid cells' K = 10 union candidate sets (verifier input).

The Session 136 grid experiment (`results/grid-2026-08-18/findings.md`)
costed a verifier stage over the four cells' K = 10 unions — the
(c >= 1, k >= 1) operating point — at US$6.33 for 9,133 candidates, but
the union SETS existed only inside the sweep, never as files. The
Principal Investigator approved the spend on 2026-08-24 with an
exact-reproduction stop rule, and this script produces the verifier's
inputs under that rule:

* passes load through the SAME loader the sweep used
  (``grid_analysis.load_cell_passes``, common scope, runs 1–10);
* clustering is the SAME function at the same corroboration level
  (``h13_k_sensitivity.cluster_votes`` at c = 1);
* the carrier-tile filter replicates ``grid_analysis.as_gdf`` (clusters
  falling on no carrier tile are dropped), with each cluster's vote
  count carried through the filter;
* the GATE: each cell's surviving count must equal the documented
  figure EXACTLY (1,402 / 2,585 / 1,827 / 3,319; findings § verifier
  costing) or the script refuses to write and exits non-zero.

Outputs land as spec-compliant EPSG:4326 GeoJSON (the shape
``run_pv.py extract`` consumes), one file per cell, each feature
carrying ``vote_count`` so post-verifier threshold sweeps stay free.

Usage::

    python scripts/materialise_grid_unions.py            # dry run, gates only
    python scripts/materialise_grid_unions.py --write

$0 API. Light compute; run beside the scoring artefacts.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_analysis import (  # noqa: E402
    CELL_LABEL,
    CELL_ORDER,
    CRS,
    assign_primary_tiles,
    load_cell_passes,
)
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402

SCORING_DIR = PROJECT_ROOT / "outputs/grid-2026-08-18/scoring"
OUT_DIR = PROJECT_ROOT / "outputs/grid-2026-08-18/verifier"
K = 10
CORROBORATION = 1

#: The documented union counts (results/grid-2026-08-18/findings.md,
#: verifier-costing table). The PI's stop rule: reproduce EXACTLY or halt.
EXPECTED = {
    "g512_ov064": 1402,
    "g512_ov256": 2585,
    "g384_ov048": 1827,
    "g384_ov192": 3319,
}


def union_with_votes(
    passes: list[list[dict]], bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Cluster a K-pass pool at c = 1 and tile-filter, carrying votes.

    Replicates the sweep's candidate construction (``cluster_votes`` then
    ``as_gdf``'s carrier-tile drop) with ``vote_count`` retained per
    surviving cluster.

    Args:
        passes: Deduplicated detections per pass (the loader's shape).
        bounds: Carrier tile bounds with a ``tile_name`` column.

    Returns:
        GeoDataFrame in the project CRS with ``vote_count`` and
        ``source_tile`` columns; off-carrier clusters dropped.
    """
    centroids, votes = cluster_votes(passes, CORROBORATION)
    if len(centroids) == 0:
        return gpd.GeoDataFrame(
            {"vote_count": [], "source_tile": []}, geometry=[], crs=CRS)
    gdf = gpd.GeoDataFrame(
        {"vote_count": votes},
        geometry=[Point(xy) for xy in centroids], crs=CRS)
    gdf["source_tile"] = assign_primary_tiles(gdf, bounds)
    return gdf[gdf["source_tile"].notna()].copy()


def main() -> int:
    """Materialise all four unions under the exact-count gate."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scoring-dir", type=Path, default=SCORING_DIR)
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--write", action="store_true",
                    help="Write the union GeoJSONs after every gate passes.")
    args = ap.parse_args()

    bounds = gpd.read_file(
        args.scoring_dir / "bounds" / "grid_common_bounds.geojson")

    results: dict[str, gpd.GeoDataFrame] = {}
    failures = []
    for cell in CELL_ORDER:
        passes = load_cell_passes(args.scoring_dir, cell)[:K]
        if len(passes) != K:
            failures.append(f"{cell}: {len(passes)} passes, expected {K}")
            continue
        gdf = union_with_votes(passes, bounds)
        ok = len(gdf) == EXPECTED[cell]
        print(f"{CELL_LABEL[cell]:14s} union n={len(gdf):5d} "
              f"expected={EXPECTED[cell]:5d} {'OK' if ok else 'MISMATCH'}")
        if not ok:
            failures.append(f"{cell}: {len(gdf)} != {EXPECTED[cell]}")
        results[cell] = gdf

    if failures:
        print("GATE FAIL — refusing to write (the PI's stop rule):")
        for f in failures:
            print("  ", f)
        return 1

    total = sum(len(g) for g in results.values())
    print(f"total candidates: {total} (documented 9,133)")
    if not args.write:
        print("dry run — pass --write to materialise")
        return 0
    for cell, gdf in results.items():
        dest = args.out_dir / cell / "union_k10.geojson"
        dest.parent.mkdir(parents=True, exist_ok=True)
        gdf.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
        print(f"wrote {dest.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
