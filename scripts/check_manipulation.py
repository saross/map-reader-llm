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
Per-meta field extraction is the 2026-10-05 harvester's own
``harvest()``, imported from ``reports/manipulation-check-2026-10-05-scripts/
harvest.py`` (:data:`HARVEST_SCRIPT`). ``arms.py`` there runs at import time
against hard-coded paths, so its ``signature()``, ``_model_of_record()`` and
``eff_temp()`` are COPIED below with attribution (and extended by
``max_output_tokens`` and ``inputs``).

Arms are resolved through ``results/passes-manifest.json``
(``provenance.source_files`` per pass), falling back to the pool's output
directory, the register's ``source_run``, the pool named on the condition's
detections path, and a run's sole pool (:func:`proposer_metas_for_condition`):
the proposer pool's passes, and for a proposer-verifier condition its
verifier stage's passes. A condition's stage
is found from the register's own detections path, else from its label; a
stage that cannot be found leaves the verifier part DECLARED (the
condition's registered ``verifier_config``), which can distinguish arms but
never refuse them.

Usage
-----
    # Gate one registered analysis (exit 0 PASS, 2 REFUSE, 3 UNVERIFIABLE)
    python3 scripts/check_manipulation.py era1-leaderboard

    # The same, with the per-arm signature table
    python3 scripts/check_manipulation.py era1-leaderboard --report

    # An ad hoc set of conditions
    python3 scripts/check_manipulation.py --conditions RUN::LABEL RUN::LABEL

    # Every registered analysis, one line each (exit 2 if any refuses)
    python3 scripts/check_manipulation.py --all

Exit codes: 0 PASS; 1 usage error (unknown analysis or condition); 2 REFUSE
(a null manipulation); 3 UNVERIFIABLE (an arm with no readable pass metadata,
unless ``--allow-unverifiable``).
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts import derive_condition_modality as dcm  # noqa: E402

#: The 2026-10-05 harvester, imported for its per-meta field extraction.
HARVEST_SCRIPT = BASE_DIR / "reports" / "manipulation-check-2026-10-05-scripts" / "harvest.py"

RUN_ANALYSES = "results/run-analyses.json"
CONDITIONS_MANIFEST = "results/conditions-manifest.json"

#: The signature definition's version (see the module docstring).
SIGNATURE_VERSION = "manipulation-signature/1"

#: The fields of a transmitted signature, in order.
SIGNATURE_FIELDS = ("stage", "model", "temperature_eff", "thinking", "sys_hash",
                    "examples_sent", "tile_size", "max_output_tokens", "inputs")

#: The fields of a configuration identity, in order.
CONFIG_FIELDS = ("stage", "version", "instruction_file", "model", "temperature",
                 "thinking_level", "listed_library", "include_example_images",
                 "ordering", "text_only_labels", "tile_size", "max_output_tokens")

#: Verdicts and their exit codes.
PASS, REFUSE, UNVERIFIABLE = "PASS", "REFUSE", "UNVERIFIABLE"
EXIT_CODES = {PASS: 0, REFUSE: 2, UNVERIFIABLE: 3}


def _load_harvest():
    """Import the 2026-10-05 harvester's ``harvest`` function.

    Returns:
        The ``harvest(path) -> dict`` function.

    Raises:
        ImportError: The provenance script has moved; update
            :data:`HARVEST_SCRIPT`.
    """
    spec = importlib.util.spec_from_file_location("manipulation_harvest", HARVEST_SCRIPT)
    if spec is None or spec.loader is None or not HARVEST_SCRIPT.exists():
        raise ImportError(f"the manipulation-check harvester is not at {HARVEST_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.harvest


_harvest = _load_harvest()


def dispatched_ids(meta: dict[str, Any]) -> frozenset[str]:
    """The ids of every item a pass dispatched (its tiles, or its candidates).

    Args:
        meta: A parsed ``*.meta.json``.

    Returns:
        ``execution_stats`` ``completed_items`` plus ``failed_items`` ids.

    Examples:
        >>> sorted(dispatched_ids({"execution_stats": {"completed_items": ["b", "a"],
        ...     "failed_items": [{"item_id": "c"}]}}))
        ['a', 'b', 'c']
    """
    stats = meta.get("execution_stats") or {}
    ids = {str(i) for i in stats.get("completed_items") or [] if i is not None}
    for f in stats.get("failed_items") or []:
        item = f.get("item_id") if isinstance(f, dict) else f
        if item is not None:
            ids.add(str(item))
    return frozenset(ids)


def inputs_fingerprint(ids: frozenset[str] | set[str], manifest_path: str | None = None) -> str:
    """The ``inputs`` signature field for a set of dispatched ids.

    Args:
        ids: Dispatched item ids (one pass's, or the union over an arm).
        manifest_path: The recorded manifest path, used when no ids are.

    Returns:
        ``"<first 12 hex of sha256 over the sorted ids>/<n>"``; else
        ``"manifest:<path>"``; else ``"unrecorded"``.

    Examples:
        >>> inputs_fingerprint(frozenset({"a", "b"})).endswith("/2")
        True
        >>> inputs_fingerprint(frozenset())
        'unrecorded'
    """
    if ids:
        digest = hashlib.sha256(json.dumps(sorted(ids)).encode()).hexdigest()
        return f"{digest[:12]}/{len(ids)}"
    if manifest_path:
        return f"manifest:{manifest_path}"
    return "unrecorded"


@functools.lru_cache(maxsize=None)
def meta_record(path: str) -> dict[str, Any]:
    """One meta's harvested fields, plus the output budget the harvester omits.

    Args:
        path: Repository-relative or absolute ``*.meta.json`` path.

    Returns:
        The harvester's record (``error`` set when unreadable), with
        ``max_output_tokens`` added from ``configuration`` or its snapshot,
        and ``inputs`` (the dispatched-item fingerprint, see the module
        docstring).
    """
    p = Path(path)
    full = p if p.is_absolute() else BASE_DIR / p
    rec = dict(_harvest(str(full)))
    rec["path"] = path
    if "error" not in rec:
        try:
            meta = json.loads(full.read_text())
        except (OSError, ValueError):
            meta = {}
        cfg = meta.get("configuration") or {}
        snap = cfg.get("full_config_snapshot") or {}
        rec["max_output_tokens"] = cfg.get("max_output_tokens", snap.get("max_output_tokens"))
        rec["input_ids"] = dispatched_ids(meta)
        rec["inputs"] = inputs_fingerprint(rec["input_ids"], rec.get("manifest_path"))
    return rec


# ── copied from reports/manipulation-check-2026-10-05-scripts/arms.py ────
# (2026-10-05, Session 160; that script runs at import against hard-coded
# paths, so these three functions are copied rather than imported. Change
# made here: max_output_tokens and inputs added to the signature.)

def eff_temp(r: dict[str, Any]) -> Any:
    """Effective temperature of a record: ``temperature_effective`` if set (E55).

    Args:
        r: A harvested meta record.

    Returns:
        The effective temperature, else the configured one.
    """
    t = r.get("temperature_effective")
    return t if t is not None else r.get("temperature")


def _model_of_record(r: dict[str, Any]) -> Any:
    """What ran: per-item model_version, else pricing model, else config (E57).

    Args:
        r: A harvested meta record.

    Returns:
        The model of record.
    """
    pm = r.get("pim_models") or []
    if len(pm) == 1:
        return pm[0]
    if r.get("pricing_model"):
        return r["pricing_model"]
    return r.get("model")


def is_verifier_record(r: dict[str, Any]) -> bool:
    """True for a verifier pass's meta (verify config or verifier script).

    Args:
        r: A harvested meta record.

    Returns:
        Whether the record is a verifier pass.
    """
    return str(r.get("version") or "").startswith("verify_") or \
        r.get("script") in ("run_pv.py", "5_verify_crops.py")


def signature(r: dict[str, Any]) -> dict[str, Any]:
    """Transmitted signature of one meta record (:data:`SIGNATURE_FIELDS`).

    Args:
        r: A harvested meta record (:func:`meta_record`).

    Returns:
        The signature dict.

    Examples:
        >>> sig = signature({"version": "detect_x", "temperature": 0.7,
        ...     "images_sent_by_config": False, "listed_example_n": 17,
        ...     "listed_library_fp": "abc", "sys_hash": "e169b7237b85ffff"})
        >>> (sig["stage"], sig["examples_sent"], sig["sys_hash"])
        ('proposer', 'none', 'e169b7237b85')
    """
    if is_verifier_record(r):
        # lib_verifier.build_reference_items: text_only_labels win; else
        # every listed example is sent as an image (no include flag read).
        tl = r.get("text_only_labels") or []
        if tl:
            sent = "text-labels:" + str(len(tl))
        elif r.get("listed_example_n"):
            sent = "images:" + r["listed_library_fp"] + f"/{r['listed_example_n']}"
        else:
            sent = "none"
    else:
        if r.get("images_sent_by_config") and r.get("listed_example_n"):
            sent = "images:" + r["listed_library_fp"] + f"/{r['listed_example_n']}"
        else:
            sent = "none"
    return {
        "stage": "verifier" if is_verifier_record(r) else "proposer",
        "model": _model_of_record(r),
        "temperature_eff": eff_temp(r),
        "thinking": r.get("thinking_level"),
        "sys_hash": (r.get("sys_hash") or "")[:12] or None,
        "examples_sent": sent,
        "tile_size": r.get("tile_size"),
        "max_output_tokens": r.get("max_output_tokens"),
        "inputs": r.get("inputs"),
    }

# ── end of the copied functions ──────────────────────────────────────────


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
        declared_verifier: The registered verifier configuration, used as
            both identity and signature when the stage's metas are unknown
            (it can distinguish arms but never make them look identical).

    Returns:
        ``{"arm", "config", "signature", "proposer_signatures",
        "verifier_basis", "meta_paths", "unreadable", "unverifiable_reason"}``.
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
    if ver:
        basis = "transmitted"
    elif declared_verifier:
        basis = "declared"
        declared = {"stage": "verifier-declared", **declared_verifier}
        config.append(declared)
        sigs.append(declared)
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


def judge(arms: list[dict[str, Any]], allow_unverifiable: bool = False) -> dict[str, Any]:
    """Apply the rule to a set of arms.

    Args:
        arms: Arms from :func:`arm_from_metas`.
        allow_unverifiable: Treat arms with no readable metadata as out of
            scope rather than as a verdict.

    Returns:
        ``{"verdict", "null_pairs", "unverifiable"}``. ``null_pairs`` names
        each pair that differs in configuration but not in signature, with
        the differing fields.
    """
    checkable = [a for a in arms if not a["unverifiable_reason"]]
    unverifiable = [{"arm": a["arm"], "reason": a["unverifiable_reason"]}
                    for a in arms if a["unverifiable_reason"]]
    null_pairs = []
    for a, b in itertools.combinations(checkable, 2):
        if a["config"] != b["config"] and a["signature"] == b["signature"]:
            null_pairs.append({"arms": [a["arm"], b["arm"]],
                               "config_fields_differing": differing_fields(a, b),
                               "shared_signature": sorted(a["signature"])})
    if null_pairs:
        verdict = REFUSE
    elif unverifiable and not allow_unverifiable:
        verdict = UNVERIFIABLE
    else:
        verdict = PASS
    return {"verdict": verdict, "null_pairs": null_pairs, "unverifiable": unverifiable}


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


def check_conditions(condition_ids: list[str], allow_unverifiable: bool = False
                     ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Judge a set of registered conditions as one analysis.

    Args:
        condition_ids: Condition ids.
        allow_unverifiable: See :func:`judge`.

    Returns:
        ``(judgement, arms)``.
    """
    arms = [arm_for_condition(c) for c in condition_ids]
    return judge(arms, allow_unverifiable), arms


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
    out = [f"{judgement['verdict']} {name}: {len(arms)} arm(s), "
           f"{len(judgement['null_pairs'])} null-manipulation pair(s), "
           f"{len(judgement['unverifiable'])} unverifiable arm(s) "
           f"[{SIGNATURE_VERSION}]"]
    for pair in judgement["null_pairs"]:
        out.append(f"  NULL MANIPULATION: {pair['arms'][0]} vs {pair['arms'][1]} differ in "
                   f"configuration ({', '.join(pair['config_fields_differing'])}) but "
                   "transmitted identical requests")
    for u in judgement["unverifiable"]:
        out.append(f"  UNVERIFIABLE: {u['arm']}: {u['reason']}")
    declared = [a["arm"] for a in arms if a["verifier_basis"] == "declared"]
    if declared:
        out.append(f"  note: {len(declared)} arm(s) carry a DECLARED verifier configuration "
                   "(their stage's metas could not be located); it can separate arms "
                   "but cannot show a verifier-side null manipulation")
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
        print(json.dumps({"signature_version": SIGNATURE_VERSION, "analyses": [
            {"analysis": name, **judgement,
             "arms": [{k: (sorted(v) if isinstance(v, frozenset) else v)
                       for k, v in a.items()} for a in arms] if args.report else None}
            for name, judgement, arms in results]}, indent=1))
    else:
        for name, judgement, arms in results:
            print(render(name, judgement, arms, args.report))
    # REFUSE outranks UNVERIFIABLE: a null manipulation is a finding, an
    # unreadable arm an absence of one.
    if any(j["verdict"] == REFUSE for _, j, _ in results):
        return EXIT_CODES[REFUSE]
    return worst


if __name__ == "__main__":
    sys.exit(main())
