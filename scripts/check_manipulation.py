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

Reviewed bindings (what the register does not record)
-----------------------------------------------------
Many registered conditions score a DERIVED product: a re-score of one
detection set against another reference, a threshold or operating point
materialised from a stage's verified probabilities, a K-ladder rung, a
union of passes. The register names the product, not the stage whose
requests produced it, so until 2026-10-06 the gate left 298 arms with a
DECLARED verifier half and 43 with no proposer metas at all. Those links are
not guessed here from names: ``results/manipulation-gate-bindings.json``
(:data:`BINDINGS`) records each one as a reviewable entry — the conditions,
their registered detections, the SOURCES the documented derivation read
(the stage's output for the verifier half, the pass or pool directories for
the proposer half) and the evidence (the deriving script and lines, the
commit that added the product, the documents). The gate consults a binding
only where the register's own routes find nothing, and resolves each source
mechanically (:func:`verifier_metas_for_source`,
:func:`proposer_metas_for_source`): a verifier source to the registered
stage whose directory contains it (longest match, any run), whose metas the
W4.4 resolver (``derive_condition_modality.resolve_verifier_stage``)
locates, else to the verify metas beside it, else to where git moved it; a
proposer source to the passes-manifest source metas that lie under it, else
to the proposer metas on disk under it. A malformed bindings file, or one
naming an unregistered condition or a detections path the register does not
record for it, stops the gate (exit 1) rather than binding silently.

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

Exit codes: 0 PASS; 1 usage error (unknown analysis or condition, or an
invalid bindings file); 2 REFUSE
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

#: Reviewed bindings for links the register does not record (module docstring).
BINDINGS = "results/manipulation-gate-bindings.json"
BINDINGS_SCHEMA = "manipulation-gate-bindings/1"

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
        The harvester's record (``error`` set when unreadable, or when the
        file is JSON with no ``configuration`` block: the passes manifest
        cites ``results/run-conditions.json`` and ``run.log`` files beside
        some passes' metas, and neither records a request), with
        ``input_ids`` (the dispatched ids, a frozenset) and ``inputs`` (their
        fingerprint, see the module docstring).
    """
    p = Path(path)
    full = p if p.is_absolute() else BASE_DIR / p
    rec = harvest(str(full))
    rec["path"] = path
    if "error" not in rec and not rec.get("has_configuration"):
        rec["error"] = "no configuration block: not a pass meta"
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
                   declared_verifier: dict[str, Any] | None = None,
                   verifier_reason: str | None = None,
                   verifier_identity: str | None = None) -> dict[str, Any]:
    """Build one arm's configuration identity and transmitted signature.

    Chunk metas are set aside when the pass has a merged meta (as the
    2026-10-05 check did), so a chunked pass is not counted twice.

    The verifier half is one of four kinds (``verifier_basis``):
    ``"transmitted"`` (verifier metas were read), ``"declared"`` (only the
    register's configuration is known), ``"unverifiable"`` (the half has a
    verifier stage whose requests the gate cannot read in full) or None (no
    verifier stage). A verifier half is UNVERIFIABLE when metas were listed
    for it but none is a readable verifier meta (PR #25 review, finding 1:
    until then such an arm read as having no verifier stage, and a pair
    beside it passed as "differ in transmission"), or when the caller
    supplies ``verifier_reason`` (a dead binding source, a stage whose
    surviving meta covers only part of its requests, a binding that
    contradicts the register). Its metas are then not evidence: they join
    neither the configuration identity nor the signature.

    Args:
        arm_id: The arm's name (a condition id).
        proposer_metas: The proposer passes' meta paths.
        verifier_metas: The verifier stage's meta paths, when resolved.
        declared_verifier: The registered verifier configuration, used when
            the stage's metas are unknown. It joins the configuration
            identity (what the arm SAID) but not the transmitted signature:
            it is not evidence of what a request carried (see
            :func:`transmission_relation`).
        verifier_reason: Why the verifier half is unverifiable, when the
            caller knows (see above); None to judge by the metas alone.
        verifier_identity: What the unverifiable half read (its stage(s) or
            sources), so two arms that read the same unverifiable stage are
            recognised as one verifier configuration; defaults to the sorted
            listed metas, else the reason.

    Returns:
        ``{"arm", "config", "signature", "proposer_signatures",
        "verifier_basis", "declared_verifier", "unverifiable_verifier",
        "verifier_unverifiable_reason", "meta_paths",
        "verifier_metas_set_aside", "unreadable", "unverifiable_reason"}``.
        ``signature`` holds transmitted evidence only; ``declared_verifier``
        is the declared configuration's sorted-key JSON, or None;
        ``unverifiable_verifier`` the unverifiable half's identity marker
        (sorted-key JSON), or None; ``verifier_metas_set_aside`` the readable
        verifier metas of an unverifiable half (read, but not taken as
        evidence). ``unverifiable_reason`` concerns the proposer half and
        makes the whole arm unverifiable; ``verifier_unverifiable_reason``
        concerns the verifier half only (:func:`transmission_relation`
        decides each pair).
    """
    def readable(paths: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
        """Read metas, setting aside chunk metas beside a merged meta.

        Args:
            paths: Meta paths (duplicates are read once).

        Returns:
            ``(readable records, unreadable paths)``.
        """
        recs = [meta_record(p) for p in sorted(set(paths))]
        bad = [r["path"] for r in recs if "error" in r]
        good = [r for r in recs if "error" not in r]
        main = [r for r in good if "_chunk" not in Path(r["path"]).name] or good
        return main, bad

    prop, bad_p = readable(proposer_metas)
    ver_read, bad_v = readable(verifier_metas or [])
    # A readable meta in a verifier list that records no verifier pass is
    # not verifier evidence (it is named among the unreadable).
    ver = [r for r in ver_read if is_verifier_record(r)]
    bad_v += [r["path"] for r in ver_read if not is_verifier_record(r)]
    if verifier_metas and not ver and not verifier_reason:
        verifier_reason = (f"{len(set(verifier_metas))} verifier meta(s) listed, none readable "
                           f"as a verifier pass (e.g. {sorted(bad_v)[0]})")
    set_aside = []
    if verifier_reason:
        set_aside, ver = [r["path"] for r in ver], []
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
    declared_json = unverifiable_json = None
    if verifier_reason:
        basis = "unverifiable"
        # What the half read, not what it sent: two arms reading one
        # unverifiable stage share it, so a pair of them is judged on the
        # proposer half (as two equal declared configurations are).
        marker = {"stage": "verifier-unverifiable",
                  "of": verifier_identity or "|".join(sorted(set(verifier_metas or [])))
                  or verifier_reason}
        config.append(marker)
        unverifiable_json = json.dumps(marker, sort_keys=True)
    elif ver:
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
        "unverifiable_verifier": unverifiable_json,
        "verifier_unverifiable_reason": verifier_reason,
        "meta_paths": [r["path"] for r in prop + ver],
        "verifier_metas_set_aside": set_aside,
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
        """Each configuration field's set of encoded values across an arm.

        Args:
            arm: An arm from :func:`arm_from_metas`.

        Returns:
            Field name -> the JSON encodings of its values.
        """
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
    finding 2), and an UNVERIFIABLE half (metas listed but unreadable, a
    dead binding source, a meta covering only part of the stage) shows
    nothing at all (PR #25 review, findings 1, 2 and 4). Two equal declared
    configurations, or two unverifiable halves that read the same stage,
    leave nothing on the verifier half to separate the arms, so the
    proposer half decides. An arm with no verifier stage beside one with a
    stage (of any basis) differs: only one of them sent verifier requests.

    Args:
        a: An arm from :func:`arm_from_metas`.
        b: Another.

    Returns:
        :data:`SAME`, :data:`DIFFER` or :data:`UNDETERMINED`.
    """
    evidence = ("transmitted", None)
    if a["verifier_basis"] in evidence and b["verifier_basis"] in evidence:
        return SAME if a["signature"] == b["signature"] else DIFFER
    if _proposer_half(a) != _proposer_half(b):
        return DIFFER
    if a["verifier_basis"] is None or b["verifier_basis"] is None:
        return DIFFER
    for field in ("declared_verifier", "unverifiable_verifier"):
        if a.get(field) is not None and a.get(field) == b.get(field):
            return SAME
    return UNDETERMINED


def judge(arms: list[dict[str, Any]], allow_unverifiable: bool = False) -> dict[str, Any]:
    """Apply the rule to a set of arms.

    Args:
        arms: Arms from :func:`arm_from_metas`.
        allow_unverifiable: Treat arms with no readable metadata, and pairs
            only a declared or unverifiable verifier half could separate, as
            out of scope rather than as a verdict.

    Returns:
        ``{"verdict", "null_pairs", "undetermined_pairs", "unverifiable",
        "unverifiable_halves"}``. ``null_pairs`` names each pair that
        differs in configuration but not in transmission, with the differing
        fields; ``undetermined_pairs`` each pair that differs in
        configuration, sent identical proposer requests, and has a verifier
        half that is declared or unverifiable, not transmitted;
        ``unverifiable_halves`` each arm whose verifier half is unverifiable,
        with the reason (it makes the verdict UNVERIFIABLE only through a
        pair the proposer half cannot separate).
    """
    checkable = [a for a in arms if not a["unverifiable_reason"]]
    unverifiable = [{"arm": a["arm"], "reason": a["unverifiable_reason"]}
                    for a in arms if a["unverifiable_reason"]]
    halves = [{"arm": a["arm"], "half": "verifier",
               "reason": a.get("verifier_unverifiable_reason")}
              for a in arms if a.get("verifier_basis") == "unverifiable"]
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
            "undetermined_pairs": undetermined_pairs, "unverifiable": unverifiable,
            "unverifiable_halves": halves}


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


def _run_roots(run: str) -> frozenset[str]:
    """The directories that hold a run's whole output tree.

    Args:
        run: Run id.

    Returns:
        ``<root>/<run>`` for every :data:`derive_condition_modality.POOL_ROOTS`
        root, and ``outputs/retest/<phase>`` for a ``retest-<phase>`` run.
    """
    roots = {f"{root}/{run}" for root in dcm.POOL_ROOTS}
    if run.startswith("retest-"):
        roots.add(f"outputs/retest/{run[len('retest-'):]}")
    return frozenset(roots)


def _stage_homes(run: str, key: str, spec: Any) -> list[str]:
    """The directories a registered verifier stage may occupy, for containment.

    A stage that names its own root (``repo_path``, ruling D32) lives at
    ``<repo_path>/<path>`` and nowhere else: the run-tree candidates
    :func:`derive_condition_modality.stage_path_candidates` adds for it are
    another stage's ground. Any candidate that is a run's whole tree (a
    registered path of ``.``, as ``55maps-generalisation``'s
    ``verified-cleanup-20260410`` has) is dropped: it would make the stage
    the home of every source in the run that no deeper stage claims (PR #25
    review, finding 3).

    Args:
        run: Run id.
        key: The ``verifier_passes`` key.
        spec: Its recorded spec (a bare modality string or a dict).

    Returns:
        Repository-relative directories, normalised (no trailing ``/`` or
        ``/.``), most specific first.

    Examples:
        >>> _stage_homes("r", "k", {"path": "x", "repo_path": "archive/y"})
        ['archive/y/x']
    """
    def norm(path: str) -> str:
        """A candidate without its trailing ``/`` or ``/.``.

        Args:
            path: A candidate directory.

        Returns:
            The normalised directory.
        """
        return path.rstrip("/").removesuffix("/.").rstrip("/")

    if isinstance(spec, dict) and spec.get("repo_path") and spec.get("path"):
        return [norm(f"{spec['repo_path']}/{spec['path']}")]
    roots = _run_roots(run)
    return [c for c in map(norm, dcm.stage_path_candidates(run, key, spec)) if c not in roots]


def verifier_stage_of(condition: dict[str, Any]) -> tuple[str | None, str]:
    """Which registered verifier stage a proposer-verifier condition used.

    Args:
        condition: A conditions-manifest record.

    Returns:
        ``(stage_key, how)``: the stage, found by the register's detections
        path lying under one of the stage's homes (:func:`_stage_homes`;
        longest match), else by the label naming the stage (``label ==
        key`` or ``label`` starting ``key-``; longest key); ``(None,
        reason)`` otherwise.
    """
    run = condition["run_id"]
    entry = dcm._decomposition().get(run) or {}
    stages = entry.get("verifier_passes") or {}
    det = _register_entry(condition).get("detections") or ""
    best: tuple[str, int] | None = None
    for key, spec in stages.items():
        for cand in _stage_homes(run, key, spec):
            if det.startswith(cand + "/") and (best is None or len(cand) > best[1]):
                best = (key, len(cand))
    if best:
        return best[0], "detections-path"
    label = condition["label"]
    keys = [k for k in stages if label == k or label.startswith(k + "-")]
    if keys:
        return max(keys, key=len), "label"
    return None, "no registered stage contains the condition's detections or prefixes its label"


@functools.lru_cache(maxsize=None)
def stage_metas(run: str, key: str) -> tuple[str, ...]:
    """A registered verifier stage's metas, by the W4.4 resolver's routes.

    Args:
        run: Run id.
        key: The ``verifier_passes`` key.

    Returns:
        The passes manifest's source metas for ``(run, key)`` when one of
        them is a readable verifier meta; else the metas
        :func:`derive_condition_modality.resolve_verifier_stage` finds (stage
        directory, then git's record of an archived leg); else the
        manifest's source files as recorded, so that
        :func:`arm_from_metas` names them unreadable and the half
        UNVERIFIABLE rather than reading the stage as absent (PR #25
        review, finding 1: an absent or corrupt manifest meta used to stop
        the resolver from being consulted at all).
    """
    found = _source_files(run, key)
    if any(_is_verifier_meta(f) for f in found):
        return tuple(found)
    spec = (dcm._decomposition().get(run) or {}).get("verifier_passes", {}).get(key)
    resolved = [m["meta_path"] for m in dcm.resolve_verifier_stage(run, key, spec)["metas"]]
    return tuple(resolved or found)


# ── reviewed bindings: derived products followed to their sources ────────

class BindingError(ValueError):
    """The bindings file is malformed, or names what the register does not hold."""


def _is_relative_path(value: Any) -> bool:
    """True for a non-empty repository-relative path string.

    Args:
        value: A candidate path.

    Returns:
        Whether it is a string that is neither absolute nor climbs out of
        the repository.
    """
    return (isinstance(value, str) and bool(value) and not value.startswith("/")
            and ".." not in Path(value).parts)


def validate_bindings(doc: Any, conditions: dict[str, dict[str, Any]],
                      registered_detections: Any) -> list[str]:
    """Check a bindings document against the register; name every problem.

    Each binding must name its conditions, the registered detections they
    score (every listed condition's registered detections path must be
    among them, so an entry cannot drift from the product it was reviewed
    for), at least one source, and evidence: a derivation and a script or
    document. A condition may be bound once; a verifier source binds only a
    proposer-verifier condition.

    Args:
        doc: The parsed bindings file.
        conditions: The conditions manifest, by condition id.
        registered_detections: ``condition record -> detections path``
            (:func:`_register_entry`'s ``detections``).

    Returns:
        Problem descriptions; empty when the document is valid.

    Examples:
        >>> validate_bindings({"schema_version": "x", "bindings": []}, {}, dict.get)
        ["schema_version is 'x', expected 'manipulation-gate-bindings/1'"]
    """
    if not isinstance(doc, dict):
        return ["the bindings file is not a JSON object"]
    problems = []
    if doc.get("schema_version") != BINDINGS_SCHEMA:
        problems.append(f"schema_version is {doc.get('schema_version')!r}, "
                        f"expected {BINDINGS_SCHEMA!r}")
    ids: set[str] = set()
    bound: dict[str, str] = {}
    for i, entry in enumerate(doc.get("bindings") or []):
        name = entry.get("id") if isinstance(entry, dict) else None
        where = f"binding {name or f'#{i}'}"
        if not isinstance(entry, dict):
            problems.append(f"{where}: not an object")
            continue
        if not name:
            problems.append(f"{where}: no id")
        elif name in ids:
            problems.append(f"{where}: duplicate id")
        ids.add(name or "")
        sources = (entry.get("verifier_sources") or []) + (entry.get("proposer_sources") or [])
        if not sources:
            problems.append(f"{where}: names no verifier or proposer source")
        for field in ("detections", "verifier_sources", "proposer_sources"):
            for path in entry.get(field) or []:
                if not _is_relative_path(path):
                    problems.append(f"{where}: {field} entry {path!r} is not a "
                                    "repository-relative path")
        evidence = entry.get("evidence") or {}
        if not evidence.get("derivation"):
            problems.append(f"{where}: evidence has no derivation")
        if not (evidence.get("script") or evidence.get("documents")):
            problems.append(f"{where}: evidence cites no script or document")
        products = set(entry.get("detections") or [])
        if not products:
            problems.append(f"{where}: names no detections (the products it binds)")
        if not entry.get("conditions"):
            problems.append(f"{where}: binds no conditions")
        for cid in entry.get("conditions") or []:
            cond = conditions.get(cid)
            if cond is None:
                problems.append(f"{where}: {cid} is not a registered condition")
                continue
            if cid in bound:
                problems.append(f"{where}: {cid} is already bound by {bound[cid]}")
            bound[cid] = name or where
            det = registered_detections(cond)
            if products and det not in products:
                problems.append(f"{where}: {cid}'s registered detections {det!r} are not "
                                "among the binding's detections")
            if entry.get("verifier_sources") and cond.get("architecture") != "proposer-verifier":
                problems.append(f"{where}: {cid} is not proposer-verifier, but the binding "
                                "names verifier sources")
    return problems


@functools.lru_cache(maxsize=1)
def _bindings() -> dict[str, dict[str, Any]]:
    """The reviewed bindings, by condition id (empty when there is no file).

    Returns:
        Condition id -> its binding entry.

    Raises:
        BindingError: The file is not valid JSON, or :func:`validate_bindings`
            finds a problem.
    """
    path = BASE_DIR / BINDINGS
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise BindingError(f"{BINDINGS} is not valid JSON: {exc}") from exc
    problems = validate_bindings(doc, _conditions(),
                                 lambda cond: _register_entry(cond).get("detections"))
    if problems:
        raise BindingError(f"{BINDINGS}: " + "; ".join(problems))
    return {cid: entry for entry in doc["bindings"] for cid in entry["conditions"]}


def _under(path: str, root: str) -> bool:
    """True when ``path`` is ``root`` or lies beneath it.

    Args:
        path: A repository-relative path.
        root: A repository-relative directory.

    Returns:
        Whether ``path`` equals ``root`` or starts with ``root + "/"``.

    Examples:
        >>> _under("outputs/r/verify/probabilities.json", "outputs/r/verify")
        True
        >>> _under("outputs/r/verify_k3", "outputs/r/verify")
        False
    """
    path = path.rstrip("/")
    root = root.rstrip("/").removesuffix("/.")
    return path == root or path.startswith(root + "/")


@functools.lru_cache(maxsize=1)
def _stage_dirs() -> tuple[tuple[str, str, str], ...]:
    """Every directory a registered verifier stage may occupy, with its stage.

    Returns:
        ``(directory, run, key)`` for each of :func:`_stage_homes` of every
        stage in every run (never a run's whole tree; PR #25 review,
        finding 3).
    """
    return tuple((cand, run, key)
                 for run, entry in dcm._decomposition().items()
                 for key, spec in (entry.get("verifier_passes") or {}).items()
                 for cand in _stage_homes(run, key, spec))


def stages_containing(source: str) -> list[tuple[str, str]]:
    """The registered verifier stage(s) whose directory holds a source path.

    Args:
        source: A repository-relative path a derivation read (a stage's
            ``probabilities.json``, its ``verified/`` directory, ...).

    Returns:
        The ``(run, key)`` stages with the LONGEST directory containing the
        source (several when two runs register one directory), else ``[]``.
    """
    hits = [(len(d), run, key) for d, run, key in _stage_dirs() if _under(source, d)]
    if not hits:
        return []
    best = max(n for n, _run, _key in hits)
    return sorted({(run, key) for n, run, key in hits if n == best})


def _rel(path: str | Path) -> str:
    """A path relative to the repository when it lies inside it.

    Args:
        path: An absolute or repository-relative path.

    Returns:
        The repository-relative form, else the path unchanged.
    """
    p = Path(path)
    return str(p.relative_to(BASE_DIR)) if p.is_absolute() and p.is_relative_to(BASE_DIR) \
        else str(path)


def _is_verifier_meta(path: str) -> bool:
    """True for a readable meta that records a verifier pass.

    Args:
        path: A meta path.

    Returns:
        Whether :func:`meta_record` reads it and
        :func:`lib_manipulation_signature.is_verifier_record` holds.
    """
    rec = meta_record(path)
    return "error" not in rec and is_verifier_record(rec)


def verifier_metas_for_source(source: str) -> tuple[list[str], str | None]:
    """Follow one verifier source of a binding to the metas of its requests.

    Routes, in order:

    1. ``stage`` — the registered stage(s) whose directory contains the
       source (:func:`stages_containing`), read by :func:`stage_metas`;
    2. ``source-directory`` — for an existing directory, the verifier metas
       in it or one level below; for an existing file (a
       ``probabilities.json``), the verifier metas beside it. A source that
       does not exist is never widened to its parent;
    3. ``git-rename`` — the verifier metas among the files git moved away
       from the source (an archived leg).

    Args:
        source: A repository-relative path the derivation read.

    Returns:
        ``(meta paths, route)``; ``([], None)`` when no route reads one.
    """
    stages = stages_containing(source)
    found = sorted({m for run, key in stages for m in stage_metas(run, key)})
    if found:
        return found, "stage:" + ",".join(f"{run}/{key}" for run, key in stages)
    path = BASE_DIR / source
    candidates: list[str] = []
    if path.is_dir():
        candidates = dcm._metas_under(source)
    elif path.is_file():
        candidates = sorted(str(f) for f in path.parent.glob("*.meta.json"))
    found = [_rel(f) for f in candidates if _is_verifier_meta(f)]
    if found:
        return found, "source-directory"
    moved, commit = dcm.git_renamed_to([source])
    found = [f for f in moved if f.endswith(".meta.json") and _is_verifier_meta(f)]
    if found:
        return found, f"git-rename:{commit}"
    return [], None


@functools.lru_cache(maxsize=1)
def _manifest_sources() -> tuple[tuple[str, str, str], ...]:
    """Every source meta the passes manifest records, with its pass key.

    Returns:
        ``(meta path, run, pool or stage key)`` per recorded source file.
    """
    return tuple((f, run, key) for (run, key), passes in dcm._passes_index().items()
                 for p in passes for f in (p.get("provenance") or {}).get("source_files") or [])


def proposer_metas_for_source(source: str) -> tuple[list[str], str | None]:
    """Follow one proposer source of a binding to the metas of its passes.

    Routes, in order (a ``verified`` or ``crops`` subtree below the source is
    the verifier's, never the proposer's):

    1. ``passes-manifest`` — the source metas the passes manifest records
       under the source path that are not verifier metas;
    2. ``source-directory`` — the proposer metas on disk under the source
       (four levels, as :func:`proposer_metas_of` searches a pool);
    3. ``git-rename`` — the proposer metas git moved away from the source.

    Args:
        source: A repository-relative pass or pool directory (or one meta).

    Returns:
        ``(meta paths, route)``; ``([], None)`` when no route reads one.
    """
    def proposer_side(path: str) -> bool:
        tail = path[len(source.rstrip("/")):]
        return "/verified" not in tail and "/crops" not in tail

    hits = [(f, run, key) for f, run, key in _manifest_sources()
            if _under(f, source) and proposer_side(f)
            and not ("error" not in meta_record(f) and is_verifier_record(meta_record(f)))]
    if hits:
        keys = sorted({f"{run}/{key}" for _f, run, key in hits})
        return sorted({f for f, _run, _key in hits}), "passes-manifest:" + ",".join(keys)
    root = BASE_DIR / source
    found = []
    if root.is_file() and source.endswith(".meta.json"):
        found = [source]
    elif root.is_dir():
        for depth in ("*", "*/*", "*/*/*", "*/*/*/*"):
            for f in sorted(root.glob(f"{depth}.meta.json")):
                rel = _rel(f)
                meta = dcm.read_meta(f)
                if proposer_side(rel) and meta and dcm.is_proposer_meta(meta):
                    found.append(rel)
    if found:
        return found, "source-directory"
    moved, commit = dcm.git_renamed_to([source])
    found = [f for f in moved if f.endswith(".meta.json") and proposer_side(f)
             and (meta := dcm.read_meta(f)) and dcm.is_proposer_meta(meta)]
    if found:
        return found, f"git-rename:{commit}"
    return [], None


def _from_sources(sources: list[str], follow: Any) -> tuple[list[str], list[str], list[str]]:
    """Follow every source of one half of a binding.

    Args:
        sources: The binding's sources for one stage.
        follow: :func:`verifier_metas_for_source` or
            :func:`proposer_metas_for_source`.

    Returns:
        ``(meta paths, routes, sources that resolved nothing)``.
    """
    metas: set[str] = set()
    routes, dead = [], []
    for source in sources:
        found, route = follow(source)
        if found:
            metas.update(found)
            routes.append(route)
        else:
            dead.append(source)
    return sorted(metas), routes, dead


def _source_stage_label(source: str) -> str:
    """The verifier stage a binding source names, as the arm reports it.

    Args:
        source: A binding's verifier source (repository-relative).

    Returns:
        The registered stage(s) whose directory holds the source, as
        ``run/key`` (joined by ``|`` when two runs register one directory);
        else the source's directory, marked ``(unregistered)``. Always a
        stage, never a route (PR #25 review, finding 7).
    """
    stages = stages_containing(source)
    if stages:
        return "|".join(f"{run}/{key}" for run, key in stages)
    directory = source if (BASE_DIR / source).is_dir() or not Path(source).suffix \
        else str(Path(source).parent)
    return f"{directory} (unregistered)"


def arm_for_condition(condition_id: str) -> dict[str, Any]:
    """Build the arm for one registered condition.

    The register's own routes are tried first (:func:`proposer_metas_for_condition`,
    :func:`verifier_stage_of`); a reviewed binding (:data:`BINDINGS`) is
    consulted only for a half they leave unresolved. A binding is used
    whole or not at all: when any of a half's sources resolves no meta, the
    sources that did resolve are not a partial substitute (a missing pass
    or stage changes the inputs fingerprint and the configuration set), so
    that half is UNVERIFIABLE, with the dead sources named and a BINDING GAP
    line printed (PR #25 review, finding 2). When the register identifies
    the verifier stage but reads no meta for it, a binding is followed only
    if every verifier source lies in that same stage; a binding naming any
    other stage leaves the half UNVERIFIABLE, with both stages named
    (finding 7).

    Args:
        condition_id: A ``run_id::label`` condition id.

    Returns:
        The arm (:func:`arm_from_metas`), with ``verifier_stage``
        (``{"stage", "how"}``: a stage, never a route), ``verifier_route``
        (the binding's resolution routes, when one was followed),
        ``proposer_route``, ``binding`` (the binding's id when it supplied
        evidence, else None) and ``binding_notes`` added.

    Raises:
        KeyError: The condition is not registered.
        BindingError: The bindings file is invalid.
    """
    cond = _conditions()[condition_id]
    run = cond["run_id"]
    binding = _bindings().get(condition_id)
    used = False
    notes = []
    proposer, proposer_route = proposer_metas_for_condition(cond)
    if not proposer and binding and binding.get("proposer_sources"):
        found, routes, dead = _from_sources(binding["proposer_sources"],
                                            proposer_metas_for_source)
        if dead:
            notes.append(f"binding {binding['id']}: proposer source(s) resolved no meta: "
                         + ", ".join(dead) + (" (the other sources are not read as the "
                                              "whole pass set)" if found else ""))
        elif found:
            used = True
            proposer = found
            proposer_route = f"binding:{binding['id']}:" + "|".join(routes)
    verifier: list[str] = []
    declared = None
    stage, how, verifier_route = None, None, None
    v_reason = v_identity = None
    if cond.get("architecture") == "proposer-verifier":
        stage, how = verifier_stage_of(cond)
        if stage:
            verifier = list(stage_metas(run, stage))
        sources = (binding or {}).get("verifier_sources") or []
        bound = "|".join(dict.fromkeys(_source_stage_label(s) for s in sources))
        if not verifier and sources and stage and any(
                stages_containing(s) != [(run, stage)] for s in sources):
            # The register identified a stage (whose metas it could not
            # read) and the binding names another: neither silently wins,
            # and the stage field keeps the register's stage (PR #25
            # review, finding 7).
            v_reason = (f"binding {binding['id']} names stage(s) {bound}, but the register "
                        f"identifies stage {run}/{stage} (by {how}); the binding is not used")
            v_identity = f"{run}/{stage} vs {bound}"
        elif not verifier and sources:
            found, routes, dead = _from_sources(sources, verifier_metas_for_source)
            stage, how = bound, f"binding:{binding['id']}"
            if dead:
                note = (f"binding {binding['id']}: verifier source(s) resolved no meta: "
                        + ", ".join(dead))
                notes.append(note + (" (the other sources are not read as the whole "
                                     "stage set)" if found else ""))
                v_reason, v_identity = note, f"{stage} <- {'|'.join(sorted(sources))}"
            elif found:
                used = True
                verifier, verifier_route = found, "|".join(routes)
        if not verifier and not v_reason:
            declared = cond.get("verifier_config") or None
    arm = arm_from_metas(condition_id, proposer, verifier, declared,
                         verifier_reason=v_reason, verifier_identity=v_identity)
    proposer_notes = [n for n in notes if ": proposer source(s)" in n]
    if not proposer and proposer_notes and arm["unverifiable_reason"]:
        arm["unverifiable_reason"] += "; " + "; ".join(proposer_notes)
    arm["verifier_stage"] = {"stage": stage, "how": how}
    arm["verifier_route"] = verifier_route
    arm["proposer_route"] = proposer_route
    arm["binding"] = binding["id"] if binding and used else None
    arm["binding_notes"] = notes
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
    halves = judgement.get("unverifiable_halves") or []
    n_halves = f", {len(halves)} unverifiable verifier half(s)" if halves else ""
    out = [f"{judgement['verdict']} {name}: {len(arms)} arm(s), "
           f"{len(judgement['null_pairs'])} null-manipulation pair(s){known}, "
           f"{len(judgement['unverifiable'])} unverifiable arm(s), "
           f"{len(undetermined)} unverifiable pair(s){n_halves} [{SIGNATURE_VERSION}]"]
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
    for h in halves:
        out.append(f"  UNVERIFIABLE VERIFIER HALF: {h['arm']}: {h['reason']}")
    for pair in undetermined:
        out.append(f"  UNVERIFIABLE PAIR: {pair['arms'][0]} vs {pair['arms'][1]} sent identical "
                   "proposer requests and differ in configuration "
                   f"({', '.join(pair['config_fields_differing'])}), but a verifier half is "
                   "DECLARED or UNVERIFIABLE, so whether the difference reached the model is "
                   "unknown")
    bound = sorted({a["binding"] for a in arms if a.get("binding")})
    if bound:
        n_bound = sum(1 for a in arms if a.get("binding"))
        out.append(f"  note: {n_bound} arm(s) resolved through reviewed bindings in "
                   f"{BINDINGS} ({', '.join(bound)})")
    for a in arms:
        for note in a.get("binding_notes") or []:
            out.append(f"  BINDING GAP: {a['arm']}: {note}")
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
    try:
        for name, cids in targets:
            judgement, arms = check_conditions(cids, args.allow_unverifiable)
            worst = max(worst, EXIT_CODES[judgement["verdict"]])
            results.append((name, judgement, arms))
    except BindingError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

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
