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
this script returns **US$22.5004 over 6,990 tile-passes = US$0.00322 per
tile-pass**, reproducing the figure in
``reports/gemini37-image-55map-costing-2026-09-10.md`` section "Arithmetic"
and in ``results/gemini37-image-gs-2026-09-01/findings.md``.

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

Options
-------
``--model``  rate card to price against (default ``gemini-3.7-flash``).
``--tier``   ``flex`` (default, half of list) or ``standard``.
``--json``   emit the breakdown as JSON instead of a table.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from typing import Any

#: List rate cards, USD per 1M tokens, read at source and recorded in
#: ``reports/token-load-audit-2026-06-12.md`` section 2 (Gemini 3) and
#: ``reports/billing-reconciliation-2026-09-11.md`` section 3.2 (3.7).
#: ``cache`` is the context-caching read rate, 10 per cent of list input. It is
#: **the same at every tier** — "Context caching $0.05 / 1M (text/image/video)
#: at all tiers" (token-load audit section 2) — so the tier discount below must
#: NOT be applied to it. Discounting the cache read is a 19 per cent
#: understatement on a cache-heavy image leg: it returns US$18.33 where the
#: committed GS figure is US$22.50.
RATE_CARDS: dict[str, dict[str, float]] = {
    "gemini-3-flash": {"input": 0.50, "output": 3.00, "cache": 0.05},
    "gemini-3-flash-preview": {"input": 0.50, "output": 3.00, "cache": 0.05},
    "gemini-3.7-flash": {"input": 0.75, "output": 3.75, "cache": 0.075},
}

#: Flex and batch both bill at half of list; standard bills at list.
TIER_DISCOUNT: dict[str, float] = {"flex": 0.5, "standard": 1.0}


class RateCardError(KeyError):
    """Raised when no rate card is known for the requested model."""


def rates(model: str, tier: str) -> dict[str, float]:
    """
    Effective per-token rates for a model at a service tier.

    Args:
        model: Model identifier, e.g. ``gemini-3.7-flash``.
        tier: ``flex`` or ``standard``.

    The tier discount applies to input and output only; the cache read rate is
    the same at every tier (see the note on :data:`RATE_CARDS`).

    Returns:
        Per-token (not per-1M) rates keyed ``input``, ``output``, ``cache``.

    Raises:
        RateCardError: If the model has no recorded rate card. Guessing a
            rate card is how the meta's own figure went wrong; fail instead.
    """
    if model not in RATE_CARDS:
        raise RateCardError(
            f"no rate card for {model!r}; known: {sorted(RATE_CARDS)}"
        )
    discount = TIER_DISCOUNT[tier]
    card = RATE_CARDS[model]
    return {
        "input": card["input"] * discount / 1e6,
        "output": card["output"] * discount / 1e6,
        "cache": card["cache"] / 1e6,
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


def read_fragments(root: str) -> list[dict[str, Any]]:
    """
    Summarise every ``run_*`` fragment under one pass root.

    Args:
        root: Directory holding ``run_*`` subdirectories.

    Returns:
        One dict per fragment that has a meta file, in directory-sorted order.
    """
    out: list[dict[str, Any]] = []
    for name in sorted(d for d in os.listdir(root) if d.startswith("run_")):
        metas = sorted(glob.glob(os.path.join(root, name, "*.meta.json")))
        if not metas:
            continue
        meta = json.load(open(metas[0]))
        usage = meta["usage_stats"]
        total_input = usage["total_input_tokens"]
        out.append(
            {
                "fragment": name,
                "meta": metas[0],
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
        default="gemini-3.7-flash",
        help="Rate card to price against (default: gemini-3.7-flash)",
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

    try:
        rate = rates(args.model, args.tier)
    except RateCardError as exc:
        print(f"error: {exc}", file=sys.stderr)
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

    for frag in fragments:
        frag["audited_usd"] = audited_cost(frag["usage"], rate)
        del frag["usage"]

    total = sum(f["audited_usd"] for f in fragments)
    items = sum(f["items"] for f in fragments)
    meta_total = sum(f["meta_cost_usd"] or 0.0 for f in fragments)
    per_item = total / items if items else 0.0

    if args.as_json:
        print(
            json.dumps(
                {
                    "model": args.model,
                    "tier": args.tier,
                    "rate_card_per_1m": RATE_CARDS[args.model],
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

    effective = {k: round(v * 1e6, 4) for k, v in rate.items()}
    print(
        f"rate card: {args.model} at {args.tier} — "
        f"effective USD/1M {effective} (cache undiscounted by tier)"
    )
    print()
    for frag in fragments:
        print(
            f"{frag['fragment']:26s} n={frag['items']:6d} "
            f"cache={frag['cache_share']:.3f} "
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
