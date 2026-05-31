"""Tier-1 tests for ``scripts/verify_run_conditions.py`` (the decomposition verifier).

Deterministic checks against committed source-of-truth files:

- gold-standard-v2's authored decomposition verifies clean (PASS);
- a condition mis-pointed at the wrong run's evaluation is caught (FAIL) on all
  three correctness axes — eval↔detections, scope, and feature count.
"""

from __future__ import annotations

import pytest

from scripts.generate_post_run_report import (
    load_run_facts,
    load_run_registry,
)
from scripts.verify_run_conditions import verify_all, verify_run

# the eval index is private to the generator; import via the module to reuse it
from scripts import generate_post_run_report as _g


@pytest.mark.tier1
def test_verify_gs_v2_passes():
    reports = verify_all(only="gold-standard-v2")
    assert len(reports) == 1
    assert reports[0]["verdict"] == "PASS"
    assert reports[0]["discrepancies"] == []


@pytest.mark.tier1
def test_verify_detects_wrong_eval():
    # a gold-standard-v2 condition mis-pointed at an h8-v2 eval: that eval scored a
    # different geojson (consensus_t4), at a different scope (327 vs 487), with a
    # different detection count (258 vs 608). All three correctness checks must fire.
    registry_obj = load_run_registry()
    facts = load_run_facts()
    index = _g._build_eval_index()
    bad_decomp = {
        "gold-standard-v2": {
            "proposer_pools": {"detect_brief-text": "text"},
            "verifier_passes": {},
            "conditions": [{
                "label": "mispointed",
                "architecture": "consensus",
                "aggregation": "consensus",
                "proposer_pool": "detect_brief-text",
                "n_passes": 5,
                "detections": "outputs/gs/gold-standard-v2/consensus/consensus-4of5.geojson",
                "eval_path": "results/h8-v2/with-mcc/canonical/evaluation.json",
            }],
        }
    }
    rep = verify_run("gold-standard-v2", registry_obj, facts, bad_decomp, index)
    assert rep["verdict"] == "FAIL"
    codes = {d["code"] for d in rep["discrepancies"]}
    assert "eval-detections-mismatch" in codes
    assert "scope-mismatch" in codes
    assert "feature-count-mismatch" in codes


@pytest.mark.tier1
def test_verify_flags_unresolved_pool():
    # a condition naming a pool the run does not have (and no source_run) is flagged
    registry_obj = load_run_registry()
    facts = load_run_facts()
    index = _g._build_eval_index()
    decomp = {
        "gold-standard-v2": {
            "proposer_pools": {"detect_brief-text": "text"},
            "verifier_passes": {},
            "conditions": [{
                "label": "consensus-4of5",
                "architecture": "consensus",
                "aggregation": "consensus",
                "proposer_pool": "ghost-pool",  # not a pool of this run
                "n_passes": 5,
                "detections": "outputs/gs/gold-standard-v2/consensus/consensus-4of5.geojson",
            }],
        }
    }
    rep = verify_run("gold-standard-v2", registry_obj, facts, decomp, index)
    assert any(d["code"] == "pool-unresolved" for d in rep["discrepancies"])
