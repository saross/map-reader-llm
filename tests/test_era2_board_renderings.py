"""Tier-1 drift guards for the Era-2 board's two generated Markdown tables.

``results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.md``
and ``frame-deltas.md`` are the documents a reader reaches for a *rank* and
a *frame delta*, and the 2026-09-13 re-score found them in neither
compliance regime: no hand banner and changelog, and no GENERATED banner,
source commit or drift guard either
(``planning/interim-docs-review.md`` § 11.4 state 3). This module is the
guard half of closing that (checklist item 11b).

Both documents are pure projections of committed JSON — ``tiering_20m.json``
and ``gates.json`` — so the guard re-renders in memory and compares. No
permutation is re-run, no cell is re-scored, and nothing under ``outputs/``
is read: the whole module is a few file reads, which is why it is tier 1.
"""

from __future__ import annotations

import json

import pytest

# Each generator owns its own render-stamp regex, and the two banners word
# the stamp differently, so the aliases keep the assertions honest.
from scripts.build_gs_era2_board import _RENDER_STAMP_RE as BOARD_STAMP_RE
from scripts.build_gs_era2_board import (
    BOARD_DIR,
    REPO_ROOT,
    check_renderings,
    render_deltas,
)
from scripts.era1_leaderboard_tiering import _RENDER_STAMP_RE as TIERING_STAMP_RE
from scripts.era1_leaderboard_tiering import (
    check_rendering,
    render_markdown,
    tiering_paths,
)

pytestmark = pytest.mark.tier1

BOARD = REPO_ROOT / BOARD_DIR
BUFFER_M = 20
HEAD_LINES = 15


@pytest.fixture(scope="module")
def tiering() -> dict:
    """The committed tiering result for the Era-2 verified board."""
    json_path, _ = tiering_paths(BOARD, BUFFER_M)
    return json.loads(json_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def gates() -> dict:
    """The committed gates report for the Era-2 verified board."""
    return json.loads((BOARD / "gates.json").read_text(encoding="utf-8"))


def test_committed_tiering_markdown_has_no_drift():
    """``--check <board dir>`` passes against the committed pair."""
    assert check_rendering(BOARD, BUFFER_M) == 0


def test_committed_board_renderings_have_no_drift():
    """``check-renderings`` passes for frame-deltas.md and membership.txt."""
    assert check_renderings(BOARD) == 0


def test_tiering_markdown_carries_banner_generator_and_both_commits(tiering):
    _, md_path = tiering_paths(BOARD, BUFFER_M)
    head = "\n".join(md_path.read_text(encoding="utf-8").splitlines()[:HEAD_LINES])
    assert "GENERATED FILE" in head
    assert "scripts/era1_leaderboard_tiering.py" in head
    # The commit the board was COMPUTED at is the provenance that matters;
    # the render commit is the one the drift check neutralises.
    assert f"`{tiering['git_commit']}`" in head
    assert TIERING_STAMP_RE.search(head)


def test_frame_deltas_carries_banner_generator_and_stamp():
    head = "\n".join((BOARD / "frame-deltas.md").read_text(
        encoding="utf-8").splitlines()[:HEAD_LINES])
    assert "GENERATED FILE" in head
    assert "scripts/build_gs_era2_board.py" in head
    assert "at commit `" in head


def test_render_stamp_is_neutralised_but_a_changed_row_is_not(tiering):
    """The guard must ignore a re-render and catch a moved number."""
    at_a = render_markdown(tiering, "aaaaaaaaa")
    at_b = render_markdown(tiering, "bbbbbbbbb")
    assert at_a != at_b
    assert TIERING_STAMP_RE.sub("", at_a) == TIERING_STAMP_RE.sub("", at_b)

    tampered = json.loads(json.dumps(tiering))
    tampered["ranking"][0]["eval_f1"] = 0.1234
    assert TIERING_STAMP_RE.sub("", render_markdown(tampered, "aaaaaaaaa")) != \
        TIERING_STAMP_RE.sub("", at_a)


def test_frame_deltas_render_stamp_is_neutralised_but_a_delta_is_not(gates):
    at_a = render_deltas(gates, "aaaaaaaaa")
    at_b = render_deltas(gates, "bbbbbbbbb")
    assert at_a != at_b
    assert BOARD_STAMP_RE.sub("", at_a) == BOARD_STAMP_RE.sub("", at_b)

    tampered = json.loads(json.dumps(gates))
    scored = next(c for c in tampered["cells"] if c["status"] != "missing")
    scored["board_f1_20"] = 0.1234
    assert BOARD_STAMP_RE.sub("", render_deltas(tampered, "aaaaaaaaa")) != \
        BOARD_STAMP_RE.sub("", at_a)


def test_tiering_markdown_has_one_row_per_ranked_cell(tiering):
    """A rank table that silently loses a cell is drift a banner cannot hide."""
    _, md_path = tiering_paths(BOARD, BUFFER_M)
    text = md_path.read_text(encoding="utf-8")
    f1_rows = [ln for ln in text.splitlines()
               if ln.startswith("| ") and ln.count("|") == 10]
    # One label row plus one row per ranked cell, in the F1 table; the MCC
    # table's rows carry a different column count.
    assert len(f1_rows) - 1 == len(tiering["ranking"])
    assert f"**Cells**: {tiering['n_cells']} " in text


def test_withheld_cells_are_still_disclosed_in_the_rendering(tiering):
    """Ruling 6's withheld-cell disclosure must survive a re-render."""
    withheld = tiering.get("withheld_cells") or []
    _, md_path = tiering_paths(BOARD, BUFFER_M)
    text = md_path.read_text(encoding="utf-8")
    if withheld:
        assert f"**{len(withheld)} cell(s) WITHHELD**" in text
        for row in withheld:
            assert f"`{row['label']}`" in text
