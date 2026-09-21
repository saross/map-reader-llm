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
page, reads the "Input price", "Output price" and "Context caching price"
rows as text, and collects every dollar amount on each row. The card's
standard, batch and flex rates for the class must all appear among those
amounts (``OK``). An amount on the row that the card does not carry, or a
card rate the row lacks, is ``CHANGED``; a section or row that cannot be
found is ``UNPARSED``. Both non-OK verdicts exit 1, because both need a
human to look: a silent parse failure would be the same defect as a silent
rate fallthrough.

The page is HTML with no machine-readable feed (capability scan,
``planning/cost-accounting-fix-plan-2026-09-21.md`` § 3.1), so the parse is
deliberately loose — membership of amounts on a labelled row — rather than a
column-position rule that a page redesign would silently break. Storage
rates are not checked (no run here is priced on them).

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
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_cost import load_rate_card, rate_row  # noqa: E402

PRICING_URL = "https://ai.google.dev/gemini-api/docs/pricing"

#: How the page names each card model in its section heading.
PAGE_NAMES: dict[str, str] = {
    "gemini-3-flash-preview": "Gemini 3 Flash Preview",
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


def page_text(raw_html: str) -> str:
    """The page as one line of plain text per block element."""
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw_html)
    text = re.sub(r"(?i)</(tr|p|h[1-6]|li|div|table)>", "\n", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    lines = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def model_section(text: str, page_name: str) -> str | None:
    """The text from a model's heading to the next model heading."""
    heads = [m for m in re.finditer(r"(?m)^Gemini [0-9][^\n]{0,60}$", text)]
    for i, m in enumerate(heads):
        if m.group(0).strip().lower().startswith(page_name.lower()):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            return text[m.start():end]
    return None


def amounts_on_row(section: str, label: str) -> set[float] | None:
    """Every dollar amount on the first row that starts with ``label``."""
    for line in section.splitlines():
        if line.lower().startswith(label.lower()):
            return {float(x.replace(",", "")) for x in _MONEY.findall(line)}
    return None


def compare(card: dict[str, Any], text: str, at: str | None = None) -> list[dict[str, Any]]:
    """One verdict per (model, class).

    Args:
        card: The parsed rate card.
        text: The pricing page as plain text.
        at: The date whose card row is compared; ``None`` means today.

    Returns:
        Dicts with ``model``, ``class``, ``expected`` (the card's rates by
        tier), ``found`` (amounts on the page row) and ``verdict``.
    """
    out: list[dict[str, Any]] = []
    for model in card["models"]:
        page_name = PAGE_NAMES.get(model)
        section = model_section(text, page_name) if page_name else None
        row = rate_row(model, at, card)
        for cls, label in ROW_LABELS.items():
            expected = {tier: row["rates"][tier][cls] for tier in card["tiers"]}
            found = amounts_on_row(section, label) if section else None
            if found is None:
                verdict = "UNPARSED"
            else:
                wanted = set(expected.values())
                verdict = "OK" if wanted <= found and found <= wanted else "CHANGED"
            out.append({"model": model, "class": cls, "expected": expected,
                        "found": sorted(found) if found is not None else None,
                        "verdict": verdict})
    return out


def report(results: list[dict[str, Any]], source: str) -> str:
    lines = [f"published-rate check against {source}"]
    for r in results:
        exp = ", ".join(f"{t} {v}" for t, v in r["expected"].items())
        lines.append(f"  {r['verdict']:<8} {r['model']:<24} {r['class']:<13} "
                     f"card: {exp}  page: {r['found']}")
    bad = [r for r in results if r["verdict"] != "OK"]
    if bad:
        lines.append(
            f"FLAG for the PI: {len(bad)} class(es) differ from or could not be read "
            "off the published page. Confirm the current rates in AI Studio or the "
            "Cloud Console before editing data/pricing/gemini-rate-card.json; this "
            "script never edits it.")
    else:
        lines.append("every card rate appears on its published row; nothing to confirm")
    return "\n".join(lines)


def fetch(url: str) -> str:
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
