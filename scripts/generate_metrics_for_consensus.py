#!/usr/bin/env python3
"""
Metrics Generator for Consensus Runs
=====================================

Generates metrics files for each detection run in a directory, calculating
F1, precision, recall, and per-class performance against ground truth.

Used to prepare data for consensus analysis and benchmark variability studies.

Usage::

    python scripts/generate_metrics_for_consensus.py \\
        --run_dir outputs/results/v4.1/ \\
        --bounds inputs/vectors/region_bounds.geojson

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import traceback
from pathlib import Path

from scripts.lib_advanced_metrics import calculate_f1_internal, calculate_per_class_f1, load_data


def generate_metrics(
    run_dir: Path | str,
    bounds_path: Path | str,
    output_dir: Path | str | None = None,
) -> None:
    """
    Generate metrics files for all detection runs in a directory.

    Scans for ``run_*.geojson`` files and calculates F1, precision, recall,
    and per-class performance for each, saving results as JavaScript Object
    Notation (JSON) files.

    Args:
        run_dir: Directory containing run GeoJSON files.
        bounds_path: Path to the tile bounds GeoJSON file.
        output_dir: Optional output directory for metrics files
            (defaults to *run_dir*).
    """
    run_dir = Path(run_dir)
    output_dir = Path(output_dir) if output_dir else run_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning runs in {run_dir}...")

    # Find all run_* files, excluding metadata, metrics, and directories
    all_files = sorted(run_dir.glob("run_*"))
    run_files = [
        f
        for f in all_files
        if f.is_file()
        and "meta" not in f.name
        and "_metrics" not in f.name
        and "_advanced_metrics" not in f.name
    ]

    for run_file in run_files:
        run_name = run_file.stem
        print(f"Processing {run_name}...")

        try:
            gdf_det, gdf_bounds, gdf_ref = load_data(run_file, bounds_path)

            if gdf_det is None or gdf_det.empty:
                print(f"Skipping {run_name}: No detections or load error.")
                continue

            # Calculate overall and per-class metrics
            precision, recall, f1 = calculate_f1_internal(
                gdf_det, gdf_ref, gdf_bounds,
            )
            per_class_results = calculate_per_class_f1(
                gdf_det, gdf_ref, gdf_bounds,
            )

            # Structure expected by benchmark_variability.py
            tiles_processed: int = (
                len(gdf_bounds["tile_name"].unique())
                if gdf_bounds is not None
                else 0
            )
            metrics: dict[str, float | int] = {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
                "tiles_processed": tiles_processed,
            }

            advanced_metrics: dict[str, list[dict]] = {
                "per_class_performance": per_class_results,
            }

            # Save standard metrics file
            metrics_path = output_dir / f"{run_name}_metrics.json"
            with open(metrics_path, "w") as fh:
                json.dump(metrics, fh, indent=2)

            # Save advanced (per-class) metrics file
            adv_metrics_path = output_dir / f"{run_name}_advanced_metrics.json"
            with open(adv_metrics_path, "w") as fh:
                json.dump(advanced_metrics, fh, indent=2)

            print(f"Saved metrics for {run_name}")

        except Exception as exc:
            traceback.print_exc()
            print(f"Error processing {run_name}: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate metrics files for consensus detection runs.",
    )
    parser.add_argument(
        "--run_dir",
        required=True,
        help="Directory containing run GeoJSON files",
    )
    parser.add_argument(
        "--bounds",
        required=True,
        help="Path to bounds GeoJSON file",
    )
    args = parser.parse_args()

    generate_metrics(args.run_dir, args.bounds)
