"""Tier-1 test: the top-N filter records and logs what it drops (S151-d).

A regression rebuild of a 44-cell board silently produced 26 because the
builder's default top-N filter logged only counts at INFO. Dropping lower
cells from the tiered board is acceptable; dropping them silently is not.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from scripts import build_tiered_leaderboard as b

pytestmark = pytest.mark.tier1


def _cond(label: str) -> b.ConditionSpec:
    return b.ConditionSpec(label=label, geojson_paths=[Path(f"/x/{label}.geojson")], thresholds=[1],
                           era=2, track="text", category="pv", k=5, condition_id=f"run::{label}", metadata={})


def _evals(f1_by_label: dict[str, float]) -> dict:
    return {label: {1: {"buffers": [{"buffer_metres": 20, "f1": f1}]}} for label, f1 in f1_by_label.items()}


def test_top_n_drop_is_logged_and_recorded(caplog):
    conds = [_cond("a"), _cond("b"), _cond("c")]
    evals = _evals({"a": 0.9, "b": 0.8, "c": 0.7})
    dropped: list[dict] = []
    with caplog.at_level(logging.WARNING, logger=b.logger.name):
        selected = b.select_best_thresholds(conds, evals, primary_buffer=20, top_n=2,
                                            dropped_by_top_n_out=dropped)
    assert [s.label for s in selected] == ["a", "b"]
    assert dropped == [{"label": "c", "condition_id": "run::c", "best_threshold": 1, "f1_primary": 0.7}]
    assert any("DROPPED 1 condition" in r.getMessage() and "c (F1@20m=0.7000)" in r.getMessage()
               for r in caplog.records)


def test_top_n_zero_keeps_everything_and_records_nothing():
    conds = [_cond("a"), _cond("b"), _cond("c")]
    dropped: list[dict] = []
    selected = b.select_best_thresholds(conds, _evals({"a": 0.9, "b": 0.8, "c": 0.7}), primary_buffer=20,
                                        top_n=0, dropped_by_top_n_out=dropped)
    assert len(selected) == 3 and dropped == []
