#!/usr/bin/env python3
"""
Paired Tile-Level Permutation Test for PV Pipeline Comparisons
==============================================================

Compares two detection sets using the project's standard tile-swap
permutation test (micro-average F1, per-tile TP/FP/FN swap). This is
the same methodology used for the leaderboard pairwise tests (see E45).

Supports two comparison modes:

1. **WBF vs Greedy PV** (--mode wbf): Compares WBF and greedy-ball
   consensus through the same adversarial verifier.
2. **H10 Pool Size** (--mode h10): Compares pool_020 vs pool_160
   PV pipeline outputs.

Usage:
    python scripts/compare_wbf_greedy_pv_permutation.py --mode wbf --pool-size 5
    python scripts/compare_wbf_greedy_pv_permutation.py --mode wbf --pool-size 30
    python scripts/compare_wbf_greedy_pv_permutation.py --mode h10

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

from lib_advanced_metrics import calculate_f1_internal  # noqa: E402
from pairwise_permutation_test import run_permutation_test  # noqa: E402

GT_PATH = _PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"

# ── Comparison configurations ──

WBF_CONFIGS = {
    5: {
        "label_a": "greedy_pv",
        "label_b": "wbf_pv",
        "manifest_a": "outputs/h11/pv-diag-384/verified/flash-high-text-1of5/candidate_manifest.json",
        "probs_a": "outputs/h11/pv-diag-384/verified/flash-high-text-1of5/probabilities.json",
        "manifest_b": "outputs/wbf/fh-text-n5/crops/candidate_manifest.json",
        "probs_b": "outputs/wbf/fh-text-n5/verified/probabilities.json",
        "vote_t": 4,
        "prob_t": 0.15,
        "bounds": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
        "output_dir": "results/wbf-greedy-comparison",
        "output_name": "wbf_vs_greedy_pv_n5_permutation.json",
    },
    30: {
        "label_a": "greedy_pv",
        "label_b": "wbf_pv",
        "manifest_a": "outputs/h11/pv-diag-384/verified/flash-high-text-1of30/candidate_manifest.json",
        "probs_a": "outputs/h11/pv-diag-384/verified/flash-high-text-1of30/probabilities.json",
        "manifest_b": "outputs/wbf/fh-text-n30/crops/candidate_manifest.json",
        "probs_b": "outputs/wbf/fh-text-n30/verified/probabilities.json",
        "vote_t": 16,
        "prob_t": 0.15,
        "bounds": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
        "output_dir": "results/wbf-greedy-comparison",
        "output_name": "wbf_vs_greedy_pv_n30_permutation.json",
    },
}

H10_CONFIG = {
    "label_a": "pool_020_pv",
    "label_b": "pool_160_pv",
    "manifest_a": "outputs/h10/evaluation-v2/pool_020_hp4hn4/crops/candidate_manifest.json",
    "probs_a": "outputs/h10/evaluation-v2/pool_020_hp4hn4/verified/probabilities.json",
    "manifest_b": "outputs/h10/evaluation-v2/pool_160_hp4hn4/crops/candidate_manifest.json",
    "probs_b": "outputs/h10/evaluation-v2/pool_160_hp4hn4/verified/probabilities.json",
    "vote_t_a": 3,
    "prob_t_a": 0.15,
    "vote_t_b": 4,
    "prob_t_b": 0.05,
    "bounds": "inputs/calibration/h10-384/test_bounds.geojson",
    "output_dir": "results/h10",
    "output_name": "h10_pv_permutation_020_vs_160.json",
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


def run_comparison(
    cfg: dict,
    n_permutations: int,
    seed: int,
    buffer_m: int,
) -> None:
    """Run tile-level permutation test for one comparison."""
    # Load bounds and GT
    bounds_path = _PROJECT_ROOT / cfg["bounds"]
    bounds = gpd.read_file(bounds_path)
    if bounds.crs != "EPSG:32635":
        bounds = bounds.to_crs("EPSG:32635")

    gt = gpd.read_file(GT_PATH)
    if gt.crs != "EPSG:32635":
        gt = gt.to_crs("EPSG:32635")

    # Load candidates — handle per-condition thresholds (H10) or shared (WBF)
    vote_t_a = cfg.get("vote_t_a", cfg.get("vote_t"))
    prob_t_a = cfg.get("prob_t_a", cfg.get("prob_t"))
    vote_t_b = cfg.get("vote_t_b", cfg.get("vote_t"))
    prob_t_b = cfg.get("prob_t_b", cfg.get("prob_t"))

    print(f"Loading {cfg['label_a']} (vote>={vote_t_a}, prob>={prob_t_a})...")
    gdf_a = load_pv_candidates(
        str(_PROJECT_ROOT / cfg["manifest_a"]),
        str(_PROJECT_ROOT / cfg["probs_a"]),
        vote_t_a, prob_t_a,
    )
    print(f"  {cfg['label_a']}: {len(gdf_a)} candidates")

    print(f"Loading {cfg['label_b']} (vote>={vote_t_b}, prob>={prob_t_b})...")
    gdf_b = load_pv_candidates(
        str(_PROJECT_ROOT / cfg["manifest_b"]),
        str(_PROJECT_ROOT / cfg["probs_b"]),
        vote_t_b, prob_t_b,
    )
    print(f"  {cfg['label_b']}: {len(gdf_b)} candidates")

    # Global F1 for reporting
    pa, ra, f1a = calculate_f1_internal(gdf_a, gt, bounds, buffer_metres=buffer_m)
    pb, rb, f1b = calculate_f1_internal(gdf_b, gt, bounds, buffer_metres=buffer_m)
    print(f"\nGlobal F1 at {buffer_m}m:")
    print(f"  {cfg['label_a']}: P={pa:.4f}, R={ra:.4f}, F1={f1a:.4f}")
    print(f"  {cfg['label_b']}: P={pb:.4f}, R={rb:.4f}, F1={f1b:.4f}")
    print(f"  Delta F1 ({cfg['label_a']} - {cfg['label_b']}): {f1a - f1b:+.4f}")

    # Tile-level permutation test
    print(f"\nRunning tile-level permutation test ({n_permutations:,} iterations, "
          f"{len(bounds)} tiles, seed {seed})...")
    perm_result = run_permutation_test(
        gdf_a, gdf_b, gt, bounds,
        buffer_metres=buffer_m,
        n_permutations=n_permutations,
        seed=seed,
    )

    obs_diff = perm_result["permutation_test"]["observed_f1_diff"]
    p_value = perm_result["permutation_test"]["p_value"]
    wins_a = perm_result["permutation_test"]["wins_a"]
    losses_a = perm_result["permutation_test"]["losses_a"]
    ties = perm_result["permutation_test"]["ties"]

    sig = "SIGNIFICANT" if p_value < 0.05 else "NOT significant"
    print("\nResults:")
    print(f"  Observed F1 diff ({cfg['label_a']} - {cfg['label_b']}): {obs_diff:+.4f}")
    print(f"  p-value (two-sided): {p_value:.4f}")
    print(f"  {sig} (p {'<' if p_value < 0.05 else '>='} 0.05)")
    print(f"  Per-tile: {cfg['label_a']} wins {wins_a}, "
          f"{cfg['label_b']} wins {losses_a}, ties {ties}")

    # Save — wrap the perm_result with comparison metadata
    output = {
        "comparison": f"{cfg['label_a']}_vs_{cfg['label_b']}",
        "method": "tile-level micro-average F1 permutation test (E45)",
        "buffer_m": buffer_m,
        "thresholds_a": {"vote_t": vote_t_a, "prob_t": prob_t_a},
        "thresholds_b": {"vote_t": vote_t_b, "prob_t": prob_t_b},
        **perm_result,
    }

    # Remove per_tile details from saved output (large, not needed for summary)
    output.pop("per_tile", None)

    out_dir = _PROJECT_ROOT / cfg["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / cfg["output_name"]
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")


def main() -> None:
    """Run tile-level permutation test."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", required=True, choices=["wbf", "h10"],
        help="Comparison mode: 'wbf' (WBF vs greedy PV) or 'h10' (pool size)",
    )
    parser.add_argument(
        "--pool-size", type=int, choices=[5, 30], default=None,
        help="Pool size for WBF mode (required for --mode wbf)",
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

    if args.mode == "wbf":
        if args.pool_size is None:
            parser.error("--pool-size required for --mode wbf")
        cfg = WBF_CONFIGS[args.pool_size]
    else:
        cfg = H10_CONFIG

    run_comparison(cfg, args.n_permutations, args.seed, args.buffer)


if __name__ == "__main__":
    main()
