"""Tier-1 tests for ``scripts/derive_gemini_spend_by_sku.py`` (WP4, 2026-10-04).

The real exports are gitignored (they carry account identifiers), so these
tests build a synthetic Cost table export in the console's shape: an
eight-line preamble, the column row, then one row per SKU.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import derive_gemini_spend_by_sku as d

pytestmark = pytest.mark.tier1

COLUMNS = ("Billing account name,Billing account ID,Project name,Project ID,Project hierarchy,"
           "Service description,Service ID,SKU description,SKU ID,Consumption model description,"
           "Credit type,Cost type,Usage start date,Usage end date,Usage amount,Usage unit,"
           "Unrounded cost ($),Cost ($)")


def export(fx: str, rows: list[tuple[str, str, str, str, str, str]]) -> str:
    """A synthetic export: rows are (project, service, sku, amount, unrounded, cost)."""
    pre = ["Invoice number,X", "Invoice date,2026-08-31", "Due date,X", "Billing ID,X",
           "Billing account ID,X", "Currency,AUD", f"Currency exchange rate,{fx}",
           'Total amount due,"$1,000.00"']
    body = [f'acct,ID,{p},pid,h,{s},sid,{sku},skuid,Default,,Usage,d1,d2,"{amt}",count,{unr},{cost}'
            for p, s, sku, amt, unr, cost in rows]
    return "\n".join([*pre, COLUMNS, *body]) + "\n"


AUGUST = export("1.4389", [
    ("map-reader-llm", "Gemini API", "sku caching", "20,122,880", "1.085840", "1.09"),
    ("map-reader-llm", "Gemini API", "sku text", "46,546", "0.050230", "0.05"),
    ("Shawn-individual", "Gemini API", "other project", "5", "9.0", "9.00"),
    ("map-reader-llm", "", "tax line", "0", "1.0", "1.00"),
])


def test_a_month_derives_in_the_committed_method():
    rows = d.derive_month("2026-08", AUGUST)
    # Other projects and non-Gemini lines are dropped; separators stripped.
    assert rows == ["2026-08,sku caching,20122880,count,1.09,1.4389,0.76,invoice",
                    "2026-08,sku text,46546,count,0.05,1.4389,0.03,invoice"]


def test_usd_comes_from_the_rounded_aud():
    # SENTINEL: from the unrounded AUD (1.085840 / 1.4389 = 0.7546) the row
    # would read 0.75; the committed August row reads 0.76 (1.09 / 1.4389).
    assert d.derive_month("2026-08", AUGUST)[0].split(",")[6] == "0.76"
    assert f"{1.085840 / 1.4389:.2f}" == "0.75"


def test_an_export_without_a_rate_is_refused():
    text = AUGUST.replace("Currency exchange rate,1.4389", "Something else,1")
    with pytest.raises(d.DerivationError, match="exchange rate"):
        d.derive_month("2026-08", text)


def _write(tmp_path: Path, month: str, text: str) -> Path:
    path = tmp_path / f"Acct_Cost table, {month}-01 — {month}-28.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_the_gate_refuses_a_committed_month_that_does_not_reproduce(tmp_path):
    exports = {"2026-08": _write(tmp_path, "2026-08", AUGUST)}
    table = {"2026-08": ["2026-08,sku caching,20122880,count,1.09,1.4389,0.75,invoice",
                         "2026-08,sku text,46546,count,0.05,1.4389,0.03,invoice"]}
    with pytest.raises(d.DerivationError, match="do not re-derive"):
        d.reconcile(table, exports)


def test_a_provisional_month_is_replaced_and_an_unexported_one_kept(tmp_path):
    exports = {"2026-08": _write(tmp_path, "2026-08", AUGUST)}
    table = {"2026-07": ["2026-07,old,1,count,0.10,1.4468,0.07,invoice"],
             "2026-08": ["2026-08,partial,1,count,0.01,1.4000,0.01,reports export; fx provisional"]}
    new, report = d.reconcile(table, exports)
    assert new["2026-07"] == table["2026-07"]
    assert new["2026-08"] == d.derive_month("2026-08", AUGUST)
    assert report == ["2026-07: kept (1 rows; no export here)",
                      "2026-08: replaced from the invoice (1 -> 2 rows)"]


def test_an_invoiced_month_that_reproduces_passes_the_gate(tmp_path):
    exports = {"2026-08": _write(tmp_path, "2026-08", AUGUST)}
    table = {"2026-08": d.derive_month("2026-08", AUGUST)}
    new, report = d.reconcile(table, exports)
    assert new == table and report == ["2026-08: reproduced exactly (2 rows)"]


def test_two_exports_for_one_month_are_refused(tmp_path):
    _write(tmp_path, "2026-08", AUGUST)
    (tmp_path / "Acct_Cost table, 2026-08-01 — 2026-08-31 (1).csv").write_text(AUGUST)
    with pytest.raises(d.DerivationError, match="two Cost table exports"):
        d.find_exports(tmp_path)


def test_render_orders_months_under_the_header():
    text = d.render({"2026-09": ["2026-09,b"], "2026-08": ["2026-08,a"]})
    assert text == f"{d.HEADER}\n2026-08,a\n2026-09,b\n"


def test_render_keeps_a_crlf_terminator():
    # The committed table is CRLF; an LF rewrite churned all 128 lines once.
    text = d.render({"2026-08": ["2026-08,a"]}, "\r\n")
    assert text == f"{d.HEADER}\r\n2026-08,a\r\n"
