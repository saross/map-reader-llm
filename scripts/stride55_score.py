#!/usr/bin/env python3
"""
55-map portfolio scoring — the § 3 measurement contract, primary points.

Materialises each run's PRIMARY verified set at the pre-registered
operating point (card § 3: Run A prob_t ≥ 0.15, k ≥ 8; Run B prob_t ≥
0.15, k ≥ 10 — committed before launch) exactly per the deployment-era
precedent (`55maps-t0.3-rebuild-verified-geojson.py`: EPSG:32635 points
from the crop manifest's centroids, candidate_id / vote_count /
mound_probability properties), then scores it with the canonical-GT
corrected-F1 machinery in the Track-2 configuration
(`compute_corrected_f1_multi_buffer.py` with the canonical review CSV,
buffers 20/30/50, B = 10,000, seed 42, tile MCC).

Join gates per run: the crop manifest's candidate count equals the
committed union's; every candidate id has a probability; ids are the
contiguous range.

Usage::

    python scripts/stride55_score.py            # gates + materialise + score

Zero API. Run on sapphire (two 10,000-iteration bootstrap evaluations).

Created: 2026-08-27 (Session 142)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

VROOT = PROJECT_ROOT / "outputs/stride-55map-2026-08-25/verifier"
OUT_BASE = PROJECT_ROOT / "results/stride55-2026-08-27"
STUDENT_GT = PROJECT_ROOT / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson"
CANONICAL_REVIEW = (
    PROJECT_ROOT / "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv")

#: The pre-registered primary operating points (card § 3, committed
#: 2026-08-25 before launch).
RUNS = {
    "g384_ov128_55map": {"union_n": 38713, "prob_t": 0.15, "min_votes": 8,
                         "expect_f1_50": 0.8325895173845355},
    "g384_ov192_55map": {"union_n": 57482, "prob_t": 0.15, "min_votes": 10,
                         "expect_f1_50": 0.8422141748577341},
}


def build_map_constrained_index() -> dict:
    """Per-map KD-trees over the standard evaluation grid's tile centroids."""
    import geopandas as gpd
    import numpy as np
    from scipy.spatial import cKDTree

    from scripts.lib_advanced_metrics import get_map_name
    bounds = gpd.read_file(BOUNDS)
    index: dict = {}
    for name, geom in zip(bounds["tile_name"], bounds.geometry, strict=True):
        index.setdefault(get_map_name(name), {"names": [], "xy": []})
        m = index[get_map_name(name)]
        m["names"].append(name)
        m["xy"].append((geom.centroid.x, geom.centroid.y))
    for m in index.values():
        m["tree"] = cKDTree(np.asarray(m["xy"]))
    return index


def assign_standard_tile(index: dict, origin_tile: str,
                         x: float, y: float) -> str:
    """Nearest standard tile WITHIN the origin raster's map (E79-in-map)."""
    from scripts.lib_advanced_metrics import get_map_name
    m = index[get_map_name(origin_tile)]
    _, i = m["tree"].query([x, y], k=1)
    return m["names"][int(i)]


def materialise_primary(cell: str, spec: dict) -> Path:
    """Build one run's primary verified set from manifest + probabilities.

    Args:
        cell: Run label.
        spec: The registered operating point and expected union size.

    Returns:
        Path to the written EPSG:32635 GeoJSON.

    Raises:
        RuntimeError: On any join-gate failure.
    """
    vdir = VROOT / cell
    manifest = json.loads((vdir / "crops" / "candidate_manifest.json").read_text())
    results = json.loads((vdir / "verify" / "probabilities.json").read_text())["results"]
    cands = manifest["candidates"]
    if len(cands) != spec["union_n"]:
        raise RuntimeError(
            f"{cell}: crop manifest has {len(cands)} candidates, union "
            f"documented {spec['union_n']}")
    if len(results) != spec["union_n"]:
        raise RuntimeError(
            f"{cell}: {len(results)} probabilities vs {spec['union_n']} expected")
    expected_keys = {f"candidate_{i:05d}" for i in range(spec["union_n"])}
    if set(results) != expected_keys:
        raise RuntimeError(f"{cell}: probability keys not the contiguous range")

    # source_tile must name tiles of the STANDARD 55-map evaluation grid
    # (the engine's tile classification and tile-bootstrap CIs join on
    # them), but map ATTRIBUTION must stay the origin raster's map — the
    # protocol the incumbents' runs used for Hungarian scoping. The sheet
    # rasters overlap, so an UNCONSTRAINED nearest-centroid assignment
    # flips 10.1 % of candidates to the adjacent sheet (measured
    # 2026-08-27) and moves corrected-F1 by ~0.04 — an artefact, caught by
    # the first/second-pass divergence. Assignment is therefore
    # constrained to the origin map's own standard tiles.
    tile_index = build_map_constrained_index()

    kept = []
    for cand in cands:
        cid = cand["candidate_id"]
        vote = cand.get("properties", {}).get("vote_count", 0)
        prob = results[f"candidate_{cid:05d}"]["mound_probability"]
        if prob is None:
            raise RuntimeError(f"{cell}: null probability for candidate {cid}")
        if vote >= spec["min_votes"] and float(prob) >= spec["prob_t"]:
            tile = assign_standard_tile(
                tile_index, cand["source_tile"],
                cand["centroid_x"], cand["centroid_y"])
            kept.append({
                "type": "Feature",
                "geometry": {"type": "Point",
                             "coordinates": [cand["centroid_x"], cand["centroid_y"]]},
                "properties": {"candidate_id": cid, "vote_count": vote,
                               "mound_probability": float(prob),
                               "source_tile": tile,
                               "label": "mound"},
            })
    dest = OUT_BASE / cell / "primary" / "verified_detections.geojson"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:32635"}},
        "features": kept,
    }, indent=1))
    logger.info("%s: primary set n=%d at prob_t>=%.2f k>=%d -> %s",
                cell, len(kept), spec["prob_t"], spec["min_votes"],
                dest.relative_to(PROJECT_ROOT))
    return dest


def ensure_empty_yesterday() -> Path:
    """Header-only review CSV so only the canonical set feeds the phantoms.

    Mirrors `score_55maps_extended_gt_canonical.ensure_empty_yesterday`:
    the engine requires both review CSVs in legacy ring-gated mode, and the
    canonical review passes as today with an empty yesterday (yesterday=0,
    today=773 — the §4b configuration).
    """
    import csv
    OUT_BASE.mkdir(parents=True, exist_ok=True)
    path = OUT_BASE / "empty-yesterday-review.csv"
    with path.open("w", newline="") as fh:
        csv.writer(fh).writerow(
            ["candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"])
    return path


def score(cell: str, detections: Path) -> None:
    """Score one verified set on the canonical-GT Track-2 configuration."""
    out_dir = OUT_BASE / cell / "primary" / "eval"
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts/compute_corrected_f1_multi_buffer.py"),
        "--verified-detections", str(detections),
        "--student-gt", str(STUDENT_GT),
        "--bounds", str(BOUNDS),
        "--review-yesterday", str(ensure_empty_yesterday()),
        "--review-today", str(CANONICAL_REVIEW),
        "--output-dir", str(out_dir),
        "--buffers", "20", "30", "50",
        "--n-bootstrap", "10000",
        "--seed", "42",
        "--compute-mcc",
    ]
    logger.info("%s: scoring at B=10,000 (canonical GT, buffers 20/30/50)", cell)
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        logger.error("scoring failed for %s:\n%s", cell, res.stderr[-2500:])
        raise RuntimeError(f"scoring failed for {cell}")
    summary = json.loads((out_dir / "summary.json").read_text())
    for row in summary.get("buffers", summary.get("per_buffer", [])):
        logger.info("%s @%sm: %s", cell,
                    row.get("buffer_metres", row.get("buffer")), {
                        k: row.get(k) for k in
                        ("corrected_f1", "f1", "precision", "recall", "mcc")
                        if row.get(k) is not None})


def main() -> int:
    import csv as csvmod
    for required in (STUDENT_GT, BOUNDS, CANONICAL_REVIEW):
        if not required.exists():
            raise FileNotFoundError(required)
    for cell, spec in RUNS.items():
        det = materialise_primary(cell, spec)
        score(cell, det)
        # Attribution-invariance gate: map-constrained standard-tile
        # assignment must leave the per-map Hungarian F1 identical to the
        # origin-attribution run (2026-08-27 first pass). A mismatch means
        # attribution drifted — the 10.1 % border-flip artefact class.
        with (OUT_BASE / cell / "primary" / "eval" /
              "corrected-f1.csv").open() as fh:
            f1_50 = next(float(r["F1"]) for r in csvmod.DictReader(fh)
                         if int(r["R_m"]) == 50)
        if abs(f1_50 - spec["expect_f1_50"]) > 1e-6:
            raise RuntimeError(
                f"{cell}: attribution-invariance gate FAILED — F1@50 "
                f"{f1_50:.10f} vs expected {spec['expect_f1_50']:.10f}")
        logger.info("%s: attribution-invariance gate OK (%.6f)", cell, f1_50)
    logger.info("primary scoring complete -> %s", OUT_BASE.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
