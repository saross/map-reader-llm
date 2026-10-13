"""
Tier-1 tests for ``per_map_counts`` in ``scripts/stride55_sweep_oracle.py``.

``per_map_counts`` returns each map sheet's (TP, FP, FN) at ``BUFFER_R``, the
input to the per-map paired sign-swap permutations of the stride sweep, the
stride ladder, the A5-versus-B5 test, and the Gemini 3.7 campaign's sweep and
grid board. Until 2026-10-12 it kept its own per-sheet loop: detections were
split by a bare ``source_tile.str.startswith(sheet)`` prefix, wherever they
lay, and any recorded origin column was ignored. That is the pre-D50 rule the
shared scorer replaced on 2026-10-07 (PI ruling D50,
``planning/pi-decisions-2026-09-20.md``), so the permutation input and the
F1 the sweep reports (``compute_counts_at_r``, already on the shared rule)
could describe different detections.

PI ruling D60 (3) and (4) name this function in Phase 5's sweep for scorer
restatements. The contract tested here, on the synthetic two-sheet frame of
``tests/test_detection_scope.py`` (sheet ``A`` tiles x 0-200, sheet ``B``
tiles x 190-390, overlapping by 10 m):

* a detection named on a sheet but outside that sheet's tiles is dropped,
  not booked as a false positive;
* a detection re-keyed onto another sheet's tile is scored on its recorded
  origin sheet;
* a tile name is put on ONE sheet by the library's longest-prefix rule, so a
  sheet whose name prefixes another's does not also claim its detections;
* the per-sheet counts sum to the corrected-F1 engine's totals, so the
  permutation statistic and the reported F1 describe the same detections;
* the keys are the frame's sheets, as before.
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import lib_advanced_metrics as lam  # noqa: E402
from scripts.compute_corrected_f1_multi_buffer import (  # noqa: E402
    compute_counts_at_r,
)
from scripts.stride55_sweep_oracle import (  # noqa: E402
    BUFFER_R,
    f1_from_map_counts,
    per_map_counts,
)

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"


@pytest.fixture()
def frame() -> gpd.GeoDataFrame:
    """Two sheets of two 100 m tiles; B's first tile overlaps A's last by 10 m."""
    return gpd.GeoDataFrame(
        {"tile_name": ["A_x0_y0.png", "A_x100_y0.png", "B_x0_y0.png", "B_x100_y0.png"]},
        geometry=[box(0, 0, 100, 100), box(100, 0, 200, 100),
                  box(190, 0, 290, 100), box(290, 0, 390, 100)],
        crs=CRS,
    )


@pytest.fixture()
def refs() -> gpd.GeoDataFrame:
    """Extended ground truth: two references on A, one on B (55-map column)."""
    return gpd.GeoDataFrame(
        {"source_map": ["A", "A", "B"]},
        geometry=[Point(50, 50), Point(195, 50), Point(300, 50)],
        crs=CRS,
    )


def dets(rows: list[tuple[str | None, float, float]], **extra: list) -> gpd.GeoDataFrame:
    """Detections from ``(source_tile, x, y)`` rows plus any extra columns."""
    data: dict = {"source_tile": [r[0] for r in rows], **extra}
    return gpd.GeoDataFrame(
        data, geometry=[Point(r[1], r[2]) for r in rows], crs=CRS,
    )


def test_buffer_is_wide_enough_for_the_fixture() -> None:
    """The fixture's matches sit 1 m apart; any registered buffer covers them."""
    assert BUFFER_R >= 1


def test_out_of_frame_detection_is_dropped_not_a_false_positive(frame, refs):
    """Named on A, lying 400 m outside every tile: before D50 an FP on A."""
    d = dets([("A_x0_y0.png", 51, 50), ("A_x0_y0.png", 50, 500)])
    counts = per_map_counts(d, refs, frame)
    assert counts == {"A": (1, 0, 1), "B": (0, 0, 1)}


def test_cross_sheet_point_is_dropped(frame, refs):
    """Named on A, lying only in B's tiles: outside its own sheet, so dropped."""
    d = dets([("A_x100_y0.png", 250, 50)])
    assert per_map_counts(d, refs, frame) == {"A": (0, 0, 2), "B": (0, 0, 1)}


def test_a_rekeyed_detection_is_scored_on_its_origin_sheet(frame, refs):
    """Re-keyed onto B's overlapping tile but seen on A: it matches A's reference."""
    d = dets([("A_x0_y0.png", 51, 50), ("B_x0_y0.png", 196, 50),
              ("B_x100_y0.png", 301, 50)],
             origin_source_tile=["A_x0_y0.png", "A_x100_y0.png", "B_x100_y0.png"])
    assert per_map_counts(d, refs, frame) == {"A": (2, 0, 0), "B": (1, 0, 0)}
    # Without the origin record the re-key costs a TP: an FP on B and an FN on A.
    rekeyed_only = d.drop(columns=["origin_source_tile"])
    assert per_map_counts(rekeyed_only, refs, frame) == {"A": (1, 0, 1), "B": (1, 1, 0)}


def test_a_sheet_name_prefixing_another_does_not_claim_its_detections():
    """``K-1`` prefixes ``K-1_X``: a ``K-1_X`` detection is scored once, on ``K-1_X``.

    The bare ``startswith`` split booked it on both sheets, an extra false
    positive on ``K-1`` wherever no ``K-1`` reference lay near it.
    """
    frame = gpd.GeoDataFrame(
        {"tile_name": ["K-1_x0_y0.png", "K-1_X_x0_y0.png"]},
        geometry=[box(0, 0, 100, 100), box(500, 0, 600, 100)],
        crs=CRS,
    )
    refs = gpd.GeoDataFrame(
        {"source_map": ["K-1", "K-1_X"]},
        geometry=[Point(50, 50), Point(550, 50)],
        crs=CRS,
    )
    d = dets([("K-1_x0_y0.png", 51, 50), ("K-1_X_x0_y0.png", 551, 50)])
    assert lam.frame_sheets(frame) == ["K-1", "K-1_X"]
    assert per_map_counts(d, refs, frame) == {"K-1": (1, 0, 0), "K-1_X": (1, 0, 0)}


def test_per_sheet_counts_sum_to_the_engine_totals(frame, refs):
    """The permutation input and the reported F1 describe the same detections.

    The Gemini 3.7 sweep gates its per-map F1 against the sweep's
    ``compute_counts_at_r`` value to 1e-6; under the old split that gate
    failed wherever a detection lay out of frame or had been re-keyed.
    """
    d = dets([("A_x0_y0.png", 51, 50), ("A_x0_y0.png", 50, 500),
              ("B_x0_y0.png", 196, 50), ("B_x100_y0.png", 301, 50),
              ("A_x100_y0.png", 250, 50), ("B_x100_y0.png", 380, 90)],
             origin_source_tile=["A_x0_y0.png", "A_x0_y0.png", "A_x100_y0.png",
                                 "B_x100_y0.png", "A_x100_y0.png", "B_x100_y0.png"])
    counts = per_map_counts(d, refs, frame)
    tp, fp, fn, _ = compute_counts_at_r(d, refs, frame, BUFFER_R)
    assert tuple(sum(c[i] for c in counts.values()) for i in range(3)) == (tp, fp, fn)
    assert f1_from_map_counts(counts) == pytest.approx(
        2 * tp / (2 * tp + fp + fn), abs=1e-12)


def test_keys_are_the_frame_sheets_including_empty_ones(frame, refs):
    """Every frame sheet is a pairing unit, even with nothing on it."""
    assert per_map_counts(dets([]), refs, frame) == {"A": (0, 0, 2), "B": (0, 0, 1)}
    empty_refs = refs.iloc[0:0]
    d = dets([("A_x0_y0.png", 51, 50)])
    assert per_map_counts(d, empty_refs, frame) == {"A": (0, 1, 0), "B": (0, 0, 0)}


def test_a_fully_in_frame_set_keeps_the_legacy_counts(frame, refs):
    """Nothing out of frame, nothing re-keyed: the counts cannot move."""
    d = dets([("A_x0_y0.png", 51, 50), ("A_x100_y0.png", 120, 50),
              ("B_x100_y0.png", 301, 50)])
    assert per_map_counts(d, refs, frame) == {"A": (1, 1, 1), "B": (1, 0, 0)}
