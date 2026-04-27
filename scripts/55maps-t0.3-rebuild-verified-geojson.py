#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
55maps-t0.3-rebuild-verified-geojson.py — Rebuild verified_detections.geojson
=============================================================================

Purpose
-------
After a recovery cycle (proposer + verifier patches), the
``verified_detections.geojson`` (the final filtered-by-vote-and-prob detection
set used by ``evaluate_detections.py``) must be rebuilt from the (possibly
extended) candidate manifest and the (possibly patched) probabilities.json.

This mirrors the in-process logic from
``run_generalisation.py:_build_verified_geojson()`` but is callable from a
shell script after partial-recovery.

Filter logic:
  Include candidate if BOTH:
    - vote_count >= --vote-threshold (e.g. 4 for 4-of-5)
    - mound_probability >= --prob-threshold (e.g. 0.15)

Output coordinates are EPSG:32635 (UTM zone 35N), matching the project
convention for downstream evaluation.

Usage
-----
    python3 scripts/55maps-t0.3-rebuild-verified-geojson.py \\
        --crops-dir outputs/.../crops \\
        --verified-dir outputs/.../verified \\
        --vote-threshold 4 \\
        --prob-threshold 0.15 \\
        --output outputs/.../verified/verified_detections.geojson
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--crops-dir", required=True, type=Path,
        help="Crops directory containing candidate_manifest.json",
    )
    parser.add_argument(
        "--verified-dir", required=True, type=Path,
        help="Verifier output directory containing probabilities.json",
    )
    parser.add_argument(
        "--vote-threshold", type=int, required=True,
        help="Minimum vote count to retain a candidate (e.g. 4 for 4-of-5)",
    )
    parser.add_argument(
        "--prob-threshold", type=float, required=True,
        help="Minimum verifier mound_probability to retain (e.g. 0.15)",
    )
    parser.add_argument(
        "--output", required=True, type=Path,
        help="Output path for verified_detections.geojson",
    )
    args = parser.parse_args()

    manifest = json.loads(
        (args.crops_dir / "candidate_manifest.json").read_text(encoding="utf-8"),
    )
    probs = json.loads(
        (args.verified_dir / "probabilities.json").read_text(encoding="utf-8"),
    )
    results = probs.get("results", {})

    features: list[dict[str, Any]] = []
    skipped_no_prob = 0
    skipped_low_vote = 0
    skipped_low_prob = 0
    for cand in manifest.get("candidates", []):
        cid = cand["candidate_id"]
        vote = cand.get("properties", {}).get("vote_count", 0)
        key = f"candidate_{cid:05d}"
        entry = results.get(key)
        if entry is None:
            skipped_no_prob += 1
            continue
        prob = entry.get("mound_probability")
        if prob is None:
            skipped_no_prob += 1
            continue
        if vote < args.vote_threshold:
            skipped_low_vote += 1
            continue
        if prob < args.prob_threshold:
            skipped_low_prob += 1
            continue
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [cand["centroid_x"], cand["centroid_y"]],
            },
            "properties": {
                "candidate_id": cid,
                "vote_count": vote,
                "probability": prob,
                "source_tile": cand.get("source_tile"),
            },
        })

    gj = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "EPSG:32635"},
        },
        "features": features,
    }

    # Backup existing output if present
    if args.output.exists():
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        backup = args.output.with_name(
            args.output.name + f".pre-recovery-{ts}.backup",
        )
        shutil.copy(args.output, backup)
        print(f"Backup: {backup.name}")

    # Atomic write — match the indent=2 style used by
    # run_generalisation.py:_build_verified_geojson() so the diff vs
    # the in-process build is empty in formatting.
    tmp = args.output.with_suffix(".geojson.tmp")
    with open(tmp, "w") as f:
        json.dump(gj, f, indent=2)
    tmp.rename(args.output)

    print(f"Wrote: {args.output}")
    print(f"  total candidates: {len(manifest.get('candidates', []))}")
    print(f"  retained features: {len(features)}")
    print(f"  skipped (no prob): {skipped_no_prob}")
    print(f"  skipped (low vote): {skipped_low_vote}")
    print(f"  skipped (low prob): {skipped_low_prob}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
