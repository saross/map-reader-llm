#!/usr/bin/env python3
"""
Confirm that candidate pools meant to differ in one lever assessed the same area
================================================================================

Description:
    The command-line face of ``scripts/lib_assessed_area.py`` (PI ruling D51).
    Give it the pools of a K-ladder (or of any contrast whose cells should
    differ in one lever only) and the scoring frame; it determines each
    pool's assessed area from its provenance, intersects it with the frame,
    and compares.

    * **Same area** (every pool within the tolerance of the common area):
      exit 0.
    * **Different areas**: REFUSED, exit 3 — unless ``--clip-to-common`` is
      given, in which case the common area is written to that GeoJSON (named
      ``clip-to-common-assessed-area``) for the sweeps and scorers to clip
      to, the per-pool area removed is reported, and the exit is 0.
    * **An undetermined area** (no record, no declaration, no pass
      provenance): exit 4, loudly, unless ``--allow-undetermined`` is given,
      which records the pool as undetermined (never as the same area).

    ``--json`` writes the full comparison record, which ladder outputs embed.

Usage::

    python scripts/check_assessed_areas.py \\
        --frame inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \\
        --pool "K = 1=outputs/.../crops_k1_recovery-fixed" \\
        --pool "K = 5=outputs/.../crops" \\
        [--tolerance-km2 0.01] [--clip-to-common common.geojson] \\
        [--json comparison.json]

Created: 2026-10-07 (Session 163)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.lib_assessed_area import (  # noqa: E402
    COMMON_AREA_CLIP_NAME,
    DEFAULT_TOLERANCE_KM2,
    AssessedAreaMismatchError,
    AssessedAreaUndeterminedError,
    compare_assessed_areas,
    determine_assessed_area,
    write_area_geojson,
)

logger = logging.getLogger(__name__)

#: Exit codes.
EXIT_SAME = 0
EXIT_MISMATCH = 3
EXIT_UNDETERMINED = 4


def parse_pool(spec: str) -> tuple[str, str]:
    """Split ``LABEL=PATH`` (the label may contain spaces and ``=``-free text).

    Args:
        spec: The ``--pool`` argument.

    Returns:
        ``(label, path)``.

    Raises:
        argparse.ArgumentTypeError: If there is no ``=``.
    """
    if "=" not in spec:
        raise argparse.ArgumentTypeError(f"--pool needs LABEL=PATH, got {spec!r}")
    label, path = spec.rsplit("=", 1)
    return label.strip(), path.strip()


def main(argv: list[str] | None = None) -> int:
    """Run the check; see the module docstring for the exit codes."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pool", action="append", required=True, type=parse_pool,
                        help="LABEL=PATH of a crops dir, crop manifest or union (repeat)")
    parser.add_argument("--frame", default=None,
                        help="Scoring frame bounds; areas are compared within it")
    parser.add_argument("--tolerance-km2", type=float, default=DEFAULT_TOLERANCE_KM2)
    parser.add_argument("--clip-to-common", type=Path, default=None,
                        help="On a mismatch, write the common area here and pass")
    parser.add_argument("--allow-undetermined", action="store_true",
                        help="Record undetermined pools as such instead of exiting 4")
    parser.add_argument("--json", type=Path, default=None,
                        help="Write the comparison record here")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    areas = [determine_assessed_area(path, label=label) for label, path in args.pool]
    for area in areas:
        logger.info("%-12s %-16s %s km²  %s", area.label, area.method,
                    "—" if area.area_km2 is None else f"{area.area_km2:.4f}",
                    area.reason or (area.evidence[0] if area.evidence else ""))
    try:
        comparison = compare_assessed_areas(
            areas, frame=args.frame, tolerance_km2=args.tolerance_km2,
            clip_to_common=args.clip_to_common is not None,
            allow_undetermined=args.allow_undetermined,
        )
    except AssessedAreaUndeterminedError as exc:
        logger.error("%s", exc)
        return EXIT_UNDETERMINED
    except AssessedAreaMismatchError as exc:
        logger.error("%s", exc)
        if args.json:
            args.json.write_text(json.dumps(exc.comparison, indent=2) + "\n")
        return EXIT_MISMATCH
    record = comparison.record
    if args.clip_to_common is not None and comparison.common is not None:
        write_area_geojson(comparison.common, args.clip_to_common,
                           name=COMMON_AREA_CLIP_NAME)
        record["clip_geojson"] = str(args.clip_to_common)
    logger.info("status: %s (common %s km², max excess %s km², tolerance %s km²)",
                record["status"], record["common_area_km2"], record["max_excess_km2"],
                record["tolerance_km2"])
    if args.json:
        args.json.write_text(json.dumps(record, indent=2) + "\n")
    return EXIT_SAME


if __name__ == "__main__":
    raise SystemExit(main())
