#!/usr/bin/env python3
"""
Phase 3c Diversity Analysis
============================

Analyses whether introducing diversity across consensus voting passes
(text, image, temperature, or combined) improves detection accuracy
compared to identical passes (H9).

Implements the consensus_diversity analysis method specified in the
Phase 3c study YAMLs (Yet Another Markup Language). For each condition,
groups sub-conditions into replications using the preregistered rule:

    Replication k = {run_k from sub-condition p1, run_k from p2, ..., run_k from p5}

Then applies consensus voting with a configurable threshold sweep and
evaluates F1 against ground truth. Conditions are compared using paired
permutation tests on tile-level F1 scores (preregistration Section 3.5).

Supports both tracks:
    Track 1 (image): 5 conditions (A, B, C, D, E), 5 passes, 5 replications
    Track 2 (text-only): 4 conditions (A, B, D, E), C omitted as degenerate

Usage:
    # Track 2 (text-only)
    python scripts/analyse_diversity.py \\
        --study-yaml studies/phase3c-h9-diversity-track2.yaml \\
        --output-dir results/phase3c-diversity/track2-text

    # Track 1 (image)
    python scripts/analyse_diversity.py \\
        --study-yaml studies/phase3c-h9-diversity-track1.yaml \\
        --output-dir results/phase3c-diversity/track1-image

    # Quick test with fewer bootstrap iterations
    python scripts/analyse_diversity.py \\
        --study-yaml studies/phase3c-h9-diversity-track2.yaml \\
        --output-dir results/phase3c-diversity/track2-text \\
        --bootstrap 100

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml
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
__version__ = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_N_BOOTSTRAP = 1000
RANDOM_SEED = 42
TARGET_CRS = "EPSG:32635"
DEFAULT_BUFFER_METRES = 20
N_PERMUTATIONS = 10000

# Default paths (relative to repository root)
DEFAULT_GROUND_TRUTH = Path(
    "inputs/vectors/references/mounds-reference.geojson"
)
DEFAULT_BOUNDS = Path(
    "inputs/vectors/bounds/validation_bounds.geojson"
)


# ── Data loading ──────────────────────────────────────────────────


def load_study_yaml(yaml_path: Path) -> dict:
    """
    Load and parse a Phase 3c study YAML file.

    Args:
        yaml_path: Path to the study YAML file.

    Returns:
        Parsed YAML as a dict.
    """
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def extract_consensus_design(study: dict) -> dict[str, list[str]]:
    """
    Extract condition → sub-condition mapping from consensus_design.

    Args:
        study: Parsed study YAML dict.

    Returns:
        Dict mapping condition label (e.g., 'A') to list of
        sub-condition names (e.g., ['h9-A-p1', ..., 'h9-A-p5']).
    """
    design = study.get("consensus_design", {})
    conditions = design.get("conditions", {})
    result = {}
    for label, info in conditions.items():
        result[label] = info["sub_conditions"]
    return result


def load_replication_passes(
    study_dir: Path,
    sub_conditions: list[str],
    replication_k: int,
) -> dict[str, list[dict]]:
    """
    Load detections for one replication of one condition.

    Replication k uses run_k from each sub-condition. The result is a
    dict mapping sub-condition name → list of deduplicated GeoJSON
    features, suitable for ``cluster_across_passes()``.

    Args:
        study_dir: Base output directory (e.g., outputs/phase3c/track2-text).
        sub_conditions: List of sub-condition directory names.
        replication_k: Replication index (1-based: run_1, run_2, ...).

    Returns:
        Dict mapping sub-condition name → deduplicated feature list.
        Missing or empty runs are logged and excluded.
    """
    pass_detections: dict[str, list[dict]] = {}

    for sub_cond in sub_conditions:
        # Use load_condition_results to get all runs, then pick run_k
        all_runs = load_condition_results(study_dir, sub_cond)

        # Find the specific run number
        target_gdf = None
        for run_num, gdf in all_runs:
            if run_num == replication_k:
                target_gdf = gdf
                break

        if target_gdf is None:
            logger.warning(
                "Missing run_%d for %s — excluding from "
                "replication %d",
                replication_k, sub_cond, replication_k,
            )
            continue

        # Standardise CRS (Coordinate Reference System)
        if target_gdf.crs != TARGET_CRS:
            target_gdf = target_gdf.to_crs(TARGET_CRS)

        # Convert to GeoJSON features and deduplicate within pass
        features = gdf_to_features(target_gdf)
        deduped = deduplicate_within_pass(features)
        pass_detections[sub_cond] = deduped

    return pass_detections


def gdf_to_features(gdf: gpd.GeoDataFrame) -> list[dict]:
    """
    Convert GeoDataFrame rows to GeoJSON feature dicts.

    Produces the format expected by merge_passes functions: each dict
    has 'geometry' (GeoJSON geometry dict) and 'properties' (dict with
    'source_tile' and 'subtype' keys).

    Args:
        gdf: GeoDataFrame with geometry column and source_tile,
            subtype attributes.

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
    with 'source_tiles' (plural) in properties. For F1 evaluation, each
    detection needs a single 'source_tile' assigned via spatial join
    against tile boundaries.

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

    points = [shape(f["geometry"]) for f in features]
    props_list = [f.get("properties", {}) for f in features]
    gdf = gpd.GeoDataFrame(
        props_list, geometry=points, crs=TARGET_CRS,
    )

    # Assign source_tile via spatial join against tile boundaries
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

    return gdf_joined[
        ["source_tile", "subtype", "geometry"]
    ].copy()


# ── Core analysis ─────────────────────────────────────────────────


def evaluate_condition_replication(
    condition_label: str,
    replication_k: int,
    study_dir: Path,
    sub_conditions: list[str],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    thresholds: list[int],
    n_bootstrap: int,
    random_seed: int,
    buffer_metres: int = DEFAULT_BUFFER_METRES,
) -> list[dict]:
    """
    Evaluate one condition × one replication across all thresholds.

    Loads detections for the replication, clusters across passes,
    then evaluates at each vote threshold.

    Args:
        condition_label: Condition identifier (e.g., 'A', 'B').
        replication_k: Replication index (1-based).
        study_dir: Base output directory.
        sub_conditions: Sub-condition names for this condition.
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Tile boundary GeoDataFrame.
        thresholds: Vote thresholds to evaluate (e.g., [1, 2, 3, 4, 5]).
        n_bootstrap: Number of bootstrap iterations for CIs.
        random_seed: Random seed for reproducibility.
        buffer_metres: Spatial matching tolerance in metres.

    Returns:
        List of result dicts, one per threshold.
    """
    # Load and cluster detections for this replication
    pass_detections = load_replication_passes(
        study_dir, sub_conditions, replication_k,
    )

    n_passes_loaded = len(pass_detections)
    if n_passes_loaded == 0:
        logger.warning(
            "No passes loaded for %s rep %d",
            condition_label, replication_k,
        )
        return []

    clusters = cluster_across_passes(pass_detections)
    total_passes = len(sub_conditions)

    results = []
    for x in thresholds:
        consensus_fc = apply_threshold(clusters, x, total_passes)
        gdf_consensus = consensus_to_gdf(consensus_fc, gdf_bounds)
        n_detections = len(gdf_consensus)

        if n_detections == 0:
            results.append({
                "condition": condition_label,
                "replication": replication_k,
                "threshold": x,
                "n_passes": n_passes_loaded,
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
            })
            continue

        # Point estimates
        precision, recall, f1 = calculate_f1_internal(
            gdf_consensus, gdf_ref, gdf_bounds,
            buffer_metres=buffer_metres,
        )

        # Bootstrapped 95% confidence intervals
        ci = bootstrap_ci(
            gdf_consensus, gdf_ref, gdf_bounds,
            n_iterations=n_bootstrap,
            random_seed=random_seed,
            buffer_metres=buffer_metres,
        )

        results.append({
            "condition": condition_label,
            "replication": replication_k,
            "threshold": x,
            "n_passes": n_passes_loaded,
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
        })

    return results


# ── Statistical comparison ────────────────────────────────────────


def paired_permutation_test(
    scores_a: list[float],
    scores_b: list[float],
    n_permutations: int = N_PERMUTATIONS,
    random_seed: int = RANDOM_SEED,
) -> dict:
    """
    Two-sided paired permutation test for mean difference.

    Tests whether the mean of scores_b differs significantly from
    scores_a by randomly permuting the sign of the differences.

    Args:
        scores_a: Baseline condition scores (one per replication).
        scores_b: Test condition scores (one per replication).
        n_permutations: Number of random permutations.
        random_seed: Random seed for reproducibility.

    Returns:
        Dict with observed_diff, p_value, and n_permutations.
    """
    scores_a = np.array(scores_a)
    scores_b = np.array(scores_b)
    diffs = scores_b - scores_a
    observed_diff = float(np.mean(diffs))

    rng = np.random.default_rng(random_seed)
    n_extreme = 0

    for _ in range(n_permutations):
        # Randomly flip signs of differences
        signs = rng.choice([-1, 1], size=len(diffs))
        perm_diff = float(np.mean(diffs * signs))
        if abs(perm_diff) >= abs(observed_diff):
            n_extreme += 1

    p_value = (n_extreme + 1) / (n_permutations + 1)

    return {
        "observed_diff": round(observed_diff, 4),
        "p_value": round(p_value, 4),
        "n_permutations": n_permutations,
    }


# ── Output generation ─────────────────────────────────────────────


def find_optimal_threshold(
    results_df: pd.DataFrame,
    condition: str,
) -> dict:
    """
    Find the threshold that maximises mean F1 across replications.

    Args:
        results_df: DataFrame with condition, replication, threshold, f1.
        condition: Condition label to filter.

    Returns:
        Dict with optimal threshold and associated metrics.
    """
    cond_df = results_df[results_df["condition"] == condition]

    # Mean F1 across replications for each threshold
    mean_by_threshold = cond_df.groupby("threshold").agg(
        f1_mean=("f1", "mean"),
        f1_std=("f1", "std"),
        precision_mean=("precision", "mean"),
        recall_mean=("recall", "mean"),
        n_detections_mean=("n_detections", "mean"),
    ).reset_index()

    best_row = mean_by_threshold.loc[
        mean_by_threshold["f1_mean"].idxmax()
    ]

    return {
        "threshold": int(best_row["threshold"]),
        "f1_mean": round(float(best_row["f1_mean"]), 4),
        "f1_std": round(float(best_row["f1_std"]), 4),
        "precision_mean": round(
            float(best_row["precision_mean"]), 4,
        ),
        "recall_mean": round(
            float(best_row["recall_mean"]), 4,
        ),
        "n_detections_mean": round(
            float(best_row["n_detections_mean"]), 1,
        ),
    }


def generate_summary_md(
    results_df: pd.DataFrame,
    condition_optima: dict,
    comparisons: dict,
    metadata: dict,
    consensus_design: dict,
) -> str:
    """
    Generate a Markdown summary of the diversity analysis.

    Args:
        results_df: Full results DataFrame.
        condition_optima: Per-condition optimal threshold info.
        comparisons: Pairwise comparison results vs baseline.
        metadata: Analysis metadata dict.
        consensus_design: Condition → sub-condition mapping.

    Returns:
        Markdown-formatted summary string.
    """
    lines = [
        "# Phase 3c Diversity Analysis",
        "",
        f"**Generated**: {metadata.get('timestamp', 'N/A')}  ",
        f"**Track**: {metadata.get('track', 'N/A')}  ",
        f"**Bootstrap iterations**: "
        f"{metadata.get('n_bootstrap', 'N/A')}  ",
        f"**Buffer (spatial tolerance)**: "
        f"{metadata.get('buffer_metres', 20)} m  ",
        f"**Permutation test iterations**: "
        f"{metadata.get('n_permutations', N_PERMUTATIONS)}",
        "",
        "## Experimental Design",
        "",
        "| Condition | Diversity | Sub-conditions |",
        "|-----------|-----------|----------------|",
    ]

    study_conditions = metadata.get(
        "study_conditions", {},
    )
    for label in sorted(consensus_design.keys()):
        dims = study_conditions.get(label, {}).get(
            "diversity_dimensions", [],
        )
        dim_str = ", ".join(dims) if dims else "none (baseline)"
        subs = consensus_design[label]
        lines.append(
            f"| {label} | {dim_str} | "
            f"{', '.join(subs)} |"
        )

    # Per-condition optimal results
    lines.extend([
        "",
        "## Per-Condition Optima",
        "",
        "Best threshold (maximising mean F1 across replications):",
        "",
        "| Condition | x* | F1 | ±SD | P | R | n_det |",
        "|-----------|---:|----:|----:|---:|---:|------:|",
    ])

    for label in sorted(condition_optima.keys()):
        opt = condition_optima[label]
        lines.append(
            f"| {label} | {opt['threshold']} "
            f"| {opt['f1_mean']:.4f} "
            f"| {opt['f1_std']:.4f} "
            f"| {opt['precision_mean']:.4f} "
            f"| {opt['recall_mean']:.4f} "
            f"| {opt['n_detections_mean']:.0f} |"
        )

    # Pairwise comparisons vs baseline (A)
    lines.extend([
        "",
        "## Comparisons vs Baseline (A)",
        "",
        "Paired permutation test on per-replication F1 scores "
        "(at each condition's optimal threshold):",
        "",
        "| Comparison | ΔF1 | p-value | Significant? |",
        "|------------|----:|--------:|:------------:|",
    ])

    for comp_label in sorted(comparisons.keys()):
        comp = comparisons[comp_label]
        sig = "Yes" if comp["p_value"] < 0.05 else "No"
        lines.append(
            f"| {comp_label} vs A "
            f"| {comp['observed_diff']:+.4f} "
            f"| {comp['p_value']:.4f} "
            f"| {sig} |"
        )

    # Per-replication detail table
    lines.extend([
        "",
        "## Per-Replication F1 (at optimal threshold)",
        "",
    ])

    # Build a pivot table: replications × conditions
    opt_thresholds = {
        label: opt["threshold"]
        for label, opt in condition_optima.items()
    }

    header_labels = sorted(condition_optima.keys())
    lines.append(
        "| Rep | "
        + " | ".join(
            f"{lbl} (x={opt_thresholds[lbl]})"
            for lbl in header_labels
        )
        + " |"
    )
    lines.append(
        "|----:|"
        + "|".join(["-----:" for _ in header_labels])
        + "|"
    )

    # Get replications
    reps = sorted(results_df["replication"].unique())
    for rep in reps:
        row_vals = []
        for label in header_labels:
            opt_x = opt_thresholds[label]
            mask = (
                (results_df["condition"] == label)
                & (results_df["replication"] == rep)
                & (results_df["threshold"] == opt_x)
            )
            matching = results_df[mask]
            if len(matching) > 0:
                row_vals.append(
                    f"{matching.iloc[0]['f1']:.4f}"
                )
            else:
                row_vals.append("—")
        lines.append(
            f"| {rep} | " + " | ".join(row_vals) + " |"
        )

    # Key finding
    lines.extend([
        "",
        "## Key Finding",
        "",
    ])

    any_significant = any(
        comp["p_value"] < 0.05
        for comp in comparisons.values()
    )

    baseline_f1 = condition_optima.get("A", {}).get(
        "f1_mean", 0.0,
    )

    if any_significant:
        best_label = max(
            comparisons.keys(),
            key=lambda k: comparisons[k]["observed_diff"],
        )
        best_comp = comparisons[best_label]
        lines.append(
            f"Diversity **significantly improves** consensus F1. "
            f"Condition {best_label} achieves "
            f"ΔF1={best_comp['observed_diff']:+.4f} vs baseline "
            f"(p={best_comp['p_value']:.4f})."
        )
    else:
        lines.append(
            f"No diversity condition significantly outperforms "
            f"the identical-pass baseline (A, "
            f"F1={baseline_f1:.4f}). "
            f"Diversity does not improve consensus voting for "
            f"this track."
        )

    lines.extend([
        "",
        "## Methodology",
        "",
        "1. For each condition, form replications by taking "
        "run_k from each sub-condition",
        "2. Within each pass: deduplicate detections (20 m)",
        "3. Across passes: cluster and count votes (20 m)",
        "4. Apply vote threshold sweep (x=1 to x=5)",
        (
            f"5. Evaluate F1 against ground truth "
            f"({metadata.get('buffer_metres', 20)} m tolerance)"
        ),
        "6. Select optimal threshold per condition "
        "(maximising mean F1 across replications)",
        "7. Compare conditions using paired permutation test "
        f"({metadata.get('n_permutations', N_PERMUTATIONS)} "
        "permutations, two-sided, α=0.05)",
        "",
    ])

    return "\n".join(lines)


def print_console_summary(
    condition_optima: dict,
    comparisons: dict,
) -> None:
    """Print a formatted console summary of the diversity analysis."""
    print("\n" + "=" * 70)
    print(" Phase 3c Diversity Analysis")
    print("=" * 70)

    # Per-condition optima
    print("\n  Per-Condition Optima (best threshold):")
    print(
        f"  {'Cond':<6} {'x*':>3} {'F1':>7} {'±SD':>7} "
        f"{'P':>7} {'R':>7} {'n_det':>6}"
    )
    print(f"  {'-' * 50}")

    for label in sorted(condition_optima.keys()):
        opt = condition_optima[label]
        print(
            f"  {label:<6} {opt['threshold']:>3} "
            f"{opt['f1_mean']:>7.4f} "
            f"{opt['f1_std']:>7.4f} "
            f"{opt['precision_mean']:>7.4f} "
            f"{opt['recall_mean']:>7.4f} "
            f"{opt['n_detections_mean']:>6.0f}"
        )

    # Comparisons vs baseline
    print(f"\n  {'─' * 50}")
    print("  Comparisons vs Baseline (A):")
    print(f"  {'Comp':<10} {'ΔF1':>8} {'p-value':>9} {'Sig?':>6}")
    print(f"  {'-' * 38}")

    for comp_label in sorted(comparisons.keys()):
        comp = comparisons[comp_label]
        sig = "***" if comp["p_value"] < 0.01 else (
            "**" if comp["p_value"] < 0.05 else ""
        )
        print(
            f"  {comp_label + ' vs A':<10} "
            f"{comp['observed_diff']:>+8.4f} "
            f"{comp['p_value']:>9.4f} "
            f"{sig:>6}"
        )

    print("\n" + "=" * 70 + "\n")


# ── Main ──────────────────────────────────────────────────────────


def main() -> int:
    """Run the Phase 3c diversity analysis."""
    parser = argparse.ArgumentParser(
        description=(
            "Phase 3c diversity analysis: compare consensus F1 "
            "across diversity conditions"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Track 2 (text-only)
    python scripts/analyse_diversity.py \\
        --study-yaml studies/phase3c-h9-diversity-track2.yaml \\
        --output-dir results/phase3c-diversity/track2-text

    # Track 1 (image)
    python scripts/analyse_diversity.py \\
        --study-yaml studies/phase3c-h9-diversity-track1.yaml \\
        --output-dir results/phase3c-diversity/track1-image

    # Quick test with reduced bootstrap
    python scripts/analyse_diversity.py \\
        --study-yaml studies/phase3c-h9-diversity-track2.yaml \\
        --output-dir results/phase3c-diversity/track2-text \\
        --bootstrap 100
        """,
    )

    parser.add_argument(
        "--study-yaml",
        type=Path,
        required=True,
        help="Path to Phase 3c study YAML file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory for analysis results",
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
        "--bootstrap",
        type=int,
        default=DEFAULT_N_BOOTSTRAP,
        help=(
            "Number of bootstrap iterations for CIs "
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
        "--buffer-metres",
        type=int,
        default=DEFAULT_BUFFER_METRES,
        help=(
            "Spatial matching tolerance in metres for F1 "
            f"(default: {DEFAULT_BUFFER_METRES})"
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

    args = parser.parse_args()

    # ── Load study YAML and extract design ────────────────────
    study = load_study_yaml(args.study_yaml)
    study_info = study.get("study", {})
    execution = study.get("execution", {})
    n_replications = execution.get("runs", 5)
    study_dir = Path(execution.get("output_dir", ""))

    if not study_dir.exists():
        logger.error(
            "Output directory not found: %s", study_dir,
        )
        return 1

    consensus_design = extract_consensus_design(study)
    condition_labels = sorted(consensus_design.keys())

    # Track name for reporting
    track_name = study_info.get("name", "Unknown")

    logger.info("Study: %s", track_name)
    logger.info(
        "Conditions: %s", ", ".join(condition_labels),
    )
    logger.info("Replications: %d", n_replications)

    # ── Load reference data ───────────────────────────────────
    if not args.ground_truth.exists():
        logger.error(
            "Ground truth not found: %s", args.ground_truth,
        )
        return 1
    if not args.bounds.exists():
        logger.error(
            "Bounds file not found: %s", args.bounds,
        )
        return 1

    logger.info("Loading ground truth and bounds...")
    gdf_ref = gpd.read_file(args.ground_truth)
    gdf_bounds = gpd.read_file(args.bounds)

    if gdf_ref.crs != TARGET_CRS:
        gdf_ref = gdf_ref.to_crs(TARGET_CRS)
    if gdf_bounds.crs != TARGET_CRS:
        gdf_bounds = gdf_bounds.to_crs(TARGET_CRS)

    logger.info(
        "Loaded %d reference features, %d tiles",
        len(gdf_ref), len(gdf_bounds),
    )

    # ── Evaluate all conditions × replications × thresholds ──
    n_passes = 5  # Fixed by design
    thresholds = list(range(1, n_passes + 1))

    # Build task list for parallel evaluation
    tasks = []
    for label in condition_labels:
        sub_conds = consensus_design[label]
        for rep_k in range(1, n_replications + 1):
            tasks.append((label, rep_k, sub_conds))

    total_evals = len(tasks) * len(thresholds)
    logger.info(
        "Evaluating %d condition×replication combos "
        "(%d total threshold evaluations, %d bootstrap each)",
        len(tasks), total_evals, args.bootstrap,
    )

    # Parallel evaluation
    cpu_count = os.cpu_count() or 4
    max_workers = args.workers or max(1, cpu_count - 4)
    all_results: list[dict] = []

    with ProcessPoolExecutor(
        max_workers=max_workers,
    ) as executor:
        futures = {}
        for label, rep_k, sub_conds in tasks:
            future = executor.submit(
                evaluate_condition_replication,
                label, rep_k, study_dir, sub_conds,
                gdf_ref, gdf_bounds, thresholds,
                args.bootstrap, args.seed,
                args.buffer_metres,
            )
            futures[future] = (label, rep_k)

        for future in as_completed(futures):
            key = futures[future]
            try:
                rep_results = future.result()
                all_results.extend(rep_results)
                # Log the best threshold for this replication
                if rep_results:
                    best = max(
                        rep_results, key=lambda r: r["f1"],
                    )
                    logger.info(
                        "  %s rep %d: best F1=%.4f (x=%d, "
                        "%d det)",
                        key[0], key[1], best["f1"],
                        best["threshold"],
                        best["n_detections"],
                    )
            except Exception as e:
                logger.error(
                    "Error evaluating %s: %s", key, e,
                )

    if not all_results:
        logger.error("No evaluation results produced")
        return 1

    # ── Analyse results ───────────────────────────────────────
    results_df = pd.DataFrame(all_results)

    # Find optimal threshold per condition
    condition_optima = {}
    for label in condition_labels:
        condition_optima[label] = find_optimal_threshold(
            results_df, label,
        )

    # Pairwise comparisons vs baseline (A) using paired
    # permutation test at each condition's optimal threshold
    comparisons = {}
    baseline_opt_x = condition_optima["A"]["threshold"]

    # Get baseline (A) F1 per replication at A's optimal threshold
    baseline_f1s = []
    for rep_k in range(1, n_replications + 1):
        mask = (
            (results_df["condition"] == "A")
            & (results_df["replication"] == rep_k)
            & (results_df["threshold"] == baseline_opt_x)
        )
        matching = results_df[mask]
        if len(matching) > 0:
            baseline_f1s.append(matching.iloc[0]["f1"])

    for label in condition_labels:
        if label == "A":
            continue

        test_opt_x = condition_optima[label]["threshold"]

        # Get test condition F1 per replication at its optimal x
        test_f1s = []
        for rep_k in range(1, n_replications + 1):
            mask = (
                (results_df["condition"] == label)
                & (results_df["replication"] == rep_k)
                & (results_df["threshold"] == test_opt_x)
            )
            matching = results_df[mask]
            if len(matching) > 0:
                test_f1s.append(matching.iloc[0]["f1"])

        if len(baseline_f1s) == len(test_f1s) and len(test_f1s) > 0:
            comparisons[label] = paired_permutation_test(
                baseline_f1s, test_f1s,
                n_permutations=N_PERMUTATIONS,
                random_seed=args.seed,
            )
        else:
            logger.warning(
                "Cannot compare %s vs A: mismatched "
                "replication counts (%d vs %d)",
                label, len(test_f1s), len(baseline_f1s),
            )

    # ── Write outputs ─────────────────────────────────────────
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # CSV of all results
    csv_path = args.output_dir / "diversity-sweep-results.csv"
    results_df.to_csv(csv_path, index=False)
    logger.info("Saved CSV: %s", csv_path)

    # Metadata for report
    study_conditions_meta = {}
    design_section = study.get("consensus_design", {}).get(
        "conditions", {},
    )
    for label, info in design_section.items():
        study_conditions_meta[label] = {
            "sub_conditions": info.get("sub_conditions", []),
            "diversity_dimensions": info.get(
                "diversity_dimensions", [],
            ),
        }

    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "study_yaml": str(args.study_yaml),
        "study_dir": str(study_dir),
        "track": track_name,
        "ground_truth": str(args.ground_truth),
        "bounds": str(args.bounds),
        "n_bootstrap": args.bootstrap,
        "random_seed": args.seed,
        "buffer_metres": args.buffer_metres,
        "n_permutations": N_PERMUTATIONS,
        "conditions": condition_labels,
        "n_replications": n_replications,
        "n_passes": n_passes,
        "thresholds": thresholds,
        "max_workers": max_workers,
        "study_conditions": study_conditions_meta,
    }

    # JSON report
    report = {
        "metadata": metadata,
        "condition_optima": condition_optima,
        "comparisons": comparisons,
        "results": all_results,
    }

    json_path = (
        args.output_dir / "diversity-analysis-report.json"
    )
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
    logger.info("Saved JSON: %s", json_path)

    # Markdown summary
    md_content = generate_summary_md(
        results_df, condition_optima, comparisons,
        metadata, consensus_design,
    )
    md_path = (
        args.output_dir / "diversity-analysis-summary.md"
    )
    with open(md_path, "w") as f:
        f.write(md_content)
    logger.info("Saved Markdown: %s", md_path)

    # Console output
    if not args.quiet:
        print_console_summary(condition_optima, comparisons)

    return 0


if __name__ == "__main__":
    sys.exit(main())
