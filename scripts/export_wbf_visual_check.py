#!/usr/bin/env python3
# ============================================================================
# export_wbf_visual_check.py
# ----------------------------------------------------------------------------
# Export QGIS-ready GeoJSON layers for visual verification of WBF output.
#
# Produces one layer per named variant, plus a GT layer, all in EPSG:32635.
# Each variant layer is a point-per-candidate file with attributes:
#     variant, candidate_id, vote_count, cluster_size, distance_to_gt_m,
#     near_gt (bool), source_tile
# Candidates with vote_count < 2 are excluded because the downstream
# pipeline filters them.
#
# Usage (compares the greedy baseline + two WBF variants):
#
#     python scripts/export_wbf_visual_check.py
# ============================================================================

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import MultiPoint, Point

TARGET_CRS = "EPSG:32635"
OUT_DIR = Path("outputs/qgis-wbf-check")

VARIANTS = [
    {
        "name": "greedy_baseline",
        "label": "Greedy 20m (current baseline)",
        "manifest": "outputs/h10/verifier-crops/pool_160_hp4hn4/candidate_manifest.json",
    },
    {
        "name": "wbf_no_minsep",
        "label": "WBF, no min-separation (Option A)",
        "manifest": "outputs/h10/wbf/pool_160_hp4hn4_no_minsep/wbf_candidates.json",
    },
    {
        "name": "wbf_voteaware_v6",
        "label": "WBF + vote-aware min-separation anchor >= 6 @ 60m (Option B)",
        "manifest": "outputs/h10/wbf/pool_160_hp4hn4_voteaware_v6/wbf_candidates.json",
    },
    {
        "name": "wbf_variant_c",
        "label": "WBF + vote-aware min-separation anchor >= 6 @ 30m (Option C)",
        "manifest": "outputs/h10/wbf/pool_160_hp4hn4_variant_c/wbf_candidates.json",
    },
]


def load_gt_on_test_tiles() -> np.ndarray:
    """GT mound centroids within the 327 test tiles."""
    bounds = gpd.read_file(
        "inputs/calibration/h10-384/test_bounds.geojson"
    ).to_crs(TARGET_CRS)
    gt = gpd.read_file(
        "inputs/vectors/references/mounds-reference.geojson"
    ).to_crs(TARGET_CRS)

    def to_point(geom):
        return list(geom.geoms)[0] if isinstance(geom, MultiPoint) else geom

    gt = gt.copy()
    gt["geometry"] = gt.geometry.apply(to_point)
    gt["gt_idx"] = np.arange(len(gt))
    within = gpd.sjoin(
        gt[["gt_idx", "geometry"]],
        bounds[["tile_name", "geometry"]],
        how="inner",
        predicate="within",
    ).drop_duplicates(subset=["gt_idx"]).reset_index(drop=True)
    return np.array([(p.x, p.y) for p in within.geometry])


def load_candidates(path: Path) -> list[dict]:
    """Load a manifest-format JSON into a flat list of candidate dicts."""
    d = json.loads(Path(path).read_text())
    out = []
    for c in d["candidates"]:
        props = c.get("properties", {})
        out.append({
            "candidate_id": c.get("candidate_id"),
            "x": float(c["centroid_x"]),
            "y": float(c["centroid_y"]),
            "vote_count": int(props.get("vote_count", 0)),
            "cluster_size": int(props.get("cluster_size", 0)),
            "source_tile": c.get("source_tile", ""),
        })
    return out


def export_variant(
    variant: dict,
    gt_coords: np.ndarray,
    out_dir: Path,
) -> dict:
    """Export one variant's candidates as a point GeoJSON with metadata."""
    cands = load_candidates(Path(variant["manifest"]))
    # Filter to vote >= 2 (matches the downstream pipeline's minimum)
    cands = [c for c in cands if c["vote_count"] >= 2]
    if not cands:
        return {"variant": variant["name"], "n_candidates": 0}

    coords = np.array([[c["x"], c["y"]] for c in cands])
    gt_tree = cKDTree(gt_coords)
    distances, _ = gt_tree.query(coords, k=1)

    records = []
    for i, c in enumerate(cands):
        records.append({
            "variant": variant["name"],
            "candidate_id": c["candidate_id"],
            "vote_count": c["vote_count"],
            "cluster_size": c["cluster_size"],
            "source_tile": c["source_tile"],
            "distance_to_gt_m": float(distances[i]),
            "near_gt": bool(distances[i] <= 75.0),
            "geometry": Point(c["x"], c["y"]),
        })

    gdf = gpd.GeoDataFrame(records, crs=TARGET_CRS)
    out_path = out_dir / f"wbf_check_{variant['name']}.geojson"
    gdf.to_file(out_path, driver="GeoJSON")

    n_near = int(gdf["near_gt"].sum())
    n_far = len(gdf) - n_near
    return {
        "variant": variant["name"],
        "label": variant["label"],
        "n_candidates": len(gdf),
        "n_near_gt": n_near,
        "n_far_gt": n_far,
        "precision_proxy": n_near / len(gdf) if len(gdf) else 0.0,
        "out_path": str(out_path),
    }


def export_gt(gt_coords: np.ndarray, out_dir: Path) -> Path:
    """Export the test-set GT mounds with 75 m buffer rings."""
    records = []
    for i, (x, y) in enumerate(gt_coords):
        records.append({
            "gt_idx": i,
            "geometry": Point(x, y),
        })
    gdf = gpd.GeoDataFrame(records, crs=TARGET_CRS)
    out_path = out_dir / "wbf_check_gt_points.geojson"
    gdf.to_file(out_path, driver="GeoJSON")

    buf_gdf = gdf.copy()
    buf_gdf["geometry"] = buf_gdf.geometry.buffer(75.0)
    buf_gdf["radius_m"] = 75.0
    buf_path = out_dir / "wbf_check_gt_buffers_75m.geojson"
    buf_gdf.to_file(buf_path, driver="GeoJSON")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading GT mounds on 327 test tiles...")
    gt_coords = load_gt_on_test_tiles()
    print(f"  {len(gt_coords)} GT mounds")

    print("\nExporting GT point and buffer layers...")
    export_gt(gt_coords, args.output_dir)

    print("\nExporting variant layers...")
    summaries = []
    for variant in VARIANTS:
        s = export_variant(variant, gt_coords, args.output_dir)
        summaries.append(s)
        print(f"  {s['variant']:<22} n={s['n_candidates']:<5}  "
              f"near_gt={s['n_near_gt']:<5}  far_gt={s['n_far_gt']:<5}  "
              f"P_proxy={s['precision_proxy']:.3f}")

    summary_path = args.output_dir / "wbf_check_summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2))
    print(f"\nWrote summary: {summary_path}")
    print(f"\nAll layers in {args.output_dir}")
    print("Load in QGIS alongside inputs/rasters/*.tif to inspect.")


if __name__ == "__main__":
    main()
