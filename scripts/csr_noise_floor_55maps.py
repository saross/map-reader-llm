#!/usr/bin/env python3
# ============================================================================
# csr_noise_floor_55maps.py
# ----------------------------------------------------------------------------
# Session 111 ($0): the 55-map noise-floor check Shawn requested for the
# generalisation-track working precision — at what buffer does the signal
# fade into background noise / incidental detection?
#
# THREE components, each answering a different version of "noise":
#
# 1. CSR NULL (chance matching): per map, with N_m detections placed
#    uniformly at random over map area A_m (complete spatial randomness),
#    the expected number of GT mounds with >=1 detection within R is
#    M_m(R) x (1 - exp(-N_m pi R^2 / A_m)). Null precision/recall/F1
#    follow. The GT denominator M_m(R) honours the canonical-GT per-buffer
#    phantom gating (phantoms enter at R >= their review buffer).
#
# 2. MARGINAL noise: the per-step F1 gain a random process would produce,
#    compared with the observed per-step gains from the committed
#    canonical-GT evaluations — the "incidental detection" rate.
#
# 3. ATTRIBUTION-AMBIGUITY bound: at large R a detection stops being
#    attributable to a specific mound. The bound is half the GT
#    nearest-neighbour distance — we report the NN-distance distribution
#    and the share of mounds whose NN is within 2R at each canonical R
#    (cross-matching risk).
#
# Usage:
#   .venv/bin/python scripts/csr_noise_floor_55maps.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-10 | Apache 2.0
# ============================================================================
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

BASE_DIR = Path(__file__).resolve().parent.parent
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
STUDENT_GT = BASE_DIR / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
PHANTOMS = BASE_DIR / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv"
EVAL_ROOT = BASE_DIR / "results/55maps-extended-gt-2026-06-07"
OUT_DIR = BASE_DIR / "results" / "working-precision"
BUFFERS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]

# (cell label, detections geojson, eval dir) — the canonical-GT cells.
K3 = "results/deployment-oracle-2026-06-06/k3-scoring"
CELLS = [
    ("T03-k3 (oracle)", f"{K3}/55maps-text-high-t0.3-generalisation/k3_verified.geojson",
     "T03-k3"),
    ("TH7-k4 (carry-forward)",
     "outputs/55maps-text-high-generalisation/verified/verified_detections.geojson",
     "TH7-k4"),
]


def map_of(tile: str) -> str:
    """Map sheet id from a tile name (K-35-042-3_x3024_y1344.png -> K-35-042-3)."""
    return tile.rsplit("_x", 1)[0].split("_x")[0] if "_x" in tile else tile


def main() -> int:
    """Build CSR null curves, marginal comparison, and the ambiguity bound."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- per-map areas from the tile bounds ---------------------------------
    b = gpd.read_file(BOUNDS)
    g0 = b.geometry.iloc[0]
    tile_w = g0.bounds[2] - g0.bounds[0]
    tile_area = tile_w * (g0.bounds[3] - g0.bounds[1])
    tiles_per_map = Counter(map_of(t) for t in b["tile_name"])
    area = {m: n * tile_area for m, n in tiles_per_map.items()}
    print(f"{len(area)} maps, {len(b)} tiles, tile {tile_w:.0f} m "
          f"({tile_area / 1e6:.2f} km2)", flush=True)

    # --- GT: students (fixed) + phantoms (per-buffer gated) -----------------
    s = gpd.read_file(STUDENT_GT).to_crs("EPSG:32635")
    students = Counter(s["source_map"])
    s_xy = {m: np.c_[grp.geometry.x, grp.geometry.y]
            for m, grp in s.groupby("source_map")}
    phantoms = defaultdict(list)   # map -> list of (gate_buffer, x, y)
    with open(PHANTOMS) as fh:
        for row in csv.DictReader(fh):
            phantoms[row["map_name"]].append(
                (float(row["buffer_metres"]), float(row["x"]), float(row["y"])))
    gate_dist = Counter(g for plist in phantoms.values() for g, _, _ in plist)
    print(f"students {sum(students.values())}, phantoms "
          f"{sum(len(v) for v in phantoms.values())} (gate buffers: {dict(gate_dist)})",
          flush=True)

    def m_of(map_id: str, r: float) -> int:
        return students.get(map_id, 0) + sum(
            1 for g, _, _ in phantoms.get(map_id, []) if g <= r)

    # --- component 3: GT nearest-neighbour distances (full canonical GT) ----
    nn_all = []
    for m in area:
        pts = [s_xy[m]] if m in s_xy else []
        ph = phantoms.get(m, [])
        if ph:
            pts.append(np.array([[x, y] for _, x, y in ph]))
        if not pts:
            continue
        xy = np.vstack(pts)
        if len(xy) < 2:
            continue
        d, _ = cKDTree(xy).query(xy, k=2)
        nn_all.extend(d[:, 1].tolist())
    nn = np.array(nn_all)
    nn_pcts = {p: float(np.percentile(nn, p)) for p in (10, 25, 50, 75)}
    print(f"GT nearest-neighbour distance: p10 {nn_pcts[10]:.0f} m, "
          f"p25 {nn_pcts[25]:.0f} m, median {nn_pcts[50]:.0f} m", flush=True)
    ambiguity = {r: float((nn <= 2 * r).mean()) for r in BUFFERS}

    # --- components 1+2 per cell --------------------------------------------
    out_cells = []
    for label, det_path, eval_dir in CELLS:
        det = gpd.read_file(BASE_DIR / det_path)
        n_by_map = Counter(map_of(t) for t in det["source_tile"])
        ev = json.loads((EVAL_ROOT / eval_dir / "evaluation.json").read_text())
        obs = {int(r["buffer_metres"]): r["f1"] for r in ev["summary"]["buffers"]}

        rows = []
        for r in BUFFERS:
            tp = sum(m_of(m, r) * (1 - math.exp(-n_by_map.get(m, 0)
                                                * math.pi * r * r / area[m]))
                     for m in area)
            n_tot = sum(n_by_map.values())
            m_tot = sum(m_of(m, r) for m in area)
            p_null = tp / n_tot if n_tot else 0.0
            r_null = tp / m_tot if m_tot else 0.0
            f1_null = (2 * p_null * r_null / (p_null + r_null)
                       if p_null + r_null else 0.0)
            rows.append({"buffer_m": r, "f1_observed": obs.get(r),
                         "f1_null": round(f1_null, 4),
                         "ambiguity_frac": round(ambiguity[r], 3)})
        for i in range(1, len(rows)):
            rows[i]["obs_step_gain"] = (
                round(rows[i]["f1_observed"] - rows[i - 1]["f1_observed"], 4)
                if rows[i]["f1_observed"] is not None
                and rows[i - 1]["f1_observed"] is not None else None)
            rows[i]["null_step_gain"] = round(
                rows[i]["f1_null"] - rows[i - 1]["f1_null"], 4)
        out_cells.append({"cell": label, "detections": det_path,
                          "n_detections": int(sum(n_by_map.values())),
                          "curve": rows})
        print(f"\n{label}: {sum(n_by_map.values())} detections", flush=True)
        print("  R     obs-F1   null-F1  obs-step  null-step  NN<=2R", flush=True)
        for row in rows:
            print(f"  {row['buffer_m']:>3}  {row['f1_observed'] or 0:.4f}   "
                  f"{row['f1_null']:.4f}   {row.get('obs_step_gain', ''):>7}   "
                  f"{row.get('null_step_gain', ''):>7}   {row['ambiguity_frac']:.1%}",
                  flush=True)

    (OUT_DIR / "55maps-csr-noise-floor.json").write_text(json.dumps({
        "method": {"csr_null": "per-map Poisson chance-matching, GT honours "
                               "per-buffer phantom gating",
                   "ambiguity": "fraction of GT mounds whose nearest neighbour "
                                "is within 2R (cross-matching risk)"},
        "gt_nn_percentiles_m": nn_pcts,
        "ambiguity_by_buffer": ambiguity,
        "cells": out_cells}, indent=2) + "\n")
    print(f"\nWrote {OUT_DIR.relative_to(BASE_DIR)}/55maps-csr-noise-floor.json",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
