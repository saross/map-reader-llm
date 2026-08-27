#!/usr/bin/env python3
"""
55-map portfolio secondary analyses: the sweep, the new oracle, and A-vs-B.

Answers the PI's two questions (2026-08-27) inside the card's § 3
secondary contract:

1. **The full (prob_t × k) sweep at 50 m per run** — every achievable
   operating point scored against the SAME fixed extended GT the primary
   evaluation used (Approach B at R = 50: student GT + canonical
   reviewer-promoted phantoms; detection-independent, so built once and
   reused). The sweep's best point is the run's **deployment oracle**;
   the gap from the registered primary point is the measured
   calibration-transfer cost, and the drift direction settles bets
   P1–P4/P8.

2. **Paired A-versus-B permutation** — per-map (55 sheets) TP/FP/FN at
   the primary points and at the oracles; paired sign-swap permutation
   (10,000, seed 42) of the corrected-F1 difference, the S104
   instrument. Settles P6 and the is-B-worth-its-cost question.

REPLICATION GATE: the sweep's value at each run's registered primary
point must equal the engine's committed evaluation @50 m to 1e-6
(`results/stride55-2026-08-27/<run>/primary/eval/corrected-f1.csv`), or
nothing is written — this proves the in-process replication of the
engine's matching chain before any derived number is trusted.

Usage::

    python scripts/stride55_sweep_oracle.py

Zero API. Run on sapphire (~320 sweep points × 55 Hungarian problems).

Created: 2026-08-27 (Session 142)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import csv as csvmod
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    DEFAULT_CRS,
    REF_MAP_COL,
    build_extended_gt,
    build_phantom_gdf,
    compute_counts_at_r,
    compute_point_estimate,
)
from scripts.lib_advanced_metrics import (  # noqa: E402
    get_map_name,
    match_detections_to_references,
    scope_references_to_tiles,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

VROOT = PROJECT_ROOT / "outputs/stride-55map-2026-08-25/verifier"
OUT_BASE = PROJECT_ROOT / "results/stride55-2026-08-27"
STUDENT_GT = PROJECT_ROOT / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
CANONICAL_REVIEW = (
    PROJECT_ROOT / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv")

BUFFER_R = 50
N_PERMS = 10_000
SEED = 42

RUNS = {
    "g384_ov128_55map": {"union_n": 38713, "primary": (0.15, 8)},
    "g384_ov192_55map": {"union_n": 57482, "primary": (0.15, 10)},
}


def load_candidates(cell: str, spec: dict,
                    bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Full candidate set with probabilities and standard-grid source tiles."""
    vdir = VROOT / cell
    manifest = json.loads((vdir / "crops" / "candidate_manifest.json").read_text())
    results = json.loads((vdir / "verify" / "probabilities.json").read_text())["results"]
    cands = manifest["candidates"]
    if len(cands) != spec["union_n"] or len(results) != spec["union_n"]:
        raise RuntimeError(f"{cell}: count gate failed")
    if set(results) != {f"candidate_{i:05d}" for i in range(spec["union_n"])}:
        raise RuntimeError(f"{cell}: key gate failed")
    from scripts.stride55_score import (
        assign_standard_tile,
        build_map_constrained_index,
    )
    index = build_map_constrained_index()
    xs = [c["centroid_x"] for c in cands]
    ys = [c["centroid_y"] for c in cands]
    tiles = [assign_standard_tile(index, c["source_tile"],
                                  c["centroid_x"], c["centroid_y"])
             for c in cands]
    gdf = gpd.GeoDataFrame(
        {
            "candidate_id": [c["candidate_id"] for c in cands],
            "vote_count": [c.get("properties", {}).get("vote_count", 0)
                           for c in cands],
            "mound_probability": [
                float(results[f"candidate_{c['candidate_id']:05d}"]
                      ["mound_probability"]) for c in cands],
            "source_tile": tiles,
        },
        geometry=gpd.points_from_xy(xs, ys), crs=DEFAULT_CRS)
    return gdf


def per_map_counts(gdf_det: gpd.GeoDataFrame, gdf_ext: gpd.GeoDataFrame,
                   bounds: gpd.GeoDataFrame) -> dict[str, tuple[int, int, int]]:
    """Per-map (TP, FP, FN) at BUFFER_R — the paired-permutation input."""
    maps = {get_map_name(n) for n in bounds["tile_name"].unique()}
    maps.discard("Unknown")
    out: dict[str, tuple[int, int, int]] = {}
    for m in sorted(maps):
        mb = bounds[bounds["tile_name"].str.startswith(m)]
        ref = gdf_ext[gdf_ext[REF_MAP_COL] == m]
        ref = scope_references_to_tiles(ref, mb) if not ref.empty else ref
        det = gdf_det[gdf_det["source_tile"].str.startswith(m)]
        if det.empty and ref.empty:
            out[m] = (0, 0, 0)
            continue
        if det.empty:
            out[m] = (0, 0, len(ref))
            continue
        if ref.empty:
            out[m] = (0, len(det), 0)
            continue
        md, _, ud, ur = match_detections_to_references(
            list(det.geometry), list(ref.geometry), BUFFER_R)
        out[m] = (len(md), len(ud), len(ur))
    return out


def f1_from_map_counts(counts: dict[str, tuple[int, int, int]]) -> float:
    tp = sum(c[0] for c in counts.values())
    fp = sum(c[1] for c in counts.values())
    fn = sum(c[2] for c in counts.values())
    return compute_point_estimate(tp, fp, fn)[2]


def paired_permutation(a: dict, b: dict) -> dict:
    """Paired sign-swap permutation of corrected-F1 over the 55 maps."""
    maps = sorted(a)
    assert maps == sorted(b)
    rng = np.random.default_rng(SEED)
    obs = f1_from_map_counts(a) - f1_from_map_counts(b)
    arr_a = np.array([a[m] for m in maps])
    arr_b = np.array([b[m] for m in maps])
    count = 0
    for _ in range(N_PERMS):
        swap = rng.random(len(maps)) < 0.5
        pa = np.where(swap[:, None], arr_b, arr_a).sum(axis=0)
        pb = np.where(swap[:, None], arr_a, arr_b).sum(axis=0)
        d = (compute_point_estimate(*pa)[2] - compute_point_estimate(*pb)[2])
        if abs(d) >= abs(obs):
            count += 1
    return {"delta_f1": float(obs),
            "p_two_sided": max(count / N_PERMS, 1.0 / N_PERMS),
            "n_permutations": N_PERMS, "seed": SEED}


def main() -> int:
    student = gpd.read_file(STUDENT_GT).to_crs(DEFAULT_CRS)
    bounds = gpd.read_file(BOUNDS).to_crs(DEFAULT_CRS)
    empty_y = pd.DataFrame(columns=[
        "candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"])
    review_t = pd.read_csv(CANONICAL_REVIEW)
    phantoms = build_phantom_gdf(empty_y, review_t, BUFFER_R)
    ext_gt = build_extended_gt(student, phantoms)
    logger.info("extended GT at %dm: %d (student %d + phantoms %d, deduped)",
                BUFFER_R, len(ext_gt), len(student), len(phantoms))

    payload: dict = {"buffer_m": BUFFER_R, "runs": {}}
    map_counts_at: dict[str, dict] = {}
    for cell, spec in RUNS.items():
        gdf = load_candidates(cell, spec, bounds)
        thresholds = sorted({0.0} | {round(float(v), 4)
                                     for v in gdf["mound_probability"]})
        rows = []
        for prob_t in thresholds:
            for k in range(1, 11):
                sub = gdf[(gdf["mound_probability"] >= prob_t)
                          & (gdf["vote_count"] >= k)]
                tp, fp, fn, nref = compute_counts_at_r(sub, ext_gt, bounds,
                                                       BUFFER_R)
                p, r, f1 = compute_point_estimate(tp, fp, fn)
                rows.append({"cell": cell, "prob_t": prob_t, "min_votes": k,
                             "n_detections": int(len(sub)), "tp": tp,
                             "fp": fp, "fn": fn, "precision": p, "recall": r,
                             "corrected_f1": f1})
        # Replication gate against the engine's committed primary value.
        pt, pk = spec["primary"]
        prim = next(r for r in rows
                    if r["prob_t"] == pt and r["min_votes"] == pk)
        committed = None
        with (OUT_BASE / cell / "primary" / "eval" /
              "corrected-f1.csv").open() as fh:
            for row in csvmod.DictReader(fh):
                if int(row["R_m"]) == BUFFER_R:
                    committed = float(row["F1"])
        if committed is None or abs(prim["corrected_f1"] - committed) > 1e-6:
            raise RuntimeError(
                f"{cell}: replication gate FAILED — sweep primary "
                f"{prim['corrected_f1']:.6f} vs committed {committed}")
        logger.info("%s: replication gate OK (%.6f)", cell,
                    prim["corrected_f1"])

        best = max(rows, key=lambda r: r["corrected_f1"])
        logger.info(
            "%s: PRIMARY %.4f at (%.2f, k%d) | ORACLE %.4f at (%.2f, k%d) "
            "| transfer gap %.4f",
            cell, prim["corrected_f1"], pt, pk, best["corrected_f1"],
            best["prob_t"], best["min_votes"],
            best["corrected_f1"] - prim["corrected_f1"])
        payload["runs"][cell] = {"primary": prim, "oracle": best,
                                 "n_sweep_rows": len(rows)}

        out_csv = OUT_BASE / cell / "sweep_50m.csv"
        with out_csv.open("w", newline="") as fh:
            w = csvmod.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

        for tag, (tprob, tk) in (("primary", (pt, pk)),
                                 ("oracle", (best["prob_t"],
                                             best["min_votes"]))):
            sub = gdf[(gdf["mound_probability"] >= tprob)
                      & (gdf["vote_count"] >= tk)]
            map_counts_at[f"{cell}:{tag}"] = per_map_counts(sub, ext_gt, bounds)

    a, b = "g384_ov128_55map", "g384_ov192_55map"
    payload["paired_A_vs_B"] = {
        "at_primaries": paired_permutation(
            map_counts_at[f"{a}:primary"], map_counts_at[f"{b}:primary"]),
        "at_oracles": paired_permutation(
            map_counts_at[f"{a}:oracle"], map_counts_at[f"{b}:oracle"]),
        "convention": "delta = A(384/33.3) - B(384/50), corrected-F1@50m",
    }
    for tag, res in payload["paired_A_vs_B"].items():
        if isinstance(res, dict) and "delta_f1" in res:
            logger.info("A - B %s: dF1=%+.4f p=%.4f", tag,
                        res["delta_f1"], res["p_two_sided"])

    (OUT_BASE / "sweep_oracle.json").write_text(
        json.dumps(payload, indent=2) + "\n")
    logger.info("SWEEP-ORACLE COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
