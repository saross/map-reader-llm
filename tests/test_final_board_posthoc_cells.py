"""Tier-1 tests for the board's post-hoc addendum cells (PI ruling 2026-09-20).

``scripts/final_board_posthoc_cells.py`` materialises two sets of cells the
stage-1 sweep swept but never built:

* the seven **carried-analogue** rungs of the 3.7 families — each family's
  top-rung GS-carried probability applied downward, with ``k`` set to the
  rung's own N (ruling item 1;
  ``reports/comparability-inventory-37-runs-2026-09-20.md`` § 3.2);
* the ten **tile-MCC oracles** of the same families, read from
  ``sweeps.json``'s ``mcc_argmax`` (ruling item 2, § 3.7) — superseded
  2026-09-20 and relabelled, not deleted;
* the ten **carried-k tile-MCC oracles** that replaced them, read from
  ``mcc_argmax_at_carried_k`` and labelled
  ``<family>-mcc-oracle-k<carried>``.

The derivation is the part worth pinning: the rung set and the threshold are
derived from ``final_board_sweeps.G37_IDENTITY``, the table the stage-1
identity gate enforces, so a hand-typed point cannot drift away from the one
the board actually carried. These tests hold that derivation, the basis
labels the regeneration carry-forward matches on, and the two refusals.

Everything runs over synthetic records in ``tmp_path``; no committed board
artefact is read and nothing is written outside it.
"""

from __future__ import annotations

import json

import pytest

from scripts import final_board_posthoc_cells as ph

pytestmark = pytest.mark.tier1

#: The seven cells the ruling names, as (label, prob_t, min_votes).
EXPECTED_CARRIED = {
    ("ARM2-N1-carried", 0.80, 1),
    ("ARM2-N3-carried", 0.80, 3),
    ("ARM1-N1-carried", 0.10, 1),
    ("ARM1-N3-carried", 0.10, 3),
    ("FOURTH-N1-carried", 0.98, 1),
    ("FOURTH-N3-carried", 0.98, 3),
    ("FOURTH-N5-carried", 0.98, 5),
}


# --- The carried-analogue derivation ----------------------------------------

def test_carried_analogue_points_are_the_seven_the_ruling_names() -> None:
    got = {(label, pt, k) for _f, label, pt, k, _n in
           ph.carried_analogue_points()}
    assert got == EXPECTED_CARRIED


def test_carried_analogue_rungs_follow_k_max_not_a_list() -> None:
    """The arms stop at N = 3 and the fourth cell reaches N = 5.

    The rung set is derived from each family's ``k_max`` (5 for the arms,
    10 for the fourth cell), so the asymmetry cannot drift back in.
    """
    by_stem: dict[str, set[int]] = {}
    for family, _label, _pt, k, _note in ph.carried_analogue_points():
        by_stem.setdefault(family.rsplit("-N", 1)[0], set()).add(k)
    assert by_stem == {"ARM1": {1, 3}, "ARM2": {1, 3}, "FOURTH": {1, 3, 5}}


def test_carried_analogue_threshold_is_the_top_rungs_carried_point() -> None:
    """Every analogue reuses its own family's top-rung GS-carried threshold."""
    from scripts.final_board_sweeps import G37_IDENTITY
    top = {f.rsplit("-N", 1)[0]: pt for f, ((pt, _k), _n) in
           G37_IDENTITY.items()}
    for family, _label, pt, _k, _note in ph.carried_analogue_points():
        assert pt == top[family.rsplit("-N", 1)[0]]


def test_carried_analogue_notes_say_what_the_point_is_and_when_it_landed(
) -> None:
    for _f, _label, _pt, _k, note in ph.carried_analogue_points():
        assert "applied downward" in note
        assert "2026-09-20" in note
        assert "Post-hoc" in note


def test_every_basis_label_carries_the_post_hoc_marker() -> None:
    """``final_board_sweeps`` carries a cell forward by matching "post-hoc".

    A label without it would be dropped from ``cells_manifest.json`` the
    next time stage 1 regenerated the board — the 2026-09-13 defect.
    """
    assert all("post-hoc" in basis for basis in ph.BASIS.values())


def test_the_published_f1_cross_check_covers_every_carried_cell() -> None:
    labels = {label for _f, label, _pt, _k, _n in ph.carried_analogue_points()}
    assert set(ph.CARRIED_ANALOGUE_F1) == labels


# --- The sweep-row lookup ----------------------------------------------------

def _csv(tmp_path, family: str, rows: list[tuple[float, int, int, float]]):
    """Write a minimal ``sweep_<family>.csv`` and return its directory."""
    lines = ["family,prob_t,min_votes,n_detections,micro_f1_50"]
    lines += [f"{family},{pt},{k},{n},{f1}" for pt, k, n, f1 in rows]
    (tmp_path / f"sweep_{family}.csv").write_text("\n".join(lines) + "\n")
    return tmp_path


def test_sweep_row_finds_the_point(tmp_path) -> None:
    out = _csv(tmp_path, "ARM2-N1", [(0.0, 1, 8372, 0.6993),
                                     (0.8, 1, 5936, 0.8459)])
    row = ph.sweep_row(out, "ARM2-N1", 0.80, 1)
    assert int(row["n_detections"]) == 5936
    assert float(row["micro_f1_50"]) == pytest.approx(0.8459)


def test_sweep_row_refuses_a_point_the_sweep_never_scored(tmp_path) -> None:
    out = _csv(tmp_path, "ARM2-N1", [(0.0, 1, 8372, 0.6993)])
    with pytest.raises(SystemExit, match="no sweep row"):
        ph.sweep_row(out, "ARM2-N1", 0.80, 1)


# --- The MCC-oracle set ------------------------------------------------------

def _sweeps(tmp_path, families: dict) -> None:
    (tmp_path / "sweeps.json").write_text(
        json.dumps({"buffer_m": 50, "reference": "r2",
                    "families": families}) + "\n")


def test_mcc_oracle_points_refuse_a_record_without_an_mcc_argmax(
        tmp_path) -> None:
    """The sweep must have been re-run with the extended record first."""
    _sweeps(tmp_path, {"ARM2-N1": {"argmax": {"micro_f1_50": 0.861}}})
    with pytest.raises(SystemExit, match="no mcc_argmax"):
        ph.mcc_oracle_points(tmp_path)


def test_mcc_oracle_points_ignore_families_outside_the_ruling(
        tmp_path) -> None:
    """A/B and the incumbents are not part of this addendum."""
    rec = {"argmax": {"micro_f1_50": 0.861},
           "mcc_argmax": {"prob_t": 0.96, "min_votes": 1, "tile_mcc": 0.747}}
    _sweeps(tmp_path, {"ARM2-N1": rec, "FOURTH-N10": rec,
                       "A-N10": {"argmax": {"micro_f1_50": 0.84}},
                       "TH7": {"argmax": {"micro_f1_50": 0.83}}})
    got = ph.mcc_oracle_points(tmp_path)
    assert [label for _f, label, _pt, _k, _n in got] == [
        "ARM2-N1-mcc-oracle", "FOURTH-N10-mcc-oracle"]
    assert all(pt == 0.96 and k == 1 for _f, _l, pt, k, _n in got)
    assert all("2026-09-20" in note for *_rest, note in got)


# --- The carried-k MCC-oracle set (PI ruling 2026-09-20) --------------------

def _carried_k_record(carried_k: int, at_k: tuple[float, int],
                      free: tuple[float, int]) -> dict:
    """One family's record, reduced to what the carried-k set reads."""
    return {
        "argmax": {"micro_f1_50": 0.8818},
        "carried_k": carried_k,
        "carried_k_source": f"X-N{carried_k}-carried",
        "mcc_argmax": {"prob_t": free[0], "min_votes": free[1],
                       "tile_mcc": 0.7475, "micro_f1_50": 0.8245},
        "mcc_argmax_at_carried_k": {"prob_t": at_k[0], "min_votes": at_k[1],
                                    "tile_mcc": 0.7326,
                                    "micro_f1_50": 0.8818},
    }


def test_carried_k_points_name_the_carried_k_in_the_label(tmp_path) -> None:
    """``<family>-mcc-oracle-k<carried>`` can never be read as the old cell."""
    _sweeps(tmp_path, {
        "ARM2-N3": _carried_k_record(3, (0.96, 3), (0.96, 1)),
        "ARM2-N1": _carried_k_record(1, (0.96, 1), (0.96, 1)),
        "A-N10": {"argmax": {"micro_f1_50": 0.84}},
    })
    got = ph.mcc_oracle_at_carried_k_points(tmp_path)
    assert [(label, pt, k) for _f, label, pt, k, _n in got] == [
        ("ARM2-N1-mcc-oracle-k1", 0.96, 1),
        ("ARM2-N3-mcc-oracle-k3", 0.96, 3)]


def test_carried_k_points_refuse_a_record_without_the_field(tmp_path) -> None:
    """``final_board_sweeps.py --record-carried-k`` has to have run first."""
    _sweeps(tmp_path, {"ARM2-N1": {"argmax": {"micro_f1_50": 0.861},
                                   "mcc_argmax": {"prob_t": 0.96}}})
    with pytest.raises(SystemExit, match="no mcc_argmax_at_carried_k"):
        ph.mcc_oracle_at_carried_k_points(tmp_path)


def test_carried_k_points_refuse_a_family_with_no_carried_k(tmp_path) -> None:
    """Null means the family has no carried cell; guessing one is the defect."""
    rec = _carried_k_record(3, (0.96, 3), (0.96, 1))
    rec["mcc_argmax_at_carried_k"] = None
    rec["carried_k"] = None
    _sweeps(tmp_path, {"ARM2-N3": rec})
    with pytest.raises(SystemExit, match="no carried k on this board"):
        ph.mcc_oracle_at_carried_k_points(tmp_path)


def test_carried_k_notes_name_the_superseded_point(tmp_path) -> None:
    """A reader of the manifest must be able to find the retained evidence."""
    _sweeps(tmp_path, {"ARM2-N3": _carried_k_record(3, (0.96, 3), (0.96, 1))})
    (_f, _label, _pt, _k, note), = ph.mcc_oracle_at_carried_k_points(tmp_path)
    assert "carried" in note and "k3" in note
    assert "ARM2-N3-mcc-oracle" in note
    assert "UNCONSTRAINED" in note


# --- Relabelling the superseded cells ---------------------------------------

def test_relabel_touches_only_the_unconstrained_mcc_cells() -> None:
    manifest = {"cells": [
        {"label": "ARM2-N3-mcc-oracle", "basis": ph.BASIS["mcc-oracle"]},
        {"label": "ARM2-N3-mcc-oracle-k3",
         "basis": ph.BASIS["mcc-oracle-at-carried-k"]},
        {"label": "ARM2-N3-carried", "basis": ph.BASIS["carried-analogue"]},
        {"label": "ARM2-N3-oracle", "basis": "oracle (r2-reference argmax)"},
    ]}
    assert ph.relabel_superseded_mcc_cells(manifest) == ["ARM2-N3-mcc-oracle"]
    by_label = {c["label"]: c["basis"] for c in manifest["cells"]}
    assert by_label["ARM2-N3-mcc-oracle"] == ph.SUPERSEDED_MCC_BASIS
    assert by_label["ARM2-N3-carried"] == ph.BASIS["carried-analogue"]
    assert by_label["ARM2-N3-oracle"] == "oracle (r2-reference argmax)"


def test_relabelling_is_idempotent() -> None:
    """A second run must not re-flag a cell that is already superseded."""
    manifest = {"cells": [{"label": "X-mcc-oracle",
                           "basis": ph.BASIS["mcc-oracle"]}]}
    ph.relabel_superseded_mcc_cells(manifest)
    assert ph.relabel_superseded_mcc_cells(manifest) == []


def test_the_superseded_basis_keeps_the_post_hoc_marker() -> None:
    """Otherwise a board regeneration would drop the retained evidence."""
    assert "post-hoc" in ph.SUPERSEDED_MCC_BASIS
    assert "superseded" in ph.SUPERSEDED_MCC_BASIS
