"""Tier-1 tests for the vintage guard in ``scripts/materialise_opmax_cells.py``.

The guard exists because the ``-opmax`` filter joins a proposer union to a
verifier's ``probabilities.json`` by candidate INDEX, and that join is
meaningful only while the union still holds the features, in the order, the
verifier cropped. When it does not, the join fails soft and returns a
plausible count that is not an operating point (``pv-high-text-t0.0-n3``:
410 against a registered 403, 2026-09-11).

These tests pin the classifier's three verdicts and the sweep-universe reader
that feeds it. Both are pure functions over already-parsed inputs, so no
board directory, register or geo stack is touched.
"""

from __future__ import annotations

import json

import pytest

from scripts import materialise_opmax_cells as m

pytestmark = pytest.mark.tier1


@pytest.mark.parametrize(
    "n_union, n_probabilities, n_sweep, expected",
    [
        (2954, 2954, 2954, "same-vintage"),
        # The probabilities were completed after the sweep ran: the union is
        # untouched, so the index join is still sound (Obs 461 class).
        (2190, 2190, 2179, "probabilities-grew"),
        # The union grew past what the stage verified: order no longer matches
        # the keys, so no count derived from the join means anything.
        (1319, 1256, 1256, "union-rebuilt"),
        # A rebuilt union is caught even without a sweep to compare against.
        (1319, 1256, None, "union-rebuilt"),
        (690, 690, None, "unknown"),
        # A sweep LARGER than the union is not a shape the classifier claims
        # to understand; it must say so rather than pass the row.
        (500, 500, 600, "unknown"),
    ],
)
def test_classify_vintage_names_the_failure_mode(n_union, n_probabilities, n_sweep, expected):
    verdict, why = m.classify_vintage(n_union, n_probabilities, n_sweep)
    assert verdict == expected
    assert why


def test_union_rebuilt_is_decided_before_the_sweep_is_consulted():
    """A rebuilt union outranks any sweep evidence: the join is invalid either way."""
    assert m.classify_vintage(1319, 1256, 1319)[0] == "union-rebuilt"


def _write_sweep(tmp_path, rows):
    path = tmp_path / "sweep_2d.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


def test_sweep_universe_reads_the_all_candidates_cell(tmp_path, monkeypatch):
    """``n`` at (vote_t 1, prob_t 0.0) keeps every candidate, so it IS the universe."""
    _write_sweep(tmp_path, [
        {"vote_t": 1, "prob_t": 0.0, "n": 1256, "buffer_m": 20},
        {"vote_t": 1, "prob_t": 0.05, "n": 887, "buffer_m": 20},
        # A different buffer's identical cell must not be read instead.
        {"vote_t": 1, "prob_t": 0.0, "n": 9999, "buffer_m": 50},
    ])
    monkeypatch.setattr(m, "REPO_ROOT", tmp_path)
    assert m.sweep_universe("sweep_2d.json") == 1256


def test_sweep_universe_defaults_a_buffer_less_row_to_20_m(tmp_path, monkeypatch):
    """Older sweeps predate the ``buffer_m`` tag and are single-buffer at 20 m."""
    path = _write_sweep(tmp_path, [{"vote_t": 1, "prob_t": 0.0, "n": 412}])
    monkeypatch.setattr(m, "REPO_ROOT", tmp_path)
    assert m.sweep_universe(path.name) == 412


def test_sweep_universe_is_none_when_there_is_nothing_to_read(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "REPO_ROOT", tmp_path)
    assert m.sweep_universe(None) is None
    assert m.sweep_universe("absent.json") is None
    _write_sweep(tmp_path, [{"vote_t": 2, "prob_t": 0.0, "n": 300, "buffer_m": 20}])
    assert m.sweep_universe("sweep_2d.json") is None
