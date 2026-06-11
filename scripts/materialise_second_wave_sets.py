#!/usr/bin/env python3
# ============================================================================
# materialise_second_wave_sets.py
# ----------------------------------------------------------------------------
# Session 113 ($0): materialise the three second-wave registration cells that
# have committed sweep records but no best-operating-point detection set on
# disk (the S111 author/gate pattern requires a geojson + a standard
# evaluation per condition):
#
#   t03-4of5-n1-pt0.2      GS text HIGH T0.3 5-pass + carry-forward n=1 vf
#                          (Run A; results/working-precision/gs-t03-pv-cell.json)
#   image-3of5-n1-pt0.15   GS image HIGH T0.7 5-pass + carry-forward n=1 vf
#                          (results/working-precision/gs-image-pv-cell.json)
#   min11-uplift-5of10-pt0.15  55-map Run B uplift, 10 minimal passes +
#                          carry-forward n=1 vf, >=3of10 band
#                          (results/55map-leaderboard/min11_uplift_cell.json)
#
# The operating point (k, prob_t) and the expected feature count are PARSED
# FROM the committed cell record — the script refuses to write a set whose
# selection does not reproduce the recorded n exactly (the Session-77
# feature-count cross-check, applied at materialisation time). Selection rule
# is accepted_cids(table, k, "mean", prob_t), the same rule the sweeps used
# (n=1 verifier: mean == that iteration's probability).
#
# Usage:  .venv/bin/python scripts/materialise_second_wave_sets.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.analyse_verifier_robustness import (  # noqa: E402
    EVAL_CRS,
    accepted_cids,
    load_candidate_table,
)

PVD = BASE_DIR / "outputs" / "h11" / "pv-diag-384"
UPLIFT = BASE_DIR / "outputs" / "55maps-text-min-n10-uplift"

# (cell record json, expected-n key, crops manifest, probabilities, output)
SETS = [
    (BASE_DIR / "results/working-precision/gs-t03-pv-cell.json",
     PVD / "crops/flash-high-text-t03-1of5/candidate_manifest.json",
     PVD / "verified/flash-high-text-t03-1of5/probabilities.json",
     BASE_DIR / "results/verifier-robustness/condition-sets/t03-4of5-n1-pt0.2.geojson"),
    (BASE_DIR / "results/working-precision/gs-image-pv-cell.json",
     PVD / "crops/flash-high-image-1of5/candidate_manifest.json",
     PVD / "verified/flash-high-image-1of5/probabilities.json",
     BASE_DIR / "results/verifier-robustness/condition-sets/image-3of5-n1-pt0.15.geojson"),
    (BASE_DIR / "results/55map-leaderboard/min11_uplift_cell.json",
     UPLIFT / "crops-3of10/candidate_manifest.json",
     UPLIFT / "verified-3of10/probabilities.json",
     BASE_DIR / "results/55map-leaderboard/min11-uplift-5of10-pt0.15.geojson"),
]


def main() -> int:
    """Materialise each cell's best-op set, gating n against the record."""
    for record_path, manifest, probs, out in SETS:
        record = json.loads(record_path.read_text())
        m = re.fullmatch(r"(\d+)of\d+/pt([0-9.]+)", record["best_op"])
        if not m:
            sys.exit(f"cannot parse best_op {record['best_op']!r} in {record_path.name}")
        k, prob_t = int(m.group(1)), float(m.group(2))
        expect_n = int(record["n"])

        table = load_candidate_table(manifest, probs)
        by_cid = {r["cid"]: r for r in table}
        sel = [by_cid[c] for c in sorted(accepted_cids(table, k, "mean", prob_t))]
        if len(sel) != expect_n:
            sys.exit(f"GATE FAIL {out.name}: n={len(sel)} != recorded {expect_n} "
                     f"({record_path.name}, {record['best_op']})")

        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(r["x"], r["y"]) for r in sel],
             "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
        out.parent.mkdir(parents=True, exist_ok=True)
        gdf.to_crs("EPSG:4326").to_file(out, driver="GeoJSON")
        print(f"  {out.name}: n={len(sel)} ({k}of?/pt{prob_t}, gate ok) -> "
              f"{out.relative_to(BASE_DIR)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
