#!/usr/bin/env python3
"""
Materialise Session-78 Verifier-Calibration Matrix GeoJSONs
============================================================

For the 14 Session-78 verifier-calibration matrix cells ({adversarial,
adversarial-text, brief, brief-text, checklist, checklist-text, comparative}
× {image, text}), emit one post-verifier detection GeoJSON per cell at its
F1-optimal (vote_t, prob_t) operating point at the 20 m buffer.

Each GeoJSON contains the filtered set of consensus candidates that pass
both the vote-count threshold and the verifier probability threshold, so
the resulting files are directly comparable to the pre-existing
``results/leaderboard/era2/pv-materialised/`` artefacts and can be fed to
``build_tiered_leaderboard.py`` as ``pv`` architecture conditions.

Inputs (one per cell):
    Shared candidate manifest (same across all 7 variants per pool):
        outputs/h11/pv-diag-384/flash-high-<pool>-n5/<pool>-t0.7/
            session-78-matrix/shared-crops/candidate_manifest.json
    Verifier probabilities (one per variant):
        outputs/h11/pv-diag-384/flash-high-<pool>-n5/<pool>-t0.7/
            session-78-matrix/verified-<variant>/probabilities.json
        (except canonical adversarial-text, which reads from
         verified-v1-n5/probabilities.json — see Obs 275 note)
    Pre-computed 20m optima per cell:
        results/leaderboard/cells/session-78-<pool>-<variant>-487tile.json

Outputs:
    results/leaderboard/era2/pv-materialised/session-78-<pool>-<variant>.geojson
    results/leaderboard/era2/pv-materialised/session-78-matrix-registry.json

Usage:
    .venv/bin/python scripts/materialise_session78_geojsons.py

Run on sapphire because the shared-crops manifest + per-variant probability
files live there (outputs/ not synced to amd-tower).

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-25 (Session 79)
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

POOLS = ["image", "text"]
VARIANTS_NOVEL = [
    "adversarial",
    "brief",
    "brief-text",
    "checklist",
    "checklist-text",
    "comparative",
]
VARIANTS_CANONICAL = ["adversarial-text"]
ALL_VARIANTS = VARIANTS_NOVEL + VARIANTS_CANONICAL

POOL_BASE = {
    "image": REPO_ROOT / "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
    "text": REPO_ROOT / "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
}
POOL_K = {"image": 10, "text": 30}  # Underlying proposer K (paper-headline)
POOL_TRACK_K_USED_IN_S78 = 5  # S78 matrix uses consensus-n5 for both pools

BOUNDS_487 = REPO_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

OUTPUT_DIR = REPO_ROOT / "results/leaderboard/era2/pv-materialised"
CELLS_DIR = REPO_ROOT / "results/leaderboard/cells"


def load_manifest(pool: str) -> dict:
    """Load the shared-crops candidate manifest for a pool."""
    path = POOL_BASE[pool] / "session-78-matrix/shared-crops/candidate_manifest.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_probabilities(pool: str, variant: str) -> dict:
    """Load verifier probabilities for a (pool, variant) cell.

    After the 2026-04-25 re-run, all 7 variants (canonical + 6 alternatives)
    share the same shared-crops candidate pool under session-78-matrix/.
    Previously, canonical adversarial-text read from verified-v1-n5/ on a
    slightly different candidate pool (separate crops). The re-run aligned
    canonical and alternatives onto a single crop set for crop-parity.
    """
    path = POOL_BASE[pool] / f"session-78-matrix/verified-{variant}/probabilities.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("results", {})


def load_cell_optimum(pool: str, variant: str) -> tuple[int, float]:
    """Return the 20 m optimal (vote_t, prob_t) from the cached cell JSON."""
    path = CELLS_DIR / f"session-78-{pool}-{variant}-487tile.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    opt = data["optima_per_buffer"]["20"]
    return int(opt["vote_t"]), float(opt["prob_t"])


def load_bounds_allowlist() -> set:
    """Read the 487-tile Era 2 evaluation bounds and return tile_name set."""
    import geopandas as gpd

    gdf = gpd.read_file(BOUNDS_487)
    return set(gdf["tile_name"].tolist())


def materialise_cell(
    pool: str, variant: str, out_dir: Path, allowlist: set
) -> dict:
    """Filter the manifest by (vote_t, prob_t) and write a GeoJSON.

    Applies the 487-tile Era 2 bounds allowlist to match the pre-computed
    session-78 cell scope — candidates whose source_tile falls outside the
    allowlist are dropped before threshold filtering.

    Returns a registry row with the filter parameters + output path +
    detection count so the leaderboard builder can pick up the file.
    """
    manifest = load_manifest(pool)
    probs = load_probabilities(pool, variant)
    vote_t, prob_t = load_cell_optimum(pool, variant)

    # Filter: bounds-in-scope AND vote_count >= vote_t AND
    # mound_probability >= prob_t.
    features = []
    kept = 0
    missing_probs = 0
    out_of_scope = 0
    for cand in manifest["candidates"]:
        if cand["source_tile"] not in allowlist:
            out_of_scope += 1
            continue
        vote_count = cand["properties"].get("vote_count", 0)
        if vote_count < vote_t:
            continue
        cid = f"candidate_{cand['candidate_id']:05d}"
        if cid not in probs:
            missing_probs += 1
            continue
        prob = float(probs[cid].get("mound_probability", 0.0))
        if prob < prob_t:
            continue
        feat = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [cand["centroid_x"], cand["centroid_y"]],
            },
            "properties": {
                "candidate_id": cand["candidate_id"],
                "source_tile": cand["source_tile"],
                "source_tiles": cand["properties"].get(
                    "source_tiles", [cand["source_tile"]]
                ),
                "vote_count": vote_count,
                "mound_probability": prob,
                "subtype": cand["properties"].get("subtype", "burial_mound"),
                "confidence": cand["properties"].get("confidence"),
            },
        }
        features.append(feat)
        kept += 1

    # GeoJSON with EPSG:32635 CRS (matching the manifest's centroid coords)
    gj = {
        "type": "FeatureCollection",
        "name": f"session-78-{pool}-{variant}",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:EPSG::32635"},
        },
        "features": features,
    }

    out_path = out_dir / f"session-78-{pool}-{variant}.geojson"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(gj, f, indent=None)  # compact for size

    return {
        "pool": pool,
        "variant": variant,
        "vote_t": vote_t,
        "prob_t": prob_t,
        "candidates_input_total": manifest["total_detections"],
        "candidates_input_in_scope": manifest["total_detections"] - out_of_scope,
        "candidates_out_of_scope": out_of_scope,
        "candidates_kept": kept,
        "missing_probabilities": missing_probs,
        "output_geojson": str(out_path.relative_to(REPO_ROOT)),
        "source_cell": str(
            (CELLS_DIR / f"session-78-{pool}-{variant}-487tile.json").relative_to(
                REPO_ROOT
            )
        ),
    }


def main() -> int:
    """Materialise all 14 S78 matrix cells as GeoJSONs + write registry."""
    print(f"Loading 487-tile allowlist from {BOUNDS_487.name}...")
    allowlist = load_bounds_allowlist()
    print(f"  {len(allowlist)} tiles in scope")
    registry: list[dict] = []
    for pool in POOLS:
        for variant in ALL_VARIANTS:
            print(f"Materialising session-78-{pool}-{variant} ...", end=" ")
            row = materialise_cell(pool, variant, OUTPUT_DIR, allowlist)
            registry.append(row)
            print(
                f"vote_t={row['vote_t']} prob_t={row['prob_t']} "
                f"→ {row['candidates_kept']} features"
            )

    registry_path = OUTPUT_DIR / "session-78-matrix-registry.json"
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "script": "materialise_session78_geojsons.py",
                "description": (
                    "Session-78 verifier-calibration matrix: "
                    "7 variants × 2 pools materialised at per-cell 20m-optimal "
                    "(vote_t, prob_t). Source cells at "
                    "results/leaderboard/cells/session-78-<pool>-<variant>-487tile.json."
                ),
                "cells": registry,
            },
            f,
            indent=2,
        )
    print(f"\nRegistry: {registry_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
