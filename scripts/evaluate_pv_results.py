#!/usr/bin/env python3
"""
PV Pipeline Evaluation Script
==============================

Description:
    Evaluates Proposer-Verifier (PV) pipeline results by sweeping
    probability thresholds and computing F1/precision/recall with
    bootstrap confidence intervals (CIs). Supports comparing multiple
    verifier variants.

    Two subcommands:

    - **sweep** — Threshold sweep on a single verifier variant
    - **compare** — Compare multiple variants at their optimal thresholds

Usage::

    # Threshold sweep
    python scripts/evaluate_pv_results.py sweep \\
        --probabilities outputs/pv/results/.../probabilities.json \\
        --manifest outputs/pv/crops-150/.../candidate_manifest.json \\
        --output-dir results/pv/phase1/adversarial-text-150/config-name

    # Compare variants
    python scripts/evaluate_pv_results.py compare \\
        --sweep-dirs results/pv/phase1/*/config-name \\
        --output-dir results/pv/phase1/comparison

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

# Project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_advanced_metrics import (
    bootstrap_ci,
    bootstrap_effect_size_ci,
    calculate_f1_internal,
)

# Script version
__version__ = "1.0.0"

# Default paths for reference data
_VECTORS_DIR = BASE_DIR / "inputs" / "vectors"
_REFERENCE_PATH = _VECTORS_DIR / "references" / "mounds-reference.geojson"
_BOUNDS_PATH = _VECTORS_DIR / "bounds" / "full_evaluation_bounds.geojson"

# Coordinate Reference System (CRS) for all spatial data
_TARGET_CRS = "EPSG:32635"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =========================================================================
# Helper: Load Probabilities (single-pass or consensus)
# =========================================================================


def load_probabilities(
    probabilities_path: Path,
    consensus_path: Path | None = None,
) -> dict[str, dict]:
    """Load per-candidate probabilities from single-pass or consensus output.

    For single-pass results (``probabilities.json``), returns the
    ``results`` dict directly — keys are ``"candidate_NNNNN"``.

    For consensus results (``consensus.json``), converts the aggregated
    ``mean_probability`` into the same format so downstream code
    (``build_candidate_gdf``) works unchanged.

    Args:
        probabilities_path: Path to ``probabilities.json``.
        consensus_path: Optional path to ``consensus.json``. If provided
            and the file exists, consensus mean probabilities are used
            instead of raw iteration-level results.

    Returns:
        Dict mapping ``"candidate_NNNNN"`` to result dicts containing
        ``mound_probability``.
    """
    # Prefer consensus if available
    if consensus_path and consensus_path.exists():
        with open(consensus_path, encoding="utf-8") as f:
            consensus_data = json.load(f)
        consensus = consensus_data.get("consensus", {})
        probabilities: dict[str, dict] = {}
        for _str_id, entry in consensus.items():
            cid = entry.get("candidate_id")
            if cid is None:
                continue
            key = f"candidate_{int(cid):05d}"
            probabilities[key] = {
                "mound_probability": entry.get("mean_probability", 0.0),
                "vote_count": entry.get("vote_count", 0),
                "total_iterations": entry.get("total_iterations", 0),
            }
        logger.info(
            "Loaded consensus probabilities: %d candidates "
            "(mean of %d iterations)",
            len(probabilities),
            consensus_data.get("iterations", 0),
        )
        return probabilities

    # Single-pass: unwrap from probabilities.json
    with open(probabilities_path, encoding="utf-8") as f:
        prob_data = json.load(f)
    probabilities = prob_data.get("results", {})

    # Check if these are iteration-level keys (consensus without consensus.json)
    if probabilities and any("_iter" in k for k in list(probabilities)[:5]):
        logger.warning(
            "Probabilities appear to be iteration-level (consensus) "
            "but no consensus.json found. Use run_pv.py verify to "
            "generate consensus.json, or pass --consensus. "
            "Returning empty dict to avoid silent all-zero results.",
        )
        return {}

    return probabilities


# =========================================================================
# Helper: Build Candidate GeoDataFrame
# =========================================================================


def build_candidate_gdf(
    manifest: dict,
    probabilities: dict[str, dict],
    threshold: float,
    crs: str = _TARGET_CRS,
) -> gpd.GeoDataFrame:
    """Filter candidates by probability threshold and build a GeoDataFrame.

    Constructs Point geometries from manifest centroids and retains only
    candidates whose ``mound_probability`` meets or exceeds the threshold.

    Args:
        manifest: Candidate manifest dict with ``candidates`` list.
        probabilities: Results dict from ``probabilities.json``, mapping
            candidate keys (e.g., ``"candidate_00042"``) to result dicts
            containing ``mound_probability``.
        threshold: Minimum ``mound_probability`` to accept a candidate.
        crs: Coordinate Reference System (default: EPSG:32635).

    Returns:
        GeoDataFrame with ``source_tile`` and ``geometry`` columns.
        Empty GeoDataFrame if no candidates pass the threshold.
    """
    rows: list[dict] = []
    geometries: list[Point] = []

    for candidate in manifest.get("candidates", []):
        # Guard required keys — skip malformed candidates
        cid = candidate.get("candidate_id")
        centroid_x = candidate.get("centroid_x")
        centroid_y = candidate.get("centroid_y")
        source_tile = candidate.get("source_tile")

        if cid is None or centroid_x is None or centroid_y is None:
            logger.warning(
                "Skipping candidate with missing fields: %s",
                candidate.get("candidate_id", "unknown"),
            )
            continue

        key = f"candidate_{cid:05d}"

        result = probabilities.get(key)
        if result is None:
            continue

        prob = result.get("mound_probability", 0.0)
        if prob < threshold:
            continue

        geometries.append(Point(centroid_x, centroid_y))
        rows.append({
            "source_tile": source_tile or "unknown",
            "mound_probability": prob,
        })

    if not rows:
        return gpd.GeoDataFrame(
            columns=["source_tile", "mound_probability", "geometry"],
            geometry="geometry",
            crs=crs,
        )

    return gpd.GeoDataFrame(rows, geometry=geometries, crs=crs)


# =========================================================================
# Sweep Subcommand
# =========================================================================


def cmd_sweep(args: argparse.Namespace) -> int:
    """Execute the sweep subcommand.

    Sweeps probability thresholds from 0.0 to 1.0, computing F1,
    precision, and recall with bootstrap CIs at each step.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    # Load probabilities (single-pass or consensus)
    consensus_path = getattr(args, "consensus", None)
    if consensus_path is None:
        # Auto-detect: look for consensus.json next to probabilities.json
        auto_consensus = args.probabilities.parent / "consensus.json"
        if auto_consensus.exists():
            consensus_path = auto_consensus
            logger.info("Auto-detected consensus.json: %s", consensus_path)

    try:
        probabilities = load_probabilities(args.probabilities, consensus_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Cannot load probabilities: %s", e)
        return 1

    # Load manifest
    try:
        with open(args.manifest, encoding="utf-8") as f:
            manifest = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Cannot load manifest: %s", e)
        return 1

    n_candidates = len(manifest.get("candidates", []))
    logger.info("Loaded %d candidates, %d probability results",
                n_candidates, len(probabilities))

    # Load reference data and verify CRS consistency
    gdf_ref = gpd.read_file(_REFERENCE_PATH)
    gdf_bounds = gpd.read_file(_BOUNDS_PATH)
    for name, gdf in [("reference", gdf_ref), ("bounds", gdf_bounds)]:
        if gdf.crs is None or gdf.crs.to_epsg() != 32635:
            logger.error(
                "%s data has CRS %s, expected EPSG:32635", name, gdf.crs,
            )
            return 1
    logger.info("Ground truth: %d mounds, %d evaluation tiles",
                len(gdf_ref), len(gdf_bounds))

    # Generate threshold steps
    step = args.step
    if step <= 0 or step > 1.0:
        logger.error("--step must be in (0.0, 1.0], got %.4f", step)
        return 1
    thresholds = list(np.arange(0.0, 1.0 + step / 2, step))
    # Ensure 1.0 is included, clamp values >1.0, and round to avoid float artefacts
    thresholds = sorted(set(round(t, 4) for t in thresholds if t <= 1.0) | {1.0})

    logger.info(
        "Sweeping %d thresholds (step=%.2f, bootstrap=%d)",
        len(thresholds), step, args.bootstrap,
    )

    # Sweep
    results: list[dict] = []
    best_f1 = -1.0
    best_entry: dict = {}

    for threshold in thresholds:
        gdf_det = build_candidate_gdf(manifest, probabilities, threshold)
        n_accepted = len(gdf_det)

        if n_accepted == 0:
            entry = {
                "threshold": threshold,
                "n_accepted": 0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "ci": {},
            }
            results.append(entry)
            # Still track as potential best if nothing better exists
            if not best_entry:
                best_entry = entry
            continue

        # Point estimate
        precision, recall, f1 = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds,
        )

        # Bootstrap CIs
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=args.bootstrap,
            random_seed=args.seed,
        )

        entry = {
            "threshold": threshold,
            "n_accepted": n_accepted,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "ci": {
                "f1": {
                    "mean": round(ci["f1"]["mean"], 4),
                    "lower": round(ci["f1"]["ci_lower"], 4),
                    "upper": round(ci["f1"]["ci_upper"], 4),
                },
                "precision": {
                    "mean": round(ci["precision"]["mean"], 4),
                    "lower": round(ci["precision"]["ci_lower"], 4),
                    "upper": round(ci["precision"]["ci_upper"], 4),
                },
                "recall": {
                    "mean": round(ci["recall"]["mean"], 4),
                    "lower": round(ci["recall"]["ci_lower"], 4),
                    "upper": round(ci["recall"]["ci_upper"], 4),
                },
            },
        }
        results.append(entry)

        if f1 > best_f1:
            best_f1 = f1
            best_entry = entry

        logger.info(
            "  T=%.2f: n=%d, P=%.3f, R=%.3f, F1=%.3f "
            "[%.3f–%.3f]",
            threshold, n_accepted, precision, recall, f1,
            ci["f1"]["ci_lower"], ci["f1"]["ci_upper"],
        )

    # Write outputs
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    sweep_data = {
        "version": "1.0",
        "probabilities_file": str(args.probabilities.resolve()),
        "manifest_file": str(args.manifest.resolve()),
        "total_candidates": n_candidates,
        "ground_truth_mounds": len(gdf_ref),
        "evaluation_tiles": len(gdf_bounds),
        "step": step,
        "bootstrap_iterations": args.bootstrap,
        "seed": args.seed,
        "thresholds": results,
        "optimal": best_entry,
    }
    json_path = args.output_dir / "threshold_sweep.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sweep_data, f, indent=2)
    logger.info("Sweep JSON written: %s", json_path)

    # CSV
    csv_path = args.output_dir / "threshold_sweep.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "threshold", "n_accepted",
            "precision", "recall", "f1",
            "f1_ci_lower", "f1_ci_upper",
            "p_ci_lower", "p_ci_upper",
            "r_ci_lower", "r_ci_upper",
        ])
        for entry in results:
            ci = entry.get("ci", {})
            writer.writerow([
                entry["threshold"],
                entry["n_accepted"],
                entry["precision"],
                entry["recall"],
                entry["f1"],
                ci.get("f1", {}).get("lower", ""),
                ci.get("f1", {}).get("upper", ""),
                ci.get("precision", {}).get("lower", ""),
                ci.get("precision", {}).get("upper", ""),
                ci.get("recall", {}).get("lower", ""),
                ci.get("recall", {}).get("upper", ""),
            ])
    logger.info("Sweep CSV written: %s", csv_path)

    # Summary
    if best_entry:
        logger.info(
            "Optimal: threshold=%.2f, F1=%.3f [%.3f–%.3f], "
            "P=%.3f, R=%.3f, n=%d",
            best_entry["threshold"], best_entry["f1"],
            best_entry.get("ci", {}).get("f1", {}).get("lower", 0),
            best_entry.get("ci", {}).get("f1", {}).get("upper", 0),
            best_entry["precision"], best_entry["recall"],
            best_entry["n_accepted"],
        )

    return 0


# =========================================================================
# Compare Subcommand
# =========================================================================


def cmd_compare(args: argparse.Namespace) -> int:
    """Execute the compare subcommand.

    Loads threshold sweep results from multiple variant directories and
    produces a comparison table. Optionally runs pairwise bootstrap
    effect size tests.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    # Load sweep results from each directory
    variants: list[dict] = []
    for sweep_dir in sorted(args.sweep_dirs):
        sweep_path = Path(sweep_dir) / "threshold_sweep.json"
        if not sweep_path.exists():
            logger.warning("Sweep file not found: %s — skipping", sweep_path)
            continue

        with open(sweep_path, encoding="utf-8") as f:
            sweep_data = json.load(f)

        # Derive variant name from directory path — use parent/dir
        # to distinguish variants with shared parent directories
        sweep_path_obj = Path(sweep_dir)
        variant_name = (
            f"{sweep_path_obj.parent.name}/{sweep_path_obj.name}"
        )
        optimal = sweep_data.get("optimal", {})
        variants.append({
            "name": variant_name,
            "dir": str(sweep_dir),
            "optimal_threshold": optimal.get("threshold", 0.0),
            "f1": optimal.get("f1", 0.0),
            "precision": optimal.get("precision", 0.0),
            "recall": optimal.get("recall", 0.0),
            "n_accepted": optimal.get("n_accepted", 0),
            "ci": optimal.get("ci", {}),
            "probabilities_file": sweep_data.get("probabilities_file", ""),
            "manifest_file": sweep_data.get("manifest_file", ""),
        })

    if len(variants) < 2:
        logger.error(
            "Need at least 2 variants for comparison, found %d",
            len(variants),
        )
        return 1

    logger.info("Comparing %d variants", len(variants))
    for v in variants:
        logger.info(
            "  %s: F1=%.3f at threshold=%.2f",
            v["name"], v["f1"], v["optimal_threshold"],
        )

    # Pairwise bootstrap effect size tests
    pairwise: list[dict] = []
    if args.pairwise:
        gdf_ref = gpd.read_file(_REFERENCE_PATH)
        gdf_bounds = gpd.read_file(_BOUNDS_PATH)

        for i, va in enumerate(variants):
            for vb in variants[i + 1:]:
                logger.info(
                    "  Pairwise: %s vs %s", va["name"], vb["name"],
                )
                gdf_a = _load_variant_gdf(va, gdf_bounds)
                gdf_b = _load_variant_gdf(vb, gdf_bounds)

                if gdf_a is None or gdf_b is None:
                    logger.warning(
                        "  Skipping — could not load GeoDataFrames",
                    )
                    continue

                effect = bootstrap_effect_size_ci(
                    gdf_det_a=gdf_a,
                    gdf_bounds_a=gdf_bounds,
                    gdf_det_b=gdf_b,
                    gdf_bounds_b=gdf_bounds,
                    gdf_ref=gdf_ref,
                    n_iterations=args.bootstrap,
                    random_seed=args.seed,
                    return_p_values=True,
                )

                pairwise.append({
                    "variant_a": va["name"],
                    "variant_b": vb["name"],
                    "f1_difference": effect.get("f1_difference", {}),
                    "precision_difference": effect.get(
                        "precision_difference", {},
                    ),
                    "recall_difference": effect.get(
                        "recall_difference", {},
                    ),
                })

    # Write outputs
    args.output_dir.mkdir(parents=True, exist_ok=True)

    comparison_data = {
        "version": "1.0",
        "n_variants": len(variants),
        "variants": variants,
        "pairwise": pairwise,
    }
    json_path = args.output_dir / "comparison.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comparison_data, f, indent=2)
    logger.info("Comparison JSON written: %s", json_path)

    # CSV — variant summary
    csv_path = args.output_dir / "comparison.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "variant", "optimal_threshold", "n_accepted",
            "precision", "recall", "f1",
            "f1_ci_lower", "f1_ci_upper",
        ])
        for v in variants:
            ci = v.get("ci", {}).get("f1", {})
            writer.writerow([
                v["name"],
                v["optimal_threshold"],
                v["n_accepted"],
                v["precision"],
                v["recall"],
                v["f1"],
                ci.get("lower", ""),
                ci.get("upper", ""),
            ])
    logger.info("Comparison CSV written: %s", csv_path)

    return 0


def _load_variant_gdf(
    variant: dict,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame | None:
    """Load and filter a variant's detections at its optimal threshold.

    Reconstructs the GeoDataFrame from the variant's original
    probabilities and manifest files.

    Args:
        variant: Variant dict with ``probabilities_file``,
            ``manifest_file``, and ``optimal_threshold``.
        gdf_bounds: Evaluation bounds GeoDataFrame (unused but kept
            for consistency with potential future scoping).

    Returns:
        Filtered GeoDataFrame, or None if files cannot be loaded.
    """
    try:
        # Check for consensus.json alongside probabilities
        prob_path = Path(variant["probabilities_file"])
        consensus_path = prob_path.parent / "consensus.json"
        probabilities = load_probabilities(
            prob_path,
            consensus_path if consensus_path.exists() else None,
        )

        with open(variant["manifest_file"], encoding="utf-8") as f:
            manifest = json.load(f)

        return build_candidate_gdf(
            manifest,
            probabilities,
            variant["optimal_threshold"],
        )
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.warning("Cannot load variant %s: %s", variant["name"], e)
        return None


# =========================================================================
# CLI
# =========================================================================


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with sweep and compare subcommands."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate PV pipeline results — threshold sweep with "
            "bootstrap CIs and variant comparison"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Sweep subcommand ---
    sweep_parser = subparsers.add_parser(
        "sweep",
        help="Threshold sweep on a single verifier variant",
    )
    sweep_parser.add_argument(
        "--probabilities", type=Path, required=True,
        help="Path to probabilities.json from run_pv.py verify",
    )
    sweep_parser.add_argument(
        "--manifest", type=Path, required=True,
        help="Path to candidate_manifest.json from run_pv.py extract",
    )
    sweep_parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Directory for sweep outputs (JSON + CSV)",
    )
    sweep_parser.add_argument(
        "--consensus", type=Path, default=None,
        help=(
            "Path to consensus.json (for multi-iteration results). "
            "Auto-detected if next to probabilities.json."
        ),
    )
    sweep_parser.add_argument(
        "--step", type=float, default=0.05,
        help="Threshold step size (default: 0.05)",
    )
    sweep_parser.add_argument(
        "--bootstrap", type=int, default=1000,
        help="Number of bootstrap iterations (default: 1000)",
    )
    sweep_parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    sweep_parser.set_defaults(func=cmd_sweep)

    # --- Compare subcommand ---
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare multiple verifier variants",
    )
    compare_parser.add_argument(
        "--sweep-dirs", type=Path, nargs="+", required=True,
        help="Directories containing threshold_sweep.json files",
    )
    compare_parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Directory for comparison outputs",
    )
    compare_parser.add_argument(
        "--pairwise", action="store_true",
        help="Run pairwise bootstrap effect size tests",
    )
    compare_parser.add_argument(
        "--bootstrap", type=int, default=1000,
        help="Bootstrap iterations for pairwise tests (default: 1000)",
    )
    compare_parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    compare_parser.set_defaults(func=cmd_compare)

    return parser


def main() -> None:
    """Parse arguments and dispatch to subcommand handler."""
    parser = _build_parser()
    args = parser.parse_args()
    exit_code = args.func(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
