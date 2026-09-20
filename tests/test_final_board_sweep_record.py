"""Tier-1 tests for the final board's extended sweep record (PI ruling 2026-09-20).

``scripts/final_board_sweeps.py`` recorded micro-F1 per sweep point and nothing
else, so the text track and the fourth cell could publish no tile-MCC oracle
while the image campaigns published one per rung — the asymmetry
``reports/comparability-inventory-37-runs-2026-09-20.md`` § 1.2 and § 3.7
record. Item 2 of the ruling extends the record with the tile confusion
(``tile_mcc``, ``tile_tp``, ``tile_tn``, ``tile_fp``, ``tile_fn``) and an
``mcc_argmax`` beside the F1 ``argmax``.

These tests pin the three pieces that can silently go wrong:

* the tile confusion must be the **engine's own**, not a second copy of the
  rule — so it is checked against
  ``lib_advanced_metrics.calculate_tile_classification`` on the same frame;
* the MCC argmax's tie-break must match the image script's (lowest operating
  point wins), or the two tracks' oracles are selected differently;
* the carried-k MCC oracle the PI ruled in on 2026-09-20 — the tile-MCC
  optimum over ``prob_t`` at the family's CARRIED vote count — must ignore
  every other vote count, must read that vote count out of the board's own
  ``cells_manifest.json``, and must record ``"no carried k"`` rather than
  guessing for a family with no carried cell (``UPL``, ``A-N1``, ``B-N1``);
* a filtered re-sweep must MERGE into the committed ``sweeps.json``, because
  dropping the families it did not sweep is the 2026-09-13 manifest defect in
  a new guise.

Everything runs over synthetic frames in memory or ``tmp_path``; no committed
board artefact is read and nothing is written outside ``tmp_path``.
"""

from __future__ import annotations

import json

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from scripts import final_board_sweeps as fbs
from scripts.lib_advanced_metrics import calculate_tile_classification

pytestmark = pytest.mark.tier1

TILE_M = 100.0
N_TILES = 6


def _bounds() -> gpd.GeoDataFrame:
    """Six 100 m tiles in a row, named ``t0``..``t5`` (EPSG:32635)."""
    return gpd.GeoDataFrame(
        {"tile_name": [f"t{i}" for i in range(N_TILES)]},
        geometry=[box(i * TILE_M, 0.0, (i + 1) * TILE_M, TILE_M)
                  for i in range(N_TILES)],
        crs="EPSG:32635",
    )


def _centre(i: int) -> Point:
    """The centre point of tile ``i``."""
    return Point((i + 0.5) * TILE_M, TILE_M / 2)


def _points(tile_ids: list[int], with_source_tile: bool) -> gpd.GeoDataFrame:
    """Point rows at the centres of the named tiles."""
    data = ({"source_tile": [f"t{i}" for i in tile_ids]}
            if with_source_tile else {})
    return gpd.GeoDataFrame(data, geometry=[_centre(i) for i in tile_ids],
                            crs="EPSG:32635")


# --- The tile confusion (scripts/final_board_sweeps.tile_confusion) ----------

def test_tile_confusion_counts_the_four_cells() -> None:
    """Reference in t0/t1/t2, detection in t0/t1/t3 -> 2 TP, 1 FN, 1 FP, 2 TN."""
    conf = fbs.tile_confusion(_points([0, 1, 3], True),
                              _points([0, 1, 2], False), _bounds())
    assert (conf["tile_tp"], conf["tile_fn"], conf["tile_fp"],
            conf["tile_tn"]) == (2, 1, 1, 2)
    # MCC = (2*2 - 1*1) / sqrt(3*3*3*3) = 3/9.
    assert conf["tile_mcc"] == pytest.approx(1.0 / 3.0)


def test_tile_confusion_matches_the_engines_own_rule() -> None:
    """The sweep's confusion is the scorer's, not a second copy of the rule.

    A drift here would put the board's MCC oracle on a different tile join
    from the ``--mcc`` evaluation that scores the cell it nominates.
    """
    det, ref, bounds = _points([0, 1, 3], True), _points([0, 1, 2], False), _bounds()
    conf = fbs.tile_confusion(det, ref, bounds)
    engine = calculate_tile_classification(det, ref, bounds)
    assert "error" not in engine
    for key in ("tp", "tn", "fp", "fn"):
        assert conf[f"tile_{key}"] == engine[key]
    assert conf["tile_mcc"] == pytest.approx(engine["mcc"])


def test_tile_confusion_is_null_on_an_empty_point() -> None:
    """A point that retains nothing reports nulls rather than crashing."""
    empty = _points([], True)
    conf = fbs.tile_confusion(empty, _points([0, 1, 2], False), _bounds())
    assert conf == {"tile_mcc": None, "tile_tp": None, "tile_tn": None,
                    "tile_fp": None, "tile_fn": None}


# --- The MCC argmax (scripts/final_board_sweeps.mcc_argmax) ------------------

def _row(prob_t: float, k: int, mcc: float | None) -> dict:
    """One sweep row, reduced to the keys the argmax consults."""
    return {"prob_t": prob_t, "min_votes": k, "tile_mcc": mcc}


def test_mcc_argmax_picks_the_largest() -> None:
    rows = [_row(0.1, 1, 0.50), _row(0.9, 5, 0.71), _row(0.5, 3, 0.64)]
    assert fbs.mcc_argmax(rows) == _row(0.9, 5, 0.71)


def test_mcc_argmax_ties_break_to_the_lowest_operating_point() -> None:
    """The image script's tie-break, so both tracks select an oracle alike."""
    rows = [_row(0.9, 5, 0.70), _row(0.2, 1, 0.70), _row(0.5, 3, 0.70)]
    best = fbs.mcc_argmax(rows)
    assert (best["prob_t"], best["min_votes"]) == (0.2, 1)


def test_mcc_argmax_is_none_without_a_tile_mcc() -> None:
    """A sweep record written before this column existed has no MCC oracle."""
    assert fbs.mcc_argmax([]) is None
    assert fbs.mcc_argmax([{"prob_t": 0.1, "min_votes": 1}]) is None
    assert fbs.mcc_argmax([_row(0.1, 1, None)]) is None


# --- The carried-k MCC oracle (PI ruling 2026-09-20) ------------------------

def test_mcc_argmax_at_carried_k_ignores_every_other_vote_count() -> None:
    """The redefinition in one assertion.

    The unconstrained optimum here is a k = 1 row — exactly the collapse
    the ruling removed — while pinning ``min_votes`` to the carried k
    returns the best row AT that k.
    """
    rows = [_row(0.2, 1, 0.75), _row(0.4, 1, 0.76),
            _row(0.2, 3, 0.72), _row(0.4, 3, 0.73)]
    assert fbs.mcc_argmax(rows) == _row(0.4, 1, 0.76)
    assert fbs.mcc_argmax_at_carried_k(rows, 3) == _row(0.4, 3, 0.73)


def test_mcc_argmax_at_carried_k_ties_break_to_the_lowest_threshold() -> None:
    """Same tie-break as the unconstrained argmax, so the two agree."""
    rows = [_row(0.9, 3, 0.70), _row(0.2, 3, 0.70), _row(0.5, 3, 0.70)]
    assert fbs.mcc_argmax_at_carried_k(rows, 3)["prob_t"] == 0.2


def test_mcc_argmax_at_carried_k_is_none_without_a_usable_carried_k() -> None:
    """UPL, A-N1 and B-N1 have no carried cell on the board."""
    rows = [_row(0.2, 1, 0.75)]
    assert fbs.mcc_argmax_at_carried_k(rows, None) is None
    assert fbs.mcc_argmax_at_carried_k(rows, 4) is None
    assert fbs.mcc_argmax_at_carried_k([_row(0.2, 1, None)], 1) is None


def test_the_two_argmaxes_coincide_on_a_single_vote_family() -> None:
    """An N = 1 family's sweep offers one k, so the redefinition is a no-op."""
    rows = [_row(0.2, 1, 0.72), _row(0.3, 1, 0.75)]
    assert fbs.mcc_argmax_at_carried_k(rows, 1) == fbs.mcc_argmax(rows)


# --- Reading the carried k out of the board's manifest ----------------------

@pytest.mark.parametrize(("label", "family"), [
    ("ARM1-N3-carried", "ARM1-N3"),
    ("A-N10-carried", "A-N10"),
    ("TH7-k4", "TH7"),
    ("IM-k4", "IM"),
    ("ARM2-N5-oracle", None),
    ("TM", None),
])
def test_family_of_carried_label_reads_both_spellings(label, family) -> None:
    assert fbs.family_of_carried_label(label) == family


def _manifest(tmp_path, cells: list[dict]) -> None:
    (tmp_path / "cells_manifest.json").write_text(
        json.dumps({"cells": cells}) + "\n")


def test_carried_k_by_family_takes_every_carried_basis(tmp_path) -> None:
    """Plain carried, emergent post-hoc and carried-analogue all count.

    The 3.7 rungs take their carried k from the carried ANALOGUES the
    2026-09-20 addendum added, which is what the ruling directs.
    """
    _manifest(tmp_path, [
        {"label": "TH7-k4", "basis": "carried", "point": "(0.15, k4)"},
        {"label": "A-N3-carried", "basis": "carried (post-hoc)",
         "point": "(0.15, k3)"},
        {"label": "ARM1-N3-carried", "basis": "carried-analogue (post-hoc)",
         "point": "(0.10, k3)"},
        {"label": "ARM2-N5-oracle", "basis": "oracle (r2-reference argmax)",
         "point": "(0.95, k5)"},
    ])
    got = fbs.carried_k_by_family(tmp_path / "cells_manifest.json")
    assert {f: rec["k"] for f, rec in got.items()} == {
        "TH7": 4, "A-N3": 3, "ARM1-N3": 3}
    assert got["ARM1-N3"]["label"] == "ARM1-N3-carried"


def test_carried_k_by_family_is_empty_without_a_manifest(tmp_path) -> None:
    assert fbs.carried_k_by_family(tmp_path / "nothing.json") == {}


def test_carried_k_by_family_refuses_two_disagreeing_carried_cells(
        tmp_path) -> None:
    """A family cannot have two carried vote counts; silence would pick one."""
    _manifest(tmp_path, [
        {"label": "A-N5-carried", "basis": "carried", "point": "(0.15, k4)"},
        {"label": "A-N5-k5", "basis": "carried", "point": "(0.15, k5)"},
    ])
    with pytest.raises(RuntimeError, match="disagree on k"):
        fbs.carried_k_by_family(tmp_path / "cells_manifest.json")


# --- The record block -------------------------------------------------------

def test_carried_k_record_says_no_carried_k_when_there_is_none() -> None:
    block = fbs.carried_k_record([_row(0.2, 1, 0.7)], None)
    assert block["carried_k"] is None
    assert block["mcc_argmax_at_carried_k"] is None
    assert block["mcc_argmax_at_carried_k_note"] == fbs.NO_CARRIED_K


def test_carried_k_record_flags_when_the_two_optima_coincide() -> None:
    rows = [_row(0.2, 1, 0.72), _row(0.3, 1, 0.75)]
    carried = {"k": 1, "prob_t": 0.1, "label": "X-N1-carried",
               "basis": "carried-analogue (post-hoc)"}
    block = fbs.carried_k_record(rows, carried)
    assert block["mcc_argmax_at_carried_k_is_unconstrained"] is True
    assert block["carried_k_source"] == "X-N1-carried"
    assert block["mcc_argmax_at_carried_k_note"] is None


def test_carried_k_record_flags_when_they_differ() -> None:
    rows = [_row(0.2, 1, 0.75), _row(0.2, 3, 0.72)]
    carried = {"k": 3, "prob_t": 0.1, "label": "X-N3-carried",
               "basis": "carried"}
    block = fbs.carried_k_record(rows, carried)
    assert block["mcc_argmax_at_carried_k_is_unconstrained"] is False
    assert block["mcc_argmax_at_carried_k"]["min_votes"] == 3


# --- Reading the committed CSVs back ----------------------------------------

def test_read_sweep_csv_restores_the_row_types(tmp_path) -> None:
    """``--record-carried-k`` recomputes from the CSVs, so types must survive."""
    path = tmp_path / "sweep_X.csv"
    path.write_text(
        "family,prob_t,min_votes,n_detections,tp,fp,fn,micro_f1_50,"
        "tile_mcc,tile_tp,tile_tn,tile_fp,tile_fn\n"
        "X,0.15,3,4786,4108,678,910,0.8380252957976336,0.679178,"
        "2424,4772,240,1105\n")
    row = fbs.read_sweep_csv(path)[0]
    assert row["prob_t"] == pytest.approx(0.15)
    assert row["min_votes"] == 3 and row["n_detections"] == 4786
    assert row["tile_tp"] == 2424
    assert row["micro_f1_50"] == pytest.approx(0.8380252957976336)


def test_read_sweep_csv_keeps_integer_counts_exact(tmp_path) -> None:
    """The board writes whole numbers and they must stay whole."""
    path = tmp_path / "sweep_X.csv"
    path.write_text("family,prob_t,min_votes,n_detections,tp,fp,fn\n"
                    "X,0.15,3,4786,4108,678,910\n")
    row = fbs.read_sweep_csv(path)[0]
    assert isinstance(row["tp"], int) and row["tp"] == 4108


def test_read_sweep_csv_accepts_the_image_campaigns_float_counts(
        tmp_path) -> None:
    """The image sweeps sum numpy arrays, so tp/fp/fn are written as floats.

    The tile-presence builder reads both spellings; a blanket int() here
    crashed on 4870.0 the first time it did (2026-09-21).
    """
    path = tmp_path / "sweep_X.csv"
    path.write_text("rung,prob_t,min_votes,n_detections,tp,fp,fn\n"
                    "X,0.9,3,5343,4870.0,473.0,148.0\n")
    row = fbs.read_sweep_csv(path)[0]
    assert row["tp"] == pytest.approx(4870.0)
    assert row["n_detections"] == 5343


def test_read_sweep_csv_reads_an_empty_metric_as_none(tmp_path) -> None:
    """A point that retained nothing is written with blank metrics."""
    path = tmp_path / "sweep_X.csv"
    path.write_text("family,prob_t,min_votes,n_detections,micro_f1_50,"
                    "tile_mcc\nX,1.0,3,0,,\n")
    row = fbs.read_sweep_csv(path)[0]
    assert row["micro_f1_50"] is None and row["tile_mcc"] is None


# --- The record's index keys ------------------------------------------------

def test_stamp_record_indexes_both_oracle_families() -> None:
    sweeps = {"families": {
        "WITH": {"mcc_argmax": _row(0.2, 1, 0.7),
                 "mcc_argmax_at_carried_k": _row(0.2, 3, 0.6)},
        "UNCONSTRAINED-ONLY": {"mcc_argmax": _row(0.2, 1, 0.7),
                               "mcc_argmax_at_carried_k": None},
        "NEITHER": {"mcc_argmax": None, "mcc_argmax_at_carried_k": None},
    }}
    fbs.stamp_record(sweeps)
    assert sweeps["mcc_families"] == ["UNCONSTRAINED-ONLY", "WITH"]
    assert sweeps["mcc_carried_k_families"] == ["WITH"]
    assert "unconstrained" in sweeps["_README"].lower()


# --- The filtered-run merge (scripts/final_board_sweeps.load_sweeps) ---------

def test_load_sweeps_keeps_the_families_a_filtered_run_did_not_sweep(
        tmp_path) -> None:
    path = tmp_path / "sweeps.json"
    path.write_text(json.dumps({
        "buffer_m": 50, "reference": "r2",
        "families": {"ARM1-N1": {"n_sweep_points": 19},
                     "A-N10": {"n_sweep_points": 200}}}) + "\n")
    sweeps = fbs.load_sweeps(path, "r2")
    sweeps["families"]["ARM1-N1"] = {"n_sweep_points": 19, "mcc_argmax": {}}
    assert set(sweeps["families"]) == {"ARM1-N1", "A-N10"}
    assert sweeps["families"]["A-N10"] == {"n_sweep_points": 200}


def test_load_sweeps_returns_a_fresh_record_when_absent(tmp_path) -> None:
    sweeps = fbs.load_sweeps(tmp_path / "nothing.json", "r2")
    assert sweeps == {"buffer_m": fbs.BUFFER_M, "reference": "r2",
                      "families": {}}


def test_load_sweeps_repairs_a_missing_families_block(tmp_path) -> None:
    path = tmp_path / "sweeps.json"
    path.write_text(json.dumps({"buffer_m": 50, "reference": "r2"}) + "\n")
    assert fbs.load_sweeps(path, "r2")["families"] == {}


# --- The manifest carry-forward (scripts/final_board_sweeps.main) -----------
#
# Stage 1 rebuilds cells_manifest.json from its own output, so every cell
# another step appended has to be carried forward or it is dropped — the
# 2026-09-13 defect. The guard used to match the substring "post-hoc", which
# every basis then in use happened to contain; the PI ruling of 2026-09-21
# re-labelled twenty cells to bases that do not, so the match is now "any
# committed label this run did not produce".

def _carry_forward(produced_labels: list[str], prior: list[dict]) -> list[str]:
    """The carry-forward rule, isolated from the stage that runs it."""
    produced = set(produced_labels)
    return [c["label"] for c in prior if c["label"] not in produced]


def test_carry_forward_keeps_a_cell_whose_basis_says_nothing_about_post_hoc(
) -> None:
    """The 2026-09-21 bases: the guard must not depend on a word."""
    prior = [
        {"label": "ARM2-N3-mcc-oracle",
         "basis": "tile-presence oracle (unconstrained tile-MCC optimum; "
                  "presented in results/tile-presence-2026-09-21/)"},
        {"label": "ARM2-N3-mcc-oracle-k3",
         "basis": "mcc-oracle at carried k — retained, not presented "
                  "(PI ruling 2026-09-21)"},
        {"label": "A-N3-carried", "basis": "carried (post-hoc)"},
    ]
    assert _carry_forward(["ARM2-N5-oracle"], prior) == [
        "ARM2-N3-mcc-oracle", "ARM2-N3-mcc-oracle-k3", "A-N3-carried"]


def test_carry_forward_does_not_duplicate_a_cell_this_run_produced() -> None:
    prior = [{"label": "A-N3-carried", "basis": "carried (post-hoc)"}]
    assert _carry_forward(["A-N3-carried"], prior) == []
