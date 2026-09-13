#!/usr/bin/env python3
"""Histogram the match distances between a pre-fix and a rebuilt union.

A carried verifier probability is only valid for a candidate whose crop
centre did not move, so this reports how many matched candidates moved at
all, and by how much.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_unions import load  # noqa: E402


def main() -> None:
    """Match old to new and report the distribution of displacements."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path, help="Pre-fix union GeoJSON")
    parser.add_argument("new", type=Path, help="Rebuilt union GeoJSON")
    parser.add_argument("--tolerance", type=float, default=20.0)
    args = parser.parse_args()

    old, new = load(args.old), load(args.new)
    cell = args.tolerance
    buckets: dict[tuple[int, int], list[int]] = {}
    for j, feature in enumerate(new):
        key = (int(feature["x"] // cell), int(feature["y"] // cell))
        buckets.setdefault(key, []).append(j)

    taken: set[int] = set()
    dists: list[float] = []
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
                    if dist <= args.tolerance and (best_d is None or dist < best_d):
                        best_j, best_d = j, dist
        if best_j is not None:
            taken.add(best_j)
            dists.append(best_d)

    moved = [d for d in dists if d > 1e-6]
    print(
        json.dumps(
            {
                "file": str(args.new),
                "tolerance_m": args.tolerance,
                "matched": len(dists),
                "exactly_unmoved": len(dists) - len(moved),
                "moved": len(moved),
                "largest_moves_m": [round(d, 4) for d in sorted(moved, reverse=True)][
                    :20
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
