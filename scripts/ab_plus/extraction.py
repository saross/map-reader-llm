"""Extract per-page text from a source PDF or HTML snapshot, with a JSON cache.

A thin, caching wrapper over the canonical extractor. ``extract_source`` runs
``PDFExtractor.extract_pages`` once per source and caches the result to
``_work/<citekey>.pages.json`` so the proposer and checker can both read the
same page text without re-running PyMuPDF (and so a run is reproducible without
the PDF present, as long as the cache exists).

HTML sources (Zotero webpage snapshots, added 2026-07-24) are extracted with a
stdlib tag-stripper into a single page dict — HTML has no page structure, and
the quote checker only needs the cache text to be exactly what the proposer
read, which a single self-consistent page satisfies.

The page text is copyrighted, so the cache lives under the gitignored
``_work/`` directory and is never committed.
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

from ._extractor import PDFExtractor
from .config import WORK_DIR


class _HTMLTextExtractor(HTMLParser):
    """Collect readable text from an HTML document, skipping script/style."""

    _SKIP = {"script", "style", "noscript", "template"}
    _BLOCK = {
        "p", "div", "br", "li", "tr", "td", "th", "dt", "dd", "caption",
        "figcaption", "h1", "h2", "h3", "h4", "h5", "h6",
        "blockquote", "section", "article", "header", "footer", "pre",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in self._SKIP:
            self._skip_depth += 1
        elif tag in self._BLOCK:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._skip_depth:
            self._skip_depth -= 1
        elif tag in self._BLOCK:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._chunks.append(data)

    def text(self) -> str:
        raw = "".join(self._chunks)
        # Collapse intra-line whitespace; keep paragraph breaks readable.
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in raw.splitlines()]
        out: list[str] = []
        for ln in lines:
            if ln:
                out.append(ln)
            elif out and out[-1] != "":
                out.append("")
        return "\n".join(out).strip()


def _extract_html_pages(html_path: Path) -> list[dict]:
    """Extract an HTML snapshot as a single-page cache entry.

    ``close()`` flushes html.parser's internal buffer — without it, trailing
    text after an unterminated entity or tag fragment in a truncated snapshot
    is silently dropped (/audit, 2026-07-24). Snapshots are read as UTF-8
    with replacement; a non-UTF-8 snapshot degrades visibly (U+FFFD) rather
    than crashing, and the cache stays self-consistent for the quote checker.
    """
    parser = _HTMLTextExtractor()
    parser.feed(html_path.read_text(encoding="utf-8", errors="replace"))
    parser.close()
    return [{"page_index": 0, "text": parser.text(), "section": "html-snapshot"}]

# A single extractor instance is reused across sources (it is stateless per call).
_EXTRACTOR = PDFExtractor()


def _cache_path(citekey: str) -> Path:
    """Return the page-cache path for a citekey."""
    return WORK_DIR / f"{citekey}.pages.json"


def extract_source(
    citekey: str,
    pdf_path: Path,
    force: bool = False,
) -> list[dict]:
    """Extract per-page text for one source, caching the result.

    Args:
        citekey: BibTeX citekey, used as the cache key.
        pdf_path: Path to the source PDF.
        force: Re-extract even if a cache file exists.

    Returns:
        A list of page dicts ``{page_index, text, section}`` exactly as the
        extractor produces them (``page_index`` authoritative, ``section``
        advisory).

    Raises:
        FileNotFoundError: If ``pdf_path`` does not exist.
    """
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Source file not found: {pdf_path}")

    cache = _cache_path(citekey)
    if cache.exists() and not force:
        return json.loads(cache.read_text(encoding="utf-8"))

    if pdf_path.suffix.lower() in {".html", ".htm", ".xhtml", ".shtml"}:
        pages = _extract_html_pages(pdf_path)
    else:
        pages = _EXTRACTOR.extract_pages(str(pdf_path))
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")
    return pages


def load_cached_pages(citekey: str) -> list[dict]:
    """Load previously-extracted pages for a citekey.

    Args:
        citekey: BibTeX citekey.

    Returns:
        The cached page list.

    Raises:
        FileNotFoundError: If no cache exists for this citekey.
    """
    cache = _cache_path(citekey)
    if not cache.exists():
        raise FileNotFoundError(
            f"No page cache for {citekey!r}. Run extraction first: "
            f"ab_plus extract --citekey {citekey}"
        )
    return json.loads(cache.read_text(encoding="utf-8"))
