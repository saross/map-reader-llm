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
    frontiers_of,
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
    rows = frontiers_of(board)
    assert refresh_markdown(md, board, rows) == md


@pytest.mark.tier1
def test_the_refresh_changes_only_the_cost_axis(committed):
    # Revert the cost sentence alone and refresh: every other line must come
    # back unchanged. (Stale COSTS are the next test's sentinel.)
    board, md = committed
    old_md = md.replace("\n".join(fbb.COST_SENTENCE), "\n".join(OLD_SENTENCE))
    refreshed = refresh_markdown(old_md, board, frontiers_of(board))
    assert refreshed == md
    head = md.split("## Cost efficiency: what a dollar buys")[0]
    assert "| 1 | ARM2-N5-oracle |" in head  # the ranked table is still there


@pytest.mark.tier1
def test_a_document_of_another_shape_is_refused(committed):
    board, md = committed
    rows = frontiers_of(board)
    with pytest.raises(SystemExit, match="cost-efficiency section"):
        refresh_markdown(md.replace("## Cost efficiency: what a dollar buys", "## X"),
                         board, rows)
    with pytest.raises(SystemExit, match="ranked rows"):
        refresh_markdown(md.replace("| 1 | ARM2-N5-oracle |", "| 1 | renamed |"), board, rows)


@pytest.mark.tier1
def test_the_efficiency_frontier_is_the_priced_one(committed):
    # The frontier the PI reviewed (2026-10-04): every run priced, on the
    # deployment basis (carried where a registered carried cell exists).
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
def test_the_two_frontiers_of_d24(committed):
    # PI ruling D24 (2026-10-04): a carried frontier, the 3.7 rungs at their
    # addendum carried-analogues, beside the oracle frontier as the ceiling.
    board, md = committed
    frontiers = frontiers_of(board)
    # B N = 3 carried (0.8477) beats ARM2 N = 1 carried (0.8459): the step the
    # S158 walkthrough's carried path had left out.
    assert membership(frontiers["carried"]) == [
        "A, N = 1", "3.7 arm 2, N = 1", "B, N = 3", "fourth cell, N = 3",
        "3.7 arm 2, N = 3", "3.7 arm 2: all-3.7 stack, N = 5"]
    assert membership(frontiers["oracle"]) == [
        "A, N = 1", "3.7 arm 1, N = 1", "3.7 arm 2, N = 1", "fourth cell, N = 3",
        "3.7 arm 2, N = 3", "3.7 arm 2: all-3.7 stack, N = 5"]
    carried = {r["name"]: r for r in frontiers["carried"]}
    assert carried["3.7 arm 2, N = 1"]["label"] == "ARM2-N1-carried"
    assert carried["3.7 arm 2, N = 1"]["basis"] == "carried-analogue (post-hoc)"
    assert carried["3.7 arm 2, N = 1"]["tier"] is None  # untiered: not a board cell
    assert carried["A, N = 1"]["basis"] == "oracle"  # no carried point exists
    # The oracle frontier holds oracle cells only, and no ceiling rows.
    assert all(r["label"].endswith("-oracle") for r in frontiers["oracle"])
    assert not any(r["frontier"] == "ceiling" for rows in frontiers.values() for r in rows)
    # The committed document and JSON carry both.
    section = md.split("## Cost efficiency: what a dollar buys")[1].split("\n## ")[0]
    assert "### The carried frontier" in section
    assert "### The oracle frontier (the ceiling)" in section
    assert "| 3.7 arm 2, N = 1 | carried-analogue (post-hoc) | $38 | 0.8459 (untiered) |" \
        in section
    assert board["efficiency_frontiers"]["carried"][2] == "B-N3-carried"
    assert board["efficiency_frontiers"]["oracle"][-1] == "ARM2-N5-oracle"


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
    old_cost = lambda lbl: OLD_FAMILY_COST.get(fbb.family_of(lbl))  # noqa: E731
    # The stale ranked column is written HERE, independently of the function
    # under test (built through it, a no-op column survived; mutation round).
    labels = {c["label"] for c in board["cells"]}
    lines = md.split("\n")
    for i, line in enumerate(lines):
        cells = line.split(" | ")
        if line.startswith("| ") and len(cells) > 6 and cells[1] in labels:
            cells[5] = fbb.fmt_cost(old_cost(cells[1]))
            lines[i] = " | ".join(cells)
    stale = "\n".join(lines)
    monkeypatch.setattr(fbb, "cost_of", old_cost)
    monkeypatch.setattr(fbb, "cost_completed", lambda _lbl: False)
    stale_section = "\n".join(fbb.render_efficiency(frontiers_of(board)))
    head, rest = stale.split("## Cost efficiency: what a dollar buys", 1)
    stale = head + stale_section + "\n" + rest[rest.find("\n## "):]
    stale = stale.replace("\n".join(fbb.COST_SENTENCE), "\n".join(OLD_SENTENCE))
    assert "| 1 | ARM2-N5-oracle | oracle | 1 | a | — |" in stale  # the old, unpriced column
    assert stale != md
    assert "| A, N = 1 | oracle | $21 |" in stale       # the old cost, in the section
    assert "3.7 arm 1, N = 1" not in stale.split("## Cost efficiency")[1].split("\n## ")[0]
    monkeypatch.setattr(fbb, "cost_of", real_cost_of)
    monkeypatch.setattr(fbb, "cost_completed", real_completed)
    assert refresh_markdown(stale, board, frontiers_of(board)) == md


@pytest.mark.tier1
def test_the_write_path_records_cost_basis_and_leaves_the_addendum(tmp_path, monkeypatch,
                                                                     committed):
    board, md = committed
    stale = json.loads(json.dumps(board))
    for cell in stale["cells"]:
        cell["cost_usd"], cell.pop("cost_basis", None)
    stale.pop("cost_axis", None)
    stale.pop("efficiency_frontiers", None)  # the D24 block must be written back
    j, m = tmp_path / "b.json", tmp_path / "b.md"
    j.write_text(json.dumps(stale)), m.write_text(md)
    monkeypatch.setattr("scripts.final_board_cost_refresh.board_paths", lambda _ref: (j, m))
    assert main(["--write"]) == 0
    written = json.loads(j.read_text())
    assert written["cells"] == board["cells"] and written["cost_axis"] == board["cost_axis"]
    # Labels, not run names, in both frontiers' memberships (D24).
    assert written["efficiency_frontiers"] == board["efficiency_frontiers"]
    assert board["efficiency_frontiers"]["carried"] == [
        "A-N1-oracle", "ARM2-N1-carried", "B-N3-carried", "FOURTH-N3-carried",
        "ARM2-N3-carried", "ARM2-N5-carried"]
    assert board["efficiency_frontiers"]["oracle"] == [
        "A-N1-oracle", "ARM1-N1-oracle", "ARM2-N1-oracle", "FOURTH-N3-oracle",
        "ARM2-N3-oracle", "ARM2-N5-oracle"]
    assert written["addendum_cells"] == board["addendum_cells"]  # untouched
    assert written["tiers"] == board["tiers"] and written["pairwise"] == board["pairwise"]


@pytest.mark.tier1
def test_an_analogue_label_may_not_shadow_a_board_cell(committed):
    board, _ = committed
    paper_rows, by_label, tier_of, _ = frontier_inputs(board)
    clash = {"B-N3-carried": dict(by_label["B-N3-carried"])}
    with pytest.raises(ValueError, match="collide with board cells"):
        fbb.frontier_rows(paper_rows, by_label, tier_of, clash)


@pytest.mark.tier1
def test_a_board_cell_without_a_tier_is_a_defect_not_untiered(committed):
    board, _ = committed
    untiered = [[label for label in tier if label != "A-N1-oracle"] for tier in board["tiers"]]
    with pytest.raises(KeyError):
        frontiers_of({**board, "tiers": untiered})


@pytest.mark.tier1
def test_at_equal_cost_the_better_run_takes_the_step():
    rows = [("weak", "W", None), ("strong", "S", None)]
    cells = {lbl: {"f1_50": f1, "precision_50": 0.9, "n_detections": 100, "basis": "carried"}
             for lbl, f1 in (("W", 0.80), ("S", 0.85))}
    out = fbb.efficiency_rows(rows, cells, {"W": 2, "S": 1}, [],
                              cost_fn=lambda _: 10.0, completed_fn=lambda _: False)
    assert [r["name"] for r in out if r["frontier"] is True] == ["strong"]


@pytest.mark.tier1
def test_a_full_rebuild_says_its_analogues_are_pending(committed):
    board, _ = committed
    paper_rows, by_label, tier_of, _ = frontier_inputs(board)
    text = "\n".join(fbb.render_efficiency(fbb.frontier_rows(paper_rows, by_label, tier_of),
                                           analogues_applied=False))
    assert "not yet" in text and "substituted" in text
    assert "not yet" not in "\n".join(fbb.render_efficiency(frontiers_of(board)))
