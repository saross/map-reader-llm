#!/usr/bin/env python3
"""Generate markdown summaries for PV threshold sweep results.

Reads threshold_sweep.json files from PV diagnostic results directories
and generates a companion threshold_sweep_summary.md in each directory.

Usage:
    # Generate summaries for all conditions (skip existing)
    python scripts/generate_pv_sweep_summaries.py

    # Overwrite existing summaries
    python scripts/generate_pv_sweep_summaries.py --overwrite

    # Target a specific results directory
    python scripts/generate_pv_sweep_summaries.py \
        --results-dir results/h11-384-pv-diagnostic
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

__version__ = "1.0.0"

logger = logging.getLogger(__name__)

# Default results directory
DEFAULT_RESULTS_DIR = Path("results/h11-384-pv-diagnostic")


def generate_summary(sweep_path: Path, overwrite: bool = False) -> bool:
    """Generate a markdown summary from a threshold_sweep.json file.

    Args:
        sweep_path: Path to the threshold_sweep.json file.
        overwrite: If True, overwrite existing summaries.

    Returns:
        True if a summary was written, False if skipped.
    """
    output_path = sweep_path.parent / "threshold_sweep_summary.md"

    if output_path.exists() and not overwrite:
        return False

    data = json.loads(sweep_path.read_text())

    # Handle old-format files (bare list instead of dict)
    if isinstance(data, list):
        logger.warning(
            "Skipping old-format file (bare list): %s", sweep_path
        )
        return False

    condition_name = sweep_path.parent.name
    total_candidates = data.get("total_candidates", "?")
    gt_mounds = data.get("ground_truth_mounds", "?")
    eval_tiles = data.get("evaluation_tiles", "?")
    step = data.get("step", "?")
    bootstrap = data.get("bootstrap_iterations", "?")
    seed = data.get("seed", "?")

    optimal = data.get("optimal", {})
    opt_t = optimal.get("threshold", "?")
    opt_f1 = optimal.get("f1", 0)
    opt_p = optimal.get("precision", 0)
    opt_r = optimal.get("recall", 0)
    opt_n = optimal.get("n_accepted", "?")
    opt_ci = optimal.get("ci", {}).get("f1", {})
    opt_ci_lo = opt_ci.get("lower", 0)
    opt_ci_hi = opt_ci.get("upper", 0)

    thresholds = data.get("thresholds", [])

    # Build markdown
    lines = [
        f"# PV Threshold Sweep: {condition_name}",
        "",
        f"**Candidates**: {total_candidates}  ",
        f"**Ground truth**: {gt_mounds} mounds, {eval_tiles} tiles  ",
        f"**Bootstrap**: {bootstrap} iterations (seed {seed})  ",
        f"**Step size**: {step}",
        "",
        "## Optimal Configuration",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Threshold | {opt_t} |",
        f"| F1 | {opt_f1:.4f} |",
        f"| 95% CI | [{opt_ci_lo:.3f}, {opt_ci_hi:.3f}] |",
        f"| Precision | {opt_p:.4f} |",
        f"| Recall | {opt_r:.4f} |",
        f"| Detections | {opt_n} |",
        "",
        "## Full Sweep",
        "",
        "| Threshold | Accepted | Precision | Recall | F1 | 95% CI |",
        "|-----------|----------|-----------|--------|------|--------|",
    ]

    for t in thresholds:
        ci = t.get("ci", {}).get("f1", {})
        ci_lo = ci.get("lower", 0)
        ci_hi = ci.get("upper", 0)
        is_optimal = t.get("threshold") == opt_t
        marker = " **" if is_optimal else ""
        marker_end = "**" if is_optimal else ""
        lines.append(
            f"| {marker}{t.get('threshold', '?')}{marker_end} "
            f"| {t.get('n_accepted', '?')} "
            f"| {t.get('precision', 0):.4f} "
            f"| {t.get('recall', 0):.4f} "
            f"| {marker}{t.get('f1', 0):.4f}{marker_end} "
            f"| [{ci_lo:.3f}, {ci_hi:.3f}] |"
        )

    lines.append("")

    output_path.write_text("\n".join(lines))
    return True


def main() -> None:
    """Generate PV sweep summaries for all conditions."""
    parser = argparse.ArgumentParser(
        description="Generate markdown summaries for PV threshold sweeps.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help=(
            "Base directory containing per-condition sweep results "
            f"(default: {DEFAULT_RESULTS_DIR})"
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing summary files",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    results_dir = args.results_dir
    if not results_dir.exists():
        logger.error("Results directory not found: %s", results_dir)
        return

    sweep_files = sorted(results_dir.glob("*/threshold_sweep.json"))
    logger.info("Found %d sweep files in %s", len(sweep_files), results_dir)

    generated = 0
    skipped = 0
    errors = 0

    for sweep_path in sweep_files:
        try:
            if generate_summary(sweep_path, overwrite=args.overwrite):
                generated += 1
                logger.info("Generated: %s", sweep_path.parent.name)
            else:
                skipped += 1
        except Exception:
            errors += 1
            logger.exception("Error processing %s", sweep_path)

    logger.info(
        "Done: %d generated, %d skipped, %d errors",
        generated, skipped, errors,
    )


if __name__ == "__main__":
    main()
