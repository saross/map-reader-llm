#!/usr/bin/env python3
"""
Grid post-verifier scoring: the proposer-verifier board for the 2026-08-18 grid.

The tile-size x overlap grid (`results/grid-2026-08-18/findings.md`) left two
questions explicitly unresolved because no verifier had run: whether the
tile-size ranking (512 px > 384 px everywhere) survives a precision stage, and
whether the overlap reversal (50 % wins under aggregation) survives one. The
Principal Investigator (PI) approved the costed verifier stage on 2026-08-24;
`materialise_grid_unions.py` produced the four K = 10 union candidate sets
under an exact-count gate, and the adversarial text verifier
(`verify_adversarial-text`, gemini-3-flash-preview, T = 0.0, MINIMAL, n = 1)
scored all 9,133 candidates with zero failures (committed at `8eda1e3a3`).

This script spends $0: it thresholds the committed per-candidate probabilities
into verified sets and scores them with the grid analysis's own machinery —
the same `score_detection_set` wrapper, the same common carrier grid, the same
Decision 10 paired tile bootstrap at B = 10,000 (erratum E82), seed 42.

What it does:

1. **Join gates.** Each cell's `union_k10.geojson` joins its
   `verify/probabilities.json` by feature index (`extract_candidates` assigns
   ``candidate_id = idx`` in feature order, and `run_pv.py` keys results as
   ``candidate_{idx:05d}``). Gates: the documented union counts reproduce
   EXACTLY (1,402 / 2,585 / 1,827 / 3,319); the probability keys are exactly
   ``candidate_00000 .. candidate_{n-1:05d}``; carrier-tile reassignment of the
   round-tripped geometries reproduces the stored ``source_tile`` per feature;
   and re-scoring the unthresholded union reproduces the committed sweep's
   (K = 10, c >= 1, k >= 1) row.

2. **The post-verifier sweep.** Per cell, every achievable operating point:
   verifier threshold ``prob_t`` over the cell's distinct observed
   probabilities (keep if ``mound_probability >= prob_t``, the
   `materialise_pv_geojson` convention) crossed with vote threshold
   ``k`` in 1..10 (keep if ``vote_count >= k``). Undefined tile Matthews
   Correlation Coefficient (MCC) stays ``null``, never 0.0 (erratum E81).

3. **The two contrasts, post-verifier.** Paired tile bootstrap of the best-F1
   operating points: tile size at each overlap, overlap at each tile size, and
   the difference-of-differences interaction — the same instrument the
   consensus-only board used, so the pre/post comparison is like for like.

4. **Verifier-versus-consensus redundancy.** The pure-verifier board (k = 1,
   best ``prob_t``) against the committed consensus-only board, per cell.

5. **Billing reconciliation.** Sums the four verifier `run.meta.json` cost
   blocks (list basis), applies the flex divisor, and reconciles against the
   findings document's costed estimate ($6.33 at $0.000693/call).

6. **Condition materialisation** (``--materialise-conditions``): writes each
   cell's best-F1 verified set as a scorable GeoJSON and scores it with
   `evaluate_detections.py` at B = 10,000 under a reproduction gate, so the
   analysis can take a register row (the analyses schema requires a non-empty
   ``conditions_compared``; defect D16 pattern).

Usage::

    python scripts/grid_verifier_analysis.py                # sweep + contrasts
    python scripts/grid_verifier_analysis.py --materialise-conditions

Inputs:
    - outputs/grid-2026-08-18/verifier/<cell>/union_k10.geojson
    - outputs/grid-2026-08-18/verifier/<cell>/verify/probabilities.json
    - outputs/grid-2026-08-18/verifier/<cell>/verify/run.meta.json
    - outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson
    - results/grid-2026-08-18/grid_analysis.json (consensus-only anchors)
    - inputs/vectors/references/mounds-reference.geojson

Outputs (under ``--output-dir``, default results/grid-2026-08-18):
    - verifier_analysis.json — every number, machine-readable
    - verifier_sweep.csv — the full prob_t x k sweep per cell
    - conditions-verified/<cell>/{detections.geojson, eval/evaluation.json}
      and conditions-verified/grid_verified_conditions.json (with the flag)

Zero API spend; reads committed artefacts only. Run on sapphire: the sweep is
several hundred Hungarian matchings and the bootstraps are B = 10,000.

Created: 2026-08-24 (Session 142)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_analysis import (  # noqa: E402
    BUFFER_M,
    CELL_LABEL,
    CELL_ORDER,
    CRS,
    SEED,
    paired_bootstrap,
    paired_interaction,
    score,
)
from scripts.grid_prepare_scoring import CELLS  # noqa: E402
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from scripts.materialise_grid_unions import EXPECTED  # noqa: E402
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

VERIFIER_DIR = PROJECT_ROOT / "outputs/grid-2026-08-18/verifier"
COMMON_BOUNDS = (
    PROJECT_ROOT / "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson")
GRID_ANALYSIS = PROJECT_ROOT / "results/grid-2026-08-18/grid_analysis.json"
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"

#: Bootstrap iterations: 10,000 per the 2026-08-19 PI ruling (erratum E82).
BOOTSTRAP = 10_000

K_TOTAL = 10
CRS_URN = "urn:ogc:def:crs:EPSG::32635"

#: Gemini real-time flex bills at half list price; the meta cost blocks are
#: list basis (``cost_basis: "list"``) and never apply the discount themselves.
FLEX_DISCOUNT_DIVISOR = 2.0

#: The findings document's costed verifier stage, for reconciliation.
COSTED_TOTAL_USD = 6.33
COSTED_PER_CALL_USD = 0.000693


class JoinGateError(RuntimeError):
    """A verifier join or reproduction gate failed; nothing may be scored."""


def load_verified_union(cell: str) -> gpd.GeoDataFrame:
    """Load one cell's K = 10 union with per-candidate verifier probabilities.

    Joins ``union_k10.geojson`` to ``verify/probabilities.json`` by feature
    index: `extract_candidates` assigns ``candidate_id = idx`` in feature
    order and `run_pv.py` persists results under ``candidate_{idx:05d}``.

    Args:
        cell: Cell label (e.g. ``g512_ov064``).

    Returns:
        GeoDataFrame in the project Coordinate Reference System (CRS) with
        ``vote_count``, ``mound_probability`` and ``source_tile`` columns.

    Raises:
        JoinGateError: If the feature count does not reproduce the documented
            union count, or the probability keys are not exactly the
            contiguous ``candidate_NNNNN`` range.
    """
    union_path = VERIFIER_DIR / cell / "union_k10.geojson"
    probs_path = VERIFIER_DIR / cell / "verify" / "probabilities.json"
    gdf = gpd.read_file(union_path).to_crs(CRS)
    results = json.loads(probs_path.read_text())["results"]

    if len(gdf) != EXPECTED[cell]:
        raise JoinGateError(
            f"{cell}: union holds {len(gdf)} features, documented {EXPECTED[cell]}")
    expected_keys = {f"candidate_{i:05d}" for i in range(len(gdf))}
    if set(results) != expected_keys:
        missing = sorted(expected_keys - set(results))[:5]
        extra = sorted(set(results) - expected_keys)[:5]
        raise JoinGateError(
            f"{cell}: probability keys are not the contiguous candidate range "
            f"(missing {missing}, extra {extra})")

    gdf["mound_probability"] = [
        float(results[f"candidate_{i:05d}"]["mound_probability"])
        for i in range(len(gdf))
    ]
    return gdf


def reassignment_gate(gdf: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame,
                      cell: str) -> gpd.GeoDataFrame:
    """Re-derive ``source_tile`` from geometry and assert it matches the stored one.

    The union file round-trips through EPSG:4326; re-running the carrier
    assignment on the reprojected geometries and comparing to the stored
    column catches any coordinate drift large enough to matter.

    Args:
        gdf: Joined union in the project CRS with a stored ``source_tile``.
        bounds: Common carrier tile bounds.
        cell: Cell label, for the error message.

    Returns:
        The GeoDataFrame with ``source_tile`` refreshed from the reassignment.

    Raises:
        JoinGateError: If any feature's reassigned tile differs from the
            stored one.
    """
    fresh = assign_primary_tiles(gdf, bounds)
    stored = gdf["source_tile"]
    mismatches = int((fresh != stored).sum())
    if mismatches:
        raise JoinGateError(
            f"{cell}: {mismatches} features reassign to a different carrier tile "
            "after the CRS round-trip")
    out = gdf.copy()
    out["source_tile"] = fresh
    return out


def union_reproduction_gate(
    gdf: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
    anchor: dict[str, Any], cell: str,
) -> dict[str, Any]:
    """Score the unthresholded union and assert it reproduces the committed sweep row.

    Args:
        gdf: Joined union in the project CRS.
        bounds: Common carrier tile bounds.
        gdf_ref: Ground-truth references.
        anchor: The committed (K = 10, c >= 1, k >= 1) sweep row for this cell.
        cell: Cell label, for the error message.

    Returns:
        The union's score dict.

    Raises:
        JoinGateError: If precision, recall or F1 moves by more than 1e-6, or
            the detection count differs at all.
    """
    result = score(gdf, gdf_ref, bounds)
    if result["n_detections"] != anchor["n_detections"]:
        raise JoinGateError(
            f"{cell}: union scores {result['n_detections']} detections, committed "
            f"sweep row has {anchor['n_detections']}")
    for key in ("precision", "recall", "f1"):
        if abs(result[key] - anchor[key]) > 1e-6:
            raise JoinGateError(
                f"{cell}: union {key} {result[key]:.8f} != committed "
                f"{anchor[key]:.8f}")
    return result


def verified_subset(gdf: gpd.GeoDataFrame, prob_t: float,
                    min_votes: int) -> gpd.GeoDataFrame:
    """Apply the verifier and vote thresholds (both inclusive).

    Args:
        gdf: Joined union with ``mound_probability`` and ``vote_count``.
        prob_t: Minimum verifier probability (kept if ``>= prob_t``).
        min_votes: Minimum across-pass vote count (kept if ``>= min_votes``).

    Returns:
        The filtered GeoDataFrame (a view-independent copy).
    """
    mask = (gdf["mound_probability"] >= prob_t) & (gdf["vote_count"] >= min_votes)
    return gdf[mask].copy()


def sweep_cell(
    gdf: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
    cell: str,
) -> list[dict[str, Any]]:
    """Score every achievable (prob_t, min_votes) operating point for one cell.

    Sweeping ``prob_t`` over the cell's distinct observed probabilities loses
    nothing: every achievable verified set corresponds to a threshold at an
    observed value (0.0 is always included and is the no-filter point).

    Args:
        gdf: Joined union in the project CRS.
        bounds: Common carrier tile bounds.
        gdf_ref: Ground-truth references.
        cell: Cell label.

    Returns:
        One row per operating point with precision, recall, F1, MCC and count.
    """
    thresholds = sorted({0.0} | set(gdf["mound_probability"].round(4)))
    rows: list[dict[str, Any]] = []
    for prob_t in thresholds:
        for k in range(1, K_TOTAL + 1):
            subset = verified_subset(gdf, prob_t, k)
            row = score(subset, gdf_ref, bounds)
            row.update({
                "cell": cell, "label": CELL_LABEL[cell],
                "tile_px": CELLS[cell]["tile_px"],
                "overlap_frac": CELLS[cell]["overlap_frac"],
                "K": K_TOTAL, "prob_t": prob_t, "min_votes": k,
            })
            rows.append(row)
    best = max(rows, key=lambda r: r["f1"])
    logger.info(
        "%-16s post-verifier: best F1=%.4f at prob_t>=%.2f k>=%d "
        "(n=%d, P=%.4f R=%.4f MCC=%s)",
        CELL_LABEL[cell], best["f1"], best["prob_t"], best["min_votes"],
        best["n_detections"], best["precision"], best["recall"],
        "undefined" if best["mcc"] is None else f"{best['mcc']:.4f}",
    )
    return rows


def best_row(rows: list[dict[str, Any]], cell: str,
             pure_verifier: bool = False) -> dict[str, Any]:
    """Return one cell's best-F1 row, optionally restricted to k = 1.

    Args:
        rows: Sweep rows (any mix of cells).
        cell: Cell label to select.
        pure_verifier: If True, only k = 1 rows compete — the verifier as the
            sole precision stage, no consensus filter.

    Returns:
        The best-F1 row.
    """
    sel = [r for r in rows if r["cell"] == cell
           and (not pure_verifier or r["min_votes"] == 1)]
    return max(sel, key=lambda r: r["f1"])


def per_tile_counts(
    gdf: gpd.GeoDataFrame, bounds: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame,
) -> dict[str, np.ndarray]:
    """Per-tile TP/FP/FN arrays for one verified set on the carrier grid.

    A verified set is a single detection set, so counts are integer per-tile
    (the same treatment the era-1 leaderboard gives consensus single-set
    cells); no run averaging applies.

    Args:
        gdf: The verified detection set with ``source_tile``.
        bounds: Common carrier tile bounds (defines tile order).
        gdf_ref: Ground-truth references.

    Returns:
        ``{"tp", "fp", "fn"}`` float arrays aligned with the bounds order.
    """
    tile_order = list(bounds["tile_name"])
    tm = compute_per_tile_tp_fp_fn(gdf, gdf_ref, bounds, buffer_metres=BUFFER_M)
    tm = tm.set_index("tile_name").reindex(tile_order).fillna(0)
    return {k: tm[k].to_numpy(dtype=float) for k in ("tp", "fp", "fn")}


def billing() -> dict[str, Any]:
    """Sum the four verifier metas and reconcile list, flex and costed figures.

    Returns:
        Per-cell and total spend on both bases, with the costed-estimate
        reconciliation.
    """
    cells: dict[str, Any] = {}
    total_list = 0.0
    total_calls = 0
    for cell in CELL_ORDER:
        meta = json.loads(
            (VERIFIER_DIR / cell / "verify" / "run.meta.json").read_text())
        cost = meta["cost_estimate"]
        n = EXPECTED[cell]
        cells[cell] = {
            "calls": n,
            "list_usd": cost["list_total_cost_usd"],
            "flex_usd": cost["list_total_cost_usd"] / FLEX_DISCOUNT_DIVISOR,
            "cost_basis_recorded": cost["cost_basis"],
            "input_tokens": meta["usage_stats"]["total_input_tokens"],
            "output_tokens": meta["usage_stats"]["total_output_tokens"],
        }
        total_list += cost["list_total_cost_usd"]
        total_calls += n
    total_flex = total_list / FLEX_DISCOUNT_DIVISOR
    return {
        "cells": cells,
        "total_calls": total_calls,
        "total_list_usd": round(total_list, 4),
        "total_flex_usd": round(total_flex, 4),
        "flex_per_call_usd": round(total_flex / total_calls, 6),
        "costed_estimate": {
            "total_usd": COSTED_TOTAL_USD,
            "per_call_usd": COSTED_PER_CALL_USD,
            "delta_usd": round(total_flex - COSTED_TOTAL_USD, 4),
        },
        "note": (
            "Meta cost blocks are list basis; Gemini real-time flex bills at "
            "half list, so the flex column is the billed basis (cf. the "
            "proposer-stage cost audit in findings.md § Cost)."
        ),
    }


def materialise_condition(
    gdf: gpd.GeoDataFrame, point: dict[str, Any], target: Path,
    bounds: gpd.GeoDataFrame,
) -> int:
    """Write one cell's best verified operating point as a scorable GeoJSON.

    Args:
        gdf: Joined union in the project CRS.
        point: The sweep row naming ``prob_t`` and ``min_votes``.
        target: Output GeoJSON path.
        bounds: Common carrier bounds; stamped as the coverage record so the
            evaluator's partial-coverage guard (E72) can see full coverage.

    Returns:
        Number of features written.
    """
    subset = verified_subset(gdf, point["prob_t"], point["min_votes"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": CRS_URN}},
        "processed_tiles": sorted(bounds["tile_name"].tolist()),
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.x, geom.y]},
                "properties": {
                    "source_tile": tile,
                    "label": "mound",
                    "subtype": "mound",
                    "vote_count": int(votes),
                    "mound_probability": float(prob),
                },
            }
            for geom, tile, votes, prob in zip(
                subset.geometry, subset["source_tile"], subset["vote_count"],
                subset["mound_probability"], strict=True)
        ],
    }, indent=2))
    return len(subset)


def evaluate(detections: Path, out_dir: Path) -> Path:
    """Run `evaluate_detections.py` on one materialised set at B = 10,000."""
    cmd = [
        sys.executable, str(PROJECT_ROOT / "scripts/evaluate_detections.py"),
        "--detections", str(detections),
        "--ground-truth", str(GROUND_TRUTH),
        "--bounds", str(COMMON_BOUNDS),
        "--bootstrap", str(BOOTSTRAP),
        "--seed", str(SEED),
        "--output-dir", str(out_dir),
        "--mcc",
    ]
    logger.info("scoring %s at B=%d", detections.name, BOOTSTRAP)
    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT, capture_output=True, text=True)
    return out_dir / "evaluation.json"


def main() -> int:
    """Run the gates, the sweep, the contrasts, and (optionally) the conditions.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="Post-verifier board for the tile-size x overlap grid.")
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results/grid-2026-08-18")
    parser.add_argument("--bootstrap", type=int, default=BOOTSTRAP)
    parser.add_argument(
        "--materialise-conditions", action="store_true",
        help="Also write each cell's best verified set and score it with "
             "evaluate_detections.py under a reproduction gate.")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    bounds = gpd.read_file(COMMON_BOUNDS)
    gdf_ref = gpd.read_file(GROUND_TRUTH)
    committed = json.loads(GRID_ANALYSIS.read_text())["sweep"]
    logger.info("common carrier grid: %d tiles", len(bounds))

    # --- Gates, then the sweep, per cell -----------------------------------
    unions: dict[str, gpd.GeoDataFrame] = {}
    union_scores: dict[str, dict[str, Any]] = {}
    sweep_rows: list[dict[str, Any]] = []
    for cell in CELL_ORDER:
        gdf = load_verified_union(cell)
        gdf = reassignment_gate(gdf, bounds, cell)
        anchor = next(
            r for r in committed
            if r["cell"] == cell and r["K"] == K_TOTAL
            and r["min_corroboration"] == 1 and r["min_votes"] == 1)
        union_scores[cell] = union_reproduction_gate(
            gdf, bounds, gdf_ref, anchor, cell)
        logger.info("%-16s gates passed: %d candidates, union F1 %.4f reproduced",
                    CELL_LABEL[cell], len(gdf), union_scores[cell]["f1"])
        unions[cell] = gdf
        sweep_rows.extend(sweep_cell(gdf, bounds, gdf_ref, cell))

    # --- Boards ------------------------------------------------------------
    best = {cell: best_row(sweep_rows, cell) for cell in CELL_ORDER}
    pure = {cell: best_row(sweep_rows, cell, pure_verifier=True)
            for cell in CELL_ORDER}
    consensus_best = {
        cell: max((r for r in committed
                   if r["cell"] == cell and r["K"] == K_TOTAL),
                  key=lambda r: r["f1"])
        for cell in CELL_ORDER
    }

    # --- Contrasts at the best post-verifier operating points --------------
    per_tile = {
        cell: per_tile_counts(
            verified_subset(unions[cell], best[cell]["prob_t"],
                            best[cell]["min_votes"]),
            bounds, gdf_ref)
        for cell in CELL_ORDER
    }
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
        "interaction = %+.4f CI95 [%+.4f, %+.4f] p=%.4f %s",
        interaction["difference_of_differences"], interaction["ci_lower"],
        interaction["ci_upper"], interaction["p_two_sided"],
        "EXCLUDES 0" if interaction["excludes_zero"] else "includes 0")

    # --- Optional condition materialisation --------------------------------
    conditions: list[dict[str, Any]] | None = None
    failures = 0
    if args.materialise_conditions:
        conditions = []
        cond_root = args.output_dir / "conditions-verified"
        for cell in CELL_ORDER:
            point = best[cell]
            det = cond_root / cell / "detections.geojson"
            n = materialise_condition(unions[cell], point, det, bounds)
            if n != point["n_detections"]:
                logger.error("%s: materialised %d features, sweep row has %d",
                             cell, n, point["n_detections"])
                failures += 1
            eval_path = evaluate(det, cond_root / cell / "eval")
            doc = json.loads(eval_path.read_text())
            buf = next(b for b in doc["summary"]["buffers"]
                       if b["buffer_metres"] == BUFFER_M)
            delta = abs(buf["f1"] - point["f1"])
            ok = delta < 5e-4
            failures += 0 if ok else 1
            logger.info(
                "%-16s prob_t>=%.2f k>=%d | n=%d | sweep F1 %.4f, re-scored "
                "%.4f (delta %.5f) %s",
                CELL_LABEL[cell], point["prob_t"], point["min_votes"], n,
                point["f1"], buf["f1"], delta, "OK" if ok else "MISMATCH")
            tc = doc["summary"].get("tile_classification", {})
            mcc = (tc.get("mcc") if not isinstance(tc.get("mcc"), dict)
                   else tc["mcc"].get("point"))
            conditions.append({
                "cell": cell,
                "label": CELL_LABEL[cell],
                "condition_label": (
                    f"{cell.replace('_', '-')}-k10-verified-"
                    f"p{point['prob_t']:.2f}-k{point['min_votes']}"),
                "prob_t": point["prob_t"],
                "min_votes": point["min_votes"],
                "n_detections": n,
                "sweep_f1_at_20m": point["f1"],
                "rescored_f1_at_20m": buf["f1"],
                "f1_ci_lower": buf["f1_ci_lower"],
                "f1_ci_upper": buf["f1_ci_upper"],
                "f1_ci_method": buf["f1_ci_method"],
                "precision": buf["precision"],
                "recall": buf["recall"],
                "tile_mcc": mcc,
                "bootstrap_iterations": args.bootstrap,
                "detections": str(det.relative_to(PROJECT_ROOT)),
                "evaluation": str(eval_path.relative_to(PROJECT_ROOT)),
                "reproduces_sweep": ok,
            })
        (cond_root / "grid_verified_conditions.json").write_text(json.dumps({
            "classification": (
                "POST-HOC (E41-class); registrable proposer-verifier "
                "conditions for the tile-size x overlap grid. K = 10 union "
                "input, adversarial text verifier, best-F1@20m operating "
                "point per cell."),
            "verifier": {
                "config": "verify_adversarial-text",
                "model": "gemini-3-flash-preview",
                "temperature": 0.0, "thinking_level": "minimal", "n": 1,
            },
            "bootstrap": {"n_iterations": args.bootstrap, "seed": SEED},
            "cells": conditions,
        }, indent=2) + "\n")

    # --- Payload -----------------------------------------------------------
    def _board(rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
        return {cell: {k: rows[cell][k] for k in
                       ("precision", "recall", "f1", "mcc", "n_detections",
                        "prob_t", "min_votes")}
                for cell in CELL_ORDER}

    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": (
            "POST-HOC (E41-class) proposer-verifier board for the tile-size x "
            "overlap grid: the committed K = 10 unions thresholded on the "
            "committed per-candidate verifier probabilities. $0 scoring."),
        "verifier": {
            "config": "verify_adversarial-text",
            "model": "gemini-3-flash-preview",
            "temperature": 0.0, "thinking_level": "minimal", "n": 1,
            "candidates_verified": sum(EXPECTED.values()),
            "failures": 0,
        },
        "gates": {
            "union_counts": {c: EXPECTED[c] for c in CELL_ORDER},
            "union_scores_reproduced": {
                c: union_scores[c]["f1"] for c in CELL_ORDER},
        },
        "board_best": _board(best),
        "board_pure_verifier_k1": _board(pure),
        "board_consensus_only_committed": {
            cell: {k: consensus_best[cell][k] for k in
                   ("precision", "recall", "f1", "mcc", "n_detections",
                    "min_corroboration", "min_votes")}
            for cell in CELL_ORDER
        },
        "verifier_gain_over_consensus": {
            cell: round(best[cell]["f1"] - consensus_best[cell]["f1"], 4)
            for cell in CELL_ORDER
        },
        "bootstrap_contrasts": bootstrap,
        "interaction": interaction,
        "bootstrap_config": {"n_iterations": args.bootstrap, "seed": SEED,
                             "method": "paired tile bootstrap, Decision 10; "
                                       "B per erratum E82"},
        "billing": billing(),
    }
    if conditions is not None:
        payload["conditions"] = conditions

    out_json = args.output_dir / "verifier_analysis.json"
    out_json.write_text(json.dumps(payload, indent=2) + "\n")

    sweep_cols = ["cell", "label", "tile_px", "overlap_frac", "K", "prob_t",
                  "min_votes", "n_detections", "precision", "recall", "f1", "mcc"]
    out_csv = args.output_dir / "verifier_sweep.csv"
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=sweep_cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sweep_rows)

    logger.info("wrote %s and %s (%d sweep rows)", out_json.name, out_csv.name,
                len(sweep_rows))
    if failures:
        logger.error("%d condition gate(s) FAILED", failures)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
