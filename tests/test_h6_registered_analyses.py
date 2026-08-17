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

from h6_registered_analyses import (  # noqa: E402
    A08_STATEMENT,
    argmax_with_margin,
    committed_f1,
    gate_model_provenance,
    limbs,
)
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
    assert "exactly ONE" in A08_STATEMENT


def _pass(run, pool, model):
    return {"run_id": run, "proposer_pool": pool, "model_used": model}


@pytest.mark.tier1
def test_provenance_gate_three_paths():
    """The BLOCKER-1 gate passes, fails on wrong model, fails on empty."""
    good = (
        [_pass("n1-pro-rerun-384", p, "gemini-3.1-pro-preview")
         for p in ("pro-text-high-t0", "pro-text-medium-t07",
                   "pro-image-high-t0", "pro-image-medium-t07")]
        + [_pass("n1-outstanding-384", p, "gemini-3-flash-preview")
           for p in ("pro-text-high-t0", "pro-text-medium-t07",
                     "pro-image-high-t0", "pro-image-medium-t07")]
        + [_pass("pv-diag-384", p, "gemini-3.1-pro-preview")
           for p in ("pro-high-text-n5-text-t0.7",
                     "pro-high-image-n5-image-t0.7",
                     "pro-medium-text-baseline-text-t0.0",
                     "pro-medium-image-baseline-image-t0.0")])
    record = gate_model_provenance(good)
    assert len(record) == 12

    bad = list(good)
    bad[0] = _pass("n1-pro-rerun-384", "pro-text-high-t0",
                   "gemini-3-flash-preview")
    with pytest.raises(SystemExit):
        gate_model_provenance(bad)

    with pytest.raises(SystemExit):
        gate_model_provenance(good[1:])  # first pool now empty


@pytest.mark.tier1
def test_a09_limbs_require_cost_comparability():
    """Limb 1 needs BOTH the F1 ratio and comparable cost (audit H-1).

    The real image row (ratio 1.2051 at a 32 % cost premium) must NOT
    fire; the text row (3.5 % premium) must.
    """
    text = limbs(0.8045, 1.8533, 0.5665, 1.7913)
    assert text["limb1_fires (>=1.20 F1 at comparable cost)"] is True
    image = limbs(0.6658, 15.7365, 0.5525, 11.9151)
    assert image["cost_comparable_within_10pct"] is False
    assert image["limb1_fires (>=1.20 F1 at comparable cost)"] is False
    # Limb 2: comparable F1 at <= 50 % cost.
    cheap = limbs(0.870, 1.0, 0.880, 2.5)
    assert cheap["limb2_fires (comparable F1 at <=50% cost)"] is True
    dear = limbs(0.870, 1.9, 0.880, 2.5)
    assert dear["limb2_fires (comparable F1 at <=50% cost)"] is False


@pytest.mark.tier1
def test_argmax_with_margin():
    """Reports the winner and its margin over the runner-up."""
    k, margin = argmax_with_margin({1: 0.5509, 2: 0.5499, 3: 0.5525})
    assert k == 3
    assert margin == pytest.approx(0.0016)
