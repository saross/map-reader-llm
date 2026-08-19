#!/usr/bin/env python3
"""
Materialise the four grid cells as registrable conditions (defect D16).

`results/grid-2026-08-18/` computes its metrics inside `grid_analysis.py` and
never writes a per-cell `evaluation.json`. The run register cannot record the
grid's analysis row without one: the analyses schema requires a non-empty
`conditions_compared`, and a condition needs an evaluation to carry its metrics.
D16 recorded this, and was blocked a second time by D15 (the BCa axis defect),
because `evaluate_detections.py` always computes bootstrap intervals and there
was no way to ask it not to write ones known to be wrong.

Both blocks are now clear. D15's fix landed in `122104b8a`, and the 2026-08-19
Principal-Investigator ruling standardises the study on 10 000 bootstrap
iterations (erratum E82), which is what this script passes.

What it does, per cell:

1. Rebuilds the cell's best-F1@20 m operating point at K = 10 from the prepared
   deduplicated passes, using `grid_analysis`'s own clustering so the
   materialised set is the same set the published sweep scored.
2. Writes it as a scorable GeoJSON with `source_tile` assigned against the
   common carrier grid (the E79 nearest-centroid rule).
3. Runs `evaluate_detections.py` against the common bounds at B = 10 000.
4. Verifies the resulting F1@20 m reproduces the published sweep value, and
   fails loudly if it does not.

Usage::

    python scripts/grid_materialise_conditions.py \\
        --output-dir results/grid-2026-08-18/conditions

Notes:
    - Zero API spend; reads committed artefacts only.
    - Run on sapphire: four 10 000-iteration bootstraps over 487 tiles.

Created: 2026-08-19 (Session 137)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import mapping

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_analysis import (  # noqa: E402
    CELL_LABEL,
    CELL_ORDER,
    as_gdf,
    cluster_votes,
    load_cell_passes,
)
from scripts.grid_prepare_scoring import CELLS  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCORING_DIR = PROJECT_ROOT / "outputs/grid-2026-08-18/scoring"
GRID_ANALYSIS = PROJECT_ROOT / "results/grid-2026-08-18/grid_analysis.json"
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
COMMON_BOUNDS = SCORING_DIR / "bounds" / "grid_common_bounds.geojson"

#: Bootstrap iterations. The 2026-08-19 PI ruling (erratum E82) standardises the
#: study on 10 000 rather than the 1 000 Decision 10 pre-specified. At 487
#: carrier tiles this is the B > n regime, so these intervals are WIDER than the
#: study's committed B = 1 000 ones, not narrower.
BOOTSTRAP = 10_000
SEED = 42
K_TOTAL = 10
BUFFER_M = 20
CRS_URN = "urn:ogc:def:crs:EPSG::32635"


def best_operating_point(sweep_rows: list[dict], cell: str) -> dict[str, Any]:
    """Return the published best-F1@20 m row for one cell at K = 10.

    Reading the operating point from the published sweep rather than recomputing
    a maximum keeps this script's choice identical to the one the findings
    document reports.
    """
    sel = [r for r in sweep_rows if r["cell"] == cell and r["K"] == K_TOTAL]
    if not sel:
        raise ValueError(f"no K={K_TOTAL} sweep rows for cell {cell}")
    return max(sel, key=lambda x: x["f1"])


def materialise(cell: str, point: dict, bounds: gpd.GeoDataFrame, target: Path) -> int:
    """Rebuild and write one cell's operating point as a scorable GeoJSON.

    Args:
        cell: Cell label.
        point: The sweep row naming `min_corroboration` and `min_votes`.
        bounds: Common carrier bounds.
        target: Output GeoJSON path.

    Returns:
        Number of features written.
    """
    passes = load_cell_passes(SCORING_DIR, cell)[:K_TOTAL]
    centroids, votes = cluster_votes(passes, point["min_corroboration"])
    gdf = as_gdf(centroids[votes >= point["min_votes"]], bounds)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": CRS_URN}},
        "processed_tiles": sorted(bounds["tile_name"].tolist()),
        "features": [
            {
                "type": "Feature",
                "geometry": mapping(geom),
                "properties": {
                    "source_tile": tile,
                    "label": "mound",
                    "subtype": "mound",
                },
            }
            for geom, tile in zip(gdf.geometry, gdf["source_tile"], strict=True)
        ],
    }, indent=2))
    return len(gdf)


def evaluate(detections: Path, out_dir: Path) -> Path:
    """Run `evaluate_detections.py` on one materialised cell at B = 10 000."""
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
    """Materialise, score, and verify all four cells.

    Returns:
        Process exit status; non-zero if any cell fails its reproduction gate.
    """
    parser = argparse.ArgumentParser(
        description="Materialise the grid's four cells as registrable conditions.")
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results/grid-2026-08-18/conditions")
    args = parser.parse_args()

    sweep_rows = json.loads(GRID_ANALYSIS.read_text())["sweep"]
    bounds = gpd.read_file(COMMON_BOUNDS)
    logger.info("common carrier: %d tiles", len(bounds))

    summary: list[dict[str, Any]] = []
    failures = 0
    for cell in CELL_ORDER:
        point = best_operating_point(sweep_rows, cell)
        cell_dir = args.output_dir / cell
        det = cell_dir / "detections.geojson"
        n = materialise(cell, point, bounds, det)

        if n != point["n_detections"]:
            logger.error("%s: materialised %d features, sweep recorded %d",
                         cell, n, point["n_detections"])
            failures += 1

        eval_path = evaluate(det, cell_dir / "eval")
        doc = json.loads(eval_path.read_text())
        buf = next(b for b in doc["summary"]["buffers"]
                   if b["buffer_metres"] == BUFFER_M)

        delta = abs(buf["f1"] - point["f1"])
        ok = delta < 5e-4
        failures += 0 if ok else 1
        logger.info(
            "%-16s c>=%d k>=%d | n=%d | published F1 %.4f, re-scored %.4f "
            "(delta %.5f) %s",
            CELL_LABEL[cell], point["min_corroboration"], point["min_votes"],
            n, point["f1"], buf["f1"], delta, "OK" if ok else "MISMATCH",
        )

        tc = doc["summary"].get("tile_classification", {})
        mcc = tc.get("mcc") if not isinstance(tc.get("mcc"), dict) else tc["mcc"].get("point")
        summary.append({
            "cell": cell,
            "label": CELL_LABEL[cell],
            "tile_px": CELLS[cell]["tile_px"],
            "overlap_frac": CELLS[cell]["overlap_frac"],
            "K": K_TOTAL,
            "min_corroboration": point["min_corroboration"],
            "min_votes": point["min_votes"],
            "n_detections": n,
            "published_f1_at_20m": point["f1"],
            "rescored_f1_at_20m": buf["f1"],
            "f1_ci_lower": buf["f1_ci_lower"],
            "f1_ci_upper": buf["f1_ci_upper"],
            "f1_ci_method": buf["f1_ci_method"],
            "precision": buf["precision"],
            "recall": buf["recall"],
            "tile_mcc": mcc,
            "bootstrap_iterations": BOOTSTRAP,
            "detections": str(det.relative_to(PROJECT_ROOT)),
            "evaluation": str(eval_path.relative_to(PROJECT_ROOT)),
            "reproduces_published": ok,
        })

    payload = {
        "classification": "POST-HOC (E41-class); registrable conditions for the "
                          "tile-size x overlap grid. Proposer stage only, "
                          "consensus-only aggregation, NO verifier.",
        "scope": {
            "carrier": "era-2-487 grid clipped to the four-way tile-union intersection",
            "carrier_tiles": len(bounds),
            "buffer_metres": BUFFER_M,
        },
        "bootstrap": {
            "n_iterations": BOOTSTRAP,
            "seed": SEED,
            "note": "10 000 per the 2026-08-19 PI ruling (erratum E82), not the "
                    "1 000 Decision 10 pre-specified. B > n at 487 tiles, so "
                    "these intervals are wider than the study's committed ones.",
        },
        "cells": summary,
    }
    out = args.output_dir / "grid_conditions.json"
    out.write_text(json.dumps(payload, indent=2))
    logger.info("wrote %s", out)

    if failures:
        logger.error("%d cell(s) failed the reproduction gate", failures)
        return 1
    logger.info("all four cells reproduce their published F1 to < 5e-4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
