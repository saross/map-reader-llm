"""Tests for the tile-metric point backfill and batch roll-up rebuild (D30)."""

from __future__ import annotations

import pytest

from scripts.backfill_tile_point_estimates import (
    backfill_block,
    backfill_doc,
    points_from_confusion,
)

pytestmark = pytest.mark.tier1


def test_points_from_confusion_matches_known_block():
    """Recomputation reproduces a committed worked example exactly.

    The 188/247/11/41 table is the corrected derivation in
    docs/methodology/tile-mcc-explained.md (MCC 0.7903).
    """
    pts = points_from_confusion({"tp": 188, "tn": 247, "fp": 11, "fn": 41})
    assert pts["mcc"] == 0.7903
    assert pts["sensitivity"] == round(188 / 229, 4)
    assert pts["specificity"] == round(247 / 258, 4)


def test_vanishing_marginal_yields_none_not_zero():
    """E81: a degenerate confusion matrix must never backfill a 0.

    With no detections at all, the predicted-positive marginal (tp + fp)
    vanishes, so MCC is undefined; sensitivity and specificity remain
    defined and genuinely zero-or-one valued.
    """
    pts = points_from_confusion({"tp": 0, "tn": 20, "fp": 0, "fn": 5})
    assert pts["mcc"] is None
    assert pts["sensitivity"] == 0.0  # tp/(tp+fn) defined: 0/5
    assert pts["specificity"] == 1.0  # tn/(tn+fp) defined: 20/20


def test_backfill_only_touches_pointless_blocks():
    tc = {
        "confusion": {"tp": 188, "tn": 247, "fp": 11, "fn": 41},
        "mcc": {"mean": 0.79, "ci_lower": 0.7, "ci_upper": 0.85},
        "sensitivity": {"point": 0.9, "mean": 0.89},
        "specificity": {"mean": 0.95},
    }
    n = backfill_block(tc)
    assert n == 2  # mcc and specificity gain a point; sensitivity untouched
    assert tc["mcc"]["point"] == 0.7903
    assert tc["sensitivity"]["point"] == 0.9
    assert backfill_block(tc) == 0  # idempotent


def test_backfill_doc_covers_summary_and_per_run():
    conf = {"tp": 188, "tn": 247, "fp": 11, "fn": 41}
    doc = {
        "summary": {"tile_classification": {
            "confusion": conf, "mcc": {"mean": 0.79}}},
        "per_run": [{"tile_classification": {
            "confusion": conf, "mcc": {"mean": 0.78}}}],
    }
    assert backfill_doc(doc) == 2
    assert doc["summary"]["tile_classification"]["mcc"]["point"] == 0.7903
    assert doc["per_run"][0]["tile_classification"]["mcc"]["point"] == 0.7903
