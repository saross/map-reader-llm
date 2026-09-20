#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
55maps-t0.3-extract-new-candidates.py — Append new consensus candidates to crops dir
====================================================================================

Purpose
-------
After a proposer-recovery + consensus re-run, the new consensus geojson may
contain features that did not exist in the original consensus. This script:

1. Loads the EXISTING ``candidate_manifest.json`` (from crops dir)
2. Loads the NEW consensus geojson
3. Spatial-matches the new features to existing candidates **one to one**
   (nearest pair first, 20 m tolerance, each existing candidate claimable
   exactly once)
4. **Refreshes the ``properties`` of every matched candidate** from the
   consensus feature that claimed it, so the post-recovery ``vote_count``,
   ``contributing_passes`` and ``cluster_size`` replace the pre-recovery ones
5. For unmatched new features, assigns new candidate IDs (continuing from
   the maximum existing ID + 1) and extracts their crops
6. Writes an UPDATED ``candidate_manifest.json`` — refreshed entries in
   place, new entries appended
7. Backs up the original manifest with a ``.pre-recovery-{ts}.backup`` suffix

This preserves the ID assignments of all existing candidates so that the
existing ``probabilities.json`` (verifier output) remains valid; only NEW
candidates need verification.

Why steps 3 and 4 read as they do — the 2026-05-03 defect
---------------------------------------------------------
Before 2026-09-20 this script took the **first** existing candidate within the
tolerance and never touched a matched entry's ``properties``. Both halves were
wrong, and ``results/im-june-pool-grid-2026-09-20/findings.md`` § 7 measures
the damage:

* **No refresh.** Five legacy manifests carry a ``vote_count`` one *low* on 15
  to 110 candidates each: the recovery campaign added a pass to those clusters
  and the manifest was never told. The manifest is the file the verifier is
  handed and the file the boards read, so those runs' vote histograms disagree
  with their own consensus union.
* **Greedy first match.** The match radius equals the clustering radius, so two
  distinct consensus clusters can both fall inside one manifest entry's radius
  and the first one to be tested wins. In ``55maps-text-high-generalisation``
  two clusters 17.29 m apart both matched candidate 505
  (``K-35-051-4_x1344_y3360.png``); the second was never extracted and has
  never been verified. That run's own ``recovery_history`` books the
  impossibility — ``existing_candidates`` 9,131 against ``matched_to_existing``
  9,132.

Matching is by Euclidean distance on UTM (EPSG:32635) centroids: every pair
inside the tolerance is sorted by distance and claimed nearest-first, so no
manifest entry can absorb two consensus features and no consensus feature can
be silently dropped. A manifest entry with more than one consensus feature
inside the radius is **ambiguous**; it is logged with its distances and
recorded in ``recovery_history`` even when the assignment resolves it.

A refresh is a **merge**, not a replacement: every key the consensus feature
carries overwrites the manifest's copy, and every key the manifest holds that
the consensus does not (verification-derived fields, for instance) survives.
The entry's identity — ``candidate_id``, ``crop_file`` — and the
``source_tile`` the crop on disk was actually cut from are never rewritten.

Usage
-----
    python3 scripts/55maps-t0.3-extract-new-candidates.py \\
        --consensus outputs/.../consensus/consensus-4of5.geojson \\
        --crops-dir outputs/.../crops \\
        --rasters-dir inputs/rasters/Russian1981_32635 \\
        --tiles-dir inputs/tiles_384_55maps \\
        --padding 75
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

# Project lib for raster cropping (shared with extract_candidates.py)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# Import deferred to runtime so that --help doesn't trigger heavy imports
DISTANCE_THRESHOLD_METRES = 20.0

#: Property keys a refresh must not rewrite. ``source_tile`` is pinned because
#: the PNG on disk was cut from that tile: a re-merged cluster may list its
#: tiles in a different order, and re-pointing the entry would misdescribe a
#: crop nobody is going to re-cut.
PINNED_PROPERTY_KEYS: tuple[str, ...] = ("source_tile",)


def _euclid(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


@lru_cache(maxsize=1)
def _utm_transformer() -> Any:
    """Build (once) the EPSG:4326 → EPSG:32635 transformer."""
    from pyproj import Transformer
    return Transformer.from_crs("EPSG:4326", "EPSG:32635", always_xy=True)


def _centroid_4326_to_utm(lon: float, lat: float) -> tuple[float, float]:
    """Project EPSG:4326 (lon, lat) to EPSG:32635 (UTM zone 35N, metres)."""
    return _utm_transformer().transform(lon, lat)


def _within_radius_pairs(
    consensus_points: Sequence[tuple[float, float]],
    existing_points: Sequence[tuple[float, float]],
    threshold: float,
) -> list[tuple[float, int, int]]:
    """Every (distance, consensus position, existing position) inside ``threshold``.

    Uses a k-d tree when SciPy is importable — the pool sizes here run to tens
    of thousands of points on each side — and falls back to the brute-force
    double loop otherwise, which is what this script did before the k-d tree.

    Args:
        consensus_points: UTM centroids of the new consensus features.
        existing_points: UTM centroids of the existing manifest entries.
        threshold: Match radius in metres.

    Returns:
        Unsorted list of ``(distance_m, consensus_index, existing_index)``.
    """
    if not consensus_points or not existing_points:
        return []

    try:
        import numpy as np
        from scipy.spatial import cKDTree
    except ImportError:  # pragma: no cover - SciPy is a declared dependency
        return [
            (d, ci, ei)
            for ci, cpt in enumerate(consensus_points)
            for ei, ept in enumerate(existing_points)
            if (d := _euclid(cpt, ept)) <= threshold
        ]

    tree = cKDTree(np.asarray(existing_points, dtype=float))
    neighbours = tree.query_ball_point(
        np.asarray(consensus_points, dtype=float), r=threshold,
    )
    return [
        (_euclid(consensus_points[ci], existing_points[ei]), ci, int(ei))
        for ci, hits in enumerate(neighbours)
        for ei in hits
    ]


def match_one_to_one(
    consensus_points: Sequence[tuple[float, float]],
    existing_points: Sequence[tuple[float, float]],
    threshold: float = DISTANCE_THRESHOLD_METRES,
    consensus_ids: Sequence[Any] | None = None,
    existing_ids: Sequence[Any] | None = None,
) -> tuple[dict[int, int], list[dict[str, Any]]]:
    """Assign consensus features to manifest entries, one to one.

    Every pair inside ``threshold`` is sorted by distance and claimed
    nearest-first; once a manifest entry is claimed it is out of the running,
    so two consensus clusters inside one entry's radius produce one match and
    one unassigned feature (which the caller then extracts) rather than a
    silent drop.

    Args:
        consensus_points: UTM centroids of the new consensus features.
        existing_points: UTM centroids of the existing manifest entries.
        threshold: Match radius in metres (default 20 m, the clustering
            radius the unions themselves were built at).
        consensus_ids: Labels for the consensus features, used only when
            reporting ambiguity. Defaults to their positions.
        existing_ids: Labels for the manifest entries (their
            ``candidate_id``), used only when reporting ambiguity. Defaults
            to their positions.

    Returns:
        ``(assignment, ambiguous)`` where ``assignment`` maps a consensus
        position to the existing position that claimed it, and ``ambiguous``
        holds one record per manifest entry that had more than one consensus
        feature inside ``threshold`` — the case that silently lost a
        candidate before 2026-09-20.

    Example:
        >>> match_one_to_one([(0.0, 0.0)], [(1.0, 0.0)], 20.0)
        ({0: 0}, [])
    """
    pairs = _within_radius_pairs(consensus_points, existing_points, threshold)

    # Every consensus feature inside each entry's radius, for the audit block.
    within: dict[int, list[tuple[float, int]]] = {}
    for distance, ci, ei in pairs:
        within.setdefault(ei, []).append((distance, ci))

    # Nearest pair first; ties broken deterministically by position.
    pairs.sort(key=lambda p: (p[0], p[1], p[2]))
    assignment: dict[int, int] = {}
    claimed: set[int] = set()
    for _distance, ci, ei in pairs:
        if ci in assignment or ei in claimed:
            continue
        assignment[ci] = ei
        claimed.add(ei)

    def _cid(pos: int) -> Any:
        return consensus_ids[pos] if consensus_ids is not None else pos

    def _eid(pos: int) -> Any:
        return existing_ids[pos] if existing_ids is not None else pos

    ambiguous: list[dict[str, Any]] = []
    for ei in sorted(within):
        hits = sorted(within[ei])
        if len(hits) < 2:
            continue
        ambiguous.append({
            "candidate_id": _eid(ei),
            "existing_index": ei,
            "n_features_within_radius": len(hits),
            "features": [
                {
                    "feature_id": _cid(ci),
                    "distance_m": round(distance, 3),
                    "assigned": assignment.get(ci) == ei,
                }
                for distance, ci in hits
            ],
        })
    return assignment, ambiguous


def refresh_entry_properties(
    entry: dict[str, Any],
    consensus_properties: dict[str, Any] | None,
) -> tuple[bool, Any, Any]:
    """Merge a consensus feature's properties into a matched manifest entry.

    The merge overwrites every key the consensus carries and keeps every key
    it does not — so a verification-derived field written onto the entry
    survives a refresh — except for :data:`PINNED_PROPERTY_KEYS`, which
    describe the crop on disk rather than the cluster.

    Args:
        entry: The manifest candidate entry, mutated in place.
        consensus_properties: ``properties`` of the consensus feature that
            claimed this entry.

    Returns:
        ``(changed, vote_count_before, vote_count_after)``.

    Example:
        >>> e = {"candidate_id": 7, "properties": {"vote_count": 4}}
        >>> refresh_entry_properties(e, {"vote_count": 5})
        (True, 4, 5)
    """
    before: dict[str, Any] = dict(entry.get("properties") or {})
    merged = {**before, **(consensus_properties or {})}
    for key in PINNED_PROPERTY_KEYS:
        if key in before:
            merged[key] = before[key]
        elif entry.get(key) is not None:
            merged[key] = entry[key]
    entry["properties"] = merged
    return merged != before, before.get("vote_count"), merged.get("vote_count")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--consensus", required=True, type=Path,
        help="Path to the NEW consensus geojson (post-recovery)",
    )
    parser.add_argument(
        "--crops-dir", required=True, type=Path,
        help="Existing crops directory (contains candidate_manifest.json)",
    )
    parser.add_argument(
        "--rasters-dir", required=True, type=Path,
        help="Source rasters directory (for crop extraction)",
    )
    parser.add_argument(
        "--tiles-dir", required=True, type=Path,
        help="Tiles directory (fallback for crop extraction)",
    )
    parser.add_argument(
        "--padding", type=int, default=75,
        help="Crop half-size in pixels (default: 75 → 150x150)",
    )
    parser.add_argument(
        "--distance-threshold", type=float, default=DISTANCE_THRESHOLD_METRES,
        help="Spatial match tolerance in metres (default: 20.0)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Identify new candidates without extracting crops or writing",
    )
    args = parser.parse_args()

    manifest_path = args.crops_dir / "candidate_manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    # Load existing manifest
    with open(manifest_path) as f:
        manifest = json.load(f)
    existing_candidates: list[dict[str, Any]] = manifest.get("candidates", [])
    existing_n = len(existing_candidates)
    next_id = max((c["candidate_id"] for c in existing_candidates), default=-1) + 1
    print(f"Existing candidates: {existing_n} (max id={next_id - 1})")

    # Existing candidates' UTM centroids and ids
    existing_utm = [
        (c["centroid_x"], c["centroid_y"]) for c in existing_candidates
    ]
    existing_ids = [c.get("candidate_id") for c in existing_candidates]

    # Load new consensus
    with open(args.consensus) as f:
        consensus = json.load(f)
    new_features = consensus.get("features", [])
    print(f"New consensus features: {len(new_features)}")

    # Project every usable consensus feature to UTM, keeping its file index
    feature_points: list[tuple[int, dict[str, Any], tuple[float, float]]] = []
    skipped_geometry = 0
    for idx, feat in enumerate(new_features):
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates")
        if not coords or len(coords) < 2:
            skipped_geometry += 1
            continue
        # Consensus geojson is in EPSG:4326 (per merge_passes.py); reproject to UTM
        x4326, y4326 = coords[0], coords[1]
        if abs(x4326) <= 180 and abs(y4326) <= 90:
            ux, uy = _centroid_4326_to_utm(x4326, y4326)
        else:
            # Already UTM
            ux, uy = x4326, y4326
        feature_points.append((idx, feat, (ux, uy)))
    if skipped_geometry:
        print(f"  skipped (no usable geometry): {skipped_geometry}")

    # One-to-one assignment, nearest pair first
    assignment, ambiguous = match_one_to_one(
        [point for _, _, point in feature_points],
        existing_utm,
        threshold=args.distance_threshold,
        consensus_ids=[idx for idx, _, _ in feature_points],
        existing_ids=existing_ids,
    )
    matched = len(assignment)
    new_only_features = [
        feature_points[pos]
        for pos in range(len(feature_points))
        if pos not in assignment
    ]

    # Refresh the properties of every matched entry from its consensus feature
    refreshed = 0
    vote_changes: list[dict[str, Any]] = []
    for pos, existing_index in sorted(assignment.items()):
        _idx, feat, _point = feature_points[pos]
        entry = existing_candidates[existing_index]
        changed, votes_before, votes_after = refresh_entry_properties(
            entry, feat.get("properties", {}),
        )
        if changed:
            refreshed += 1
        if votes_before != votes_after:
            vote_changes.append({
                "candidate_id": entry.get("candidate_id"),
                "vote_count_before": votes_before,
                "vote_count_after": votes_after,
            })

    print(f"  matched to existing: {matched} (one-to-one)")
    print(f"  properties refreshed: {refreshed}")
    print(f"  vote_count changed:   {len(vote_changes)}")
    print(f"  truly new: {len(new_only_features)}")

    if ambiguous:
        print(
            f"  AMBIGUOUS: {len(ambiguous)} existing candidate(s) had more than "
            f"one consensus feature within {args.distance_threshold:g} m",
        )
        for record in ambiguous:
            detail = ", ".join(
                f"feature {hit['feature_id']} at {hit['distance_m']:.2f} m"
                f"{' (matched)' if hit['assigned'] else ' (unassigned → extracted)'}"
                for hit in record["features"]
            )
            print(f"    candidate {record['candidate_id']}: {detail}")

    if args.dry_run:
        for idx, feat, (ux, uy) in new_only_features[:20]:
            print(f"  new: feature_idx={idx}, utm=({ux:.1f}, {uy:.1f}), "
                  f"props={feat.get('properties', {})}")
        print("[DRY RUN] manifest not written")
        return 0

    # Extract crops for new candidates only.
    # Re-use extract_candidates' crop_region helper for consistency.
    crops_subdir = args.crops_dir / "crops"
    new_manifest_entries: list[dict[str, Any]] = []
    successful = 0
    failed = 0

    if new_only_features:
        from scripts.extract_candidates import (
            crop_region, get_tile_path, resolve_raster_path, tile_id_to_map_name,
        )

        crops_subdir.mkdir(parents=True, exist_ok=True)
        raster_cache: dict[str, Path | None] = {}

        for idx, feat, (ux, uy) in new_only_features:
            props = feat.get("properties", {})
            # Source tile selection: prefer first source_tile from cluster
            src_tiles = props.get("source_tiles", [])
            source_tile = src_tiles[0] if src_tiles else None
            if not source_tile:
                print(f"  skipping new feature {idx}: no source_tile")
                failed += 1
                continue

            # Resolve raster path (cache by map name)
            map_name = tile_id_to_map_name(source_tile)
            if map_name not in raster_cache:
                raster_cache[map_name] = resolve_raster_path(source_tile, args.rasters_dir)
            raster_path = raster_cache[map_name]
            crop_source = raster_path
            used_raster = raster_path is not None
            if not raster_path:
                crop_source = get_tile_path(source_tile, args.tiles_dir)
                if not crop_source:
                    print(f"  skipping new feature {idx}: no raster or tile for {source_tile}")
                    failed += 1
                    continue

            # Assign candidate ID
            cid = next_id
            next_id += 1
            crop_filename = f"candidate_{cid:05d}.png"
            crop_path = crops_subdir / crop_filename

            if crop_region(crop_source, (ux, uy), args.padding, crop_path):
                new_entry = {
                    "candidate_id": cid,
                    "crop_file": f"crops/{crop_filename}",
                    "source_tile": source_tile,
                    "centroid_x": ux,
                    "centroid_y": uy,
                    "cropped_from": "raster" if used_raster else "tile",
                    "properties": {**props, "source_tile": source_tile},
                }
                new_manifest_entries.append(new_entry)
                successful += 1
            else:
                failed += 1

    if not (new_manifest_entries or refreshed or ambiguous):
        print("No new candidates and no properties to refresh — manifest untouched.")
        return 0

    # Append to manifest, back up original first
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup_path = manifest_path.with_name(
        f"candidate_manifest.json.pre-recovery-{timestamp}.backup",
    )
    shutil.copy(manifest_path, backup_path)
    print(f"Backup: {backup_path.name}")

    manifest["candidates"].extend(new_manifest_entries)
    manifest["successful_extractions"] = (
        manifest.get("successful_extractions", existing_n) + successful
    )
    manifest["failed_extractions"] = (
        manifest.get("failed_extractions", 0) + failed
    )
    # The manifest's source set is now the consensus file just read, so
    # ``total_detections`` is that file's feature count — not the previous
    # value plus the new ones, which only agreed by arithmetic accident.
    manifest["total_detections"] = len(new_features)

    # Add a recovery_history audit entry
    history = manifest.setdefault("recovery_history", [])
    history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "consensus_source": str(args.consensus),
        "existing_candidates": existing_n,
        "new_consensus_features": len(new_features),
        "matched_to_existing": matched,
        "matching": "one-to-one-nearest",
        "distance_threshold_m": args.distance_threshold,
        "properties_refreshed": refreshed,
        "vote_count_changed": len(vote_changes),
        "vote_count_changes": vote_changes,
        "ambiguous_matches": ambiguous,
        "new_extracted": successful,
        "new_extraction_failed": failed,
    })

    tmp_path = manifest_path.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(manifest, f, indent=2)
    tmp_path.rename(manifest_path)

    print(f"Updated manifest: {manifest_path}")
    print(f"  total candidates now: {len(manifest['candidates'])}")
    print(f"  properties refreshed: {refreshed}")
    print(f"  vote_count changed: {len(vote_changes)}")
    print(f"  new extracted: {successful}")
    print(f"  new failed: {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
