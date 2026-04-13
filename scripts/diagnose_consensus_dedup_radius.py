#!/usr/bin/env python3
# ============================================================================
# diagnose_consensus_dedup_radius.py
# ----------------------------------------------------------------------------
# One-off diagnostic for Obs 228: measure how often the upstream consensus
# pipeline produces multiple final candidates for a single physical mound.
#
# Context
# -------
# The cartographic constraint is that Soviet burial mound symbols are ~75 m
# in diameter and do not overlap on the map. Therefore any two centroids
# within ~75 m of each other must correspond to the same physical mound.
#
# The upstream consensus pipeline currently dedups at DISTANCE_THRESHOLD_METRES
# = 20.0 m (lib_consensus.py). Candidates >20 m and <75 m apart centroid-to-
# centroid are therefore split into distinct cluster IDs despite representing
# the same physical feature.
#
# This script quantifies the impact on the H10/H12 test set.
#
# Method
# ------
# 1. Load the 327 test tile polygons.
# 2. Filter mounds-reference.geojson to GT mounds whose centroid lies inside
#    at least one test tile polygon.
# 3. For each of the 5 H10 pool configs, load its final candidates.
# 4. For each GT mound, count how many candidates from each pool have
#    centroids within R metres, for R in {20, 40, 60, 75}.
# 5. Report:
#      * Fraction of GT mounds with ANY matching candidate (recall proxy)
#      * Fraction of GT mounds with >=2 matching candidates (dedup failures)
#      * Distribution of per-mound match counts
#      * Pairwise centroid separations for the >=2 cases (should be >20 and
#        <=75 if the failure story is correct)
# ============================================================================

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import MultiPoint, Point

H10 = Path("outputs/h10")
CONFIGS = [
    "pool_160_hp4hn4",
    "pool_160_hp2hn6",
    "pool_160_hp6hn2",
    "pool_160_hp8hn8",
    "pool_160_hp16hn16",
]
RADII_M = [20.0, 40.0, 60.0, 75.0]
TARGET_CRS = "EPSG:32635"


def load_gt_on_test_tiles() -> gpd.GeoDataFrame:
    """Return GT mound centroids falling inside any of the 327 test tiles."""
    bounds = gpd.read_file(
        "inputs/calibration/h10-384/test_bounds.geojson"
    ).to_crs(TARGET_CRS)
    gt = gpd.read_file(
        "inputs/vectors/references/mounds-reference.geojson"
    ).to_crs(TARGET_CRS)

    # mounds-reference uses MULTIPOINT geometry; explode to single points.
    def to_point(geom):
        if isinstance(geom, MultiPoint):
            return list(geom.geoms)[0]
        return geom

    gt = gt.copy()
    gt["geometry"] = gt.geometry.apply(to_point)
    gt["gt_idx"] = np.arange(len(gt))

    # Spatial join (inner) — keep only GT within a test tile.
    within = gpd.sjoin(
        gt[["gt_idx", "geometry"]],
        bounds[["tile_name", "geometry"]],
        how="inner",
        predicate="within",
    )
    # A GT mound may intersect multiple overlapping tiles; keep one row per
    # original GT fid.
    within = within.drop_duplicates(subset=["gt_idx"])
    return within[["geometry"]].reset_index(drop=True)


def load_pool_candidates(config: str) -> pd.DataFrame:
    """Return a DataFrame with one row per final candidate for a pool config."""
    manifest = json.loads(
        (H10 / "verifier-crops" / config / "candidate_manifest.json").read_text()
    )
    rows = []
    for entry in manifest["candidates"]:
        rows.append({
            "config": config,
            "candidate_id": entry["candidate_id"],
            "x": float(entry["centroid_x"]),
            "y": float(entry["centroid_y"]),
            "vote_count": int(entry["properties"].get("vote_count", 0)),
            "cluster_size": int(entry["properties"].get("cluster_size", 0)),
            "source_tiles": tuple(
                sorted(entry["properties"].get("source_tiles") or [])
            ),
        })
    return pd.DataFrame(rows)


def per_config_diagnostic(
    gt: gpd.GeoDataFrame,
    candidates: pd.DataFrame,
) -> dict:
    """For one pool config, compute match counts at each radius."""
    gt_coords = np.array([(p.x, p.y) for p in gt.geometry])
    cand_coords = candidates[["x", "y"]].to_numpy()
    if len(cand_coords) == 0:
        return {"n_gt": len(gt_coords), "n_candidates": 0}

    tree = cKDTree(cand_coords)

    per_radius: dict[float, dict] = {}
    separations: dict[float, list[float]] = {}
    for r in RADII_M:
        matches_per_gt = tree.query_ball_point(gt_coords, r)
        counts = [len(m) for m in matches_per_gt]
        c = Counter(counts)
        n_gt = len(counts)
        n_any = sum(1 for k in counts if k >= 1)
        n_multi = sum(1 for k in counts if k >= 2)

        # Pairwise centroid separations for GT mounds with >=2 matches.
        seps: list[float] = []
        for idxs in matches_per_gt:
            if len(idxs) < 2:
                continue
            pts = cand_coords[idxs]
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    d = float(np.hypot(pts[i, 0] - pts[j, 0],
                                       pts[i, 1] - pts[j, 1]))
                    seps.append(d)
        separations[r] = seps

        per_radius[r] = {
            "n_gt": n_gt,
            "n_any_match": n_any,
            "n_multi_match": n_multi,
            "fraction_any": n_any / n_gt if n_gt else 0.0,
            "fraction_multi": n_multi / n_gt if n_gt else 0.0,
            "match_count_histogram": dict(sorted(c.items())),
            "n_pairs_in_multi_clusters": len(seps),
            "sep_min": float(np.min(seps)) if seps else None,
            "sep_p50": float(np.percentile(seps, 50)) if seps else None,
            "sep_p90": float(np.percentile(seps, 90)) if seps else None,
            "sep_max": float(np.max(seps)) if seps else None,
        }

    return {
        "n_gt": len(gt_coords),
        "n_candidates": len(cand_coords),
        "per_radius": per_radius,
    }


def main() -> None:
    gt = load_gt_on_test_tiles()
    print(f"GT mounds on 327 test tiles: {len(gt)}")

    results: dict[str, dict] = {}
    for cfg in CONFIGS:
        cands = load_pool_candidates(cfg)
        diag = per_config_diagnostic(gt, cands)
        results[cfg] = diag
        pr = diag["per_radius"]
        print(f"\n{cfg}  (n_candidates={diag['n_candidates']})")
        print(
            f"  r=20m: any={pr[20.0]['fraction_any']:.3f}  "
            f"multi={pr[20.0]['fraction_multi']:.3f}  "
            f"(n_multi={pr[20.0]['n_multi_match']})"
        )
        print(
            f"  r=40m: any={pr[40.0]['fraction_any']:.3f}  "
            f"multi={pr[40.0]['fraction_multi']:.3f}  "
            f"(n_multi={pr[40.0]['n_multi_match']})"
        )
        print(
            f"  r=60m: any={pr[60.0]['fraction_any']:.3f}  "
            f"multi={pr[60.0]['fraction_multi']:.3f}  "
            f"(n_multi={pr[60.0]['n_multi_match']})"
        )
        print(
            f"  r=75m: any={pr[75.0]['fraction_any']:.3f}  "
            f"multi={pr[75.0]['fraction_multi']:.3f}  "
            f"(n_multi={pr[75.0]['n_multi_match']})"
        )
        # Separation statistics for the 75 m case — the most permissive view.
        s75 = pr[75.0]
        if s75["sep_min"] is not None:
            print(
                f"  pairs in multi (r=75m): n={s75['n_pairs_in_multi_clusters']}"
                f"  sep_min={s75['sep_min']:.1f}m"
                f"  p50={s75['sep_p50']:.1f}m"
                f"  p90={s75['sep_p90']:.1f}m"
                f"  sep_max={s75['sep_max']:.1f}m"
            )

    # Aggregate across configs at r=75m for a cross-config view.
    agg = {}
    for r in RADII_M:
        frac_multi = [results[c]["per_radius"][r]["fraction_multi"]
                      for c in CONFIGS]
        n_multi = [results[c]["per_radius"][r]["n_multi_match"] for c in CONFIGS]
        agg[r] = {
            "mean_fraction_multi": float(np.mean(frac_multi)),
            "min_fraction_multi": float(np.min(frac_multi)),
            "max_fraction_multi": float(np.max(frac_multi)),
            "mean_n_multi": float(np.mean(n_multi)),
        }

    print("\nCross-config aggregate (5 configs):")
    for r in RADII_M:
        a = agg[r]
        print(
            f"  r={int(r)}m: mean_multi_frac={a['mean_fraction_multi']:.3f}  "
            f"range=[{a['min_fraction_multi']:.3f}, "
            f"{a['max_fraction_multi']:.3f}]  "
            f"mean n_multi={a['mean_n_multi']:.1f}"
        )

    out = {
        "n_gt_on_test_tiles": len(gt),
        "configs": CONFIGS,
        "radii_m": RADII_M,
        "per_config": results,
        "aggregate": agg,
    }
    out_path = Path("results/h10/consensus_dedup_magnitude_diagnostic.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
