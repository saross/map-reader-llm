"""Tier-1 tests for ``scripts/final_board_cost_refresh.py`` (WP4b).

The refresh re-prices a signed board's cost axis without re-tiering it.
These tests pin that it changes nothing but cost, that it is idempotent,
and that the committed r2 board carries exactly the mapping's costs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.final_board_build as fbb
from scripts.final_board_cost_refresh import (
    OLD_SENTENCE,
    board_paths,
    frontier_inputs,
    main,
    membership,
    refresh_markdown,
)

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def committed():
    json_path, md_path = board_paths("r2")
    return (json.loads(json_path.read_text(encoding="utf-8")),
            md_path.read_text(encoding="utf-8"))


@pytest.mark.tier1
def test_the_committed_board_carries_the_mappings_costs(committed):
    # Drift guard: a mapping or register change without a refresh turns red.
    board, _ = committed
    for cell in board["cells"]:
        assert cell["cost_usd"] == pytest.approx(fbb.cost_of(cell["label"]), abs=1e-9), \
            cell["label"]
        assert cell["cost_basis"] == fbb.family_cost(fbb.family_of(cell["label"])).basis
    assert board["cost_axis"] == fbb.COST_AXIS


@pytest.mark.tier1
def test_the_refresh_is_idempotent_on_the_committed_board(committed):
    board, md = committed
    rows = fbb.efficiency_rows(*frontier_inputs(board))
    assert refresh_markdown(md, board, rows) == md


@pytest.mark.tier1
def test_the_refresh_changes_only_the_cost_axis(committed):
    # Rebuild the pre-WP4b shape (old sentence, old costs) and refresh it:
    # every line outside the cost column, the sentence and the efficiency
    # section must come back unchanged.
    board, md = committed
    old_md = md.replace("\n".join(fbb.COST_SENTENCE), "\n".join(OLD_SENTENCE))
    refreshed = refresh_markdown(old_md, board, fbb.efficiency_rows(*frontier_inputs(board)))
    assert refreshed == md
    head = md.split("## Cost efficiency: what a dollar buys")[0]
    assert "| 1 | ARM2-N5-oracle |" in head  # the ranked table is still there


@pytest.mark.tier1
def test_a_document_of_another_shape_is_refused(committed):
    board, md = committed
    rows = fbb.efficiency_rows(*frontier_inputs(board))
    with pytest.raises(SystemExit, match="cost-efficiency section"):
        refresh_markdown(md.replace("## Cost efficiency: what a dollar buys", "## X"),
                         board, rows)
    with pytest.raises(SystemExit, match="ranked rows"):
        refresh_markdown(md.replace("| 1 | ARM2-N5-oracle |", "| 1 | renamed |"), board, rows)


@pytest.mark.tier1
def test_the_efficiency_frontier_is_the_priced_one(committed):
    # The frontier the PI reviews (2026-10-04): every run priced.
    board, _ = committed
    rows = fbb.efficiency_rows(*frontier_inputs(board))
    assert membership(rows) == ["A, N = 1", "3.7 arm 1, N = 1", "3.7 arm 2, N = 1",
                                "fourth cell, N = 3", "3.7 arm 2, N = 3"]
    # Under the old table the 3.7 runs were absent, which made a different frontier.
    old = {"A-N1": 20.53, "A-N3": 41.22, "A-N5": 59.75, "A-N10": 103.91, "B-N1": 30.99,
           "B-N3": 65.48, "B-N5": 97.22, "B-N10": 173.59, "TM": 23.4, "TH7": 207.4,
           "T03": 261.0, "IM": 195.4, "UPL": 57.87}
    before = fbb.efficiency_rows(*frontier_inputs(board),
                                 cost_fn=lambda lbl: old.get(fbb.family_of(lbl)),
                                 completed_fn=lambda _: False)
    assert membership(before) == ["A, N = 1", "A, N = 3", "A, N = 5", "B, N = 3", "B, N = 5"]


@pytest.mark.tier1
def test_a_dry_run_writes_nothing(tmp_path, monkeypatch, committed):
    board, md = committed
    j, m = tmp_path / "b.json", tmp_path / "b.md"
    j.write_text(json.dumps(board)), m.write_text(md)
    monkeypatch.setattr("scripts.final_board_cost_refresh.board_paths", lambda _ref: (j, m))
    before = (j.read_bytes(), m.read_bytes())
    assert main([]) == 0
    assert (j.read_bytes(), m.read_bytes()) == before


#: The hand-entered table WP4b replaced (``final_board_build.py`` before
#: 2026-10-04); the 3.7 families had no figure.
OLD_FAMILY_COST = {"A-N1": 20.53, "A-N3": 41.22, "A-N5": 59.75, "A-N10": 103.91,
                   "B-N1": 30.99, "B-N3": 65.48, "B-N5": 97.22, "B-N10": 173.59,
                   "TM": 23.4, "TH7": 207.4, "T03": 261.0, "IM": 195.4, "UPL": 57.87}


@pytest.mark.tier1
def test_the_refresh_rewrites_a_stale_cost_column_and_section(committed, monkeypatch):
    # SENTINEL (lens B, 2026-10-04): render the board as it stood before WP4b
    # (old costs in the ranked column and the efficiency section, the old
    # sentence), then refresh it: the result must be the committed document.
    # A refresh that left the column or the section alone stays stale here.
    board, md = committed
    real_cost_of, real_completed = fbb.cost_of, fbb.cost_completed
    monkeypatch.setattr(fbb, "cost_of", lambda lbl: OLD_FAMILY_COST.get(fbb.family_of(lbl)))
    monkeypatch.setattr(fbb, "cost_completed", lambda _lbl: False)
    stale_rows = fbb.efficiency_rows(*frontier_inputs(board))
    stale = refresh_markdown(md, board, stale_rows).replace(
        "\n".join(fbb.COST_SENTENCE), "\n".join(OLD_SENTENCE))
    assert stale != md
    assert "| A, N = 1 | oracle | $21 |" in stale       # the old cost, in the section
    assert "3.7 arm 1, N = 1" not in stale.split("## Cost efficiency")[1].split("\n## ")[0]
    monkeypatch.setattr(fbb, "cost_of", real_cost_of)
    monkeypatch.setattr(fbb, "cost_completed", real_completed)
    assert refresh_markdown(stale, board, fbb.efficiency_rows(*frontier_inputs(board))) == md


@pytest.mark.tier1
def test_the_write_path_records_cost_basis_and_leaves_the_addendum(tmp_path, monkeypatch,
                                                                     committed):
    board, md = committed
    stale = json.loads(json.dumps(board))
    for cell in stale["cells"]:
        cell["cost_usd"], cell.pop("cost_basis", None)
    stale.pop("cost_axis", None)
    j, m = tmp_path / "b.json", tmp_path / "b.md"
    j.write_text(json.dumps(stale)), m.write_text(md)
    monkeypatch.setattr("scripts.final_board_cost_refresh.board_paths", lambda _ref: (j, m))
    assert main(["--write"]) == 0
    written = json.loads(j.read_text())
    assert written["cells"] == board["cells"] and written["cost_axis"] == board["cost_axis"]
    assert written["addendum_cells"] == board["addendum_cells"]  # untouched
    assert written["tiers"] == board["tiers"] and written["pairwise"] == board["pairwise"]
