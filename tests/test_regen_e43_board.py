"""Tests for ``scripts.regen_e43_board`` — the E72 board regeneration harness.

The statistical machinery this script consumes is imported verbatim from the
project's canonical implementations (``apply_fdr_correction.apply_bh_correction``
and ``n1_baseline_leaderboard_tiering.greedy_clique_tiers``), each covered by
its own suite. What is new here, and pinned below, is the E72-specific logic:

Tier 1 (synthetic, no input/output):
  1. ``source_is_confounded`` — flags an arm by its recorded on-disk provenance,
     never by its display label, and tolerates missing/non-string source fields.
  2. ``PairTest.key`` — the unordered pair key used as the significance-map key.
  3. ``rank_conditions`` — F1 descending with a deterministic label tiebreak.
  4. ``condition_metrics`` — collects per-condition metrics and fails loud when
     a condition's metrics disagree between tests (Gate C).
  5. ``split_confounded`` — partitions a board into retained and dropped pairs.
  6. ``build_board`` — BH plus greedy-clique tiering over a synthetic board.
  7. ``tier_movement`` / ``significance_changes`` — the movement report.
  8. ``recompute_families`` — drops confounded members, recomputes BH within
     the family, and reports per-member status changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.regen_e43_board import (  # noqa: E402
    CONFOUNDED_STUDY_MARKER,
    PairTest,
    build_board,
    condition_metrics,
    rank_conditions,
    recompute_families,
    significance_changes,
    source_is_confounded,
    split_confounded,
    tier_movement,
)


def make_test(
    label_a: str,
    label_b: str,
    f1_a: float,
    f1_b: float,
    p_value: float,
    *,
    confounded: bool = False,
) -> PairTest:
    """Build a synthetic :class:`PairTest` with plausible filler metrics.

    Args:
        label_a: Condition A label.
        label_b: Condition B label.
        f1_a: Condition A F1.
        f1_b: Condition B F1.
        p_value: Raw permutation p-value.
        confounded: Whether the pair touches the E72 study.

    Returns:
        A populated :class:`PairTest`.
    """
    return PairTest(
        label_a=label_a,
        label_b=label_b,
        f1_a=f1_a,
        f1_b=f1_b,
        precision_a=f1_a,
        precision_b=f1_b,
        recall_a=f1_a,
        recall_b=f1_b,
        n_detections_a=int(f1_a * 1000),
        n_detections_b=int(f1_b * 1000),
        delta_f1=f1_a - f1_b,
        p_value=p_value,
        confounded=confounded,
        source_file=f"synthetic/{label_a}-vs-{label_b}.json",
    )


# --------------------------------------------------------------------------- #
# 1. source_is_confounded — provenance, not labels
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_source_is_confounded_matches_study_dir() -> None:
    """A consensus arm pointing at the 240-tile study is flagged."""
    source = {
        "mode": "consensus",
        "study_dir": f"outputs/h11/{CONFOUNDED_STUDY_MARKER}",
        "pool_size": 10,
        "threshold": 9,
    }
    assert source_is_confounded(source) is True


@pytest.mark.tier1
def test_source_is_confounded_matches_geojson_arm() -> None:
    """The N=1 geojson-mode arm is flagged by its detections path."""
    source = {
        "mode": "geojson",
        "geojson": (
            f"/home/shawn/Code/map-reader-llm/outputs/h11/{CONFOUNDED_STUDY_MARKER}"
            "/384/run_1/detections_384_run01.geojson"
        ),
    }
    assert source_is_confounded(source) is True


@pytest.mark.tier1
def test_source_is_confounded_ignores_clean_arms() -> None:
    """A clean proposer-verifier arm is not flagged, non-strings do not crash."""
    source = {
        "mode": "pv",
        "probabilities": "outputs/h11/pv-diag-384/verified/x/probabilities.json",
        "threshold": 0.15,
    }
    assert source_is_confounded(source) is False


@pytest.mark.tier1
def test_source_is_confounded_handles_missing_source() -> None:
    """A missing or empty source mapping is not confounded."""
    assert source_is_confounded(None) is False
    assert source_is_confounded({}) is False


@pytest.mark.tier1
def test_source_is_confounded_ignores_label_aliases() -> None:
    """A t10 LABEL with a clean source is not flagged — provenance decides."""
    source = {"mode": "consensus", "study_dir": "outputs/h11/pv-diag-384/text-t1.0"}
    assert source_is_confounded(source) is False


# --------------------------------------------------------------------------- #
# 2. PairTest.key
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_pair_test_key_is_unordered() -> None:
    """The pair key does not depend on which arm is A."""
    forward = make_test("A", "B", 0.9, 0.8, 0.1)
    reverse = make_test("B", "A", 0.8, 0.9, 0.1)
    assert forward.key == reverse.key


# --------------------------------------------------------------------------- #
# 3. rank_conditions
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_rank_conditions_orders_by_f1_then_label() -> None:
    """F1 descending, with ties broken deterministically on the label."""
    metrics = {
        "beta": {"f1": 0.80},
        "alpha": {"f1": 0.80},
        "gamma": {"f1": 0.95},
    }
    assert rank_conditions(metrics) == ["gamma", "alpha", "beta"]


# --------------------------------------------------------------------------- #
# 4. condition_metrics — Gate C
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_condition_metrics_collects_each_condition_once() -> None:
    """Each condition contributes one metric record regardless of arm position."""
    tests = [
        make_test("A", "B", 0.9, 0.8, 0.01),
        make_test("A", "C", 0.9, 0.5, 0.0),
        make_test("B", "C", 0.8, 0.5, 0.0),
    ]
    metrics = condition_metrics(tests)
    assert set(metrics) == {"A", "B", "C"}
    assert metrics["A"]["f1"] == pytest.approx(0.9)
    assert metrics["C"]["n_detections"] == pytest.approx(500)


@pytest.mark.tier1
def test_condition_metrics_rejects_inconsistent_metrics() -> None:
    """A condition scored two different ways fails loud rather than silently."""
    tests = [
        make_test("A", "B", 0.9, 0.8, 0.01),
        make_test("A", "C", 0.7, 0.5, 0.0),  # A's F1 disagrees
    ]
    with pytest.raises(AssertionError, match="inconsistent f1"):
        condition_metrics(tests)


# --------------------------------------------------------------------------- #
# 5. split_confounded
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_split_confounded_partitions_the_board() -> None:
    """Confounded pairs leave the family; retained pairs keep their order."""
    tests = [
        make_test("A", "B", 0.9, 0.8, 0.01),
        make_test("A", "X", 0.9, 0.4, 0.0, confounded=True),
        make_test("B", "X", 0.8, 0.4, 0.0, confounded=True),
    ]
    retained, dropped = split_confounded(tests)
    assert [t.key for t in retained] == [frozenset({"A", "B"})]
    assert len(dropped) == 2


# --------------------------------------------------------------------------- #
# 6. build_board — BH plus greedy-clique tiering
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_build_board_tiers_indistinguishable_conditions_together() -> None:
    """A and B are indistinguishable, C is worse than both: two tiers."""
    tests = [
        make_test("A", "B", 0.90, 0.88, 0.50),
        make_test("A", "C", 0.90, 0.50, 0.00),
        make_test("B", "C", 0.88, 0.50, 0.00),
    ]
    board = build_board("synthetic", tests)
    assert board.order == ["A", "B", "C"]
    assert board.tiers == [["A", "B"], ["C"]]
    assert board.n_significant == 2
    assert board.tier_of("B") == 1
    assert board.tier_of("C") == 2


@pytest.mark.tier1
def test_build_board_shrinking_family_can_change_significance() -> None:
    """BH is family-size dependent — the point of the whole regeneration.

    A borderline p-value that survives correction in a two-member family fails
    it in a larger family, so recomputing over the retained members is not a
    no-op in general.
    """
    small = build_board("small", [make_test("A", "B", 0.9, 0.8, 0.04)])
    assert small.n_significant == 1

    large = build_board(
        "large",
        [
            make_test("A", "B", 0.90, 0.80, 0.04),
            make_test("A", "C", 0.90, 0.85, 0.60),
            make_test("B", "C", 0.80, 0.85, 0.70),
        ],
    )
    assert large.n_significant == 0


# --------------------------------------------------------------------------- #
# 7. movement reporting
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_tier_movement_reports_promotion_after_dropping_a_cell() -> None:
    """Dropping a distinguishable cell can merge tiers and promote survivors."""
    full = build_board(
        "full",
        [
            make_test("A", "B", 0.90, 0.60, 0.0),
            make_test("A", "C", 0.90, 0.50, 0.0),
            make_test("B", "C", 0.60, 0.50, 0.0),
        ],
    )
    reduced = build_board("reduced", [make_test("A", "B", 0.90, 0.60, 0.40)])
    movement = tier_movement(full, reduced)
    by_condition = {record["condition"]: record for record in movement}
    assert by_condition["A"]["tier_old"] == 1
    assert by_condition["B"]["tier_old"] == 2
    assert by_condition["B"]["tier_new"] == 1
    assert by_condition["B"]["delta_tier"] == -1
    assert "C" not in by_condition


@pytest.mark.tier1
def test_significance_changes_lists_only_flipped_pairs() -> None:
    """Only retained pairs whose verdict flipped appear in the change list."""
    full = build_board(
        "full",
        [
            make_test("A", "B", 0.90, 0.80, 0.04),
            make_test("A", "C", 0.90, 0.85, 0.60),
            make_test("B", "C", 0.80, 0.85, 0.70),
        ],
    )
    reduced = build_board("reduced", [make_test("A", "B", 0.90, 0.80, 0.04)])
    changes = significance_changes(full, reduced)
    assert len(changes) == 1
    assert changes[0]["was_significant"] is False
    assert changes[0]["is_significant"] is True


# --------------------------------------------------------------------------- #
# 8. recompute_families
# --------------------------------------------------------------------------- #


def _member(
    family: str, group: int, question: str, p_raw: float, p_adj: float, confounded: bool
) -> dict:
    """Build a synthetic family-member record.

    Args:
        family: BH family name.
        group: Comparison group number.
        question: Comparison question label.
        p_raw: Raw p-value.
        p_adj: Published BH-adjusted p-value.
        confounded: Whether this member is an E72 casualty.

    Returns:
        A record shaped like a manifest comparison entry.
    """
    return {
        "family": family,
        "group": group,
        "question": question,
        "label_a": f"{question} A",
        "label_b": f"{question} B",
        "p_value_raw": p_raw,
        "p_value_adj": p_adj,
        "confounded": confounded,
    }


@pytest.mark.tier1
def test_recompute_families_drops_confounded_and_recorrects() -> None:
    """A four-member family loses two members; BH is redone over the rest."""
    records = [
        _member("temperature", 4, "N=5", 0.0000, 0.0000, True),
        _member("temperature", 4, "N=10", 0.0000, 0.0000, True),
        _member("temperature", 12, "P2b text", 0.0055, 0.0066, False),
        _member("temperature", 12, "P2b image", 0.4763, 0.4763, False),
    ]
    (summary,) = recompute_families(records)
    assert summary["family"] == "temperature"
    assert summary["n_published"] == 4
    assert summary["n_dropped"] == 2
    assert summary["n_retained"] == 2
    # BH over two members: 0.0055 * 2 / 1 = 0.011; 0.4763 * 2 / 2 = 0.4763.
    q_values = {m["question"]: m["q_recomputed"] for m in summary["members"]}
    assert q_values["P2b text"] == pytest.approx(0.011, abs=1e-6)
    assert q_values["P2b image"] == pytest.approx(0.4763, abs=1e-6)
    assert summary["significant_recomputed"] == 1


@pytest.mark.tier1
def test_recompute_families_leaves_clean_families_with_zero_dropped() -> None:
    """A family with no confounded member reports n_dropped == 0."""
    records = [
        _member("modality", 2, "text vs image", 0.0143, 0.0196, False),
        _member("modality", 2, "text vs image (N=10)", 0.0054, 0.0108, False),
    ]
    (summary,) = recompute_families(records)
    assert summary["n_dropped"] == 0
    assert summary["n_retained"] == 2


@pytest.mark.tier1
def test_recompute_families_flags_status_changes() -> None:
    """A member whose verdict flips under the smaller family is flagged."""
    records = [
        _member("thinking", 4, "confounded", 0.0000, 0.0000, True),
        _member("thinking", 3, "borderline", 0.0400, 0.0800, False),
    ]
    (summary,) = recompute_families(records)
    (member,) = summary["members"]
    # Alone in the family, 0.04 * 1 / 1 = 0.04 < 0.05 — it flips to significant.
    assert member["q_recomputed"] == pytest.approx(0.04, abs=1e-6)
    assert member["status_changed"] is True
    assert summary["significant_recomputed"] == 1
