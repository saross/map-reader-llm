"""Tier-1 tests for ``scripts/recompute_c4_claims.py`` (C4 harness).

Synthetic-fixture coverage of the mechanical layer: read resolution
(incl. ``len:``), arithmetic over named operands, percentage rescaling,
per-value method/path overrides, and the triage buckets. No real corpus
I/O beyond tmp fixtures.
"""

from __future__ import annotations

import json

import pytest

import scripts.recompute_c4_claims as rc
from scripts.recompute_c4_claims import process_claim, safe_eval


@pytest.fixture()
def anchored_repo(tmp_path, monkeypatch):
    """Point the harness at a tmp repo with one anchor artefact."""
    anchor = tmp_path / "results" / "eval.json"
    anchor.parent.mkdir(parents=True)
    anchor.write_text(json.dumps({
        "results": {"20m": {"f1": 0.8902, "recall": 0.9203}},
        "features": [1, 2, 3],
        "a": 10.0, "b": 4.0,
    }))
    monkeypatch.setattr(rc, "REPO_ROOT", tmp_path)
    rc._json_cache.clear()
    return tmp_path


def make_claim(**kw) -> dict:
    base = {
        "claim_id": None,
        "source": {"lines": [1, 1], "section": "t"},
        "claim_text": "x",
        "values": [],
        "anchor": None,
        "method": "read",
        "notes": None,
    }
    base.update(kw)
    return base


def val(verbatim, path=None, method=None, quantity="q"):
    return {"quantity": quantity, "value_verbatim": verbatim, "value_parsed": None,
            "unit": None, "kind": "metric", "path": path, "method": method}


@pytest.mark.tier1
def test_read_match_at_quoted_precision(anchored_repo):
    claim = make_claim(values=[val("0.890")],
                       anchor={"file": "results/eval.json",
                               "path": "$.results['20m'].f1"})
    (row,) = process_claim("b", 0, claim)
    assert row["status"] == "MATCH" and row["mode"] == "round"


@pytest.mark.tier1
def test_read_mismatch_and_len_prefix(anchored_repo):
    claim = make_claim(values=[val("0.900"), val("3", path="len:$.features")],
                       anchor={"file": "results/eval.json",
                               "path": "$.results['20m'].f1"})
    rows = process_claim("b", 0, claim)
    assert rows[0]["status"] == "MISMATCH"
    assert rows[1]["status"] == "MATCH" and rows[1]["mode"] == "exact"


@pytest.mark.tier1
def test_percentage_rescaling(anchored_repo):
    claim = make_claim(values=[val("92.0 %", path="$.results['20m'].recall")],
                       anchor={"file": "results/eval.json", "path": None})
    (row,) = process_claim("b", 0, claim)
    assert row["status"] == "MATCH" and row["mode"] == "percent-rescaled"


@pytest.mark.tier1
def test_arithmetic_over_operands(anchored_repo):
    claim = make_claim(
        method="arithmetic",
        values=[val("2.5")],
        anchor={"file": "results/eval.json", "path": None,
                "expression": "a / b",
                "operands": [
                    {"name": "a", "file": "results/eval.json", "path": "$.a"},
                    {"name": "b", "file": "results/eval.json", "path": "$.b"},
                ]})
    (row,) = process_claim("b", 0, claim)
    assert row["status"] == "MATCH" and row["mode"] == "exact"


@pytest.mark.tier1
def test_unresolved_and_skipped_buckets(anchored_repo):
    bad_path = make_claim(values=[val("1")],
                          anchor={"file": "results/eval.json", "path": "$.absent"})
    (row,) = process_claim("b", 0, bad_path)
    assert row["status"] == "UNRESOLVED" and "absent" in row["reason"]

    historical = make_claim(method="historical", values=[val("0.5")])
    (row,) = process_claim("b", 0, historical)
    assert row["status"] == "SKIPPED"

    # Per-value method override: one live read, one historical, same span.
    mixed = make_claim(values=[val("0.890"), val("0.850", method="historical")],
                       anchor={"file": "results/eval.json",
                               "path": "$.results['20m'].f1"})
    rows = process_claim("b", 0, mixed)
    assert rows[0]["status"] == "MATCH"
    assert rows[1]["status"] == "SKIPPED"


@pytest.mark.tier1
def test_safe_eval_rejects_hostile_expressions():
    with pytest.raises(ValueError):
        safe_eval("__import__('os').system('x')", {})
    with pytest.raises(ValueError):
        safe_eval("a + b", {"a": 1.0})
    with pytest.raises(ValueError):
        safe_eval("", {})  # malformed expression -> ValueError, not SyntaxError
    assert safe_eval("100 * a / b", {"a": 1.0, "b": 8.0}) == pytest.approx(12.5)
