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
from scripts.verify_run_conditions import (
    _geojson_coord_frame,
    classify_run,
    verify_all,
    verify_condition,
    verify_run,
)

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
    # NB (data-coupled): the cleaned-GT eval was archived in Session 105 (commit
    # da2cf355) → results/55maps-cleaned-gt-evaluation/ moved to
    # archive/55maps-superseded-gt-evals/; eval_path repointed there 2026-06-08 so
    # the drift case (3861 vs 3865) still holds. (These verifier tests are coupled
    # to mutable repo state and need repointing when data moves — see the note in
    # planning/deferred-extensions.md on making them fixture-based.)
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
                "eval_path": "archive/55maps-superseded-gt-evals/55maps-cleaned-gt-evaluation/text-min/evaluation.json",
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
def test_coord_frame_distinguishes_utm_no_crs_from_declared():
    # the silent-misread hazard: projected metres with NO crs member is flagged;
    # WGS84, and projected-WITH-explicit-crs, are both "ok".
    archived_utm = ("archive/data-repairs/consensus-384-UNINTENDED-T1.0-missing-crs/"
                    "voting/consensus_t1.geojson")
    assert _geojson_coord_frame(archived_utm) == "utm-no-crs"
    assert _geojson_coord_frame(
        "outputs/h11/proposer-verifier-384/verified-brief-text.geojson") == "ok"  # repaired -> WGS84
    # UTM coords but a declared EPSG::32635 crs member -> the scorer reprojects it; not a hazard
    assert _geojson_coord_frame(
        "outputs/h11/e47-propose-brief/text-baseline/"
        "detections-propose_brief-text-3-flash-2026-04-08.geojson") == "ok"


@pytest.mark.tier1
def test_verify_flags_crs_missing_utm():
    # a condition pointing at a UTM-no-crs geojson is flagged (the user-requested flag)
    discs = verify_condition(
        {"label": "utm-test",
         "detections": ("archive/data-repairs/consensus-384-UNINTENDED-T1.0-missing-crs/"
                        "voting/consensus_t1.geojson")},
        None, {}, "outputs/h11/consensus-384-UNINTENDED-T1.0", _g._build_eval_index())
    assert "crs-missing-utm" in {d["code"] for d in discs}


@pytest.mark.tier1
def test_verify_flags_f1_all_zero():
    # an eval that is F1=0 at every buffer is flagged as a scoring red flag. The
    # verified-checklist-image-v2 condition is a real all-zero (only 2 detections,
    # both >1 km from any mound) — correctly surfaced for human review.
    discs = verify_condition(
        {"label": "zero-test",
         "eval_path": ("results/rescore-2026-05-31/proposer-verifier-384/"
                       "verified-checklist-image-v2/evaluation.json"),
         "detections": "outputs/h11/proposer-verifier-384/verified-checklist-image-v2.geojson"},
        "inputs/vectors/bounds/384/full_evaluation_bounds.geojson", {},
        "outputs/h11/proposer-verifier-384", _g._build_eval_index())
    assert "f1-all-zero" in {d["code"] for d in discs}


@pytest.mark.tier1
def test_classify_flags_no_standard_scoring(tmp_path):
    # A run with materialised detection geojsons but ZERO standard evals is flagged
    # `no_standard_scoring` (results scored only by a non-standard leaderboard/sweep,
    # or not at all → needs re-scoring). Built from a synthetic run so it does NOT
    # couple to a live decomposition-backlog run: the real backlog was cleared once
    # all 28 runs were decomposed and re-scored (Session 108). This previously
    # pointed at retest-phase3c, then pv-diag-256 — both since standardised, which
    # is exactly why a live example no longer exists. The synthetic run also pins
    # the materialised-count rule: aggregation/verified geojsons count, but raw
    # proposer `run_N/` passes and `crops/` do not.
    run_dir = tmp_path / "synthetic-run"
    run_dir.mkdir()
    fc = '{"type": "FeatureCollection", "features": []}'
    (run_dir / "consensus_t4.geojson").write_text(fc)  # a materialised aggregation output
    (run_dir / "run_1").mkdir()
    (run_dir / "run_1" / "raw.geojson").write_text(fc)  # raw proposer pass — excluded
    (run_dir / "crops").mkdir()
    (run_dir / "crops" / "candidate.geojson").write_text(fc)  # crop output — excluded
    registry_obj = {"registry": [{"run_id": "synthetic-run", "directory_path": str(run_dir)}]}
    c = classify_run("synthetic-run", registry_obj, index={})
    assert c["n_evals"] == 0
    assert c["n_materialised_geojson"] == 1  # only consensus_t4.geojson; run_N/ + crops/ excluded
    assert c["no_standard_scoring"]


@pytest.mark.tier1
def test_classify_all_skips_planned_runs_on_evidence_not_label(tmp_path, monkeypatch):
    """AUDIT M10/M-4: classify_all had no test at all, and the label is not evidence.

    A genuinely planned run (no directory) yields a row of zeros indistinguishable
    from an executed run whose evaluations are missing, so it is skipped. But a run
    left MARKED planned after it actually ran must still be classified — the old
    zero-row was informative there, and skipping on the label alone would convert
    that signal into silence.
    """
    import scripts.verify_run_conditions as v

    monkeypatch.setattr(v.g, "REPO_ROOT", tmp_path)
    (tmp_path / "outputs" / "has-run").mkdir(parents=True)
    entries = [
        {"run_id": "active-run", "directory_path": "outputs/active-run"},
        {"run_id": "truly-planned", "directory_path": "outputs/truly-planned",
         "status": "planned", "planned_at": "2026-07-28T00:00:00Z"},
        {"run_id": "has-run", "directory_path": "outputs/has-run",
         "status": "planned", "planned_at": "2026-07-28T00:00:00Z"},
    ]
    monkeypatch.setattr(v.g, "load_run_registry", lambda: {"registry": entries})
    monkeypatch.setattr(v.g, "_build_eval_index", lambda: {})
    monkeypatch.setattr(v, "classify_run",
                        lambda rid, reg, idx: {"run_id": rid, "verdict": "PASS",
                                               "discrepancies": []})

    ids = [r["run_id"] for r in v.classify_all()]
    assert "active-run" in ids
    assert "truly-planned" not in ids   # no directory -> genuinely not executed
    assert "has-run" in ids             # mis-marked but materialised -> still visible
