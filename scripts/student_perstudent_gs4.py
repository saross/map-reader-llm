#!/usr/bin/env python3
"""
Per-student GS-4 baseline: novices and model configs on identical ground.

Phase 0a/1a of `planning/student-baseline-2026-08-31.md`: decompose
the committed pooled GS-4 student baseline (P 1.000 / R 0.9473 /
F1 0.9729 at 50 m, `results/student-gt-fn-rate-analysis-gs4/`) into
per-student results within the 2023 QA audit-area polygons, at
matched radii 20/30/50 m, against the curator reference — and score
model configurations inside the SAME polygons so students and configs
rank on identical ground.

Method:

1. The committed reviewed GS-4 student layer (mound-filtered,
   collar-clipped) is ATTRIBUTED by nearest-neighbour join to the
   staged 2023 master layer (`mounds-attributed.geojson`), so the
   per-student split decomposes exactly the layer whose pooled
   numbers are committed.
2. Scoring unit = the five audit-area polygons (B, D, C-Rakovski,
   and the Elenovo A/C partition). Reference = curator GT clipped to
   the polygon; detections = attributed student points (or a model
   cell's verified detections) clipped to the same polygon;
   one-to-one Hungarian matching at each radius.
3. Student C is additionally scored with his three digitised
   missed-swath polygons EXCLUDED — separating coverage failure
   (attention) from perception failure, per the 2023 paper's own
   decomposition (error rate 10.6 % -> 2.8 % family of results).

REPLICATION GATE: pooled TP/FP/FN across the audit polygons at 50 m
must reproduce the committed GS-4 aggregate (TP 539 / FP 0 / FN 30)
exactly — the audit polygons tile the four sheets, so the per-student
split must sum to the committed baseline or nothing is written.

Model cells scored alongside (their GS verified sets clipped per
polygon): the 3.7 text screen best and the all-3.7 swap best. Caveat
recorded in the output: both are 20 m-optimised operating points, so
their 50 m rows slightly under-serve the model.

Usage::

    python scripts/student_perstudent_gs4.py

Zero API, seconds of compute (fine locally per the compute rule).

Created: 2026-09-01 (Session 145)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (  # noqa: E402
    match_detections_to_references,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

CRS = "EPSG:32635"
REVIEWED = PROJECT_ROOT / "inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson"
ACTIVE_AREA = PROJECT_ROOT / "inputs/vectors/bounds/gs-4maps-active-area-bounds.geojson"
CURATOR = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
#: The 487-tile GS evaluation footprint — the ONLY ground the model
#: cells ever saw. Model rows (and the like-for-like "footprint"
#: basis) are scored inside audit-polygon ∩ footprint; scoring the
#: model against full sheets charges it false negatives in areas it
#: was never shown (caught on this script's first run: recall 0.59 to
#: 0.91 by sheet with healthy precision — the partial-coverage
#: signature).
EVAL_FOOTPRINT = PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
STAGED = PROJECT_ROOT / "inputs/student-baseline-2023/staged"
OUT_DIR = PROJECT_ROOT / "results/student-baseline-2026-09-01/per-student-gs4"

#: Model cells to rank alongside the students (GS verified sets).
MODEL_CELLS = {
    "model:3.7-text-screen-best": PROJECT_ROOT
    / "results/gemini37-screen-2026-08-28/verified_best_20m.geojson",
    "model:all-3.7-swap-best": PROJECT_ROOT
    / "results/gemini37-screen-2026-08-28/swap37/verified_best_20m.geojson",
}

RADII = (20, 30, 50)
JOIN_TOL_M = 10.0  # attribution join; same-source data, expect ~0 m
COMMITTED_50 = {"tp": 539, "fp": 0, "fn": 30}


def score(det: gpd.GeoDataFrame, ref: gpd.GeoDataFrame,
          radius: float) -> dict:
    """One-to-one Hungarian P/R/F1 at ``radius`` metres."""
    if len(det) == 0 or len(ref) == 0:
        tp = 0
        fp, fn = len(det), len(ref)
    else:
        md, _, ud, ur = match_detections_to_references(
            list(det.geometry), list(ref.geometry), radius)
        tp, fp, fn = len(md), len(ud), len(ur)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return {"radius_m": radius, "tp": tp, "fp": fp, "fn": fn,
            "precision": p, "recall": r, "f1": f1,
            "n_det": int(len(det)), "n_ref": int(len(ref))}


def main() -> int:
    reviewed = gpd.read_file(REVIEWED).to_crs(CRS)
    active = gpd.read_file(ACTIVE_AREA).to_crs(CRS)
    curator = gpd.read_file(CURATOR).to_crs(CRS)
    areas = gpd.read_file(STAGED / "assignment-areas.geojson").to_crs(CRS)
    master = gpd.read_file(STAGED / "mounds-attributed.geojson")
    master = master[master.geometry.notna()].to_crs(CRS)

    # Collar-clip the reviewed layer exactly as the committed analysis.
    reviewed = gpd.sjoin(reviewed, active[["geometry"]], how="inner",
                         predicate="within").drop(columns="index_right")
    logger.info("reviewed GS-4 layer after active-area clip: %d",
                len(reviewed))

    # Attribute reviewed points by nearest staged master point.
    tree = cKDTree(np.c_[master.geometry.x, master.geometry.y])
    d, idx = tree.query(np.c_[reviewed.geometry.x, reviewed.geometry.y], k=1)
    reviewed["student_code"] = master["student_code"].to_numpy()[idx]
    reviewed["join_dist_m"] = d
    n_far = int((d > JOIN_TOL_M).sum())
    logger.info("attribution join: max %.2f m, p99 %.2f m, >%g m: %d",
                d.max(), np.percentile(d, 99), JOIN_TOL_M, n_far)
    if n_far:
        logger.warning("%d reviewed points join beyond %g m — attributed "
                       "to nearest anyway; inspect join_dist_m in output",
                       n_far, JOIN_TOL_M)

    audit = areas[areas["area_role"] == "audit_area"]
    swaths = areas[areas["area_role"] == "missed_swath"]
    swath_union = swaths.union_all()

    rows: list[dict] = []
    pooled = {"tp": 0, "fp": 0, "fn": 0}
    units: list[tuple[str, gpd.GeoDataFrame, gpd.GeoDataFrame]] = []
    for rec in audit.itertuples():
        label = f"student:{rec.student_code}@{rec.sheet_id}"
        poly = rec.geometry
        ref = curator[curator.within(poly)]
        det = reviewed[reviewed.within(poly)]
        att = det["student_code"].value_counts().to_dict()
        logger.info("%s: ref %d, det %d (attribution %s)",
                    label, len(ref), len(det), att)
        units.append((label, det, ref))
        for radius in RADII:
            row = {"unit": label, "student": rec.student_code,
                   "sheet": rec.sheet_id, "basis": "as-digitised",
                   **score(det, ref, radius)}
            rows.append(row)
            if radius == 50:
                for k in pooled:
                    pooled[k] += row[k]

    # Gate: the per-polygon split must sum to the committed aggregate.
    if pooled != COMMITTED_50:
        raise RuntimeError(
            f"replication gate FAILED — pooled {pooled} vs committed "
            f"{COMMITTED_50}")
    logger.info("replication gate OK — pooled 50 m %s", pooled)

    # Student C, coverage-corrected: swath polygons excluded.
    c_rak = audit[(audit["student_code"] == "C")
                  & (audit["sheet_id"] == "K-35-062-2_Rakovski")]
    poly = c_rak.union_all()
    ref = curator[curator.within(poly)
                  & ~curator.within(swath_union)]
    det = reviewed[reviewed.within(poly)
                   & ~reviewed.within(swath_union)]
    for radius in RADII:
        rows.append({"unit": "student:C@K-35-062-2_Rakovski",
                     "student": "C", "sheet": "K-35-062-2_Rakovski",
                     "basis": "swaths-excluded",
                     **score(det, ref, radius)})

    # Like-for-like ground: audit polygon ∩ evaluation footprint.
    # Students AND models are re-scored inside these zones so the
    # ranking compares performances on identical territory.
    footprint = gpd.read_file(EVAL_FOOTPRINT).to_crs(CRS).union_all()
    cells = {name: gpd.read_file(path).to_crs(CRS)
             for name, path in MODEL_CELLS.items()}
    zone_agg: dict[str, dict] = {
        name: {r: {"tp": 0, "fp": 0, "fn": 0} for r in RADII}
        for name in list(cells) + ["students-pooled"]}
    for rec in audit.itertuples():
        zone = rec.geometry.intersection(footprint)
        sheet, code = rec.sheet_id, rec.student_code
        ref = curator[curator.within(zone)]
        sdet = reviewed[reviewed.within(zone)]
        logger.info("zone %s[%s]: ref %d, student det %d",
                    sheet, code, len(ref), len(sdet))
        for radius in RADII:
            row = {"unit": f"student:{code}@{sheet}", "student": code,
                   "sheet": sheet, "basis": "footprint",
                   **score(sdet, ref, radius)}
            rows.append(row)
            for k in ("tp", "fp", "fn"):
                zone_agg["students-pooled"][radius][k] += row[k]
        for name, cell in cells.items():
            det = cell[cell.within(zone)]
            for radius in RADII:
                row = {"unit": f"{name}@{sheet}[{code}]",
                       "student": name, "sheet": sheet,
                       "basis": "footprint", **score(det, ref, radius)}
                rows.append(row)
                for k in ("tp", "fp", "fn"):
                    zone_agg[name][radius][k] += row[k]
    for name, agg in zone_agg.items():
        for radius in RADII:
            tp, fp, fn = (agg[radius][k] for k in ("tp", "fp", "fn"))
            p = tp / (tp + fp) if tp + fp else 0.0
            r = tp / (tp + fn) if tp + fn else 0.0
            rows.append({"unit": f"{name}@ALL-ZONES", "student": name,
                         "sheet": "ALL", "basis": "footprint",
                         "radius_m": radius, "tp": tp, "fp": fp,
                         "fn": fn, "precision": p, "recall": r,
                         "f1": 2 * p * r / (p + r) if p + r else 0.0,
                         "n_det": tp + fp, "n_ref": tp + fn})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    import csv as csvmod
    with (OUT_DIR / "per_student.csv").open("w", newline="") as fh:
        w = csvmod.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (OUT_DIR / "analysis.json").write_text(json.dumps({
        "committed_pooled_50m": COMMITTED_50,
        "replication_gate": "PASS",
        "attribution_join_max_m": float(d.max()),
        "model_cell_caveat": ("model sets are 20 m-optimised operating "
                              "points; 50 m rows under-serve the model"),
        "rows": rows}, indent=2) + "\n")
    logger.info("PER-STUDENT GS-4 COMPLETE -> %s",
                OUT_DIR.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
