#!/usr/bin/env python3
"""
Final 55-map board, stage 1: gates, oracle re-sweeps, cell materialisation.

Executes §§ 3–5 of `planning/55map-final-board-2026-08-27.md` (PI
sign-off 2026-08-27). Every oracle cell on the final board is the
STANDARDISED-REFERENCE argmax within its run's verified sweep space
(PI ruling: the oracle column claims the theoretical maximum, so the
argmax is computed on the board's own reference, uniformly):

- Runs A/B and their N ∈ {1, 3, 5} rungs: the full vote ≥ 1 unions
  (rungs rebuilt by the gated first-N derivation with inherited
  K = 10 verification).
- Text incumbents (TH7 / T03 / TM): the original vote ≥ 4
  verification merged with the S104 vote-3 increment — the same
  two-pass union their committed k3 cells were built from;
  k ∈ {3, 4, 5}.
- Image: its own vote ≥ 3 verified union; k ∈ {3, 4, 5}.
- Uplift: the ≥ 3-of-10 verified band; k ∈ {3..10}.

Scorer: per-map Hungarian → per-tile counts → micro-F1 @ 50 m
(`lib_advanced_metrics.compute_per_tile_tp_fp_fn` + `micro_f1` — the
board instrument's own counting path, with uniform spatial tile
assignment via `assign_source_tiles`, so sweep argmaxes and board
tiers share one mechanism).

GATES (card § 5; nothing is written unless all pass):

- G4 sweep-scorer gate: the light scorer reproduces the committed
  standardised-board F1@50 for all 8 board cells + IM-k4 within the
  documented mechanism bound (0.003).
- Family identity gates: thresholding each family at its committed
  operating point reproduces the committed cell's detection count
  EXACTLY (TH7-k3 4,786; T03-k3 4,905; TM-k3 4,279; IM-k3 4,680;
  uplift 4,361; A-N10 4,475; B-N10 4,505; A-N5 4,597; B-N5 4,736).

Outputs (results/55map-final-board-2026-08-27/): sweeps.json,
per-family sweep CSVs, cells/<label>/detections.geojson for every
non-committed cell, and cells_manifest.json for stages 2 (full
evaluations) and 3 (board build).

Usage::

    python scripts/final_board_sweeps.py [--workers N]

Zero API. Run on sapphire.

Created: 2026-08-27 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
import logging
import sys
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.build_55map_leaderboard import (  # noqa: E402
    BOUNDS,
    standardised_gt,
)
from scripts.score_55maps_standardised_reference import (  # noqa: E402
    CELLS as BOARD_CELLS,
)
from scripts.lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
)
from scripts.n1_baseline_leaderboard_tiering import micro_f1  # noqa: E402
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402
from scripts.stride55_ladder import (  # noqa: E402
    INHERIT_TOL_M,
    cluster_first_n,
    load_deduped_passes,
)
from scripts.stride55_score import build_map_constrained_index  # noqa: E402
from scripts.stride55_sweep_oracle import (  # noqa: E402
    RUNS as STRIDE_RUNS,
    load_candidates,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OUT = PROJECT_ROOT / "results/55map-final-board-2026-08-27"
BUFFER_M = 50
MECHANISM_BOUND = 0.003  # the board's documented micro-vs-eval bound
DEPLOY = PROJECT_ROOT / "results/deployment-oracle-2026-06-06/vote3-verify"
IMK4_DET = (PROJECT_ROOT / "results/55maps-standardised-ref-2026-08-14"
            / "IM-k4/k4_verified_detections.geojson")
IMK4_F1_50 = 0.74  # committed evaluation.json @50 (2026-08-23)

# Family identity gates: committed operating point -> exact count.
IDENTITY = {
    "TH7": ((0.15, 3), 4786), "T03": ((0.15, 3), 4905),
    "TM": ((0.15, 3), 4279), "IM": ((0.15, 3), 4680),
    "UPL": ((0.15, 5), 4361),
    "A-N10": ((0.15, 8), 4475), "B-N10": ((0.15, 10), 4505),
    "A-N5": ((0.15, 4), 4597), "B-N5": ((0.15, 5), 4736),
}

# Carried cells whose full evaluations are already committed.
COMMITTED_CARRIED = [
    ("TH7-k4", "outputs/55maps-text-high-generalisation/verified/"
               "verified_detections.geojson"),
    ("T03-k4", "outputs/55maps-text-high-t0.3-generalisation/verified/"
               "verified_detections.geojson"),
    ("TM-k4", "outputs/55maps-text-min-generalisation/verified/"
              "verified_detections.geojson"),
    ("IM-k4", "results/55maps-standardised-ref-2026-08-14/IM-k4/"
              "k4_verified_detections.geojson"),
]

_G: dict = {}  # worker globals


def prob_key(candidate_id) -> str:
    """probabilities.json key for a manifest candidate_id."""
    return (f"candidate_{candidate_id:05d}" if isinstance(candidate_id, int)
            else str(candidate_id))


def load_manifest_probs(cdir: Path, vdir: Path) -> gpd.GeoDataFrame:
    """Candidates + probabilities from an extract/verify pair (EPSG:32635)."""
    cands = json.loads(
        (cdir / "candidate_manifest.json").read_text())["candidates"]
    probs = json.loads((vdir / "probabilities.json").read_text())["results"]
    if len(cands) != len(probs):
        raise RuntimeError(
            f"{cdir}: {len(cands)} candidates vs {len(probs)} probabilities")
    return gpd.GeoDataFrame(
        {
            "vote_count": [c["properties"]["vote_count"] for c in cands],
            "mound_probability": [
                float(probs[prob_key(c["candidate_id"])]["mound_probability"])
                for c in cands],
        },
        geometry=gpd.points_from_xy([c["centroid_x"] for c in cands],
                                    [c["centroid_y"] for c in cands]),
        crs="EPSG:32635")


def build_families(bounds: gpd.GeoDataFrame) -> dict[str, dict]:
    """Every run's verified sweep space, per the card § 2."""
    fam: dict[str, dict] = {}
    for label, run in (("TH7", "55maps-text-high-generalisation"),
                       ("T03", "55maps-text-high-t0.3-generalisation"),
                       ("TM", "55maps-text-min-generalisation")):
        orig = load_manifest_probs(PROJECT_ROOT / "outputs" / run / "crops",
                                   PROJECT_ROOT / "outputs" / run / "verified")
        inc = load_manifest_probs(DEPLOY / run / "crops",
                                  DEPLOY / run / "verified")
        if not (orig["vote_count"] >= 4).all() or not (
                inc["vote_count"] == 3).all():
            raise RuntimeError(
                f"{label}: unexpected vote structure in the two-pass union")
        fam[label] = {"gdf": pd.concat([orig, inc], ignore_index=True),
                      "ks": (3, 4, 5)}
    im = PROJECT_ROOT / "outputs/55maps-image-generalisation"
    fam["IM"] = {"gdf": load_manifest_probs(im / "crops", im / "verified"),
                 "ks": (3, 4, 5)}
    upl = PROJECT_ROOT / "outputs/55maps-text-min-n10-uplift"
    fam["UPL"] = {"gdf": load_manifest_probs(upl / "crops-3of10",
                                             upl / "verified-3of10"),
                  "ks": tuple(range(3, 11))}

    from scipy.spatial import cKDTree
    index = build_map_constrained_index()
    for cell, key in (("g384_ov128_55map", "A"), ("g384_ov192_55map", "B")):
        spec = STRIDE_RUNS[cell]
        k10 = load_candidates(cell, spec, bounds)
        fam[f"{key}-N10"] = {"gdf": k10, "ks": tuple(range(1, 11))}
        passes = load_deduped_passes(cell)
        tree = cKDTree(np.c_[k10.geometry.x, k10.geometry.y])
        probs10 = k10["mound_probability"].to_numpy()
        for n in (1, 3, 5):
            gdf = cluster_first_n(passes, n, index)
            d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
            gdf["mound_probability"] = probs10[idx]
            gdf = gdf[d <= INHERIT_TOL_M].copy()
            fam[f"{key}-N{n}"] = {"gdf": gdf, "ks": tuple(range(1, n + 1))}
    return fam


def _init(ref, bounds, family_gdfs):
    _G["ref"], _G["bounds"], _G["fams"] = ref, bounds, family_gdfs


def _score(task):
    fam_name, prob_t, k = task
    g = _G["fams"][fam_name]
    sub = g[(g["mound_probability"] >= prob_t) & (g["vote_count"] >= k)]
    tm = compute_per_tile_tp_fp_fn(sub, _G["ref"], _G["bounds"],
                                   buffer_metres=BUFFER_M)
    tp, fp, fn = (int(tm["tp"].sum()), int(tm["fp"].sum()),
                  int(tm["fn"].sum()))
    return {"family": fam_name, "prob_t": prob_t, "min_votes": k,
            "n_detections": int(len(sub)), "tp": tp, "fp": fp, "fn": fn,
            "micro_f1_50": micro_f1(tp, fp, fn)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    ref = standardised_gt()
    bounds = gpd.read_file(BOUNDS)
    if bounds.crs is None:
        bounds = bounds.set_crs("EPSG:4326")
    bounds = bounds.to_crs("EPSG:32635")

    # G4: the light scorer reproduces the committed standardised board.
    board = json.loads(
        (PROJECT_ROOT / "results/55map-leaderboard"
         / "55map_leaderboard_50m_standardised.json").read_text())
    committed = {c["name"].split(" ")[0]: c["f1_50"] for c in board["cells"]}
    checks = [(c["label"], PROJECT_ROOT / c["det"], committed[c["label"]])
              for c in BOARD_CELLS if c["label"] in committed]
    checks.append(("IM-k4", IMK4_DET, IMK4_F1_50))
    for label, det_path, f1_committed in checks:
        det = gpd.read_file(det_path).to_crs("EPSG:32635")
        det = assign_source_tiles(det, bounds)
        tm = compute_per_tile_tp_fp_fn(det, ref, bounds,
                                       buffer_metres=BUFFER_M)
        f1 = micro_f1(int(tm["tp"].sum()), int(tm["fp"].sum()),
                      int(tm["fn"].sum()))
        if abs(f1 - f1_committed) > MECHANISM_BOUND:
            raise RuntimeError(
                f"G4 FAILED {label}: micro {f1:.6f} vs committed "
                f"{f1_committed:.6f}")
        logger.info("G4 OK %-8s micro %.4f vs committed %.4f (d %+.4f)",
                    label, f1, f1_committed, f1 - f1_committed)

    families = build_families(bounds)
    for name, spec in families.items():
        spec["gdf"] = assign_source_tiles(spec["gdf"], bounds)

    # Family identity gates.
    for name, ((pt, pk), expected) in IDENTITY.items():
        g = families[name]["gdf"]
        n = int(((g["mound_probability"] >= pt)
                 & (g["vote_count"] >= pk)).sum())
        if n != expected:
            raise RuntimeError(
                f"identity gate FAILED {name}: {n} at ({pt}, k{pk}) vs "
                f"committed {expected}")
        logger.info("identity OK %-6s (%.2f, k%d) -> %d", name, pt, pk, n)

    # Sweeps (parallel over points; family frames shared via initargs).
    tasks = []
    for name, spec in families.items():
        thresholds = sorted({0.0} | {round(float(v), 4)
                                     for v in spec["gdf"]["mound_probability"]})
        tasks.extend((name, prob_t, k)
                     for prob_t in thresholds for k in spec["ks"])
    logger.info("sweeping %d points across %d families (%d workers)",
                len(tasks), len(families), args.workers)
    family_gdfs = {n: s["gdf"] for n, s in families.items()}
    with Pool(args.workers, initializer=_init,
              initargs=(ref, bounds, family_gdfs)) as pool:
        rows = pool.map(_score, tasks, chunksize=4)

    OUT.mkdir(parents=True, exist_ok=True)
    sweeps: dict = {"buffer_m": BUFFER_M, "reference": "standardised",
                    "families": {}}
    for name in families:
        frows = sorted((r for r in rows if r["family"] == name),
                       key=lambda r: -r["micro_f1_50"])
        with (OUT / f"sweep_{name}.csv").open("w", newline="") as fh:
            w = csvmod.DictWriter(fh, fieldnames=list(frows[0].keys()))
            w.writeheader()
            w.writerows(sorted(frows, key=lambda r: (r["prob_t"],
                                                     r["min_votes"])))
        best = frows[0]
        sweeps["families"][name] = {
            "n_sweep_points": len(frows), "argmax": best, "top3": frows[:3]}
        logger.info("%-6s oracle: micro %.4f at (%.2f, k%d) | runners: %s",
                    name, best["micro_f1_50"], best["prob_t"],
                    best["min_votes"],
                    ", ".join(f"{r['micro_f1_50']:.4f}@({r['prob_t']:.2f},"
                              f"k{r['min_votes']})" for r in frows[1:3]))

    # Cells manifest: committed carried incumbents + materialised new cells.
    manifest_cells: list[dict] = [
        {"label": label, "det": det, "basis": "carried",
         "point": "(0.15, k4)", "committed_eval": True}
        for label, det in COMMITTED_CARRIED]

    def materialise(name: str, label: str, basis: str,
                    pt: float, pk: int) -> None:
        g = families[name]["gdf"]
        sub = g[(g["mound_probability"] >= pt) & (g["vote_count"] >= pk)]
        dest = OUT / "cells" / label / "detections.geojson"
        dest.parent.mkdir(parents=True, exist_ok=True)
        sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
        manifest_cells.append({
            "label": label, "det": str(dest.relative_to(PROJECT_ROOT)),
            "basis": basis, "point": f"({pt:.2f}, k{pk})",
            "committed_eval": False})

    for name in families:
        best = sweeps["families"][name]["argmax"]
        materialise(name, f"{name}-oracle",
                    "oracle (standardised-reference argmax)",
                    best["prob_t"], best["min_votes"])
        if name in ("A-N10", "B-N10", "A-N5", "B-N5"):
            (pt, pk), _ = IDENTITY[name]
            materialise(name, f"{name}-carried", "carried", pt, pk)

    (OUT / "sweeps.json").write_text(json.dumps(sweeps, indent=2) + "\n")
    (OUT / "cells_manifest.json").write_text(
        json.dumps({"cells": manifest_cells}, indent=2) + "\n")
    logger.info("STAGE 1 COMPLETE: %d cells in the manifest",
                len(manifest_cells))
    return 0


if __name__ == "__main__":
    sys.exit(main())
