#!/usr/bin/env python3
"""
Derive the per-SKU Gemini spend table from the monthly invoice exports.

Why this script exists
----------------------
``reports/billing/gemini-spend-by-sku.csv`` is the project's public record
of what Google billed for Gemini, per month and per SKU (stock-keeping unit:
one priced line such as "input token count gemini 3 flash text flex"). It
carries no account, invoice or project identifiers. Until 2026-10-04 it was
built by hand from the billing console's exports (Session 153); this script
reproduces that method exactly and is the table's writer from then on (WP4
of ``planning/cost-accounting-fix-plan-2026-09-21.md``; the monthly routine
in PI ruling D17 revised).

The method, as the committed rows encode it:

* source: the monthly **Cost table** export in ``docs/costs/`` (gitignored:
  it carries account identifiers), one file per invoice month, named
  ``... Cost table, YYYY-MM-01 — YYYY-MM-DD.csv``;
* rows: ``Service description`` is ``Gemini API`` and ``Project name`` is
  ``map-reader-llm``, one output row per SKU, in the export's own order;
* ``usage_amount`` without thousands separators; ``aud`` is the export's
  rounded ``Cost ($)``;
* ``aud_per_usd`` is the invoice header's ``Currency exchange rate``, and
  ``usd = round(aud / aud_per_usd, 2)`` from the ROUNDED AUD figure;
* ``basis`` is ``invoice``.

Gate: before writing, every month already in the table with basis
``invoice`` is re-derived from its export and must match the committed rows
byte for byte (nine months matched on 2026-10-04). A month whose export is
absent is kept as committed. A month whose rows are on another basis (the
provisional partial-month rows the September 2026 export left) is replaced
once its invoice export exists.

Usage::

    python scripts/derive_gemini_spend_by_sku.py            # dry run: report
    python scripts/derive_gemini_spend_by_sku.py --write    # apply
    python scripts/derive_gemini_spend_by_sku.py --check    # exit 1 on drift

Zero API, seconds of compute.

Created: 2026-10-04 (WP4 of the cost accounting plan, Session 159)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import calendar
import csv
import io
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLE = PROJECT_ROOT / "reports" / "billing" / "gemini-spend-by-sku.csv"
EXPORTS = PROJECT_ROOT / "docs" / "costs"
HEADER = "month,sku,usage_amount,usage_unit,aud,aud_per_usd,usd,basis"
SERVICE = "Gemini API"
PROJECT = "map-reader-llm"
#: The Cost table export's file name carries the invoice month's first and
#: last days; only a whole month is an invoice.
EXPORT_NAME = re.compile(r"Cost table, (\d{4}-\d{2})-01 \S+ (\d{4}-\d{2})-(\d{2})")


class DerivationError(Exception):
    """An export or the committed table is not in the shape this method reads."""


def find_exports(directory: Path = EXPORTS) -> dict[str, Path]:
    """Each invoice month's Cost table export, keyed ``YYYY-MM``.

    Raises:
        DerivationError: When one month has more than one Cost table export,
            since the method could not tell which is the invoice.
    """
    found: dict[str, Path] = {}
    for path in sorted(directory.glob("*Cost table*.csv")):
        match = EXPORT_NAME.search(path.name)
        if not match:
            print(f"skipped (name not a Cost table export): {path.name}", file=sys.stderr)
            continue
        month, end_month, end_day = match.group(1), match.group(2), int(match.group(3))
        year, mon = (int(x) for x in month.split("-"))
        if end_month != month or end_day != calendar.monthrange(year, mon)[1]:
            # A part-month export is not an invoice (the 2026-09-11 Reports
            # export was one): it must never replace or gate invoice rows.
            print(f"skipped (not a whole month): {path.name}", file=sys.stderr)
            continue
        if month in found:
            raise DerivationError(f"two Cost table exports for {month}: {found[month].name}, "
                                  f"{path.name}")
        found[month] = path
    return found


def derive_month(month: str, export_text: str) -> list[str]:
    """The table rows one month's Cost table export gives, in export order.

    Args:
        month: ``YYYY-MM``.
        export_text: The export's full text (preamble, column row, rows).

    Returns:
        CSV lines (no header), one per Gemini SKU of the project.

    Raises:
        DerivationError: When the preamble lacks an exchange rate or the
            column row is missing.

    Example:
        >>> derive_month("2026-08", text)[0]  # doctest: +SKIP
        '2026-08,Generate content ... caching,20122880,count,1.09,1.4389,0.76,invoice'
    """
    lines = export_text.lstrip("\ufeff").splitlines()  # a BOM, if read without utf-8-sig
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith("Billing account name"))
    except StopIteration as exc:
        raise DerivationError(f"{month}: no column row") from exc
    preamble = {row[0]: row[1] for row in csv.reader(lines[:start]) if len(row) > 1}
    if "Currency exchange rate" not in preamble:
        raise DerivationError(f"{month}: no exchange rate in the preamble")
    fx_text = preamble["Currency exchange rate"].strip()
    fx = float(fx_text)
    out = []
    for row in csv.DictReader(io.StringIO("\n".join(lines[start:]))):
        if row["Service description"] != SERVICE or row["Project name"] != PROJECT:
            continue
        # Both read strictly: a renamed column must refuse (KeyError -> exit 2),
        # never silently switch this guard off (re-audit, 2026-10-04).
        if row["Cost type"] != "Usage" or row["Credit type"]:
            # Every row of the ten months so far is plain usage. A credit,
            # adjustment or refund would emit a second row for its SKU, which
            # the table's one-row-per-SKU method has no place for: refuse it
            # so a human decides (audit lens A, 2026-10-04).
            raise DerivationError(f"{month}: a {row['Cost type']!r} row "
                                  f"(credit {row['Credit type']!r}) for "
                                  f"{row['SKU description']!r}; the method covers usage only")
        aud = row["Cost ($)"]
        usd = float(aud) / fx  # from the ROUNDED AUD, as the committed rows are
        out.append(",".join([month, row["SKU description"],
                             row["Usage amount"].replace(",", ""), row["Usage unit"],
                             aud, fx_text, f"{usd:.2f}", "invoice"]))
    return out


def read_table(path: Path = TABLE) -> dict[str, list[str]]:
    """The committed table's rows by month, in file order.

    Raises:
        DerivationError: When the header is not the expected one.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != HEADER:
        raise DerivationError(f"unexpected header in {path}")
    months: dict[str, list[str]] = {}
    for line in lines[1:]:
        months.setdefault(line.split(",", 1)[0], []).append(line)
    return months


def reconcile(table: dict[str, list[str]],
              exports: dict[str, Path]) -> tuple[dict[str, list[str]], list[str]]:
    """The table with every replaceable month re-derived, after the gate.

    Args:
        table: The committed rows by month.
        exports: The available Cost table exports by month.

    Returns:
        ``(new table, report lines)``.

    Raises:
        DerivationError: When a month already on the ``invoice`` basis does
            not re-derive exactly (the gate), so nothing is written.
    """
    new: dict[str, list[str]] = {}
    report = []
    for month in sorted(set(table) | set(exports)):
        rows = table.get(month, [])
        if month not in exports:
            new[month] = rows
            report.append(f"{month}: kept ({len(rows)} rows; no export here)")
            continue
        derived = derive_month(month, exports[month].read_text(encoding="utf-8-sig"))
        invoiced = bool(rows) and all(r.rsplit(",", 1)[1] == "invoice" for r in rows)
        if invoiced:
            if derived != rows:
                raise DerivationError(f"{month}: the committed invoice rows do not re-derive "
                                      "exactly; nothing written")
            report.append(f"{month}: reproduced exactly ({len(rows)} rows)")
        else:
            report.append(f"{month}: {'replaced' if rows else 'added'} from the invoice "
                          f"({len(rows)} -> {len(derived)} rows)")
        new[month] = derived
    return new, report


def render(table: dict[str, list[str]], newline: str = "\n") -> str:
    """The table as file text, months in order, with the given line terminator.

    The committed table uses CRLF (as the console exports do); ``main`` keeps
    whatever terminator the file already has, so a re-derivation never
    rewrites unchanged rows.
    """
    return newline.join([HEADER, *(r for m in sorted(table) for r in table[m])]) + newline


def main(argv: list[str] | None = None) -> int:
    """Report, and with ``--write`` apply, the per-SKU table from the invoices."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="apply the derivation")
    mode.add_argument("--check", action="store_true", help="exit 1 if the table would change")
    args = parser.parse_args(argv)
    try:
        # The module paths are read at call time (not as bound defaults), so a
        # caller that repoints them, as the tests do, is obeyed.
        exports = find_exports(EXPORTS)
        new, report = reconcile(read_table(TABLE), exports)
    except (DerivationError, KeyError) as exc:  # KeyError: a renamed export column
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print("\n".join(report))
    if not exports:
        # Without the gitignored exports nothing can be compared: say so
        # rather than report the table current (audit lens A, 2026-10-04).
        print(f"no invoice exports in {EXPORTS.relative_to(PROJECT_ROOT)}/; nothing checked")
        return 0
    current = TABLE.read_bytes().decode("utf-8")
    text = render(new, "\r\n" if "\r\n" in current else "\n")
    changed = text != current
    if args.check:
        print("drift: the table differs from the invoices" if changed else "table current")
        return 1 if changed else 0
    if args.write and changed:
        TABLE.write_bytes(text.encode("utf-8"))  # bytes: no newline translation
        print(f"wrote {TABLE.relative_to(PROJECT_ROOT)}")
    elif not args.write:
        print("(dry run: nothing written; --write applies it)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
