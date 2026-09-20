"""Tier-1 tests for the r2 board's post-hoc addendum renderer.

``scripts/final_board_addendum_render.py`` exists because the 35-cell board is
SIGNED — its tiers and its 595-pair Benjamini-Hochberg family were computed
over exactly those cells — and the PI has ruled twice (2026-09-13, carried
forward 2026-09-20) that a cell landing afterwards does not re-tier it. The
renderer therefore has one job that must not slip: put the new cells BESIDE
the tiered board, never in it, and say so in both published documents.

These tests pin the three ways that could go wrong: an addendum row acquiring
a tier or a group letter, the tiered blocks being disturbed, and a re-run
appending a second section instead of refreshing the first.

Everything runs over synthetic documents in ``tmp_path``; no committed board
artefact is read and nothing is written outside it.
"""

from __future__ import annotations

import json

import pytest

from scripts import final_board_addendum_render as r

pytestmark = pytest.mark.tier1


def _evaluation(f1: float, mcc: float, n: int) -> dict:
    """A committed cell evaluation, reduced to the keys the renderer reads."""
    return {"summary": {
        "n_detections": n,
        "buffers": [
            {"buffer_metres": 20, "f1": f1 - 0.1, "f1_ci_lower": f1 - 0.11,
             "f1_ci_upper": f1 - 0.09, "precision": 0.7, "recall": 0.7},
            {"buffer_metres": 50, "f1": f1, "f1_ci_lower": f1 - 0.01,
             "f1_ci_upper": f1 + 0.01, "precision": 0.88, "recall": 0.86},
        ],
        "tile_classification": {
            "mcc": {"point": mcc, "ci_lower": mcc - 0.01,
                    "ci_upper": mcc + 0.01}},
    }}


def _board(tmp_path, cells: list[dict]) -> None:
    """Write a synthetic board home: manifest, evaluations, both documents."""
    (tmp_path / "cells_manifest.json").write_text(
        json.dumps({"cells": cells}) + "\n")
    for cell in cells:
        d = tmp_path / "cells" / cell["label"]
        d.mkdir(parents=True, exist_ok=True)
        if cell.get("_eval") is not None:
            (d / "evaluation.json").write_text(
                json.dumps(cell["_eval"]) + "\n")
    (tmp_path / "final_board_50m.json").write_text(json.dumps({
        "buffer_m": 50, "reference": "r2",
        "tiers": [["ARM2-N5-oracle"]],
        "cells": [{"label": "ARM2-N5-oracle", "group": "a"}],
        "pairwise": [{"a": "x", "b": "y"}]}) + "\n")
    (tmp_path / "final-board-50m.md").write_text(
        "# Board\n\n| rank |\n|---|\n\n## Provenance and gates\n\n- stage 1\n")


def _cell(label: str, basis: str, f1: float, mcc: float = 0.7,
          n: int = 5000) -> dict:
    return {"label": label, "basis": basis, "point": "(0.80, k1)",
            "committed_eval": False, "note": "why this point",
            "_eval": _evaluation(f1, mcc, n)}


# --- headline ---------------------------------------------------------------

def test_headline_reads_the_50m_row_and_the_tile_mcc(tmp_path) -> None:
    path = tmp_path / "evaluation.json"
    path.write_text(json.dumps(_evaluation(0.8459, 0.7128, 5936)))
    got = r.headline(path)
    assert got["f1_50"] == pytest.approx(0.8459)
    assert got["n_detections"] == 5936
    assert got["mcc"] == pytest.approx(0.7128)
    assert got["ci"] == pytest.approx([0.8359, 0.8559])


def test_headline_refuses_an_evaluation_without_the_headline_buffer(
        tmp_path) -> None:
    ev = _evaluation(0.8, 0.7, 10)
    ev["summary"]["buffers"] = [b for b in ev["summary"]["buffers"]
                                if b["buffer_metres"] != 50]
    path = tmp_path / "evaluation.json"
    path.write_text(json.dumps(ev))
    with pytest.raises(SystemExit, match="no 50 m row"):
        r.headline(path)


# --- addendum_rows ----------------------------------------------------------

def test_addendum_rows_take_only_the_covered_bases(tmp_path) -> None:
    _board(tmp_path, [
        _cell("ARM2-N1-carried", "carried-analogue (post-hoc)", 0.8459),
        _cell("ARM2-N1-mcc-oracle", "mcc-oracle (post-hoc)", 0.8100),
        _cell("A-N3-carried", "carried (post-hoc)", 0.8307),
        _cell("ARM2-N5-oracle", "oracle (r2-reference argmax)", 0.8871),
    ])
    labels = [row["label"] for row in r.addendum_rows(tmp_path)]
    assert labels == ["ARM2-N1-carried", "ARM2-N1-mcc-oracle"]


def test_addendum_rows_are_never_tiered_or_grouped(tmp_path) -> None:
    """The one invariant: an addendum row must not look like a board row."""
    _board(tmp_path, [
        _cell("ARM2-N1-carried", "carried-analogue (post-hoc)", 0.8459)])
    for row in r.addendum_rows(tmp_path):
        assert row["tier"] is None
        assert row["group"] is None


def test_addendum_rows_sort_by_f1_descending(tmp_path) -> None:
    _board(tmp_path, [
        _cell("low", "carried-analogue (post-hoc)", 0.7859),
        _cell("high", "carried-analogue (post-hoc)", 0.8802),
        _cell("mid", "mcc-oracle (post-hoc)", 0.8469),
    ])
    assert [row["label"] for row in r.addendum_rows(tmp_path)] == [
        "high", "mid", "low"]


def test_addendum_rows_refuse_an_unscored_cell(tmp_path) -> None:
    cell = _cell("ARM2-N1-carried", "carried-analogue (post-hoc)", 0.84)
    cell["_eval"] = None
    _board(tmp_path, [cell])
    with pytest.raises(SystemExit, match="no evaluation.json"):
        r.addendum_rows(tmp_path)


# --- render_table -----------------------------------------------------------

def test_render_table_emits_one_row_per_cell_without_the_posthoc_suffix(
        tmp_path) -> None:
    _board(tmp_path, [
        _cell("ARM2-N1-carried", "carried-analogue (post-hoc)", 0.8459)])
    table = r.render_table(r.addendum_rows(tmp_path))
    body = [ln for ln in table.splitlines() if ln.startswith("| ARM2")]
    assert len(body) == 1
    assert "| carried-analogue |" in body[0]
    assert "post-hoc" not in body[0]
    assert "0.8459" in body[0]


# --- splice -----------------------------------------------------------------

def test_splice_inserts_before_the_provenance_anchor() -> None:
    out = r.splice("# Board\n\nrows\n\n## Provenance and gates\n\n- stage 1\n",
                   f"{r.BEGIN}\nBLOCK\n{r.END}")
    assert out.index(r.BEGIN) < out.index("## Provenance and gates")
    assert out.count(r.BEGIN) == 1


def test_splice_is_idempotent() -> None:
    doc = "# Board\n\n## Provenance and gates\n"
    once = r.splice(doc, f"{r.BEGIN}\nFIRST\n{r.END}")
    twice = r.splice(once, f"{r.BEGIN}\nSECOND\n{r.END}")
    assert twice.count(r.BEGIN) == 1
    assert "FIRST" not in twice and "SECOND" in twice


def test_splice_refuses_a_document_it_cannot_place_the_block_in() -> None:
    with pytest.raises(SystemExit, match="refusing to guess"):
        r.splice("# Board\n\nno anchor here\n", f"{r.BEGIN}\nX\n{r.END}")


# --- main -------------------------------------------------------------------

def test_main_leaves_the_tiered_blocks_alone(tmp_path, monkeypatch) -> None:
    _board(tmp_path, [
        _cell("ARM2-N1-carried", "carried-analogue (post-hoc)", 0.8459)])
    before = json.loads((tmp_path / "final_board_50m.json").read_text())
    monkeypatch.setattr(r, "board_home", lambda _ref: tmp_path)
    assert r.main("r2") == 0
    after = json.loads((tmp_path / "final_board_50m.json").read_text())
    for key in ("cells", "tiers", "pairwise"):
        assert after[key] == before[key]
    assert [c["label"] for c in after["addendum_cells"]] == [
        "ARM2-N1-carried"]
    assert after["addendum"]["tiered_cells"] == 1
    assert r.BEGIN in (tmp_path / "final-board-50m.md").read_text()
