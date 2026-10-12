"""
Tier-1 tests for the W2.7 floors-v2 ``FastScorer`` (PI ruling D60 (4)).

``reports/w27-replicate-floors-2026-10-06-scripts/floors-v2/floors2_lib.py``
restates ``lib_advanced_metrics.compute_per_tile_tp_fp_fn`` (``id`` tile join)
for speed: each frame is attributed once by the library's own
``scope_detections_to_frame`` and every threshold cell is a row mask of it.
Ruling D60 (4) requires it to reproduce the CURRENT library exactly. On a
synthetic two-sheet frame (sheet ``A`` tiles x 0-200, sheet ``B`` x 190-390;
the sheets' padded tiles overlap by 10 m) these tests check that:

* every cell (row mask) of a prepared frame equals the library's per-tile
  table, tile by tile, with an int and with a float buffer, on hand-built
  cases (an out-of-frame row, a cross-sheet row, a re-keyed row restored to
  its origin sheet, a null name) and on seeded random frames;
* a scored detection whose ``source_tile`` is not a frame tile is refused,
  as the library refuses it;
* the archived pre-D50 ``FastScorer`` (the red sentinel of
  ``floors2_scorer_gate.py``) books the out-of-frame row as a false
  positive, which is the difference the gate exists to catch.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import lib_advanced_metrics as lam  # noqa: E402

pytestmark = pytest.mark.tier1

CRS = "EPSG:32635"
FLOORS = PROJECT_ROOT / "reports/w27-replicate-floors-2026-10-06-scripts/floors-v2"
LEGACY = PROJECT_ROOT / "archive/superseded-w27-floors-2026-10-12/floors-v2/floors2_lib.py"


def _module(name: str, path: Path):
    """Load a script module from its path (the floors-v2 scripts are not a package)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # a dataclass resolves its module through sys.modules
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def lib():
    """The rebuilt floors-v2 library."""
    return _module("floors2_lib_under_test", FLOORS / "floors2_lib.py")


@pytest.fixture()
def bounds() -> gpd.GeoDataFrame:
    """Two sheets of two 100 m tiles; B's first tile overlaps A's last by 10 m."""
    return gpd.GeoDataFrame(
        {"tile_name": ["A_x0_y0.png", "A_x100_y0.png", "B_x0_y0.png", "B_x100_y0.png"]},
        geometry=[box(0, 0, 100, 100), box(100, 0, 200, 100),
                  box(190, 0, 290, 100), box(290, 0, 390, 100)],
        crs=CRS,
    )


@pytest.fixture()
def refs() -> gpd.GeoDataFrame:
    """References on both sheets, one in the overlap strip and one off every tile."""
    return gpd.GeoDataFrame(
        {"source_map": ["A", "A", "A", "B", "B", "B"]},
        geometry=[Point(50, 50), Point(150, 20), Point(195, 50),
                  Point(300, 50), Point(350, 80), Point(50, 500)],
        crs=CRS,
    )


def _dets(rows: list[tuple], **extra: list) -> gpd.GeoDataFrame:
    """Detections from ``(source_tile, x, y, prob)`` rows plus any extra columns."""
    return gpd.GeoDataFrame(
        {"source_tile": [r[0] for r in rows], "prob": [r[3] for r in rows], **extra},
        geometry=[Point(r[1], r[2]) for r in rows],
        crs=CRS,
    )


def _library(dets, refs, bounds, buffer) -> dict:
    tm = lam.compute_per_tile_tp_fp_fn(dets, refs, bounds, buffer_metres=buffer)
    return {r.tile_name: (int(r.tp), int(r.fp), int(r.fn)) for r in tm.itertuples()}


def _fast(scorer, prep, mask) -> dict:
    arr = scorer.per_tile(prep, mask)
    return {t: tuple(int(x) for x in arr[i]) for t, i in scorer.tile_pos.items()}


@pytest.mark.parametrize("buffer", [20, 20.0])
def test_every_cell_equals_the_library_on_the_d50_cases(lib, bounds, refs, buffer):
    """Out-of-frame, cross-sheet, restored and null rows: each threshold cell exact."""
    d = _dets(
        [
            ("A_x0_y0.png", 52, 50, 0.9),       # TP on A
            ("A_x100_y0.png", 160, 25, 0.4),    # TP on A
            ("A_x0_y0.png", 50, 520, 0.95),     # named on A, off every tile: dropped
            ("A_x100_y0.png", 300, 55, 0.7),    # named on A, inside B only: dropped
            ("B_x0_y0.png", 196, 50, 0.8),      # re-keyed to B; origin A: scored on A
            ("B_x100_y0.png", 302, 48, 0.3),    # TP on B
            ("B_x100_y0.png", 380, 10, 0.6),    # FP on B
            (None, 60, 60, 0.99),               # unattributed: never scored
        ],
        origin_source_tile=[None, None, None, None, "A_x100_y0.png", None, None, None],
    )
    scorer = lib.FastScorer(refs, bounds, buffer)
    prep = scorer.prepare(d)
    assert prep.diagnostics["n_out_of_frame"] == 2
    assert prep.diagnostics["n_origin_restored"] == 1
    for t in (0.0, 0.35, 0.5, 0.65, 0.85, 0.96, 1.0):
        mask = d["prob"].to_numpy() >= t
        assert _fast(scorer, prep, mask) == _library(d[mask], refs, bounds, buffer), t


@pytest.mark.parametrize("seed", [1, 2, 3])
@pytest.mark.parametrize("buffer", [20, 20.0])
def test_random_frames_equal_the_library_cell_by_cell(lib, bounds, refs, seed, buffer):
    """Seeded random frames (some rows off-frame or cross-named): every cell exact."""
    rng = np.random.default_rng(seed)
    n = 80
    xs, ys = rng.uniform(-20, 410, n), rng.uniform(-20, 120, n)
    names = rng.choice(["A_x0_y0.png", "A_x100_y0.png", "B_x0_y0.png", "B_x100_y0.png"], n)
    d = _dets([(str(nm), x, y, p) for nm, x, y, p in zip(names, xs, ys, rng.uniform(0, 1, n))])
    d.index = rng.permutation(np.arange(100, 100 + n))  # a non-positional index
    scorer = lib.FastScorer(refs, bounds, buffer)
    prep = scorer.prepare(d)
    for t in (0.0, 0.2, 0.5, 0.8):
        mask = d["prob"].to_numpy() >= t
        assert _fast(scorer, prep, mask) == _library(d[mask], refs, bounds, buffer), t
        tp, fp, fn = scorer.totals(prep, mask)
        lt = np.sum(list(_library(d[mask], refs, bounds, buffer).values()), axis=0)
        assert (tp, fp, fn) == tuple(int(x) for x in lt)


def test_a_scored_row_naming_no_frame_tile_is_refused(lib, bounds, refs):
    """The library's tile-join invariant refuses the table; so does the restatement."""
    d = _dets(
        [("A_x0_y0.png", 52, 50, 0.9), (None, 160, 25, 0.9)],
        origin_source_tile=[None, "A_x100_y0.png"],  # attributed to A, booked nowhere
    )
    with pytest.raises(ValueError):
        lam.compute_per_tile_tp_fp_fn(d, refs, bounds, buffer_metres=20)
    scorer = lib.FastScorer(refs, bounds, 20)
    with pytest.raises(ValueError):
        scorer.per_tile(scorer.prepare(d))


def test_the_archived_pre_d50_scorer_books_the_out_of_frame_row(lib, bounds, refs):
    """The red sentinel's premise: the old split books an off-frame row as an FP."""
    legacy = _module("floors2_lib_legacy_under_test", LEGACY)
    d = _dets([("A_x0_y0.png", 52, 50, 0.9), ("A_x0_y0.png", 50, 520, 0.9)])
    old = legacy.FastScorer(refs, bounds, 20)
    xy = np.c_[d.geometry.x, d.geometry.y]
    old_fp = int(old.per_tile(xy, d["source_tile"].to_numpy(dtype=object))[:, 1].sum())
    new = lib.FastScorer(refs, bounds, 20)
    new_fp = new.totals(new.prepare(d))[1]
    lib_fp = sum(v[1] for v in _library(d, refs, bounds, 20).values())
    assert (old_fp, new_fp, lib_fp) == (1, 0, 0)
