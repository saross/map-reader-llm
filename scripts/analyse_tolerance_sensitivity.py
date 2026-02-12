#!/usr/bin/env python3
"""
Spatial tolerance sensitivity analysis across all Phase 2 conditions.

Computes F1, precision, and recall at multiple matching buffer distances
(10, 20, 30, 40, 50 m) for every Phase 2 condition. Uses run 1 from each
condition as the representative run. Produces a CSV table and console
summary to check whether the 20 m default tolerance is appropriate and
whether condition rankings change at larger tolerances.

Usage:
    python scripts/analyse_tolerance_sensitivity.py
    python scripts/analyse_tolerance_sensitivity.py --output-dir results/tolerance-sensitivity
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyse_phase2_results import load_condition_results  # noqa: E402
from lib_advanced_metrics import spatial_tolerance_curve  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Phase 2 condition registry
# ---------------------------------------------------------------------------
# Each entry: (phase_label, study_dir relative to outputs/, condition_name)
PHASE2_CONDITIONS: list[tuple[str, str, str]] = [
    # Phase 2a — M/E (modality × elaboration)
    ("2a", "phase2a", "image-only"),
    ("2a", "phase2a", "brief-text"),
    ("2a", "phase2a", "brief-text-image"),
    ("2a", "phase2a", "verbose-text"),
    ("2a", "phase2a", "verbose-text-image"),
    # Phase 2b Track 1 — Temperature (image-using, canonical library)
    ("2b-T1", "phase2b/track1-image", "T0.0"),
    ("2b-T1", "phase2b/track1-image", "T0.3"),
    ("2b-T1", "phase2b/track1-image", "T0.7"),
    ("2b-T1", "phase2b/track1-image", "T1.0"),
    ("2b-T1", "phase2b/track1-image", "T1.3"),
    # Phase 2b Track 2 — Temperature (text-only)
    ("2b-T2", "phase2b/track2-text", "T0.0"),
    ("2b-T2", "phase2b/track2-text", "T0.3"),
    ("2b-T2", "phase2b/track2-text", "T0.7"),
    ("2b-T2", "phase2b/track2-text", "T1.0"),
    ("2b-T2", "phase2b/track2-text", "T1.3"),
    # Phase 2c Track 1 — Library composition (main)
    ("2c", "phase2c/track1-image", "canonical"),
    ("2c", "phase2c/track1-image", "plus-hp"),
    ("2c", "phase2c/track1-image", "pure-positive-canon"),
    ("2c", "phase2c/track1-image", "scale-4"),
    ("2c", "phase2c/track1-image", "scale-8"),
    # Phase 2c exploratory — Pure-positive HP scaling
    ("2c-exp", "phase2c/track1-image-exploratory", "pure-positive-2hp"),
    ("2c-exp", "phase2c/track1-image-exploratory", "pure-positive-4hp"),
    ("2c-exp", "phase2c/track1-image-exploratory", "pure-positive-canon"),
    # Phase 2d Track 1 — Exclusion guidance (image-using)
    ("2d-T1", "phase2d/track1-image", "minimal"),
    ("2d-T1", "phase2d/track1-image", "terse"),
    ("2d-T1", "phase2d/track1-image", "verbose"),
    # Phase 2d Track 2 — Exclusion guidance (text-only)
    ("2d-T2", "phase2d/track2-text", "minimal"),
    ("2d-T2", "phase2d/track2-text", "terse"),
    ("2d-T2", "phase2d/track2-text", "verbose"),
    # Phase 2e — Example ordering
    ("2e", "phase2e", "config-default"),
    ("2e", "phase2e", "canonical-first"),
    ("2e", "phase2e", "canonical-last"),
    ("2e", "phase2e", "random"),
]

BUFFERS = [10, 20, 30, 40, 50]


def load_reference_data(
    project_root: Path,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Load ground truth references and tile boundaries."""
    ref_path = project_root / "inputs/vectors/references/mounds-reference.geojson"
    bounds_path = project_root / "inputs/vectors/bounds/validation_bounds.geojson"

    gdf_ref = gpd.read_file(ref_path)
    gdf_bounds = gpd.read_file(bounds_path)

    # Ensure EPSG:32635
    if gdf_ref.crs and gdf_ref.crs.to_epsg() != 32635:
        gdf_ref = gdf_ref.to_crs(epsg=32635)
    if gdf_bounds.crs and gdf_bounds.crs.to_epsg() != 32635:
        gdf_bounds = gdf_bounds.to_crs(epsg=32635)

    return gdf_ref, gdf_bounds


def run_tolerance_analysis(
    project_root: Path,
    output_dir: Path,
) -> list[dict]:
    """
    Compute spatial tolerance curves for all Phase 2 conditions.

    Uses run 1 as the representative run for each condition. If run 1 is
    unavailable, uses the first available run.

    Returns:
        List of result dicts with keys: phase, condition, buffer, f1,
        precision, recall.
    """
    outputs_root = project_root / "outputs"
    gdf_ref, gdf_bounds = load_reference_data(project_root)

    all_results: list[dict] = []
    skipped: list[str] = []

    for phase_label, study_rel, condition_name in PHASE2_CONDITIONS:
        study_dir = outputs_root / study_rel
        label = f"{phase_label}/{condition_name}"

        # Load runs for this condition
        runs = load_condition_results(study_dir, condition_name)
        if not runs:
            logger.warning("No runs found for %s — skipping", label)
            skipped.append(label)
            continue

        # Use run 1 (or first available)
        run_num, gdf_det = runs[0]

        # Ensure CRS
        if gdf_det.crs and gdf_det.crs.to_epsg() != 32635:
            gdf_det = gdf_det.to_crs(epsg=32635)

        # Compute tolerance curve
        curve = spatial_tolerance_curve(gdf_det, gdf_ref, gdf_bounds, buffers=BUFFERS)

        for row in curve:
            all_results.append({
                "phase": phase_label,
                "condition": condition_name,
                "run": run_num,
                "buffer_m": row["buffer"],
                "f1": row["f1"],
                "precision": row["precision"],
                "recall": row["recall"],
            })

        logger.info(
            "  %s (run %d): F1 @ 20m=%.3f, @ 50m=%.3f",
            label, run_num,
            next(r["f1"] for r in curve if r["buffer"] == 20),
            next(r["f1"] for r in curve if r["buffer"] == 50),
        )

    if skipped:
        logger.warning("Skipped %d conditions: %s", len(skipped), skipped)

    return all_results


def write_csv(results: list[dict], output_path: Path) -> None:
    """Write results to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["phase", "condition", "run", "buffer_m", "f1", "precision", "recall"]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    logger.info("Wrote %d rows to %s", len(results), output_path)


def print_summary(results: list[dict]) -> None:
    """Print a formatted console summary showing F1 at each buffer size."""
    # Build pivot: (phase, condition) → {buffer: f1}
    pivot: dict[tuple[str, str], dict[int, float]] = {}
    for r in results:
        key = (r["phase"], r["condition"])
        if key not in pivot:
            pivot[key] = {}
        pivot[key][r["buffer_m"]] = r["f1"]

    # Sort by F1 at 20m (descending)
    sorted_keys = sorted(pivot.keys(), key=lambda k: pivot[k].get(20, 0), reverse=True)

    # Print table
    header = f"{'Phase':<8} {'Condition':<22}"
    for b in BUFFERS:
        header += f" {'F1@' + str(b) + 'm':>8}"
    header += f" {'Δ50-20':>8}"
    print("\n" + "=" * len(header))
    print("Spatial Tolerance Sensitivity — F1 across buffer sizes")
    print("=" * len(header))
    print(header)
    print("-" * len(header))

    for phase, condition in sorted_keys:
        vals = pivot[(phase, condition)]
        row = f"{phase:<8} {condition:<22}"
        for b in BUFFERS:
            f1 = vals.get(b, 0.0)
            row += f" {f1:>8.4f}"
        # Delta: F1@50m - F1@20m
        delta = vals.get(50, 0.0) - vals.get(20, 0.0)
        row += f" {delta:>+8.4f}"
        print(row)

    print("-" * len(header))

    # Print ranking comparison: top 5 at 20m vs top 5 at 50m
    print("\nTop 5 by F1 @ 20m:")
    for i, (phase, cond) in enumerate(sorted_keys[:5], 1):
        print(f"  {i}. {phase}/{cond}: {pivot[(phase, cond)].get(20, 0):.4f}")

    sorted_50 = sorted(pivot.keys(), key=lambda k: pivot[k].get(50, 0), reverse=True)
    print("\nTop 5 by F1 @ 50m:")
    for i, (phase, cond) in enumerate(sorted_50[:5], 1):
        print(f"  {i}. {phase}/{cond}: {pivot[(phase, cond)].get(50, 0):.4f}")

    # Check for ranking changes
    top5_20 = set(sorted_keys[:5])
    top5_50 = set(sorted_50[:5])
    if top5_20 != top5_50:
        changed = top5_50 - top5_20
        print(f"\n⚠ Ranking changes: {len(changed)} condition(s) enter top 5 at 50m:")
        for phase, cond in changed:
            rank_20 = sorted_keys.index((phase, cond)) + 1
            rank_50 = sorted_50.index((phase, cond)) + 1
            print(f"  {phase}/{cond}: rank {rank_20} @ 20m → rank {rank_50} @ 50m")
    else:
        print("\n✓ Top 5 ranking is stable across 20m and 50m tolerances.")


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Spatial tolerance sensitivity across Phase 2 conditions",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Project root directory (default: auto-detect)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: results/tolerance-sensitivity)",
    )
    args = parser.parse_args()

    project_root = args.project_root
    output_dir = args.output_dir or project_root / "results" / "tolerance-sensitivity"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    logger.info("Running spatial tolerance sensitivity analysis...")
    logger.info("Project root: %s", project_root)

    results = run_tolerance_analysis(project_root, output_dir)

    if not results:
        logger.error("No results produced — check condition directories")
        sys.exit(1)

    # Write CSV
    csv_path = output_dir / "tolerance-sensitivity.csv"
    write_csv(results, csv_path)

    # Write JSON
    json_path = output_dir / "tolerance-sensitivity.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info("Wrote JSON to %s", json_path)

    # Console summary
    print_summary(results)


if __name__ == "__main__":
    main()
