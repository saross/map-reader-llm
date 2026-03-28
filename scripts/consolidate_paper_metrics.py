#!/usr/bin/env python3
"""Consolidate multi-buffer evaluation results into paper-ready tables.

Reads consensus sweep reports and PV buffer sensitivity results, extracts
F1/Precision/Recall with 95% bootstrap CIs at each spatial buffer distance,
and produces a unified master table for paper results and spatial tolerance
decision-making.

Usage:
    python scripts/consolidate_paper_metrics.py
    python scripts/consolidate_paper_metrics.py \
        --input-dir results/paper-eval \
        --output-dir results/paper-tables

Inputs:
    - Consensus results: {input_dir}/*/consensus-analysis-report.json
    - PV results: {input_dir}/pv/*/buffer_sensitivity.json

Outputs:
    - metrics_master.json  — Full structured data
    - metrics_master.csv   — Flat table for LaTeX import
    - spatial_tolerance_comparison.md — Pivoted Markdown decision table

Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
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

__version__ = "1.0.0"

# ── Defaults ──────────────────────────────────────────────────────────
DEFAULT_INPUT_DIR = "results/paper-eval"
DEFAULT_OUTPUT_DIR = "results/paper-tables"


# ── Consensus result extraction ───────────────────────────────────────

def extract_consensus_metrics(report_path: Path) -> list[dict[str, Any]]:
    """Extract per-config metrics from a consensus analysis report.

    Reads a consensus-analysis-report.json and extracts the global
    optimum plus all individual configurations. Returns a list of
    metric dicts.

    Args:
        report_path: Path to consensus-analysis-report.json.

    Returns:
        List of metric dicts with keys: pool_size, threshold, f1,
        f1_ci_lower, f1_ci_upper, precision, p_ci_lower, p_ci_upper,
        recall, r_ci_lower, r_ci_upper, n_detections.
    """
    with open(report_path, encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for entry in data.get("results", []):
        row = {
            "pool_size": entry.get("pool_size"),
            "vote_threshold": entry.get("threshold"),
            "f1": entry.get("f1", 0),
            "f1_ci_lower": entry.get("f1_ci_lo", 0),
            "f1_ci_upper": entry.get("f1_ci_hi", 0),
            "precision": entry.get("precision", 0),
            "p_ci_lower": entry.get("p_ci_lo", 0),
            "p_ci_upper": entry.get("p_ci_hi", 0),
            "recall": entry.get("recall", 0),
            "r_ci_lower": entry.get("r_ci_lo", 0),
            "r_ci_upper": entry.get("r_ci_hi", 0),
            "n_detections": entry.get("n_detections", 0),
        }
        rows.append(row)
    return rows


def find_best_consensus_config(
    rows: list[dict[str, Any]],
    pool_size: int | None = None,
) -> dict[str, Any] | None:
    """Find the best configuration by F1 from extracted consensus rows.

    Args:
        rows: List of metric dicts from extract_consensus_metrics().
        pool_size: If specified, filter to this pool size only.

    Returns:
        The row dict with the highest F1, or None if no rows match.
    """
    candidates = rows
    if pool_size is not None:
        candidates = [r for r in rows if r["pool_size"] == pool_size]
    if not candidates:
        return None
    return max(candidates, key=lambda r: r["f1"])


# ── PV result extraction ─────────────────────────────────────────────

def extract_pv_metrics(sensitivity_path: Path) -> list[dict[str, Any]]:
    """Extract per-buffer metrics from a PV buffer sensitivity result.

    Args:
        sensitivity_path: Path to buffer_sensitivity.json.

    Returns:
        List of metric dicts, one per buffer distance.
    """
    with open(sensitivity_path, encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for buf_entry in data.get("buffers", []):
        ci = buf_entry.get("ci", {})
        f1_ci = ci.get("f1", {})
        p_ci = ci.get("precision", {})
        r_ci = ci.get("recall", {})

        row = {
            "buffer_metres": buf_entry.get("buffer_metres"),
            "f1": buf_entry.get("f1", 0),
            "f1_ci_lower": f1_ci.get("lower", 0),
            "f1_ci_upper": f1_ci.get("upper", 0),
            "precision": buf_entry.get("precision", 0),
            "p_ci_lower": p_ci.get("lower", 0),
            "p_ci_upper": p_ci.get("upper", 0),
            "recall": buf_entry.get("recall", 0),
            "r_ci_lower": r_ci.get("lower", 0),
            "r_ci_upper": r_ci.get("upper", 0),
            "n_detections": data.get("n_accepted", 0),
            "pv_threshold": data.get("threshold"),
        }
        rows.append(row)
    return rows


# ── Master table construction ─────────────────────────────────────────

def build_master_table(input_dir: Path) -> list[dict[str, Any]]:
    """Build the unified master table from all result files.

    Scans the input directory for consensus reports and PV buffer
    sensitivity files, extracts best configs, and assembles a flat
    table.

    Args:
        input_dir: Root directory containing paper-eval results.

    Returns:
        List of row dicts for the master table.
    """
    master_rows: list[dict[str, Any]] = []

    # ── Consensus conditions ──────────────────────────────────
    # Directory pattern: {input_dir}/{label}-{buffer}m/
    consensus_reports = sorted(input_dir.glob(
        "*/consensus-analysis-report.json",
    ))

    # Group by condition label (strip buffer suffix)
    from collections import defaultdict
    consensus_groups: dict[str, list[tuple[int, Path]]] = defaultdict(list)

    for report_path in consensus_reports:
        dir_name = report_path.parent.name
        # Skip PV subdirectory
        if dir_name == "pv" or report_path.parent.parent.name == "pv":
            continue

        # Parse: "flash-high-text-20m" → label="flash-high-text", buffer=20
        parts = dir_name.rsplit("-", 1)
        if len(parts) == 2 and parts[1].endswith("m"):
            try:
                buffer_m = int(parts[1][:-1])
                label = parts[0]
                consensus_groups[label].append((buffer_m, report_path))
            except ValueError:
                logger.warning("Cannot parse buffer from %s", dir_name)
                continue
        else:
            logger.warning("Unexpected directory name: %s", dir_name)

    logger.info(
        "Found %d consensus conditions across %d reports",
        len(consensus_groups), len(consensus_reports),
    )

    for label, buffer_reports in sorted(consensus_groups.items()):
        for buffer_m, report_path in sorted(buffer_reports):
            rows = extract_consensus_metrics(report_path)
            if not rows:
                logger.warning("No results in %s", report_path)
                continue

            # Extract best config at each pool size
            pool_sizes = sorted({r["pool_size"] for r in rows})
            for pool_size in pool_sizes:
                best = find_best_consensus_config(rows, pool_size=pool_size)
                if best is None:
                    continue

                config_desc = (
                    f"N={pool_size}, "
                    f"{best['vote_threshold']}-of-{pool_size}"
                )

                master_rows.append({
                    "condition_type": "consensus",
                    "condition_label": label,
                    "pool_size": pool_size,
                    "buffer_metres": buffer_m,
                    "config_details": config_desc,
                    **{k: best[k] for k in [
                        "f1", "f1_ci_lower", "f1_ci_upper",
                        "precision", "p_ci_lower", "p_ci_upper",
                        "recall", "r_ci_lower", "r_ci_upper",
                        "n_detections",
                    ]},
                })

    # ── PV conditions ─────────────────────────────────────────
    pv_dir = input_dir / "pv"
    if pv_dir.exists():
        pv_files = sorted(pv_dir.glob("*/buffer_sensitivity.json"))
        logger.info("Found %d PV conditions", len(pv_files))

        for pv_path in pv_files:
            pv_label = pv_path.parent.name
            pv_rows = extract_pv_metrics(pv_path)

            for row in pv_rows:
                master_rows.append({
                    "condition_type": "pv",
                    "condition_label": pv_label,
                    "pool_size": None,
                    "buffer_metres": row["buffer_metres"],
                    "config_details": f"t={row.get('pv_threshold', '?')}",
                    **{k: row[k] for k in [
                        "f1", "f1_ci_lower", "f1_ci_upper",
                        "precision", "p_ci_lower", "p_ci_upper",
                        "recall", "r_ci_lower", "r_ci_upper",
                        "n_detections",
                    ]},
                })
    else:
        logger.info("No PV directory found at %s", pv_dir)

    return master_rows


# ── Output writers ────────────────────────────────────────────────────

def write_master_json(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Write the master table as structured JSON.

    Args:
        rows: Master table rows.
        output_path: Output file path.
    """
    output = {
        "_metadata": {
            "version": __version__,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_rows": len(rows),
            "description": (
                "Consolidated paper metrics: F1, Precision, Recall "
                "with 95% bootstrap CIs at multiple spatial buffer "
                "distances. All evaluated on full 487-tile bounds."
            ),
        },
        "rows": rows,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logger.info("JSON written: %s (%d rows)", output_path, len(rows))


def write_master_csv(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Write the master table as a flat CSV.

    Args:
        rows: Master table rows.
        output_path: Output file path.
    """
    fieldnames = [
        "condition_type", "condition_label", "pool_size",
        "buffer_metres", "config_details",
        "f1", "f1_ci_lower", "f1_ci_upper",
        "precision", "p_ci_lower", "p_ci_upper",
        "recall", "r_ci_lower", "r_ci_upper",
        "n_detections",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    logger.info("CSV written: %s (%d rows)", output_path, len(rows))


def write_spatial_tolerance_md(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Write a pivoted Markdown table for spatial tolerance comparison.

    Shows each condition as a row with F1 [CI] at each buffer distance
    as column groups. Includes delta-from-20m for quick comparison.

    Args:
        rows: Master table rows.
        output_path: Output file path.
    """
    # Group by condition+pool_size, then pivot by buffer
    from collections import defaultdict

    # Build unique condition keys
    pivoted: dict[str, dict[int, dict]] = defaultdict(dict)
    for row in rows:
        pool = row.get("pool_size")
        pool_str = f" N={pool}" if pool else ""
        key = f"{row['condition_label']}{pool_str}"
        buf = row["buffer_metres"]
        pivoted[key][buf] = row

    buffers = sorted({r["buffer_metres"] for r in rows})

    lines = [
        "# Spatial Tolerance Comparison",
        "",
        f"**Generated**: {datetime.now(timezone.utc).isoformat()}  ",
        f"**Buffers**: {', '.join(str(b) for b in buffers)} m  ",
        "**Bounds**: full_evaluation_bounds.geojson (487 tiles, 435 mounds)  ",
        "",
        "## F1 with 95% CI by Buffer Distance",
        "",
    ]

    # Table header
    header = "| Condition | Type |"
    sep = "|---|---|"
    for buf in buffers:
        header += f" F1 @ {buf}m |"
        sep += "---|"
    if len(buffers) >= 2:
        header += f" Delta {buffers[0]}m->{buffers[-1]}m |"
        sep += "---|"
    lines.append(header)
    lines.append(sep)

    # Data rows, sorted by best F1 at first buffer descending
    sorted_keys = sorted(
        pivoted.keys(),
        key=lambda k: pivoted[k].get(
            buffers[0], {},
        ).get("f1", 0),
        reverse=True,
    )

    for key in sorted_keys:
        buf_data = pivoted[key]
        # Determine type from first available entry
        first_entry = next(iter(buf_data.values()), {})
        cond_type = first_entry.get("condition_type", "?")

        row_str = f"| {key} | {cond_type} |"
        first_f1 = None
        last_f1 = None

        for buf in buffers:
            entry = buf_data.get(buf)
            if entry:
                f1 = entry["f1"]
                lo = entry["f1_ci_lower"]
                hi = entry["f1_ci_upper"]
                row_str += f" {f1:.3f} [{lo:.3f}, {hi:.3f}] |"
                if first_f1 is None:
                    first_f1 = f1
                last_f1 = f1
            else:
                row_str += " — |"

        if len(buffers) >= 2 and first_f1 is not None and last_f1 is not None:
            delta = last_f1 - first_f1
            sign = "+" if delta >= 0 else ""
            row_str += f" {sign}{delta:.3f} |"
        else:
            row_str += " — |"

        lines.append(row_str)

    lines.append("")
    lines.append("## Precision and Recall at Each Buffer")
    lines.append("")

    # Second table: P and R
    header2 = "| Condition |"
    sep2 = "|---|"
    for buf in buffers:
        header2 += f" P @ {buf}m | R @ {buf}m |"
        sep2 += "---|---|"
    lines.append(header2)
    lines.append(sep2)

    for key in sorted_keys:
        buf_data = pivoted[key]
        row_str = f"| {key} |"
        for buf in buffers:
            entry = buf_data.get(buf)
            if entry:
                p = entry["precision"]
                r = entry["recall"]
                row_str += f" {p:.3f} | {r:.3f} |"
            else:
                row_str += " — | — |"
        lines.append(row_str)

    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    logger.info("Markdown written: %s", output_path)


# ── CLI ───────────────────────────────────────────────────────────────

def main() -> int:
    """Run the consolidation pipeline."""
    parser = argparse.ArgumentParser(
        description=(
            "Consolidate multi-buffer evaluation results into "
            "paper-ready tables."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input-dir", type=Path,
        default=Path(DEFAULT_INPUT_DIR),
        help=f"Input directory (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    if not args.input_dir.exists():
        logger.error("Input directory does not exist: %s", args.input_dir)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Build master table
    rows = build_master_table(args.input_dir)
    if not rows:
        logger.error("No results found in %s", args.input_dir)
        return 1

    logger.info("Consolidated %d rows from %s", len(rows), args.input_dir)

    # Write outputs
    write_master_json(rows, args.output_dir / "metrics_master.json")
    write_master_csv(rows, args.output_dir / "metrics_master.csv")
    write_spatial_tolerance_md(
        rows, args.output_dir / "spatial_tolerance_comparison.md",
    )

    # Summary stats
    n_consensus = sum(1 for r in rows if r["condition_type"] == "consensus")
    n_pv = sum(1 for r in rows if r["condition_type"] == "pv")
    buffers = sorted({r["buffer_metres"] for r in rows})
    conditions = sorted({r["condition_label"] for r in rows})

    logger.info(
        "Summary: %d conditions, %d buffers, %d consensus rows, %d PV rows",
        len(conditions), len(buffers), n_consensus, n_pv,
    )

    # Completeness check
    expected = len(conditions) * len(buffers)
    if len(rows) < expected:
        logger.warning(
            "Possible gaps: %d rows vs %d expected "
            "(%d conditions x %d buffers). "
            "Note: consensus conditions have multiple pool sizes.",
            len(rows), expected, len(conditions), len(buffers),
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
