"""Deterministic quote verification — the load-bearing atom of the pipeline.

This is the AB+ analogue of DOI-resolution in lit-scout: the one guarantee the
pipeline gives in *code*, not by asking an LLM. A quote is either present in the
source or it is not, decided by::

    normalise_for_matching(quote) in normalise_for_matching(page["text"])

For every quote the proposer emits we record three things:

* whether it matches anywhere in the document (catches fabrication / drift);
* which page(s) actually contain it (the *verified* locator);
* whether the proposer's claimed ``page_index`` agrees with that (catches a
  right-quote / wrong-page slip).

Nothing here calls an LLM. A ``NOT_FOUND`` is a hard failure: the quote does not
exist in the source as written and must not reach the deliverable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ._extractor import normalise_for_matching
from .schema import iter_quotes


class QuoteStatus(str, Enum):
    """Outcome of checking one quote against the source."""

    PASS = "PASS"
    """Quote found and the proposer's claimed page is among the matches."""
    LOCATOR_MISMATCH = "LOCATOR_MISMATCH"
    """Quote found, but not on the page the proposer claimed."""
    NOT_FOUND = "NOT_FOUND"
    """Quote not present anywhere in the source — fabricated or drifted."""


@dataclass
class QuoteResult:
    """Per-quote check outcome."""

    role: str           # 'key_point' | 'framing_hook'
    index: int          # position within its group
    quote: str          # the quote as proposed (untruncated)
    claimed_page: int | None
    verified_pages: list[int]
    status: QuoteStatus

    @property
    def quote_preview(self) -> str:
        """First 70 characters of the quote, for compact reporting."""
        return self.quote if len(self.quote) <= 70 else self.quote[:67] + "..."


@dataclass
class CheckReport:
    """Aggregate result of checking every quote in an entry."""

    citekey: str
    results: list[QuoteResult] = field(default_factory=list)

    @property
    def n_quotes(self) -> int:
        return len(self.results)

    @property
    def n_passed(self) -> int:
        return sum(1 for r in self.results if r.status is QuoteStatus.PASS)

    @property
    def failures(self) -> list[QuoteResult]:
        """Quotes that did not cleanly pass (NOT_FOUND or LOCATOR_MISMATCH)."""
        return [r for r in self.results if r.status is not QuoteStatus.PASS]

    @property
    def all_passed(self) -> bool:
        return self.n_quotes > 0 and not self.failures

    @property
    def has_fabrication(self) -> bool:
        """True if any quote is NOT_FOUND (the serious failure mode)."""
        return any(r.status is QuoteStatus.NOT_FOUND for r in self.results)


def _matching_pages(quote: str, pages: list[dict]) -> list[int]:
    """Return the page_indexes whose normalised text contains the quote.

    Both sides go through ``normalise_for_matching`` so the comparison is
    whitespace- and (mostly) hyphenation-insensitive.
    """
    needle = normalise_for_matching(quote)
    if not needle:
        return []
    hits: list[int] = []
    for page in pages:
        haystack = normalise_for_matching(page.get("text", ""))
        if needle in haystack:
            hits.append(page["page_index"])
    return hits


def check_entry(entry: dict, pages: list[dict]) -> CheckReport:
    """Verify every quote in an AB+ entry against the source pages.

    Args:
        entry: A parsed AB+ entry conforming to the schema.
        pages: The source's extracted pages (``{page_index, text, section}``).

    Returns:
        A :class:`CheckReport` with one :class:`QuoteResult` per quote (key
        points first, then the optional framing hook).
    """
    report = CheckReport(citekey=entry.get("citekey", "<unknown>"))
    for q in iter_quotes(entry):
        verified = _matching_pages(q["quote"], pages)
        claimed = q["page_index"]
        if not verified:
            status = QuoteStatus.NOT_FOUND
        elif claimed in verified:
            status = QuoteStatus.PASS
        else:
            status = QuoteStatus.LOCATOR_MISMATCH
        report.results.append(
            QuoteResult(
                role=q["role"],
                index=q["index"],
                quote=q["quote"],
                claimed_page=claimed,
                verified_pages=verified,
                status=status,
            )
        )
    return report


def format_report(report: CheckReport) -> str:
    """Render a human-readable one-line-per-quote check report."""
    lines = [
        f"Quote check for {report.citekey}: "
        f"{report.n_passed}/{report.n_quotes} passed"
        + ("  [FABRICATION DETECTED]" if report.has_fabrication else ""),
    ]
    for r in report.results:
        loc = (
            f"claimed p{r.claimed_page}, found {r.verified_pages}"
            if r.status is QuoteStatus.LOCATOR_MISMATCH
            else f"p{r.claimed_page}"
            if r.status is QuoteStatus.PASS
            else f"claimed p{r.claimed_page}, found nowhere"
        )
        lines.append(f"  [{r.status.value:16}] {r.role}[{r.index}] {loc}  “{r.quote_preview}”")
    return "\n".join(lines)


def check_overflow(overflow: dict, pages: list[dict]) -> CheckReport:
    """Byte-check every overflow item's quote exactly like a key-point quote.

    Added 2026-09-03: the overflow sidecar pairs each paraphrase with the
    verbatim span it rests on, so the same deterministic check that guards
    key points guards the appendix. Items are reported under the role
    ``overflow`` with their list index; an empty quote counts as NOT_FOUND.

    Args:
        overflow: The parsed sidecar (see ``schema.OVERFLOW_SCHEMA``).
        pages: The cached page list for the citekey.

    Returns:
        A :class:`CheckReport` over the overflow items only.
    """
    results: list[QuoteResult] = []
    for i, item in enumerate(overflow.get("items") or []):
        quote = str(item.get("quote", ""))
        claimed = item.get("page_index")
        found = _matching_pages(quote, pages) if quote.strip() else []
        if not found:
            status = QuoteStatus.NOT_FOUND
        elif claimed in found:
            status = QuoteStatus.PASS
        else:
            status = QuoteStatus.LOCATOR_MISMATCH
        results.append(
            QuoteResult(
                role="overflow",
                index=i,
                quote=quote,
                claimed_page=claimed,
                verified_pages=found,
                status=status,
            )
        )
    return CheckReport(citekey=str(overflow.get("citekey", "")), results=results)
