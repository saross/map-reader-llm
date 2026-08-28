#!/usr/bin/env python3
"""
Image-on-B GS cell: sweep, ladder, and the text-vs-image head-to-head.

The card's measurement contract (`planning/image-b-gs-2026-08-28.md`
§ 3): scores the image cell with the committed GS stride machinery on
the common footprint, derives its verified best point from the full
(prob_t × k) sweep at the GS-primary 20 m buffer, builds the free
first-N ladder (N ∈ {1, 3, 5}, inherited K = 10 verification), and
answers IP1–IP5 against the committed text-B anchor
(`results/grid-2026-08-18/conditions-verified/g384_ov192`,
F1@20 0.8961 registered).

GATES (nothing written unless all pass):

1. Join gates on the image union ↔ probabilities (count + contiguous
   keys) and the carrier reassignment gate — the stride instruments.
2. Anchor gate: the text-B registered detections re-scored through
   THIS script's path must reproduce the registered F1@20 (0.8961)
   within 0.0005 (the board showed mechanism identity at this cell).

Instruments: per-tile counts + round-robin tile-swap permutation
(10,000, seed 42) for text-vs-image and the saturation tests — the
board chain.

Usage::

    python scripts/image_b_analysis.py

Zero API. Run on sapphire.

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import csv as csvmod
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.grid_analysis import CRS, load_cell_passes, score  # noqa: E402
from scripts.grid_verifier_analysis import (  # noqa: E402
    JoinGateError,
    per_tile_counts,
    verified_subset,
)
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    permutation_test_float,
)
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402
from scripts.stride_verifier_analysis import (  # noqa: E402
    COMMON_BOUNDS,
    GROUND_TRUTH,
    reassign_gate,
    score_at,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

CELL = "g384_ov192_image"
VROOT = PROJECT_ROOT / "outputs/image-b-gs-2026-08-28/verifier" / CELL
SCORING = PROJECT_ROOT / "outputs/image-b-gs-2026-08-28/scoring"
ANCHOR_DIR = (PROJECT_ROOT
              / "results/grid-2026-08-18/conditions-verified/g384_ov192")
ANCHOR_F1_20 = 0.8961  # registered text-B verified best (eval committed)
OUT = PROJECT_ROOT / "results/image-b-gs-2026-08-28"
BUFFER_PRIMARY = 20
CURVE_BUFFERS = (20, 30, 50, 75)
INHERIT_TOL_M = 10.0
N_PERMS = 10_000
SEED = 42


def load_image_union() -> gpd.GeoDataFrame:
    """The image union joined to its probabilities, join-gated."""
    gdf = gpd.read_file(VROOT / "union_k10.geojson").to_crs(CRS)
    results = json.loads(
        (VROOT / "verify/probabilities.json").read_text())["results"]
    if len(results) != len(gdf):
        raise JoinGateError(
            f"{CELL}: {len(results)} probabilities vs {len(gdf)} features")
    if set(results) != {f"candidate_{i:05d}" for i in range(len(gdf))}:
        raise JoinGateError(f"{CELL}: probability keys not contiguous")
    gdf["mound_probability"] = [
        float(results[f"candidate_{i:05d}"]["mound_probability"])
        for i in range(len(gdf))]
    return gdf


def sweep(gdf: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
          bounds: gpd.GeoDataFrame, ks: range) -> list[dict]:
    rows = []
    thresholds = sorted({0.0} | {round(float(v), 4)
                                 for v in gdf["mound_probability"]})
    for prob_t in thresholds:
        for k in ks:
            sub = verified_subset(gdf, prob_t, k)
            row = score(sub, gdf_ref, bounds)
            row.update({"prob_t": prob_t, "min_votes": k,
                        "n_detections": int(len(sub))})
            rows.append(row)
    return rows


def main() -> int:
    bounds = gpd.read_file(COMMON_BOUNDS)
    gdf_ref = gpd.read_file(GROUND_TRUTH).to_crs(CRS)

    # ---- Image union, gated. ----
    union = load_image_union()
    union = reassign_gate(union, bounds, CELL)
    logger.info("%s: union %d joined and reassignment-gated", CELL,
                len(union))

    # ---- Anchor gate: text-B registered set through this path. ----
    anchor = gpd.read_file(ANCHOR_DIR / "detections.geojson").to_crs(CRS)
    anchor["source_tile"] = assign_primary_tiles(anchor, bounds)
    a20 = score(anchor, gdf_ref, bounds)
    if abs(a20["f1"] - ANCHOR_F1_20) > 0.0005:
        raise JoinGateError(
            f"anchor gate FAILED: {a20['f1']:.4f} vs registered "
            f"{ANCHOR_F1_20}")
    logger.info("anchor gate OK: text-B rescored %.4f (registered %.4f)",
                a20["f1"], ANCHOR_F1_20)

    OUT.mkdir(parents=True, exist_ok=True)

    # ---- The image sweep at 20 m; best point. ----
    rows = sweep(union, gdf_ref, bounds, range(1, 11))
    with (OUT / "sweep_20m.csv").open("w", newline="") as fh:
        w = csvmod.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    best = max(rows, key=lambda r: r["f1"])
    logger.info("IMAGE best @20m: F1=%.4f at (%.2f, k%d) P=%.4f R=%.4f",
                best["f1"], best["prob_t"], best["min_votes"],
                best["precision"], best["recall"])
    best_set = verified_subset(union, best["prob_t"], best["min_votes"])
    best_set.to_crs("EPSG:4326").to_file(
        OUT / "verified_best_20m.geojson", driver="GeoJSON")

    # ---- Buffer curves (IP1 / IP2). ----
    curves = {"image": {}, "text": {}}
    for b in CURVE_BUFFERS:
        curves["image"][b] = score_at(best_set, gdf_ref, bounds, b)
        curves["text"][b] = score_at(anchor, gdf_ref, bounds, b)
    for b in CURVE_BUFFERS:
        logger.info("buffer %3dm: text %.4f vs image %.4f (d %+.4f)", b,
                    curves["text"][b]["f1"], curves["image"][b]["f1"],
                    curves["text"][b]["f1"] - curves["image"][b]["f1"])

    # ---- Paired significance at 20 m (board instrument; the
    # per-tile counter scores at the grid BUFFER_M = 20). ----
    ta = per_tile_counts(anchor, bounds, gdf_ref)
    ti = per_tile_counts(best_set, bounds, gdf_ref)
    head = permutation_test_float(ta["tp"], ta["fp"], ta["fn"],
                                  ti["tp"], ti["fp"], ti["fn"],
                                  n_permutations=N_PERMS, seed=SEED)
    logger.info("text - image @20m: dF1=%+.4f p=%.4f",
                head["observed_diff"], head["p_value"])

    # ---- First-N ladder (IP5). ----
    passes = load_cell_passes(SCORING, CELL)
    tree = cKDTree(np.c_[union.geometry.x, union.geometry.y])
    probs10 = union["mound_probability"].to_numpy()
    ladder: dict = {}
    rung_sets: dict = {}
    for n in (1, 3, 5):
        centroids, votes = cluster_votes(passes[:n], 1)
        gdf = gpd.GeoDataFrame(
            {"vote_count": np.asarray(votes)},
            geometry=gpd.points_from_xy([c[0] for c in centroids],
                                        [c[1] for c in centroids]),
            crs=CRS)
        gdf["source_tile"] = assign_primary_tiles(gdf, bounds)
        d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
        gdf["mound_probability"] = probs10[idx]
        matched = d <= INHERIT_TOL_M
        gdf = gdf[matched].copy()
        rrows = sweep(gdf, gdf_ref, bounds, range(1, n + 1))
        rbest = max(rrows, key=lambda r: r["f1"])
        rung_sets[n] = verified_subset(gdf, rbest["prob_t"],
                                       rbest["min_votes"])
        ladder[n] = {"union_n": int(len(gdf)) + int((~matched).sum()),
                     "unmatched": int((~matched).sum()),
                     "best": rbest}
        logger.info("ladder N=%d: best F1=%.4f at (%.2f, k%d) union %d",
                    n, rbest["f1"], rbest["prob_t"], rbest["min_votes"],
                    ladder[n]["union_n"])
    t5 = per_tile_counts(rung_sets[5], bounds, gdf_ref)
    sat = permutation_test_float(t5["tp"], t5["fp"], t5["fn"],
                                 ti["tp"], ti["fp"], ti["fn"],
                                 n_permutations=N_PERMS, seed=SEED)
    logger.info("image N5 - N10 @20m: dF1=%+.4f p=%.4f",
                sat["observed_diff"], sat["p_value"])

    payload = {
        "cell": CELL, "buffer_primary_m": BUFFER_PRIMARY,
        "image_best": best,
        "anchor": {"f1_20": a20["f1"], "registered": ANCHOR_F1_20,
                   "n": int(len(anchor))},
        "buffer_curves": curves,
        "head_to_head_20m": head,
        "ladder": ladder,
        "saturation_N5_vs_N10": sat,
    }
    (OUT / "analysis.json").write_text(
        json.dumps(payload, indent=2, default=float) + "\n")
    logger.info("IMAGE-B ANALYSIS COMPLETE -> %s",
                (OUT / "analysis.json").relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
