#!/usr/bin/env python3
"""Evaluate tile-level MCC for any condition type.

Computes tile-level MCC (Matthews Correlation Coefficient), sensitivity,
and specificity with 95% bootstrap confidence intervals. Supports three
condition types:

- **n1**: Raw detection GeoJSON files (single-pass N=1 runs)
- **consensus**: Consensus-voted detections reconstructed from multi-run
  detection data via clustering and vote thresholding
- **pv**: Proposer-verifier pipeline outputs filtered by probability
  threshold

All condition types produce a detection GeoDataFrame with `source_tile`
and `geometry` columns, which feeds into the same tile-level
classification and bootstrap functions.

Usage:
    # Batch mode (recommended)
    python scripts/evaluate_tile_mcc.py \\
        --batch configs/mcc-eval-consensus-pv.yaml \\
        --output-dir results/paper-eval/mcc/consensus-pv

    # Single consensus condition
    python scripts/evaluate_tile_mcc.py \\
        --type consensus \\
        --study-dir outputs/h11/pv-diag-384/flash-high-text-n5 \\
        --temperature text-t0.7 --pool-size 30 --vote-threshold 26 \\
        --label "Flash HIGH text 26-of-30" \\
        --output-dir results/mcc-test

    # Single PV condition
    python scripts/evaluate_tile_mcc.py \\
        --type pv \\
        --probabilities outputs/.../probabilities.json \\
        --manifest outputs/.../candidate_manifest.json \\
        --pv-threshold 0.20 \\
        --label "Flash HIGH text 16-of-30 + PV" \\
        --output-dir results/mcc-test

Created: 2026-03-28
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib_advanced_metrics import (  # noqa: E402
    DEFAULT_CRS,
    bootstrap_tile_classification_ci,
    calculate_tile_classification,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

__version__ = "1.0.0"

# ── Defaults ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_GROUND_TRUTH = (
    PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
)
DEFAULT_BOUNDS = (
    PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
)
DEFAULT_BOOTSTRAP = 1000
DEFAULT_SEED = 42


# ── Helpers ───────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert label to filesystem-safe directory name."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def load_geojson(
    path: Path,
    target_crs: str = DEFAULT_CRS,
) -> gpd.GeoDataFrame:
    """Load GeoJSON and ensure target CRS."""
    gdf = gpd.read_file(path)
    if gdf.empty:
        return gdf
    if gdf.crs is None:
        gdf.set_crs(target_crs, inplace=True)
    elif str(gdf.crs) != target_crs:
        gdf = gdf.to_crs(target_crs)
    return gdf


def _safe_round(
    val: float | None,
    digits: int = 4,
) -> float | None:
    """Round a value, preserving None for undefined metrics.

    Returns None when the input is None (e.g., MCC undefined due to
    a degenerate confusion matrix). Downstream consumers should handle
    None explicitly rather than assuming 0.0.
    """
    return round(val, digits) if val is not None else None


# ── GeoDataFrame builders ────────────────────────────────────────────

def build_n1_gdf(
    detections_dir: Path,
    glob_pattern: str,
    gdf_bounds: gpd.GeoDataFrame,
) -> list[gpd.GeoDataFrame]:
    """Load N=1 detection GeoJSON files as GeoDataFrames.

    Args:
        detections_dir: Directory containing run subdirectories.
        glob_pattern: Glob pattern for finding GeoJSON files.
        gdf_bounds: Tile boundaries for source_tile assignment.

    Returns:
        List of GeoDataFrames, one per run.
    """
    det_files = sorted(detections_dir.glob(glob_pattern))
    if not det_files:
        logger.warning("No files matching '%s' in %s", glob_pattern, detections_dir)
        return []

    gdfs = []
    for det_path in det_files:
        gdf = load_geojson(det_path)
        if gdf.empty:
            continue
        if "source_tile" not in gdf.columns:
            joined = gpd.sjoin(
                gdf, gdf_bounds[["tile_name", "geometry"]],
                how="left", predicate="intersects",
            )
            # Deduplicate: detections on tile boundaries may match
            # multiple tiles; keep first match only.
            joined = joined[~joined.index.duplicated(keep="first")]
            gdf["source_tile"] = joined["tile_name"]
        gdfs.append(gdf)
    return gdfs


def build_consensus_gdf(
    study_dir: Path,
    temperature: str,
    pool_size: int,
    vote_threshold: int,
    gdf_bounds: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Build detection GeoDataFrame from consensus voting.

    Args:
        study_dir: Base directory containing temperature condition dirs.
        temperature: Temperature condition label (e.g., 'text-t0.7').
        pool_size: Number of runs to pool (N).
        vote_threshold: Minimum votes to accept a detection.
        gdf_bounds: Tile boundaries for source_tile assignment.

    Returns:
        GeoDataFrame of consensus-filtered detections.
    """
    from scripts.analyse_consensus_sweep import (
        consensus_to_gdf,
        precompute_clusters,
    )
    from scripts.merge_passes import apply_threshold

    clusters_dict = precompute_clusters(
        study_dir, [temperature], [pool_size],
    )
    clusters = clusters_dict.get((temperature, pool_size), [])
    if not clusters:
        logger.warning(
            "No clusters for %s N=%d in %s",
            temperature, pool_size, study_dir,
        )
        return gpd.GeoDataFrame(
            columns=["source_tile", "geometry"],
            geometry="geometry", crs=DEFAULT_CRS,
        )

    consensus_fc = apply_threshold(clusters, vote_threshold, pool_size)
    gdf_det = consensus_to_gdf(consensus_fc, gdf_bounds)
    return gdf_det


def build_pv_gdf(
    probabilities_path: Path,
    manifest_path: Path,
    pv_threshold: float,
) -> gpd.GeoDataFrame:
    """Build detection GeoDataFrame from PV pipeline output.

    Args:
        probabilities_path: Path to probabilities.json.
        manifest_path: Path to candidate_manifest.json.
        pv_threshold: Minimum probability to accept.

    Returns:
        GeoDataFrame of probability-filtered detections.
    """
    from scripts.evaluate_pv_results import (
        build_candidate_gdf,
        load_probabilities,
    )

    # Auto-detect consensus.json for multi-iteration PV results
    consensus_path = probabilities_path.parent / "consensus.json"
    if not consensus_path.exists():
        consensus_path = None
    probabilities = load_probabilities(
        probabilities_path, consensus_path=consensus_path,
    )
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    gdf_det = build_candidate_gdf(manifest, probabilities, pv_threshold)
    return gdf_det


# ── MCC evaluation ────────────────────────────────────────────────────

def evaluate_mcc(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    n_bootstrap: int = DEFAULT_BOOTSTRAP,
    seed: int = DEFAULT_SEED,
    label: str = "",
) -> dict:
    """Compute tile-level MCC with bootstrap CIs.

    Args:
        gdf_det: Detection GeoDataFrame with source_tile.
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Tile boundaries GeoDataFrame.
        n_bootstrap: Bootstrap iterations.
        seed: Random seed.
        label: Human-readable condition label.

    Returns:
        Dict with confusion matrix, MCC, sensitivity, specificity
        and bootstrap CIs.
    """
    # Point estimate
    tile_class = calculate_tile_classification(
        gdf_det, gdf_ref, gdf_bounds,
    )

    # Bootstrap CIs
    tile_ci = bootstrap_tile_classification_ci(
        gdf_det, gdf_ref, gdf_bounds,
        n_iterations=n_bootstrap,
        random_seed=seed,
    )

    result = {
        "label": label,
        "n_detections": len(gdf_det),
        "confusion": {
            "tp": tile_class["tp"],
            "tn": tile_class["tn"],
            "fp": tile_class["fp"],
            "fn": tile_class["fn"],
        },
        "n_tiles": tile_class["n_tiles"],
        "n_populated": tile_class["n_populated"],
        "n_empty": tile_class["n_empty"],
    }

    for metric in ["mcc", "sensitivity", "specificity"]:
        ci = tile_ci.get(metric, {})
        result[metric] = {
            "point": _safe_round(tile_class.get(metric)),
            "mean": _safe_round(ci.get("mean")),
            "ci_lower": _safe_round(ci.get("ci_lower")),
            "ci_upper": _safe_round(ci.get("ci_upper")),
        }

    # Use _safe_round for logging to avoid TypeError on None values
    # (MCC/sensitivity/specificity can be None when the confusion
    # matrix has a zero row or column sum).
    logger.info(
        "  %s: MCC=%.3f [%.3f, %.3f], Sens=%.3f, Spec=%.3f, "
        "TP=%d TN=%d FP=%d FN=%d (%d det)",
        label,
        _safe_round(tile_class["mcc"], 3),
        _safe_round(tile_ci["mcc"].get("ci_lower"), 3),
        _safe_round(tile_ci["mcc"].get("ci_upper"), 3),
        _safe_round(tile_class["sensitivity"], 3),
        _safe_round(tile_class["specificity"], 3),
        tile_class["tp"], tile_class["tn"],
        tile_class["fp"], tile_class["fn"],
        len(gdf_det),
    )

    return result


# ── Output ────────────────────────────────────────────────────────────

def write_condition_output(result: dict, output_dir: Path) -> None:
    """Write per-condition MCC result as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "mcc.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    logger.info("  Written: %s", json_path)


def write_batch_summary(
    all_results: list[dict],
    output_dir: Path,
    metadata: dict | None = None,
) -> None:
    """Write consolidated MCC batch summary."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sort by MCC descending (None values sort to bottom)
    sorted_results = sorted(
        all_results,
        key=lambda r: r.get("mcc", {}).get("point") or -1,
        reverse=True,
    )

    # CSV
    csv_path = output_dir / "batch_mcc_summary.csv"
    fieldnames = [
        "label", "n_detections",
        "mcc", "mcc_ci_lower", "mcc_ci_upper",
        "sensitivity", "sens_ci_lower", "sens_ci_upper",
        "specificity", "spec_ci_lower", "spec_ci_upper",
        "tp", "tn", "fp", "fn",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in sorted_results:
            writer.writerow({
                "label": r["label"],
                "n_detections": r["n_detections"],
                "mcc": r["mcc"]["point"],
                "mcc_ci_lower": r["mcc"]["ci_lower"],
                "mcc_ci_upper": r["mcc"]["ci_upper"],
                "sensitivity": r["sensitivity"]["point"],
                "sens_ci_lower": r["sensitivity"]["ci_lower"],
                "sens_ci_upper": r["sensitivity"]["ci_upper"],
                "specificity": r["specificity"]["point"],
                "spec_ci_lower": r["specificity"]["ci_lower"],
                "spec_ci_upper": r["specificity"]["ci_upper"],
                **r["confusion"],
            })
    logger.info("Batch CSV: %s (%d rows)", csv_path, len(sorted_results))

    # JSON
    json_path = output_dir / "batch_mcc_summary.json"
    output = {
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_conditions": len(sorted_results),
    }
    if metadata:
        output["metadata"] = metadata
    output["results"] = sorted_results
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logger.info("Batch JSON: %s", json_path)

    # Markdown
    md_path = output_dir / "batch_mcc_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Tile-Level MCC Summary\n\n")
        f.write(
            f"**Generated**: "
            f"{datetime.now(timezone.utc).isoformat()}  \n",
        )
        f.write(f"**Conditions**: {len(sorted_results)}  \n")
        if metadata:
            desc = metadata.get("description", "")
            if desc:
                f.write(f"**Description**: {desc}  \n")
        f.write("\n")

        # Table
        f.write(
            "| # | Condition | Det | MCC [95% CI] "
            "| Sens [95% CI] | Spec [95% CI] "
            "| TP | TN | FP | FN |\n",
        )
        f.write(
            "|---|---|---|---|---|---|---|---|---|---|\n",
        )
        def _fmt(val: float | None) -> str:
            """Format a metric value, showing 'N/A' for None."""
            return f"{val:.3f}" if val is not None else "N/A"

        for i, r in enumerate(sorted_results, 1):
            mcc = r["mcc"]
            sens = r["sensitivity"]
            spec = r["specificity"]
            c = r["confusion"]
            f.write(
                f"| {i} | {r['label']} | {r['n_detections']} "
                f"| {_fmt(mcc['point'])} "
                f"[{_fmt(mcc['ci_lower'])}, {_fmt(mcc['ci_upper'])}] "
                f"| {_fmt(sens['point'])} "
                f"[{_fmt(sens['ci_lower'])}, {_fmt(sens['ci_upper'])}] "
                f"| {_fmt(spec['point'])} "
                f"[{_fmt(spec['ci_lower'])}, {_fmt(spec['ci_upper'])}] "
                f"| {c['tp']} | {c['tn']} | {c['fp']} | {c['fn']} |\n",
            )
        f.write("\n")
    logger.info("Batch Markdown: %s", md_path)


# ── Batch mode ────────────────────────────────────────────────────────

def load_batch_yaml(path: Path) -> tuple[dict, list[dict]]:
    """Load batch YAML spec and merge defaults."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    defaults = data.get("defaults", {})
    metadata = data.get("metadata", {})
    conditions = data.get("conditions", [])

    if not conditions:
        raise ValueError(f"No conditions in {path}")

    # Resolve paths relative to PROJECT_ROOT
    for key in ["bounds", "ground_truth"]:
        if key in defaults and not Path(defaults[key]).is_absolute():
            defaults[key] = str(PROJECT_ROOT / defaults[key])

    resolved = []
    for cond in conditions:
        merged = {**defaults, **cond}
        for key in ["bounds", "ground_truth", "study_dir",
                     "probabilities", "manifest", "detections_dir"]:
            val = merged.get(key)
            if val and not Path(val).is_absolute():
                merged[key] = str(PROJECT_ROOT / val)
        resolved.append(merged)

    if metadata:
        defaults["_metadata"] = metadata

    logger.info("Loaded %d conditions from %s", len(resolved), path)
    return defaults, resolved


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> int:
    """Run tile-level MCC evaluation."""
    parser = argparse.ArgumentParser(
        description=(
            "Compute tile-level MCC with bootstrap CIs for "
            "N=1, consensus, or PV conditions."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--batch", type=Path,
        help="YAML batch spec (overrides all other input args).",
    )
    parser.add_argument("--type", choices=["n1", "consensus", "pv"])
    parser.add_argument("--study-dir", type=Path)
    parser.add_argument("--temperature", type=str)
    parser.add_argument("--pool-size", type=int)
    parser.add_argument("--vote-threshold", type=int)
    parser.add_argument("--probabilities", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--pv-threshold", type=float)
    parser.add_argument("--detections-dir", type=Path)
    parser.add_argument(
        "--glob", default="*/detections_*.geojson",
    )
    parser.add_argument("--label", type=str, default="condition")
    parser.add_argument(
        "--bounds", type=Path, default=DEFAULT_BOUNDS,
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=DEFAULT_GROUND_TRUTH,
    )
    parser.add_argument(
        "--bootstrap", type=int, default=DEFAULT_BOOTSTRAP,
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output-dir", type=Path, required=True)

    args = parser.parse_args()

    if args.batch:
        return _run_batch(args)
    return _run_single(args)


def _run_single(args: argparse.Namespace) -> int:
    """Evaluate a single condition from CLI args."""
    gdf_ref = load_geojson(args.ground_truth)
    gdf_bounds = load_geojson(args.bounds)

    cond_type = args.type
    if cond_type == "consensus":
        gdf_det = build_consensus_gdf(
            args.study_dir, args.temperature,
            args.pool_size, args.vote_threshold,
            gdf_bounds,
        )
    elif cond_type == "pv":
        gdf_det = build_pv_gdf(
            args.probabilities, args.manifest, args.pv_threshold,
        )
    elif cond_type == "n1":
        gdfs = build_n1_gdf(
            args.detections_dir, args.glob, gdf_bounds,
        )
        if not gdfs:
            logger.error("No detection files found.")
            return 1
        # Use first run for MCC (or average later)
        gdf_det = gdfs[0]
    else:
        logger.error("--type is required for single-condition mode.")
        return 1

    result = evaluate_mcc(
        gdf_det, gdf_ref, gdf_bounds,
        n_bootstrap=args.bootstrap, seed=args.seed,
        label=args.label,
    )
    write_condition_output(result, args.output_dir)
    return 0


def _run_batch(args: argparse.Namespace) -> int:
    """Evaluate multiple conditions from YAML batch spec."""
    defaults, conditions = load_batch_yaml(args.batch)
    metadata = defaults.get("_metadata")

    gt_path = Path(defaults.get(
        "ground_truth", str(DEFAULT_GROUND_TRUTH),
    ))
    gdf_ref = load_geojson(gt_path)
    logger.info("Ground truth: %d mounds", len(gdf_ref))

    current_bounds_path: str | None = None
    gdf_bounds: gpd.GeoDataFrame | None = None

    all_results = []
    total = len(conditions)

    for i, cond in enumerate(conditions, 1):
        label = cond.get("label", f"condition_{i}")
        cond_type = cond.get("type", "n1")
        n_bootstrap = cond.get("bootstrap", DEFAULT_BOOTSTRAP)
        seed = cond.get("seed", DEFAULT_SEED)
        bounds_path = cond.get("bounds", str(DEFAULT_BOUNDS))

        logger.info("[%d/%d] %s (type=%s)", i, total, label, cond_type)

        # Reload bounds if changed
        if bounds_path != current_bounds_path:
            gdf_bounds = load_geojson(Path(bounds_path))
            current_bounds_path = bounds_path
            logger.info("  Bounds: %d tiles", len(gdf_bounds))

        # Build detection GeoDataFrame
        try:
            if cond_type == "consensus":
                gdf_det = build_consensus_gdf(
                    Path(cond["study_dir"]),
                    cond["temperature"],
                    cond["pool_size"],
                    cond["vote_threshold"],
                    gdf_bounds,
                )
            elif cond_type == "pv":
                gdf_det = build_pv_gdf(
                    Path(cond["probabilities"]),
                    Path(cond["manifest"]),
                    cond["pv_threshold"],
                )
            elif cond_type == "n1":
                det_dir = Path(cond["detections_dir"])
                glob_pat = cond.get("glob", "*/detections_*.geojson")
                gdfs = build_n1_gdf(det_dir, glob_pat, gdf_bounds)
                if not gdfs:
                    logger.warning("  No files — skipping")
                    continue
                # For N=1 MCC, evaluate first run (deterministic
                # runs are identical; stochastic runs vary slightly).
                # Multi-run averaging is handled in evaluate_detections.py.
                gdf_det = gdfs[0]
            else:
                logger.warning("  Unknown type '%s' — skipping", cond_type)
                continue
        except Exception as e:
            logger.error("  Failed to build GeoDataFrame: %s", e)
            continue

        if gdf_det.empty:
            logger.warning("  Empty GeoDataFrame — skipping")
            continue

        # Evaluate MCC
        result = evaluate_mcc(
            gdf_det, gdf_ref, gdf_bounds,
            n_bootstrap=n_bootstrap, seed=seed,
            label=label,
        )

        # Write per-condition output
        cond_dir = args.output_dir / slugify(label)
        write_condition_output(result, cond_dir)
        all_results.append(result)

    if not all_results:
        logger.error("No conditions produced results.")
        return 1

    # Write batch summary
    write_batch_summary(all_results, args.output_dir, metadata=metadata)
    logger.info("Batch complete: %d conditions", len(all_results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
