#!/usr/bin/env python3
"""
Gemini 3.7 55-map campaign N-ladder: first-N rungs for both arms.

Card § 5 step 4 (`planning/gemini37-55map-2026-08-29.md`): the
N ∈ {1, 3} ladder rungs for the 3.7 K=5 deployment cell, derived by
the preregistered first-N rule exactly as `stride55_ladder.py` derived
the Gemini-3 rungs — first-N deduped passes → c=1 clustering with
votes → standard-grid tile assignment → verifier-probability
inheritance by nearest committed K=5 candidate within 10 m — evaluated
under BOTH verifier arms (carried Gemini-3, `verify_arm1`; all-3.7,
`verify_arm2`) against the canonical adjudicated extended GT at 50 m.

Rung oracles are descriptive (screening-protocol sweep bests); the
committed carried points exist only at N = 5.

REPLICATION GATES (nothing is written unless all pass), mirroring the
stride55 ladder:

1. The first-5 rebuild reproduces the committed K=5 union: exact
   candidate count (12,715), identical votes, centroids within 0.2 m
   of the verifier manifest's.
2. The rebuilt N=5 rung at each arm's carried point equals that arm's
   committed primary @ 50 m to 1e-6.

Usage::

    python scripts/gemini37_arm_ladder.py

Zero API. Run on sapphire (pass dedup + ~150 sweep points x 55
Hungarian problems per arm).

Created: 2026-08-31 (Session 145)
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

from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    DEFAULT_CRS,
    build_extended_gt,
    build_phantom_gdf,
    compute_counts_at_r,
    compute_point_estimate,
)
from scripts.gemini37_sweep_oracle import (  # noqa: E402
    CELLS as CAMPAIGN_CELLS,
    committed_f1_at_50,
    load_candidates,
)
from scripts.grid_prepare_scoring import CoverageError, load_pass  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.merge_passes import deduplicate_within_pass  # noqa: E402
from scripts.stride55_ladder import (  # noqa: E402
    INHERIT_TOL_M,
    UNION_GATE_M,
)
from scripts.stride55_prepare_and_union import (  # noqa: E402
    DEDUP_METRES,
    resolve_pass_paths,
)
from scripts.stride55_score import (  # noqa: E402
    assign_standard_tile,
    build_map_constrained_index,
)
from scripts.stride55_sweep_oracle import (  # noqa: E402
    BOUNDS,
    BUFFER_R,
    CANONICAL_REVIEW,
    STUDENT_GT,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

CELL_DIR = PROJECT_ROOT / "outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37"
MANIFEST = PROJECT_ROOT / "inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json"
OUT_DIR = PROJECT_ROOT / "results/gemini37-55map-2026-08-31/ladder"
K_TOTAL = 5
NS = (1, 3)
ARMS = ("arm1", "arm2")


def load_deduped_passes() -> list[list[dict]]:
    """The five deduped 3.7 passes, coverage-gated as the union build."""
    manifest = set(json.loads(MANIFEST.read_text()))
    passes: list[list[dict]] = []
    for i in range(1, K_TOTAL + 1):
        run = f"run_{i}"
        raw, processed = load_pass(resolve_pass_paths(CELL_DIR, run))
        if processed != manifest:
            raise CoverageError(
                f"{run}: {len(processed)} tiles vs {len(manifest)} pinned")
        passes.append(deduplicate_within_pass(raw, distance_thresh=DEDUP_METRES))
    return passes


def cluster_first_n(passes: list[list[dict]], n: int,
                    index: dict) -> gpd.GeoDataFrame:
    """First-N clusters with votes and standard-grid tile assignment."""
    from shapely.geometry import Point

    subset = passes[:n]
    centroids, votes = cluster_votes(subset, 1)
    tiles_flat = [d["source_tiles"][0] for p in subset for d in p]
    pooled = np.asarray([d["centroid"] for p in subset for d in p], dtype=float)
    gdf = gpd.GeoDataFrame(
        {"vote_count": np.asarray(votes)},
        geometry=[Point(xy) for xy in centroids], crs=DEFAULT_CRS)
    _, idx = cKDTree(pooled).query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
    gdf["source_tile"] = [
        assign_standard_tile(index, tiles_flat[i], x, y)
        for i, x, y in zip(idx, gdf.geometry.x, gdf.geometry.y)]
    return gdf


def main() -> int:
    import pandas as pd

    student = gpd.read_file(STUDENT_GT).to_crs(DEFAULT_CRS)
    bounds = gpd.read_file(BOUNDS).to_crs(DEFAULT_CRS)
    empty_y = pd.DataFrame(columns=[
        "candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"])
    review_t = pd.read_csv(CANONICAL_REVIEW)
    phantoms = build_phantom_gdf(empty_y, review_t, BUFFER_R)
    ext_gt = build_extended_gt(student, phantoms)
    logger.info("extended GT at %dm: %d (student %d + phantoms %d, deduped)",
                BUFFER_R, len(ext_gt), len(student), len(phantoms))
    index = build_map_constrained_index()

    passes = load_deduped_passes()
    union_n = CAMPAIGN_CELLS["arm1"]["union_n"]
    k5 = load_candidates("arm1", CAMPAIGN_CELLS["arm1"])
    probs = {arm: load_candidates(arm, CAMPAIGN_CELLS[arm])
             ["mound_probability"].to_numpy() for arm in ARMS}
    tree = cKDTree(np.c_[k5.geometry.x, k5.geometry.y])

    # Gate 1: the first-5 rebuild reproduces the committed union.
    rebuilt = cluster_first_n(passes, K_TOTAL, index)
    if len(rebuilt) != union_n:
        raise RuntimeError(
            f"union gate FAILED — rebuilt {len(rebuilt)} vs "
            f"committed {union_n}")
    d5, i5 = tree.query(np.c_[rebuilt.geometry.x, rebuilt.geometry.y], k=1)
    votes_match = (rebuilt["vote_count"].to_numpy()
                   == k5["vote_count"].to_numpy()[i5])
    if d5.max() > UNION_GATE_M or not votes_match.all():
        raise RuntimeError(
            f"union gate FAILED — max centroid distance {d5.max():.6f} m, "
            f"vote mismatches {int((~votes_match).sum())}")
    logger.info("union gate OK (n=%d, max dist %.6f m)",
                len(rebuilt), d5.max())

    # Gate 2 per arm: rebuilt N=5 at the carried point vs committed.
    for arm in ARMS:
        spec = CAMPAIGN_CELLS[arm]
        rebuilt["mound_probability"] = probs[arm][i5]
        pt, pk = spec["carried"]
        sub = rebuilt[(rebuilt["mound_probability"] >= pt)
                      & (rebuilt["vote_count"] >= pk)]
        tp, fp, fn, _ = compute_counts_at_r(sub, ext_gt, bounds, BUFFER_R)
        f1_primary = compute_point_estimate(tp, fp, fn)[2]
        committed = committed_f1_at_50(spec["committed"])
        if abs(f1_primary - committed) > 1e-6:
            raise RuntimeError(
                f"{arm}: primary gate FAILED — ladder-path "
                f"{f1_primary:.6f} vs committed {committed:.6f}")
        logger.info("%s: primary gate OK (%.6f)", arm, f1_primary)

    payload: dict = {"buffer_m": BUFFER_R, "inherit_tol_m": INHERIT_TOL_M,
                     "cell": "g384_ov192_55map_g37", "arms": {}}
    rows_all: list[dict] = []
    for n in NS:
        gdf_base = cluster_first_n(passes, n, index)
        d, idx = tree.query(np.c_[gdf_base.geometry.x, gdf_base.geometry.y],
                            k=1)
        matched = d <= INHERIT_TOL_M
        n_total = int(len(gdf_base))
        n_unmatched = n_total - int(matched.sum())
        for arm in ARMS:
            gdf = gdf_base[matched].copy()
            gdf["mound_probability"] = probs[arm][idx[matched]]
            thresholds = sorted({0.0} | {round(float(v), 4)
                                         for v in gdf["mound_probability"]})
            rung_rows = []
            for prob_t in thresholds:
                for k in range(1, n + 1):
                    s = gdf[(gdf["mound_probability"] >= prob_t)
                            & (gdf["vote_count"] >= k)]
                    tp, fp, fn, _ = compute_counts_at_r(
                        s, ext_gt, bounds, BUFFER_R)
                    p, r, f1 = compute_point_estimate(tp, fp, fn)
                    rung_rows.append({
                        "arm": arm, "N": n, "prob_t": prob_t,
                        "min_votes": k, "n_detections": int(len(s)),
                        "tp": tp, "fp": fp, "fn": fn, "precision": p,
                        "recall": r, "corrected_f1": f1})
            rows_all.extend(rung_rows)
            best = max(rung_rows, key=lambda r: r["corrected_f1"])
            logger.info("%s N=%d: union %d (unmatched %d) | ORACLE %.4f "
                        "at (%.2f, k%d)", arm, n, n_total, n_unmatched,
                        best["corrected_f1"], best["prob_t"],
                        best["min_votes"])
            payload["arms"].setdefault(arm, {})[str(n)] = {
                "union_n": n_total, "unmatched": n_unmatched, "oracle": best}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / "ladder_sweep_50m.csv"
    with out_csv.open("w", newline="") as fh:
        w = csvmod.DictWriter(fh, fieldnames=list(rows_all[0].keys()))
        w.writeheader()
        w.writerows(rows_all)
    (OUT_DIR / "ladder.json").write_text(json.dumps(payload, indent=2) + "\n")
    logger.info("ARM LADDER COMPLETE -> %s", OUT_DIR.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
