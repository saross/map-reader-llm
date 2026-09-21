#!/usr/bin/env python3
"""
Audited flex cost of a proposer leg, computed from committed pass metadata.

Why this script exists
----------------------
A run's own ``run.meta.json`` stamps a ``cost_estimate`` block, and for Gemini
3.7 that figure must not be used at a budget gate. It is wrong in three
compounding ways:

1. **Wrong rate card.** ``pricing_used`` records ``input_per_1m: 0.5,
   output_per_1m: 3.0`` — the *Gemini 3* rates — even when ``model`` is
   ``gemini-3.7-flash``, which lists at 0.75 / 3.75. A 1.5x understatement.
   ``reports/billing-reconciliation-2026-09-11.md`` section 3.2 identifies this
   same error as one of the two candidate origins of the discredited "billed at
   roughly 0.6x the token basis" expectation.
2. **Cache-blind.** Cached input is priced at the full input rate. On an
   image run at ~79 per cent cached this is the dominant error, and it
   overstates.
3. **Thinking omitted.** Gemini bills thinking tokens at the output rate; the
   meta's ``output_cost_usd`` counts only ``total_output_tokens``. An
   understatement.

Net effect on the Gemini 3.7 image Gold Standard (GS) run: the metas sum to
US$35.82 where the audited basis is US$22.50 — about 1.6x. A pass-1 stop rule
of "US$110 on the audited basis" would misfire if checked against the meta.

The audited basis is the rule in ``reports/token-load-audit-2026-06-12.md``
section 2: cache-aware, thinking-inclusive, at the service tier actually used.

Verification
------------
Run over the five committed GS 3.7 image passes and their recovery fragments,
this script returns **US$18.33 over 6,990 tile-passes = US$0.00262 per
tile-pass** on the rate card of record. The figure those documents carry,
US$22.5004 (US$0.00322), priced the 111.2 M cached tokens at the standard
cache-read rate on the belief that cache reads are tier-invariant; the
August 2026 invoice bills the 3.7 flex cache read at half that
(``reports/billing/gemini-spend-by-sku.csv``), and the rate card
(``data/pricing/gemini-rate-card.json``) now carries the invoiced rate. The
difference is exactly the cached tokens times the halved rate, US$4.17
(``planning/cost-accounting-fix-plan-2026-09-21.md`` section 1.1).

Usage
-----
    python scripts/audit_proposer_cost.py <pass-root> [<pass-root> ...]

where each ``<pass-root>`` holds ``run_*`` subdirectories, each containing one
``*.meta.json``. Recovery fragments (``run_2_recovery``, ``run_2_recovery_rd3``)
are included: they are ordinary fragments of their pass and their tokens were
ordinary tokens.

    # The GS leg, as verified above
    python scripts/audit_proposer_cost.py \
        outputs/gemini37-image-gs-2026-09-01/g384_ov192_g37img

    # A 55-map leg, at the pass-1 stop-rule gate
    python scripts/audit_proposer_cost.py \
        outputs/gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img

Which model a fragment is priced at
-----------------------------------
Each fragment is priced at **its own** recorded model —
``configuration.model`` in its ``*.meta.json``, the field the writer stamps
(e.g. ``"gemini-3-flash-preview"`` in
``outputs/gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img/run_1/
detections-detect_brief-text-image-3-flash-2026-09-16.meta.json``).

Until 2026-09-20 this script never read that field and priced everything at
a ``--model`` default of ``gemini-3.7-flash``. The Gemini 3 image pool under
``outputs/gemini3-image-55map-2026-09-16/`` therefore read **US$345.90**
where its own model's card gives **US$233.63** — 48 per cent high, on a
figure used at a budget gate. The row B post-run report
(``outputs/gemini3-image-55map-2026-09-16/post_run_report.md``) records the
correct 233.6295 and warns in its reproduction block that the run without
``--model`` reads 345.9024. Guessing a rate card is the very error this
script exists to correct (audit 2026-09-20, the proposer cost auditor).

A meta carrying no model is **refused** unless ``--model`` is passed, and
that override is logged when it is used. A ``--model`` that disagrees with
a meta's own recorded model warns, loudly, per model.

Options
-------
``--model``  rate card override. Used only for metas that record no model
             of their own; a meta that records one is always priced at it.
``--tier``   ``flex`` (default, half of list) or ``standard``.
``--json``   emit the breakdown as JSON instead of a table.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

#: Since 2026-09-21 the rate card is DATA — ``data/pricing/gemini-rate-card.json``,
#: read through ``scripts/lib_cost.py`` (PI ruling D18). This module's
#: earlier hand-typed card priced the Gemini 3.7 cache read at the standard
#: rate on every tier on the stated ground that cache reads are
#: tier-invariant; the invoices show that holds for Gemini 3 Flash (US$0.0500
#: per million at every tier) and not for 3.7 (US$0.0378 on flex, August
#: 2026), so the committed GS image figure of US$22.50 was a US$4.17
#: overstatement (18.33 on the invoice basis). ``RATE_CARDS`` survives as a
#: derived view — model to its current STANDARD rates — for the CLI's
#: "known models" message and for callers that only ask which models exist.
from scripts.lib_cost import (  # noqa: E402
    RateCardError as _CardError,
    UnknownModelError as _UnknownModel,
    load_rate_card,
    rates_for,
)


def _current_standard_rates() -> dict[str, dict[str, float]]:
    """Every card model at today's standard rates, USD per 1M."""
    card = load_rate_card()
    out: dict[str, dict[str, float]] = {}
    for model, entry in card["models"].items():
        names = [model, *entry.get("aliases", [])]
        try:
            r = rates_for(model, "standard")
        except _CardError:
            continue
        for name in names:
            out[name] = {"input": r["input_fresh"], "output": r["output"],
                         "cache": r["input_cached"]}
    return out


RATE_CARDS: dict[str, dict[str, float]] = _current_standard_rates()

#: The > 200K-token prompt tier of the 3.1 Pro card, recorded as a tripwire
#: only: no pass in this project approaches a 200K-token prompt (the largest
#: verifier crop prompt is about 8.5K tokens), so every price here is the
#: <= 200K tier. A future long-context pass would need a dated row for this
#: in ``data/pricing/gemini-rate-card.json``, keyed by prompt size.
LONG_PROMPT_RATE_CARDS: dict[str, dict[str, float]] = {
    "gemini-3.1-pro-preview": {"input": 4.00, "output": 18.00, "cache": 0.40},
}

TIER_DISCOUNT: dict[str, float] = {"flex": 0.5, "batch": 0.5, "standard": 1.0}


class RateCardError(KeyError):
    """Raised when no rate card is known for the requested model or date."""

    def __str__(self) -> str:  # KeyError would wrap the message in quotes
        return str(self.args[0]) if self.args else ""


def rates(model: str, tier: str, at: Any = None) -> dict[str, float]:
    """
    Effective per-token rates for a model at a service tier on a date.

    Args:
        model: Model identifier as the run recorded it, e.g. ``gemini-3.7-flash``.
        tier: ``standard``, ``flex`` or ``batch``.
        at: The usage date the rate card row is chosen for; ``None`` is today.
            Pass the pass's own timestamp: every headline Gemini rate doubles
            on 2027-01-01, so a 2026 leg audited in 2027 must not be priced at
            the later row.

    Returns:
        Per-token (not per-1M) rates keyed ``input``, ``output``, ``cache``,
        each already at the tier — including ``cache``, whose tier treatment
        is the card row's, not this function's.

    Raises:
        RateCardError: If the model has no rate card, the tier is unknown, or
            no row is valid on the date. Guessing a rate card is how the
            meta's own figure went wrong; fail instead.
    """
    try:
        r = rates_for(model, tier, at)
    except _UnknownModel as exc:
        raise RateCardError(
            f"no rate card for {model!r}; known: {sorted(load_rate_card()['models'])}"
        ) from exc
    except _CardError as exc:
        raise RateCardError(str(exc)) from exc
    return {
        "input": r["input_fresh"] / 1e6,
        "output": r["output"] / 1e6,
        "cache": r["input_cached"] / 1e6,
    }


def audited_cost(usage: dict[str, Any], rate: dict[str, float]) -> float:
    """
    Audited cost of one pass fragment, in USD.

    Applies the rule in ``reports/token-load-audit-2026-06-12.md`` section 2:
    fresh input at the input rate, cached input at the cache rate, and output
    **plus thinking** at the output rate.

    Args:
        usage: A fragment's ``usage_stats`` block.
        rate: Per-token rates from :func:`rates`.

    Returns:
        Cost in USD.
    """
    total_input = usage["total_input_tokens"]
    cached = usage.get("total_cached_tokens", 0)
    fresh = total_input - cached
    billed_output = (
        usage["total_output_tokens"] + usage.get("total_thoughts_tokens", 0)
    )
    return (
        fresh * rate["input"]
        + cached * rate["cache"]
        + billed_output * rate["output"]
    )


def fragment_model(meta: dict[str, Any]) -> str | None:
    """
    The model a pass fragment recorded for itself.

    The writer stamps it at ``configuration.model``; verified against
    ``outputs/gemini3-image-55map-2026-09-16/g384_ov192_55map_g3img/run_1/
    detections-detect_brief-text-image-3-flash-2026-09-16.meta.json``,
    which carries ``"model": "gemini-3-flash-preview"``. Note this is a
    different field from ``cost_estimate.pricing_used.model``, which is
    part of the figure this script exists to replace and is therefore not
    consulted.

    Args:
        meta: A parsed ``*.meta.json``.

    Returns:
        The recorded model id, or None when the meta records none.

    Examples:
        >>> fragment_model({"configuration": {"model": "gemini-3-flash"}})
        'gemini-3-flash'
    """
    configuration = meta.get("configuration") or {}
    model = configuration.get("model")
    return model or None


def read_fragments(root: str) -> list[dict[str, Any]]:
    """
    Summarise every ``run_*`` fragment under one pass root.

    Each fragment carries its own recorded model, so the caller can price
    it at its own rate card rather than at one default for the whole run
    (audit 2026-09-20: a 48 per cent overstatement on the Gemini 3 image
    pool).

    Args:
        root: Directory holding ``run_*`` subdirectories.

    Returns:
        One dict per fragment that has a meta file, in directory-sorted
        order. ``model`` is the fragment's recorded model, or None.
    """
    from scripts.normalise_pass_layout import select_pass_file

    out: list[dict[str, Any]] = []
    for name in sorted(d for d in os.listdir(root) if d.startswith("run_")):
        metas = sorted(Path(p) for p in glob.glob(os.path.join(root, name, "*.meta.json")))
        if not metas:
            continue
        # The pass's meta by rule, never by sort order: a chunked pass whose
        # chunks were never merged has no pass meta, and pricing chunk 0 as
        # the pass at a budget gate reports one seventh of the run with no
        # sign anything is wrong (audit lens A and B, 2026-09-19). Such a
        # directory stops the audit.
        try:
            chosen = select_pass_file(metas, ".meta.json", Path(root) / name)
        except (FileNotFoundError, ValueError) as exc:
            raise SystemExit(
                f"audit_proposer_cost: cannot price {Path(root) / name}: {exc}. "
                "Merge the chunks, or archive the superseded meta, then re-run."
            ) from exc
        with open(chosen) as fh:
            meta = json.load(fh)
        metas = [str(chosen)]
        usage = meta["usage_stats"]
        total_input = usage["total_input_tokens"]
        out.append(
            {
                "fragment": name,
                "meta": metas[0],
                "model": fragment_model(meta),
                # The pass's own end date selects the rate card row (the
                # card is dated: every Gemini rate doubles on 2027-01-01).
                "ended": ((meta.get("timestamp") or {}).get("end") or "")[:10] or None,
                "items": meta["execution_stats"]["items_processed"],
                "retries": meta["execution_stats"].get("retries_total"),
                "input_tokens": total_input,
                "cached_tokens": usage.get("total_cached_tokens", 0),
                "cache_share": usage.get("total_cached_tokens", 0)
                / max(total_input, 1),
                "usage": usage,
                "meta_cost_usd": meta.get("cost_estimate", {}).get(
                    "total_cost_usd"
                ),
            }
        )
    return out


def main() -> int:
    """Entry point. Returns a process exit status."""
    parser = argparse.ArgumentParser(
        description=(
            "Audited flex cost of a proposer leg. Use this at a budget gate, "
            "never the meta's own cost_estimate."
        ),
    )
    parser.add_argument(
        "roots",
        nargs="+",
        help="Directories holding run_* pass fragments",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Rate card override, for metas that record no model of their "
            "own. A meta that records a model is always priced at it, and "
            "a disagreement is warned about. Without this flag a meta "
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
    args = parser.parse_args()

    if args.model is not None and args.model not in RATE_CARDS:
        print(
            f"error: no rate card for {args.model!r}; "
            f"known: {sorted(RATE_CARDS)}",
            file=sys.stderr,
        )
        return 2

    fragments: list[dict[str, Any]] = []
    for root in args.roots:
        if not os.path.isdir(root):
            print(f"error: not a directory: {root}", file=sys.stderr)
            return 2
        fragments.extend(read_fragments(root))

    if not fragments:
        print("error: no run_* fragments with metadata found", file=sys.stderr)
        return 2

    # Price each fragment at ITS OWN recorded model. Pricing a pool at one
    # default is how the Gemini 3 image pool read US$345.90 against its own
    # card's US$233.63 (audit 2026-09-20).
    disagreed: set[str] = set()
    used_override = False
    rate_cache: dict[tuple[str, str | None], dict[str, float]] = {}
    for frag in fragments:
        model = frag["model"]
        if model is None:
            if args.model is None:
                print(
                    f"error: {frag['meta']} records no configuration.model "
                    f"and no --model was given. Guessing a rate card is the "
                    f"error this script exists to correct; pass --model "
                    f"explicitly if you know what this pass ran on.",
                    file=sys.stderr,
                )
                return 2
            model = args.model
            frag["model"] = model
            frag["model_source"] = "--model override"
            used_override = True
        else:
            frag["model_source"] = "meta configuration.model"
            if args.model is not None and args.model != model:
                disagreed.add(model)
        if (model, frag.get("ended")) not in rate_cache:
            try:
                rate_cache[(model, frag.get("ended"))] = rates(
                    model, args.tier, at=frag.get("ended"))
            except RateCardError as exc:
                print(f"error: {exc} (from {frag['meta']})", file=sys.stderr)
                return 2
        frag["audited_usd"] = audited_cost(frag["usage"], rate_cache[(model, frag.get("ended"))])
        del frag["usage"]

    if used_override:
        print(
            f"note: --model {args.model} used as the rate card for "
            f"{sum(1 for f in fragments if f['model_source'].startswith('--'))}"
            f" fragment(s) that record no model of their own",
            file=sys.stderr,
        )
    for model in sorted(disagreed):
        print(
            f"warning: --model {args.model} disagrees with the model "
            f"{model!r} recorded by "
            f"{sum(1 for f in fragments if f['model'] == model)} fragment(s); "
            f"those fragments are priced at {model!r}, which is what they "
            f"ran on. Drop --model unless you mean to override a pass that "
            f"records nothing.",
            file=sys.stderr,
        )

    total = sum(f["audited_usd"] for f in fragments)
    items = sum(f["items"] for f in fragments)
    meta_total = sum(f["meta_cost_usd"] or 0.0 for f in fragments)
    per_item = total / items if items else 0.0
    models = sorted({f["model"] for f in fragments})

    if args.as_json:
        print(
            json.dumps(
                {
                    "models": models,
                    "model_override": args.model,
                    "tier": args.tier,
                    "rate_cards_per_1m": {m: RATE_CARDS[m] for m in models},
                    "fragments": fragments,
                    "tile_passes": items,
                    "audited_usd": round(total, 4),
                    "audited_usd_per_tile_pass": round(per_item, 6),
                    "meta_cost_estimate_usd": round(meta_total, 4),
                },
                indent=2,
            )
        )
        return 0

    for (model, ended), rate in sorted(rate_cache.items(),
                                       key=lambda kv: (kv[0][0], kv[0][1] or "")):
        effective = {k: round(v * 1e6, 4) for k, v in rate.items()}
        print(
            f"rate card: {model} at {args.tier} on {ended or 'today'} — "
            f"effective USD/1M {effective} (the cache read's tier treatment "
            f"is the card row's)"
        )
    print()
    for frag in fragments:
        print(
            f"{frag['fragment']:26s} n={frag['items']:6d} "
            f"cache={frag['cache_share']:.3f} "
            f"model={frag['model']:24s} "
            f"audited=${frag['audited_usd']:9.4f}"
        )
    print("-" * 70)
    print(
        f"{'TOTAL':26s} n={items:6d} audited=${total:9.4f}  "
        f"${per_item:.5f}/tile-pass"
    )
    print(
        f"{'(meta cost_estimate)':26s} "
        f"${meta_total:9.4f}  — do NOT use at a gate"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
