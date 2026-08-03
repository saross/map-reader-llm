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


# ---------------------------------------------------------------------------
# Coincidence de-duplication in build_extended_gt (Session 126, W6-E9): a
# rescue entering through BOTH channels (review-CSV mound row AND a curator
# point later added to the student layer at the same coordinates) must be
# counted once — the phantom is dropped, the student point kept. Without
# this, one-to-one Hungarian matching books the twin as a spurious FN and
# recall falls from a rescue (the cand-2397 case).
# ---------------------------------------------------------------------------

import geopandas as gpd
from shapely.geometry import Point

from scripts.compute_corrected_f1_multi_buffer import build_extended_gt


def _student(points: list[tuple[str, float, float]]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"source_map": [m for m, _, _ in points]},
        geometry=[Point(x, y) for _, x, y in points],
        crs="EPSG:32635",
    )


def _phantoms(points: list[tuple[str, float, float]]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {
            "candidate_id": list(range(len(points))),
            "source_map": [m for m, _, _ in points],
            "human_label": ["mound"] * len(points),
            "buffer_metres": [50] * len(points),
        },
        geometry=[Point(x, y) for _, x, y in points],
        crs="EPSG:32635",
    )


@pytest.mark.tier1
def test_extended_gt_drops_exact_coordinate_twin_same_map():
    """A phantom at a same-map student point's coordinates is dropped."""
    student = _student([("K-1", 100.0, 100.0), ("K-1", 500.0, 500.0)])
    phantoms = _phantoms([("K-1", 100.0, 100.0), ("K-1", 900.0, 900.0)])
    ext = build_extended_gt(student, phantoms)
    assert len(ext) == 3  # 2 student + 1 surviving phantom
    assert ext.attrs["n_phantom_duplicates_dropped"] == 1
    # The student side is untouched.
    assert int((~ext["_is_phantom"]).sum()) == 2


@pytest.mark.tier1
def test_extended_gt_keeps_twin_on_different_map():
    """Coordinate coincidence on a DIFFERENT map is not a duplicate."""
    student = _student([("K-1", 100.0, 100.0)])
    phantoms = _phantoms([("K-2", 100.0, 100.0)])
    ext = build_extended_gt(student, phantoms)
    assert len(ext) == 2
    assert ext.attrs["n_phantom_duplicates_dropped"] == 0


@pytest.mark.tier1
def test_extended_gt_keeps_nearby_but_distinct_mound():
    """A phantom 30 m from a student point is a distinct mound — kept."""
    student = _student([("K-1", 100.0, 100.0)])
    phantoms = _phantoms([("K-1", 130.0, 100.0)])
    ext = build_extended_gt(student, phantoms)
    assert len(ext) == 2
    assert ext.attrs["n_phantom_duplicates_dropped"] == 0


@pytest.mark.tier1
def test_extended_gt_dedup_disabled_at_zero_tolerance():
    """dedup_tolerance_m=0 reproduces the pre-fix concatenation exactly."""
    student = _student([("K-1", 100.0, 100.0)])
    phantoms = _phantoms([("K-1", 100.0, 100.0)])
    ext = build_extended_gt(student, phantoms, dedup_tolerance_m=0)
    assert len(ext) == 2
    assert ext.attrs["n_phantom_duplicates_dropped"] == 0
