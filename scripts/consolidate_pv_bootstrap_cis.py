#!/usr/bin/env python3
"""Consolidate PV bootstrap confidence intervals from threshold sweep results.

Reads threshold_sweep.json files produced by the PV evaluation pipeline,
extracts optimal-threshold F1/precision/recall with bootstrap CIs, and
writes a single consolidated JSON for downstream analysis.

Usage:
    python scripts/consolidate_pv_bootstrap_cis.py
    python scripts/consolidate_pv_bootstrap_cis.py \
        --results-dir results/h11-384-pv-diagnostic \
        --output results/h11-384-pv-diagnostic/bootstrap-cis-384px.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

__version__ = "1.1.0"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_RESULTS_DIR = "results/h11-384-pv-diagnostic"
DEFAULT_OUTPUT = "results/h11-384-pv-diagnostic/bootstrap-cis-384px.json"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Consolidate PV bootstrap CIs from threshold sweep files.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(DEFAULT_RESULTS_DIR),
        help=f"Directory containing per-condition subdirectories (default: {DEFAULT_RESULTS_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(DEFAULT_OUTPUT),
        help=f"Output JSON path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def load_sweep(path: Path) -> dict[str, Any] | None:
    """Load a threshold_sweep.json, returning None for old-format (list) files.

    New-format files have a top-level dict with keys like 'version',
    'thresholds', and 'optimal'.  Old-format files are bare JSON arrays.

    Args:
        path: Path to a threshold_sweep.json file.

    Returns:
        Parsed dict if new-format, or None if old-format / unreadable.
    """
    try:
        with path.open() as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return None

    if isinstance(data, list):
        logger.warning(
            "Skipping old-format (bare JSON list) file: %s — re-run "
            "evaluate_pv_results.py sweep to regenerate with the new "
            "dict schema that includes optimal-threshold bootstrap CIs",
            path,
        )
        return None

    if not isinstance(data, dict):
        logger.warning("Unexpected top-level type in %s: %s", path, type(data).__name__)
        return None

    return data


def extract_condition(sweep: dict[str, Any]) -> dict[str, Any] | None:
    """Extract consolidated metrics from a new-format threshold sweep.

    Reads the 'optimal' block and reshapes it into the output format
    expected by downstream analysis.

    Args:
        sweep: Parsed threshold_sweep.json dict.

    Returns:
        Dict with f1/precision/recall CIs plus metadata, or None on error.
    """
    optimal = sweep.get("optimal")
    if optimal is None:
        return None

    ci = optimal.get("ci", {})

    def _metric_block(name: str) -> dict[str, float]:
        """Build a {mean, ci_lower, ci_upper} block for the given metric."""
        block = ci.get(name, {})
        return {
            "mean": block.get("mean", optimal.get(name, 0.0)),
            "ci_lower": block.get("lower", 0.0),
            "ci_upper": block.get("upper", 0.0),
        }

    return {
        "f1": _metric_block("f1"),
        "precision": _metric_block("precision"),
        "recall": _metric_block("recall"),
        "n_iterations": sweep.get("bootstrap_iterations", 0),
        "n_detections": optimal.get("n_accepted", 0),
        "threshold": optimal.get("threshold", 0.0),
    }


def consolidate(results_dir: Path) -> dict[str, Any]:
    """Scan results_dir for threshold sweep files and consolidate.

    Args:
        results_dir: Directory containing per-condition subdirectories,
            each with a threshold_sweep.json.

    Returns:
        Consolidated dict with '_metadata' and 'results' keys.
    """
    source_glob = f"{results_dir}/*/threshold_sweep.json"
    sweep_paths = sorted(results_dir.glob("*/threshold_sweep.json"))

    logger.info("Found %d threshold_sweep.json files in %s", len(sweep_paths), results_dir)

    results: dict[str, Any] = {}
    skipped = 0
    sources_processed: list[str] = []
    sources_skipped: list[str] = []

    for path in sweep_paths:
        condition = path.parent.name
        sweep = load_sweep(path)
        if sweep is None:
            skipped += 1
            sources_skipped.append(str(path.relative_to(results_dir.parent)))
            continue

        entry = extract_condition(sweep)
        if entry is None:
            logger.warning("No 'optimal' block in %s — skipping", path)
            skipped += 1
            sources_skipped.append(str(path.relative_to(results_dir.parent)))
            continue

        results[condition] = entry
        sources_processed.append(str(path.relative_to(results_dir.parent)))

    logger.info(
        "Consolidated %d conditions (%d skipped)",
        len(results),
        skipped,
    )

    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "n_conditions": len(results),
        "n_skipped": skipped,
        "source_glob": source_glob,
        "source_files_processed": sources_processed,
        "source_files_skipped": sources_skipped,
    }

    return {"_metadata": metadata, "results": results}


def main() -> None:
    """Entry point: parse args, consolidate, write output."""
    args = parse_args()

    if not args.results_dir.is_dir():
        logger.error("Results directory does not exist: %s", args.results_dir)
        sys.exit(1)

    consolidated = consolidate(args.results_dir)

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w") as fh:
        json.dump(consolidated, fh, indent=2)

    logger.info("Wrote %s (%d conditions)", args.output, consolidated["_metadata"]["n_conditions"])

    # Print a brief summary to stdout
    print(f"\nConsolidated {consolidated['_metadata']['n_conditions']} conditions")
    print(f"Output: {args.output}")

    # Spot-check: show first 3 conditions
    items = list(consolidated["results"].items())[:3]
    for name, data in items:
        f1 = data["f1"]
        print(
            f"  {name}: F1={f1['mean']:.4f} "
            f"[{f1['ci_lower']:.4f}, {f1['ci_upper']:.4f}] "
            f"(threshold={data['threshold']}, n={data['n_detections']})"
        )


if __name__ == "__main__":
    main()
