"""
Tests for ``scripts/check_manipulation.py`` (tracker W6.1).

The guard refuses an analysis whose arms differ in configuration but not in
the transmitted signature (a null manipulation). The synthetic tests write
pairs of minimal pass metas and judge them:

- two text-only arms listing different libraries → identical signatures →
  REFUSE (the Phase 2c text-track shape, erratum E90);
- the same pair with images on in one arm → signatures differ → PASS;
- a replicate of one configuration → PASS (identical configuration);
- one configuration on two different tile sets → PASS (different inputs);
- an arm with no readable metadata → UNVERIFIABLE, or out of scope with the
  opt-out.

One test runs the CLI on a registered analysis and pins the 2026-10-05
finding: the Era-1 single-pass matrix carries the Phase 2c text replicates.
Another pins the replicate pair inside ``verifier-uplift-pairing``
(h10 pool_160 and h8-v2 scale-8) as an expected, documented refusal, and
synthetic tests pin the known-refusal allow-list and the ``--all`` exit rule
(PR #24 review, finding 1).

Tiers: the synthetic tests write their metas to ``tmp_path`` and run in
well under a second, so they are tier 1 (the per-commit gate); the tests
that read the committed register and metas are tier 2.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import check_manipulation as cm
from scripts import lib_manipulation_signature as sig

_LIBRARY_A = [{"path": f"neutral-naming/example_{i:02d}.png", "label": "Positive",
               "category": "canonical_positive"} for i in range(1, 10)]
_LIBRARY_B = _LIBRARY_A[:7]


def _meta(path: Path, version: str, examples: list[dict], include_images: bool,
          tiles: list[str] | None = None, temperature: float = 0.0) -> str:
    """Write a minimal proposer pass meta in the pipeline's shape.

    Args:
        path: Where to write it.
        version: The configuration version.
        examples: The listed example library.
        include_images: ``include_example_images``.
        tiles: The dispatched tile ids (completed items).
        temperature: The configured temperature.

    Returns:
        The path, as a string.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "environment": {"script": "4_detect_mounds_batch.py", "git_commit": "abc"},
        "configuration": {
            "version": version, "model": "gemini-3-flash-preview",
            "instruction_file": "detect_brief-text.md",
            "system_instruction_hash": "e169b7237b853eeaad990fc2e54f",
            "temperature": temperature, "thinking_level": "minimal",
            "max_output_tokens": 8192, "tile_size": None,
            "include_example_images": include_images,
            "full_config_snapshot": {"version": version, "examples": examples,
                                     "include_example_images": include_images},
        },
        "execution_stats": {"items_processed": len(tiles or ["t1.png"]),
                            "completed_items": tiles or ["t1.png", "t2.png"],
                            "failed_items": []},
        "usage_stats": {},
    }))
    return str(path)


@pytest.mark.tier1
def test_identical_requests_under_different_configurations_refuse(tmp_path) -> None:
    """Two text-only arms with different listed libraries sent the same
    request: the analysis compares replicates, and the guard refuses."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "library_a-text",
                                      _LIBRARY_A, include_images=False)])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "library_b-text",
                                      _LIBRARY_B, include_images=False)])
    judgement = cm.judge([a, b])
    assert judgement["verdict"] == cm.REFUSE
    (pair,) = judgement["null_pairs"]
    assert pair["arms"] == ["A", "B"]
    assert pair["config_fields_differing"] == ["listed_library", "version"]


@pytest.mark.tier1
def test_a_recovery_fragment_does_not_hide_a_null_manipulation(tmp_path) -> None:
    """A recovery fragment re-sends a few of its pass's tiles; the arm's
    inputs are the union over its passes, so a fragment in one arm and not
    the other does not make two identical requests look different."""
    tiles = ["x0_y0.png", "x1_y0.png", "x2_y0.png"]
    a = cm.arm_from_metas("A", [
        _meta(tmp_path / "a" / "run_1.meta.json", "library_a-text", _LIBRARY_A, False,
              tiles=tiles[:2]),
        _meta(tmp_path / "a" / "run_1_recovery.meta.json", "library_a-text", _LIBRARY_A,
              False, tiles=tiles[2:])])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "library_b-text",
                                      _LIBRARY_B, False, tiles=tiles)])
    assert cm.judge([a, b])["verdict"] == cm.REFUSE


@pytest.mark.tier1
def test_a_manipulation_that_reached_the_request_passes(tmp_path) -> None:
    """With images on, the library reaches the request: the signatures
    differ and the analysis passes."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "library_a",
                                      _LIBRARY_A, include_images=True)])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "library_b",
                                      _LIBRARY_B, include_images=True)])
    assert a["signature"] != b["signature"]
    assert cm.judge([a, b])["verdict"] == cm.PASS


@pytest.mark.tier1
def test_a_replicate_of_one_configuration_passes(tmp_path) -> None:
    """Identical configuration and identical request: a replicate, not a
    null manipulation (e.g. two aggregations of one pool)."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "library_a-text",
                                      _LIBRARY_A, include_images=False)])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "library_a-text",
                                      _LIBRARY_A, include_images=False)])
    assert cm.judge([a, b])["verdict"] == cm.PASS


@pytest.mark.tier1
def test_different_inputs_are_different_requests(tmp_path) -> None:
    """One configuration on two tile sets sent different tiles: not a null
    manipulation, even when the version names differ."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "v-384", _LIBRARY_A,
                                      False, tiles=["x0_y0.png", "x1_y0.png"])])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "v-512", _LIBRARY_A,
                                      False, tiles=["x0_y0.png"])])
    assert cm.judge([a, b])["verdict"] == cm.PASS


@pytest.mark.tier1
def test_a_configured_temperature_that_was_sent_passes(tmp_path) -> None:
    """A temperature manipulation reaches the request (temperature_eff)."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "v", _LIBRARY_A,
                                      False, temperature=0.0)])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "v", _LIBRARY_A,
                                      False, temperature=0.7)])
    assert cm.judge([a, b])["verdict"] == cm.PASS


@pytest.mark.tier1
def test_an_arm_without_metadata_is_unverifiable_not_passed(tmp_path) -> None:
    """No readable meta is a named absence: UNVERIFIABLE unless allowed."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "v", _LIBRARY_A, False)])
    b = cm.arm_from_metas("B", [str(tmp_path / "absent.meta.json")])
    judgement = cm.judge([a, b])
    assert judgement["verdict"] == cm.UNVERIFIABLE
    assert judgement["unverifiable"][0]["arm"] == "B"
    assert cm.judge([a, b], allow_unverifiable=True)["verdict"] == cm.PASS


_VERIFIER_V1 = {"variant": "v1", "instruction_file": "verify_adversarial.md",
                "model": "gemini-3-flash-preview", "thinking_level": "minimal",
                "temperature": 0.0}
_VERIFIER_V2 = {**_VERIFIER_V1, "variant": "v2", "instruction_file": "verify_v2.md"}


def _verifier_meta(path: Path, candidates: list[str]) -> str:
    """Write a minimal verifier stage meta (``run_pv.py``) in the pipeline's shape.

    Args:
        path: Where to write it.
        candidates: The verified candidate ids (completed items).

    Returns:
        The path, as a string.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "environment": {"script": "run_pv.py", "git_commit": "abc"},
        "configuration": {
            "version": "verify_adversarial", "model": "gemini-3-flash-preview",
            "system_instruction_hash": "2518d5298d9bffff", "temperature": 0.0,
            "thinking_level": "minimal", "max_output_tokens": 8192,
            "full_config_snapshot": {"version": "verify_adversarial",
                                     "text_only_labels": ["a", "b"]},
        },
        "execution_stats": {"completed_items": candidates, "failed_items": []},
        "usage_stats": {},
    }))
    return str(path)


@pytest.mark.tier1
def test_a_declared_verifier_difference_is_not_a_transmitted_one(tmp_path) -> None:
    """PR #24 review, finding 2: two arms of one proposer request whose only
    difference is a DECLARED verifier configuration did not pass as
    "differ in transmission"; they are an unverifiable pair."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "v", _LIBRARY_A, True)],
                          declared_verifier=_VERIFIER_V1)
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "v", _LIBRARY_A, True)],
                          declared_verifier=_VERIFIER_V2)
    assert a["config"] != b["config"]
    assert a["signature"] == b["signature"]  # the declared dict is not transmitted
    assert cm.transmission_relation(a, b) == cm.UNDETERMINED
    judgement = cm.judge([a, b])
    assert judgement["verdict"] == cm.UNVERIFIABLE
    assert judgement["null_pairs"] == []
    (pair,) = judgement["undetermined_pairs"]
    assert pair["arms"] == ["A", "B"]
    assert pair["config_fields_differing"] == ["instruction_file", "variant"]
    assert cm.judge([a, b], allow_unverifiable=True)["verdict"] == cm.PASS


@pytest.mark.tier1
def test_a_declared_and_a_transmitted_verifier_cannot_be_compared(tmp_path) -> None:
    """One arm's verifier metas were read, the other's only declared: the
    verifier half cannot show a difference either way."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "v", _LIBRARY_A, True)],
                          verifier_metas=[_verifier_meta(tmp_path / "av" / "run.meta.json",
                                                         ["c1", "c2"])])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "v", _LIBRARY_A, True)],
                          declared_verifier=_VERIFIER_V1)
    assert (a["verifier_basis"], b["verifier_basis"]) == ("transmitted", "declared")
    judgement = cm.judge([a, b])
    assert judgement["verdict"] == cm.UNVERIFIABLE
    assert [p["arms"] for p in judgement["undetermined_pairs"]] == [["A", "B"]]


@pytest.mark.tier1
@pytest.mark.parametrize(("images", "verifiers", "verdict"), [
    (False, (_VERIFIER_V1, _VERIFIER_V1), cm.REFUSE),  # equal declared: the proposer decides
    (True, (_VERIFIER_V1, _VERIFIER_V2), cm.PASS),     # the proposer requests differ
    (False, (_VERIFIER_V1, None), cm.PASS),            # only one arm has a verifier stage
])
def test_the_proposer_half_decides_beside_a_declared_verifier(tmp_path, images, verifiers,
                                                              verdict) -> None:
    """Two listed libraries (sent only with images on) beside declared
    verifiers: identical declared configurations leave the text-track null
    manipulation refused; transmitted proposer differences still pass; a
    proposer-verifier arm and a single-pass arm sent different requests."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "library_a", _LIBRARY_A,
                                      images)], declared_verifier=verifiers[0])
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "library_b", _LIBRARY_B,
                                      images)], declared_verifier=verifiers[1])
    judgement = cm.judge([a, b])
    assert judgement["verdict"] == verdict
    assert judgement["undetermined_pairs"] == []


@pytest.mark.tier1
def test_the_render_note_says_what_the_declared_configuration_did(tmp_path) -> None:
    """The note no longer claims a declared configuration can separate arms."""
    a = cm.arm_from_metas("A", [_meta(tmp_path / "a.meta.json", "v", _LIBRARY_A, True)],
                          declared_verifier=_VERIFIER_V1)
    b = cm.arm_from_metas("B", [_meta(tmp_path / "b.meta.json", "v", _LIBRARY_A, True)],
                          declared_verifier=_VERIFIER_V2)
    out = cm.render("ad hoc", cm.judge([a, b]), [a, b], report=False)
    assert out.startswith("UNVERIFIABLE ad hoc: 2 arm(s), 0 null-manipulation pair(s), "
                          "0 unverifiable arm(s), 1 unverifiable pair(s)")
    assert "UNVERIFIABLE PAIR: A vs B sent identical proposer requests" in out
    assert "2 arm(s) carry only a DECLARED verifier configuration" in out
    assert "separated no pair" in out
    assert "can separate arms" not in out


@pytest.mark.tier1
def test_the_signature_carries_exactly_the_shared_fields(tmp_path) -> None:
    """The signature is the definition shared with map-reader-bench:
    its keys are SIGNATURE_FIELDS, no more and no fewer."""
    rec = cm.meta_record(_meta(tmp_path / "a.meta.json", "v", _LIBRARY_A, True))
    assert tuple(sig.signature(rec)) == sig.SIGNATURE_FIELDS
    assert tuple(cm.configuration_identity(rec)) == cm.CONFIG_FIELDS


@pytest.mark.tier2
def test_the_registered_era1_matrix_is_refused(capsys) -> None:
    """The 2026-10-05 finding, pinned: the Era-1 single-pass matrix compares
    the retest's Phase 2c text arms (five libraries, one request) and the
    Phase 2b image arm with its 2c scale-8 twin."""
    assert cm.main(["era1-single-pass-baseline-matrix"]) == 2
    out = capsys.readouterr().out
    assert out.startswith("REFUSE era1-single-pass-baseline-matrix")
    assert "retest-phase2c::text-canonical vs retest-phase2c::text-plus-hp" in out
    assert "retest-phase2b::image-t0.0 vs retest-phase2c::image-scale-8" in out


# ── documented null manipulations and the --all exit rule (finding 1) ────

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.tier1
def test_every_known_null_manipulation_cites_documents_that_exist() -> None:
    """Each allow-list group joins at least two pools and names committed
    documents, the first of which leads its ``documented_by`` text."""
    for group in cm.KNOWN_NULL_MANIPULATIONS:
        assert len(group["pools"]) >= 2
        assert all((REPO / doc).is_file() for doc in group["documents"])
        assert group["documented_by"].startswith(group["documents"][0])


def _registered(monkeypatch, tmp_path, analyses: dict[str, list[str]],
                pools: dict[str, tuple[str, str]],
                configs: dict[str, tuple[str, list, float]]) -> None:
    """Stand in a synthetic register for the gate's register readers.

    Args:
        monkeypatch: pytest's fixture.
        tmp_path: Where the arms' metas are written.
        analyses: Analysis id -> condition ids.
        pools: Condition id -> ``(run_id, proposer_pool)``.
        configs: Condition id -> ``(version, examples, temperature)`` of a
            text-only pass, or ``("absent", [], 0.0)`` for an arm with no
            readable meta.
    """
    monkeypatch.setattr(cm, "_analyses", lambda: {
        a: {"conditions_compared": c} for a, c in analyses.items()})
    monkeypatch.setattr(cm, "_conditions", lambda: {
        c: {"condition_id": c, "run_id": r, "proposer_pool": p}
        for c, (r, p) in pools.items()})

    def arm(cid: str) -> dict:
        version, examples, temperature = configs[cid]
        path = tmp_path / f"{cid.replace(':', '_')}.meta.json"
        if version != "absent":
            _meta(path, version, examples, include_images=False, temperature=temperature)
        return cm.arm_from_metas(cid, [str(path)])

    monkeypatch.setattr(cm, "arm_for_condition", arm)
    monkeypatch.setattr(cm, "KNOWN_NULL_MANIPULATIONS", (
        {"pools": frozenset({("r1", "lib-a"), ("r1", "lib-b")}),
         "documents": ("reports/x.md",), "documented_by": "reports/x.md § 1"},))


@pytest.mark.tier1
def test_a_null_pair_is_known_only_inside_one_documented_group(monkeypatch, tmp_path) -> None:
    """Both arms' pools in one group: KNOWN; otherwise, or unregistered: NEW."""
    _registered(monkeypatch, tmp_path, {}, {"r1::a": ("r1", "lib-a"), "r1::b": ("r1", "lib-b"),
                                            "r2::c": ("r2", "lib-c")}, {})
    assert cm.documented_null_pair("r1::a", "r1::b") == "reports/x.md § 1"
    assert cm.documented_null_pair("r1::a", "r2::c") is None
    assert cm.documented_null_pair("r1::a", "ad-hoc::z") is None


@pytest.mark.tier1
@pytest.mark.parametrize(("extra", "flags", "status", "line"), [
    ({}, [], 0, "  KNOWN REFUSAL known: all 1 null pair(s) documented (reports/x.md § 1)"),
    ({"new": ["r2::c", "r2::d"]}, [], 2, "  NEW REFUSAL new: 1 of 1 null pair(s)"),
    ({"gap": ["r2::c", "r9::absent"]}, [], 3, "  exit 3: every refusal is documented"),
    ({"gap": ["r2::c", "r9::absent"]}, ["--allow-unverifiable"], 0, "  exit 0:"),
])
def test_all_fails_only_on_an_undocumented_refusal(monkeypatch, tmp_path, capsys, extra,
                                                   flags, status, line) -> None:
    """``--all`` lists each refusal as KNOWN or NEW and exits 2 only for a
    NEW one; a documented refusal alone exits 0, or 3 beside an
    unverifiable analysis unless that is allowed."""
    analyses = {"known": ["r1::a", "r1::b"], "clean": ["r1::a", "r2::c"], **extra}
    pools = {"r1::a": ("r1", "lib-a"), "r1::b": ("r1", "lib-b"), "r2::c": ("r2", "lib-c"),
             "r2::d": ("r2", "lib-d"), "r9::absent": ("r9", "none")}
    configs = {"r1::a": ("library_a-text", _LIBRARY_A, 0.0),
               "r1::b": ("library_b-text", _LIBRARY_B, 0.0),
               "r2::c": ("v-c", [], 0.7), "r2::d": ("v-d", [], 0.7),
               "r9::absent": ("absent", [], 0.0)}
    # r1::a and r1::b list different libraries with images off: the KNOWN
    # pair. r2::c and r2::d differ only in a version name: a null pair no
    # document records. r2's temperature separates "clean" in transmission.
    _registered(monkeypatch, tmp_path, analyses, pools, configs)
    assert cm.main(["--all", *flags]) == status
    out = capsys.readouterr().out
    assert "REFUSE known:" in out and "[KNOWN: reports/x.md § 1]" in out
    assert any(o.startswith(line) for o in out.splitlines())


@pytest.mark.tier2
def test_the_h8_h10_replicate_pair_is_a_known_refusal(capsys) -> None:
    """``verifier-uplift-pairing`` pairs h10::verified-pool-160 with
    h8-v2::verified-wbf-scale-8: two executions of one configuration
    (``reports/manipulation-check-2026-10-05.md`` § B.5 group 10). The gate
    refuses the pair, as it should, and labels it documented."""
    assert cm.main(["--conditions", "h10::verified-pool-160",
                    "h8-v2::verified-wbf-scale-8"]) == 2
    out = capsys.readouterr().out
    assert ("NULL MANIPULATION: h10::verified-pool-160 vs h8-v2::verified-wbf-scale-8 "
            "differ in configuration (version)") in out
    assert "[KNOWN: reports/manipulation-check-2026-10-05.md § B.5 group 10" in out
