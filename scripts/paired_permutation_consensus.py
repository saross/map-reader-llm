"""
Paired Permutation Test for Consensus Voting Conditions
========================================================

Description:
    Compares two consensus voting conditions using a paired permutation
    test at tile level. Each tile contributes a paired (F1_A, F1_B)
    observation; the test permutes condition labels within tiles to
    build a null distribution of the mean F1 difference.

    This is the appropriate test for Phase 3a comparisons because:
    - Tiles are the natural experimental unit (same 60 tiles in both
      conditions)
    - Pairing controls for between-tile variance (some tiles are
      harder than others)
    - The permutation test makes no distributional assumptions about
      tile-level F1 values

Usage:
    # Compare HIGH vs MINIMAL thinking on Track 2 (Text)
    python scripts/paired_permutation_consensus.py \
        --condition-a outputs/phase3a/track2-text-high \
        --condition-b outputs/phase3a/track2-text \
        --config-a T0.7,30,22 \
        --config-b T1.0,30,22 \
        --label-a "Text HIGH" \
        --label-b "Text MINIMAL" \
        --output-dir results/phase3a-consensus/permutation-tests

    Config format: temperature,pool_size,threshold (e.g. T0.7,30,22)

Author: Shawn Ross
Licence: Apache 2.0
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from analyse_consensus_sweep import (  # noqa: E402
    consensus_to_gdf,
    precompute_clusters,
)
from lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
)
from merge_passes import apply_threshold  # noqa: E402

# Default paths for evaluation data
GROUND_TRUTH_PATH = (
    BASE_DIR / "inputs/vectors/references/mounds-reference.geojson"
)
BOUNDS_PATH = BASE_DIR / "inputs/vectors/bounds/validation_bounds.geojson"
TARGET_CRS = "EPSG:32635"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_config(config_str: str) -> tuple[str, int, int]:
    """
    Parse a consensus config string like 'T0.7,30,22'.

    Returns:
        Tuple of (temperature_label, pool_size, threshold).
    """
    parts = config_str.split(",")
    if len(parts) != 3:
        raise ValueError(
            f"Config must be 'temperature,pool_size,threshold', "
            f"got '{config_str}'"
        )
    return parts[0], int(parts[1]), int(parts[2])


def compute_tile_f1s(
    tile_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute per-tile F1 from TP/FP/FN counts.

    Args:
        tile_metrics: DataFrame with columns [tile_name, tp, fp, fn].

    Returns:
        DataFrame with columns [tile_name, f1, precision, recall].
    """
    rows = []
    for _, row in tile_metrics.iterrows():
        tp, fp, fn = row["tp"], row["fp"], row["fn"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        rows.append({
            "tile_name": row["tile_name"],
            "f1": f1,
            "precision": precision,
            "recall": recall,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        })
    return pd.DataFrame(rows)


def paired_permutation_test(
    f1_a: np.ndarray,
    f1_b: np.ndarray,
    n_permutations: int = 10_000,
    seed: int = 42,
) -> dict:
    """
    Two-sided paired permutation test on tile-level F1 differences.

    Under the null hypothesis, condition labels are exchangeable within
    each tile. We permute labels independently for each tile and compute
    the mean difference for each permutation to build the null
    distribution.

    Args:
        f1_a: Per-tile F1 values for condition A.
        f1_b: Per-tile F1 values for condition B.
        n_permutations: Number of permutations (default 10,000).
        seed: Random seed for reproducibility.

    Returns:
        Dict with observed_diff, p_value, n_permutations, wins/losses/ties,
        and null distribution summary statistics.
    """
    assert len(f1_a) == len(f1_b), "Arrays must have equal length"
    n_tiles = len(f1_a)

    differences = f1_a - f1_b
    observed_diff = float(np.mean(differences))

    # Count wins, losses, ties
    wins = int(np.sum(differences > 0))
    losses = int(np.sum(differences < 0))
    ties = int(np.sum(differences == 0))

    # Permutation null distribution
    rng = np.random.default_rng(seed)
    null_diffs = np.empty(n_permutations)

    for i in range(n_permutations):
        # For each tile, independently flip the sign of the difference
        # (equivalent to swapping condition labels)
        signs = rng.choice([-1, 1], size=n_tiles)
        null_diffs[i] = np.mean(signs * differences)

    # Two-sided p-value: proportion of permutations with |diff| >= |observed|
    p_value = float(
        np.mean(np.abs(null_diffs) >= np.abs(observed_diff))
    )

    return {
        "observed_mean_diff": round(observed_diff, 6),
        "p_value": round(p_value, 4),
        "n_permutations": n_permutations,
        "n_tiles": n_tiles,
        "wins_a": wins,
        "losses_a": losses,
        "ties": ties,
        "null_distribution": {
            "mean": round(float(np.mean(null_diffs)), 6),
            "std": round(float(np.std(null_diffs)), 6),
            "percentile_2.5": round(float(np.percentile(null_diffs, 2.5)), 6),
            "percentile_97.5": round(float(np.percentile(null_diffs, 97.5)), 6),
        },
    }


def build_consensus_gdf(
    study_dir: Path,
    temperature: str,
    pool_size: int,
    threshold: int,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Build a consensus GeoDataFrame for a specific (T, N, x) config.

    Loads runs, clusters detections, applies vote threshold, and
    assigns source tiles via spatial join.

    Args:
        study_dir: Path to condition output directory.
        temperature: Temperature label (e.g. 'T0.7').
        pool_size: Number of runs to pool.
        threshold: Minimum vote count.
        gdf_bounds: Tile boundary GeoDataFrame.

    Returns:
        GeoDataFrame of consensus detections with source_tile.
    """
    clusters_dict = precompute_clusters(
        study_dir,
        temperatures=[temperature],
        pool_sizes=[pool_size],
    )

    clusters = clusters_dict.get((temperature, pool_size), [])
    if not clusters:
        logger.error(
            "No clusters for %s N=%d in %s",
            temperature, pool_size, study_dir,
        )
        return gpd.GeoDataFrame()

    consensus_fc = apply_threshold(clusters, threshold, pool_size)
    return consensus_to_gdf(consensus_fc, gdf_bounds)


def run_comparison(
    condition_a_dir: Path,
    condition_b_dir: Path,
    config_a: tuple[str, int, int],
    config_b: tuple[str, int, int],
    label_a: str,
    label_b: str,
    buffer_metres: int = 20,
    n_permutations: int = 10_000,
    seed: int = 42,
) -> dict:
    """
    Run paired permutation test comparing two consensus conditions.

    Args:
        condition_a_dir: Path to condition A output directory.
        condition_b_dir: Path to condition B output directory.
        config_a: (temperature, pool_size, threshold) for condition A.
        config_b: (temperature, pool_size, threshold) for condition B.
        label_a: Human-readable label for condition A.
        label_b: Human-readable label for condition B.
        buffer_metres: Spatial matching tolerance.
        n_permutations: Number of permutations.
        seed: Random seed.

    Returns:
        Dict with full comparison results.
    """
    # Load shared evaluation data
    gdf_ref = gpd.read_file(GROUND_TRUTH_PATH).to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file(BOUNDS_PATH).to_crs(TARGET_CRS)

    temp_a, pool_a, thresh_a = config_a
    temp_b, pool_b, thresh_b = config_b

    logger.info(
        "Condition A: %s — %s N=%d x=%d",
        label_a, temp_a, pool_a, thresh_a,
    )
    logger.info(
        "Condition B: %s — %s N=%d x=%d",
        label_b, temp_b, pool_b, thresh_b,
    )

    # Build consensus GeoDataFrames
    logger.info("Building consensus for condition A...")
    gdf_consensus_a = build_consensus_gdf(
        condition_a_dir, temp_a, pool_a, thresh_a, gdf_bounds,
    )
    logger.info(
        "  Condition A: %d consensus detections", len(gdf_consensus_a),
    )

    logger.info("Building consensus for condition B...")
    gdf_consensus_b = build_consensus_gdf(
        condition_b_dir, temp_b, pool_b, thresh_b, gdf_bounds,
    )
    logger.info(
        "  Condition B: %d consensus detections", len(gdf_consensus_b),
    )

    # Compute per-tile metrics
    logger.info("Computing per-tile metrics (buffer=%dm)...", buffer_metres)
    tile_metrics_a = compute_per_tile_tp_fp_fn(
        gdf_consensus_a, gdf_ref, gdf_bounds,
        buffer_metres=buffer_metres,
    )
    tile_metrics_b = compute_per_tile_tp_fp_fn(
        gdf_consensus_b, gdf_ref, gdf_bounds,
        buffer_metres=buffer_metres,
    )

    tile_f1s_a = compute_tile_f1s(tile_metrics_a)
    tile_f1s_b = compute_tile_f1s(tile_metrics_b)

    # Merge on tile_name for paired comparison
    merged = tile_f1s_a.merge(
        tile_f1s_b,
        on="tile_name",
        suffixes=("_a", "_b"),
    )

    # Global F1 (micro-averaged from TP/FP/FN totals)
    tp_a, fp_a, fn_a = (
        tile_metrics_a["tp"].sum(),
        tile_metrics_a["fp"].sum(),
        tile_metrics_a["fn"].sum(),
    )
    tp_b, fp_b, fn_b = (
        tile_metrics_b["tp"].sum(),
        tile_metrics_b["fp"].sum(),
        tile_metrics_b["fn"].sum(),
    )
    global_f1_a = (
        2 * tp_a / (2 * tp_a + fp_a + fn_a)
        if (2 * tp_a + fp_a + fn_a) > 0
        else 0.0
    )
    global_f1_b = (
        2 * tp_b / (2 * tp_b + fp_b + fn_b)
        if (2 * tp_b + fp_b + fn_b) > 0
        else 0.0
    )

    logger.info(
        "Global F1: %s=%.4f, %s=%.4f (diff=%.4f)",
        label_a, global_f1_a, label_b, global_f1_b,
        global_f1_a - global_f1_b,
    )

    # Run paired permutation test
    logger.info(
        "Running paired permutation test (%d permutations)...",
        n_permutations,
    )
    perm_result = paired_permutation_test(
        merged["f1_a"].values,
        merged["f1_b"].values,
        n_permutations=n_permutations,
        seed=seed,
    )

    logger.info(
        "  Observed mean diff: %.4f, p=%.4f, wins:losses = %d:%d",
        perm_result["observed_mean_diff"],
        perm_result["p_value"],
        perm_result["wins_a"],
        perm_result["losses_a"],
    )

    # Assemble full results
    return {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "script": "paired_permutation_consensus.py",
            "buffer_metres": buffer_metres,
            "n_permutations": n_permutations,
            "seed": seed,
        },
        "condition_a": {
            "label": label_a,
            "study_dir": str(condition_a_dir),
            "config": {
                "temperature": temp_a,
                "pool_size": pool_a,
                "threshold": thresh_a,
            },
            "global_f1": round(global_f1_a, 4),
            "n_detections": len(gdf_consensus_a),
            "tp": int(tp_a),
            "fp": int(fp_a),
            "fn": int(fn_a),
        },
        "condition_b": {
            "label": label_b,
            "study_dir": str(condition_b_dir),
            "config": {
                "temperature": temp_b,
                "pool_size": pool_b,
                "threshold": thresh_b,
            },
            "global_f1": round(global_f1_b, 4),
            "n_detections": len(gdf_consensus_b),
            "tp": int(tp_b),
            "fp": int(fp_b),
            "fn": int(fn_b),
        },
        "permutation_test": perm_result,
        "per_tile": merged.to_dict(orient="records"),
    }


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Paired permutation test comparing two consensus voting "
            "conditions at tile level."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # HIGH vs MINIMAL thinking on Track 2 (Text)
  python scripts/paired_permutation_consensus.py \\
      --condition-a outputs/phase3a/track2-text-high \\
      --condition-b outputs/phase3a/track2-text \\
      --config-a T0.7,30,22 \\
      --config-b T1.0,30,22 \\
      --label-a "Text HIGH" \\
      --label-b "Text MINIMAL"

  # HIGH vs MINIMAL thinking on Track 1 (Image)
  python scripts/paired_permutation_consensus.py \\
      --condition-a outputs/phase3a/track1-image-high \\
      --condition-b outputs/phase3a/track1-image \\
      --config-a T0.3,30,25 \\
      --config-b T0.7,10,6 \\
      --label-a "Image HIGH" \\
      --label-b "Image MINIMAL"
""",
    )
    parser.add_argument(
        "--condition-a", type=Path, required=True,
        help="Path to condition A output directory",
    )
    parser.add_argument(
        "--condition-b", type=Path, required=True,
        help="Path to condition B output directory",
    )
    parser.add_argument(
        "--config-a", type=str, required=True,
        help="Consensus config for A: temperature,pool_size,threshold",
    )
    parser.add_argument(
        "--config-b", type=str, required=True,
        help="Consensus config for B: temperature,pool_size,threshold",
    )
    parser.add_argument(
        "--label-a", type=str, default="Condition A",
        help="Human-readable label for condition A",
    )
    parser.add_argument(
        "--label-b", type=str, default="Condition B",
        help="Human-readable label for condition B",
    )
    parser.add_argument(
        "--buffer-metres", type=int, default=20,
        help="Spatial matching tolerance in metres (default: 20)",
    )
    parser.add_argument(
        "--n-permutations", type=int, default=10_000,
        help="Number of permutations (default: 10,000)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("results/phase3a-consensus/permutation-tests"),
        help="Output directory for results JSON",
    )

    args = parser.parse_args()

    config_a = parse_config(args.config_a)
    config_b = parse_config(args.config_b)

    results = run_comparison(
        condition_a_dir=args.condition_a,
        condition_b_dir=args.condition_b,
        config_a=config_a,
        config_b=config_b,
        label_a=args.label_a,
        label_b=args.label_b,
        buffer_metres=args.buffer_metres,
        n_permutations=args.n_permutations,
        seed=args.seed,
    )

    # Save results
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # Sanitise labels for filename
    safe_a = args.label_a.lower().replace(" ", "-")
    safe_b = args.label_b.lower().replace(" ", "-")
    output_file = (
        args.output_dir
        / f"permutation-{safe_a}-vs-{safe_b}-{args.buffer_metres}m.json"
    )

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info("Results saved to %s", output_file)

    # Print summary
    perm = results["permutation_test"]
    sig = "SIGNIFICANT" if perm["p_value"] < 0.05 else "not significant"
    print(
        f"\n{'=' * 60}\n"
        f"  {args.label_a} vs {args.label_b}\n"
        f"  F1: {results['condition_a']['global_f1']:.4f} vs "
        f"{results['condition_b']['global_f1']:.4f} "
        f"(diff = {perm['observed_mean_diff']:+.4f})\n"
        f"  p = {perm['p_value']:.4f} ({sig} at α=0.05)\n"
        f"  Tile wins:losses:ties = "
        f"{perm['wins_a']}:{perm['losses_a']}:{perm['ties']}\n"
        f"{'=' * 60}"
    )


if __name__ == "__main__":
    main()
