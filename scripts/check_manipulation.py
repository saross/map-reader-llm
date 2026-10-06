#!/usr/bin/env python3
"""
Manipulation check as a maintained guard: refuse an analysis whose arms differ
in configuration but not in what was transmitted to the model.

Why this script exists
----------------------
On 2026-10-05 a read-only check (``reports/manipulation-check-2026-10-05.md``)
asked, for every registered arm, whether its manipulation reached the model.
It found three null manipulations, the largest being the retest's Phase 2c
text track: five arms with five different example libraries that sent five
IDENTICAL requests, because ``include_example_images: false`` transmits
nothing from the library (erratum E90). One "significant" contrast
(p = 0.001) was a difference between replicates. The check's scratch scripts
(``reports/manipulation-check-2026-10-05-scripts/``) were written for one
run; this module makes the test a gate an analysis must pass (tracker
``planning/text-track-transmission-2026-10-05.md`` § W6.1).

The rule
--------
For each arm (a registered condition), build two things from its pass
metadata:

- a **configuration identity** — what the configuration SAID: the config
  version, instruction file, model, temperature, thinking level, the listed
  example library, the ``include_example_images`` flag, any ordering
  override, ``text_only_labels``, tile size and output budget;
- a **transmitted signature** — what the request CARRIED
  (:data:`SIGNATURE_FIELDS`): the model of record, effective temperature,
  thinking level, system-instruction hash, the examples actually sent, tile
  size and output budget.

Two arms of one analysis whose configuration identities DIFFER but whose
transmitted signatures are IDENTICAL are a null manipulation: the analysis
compares replicates under different names. The guard REFUSES such an
analysis (exit 2, naming the pair and the configuration fields that differ).
Arms that differ only after the model (vote thresholds, K, aggregation) share
both and pass, as do arms that are intended replicates of one configuration.

The signature (shared definition)
---------------------------------
map-reader-bench is designing the same gate for its own runner (its
``scripts/check-payload-manipulations.py``; ``reports/2026-10-05-d8-preflight.md``
§ 3.1 there compares saved request payloads byte for byte). The signature
here is the metadata-level counterpart, versioned as
:data:`SIGNATURE_VERSION`, so the two projects can share one definition:

    stage            proposer | verifier
    model            model of record: per-item model_version, else
                     cost_estimate.pricing_used.model, else configuration.model
                     (erratum E57's precedence)
    temperature_eff  configuration.temperature_effective, else .temperature (E55)
    thinking         configuration.thinking_level
    sys_hash         first 12 hex of configuration.system_instruction_hash
    examples_sent    proposer: "images:<fp>/<n>" only when
                     include_example_images is true or absent AND the list is
                     non-empty, else "none"; verifier: "text-labels:<n>" when
                     text_only_labels is present, else "images:<fp>/<n>" for a
                     non-empty list (scripts/lib_verifier.py
                     build_reference_items), else "none". <fp> is the first 12
                     hex of sha256 over the ordered (path, label) list.
    tile_size        configuration.tile_size
    max_output_tokens configuration.max_output_tokens (added 2026-10-06: it is
                     transmitted, and the 2026-10-05 signature omitted it)
    inputs           "<fp>/<n>" over the sorted ids of every item dispatched
                     (execution_stats completed_items plus failed_items: tiles
                     for a proposer, candidates for a verifier), else the
                     recorded manifest path, else "unrecorded". An ARM's
                     signature carries one inputs field per stage over the
                     union of its passes (a recovery fragment re-sends a
                     subset of its pass's tiles). Added
                     2026-10-06: the 2026-10-05 check compared arms within a
                     run, where the tiles are shared; across runs a 384 px
                     487-tile pass and a 512 px 340-tile pass of one
                     configuration are different requests, and the tile size
                     itself is rarely recorded (W7.2).

What the signature cannot see: an example ORDER that the metas do not record
(the Phase 2e orderings were transmitted but no meta shows them; W7.3), and
any manipulation that leaves no field in the meta (W7). A PASS is evidence
that every configured difference left a transmitted trace, not proof that it
changed the model's input.

Reuse
-----
Per-meta field extraction and the signature live in
``scripts/lib_manipulation_signature.py``: the 2026-10-05 harvester's
``harvest()`` and ``arms.py``'s ``signature()``, ``_model_of_record()`` and
``eff_temp()``, copied there with attribution (and extended by
``max_output_tokens`` and ``inputs``). This gate once loaded the harvester
from ``reports/manipulation-check-2026-10-05-scripts/`` at import, so
archiving that report would have broken it (PR #24 review, finding 4); the
report's scripts stay as the record of what that check ran.

Arms are resolved through ``results/passes-manifest.json``
(``provenance.source_files`` per pass), falling back to the pool's output
directory, the register's ``source_run``, the pool named on the condition's
detections path, and a run's sole pool (:func:`proposer_metas_for_condition`):
the proposer pool's passes, and for a proposer-verifier condition its
verifier stage's passes. A condition's stage
is found from the register's own detections path, else from its label; a
stage that cannot be found leaves the verifier part DECLARED (the
condition's registered ``verifier_config``). A declared configuration is
what the register SAYS, not what a request carried, so it never makes two
arms differ in transmission: a pair whose proposer requests are identical
and whose verifier halves are not both transmitted is UNVERIFIABLE (PR #24
review, finding 2; until then a declared difference passed by assumption).
Two arms that declare the SAME verifier configuration are judged on their
proposer requests, since nothing configured on the verifier half separates
them.

Usage
-----
    # Gate one registered analysis (exit 0 PASS, 2 REFUSE, 3 UNVERIFIABLE)
    python3 scripts/check_manipulation.py era1-leaderboard

    # The same, with the per-arm signature table
    python3 scripts/check_manipulation.py era1-leaderboard --report

    # An ad hoc set of conditions
    python3 scripts/check_manipulation.py --conditions RUN::LABEL RUN::LABEL

    # Every registered analysis, one line each, then which refusals are
    # documented (exit 2 only if a refusal is undocumented)
    python3 scripts/check_manipulation.py --all

Exit codes: 0 PASS; 1 usage error (unknown analysis or condition); 2 REFUSE
(a null manipulation); 3 UNVERIFIABLE (an arm with no readable pass metadata,
or a pair that only a declared verifier configuration could separate, unless
``--allow-unverifiable``).

Known null manipulations
------------------------
Some null manipulations are already documented findings: the analysis does
compare replicates, and the document says so. :data:`KNOWN_NULL_MANIPULATIONS`
lists them as groups of ``(run_id, proposer_pool)`` keys, each with the
document that records it. Every null pair of registered arms is labelled
KNOWN (with that document) or NEW. A single analysis still REFUSES on a
known pair, because the comparison is still between replicates; ``--all``
exits 2 only when some refusal rests on a NEW pair, so a sweep is clean once
every refusal is documented (with ``--allow-unverifiable``, exit 0).
"""

from __future__ import annotations

import argparse
import functools
import itertools
import json
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts import derive_condition_modality as dcm  # noqa: E402
from scripts.lib_manipulation_signature import (  # noqa: E402,F401 - re-exported
    SIGNATURE_FIELDS,
    SIGNATURE_VERSION,
    dispatched_ids,
    eff_temp,
    harvest,
    inputs_fingerprint,
    is_verifier_record,
    model_of_record,
    signature,
)

RUN_ANALYSES = "results/run-analyses.json"
CONDITIONS_MANIFEST = "results/conditions-manifest.json"

#: The fields of a configuration identity, in order.
CONFIG_FIELDS = ("stage", "version", "instruction_file", "model", "temperature",
                 "thinking_level", "listed_library", "include_example_images",
                 "ordering", "text_only_labels", "tile_size", "max_output_tokens")

#: Verdicts and their exit codes.
PASS, REFUSE, UNVERIFIABLE = "PASS", "REFUSE", "UNVERIFIABLE"
EXIT_CODES = {PASS: 0, REFUSE: 2, UNVERIFIABLE: 3}

#: Documented null manipulations: groups of ``(run_id, proposer_pool)`` keys
#: whose passes sent one configuration's requests under different names, each
#: with the documents that record it (``documents``, the files; and
#: ``documented_by``, where in them). A null pair whose two arms' keys lie in
#: one group is KNOWN (see the module docstring). Add a group only with the
#: document that establishes the replicate.
KNOWN_NULL_MANIPULATIONS: tuple[dict[str, Any], ...] = (
    {"pools": frozenset({("retest-phase2b", "track2-text-t0.0"),
                         ("retest-phase2c", "track2-text-canonical"),
                         ("retest-phase2c", "track2-text-plus-hp"),
                         ("retest-phase2c", "track2-text-pure-positive-canon"),
                         ("retest-phase2c", "track2-text-scale-4"),
                         ("retest-phase2c", "track2-text-scale-8")}),
     "documents": ("reports/manipulation-check-2026-10-05.md",),
     "documented_by": ("reports/manipulation-check-2026-10-05.md § B.5 group 16 (null "
                       "manipulation #1: five text-track libraries, one request, E90)")},
    {"pools": frozenset({("retest-phase2b", "track1-image-t0.0"),
                         ("retest-phase2c", "track1-image-scale-8")}),
     "documents": ("reports/manipulation-check-2026-10-05.md",),
     "documented_by": ("reports/manipulation-check-2026-10-05.md § B.5 group 15 (the same "
                       "17 examples under two configuration names)")},
    {"pools": frozenset({("h8-v2", "scale-8"), ("h10", "pool_160_hp4hn4"),
                         ("h12-v2", "pool_160_hp4hn4")}),
     "documents": ("reports/manipulation-check-2026-10-05.md",
                   "results/h12-v2/analysis_summary.md"),
     "documented_by": ("reports/manipulation-check-2026-10-05.md § B.5 group 10 (h8-v2 "
                       "scale-8 and h10 pool_160_hp4hn4: one configuration, run twice on "
                       "2026-04-15); results/h12-v2/analysis_summary.md lines 73-74 and 148 "
                       "(h12-v2 R2 reuses the pool_160_hp4hn4 run)")},
)


@functools.lru_cache(maxsize=None)
def meta_record(path: str) -> dict[str, Any]:
    """One meta's harvested fields, with its dispatched-item fingerprint.

    The meta is parsed once, by :func:`lib_manipulation_signature.harvest`,
    whose record carries ``max_output_tokens`` and ``dispatched_ids`` (until
    PR #24 review finding 9, this function re-read the file for both).

    Args:
        path: Repository-relative or absolute ``*.meta.json`` path.

    Returns:
        The harvester's record (``error`` set when unreadable), with
        ``input_ids`` (the dispatched ids, a frozenset) and ``inputs`` (their
        fingerprint, see the module docstring).
    """
    p = Path(path)
    full = p if p.is_absolute() else BASE_DIR / p
    rec = harvest(str(full))
    rec["path"] = path
    if "error" not in rec:
        rec["input_ids"] = frozenset(rec.pop("dispatched_ids"))
        rec["inputs"] = inputs_fingerprint(rec["input_ids"], rec.get("manifest_path"))
    return rec


def configuration_identity(r: dict[str, Any]) -> dict[str, Any]:
    """What one meta's configuration SAID (:data:`CONFIG_FIELDS`).

    The model name is folded across the ``-preview`` suffix, which the
    runner adds when resolving a marketing name, so the same configuration
    run before and after a promotion is not mistaken for two.

    Args:
        r: A harvested meta record.

    Returns:
        The configuration identity dict.
    """
    model = str(r.get("model") or "").removesuffix("-preview") or None
    listed = (f"{r['listed_library_fp']}/{r['listed_example_n']}"
              if r.get("listed_example_n") else "none")
    return {
        "stage": "verifier" if is_verifier_record(r) else "proposer",
        "version": r.get("version"),
        "instruction_file": r.get("instruction_file"),
        "model": model,
        "temperature": r.get("temperature"),
        "thinking_level": r.get("thinking_level"),
        "listed_library": listed,
        "include_example_images": str(r.get("snap_include_example_images")),
        "ordering": f"{r.get('ordering_override')}|{r.get('ordering_seed')}",
        "text_only_labels": len(r.get("text_only_labels") or []),
        "tile_size": r.get("tile_size"),
        "max_output_tokens": r.get("max_output_tokens"),
    }


def _frozen(dicts: list[dict[str, Any]]) -> frozenset[str]:
    """A set of dicts as a hashable, order-free value.

    Args:
        dicts: Signature or identity dicts.

    Returns:
        The frozenset of their sorted-key JSON encodings.
    """
    return frozenset(json.dumps(d, sort_keys=True) for d in dicts)


def arm_from_metas(arm_id: str, proposer_metas: list[str],
                   verifier_metas: list[str] | None = None,
                   declared_verifier: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build one arm's configuration identity and transmitted signature.

    Chunk metas are set aside when the pass has a merged meta (as the
    2026-10-05 check did), so a chunked pass is not counted twice.

    Args:
        arm_id: The arm's name (a condition id).
        proposer_metas: The proposer passes' meta paths.
        verifier_metas: The verifier stage's meta paths, when resolved.
        declared_verifier: The registered verifier configuration, used when
            the stage's metas are unknown. It joins the configuration
            identity (what the arm SAID) but not the transmitted signature:
            it is not evidence of what a request carried (see
            :func:`transmission_relation`).

    Returns:
        ``{"arm", "config", "signature", "proposer_signatures",
        "verifier_basis", "declared_verifier", "meta_paths", "unreadable",
        "unverifiable_reason"}``. ``signature`` holds transmitted evidence
        only; ``declared_verifier`` is the declared configuration's sorted-key
        JSON, or None.
    """
    def readable(paths: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
        recs = [meta_record(p) for p in sorted(set(paths))]
        bad = [r["path"] for r in recs if "error" in r]
        good = [r for r in recs if "error" not in r]
        main = [r for r in good if "_chunk" not in Path(r["path"]).name] or good
        return main, bad

    prop, bad_p = readable(proposer_metas)
    ver, bad_v = readable(verifier_metas or [])
    config = [configuration_identity(r) for r in prop + ver]
    # Per-pass signatures WITHOUT their inputs, plus one inputs field per
    # stage over the UNION of what the arm's passes dispatched: a recovery
    # fragment re-sends a few tiles of its pass, and per-fragment inputs
    # would make two arms of one request look different by their failures.
    sigs = [{k: v for k, v in signature(r).items() if k != "inputs"} for r in prop + ver]
    for stage, recs in (("proposer", prop), ("verifier", ver)):
        if recs:
            ids = frozenset().union(*(r.get("input_ids") or frozenset() for r in recs))
            manifests = sorted({str(r.get("manifest_path")) for r in recs
                                if r.get("manifest_path")})
            sigs.append({"stage": f"{stage}-inputs",
                         "inputs": inputs_fingerprint(ids, "|".join(manifests) or None)})
    declared_json = None
    if ver:
        basis = "transmitted"
    elif declared_verifier:
        basis = "declared"
        declared = {"stage": "verifier-declared", **declared_verifier}
        config.append(declared)
        declared_json = json.dumps(declared, sort_keys=True)
    else:
        basis = None
    reason = None
    if not prop:
        reason = ("no readable proposer pass metadata"
                  + (f" ({len(bad_p)} unreadable)" if bad_p else
                     " (no register binding — pool key, source_run, detections path "
                     "or sole pool — reaches a proposer meta)"))
    return {
        "arm": arm_id,
        "config": _frozen(config),
        "signature": _frozen(sigs),
        "proposer_signatures": sorted({json.dumps(signature(r), sort_keys=True)
                                       for r in prop}),
        "verifier_basis": basis,
        "declared_verifier": declared_json,
        "meta_paths": [r["path"] for r in prop + ver],
        "unreadable": bad_p + bad_v,
        "unverifiable_reason": reason,
    }


def differing_fields(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    """The configuration fields on which two arms' identities differ.

    Args:
        a: An arm from :func:`arm_from_metas`.
        b: Another.

    Returns:
        Sorted field names whose value sets differ between the arms.
    """
    def values(arm: dict[str, Any]) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for enc in arm["config"]:
            for k, v in json.loads(enc).items():
                out.setdefault(k, set()).add(json.dumps(v))
        return out

    va, vb = values(a), values(b)
    return sorted(k for k in set(va) | set(vb) if va.get(k) != vb.get(k))


#: How two arms' transmitted requests relate (:func:`transmission_relation`).
SAME, DIFFER, UNDETERMINED = "same", "differ", "undetermined"


def _proposer_half(arm: dict[str, Any]) -> frozenset[str]:
    """The proposer entries of an arm's transmitted signature.

    Args:
        arm: An arm from :func:`arm_from_metas`.

    Returns:
        The encoded ``proposer`` and ``proposer-inputs`` entries.
    """
    return frozenset(enc for enc in arm["signature"]
                     if json.loads(enc)["stage"] in ("proposer", "proposer-inputs"))


def transmission_relation(a: dict[str, Any], b: dict[str, Any]) -> str:
    """Whether two arms sent the same requests, different ones, or cannot be told.

    The proposer half is always transmitted evidence. The verifier half is
    evidence only when both arms' verifier metas were read: a DECLARED
    verifier configuration says what the register recorded, not what a
    request carried, so it cannot show a difference (PR #24 review,
    finding 2). Two equal declared configurations leave nothing configured
    on the verifier half to separate the arms, so the proposer half decides.
    An arm with no verifier stage beside one with a stage (declared or
    transmitted) differs: only one of them sent verifier requests.

    Args:
        a: An arm from :func:`arm_from_metas`.
        b: Another.

    Returns:
        :data:`SAME`, :data:`DIFFER` or :data:`UNDETERMINED`.
    """
    if "declared" not in (a["verifier_basis"], b["verifier_basis"]):
        return SAME if a["signature"] == b["signature"] else DIFFER
    if _proposer_half(a) != _proposer_half(b):
        return DIFFER
    if a["verifier_basis"] is None or b["verifier_basis"] is None:
        return DIFFER
    if a["declared_verifier"] is not None and a["declared_verifier"] == b["declared_verifier"]:
        return SAME
    return UNDETERMINED


def judge(arms: list[dict[str, Any]], allow_unverifiable: bool = False) -> dict[str, Any]:
    """Apply the rule to a set of arms.

    Args:
        arms: Arms from :func:`arm_from_metas`.
        allow_unverifiable: Treat arms with no readable metadata, and pairs
            only a declared verifier configuration could separate, as out of
            scope rather than as a verdict.

    Returns:
        ``{"verdict", "null_pairs", "undetermined_pairs", "unverifiable"}``.
        ``null_pairs`` names each pair that differs in configuration but not
        in transmission, with the differing fields; ``undetermined_pairs``
        each pair that differs in configuration, sent identical proposer
        requests, and has a verifier half that is declared, not transmitted.
    """
    checkable = [a for a in arms if not a["unverifiable_reason"]]
    unverifiable = [{"arm": a["arm"], "reason": a["unverifiable_reason"]}
                    for a in arms if a["unverifiable_reason"]]
    null_pairs, undetermined_pairs = [], []
    for a, b in itertools.combinations(checkable, 2):
        if a["config"] == b["config"]:
            continue
        relation = transmission_relation(a, b)
        if relation == SAME:
            null_pairs.append({"arms": [a["arm"], b["arm"]],
                               "config_fields_differing": differing_fields(a, b),
                               "shared_signature": sorted(a["signature"])})
        elif relation == UNDETERMINED:
            undetermined_pairs.append({"arms": [a["arm"], b["arm"]],
                                       "config_fields_differing": differing_fields(a, b)})
    if null_pairs:
        verdict = REFUSE
    elif (unverifiable or undetermined_pairs) and not allow_unverifiable:
        verdict = UNVERIFIABLE
    else:
        verdict = PASS
    return {"verdict": verdict, "null_pairs": null_pairs,
            "undetermined_pairs": undetermined_pairs, "unverifiable": unverifiable}


# ── resolving registered conditions to their metas ───────────────────────

@functools.lru_cache(maxsize=1)
def _conditions() -> dict[str, dict[str, Any]]:
    """The conditions manifest, by condition id."""
    return {c["condition_id"]: c for c in json.loads(
        (BASE_DIR / CONDITIONS_MANIFEST).read_text())["conditions"]}


@functools.lru_cache(maxsize=1)
def _analyses() -> dict[str, dict[str, Any]]:
    """The registered analyses, by analysis id."""
    return {a["analysis_id"]: a for a in json.loads(
        (BASE_DIR / RUN_ANALYSES).read_text())["analyses"]}


def _source_files(run: str, key: str) -> list[str]:
    """The source metas the passes manifest records for ``(run, key)``.

    Args:
        run: Run id.
        key: A proposer pool or verifier stage key.

    Returns:
        Repository-relative meta paths.
    """
    return [f for p in dcm._passes_index().get((run, key), [])
            for f in (p.get("provenance") or {}).get("source_files") or []]


def proposer_metas_of(run: str, pool: str) -> tuple[list[str], str | None]:
    """The proposer pass metas of a condition's pool, by the modality
    checker's two transmitted routes.

    1. ``passes-manifest`` — the source files the passes manifest records
       for ``(run, pool)``.
    2. ``pool-directory`` — the proposer metas under the pool's output
       directory, located as :func:`dcm.pool_output_dir` locates it (vote
       fraction and aggregation suffixes normalised away), its ``verified``
       and ``crops`` subtrees excluded.

    Args:
        run: Run id.
        pool: The condition's ``proposer_pool`` key.

    Returns:
        ``(meta paths, route)``; ``([], None)`` when neither route finds one.
    """
    found = _source_files(run, pool)
    if found:
        return found, "passes-manifest"
    spec = dcm.register_pool_spec(dcm._decomposition(), run, pool)
    pool_dir, _matched = dcm.pool_output_dir(run, pool, spec.get("path"))
    if pool_dir is None:
        return [], None
    root = BASE_DIR / pool_dir
    paths = []
    for depth in ("*", "*/*", "*/*/*", "*/*/*/*"):
        for f in sorted(root.glob(f"{depth}.meta.json")):
            tail = str(f)[len(str(root)):]
            if "/verified" in tail or "/crops" in tail:
                continue
            meta = dcm.read_meta(f)
            if meta and dcm.is_proposer_meta(meta):
                paths.append(str(f.relative_to(BASE_DIR)))
    return (paths, "pool-directory") if paths else ([], None)


def _register_entry(condition: dict[str, Any]) -> dict[str, Any]:
    """The condition's own entry in the register's decomposition.

    Args:
        condition: A conditions-manifest record.

    Returns:
        The ``conditions`` entry with the same label, or ``{}``.
    """
    entry = dcm._decomposition().get(condition["run_id"]) or {}
    return next((c for c in entry.get("conditions") or []
                 if c.get("label") == condition["label"]), {})


def proposer_metas_for_condition(condition: dict[str, Any]) -> tuple[list[str], str | None]:
    """A condition's proposer pass metas, from the register's own bindings.

    In order, for the condition's run and then for the run its register
    entry names as ``source_run`` (where a condition re-uses another run's
    passes):

    1. :func:`proposer_metas_of` on the condition's ``proposer_pool``;
    2. ``detections-path`` — the one registered pool whose key or path is a
       directory on the condition's registered detections path;
    3. ``sole-pool`` — the run's only registered proposer pool.

    A condition no route binds is left unverifiable, with the reason named,
    rather than matched by name (e.g. the grid's prompt-level pool
    ``brief-text`` spans four geometry pools).

    Args:
        condition: A conditions-manifest record.

    Returns:
        ``(meta paths, route)``; ``([], None)`` when no route binds it.
    """
    reg = _register_entry(condition)
    runs = [condition["run_id"]]
    if reg.get("source_run") and reg["source_run"] not in runs:
        runs.append(reg["source_run"])
    det = "/" + (reg.get("detections") or "").strip("/") + "/"
    for i, run in enumerate(runs):
        where = "" if i == 0 else f" (source_run {run})"
        found, how = proposer_metas_of(run, condition["proposer_pool"])
        if found:
            return found, f"{how}{where}"
        pools = (dcm._decomposition().get(run) or {}).get("proposer_pools") or {}
        hits = [k for k, spec in pools.items()
                if f"/{k}/" in det or (isinstance(spec, dict) and spec.get("path")
                                       and f"/{spec['path'].strip('/')}/" in det)]
        if len(hits) == 1:
            found, how = proposer_metas_of(run, hits[0])
            if found:
                return found, f"detections-path:{hits[0]}{where}"
        if len(pools) == 1:
            sole = next(iter(pools))
            found, how = proposer_metas_of(run, sole)
            if found:
                return found, f"sole-pool:{sole}{where}"
    return [], None


def verifier_stage_of(condition: dict[str, Any]) -> tuple[str | None, str]:
    """Which registered verifier stage a proposer-verifier condition used.

    Args:
        condition: A conditions-manifest record.

    Returns:
        ``(stage_key, how)``: the stage, found by the register's detections
        path lying under the stage's directory (longest match), else by the
        label naming the stage (``label == key`` or ``label`` starting
        ``key-``; longest key); ``(None, reason)`` otherwise.
    """
    run = condition["run_id"]
    entry = dcm._decomposition().get(run) or {}
    stages = entry.get("verifier_passes") or {}
    det = _register_entry(condition).get("detections") or ""
    best: tuple[str, int] | None = None
    for key, spec in stages.items():
        for cand in dcm.stage_path_candidates(run, key, spec):
            cand = cand.rstrip("/").removesuffix("/.")
            if det.startswith(cand + "/") and (best is None or len(cand) > best[1]):
                best = (key, len(cand))
    if best:
        return best[0], "detections-path"
    label = condition["label"]
    keys = [k for k in stages if label == k or label.startswith(k + "-")]
    if keys:
        return max(keys, key=len), "label"
    return None, "no registered stage contains the condition's detections or prefixes its label"


def arm_for_condition(condition_id: str) -> dict[str, Any]:
    """Build the arm for one registered condition.

    Args:
        condition_id: A ``run_id::label`` condition id.

    Returns:
        The arm (:func:`arm_from_metas`), with ``verifier_stage`` added.

    Raises:
        KeyError: The condition is not registered.
    """
    cond = _conditions()[condition_id]
    run = cond["run_id"]
    proposer, proposer_route = proposer_metas_for_condition(cond)
    verifier: list[str] = []
    declared = None
    stage, how = None, None
    if cond.get("architecture") == "proposer-verifier":
        stage, how = verifier_stage_of(cond)
        if stage:
            verifier = _source_files(run, stage)
            if not verifier:
                spec = (dcm._decomposition().get(run) or {}).get(
                    "verifier_passes", {}).get(stage)
                verifier = [m["meta_path"] for m in
                            dcm.resolve_verifier_stage(run, stage, spec)["metas"]]
        if not verifier:
            declared = cond.get("verifier_config") or None
    arm = arm_from_metas(condition_id, proposer, verifier, declared)
    arm["verifier_stage"] = {"stage": stage, "how": how}
    arm["proposer_route"] = proposer_route
    return arm


def documented_null_pair(arm_a: str, arm_b: str) -> str | None:
    """Where a null-manipulation pair of registered arms is documented.

    Args:
        arm_a: A condition id.
        arm_b: Another.

    Returns:
        The ``documented_by`` of the :data:`KNOWN_NULL_MANIPULATIONS` group
        holding both arms' ``(run_id, proposer_pool)``, else None (including
        for an arm that is not a registered condition).
    """
    keys = []
    for arm in (arm_a, arm_b):
        cond = _conditions().get(arm)
        if cond is None:
            return None
        keys.append((cond["run_id"], cond.get("proposer_pool")))
    for group in KNOWN_NULL_MANIPULATIONS:
        if keys[0] in group["pools"] and keys[1] in group["pools"]:
            return group["documented_by"]
    return None


def check_conditions(condition_ids: list[str], allow_unverifiable: bool = False
                     ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Judge a set of registered conditions as one analysis.

    Args:
        condition_ids: Condition ids.
        allow_unverifiable: See :func:`judge`.

    Returns:
        ``(judgement, arms)``. Each null pair carries ``documented_by``
        (:func:`documented_null_pair`): the document, or None for a NEW pair.
    """
    arms = [arm_for_condition(c) for c in condition_ids]
    judgement = judge(arms, allow_unverifiable)
    for pair in judgement["null_pairs"]:
        pair["documented_by"] = documented_null_pair(*pair["arms"])
    return judgement, arms


def undocumented_pairs(judgement: dict[str, Any]) -> list[dict[str, Any]]:
    """The null pairs of a judgement that no document records.

    Args:
        judgement: From :func:`judge` or :func:`check_conditions`.

    Returns:
        The NEW null pairs; a pair never labelled (an ad hoc arm outside the
        register) counts as NEW.
    """
    return [p for p in judgement["null_pairs"] if not p.get("documented_by")]


def all_exit_status(results: list[tuple[str, dict[str, Any], Any]]) -> int:
    """The ``--all`` exit status: 2 only for a refusal on an undocumented pair.

    Args:
        results: ``(analysis, judgement, arms)`` for every analysis judged.

    Returns:
        2 if any analysis has a NEW null pair; else the worst exit code of
        the analyses that do not refuse (a refusal on KNOWN pairs only
        counts as 0).
    """
    if any(undocumented_pairs(j) for _, j, _ in results):
        return EXIT_CODES[REFUSE]
    return max((EXIT_CODES[j["verdict"]] for _, j, _ in results if j["verdict"] != REFUSE),
               default=0)


def all_summary(results: list[tuple[str, dict[str, Any], Any]]) -> str:
    """The ``--all`` closing summary: which refusals are known, which new.

    Args:
        results: ``(analysis, judgement, arms)`` for every analysis judged.

    Returns:
        The text to print after the per-analysis lines.
    """
    refusing = [(name, j) for name, j, _ in results if j["verdict"] == REFUSE]
    counts = {v: sum(1 for _, j, _ in results if j["verdict"] == v)
              for v in (PASS, REFUSE, UNVERIFIABLE)}
    out = ["", f"--all: {len(results)} analyses: {counts[PASS]} PASS, {counts[REFUSE]} REFUSE, "
               f"{counts[UNVERIFIABLE]} UNVERIFIABLE"]
    for name, j in refusing:
        new = undocumented_pairs(j)
        if new:
            out.append(f"  NEW REFUSAL {name}: {len(new)} of {len(j['null_pairs'])} null pair(s) "
                       "are documented nowhere")
        else:
            docs = sorted({p["documented_by"] for p in j["null_pairs"]})
            out.append(f"  KNOWN REFUSAL {name}: all {len(j['null_pairs'])} null pair(s) "
                       f"documented ({' | '.join(docs)})")
    status = all_exit_status(results)
    reason = {0: "every refusal is documented and nothing is unverifiable",
              2: "a refusal rests on an undocumented null manipulation",
              3: ("every refusal is documented, but some analyses are unverifiable "
                  "(--allow-unverifiable treats them as out of scope)")}[status]
    out.append(f"  exit {status}: {reason}")
    return "\n".join(out)


# ── reporting ────────────────────────────────────────────────────────────

def signature_table(arms: list[dict[str, Any]]) -> str:
    """The per-arm signature table, as Markdown.

    Args:
        arms: Arms from :func:`arm_for_condition`.

    Returns:
        One row per arm: its proposer signature(s), verifier basis and stage.
    """
    lines = ["| Arm | Proposer signature(s) | Verifier | Metas |",
             "| --- | --- | --- | ---: |"]
    for a in arms:
        sigs = "<br>".join(
            ", ".join(f"{k}={v}" for k, v in json.loads(s).items() if k != "stage")
            for s in a["proposer_signatures"]) or "—"
        stage = (a.get("verifier_stage") or {}).get("stage")
        ver = f"{a['verifier_basis'] or '—'}" + (f" (`{stage}`)" if stage else "")
        lines.append(f"| `{a['arm']}` | {sigs} | {ver} | {len(a['meta_paths'])} |")
    return "\n".join(lines)


def render(name: str, judgement: dict[str, Any], arms: list[dict[str, Any]],
           report: bool) -> str:
    """Render one analysis's verdict (and optionally its table).

    Args:
        name: The analysis id or "ad hoc".
        judgement: From :func:`judge`.
        arms: The arms judged.
        report: Include the signature table.

    Returns:
        The text to print.
    """
    undetermined = judgement.get("undetermined_pairs") or []
    n_known = sum(1 for p in judgement["null_pairs"] if p.get("documented_by"))
    known = f" ({n_known} documented)" if judgement["null_pairs"] else ""
    out = [f"{judgement['verdict']} {name}: {len(arms)} arm(s), "
           f"{len(judgement['null_pairs'])} null-manipulation pair(s){known}, "
           f"{len(judgement['unverifiable'])} unverifiable arm(s), "
           f"{len(undetermined)} unverifiable pair(s) [{SIGNATURE_VERSION}]"]
    for pair in judgement["null_pairs"]:
        label = ""
        if "documented_by" in pair:
            label = (f" [KNOWN: {pair['documented_by']}]" if pair["documented_by"]
                     else " [NEW: documented nowhere]")
        out.append(f"  NULL MANIPULATION: {pair['arms'][0]} vs {pair['arms'][1]} differ in "
                   f"configuration ({', '.join(pair['config_fields_differing'])}) but "
                   f"transmitted identical requests{label}")
    for u in judgement["unverifiable"]:
        out.append(f"  UNVERIFIABLE: {u['arm']}: {u['reason']}")
    for pair in undetermined:
        out.append(f"  UNVERIFIABLE PAIR: {pair['arms'][0]} vs {pair['arms'][1]} sent identical "
                   "proposer requests and differ in configuration "
                   f"({', '.join(pair['config_fields_differing'])}), but a verifier half is "
                   "DECLARED, so whether the difference reached the model is unknown")
    declared = [a["arm"] for a in arms if a["verifier_basis"] == "declared"]
    if declared:
        out.append(f"  note: {len(declared)} arm(s) carry only a DECLARED verifier "
                   "configuration (their stage's metas could not be located). It is not "
                   "transmitted evidence, so it separated no pair; "
                   f"{len(undetermined)} pair(s) whose proposer requests matched are left "
                   "unverifiable above")
    if report:
        out += ["", signature_table(arms)]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point.

    Args:
        argv: Arguments (defaults to ``sys.argv[1:]``).

    Returns:
        The process exit status (see the module docstring).
    """
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("analysis_id", nargs="?",
                    help=f"A registered analysis id from {RUN_ANALYSES}.")
    ap.add_argument("--conditions", nargs="+", metavar="CONDITION_ID",
                    help="Judge these registered conditions as one ad hoc analysis.")
    ap.add_argument("--all", action="store_true",
                    help="Judge every registered analysis, one line each.")
    ap.add_argument("--report", action="store_true",
                    help="Print the per-arm signature table.")
    ap.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    ap.add_argument("--allow-unverifiable", action="store_true",
                    help="Treat arms with no readable pass metadata as out of scope.")
    args = ap.parse_args(argv)

    if sum(bool(x) for x in (args.analysis_id, args.conditions, args.all)) != 1:
        ap.error("give exactly one of: an analysis id, --conditions, --all")

    if args.all:
        targets = [(aid, a["conditions_compared"]) for aid, a in sorted(_analyses().items())]
    elif args.conditions:
        targets = [("ad hoc", args.conditions)]
    else:
        if args.analysis_id not in _analyses():
            print(f"ERROR: no analysis {args.analysis_id!r} in {RUN_ANALYSES}", file=sys.stderr)
            return 1
        targets = [(args.analysis_id, _analyses()[args.analysis_id]["conditions_compared"])]

    unknown = sorted({c for _, cids in targets for c in cids} - set(_conditions()))
    if unknown:
        print(f"ERROR: unregistered condition(s): {', '.join(unknown)}", file=sys.stderr)
        return 1

    results = []
    worst = 0
    for name, cids in targets:
        judgement, arms = check_conditions(cids, args.allow_unverifiable)
        worst = max(worst, EXIT_CODES[judgement["verdict"]])
        results.append((name, judgement, arms))

    if args.json:
        doc: dict[str, Any] = {"signature_version": SIGNATURE_VERSION, "analyses": [
            {"analysis": name, **judgement,
             "arms": [{k: (sorted(v) if isinstance(v, frozenset) else v)
                       for k, v in a.items()} for a in arms] if args.report else None}
            for name, judgement, arms in results]}
        if args.all:
            doc["exit_status"] = all_exit_status(results)
            doc["new_refusals"] = [n for n, j, _ in results if undocumented_pairs(j)]
        print(json.dumps(doc, indent=1))
    else:
        for name, judgement, arms in results:
            print(render(name, judgement, arms, args.report))
        if args.all:
            print(all_summary(results))
    if args.all:
        # A sweep fails on a NEW null manipulation; a documented one is a
        # known finding, listed above with its document.
        return all_exit_status(results)
    # REFUSE outranks UNVERIFIABLE: a null manipulation is a finding, an
    # unreadable arm an absence of one.
    if any(j["verdict"] == REFUSE for _, j, _ in results):
        return EXIT_CODES[REFUSE]
    return worst


if __name__ == "__main__":
    sys.exit(main())
