#!/usr/bin/env python3
"""
Selection-aware uncertainty for in-sample-optimised operating points.

Every "best cell" figure in this study is an argmax taken over a candidate sweep
scored on the evaluation set itself. The reported maximum is therefore
optimistically biased — it has been chosen partly for its noise — and an ordinary
confidence interval for that cell describes the wrong quantity, because it treats
the winner as though it were the only configuration ever scored. Erratum E56
documents the problem for verifier probability thresholds; it is general.

Two instruments, because the study makes two different kinds of claim.

**MCB (multiple comparisons with the best; Hsu 1984, Edwards & Hsu 1983).**
Simultaneous intervals for each candidate against the best of the others,
``theta_i = F1_i - max_{j != i} F1_j``. The candidates whose interval does not
exclude zero are those that **cannot be ruled out as best** at the stated
simultaneous confidence. That set is precisely what this project already reports
as a tie set, currently derived ad hoc from pairwise permutation plus BH-FDR plus
a greedy clique; MCB is the canonical instrument for it and is simultaneous by
construction rather than by correction.

**Selection-aware bootstrap (Efron-Gong optimism, with the argmax replayed).**
For the headline point estimate. Within each tile resample the whole selection is
re-run, so the optimism the selection itself introduces is measured rather than
assumed away. The correction is a location shift applied to both the point
estimate and its percentile interval.

Both resample **tiles**, the unit Decision 10 registers, and both resample the
same tiles for every candidate, so the strong correlation between neighbouring
operating points is preserved rather than broken.

Scope, deliberately narrow
--------------------------
This applies ONLY where an argmax was taken over candidates scored on the
evaluation data. It must NOT be applied to a comparison made at a fixed operating
point across arms — the grid's overlap, tile-size, and interaction contrasts are
computed by ``grid_analysis.build_per_tile`` on run-averaged single-pass counts
with no consensus filter and no selection, so they are already selection-free and
correcting them would introduce a bias rather than remove one.

Known limitation
----------------
The ordinary n-out-of-n bootstrap of an argmax is delicate when candidates are
tied, which is this study's common case: tie sets run to 20 members. ``--m-frac``
enables m-out-of-n subsampling, the standard remedy. The pilot reports the
tie-mass diagnostic (how often the argmax changes across resamples) so the
severity is visible rather than assumed.

Usage::

    # a grid cell's (corroboration x vote) sweep
    python scripts/selection_aware_intervals.py --cell g512_ov256 --K 10 \\
        --bootstrap 10000 --out results/selection-aware/

    # any registered leaderboard, by analysis id
    python scripts/selection_aware_intervals.py --board era1-single-pass-baseline-matrix \\
        --bootstrap 10000 --out results/selection-aware/

Notes:
    - Zero API spend; reads committed artefacts only.
    - Run on sapphire.

Created: 2026-08-19 (Session 137)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_analysis import (  # noqa: E402
    BUFFER_M,
    CELL_LABEL,
    CORROBORATION,
    as_gdf,
    cluster_votes,
    load_cell_passes,
)
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCORING_DIR = PROJECT_ROOT / "outputs/grid-2026-08-18/scoring"
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
COMMON_BOUNDS = SCORING_DIR / "bounds" / "grid_common_bounds.geojson"
SEED = 42


def reference_occupancy(
    gdf_ref: "gpd.GeoDataFrame", gdf_bounds: "gpd.GeoDataFrame",
    tile_order: list[str],
) -> np.ndarray:
    """Per-tile reference occupancy, by INTERSECTION (registered § 4.2).

    A reference lying in an overlap region counts for every tile it intersects,
    which is what `lib_advanced_metrics.calculate_tile_classification` does and
    what makes the derived confusion matrix reproduce the committed one.
    """
    geom = dict(zip(gdf_bounds["tile_name"], gdf_bounds.geometry, strict=False))
    return np.array([len(gdf_ref[gdf_ref.intersects(geom[t])]) > 0
                     for t in tile_order])


def build_candidate_tile_counts(
    cell: str, k_total: int, bounds: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
) -> tuple[list[dict[str, int]], np.ndarray, np.ndarray]:
    """Score every (corroboration, vote) candidate to per-tile TP/FP/FN.

    Args:
        cell: Grid cell label.
        k_total: Pass budget K; the first K passes are used, matching the sweep.
        bounds: Carrier tile bounds, which fix tile order.
        gdf_ref: Ground-truth references.

    Returns:
        ``(specs, counts, has_mounds)`` where ``specs`` names each candidate,
        ``counts`` has shape ``(n_candidates, n_tiles, 3)`` in TP/FP/FN order,
        and ``has_mounds`` is per-tile reference occupancy.
    """
    passes = load_cell_passes(SCORING_DIR, cell)[:k_total]
    tile_order = list(bounds["tile_name"])
    specs: list[dict[str, int]] = []
    rows: list[np.ndarray] = []

    for c in CORROBORATION:
        centroids, votes = cluster_votes(passes, c)
        for k in range(1, k_total + 1):
            gdf = as_gdf(centroids[votes >= k], bounds)
            arr = np.zeros((len(tile_order), 3))
            if not gdf.empty:
                tm = compute_per_tile_tp_fp_fn(
                    gdf, gdf_ref, bounds, buffer_metres=BUFFER_M)
                tm = tm.set_index("tile_name").reindex(tile_order).fillna(0)
                arr[:, 0] = tm["tp"].to_numpy(dtype=float)
                arr[:, 1] = tm["fp"].to_numpy(dtype=float)
                arr[:, 2] = tm["fn"].to_numpy(dtype=float)
            else:
                # No detections: every reference in scope is a false negative.
                # The empty column must be explicitly string-typed — an empty
                # pandas column defaults to float64, and the scorer's
                # `.str.startswith` on it raises rather than returning nothing.
                empty = gpd.GeoDataFrame(
                    {"source_tile": pd.Series([], dtype="object")},
                    geometry=[], crs=bounds.crs,
                )
                tm = compute_per_tile_tp_fp_fn(
                    empty, gdf_ref, bounds, buffer_metres=BUFFER_M)
                tm = tm.set_index("tile_name").reindex(tile_order).fillna(0)
                arr[:, 2] = tm["fn"].to_numpy(dtype=float)
            specs.append({"min_corroboration": c, "min_votes": k})
            rows.append(arr)
    return specs, np.stack(rows), reference_occupancy(gdf_ref, bounds, tile_order)


def f1_from_counts(counts: np.ndarray, weights: np.ndarray | None = None) -> np.ndarray:
    """Micro-F1 per candidate from per-tile counts, optionally tile-weighted.

    Args:
        counts: ``(n_candidates, n_tiles, 3)`` TP/FP/FN array.
        weights: Per-tile multiplicities from a resample; ``None`` means all ones.

    Returns:
        ``(n_candidates,)`` micro-F1.
    """
    if weights is None:
        tot = counts.sum(axis=1)
    else:
        tot = np.einsum("ctm,t->cm", counts, weights)
    tp, fp, fn = tot[:, 0], tot[:, 1], tot[:, 2]
    denom = 2 * tp + fp + fn
    return np.where(denom > 0, 2 * tp / np.maximum(denom, 1e-12), 0.0)


def mcc_from_indicators(
    has_det: np.ndarray, has_mounds: np.ndarray, weights: np.ndarray | None = None,
) -> np.ndarray:
    """Tile-level MCC per candidate, optionally tile-weighted.

    Implements registered § 4.2 tile-level discrimination. A tile is
    reference-populated when any reference INTERSECTS it (so a reference in an
    overlap region counts for both neighbours) and predicted-populated when any
    detection is booked to it. Verified to reproduce a committed
    ``tile_classification`` block exactly, confusion counts and MCC alike, before
    being used here — deriving reference occupancy from the detection-level FN
    column instead does NOT reproduce it, because references are booked to tiles
    by a different rule than detections.

    An undefined MCC (any vanishing marginal, erratum E81) is returned as NaN and
    never as 0.0.

    Args:
        has_det: ``(n_candidates, n_tiles)`` boolean predicted-populated.
        has_mounds: ``(n_tiles,)`` boolean reference-populated.
        weights: Per-tile multiplicities from a resample; ``None`` means ones.

    Returns:
        ``(n_candidates,)`` tile MCC, NaN where undefined.
    """
    w = np.ones(has_mounds.shape[0]) if weights is None else weights
    ref = has_mounds[None, :]
    tp = (has_det & ref) @ w
    tn = (~has_det & ~ref) @ w
    fp = (has_det & ~ref) @ w
    fn = (~has_det & ref) @ w
    den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.where(den > 0, (tp * tn - fp * fn) / np.maximum(den, 1e-300), np.nan)
    return out


def resample_weights(rng: np.random.Generator, n: int, m: int) -> np.ndarray:
    """Draw one tile resample as a multiplicity vector (m draws from n tiles)."""
    return np.bincount(rng.integers(0, n, size=m), minlength=n).astype(float)


def run(
    counts: np.ndarray, b: int, m_frac: float, seed: int,
    has_mounds: np.ndarray | None = None, metric: str = "f1",
) -> dict[str, Any]:
    """Selection-aware bootstrap plus bootstrap MCB over one candidate set.

    Args:
        counts: ``(n_candidates, n_tiles, 3)`` per-tile TP/FP/FN counts.
        b: Bootstrap resamples.
        m_frac: Subsample size as a fraction of n (1.0 = ordinary n-out-of-n).
        seed: RNG seed.
        has_mounds: ``(n_tiles,)`` reference occupancy; required for ``mcc``.
        metric: ``f1`` (detection-level micro-F1) or ``mcc`` (tile-level).

    Returns:
        A dict of results; see the module docstring for interpretation.

    Raises:
        ValueError: if ``mcc`` is requested without ``has_mounds``, or if fewer
            than two candidates have a defined statistic.
    """
    rng = np.random.default_rng(seed)
    n_cand, n_tiles, _ = counts.shape
    m = max(1, int(round(m_frac * n_tiles)))

    if metric == "mcc":
        if has_mounds is None:
            raise ValueError("metric='mcc' requires has_mounds")
        has_det = (counts[:, :, 0] + counts[:, :, 1]) > 0

        def stat(w: np.ndarray | None = None) -> np.ndarray:
            return mcc_from_indicators(has_det, has_mounds, w)
    else:
        def stat(w: np.ndarray | None = None) -> np.ndarray:
            return f1_from_counts(counts, w)

    f1_full = stat()
    # A candidate whose statistic is undefined on the full data cannot be
    # "the best" in any defined sense, and E81 forbids reading its undefined
    # MCC as 0.0. Drop it from the candidate set and say so.
    defined = np.isfinite(f1_full)
    n_undefined = int((~defined).sum())
    if n_undefined:
        if int(defined.sum()) < 2:
            raise ValueError("fewer than two candidates have a defined statistic")
        keep = np.flatnonzero(defined)
        counts = counts[keep]
        if metric == "mcc":
            has_det = has_det[keep]

            def stat(w: np.ndarray | None = None) -> np.ndarray:  # noqa: F811
                return mcc_from_indicators(has_det, has_mounds, w)
        else:
            def stat(w: np.ndarray | None = None) -> np.ndarray:  # noqa: F811
                return f1_from_counts(counts, w)
        f1_full = stat()
        n_cand = len(keep)
    else:
        keep = np.arange(n_cand)
    k_star = int(np.nanargmax(f1_full))
    apparent = float(f1_full[k_star])

    # theta_i = F1_i - max_{j != i} F1_j, the MCB quantity.
    def theta(f: np.ndarray) -> np.ndarray:
        """theta_i = stat_i - max_{j != i} stat_j, NaN-safe."""
        order = np.argsort(np.where(np.isfinite(f), f, -np.inf))[::-1]
        best, second = f[order[0]], f[order[1]]
        out = f - best
        out[order[0]] = best - second
        return out

    theta_full = theta(f1_full)

    boot_f1 = np.empty((b, n_cand))
    boot_theta = np.empty((b, n_cand))
    sel = np.empty(b, dtype=int)
    optimism = np.empty(b)
    for i in range(b):
        w = resample_weights(rng, n_tiles, m)
        f = stat(w)
        # A resample can make a candidate's MCC undefined even where the full
        # data does not. Undefined stays NaN — substituting -inf would poison
        # the MCB deviation arithmetic downstream — and the argmax and the
        # deviation quantiles are taken NaN-aware instead.
        boot_f1[i] = f
        boot_theta[i] = theta(f)
        kb = int(np.nanargmax(f)) if np.any(np.isfinite(f)) else k_star
        sel[i] = kb
        # Efron-Gong optimism with the argmax REPLAYED: the winner inside this
        # resample, scored in-resample, against that same winner scored on the
        # full data. The comparator is held fixed by construction.
        optimism[i] = f[kb] - f1_full[kb]

    opt = float(np.nanmean(optimism))
    # The SPREAD of per-resample optimism is not the uncertainty on its MEAN.
    # Report both: the spread describes how variable the selection penalty is
    # from resample to resample, while the Monte Carlo standard error says how
    # well B resamples pin the estimate down. Quoting the spread alone would
    # make a well-determined optimism look unmeasurable.
    opt_mcse = float(np.nanstd(optimism, ddof=1) / np.sqrt(np.isfinite(optimism).sum()))
    corrected = apparent - opt

    # Naive interval for k*, then the same interval location-shifted by the
    # measured optimism. The shift is what makes it a post-selection interval.
    naive_lo, naive_hi = np.nanpercentile(boot_f1[:, k_star], [2.5, 97.5])
    shifted = (float(naive_lo - opt), float(naive_hi - opt))

    # --- MCB, two ways -------------------------------------------------------
    #
    # Both target Hsu's quantity theta_i = F1_i - max_{j != i} F1_j and both use
    # the same decision rule (a candidate is ruled out as best only when its
    # simultaneous UPPER bound falls at or below zero). They differ in the
    # critical value, and the difference is the point of running both.
    #
    # (a) Two-sided max-|deviation| band. One common width for every candidate,
    #     taken from the distribution of the largest absolute deviation. Simple
    #     and assumption-light, but it spends confidence on the lower tail that
    #     the admissibility question never uses, so it is CONSERVATIVE.
    #
    # (b) Hsu's constrained one-sided form. The critical value comes from the
    #     one-sided distribution of the largest deviation in the direction that
    #     actually decides exclusion, and the bounds are truncated at zero
    #     because no candidate can beat the best by construction. This is the
    #     published instrument; the bootstrap replaces Dunnett's tabulated
    #     critical value, which assumes normal homoscedastic means that micro-F1
    #     on correlated tiles does not satisfy.
    dev_signed_up = boot_theta - theta_full[None, :]
    crit = float(np.nanpercentile(np.nanmax(np.abs(dev_signed_up), axis=1), 95))
    mcb_lo = theta_full - crit
    mcb_hi = theta_full + crit
    not_ruled_out = [i for i in range(n_cand)
                     if np.isfinite(mcb_hi[i]) and mcb_hi[i] >= 0]

    w_upper = float(np.nanpercentile(np.nanmax(dev_signed_up, axis=1), 95))
    w_lower = float(np.nanpercentile(np.nanmax(-dev_signed_up, axis=1), 95))
    hsu_lo = np.minimum(0.0, theta_full - w_lower)
    hsu_hi = np.maximum(0.0, theta_full + w_upper)
    hsu_not_ruled_out = [i for i in range(n_cand)
                         if np.isfinite(theta_full[i]) and theta_full[i] + w_upper > 0]

    sel_counts = np.bincount(sel, minlength=n_cand)
    return {
        "metric": metric,
        "n_candidates": n_cand,
        "n_candidates_dropped_undefined": n_undefined,
        "kept_indices": [int(i) for i in keep],
        "n_tiles": n_tiles,
        "m_out_of_n": m,
        "bootstrap": b,
        "selected_index": k_star,
        "apparent_f1": apparent,
        "optimism": opt,
        "optimism_mcse": opt_mcse,
        "optimism_spread_p2_5_p97_5": [float(x) for x in np.nanpercentile(optimism, [2.5, 97.5])],
        "corrected_f1": float(corrected),
        "naive_ci": [float(naive_lo), float(naive_hi)],
        "selection_aware_ci": list(shifted),
        "argmax_stability": float(sel_counts[k_star] / b),
        "n_distinct_argmax": int((sel_counts > 0).sum()),
        "mcb_critical_width": crit,
        "mcb_theta": [float(x) for x in theta_full],
        "mcb_lower": [float(x) for x in mcb_lo],
        "mcb_upper": [float(x) for x in mcb_hi],
        "mcb_not_ruled_out": not_ruled_out,
        "hsu_w_upper": w_upper,
        "hsu_w_lower": w_lower,
        "hsu_lower": [float(x) for x in hsu_lo],
        "hsu_upper": [float(x) for x in hsu_hi],
        "hsu_not_ruled_out": hsu_not_ruled_out,
        "hsu_vs_band_delta": len(hsu_not_ruled_out) - len(not_ruled_out),
    }


def build_board_tile_counts(
    analysis_id: str,
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    """Load a registered leaderboard's cells as per-tile TP/FP/FN.

    Reuses ``era1_leaderboard_tiering.load_cells``, which resolves each cell from
    its own committed evaluation and reproduces the per-tile counts that eval
    scored, so the candidate set here is exactly the board the register reports.

    Args:
        analysis_id: The analysis whose ``conditions_compared`` defines the board.

    Returns:
        ``(specs, counts)`` with ``counts`` shaped ``(n_cells, n_tiles, 3)``.
    """
    from scripts.era1_leaderboard_tiering import load_cells  # noqa: PLC0415

    cells, gdf_ref, gdf_bounds, tile_order = load_cells(
        PROJECT_ROOT / "results/run-conditions.json",
        PROJECT_ROOT / "results/run-analyses.json",
        analysis_id, None, None,
    )
    specs = [{"ref": c["ref"], "label": c["label"], "eval_f1": c["eval_f1"]}
             for c in cells]
    counts = np.stack([
        np.column_stack([np.asarray(c["tp"], dtype=float),
                         np.asarray(c["fp"], dtype=float),
                         np.asarray(c["fn"], dtype=float)])
        for c in cells
    ])
    logger.info("board %s: %d cells over %d tiles", analysis_id, len(specs),
                len(tile_order))
    return specs, counts, reference_occupancy(gdf_ref, gdf_bounds, tile_order)


def build_evals_tile_counts(
    pattern: str,
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    """Load an arbitrary set of committed evaluations as per-tile TP/FP/FN.

    For candidate sets that are not a registered board — the verifier
    probability-threshold curve of erratum E56, for instance, whose operating
    points are separate evaluation directories rather than register conditions.

    Each evaluation is reproduced through
    ``era1_leaderboard_tiering.cell_per_tile``, which dispatches on the eval's own
    ``cli_args``, so the candidate scored here is the candidate that eval scored.
    Every evaluation must declare the same bounds and ground truth; a mismatch
    raises rather than silently mixing scopes.

    Args:
        pattern: Glob matching the ``evaluation.json`` files to load.

    Returns:
        ``(specs, counts)`` with ``counts`` shaped ``(n_evals, n_tiles, 3)``.
    """
    import glob as _glob  # noqa: PLC0415

    from scripts.era1_leaderboard_tiering import cell_per_tile  # noqa: PLC0415

    paths = sorted(_glob.glob(pattern))
    if not paths:
        raise ValueError(f"no evaluations matched {pattern!r}")

    metas = [(p, json.loads(Path(p).read_text())["_metadata"]) for p in paths]
    scopes = {(m["cli_args"]["bounds"], m["cli_args"]["ground_truth"]) for _, m in metas}
    if len(scopes) != 1:
        raise ValueError(f"evaluations disagree on scope: {scopes}")
    bounds_rel, gt_rel = scopes.pop()

    gdf_bounds = gpd.read_file(PROJECT_ROOT / bounds_rel).to_crs("EPSG:32635")
    gdf_ref = gpd.read_file(PROJECT_ROOT / gt_rel).to_crs("EPSG:32635")
    tile_order = list(gdf_bounds["tile_name"])

    specs, rows = [], []
    for path, meta in metas:
        tp, fp, fn, _n = cell_per_tile(meta["cli_args"], gdf_ref, gdf_bounds, tile_order)
        rows.append(np.column_stack([tp, fp, fn]).astype(float))
        doc = json.loads(Path(path).read_text())
        b20 = next((b for b in doc["summary"]["buffers"]
                    if b["buffer_metres"] == BUFFER_M), {})
        parent = Path(path).parent
        rel = (parent.relative_to(PROJECT_ROOT)
               if parent.is_absolute() and parent.is_relative_to(PROJECT_ROOT)
               else parent)
        specs.append({"ref": str(rel),
                      "label": parent.name,
                      "eval_f1": b20.get("f1")})
    logger.info("evals %s: %d candidates over %d tiles", pattern, len(specs),
                len(tile_order))
    return specs, np.stack(rows), reference_occupancy(gdf_ref, gdf_bounds, tile_order)


def main() -> int:
    """Run the pilot on one cell and report both instruments."""
    ap = argparse.ArgumentParser(
        description="Selection-aware intervals for an in-sample-optimised argmax.")
    ap.add_argument("--cell", default=None,
                    help="Grid cell whose (corroboration x vote) sweep to analyse.")
    ap.add_argument("--board", default=None,
                    help="Analysis id of a registered leaderboard to analyse instead.")
    ap.add_argument("--evals", default=None,
                    help="Glob of evaluation.json files forming the candidate set.")
    ap.add_argument("--tag", default=None, help="Output filename stem for --evals.")
    ap.add_argument("--metric", choices=("f1", "mcc"), default="f1",
                    help="Detection-level micro-F1, or registered tile-level MCC.")
    ap.add_argument("--K", type=int, default=10)
    ap.add_argument("--bootstrap", type=int, default=10000)
    ap.add_argument("--m-frac", type=float, default=1.0,
                    help="Subsample fraction; <1 enables m-out-of-n for tie robustness.")
    ap.add_argument("--out", type=Path,
                    default=PROJECT_ROOT / "results/selection-aware")
    args = ap.parse_args()
    given = [bool(args.cell), bool(args.board), bool(args.evals)]
    if sum(given) != 1:
        ap.error("give exactly one of --cell, --board or --evals")
    args.out.mkdir(parents=True, exist_ok=True)

    if args.evals:
        specs, counts, has_mounds = build_evals_tile_counts(args.evals)
        tag = args.tag or "evals"
        res_meta = {"evals_glob": args.evals}
    elif args.board:
        specs, counts, has_mounds = build_board_tile_counts(args.board)
        tag = args.board
        res_meta = {"board": args.board}
    else:
        bounds = gpd.read_file(COMMON_BOUNDS)
        gdf_ref = gpd.read_file(GROUND_TRUTH)
        specs, counts, has_mounds = build_candidate_tile_counts(
            args.cell, args.K, bounds, gdf_ref)
        logger.info("%s K=%d: %d candidates over %d carrier tiles",
                    CELL_LABEL.get(args.cell, args.cell), args.K, len(specs),
                    len(bounds))
        tag = f"{args.cell}_K{args.K}"
        res_meta = {"cell": args.cell, "label": CELL_LABEL.get(args.cell, args.cell),
                    "K": args.K}

    res = run(counts, args.bootstrap, args.m_frac, SEED,
              has_mounds=has_mounds, metric=args.metric)
    res.update(res_meta)
    res.update({"m_frac": args.m_frac, "candidates": specs, "seed": SEED,
                "buffer_metres": BUFFER_M})

    kept = res["kept_indices"]
    specs = [specs[i] for i in kept]
    if res["n_candidates_dropped_undefined"]:
        logger.info("dropped %d candidate(s) with an undefined %s (E81)",
                    res["n_candidates_dropped_undefined"], args.metric)
    s = specs[res["selected_index"]]
    logger.info("selected: %s", s.get("label") or
                f"c>={s.get('min_corroboration')} k>={s.get('min_votes')}")
    logger.info("apparent %-4s          : %.4f", args.metric, res["apparent_f1"])
    logger.info("optimism (selection)   : %+.4f  (MC s.e. %.5f; per-resample "
                "spread [%+.4f, %+.4f])", res["optimism"], res["optimism_mcse"],
                *res["optimism_spread_p2_5_p97_5"])
    logger.info("corrected %-4s         : %.4f", args.metric, res["corrected_f1"])
    logger.info("naive CI95             : [%.4f, %.4f]", *res["naive_ci"])
    logger.info("selection-aware CI95   : [%.4f, %.4f]", *res["selection_aware_ci"])
    logger.info("argmax stability       : %.3f (%d distinct winners across resamples)",
                res["argmax_stability"], res["n_distinct_argmax"])
    logger.info("MCB two-sided band : %d of %d admissible (w=%.4f)",
                len(res["mcb_not_ruled_out"]), res["n_candidates"],
                res["mcb_critical_width"])
    logger.info("MCB Hsu constrained: %d of %d admissible "
                "(w_upper=%.4f, w_lower=%.4f)",
                len(res["hsu_not_ruled_out"]), res["n_candidates"],
                res["hsu_w_upper"], res["hsu_w_lower"])
    for i in res["hsu_not_ruled_out"]:
        c = specs[i]
        name = c.get("label") or f"c>={c.get('min_corroboration')} k>={c.get('min_votes')}"
        logger.info("    %-38s theta=%+.4f  [%+.4f, %+.4f]", name,
                    res["mcb_theta"][i], res["mcb_lower"][i], res["mcb_upper"][i])

    suffix = "" if args.metric == "f1" else f"_{args.metric}"
    out = args.out / f"{tag}{suffix}_m{args.m_frac:g}.json"
    out.write_text(json.dumps(res, indent=2))
    logger.info("wrote %s", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
