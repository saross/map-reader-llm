"""Centralised paths and constants for the AB+ pipeline.

Vendored 2026-08-30 from the paper-b repository (2026-mq-llm-dh-judgement-paper-b,
Apache-2.0) per planning/ab-plus-run-card-2026-08-30.md; paths repointed to
this repository (map-reader-llm) and the TRAP collection.

All filesystem locations the pipeline depends on live here so the rest of the
package never hard-codes a path. Paths are derived from this file's location
(so the package is portable within the repo) with environment-variable
overrides for the two machine-specific dependencies (the Zotero database and
the external extractor).

Usage example
-------------
>>> from ab_plus import config
>>> config.BIB_PATH.exists()
True
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Repo-relative paths ---------------------------------------------------
# This file is scripts/ab_plus/config.py, so the repo root is two parents up.
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

AB_PLUS_DIR: Path = REPO_ROOT / "outputs" / "ab-plus"
"""Where the per-source AB+ markdown deliverables and the index live."""

WORK_DIR: Path = AB_PLUS_DIR / "_work"
"""Gitignored scratch space for page/entry/verdict JSON. Page text is
copyrighted, so nothing here is ever committed (see .gitignore)."""

BIB_PATH: Path = REPO_ROOT / "paper" / "references.bib"
"""The 25-entry BibTeX file produced by lit-scout-iterate (citekey -> title)."""

# --- Zotero collection that holds the paper's sources ----------------------
COLLECTION_KEY: str = "BTKV5ZIF"
"""Zotero collection key for 'Paper-B' (group library 5861859).

Updated 2026-07-24: the original staging subcollection ('2026-06-06-
independence-of-context-llm-verification-grounding', key VQQ9C2RK) was
dissolved when the bibliography was consolidated into the Paper-B
collection; the stale key made resolve_collection return nothing."""

ZOTERO_DB: Path = Path(
    os.environ.get("AB_PLUS_ZOTERO_DB", "~/Zotero/zotero.sqlite")
).expanduser()
"""Zotero's SQLite database. Opened read-only (immutable URI) — never written."""

# --- The external matching-grade extractor (lives in llm-reproducibility) --
EXTRACTOR_DIR: Path = Path(
    os.environ.get(
        "AB_PLUS_EXTRACTOR_DIR",
        "~/Code/llm-reproducibility/extraction-system/scripts/pdf_processing",
    )
).expanduser()
"""Directory holding extract_pdf_text.py and pdf_cleaner.py. Imported in place
(the established convention); requires a Python with PyMuPDF installed
(e.g. the repo-local .venv/bin/python)."""

# --- Pipeline tuning -------------------------------------------------------
KEY_POINT_MIN: int = 3
KEY_POINT_MAX: int = 7
"""Salience cap on key points per source (cap by salience to the paper, not by
what the source covers — surveys would otherwise balloon)."""

SUMMARY_WORDS_MIN: int = 300
SUMMARY_WORDS_MAX: int = 500
"""Target band for the advisory whole-paper summary. No padding — longer only
where the paper's length/density warrants it."""
