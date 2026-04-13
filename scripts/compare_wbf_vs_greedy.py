#!/usr/bin/env python3
# ============================================================================
# compare_wbf_vs_greedy.py
# ----------------------------------------------------------------------------
# Bootstrap CIs and paired permutation test comparing the WBF Variant C
# output against the greedy-ball baseline on the same H10 test tiles.
#
# Each method is loaded at its own optimal (vote_t, prob_t) operating point
# from the respective F1 sweep — we compare the two methods at the best
# threshold each can achieve, not at a fixed shared threshold.
#
# Outputs a JSON summary with:
#   - greedy baseline: F1, bootstrap CI
#   - WBF Variant C: F1, bootstrap CI
#   - paired permutation test: observed delta, p-value, wins/losses/ties
# ============================================================================

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import MultiPoint, Point

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_advanced_metrics import bootstrap_ci, calculate_f1_internal
from scripts.pairwise_permutation_test import run_permutation_test

TARGET_CRS = "EPSG:32635"
GT_PATH = BASE_DIR / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
BOUNDS_PATH = BASE_DIR / "inputs" / "calibration" / "h10-384" / "test_bounds.geojson"


def load_candidates_with_probs(
    manifest_path: Path,
    probs_path: Path,
) -> gpd.GeoDataFrame:
    """Load candidate manifest + verifier probabilities into a GeoDataFrame.

    Returns one row per candidate with columns:
        candidate_id, source_tile, vote_count, mound_probability, geometry
    """
    manifest = json.loads(manifest_path.read_text())
    probs = json.loads(probs_path.read_text())["results"]

    rows = []
    for c in manifest["candidates"]:
        cid = c["candidate_id"]
        key = f"candidate_{cid:05d}"
        prob_entry = probs.get(key)
        if prob_entry is None:
            continue
        props = c.get("properties", {})
        rows.append({
            "candidate_id": cid,
            "source_tile": c.get("source_tile") or props.get("source_tile") or "",
            "vote_count": int(props.get("vote_count", 0)),
            "mound_probability": float(prob_entry["mound_probability"]),
            "geometry": Point(float(c["centroid_x"]), float(c["centroid_y"])),
        })

    return gpd.GeoDataFrame(rows, crs=TARGET_CRS)


def filter_at_threshold(
    gdf: gpd.GeoDataFrame, vote_t: int, prob_t: float,
) -> gpd.GeoDataFrame:
    """Return the subset of candidates that survive a (vote_t, prob_t) filter."""
    mask = (gdf["vote_count"] >= vote_t) & (gdf["mound_probability"] >= prob_t)
    return gdf[mask].reset_index(drop=True)


def load_gt() -> gpd.GeoDataFrame:
    g = gpd.read_file(GT_PATH).to_crs(TARGET_CRS)
    def to_point(geom):
        if isinstance(geom, MultiPoint):
            return list(geom.geoms)[0]
        return geom
    g = g.copy()
    g["geometry"] = g.geometry.apply(to_point)
    return g


def load_bounds() -> gpd.GeoDataFrame:
    return gpd.read_file(BOUNDS_PATH).to_crs(TARGET_CRS)


def main() -> int:
    print("Loading GT and bounds...")
    gt = load_gt()
    bounds = load_bounds()
    print(f"  {len(gt)} GT mounds, {len(bounds)} test tiles")

    # Greedy baseline: optimum found previously at (vote=6, prob=0.15)
    print("\nLoading greedy baseline at optimum (vote=6, prob=0.15)...")
    greedy = load_candidates_with_probs(
        BASE_DIR / "outputs" / "h10" / "verifier-crops" / "pool_160_hp4hn4" / "candidate_manifest.json",
        BASE_DIR / "outputs" / "h10" / "verified" / "pool_160_hp4hn4" / "probabilities.json",
    )
    greedy_best = filter_at_threshold(greedy, vote_t=6, prob_t=0.15)
    print(f"  {len(greedy)} total candidates -> {len(greedy_best)} at optimum")

    # WBF Variant C: optimum found previously at (vote=7, prob=0.15)
    print("\nLoading WBF Variant C at optimum (vote=7, prob=0.15)...")
    wbf = load_candidates_with_probs(
        BASE_DIR / "outputs" / "h10" / "wbf" / "pool_160_hp4hn4_variant_c" / "crops" / "candidate_manifest.json",
        BASE_DIR / "outputs" / "h10" / "wbf" / "pool_160_hp4hn4_variant_c" / "verified" / "probabilities.json",
    )
    wbf_best = filter_at_threshold(wbf, vote_t=7, prob_t=0.15)
    print(f"  {len(wbf)} total candidates -> {len(wbf_best)} at optimum")

    # Observed F1 at each optimum
    print("\nComputing point F1 estimates...")
    p_g, r_g, f1_g = calculate_f1_internal(greedy_best, gt, bounds, buffer_metres=20)
    p_w, r_w, f1_w = calculate_f1_internal(wbf_best, gt, bounds, buffer_metres=20)
    print(f"  greedy:    P={p_g:.4f}  R={r_g:.4f}  F1={f1_g:.4f}")
    print(f"  wbf c:     P={p_w:.4f}  R={r_w:.4f}  F1={f1_w:.4f}")
    print(f"  Δ F1:      {f1_w - f1_g:+.4f}")

    def _ci_tuple(b: dict, metric: str) -> tuple[float, float]:
        return (b[metric]["ci_lower"], b[metric]["ci_upper"])

    # Bootstrap CI for each method
    print("\nBootstrap CI — greedy baseline (1000 iterations, seed 42)...")
    greedy_ci = bootstrap_ci(
        greedy_best, gt, bounds,
        n_iterations=1000, random_seed=42, buffer_metres=20,
    )
    f1_lo, f1_hi = _ci_tuple(greedy_ci, "f1")
    p_lo, p_hi = _ci_tuple(greedy_ci, "precision")
    r_lo, r_hi = _ci_tuple(greedy_ci, "recall")
    print(f"  F1 CI: [{f1_lo:.4f}, {f1_hi:.4f}]")
    print(f"  P CI:  [{p_lo:.4f}, {p_hi:.4f}]")
    print(f"  R CI:  [{r_lo:.4f}, {r_hi:.4f}]")

    print("\nBootstrap CI — WBF Variant C (1000 iterations, seed 42)...")
    wbf_ci = bootstrap_ci(
        wbf_best, gt, bounds,
        n_iterations=1000, random_seed=42, buffer_metres=20,
    )
    f1_lo_w, f1_hi_w = _ci_tuple(wbf_ci, "f1")
    p_lo_w, p_hi_w = _ci_tuple(wbf_ci, "precision")
    r_lo_w, r_hi_w = _ci_tuple(wbf_ci, "recall")
    print(f"  F1 CI: [{f1_lo_w:.4f}, {f1_hi_w:.4f}]")
    print(f"  P CI:  [{p_lo_w:.4f}, {p_hi_w:.4f}]")
    print(f"  R CI:  [{r_lo_w:.4f}, {r_hi_w:.4f}]")

    # Paired permutation test
    print("\nPaired permutation test (10,000 iterations, seed 42)...")
    perm = run_permutation_test(
        gdf_a=greedy_best,
        gdf_b=wbf_best,
        gdf_ref=gt,
        gdf_bounds=bounds,
        buffer_metres=20,
        n_permutations=10_000,
        seed=42,
    )
    pt = perm["permutation_test"]
    print(f"  observed Δ F1 (greedy − WBF): {pt['observed_f1_diff']:+.4f}")
    print(f"  p-value (two-sided):          {pt['p_value']:.4f}")
    print(f"  wins greedy:   {pt['wins_a']} tiles")
    print(f"  wins WBF:      {pt['losses_a']} tiles")
    print(f"  ties:          {pt['ties']} tiles")
    print(f"  n_tiles:       {pt['n_tiles']}")

    # Save summary
    summary = {
        "greedy_baseline": {
            "vote_t": 6, "prob_t": 0.15,
            "n_candidates": int(len(greedy_best)),
            "precision": float(p_g), "recall": float(r_g), "f1": float(f1_g),
            "f1_ci_95": [float(f1_lo), float(f1_hi)],
            "precision_ci_95": [float(p_lo), float(p_hi)],
            "recall_ci_95": [float(r_lo), float(r_hi)],
        },
        "wbf_variant_c": {
            "vote_t": 7, "prob_t": 0.15,
            "n_candidates": int(len(wbf_best)),
            "precision": float(p_w), "recall": float(r_w), "f1": float(f1_w),
            "f1_ci_95": [float(f1_lo_w), float(f1_hi_w)],
            "precision_ci_95": [float(p_lo_w), float(p_hi_w)],
            "recall_ci_95": [float(r_lo_w), float(r_hi_w)],
        },
        "paired_permutation_test": {
            "n_permutations": 10_000,
            "seed": 42,
            "observed_f1_diff_greedy_minus_wbf": float(pt["observed_f1_diff"]),
            "p_value_two_sided": float(pt["p_value"]),
            "wins_greedy": int(pt["wins_a"]),
            "wins_wbf": int(pt["losses_a"]),
            "ties": int(pt["ties"]),
            "n_tiles": int(pt["n_tiles"]),
        },
    }

    out_path = BASE_DIR / "results" / "h10" / "wbf" / "variant_c_vs_greedy_hp4hn4.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
