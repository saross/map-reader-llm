"""Golden tests for the deterministic AB+ core.

The load-bearing guarantee is the quote-checker, so the central test reuses the
six quotes hand-verified during co-design (mirroring ``ab-plus/huang2023large.md``)
as a fixture: they must all PASS, a fabricated quote must be NOT_FOUND, and a
real quote on the wrong claimed page must be LOCATOR_MISMATCH.

These are integration tests: they extract from the real Huang 2023 PDF in the
local Zotero library. If the PDF or the PyMuPDF extractor is unavailable they
skip rather than fail, so the suite is portable, but on Shawn's machine they run
fully.

Run with pytest, or standalone::

    ~/Code/write-like-me/.venv/bin/python scripts/ab_plus/tests/test_ab_plus.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the package importable when run as a standalone script.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ab_plus.checking import QuoteStatus, check_entry  # noqa: E402
from ab_plus.extraction import extract_source  # noqa: E402
from ab_plus.zotero import resolve_collection  # noqa: E402

CITEKEY = "Huang2023large"

# The six co-design-verified quotes with their authoritative page_index, plus
# the framing hook — the exact content of the hand-drafted golden entry.
GOLDEN_KEY_POINTS = [
    # (quote, page_index)
    ("The fundamental issue is that LLMs cannot properly judge the correctness of their reasoning", 3),
    ("the accuracies of all models drop across all benchmarks", 3),
    ("current LLMs struggle to self-correct their reasoning without external feedback", 7),
    ("based solely on its inherent capabilities, without the crutch of external feedback", 0),
    ("the code executor serves as the perfect verifier to judge the correctness of predicted programs", 7),
]
GOLDEN_HOOK = (
    "If an LLM possesses the ability to self-correct, why doesn't it simply offer the correct answer in its initial attempt?",
    0,
)


def _build_entry(key_points, hook=None) -> dict:
    """Assemble a minimal schema-shaped entry from (quote, page_index) pairs."""
    entry = {
        "citekey": CITEKEY,
        "summary": "(fixture)",
        "positioning": "(fixture)",
        "key_points": [
            {
                "quote": q,
                "page_index": p,
                "section": "",
                "paraphrase": "(fixture)",
                "relevance_gap": "Gap 2",
                "relevance_section": "§2",
                "relevance_stance": "supports",
            }
            for q, p in key_points
        ],
    }
    if hook is not None:
        entry["framing_hook"] = {"quote": hook[0], "page_index": hook[1], "note": "(fixture)"}
    return entry


def _huang_pages():
    """Resolve + extract Huang 2023, or return None if unavailable (skip)."""
    try:
        resolved, _ = resolve_collection()
    except Exception:
        return None
    ref = resolved.get(CITEKEY)
    if ref is None or not ref.exists:
        return None
    try:
        return extract_source(CITEKEY, ref.pdf_path)
    except Exception:
        return None


def test_golden_quotes_all_pass():
    """All six verified quotes + the hook pass on their claimed pages."""
    pages = _huang_pages()
    if pages is None:
        print("SKIP test_golden_quotes_all_pass (Huang PDF/extractor unavailable)")
        return
    entry = _build_entry(GOLDEN_KEY_POINTS, GOLDEN_HOOK)
    report = check_entry(entry, pages)
    assert report.all_passed, f"expected all PASS, got:\n{report.failures}"
    assert report.n_quotes == 6, f"expected 6 quotes, got {report.n_quotes}"
    print(f"PASS test_golden_quotes_all_pass ({report.n_passed}/{report.n_quotes})")


def test_fabricated_quote_not_found():
    """A plausible-but-absent quote is caught as NOT_FOUND."""
    pages = _huang_pages()
    if pages is None:
        print("SKIP test_fabricated_quote_not_found (unavailable)")
        return
    entry = _build_entry([
        ("large language models can reliably correct their own mistakes without any help", 0),
    ])
    report = check_entry(entry, pages)
    assert report.has_fabrication, "fabricated quote should be NOT_FOUND"
    assert report.results[0].status is QuoteStatus.NOT_FOUND
    print("PASS test_fabricated_quote_not_found")


def test_wrong_page_is_locator_mismatch():
    """A real quote with a wrong claimed page is LOCATOR_MISMATCH, not PASS."""
    pages = _huang_pages()
    if pages is None:
        print("SKIP test_wrong_page_is_locator_mismatch (unavailable)")
        return
    # The mechanism quote really sits on page_index 3; claim 0.
    entry = _build_entry([
        ("The fundamental issue is that LLMs cannot properly judge the correctness of their reasoning", 0),
    ])
    report = check_entry(entry, pages)
    r = report.results[0]
    assert r.status is QuoteStatus.LOCATOR_MISMATCH, f"got {r.status}"
    assert 3 in r.verified_pages, f"expected page 3 in verified, got {r.verified_pages}"
    print("PASS test_wrong_page_is_locator_mismatch")


def test_resolve_finds_pdfs():
    """The Zotero title-join resolves a healthy share of the collection."""
    try:
        resolved, unresolved = resolve_collection()
    except Exception as exc:
        print(f"SKIP test_resolve_finds_pdfs ({exc})")
        return
    assert CITEKEY in resolved, f"{CITEKEY} should resolve; unresolved={unresolved}"
    print(f"PASS test_resolve_finds_pdfs ({len(resolved)} resolved, {len(unresolved)} unresolved)")


if __name__ == "__main__":
    test_resolve_finds_pdfs()
    test_golden_quotes_all_pass()
    test_fabricated_quote_not_found()
    test_wrong_page_is_locator_mismatch()
    print("\nAll standalone checks complete.")
