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
   ``batch-marker``          ``batch_api`` block in the meta, ``batch_jobs.json``
                             beside it, or ``probabilities.json`` ``mode: batch``
   ``runner-record``         a ``cost/2`` block (WP2 onwards) whose tier came
                             from the CLI or the Batch API path
   ``batch-path-pricing``    a ``discount_reason`` naming the Batch API (only
                             the batch path writes it)
   ``cached-path``           the run used an EXPLICIT context cache on the
                             real-time path, whose request config omits
                             ``service_tier``: billed at standard, whatever the
                             launch line asked for (see below)
   ``run-log``               the runner's ``Service tier: <tier>`` launch line in
                             the fragment's OWN directory
                             (``data/pricing/run-log-tiers.json``)
   ``launch-manifest``       ``service_tier`` in a ``launch_manifest.json``
   ``attestation``           the PI's dated attestation
                             (``data/pricing/tier-attestations.json``)
   ``run-log-inherited``     a launch line in an ENCLOSING directory: it
                             describes the run's launch, which a verifier leg
                             or a later batch rung beneath it need not share
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

**The cached-path defect.** ``scripts/4_detect_mounds_batch.py`` builds a
fresh ``GenerateContentConfig`` for requests that use an explicit context
cache (``--use-cache``) and does not copy ``service_tier`` into it (the
block dates from ``76a2cc719``, 2026-03-28; flex arrived on the main path
only, ``2a2cd81c7``, 2026-04-09). Such a run prints ``Service tier: flex``
at launch and is billed at standard. Found 2026-10-03 when the volume rule
showed ``h8-v2`` (35 passes, 23.25 M output tokens on 2026-04-15 Pacific,
every launch log reading flex) against 0.60 M flex output billed for the
whole day; the two runs whose logs record an explicit cache (``h8-v2`` and
``55maps-image-generalisation``) are the two that fall in the April
standard-tier window. A log directory recording an explicit cache therefore
pins standard for a real-time fragment beneath it, outranking the launch
line it sits beside.

A pass whose meta a cleanup leg overwrote is listed in
``data/pricing/cost-overrides.json``: with a published figure it carries
that figure (``published``, D13); without one, its remaining tokens are
priced and labelled ``audited-lower-bound``.

When the evidence leaves more than one tier possible, the pass is priced at
every candidate and published at the HIGHEST, with ``cost_basis:
"audited-upper-bound"`` and both bounds in ``cost_source``, so the register
never understates and moves only downward as evidence arrives (the PI's
choice, 2026-10-03). Candidates that price within half a cent of each other
are reported as ``audited``: the tier is unknown but the cost is not.

Usage::

    from scripts.lib_pass_cost import PassCoster
    coster = PassCoster()
    result = coster.cost_pass(fragments=[(meta, meta_path)], run_id=..., pool=...,
                              run_dir=..., model=row_model)
    row.update(result)          # cost_usd, cost_basis, cost_source

Created: 2026-10-03 (WP3 of the cost accounting plan)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass, field
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
PIN_PRIORITY = ("batch-marker", "runner-record", "batch-path-pricing", "cached-path",
                "run-log", "launch-manifest", "attestation", "run-log-inherited")

#: Evidence that records the tier a run ASKED for, not the one it was billed
#: at; the cached-path rule overrules these without calling it a conflict.
REQUEST_RECORDS = ("run-log", "run-log-inherited", "launch-manifest")

#: Where the cached call path drops ``service_tier`` (cited in evidence).
CACHED_PATH_CITE = ("scripts/4_detect_mounds_batch.py cached-call GenerateContentConfig "
                    "omits service_tier (since 76a2cc719)")

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
        self.log_dirs: dict[str, dict[str, Any]] = _read_json(logs_path)["directories"]
        self.attestations: list[dict[str, Any]] = _read_json(attestations_path)["attestations"]
        self.overrides: dict[str, dict[str, Any]] = _read_json(overrides_path)["entries"]
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

    def _log_evidence(self, directory: Path, run_dir: Path) -> list[Evidence]:
        """Tiers named by the nearest enclosing directory's own logs.

        The walk stops at the first directory (from the fragment's own, up to
        and including the run directory) whose logs carry a tier line. A
        directory naming two tiers yields set-valued evidence; the walk does
        NOT continue upward past it, because a parent's logs describe the run
        as a whole and the child is where the disagreement lives.
        """
        own, stop = directory.resolve(), run_dir.resolve()
        cur = own
        while True:
            entry = self.log_dirs.get(_rel(cur))
            if entry:
                logs = ", ".join(lg["path"].rsplit("/", 1)[-1] for lg in entry["logs"])
                kind = "run-log" if cur == own else "run-log-inherited"
                found = [Evidence(kind, tuple(entry["tiers"]), f"{_rel(cur)}/{{{logs}}}")]
                if entry.get("explicit_cache"):
                    found.append(Evidence("cached-path", ("standard",),
                                          f"{_rel(cur)} logs record an explicit context "
                                          f"cache; {CACHED_PATH_CITE}"))
                return found
            if cur == stop or cur == cur.parent or stop not in cur.parents:
                return []
            cur = cur.parent

    @staticmethod
    def _launch_manifest(directory: Path, run_dir: Path) -> Evidence | None:
        """``service_tier`` from the nearest ``launch_manifest.json`` up to the run."""
        cur, stop = directory.resolve(), run_dir.resolve()
        while True:
            lm = cur / "launch_manifest.json"
            if lm.exists():
                tier = _read_json(lm).get("service_tier")
                if tier in TIERS:
                    return Evidence("launch-manifest", (tier,), _rel(lm))
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
        if meta.get("batch_api"):
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
            # A WP2 writer records where its tier came from; only a CLI switch
            # or the Batch API path is a record of what ran.
            if source.startswith(("cli", "Batch API", "no --service-tier")):
                out.append(Evidence("runner-record", (pricing["tier"],),
                                    f"{_rel(meta_path)} cost/2 tier_source={source!r}"))
        # Only the batch path's own wording counts. The real-time CONSTANT reads
        # "Gemini real-time flex (50 % of list, as per Batch API)", so a
        # substring test for "batch api" would read every real-time pass of
        # 2026-08-18 to 2026-09-21 as batch (caught on its first run, 2026-10-03).
        reason = str(pricing.get("discount_reason") or "").strip().lower()
        if reason.startswith("google async batch api"):
            out.append(Evidence("batch-path-pricing", ("batch",),
                                f"{_rel(meta_path)} discount_reason names the Batch API"))
        logs = self._log_evidence(here, run_dir)
        if stage != "proposer" or any(e.kind == "batch-marker" for e in out):
            # The cached-path rule is about the detection runner's REAL-TIME
            # call; a verifier leg, or a batch leg, beneath a cached run's log
            # is not on that path.
            logs = [e for e in logs if e.kind != "cached-path"]
        out.extend(logs)
        lm = self._launch_manifest(here, run_dir)
        if lm:
            out.append(lm)
        return out

    def attestation(self, run_id: str, pool: str, days: list[str]) -> Evidence | None:
        """The PI's attestation covering this fragment, if any.

        An attestation matches on ``run_id``, a glob over ``pool``, and, when
        it lists ``pacific_days``, only a fragment whose every billing day is
        listed. Two matching attestations naming different tiers are an
        error in the file, not a conflict to report.
        """
        hits = []
        for att in self.attestations:
            if att["run_id"] != run_id or not fnmatch.fnmatchcase(pool, att["pool"]):
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
                if tiers:
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
        att = self.attestation(run_id, pool, days)
        if att:
            evidence.append(att)
        bill = self.billing_evidence(model, days,
                                     continuous=is_continuous(start, end, duration_s),
                                     output_tokens=output_tokens)
        if bill:
            evidence.append(bill)
        conflicts: list[str] = []
        notes: list[str] = []
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
                elif e.kind == "run-log-inherited":
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
        try:
            canonical = resolve_model(model)
        except UnknownModelError as exc:
            entry.update(tier=None, tier_method="not-needed", unpriceable=str(exc))
            return {**entry, "_basis": "unpriceable", "_cost": None, "_low": None, "_high": None}
        entry["model"] = canonical
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
        if bases == {"unrecorded"}:
            basis = "unrecorded"
        elif "unpriceable" in bases:
            basis = "unpriceable"
        elif "audited-upper-bound" in bases:
            basis = "audited-upper-bound"
        else:
            basis = "audited"
        costed = [f for f in priced if f["_cost"] is not None]
        cost = (None if basis in ("unrecorded", "unpriceable")
                else round(sum(f["_cost"] for f in costed), 6))
        source: dict[str, Any] = {"rate_card": self.card_identity,
                                  "fragments": [{k: v for k, v in f.items()
                                                 if not k.startswith("_")} for f in priced]}
        if basis == "audited-upper-bound":
            source["bounds_usd"] = {"low": round(sum(f["_low"] for f in costed), 6),
                                    "high": round(sum(f["_high"] for f in costed), 6)}
        if basis == "unrecorded":
            source["note"] = "usage_stats recorded no tokens; null, not zero (PI ruling D12)"
        if override.get("basis") == "audited-lower-bound" and cost is not None:
            # The cited metas price correctly but cover only part of the pass:
            # the figure is a floor, and is labelled so rather than "audited".
            basis = "audited-lower-bound"
            source["note"] = "LOWER bound: " + override["source"]
        return {"cost_usd": cost, "cost_basis": basis, "cost_source": source}


__all__ = ["BASES", "Evidence", "PassCoster", "TierFinding", "fragment_usage",
           "is_continuous", "pacific_days"]
