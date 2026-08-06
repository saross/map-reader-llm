#!/usr/bin/env python3
"""Assemble the list of marks needing a second look, with reasons.

Two independent things went stale during the marking pass, and they
overlap only partly, so the union has to be derived rather than guessed:

``rule_consistency``
    The adjudication rule (``planning/point-marking-app-spec.md``
    § "Adjudication rule") was settled after roughly the first 130 items.
    Marks made before it are not wrong so much as *inconsistent* with the
    ones after, which is the property the reference cannot afford to lose.
    Selected by **marking time**, not queue position: the queue was
    re-sorted mid-pass, so position no longer tracks the order decisions
    were made in.

``double_claim``
    Two "same as a neighbour" verdicts that resolved to the SAME partner
    point. One of them must be wrong: a mound cannot be the duplicate of
    two different records. Existing marks predate the partner coordinates
    being stored, so the partner is RECONSTRUCTED from what was recorded —
    the layer and the distance from the marked point — which is exact
    wherever one point in that layer sits at that distance and ambiguous
    otherwise; ambiguous cases are reported rather than silently resolved.

``jitter_precision``
    Jitter-sample marks made before keyboard nudging existed. Unaided
    click placement measured ~2.5-5 m off in about two thirds of cases,
    and for the jitter sample the reviewer's own precision IS the
    measurement, so these are the marks where that error propagates
    directly into a reported number.

``partner_ambiguity``
    Before the partner selector existed, a "same as a neighbour" verdict
    auto-resolved to the neighbour nearest the marked point. That is the
    right default and the wrong answer whenever a nearer neighbour is a
    genuinely separate mound — the attractor case, where a phantom pulled
    off *this* mound sits further away than an unrelated one. Only marks
    with MORE THAN ONE candidate in range could have been affected; the
    rest resolved correctly by construction.

Both reasons are recorded per row, so a row needing only one of them can
be handled accordingly rather than re-adjudicated from scratch.

Usage::

    .venv/bin/python scripts/build_re_review_list.py \\
        --earliest 130 \\
        --output results/deployment-oracle-2026-06-06/canonical-gt/\\
re-review-list.csv

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from scipy.spatial import cKDTree

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mark_mound_centres import (  # noqa: E402
    _FLAG_RADIUS_M,
    _item_id,
    load_phantom_points,
    load_queue,
    load_student_points,
)

_PROJECT_ROOT = _SCRIPT_DIR.parent
_OUTPUT_COLUMNS = [
    "item_id", "current_queue_index", "reasons", "verdict",
    "displacement_m", "n_candidates_in_range", "n_marks_sharing_partner",
    "marked_at",
]


def find_rule_consistency(marks: pd.DataFrame, earliest: int) -> set[str]:
    """Identify the earliest ``earliest`` marks by marking time.

    Args:
        marks: The saved marks.
        earliest: How many of the earliest to select.

    Returns:
        The set of affected ``item_id`` values.
    """
    ordered = marks.sort_values("marked_at").head(earliest)
    return {
        f"{r.source_layer}:{int(r.source_index)}"
        for r in ordered.itertuples()
    }


def find_partner_ambiguity(
    marks: pd.DataFrame, students, phantoms,
) -> dict[str, int]:
    """Identify conflation verdicts that had a competing candidate.

    Args:
        marks: The saved marks.
        students: ``(n, 2)`` student positions.
        phantoms: ``(n, 2)`` phantom positions.

    Returns:
        Mapping of ``item_id`` to the number of candidates in range, for
        rows where that number exceeds one.
    """
    student_tree, phantom_tree = cKDTree(students), cKDTree(phantoms)
    affected: dict[str, int] = {}
    conflations = marks[marks["verdict"] == "same_as_neighbour"]
    for row in conflations.itertuples():
        if pd.isna(row.x_marked):
            continue
        point = [float(row.x_marked), float(row.y_marked)]
        # -1 because the item itself sits in one of the two layers.
        count = (
            len(student_tree.query_ball_point(point, r=_FLAG_RADIUS_M))
            + len(phantom_tree.query_ball_point(point, r=_FLAG_RADIUS_M))
            - 1
        )
        if count > 1:
            affected[f"{row.source_layer}:{int(row.source_index)}"] = count
    return affected


def find_double_claims(
    marks: pd.DataFrame, students, phantoms,
) -> tuple[dict[str, int], list[str]]:
    """Find conflation verdicts that claim the same partner point.

    Args:
        marks: The saved marks.
        students: ``(n, 2)`` student positions.
        phantoms: ``(n, 2)`` phantom positions.

    Returns:
        A ``(affected, notes)`` pair: mapping of ``item_id`` to how many
        marks share its partner, and human-readable notes on any mark whose
        partner could not be reconstructed unambiguously.
    """
    trees = {
        "corrected_student": (cKDTree(students), students),
        "promoted_phantom": (cKDTree(phantoms), phantoms),
    }
    owners: dict[tuple[float, float], list[str]] = {}
    notes: list[str] = []
    for row in marks[marks["verdict"] == "same_as_neighbour"].itertuples():
        key = f"{row.source_layer}:{int(row.source_index)}"
        stored_x = getattr(row, "resolved_partner_x", None)
        if stored_x is not None and not pd.isna(stored_x):
            pos = (round(float(stored_x), 2),
                   round(float(row.resolved_partner_y), 2))
        else:
            layer = str(getattr(row, "resolved_partner_layer", "") or "")
            dist = getattr(row, "resolved_partner_m", None)
            if layer not in trees or dist is None or pd.isna(dist):
                continue
            if pd.isna(row.x_marked):
                continue
            tree, points = trees[layer]
            near = tree.query_ball_point(
                [float(row.x_marked), float(row.y_marked)],
                r=float(dist) + 0.5,
            )
            # Keep only points at (about) the recorded distance.
            at_distance = [
                i for i in near
                if abs(
                    ((points[i][0] - float(row.x_marked)) ** 2
                     + (points[i][1] - float(row.y_marked)) ** 2) ** 0.5
                    - float(dist)
                ) < 0.5
            ]
            if len(at_distance) != 1:
                notes.append(
                    f"{key}: partner not reconstructable "
                    f"({len(at_distance)} candidates at {float(dist):.1f} m)",
                )
                continue
            pos = (round(float(points[at_distance[0]][0]), 2),
                   round(float(points[at_distance[0]][1]), 2))
        owners.setdefault(pos, []).append(key)

    affected = {
        key: len(keys)
        for keys in owners.values() if len(keys) > 1
        for key in keys
    }
    return affected, notes


def find_jitter_precision(marks: pd.DataFrame, queue: pd.DataFrame) -> set:
    """Identify jitter-sample marks, where placement error is the result."""
    jitter = {
        _item_id(queue.iloc[i]) for i in range(len(queue))
        if "jitter_sample" in str(queue.iloc[i]["item_type"])
    }
    marked = {
        f"{r.source_layer}:{int(r.source_index)}" for r in marks.itertuples()
    }
    return jitter & marked


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Build the re-review list for the marking pass.",
    )
    gt = "results/deployment-oracle-2026-06-06/canonical-gt"
    parser.add_argument("--marks", type=Path,
                        default=_PROJECT_ROOT / gt / "marked-centres.csv")
    parser.add_argument("--queue", type=Path,
                        default=_PROJECT_ROOT / gt / "marking-queue.csv")
    parser.add_argument(
        "--earliest", type=int, default=130,
        help="How many of the earliest marks predate the adjudication rule.",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main() -> None:
    """Build the list and write it."""
    args = parse_args()
    marks = pd.read_csv(args.marks)
    queue = load_queue(args.queue)
    students = load_student_points(
        str(_PROJECT_ROOT / "inputs/vectors/references/"
            "student-mounds-55maps-reviewed.geojson"),
    )
    phantoms = load_phantom_points(
        str(args.queue.parent / "canonical-review.csv"),
    )

    rule_ids = find_rule_consistency(marks, args.earliest)
    partner_ids = find_partner_ambiguity(marks, students, phantoms)
    double_ids, double_notes = find_double_claims(marks, students, phantoms)
    jitter_ids = find_jitter_precision(marks, queue)
    position = {_item_id(queue.iloc[i]): i for i in range(len(queue))}

    rows = []
    for row in marks.itertuples():
        key = f"{row.source_layer}:{int(row.source_index)}"
        reasons = []
        if key in rule_ids:
            reasons.append("rule_consistency")
        if key in partner_ids:
            reasons.append("partner_ambiguity")
        if key in double_ids:
            reasons.append("double_claim")
        if key in jitter_ids:
            reasons.append("jitter_precision")
        if not reasons:
            continue
        rows.append({
            "item_id": key,
            "current_queue_index": position.get(key, -1),
            "reasons": "+".join(reasons),
            "verdict": row.verdict,
            "displacement_m": row.displacement_m,
            "n_candidates_in_range": partner_ids.get(key, ""),
            "n_marks_sharing_partner": double_ids.get(key, ""),
            "marked_at": row.marked_at,
        })

    frame = pd.DataFrame(rows, columns=_OUTPUT_COLUMNS)
    frame = frame.sort_values("current_queue_index")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)

    print(f"re-review list: {len(frame)} items")
    for reason, count in frame["reasons"].value_counts().items():
        print(f"  {reason:<38} {count:>4}")
    if double_notes:
        print(f"\n{len(double_notes)} partner(s) not reconstructable "
              "(reported, not guessed):")
        for note in double_notes[:10]:
            print(f"  {note}")
    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
