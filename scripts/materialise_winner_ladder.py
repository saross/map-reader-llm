#!/usr/bin/env python3
"""
Materialise the winner's first-N unions for exact re-verification.

The free N-ladder (`scripts/stride_plateau_analyses.py`) estimated the
384 px / 33.3 % cell's N ∈ {1, 3, 5} boards by inheriting K = 10 verifier
probabilities. The PI approved exact re-verification (2026-08-25, ~$3.4
flex): this script writes those three unions as verifier inputs, derived
EXACTLY as the ladder derived them (first-N passes, `cluster_votes` at
c = 1, carrier filter with per-cluster votes; since PI ruling D62 (1),
2026-10-13, each cluster also records its members' tiles as
``origin_tiles`` and is booked to a carrier tile on its own sheet, via
``materialise_grid_unions.union_with_votes``), under a count gate against
the ladder's published union sizes (1,290 / 1,700 / 1,968 — the
`union_n` fields in `plateau_analyses.json`, which include the
inheritance-unmatched clusters; exact verification covers those too,
which is the point).

Usage::

    python scripts/materialise_winner_ladder.py          # gates, dry run
    python scripts/materialise_winner_ladder.py --write

Zero API. Run on sapphire.

Created: 2026-08-25 (Session 142)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.grid_analysis import load_cell_passes  # noqa: E402
from scripts.materialise_grid_unions import union_with_votes  # noqa: E402

CELL = "g384_ov128"
ROOT = PROJECT_ROOT / "outputs/stride-phaseb-2026-08-25"
COMMON_BOUNDS = (
    PROJECT_ROOT / "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson")
LADDER = PROJECT_ROOT / "results/stride-2026-08-25/plateau_analyses.json"
NS = (1, 3, 5)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    bounds = gpd.read_file(COMMON_BOUNDS)
    expected = {int(n): v["union_n"] for n, v in
                json.loads(LADDER.read_text())
                ["first_n_ladder"][CELL]["N"].items()}
    passes = load_cell_passes(ROOT / "scoring", CELL)

    failures = 0
    for n in NS:
        gdf = union_with_votes(passes[:n], bounds)
        ok = len(gdf) == expected[n]
        print(f"N={n}: union {len(gdf)} (ladder recorded {expected[n]}) "
              f"{'OK' if ok else 'MISMATCH'}")
        failures += 0 if ok else 1
        if args.write and ok:
            dest = ROOT / "verifier" / CELL / f"union_k{n}.geojson"
            gdf.to_crs("EPSG:4326").to_file(dest, driver="GeoJSON")
            print(f"  wrote {dest.relative_to(PROJECT_ROOT)}")
    if failures:
        print("GATE FAIL — nothing further may run.")
        return 1
    if not args.write:
        print("dry run — pass --write to materialise")
    return 0


if __name__ == "__main__":
    sys.exit(main())
