#!/usr/bin/env python3
# ============================================================================
# materialise_flash35_best_ops.py
# ----------------------------------------------------------------------------
# Session 112 ($0): materialise the Flash 3.5 tranche's best-operating-point
# detection sets so they can receive standard 14-buffer evaluations and join
# the metric-led leaderboards (Shawn: "let's get Flash 3.5 into them").
#
# Sets (best ops re-derived deterministically from the same tables the
# 2x2x2 analysis used; gated against analysis-full.json):
#   f35prop-f3vf-n10    0.8480 (4of10 / pt0.15)
#   f35prop-f35vf-n10   0.8362 (4of10 / pt0.25)
#   f3prop-f35vf-n10    0.8689 (6of10 / pt0.25)
#   f35prop-bare-n10    0.6196 (10of10, no verifier)
# (n5-derived siblings excluded: method-matched analysis cells, not
#  leaderboard candidates; the F3xF3 cell is the already-registered min11.)
#
# Usage (zbook):  .venv/bin/python scripts/materialise_flash35_best_ops.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.analyse_verifier_robustness import (  # noqa: E402
    EVAL_CRS,
    load_candidate_table,
)

T2 = BASE_DIR / "outputs" / "flash35-pv-2x2"
OUT_DIR = BASE_DIR / "results" / "flash35-2x2" / "best-op-sets"
ANALYSIS = BASE_DIR / "results" / "flash35-2x2" / "analysis-full.json"

# (set name, probs path or None for bare, k, prob_t, analysis cell, branch)
SETS = [
    ("f35prop-f3vf-n10-4of10-pt0.15", T2 / "verified-f3vf/probabilities.json",
     4, 0.15, "f35prop-f3vf", "n10"),
    ("f35prop-f35vf-n10-4of10-pt0.25", T2 / "verified-f35vf/probabilities.json",
     4, 0.25, "f35prop-f35vf", "n10"),
    ("f3prop-f35vf-n10-6of10-pt0.25", T2 / "min-f3-verified-f35vf/probabilities.json",
     6, 0.25, "f3prop-f35vf", "n10"),
    ("f35prop-bare-n10-10of10", None, 10, None, "f35prop-bare", "n10"),
]
MANIFESTS = {
    "f35prop-f3vf": T2 / "crops/candidate_manifest.json",
    "f35prop-f35vf": T2 / "crops/candidate_manifest.json",
    "f3prop-f35vf": T2 / "min-f3-crops/candidate_manifest.json",
    "f35prop-bare": T2 / "crops/candidate_manifest.json",
}


def main() -> int:
    """Materialise each best-op set, gating n/F1 fields vs analysis-full.json."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    analysis = json.loads(ANALYSIS.read_text())["cells"]
    for name, probs, k, pt, cell, branch in SETS:
        manifest = MANIFESTS[cell]
        if probs is not None:
            table = load_candidate_table(manifest, probs)
            sel = [r for r in table if r["vote_count"] >= k and r["iter_probs"][0] >= pt]
        else:
            m = json.loads(manifest.read_text())["candidates"]
            sel = [{"x": float(c["centroid_x"]), "y": float(c["centroid_y"]),
                    "source_tile": c.get("source_tile", "")} for c in m
                   if int(c.get("properties", {}).get("vote_count", 0)) >= k]
        expect_n = analysis[cell][branch]["best"]["n"]
        if len(sel) != expect_n:
            sys.exit(f"GATE FAIL {name}: n={len(sel)} != analysis {expect_n}")
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
        out = OUT_DIR / f"{name}.geojson"
        gdf.to_crs("EPSG:4326").to_file(out, driver="GeoJSON")
        print(f"  {name}: n={len(sel)} (gate ok) -> {out.relative_to(BASE_DIR)}",
              flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
