#!/usr/bin/env python3
"""
Positional diff of a pre-fix consensus union against its rebuilt counterpart
============================================================================

Description:
    Matches every candidate of an "old" (pre-recovery-fix) consensus union
    against a "new" (rebuilt) one by projected position, so the question
    "is every previously present candidate still present at the same
    coordinates?" is answered by measurement rather than by a count check.

    Consensus unions are written in EPSG:4326 (decimal degrees); matching is
    done in EPSG:32635 (UTM zone 35N, metres) so the tolerance is a true
    metric distance. Matching is greedy nearest-neighbour under the
    tolerance, one-to-one.

Usage::

    python compare_unions.py OLD.geojson NEW.geojson [--tolerance 2.0]

Outputs:
    A JSON report on stdout: matched / absent (in old, not in new) /
    new (in new, not in old), with the coordinates and candidate ids of
    every unmatched feature, plus any vote-count changes among matches.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from pyproj import Transformer

#: Consensus unions are written in WGS84; the study's metric CRS is UTM 35N.
_TO_UTM35N = Transformer.from_crs("EPSG:4326", "EPSG:32635", always_xy=True)


def load(path: Path) -> list[dict[str, Any]]:
    """Load a union's features, annotated with projected coordinates.

    Args:
        path: Path to a ``consensus_t*.geojson`` file.

    Returns:
        One dict per feature carrying ``x``/``y`` in metres (EPSG:32635),
        the original ``lon``/``lat``, the candidate id if the file records
        one, and the vote count.
    """
    with open(path) as handle:
        data = json.load(handle)
    out: list[dict[str, Any]] = []
    for index, feature in enumerate(data.get("features", [])):
        lon, lat = feature["geometry"]["coordinates"][:2]
        x, y = _TO_UTM35N.transform(lon, lat)
        props = feature.get("properties", {})
        out.append(
            {
                "index": index,
                "candidate_id": props.get("candidate_id"),
                "lon": lon,
                "lat": lat,
                "x": x,
                "y": y,
                "vote_count": props.get("vote_count"),
                "source_tile": props.get("source_tile")
                or (props.get("source_tiles") or [None])[0],
            }
        )
    return out


def match(
    old: list[dict[str, Any]],
    new: list[dict[str, Any]],
    tolerance: float,
) -> dict[str, Any]:
    """Greedily match old features to new ones within ``tolerance`` metres.

    Args:
        old: Features of the pre-fix union.
        new: Features of the rebuilt union.
        tolerance: Maximum separation in metres for a pair to count as the
            same candidate.

    Returns:
        A report dict with counts, the unmatched features on both sides,
        and every match whose vote count moved.
    """
    # Bucket the new features on a grid of tolerance-sized cells so the
    # search is local rather than O(n^2) over the whole union.
    cell = max(tolerance, 1.0)
    buckets: dict[tuple[int, int], list[int]] = {}
    for j, feature in enumerate(new):
        key = (int(feature["x"] // cell), int(feature["y"] // cell))
        buckets.setdefault(key, []).append(j)

    taken: set[int] = set()
    matched: list[tuple[int, int, float]] = []
    absent: list[dict[str, Any]] = []

    for feature in old:
        cx, cy = int(feature["x"] // cell), int(feature["y"] // cell)
        best_j, best_d = None, None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in buckets.get((cx + dx, cy + dy), ()):
                    if j in taken:
                        continue
                    dist = math.hypot(
                        feature["x"] - new[j]["x"], feature["y"] - new[j]["y"]
                    )
                    if dist <= tolerance and (best_d is None or dist < best_d):
                        best_j, best_d = j, dist
        if best_j is None:
            absent.append(feature)
        else:
            taken.add(best_j)
            matched.append((feature["index"], best_j, best_d))

    vote_changes = [
        {
            "old_index": oi,
            "new_index": nj,
            "lon": new[nj]["lon"],
            "lat": new[nj]["lat"],
            "source_tile": new[nj]["source_tile"],
            "old_vote_count": old[oi]["vote_count"],
            "new_vote_count": new[nj]["vote_count"],
        }
        for oi, nj, _ in matched
        if old[oi]["vote_count"] != new[nj]["vote_count"]
    ]

    return {
        "old_count": len(old),
        "new_count": len(new),
        "tolerance_m": tolerance,
        "matched": len(matched),
        "absent_from_new": len(absent),
        "new_not_in_old": len(new) - len(taken),
        "max_match_distance_m": round(max((d for _, _, d in matched), default=0.0), 6),
        "absent_features": [
            {
                "index": f["index"],
                "lon": f["lon"],
                "lat": f["lat"],
                "vote_count": f["vote_count"],
                "source_tile": f["source_tile"],
            }
            for f in absent
        ],
        "new_features": [
            {
                "index": f["index"],
                "lon": f["lon"],
                "lat": f["lat"],
                "vote_count": f["vote_count"],
                "source_tile": f["source_tile"],
            }
            for j, f in enumerate(new)
            if j not in taken
        ],
        "vote_count_changes": vote_changes,
    }


def main() -> None:
    """Parse arguments and print the positional diff as JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path, help="Pre-fix union GeoJSON")
    parser.add_argument("new", type=Path, help="Rebuilt union GeoJSON")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=2.0,
        help="Match tolerance in metres (default: 2.0)",
    )
    args = parser.parse_args()
    report = match(load(args.old), load(args.new), args.tolerance)
    report["old_path"] = str(args.old)
    report["new_path"] = str(args.new)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
