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
from scripts.verify_run_conditions import classify_run, verify_all, verify_run

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
    assert rep["verdict"] == "FAIL"  # the two ERRORs (wrong file + scope) fail it
    codes = {d["code"] for d in rep["discrepancies"]}
    assert "eval-detections-mismatch" in codes  # ERROR: scored a different file
    assert "scope-mismatch" in codes  # ERROR: real scope leak, both bounds known
    assert "feature-count-drift" in codes  # WARN: count divergence (now a signal, not a fail)


@pytest.mark.tier1
def test_verify_feature_count_drift_warns_not_fails():
    # The recalibration (verifier as audit instrument): a STALE eval — correct file,
    # correct scope, but n_detections != current geojson feature count — must WARN
    # for adjudication, NOT hard-fail. Real case: the 55maps text-min cleaned-GT eval
    # records 3861 detections; its geojson was refreshed to 3865 after the eval ran.
    registry_obj = load_run_registry()
    facts = load_run_facts()
    index = _g._build_eval_index()
    decomp = {
        "55maps-text-min-generalisation": {
            "proposer_pools": {},
            "verifier_passes": {},
            "conditions": [{
                "label": "verified",
                "architecture": "proposer-verifier",
                "aggregation": "verified",
                "n_passes": 5,
                "detections": "outputs/55maps-text-min-generalisation/verified/verified_detections.geojson",
                "eval_path": "results/55maps-cleaned-gt-evaluation/text-min/evaluation.json",
            }],
        }
    }
    rep = verify_run("55maps-text-min-generalisation", registry_obj, facts, decomp, index)
    codes = {d["code"] for d in rep["discrepancies"]}
    severities = {d["severity"] for d in rep["discrepancies"]}
    assert "feature-count-drift" in codes
    assert "ERROR" not in severities  # a stale eval is a WARN signal, not a failure
    assert rep["verdict"] == "PARTIAL"


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


@pytest.mark.tier1
def test_classify_gs_v2_standard_current():
    # the audit pass: gold-standard-v2's evals are standard-current (full buffers +
    # MCC + matching geojson), so it has no re-scoring work and is not flagged.
    registry_obj = load_run_registry()
    index = _g._build_eval_index()
    c = classify_run("gold-standard-v2", registry_obj, index)
    assert c["n_standard_current"] >= 4
    assert c["n_needs_rescore"] == 0
    assert not c["no_standard_scoring"]


@pytest.mark.tier1
def test_classify_flags_no_standard_scoring():
    # A run with materialised detection geojsons but ZERO standard evals is flagged
    # for re-scoring. retest-phase3c (H9 diversity, scored by a non-standard pipeline)
    # is the example — it sits deep in the backlog and is not yet standardised.
    # (Data-coupled: once retest-phase3c is re-scored, repoint to another backlog run.)
    registry_obj = load_run_registry()
    index = _g._build_eval_index()
    c = classify_run("retest-phase3c", registry_obj, index)
    assert c["n_evals"] == 0
    assert c["n_materialised_geojson"] > 0
    assert c["no_standard_scoring"]
