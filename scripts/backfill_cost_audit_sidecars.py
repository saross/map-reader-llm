#!/usr/bin/env python3
"""
Back-fill a ``cost_audit.json`` sidecar beside every historical meta that recorded usage.

Why this script exists
----------------------
The historical run metas under ``outputs/`` carry a ``cost_estimate`` written
at the call site, before the cost accounting fix: no cache rate, and on the
verifier path no tier (``planning/cost-accounting-fix-plan-2026-09-21.md``
§ 1.3). PI ruling D14 leaves those metas exactly as written and puts an
audited sidecar beside each one instead; ruling D28 says what the sidecar
holds: a COPY of the passes register's figure (``results/passes-manifest.json``),
so the register stays the one source of truth and the sidecar is only the
pointer a reader of the meta finds beside it. This is deliverable A of WP4
(``planning/wp4-backfill-design-2026-10-04.md`` § A).

What it writes
--------------
For every ``outputs/**/*.meta.json`` whose usage (as
:func:`scripts.lib_pass_cost.fragment_usage` reads it, the same usage the
register prices) is recorded and non-zero:

* **Name.** ``cost_audit.json`` beside ``run.meta.json`` (the plan's own
  name); ``<stem>.cost_audit.json`` beside any other ``<stem>.meta.json``.
  The two forms cannot collide: only ``run.meta.json`` maps to the bare name,
  and every other sidecar name carries a ``.`` before ``cost_audit``. The
  sidecar name never ends in ``.meta.json``, so no meta glob picks it up.
* **A register fragment** (the meta is named in a row's
  ``cost_source.fragments``, or, for a row published from a report with no
  fragments, in its ``provenance.source_files``): ``"in_register": true`` and,
  per row, the row's ``pass_id``, ``cost_usd`` and ``cost_basis``, the
  fragment's own record as the register holds it (model, tier,
  ``tier_method``, ``priced_at``, evidence, and any candidates, conflicts or
  notes), the row's other ``cost_source`` keys (rate card, bounds, note,
  published source), the metas of all the row's fragments, and the row's
  provenance stamp; plus the register's ``generated_at``,
  ``generator_version`` and ``schema_version``. Nothing is re-priced.
* **Not in the register** (smoke tests, probes, superseded or archived
  executions, batch staging chunks, and runs the register does not extract):
  ``"in_register": false`` with the reason, priced by
  :meth:`scripts.lib_pass_cost.PassCoster.cost_fragment`, the register's own
  per-fragment pricing: the meta's own tokens through
  :func:`scripts.lib_cost.price_usage` at its end date, at the tier the
  committed evidence resolves for that one meta (served-tier headers, batch
  markers, runner records, run logs, launch manifests, attestations, billing
  days). Where the evidence leaves several tiers, the meta is priced at each
  and published at the highest with the candidates beside it
  (``audited-upper-bound``), exactly as the register does. A chunk of a
  chunked Batch API pass whose merged meta the register prices also gets a
  ``merged_into`` pointer: its tokens are already inside that row, so its
  figure is for reference and must not be added to the register's
  (:func:`chunk_links` says how the link is verified). A verifier meta
  that accounts for fewer candidates than its ``probabilities.json`` holds,
  below the register's coverage floor, is published as
  ``audited-lower-bound`` with the count beside it, as the register
  publishes such a leg, unless the stage carried the missing results
  forward from a stage priced elsewhere (:func:`leg_coverage`).
* **Zero or unrecorded usage**: no sidecar (plan § 4.5; such passes are
  ``null`` with ``cost_basis: unrecorded`` in the register, D12).

Determinism: JSON with ``indent=2``, sorted keys and a trailing newline;
repository-relative paths only; no clock is read (the sidecar carries the
register's ``generated_at``). So ``--check`` is byte-stable, and it turns red
whenever the register is regenerated without a sidecar refresh.

Metas are opened for reading only (D14). The writer refuses to overwrite a
file that is not one of its own sidecars, and never deletes: a stale sidecar
(its meta gone or now zero-usage) is reported, and ``--check`` fails on it.

Usage::

    python scripts/backfill_cost_audit_sidecars.py            # dry run: report
    python scripts/backfill_cost_audit_sidecars.py --write    # write the sidecars
    python scripts/backfill_cost_audit_sidecars.py --check    # exit 1 on drift

Zero API calls; reads about 1,500 JSON files (seconds of compute).

Created: 2026-10-04 (WP4 § A of the cost accounting plan, Session 159)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.lib_cost import is_unrecorded, token_classes  # noqa: E402
from scripts.lib_pass_cost import (  # noqa: E402
    COVERAGE_FLOOR,
    PassCoster,
    fragment_usage,
    verifier_coverage,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: The sidecar's own schema tag: the writer overwrites only files carrying it.
SCHEMA = "cost_audit/1"
#: This writer's version, stamped into every sidecar.
GENERATOR_VERSION = "1.0.0"
#: The script's repository-relative path, stamped into every sidecar.
GENERATOR = "scripts/backfill_cost_audit_sidecars.py"

META_SUFFIX = ".meta.json"
RUN_META = "run.meta.json"
RUN_SIDECAR = "cost_audit.json"
SIDECAR_SUFFIX = ".cost_audit.json"

#: The fields a register row's fragment record is matched under.
BY_FRAGMENT = "cost_source.fragments"
BY_SOURCE = "provenance.source_files"


class BackfillError(RuntimeError):
    """The sidecars cannot be planned or written safely."""


# ---------------------------------------------------------------------------
# Naming and reading.
# ---------------------------------------------------------------------------


def sidecar_path(meta_path: Path) -> Path:
    """The sidecar a meta's audited cost is written to.

    Args:
        meta_path: A ``*.meta.json`` file.

    Returns:
        ``cost_audit.json`` beside ``run.meta.json``; ``<stem>.cost_audit.json``
        beside any other ``<stem>.meta.json``.

    Raises:
        BackfillError: For a file not named ``*.meta.json``.

    Examples:
        >>> sidecar_path(Path("a/run.meta.json")).as_posix()
        'a/cost_audit.json'
        >>> sidecar_path(Path("a/detections-x-2026-04-09.meta.json")).as_posix()
        'a/detections-x-2026-04-09.cost_audit.json'
    """
    name = meta_path.name
    if not name.endswith(META_SUFFIX):
        raise BackfillError(f"{meta_path} is not a *{META_SUFFIX} file")
    if name == RUN_META:
        return meta_path.with_name(RUN_SIDECAR)
    return meta_path.with_name(name[: -len(META_SUFFIX)] + SIDECAR_SUFFIX)


def is_sidecar_name(name: str) -> bool:
    """Whether a file name is one this writer produces (for the stale-sidecar sweep).

    Examples:
        >>> is_sidecar_name("cost_audit.json"), is_sidecar_name("x.cost_audit.json")
        (True, True)
        >>> is_sidecar_name("run.meta.json")
        False
    """
    return name == RUN_SIDECAR or name.endswith(SIDECAR_SUFFIX)


def tracked_files(repo_root: Path) -> set[Path] | None:
    """The repository's git-tracked files (resolved), or ``None`` outside a git checkout.

    The back-fill is for the committed, historical metas (D14). A meta that
    exists on one machine only (sapphire held two untracked batch-staging
    merges on 2026-10-04) must not change the plan, or the committed sidecars
    would be current on one machine and drifted on another.
    """
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=repo_root, check=True,
                             capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {(repo_root / name).resolve() for name in out.decode("utf-8").split("\0") if name}


def enumerate_metas(outputs_dir: Path) -> list[Path]:
    """Every ``*.meta.json`` file beneath *outputs_dir*, sorted.

    Args:
        outputs_dir: The tree to walk (``outputs/``).

    Returns:
        Regular files only, in sorted path order, so the run is reproducible.
    """
    return sorted(p for p in outputs_dir.rglob("*" + META_SUFFIX) if p.is_file())


def rel_path(path: Path, repo_root: Path) -> str:
    """Repository-relative POSIX path of *path*.

    Raises:
        BackfillError: For a path outside the repository (a sidecar must never
            carry a machine-specific absolute path).
    """
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise BackfillError(f"{path} lies outside the repository {repo_root}") from exc


def read_json(path: Path) -> Any:
    """Parse a JSON file (UTF-8)."""
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def usage_status(meta: dict[str, Any]) -> tuple[str, dict[str, Any], str | None]:
    """Whether a meta recorded usage, read the way the register reads it.

    Args:
        meta: A parsed meta.

    Returns:
        ``(status, usage, note)``: status is ``recorded``, ``zero`` (the block
        reports responses but every token class is zero) or ``unrecorded``
        (:func:`scripts.lib_cost.is_unrecorded`); ``usage`` and ``note`` are
        :func:`scripts.lib_pass_cost.fragment_usage`'s.
    """
    usage, note = fragment_usage(meta)
    if not usage or is_unrecorded(usage):
        return "unrecorded", usage, note
    if not any(token_classes(usage).values()):
        return "zero", usage, note
    return "recorded", usage, note


def render(doc: dict[str, Any]) -> str:
    """The sidecar's exact text: indent 2, sorted keys, trailing newline."""
    return json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# The register.
# ---------------------------------------------------------------------------


def register_stamp(register: dict[str, Any], register_rel: str) -> dict[str, Any]:
    """The register identity every sidecar carries (no clock is read)."""
    return {"path": register_rel, "generated_at": register.get("generated_at"),
            "generator_version": register.get("generator_version"),
            "schema_version": register.get("schema_version")}


def index_register(register: dict[str, Any]) -> dict[str, list[tuple[str, dict, dict | None]]]:
    """Map each meta path the register cites to the rows that cite it.

    A meta is matched under ``cost_source.fragments`` (the metas that priced
    the row). Only a row with NO fragments at all (the two legs whose figure
    is published from their report, D13) is matched under
    ``provenance.source_files`` instead, with no fragment record: a meta a
    priced row cites as provenance but did not price is not in its figure,
    so it is treated as outside the register.

    Args:
        register: The parsed passes register.

    Returns:
        ``{meta_path: [(matched_by, row, fragment_or_None), ...]}``.
    """
    index: dict[str, list[tuple[str, dict, dict | None]]] = {}
    for row in register.get("passes") or []:
        fragments = (row.get("cost_source") or {}).get("fragments") or []
        priced = set()
        for frag in fragments:
            meta = frag.get("meta")
            if meta and meta not in priced:
                priced.add(meta)
                index.setdefault(meta, []).append((BY_FRAGMENT, row, frag))
        if fragments:
            continue
        for src in dict.fromkeys((row.get("provenance") or {}).get("source_files") or []):
            if src.endswith(META_SUFFIX):
                index.setdefault(src, []).append((BY_SOURCE, row, None))
    return index


def register_entry(matched_by: str, row: dict[str, Any],
                   fragment: dict[str, Any] | None) -> dict[str, Any]:
    """One row's copy in a sidecar: the register's figures, verbatim.

    Args:
        matched_by: :data:`BY_FRAGMENT` or :data:`BY_SOURCE`.
        row: The register row.
        fragment: The row's fragment record for this meta, or None.

    Returns:
        ``pass_id``, ``cost_usd``, ``cost_basis``, the fragment record, the
        row's other ``cost_source`` keys, its fragment metas, and its
        provenance stamp.
    """
    source = row.get("cost_source") or {}
    prov = row.get("provenance") or {}
    return {
        "pass_id": row.get("pass_id"),
        "cost_usd": row.get("cost_usd"),
        "cost_basis": row.get("cost_basis"),
        "matched_by": matched_by,
        "fragment": fragment,
        "row_cost_source": {k: v for k, v in source.items() if k != "fragments"},
        "row_fragment_metas": [f.get("meta") for f in source.get("fragments") or []],
        "row_provenance": {"last_extracted_at": prov.get("last_extracted_at"),
                           "extractor_version": prov.get("extractor_version")},
    }


# ---------------------------------------------------------------------------
# Metas outside the register.
# ---------------------------------------------------------------------------


def run_context(meta_rel: str, runs: list[dict[str, Any]]) -> tuple[str, str, bool]:
    """The run a meta belongs to, for the tier walk and attestation lookup.

    Args:
        meta_rel: The meta's repository-relative path.
        runs: ``results/run-registry.json``'s ``registry`` entries.

    Returns:
        ``(run_id, run_dir, registered)``: the registered run whose
        ``directory_path`` is the longest prefix of the meta's path; else the
        meta's first directory under ``outputs/``, named for itself and
        marked unregistered.
    """
    best: tuple[str, str] | None = None
    for run in runs:
        prefix = str(run.get("directory_path") or "").rstrip("/")
        if prefix and meta_rel.startswith(prefix + "/") and (
                best is None or len(prefix) > len(best[1])):
            best = (str(run["run_id"]), prefix)
    if best:
        return best[0], best[1], True
    parts = meta_rel.split("/")
    run_dir = "/".join(parts[:2]) if len(parts) > 2 else parts[0]
    return run_dir.rsplit("/", 1)[-1], run_dir, False


def meta_stage(meta_path: Path) -> str:
    """``verifier`` or ``proposer``, by the register's own file-naming split.

    The register reads a verifier leg from ``run.meta.json`` (directory form)
    or ``verified-*.meta.json`` beside its GeoJSON (sidecar form), and every
    proposer fragment from a ``detections-*.meta.json``; on the committed
    register no proposer fragment is named either way.
    """
    name = meta_path.name
    return "verifier" if name == RUN_META or name.startswith("verif") else "proposer"


def meta_model(meta: dict[str, Any]) -> tuple[str | None, str]:
    """The model a meta is priced at, and the field it came from.

    The per-item ``model_used`` (what the API dispatched; the register's
    authority for verifier legs and recovery fragments), else
    ``configuration.model``, else the model its call-site cost block priced.
    """
    pim = meta.get("per_item_metadata") or []
    own = next((it.get("model_used") for it in pim
                if isinstance(it, dict) and it.get("model_used")), None)
    if own:
        return str(own), "per_item_metadata.model_used"
    cfg = (meta.get("configuration") or {}).get("model")
    if cfg:
        return str(cfg), "configuration.model"
    priced = ((meta.get("cost_estimate") or {}).get("pricing_used") or {}).get("model")
    if priced:
        return str(priced), "cost_estimate.pricing_used.model"
    return None, "none recorded"


def chunk_links(parsed: dict[str, tuple[Path, dict[str, Any], dict[str, int]]],
                index: dict[str, list[tuple[str, dict, dict | None]]]
                ) -> dict[str, dict[str, Any]]:
    """Chunk metas whose tokens a register fragment already carries, merged.

    A chunked Batch API pass (``scripts/lib_batch_api.py`` merge) writes one
    meta per chunk in a staging directory and a merged meta for the pass
    whose ``usage_stats`` is their sum; the register prices the merged meta
    and never a chunk (``generate_post_run_report._sibling_metas``). The
    merged meta lists its chunks by file NAME only, and two staging
    directories can hold the same names (``batch-staging-run4`` and ``-run5``
    of ``gemini37-image-55map-2026-09-13``), so a directory is linked only
    when its listed chunks' summed token classes equal the merged meta's
    exactly, and only when exactly one directory does.

    Args:
        parsed: ``{meta_rel: (path, meta, token_classes)}`` for every meta with
            recorded usage.
        index: :func:`index_register`'s map.

    Returns:
        ``{chunk_meta_rel: {"meta": merged_rel, "pass_ids": [...],
        "verified_by": ...}}``.
    """
    by_name: dict[str, list[str]] = {}
    for rel in parsed:
        by_name.setdefault(rel.rsplit("/", 1)[-1], []).append(rel)
    links: dict[str, dict[str, Any]] = {}
    for merged_rel, (_, meta, classes) in sorted(parsed.items()):
        names = (meta.get("chunked_run") or {}).get("chunk_metas") or []
        hits = [h for h in index.get(merged_rel) or [] if h[0] == BY_FRAGMENT]
        if not names or not hits:
            continue
        groups: dict[str, list[str]] = {}
        for name in names:
            for rel in by_name.get(str(name), []):
                groups.setdefault(rel.rsplit("/", 1)[0], []).append(rel)
        matching = []
        for rels in groups.values():
            if len(rels) != len(names):
                continue
            summed = {k: sum(parsed[r][2][k] for r in rels) for k in classes}
            if summed == classes:
                matching.append(rels)
        if len(matching) != 1:
            continue
        for rel in matching[0]:
            links[rel] = {
                "meta": merged_rel,
                "pass_ids": sorted(str(h[1].get("pass_id")) for h in hits),
                "verified_by": (f"listed in the merged meta's chunked_run.chunk_metas, and the "
                                f"{len(names)} chunks' summed token classes equal its usage "
                                "exactly"),
            }
    return links


#: The schema of the provenance a carry-forward verifier stage writes.
CARRY_SCHEMA = "verifier-stage-carry/1"


def carried_forward(directory: Path) -> tuple[int, str] | None:
    """Results a verifier stage carried from an earlier stage, unverified again.

    A stage rebuilt over a re-numbered union (the ``*_recovery-fixed``
    stages) copies the earlier stage's results into its own
    ``probabilities.json`` and verifies only the candidates it could not
    match; ``carry_provenance.json`` records how many it carried and from
    where. Those results' spend belongs to the stage it extends.

    Args:
        directory: The verifier stage's directory.

    Returns:
        ``(carried, extends_stage, uncovered)``, or None when the stage carries
        nothing or the file is malformed (no schema, counts, or extended stage).
    """
    path = directory / "carry_provenance.json"
    if not path.is_file():
        return None
    doc = read_json(path)
    if not isinstance(doc, dict) or doc.get("schema") != CARRY_SCHEMA:
        return None
    carried, uncovered = doc.get("carried"), doc.get("uncovered")
    extends = str(doc.get("extends_stage") or "")
    if not isinstance(carried, int) or carried <= 0 or not isinstance(uncovered, int) \
            or uncovered < 0 or not extends:
        return None
    return carried, extends, uncovered


def _stage_exists(meta_path: Path, stage: str) -> bool:
    """Whether a repository-relative stage directory exists, found from a meta's path."""
    for parent in meta_path.resolve().parents:
        if (parent / ".git").exists() or (parent / "results" / "passes-manifest.json").exists():
            return (parent / stage).is_dir()
    return False


def leg_coverage(meta: dict[str, Any], meta_path: Path, stage: str) -> dict[str, Any] | None:
    """The register's coverage test for a verifier meta, where it falls short.

    The register publishes a verifier leg whose metas account for fewer
    than :data:`scripts.lib_pass_cost.COVERAGE_FLOOR` of the candidates in
    its ``probabilities.json`` as ``audited-lower-bound`` (a later leg, such
    as a cleanup, overwrote the main meta; ``PassCoster.cost_pass``). The
    count is :func:`scripts.lib_pass_cost.verifier_coverage`'s, reused here,
    not re-derived. One case the register has never met: a carry-forward
    stage (:func:`carried_forward`), whose shortfall is results copied from
    a stage priced elsewhere, so its meta IS its whole spend.

    Args:
        meta: The parsed meta.
        meta_path: Its path.
        stage: ``verifier`` or ``proposer`` (a proposer is never tested).

    Returns:
        None when the meta covers its results (or there is nothing to test);
        else a record of the count with ``lower_bound`` True, or False with
        the carry that explains the shortfall.
    """
    if stage == "proposer":
        return None
    cover = verifier_coverage([(meta, meta_path)])
    if not cover or cover[0] >= COVERAGE_FLOOR * cover[1]:
        return None
    accounted, results = cover
    record: dict[str, Any] = {
        "accounted_candidates": accounted, "results": results, "floor": COVERAGE_FLOOR,
        "method": "scripts/lib_pass_cost.py verifier_coverage, as PassCoster.cost_pass applies it",
    }
    carry = carried_forward(meta_path.parent)
    # The exemption holds only when this meta accounts for every result the
    # carry did NOT bring (the file's own ``uncovered`` count), and the carry
    # came from a stage that exists. Testing ``accounted + carried`` against
    # the floor alone was vacuous whenever the carry was 90 % of the results
    # (re-audit, 2026-10-04: 756 of 759 passed with the meta covering none).
    if carry and accounted >= carry[2] and accounted + carry[0] >= results \
            and _stage_exists(meta_path, carry[1]):
        record.update(lower_bound=False, carried=carry[0], carried_from=carry[1], note=(
            f"the meta accounts for {accounted:,} candidate(s) against {results:,} results, "
            f"but {carry[0]:,} of those results were carried forward from {carry[1]} "
            "(carry_provenance.json) and their spend is priced there: this meta is the "
            "stage's whole spend, so the figure is not a lower bound"))
    else:
        record.update(lower_bound=True, note=(
            f"LOWER bound: the meta accounts for {accounted:,} candidate(s) against "
            f"{results:,} results in probabilities.json, below the register's "
            f"{COVERAGE_FLOOR:.0%} coverage floor: the leg's other calls are not recorded "
            "here (as the register reads it, a later leg such as a cleanup overwrote the "
            "main meta), so this is a floor on the leg's spend"))
    return record


def _relativise(value: Any, prefix: str) -> Any:
    """Strip an absolute repository prefix from every string in *value*."""
    if isinstance(value, str):
        return value.replace(prefix, "")
    if isinstance(value, list):
        return [_relativise(v, prefix) for v in value]
    if isinstance(value, dict):
        return {k: _relativise(v, prefix) for k, v in value.items()}
    return value


def outside_entry(meta: dict[str, Any], meta_path: Path, meta_rel: str,
                  runs: list[dict[str, Any]], coster: PassCoster,
                  repo_root: Path, merged_into: dict[str, Any] | None = None) -> dict[str, Any]:
    """Price a meta the register does not cite, the way the register prices a fragment.

    Args:
        meta: The parsed meta.
        meta_path: Its path (absolute or relative to the working directory).
        meta_rel: Its repository-relative path.
        runs: The run registry's entries.
        coster: The register's coster over the committed tier evidence.
        repo_root: The repository root.
        merged_into: :func:`chunk_links`' record when a register fragment
            already carries this meta's tokens, merged.

    Returns:
        The sidecar fields for a meta outside the register: reason, cost,
        basis, the fragment record, and the context it was resolved in;
        for a verifier meta short of the register's coverage floor, the
        coverage record (:func:`leg_coverage`) and, unless a carry explains
        the shortfall, ``audited-lower-bound`` at the lowest candidate.
    """
    run_id, run_dir, registered = run_context(meta_rel, runs)
    stage = meta_stage(meta_path)
    model, model_source = meta_model(meta)
    # The pool feeds only the attestation lookup (a glob over register pool
    # ids); the meta's directory within its run is the nearest analogue.
    parent = Path(meta_rel).parent
    pool = (parent.relative_to(run_dir).as_posix() if meta_rel.startswith(run_dir + "/")
            else parent.name)
    coverage = None
    if model is None:
        fragment: dict[str, Any] = {"meta": meta_rel, "model_recorded": None, "tier": None,
                                    "tier_method": "not-needed",
                                    "unpriceable": "the meta records no model"}
        basis, cost = "unpriceable", None
    else:
        priced = coster.cost_fragment(meta=meta, meta_path=meta_path.resolve(), run_id=run_id,
                                      pool=pool, run_dir=(repo_root / run_dir).resolve(),
                                      model=model, stage=stage)
        basis, cost = priced["_basis"], priced["_cost"]
        fragment = {k: v for k, v in priced.items() if not k.startswith("_")}
        if basis == "audited-upper-bound":
            fragment["bounds_usd"] = {"low": round(priced["_low"], 6),
                                      "high": round(priced["_high"], 6)}
        coverage = leg_coverage(meta, meta_path, stage)
        if coverage and coverage["lower_bound"] and basis in ("audited",
                                                              "audited-upper-bound"):
            # cost_pass's floor: the fragment at its LOWEST candidate tier,
            # valid whatever an unresolved tier was.
            basis, cost = "audited-lower-bound", priced["_low"]
    if merged_into:
        reason = (f"a chunk of a chunked Batch API pass: the register prices the merged meta "
                  f"{merged_into['meta']} ({', '.join(merged_into['pass_ids'])}), whose usage "
                  "is the sum of its chunks', so this meta's cost is ALREADY inside that row "
                  "and must not be added to it")
    elif registered:
        reason = (f"no row of the passes register cites this meta (its run {run_id} is in "
                  "results/run-registry.json, but the register's pass extraction does not "
                  "reach this file)")
    else:
        reason = (f"no row of the passes register cites this meta (its directory {run_dir} is "
                  "not a run in results/run-registry.json, so the register never extracted it)")
    entry = {
        "reason": reason,
        "cost_usd": None if cost is None else round(cost, 6),
        "cost_basis": basis,
        "fragment": fragment,
        "rate_card": coster.card_identity,
        "priced_by": ("scripts/lib_pass_cost.py PassCoster.cost_fragment: this meta's own "
                      "recorded usage through scripts/lib_cost.py price_usage at its end date, "
                      "at the tier the committed evidence resolves for it (the register's "
                      "per-fragment method; several candidate tiers publish the highest)"),
        "resolution_context": {"run_id": run_id, "run_dir": run_dir,
                               "run_registered": registered, "pool": pool, "stage": stage,
                               "model": model, "model_source": model_source},
    }
    if merged_into:
        entry["merged_into"] = merged_into
    if coverage:
        entry["coverage"] = coverage
    return _relativise(entry, str(repo_root.resolve()) + "/")


# ---------------------------------------------------------------------------
# The plan.
# ---------------------------------------------------------------------------


@dataclass
class Plan:
    """What the sidecars should be, and how the metas were sorted to get there."""

    sidecars: dict[Path, str] = field(default_factory=dict)
    stats: Counter = field(default_factory=Counter)
    tier_methods: Counter = field(default_factory=Counter)
    outside_bases: Counter = field(default_factory=Counter)
    outside_tiers: Counter = field(default_factory=Counter)
    outside_usd: float = 0.0
    #: Outside-register metas whose tokens a register row already carries.
    merged: list[str] = field(default_factory=list)
    merged_usd: float = 0.0
    multi_row: list[str] = field(default_factory=list)
    rebuilt_usage: list[str] = field(default_factory=list)
    cited_outside_glob: list[str] = field(default_factory=list)
    outside: list[str] = field(default_factory=list)
    stale: list[Path] = field(default_factory=list)


#: The trees whose metas get sidecars when no directory is named. ``results/``
#: holds six metas (the S104 vote-3 increments among them, outside the
#: register until D30's repair); ``archive/`` is superseded and is left alone.
META_ROOTS = ("outputs", "results")


def build_plan(repo_root: Path, *, outputs_dir: Path | None = None,
               register_path: Path | None = None, run_registry_path: Path | None = None,
               coster: PassCoster | None = None) -> Plan:
    """Decide every sidecar's text without writing anything.

    Args:
        repo_root: The repository root (all recorded paths are relative to it).
        outputs_dir: One tree of metas; by default every ``META_ROOTS`` tree
            under ``repo_root`` (``outputs/`` and ``results/``).
        register_path: The passes register; ``<repo_root>/results/passes-manifest.json``.
        run_registry_path: ``<repo_root>/results/run-registry.json`` by default
            (optional: absent, every meta outside the register is unregistered).
        coster: The pricing for metas outside the register; built from the
            committed evidence on first need when None.

    Returns:
        The plan: sidecar path to text, counts, and the stale sidecars found.

    Raises:
        BackfillError: On a sidecar name collision or an unreadable meta.
    """
    roots = [outputs_dir] if outputs_dir else [repo_root / r for r in META_ROOTS
                                                if (repo_root / r).is_dir()]
    # The default scope is the committed metas only; a named directory (the
    # tests' scratch trees) is read as it stands.
    tracked = None if outputs_dir else tracked_files(repo_root)
    register_path = register_path or repo_root / "results" / "passes-manifest.json"
    run_registry_path = run_registry_path or repo_root / "results" / "run-registry.json"
    register = read_json(register_path)
    stamp = register_stamp(register, rel_path(register_path, repo_root))
    index = index_register(register)
    runs = (read_json(run_registry_path).get("registry") or []
            if run_registry_path.exists() else [])
    header = {"schema": SCHEMA, "generator": GENERATOR, "generator_version": GENERATOR_VERSION,
              "register": stamp}
    plan = Plan()
    # Pass 1: read every meta and keep those with recorded usage.
    parsed: dict[str, tuple[Path, dict[str, Any], dict[str, int]]] = {}
    notes: dict[str, str | None] = {}
    seen_rel = set()
    for meta_path in (m for root in roots for m in enumerate_metas(root)
                      if tracked is None or m.resolve() in tracked):
        meta_rel = rel_path(meta_path, repo_root)
        seen_rel.add(meta_rel)
        plan.stats["metas"] += 1
        if meta_path.name == RUN_META:
            plan.stats["metas named run.meta.json"] += 1
        try:
            meta = read_json(meta_path)
        except (OSError, json.JSONDecodeError) as exc:
            raise BackfillError(f"cannot read {meta_rel}: {exc}") from exc
        if not isinstance(meta, dict):
            raise BackfillError(f"{meta_rel} is not a JSON object")
        status, usage, note = usage_status(meta)
        plan.stats[f"usage {status}"] += 1
        if status == "recorded":
            parsed[meta_rel] = (meta_path, meta, token_classes(usage))
            notes[meta_rel] = note
    # Pass 2: chunk metas whose tokens a register fragment carries, merged.
    links = chunk_links(parsed, index)
    # Pass 3: one sidecar per meta with recorded usage.
    for meta_rel, (meta_path, meta, _) in parsed.items():
        note = notes[meta_rel]
        if note:
            plan.rebuilt_usage.append(meta_rel)
        target = sidecar_path(meta_path)
        if target in plan.sidecars:
            raise BackfillError(f"sidecar name collision at {rel_path(target, repo_root)}")
        doc = {**header, "meta": meta_rel}
        if note:
            doc["usage_source"] = note
        hits = index.get(meta_rel) or []
        if hits:
            entries = sorted((register_entry(*h) for h in hits),
                             key=lambda e: str(e["pass_id"]))
            doc.update(in_register=True, rows=entries,
                       note=("copied from the passes register (PI ruling D28), which is the "
                             "source of truth: cost_usd and cost_basis are the ROW's (every "
                             "fragment of the pass), and the fragment record is copied as the "
                             "register holds it (on a lower-bound row the row sums each "
                             "fragment's lowest candidate, so the record's cost_usd need not "
                             "be this meta's part of the row's figure)"))
            plan.stats["sidecars in register"] += 1
            for e in entries:
                plan.stats[f"in register via {e['matched_by']}"] += 1
            if len(entries) > 1:
                plan.multi_row.append(meta_rel)
        else:
            if coster is None:
                coster = PassCoster()
            doc.update(in_register=False,
                       **outside_entry(meta, meta_path, meta_rel, runs, coster, repo_root,
                                       merged_into=links.get(meta_rel)))
            plan.stats["sidecars not in register"] += 1
            plan.outside.append(meta_rel)
            plan.tier_methods[str(doc["fragment"].get("tier_method"))] += 1
            plan.outside_bases[str(doc["cost_basis"])] += 1
            plan.outside_tiers[str(doc["fragment"].get("tier"))] += 1
            plan.outside_usd += doc["cost_usd"] or 0.0
            if meta_rel in links:
                plan.merged.append(meta_rel)
                plan.merged_usd += doc["cost_usd"] or 0.0
        plan.sidecars[target] = render(doc)
    prefixes = tuple(rel_path(root, repo_root) + "/" for root in roots)
    plan.cited_outside_glob = sorted(m for m in index if m.startswith(prefixes)
                                     and m not in seen_rel)
    wanted = set(plan.sidecars)
    plan.stale = sorted(p for root in roots for p in root.rglob("*cost_audit.json")
                        if p.is_file() and is_sidecar_name(p.name) and p not in wanted)
    return plan


# ---------------------------------------------------------------------------
# Writing and checking.
# ---------------------------------------------------------------------------


def _ours(path: Path) -> bool:
    """Whether an existing file is one of this writer's sidecars."""
    try:
        return read_json(path).get("schema") == SCHEMA
    except (OSError, json.JSONDecodeError, AttributeError):
        return False


def drift(plan: Plan) -> tuple[list[Path], list[Path]]:
    """Sidecars that are missing or differ from the plan.

    Returns:
        ``(missing, differing)``.
    """
    missing, differing = [], []
    for target, text in plan.sidecars.items():
        if not target.exists():
            missing.append(target)
        elif target.read_bytes() != text.encode("utf-8"):
            differing.append(target)
    return missing, differing


def write_plan(plan: Plan) -> int:
    """Write every sidecar that is missing or differs; never touch a meta.

    Returns:
        The number of files written.

    Raises:
        BackfillError: Before writing anything, if a target is a meta or an
            existing file that is not one of this writer's sidecars.
    """
    missing, differing = drift(plan)
    for target in missing + differing:
        if target.name.endswith(META_SUFFIX):
            raise BackfillError(f"refusing to write a meta: {target} (D14)")
    for target in differing:
        if not _ours(target):
            raise BackfillError(f"refusing to overwrite {target}: it is not a {SCHEMA} sidecar")
    for target in missing + differing:
        target.write_bytes(plan.sidecars[target].encode("utf-8"))  # no newline translation
    return len(missing) + len(differing)


def report(plan: Plan, repo_root: Path) -> list[str]:
    """Human-readable counts for the dry run and the log."""
    s = plan.stats
    lines = [
        f"metas: {s['metas']} ({s['metas named run.meta.json']} named run.meta.json)",
        f"usage recorded: {s['usage recorded']}; unrecorded: {s['usage unrecorded']}; "
        f"zero: {s['usage zero']} (no sidecar for the last two)",
        f"usage rebuilt from per-item records (recovery-merge inflation): "
        f"{len(plan.rebuilt_usage)}",
        f"sidecars planned: {len(plan.sidecars)}",
        f"  in register: {s['sidecars in register']} (rows matched via {BY_FRAGMENT}: "
        f"{s['in register via ' + BY_FRAGMENT]}, via {BY_SOURCE} only: "
        f"{s['in register via ' + BY_SOURCE]}); metas in more than one row: "
        f"{len(plan.multi_row)}",
        f"  not in register: {s['sidecars not in register']}, US${plan.outside_usd:,.6f} "
        "in all",
        f"    of which chunks a register row already carries, merged (do not add): "
        f"{len(plan.merged)}, US${plan.merged_usd:,.6f}",
    ]
    for label, counter in (("basis", plan.outside_bases), ("tier", plan.outside_tiers),
                           ("tier_method", plan.tier_methods)):
        for key, n in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"    {label} {key}: {n}")
    if plan.cited_outside_glob:
        lines.append(f"register-cited metas not named *{META_SUFFIX} (no sidecar): "
                     f"{len(plan.cited_outside_glob)}")
        lines.extend(f"    {m}" for m in plan.cited_outside_glob)
    if plan.stale:
        lines.append(f"stale sidecars (not deleted; archive by hand): {len(plan.stale)}")
        lines.extend(f"    {rel_path(p, repo_root)}" for p in plan.stale)
    return lines


def main(argv: list[str] | None = None, coster: PassCoster | None = None) -> int:
    """Report, and with ``--write`` apply, the sidecars; ``--check`` exits 1 on drift.

    Args:
        argv: Command-line arguments (``sys.argv[1:]`` when None).
        coster: An alternative coster (tests pass one over fixture evidence).

    Returns:
        The exit status: 0, 1 on drift under ``--check``, 2 when refused.
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip())
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the sidecars")
    mode.add_argument("--check", action="store_true",
                      help="exit 1 if any sidecar is missing, differs or is stale")
    parser.add_argument("--repo-root", type=Path, default=PROJECT_ROOT,
                        help="repository root (tests point it at a fixture tree)")
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    try:
        plan = build_plan(root, coster=coster)
    except BackfillError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print("\n".join(report(plan, root)))
    missing, differing = drift(plan)
    if args.check:
        for label, paths in (("missing", missing), ("differs", differing),
                             ("stale", plan.stale)):
            for p in paths:
                print(f"{label}: {rel_path(p, root)}")
        bad = bool(missing or differing or plan.stale)
        print(f"drift: {len(missing)} missing, {len(differing)} differing, "
              f"{len(plan.stale)} stale" if bad else "sidecars current")
        return 1 if bad else 0
    if args.write:
        try:
            n = write_plan(plan)
        except BackfillError as exc:
            print(f"refused: {exc}", file=sys.stderr)
            return 2
        print(f"wrote {n} sidecar(s); {len(plan.sidecars) - n} already current")
    else:
        print(f"(dry run: {len(missing)} to create, {len(differing)} to update; "
              "--write applies it)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
