#!/usr/bin/env python3
"""
The rows of W2.7's rung frames that carrying the contributing tiles re-attributes.

D62 (1) workstream ``origin-gap-h13-copies`` (2026-10-13), step 3. For every
inherited frame ``probe_w27_scope.py`` found with a re-attributed row, this
rebuilds the frame and lists each such row: its vote count, its inherited
verifier probability, the sheet it is matched on without and with
``source_tiles``, its contributing tiles, and the distance to the nearest r2
reference on each of those sheets. A row can change a cell only at an
operating point (prob_t, k) it passes, and only if the nearest reference on
one sheet is within the 50 m buffer.

Usage (from the W2.7 clone, ``REPO`` and ``W27_CACHE`` set)::

    python rows_w27_reattributed.py --probe <probe json> --out <json>

Author: Claude Code (Opus 5.5) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(os.environ["REPO"])
F2 = REPO / "reports/w27-replicate-floors-2026-10-06-scripts/floors-v2"
sys.path.insert(0, str(F2))
sys.path.insert(0, str(REPO / "reports/w27-replicate-floors-2026-10-06-scripts"))
import w27_55map_subset_replicates as w27  # noqa: E402  (inserts REPO, REPO/scripts)

import floors2_lib as L  # noqa: E402
from scripts.build_55map_leaderboard import BOUNDS, reference_gt  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    reference_map_column,
    scope_detections_to_frame,
)


def sheets_of(gdf, bounds) -> list:
    """Per row, the sheet the scorer matches it on (None if not scored)."""
    scope = scope_detections_to_frame(gdf, bounds)
    out = [None] * len(gdf)
    for pos, sheet in zip(scope.detections.index, scope.sheets):
        out[int(pos)] = str(sheet)
    return out


def main() -> int:
    """List the re-attributed rows of every flagged inherited frame."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--probe", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    import geopandas as gpd

    probe = json.loads(args.probe.read_text())
    flagged = sorted(k for k, v in probe.items()
                     if k != "_totals" and v.get("inherited", {}).get("n_reattributed"))
    fam = w27.build_families(gate_only=False)
    w27.cluster_votes_origins = L.cluster_votes_fast_origins
    bounds = gpd.read_file(BOUNDS)
    bounds = (bounds.set_crs("EPSG:4326") if bounds.crs is None else bounds).to_crs("EPSG:32635")
    ref = reference_gt("r2")
    col = reference_map_column(ref)
    out: dict = {}
    for key in flagged:
        f, s = key.split("|")
        subset = tuple(int(x) for x in s.split("-"))
        spec = fam[f]
        g = w27.inherit(w27.cluster_subset(spec["passes"], subset, spec["index"]),
                        spec["union"]).reset_index(drop=True)
        with_list = sheets_of(g, bounds)
        without = sheets_of(g.drop(columns="source_tiles"), bounds)
        rows = []
        for i, (a, b) in enumerate(zip(without, with_list)):
            if a == b:
                continue
            pt = g.geometry.iloc[i]
            dist = {}
            for sh in (a, b):
                if sh is None:
                    continue
                r = ref[ref[col] == sh]
                dist[sh] = round(float(r.geometry.distance(pt).min()), 2) if len(r) else None
            rows.append({
                "row": i, "vote_count": int(g["vote_count"].iloc[i]),
                "mound_probability": float(g["mound_probability"].iloc[i]),
                "sheet_without": a, "sheet_with": b,
                "source_tile": g["source_tile"].iloc[i],
                "source_tiles": list(g["source_tiles"].iloc[i]),
                "nearest_reference_m": dist,
            })
        out[key] = rows
        print(key, rows, flush=True)
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
