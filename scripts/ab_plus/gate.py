"""Pre-flight cache-quality gate for extracted page text.

The pilot (2026-08-30) found that 3 of 25 sources were rasterised
print-to-PDFs whose text layer was empty or consisted solely of a publisher
download watermark repeated on every page. An empty cache is caught by a
zero-length check; a watermark-only cache is not — it *looks* populated
(hundreds of characters per page) while carrying no article text. Both
signatures let a drafter start work on a source it cannot actually read.

This module classifies a page cache BEFORE any drafter launches, using three
cheap statistics: characters per page, the number of empty pages, and the
largest count of pages sharing byte-identical text (the watermark
signature). It never calls an LLM and never modifies the cache.

Usage (from the repo root)::

    PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli gate            # all cached
    PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli gate --citekey X

Exit status 2 if any source FAILs, so a shell driver can stop before
dispatching agents.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

MIN_CHARS_PER_PAGE: int = 1000
"""Below this, a cache is thin enough to be suspect. The three pilot
failures sat at 0, 0, and 387 characters per page; the thinnest genuine
cache in the 88-source tail (an accepted-manuscript bundle with image-only
figure pages) sat at 1,306."""


@dataclass(frozen=True)
class GateResult:
    """Outcome of gating one page cache."""

    citekey: str
    n_pages: int
    n_chars: int
    empty_pages: tuple[int, ...]
    max_identical: int
    verdict: str  # 'PASS' | 'WARN' | 'FAIL'
    reason: str

    @property
    def chars_per_page(self) -> float:
        """Mean characters per page (0 for an empty document)."""
        return self.n_chars / self.n_pages if self.n_pages else 0.0


def assess_cache(
    citekey: str,
    pages: list[dict],
    min_chars_per_page: int = MIN_CHARS_PER_PAGE,
) -> GateResult:
    """Classify a page cache as PASS, WARN, or FAIL.

    Rules, in order of precedence:

    * FAIL ``empty`` — no text on any page.
    * FAIL ``watermark-only`` — more than one page carries byte-identical
      text AND the cache is thin (below ``min_chars_per_page``). A genuine
      article never repeats a whole page verbatim; a download watermark
      stamped by the publisher does.
    * WARN ``thin`` — below ``min_chars_per_page`` without the watermark
      signature (a short paper with large figures, or a partial failure).
    * WARN ``empty-pages`` — some pages carry no text (image-only figure
      or plate pages); the cache is usable but the drafter must know.
    * PASS otherwise.

    Args:
        citekey: BibTeX citekey (carried through for reporting).
        pages: The cached page list ``[{page_index, text, section}]``.
        min_chars_per_page: Threshold separating thin from normal caches.

    Returns:
        A :class:`GateResult` with the verdict and the statistics behind it.
    """
    texts = [str(p.get("text", "")) for p in pages]
    stripped = [t.strip() for t in texts]
    n_pages = len(pages)
    n_chars = sum(len(t) for t in texts)
    empty = tuple(
        int(p.get("page_index", i)) for i, (p, t) in enumerate(zip(pages, stripped)) if not t
    )
    non_empty = [t for t in stripped if t]
    max_identical = max(Counter(non_empty).values()) if non_empty else 0
    cpp = n_chars / n_pages if n_pages else 0.0

    if n_chars == 0 or not non_empty:
        verdict, reason = "FAIL", "empty: no text on any page (rasterised PDF?)"
    elif max_identical > 1 and cpp < min_chars_per_page:
        verdict, reason = (
            "FAIL",
            f"watermark-only: {max_identical} pages byte-identical at "
            f"{cpp:.0f} chars/page (publisher download stamp; OCR repair required)",
        )
    elif cpp < min_chars_per_page:
        verdict, reason = "WARN", f"thin: {cpp:.0f} chars/page (< {min_chars_per_page})"
    elif empty:
        verdict, reason = (
            "WARN",
            f"empty-pages: {len(empty)} page(s) without text at indices "
            f"{list(empty)} (image-only figure pages?)",
        )
    else:
        verdict, reason = "PASS", ""

    return GateResult(
        citekey=citekey,
        n_pages=n_pages,
        n_chars=n_chars,
        empty_pages=empty,
        max_identical=max_identical,
        verdict=verdict,
        reason=reason,
    )


def format_table(results: list[GateResult]) -> str:
    """Render gate results as a fixed-width table, worst first."""
    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    rows = sorted(results, key=lambda r: (order[r.verdict], r.chars_per_page, r.citekey))
    lines = [f"{'verdict':<7} {'pages':>5} {'chars':>8} {'c/page':>7}  citekey  reason"]
    for r in rows:
        lines.append(
            f"{r.verdict:<7} {r.n_pages:>5} {r.n_chars:>8} {r.chars_per_page:>7.0f}  "
            f"{r.citekey}  {r.reason}"
        )
    counts = Counter(r.verdict for r in results)
    lines.append(
        f"-- {len(results)} caches: {counts.get('PASS', 0)} PASS, "
        f"{counts.get('WARN', 0)} WARN, {counts.get('FAIL', 0)} FAIL"
    )
    return "\n".join(lines)
