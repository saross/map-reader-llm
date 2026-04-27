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
3. Spatial-matches each new feature to existing candidates (20 m tolerance)
4. For unmatched new features, assigns new candidate IDs (continuing from
   the maximum existing ID + 1) and extracts their crops
5. Writes an UPDATED ``candidate_manifest.json`` with the new entries appended
6. Backs up the original manifest with a ``.pre-recovery-{ts}.backup`` suffix

This preserves the ID assignments of all existing candidates so that the
existing ``probabilities.json`` (verifier output) remains valid; only NEW
candidates need verification.

The matching is by Euclidean distance on UTM (EPSG:32635) centroids.

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
from pathlib import Path
from typing import Any

# Project lib for raster cropping (shared with extract_candidates.py)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# Import deferred to runtime so that --help doesn't trigger heavy imports
DISTANCE_THRESHOLD_METRES = 20.0


def _euclid(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _centroid_4326_to_utm(lon: float, lat: float) -> tuple[float, float]:
    """Project EPSG:4326 (lon, lat) to EPSG:32635 (UTM zone 35N, metres)."""
    from pyproj import Transformer
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32635", always_xy=True)
    return transformer.transform(lon, lat)


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
        help="Identify new candidates without extracting crops",
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

    # Build a spatial index of existing candidates (UTM centroids)
    existing_utm = [
        (c["centroid_x"], c["centroid_y"]) for c in existing_candidates
    ]

    # Load new consensus
    with open(args.consensus) as f:
        consensus = json.load(f)
    new_features = consensus.get("features", [])
    print(f"New consensus features: {len(new_features)}")

    # Match new features against existing
    new_only_features: list[tuple[int, dict[str, Any], tuple[float, float]]] = []
    matched = 0
    for idx, feat in enumerate(new_features):
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates")
        if not coords or len(coords) < 2:
            continue
        # Consensus geojson is in EPSG:4326 (per merge_passes.py); reproject to UTM
        x4326, y4326 = coords[0], coords[1]
        if abs(x4326) <= 180 and abs(y4326) <= 90:
            ux, uy = _centroid_4326_to_utm(x4326, y4326)
        else:
            # Already UTM
            ux, uy = x4326, y4326

        # Find any existing candidate within threshold
        match_idx = None
        for ei, (eux, euy) in enumerate(existing_utm):
            if _euclid((ux, uy), (eux, euy)) <= args.distance_threshold:
                match_idx = ei
                break
        if match_idx is not None:
            matched += 1
        else:
            new_only_features.append((idx, feat, (ux, uy)))

    print(f"  matched to existing: {matched}")
    print(f"  truly new: {len(new_only_features)}")

    if args.dry_run:
        for idx, feat, (ux, uy) in new_only_features[:20]:
            print(f"  new: feature_idx={idx}, utm=({ux:.1f}, {uy:.1f}), "
                  f"props={feat.get('properties', {})}")
        return 0

    if not new_only_features:
        print("No new candidates to extract.")
        return 0

    # Extract crops for new candidates only.
    # Re-use extract_candidates' crop_region helper for consistency.
    from scripts.extract_candidates import (
        crop_region, get_tile_path, resolve_raster_path, tile_id_to_map_name,
    )

    crops_subdir = args.crops_dir / "crops"
    crops_subdir.mkdir(parents=True, exist_ok=True)

    raster_cache: dict[str, Path | None] = {}
    new_manifest_entries: list[dict[str, Any]] = []
    successful = 0
    failed = 0

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
    manifest["total_detections"] = (
        manifest.get("total_detections", existing_n) + len(new_only_features)
    )

    # Add a recovery_history audit entry
    history = manifest.setdefault("recovery_history", [])
    history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "consensus_source": str(args.consensus),
        "existing_candidates": existing_n,
        "new_consensus_features": len(new_features),
        "matched_to_existing": matched,
        "new_extracted": successful,
        "new_extraction_failed": failed,
    })

    tmp_path = manifest_path.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(manifest, f, indent=2)
    tmp_path.rename(manifest_path)

    print(f"Updated manifest: {manifest_path}")
    print(f"  total candidates now: {len(manifest['candidates'])}")
    print(f"  new extracted: {successful}")
    print(f"  new failed: {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
