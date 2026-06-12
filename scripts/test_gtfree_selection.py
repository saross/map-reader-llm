#!/usr/bin/env python3
# ============================================================================
# test_gtfree_selection.py
# ----------------------------------------------------------------------------
# Session 113 ($0): can a practitioner WITHOUT ground truth pick the best
# production run? (Shawn, 2026-06-13: GT-free diagnostics for real discovery
# runs would increase the contribution's value.)
#
# DESIGN — leave-one-family-out (LOFO) cross-config consensus:
# the eight 55-map board cells group into four config FAMILIES (T03, TH7,
# TM, IM) by proposer configuration. For each family F, a pseudo-GT is
# built from the OTHER three families' representative (k3) detection sets:
# union the three sets, single-linkage cluster at 50 m, keep clusters
# supported by >= 2 distinct families, centroid = pseudo-mound. Each cell
# is then scored (50 m, Hungarian per map — the board machinery) against
# its family's LOFO pseudo-GT, so no cell is evaluated against a reference
# containing its own family's detections.
#
# VALIDATION: because the canonical extended GT exists, the GT-free ranking
# can be checked against the true board ranking (Spearman + top-pick
# agreement). Sensitivity: vote >= 3 (all-other-families consensus).
#
# COST: $0 (on-disk). Run on zbook (8 cells x 8,541-tile Hungarian).
#
# Usage (zbook):  .venv/bin/python scripts/test_gtfree_selection.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-13 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402
from scripts.run_generalisation import tile_to_map  # noqa: E402

BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
BOARD = BASE_DIR / "results/55map-leaderboard/55map_leaderboard_50m.json"
RUN_CONDS = BASE_DIR / "results/run-conditions.json"
OUT_DIR = BASE_DIR / "results/gtfree-selection"
RADIUS_M = 50.0

# Board cell -> (run_id, label) as registered; family = proposer config.
CELLS = {
    "T03-k3 (oracle)": ("55maps-text-high-t0-3-generalisation",
                        "verified-k3-canonical-gt", "T03"),
    "T03-k4": ("55maps-text-high-t0-3-generalisation",
               "verified-k4-canonical-gt", "T03"),
    "TH7-k3": ("55maps-text-high-generalisation",
               "verified-k3-canonical-gt", "TH7"),
    "TH7-k4 (carry-forward)": ("55maps-text-high-generalisation",
                               "verified-k4-canonical-gt", "TH7"),
    "TM-k3": ("55maps-text-min-generalisation",
              "verified-k3-canonical-gt", "TM"),
    "TM-k4": ("55maps-text-min-generalisation",
              "verified-k4-canonical-gt", "TM"),
    "TM-n10-k5 (uplift)": ("55maps-text-min-n10-uplift",
                           "verified-5of10-canonical-gt", "TM"),
    "IM-k3": ("55maps-image-generalisation",
              "verified-k3-canonical-gt", "IM"),
}
# Family representatives used to BUILD pseudo-GT (the k3 cells).
FAMILY_REPS = {
    "T03": "T03-k3 (oracle)",
    "TH7": "TH7-k3",
    "TM": "TM-k3",
    "IM": "IM-k3",
}


def load_det(rel: str, gdf_bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Load a detection set, normalise CRS, attach source_map."""
    det = gpd.read_file(BASE_DIR / rel)
    crs = "EPSG:32635" if abs(det.geometry.x.iloc[0]) > 180 else "EPSG:4326"
    det = det.set_crs(crs, allow_override=True).to_crs("EPSG:32635")
    det = assign_source_tiles(det, gdf_bounds)
    det["source_map"] = [tile_to_map(t) for t in det["source_tile"]]
    return det


def consensus_pseudo_gt(sets: list[gpd.GeoDataFrame], min_sources: int,
                        ) -> gpd.GeoDataFrame:
    """Cluster the union of detection sets; keep multi-source clusters.

    Single-linkage at RADIUS_M via union-find over cKDTree pairs. A cluster
    becomes a pseudo-mound if it contains points from >= min_sources
    distinct input sets; its location is the member centroid and its
    source_map the first member's (members are within ~50 m, so map
    assignment is unambiguous away from sheet edges).
    """
    xs, ys, src, maps = [], [], [], []
    for i, g in enumerate(sets):
        xs.extend(g.geometry.x)
        ys.extend(g.geometry.y)
        src.extend([i] * len(g))
        maps.extend(g["source_map"])
    pts = np.column_stack([xs, ys])
    parent = list(range(len(pts)))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in cKDTree(pts).query_pairs(r=RADIUS_M):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    clusters: dict[int, list[int]] = {}
    for i in range(len(pts)):
        clusters.setdefault(find(i), []).append(i)

    keep_x, keep_y, keep_map = [], [], []
    for members in clusters.values():
        if len({src[m] for m in members}) >= min_sources:
            keep_x.append(float(np.mean([pts[m][0] for m in members])))
            keep_y.append(float(np.mean([pts[m][1] for m in members])))
            keep_map.append(maps[members[0]])
    return gpd.GeoDataFrame(
        {"geometry": [Point(x, y) for x, y in zip(keep_x, keep_y)],
         "source_map": keep_map}, crs="EPSG:32635")


def spearman(xs: list[float], ys: list[float]) -> float:
    """Spearman rank correlation (no ties expected at these precisions)."""
    def ranks(v: list[float]) -> list[float]:
        order = sorted(range(len(v)), key=lambda i: v[i])
        out = [0.0] * len(v)
        for rank, i in enumerate(order):
            out[i] = float(rank)
        return out
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = np.sqrt(sum((a - mx) ** 2 for a in rx)
                  * sum((b - my) ** 2 for b in ry))
    return float(num / den)


def main() -> int:
    """Build LOFO pseudo-GTs, score all cells, compare to the true board."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf_bounds = gpd.read_file(BOUNDS)
    if gdf_bounds.crs is None:
        gdf_bounds = gdf_bounds.set_crs("EPSG:4326")
    gdf_bounds = gdf_bounds.to_crs("EPSG:32635")

    dec = json.loads(RUN_CONDS.read_text())["decomposition"]
    board = {c["name"]: c for c in json.loads(BOARD.read_text())["cells"]}

    dets: dict[str, gpd.GeoDataFrame] = {}
    for name, (run_id, label, _fam) in CELLS.items():
        cond = next(c for c in dec[run_id]["conditions"] if c["label"] == label)
        dets[name] = load_det(cond["detections"], gdf_bounds)
        print(f"loaded {name}: {len(dets[name])} detections", flush=True)

    results = {}
    for vote in (2, 3):
        print(f"\n=== LOFO pseudo-GT, vote >= {vote} of 3 other families ===",
              flush=True)
        pseudo = {}
        for fam in FAMILY_REPS:
            reps = [dets[FAMILY_REPS[f]] for f in FAMILY_REPS if f != fam]
            pseudo[fam] = consensus_pseudo_gt(reps, vote)
            print(f"  pseudo-GT for family {fam} (from others): "
                  f"{len(pseudo[fam])} pseudo-mounds", flush=True)

        rows = []
        for name, (_r, _l, fam) in CELLS.items():
            res = score_detection_set(dets[name], pseudo[fam], gdf_bounds,
                                      buffer_metres=RADIUS_M, compute_mcc=False)
            rows.append({"cell": name, "family": fam,
                         "pseudo_f1": round(res["f1"], 4),
                         "pseudo_precision": round(res["precision"], 4),
                         "pseudo_recall": round(res["recall"], 4),
                         "true_f1": board[name]["f1_50"]})
            print(f"  {name:<24} pseudo-F1={res['f1']:.4f}  "
                  f"true F1={board[name]['f1_50']:.4f}", flush=True)

        rho = spearman([r["pseudo_f1"] for r in rows],
                       [r["true_f1"] for r in rows])
        text_rows = [r for r in rows if r["family"] != "IM"]
        rho_text = spearman([r["pseudo_f1"] for r in text_rows],
                            [r["true_f1"] for r in text_rows])
        top_pseudo = max(rows, key=lambda r: r["pseudo_f1"])["cell"]
        top_true = max(rows, key=lambda r: r["true_f1"])["cell"]
        print(f"  Spearman(pseudo, true) = {rho:+.3f} (all 8) / "
              f"{rho_text:+.3f} (7 text cells)", flush=True)
        print(f"  top pick: pseudo={top_pseudo} | true={top_true} | "
              f"agree={top_pseudo == top_true}", flush=True)
        results[f"vote{vote}"] = {
            "pseudo_gt_sizes": {f: len(pseudo[f]) for f in pseudo},
            "cells": rows, "spearman_all8": round(rho, 4),
            "spearman_text7": round(rho_text, 4),
            "top_pick_pseudo": top_pseudo, "top_pick_true": top_true,
        }

    out = OUT_DIR / "gtfree_selection.json"
    out.write_text(json.dumps({
        "design": ("leave-one-family-out cross-config consensus pseudo-GT; "
                   "single-linkage clustering at 50 m; families T03/TH7/TM/IM "
                   "with k3 representatives; scored vs the canonical-GT board "
                   "(results/55map-leaderboard/55map_leaderboard_50m.json)"),
        "radius_m": RADIUS_M, **results}, indent=2) + "\n")
    print(f"\nWrote {out.relative_to(BASE_DIR)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
