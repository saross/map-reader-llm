#!/usr/bin/env python3
# ============================================================================
# compute_pool_recall_ceilings.py
# ----------------------------------------------------------------------------
# Session 111 ($0): recall ceilings of the GS 384 px proposer pools — the
# maximum recall any verifier could deliver from each union — plus the
# per-pass yield and union/per-pass ratio (a direct measure of inter-pass
# proposal diversity). Ground for the temperature-vs-thinking diversity
# question (Shawn, S111): which diversity source raises REACHABLE recall,
# and which only adds volume?
#
# CRS note: some consensus geojsons hold EPSG:32635 coordinates without a
# declared CRS (the known mislabelling trap, Obs 350) — detected here by
# coordinate magnitude (|x| > 180 -> projected).
#
# COST: $0 (on-disk re-score). Run on zbook per the project compute rule.
#
# Usage:
#   .venv/bin/python scripts/compute_pool_recall_ceilings.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-10 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.analyse_verifier_robustness import GROUND_TRUTH  # noqa: E402
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402
from scripts.lib_detection_paths import resolve_pool_passes  # noqa: E402

BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
C = BASE_DIR / "outputs/h11/pv-diag-384/consensus"
M = BASE_DIR / "outputs/h11/pv-diag-384"
OUT = BASE_DIR / "results/verifier-robustness/pool_recall_ceilings.json"

# (label, union geojson, proposer pool dir or None, achieved best PV F1@20m
#  for context — committed records, see min_thinking_pv.log / pro_pv.log /
#  pareto_leaderboard.json / opmax_vs_headline_permutation.json)
#
# The per-pass detection counts come from each pass file's ``.meta.json``
# sidecar. The pool is resolved through ``scripts/lib_detection_paths.py`` and
# the sidecars derived from the resolved pass files, rather than globbed with a
# literal batch-convention sidecar pattern: that literal matched only the
# batch-written naming convention, so a pool holding real-time passes would
# have contributed a per-pass mean over the wrong subset (defect D6). On the
# four convention-A pools below the two routes resolve the same 10/30/10/30
# sidecars.
POOLS = [
    ("pro-high-t07-5pass", C / "pro-high-text-1of5.geojson",
     M / "pro-high-text-n5/text-t0.7", 0.8506),
    ("flash-min-t07-5pass", C / "flash-minimal-text-t07-1of5.geojson",
     M / "flash-minimal-text-n30-t07/text-t0.7", 0.8708),
    ("flash-min-t07-10pass", C / "text-1of10.geojson",
     M / "text-n10/text-t0.7", 0.8835),
    ("flash-high-t07-5pass", C / "flash-high-text-1of5.geojson",
     M / "flash-high-text-n5/text-t0.7", 0.8641),
    ("flash-high-t07-30pass", C / "flash-high-text-1of30.geojson", None, None),
    ("flash-high-16of30-headline-pool", C / "flash-high-text-16of30.geojson",
     None, 0.8951),
]


def main() -> int:
    """Score each union's recall ceiling at 20 m and report diversity ratios."""
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)
    rows = []
    print(f"{'pool':<34} {'n':>6} {'/pass':>6} {'u/p':>5}  R-ceil@20m  F1max  bestPV")
    for label, gj, pool_dir, pv_f1 in POOLS:
        gdf = gpd.read_file(gj)
        # Magnitude-based CRS detection (declared CRS may be absent or wrong).
        crs = "EPSG:32635" if abs(gdf.geometry.x.iloc[0]) > 180 else "EPSG:4326"
        gdf = gdf.set_crs(crs, allow_override=True).to_crs("EPSG:32635")
        res = score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                                  compute_mcc=False)
        r = res["recall"]
        f1max = 2 * r / (1 + r)  # F1 at the ceiling recall with perfect precision
        per_pass = ratio = None
        if pool_dir:
            metas = [pass_file.with_suffix(".meta.json")
                     for pass_file in resolve_pool_passes(pool_dir, allow_multiple=True)]
            nds = [json.load(open(m)).get("results_summary", {}).get("total_detections")
                   for m in metas if m.exists()]
            nds = [n for n in nds if n]
            if nds:
                per_pass = sum(nds) / len(nds)
                ratio = len(gdf) / per_pass
        rows.append({"pool": label, "n_union": len(gdf),
                     "per_pass_mean": round(per_pass, 1) if per_pass else None,
                     "union_per_pass": round(ratio, 2) if ratio else None,
                     "recall_ceiling_20m": round(r, 4),
                     "f1_max_at_ceiling": round(f1max, 4),
                     "best_pv_f1_20m": pv_f1, "crs_detected": crs})
        pp = f"{per_pass:.0f}" if per_pass else "-"
        rt = f"{ratio:.2f}" if ratio else "-"
        pv = f"{pv_f1:.4f}" if pv_f1 else "-"
        print(f"{label:<34} {len(gdf):>6} {pp:>6} {rt:>5}  {r:>9.4f}  {f1max:.4f}  {pv}")
    OUT.write_text(json.dumps({
        "scope": "GS 384px / 487 tiles / curator GT / 20 m",
        "note": "recall ceiling = union GT coverage (max recall any verifier could "
                "deliver); f1_max = 2R/(1+R) (ceiling F1 at perfect precision); "
                "union_per_pass measures inter-pass proposal diversity",
        "pools": rows}, indent=2) + "\n")
    print(f"\nWrote {OUT.relative_to(BASE_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
