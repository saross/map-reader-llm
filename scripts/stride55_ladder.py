#!/usr/bin/env python3
"""
55-map portfolio N-ladder: first-N rungs with inherited verification.

The card's § 3 secondary contract, item 2 (`planning/
55map-portfolio-2026-08-25.md`): the K-subset ladder N ∈ {1, 3, 5} by the
preregistered first-N rule for both deployment runs, verifier
probabilities INHERITED from the committed K = 10 verification (the
method validated at ±0.008 on the gold standard, 2026-08-25). N = 10 is
the committed primary/sweep itself (`stride55_sweep_oracle.py`); it is
rebuilt here only as a gate. Settles bets P2, P4, and P7.

Derivation per cell and rung, mirroring `stride55_prepare_and_union.py`
exactly (no carrier clip — the 55-map corpus is scored full-extent):
first-N deduped passes → `cluster_votes` at c = 1 → standard-grid tile
assignment → probability inheritance by nearest K = 10 candidate within
10 m (unmatched clusters counted, excluded from scoring, included in
cost) → full (prob_t × k ≤ N) sweep of corrected-F1 at 50 m against the
same fixed extended GT as the primary evaluations.

REPLICATION GATES (nothing is written unless all pass):

1. The first-10 rebuild must reproduce the committed K = 10 union:
   exact candidate count, every centroid within 0.01 m of the verifier
   manifest's, votes identical.
2. The rebuilt N = 10 rung evaluated at the registered primary point
   must equal the engine's committed evaluation @ 50 m to 1e-6
   (`results/stride55-2026-08-27/<run>/primary/eval/corrected-f1.csv`).

P7 (saturation) instrument: per-map paired sign-swap permutation
(10,000, seed 42) of N = 5 versus N = 10, at the carried points and at
the rung oracles.

Usage::

    python scripts/stride55_ladder.py

Zero API. Run on sapphire (~360 sweep points × 55 Hungarian problems).

Created: 2026-08-27 (Session 143)
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
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    DEFAULT_CRS,
    build_extended_gt,
    build_phantom_gdf,
    compute_counts_at_r,
    compute_point_estimate,
)
from scripts.grid_prepare_scoring import CoverageError, load_pass  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.merge_passes import deduplicate_within_pass  # noqa: E402
from scripts.stride55_prepare_and_union import (  # noqa: E402
    CELLS,
    DEDUP_METRES,
    MANDIR,
    OUTROOT,
    VF_CALL_USD,
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
    OUT_BASE,
    RUNS,
    STUDENT_GT,
    load_candidates,
    paired_permutation,
    per_map_counts,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NS = (1, 3, 5)
INHERIT_TOL_M = 10.0  # the GS-validated inheritance radius
UNION_GATE_M = 0.01  # first-10 rebuild vs committed union (4326 round-trip)

# Audited K = 10 proposer flex (card § 4) and the GS-carried N = 5
# operating points (card § 3b, bets P2/P4).
PROP10_USD = {"g384_ov128_55map": 77.31, "g384_ov192_55map": 134.10}
CARRIED_N5 = {"g384_ov128_55map": (0.15, 4), "g384_ov192_55map": (0.15, 5)}


def load_deduped_passes(cell: str) -> list[list[dict]]:
    """The ten deduped passes, coverage-gated exactly as the union build."""
    manifest = set(json.loads((MANDIR / CELLS[cell]).read_text()))
    cell_dir = OUTROOT / cell
    passes: list[list[dict]] = []
    for i in range(1, 11):
        run = f"run_{i}"
        raw, processed = load_pass(resolve_pass_paths(cell_dir, run))
        if processed != manifest:
            raise CoverageError(
                f"{cell}/{run}: {len(processed)} tiles vs "
                f"{len(manifest)} pinned")
        passes.append(deduplicate_within_pass(raw, distance_thresh=DEDUP_METRES))
    return passes


def cluster_first_n(passes: list[list[dict]], n: int,
                    index: dict) -> gpd.GeoDataFrame:
    """First-N clusters with votes and standard-grid tile assignment."""
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

    payload: dict = {"buffer_m": BUFFER_R, "inherit_tol_m": INHERIT_TOL_M,
                     "runs": {}}
    map_counts_at: dict[str, dict] = {}
    for cell, spec in RUNS.items():
        passes = load_deduped_passes(cell)
        k10 = load_candidates(cell, spec, bounds)
        tree = cKDTree(np.c_[k10.geometry.x, k10.geometry.y])
        probs10 = k10["mound_probability"].to_numpy()

        # Gate 1: the first-10 rebuild reproduces the committed union.
        rebuilt = cluster_first_n(passes, 10, index)
        if len(rebuilt) != spec["union_n"]:
            raise RuntimeError(
                f"{cell}: union gate FAILED — rebuilt {len(rebuilt)} vs "
                f"committed {spec['union_n']}")
        d10, i10 = tree.query(np.c_[rebuilt.geometry.x, rebuilt.geometry.y],
                              k=1)
        votes_match = (rebuilt["vote_count"].to_numpy()
                       == k10["vote_count"].to_numpy()[i10])
        if d10.max() > UNION_GATE_M or not votes_match.all():
            raise RuntimeError(
                f"{cell}: union gate FAILED — max centroid distance "
                f"{d10.max():.6f} m, vote mismatches "
                f"{int((~votes_match).sum())}")
        logger.info("%s: union gate OK (n=%d, max dist %.6f m)",
                    cell, len(rebuilt), d10.max())

        # Gate 2: the rebuilt N = 10 rung reproduces the committed primary.
        rebuilt["mound_probability"] = probs10[i10]
        pt, pk = spec["primary"]
        sub = rebuilt[(rebuilt["mound_probability"] >= pt)
                      & (rebuilt["vote_count"] >= pk)]
        tp, fp, fn, _ = compute_counts_at_r(sub, ext_gt, bounds, BUFFER_R)
        f1_primary = compute_point_estimate(tp, fp, fn)[2]
        committed = None
        with (OUT_BASE / cell / "primary" / "eval"
              / "corrected-f1.csv").open() as fh:
            for row in csvmod.DictReader(fh):
                if int(row["R_m"]) == BUFFER_R:
                    committed = float(row["F1"])
        if committed is None or abs(f1_primary - committed) > 1e-6:
            raise RuntimeError(
                f"{cell}: primary gate FAILED — ladder-path "
                f"{f1_primary:.6f} vs committed {committed}")
        logger.info("%s: primary gate OK (%.6f)", cell, f1_primary)
        map_counts_at[f"{cell}:N10:carried"] = per_map_counts(
            sub, ext_gt, bounds)

        cell_out = {"prop10_flex_usd": PROP10_USD[cell], "N": {}}
        rows_all = []
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
                        "cell": cell, "N": n, "prob_t": prob_t,
                        "min_votes": k, "n_detections": int(len(s)),
                        "tp": tp, "fp": fp, "fn": fn, "precision": p,
                        "recall": r, "corrected_f1": f1})
            rows_all.extend(rung_rows)
            best = max(rung_rows, key=lambda r: r["corrected_f1"])

            rung = {
                "union_n": n_total, "unmatched": n_unmatched,
                "match_dist_p50_m": float(np.percentile(d, 50)),
                "match_dist_p95_m": float(np.percentile(d, 95)),
                "oracle": best,
                "est_all_in_flex_usd": round(
                    PROP10_USD[cell] * n / 10 + n_total * VF_CALL_USD, 2),
            }
            if n == 5:
                ct, ck = CARRIED_N5[cell]
                carried = next(r for r in rung_rows
                               if r["prob_t"] == ct and r["min_votes"] == ck)
                rung["carried"] = carried
                s = gdf[(gdf["mound_probability"] >= ct)
                        & (gdf["vote_count"] >= ck)]
                map_counts_at[f"{cell}:N5:carried"] = per_map_counts(
                    s, ext_gt, bounds)
            s = gdf[(gdf["mound_probability"] >= best["prob_t"])
                    & (gdf["vote_count"] >= best["min_votes"])]
            map_counts_at[f"{cell}:N{n}:oracle"] = per_map_counts(
                s, ext_gt, bounds)
            cell_out["N"][n] = rung
            logger.info(
                "%s N=%d: union %5d (unmatched %d, p95 %.2f m) | oracle "
                "F1=%.4f at (%.2f, k%d) | est $%.2f all-in",
                cell, n, n_total, n_unmatched, rung["match_dist_p95_m"],
                best["corrected_f1"], best["prob_t"], best["min_votes"],
                rung["est_all_in_flex_usd"])

        out_csv = OUT_BASE / cell / "ladder_sweep_50m.csv"
        with out_csv.open("w", newline="") as fh:
            w = csvmod.DictWriter(fh, fieldnames=list(rows_all[0].keys()))
            w.writeheader()
            w.writerows(rows_all)
        payload["runs"][cell] = cell_out

    # P7: N = 5 vs N = 10, carried and oracle, per cell. The N = 10
    # oracle counts come from the committed sweep output.
    sweep = json.loads((OUT_BASE / "sweep_oracle.json").read_text())
    for cell, spec in RUNS.items():
        k10 = load_candidates(cell, spec, bounds)
        o = sweep["runs"][cell]["oracle"]
        s = k10[(k10["mound_probability"] >= o["prob_t"])
                & (k10["vote_count"] >= o["min_votes"])]
        map_counts_at[f"{cell}:N10:oracle"] = per_map_counts(s, ext_gt, bounds)
        payload["runs"][cell]["p7_saturation"] = {
            "carried_N5_vs_N10": paired_permutation(
                map_counts_at[f"{cell}:N5:carried"],
                map_counts_at[f"{cell}:N10:carried"]),
            "oracle_N5_vs_N10": paired_permutation(
                map_counts_at[f"{cell}:N5:oracle"],
                map_counts_at[f"{cell}:N10:oracle"]),
            "convention": "delta = N5 - N10, corrected-F1@50m",
        }
        for tag, res in payload["runs"][cell]["p7_saturation"].items():
            if isinstance(res, dict) and "delta_f1" in res:
                logger.info("%s N5 - N10 %s: dF1=%+.4f p=%.4f",
                            cell, tag, res["delta_f1"], res["p_two_sided"])

    (OUT_BASE / "ladder.json").write_text(json.dumps(payload, indent=2) + "\n")
    logger.info("LADDER COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
