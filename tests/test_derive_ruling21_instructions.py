"""
Tests for scripts/derive_ruling21_instructions.py — the ruling-21
instruction-set derivation.

Tier 1: synthetic exercises of the survivor-selection and clustering
rules, each pinned to the Session-130 decision it implements. The
cross-cluster non-merge case is the load-bearing one: an earlier draft
of the derivation unioned claim chains transitively and would have
deleted real mounds (the ``student:4635 → phantom:699 → student:4634``
chain spans 170 m and is two mounds).

Tier 2: the full derivation against the committed campaign layers must
reproduce the census this instruction set was signed off on.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from derive_ruling21_instructions import (  # noqa: E402
    _DEFAULT_GT_DIR,
    _DEFAULT_STUDENT_GT,
    Derivation,
    Node,
    build_clusters,
    choose_survivor,
    derive,
    load_inputs,
    survivor_position,
)


def _node(node_id: str, layer: str, index: int, x: float = 0.0, y: float = 0.0,
          **kwargs) -> Node:
    return Node(node_id, layer, index, x, y, **kwargs)


# ---------------------------------------------------------------------------
# Survivor selection
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_student_beats_phantom() -> None:
    """Prefer the student record over the phantom (spec § How to count)."""
    student = _node("student:1", "corrected_student", 1, claims="phantom:2")
    phantom = _node("phantom:2", "promoted_phantom", 2)
    survivor, tiebreak = choose_survivor([phantom, student])
    assert survivor is student
    assert not tiebreak


@pytest.mark.tier1
def test_claimed_partner_beats_claimant() -> None:
    """Student→student: the claimant is the duplicate (S130 decision)."""
    claimant = _node("student:1", "corrected_student", 1, claims="student:2")
    partner = _node("student:2", "corrected_student", 2)
    survivor, tiebreak = choose_survivor([claimant, partner])
    assert survivor is partner
    assert not tiebreak


@pytest.mark.tier1
def test_w7r2_model_detection_yields_to_phantom() -> None:
    """Student #4744/#4745 are model detections, not student provenance."""
    curator = _node("student:4744", "corrected_student", 4744, claims="phantom:2")
    phantom = _node("phantom:2", "promoted_phantom", 2)
    survivor, _ = choose_survivor([curator, phantom])
    assert survivor is phantom


@pytest.mark.tier1
def test_restored_premerge_counts_as_student() -> None:
    """A restored pre-merge original is student digitisation."""
    restored = _node("superseded:46", "superseded_premerge", 46)
    phantom = _node("phantom:389", "promoted_phantom", 389,
                    claims="superseded:46")
    survivor, _ = choose_survivor([phantom, restored])
    assert survivor is restored


@pytest.mark.tier1
def test_mutual_phantom_pair_flags_the_index_tiebreak() -> None:
    """Mutual claims tie on every principled rank; index decides, flagged."""
    a = _node("phantom:10", "promoted_phantom", 10, claims="phantom:476")
    b = _node("phantom:476", "promoted_phantom", 476, claims="phantom:10")
    survivor, tiebreak = choose_survivor([b, a])
    assert survivor is a
    assert tiebreak


# ---------------------------------------------------------------------------
# Survivor position
# ---------------------------------------------------------------------------


@pytest.mark.tier1
def test_reviewed_survivor_keeps_its_own_mark() -> None:
    survivor = _node("student:2", "corrected_student", 2, x=50.0, y=50.0,
                     mark=(10.0, 20.0), verdict="distinct")
    x, y, source = survivor_position(survivor, [survivor], Derivation())
    assert (x, y, source) == (10.0, 20.0, "own_mark")


@pytest.mark.tier1
def test_unreviewed_survivor_inherits_the_claimant_mark() -> None:
    """The survivor inherits the claimant's marked centre, not its own
    original position — the attractor-displacement correction."""
    claimant = _node("student:1", "corrected_student", 1,
                     mark=(10.0, 20.0), verdict="same_as_neighbour",
                     claims="student:2")
    partner = _node("student:2", "corrected_student", 2, x=105.0, y=20.0)
    x, y, source = survivor_position(partner, [claimant, partner], Derivation())
    assert (x, y, source) == (10.0, 20.0, "claimant_mark")


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------


def _clustered(nodes: list[Node]) -> tuple[list[set], Derivation]:
    derivation = Derivation()
    clusters = build_clusters({n.node_id: n for n in nodes}, derivation)
    return (
        [{m.node_id for m in members} for members in clusters.values()],
        derivation,
    )


@pytest.mark.tier1
def test_claim_chain_does_not_merge_distant_marks() -> None:
    """A claim onto a marked record in another cluster must NOT merge.

    Modelled on student:4635 → phantom:699 → student:4634: the end
    members are two different mounds. The claim is reported as
    superseded, and membership follows the marks.
    """
    south = _node("student:4635", "corrected_student", 4635,
                  mark=(0.0, 0.0), verdict="same_as_neighbour",
                  claims="phantom:699")
    detection = _node("phantom:699", "promoted_phantom", 699,
                      mark=(0.0, 165.0), verdict="same_as_neighbour",
                      claims="student:4634")
    north = _node("student:4634", "corrected_student", 4634, x=5.0, y=160.0)
    groups, derivation = _clustered([south, detection, north])
    assert {"student:4635"} in groups
    assert {"phantom:699", "student:4634"} in groups
    assert derivation.summary["cross_cluster_claims"] == [{
        "claimant": "student:4635", "target": "phantom:699",
        "marks_apart_m": 165.0,
    }]


@pytest.mark.tier1
def test_claim_within_the_distinct_floor_corroborates_one_mound() -> None:
    """Marks straddling the 5 m tolerance union when a claim links them
    inside the 15 m floor (the student:861 ↔ phantom:329 case)."""
    student = _node("student:861", "corrected_student", 861,
                    mark=(0.0, 0.0), verdict="same_as_neighbour",
                    claims="phantom:329")
    phantom = _node("phantom:329", "promoted_phantom", 329,
                    mark=(5.03, 0.0), verdict="same_as_neighbour",
                    claims="student:861")
    groups, derivation = _clustered([student, phantom])
    assert {"student:861", "phantom:329"} in groups
    assert derivation.summary["cross_cluster_claims"] == []


@pytest.mark.tier1
def test_removed_records_do_not_glue_clusters() -> None:
    """An x-verdicted record never joins (or bridges) a cluster."""
    fp = _node("phantom:1", "promoted_phantom", 1,
               mark=(2.0, 0.0), verdict="not_a_mound")
    real = _node("student:1", "corrected_student", 1,
                 mark=(0.0, 0.0), verdict="distinct")
    groups, _ = _clustered([fp, real])
    assert {"student:1"} in groups
    assert not any("phantom:1" in g for g in groups)


# ---------------------------------------------------------------------------
# Tier 2 — the committed campaign layers
# ---------------------------------------------------------------------------


@pytest.mark.tier2
def test_derivation_reproduces_the_census() -> None:
    """The full derivation must reproduce the signed-off census."""
    gt_dir = PROJECT_ROOT / _DEFAULT_GT_DIR
    student_gt = PROJECT_ROOT / _DEFAULT_STUDENT_GT
    if not gt_dir.exists() or not student_gt.exists():
        pytest.skip("campaign layers not present in this checkout")
    derivation = derive(load_inputs(gt_dir, student_gt))
    summary = derivation.summary
    assert summary["actions"] == {
        "keep_student": 639,
        "remove_duplicate": 466,
        "keep_phantom_extension": 278,
        "remove_fp": 45,
        "restore_premerge": 2,
        "remove_contradicted_merge": 1,
        "add_marking_pass_extra": 1,
    }
    assert summary["final_student_layer"] == {
        "before": 4746, "removed": 17, "restored_premerge": 2,
        "after": 4731, "out_of_scope_implicit": 4090,
    }
    assert summary["confidence_grades_assigned"] == {
        "directly_reviewed": 806, "proxy_confirmed": 114,
    }
    # Zero since the 2026-08-14 walk resolved all six cross-cluster
    # claimants to `distinct`, retiring their contradictory claims.
    assert len(summary["cross_cluster_claims"]) == 0
    assert len(summary["clusters"]["index_tiebreaks"]) == 24
