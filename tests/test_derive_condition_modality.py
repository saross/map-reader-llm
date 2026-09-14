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
