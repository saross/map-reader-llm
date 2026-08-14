"""
Tests for scripts/materialise_standardised_reference.py.

Tier 1: the grade tally helper on synthetic inputs.

Tier 2: full materialisation from the committed instruction set,
asserting the census, the removals, the restorations, and the anchor
positions that the PI's walk pinned. This is the artefact-level
counterpart of the derivation's census test: if either the instruction
set or the source layers drift, the build must fail loudly, never
materialise silently.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from materialise_standardised_reference import (  # noqa: E402
    _DEFAULT_GT_DIR,
    _DEFAULT_STUDENT_GT,
    build_extension_layer,
    build_student_layer,
    grade_tallies,
    load_instructions,
)


@pytest.mark.tier1
def test_grade_tallies_counts_both_layers() -> None:
    student_layer = {"features": [
        {"properties": {"std_confidence_grade": "directly_reviewed"}},
        {"properties": {"std_confidence_grade": "out_of_scope"}},
        {"properties": {"std_confidence_grade": "out_of_scope"}},
    ]}
    extension = [{"confidence_grade": "directly_reviewed"}]
    tallies = grade_tallies(student_layer, extension)
    assert tallies["student"] == {"directly_reviewed": 1, "out_of_scope": 2}
    assert tallies["extension"] == {"directly_reviewed": 1}


@pytest.mark.tier2
def test_materialisation_reproduces_the_census() -> None:
    """Build both layers from the committed state and check every anchor."""
    gt_dir = PROJECT_ROOT / _DEFAULT_GT_DIR
    student_gt = PROJECT_ROOT / _DEFAULT_STUDENT_GT
    if not gt_dir.exists() or not student_gt.exists():
        pytest.skip("campaign layers not present in this checkout")

    instructions, summary = load_instructions(gt_dir)
    student_layer = build_student_layer(instructions, summary, student_gt, gt_dir)
    extension = build_extension_layer(
        instructions, summary, gt_dir, student_layer,
        gt_dir / "extra-review-items.csv",
    )

    # Census.
    assert len(student_layer["features"]) == 4731
    assert len(extension) == 279
    tallies = grade_tallies(student_layer, extension)
    assert tallies["student"] == {
        "directly_reviewed": 527, "proxy_confirmed": 114, "out_of_scope": 4090,
    }
    assert tallies["extension"] == {"directly_reviewed": 279}

    by_index = {
        f["properties"]["std_source_index"]: f
        for f in student_layer["features"]
        if f["properties"]["std_source_index"] is not None
    }

    # Removals: the 4 false positives, the contradicted merge, and the
    # two W7-R2 model-provenance curator additions must be absent.
    for removed in (2508, 2536, 2601, 4559, 4172, 4744, 4745):
        assert removed not in by_index

    # The PI's walk pinned #4547's re-centred mark.
    x, y = by_index[4547]["geometry"]["coordinates"]
    assert (round(x, 3), round(y, 3)) == (432575.074, 4643765.601)

    # Restorations: exactly two, provenance-tagged, one proxy-positioned.
    restored = [
        f for f in student_layer["features"]
        if f["properties"]["std_provenance"] == "restored_premerge"
    ]
    assert len(restored) == 2
    assert sorted(
        f["properties"]["std_position_source"] for f in restored
    ) == ["as_recorded", "claimant_mark"]

    # A proxy confirmation: #4634 inherits phantom:699's mark.
    assert by_index[4634]["properties"]["std_confidence_grade"] == "proxy_confirmed"
    assert by_index[4634]["properties"]["std_position_source"] == "claimant_mark"

    # Extension integrity: unique ids, one marking-pass extra, and the
    # exact-position distances all positive.
    ids = [r["candidate_id"] for r in extension]
    assert len(ids) == len(set(ids))
    assert sum(1 for r in extension if r["provenance"] == "marking_pass_extra") == 1
    assert all(r["nearest_student_m"] > 0 for r in extension)
