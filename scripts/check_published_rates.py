#!/usr/bin/env python3
"""
Compare the rate card of record with Google's published Gemini pricing page.

PI ruling D18 as amended (2026-09-21): the pinned, invoice-validated rate
card (``data/pricing/gemini-rate-card.json``) is the authority for every
cost figure, AND it is checked against the rates Google publishes; a
difference raises a flag for the PI to confirm in AI Studio or the Cloud
Console before the card is edited. This script is that check. It never
edits the card.

What it does
------------
For every model on the card, it locates that model's section of the pricing
page (an exact heading match; banners such as "Gemini 3.8 Flash is now
available" are not headings), then within it each tier block (Standard,
Batch, Flex) and each class row ("Input price", "Output price (including
thinking tokens)", "Context caching price"). A row's amounts sit on their
own lines with a validity phrase — "$0.75 through December 31, 2026", "$1.50
starting January 1, 2027" — and the amount in force on the requested date
is compared with the card's rate for that date: ``OK`` when equal,
``CHANGED`` when both are read and differ, ``UNPARSED`` when the section,
tier or row cannot be read. Both non-OK verdicts exit 1, because both need
a human to look: a silent parse failure would be the same defect as a
silent rate fallthrough. Storage rates are not checked (no run here is
priced on them).

The page is HTML with no machine-readable feed (capability scan,
``planning/cost-accounting-fix-plan-2026-09-21.md`` § 3.1); the layout
this reads was retrieved 2026-09-21 and a text excerpt of it is the test
fixture ``tests/fixtures/pricing-page-2026-09-21.txt``.

Usage::

    python scripts/check_published_rates.py            # fetches the page
    python scripts/check_published_rates.py --html saved.html   # offline
    python scripts/check_published_rates.py --json

Exit status: 0 every class OK; 1 any CHANGED or UNPARSED; 2 fetch failure.
Zero API spend (a documentation page, not a model call).

Created: 2026-09-21 (Session 157, WP1 of the cost accounting plan)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_cost import RateCardError, load_rate_card, rate_row  # noqa: E402

PRICING_URL = "https://ai.google.dev/gemini-api/docs/pricing"

#: How the page names each card model in its section heading.
PAGE_NAMES: dict[str, str] = {
    "gemini-3-flash-preview": "Gemini 3 Flash Preview",
    "gemini-3.5-flash": "Gemini 3.5 Flash",
    "gemini-3.7-flash": "Gemini 3.7 Flash",
    "gemini-3.8-flash": "Gemini 3.8 Flash",
    "gemini-3.1-pro-preview": "Gemini 3.1 Pro Preview",
}

#: The row label on the page for each usage class.
ROW_LABELS: dict[str, str] = {
    "input_fresh": "Input price",
    "output": "Output price",
    "input_cached": "Context caching price",
}

_MONEY = re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)")
_THROUGH = re.compile(r"through ([A-Z][a-z]+ \d{1,2}, \d{4})")
_STARTING = re.compile(r"starting ([A-Z][a-z]+ \d{1,2}, \d{4})")
_MODEL_ID = re.compile(r"^gemini-[\w.\-]+")

#: The tier block headings inside a model section, as the page names them.
#: ``Priority`` is read so that its rows end the Flex block; it is not on
#: the card and is never compared.
PAGE_TIERS: dict[str, str] = {"Standard": "standard", "Batch": "batch", "Flex": "flex",
                              "Priority": "priority"}


def page_text(raw_html: str) -> str:
    """The page as one line of plain text per block element."""
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw_html)
    text = re.sub(r"(?i)</(tr|td|th|p|h[1-6]|li|div|table)>", "\n", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    # Tags only: a bare "<= 200k tokens" in the text is not a tag, and the
    # earlier ``<[^>]+>`` ate it together with everything up to the next
    # closing bracket.
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"</?[A-Za-z][^<>]*>", " ", text)
    text = html.unescape(text)
    lines = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def _is_heading(lines: list[str], i: int) -> bool:
    """Whether line ``i`` is a model section heading.

    A heading is a line beginning ``Gemini <version>`` whose next line is
    the model id (``gemini-3.7-flash``) or a tier block name — the page
    also prints banners such as "Gemini 3.8 Flash is now available. Try it
    out." followed by prose, which this rule rejects. Headings with
    parentheses or emoji ("Gemini 3.1 Flash Image (Nano Banana 2)") are
    headings all the same, which is why the rule reads the next line
    rather than the heading's own characters.
    """
    if not re.match(r"^Gemini \d", lines[i]) or i + 1 >= len(lines):
        return False
    nxt = lines[i + 1]
    # A banner reads like prose ("Gemini 3.8 Flash is now available. Try it
    # out.") and is never a heading, whatever follows it.
    if re.search(r"\b(is|are|now|try|available)\b", lines[i], re.I):
        return False
    # A heading is followed by the model id, or straight by a tier block
    # (the page's "Gemini 3.1 Pro ." line).
    return bool(_MODEL_ID.match(nxt)) or nxt in PAGE_TIERS


def model_section(text: str, page_name: str) -> str | None:
    """The text from a model's own heading line to the next model heading."""
    lines = text.splitlines()
    heads = [i for i in range(len(lines)) if _is_heading(lines, i)]
    for n, i in enumerate(heads):
        if lines[i].strip().rstrip(" .").lower() == page_name.lower():
            end = heads[n + 1] if n + 1 < len(heads) else len(lines)
            return "\n".join(lines[i:end]) + "\n"
    return None


def _date(s: str) -> date:
    return datetime.strptime(s, "%B %d, %Y").date()


def amount_valid_on(lines: list[str], at: date) -> float | None:
    """The one dollar amount among ``lines`` that is in force on ``at``.

    A line reads ``$X through <date>``, ``$X starting <date>`` or a bare
    ``$X`` (no validity qualifier, in force now). Storage-rate lines
    (``per hour``) are ignored. ``None`` when no line applies.
    """
    for line in lines:
        low = line.lower()
        if "per hour" in low or "storage" in low:
            continue
        # The >200K-token prompt tier and the audio input rate are separate
        # prices on the same row; no run here is priced on either.
        if re.search(r">\s*200k", low) or "(audio)" in low:
            continue
        m = _MONEY.search(line)
        if not m:
            continue
        amount = float(m.group(1).replace(",", ""))
        through, starting = _THROUGH.search(line), _STARTING.search(line)
        if through and at <= _date(through.group(1)):
            return amount
        if starting and at >= _date(starting.group(1)):
            return amount
        if not through and not starting:
            return amount
    return None


def published_rates(section: str, at: date) -> dict[str, dict[str, float | None]]:
    """``{tier: {class: amount}}`` read off one model section on a date.

    Each tier block starts with its heading line (``Standard``, ``Batch``,
    ``Flex``); within it each class row is its label line followed by the
    amount lines until the next label or the next tier. A tier or row the
    section lacks is absent from the result.
    """
    out: dict[str, dict[str, float | None]] = {}
    lines = section.splitlines()
    tier: str | None = None
    label: str | None = None
    pending: list[str] = []

    def flush() -> None:
        if tier and label:
            out.setdefault(tier, {})[label] = amount_valid_on(pending, at)

    for line in lines:
        if line in PAGE_TIERS:
            flush()
            tier, label, pending = PAGE_TIERS[line], None, []
            continue
        low = line.lower()
        hit = next((cls for cls, lab in ROW_LABELS.items() if low.startswith(lab.lower())), None)
        if hit and tier:
            flush()
            label, pending = hit, []
            continue
        if tier and label:
            if low.startswith(("grounding", "used to improve", "free tier", "paid tier")):
                flush()
                label, pending = None, []
            else:
                pending.append(line)
    flush()
    return out


def compare(card: dict[str, Any], text: str, at: str | None = None) -> list[dict[str, Any]]:
    """One verdict per (model, tier, class).

    Args:
        card: The parsed rate card.
        text: The pricing page as plain text.
        at: The date whose card row and whose published amount are compared;
            ``None`` means today.

    Returns:
        Dicts with ``model``, ``tier``, ``class``, ``card`` (the card's rate),
        ``page`` (the published amount in force on the date, or ``None``) and
        ``verdict``: ``OK`` (equal), ``CHANGED`` (both read, different),
        ``UNPARSED`` (the page's section, tier or row could not be read).
    """
    when = date.fromisoformat(at) if at else datetime.now(timezone.utc).date()
    out: list[dict[str, Any]] = []
    for model in card["models"]:
        page_name = PAGE_NAMES.get(model)
        section = model_section(text, page_name) if page_name else None
        published = published_rates(section, when) if section else {}
        try:
            row = rate_row(model, when, card)
        except RateCardError as exc:
            # No card row on the date: nothing to compare, which is still a
            # verdict for the PI rather than a traceback.
            for tier in card["tiers"]:
                for cls in ROW_LABELS:
                    out.append({"model": model, "tier": tier, "class": cls, "card": None,
                                "page": published.get(tier, {}).get(cls),
                                "verdict": "UNPARSED", "note": str(exc)})
            continue
        for tier in card["tiers"]:
            for cls in ROW_LABELS:
                expected = float(row["rates"][tier][cls])
                found = published.get(tier, {}).get(cls)
                if found is None:
                    verdict = "UNPARSED"
                else:
                    verdict = "OK" if abs(found - expected) < 1e-9 else "CHANGED"
                out.append({"model": model, "tier": tier, "class": cls,
                            "card": expected, "page": found, "verdict": verdict})
    return out


def report(results: list[dict[str, Any]], source: str) -> str:
    """The human-readable verdict list, ending with the flag or the all-clear."""
    lines = [f"published-rate check against {source}"]
    for r in results:
        lines.append(f"  {r['verdict']:<8} {r['model']:<24} {r['tier']:<9} {r['class']:<13} "
                     f"card {r['card']}  page {r['page']}")
    bad = [r for r in results if r["verdict"] != "OK"]
    if bad:
        lines.append(
            f"FLAG for the PI: {len(bad)} rate(s) differ from or could not be read "
            "off the published page. Confirm the current rates in AI Studio or the "
            "Cloud Console before editing data/pricing/gemini-rate-card.json; this "
            "script never edits it.")
    else:
        lines.append("every card rate equals its published amount; nothing to confirm")
    return "\n".join(lines)


def fetch(url: str) -> str:
    """The pricing page's HTML. A documentation fetch, not a model call."""
    req = urllib.request.Request(url, headers={"User-Agent": "map-reader-llm rate check"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        return resp.read().decode("utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 (all OK), 1 (flag for the PI) or 2 (fetch failed)."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--html", type=Path, help="a saved copy of the pricing page (offline)")
    ap.add_argument("--url", default=PRICING_URL)
    ap.add_argument("--at", default=None, help="date whose card row to compare (YYYY-MM-DD)")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args(argv)
    if args.html:
        raw, source = args.html.read_text(encoding="utf-8", errors="replace"), str(args.html)
    else:
        try:
            raw, source = fetch(args.url), args.url
        except Exception as exc:  # network failure is a fetch failure, not a rate change
            print(f"could not fetch {args.url}: {exc}", file=sys.stderr)
            return 2
    results = compare(load_rate_card(), page_text(raw), args.at)
    if args.as_json:
        print(json.dumps({"source": source, "results": results}, indent=2))
    else:
        print(report(results, source))
    return 0 if all(r["verdict"] == "OK" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
