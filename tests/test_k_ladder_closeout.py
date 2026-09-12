#!/usr/bin/env python3
"""
Tier-1 tests for the K-ladder closeout job
==========================================

Covers the decision-bearing logic of the closeout's four new scripts, plus the
two register-side changes it made, choosing in every case the part where a
silent mistake would corrupt an API-spend decision, a published caveat, or a
registered claim:

* ``run_k_ladder_tier_e`` — the three-rung worklist, the PI's approved candidate
  counts and the 2 % STOP either side of them, the budget constants, and the
  condition labels;
* ``k_ladder_tension_analyses`` — the Benjamini-Hochberg adjustment (the step
  every "fraction of draws significant" figure rests on) and the deployment
  ladder map's completeness;
* ``author_k_ladder_analysis_row`` — that the row is authored UNSIGNED, carries
  the hypothesis refs the register's other ladder rows carry, and that its
  ``conditions_compared`` is derived rather than hard-coded;
* ``final_board_sweeps`` — that the fourth cell gains an N = 5 rung while the
  two five-pass arms keep exactly the rungs they had (the asymmetry item 2
  fixed, pinned so it cannot drift back);
* **the register**, live: that the five relabelled conditions are N = 5, carry
  both E72 and E85, and that no ``…of30`` label survives;
* **the caveat channel**, live: that the manifest schema declares ``caveat`` and
  the generator emits it, which is E72 remediation item 4.

No network, no API. The live-register checks read two committed JSON files.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import author_k_ladder_analysis_row as author  # noqa: E402
from scripts import k_ladder_tension_analyses as tension  # noqa: E402
from scripts import run_k_ladder_tier_e as tier_e  # noqa: E402

pytestmark = pytest.mark.tier1


# --- tier E: the worklist and the spend gate --------------------------------


def test_tier_e_has_exactly_three_rungs_at_k_1_3_5():
    """The approval is for three rungs; a fourth would be unapproved spend."""
    rungs = tier_e.rungs()
    assert [r["n_passes"] for r in rungs] == [1, 3, 5]
    assert {r["tier"] for r in rungs} == {"E"}
    assert [r["row"] for r in rungs] == [1, 2, 3]


def test_tier_e_pass_lists_are_first_n_prefixes():
    """A rung's pass list must be 1..N, the preregistered first-N rule."""
    for rung in tier_e.rungs():
        expected = ",".join(str(i) for i in range(1, rung["n_passes"] + 1))
        assert rung["pass_list"] == expected


def test_tier_e_expected_counts_are_the_pi_approved_figures():
    """These three numbers are the approval; a drift here is unapproved spend."""
    assert tier_e.EXPECTED_CANDIDATES == {1: 1826, 3: 2481, 5: 2932}
    assert sum(tier_e.EXPECTED_CANDIDATES.values()) == 7239


def test_tier_e_budget_constants_match_the_approval():
    """US$5.02 approved, US$7.00 hard stop, at the audited per-candidate rate."""
    assert tier_e.APPROVED_USD == 5.02
    assert tier_e.HARD_STOP_USD == 7.00
    assert tier_e.USD_PER_CANDIDATE == 0.000693
    # The approval and the rate must agree on the total, or one of them is stale.
    estimate = sum(tier_e.EXPECTED_CANDIDATES.values()) * tier_e.USD_PER_CANDIDATE
    assert estimate == pytest.approx(tier_e.APPROVED_USD, abs=0.01)


def test_tier_e_hard_stop_is_above_the_approval():
    """A hard stop at or below the approval would abort a compliant run."""
    assert tier_e.HARD_STOP_USD > tier_e.APPROVED_USD


def test_tier_e_verifier_config_is_the_carried_one(tmp_path):
    """Ruling R1 fixes the verifier; the driver must not name another config."""
    assert tier_e.VERIFIER_CONFIG.name == "verify_adversarial-text.json"
    source = (PROJECT_ROOT / "scripts" / "run_k_ladder_tier_e.py").read_text()
    # No CLI override of the three fields the config owns.
    for flag in ("--model", "--temperature", "--thinking-level"):
        assert f'"{flag}"' not in source, f"{flag} must not be passed"


def test_tier_e_carried_probability_matches_the_committed_grid_cells():
    """0.15 is the committed grid cells' threshold; another value breaks the ladder."""
    assert tier_e.CARRIED_PROB == 0.15


def test_tier_e_condition_labels_follow_the_grid_convention():
    """Labels must sit beside g384-ov192-k10-verified-p0.15-k10."""
    for rung in tier_e.rungs():
        labels = tier_e.condition_labels(rung)
        k = rung["n_passes"]
        assert labels["opmax"] == f"g384-ov192-k{k}-verified-opmax"
        assert labels["carried"] == f"g384-ov192-k{k}-verified-p0.15-k{k}"


def test_tier_e_records_the_k10_construction_asymmetry():
    """The asymmetry must stay in the artefact, not only in a report."""
    k10 = tier_e.COMMITTED_K10
    assert k10["candidates"] == 3319
    assert k10["merge_passes_equivalent"] == 3591
    assert k10["merge_passes_on_carrier"] == 3325
    # The filtered figure must be the one closest to the committed count.
    assert abs(k10["merge_passes_on_carrier"] - k10["candidates"]) < abs(
        k10["merge_passes_equivalent"] - k10["candidates"]
    )


# --- the tension analyses ---------------------------------------------------


def test_bh_adjustment_is_monotone_and_bounded():
    """Every 'fraction of draws significant' figure rests on this step."""
    raw = [0.001, 0.02, 0.04, 0.3, 0.5, 0.9]
    adjusted = tension.bh_adjust(raw)
    assert all(0.0 <= p <= 1.0 for p in adjusted)
    # BH never lowers a p-value, and never breaks the rank order.
    assert all(a >= r - 1e-12 for a, r in zip(adjusted, raw))
    assert adjusted == sorted(adjusted)


def test_bh_adjustment_matches_the_textbook_step_up():
    """Hand-computed against the step-up definition, n = 4."""
    raw = [0.01, 0.02, 0.03, 0.04]
    # p_i * n / i, then enforced monotone from the largest rank down:
    # 0.04*4/4=0.04; 0.03*4/3=0.04; 0.02*4/2=0.04; 0.01*4/1=0.04
    assert tension.bh_adjust(raw) == pytest.approx([0.04, 0.04, 0.04, 0.04])


def test_bh_adjustment_preserves_input_order():
    """The adjusted list is returned in the INPUT order, not sorted."""
    raw = [0.9, 0.001, 0.5]
    adjusted = tension.bh_adjust(raw)
    assert adjusted[1] < adjusted[2] < adjusted[0]


def test_subsample_size_is_the_gold_standards_tile_count():
    """The whole point is to score at 487 tiles; another size answers nothing."""
    assert tension.GS_N_TILES == 487


def test_both_deployment_minimal_ladders_carry_four_rungs():
    """A missing rung would silently shrink the round-robin family."""
    assert set(tension.DEPLOYMENT_LADDERS) == {
        "55map-stride-a-r2", "55map-stride-b-r2",
    }
    for spec in tension.DEPLOYMENT_LADDERS.values():
        assert sorted(spec["cells"]) == [1, 3, 5, 10]
        assert len(set(spec["cells"].values())) == 4


# --- the analysis row ------------------------------------------------------


def test_analysis_row_is_authored_unsigned():
    """Only the PI signs. An authored signature would be a forged one."""
    assert author.ROW["manually_verified_at"] is None
    assert "UNSIGNED" in author.ROW["_signature_note"]


def test_analysis_row_carries_the_ladder_hypothesis_refs():
    """H3 is the pass-count factor, H13 the tile geometry."""
    assert author.ROW["hypothesis_refs"] == ["H3", "H13"]
    assert author.ROW["preregistered"] == "post-hoc"
    assert author.ROW["type"] == "comparison"


def test_analysis_row_conditions_compared_is_not_hard_coded():
    """It must be derived from the inventories, or it will drift from them."""
    assert author.ROW["conditions_compared"] == []


def test_analysis_row_declares_the_relabel_erratum():
    """E85 relabelled five conditions; E56 is the in-sample-optimum class."""
    assert set(author.ROW["deviations"]) == {"E56", "E85"}


def test_analysis_row_outcome_names_the_instrument_ruling():
    """The PI's ruling is the row's warrant and must be stated in it."""
    outcome = author.ROW["outcome"]
    assert "CROSS-CHECK" in outcome
    assert "tile-swap" in outcome
    assert "sign-swap" in outcome


def test_analysis_row_outcome_states_the_withheld_cells():
    """Three cells' tile-MCC is withheld; a reader must not infer a number."""
    outcome = author.ROW["outcome"]
    assert "WITHHELD" in outcome
    for cell in (
        "g37-text-k1-verified-opmax",
        "g37-text-k1-verified-carried-p0.10-k1",
        "g37-text-k3-verified-opmax",
    ):
        assert cell in outcome


# --- the fourth cell's rung loop -------------------------------------------


def test_fourth_cell_gains_n5_and_the_arms_do_not():
    """Item 2's fix, pinned: rungs derive from k_max, so arms are unchanged."""
    source = (PROJECT_ROOT / "scripts" / "final_board_sweeps.py").read_text()
    assert "for n in (n for n in (1, 3, 5) if n < k_max):" in source
    # The literal the defect consisted of must be gone.
    assert "for n in (1, 3):" not in source

    # And the rule itself, evaluated: five-pass arms give (1, 3); the fourth
    # cell's ten passes give (1, 3, 5).
    def rungs_for(k_max: int) -> list[int]:
        return [n for n in (1, 3, 5) if n < k_max]

    assert rungs_for(5) == [1, 3]
    assert rungs_for(10) == [1, 3, 5]


# --- the register, live ----------------------------------------------------


@pytest.fixture(scope="module")
def register() -> dict:
    """The committed condition register."""
    path = PROJECT_ROOT / "results" / "run-conditions.json"
    return json.loads(path.read_text())


def test_the_five_relabelled_conditions_are_n5(register):
    """Erratum E85: the cell is a 5-pass union, whatever its old label said."""
    conditions = register["decomposition"]["consensus-384-t1-0"]["conditions"]
    relabelled = [
        c for c in conditions
        if re.fullmatch(r"consensus-\dof5", c.get("label", ""))
    ]
    assert len(relabelled) == 5
    for cond in relabelled:
        assert cond["n_passes"] == 5, cond["label"]
        # The vote threshold is out of 5, so it cannot exceed 5.
        assert 1 <= cond["vote_threshold"] <= 5


def test_no_of30_label_survives_the_relabel(register):
    """A surviving …of30 label would contradict the erratum."""
    conditions = register["decomposition"]["consensus-384-t1-0"]["conditions"]
    assert not [
        c for c in conditions
        if re.fullmatch(r"consensus-\dof30", c.get("label", ""))
    ]


def test_the_five_carry_both_errata(register):
    """E72 fences the coverage confound; E85 the pass count. Both must travel."""
    conditions = register["decomposition"]["consensus-384-t1-0"]["conditions"]
    relabelled = [
        c for c in conditions
        if re.fullmatch(r"consensus-\dof5", c.get("label", ""))
    ]
    for cond in relabelled:
        note = cond.get("_note") or ""
        assert "E72 COVERAGE CONFOUND" in note, cond["label"]
        assert "ERRATUM E85" in note, cond["label"]


def test_erratum_e85_exists_and_cross_references_e72():
    """The erratum is the record; a note without it is unanchored."""
    errata = (
        PROJECT_ROOT / "docs" / "methodology" / "preregistration"
        / "protocol-errata.md"
    ).read_text()
    assert "### E85:" in errata
    e85 = errata.split("### E85:", 1)[1]
    assert "E72" in e85
    assert "5-pass union" in e85 or "N = 5" in e85


# --- the caveat channel (E72 remediation item 4) ---------------------------


def test_conditions_manifest_schema_declares_the_caveat_field():
    """additionalProperties is false, so an undeclared field fails validation."""
    schema = json.loads(
        (
            PROJECT_ROOT / "docs" / "manifest-schemas"
            / "conditions-manifest.schema.json"
        ).read_text()
    )
    condition = schema["$defs"]["condition"]
    assert condition["additionalProperties"] is False
    assert "caveat" in condition["properties"]
    # Nullable and optional: most conditions carry no caveat.
    assert "null" in condition["properties"]["caveat"]["type"]
    assert "caveat" not in condition["required"]


def test_the_generator_emits_the_register_caveat():
    """Without this the manifest publishes figures with no warning attached."""
    source = (
        PROJECT_ROOT / "scripts" / "generate_post_run_report.py"
    ).read_text()
    assert '"caveat": spec.get("_note"),' in source


def test_the_supplement_carries_the_register_caveat_into_notes():
    """The uplift CSV's notes cell was empty for a cell marked 'do not cite'."""
    source = (
        PROJECT_ROOT / "scripts" / "build_uplift_supplement.py"
    ).read_text()
    assert 'register_caveat = (spec.get("_note") or "").strip()' in source
    assert 'notes.append(f"register caveat: {register_caveat}")' in source
