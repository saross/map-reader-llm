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

    python scripts/selection_aware_intervals.py --cell g512_ov256 --K 10 \\
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


def build_candidate_tile_counts(
    cell: str, k_total: int, bounds: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
) -> tuple[list[dict[str, int]], np.ndarray]:
    """Score every (corroboration, vote) candidate to per-tile TP/FP/FN.

    Args:
        cell: Grid cell label.
        k_total: Pass budget K; the first K passes are used, matching the sweep.
        bounds: Carrier tile bounds, which fix tile order.
        gdf_ref: Ground-truth references.

    Returns:
        ``(specs, counts)`` where ``specs`` names each candidate and ``counts``
        has shape ``(n_candidates, n_tiles, 3)`` in TP/FP/FN order.
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
    return specs, np.stack(rows)


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


def resample_weights(rng: np.random.Generator, n: int, m: int) -> np.ndarray:
    """Draw one tile resample as a multiplicity vector (m draws from n tiles)."""
    return np.bincount(rng.integers(0, n, size=m), minlength=n).astype(float)


def run(counts: np.ndarray, b: int, m_frac: float, seed: int) -> dict[str, Any]:
    """Selection-aware bootstrap plus bootstrap MCB over one candidate set.

    Args:
        counts: ``(n_candidates, n_tiles, 3)`` per-tile counts.
        b: Bootstrap resamples.
        m_frac: Subsample size as a fraction of n (1.0 = ordinary n-out-of-n).
        seed: RNG seed.

    Returns:
        A dict of results; see the module docstring for interpretation.
    """
    rng = np.random.default_rng(seed)
    n_cand, n_tiles, _ = counts.shape
    m = max(1, int(round(m_frac * n_tiles)))

    f1_full = f1_from_counts(counts)
    k_star = int(np.argmax(f1_full))
    apparent = float(f1_full[k_star])

    # theta_i = F1_i - max_{j != i} F1_j, the MCB quantity.
    def theta(f: np.ndarray) -> np.ndarray:
        order = np.argsort(f)[::-1]
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
        f = f1_from_counts(counts, w)
        boot_f1[i] = f
        boot_theta[i] = theta(f)
        kb = int(np.argmax(f))
        sel[i] = kb
        # Efron-Gong optimism with the argmax REPLAYED: the winner inside this
        # resample, scored in-resample, against that same winner scored on the
        # full data. The comparator is held fixed by construction.
        optimism[i] = f[kb] - f1_full[kb]

    opt = float(optimism.mean())
    # The SPREAD of per-resample optimism is not the uncertainty on its MEAN.
    # Report both: the spread describes how variable the selection penalty is
    # from resample to resample, while the Monte Carlo standard error says how
    # well B resamples pin the estimate down. Quoting the spread alone would
    # make a well-determined optimism look unmeasurable.
    opt_mcse = float(optimism.std(ddof=1) / np.sqrt(len(optimism)))
    corrected = apparent - opt

    # Naive interval for k*, then the same interval location-shifted by the
    # measured optimism. The shift is what makes it a post-selection interval.
    naive_lo, naive_hi = np.percentile(boot_f1[:, k_star], [2.5, 97.5])
    shifted = (float(naive_lo - opt), float(naive_hi - opt))

    # Bootstrap MCB: one critical width from the distribution of the maximum
    # absolute deviation, so coverage is simultaneous across candidates.
    dev = np.abs(boot_theta - theta_full[None, :])
    crit = float(np.percentile(dev.max(axis=1), 95))
    mcb_lo = theta_full - crit
    mcb_hi = theta_full + crit
    not_ruled_out = [i for i in range(n_cand) if mcb_hi[i] >= 0]

    sel_counts = np.bincount(sel, minlength=n_cand)
    return {
        "n_candidates": n_cand,
        "n_tiles": n_tiles,
        "m_out_of_n": m,
        "bootstrap": b,
        "selected_index": k_star,
        "apparent_f1": apparent,
        "optimism": opt,
        "optimism_mcse": opt_mcse,
        "optimism_spread_p2_5_p97_5": [float(x) for x in np.percentile(optimism, [2.5, 97.5])],
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
    }


def main() -> int:
    """Run the pilot on one cell and report both instruments."""
    ap = argparse.ArgumentParser(
        description="Selection-aware intervals for an in-sample-optimised argmax.")
    ap.add_argument("--cell", default="g512_ov256")
    ap.add_argument("--K", type=int, default=10)
    ap.add_argument("--bootstrap", type=int, default=10000)
    ap.add_argument("--m-frac", type=float, default=1.0,
                    help="Subsample fraction; <1 enables m-out-of-n for tie robustness.")
    ap.add_argument("--out", type=Path,
                    default=PROJECT_ROOT / "results/selection-aware")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    bounds = gpd.read_file(COMMON_BOUNDS)
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    specs, counts = build_candidate_tile_counts(args.cell, args.K, bounds, gdf_ref)
    logger.info("%s K=%d: %d candidates over %d carrier tiles",
                CELL_LABEL.get(args.cell, args.cell), args.K, len(specs), len(bounds))

    res = run(counts, args.bootstrap, args.m_frac, SEED)
    res.update({"cell": args.cell, "label": CELL_LABEL.get(args.cell, args.cell),
                "K": args.K, "m_frac": args.m_frac,
                "candidates": specs, "seed": SEED, "buffer_metres": BUFFER_M})

    s = specs[res["selected_index"]]
    logger.info("selected: c>=%d k>=%d", s["min_corroboration"], s["min_votes"])
    logger.info("apparent F1            : %.4f", res["apparent_f1"])
    logger.info("optimism (selection)   : %+.4f  (MC s.e. %.5f; per-resample "
                "spread [%+.4f, %+.4f])", res["optimism"], res["optimism_mcse"],
                *res["optimism_spread_p2_5_p97_5"])
    logger.info("corrected F1           : %.4f", res["corrected_f1"])
    logger.info("naive CI95             : [%.4f, %.4f]", *res["naive_ci"])
    logger.info("selection-aware CI95   : [%.4f, %.4f]", *res["selection_aware_ci"])
    logger.info("argmax stability       : %.3f (%d distinct winners across resamples)",
                res["argmax_stability"], res["n_distinct_argmax"])
    logger.info("MCB: %d of %d candidates cannot be ruled out as best "
                "(simultaneous 95%%, critical width %.4f)",
                len(res["mcb_not_ruled_out"]), res["n_candidates"],
                res["mcb_critical_width"])
    for i in res["mcb_not_ruled_out"]:
        c = specs[i]
        logger.info("    c>=%d k>=%2d  theta=%+.4f  [%+.4f, %+.4f]",
                    c["min_corroboration"], c["min_votes"], res["mcb_theta"][i],
                    res["mcb_lower"][i], res["mcb_upper"][i])

    out = args.out / f"{args.cell}_K{args.K}_m{args.m_frac:g}.json"
    out.write_text(json.dumps(res, indent=2))
    logger.info("wrote %s", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
