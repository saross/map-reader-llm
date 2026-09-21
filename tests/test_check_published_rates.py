"""
Tier-1 tests for ``scripts/check_published_rates.py`` (PI ruling D18, amended).

The checker compares the rate card of record with Google's pricing page and
flags any difference for the PI; it never edits the card. These tests drive
it offline on synthetic pages shaped like the real one (a heading per
model, table rows per class with several dollar columns).
"""

from __future__ import annotations

import json

import pytest

from scripts import check_published_rates as cpr
from scripts.lib_cost import load_rate_card

pytestmark = pytest.mark.tier1


def _page(rates: dict[str, dict[str, tuple[float, float, float]]]) -> str:
    """A page with one section per model; each class row lists three amounts."""
    parts = ["<html><body><h1>Gemini Developer API pricing</h1>"]
    for name, rows in rates.items():
        parts.append(f"<h2>{name}</h2><table>")
        for label, (std, batch, flex) in rows.items():
            parts.append(f"<tr><td>{label}</td><td>${std}</td><td>${batch} through "
                         f"December 31, 2026</td><td>${flex}</td></tr>")
        parts.append("</table>")
    parts.append("</body></html>")
    return "".join(parts)


def _card_page(at: str = "2026-09-21") -> dict:
    """The page every card model would print today, from the card itself."""
    card = load_rate_card()
    page = {}
    for model, page_name in cpr.PAGE_NAMES.items():
        row = cpr.rate_row(model, at, card)["rates"]
        page[page_name] = {
            label: (row["standard"][cls], row["batch"][cls], row["flex"][cls])
            for cls, label in cpr.ROW_LABELS.items()}
    return page


def test_a_page_that_matches_the_card_is_ok(tmp_path) -> None:
    p = tmp_path / "pricing.html"
    p.write_text(_page(_card_page()))
    assert cpr.main(["--html", str(p), "--at", "2026-09-21"]) == 0


def test_a_changed_rate_is_flagged_and_names_the_class(tmp_path, capsys) -> None:
    page = _card_page()
    page["Gemini 3.7 Flash"]["Context caching price"] = (0.075, 0.075, 0.075)  # cache no longer halved
    p = tmp_path / "pricing.html"
    p.write_text(_page(page))
    assert cpr.main(["--html", str(p), "--at", "2026-09-21", "--json"]) == 1
    out = json.loads(capsys.readouterr().out)
    bad = [r for r in out["results"] if r["verdict"] != "OK"]
    assert [(r["model"], r["class"], r["verdict"]) for r in bad] == [
        ("gemini-3.7-flash", "input_cached", "CHANGED")]
    assert bad[0]["expected"] == {"standard": 0.075, "flex": 0.0375, "batch": 0.0375}
    assert bad[0]["found"] == [0.075]


def test_a_missing_section_or_row_is_unparsed_not_ok(tmp_path, capsys) -> None:
    page = _card_page()
    del page["Gemini 3.8 Flash"]
    del page["Gemini 3.7 Flash"]["Output price"]
    p = tmp_path / "pricing.html"
    p.write_text(_page(page))
    assert cpr.main(["--html", str(p), "--at", "2026-09-21"]) == 1
    text = capsys.readouterr().out
    assert "UNPARSED gemini-3.8-flash" in text.replace("  ", " ").replace("UNPARSED ", "UNPARSED ")
    assert "FLAG for the PI" in text
    assert "never edits it" in text


def test_the_checker_never_writes_the_card(tmp_path) -> None:
    card_path = cpr.PROJECT_ROOT / "data" / "pricing" / "gemini-rate-card.json"
    stamp = (card_path.stat().st_mtime_ns, card_path.read_bytes())
    page = _card_page()
    page["Gemini 3 Flash Preview"]["Input price"] = (9.0, 9.0, 9.0)
    p = tmp_path / "pricing.html"
    p.write_text(_page(page))
    assert cpr.main(["--html", str(p), "--at", "2026-09-21"]) == 1
    assert (card_path.stat().st_mtime_ns, card_path.read_bytes()) == stamp


def test_page_text_strips_markup_and_keeps_rows_on_one_line() -> None:
    raw = "<table><tr><td>Input price</td><td>$0.75</td><td>$0.375&nbsp;flex</td></tr></table>"
    text = cpr.page_text(raw)
    assert text == "Input price $0.75 $0.375 flex"
    assert cpr.amounts_on_row(text, "Input price") == {0.75, 0.375}
    assert cpr.amounts_on_row(text, "Output price") is None
    assert cpr.model_section("Gemini 3.7 Flash\nInput price $1\nGemini 3.8 Flash\nx",
                             "Gemini 3.7 Flash") == "Gemini 3.7 Flash\nInput price $1\n"
