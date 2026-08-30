"""Single import point for the llm-reproducibility matching-grade extractor.

The extractor is imported *in place* from its home repo (the established
convention; cf. the style-analyser) rather than vendored, so the AB+ pipeline
always uses the canonical, tested implementation. Importing it requires a
Python with PyMuPDF (``fitz``) available.

This module isolates the ``sys.path`` manipulation so the rest of the package
imports clean names::

    from ab_plus._extractor import PDFExtractor, normalise_for_matching

Re-exports
----------
PDFExtractor
    ``.extract_pages(pdf_path)`` -> ``[{page_index, text, section}]``.
normalise_for_matching
    The deterministic, idempotent canonical key for quote verification.
normalise_text_readable
    Same character cleanup but preserves paragraph structure — used for
    display-side cleanup of quotes before they reach prose.
"""

from __future__ import annotations

import sys

from .config import EXTRACTOR_DIR

if not EXTRACTOR_DIR.is_dir():
    raise ImportError(
        f"Extractor directory not found: {EXTRACTOR_DIR}. "
        "Set AB_PLUS_EXTRACTOR_DIR or check the llm-reproducibility checkout."
    )

# Prepend so the canonical extractor wins over any same-named module on the path.
_dir_str = str(EXTRACTOR_DIR)
if _dir_str not in sys.path:
    sys.path.insert(0, _dir_str)

try:  # noqa: E402 — import must follow the sys.path insert above
    from extract_pdf_text import PDFExtractor
    from pdf_cleaner import normalise_for_matching, normalise_text_readable
except ImportError as exc:  # pragma: no cover - environment-dependent
    raise ImportError(
        f"Could not import the extractor from {EXTRACTOR_DIR}. "
        "This package needs a Python with PyMuPDF, e.g. "
        "~/Code/write-like-me/.venv/bin/python. "
        f"Underlying error: {exc}"
    ) from exc

__all__ = ["PDFExtractor", "normalise_for_matching", "normalise_text_readable"]
