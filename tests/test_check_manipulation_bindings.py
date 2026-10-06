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
           cm.stage_metas, cm.verifier_metas_for_source, cm.proposer_metas_for_source,
           cm._incomplete_stages, dcm.load_meta_json, dcm.pool_output_dir)


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
    not exist is never widened to its parent. (The resolvers are memoised
    over a tree that does not change during a run, so the test drops the
    caches after writing.)"""
    expected = ((repo["meta"]["loose"],), "source-directory")
    assert cm.verifier_metas_for_source("outputs/loose") == expected
    assert cm.verifier_metas_for_source("outputs/loose/probabilities.json") == ((), None)
    _write(repo["root"], "outputs/loose/probabilities.json", {})
    _clear_caches()
    assert cm.verifier_metas_for_source("outputs/loose/probabilities.json") == expected


def test_a_proposer_source_resolves_by_manifest_then_disk(repo) -> None:
    """A pass directory the passes manifest records resolves through it; one
    it does not record is read from disk."""
    assert cm.proposer_metas_for_source(f"outputs/{RUN}/pool") == (
        (repo["meta"]["pool"],), f"passes-manifest:{RUN}/pool")
    assert cm.proposer_metas_for_source("outputs/other-pool") == (
        (repo["meta"]["other"],), "source-directory")
    assert cm.proposer_metas_for_source("outputs/absent") == ((), None)


# ── PR #25 review, findings 5, 6 and 9: the proposer routes ──────────────

def test_unreadable_manifest_hits_do_not_stop_the_disk_route(repo) -> None:
    """The passes manifest records, under a pass directory, only a meta that
    is absent here and a run.log: neither is a readable proposer meta, so the
    disk route still runs and finds the pass meta that IS there (they used
    to suppress it, leaving the arm with no proposer evidence)."""
    disk = _write(repo["root"], "outputs/p2/run_1/d.meta.json", _proposer_meta("detect_z"))
    _write(repo["root"], "outputs/p2/run_1/run.log", "log")
    repo["passes"][(RUN, "pool2")] = [{"provenance": {"source_files": [
        "outputs/p2/run_1/gone.meta.json", "outputs/p2/run_1/run.log"]}}]
    _clear_caches()
    assert cm.proposer_metas_for_source("outputs/p2") == ((disk,), "source-directory")


def test_a_readable_manifest_hit_keeps_its_unreadable_sibling_visible(repo) -> None:
    """With one readable proposer meta among the manifest's hits, the route
    answers, and keeps an unreadable META beside it (named unreadable by the
    arm) but drops a non-meta file."""
    good = _write(repo["root"], "outputs/p3/run_1/d.meta.json", _proposer_meta("detect_z"))
    repo["passes"][(RUN, "pool2")] = [{"provenance": {"source_files": [
        good, "outputs/p3/run_2/gone.meta.json", "outputs/p3/run_1/run.log"]}}]
    _clear_caches()
    assert cm.proposer_metas_for_source("outputs/p3") == (
        (good, "outputs/p3/run_2/gone.meta.json"), f"passes-manifest:{RUN}/pool2")


def test_a_single_file_source_must_be_a_readable_proposer_meta(repo) -> None:
    """A source naming one meta file is accepted only if it reads as a
    proposer pass (it used to be accepted unread)."""
    verifier = repo["meta"]["loose"]
    corrupt = "outputs/p4/run_1/d.meta.json"
    (repo["root"] / corrupt).parent.mkdir(parents=True)
    (repo["root"] / corrupt).write_text("{")
    assert cm.proposer_metas_for_source(verifier) == ((), None)
    assert cm.proposer_metas_for_source(corrupt) == ((), None)
    assert cm.proposer_metas_for_source(repo["meta"]["other"]) == (
        (repo["meta"]["other"],), "source-directory")


def test_the_disk_route_never_parses_a_verified_subtree(repo, monkeypatch) -> None:
    """The path filter runs before a meta is read: a pool's ``verified/``
    and ``crops/`` metas are never harvested (or cached) by the search."""
    _write(repo["root"], "outputs/p5/run_1/d.meta.json", _proposer_meta("detect_z"))
    _write(repo["root"], "outputs/p5/verified/run.meta.json", _verifier_meta())
    _write(repo["root"], "outputs/p5/crops/x/run.meta.json", _verifier_meta())
    read: list[str] = []
    real = cm.meta_record

    def spy(path: str) -> dict[str, Any]:
        """Record which metas the search harvests.

        Args:
            path: The meta path.

        Returns:
            The real harvested record.
        """
        read.append(path)
        return real(path)

    monkeypatch.setattr(cm, "meta_record", spy)
    assert cm._proposer_metas_under("outputs/p5") == ["outputs/p5/run_1/d.meta.json"]
    assert read == ["outputs/p5/run_1/d.meta.json"]


def test_a_git_renamed_meta_is_judged_by_where_it_sat(repo, monkeypatch) -> None:
    """The git-rename route tests the OLD path's place below the source: a
    pass meta moved from ``outputs/pp/run_1`` to ``archive/xy/verified/
    run_1`` is a proposer meta, and a meta that sat in
    ``outputs/pp/verified`` is not. The old code sliced the NEW path by the
    source's length (``outputs/pp`` and ``archive/xy`` are both 10
    characters), so it rejected the first and accepted the second."""
    _write(repo["root"], "archive/xy/verified/run_1/d.meta.json", _proposer_meta("detect_z"))
    _write(repo["root"], "archive/xy/run_v/d.meta.json", _proposer_meta("detect_w"))
    renames = [("outputs/pp/run_1/d.meta.json", "archive/xy/verified/run_1/d.meta.json"),
               ("outputs/pp/verified/d.meta.json", "archive/xy/run_v/d.meta.json")]
    monkeypatch.setattr(dcm, "git_renames", lambda paths: (renames, "abc1234"))
    monkeypatch.setattr(dcm, "git_renamed_to",
                        lambda paths: ([new for _old, new in renames], "abc1234"))
    assert cm.proposer_metas_for_source("outputs/pp") == (
        ("archive/xy/verified/run_1/d.meta.json",), "git-rename:abc1234")


def test_a_meta_reached_by_two_spellings_is_harvested_once(repo) -> None:
    """An absolute and a relative path to one meta share one harvest."""
    cm.meta_record.cache_clear()
    rel = repo["meta"]["a"]
    assert cm._is_verifier_meta(str(repo["root"] / rel)) and cm._is_verifier_meta(rel)
    assert cm.meta_record.cache_info().currsize == 1


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


def _add_stage_condition(repo: dict[str, Any], stage: str, path: str, label: str) -> str:
    """Register one more verifier stage and a condition its label names.

    Args:
        repo: The :func:`repo` namespace.
        stage: The ``verifier_passes`` key.
        path: Its registered path (under ``outputs/<run>/``).
        label: The new condition's label (``<stage>-...`` names the stage).

    Returns:
        The new condition's id.
    """
    entry = repo["decomposition"][RUN]
    entry["verifier_passes"][stage] = {"path": path}
    entry["conditions"].append({"label": label,
                                "detections": f"results/cells/{label}/detections.geojson"})
    cid = f"{RUN}::{label}"
    repo["conditions"][cid] = {"condition_id": cid, "run_id": RUN, "label": label,
                               "architecture": "proposer-verifier", "proposer_pool": "pool",
                               "verifier_config": _DECLARED}
    _clear_caches()
    return cid


# ── PR #25 review, finding 3: no stage is a run's whole tree ────────────

def test_a_dot_path_stage_is_not_a_catch_all(repo) -> None:
    """A stage registered at path ``.`` (as 55maps-generalisation's
    verified-cleanup-20260410 is, with a ``repo_path``) used to make the
    run's whole output tree its directory, so any source no deeper stage
    claimed, and any condition's detections under the run, resolved to it.
    Without a repo_path its run-tree candidates are dropped; with one it
    lives at its repo_path only."""
    passes = repo["decomposition"][RUN]["verifier_passes"]
    passes["cleanup"] = {"path": "."}
    _clear_caches()
    stray = f"outputs/{RUN}/elsewhere/probabilities.json"
    assert cm.stages_containing(stray) == []
    assert all(d not in cm._run_roots(RUN) for d, _run, _key in cm._stage_dirs())
    passes["cleanup"] = {"path": ".", "repo_path": "archive/staging/cleanup"}
    _clear_caches()
    assert cm._stage_homes(RUN, "cleanup", passes["cleanup"]) == ["archive/staging/cleanup"]
    assert cm.stages_containing(stray) == []
    assert cm.stages_containing("archive/staging/cleanup/probabilities.json") == [
        (RUN, "cleanup")]
    # The register's own route: detections under the run tree but in no
    # stage's directory name no stage (they used to name the catch-all).
    cid = _add_stage_condition(repo, "unused-stage", "verifier/unused", "elsewhere-cell")
    repo["decomposition"][RUN]["conditions"][-1]["detections"] = (
        f"outputs/{RUN}/elsewhere/detections.geojson")
    assert cm.verifier_stage_of(repo["conditions"][cid])[0] is None


def test_a_repo_path_stage_does_not_claim_the_run_tree(repo) -> None:
    """A stage that names its own root (repo_path, ruling D32) does not
    also occupy ``outputs/<run>/<path>``, which may be another stage's."""
    passes = repo["decomposition"][RUN]["verifier_passes"]
    passes["moved"] = {"path": "verifier/pool/verify_b", "repo_path": "archive/legs"}
    _clear_caches()
    assert cm.stages_containing(f"outputs/{RUN}/verifier/pool/verify_b/probabilities.json") == [
        (RUN, "pool-verify-b")]
    assert cm.stages_containing("archive/legs/verifier/pool/verify_b/x.json") == [(RUN, "moved")]


# ── PR #25 review, finding 7: a binding against the register's stage ────

def test_a_binding_to_another_stage_does_not_override_the_register(repo) -> None:
    """The label names stage ``pool-verify-d``, whose metas cannot be found;
    a binding naming stage ``pool-verify-a`` is NOT silently used in its
    place. The half is UNVERIFIABLE with both stages named, and the stage
    field keeps the register's stage."""
    cid = _add_stage_condition(repo, "pool-verify-d", "verifier/pool/verify_d",
                               "pool-verify-d-k5")
    entry = {**_entry("other", ["pool-verify-d-k5"]),
             "verifier_sources": [f"outputs/{RUN}/verifier/pool/verify_a"]}
    repo["write_bindings"]([entry])
    arm = cm.arm_for_condition(cid)
    assert arm["verifier_basis"] == "unverifiable"
    assert arm["verifier_unverifiable_reason"] == (
        f"binding other names stage(s) {RUN}/pool-verify-a, but the register identifies "
        f"stage {RUN}/pool-verify-d (by label); the binding is not used")
    assert arm["verifier_stage"] == {"stage": "pool-verify-d", "how": "label"}
    assert arm["binding"] is None
    assert repo["meta"]["a"] not in arm["meta_paths"]


def test_a_binding_inside_the_registers_stage_is_followed(repo) -> None:
    """A binding whose source lies inside the register's own stage (here a
    leg two levels down, beyond the stage resolver's reach) agrees with the
    register and is followed; the stage field names the stage, and the
    route is recorded apart from it."""
    cid = _add_stage_condition(repo, "pool-verify-d", "verifier/pool/verify_d",
                               "pool-verify-d-k5")
    leg = f"outputs/{RUN}/verifier/pool/verify_d/leg/one"
    meta = _write(repo["root"], f"{leg}/run.meta.json", _verifier_meta(temperature=0.5))
    entry = {**_entry("inside", ["pool-verify-d-k5"]), "verifier_sources": [leg]}
    repo["write_bindings"]([entry])
    arm = cm.arm_for_condition(cid)
    assert arm["verifier_basis"] == "transmitted"
    assert meta in arm["meta_paths"]
    assert arm["verifier_stage"] == {"stage": f"{RUN}/pool-verify-d", "how": "binding:inside"}
    assert arm["verifier_route"] == "source-directory"
    assert arm["binding"] == "inside"


# ── PR #25 review, finding 4: a stage whose meta covers part of it ──────

_PARTIAL = "run.meta.json records only the 6-item cleanup leg of 38,713 requests"


def test_an_incomplete_meta_binding_leaves_the_half_unverifiable(repo) -> None:
    """A binding whose review found the stage's only meta to be a cleanup
    leg: the meta is set aside, the half is UNVERIFIABLE with the binding's
    reason, and a pair beside a transmitted arm of the same proposer
    request is unverifiable. Without the flag the cleanup meta read as the
    whole stage and the pair PASSED on it."""
    entry = _entry("cleanup-only", ["cell-a"], verifier_sources=[
        f"outputs/{RUN}/verifier/pool/verify_a/probabilities.json"])
    repo["write_bindings"]([entry])
    judgement, _arms = cm.check_conditions([f"{RUN}::cell-a", f"{RUN}::pool-verify-b-k5"])
    assert judgement["verdict"] == cm.PASS  # the unflagged binding: the meta is evidence
    repo["write_bindings"]([{**entry, "incomplete_meta": True,
                             "incomplete_meta_reason": _PARTIAL}])
    arm = cm.arm_for_condition(f"{RUN}::cell-a")
    assert arm["verifier_basis"] == "unverifiable"
    assert arm["verifier_unverifiable_reason"] == (
        f"incomplete meta: {RUN}/pool-verify-a: binding cleanup-only: {_PARTIAL}")
    assert arm["verifier_metas_set_aside"] == [repo["meta"]["a"]]
    assert arm["binding"] == "cleanup-only"
    judgement, _arms = cm.check_conditions([f"{RUN}::cell-a", f"{RUN}::pool-verify-b-k5"])
    assert judgement["verdict"] == cm.UNVERIFIABLE
    assert judgement["undetermined_pairs"]


def test_an_incomplete_stage_is_unverifiable_by_every_route(repo) -> None:
    """The flag is a fact about the stage: an arm that reaches the same
    stage through the register's own route (its label) and another bound
    to it by an unflagged binding are unverifiable too; two arms reading
    the one stage are then judged on the proposer half (here, one request
    and one configuration: no pair to judge)."""
    repo["decomposition"][RUN]["conditions"].append(
        {"label": "pool-verify-a-k3", "detections": "results/cells/a3/detections.geojson"})
    repo["conditions"][f"{RUN}::pool-verify-a-k3"] = {
        **repo["conditions"][f"{RUN}::cell-a"], "condition_id": f"{RUN}::pool-verify-a-k3",
        "label": "pool-verify-a-k3"}
    source = f"outputs/{RUN}/verifier/pool/verify_a/probabilities.json"
    repo["write_bindings"]([
        {**_entry("flagged", ["cell-a"], verifier_sources=[source]),
         "incomplete_meta": True, "incomplete_meta_reason": _PARTIAL},
        _entry("plain", ["cell-b"], verifier_sources=[source])])
    arms = [cm.arm_for_condition(f"{RUN}::{lab}") for lab in ("pool-verify-a-k3", "cell-b")]
    assert arms[0]["verifier_stage"] == {"stage": "pool-verify-a", "how": "label"}
    for arm in arms:
        assert arm["verifier_basis"] == "unverifiable"
        assert arm["verifier_unverifiable_reason"] == (
            f"incomplete meta: {RUN}/pool-verify-a: binding flagged: {_PARTIAL}")
    judgement, _arms = cm.check_conditions([f"{RUN}::cell-a", f"{RUN}::cell-b",
                                            f"{RUN}::pool-verify-a-k3"])
    assert judgement["verdict"] == cm.PASS
    assert len(judgement["unverifiable_halves"]) == 3


@pytest.mark.parametrize(("extra", "problem"), [
    ({"incomplete_meta": "yes"}, "incomplete_meta is str, not true or false"),
    ({"incomplete_meta": True}, "incomplete_meta_reason is not a one-line reason"),
    ({"incomplete_meta": True, "incomplete_meta_reason": " "},
     "incomplete_meta_reason is not a one-line reason"),
    ({"incomplete_meta": False, "incomplete_meta_reason": "x"},
     "incomplete_meta_reason without incomplete_meta: true"),
    ({"incomplete_meta": True, "incomplete_meta_reason": "x", "verifier_sources": [],
      "proposer_sources": ["outputs/other-pool"]},
     "incomplete_meta is true but the binding names no verifier source"),
])
def test_an_invalid_incomplete_meta_flag_is_named(repo, extra, problem) -> None:
    """The flag is a boolean with a reason, on a binding with a verifier
    source; anything else is a named problem (exit 1 through the gate)."""
    entry = {**_entry("bad", ["cell-a"], verifier_sources=["outputs/loose"]), **extra}
    problems = cm.validate_bindings({"schema_version": cm.BINDINGS_SCHEMA,
                                     "bindings": [entry]}, repo["conditions"],
                                    lambda c: f"results/cells/{c['label']}/detections.geojson")
    assert any(problem in p for p in problems), problems


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


# ── PR #25 review, finding 8: a malformed file stops the gate, by name ──

def _good() -> dict[str, Any]:
    """A well-formed entry for the malformed-file cases to break.

    Returns:
        A binding of ``cell-a`` to the unregistered ``loose`` stage.
    """
    return _entry("bad", ["cell-a"], verifier_sources=["outputs/loose"])


def _doc(*entries: Any) -> dict[str, Any]:
    """A bindings document holding ``entries``.

    Args:
        *entries: The ``bindings`` list's items.

    Returns:
        The document.
    """
    return {"schema_version": cm.BINDINGS_SCHEMA, "bindings": list(entries)}


@pytest.mark.parametrize(("doc", "problem"), [
    ({"schema_version": cm.BINDINGS_SCHEMA}, "bindings is absent"),
    ({"schema_version": cm.BINDINGS_SCHEMA, "bindings": None}, "bindings is null"),
    ({"schema_version": cm.BINDINGS_SCHEMA, "bindings": []}, "bindings is empty"),
    ({"schema_version": cm.BINDINGS_SCHEMA, "bindings": {"x": 1}},
     "bindings is a dict, not a list"),
    (["not", "an", "object"], "the bindings file is a JSON list, not an object"),
    ("{not json", "cannot be read as JSON"),
    (_doc("a binding"), "binding #0: a str, not an object"),
    (_doc({**_good(), "id": ["x"]}), "binding #0: no id"),
    (_doc({**_good(), "verifier_sources": "outputs/loose"}),
     "verifier_sources is str, not a list of strings"),
    (_doc({**_good(), "verifier_sources": [1, 2]}),
     "verifier_sources is list, not a list of strings"),
    (_doc({**_good(), "proposer_sources": "outputs/other-pool"}),
     "proposer_sources is str, not a list of strings"),
    (_doc({**_good(), "conditions": "run1::cell-a"}), "conditions is str, not a list"),
    (_doc({**_good(), "detections": "results/cells/cell-a/detections.geojson"}),
     "detections is str, not a list"),
    (_doc({**_good(), "evidence": "see the log"}), "evidence is str, not an object"),
    (_doc({**_good(), "evidence": {"derivation": "x", "documents": "doc.md"}}),
     "evidence: documents is str, not a list of strings"),
])
def test_a_malformed_bindings_file_exits_1_with_an_error(repo, monkeypatch, capsys, doc,
                                                         problem) -> None:
    """Every malformed case (wrong types, a missing, null or empty bindings
    list) is named on an ``ERROR:`` line and exits 1. Until the fix a str
    source raised TypeError, a missing list KeyError, a str evidence
    AttributeError, and an empty or null list silently disabled every
    binding."""
    path = repo["root"] / cm.BINDINGS
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc if isinstance(doc, str) else json.dumps(doc))
    _clear_caches()
    monkeypatch.setattr(cm, "_analyses", lambda: {"x": {"conditions_compared": [
        f"{RUN}::cell-a", f"{RUN}::cell-b"]}})
    assert cm.main(["x"]) == 1
    err = capsys.readouterr().err
    assert err.startswith("ERROR: ") and problem in err, err


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
