#!/usr/bin/env python3
"""Closing-gate battery for the 2026-08 point-marking campaign.

Persistent form of the eight ad-hoc gates that closed the marking
campaign in Session 130 (all green at commit ``1b9c308aa``). The gate
list survives in that commit's message and in
``docs/notes/reflections/session-log.md`` § Session 130; this script
reconstructs them as a repeatable battery so that ruling-21 application
(and anything else that touches the campaign's layers) can re-verify the
closed state at any time.

The eight gates:

1. **Completeness** — every queue item has exactly one decisive mark
   (``d``/``c``/``x``/``m``; never ``uncertain``/``skipped``), resolved
   through the app's own identity rule, and the verdict tally matches
   the campaign-close fingerprint (762 c / 509 d / 45 x / 1 m).
2. **Final four landed** — the last four adjudications of the campaign,
   anchored on stable item ids: ``promoted_phantom:688`` (c → student
   #2667), ``promoted_phantom:255`` (c → phantom at 115.0 m) and
   ``promoted_phantom:762`` (c → phantom at 140.7 m — both storable only
   via the dual-anchor radius fix), ``promoted_phantom:742`` (x, a
   numeral-spawned detection confirmed FP by the PI).
3. **Red partners legal** — the only claim of a ``superseded_premerge``
   (red) point is ``promoted_phantom:389``, whose true partner is a
   pre-merge original of the contradicted merge ``corrected_student:4172``.
4. **No conflicting double-claims** — where several marks claim the same
   partner point, their marked centres are co-located (legitimate
   multi-records of one mound), within the app's de-duplication
   tolerance.
5. **No claims of removed records** — no conflation claim resolves to a
   queue item verdicted ``x`` (not a mound) or ``m`` (merge incorrect).
6. **No partner-less conflations** — every ``c`` mark names a partner
   layer and distance.
7. **Merge sites** — the 26 merged-centroid items resolve as 24 ``d`` /
   1 ``m`` (``corrected_student:4172``) / 1 legitimate ``c`` to a
   phantom partner (``corrected_student:2397``).
8. **No unreviewed cyan near a non-claimant mark** — no out-of-queue
   student (cyan) point sits within the 15 m distinct-mound floor of a
   ``c`` mark other than that mark's own claimed partner. ``d`` marks
   near a cyan point are the reviewer's explicit "distinct" adjudication
   and are reported informationally, not gated; stale clicks on ``x``
   records assert nothing and are excluded.

Reconstruction provenance: thresholds and identity rules are imported
from the marking app itself (``mark_mound_centres``) rather than
re-derived — Session 130's first ad-hoc battery re-derived them and
produced two false alarms. Partner-claim identity follows the app's
convention: a claim is keyed on the partner position rounded to 2 dp;
the 64 early marks (2026-08-05/06, before the app recorded partner
coordinates) carry layer + distance only and are excluded from
position-keyed gates, exactly as the app's own double-claim warning
excludes them.

Usage (from the repository root)::

    .venv/bin/python scripts/marking_campaign_gates.py
    # or with explicit paths:
    .venv/bin/python scripts/marking_campaign_gates.py \
        --canonical-gt-dir results/deployment-oracle-2026-06-06/canonical-gt \
        --student-gt inputs/vectors/references/student-mounds-55maps-reviewed.geojson

Exit status 0 when all eight gates pass, 1 otherwise.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# Reuse the app's own constants and identity rule — never re-derive them
# (Session 130 lesson: re-derivation produced false alarms).
from mark_mound_centres import (  # noqa: E402
    _DEDUP_TOLERANCE_M,
    _DISTINCT_FLOOR_M,
    _FLAG_RADIUS_M,
    _item_id,
)

# Campaign-close fingerprint (commit 1b9c308aa): verdict tallies at the
# moment all eight gates first went green.
_EXPECTED_TALLY = {
    "same_as_neighbour": 762,
    "distinct": 509,
    "not_a_mound": 45,
    "merge_incorrect": 1,
}

# Default layer paths — the same set scripts/launch_point_marking.sh
# passes to the app.
_DEFAULT_GT_DIR = Path("results/deployment-oracle-2026-06-06/canonical-gt")
_DEFAULT_STUDENT_GT = Path(
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
)


@dataclass
class GateResult:
    """Outcome of one gate.

    Attributes:
        name: Short gate title, numbered as in the closing commit.
        passed: Whether the gate holds on the current state.
        detail: One-line summary of what was measured.
        violations: Zero or more human-readable violation descriptions.
    """

    name: str
    passed: bool
    detail: str
    violations: list[str]


def item_id(row: pd.Series) -> str:
    """The app's identity rule, applied to a queue row or saved mark."""
    return _item_id(row)


def _claim_key(row: pd.Series) -> tuple[str, float, float] | None:
    """Position-based claim identity, as the app's double-claim warning uses.

    Args:
        row: A saved mark.

    Returns:
        ``(partner_layer, x, y)`` with coordinates rounded to 2 dp, or
        ``None`` when the mark is not a coordinate-bearing conflation
        claim (non-``c`` verdicts, and the 64 pre-fix marks that carry
        layer + distance only).
    """
    if row["verdict"] != "same_as_neighbour":
        return None
    px, py = row.get("resolved_partner_x"), row.get("resolved_partner_y")
    if px is None or py is None or pd.isna(px) or pd.isna(py):
        return None
    return (str(row["resolved_partner_layer"]), round(float(px), 2), round(float(py), 2))


def load_marks(marks_csv: Path) -> pd.DataFrame:
    """Load marked-centres.csv with item ids resolved via the app rule."""
    marks = pd.read_csv(marks_csv)
    marks["resolved_item_id"] = marks.apply(_item_id, axis=1)
    return marks


def load_queue(queue_csv: Path) -> pd.DataFrame:
    """Load marking-queue.csv with item ids resolved via the app rule."""
    queue = pd.read_csv(queue_csv)
    queue["resolved_item_id"] = queue.apply(_item_id, axis=1)
    return queue


def load_student_points(student_gt: Path) -> np.ndarray:
    """Student GT positions as an ``(n, 2)`` array, feature-indexed.

    ``json`` rather than geopandas: the gate only needs coordinates, and
    the feature index must match the queue's ``source_index`` exactly,
    which positional iteration guarantees.
    """
    with open(student_gt, encoding="utf-8") as fh:
        collection = json.load(fh)
    return np.array(
        [f["geometry"]["coordinates"][:2] for f in collection["features"]]
    )


def gate_1_completeness(queue: pd.DataFrame, marks: pd.DataFrame) -> GateResult:
    """Every queue item decisively marked; tally at the close fingerprint."""
    violations: list[str] = []
    qids = set(queue["resolved_item_id"])
    mids = set(marks["resolved_item_id"])
    for missing in sorted(qids - mids):
        violations.append(f"queue item never marked: {missing}")
    for orphan in sorted(mids - qids):
        violations.append(f"mark with no queue item: {orphan}")
    dup = marks["resolved_item_id"].value_counts()
    for iid in dup[dup > 1].index:
        violations.append(f"multiple marks for one item: {iid}")
    indecisive = marks[
        marks["verdict"].isin(("uncertain", "skipped"))
        | marks["uncertain"].astype(bool)
        | marks["skipped"].astype(bool)
    ]
    for iid in indecisive["resolved_item_id"]:
        violations.append(f"indecisive verdict: {iid}")
    tally = marks["verdict"].value_counts().to_dict()
    if tally != _EXPECTED_TALLY:
        violations.append(
            f"verdict tally {tally} != campaign-close fingerprint {_EXPECTED_TALLY}"
        )
    return GateResult(
        "1 completeness",
        not violations,
        f"{len(mids & qids)}/{len(qids)} items marked; tally {tally}",
        violations,
    )


def gate_2_final_four(marks: pd.DataFrame) -> GateResult:
    """The campaign's last four adjudications, anchored on item ids."""
    violations: list[str] = []
    by_id = marks.set_index("resolved_item_id")

    def check(iid: str, verdict: str, partner_layer: str | None,
              partner_m: float | None) -> None:
        if iid not in by_id.index:
            violations.append(f"{iid}: no mark found")
            return
        row = by_id.loc[iid]
        if row["verdict"] != verdict:
            violations.append(f"{iid}: verdict {row['verdict']!r} != {verdict!r}")
        if partner_layer and row["resolved_partner_layer"] != partner_layer:
            violations.append(
                f"{iid}: partner layer {row['resolved_partner_layer']!r} "
                f"!= {partner_layer!r}"
            )
        if partner_m is not None and abs(row["resolved_partner_m"] - partner_m) > 0.1:
            violations.append(
                f"{iid}: partner distance {row['resolved_partner_m']:.1f} "
                f"!= {partner_m:.1f} m"
            )

    check("promoted_phantom:688", "same_as_neighbour", "corrected_student", None)
    # Both extreme claims exceed the 110 m flag radius and were storable
    # only via the dual-anchor partner-radius fix.
    check("promoted_phantom:255", "same_as_neighbour", "promoted_phantom", 115.0)
    check("promoted_phantom:762", "same_as_neighbour", "promoted_phantom", 140.7)
    check("promoted_phantom:742", "not_a_mound", None, None)
    extremes = marks[
        (marks["verdict"] == "same_as_neighbour")
        & (marks["resolved_partner_m"] > _FLAG_RADIUS_M)
    ]["resolved_item_id"].tolist()
    if sorted(extremes) != ["promoted_phantom:255", "promoted_phantom:762"]:
        violations.append(
            f"claims beyond the {_FLAG_RADIUS_M:.0f} m flag radius are {extremes}, "
            "expected exactly promoted_phantom:255 and :762"
        )
    return GateResult(
        "2 final four landed",
        not violations,
        "688 c→student, 255 c→phantom@115.0, 762 c→phantom@140.7, 742 x",
        violations,
    )


def gate_3_red_partners(marks: pd.DataFrame) -> GateResult:
    """Only promoted_phantom:389 may claim a superseded (red) point."""
    red = marks[marks["resolved_partner_layer"] == "superseded_premerge"]
    claimants = sorted(red["resolved_item_id"])
    violations = (
        []
        if claimants == ["promoted_phantom:389"]
        else [f"red-partner claimants {claimants} != ['promoted_phantom:389']"]
    )
    return GateResult(
        "3 red partners legal",
        not violations,
        f"superseded_premerge claims: {claimants}",
        violations,
    )


def gate_4_double_claims(marks: pd.DataFrame) -> GateResult:
    """Shared partner points only where the claimant marks are co-located."""
    groups: dict[tuple[str, float, float], list[pd.Series]] = {}
    for _, row in marks.iterrows():
        key = _claim_key(row)
        if key is not None:
            groups.setdefault(key, []).append(row)
    shared = {k: v for k, v in groups.items() if len(v) > 1}
    violations: list[str] = []
    for key, rows in shared.items():
        pts = [(float(r["x_marked"]), float(r["y_marked"])) for r in rows]
        worst = max(
            float(np.hypot(a[0] - b[0], a[1] - b[1]))
            for i, a in enumerate(pts)
            for b in pts[i + 1 :]
        )
        if worst > _DEDUP_TOLERANCE_M:
            ids = [r["resolved_item_id"] for r in rows]
            violations.append(
                f"partner {key} claimed by {ids} with marks {worst:.1f} m apart "
                f"(> {_DEDUP_TOLERANCE_M:.0f} m co-location tolerance)"
            )
    return GateResult(
        "4 no conflicting double-claims",
        not violations,
        f"{len(shared)} shared-partner groups, all marks co-located within "
        f"{_DEDUP_TOLERANCE_M:.0f} m",
        violations,
    )


def gate_5_no_claims_of_removed(
    queue: pd.DataFrame, marks: pd.DataFrame,
) -> GateResult:
    """No conflation claim resolves to an x-ed or m-ed queue item."""
    removed_pos = {}
    verdict_by_id = dict(zip(marks["resolved_item_id"], marks["verdict"], strict=True))
    for _, q in queue.iterrows():
        verdict = verdict_by_id.get(q["resolved_item_id"])
        if verdict in ("not_a_mound", "merge_incorrect"):
            key = (str(q["source_layer"]), round(float(q["x"]), 2), round(float(q["y"]), 2))
            removed_pos[key] = (q["resolved_item_id"], verdict)
    violations: list[str] = []
    for _, row in marks.iterrows():
        key = _claim_key(row)
        if key is not None and key in removed_pos:
            target, verdict = removed_pos[key]
            violations.append(
                f"{row['resolved_item_id']} claims {target} (verdict {verdict})"
            )
    return GateResult(
        "5 no claims of removed records",
        not violations,
        f"checked {len(removed_pos)} removed-record positions",
        violations,
    )


def gate_6_partnered_conflations(marks: pd.DataFrame) -> GateResult:
    """Every c mark names a partner layer and distance."""
    conflations = marks[marks["verdict"] == "same_as_neighbour"]
    missing = conflations[
        conflations["resolved_partner_layer"].isna()
        | conflations["resolved_partner_m"].isna()
    ]
    violations = [
        f"partner-less conflation: {iid}" for iid in missing["resolved_item_id"]
    ]
    legacy = int(conflations["resolved_partner_x"].isna().sum())
    return GateResult(
        "6 no partner-less conflations",
        not violations,
        f"{len(conflations)} c marks all carry partner layer + distance "
        f"({legacy} pre-fix marks carry no partner coordinates)",
        violations,
    )


def gate_7_merge_sites(marks: pd.DataFrame) -> GateResult:
    """26 merge sites resolve as 24 d / 1 m (4172) / 1 c-to-phantom (2397)."""
    sites = marks[marks["item_type"].str.contains("merge_site")]
    violations: list[str] = []
    tally = sites["verdict"].value_counts().to_dict()
    if len(sites) != 26 or tally != {
        "distinct": 24, "merge_incorrect": 1, "same_as_neighbour": 1,
    }:
        violations.append(f"merge-site tally {tally} over {len(sites)} items")
    m_items = sites[sites["verdict"] == "merge_incorrect"]["resolved_item_id"].tolist()
    if m_items != ["corrected_student:4172"]:
        violations.append(f"merge_incorrect items {m_items}")
    c_rows = sites[sites["verdict"] == "same_as_neighbour"]
    for _, row in c_rows.iterrows():
        if row["resolved_partner_layer"] != "promoted_phantom":
            violations.append(
                f"merge-site c claim {row['resolved_item_id']} partners "
                f"{row['resolved_partner_layer']!r}, not a phantom"
            )
    return GateResult(
        "7 merge sites",
        not violations,
        f"{len(sites)} sites: {tally}",
        violations,
    )


def gate_8_unreviewed_cyan(
    queue: pd.DataFrame, marks: pd.DataFrame, student_points: np.ndarray,
) -> GateResult:
    """No out-of-queue cyan point within 15 m of a c mark bar its partner.

    Scope is conflation (``c``) marks only: a ``d`` mark near a cyan
    point is the reviewer's explicit distinct-mound adjudication of a
    borderline case (ruling 20c), and a click left on an ``x`` record
    asserts nothing. Both are reported by the informational summary.
    """
    queued = {
        int(q["source_index"])
        for _, q in queue.iterrows()
        if q["source_layer"] == "corrected_student"
    }
    unreviewed = np.array(sorted(set(range(len(student_points))) - queued))
    pos_to_idx = {
        (round(float(x), 2), round(float(y), 2)): i
        for i, (x, y) in enumerate(student_points)
    }
    violations: list[str] = []
    conflations = marks[
        (marks["verdict"] == "same_as_neighbour") & marks["x_marked"].notna()
    ]
    for _, row in conflations.iterrows():
        mx, my = float(row["x_marked"]), float(row["y_marked"])
        dists = np.hypot(
            student_points[unreviewed, 0] - mx, student_points[unreviewed, 1] - my,
        )
        near = unreviewed[dists <= _DISTINCT_FLOOR_M]
        if len(near) == 0:
            continue
        claimed: set[int] = set()
        key = _claim_key(row)
        if key is not None and key[0] == "corrected_student":
            idx = pos_to_idx.get((key[1], key[2]))
            if idx is not None:
                claimed.add(idx)
        elif row["resolved_partner_layer"] == "corrected_student":
            # Pre-fix claim: resolve by the recorded partner distance.
            all_d = np.hypot(
                student_points[:, 0] - mx, student_points[:, 1] - my,
            )
            claimed.update(
                int(i)
                for i in np.where(
                    np.abs(all_d - float(row["resolved_partner_m"])) <= 0.5
                )[0]
            )
        for idx in near:
            if int(idx) not in claimed:
                d = float(
                    np.hypot(
                        student_points[idx, 0] - mx, student_points[idx, 1] - my,
                    )
                )
                violations.append(
                    f"{row['resolved_item_id']}: unreviewed student #{idx} at "
                    f"{d:.1f} m is not the claimed partner"
                )
    return GateResult(
        "8 no unreviewed cyan near a non-claimant mark",
        not violations,
        f"{len(conflations)} c marks checked against "
        f"{len(unreviewed)} out-of-queue student points at "
        f"{_DISTINCT_FLOOR_M:.0f} m",
        violations,
    )


def informational_summary(
    queue: pd.DataFrame, marks: pd.DataFrame, student_points: np.ndarray,
) -> list[str]:
    """Non-gated facts the ruling-21 derivation consumes.

    Reported so a battery run doubles as a state census: the confidence-
    grade populations, the coordinate-less legacy claims, and the
    reviewer-adjudicated borderline cases near unreviewed cyan points.
    """
    lines: list[str] = []
    queued = {
        int(q["source_index"])
        for _, q in queue.iterrows()
        if q["source_layer"] == "corrected_student"
    }
    pos_to_idx = {
        (round(float(x), 2), round(float(y), 2)): i
        for i, (x, y) in enumerate(student_points)
    }
    # Proxy-confirmed cyan points: out-of-queue student points claimed as
    # partners by coordinate-bearing marks (the S130 convention).
    claims: list[tuple[str, int, float]] = []
    for _, row in marks.iterrows():
        key = _claim_key(row)
        if key is None or key[0] != "corrected_student":
            continue
        idx = pos_to_idx.get((key[1], key[2]))
        if idx is None or idx in queued:
            continue
        d = float(
            np.hypot(
                float(row["x_marked"]) - key[1], float(row["y_marked"]) - key[2],
            )
        )
        claims.append((row["resolved_item_id"], idx, d))
    unique = {idx for _, idx, _ in claims}
    within = sum(1 for _, _, d in claims if d <= _DISTINCT_FLOOR_M)
    lines.append(
        f"proxy-confirmed cyan points: {len(unique)} unique out-of-queue student "
        f"points under {len(claims)} coordinate claims "
        f"({within} claims within {_DISTINCT_FLOOR_M:.0f} m of the mark)"
    )
    legacy = marks[
        (marks["verdict"] == "same_as_neighbour")
        & marks["resolved_partner_x"].isna()
    ]
    legacy_by_layer = {
        str(k): int(v)
        for k, v in legacy["resolved_partner_layer"].value_counts().items()
    }
    lines.append(
        f"coordinate-less legacy claims: {len(legacy)} ({legacy_by_layer})"
    )
    # Distinct-verdict marks with an unreviewed cyan point inside the
    # 15 m floor: the reviewer saw the pair and judged them distinct.
    unreviewed = np.array(sorted(set(range(len(student_points))) - queued))
    distinct = marks[(marks["verdict"] == "distinct") & marks["x_marked"].notna()]
    for _, row in distinct.iterrows():
        dists = np.hypot(
            student_points[unreviewed, 0] - float(row["x_marked"]),
            student_points[unreviewed, 1] - float(row["y_marked"]),
        )
        for idx, d in zip(unreviewed[dists <= _DISTINCT_FLOOR_M],
                          dists[dists <= _DISTINCT_FLOOR_M], strict=True):
            lines.append(
                f"adjudicated borderline: {row['resolved_item_id']} marked "
                f"distinct with unreviewed student #{idx} at {d:.1f} m"
            )
    return lines


def run_gates(
    queue: pd.DataFrame, marks: pd.DataFrame, student_points: np.ndarray,
) -> list[GateResult]:
    """Run all eight gates and return their results in battery order."""
    return [
        gate_1_completeness(queue, marks),
        gate_2_final_four(marks),
        gate_3_red_partners(marks),
        gate_4_double_claims(marks),
        gate_5_no_claims_of_removed(queue, marks),
        gate_6_partnered_conflations(marks),
        gate_7_merge_sites(marks),
        gate_8_unreviewed_cyan(queue, marks, student_points),
    ]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Re-run the eight closing gates of the point-marking campaign.",
    )
    parser.add_argument(
        "--canonical-gt-dir", type=Path, default=_DEFAULT_GT_DIR,
        help="Directory holding marking-queue.csv and marked-centres.csv.",
    )
    parser.add_argument(
        "--student-gt", type=Path, default=_DEFAULT_STUDENT_GT,
        help="Reviewed student-mound GeoJSON (the cyan layer).",
    )
    return parser.parse_args(argv)


def main() -> int:
    """Run the battery and report; 0 when all gates pass."""
    args = parse_args()
    queue = load_queue(args.canonical_gt_dir / "marking-queue.csv")
    marks = load_marks(args.canonical_gt_dir / "marked-centres.csv")
    student_points = load_student_points(args.student_gt)
    results = run_gates(queue, marks, student_points)
    for result in results:
        flag = "PASS" if result.passed else "FAIL"
        print(f"[{flag}] gate {result.name} — {result.detail}")
        for violation in result.violations:
            print(f"       ! {violation}")
    print("\nInformational summary (not gated):")
    for line in informational_summary(queue, marks, student_points):
        print(f"  - {line}")
    failed = [r for r in results if not r.passed]
    print(
        f"\n{8 - len(failed)}/8 gates green"
        + (f" — FAILED: {[r.name for r in failed]}" if failed else "")
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
