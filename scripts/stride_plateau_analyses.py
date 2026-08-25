#!/usr/bin/env python3
"""
Stride plateau follow-ups: the tiered board, k-curves, and the free N-ladder.

The three $0 analyses the PI commissioned on 2026-08-25 after the overnight
stride programme (`results/stride-2026-08-25/findings.md`):

1. **The 13-cell tiered board.** The nine geometry cells' verified best
   points plus the four Phase A incumbents, tiered with the study's board
   instrument imported VERBATIM (round-robin tile-swap micro-F1 permutation,
   10,000 perms, seed 42; Benjamini–Hochberg q = 0.05; greedy cliques).
   Characterises the plateau the 55-map choice must be made from. (The
   formal E83 Multiple-Comparisons-with-the-Best admissible set can be run
   through `selection_aware_intervals.py` if the paper needs it; the greedy
   tiers here are the descriptive board.)

2. **k-of-10 curves.** Per cell, F1 versus the consensus vote threshold at
   the cell's best verifier threshold, from the committed sweeps — how flat
   is the top, and how much threshold precision does deployment need?

3. **The N-ladder, free.** N ∈ {1, 3, 5} boards for all nine cells, derived
   from the committed pools by the preregistered first-N rule. Verifier
   probabilities are INHERITED: each first-N cluster takes the probability
   of its nearest K = 10 verified candidate. The inheritance is validated,
   not assumed — per cell and N the match-distance distribution and any
   unmatched clusters are reported; T = 0.0 n = 1 verification is
   deterministic per crop, so inheritance error is bounded by centroid
   drift between clusterings. Exact re-verification of finalists is a
   separately gated spend.

Zero API. Run on sapphire (~40 sweeps, 78 permutation pairs at 10k).

Usage::

    python scripts/stride_plateau_analyses.py

Created: 2026-08-25 (Session 142)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from apply_fdr_correction import apply_bh_correction  # noqa: E402
from n1_baseline_leaderboard_tiering import (  # noqa: E402
    greedy_clique_tiers,
    permutation_test_float,
)

from scripts.grid_analysis import CRS, as_gdf, load_cell_passes, score  # noqa: E402
from scripts.grid_verifier_analysis import per_tile_counts, verified_subset  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.stride_verifier_analysis import (  # noqa: E402
    load_stride_union,
    reassign_gate,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

COMMON_BOUNDS = (
    PROJECT_ROOT / "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson")
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
STRIDE_RESULTS = PROJECT_ROOT / "results/stride-2026-08-25"
OUT_PATH = STRIDE_RESULTS / "plateau_analyses.json"

N_PERMUTATIONS = 10_000
SEED = 42
FDR_Q = 0.05

#: Verifier flex rate, measured on the 16,966-call stride verifier campaign.
VF_CALL_USD = 0.000687

#: Inheritance tolerance: a first-N cluster whose nearest K = 10 candidate is
#: farther than this is left unverified (excluded, counted, reported).
INHERIT_TOL_M = 10.0

#: cell -> (scoring dir root, K10 union loader kind, K10 proposer flex $).
#: Proposer costs are the audited per-cell flex figures.
CELL_SPECS: dict[str, dict[str, Any]] = {
    "g512_ov064": {"root": "outputs/grid-2026-08-18", "grid": True, "prop10": 1.9022},
    "g512_ov256": {"root": "outputs/grid-2026-08-18", "grid": True, "prop10": 5.3398},
    "g384_ov048": {"root": "outputs/grid-2026-08-18", "grid": True, "prop10": 2.9059},
    "g384_ov192": {"root": "outputs/grid-2026-08-18", "grid": True, "prop10": 8.3821},
    "g512_ov176": {"root": "outputs/stride-phaseb-2026-08-25", "grid": False},
    "g384_ov128": {"root": "outputs/stride-phaseb-2026-08-25", "grid": False},
    "g256_ov064": {"root": "outputs/stride-phaseb-2026-08-25", "grid": False},
    "g512_ov320": {"root": "outputs/stride-phaseb-2026-08-25", "grid": False},
    "g384_ov240": {"root": "outputs/stride-phasec-2026-08-25", "grid": False},
}

#: Phase A incumbents on the common footprint (clip via as_gdf at load).
INCUMBENTS: dict[str, str] = {
    "opmax": "results/verifier-robustness/opmax-sets/"
             "opmax-16of30-N5minT0.3-vt3-pt0.15.geojson",
    "headline": "outputs/era1-pv-stage-d/384-consensus-text-high/pass_1/"
                "accepted_t0.2.geojson",
    "min11": "results/verifier-robustness/min-thinking-sets/"
             "text-min-t07-10pass-6of10-n1-pt0.2.geojson",
    "min6": "results/verifier-robustness/min-thinking-sets/"
            "text-min-t07-TRUE-5pass-3of5-n1-pt0.15.geojson",
}


def load_k10_union(cell: str, bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Load a cell's K = 10 verified union (grid or stride layout)."""
    spec = CELL_SPECS[cell]
    if spec["grid"]:
        root = PROJECT_ROOT / spec["root"] / "verifier" / cell
        gdf = gpd.read_file(root / "union_k10.geojson").to_crs(CRS)
        results = json.loads(
            (root / "verify" / "probabilities.json").read_text())["results"]
        gdf["mound_probability"] = [
            float(results[f"candidate_{i:05d}"]["mound_probability"])
            for i in range(len(gdf))
        ]
        return gdf
    return reassign_gate(load_stride_union(cell), bounds, cell)


def best_points() -> dict[str, dict[str, Any]]:
    """The nine cells' published best (prob_t, min_votes) operating points."""
    grid = json.loads((PROJECT_ROOT / "results/grid-2026-08-18/"
                       "verifier_analysis.json").read_text())["board_best"]
    stride = json.loads((STRIDE_RESULTS /
                         "stride_verifier_analysis.json").read_text())["boards"]
    out = {}
    for cell in CELL_SPECS:
        src = grid.get(cell) or stride.get(cell)
        out[cell] = {"prob_t": src["prob_t"], "min_votes": src["min_votes"],
                     "f1": src["f1"]}
    return out


def board_and_tiers(
    sets: dict[str, gpd.GeoDataFrame], bounds: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
) -> dict[str, Any]:
    """Pairwise tile-swap permutation board over the given single sets."""
    pt = {name: per_tile_counts(g, bounds, gdf_ref) for name, g in sets.items()}
    f1s = {name: score(g, gdf_ref, bounds)["f1"] for name, g in sets.items()}
    ordered = sorted(f1s, key=lambda n: -f1s[n])
    pairs = list(combinations(ordered, 2))
    logger.info("board: %d cells, %d pairs at %d perms",
                len(ordered), len(pairs), N_PERMUTATIONS)
    raw = {}
    for a, b in pairs:
        res = permutation_test_float(
            pt[a]["tp"], pt[a]["fp"], pt[a]["fn"],
            pt[b]["tp"], pt[b]["fp"], pt[b]["fn"],
            n_permutations=N_PERMUTATIONS, seed=SEED)
        raw[(a, b)] = res
    pvals = [raw[p]["p_value"] for p in pairs]
    rejected = apply_bh_correction(pvals, q=FDR_Q)
    significant = {frozenset(p): bool(r) for p, r in zip(pairs, rejected)}
    tiers = greedy_clique_tiers(ordered, significant)
    n_sig = sum(significant.values())
    logger.info("board: %d/%d pairs significant after BH -> %d tiers; "
                "tier 1 = %s", n_sig, len(pairs), len(tiers), tiers[0])
    return {
        "f1": f1s,
        "order": ordered,
        "n_pairs_significant": n_sig,
        "n_pairs": len(pairs),
        "tiers": tiers,
        "pairwise": {
            f"{a} vs {b}": {"delta": raw[(a, b)]["observed_diff"],
                            "p": raw[(a, b)]["p_value"],
                            "significant_bh": significant[frozenset((a, b))]}
            for a, b in pairs
        },
    }


def k_curves(bounds_len_hint: int) -> dict[str, Any]:
    """F1 vs vote threshold at each cell's best prob_t, from committed sweeps."""
    rows = []
    import csv as _csv
    for path in [PROJECT_ROOT / "results/grid-2026-08-18/verifier_sweep.csv",
                 STRIDE_RESULTS / "stride_verifier_sweep.csv"]:
        with path.open() as fh:
            rows.extend(list(_csv.DictReader(fh)))
    points = best_points()
    out = {}
    for cell, bp in points.items():
        curve = sorted(
            ((int(r["min_votes"]), float(r["f1"]))
             for r in rows
             if r["cell"] == cell and float(r["prob_t"]) == float(bp["prob_t"])),
            key=lambda x: x[0])
        best_f1 = max(f for _, f in curve)
        near = [k for k, f in curve if best_f1 - f <= 0.005]
        out[cell] = {
            "prob_t": bp["prob_t"],
            "curve": curve,
            "best_k": max(curve, key=lambda x: x[1])[0],
            "k_within_0p005": near,
            "flat_top_width": len(near),
        }
        logger.info("k-curve %-11s: best k=%d, %d thresholds within 0.005 "
                    "of peak (%s)", cell, out[cell]["best_k"], len(near), near)
    return out


def first_n_ladder(
    bounds: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
) -> dict[str, Any]:
    """N in {1,3,5} verified boards via first-N derivation + inheritance."""
    ladder: dict[str, Any] = {}
    for cell, spec in CELL_SPECS.items():
        scoring = PROJECT_ROOT / spec["root"] / "scoring"
        passes = load_cell_passes(scoring, cell)
        k10 = load_k10_union(cell, bounds)
        tree = cKDTree(np.c_[k10.geometry.x, k10.geometry.y])
        probs10 = k10["mound_probability"].to_numpy()
        # Audited K=10 proposer flex: grid cells carry it in the spec; the
        # stride cells' figure comes from their committed metas.
        prop10 = spec.get("prop10")
        if prop10 is None:
            total = 0.0
            for meta in (PROJECT_ROOT / spec["root"] / cell).glob(
                    "run_*/*.meta.json"):
                total += json.loads(meta.read_text())[
                    "cost_estimate"]["list_total_cost_usd"]
            prop10 = total / 2.0
        cell_out = {"prop10_flex_usd": round(float(prop10), 4), "N": {}}
        for n in (1, 3, 5):
            subset_passes = passes[:n]
            centroids, votes = cluster_votes(subset_passes, 1)
            gdf = as_gdf(centroids, bounds)
            # as_gdf drops off-carrier rows but keeps positional indices, so
            # the surviving rows' votes are recovered by original position.
            kept = gdf.index.to_numpy()
            gdf = gdf.reset_index(drop=True)
            gdf["vote_count"] = np.asarray(votes)[kept]
            d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
            gdf["mound_probability"] = probs10[idx]
            matched = d <= INHERIT_TOL_M
            n_unmatched = int((~matched).sum())
            gdf = gdf[matched].copy()
            thresholds = sorted({0.0} | {float(v)
                                         for v in gdf["mound_probability"]})
            best = None
            for prob_t in thresholds:
                for k in range(1, n + 1):
                    sub = verified_subset(gdf, prob_t, k)
                    row = score(sub, gdf_ref, bounds)
                    row.update({"prob_t": prob_t, "min_votes": k})
                    if best is None or row["f1"] > best["f1"]:
                        best = row
            vf_cost = len(gdf) * VF_CALL_USD
            all_in = prop10 * n / 10 + vf_cost
            cell_out["N"][n] = {
                "union_n": int(len(gdf)) + n_unmatched,
                "unmatched": n_unmatched,
                "match_dist_p50_m": float(np.percentile(d, 50)),
                "match_dist_p95_m": float(np.percentile(d, 95)),
                "match_dist_max_m": float(d.max()) if len(d) else None,
                "best": {k: best[k] for k in
                         ("precision", "recall", "f1", "mcc",
                          "n_detections", "prob_t", "min_votes")},
                "est_all_in_flex_usd": round(all_in, 2),
            }
            logger.info(
                "%-11s N=%d: union %4d (unmatched %d, p95 dist %.2f m) | "
                "best F1=%.4f at p>=%.2f k>=%d | est $%.2f all-in",
                cell, n, len(gdf) + n_unmatched, n_unmatched,
                float(np.percentile(d, 95)), best["f1"], best["prob_t"],
                best["min_votes"], all_in)
        ladder[cell] = cell_out
    return ladder


def main() -> int:
    bounds = gpd.read_file(COMMON_BOUNDS)
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    logger.info("common carrier: %d tiles", len(bounds))

    points = best_points()
    sets: dict[str, gpd.GeoDataFrame] = {}
    for cell in CELL_SPECS:
        u = load_k10_union(cell, bounds)
        sets[cell] = verified_subset(u, points[cell]["prob_t"],
                                     points[cell]["min_votes"])
    for name, rel in INCUMBENTS.items():
        inc = gpd.read_file(PROJECT_ROOT / rel).to_crs(CRS)
        sets[name] = as_gdf(
            np.asarray([[g.x, g.y] for g in inc.geometry]), bounds)

    board = board_and_tiers(sets, bounds, gdf_ref)
    curves = k_curves(len(bounds))
    ladder = first_n_ladder(bounds, gdf_ref)

    OUT_PATH.write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": (
            "POST-HOC (E41-class) plateau follow-ups: 13-cell tiered board "
            "(verbatim board instrument), k-of-10 curves, and the free "
            "first-N ladder with inheritance validation. $0."),
        "board_13cell": board,
        "k_curves": curves,
        "first_n_ladder": ladder,
        "inheritance": {
            "tolerance_m": INHERIT_TOL_M,
            "note": ("Probabilities inherited from the K = 10 verified "
                     "candidates; deterministic n = 1 T = 0.0 verification "
                     "makes the error bounded by centroid drift, measured "
                     "above. Exact re-verification of finalists is a "
                     "separately gated spend."),
        },
        "bootstrap_config": {"n_permutations": N_PERMUTATIONS, "seed": SEED,
                             "fdr_q": FDR_Q},
    }, indent=2) + "\n")
    logger.info("wrote %s", OUT_PATH.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
