"""Tier-1 tests for ``scripts/generate_post_run_report.py`` (the manifest generator).

Covers the schema-validation harness plus the gold-standard-v2 vertical-slice
extractors. These are integration tests against the committed source-of-truth
files (the gs-v2 outputs, the backfilled evaluations, and the JSON Schemas), so
they are deterministic and fast (no API, no bootstrap compute).

Asserts:

- the six manifest schemas load and the row validator rejects a malformed slug;
- the gs-v2 passes/conditions/run/registry rows validate against their schemas;
- ``model_used`` is the authoritative metadata value (gemini-3 family), never a
  directory-name inference;
- the consensus vote-threshold sweep is monotonic in F1 (the H3 signal);
- every condition carries the schema-required tile-classification confusion
  counts as integers;
- the gold-standard-v2 run row is ``mixed`` with a null (human-designated) headline;
- the 27-run registry input validates and stays in sync with the facts (drift
  guard), and the whole-manifest envelopes validate;
- the run-conditions decomposition sidecar is free of orphan runs (every
  decomposed run is in the registry and the facts — the 3-input drift guard).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import json

import pytest

from scripts.generate_post_run_report import (
    PLANNED_STALE_DAYS,
    _carry_timestamps,
    _stabilise_timestamps,
    _strip_ts,
    assemble_manifest,
    build_analyses,
    build_manifests,
    build_run_row,
    check_write_once_predictions,
    draft_run,
    drift_check,
    extract_conditions,
    extract_passes,
    extraction_context,
    load_run_analyses,
    load_run_conditions,
    load_run_facts,
    load_run_registry,
    load_schema_registry,
    report_planned_runs,
    validate_manifest,
    validate_row,
)


@pytest.fixture(scope="module")
def registry():
    """The schema registry, loaded once for the module."""
    reg, _ = load_schema_registry()
    return reg


@pytest.mark.tier1
def test_all_six_schemas_load():
    _reg, contents = load_schema_registry()
    assert len(contents) == 6  # runs/conditions/passes/analyses/run-registry/common-defs


@pytest.mark.tier1
def test_validate_row_rejects_bad_slug(registry):
    errors = validate_row(
        "run-registry", {"run_id": "Bad/Slug", "directory_path": "outputs/x"}, registry
    )
    assert any("run_id" in e for e in errors)


@pytest.mark.tier1
def test_gs_v2_passes_valid(registry):
    passes = extract_passes(extraction_context("gold-standard-v2"))
    assert len(passes) == 6  # 5 detect_brief-text proposer + 1 verified-v1 verifier
    for p in passes:
        assert validate_row("passes", p, registry) == []
    # authoritative model identity, read from metadata not the directory name
    assert all(p["model_used"].startswith("gemini-3") for p in passes)


@pytest.mark.tier1
def test_era1_proposer_pass_model_fallback(registry):
    # GAP-9: the Era-1 batch-API meta has no per_item_metadata, so model_used must
    # fall back to configuration.model (gemini-3-flash) and the tile count to
    # execution_stats.items_processed (340) — not "" / 0. Uses an explicit pool path
    # because Era-1 runs put pool dirs directly under the run (no proposer/ subdir).
    ctx = {
        "run_id": "retest-phase2a",
        "directory_path": "outputs/retest/phase2a",
        "scope": {},
        "proposer_pools": {"brief-text": {"modality": "text", "path": "brief-text"}},
        "verifier_passes": {},
        "conditions": [],
    }
    passes = extract_passes(ctx)
    assert len(passes) == 3  # brief-text/run_1..run_3
    for p in passes:
        assert validate_row("passes", p, registry) == []
        assert p["model_used"] == "gemini-3-flash"  # from configuration.model, not ""
        assert p["n_tiles_processed"] == 340  # from execution_stats, not len(pim)=0
        assert p["status"] == "ok"


@pytest.mark.tier1
def test_verifier_pass_effective_temperature(registry):
    # GAP-10/E55: the swept verifier temperature lives in temperature_effective, not
    # configuration.temperature (which reads 0.0). The label is slug-safe; the path
    # points at the real dotted directory.
    ctx = {
        "run_id": "verifier-t-pilot",
        "directory_path": "outputs/verifier-t-pilot",
        "scope": {},
        "proposer_pools": {},
        "verifier_passes": {"t0-5": {"modality": "image", "path": "T0.5"}},
        "conditions": [],
    }
    passes = extract_passes(ctx)
    assert len(passes) == 1
    assert validate_row("passes", passes[0], registry) == []
    assert passes[0]["temperature"] == 0.5  # temperature_effective, not the 0.0 base field


@pytest.mark.tier1
def test_verifier_pass_sidecar_meta(registry):
    # proposer-verifier strategy runs (pv-384/pv-512) store the verifier run metadata
    # as a sibling sidecar `verified-<strategy>.meta.json`, not the gold-standard-v2
    # per-pass `<dir>/run.meta.json`. The extractor must fall back to the sidecar, and
    # the model-of-record must come from per_item_metadata (gemini-3-flash-preview),
    # NOT configuration.model (the unreliable gemini-3-flash template default — E57).
    ctx = {
        "run_id": "proposer-verifier-512",
        "directory_path": "outputs/h11/proposer-verifier-512",
        "scope": {},
        "proposer_pools": {},
        "verifier_passes": {"verified-adversarial-text": {"modality": "text"}},
        "conditions": [],
    }
    passes = extract_passes(ctx)
    assert len(passes) == 1  # the sidecar meta is found despite no run_N dir
    assert validate_row("passes", passes[0], registry) == []
    assert passes[0]["model_used"] == "gemini-3-flash-preview"  # per-item, not cfg.model
    assert passes[0]["model_version"] == "gemini-3-flash-preview"
    assert passes[0]["status"] == "ok"


@pytest.mark.tier1
def test_gs_v2_conditions_valid_with_metrics(registry):
    conditions = extract_conditions(extraction_context("gold-standard-v2"))
    assert {c["label"] for c in conditions} == {
        "consensus-3of5", "consensus-4of5", "consensus-5of5", "verified-v1",
    }
    for c in conditions:
        assert validate_row("conditions", c, registry) == []
        tile = c["metrics"]["tile_classification"]
        assert all(isinstance(tile[k], int) for k in ("tp", "tn", "fp", "fn"))
    # H3 signal: F1 rises monotonically with the consensus vote threshold
    by_vote = {
        c["vote_threshold"]: c["metrics"]["per_buffer"]["20"]["f1"]
        for c in conditions
        if c["aggregation"] == "consensus"
    }
    assert by_vote[3] < by_vote[4] < by_vote[5]


@pytest.mark.tier1
def test_condition_explicit_eval_path(registry):
    # G-E: a condition names its scoring eval explicitly, overriding the auto-matcher.
    # consensus_t4.geojson is scored by TWO evals: greedy/canonical/t4 (487 scope,
    # F1-only, no MCC) and with-mcc/canonical (327 scope, F1@20 + MCC). The context
    # below is rigged so the auto-matcher WOULD mispick: detections is set and the
    # scope is the 487 bounds, so a regression that ignored eval_path would select
    # the MCC-less 487 sibling and the mcc==0.6785 assertion would fail. eval_path
    # must force the complete with-MCC eval.
    ctx = {
        "run_id": "h8-v2",
        "directory_path": "outputs/h8-v2",
        "scope": {"bounds_path": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"},
        "proposer_pools": {},
        "verifier_passes": {},
        "conditions": [{
            "label": "canonical-greedy",
            "architecture": "consensus",
            "aggregation": "greedy",
            "proposer_pool": "canonical",
            "n_passes": 5,
            "vote_threshold": 4,
            "detections": "outputs/h8-v2/greedy/canonical/consensus_t4.geojson",
            "eval_path": "results/h8-v2/with-mcc/canonical/evaluation.json",
        }],
    }
    conditions = extract_conditions(ctx)
    assert len(conditions) == 1
    c = conditions[0]
    assert validate_row("conditions", c, registry) == []
    assert c["condition_id"] == "h8-v2::canonical-greedy"
    tile = c["metrics"]["tile_classification"]
    assert tile["mcc"] == 0.6785  # from the named with-MCC eval, NOT the 487 auto-match
    assert (tile["tp"], tile["tn"], tile["fp"], tile["fn"]) == (118, 156, 16, 37)
    assert c["metrics"]["per_buffer"]["20"]["f1"] == 0.7071
    # provenance cites the named eval, not the auto-match detections path
    assert c["provenance"]["source_files"] == ["results/h8-v2/with-mcc/canonical/evaluation.json"]


@pytest.mark.tier1
def test_draft_run_enumerates_pools_and_candidates():
    # the I-draft half: walking h8-v2 finds its 7 composition pools (each by its
    # run_N/*.meta.json children) and lists scored evals as condition candidates.
    draft = draft_run("h8-v2")
    pools = draft["proposed_decomposition"]["proposer_pools"]
    assert {v["path"] for v in pools.values()} == {
        "canonical", "plus-hp", "pure-positive-canon",
        "scale-4", "scale-8", "scale-16", "scale-32",
    }
    assert all("modality" in v and "path" in v for v in pools.values())
    cands = draft["condition_candidates"]
    assert cands
    assert all({"detections", "eval_path", "has_mcc", "n_detections"} <= set(c) for c in cands)
    # modality keyword-inference: Era-1 pool names carry the modality
    a2 = draft_run("retest-phase2a")["proposed_decomposition"]["proposer_pools"]
    assert a2["brief-text"]["modality"] == "text"
    assert a2["image-only"]["modality"] == "image"


@pytest.mark.tier1
def test_draft_run_unknown_raises():
    with pytest.raises(KeyError, match="not in the run registry"):
        draft_run("no-such-run")


@pytest.mark.tier1
def test_condition_missing_key_raises():
    # audit §4a: a hand-authored spec missing a required key fails with a descriptive
    # ValueError naming the run + label, not an opaque KeyError mid-build.
    ctx = {
        "run_id": "x", "directory_path": "outputs/x", "scope": {},
        "conditions": [{  # missing "architecture"
            "label": "bad", "aggregation": "greedy", "proposer_pool": "p",
            "n_passes": 5, "eval_path": "results/whatever.json",
        }],
    }
    with pytest.raises(ValueError, match="architecture"):
        extract_conditions(ctx)


@pytest.mark.tier1
def test_gs_v2_run_row_valid(registry):
    facts = load_run_facts()
    conditions = extract_conditions(extraction_context("gold-standard-v2"))
    run_row = build_run_row(
        "gold-standard-v2", "outputs/gs/gold-standard-v2", facts["gold-standard-v2"], conditions
    )
    assert validate_row("runs", run_row, registry) == []
    assert run_row["run_type"] == "mixed"  # consensus + proposer-verifier conditions
    assert run_row["headline_condition_id"] is None  # human-designated; left null


@pytest.mark.tier1
def test_run_registry_input_valid_and_in_sync(registry):
    # the registry is now a hand-authored INPUT the generator reads, not synthesises (B1)
    reg = load_run_registry()
    assert validate_manifest("run-registry", reg, registry) == []
    # 29: +verifier-robustness (S111); 31: +flash35-pv-2x2,
    # +55maps-text-min-n10-uplift (S113 second wave)
    assert len(reg["registry"]) == 31
    assert "generator_version" not in reg  # run-registry schema is closed; no generator_version
    # registry and facts must describe the same run set (the B1 drift guard)
    assert drift_check(reg["registry"], load_run_facts()) == []


@pytest.mark.tier1
def test_run_conditions_sidecar_in_sync(registry):
    # the decomposition sidecar (3b, Q3) is the generator's third hand-authored
    # input; every decomposed run must resolve against the registry and the facts
    reg = load_run_registry()
    facts = load_run_facts()
    decomposition = load_run_conditions()
    assert "gold-standard-v2" in decomposition  # the migrated vertical slice
    # no orphan decomposition: 3-input drift (registry <-> facts <-> conditions) is clean
    assert drift_check(reg["registry"], facts, decomposition) == []
    # negative path: a decomposed run absent from registry + facts MUST be flagged.
    # Proves the 3rd-argument branch actually executes (not a tautology on live data,
    # where the sole decomposed run happens to be present in both other inputs).
    orphaned = {**decomposition, "zzz-orphan-run": {"conditions": []}}
    warnings = drift_check(reg["registry"], facts, orphaned)
    assert any("zzz-orphan-run" in w for w in warnings)


@pytest.mark.tier1
def test_manifest_envelopes_valid(registry):
    at = "2026-05-30T00:00:00Z"
    _reg, run_rows, conditions, passes, analyses, warnings = build_manifests(at)
    # 29: +verifier-robustness (S111); 31: +flash35-pv-2x2,
    # +55maps-text-min-n10-uplift (S113 second wave)
    assert len(run_rows) == 31
    assert warnings == []

    runs_obj = assemble_manifest("runs", run_rows, at)
    assert validate_manifest("runs", runs_obj, registry) == []
    assert "generator_version" in runs_obj

    cond_obj = assemble_manifest("conditions", conditions, at)
    assert validate_manifest("conditions", cond_obj, registry) == []
    # The gold-standard-v2 vertical slice (4 conditions) is stable; Phase 3b adds
    # more runs, so assert the slice + a non-shrinking total rather than a brittle ==.
    gs_conditions = [c for c in conditions if c["run_id"] == "gold-standard-v2"]
    assert len(gs_conditions) == 4
    assert len(conditions) >= 4

    passes_obj = assemble_manifest("passes", passes, at)
    assert validate_manifest("passes", passes_obj, registry) == []
    gs_passes = [p for p in passes if p["run_id"] == "gold-standard-v2"]
    assert len(gs_passes) == 6
    assert len(passes) >= 6

    # Analyses (sub-step 3c): the assembled envelope validates, and every
    # conditions_compared id resolves to a built condition (the build_manifests FK
    # guard would have populated `warnings` otherwise — already asserted empty above).
    analyses_obj = assemble_manifest("analyses", analyses, at)
    assert validate_manifest("analyses", analyses_obj, registry) == []
    known_ids = {c["condition_id"] for c in conditions}
    for a in analyses:
        assert set(a["conditions_compared"]) <= known_ids


@pytest.mark.tier1
def test_model_of_record_override(registry):
    """``model_of_record`` declares the authoritative dispatched model (E57).

    Two cases, both exercised here:

    * **n1-outstanding-384** — its four Pro-slug pools were DISPATCHED AS FLASH (the
      runner never threaded --model; per_item_metadata.model_version is
      gemini-3-flash-preview). The sidecar's model_of_record was CORRECTED from the
      mistaken gemini-3.1-pro to gemini-3-flash-preview (the Session-97 billing
      verdict). Passes from those pools report flash as model_used/model_requested and
      cite the sidecar in provenance (the override path still executes, even though the
      value now agrees with the meta); the run's other, genuinely-flash pools report
      flash from the meta with NO sidecar citation.
    * **n1-pro-rerun-384** — the genuine-Pro re-dispatch. Every pool declares
      model_of_record=gemini-3.1-pro-preview, matching the reliable meta
      (model_version), and cites the sidecar in provenance.
    """
    # n1-outstanding-384: the four Pro-slug pools billed as Flash (E57 corrected).
    passes = extract_passes(extraction_context("n1-outstanding-384"))
    pro = [p for p in passes if p["proposer_pool"].startswith("pro-")]
    flash = [p for p in passes if not p["proposer_pool"].startswith("pro-")]
    assert pro and flash
    for p in pro:
        assert validate_row("passes", p, registry) == []
        assert p["model_used"] == "gemini-3-flash-preview"
        assert p["model_requested"] == "gemini-3-flash-preview"
        assert "results/run-conditions.json" in p["provenance"]["source_files"]
    for p in flash:
        assert p["model_used"] == "gemini-3-flash-preview"
        assert "results/run-conditions.json" not in p["provenance"]["source_files"]

    # n1-pro-rerun-384: the genuine-Pro re-dispatch asserts gemini-3.1-pro-preview.
    rerun = extract_passes(extraction_context("n1-pro-rerun-384"))
    assert rerun
    for p in rerun:
        assert validate_row("passes", p, registry) == []
        assert p["model_used"] == "gemini-3.1-pro-preview"
        assert p["model_requested"] == "gemini-3.1-pro-preview"
        assert p["model_version"] == "gemini-3.1-pro-preview"
        assert "results/run-conditions.json" in p["provenance"]["source_files"]


@pytest.mark.tier1
def test_analyses_leaderboard_finding(registry):
    """The N=1 baseline-matrix leaderboard builds, validates, and reflects the E57 replace.

    Machine fields are populated (18 baseline condition_ids, type=leaderboard,
    preregistered=exploratory). The four anti-diagonal Pro cells are sourced from the
    genuine-Pro re-run (n1-pro-rerun-384), REPLACING the Flash-misdispatched
    n1-outstanding cells of the same corners (E57). The interpretive finding
    (outcome / tie_set) is authored/revised separately and is not pinned here, so this
    test is stable across the PENDING-re-tiering window.
    """
    analyses = build_analyses(load_run_analyses(), "2026-05-30T00:00:00Z")
    lb = next(a for a in analyses if a["analysis_id"] == "n1-baseline-matrix-384")
    assert validate_row("analyses", lb, registry) == []
    assert lb["type"] == "leaderboard"
    assert len(lb["conditions_compared"]) == 18
    assert all(cid.split("::")[1].startswith("baseline-") for cid in lb["conditions_compared"])
    assert lb["preregistered"] == "exploratory"
    # E57 replace: the genuine-Pro re-run cells are IN; the Flash-misdispatched
    # n1-outstanding "pro" cells of the same four corners are OUT.
    corners = (
        "baseline-pro-text-high-t-0-0",
        "baseline-pro-text-medium-t-0-7",
        "baseline-pro-image-high-t-0-0",
        "baseline-pro-image-medium-t-0-7",
    )
    for corner in corners:
        assert f"n1-pro-rerun-384::{corner}" in lb["conditions_compared"]
        assert f"n1-outstanding-384::{corner}" not in lb["conditions_compared"]
    assert "_note" not in lb  # additionalProperties:false — sidecar note not emitted


# --------------------------------------------------------------------------- #
# Timestamp stabilisation — no-op regenerations stay byte-identical so manifest
# git diffs show only real changes (no per-row last_extracted_at churn).
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_strip_ts_blanks_timestamps_recursively():
    obj = {
        "generated_at": "T1",
        "rows": [{"id": "a", "provenance": {"last_extracted_at": "T2", "x": 1}}],
    }
    stripped = _strip_ts(obj)
    assert stripped["generated_at"] == ""
    assert stripped["rows"][0]["provenance"]["last_extracted_at"] == ""
    assert stripped["rows"][0]["provenance"]["x"] == 1  # content preserved
    assert obj["generated_at"] == "T1"  # original untouched (deep copy)


@pytest.mark.tier1
def test_carry_timestamps_copies_only_timestamp_values():
    new = {"id": "a", "provenance": {"last_extracted_at": "NEW", "f1": 0.9}}
    old = {"id": "a", "provenance": {"last_extracted_at": "OLD", "f1": 0.9}}
    _carry_timestamps(new, old)
    assert new["provenance"]["last_extracted_at"] == "OLD"  # timestamp carried
    assert new["provenance"]["f1"] == 0.9  # content untouched


@pytest.mark.tier1
def test_stabilise_timestamps_noop_regen_is_byte_identical(tmp_path):
    import json

    disk = {
        "schema_version": "1.0",
        "generated_at": "OLD",
        "conditions": [
            {"condition_id": "r::a", "n_passes": 1,
             "provenance": {"last_extracted_at": "OLD", "source_files": ["x"]}},
        ],
    }
    path = tmp_path / "conditions-manifest.json"
    path.write_text(json.dumps(disk, indent=2) + "\n")
    # A fresh build: identical content, but every timestamp re-stamped to "NOW".
    fresh = json.loads(json.dumps(disk).replace("OLD", "NOW"))
    _stabilise_timestamps("conditions", fresh, path)
    assert fresh["generated_at"] == "OLD"
    assert fresh["conditions"][0]["provenance"]["last_extracted_at"] == "OLD"
    # The whole object is byte-identical to disk → no git diff.
    assert json.dumps(fresh, indent=2) + "\n" == path.read_text()


@pytest.mark.tier1
def test_stabilise_timestamps_restamps_only_changed_row(tmp_path):
    import json

    disk = {
        "schema_version": "1.0",
        "generated_at": "OLD",
        "conditions": [
            {"condition_id": "r::a", "f1": 1,
             "provenance": {"last_extracted_at": "OLD", "source_files": ["x"]}},
            {"condition_id": "r::b", "f1": 2,
             "provenance": {"last_extracted_at": "OLD", "source_files": ["x"]}},
        ],
    }
    path = tmp_path / "conditions-manifest.json"
    path.write_text(json.dumps(disk, indent=2) + "\n")
    fresh = {
        "schema_version": "1.0",
        "generated_at": "NOW",
        "conditions": [
            {"condition_id": "r::a", "f1": 1,
             "provenance": {"last_extracted_at": "NOW", "source_files": ["x"]}},
            {"condition_id": "r::b", "f1": 99,  # this row changed
             "provenance": {"last_extracted_at": "NOW", "source_files": ["x"]}},
        ],
    }
    _stabilise_timestamps("conditions", fresh, path)
    assert fresh["conditions"][0]["provenance"]["last_extracted_at"] == "OLD"  # unchanged row
    assert fresh["conditions"][1]["provenance"]["last_extracted_at"] == "NOW"  # changed row
    assert fresh["generated_at"] == "NOW"  # a row changed → manifest stamp bumps


@pytest.mark.tier1
def test_stabilise_timestamps_absent_file_keeps_fresh(tmp_path):
    fresh = {"schema_version": "1.0", "generated_at": "NOW", "conditions": []}
    _stabilise_timestamps("conditions", fresh, tmp_path / "does-not-exist.json")
    assert fresh["generated_at"] == "NOW"  # first generation keeps fresh timestamps


@pytest.mark.tier1
def test_cross_family_model_override_prefers_pricing_used(registry):
    """E57: a cross-family config/pricing disagreement resolves to pricing_used.model.

    `pv-diag-384::pro-high-text-n5` runs 1-5 carry `configuration.model =
    gemini-3-flash` (an unreliable template default, serialised without the
    per-study Pro override) while `cost_estimate.pricing_used.model` records the
    model actually dispatched. Per E57's 2026-06-03 Update, pricing_used is
    authoritative. Regression guard: these ten passes were previously published
    as Flash.
    """
    ctx = {
        "run_id": "pv-diag-384",
        "directory_path": "outputs/h11/pv-diag-384",
        "scope": {},
        "proposer_pools": {
            "pro-high-text-n5-text-t0.7": {
                "modality": "text", "path": "pro-high-text-n5/text-t0.7"},
        },
        "verifier_passes": {},
        "conditions": [],
    }
    passes = extract_passes(ctx)
    assert passes, "expected the pro-high-text pool to yield passes"
    for p in passes:
        assert validate_row("passes", p, registry) == []
    early = [p for p in passes if p["pass_n"] <= 5]
    assert early, "runs 1-5 are the cross-family cases"
    for p in early:
        assert p["model_used"] == "gemini-3.1-pro-preview"
        assert p["model_requested"] == "gemini-3.1-pro-preview"


@pytest.mark.tier1
def test_alias_resolution_does_not_rewrite_model_of_record(registry):
    """A same-family suffix difference must NOT trigger the override.

    `gemini-3-flash` vs `gemini-3-flash-preview` is alias resolution, not a
    different model. Rewriting the project's model-of-record string is a separate
    decision from correcting a mislabelled family, and letting the override fire
    here would churn ~744 pass rows. Pins the prefix test in both directions.
    """
    ctx = {
        "run_id": "retest-phase2a",
        "directory_path": "outputs/retest/phase2a",
        "scope": {},
        "proposer_pools": {"brief-text": {"modality": "text", "path": "brief-text"}},
        "verifier_passes": {},
        "conditions": [],
    }
    passes = extract_passes(ctx)
    assert passes
    for p in passes:
        assert p["model_used"] == "gemini-3-flash"  # NOT ...-preview


# --------------------------------------------------------------------------- #
# status: planned — declaring intent before execution (repair (3), 2026-07-28)
# --------------------------------------------------------------------------- #

_PLANNED = {
    "run_id": "h7-escalation",
    "directory_path": "outputs/h7-escalation",
    "status": "planned",
    "planned_at": "2026-07-28T00:00:00Z",
}


@pytest.mark.tier1
def test_drift_check_exempts_planned_runs():
    """A planned run has no facts and no decomposition BY DESIGN — not a drift."""
    assert drift_check([_PLANNED], facts={}, conditions={}) == []
    # An ACTIVE run with no facts is still a drift; the exemption is status-scoped.
    active = dict(_PLANNED, status="active")
    assert any("NO facts entry" in w for w in drift_check([active], facts={}, conditions={}))


@pytest.mark.tier1
def test_drift_check_flags_decomposed_planned_run():
    """Decomposing a run that has not executed is its own, distinctly-worded error."""
    warnings = drift_check([_PLANNED], facts={}, conditions={"h7-escalation": {}})
    assert len(warnings) == 1
    assert "registry status is 'planned'" in warnings[0]
    # Must NOT be mistaken for an ordinary orphan decomposition.
    assert "NOT in the registry" not in warnings[0]


@pytest.mark.tier1
def test_report_planned_runs_ages_and_flags_stale():
    """Planned runs are the only build output that mentions them, so age is shown."""
    fresh = report_planned_runs([_PLANNED], now=datetime(2026, 7, 29, tzinfo=timezone.utc))
    assert fresh == ["PLANNED  h7-escalation  (declared 1d ago)"]

    stale_day = datetime(2026, 7, 28, tzinfo=timezone.utc) + timedelta(
        days=PLANNED_STALE_DAYS)
    stale = report_planned_runs([_PLANNED], now=stale_day)
    assert "STALE" in stale[0]

    # Non-planned entries are ignored entirely.
    assert report_planned_runs([dict(_PLANNED, status="active")]) == []


@pytest.mark.tier1
def test_report_planned_runs_survives_missing_or_bad_date():
    """A malformed planned_at must not break the build — it degrades to a note."""
    no_date = report_planned_runs([{"run_id": "x", "status": "planned"}])
    assert "no planned_at recorded" in no_date[0]
    bad = report_planned_runs([{"run_id": "x", "status": "planned", "planned_at": "soon"}])
    assert "unparseable" in bad[0]


# --------------------------------------------------------------------------- #
# Write-once predictions (repair (2), 2026-07-28)
# --------------------------------------------------------------------------- #

def _analyses_file(tmp_path, predicted):
    """Write a minimal on-disk analyses manifest carrying one prediction."""
    p = tmp_path / "analyses-manifest.json"
    p.write_text(json.dumps({
        "schema_version": "1.0",
        "analyses": [{"analysis_id": "a1", "predicted_outcome": predicted}],
    }))
    return p


@pytest.mark.tier1
def test_write_once_blocks_silent_prediction_rewrite(tmp_path):
    """The H7 failure mode: a prediction restated to match the finding."""
    path = _analyses_file(tmp_path, "T=1.0 will be optimal")
    fresh = {"analyses": [{"analysis_id": "a1", "predicted_outcome": "T=0.0 will be optimal"}]}
    errors = check_write_once_predictions(fresh, path)
    assert len(errors) == 1
    assert "WRITE-ONCE" in errors[0]
    assert "predicted_outcome_amended" in errors[0]  # tells the author the legal route
    assert "T=1.0 will be optimal" in errors[0]      # and shows what is being overwritten


@pytest.mark.tier1
def test_write_once_allows_first_set_unchanged_and_explicit_amendment(tmp_path):
    """Setting, re-writing identically, and declared amendment are all legal."""
    # null -> value: always allowed (this IS the act of predicting).
    blank = _analyses_file(tmp_path, None)
    assert check_write_once_predictions(
        {"analyses": [{"analysis_id": "a1", "predicted_outcome": "declines"}]}, blank) == []

    path = _analyses_file(tmp_path, "declines")
    # Unchanged: the no-op regeneration case.
    assert check_write_once_predictions(
        {"analyses": [{"analysis_id": "a1", "predicted_outcome": "declines"}]}, path) == []
    # Explicitly amended: allowed, and the amendment is preserved in the row.
    amended = {"analyses": [{
        "analysis_id": "a1",
        "predicted_outcome": "rises",
        "predicted_outcome_amended": {"reason": "pilot invalidated the premise",
                                      "date": "2026-07-28",
                                      "previous": "declines"},
    }]}
    assert check_write_once_predictions(amended, path) == []


@pytest.mark.tier1
def test_write_once_is_inert_on_first_generation_and_new_rows(tmp_path):
    """No prior manifest, or an analysis_id not previously present, protects nothing."""
    assert check_write_once_predictions({"analyses": []}, tmp_path / "absent.json") == []
    path = _analyses_file(tmp_path, "declines")
    new_row = {"analyses": [{"analysis_id": "a2", "predicted_outcome": "anything"}]}
    assert check_write_once_predictions(new_row, path) == []


# --------------------------------------------------------------------------- #
# Regression tests for the 2026-07-28 /audit findings on the two repairs above.
# Each pins a defect that SHIPPED and was caught by adversarial review, not by
# the original tests — which is itself the argument for these existing.
# --------------------------------------------------------------------------- #

_AMEND_SPEC = {
    "analysis_id": "a1",
    "type": "leaderboard",
    "conditions_compared": ["some-run::some-condition"],
    "output_path": "results/nowhere",
    "predicted_outcome": "revised prediction",
    "predicted_outcome_amended": {"reason": "pilot invalidated the premise",
                                  "date": "2026-07-28",
                                  "previous": "original prediction"},
}


@pytest.mark.tier1
def test_amendment_survives_build_and_validates(registry):
    """AUDIT C1: the write-once escape hatch did not exist end to end.

    `predicted_outcome_amended` was checked by the guard but never copied by
    `build_analyses` (which enumerates its row keys) and was absent from the
    analyses schema (`additionalProperties: false`). The guard was therefore a
    permanent deadlock for every analysis already carrying a prediction, and its
    error message told authors to do something impossible. Both halves are pinned
    here: the key must reach the built row AND the row must validate.
    """
    row = build_analyses([_AMEND_SPEC], "2026-07-28T00:00:00Z")[0]
    assert row["predicted_outcome_amended"]["reason"] == "pilot invalidated the premise"
    assert validate_row("analyses", row, registry) == []


@pytest.mark.tier1
def test_amendment_unblocks_the_write_once_guard(tmp_path):
    """The escape hatch must actually release the guard on a real built row."""
    path = tmp_path / "analyses-manifest.json"
    path.write_text(json.dumps({
        "schema_version": "1.0",
        "analyses": [{"analysis_id": "a1", "predicted_outcome": "original prediction"}],
    }))
    built = {"analyses": [build_analyses([_AMEND_SPEC], "2026-07-28T00:00:00Z")[0]]}
    assert check_write_once_predictions(built, path) == []

    # ...and without the amendment the same rewrite is still refused.
    bare = dict(_AMEND_SPEC)
    del bare["predicted_outcome_amended"]
    built_bare = {"analyses": [build_analyses([bare], "2026-07-28T00:00:00Z")[0]]}
    assert len(check_write_once_predictions(built_bare, path)) == 1


@pytest.mark.tier1
def test_planned_run_with_facts_is_not_falsely_reported_missing():
    """AUDIT M1: the exemption was applied to one direction of the set algebra only.

    A planned run may legitimately have a facts entry — corpus, GT and scope are
    exactly what one authors when declaring intent — and was then reported as
    absent from the registry it was sitting in.
    """
    assert drift_check([_PLANNED], facts={"h7-escalation": {}}, conditions={}) == []
    # The same check still fires for a genuinely unregistered facts entry.
    assert any("NOT in the registry" in w
               for w in drift_check([], facts={"ghost": {}}, conditions={}))


@pytest.mark.tier1
def test_planned_run_needs_no_directory_path(tmp_path, monkeypatch):
    """AUDIT M2: directory_path was dereferenced before the planned skip.

    The schema says a planned run's path "need not exist yet", and the easiest
    thing to author omits it entirely — which raised KeyError instead of skipping.
    """
    import scripts.generate_post_run_report as gen

    entry = {"run_id": "h7-escalation", "status": "planned",
             "planned_at": "2026-07-28T00:00:00Z"}
    monkeypatch.setattr(gen, "load_run_registry", lambda: {"registry": [entry]})
    monkeypatch.setattr(gen, "load_run_facts", lambda: {})
    monkeypatch.setattr(gen, "load_run_conditions", lambda: {})
    monkeypatch.setattr(gen, "load_run_analyses", lambda: [])

    _, run_rows, conditions, passes, analyses, warnings = gen.build_manifests(
        "2026-07-28T00:00:00Z")
    assert run_rows == [] and conditions == [] and passes == []
    assert warnings == []  # a planned run is not drift


@pytest.mark.tier1
def test_lowercase_rfc3339_zone_designator_parses():
    """AUDIT L4: RFC 3339 permits lowercase 'z'; fromisoformat does not accept it."""
    line = report_planned_runs(
        [{"run_id": "x", "status": "planned", "planned_at": "2026-07-28t00:00:00z"}],
        now=datetime(2026, 7, 29, tzinfo=timezone.utc))[0]
    assert "declared 1d ago" in line and "unparseable" not in line


# --------------------------------------------------------------------------- #
# INTEGRATION — the gap the /audit identified: every unit test above stops at the
# function boundary, three layers short of the write. Deleting the four-line
# wiring in write_manifests, or the planned-run `continue`, left the whole suite
# green. These exercise write_manifests itself.
# --------------------------------------------------------------------------- #

def _sandbox_manifests(tmp_path, monkeypatch):
    """Point the writer at a throwaway tree so the real results/ is untouched."""
    import scripts.generate_post_run_report as gen
    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    (tmp_path / "results").mkdir(parents=True, exist_ok=True)
    return gen


def _analysis_spec(predicted, amended=None):
    spec = {
        "analysis_id": "a1",
        "type": "leaderboard",
        "conditions_compared": ["some-run::some-condition"],
        "output_path": "results/nowhere",
        "predicted_outcome": predicted,
    }
    if amended:
        spec["predicted_outcome_amended"] = amended
    return spec


@pytest.mark.tier1
def test_write_manifests_refuses_a_rewritten_prediction_end_to_end(
        tmp_path, monkeypatch, registry):
    """AUDIT C1: removing the guard's wiring left every unit test green.

    Exercises the real path — assemble, validate, guard, write — and asserts the
    on-disk file is unchanged by the refused rewrite. This is the historical H7
    failure mode tested where it actually has to be stopped.
    """
    gen = _sandbox_manifests(tmp_path, monkeypatch)
    at = "2026-07-28T00:00:00Z"
    path = tmp_path / gen.MANIFEST_FILES["analyses"]

    first = gen.build_analyses([_analysis_spec("T=1.0 will be optimal")], at)
    assert gen.write_manifests({"analyses": first}, at, registry)["analyses"][1] == []
    assert "T=1.0 will be optimal" in path.read_text()

    rewritten = gen.build_analyses([_analysis_spec("T=0.0 was preregistered")], at)
    errors = gen.write_manifests({"analyses": rewritten}, at, registry)["analyses"][1]
    assert errors and "WRITE-ONCE" in errors[0]
    assert "T=1.0 will be optimal" in path.read_text()   # disk untouched
    assert "T=0.0 was preregistered" not in path.read_text()


@pytest.mark.tier1
def test_write_manifests_accepts_a_targeted_amendment_end_to_end(
        tmp_path, monkeypatch, registry):
    """The documented escape hatch must work through the real pipeline.

    AUDIT C2: the escape hatch was previously tested only against a hand-built
    fixture the pipeline could not produce, which is exactly how a permanent
    deadlock shipped with seven tests green.
    """
    gen = _sandbox_manifests(tmp_path, monkeypatch)
    at = "2026-07-28T00:00:00Z"
    path = tmp_path / gen.MANIFEST_FILES["analyses"]

    gen.write_manifests(
        {"analyses": gen.build_analyses([_analysis_spec("T=1.0 will be optimal")], at)},
        at, registry)

    amended = gen.build_analyses([_analysis_spec(
        "T=0.0 will be optimal",
        {"reason": "pilot invalidated the premise", "date": "2026-07-28",
         "previous": "T=1.0 will be optimal"})], at)
    assert gen.write_manifests({"analyses": amended}, at, registry)["analyses"][1] == []
    assert "T=0.0 will be optimal" in path.read_text()


@pytest.mark.tier1
def test_stale_amendment_does_not_permanently_unlock(tmp_path, monkeypatch, registry):
    """AUDIT C4: any truthy amendment used to skip the check forever.

    `previous` must match what is on disk, so an amendment is spent when used and
    a leftover one cannot make the row freely rewritable on later builds.
    """
    gen = _sandbox_manifests(tmp_path, monkeypatch)
    at = "2026-07-28T00:00:00Z"
    amendment = {"reason": "pilot invalidated the premise", "date": "2026-07-28",
                 "previous": "T=1.0 will be optimal"}

    gen.write_manifests(
        {"analyses": gen.build_analyses([_analysis_spec("T=1.0 will be optimal")], at)},
        at, registry)
    gen.write_manifests(
        {"analyses": gen.build_analyses(
            [_analysis_spec("T=0.0 will be optimal", amendment)], at)}, at, registry)

    # Same amendment, third distinct prediction: `previous` is now stale.
    third = gen.build_analyses([_analysis_spec("something else entirely", amendment)], at)
    errors = gen.write_manifests({"analyses": third}, at, registry)["analyses"][1]
    assert errors and "does not match what is on disk" in errors[0]


@pytest.mark.tier1
def test_write_manifests_is_all_or_nothing(tmp_path, monkeypatch, registry):
    """AUDIT M5: a tripped guard used to leave three of four manifests written."""
    gen = _sandbox_manifests(tmp_path, monkeypatch)
    at = "2026-07-28T00:00:00Z"

    gen.write_manifests(
        {"analyses": gen.build_analyses([_analysis_spec("T=1.0 will be optimal")], at)},
        at, registry)
    runs_path = tmp_path / gen.MANIFEST_FILES["runs"]
    assert not runs_path.exists()

    # A valid runs bundle alongside a blocked analyses bundle: neither may land.
    bad = gen.build_analyses([_analysis_spec("rewritten")], at)
    out = gen.write_manifests({"runs": [], "analyses": bad}, at, registry)
    assert out["analyses"][1]          # analyses blocked
    assert out["runs"][1] == []        # runs itself was fine...
    assert not runs_path.exists()      # ...but was NOT written


@pytest.mark.tier1
def test_planned_run_is_excluded_from_generated_manifests(tmp_path, monkeypatch):
    """AUDIT C5: replacing the planned `continue` with `if False:` stayed green.

    The exclusion is the headline promise of repair (3) and had no coverage: the
    live registry contains no planned entries, so nothing reached the branch.
    """
    gen = _sandbox_manifests(tmp_path, monkeypatch)
    planned = {"run_id": "h7-escalation", "directory_path": "outputs/h7-escalation",
               "status": "planned", "planned_at": "2026-07-28T00:00:00Z"}
    monkeypatch.setattr(gen, "load_run_registry", lambda: {"registry": [planned]})
    monkeypatch.setattr(gen, "load_run_facts", lambda: {"h7-escalation": {}})
    monkeypatch.setattr(gen, "load_run_conditions", lambda: {})
    monkeypatch.setattr(gen, "load_run_analyses", lambda: [])

    _, run_rows, conditions, passes, _, warnings = gen.build_manifests(
        "2026-07-28T00:00:00Z")
    assert [r["run_id"] for r in run_rows] == []
    assert conditions == [] and passes == [] and warnings == []
    # ...and it is visible in the build output rather than silently absent.
    assert gen.report_planned_runs([planned])[0].startswith("PLANNED  h7-escalation")
