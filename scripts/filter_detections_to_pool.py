#!/usr/bin/env python3
"""Filter detection GeoJSONs to a tile subset.

Reads a calibration manifest (JSON list of tile names) and filters each
per-run detection GeoJSON to keep only features whose ``source_tile``
is in the manifest. Used to derive smaller-pool detection sets from a
larger pool's runs, exploiting the fact that VLM detection is
tile-independent.

Usage:
    python scripts/filter_detections_to_pool.py \\
        --source-dir outputs/h10/calibration-runs-v2/pool_160 \\
        --manifest inputs/calibration/h10-384/calibration_manifest_040.json \\
        --output-dir outputs/h10/calibration-runs-v2/pool_040

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.lib_detection_paths import find_pass_geojsons  # noqa: E402

logger = logging.getLogger(__name__)


def filter_geojson(
    geojson_path: Path,
    tile_set: set[str],
    output_path: Path,
) -> tuple[int, int]:
    """Filter a detection GeoJSON to keep only features in the tile set.

    Args:
        geojson_path: Path to source detection GeoJSON.
        tile_set: Set of allowed tile names.
        output_path: Path for filtered output.

    Returns:
        Tuple of (original_count, filtered_count).
    """
    with open(geojson_path) as f:
        data = json.load(f)

    original = data.get("features", [])
    filtered = [
        feat for feat in original
        if feat.get("properties", {}).get("source_tile", "") in tile_set
    ]

    data["features"] = filtered
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f)

    return len(original), len(filtered)


def main() -> None:
    """Filter all detection GeoJSONs in source run directories."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir", type=Path, required=True,
        help="Source directory with run_*/ subdirectories",
    )
    parser.add_argument(
        "--manifest", type=Path, required=True,
        help="Calibration manifest (JSON list of tile names)",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for filtered run_*/ subdirectories",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    # Load tile manifest
    with open(args.manifest) as f:
        tile_list = json.load(f)
    tile_set = set(tile_list)
    logger.info("Loaded %d tiles from %s", len(tile_set), args.manifest)

    # Process each run directory
    run_dirs = sorted(args.source_dir.glob("run_*"))
    if not run_dirs:
        logger.error("No run_* directories found in %s", args.source_dir)
        return

    for run_dir in run_dirs:
        geojsons = find_pass_geojsons(run_dir)
        if not geojsons:
            logger.warning("No detection GeoJSON in %s", run_dir)
            continue

        for gj in geojsons:
            out_path = args.output_dir / run_dir.name / gj.name
            orig, filt = filter_geojson(gj, tile_set, out_path)
            logger.info(
                "  %s/%s: %d → %d features (%.0f%%)",
                run_dir.name, gj.name, orig, filt,
                100 * filt / orig if orig else 0,
            )

    logger.info("Done. Output in %s", args.output_dir)


if __name__ == "__main__":
    main()
