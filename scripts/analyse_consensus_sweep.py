#!/usr/bin/env python3
"""
Consensus Voting Sweep Analysis
================================

Analyses whether consensus voting across multiple runs at elevated
temperatures can outperform single-run baseline performance.

Originally built for Phase 2b retroactive analysis (5 temperatures x
10 runs, zero additional API calls). Extended for Phase 3a validation
with configurable temperatures, pool sizes, and baseline F1 via CLI.

For each (temperature, pool_size, threshold) combination, detections
are merged using the preregistration Section 8.5 voting algorithm,
then evaluated against ground truth with bootstrapped 95% confidence
intervals (CIs).

Pool sizes (configurable via --pool-sizes):
- Default: N=5, N=10 (Phase 2b)
- Phase 3a: N=5, N=10, N=30

Key question: Does the best (temperature, N, threshold) consensus
configuration beat the single-run baseline F1?

Usage:
    # Phase 2b (defaults)
    python scripts/analyse_consensus_sweep.py
    python scripts/analyse_consensus_sweep.py --bootstrap 200  # quick

    # Phase 3a Track 1 (image)
    python scripts/analyse_consensus_sweep.py \\
        --study-dir outputs/phase3a/track1-image \\
        --output-dir results/phase3a-consensus/track1-image \\
        --temperatures T0.3 T0.7 \\
        --pool-sizes 5 10 30 \\
        --baseline-f1 0.609

    # Phase 3a Track 2 (text-only)
    python scripts/analyse_consensus_sweep.py \\
        --study-dir outputs/phase3a/track2-text \\
        --output-dir results/phase3a-consensus/track2-text \\
        --temperatures T0.3 T0.7 \\
        --pool-sizes 5 10 30 \\
        --baseline-f1 0.660

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping, shape

# Add scripts directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))
from analyse_phase2_results import load_condition_results
from lib_advanced_metrics import bootstrap_ci, calculate_f1_internal
from merge_passes import (
    apply_threshold,
    cluster_across_passes,
    deduplicate_within_pass,
)

# Script version
__version__ = "2.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
TEMPERATURES = ["T0.0", "T0.3", "T0.7", "T1.0", "T1.3"]
POOL_SIZES = [5, 10]
DEFAULT_N_BOOTSTRAP = 1000
RANDOM_SEED = 42
TARGET_CRS = "EPSG:32635"

# Default paths (relative to repository root)
DEFAULT_STUDY_DIR = Path("outputs/phase2b/track1-image")
DEFAULT_GROUND_TRUTH = Path(
    "inputs/vectors/references/mounds-reference.geojson"
)
DEFAULT_BOUNDS = Path("inputs/vectors/bounds/validation_bounds.geojson")
DEFAULT_OUTPUT_DIR = Path("results/phase2b-consensus")


def gdf_to_features(gdf: gpd.GeoDataFrame) -> list[dict]:
    """
    Convert GeoDataFrame rows to GeoJSON feature dicts.

    Produces the format expected by merge_passes.deduplicate_within_pass():
    each dict has 'geometry' (GeoJSON geometry dict) and 'properties'
    (dict with 'source_tile' and 'subtype' keys).

    Args:
        gdf: GeoDataFrame with geometry column and 'source_tile',
            'subtype' attributes.

    Returns:
        List of GeoJSON-like feature dicts.
    """
    features = []
    for _, row in gdf.iterrows():
        feature = {
            "geometry": mapping(row.geometry),
            "properties": {
                "source_tile": row.get(
                    "source_tile", "unknown"
                ),
                "subtype": row.get("subtype", "mound"),
            },
        }
        features.append(feature)
    return features


def consensus_to_gdf(
    consensus_fc: dict,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Convert consensus FeatureCollection to GeoDataFrame with source_tile.

    The consensus output from apply_threshold() contains Point geometries
    with 'source_tiles' (plural) in properties — a list of all
    contributing tiles. For F1 evaluation, each detection needs a single
    'source_tile' assigned via spatial join against tile boundaries.

    Args:
        consensus_fc: GeoJSON FeatureCollection from apply_threshold().
        gdf_bounds: GeoDataFrame of tile boundaries with 'tile_name'.

    Returns:
        GeoDataFrame with 'source_tile', 'subtype', and Point geometry
        in EPSG:32635.
    """
    features = consensus_fc.get("features", [])
    if not features:
        return gpd.GeoDataFrame(
            columns=["source_tile", "subtype", "geometry"],
            geometry="geometry",
            crs=TARGET_CRS,
        )

    # Build GeoDataFrame from Point features
    points = [shape(f["geometry"]) for f in features]
    props_list = [f.get("properties", {}) for f in features]
    gdf = gpd.GeoDataFrame(
        props_list, geometry=points, crs=TARGET_CRS
    )

    # Assign source_tile via spatial join against tile boundaries.
    # Each consensus centroid falls within exactly one tile (or on a
    # boundary between tiles, in which case we take the first match).
    gdf_joined = gpd.sjoin(
        gdf,
        gdf_bounds[["tile_name", "geometry"]],
        how="left",
        predicate="intersects",
    )

    # Deduplicate: points on tile boundaries may match multiple tiles
    gdf_joined = gdf_joined[
        ~gdf_joined.index.duplicated(keep="first")
    ]
    gdf_joined["source_tile"] = gdf_joined[
        "tile_name"
    ].fillna("unknown")

    # Return only columns needed for F1 evaluation
    result = gdf_joined[
        ["source_tile", "subtype", "geometry"]
    ].copy()
    return result


def evaluate_single_config(
    temperature: str,
    pool_size: int,
    threshold: int,
    clusters: list[dict],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_bootstrap: int,
    random_seed: int,
) -> dict:
    """
    Evaluate a single (T, N, x) consensus configuration.

    Applies the vote threshold to pre-computed clusters, converts the
    result to a GeoDataFrame, assigns source tiles via spatial join,
    and calculates F1 with bootstrapped confidence intervals.

    Args:
        temperature: Temperature condition label (e.g., 'T0.3').
        pool_size: Number of runs in the consensus pool (N).
        threshold: Minimum vote count to retain a detection (x).
        clusters: Pre-computed clusters from cluster_across_passes().
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Tile boundary GeoDataFrame.
        n_bootstrap: Number of bootstrap iterations.
        random_seed: Random seed for reproducibility.

    Returns:
        Dict with temperature, pool_size, threshold, metrics, and CIs.
    """
    # Apply vote threshold to pre-computed clusters
    consensus_fc = apply_threshold(clusters, threshold, pool_size)
    gdf_consensus = consensus_to_gdf(consensus_fc, gdf_bounds)
    n_detections = len(gdf_consensus)

    # Handle empty consensus gracefully (e.g., unanimous threshold
    # at high temperature where no location has all-run agreement)
    if n_detections == 0:
        return {
            "temperature": temperature,
            "pool_size": pool_size,
            "threshold": threshold,
            "f1": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_ci_lo": 0.0,
            "f1_ci_hi": 0.0,
            "p_ci_lo": 0.0,
            "p_ci_hi": 0.0,
            "r_ci_lo": 0.0,
            "r_ci_hi": 0.0,
            "n_detections": 0,
        }

    # Point estimates
    precision, recall, f1 = calculate_f1_internal(
        gdf_consensus, gdf_ref, gdf_bounds, buffer_metres=20
    )

    # Bootstrapped 95% CIs (tile-level resampling)
    ci = bootstrap_ci(
        gdf_consensus,
        gdf_ref,
        gdf_bounds,
        n_iterations=n_bootstrap,
        random_seed=random_seed,
    )

    return {
        "temperature": temperature,
        "pool_size": pool_size,
        "threshold": threshold,
        "f1": round(f1, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_ci_lo": round(ci["f1"]["ci_lower"], 4),
        "f1_ci_hi": round(ci["f1"]["ci_upper"], 4),
        "p_ci_lo": round(ci["precision"]["ci_lower"], 4),
        "p_ci_hi": round(ci["precision"]["ci_upper"], 4),
        "r_ci_lo": round(ci["recall"]["ci_lower"], 4),
        "r_ci_hi": round(ci["recall"]["ci_upper"], 4),
        "n_detections": n_detections,
    }


def precompute_clusters(
    study_dir: Path,
    temperatures: list[str],
    pool_sizes: list[int],
) -> dict[tuple[str, int], list[dict]]:
    """
    Load detection data and precompute clusters for all (T, N) combos.

    For each temperature and pool size:
    1. Load per-run GeoDataFrames via load_condition_results()
    2. Convert to GeoJSON features via gdf_to_features()
    3. Deduplicate within each run (20 m tolerance)
    4. Cluster across runs (20 m tolerance) and count votes

    Args:
        study_dir: Base directory containing temperature condition dirs.
        temperatures: List of temperature condition labels.
        pool_sizes: List of pool sizes (N values).

    Returns:
        Dict mapping (temperature, pool_size) to cluster list.
    """
    all_clusters: dict[tuple[str, int], list[dict]] = {}

    for temp in temperatures:
        logger.info("Loading runs for %s...", temp)
        run_results = load_condition_results(study_dir, temp)

        if not run_results:
            logger.warning("No data for %s, skipping", temp)
            continue

        # Standardise CRS (Coordinate Reference System)
        standardised: list[tuple[int, gpd.GeoDataFrame]] = []
        for run_num, gdf in run_results:
            if gdf.crs != TARGET_CRS:
                gdf = gdf.to_crs(TARGET_CRS)
            standardised.append((run_num, gdf))

        for pool_size in pool_sizes:
            # Select runs: first N (preregistration Section 3.8)
            selected = [
                (rn, gdf)
                for rn, gdf in standardised
                if rn <= pool_size
            ]

            if len(selected) < pool_size:
                logger.warning(
                    "%s N=%d: only %d runs available (expected %d)",
                    temp,
                    pool_size,
                    len(selected),
                    pool_size,
                )

            # Convert GeoDataFrames to features, deduplicate, cluster
            pass_detections: dict[str, list[dict]] = {}
            for run_num, gdf in selected:
                features = gdf_to_features(gdf)
                deduped = deduplicate_within_pass(features)
                pass_detections[f"run_{run_num}"] = deduped

            clusters = cluster_across_passes(pass_detections)
            all_clusters[(temp, pool_size)] = clusters

            logger.info(
                "  %s N=%d: %d runs -> %d clusters",
                temp,
                pool_size,
                len(selected),
                len(clusters),
            )

    return all_clusters


def find_optimal_configs(
    results: list[dict],
    baseline_f1: float,
) -> dict:
    """
    Identify optimal consensus configurations and compare to baseline.

    For each temperature, finds the (N, x) combination that maximises
    F1. Determines whether any consensus configuration beats the
    single-run T=0.0 baseline.

    Args:
        results: List of evaluation result dicts.
        baseline_f1: Single-run T=0.0 mean F1 for comparison.

    Returns:
        Dict with per-temperature optima, global optimum, and
        beat-baseline determination.
    """
    df = pd.DataFrame(results)

    per_temp_optima = {}
    for temp in df["temperature"].unique():
        temp_df = df[df["temperature"] == temp]
        best_idx = temp_df["f1"].idxmax()
        best_row = temp_df.loc[best_idx]
        per_temp_optima[temp] = {
            "pool_size": int(best_row["pool_size"]),
            "threshold": int(best_row["threshold"]),
            "f1": float(best_row["f1"]),
            "f1_ci": [
                float(best_row["f1_ci_lo"]),
                float(best_row["f1_ci_hi"]),
            ],
            "precision": float(best_row["precision"]),
            "recall": float(best_row["recall"]),
            "n_detections": int(best_row["n_detections"]),
            "delta_vs_baseline": round(
                float(best_row["f1"]) - baseline_f1, 4
            ),
        }

    # Global optimum across all temperatures
    global_best_idx = df["f1"].idxmax()
    global_best = df.loc[global_best_idx]
    beats_baseline = float(global_best["f1"]) > baseline_f1

    return {
        "per_temperature_optima": per_temp_optima,
        "global_optimum": {
            "temperature": global_best["temperature"],
            "pool_size": int(global_best["pool_size"]),
            "threshold": int(global_best["threshold"]),
            "f1": float(global_best["f1"]),
            "f1_ci": [
                float(global_best["f1_ci_lo"]),
                float(global_best["f1_ci_hi"]),
            ],
            "delta_vs_baseline": round(
                float(global_best["f1"]) - baseline_f1, 4
            ),
        },
        "baseline_f1": baseline_f1,
        "beats_baseline": beats_baseline,
    }


def generate_summary_md(
    results: list[dict],
    optima: dict,
    metadata: dict,
) -> str:
    """
    Generate a Markdown summary of the consensus sweep analysis.

    Args:
        results: List of evaluation result dicts.
        optima: Output from find_optimal_configs().
        metadata: Analysis metadata dict.

    Returns:
        Markdown-formatted summary string.
    """
    lines = [
        "# Consensus Voting Sweep Analysis",
        "",
        f"**Generated**: {metadata.get('timestamp', 'N/A')}  ",
        f"**Bootstrap iterations**: {metadata.get('n_bootstrap', 'N/A')}  ",
        f"**Random seed**: {metadata.get('random_seed', 'N/A')}  ",
        f"**Baseline F1**: {optima['baseline_f1']:.4f}",
        "",
        "## Key Finding",
        "",
    ]

    global_opt = optima["global_optimum"]
    if optima["beats_baseline"]:
        lines.append(
            f"Consensus voting **improves** over single-run baseline. "
            f"Best configuration: {global_opt['temperature']} "
            f"N={global_opt['pool_size']} "
            f"x={global_opt['threshold']} "
            f"achieves F1={global_opt['f1']:.4f} "
            f"({global_opt['delta_vs_baseline']:+.4f} vs baseline)."
        )
    else:
        lines.append(
            f"Consensus voting does **not** improve over single-run "
            f"baseline (F1={optima['baseline_f1']:.4f}). "
            f"Best consensus F1={global_opt['f1']:.4f} "
            f"({global_opt['delta_vs_baseline']:+.4f})."
        )

    # Per-temperature optima table
    lines.extend([
        "",
        "## Per-Temperature Optima",
        "",
        "| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |",
        "|------|---:|---:|----:|:------:|----:|----:|------:|----:|",
    ])

    temperatures = metadata.get("temperatures", TEMPERATURES)
    for temp in temperatures:
        if temp not in optima["per_temperature_optima"]:
            continue
        opt = optima["per_temperature_optima"][temp]
        ci_str = (
            f"[{opt['f1_ci'][0]:.3f}, {opt['f1_ci'][1]:.3f}]"
        )
        lines.append(
            f"| {temp} | {opt['pool_size']} | {opt['threshold']} "
            f"| {opt['f1']:.4f} | {ci_str} "
            f"| {opt['precision']:.4f} | {opt['recall']:.4f} "
            f"| {opt['n_detections']} "
            f"| {opt['delta_vs_baseline']:+.4f} |"
        )

    # Full sweep table
    lines.extend([
        "",
        "## Full Sweep Results",
        "",
        "| Temp | N | x | F1 | 95% CI | P | R | n_det |",
        "|------|---:|---:|----:|:------:|----:|----:|------:|",
    ])

    df = pd.DataFrame(results)
    df = df.sort_values(
        ["temperature", "pool_size", "threshold"]
    )
    for _, row in df.iterrows():
        ci_str = (
            f"[{row['f1_ci_lo']:.3f}, {row['f1_ci_hi']:.3f}]"
        )
        lines.append(
            f"| {row['temperature']} "
            f"| {int(row['pool_size'])} "
            f"| {int(row['threshold'])} "
            f"| {row['f1']:.4f} | {ci_str} "
            f"| {row['precision']:.4f} "
            f"| {row['recall']:.4f} "
            f"| {int(row['n_detections'])} |"
        )

    lines.extend([
        "",
        "## Methodology",
        "",
        "For each (temperature, pool_size, threshold) combination:",
        "",
        "1. Detection GeoDataFrames are converted to GeoJSON "
        "features",
        "2. Within-run deduplication (20 m tolerance) removes "
        "overlapping-tile duplicates",
        "3. Cross-run clustering (20 m tolerance) groups "
        "detections and counts votes",
        "4. Vote threshold filters clusters by minimum agreement",
        "5. Consensus centroids are spatially joined to tile "
        "boundaries for F1 evaluation",
        (
            "6. Bootstrapped 95% CIs use tile-level resampling "
            f"(K={metadata.get('n_bootstrap', 1000)} iterations)"
        ),
        "",
        "Pool selection follows the first-N convention "
        "(preregistration Section 3.8): N=5 uses runs 1-5, "
        "N=10 uses runs 1-10, etc.",
        "",
    ])

    return "\n".join(lines)


def print_console_summary(
    results: list[dict],
    optima: dict,
) -> None:
    """Print a formatted console summary of the analysis."""
    print("\n" + "=" * 78)
    print(" Consensus Voting Sweep Analysis")
    print("=" * 78)

    baseline = optima["baseline_f1"]
    print(f"\n  Baseline (single-run T=0.0 mean F1): {baseline:.4f}")

    global_opt = optima["global_optimum"]
    if optima["beats_baseline"]:
        print(
            f"  >> Consensus BEATS baseline: "
            f"{global_opt['temperature']} "
            f"N={global_opt['pool_size']} "
            f"x={global_opt['threshold']} "
            f"-> F1={global_opt['f1']:.4f} "
            f"({global_opt['delta_vs_baseline']:+.4f})"
        )
    else:
        print(
            f"  >> Consensus does NOT beat baseline: "
            f"best F1={global_opt['f1']:.4f} "
            f"({global_opt['delta_vs_baseline']:+.4f})"
        )

    # Per-temperature optima
    print("\n" + "-" * 78)
    print(
        " Per-Temperature Optima "
        "(best N, x for each temperature)"
    )
    print("-" * 78)
    print(
        f"  {'Temp':<6} {'N':>3} {'x':>3} {'F1':>7} "
        f"{'95% CI':>18} {'P':>7} {'R':>7} "
        f"{'n_det':>6} {'dF1':>7}"
    )
    print(
        f"  {'-' * 6} {'-' * 3} {'-' * 3} {'-' * 7} "
        f"{'-' * 18} {'-' * 7} {'-' * 7} "
        f"{'-' * 6} {'-' * 7}"
    )

    for temp in sorted(
        optima["per_temperature_optima"].keys()
    ):
        opt = optima["per_temperature_optima"][temp]
        ci_str = (
            f"[{opt['f1_ci'][0]:.3f}, {opt['f1_ci'][1]:.3f}]"
        )
        marker = " *" if opt["f1"] > baseline else ""
        print(
            f"  {temp:<6} {opt['pool_size']:>3} "
            f"{opt['threshold']:>3} "
            f"{opt['f1']:>7.4f} {ci_str:>18} "
            f"{opt['precision']:>7.4f} "
            f"{opt['recall']:>7.4f} "
            f"{opt['n_detections']:>6} "
            f"{opt['delta_vs_baseline']:>+7.4f}{marker}"
        )

    print("\n  * = beats single-run T=0.0 baseline")

    # Full sweep table
    print("\n" + "-" * 78)
    print(" Full Sweep Results")
    print("-" * 78)
    print(
        f"  {'Temp':<6} {'N':>3} {'x':>3} {'F1':>7} "
        f"{'95% CI':>18} {'P':>7} {'R':>7} {'n_det':>6}"
    )
    print(
        f"  {'-' * 6} {'-' * 3} {'-' * 3} {'-' * 7} "
        f"{'-' * 18} {'-' * 7} {'-' * 7} {'-' * 6}"
    )

    df = pd.DataFrame(results)
    df = df.sort_values(
        ["temperature", "pool_size", "threshold"]
    )
    prev_temp = None
    for _, row in df.iterrows():
        # Visual separator between temperatures
        if row["temperature"] != prev_temp:
            if prev_temp is not None:
                print()
            prev_temp = row["temperature"]

        ci_str = (
            f"[{row['f1_ci_lo']:.3f}, {row['f1_ci_hi']:.3f}]"
        )
        print(
            f"  {row['temperature']:<6} "
            f"{int(row['pool_size']):>3} "
            f"{int(row['threshold']):>3} "
            f"{row['f1']:>7.4f} {ci_str:>18} "
            f"{row['precision']:>7.4f} "
            f"{row['recall']:>7.4f} "
            f"{int(row['n_detections']):>6}"
        )

    print("\n" + "=" * 78 + "\n")


def main() -> int:
    """Run the retroactive consensus voting analysis."""
    parser = argparse.ArgumentParser(
        description=(
            "Retroactive consensus voting analysis on Phase 2b "
            "temperature sweep data"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full analysis with default settings
    python scripts/analyse_consensus_sweep.py

    # Quick test with fewer bootstrap iterations
    python scripts/analyse_consensus_sweep.py --bootstrap 100

    # Custom output directory
    python scripts/analyse_consensus_sweep.py \\
        --output-dir results/test
        """,
    )

    parser.add_argument(
        "--study-dir",
        type=Path,
        default=DEFAULT_STUDY_DIR,
        help=(
            "Base directory for Phase 2b results "
            f"(default: {DEFAULT_STUDY_DIR})"
        ),
    )
    parser.add_argument(
        "--ground-truth",
        type=Path,
        default=DEFAULT_GROUND_TRUTH,
        help=(
            "Ground truth GeoJSON "
            f"(default: {DEFAULT_GROUND_TRUTH})"
        ),
    )
    parser.add_argument(
        "--bounds",
        type=Path,
        default=DEFAULT_BOUNDS,
        help=(
            "Tile boundaries GeoJSON "
            f"(default: {DEFAULT_BOUNDS})"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=DEFAULT_N_BOOTSTRAP,
        help=(
            "Number of bootstrap iterations "
            f"(default: {DEFAULT_N_BOOTSTRAP})"
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help=(
            "Random seed for reproducibility "
            f"(default: {RANDOM_SEED})"
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Max parallel workers (default: CPU count - 4)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--temperatures",
        nargs="+",
        default=TEMPERATURES,
        help=(
            "Temperature condition labels to analyse "
            f"(default: {' '.join(TEMPERATURES)}). "
            "Phase 3a: --temperatures T0.3 T0.7"
        ),
    )
    parser.add_argument(
        "--pool-sizes",
        nargs="+",
        type=int,
        default=POOL_SIZES,
        help=(
            "Pool sizes (N values) to evaluate "
            f"(default: {' '.join(str(n) for n in POOL_SIZES)}). "
            "Phase 3a: --pool-sizes 5 10 30"
        ),
    )
    parser.add_argument(
        "--baseline-f1",
        type=float,
        default=None,
        help=(
            "Override baseline F1 for comparison. If not "
            "provided, reads from per_run_metrics.csv or "
            "uses hardcoded fallback. "
            "Phase 3a: --baseline-f1 0.609 (Track 1) "
            "or --baseline-f1 0.660 (Track 2)"
        ),
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.study_dir.exists():
        logger.error(
            "Study directory not found: %s", args.study_dir
        )
        return 1
    if not args.ground_truth.exists():
        logger.error(
            "Ground truth not found: %s", args.ground_truth
        )
        return 1
    if not args.bounds.exists():
        logger.error(
            "Bounds file not found: %s", args.bounds
        )
        return 1

    # Load shared reference data
    logger.info("Loading ground truth and bounds...")
    gdf_ref = gpd.read_file(args.ground_truth)
    gdf_bounds = gpd.read_file(args.bounds)

    # Standardise CRS
    if gdf_ref.crs != TARGET_CRS:
        gdf_ref = gdf_ref.to_crs(TARGET_CRS)
    if gdf_bounds.crs != TARGET_CRS:
        gdf_bounds = gdf_bounds.to_crs(TARGET_CRS)

    logger.info(
        "Loaded %d reference features, %d tiles",
        len(gdf_ref),
        len(gdf_bounds),
    )

    # Step 1: Precompute clusters for all (T, N) combinations
    logger.info("Precomputing clusters...")
    all_clusters = precompute_clusters(
        args.study_dir, args.temperatures, args.pool_sizes
    )

    if not all_clusters:
        logger.error(
            "No clusters computed — check data paths"
        )
        return 1

    # Step 2: Build evaluation tasks
    tasks = []
    for (temp, pool_size), clusters in all_clusters.items():
        for x in range(1, pool_size + 1):
            tasks.append((temp, pool_size, x, clusters))

    logger.info(
        "Evaluating %d (T, N, x) configurations with %d "
        "bootstrap iterations each...",
        len(tasks),
        args.bootstrap,
    )

    # Step 3: Parallelised evaluation
    cpu_count = os.cpu_count() or 4
    max_workers = args.workers or max(1, cpu_count - 4)
    results: list[dict] = []

    with ProcessPoolExecutor(
        max_workers=max_workers
    ) as executor:
        futures = {}
        for temp, pool_size, x, clusters in tasks:
            future = executor.submit(
                evaluate_single_config,
                temp,
                pool_size,
                x,
                clusters,
                gdf_ref,
                gdf_bounds,
                args.bootstrap,
                args.seed,
            )
            futures[future] = (temp, pool_size, x)

        for future in as_completed(futures):
            key = futures[future]
            try:
                result = future.result()
                results.append(result)
                logger.info(
                    "  %s N=%d x=%d: F1=%.4f (%d det)",
                    result["temperature"],
                    result["pool_size"],
                    result["threshold"],
                    result["f1"],
                    result["n_detections"],
                )
            except Exception as e:
                logger.error(
                    "Error evaluating %s: %s", key, e
                )

    if not results:
        logger.error("No evaluation results produced")
        return 1

    # Sort results for consistent output
    results.sort(
        key=lambda r: (
            r["temperature"],
            r["pool_size"],
            r["threshold"],
        )
    )

    # Step 4: Compute baseline and find optima
    # Baseline: CLI override > per_run_metrics.csv > hardcoded fallback
    if args.baseline_f1 is not None:
        baseline_f1 = args.baseline_f1
        logger.info(
            "Baseline F1 (CLI override): %.4f", baseline_f1
        )
    else:
        baseline_csv = (
            args.study_dir / "per_run_metrics.csv"
        )
        if baseline_csv.exists():
            df_baseline = pd.read_csv(baseline_csv)
            t0_runs = df_baseline[
                df_baseline["condition"] == "T0.0"
            ]
            baseline_f1 = float(t0_runs["f1"].mean())
            logger.info(
                "Baseline T=0.0 mean F1: %.4f", baseline_f1
            )
        else:
            # Fallback: known value from Phase 2b analysis
            baseline_f1 = 0.5574
            logger.warning(
                "Baseline CSV not found, using known "
                "value: %.4f",
                baseline_f1,
            )

    optima = find_optimal_configs(results, baseline_f1)

    # Step 5: Write outputs
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # CSV output
    df_results = pd.DataFrame(results)
    csv_path = args.output_dir / "consensus-sweep-results.csv"
    df_results.to_csv(csv_path, index=False)
    logger.info("Saved CSV: %s", csv_path)

    # JSON report with full metadata
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "study_dir": str(args.study_dir),
        "ground_truth": str(args.ground_truth),
        "bounds": str(args.bounds),
        "n_bootstrap": args.bootstrap,
        "random_seed": args.seed,
        "pool_selection": (
            "first-N (preregistration Section 3.8)"
        ),
        "temperatures": args.temperatures,
        "pool_sizes": args.pool_sizes,
        "n_configurations": len(results),
        "max_workers": max_workers,
    }

    report = {
        "metadata": metadata,
        "optima": optima,
        "results": results,
    }

    json_path = (
        args.output_dir / "consensus-analysis-report.json"
    )
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
    logger.info("Saved JSON: %s", json_path)

    # Markdown summary
    md_content = generate_summary_md(
        results, optima, metadata
    )
    md_path = (
        args.output_dir / "consensus-analysis-summary.md"
    )
    with open(md_path, "w") as f:
        f.write(md_content)
    logger.info("Saved Markdown: %s", md_path)

    # Console output
    if not args.quiet:
        print_console_summary(results, optima)

    return 0


if __name__ == "__main__":
    sys.exit(main())
