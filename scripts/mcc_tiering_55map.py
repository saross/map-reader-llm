#!/usr/bin/env python3
# ============================================================================
# mcc_tiering_55map.py
# ----------------------------------------------------------------------------
# Session 114: alternate-metric (tile-MCC) permutation tiering for the
# 55-map canonical board (Shawn-requested 2026-06-13: "run the alternate
# metric permutation, I would like CIs").
#
# The metric-led boards (results/metric-leaderboards/55map-canonical-50m.md)
# rank the eight canonical-GT cells by tile-MCC but carry no statistics —
# the board header notes "alternate-metric permutation tiering is available
# on demand (same tile-swap machinery)". This script supplies it:
#
#   1. Rebuild each cell's PER-TILE binary classification (has_detections
#      vs has_mounds) exactly as the Track-2 engine computed it: the
#      detections' own `source_tile` property, reference = canonical
#      extended GT at R = 50 m (reviewed students + phantoms gated <= 50 m
#      via the engine's build_phantom_gdf / build_extended_gt), tile truth
#      by geometric intersection, all in EPSG:32635.
#   2. GATE (exact): each cell's rebuilt confusion matrix (tp/tn/fp/fn)
#      must EQUAL the committed Track-2 summary.json tile_classification
#      at 50 m. Any mismatch aborts.
#   3. Round-robin pairwise tile-swap permutation on the MCC statistic
#      (10k perms, seed 42, two-sided — mirrors the F1 board's
#      permutation_test_float conventions: probability-0.5 per-tile swap,
#      numpy default_rng stream, p = mean(|null| >= |observed|)),
#      then BH-FDR q = 0.05 and greedy-clique tiers (machinery imported
#      VERBATIM from the F1 boards).
#   4. Bootstrap CIs are NOT recomputed: the Track-2 engine already wrote
#      BCa MCC CIs (summary.json tile_classification.mcc_CI); they are
#      carried through to the outputs.
#
# OUTPUTS: results/metric-leaderboards/55map-mcc-tiering.{json,md}
# COST: $0 (on-disk re-analysis). Run on zbook (sapphire in use, S114).
#
# Usage:
#   .venv/bin/python scripts/mcc_tiering_55map.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-13 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    DEFAULT_CRS,
    build_extended_gt,
    build_phantom_gdf,
)
from scripts.n1_baseline_leaderboard_tiering import greedy_clique_tiers  # noqa: E402

BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
STUDENT_GT = BASE_DIR / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
TRACK2 = BASE_DIR / "results/55maps-extended-gt-2026-06-07"
REVIEW_YESTERDAY = TRACK2 / "empty-yesterday-review.csv"
CANONICAL_REVIEW = (
    BASE_DIR / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv"
)
OUT_DIR = BASE_DIR / "results/metric-leaderboards"
BUFFER_M = 50
N_PERMUTATIONS = 10_000
SEED = 42

# Display name -> Track-2 evaluation directory (the eight canonical cells,
# matching results/metric-leaderboards/55map-canonical-50m.md). Detections
# paths are taken from each cell's OWN summary.json provenance block, so the
# permutation consumes exactly the files the committed evaluations scored.
CELLS = {
    "IM-k3": "IM-k3",
    "T03-k3 (oracle)": "T03-k3",
    "T03-k4": "T03-k4",
    "TH7-k3": "TH7-k3",
    "TH7-k4 (carry-forward)": "TH7-k4",
    "TM-k3": "TM-k3",
    "TM-k4": "TM-k4",
    "TM-n10-k5 (uplift)": "TM-n10-k5",
}


def mcc_from_confusion(
    tp: np.ndarray | float,
    tn: np.ndarray | float,
    fp: np.ndarray | float,
    fn: np.ndarray | float,
) -> np.ndarray | float:
    """Matthews correlation coefficient from confusion counts.

    Mirrors ``lib_advanced_metrics.calculate_tile_classification``:
    MCC = (TP*TN - FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)), with 0.0
    where the denominator is zero (the vectorised analogue of its
    ``None`` edge case — a zero row/column sum cannot occur on this
    board, so the substitution is inert here).

    Args:
        tp, tn, fp, fn: Confusion counts (scalars or aligned arrays).

    Returns:
        MCC value(s), same shape as the inputs.
    """
    tp = np.asarray(tp, dtype=float)
    tn = np.asarray(tn, dtype=float)
    fp = np.asarray(fp, dtype=float)
    fn = np.asarray(fn, dtype=float)
    numerator = tp * tn - fp * fn
    denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    out = np.divide(
        numerator, np.sqrt(denom), out=np.zeros_like(numerator), where=denom > 0
    )
    return float(out) if out.ndim == 0 else out


def tile_vectors(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Per-tile truth and prediction vectors for tile classification.

    Vectorised equivalent of the per-tile loop in
    ``lib_advanced_metrics.calculate_tile_classification``: a tile is
    TRUE if any reference point intersects its geometry (boundary points
    therefore count for every tile they touch), and PREDICTED if any
    detection carries its ``tile_name`` in ``source_tile``. Equivalence
    is pinned by a tier-1 test and by the exact confusion-matrix gate in
    ``main``.

    Args:
        gdf_det: Detections with a ``source_tile`` column.
        gdf_ref: Reference (ground-truth) points, same CRS as bounds.
        gdf_bounds: Tile boundary polygons with ``tile_name``.

    Returns:
        (tile_names, truth, pred) — names in bounds order, two aligned
        boolean arrays.
    """
    tiles = list(gdf_bounds["tile_name"].unique())
    if len(tiles) != len(gdf_bounds):
        raise ValueError("duplicate tile_name rows in bounds — loop/sjoin semantics differ")
    index = {t: i for i, t in enumerate(tiles)}

    truth = np.zeros(len(tiles), dtype=bool)
    joined = gpd.sjoin(
        gdf_ref[["geometry"]], gdf_bounds[["tile_name", "geometry"]],
        how="inner", predicate="intersects",
    )
    for t in joined["tile_name"].unique():
        truth[index[t]] = True

    pred = np.zeros(len(tiles), dtype=bool)
    for t in pd.unique(gdf_det["source_tile"]):
        i = index.get(t)
        if i is not None:
            pred[i] = True
    return tiles, truth, pred


def permutation_test_mcc(
    pred_a: np.ndarray,
    pred_b: np.ndarray,
    truth: np.ndarray,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict:
    """Paired tile-swap permutation test on the tile-MCC statistic.

    Mirrors ``n1_baseline_leaderboard_tiering.permutation_test_float``
    exactly — the probability-0.5 per-tile label swap, the
    ``numpy.random.default_rng(seed)`` stream, and the two-sided
    p = mean(|null| >= |observed|) — but the statistic is tile-level MCC
    rather than micro-F1. Truth labels are fixed per tile; the swap
    exchanges the two cells' predictions tile-by-tile.

    Args:
        pred_a: Cell A per-tile boolean predictions.
        pred_b: Cell B per-tile boolean predictions.
        truth: Per-tile boolean ground-truth labels (shared).
        n_permutations: Number of permutation iterations.
        seed: Random seed for reproducibility.

    Returns:
        Dict with ``mcc_a``, ``mcc_b``, ``observed_diff``, ``p_value``,
        ``n_permutations``, ``n_tiles``, and null-distribution stats.
    """
    def _mcc(pred: np.ndarray) -> float | np.ndarray:
        """MCC of prediction vector(s) against the shared truth."""
        tp = (pred & truth).sum(axis=-1)
        fp = (pred & ~truth).sum(axis=-1)
        fn = (~pred & truth).sum(axis=-1)
        tn = (~pred & ~truth).sum(axis=-1)
        return mcc_from_confusion(tp, tn, fp, fn)

    mcc_a = float(_mcc(pred_a))
    mcc_b = float(_mcc(pred_b))
    observed_diff = mcc_a - mcc_b

    rng = np.random.default_rng(seed)
    swap = rng.random((n_permutations, len(truth))) < 0.5
    perm_a = np.where(swap, pred_b[None, :], pred_a[None, :])
    perm_b = np.where(swap, pred_a[None, :], pred_b[None, :])
    null_diffs = _mcc(perm_a) - _mcc(perm_b)
    p_value = float(np.mean(np.abs(null_diffs) >= abs(observed_diff)))

    return {
        "mcc_a": round(mcc_a, 6),
        "mcc_b": round(mcc_b, 6),
        "observed_diff": round(observed_diff, 6),
        "p_value": round(p_value, 4),
        "n_permutations": n_permutations,
        "n_tiles": int(len(truth)),
        "null_mean": round(float(np.mean(null_diffs)), 6),
        "null_std": round(float(np.std(null_diffs)), 6),
    }


def _load_cell_inputs(track2_dir: Path) -> tuple[gpd.GeoDataFrame, dict]:
    """Load one cell's detections (engine CRS handling) and its committed
    50 m tile_classification block (the gate target + the BCa CI source).

    Args:
        track2_dir: The cell's Track-2 evaluation directory.

    Returns:
        (gdf_det reprojected to the engine CRS, tile_classification dict).
    """
    summary = json.loads((track2_dir / "summary.json").read_text())
    det_path = summary["metadata"]["input_paths"]["detections"]
    # Provenance paths were recorded absolute on the scoring host;
    # relativise against this repo checkout.
    rel = det_path.split("map-reader-llm/", 1)[1]
    gdf_det = gpd.read_file(BASE_DIR / rel)
    if gdf_det.crs is None:
        gdf_det = gdf_det.set_crs("EPSG:4326")
    gdf_det = gdf_det.to_crs(DEFAULT_CRS)
    row50 = next(r for r in summary["results"] if r["R_m"] == BUFFER_M)
    return gdf_det, row50["tile_classification"]


def main() -> int:
    """Build the 55-map tile-MCC permutation tiering."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    gdf_bounds = gpd.read_file(BOUNDS)
    if gdf_bounds.crs is None:
        gdf_bounds = gdf_bounds.set_crs("EPSG:4326")
    gdf_bounds = gdf_bounds.to_crs(DEFAULT_CRS)

    gdf_student = gpd.read_file(STUDENT_GT).to_crs(DEFAULT_CRS)
    review_y = pd.read_csv(REVIEW_YESTERDAY)
    review_t = pd.read_csv(CANONICAL_REVIEW)
    gdf_phantoms = build_phantom_gdf(review_y, review_t, BUFFER_M, crs=DEFAULT_CRS)
    gdf_ref = build_extended_gt(gdf_student, gdf_phantoms)
    print(f"extended GT at {BUFFER_M} m: {len(gdf_ref)} points "
          f"({len(gdf_student)} students + {len(gdf_phantoms)} phantoms); "
          f"{len(gdf_bounds)} tiles", flush=True)

    cells: list[dict] = []
    truth: np.ndarray | None = None
    for name, dirname in CELLS.items():
        gdf_det, committed = _load_cell_inputs(TRACK2 / dirname)
        tiles, cell_truth, pred = tile_vectors(gdf_det, gdf_ref, gdf_bounds)
        if truth is None:
            truth = cell_truth
        elif not np.array_equal(truth, cell_truth):
            sys.exit("GATE FAIL: truth vector differs between cells")
        confusion = {
            "tp": int((pred & truth).sum()), "tn": int((~pred & ~truth).sum()),
            "fp": int((pred & ~truth).sum()), "fn": int((~pred & truth).sum()),
        }
        committed_counts = {k: committed[k] for k in ("tp", "tn", "fp", "fn")}
        ok = confusion == committed_counts
        print(f"  {name:<24} rebuilt {confusion} "
              f"{'== committed ok' if ok else f'!= committed {committed_counts} GATE FAIL'}",
              flush=True)
        if not ok:
            sys.exit(f"GATE FAIL: {name} rebuilt confusion != committed summary.json")
        cells.append({
            "name": name,
            "condition_dir": str((TRACK2 / dirname).relative_to(BASE_DIR)),
            "mcc": committed["mcc"],
            "mcc_ci": committed.get("mcc_CI"),
            "sensitivity": committed["sensitivity"],
            "specificity": committed["specificity"],
            "confusion": confusion,
            "pred": pred,
        })

    assert truth is not None
    print(f"\n=== round-robin ({len(cells)} cells, {N_PERMUTATIONS // 1000}k "
          f"tile-swap on MCC, seed {SEED}) ===", flush=True)
    pairs, significant = [], {}
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            a, b = cells[i], cells[j]
            r = permutation_test_mcc(a["pred"], b["pred"], truth)
            pairs.append({"a": a["name"], "b": b["name"], **r})
    adjusted = apply_bh_correction([p["p_value"] for p in pairs], q=0.05)
    for p, adj in zip(pairs, adjusted):
        p["bh_adjusted_p"] = round(adj, 6)
        p["significant"] = bool(adj < 0.05)
        significant[frozenset({p["a"], p["b"]})] = p["significant"]

    ordered = sorted(cells, key=lambda c: -c["mcc"])
    tiers = greedy_clique_tiers([c["name"] for c in ordered], significant)
    tier_of = {n: t for t, members in enumerate(tiers, 1) for n in members}
    n_sig = sum(1 for p in pairs if p["significant"])
    print(f"{n_sig}/{len(pairs)} pairs significant -> {len(tiers)} tier(s)", flush=True)

    out = {
        "track": "55map-canonical", "metric": "tile_mcc", "buffer_m": BUFFER_M,
        "n_tiles": int(len(truth)), "n_populated_tiles": int(truth.sum()),
        "n_permutations": N_PERMUTATIONS, "seed": SEED,
        "bh_q": 0.05, "n_significant": n_sig, "n_pairs": len(pairs),
        "ci_source": "Track-2 summary.json tile_classification.mcc_CI "
                     "(BCa, 10k bootstrap, seed 42 — computed by the engine at scoring time)",
        "gate": "rebuilt per-tile confusion == committed summary.json (exact), 8/8",
        "cells": [{k: v for k, v in c.items() if k != "pred"}
                  | {"tier": tier_of[c["name"]]} for c in ordered],
        "pairwise": pairs,
        "tiers": tiers,
    }
    (OUT_DIR / "55map-mcc-tiering.json").write_text(json.dumps(out, indent=2) + "\n")

    md = [
        "# 55-map canonical board — tile-MCC permutation tiering @ 50 m",
        "",
        "> Alternate-metric (tile-MCC) statistical tiering for the eight"
        " canonical-GT cells: round-robin tile-swap permutation on the MCC"
        f" statistic ({N_PERMUTATIONS // 1000}k, seed {SEED}, two-sided)"
        " + BH-FDR q=0.05 + greedy-clique tiers — the same machinery as the"
        f" F1-led board. {n_sig}/{len(pairs)} pairs significant ->"
        f" {len(tiers)} tier(s). 95% CIs are the Track-2 engine's BCa"
        " bootstrap CIs, carried from `summary.json`. Gate: rebuilt"
        " per-tile confusion matrices reproduce the committed evaluations"
        " exactly (8/8).",
        "",
        "| rank | cell | tier | MCC | 95% CI | sens | spec | tp/fp/fn/tn |",
        "|---:|---|---:|---:|---|---:|---:|---|",
    ]
    for i, c in enumerate(ordered, 1):
        lo, hi = c["mcc_ci"] if c["mcc_ci"] else (None, None)
        ci = f"[{lo:.3f}, {hi:.3f}]" if lo is not None else "—"
        cf = c["confusion"]
        md.append(
            f"| {i} | {c['name']} | {tier_of[c['name']]} | {c['mcc']:.4f} | {ci} "
            f"| {c['sensitivity']:.3f} | {c['specificity']:.3f} "
            f"| {cf['tp']}/{cf['fp']}/{cf['fn']}/{cf['tn']} |")
    md += ["", "## Pairwise (BH-adjusted)", "",
           "| pair | ΔMCC | p | BH p | sig |", "|---|---:|---:|---:|---|"]
    for p in sorted(pairs, key=lambda x: x["bh_adjusted_p"]):
        md.append(f"| {p['a']} vs {p['b']} | {p['observed_diff']:+.4f} "
                  f"| {p['p_value']:.4f} | {p['bh_adjusted_p']:.4f} "
                  f"| {'yes' if p['significant'] else 'ns'} |")
    (OUT_DIR / "55map-mcc-tiering.md").write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_DIR.relative_to(BASE_DIR)}/55map-mcc-tiering.{{json,md}}",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
