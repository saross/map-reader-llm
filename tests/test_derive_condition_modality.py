"""Tests for ``scripts/derive_condition_modality.py`` (the modality derivation).

Modality is a preregistered factor (H1), so no artefact may assert a
condition's modality: it has to be derivable from the configuration the
proposer transmitted. These tests pin the derivation's pure logic against
synthetic fixtures (tier 1) and, for the two artefacts whose labels are now
derived, assert corpus-wide agreement against the committed register
(tier 2 — it reads the manifests and the ``outputs/`` metas).

The two failure shapes the 2026-09-14 audit found are covered explicitly:

1. a label naming the VERIFIER's modality over a text proposer
   (``verified-brief-image`` on ``detect_brief-text``), and
2. a label with NO modality token, where ``"image" in label`` is false and a
   substring test falls through to ``"text"`` (``pv-scale4-optimal-n1-opmax``
   on ``detect_h8_scale-4_v2``).

The register's ``verifier_passes[...].modality`` convention — the VERIFIER
stage's own exemplar modality, settled by the PI on 2026-09-14 (erratum E88) —
is pinned here too: the planner that brings the register to that convention,
and a corpus-wide assertion that the committed register carries it.
"""

from __future__ import annotations

import gzip
import json

import pytest

from scripts import derive_condition_modality as d


# ── tier 1: the pure logic ───────────────────────────────────────────────

@pytest.mark.tier1
@pytest.mark.parametrize(
    "configs, expected",
    [
        ([], None),
        ([{"include_example_images": False, "n_examples": 3}], "text"),
        ([{"include_example_images": True, "n_examples": 13}], "image"),
        # include_example_images true but nothing to send is not image-bearing.
        ([{"include_example_images": True, "n_examples": 0}], "text"),
        # ANY pass that sent pixels makes the pool image-bearing.
        ([{"include_example_images": False, "n_examples": 3},
          {"include_example_images": True, "n_examples": 3}], "image"),
    ],
)
def test_modality_of_reads_the_transmitted_exemplar_library(configs, expected):
    assert d.modality_of(configs) == expected


@pytest.mark.tier1
@pytest.mark.parametrize(
    "text, token, as_modality",
    [
        ("detect_brief-text", "text", "text"),
        ("image-n5-image-t0.3", "image", "image"),
        # A text+image config DID send pixels: "both" reads as image.
        ("brief-text-image", "both", "image"),
        # The failure shape: no token at all.
        ("pv-scale4-optimal-n1-opmax", None, None),
        ("scale-4-optimal-487", None, None),
    ],
)
def test_name_token_and_its_reading(text, token, as_modality):
    assert d.name_token(text) == token
    assert d.token_as_modality(token) == as_modality


@pytest.mark.tier1
@pytest.mark.parametrize(
    "recorded, expected",
    [
        ("image", "image"),
        ("text", "text"),
        # A refinement of "image", not a third level of the binary factor.
        ("text+image", "image"),
        ("unknown", None),
        (None, None),
        (3, None),
    ],
)
def test_comparable_maps_recorded_values_onto_the_binary_factor(recorded, expected):
    assert d.comparable(recorded) == expected


@pytest.mark.tier1
def test_read_meta_defaults_include_example_images_to_true():
    """The pipeline defaults the key to True, so a config without it sent images."""
    assert d.PIPELINE_INCLUDE_IMAGES_DEFAULT is True


@pytest.mark.tier1
def test_read_meta_reads_a_plain_meta(tmp_path):
    path = tmp_path / "detections.meta.json"
    path.write_text(json.dumps({"configuration": {
        "version": "detect_h8_scale-4_v2",
        "full_config_snapshot": {
            "include_example_images": True,
            "examples": [{"category": "null"}, {"category": "canonical_positive"}],
        }}}), encoding="utf-8")
    meta = d.read_meta(path)
    assert meta["config"] == "detect_h8_scale-4_v2"
    assert meta["include_example_images"] is True
    assert meta["n_examples"] == 2 and meta["n_null_examples"] == 1
    assert d.modality_of([meta]) == "image"


@pytest.mark.tier1
def test_read_meta_falls_back_to_the_pipeline_default(tmp_path):
    path = tmp_path / "no-key.meta.json"
    path.write_text(json.dumps({"configuration": {
        "version": "detect_something", "full_config_snapshot": {"examples": [{"category": "x"}]}}}),
        encoding="utf-8")
    assert d.read_meta(path)["include_example_images"] is True


@pytest.mark.tier1
def test_read_meta_reads_a_gzipped_meta(tmp_path):
    path = tmp_path / "gz.meta.json"
    path.write_bytes(gzip.compress(json.dumps({"configuration": {
        "version": "detect_brief-text",
        "include_example_images": False,
        "full_config_snapshot": {"examples": [{"category": "null"}]}}}).encode()))
    meta = d.read_meta(path)
    assert meta["include_example_images"] is False
    assert d.modality_of([meta]) == "text"


@pytest.mark.tier1
def test_read_meta_returns_none_for_absent_or_configless_files(tmp_path):
    assert d.read_meta(tmp_path / "missing.meta.json") is None
    empty = tmp_path / "empty.meta.json"
    empty.write_text("{}", encoding="utf-8")
    assert d.read_meta(empty) is None


@pytest.mark.tier1
def test_verifier_metas_are_not_mistaken_for_proposer_metas():
    """A ``verify_*`` config transmits no exemplar library at all."""
    assert d.is_proposer_meta({"config": "detect_brief-text"}) is True
    assert d.is_proposer_meta({"config": "verify_adversarial-text"}) is False
    assert d.is_proposer_meta({"config": None}) is False


@pytest.mark.tier1
@pytest.mark.parametrize(
    "pool, expected_member",
    [
        # Vote-fraction suffix -> the -nK pool directory that supplied it.
        ("flash-high-text-1of5", "flash-high-text-n5"),
        ("flash-high-text-consensus-16of30", "flash-high-text-n30"),
        # Operating-point markers the board builders mint.
        ("scale-4-optimal-487-opmax", "scale-4-optimal-487"),
        ("pv-scale4-optimal-carried-p0.15-k1", "pv-scale4-optimal"),
    ],
)
def test_pool_dir_candidates_normalises_derived_set_suffixes(pool, expected_member):
    assert expected_member in d.pool_dir_candidates("any-run", pool, None)


@pytest.mark.tier1
def test_pool_dir_candidates_keeps_the_literal_name_first():
    cands = d.pool_dir_candidates("pv-diag-384", "image-n5", "image-n5")
    assert cands[0] == "image-n5"


@pytest.mark.tier1
def test_register_pool_spec_tolerates_both_recorded_shapes():
    dec = {
        "old": {"proposer_pools": {"detect_brief-text": "text"}},
        "new": {"proposer_pools": {"image-t03": {"modality": "image", "path": "image-t03"}}},
        "by-path": {"proposer_pools": {"key": {"modality": "text", "path": "on-disk"}}},
    }
    assert d.register_pool_spec(dec, "old", "detect_brief-text")["modality"] == "text"
    assert d.register_pool_spec(dec, "new", "image-t03")["modality"] == "image"
    assert d.register_pool_spec(dec, "by-path", "on-disk")["modality"] == "text"
    assert d.register_pool_spec(dec, "new", "absent") == {}


@pytest.mark.tier1
def test_register_verifier_modality_needs_an_unambiguous_hit():
    dec = {"r": {"verifier_passes": {"verified-brief-image": "image",
                                     "verified-adversarial-text": "text"}}}
    assert d.register_verifier_modality(dec, "r", "verified-brief-image") == "image"
    assert d.register_verifier_modality(dec, "r", "something-else") is None


@pytest.mark.tier1
def test_mechanism_names_the_verifier_label_failure_shape():
    """Shape 1: the label's token names the VERIFIER, over a text proposer."""
    rec = {
        "proposer_pool": "detect_brief-text",
        "derived": {"modality": "text"},
        "recorded": {"label_token": "image", "register_verifier_modality": "image",
                     "register_pool_modality": None},
    }
    assert "VERIFIER" in d.mechanism_for(rec, "image")


@pytest.mark.tier1
def test_mechanism_names_the_no_token_fallthrough_failure_shape():
    """Shape 2: no modality token, so the substring test defaulted to text."""
    rec = {
        "proposer_pool": "scale-4-optimal-487",
        "derived": {"modality": "image"},
        "recorded": {"label_token": None, "register_verifier_modality": None,
                     "register_pool_modality": None},
    }
    assert "fell through" in d.mechanism_for(rec, "text")


@pytest.mark.tier1
def test_walk_for_modality_finds_nested_records():
    doc = {"best_per_size": {"512": {"single-pass/text": {
        "ref": "retest-phase2e::canonical-last", "modality": "text"}}},
        "other": [{"condition_id": "a::b", "track": "image"}],
        "ignored": {"label": "no-id-field", "modality": "text"}}
    found = dict((cid, value) for cid, _field, value in d.walk_for_modality(doc))
    assert found == {"retest-phase2e::canonical-last": "text", "a::b": "image"}


# ── tier 1: the verifier-stage modality convention (E88) ─────────────────

@pytest.mark.tier1
def test_verifier_modality_plan_targets_only_stages_that_disagree():
    """The planner moves a stage only when a derivable reading contradicts it.

    Covers all four cases the register contains: agreement (no entry), the
    ``image``-recorded stage over a ``verify_*-text`` config (the 51-stage
    majority), the ``text``-recorded stage over an exemplar-bearing verify
    config (the 4-stage minority), and the stage whose verify metadata no route
    can read, which keeps its recorded value rather than being guessed at.
    """
    rows = [
        {"run_id": "r", "stage": "agrees", "recorded": "text",
         "verifier_reading": "text", "verify_configs": ["verify_adversarial-text"]},
        {"run_id": "r", "stage": "track-reading-image", "recorded": "image",
         "verifier_reading": "text", "verify_configs": ["verify_adversarial-text"]},
        {"run_id": "r", "stage": "track-reading-text", "recorded": "text",
         "verifier_reading": "image", "verify_configs": ["verify_adversarial"]},
        {"run_id": "r", "stage": "underivable", "recorded": "image",
         "verifier_reading": None, "verify_configs": []},
    ]
    plan = d.plan_verifier_modality_fix(rows)
    assert [(e["stage"], e["before"], e["after"]) for e in plan] == [
        ("track-reading-image", "image", "text"),
        ("track-reading-text", "text", "image"),
    ]


@pytest.mark.tier1
def test_verifier_modality_plan_treats_text_plus_image_as_a_refinement():
    """``text+image`` recorded against an image-bearing verifier is not a move.

    ``comparable()`` folds the refinement onto the binary preregistered factor,
    so a stage recorded ``text+image`` over an exemplar-bearing verify config
    already carries the settled value.
    """
    rows = [{"run_id": "r", "stage": "s", "recorded": "text+image",
             "verifier_reading": "image", "verify_configs": ["verify_brief"]}]
    assert d.plan_verifier_modality_fix(rows) == []


@pytest.mark.tier1
def test_verifier_stage_modality_returns_none_for_an_unknown_stage():
    """A stage with no directory on disk yields no reading and no config list.

    The derivation never guesses: an unreadable stage returns ``None`` so the
    planner leaves the recorded value alone.
    """
    modality, configs = d.verifier_stage_modality(
        "no-such-run", "no-such-stage", {"path": "no/such/path"})
    assert (modality, configs) == (None, [])


def _verify_meta_file(path, version: str, n_examples: int) -> None:
    """Write a minimal verifier ``*.meta.json`` (configuration block only)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"configuration": {
        "version": version, "include_example_images": True,
        "full_config_snapshot": {"version": version,
                                 "examples": [{"path": "x.png"}] * n_examples}}}))


@pytest.mark.tier1
def test_a_sidecar_form_stage_resolves_from_the_passes_manifest(tmp_path, monkeypatch):
    """A stage whose meta sits beside the pools (``verified-*.meta.json``)
    has no stage directory; the passes manifest names its meta, and that is
    the route that reads it (W4.4)."""
    sidecar = tmp_path / "verified-brief-image.meta.json"
    _verify_meta_file(sidecar, "verify_brief", 6)
    monkeypatch.setattr(d, "_passes_index", lambda: {
        ("run-x", "verified-brief-image"): [
            {"provenance": {"source_files": [str(sidecar)]}}]})
    res = d.resolve_verifier_stage("run-x", "verified-brief-image", "image")
    assert res["resolved_by"] == ["passes-manifest"]
    assert d.modality_of(res["metas"]) == "image"
    assert res["unresolved_reason"] is None


@pytest.mark.tier1
def test_an_unresolvable_stage_carries_a_named_reason(tmp_path, monkeypatch):
    """Nothing is skipped silently: a manifest source absent on this machine
    (outputs on another host) is named in the reason."""
    monkeypatch.setattr(d, "_passes_index", lambda: {
        ("run-y", "verified"): [{"provenance": {"source_files": [
            "outputs/no-such-run/verified/run.meta.json"]}}]})
    monkeypatch.setattr(d, "git_renamed_to", lambda paths: ([], None))
    res = d.resolve_verifier_stage("run-y", "verified", {"path": "verified"})
    assert res["metas"] == [] and res["resolved_by"] == []
    assert "absent on this machine" in res["unresolved_reason"]
    assert "no git rename" in res["unresolved_reason"]


@pytest.mark.tier1
def test_git_renamed_to_follows_an_archived_leg(tmp_path, monkeypatch):
    """An archived leg keeps its bytes under ``archive/``; the registered
    path is followed through the commit that moved it (pv-diag-384
    ``verified-text-1of5``, archived in 8913cab2c, is the live case)."""
    import subprocess

    def git(*args: str) -> None:
        """Run git in the synthetic repository with a throwaway identity.

        Args:
            *args: The git subcommand and its arguments.
        """
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t",
                        *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    old = tmp_path / "outputs" / "run" / "verified" / "s" / "run.meta.json"
    _verify_meta_file(old, "verify_adversarial-text", 0)
    git("add", ".")
    git("commit", "-q", "-m", "stage")
    (tmp_path / "archive" / "superseded").mkdir(parents=True)
    git("mv", "outputs/run/verified/s", "archive/superseded/s")
    git("commit", "-q", "-m", "archive the stage")
    monkeypatch.setattr(d, "BASE_DIR", tmp_path)
    moved, commit = d.git_renamed_to(["outputs/run/verified/s"])
    assert moved == ["archive/superseded/s/run.meta.json"]
    assert commit
    # git_renames keeps each destination's original path (PR #25 review,
    # finding 6: a filter on where a file sat must read the OLD path).
    assert d.git_renames(["outputs/run/verified/s"]) == (
        [("outputs/run/verified/s/run.meta.json", "archive/superseded/s/run.meta.json")],
        commit)
    # SENTINEL: a path git never removed is not followed anywhere.
    assert d.git_renamed_to(["outputs/never/existed"]) == ([], None)
    assert d.git_renames(["outputs/never/existed"]) == ([], None)


# ── tier 2: corpus-wide agreement ────────────────────────────────────────

@pytest.mark.tier2
def test_derived_modality_agrees_with_the_register_for_every_condition():
    """The register's ``proposer_pools[...].modality`` must match what was sent.

    The register is hand-authored; this is the assertion that every one of
    its assertions is still true of the bytes on disk.
    """
    records, _pool_records = d.derive()
    offenders = [
        (r["condition_id"], r["recorded"]["register_pool_modality"],
         r["derived"]["modality"])
        for r in records
        if r["derived"]["modality"]
        and d.comparable(r["recorded"]["register_pool_modality"])
        and d.comparable(r["recorded"]["register_pool_modality"]) != r["derived"]["modality"]
    ]
    assert offenders == []


@pytest.mark.tier2
def test_no_derivation_route_contradicts_another():
    """Pass metadata, pool metadata and the config file must agree."""
    records, _ = d.derive()
    assert [r["condition_id"] for r in records if r["derived"]["routes_disagree"]] == []



@pytest.mark.tier2
def test_register_verifier_modality_is_the_verifier_stages_own_modality():
    """Every derivable verifier stage carries the convention settled 2026-09-14.

    The field records what the VERIFIER was sent, not the track it sits
    beneath (erratum E88). Stages whose verify metadata cannot be read are out
    of scope by construction — the planner skips them.
    """
    plan = d.plan_verifier_modality_fix(d.verifier_pass_audit())
    assert [(e["run_id"], e["stage"], e["before"], e["after"]) for e in plan] == []


#: Registered verifier stages the checker cannot resolve to their verify
#: metadata, each for a stated reason. Until S160 ``outputs/gs/`` was among
#: them unnamed, and a stage registered ``image`` that sent text labels
#: (gold-standard-v2 verified-v1) went unchecked (tracker C-18). S160 named
#: 17 more (13 + 2 sidecar-form metas under proposer-verifier-384/512, the
#: ``t0.3`` directory of ``55maps-text-high-t0-3-generalisation``, and the
#: archived pv-diag-384 ``verified-text-1of5``); W4.4 (2026-10-06) resolves
#: them from the passes manifest's own source files and, for the archived
#: leg, from git's record of where the files were moved. All 17 labels agree
#: with what the verifier was sent. The set is now empty and must stay so:
#: a stage added here needs a reason, as before.
UNRESOLVED_VERIFIER_STAGES: dict[tuple[str, str], str] = {}


@pytest.mark.tier2
def test_every_unresolved_verifier_stage_is_named():
    """A verifier stage the checker cannot read is out of its scope by
    construction, so the set must be named: a new blind spot turns this red
    rather than leaving a wrong label unchecked, as C-18 was."""
    unresolved = {(r["run_id"], r["stage"]) for r in d.verifier_pass_audit()
                  if r["verifier_reading"] is None}
    assert unresolved == set(UNRESOLVED_VERIFIER_STAGES)


@pytest.mark.tier2
def test_no_pool_keyed_label_disagrees_with_its_derivation():
    """Pool-keyed modality labels in generated outputs (the K-ladder unions
    and ladders among them) match what the pool sent. The K-ladder Phase 2
    unions carried a stale 'text' for an image pool until S160 (C-22), its
    builder corrected on 2026-09-14 but its output never regenerated."""
    _records, pool_records = d.derive()
    assert [r for r in pool_records if r["mismatch"]] == []
