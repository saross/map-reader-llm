#!/usr/bin/env python3
"""
Audited flex cost of a VERIFIER leg, summed across its main and cleanup passes.

Why this script exists
----------------------
``scripts/audit_proposer_cost.py`` audits a proposer leg, whose passes live in
``run_*`` fragment directories. A verifier leg has no such fragments: one stage
directory holds one ``probabilities.json`` and one ``run.meta.json``, so the
proposer auditor cannot be pointed at it. The image campaign's steward met this
on 2026-09-13 and imported ``rates()`` and ``audited_cost()`` by hand
(``outputs/gemini37-image-55map-2026-09-13/post_run_report.md`` section 3.1).
This script is that method promoted to a tool, and it closes the trap the
steward named:

    ``run_pv.py cleanup`` (before 2026-09-14) rewrote ``run.meta.json`` with
    the RETRY pass's usage only. Reading that file alone understates the arm.
    The campaign's K = 1 arm 2 reads **US$0.0153** where the audited truth is
    **US$7.7028** — US$7.6875 for the main pass plus US$0.0153 for the
    cleanup, both of which have to be read.

So this auditor never trusts one file. It sums every pass of a stage, taking
them from whichever of the three conventions is present:

1. **The fixed format** (``run_pv.py`` from 2026-09-14): ``run.meta.json``
   carries the summed totals, with ``main_pass`` holding the original pass
   verbatim and ``cleanup_passes`` one entry per retry. The stage total is
   the sum over those per-pass blocks, each priced at ITS OWN rate card —
   pricing the merged totals instead would apply the main pass's card to a
   cleanup that ran under a different model, which ``--allow-config-change``
   permits. The merged block is priced as a cross-check, and the sidecars
   beside the meta are earlier *merged* states, never added in.
2. **The legacy backup convention**: the cleanup's meta is
   ``run.meta.json``, and the main pass survives only in an operator-made
   copy — ``run.meta.json.pre-cleanup-<timestamp>.backup`` (the campaign's
   arm 2) or ``run.meta.main-<date>.json`` (the S144 verifier swap). These
   files hold disjoint passes, so they are summed.
3. **The recovery register** (``outputs/verifier-meta-recovery-2026-09-14.json``,
   written by ``scripts/recover_verifier_meta_from_git.py``): the repository
   commits ``outputs/**``, so a stage committed *before* the overwrite still
   carries its pre-overwrite ``run.meta.json`` as a git blob. The register
   records those blobs' ``usage_stats`` verbatim, and this auditor counts them
   as passes of the stage — named in the report as
   ``register:git-blob:<blob>`` so every dollar traces to a blob hash. The
   register's ``residual_estimate`` blocks are estimates and are **never**
   counted; they are surfaced as a note.

4. **None of the three**, which is the fourth cell: one meta covering 29 of
   57,482 candidates, nothing else on disc, and nothing in history. The audit
   then reports what the surviving meta covers AND the shortfall, and refuses
   to present the figure as the stage's cost.

The cost basis
--------------
The rule is ``reports/token-load-audit-2026-06-12.md`` section 2 — fresh input
at the input rate, cached input at the cache rate, output **plus thinking** at
the output rate — applied at the service tier actually used. ``run_pv.py
verify`` defaults to ``--service-tier flex``, which bills at half of list,
while the meta's own ``cost_estimate`` prices at list: on the Gold Standard
(GS) calibration arms the meta prints exactly **2x** the audited figure. That
factor of two is the *flex correction*, and it is why the meta's
``cost_estimate`` must never be used at a budget gate.

Verification (the gate in ``tests/test_audit_verifier_cost.py``)
----------------------------------------------------------------
Run over the GS calibration leg's two committed arms this script reproduces
the costs recorded in ``planning/gemini37-image-55map-2026-09-13.md`` line 112
and ``reports/gemini37-image-55map-deltas-2026-09-13.md`` line 43 exactly:

    arm 1 (``gemini-3-flash-preview``, MINIMAL)  US$0.4417 over 622 candidates
    arm 2 (``gemini-3.7-flash``, low)            US$0.6804 over 622 candidates

Usage
-----
::

    # One stage, or several
    python scripts/audit_verifier_cost.py \\
        outputs/gemini37-image-gs-2026-09-01/verifier/g384_ov192_g37img/verify_k3_arm1

    # The retrospective sweep: every verifier stage whose meta shows the
    # cleanup-overwrite signature, classified recoverable or not
    python scripts/audit_verifier_cost.py --sweep outputs

    # Explicit file pairs: price metadata files that are not (or no longer) a
    # stage on disc — a main-pass backup beside its cleanup, or blobs
    # extracted from git history with `git cat-file blob`
    python scripts/audit_verifier_cost.py \\
        --pass-file /tmp/main-pass.json --pass-file /tmp/cleanup.json

Options
-------
``--tier``            ``flex`` (default, half of list) or ``standard``.
``--model``           Rate card for a pass that records no model of its
                      own. A pass that records one is always priced at
                      it; a disagreement warns. Omitted, a pass with no
                      model is refused rather than guessed at.
``--json``            Emit JSON instead of a table.
``--sweep <root>``    Retrospective mode over a tree of verifier stages.
``--min-shortfall N`` Sweep only: smallest meta-vs-results gap to report
                      (default 1).
``--pass-file F``     Repeatable: price these metadata files as one stage.
``--recovery-register P`` Register to read recovered passes from (default:
                      ``outputs/verifier-meta-recovery-2026-09-14.json``).
``--no-recovery-register`` Ignore the register, to see a stage as the working
                      tree alone reports it.

Author: Claude Code, for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.audit_proposer_cost import (  # noqa: E402
    RATE_CARDS,
    TIER_DISCOUNT,
    RateCardError,
    audited_cost,
    rates,
)

__version__ = "1.0.0"

#: Glob patterns for a prior pass's meta under the LEGACY conventions, where
#: the surviving ``run.meta.json`` describes the cleanup and the main pass
#: lives in an operator-made copy. A match normally holds a pass DISJOINT from
#: the primary meta's and is summed into the stage total — but the conventions
#: give one pass more than one name, and a stage can hold two of them for the
#: same pass, so ``audit_stage`` de-duplicates by pass identity before summing.
#:
#: ORDER IS THE PREFERENCE: when two names hold one pass, the FIRST pattern's
#: file is the one reported and priced. ``run.meta.main-<date>.json`` leads
#: because it is the durable, committed name; the ``*.backup`` spellings are
#: operator artefacts that may exist on one machine only.
LEGACY_PRIOR_META_GLOBS: tuple[str, ...] = (
    "run.meta.main-*.json",
    "run.meta.json.pre-cleanup-*.backup",
    "run.meta.json.pre-*.backup",
)

#: Default recovery register: passes recovered from git history by
#: ``scripts/recover_verifier_meta_from_git.py``. Read as the THIRD source of
#: passes, after the fixed schema and the legacy backup convention, for stages
#: whose main pass survives only as a git blob.
RECOVERY_REGISTER_DEFAULT: Path = (
    BASE_DIR / "outputs" / "verifier-meta-recovery-2026-09-14.json"
)

#: Schema tag the register must carry for this auditor to read it. A register
#: written under a later contract is ignored with a warning rather than
#: mis-read: a wrong pass block is a wrong dollar figure.
RECOVERY_REGISTER_SCHEMA = "verifier-meta-recovery/1"

#: Glob for the sidecars the fixed writer leaves. Each is an earlier MERGED
#: state of the same stage, so it must never be added to the primary total —
#: it is reported as evidence that a merge happened.
FIXED_SIDECAR_GLOB: str = "run.meta.pre-*.json"

#: Fields naming a stage's candidate population, in order of preference.
_RESULT_COUNT_KEYS: tuple[str, ...] = ("results", "consensus")

#: Model-provenance notes already emitted, so a sweep over hundreds of
#: stages says each thing once rather than once per block.
_WARNED: set[str] = set()


def _warn_once(message: str) -> None:
    """Print a provenance note to stderr, at most once per distinct text.

    Model provenance is worth saying and not worth repeating: a ``--sweep``
    reads hundreds of blocks, and an override or a disagreement that
    printed per block would bury the table it annotates.

    Args:
        message: The full line to print, including its ``note:`` or
            ``warning:`` prefix.
    """
    if message in _WARNED:
        return
    _WARNED.add(message)
    print(message, file=sys.stderr)


@dataclass
class PassAudit:
    """One pass of a verifier stage, priced on the audited basis.

    Attributes:
        source: Where the pass was read from — a file name, or
            ``"run.meta.json:main_pass"`` / ``":cleanup_passes[N]"`` for a
            block inside the fixed-format meta.
        kind: ``main``, ``cleanup``, ``legacy-prior`` or ``merged-total``.
        model: The model whose rate card was used.
        items: Items the pass processed.
        cached_share: Cached fraction of the pass's input tokens.
        audited_usd: Cost on the audited basis at the requested tier.
        meta_cost_usd: What the pass's own ``cost_estimate`` claimed, or
            None when the block records none.
        counted: Whether this row contributes to the stage total. A merged
            meta's top-level block is priced as a cross-check and is NOT
            counted, because the per-pass blocks it summarises are.
        identity: The pass's own identity, from ``_pass_identity``. Two rows
            describing ONE pass share it, whichever file or register entry
            each was read from; ``audit_stage`` uses it to refuse to count a
            pass twice.
    """

    source: str
    kind: str
    model: str
    items: int
    cached_share: float
    audited_usd: float
    meta_cost_usd: float | None
    counted: bool = True
    identity: str = ""


@dataclass
class StageAudit:
    """The audited cost of one verifier stage and how complete it is.

    Attributes:
        stage: The stage directory.
        format: ``fixed`` (a merged meta), ``legacy-summed`` (primary plus
            an operator backup) or ``single-meta`` (one file only).
        results: Result keys in ``probabilities.json``, or None when absent.
        passes: One :class:`PassAudit` per pass, plus any cross-check row
            (``counted`` False), which is excluded from the total.
        audited_usd: The stage total on the audited basis.
        items_covered: Items the counted passes account for.
        shortfall: ``results - items_covered``, floored at 0 — candidates
            whose token load no file on disc records.
        meta_only_usd: What an audit reading ``run.meta.json``'s
            ``cost_estimate`` alone would have reported.
        complete: True when the counted passes cover every result.
        notes: Human-readable warnings.
    """

    stage: str
    format: str
    results: int | None
    passes: list[PassAudit]
    audited_usd: float
    items_covered: int
    shortfall: int
    meta_only_usd: float | None
    complete: bool
    notes: list[str] = field(default_factory=list)

    @property
    def audited_usd_per_candidate(self) -> float | None:
        """Audited cost per item covered, or None when nothing is covered."""
        if not self.items_covered:
            return None
        return self.audited_usd / self.items_covered


def _load_json(path: Path) -> dict[str, Any]:
    """Read a JSON object from *path*.

    Args:
        path: File to read.

    Returns:
        The parsed object, or an empty dict when the file cannot be parsed.
    """
    try:
        with open(path) as handle:
            loaded = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _pass_identity(meta: dict[str, Any] | None) -> str:
    """Return a stable identity for one pass, for de-duplication.

    A stage can hold the same pass under two names — the operator's
    ``run.meta.json.pre-cleanup-<timestamp>.backup`` beside the same bytes
    saved as ``run.meta.main-<date>.json``, for instance — and summing both
    would double the stage's audited cost. ``run_id`` is the pass's own
    identifier and is preferred; a legacy meta that records none falls back
    to a hash of its usage and execution stats, which is what the pricing
    reads anyway.

    Args:
        meta: A pass meta, or None.

    Returns:
        An identity string. Two metas describing one pass share it.

    Examples:
        >>> _pass_identity({"run_id": "abc"})
        'run_id:abc'
        >>> a = {"usage_stats": {"input_tokens": 10}}
        >>> _pass_identity(a) == _pass_identity(dict(a))
        True
    """
    if not meta:
        return "empty"
    run_id = meta.get("run_id")
    if run_id:
        return f"run_id:{run_id}"
    payload = json.dumps(
        {
            "usage_stats": meta.get("usage_stats"),
            "execution_stats": meta.get("execution_stats"),
            "configuration": meta.get("configuration"),
        },
        sort_keys=True,
        default=str,
    )
    return "digest:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_recovery_register(path: Path | None) -> dict[str, Any]:
    """Load the git-history recovery register, or return an empty mapping.

    Args:
        path: Register file, or None to skip the register entirely.

    Returns:
        The register's ``stages`` mapping, keyed by stage path as the register
        records it. Empty when the file is absent, unparseable, or written
        under a schema this auditor does not know.
    """
    if path is None or not path.exists():
        return {}
    register = _load_json(path)
    schema = register.get("schema")
    if schema != RECOVERY_REGISTER_SCHEMA:
        print(
            f"warning: ignoring {path}: schema {schema!r} is not "
            f"{RECOVERY_REGISTER_SCHEMA!r}",
            file=sys.stderr,
        )
        return {}
    stages = register.get("stages")
    return stages if isinstance(stages, dict) else {}


def _register_entry(
    register: dict[str, Any], stage: Path,
) -> dict[str, Any] | None:
    """Find *stage* in the register, tolerating path spelling differences.

    The register records repository-relative paths; a caller may name a stage
    absolutely, with a trailing slash, or relative to the working directory.

    Args:
        register: The register's ``stages`` mapping.
        stage: The stage directory as the caller named it.

    Returns:
        The register entry, or None when the stage is not registered.
    """
    candidates = [str(stage), str(stage).rstrip("/")]
    try:
        candidates.append(str(stage.resolve().relative_to(BASE_DIR)))
    except ValueError:
        pass
    for candidate in candidates:
        entry = register.get(candidate)
        if isinstance(entry, dict):
            return entry
    return None


def count_results(stage: Path) -> int | None:
    """Count the result keys a stage's ``probabilities.json`` holds.

    Args:
        stage: A verifier stage directory.

    Returns:
        The number of result keys, or None when the file is absent. For a
        consensus run the count is per candidate-iteration, which is the
        unit ``execution_stats.items_processed`` also counts.
    """
    probs_path = stage / "probabilities.json"
    if not probs_path.exists():
        return None
    probs = _load_json(probs_path)
    for key in _RESULT_COUNT_KEYS:
        block = probs.get(key)
        if isinstance(block, dict):
            return len(block)
    return None


def _price_block(
    block: dict[str, Any],
    *,
    source: str,
    kind: str,
    tier: str,
    default_model: str | None,
    counted: bool = True,
    identity: str | None = None,
) -> PassAudit:
    """Price one pass block on the audited basis.

    Args:
        block: A dict carrying ``usage_stats``, ``execution_stats`` and
            optionally ``configuration`` and ``cost_estimate``.
        source: Provenance string for the report.
        kind: Pass kind for the report.
        tier: Service tier to price at.
        default_model: Rate card for a block that records no model of
            its own. None (the default) REFUSES such a block rather
            than guessing. A block that records a model is always
            priced at it, and a disagreement with *default_model* is
            warned about (audit 2026-09-20).
        counted: Whether the row contributes to the stage total.
        identity: Override for the pass's identity. Blocks ENUMERATED inside
            one merged meta are known-distinct by construction — the writer
            listed them — so they pass their own source here rather than be
            compared by content, which two passes can legitimately share.
            Passes DISCOVERED by globbing files or reading the register have
            no such guarantee and take the content-derived default.

    Returns:
        The priced pass.

    Raises:
        RateCardError: When the model has no recorded rate card. Guessing
            one is how the meta's own figure went wrong; fail instead.
    """
    usage = block.get("usage_stats", {}) or {}
    execution = block.get("execution_stats", {}) or {}
    configuration = block.get("configuration", {}) or {}
    recorded = configuration.get("model") or None
    model = recorded or default_model
    if model is None:
        raise RateCardError(
            f"{source} records no configuration.model and no --model was "
            f"given; guessing a rate card is the error this auditor exists "
            f"to correct. Pass --model explicitly if you know what this "
            f"pass ran on.",
        )
    if recorded is None:
        _warn_once(
            f"note: --model {default_model} used as the rate card for "
            f"{source}, which records no model of its own",
        )
    elif default_model is not None and default_model != recorded:
        _warn_once(
            f"warning: --model {default_model} disagrees with the model "
            f"{recorded!r} recorded by {source}; it is priced at "
            f"{recorded!r}, which is what it ran on. Drop --model unless "
            f"you mean to override a pass that records nothing.",
        )
    rate = rates(model, tier)
    # A meta and a ``main_pass`` block carry ``execution_stats``; a
    # ``cleanup_passes`` entry carries its counts flat instead.
    items = execution.get("items_processed")
    if items is None:
        items = block.get("candidates_verified")
    total_input = usage.get("total_input_tokens", 0) or 0
    cached = usage.get("total_cached_tokens", 0) or 0
    return PassAudit(
        source=source,
        kind=kind,
        model=model,
        items=items or 0,
        cached_share=cached / total_input if total_input else 0.0,
        audited_usd=audited_cost(
            {
                "total_input_tokens": total_input,
                "total_cached_tokens": cached,
                "total_output_tokens": usage.get("total_output_tokens", 0) or 0,
                "total_thoughts_tokens": (
                    usage.get("total_thoughts_tokens", 0) or 0
                ),
            },
            rate,
        ),
        meta_cost_usd=(block.get("cost_estimate") or {}).get("total_cost_usd"),
        counted=counted,
        identity=identity if identity is not None else _pass_identity(block),
    )


def audit_stage(
    stage: Path,
    *,
    tier: str = "flex",
    default_model: str | None = None,
    register: dict[str, Any] | None = None,
) -> StageAudit:
    """Audit one verifier stage, summing every pass recorded on disc.

    Args:
        stage: The stage directory, holding ``run.meta.json``.
        tier: Service tier actually used (``run_pv.py verify`` defaults to
            ``flex``, which bills at half of list).
        default_model: Rate card for a pass that records no model of its
            own; None refuses such a pass rather than guessing.
        register: The recovery register's ``stages`` mapping (see
            :func:`load_recovery_register`). Passes it records for this stage
            are counted as a third source, after the fixed schema and the
            legacy backup convention. None or empty ignores the register.

    Returns:
        The stage's audit.

    Raises:
        FileNotFoundError: When the stage holds no ``run.meta.json``.
    """
    meta_path = stage / "run.meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"no run.meta.json in {stage}")

    meta = _load_json(meta_path)
    results = count_results(stage)
    notes: list[str] = []
    passes: list[PassAudit] = []

    cleanup_passes = meta.get("cleanup_passes")
    main_pass = meta.get("main_pass")
    is_fixed = isinstance(cleanup_passes, list) and isinstance(main_pass, dict)

    if is_fixed:
        # Each pass is priced at ITS OWN rate card and the stage total is
        # their sum. Pricing the merged top-level block instead would apply
        # the main pass's card to every pass — wrong whenever a cleanup ran
        # under a different model, which --allow-config-change permits. The
        # merged block is still priced, as a cross-check row that does not
        # contribute to the total.
        stage_format = "fixed"
        counted = [
            _price_block(
                main_pass,
                source="run.meta.json:main_pass",
                identity="block:run.meta.json:main_pass",
                kind="main",
                tier=tier,
                default_model=default_model,
            ),
        ]
        for index, entry in enumerate(cleanup_passes):
            counted.append(
                _price_block(
                    entry,
                    source=f"run.meta.json:cleanup_passes[{index}]",
                    identity=f"block:run.meta.json:cleanup_passes[{index}]",
                    kind=entry.get("kind", "cleanup"),
                    tier=tier,
                    default_model=default_model,
                ),
            )
        passes.extend(counted)
        passes.append(
            _price_block(
                meta,
                source="run.meta.json (merged totals)",
                identity="block:run.meta.json (merged totals)",
                kind="merged-total",
                tier=tier,
                default_model=default_model,
                counted=False,
            ),
        )
        audited_total = sum(p.audited_usd for p in counted)
        items_covered = sum(p.items for p in counted)
        _check_token_sum(meta, counted_blocks=[main_pass, *cleanup_passes],
                         notes=notes)
        for pass_entry in cleanup_passes:
            if pass_entry.get("configuration_differs_from_main_pass"):
                notes.append(
                    "a cleanup pass ran under a configuration differing "
                    "from the main pass's on: "
                    + ", ".join(
                        pass_entry.get("changed_configuration_fields", []),
                    ),
                )
    else:
        primary = _price_block(
            meta,
            source="run.meta.json",
            kind="cleanup" if _looks_like_cleanup(meta, results) else "main",
            tier=tier,
            default_model=default_model,
        )
        passes.append(primary)
        # The legacy conventions name the SAME surviving pass in more than one
        # way, so two globs can match two files holding one pass: a stage that
        # carries both `run.meta.json.pre-cleanup-*.backup` and
        # `run.meta.main-*.json` has been seen holding byte-identical copies.
        # Summing both double-counts the pass and doubles the stage's dollar
        # figure, so identity is taken from the pass itself — its `run_id`,
        # or its content when a legacy meta records none — exactly as the
        # recovery register's guard below does.
        counted_identities: set[str] = {_pass_identity(meta)}
        for pattern in LEGACY_PRIOR_META_GLOBS:
            for path in sorted(stage.glob(pattern)):
                if any(p.source == path.name for p in passes):
                    continue
                prior = _load_json(path)
                identity = _pass_identity(prior)
                if identity in counted_identities:
                    notes.append(
                        f"{path.name} skipped: it holds a pass already "
                        "counted from another file in this stage "
                        f"({'run_id ' + prior['run_id'] if prior.get('run_id') else 'identical content'})",
                    )
                    continue
                counted_identities.add(identity)
                passes.append(
                    _price_block(
                        prior,
                        source=path.name,
                        kind="legacy-prior",
                        tier=tier,
                        default_model=default_model,
                    ),
                )
        stage_format = (
            "legacy-summed" if len(passes) > 1 else "single-meta"
        )
        # THIRD SOURCE: passes recovered from git history. Only for a stage
        # with no merged meta — a merged meta already carries every pass — and
        # only for passes whose run_id is not already counted, so a register
        # that overlaps a file on disc cannot double-count the same pass.
        entry = _register_entry(register or {}, stage)
        if entry is not None:
            added = 0
            for recovered in entry.get("recovered_passes") or []:
                identity = _pass_identity(recovered)
                if identity in counted_identities:
                    notes.append(
                        "register pass "
                        f"{recovered.get('source', '?')} skipped: it holds a "
                        "pass already counted from a file on disc "
                        f"({identity.split(':', 1)[0].replace('digest', 'identical content')})",
                    )
                    continue
                counted_identities.add(identity)
                passes.append(
                    _price_block(
                        recovered,
                        source=f"register:{recovered.get('source', '?')}",
                        kind="recovered-from-git",
                        tier=tier,
                        default_model=default_model,
                    ),
                )
                added += 1
            if added:
                stage_format = "register-recovered"
                notes.append(
                    f"{added} pass(es) recovered from git history by the "
                    f"recovery register ({entry.get('verdict')}): "
                    + "; ".join(
                        f"{recovered.get('source', '?')} at "
                        f"{recovered.get('commit', '?')[:9]} "
                        f"({(recovered.get('commit_date') or '?')[:10]})"
                        for recovered in entry.get("recovered_passes") or []
                    ),
                )
            estimate = entry.get("residual_estimate")
            if estimate is not None:
                notes.append(
                    "the register carries a residual ESTIMATE for this stage "
                    f"({estimate.get('missing_candidates')} candidates, "
                    f"{estimate.get('usage_stats', {}).get('total_input_tokens', 0):,} "
                    "input tokens) — an estimate, never counted into the "
                    "audited total; see the register for its basis",
                )
        audited_total = sum(p.audited_usd for p in passes if p.counted)
        items_covered = sum(p.items for p in passes if p.counted)

    # ONE INVARIANT over every source. Each branch guards its own additions,
    # but the stage total is only trustworthy if no pass is counted twice by
    # ANY route, so the assembled result is checked once here. A duplicate at
    # this point is a defect in a guard above, not a data condition, so it is
    # reported loudly rather than silently corrected — a wrong dollar figure
    # that looks right is the failure this auditor exists to prevent.
    seen: dict[str, str] = {}
    for pass_audit in passes:
        if not pass_audit.counted:
            continue
        identity = pass_audit.identity
        if identity in seen:
            notes.append(
                "DOUBLE-COUNT: "
                f"{pass_audit.source} holds the same pass as {seen[identity]} "
                "and both are counted into this stage's total — the figure "
                "below is overstated; this is a guard defect, please report it",
            )
        else:
            seen[identity] = pass_audit.source

    orphan_sidecars = sorted(
        path.name for path in stage.glob(FIXED_SIDECAR_GLOB)
    )
    if orphan_sidecars and not is_fixed:
        notes.append(
            "merge sidecars present without a merged primary meta: "
            + ", ".join(orphan_sidecars),
        )

    shortfall = max(0, (results or 0) - items_covered) if results else 0
    if shortfall:
        notes.append(
            f"{shortfall} of {results} results are not accounted for by any "
            "pass on disc — the cleanup-overwrite signature; the figure "
            "below is a LOWER BOUND, not the stage's cost",
        )

    meta_only = (meta.get("cost_estimate") or {}).get("total_cost_usd")
    return StageAudit(
        stage=str(stage),
        format=stage_format,
        results=results,
        passes=passes,
        audited_usd=audited_total,
        items_covered=items_covered,
        shortfall=shortfall,
        meta_only_usd=meta_only,
        complete=not shortfall,
        notes=notes,
    )


def audit_files(
    paths: list[Path],
    *,
    tier: str = "flex",
    default_model: str | None = None,
) -> StageAudit:
    """Audit explicit metadata files as one stage, summing them.

    For passes that are not (or are no longer) a stage on disc: a main-pass
    backup beside its cleanup, or blobs pulled out of git history with
    ``git cat-file blob <hash> > /tmp/main-pass.json``. The caller asserts that
    the files hold DISJOINT passes of one stage — nothing here can check that,
    so the audit reports each file's coverage for the caller to verify.

    Args:
        paths: Metadata files to price, in any order.
        tier: Service tier actually used.
        default_model: Rate card for a file recording no model of its
            own; None refuses such a file rather than guessing.

    Returns:
        A :class:`StageAudit` over the files, with ``results`` None (there is
        no ``probabilities.json`` to count) and therefore no shortfall.

    Raises:
        FileNotFoundError: When a named file does not exist.
    """
    passes: list[PassAudit] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"no such metadata file: {path}")
        meta = _load_json(path)
        passes.append(
            _price_block(
                meta,
                source=path.name,
                kind="explicit-file",
                tier=tier,
                default_model=default_model,
            ),
        )
    return StageAudit(
        stage=" + ".join(str(path) for path in paths),
        format="explicit-files",
        results=None,
        passes=passes,
        audited_usd=sum(entry.audited_usd for entry in passes),
        items_covered=sum(entry.items for entry in passes),
        shortfall=0,
        meta_only_usd=None,
        complete=True,
        notes=[
            "explicit file mode: the caller asserts these files hold disjoint "
            "passes of one stage; check the per-file item counts above",
        ],
    )


def _check_token_sum(
    meta: dict[str, Any],
    *,
    counted_blocks: list[dict[str, Any]],
    notes: list[str],
) -> None:
    """Warn when a merged meta's totals disagree with its per-pass blocks.

    Token counts are model-independent, so this is the one comparison that
    can police a merged meta without assuming a rate card. A disagreement
    means the meta was hand-edited, or a pass was written into the totals
    without its own ``cleanup_passes`` entry — either way the per-pass sum
    the audit reports would be short.

    Args:
        meta: The merged meta.
        counted_blocks: The ``main_pass`` and ``cleanup_passes`` blocks.
        notes: List to append a warning to, in place.
    """
    merged_usage = meta.get("usage_stats", {}) or {}
    for field_name in (
        "total_input_tokens",
        "total_output_tokens",
        "total_thoughts_tokens",
    ):
        merged_value = merged_usage.get(field_name, 0) or 0
        block_sum = sum(
            (block.get("usage_stats", {}) or {}).get(field_name, 0) or 0
            for block in counted_blocks
        )
        if merged_value != block_sum:
            notes.append(
                f"{field_name}: the merged total is {merged_value:,} but the "
                f"per-pass blocks sum to {block_sum:,} — the meta was edited, "
                "or a pass reached the totals without its own entry, so the "
                "audited figure is short",
            )


def _looks_like_cleanup(meta: dict[str, Any], results: int | None) -> bool:
    """Whether a legacy meta looks like a cleanup pass rather than a main one.

    Args:
        meta: The meta's contents.
        results: The stage's result count, or None.

    Returns:
        True when the meta's ``items_processed`` covers fewer than all the
        stage's results — the signature of a pass that replaced a larger
        one.
    """
    if not results:
        return False
    processed = (meta.get("execution_stats") or {}).get("items_processed") or 0
    return 0 < processed < results


@dataclass
class StageSignature:
    """One stage's position in the retrospective sweep.

    Attributes:
        stage: The stage directory.
        results: Result keys in ``probabilities.json``.
        items_processed: What the surviving ``run.meta.json`` covers.
        shortfall: ``results - items_processed``.
        mode: The results file's execution mode.
        cleanup_history: Cleanup rounds recorded in ``probabilities.json``.
        main_pass_covered: Candidates the main pass covered according to
            ``cleanup_history`` (``results`` minus the first round's
            ``initial_missing``), or None when no history is recorded.
        prior_meta_files: Prior-pass metas found in the stage directory.
        sibling_candidates: Sibling stages whose meta matches this stage's
            model and instruction hash and covers the whole result set —
            evidence for manual adjudication, not automatic recovery.
        classification: ``RECOVERABLE`` (a prior meta on disc),
            ``RECOVERED-FROM-GIT`` (the recovery register holds the main
            pass), ``UNRECOVERABLE`` or ``MERGED``.
        audited_usd: The audited figure for what IS on disc, or None when
            the stage could not be priced.
        audit_error: Why the stage could not be priced, when it could not.
            A stage is never dropped from the sweep for want of a rate
            card — that would hide exactly what the sweep is looking for.
    """

    stage: str
    results: int
    items_processed: int
    shortfall: int
    mode: str | None
    cleanup_history: int
    main_pass_covered: int | None
    prior_meta_files: list[str]
    sibling_candidates: list[str]
    classification: str
    audited_usd: float | None
    audit_error: str | None = None


def _sibling_candidates(stage: Path, shortfall: int) -> list[str]:
    """Find sibling stages that could hold this stage's main pass.

    An operator who copied a finished stage and cleaned up the copy leaves
    the main pass's meta in the original directory. A sibling qualifies when
    its meta covers at least this stage's shortfall and records the same
    model and system-instruction hash — a *candidate*, not a finding: only
    comparing the two stages' result keys settles whether the sibling is
    this stage's earlier self or an unrelated re-run.

    Args:
        stage: The stage with the shortfall.
        shortfall: Candidates this stage's meta does not account for.

    Returns:
        Sibling directory names, sorted. Evidence only — the caller
        adjudicates.
    """
    meta = _load_json(stage / "run.meta.json")
    configuration = meta.get("configuration") or {}
    model = configuration.get("model")
    instruction_hash = configuration.get("system_instruction_hash")
    found: list[str] = []
    parent = stage.parent
    if not parent.is_dir():
        return found
    for sibling in sorted(parent.iterdir()):
        if sibling == stage or not sibling.is_dir():
            continue
        sibling_meta = _load_json(sibling / "run.meta.json")
        if not sibling_meta:
            continue
        sibling_config = sibling_meta.get("configuration") or {}
        processed = (
            (sibling_meta.get("execution_stats") or {}).get("items_processed")
            or 0
        )
        if (
            processed >= shortfall
            and sibling_config.get("model") == model
            and sibling_config.get("system_instruction_hash")
            == instruction_hash
        ):
            found.append(sibling.name)
    return found


def sweep(
    root: Path,
    *,
    tier: str = "flex",
    default_model: str | None = None,
    min_shortfall: int = 1,
    register: dict[str, Any] | None = None,
) -> list[StageSignature]:
    """Enumerate verifier stages whose meta understates their candidate load.

    A stage qualifies when its ``run.meta.json`` records a positive
    ``items_processed`` below the number of results its
    ``probabilities.json`` holds. A realtime stage at ``items_processed == 0``
    has nothing to compare; a BATCH stage at zero is a booking failure and is
    reported (the Batch Application Programming Interface (API) reports usage
    per response and the path has read it since 2026-09-17), so it no longer
    counts as a stage that legitimately records zero and its tokens were
    never in the meta to lose.

    Args:
        root: Tree to walk (normally ``outputs``).
        tier: Service tier to price at.
        default_model: Rate card for a pass recording no model of its
            own; None refuses such a pass rather than guessing.
        min_shortfall: Smallest gap worth reporting.
        register: The recovery register's ``stages`` mapping; a stage whose
            main pass it holds is classified ``RECOVERED-FROM-GIT`` and its
            audited figure includes the recovered pass.

    Returns:
        One :class:`StageSignature` per qualifying stage, worst first.
    """
    signatures: list[StageSignature] = []
    for probs_path in sorted(root.rglob("probabilities.json")):
        stage = probs_path.parent
        if not (stage / "run.meta.json").exists():
            continue
        results = count_results(stage)
        if not results:
            continue
        meta = _load_json(stage / "run.meta.json")
        processed = (
            (meta.get("execution_stats") or {}).get("items_processed") or 0
        )
        probs = _load_json(probs_path)
        # A batch stage booking zero items is a BOOKING failure, not a
        # legitimate zero: the Batch API reports usage per response and the
        # path has read it since 2026-09-17 (aggregate_batch_usage). Until
        # 2026-09-19 such stages were skipped here as "nothing to lose"
        # (audit lens B), which is exactly how a regression of that booking
        # would hide. A realtime stage at zero has nothing to compare.
        if processed <= 0 and probs.get("mode") != "batch":
            continue
        if results - processed < min_shortfall:
            continue
        history = probs.get("cleanup_history") or []
        main_covered: int | None = None
        if history and isinstance(history[0], dict):
            initial_missing = history[0].get("initial_missing")
            if isinstance(initial_missing, int):
                main_covered = results - initial_missing

        audit: StageAudit | None = None
        audit_error: str | None = None
        try:
            audit = audit_stage(
                stage, tier=tier, default_model=default_model,
                register=register,
            )
        except (FileNotFoundError, RateCardError) as exc:
            audit_error = str(exc)

        prior_files = (
            [p.source for p in audit.passes if p.kind == "legacy-prior"]
            if audit is not None
            else [
                path.name
                for pattern in LEGACY_PRIOR_META_GLOBS
                for path in sorted(stage.glob(pattern))
            ]
        )
        if audit is not None and audit.format == "fixed":
            classification = "MERGED"
        elif prior_files:
            classification = "RECOVERABLE"
        elif audit is not None and audit.format == "register-recovered":
            classification = "RECOVERED-FROM-GIT"
        else:
            classification = "UNRECOVERABLE"
        signatures.append(
            StageSignature(
                stage=str(stage),
                results=results,
                items_processed=processed,
                shortfall=results - processed,
                mode=probs.get("mode"),
                cleanup_history=len(history),
                main_pass_covered=main_covered,
                prior_meta_files=prior_files,
                sibling_candidates=(
                    _sibling_candidates(stage, results - processed)
                    if classification == "UNRECOVERABLE"
                    else []
                ),
                classification=classification,
                audited_usd=audit.audited_usd if audit is not None else None,
                audit_error=audit_error,
            ),
        )
    return sorted(signatures, key=lambda s: -s.shortfall)


def _print_stage(audit: StageAudit) -> None:
    """Print one stage's audit as a table.

    Args:
        audit: The stage audit to render.
    """
    print(f"stage: {audit.stage}")
    print(f"format: {audit.format}   results: {audit.results}")
    print()
    for pass_audit in audit.passes:
        marker = " " if pass_audit.counted else "~"
        print(
            f" {marker}{pass_audit.source:44s} {pass_audit.kind:14s} "
            f"n={pass_audit.items:7d} cache={pass_audit.cached_share:.3f} "
            f"audited=${pass_audit.audited_usd:10.4f}"
        )
    if any(not p.counted for p in audit.passes):
        print("  (~ = cross-check row, not added to the total)")
    print("  " + "-" * 96)
    per_candidate = audit.audited_usd_per_candidate
    per_text = (
        f"${per_candidate:.6f}/candidate" if per_candidate else "n/a"
    )
    print(
        f"  {'STAGE TOTAL (audited)':44s} {'':14s} "
        f"n={audit.items_covered:7d} {'':11s} "
        f"audited=${audit.audited_usd:10.4f}  {per_text}"
    )
    if audit.meta_only_usd is not None:
        label = "run.meta.json cost_estimate ALONE"
        line = f"  {label:44s} ${audit.meta_only_usd:10.4f}"
        if audit.meta_only_usd and audit.audited_usd > audit.meta_only_usd:
            factor = audit.audited_usd / audit.meta_only_usd
            print(f"{line}  — {factor:,.1f}x BELOW the audited total")
        else:
            print(f"{line}  — do NOT use at a gate")
    for note in audit.notes:
        print(f"  ! {note}")
    print()


def _print_sweep(signatures: list[StageSignature]) -> None:
    """Print the retrospective sweep as a table.

    Args:
        signatures: The sweep's findings.
    """
    header = (
        f"{'stage':84s} {'results':>8s} {'meta n':>8s} {'short':>7s} "
        f"{'main?':>6s} {'class':14s} {'audited':>10s}"
    )
    print(header)
    print("-" * len(header))
    for sig in signatures:
        main_text = (
            str(sig.main_pass_covered)
            if sig.main_pass_covered is not None
            else "-"
        )
        cost_text = (
            f"${sig.audited_usd:9.4f}" if sig.audited_usd is not None else
            "        —"
        )
        print(
            f"{sig.stage:84s} {sig.results:8d} {sig.items_processed:8d} "
            f"{sig.shortfall:7d} {main_text:>6s} {sig.classification:14s} "
            f"{cost_text:>10s}"
        )
        if sig.audit_error:
            print(f"    not priced: {sig.audit_error}")
        if sig.prior_meta_files:
            print(f"    prior meta: {', '.join(sig.prior_meta_files)}")
        if sig.sibling_candidates:
            print(
                "    sibling candidates (adjudicate manually): "
                + ", ".join(sig.sibling_candidates)
            )
    print()
    counts: dict[str, int] = {}
    for sig in signatures:
        counts[sig.classification] = counts.get(sig.classification, 0) + 1
    print(
        "stages with the cleanup-overwrite signature: "
        f"{len(signatures)} — "
        + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
    )


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Argument vector, for testing. Defaults to ``sys.argv[1:]``.

    Returns:
        A process exit status: 0 on success, 2 on a usage or rate-card
        error, 1 when a stage is incomplete (audit mode only), so a driver
        can gate on completeness.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Audited flex cost of a verifier leg, summed across its main "
            "and cleanup passes. Never reads run.meta.json alone."
        ),
    )
    parser.add_argument(
        "stages",
        nargs="*",
        type=Path,
        help="Verifier stage directories (each holding run.meta.json)",
    )
    parser.add_argument(
        "--sweep",
        type=Path,
        default=None,
        help=(
            "Retrospective mode: walk this tree and classify every stage "
            "whose meta understates its candidate load"
        ),
    )
    parser.add_argument(
        "--min-shortfall",
        type=int,
        default=1,
        help="Sweep only: smallest meta-vs-results gap to report",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Rate card override, for passes that record no model of their "
            "own. A pass that records a model is always priced at it, and "
            "a disagreement is warned about. Without this flag a pass "
            "recording no model is refused rather than guessed at."
        ),
    )
    parser.add_argument(
        "--tier",
        default="flex",
        choices=sorted(TIER_DISCOUNT),
        help="Service tier actually used (default: flex)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit JSON instead of a table",
    )
    parser.add_argument(
        "--pass-file",
        action="append",
        type=Path,
        default=None,
        dest="pass_files",
        help=(
            "Repeatable: price these metadata files as one stage, summed. For "
            "passes that are not a stage on disc (a main-pass backup, or a "
            "blob extracted from git history)."
        ),
    )
    parser.add_argument(
        "--recovery-register",
        type=Path,
        default=RECOVERY_REGISTER_DEFAULT,
        help=(
            "Recovery register to read pre-overwrite passes from "
            f"(default: {RECOVERY_REGISTER_DEFAULT})"
        ),
    )
    parser.add_argument(
        "--no-recovery-register",
        action="store_true",
        help=(
            "Ignore the recovery register, to see a stage as the working tree "
            "alone reports it"
        ),
    )
    args = parser.parse_args(argv)

    if args.model is not None and args.model not in RATE_CARDS:
        print(
            f"error: no rate card for {args.model!r}; "
            f"known: {sorted(RATE_CARDS)}",
            file=sys.stderr,
        )
        return 2

    register = load_recovery_register(
        None if args.no_recovery_register else args.recovery_register,
    )

    if args.pass_files:
        try:
            audit = audit_files(
                args.pass_files, tier=args.tier, default_model=args.model,
            )
        except (FileNotFoundError, RateCardError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.as_json:
            print(json.dumps(asdict(audit), indent=2))
        else:
            _print_stage(audit)
        return 0

    if args.sweep is not None:
        if not args.sweep.is_dir():
            print(f"error: not a directory: {args.sweep}", file=sys.stderr)
            return 2
        signatures = sweep(
            args.sweep,
            tier=args.tier,
            default_model=args.model,
            min_shortfall=args.min_shortfall,
            register=register,
        )
        if args.as_json:
            print(json.dumps([asdict(s) for s in signatures], indent=2))
        else:
            _print_sweep(signatures)
        return 0

    if not args.stages:
        parser.error(
            "give at least one stage directory, --sweep <root>, or "
            "--pass-file <file>",
        )

    audits: list[StageAudit] = []
    for stage in args.stages:
        try:
            audits.append(
                audit_stage(
                    stage, tier=args.tier, default_model=args.model,
                    register=register,
                ),
            )
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        except RateCardError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    if args.as_json:
        print(json.dumps([asdict(a) for a in audits], indent=2))
    else:
        for audit in audits:
            _print_stage(audit)
        if len(audits) > 1:
            total = sum(a.audited_usd for a in audits)
            print(f"ALL STAGES (audited, {args.tier}): ${total:.4f}")
    return 1 if any(not a.complete for a in audits) else 0


if __name__ == "__main__":
    sys.exit(main())
