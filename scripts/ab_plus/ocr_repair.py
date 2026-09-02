"""Rebuild a page cache by OCR when the PDF's text layer is unusable.

Some copies of record are rasterised browser print-to-PDFs (``Skia/PDF``
producer, one full-page image per page) whose only text layer is empty or a
publisher download watermark. The normal extractor then yields a cache the
gate marks FAIL. This module reproduces the repair pattern established by
hand in the pilot (three provenance notes, 2026-08-30):

1. preserve the original cache beside the new one
   (``<citekey>.pages.json.<signature>-pymupdf-original``);
2. render every page with PyMuPDF at a fixed dpi (optionally rotating
   named pages — landscape tables OCR as character soup upright);
3. run ``tesseract`` per page and store ``{page_index, text, section}``
   page-for-page aligned with the copy of record;
4. write a provenance note (``<citekey>.pages-provenance.md``) recording
   what was done and what the drafter must still do — OCR text is a
   derived artefact, so every quote drawn from it must be confirmed
   against the rendered page image before it is trusted.

Requires the ``tesseract`` binary (present on the workstation, absent on
sapphire at the time of writing). Nothing here calls an LLM.

Usage (from the repo root)::

    PYTHONPATH=scripts .venv/bin/python -m ab_plus.cli ocr-repair \
        --citekey trier_using_2019 [--dpi 300] [--rotate 12:90]
"""

from __future__ import annotations

import datetime as _dt
import json
import shutil
import subprocess
from pathlib import Path

from .config import WORK_DIR
from .gate import assess_cache


def _tesseract_version() -> str:
    """Return the first line of ``tesseract --version`` (or '' if absent)."""
    exe = shutil.which("tesseract")
    if not exe:
        return ""
    out = subprocess.run([exe, "--version"], capture_output=True, text=True, check=False)
    first = (out.stdout or out.stderr).strip().splitlines()
    return first[0] if first else exe


def ocr_page_png(png_bytes: bytes, lang: str = "eng", psm: int = 3) -> str:
    """OCR one rendered page (PNG bytes) with tesseract via stdin/stdout."""
    exe = shutil.which("tesseract")
    if not exe:
        raise RuntimeError("tesseract binary not found on PATH; OCR repair needs it")
    proc = subprocess.run(
        [exe, "stdin", "stdout", "--psm", str(psm), "-l", lang],
        input=png_bytes,
        capture_output=True,
        check=True,
    )
    return proc.stdout.decode("utf-8", errors="replace")


def ocr_repair(
    citekey: str,
    pdf_path: Path,
    dpi: int = 300,
    rotate: dict[int, int] | None = None,
    lang: str = "eng",
    psm: int = 3,
    force: bool = False,
) -> Path:
    """Replace ``<citekey>.pages.json`` with OCR-derived text and write provenance.

    Args:
        citekey: BibTeX citekey whose cache is being rebuilt.
        pdf_path: The copy of record (from the citekey→PDF map).
        dpi: Render resolution for OCR (300 matches the pilot repairs).
        rotate: Optional ``{page_index: degrees}`` for pages that must be
            rotated before OCR (landscape tables).
        lang: Tesseract language pack.
        psm: Tesseract page-segmentation mode (3 = fully automatic).
        force: Repair even if the gate does not mark the cache FAIL.

    Returns:
        Path of the provenance note written.

    Raises:
        RuntimeError: If tesseract is unavailable, or the existing cache
            passes the gate and ``force`` is not set.
    """
    import fitz  # PyMuPDF; imported lazily so the gate stays importable without it

    rotate = rotate or {}
    cache = WORK_DIR / f"{citekey}.pages.json"
    original_pages: list[dict] = (
        json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else []
    )
    gate = assess_cache(citekey, original_pages)
    if gate.verdict != "FAIL" and not force:
        raise RuntimeError(
            f"{citekey}: cache gate is {gate.verdict} ({gate.reason or 'ok'}); "
            "pass --force to OCR anyway"
        )
    signature = "empty" if gate.reason.startswith("empty") else "watermark-only"
    if cache.exists():
        backup = cache.with_name(f"{citekey}.pages.json.{signature}-pymupdf-original")
        if not backup.exists():
            shutil.copy2(cache, backup)

    doc = fitz.open(str(pdf_path))
    meta = doc.metadata or {}
    pages: list[dict] = []
    for i, page in enumerate(doc):
        if i in rotate:
            page.set_rotation(rotate[i])
        pix = page.get_pixmap(dpi=dpi)
        text = ocr_page_png(pix.tobytes("png"), lang=lang, psm=psm)
        pages.append({"page_index": i, "text": text, "section": "ocr (unsectioned)"})
    n_chars = sum(len(p["text"]) for p in pages)

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")

    note = cache.with_name(f"{citekey}.pages-provenance.md")
    today = _dt.date.today().isoformat()
    rot_line = (
        ", ".join(f"page_index {k} rotated {v}°" for k, v in sorted(rotate.items()))
        or "none"
    )
    note.write_text(
        "\n".join(
            [
                f"# Page-cache provenance — `{citekey}`",
                "",
                f"**Written {today} by `ab_plus.cli ocr-repair`.** Read this before "
                f"trusting `{citekey}.pages.json`.",
                "",
                "## Why this file exists",
                "",
                f"The pipeline's normal extraction produced a cache the pre-flight gate "
                f"marked **FAIL** — {gate.reason}. The cause is the source PDF, not the "
                "extractor.",
                "",
                f"- Copy of record: `{pdf_path}`",
                f"- PyMuPDF metadata: producer `{meta.get('producer', '')}`, creator "
                f"`{meta.get('creator', '')}`, {len(doc)} pages.",
                f"- Original cache: {gate.n_pages} pages, {gate.n_chars} characters, "
                f"{len(gate.empty_pages)} empty page(s), {gate.max_identical} pages "
                "byte-identical.",
                f"- The original cache is preserved beside this file as "
                f"`{citekey}.pages.json.{signature}-pymupdf-original`.",
                "",
                "## What replaced it",
                "",
                f"`{citekey}.pages.json` now holds **OCR-derived** page text:",
                "",
                f"1. Pages rendered at {dpi} dpi with PyMuPDF (`get_pixmap(dpi={dpi})`); "
                f"rotation: {rot_line}.",
                f"2. `tesseract stdin stdout --psm {psm} -l {lang}` per page "
                f"({_tesseract_version() or 'tesseract version unknown'}).",
                "3. One `{page_index, text, section}` dict per page, page-for-page aligned "
                "with the copy of record, so `page_index N` is the Nth page of the "
                "copy of record as usual (printed folios may differ — check the header).",
                "",
                f"Total {n_chars} characters across {len(pages)} pages "
                f"(was {gate.n_chars}).",
                "",
                "## Fidelity controls REQUIRED of the drafter and verifier",
                "",
                "OCR text is a derived artefact, so a quote byte-checked against it is "
                "attested against OCR rather than against the paper. Before a quote from "
                "this cache is trusted:",
                "",
                "1. **Visual attestation.** Read every quoted span directly off the "
                f"rendered page image (PyMuPDF `get_pixmap` at 200–{dpi} dpi, same "
                "rotation) and confirm it character-for-character, digits and "
                "punctuation included. Record the page indices checked in the section "
                "below.",
                "2. **Tables.** Read any table you cite as an image; OCR routinely "
                "truncates or reorders table rows. Do not lift table numbers from the "
                "cache.",
                "3. **Systematic OCR slips.** If a recurring misread would misname a term "
                "used in a quote (the pilot's `loU` for `IoU`), apply a global correction "
                "to the cache, and record it here with counts and the grounds.",
                "4. **Second witness.** If an open-access twin with a real text layer "
                "exists (preprint, repository deposit), extract it and use it to "
                "cross-check load-bearing numbers — but do NOT substitute its text: "
                "quotes are version-specific.",
                "",
                "## Drafter's attestation record",
                "",
                "_To be completed by the drafter: pages read as images; quotes confirmed; "
                "corrections applied; table caveats; second witness used (or 'none "
                "located', with where you looked)._",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return note
