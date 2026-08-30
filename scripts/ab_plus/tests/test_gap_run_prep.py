"""Tests for the gap-run prep fixes (title-markup join, citation-context seed)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ab_plus.citation_context_seed import _CITE_RE, _paragraphs
from ab_plus.zotero import _norm_title


def test_norm_title_strips_markup() -> None:
    """Embedded HTML tags must not leak tag names into the join key
    (the Marchionini_2024 failure: <scp> became literal 'scp')."""
    tagged = "Search, <scp>AI</scp>, and the Future"
    plain = "Search, AI, and the Future"
    assert _norm_title(tagged) == _norm_title(plain)
    assert "scp" not in _norm_title(tagged)
    # Plain titles are unaffected.
    assert _norm_title("LM vs LM: Detecting") == _norm_title("LM vs LM Detecting")


def test_cite_regex_full_family() -> None:
    """The context matcher covers the full natbib/biblatex cite family."""
    para = (
        r"As shown \citealp{Asch_1956} and \parencite[10]{flyvbjerg_five_2006}, "
        r"also \textcite{a, b} and \Cite*{c}."
    )
    keys = {k.strip() for m in _CITE_RE.finditer(para) for k in m.group(1).split(",")}
    assert {"Asch_1956", "flyvbjerg_five_2006", "a", "b", "c"} <= keys


def test_paragraph_split() -> None:
    """Paragraphs split on blank lines, whitespace-tolerant."""
    text = "Para one\ncontinues.\n\n  \nPara two."
    paras = _paragraphs(text)
    assert len(paras) == 2
    assert paras[1] == "Para two."
