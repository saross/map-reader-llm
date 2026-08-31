#!/usr/bin/env python3
"""
Fourth grid cell N-ladder: first-N rungs under the 3.7 verifier.

The fourth cell of the proposer x verifier 2x2 (`planning/
gemini37-55map-2026-08-29.md` changelog 2026-08-31) is the Gemini-3
Run B K=10 union (57,482 candidates) re-verified with the
gemini-3.7-flash verifier (`verify_37`). This script derives its
N ∈ {1, 3, 5} first-N rungs exactly as `stride55_ladder.py` derived
the Gemini-3-verifier rungs — same union rebuild, same inheritance
rule (nearest K=10 candidate within 10 m) — with probabilities
inherited from the 3.7 verification instead of the Gemini-3 one.

Rung reporting: each rung's full (prob_t x min_votes <= N) sweep and
its oracle. The committed carried point (0.98, k10) exists only at
N = 10 (min_votes cannot exceed N), so no carried claims are made at
lower rungs — rung oracles are descriptive, labelled as such.

REPLICATION GATES (nothing is written unless all pass), mirroring
`stride55_ladder.py`:

1. The first-10 rebuild reproduces the committed K=10 union: exact
   count, identical votes, centroids within 0.2 m of the manifest.
2. The rebuilt N=10 rung at the carried point (0.98, k10) equals the
   committed fourth-cell primary @ 50 m to 1e-6
   (`results/gemini37-fourth-cell/55map/g384_ov192_55map/primary/
   eval/corrected-f1.csv`).

Usage::

    python scripts/gemini37_fourth_cell_ladder.py

Zero API. Run on sapphire (union rebuilds + ~150 sweep points x 55
Hungarian problems). Requires the completed `verify_37` verification.

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
from scripts.stride55_ladder import (  # noqa: E402
    INHERIT_TOL_M,
    NS,
    UNION_GATE_M,
    cluster_first_n,
    load_deduped_passes,
)
from scripts.stride55_score import build_map_constrained_index  # noqa: E402
from scripts.stride55_sweep_oracle import (  # noqa: E402
    BOUNDS,
    BUFFER_R,
    CANONICAL_REVIEW,
    STUDENT_GT,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

CELL = "g384_ov192_55map"
SPEC = CAMPAIGN_CELLS["fourth"]
OUT_DIR = PROJECT_ROOT / "results/gemini37-fourth-cell/55map" / CELL


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

    passes = load_deduped_passes(CELL)
    k10 = load_candidates("fourth", SPEC)
    tree = cKDTree(np.c_[k10.geometry.x, k10.geometry.y])
    probs10 = k10["mound_probability"].to_numpy()

    # Gate 1: the first-10 rebuild reproduces the committed union.
    rebuilt = cluster_first_n(passes, 10, index)
    if len(rebuilt) != SPEC["union_n"]:
        raise RuntimeError(
            f"union gate FAILED — rebuilt {len(rebuilt)} vs "
            f"committed {SPEC['union_n']}")
    d10, i10 = tree.query(np.c_[rebuilt.geometry.x, rebuilt.geometry.y], k=1)
    votes_match = (rebuilt["vote_count"].to_numpy()
                   == k10["vote_count"].to_numpy()[i10])
    if d10.max() > UNION_GATE_M or not votes_match.all():
        raise RuntimeError(
            f"union gate FAILED — max centroid distance {d10.max():.6f} m, "
            f"vote mismatches {int((~votes_match).sum())}")
    logger.info("union gate OK (n=%d, max dist %.6f m)",
                len(rebuilt), d10.max())

    # Gate 2: the rebuilt N=10 rung reproduces the committed primary.
    rebuilt["mound_probability"] = probs10[i10]
    pt, pk = SPEC["carried"]
    sub = rebuilt[(rebuilt["mound_probability"] >= pt)
                  & (rebuilt["vote_count"] >= pk)]
    tp, fp, fn, _ = compute_counts_at_r(sub, ext_gt, bounds, BUFFER_R)
    f1_primary = compute_point_estimate(tp, fp, fn)[2]
    committed = committed_f1_at_50(SPEC["committed"])
    if abs(f1_primary - committed) > 1e-6:
        raise RuntimeError(
            f"primary gate FAILED — ladder-path {f1_primary:.6f} vs "
            f"committed {committed:.6f}")
    logger.info("primary gate OK (%.6f)", f1_primary)

    payload: dict = {"buffer_m": BUFFER_R, "inherit_tol_m": INHERIT_TOL_M,
                     "cell": CELL, "verify_dir": SPEC["verify_dir"],
                     "carried_point": [pt, pk], "N": {}}
    rows_all: list[dict] = []
    for n in NS:
        gdf = cluster_first_n(passes, n, index)
        d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
        gdf["mound_probability"] = probs10[idx]
        matched = d <= INHERIT_TOL_M
        n_total = int(len(gdf))
        gdf = gdf[matched].copy()
        n_unmatched = n_total - int(len(gdf))

        thresholds = sorted({0.0} | {round(float(v), 4)
                                     for v in gdf["mound_probability"]})
        rung_rows = []
        for prob_t in thresholds:
            for k in range(1, n + 1):
                s = gdf[(gdf["mound_probability"] >= prob_t)
                        & (gdf["vote_count"] >= k)]
                tp, fp, fn, _ = compute_counts_at_r(s, ext_gt, bounds,
                                                    BUFFER_R)
                p, r, f1 = compute_point_estimate(tp, fp, fn)
                rung_rows.append({
                    "cell": CELL, "N": n, "prob_t": prob_t,
                    "min_votes": k, "n_detections": int(len(s)),
                    "tp": tp, "fp": fp, "fn": fn, "precision": p,
                    "recall": r, "corrected_f1": f1})
        rows_all.extend(rung_rows)
        best = max(rung_rows, key=lambda r: r["corrected_f1"])
        logger.info("N=%d: union %d (unmatched %d) | ORACLE %.4f at "
                    "(%.2f, k%d)", n, n_total, n_unmatched,
                    best["corrected_f1"], best["prob_t"], best["min_votes"])
        payload["N"][str(n)] = {
            "union_n": n_total, "unmatched": n_unmatched,
            "match_dist_p50_m": float(np.percentile(d[matched], 50)),
            "match_dist_p95_m": float(np.percentile(d[matched], 95)),
            "oracle": best}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / "ladder_sweep_50m.csv"
    with out_csv.open("w", newline="") as fh:
        w = csvmod.DictWriter(fh, fieldnames=list(rows_all[0].keys()))
        w.writeheader()
        w.writerows(rows_all)
    (OUT_DIR / "ladder.json").write_text(json.dumps(payload, indent=2) + "\n")
    logger.info("FOURTH-CELL LADDER COMPLETE -> %s",
                OUT_DIR.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
