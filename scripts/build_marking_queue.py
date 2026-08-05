#!/usr/bin/env python3
"""Assemble the point-marking review queue from the ruling-19 GT layers.

The marking pass was originally scoped to the 773 promoted phantoms
(ruling 21c). The PI widened it: every possible conflation should be swept
up in the same pass, at a **40 m** cut — mound symbols run roughly 12-18 px
across at ~5 m/px, so two mounds 40 m apart are nearly touching — and the
student layer's own near-pairs should be reviewed too.

This script builds the resulting queue. Five item types:

``phantom``
    All 773 promoted phantoms (layer 4). The original scope; each needs a
    true centre for Obs 371 regardless of whether it conflates.
``student_conflation``
    Corrected-student points (layer 2) within the threshold of a phantom.
    These are the cross-layer conflations — including four that sit inside
    the 5 m de-duplication tolerance and should never have survived it.
``student_pair``
    Corrected-student points within the threshold of *another* student
    point. Layer 2 is nearly clean here, because the 26 merges already
    removed these; the residual is the check on that merge.
``merge_site``
    Positions present in layer 2 but not layer 1, with exactly two
    superseded layer-1 points nearby: the merged-centroid replacements.
    Reviewing these is what "see all of my corrected dataset" means in
    practice — they are the corrections themselves.
``curator_addition``
    Positions present in layer 2 but not layer 1 with no superseded points
    nearby: the two curator additions.
``jitter_sample``
    A random sample of student mounds with no conflation of any kind,
    drawn to measure typical student placement error. These exist purely
    to yield a displacement distribution, and they are sampled **at
    random** rather than taken from whatever happened to be in view: the
    ~400 student mounds visible alongside a queue item are there because
    they sit near a phantom, i.e. in terrain where the model found mounds
    students missed, so estimating "typical sloppiness" from them would
    bias the figure toward the hard cases.

An item appearing under several headings is emitted **once**, with its
reasons joined in ``item_type``, so the reviewer never sees the same
mound twice. Jitter-sample points are drawn only from mounds not already
queued, so the sample stays clean of conflation cases.

Usage::

    .venv/bin/python scripts/build_marking_queue.py \\
        --output results/deployment-oracle-2026-06-06/canonical-gt/\\
marking-queue.csv

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from audit_mound_proximity import (
    _LAYER_CORRECTED_STUDENT,
    _LAYER_FIXED_ORIGINAL,
    _LAYER_PROMOTED,
    _PROJECT_ROOT,
    load_points_csv,
    load_points_geojson,
)

# The PI's cut. Symbols are ~12-18 px at ~5 m/px, so two mounds 40 m apart
# are nearly touching. Set at 50 m rather than 40 m on the PI's decision
# (2026-08-05): the proximity audit priced the widening at only ~23 further
# items, which is cheap insurance against a missed conflation.
_DEFAULT_THRESHOLD_M = 50.0

# Coordinate-identity tolerance when diffing layer 1 against layer 2. These
# layers share provenance, so an unchanged point matches to floating-point
# noise; 1 cm is far below the ~5 m pixel and far above that noise.
_IDENTITY_TOL_M = 0.01

# A merged centroid sits between the two points it replaced. 60 m is
# comfortably wider than the 50 m band the merges were drawn from, so the
# classification does not depend on a tight radius.
_MERGE_SEARCH_M = 60.0

# Random student mounds added to measure placement jitter. n = 100 puts the
# standard error on the mean near 1 m for a jitter SD of ~10 m, which is
# ample to characterise typical error and to check the 5 m de-duplication
# tolerance empirically rather than by convention.
_DEFAULT_JITTER_SAMPLE = 100

# Fixed so the sample is reproducible: the same corpus and seed must always
# yield the same points, or a re-run would silently re-draw and invalidate
# a partially-completed review.
_JITTER_SEED = 20260805

_QUEUE_COLUMNS = [
    "queue_index",
    "item_type",
    "source_layer",
    "source_index",
    "candidate_id",
    "map_name",
    "buffer_metres",
    "x",
    "y",
    "n_partners_within_threshold",
    "nearest_partner_m",
    "nearest_partner_layer",
    # Student-side attributes, carried so the reviewer can confirm or
    # correct the symbol type without a second lookup. Empty for phantoms.
    "student_map_symbol",
    "student_feature_type",
    "student_reviewed_subtype",
]


def _attribute(frame: "gpd.GeoDataFrame", index: int, column: str) -> str:
    """Read one attribute as a string, treating missing values as empty.

    The student layer's ``_reviewed_subtype`` is null for most features, and
    a bare ``str(nan)`` would write the literal text "nan" into the queue.

    Args:
        frame: The attribute table.
        index: Positional row index.
        column: Column name; a missing column yields an empty string.

    Returns:
        The value as a string, or ``""`` if absent or null.
    """
    if column not in frame.columns:
        return ""
    value = frame.iloc[index][column]
    return "" if pd.isna(value) else str(value)


def classify_layer_diff(
    original: np.ndarray, corrected: np.ndarray,
) -> tuple[list[int], list[int], np.ndarray]:
    """Split layer 2's new positions into merge sites and curator additions.

    Layer 2 is derived from layer 1 by replacing sub-50 m student
    double-marks with merged centroids, plus a couple of additions. A new
    position with exactly two superseded layer-1 points nearby is a merge;
    one with none is an addition.

    Args:
        original: ``(n, 2)`` coordinates of the fixed original layer.
        corrected: ``(m, 2)`` coordinates of the corrected layer.

    Returns:
        A ``(merge_sites, curator_additions, superseded)`` tuple. The first
        two are index lists into ``corrected``; ``superseded`` is the
        ``(k, 2)`` array of layer-1 points absent from layer 2.
    """
    distance_to_original, _ = cKDTree(original).query(corrected, k=1)
    new_positions = np.where(distance_to_original > _IDENTITY_TOL_M)[0]

    distance_to_corrected, _ = cKDTree(corrected).query(original, k=1)
    superseded = original[
        np.where(distance_to_corrected > _IDENTITY_TOL_M)[0]
    ]

    merge_sites: list[int] = []
    curator_additions: list[int] = []
    if len(superseded):
        superseded_tree = cKDTree(superseded)
        for index in new_positions:
            nearby = superseded_tree.query_ball_point(
                corrected[index], r=_MERGE_SEARCH_M,
            )
            (merge_sites if len(nearby) == 2 else curator_additions).append(
                int(index),
            )
    else:
        curator_additions = [int(i) for i in new_positions]
    return merge_sites, curator_additions, superseded


def build_queue(
    threshold_m: float = _DEFAULT_THRESHOLD_M,
    jitter_sample: int = _DEFAULT_JITTER_SAMPLE,
) -> tuple[pd.DataFrame, np.ndarray]:
    """Build the full review queue.

    Args:
        threshold_m: Separation below which two mounds are a possible
            conflation.
        jitter_sample: Number of random unconflicted student mounds to add
            for the placement-jitter estimate. Zero disables the sample.

    Returns:
        A ``(queue, superseded)`` pair: the queue as a DataFrame with
        :data:`_QUEUE_COLUMNS`, and the superseded layer-1 positions, which
        the app overlays as context at merge sites.
    """
    phantom_rows = pd.read_csv(_PROJECT_ROOT / _LAYER_PROMOTED)
    phantoms = load_points_csv(_PROJECT_ROOT / _LAYER_PROMOTED)
    corrected = load_points_geojson(_PROJECT_ROOT / _LAYER_CORRECTED_STUDENT)
    original = load_points_geojson(_PROJECT_ROOT / _LAYER_FIXED_ORIGINAL)

    # Attributes for the student layer, read separately from the geometry
    # so the coordinate loaders stay single-purpose. Row order matches
    # `corrected`, since both come from the same file in file order.
    student_attributes = gpd.read_file(
        _PROJECT_ROOT / _LAYER_CORRECTED_STUDENT,
    )

    phantom_tree = cKDTree(phantoms)
    corrected_tree = cKDTree(corrected)

    # Cross-layer conflations.
    cross = phantom_tree.sparse_distance_matrix(
        corrected_tree, max_distance=threshold_m, output_type="coo_matrix",
    )
    students_in_conflation = set(np.unique(cross.col).tolist())

    # Residual student-student near-pairs inside layer 2.
    student_pairs = corrected_tree.query_pairs(
        r=threshold_m, output_type="ndarray",
    )
    students_in_pairs = (
        set(np.unique(student_pairs).tolist()) if len(student_pairs) else set()
    )

    merge_sites, curator_additions, superseded = classify_layer_diff(
        original, corrected,
    )

    reasons: dict[int, list[str]] = {}
    for index in sorted(students_in_conflation):
        reasons.setdefault(index, []).append("student_conflation")
    for index in sorted(students_in_pairs):
        reasons.setdefault(index, []).append("student_pair")
    for index in merge_sites:
        reasons.setdefault(index, []).append("merge_site")
    for index in curator_additions:
        reasons.setdefault(index, []).append("curator_addition")

    # The jitter sample is drawn from student mounds with no near neighbour
    # of any kind, so a displacement measured on one of them reflects
    # digitisation error alone and not an unresolved conflation.
    if jitter_sample > 0:
        has_phantom_near = set(np.unique(cross.col).tolist())
        eligible = np.array([
            index for index in range(len(corrected))
            if index not in reasons
            and index not in has_phantom_near
        ])
        rng = np.random.default_rng(_JITTER_SEED)
        drawn = rng.choice(
            eligible, size=min(jitter_sample, len(eligible)), replace=False,
        )
        for index in sorted(int(i) for i in drawn):
            reasons.setdefault(index, []).append("jitter_sample")

    records: list[dict] = []

    # Phantoms first, in their existing order, so a partially-completed
    # review of the original 773 keeps its row correspondence.
    phantom_to_student, _ = corrected_tree.query(phantoms, k=1)
    phantom_neighbours = phantom_tree.query_ball_point(
        phantoms, r=threshold_m,
    )
    for index, row in phantom_rows.iterrows():
        n_phantom_partners = len(phantom_neighbours[index]) - 1
        n_student_partners = len(
            corrected_tree.query_ball_point(phantoms[index], r=threshold_m),
        )
        records.append({
            "queue_index": len(records),
            "item_type": "phantom",
            "source_layer": "promoted_phantom",
            "source_index": int(index),
            "candidate_id": row["candidate_id"],
            "map_name": row["map_name"],
            # Cast to float: the source column mixes '50' and '50.0'.
            "buffer_metres": float(row["buffer_metres"]),
            "x": float(phantoms[index][0]),
            "y": float(phantoms[index][1]),
            "n_partners_within_threshold": (
                n_phantom_partners + n_student_partners
            ),
            "nearest_partner_m": float(phantom_to_student[index]),
            "nearest_partner_layer": "corrected_student",
            "student_map_symbol": "",
            "student_feature_type": "",
            "student_reviewed_subtype": "",
        })

    # Then the student points, in layer order.
    student_to_phantom, _ = phantom_tree.query(corrected, k=1)
    for index in sorted(reasons):
        n_partners = len(
            corrected_tree.query_ball_point(corrected[index], r=threshold_m),
        ) - 1 + len(
            phantom_tree.query_ball_point(corrected[index], r=threshold_m),
        )
        records.append({
            "queue_index": len(records),
            "item_type": "+".join(reasons[index]),
            "source_layer": "corrected_student",
            "source_index": int(index),
            "candidate_id": "",
            "map_name": "",
            "buffer_metres": "",
            "x": float(corrected[index][0]),
            "y": float(corrected[index][1]),
            "n_partners_within_threshold": n_partners,
            "nearest_partner_m": float(student_to_phantom[index]),
            "nearest_partner_layer": "promoted_phantom",
            "student_map_symbol": _attribute(
                student_attributes, index, "MapSymbol",
            ),
            "student_feature_type": _attribute(
                student_attributes, index, "FeatureType",
            ),
            "student_reviewed_subtype": _attribute(
                student_attributes, index, "_reviewed_subtype",
            ),
        })

    return pd.DataFrame(records, columns=_QUEUE_COLUMNS), superseded


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list; defaults to ``sys.argv[1:]``.

    Returns:
        The parsed namespace.
    """
    parser = argparse.ArgumentParser(
        description="Build the point-marking review queue.",
    )
    parser.add_argument(
        "--threshold-m", type=float, default=_DEFAULT_THRESHOLD_M,
        help=f"Conflation threshold (default {_DEFAULT_THRESHOLD_M:.0f} m).",
    )
    parser.add_argument(
        "--jitter-sample", type=int, default=_DEFAULT_JITTER_SAMPLE,
        help=(
            "Random unconflicted student mounds added to measure placement "
            f"jitter (default {_DEFAULT_JITTER_SAMPLE}; 0 disables). Drawn "
            f"with a fixed seed ({_JITTER_SEED}) so the queue is stable "
            "across rebuilds."
        ),
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="Destination queue CSV.",
    )
    parser.add_argument(
        "--superseded-output", type=Path, default=None,
        help=(
            "Optional CSV of superseded layer-1 positions, overlaid by the "
            "app as context at merge sites. Defaults to a 'superseded-' "
            "sibling of --output."
        ),
    )
    return parser.parse_args(argv)


def main() -> None:
    """Build the queue and write it to disk."""
    args = parse_args()
    queue, superseded = build_queue(args.threshold_m, args.jitter_sample)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(args.output, index=False)

    superseded_path = args.superseded_output or (
        args.output.parent / f"superseded-{args.output.name}"
    )
    pd.DataFrame(superseded, columns=["x", "y"]).to_csv(
        superseded_path, index=False,
    )

    counts = queue["item_type"].value_counts()
    print(f"Queue: {len(queue)} items at a {args.threshold_m:.0f} m cut")
    for item_type, count in counts.items():
        print(f"  {item_type:<40} {count:>5}")
    print(f"\nWrote {args.output}")
    print(f"Wrote {superseded_path} ({len(superseded)} superseded positions)")


if __name__ == "__main__":
    main()
