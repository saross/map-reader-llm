#!/usr/bin/env python3
"""Derive the ruling-21 instruction set from the marking-campaign output.

Ruling 21 (``reports/verification/phase3-rulings-2026-07-31.md`` § 21)
requires the ground-truth reference to be standardised ONCE, from a fixed
artefact, before any reference-tainted re-analysis runs. The fixed
artefact is the point-marking campaign's output
(``marked-centres.csv``, 1,317 adjudications, campaign closed at commit
``1b9c308aa``). This script turns those adjudications into a concrete,
per-record **instruction set** for building the standardised reference —
it computes what should happen to every affected record, and deliberately
does NOT materialise the reference itself (that step follows PI review of
the instructions, per the marking app's output contract: source layers
are never mutated in place).

Decision rules applied (Session-130 adjudications, recorded in
``planning/paper-writeup-continuity.md`` § NEXT SESSION (131) and
``docs/notes/reflections/session-log.md`` § Session 130):

1. **Counting is position-cluster-based** (app spec § How to count):
   records describing one mound are grouped by their co-located marked
   centres and conflation claims; never by tallying ``c`` verdicts.
2. **One survivor per cluster**, chosen by provenance priority: a
   genuine student record beats a phantom, which beats a marking-pass
   extra. Among students, the claimed partner beats the claimant
   ("student→student tiebreak: the claimant is the duplicate").
3. **The survivor inherits the marked centre**: its own mark where it
   was reviewed in-queue; the claimant's mark where it was claimed from
   outside the queue (the proxy-confirmed grade).
4. **The contradicted merge** ``corrected_student:4172`` (verdict ``m``)
   is removed and both pre-merge originals are restored;
   ``promoted_phantom:389``'s red-partner claim attaches to one of them.
5. **W7-R2**: student features #4744 and #4745 are curator additions of
   MODEL detections, not student digitisation. Both were verdicted
   ``c`` against phantom partners; they leave the student layer as
   duplicates, keeping its provenance purely student.
6. **Removals**: ``x`` (not a mound) records are false positives and
   are removed outright — 41 phantoms and 4 student records.
7. **Confidence grades** for the student layer: ``directly_reviewed``
   (in-queue, own mark), ``proxy_confirmed`` (out-of-queue, claimed as
   a partner from a reviewed mark, position inherited), and
   ``out_of_scope`` (untouched by the campaign, as-digitised).

Outputs (written next to the campaign layers, never overwriting them):

- ``ruling21-instructions.csv`` — one row per affected record: action,
  final position, position source, confidence grade, cluster id, and
  the rule that produced it. Records not listed are implicitly "keep
  as digitised, out_of_scope".
- ``ruling21-summary.json`` — the census: cluster counts, per-action
  tallies, grade populations, symbol reclassifications, and every
  deterministic tiebreak that a reviewer may want to eyeball.

Usage (from the repository root)::

    .venv/bin/python scripts/derive_ruling21_instructions.py
    # paths overridable; see --help

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mark_mound_centres import (  # noqa: E402
    _DEDUP_TOLERANCE_M,
    _DISTINCT_FLOOR_M,
    _item_id,
)

_DEFAULT_GT_DIR = Path("results/deployment-oracle-2026-06-06/canonical-gt")
_DEFAULT_STUDENT_GT = Path(
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
)

# Tolerance for resolving the 64 pre-fix (coordinate-less) claims by
# their recorded partner distance. Half a metre: far tighter than the
# 20.66 m minimum real mound separation, far looser than float noise.
_LEGACY_RESOLVE_TOL_M = 0.5

# W7-R2: the two curator additions that are model detections, not
# student digitisation (session-log § Session 130; continuity § S131).
_MODEL_PROVENANCE_STUDENTS = {4744, 4745}

# The contradicted merge and the claimant whose red-partner claim
# attaches to one of its restored originals.
_CONTRADICTED_MERGE = "corrected_student:4172"
_RED_CLAIMANT = "promoted_phantom:389"


@dataclass
class Node:
    """One record participating in the derivation.

    Attributes:
        node_id: ``"student:<i>"``, ``"phantom:<i>"``,
            ``"superseded:<i>"``, or ``"extra:<extra_id>"``.
        layer: Source layer name.
        index: Index within the layer (``-1`` for extras).
        x: Recorded (as-digitised / as-detected) easting.
        y: Recorded northing.
        mark: ``(x, y)`` of this record's own reviewed mark, if any.
        verdict: This record's own verdict, if it was in the queue.
        claims: Node id of the partner this record ``c``-claims, if any.
        symbol_type: Reviewed symbol type where marked, else the prior.
        candidate_id: Phantom candidate id, for provenance.
    """

    node_id: str
    layer: str
    index: int
    x: float
    y: float
    mark: tuple[float, float] | None = None
    verdict: str | None = None
    claims: str | None = None
    symbol_type: str = ""
    candidate_id: str = ""


@dataclass
class Instruction:
    """One row of the instruction set."""

    record: str
    layer: str
    action: str
    rule: str
    cluster: int | None = None
    final_x: float | None = None
    final_y: float | None = None
    position_source: str = ""
    confidence_grade: str = ""
    symbol_type: str = ""
    note: str = ""


@dataclass
class Derivation:
    """The full derivation result."""

    instructions: list[Instruction] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class UnionFind:
    """Minimal union-find over string node ids."""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def find(self, a: str) -> str:
        self._parent.setdefault(a, a)
        while self._parent[a] != a:
            self._parent[a] = self._parent[self._parent[a]]
            a = self._parent[a]
        return a

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[rb] = ra


def load_inputs(gt_dir: Path, student_gt: Path) -> dict:
    """Load every campaign layer the derivation reads."""
    marks = pd.read_csv(gt_dir / "marked-centres.csv")
    marks["resolved_item_id"] = marks.apply(_item_id, axis=1)
    with open(student_gt, encoding="utf-8") as fh:
        student = json.load(fh)["features"]
    phantoms = pd.read_csv(gt_dir / "canonical-review.csv")
    superseded = pd.read_csv(gt_dir / "superseded-marking-queue.csv")
    extras = pd.read_csv(gt_dir / "extra-review-items.csv")
    return {
        "marks": marks,
        "student": student,
        "phantoms": phantoms,
        "superseded": superseded,
        "extras": extras,
    }


def build_nodes(inputs: dict) -> dict[str, Node]:
    """Create a node for every record any instruction could touch.

    Student and phantom records always get nodes; superseded pre-merge
    points get nodes so the contradicted merge can restore them; the
    extra item gets a node so its addition is part of the same census.
    """
    nodes: dict[str, Node] = {}
    for i, feature in enumerate(inputs["student"]):
        x, y = feature["geometry"]["coordinates"][:2]
        nodes[f"student:{i}"] = Node(f"student:{i}", "corrected_student", i, x, y)
    for i, row in inputs["phantoms"].iterrows():
        nodes[f"phantom:{i}"] = Node(
            f"phantom:{i}", "promoted_phantom", i, row["x"], row["y"],
            candidate_id=str(row["candidate_id"]),
        )
    for i, row in inputs["superseded"].iterrows():
        nodes[f"superseded:{i}"] = Node(
            f"superseded:{i}", "superseded_premerge", i, row["x"], row["y"],
        )
    for _, row in inputs["extras"].iterrows():
        nid = f"extra:{row['extra_id']}"
        nodes[nid] = Node(
            nid, "extra_point", -1, row["x"], row["y"],
            symbol_type=str(row["prior_symbol_type"]),
        )
    return nodes


def _mark_node_id(mark: pd.Series) -> str:
    """Map a mark row to its node id."""
    layer = mark["source_layer"]
    if layer == "corrected_student":
        return f"student:{int(mark['source_index'])}"
    if layer == "promoted_phantom":
        return f"phantom:{int(mark['source_index'])}"
    if layer == "extra_point":
        return mark["resolved_item_id"].replace("extra:", "extra:", 1)
    raise ValueError(f"unknown mark source layer: {layer}")


def _position_index(
    nodes: dict[str, Node], layer: str,
) -> dict[tuple[float, float], str]:
    """Rounded-2dp position → node id, for one layer."""
    return {
        (round(n.x, 2), round(n.y, 2)): n.node_id
        for n in nodes.values()
        if n.layer == layer
    }


def attach_marks_and_claims(
    inputs: dict, nodes: dict[str, Node], derivation: Derivation,
) -> None:
    """Attach each mark to its node and resolve every claim to a target.

    Coordinate-bearing claims resolve through the app's own identity
    convention (partner position rounded to 2 dp). The 64 pre-fix
    claims carry layer + distance only and resolve by matching the
    recorded partner distance from the mark against the named layer,
    requiring a unique match within ``_LEGACY_RESOLVE_TOL_M``.
    """
    layer_index = {
        layer: _position_index(nodes, layer)
        for layer in ("corrected_student", "promoted_phantom", "superseded_premerge")
    }
    layer_points = {
        layer: [
            (n.node_id, n.x, n.y) for n in nodes.values() if n.layer == layer
        ]
        for layer in ("corrected_student", "promoted_phantom", "superseded_premerge")
    }
    for _, mark in inputs["marks"].iterrows():
        nid = _mark_node_id(mark)
        node = nodes[nid]
        node.verdict = mark["verdict"]
        if not pd.isna(mark["x_marked"]):
            node.mark = (float(mark["x_marked"]), float(mark["y_marked"]))
        node.symbol_type = str(mark["symbol_type"])
        if mark["verdict"] != "same_as_neighbour":
            continue
        partner_layer = mark["resolved_partner_layer"]
        if not pd.isna(mark["resolved_partner_x"]):
            key = (
                round(float(mark["resolved_partner_x"]), 2),
                round(float(mark["resolved_partner_y"]), 2),
            )
            target = layer_index[partner_layer].get(key)
            if target is None:
                derivation.warnings.append(
                    f"{nid}: claim position {key} matches nothing in {partner_layer}"
                )
                continue
        else:
            mx, my = node.mark  # a c verdict always has a mark
            wanted = float(mark["resolved_partner_m"])
            hits = [
                cand_id
                for cand_id, cx, cy in layer_points[partner_layer]
                if abs(float(np.hypot(cx - mx, cy - my)) - wanted)
                <= _LEGACY_RESOLVE_TOL_M
            ]
            if len(hits) != 1:
                derivation.warnings.append(
                    f"{nid}: legacy claim at {wanted:.1f} m resolves to "
                    f"{len(hits)} candidates in {partner_layer}"
                )
                continue
            target = hits[0]
        node.claims = target


def build_clusters(
    nodes: dict[str, Node], derivation: Derivation,
) -> dict[str, list[Node]]:
    """Group records into mound clusters per the app spec's counting rule.

    "Distinct mounds = number of position clusters among marks carrying
    a centre" (spec § How to count). Mound identity therefore comes from
    MARK co-location alone (single linkage at the de-duplication
    tolerance); a conflation claim is a record-level statement, and a
    chain of claims does NOT imply transitive mound identity — the
    campaign's attractor cases include chains such as
    ``student:4635 → phantom:699 → student:4634`` whose end members are
    170 m apart and are two different mounds.

    Claims therefore act only as attachments: a claim onto an UNMARKED
    record (an out-of-queue student, or a restored pre-merge original)
    pulls that record into the claimant's cluster as another record of
    the same mound. A claim onto a marked record in ANOTHER cluster is
    superseded by the partner's own mark; it is reported in the summary
    for PI review and has no membership effect.

    Removed records (``x``, and the contradicted merge centroid) do not
    join clusters — a false positive must not glue two real mounds
    together.
    """
    active = [
        n for n in nodes.values()
        if n.verdict not in ("not_a_mound", "merge_incorrect")
    ]
    uf = UnionFind()
    for node in active:
        uf.find(node.node_id)
    marked = [n for n in active if n.mark is not None]
    positions = np.array([n.mark for n in marked])
    for i, node in enumerate(marked):
        dists = np.hypot(
            positions[:, 0] - node.mark[0], positions[:, 1] - node.mark[1],
        )
        for j in np.where(dists <= _DEDUP_TOLERANCE_M)[0]:
            if j > i:
                uf.union(node.node_id, marked[j].node_id)
    by_id = {n.node_id: n for n in active}
    cross_claims: list[dict] = []
    for node in active:
        if node.claims is None or node.claims not in by_id:
            continue
        target = by_id[node.claims]
        if target.mark is None:
            uf.union(node.node_id, target.node_id)
        elif uf.find(node.node_id) != uf.find(target.node_id):
            spread = float(np.hypot(
                node.mark[0] - target.mark[0], node.mark[1] - target.mark[1],
            ))
            if spread <= _DISTINCT_FLOOR_M:
                # A claim corroborated by proximity: marks inside the
                # 15 m distinct-mound floor cannot be two mounds (the
                # measured minimum real separation is 20.66 m), so a
                # boundary-straddling pair like student:861 ↔
                # phantom:329 (5.03 m, mutual claims) is one mound.
                uf.union(node.node_id, target.node_id)
            else:
                cross_claims.append({
                    "claimant": node.node_id,
                    "target": target.node_id,
                    "marks_apart_m": round(spread, 1),
                })
    derivation.summary["cross_cluster_claims"] = cross_claims
    clusters: dict[str, list[Node]] = {}
    for node in active:
        clusters.setdefault(uf.find(node.node_id), []).append(node)
    return clusters


def _is_real_student(node: Node) -> bool:
    """Student-layer provenance, excluding the W7-R2 model detections."""
    if node.layer == "corrected_student":
        return node.index not in _MODEL_PROVENANCE_STUDENTS
    return node.layer == "superseded_premerge"


def choose_survivor(members: list[Node]) -> tuple[Node, bool]:
    """Pick the cluster's surviving record.

    Priority: genuine student provenance (including restored pre-merge
    originals) over phantoms over extras; among equals, a record that
    claims no partner (the claimed side) over a claimant; then lowest
    layer index, which is deterministic but arbitrary — the second
    return value reports whether that final tiebreak decided anything.

    Returns:
        ``(survivor, tiebreak_applied)``.
    """
    def rank(node: Node) -> tuple:
        provenance = (
            0 if _is_real_student(node)
            else 1 if node.layer == "promoted_phantom"
            else 2 if node.layer == "extra_point"
            else 3
        )
        return (provenance, 0 if node.claims is None else 1, node.index)

    ordered = sorted(members, key=rank)
    survivor = ordered[0]
    tiebreak = (
        len(ordered) > 1 and rank(ordered[0])[:2] == rank(ordered[1])[:2]
    )
    return survivor, tiebreak


def survivor_position(
    survivor: Node, members: list[Node], derivation: Derivation,
) -> tuple[float, float, str]:
    """The survivor's final position and its source.

    Own mark where the survivor was reviewed; otherwise the mark of the
    claimant that claimed it (Session-130 rule: the survivor inherits
    the claimant's marked centre, not its own original position). With
    several claimants their marks are co-located within the 5 m
    tolerance (gate 4); the lowest-indexed claimant is used and the
    case is noted.
    """
    if survivor.mark is not None:
        return survivor.mark[0], survivor.mark[1], "own_mark"
    claimants = sorted(
        (m for m in members if m.claims == survivor.node_id and m.mark),
        key=lambda m: (m.layer, m.index),
    )
    if claimants:
        if len(claimants) > 1:
            derivation.warnings.append(
                f"{survivor.node_id}: {len(claimants)} co-located claimant "
                f"marks; using {claimants[0].node_id}"
            )
        cx, cy = claimants[0].mark
        return cx, cy, "claimant_mark"
    return survivor.x, survivor.y, "as_recorded"


def derive(inputs: dict) -> Derivation:
    """Run the full derivation and return instructions plus census."""
    derivation = Derivation()
    nodes = build_nodes(inputs)

    # The contradicted merge: restore both pre-merge originals before
    # clustering, so promoted_phantom:389's claim lands on a live node.
    marks = inputs["marks"]
    merge_mark = marks[marks["resolved_item_id"] == _CONTRADICTED_MERGE].iloc[0]
    centroid = np.array([float(merge_mark["x"]), float(merge_mark["y"])])
    superseded_xy = inputs["superseded"][["x", "y"]].to_numpy()
    nearest_two = np.argsort(
        np.hypot(*(superseded_xy - centroid).T)
    )[:2]
    restored_ids = {f"superseded:{int(i)}" for i in nearest_two}

    attach_marks_and_claims(inputs, nodes, derivation)

    red_target = nodes[
        _mark_node_id(
            marks[marks["resolved_item_id"] == _RED_CLAIMANT].iloc[0]
        )
    ].claims
    if red_target not in restored_ids:
        derivation.warnings.append(
            f"{_RED_CLAIMANT} claims {red_target}, which is NOT one of the "
            f"restored pre-merge originals {sorted(restored_ids)}"
        )

    # Superseded points that are NOT restored play no part: their merges
    # were confirmed by the 24 merge-right verdicts.
    for node_id in [
        n.node_id for n in nodes.values()
        if n.layer == "superseded_premerge" and n.node_id not in restored_ids
    ]:
        del nodes[node_id]

    clusters = build_clusters(nodes, derivation)

    # --- Removals (outside clusters) -----------------------------------
    for node in nodes.values():
        if node.verdict == "not_a_mound":
            derivation.instructions.append(Instruction(
                record=node.node_id, layer=node.layer, action="remove_fp",
                rule="verdict x: a clear symbol falsely tagged as a mound",
                symbol_type=node.symbol_type,
            ))
    derivation.instructions.append(Instruction(
        record="student:4172", layer="corrected_student",
        action="remove_contradicted_merge",
        rule="verdict m: merged centroid never a single mound; "
             "both pre-merge originals restored",
    ))

    # --- Clusters: survivors, duplicates, grades -----------------------
    queued_students = {
        int(m["source_index"])
        for _, m in marks.iterrows()
        if m["source_layer"] == "corrected_student"
    }
    cluster_census = {"total": 0, "multi_record": 0, "tiebreaks": []}
    mark_spread_violations = []
    for cluster_no, (_, members) in enumerate(sorted(clusters.items())):
        cluster_census["total"] += 1
        marked = [m for m in members if m.mark is not None]
        if len(marked) > 1:
            pts = np.array([m.mark for m in marked])
            spread = max(
                float(np.hypot(*(a - b)))
                for i, a in enumerate(pts) for b in pts[i + 1:]
            )
            # Single-linkage chains may legitimately exceed the pairwise
            # tolerance slightly; twice the tolerance means bad gluing.
            if spread > 2 * _DEDUP_TOLERANCE_M:
                mark_spread_violations.append(
                    f"cluster {cluster_no}: marks spread {spread:.1f} m"
                )
        if len(members) == 1:
            node = members[0]
            if node.node_id in restored_ids or node.verdict is not None:
                # Reviewed singletons and unclaimed restored originals
                # get explicit keep instructions below.
                pass
            else:
                continue  # out-of-scope student, untouched: implicit keep
        cluster_census["multi_record"] += len(members) > 1
        survivor, tiebreak = choose_survivor(members)
        if tiebreak:
            cluster_census["tiebreaks"].append(
                {"cluster": cluster_no,
                 "members": [m.node_id for m in members],
                 "survivor": survivor.node_id}
            )
        x, y, source = survivor_position(survivor, members, derivation)
        if survivor.layer == "corrected_student":
            grade = (
                "directly_reviewed"
                if survivor.index in queued_students
                else "proxy_confirmed"
            )
        elif survivor.node_id in restored_ids:
            grade = (
                "proxy_confirmed" if source == "claimant_mark"
                else "directly_reviewed"
            )
        else:
            grade = "directly_reviewed"
        action = {
            "corrected_student": "keep_student",
            "superseded_premerge": "restore_premerge",
            "promoted_phantom": "keep_phantom_extension",
            "extra_point": "add_marking_pass_extra",
        }[survivor.layer]
        derivation.instructions.append(Instruction(
            record=survivor.node_id, layer=survivor.layer, action=action,
            rule="cluster survivor" + (" (index tiebreak)" if tiebreak else ""),
            cluster=cluster_no, final_x=round(x, 3), final_y=round(y, 3),
            position_source=source, confidence_grade=grade,
            symbol_type=survivor.symbol_type,
            note=(f"candidate {survivor.candidate_id}"
                  if survivor.candidate_id else ""),
        ))
        for member in members:
            if member.node_id == survivor.node_id:
                continue
            if member.layer == "corrected_student":
                rule = (
                    "W7-R2: curator addition of a model detection leaves "
                    "the student layer"
                    if member.index in _MODEL_PROVENANCE_STUDENTS
                    else "student→student: the claimant is the duplicate"
                    if survivor.layer == "corrected_student"
                    else "duplicate record of the cluster's mound"
                )
            else:
                rule = "prefer the student record over the phantom" if (
                    _is_real_student(survivor)
                ) else "duplicate record of the cluster's mound"
            derivation.instructions.append(Instruction(
                record=member.node_id, layer=member.layer,
                action="remove_duplicate", rule=rule, cluster=cluster_no,
                note=f"survivor {survivor.node_id}",
            ))

    derivation.warnings.extend(mark_spread_violations)

    # --- Census --------------------------------------------------------
    actions = pd.Series([i.action for i in derivation.instructions])
    grades = pd.Series([
        i.confidence_grade for i in derivation.instructions
        if i.confidence_grade
    ])
    kept_students = actions[actions == "keep_student"].size
    removed_students = sum(
        1 for i in derivation.instructions
        if i.layer == "corrected_student"
        and i.action in ("remove_fp", "remove_duplicate",
                         "remove_contradicted_merge")
    )
    n_student = len(inputs["student"])
    derivation.summary |= {
        "inputs": {
            "marks": int(len(marks)),
            "student_features": n_student,
            "phantom_records": int(len(inputs["phantoms"])),
            "superseded_points": int(len(inputs["superseded"])),
        },
        "clusters": {
            "total": cluster_census["total"],
            "multi_record": int(cluster_census["multi_record"]),
            "index_tiebreaks": cluster_census["tiebreaks"],
        },
        "actions": {k: int(v) for k, v in actions.value_counts().items()},
        "confidence_grades_assigned": {
            k: int(v) for k, v in grades.value_counts().items()
        },
        "final_student_layer": {
            "before": n_student,
            "removed": removed_students,
            "restored_premerge": int(actions[actions == "restore_premerge"].size),
            "after": n_student - removed_students
            + int(actions[actions == "restore_premerge"].size),
            "out_of_scope_implicit": n_student - removed_students - kept_students,
        },
        "final_extension_layer": {
            "phantom_survivors": int(
                actions[actions == "keep_phantom_extension"].size
            ),
            "marking_pass_extras": int(
                actions[actions == "add_marking_pass_extra"].size
            ),
        },
        "implicit_default": (
            "any student feature not named in the instructions is kept "
            "as digitised with confidence grade out_of_scope"
        ),
    }
    return derivation


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Derive the ruling-21 instruction set (no layer mutation).",
    )
    parser.add_argument(
        "--canonical-gt-dir", type=Path, default=_DEFAULT_GT_DIR,
        help="Directory holding the campaign layers.",
    )
    parser.add_argument(
        "--student-gt", type=Path, default=_DEFAULT_STUDENT_GT,
        help="Reviewed student-mound GeoJSON.",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=None,
        help="Output directory (default: the canonical-gt dir).",
    )
    return parser.parse_args(argv)


def main() -> int:
    """Run the derivation and write the instruction set."""
    args = parse_args()
    out_dir = args.out_dir or args.canonical_gt_dir
    inputs = load_inputs(args.canonical_gt_dir, args.student_gt)
    derivation = derive(inputs)

    instructions_csv = out_dir / "ruling21-instructions.csv"
    columns = [
        "record", "layer", "action", "rule", "cluster", "final_x", "final_y",
        "position_source", "confidence_grade", "symbol_type", "note",
    ]
    with open(instructions_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for instruction in derivation.instructions:
            writer.writerow({c: getattr(instruction, c) for c in columns})

    summary_json = out_dir / "ruling21-summary.json"
    with open(summary_json, "w", encoding="utf-8") as fh:
        json.dump(derivation.summary, fh, indent=2)
        fh.write("\n")

    print(f"wrote {instructions_csv} ({len(derivation.instructions)} instructions)")
    print(f"wrote {summary_json}")
    print(json.dumps(derivation.summary, indent=2))
    if derivation.warnings:
        print(f"\n{len(derivation.warnings)} warnings:")
        for warning in derivation.warnings:
            print(f"  ! {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
