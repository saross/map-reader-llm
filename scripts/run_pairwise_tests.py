#!/usr/bin/env python3
"""Orchestrate batch pairwise permutation tests from a YAML config.

Reads a YAML file defining pairwise comparisons (conditions, groups,
families), builds detection GeoDataFrames for each side, runs tile-swap
permutation tests, and writes per-comparison JSONs plus a consolidated
run manifest for downstream FDR correction.

Supports three condition types:
- **pv**: Proposer-Verifier (probabilities + manifest + threshold)
- **consensus**: Consensus voting (study directory + config string)
- **geojson**: Arbitrary detection GeoJSON files

All heavy lifting is delegated to ``pairwise_permutation_test.py`` via
direct function imports — ground truth and bounds are loaded once and
GeoDataFrames are cached across comparisons.

Usage — hypothesis-driven comparisons:

    python scripts/run_pairwise_tests.py \\
        --config configs/pairwise-comparisons.yaml \\
        --buffer-metres 30 \\
        --output-dir results/pairwise/30m

Usage — filter to a single group:

    python scripts/run_pairwise_tests.py \\
        --config configs/pairwise-comparisons.yaml \\
        --buffer-metres 30 \\
        --output-dir results/pairwise/30m \\
        --filter-group 6

Usage — leaderboard round-robin:

    python scripts/run_pairwise_tests.py \\
        --leaderboard configs/condition-registry.yaml \\
        --metrics results/paper-tables/metrics_master.csv \\
        --top-n 25 \\
        --buffer-metres 30 \\
        --output-dir results/pairwise/leaderboard-30m

Created: 2026-03-28
Author: Shawn Ross & Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
import time
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import yaml

# Ensure scripts/ is on the path for sibling imports
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pairwise_permutation_test import (  # noqa: E402
    assign_source_tiles,
    load_consensus_detections,
    load_geojson_detections,
    load_pv_detections,
    run_permutation_test,
)

__version__ = "1.0.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default paths
BASE_DIR = _SCRIPT_DIR.parent
_VECTORS_DIR = BASE_DIR / "inputs" / "vectors"
_BOUNDS_PATH = (
    _VECTORS_DIR / "bounds" / "384" / "full_evaluation_bounds.geojson"
)
_REF_PATH = _VECTORS_DIR / "references" / "mounds-reference.geojson"
_TARGET_CRS = "EPSG:32635"

# Group name mapping for output directory names
_GROUP_NAMES = {
    1: "group_1_architecture",
    2: "group_2_modality",
    3: "group_3_thinking",
    4: "group_4_temperature",
    5: "group_5_model",
    6: "group_6_topn",
    7: "group_7_poolsize",
}


# ── YAML loading and validation ─────────────────────────────────────


def sanitise_slug(label: str) -> str:
    """Convert a human-readable label to a filesystem-safe slug.

    Lowercases, replaces non-alphanumeric characters with hyphens,
    collapses runs, and strips leading/trailing hyphens.

    Args:
        label: Human-readable condition or comparison label.

    Returns:
        Filesystem-safe slug string.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def load_comparisons_yaml(
    path: Path,
) -> tuple[dict, list[dict]]:
    """Load and validate a pairwise comparisons YAML config.

    Resolves relative paths against the project root. Each comparison
    inherits from the defaults section unless overridden.

    Args:
        path: Path to the YAML config file.

    Returns:
        Tuple of (defaults_dict, comparisons_list).

    Raises:
        ValueError: If the YAML is malformed or missing required fields.
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    defaults = data.get("defaults", {})
    metadata = data.get("metadata", {})
    comparisons = data.get("comparisons", [])

    if not comparisons:
        msg = f"No comparisons found in {path}"
        raise ValueError(msg)

    # Resolve default paths relative to project root
    for key in ["bounds", "ground_truth"]:
        if key in defaults and not Path(defaults[key]).is_absolute():
            defaults[key] = str(BASE_DIR / defaults[key])

    # Merge defaults into each comparison and resolve paths
    resolved = []
    for i, comp in enumerate(comparisons, 1):
        merged = {**defaults, **comp}

        # Validate required fields
        if "label_a" not in merged or "label_b" not in merged:
            msg = f"Comparison {i} missing label_a or label_b"
            raise ValueError(msg)

        # Resolve relative paths for condition-specific fields
        for suffix in ["a", "b"]:
            ctype = merged.get(f"type_{suffix}", "consensus")
            if ctype == "pv":
                for field in [
                    f"probabilities_{suffix}",
                    f"manifest_{suffix}",
                ]:
                    val = merged.get(field)
                    if val and not Path(val).is_absolute():
                        merged[field] = str(BASE_DIR / val)
            elif ctype == "consensus":
                field = f"study_dir_{suffix}"
                val = merged.get(field)
                if val and not Path(val).is_absolute():
                    merged[field] = str(BASE_DIR / val)
            elif ctype == "geojson":
                field = f"geojson_{suffix}"
                val = merged.get(field)
                if val and not Path(val).is_absolute():
                    merged[field] = str(BASE_DIR / val)

        merged.setdefault("group", 0)
        merged.setdefault("family", "confirmatory")
        merged.setdefault("question", "")
        resolved.append(merged)

    logger.info(
        "Loaded %d comparisons from %s", len(resolved), path,
    )
    defaults["_metadata"] = metadata
    return defaults, resolved


def validate_paths(comparisons: list[dict]) -> list[str]:
    """Pre-flight check that all referenced paths exist.

    Args:
        comparisons: List of resolved comparison dicts.

    Returns:
        List of error messages for missing paths (empty if all OK).
    """
    errors = []
    for i, comp in enumerate(comparisons, 1):
        label = f"#{i} {comp.get('label_a', '?')} vs {comp.get('label_b', '?')}"
        for suffix in ["a", "b"]:
            ctype = comp.get(f"type_{suffix}", "consensus")
            if ctype == "pv":
                for field in [
                    f"probabilities_{suffix}",
                    f"manifest_{suffix}",
                ]:
                    val = comp.get(field)
                    if val and not Path(val).exists():
                        errors.append(f"{label}: {field} not found: {val}")
            elif ctype == "consensus":
                val = comp.get(f"study_dir_{suffix}")
                if val and not Path(val).is_dir():
                    errors.append(
                        f"{label}: study_dir_{suffix} not found: {val}"
                    )
            elif ctype == "geojson":
                val = comp.get(f"geojson_{suffix}")
                if val and not Path(val).exists():
                    errors.append(
                        f"{label}: geojson_{suffix} not found: {val}"
                    )
    return errors


# ── GeoDataFrame loading with cache ─────────────────────────────────


def build_cache_key(
    comp: dict,
    suffix: str,
) -> tuple:
    """Build a hashable cache key for a condition specification.

    Args:
        comp: Comparison dict.
        suffix: "a" or "b".

    Returns:
        Hashable tuple identifying this condition's detection source.
    """
    ctype = comp.get(f"type_{suffix}", "consensus")
    if ctype == "pv":
        return (
            "pv",
            comp.get(f"probabilities_{suffix}", ""),
            comp.get(f"manifest_{suffix}", ""),
            comp.get(f"threshold_{suffix}", 0.0),
        )
    elif ctype == "consensus":
        return (
            "consensus",
            comp.get(f"study_dir_{suffix}", ""),
            comp.get(f"config_{suffix}", ""),
        )
    elif ctype == "geojson":
        return (
            "geojson",
            comp.get(f"geojson_{suffix}", ""),
        )
    return ("unknown",)


def load_condition_gdf(
    comp: dict,
    suffix: str,
    gdf_bounds: gpd.GeoDataFrame,
    cache: dict[tuple, gpd.GeoDataFrame],
) -> gpd.GeoDataFrame:
    """Load a condition's detection GeoDataFrame, using cache if available.

    Dispatches to the appropriate loader based on the condition type.

    Args:
        comp: Comparison dict with condition parameters.
        suffix: "a" or "b".
        gdf_bounds: Tile boundary GeoDataFrame.
        cache: Mutable dict mapping cache keys to GeoDataFrames.

    Returns:
        Detection GeoDataFrame with source_tile and geometry columns.
    """
    key = build_cache_key(comp, suffix)
    if key in cache:
        logger.debug("Cache hit: %s", comp.get(f"label_{suffix}", "?"))
        return cache[key]

    ctype = comp.get(f"type_{suffix}", "consensus")

    if ctype == "pv":
        gdf = load_pv_detections(
            Path(comp[f"probabilities_{suffix}"]),
            Path(comp[f"manifest_{suffix}"]),
            float(comp[f"threshold_{suffix}"]),
        )
    elif ctype == "consensus":
        gdf = load_consensus_detections(
            Path(comp[f"study_dir_{suffix}"]),
            comp[f"config_{suffix}"],
            gdf_bounds,
        )
    elif ctype == "geojson":
        gdf = load_geojson_detections(Path(comp[f"geojson_{suffix}"]))
        gdf = assign_source_tiles(gdf, gdf_bounds)
    else:
        msg = f"Unknown condition type: {ctype}"
        raise ValueError(msg)

    cache[key] = gdf
    return gdf


def build_source_metadata(comp: dict, suffix: str) -> dict:
    """Build source provenance metadata for a condition.

    Args:
        comp: Comparison dict.
        suffix: "a" or "b".

    Returns:
        Dict with mode-specific source information.
    """
    ctype = comp.get(f"type_{suffix}", "consensus")
    if ctype == "pv":
        return {
            "mode": "pv",
            "probabilities": comp.get(f"probabilities_{suffix}", ""),
            "manifest": comp.get(f"manifest_{suffix}", ""),
            "threshold": comp.get(f"threshold_{suffix}", 0.0),
        }
    elif ctype == "consensus":
        config_str = comp.get(f"config_{suffix}", "")
        parts = config_str.split(",")
        return {
            "mode": "consensus",
            "study_dir": comp.get(f"study_dir_{suffix}", ""),
            "temperature": parts[0].strip() if parts else "",
            "pool_size": int(parts[1].strip()) if len(parts) > 1 else 0,
            "threshold": int(parts[2].strip()) if len(parts) > 2 else 0,
        }
    elif ctype == "geojson":
        return {
            "mode": "geojson",
            "geojson": comp.get(f"geojson_{suffix}", ""),
        }
    return {"mode": "unknown"}


# ── Leaderboard mode ────────────────────────────────────────────────


def load_leaderboard_conditions(
    registry_path: Path,
    metrics_path: Path,
    top_n: int,
    buffer_metres: int,
) -> tuple[dict, list[dict]]:
    """Generate all-pairs comparisons from top-N leaderboard conditions.

    Reads a condition registry (label → source parameters) and a
    metrics CSV (label → F1 at specified buffer), selects the top-N,
    and generates C(N,2) pairwise comparisons.

    Args:
        registry_path: Path to condition-registry.yaml.
        metrics_path: Path to metrics_master.csv.
        top_n: Number of top conditions to include.
        buffer_metres: Buffer distance to filter metrics by.

    Returns:
        Tuple of (defaults_dict, comparisons_list) in the same
        format as load_comparisons_yaml().
    """
    # Load registry
    with open(registry_path, encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    conditions_map = {}
    for cond in registry.get("conditions", []):
        conditions_map[cond["label"]] = cond

    # Load metrics and filter to target buffer
    metrics = []
    with open(metrics_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["buffer_metres"]) == buffer_metres:
                metrics.append(row)

    # Sort by F1 descending and take top-N unique conditions
    metrics.sort(key=lambda x: float(x["f1"]), reverse=True)
    seen_labels: set[str] = set()
    top_conditions: list[dict] = []
    for row in metrics:
        # Build a unique key from type + label + pool_size + config
        label_key = (
            f"{row['condition_type']}|{row['condition_label']}"
            f"|{row['pool_size']}|{row['config_details']}"
        )
        if label_key not in seen_labels:
            seen_labels.add(label_key)
            top_conditions.append(row)
            if len(top_conditions) >= top_n:
                break

    logger.info(
        "Selected top-%d conditions at %dm buffer",
        len(top_conditions), buffer_metres,
    )

    # Generate all pairs
    comparisons = []
    for cond_a, cond_b in combinations(top_conditions, 2):
        # Look up source parameters from registry
        label_a = _build_leaderboard_label(cond_a)
        label_b = _build_leaderboard_label(cond_b)

        reg_a = conditions_map.get(label_a)
        reg_b = conditions_map.get(label_b)

        if reg_a is None:
            logger.warning(
                "Registry missing condition: %s — skipping pairs",
                label_a,
            )
            continue
        if reg_b is None:
            logger.warning(
                "Registry missing condition: %s — skipping pairs",
                label_b,
            )
            continue

        comp = {
            "label_a": label_a,
            "label_b": label_b,
            "group": 8,
            "question": "Leaderboard distinguishability",
            "family": "leaderboard",
            **_registry_to_comparison_fields(reg_a, "a"),
            **_registry_to_comparison_fields(reg_b, "b"),
        }
        comparisons.append(comp)

    logger.info(
        "Generated %d leaderboard comparisons from %d conditions",
        len(comparisons), len(top_conditions),
    )

    defaults = {
        "bounds": str(_BOUNDS_PATH),
        "ground_truth": str(_REF_PATH),
        "_metadata": {
            "description": (
                f"Leaderboard round-robin: top-{top_n} at "
                f"{buffer_metres}m buffer"
            ),
            "source_registry": str(registry_path),
            "source_metrics": str(metrics_path),
        },
    }
    return defaults, comparisons


def _build_leaderboard_label(row: dict) -> str:
    """Build a unique label for a leaderboard condition row.

    Args:
        row: CSV row dict from metrics_master.csv.

    Returns:
        Human-readable label string.
    """
    ctype = row["condition_type"]
    label = row["condition_label"]
    pool = row.get("pool_size", "")
    config = row.get("config_details", "")
    if ctype == "pv":
        return f"{label} ({config})"
    return f"{label} N={pool} {config}"


def _registry_to_comparison_fields(
    reg: dict,
    suffix: str,
) -> dict:
    """Convert a registry entry to comparison dict fields.

    Args:
        reg: Registry condition dict with type and source params.
        suffix: "a" or "b".

    Returns:
        Dict with type_{suffix} and source-specific fields.
    """
    ctype = reg["type"]
    fields: dict = {f"type_{suffix}": ctype}
    if ctype == "pv":
        fields[f"probabilities_{suffix}"] = reg["probabilities"]
        fields[f"manifest_{suffix}"] = reg["manifest"]
        fields[f"threshold_{suffix}"] = reg["threshold"]
    elif ctype == "consensus":
        fields[f"study_dir_{suffix}"] = reg["study_dir"]
        fields[f"config_{suffix}"] = reg["config"]
    elif ctype == "geojson":
        fields[f"geojson_{suffix}"] = reg["geojson"]
    return fields


# ── Output writers ───────────────────────────────────────────────────


def write_comparison_result(
    result: dict,
    comp: dict,
    buffer_metres: int,
    n_permutations: int,
    seed: int,
    output_path: Path,
    include_per_tile: bool = True,
) -> None:
    """Write a single comparison result as JSON.

    Produces output compatible with the existing
    ``pairwise_permutation_result.json`` schema.

    Args:
        result: Dict from run_permutation_test().
        comp: Comparison spec dict.
        buffer_metres: Buffer distance used.
        n_permutations: Number of permutations.
        seed: Random seed.
        output_path: Path to write JSON file.
        include_per_tile: Whether to include per-tile details.
    """
    output = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "script": "run_pairwise_tests.py",
            "version": __version__,
            "group": comp.get("group", 0),
            "question": comp.get("question", ""),
            "family": comp.get("family", "confirmatory"),
            "buffer_metres": buffer_metres,
            "n_permutations": n_permutations,
            "seed": seed,
        },
        "condition_a": {
            "label": comp["label_a"],
            "source": build_source_metadata(comp, "a"),
            **result["global_a"],
        },
        "condition_b": {
            "label": comp["label_b"],
            "source": build_source_metadata(comp, "b"),
            **result["global_b"],
        },
        "permutation_test": result["permutation_test"],
    }
    if include_per_tile:
        output["per_tile"] = result["per_tile"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)


def write_run_manifest(
    all_results: list[dict],
    output_dir: Path,
    buffer_metres: int,
    n_permutations: int,
    seed: int,
) -> None:
    """Write consolidated run manifest for FDR correction.

    The manifest contains summary data for all comparisons without
    per-tile details (those are in individual JSONs).

    Args:
        all_results: List of (comparison_spec, result_dict) tuples.
        output_dir: Root output directory.
        buffer_metres: Buffer distance used.
        n_permutations: Number of permutations.
        seed: Random seed.
    """
    manifest = {
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "script": "run_pairwise_tests.py",
            "version": __version__,
            "buffer_metres": buffer_metres,
            "n_permutations": n_permutations,
            "seed": seed,
            "n_comparisons": len(all_results),
        },
        "comparisons": [],
    }

    for comp, result in all_results:
        entry = {
            "group": comp.get("group", 0),
            "question": comp.get("question", ""),
            "family": comp.get("family", "confirmatory"),
            "label_a": comp["label_a"],
            "label_b": comp["label_b"],
            "f1_a": result["global_a"]["f1"],
            "f1_b": result["global_b"]["f1"],
            "precision_a": result["global_a"]["precision"],
            "precision_b": result["global_b"]["precision"],
            "recall_a": result["global_a"]["recall"],
            "recall_b": result["global_b"]["recall"],
            "n_detections_a": result["global_a"]["n_detections"],
            "n_detections_b": result["global_b"]["n_detections"],
            "delta_f1": result["permutation_test"]["observed_f1_diff"],
            "p_value": result["permutation_test"]["p_value"],
            "n_tiles": result["permutation_test"]["n_tiles"],
            "wins_a": result["permutation_test"]["wins_a"],
            "losses_a": result["permutation_test"]["losses_a"],
            "ties": result["permutation_test"]["ties"],
        }
        manifest["comparisons"].append(entry)

    out_path = output_dir / "run_manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Run manifest written: %s", out_path)


def _significance_marker(p: float) -> str:
    """Return significance marker string for a p-value."""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


def print_summary_table(all_results: list[tuple[dict, dict]]) -> None:
    """Print a console summary table of all comparison results.

    Args:
        all_results: List of (comparison_spec, result_dict) tuples.
    """
    print("\n" + "=" * 80)
    print("PAIRWISE PERMUTATION TEST RESULTS")
    print("=" * 80)

    current_group = None
    for comp, result in all_results:
        group = comp.get("group", 0)
        if group != current_group:
            current_group = group
            group_name = _GROUP_NAMES.get(
                group, f"group_{group}",
            )
            print(f"\n── {group_name} ──")

        test = result["permutation_test"]
        sig = _significance_marker(test["p_value"])
        print(
            f"  {comp['label_a'][:35]:35s} vs "
            f"{comp['label_b'][:35]:35s}  "
            f"ΔF1={test['observed_f1_diff']:+.4f}  "
            f"p={test['p_value']:.4f} {sig}"
        )

    print("\n" + "=" * 80)
    n_sig = sum(
        1 for _, r in all_results
        if r["permutation_test"]["p_value"] < 0.05
    )
    print(
        f"Total: {len(all_results)} comparisons, "
        f"{n_sig} significant at p < 0.05 (before FDR)"
    )
    print("=" * 80)


# ── Main ─────────────────────────────────────────────────────────────


def main() -> None:
    """Run batch pairwise permutation tests."""
    parser = argparse.ArgumentParser(
        description=(
            "Batch pairwise permutation tests from YAML config. "
            "Runs all comparisons, writes per-comparison JSONs, "
            "and produces a consolidated manifest for FDR correction."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )

    # Input mode (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--config", type=Path,
        help="YAML config defining pairwise comparisons",
    )
    input_group.add_argument(
        "--leaderboard", type=Path,
        help=(
            "Condition registry YAML for leaderboard round-robin mode"
        ),
    )

    # Leaderboard-specific
    parser.add_argument(
        "--metrics", type=Path,
        help=(
            "Metrics CSV for leaderboard mode "
            "(default: results/paper-tables/metrics_master.csv)"
        ),
        default=BASE_DIR / "results" / "paper-tables" / "metrics_master.csv",
    )
    parser.add_argument(
        "--top-n", type=int, default=25,
        help="Number of top conditions for leaderboard (default: 25)",
    )

    # Common parameters
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Root output directory for results",
    )
    parser.add_argument(
        "--buffer-metres", type=int, default=30,
        help="Spatial matching tolerance in metres (default: 30)",
    )
    parser.add_argument(
        "--n-permutations", type=int, default=10_000,
        help="Number of permutation iterations (default: 10,000)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--filter-group", type=int, default=None,
        help="Only run comparisons from this group number",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress per-tile details in output JSONs",
    )
    parser.add_argument(
        "--bounds", type=Path, default=_BOUNDS_PATH,
        help=f"Evaluation bounds GeoJSON (default: {_BOUNDS_PATH.name})",
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=_REF_PATH,
        help=f"Ground truth GeoJSON (default: {_REF_PATH.name})",
    )

    args = parser.parse_args()

    # Load comparisons from config or leaderboard mode
    if args.config:
        defaults, comparisons = load_comparisons_yaml(args.config)
    else:
        defaults, comparisons = load_leaderboard_conditions(
            registry_path=args.leaderboard,
            metrics_path=args.metrics,
            top_n=args.top_n,
            buffer_metres=args.buffer_metres,
        )

    # Apply group filter if specified
    if args.filter_group is not None:
        comparisons = [
            c for c in comparisons
            if c.get("group") == args.filter_group
        ]
        logger.info(
            "Filtered to group %d: %d comparisons",
            args.filter_group, len(comparisons),
        )

    if not comparisons:
        logger.error("No comparisons to run after filtering.")
        sys.exit(1)

    # Validate all paths before running anything
    path_errors = validate_paths(comparisons)
    if path_errors:
        logger.error(
            "Path validation failed (%d errors):", len(path_errors),
        )
        for err in path_errors:
            logger.error("  %s", err)
        sys.exit(1)

    # Load reference data once
    bounds_path = args.bounds
    gt_path = args.ground_truth
    logger.info("Loading ground truth: %s", gt_path)
    gdf_ref = gpd.read_file(gt_path).to_crs(_TARGET_CRS)
    logger.info("Loading bounds: %s", bounds_path)
    gdf_bounds = gpd.read_file(bounds_path).to_crs(_TARGET_CRS)
    logger.info(
        "Reference: %d mounds, %d tiles",
        len(gdf_ref), len(gdf_bounds),
    )

    # GeoDataFrame cache
    gdf_cache: dict[tuple, gpd.GeoDataFrame] = {}

    # Run all comparisons
    all_results: list[tuple[dict, dict]] = []
    total = len(comparisons)
    t_start = time.time()

    for i, comp in enumerate(comparisons, 1):
        group = comp.get("group", 0)
        group_name = _GROUP_NAMES.get(group, f"group_{group}")
        logger.info(
            "[%d/%d] Group %d: %s vs %s",
            i, total, group,
            comp["label_a"][:40], comp["label_b"][:40],
        )

        # Load detection GeoDataFrames
        gdf_a = load_condition_gdf(comp, "a", gdf_bounds, gdf_cache)
        gdf_b = load_condition_gdf(comp, "b", gdf_bounds, gdf_cache)

        if len(gdf_a) == 0:
            logger.warning(
                "  Condition A (%s) has 0 detections",
                comp["label_a"],
            )
        if len(gdf_b) == 0:
            logger.warning(
                "  Condition B (%s) has 0 detections",
                comp["label_b"],
            )

        # Run permutation test
        result = run_permutation_test(
            gdf_a, gdf_b, gdf_ref, gdf_bounds,
            buffer_metres=args.buffer_metres,
            n_permutations=args.n_permutations,
            seed=args.seed,
        )

        # Log summary
        test = result["permutation_test"]
        sig = _significance_marker(test["p_value"])
        logger.info(
            "  ΔF1=%+.4f, p=%.4f %s (A: F1=%.3f, B: F1=%.3f)",
            test["observed_f1_diff"], test["p_value"], sig,
            result["global_a"]["f1"], result["global_b"]["f1"],
        )

        # Write per-comparison JSON
        slug = sanitise_slug(
            f"{comp.get('question', 'comparison')}-"
            f"{comp['label_a']}-vs-{comp['label_b']}"
        )
        output_path = (
            args.output_dir / group_name
            / f"{slug}.json"
        )
        write_comparison_result(
            result, comp,
            buffer_metres=args.buffer_metres,
            n_permutations=args.n_permutations,
            seed=args.seed,
            output_path=output_path,
            include_per_tile=not args.quiet,
        )

        all_results.append((comp, result))

    elapsed = time.time() - t_start
    logger.info(
        "Completed %d comparisons in %.1f seconds (%.1fs each)",
        total, elapsed, elapsed / total if total else 0,
    )

    # Write consolidated manifest
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_run_manifest(
        all_results, args.output_dir,
        buffer_metres=args.buffer_metres,
        n_permutations=args.n_permutations,
        seed=args.seed,
    )

    # Console summary
    print_summary_table(all_results)


if __name__ == "__main__":
    main()
