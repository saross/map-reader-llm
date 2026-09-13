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


@pytest.mark.tier1
def test_directory_detections_match_when_every_scored_file_lies_under_it():
    """An aggregated multi-pass cell registers its pass DIRECTORY; the evaluation
    records the per-pass files it scored. The row matches when all of them lie
    under that directory (the h13 overlap arms), and mismatches otherwise
    (Session 149-c, register-verifier debt ruling 3c)."""
    from scripts.verify_run_conditions import verify_condition
    index = _g._build_eval_index()
    base = {"label": "arm-a", "architecture": "consensus", "aggregation": "consensus",
            "eval_path": "results/h13-overlap-2026-08-18/common/armA/evaluation.json"}
    ok = verify_condition({**base, "detections": "outputs/h13/scoring/common/armA"},
                          None, {}, "results/h13-overlap-2026-08-18", index)
    assert not [d for d in ok if "eval-detections-mismatch" in str(d)], ok
    bad = verify_condition({**base, "detections": "outputs/h13/scoring/native/armA"},
                           None, {}, "results/h13-overlap-2026-08-18", index)
    assert [d for d in bad if "eval-detections-mismatch" in str(d)], bad


# ------------------------------------------------ Session 150 (ruling 3a) ---
# The E82 replay scored nine legacy rows against VINTAGE-FROZEN detections
# (D40); the E71 recovery then rewrote the files. A row stamped
# ``input_vintage`` is checked against the commit it names, not the tree.

_PINNED_SPEC = {
    "label": "pro-image-high-t0-single-pass-run_1",
    "architecture": "single-pass",
    "aggregation": "none",
    "proposer_pool": "pro-image-high-t0",
    "n_passes": 1,
    "eval_path": ("results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/"
                  "run_1/evaluation.json"),
    "detections": ("outputs/h11/n1-outstanding-384/pro-image-high-t0/run_1/"
                   "detections_pro-image-high-t0_run01.geojson"),
}
_SCOPE = "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"


def _n1_pools() -> dict:
    return _g.load_run_conditions()["n1-outstanding-384"]["proposer_pools"]


@pytest.mark.tier1
def test_pinned_vintage_row_is_disclosed_not_failed():
    """A correctly pinned row: one WARN naming the vintage, no wrong-source ERROR."""
    spec = dict(_PINNED_SPEC, input_vintage={
        "detections_commit": "c3852ebad",
        "superseded_measurement": "pro-image-high-t0-single-pass-run_1-post-e71",
        "erratum": "E71"})
    discs = verify_condition(spec, _SCOPE, _n1_pools(), "outputs/h11/n1-outstanding-384",
                             _g._build_eval_index())
    codes = {d["code"] for d in discs}
    assert "pinned-vintage" in codes
    assert not codes & {"eval-detections-mismatch", "scope-mismatch", "feature-count-drift"}
    assert not [d for d in discs if d["severity"] == "ERROR"], discs


@pytest.mark.tier1
def test_pinned_vintage_wrong_commit_is_an_error():
    """A pin the evaluation does not record cannot be checked — that is an ERROR."""
    spec = dict(_PINNED_SPEC, input_vintage={"detections_commit": "deadbeef0"})
    discs = verify_condition(spec, _SCOPE, _n1_pools(), "outputs/h11/n1-outstanding-384",
                             _g._build_eval_index())
    assert [d for d in discs if d["code"] == "pinned-vintage-mismatch"
            and d["severity"] == "ERROR"], discs


@pytest.mark.tier1
def test_unpinned_frozen_replay_still_fails():
    """Regression guard: without the stamp, the frozen-copy eval is still wrong-source."""
    discs = verify_condition(dict(_PINNED_SPEC), _SCOPE, _n1_pools(),
                             "outputs/h11/n1-outstanding-384", _g._build_eval_index())
    codes = {d["code"] for d in discs}
    assert {"eval-detections-mismatch", "scope-mismatch"} <= codes


@pytest.mark.tier1
def test_malformed_vintage_stamp_surfaces():
    """A stamp without detections_commit disables nothing and says so."""
    spec = dict(_PINNED_SPEC, input_vintage={"pinned": "pre-e71"})
    discs = verify_condition(spec, _SCOPE, _n1_pools(), "outputs/h11/n1-outstanding-384",
                             _g._build_eval_index())
    codes = {d["code"] for d in discs}
    assert "input-vintage-malformed" in codes
    assert "eval-detections-mismatch" in codes


# --------------------------------------------------------------------------- #
# The two instrument corrections of 2026-09-13 (Session 153, Batch 1 item 2)
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_directory_valued_detections_is_not_geojson_missing():
    """An aggregated multi-pass cell must NOT be reported as missing detections.

    ``detections`` naming a DIRECTORY is the aggregated-cell shape: the evaluation
    was pointed at the directory and ``summary.n_detections`` is the post-aggregation
    count, so there is no single file whose features could be counted. Before the
    correction this raised ``geojson-missing`` — "detections missing/unreadable" —
    about 79 directories that were all present, which made eleven runs PARTIAL on an
    instrument defect. Real case: retest-phase2b's T=0.0 image cell.
    """
    discs = verify_condition(
        {"label": "image-t0.0",
         "architecture": "single-pass",
         "aggregation": "none",
         "n_passes": 3,
         "eval_path": ("results/paper-eval/phase2/512px-14buf-mcc/p2b-image-t-0-0/"
                       "evaluation.json"),
         "detections": "outputs/retest/phase2b/track1-image/T0.0"},
        None, {}, "outputs/retest/phase2b", _g._build_eval_index())
    codes = {d["code"] for d in discs}
    assert "geojson-missing" not in codes, discs
    assert "detections-dir-empty" not in codes, discs


@pytest.mark.tier1
def test_absent_detections_still_reported_missing():
    """Regression guard for the other half of the branch: a genuinely absent path
    must still raise ``geojson-missing``. The correction narrowed the WARN to real
    absence; it must not have removed it."""
    discs = verify_condition(
        {"label": "ghost",
         "architecture": "single-pass",
         "aggregation": "none",
         "n_passes": 1,
         "eval_path": ("results/paper-eval/phase2/512px-14buf-mcc/p2b-image-t-0-0/"
                       "evaluation.json"),
         "detections": "outputs/retest/phase2b/track1-image/T0.0/does-not-exist.geojson"},
        None, {}, "outputs/retest/phase2b", _g._build_eval_index())
    assert "geojson-missing" in {d["code"] for d in discs}, discs


@pytest.mark.tier1
def test_empty_detections_directory_is_flagged(tmp_path, monkeypatch):
    """An aggregated cell whose directory holds no geojson HAS lost its inputs —
    the signal the directory branch keeps."""
    import json as _json
    monkeypatch.setattr(_g, "REPO_ROOT", tmp_path)
    (tmp_path / "empty-cell").mkdir()
    # a minimal eval that names the directory as its input, as the real ones do
    (tmp_path / "eval.json").write_text(_json.dumps({
        "_metadata": {"input_files": {"detections": ["empty-cell"]}},
        "summary": {"n_detections": None, "buffers": [{"buffer_metres": 20, "f1": 0.5}]},
    }), encoding="utf-8")
    discs = verify_condition(
        {"label": "empty", "architecture": "single-pass", "aggregation": "none",
         "n_passes": 1, "detections": "empty-cell", "eval_path": "eval.json"},
        None, {}, "outputs/synthetic", {})
    assert "detections-dir-empty" in {d["code"] for d in discs}, discs


@pytest.mark.tier1
def test_materialised_pool_path_is_not_pool_dir_not_found():
    """A pool whose registered ``path`` resolves to a FILE is a materialised pool.

    flash35-pv-2x2's ``f3-min-text-1of10`` is the cross-run pv-diag-384 text-n10
    minimal lineage merged into one committed geojson, so pass resolution has nothing
    to count — but the artefact is present, which "not found" denied.
    """
    discs = verify_condition(
        {"label": "f3prop-f35vf-6of10",
         "architecture": "proposer-verifier",
         "aggregation": "verified",
         "proposer_pool": "f3-min-text-1of10",
         "n_passes": 10,
         "source_run": "pv-diag-384"},
        None,
        {"f3-min-text-1of10": {"modality": "text",
                               "path": "consensus/f3-min-text-1of10-with-passes.geojson"}},
        "outputs/flash35-pv-2x2", _g._build_eval_index())
    assert "pool-dir-not-found" not in {d["code"] for d in discs}, discs


@pytest.mark.tier1
def test_absent_pool_path_still_reported_not_found():
    """Regression guard: a pool path that is neither a directory nor a file still
    raises ``pool-dir-not-found``."""
    discs = verify_condition(
        {"label": "ghost-pool",
         "architecture": "consensus",
         "aggregation": "consensus",
         "proposer_pool": "nowhere",
         "n_passes": 5},
        None, {"nowhere": {"modality": "text", "path": "proposer/nowhere"}},
        "outputs/flash35-pv-2x2", _g._build_eval_index())
    assert "pool-dir-not-found" in {d["code"] for d in discs}, discs


@pytest.mark.tier1
def test_partial_runs_are_exactly_the_three_by_design_disclosures():
    """After the 2026-09-13 annotation pass, the only PARTIAL runs are the three
    whose WARNs are by-design disclosures the project has already settled:

    * ``55maps-text-min-n10-uplift`` — ``n-passes-over`` on a MIXED-PROVENANCE pool
      (passes 1-5 from the deployment run, 6-10 from this one), which the run's own
      ``_note`` calls "the honest by-design signal, per the S106 settled position";
    * ``e47-propose-brief`` and ``n1-outstanding-384`` — ``pinned-vintage``, the
      ruling-3a (PI, 2026-09-07) disclosure that a row's eval scored a
      vintage-frozen copy, raised only when the pin CHECKS OUT.

    A new PARTIAL run is therefore a real finding, and this test is the tripwire.
    """
    reports = verify_all()
    partial = {r["run_id"]: {d["code"] for d in r["discrepancies"]}
               for r in reports if r["verdict"] == "PARTIAL"}
    assert not [r for r in reports if r["verdict"] == "FAIL"]
    assert set(partial) == {"55maps-text-min-n10-uplift", "e47-propose-brief",
                            "n1-outstanding-384"}, partial
    assert partial["55maps-text-min-n10-uplift"] == {"n-passes-over"}
    assert partial["e47-propose-brief"] == {"pinned-vintage"}
    assert partial["n1-outstanding-384"] == {"pinned-vintage"}
