#!/usr/bin/env python3
"""
H13 Tier-0 sweep: can aggregation recover the precision that overlap costs?

The registered H13 result is that F1 falls monotonically as tile overlap
rises (`results/h13-overlap-2026-08-18/findings.md`): denser tiling buys
recall but loses more precision. That result is for *raw single-pass*
scoring. This sweep asks the obvious follow-up at zero API cost — whether
a precision filter changes the ranking, i.e. whether the optimal overlap
depends on the aggregation stage rather than being monotone.

Two orthogonal filters are swept, and their interaction:

**Within-pass cross-tile corroboration** (``c``) — new, and available
*only* because the tiles overlap. When several overlapping tiles are each
sent to the model independently, a real mound tends to be reported by
every tile that contains it while a hallucination tends not to recur at
the same coordinates in a neighbour's independent call. The within-pass
deduplication already records how many raw detections merged into each
cluster (``cluster_size``); requiring ``cluster_size >= c`` turns that
into a precision filter. Its strength scales with the factor under test:
6 % of arm A's deduplicated detections are corroborated by a second tile
against 37 % of arm C's.

**Across-pass consensus** (``k``) — the study's usual lever: pool the
arm's passes, cluster at 20 m, and keep clusters carrying votes from at
least ``k`` distinct passes (preregistration § 8.5 Steps 2-5).

Every arm is swept over the full c x k grid, so a like-for-like
comparison exists at each filter strength. Scoring is unchanged from the
main analysis: the common A n B n C footprint, 20 m matching, the same
evaluator.

Note on classification: this sweep is a POST-HOC extension (E41-class)
beyond H13's registered single-factor overlap design, which registers no
aggregation stage. It must not be reported under the registered-
exploratory H13 row.

Usage::

    python scripts/h13_aggregation_sweep.py \\
        --scoring-dir outputs/h13/scoring \\
        --output-dir results/h13-overlap-2026-08-18/tier0-aggregation

Inputs:
    - outputs/h13/scoring/common/arm{A,B,C}/run_N/detections_dedup.geojson
    - outputs/h13/scoring/bounds/h13_common_bounds.geojson
    - inputs/vectors/references/mounds-reference.geojson

Outputs:
    - cells/{arm}_c{c}_k{k}.geojson - aggregated detection set per cell
    - tier0_sweep.json              - metrics for every cell
    - tier0_sweep.md                - the grid, human-readable

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import Point, mapping

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (  # noqa: E402
    bootstrap_ci,
    calculate_f1_internal,
)
from scripts.merge_passes import cluster_across_passes  # noqa: E402
from scripts.prepare_h13_scoring import (  # noqa: E402
    CRS_EPSG,
    CRS_URN,
    assign_primary_tiles,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

RUNS = ("run_1", "run_2", "run_3")
ARMS = {"armA": 0.125, "armB": 0.25, "armC": 0.50}
CORROBORATION = (1, 2, 3)
VOTES = (1, 2, 3)
BUFFER_M = 20
DEDUP_M = 20.0
SEED = 42
N_BOOTSTRAP = 1000
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"


def load_arm_passes(scoring_dir: Path, arm: str) -> dict[str, list[dict]]:
    """Load one arm's deduplicated passes in the shape ``cluster_across_passes`` wants.

    Args:
        scoring_dir: Root of the prepared scoring artefacts.
        arm: Arm label (``armA``/``armB``/``armC``).

    Returns:
        Mapping pass id -> detection dicts carrying centroid, label,
        source tiles, and the within-pass ``cluster_size``.
    """
    passes: dict[str, list[dict]] = {}
    for run in RUNS:
        path = scoring_dir / "common" / arm / run / "detections_dedup.geojson"
        data = json.loads(path.read_text())
        dets = []
        for f in data["features"]:
            x, y = f["geometry"]["coordinates"]
            props = f["properties"]
            dets.append({
                "centroid": (x, y),
                "label": props.get("label", "mound"),
                "source_tiles": (props.get("origin_tiles") or "").split(";"),
                "cluster_size": int(props.get("cluster_size", 1)),
            })
        passes[run] = dets
    return passes


def aggregate(
    passes: dict[str, list[dict]], min_corroboration: int, min_votes: int,
) -> list[dict]:
    """Apply the corroboration filter, then across-pass consensus.

    Order matters and is deliberate: corroboration is a *within-pass*
    property, so it must be applied before pooling, exactly as it would be
    in a deployed pipeline where each pass is filtered as it lands.

    Args:
        passes: Per-pass detections from :func:`load_arm_passes`.
        min_corroboration: Minimum overlapping tiles that must have
            reported a detection for it to survive (1 = no filter).
        min_votes: Minimum distinct passes a cluster must carry (1 = union).

    Returns:
        Surviving cluster dicts with centroid, label, and vote count.
    """
    filtered = {
        pid: [d for d in dets if d["cluster_size"] >= min_corroboration]
        for pid, dets in passes.items()
    }
    clusters = cluster_across_passes(filtered, distance_thresh=DEDUP_M)
    return [c for c in clusters if c["vote_count"] >= min_votes]


def write_cell(clusters: list[dict], bounds: gpd.GeoDataFrame, target: Path) -> gpd.GeoDataFrame:
    """Write one swept cell as a scorable GeoJSON and return it loaded.

    Args:
        clusters: Surviving clusters for the cell.
        bounds: Common-scope carrier bounds, for tile assignment.
        target: Output path.

    Returns:
        The cell as a GeoDataFrame with a ``source_tile`` column.
    """
    if clusters:
        gdf = gpd.GeoDataFrame(
            {
                "label": [c["label"] for c in clusters],
                "votes": [c["vote_count"] for c in clusters],
            },
            geometry=[Point(c["centroid"]) for c in clusters],
            crs=f"EPSG:{CRS_EPSG}",
        )
        gdf["source_tile"] = assign_primary_tiles(gdf, bounds)
    else:
        gdf = gpd.GeoDataFrame(
            {"label": [], "votes": [], "source_tile": []},
            geometry=[], crs=f"EPSG:{CRS_EPSG}",
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": CRS_URN}},
        "processed_tiles": sorted(bounds["tile_name"].tolist()),
        "features": [
            {
                "type": "Feature",
                "geometry": mapping(row.geometry),
                "properties": {
                    "source_tile": row["source_tile"],
                    "label": row["label"],
                    "subtype": row["label"],
                    "votes": int(row["votes"]),
                },
            }
            for _, row in gdf.iterrows()
        ],
    }))
    return gdf


def main() -> int:
    """Run the c x k sweep across all three arms and write the outputs.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="H13 Tier-0 aggregation sweep (corroboration x consensus).")
    parser.add_argument(
        "--scoring-dir", type=Path,
        default=PROJECT_ROOT / "outputs/h13/scoring")
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results/h13-overlap-2026-08-18/tier0-aggregation")
    parser.add_argument("--bootstrap", type=int, default=N_BOOTSTRAP)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    bounds = gpd.read_file(
        args.scoring_dir / "bounds" / "h13_common_bounds.geojson")
    gdf_ref = gpd.read_file(GROUND_TRUTH)

    cells: list[dict[str, Any]] = []
    for arm in ARMS:
        passes = load_arm_passes(args.scoring_dir, arm)
        for c in CORROBORATION:
            for k in VOTES:
                clusters = aggregate(passes, c, k)
                gdf = write_cell(
                    clusters, bounds,
                    args.output_dir / "cells" / f"{arm}_c{c}_k{k}.geojson")
                if gdf.empty:
                    p = r = f1 = 0.0
                    ci = {}
                else:
                    p, r, f1 = calculate_f1_internal(
                        gdf, gdf_ref, bounds, buffer_metres=BUFFER_M)
                    ci = bootstrap_ci(
                        gdf, gdf_ref, bounds, n_iterations=args.bootstrap,
                        random_seed=SEED, buffer_metres=BUFFER_M,
                        processed_tiles=set(bounds["tile_name"]),
                    )
                cells.append({
                    "arm": arm,
                    "overlap_fraction": ARMS[arm],
                    "min_corroboration": c,
                    "min_votes": k,
                    "n_detections": int(len(gdf)),
                    "precision": p, "recall": r, "f1": f1,
                    "f1_ci_lower": (ci.get("f1") or {}).get("ci_lower"),
                    "f1_ci_upper": (ci.get("f1") or {}).get("ci_upper"),
                })
                logger.info(
                    "%s c>=%d k>=%d: n=%4d  P=%.4f R=%.4f F1=%.4f",
                    arm, c, k, len(gdf), p, r, f1,
                )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": (
            "POST-HOC extension (E41-class) beyond H13's registered "
            "single-factor overlap design; not covered by the "
            "registered-exploratory H13 row."
        ),
        "scope": {
            "name": "common (arm A n arm B n arm C)",
            "carrier_tiles": len(bounds),
            "buffer_metres": BUFFER_M,
            "dedup_metres": DEDUP_M,
            "passes_per_arm": len(RUNS),
        },
        "cells": cells,
    }
    (args.output_dir / "tier0_sweep.json").write_text(json.dumps(payload, indent=2))

    # Best cell per arm, and the raw single-pass reference point.
    lines = ["# H13 Tier-0 aggregation sweep", "",
             "Post-hoc extension; see `tier0_sweep.json`.", "",
             "| arm | c | k | n | P | R | F1 |", "|---|---:|---:|---:|---:|---:|---:|"]
    for cell in cells:
        lines.append(
            f"| {cell['arm']} | {cell['min_corroboration']} | {cell['min_votes']} | "
            f"{cell['n_detections']} | {cell['precision']:.4f} | "
            f"{cell['recall']:.4f} | {cell['f1']:.4f} |")
    (args.output_dir / "tier0_sweep.md").write_text("\n".join(lines) + "\n")

    for arm in ARMS:
        best = max((c for c in cells if c["arm"] == arm), key=lambda x: x["f1"])
        logger.info(
            "BEST %s: c>=%d k>=%d -> F1=%.4f (P=%.4f R=%.4f)",
            arm, best["min_corroboration"], best["min_votes"],
            best["f1"], best["precision"], best["recall"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
