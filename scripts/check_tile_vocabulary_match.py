#!/usr/bin/env python3
"""
Does a cell's ``source_tile`` vocabulary match its scoring frame's tiles?
========================================================================

Description:
    Tile-level Matthews Correlation Coefficient (MCC) is **not** computed
    geometrically. `scripts/lib_advanced_metrics.py:2079` decides whether a
    tile holds a detection with a **string** comparison::

        dets_in_tile = gdf_det[gdf_det['source_tile'] == tile_name]

    So a detection contributes to a tile only when its ``source_tile``
    property is byte-equal to a ``tile_name`` in the bounds file. Point
    matching — and therefore F1 at every buffer — is geometric and unaffected.

    The consequence is sharp and easy to miss: score a cell on a frame whose
    tile vocabulary differs from the tiling its proposer ran on, and F1 comes
    out right while tile-MCC comes out meaningless. It fails **quietly**: the
    numbers are plausible-looking, the evaluation reports no error, and the
    board's own confusion gate reproduces the same wrong confusion and passes.

    This script measures the exposure for any set of detection files against
    any bounds file, so the question is answered by counting rather than by
    assumption.

Usage::

    python scripts/check_tile_vocabulary_match.py \\
        --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \\
        --detections results/.../a.geojson --detections results/.../b.geojson

    # Or every materialised cell of a directory
    python scripts/check_tile_vocabulary_match.py \\
        --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \\
        --glob 'results/k-ladder-2026-09-12/phase2/materialised/*.geojson' \\
        --json-out results/k-ladder-2026-09-12/phase2/tile-vocabulary-match.json

Verdicts:
    ``MATCH``      every detection's ``source_tile`` is a tile of the frame.
    ``PARTIAL``    some are, some are not — tile-MCC undercounts silently.
    ``MISMATCH``   almost none are; tile-MCC is not interpretable at all.
    ``NO-KEY``     the detections carry no ``source_tile`` at all.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import glob as globmod
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

#: Above this share of matched detections a cell is called MATCH; below
#: MISMATCH_BELOW it is called MISMATCH; between, PARTIAL.
MATCH_AT_OR_ABOVE = 0.999
MISMATCH_BELOW = 0.10


def tile_names(bounds_path: Path) -> set[str]:
    """Read the ``tile_name`` set from a bounds GeoJSON."""
    with open(bounds_path) as handle:
        data = json.load(handle)
    return {
        feature["properties"]["tile_name"]
        for feature in data["features"]
        if feature.get("properties", {}).get("tile_name")
    }


def check(detections_path: Path, frame: set[str]) -> dict[str, Any]:
    """Classify one detection file against a frame's tile vocabulary."""
    with open(detections_path) as handle:
        data = json.load(handle)
    features = data.get("features", [])
    keys = [
        feature.get("properties", {}).get("source_tile") for feature in features
    ]
    present = [key for key in keys if key]
    matched = [key for key in present if key in frame]
    n = len(features)

    if not present:
        verdict = "NO-KEY"
    elif n and len(matched) / n >= MATCH_AT_OR_ABOVE:
        verdict = "MATCH"
    elif n and len(matched) / n < MISMATCH_BELOW:
        verdict = "MISMATCH"
    else:
        verdict = "PARTIAL"

    distinct_unmatched = sorted({key for key in present if key not in frame})
    return {
        "detections": str(detections_path),
        "n_features": n,
        "n_with_source_tile": len(present),
        "n_matching_frame": len(matched),
        "share_matching": round(len(matched) / n, 6) if n else None,
        "n_distinct_unmatched_tiles": len(distinct_unmatched),
        "example_unmatched": distinct_unmatched[:3],
        "verdict": verdict,
    }


def main() -> None:
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Check whether detections' source_tile values are tiles of the "
            "scoring frame — the condition tile-MCC silently depends on"
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--bounds", type=Path, required=True)
    parser.add_argument("--detections", type=Path, action="append", default=[])
    parser.add_argument("--glob", type=str, action="append", default=[])
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    frame = tile_names(args.bounds)
    logger.info("frame %s: %d tile name(s)", args.bounds.name, len(frame))

    paths = list(args.detections)
    for pattern in args.glob:
        paths.extend(Path(hit) for hit in sorted(globmod.glob(pattern)))
    if not paths:
        logger.error("no detection files given")
        raise SystemExit(2)

    results = [check(path, frame) for path in paths]
    counts: dict[str, int] = {}
    for result in results:
        counts[result["verdict"]] = counts.get(result["verdict"], 0) + 1
        if result["verdict"] != "MATCH":
            logger.warning(
                "%-12s %s  %d/%d matching (%d distinct unmatched tile(s), e.g. %s)",
                result["verdict"],
                Path(result["detections"]).name,
                result["n_matching_frame"],
                result["n_features"],
                result["n_distinct_unmatched_tiles"],
                ", ".join(result["example_unmatched"]) or "—",
            )
    for verdict in ("MATCH", "PARTIAL", "MISMATCH", "NO-KEY"):
        if verdict in counts:
            logger.info("%-10s %d", verdict, counts[verdict])

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_out, "w") as handle:
            json.dump(
                {
                    "bounds": str(args.bounds),
                    "n_frame_tiles": len(frame),
                    "mechanism": (
                        "lib_advanced_metrics.calculate_tile_classification "
                        "matches detections to tiles by the source_tile STRING, "
                        "not geometrically, so a vocabulary mismatch makes "
                        "tile-MCC meaningless while leaving F1 correct"
                    ),
                    "thresholds": {
                        "match_at_or_above": MATCH_AT_OR_ABOVE,
                        "mismatch_below": MISMATCH_BELOW,
                    },
                    "counts": counts,
                    "cells": results,
                },
                handle,
                indent=2,
            )
            handle.write("\n")
        logger.info("-> %s", args.json_out)

    if counts.get("MISMATCH") or counts.get("NO-KEY"):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
