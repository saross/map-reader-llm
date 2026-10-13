#!/usr/bin/env python3
"""
How many rows of W2.7's rung frames does carrying the contributing tiles re-attribute?

D62 (1) workstream ``origin-gap-h13-copies`` (2026-10-13), step 3. For every
§ 6 subset frame of the board families (``cluster_subset`` then ``inherit``),
every family's first-N rungs (N = 1 to all its passes, the last being the
full top rung), and UPL's verified union (which holds both halves' rows), this scores the
shared library's detection scope (``scope_detections_to_frame``) with and
without ``source_tiles`` and counts the rows whose attribution differs
(kept or not, and the sheet matched on). The first-N subsets and the top
rungs are exactly the board's own rungs (``stride55_ladder.cluster_first_n``
and ``gemini37_arm_ladder.cluster_first_n`` build them the same way; W2.7's
gates hold the counts equal), so a zero here also says that carrying the
tiles in the board's builder would re-attribute nothing on those rungs.

Clustering uses the gated fast restatement (``cluster_votes_fast_origins``),
after checking it against the committed function on two subsets.

Usage (from the W2.7 clone, ``REPO`` and ``W27_CACHE`` set)::

    python probe_w27_scope.py --out <json>

Author: Claude Code (Opus 5.5) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(os.environ["REPO"])
F2 = REPO / "reports/w27-replicate-floors-2026-10-06-scripts/floors-v2"
sys.path.insert(0, str(F2))
sys.path.insert(0, str(REPO / "reports/w27-replicate-floors-2026-10-06-scripts"))
import w27_55map_subset_replicates as w27  # noqa: E402  (inserts REPO, REPO/scripts)

import floors2_lib as L  # noqa: E402
from scripts.build_55map_leaderboard import BOUNDS  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes_with_origins  # noqa: E402
from scripts.lib_advanced_metrics import scope_detections_to_frame  # noqa: E402


def attribution(gdf, bounds) -> list:
    """Per row: the sheet the scorer matches it on, or None when it is not scored."""
    g = gdf.reset_index(drop=True)
    scope = scope_detections_to_frame(g, bounds)
    out = [None] * len(g)
    for pos, sheet in zip(scope.detections.index, scope.sheets):
        out[int(pos)] = str(sheet)
    return out


def compare(gdf, bounds) -> dict:
    """Rows whose attribution differs with and without ``source_tiles``."""
    a = attribution(gdf, bounds)
    b = attribution(gdf.drop(columns="source_tiles"), bounds)
    multi = sum(len({t.split("_x")[0] for t in o}) > 1 for o in gdf["source_tiles"])
    return {"n": len(gdf), "n_multi_sheet_origin": int(multi),
            "n_reattributed": int(sum(x != y for x, y in zip(a, b)))}


def main() -> int:
    """Probe every frame and write the counts."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    import geopandas as gpd

    fam = w27.build_families(gate_only=False)
    for f, s in (("A", (0, 1, 2)), ("ARM1", (1, 3))):
        sub = [fam[f]["passes"][i] for i in s]
        c0, v0, o0 = cluster_votes_with_origins(sub, 1)
        c1, v1, o1 = L.cluster_votes_fast_origins(sub, 1)
        assert np.array_equal(c0, c1) and np.array_equal(v0, v1) and o0 == o1, (f, s)
    w27.cluster_votes_origins = L.cluster_votes_fast_origins
    bounds = gpd.read_file(BOUNDS)
    bounds = (bounds.set_crs("EPSG:4326") if bounds.crs is None else bounds).to_crs("EPSG:32635")

    res: dict = {}
    seen_sets: dict = {}
    for f, spec in fam.items():
        frames = [s for subs in w27.subsets_for(spec["n"]).values() for s in subs]
        # Every first-N rung, N = 1 .. n (the board's ladders use first-N;
        # N = n is the full top rung), added once each.
        frames += [tuple(range(n)) for n in range(1, spec["n"] + 1)
                   if tuple(range(n)) not in frames]
        for s in frames:
            raw = w27.cluster_subset(spec["passes"], s, spec["index"])
            key = (id(spec["passes"]), s)
            if key not in seen_sets:
                seen_sets[key] = compare(raw, bounds)
            rec = {"raw": seen_sets[key],
                   "inherited": compare(w27.inherit(raw, spec["union"]), bounds)}
            res[f"{f}|{'-'.join(map(str, s))}"] = rec
            print(f, s, rec, flush=True)
    upl = w27.load_upl_frame()
    res["UPL|union"] = {"raw": compare(upl, bounds)}
    print("UPL", res["UPL|union"], flush=True)
    total = sum(r["raw"]["n_reattributed"] for r in res.values())
    total_inh = sum(r.get("inherited", {}).get("n_reattributed", 0) for r in res.values())
    res["_totals"] = {"frames": len(res), "raw_reattributed": total,
                      "inherited_reattributed": total_inh}
    args.out.write_text(json.dumps(res, indent=1, sort_keys=True))
    print("TOTAL reattributed raw", total, "inherited", total_inh, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
