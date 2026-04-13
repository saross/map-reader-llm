#!/usr/bin/env python3
# ============================================================================
# compare_wbf_vs_greedy_production.py
# ----------------------------------------------------------------------------
# Full (vote_t × prob_t × buffer_m) sweep + bootstrap CIs + paired permutation
# tests comparing the WBF Variant C output against the greedy-ball baseline on
# the H11 production run (e47-propose-brief, 4 gold-standard maps, 5 proposer
# passes of propose_brief-text with HIGH thinking / T=0.7).
#
# Runs the comparison separately for the v1 and v2 verifier configurations.
#
# Output: results/h11/wbf/production_vs_greedy_summary.json
#
# Usage:
#     python scripts/compare_wbf_vs_greedy_production.py
# ============================================================================

from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import MultiPoint, Point, shape

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_advanced_metrics import bootstrap_ci, calculate_f1_internal
from scripts.pairwise_permutation_test import run_permutation_test

TARGET_CRS = "EPSG:32635"
GT_PATH = BASE_DIR / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
PRODUCTION_BOUNDS = BASE_DIR / "inputs" / "vectors" / "bounds" / "384" / "full_evaluation_bounds.geojson"

#: Full sweep grid — matches the original production run sweeps
VOTE_THRESHOLDS = [1, 2, 3, 4, 5]
PROB_THRESHOLDS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60]
BUFFER_METRES_LIST = [20, 25, 30, 40, 50]

# Greedy baseline paths (4-maps production) — existing stored outputs
GREEDY_MANIFEST = (
    BASE_DIR / "outputs" / "h11" / "e47-propose-brief" / "verified"
    / "flash-high-text-1of5" / "candidate_manifest.json"
)
GREEDY_PROBS_V1 = (
    BASE_DIR / "outputs" / "h11" / "e47-propose-brief" / "verified"
    / "flash-high-text-1of5" / "probabilities.json"
)
GREEDY_PROBS_V2 = (
    BASE_DIR / "outputs" / "h11" / "e47-propose-brief" / "verified-v2"
    / "flash-high-text-1of5" / "probabilities.json"
)

# WBF paths (new outputs from this session)
WBF_MANIFEST = BASE_DIR / "outputs" / "h11" / "wbf" / "e47-propose-brief-n5" / "crops" / "candidate_manifest.json"
WBF_PROBS_V1 = BASE_DIR / "outputs" / "h11" / "wbf" / "e47-propose-brief-n5" / "verified-v1" / "probabilities.json"
WBF_PROBS_V2 = BASE_DIR / "outputs" / "h11" / "wbf" / "e47-propose-brief-n5" / "verified-v2" / "probabilities.json"


def load_candidates_with_probs(
    manifest_path: Path, probs_path: Path,
) -> gpd.GeoDataFrame:
    """Load a candidate manifest + verifier probabilities into a GeoDataFrame.

    Returns one row per candidate (with verifier probability) containing:
        candidate_id, source_tile, vote_count, mound_probability, geometry

    Handles both the legacy field name ``proposer_votes`` (used in the
    production run manifest) and the newer ``vote_count`` field (H10/H12).
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
        # Legacy: proposer_votes; current: vote_count
        vc = props.get("vote_count")
        if vc is None:
            vc = props.get("proposer_votes", 0)
        rows.append({
            "candidate_id": cid,
            "source_tile": c.get("source_tile") or props.get("source_tile") or "",
            "vote_count": int(vc),
            "mound_probability": float(prob_entry["mound_probability"]),
            "geometry": Point(float(c["centroid_x"]), float(c["centroid_y"])),
        })

    return gpd.GeoDataFrame(rows, crs=TARGET_CRS)


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
    """Load evaluation tile bounds for the 4-map production run."""
    return gpd.read_file(PRODUCTION_BOUNDS).to_crs(TARGET_CRS)


def filter_at_threshold(
    gdf: gpd.GeoDataFrame, vote_t: int, prob_t: float,
) -> gpd.GeoDataFrame:
    return gdf[
        (gdf["vote_count"] >= vote_t)
        & (gdf["mound_probability"] >= prob_t)
    ].reset_index(drop=True)


def run_full_sweep(
    cands: gpd.GeoDataFrame,
    gt: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
    label: str,
) -> list[dict]:
    """Run the (vote_t × prob_t × buffer_m) sweep and return all rows."""
    rows: list[dict] = []
    for vt, pt, bm in product(VOTE_THRESHOLDS, PROB_THRESHOLDS, BUFFER_METRES_LIST):
        sub = filter_at_threshold(cands, vt, pt)
        n = len(sub)
        if n == 0:
            rows.append({
                "label": label, "vote_t": vt, "prob_t": pt, "buffer_m": bm,
                "n": 0, "p": 0.0, "r": 0.0, "f1": 0.0,
            })
            continue
        p, r, f1 = calculate_f1_internal(sub, gt, bounds, buffer_metres=bm)
        rows.append({
            "label": label, "vote_t": vt, "prob_t": pt, "buffer_m": bm,
            "n": int(n),
            "p": round(p, 4), "r": round(r, 4), "f1": round(f1, 4),
        })
    return rows


def find_optima_per_buffer(rows: list[dict]) -> dict[int, dict]:
    """Return the best (vote_t, prob_t) row per buffer_m value."""
    by_buffer: dict[int, dict] = {}
    for bm in BUFFER_METRES_LIST:
        sub = [r for r in rows if r["buffer_m"] == bm]
        if not sub:
            continue
        best = max(sub, key=lambda r: r["f1"])
        by_buffer[bm] = best
    return by_buffer


def main() -> int:
    print("Loading GT and bounds...")
    gt = load_gt()
    bounds = load_bounds()
    print(f"  {len(gt)} GT mounds, {len(bounds)} tile bounds")

    print("\nLoading greedy baseline + v1 verifier probs...")
    greedy_v1 = load_candidates_with_probs(GREEDY_MANIFEST, GREEDY_PROBS_V1)
    print(f"  {len(greedy_v1)} greedy candidates with v1 probs")

    print("\nLoading greedy baseline + v2 verifier probs...")
    greedy_v2 = load_candidates_with_probs(GREEDY_MANIFEST, GREEDY_PROBS_V2)
    print(f"  {len(greedy_v2)} greedy candidates with v2 probs")

    print("\nLoading WBF output + v1 verifier probs...")
    wbf_v1 = load_candidates_with_probs(WBF_MANIFEST, WBF_PROBS_V1)
    print(f"  {len(wbf_v1)} WBF candidates with v1 probs")

    print("\nLoading WBF output + v2 verifier probs...")
    wbf_v2 = load_candidates_with_probs(WBF_MANIFEST, WBF_PROBS_V2)
    print(f"  {len(wbf_v2)} WBF candidates with v2 probs")

    # Full sweep per (method, verifier)
    print("\nRunning full sweeps...")
    sweep_greedy_v1 = run_full_sweep(greedy_v1, gt, bounds, "greedy-v1")
    sweep_greedy_v2 = run_full_sweep(greedy_v2, gt, bounds, "greedy-v2")
    sweep_wbf_v1 = run_full_sweep(wbf_v1, gt, bounds, "wbf-v1")
    sweep_wbf_v2 = run_full_sweep(wbf_v2, gt, bounds, "wbf-v2")
    print(f"  {len(sweep_greedy_v1)} rows per method × verifier")

    # Per-buffer optima
    opt_greedy_v1 = find_optima_per_buffer(sweep_greedy_v1)
    opt_greedy_v2 = find_optima_per_buffer(sweep_greedy_v2)
    opt_wbf_v1 = find_optima_per_buffer(sweep_wbf_v1)
    opt_wbf_v2 = find_optima_per_buffer(sweep_wbf_v2)

    # Print optima table
    print("\n=== Optima per buffer ===")
    print(f"{'Method':<12} {'Buf':<5} {'vote_t':<7} {'prob_t':<7} {'n':<6} {'P':<7} {'R':<7} {'F1':<7}")
    for label, opt in [
        ("greedy-v1", opt_greedy_v1),
        ("greedy-v2", opt_greedy_v2),
        ("wbf-v1", opt_wbf_v1),
        ("wbf-v2", opt_wbf_v2),
    ]:
        for bm in BUFFER_METRES_LIST:
            r = opt.get(bm)
            if r is None:
                continue
            print(f"{label:<12} {bm:<5} {r['vote_t']:<7} {r['prob_t']:<7.2f} "
                  f"{r['n']:<6} {r['p']:<7.4f} {r['r']:<7.4f} {r['f1']:<7.4f}")

    # Bootstrap CIs at each optimum, plus paired permutation between
    # greedy and WBF at the matching (verifier, buffer) cell
    print("\n=== Bootstrap CIs and paired permutation tests ===")
    comparisons: list[dict] = []
    for verifier in ["v1", "v2"]:
        greedy_cands = greedy_v1 if verifier == "v1" else greedy_v2
        wbf_cands = wbf_v1 if verifier == "v1" else wbf_v2
        opt_g = opt_greedy_v1 if verifier == "v1" else opt_greedy_v2
        opt_w = opt_wbf_v1 if verifier == "v1" else opt_wbf_v2
        for bm in BUFFER_METRES_LIST:
            g_opt = opt_g.get(bm)
            w_opt = opt_w.get(bm)
            if g_opt is None or w_opt is None:
                continue
            greedy_best = filter_at_threshold(
                greedy_cands, g_opt["vote_t"], g_opt["prob_t"],
            )
            wbf_best = filter_at_threshold(
                wbf_cands, w_opt["vote_t"], w_opt["prob_t"],
            )

            print(f"\n--- verifier={verifier}, buffer={bm} m ---")
            g_ci = bootstrap_ci(
                greedy_best, gt, bounds,
                n_iterations=1000, random_seed=42, buffer_metres=bm,
            )
            w_ci = bootstrap_ci(
                wbf_best, gt, bounds,
                n_iterations=1000, random_seed=42, buffer_metres=bm,
            )
            print(f"  greedy F1 CI: [{g_ci['f1']['ci_lower']:.4f}, "
                  f"{g_ci['f1']['ci_upper']:.4f}]")
            print(f"  wbf    F1 CI: [{w_ci['f1']['ci_lower']:.4f}, "
                  f"{w_ci['f1']['ci_upper']:.4f}]")

            perm = run_permutation_test(
                gdf_a=greedy_best, gdf_b=wbf_best,
                gdf_ref=gt, gdf_bounds=bounds,
                buffer_metres=bm,
                n_permutations=10_000, seed=42,
            )
            pt = perm["permutation_test"]
            print(f"  ΔF1 (greedy−wbf): {pt['observed_f1_diff']:+.4f}")
            print(f"  p-value (2-sided): {pt['p_value']:.4f}")
            print(f"  wins greedy: {pt['wins_a']}  wins wbf: {pt['losses_a']}  "
                  f"ties: {pt['ties']}  tiles: {pt['n_tiles']}")

            comparisons.append({
                "verifier": verifier,
                "buffer_m": bm,
                "greedy": {
                    "vote_t": g_opt["vote_t"], "prob_t": g_opt["prob_t"],
                    "n": int(g_opt["n"]),
                    "f1": float(g_opt["f1"]), "p": float(g_opt["p"]),
                    "r": float(g_opt["r"]),
                    "f1_ci_95": [
                        float(g_ci["f1"]["ci_lower"]),
                        float(g_ci["f1"]["ci_upper"]),
                    ],
                },
                "wbf": {
                    "vote_t": w_opt["vote_t"], "prob_t": w_opt["prob_t"],
                    "n": int(w_opt["n"]),
                    "f1": float(w_opt["f1"]), "p": float(w_opt["p"]),
                    "r": float(w_opt["r"]),
                    "f1_ci_95": [
                        float(w_ci["f1"]["ci_lower"]),
                        float(w_ci["f1"]["ci_upper"]),
                    ],
                },
                "permutation_test": {
                    "n_permutations": 10_000,
                    "seed": 42,
                    "observed_f1_diff_greedy_minus_wbf": float(pt["observed_f1_diff"]),
                    "p_value_two_sided": float(pt["p_value"]),
                    "wins_greedy": int(pt["wins_a"]),
                    "wins_wbf": int(pt["losses_a"]),
                    "ties": int(pt["ties"]),
                    "n_tiles": int(pt["n_tiles"]),
                },
            })

    # Save everything
    summary = {
        "sweeps": {
            "greedy-v1": sweep_greedy_v1,
            "greedy-v2": sweep_greedy_v2,
            "wbf-v1": sweep_wbf_v1,
            "wbf-v2": sweep_wbf_v2,
        },
        "optima_per_buffer": {
            "greedy-v1": opt_greedy_v1,
            "greedy-v2": opt_greedy_v2,
            "wbf-v1": opt_wbf_v1,
            "wbf-v2": opt_wbf_v2,
        },
        "comparisons": comparisons,
        "parameters": {
            "vote_thresholds": VOTE_THRESHOLDS,
            "prob_thresholds": PROB_THRESHOLDS,
            "buffer_metres": BUFFER_METRES_LIST,
            "bootstrap_iterations": 1000,
            "permutation_iterations": 10_000,
            "seed": 42,
        },
    }

    out_path = BASE_DIR / "results" / "h11" / "wbf" / "production_vs_greedy_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
