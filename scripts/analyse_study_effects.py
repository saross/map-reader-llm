#!/usr/bin/env python3
"""
Study Effect Size Analysis with Bootstrapped Confidence Intervals (CIs)
=======================================================================

Computes bootstrapped 95% CIs for effect sizes (differences) between
experimental conditions, as specified in preregistration Sections 3.5 and 4.2:

Symbol-level (Section 3.5):
    "Report effect sizes (F1 difference, precision difference, recall
    difference) with 95% bootstrapped CIs"

Tile-level (Section 4.2):
    Matthews Correlation Coefficient (MCC), sensitivity, and specificity
    differences for binary tile classification (empty vs populated tiles)

Usage:
    # Compare two specific conditions
    python scripts/analyse_study_effects.py outputs/study \\
        --condition-a image-only_canonical-first_baseline_T1.0 \\
        --condition-b text-image_canonical-first_baseline_T1.0

    # Run all pairwise comparisons for a factor
    python scripts/analyse_study_effects.py outputs/study \\
        --factor modality

    # Export results to JavaScript Object Notation (JSON)
    python scripts/analyse_study_effects.py outputs/study \\
        --condition-a A --condition-b B --output results.json

Inputs:
    - Study output directory containing detection GeoJSON files
    - Tile bounds GeoJSON files
    - Reference ground truth (from inputs/vectors/)

Outputs:
    - Console summary of effect sizes with 95% CIs
    - Optional JSON export of all comparisons

Author: Claude Code
Version: 1.0.0
Licence: Apache 2.0
"""

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import pandas as pd

from scripts.lib_advanced_metrics import (
    bootstrap_effect_size_ci,
    bootstrap_tile_effect_size_ci,
    print_effect_size_summary,
    print_tile_effect_size_summary,
)

__version__ = "1.0.0"

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Target Coordinate Reference System (CRS): UTM Zone 35N (Bulgaria)
TARGET_CRS = "EPSG:32635"


def _ensure_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Ensure a GeoDataFrame uses the project target CRS.

    Sets the CRS if missing, or reprojects if it differs from TARGET_CRS.

    Args:
        gdf: GeoDataFrame to normalise.

    Returns:
        GeoDataFrame in the target CRS.
    """
    if gdf.crs == TARGET_CRS:
        return gdf
    if gdf.crs is None:
        gdf.set_crs(TARGET_CRS, inplace=True)
        return gdf
    return gdf.to_crs(TARGET_CRS)


def find_condition_files(study_dir: Path, condition_id: str) -> tuple[Path, Path]:
    """
    Locate detection and bounds files for a condition.

    Searches for files matching known naming patterns within the study
    output directory.

    Args:
        study_dir: Path to study output directory.
        condition_id: Condition identifier string.

    Returns:
        Tuple of (detection_path, bounds_path).

    Raises:
        FileNotFoundError: If detection or bounds files cannot be located.
    """
    # Standard naming patterns
    det_patterns = [
        f"{condition_id}_detections.geojson",
        f"{condition_id}_consensus_detections.geojson",
        f"detections_{condition_id}.geojson",
    ]

    bounds_patterns = [
        f"{condition_id}_bounds.geojson",
        f"{condition_id}_tile_bounds.geojson",
        f"bounds_{condition_id}.geojson",
    ]

    def _first_match(patterns: list[str], label: str) -> Path:
        """Return the first existing file matching a pattern, or raise."""
        for pattern in patterns:
            candidate = study_dir / pattern
            if candidate.exists():
                return candidate
        raise FileNotFoundError(
            f"{label} file not found for condition "
            f"'{condition_id}' in {study_dir}"
        )

    det_path = _first_match(det_patterns, "Detection")
    bounds_path = _first_match(bounds_patterns, "Bounds")

    return det_path, bounds_path


def load_condition_data(
    study_dir: Path,
    condition_id: str,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Load detection and bounds GeoDataFrames for a condition.

    Args:
        study_dir: Path to study output directory.
        condition_id: Condition identifier string.

    Returns:
        Tuple of (gdf_det, gdf_bounds), both in TARGET_CRS.
    """
    det_path, bounds_path = find_condition_files(study_dir, condition_id)

    gdf_det = _ensure_crs(gpd.read_file(det_path))
    gdf_bounds = _ensure_crs(gpd.read_file(bounds_path))

    return gdf_det, gdf_bounds


def load_reference_data(inputs_dir: Path | None = None) -> gpd.GeoDataFrame:
    """
    Load ground truth reference data.

    Args:
        inputs_dir: Path to inputs directory (default: PROJECT_ROOT/inputs).

    Returns:
        GeoDataFrame of reference points in TARGET_CRS.

    Raises:
        FileNotFoundError: If no reference vectors exist.
    """
    if inputs_dir is None:
        inputs_dir = PROJECT_ROOT / "inputs"

    ref_dir = inputs_dir / "vectors" / "references"
    ref_files = list(ref_dir.glob("reference_*.geojson"))

    ref_gdfs = []
    for rf in ref_files:
        gdf = gpd.read_file(rf)
        gdf["Map"] = rf.stem.replace("reference_", "")
        ref_gdfs.append(gdf)

    if not ref_gdfs:
        raise FileNotFoundError(f"No reference vectors found in {ref_dir}")

    gdf_ref = pd.concat(ref_gdfs, ignore_index=True)
    return _ensure_crs(gdf_ref)


def compare_conditions(
    study_dir: Path,
    condition_a: str,
    condition_b: str,
    n_iterations: int = 1000,
    random_seed: int | None = None,
    verbose: bool = True,
) -> dict:
    """
    Compare two conditions using bootstrapped effect size CIs.

    Computes both symbol-level (F1, precision, recall) and tile-level
    (MCC, sensitivity, specificity) effect sizes as per preregistration
    Sections 3.5 and 4.2.

    Args:
        study_dir: Path to study output directory.
        condition_a: First condition identifier.
        condition_b: Second condition identifier.
        n_iterations: Bootstrap iterations (default 1000).
        random_seed: Optional seed for reproducibility.
        verbose: Print summary to console.

    Returns:
        Dict with 'symbol_level' and 'tile_level' effect size results.
    """
    gdf_det_a, gdf_bounds_a = load_condition_data(study_dir, condition_a)
    gdf_det_b, gdf_bounds_b = load_condition_data(study_dir, condition_b)
    gdf_ref = load_reference_data()

    # Symbol-level bootstrapped effect sizes (F1, precision, recall)
    symbol_effects = bootstrap_effect_size_ci(
        gdf_det_a,
        gdf_bounds_a,
        gdf_det_b,
        gdf_bounds_b,
        gdf_ref,
        n_iterations=n_iterations,
        random_seed=random_seed,
    )

    # Tile-level bootstrapped effect sizes (MCC, sensitivity, specificity)
    tile_effects = bootstrap_tile_effect_size_ci(
        gdf_det_a,
        gdf_bounds_a,
        gdf_det_b,
        gdf_bounds_b,
        gdf_ref,
        n_iterations=n_iterations,
        random_seed=random_seed,
    )

    results = {
        "condition_a": condition_a,
        "condition_b": condition_b,
        "symbol_level": symbol_effects,
        "tile_level": tile_effects,
    }

    if verbose:
        print_effect_size_summary(symbol_effects, condition_a, condition_b)
        print_tile_effect_size_summary(tile_effects, condition_a, condition_b)

    return results


def list_conditions(study_dir: Path) -> list[str]:
    """
    List all condition identifiers found in the study directory.

    Scans for detection GeoJSON files and extracts condition identifiers
    from their filenames.

    Args:
        study_dir: Path to study output directory.

    Returns:
        Sorted list of condition identifier strings.
    """
    conditions: set[str] = set()

    for f in study_dir.glob("*_detections.geojson"):
        conditions.add(f.stem.replace("_detections", ""))

    for f in study_dir.glob("*_consensus_detections.geojson"):
        conditions.add(f.stem.replace("_consensus_detections", ""))

    return sorted(conditions)


def compare_factor_levels(
    study_dir: Path,
    factor: str,
    n_iterations: int = 1000,
    random_seed: int | None = None,
) -> list[dict]:
    """
    Compare all pairs of conditions that differ only in the specified factor.

    Groups conditions by all factor parts except the target, then runs
    pairwise comparisons within each group.

    Args:
        study_dir: Path to study output directory.
        factor: Factor name (e.g., 'modality', 'ordering', 'hard_negatives').
        n_iterations: Bootstrap iterations.
        random_seed: Optional seed for reproducibility.

    Returns:
        List of effect size dictionaries for all comparisons.
    """
    conditions = list_conditions(study_dir)

    if not conditions:
        print(f"No conditions found in {study_dir}")
        return []

    # Group conditions by all factor parts except the target one.
    # Assumes format: factor1_factor2_factor3_factor4
    # e.g., image-only_canonical-first_baseline_T1.0
    groups: dict[tuple[str, ...], list[str]] = {}
    for cond in conditions:
        parts = cond.split("_")
        key = tuple(p for p in parts if factor not in p.lower())
        groups.setdefault(key, []).append(cond)

    # Run pairwise comparisons within each group
    results: list[dict] = []
    for group_conditions in groups.values():
        if len(group_conditions) < 2:
            continue

        for cond_a, cond_b in combinations(group_conditions, 2):
            print(f"\nComparing: {cond_a} vs {cond_b}")
            try:
                effect = compare_conditions(
                    study_dir,
                    cond_a,
                    cond_b,
                    n_iterations=n_iterations,
                    random_seed=random_seed,
                    verbose=True,
                )
                results.append(effect)
            except FileNotFoundError as e:
                print(f"  Skipping: {e}")

    return results


def _export_json(data: dict | list[dict], output_path: Path) -> None:
    """Write results to a JSON file and print confirmation."""
    with open(output_path, "w") as fh:
        json.dump(data, fh, indent=2)
    print(f"\nResults exported to {output_path}")


def main() -> None:
    """Parse command-line arguments and run the requested comparison."""
    parser = argparse.ArgumentParser(
        description=(
            "Compute bootstrapped effect size CIs between study conditions"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two conditions
  python scripts/analyse_study_effects.py outputs/study \\
      --condition-a image-only_canonical-first_baseline_T1.0 \\
      --condition-b text-image_canonical-first_baseline_T1.0

  # List available conditions
  python scripts/analyse_study_effects.py outputs/study --list

  # Export to JSON
  python scripts/analyse_study_effects.py outputs/study \\
      --condition-a A --condition-b B --output effects.json
        """,
    )

    parser.add_argument(
        "study_dir",
        type=Path,
        help="Path to study output directory",
    )
    parser.add_argument(
        "--condition-a",
        type=str,
        help="First condition ID",
    )
    parser.add_argument(
        "--condition-b",
        type=str,
        help="Second condition ID",
    )
    parser.add_argument(
        "--factor",
        type=str,
        help="Compare all pairs differing in this factor",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available conditions and exit",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="Number of bootstrap iterations (default: 1000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Export results to JSON file",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Validate study directory
    if not args.study_dir.exists():
        print(f"Error: Study directory not found: {args.study_dir}")
        sys.exit(1)

    # List conditions
    if args.list:
        conditions = list_conditions(args.study_dir)
        print(f"Conditions found in {args.study_dir}:")
        for c in conditions:
            print(f"  {c}")
        print(f"\nTotal: {len(conditions)} conditions")
        sys.exit(0)

    # Factor-based comparison
    if args.factor:
        results = compare_factor_levels(
            args.study_dir,
            args.factor,
            n_iterations=args.iterations,
            random_seed=args.seed,
        )
        if args.output:
            _export_json(results, args.output)
        sys.exit(0)

    # Pairwise comparison
    if args.condition_a and args.condition_b:
        effect_sizes = compare_conditions(
            args.study_dir,
            args.condition_a,
            args.condition_b,
            n_iterations=args.iterations,
            random_seed=args.seed,
            verbose=True,
        )
        if args.output:
            _export_json(effect_sizes, args.output)
        sys.exit(0)

    # No valid operation specified
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
