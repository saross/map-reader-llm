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

import pytest

from scripts.generate_post_run_report import (
    assemble_manifest,
    build_manifests,
    build_run_row,
    drift_check,
    extract_conditions,
    extract_passes,
    extraction_context,
    load_run_conditions,
    load_run_facts,
    load_run_registry,
    load_schema_registry,
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
    assert len(reg["registry"]) == 27
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
    _reg, run_rows, conditions, passes, warnings = build_manifests(at)
    assert len(run_rows) == 27
    assert warnings == []

    runs_obj = assemble_manifest("runs", run_rows, at)
    assert validate_manifest("runs", runs_obj, registry) == []
    assert "generator_version" in runs_obj

    cond_obj = assemble_manifest("conditions", conditions, at)
    assert validate_manifest("conditions", cond_obj, registry) == []
    assert len(conditions) == 4  # gold-standard-v2 vertical slice (Phase 3b extends this)

    passes_obj = assemble_manifest("passes", passes, at)
    assert validate_manifest("passes", passes_obj, registry) == []
    assert len(passes) == 6  # gold-standard-v2 vertical slice (Phase 3b extends this)
