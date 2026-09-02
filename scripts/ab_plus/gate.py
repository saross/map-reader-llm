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

Added 2026-09-03 (PI ruling after the 88-source tail): CONTENT heuristics for
the defect classes the statistics cannot see, because the text is present and
plausible. Each is a WARN with a named reason, never a FAIL — the cache is
usable, but the drafter and verifier dispatch must carry the caution:

* ``cover-sheet`` — page 0 is a repository or preprint-server cover sheet
  (UvA-DARE, ResearchGate, SocArXiv …), so the usual ``page_index N`` =
  printed p.(N+1) mapping is off by one.
* ``author-manuscript`` — an accepted-manuscript deposit (PMC, HHS Public
  Access), so page indices do not map to journal pagination at all.
* ``neighbour-contamination`` — the first or last page carries text from an
  adjacent article in the same issue: a sibling DOI (same journal prefix,
  different final segment) on those pages, or page 0 opening mid-sentence.
  The deterministic checker would pass a verbatim quote from the wrong
  article, so this is the class that most needs a human-readable flag.
* ``caption-only-table`` — a page carries a "Table N" caption but almost no
  digits, the IEEE Access signature where captions extract without bodies.
* ``sections-empty`` — every page's ``section`` field is blank, so section
  locators must be reconstructed from headings in the text.

Usage (from the repo root)::

    PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli gate            # all cached
    PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli gate --citekey X

Exit status 2 if any source FAILs, so a shell driver can stop before
dispatching agents.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

MIN_CHARS_PER_PAGE: int = 1000
"""Below this, a cache is thin enough to be suspect. The three pilot
failures sat at 0, 0, and 387 characters per page; the thinnest genuine
cache in the 88-source tail (an accepted-manuscript bundle with image-only
figure pages) sat at 1,306."""


COVER_SHEET_SIGNATURES: tuple[str, ...] = (
    "UvA-DARE",
    "Digital Academic Repository",
    "See discussions, stats, and author profiles for this publication",
    "researchgate.net/publication",
    "Citation for published version",
    "This is a repository copy",
    "Link to publication",
    "osf.io/preprints",
    "SocArXiv",
)
"""Phrases that mark a repository or preprint-server cover sheet on page 0.
Drawn from the tail corpus: UvA-DARE (Crüwell 2021, Sarafoglou 2022/2023),
ResearchGate (Ross 2022). Matched case-sensitively on the first page only."""

AUTHOR_MANUSCRIPT_SIGNATURES: tuple[str, ...] = (
    "Author manuscript",
    "HHS Public Access",
    "PMC Author Manuscript",
    "NIH Public Access",
    "available in PMC",
)
"""Phrases that mark an accepted-manuscript deposit whose pagination is not
the journal's (Willroth 2022 via PubMed Central)."""

MAX_COVER_SHEET_CHARS: int = 2500
"""A cover sheet is short; a genuine first page with a signature phrase in
running text (a paper ABOUT repositories) is not, so the page-length cap keeps
the heuristic specific."""

MAX_NUMBERS_ON_POOR_PAGE: int = 40
"""The conservative caption rule only looks at pages with fewer numeric
tokens than this; a page dense with numbers has its tables somewhere."""

CAPTION_WINDOW: int = 600
MIN_NUMBERS_NEAR_TABLE: int = 4
"""A caption describing numeric content (results, accuracy, IoU …) with fewer
than this many numeric tokens in the window on EITHER side has lost its
body. Text-only tables (taxonomies, templates) are exempt by the wording
test, so the rule stays specific to the numeric tables a drafter would cite."""

_NUMERIC_TABLE_WORDS_RE = re.compile(
    r"result|accurac|precision|recall|f1|iou|performance|comparison|score|"
    r"statistic|error|rate|mean|count|number|percent|%",
    re.IGNORECASE,
)
_NUMBER_TOKEN_RE = re.compile(r"(?<![A-Za-z])\d+(?:[.,]\d+)?%?(?![A-Za-z])")

MAX_DOIS_ON_EDGE_PAGE: int = 3
"""A first or last page with more DOIs than this is a reference list, where
same-journal DOIs are citations rather than neighbours."""

MIN_MID_SENTENCE_LINE: int = 50
"""The mid-sentence rule needs a first line this long: journal logos ("remote
sensing") and preprint stamps are short lowercase lines on genuine first
pages."""

MIN_TRAILING_CHARS: int = 600
"""Non-boilerplate text after the last reference entry on the last page long
enough to be more than a footer: an appendix, author biographies (IEEE), or
an adjacent article's opening (MacCoun 2015's Nature neighbour runs ~650
characters). A weak, honestly labelled signal — most hits are appendices."""

IEEE_ACCESS_SIGNATURES: tuple[str, ...] = ("IEEE Access", "IEEEAccess")
"""Both IEEE Access sources in the tail corpus extracted every table as a
caption without a body (Can 2021, Uhl 2020); the text statistics cannot see
it, so the publisher itself is the trigger."""

_BOILERPLATE_RE = re.compile(
    r"downloaded from|copyright|©|terms of (service|use)|permissions|issn|reprints|"
    r"all rights reserved|creative commons|licens",
    re.IGNORECASE,
)
_REFERENCE_ENTRY_RE = re.compile(r"(?m)^\s*(?:\d{1,3}\.|\[\d{1,3}\])\s+\S")

_DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>)]+")
_TABLE_CAPTION_RE = re.compile(r"\b(?:TABLE|Table)\s+(?:[IVX]+|\d+)\s*[.:|]")


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
    notes: tuple[str, ...] = field(default_factory=tuple)
    """Content-heuristic warnings (2026-09-03), each ``<class>: <detail>``."""

    @property
    def chars_per_page(self) -> float:
        """Mean characters per page (0 for an empty document)."""
        return self.n_chars / self.n_pages if self.n_pages else 0.0


def _clean_doi(doi: str) -> str:
    """Lower-case a DOI and strip trailing punctuation or glued text."""
    doi = doi.strip().lower().rstrip(".,;:)⟩]")
    return re.sub(r"[a-z]+$", "", doi) if re.search(r"\d[a-z]{4,}$", doi) else doi


def _doi_stem(doi: str) -> str | None:
    """The DOI minus its final segment, or None when the suffix has no segments.

    Sibling articles in one issue share a stem: ``10.1016/j.tics.2019.07.009``
    and ``…07.010`` (Nosek 2019 and its TICS neighbour). Elsevier, Wiley, and
    Cambridge DOIs carry an issue-level stem; Science, Nature, and opaque
    Cambridge/Springer identifiers do not, so this signal is
    publisher-dependent by construction and returns None for those.
    """
    doi = _clean_doi(doi)
    prefix, _, suffix = doi.partition("/")
    cut = max(suffix.rfind("."), suffix.rfind("/"), suffix.rfind("_"))
    if cut <= 0:
        return None
    return f"{prefix}/{suffix[:cut]}"


def _text_after_references(last_page: str) -> int:
    """Characters of non-boilerplate text after the last reference entry.

    Returns 0 when the page carries no numbered reference entry, so the
    signal only fires for articles whose reference list ends on the last
    page (the common case for a journal issue's shared pages).
    """
    matches = list(_REFERENCE_ENTRY_RE.finditer(last_page))
    if not matches:
        return 0
    tail = last_page[matches[-1].end():]
    # Drop the final reference entry's own line; a wrapped continuation line
    # or two may survive, which the caller's threshold absorbs.
    lines = tail.splitlines()[1:]
    kept = [ln for ln in lines if ln.strip() and not _BOILERPLATE_RE.search(ln)]
    return sum(len(ln) for ln in kept)


def content_notes(pages: list[dict], source_doi: str | None = None) -> list[str]:
    """Run the content heuristics over a cache and return WARN notes.

    Pure and deterministic; each note reads ``<class>: <detail>`` and is
    meant to be pasted into the drafter's and verifier's dispatch messages.

    Args:
        pages: The cached page list ``[{page_index, text, section}]``.
        source_doi: The source's own DOI from the bibliography, if known.
            With it, any DOI on the first or last page sharing its stem but
            differing in the final segment is a neighbour; without it, two
            stem-sharing DOIs on those pages are reported instead.

    Returns:
        A list of note strings, possibly empty.
    """
    notes: list[str] = []
    if not pages:
        return notes
    texts = [str(p.get("text", "")) for p in pages]
    first, last = texts[0], texts[-1]

    # --- cover sheet / author manuscript on page 0 ---------------------------
    if len(first) <= MAX_COVER_SHEET_CHARS:
        hits = [s for s in COVER_SHEET_SIGNATURES if s in first]
        if hits:
            notes.append(
                f"cover-sheet: page 0 is a repository/preprint cover sheet ({hits[0]!r}); "
                "page_index N = printed p.N, not p.(N+1) — confirm against running heads"
            )
    ms_hits = [s for s in AUTHOR_MANUSCRIPT_SIGNATURES if s in first]
    if ms_hits:
        notes.append(
            f"author-manuscript: page 0 carries {ms_hits[0]!r}; page indices map to the "
            "deposited manuscript, not to journal pagination"
        )

    # --- neighbouring-article contamination ----------------------------------
    # A sibling DOI is only evidence on a page with FEW DOIs: a reference list
    # cites the same journal freely (Trier 2019's last page carries three
    # Archaeological Prospection DOIs, all citations).
    own = _clean_doi(source_doi) if source_doi else None
    own_stem = _doi_stem(own) if own else None
    for label, txt in (("first", first), ("last", last)):
        page_dois = sorted({_clean_doi(d) for d in _DOI_RE.findall(txt)})
        if len(page_dois) > MAX_DOIS_ON_EDGE_PAGE:
            continue
        if own_stem:
            siblings = [d for d in page_dois if d != own and _doi_stem(d) == own_stem]
        else:
            stems = Counter(s for s in (_doi_stem(d) for d in page_dois) if s)
            siblings = [d for d in page_dois if stems.get(_doi_stem(d) or "", 0) > 1]
        if siblings:
            notes.append(
                f"neighbour-contamination: sibling DOI(s) {siblings} on the {label} page"
                + (f" beside the source's {own}" if own else "")
                + " — an adjacent article shares the page; attribute quotes from it by "
                "reading, not by string match"
            )
    first_line = first.lstrip().split("\n", 1)[0].strip()
    if (
        len(first_line) >= MIN_MID_SENTENCE_LINE
        and first_line[0].islower()
        and ". " in first_line  # a continuation that finishes a sentence
        and not first_line.lower().startswith("arxiv")
    ):
        notes.append(
            "neighbour-contamination: page 0 opens mid-sentence "
            f"({first_line[:40]!r}…) — the tail of the preceding article is on this page"
        )
    trailing = _text_after_references(last)
    if trailing >= MIN_TRAILING_CHARS:
        notes.append(
            f"trailing-text: {trailing} chars of non-boilerplate text follow the last "
            "reference entry on the last page — an appendix, author biographies, or the "
            "next article's opening; attribute anything quoted from there by reading"
        )

    # --- caption-only tables ---------------------------------------------------
    # Calibrated 2026-09-03 across all 113 caches: no text statistic separates
    # a caption whose body is missing from a caption whose body sits elsewhere
    # on the page (adjacent-caption and digit-density rules each flagged a
    # third of the corpus). Two signals survive: the publisher, and a
    # conservative numeric rule that fires only on number-poor pages.
    if any(s in first for s in IEEE_ACCESS_SIGNATURES):
        notes.append(
            "caption-only-table: IEEE Access source — both such sources in the 2026-09 "
            "corpus extracted every table as a caption without a body; render the page "
            "before citing any table number"
        )
    flagged: list[int] = []
    for i, txt in enumerate(texts):
        if not txt.strip() or len(_NUMBER_TOKEN_RE.findall(txt)) >= MAX_NUMBERS_ON_POOR_PAGE:
            continue
        for m in _TABLE_CAPTION_RE.finditer(txt):
            caption = txt[m.end(): m.end() + 200]
            if not _NUMERIC_TABLE_WORDS_RE.search(caption):
                continue
            before = txt[max(0, m.start() - CAPTION_WINDOW): m.start()]
            after = txt[m.end() + len(caption.split(".")[0]): m.end() + CAPTION_WINDOW]
            if (
                len(_NUMBER_TOKEN_RE.findall(before)) < MIN_NUMBERS_NEAR_TABLE
                and len(_NUMBER_TOKEN_RE.findall(after)) < MIN_NUMBERS_NEAR_TABLE
            ):
                flagged.append(int(pages[i].get("page_index", i)))
                break
    if flagged:
        notes.append(
            f"caption-only-table: page(s) {flagged} carry a numeric-results caption on a "
            "number-poor page — the body may be unextracted; read the rendered page before "
            "citing a table number (low-recall signal)"
        )

    # --- section field ---------------------------------------------------------
    if all(not str(p.get("section", "")).strip() for p in pages):
        notes.append(
            "sections-empty: no page carries a section label; reconstruct locators from "
            "headings in the text"
        )
    return notes


def assess_cache(
    citekey: str,
    pages: list[dict],
    min_chars_per_page: int = MIN_CHARS_PER_PAGE,
    source_doi: str | None = None,
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
    * WARN ``content`` — one or more :func:`content_notes` fired (cover
      sheet, author manuscript, neighbour contamination, caption-only
      table, empty sections); the notes travel in ``GateResult.notes``.
    * PASS otherwise.

    Args:
        citekey: BibTeX citekey (carried through for reporting).
        pages: The cached page list ``[{page_index, text, section}]``.
        min_chars_per_page: Threshold separating thin from normal caches.
        source_doi: The source's DOI, if known, for the sibling-DOI check.

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

    notes = tuple(content_notes(pages, source_doi)) if verdict != "FAIL" else ()
    if verdict == "PASS" and notes:
        verdict = "WARN"
        reason = "content: " + "; ".join(n.split(":", 1)[0] for n in notes)
    elif verdict == "WARN" and notes:
        reason += " | content: " + "; ".join(n.split(":", 1)[0] for n in notes)

    return GateResult(
        citekey=citekey,
        n_pages=n_pages,
        n_chars=n_chars,
        empty_pages=empty,
        max_identical=max_identical,
        verdict=verdict,
        reason=reason,
        notes=notes,
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
        for note in r.notes:
            lines.append(f"        · {note}")
    counts = Counter(r.verdict for r in results)
    lines.append(
        f"-- {len(results)} caches: {counts.get('PASS', 0)} PASS, "
        f"{counts.get('WARN', 0)} WARN, {counts.get('FAIL', 0)} FAIL"
    )
    return "\n".join(lines)
