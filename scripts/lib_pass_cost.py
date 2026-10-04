#!/usr/bin/env python3
"""
The passes register's cost for one pass: tier evidence, then the one price function.

Why this module exists
----------------------
The register (``results/passes-manifest.json``) published each pass's
``cost_usd`` by copying the meta's ``cost_estimate.total_cost_usd`` — a
figure written at the call site with no cache rate and, on the verifier
path, no tier (``planning/cost-accounting-fix-plan-2026-09-21.md`` § 1.3).
PI ruling D11 makes the register's figure the AUDITED basis instead: the
pass's own tokens priced through :func:`scripts.lib_cost.price_usage` at
the tier the pass ran at, on its own date. This module supplies the two
things that sentence needs and the metas do not record:

1. **The tier.** No meta written before 2026-09-21 records its service tier.
   Worse, from 2026-08-18 (commit ``d0a709059``) the real-time writer
   stamped ``discount_reason: "Gemini real-time flex"`` as a CONSTANT, so
   that label is an assumption made at the call site, not a record, and is
   ignored here. The tier is instead inferred from evidence, strongest
   first, and the evidence is cited per pass:

   ========================  ==================================================
   ``applied-header``        the tier that SERVED each request, from the
                             ``x-gemini-service-tier`` response header (runs from
                             2026-10-03): per item (``service_tier_applied``) or
                             counted per run (``usage_stats.served_tier_counts``).
                             It pins only when EVERY response reported a tier
                             (see below)
   ``batch-marker``          ``batch_api`` block in the meta (unless a real-time
                             resume merge carried it, D36), ``batch_jobs.json``
                             beside it, or ``probabilities.json`` ``mode: batch``
   ``runner-record-batch``   a ``cost/2`` block (WP2 onwards) priced on the Batch
                             API path: structural, like a batch marker
   ``batch-path-pricing``    a ``discount_reason`` naming the Batch API (only
                             the batch path writes it)
   ``cached-path``           the run used an EXPLICIT context cache on the
                             real-time path, whose request config omits
                             ``service_tier``: billed at standard, whatever the
                             launch line asked for (see below). Read from a log
                             recording the cache, or from the fragment's own
                             requests all reporting one cached size (D34 (1),
                             :func:`cache_signature`)
   ``runner-record``         a ``cost/2`` block whose tier came from the CLI: the
                             tier REQUESTED, which the cached path can drop
   ``run-log``               the runner's ``Service tier: <tier>`` launch line in
                             the fragment's OWN directory
                             (``data/pricing/run-log-tiers.json``)
   ``launch-manifest``       ``service_tier`` in a ``launch_manifest.json``
   ``attestation``           the PI's dated attestation
                             (``data/pricing/tier-attestations.json``)
   ``run-log-inherited``     a launch line in an ENCLOSING directory: it
                             describes the run's launch, which a verifier leg
                             or a later batch rung beneath it need not share,
                             so for a verifier leg only the tiers the log
                             records FOR a verifier stage count
   ``launch-manifest-``      a launch manifest in an enclosing directory, at the
   ``inherited``             same rank
   ``billing-day``           the tiers the invoice billed for the model on the
                             pass's Pacific-time billing days
                             (``data/pricing/billing-day-tiers.json``)
   ``verifier-mode``         ``probabilities.json`` ``mode: realtime`` (rules
                             out batch, decides nothing else)
   ========================  ==================================================

   Single-tier evidence PINS the tier; set-valued evidence (billing days,
   real-time mode, a log directory naming two tiers) NARROWS it. Pins that
   disagree, or a pin the billing excludes, are reported as conflicts, never
   silently resolved; an inherited log overruled by the fragment's own
   evidence is recorded as a note, because a run-level launch line and a
   leg-level batch marker describe different launches.

   Billing days are read two ways. A CONTINUOUS fragment (its span is its
   own run time, within six hours) billed on every Pacific day it touched,
   so the tiers are intersected across those days, and a tier whose whole
   day's billed output (from single-day exports) is smaller than the
   fragment's own output is ruled out: the fragment cannot have run there.
   A RESUMED fragment (a meta whose start and end are sessions apart, up to
   four months on this corpus) is held only to its first and last days, and
   their tiers are UNITED, because its sessions may have run at different
   tiers.

2. **The pass's whole spend.** A pass is its primary meta plus every
   ``run_N_recovery*`` fragment beside it (the register's tile count already
   unions them; its tokens and cost did not, 118 M tokens on 57 passes when
   measured 2026-10-03). Each fragment is priced at ITS OWN tier and date,
   because a recovery can run at a different tier from its pass (the
   ``gemini37-55map-2026-08-29`` run-2 recovery ran at standard).

**The served tier.** From 2026-10-03 every real-time response records the
tier that served it. Where every response of a fragment reported one tier,
that tier is pinned, above every other record. Where they reported several,
the fragment is priced across exactly those tiers (an upper bound), and a
request record naming one of them is a note, not a conflict: the API's
statement of what it served outranks what was asked for. Where only some
responses reported a tier (a meta that merged a pre-header leg), the
reported tiers WIDEN the candidates instead of narrowing them: the
unreported responses may have run elsewhere, and narrowing would
understate. The invoice's tiers for the day (without the volume rule, which
tests the whole fragment) and the PI's attestation of the meta are set
against the served tiers as conflicts; a batch marker beside them is a note
(a real-time cleanup or retry ran too); a request record yields. A response served at a tier the rate card does not
price makes the fragment unpriceable, because any card tier could
understate it.

**The cached-path defect (fixed).** Until ``2df65047e`` (2026-10-03
12:02:23 UTC) ``scripts/4_detect_mounds_batch.py`` built a fresh
``GenerateContentConfig`` for requests that use an explicit context cache
(``--use-cache``) and did not copy ``service_tier`` into it (the block
dated from ``76a2cc719``, 2026-03-28; flex arrived on the main path only,
``2a2cd81c7``, 2026-04-09). Such a run prints ``Service tier: flex``
at launch and is billed at standard. Found 2026-10-03 when the volume rule
showed ``h8-v2`` (35 passes, 23.25 M output tokens on 2026-04-15 Pacific,
every launch log reading flex) against 0.60 M flex output billed for the
whole day; the two runs whose logs record an explicit cache (``h8-v2`` and
``55maps-image-generalisation``) are the two that fall in the April
standard-tier window. A log directory recording an explicit cache therefore
pins standard for a real-time fragment beneath it, outranking the launch
line it sits beside, unless the fragment's own code had the fix: every
commit its meta records (``environment.git_commit``, or ``git_commits`` for
a merged meta) descends from ``2df65047e``, or every response reported its
served tier. The test is the code a run executed, not the
date it ran: a run launched after the fix from a checkout without it (the
fix reached ``main`` only when this branch merged) still dropped its tier.
A meta whose commit cannot be resolved stays subject to the rule, which
can only overstate (standard is the dearer real-time tier).

A pass whose meta a cleanup leg overwrote carries its report's figure where
``data/pricing/cost-overrides.json`` publishes one (``published``, D13).
Otherwise it is a PARTIAL pass, as is a verifier leg whose meta accounts for
fewer requests than its ``probabilities.json`` has results (the overwrite
signature, detected), and a pass with a fragment that recorded no usage. A
partial pass publishes a floor: the sum of each priced fragment's lowest
candidate, labelled ``audited-lower-bound``.

When the evidence leaves more than one tier possible, the pass is priced at
every candidate and published at the HIGHEST, with ``cost_basis:
"audited-upper-bound"`` and both bounds in ``cost_source``, so the register
never understates and moves only downward as evidence arrives (the PI's
choice, 2026-10-03). Candidates that price within half a cent of each other
are reported as ``audited``: the tier is unknown but the cost is not.

Usage::

    from scripts.lib_pass_cost import PassCoster
    coster = PassCoster()
    result = coster.cost_pass(pass_id="run::pool::run1", fragments=[(meta, meta_path)],
                              run_id="run", pool="pool", run_dir=run_dir, model=row_model)
    row.update(result)          # cost_usd, cost_basis, cost_source

Created: 2026-10-03 (WP3 of the cost accounting plan)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import fnmatch
import json
import re
import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from scripts.lib_cost import (
    TIERS,
    RateCardError,
    UnknownModelError,
    is_unrecorded,
    price_usage,
    rate_card_identity,
    resolve_model,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRICING_DIR = PROJECT_ROOT / "data" / "pricing"
BILLING_DAYS = PRICING_DIR / "billing-day-tiers.json"
RUN_LOG_TIERS = PRICING_DIR / "run-log-tiers.json"
ATTESTATIONS = PRICING_DIR / "tier-attestations.json"
OVERRIDES = PRICING_DIR / "cost-overrides.json"

#: Cloud Billing dates usage in US Pacific time
#: (``reports/billing-reconciliation-2026-09-11.md`` § 3.1).
PACIFIC = ZoneInfo("America/Los_Angeles")

#: Order in which pinning evidence is believed when two pins disagree. A
#: batch marker is a structural fact of the path that ran; the PI's
#: attestation is recollection, so the machine record outranks it, and the
#: disagreement is reported either way.
PIN_PRIORITY = ("applied-header", "batch-marker", "runner-record-batch", "batch-path-pricing",
                "cached-path",
                "runner-record", "run-log", "launch-manifest", "attestation",
                "run-log-inherited", "launch-manifest-inherited")

#: Evidence that the path which ran was the Batch API. Any of it rules the
#: cached-path rule out, because that rule is about the real-time call.
BATCH_KINDS = ("batch-marker", "runner-record-batch", "batch-path-pricing")

#: Evidence that records the tier a run ASKED for, not the one it was billed
#: at; the cached-path rule overrules these without calling it a conflict.
#: The WP2 runner's CLI-sourced ``cost/2`` tier is one of them: the cached
#: request that dropped ``service_tier`` still records the switch it was given
#: (audit lenses A and B, 2026-10-03).
REQUEST_RECORDS = ("runner-record", "run-log", "run-log-inherited", "launch-manifest",
                   "launch-manifest-inherited")

#: Kinds that describe a whole run rather than the fragment's own launch.
INHERITED_KINDS = ("run-log-inherited", "launch-manifest-inherited")

#: A verifier meta that accounts for fewer requests than this share of its
#: leg's ``probabilities.json`` results was overwritten by a later leg.
COVERAGE_FLOOR = 0.9

#: Where the cached call path dropped ``service_tier`` (cited in evidence).
CACHED_PATH_CITE = ("scripts/4_detect_mounds_batch.py cached-call GenerateContentConfig "
                    "omitted service_tier from 76a2cc719 until 2df65047e")

#: The commit that fixed the cached path. A fragment whose recorded code
#: descends from it sent its tier on the cached call too.
CACHED_PATH_FIX_COMMIT = "2df65047ed913f93ff8b7319bc89e478676194d9"

#: A recorded commit, abbreviated or full; anything else keeps the cached-path rule.
_COMMIT_HASH = re.compile(r"[0-9a-f]{7,40}")

#: The ``served_tier_counts`` key for a response that carried no tier header.
UNREPORTED = "unreported"

#: A fragment whose span exceeds its own recorded run time by more than this
#: was resumed in a later session, and is not held to every day in between.
RESUME_GAP_S = 6 * 3600

#: With no recorded run time, a span longer than this is treated as resumed.
CONTINUOUS_MAX_S = 36 * 3600

#: Slack on the volume rule, for rounding in the console's token counts.
VOLUME_SLACK = 1.001

#: Candidate tiers whose prices differ by less than this are one cost.
INDIFFERENT_USD = 0.005

#: ``cost_basis`` values the register may carry (passes schema).
BASES = ("audited", "audited-upper-bound", "audited-lower-bound", "published", "unrecorded",
         "unpriceable")


@dataclass(frozen=True)
class Evidence:
    """One piece of tier evidence: what it allows, and where it came from."""

    kind: str
    tiers: tuple[str, ...]
    ref: str

    @property
    def pins(self) -> bool:
        """Whether this evidence names exactly one tier."""
        return len(self.tiers) == 1

    def describe(self) -> str:
        """``kind: ref -> tier`` for ``cost_source``."""
        return f"{self.kind}: {self.ref} -> {'|'.join(self.tiers) or 'none'}"


@dataclass
class TierFinding:
    """The tier (or candidate tiers) a fragment ran at, with its reasons."""

    tier: str | None
    method: str
    candidates: tuple[str, ...]
    evidence: list[Evidence] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _rel(path: Path) -> str:
    """Repository-relative POSIX path (absolute paths outside the repo pass through)."""
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def pacific_days(start: str | None, end: str | None) -> list[str]:
    """The Pacific-time calendar days an interval touches, inclusive.

    Args:
        start: ISO timestamp with offset (a pass's start).
        end: ISO timestamp with offset (its end); the start alone if None.

    Returns:
        ISO dates, ascending; empty when ``start`` is missing.

    Examples:
        >>> pacific_days("2026-04-16T03:00:00+00:00", "2026-04-16T09:00:00+00:00")
        ['2026-04-15', '2026-04-16']
        >>> pacific_days(None, None)
        []
    """
    if not start:
        return []
    s = datetime.fromisoformat(start).astimezone(PACIFIC).date()
    e = datetime.fromisoformat(end or start).astimezone(PACIFIC).date()
    out, d = [], s
    while d <= e:
        out.append(d.isoformat())
        d += timedelta(days=1)
    return out


#: A meta whose ``items_processed`` exceeds its unique completed items by this
#: factor, and which carries a ``recovery_history``, was double-counted by the
#: 2026-05-02 recovery merge (``reports/token-load-audit-2026-06-12.md`` § 3.2).
MERGE_INFLATION_FACTOR = 1.5


def fragment_usage(meta: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """The usage block a fragment is priced (and counted) from.

    Normally the meta's own ``usage_stats``. The exception is a meta the
    2026-05-02 recovery merge inflated: it summed the original run's usage
    into the post-recovery cumulative usage, doubling every token class
    (TH7 run 1 records 25,694,714 input tokens = 2 x 12,828,582 + 37,550 for
    25 re-sent tiles). Its signature is a ``recovery_history`` block with
    ``items_processed`` well above the unique ``completed_items``. For such
    a meta the per-item records are summed instead, one per tile, which is
    the June audit's "clean" method (§§ 3.2, 3.4) and reproduces its figures
    exactly; it omits the re-sent tiles' second attempt (about 0.3 %).

    Args:
        meta: A parsed pass meta.

    Returns:
        ``(usage, note)``: the usage block, and None or a note saying it was
        rebuilt from per-item sums and why.
    """
    usage = meta.get("usage_stats") or {}
    es = meta.get("execution_stats") or {}
    pim = meta.get("per_item_metadata") or []
    completed = len(set(es.get("completed_items") or []))
    processed = es.get("items_processed") or 0
    inflated = (bool(meta.get("recovery_history")) and completed > 0
                and processed > MERGE_INFLATION_FACTOR * completed
                and pim and all(isinstance(it.get("tokens"), dict) for it in pim))
    if not inflated:
        return usage, None

    def total(key: str) -> int:
        return sum(int((it["tokens"].get(key) or 0)) for it in pim)

    rebuilt = {"total_input_tokens": total("input_tokens"),
               "total_cached_tokens": total("cached_input_tokens"),
               "total_output_tokens": total("output_tokens"),
               "total_thoughts_tokens": total("thoughts_tokens"),
               "total_tokens": total("total_tokens"),
               "n_responses_with_usage": len(pim)}
    note = (f"usage_stats double-counted by the 2026-05-02 recovery merge (items_processed "
            f"{processed} vs {completed} completed; token-load-audit-2026-06-12 § 3.2): "
            f"priced from the sum of {len(pim)} per-item records instead")
    return rebuilt, note


def is_continuous(start: str | None, end: str | None, duration_s: float | None) -> bool:
    """Whether a fragment ran in one sitting rather than across resumed sessions.

    Examples:
        >>> is_continuous("2026-04-16T01:00:00+00:00", "2026-04-16T05:00:00+00:00", 14000)
        True
        >>> is_continuous("2026-03-26T01:00:00+00:00", "2026-07-30T05:00:00+00:00", 20000)
        False
        >>> is_continuous("2026-04-16T01:00:00+00:00", "2026-04-18T05:00:00+00:00", None)
        False
    """
    if not start or not end:
        return True
    span = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()
    if duration_s is not None:
        return span - float(duration_s) <= RESUME_GAP_S
    return span <= CONTINUOUS_MAX_S


#: The schema of the provenance a carry-forward verifier stage writes.
CARRY_SCHEMA = "verifier-stage-carry/1"


def carried_forward(directory: Path) -> tuple[int, str, int] | None:
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
    doc = _read_json(path)
    if not isinstance(doc, dict) or doc.get("schema") != CARRY_SCHEMA:
        return None
    carried, uncovered = doc.get("carried"), doc.get("uncovered")
    extends = str(doc.get("extends_stage") or "")
    if not isinstance(carried, int) or carried <= 0 or not isinstance(uncovered, int) \
            or uncovered < 0 or not extends:
        return None
    return carried, extends, uncovered


def stage_exists(meta_path: Path, stage: str) -> bool:
    """Whether a repository-relative stage directory exists, found from a meta's path.

    The repository root is the nearest ancestor with a real git directory (one
    holding ``HEAD``), a ``.git`` file (a worktree), or the passes register.
    A bare ``.git`` directory does not count: an empty ``/tmp/.git`` on the
    workstation once passed for every scratch tree's root (S160).
    """
    for parent in meta_path.resolve().parents:
        git = parent / ".git"
        if (git / "HEAD").exists() or git.is_file() \
                or (parent / "results" / "passes-manifest.json").exists():
            return (parent / stage).is_dir()
    return False


def carry_explains(metas: list[tuple[dict[str, Any], Path]],
                   cover: tuple[int, int]) -> tuple[int, str] | None:
    """Whether a carry-forward explains a verifier leg's coverage shortfall.

    A carry-forward stage's metas account for fewer candidates than its
    ``probabilities.json`` holds because the rest were copied from the stage
    it extends, whose own leg prices them: its metas are its whole spend, not
    a floor. The exemption holds only when the metas account for every
    result the carry did NOT bring (the file's own ``uncovered`` count), the
    two together reach the results, and the extended stage exists. Testing
    ``accounted + carried`` alone was vacuous whenever the carry was 90 % of
    the results (WP4 re-audit, 2026-10-04: 756 of 759 passed with the meta
    covering none). Shared by the register (:meth:`PassCoster.cost_pass`) and
    the ``cost_audit.json`` sidecars, so the two never disagree on a basis
    (they did on the two 3.7 screen ``recovery-fixed`` legs until S160).

    Args:
        metas: The leg's ``(meta, path)`` list; the carry file sits beside
            the first.
        cover: ``(accounted, results)`` from :func:`verifier_coverage`.

    Returns:
        ``(carried, extends_stage)`` when the carry explains the shortfall,
        else None.
    """
    accounted, results = cover
    carry = carried_forward(metas[0][1].parent)
    if carry and accounted >= carry[2] and accounted + carry[0] >= results \
            and stage_exists(metas[0][1], carry[1]):
        return carry[0], carry[1]
    return None


def verifier_coverage(metas: list[tuple[dict[str, Any], Path]]) -> tuple[int, int] | None:
    """How many candidates a verifier leg's metas account for, against its results.

    Args:
        metas: ``(meta, path)`` for every priced meta of the leg (the primary
            first; a preserved main leg after it); ``probabilities.json`` sits
            beside the primary.

    Returns:
        ``(accounted, results)``, or None when the leg has no probabilities
        file. Per meta, the best count it records: unique completed items, else
        processed items, else requests or responses with usage divided by the
        leg's iterations (requests include retries and every iteration, so an
        unscaled count would let a partial meta pass; re-audit round 2). T03's
        meta records 10,539 requests and no completed items against 9,910
        results; the Gemini 3 batch legs record only processed items.
    """
    prob = metas[0][1].parent / "probabilities.json"
    if not prob.exists():
        return None
    doc = _read_json(prob) or {}
    # Results are keyed per CALL: a multi-iteration leg writes
    # ``candidate_00005_iter1`` to ``_iter5``. Coverage is counted in
    # CANDIDATES on both sides, so the keys are reduced to their candidates
    # (WP4b audit lens A, 2026-10-04; latent: every register leg runs one
    # iteration).
    results = len({str(key).rsplit("_iter", 1)[0] for key in (doc.get("results") or {})})
    if not results:
        return None
    iterations = max(int(doc.get("iterations") or 1), 1)
    accounted = 0
    for meta, _ in metas:
        es = meta.get("execution_stats") or {}
        usage = meta.get("usage_stats") or {}
        requests = max(int(((usage.get("by_provider") or {}).get("google_gemini") or {}).get(
                           "request_count") or 0),
                       int(usage.get("n_responses_with_usage") or 0))
        # Every side in CANDIDATES. A multi-iteration writer logs one
        # completion per call key (run_pv ``log_success(key)``), so completed
        # items are reduced to their candidates and processed items, which
        # count calls, are divided like the requests (WP4b re-audit B: the
        # half-fixed version read a real 5-iteration leg as (60, 12)).
        completed = {str(item).rsplit("_iter", 1)[0]
                     for item in (es.get("completed_items") or [])}
        accounted += (len(completed)
                      or int(es.get("items_processed") or 0) // iterations
                      or requests // iterations)
    return accounted, results


def _every_commit_has_fix(environment: dict[str, Any]) -> bool:
    """Whether every commit a meta records running has the cached-path fix.

    A merged meta lists each contributing commit in ``git_commits``
    (``merge_meta``, 2026-10-03); a single run records ``git_commit``.
    """
    commits = environment.get("git_commits") or [environment.get("git_commit")]
    return bool(commits) and all(has_cached_path_fix(c) for c in commits)


def has_cached_path_fix(commit: Any) -> bool:
    """Whether a run's recorded code commit contains the cached-path fix.

    Asks git whether :data:`CACHED_PATH_FIX_COMMIT` is an ancestor of (or is)
    *commit*. A missing commit, one this clone does not hold, or no git at
    all answers False, which keeps the cached-path rule: the conservative
    answer, because the rule can only price a fragment at the dearer tier.
    Metas written before the round-8 fix (2026-10-03) recorded the commit at
    FINALISE time, so a pull during a run could name a later commit than the
    code loaded. Of those, only the four probe runs of 2026-10-03 record a
    commit with the fix (``651a2eb90``), and they ran on it: each lasted
    under a minute, after the fix was committed.

    Args:
        commit: ``environment.git_commit`` from a meta (full or abbreviated).

    Returns:
        True only when git confirms the ancestry.
    """
    if not isinstance(commit, str) or not _COMMIT_HASH.fullmatch(commit):
        # Only a hash counts: a ref such as "HEAD" or a branch name would ask
        # git about TODAY's checkout, not the run's ("unknown", "-dirty"
        # suffixes and empty values keep the rule too).
        return False
    return _descends_from_fix(commit)


@lru_cache(maxsize=None)
def _descends_from_fix(commit: str) -> bool:
    """Git's answer for one commit string, cached (type-checked by the caller)."""
    try:
        done = subprocess.run(["git", "merge-base", "--is-ancestor", CACHED_PATH_FIX_COMMIT,
                               commit], cwd=PROJECT_ROOT, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def attestation_glob_problem(pattern: Any) -> str | None:
    """Why an attestation's ``meta`` glob could never apply, or None if it can.

    Matched the way :meth:`PassCoster.attestation` matches (``fnmatch`` over
    the repository-relative path; absolute only outside the repository),
    over the files beneath the pattern's literal directory prefix.

    Args:
        pattern: The attestation's ``meta`` value.

    Returns:
        A reason the glob is refused, or None when it matches a file.

    Examples:
        >>> attestation_glob_problem("../x")
        'climbs out of its directory'
        >>> attestation_glob_problem("outputs/*/run.meta.json")
        'names fewer than two directories before its first wildcard (too broad to check)'
    """
    if not isinstance(pattern, str) or not pattern:
        return "is not a non-empty string"
    if ".." in pattern.split("/"):
        return "climbs out of its directory"
    if pattern.startswith("/") and Path(pattern).is_relative_to(PROJECT_ROOT):
        # attestation() compares against the REPOSITORY-RELATIVE path, so an
        # absolute path inside the repository could never match (audit A L1).
        return "is absolute inside the repository: write it repository-relative"
    literal = pattern
    for ch in "*?[":
        literal = literal.split(ch, 1)[0]
    if literal != pattern and "/" not in literal.rsplit("/", 1)[0].strip("/"):
        # Fewer than two directories before the first wildcard would walk the
        # whole repository, or its parent (``outputs/*/...`` took 17.6 s).
        return ("names fewer than two directories before its first wildcard (too broad "
                "to check)")
    root = Path(literal) if literal.startswith("/") else PROJECT_ROOT / literal
    if literal == pattern:
        return None if root.is_file() else "matches no file"
    base = root if literal.endswith("/") else root.parent
    if base.is_dir() and any(f.is_file() and fnmatch.fnmatchcase(_rel(f), pattern)
                             for f in base.rglob("*")):
        return None
    return "matches no file"


def served_tiers(meta: dict[str, Any]) -> tuple[dict[str, int], int] | None:
    """Responses per served tier, and the number of responses they must cover.

    The run-level ``usage_stats.served_tier_counts`` is read first, because
    ``merge_meta`` sums it with the tokens it describes, whereas per-item
    records are deduplicated by ``item_id`` on a merge (a superseded
    attempt's record is dropped, its tokens kept). Per-item
    ``service_tier_applied`` is the fallback, for a meta written between the
    per-item field (``651a2eb90``) and the run-level count.

    Args:
        meta: A parsed meta.

    Returns:
        ``(counts, responses)``: counts keyed by the header's value, lower-cased
        (``unreported`` for none), and the responses the fragment's usage
        covers (the provider's request count, or the counts' own sum if
        larger). None when the meta records no served tier at all, which is
        every meta written before 2026-10-03.

    Examples:
        >>> served_tiers({"usage_stats": {"served_tier_counts": {"flex": 3},
        ...     "by_provider": {"google_gemini": {"request_count": 4}}}})
        ({'flex': 3}, 4)
        >>> served_tiers({"per_item_metadata": [{"service_tier_applied": "Flex"}, {}]})
        ({'flex': 1, 'unreported': 1}, 2)
        >>> served_tiers({"usage_stats": {}}) is None
        True
    """
    usage = meta.get("usage_stats") or {}
    counts: dict[str, int] = {}
    for key, n in (usage.get("served_tier_counts") or {}).items():
        tier = str(key).lower()
        counts[tier] = counts.get(tier, 0) + int(n or 0)
    if not counts:
        for item in meta.get("per_item_metadata") or []:
            tier = str(item.get("service_tier_applied") or UNREPORTED).lower()
            counts[tier] = counts.get(tier, 0) + 1
    if not any(n and t != UNREPORTED for t, n in counts.items()):
        return None
    requests = int(((usage.get("by_provider") or {}).get("google_gemini") or {}).get(
        "request_count") or 0)
    return counts, max(requests, sum(counts.values()))


def realtime_resume_only(meta: dict[str, Any]) -> bool:
    """Whether a meta's recorded usage is all a later real-time resume's.

    A Batch API pass whose own execution recorded no usage can be resumed
    in real time weeks later; the resume merge keeps the original's
    ``batch_api`` block, so the block then describes an execution the meta
    holds no tokens for (the two ``pv-diag-384`` pro-medium baseline run 1
    metas: batch on 2026-03-23 with zero usage, 26 real-time requests on
    2026-06-03; PI ruling D36). All four must hold, else the block stands:

    - the meta records a ``recovery_history`` (the real-time runner's resume);
    - its per-item records are exactly its requests (none unrecorded);
    - every one was sent more than :data:`RESUME_GAP_S` after the meta's
      start, so none belongs to the original session.

    Args:
        meta: A parsed meta.

    Returns:
        True when the ``batch_api`` block must not pin the meta's usage.

    Examples:
        >>> item = {"request_timestamp": "2026-06-03T12:26:39+00:00"}
        >>> meta = {"recovery_history": [{"recovered": 1}], "per_item_metadata": [item],
        ...         "timestamp": {"start": "2026-03-23T15:11:34+00:00"},
        ...         "usage_stats": {"by_provider": {"google_gemini": {"request_count": 1}}}}
        >>> realtime_resume_only(meta)
        True
        >>> realtime_resume_only({**meta, "recovery_history": []})
        False
    """
    items = meta.get("per_item_metadata") or []
    start = (meta.get("timestamp") or {}).get("start")
    requests = int((((meta.get("usage_stats") or {}).get("by_provider") or {})
                    .get("google_gemini") or {}).get("request_count") or 0)
    if not meta.get("recovery_history") or not items or not start or requests != len(items):
        return False
    origin = datetime.fromisoformat(start)
    for item in items:
        sent = item.get("request_timestamp")
        if not sent or (datetime.fromisoformat(sent) - origin).total_seconds() <= RESUME_GAP_S:
            return False
    return True


def billed_cache_sizes(meta: dict[str, Any]) -> list[int]:
    """The cached input tokens of each billed request a meta records.

    Requests that recorded no input tokens were not billed (a failure before
    the model ran) and are left out, as is the per-item record a merge
    dropped for a superseded attempt.

    Args:
        meta: A parsed meta.

    Returns:
        One count per billed request, in record order; empty for a meta
        without per-item records.

    Examples:
        >>> billed_cache_sizes({"per_item_metadata": [
        ...     {"tokens": {"input_tokens": 900, "cached_input_tokens": 0}},
        ...     {"tokens": {"input_tokens": 0}}]})
        [0]
    """
    return [int((item.get("tokens") or {}).get("cached_input_tokens") or 0)
            for item in meta.get("per_item_metadata") or []
            if (item.get("tokens") or {}).get("input_tokens")]


def cache_signature(meta: dict[str, Any]) -> tuple[int, int] | None:
    """An explicit context cache's size, when every billed request reports it.

    An explicit cache (``--use-cache``) is attached to every request, so each
    one reports the cache's exact size as ``cached_input_tokens``: 14,549 on
    all 487 requests of ``pv-diag-384``'s image passes, against 0 on the
    matching text passes. The PI ruled the signature sufficient to establish
    the cached path where a pass's own "Context cache created" line did not
    survive (D34 (1), 2026-10-04). One count on every request is NOT enough
    by itself: implicit caching hit every request of image-b's no-cache
    recoveries (16,272 tokens, where that pool's explicit cache is 18,909).
    The caller therefore also requires the size to be one a log records for
    an explicit cache (``PassCoster.cache_sizes``). A false reading can only
    overstate a cost, as the cached path is billed at standard, the dearer
    real-time tier.

    Requests that recorded no input tokens are left out
    (:func:`billed_cache_sizes`).

    Args:
        meta: A parsed meta.

    Returns:
        ``(cached tokens per request, requests)``, or None when no request
        recorded usage or the counts are not one positive value.

    Examples:
        >>> item = {"tokens": {"input_tokens": 15659, "cached_input_tokens": 14549}}
        >>> cache_signature({"per_item_metadata": [item, item]})
        (14549, 2)
        >>> cache_signature({"per_item_metadata": [item, {"tokens": {
        ...     "input_tokens": 900, "cached_input_tokens": 0}}]}) is None
        True
        >>> failed = {"tokens": {"input_tokens": 0, "cached_input_tokens": 0}}
        >>> cache_signature({"per_item_metadata": [item, failed]})
        (14549, 1)
    """
    sizes = billed_cache_sizes(meta)
    if sizes and sizes[0] > 0 and all(s == sizes[0] for s in sizes):
        return sizes[0], len(sizes)
    return None


class PassCoster:
    """Prices register passes on the audited basis from committed evidence.

    Args:
        billing_path: ``billing-day-tiers.json`` (tests pass fixtures).
        logs_path: ``run-log-tiers.json``.
        attestations_path: ``tier-attestations.json``.
        overrides_path: ``cost-overrides.json`` (published figures and lower bounds).
        card_path: An alternative rate card, for tests.
    """

    def __init__(self, billing_path: Path = BILLING_DAYS, logs_path: Path = RUN_LOG_TIERS,
                 attestations_path: Path = ATTESTATIONS, overrides_path: Path = OVERRIDES,
                 card_path: Path | None = None) -> None:
        self.billing = _read_json(billing_path)
        logs_doc = _read_json(logs_path)
        self.log_dirs: dict[str, dict[str, Any]] = logs_doc["directories"]
        #: Explicit-cache sizes the runner's logs print, with the logs (D34 (1)).
        self.cache_sizes: dict[int, list[str]] = {
            int(n): paths for n, paths in (logs_doc.get("explicit_cache_sizes") or {}).items()}
        self.attestations: list[dict[str, Any]] = _read_json(attestations_path)["attestations"]
        overrides_doc = _read_json(overrides_path)
        self.overrides: dict[str, dict[str, Any]] = overrides_doc["entries"]
        #: Tracked metas holding a leg's overwritten main execution, by pass_id.
        self.main_legs: dict[str, dict[str, Any]] = overrides_doc.get(
            "preserved_main_legs", {})
        for pid, entry in self.overrides.items():
            if entry.get("basis") not in ("published", "audited-lower-bound") or not entry.get(
                    "source") or (entry["basis"] == "published" and entry.get("cost_usd") is None):
                raise ValueError(f"cost override for {pid!r} needs basis published (with "
                                 "cost_usd) or audited-lower-bound, and a source")
        self.card_path = card_path
        self.card_identity = rate_card_identity(card_path)
        self._validate_attestations()

    # -- evidence ------------------------------------------------------------

    def _validate_attestations(self) -> None:
        """Refuse an attestation file that cannot be applied unambiguously."""
        required = {"id", "run_id", "pool", "tier", "attested_by", "attested_on", "evidence"}
        ids = set()
        for att in self.attestations:
            missing = required - set(att)
            if missing:
                raise ValueError(f"tier attestation {att.get('id')!r} lacks {sorted(missing)}")
            if att["tier"] not in TIERS:
                raise ValueError(f"tier attestation {att['id']!r}: unknown tier {att['tier']!r}")
            if att["id"] in ids:
                raise ValueError(f"tier attestation id {att['id']!r} is duplicated")
            ids.add(att["id"])
            problem = attestation_glob_problem(att["meta"]) if "meta" in att else None
            if problem:
                # A glob that could never match would leave the attestation
                # silently never applying (re-audit round 7).
                raise ValueError(f"tier attestation {att['id']!r}: meta {att['meta']!r} "
                                 f"{problem}")

    def _log_evidence(self, directory: Path, run_dir: Path,
                      stage: str = "proposer") -> list[Evidence]:
        """Tiers named by the nearest enclosing directory's own logs.

        The walk stops at the first directory (from the fragment's own, up to
        and including the run directory) whose logs carry a tier line. A
        directory naming two tiers yields set-valued evidence; the walk does
        NOT continue upward past it, because a parent's logs describe the run
        as a whole and the child is where the disagreement lives. Each stage
        reads its own record: a proposer the launch lines (``tiers``), a
        verifier the tiers a log records FOR a verifier stage
        (``verifier_tiers``), in its own directory as in an enclosing one
        (audit rounds 1 and 2, 2026-10-03). Only the logs that supplied the
        tiers used are cited.
        """
        own, stop = directory.resolve(), run_dir.resolve()
        cur = own
        while True:
            entry = self.log_dirs.get(_rel(cur))
            key = "tiers" if stage == "proposer" else "verifier_tiers"
            tiers: list[str] = (entry or {}).get(key) or []
            if not tiers and entry and stage != "proposer" and cur == own:
                # A verifier leg's OWN directory log is that verifier's launch:
                # its tier lines count when no verifier-stage tier is recorded.
                key = "tiers"
                tiers = entry.get("tiers") or []
            if tiers:
                logs = ", ".join(lg["path"].rsplit("/", 1)[-1] for lg in entry["logs"]
                                 if lg.get(key))
                kind = "run-log" if cur == own else "run-log-inherited"
                found = [Evidence(kind, tuple(tiers), f"{_rel(cur)}/{{{logs}}}")]
                if entry.get("explicit_cache"):
                    found.append(Evidence("cached-path", ("standard",),
                                          f"{_rel(cur)} logs record an explicit context "
                                          f"cache; {CACHED_PATH_CITE}"))
                return found
            if cur == stop or cur == cur.parent or stop not in cur.parents:
                return []
            cur = cur.parent

    @staticmethod
    def _launch_manifest(directory: Path, run_dir: Path,
                         stage: str = "proposer") -> Evidence | None:
        """``service_tier`` from the nearest ``launch_manifest.json`` up to the run.

        The stage's own tier where the manifest resolves one
        (``resolved_config.proposer`` or ``.verify``), else the run's. One found
        above the fragment's own directory ranks as inherited evidence.
        """
        own, stop = directory.resolve(), run_dir.resolve()
        cur = own
        while True:
            lm = cur / "launch_manifest.json"
            if lm.exists():
                doc = _read_json(lm)
                section = "proposer" if stage == "proposer" else "verify"
                tier = ((doc.get("resolved_config") or {}).get(section) or {}).get(
                    "service_tier")
                if tier is None and stage == "proposer":
                    # The run-level tier describes the proposer launch; it is
                    # never a verifier's (re-audit round 2).
                    tier = doc.get("service_tier")
                if tier in TIERS:
                    kind = "launch-manifest" if cur == own else "launch-manifest-inherited"
                    return Evidence(kind, (tier,), _rel(lm))
                return None
            if cur == stop or cur == cur.parent or stop not in cur.parents:
                return None
            cur = cur.parent

    def direct_evidence(self, meta: dict[str, Any], meta_path: Path, run_dir: Path,
                        stage: str = "proposer") -> list[Evidence]:
        """Evidence a fragment carries in or beside its own meta.

        Args:
            meta: The parsed meta.
            meta_path: Where it lives.
            run_dir: The run's directory (the upward walks stop there).
            stage: ``proposer`` or ``verifier``. The cached-path rule is about
                the detection runner, which only proposer passes go through.

        Returns:
            Evidence items, possibly empty.
        """
        out: list[Evidence] = []
        here = meta_path.parent
        # The API's own statement of the tier that served each request: the
        # strongest evidence there is, where EVERY response recorded it. A
        # partial record cannot speak for the responses it lacks, so it is
        # "applied-header-partial", which widens the candidates (resolve).
        served = served_tiers(meta)
        full_header = False
        if served:
            counts, responses = served
            known = {t: n for t, n in counts.items() if t in TIERS and n}
            full_header = sum(known.values()) >= responses
            tally = ", ".join(f"{t} {n}" for t, n in sorted(counts.items()))
            out.append(Evidence("applied-header" if full_header else "applied-header-partial",
                                tuple(t for t in TIERS if t in known),
                                f"{_rel(meta_path)} served tiers ({tally}) of {responses} "
                                "responses"))
        # A batch_api block carried by a real-time resume merge describes
        # an execution the meta holds no tokens for (D36): it pins nothing.
        if meta.get("batch_api") and not realtime_resume_only(meta):
            out.append(Evidence("batch-marker", ("batch",), f"{_rel(meta_path)} batch_api block"))
        if (here / "batch_jobs.json").exists():
            out.append(Evidence("batch-marker", ("batch",), _rel(here / "batch_jobs.json")))
        prob = here / "probabilities.json"
        if prob.exists():
            mode = (_read_json(prob) or {}).get("mode")
            if mode == "batch":
                out.append(Evidence("batch-marker", ("batch",), f"{_rel(prob)} mode=batch"))
            elif mode == "realtime":
                out.append(Evidence("verifier-mode", ("flex", "standard"),
                                    f"{_rel(prob)} mode=realtime"))
        block = meta.get("cost_estimate") or {}
        pricing = block.get("pricing_used") or {}
        if block.get("schema") == "cost/2" and pricing.get("tier") in TIERS:
            source = str(pricing.get("tier_source") or "")
            ref = f"{_rel(meta_path)} cost/2 tier_source={source!r}"
            # A WP2 writer records where its tier came from. The Batch API path
            # is structural; a CLI switch is only what the run ASKED for (the
            # cached path drops it); any other source is an inference, not a record.
            if source.startswith("Batch API") and pricing["tier"] == "batch":
                out.append(Evidence("runner-record-batch", ("batch",), ref))
            elif source.startswith(("cli", "no --service-tier")):
                out.append(Evidence("runner-record", (pricing["tier"],), ref))
        # Only the batch path's own wording counts. The real-time CONSTANT reads
        # "Gemini real-time flex (50 % of list, as per Batch API)", so a
        # substring test for "batch api" would read every real-time pass of
        # 2026-08-18 to 2026-09-21 as batch (caught on its first run, 2026-10-03).
        reason = str(pricing.get("discount_reason") or "").strip().lower()
        if reason.startswith("google async batch api"):
            out.append(Evidence("batch-path-pricing", ("batch",),
                                f"{_rel(meta_path)} discount_reason names the Batch API"))
        logs = self._log_evidence(here, run_dir, stage)
        # The fragment's own requests can show the cached path where no log
        # line about the cache survived (D34 (1)): the same fact as a log's
        # "Context cache created", so it is cached-path evidence, subject to
        # the same exemptions just below. The size must be one a log records
        # for an explicit cache: implicit caching can also hit every request
        # (16,272 on all of image-b's no-cache recoveries, 2026-08-28; 99.9 %
        # of the Gemini 3 batch passes), but at a size of its own.
        signature = cache_signature(meta)
        if (signature and signature[0] in self.cache_sizes
                and not any(e.kind == "cached-path" for e in logs)):
            size, requests = signature
            logs.append(Evidence("cached-path", ("standard",),
                                 f"{_rel(meta_path)}: all {requests} requests with usage "
                                 f"report {size} cached input tokens, the exact size of the "
                                 f"explicit cache {self.cache_sizes[size][0]} records "
                                 f"(D34 (1)); {CACHED_PATH_CITE}"))
        # An explicit cache reports its size on every request it is attached
        # to, so a fragment none of whose billed requests reports a cached
        # token never used one, whatever its directory's logs record: one
        # run-level log can cover pools whose cache creation failed (the
        # n1-pro-rerun text pools, "Cached content is too small"; D34 (2)).
        sizes = billed_cache_sizes(meta)
        uncached = bool(sizes) and not any(sizes)
        if any(e.kind == "cached-path" for e in logs) and (
                stage != "proposer" or any(e.kind in BATCH_KINDS for e in out) or full_header
                or uncached or _every_commit_has_fix(meta.get("environment") or {})):
            # The cached-path rule is about the detection runner's REAL-TIME
            # call on code WITHOUT the fix, WITH a cache attached: a verifier
            # leg, a batch leg, a fragment whose every recorded commit
            # (git_commit, or a merge's git_commits) descends from 2df65047e,
            # one whose every response reported the tier that served it, or
            # one whose requests show no cache at all, is not subject to it.
            logs = [e for e in logs if e.kind != "cached-path"]
        out.extend(logs)
        lm = self._launch_manifest(here, run_dir, stage)
        if lm:
            out.append(lm)
        return out

    def attestation(self, run_id: str, pool: str, days: list[str],
                    meta_path: Path | None = None) -> Evidence | None:
        """The PI's attestation covering this fragment, if any.

        An attestation matches on ``run_id``, a glob over ``pool``, and, when
        it lists ``pacific_days``, only a fragment whose every billing day is
        listed; when it names ``meta`` (a glob over the repository-relative
        meta path), only that fragment of the pass (a leg's main run and its
        cleanup can run at different tiers). Two matching attestations naming
        different tiers are an error in the file, not a conflict to report.
        """
        hits = []
        for att in self.attestations:
            if att["run_id"] != run_id or not fnmatch.fnmatchcase(pool, att["pool"]):
                continue
            if att.get("meta") and not (meta_path is not None and fnmatch.fnmatchcase(
                    _rel(meta_path), att["meta"])):
                continue
            listed = att.get("pacific_days")
            if listed and not (days and set(days) <= set(listed)):
                continue
            hits.append(att)
        if not hits:
            return None
        tiers = {att["tier"] for att in hits}
        if len(tiers) > 1:
            raise ValueError(f"tier attestations {[a['id'] for a in hits]} disagree for "
                             f"{run_id}::{pool} on {days}")
        att = hits[0]
        return Evidence("attestation", (att["tier"],),
                        f"{att['id']} ({att['attested_by']}, {att['attested_on']})")

    def _allowed(self, model: str, day: str) -> tuple[set[str] | None, str]:
        """Tiers billed for *model* on one Pacific day, and from what."""
        days = self.billing["days"]
        if day in days:
            cell = days[day]["models"].get(model)
            if cell and cell["tiers"]:
                return set(cell["tiers"]), f"day export ({days[day]['project_filter']})"
            return None, "day export: model not billed"
        if day[:7] not in self.billing["months_covered"]:
            return None, "month not invoiced"
        ivs = self.billing["intervals"].get(model, {})
        tiers = {t for t, spans in ivs.items() if any(a <= day <= b for a, b in spans)}
        return (tiers or None), "invoice line windows"

    def _day_output(self, model: str, day: str, tier: str) -> int | None:
        """Output tokens billed for *model* at *tier* on a day, from a day export only."""
        cell = self.billing["days"].get(day, {}).get("models", {}).get(model)
        if not cell:
            return None
        return int((cell["tiers"].get(tier) or {}).get("output", 0))

    def billing_evidence(self, model: str, days: list[str], *, continuous: bool = True,
                         output_tokens: int = 0) -> Evidence | None:
        """What the invoice allows over the fragment's billing days.

        Args:
            model: The card's canonical model id.
            days: The Pacific days the fragment touched.
            continuous: Whether it ran in one sitting (see the module notes).
            output_tokens: Its output plus thinking tokens, for the volume rule.

        Returns:
            Set-valued evidence, or None when no day carries information.
        """
        if not continuous:
            ends = sorted({days[0], days[-1]}) if days else []
            allowed: set[str] = set()
            used = []
            for day in ends:
                tiers, how = self._allowed(model, day)
                if not tiers:
                    # A session on a day the invoice says nothing about could
                    # have run at any tier, so the union is every tier: one
                    # informative end day must not narrow it alone (audit
                    # lens A, 2026-10-03).
                    return None
                allowed |= tiers
                used.append(f"{day} {'|'.join(sorted(tiers))} [{how}]")
            if not used:
                return None
            return Evidence("billing-day", tuple(t for t in TIERS if t in allowed),
                            f"{model}: resumed over {days[0]}..{days[-1]}, first and last "
                            "days united: " + "; ".join(used))
        allowed = set(TIERS)
        used = []
        for day in days:
            tiers, how = self._allowed(model, day)
            if tiers is None:
                continue
            allowed &= tiers
            used.append(f"{day} {'|'.join(sorted(tiers))} [{how}]")
        if not used:
            return None
        # Volume rule: only where every touched day has a day export, so the
        # day's whole billed output at the tier is known.
        if output_tokens and all(d in self.billing["days"] for d in days):
            for tier in sorted(allowed):
                vols = [self._day_output(model, d, tier) for d in days]
                if None in vols:
                    continue
                if output_tokens > sum(vols) * VOLUME_SLACK:
                    allowed.discard(tier)
                    used.append(f"not {tier}: fragment output {output_tokens:,} exceeds the "
                                f"{sum(vols):,} {tier} output billed on {','.join(days)}")
        return Evidence("billing-day", tuple(t for t in TIERS if t in allowed),
                        f"{model}: " + "; ".join(used))

    # -- resolution ----------------------------------------------------------

    def resolve(self, *, meta: dict[str, Any], meta_path: Path, run_id: str, pool: str,
                run_dir: Path, model: str, start: str | None, end: str | None,
                duration_s: float | None = None, output_tokens: int = 0,
                stage: str = "proposer") -> TierFinding:
        """The tier one fragment ran at, from all the evidence there is.

        Args:
            meta: The fragment's parsed meta.
            meta_path: Its path.
            run_id: The register run id.
            pool: The register pool (or verifier label).
            run_dir: The run directory.
            model: The card's canonical model id for the fragment.
            start: Fragment start timestamp (ISO, with offset).
            end: Fragment end timestamp.
            duration_s: Its recorded run time, which tells a continuous
                fragment from a resumed one.
            output_tokens: Its output plus thinking tokens (the volume rule).
            stage: ``proposer`` or ``verifier``.

        Returns:
            The finding: a tier when one is pinned or the evidence narrows to
            one, else ``None`` with the candidate tiers.
        """
        days = pacific_days(start, end)
        evidence = self.direct_evidence(meta, meta_path, run_dir, stage)
        att = self.attestation(run_id, pool, days, meta_path)
        if att:
            evidence.append(att)
        bill = self.billing_evidence(model, days,
                                     continuous=is_continuous(start, end, duration_s),
                                     output_tokens=output_tokens)
        if bill:
            evidence.append(bill)
        conflicts: list[str] = []
        notes: list[str] = []
        # Header values outside the card's tiers never reach here through
        # cost_fragment, which refuses to price them; called directly, they
        # count as unreported (served_tiers keeps them out of "known").
        partial = [e for e in evidence if e.kind == "applied-header-partial"]
        mixed = [e for e in evidence if e.kind == "applied-header" and not e.pins]
        if mixed:
            return self._served_mixed(mixed[0], evidence, notes)
        finding = self._resolve_records(
            [e for e in evidence if e.kind != "applied-header-partial"], conflicts, notes)
        # The invoice's tiers for the day WITHOUT the volume rule: the volume
        # rule tests the whole fragment's output, and a partial header speaks
        # for only part of it (re-audit A, round 9).
        day_set = self.billing_evidence(model, days,
                                        continuous=is_continuous(start, end, duration_s))
        for e in partial:
            # Some responses reported the tier that served them, the rest did
            # not: the fragment ran at least partly at each reported tier, so
            # every one of them is a candidate, whatever the records pin.
            # Contradictions (re-audits A, rounds 7 to 9):
            # - the invoice's day set, which speaks for every response of the
            #   day, and the PI's attestation, which names this one meta,
            #   ruling a served tier out are conflicts;
            # - a batch marker beside served-tier headers means a real-time
            #   part (a cleanup or retry) ran too, which is a mix, not a
            #   contradiction: a note, so a scan still finds it;
            # - a record of the tier REQUESTED yields silently.
            for other in [day_set] + [x for x in finding.evidence if x.kind == "attestation"]:
                outside = [t for t in e.tiers if other and t not in other.tiers]
                if outside:
                    finding.conflicts.append(f"applied-header-partial served "
                                             f"{'|'.join(outside)} but {other.describe()}")
            if any(x.kind in BATCH_KINDS for x in finding.evidence) and \
                    any(t != "batch" for t in e.tiers):
                finding.notes.append(f"{e.describe()} beside a batch marker: a real-time part "
                                     "(a cleanup or a retry) ran too")
            extra = [t for t in e.tiers if t not in finding.candidates]
            if not extra:
                continue
            widened = tuple(t for t in TIERS if t in set(finding.candidates) | set(extra))
            finding.notes.append(f"{e.describe()} widens {'|'.join(finding.candidates)} "
                                 f"(by {finding.method}) to {'|'.join(widened)}")
            finding.tier = widened[0] if len(widened) == 1 else None
            finding.method = "unresolved" if finding.tier is None else finding.method
            finding.candidates = widened
        finding.evidence = evidence
        return finding

    def _served_mixed(self, served: Evidence, evidence: list[Evidence],
                      notes: list[str]) -> TierFinding:
        """A fragment whose every response reported a tier, and they differ.

        Its candidates are exactly the served tiers: it ran at each of them,
        so its cost lies between their prices. A record of the tier REQUESTED
        that names one of them is a note; any other evidence excluding a
        served tier is a conflict, because the API's statement stands.
        """
        conflicts: list[str] = []
        for e in evidence:
            if e is served or e.kind == "applied-header-partial":
                continue
            outside = [t for t in served.tiers if t not in e.tiers]
            if not outside:
                continue
            if e.kind in REQUEST_RECORDS or e.kind == "cached-path":
                notes.append(f"{e.describe()} is the tier REQUESTED; the API served "
                             f"{'|'.join(served.tiers)}")
            else:
                conflicts.append(f"applied-header served {'|'.join(served.tiers)} but "
                                 f"{e.describe()}")
        return TierFinding(None, "unresolved", served.tiers, evidence, conflicts, notes)

    def _resolve_records(self, evidence: list[Evidence], conflicts: list[str],
                         notes: list[str]) -> TierFinding:
        """Pins first, by priority; else the intersection of the narrowing evidence."""
        pins = [e for e in evidence if e.pins and e.kind in PIN_PRIORITY]
        narrows = [e for e in evidence if e not in pins]
        if pins:
            chosen = min(pins, key=lambda e: PIN_PRIORITY.index(e.kind))
            tier = chosen.tiers[0]
            for e in pins:
                if e.tiers[0] == tier:
                    continue
                if chosen.kind == "cached-path" and e.kind in REQUEST_RECORDS:
                    notes.append(f"{e.describe()} is the tier REQUESTED; the cached path "
                                 "dropped it")
                elif chosen.kind == "applied-header" and e.kind in REQUEST_RECORDS:
                    notes.append(f"{e.describe()} is the tier REQUESTED; the API served "
                                 f"{tier}")
                elif e.kind in INHERITED_KINDS and chosen.kind not in INHERITED_KINDS:
                    notes.append(f"{e.describe()} overruled by the fragment's own {chosen.kind}")
                else:
                    conflicts.append(f"pins disagree: {chosen.describe()} vs {e.describe()}")
            for e in narrows:
                if tier not in e.tiers:
                    conflicts.append(f"{chosen.kind} pins {tier} but {e.describe()}")
            return TierFinding(tier, chosen.kind, (tier,), evidence, conflicts, notes)
        candidates = set(TIERS)
        for e in narrows:
            candidates &= set(e.tiers)
        if not candidates:
            conflicts.append("evidence excludes every tier: "
                             + "; ".join(e.describe() for e in narrows))
            candidates = set(TIERS)
        ordered = tuple(t for t in TIERS if t in candidates)
        if len(ordered) == 1:
            method = "+".join(sorted({e.kind for e in narrows if len(e.tiers) < len(TIERS)}))
            return TierFinding(ordered[0], method or "billing-day", ordered, evidence,
                               conflicts, notes)
        return TierFinding(None, "unresolved", ordered, evidence, conflicts, notes)

    # -- pricing -------------------------------------------------------------

    def cost_fragment(self, *, meta: dict[str, Any], meta_path: Path, run_id: str, pool: str,
                      run_dir: Path, model: str, stage: str = "proposer") -> dict[str, Any]:
        """Price one fragment (a primary meta or a recovery meta).

        Returns:
            A ``cost_source.fragments`` entry with private ``_cost``,
            ``_low``, ``_high`` and ``_basis`` keys the caller strips.
        """
        usage, usage_note = fragment_usage(meta)
        ts = meta.get("timestamp") or {}
        start, end = ts.get("start"), ts.get("end")
        entry: dict[str, Any] = {"meta": _rel(meta_path), "model_recorded": model,
                                 "priced_at": (end or start or "")[:10] or None}
        if usage_note:
            entry["usage_source"] = usage_note
        if not usage or is_unrecorded(usage):
            entry.update(tier=None, tier_method="not-needed: no usage recorded")
            return {**entry, "_basis": "unrecorded", "_cost": None, "_low": None, "_high": None}
        if not entry["priced_at"]:
            # price_usage(at=None) means "today", so an undated fragment would
            # re-price whenever the register is regenerated. Refuse instead.
            entry.update(tier=None, tier_method="not-needed",
                         unpriceable="no timestamp: the rate card row cannot be chosen")
            return {**entry, "_basis": "unpriceable", "_cost": None, "_low": None, "_high": None}
        try:
            canonical = resolve_model(model)
        except UnknownModelError as exc:
            entry.update(tier=None, tier_method="not-needed", unpriceable=str(exc))
            return {**entry, "_basis": "unpriceable", "_cost": None, "_low": None, "_high": None}
        entry["model"] = canonical
        served = served_tiers(meta)
        foreign = {t: n for t, n in (served[0] if served else {}).items()
                   if t not in TIERS and t != UNREPORTED and n}
        if foreign:
            # The API says it served these responses at a tier the rate card
            # does not price (re-audit A, L4): any card tier could understate.
            entry.update(tier=None, tier_method="not-needed", unpriceable=(
                "served at a tier the rate card does not price: "
                + ", ".join(f"{t} ({n} of {served[1]} responses)"
                            for t, n in sorted(foreign.items()))))
            return {**entry, "_basis": "unpriceable", "_cost": None, "_low": None, "_high": None}
        finding = self.resolve(
            meta=meta, meta_path=meta_path, run_id=run_id, pool=pool, run_dir=run_dir,
            model=canonical, start=start, end=end, duration_s=ts.get("duration_seconds"),
            output_tokens=int(usage.get("total_output_tokens") or 0)
            + int(usage.get("total_thoughts_tokens") or 0), stage=stage)
        prices: dict[str, float] = {}
        try:
            for tier in finding.candidates:
                block = price_usage(usage, model, tier, at=entry["priced_at"],
                                    tier_source=finding.method, card_path=self.card_path)
                prices[tier] = block["total_cost_usd"]
        except RateCardError as exc:
            entry.update(tier=None, tier_method=finding.method, unpriceable=str(exc))
            return {**entry, "_basis": "unpriceable", "_cost": None, "_low": None, "_high": None}
        low, high = min(prices.values()), max(prices.values())
        entry.update(tier=finding.tier, tier_method=finding.method,
                     evidence=[e.describe() for e in finding.evidence])
        if finding.conflicts:
            entry["conflicts"] = finding.conflicts
        if finding.notes:
            entry["notes"] = finding.notes
        if finding.tier is not None or high - low < INDIFFERENT_USD:
            if finding.tier is None:
                entry["tier_method"] = "tier-indifferent: " + "|".join(finding.candidates)
            entry["cost_usd"] = round(high, 6)
            return {**entry, "_basis": "audited", "_cost": high, "_low": high, "_high": high}
        entry["candidates"] = {t: round(p, 6) for t, p in prices.items()}
        entry["cost_usd"] = round(high, 6)
        return {**entry, "_basis": "audited-upper-bound", "_cost": high, "_low": low, "_high": high}

    def cost_pass(self, *, pass_id: str, fragments: list[tuple[dict[str, Any], Path]],
                  run_id: str, pool: str, run_dir: Path, model: str,
                  fragment_models: list[str] | None = None,
                  stage: str = "proposer") -> dict[str, Any]:
        """The register's ``cost_usd``, ``cost_basis`` and ``cost_source`` for a pass.

        Args:
            pass_id: The register key (``cost-overrides.json`` is keyed by it).
            fragments: ``(meta, meta_path)`` for the primary meta then each
                recovery fragment.
            run_id: The run id.
            pool: The pool (or verifier label).
            run_dir: The run directory.
            model: The row's authoritative ``model_used``.
            fragment_models: Per-fragment model overrides (a recovery that
                recorded its own model); defaults to ``model`` for each.
            stage: ``proposer`` or ``verifier``.

        Returns:
            The three register fields.
        """
        override = self.overrides.get(pass_id) or {}
        if override.get("basis") == "published":
            return {"cost_usd": override["cost_usd"], "cost_basis": "published",
                    "cost_source": {"published": override["source"],
                                    "rate_card": self.card_identity}}
        models = fragment_models or [model] * len(fragments)
        priced = [self.cost_fragment(meta=m, meta_path=p, run_id=run_id, pool=pool,
                                     run_dir=run_dir, model=fm, stage=stage)
                  for (m, p), fm in zip(fragments, models, strict=True)]
        bases = {f["_basis"] for f in priced}
        # Why the cited metas may cover only part of the pass's spend.
        partial_why = []
        if override.get("basis") == "audited-lower-bound":
            partial_why.append(override["source"])
        if "unrecorded" in bases and bases != {"unrecorded"}:
            partial_why.append("a fragment of this pass recorded no usage")
        carry_note = None
        if stage != "proposer" and fragments:
            cover = verifier_coverage(fragments)
            if cover and cover[0] < COVERAGE_FLOOR * cover[1]:
                carry = carry_explains(fragments, cover)
                if carry:
                    carry_note = (
                        f"the leg's metas account for {cover[0]:,} candidate(s) against "
                        f"{cover[1]:,} results in probabilities.json, but {carry[0]:,} of "
                        f"those results were carried forward from {carry[1]} "
                        "(carry_provenance.json) and are priced there: the metas are this "
                        "stage's whole spend")
                else:
                    partial_why.append(
                        f"the leg's metas account for {cover[0]:,} candidate(s) against "
                        f"{cover[1]:,} results in probabilities.json: a later leg (a cleanup) "
                        "overwrote the main meta")
        costed = [f for f in priced if f["_cost"] is not None]
        if bases == {"unrecorded"}:
            basis, cost = "unrecorded", None
        elif "unpriceable" in bases:
            basis, cost = "unpriceable", None  # part of the pass cannot be priced
        elif partial_why:
            # A floor: each priced fragment at its LOWEST candidate tier (a
            # pinned fragment has one price). Valid whatever the unresolved
            # tiers were, which a sum of highest candidates would not be.
            basis = "audited-lower-bound"
            cost = round(sum(f["_low"] for f in costed), 6)
        elif "audited-upper-bound" in bases:
            basis = "audited-upper-bound"
            cost = round(sum(f["_cost"] for f in costed), 6)
        else:
            basis = "audited"
            cost = round(sum(f["_cost"] for f in costed), 6)
        source: dict[str, Any] = {"rate_card": self.card_identity,
                                  "fragments": [{k: v for k, v in f.items()
                                                 if not k.startswith("_")} for f in priced]}
        if basis == "audited-upper-bound":
            source["bounds_usd"] = {"low": round(sum(f["_low"] for f in costed), 6),
                                    "high": round(sum(f["_high"] for f in costed), 6)}
        if basis == "unrecorded":
            source["note"] = "usage_stats recorded no tokens; null, not zero (PI ruling D12)"
        if basis == "audited-lower-bound":
            source["note"] = "LOWER bound: " + "; ".join(partial_why)
        elif carry_note:
            source["note"] = carry_note
        return {"cost_usd": cost, "cost_basis": basis, "cost_source": source}


__all__ = ["BASES", "BATCH_KINDS", "CARRY_SCHEMA", "COVERAGE_FLOOR", "Evidence",
           "INHERITED_KINDS", "PIN_PRIORITY", "PassCoster", "REQUEST_RECORDS", "TierFinding",
           "billed_cache_sizes", "cache_signature", "carried_forward", "carry_explains",
           "fragment_usage", "is_continuous", "pacific_days", "realtime_resume_only",
           "stage_exists", "verifier_coverage"]
