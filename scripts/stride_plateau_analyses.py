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

4. **The exact winner ladder** (``winner_ladder_exact``). The 384 px /
   33.3 % cell's N ∈ {1, 3, 5} unions were re-verified exactly (PI-approved
   2026-08-25, commit ``346694beb``); their boards were folded into this
   file then by hand. :func:`winner_ladder_exact` now computes them, so the
   script regenerates its whole artefact.

**Origins (PI ruling D62 (1), 2026-10-13).** Every scored detection carries
the tiles it was seen on into the shared scorer, so it is booked to a
carrier tile on its OWN sheet: the nine cells' verified unions are rebuilt
from their passes (``lib_cluster_origins.union_on_origin``), the first-N
clusters keep their members' tiles, and the four incumbents keep the
``source_tile`` their own files record. Before D62 all of these were bare
centroids booked to the nearest carrier tile on ANY sheet, which near a
sheet edge re-keyed a detection to the neighbouring sheet
(``reports/s163-agent-records/origin-gap-grid-plateau.md``).

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
from scripts.grid_verifier_analysis import (  # noqa: E402
    load_verified_union,
    per_tile_counts,
    reassignment_gate,
    verified_subset,
)
from scripts.lib_cluster_origins import (  # noqa: E402
    cluster_votes_with_members,
    recorded_origin,
    union_on_origin,
)
from scripts.stride_verifier_analysis import (  # noqa: E402
    load_stride_union_on_origin,
    score_at,
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

#: The exact winner ladder: the cell whose first-N unions were re-verified,
#: and the rungs (``verifier/<cell>/union_k<N>.geojson`` with
#: ``verify_k<N>/``).
WINNER_CELL = "g384_ov128"
WINNER_NS = (1, 3, 5)

#: Phase A incumbents on the common footprint (clip via as_gdf at load, each
#: detection kept on the sheet of its own recorded ``source_tile``).
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
    """Load a cell's K = 10 verified union (grid or stride layout), on origin.

    Both layouts go through their own join and round-trip gates, then
    (D62 (1)) the union is rebuilt from the cell's passes, its members'
    tiles are attached, and each row is booked on its own sheet.

    Args:
        cell: Cell label (a key of :data:`CELL_SPECS`).
        bounds: Common carrier bounds.

    Returns:
        The joined union with ``mound_probability``, ``vote_count``,
        ``origin_tiles`` and an origin-sheet ``source_tile``.
    """
    spec = CELL_SPECS[cell]
    if spec["grid"]:
        gdf = reassignment_gate(load_verified_union(cell), bounds, cell)
        passes = load_cell_passes(PROJECT_ROOT / spec["root"] / "scoring", cell)
        return union_on_origin(gdf, passes, bounds, label=cell, n_passes=10)
    return load_stride_union_on_origin(cell, bounds)


def load_incumbent(rel: str, bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """One Phase A incumbent clipped to the common carrier, on its own sheet.

    Each incumbent file records its own ``source_tile``; that tile's sheet is
    kept as the detection's origin (D62 (1)) rather than discarded for a bare
    centroid, so a detection near a sheet edge is not booked to the
    neighbouring sheet's carrier tile.

    Args:
        rel: The incumbent's path relative to the repository root.
        bounds: Common carrier bounds.

    Returns:
        The scorable set (rows on no carrier tile of their own sheet dropped).
    """
    inc = gpd.read_file(PROJECT_ROOT / rel).to_crs(CRS)
    return as_gdf(np.asarray([[g.x, g.y] for g in inc.geometry]), bounds,
                  origins=recorded_origin(inc))


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
    # apply_bh_correction returns ADJUSTED p-values; significance is the
    # comparison against q (the canonical callers' contract — boolifying
    # the floats marks every pair significant, the bug the first run of
    # this script shipped and the paired-bootstrap cross-check caught).
    adjusted = apply_bh_correction(pvals, q=FDR_Q)
    significant = {frozenset(p): (adj <= FDR_Q)
                   for p, adj in zip(pairs, adjusted)}
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
            centroids, votes, members = cluster_votes_with_members(subset_passes, 1)
            gdf = as_gdf(centroids, bounds, origins=members)
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


def winner_ladder_exact(
    bounds: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame, prop10_flex_usd: float,
) -> dict[str, Any]:
    """The exactly re-verified first-N rungs of the winner cell.

    Each rung's union (``union_k<N>.geojson``, built from the first N passes)
    is joined to its own ``verify_k<N>`` probabilities and gated as the K = 10
    unions are, then swept over every observed ``prob_t`` (and 0.0) crossed
    with ``min_votes`` 1..N; the best F1 at 20 m is kept (first maximum in
    sweep order, as :func:`first_n_ladder` keeps it).

    Args:
        bounds: Common carrier bounds.
        gdf_ref: Curator references.
        prop10_flex_usd: The cell's audited K = 10 proposer spend on the flex
            basis (the ladder's ``prop10_flex_usd``); a rung's proposer share
            is N/10 of it.

    Returns:
        ``{"cell", "note", "N": {n: {...}}}`` in the committed layout.
    """
    root = PROJECT_ROOT / CELL_SPECS[WINNER_CELL]["root"] / "verifier" / WINNER_CELL
    out: dict[str, Any] = {
        "cell": WINNER_CELL,
        "note": ("Exact re-verification of the N in {1,3,5} unions (PI-approved "
                 "2026-08-25, ~$3.4 flex): full unions verified including "
                 "inheritance-unmatched clusters; join gates exact."),
        "N": {},
    }
    for n in WINNER_NS:
        union_name = f"union_k{n}.geojson"
        union_n = len(json.loads((root / union_name).read_text())["features"])
        gdf = load_stride_union_on_origin(
            WINNER_CELL, bounds, union_name=union_name,
            verify_dir=f"verify_k{n}", n_passes=n)
        thresholds = sorted({0.0} | {float(v) for v in gdf["mound_probability"]})
        best = None
        for prob_t in thresholds:
            for k in range(1, n + 1):
                row = score(verified_subset(gdf, prob_t, k), gdf_ref, bounds)
                row.update({"prob_t": prob_t, "min_votes": k})
                if best is None or row["f1"] > best["f1"]:
                    best = row
        best_set = verified_subset(gdf, best["prob_t"], best["min_votes"])
        meta = json.loads((root / f"verify_k{n}" / "run.meta.json").read_text())
        list_usd = float(meta["cost_estimate"]["list_total_cost_usd"])
        flex_usd = round(list_usd / 2.0, 4)
        out["N"][n] = {
            "union_n": union_n,
            "verified_failed": int(meta["execution_stats"]["items_failed"]),
            "best": {k: best[k] for k in
                     ("precision", "recall", "f1", "mcc",
                      "n_detections", "prob_t", "min_votes")},
            "f1_30m": score_at(best_set, gdf_ref, bounds, 30)["f1"],
            "verifier_list_usd": list_usd,
            "verifier_flex_usd": flex_usd,
            "all_in_flex_usd": round(prop10_flex_usd * n / 10 + flex_usd, 2),
        }
        logger.info("exact ladder N=%d: union %d | best F1=%.4f at p>=%.2f k>=%d "
                    "| @30m %.4f | $%.2f all-in", n, union_n, best["f1"],
                    best["prob_t"], best["min_votes"], out["N"][n]["f1_30m"],
                    out["N"][n]["all_in_flex_usd"])
    return out


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
        sets[name] = load_incumbent(rel, bounds)

    board = board_and_tiers(sets, bounds, gdf_ref)
    curves = k_curves(len(bounds))
    ladder = first_n_ladder(bounds, gdf_ref)
    exact = winner_ladder_exact(
        bounds, gdf_ref, ladder[WINNER_CELL]["prop10_flex_usd"])

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
        "winner_ladder_exact": exact,
    }, indent=2) + "\n")
    logger.info("wrote %s", OUT_PATH.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
