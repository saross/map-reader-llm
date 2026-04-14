#!/usr/bin/env python3
"""
Paired Permutation Test: WBF PV vs Greedy PV
=============================================

Compares WBF and greedy-ball proposer consensus through the same
adversarial verifier pipeline, using a paired permutation test
on per-map F1 scores.

Usage:
    python scripts/compare_wbf_greedy_pv_permutation.py --pool-size 5
    python scripts/compare_wbf_greedy_pv_permutation.py --pool-size 30

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

from lib_advanced_metrics import calculate_f1_internal, get_map_name  # noqa: E402

GT_PATH = _PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BOUNDS_PATH = _PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUTPUT_DIR = _PROJECT_ROOT / "results/wbf-greedy-comparison"

CONFIGS = {
    5: {
        "greedy_manifest": "outputs/h11/pv-diag-384/verified/flash-high-text-1of5/candidate_manifest.json",
        "greedy_probs": "outputs/h11/pv-diag-384/verified/flash-high-text-1of5/probabilities.json",
        "wbf_manifest": "outputs/h11/wbf/fh-text-n5/crops/candidate_manifest.json",
        "wbf_probs": "outputs/h11/wbf/fh-text-n5/verified/probabilities.json",
        "vote_t": 4,
        "prob_t": 0.15,
    },
    30: {
        "greedy_manifest": "outputs/h11/pv-diag-384/verified/flash-high-text-1of30/candidate_manifest.json",
        "greedy_probs": "outputs/h11/pv-diag-384/verified/flash-high-text-1of30/probabilities.json",
        "wbf_manifest": "outputs/h11/wbf/fh-text-n30/crops/candidate_manifest.json",
        "wbf_probs": "outputs/h11/wbf/fh-text-n30/verified/probabilities.json",
        "vote_t": 16,
        "prob_t": 0.15,
    },
}


def load_pv_candidates(
    manifest_path: str,
    probs_path: str,
    vote_t: int,
    prob_t: float,
) -> gpd.GeoDataFrame:
    """Load PV candidates filtered at given thresholds."""
    with open(manifest_path) as f:
        manifest = json.load(f)
    with open(probs_path) as f:
        probs = json.load(f)

    results = probs.get("results", {})
    points = []
    tiles = []

    for c in manifest["candidates"]:
        cid = c["candidate_id"]
        vote = c["properties"].get(
            "vote_count", c["properties"].get("proposer_votes", 0)
        )
        if vote < vote_t:
            continue

        # Try multiple candidate ID formats
        prob_data = None
        for key in [f"candidate_{int(cid):05d}", f"candidate_{cid}", str(cid)]:
            if key in results:
                prob_data = results[key]
                break
        if prob_data is None:
            continue

        prob = prob_data.get("mound_probability", 0)
        if prob < prob_t:
            continue

        points.append(Point(c["centroid_x"], c["centroid_y"]))
        tiles.append(c["source_tile"])

    return gpd.GeoDataFrame(
        {"source_tile": tiles}, geometry=points, crs="EPSG:32635"
    )


def main() -> None:
    """Run paired permutation test."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pool-size", type=int, required=True, choices=[5, 30],
        help="Pool size: 5 or 30",
    )
    parser.add_argument(
        "--n-permutations", type=int, default=10000,
        help="Number of permutations (default: 10,000)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--buffer", type=int, default=20,
        help="F1 matching buffer in metres (default: 20)",
    )
    args = parser.parse_args()

    cfg = CONFIGS[args.pool_size]

    # Load evaluation data
    gt = gpd.read_file(GT_PATH)
    bounds = gpd.read_file(BOUNDS_PATH)

    # Load candidates at thresholds
    print(f"Loading greedy PV candidates (vote>={cfg['vote_t']}, prob>={cfg['prob_t']})...")
    greedy_gdf = load_pv_candidates(
        str(_PROJECT_ROOT / cfg["greedy_manifest"]),
        str(_PROJECT_ROOT / cfg["greedy_probs"]),
        cfg["vote_t"], cfg["prob_t"],
    )
    print(f"  Greedy: {len(greedy_gdf)} candidates")

    print(f"Loading WBF PV candidates (vote>={cfg['vote_t']}, prob>={cfg['prob_t']})...")
    wbf_gdf = load_pv_candidates(
        str(_PROJECT_ROOT / cfg["wbf_manifest"]),
        str(_PROJECT_ROOT / cfg["wbf_probs"]),
        cfg["vote_t"], cfg["prob_t"],
    )
    print(f"  WBF: {len(wbf_gdf)} candidates")

    # Global F1
    gp, gr, gf1 = calculate_f1_internal(
        greedy_gdf, gt, bounds, buffer_metres=args.buffer
    )
    wp, wr, wf1 = calculate_f1_internal(
        wbf_gdf, gt, bounds, buffer_metres=args.buffer
    )
    print(f"\nGlobal F1 at {args.buffer}m:")
    print(f"  Greedy PV: P={gp:.4f}, R={gr:.4f}, F1={gf1:.4f}")
    print(f"  WBF PV:    P={wp:.4f}, R={wr:.4f}, F1={wf1:.4f}")
    print(f"  Delta F1:  {wf1 - gf1:+.4f}")

    # Per-map F1 for paired test
    map_names = sorted(
        {get_map_name(n) for n in bounds["tile_name"].unique()} - {"Unknown"}
    )
    print(f"\nPer-map breakdown ({len(map_names)} maps):")

    greedy_per_map = []
    wbf_per_map = []
    for map_name in map_names:
        map_bounds = bounds[bounds["tile_name"].str.startswith(map_name)]
        gp_m, gr_m, gf1_m = calculate_f1_internal(
            greedy_gdf, gt, map_bounds, buffer_metres=args.buffer
        )
        wp_m, wr_m, wf1_m = calculate_f1_internal(
            wbf_gdf, gt, map_bounds, buffer_metres=args.buffer
        )
        greedy_per_map.append(gf1_m)
        wbf_per_map.append(wf1_m)
        print(
            f"  {map_name}: greedy={gf1_m:.4f}, wbf={wf1_m:.4f}, "
            f"delta={wf1_m - gf1_m:+.4f}"
        )

    # Paired permutation test
    greedy_arr = np.array(greedy_per_map)
    wbf_arr = np.array(wbf_per_map)
    diffs = wbf_arr - greedy_arr
    obs_mean_diff = float(np.mean(diffs))

    rng = np.random.RandomState(args.seed)
    n_extreme = 0
    for _ in range(args.n_permutations):
        swaps = rng.randint(0, 2, size=len(diffs))
        perm_diffs = np.where(swaps, -diffs, diffs)
        if abs(np.mean(perm_diffs)) >= abs(obs_mean_diff):
            n_extreme += 1

    p_value = n_extreme / args.n_permutations

    sig = "SIGNIFICANT" if p_value < 0.05 else "NOT significant"
    print(f"\nPaired permutation test ({args.n_permutations:,} iterations, seed {args.seed}):")
    print(f"  Observed mean delta F1: {obs_mean_diff:+.4f}")
    print(f"  p-value (two-sided): {p_value:.4f}")
    print(f"  Result: {sig} (p {'<' if p_value < 0.05 else '>='} 0.05)")

    # Wins/losses
    wbf_wins = int(np.sum(diffs > 0))
    greedy_wins = int(np.sum(diffs < 0))
    ties = int(np.sum(diffs == 0))
    print(f"  Per-map: WBF wins {wbf_wins}, greedy wins {greedy_wins}, ties {ties}")

    # Save results
    result = {
        "comparison": "WBF_PV_vs_Greedy_PV",
        "condition": f"FH text N={args.pool_size}",
        "buffer_m": args.buffer,
        "vote_t": cfg["vote_t"],
        "prob_t": cfg["prob_t"],
        "greedy": {
            "n": len(greedy_gdf), "p": round(gp, 6),
            "r": round(gr, 6), "f1": round(gf1, 6),
        },
        "wbf": {
            "n": len(wbf_gdf), "p": round(wp, 6),
            "r": round(wr, 6), "f1": round(wf1, 6),
        },
        "delta_f1": round(wf1 - gf1, 6),
        "permutation_test": {
            "n_permutations": args.n_permutations,
            "seed": args.seed,
            "observed_mean_diff": round(obs_mean_diff, 6),
            "p_value_two_sided": p_value,
            "per_map": {
                m: {"greedy": round(g, 4), "wbf": round(w, 4)}
                for m, g, w in zip(map_names, greedy_per_map, wbf_per_map)
            },
            "wbf_wins": wbf_wins,
            "greedy_wins": greedy_wins,
            "ties": ties,
        },
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"wbf_vs_greedy_pv_n{args.pool_size}_permutation.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
