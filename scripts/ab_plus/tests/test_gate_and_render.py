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
    return [{"page_index": i, "text": t, "section": "§1"} for i, t in enumerate(texts)]


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


# --- 2026-09-03 additions: content heuristics, band warnings, verdict enum, overflow ----

from ab_plus.checking import check_overflow  # noqa: E402
from ab_plus.gate import content_notes  # noqa: E402
from ab_plus.schema import entry_warnings, validate_overflow, validate_verdict  # noqa: E402

BODY = ("The mound count was 169 of 1212 images in total. " * 40)  # number-rich prose


def _notes(texts: list[str], doi: str | None = None, sections: bool = True) -> list[str]:
    pages = _pages(texts)
    if not sections:
        for p in pages:
            p["section"] = ""
    return content_notes(pages, source_doi=doi)


def test_gate_content_cover_sheet_on_short_page_zero() -> None:
    """A repository cover sheet shifts the page mapping by one (UvA-DARE, ResearchGate)."""
    cover = "UvA-DARE (Digital Academic Repository)\nTitle\nDOI 10.1098/rsos.210155\n"
    notes = _notes([cover, BODY, BODY])
    assert any(n.startswith("cover-sheet") for n in notes)
    # The same phrase inside a long genuine first page is not a cover sheet.
    assert not any(n.startswith("cover-sheet") for n in _notes([cover + BODY * 2, BODY]))


def test_gate_content_author_manuscript() -> None:
    notes = _notes(["HHS Public Access\nAuthor manuscript\nPsychol Aging.\n" + BODY, BODY])
    assert any(n.startswith("author-manuscript") for n in notes)


def test_gate_content_sibling_doi_only_on_sparse_edge_pages() -> None:
    """Nosek 2019: the TICS neighbour's DOI sits on page 0; a reference list does not count."""
    first = "…lexical access is serial [4].\nhttps://doi.org/10.1016/j.tics.2019.07.010\n" + BODY
    notes = _notes([first, BODY], doi="10.1016/j.tics.2019.07.009")
    assert any("sibling DOI" in n for n in notes)
    refs = "\n".join(f"{i}. Author. Journal. https://doi.org/10.1002/arp.{1400 + i}" for i in range(6))
    assert not any("sibling DOI" in n for n in _notes([BODY, refs], doi="10.1002/arp.1731"))
    # An opaque suffix has no stem, so a case-variant of the source's own DOI is not a sibling.
    same = "DOI: 10.1017/S1537592721000931\n" + BODY
    assert not any("sibling DOI" in n for n in _notes([same, BODY], doi="10.1017/s1537592721000931"))


def test_gate_content_mid_sentence_opening_ignores_logo_lines() -> None:
    mid = "visual processing, up to the level of orthographic analysis. However, lexical\n" + BODY
    assert any("opens mid-sentence" in n for n in _notes([mid, BODY]))
    assert not any("opens mid-sentence" in n for n in _notes(["remote sensing\nArticle\n" + BODY]))
    assert not any("opens mid-sentence" in n for n in _notes(["arXiv:2505.21523v3 [cs.CL]\n" + BODY]))


def test_gate_content_trailing_text_after_references() -> None:
    """MacCoun 2015: the next Nature Comment opens after the reference list on the last page."""
    refs = "\n".join(f"{i}. Author, A. Journal 1, 1–2 ({2000 + i})." for i in range(1, 11))
    neighbour = "\nMany hands make tight work\n" + "Crowdsourcing research can balance discussions. " * 20
    footer = "\n© 2015 Macmillan Publishers Limited. All rights reserved"
    assert any(n.startswith("trailing-text") for n in _notes([BODY, refs + neighbour + footer]))
    assert not any(n.startswith("trailing-text") for n in _notes([BODY, refs + footer]))


def test_gate_content_ieee_access_and_conservative_caption_rule() -> None:
    ieee = "IEEE Access\nDigital Object Identifier 10.1109/ACCESS.2021.3080423\n" + BODY
    assert any("IEEE Access source" in n for n in _notes([ieee, BODY]))
    poor = "Intro text. TABLE 3. IoU and accuracy results are provided. " + ("prose word " * 150)
    assert any("number-poor page" in n for n in _notes([BODY, poor]))
    assert not any("caption-only" in n for n in _notes([BODY, "TABLE 3. IoU results.\n" + BODY]))


def test_gate_content_sections_empty_and_result_wiring() -> None:
    assert any(n.startswith("sections-empty") for n in _notes([BODY, BODY], sections=False))
    r = assess_cache("k", _pages([BODY, BODY]))
    assert r.verdict == "PASS" and r.notes == ()
    r2 = assess_cache("k", _pages(["UvA-DARE (Digital Academic Repository)\n", BODY, BODY]))
    assert r2.verdict == "WARN" and r2.reason.startswith("content: cover-sheet")
    assert "· cover-sheet" in format_table([r2])


def test_entry_warnings_are_advisory() -> None:
    entry, _ = _entry_and_pages()
    entry["summary"] = "w " * 200
    entry["positioning"] = "One. Two. Three. Four."
    ws = entry_warnings(entry)
    assert any("summary is 200 words" in w for w in ws)
    assert any("positioning runs to 4 sentences" in w for w in ws)
    entry["summary"] = "w " * 400
    entry["positioning"] = "One. Two (p. 3). Three."
    assert entry_warnings(entry) == []


def test_validate_verdict_enforces_vocabulary() -> None:
    ok = {"overall": "PASS-WITH-EDITS", "per_point": [
        {"index": 0, "verdict": "OVERREACH", "note": "n"},
        {"index": "not_checkable", "verdict": "NOT CHECKABLE", "note": "external knowledge"},
    ], "edits": []}
    assert validate_verdict(ok) == []
    bad = {"overall": "MAYBE", "per_point": [
        {"index": 0, "verdict": "PLAUSIBLE", "note": ""},
        {"index": 1, "verdict": "NOT CHECKABLE", "note": ""},
    ]}
    problems = validate_verdict(bad)
    assert any("overall 'MAYBE'" in p for p in problems)
    assert any("'PLAUSIBLE'" in p for p in problems)
    assert any("requires a note" in p for p in problems)
    # The vendored flag-list shape is accepted untouched.
    assert validate_verdict({"paraphrase_flags": [], "overall": "PASS"}) == []


def test_overflow_check_and_paraphrase_only_render() -> None:
    entry, pages = _entry_and_pages()
    overflow = {"citekey": "k", "items": [
        {"topic": "Count", "paraphrase": "About one image in seven carried a mound.",
         "quote": "169 of 1212 images", "page_index": 0, "section": "§3"},
        {"paraphrase": "This one is invented.", "quote": "not in the source", "page_index": 0},
    ]}
    assert validate_overflow(overflow) == []
    oreport = check_overflow(overflow, pages)
    assert oreport.n_quotes == 2 and oreport.n_passed == 1
    md = render_entry(entry, check_entry(entry, pages), overflow=overflow, overflow_report=oreport)
    assert "## Overflow (paraphrase only" in md
    assert "**Count** — About one image in seven carried a mound. (page_index 0" in md
    assert "169 of 1212 images" not in md.split("## Overflow")[1].split("## Extraction")[0]
    assert "1 item(s) withheld" in md
    assert "Overflow span check: **1/2 passed**" in md
    assert validate_overflow({"citekey": "k", "items": [{"paraphrase": "", "quote": "q", "page_index": "0"}]})


def test_render_labels_non_integer_per_point_index() -> None:
    entry, pages = _entry_and_pages()
    verdict = {"overall": "PASS", "per_point": [
        {"index": "summary", "verdict": "SUPPORTED", "note": "fine"},
        {"index": "not_checkable", "verdict": "NOT CHECKABLE", "note": "external"},
    ]}
    md = render_entry(entry, check_entry(entry, pages), verdict)
    assert "**summary: SUPPORTED**" in md and "**not_checkable: NOT CHECKABLE**" in md
