#!/usr/bin/env python3
"""Count near-neighbour mound pairs, to scope the point-marking review.

The point-marking pass (``scripts/mark_mound_centres.py``, ruling 20d
step 1) was originally scoped to the 773 promoted phantoms alone. The PI
asked to widen it: "I'd like to see all of my 'corrected' dataset plus
all possible conflations", and proposed a **40 m** cut on the grounds
that mound symbols on these 1:50k sheets run roughly 12-18 px across at
~5 m/px, so two mounds 40 m apart are nearly touching.

This script answers "how many are within X of one another?" for every
pairing that could produce a conflation, across the ground-truth layers
ruling 19 defines:

- **within the promoted phantoms** (layer 4, 773) — duplicate promotions
- **within the corrected student GT** (layer 2, 4,746) — residual student
  double-marks that the 26 merged-centroid replacements did not catch
- **between phantoms and student GT** — the cross-layer conflations the
  marking pass exists to settle
- **within the fixed original digitisation** (layer 1, 4,770) — reported
  for contrast, since layer 2 was derived from it by merging sub-50 m
  double-marks and the residual is the check on that merge

Counts are reported two ways, because they answer different questions:
**pairs** sizes the adjudication workload, while **distinct mounds
involved** sizes the review queue — a cluster of three mutually close
mounds is three pairs but only three mounds to look at.

Usage::

    .venv/bin/python scripts/audit_mound_proximity.py
    .venv/bin/python scripts/audit_mound_proximity.py --thresholds 40 50 \\
        --json-out reports/verification/mound-proximity.json

Ground-truth layer paths follow ruling 19 as recorded in
``reports/verification/c4-triage/wave7-open-items-2026-08-04.json``.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_TARGET_CRS = "EPSG:32635"

# Ruling 19's four ground-truth layers. Layer 3 (historical states 4,744
# and 4,745) is record-only and deliberately absent: ruling 19(a) forbids
# its use in any analysis postdating the correction to 4,746.
_LAYER_FIXED_ORIGINAL = (
    "inputs/vectors/references/student-mounds-55maps.geojson"
)
_LAYER_CORRECTED_STUDENT = (
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
)
_LAYER_PROMOTED = (
    "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv"
)

_DEFAULT_THRESHOLDS = (10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0)


def load_points_geojson(path: Path) -> np.ndarray:
    """Load a GeoJSON mound layer as projected ``(n, 2)`` coordinates.

    Args:
        path: Path to the layer.

    Returns:
        Coordinates in :data:`_TARGET_CRS`, one row per feature.

    Raises:
        ValueError: If the layer carries no CRS, since assuming one would
            silently misplace every point.
    """
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        raise ValueError(f"{path} has no CRS")
    if gdf.crs.to_string() != _TARGET_CRS:
        gdf = gdf.to_crs(_TARGET_CRS)
    centroids = gdf.geometry.centroid
    return np.column_stack([centroids.x.to_numpy(), centroids.y.to_numpy()])


def load_points_csv(path: Path) -> np.ndarray:
    """Load the promoted-phantom CSV as projected ``(n, 2)`` coordinates.

    Args:
        path: Path to ``canonical-review.csv``.

    Returns:
        Coordinates in :data:`_TARGET_CRS`, one row per phantom.
    """
    frame = pd.read_csv(path)
    return np.column_stack([
        frame["x"].to_numpy(dtype=float), frame["y"].to_numpy(dtype=float),
    ])


def within_set_pairs(
    points: np.ndarray, threshold_m: float,
) -> tuple[int, int]:
    """Count close pairs *inside* one set of points.

    Args:
        points: ``(n, 2)`` coordinates.
        threshold_m: Separation below which a pair counts as close.

    Returns:
        A ``(n_pairs, n_mounds_involved)`` tuple. Self-pairs are excluded
        and each unordered pair is counted once.
    """
    if len(points) < 2:
        return 0, 0
    tree = cKDTree(points)
    pairs = tree.query_pairs(r=threshold_m, output_type="ndarray")
    if len(pairs) == 0:
        return 0, 0
    involved = np.unique(pairs)
    return int(len(pairs)), int(len(involved))


def cross_set_pairs(
    left: np.ndarray, right: np.ndarray, threshold_m: float,
) -> tuple[int, int, int]:
    """Count close pairs *between* two sets of points.

    Args:
        left: ``(n, 2)`` coordinates of the first set.
        right: ``(m, 2)`` coordinates of the second set.
        threshold_m: Separation below which a pair counts as close.

    Returns:
        A ``(n_pairs, n_left_involved, n_right_involved)`` tuple.
    """
    if len(left) == 0 or len(right) == 0:
        return 0, 0, 0
    left_tree = cKDTree(left)
    right_tree = cKDTree(right)
    coo = left_tree.sparse_distance_matrix(
        right_tree, max_distance=threshold_m, output_type="coo_matrix",
    )
    # sparse_distance_matrix omits exact-zero distances from its data
    # array, so count structural entries via the index arrays instead.
    n_pairs = int(len(coo.row))
    if n_pairs == 0:
        return 0, 0, 0
    return n_pairs, int(len(np.unique(coo.row))), int(len(np.unique(coo.col)))


def nearest_neighbour_distances(points: np.ndarray) -> np.ndarray:
    """Distance from each point to its closest neighbour in the same set.

    Args:
        points: ``(n, 2)`` coordinates.

    Returns:
        One distance per point; empty if fewer than two points.
    """
    if len(points) < 2:
        return np.empty(0)
    tree = cKDTree(points)
    # k=2 because the closest neighbour of a point is itself at distance 0.
    distances, _ = tree.query(points, k=2)
    return distances[:, 1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list; defaults to ``sys.argv[1:]``.

    Returns:
        The parsed namespace.
    """
    parser = argparse.ArgumentParser(
        description="Count near-neighbour mound pairs across GT layers.",
    )
    parser.add_argument(
        "--thresholds", type=float, nargs="+", default=list(
            _DEFAULT_THRESHOLDS,
        ),
        help="Separation thresholds in metres.",
    )
    parser.add_argument(
        "--json-out", type=Path, default=None,
        help="Optional path to write the full result as JSON.",
    )
    return parser.parse_args(argv)


def main() -> None:
    """Compute and report the proximity audit."""
    args = parse_args()

    promoted = load_points_csv(_PROJECT_ROOT / _LAYER_PROMOTED)
    corrected = load_points_geojson(_PROJECT_ROOT / _LAYER_CORRECTED_STUDENT)
    original = load_points_geojson(_PROJECT_ROOT / _LAYER_FIXED_ORIGINAL)

    print("Ground-truth layers (ruling 19):")
    print(f"  layer 1  fixed original digitisation : {len(original):>5}")
    print(f"  layer 2  corrected student GT        : {len(corrected):>5}")
    print(f"  layer 4  promoted phantoms           : {len(promoted):>5}")
    print()

    results: dict[str, dict] = {
        "layer_counts": {
            "fixed_original": len(original),
            "corrected_student": len(corrected),
            "promoted_phantoms": len(promoted),
        },
        "thresholds": {},
    }

    header = (
        f"{'threshold':>9} | {'phantom-phantom':>21} | "
        f"{'phantom-student':>21} | {'student-student':>21} | "
        f"{'original-original':>21}"
    )
    print(header)
    print(
        f"{'':>9} | {'pairs / mounds':>21} | {'pairs / ph. / st.':>21} | "
        f"{'pairs / mounds':>21} | {'pairs / mounds':>21}",
    )
    print("-" * len(header))

    for threshold in args.thresholds:
        pp_pairs, pp_mounds = within_set_pairs(promoted, threshold)
        ps_pairs, ps_left, ps_right = cross_set_pairs(
            promoted, corrected, threshold,
        )
        ss_pairs, ss_mounds = within_set_pairs(corrected, threshold)
        oo_pairs, oo_mounds = within_set_pairs(original, threshold)

        print(
            f"{threshold:>7.0f} m | {pp_pairs:>9} / {pp_mounds:<9} | "
            f"{ps_pairs:>6} / {ps_left:>4} / {ps_right:<6} | "
            f"{ss_pairs:>9} / {ss_mounds:<9} | "
            f"{oo_pairs:>9} / {oo_mounds:<9}",
        )
        results["thresholds"][f"{threshold:g}"] = {
            "phantom_phantom": {"pairs": pp_pairs, "mounds": pp_mounds},
            "phantom_student": {
                "pairs": ps_pairs,
                "phantoms_involved": ps_left,
                "students_involved": ps_right,
            },
            "student_student": {"pairs": ss_pairs, "mounds": ss_mounds},
            "original_original": {"pairs": oo_pairs, "mounds": oo_mounds},
        }

    # Nearest-neighbour distributions give the shape behind the cuts, so a
    # threshold can be chosen from the data rather than from a round number.
    print("\nNearest-neighbour distance within each layer (metres):")
    for name, points in (
        ("promoted phantoms", promoted),
        ("corrected student GT", corrected),
        ("fixed original", original),
    ):
        nn = nearest_neighbour_distances(points)
        percentiles = np.percentile(nn, [1, 5, 10, 25, 50])
        print(
            f"  {name:<22} p1 {percentiles[0]:6.1f}  p5 {percentiles[1]:6.1f}"
            f"  p10 {percentiles[2]:6.1f}  p25 {percentiles[3]:6.1f}"
            f"  median {percentiles[4]:7.1f}",
        )
        results.setdefault("nearest_neighbour", {})[name] = {
            "p1": float(percentiles[0]), "p5": float(percentiles[1]),
            "p10": float(percentiles[2]), "p25": float(percentiles[3]),
            "median": float(percentiles[4]),
        }

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(results, indent=2) + "\n")
        print(f"\nWrote {args.json_out}")


if __name__ == "__main__":
    main()
