"""AB+ pipeline — annotated-bibliography-plus generation for Paper B.

Takes a reference list plus downloaded full-text PDFs and produces, per source,
an annotated bibliography "+": a whole-paper summary, salience-ranked key points
each carrying a verbatim (deterministically-verified) quote and locator, a
faithful paraphrase, and a relevance annotation positioning the source in the
paper-in-progress.

Design (locked 2026-06-10): deterministic work in Python (resolve, extract,
quote-check, render); interpretive work in LLM agents (summary, paraphrase,
positioning, relevance, the independent verifier). The quote-check is the one
structural guarantee — code, not an LLM.

Public surface
--------------
resolve_collection
    citekey -> PDF, via Zotero (read-only).
extract_source / load_cached_pages
    PDF -> per-page text, cached.
check_entry / CheckReport
    Deterministic quote verification.
ENTRY_SCHEMA / validate_entry
    The AB+ entry data contract.
"""

from __future__ import annotations

from .checking import CheckReport, QuoteResult, QuoteStatus, check_entry, format_report
from .extraction import extract_source, load_cached_pages
from .schema import ENTRY_SCHEMA, iter_quotes, validate_entry
from .zotero import PdfRef, resolve_collection

__all__ = [
    "resolve_collection",
    "PdfRef",
    "extract_source",
    "load_cached_pages",
    "check_entry",
    "CheckReport",
    "QuoteResult",
    "QuoteStatus",
    "format_report",
    "ENTRY_SCHEMA",
    "validate_entry",
    "iter_quotes",
]
