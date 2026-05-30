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
- the run row is ``mixed`` with a null (human-designated) headline;
- whole-manifest envelopes validate, including the run-registry's deliberate
  omission of ``generator_version`` (regression guard for the envelope builder).
"""

from __future__ import annotations

import pytest

from scripts.generate_post_run_report import (
    GS_V2_FACTS,
    assemble_manifest,
    extract_conditions,
    extract_passes,
    extract_registry_entry,
    extract_run_row,
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
    passes = extract_passes(GS_V2_FACTS)
    assert len(passes) == 6  # 5 detect_brief-text proposer + 1 verified-v1 verifier
    for p in passes:
        assert validate_row("passes", p, registry) == []
    # authoritative model identity, read from metadata not the directory name
    assert all(p["model_used"].startswith("gemini-3") for p in passes)


@pytest.mark.tier1
def test_gs_v2_conditions_valid_with_metrics(registry):
    conditions = extract_conditions(GS_V2_FACTS)
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
def test_gs_v2_run_and_registry_valid(registry):
    conditions = extract_conditions(GS_V2_FACTS)
    run_row = extract_run_row(GS_V2_FACTS, conditions)
    assert validate_row("runs", run_row, registry) == []
    assert run_row["run_type"] == "mixed"  # consensus + proposer-verifier conditions
    assert run_row["headline_condition_id"] is None  # human-designated; left null
    assert validate_row("run-registry", extract_registry_entry(GS_V2_FACTS), registry) == []


@pytest.mark.tier1
def test_manifest_envelopes_valid(registry):
    at = "2026-05-30T00:00:00Z"
    conditions = extract_conditions(GS_V2_FACTS, at)

    runs_obj = assemble_manifest("runs", [extract_run_row(GS_V2_FACTS, conditions, at)], at)
    assert validate_manifest("runs", runs_obj, registry) == []
    assert "generator_version" in runs_obj

    # the run-registry schema declares no generator_version and is closed —
    # the envelope builder must omit it (regression for the additionalProperties bug)
    reg_obj = assemble_manifest("run-registry", [extract_registry_entry(GS_V2_FACTS)], at)
    assert validate_manifest("run-registry", reg_obj, registry) == []
    assert "generator_version" not in reg_obj
