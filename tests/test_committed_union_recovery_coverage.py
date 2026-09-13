"""
The five repaired consensus unions must keep covering their recovery fragments.

Guards the PI's "fix properly" ruling of 2026-09-13. ``merge_passes.py`` used to
derive a pass directory's number by casting the text after the ``run_`` prefix, so
``int("2_recovery")`` raised and an ``except ValueError: continue`` **silently**
dropped every storm-recovery fragment. Five committed unions were built through
that blind spot; commit ``75d7c8d4cd55b6ec8d2a40abff70a31f62b67725`` folds each
fragment into its parent pass, and the five were rebuilt
(``reports/recovery-drop-fix-2026-09-13.md``).

The defect was invisible in three ways at once, and each is a separate assertion
here:

* the skip logged nothing, so only the artefact records whether a fragment was
  read — hence the ``pass_provenance`` assertions;
* ``merge_passes --sweep`` reproduces a wrong union perfectly when re-run with
  the same defective resolver, so "it rebuilds to the same number" proves
  nothing — hence the exact expected candidate counts, which are the corrected
  ones;
* one union's count did not change at all when the fragment was folded in
  (640 before, 640 after, one candidate displaced), so a count check alone would
  have passed it — hence ``test_pass_count_is_not_inflated_by_folding`` and the
  fragment-coverage assertions, which do not depend on counts.

These tests read COMMITTED artefacts rather than rebuilding anything, so they
stay fast and tier 1, and they fail if anyone re-materialises one of these five
unions with a resolver that has regressed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.merge_passes import PASS_PROVENANCE_SCHEMA  # noqa: E402

pytestmark = pytest.mark.tier1

#: A pass directory name, split into its number and any fragment suffix.
_PASS_DIR = re.compile(r"^(?:pass|run)_(?P<num>\d+)(?P<suffix>.*)$")

#: The three rebuilt consensus directories, with the pool that feeds each, the
#: ``--passes`` selection the committed build recorded in its
#: ``experiment_intent.md``, and the corrected candidate count per vote
#: threshold. Counts are the ones
#: ``reports/recovery-fragment-drop-2026-09-13.md`` § 3.1 predicted and the
#: rebuild reproduced exactly.
UNIONS: tuple[dict, ...] = (
    {
        "id": "gemini37-screen consensus-n1",
        "pool": "outputs/gemini37-screen-2026-08-28/g384_ov192_g37",
        "consensus_dir": (
            "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n1"
        ),
        "passes": (1,),
        "expected_counts": {"1": 640},
    },
    {
        "id": "gemini37-screen consensus-n3",
        "pool": "outputs/gemini37-screen-2026-08-28/g384_ov192_g37",
        "consensus_dir": (
            "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/consensus-n3"
        ),
        "passes": (1, 2, 3),
        "expected_counts": {"1": 759, "2": 609, "3": 530},
    },
    {
        "id": "grid consensus-n5",
        "pool": "outputs/grid-2026-08-18/g384_ov192",
        "consensus_dir": "outputs/grid-2026-08-18/g384_ov192/consensus-n5",
        "passes": (1, 2, 3, 4, 5),
        "expected_counts": {
            "1": 2932,
            "2": 2025,
            "3": 1650,
            "4": 1396,
            "5": 1169,
        },
    },
)


def _summary(union: dict) -> dict:
    """Load a rebuilt union's ``voting_summary.json``.

    Args:
        union: One entry of :data:`UNIONS`.

    Returns:
        The parsed voting summary.
    """
    path = PROJECT_ROOT / union["consensus_dir"] / "voting_summary.json"
    assert path.is_file(), f"{union['id']}: missing {path}"
    return json.loads(path.read_text())


def _fragments_in_selection(union: dict) -> dict[int, list[str]]:
    """Return the pool's recovery fragment directories, by parent pass number.

    Only passes inside the union's ``--passes`` selection are returned, because a
    fragment outside the selection is correctly absent from the union.

    Args:
        union: One entry of :data:`UNIONS`.

    Returns:
        Mapping of pass number to the fragment directory names under it.
    """
    pool = PROJECT_ROOT / union["pool"]
    found: dict[int, list[str]] = {}
    for child in sorted(pool.iterdir()):
        if not child.is_dir():
            continue
        match = _PASS_DIR.match(child.name)
        if not match or not match.group("suffix"):
            continue
        number = int(match.group("num"))
        if number in union["passes"]:
            found.setdefault(number, []).append(child.name)
    return found


@pytest.mark.parametrize("union", UNIONS, ids=lambda u: u["id"])
def test_pool_still_has_the_fragments_these_tests_are_about(union: dict) -> None:
    """The premise: each selection really does contain a recovery fragment.

    Without this the coverage assertions below would pass vacuously if the
    fragment directories were ever moved or renamed.
    """
    fragments = _fragments_in_selection(union)
    assert fragments, (
        f"{union['id']}: no run_<N>_recovery* directory inside passes "
        f"{union['passes']} — either the pool moved or this test is now vacuous"
    )


@pytest.mark.parametrize("union", UNIONS, ids=lambda u: u["id"])
def test_pass_provenance_covers_every_recovery_fragment(union: dict) -> None:
    """Every fragment in the selection appears in ``pass_provenance``.

    This is the artefact-level signature of the fix: the defective resolver
    logged nothing when it skipped a fragment, so the provenance block is the
    only place the union itself records whether the fragment was read.
    """
    summary = _summary(union)
    assert summary.get("pass_provenance_schema") == PASS_PROVENANCE_SCHEMA
    recorded = {Path(entry["path"]).parent.name for entry in summary["pass_provenance"]}

    missing = [
        name
        for names in _fragments_in_selection(union).values()
        for name in names
        if name not in recorded
    ]
    assert not missing, (
        f"{union['id']}: recovery fragment(s) {missing} absent from "
        f"pass_provenance — the recovery-fragment drop has regressed "
        f"(fix 75d7c8d4c)"
    )


@pytest.mark.parametrize("union", UNIONS, ids=lambda u: u["id"])
def test_a_fragment_is_credited_to_its_parent_pass(union: dict) -> None:
    """A fragment must join an existing pass, never announce a new one.

    The fix keeps the main directory's name as the pass id, so ``run_2_recovery``
    is recorded under ``pass_id`` ``run_2``. Getting this wrong would inflate the
    vote denominator instead of correcting it.
    """
    summary = _summary(union)
    for entry in summary["pass_provenance"]:
        directory = Path(entry["path"]).parent.name
        match = _PASS_DIR.match(directory)
        assert match, f"{union['id']}: unparsable pass directory {directory}"
        if not match.group("suffix"):
            continue
        expected = f"run_{int(match.group('num'))}"
        assert entry["pass_id"] == expected, (
            f"{union['id']}: fragment {directory} is credited to "
            f"{entry['pass_id']!r}, not to its parent pass {expected!r}"
        )


@pytest.mark.parametrize("union", UNIONS, ids=lambda u: u["id"])
def test_pass_count_is_not_inflated_by_folding(union: dict) -> None:
    """Folding a fragment must not change the pass count or the vote denominator.

    ``total_passes`` is the divisor ``apply_threshold`` writes ``confidence``
    with, and the defect's graver half was computing it over the wrong pass
    count. The selection size is the only correct value.
    """
    summary = _summary(union)
    assert summary["total_passes"] == len(union["passes"])
    assert len(summary["pass_ids"]) == len(union["passes"])
    assert sorted(summary["pass_ids"]) == sorted(
        f"run_{number}" for number in union["passes"]
    )
    # Every fragment shares its parent's id, so the id set stays the pass set
    # even though pass_provenance has more entries than passes.
    assert len(summary["pass_provenance"]) >= len(union["passes"])


@pytest.mark.parametrize("union", UNIONS, ids=lambda u: u["id"])
def test_committed_counts_are_the_corrected_ones(union: dict) -> None:
    """Each threshold file holds the corrected candidate count.

    The defective resolver reproduced its own wrong counts exactly, so a
    self-consistency check cannot catch this; only the absolute corrected
    numbers can. ``consensus-n1`` is why these are asserted per file rather than
    only in the summary: its count is 640 either way, and the fix changed which
    candidates are in it, not how many.
    """
    summary = _summary(union)
    assert summary["thresholds"] == {
        key: value for key, value in union["expected_counts"].items()
    }, f"{union['id']}: voting_summary thresholds moved"

    for threshold, expected in union["expected_counts"].items():
        path = (
            PROJECT_ROOT
            / union["consensus_dir"]
            / f"consensus_t{threshold}.geojson"
        )
        assert path.is_file(), f"{union['id']}: missing {path}"
        features = json.loads(path.read_text())["features"]
        assert len(features) == expected, (
            f"{union['id']}: consensus_t{threshold}.geojson holds "
            f"{len(features)} candidates, expected {expected}"
        )


def test_the_five_files_the_ruling_names_all_exist_at_their_counts() -> None:
    """The PI's ruling names five files; assert them as a set, once.

    A belt-and-braces guard against a future edit to :data:`UNIONS` quietly
    dropping one of the five from coverage.
    """
    expected = {
        (
            "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/"
            "consensus-n3/consensus_t1.geojson"
        ): 759,
        (
            "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/"
            "consensus-n3/consensus_t2.geojson"
        ): 609,
        (
            "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/"
            "consensus-n3/consensus_t3.geojson"
        ): 530,
        (
            "outputs/gemini37-screen-2026-08-28/g384_ov192_g37/"
            "consensus-n1/consensus_t1.geojson"
        ): 640,
        "outputs/grid-2026-08-18/g384_ov192/consensus-n5/consensus_t5.geojson": 1169,
    }
    measured = {
        path: len(json.loads((PROJECT_ROOT / path).read_text())["features"])
        for path in expected
    }
    assert measured == expected
