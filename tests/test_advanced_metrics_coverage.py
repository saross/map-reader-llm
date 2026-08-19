"""
Tier 1 tests for the BCa bootstrap upgrade and Mitigation 3 sparse-coverage
transparency in ``scripts.lib_advanced_metrics``.

Background
----------
On 2026-04-29 the bootstrap CI implementation was upgraded from the
percentile method to the Bias-Corrected and Accelerated (BCa) bootstrap
via :func:`scipy.stats.bootstrap`. The same change introduced a
sparse-coverage flag (Mitigation 3) that fires when more than 50 % of
evaluation tiles have zero true-positive (TP), false-positive (FP), and
false-negative (FN) counts. The flag suppresses CI bounds in
human-readable Markdown / Comma-Separated Values (CSV) outputs while
preserving them in the JavaScript Object Notation (JSON) copy for
downstream tooling.

These tests pin both the structural changes (new metadata fields,
``coverage`` block, ``point`` fields) and the behavioural changes
(threshold semantics, fallback handling, deterministic point estimates)
so a regression that quietly reverts to the percentile method would be
caught.

Test layers
-----------
1. ``_compute_coverage`` unit tests — boundary, sparse, dense, edge cases.
2. ``_bca_ci_from_indices`` tests — BCa correctness on a known-skewed
   distribution; degenerate-case fallback to percentile.
3. ``_compute_bca_ci`` tests — BCa via jackknife of an external bootstrap
   distribution, used by effect-size / multi-run / interaction callers.
4. ``bootstrap_ci`` integration tests — schema, point-estimate stability,
   coverage block plumbing, fallback path.

All tests use synthetic data and run without network or filesystem I/O
beyond ``tmp_path`` fixtures.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (  # noqa: E402
    BOOTSTRAP_LIB,
    BOOTSTRAP_METHOD,
    COVERAGE_SOURCE_HEURISTIC,
    COVERAGE_SOURCE_PROCESSED_TILES,
    COVERAGE_STATUS_NORMAL,
    COVERAGE_STATUS_PARTIAL,
    COVERAGE_STATUS_SPARSE,
    DEFAULT_COVERAGE_THRESHOLD,
    _bca_ci_from_indices,
    _compute_bca_ci,
    _compute_coverage,
    bootstrap_ci,
    read_processed_tiles,
    calculate_f1_internal,
)


# =========================================================================
# FIXTURES
# =========================================================================


def _make_tile_metrics(
    n_tiles: int,
    n_zero_tiles: int,
    seed: int = 42,
) -> pd.DataFrame:
    """Build a synthetic ``tile_metrics`` DataFrame for coverage tests.

    The first ``n_zero_tiles`` rows have zero TP/FP/FN counts (i.e. they
    contribute no signal to the bootstrap aggregate). The remaining rows
    have a small random non-zero count so the aggregate F1 is well
    defined.

    Args:
        n_tiles: Total number of tiles in the synthesised frame.
        n_zero_tiles: Number of leading rows that should have zero counts.
        seed: Deterministic seed for the random non-zero counts.

    Returns:
        A DataFrame with the columns required by
        :func:`_compute_coverage`.
    """
    _ = seed  # currently unused; placeholder for future jitter
    rows = []
    for i in range(n_tiles):
        if i < n_zero_tiles:
            rows.append({"tile_name": f"t{i:03d}", "tp": 0, "fp": 0, "fn": 0})
        else:
            # Deterministic non-zero counts so the active tiles are
            # guaranteed to have TP+FP+FN > 0 (the coverage check would
            # otherwise misclassify a randomly-zero active tile as
            # zero-coverage and inflate ``n_zero_count_tiles``).
            rows.append({
                "tile_name": f"t{i:03d}", "tp": 1, "fp": 0, "fn": 0,
            })
    return pd.DataFrame(rows)


def _make_synthetic_eval_inputs(
    n_tiles: int,
    n_active_tiles: int,
    seed: int = 42,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Build minimal synthetic detection / reference / bounds GeoDataFrames.

    The first ``n_active_tiles`` tiles each contain one reference and
    one detection co-located inside the buffer tolerance — they generate
    TP counts. The remaining ``n_tiles - n_active_tiles`` tiles are empty
    and generate zero-coverage rows in the bootstrap.

    Tile names follow the canonical ``<map>_x{X}_y{Y}.png`` pattern so
    :func:`scripts.lib_advanced_metrics.get_map_name` extracts a non-
    ``Unknown`` map name and the per-map matching loop fires.

    Args:
        n_tiles: Total number of tiles.
        n_active_tiles: Number of tiles that contain a reference + a
            detection (the rest are empty).
        seed: Deterministic seed (unused for now; placeholder for
            future jitter).

    Returns:
        Tuple of (gdf_det, gdf_ref, gdf_bounds) ready for
        :func:`bootstrap_ci`.
    """
    _ = seed  # unused; placeholder for future jitter
    map_name = "K-35-052-4_32635"

    bounds_rows = []
    ref_rows = []
    det_rows = []
    for i in range(n_tiles):
        x0 = 500000 + i * 200
        y0 = 4700000
        tile_name = f"{map_name}_x{x0}_y{y0}.png"
        bounds_rows.append({
            "tile_name": tile_name,
            "geometry": box(x0, y0, x0 + 100, y0 + 100),
        })
        if i < n_active_tiles:
            ref_rows.append({
                "geometry": Point(x0 + 50, y0 + 50),
                "Map": map_name,
                "Symbol": "Burial Mound",
            })
            det_rows.append({
                "source_tile": tile_name,
                "geometry": box(x0 + 45, y0 + 45, x0 + 55, y0 + 55),
                "label": "mound",
                "subtype": "burial_mound",
            })

    gdf_bounds = gpd.GeoDataFrame(bounds_rows, crs="EPSG:32635")
    gdf_ref = (
        gpd.GeoDataFrame(ref_rows, crs="EPSG:32635")
        if ref_rows
        else gpd.GeoDataFrame(
            {"Map": [], "Symbol": []}, geometry=[], crs="EPSG:32635",
        )
    )
    gdf_det = (
        gpd.GeoDataFrame(det_rows, crs="EPSG:32635")
        if det_rows
        else gpd.GeoDataFrame(
            {"source_tile": [], "label": [], "subtype": []},
            geometry=[], crs="EPSG:32635",
        )
    )
    return gdf_det, gdf_ref, gdf_bounds


# =========================================================================
# COVERAGE HELPER TESTS
# =========================================================================


@pytest.mark.tier1
class TestComputeCoverage:
    """Unit tests for :func:`_compute_coverage`."""

    def test_dense_coverage_is_normal(self) -> None:
        """Zero-fraction below threshold => ``coverage_status='normal'``."""
        # 10 tiles, 2 zero-coverage (20 %) — well under the default 50 %.
        tile_metrics = _make_tile_metrics(n_tiles=10, n_zero_tiles=2)
        cov = _compute_coverage(tile_metrics)
        assert cov["coverage_status"] == COVERAGE_STATUS_NORMAL
        assert cov["zero_fraction"] == pytest.approx(0.2)
        assert cov["n_tiles"] == 10
        assert cov["n_zero_count_tiles"] == 2

    def test_sparse_coverage_is_flagged(self) -> None:
        """Zero-fraction above threshold => ``sparse_cross_grid``.

        Mirrors the production cross-grid case (74.5 % – 83.4 % zero
        coverage on the 5 affected pairwise/tile-size-30m cells).
        """
        # 100 tiles, 80 zero-coverage (80 %) — above the 50 % default.
        tile_metrics = _make_tile_metrics(n_tiles=100, n_zero_tiles=80)
        cov = _compute_coverage(tile_metrics)
        assert cov["coverage_status"] == COVERAGE_STATUS_SPARSE
        assert cov["zero_fraction"] == pytest.approx(0.80)
        assert cov["n_zero_count_tiles"] == 80

    def test_boundary_at_threshold_is_normal(self) -> None:
        """Strict ``>`` semantics: exactly 50 % zero is NOT flagged.

        The default threshold is 0.5 with strict-greater-than semantics
        (the threshold is the maximum acceptable coverage gap). Exactly
        50 % zero-coverage should therefore be reported as ``normal``,
        not as sparse.
        """
        tile_metrics = _make_tile_metrics(n_tiles=10, n_zero_tiles=5)
        cov = _compute_coverage(tile_metrics, threshold=0.5)
        assert cov["zero_fraction"] == pytest.approx(0.5)
        assert cov["coverage_status"] == COVERAGE_STATUS_NORMAL

    def test_boundary_just_above_threshold_is_sparse(self) -> None:
        """One extra zero tile above threshold trips the flag."""
        # 11 tiles, 6 zero -> 54.5 %.
        tile_metrics = _make_tile_metrics(n_tiles=11, n_zero_tiles=6)
        cov = _compute_coverage(tile_metrics, threshold=0.5)
        assert cov["coverage_status"] == COVERAGE_STATUS_SPARSE

    def test_custom_threshold_overrides_default(self) -> None:
        """Caller-supplied threshold overrides the module default."""
        # 30 % zero — sparse only under a stricter 0.2 threshold.
        tile_metrics = _make_tile_metrics(n_tiles=10, n_zero_tiles=3)
        cov_default = _compute_coverage(tile_metrics)
        cov_strict = _compute_coverage(tile_metrics, threshold=0.2)
        assert cov_default["coverage_status"] == COVERAGE_STATUS_NORMAL
        assert cov_strict["coverage_status"] == COVERAGE_STATUS_SPARSE
        assert cov_strict["threshold"] == pytest.approx(0.2)

    def test_empty_frame_returns_normal(self) -> None:
        """Empty tile metrics => zero fraction with no flag."""
        empty = pd.DataFrame({"tile_name": [], "tp": [], "fp": [], "fn": []})
        cov = _compute_coverage(empty)
        assert cov["n_tiles"] == 0
        assert cov["zero_fraction"] == 0.0
        assert cov["coverage_status"] == COVERAGE_STATUS_NORMAL

    def test_default_threshold_constant(self) -> None:
        """The module-level default threshold matches the 0.5 contract."""
        assert DEFAULT_COVERAGE_THRESHOLD == pytest.approx(0.5)


# =========================================================================
# E72 PARTIAL-COVERAGE TESTS
# =========================================================================


def _e72_shaped_tile_metrics() -> tuple[pd.DataFrame, set[str]]:
    """Reproduce the E72 defect's numbers in miniature.

    The real case: a detection set covering 240 tiles was scored against
    487-tile Era 2 bounds. The 247 unprocessed tiles held 193 ground-truth
    mounds, which entered the score as artificial false negatives — so
    they raised the FN count rather than the zero count, and the resulting
    ``zero_fraction`` of 0.4641 slipped under the 0.5 sparse threshold.

    This fixture reproduces that shape exactly: 487 bounds tiles, 240
    processed, 226 zero-count tiles (0.4641 zero-fraction, matching the
    recorded diagnostic), and unprocessed-but-mound-bearing tiles carrying
    FN counts. The point is that the zero-fraction heuristic ALONE returns
    ``normal`` on this frame.

    Returns:
        Tuple of (tile_metrics frame over all 487 bounds tiles, the set of
        240 processed tile names).
    """
    n_bounds = 487
    n_processed = 240
    # 0.4641 * 487 = 226.0 (the recorded zero_fraction, to 4 d.p.)
    n_zero = 226

    processed = {f"tile_{i:04d}.png" for i in range(n_processed)}
    rows = []
    for i in range(n_bounds):
        name = f"tile_{i:04d}.png"
        if i < n_zero:
            # Zero-count tiles: no detection, no reference.
            rows.append({"tile_name": name, "tp": 0, "fp": 0, "fn": 0})
        elif name in processed:
            # Processed tiles that found something.
            rows.append({"tile_name": name, "tp": 1, "fp": 0, "fn": 0})
        else:
            # Unprocessed tiles holding ground truth: pure false
            # negatives. These are exactly what the zero-count heuristic
            # cannot see.
            rows.append({"tile_name": name, "tp": 0, "fp": 0, "fn": 1})
    return pd.DataFrame(rows), processed


@pytest.mark.tier1
class TestPartialCoverageGuard:
    """E72 hardening: coverage counted from ``processed_tiles``.

    Three behaviours are pinned:

    1. **Full coverage stays normal** — the additive change must not
       reclassify any existing full-coverage evaluation.
    2. **Partial coverage is caught** — the E72 240/487 shape must flag,
       even though its zero-fraction sits under the threshold.
    3. **Fallback is preserved** — with no ``processed_tiles`` evidence,
       the zero-fraction heuristic behaves exactly as before.
    """

    # -- 1. full coverage ------------------------------------------------

    def test_full_coverage_is_normal(self) -> None:
        """Every bounds tile processed => ``normal``, zero unprocessed."""
        tile_metrics = _make_tile_metrics(n_tiles=20, n_zero_tiles=4)
        processed = set(tile_metrics["tile_name"])
        cov = _compute_coverage(tile_metrics, processed_tiles=processed)
        assert cov["coverage_status"] == COVERAGE_STATUS_NORMAL
        assert cov["n_unprocessed_tiles"] == 0
        assert cov["n_processed_tiles"] == 20
        assert cov["coverage_detail"] is None
        assert cov["coverage_source"] == COVERAGE_SOURCE_PROCESSED_TILES

    def test_full_coverage_result_matches_heuristic_result(self) -> None:
        """Full coverage must not change any pre-E72 field value.

        The hardening is additive: for a fully-covered detection set the
        status, zero-fraction, tile counts, and threshold must be
        byte-identical to what the pre-E72 code path produced (which is
        what the no-evidence path still produces).
        """
        tile_metrics = _make_tile_metrics(n_tiles=20, n_zero_tiles=4)
        processed = set(tile_metrics["tile_name"])
        with_evidence = _compute_coverage(
            tile_metrics, processed_tiles=processed,
        )
        no_evidence = _compute_coverage(tile_metrics)
        legacy_keys = (
            "n_tiles", "n_zero_count_tiles", "zero_fraction",
            "threshold", "coverage_status",
        )
        for key in legacy_keys:
            assert with_evidence[key] == no_evidence[key], key

    def test_full_coverage_does_not_mask_a_sparse_flag(self) -> None:
        """A sparse-but-fully-covered set still reports ``sparse_cross_grid``.

        Direct coverage evidence answers "did the data cover the bounds?",
        not "are the CIs stable?". A genuinely sparse cross-grid case that
        happens to carry a complete ``processed_tiles`` record must keep
        its Mitigation 3 flag.
        """
        tile_metrics = _make_tile_metrics(n_tiles=100, n_zero_tiles=80)
        processed = set(tile_metrics["tile_name"])
        cov = _compute_coverage(tile_metrics, processed_tiles=processed)
        assert cov["coverage_status"] == COVERAGE_STATUS_SPARSE
        assert cov["n_unprocessed_tiles"] == 0

    # -- 2. partial coverage (the E72 shape) -----------------------------

    def test_e72_shape_flags_partial_coverage(self) -> None:
        """A 240/487 detection set MUST flag — this is the E72 regression.

        Without ``processed_tiles`` this frame reports ``normal``: its
        zero-fraction is 0.4641, under the 0.5 threshold, because the 247
        missing tiles produce false negatives rather than zero counts.
        With the record supplied, the guard counts the gap directly.
        """
        tile_metrics, processed = _e72_shaped_tile_metrics()

        # The heuristic alone is blind to this case — that is the defect.
        heuristic_only = _compute_coverage(tile_metrics)
        assert heuristic_only["zero_fraction"] == pytest.approx(
            0.4641, abs=1e-4,
        )
        assert heuristic_only["coverage_status"] == COVERAGE_STATUS_NORMAL

        # With direct evidence it is caught.
        cov = _compute_coverage(tile_metrics, processed_tiles=processed)
        assert cov["coverage_status"] == COVERAGE_STATUS_PARTIAL
        assert cov["n_unprocessed_tiles"] == 247
        assert cov["n_processed_tiles"] == 240
        assert cov["coverage_detail"] == "partial: 247/487 tiles unprocessed"
        assert cov["coverage_source"] == COVERAGE_SOURCE_PROCESSED_TILES
        # The zero-fraction is still reported — the new check supplements
        # the diagnostic block rather than replacing it.
        assert cov["zero_fraction"] == pytest.approx(0.4641, abs=1e-4)

    def test_single_unprocessed_tile_flags_partial(self) -> None:
        """The trigger is any shortfall at all, not a fraction threshold."""
        tile_metrics = _make_tile_metrics(n_tiles=50, n_zero_tiles=2)
        processed = set(tile_metrics["tile_name"]) - {"t049"}
        cov = _compute_coverage(tile_metrics, processed_tiles=processed)
        assert cov["coverage_status"] == COVERAGE_STATUS_PARTIAL
        assert cov["n_unprocessed_tiles"] == 1
        assert cov["coverage_detail"] == "partial: 1/50 tiles unprocessed"

    def test_partial_outranks_sparse(self) -> None:
        """Partial coverage wins over a simultaneous sparse flag.

        A set that is both sparse and under-covering should report the
        more severe diagnosis, because partial coverage invalidates the
        point estimate and not merely the interval.
        """
        tile_metrics = _make_tile_metrics(n_tiles=100, n_zero_tiles=80)
        processed = {f"t{i:03d}" for i in range(60)}
        cov = _compute_coverage(tile_metrics, processed_tiles=processed)
        assert cov["coverage_status"] == COVERAGE_STATUS_PARTIAL
        assert cov["n_unprocessed_tiles"] == 40

    def test_extra_processed_tiles_outside_bounds_are_ignored(self) -> None:
        """Processed tiles outside the evaluation bounds do not count.

        A pass may legitimately have processed tiles that the current
        bounds exclude (a broader corpus scored against a narrower scope).
        Coverage asks only "are the BOUNDS tiles covered?".
        """
        tile_metrics = _make_tile_metrics(n_tiles=10, n_zero_tiles=1)
        processed = set(tile_metrics["tile_name"]) | {
            "not_in_bounds_a.png", "not_in_bounds_b.png",
        }
        cov = _compute_coverage(tile_metrics, processed_tiles=processed)
        assert cov["coverage_status"] == COVERAGE_STATUS_NORMAL
        assert cov["n_unprocessed_tiles"] == 0
        assert cov["n_processed_tiles"] == 10

    # -- 3. fallback path ------------------------------------------------

    def test_no_processed_tiles_falls_back_to_heuristic(self) -> None:
        """``processed_tiles=None`` reproduces the pre-E72 behaviour."""
        dense = _make_tile_metrics(n_tiles=10, n_zero_tiles=2)
        sparse = _make_tile_metrics(n_tiles=100, n_zero_tiles=80)
        cov_dense = _compute_coverage(dense)
        cov_sparse = _compute_coverage(sparse)
        assert cov_dense["coverage_status"] == COVERAGE_STATUS_NORMAL
        assert cov_sparse["coverage_status"] == COVERAGE_STATUS_SPARSE
        for cov in (cov_dense, cov_sparse):
            assert cov["coverage_source"] == COVERAGE_SOURCE_HEURISTIC
            assert cov["n_unprocessed_tiles"] is None
            assert cov["n_processed_tiles"] is None
            assert cov["coverage_detail"] is None

    def test_empty_frame_with_evidence_still_normal(self) -> None:
        """Empty bounds short-circuit before the coverage count."""
        empty = pd.DataFrame({"tile_name": [], "tp": [], "fp": [], "fn": []})
        cov = _compute_coverage(empty, processed_tiles={"anything.png"})
        assert cov["n_tiles"] == 0
        assert cov["coverage_status"] == COVERAGE_STATUS_NORMAL
        assert cov["coverage_source"] == COVERAGE_SOURCE_PROCESSED_TILES

    def test_empty_processed_set_is_evidence_not_absence(self) -> None:
        """An empty set means "nothing processed", not "no record".

        ``None`` and ``set()`` must not be conflated: the former is the
        fallback signal, the latter is direct evidence of total
        non-coverage.
        """
        tile_metrics = _make_tile_metrics(n_tiles=10, n_zero_tiles=2)
        cov = _compute_coverage(tile_metrics, processed_tiles=set())
        assert cov["coverage_status"] == COVERAGE_STATUS_PARTIAL
        assert cov["n_unprocessed_tiles"] == 10


@pytest.mark.tier1
class TestReadProcessedTiles:
    """Unit tests for :func:`read_processed_tiles`."""

    def test_reads_processed_tiles_from_geojson(self, tmp_path) -> None:
        """A per-pass detection GeoJSON's record is returned as a set."""
        path = tmp_path / "detections_384_run01.geojson"
        path.write_text(json.dumps({
            "type": "FeatureCollection",
            "features": [],
            "processed_tiles": ["a.png", "b.png", "a.png"],
        }), encoding="utf-8")
        assert read_processed_tiles(path) == {"a.png", "b.png"}

    def test_absent_record_returns_none(self, tmp_path) -> None:
        """A consensus-style artefact with no record returns ``None``.

        ``None`` is the fallback signal — the caller must then use the
        zero-fraction heuristic rather than assume zero coverage.
        """
        path = tmp_path / "consensus_t3.geojson"
        path.write_text(json.dumps({
            "type": "FeatureCollection", "features": [],
        }), encoding="utf-8")
        assert read_processed_tiles(path) is None

    def test_accepts_a_preparsed_dict(self) -> None:
        """Callers that already hold the parsed GeoJSON avoid a re-read."""
        payload = {
            "type": "FeatureCollection",
            "features": [],
            "processed_tiles": ["x.png"],
        }
        assert read_processed_tiles(payload) == {"x.png"}

    def test_missing_file_returns_none_without_raising(
        self, tmp_path,
    ) -> None:
        """An unreadable source is "no evidence", not a hard failure."""
        assert read_processed_tiles(tmp_path / "nope.geojson") is None

    def test_malformed_json_returns_none_without_raising(
        self, tmp_path,
    ) -> None:
        """Truncated or corrupt JSON degrades to the fallback path."""
        path = tmp_path / "broken.geojson"
        path.write_text('{"type": "FeatureCollection", "features": [',
                        encoding="utf-8")
        assert read_processed_tiles(path) is None

    def test_non_list_record_returns_none(self, tmp_path) -> None:
        """A ``processed_tiles`` value of the wrong type is not evidence."""
        path = tmp_path / "odd.geojson"
        path.write_text(json.dumps({
            "type": "FeatureCollection",
            "features": [],
            "processed_tiles": 240,
        }), encoding="utf-8")
        assert read_processed_tiles(path) is None

    def test_real_e72_artefact_reports_240_tiles(self) -> None:
        """The live E72 study pass really does record 240 processed tiles.

        Anchors the synthetic fixtures above to the artefact that caused
        the erratum. Skipped if the output tree is not present (the
        ``outputs/`` directory is gitignored in some checkouts).
        """
        path = (
            PROJECT_ROOT / "outputs" / "h11"
            / "consensus-384-UNINTENDED-T1.0" / "384" / "run_1"
            / "detections_384_run01.geojson"
        )
        if not path.exists():
            pytest.skip(f"artefact not present in this checkout: {path}")
        tiles = read_processed_tiles(path)
        assert tiles is not None
        assert len(tiles) == 240


# =========================================================================
# BCa BOOTSTRAP TESTS
# =========================================================================


@pytest.mark.tier1
class TestBcaCiFromIndices:
    """Unit tests for :func:`_bca_ci_from_indices`."""

    def test_bca_correctness_on_known_distribution(self) -> None:
        """BCa CI brackets the analytical mean of a non-degenerate sample.

        Uses a per-tile statistic with known mean and a moderate spread,
        so the bootstrap distribution is non-degenerate and BCa should
        succeed (no fallback). Asserts: (a) ``method`` is ``'BCa'``,
        (b) the CI brackets the population mean, and (c) the bounds are
        finite.
        """
        rng = np.random.default_rng(0)
        n = 200
        values = rng.normal(loc=0.5, scale=0.1, size=n)
        indices = np.arange(n)

        def stat(idx: np.ndarray) -> float:
            return float(values[idx].mean())

        result = _bca_ci_from_indices(
            indices, stat, n_iterations=2000, random_seed=42,
        )
        assert result["method"] == "BCa"
        assert np.isfinite(result["ci_lower"])
        assert np.isfinite(result["ci_upper"])
        # BCa CI should bracket the true mean with very high probability
        # at this sample size and CI width.
        assert result["ci_lower"] <= 0.5 <= result["ci_upper"]
        # Bootstrap mean should be very close to the sample mean.
        assert abs(result["mean"] - values.mean()) < 0.01

    def test_constant_statistic_returns_constant_ci(self) -> None:
        """Constant statistic => CI = [const, const] (BCa or fallback).

        scipy's BCa handles a perfectly constant bootstrap distribution
        gracefully — the jackknife acceleration is undefined but the
        CI bounds collapse to the constant value. The exact ``method``
        label depends on the scipy version; we accept either ``BCa``
        or ``percentile_fallback`` as long as the bounds are correct.
        """
        indices = np.arange(50)

        def constant_stat(idx: np.ndarray) -> float:
            return 0.42

        result = _bca_ci_from_indices(
            indices, constant_stat, n_iterations=200, random_seed=42,
        )
        assert result["mean"] == pytest.approx(0.42)
        assert result["ci_lower"] == pytest.approx(0.42)
        assert result["ci_upper"] == pytest.approx(0.42)
        assert result["method"] in {"BCa", "percentile_fallback"}

    def test_degenerate_jackknife_falls_back_to_percentile(self) -> None:
        """Degenerate jackknife => fallback to percentile.

        The known BCa failure mode is a degenerate jackknife
        acceleration estimate — the formula divides by ``sum(dens)**1.5``
        which can be zero when leave-one-out resamples yield identical
        statistics. The pattern that reliably reproduces this in
        scipy 1.17+ is a near-constant statistic from a highly skewed
        distribution: 95 % of tiles contribute zero and 5 % contribute
        the same scalar. :func:`_bca_ci_from_indices` should detect the
        ``NaN`` bounds and switch to the deterministic percentile path.
        """
        # 100 tiles: 95 zero-counts, 5 with TP=1. F1 from any resample
        # is determined entirely by how many of the 5 active tiles are
        # included — a small, integer-valued distribution that triggers
        # the BCa jackknife to divide by zero.
        n_tiles = 100
        tp_arr = np.zeros(n_tiles)
        tp_arr[:5] = 1.0
        indices = np.arange(n_tiles)

        def sparse_f1(idx: np.ndarray) -> float:
            idx = np.asarray(idx, dtype=int)
            tp = float(tp_arr[idx].sum())
            # Pretend FP=FN=0 so F1 collapses to 1 when any TP, else 0.
            return 1.0 if tp > 0 else 0.0

        result = _bca_ci_from_indices(
            indices, sparse_f1, n_iterations=500, random_seed=42,
        )
        # Either BCa succeeded (older scipy) or fell back (newer scipy).
        # Both are acceptable as long as the bounds are finite.
        assert np.isfinite(result["ci_lower"])
        assert np.isfinite(result["ci_upper"])
        assert result["method"] in {"BCa", "percentile_fallback"}

    def test_reproducibility_with_seed(self) -> None:
        """Same seed => identical CI bounds across calls."""
        rng = np.random.default_rng(0)
        values = rng.normal(loc=0.3, scale=0.05, size=80)
        indices = np.arange(80)

        def stat(idx: np.ndarray) -> float:
            return float(values[idx].mean())

        a = _bca_ci_from_indices(
            indices, stat, n_iterations=500, random_seed=7,
        )
        b = _bca_ci_from_indices(
            indices, stat, n_iterations=500, random_seed=7,
        )
        assert a["ci_lower"] == pytest.approx(b["ci_lower"])
        assert a["ci_upper"] == pytest.approx(b["ci_upper"])
        assert a["mean"] == pytest.approx(b["mean"])


@pytest.mark.tier1
class TestComputeBcaCiFromDistribution:
    """Unit tests for :func:`_compute_bca_ci` (bootstrap-distribution input)."""

    def test_normal_distribution_bca(self) -> None:
        """A normal-shaped bootstrap distribution returns a finite BCa CI."""
        rng = np.random.default_rng(0)
        diffs = rng.normal(loc=0.05, scale=0.02, size=1000)
        result = _compute_bca_ci(diffs)
        assert result["method"] == "BCa"
        assert result["ci_lower"] < result["mean"] < result["ci_upper"]
        # The BCa CI should bracket the sample mean of the distribution.
        assert result["ci_lower"] <= float(np.mean(diffs)) <= result["ci_upper"]

    def test_constant_distribution_falls_back(self) -> None:
        """Constant distribution => fallback to percentile method."""
        const = np.full(500, 0.1)
        result = _compute_bca_ci(const)
        assert result["method"] == "percentile_fallback"

    def test_empty_distribution_returns_none(self) -> None:
        """Empty input => null fields (mirrors legacy ``_compute_ci``)."""
        result = _compute_bca_ci([])
        assert result["mean"] is None
        assert result["ci_lower"] is None
        assert result["ci_upper"] is None


# =========================================================================
# bootstrap_ci INTEGRATION TESTS
# =========================================================================


@pytest.mark.tier1
class TestBootstrapCiIntegration:
    """Integration tests for :func:`bootstrap_ci` with synthetic GeoData."""

    def test_returns_new_schema_fields(self) -> None:
        """Result dict carries the schema 1.1 additions.

        Pins the new fields introduced by the BCa + Mitigation 3 commit:
        ``f1.point``, ``f1.method``, top-level ``coverage`` block,
        ``bootstrap_method``, and ``bootstrap_lib``. Legacy fields
        (``f1.mean``, ``f1.ci_lower``, ``f1.ci_upper``, plus
        backwards-compat ``mean`` / ``ci_lower`` / ``ci_upper``) must
        also still be present.
        """
        gdf_det, gdf_ref, gdf_bounds = _make_synthetic_eval_inputs(
            n_tiles=10, n_active_tiles=8,
        )
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=200, random_seed=42,
        )
        # New schema fields
        assert "coverage" in ci
        assert ci["bootstrap_method"] == BOOTSTRAP_METHOD
        assert ci["bootstrap_lib"] == BOOTSTRAP_LIB
        for metric in ("f1", "precision", "recall"):
            assert "point" in ci[metric], f"{metric} missing 'point' field"
            assert "method" in ci[metric], f"{metric} missing 'method' field"
            # ``method`` is one of {'BCa', 'percentile_fallback'}.
            assert ci[metric]["method"] in {"BCa", "percentile_fallback"}
        # Legacy fields retained for back-compat.
        assert "mean" in ci
        assert "ci_lower" in ci
        assert "ci_upper" in ci
        # Coverage block has the documented shape.
        cov = ci["coverage"]
        for key in (
            "n_tiles", "n_zero_count_tiles", "zero_fraction",
            "threshold", "coverage_status",
        ):
            assert key in cov

    def test_point_estimates_deterministic(self) -> None:
        """``f1.point`` is identical regardless of bootstrap iteration count.

        The point estimate is computed by :func:`calculate_f1_internal`
        across all tiles — it does NOT depend on the bootstrap
        resampling loop. Two calls with different ``n_iterations`` must
        therefore produce identical ``point`` fields. This is the core
        guarantee that paper-headline numbers are unchanged by the BCa
        upgrade.
        """
        gdf_det, gdf_ref, gdf_bounds = _make_synthetic_eval_inputs(
            n_tiles=10, n_active_tiles=8,
        )
        ci_low = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=100, random_seed=42,
        )
        ci_high = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=500, random_seed=42,
        )
        assert ci_low["f1"]["point"] == pytest.approx(ci_high["f1"]["point"])
        assert ci_low["precision"]["point"] == pytest.approx(
            ci_high["precision"]["point"],
        )
        assert ci_low["recall"]["point"] == pytest.approx(
            ci_high["recall"]["point"],
        )

    def test_point_matches_calculate_f1_internal(self) -> None:
        """``f1.point`` matches :func:`calculate_f1_internal` exactly.

        The headline F1 reported in the paper comes from
        :func:`calculate_f1_internal`. ``f1.point`` is just an alias —
        any drift here would mean the bootstrap pipeline is reporting a
        different point estimate than the analytic computation, which
        would be a confusing regression.
        """
        gdf_det, gdf_ref, gdf_bounds = _make_synthetic_eval_inputs(
            n_tiles=10, n_active_tiles=8,
        )
        p_pt, r_pt, f1_pt = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=20,
        )
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=200, random_seed=42,
        )
        assert ci["f1"]["point"] == pytest.approx(f1_pt)
        assert ci["precision"]["point"] == pytest.approx(p_pt)
        assert ci["recall"]["point"] == pytest.approx(r_pt)

    def test_dense_synthetic_does_not_flag_sparse(self) -> None:
        """Dense synthetic data => coverage_status = 'normal'.

        Mirrors a matched-grid evaluation where most tiles have signal.
        """
        gdf_det, gdf_ref, gdf_bounds = _make_synthetic_eval_inputs(
            n_tiles=10, n_active_tiles=8,
        )
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=200, random_seed=42,
        )
        assert ci["coverage"]["zero_fraction"] < 0.5
        assert ci["coverage"]["coverage_status"] == COVERAGE_STATUS_NORMAL

    def test_sparse_synthetic_flags_sparse(self) -> None:
        """Sparse synthetic (>= 80 % empty tiles) => sparse_cross_grid.

        Reproduces the production cross-grid regime (~80 % zero coverage).
        Asserts the flag fires and the per-tile zero-fraction is in the
        expected range.
        """
        gdf_det, gdf_ref, gdf_bounds = _make_synthetic_eval_inputs(
            n_tiles=50, n_active_tiles=10,  # 80 % empty tiles
        )
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=200, random_seed=42,
        )
        assert ci["coverage"]["zero_fraction"] > 0.5
        assert ci["coverage"]["coverage_status"] == COVERAGE_STATUS_SPARSE

    def test_processed_tiles_plumbs_through_to_coverage(self) -> None:
        """``bootstrap_ci`` forwards ``processed_tiles`` to the guard (E72).

        The same dense inputs read ``normal`` without evidence and
        ``partial_coverage`` when told that half the bounds tiles were
        never processed. Metric values are untouched either way — the
        parameter affects diagnostics only.
        """
        gdf_det, gdf_ref, gdf_bounds = _make_synthetic_eval_inputs(
            n_tiles=10, n_active_tiles=8,
        )
        all_tiles = set(gdf_bounds["tile_name"])
        covered = set(sorted(all_tiles)[:5])

        baseline = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=200, random_seed=42,
        )
        flagged = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=200, random_seed=42,
            processed_tiles=covered,
        )

        assert baseline["coverage"]["coverage_status"] == (
            COVERAGE_STATUS_NORMAL
        )
        assert flagged["coverage"]["coverage_status"] == (
            COVERAGE_STATUS_PARTIAL
        )
        assert flagged["coverage"]["n_unprocessed_tiles"] == 5
        assert flagged["coverage"]["coverage_detail"] == (
            "partial: 5/10 tiles unprocessed"
        )
        # Diagnostics only: the metrics themselves must be identical.
        assert flagged["f1"]["point"] == baseline["f1"]["point"]
        assert flagged["f1"]["ci_lower"] == baseline["f1"]["ci_lower"]

    def test_legacy_keys_present_for_back_compat(self) -> None:
        """Top-level ``mean`` / ``ci_lower`` / ``ci_upper`` still emitted.

        Several scripts (compare_wbf_vs_greedy*.py, evaluate_pv_results.py)
        index into ``ci["mean"]`` directly. Removing those keys would
        be a silent breaking change. Pin them here.
        """
        gdf_det, gdf_ref, gdf_bounds = _make_synthetic_eval_inputs(
            n_tiles=10, n_active_tiles=8,
        )
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=100, random_seed=42,
        )
        assert ci["mean"] == pytest.approx(ci["f1"]["mean"])
        assert ci["ci_lower"] == pytest.approx(ci["f1"]["ci_lower"])
        assert ci["ci_upper"] == pytest.approx(ci["f1"]["ci_upper"])

    def test_empty_bounds_returns_empty_dict(self) -> None:
        """Empty bounds => empty dict (preserves legacy behaviour)."""
        gdf_bounds = gpd.GeoDataFrame(
            {"tile_name": []}, geometry=[], crs="EPSG:32635",
        )
        gdf_det = gpd.GeoDataFrame(
            {"source_tile": []}, geometry=[], crs="EPSG:32635",
        )
        gdf_ref = gpd.GeoDataFrame(geometry=[], crs="EPSG:32635")
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=10, random_seed=42,
        )
        assert ci == {}


# --- ci_unreliable is measured, not inferred from sparseness (2026-08-19) -----
#
# The flag used to fire on `sparse_cross_grid`, a >50 % zero-count-tile
# heuristic introduced to catch percentile-method intervals that excluded their
# own point estimate. BCa fixed that pathology in the same commit and the
# heuristic was never revisited, so it ended up warning about a defect that no
# longer occurs — on 91 of 337 conditions at the 20 m headline, including the
# gold-standard cell. These tests pin the corrected rule.

_CI = {
    "f1": {"ci_lower": 0.70, "ci_upper": 0.80},
    "precision": {"ci_lower": 0.60, "ci_upper": 0.90},
    "recall": {"ci_lower": 0.60, "ci_upper": 0.90},
}


@pytest.mark.tier1
def test_sparse_coverage_alone_does_not_mark_ci_unreliable():
    """A mostly-empty scope is a fact about the scope, not a broken interval."""
    from scripts.evaluate_detections import assess_ci_reliability

    unreliable, excludes = assess_ci_reliability(
        _CI, 0.75, 0.70, 0.70, "sparse_cross_grid")
    assert unreliable is False
    assert excludes is False


@pytest.mark.tier1
def test_partial_coverage_still_marks_ci_unreliable():
    """E72 is untouched: uncovered bounds break the point estimate too."""
    from scripts.evaluate_detections import assess_ci_reliability

    unreliable, excludes = assess_ci_reliability(
        _CI, 0.75, 0.70, 0.70, "partial_coverage")
    assert unreliable is True
    assert excludes is False, "partial coverage is a separate ground"


@pytest.mark.tier1
@pytest.mark.parametrize(
    ("f1", "precision", "recall"),
    [(0.95, 0.70, 0.70), (0.75, 0.20, 0.70), (0.75, 0.70, 0.99)],
)
def test_interval_excluding_its_point_estimate_marks_ci_unreliable(
    f1, precision, recall
):
    """The actual pathology, tested on each metric that carries an interval."""
    from scripts.evaluate_detections import assess_ci_reliability

    unreliable, excludes = assess_ci_reliability(
        _CI, f1, precision, recall, "normal")
    assert excludes is True
    assert unreliable is True


@pytest.mark.tier1
def test_healthy_dense_case_is_not_flagged():
    from scripts.evaluate_detections import assess_ci_reliability

    assert assess_ci_reliability(_CI, 0.75, 0.70, 0.70, "normal") == (False, False)


@pytest.mark.tier1
def test_absent_bounds_do_not_flag():
    """A metric with no interval cannot exclude its point estimate."""
    from scripts.evaluate_detections import assess_ci_reliability

    ci = {"f1": {"ci_lower": None, "ci_upper": None},
          "precision": {}, "recall": {}}
    assert assess_ci_reliability(ci, 0.75, 0.70, 0.70, "normal") == (False, False)
