"""Tests for the 2026-09-02 tail-run additions: cache gate and verdict rendering."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ab_plus.checking import check_entry
from ab_plus.gate import assess_cache, format_table
from ab_plus.rendering import render_entry

WATERMARK = "10990763, 2018, 2, Downloaded from https://example.org/doi/x. By University L"


def _pages(texts: list[str]) -> list[dict]:
    return [{"page_index": i, "text": t, "section": ""} for i, t in enumerate(texts)]


def test_gate_flags_empty_cache() -> None:
    """Zero text on every page is the pilot's first failure signature."""
    r = assess_cache("k", _pages(["", "", ""]))
    assert r.verdict == "FAIL" and r.reason.startswith("empty")


def test_gate_flags_watermark_only_cache() -> None:
    """Identical short pages (a publisher stamp) evaded the pilot's zero-length check."""
    r = assess_cache("k", _pages([""] + [WATERMARK] * 9))
    assert r.verdict == "FAIL"
    assert r.reason.startswith("watermark-only")
    assert r.max_identical == 9
    assert r.empty_pages == (0,)


def test_gate_warns_on_image_only_pages_but_passes_body() -> None:
    """A real article with image-only figure pages is usable — WARN, not FAIL."""
    body = "word " * 400  # 2,000 chars/page
    r = assess_cache("k", _pages([body, body, "", body]))
    assert r.verdict == "WARN" and r.reason.startswith("empty-pages")
    assert r.empty_pages == (2,)


def test_gate_passes_normal_cache_and_table_counts() -> None:
    body = "word " * 400
    results = [assess_cache("a", _pages([body, body])), assess_cache("b", _pages(["", ""]))]
    assert results[0].verdict == "PASS"
    table = format_table(results)
    assert "1 PASS, 0 WARN, 1 FAIL" in table
    assert table.splitlines()[1].startswith("FAIL")  # worst first


def _entry_and_pages() -> tuple[dict, list[dict]]:
    pages = _pages(["The mound count was 169 of 1212 images in total."])
    entry = {
        "citekey": "k",
        "summary": "s",
        "positioning": "p",
        "key_points": [
            {
                "quote": "169 of 1212 images",
                "page_index": 0,
                "paraphrase": "x",
                "relevance_gap": "g",
                "relevance_section": "§2",
                "relevance_stance": "supports",
            }
        ],
    }
    return entry, pages


def test_render_per_point_verdict_shape() -> None:
    """The pilot's per-point verdicts must render, not collapse to 'none'."""
    entry, pages = _entry_and_pages()
    report = check_entry(entry, pages)
    verdict = {
        "citekey": "k",
        "overall": "PASS-WITH-EDITS",
        "per_point": [{"index": 0, "verdict": "OVERREACH", "note": "quantifier inflated"}],
        "edits": ["key_points[0].paraphrase — replace 'most' with 'many'"],
    }
    md = render_entry(entry, report, verdict)
    assert "**KP1: OVERREACH** — quantifier inflated" in md
    assert "replace 'most' with 'many'" in md
    assert "**overall:** PASS-WITH-EDITS" in md
    assert "paraphrase flags" not in md
    assert "salience-ranked to the citing paper" in md


def test_render_flag_list_verdict_shape_still_supported() -> None:
    """The paper-b verdict shape keeps rendering for the vendored corpus."""
    entry, pages = _entry_and_pages()
    report = check_entry(entry, pages)
    verdict = {"paraphrase_flags": ["p1"], "summary_flags": [], "relevance_flags": [],
               "overall": "PASS"}
    md = render_entry(entry, report, verdict)
    assert "- **paraphrase flags:**" in md and "  - p1" in md
    assert "**summary flags:** none" in md
