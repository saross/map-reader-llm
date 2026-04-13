#!/usr/bin/env python3
# ============================================================================
# export_dedup_visual_check.py
# ----------------------------------------------------------------------------
# Export QGIS-ready GeoJSON layers for visual verification of the upstream
# consensus dedup issue (Obs 228).
#
# Writes three layers to outputs/qgis-dedup-check/:
#
#   qgis_dedup_gt_multi.geojson
#       The GT mounds that have >=2 final candidates within 75 m, one feature
#       per (config, GT_mound). Attributes: config, gt_idx, n_candidates.
#
#   qgis_dedup_candidates.geojson
#       The paired candidates themselves, one feature per (config, candidate).
#       Attributes: config, candidate_id, gt_idx, distance_to_gt_m,
#       vote_count, nearest_other_m.
#
#   qgis_dedup_buffers.geojson
#       75 m circular buffers around each multi-GT centroid, for visual
#       verification of the cartographic constraint. Attributes: config,
#       gt_idx, radius_m.
#
# All layers in EPSG:32635. Load alongside the raster tiles in inputs/rasters/
# for full visual context.
#
# Usage:
#
#     python scripts/export_dedup_visual_check.py
#     python scripts/export_dedup_visual_check.py --radius-m 60
#     python scripts/export_dedup_visual_check.py --configs pool_160_hp4hn4
# ============================================================================

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import MultiPoint, Point

TARGET_CRS = "EPSG:32635"
DEFAULT_CONFIGS = [
    "pool_160_hp4hn4",
    "pool_160_hp2hn6",
    "pool_160_hp6hn2",
    "pool_160_hp8hn8",
    "pool_160_hp16hn16",
]
DEFAULT_RADIUS_M = 75.0
H10 = Path("outputs/h10")
TEST_BOUNDS = Path("inputs/calibration/h10-384/test_bounds.geojson")
GT_PATH = Path("inputs/vectors/references/mounds-reference.geojson")
OUT_DIR = Path("outputs/qgis-dedup-check")


def load_gt_on_test_tiles() -> gpd.GeoDataFrame:
    """GT mounds with centroid inside any of the 327 test tile polygons."""
    bounds = gpd.read_file(TEST_BOUNDS).to_crs(TARGET_CRS)
    gt = gpd.read_file(GT_PATH).to_crs(TARGET_CRS)

    def to_point(geom):
        if isinstance(geom, MultiPoint):
            return list(geom.geoms)[0]
        return geom

    gt = gt.copy()
    gt["geometry"] = gt.geometry.apply(to_point)
    gt["gt_idx"] = np.arange(len(gt))

    within = gpd.sjoin(
        gt[["gt_idx", "geometry"]],
        bounds[["tile_name", "geometry"]],
        how="inner",
        predicate="within",
    ).drop_duplicates(subset=["gt_idx"])
    return within[["gt_idx", "geometry"]].reset_index(drop=True)


def load_config_candidates(config: str) -> pd.DataFrame:
    """One row per final candidate for a pool config."""
    manifest = json.loads(
        (H10 / "verifier-crops" / config / "candidate_manifest.json").read_text()
    )
    rows = []
    for entry in manifest["candidates"]:
        rows.append({
            "candidate_id": entry["candidate_id"],
            "x": float(entry["centroid_x"]),
            "y": float(entry["centroid_y"]),
            "vote_count": int(entry["properties"].get("vote_count", 0)),
            "cluster_size": int(entry["properties"].get("cluster_size", 0)),
            "source_tiles": ",".join(
                entry["properties"].get("source_tiles") or []
            ),
        })
    return pd.DataFrame(rows)


def collect_multi_gt_cases(
    gt: gpd.GeoDataFrame,
    candidates: pd.DataFrame,
    config: str,
    radius_m: float,
) -> tuple[list[dict], list[dict]]:
    """For one config, find GT mounds with >=2 candidates within radius_m.

    Returns (gt_rows, candidate_rows) as lists of dicts ready for
    GeoDataFrame construction.
    """
    gt_coords = np.array([(p.x, p.y) for p in gt.geometry])
    cand_coords = candidates[["x", "y"]].to_numpy()
    tree = cKDTree(cand_coords)

    gt_rows: list[dict] = []
    candidate_rows: list[dict] = []

    for gt_i, (gx, gy) in enumerate(gt_coords):
        idxs = tree.query_ball_point([gx, gy], radius_m)
        if len(idxs) < 2:
            continue

        gt_idx_val = int(gt.iloc[gt_i]["gt_idx"])
        gt_rows.append({
            "config": config,
            "gt_idx": gt_idx_val,
            "n_candidates": int(len(idxs)),
            "geometry": Point(gx, gy),
        })

        # For each paired candidate, record distance to this GT and distance
        # to its nearest other paired candidate (a proxy for the intra-pair
        # separation).
        paired = cand_coords[idxs]
        for local_i, cand_i in enumerate(idxs):
            dists_to_others = [
                float(np.hypot(paired[local_i, 0] - paired[j, 0],
                               paired[local_i, 1] - paired[j, 1]))
                for j in range(len(idxs)) if j != local_i
            ]
            nearest_other = min(dists_to_others) if dists_to_others else None
            cand_row = candidates.iloc[cand_i]
            candidate_rows.append({
                "config": config,
                "gt_idx": gt_idx_val,
                "candidate_id": int(cand_row["candidate_id"]),
                "vote_count": int(cand_row["vote_count"]),
                "cluster_size": int(cand_row["cluster_size"]),
                "source_tiles": cand_row["source_tiles"],
                "distance_to_gt_m": float(np.hypot(
                    cand_coords[cand_i, 0] - gx,
                    cand_coords[cand_i, 1] - gy,
                )),
                "nearest_other_m": nearest_other,
                "geometry": Point(cand_coords[cand_i, 0],
                                  cand_coords[cand_i, 1]),
            })
    return gt_rows, candidate_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radius-m", type=float, default=DEFAULT_RADIUS_M)
    parser.add_argument("--configs", nargs="+", default=DEFAULT_CONFIGS)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading GT mounds within the 327 test tiles...")
    gt = load_gt_on_test_tiles()
    print(f"  {len(gt)} GT mounds on test tiles.")

    all_gt_rows: list[dict] = []
    all_candidate_rows: list[dict] = []
    summary: list[dict] = []

    for cfg in args.configs:
        print(f"\nProcessing {cfg}...")
        cands = load_config_candidates(cfg)
        gt_rows, cand_rows = collect_multi_gt_cases(
            gt, cands, cfg, args.radius_m
        )
        print(f"  multi-GT cases: {len(gt_rows)}")
        print(f"  paired candidates: {len(cand_rows)}")
        all_gt_rows.extend(gt_rows)
        all_candidate_rows.extend(cand_rows)
        summary.append({
            "config": cfg,
            "n_multi_gt": len(gt_rows),
            "n_paired_candidates": len(cand_rows),
        })

    # Build GeoDataFrames.
    gt_gdf = gpd.GeoDataFrame(all_gt_rows, crs=TARGET_CRS)
    cand_gdf = gpd.GeoDataFrame(all_candidate_rows, crs=TARGET_CRS)

    # 75 m buffer polygons around each multi-GT (one per config × gt_idx pair).
    buffer_gdf = gt_gdf.copy()
    buffer_gdf["geometry"] = buffer_gdf.geometry.buffer(args.radius_m)
    buffer_gdf["radius_m"] = args.radius_m

    gt_out = args.output_dir / "qgis_dedup_gt_multi.geojson"
    cand_out = args.output_dir / "qgis_dedup_candidates.geojson"
    buf_out = args.output_dir / "qgis_dedup_buffers.geojson"

    gt_gdf.to_file(gt_out, driver="GeoJSON")
    cand_gdf.to_file(cand_out, driver="GeoJSON")
    buffer_gdf.to_file(buf_out, driver="GeoJSON")

    print("\nWrote:")
    print(f"  {gt_out}  ({len(gt_gdf)} features)")
    print(f"  {cand_out}  ({len(cand_gdf)} features)")
    print(f"  {buf_out}  ({len(buffer_gdf)} features)")

    print("\nSummary:")
    for s in summary:
        print(f"  {s['config']}: {s['n_multi_gt']} multi-GT, "
              f"{s['n_paired_candidates']} paired candidates")


if __name__ == "__main__":
    main()
