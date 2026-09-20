"""
Tier-1 tests for the pure logic of ``scripts/t5m_matched_comparator.py``.

The script's measurement is gated at run time against the committed sweep row
and against the committed declared-T5 result, which are stronger checks than a
fixture could be and need the real reference frames. What is tested here is
the logic no committed artefact would catch: that the matched cell is pinned
to IM-k3's own threshold rather than to an oracle, that the oracle twin is
read off the sweep at three votes and nowhere else, that a sweep missing the
matched point is refused rather than silently substituted, and that the
declared-T5 reproduction gate is exact rather than tolerant — a tolerant gate
would pass a pipeline that is merely close to the one that produced
``tests_2x2_K3.json``.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pytest

from scripts import t5m_matched_comparator as t5m

pytestmark = pytest.mark.tier1

#: The sweep columns ``sweep_rows`` reads, in the 2x2 sweep file's own order.
CSV_FIELDS = [
    "rung", "prob_t", "min_votes", "n_detections", "tp", "fp", "fn",
    "micro_f1_50", "tile_mcc", "tile_tp", "tile_tn", "tile_fp", "tile_fn",
]


def _row(prob_t: float, min_votes: int, f1: float, n: int = 100) -> dict[str, Any]:
    """One sweep row with plausible, internally unimportant counts."""
    return {
        "rung": t5m.RUNG_LABEL, "prob_t": prob_t, "min_votes": min_votes,
        "n_detections": n, "tp": 10.0, "fp": 5.0, "fn": 5.0,
        "micro_f1_50": f1, "tile_mcc": 0.5,
        "tile_tp": 4, "tile_tn": 4, "tile_fp": 1, "tile_fn": 1,
    }


def _write_sweep(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write a sweep CSV with the real file's columns."""
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_the_matched_cell_is_pinned_to_im_k3_s_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The carried cell is IM-k3's own point, never the rung's best row."""
    sweep = tmp_path / "sweep.csv"
    _write_sweep(sweep, [
        _row(0.15, 3, 0.7312, n=7222),
        _row(0.20, 3, 0.7357, n=6974),
        _row(0.40, 3, 0.7305, n=6316),
    ])
    monkeypatch.setattr(t5m, "SWEEP_CSV", sweep)
    carried, _oracle = t5m.cell_specs()
    assert carried["label"] == t5m.CARRIED_LABEL
    assert carried["prob_t"] == pytest.approx(0.15), (
        "the matched comparator must sit at IM-k3's threshold, so the two "
        "cells differ in the pool and not in the operating point")
    assert carried["min_votes"] == 3
    assert carried["row"]["n_detections"] == 7222


def test_the_oracle_twin_is_the_best_f1_row_at_three_votes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The oracle is read off the sweep, and only from the three-vote rows."""
    sweep = tmp_path / "sweep.csv"
    _write_sweep(sweep, [
        _row(0.15, 3, 0.7312, n=7222),
        _row(0.20, 3, 0.7357, n=6974),
        # A better F1 at a vote count IM-k3 cannot match must be ignored.
        _row(0.15, 5, 0.8177, n=4858),
    ])
    monkeypatch.setattr(t5m, "SWEEP_CSV", sweep)
    _carried, oracle = t5m.cell_specs()
    assert oracle["label"] == t5m.ORACLE_LABEL
    assert oracle["prob_t"] == pytest.approx(0.20)
    assert oracle["min_votes"] == 3
    assert oracle["row"]["micro_f1_50"] == pytest.approx(0.7357), (
        "a five-vote row must not win the three-vote oracle: IM-k3 is a "
        "three-vote cell and the match is the whole point of T5m")


def test_a_sweep_without_the_matched_point_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No nearest-neighbour substitution: the matched point exists or it stops."""
    sweep = tmp_path / "sweep.csv"
    _write_sweep(sweep, [_row(0.20, 3, 0.7357), _row(0.40, 3, 0.7305)])
    monkeypatch.setattr(t5m, "SWEEP_CSV", sweep)
    with pytest.raises(SystemExit):
        t5m.cell_specs()


def test_the_declared_t5_gate_is_exact_not_tolerant() -> None:
    """One unit in the last place is a different input, not a rounding artefact."""
    committed = {"observed_diff": 0.001604, "p_value": 0.7604, "null_mean": 6e-06,
                 "null_std": 0.005177, "n_tiles": 8541, "f1_a": 0.802387,
                 "f1_b": 0.800784}
    assert t5m._check_reproduction("f1", dict(committed), committed) == []
    drifted = dict(committed, observed_diff=0.001605)
    failures = t5m._check_reproduction("f1", drifted, committed)
    assert len(failures) == 1
    assert "observed_diff" in failures[0]


def test_the_records_place_im_k3_outside_the_campaign_manifest() -> None:
    """IM-k3's record points at its own file, not at a campaign cell."""
    by_label = {
        t5m.CARRIED_LABEL: {"det": "results/x/carried.geojson", "point": "(0.15, k3)"},
        t5m.ORACLE_LABEL: {"det": "results/x/oracle.geojson", "point": "(0.20, k3)"},
        t5m.DECLARED_T5_CELL: {"det": "results/y/declared.geojson",
                               "point": "(0.15, k3)"},
    }
    cells = {label: {"n": 1, "confusion": {"tp": 1, "tn": 1, "fp": 0, "fn": 0}}
             for label in (*by_label, "IM-k3")}

    class _Comparator:
        detections = "outputs/55maps-image-generalisation/verified/x.geojson"

    records = t5m.cell_records(by_label, cells, _Comparator())
    assert records["IM-k3"]["det"] == _Comparator.detections
    assert records["IM-k3"]["point"] == "(0.15, k3)"
    assert set(records) == {*by_label, "IM-k3"}
