#!/usr/bin/env python3
# ============================================================================
# diagnose_consensus_dedup_exposure.py
# ----------------------------------------------------------------------------
# Explain why six CONSENSUS conditions appear in the duplicate-exposure register
# at all.
#
# THE ANOMALY
# -----------
# ``results/scoring-sensitivity-2026-08-18/exposure-survey.json`` flags 155 of
# 333 conditions as carrying features within the 20 m deduplication radius of
# another feature in the same artefact. Six of them are ``architecture:
# consensus`` — and consensus artefacts are built by ``scripts/merge_passes.py``,
# which applies the preregistered within-pass deduplication (§ 8.5 Step 1) at
# ``merge_passes.py`` Step 1 before cross-pass clustering. A deduplicated
# artefact should carry no such pairs, so either the survey has false positives,
# or these six took a different path, or deduplication is not idempotent.
#
# WHAT THIS SCRIPT ESTABLISHES
# ----------------------------
# For each flagged artefact it reports, from the file itself:
#
# 1. **Provenance fingerprint** — whether the feature properties are the ones
#    ``merge_passes.apply_threshold`` writes (``vote_count``,
#    ``contributing_passes``, ``source_tiles``, ``cluster_size``,
#    ``total_passes``). A hand-built or weighted-box-fusion artefact would not
#    carry that exact set.
# 2. **Residual-pair anatomy** — every pair of features within 20 m, with each
#    member's vote count and cluster size, and whether the two share any
#    contributing pass or source tile. Two clusters that share a contributing
#    pass cannot be "the same detection seen twice by one pass"; they are two
#    clusters whose MEAN centroids drifted within 20 m of each other after
#    ``cluster_across_passes`` recentred them.
# 3. **The vote-threshold decay curve** — because ``apply_threshold`` filters one
#    cluster list by ``vote_count >= K``, the consensus outputs at increasing K
#    are nested subsets of the same artefact. Recounting the residual pairs on
#    each subset shows directly whether exposure is a low-threshold phenomenon.
#
# Together these separate the three candidate mechanisms: a different code path,
# a survey false positive, or the residual non-idempotency of greedy star
# clustering under mean-centroid recentring.
#
# COST: US$0.00. COMPUTE: sapphire.
#
# Usage:
#     python scripts/diagnose_consensus_dedup_exposure.py \
#         --output results/dedup-metric-impact-2026-08-18/consensus-mechanism.json
#
# Author: Shawn Ross & Claude (Anthropic)
# Created: 2026-08-18 (Session 136)
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.evaluate_detections import load_geojson  # noqa: E402
from scripts.merge_passes import DISTANCE_THRESHOLD_METRES  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_SURVEY = (
    PROJECT_ROOT / "results/scoring-sensitivity-2026-08-18/exposure-survey.json"
)

#: Property set written by ``merge_passes.apply_threshold``.
MERGE_PASSES_PROPERTIES = {
    "subtype",
    "confidence",
    "vote_count",
    "total_passes",
    "contributing_passes",
    "source_tiles",
    "cluster_size",
}


def _as_list(value: Any) -> list[str]:
    """Coerce a GeoJSON property that may be a list or a JSON string to a list.

    Some GeoJSON writers serialise list-valued properties as JSON strings when
    round-tripped through a driver that has no list type. Both forms occur among
    the committed artefacts, so both are accepted.

    Args:
        value: Property value.

    Returns:
        List of strings (empty when the value is missing or unparseable).
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return [value]
        return [str(v) for v in parsed] if isinstance(parsed, list) else [str(parsed)]
    return [str(value)]


def pair_report(
    gdf,
    radius: float,
) -> dict[str, Any]:
    """Enumerate every within-radius feature pair and describe its members.

    Args:
        gdf: Detections in a metric CRS.
        radius: Pair radius in metres.

    Returns:
        Dict with the pair count, the involved-feature count, distance
        summaries, and per-pair anatomy.
    """
    centroids = gdf.geometry.centroid
    points = np.column_stack([centroids.x.values, centroids.y.values])
    pairs = sorted(cKDTree(points).query_pairs(radius)) if len(points) > 1 else []

    involved: set[int] = set()
    anatomy = []
    distances = []
    shared_pass = 0
    shared_tile = 0
    both_singleton = 0
    for a, b in pairs:
        involved.update((a, b))
        dist = float(np.hypot(*(points[a] - points[b])))
        distances.append(dist)
        row_a, row_b = gdf.iloc[a], gdf.iloc[b]
        passes_a, passes_b = (
            set(_as_list(row_a.get("contributing_passes"))),
            set(_as_list(row_b.get("contributing_passes"))),
        )
        tiles_a, tiles_b = (
            set(_as_list(row_a.get("source_tiles"))),
            set(_as_list(row_b.get("source_tiles"))),
        )
        size_a = row_a.get("cluster_size")
        size_b = row_b.get("cluster_size")
        if passes_a & passes_b:
            shared_pass += 1
        if tiles_a & tiles_b:
            shared_tile += 1
        if (size_a == 1) and (size_b == 1):
            both_singleton += 1
        anatomy.append({
            "distance_m": round(dist, 3),
            "vote_a": row_a.get("vote_count"),
            "vote_b": row_b.get("vote_count"),
            "cluster_size_a": None if size_a is None else int(size_a),
            "cluster_size_b": None if size_b is None else int(size_b),
            "n_shared_contributing_passes": len(passes_a & passes_b),
            "n_shared_source_tiles": len(tiles_a & tiles_b),
        })

    return {
        "n_features": int(len(gdf)),
        "n_pairs": len(pairs),
        "n_features_involved": len(involved),
        "involved_fraction": round(len(involved) / len(gdf), 6) if len(gdf) else 0.0,
        "distance_min_m": round(min(distances), 3) if distances else None,
        "distance_median_m": round(float(np.median(distances)), 3) if distances else None,
        "distance_max_m": round(max(distances), 3) if distances else None,
        "n_pairs_sharing_a_contributing_pass": shared_pass,
        "n_pairs_sharing_a_source_tile": shared_tile,
        "n_pairs_both_singleton_clusters": both_singleton,
        "pairs": anatomy,
    }


def threshold_decay(gdf, radius: float) -> list[dict[str, Any]]:
    """Recount residual pairs on each nested vote-threshold subset.

    ``merge_passes.apply_threshold`` filters ONE cluster list by
    ``vote_count >= K``, so the consensus outputs across K are nested subsets of
    the same artefact and can be reconstructed by filtering in place. If the
    residual pairs are a low-threshold phenomenon, the involved fraction falls
    away as K rises.

    Args:
        gdf: A consensus artefact carrying ``vote_count``.
        radius: Pair radius in metres.

    Returns:
        One row per vote threshold present in the artefact.
    """
    if "vote_count" not in gdf.columns:
        return []
    rows = []
    votes = sorted({int(v) for v in gdf["vote_count"].dropna()})
    for k in votes:
        subset = gdf[gdf["vote_count"] >= k]
        if len(subset) < 2:
            rows.append({"vote_threshold": k, "n_features": int(len(subset)),
                         "n_pairs": 0, "involved_fraction": 0.0})
            continue
        centroids = subset.geometry.centroid
        points = np.column_stack([centroids.x.values, centroids.y.values])
        pairs = cKDTree(points).query_pairs(radius)
        involved = {i for pair in pairs for i in pair}
        rows.append({
            "vote_threshold": k,
            "n_features": int(len(subset)),
            "n_pairs": len(pairs),
            "involved_fraction": round(len(involved) / len(subset), 6),
        })
    return rows


def diagnose(path: Path, radius: float) -> dict[str, Any]:
    """Run the full diagnosis on one consensus artefact.

    Args:
        path: Detection GeoJSON.
        radius: Pair radius in metres.

    Returns:
        Diagnosis dict.
    """
    gdf = load_geojson(path)
    properties = set(gdf.columns) - {"geometry"}
    return {
        "detections": str(path),
        "properties": sorted(properties),
        "merge_passes_property_set_present": sorted(
            MERGE_PASSES_PROPERTIES - properties
        ) == [],
        "missing_merge_passes_properties": sorted(
            MERGE_PASSES_PROPERTIES - properties
        ),
        "has_source_tile_singular": "source_tile" in properties,
        "pair_report": pair_report(gdf, radius),
        "vote_threshold_decay": threshold_decay(gdf, radius),
    }


def main() -> int:
    """CLI entry point.

    Returns:
        Process exit code (0 on success).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--survey", type=Path, default=DEFAULT_SURVEY,
                        help="Exposure register naming the flagged conditions.")
    parser.add_argument("--radius", type=float, default=DISTANCE_THRESHOLD_METRES)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    survey = json.loads(args.survey.read_text())
    flagged = [
        c for c in survey["conditions"]
        if c["architecture"] == "consensus" and c["dedup_exposed"]
    ]
    logger.info("%d flagged consensus conditions", len(flagged))

    results = []
    for cond in flagged:
        logger.info("diagnosing %s", cond["condition_id"])
        entry = {
            "condition_id": cond["condition_id"],
            "survey_duplicate_fraction": cond["duplicate_fraction"],
            "survey_n_features": cond["n_features"],
            "artefacts": [
                diagnose(Path(p), args.radius) for p in cond["detection_paths"]
            ],
        }
        results.append(entry)

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "radius_metres": args.radius,
        "survey": str(args.survey),
        "conditions": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    logger.info("Wrote %s", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
