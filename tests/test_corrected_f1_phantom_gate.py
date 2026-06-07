"""
Tests for build_phantom_gdf's buffer gating in compute_corrected_f1_multi_buffer.

Tier 1 unit tests covering the yesterday-review gate added 2026-06-07: a
multi-buffer review passed as "yesterday" must have its mounds gated by
``buffer_metres <= R`` (like "today"), so wider-ring (>R) mounds are not
over-promoted at R = 50 m. Single-buffer (all 50 m) and empty yesterday
reviews must be unaffected at R >= 50 (so published numbers are unchanged).
"""

import pandas as pd
import pytest

from scripts.compute_corrected_f1_multi_buffer import build_phantom_gdf


def _review(rows: list[dict]) -> pd.DataFrame:
    """Build a minimal review DataFrame with the columns the helper needs."""
    cols = ["candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"]
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows, columns=cols)


@pytest.mark.tier1
def test_multibuffer_yesterday_is_gated_by_R():
    """Yesterday's >R mounds are excluded at R (the fix)."""
    yesterday = _review([
        {"candidate_id": 0, "human_label": "mound", "buffer_metres": 50,
         "x": 1.0, "y": 1.0, "map_name": "K-1"},
        {"candidate_id": 1, "human_label": "mound", "buffer_metres": 75,
         "x": 2.0, "y": 2.0, "map_name": "K-1"},
        {"candidate_id": 2, "human_label": "mound", "buffer_metres": 125,
         "x": 3.0, "y": 3.0, "map_name": "K-1"},
    ])
    today = _review([])
    # At R = 50, only the 50 m yesterday mound qualifies.
    g50 = build_phantom_gdf(yesterday, today, buffer_r=50)
    assert len(g50) == 1
    assert set(g50["buffer_metres"]) == {50}
    # At R = 125, all three qualify.
    g125 = build_phantom_gdf(yesterday, today, buffer_r=125)
    assert len(g125) == 3


@pytest.mark.tier1
def test_single_buffer_yesterday_is_noop_at_R50():
    """A single-buffer (all 50 m) yesterday is unchanged at R = 50 (published
    corrected-F1 used exactly this shape — must not regress)."""
    yesterday = _review([
        {"candidate_id": i, "human_label": "mound", "buffer_metres": 50,
         "x": float(i), "y": float(i), "map_name": "K-1"} for i in range(4)
    ])
    today = _review([])
    g = build_phantom_gdf(yesterday, today, buffer_r=50)
    assert len(g) == 4


@pytest.mark.tier1
def test_empty_yesterday_yields_no_phantoms():
    """An empty yesterday (the published text-high shape) yields no
    yesterday-side phantoms; today still contributes."""
    yesterday = _review([])
    today = _review([
        {"candidate_id": 0, "human_label": "mound", "buffer_metres": 50,
         "x": 1.0, "y": 1.0, "map_name": "K-1"},
        {"candidate_id": 1, "human_label": "not_mound", "buffer_metres": 50,
         "x": 2.0, "y": 2.0, "map_name": "K-1"},
    ])
    g = build_phantom_gdf(yesterday, today, buffer_r=50)
    # only the today mound (not the not_mound) is promoted
    assert len(g) == 1
