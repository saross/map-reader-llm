"""Tests for the 2026-07-24 /audit fix pass (provenance, HTML, note-push).

Offline only: no Zotero API, no live SQLite, no pandoc. Each test pins a
behaviour a specific audit finding showed was broken or unguarded.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ab_plus.checking import check_entry
from ab_plus.extraction import _extract_html_pages
from ab_plus.push_notes import (
    MARKER,
    _citekey_from_entry,
    _create_status,
    _insert_stamp,
)
from ab_plus.rendering import render_entry
from ab_plus.zotero import parse_bib_titles


# --- BibTeX quoted-title parsing (zotero.py) --------------------------------

def test_quoted_titles_parse(tmp_path: Path) -> None:
    """Quoted, brace-protected, multi-line, and braced forms all extract."""
    bib = tmp_path / "t.bib"
    bib.write_text(textwrap.dedent(r'''
        @article{Plain_2026, title = "A Plain Quoted Title", year = 2026}
        @article{Umlaut_2026, title = "M{\"u}ller and the {"}Slop{"} Problem"}
        @article{Multi_2026, title = "A title
            wrapped over two lines"}
        @book{Braced_2026, title = {A {Braced} Title}, booktitle = {Decoy}}
    '''), encoding="utf-8")
    titles = parse_bib_titles(bib)
    assert titles["Plain_2026"] == "A Plain Quoted Title"
    # Brace-protected quotes must not truncate the value (audit Medium).
    assert "Slop" in titles["Umlaut_2026"] and "Problem" in titles["Umlaut_2026"]
    assert "two lines" in titles["Multi_2026"]
    # `\btitle` must not match inside `booktitle` (verified non-collision).
    assert titles["Braced_2026"] == "A Braced Title"


# --- Stamp insertion (push_notes.py) ----------------------------------------

def test_insert_stamp_anchored() -> None:
    """The stamp lands immediately after the banner paragraph."""
    note = f"<p>{MARKER} banner text.</p><hr/><h1>Body</h1>"
    out = _insert_stamp(note, "<p>STAMP</p>")
    assert out is not None
    assert out.index("STAMP") > out.index(MARKER)
    assert out == f"<p>{MARKER} banner text.</p><p>STAMP</p><hr/><h1>Body</h1>"


def test_insert_stamp_refuses_without_anchor() -> None:
    """No marker, or no closing </p> after it, must refuse — not splice at
    offset 3 (the find()-returns--1 arithmetic bug, audit Medium)."""
    assert _insert_stamp("<p>plain note</p>", "<p>S</p>") is None
    assert _insert_stamp(f"<div>{MARKER} unclosed", "<p>S</p>") is None


# --- Citekey extraction and index.md tolerance (push_notes.py) --------------

def test_citekey_from_entry(tmp_path: Path) -> None:
    """Entries yield their citekey; an index.md-shaped file yields None
    instead of aborting the run (audit Critical)."""
    entry = tmp_path / "x.md"
    entry.write_text("| **citekey** | `Xy_2026` |\n", encoding="utf-8")
    assert _citekey_from_entry(entry) == "Xy_2026"
    index = tmp_path / "index.md"
    index.write_text("# Tranche index\n- some list\n", encoding="utf-8")
    assert _citekey_from_entry(index) is None


# --- Zotero POST response interpretation (push_notes.py) --------------------

def test_create_status_reads_failed_map() -> None:
    """HTTP 200 with a failed map is a failure, not 'created' (audit
    Critical: the write API returns 200 even when every item fails)."""
    ok = {"successful": {"0": {"key": "ABCD1234"}}, "failed": {}}
    assert _create_status(200, ok) == "created"
    bad = {"successful": {}, "failed": {"0": {"code": 400, "message": "x"}}}
    assert _create_status(200, bad) == "api-item-failed-400"
    assert _create_status(200, {"successful": {}, "failed": {}}) == \
        "api-error-empty-success"
    assert _create_status(200, None) == "api-error-unparseable-body"
    assert _create_status(412, ok) == "api-error-412"
    assert _create_status(0, None) == "api-unreachable"


# --- HTML snapshot extraction (extraction.py) -------------------------------

def test_html_truncated_tail_survives(tmp_path: Path) -> None:
    """A pending entity at EOF is flushed by close(), not dropped."""
    f = tmp_path / "t.html"
    f.write_text("<p>alpha &amp", encoding="utf-8")
    pages = _extract_html_pages(f)
    assert "alpha" in pages[0]["text"]


def test_html_table_cells_separated(tmp_path: Path) -> None:
    """Adjacent table cells must not concatenate into one pseudo-word."""
    f = tmp_path / "t.html"
    f.write_text(
        "<table><tr><td>Cell1</td><td>Cell2</td></tr></table>"
        "<script>var x = 'never';</script>",
        encoding="utf-8",
    )
    text = _extract_html_pages(f)[0]["text"]
    assert "Cell1Cell2" not in text
    assert "Cell1" in text and "Cell2" in text
    assert "never" not in text  # script content skipped


def test_html_single_page_contract(tmp_path: Path) -> None:
    """The single-page cache satisfies the quote checker end to end."""
    f = tmp_path / "t.html"
    f.write_text("<p>The mechanism is independence of context.</p>", encoding="utf-8")
    pages = _extract_html_pages(f)
    entry = {
        "citekey": "Html_2026",
        "key_points": [{
            "quote": "independence of context",
            "page_index": 0, "section": "", "paraphrase": "",
            "relevance_gap": "", "relevance_section": "", "relevance_stance": "supports",
        }],
    }
    report = check_entry(entry, pages)
    assert report.n_passed == report.n_quotes == 1


# --- Provenance rendering (rendering.py) ------------------------------------

def _stub_report():
    return check_entry({"citekey": "T_2026", "key_points": []},
                       [{"page_index": 0, "text": "x", "section": ""}])


def test_render_without_provenance_is_stampless() -> None:
    """None and {} both render no stamp — bare re-renders stay byte-stable
    (audit Critical: a rev-only stamp broke re-render idempotency)."""
    entry = {"citekey": "T_2026", "summary": "S."}
    a = render_entry(entry, _stub_report(), provenance=None)
    b = render_entry(entry, _stub_report(), provenance={})
    assert a == b
    assert "Generated by" not in a


def test_render_stamp_sanitised_and_hedged() -> None:
    """Backticks in values cannot break the code span; the stamp says
    'requested' (transcripts remain ground truth for the resolved model)."""
    entry = {"citekey": "T_2026", "summary": "S."}
    md = render_entry(entry, _stub_report(), provenance={
        "model": "weird`model", "run_date": "2026-07-24",
    })
    line = next(l for l in md.splitlines() if "Generated by" in l)
    assert "weird'model" in line and "`weird`model`" not in md
    assert "requested" in line
