"""Tier-1 tests for ``scripts/validate_commitments.py`` (the commitment ledger validator).

Integration tests against the committed ledger (deterministic, no API), plus
failure-mode tests proving the load-bearing checks actually fail: a paraphrased
"quote" must be caught by the verbatim check, and a bad waiver by the errata
resolution check.

The GATE 1 state tests were redesigned in Session 124 (PI-approved) after
the 2026-07-30 recovery close-out legitimately advanced the ledgers: the
GATE 1 record is pinned as immutable history (constants + a frozen
fixture), and the CURRENT state is checked against append-only /
monotonicity invariants instead of frozen totals — so legitimate progress
passes while a rewritten ledger row or a reverting commitment status
fails loudly.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from scripts.validate_commitments import (
    DEFAULT_LEDGER,
    id_errors,
    load_json,
    verbatim_errors,
    waiver_errors,
)

# --- The GATE 1 (2026-07-29) record — immutable history, commit 4729f99dc.
# These constants never change; ledger growth is checked against them via
# invariants, not equality.
GATE1_STATUS_COUNTS = {"discharged": 402, "waived": 89, "open": 211}
GATE1_C2_ROWS = 915
GATE1_C2_VERDICTS = {"VERIFIED": 691, "FLAGGED": 224}
GATE1_C2_PREFIX_SHA256 = \
    "8cdce78aad1d1304726dcdbed23ee3f14bae5118942a550da2367c991d652532"
GATE1_STATUS_FIXTURE = (Path(__file__).parent / "fixtures"
                        / "gate1-commitment-statuses.json")
C2_VERDICT_VOCABULARY = {"VERIFIED", "FLAGGED"}


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
def test_commitment_statuses_monotone_since_gate1(ledger):
    """Statuses only advance from the frozen GATE 1 snapshot.

    The fixture is the per-commitment GATE 1 record (immutable history;
    its counts must reproduce the gate package's 402/89/211). Against
    it, the current ledger must conserve the commitment set (702, no
    additions or removals) and move each status only along
    open → discharged/waived — a discharged or waived commitment
    silently reverting fails loudly.
    """
    snapshot = json.loads(GATE1_STATUS_FIXTURE.read_text(encoding="utf-8"))
    gate1 = snapshot["statuses"]
    assert Counter(gate1.values()) == GATE1_STATUS_COUNTS  # the record itself
    current = {c["commitment_id"]: c["status"] for c in ledger["commitments"]}
    assert set(current) == set(gate1)  # conservation: no adds, no removals
    assert len(current) == 702
    allowed = {"open": {"open", "discharged", "waived"},
               "discharged": {"discharged"},
               "waived": {"waived"}}
    violations = [(cid, gate1[cid], current[cid]) for cid in gate1
                  if current[cid] not in allowed[gate1[cid]]]
    assert violations == []


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
def test_c2_ledger_append_only_since_gate1():
    """The C2 execution ledger only ever grows past its GATE 1 prefix.

    The first 915 lines must be byte-identical to the GATE 1-era file
    (sha256-pinned at commit 4729f99dc) with the recorded verdict split;
    any later rows must parse and use the known verdict vocabulary. An
    edited or reordered historical row breaks the prefix hash; growth
    (e.g. the 2026-07-30 close-out's five discharge rows) passes.
    """
    path = DEFAULT_LEDGER.parent.parent / "reports" / "verification" / \
        "ledgers" / "c2-execution.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= GATE1_C2_ROWS
    prefix = "\n".join(lines[:GATE1_C2_ROWS]) + "\n"
    assert hashlib.sha256(prefix.encode("utf-8")).hexdigest() == \
        GATE1_C2_PREFIX_SHA256
    rows = [json.loads(line) for line in lines if line]
    assert Counter(r["verdict"] for r in rows[:GATE1_C2_ROWS]) == \
        GATE1_C2_VERDICTS
    for row in rows[GATE1_C2_ROWS:]:  # appended rows: well-formed
        assert row["verdict"] in C2_VERDICT_VOCABULARY
        assert row["claim_id"] and row["class"] == "C2"
