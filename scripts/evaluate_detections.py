#!/usr/bin/env python3
"""Evaluate detection GeoJSON files against ground truth.

General-purpose evaluation script for single-pass or arbitrary detection
outputs. Computes F1, Precision, Recall with 95% bootstrap confidence
intervals at one or more spatial buffer distances. Supports evaluating
individual runs or averaging across multiple runs of the same condition.

This is the fundamental evaluation building block — other scripts
(consensus sweeps, PV threshold sweeps) build on the same library
functions but add condition-specific logic. Use this script when you
have plain detection GeoJSON files and want metrics.

Usage:
    # Single file at default 20m buffer
    python scripts/evaluate_detections.py \\
        --detections path/to/detections.geojson

    # Multiple files (averaged as independent runs of the same condition)
    python scripts/evaluate_detections.py \\
        --detections run_1/detections.geojson run_2/detections.geojson

    # Glob pattern for all runs in a directory
    python scripts/evaluate_detections.py \\
        --detections-dir outputs/retest/h11-single-pass-384-t0/brief-text-t0 \\
        --glob "*/detections_*.geojson"

    # Multiple buffer distances with custom output
    python scripts/evaluate_detections.py \\
        --detections path/to/detections.geojson \\
        --buffers 20 30 40 50 \\
        --output-dir results/my-evaluation

Created: 2026-03-27
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib_advanced_metrics import (  # noqa: E402
    DEFAULT_CRS,
    bootstrap_ci,
    bootstrap_tile_classification_ci,
    calculate_f1_internal,
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
DEFAULT_BUFFERS = [20]
DEFAULT_BOOTSTRAP = 1000
DEFAULT_SEED = 42


# ── Metadata helpers ──────────────────────────────────────────────────

# Relative script path used for provenance in the _metadata block. Fixed
# so that the recorded path is stable across invocations, regardless of
# the caller's current working directory.
_SCRIPT_RELATIVE_PATH = "scripts/evaluate_detections.py"


def _git_short_hash(repo_root: Path) -> str:
    """Return the short Git hash of HEAD, or 'unknown' on failure.

    Runs `git rev-parse --short HEAD` in the given repository root. Any
    failure mode (git not installed, not a repository, non-zero exit
    code) is mapped to the string ``"unknown"`` so that callers never
    have to handle exceptions.

    Args:
        repo_root: Path to the Git repository (typically the project
            root). The command is executed with this as its working
            directory.

    Returns:
        The short commit hash, or ``"unknown"`` if it cannot be
        determined.
    """
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, OSError):
        return "unknown"
    if proc.returncode != 0:
        return "unknown"
    value = proc.stdout.strip()
    return value or "unknown"


def _git_status(repo_root: Path) -> str:
    """Return 'clean' if the working tree is clean, else 'dirty'.

    Uses ``git status --porcelain``: an empty output indicates a clean
    tree, any non-empty output indicates uncommitted changes. If git is
    unavailable or the call fails, returns ``"unknown"`` so reviewers
    can still interpret the field.

    Args:
        repo_root: Path to the Git repository to inspect.

    Returns:
        One of ``"clean"``, ``"dirty"``, or ``"unknown"``.
    """
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, OSError):
        return "unknown"
    if proc.returncode != 0:
        return "unknown"
    return "clean" if proc.stdout.strip() == "" else "dirty"


def _serialise_cli_args(args: argparse.Namespace) -> dict[str, Any]:
    """Convert a parsed argparse Namespace into a JSON-safe dict.

    ``argparse`` may store values such as :class:`pathlib.Path` instances
    that the :mod:`json` encoder cannot handle natively. This helper
    walks the namespace once and replaces those values with plain
    strings (or lists of strings), preserving all keys exactly as the
    CLI defined them.

    Args:
        args: The parsed argparse namespace.

    Returns:
        A dict mapping option names to JSON-serialisable values.
    """
    serialised: dict[str, Any] = {}
    for key, value in vars(args).items():
        if isinstance(value, Path):
            serialised[key] = str(value)
        elif isinstance(value, list):
            serialised[key] = [
                str(item) if isinstance(item, Path) else item
                for item in value
            ]
        else:
            serialised[key] = value
    return serialised


def _build_metadata(args: argparse.Namespace) -> dict[str, Any]:
    """Build the ``_metadata`` block embedded in evaluation outputs.

    The block captures bootstrap parameters (iterations, seed, resampling
    unit), Git provenance (short HEAD hash, clean/dirty status), the
    parsed CLI arguments, and the resolved input file paths. Writing
    this alongside the metrics makes each ``evaluation.json`` file
    self-documenting — reviewers can reproduce confidence intervals
    without reading the script source.

    The schema is versioned via ``metadata_version`` so downstream
    consumers can evolve alongside future changes.

    Args:
        args: The parsed argparse namespace for this run. Expected
            attributes include ``bootstrap``, ``seed``, ``ground_truth``,
            ``bounds``, and at least one of ``detections``,
            ``detections_dir``, or ``batch``.

    Returns:
        A dict with the schema described in the module-level task
        specification. All values are JSON-serialisable.
    """
    # Resolve the input-files block from whichever input mode was used.
    # In batch mode the per-condition detection paths live inside the
    # YAML file, so we record the YAML path itself here.
    if getattr(args, "detections", None):
        detections_value: Any = [str(p) for p in args.detections]
    elif getattr(args, "detections_dir", None):
        detections_value = str(args.detections_dir)
    elif getattr(args, "batch", None):
        detections_value = str(args.batch)
    else:
        detections_value = None

    ground_truth = getattr(args, "ground_truth", None)
    bounds = getattr(args, "bounds", None)

    metadata: dict[str, Any] = {
        # ``metadata_version`` bumped to 1.1 on 2026-04-29 with the
        # introduction of the BCa bootstrap method and Mitigation 3
        # sparse-coverage flag (commit feat(bootstrap): replace percentile
        # method with BCa). Downstream consumers should treat 1.0 outputs
        # as percentile-method and 1.1+ as BCa.
        "metadata_version": "1.1",
        "script_path": _SCRIPT_RELATIVE_PATH,
        "script_git_commit": _git_short_hash(PROJECT_ROOT),
        "script_git_status": _git_status(PROJECT_ROOT),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cli_args": _serialise_cli_args(args),
        "bootstrap": {
            "n_iterations": int(getattr(args, "bootstrap", DEFAULT_BOOTSTRAP)),
            "seed": int(getattr(args, "seed", DEFAULT_SEED)),
            "resampling_unit": "tile_level",
            # Bootstrap method recorded so that downstream consumers can
            # distinguish BCa-from-1.1 outputs from the legacy percentile
            # outputs without having to read the script source.
            "method": "BCa",
            "library": "scipy.stats.bootstrap",
        },
        "input_files": {
            "detections": detections_value,
            "ground_truth": str(ground_truth) if ground_truth else None,
            "bounds": str(bounds) if bounds else None,
        },
    }
    return metadata


# ── Data loading ──────────────────────────────────────────────────────

def load_geojson(path: Path, target_crs: str = DEFAULT_CRS) -> gpd.GeoDataFrame:
    """Load a GeoJSON file and ensure it is in the target CRS.

    Args:
        path: Path to GeoJSON file.
        target_crs: Target Coordinate Reference System (default EPSG:32635).

    Returns:
        GeoDataFrame in the target CRS.
    """
    gdf = gpd.read_file(path)
    if gdf.empty:
        logger.warning("Empty GeoJSON: %s", path)
        return gdf
    if gdf.crs is None:
        gdf.set_crs(target_crs, inplace=True)
    elif str(gdf.crs) != target_crs:
        gdf = gdf.to_crs(target_crs)
    return gdf


def find_detection_files(
    detections_dir: Path,
    glob_pattern: str = "*/detections_*.geojson",
) -> list[Path]:
    """Find detection GeoJSON files in a directory using a glob pattern.

    Args:
        detections_dir: Base directory to search.
        glob_pattern: Glob pattern relative to detections_dir.

    Returns:
        Sorted list of matching file paths.
    """
    matches = sorted(detections_dir.glob(glob_pattern))
    if not matches:
        logger.warning(
            "No files matching '%s' in %s", glob_pattern, detections_dir,
        )
    return matches


# ── Evaluation ────────────────────────────────────────────────────────

def evaluate_single_run(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
    n_bootstrap: int = DEFAULT_BOOTSTRAP,
    seed: int = DEFAULT_SEED,
    label: str = "",
    compute_mcc: bool = False,
) -> dict:
    """Evaluate a single detection run at multiple buffer distances.

    Args:
        gdf_det: Detection GeoDataFrame.
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Evaluation tile boundaries GeoDataFrame.
        buffers: Buffer distances in metres.
        n_bootstrap: Bootstrap iterations for CIs.
        seed: Random seed for reproducibility.
        label: Human-readable label for this run.
        compute_mcc: If True, also compute tile-level MCC, sensitivity,
            and specificity with bootstrap CIs.

    Returns:
        Dict with metadata and per-buffer results including F1, P, R
        with bootstrap CIs. When compute_mcc is True, also includes
        a tile_classification key.
    """
    n_det = len(gdf_det)
    buffer_results = []

    for buffer_m in buffers:
        if n_det == 0:
            buffer_results.append({
                "buffer_metres": buffer_m,
                "f1": 0.0, "precision": 0.0, "recall": 0.0,
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

        # Mitigation 3 (sparse-coverage transparency): surface the coverage
        # block on each buffer entry so MD/CSV writers can suppress
        # numerically-misleading CIs while keeping the JSON copy intact for
        # downstream tooling. ``coverage_status`` is the canonical
        # human-readable flag; ``ci`` retains all numeric bounds.
        coverage = ci.get("coverage", {})
        coverage_status = coverage.get("coverage_status", "normal")
        ci_unreliable = coverage_status == "sparse_cross_grid"
        buffer_results.append({
            "buffer_metres": buffer_m,
            "f1": round(f1, 4),
            "f1_point": round(f1, 4),  # Same as ``f1`` — alias for clarity
            "f1_ci_lower": round(ci["f1"]["ci_lower"], 4),
            "f1_ci_upper": round(ci["f1"]["ci_upper"], 4),
            "f1_ci_method": ci["f1"].get("method", "BCa"),
            "precision": round(precision, 4),
            "p_point": round(precision, 4),
            "p_ci_lower": round(ci["precision"]["ci_lower"], 4),
            "p_ci_upper": round(ci["precision"]["ci_upper"], 4),
            "p_ci_method": ci["precision"].get("method", "BCa"),
            "recall": round(recall, 4),
            "r_point": round(recall, 4),
            "r_ci_lower": round(ci["recall"]["ci_lower"], 4),
            "r_ci_upper": round(ci["recall"]["ci_upper"], 4),
            "r_ci_method": ci["recall"].get("method", "BCa"),
            "coverage": coverage,
            "coverage_status": coverage_status,
            "ci_unreliable": ci_unreliable,
        })

        logger.info(
            "  %dm: F1=%.3f [%.3f, %.3f], P=%.3f [%.3f, %.3f], "
            "R=%.3f [%.3f, %.3f]%s",
            buffer_m, f1, ci["f1"]["ci_lower"], ci["f1"]["ci_upper"],
            precision, ci["precision"]["ci_lower"],
            ci["precision"]["ci_upper"],
            recall, ci["recall"]["ci_lower"], ci["recall"]["ci_upper"],
            (
                f" [sparse coverage: {coverage.get('zero_fraction', 0):.1%} zero-tiles]"
                if ci_unreliable else ""
            ),
        )

    # Cell-level rollup (Mitigation 3, per-cell flag): if ANY buffer's
    # bootstrap distribution flagged sparse coverage, flag the whole cell.
    # This gives consumers a one-shot boolean per cell without scanning
    # individual buffer entries; useful for paper tables and analysis
    # notebooks. The 20 m and 30 m buffers can in principle differ; the
    # any-buffer rule treats the worst case as the cell's status.
    cell_ci_unreliable = any(
        buf.get("ci_unreliable", False) for buf in buffer_results
    )
    cell_coverage_status = (
        "sparse_cross_grid" if cell_ci_unreliable else "normal"
    )

    result = {
        "label": label,
        "n_detections": n_det,
        "buffers": buffer_results,
        "ci_unreliable_any_buffer": cell_ci_unreliable,
        "coverage_status": cell_coverage_status,
    }

    # Tile-level MCC (optional)
    if compute_mcc and n_det > 0:
        tile_class = calculate_tile_classification(
            gdf_det, gdf_ref, gdf_bounds,
        )
        tile_ci = bootstrap_tile_classification_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=n_bootstrap, random_seed=seed,
        )
        def _safe_round(val: float | None, digits: int = 4) -> float:
            """Round a value, returning 0.0 for None (undefined MCC)."""
            return round(val, digits) if val is not None else 0.0

        # ``point`` fields carry the deterministic estimate computed
        # across all tiles (no bootstrap). The §7.5 verifier fix needs a
        # named field that is invariant to bootstrap iteration count;
        # ``mean`` is the bootstrap distribution mean and is not
        # deterministic across seed changes.
        result["tile_classification"] = {
            "confusion": {
                "tp": tile_class["tp"],
                "tn": tile_class["tn"],
                "fp": tile_class["fp"],
                "fn": tile_class["fn"],
            },
            "mcc": {
                "point": _safe_round(tile_class.get("mcc")),
                "mean": _safe_round(tile_ci["mcc"]["mean"]),
                "ci_lower": _safe_round(tile_ci["mcc"]["ci_lower"]),
                "ci_upper": _safe_round(tile_ci["mcc"]["ci_upper"]),
                "method": tile_ci["mcc"].get("method", "BCa"),
            },
            "sensitivity": {
                "point": _safe_round(tile_class.get("sensitivity")),
                "mean": _safe_round(tile_ci["sensitivity"]["mean"]),
                "ci_lower": _safe_round(
                    tile_ci["sensitivity"]["ci_lower"],
                ),
                "ci_upper": _safe_round(
                    tile_ci["sensitivity"]["ci_upper"],
                ),
                "method": tile_ci["sensitivity"].get("method", "BCa"),
            },
            "specificity": {
                "point": _safe_round(tile_class.get("specificity")),
                "mean": _safe_round(tile_ci["specificity"]["mean"]),
                "ci_lower": _safe_round(
                    tile_ci["specificity"]["ci_lower"],
                ),
                "ci_upper": _safe_round(
                    tile_ci["specificity"]["ci_upper"],
                ),
                "method": tile_ci["specificity"].get("method", "BCa"),
            },
        }
        logger.info(
            "  MCC=%.3f [%.3f, %.3f], Sens=%.3f, Spec=%.3f",
            tile_class["mcc"],
            tile_ci["mcc"]["ci_lower"], tile_ci["mcc"]["ci_upper"],
            tile_class["sensitivity"], tile_class["specificity"],
        )

    return result


def evaluate_multi_run_mean(
    run_results: list[dict],
    label: str = "",
) -> dict:
    """Compute mean metrics across multiple independent runs.

    For each buffer distance, averages the point estimates and CIs
    across runs. This gives the expected single-run performance.

    Args:
        run_results: List of per-run result dicts from evaluate_single_run().
        label: Human-readable label for the averaged condition.

    Returns:
        Dict with averaged metrics per buffer distance.
    """
    n_runs = len(run_results)
    if n_runs == 0:
        return {"label": label, "n_runs": 0, "buffers": []}

    # Group by buffer distance
    from collections import defaultdict
    by_buffer: dict[int, list[dict]] = defaultdict(list)
    for result in run_results:
        for buf_entry in result["buffers"]:
            by_buffer[buf_entry["buffer_metres"]].append(buf_entry)

    avg_buffers = []
    metric_keys = [
        "f1", "f1_ci_lower", "f1_ci_upper",
        "precision", "p_ci_lower", "p_ci_upper",
        "recall", "r_ci_lower", "r_ci_upper",
    ]

    for buffer_m in sorted(by_buffer.keys()):
        entries = by_buffer[buffer_m]
        avg = {"buffer_metres": buffer_m}
        for key in metric_keys:
            values = [e[key] for e in entries if key in e]
            avg[key] = round(float(np.mean(values)), 4) if values else 0.0
        avg_buffers.append(avg)

        logger.info(
            "  Mean across %d runs @ %dm: F1=%.3f [%.3f, %.3f], "
            "P=%.3f, R=%.3f",
            n_runs, buffer_m,
            avg["f1"], avg["f1_ci_lower"], avg["f1_ci_upper"],
            avg["precision"], avg["recall"],
        )

    result = {
        "label": label,
        "n_runs": n_runs,
        "buffers": avg_buffers,
    }

    # Average tile-level MCC across runs (if computed)
    mcc_results = [
        r["tile_classification"] for r in run_results
        if "tile_classification" in r
    ]
    if mcc_results:
        avg_mcc: dict[str, dict] = {}
        for metric in ["mcc", "sensitivity", "specificity"]:
            values = [m[metric] for m in mcc_results if metric in m]
            if values:
                avg_mcc[metric] = {
                    "mean": round(float(np.mean(
                        [v["mean"] for v in values],
                    )), 4),
                    "ci_lower": round(float(np.mean(
                        [v["ci_lower"] for v in values],
                    )), 4),
                    "ci_upper": round(float(np.mean(
                        [v["ci_upper"] for v in values],
                    )), 4),
                }
        # Use first run's confusion matrix as representative
        avg_mcc["confusion"] = mcc_results[0].get("confusion", {})
        result["tile_classification"] = avg_mcc

        logger.info(
            "  Mean MCC across %d runs: %.3f [%.3f, %.3f]",
            len(mcc_results),
            avg_mcc["mcc"]["mean"],
            avg_mcc["mcc"]["ci_lower"],
            avg_mcc["mcc"]["ci_upper"],
        )

    return result


# ── Output ────────────────────────────────────────────────────────────

def write_outputs(
    results: dict,
    run_results: list[dict] | None,
    output_dir: Path,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Write evaluation results as JSON, CSV, and Markdown.

    Args:
        results: Averaged or single-run results dict.
        run_results: Optional list of per-run results (for multi-run).
        output_dir: Output directory.
        metadata: Optional ``_metadata`` block describing how the
            evaluation was generated (bootstrap config, git provenance,
            CLI args, input files). When provided, it is written as a
            top-level ``_metadata`` key in ``evaluation.json`` so the
            JSON output is self-documenting.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON — key order preserves backward compatibility: existing
    # consumers that look up ``version`` / ``summary`` continue to work,
    # and the new ``_metadata`` block is additive.
    output: dict[str, Any] = {
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": results,
    }
    if metadata is not None:
        output["_metadata"] = metadata
    if run_results:
        output["per_run"] = run_results

    json_path = output_dir / "evaluation.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logger.info("JSON written: %s", json_path)

    # CSV
    # MCC is buffer-invariant (computed at the tile level), so when the
    # ``tile_classification`` block is present we repeat the same MCC,
    # sensitivity, and specificity values across every buffer row for
    # tabular convenience. ``has_mcc`` gates both the wider CSV columns
    # and the wider Markdown header below so legacy outputs without MCC
    # remain byte-identical.
    tc = results.get("tile_classification") or {}
    has_mcc = bool(tc)

    # Mitigation 3 (sparse coverage): emit machine-readable diagnostics
    # columns alongside the numeric CI bounds. Downstream consumers that
    # only read the numeric columns continue to work; consumers that
    # respect the flag can hide unreliable bounds at render time. The
    # boolean is the contract: "do you trust these CIs?".
    has_coverage = any(
        "coverage_status" in buf for buf in results["buffers"]
    )

    csv_path = output_dir / "evaluation.csv"
    fieldnames = [
        "label", "buffer_metres",
        "f1", "f1_ci_lower", "f1_ci_upper",
        "precision", "p_ci_lower", "p_ci_upper",
        "recall", "r_ci_lower", "r_ci_upper",
    ]
    if has_mcc:
        fieldnames.extend([
            "mcc", "mcc_ci_lower", "mcc_ci_upper",
            "sensitivity", "specificity",
        ])
    if has_coverage:
        fieldnames.extend([
            "coverage_status", "ci_unreliable",
            "ci_zero_fraction", "ci_n_tiles",
        ])
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for buf in results["buffers"]:
            row = {"label": results["label"], **buf}
            if has_mcc:
                mcc = tc.get("mcc", {})
                sens = tc.get("sensitivity", {})
                spec = tc.get("specificity", {})
                # MCC is buffer-invariant; repeated per row for tabular
                # convenience.
                row.update({
                    "mcc": mcc.get("mean", 0),
                    "mcc_ci_lower": mcc.get("ci_lower", 0),
                    "mcc_ci_upper": mcc.get("ci_upper", 0),
                    "sensitivity": sens.get("mean", 0),
                    "specificity": spec.get("mean", 0),
                })
            if has_coverage:
                cov = buf.get("coverage", {}) or {}
                row.update({
                    "coverage_status": buf.get(
                        "coverage_status", "normal",
                    ),
                    "ci_unreliable": bool(buf.get("ci_unreliable", False)),
                    "ci_zero_fraction": cov.get("zero_fraction", 0.0),
                    "ci_n_tiles": cov.get("n_tiles", 0),
                })
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    logger.info("CSV written: %s", csv_path)

    # Markdown
    md_path = output_dir / "evaluation.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Evaluation: {results['label']}\n\n")
        f.write(f"**Generated**: {datetime.now(timezone.utc).isoformat()}  \n")
        if "n_runs" in results:
            f.write(f"**Runs**: {results['n_runs']}  \n")
        f.write(
            f"**Detections**: {results.get('n_detections', '—')}  \n\n",
        )

        # When MCC is present we emit four additional columns per row.
        # The MCC mean and CI come from the buffer-invariant
        # ``tile_classification`` block; sensitivity and specificity are
        # likewise repeated across rows.
        if has_mcc:
            mcc = tc.get("mcc", {})
            sens = tc.get("sensitivity", {})
            spec = tc.get("specificity", {})
            f.write(
                "| Buffer | F1 | F1 CI | P | P CI | R | R CI "
                "| MCC | MCC CI | Sens | Spec |\n",
            )
            f.write("|" + "---|" * 11 + "\n")
        else:
            f.write("| Buffer | F1 | F1 CI | P | P CI | R | R CI |\n")
            f.write("|---|---|---|---|---|---|---|\n")
        # Mitigation 3 (sparse coverage): when a buffer's
        # ``ci_unreliable`` flag is set, replace the numeric CI cells with
        # ``N/A *`` and emit a footnote at the bottom of the table. The
        # point estimate is preserved in the F1/P/R columns; the
        # numerically-misleading bounds are hidden from human-readable
        # output. The JSON copy retains the bounds for downstream tooling.
        any_sparse = False
        for buf in results["buffers"]:
            ci_unreliable = bool(buf.get("ci_unreliable", False))
            if ci_unreliable:
                any_sparse = True

            def _ci(lo: float, hi: float, suppress: bool) -> str:
                """Format a CI cell as ``[lo, hi]`` or ``N/A *`` when sparse."""
                if suppress:
                    return "N/A *"
                return f"[{lo:.3f}, {hi:.3f}]"

            row_body = (
                f"| {buf['buffer_metres']}m "
                f"| {buf['f1']:.3f} "
                f"| {_ci(buf.get('f1_ci_lower', 0), buf.get('f1_ci_upper', 0), ci_unreliable)} "
                f"| {buf['precision']:.3f} "
                f"| {_ci(buf.get('p_ci_lower', 0), buf.get('p_ci_upper', 0), ci_unreliable)} "
                f"| {buf['recall']:.3f} "
                f"| {_ci(buf.get('r_ci_lower', 0), buf.get('r_ci_upper', 0), ci_unreliable)} "
            )
            if has_mcc:
                # MCC CI is buffer-invariant; suppression for tabular
                # MCC follows the same rule because the same tile pool
                # underlies all CIs.
                mcc_cells = (
                    f"| {mcc.get('mean', 0):.3f} "
                    f"| {_ci(mcc.get('ci_lower', 0), mcc.get('ci_upper', 0), ci_unreliable)} "
                    f"| {sens.get('mean', 0):.3f} "
                    f"| {spec.get('mean', 0):.3f} "
                )
                f.write(row_body + mcc_cells + "|\n")
            else:
                f.write(row_body + "|\n")

        # Footnote: only emit when at least one row is suppressed.
        if any_sparse:
            zero_pcts = [
                f"{buf.get('coverage', {}).get('zero_fraction', 0):.1%}"
                for buf in results["buffers"]
                if buf.get("ci_unreliable", False)
            ]
            f.write(
                "\n\\* Bootstrap CI suppressed for sparse-coverage buffers "
                f"({', '.join(zero_pcts)} of evaluation tiles have zero "
                "TP/FP/FN counts; threshold > 50 %). "
                "Numeric bounds remain in `evaluation.json` and "
                "`evaluation.csv` for downstream tooling. The point "
                "estimate (F1, P, R, MCC) is unaffected. See "
                "`planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` "
                "for the underlying methodology decision.\n",
            )
        f.write("\n")
    logger.info("Markdown written: %s", md_path)


# ── Batch mode ────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert a label to a filesystem-safe directory name.

    Args:
        text: Human-readable label.

    Returns:
        Lowercase string with spaces/special chars replaced by hyphens.
    """
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def load_batch_yaml(
    path: Path,
) -> tuple[dict, list[dict]]:
    """Load a batch evaluation YAML spec.

    Reads the YAML file, extracts defaults and per-condition specs,
    and merges overrides. Each condition inherits from defaults unless
    it provides its own value.

    Args:
        path: Path to the batch YAML file.

    Returns:
        Tuple of (defaults_dict, conditions_list) where each condition
        dict has all parameters resolved.
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    defaults = data.get("defaults", {})
    metadata = data.get("metadata", {})
    conditions = data.get("conditions", [])

    if not conditions:
        raise ValueError(f"No conditions found in {path}")

    # Resolve paths relative to PROJECT_ROOT
    for key in ["bounds", "ground_truth"]:
        if key in defaults and not Path(defaults[key]).is_absolute():
            defaults[key] = str(PROJECT_ROOT / defaults[key])

    # Merge defaults into each condition
    resolved = []
    for cond in conditions:
        merged = {**defaults, **cond}
        # Resolve condition-specific paths
        for key in ["bounds", "ground_truth"]:
            if key in merged and not Path(merged[key]).is_absolute():
                merged[key] = str(PROJECT_ROOT / merged[key])
        if "detections_dir" in merged:
            det_dir = merged["detections_dir"]
            if not Path(det_dir).is_absolute():
                merged["detections_dir"] = str(PROJECT_ROOT / det_dir)
        resolved.append(merged)

    logger.info(
        "Loaded %d conditions from %s", len(resolved), path,
    )
    if metadata:
        defaults["_metadata"] = metadata

    return defaults, resolved


def write_batch_summary(
    all_summaries: list[dict],
    output_dir: Path,
    metadata: dict | None = None,
) -> None:
    """Write consolidated batch summary files.

    Produces CSV, Markdown, and JSON summaries across all conditions.

    Args:
        all_summaries: List of per-condition summary dicts (from
            evaluate_single_run or evaluate_multi_run_mean).
        output_dir: Output directory.
        metadata: Optional metadata dict from the batch YAML.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Flatten to rows: one per condition × buffer
    flat_rows = []
    has_mcc = any("tile_classification" in s for s in all_summaries)

    for summary in all_summaries:
        label = summary.get("label", "unknown")
        n_runs = summary.get("n_runs", 1)
        tc = summary.get("tile_classification", {})
        for buf in summary.get("buffers", []):
            row = {
                "label": label,
                "n_runs": n_runs,
                "buffer_metres": buf.get("buffer_metres"),
                "f1": buf.get("f1", 0),
                "f1_ci_lower": buf.get("f1_ci_lower", 0),
                "f1_ci_upper": buf.get("f1_ci_upper", 0),
                "precision": buf.get("precision", 0),
                "p_ci_lower": buf.get("p_ci_lower", 0),
                "p_ci_upper": buf.get("p_ci_upper", 0),
                "recall": buf.get("recall", 0),
                "r_ci_lower": buf.get("r_ci_lower", 0),
                "r_ci_upper": buf.get("r_ci_upper", 0),
            }
            if has_mcc and tc:
                mcc = tc.get("mcc", {})
                sens = tc.get("sensitivity", {})
                spec = tc.get("specificity", {})
                row.update({
                    "mcc": mcc.get("mean", 0),
                    "mcc_ci_lower": mcc.get("ci_lower", 0),
                    "mcc_ci_upper": mcc.get("ci_upper", 0),
                    "sensitivity": sens.get("mean", 0),
                    "specificity": spec.get("mean", 0),
                })
            flat_rows.append(row)

    # Sort by F1 descending
    flat_rows.sort(key=lambda r: r["f1"], reverse=True)

    # CSV
    csv_path = output_dir / "batch_summary.csv"
    fieldnames = [
        "label", "n_runs", "buffer_metres",
        "f1", "f1_ci_lower", "f1_ci_upper",
        "precision", "p_ci_lower", "p_ci_upper",
        "recall", "r_ci_lower", "r_ci_upper",
    ]
    if has_mcc:
        fieldnames.extend([
            "mcc", "mcc_ci_lower", "mcc_ci_upper",
            "sensitivity", "specificity",
        ])
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in flat_rows:
            writer.writerow(row)
    logger.info("Batch CSV written: %s (%d rows)", csv_path, len(flat_rows))

    # JSON
    json_path = output_dir / "batch_summary.json"
    json_output = {
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_conditions": len(all_summaries),
        "n_rows": len(flat_rows),
    }
    if metadata:
        json_output["metadata"] = metadata
    json_output["rows"] = flat_rows
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2)
    logger.info("Batch JSON written: %s", json_path)

    # Markdown
    md_path = output_dir / "batch_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# N=1 Single-Pass Evaluation Summary\n\n")
        f.write(
            f"**Generated**: "
            f"{datetime.now(timezone.utc).isoformat()}  \n",
        )
        f.write(f"**Conditions**: {len(all_summaries)}  \n")
        if metadata:
            desc = metadata.get("description", "")
            if desc:
                f.write(f"**Description**: {desc}  \n")
        f.write("\n")

        # ``has_mcc`` mirrors the gating used for the CSV above: when any
        # condition supplied a ``tile_classification`` block, every row
        # already carries MCC / sensitivity / specificity values (the
        # row-builder above falls back to defaults for conditions that
        # did not), so the wider header is safe to emit.
        if has_mcc:
            f.write(
                "| Rank | Condition | Runs | Buffer "
                "| F1 | F1 CI | P | P CI | R | R CI "
                "| MCC | MCC CI | Sens | Spec |\n",
            )
            f.write("|" + "---|" * 14 + "\n")
        else:
            f.write(
                "| Rank | Condition | Runs | Buffer "
                "| F1 | F1 CI | P | P CI | R | R CI |\n",
            )
            f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        for i, row in enumerate(flat_rows, 1):
            row_body = (
                f"| {i} "
                f"| {row['label']} "
                f"| {row['n_runs']} "
                f"| {row['buffer_metres']}m "
                f"| {row['f1']:.3f} "
                f"| [{row['f1_ci_lower']:.3f}, {row['f1_ci_upper']:.3f}] "
                f"| {row['precision']:.3f} "
                f"| [{row['p_ci_lower']:.3f}, {row['p_ci_upper']:.3f}] "
                f"| {row['recall']:.3f} "
                f"| [{row['r_ci_lower']:.3f}, "
                f"{row['r_ci_upper']:.3f}] "
            )
            if has_mcc:
                mcc_cells = (
                    f"| {row.get('mcc', 0):.3f} "
                    f"| [{row.get('mcc_ci_lower', 0):.3f}, "
                    f"{row.get('mcc_ci_upper', 0):.3f}] "
                    f"| {row.get('sensitivity', 0):.3f} "
                    f"| {row.get('specificity', 0):.3f} "
                )
                f.write(row_body + mcc_cells + "|\n")
            else:
                f.write(row_body + "|\n")
        f.write("\n")
    logger.info("Batch Markdown written: %s", md_path)


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> int:
    """Run the detection evaluation."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate detection GeoJSON files against ground truth. "
            "Computes F1, Precision, Recall with 95% bootstrap CIs "
            "at configurable spatial buffer distances."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )

    # Input modes
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--detections", type=Path, nargs="+",
        help=(
            "One or more detection GeoJSON files. Multiple files are "
            "treated as independent runs of the same condition."
        ),
    )
    input_group.add_argument(
        "--detections-dir", type=Path,
        help="Directory containing detection runs (use with --glob).",
    )
    input_group.add_argument(
        "--batch", type=Path,
        help=(
            "YAML batch spec file listing multiple conditions to "
            "evaluate. Produces per-condition outputs plus a "
            "consolidated summary. See docstring for YAML format."
        ),
    )

    parser.add_argument(
        "--glob", type=str, default="*/detections_*.geojson",
        help=(
            "Glob pattern for finding GeoJSON files within "
            "--detections-dir (default: '*/detections_*.geojson')"
        ),
    )

    # Evaluation parameters
    parser.add_argument(
        "--buffers", type=int, nargs="+", default=DEFAULT_BUFFERS,
        help=(
            "Buffer distances in metres "
            f"(default: {' '.join(map(str, DEFAULT_BUFFERS))})"
        ),
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=DEFAULT_GROUND_TRUTH,
        help=f"Ground truth GeoJSON (default: {DEFAULT_GROUND_TRUTH.name})",
    )
    parser.add_argument(
        "--bounds", type=Path, default=DEFAULT_BOUNDS,
        help=f"Tile boundaries GeoJSON (default: {DEFAULT_BOUNDS.name})",
    )
    parser.add_argument(
        "--bootstrap", type=int, default=DEFAULT_BOOTSTRAP,
        help=f"Bootstrap iterations (default: {DEFAULT_BOOTSTRAP})",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
        help=f"Random seed (default: {DEFAULT_SEED})",
    )

    # Output
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Output directory (default: prints to console only)",
    )
    parser.add_argument(
        "--label", type=str, default=None,
        help="Human-readable condition label (default: derived from path)",
    )
    parser.add_argument(
        "--mcc", action="store_true",
        help=(
            "Compute tile-level MCC (Matthews Correlation Coefficient) "
            "with bootstrap CIs. Classifies each tile as populated or "
            "empty and reports MCC, sensitivity, and specificity."
        ),
    )

    args = parser.parse_args()

    # ── Batch mode ────────────────────────────────────────────
    if args.batch:
        return _run_batch_mode(args)

    # ── Single-condition mode ─────────────────────────────────
    return _run_single_mode(args)


def _evaluate_condition(
    det_files: list[Path],
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: list[int],
    n_bootstrap: int,
    seed: int,
    label: str,
    output_dir: Path | None = None,
    compute_mcc: bool = False,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Evaluate a single condition (one or more detection files).

    Shared logic for both single and batch modes.

    Args:
        det_files: Detection GeoJSON file paths.
        gdf_ref: Ground truth reference GeoDataFrame.
        gdf_bounds: Evaluation tile boundaries GeoDataFrame.
        buffers: Buffer distances in metres.
        n_bootstrap: Bootstrap iterations.
        seed: Random seed.
        label: Human-readable condition label.
        output_dir: Optional output directory for per-condition files.
        compute_mcc: If True, compute tile-level MCC with bootstrap CIs.
        metadata: Optional provenance metadata (see ``_build_metadata``)
            written into the resulting ``evaluation.json`` so the output
            is self-documenting.

    Returns:
        Summary dict with metrics.
    """
    run_results = []
    for det_path in det_files:
        run_label = det_path.stem
        logger.info("Evaluating: %s", det_path.name)
        gdf_det = load_geojson(det_path)

        # Add source_tile column if missing (required by bootstrap)
        if "source_tile" not in gdf_det.columns and not gdf_det.empty:
            joined = gpd.sjoin(
                gdf_det, gdf_bounds[["tile_name", "geometry"]],
                how="left", predicate="intersects",
            )
            # Deduplicate: a single detection may intersect multiple
            # bounds tiles when tiles overlap (e.g. tile_size=384 with
            # stride=336 overlaps neighbours by 48 px). Keep the first
            # matching tile per detection so the index aligns with
            # gdf_det for assignment.
            joined = joined[~joined.index.duplicated(keep="first")]
            gdf_det["source_tile"] = joined["tile_name"]

        result = evaluate_single_run(
            gdf_det, gdf_ref, gdf_bounds,
            buffers=buffers,
            n_bootstrap=n_bootstrap,
            seed=seed,
            label=run_label,
            compute_mcc=compute_mcc,
        )
        run_results.append(result)

    # Compute summary
    if len(run_results) == 1:
        summary = run_results[0]
        summary["label"] = label
        per_run = None
    else:
        summary = evaluate_multi_run_mean(run_results, label=label)
        per_run = run_results

    if output_dir:
        write_outputs(summary, per_run, output_dir, metadata=metadata)

    return summary


def _run_single_mode(args: argparse.Namespace) -> int:
    """Run single-condition evaluation mode.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Resolve detection files
    if args.detections_dir:
        det_files = find_detection_files(args.detections_dir, args.glob)
    else:
        det_files = args.detections

    if not det_files:
        logger.error("No detection files found.")
        return 1

    logger.info("Detection files: %d", len(det_files))

    # Load reference data
    logger.info("Loading ground truth: %s", args.ground_truth)
    gdf_ref = load_geojson(args.ground_truth)
    logger.info("Loading bounds: %s", args.bounds)
    gdf_bounds = load_geojson(args.bounds)
    logger.info(
        "Reference: %d mounds, %d evaluation tiles",
        len(gdf_ref), len(gdf_bounds),
    )

    label = args.label or (
        det_files[0].parent.parent.name
        if len(det_files) > 1
        else det_files[0].stem
    )

    # Capture run provenance once, so the same metadata block is
    # attached to every output file produced by this invocation.
    run_metadata = _build_metadata(args)

    summary = _evaluate_condition(
        det_files, gdf_ref, gdf_bounds,
        buffers=args.buffers,
        n_bootstrap=args.bootstrap,
        seed=args.seed,
        label=label,
        output_dir=args.output_dir,
        compute_mcc=args.mcc,
        metadata=run_metadata,
    )

    if not args.output_dir:
        print(json.dumps(summary, indent=2))

    return 0


def _run_batch_mode(args: argparse.Namespace) -> int:
    """Run batch evaluation mode from a YAML spec.

    Evaluates multiple conditions, writes per-condition outputs, and
    produces a consolidated batch summary.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    if not args.output_dir:
        logger.error("--output-dir is required in batch mode.")
        return 1

    defaults, conditions = load_batch_yaml(args.batch)
    metadata = defaults.get("_metadata")

    # Capture run provenance once for the entire batch. Each condition
    # inherits the same block, then overlays its own bootstrap/seed
    # values from the YAML below.
    run_metadata = _build_metadata(args)

    # Load ground truth once (shared across conditions)
    gt_path = Path(defaults.get(
        "ground_truth",
        str(DEFAULT_GROUND_TRUTH),
    ))
    logger.info("Loading ground truth: %s", gt_path)
    gdf_ref = load_geojson(gt_path)

    # Track bounds to avoid reloading when unchanged
    current_bounds_path: str | None = None
    gdf_bounds: gpd.GeoDataFrame | None = None

    all_summaries = []
    total = len(conditions)

    for i, cond in enumerate(conditions, 1):
        label = cond.get("label", f"condition_{i}")
        det_dir = Path(cond["detections_dir"])
        glob_pat = cond.get("glob", "*/detections_*.geojson")
        buffers = cond.get("buffers", DEFAULT_BUFFERS)
        n_bootstrap = cond.get("bootstrap", DEFAULT_BOOTSTRAP)
        seed = cond.get("seed", DEFAULT_SEED)
        bounds_path = cond.get("bounds", str(DEFAULT_BOUNDS))

        logger.info(
            "[%d/%d] %s (dir=%s)", i, total, label, det_dir,
        )

        # Reload bounds if changed
        if bounds_path != current_bounds_path:
            logger.info("Loading bounds: %s", bounds_path)
            gdf_bounds = load_geojson(Path(bounds_path))
            current_bounds_path = bounds_path
            logger.info("Bounds: %d tiles", len(gdf_bounds))

        # Find detection files
        det_files = find_detection_files(det_dir, glob_pat)
        if not det_files:
            logger.warning("No files found for %s — skipping", label)
            continue

        logger.info("  %d detection files", len(det_files))

        # Each condition records the shared run provenance plus its own
        # bootstrap/seed values from the YAML — these may differ from
        # the CLI defaults captured in ``run_metadata``.
        cond_metadata: dict[str, Any] = {
            **run_metadata,
            "bootstrap": {
                "n_iterations": int(n_bootstrap),
                "seed": int(seed),
                "resampling_unit": "tile_level",
            },
            "input_files": {
                **run_metadata["input_files"],
                "detections": str(det_dir),
                "bounds": str(bounds_path),
            },
        }

        # Evaluate
        cond_output_dir = args.output_dir / slugify(label)
        summary = _evaluate_condition(
            det_files, gdf_ref, gdf_bounds,
            buffers=buffers,
            n_bootstrap=n_bootstrap,
            seed=seed,
            label=label,
            output_dir=cond_output_dir,
            compute_mcc=args.mcc,
            metadata=cond_metadata,
        )
        all_summaries.append(summary)

    if not all_summaries:
        logger.error("No conditions produced results.")
        return 1

    # Write batch summary
    write_batch_summary(all_summaries, args.output_dir, metadata=metadata)

    logger.info(
        "Batch complete: %d conditions evaluated", len(all_summaries),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
