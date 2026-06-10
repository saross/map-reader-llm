#!/usr/bin/env python3
# ============================================================================
# validate_first5_of10_derivation.py
# ----------------------------------------------------------------------------
# Session 111 ($0): validate the "verify once at n=10, derive n=5 post-hoc"
# shortcut approved for the Flash 3.5 tranche (Shawn, 2026-06-10).
#
# METHOD: the flash-high-text lineage has BOTH verified pools on disk from
# the same 30-pass study (first-N rule): the true 5-pass union
# (flash-high-text-1of5, 3,736 cands) and the 10-pass union
# (flash-high-text-1of10, 5,866 cands), each with carry-forward n=1
# verifier probabilities. So we can test the shortcut exactly:
#
#   A (derived): re-merge runs 1..10 with the CURRENT merge_passes (which
#      emits contributing_passes), gate its geometry against the committed
#      union, join the committed 10-pool verifier probs by coordinate,
#      restrict votes to runs 1..5, sweep k-of-5 x prob_t.
#   B (true):    the committed 5-pass pool + its own verifier probs,
#      same sweep (reproduces the cheap6 line: best 0.8641 at 4of5/pt0.15).
#
# PASS criterion: |best-F1(A) - best-F1(B)| <= 0.0075 per k (the verifier
# single-run SD is 0.0025-0.0072; the comparison folds in centroid-shift,
# cluster-topology, and verifier-draw differences).
#
# Also gates the V3 side: a fresh re-merge of text-n10 runs 1..10 must
# reproduce the committed text-1of10.geojson geometry (1,939 features), so
# V3 crops extracted from the regenerated (contributing_passes-bearing)
# union stay comparable with the committed min11 cell.
#
# COST: $0 (local merges + on-disk re-score). Run on zbook.
#
# Usage:
#   .venv/bin/python scripts/validate_first5_of10_derivation.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-10 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.analyse_verifier_robustness import (  # noqa: E402
    EVAL_CRS,
    GROUND_TRUTH,
    load_candidate_table,
)
from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.lib_advanced_metrics import score_detection_set  # noqa: E402

PVD = BASE_DIR / "outputs" / "h11" / "pv-diag-384"
BOUNDS = BASE_DIR / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUT_DIR = BASE_DIR / "results" / "verifier-robustness" / "first5of10-validation"
PROB_TS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
FIRST5 = {f"run_{i}" for i in range(1, 6)}
TOLERANCE = 0.0075  # per-k best-F1 agreement bound (see header)


def remerge(passes_dir: Path, passes: str, out: Path) -> None:
    """Re-merge the given passes at threshold 1 with the current tool."""
    subprocess.run([str(BASE_DIR / ".venv/bin/python"),
                    str(BASE_DIR / "scripts/merge_passes.py"),
                    "--input-dir", str(passes_dir), "--passes", passes,
                    "--threshold", "1", "--output", str(out)],
                   check=True, capture_output=True, text=True)


def to_32635(gj: Path) -> gpd.GeoDataFrame:
    """Read a geojson, magnitude-detect undeclared CRS, return EPSG:32635."""
    gdf = gpd.read_file(gj)
    crs = "EPSG:32635" if abs(gdf.geometry.x.iloc[0]) > 180 else "EPSG:4326"
    return gdf.set_crs(crs, allow_override=True).to_crs("EPSG:32635")


def coord_key(x: float, y: float) -> tuple[int, int]:
    """Coordinate identity key at 0.1 m resolution (EPSG:32635 metres)."""
    return (round(x * 10), round(y * 10))


def geometry_gate(fresh: gpd.GeoDataFrame, committed: gpd.GeoDataFrame,
                  label: str) -> bool:
    """Check the fresh re-merge reproduces the committed union geometry."""
    fk = {coord_key(g.x, g.y) for g in fresh.geometry}
    ck = {coord_key(g.x, g.y) for g in committed.geometry}
    ok = fk == ck
    print(f"  gate [{label}]: fresh {len(fresh)} vs committed {len(committed)} "
          f"features; coord sets {'IDENTICAL' if ok else 'DIFFER'}"
          + ("" if ok else f" (only-fresh {len(fk - ck)}, only-committed {len(ck - fk)})"),
          flush=True)
    return ok


def sweep(table: list[dict], max_k: int, gdf_ref, gdf_bounds,
          vote_field: str = "vote_count") -> dict[int, dict]:
    """Best F1@20m per proposer k over the prob_t sweep (n=1 'mean' rule)."""
    by_k = {}
    for k in range(1, max_k + 1):
        best = {"f1": -1.0}
        for pt in PROB_TS:
            sel = [r for r in table if r[vote_field] >= k and r["iter_probs"][0] >= pt]
            if not sel:
                continue
            gdf = gpd.GeoDataFrame(
                {"geometry": [Point(r["x"], r["y"]) for r in sel],
                 "source_tile": [r["source_tile"] for r in sel]}, crs=EVAL_CRS)
            f1 = score_detection_set(gdf, gdf_ref, gdf_bounds, buffer_metres=20,
                                     compute_mcc=False)["f1"]
            if f1 > best["f1"]:
                best = {"f1": f1, "pt": pt, "n": len(sel)}
        by_k[k] = best
    return by_k


def main() -> int:
    """Run gates A/B and the derived-vs-true sweep comparison."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf_ref = load_geojson(GROUND_TRUTH)
    gdf_bounds = load_geojson(BOUNDS)

    print("=== re-merging unions with the current merge_passes ===", flush=True)
    fresh_high10 = OUT_DIR / "flash-high-text-1of10-remerged.geojson"
    remerge(PVD / "flash-high-text-n5/text-t0.7", "1,2,3,4,5,6,7,8,9,10", fresh_high10)
    fresh_min10 = OUT_DIR / "text-n10-1of10-remerged.geojson"
    remerge(PVD / "text-n10/text-t0.7", "1,2,3,4,5,6,7,8,9,10", fresh_min10)

    print("=== geometry gates vs committed unions ===", flush=True)
    g_high = to_32635(fresh_high10)
    ok_a = geometry_gate(g_high, to_32635(PVD / "consensus/flash-high-text-1of10.geojson"),
                         "flash-high 1of10")
    ok_b = geometry_gate(to_32635(fresh_min10),
                         to_32635(PVD / "consensus/text-1of10.geojson"),
                         "text-n10 1of10 (V3 side)")

    # --- derived sweep A: committed 10-pool probs + first-5 vote restriction
    print("=== sweep A: first-5-of-10 derived (committed 10-pool probs) ===", flush=True)
    table10 = load_candidate_table(
        PVD / "verified/flash-high-text-1of10/candidate_manifest.json",
        PVD / "verified/flash-high-text-1of10/probabilities.json")
    passes_by_coord = {coord_key(g.x, g.y): p for g, p in zip(
        g_high.geometry, g_high["contributing_passes"])}
    n_unmatched = 0
    derived = []
    for r in table10:
        cp = passes_by_coord.get(coord_key(r["x"], r["y"]))
        if cp is None:
            n_unmatched += 1
            continue
        if isinstance(cp, str):  # geopandas may deliver list columns as strings
            cp = json.loads(cp.replace("'", '"'))
        first5 = sum(1 for p in cp if p in FIRST5)
        if first5 >= 1:
            derived.append({**r, "first5_votes": first5})
    print(f"  joined {len(table10) - n_unmatched}/{len(table10)} candidates "
          f"({n_unmatched} unmatched); first-5 union size {len(derived)}", flush=True)
    sweep_a = sweep(derived, 5, gdf_ref, gdf_bounds, vote_field="first5_votes")

    # --- true sweep B: the committed 5-pass pool + its own probs
    print("=== sweep B: true 5-pass pool (committed) ===", flush=True)
    table5 = load_candidate_table(
        PVD / "verified/flash-high-text-1of5/candidate_manifest.json",
        PVD / "verified/flash-high-text-1of5/probabilities.json")
    sweep_b = sweep(table5, 5, gdf_ref, gdf_bounds)

    print(f"\n{'k':<5}{'derived A':>12}{'true B':>12}{'delta':>9}  verdict", flush=True)
    worst = 0.0
    for k in range(1, 6):
        d = sweep_a[k]["f1"] - sweep_b[k]["f1"]
        worst = max(worst, abs(d))
        print(f"{k}of5 {sweep_a[k]['f1']:>11.4f} {sweep_b[k]['f1']:>11.4f} "
              f"{d:>+8.4f}  {'ok' if abs(d) <= TOLERANCE else 'EXCEEDS'}", flush=True)

    passed = ok_a and ok_b and worst <= TOLERANCE
    verdict = ("PASS — the n=10-first design is validated: derive n=5 post-hoc "
               "from contributing_passes" if passed else
               "FAIL — do NOT use the shortcut; investigate before launch")
    print(f"\nVERDICT: {verdict} (worst per-k delta {worst:.4f}, "
          f"tolerance {TOLERANCE})", flush=True)

    (OUT_DIR / "validation.json").write_text(json.dumps({
        "geometry_gate_flash_high_1of10": ok_a,
        "geometry_gate_text_n10_1of10": ok_b,
        "sweep_derived_first5_of10": sweep_a,
        "sweep_true_5pass": sweep_b,
        "worst_abs_delta": round(worst, 4),
        "tolerance": TOLERANCE, "passed": passed}, indent=2) + "\n")
    print(f"Wrote {OUT_DIR.relative_to(BASE_DIR)}/validation.json", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
