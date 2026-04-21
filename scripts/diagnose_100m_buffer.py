#!/usr/bin/env python3
"""
Diagnostics for the 100 m buffer F1 analysis on the 55-map image-generalisation
human-reviewed-corrected set.

Two diagnostics:

1. **GT-clustering**: per-map GT-to-GT distance distribution. For each GT
   mound (student GT + reviewer-promoted phantoms), count other GT within
   50 m and 100 m on the same map. Answers: "how often does the 100 m buffer
   enclose more than one GT mound?"

2. **Pair-drift**: run the Hungarian matcher (identical to the paper
   pipeline) at 50 m and 100 m on the same detection/GT inputs. For
   detections matched at both buffers, check whether the matched GT partner
   changes. Answers: "does widening the buffer silently swap pair
   identities?"

Output directory: results/55maps-image-generalisation/buffer-100m-diagnostics/

Inputs:

- outputs/55maps-image-generalisation/verified/verified_detections.geojson
  (4,665 verified detections, CRS EPSG:32635)
- inputs/vectors/references/student-mounds-55maps-reviewed.geojson
  (4,744 student-digitised GT, reviewed for duplicates, CRS EPSG:32635)
- results/55maps-image-generalisation/human-review.csv
  (1,028 VLM-only candidates reviewed 2026-04-20; 472 promoted to 'mound'
  become reviewer-phantom GT, 556 confirmed 'not_mound' are discarded)

Matching is done per-map to avoid cross-map pairings. Both diagnostics are
deterministic given the inputs and do not sample.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from shapely.geometry import Point

# Canonical input paths (relative to repo root).
DET_PATH = Path(
    "outputs/55maps-image-generalisation/verified/verified_detections.geojson"
)
STUDENT_GT_PATH = Path(
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
)
REVIEW_PATH = Path("results/55maps-image-generalisation/human-review.csv")
OUT_DIR = Path("results/55maps-image-generalisation/buffer-100m-diagnostics")

# Project CRS: Bulgarian UTM Zone 35N (metres).
CRS = "EPSG:32635"

# Non-greedy regex: captures map_name before the `_x<digits>_y<digits>` tile
# coordinate suffix (handles map names like `K-35-053-4_Boyadzhik`).
TILE_RE = re.compile(r"^(.+?)_x\d+_y\d+")


def extract_map_name(source_tile: str) -> str | None:
    """Return the map_name prefix of a `<map>_x<int>_y<int>.png` source tile."""
    m = TILE_RE.match(str(source_tile))
    return m.group(1) if m else None


def hungarian_match(
    det_xy: list[tuple[float, float]],
    ref_xy: list[tuple[float, float]],
    max_distance: float,
) -> list[tuple[int, int, float]]:
    """
    Replicate the paper pipeline's Hungarian matcher for a single map.

    Returns a list of (det_index, ref_index, distance_metres) for pairs with
    distance ≤ max_distance, using scipy's globally-optimal assignment solver.

    This is a light re-implementation of
    `scripts/lib_advanced_metrics.py::match_detections_to_references`, kept
    local to avoid coupling the diagnostic to the full lib imports.
    """
    n_det, n_ref = len(det_xy), len(ref_xy)
    if n_det == 0 or n_ref == 0:
        return []
    inf_cost = max_distance * 1000.0
    cost = np.full((n_det, n_ref), inf_cost, dtype=float)
    det_arr = np.asarray(det_xy, dtype=float)
    ref_arr = np.asarray(ref_xy, dtype=float)
    # Pairwise Euclidean distance (small inputs per map).
    dx = det_arr[:, 0:1] - ref_arr[:, 0:1].T
    dy = det_arr[:, 1:2] - ref_arr[:, 1:2].T
    dist = np.sqrt(dx * dx + dy * dy)
    feasible = dist <= max_distance
    cost[feasible] = dist[feasible]
    di, ri = linear_sum_assignment(cost)
    matches: list[tuple[int, int, float]] = []
    for d_idx, r_idx in zip(di, ri, strict=True):
        if cost[d_idx, r_idx] <= max_distance:
            matches.append((int(d_idx), int(r_idx), float(cost[d_idx, r_idx])))
    return matches


def load_inputs() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, int]:
    """
    Load detections and the extended GT (student + reviewer-promoted phantoms).

    Returns (detections, extended_gt, n_reviewer_phantoms).
    """
    det = gpd.read_file(DET_PATH)
    det["map_name"] = det["source_tile"].apply(extract_map_name)
    assert det["map_name"].notna().all(), "source_tile parse failed on at least one row"

    student_gt = gpd.read_file(STUDENT_GT_PATH)
    student_gt = student_gt.rename(columns={"source_map": "map_name"})
    student_slim = student_gt[["map_name", "geometry"]].copy()
    student_slim["source"] = "student"

    review = pd.read_csv(REVIEW_PATH)
    phantoms = review[review["human_label"] == "mound"][["map_name", "x", "y"]].copy()
    phantom_gdf = gpd.GeoDataFrame(
        phantoms,
        geometry=[Point(xy) for xy in zip(phantoms["x"], phantoms["y"], strict=True)],
        crs=CRS,
    )
    phantom_slim = phantom_gdf[["map_name", "geometry"]].copy()
    phantom_slim["source"] = "reviewer_phantom"

    extended = gpd.GeoDataFrame(
        pd.concat([student_slim, phantom_slim], ignore_index=True),
        crs=CRS,
    )
    return det, extended, len(phantom_slim)


def diagnostic_1_gt_clustering(extended_gt: gpd.GeoDataFrame) -> pd.DataFrame:
    """For each GT feature, count same-map neighbours within 50 m and 100 m."""
    records: list[dict] = []
    for map_name, grp in extended_gt.groupby("map_name"):
        xs = np.array([g.x for g in grp.geometry])
        ys = np.array([g.y for g in grp.geometry])
        n = len(xs)
        if n == 0:
            continue
        if n == 1:
            records.append(
                {
                    "map_name": map_name,
                    "source": grp["source"].iloc[0],
                    "n_neighbours_50m": 0,
                    "n_neighbours_100m": 0,
                }
            )
            continue
        dx = xs[:, None] - xs[None, :]
        dy = ys[:, None] - ys[None, :]
        dist = np.sqrt(dx * dx + dy * dy)
        np.fill_diagonal(dist, np.inf)
        for i, src in enumerate(grp["source"].to_numpy()):
            records.append(
                {
                    "map_name": map_name,
                    "source": src,
                    "n_neighbours_50m": int((dist[i] <= 50.0).sum()),
                    "n_neighbours_100m": int((dist[i] <= 100.0).sum()),
                }
            )
    return pd.DataFrame.from_records(records)


def diagnostic_2_pair_drift(
    det: gpd.GeoDataFrame, extended_gt: gpd.GeoDataFrame
) -> tuple[pd.DataFrame, dict]:
    """
    Run Hungarian matching at 50 m and 100 m per map, compare pair identities.

    Returns (drift_df, summary_dict). drift_df contains one row per detection
    matched at 100 m whose GT partner differs from its 50 m partner.
    """
    drift_rows: list[dict] = []
    summary = {
        "total_matched_at_50m": 0,
        "total_matched_at_100m": 0,
        "matched_at_both_buffers": 0,
        "same_gt_at_both": 0,
        "different_gt_at_both": 0,
        "new_matches_at_100m_only": 0,
        "matches_lost_at_100m": 0,
    }

    for map_name in sorted(det["map_name"].unique()):
        det_g = det[det["map_name"] == map_name]
        gt_g = extended_gt[extended_gt["map_name"] == map_name]
        if len(det_g) == 0 or len(gt_g) == 0:
            continue

        det_xy = [(g.x, g.y) for g in det_g.geometry]
        ref_xy = [(g.x, g.y) for g in gt_g.geometry]

        m50 = hungarian_match(det_xy, ref_xy, 50.0)
        m100 = hungarian_match(det_xy, ref_xy, 100.0)

        summary["total_matched_at_50m"] += len(m50)
        summary["total_matched_at_100m"] += len(m100)

        m50_by_det = {d: (r, dist) for d, r, dist in m50}
        m100_by_det = {d: (r, dist) for d, r, dist in m100}

        for d_idx, (r100, d100) in m100_by_det.items():
            if d_idx in m50_by_det:
                summary["matched_at_both_buffers"] += 1
                r50, d50 = m50_by_det[d_idx]
                if r50 == r100:
                    summary["same_gt_at_both"] += 1
                else:
                    summary["different_gt_at_both"] += 1
                    drift_rows.append(
                        {
                            "map_name": map_name,
                            "det_local_idx": d_idx,
                            "ref_idx_at_50": r50,
                            "ref_idx_at_100": r100,
                            "distance_at_50": round(d50, 2),
                            "distance_at_100": round(d100, 2),
                        }
                    )
            else:
                summary["new_matches_at_100m_only"] += 1

        for d_idx in m50_by_det:
            if d_idx not in m100_by_det:
                summary["matches_lost_at_100m"] += 1

    return pd.DataFrame.from_records(drift_rows), summary


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    det, extended_gt, n_phantoms = load_inputs()
    n_student = int((extended_gt["source"] == "student").sum())

    # --- Diagnostic 1 ---
    clust_df = diagnostic_1_gt_clustering(extended_gt)
    clust_df.to_csv(OUT_DIR / "gt_clustering.csv", index=False)

    d1 = {
        "n_gt_total": int(len(clust_df)),
        "n_gt_with_0_neighbours_100m": int((clust_df["n_neighbours_100m"] == 0).sum()),
        "n_gt_with_1_neighbour_100m": int((clust_df["n_neighbours_100m"] == 1).sum()),
        "n_gt_with_2plus_neighbours_100m": int(
            (clust_df["n_neighbours_100m"] >= 2).sum()
        ),
        "pct_gt_with_any_neighbour_100m": float(
            (clust_df["n_neighbours_100m"] >= 1).mean()
        ),
        "pct_gt_with_any_neighbour_50m": float(
            (clust_df["n_neighbours_50m"] >= 1).mean()
        ),
        "max_cluster_size_100m": int(clust_df["n_neighbours_100m"].max()),
        "mean_neighbours_100m": float(clust_df["n_neighbours_100m"].mean()),
        "median_neighbours_100m": float(clust_df["n_neighbours_100m"].median()),
    }

    # --- Diagnostic 2 ---
    drift_df, d2 = diagnostic_2_pair_drift(det, extended_gt)
    drift_df.to_csv(OUT_DIR / "pair_drift.csv", index=False)
    if d2["matched_at_both_buffers"] > 0:
        d2["pct_drift_of_both_matched"] = (
            d2["different_gt_at_both"] / d2["matched_at_both_buffers"]
        )
    if d2["total_matched_at_100m"] > 0:
        d2["pct_drift_of_100m_matches"] = (
            d2["different_gt_at_both"] / d2["total_matched_at_100m"]
        )

    summary = {
        "inputs": {
            "detections": str(DET_PATH),
            "student_gt": str(STUDENT_GT_PATH),
            "review_csv": str(REVIEW_PATH),
            "n_detections": int(len(det)),
            "n_student_gt": n_student,
            "n_reviewer_phantoms": int(n_phantoms),
            "n_extended_gt": int(len(extended_gt)),
            "n_maps": int(det["map_name"].nunique()),
        },
        "diagnostic_1_gt_clustering": d1,
        "diagnostic_2_pair_drift": d2,
    }

    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
