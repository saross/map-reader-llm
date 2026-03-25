#!/usr/bin/env python3
"""Evaluate Proposer-Verifier (PV) results at multiple spatial buffer distances.

Computes F1, precision, and recall at configurable spatial matching tolerances
(default: 20, 30, 40, 50 metres) for PV pipeline outputs. Supports both
single-condition evaluation and batch mode via YAML specification.

This script consolidates buffer sensitivity analysis that was previously done
ad-hoc. It reuses the spatial matching infrastructure in ``lib_advanced_metrics``
and the PV data loading from ``evaluate_pv_results``.

Usage — single condition:

    python scripts/analyse_pv_buffer_sensitivity.py \\
        --probabilities outputs/h11/pv-diag-384/verified/flash-high-text-16of30/probabilities.json \\
        --manifest outputs/h11/pv-diag-384/verified/flash-high-text-16of30/candidate_manifest.json \\
        --threshold 0.20 \\
        --label "Flash HIGH text 16-of-30 + PV" \\
        --output-dir results/buffer-sensitivity/flash-high-text-16of30

Usage — batch mode:

    python scripts/analyse_pv_buffer_sensitivity.py \\
        --batch conditions.yaml \\
        --output-dir results/buffer-sensitivity

Batch YAML format:

    conditions:
      - label: "Flash HIGH text 16-of-30 + PV"
        probabilities: "outputs/.../probabilities.json"
        manifest: "outputs/.../candidate_manifest.json"
        threshold: 0.20

Outputs (per condition):
    - buffer_sensitivity.json — structured results with metadata
    - buffer_sensitivity.csv — one row per buffer distance

Outputs (batch mode, additionally):
    - buffer_sensitivity_summary.csv — all conditions × buffers
    - buffer_sensitivity_summary.md — formatted markdown table

FAIR4RS Compliance:
    - Findable: Descriptive filename, versioned, comprehensive metadata
    - Accessible: Standalone CLI with standard I/O formats
    - Interoperable: JSON/CSV outputs, reuses shared library functions
    - Reusable: Fully parameterised, batch mode, documented arguments

Author: Shawn Ross & Claude (Anthropic)
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import yaml

# Project imports
import sys

# Ensure scripts/ is on the path for sibling imports
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib_advanced_metrics import (  # noqa: E402
    bootstrap_ci,
    calculate_f1_internal,
)
from evaluate_pv_results import (  # noqa: E402
    build_candidate_gdf,
    load_probabilities,
)

__version__ = "1.0.0"

logger = logging.getLogger(__name__)

# Default paths
BASE_DIR = _SCRIPT_DIR.parent
_VECTORS_DIR = BASE_DIR / "inputs" / "vectors"
_BOUNDS_PATH = _VECTORS_DIR / "bounds" / "full_evaluation_bounds.geojson"
_REF_PATH = _VECTORS_DIR / "references" / "mounds-reference.geojson"
_TARGET_CRS = "EPSG:32635"

# Default buffer distances in metres
DEFAULT_BUFFERS = [20, 30, 40, 50]


def evaluate_condition_at_buffers(
    probabilities: dict[str, dict],
    manifest: dict,
    threshold: float,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
    n_bootstrap: int = 1000,
    seed: int = 42,
    label: str = "",
) -> dict:
    """Evaluate a PV condition at multiple spatial buffer distances.

    Args:
        probabilities: Dict mapping candidate IDs to probability dicts.
        manifest: Candidate manifest with coordinates and source tiles.
        threshold: Verifier probability threshold for accepting candidates.
        gdf_ref: GeoDataFrame of ground truth reference mounds.
        gdf_bounds: GeoDataFrame of evaluation tile boundaries.
        buffers: List of buffer distances in metres to evaluate.
        n_bootstrap: Number of bootstrap iterations for CIs.
        seed: Random seed for reproducibility.
        label: Human-readable condition label.

    Returns:
        Dict with metadata and per-buffer results including F1, precision,
        recall, and bootstrap confidence intervals.
    """
    # Build detection GeoDataFrame at the given threshold
    gdf_det = build_candidate_gdf(manifest, probabilities, threshold)
    n_accepted = len(gdf_det)

    logger.info(
        "%s: %d candidates accepted at threshold %.2f",
        label or "Condition", n_accepted, threshold,
    )

    buffer_results = []
    for buffer_m in buffers:
        if n_accepted == 0:
            buffer_results.append({
                "buffer_metres": buffer_m,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "ci": {},
            })
            continue

        # Point estimate
        precision, recall, f1 = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_m,
        )

        # Bootstrap CIs
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=n_bootstrap,
            random_seed=seed,
            buffer_metres=buffer_m,
        )

        buffer_results.append({
            "buffer_metres": buffer_m,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "ci": {
                metric: {
                    "mean": round(ci[metric]["mean"], 4),
                    "lower": round(ci[metric]["ci_lower"], 4),
                    "upper": round(ci[metric]["ci_upper"], 4),
                }
                for metric in ["f1", "precision", "recall"]
            },
        })

        logger.info(
            "  %dm: F1=%.4f [%.3f, %.3f], P=%.4f, R=%.4f",
            buffer_m, f1,
            ci["f1"]["ci_lower"], ci["f1"]["ci_upper"],
            precision, recall,
        )

    return {
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "label": label,
        "threshold": threshold,
        "n_accepted": n_accepted,
        "ground_truth_mounds": len(gdf_ref),
        "evaluation_tiles": len(gdf_bounds),
        "bootstrap_iterations": n_bootstrap,
        "seed": seed,
        "buffers": buffer_results,
    }


def write_condition_outputs(
    result: dict,
    output_dir: Path,
) -> None:
    """Write per-condition JSON and CSV outputs.

    Args:
        result: Result dict from evaluate_condition_at_buffers().
        output_dir: Directory for output files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = output_dir / "buffer_sensitivity.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    logger.info("JSON written: %s", json_path)

    # CSV
    csv_path = output_dir / "buffer_sensitivity.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "buffer_metres", "f1", "f1_ci_lower", "f1_ci_upper",
            "precision", "recall", "n_accepted",
        ])
        for buf in result["buffers"]:
            ci_f1 = buf.get("ci", {}).get("f1", {})
            writer.writerow([
                buf["buffer_metres"],
                buf["f1"],
                ci_f1.get("lower", ""),
                ci_f1.get("upper", ""),
                buf["precision"],
                buf["recall"],
                result["n_accepted"],
            ])
    logger.info("CSV written: %s", csv_path)


def write_batch_summary(
    all_results: list[dict],
    output_dir: Path,
) -> None:
    """Write batch summary CSV and Markdown.

    Args:
        all_results: List of result dicts, one per condition.
        output_dir: Directory for summary files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Summary CSV — one row per condition × buffer
    csv_path = output_dir / "buffer_sensitivity_summary.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "label", "threshold", "buffer_metres",
            "f1", "f1_ci_lower", "f1_ci_upper",
            "precision", "recall", "n_accepted",
        ])
        for result in all_results:
            for buf in result["buffers"]:
                ci_f1 = buf.get("ci", {}).get("f1", {})
                writer.writerow([
                    result["label"],
                    result["threshold"],
                    buf["buffer_metres"],
                    buf["f1"],
                    ci_f1.get("lower", ""),
                    ci_f1.get("upper", ""),
                    buf["precision"],
                    buf["recall"],
                    result["n_accepted"],
                ])
    logger.info("Summary CSV written: %s", csv_path)

    # Summary Markdown
    md_path = output_dir / "buffer_sensitivity_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# PV Buffer Sensitivity Summary\n\n")
        f.write(f"**Generated**: {datetime.now(timezone.utc).isoformat()}  \n")
        f.write(f"**Conditions**: {len(all_results)}  \n")
        buffers_str = ", ".join(
            str(b["buffer_metres"])
            for b in all_results[0]["buffers"]
        ) if all_results else "—"
        f.write(f"**Buffers**: {buffers_str} m  \n\n")

        # Table header
        f.write("| Condition | t |")
        if all_results:
            for buf in all_results[0]["buffers"]:
                f.write(f" F1@{buf['buffer_metres']}m |")
                f.write(f" P@{buf['buffer_metres']}m |")
                f.write(f" R@{buf['buffer_metres']}m |")
        f.write(" n |\n")

        # Separator
        f.write("|---|---|")
        if all_results:
            for _buf in all_results[0]["buffers"]:
                f.write("---|---|---|")
        f.write("---|\n")

        # Data rows
        for result in all_results:
            f.write(f"| {result['label']} | {result['threshold']} |")
            for buf in result["buffers"]:
                f.write(f" {buf['f1']:.3f} |")
                f.write(f" {buf['precision']:.3f} |")
                f.write(f" {buf['recall']:.3f} |")
            f.write(f" {result['n_accepted']} |\n")

        f.write("\n")
    logger.info("Summary Markdown written: %s", md_path)


def load_batch_yaml(batch_path: Path) -> list[dict]:
    """Load batch condition specifications from YAML.

    Args:
        batch_path: Path to the batch YAML file.

    Returns:
        List of condition dicts with keys: label, probabilities,
        manifest, threshold.
    """
    with open(batch_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    conditions = data.get("conditions", [])
    logger.info("Loaded %d conditions from %s", len(conditions), batch_path)
    return conditions


def main() -> None:
    """Run PV buffer sensitivity analysis."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate PV pipeline results at multiple spatial buffer "
            "distances. Computes F1, precision, and recall with bootstrap "
            "confidence intervals at each buffer tolerance."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )

    # Mode: single condition or batch
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--probabilities", type=Path,
        help="Path to probabilities.json (single-condition mode)",
    )
    mode_group.add_argument(
        "--batch", type=Path,
        help="Path to batch YAML file (batch mode)",
    )

    # Single-condition arguments
    parser.add_argument(
        "--manifest", type=Path,
        help="Path to candidate_manifest.json (required in single mode)",
    )
    parser.add_argument(
        "--threshold", type=float,
        help="Verifier probability threshold (required in single mode)",
    )
    parser.add_argument(
        "--label", type=str, default=None,
        help="Human-readable condition label (default: directory name)",
    )

    # Common arguments
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for results",
    )
    parser.add_argument(
        "--buffers", type=int, nargs="+", default=DEFAULT_BUFFERS,
        help=(
            "Buffer distances in metres "
            f"(default: {' '.join(map(str, DEFAULT_BUFFERS))})"
        ),
    )
    parser.add_argument(
        "--bounds", type=Path, default=_BOUNDS_PATH,
        help=(
            "Evaluation bounds GeoJSON "
            f"(default: {_BOUNDS_PATH.relative_to(BASE_DIR)})"
        ),
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=_REF_PATH,
        help=(
            "Ground truth reference GeoJSON "
            f"(default: {_REF_PATH.relative_to(BASE_DIR)})"
        ),
    )
    parser.add_argument(
        "--bootstrap", type=int, default=1000,
        help="Number of bootstrap iterations (default: 1000)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress console output",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Validate single-mode requirements
    if args.probabilities and (args.manifest is None or args.threshold is None):
        parser.error(
            "--manifest and --threshold are required in single-condition mode"
        )

    # Load reference data (shared across conditions)
    logger.info("Loading ground truth: %s", args.ground_truth)
    gdf_ref = gpd.read_file(args.ground_truth)
    logger.info("Loading bounds: %s", args.bounds)
    gdf_bounds = gpd.read_file(args.bounds)
    logger.info(
        "Reference: %d mounds, %d evaluation tiles",
        len(gdf_ref), len(gdf_bounds),
    )

    # Build condition list
    if args.batch:
        # Batch mode
        conditions = load_batch_yaml(args.batch)
    else:
        # Single-condition mode
        label = args.label or args.probabilities.parent.name
        conditions = [{
            "label": label,
            "probabilities": str(args.probabilities),
            "manifest": str(args.manifest),
            "threshold": args.threshold,
        }]

    # Evaluate each condition
    all_results = []
    for i, cond in enumerate(conditions, 1):
        label = cond["label"]
        prob_path = Path(cond["probabilities"])
        manifest_path = Path(cond["manifest"])
        threshold = float(cond["threshold"])

        logger.info(
            "[%d/%d] %s (threshold=%.2f)",
            i, len(conditions), label, threshold,
        )

        # Load data
        probabilities = load_probabilities(prob_path)
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        # Evaluate at all buffer distances
        result = evaluate_condition_at_buffers(
            probabilities=probabilities,
            manifest=manifest,
            threshold=threshold,
            gdf_ref=gdf_ref,
            gdf_bounds=gdf_bounds,
            buffers=args.buffers,
            n_bootstrap=args.bootstrap,
            seed=args.seed,
            label=label,
        )
        all_results.append(result)

        # Write per-condition outputs
        if args.batch:
            # In batch mode, use label-derived subdirectory
            safe_label = label.lower().replace(" ", "-").replace("+", "")
            safe_label = "".join(
                c for c in safe_label if c.isalnum() or c in "-_"
            )
            cond_dir = args.output_dir / safe_label
        else:
            cond_dir = args.output_dir

        write_condition_outputs(result, cond_dir)

    # Write batch summary if multiple conditions
    if len(all_results) > 1:
        write_batch_summary(all_results, args.output_dir)

    logger.info("Done: %d conditions evaluated", len(all_results))


if __name__ == "__main__":
    main()
