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
