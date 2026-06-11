#!/usr/bin/env python3
# ============================================================================
# build_55map_leaderboard.py
# ----------------------------------------------------------------------------
# Session 112: the 55-map generalisation leaderboard at the canonical 50 m
# working buffer (Shawn-approved 2026-06-11; derivation:
# results/working-precision/55maps-csr-noise-floor.json — observed gains die
# at 50 m, CSR chance-matching negligible, attribution ambiguity rises
# steeply beyond).
#
# CELLS: the seven canonical-GT conditions (the S105 two-reference set).
# REFERENCE: the canonical adjudicated GT at R=50 — 4,746 reviewed student
# points + the 415 phantoms gated <= 50 m (per-buffer gating per
# build_canonical_gt; phantoms ARE additional GT points for matching).
#
# METHOD (project-canonical): per-tile TP/FP/FN at 50 m (Hungarian per map,
# 8,541-tile order) -> C(7,2)=21 round-robin tile-swap micro-F1 permutation
# tests (10k, seed 42, two-sided) -> BH-FDR q=0.05 -> greedy-clique tiers.
# GATE: each cell's per-tile micro-F1 must reproduce its committed
# evaluation F1@50m within 0.003 (mechanism equivalence check).
#
# COST: $0 (on-disk). Run on zbook (8,541-tile Hungarian x 7 cells).
#
# Usage:
#   .venv/bin/python scripts/build_55map_leaderboard.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    greedy_clique_tiers,
    micro_f1,
    permutation_test_float,
)
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402

BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
STUDENT_GT = BASE_DIR / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
PHANTOMS = BASE_DIR / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv"
RUN_CONDS = BASE_DIR / "results/run-conditions.json"
OUT_DIR = BASE_DIR / "results/55map-leaderboard"
BUFFER_M = 50
GATE_TOL = 0.003

# Short display names for the seven canonical-GT cells, keyed by
# (run_id, label). Matches the S105 findings-doc naming.
NAMES = {
    ("55maps-text-high-t0-3-generalisation", "verified-k3-canonical-gt"): "T03-k3 (oracle)",
    ("55maps-text-high-t0-3-generalisation", "verified-k4-canonical-gt"): "T03-k4",
    ("55maps-text-high-generalisation", "verified-k3-canonical-gt"): "TH7-k3",
    ("55maps-text-high-generalisation", "verified-k4-canonical-gt"): "TH7-k4 (carry-forward)",
    ("55maps-text-min-generalisation", "verified-k3-canonical-gt"): "TM-k3",
    ("55maps-text-min-generalisation", "verified-k4-canonical-gt"): "TM-k4",
    ("55maps-image-generalisation", "verified-k3-canonical-gt"): "IM-k3",
}


def canonical_gt_at(r_m: float) -> gpd.GeoDataFrame:
    """The canonical GT at buffer R: reviewed students + phantoms gated <= R.

    Carries ``source_map`` (required by the per-map Hungarian matcher):
    students from their own property, phantoms from the review CSV.
    """
    s = gpd.read_file(STUDENT_GT).to_crs("EPSG:32635")
    pts = list(s.geometry)
    maps = list(s["source_map"])
    with open(PHANTOMS) as fh:
        for row in csv.DictReader(fh):
            if float(row["buffer_metres"]) <= r_m:
                pts.append(Point(float(row["x"]), float(row["y"])))
                maps.append(row["map_name"])
    return gpd.GeoDataFrame({"geometry": pts, "source_map": maps}, crs="EPSG:32635")


def main() -> int:
    """Build the 50 m canonical-GT board with round-robin tiers."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf_bounds = gpd.read_file(BOUNDS)
    if gdf_bounds.crs is None:
        gdf_bounds = gdf_bounds.set_crs("EPSG:4326")
    gdf_bounds = gdf_bounds.to_crs("EPSG:32635")
    tile_order = sorted(gdf_bounds["tile_name"].tolist())
    tile_index = {t: i for i, t in enumerate(tile_order)}
    gdf_ref = canonical_gt_at(BUFFER_M)
    print(f"canonical GT at {BUFFER_M} m: {len(gdf_ref)} points; "
          f"{len(tile_order)} tiles", flush=True)

    dec = json.loads(RUN_CONDS.read_text())["decomposition"]
    cells = []
    for (run_id, label), name in NAMES.items():
        cond = next(c for c in dec[run_id]["conditions"] if c["label"] == label)
        det = gpd.read_file(BASE_DIR / cond["detections"])
        crs = "EPSG:32635" if abs(det.geometry.x.iloc[0]) > 180 else "EPSG:4326"
        det = det.set_crs(crs, allow_override=True).to_crs("EPSG:32635")
        det = assign_source_tiles(det, gdf_bounds)
        tm = compute_per_tile_tp_fp_fn(det, gdf_ref, gdf_bounds, buffer_metres=BUFFER_M)
        tp = np.zeros(len(tile_order))
        fp = np.zeros(len(tile_order))
        fn = np.zeros(len(tile_order))
        for _, row in tm.iterrows():
            i = tile_index.get(row["tile_name"])
            if i is not None:
                tp[i], fp[i], fn[i] = float(row["tp"]), float(row["fp"]), float(row["fn"])

        ev = json.loads((BASE_DIR / cond["eval_path"]).read_text())["summary"]
        ev50 = next(b for b in ev["buffers"] if b["buffer_metres"] == BUFFER_M)
        board_f1 = micro_f1(tp.sum(), fp.sum(), fn.sum())
        ok = abs(board_f1 - ev50["f1"]) <= GATE_TOL
        print(f"  {name:<24} board F1@50={board_f1:.4f} eval={ev50['f1']:.4f} "
              f"{'ok' if ok else 'GATE FAIL'}", flush=True)
        if not ok:
            sys.exit(f"GATE FAIL: {name} board {board_f1:.4f} vs eval {ev50['f1']:.4f}")
        cells.append({
            "name": name, "condition_id": f"{run_id}::{label}",
            "f1_50": ev50["f1"], "ci": [ev50["f1_ci_lower"], ev50["f1_ci_upper"]],
            "precision_50": ev50["precision"], "recall_50": ev50["recall"],
            "mcc": (lambda m: m.get("point") if isinstance(m, dict) else m)(
                ev.get("tile_classification", {}).get("mcc")),
            "n_detections": ev["n_detections"],
            "tp": tp, "fp": fp, "fn": fn})

    print(f"\n=== round-robin ({len(cells)} cells, 10k tile-swap, seed 42) ===",
          flush=True)
    pairs, significant = [], {}
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            a, b = cells[i], cells[j]
            r = permutation_test_float(a["tp"], a["fp"], a["fn"],
                                       b["tp"], b["fp"], b["fn"],
                                       n_permutations=10000, seed=42)
            pairs.append({"a": a["name"], "b": b["name"], **r})
    adjusted = apply_bh_correction([p["p_value"] for p in pairs], q=0.05)
    for p, adj in zip(pairs, adjusted):
        p["bh_adjusted_p"] = round(adj, 6)
        p["significant"] = bool(adj < 0.05)
        significant[frozenset({p["a"], p["b"]})] = p["significant"]

    ordered = sorted(cells, key=lambda c: c["f1_50"], reverse=True)
    tiers = greedy_clique_tiers([c["name"] for c in ordered], significant)
    tier_of = {n: t for t, members in enumerate(tiers, 1) for n in members}
    n_sig = sum(1 for p in pairs if p["significant"])
    print(f"{n_sig}/{len(pairs)} pairs significant -> {len(tiers)} tier(s)", flush=True)

    md = ["# 55-map generalisation leaderboard — canonical GT @ 50 m",
          "",
          f"> Working buffer 50 m per the noise-floor derivation "
          f"(`results/working-precision/55maps-csr-noise-floor.json`). "
          f"Round-robin tile-swap permutation (10k, seed 42) + BH-FDR q=0.05 "
          f"+ greedy-clique tiers; {n_sig}/{len(pairs)} pairs significant.",
          "",
          "| rank | cell | tier | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | n |",
          "|---:|---|---:|---:|---|---:|---:|---:|---:|"]
    for i, c in enumerate(ordered, 1):
        mcc = f"{c['mcc']:.3f}" if c["mcc"] is not None else "—"
        md.append(f"| {i} | {c['name']} | {tier_of[c['name']]} | {c['f1_50']:.4f} "
                  f"| [{c['ci'][0]:.4f}, {c['ci'][1]:.4f}] | {c['precision_50']:.4f} "
                  f"| {c['recall_50']:.4f} | {mcc} | {c['n_detections']} |")
        print(f"{i}. {c['name']:<24} T{tier_of[c['name']]}  F1@50 {c['f1_50']:.4f}  "
              f"MCC {mcc}", flush=True)

    (OUT_DIR / "55map-leaderboard-50m.md").write_text("\n".join(md) + "\n")
    (OUT_DIR / "55map_leaderboard_50m.json").write_text(json.dumps({
        "buffer_m": BUFFER_M, "tiers": tiers,
        "cells": [{k: v for k, v in c.items() if k not in ("tp", "fp", "fn")}
                  for c in ordered],
        "pairwise": pairs}, indent=2, default=float) + "\n")
    print(f"\nWrote {OUT_DIR.relative_to(BASE_DIR)}/", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
