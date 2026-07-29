"""Tier-1 tests for ``scripts/validate_commitments.py`` (the commitment ledger validator).

Integration tests against the committed ledger (deterministic, no API), plus
failure-mode tests proving the load-bearing checks actually fail: a paraphrased
"quote" must be caught by the verbatim check, and a bad waiver by the errata
resolution check.
"""

from __future__ import annotations

import copy
import json

import pytest

from scripts.validate_commitments import (
    DEFAULT_LEDGER,
    id_errors,
    load_json,
    verbatim_errors,
    waiver_errors,
)


@pytest.fixture(scope="module")
def ledger() -> dict:
    return load_json(DEFAULT_LEDGER)


@pytest.mark.tier1
def test_committed_ledger_is_verbatim_clean(ledger):
    """Every statement in the committed ledger appears verbatim at its locator."""
    assert verbatim_errors(ledger) == []


@pytest.mark.tier1
def test_committed_ledger_waivers_resolve(ledger):
    """Every waiver E-number resolves against the errata register."""
    assert waiver_errors(ledger) == []


@pytest.mark.tier1
def test_committed_ledger_ids_unique(ledger):
    assert id_errors(ledger) == []


@pytest.mark.tier1
def test_paraphrase_fails_verbatim_check(ledger):
    """A paraphrase logged as a quote is itself a fabrication class — must FAIL."""
    tampered = copy.deepcopy(ledger)
    tampered["commitments"][0]["statement"] = (
        "A plausible paraphrase that does not appear in the lodged text."
    )
    errors = verbatim_errors(tampered)
    assert len(errors) == 1
    assert "not found verbatim" in errors[0]


@pytest.mark.tier1
def test_unknown_waiver_fails(ledger):
    """A waiver citing a nonexistent erratum must fail resolution."""
    tampered = copy.deepcopy(ledger)
    tampered["commitments"][0]["waiver"] = "E999"
    errors = waiver_errors(tampered)
    assert len(errors) == 1
    assert "E999" in errors[0]


@pytest.mark.tier1
def test_status_counts_match_gate1_record(ledger):
    """The v1.2 status distribution recorded at GATE 1 (402/89/211)."""
    counts: dict[str, int] = {}
    for cmt in ledger["commitments"]:
        counts[cmt["status"]] = counts.get(cmt["status"], 0) + 1
    assert counts == {"discharged": 402, "waived": 89, "open": 211}
    assert len(ledger["commitments"]) == 702


@pytest.mark.tier1
def test_trigger_rows_carry_five_elements(ledger):
    """Every kind=trigger row carries a complete five-element block (the H7 rule)."""
    required = {"statistic", "comparison_scope", "uncertainty_criterion",
                "evaluation_moment", "evaluation_corpus"}
    for cmt in ledger["commitments"]:
        if cmt["kind"] == "trigger":
            assert cmt["trigger"] is not None, cmt["commitment_id"]
            assert required <= set(cmt["trigger"]), cmt["commitment_id"]
            assert all(len(str(v)) >= 2 for v in cmt["trigger"].values()), \
                cmt["commitment_id"]


@pytest.mark.tier1
def test_c2_ledger_parses_and_counts(tmp_path):
    """The generated C2 ledger is valid JSONL with the recorded verdict split."""
    path = DEFAULT_LEDGER.parent.parent / "reports" / "verification" / \
        "ledgers" / "c2-execution.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    assert len(rows) == 915
    verdicts: dict[str, int] = {}
    for row in rows:
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
    assert verdicts == {"VERIFIED": 691, "FLAGGED": 224}
