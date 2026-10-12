"""Tier-1 tests for scripts/h6_registered_analyses.py.

Covers the pure helpers (manifest F1 lookup) and documents the two
design invariants the S135 audit adjudication rests on: the
registered A-07 form is data-independent across mismatched pool
sizes (HIGH-5), while the matched-N form discriminates; and the A-08
statement ships with every artefact (hardening 7). The data stages
(model-provenance gate, consensus materialisation, scoring) are
exercised by the live sapphire run and its gates.

Added 2026-10-12 (PI ruling D61 (3)): the Benjamini-Hochberg (BH)
adjustment across A-06's four registered factor-T contrasts.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from h6_registered_analyses import (  # noqa: E402
    A08_STATEMENT,
    FACTOR_T_FAMILY,
    apply_bh_to_factor_t,
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


# --------------------------------------------------------------------------- #
# A-06: Benjamini-Hochberg across the four registered factor-T contrasts
# (PI rulings D42 and D61 (3)).
# --------------------------------------------------------------------------- #


def _factor_t(p_by_contrast: dict) -> dict:
    """A minimal ``registered_factor_T`` block carrying only permutation p-values."""
    block: dict = {"text": {}, "image": {}}
    for (modality, thinking), p in p_by_contrast.items():
        block[modality][thinking] = {"delta_bootstrap": {"p_value": p}}
    return block


@pytest.mark.tier1
def test_bh_family_is_the_four_registered_contrasts():
    """The family is text and image at HIGH and MEDIUM thinking, nothing else."""
    assert FACTOR_T_FAMILY == (("text", "high"), ("text", "medium"),
                               ("image", "high"), ("image", "medium"))


@pytest.mark.tier1
def test_bh_adjusts_the_regenerated_p_values():
    """The regenerated A-06 p-values adjust as BH step-up predicts.

    Raw p 0, 0.0019, 0, 0.0002 (text HIGH, text MEDIUM, image HIGH,
    image MEDIUM): ranked 0, 0, 0.0002, 0.0019, the third adjusts to
    0.0002 x 4 / 3 and the largest stays at its own value.
    """
    block = _factor_t({("text", "high"): 0.0, ("text", "medium"): 0.0019,
                       ("image", "high"): 0.0, ("image", "medium"): 0.0002})
    summary = apply_bh_to_factor_t(block)
    assert block["text"]["high"]["p_bh_adjusted"] == 0.0
    assert block["text"]["medium"]["p_bh_adjusted"] == pytest.approx(0.0019)
    assert block["image"]["high"]["p_bh_adjusted"] == 0.0
    assert block["image"]["medium"]["p_bh_adjusted"] == pytest.approx(
        0.0002 * 4 / 3, abs=1e-6)
    for modality, thinking in FACTOR_T_FAMILY:
        row = block[modality][thinking]
        assert "Benjamini-Hochberg" in row["p_adjust_method"]
        assert row["bh_rejects_at_q_0.05"] is True
    assert summary["q"] == 0.05
    assert summary["family"] == ["text HIGH", "text MEDIUM", "image HIGH",
                                 "image MEDIUM"]
    assert summary["p_bh_adjusted"]["image MEDIUM"] == pytest.approx(
        0.0002 * 4 / 3, abs=1e-6)


@pytest.mark.tier1
def test_bh_is_step_up_not_bonferroni():
    """Four p-values evenly spaced up to 0.04 all adjust to 0.04 under BH.

    Bonferroni would give 0.04, 0.08, 0.12, and 0.16, and only the first
    would be rejected at q = 0.05; BH rejects all four.
    """
    block = _factor_t({("text", "high"): 0.01, ("text", "medium"): 0.02,
                       ("image", "high"): 0.03, ("image", "medium"): 0.04})
    apply_bh_to_factor_t(block)
    adjusted = [block[m][t]["p_bh_adjusted"] for m, t in FACTOR_T_FAMILY]
    assert adjusted == pytest.approx([0.04, 0.04, 0.04, 0.04])
    assert all(block[m][t]["bh_rejects_at_q_0.05"] for m, t in FACTOR_T_FAMILY)


@pytest.mark.tier1
def test_bh_refuses_an_incomplete_family():
    """A missing contrast would silently shrink m, so it is an error."""
    block = _factor_t({("text", "high"): 0.0, ("text", "medium"): 0.0019,
                       ("image", "high"): 0.0})
    with pytest.raises(ValueError, match="image/medium"):
        apply_bh_to_factor_t(block)

