"""
Tests for the manipulation gate's reviewed bindings (gate coverage, 2026-10-06).

``scripts/check_manipulation.py`` resolves each registered arm to the pass
metas of the requests that produced it. Where the register names only a
DERIVED product (a re-score, a materialised operating point, a ladder rung, a
union of passes), ``results/manipulation-gate-bindings.json`` records the
sources the product's documented derivation read, and the gate follows each
source mechanically. These tests build a synthetic repository under
``tmp_path`` (register, passes manifest, metas, bindings file) and pin:

- a derived product followed to the registered stage whose directory holds
  its source (and to the longest such stage, across runs);
- a verifier source outside every registered stage read from its own
  directory, and a proposer source read through the passes manifest or the
  directory on disk;
- the register's own routes taking precedence over a binding;
- a binding whose source resolves nothing left visible, never silent;
- the bindings file's validation (unregistered condition, drifted
  detections, missing evidence, a condition bound twice, verifier sources on
  a single-pass condition) stopping the gate with exit 1;
- a refusal still firing when two bound arms sent identical requests, labelled
  NEW unless an allow-listed group documents it.

Tiers: every test here is synthetic and runs in well under a second (tier 1).
The committed bindings file's agreement with the register is checked in
``tests/test_check_manipulation.py`` (tier 2, it reads the registers).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scripts import check_manipulation as cm
from scripts import derive_condition_modality as dcm

pytestmark = pytest.mark.tier1

RUN = "run1"
_CACHED = (cm._stage_dirs, cm._manifest_sources, cm._bindings, cm.meta_record,
           cm.stage_metas, dcm.load_meta_json, dcm.pool_output_dir)


def _clear_caches() -> None:
    """Drop every cache the gate keeps over the synthetic repository."""
    for fn in _CACHED:
        fn.cache_clear()


def _write(root: Path, rel: str, doc: Any) -> str:
    """Write a JSON document under the synthetic repository.

    Args:
        root: The synthetic repository root.
        rel: Repository-relative path.
        doc: The JSON value.

    Returns:
        ``rel``.
    """
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc))
    return rel


def _proposer_meta(version: str = "detect_x-text", examples: int = 3) -> dict[str, Any]:
    """A minimal text-only proposer meta (images off: the library is not sent).

    Args:
        version: The configuration version.
        examples: How many examples the configuration LISTS.

    Returns:
        The meta document.
    """
    library = [{"path": f"ex_{i}.png", "label": "Positive"} for i in range(examples)]
    return {"environment": {"script": "4_detect_mounds_batch.py"},
            "configuration": {"version": version, "model": "gemini-3-flash-preview",
                              "system_instruction_hash": "aaaaaaaaaaaaffff",
                              "temperature": 0.7, "thinking_level": "minimal",
                              "include_example_images": False,
                              "full_config_snapshot": {"version": version,
                                                       "examples": library,
                                                       "include_example_images": False}},
            "execution_stats": {"completed_items": ["t1.png", "t2.png"], "failed_items": []}}


def _verifier_meta(version: str = "verify_adversarial-text", temperature: float = 0.0,
                   sys_hash: str = "bbbbbbbbbbbbffff") -> dict[str, Any]:
    """A minimal verifier stage meta (``run_pv.py``), text labels only.

    Args:
        version: The verify configuration version.
        temperature: The verifier temperature.
        sys_hash: The system-instruction hash.

    Returns:
        The meta document.
    """
    return {"environment": {"script": "run_pv.py"},
            "configuration": {"version": version, "model": "gemini-3-flash-preview",
                              "system_instruction_hash": sys_hash,
                              "temperature": temperature, "thinking_level": "minimal",
                              "full_config_snapshot": {"version": version,
                                                       "text_only_labels": ["a", "b"]}},
            "execution_stats": {"completed_items": ["c1", "c2"], "failed_items": []}}


_DECLARED = {"variant": "v1", "instruction_file": "verify_adversarial.md",
             "model": "gemini-3-flash-preview", "thinking_level": "minimal",
             "temperature": 0.0}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A synthetic repository with one run, one pool and four verifier stages.

    Layout: the pool ``pool`` (one pass, in the passes manifest), stages
    ``pool-verify-a`` and ``pool-verify-b`` (in the passes manifest),
    ``pool-verify-a-deep`` (a sub-directory of ``verify_a``, on disk only)
    and ``pool-verify-c`` (in the passes manifest, but its one meta on disk
    is corrupt and the other is absent), an unregistered verifier directory
    ``loose/``, an unregistered proposer pass directory ``other-pool/run_1``,
    and four conditions whose detections are derived products under
    ``results/cells/``.

    Returns:
        A namespace dict: ``root``, ``meta``, ``conditions``,
        ``decomposition``, ``passes`` (the passes-manifest index; mutate it
        and call :func:`_clear_caches`) and ``write_bindings`` (a function
        writing the bindings file).
    """
    _clear_caches()
    monkeypatch.setattr(cm, "BASE_DIR", tmp_path)
    monkeypatch.setattr(dcm, "BASE_DIR", tmp_path)
    corrupt = f"outputs/{RUN}/verifier/pool/verify_c/run.meta.json"
    (tmp_path / corrupt).parent.mkdir(parents=True)
    (tmp_path / corrupt).write_text("{not json")
    meta = {
        "pool": _write(tmp_path, f"outputs/{RUN}/pool/run_1/d.meta.json", _proposer_meta()),
        "a": _write(tmp_path, f"outputs/{RUN}/verifier/pool/verify_a/run.meta.json",
                    _verifier_meta()),
        "b": _write(tmp_path, f"outputs/{RUN}/verifier/pool/verify_b/run.meta.json",
                    _verifier_meta(temperature=0.7)),
        "deep": _write(tmp_path, f"outputs/{RUN}/verifier/pool/verify_a/deep/run.meta.json",
                       _verifier_meta(temperature=1.0)),
        "loose": _write(tmp_path, "outputs/loose/run.meta.json", _verifier_meta(temperature=0.3)),
        "other": _write(tmp_path, "outputs/other-pool/run_1/d.meta.json",
                        _proposer_meta("detect_y-text")),
    }
    decomposition = {RUN: {
        # Two pools, so the gate's sole-pool route cannot bind a stray condition.
        "proposer_pools": {"pool": {"path": "pool"}, "pool2": {"path": "pool2"}},
        "verifier_passes": {"pool-verify-a": {"path": "verifier/pool/verify_a"},
                            "pool-verify-b": {"path": "verifier/pool/verify_b"},
                            "pool-verify-a-deep": {"path": "verifier/pool/verify_a/deep"},
                            "pool-verify-c": {"path": "verifier/pool/verify_c"}},
        "conditions": [{"label": lab, "detections": f"results/cells/{lab}/detections.geojson"}
                       for lab in ("cell-a", "cell-b", "cell-c", "single")]
        + [{"label": "pool-verify-b-k5", "detections": "results/cells/x/detections.geojson"},
           {"label": "pool-verify-c-k5", "detections": "results/cells/y/detections.geojson"},
           {"label": "orphan", "detections": "results/cells/orphan/detections.geojson"}]}}
    conditions = {f"{RUN}::{lab}": {"condition_id": f"{RUN}::{lab}", "run_id": RUN, "label": lab,
                                    "architecture": "proposer-verifier", "proposer_pool": "pool",
                                    "verifier_config": _DECLARED}
                  for lab in ("cell-a", "cell-b", "cell-c", "pool-verify-b-k5",
                              "pool-verify-c-k5")}
    conditions[f"{RUN}::single"] = {"condition_id": f"{RUN}::single", "run_id": RUN,
                                    "label": "single", "architecture": "single-pass",
                                    "proposer_pool": "pool"}
    conditions[f"{RUN}::orphan"] = {"condition_id": f"{RUN}::orphan", "run_id": RUN,
                                    "label": "orphan", "architecture": "proposer-verifier",
                                    "proposer_pool": "unregistered-union",
                                    "verifier_config": _DECLARED}
    passes = {(RUN, "pool"): [{"provenance": {"source_files": [meta["pool"]]}}],
              (RUN, "pool-verify-a"): [{"provenance": {"source_files": [meta["a"]]}}],
              (RUN, "pool-verify-b"): [{"provenance": {"source_files": [meta["b"]]}}],
              (RUN, "pool-verify-c"): [{"provenance": {"source_files": [
                  corrupt, f"outputs/{RUN}/verifier/pool/verify_c/absent.meta.json"]}}]}
    monkeypatch.setattr(cm, "_conditions", lambda: conditions)
    monkeypatch.setattr(dcm, "_decomposition", lambda: decomposition)
    monkeypatch.setattr(dcm, "_passes_index", lambda: passes)

    def write_bindings(entries: list[dict[str, Any]]) -> None:
        """Write the bindings file and drop the gate's cached copy.

        Args:
            entries: The ``bindings`` list.
        """
        _write(tmp_path, cm.BINDINGS, {"schema_version": cm.BINDINGS_SCHEMA,
                                       "bindings": entries})
        _clear_caches()

    yield {"root": tmp_path, "meta": meta, "conditions": conditions,
           "decomposition": decomposition, "passes": passes,
           "write_bindings": write_bindings}
    _clear_caches()


def _entry(name: str, labels: list[str], **sources: list[str]) -> dict[str, Any]:
    """A well-formed binding entry for synthetic conditions.

    Args:
        name: The binding id.
        labels: Condition labels in :data:`RUN`.
        **sources: ``verifier_sources`` and/or ``proposer_sources``.

    Returns:
        The entry.
    """
    return {"id": name, "conditions": [f"{RUN}::{lab}" for lab in labels],
            "detections": [f"results/cells/{lab}/detections.geojson" for lab in labels],
            **sources,
            "evidence": {"derivation": "materialised from the stage's probabilities",
                         "script": "scripts/build.py:10-12", "product_commit": "abc1234"}}


def test_a_derived_product_is_followed_to_the_stage_holding_its_source(repo) -> None:
    """The bound source lies in stage ``pool-verify-a``'s directory: the
    arm's verifier half is that stage's TRANSMITTED metas, not the declared
    configuration."""
    arm_before = cm.arm_for_condition(f"{RUN}::cell-a")
    assert arm_before["verifier_basis"] == "declared"
    repo["write_bindings"]([_entry("cells-a", ["cell-a"], verifier_sources=[
        f"outputs/{RUN}/verifier/pool/verify_a/probabilities.json"])])
    arm = cm.arm_for_condition(f"{RUN}::cell-a")
    assert arm["verifier_basis"] == "transmitted"
    assert arm["verifier_stage"] == {"stage": f"{RUN}/pool-verify-a", "how": "binding:cells-a"}
    assert repo["meta"]["a"] in arm["meta_paths"]
    assert arm["binding"] == "cells-a"


def test_the_longest_registered_stage_directory_wins(repo) -> None:
    """A source inside a nested stage resolves to the nested stage only."""
    deep = f"outputs/{RUN}/verifier/pool/verify_a/deep/probabilities.json"
    assert cm.stages_containing(deep) == [(RUN, "pool-verify-a-deep")]
    assert cm.stages_containing(f"outputs/{RUN}/verifier/pool/verify_a") == [
        (RUN, "pool-verify-a")]
    assert cm.stages_containing(f"outputs/{RUN}/verifier/pool/verify_ab/x.json") == []


def test_a_source_outside_every_stage_is_read_from_its_directory(repo) -> None:
    """An unregistered verifier directory: its own verify metas are read,
    from the directory or from beside an existing file; a source that does
    not exist is never widened to its parent."""
    expected = ([repo["meta"]["loose"]], "source-directory")
    assert cm.verifier_metas_for_source("outputs/loose") == expected
    assert cm.verifier_metas_for_source("outputs/loose/probabilities.json") == ([], None)
    _write(repo["root"], "outputs/loose/probabilities.json", {})
    assert cm.verifier_metas_for_source("outputs/loose/probabilities.json") == expected


def test_a_proposer_source_resolves_by_manifest_then_disk(repo) -> None:
    """A pass directory the passes manifest records resolves through it; one
    it does not record is read from disk."""
    assert cm.proposer_metas_for_source(f"outputs/{RUN}/pool") == (
        [repo["meta"]["pool"]], f"passes-manifest:{RUN}/pool")
    assert cm.proposer_metas_for_source("outputs/other-pool") == (
        [repo["meta"]["other"]], "source-directory")
    assert cm.proposer_metas_for_source("outputs/absent") == ([], None)


def test_an_unbound_proposer_is_bound_by_its_sources(repo) -> None:
    """A condition whose proposer pool the register does not hold is
    unverifiable until a binding names its pass directories."""
    assert cm.arm_for_condition(f"{RUN}::orphan")["unverifiable_reason"]
    repo["write_bindings"]([_entry("orphan-union", ["orphan"],
                                   proposer_sources=["outputs/other-pool"],
                                   verifier_sources=["outputs/loose"])])
    arm = cm.arm_for_condition(f"{RUN}::orphan")
    assert arm["unverifiable_reason"] is None
    assert arm["proposer_route"] == "binding:orphan-union:source-directory"
    assert arm["verifier_basis"] == "transmitted"


def test_the_register_outranks_a_binding(repo) -> None:
    """The label names stage ``pool-verify-b``: a binding pointing elsewhere
    is not consulted (and the arm does not claim it)."""
    repo["write_bindings"]([{**_entry("wrong", ["cell-a"]),
                             "conditions": [f"{RUN}::pool-verify-b-k5"],
                             "detections": ["results/cells/x/detections.geojson"],
                             "verifier_sources": [f"outputs/{RUN}/verifier/pool/verify_a"]}])
    arm = cm.arm_for_condition(f"{RUN}::pool-verify-b-k5")
    assert arm["verifier_stage"] == {"stage": "pool-verify-b", "how": "label"}
    assert arm["meta_paths"][-1] == repo["meta"]["b"]
    assert arm["binding"] is None


def test_a_dead_source_is_named_not_silently_skipped(repo, capsys) -> None:
    """A bound source that resolves nothing leaves the half UNVERIFIABLE
    (not declared: the reviewed binding says where the requests are, and
    they cannot be read) and prints a BINDING GAP line."""
    repo["write_bindings"]([_entry("dead", ["cell-a"], verifier_sources=["outputs/nowhere"])])
    arm = cm.arm_for_condition(f"{RUN}::cell-a")
    assert arm["verifier_basis"] == "unverifiable"
    assert arm["verifier_unverifiable_reason"] == (
        "binding dead: verifier source(s) resolved no meta: outputs/nowhere")
    assert arm["verifier_stage"] == {"stage": "outputs/nowhere (unregistered)",
                                     "how": "binding:dead"}
    assert arm["binding"] is None
    assert arm["binding_notes"] == [
        "binding dead: verifier source(s) resolved no meta: outputs/nowhere"]
    out = cm.render("ad hoc", cm.judge([arm]), [arm], report=False)
    assert "BINDING GAP: run1::cell-a: binding dead" in out


# ── PR #25 review, finding 2: a partly resolved binding is not used ─────

def test_one_dead_verifier_source_voids_the_half(repo) -> None:
    """Two verifier sources, one live (stage ``pool-verify-a``) and one
    dead: the live stage's metas are NOT the arm's verifier half (they are
    not all of its requests). The half is UNVERIFIABLE, the gap is named,
    and the binding is not claimed; beside a transmitted arm of the same
    proposer request the pair is unverifiable, where it used to PASS."""
    repo["write_bindings"]([_entry("half", ["cell-a"], verifier_sources=[
        f"outputs/{RUN}/verifier/pool/verify_a/probabilities.json", "outputs/nowhere"])])
    arm = cm.arm_for_condition(f"{RUN}::cell-a")
    assert arm["verifier_basis"] == "unverifiable"
    assert repo["meta"]["a"] not in arm["meta_paths"]
    assert arm["verifier_metas_set_aside"] == []
    assert arm["verifier_stage"]["stage"] == (
        f"{RUN}/pool-verify-a|outputs/nowhere (unregistered)")
    assert arm["binding"] is None
    assert arm["binding_notes"] == [
        "binding half: verifier source(s) resolved no meta: outputs/nowhere (the other "
        "sources are not read as the whole stage set)"]
    judgement, _arms = cm.check_conditions([f"{RUN}::cell-a", f"{RUN}::pool-verify-b-k5"])
    assert judgement["verdict"] == cm.UNVERIFIABLE
    assert judgement["undetermined_pairs"]


def test_one_dead_proposer_source_voids_the_arm(repo) -> None:
    """A proposer half bound to two pass directories, one of which resolves
    nothing: the arm is UNVERIFIABLE with the dead source named, not judged
    on the one pass that was found."""
    repo["write_bindings"]([_entry("union", ["orphan"], proposer_sources=[
        "outputs/other-pool", "outputs/absent-pass"], verifier_sources=["outputs/loose"])])
    arm = cm.arm_for_condition(f"{RUN}::orphan")
    assert repo["meta"]["other"] not in arm["meta_paths"]
    assert "binding union: proposer source(s) resolved no meta: outputs/absent-pass" in (
        arm["unverifiable_reason"])
    assert cm.judge([arm])["verdict"] == cm.UNVERIFIABLE


# ── PR #25 review, finding 1: listed but unreadable verifier metas ──────

def test_a_register_stage_with_no_readable_meta_is_unverifiable_not_absent(repo) -> None:
    """The label names stage ``pool-verify-c``, whose manifest metas are one
    corrupt and one absent. The verifier half is UNVERIFIABLE (named), not
    "no verifier stage"; beside a transmitted arm of the same proposer
    request the pair is unverifiable, where it used to PASS as "differ in
    transmission"."""
    arm = cm.arm_for_condition(f"{RUN}::pool-verify-c-k5")
    assert arm["verifier_stage"] == {"stage": "pool-verify-c", "how": "label"}
    assert arm["verifier_basis"] == "unverifiable"
    assert "2 verifier meta(s) listed, none readable" in arm["verifier_unverifiable_reason"]
    assert arm["unverifiable_reason"] is None  # the proposer half is readable
    judgement, _arms = cm.check_conditions([f"{RUN}::pool-verify-b-k5",
                                            f"{RUN}::pool-verify-c-k5"])
    assert judgement["verdict"] == cm.UNVERIFIABLE
    assert [p["arms"] for p in judgement["undetermined_pairs"]] == [
        [f"{RUN}::pool-verify-b-k5", f"{RUN}::pool-verify-c-k5"]]
    assert judgement["unverifiable_halves"][0]["arm"] == f"{RUN}::pool-verify-c-k5"
    out = cm.render("ad hoc", judgement, _arms, report=False)
    assert "UNVERIFIABLE VERIFIER HALF: run1::pool-verify-c-k5: 2 verifier meta(s)" in out


def test_a_bound_stage_with_no_readable_meta_is_unverifiable_not_absent(repo) -> None:
    """The same hole through a binding: the bound source lies in stage
    ``pool-verify-c``, whose metas cannot be read."""
    repo["write_bindings"]([_entry("dark", ["cell-a"], verifier_sources=[
        f"outputs/{RUN}/verifier/pool/verify_c/probabilities.json"])])
    arm = cm.arm_for_condition(f"{RUN}::cell-a")
    assert arm["verifier_basis"] == "unverifiable"
    assert "none readable as a verifier pass" in arm["verifier_unverifiable_reason"]
    judgement, _arms = cm.check_conditions([f"{RUN}::cell-a", f"{RUN}::pool-verify-b-k5"])
    assert judgement["verdict"] == cm.UNVERIFIABLE


def test_a_stage_listing_only_a_proposer_meta_is_unverifiable(repo) -> None:
    """A readable meta that records no verifier pass is not verifier
    evidence, and is named among the unreadable."""
    arm = cm.arm_from_metas("A", [repo["meta"]["pool"]], verifier_metas=[repo["meta"]["other"]])
    assert arm["verifier_basis"] == "unverifiable"
    assert repo["meta"]["other"] in arm["unreadable"]


def test_two_arms_reading_one_unverifiable_stage_are_judged_on_the_proposer(repo) -> None:
    """Two arms whose verifier halves read the SAME unreadable stage send
    the same verifier requests, whatever they were: the proposer half
    decides (here a null manipulation: two listed libraries, images off)."""
    root = repo["root"]
    a = cm.arm_from_metas("A", [_write(root, "p/a.meta.json", _proposer_meta("detect_a", 3))],
                          verifier_metas=["outputs/gone.meta.json"])
    b = cm.arm_from_metas("B", [_write(root, "p/b.meta.json", _proposer_meta("detect_b", 5))],
                          verifier_metas=["outputs/gone.meta.json"])
    assert cm.transmission_relation(a, b) == cm.SAME
    assert cm.judge([a, b])["verdict"] == cm.REFUSE


@pytest.mark.parametrize(("mutate", "problem"), [
    (lambda e: e.update(conditions=["run1::nope"]), "run1::nope is not a registered condition"),
    (lambda e: e.update(detections=["results/elsewhere.geojson"]),
     "registered detections 'results/cells/cell-a/detections.geojson' are not among"),
    (lambda e: e.update(evidence={"derivation": "x"}), "evidence cites no script or document"),
    (lambda e: e.update(evidence={"script": "s.py:1"}), "evidence has no derivation"),
    (lambda e: e.update(verifier_sources=[]), "names no verifier or proposer source"),
    (lambda e: e.update(verifier_sources=["/abs/path"]), "is not a repository-relative path"),
    (lambda e: e.update(conditions=["run1::single"],
                        detections=["results/cells/single/detections.geojson"]),
     "run1::single is not proposer-verifier"),
])
def test_an_invalid_binding_is_named(repo, mutate, problem) -> None:
    """Each malformed entry is reported with what is wrong."""
    entry = _entry("bad", ["cell-a"], verifier_sources=["outputs/loose"])
    mutate(entry)
    problems = cm.validate_bindings({"schema_version": cm.BINDINGS_SCHEMA,
                                     "bindings": [entry]}, repo["conditions"],
                                    lambda c: f"results/cells/{c['label']}/detections.geojson")
    assert any(problem in p for p in problems), problems


def test_a_condition_bound_twice_stops_the_gate(repo, monkeypatch, capsys) -> None:
    """Two entries binding one condition: the gate refuses to guess (exit 1)."""
    repo["write_bindings"]([_entry("one", ["cell-a"], verifier_sources=["outputs/loose"]),
                            _entry("two", ["cell-a"], verifier_sources=["outputs/loose"])])
    monkeypatch.setattr(cm, "_analyses", lambda: {"x": {"conditions_compared": [
        f"{RUN}::cell-a", f"{RUN}::cell-b"]}})
    assert cm.main(["x"]) == 1
    assert "run1::cell-a is already bound by one" in capsys.readouterr().err


def test_bound_arms_that_sent_identical_requests_are_refused_as_new(repo, monkeypatch) -> None:
    """Two arms bound to two stages whose configurations differ only in a
    name (the verify version) but whose requests were identical: the gate
    REFUSES, and labels the pair NEW (no document records it); an allow-list
    group holding both arms' pools labels it KNOWN."""
    root = repo["root"]
    _write(root, "outputs/s1/run.meta.json", _verifier_meta("verify_one-text"))
    _write(root, "outputs/s2/run.meta.json", _verifier_meta("verify_two-text"))
    repo["write_bindings"]([_entry("b1", ["cell-a"], verifier_sources=["outputs/s1"]),
                            _entry("b2", ["cell-b"], verifier_sources=["outputs/s2"])])
    judgement, arms = cm.check_conditions([f"{RUN}::cell-a", f"{RUN}::cell-b"])
    assert [a["verifier_basis"] for a in arms] == ["transmitted", "transmitted"]
    assert judgement["verdict"] == cm.REFUSE
    (pair,) = judgement["null_pairs"]
    assert pair["config_fields_differing"] == ["version"]
    assert pair["documented_by"] is None  # NEW: documented nowhere
    monkeypatch.setattr(cm, "KNOWN_NULL_MANIPULATIONS", (
        {"pools": frozenset({(RUN, "pool")}), "documents": ("reports/x.md",),
         "documented_by": "reports/x.md § 1"},))
    judgement, _arms = cm.check_conditions([f"{RUN}::cell-a", f"{RUN}::cell-b"])
    assert judgement["null_pairs"][0]["documented_by"] == "reports/x.md § 1"


def test_bound_arms_whose_requests_differ_pass(repo) -> None:
    """The same two arms bound to stages with different verifier
    temperatures sent different requests: PASS."""
    repo["write_bindings"]([
        _entry("b1", ["cell-a"], verifier_sources=[f"outputs/{RUN}/verifier/pool/verify_a"]),
        _entry("b2", ["cell-b"], verifier_sources=[f"outputs/{RUN}/verifier/pool/verify_b"])])
    judgement, _arms = cm.check_conditions([f"{RUN}::cell-a", f"{RUN}::cell-b"])
    assert judgement["verdict"] == cm.PASS
