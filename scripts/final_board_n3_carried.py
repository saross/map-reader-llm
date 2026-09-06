#!/usr/bin/env python3
"""
Final 55-map board addendum: the emergent GS-carried N = 3 cells.

PI direction (2026-08-28): add "as run" N = 3 cells for Runs A and B —
the operating points the GS ladder HAD selected before launch
(`results/stride-2026-08-25/plateau_analyses.json` first_n_ladder:
both geometries at prob 0.15, k3-of-3) but which the card never
nominated as carried points. They are therefore EMERGENT post-hoc
nominations, not registered claims, and carry the basis label
"carried (post-hoc)" wherever they appear.

Derivation identical to the stage-1 rung families (first-3 passes,
c = 1 clustering, K = 10 verifier inheritance at 10 m), thresholded at
the GS-selected (0.15, k3).

GATE: each cell's count must equal the committed stage-1 sweep row
exactly (A-N3 (0.15, k3) -> 4,400; B-N3 -> 4,971), proving the same
derivation chain.

Appends the two cells to `cells_manifest.json` (idempotent — skips
labels already present).

Usage::

    python scripts/final_board_n3_carried.py

Zero API. Run on sapphire.

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.stride55_ladder import (  # noqa: E402
    INHERIT_TOL_M,
    cluster_first_n,
    load_deduped_passes,
)
from scripts.build_55map_leaderboard import board_home  # noqa: E402
from scripts.stride55_score import build_map_constrained_index  # noqa: E402
from scripts.stride55_sweep_oracle import (  # noqa: E402
    BOUNDS,
    RUNS as STRIDE_RUNS,
    load_candidates,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: The r1 board home. Retained as documentation of where this script's outputs
#: historically landed; the working directory is now resolved per run through
#: ``board_home(--reference)`` so an r2 addendum cannot write into the r1 tree
#: (MAJOR 6 of the r2-chain audit, Session 149).
OUT = PROJECT_ROOT / "results/55map-final-board-2026-08-27"
POINT = (0.15, 3)  # the GS-ladder selection for BOTH geometries at N = 3
EXPECTED = {"A-N3-carried": 4400, "B-N3-carried": 4971}
CELLS = {"g384_ov128_55map": "A-N3", "g384_ov192_55map": "B-N3"}


def main(reference: str = "standardised") -> int:
    """Append the two N=3 carried cells to a board's manifest.

    Args:
        reference: Board vintage to append to — ``standardised`` (r1,
            default) or ``r2``. Selects the home; the cells themselves are
            derived identically either way.

    Returns:
        Process exit code.
    """
    out = board_home(reference)
    bounds = gpd.read_file(BOUNDS).to_crs("EPSG:32635")
    index = build_map_constrained_index()
    manifest_path = out / "cells_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    have = {c["label"] for c in manifest["cells"]}

    for cell, key in CELLS.items():
        label = f"{key}-carried"
        spec = STRIDE_RUNS[cell]
        k10 = load_candidates(cell, spec, bounds)
        tree = cKDTree(np.c_[k10.geometry.x, k10.geometry.y])
        probs10 = k10["mound_probability"].to_numpy()
        passes = load_deduped_passes(cell)
        gdf = cluster_first_n(passes, 3, index)
        d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
        gdf["mound_probability"] = probs10[idx]
        gdf = gdf[d <= INHERIT_TOL_M].copy()
        pt, pk = POINT
        sub = gdf[(gdf["mound_probability"] >= pt)
                  & (gdf["vote_count"] >= pk)]
        if len(sub) != EXPECTED[label]:
            raise RuntimeError(
                f"{label}: gate FAILED — {len(sub)} at ({pt}, k{pk}) vs "
                f"committed sweep {EXPECTED[label]}")
        logger.info("%s: gate OK (%d at (%.2f, k%d))", label, len(sub),
                    pt, pk)
        dest = out / "cells" / label / "detections.geojson"
        dest.parent.mkdir(parents=True, exist_ok=True)
        sub.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
        if label not in have:
            manifest["cells"].append({
                "label": label,
                "det": str(dest.relative_to(PROJECT_ROOT)),
                "basis": "carried (post-hoc)",
                "point": f"({pt:.2f}, k{pk})",
                "committed_eval": False})
            logger.info("%s: appended to cells_manifest", label)

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    logger.info("N3-CARRIED ADDENDUM COMPLETE (%d cells in manifest)",
                len(manifest["cells"]))
    return 0


if __name__ == "__main__":
    _ap = argparse.ArgumentParser(description=__doc__)
    _ap.add_argument(
        "--reference", choices=["standardised", "r2"], default="standardised",
        help="Board vintage to append the carried cells to (default: the r1 "
             "board, unchanged behaviour).",
    )
    sys.exit(main(_ap.parse_args().reference))
