#!/usr/bin/env python3
"""
Tile size x overlap: the 2x2, the K ladder, and the aggregation sweep.

Scores the four cells of the 2026-08-18 post-hoc grid (E41-class) prepared by
``scripts/grid_prepare_scoring.py`` — 384 px and 512 px tiles crossed with
12.5 % and 50 % overlap, n = 10 proposer passes each, one configuration
throughout — and answers the four questions the grid was run to settle:

1. **The 2x2.** Precision, recall, F1 and tile-level Matthews Correlation
   Coefficient (MCC) per cell at single-pass, so tile size, overlap and their
   interaction can be read off directly. An *undefined* MCC (a degenerate tile
   confusion matrix, i.e. a vanishing marginal) is reported as ``null``, never
   as ``0.0`` — coercing it to zero publishes "no discrimination" where the
   truth is "not measurable" (erratum E81).

2. **Do passes substitute for overlap?** A K ladder (K = 1, 3, 5, 10) per cell,
   sub-sampled from the same ten passes, comparing the union-recall ceiling and
   the best achievable F1. Earlier work suggested 384 px / 12.5 % at K = 10
   reached a higher recall ceiling than 512 px / 50 % at K = 3 for less money,
   but that comparison was scope-confounded. Here every cell sits on one
   footprint, so the comparison is clean.

3. **Corroboration x consensus.** The cross-tile corroboration filter (``c``,
   requiring a detection to be reported by ``c`` overlapping tiles within one
   pass) is a precision lever that exists ONLY where tiles overlap, so it is
   confounded with the factor under test by construction; it is swept jointly
   with across-pass consensus (``k``) so a like-for-like comparison exists at
   every filter strength.

4. **Cost-efficiency.** F1 per flex-discounted API dollar, and the marginal F1
   bought by each step in tiles or passes.

**Bootstrap.** Contrasts use the project's registered instrument (Decision 10):
per-tile resampling with replacement on the common carrier grid, seed 42,
percentile CI95, two-sided ``p = max(2 * min tail, 1/B)``, B = 1,000. Draws are
*paired* — one index sample applied to both arms of a contrast — which is what
the shared footprint buys. The 2x2 interaction is a difference-of-differences
on the same paired draw.

**Consensus-only.** This is the proposer stage. A proposer-verifier board needs
a verifier pass (API spend, separate gate); it is COSTED here, not run.

Usage::

    python scripts/grid_analysis.py \\
        --scoring-dir outputs/grid-2026-08-18/scoring \\
        --output-dir results/grid-2026-08-18

Inputs:
    - outputs/grid-2026-08-18/scoring/common/<cell>/run_N/detections_dedup.geojson
    - outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson
    - outputs/grid-2026-08-18/scoring/prepare_summary.json
    - outputs/grid-2026-08-18/<cell>/run_*/**.meta.json (audited spend)
    - inputs/vectors/references/mounds-reference.geojson
    - results/verifier-robustness/pareto/pareto_v2.json (verifier per-call rate)

Outputs (under ``--output-dir``):
    - grid_analysis.json  - every number below, machine-readable
    - per_tile_counts.json - run-averaged per-tile TP/FP/FN (bootstrap input)
    - sweep.csv           - the full corroboration x consensus x K sweep

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_prepare_scoring import CELLS, GRID_ROOT, N_PASSES  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.h13_overlap_analysis import micro_f1, paired_bootstrap  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    calculate_tile_classification,
    compute_per_tile_tp_fp_fn,
    score_detection_set,
)
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BUFFER_M = 20
CRS = "EPSG:32635"
SEED = 42
N_BOOTSTRAP = 1000

#: Corroboration levels swept. c = 1 is no filter.
CORROBORATION = (1, 2, 3)

#: Pass counts sub-sampled from the ten committed passes.
K_LADDER = (1, 3, 5, 10)

GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"

#: Per-verifier-call rate, measured at Gemini flex rates in the 2026-06-12
#: token-load audit and pinned in the Pareto cost model.
PARETO_V2 = PROJECT_ROOT / "results/verifier-robustness/pareto/pareto_v2.json"

#: Gemini real-time flex carries the same 50 % discount as the async Batch API.
#: The ``cost_estimate`` blocks written into ``*.meta.json`` are list price and
#: do NOT apply it, so every dollar figure here divides them by this factor.
FLEX_DISCOUNT_DIVISOR = 2.0

#: Display labels, in 2x2 reading order.
CELL_ORDER = ("g512_ov064", "g512_ov256", "g384_ov048", "g384_ov192")
CELL_LABEL = {
    "g512_ov064": "512 px / 12.5 %",
    "g512_ov256": "512 px / 50 %",
    "g384_ov048": "384 px / 12.5 %",
    "g384_ov192": "384 px / 50 %",
}


def load_cell_passes(scoring_dir: Path, cell: str, scope: str = "common") -> list[list[dict]]:
    """Load one cell's deduplicated passes in run order.

    Args:
        scoring_dir: Root of the prepared scoring artefacts.
        cell: Cell label.
        scope: ``common`` (the shared carrier grid) or ``native``.

    Returns:
        One detection list per pass, in ``run_1`` .. ``run_10`` order. Each
        detection carries ``centroid``, ``label``, ``source_tiles`` and the
        within-pass ``cluster_size`` the corroboration filter reads.

    Raises:
        FileNotFoundError: If a pass file is missing.
    """
    passes: list[list[dict]] = []
    for i in range(1, N_PASSES + 1):
        path = scoring_dir / scope / cell / f"run_{i}" / "detections_dedup.geojson"
        if not path.exists():
            raise FileNotFoundError(f"Prepared pass missing: {path}")
        data = json.loads(path.read_text())
        passes.append([
            {
                "centroid": tuple(f["geometry"]["coordinates"]),
                "label": f["properties"].get("label", "mound"),
                "source_tiles": (f["properties"].get("origin_tiles") or "").split(";"),
                "cluster_size": int(f["properties"].get("cluster_size", 1)),
            }
            for f in data["features"]
        ])
    return passes


def as_gdf(centroids: np.ndarray, bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Wrap cluster centroids as a scorable GeoDataFrame on the carrier grid.

    Args:
        centroids: Array of shape (n, 2) in the project CRS.
        bounds: Carrier tile bounds with a ``tile_name`` column.

    Returns:
        GeoDataFrame with a ``source_tile`` column; rows that fall on no
        carrier tile are dropped (they cannot be scored or booked to a tile).
    """
    if len(centroids) == 0:
        return gpd.GeoDataFrame({"source_tile": []}, geometry=[], crs=CRS)
    gdf = gpd.GeoDataFrame(geometry=[Point(xy) for xy in centroids], crs=CRS)
    gdf["source_tile"] = assign_primary_tiles(gdf, bounds)
    return gdf[gdf["source_tile"].notna()].copy()


def score(
    gdf_det: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
) -> dict[str, Any]:
    """Score one detection set, keeping an undefined MCC undefined.

    Thin wrapper over :func:`scripts.lib_advanced_metrics.score_detection_set`,
    which already returns ``None`` for a degenerate tile confusion matrix. The
    wrapper exists to make that contract explicit at the call site: nothing in
    this analysis may publish an undefined MCC as ``0.0`` (erratum E81).

    Args:
        gdf_det: Detections with a ``source_tile`` column.
        gdf_ref: Ground-truth references.
        bounds: Carrier tile bounds.

    Returns:
        ``{"f1", "precision", "recall", "n_detections", "mcc"}`` with ``mcc``
        possibly ``None``.
    """
    result = score_detection_set(gdf_det, gdf_ref, bounds, buffer_metres=BUFFER_M)
    return {
        "precision": result["precision"],
        "recall": result["recall"],
        "f1": result["f1"],
        "n_detections": result["n_detections"],
        "mcc": None if result["mcc"] is None else float(result["mcc"]),
    }


def single_pass_table(
    cell_passes: dict[str, list[list[dict]]],
    bounds: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
) -> dict[str, Any]:
    """Score every pass of every cell individually and summarise per cell.

    Single-pass is the cleanest read of the geometry factors: no aggregation
    stage sits between the tiling and the metric.

    Args:
        cell_passes: Cell label -> per-pass detection lists.
        bounds: Carrier tile bounds.
        gdf_ref: Ground-truth references.

    Returns:
        Cell label -> summary with per-pass rows, means, standard deviations,
        and the count of passes whose MCC was undefined.
    """
    out: dict[str, Any] = {}
    for cell in CELL_ORDER:
        rows = []
        for i, dets in enumerate(cell_passes[cell], start=1):
            gdf = as_gdf(np.asarray([d["centroid"] for d in dets], dtype=float), bounds)
            row = score(gdf, gdf_ref, bounds)
            # The tile confusion matrix is what makes an MCC readable at all —
            # without it a low MCC cannot be told apart from a degenerate one.
            tile_class = calculate_tile_classification(gdf, gdf_ref, bounds)
            row["tile_classification"] = {
                k: tile_class[k] for k in
                ("tp", "tn", "fp", "fn", "sensitivity", "specificity",
                 "n_tiles", "n_populated", "n_empty")
            }
            row["run"] = f"run_{i}"
            rows.append(row)

        def _mean(key: str) -> float:
            return float(np.mean([r[key] for r in rows]))

        def _sd(key: str) -> float:
            return float(np.std([r[key] for r in rows], ddof=1))

        defined_mcc = [r["mcc"] for r in rows if r["mcc"] is not None]
        tile_keys = ("tp", "tn", "fp", "fn", "sensitivity", "specificity")
        out[cell] = {
            "label": CELL_LABEL[cell],
            "tile_px": CELLS[cell]["tile_px"],
            "overlap_frac": CELLS[cell]["overlap_frac"],
            "passes": rows,
            "mean": {k: _mean(k) for k in ("precision", "recall", "f1", "n_detections")},
            "sd": {k: _sd(k) for k in ("precision", "recall", "f1", "n_detections")},
            "tile_classification_mean": {
                k: float(np.mean([r["tile_classification"][k] for r in rows]))
                for k in tile_keys
            },
            "tile_classification_constant": {
                k: rows[0]["tile_classification"][k]
                for k in ("n_tiles", "n_populated", "n_empty")
            },
            "mcc_mean": float(np.mean(defined_mcc)) if defined_mcc else None,
            "mcc_sd": (float(np.std(defined_mcc, ddof=1))
                       if len(defined_mcc) > 1 else None),
            "n_passes_mcc_undefined": len(rows) - len(defined_mcc),
        }
        logger.info(
            "%-16s single pass: P=%.4f R=%.4f F1=%.4f MCC=%s (n=%.0f dets)",
            CELL_LABEL[cell], out[cell]["mean"]["precision"],
            out[cell]["mean"]["recall"], out[cell]["mean"]["f1"],
            "undefined" if out[cell]["mcc_mean"] is None
            else f"{out[cell]['mcc_mean']:.4f}",
            out[cell]["mean"]["n_detections"],
        )
    return out


def corroboration_profile(cell_passes: dict[str, list[list[dict]]]) -> dict[str, Any]:
    """Measure how much cross-tile corroboration each cell's geometry affords.

    ``cluster_size`` is the number of raw detections the within-pass 20 m
    deduplication merged into one cluster, i.e. the number of overlapping tiles
    that independently reported the same location. It is the mechanism behind
    the ``c`` filter, and it exists only where tiles overlap — which is why the
    filter is confounded with the factor under test and must be swept rather
    than fixed.

    Args:
        cell_passes: Cell label -> per-pass detection lists.

    Returns:
        Cell label -> share of deduplicated detections at each cluster size
        (sizes 4 and above pooled), plus the share corroborated at all.
    """
    out: dict[str, Any] = {}
    for cell in CELL_ORDER:
        sizes = [min(d["cluster_size"], 4)
                 for dets in cell_passes[cell] for d in dets]
        total = len(sizes)
        counts = {str(s): sizes.count(s) / total for s in (1, 2, 3, 4)}
        counts["4+"] = counts.pop("4")
        out[cell] = {
            "label": CELL_LABEL[cell],
            "share_by_cluster_size": counts,
            "share_corroborated": 1.0 - counts["1"],
            "n_detections_pooled": total,
        }
        logger.info(
            "%-16s corroboration: %.1f %% of deduplicated detections were seen "
            "by 2+ overlapping tiles",
            CELL_LABEL[cell], 100 * out[cell]["share_corroborated"],
        )
    return out


def build_per_tile(
    cell_passes: dict[str, list[list[dict]]],
    bounds: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
) -> dict[str, dict[str, np.ndarray]]:
    """Build run-averaged per-tile TP/FP/FN arrays on the carrier grid.

    Averaging counts across the cell's ten passes before resampling keeps the
    resampling unit the tile rather than the pass, which is what Decision 10
    registers, and matches the H13 chain
    (``scripts/h13_overlap_analysis.build_per_tile``).

    Args:
        cell_passes: Cell label -> per-pass detection lists.
        bounds: Carrier tile bounds (defines tile order).
        gdf_ref: Ground-truth references.

    Returns:
        Cell label -> ``{"tp", "fp", "fn"}`` float arrays aligned with
        ``bounds['tile_name']`` order.
    """
    tile_order = list(bounds["tile_name"])
    out: dict[str, dict[str, np.ndarray]] = {}
    for cell in CELL_ORDER:
        acc = {k: np.zeros(len(tile_order)) for k in ("tp", "fp", "fn")}
        for dets in cell_passes[cell]:
            gdf = as_gdf(np.asarray([d["centroid"] for d in dets], dtype=float), bounds)
            tm = compute_per_tile_tp_fp_fn(gdf, gdf_ref, bounds, buffer_metres=BUFFER_M)
            tm = tm.set_index("tile_name").reindex(tile_order).fillna(0)
            for k in ("tp", "fp", "fn"):
                acc[k] += tm[k].to_numpy(dtype=float)
        out[cell] = {k: v / N_PASSES for k, v in acc.items()}
        p, r, f = micro_f1(*(out[cell][k].sum() for k in ("tp", "fp", "fn")))
        logger.info(
            "%-16s pooled per-tile: TP=%.1f FP=%.1f FN=%.1f -> micro-F1=%.4f "
            "(P=%.4f R=%.4f)",
            CELL_LABEL[cell], out[cell]["tp"].sum(), out[cell]["fp"].sum(),
            out[cell]["fn"].sum(), f, p, r,
        )
    return out


def paired_interaction(
    a: dict[str, np.ndarray], b: dict[str, np.ndarray],
    c: dict[str, np.ndarray], d: dict[str, np.ndarray],
    n_iter: int = N_BOOTSTRAP, seed: int = SEED,
) -> dict[str, Any]:
    """Paired difference-of-differences bootstrap for the 2x2 interaction.

    Computes ``(F1(a) - F1(b)) - (F1(c) - F1(d))`` under one shared tile index
    draw per iteration, so all four cells are resampled together and the
    contrast isolates the interaction from between-tile heterogeneity.

    Args:
        a: Per-tile counts, first factor level, first level of the second factor.
        b: Per-tile counts, first factor level, second level of the second factor.
        c: Per-tile counts, second factor level, first level of the second factor.
        d: Per-tile counts, second factor level, second level of the second factor.
        n_iter: Bootstrap iterations.
        seed: Random seed.

    Returns:
        Dict with the observed difference-of-differences, percentile CI95,
        bootstrap mean, two-sided p-value and a CI-excludes-zero flag.
    """
    n = len(a["tp"])
    rng = np.random.default_rng(seed)

    def _f1(counts: dict[str, np.ndarray], idx: np.ndarray | None = None) -> float:
        if idx is None:
            return micro_f1(*(counts[k].sum() for k in ("tp", "fp", "fn")))[2]
        return micro_f1(*(counts[k][idx].sum() for k in ("tp", "fp", "fn")))[2]

    obs = (_f1(a) - _f1(b)) - (_f1(c) - _f1(d))

    dods = np.empty(n_iter)
    for i in range(n_iter):
        idx = rng.integers(0, n, n)
        dods[i] = (_f1(a, idx) - _f1(b, idx)) - (_f1(c, idx) - _f1(d, idx))

    below = float((dods <= 0).sum()) / n_iter
    above = float((dods >= 0).sum()) / n_iter
    lower = float(np.percentile(dods, 2.5))
    upper = float(np.percentile(dods, 97.5))
    return {
        "difference_of_differences": float(obs),
        "ci_lower": lower,
        "ci_upper": upper,
        "bootstrap_mean": float(dods.mean()),
        "p_two_sided": float(max(2 * min(below, above), 1.0 / n_iter)),
        "n_iterations": n_iter,
        "seed": seed,
        "excludes_zero": bool(lower > 0 or upper < 0),
    }


def sweep(
    cell_passes: dict[str, list[list[dict]]],
    bounds: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
) -> list[dict[str, Any]]:
    """Sweep every cell over K x corroboration x consensus.

    For each K the FIRST K passes are used, so the K ladder is nested: K = 3 is
    a strict subset of K = 5, which is a strict subset of K = 10. Clustering is
    done once per (cell, K, c) and every vote threshold reads off the same
    clustering, so a cluster cannot change membership as the threshold moves.

    Args:
        cell_passes: Cell label -> per-pass detection lists.
        bounds: Carrier tile bounds.
        gdf_ref: Ground-truth references.

    Returns:
        One row per (cell, K, c, k) with precision, recall, F1, MCC and the
        surviving detection count.
    """
    rows: list[dict[str, Any]] = []
    for cell in CELL_ORDER:
        passes = cell_passes[cell]
        for k_total in K_LADDER:
            subset = passes[:k_total]
            for c in CORROBORATION:
                centroids, votes = cluster_votes(subset, c)
                for k in range(1, k_total + 1):
                    sel = votes >= k
                    gdf = as_gdf(centroids[sel], bounds)
                    row = score(gdf, gdf_ref, bounds)
                    row.update({
                        "cell": cell, "label": CELL_LABEL[cell],
                        "tile_px": CELLS[cell]["tile_px"],
                        "overlap_frac": CELLS[cell]["overlap_frac"],
                        "K": k_total, "min_corroboration": c, "min_votes": k,
                    })
                    rows.append(row)
            best = max((r for r in rows if r["cell"] == cell and r["K"] == k_total),
                       key=lambda x: x["f1"])
            union = next(r for r in rows if r["cell"] == cell and r["K"] == k_total
                         and r["min_corroboration"] == 1 and r["min_votes"] == 1)
            logger.info(
                "%-16s K=%2d: union recall %.4f (n=%d) | best F1=%.4f at "
                "c>=%d k>=%d (%s)",
                CELL_LABEL[cell], k_total, union["recall"], union["n_detections"],
                best["f1"], best["min_corroboration"], best["min_votes"],
                "interior" if best["min_votes"] < k_total else "grid edge",
            )
    return rows


def audited_costs() -> dict[str, Any]:
    """Sum audited API spend per cell and restate it on the flex-discounted basis.

    Every ``*.meta.json`` under a cell — including the additive one-tile
    recovery passes — contributes its ``cost_estimate.total_cost_usd`` and its
    ``execution_stats.items_processed``. Those blocks are LIST price; Gemini
    real-time flex carries the same 50 % discount as the async Batch API, so
    the discounted figure is the billed one and is what every dollar in this
    analysis uses.

    Returns:
        Dict with per-cell and total calls, list-price spend, flex-discounted
        spend, and the per-call rate.
    """
    per_cell: dict[str, Any] = {}
    total_calls = 0
    total_list = 0.0
    for cell in CELL_ORDER:
        calls = 0
        list_usd = 0.0
        for meta in sorted((GRID_ROOT / cell).glob("run_*/*.meta.json")):
            data = json.loads(meta.read_text())
            calls += int(data["execution_stats"]["items_processed"])
            list_usd += float(data["cost_estimate"]["total_cost_usd"])
        flex = list_usd / FLEX_DISCOUNT_DIVISOR
        per_cell[cell] = {
            "label": CELL_LABEL[cell],
            "tiles_per_pass": len(json.loads(CELLS[cell]["manifest"].read_text())),
            "calls": calls,
            "list_price_usd": list_usd,
            "flex_usd": flex,
            "flex_usd_per_call": flex / calls if calls else None,
            "flex_usd_per_pass": flex / N_PASSES,
        }
        total_calls += calls
        total_list += list_usd
        logger.info(
            "%-16s %6d calls, list $%.4f, flex $%.4f ($%.6f/call)",
            CELL_LABEL[cell], calls, list_usd, flex, flex / calls,
        )
    return {
        "per_cell": per_cell,
        "total_calls": total_calls,
        "total_list_price_usd": total_list,
        "total_flex_usd": total_list / FLEX_DISCOUNT_DIVISOR,
        "flex_discount_divisor": FLEX_DISCOUNT_DIVISOR,
        "note": (
            "cost_estimate blocks in *.meta.json are undiscounted list price; "
            "Gemini real-time flex carries the same 50 % discount as the async "
            "Batch API, so the flex column is the billed basis."
        ),
    }


def cost_efficiency(
    sweep_rows: list[dict[str, Any]], costs: dict[str, Any],
) -> dict[str, Any]:
    """Build the iso-spend frontier: what each cell buys at each pass count.

    Spend for K passes of a cell is K times that cell's audited flex cost per
    pass. The per-pass figure divides the cell's audited total (including its
    additive one-tile recovery passes, which are a few tenths of a cent) by
    ten, so it is the billed basis rather than a nominal tiles-times-rate
    estimate.

    Args:
        sweep_rows: The full K x c x k sweep.
        costs: Audited spend from :func:`audited_costs`.

    Returns:
        Dict with one frontier row per (cell, K) and the explicit
        passes-versus-overlap head-to-head the grid was run to settle.
    """
    frontier = []
    for cell in CELL_ORDER:
        per_pass = costs["per_cell"][cell]["flex_usd_per_pass"]
        tiles = costs["per_cell"][cell]["tiles_per_pass"]
        for k_total in K_LADDER:
            rows = [r for r in sweep_rows if r["cell"] == cell and r["K"] == k_total]
            best = max(rows, key=lambda x: x["f1"])
            union = next(r for r in rows if r["min_corroboration"] == 1
                         and r["min_votes"] == 1)
            spend = k_total * per_pass
            frontier.append({
                "cell": cell, "label": CELL_LABEL[cell], "K": k_total,
                "calls": k_total * tiles,
                "flex_usd": spend,
                "union_recall": union["recall"],
                "best_f1": best["f1"],
                "best_precision": best["precision"],
                "best_recall": best["recall"],
                "best_mcc": best["mcc"],
                "best_min_corroboration": best["min_corroboration"],
                "best_min_votes": best["min_votes"],
                "best_f1_per_flex_usd": best["f1"] / spend if spend else None,
            })

    def _row(cell: str, k_total: int) -> dict[str, Any]:
        return next(r for r in frontier if r["cell"] == cell and r["K"] == k_total)

    challenger = _row("g384_ov048", 10)
    incumbent = _row("g512_ov256", 3)
    head_to_head = {
        "question": (
            "Do extra passes substitute for extra overlap? Earlier, "
            "scope-confounded work suggested 384 px / 12.5 % at K = 10 reached a "
            "higher union-recall ceiling than 512 px / 50 % at K = 3 for less "
            "money. On one footprint this grid can settle it."
        ),
        "more_passes_less_overlap": challenger,
        "fewer_passes_more_overlap": incumbent,
        "delta_union_recall": challenger["union_recall"] - incumbent["union_recall"],
        "delta_best_f1": challenger["best_f1"] - incumbent["best_f1"],
        "delta_flex_usd": challenger["flex_usd"] - incumbent["flex_usd"],
        "verdict": (
            "passes substitute for overlap"
            if (challenger["union_recall"] > incumbent["union_recall"]
                and challenger["flex_usd"] <= incumbent["flex_usd"])
            else "passes do NOT substitute for overlap"
        ),
    }
    return {"frontier": frontier, "passes_versus_overlap": head_to_head}


def verifier_costing(sweep_rows: list[dict[str, Any]], costs: dict[str, Any]) -> dict[str, Any]:
    """Cost — but do not run — a proposer-verifier stage on this grid.

    A verifier pass scores one crop per surviving proposer candidate, so the
    cost of adding it to any operating point is that point's candidate count
    times the measured per-call rate.

    Args:
        sweep_rows: The full sweep, for candidate counts.
        costs: Audited proposer spend from :func:`audited_costs`.

    Returns:
        Dict with the per-call rate, its provenance, and a per-cell costing at
        the K = 10 union (the largest candidate pool, i.e. the upper bound) and
        at each cell's best consensus-only operating point.
    """
    pareto = json.loads(PARETO_V2.read_text())
    vf_call_usd = float(pareto["cost_model"]["vf_call_usd"])

    options = []
    for cell in CELL_ORDER:
        rows_k10 = [r for r in sweep_rows if r["cell"] == cell and r["K"] == 10]
        union = next(r for r in rows_k10 if r["min_corroboration"] == 1
                     and r["min_votes"] == 1)
        best = max(rows_k10, key=lambda x: x["f1"])
        for name, row in (("K10 union (c>=1, k>=1)", union),
                          ("K10 best consensus-only", best)):
            options.append({
                "cell": cell,
                "label": CELL_LABEL[cell],
                "operating_point": name,
                "min_corroboration": row["min_corroboration"],
                "min_votes": row["min_votes"],
                "n_candidates": row["n_detections"],
                "consensus_only_f1": row["f1"],
                "verifier_calls": row["n_detections"],
                "verifier_usd": row["n_detections"] * vf_call_usd,
                "proposer_flex_usd": costs["per_cell"][cell]["flex_usd"],
            })
    return {
        "vf_call_usd": vf_call_usd,
        "basis": pareto["cost_model"]["basis"],
        "source": "results/verifier-robustness/pareto/pareto_v2.json",
        "status": "COSTED, NOT RUN — the verifier stage is a separate spend gate.",
        "options": options,
    }


def main() -> int:
    """Run every analysis and write the JSON, CSV and per-tile artefacts.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="Tile size x overlap grid: 2x2, K ladder, aggregation sweep.")
    parser.add_argument(
        "--scoring-dir", type=Path, default=GRID_ROOT / "scoring",
        help="Root of the prepared scoring artefacts.")
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results/grid-2026-08-18",
        help="Directory for the analysis outputs.")
    parser.add_argument("--bootstrap", type=int, default=N_BOOTSTRAP)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    bounds = gpd.read_file(args.scoring_dir / "bounds" / "grid_common_bounds.geojson")
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    prepare = json.loads((args.scoring_dir / "prepare_summary.json").read_text())
    logger.info("common carrier grid: %d tiles", len(bounds))

    cell_passes = {cell: load_cell_passes(args.scoring_dir, cell)
                   for cell in CELL_ORDER}

    singles = single_pass_table(cell_passes, bounds, gdf_ref)
    corroboration = corroboration_profile(cell_passes)
    per_tile = build_per_tile(cell_passes, bounds, gdf_ref)

    # Simple effects and the interaction, all on one paired instrument.
    contrasts = {
        "overlap_at_512px (12.5% - 50%)": ("g512_ov064", "g512_ov256"),
        "overlap_at_384px (12.5% - 50%)": ("g384_ov048", "g384_ov192"),
        "tilesize_at_12.5pct (384 - 512)": ("g384_ov048", "g512_ov064"),
        "tilesize_at_50pct (384 - 512)": ("g384_ov192", "g512_ov256"),
    }
    bootstrap = {
        name: paired_bootstrap(per_tile[a], per_tile[b], args.bootstrap, seed=SEED)
        for name, (a, b) in contrasts.items()
    }
    interaction = paired_interaction(
        per_tile["g512_ov064"], per_tile["g512_ov256"],
        per_tile["g384_ov048"], per_tile["g384_ov192"],
        n_iter=args.bootstrap, seed=SEED,
    )
    for name, res in bootstrap.items():
        logger.info("%-34s dF1=%+.4f CI95 [%+.4f, %+.4f] p=%.4f %s",
                    name, res["delta"], res["ci_lower"], res["ci_upper"],
                    res["p_two_sided"],
                    "EXCLUDES 0" if res["excludes_zero"] else "includes 0")
    logger.info(
        "interaction (overlap effect at 512 - at 384) = %+.4f CI95 "
        "[%+.4f, %+.4f] p=%.4f %s",
        interaction["difference_of_differences"], interaction["ci_lower"],
        interaction["ci_upper"], interaction["p_two_sided"],
        "EXCLUDES 0" if interaction["excludes_zero"] else "includes 0")

    sweep_rows = sweep(cell_passes, bounds, gdf_ref)
    costs = audited_costs()
    efficiency = cost_efficiency(sweep_rows, costs)
    pv = verifier_costing(sweep_rows, costs)

    # Erratum E81: an undefined MCC is a degenerate tile confusion matrix, not
    # zero discrimination. Surface the affected cells explicitly so no reader
    # has to infer the difference from a missing value.
    undefined_mcc = [
        {k: r[k] for k in ("cell", "K", "min_corroboration", "min_votes",
                           "n_detections", "f1")}
        for r in sweep_rows if r["mcc"] is None
    ]
    logger.info(
        "%d of %d swept cells have an UNDEFINED tile MCC (reported as null, "
        "never as 0.0)", len(undefined_mcc), len(sweep_rows),
    )
    logger.info(
        "passes-versus-overlap: %s (384/12.5%% K=10 union recall %.4f at "
        "$%.4f vs 512/50%% K=3 %.4f at $%.4f)",
        efficiency["passes_versus_overlap"]["verdict"],
        efficiency["passes_versus_overlap"]["more_passes_less_overlap"]["union_recall"],
        efficiency["passes_versus_overlap"]["more_passes_less_overlap"]["flex_usd"],
        efficiency["passes_versus_overlap"]["fewer_passes_more_overlap"]["union_recall"],
        efficiency["passes_versus_overlap"]["fewer_passes_more_overlap"]["flex_usd"],
    )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": (
            "POST-HOC (E41-class) tile-size x overlap grid; not a registered "
            "hypothesis. Proposer stage only, consensus-only aggregation."
        ),
        "configuration": {
            "config": "detect_brief-text",
            "model": "gemini-3-flash-preview",
            "library_hash_prefix": "8580ecb2258b64a0",
            "modality": "text", "thinking_level": "minimal", "temperature": 0.7,
            "passes_per_cell": N_PASSES,
        },
        "scope": {
            "carrier": "era-2-487 grid clipped to the four-way tile-union intersection",
            "carrier_tiles": int(len(bounds)),
            "buffer_metres": BUFFER_M,
            "dedup_metres": prepare["dedup_metres"],
            "footprint_audit": prepare["footprint_audit"],
        },
        "single_pass": singles,
        "corroboration_profile": corroboration,
        "consensus_only_board": sorted(
            sweep_rows, key=lambda r: r["f1"], reverse=True)[:15],
        "contrasts": bootstrap,
        "interaction": interaction,
        "sweep": sweep_rows,
        "undefined_mcc_cells": undefined_mcc,
        "costs": costs,
        "cost_efficiency": efficiency,
        "verifier_costing": pv,
    }
    (args.output_dir / "grid_analysis.json").write_text(json.dumps(payload, indent=2))

    (args.output_dir / "per_tile_counts.json").write_text(json.dumps({
        "tile_order": list(bounds["tile_name"]),
        "cells": {cell: {k: v.tolist() for k, v in per_tile[cell].items()}
                  for cell in CELL_ORDER},
    }, indent=2))

    with (args.output_dir / "sweep.csv").open("w", newline="") as handle:
        fields = ["cell", "label", "tile_px", "overlap_frac", "K",
                  "min_corroboration", "min_votes", "n_detections",
                  "precision", "recall", "f1", "mcc"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sweep_rows:
            writer.writerow({k: row[k] for k in fields})

    logger.info("Wrote %s", args.output_dir / "grid_analysis.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
