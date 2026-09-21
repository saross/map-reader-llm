"""
Tier-1 tests for ``scripts/check_published_rates.py`` (PI ruling D18, amended).

The checker compares the rate card of record with Google's pricing page and
flags any difference for the PI; it never edits the card. The fixture is a
text excerpt of the real page retrieved 2026-09-21
(``tests/fixtures/pricing-page-2026-09-21.txt``): four model sections, each
with Standard, Batch, Flex and Priority blocks and dated amount lines.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import check_published_rates as cpr

pytestmark = pytest.mark.tier1

FIXTURE = Path(__file__).parent / "fixtures" / "pricing-page-2026-09-21.txt"


def _run(tmp_path: Path, text: str, *args: str) -> tuple[int, str]:
    p = tmp_path / "page.txt"
    p.write_text(text)
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cpr.main(["--html", str(p), *args])
    return rc, buf.getvalue()


def test_the_real_page_of_2026_09_21_matches_the_card_on_every_rate(tmp_path) -> None:
    rc, out = _run(tmp_path, FIXTURE.read_text(), "--at", "2026-09-21", "--json")
    results = json.loads(out)["results"]
    assert rc == 0
    assert {r["verdict"] for r in results} == {"OK"}
    assert len(results) == 4 * 3 * 3  # four models, three tiers, three classes


def test_the_2027_row_matches_the_pages_starting_amounts(tmp_path) -> None:
    rc, out = _run(tmp_path, FIXTURE.read_text(), "--at", "2027-01-02", "--json")
    results = json.loads(out)["results"]
    flash37 = [r for r in results if r["model"] == "gemini-3.7-flash"]
    assert all(r["verdict"] == "OK" for r in flash37), flash37
    assert next(r["page"] for r in flash37 if r["tier"] == "flex" and r["class"] == "input_fresh") == 0.75
    assert rc == 0


def test_a_changed_published_amount_is_flagged_precisely(tmp_path) -> None:
    text = FIXTURE.read_text()
    section = cpr.model_section(text, "Gemini 3.7 Flash")
    changed = section.replace("$0.0375 through December 31, 2026.",
                              "$0.075 through December 31, 2026.")
    assert changed != section
    rc, out = _run(tmp_path, text.replace(section, changed), "--at", "2026-09-21", "--json")
    bad = [r for r in json.loads(out)["results"] if r["verdict"] != "OK"]
    assert rc == 1
    assert [(r["model"], r["tier"], r["class"], r["page"]) for r in bad] == [
        ("gemini-3.7-flash", "flex", "input_cached", 0.075),
        ("gemini-3.7-flash", "batch", "input_cached", 0.075),
    ]


def test_a_missing_section_is_unparsed_and_flagged(tmp_path) -> None:
    text = FIXTURE.read_text()
    section = cpr.model_section(text, "Gemini 3.8 Flash")
    rc, out = _run(tmp_path, text.replace(section, ""), "--at", "2026-09-21")
    assert rc == 1
    assert out.count("UNPARSED gemini-3.8-flash") == 9
    assert "FLAG for the PI" in out and "never edits it" in out


def test_banners_and_decorated_headings_do_not_break_sections() -> None:
    text = ("Gemini 3.8 Flash is now available. Try it out .\nsome prose\n"
            "Gemini 3.8 Flash\ngemini-3.8-flash\nStandard\nInput price\n$0.75\n"
            "Gemini 3.1 Flash Image (Nano Banana 2) 🍌\ngemini-3.1-flash-image\n"
            "Standard\nInput price\n$9\n")
    section = cpr.model_section(text, "Gemini 3.8 Flash")
    assert section == "Gemini 3.8 Flash\ngemini-3.8-flash\nStandard\nInput price\n$0.75\n"
    assert cpr.published_rates(section, cpr.date(2026, 9, 21)) == {
        "standard": {"input_fresh": 0.75}}


def test_the_priority_block_does_not_overwrite_flex() -> None:
    text = ("Gemini 3.7 Flash\ngemini-3.7-flash\nFlex\nInput price\n$0.375\n"
            "Priority\nInput price\n$1.35\n")
    rates = cpr.published_rates(cpr.model_section(text, "Gemini 3.7 Flash"),
                                cpr.date(2026, 9, 21))
    assert rates["flex"]["input_fresh"] == 0.375
    assert rates["priority"]["input_fresh"] == 1.35


def test_the_checker_never_writes_the_card(tmp_path) -> None:
    card_path = cpr.PROJECT_ROOT / "data" / "pricing" / "gemini-rate-card.json"
    stamp = (card_path.stat().st_mtime_ns, card_path.read_bytes())
    text = FIXTURE.read_text().replace("$0.75 through December 31, 2026.",
                                       "$9.00 through December 31, 2026.")
    rc, _ = _run(tmp_path, text, "--at", "2026-09-21")
    assert rc == 1
    assert (card_path.stat().st_mtime_ns, card_path.read_bytes()) == stamp


def test_page_text_strips_markup_one_cell_per_line() -> None:
    raw = "<table><tr><td>Input price</td><td>$0.75</td><td>$0.375&nbsp;flex</td></tr></table>"
    assert cpr.page_text(raw) == "Input price\n$0.75\n$0.375 flex"
