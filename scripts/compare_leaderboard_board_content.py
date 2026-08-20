#!/usr/bin/env python3
"""
Compare the substantive content of two leaderboard board markdowns
===================================================================

Leaderboard boards under ``results/leaderboard/`` exist in two rendered
formats:

- the **bare** format written by ``scripts/build_tiered_leaderboard.py``
  (``| # | Condition | Arch | Era | Track | K | t | F1 | 95% CI | P | R | MCC |``),
  and
- the **enriched** format written by ``scripts/enrich_per_arch_markdown.py``
  (``| # | Condition | Track | K | Vote t | Proposer | Config | Verifier |
  Prob t | F1 [95% CI] | P | R | MCC |``), which adds a provenance header and
  metadata columns.

Phase 6 of the audit remediation (defect D35) re-emitted seven boards from the
bare format into the enriched one, and needed to show — per file — that the
tier structure, the condition tables, and every number were carried across
unchanged. A plain ``diff`` cannot show that: the two formats differ in header,
column set, and column order by construction.

This tool parses either format into a common shape::

    {tier_index: [(rank, condition, f1, ci_low, ci_high, p, r, mcc), ...]}

and reports the differences that matter: tier count, per-tier membership and
ordering, and each row's numbers. Columns present in only one format (MCC in
the bare format when the enriched source lacks it; proposer/config/verifier in
the enriched format) are reported separately as **format-only** differences
rather than as content drift, so a migration can be signed off as
number-preserving while the information the formats do not share stays visible.

Usage::

    python scripts/compare_leaderboard_board_content.py OLD.md NEW.md
    python scripts/compare_leaderboard_board_content.py --pairs pairs.tsv
    python scripts/compare_leaderboard_board_content.py --json OLD.md NEW.md

Exit codes::

    0  no content differences (format-only differences are permitted)
    1  content differences found
    2  a file could not be parsed

Author: Claude Code
Created: 2026-08-20
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

#: ``## Tier 3 (F1: 0.646–0.680)`` / ``## Tier 1 (MCC: 0.680–0.772)``.
_TIER_HEADING_RE = re.compile(r"^##\s+Tier\s+(\d+)\b")

#: A markdown table row: leading and trailing pipes, cells between.
_ROW_RE = re.compile(r"^\|(.+)\|\s*$")

#: A separator row (``|--:|-----|``) — never data.
_SEPARATOR_RE = re.compile(r"^\|[\s:\-|]+\|\s*$")

#: ``[0.751, 0.842]`` or ``n/a`` / ``n/a[^footnote]``.
_CI_RE = re.compile(r"\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]")

#: ``0.854`` possibly followed by a footnote marker.
_NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?$")


@dataclass(frozen=True)
class Row:
    """One parsed board row, reduced to the fields both formats carry.

    Attributes:
        rank: The ``#`` column.
        condition: The condition label.
        f1: F1 at the board's buffer, or None when not printed.
        ci: ``(lower, upper)`` of the F1 interval, or None when ``n/a``.
        precision: Precision, or None.
        recall: Recall, or None.
        mcc: MCC, or None when the board prints a placeholder.
    """

    rank: int
    condition: str
    f1: float | None
    ci: tuple[float, float] | None
    precision: float | None
    recall: float | None
    mcc: float | None


@dataclass
class Board:
    """A parsed board.

    Attributes:
        path: Source file.
        fmt: ``"bare"`` or ``"enriched"``.
        tiers: Tier index → ordered rows.
    """

    path: Path
    fmt: str
    tiers: dict[int, list[Row]] = field(default_factory=dict)

    @property
    def n_conditions(self) -> int:
        """Total rows across all tiers."""
        return sum(len(v) for v in self.tiers.values())


def _cells(line: str) -> list[str]:
    """Split a markdown table row into stripped cell strings.

    Args:
        line: A single ``| a | b |`` line.

    Returns:
        The cells, outer pipes discarded.
    """
    m = _ROW_RE.match(line)
    if not m:
        return []
    return [c.strip() for c in m.group(1).split("|")]


def _num(cell: str) -> float | None:
    """Parse a numeric cell, tolerating placeholders and footnote markers.

    Args:
        cell: Raw cell text.

    Returns:
        The number, or None for ``—`` / ``n/a`` / unparseable text.
    """
    token = re.sub(r"\[\^[^\]]+\]", "", cell).strip()
    if _NUM_RE.match(token):
        return float(token)
    return None


def _ci(cell: str) -> tuple[float, float] | None:
    """Parse a ``[lo, hi]`` interval cell.

    Args:
        cell: Raw cell text, possibly ``n/a`` or ``0.854 [0.83, 0.88]``.

    Returns:
        The interval, or None when the cell carries no interval.
    """
    m = _CI_RE.search(cell)
    return (float(m.group(1)), float(m.group(2))) if m else None


def detect_format(header_cells: list[str]) -> str:
    """Classify a table header as the bare or the enriched layout.

    Args:
        header_cells: Cells of the header row.

    Returns:
        ``"enriched"`` when the metadata columns are present, else ``"bare"``.
    """
    return "enriched" if "Proposer" in header_cells else "bare"


def parse_board(path: Path) -> Board:
    """Parse a board markdown into tiers of :class:`Row`.

    Args:
        path: Board file.

    Returns:
        The parsed board.

    Raises:
        ValueError: When no tier table can be found.
    """
    text = path.read_text(encoding="utf-8")
    tiers: dict[int, list[Row]] = {}
    fmt = ""
    current_tier: int | None = None
    header: list[str] = []

    for line in text.splitlines():
        heading = _TIER_HEADING_RE.match(line)
        if heading:
            current_tier = int(heading.group(1))
            tiers.setdefault(current_tier, [])
            header = []
            continue
        if current_tier is None or not line.startswith("|"):
            continue
        if _SEPARATOR_RE.match(line):
            continue
        cells = _cells(line)
        if not cells:
            continue
        if not header:
            header = cells
            fmt = fmt or detect_format(header)
            continue

        index = {name: i for i, name in enumerate(header)}

        def cell(*names: str) -> str:
            """Return the first present column among ``names``."""
            for name in names:
                if name in index and index[name] < len(cells):
                    return cells[index[name]]
            return ""

        rank_cell = cells[0]
        if not rank_cell.isdigit():
            continue

        f1_cell = cell("F1 [95% CI]", "F1")
        ci_cell = cell("95% CI", "F1 95% CI", "F1 [95% CI]")
        tiers[current_tier].append(
            Row(
                rank=int(rank_cell),
                condition=cell("Condition"),
                f1=_num(f1_cell.split("[")[0]),
                ci=_ci(ci_cell),
                precision=_num(cell("P")),
                recall=_num(cell("R")),
                mcc=_num(cell("MCC")),
            )
        )

    if not tiers:
        raise ValueError(f"no tier tables found in {path}")
    return Board(path=path, fmt=fmt or "bare", tiers=tiers)


def compare_boards(old: Board, new: Board) -> dict:
    """Diff two parsed boards on content, isolating format-only differences.

    Args:
        old: The superseded board.
        new: The replacement board.

    Returns:
        A report dict with ``content_differences`` (list of strings, empty on
        success), ``format_only_differences``, and per-board counts.
    """
    content: list[str] = []
    format_only: list[str] = []

    if sorted(old.tiers) != sorted(new.tiers):
        content.append(
            f"tier set differs: {sorted(old.tiers)} vs {sorted(new.tiers)}"
        )

    for tier in sorted(set(old.tiers) & set(new.tiers)):
        o_rows, n_rows = old.tiers[tier], new.tiers[tier]
        if len(o_rows) != len(n_rows):
            content.append(
                f"tier {tier}: {len(o_rows)} rows vs {len(n_rows)} rows"
            )
            continue
        for o, n in zip(o_rows, n_rows):
            where = f"tier {tier} rank {o.rank}"
            if o.rank != n.rank:
                content.append(f"{where}: rank {o.rank} vs {n.rank}")
            if o.condition != n.condition:
                content.append(
                    f"{where}: condition {o.condition!r} vs {n.condition!r}"
                )
            for label, a, b in (
                ("F1", o.f1, n.f1),
                ("CI", o.ci, n.ci),
                ("P", o.precision, n.precision),
                ("R", o.recall, n.recall),
            ):
                if a != b:
                    content.append(f"{where} {o.condition}: {label} {a} vs {b}")
            if o.mcc != n.mcc:
                # One format prints MCC from a field the other's source does
                # not carry; that is a format difference, not lost content —
                # unless both print a number and the numbers disagree.
                if o.mcc is not None and n.mcc is not None:
                    content.append(
                        f"{where} {o.condition}: MCC {o.mcc} vs {n.mcc}"
                    )
                else:
                    format_only.append(
                        f"{where} {o.condition}: MCC {o.mcc} vs {n.mcc}"
                    )

    if old.fmt != new.fmt:
        format_only.append(f"format: {old.fmt} → {new.fmt}")

    return {
        "old": str(old.path),
        "new": str(new.path),
        "old_format": old.fmt,
        "new_format": new.fmt,
        "old_tiers": len(old.tiers),
        "new_tiers": len(new.tiers),
        "old_conditions": old.n_conditions,
        "new_conditions": new.n_conditions,
        "content_differences": content,
        "format_only_differences": format_only,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. See the module docstring for exit codes."""
    parser = argparse.ArgumentParser(
        description="Compare two leaderboard boards on substantive content.",
    )
    parser.add_argument("old", type=Path, nargs="?", help="superseded board")
    parser.add_argument("new", type=Path, nargs="?", help="replacement board")
    parser.add_argument(
        "--pairs",
        type=Path,
        help="TSV file of OLD<TAB>NEW pairs, one per line, compared in turn.",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit the report(s) as JSON"
    )
    args = parser.parse_args(argv)

    pairs: list[tuple[Path, Path]] = []
    if args.pairs:
        for line in args.pairs.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            a, b = line.split("\t")[:2]
            pairs.append((Path(a), Path(b)))
    elif args.old and args.new:
        pairs.append((args.old, args.new))
    else:
        parser.error("give OLD and NEW, or --pairs")

    reports: list[dict] = []
    for old_path, new_path in pairs:
        try:
            report = compare_boards(parse_board(old_path), parse_board(new_path))
        except (OSError, ValueError) as exc:
            print(f"PARSE ERROR {old_path} / {new_path}: {exc}", file=sys.stderr)
            return 2
        reports.append(report)

    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        for r in reports:
            status = "SAME" if not r["content_differences"] else "DIFFERS"
            print(
                f"{status:8s} {r['new']}  "
                f"[{r['old_format']}→{r['new_format']}, "
                f"{r['old_conditions']} conditions in {r['old_tiers']} tiers "
                f"→ {r['new_conditions']} in {r['new_tiers']}]"
            )
            for line in r["content_differences"]:
                print(f"    CONTENT  {line}")
            for line in r["format_only_differences"]:
                print(f"    format   {line}")

    n_diff = sum(1 for r in reports if r["content_differences"])
    n_fmt = sum(len(r["format_only_differences"]) for r in reports)
    print(
        f"\n{len(reports)} pair(s): {len(reports) - n_diff} content-identical, "
        f"{n_diff} with content differences, "
        f"{n_fmt} format-only difference(s).",
        file=sys.stderr,
    )
    return 1 if n_diff else 0


if __name__ == "__main__":
    sys.exit(main())
