"""Tier-1 tests for scripts/h6_registered_analyses.py.

Covers the pure helpers (manifest F1 lookup) and documents the two
design invariants the S135 audit adjudication rests on: the
registered A-07 form is data-independent across mismatched pool
sizes (HIGH-5), while the matched-N form discriminates; and the A-08
statement ships with every artefact (hardening 7). The data stages
(model-provenance gate, consensus materialisation, scoring) are
exercised by the live sapphire run and its gates.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from h6_registered_analyses import A08_STATEMENT, committed_f1  # noqa: E402
from lib_phase4_transfer import (  # noqa: E402
    evaluate_voting_threshold_transfer,
)


@pytest.mark.tier1
def test_committed_f1_lookup_and_miss():
    """Lookup returns the per_buffer 20 m F1 and raises on a miss."""
    conditions = [{
        "run_id": "r1",
        "condition_id": "r1::cell-a",
        "metrics": {"per_buffer": {"20": {"f1": 0.5665}}},
    }]
    assert committed_f1(conditions, "r1", "cell-a") == 0.5665
    with pytest.raises(KeyError):
        committed_f1(conditions, "r1", "cell-b")


@pytest.mark.tier1
def test_a07_registered_form_is_data_independent():
    """Raw vote counts across N=30 vs N=3 pools always flag (HIGH-5).

    Every possible Pro threshold k in 1..3 differs from the Flash
    production optimum 26 by more than 88 % relative, so the
    registered >10 % rule cannot discriminate — the reason A-07 runs
    matched-N instead.
    """
    for k in (1, 2, 3):
        res = evaluate_voting_threshold_transfer(
            flash_optimal_n=30, flash_optimal_threshold=26,
            pro_optimal_n=3, pro_optimal_threshold=k)
        assert res.flagged is True
        assert res.relative_difference > 0.88


@pytest.mark.tier1
def test_a07_matched_n_form_discriminates():
    """At matched N the rule passes on equality and flags a 1-vs-3 gap."""
    same = evaluate_voting_threshold_transfer(
        flash_optimal_n=3, flash_optimal_threshold=3,
        pro_optimal_n=3, pro_optimal_threshold=3)
    assert same.flagged is False
    far = evaluate_voting_threshold_transfer(
        flash_optimal_n=3, flash_optimal_threshold=3,
        pro_optimal_n=3, pro_optimal_threshold=1)
    assert far.flagged is True


@pytest.mark.tier1
def test_a08_statement_names_the_criterion():
    """The A-08 statement is explicit about non-computability."""
    assert "not computed" in A08_STATEMENT
    assert "693-699" in A08_STATEMENT
    assert "confound" in A08_STATEMENT
