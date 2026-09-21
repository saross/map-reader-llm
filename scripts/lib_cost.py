#!/usr/bin/env python3
"""
The project's one cost function: price Gemini token usage from the rate card.

Why this module exists
----------------------
Until 2026-09-21 the cost of a run was computed in at least six places with
three different answers: ``lib_llm_metadata.estimate_cost`` (no cache rate,
tier chosen at the call site, silent default for an unknown model), the two
cost auditors (a correct method on a hand-typed card that priced the 3.7
cache read at the wrong tier), and three merge routines that added dollars
instead of re-pricing tokens. The register copied the first of these and
published figures two and a half times the invoice on the image campaigns.
``planning/cost-accounting-fix-plan-2026-09-21.md`` is the diagnosis; PI
rulings D11 to D18 (``planning/pi-decisions-2026-09-20.md``) are the
contract this module implements:

1. **Three token classes, priced separately.** Fresh input is
   ``prompt_token_count`` minus ``cached_content_token_count`` (the API's
   prompt count INCLUDES the cached tokens); cache-read input; and output
   PLUS thinking, which Google bills at the output rate.
2. **One rate card as dated data**, ``data/pricing/gemini-rate-card.json``,
   keyed by model, tier and validity window, each row citing its published
   source and the invoice SKUs that confirm it. The card's version and hash
   are stamped into every priced block, so a figure re-derives later without
   this code.
3. **Raise on an unknown model.** There is no default row. A silent
   fallthrough is what priced Gemini 3.7 at Gemini 3 rates for five weeks.
4. **The tier is an argument, never a constant.** Callers pass the tier the
   run recorded (``standard``, ``flex`` or ``batch``) and say where it came
   from; the discount is a property of the card row, not of the call site.
5. **Null, not zero, when nothing was recorded.** A usage block whose
   totals are all zero and which reports no responses with usage prices to
   ``None`` with ``cost_basis: "unrecorded"``, never to a confident ``0.0``.
6. **Merges re-price summed tokens.** :func:`price_usage` is the only
   arithmetic; a merged block is the function applied to the merged usage.

The block this returns keeps the legacy keys (``input_cost_usd``,
``output_cost_usd``, ``total_cost_usd``, ``pricing_used.input_per_1m``,
``pricing_used.output_per_1m``, ``pricing_used.discount``) so existing
readers keep working, and adds the audited detail beside them under
``schema: "cost/2"``.

Usage::

    from scripts.lib_cost import price_usage
    block = price_usage(meta["usage_stats"], model="gemini-3.7-flash",
                        tier="flex", at="2026-09-13", tier_source="cli")

Created: 2026-09-21 (Session 157, WP1 of the cost accounting plan)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: The rate card of record (PI ruling D18).
DEFAULT_RATE_CARD = PROJECT_ROOT / "data" / "pricing" / "gemini-rate-card.json"

#: Service tiers the card prices. ``batch`` is the async Batch API; ``flex``
#: is real-time flex; ``standard`` is list price.
TIERS: tuple[str, ...] = ("standard", "flex", "batch")

#: The block schema this module writes. ``cost/1`` is what
#: ``lib_llm_metadata.estimate_cost`` wrote before 2026-09-21 (no cache
#: class, tier chosen at the call site).
SCHEMA = "cost/2"


class UnknownModelError(KeyError):
    """No entry in the rate card for the model, under any alias."""

    def __str__(self) -> str:  # KeyError would wrap the message in quotes
        return str(self.args[0]) if self.args else ""


class RateCardError(ValueError):
    """The card has no row for the model at the date, or the file is malformed."""


# ---------------------------------------------------------------------------
# The card.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=8)
def _load(path: str, stamp: tuple[int, int]) -> tuple[dict[str, Any], str]:
    """Parse the card once per (path, mtime, size) and hash its bytes.

    The stamp is part of the key, so a card edited while a process runs is
    re-read and its recorded ``sha256`` always matches the file on disk.
    """
    raw = Path(path).read_bytes()
    card = json.loads(raw.decode("utf-8"))
    for key in ("version", "models", "tiers"):
        if key not in card:
            raise RateCardError(f"{path}: rate card lacks {key!r}")
    return card, hashlib.sha256(raw).hexdigest()


def _stamp(path: Path) -> tuple[int, int]:
    st = path.stat()
    return (st.st_mtime_ns, st.st_size)


def load_rate_card(path: Path | str | None = None) -> dict[str, Any]:
    """The parsed rate card.

    Args:
        path: An alternative card, for tests. Defaults to
            :data:`DEFAULT_RATE_CARD`.

    Returns:
        The card as a dict (shared; do not mutate).
    """
    p = Path(path or DEFAULT_RATE_CARD)
    return _load(str(p), _stamp(p))[0]


def rate_card_identity(path: Path | str | None = None) -> dict[str, str]:
    """What a priced block records about the card it used.

    Returns:
        ``path`` (repository-relative where possible), ``version`` and the
        file's ``sha256``, so a figure can be re-derived against exactly
        the card that priced it.
    """
    p = Path(path or DEFAULT_RATE_CARD)
    card, digest = _load(str(p), _stamp(p))
    try:
        rel = str(p.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        # A card outside the repository (a test's tmp_path): record its
        # name only, never a machine-specific absolute path, in a block that
        # may be committed; the hash still identifies it.
        rel = f"external:{p.name}"
    return {"path": rel, "version": str(card["version"]), "sha256": digest}


def resolve_model(model: str, card: dict[str, Any] | None = None) -> str:
    """The card's canonical id for a recorded model string.

    A recorded string matches an entry by exact id or by one of its listed
    aliases, case-insensitively. Nothing else matches: a prefix or substring
    rule is how ``gemini-3-flash`` once selected a default that happened to
    be right and ``gemini-3.7-flash`` selected one that was wrong.

    Args:
        model: The model as the run recorded it (``configuration.model``).
        card: A parsed card; defaults to the card of record.

    Returns:
        The canonical id.

    Raises:
        UnknownModelError: When no entry or alias matches.
    """
    card = card or load_rate_card()
    wanted = (model or "").strip().lower()
    if not wanted:
        raise UnknownModelError("no model recorded; refusing to guess a rate card")
    for canonical, entry in card["models"].items():
        names = {canonical.lower(), *(a.lower() for a in entry.get("aliases", []))}
        if wanted in names:
            return canonical
    raise UnknownModelError(
        f"no rate card entry for {model!r}; known: {sorted(card['models'])}. "
        "Add a row with its published source and invoice confirmation rather "
        "than pricing at another model's rates.")


def _as_date(at: date | datetime | str | None) -> date:
    if at is None:
        return datetime.now(timezone.utc).date()
    if isinstance(at, datetime):
        return at.date()
    if isinstance(at, date):
        return at
    return date.fromisoformat(str(at)[:10])


def rate_row(model: str, at: date | datetime | str | None = None,
             card: dict[str, Any] | None = None) -> dict[str, Any]:
    """The card row in force for a model on a date.

    Args:
        model: Recorded model string (resolved through :func:`resolve_model`).
        at: The usage date; ``None`` means today (UTC).
        card: A parsed card; defaults to the card of record.

    Returns:
        The row dict (``valid_from``, ``valid_to``, ``rates``, ``source`` …)
        with ``canonical_model`` added.

    Raises:
        RateCardError: When no row's validity window contains the date.
    """
    card = card or load_rate_card()
    canonical = resolve_model(model, card)
    when = _as_date(at)
    for row in card["models"][canonical]["rows"]:
        start = date.fromisoformat(row["valid_from"])
        end = date.fromisoformat(row["valid_to"]) if row.get("valid_to") else None
        if start <= when and (end is None or when <= end):
            return {**row, "canonical_model": canonical}
    raise RateCardError(
        f"{canonical}: no rate card row is valid on {when.isoformat()} "
        f"(rows start {[r['valid_from'] for r in card['models'][canonical]['rows']]})")


def rates_for(model: str, tier: str, at: date | datetime | str | None = None,
              card: dict[str, Any] | None = None) -> dict[str, Any]:
    """Effective rates, USD per 1,000,000 tokens, for a model at a tier on a date.

    Args:
        model: Recorded model string.
        tier: One of :data:`TIERS`.
        at: Usage date; ``None`` means today.
        card: A parsed card; defaults to the card of record.

    Returns:
        ``{"input_fresh", "input_cached", "output", "cache_storage_per_1m_hour",
        "row"}`` where ``row`` is the card row used.

    Raises:
        RateCardError: On an unknown tier or a row lacking a class.
    """
    if tier not in TIERS:
        raise RateCardError(f"unknown service tier {tier!r}; expected one of {TIERS}")
    row = rate_row(model, at, card)
    try:
        tier_rates = row["rates"][tier]
        out = {cls: float(tier_rates[cls]) for cls in ("input_fresh", "input_cached", "output")}
    except KeyError as exc:
        raise RateCardError(
            f"{row['canonical_model']}: row from {row['valid_from']} lacks "
            f"{exc} for tier {tier!r}") from exc
    out["cache_storage_per_1m_hour"] = float(row.get("cache_storage_per_1m_hour") or 0.0)
    out["row"] = row
    return out


# ---------------------------------------------------------------------------
# Usage.
# ---------------------------------------------------------------------------


def _usage_dict(usage: Any) -> dict[str, Any]:
    """Accept an ``AggregatedUsage`` dataclass or a ``usage_stats`` dict."""
    if is_dataclass(usage) and not isinstance(usage, type):
        return asdict(usage)
    if isinstance(usage, dict):
        return usage
    raise TypeError(f"usage must be a usage_stats dict or AggregatedUsage, not {type(usage)}")


def token_classes(usage: Any) -> dict[str, int]:
    """Split a usage block into the three billed classes.

    Args:
        usage: ``usage_stats`` (or ``AggregatedUsage``) with the keys the
            trackers write: ``total_input_tokens`` (which includes cached),
            ``total_cached_tokens``, ``total_output_tokens``,
            ``total_thoughts_tokens``.

    Returns:
        ``{"input_fresh", "input_cached", "output", "thinking"}`` as ints.
        Cached tokens are clamped to the input total, so a malformed block
        cannot yield negative fresh input.
    """
    u = _usage_dict(usage)
    total_in = int(u.get("total_input_tokens") or 0)
    cached = min(int(u.get("total_cached_tokens") or 0), total_in)
    return {
        "input_fresh": total_in - cached,
        "input_cached": cached,
        "output": int(u.get("total_output_tokens") or 0),
        "thinking": int(u.get("total_thoughts_tokens") or 0),
    }


def is_unrecorded(usage: Any, n_responses_with_usage: int | None = None) -> bool:
    """Whether a usage block says nothing rather than saying zero.

    The early runners (2026-03 to 04) wrote ``usage_stats`` blocks of zeros
    for runs that plainly consumed tokens. A block whose every class is zero
    and that reports no responses with usage is *unrecorded*; a block that
    reports responses and still sums to zero is a genuine zero.

    Args:
        usage: The usage block.
        n_responses_with_usage: The ``usage_stats.n_responses_with_usage``
            count where the writer recorded one; ``None`` when it did not.
    """
    classes = token_classes(usage)
    if any(classes.values()):
        return False
    if n_responses_with_usage is None:
        u = _usage_dict(usage)
        n_responses_with_usage = u.get("n_responses_with_usage")
    return not n_responses_with_usage


# ---------------------------------------------------------------------------
# Pricing.
# ---------------------------------------------------------------------------


def price_tokens(classes: dict[str, int], model: str, tier: str,
                 at: date | datetime | str | None = None,
                 card: dict[str, Any] | None = None) -> dict[str, float]:
    """Price three token classes at a model's tier rates.

    Args:
        classes: From :func:`token_classes`.
        model: Recorded model string.
        tier: One of :data:`TIERS`.
        at: Usage date.
        card: A parsed card.

    Returns:
        ``{"input_fresh", "input_cached", "output", "total"}`` in USD, unrounded.
    """
    r = rates_for(model, tier, at, card)
    fresh = classes["input_fresh"] * r["input_fresh"] / 1e6
    cached = classes["input_cached"] * r["input_cached"] / 1e6
    out = (classes["output"] + classes["thinking"]) * r["output"] / 1e6
    return {"input_fresh": fresh, "input_cached": cached, "output": out,
            "total": fresh + cached + out}


def price_usage(usage: Any, model: str, tier: str, *,
                at: date | datetime | str | None = None,
                tier_source: str = "unspecified",
                n_responses_with_usage: int | None = None,
                card_path: Path | str | None = None) -> dict[str, Any]:
    """Price a usage block and return the ``cost_estimate`` block to record.

    Args:
        usage: ``usage_stats`` dict or ``AggregatedUsage``.
        model: The model the run recorded (``configuration.model``).
        tier: The service tier the run ran at: ``standard``, ``flex`` or
            ``batch``. Never a constant; the caller must know.
        at: The usage date the card row is chosen for. Runners pass the
            pass's end time; the back-fill passes the meta's timestamp.
            ``None`` means today, which is right only for a live run.
        tier_source: Where the tier came from, recorded verbatim so an
            auditor can see whether it was the CLI, the Batch API path, or
            an inference from side evidence (the back-fill).
        n_responses_with_usage: See :func:`is_unrecorded`.
        card_path: An alternative rate card, for tests.

    Returns:
        The block. When the usage is unrecorded, every cost is ``None`` and
        ``cost_basis`` is ``"unrecorded"``; otherwise ``cost_basis`` is
        ``"audited"`` and ``input_cost_usd + cached_input_cost_usd +
        output_cost_usd == total_cost_usd`` to the cent.

    Raises:
        UnknownModelError: For a model the card does not know.
        RateCardError: For an unknown tier or a date the card has no row for.
    """
    card = load_rate_card(card_path)
    classes = token_classes(usage)
    when = _as_date(at)
    r = rates_for(model, tier, when, card)
    row = r["row"]
    identity = rate_card_identity(card_path)
    list_rates = rates_for(model, "standard", when, card)
    unrecorded = is_unrecorded(usage, n_responses_with_usage)
    priced = None if unrecorded else price_tokens(classes, model, tier, when, card)
    listed = None if unrecorded else price_tokens(classes, model, "standard", when, card)
    # The discount a reader may multiply the list total by: the ratio of
    # the billed total to the standard-tier total, which is exact even when
    # a row discounts the cache read differently from fresh input (Gemini 3
    # Flash Preview halves input and output on flex but not the cache read).
    # With no tokens it is the fresh-input ratio, the tier's headline.
    if priced and listed and listed["total"]:
        discount = priced["total"] / listed["total"]
    else:
        discount = (r["input_fresh"] / list_rates["input_fresh"]
                    if list_rates["input_fresh"] else 1.0)

    def money(x: float | None) -> float | None:
        return None if x is None else round(x, 6)

    return {
        "schema": SCHEMA,
        "cost_basis": "unrecorded" if unrecorded else "audited",
        # Legacy keys, kept so existing readers keep working. ``input_cost_usd``
        # is now the FRESH input only; the cached class has its own key.
        "input_cost_usd": money(priced["input_fresh"] if priced else None),
        "cached_input_cost_usd": money(priced["input_cached"] if priced else None),
        "output_cost_usd": money(priced["output"] if priced else None),
        "total_cost_usd": money(priced["total"] if priced else None),
        # Standard-tier equivalents, so the tier discount is auditable.
        "list_input_cost_usd": money(listed["input_fresh"] + listed["input_cached"]
                                     if listed else None),
        "list_output_cost_usd": money(listed["output"] if listed else None),
        "list_total_cost_usd": money(listed["total"] if listed else None),
        "tokens_billed": classes,
        "pricing_used": {
            "model": row["canonical_model"],
            "model_recorded": model,
            "tier": tier,
            "tier_source": tier_source,
            "priced_at": when.isoformat(),
            "input_per_1m": r["input_fresh"],
            "cached_input_per_1m": r["input_cached"],
            "output_per_1m": r["output"],
            "thinking_tokens_billed_as_output": classes["thinking"],
            "discount": round(discount, 6),
            "discount_reason": f"{tier} tier, billed total over standard-tier total, "
                               f"from the rate card row valid from {row['valid_from']}",
            "rate_card": {**identity, "row_valid_from": row["valid_from"],
                          "row_valid_to": row.get("valid_to"),
                          "invoice_confirmed": bool(row.get("invoice_confirmations"))},
        },
    }


def reprice_block(block: dict[str, Any], usage: Any, *,
                  fallback_model: str | None = None,
                  fallback_tier: str | None = None,
                  card_path: Path | str | None = None) -> dict[str, Any]:
    """Re-price a block from (typically merged) usage using the block's own stamp.

    A merge sums tokens and calls this, never adds dollars. A ``cost/2``
    block carries its model, tier and pricing date, so the merged usage is
    priced at exactly the terms of the original. A legacy block (no
    ``schema`` or no tier in ``pricing_used``) is re-priced only when the
    caller supplies the model and tier; otherwise the caller must keep the
    legacy additive path and label it.

    Args:
        block: The existing ``cost_estimate`` block.
        usage: The merged usage.
        fallback_model: Model to use when the block records none.
        fallback_tier: Tier to use when the block records none.
        card_path: An alternative rate card, for tests.

    Returns:
        A fresh ``cost/2`` block.

    Raises:
        RateCardError: When neither the block nor the fallbacks name a tier.
    """
    pu = (block or {}).get("pricing_used") or {}
    model = pu.get("model_recorded") or pu.get("model") or fallback_model
    tier = pu.get("tier") or fallback_tier
    if not model or not tier:
        raise RateCardError(
            "cannot re-price: the block records no tier and no fallback was given")
    n = None
    u = _usage_dict(usage)
    if "n_responses_with_usage" in u:
        n = u.get("n_responses_with_usage")
    return price_usage(usage, model, tier, at=pu.get("priced_at"),
                       tier_source=pu.get("tier_source") or "merged",
                       n_responses_with_usage=n, card_path=card_path)


def unpriceable_block(usage: Any, model: str, tier: str, reason: str, *,
                      tier_source: str = "unspecified") -> dict[str, Any]:
    """The block a writer records when the card cannot price a finished run.

    A run on a model the card lacks must not lose its metadata at the last
    step (the API work is done, the tokens are counted), and must not be
    priced at another model's rates. The block keeps the token classes and
    the tier, names the reason, and carries every cost as ``None`` under
    ``cost_basis: "unpriceable"``; the back-fill prices it once the card
    gains the row.

    Args:
        usage: The usage block.
        model: The model as recorded.
        tier: The tier the run ran at.
        reason: The card's refusal, verbatim.
        tier_source: Where the tier came from.
    """
    return {
        "schema": SCHEMA,
        "cost_basis": "unpriceable",
        "reason": reason,
        "input_cost_usd": None, "cached_input_cost_usd": None,
        "output_cost_usd": None, "total_cost_usd": None,
        "list_input_cost_usd": None, "list_output_cost_usd": None,
        "list_total_cost_usd": None,
        "tokens_billed": token_classes(usage),
        "pricing_used": {"model": None, "model_recorded": model, "tier": tier,
                         "tier_source": tier_source, "priced_at": None,
                         "rate_card": rate_card_identity()},
    }


def fmt_usd(amount: float | None, unrecorded: str = "unrecorded") -> str:
    """``$1.2345`` for a priced amount; the word for a null one.

    Every consumer that prints a cost goes through this, because a
    ``cost/2`` block may carry ``None`` (PI ruling D12: null, not zero, where
    nothing was recorded) and ``f"${x:.4f}"`` raises on it.
    """
    return unrecorded if amount is None else f"${amount:.4f}"


def tier_from_cli(service_tier: str | None, *, batch: bool = False) -> tuple[str, str]:
    """The tier a runner prices at, and where it came from, in one place.

    Args:
        service_tier: The ``--service-tier`` value (``standard`` or ``flex``),
            or ``None`` when the switch was not given.
        batch: True on the Batch API path, which is its own tier whatever
            the switch says.

    Returns:
        ``(tier, tier_source)``. No switch means the standard tier: a run
        that did not ask for flex was not billed at flex.
    """
    if batch:
        return "batch", "Batch API path"
    if service_tier:
        if service_tier not in TIERS:
            raise RateCardError(f"unknown --service-tier {service_tier!r}; expected one of {TIERS}")
        return service_tier, "cli --service-tier"
    return "standard", "no --service-tier given: standard tier"


def _unpriceable(block: dict[str, Any] | None) -> bool:
    """Whether a block records tokens the card could not price (M2)."""
    return bool(block) and block.get("cost_basis") == "unpriceable"


def _priceable(block: dict[str, Any] | None) -> bool:
    """Whether a block carries any cost worth merging.

    ``{}``, ``None``, an ``unpriceable`` block and a block of nulls do not.
    Nor does a LEGACY block of zeros — the stub the batch patcher used to
    write — since it has no dollars to add and would otherwise drag an
    audited block down to the legacy additive path. (A legacy block that
    recorded a genuine zero-cost pass is therefore treated as recording
    nothing; a legacy zero implies zero tokens, so no dollar is lost, and a
    ``cost/2`` zero, which is a real zero, is kept.)
    """
    if _unpriceable(block):
        return False
    if not block:
        return False
    keys = ("total_cost_usd", "input_cost_usd", "output_cost_usd", "cached_input_cost_usd")
    values = [block.get(k) for k in keys if block.get(k) is not None]
    if not values:
        return False
    if block.get("schema") == SCHEMA:
        return True
    return any(v != 0 for v in values)


def _terms(block: dict[str, Any]) -> tuple[Any, Any, Any]:
    """What must agree for two audited blocks to be re-priced as one."""
    pu = block.get("pricing_used") or {}
    rc = pu.get("rate_card") or {}
    return (pu.get("model"), pu.get("tier"), rc.get("row_valid_from"))


def merge_cost_blocks(blocks: list[dict[str, Any] | None],
                      merged_usage: Any, *,
                      card_path: Path | str | None = None) -> dict[str, Any]:
    """The ``cost_estimate`` of several passes merged into one. Never adds dollars
    where it can re-price tokens.

    Cases, in order:

    0. Blocks that carry no cost at all (``{}``, ``None``, a stub of nulls)
       contribute nothing; if none is priceable the result is an
       ``unrecorded`` block with every cost ``None``.
    0a. Any part is ``unpriceable`` (tokens the card could not price): the
       merged pass is unpriceable too, with the priced parts' sum and the
       reasons kept beside the null.
    1. Every priceable block is ``cost/2`` on the SAME terms — model, tier
       and rate card row — and the merged usage is re-priced once at those
       terms. Exact whatever the cached share of each part. One priced
       ``cost/2`` block among empties is re-priced over the merged usage
       too, so tokens without a block are still counted.
    2. Every priceable block is ``cost/2`` but the terms differ (a cleanup on
       another model or tier, or a pass that crosses a rate card row such as
       the 2027-01-01 step): the audited totals are added field by field,
       ``cost_basis: "audited-summed"``, ``pricing_used`` names no single
       card and ``summed_from`` lists each part's terms and total.
    3. Any priceable block is legacy (no ``schema``): the pre-2026-09-21
       additive arithmetic over the legacy keys, ``cost_basis:
       "summed-legacy"``, so no reader mistakes it for an audited figure.

    Args:
        blocks: The passes' ``cost_estimate`` blocks, in pass order.
        merged_usage: The summed ``usage_stats`` of those passes.
        card_path: An alternative rate card, for tests.

    Returns:
        The merged block.
    """
    priceable = [b for b in blocks if _priceable(b)]
    unpriced = [b for b in blocks if _unpriceable(b)]
    u = _usage_dict(merged_usage) if merged_usage is not None else {}
    if unpriced:
        # Tokens were recorded that the card could not price: the merged
        # pass cannot be priced either, and must not pass as audited on the
        # strength of the parts that could be (a pass priced at half its
        # tokens is worse than no price). The priced parts' sum is kept
        # beside the reasons so the back-fill can finish the job once the
        # card gains the row.
        priced_total = [b.get("total_cost_usd") for b in priceable
                        if b.get("total_cost_usd") is not None]
        return {
            "schema": SCHEMA,
            "cost_basis": "unpriceable",
            "reason": "; ".join(sorted({str(b.get("reason")) for b in unpriced})),
            "input_cost_usd": None, "cached_input_cost_usd": None,
            "output_cost_usd": None, "total_cost_usd": None,
            "priced_parts_total_usd": round(sum(priced_total), 6) if priced_total else None,
            "unpriceable_parts": len(unpriced),
            "tokens_billed": token_classes(u) if u else None,
            "pricing_used": None,
        }
    if not priceable:
        return {"schema": SCHEMA, "cost_basis": "unrecorded",
                "input_cost_usd": None, "cached_input_cost_usd": None,
                "output_cost_usd": None, "total_cost_usd": None,
                "tokens_billed": token_classes(u) if u else None,
                "pricing_used": None}
    if len(priceable) == 1:
        # One priced block: re-price it over the MERGED usage, so a part
        # that recorded tokens but no block (an older chunk meta) is still
        # counted; a legacy block has no terms to re-price on and is copied.
        if priceable[0].get("schema") == SCHEMA and u:
            return reprice_block(priceable[0], u, card_path=card_path)
        return copy.deepcopy(priceable[0])
    all_v2 = all(b.get("schema") == SCHEMA for b in priceable)
    if all_v2 and len({_terms(b) for b in priceable}) == 1:
        return reprice_block(priceable[0], merged_usage, card_path=card_path)

    def total(key: str) -> float | None:
        vals = [b.get(key) for b in priceable if b.get(key) is not None]
        return round(sum(vals), 6) if vals else None

    if all_v2:
        return {
            "schema": SCHEMA,
            "cost_basis": "audited-summed",
            "input_cost_usd": total("input_cost_usd"),
            "cached_input_cost_usd": total("cached_input_cost_usd"),
            "output_cost_usd": total("output_cost_usd"),
            "total_cost_usd": total("total_cost_usd"),
            "list_total_cost_usd": total("list_total_cost_usd"),
            "pricing_used": {"model": None, "tier": None,
                             "note": "summed over passes on different terms; see summed_from"},
            "summed_from": [
                {"model": (b.get("pricing_used") or {}).get("model"),
                 "tier": (b.get("pricing_used") or {}).get("tier"),
                 "row_valid_from": ((b.get("pricing_used") or {}).get("rate_card") or {}
                                    ).get("row_valid_from"),
                 "priced_at": (b.get("pricing_used") or {}).get("priced_at"),
                 "total_cost_usd": b.get("total_cost_usd")}
                for b in priceable],
        }
    first_pu = copy.deepcopy(next((b.get("pricing_used") for b in priceable
                                   if b.get("pricing_used")), None))
    return {
        "cost_basis": "summed-legacy",
        "input_cost_usd": total("input_cost_usd"),
        "cached_input_cost_usd": total("cached_input_cost_usd"),
        "output_cost_usd": total("output_cost_usd"),
        "total_cost_usd": total("total_cost_usd"),
        "pricing_used": first_pu,
    }


__all__ = [
    "DEFAULT_RATE_CARD", "SCHEMA", "TIERS", "RateCardError", "UnknownModelError",
    "fmt_usd", "is_unrecorded", "load_rate_card", "merge_cost_blocks", "price_tokens",
    "price_usage", "rate_card_identity", "rate_row", "rates_for", "reprice_block",
    "resolve_model", "tier_from_cli", "token_classes", "unpriceable_block",
]
