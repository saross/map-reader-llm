#!/usr/bin/env python3
# ============================================================================
# analyse_verifier_robustness.py
# ----------------------------------------------------------------------------
# Session 109 — analysis ($0, local) for the verifier-robustness run produced by
# run_verifier_robustness.py. Answers two questions from ONE N-iteration
# verification of the 1-of-5 proposer union per cell:
#
#   1. VERIFIER DETERMINISM. T=0.0 is not fully deterministic. For a fixed
#      accepted set we score each of the N verifier iterations INDEPENDENTLY
#      (the "N single runs") and report the spread (mean +/- SD of F1@20 m and
#      tile-MCC). A large SD means every n=1 verified cell in the paper carries
#      hidden run-to-run noise. We also score the N-run CONSENSUS verifier
#      (accept if >= vt of N iterations accept) to see whether consensus damps
#      the spread — and how it compares to the n=1 carry-forward.
#
#   2. PROPOSER INPUT. The union geojson carries vote_count per candidate, so we
#      sweep the proposer-vote input level (1of5..5of5) as free subsets and find
#      which INPUT maximises post-verifier F1@20 m. (Verify the union once;
#      every input level is a post-hoc filter.)
#
# CRS: candidate centroids are EPSG:32635 (matching build_post_verifier_geojson);
# accepted sets are built as 32635 points and reprojected to 4326 for scoring,
# mirroring that audited path exactly (avoids the Obs-350 mislabel class of bug).
#
# Scoring reuses scripts/evaluate_detections.py (14-buffer corrected-F1 + MCC),
# with accepted-set dedup so identical sets are scored once.
#
# Usage:
#     python scripts/analyse_verifier_robustness.py --temperature 0.0
#     python scripts/analyse_verifier_robustness.py --temperature 0.0 \
#         --prob-t 0.1 0.15 0.2 0.25 0.3 --out-dir results/verifier-robustness
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-06-09
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402

# Evaluation CRS is EPSG:32635 (lib_advanced_metrics.DEFAULT_CRS); candidate
# centroids are already in 32635, so no reprojection is needed for scoring.
EVAL_CRS = "EPSG:32635"
DEFAULT_CELLS = BASE_DIR / "planning" / "verifier-robustness-cells.json"
DEFAULT_OUTROOT = BASE_DIR / "outputs" / "verifier-robustness"
GROUND_TRUTH = BASE_DIR / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
BOUNDS_BY_SIZE = {
    256: BASE_DIR / "inputs" / "vectors" / "bounds" / "256" / "full_evaluation_bounds.geojson",
    384: BASE_DIR / "inputs" / "vectors" / "bounds" / "384" / "full_evaluation_bounds.geojson",
    512: BASE_DIR / "inputs" / "vectors" / "bounds" / "full_evaluation_bounds.geojson",
}


def load_candidate_table(manifest_path: Path, probs_path: Path) -> list[dict]:
    """Join manifest geometry/vote_count with the per-iteration verifier probs.

    Args:
        manifest_path: candidate_manifest.json (centroid_x/y in EPSG:32635,
            properties.vote_count = proposer vote 1..N_proposer).
        probs_path: probabilities.json with results keyed
            ``candidate_{id:05d}_iter{k}`` -> mound_probability.

    Returns:
        One dict per candidate present in BOTH files:
        ``{cid, x, y, vote_count, source_tile, iter_probs: [p1..pN]}``.
    """
    manifest = json.loads(manifest_path.read_text())
    results = json.loads(probs_path.read_text())["results"]

    # Gather per-iteration probabilities, keyed by integer candidate id.
    iters_by_cid: dict[int, list[float]] = {}
    for key, val in results.items():
        if not isinstance(val, dict):
            continue
        p = val.get("mound_probability")
        if not isinstance(p, (int, float)):
            continue
        # key form: candidate_00042_iter3  ->  cid=42
        try:
            cid = int(key.split("_iter")[0].split("_")[-1])
        except (ValueError, IndexError):
            continue
        iters_by_cid.setdefault(cid, []).append(float(p))

    table = []
    for c in manifest["candidates"]:
        cid = c["candidate_id"]
        probs = iters_by_cid.get(cid)
        if not probs:
            continue
        table.append({
            "cid": cid,
            "x": float(c["centroid_x"]),
            "y": float(c["centroid_y"]),
            "vote_count": int(c.get("properties", {}).get("vote_count", 0)),
            "source_tile": c.get("source_tile", ""),
            "iter_probs": probs,
        })
    return table


def accepted_cids(table: list[dict], proposer_k: int, rule: str, prob_t: float) -> frozenset[int]:
    """Return the candidate ids accepted under a (proposer_k, rule, prob_t) combo.

    Args:
        table: candidate table from :func:`load_candidate_table`.
        proposer_k: keep only candidates with proposer vote_count >= proposer_k.
        rule: one of ``iter{k}`` (single verifier run k, 1-indexed),
            ``consensus_vt{v}`` (>= v of N iterations accept), or ``mean``
            (mean iteration probability >= prob_t).
        prob_t: per-iteration accept threshold on mound_probability.

    Returns:
        Frozenset of accepted candidate ids (used as the dedup cache key).
    """
    out = set()
    for r in table:
        if r["vote_count"] < proposer_k:
            continue
        probs = r["iter_probs"]
        if rule.startswith("iter"):
            k = int(rule[4:]) - 1
            if k < len(probs) and probs[k] >= prob_t:
                out.add(r["cid"])
        elif rule.startswith("consensus_vt"):
            v = int(rule[len("consensus_vt"):])
            if sum(1 for p in probs if p >= prob_t) >= v:
                out.add(r["cid"])
        elif rule == "mean":
            if probs and (sum(probs) / len(probs)) >= prob_t:
                out.add(r["cid"])
    return frozenset(out)


def score_cids(cids: frozenset[int], by_cid: dict[int, dict],
               gdf_ref: gpd.GeoDataFrame,
               gdf_bounds: gpd.GeoDataFrame) -> tuple[float, float | None]:
    """Score an accepted candidate set in-process (point F1@20 m + tile-MCC).

    Builds the detection GeoDataFrame in EPSG:32635 directly — the candidate
    centroid CRS and the evaluation CRS coincide, so no reprojection or file
    round-trip is needed — and calls the shared bootstrap-free scorer
    (:func:`score_detection_set`). ``gdf_ref`` / ``gdf_bounds`` are loaded once
    by the caller and reused across every set in the grid.
    """
    if not cids:
        return 0.0, None
    sel = [by_cid[c] for c in cids]
    gdf_det = gpd.GeoDataFrame(
        {"geometry": [Point(r["x"], r["y"]) for r in sel],
         "source_tile": [r["source_tile"] for r in sel]},
        crs=EVAL_CRS,
    )
    res = score_detection_set(gdf_det, gdf_ref, gdf_bounds,
                              buffer_metres=20, compute_mcc=True)
    return res["f1"], res["mcc"]


def analyse_cell(cell: dict, outroot: Path, temperature: float,
                 prob_ts: list[float], n_iter: int,
                 gdf_ref: gpd.GeoDataFrame) -> dict:
    """Compute the determinism + proposer-input grid for one cell."""
    name = cell["name"]
    size = cell["size"]
    crops = outroot / name / "crops" / "candidate_manifest.json"
    probs = outroot / name / f"T{temperature}" / "verified" / "probabilities.json"
    table = load_candidate_table(crops, probs)
    by_cid = {r["cid"]: r for r in table}
    n_present = len(table)
    # Infer the proposer vote ceiling actually present (usually 5).
    max_pk = max((r["vote_count"] for r in table), default=0)
    gdf_bounds = load_geojson(BOUNDS_BY_SIZE[size])  # loaded once per cell

    cache: dict[frozenset[int], tuple[float, float | None]] = {}

    def scored(cids: frozenset[int]) -> tuple[float, float | None]:
        if cids not in cache:
            cache[cids] = score_cids(cids, by_cid, gdf_ref, gdf_bounds)
        return cache[cids]

    grid = []  # one row per (proposer_k, rule, prob_t)
    rules = [f"iter{k}" for k in range(1, n_iter + 1)] \
        + [f"consensus_vt{v}" for v in range(1, n_iter + 1)] + ["mean"]
    for pk in range(1, max_pk + 1):
        for rule in rules:
            for pt in prob_ts:
                cids = accepted_cids(table, pk, rule, pt)
                f1, mcc = scored(cids)
                grid.append({"proposer_k": pk, "rule": rule, "prob_t": pt,
                             "n_accepted": len(cids), "f1_20m": f1, "mcc": mcc})

    return {"cell": name, "size": size, "n_candidates": n_present,
            "max_proposer_k": max_pk, "n_iterations": n_iter,
            "n_unique_accepted_sets": len(cache), "grid": grid}


def summarise(cell_result: dict, prob_ts: list[float]) -> dict:
    """Derive the two headline answers from a cell's grid.

    - determinism: for each proposer_k, the SD of F1 across the N single
      iterations at each candidate's best single-run prob_t, plus the consensus
      (majority vt) F1 for comparison.
    - proposer optimum: the (rule, prob_t, proposer_k) maximising F1@20 m.
    """
    grid = cell_result["grid"]
    n_iter = cell_result["n_iterations"]

    # Best overall operating point (the proposer-input answer).
    best = max(grid, key=lambda g: g["f1_20m"])

    # Determinism: at the best single-run prob_t per proposer_k, spread across iters.
    determinism = []
    for pk in range(1, cell_result["max_proposer_k"] + 1):
        rows_pk = [g for g in grid if g["proposer_k"] == pk]
        # pick the prob_t maximising the mean single-run F1 at this pk
        best_pt, best_mean, best_f1s = None, -1.0, []
        for pt in prob_ts:
            f1s = [g["f1_20m"] for g in rows_pk
                   if g["prob_t"] == pt and g["rule"].startswith("iter")]
            if f1s and statistics.mean(f1s) > best_mean:
                best_mean, best_pt, best_f1s = statistics.mean(f1s), pt, f1s
        # consensus majority (vt = ceil(N/2)) at that prob_t
        vt = (n_iter // 2) + 1
        cons = next((g["f1_20m"] for g in rows_pk
                     if g["prob_t"] == best_pt and g["rule"] == f"consensus_vt{vt}"), None)
        determinism.append({
            "proposer_k": pk, "prob_t": best_pt,
            "single_run_f1_mean": round(best_mean, 4) if best_f1s else None,
            "single_run_f1_sd": round(statistics.pstdev(best_f1s), 4) if len(best_f1s) > 1 else 0.0,
            "single_run_f1_min": round(min(best_f1s), 4) if best_f1s else None,
            "single_run_f1_max": round(max(best_f1s), 4) if best_f1s else None,
            "consensus_majority_f1": round(cons, 4) if cons is not None else None,
        })

    return {
        "cell": cell_result["cell"],
        "best_operating_point": best,
        "determinism_by_proposer_k": determinism,
    }


def main() -> int:
    """CLI entry point."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cells", type=Path, default=DEFAULT_CELLS)
    p.add_argument("--output-root", type=Path, default=DEFAULT_OUTROOT)
    p.add_argument("--temperature", type=float, required=True)
    p.add_argument("--iterations", type=int, default=None)
    p.add_argument("--prob-t", type=float, nargs="+", default=None,
                   help="prob_t sweep (default: from cells spec)")
    p.add_argument("--out-dir", type=Path,
                   default=BASE_DIR / "results" / "verifier-robustness")
    args = p.parse_args()

    spec = json.loads(args.cells.read_text())
    n_iter = args.iterations if args.iterations is not None else spec["iterations"]
    prob_ts = args.prob_t if args.prob_t is not None else spec["prob_t_sweep"]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    gdf_ref = load_geojson(GROUND_TRUTH)  # ground truth loaded once for all cells
    all_results, all_summaries = [], []
    for cell in spec["cells"]:
        print(f"=== analysing {cell['name']} (T={args.temperature}) ===", flush=True)
        res = analyse_cell(cell, args.output_root, args.temperature, prob_ts, n_iter, gdf_ref)
        summ = summarise(res, prob_ts)
        all_results.append(res)
        all_summaries.append(summ)
        bop = summ["best_operating_point"]
        print(f"  best F1@20m={bop['f1_20m']:.4f} (proposer {bop['proposer_k']}of5, "
              f"{bop['rule']}, prob_t={bop['prob_t']}, MCC={bop['mcc']})", flush=True)
        for d in summ["determinism_by_proposer_k"]:
            print(f"    proposer {d['proposer_k']}of5 @ prob_t={d['prob_t']}: "
                  f"single-run F1 {d['single_run_f1_mean']}±{d['single_run_f1_sd']} "
                  f"[{d['single_run_f1_min']},{d['single_run_f1_max']}] | "
                  f"consensus {d['consensus_majority_f1']}", flush=True)

    tag = f"T{args.temperature}"
    (args.out_dir / f"robustness_grid_{tag}.json").write_text(
        json.dumps({"temperature": args.temperature, "iterations": n_iter,
                    "prob_t_sweep": prob_ts, "cells": all_results}, indent=2))
    (args.out_dir / f"robustness_summary_{tag}.json").write_text(
        json.dumps({"temperature": args.temperature, "summaries": all_summaries}, indent=2))
    print(f"\nWrote {args.out_dir}/robustness_{{grid,summary}}_{tag}.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
