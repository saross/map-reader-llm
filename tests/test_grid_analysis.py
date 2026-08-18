"""Tier-1 tests for the tile-size x overlap grid scoring chain.

Covers the pure computational core of ``scripts/grid_prepare_scoring.py`` and
``scripts/grid_analysis.py``: pass resolution (including the additive
``run_<N>_recovery`` merge and the identically-named-pass case that defeats
``lib_detection_paths.resolve_pool_passes``'s pool-wide identity guard), the
manifest-coverage gate, ground-truth scoping, the paired
difference-of-differences bootstrap, and the contract that an undefined tile
MCC stays undefined rather than being published as 0.0 (erratum E81).

The live stages — 40 committed passes, bounds generation from tile metadata,
and the four-way footprint intersection — run against the real artefacts on
sapphire and are not simulated here.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import grid_prepare_scoring  # noqa: E402
from scripts.grid_analysis import (  # noqa: E402
    as_gdf,
    paired_interaction,
    score,
)
from scripts.grid_prepare_scoring import (  # noqa: E402
    CoverageError,
    count_ground_truth,
    load_pass,
    resolve_cell_passes,
)

CRS = "EPSG:32635"

#: Real-time runs name their pass file after config, model and date — never
#: after the run number — so every run directory in a pool holds an
#: identically-named file. That is the case the tests below exercise.
PASS_FILENAME = "detections-detect_brief-text-3-flash-2026-08-18.geojson"


def _write_pass(run_dir: Path, tiles: list[str], n_features: int = 1) -> Path:
    """Write a minimal but structurally valid per-pass detection GeoJSON.

    Args:
        run_dir: Directory to write into; created if absent.
        tiles: Coverage record stamped as ``processed_tiles``.
        n_features: Number of trivial point features to emit.

    Returns:
        Path to the written file.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    target = run_dir / PASS_FILENAME
    target.write_text(json.dumps({
        "type": "FeatureCollection",
        "processed_tiles": tiles,
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [float(i), 0.0]},
                "properties": {"source_tile": tiles[0], "label": "mound"},
            }
            for i in range(n_features)
        ],
    }))
    return target


def _make_cell(root: Path, cell: str, tiles: list[str],
               recovery_for: int | None = None) -> None:
    """Build a synthetic ten-pass cell directory tree under ``root``.

    Args:
        root: Stand-in for ``GRID_ROOT``.
        cell: Cell directory name.
        tiles: The cell's full tile manifest.
        recovery_for: Run number whose main pass is one tile short and whose
            missing tile is supplied by an additive ``run_<N>_recovery``
            fragment; ``None`` for a cell with no recovery.
    """
    for run in range(1, grid_prepare_scoring.N_PASSES + 1):
        run_dir = root / cell / f"run_{run}"
        if run == recovery_for:
            _write_pass(run_dir, tiles[:-1])
            _write_pass(root / cell / f"run_{run}_recovery", tiles[-1:])
        else:
            _write_pass(run_dir, tiles)


@pytest.mark.tier1
def test_resolve_cell_passes_finds_all_ten_identically_named_passes(tmp_path, monkeypatch):
    """Ten run directories holding the same filename resolve to ten passes.

    This is the case ``resolve_pool_passes``'s pool-wide ``pass_identity``
    guard collapses to one, raising ``PassCountMismatch`` on every same-day
    multi-pass real-time pool. Counting identities per run directory is what
    keeps the grid resolvable.
    """
    tiles = ["K-35-052-4_32635_x0_y0.png", "K-35-052-4_32635_x0_y384.png"]
    _make_cell(tmp_path, "g384_ov048", tiles)
    monkeypatch.setattr(grid_prepare_scoring, "GRID_ROOT", tmp_path)

    passes = resolve_cell_passes("g384_ov048")
    assert list(passes) == [f"run_{i}" for i in range(1, 11)]
    assert all(len(v) == 1 for v in passes.values())


@pytest.mark.tier1
def test_resolve_cell_passes_merges_recovery_fragment(tmp_path, monkeypatch):
    """An additive ``run_<N>_recovery`` fragment is appended to its parent pass."""
    tiles = ["K-35-052-4_32635_x0_y0.png", "K-35-052-4_32635_x0_y384.png"]
    _make_cell(tmp_path, "g384_ov048", tiles, recovery_for=3)
    monkeypatch.setattr(grid_prepare_scoring, "GRID_ROOT", tmp_path)

    passes = resolve_cell_passes("g384_ov048")
    assert len(passes["run_3"]) == 2
    assert passes["run_3"][1].parent.name == "run_3_recovery"
    assert all(len(v) == 1 for k, v in passes.items() if k != "run_3")


@pytest.mark.tier1
def test_resolve_cell_passes_rejects_short_pool(tmp_path, monkeypatch):
    """A pool short of ten passes raises rather than scoring silently."""
    tiles = ["K-35-052-4_32635_x0_y0.png"]
    _make_cell(tmp_path, "g384_ov048", tiles)
    (tmp_path / "g384_ov048" / "run_10" / PASS_FILENAME).unlink()
    (tmp_path / "g384_ov048" / "run_10").rmdir()
    monkeypatch.setattr(grid_prepare_scoring, "GRID_ROOT", tmp_path)

    with pytest.raises(CoverageError, match="expected 10"):
        resolve_cell_passes("g384_ov048")


@pytest.mark.tier1
def test_load_pass_unions_features_and_coverage(tmp_path):
    """Concatenating a pass with its recovery fragment restores full coverage."""
    tiles = ["a.png", "b.png", "c.png"]
    main = _write_pass(tmp_path / "run_1", tiles[:-1], n_features=4)
    recovery = _write_pass(tmp_path / "run_1_recovery", tiles[-1:], n_features=2)

    features, processed = load_pass([main, recovery])
    assert len(features) == 6
    assert processed == set(tiles)


@pytest.mark.tier1
def test_load_pass_missing_file_raises(tmp_path):
    """A missing pass file is an error, not an empty pass."""
    with pytest.raises(FileNotFoundError):
        load_pass([tmp_path / "nope.geojson"])


@pytest.mark.tier1
def test_count_ground_truth_counts_only_references_on_tiles():
    """Ground truth is counted per map sheet, and only where a tile covers it."""
    grid = gpd.GeoDataFrame(
        {"tile_name": ["K-35-052-4_32635_x0_y0.png",
                       "K-35-052-4_32635_x0_y100.png"]},
        geometry=[box(0, 0, 100, 100), box(0, 100, 100, 200)],
        crs=CRS,
    )
    refs = gpd.GeoDataFrame(
        {"Map": ["K-35-052-4_32635"] * 3},
        geometry=[Point(50, 50), Point(50, 150), Point(500, 500)],
        crs=CRS,
    )
    assert count_ground_truth(grid, refs) == 2


@pytest.mark.tier1
def test_as_gdf_drops_detections_off_the_carrier_grid():
    """A detection on no carrier tile cannot be booked, so it is dropped."""
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["K-35-052-4_32635_x0_y0.png"]},
        geometry=[box(0, 0, 100, 100)], crs=CRS,
    )
    gdf = as_gdf(np.array([[50.0, 50.0], [900.0, 900.0]]), bounds)
    assert len(gdf) == 1
    assert gdf.iloc[0]["source_tile"] == "K-35-052-4_32635_x0_y0.png"


@pytest.mark.tier1
def test_as_gdf_handles_empty_input():
    """An empty cluster set yields an empty, still-scorable frame."""
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["K-35-052-4_32635_x0_y0.png"]},
        geometry=[box(0, 0, 100, 100)], crs=CRS,
    )
    assert as_gdf(np.zeros((0, 2)), bounds).empty


@pytest.mark.tier1
def test_score_reports_undefined_mcc_as_none_not_zero():
    """A degenerate tile confusion matrix yields ``None``, never 0.0 (E81).

    Every tile here holds a reference mound, so the empty-tile marginal
    (TN + FP) vanishes and MCC is undefined. Publishing 0.0 would assert "no
    discrimination" where the truth is "not measurable".
    """
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["K-35-052-4_32635_x0_y0.png",
                       "K-35-052-4_32635_x0_y100.png"]},
        geometry=[box(0, 0, 100, 100), box(0, 100, 100, 200)], crs=CRS,
    )
    refs = gpd.GeoDataFrame(
        {"Map": ["K-35-052-4_32635"] * 2},
        geometry=[Point(50, 50), Point(50, 150)], crs=CRS,
    )
    dets = gpd.GeoDataFrame(
        {"source_tile": ["K-35-052-4_32635_x0_y0.png"]},
        geometry=[Point(51, 51)], crs=CRS,
    )
    result = score(dets, refs, bounds)
    assert result["mcc"] is None
    assert result["f1"] > 0


@pytest.mark.tier1
def test_score_returns_defined_mcc_when_matrix_is_non_degenerate():
    """With both an empty and a populated tile, MCC is a real number."""
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["K-35-052-4_32635_x0_y0.png",
                       "K-35-052-4_32635_x0_y100.png"]},
        geometry=[box(0, 0, 100, 100), box(0, 100, 100, 200)], crs=CRS,
    )
    refs = gpd.GeoDataFrame(
        {"Map": ["K-35-052-4_32635"]}, geometry=[Point(50, 50)], crs=CRS,
    )
    dets = gpd.GeoDataFrame(
        {"source_tile": ["K-35-052-4_32635_x0_y0.png"]},
        geometry=[Point(51, 51)], crs=CRS,
    )
    result = score(dets, refs, bounds)
    assert result["mcc"] == pytest.approx(1.0)


def _counts(tp, fp, fn):
    """Build the per-tile count dict the bootstrap consumes.

    Args:
        tp: True-positive array. fp: False-positive array. fn: False-negative array.

    Returns:
        Dict of float NumPy arrays keyed ``tp``/``fp``/``fn``.
    """
    return {
        "tp": np.asarray(tp, dtype=float),
        "fp": np.asarray(fp, dtype=float),
        "fn": np.asarray(fn, dtype=float),
    }


@pytest.mark.tier1
def test_paired_interaction_is_deterministic():
    """The same seed and inputs give identical results."""
    rng = np.random.default_rng(0)
    cells = [_counts(rng.integers(0, 5, 40), rng.integers(0, 4, 40),
                     rng.integers(0, 3, 40)) for _ in range(4)]
    assert (paired_interaction(*cells, n_iter=150, seed=42)
            == paired_interaction(*cells, n_iter=150, seed=42))


@pytest.mark.tier1
def test_paired_interaction_is_zero_when_effects_are_equal():
    """Identical simple effects give a degenerate null at exactly zero.

    Pairing is what makes this hold: one index draw is applied to all four
    cells, so when the two simple effects are the same contrast the
    difference-of-differences is identically zero in every iteration.
    """
    rng = np.random.default_rng(3)
    a = _counts(rng.integers(0, 6, 50), rng.integers(0, 6, 50), rng.integers(0, 4, 50))
    b = _counts(rng.integers(0, 6, 50), rng.integers(0, 6, 50), rng.integers(0, 4, 50))
    res = paired_interaction(a, b, a, b, n_iter=200, seed=42)
    assert res["difference_of_differences"] == 0.0
    assert res["ci_lower"] == 0.0
    assert res["ci_upper"] == 0.0
    assert not res["excludes_zero"]


@pytest.mark.tier1
def test_paired_interaction_observed_value_matches_pooled_arithmetic():
    """The reported point estimate is the pooled difference of differences."""
    from scripts.h13_overlap_analysis import micro_f1

    a = _counts([6, 6], [1, 1], [1, 1])
    b = _counts([3, 3], [3, 3], [3, 3])
    c = _counts([5, 5], [2, 2], [1, 1])
    d = _counts([4, 4], [2, 2], [2, 2])
    res = paired_interaction(a, b, c, d, n_iter=50, seed=7)
    expected = (
        (micro_f1(12, 2, 2)[2] - micro_f1(6, 6, 6)[2])
        - (micro_f1(10, 4, 2)[2] - micro_f1(8, 4, 4)[2])
    )
    assert res["difference_of_differences"] == pytest.approx(expected)


@pytest.mark.tier1
def test_paired_interaction_detects_a_real_interaction():
    """A constructed interaction is recovered with a CI excluding zero."""
    n = 120
    # Factor level 1: a large simple effect. Factor level 2: none at all.
    a = _counts(np.full(n, 5.0), np.full(n, 1.0), np.full(n, 1.0))
    b = _counts(np.full(n, 1.0), np.full(n, 5.0), np.full(n, 5.0))
    c = _counts(np.full(n, 3.0), np.full(n, 3.0), np.full(n, 3.0))
    d = _counts(np.full(n, 3.0), np.full(n, 3.0), np.full(n, 3.0))
    res = paired_interaction(a, b, c, d, n_iter=300, seed=42)
    assert res["difference_of_differences"] > 0
    assert res["excludes_zero"]
