"""Tier-1 tests for ``scripts/compare_leaderboard_board_content.py``.

The tool signs off the Phase 6 migration of the seven per-architecture 20 m
boards from the bare format to the enriched one (defect D35): a plain ``diff``
cannot distinguish "the two generators lay the columns out differently" from
"a number changed", and the migration turns on exactly that distinction.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.compare_leaderboard_board_content import (
    compare_boards,
    detect_format,
    parse_board,
)

BARE = """# Leaderboard (F1 tiers) — 20m buffer

**Generated**: 2026-05-06T09:33:34.120902+00:00
**Tiering metric**: F1
**FDR q**: 0.05
**Conditions**: 3 in 2 tier(s)

## Tier 1 (F1: 0.763–0.763)

| # | Condition | Arch | Era | Track | K | t | F1 | 95% CI | P | R | MCC |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|:------:|---:|---:|---:|
| 1 | cond-a | 1-pass | 2 | text | 1 | 1 | 0.763 | [0.732, 0.797] | 0.767 | 0.759 | 0.752 |

## Tier 2 (F1: 0.600–0.606)

| # | Condition | Arch | Era | Track | K | t | F1 | 95% CI | P | R | MCC |
|--:|-----------|:----:|:---:|:-----:|--:|--:|---:|:------:|---:|---:|---:|
| 2 | cond-b | 1-pass | 2 | image | 1 | 1 | 0.606 | [0.575, 0.636] | 0.557 | 0.664 | 0.734 |
| 3 | cond-c | 1-pass | 2 | image | 1 | 1 | 0.600 | [0.575, 0.629] | 0.474 | 0.814 | 0.311 |
"""

ENRICHED = """# Leaderboard — Era 2, Single-pass (raw), 20 m buffer

**Generated**: 2026-08-20T06:34:06.336562+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era2/single-pass/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 3 in 2 tier(s). Bounds: `inputs/b.geojson`.

## Tier 1 (F1: 0.763–0.763)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | cond-a | text | 1 | 1 | gemini-3-flash | detect_brief-text | — | — | 0.763 [0.732, 0.797] | 0.767 | 0.759 | — |

## Tier 2 (F1: 0.600–0.606)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 2 | cond-b | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.606 [0.575, 0.636] | 0.557 | 0.664 | — |
| 3 | cond-c | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | 0.600 [0.575, 0.629] | 0.474 | 0.814 | — |
"""

#: An era board row whose CI cell is a footnoted placeholder rather than an
#: interval — the shape the era-2 hand edit used before defect D34 was fixed.
FOOTNOTED = """# Leaderboard — 20m buffer

**Generated**: 2026-04-17T03:51:29.400040+00:00
**Conditions**: 1 in 1 tier(s)

## Tier 1 (F1: 0.854–0.854)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 1 | gold-standard-v2-greedy-v1-487 | 2 | text | 5 | 4 | 0.854 | n/a[^gs2ci] | 0.927 | 0.791 |
"""


def _write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.tier1
def test_detect_format_distinguishes_the_two_layouts():
    assert detect_format(["#", "Condition", "Track", "Proposer"]) == "enriched"
    assert detect_format(["#", "Condition", "Arch", "Era", "F1"]) == "bare"


@pytest.mark.tier1
def test_parse_board_reads_tiers_rows_and_numbers(tmp_path):
    board = parse_board(_write(tmp_path, "bare.md", BARE))
    assert board.fmt == "bare"
    assert sorted(board.tiers) == [1, 2]
    assert board.n_conditions == 3
    row = board.tiers[1][0]
    assert (row.rank, row.condition) == (1, "cond-a")
    assert (row.f1, row.ci, row.precision, row.recall, row.mcc) == (
        0.763, (0.732, 0.797), 0.767, 0.759, 0.752,
    )


@pytest.mark.tier1
def test_parse_board_reads_the_enriched_combined_f1_and_ci_cell(tmp_path):
    board = parse_board(_write(tmp_path, "rich.md", ENRICHED))
    assert board.fmt == "enriched"
    row = board.tiers[1][0]
    assert row.f1 == 0.763
    assert row.ci == (0.732, 0.797)
    assert row.mcc is None  # printed as an em dash


@pytest.mark.tier1
def test_parse_board_tolerates_a_footnoted_placeholder_ci(tmp_path):
    board = parse_board(_write(tmp_path, "foot.md", FOOTNOTED))
    row = board.tiers[1][0]
    assert row.f1 == 0.854
    assert row.ci is None
    assert row.precision == 0.927


@pytest.mark.tier1
def test_cross_format_migration_reports_no_content_difference(tmp_path):
    old = parse_board(_write(tmp_path, "bare.md", BARE))
    new = parse_board(_write(tmp_path, "rich.md", ENRICHED))
    report = compare_boards(old, new)
    assert report["content_differences"] == []
    assert report["old_conditions"] == report["new_conditions"] == 3
    assert report["old_tiers"] == report["new_tiers"] == 2
    # The MCC column the enriched format cannot populate is format-only.
    assert any("MCC" in line for line in report["format_only_differences"])


@pytest.mark.tier1
def test_a_changed_number_is_reported_as_content_drift(tmp_path):
    old = parse_board(_write(tmp_path, "bare.md", BARE))
    new = parse_board(
        _write(tmp_path, "rich.md", ENRICHED.replace("0.763 [0.732, 0.797]",
                                                     "0.799 [0.732, 0.797]"))
    )
    report = compare_boards(old, new)
    assert any("F1 0.763 vs 0.799" in line for line in report["content_differences"])


@pytest.mark.tier1
def test_a_changed_condition_or_tier_count_is_reported(tmp_path):
    old = parse_board(_write(tmp_path, "bare.md", BARE))
    new = parse_board(_write(tmp_path, "rich.md", ENRICHED.replace("cond-b", "cond-z")))
    report = compare_boards(old, new)
    assert any("condition" in line for line in report["content_differences"])

    dropped = ENRICHED.replace(
        "| 3 | cond-c | image | 1 | 1 | gemini-3-flash | library_plus-hp | — | — | "
        "0.600 [0.575, 0.629] | 0.474 | 0.814 | — |\n",
        "",
    )
    report = compare_boards(old, parse_board(_write(tmp_path, "short.md", dropped)))
    assert any("rows" in line for line in report["content_differences"])


@pytest.mark.tier1
def test_two_numeric_mcc_columns_that_disagree_are_content_not_format(tmp_path):
    old = parse_board(_write(tmp_path, "a.md", BARE))
    new = parse_board(_write(tmp_path, "b.md", BARE.replace("0.752", "0.999")))
    report = compare_boards(old, new)
    assert any("MCC 0.752 vs 0.999" in line for line in report["content_differences"])


@pytest.mark.tier1
def test_parse_board_rejects_a_file_with_no_tier_tables(tmp_path):
    with pytest.raises(ValueError):
        parse_board(_write(tmp_path, "stub.md", "# Leaderboard\n\n## No conditions\n"))
