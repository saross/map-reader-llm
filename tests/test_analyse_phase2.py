"""
Tests for Phase 2 multi-condition analysis functionality.

Tier 1 unit tests for the analyse_phase2_results.py script, covering:

- Benjamini-Hochberg FDR correction for multiple pairwise comparisons.
- Per-run file discovery (no .geojson extension, no pass subdirectories).
- Per-run loading returning list of (run, GeoDataFrame) tuples.
- Multi-run bootstrap with synthetic data.
- Integration test against existing image-only runs (if available).
"""

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

PROJECT_ROOT = Path(__file__).parent.parent


def _phase2a_image_only_detections_present() -> bool:
    """Return True only if at least one Phase 2a image-only run directory
    contains a detection file (not just metadata).

    Checking for the run_1 directory alone is insufficient: a fresh checkout
    on a machine that lacks the gitignored bulk detection outputs may have
    the run skeleton (created by the API harness) without any detections,
    and the integration test would then fail rather than skip.
    """
    base = PROJECT_ROOT / "outputs" / "phase2a" / "image-only"
    if not base.exists():
        return False
    for run_dir in base.glob("run_*"):
        if not run_dir.is_dir():
            continue
        for f in run_dir.iterdir():
            if not f.is_file():
                continue
            if f.name.endswith((".meta.json", ".tiles.json")):
                continue
            if "_fp." in f.name or "_fn." in f.name:
                continue
            stem = f.stem if "." in f.name else f.name
            if stem.endswith(("_fp", "_fn")):
                continue
            return True
    return False


from scripts.analyse_phase2_results import apply_fdr_correction, load_condition_results
from scripts.lib_advanced_metrics import (
    aggregate_tile_metrics,
    bootstrap_ci,
    bootstrap_effect_size_ci,
    bootstrap_multi_run_ci,
    bootstrap_multi_run_effect_size_ci,
    calculate_f1_internal,
    compute_per_tile_tp_fp_fn,
)

pytestmark = pytest.mark.tier1


@pytest.mark.tier1
class TestApplyFdrCorrection:
    """BH over permutation p-values (D42); the CI-position pseudo-p is gone."""

    @staticmethod
    def _cmp(p_value: float | None, ci: tuple[float, float] = (-0.01, 0.01)) -> dict:
        diff = {"mean": 0.0, "ci_lower": ci[0], "ci_upper": ci[1]}
        if p_value is not None:
            diff["p_value"] = p_value
        return {"condition_a": "A", "condition_b": "B", "f1_difference": diff}

    def test_empty_list_returns_empty(self) -> None:
        """Empty pairwise results should return empty list."""
        assert apply_fdr_correction([]) == []

    def test_single_small_p_is_significant(self) -> None:
        """One comparison at p = 0.01 is significant raw and after BH."""
        result = apply_fdr_correction([self._cmp(0.01)], q=0.05)
        assert result[0]["initially_significant"] is True
        assert result[0]["fdr_significant"] is True
        assert result[0]["fdr_adjusted_p"] == pytest.approx(0.01)

    def test_single_large_p_is_not_significant(self) -> None:
        """One comparison at p = 0.3 is not significant."""
        result = apply_fdr_correction([self._cmp(0.3)], q=0.05)
        assert result[0]["initially_significant"] is False
        assert result[0]["fdr_significant"] is False

    def test_a_comparison_without_a_p_value_is_refused(self) -> None:
        """No permutation p: refused, never scored from its CI."""
        with pytest.raises(ValueError, match="pseudo-p"):
            apply_fdr_correction([self._cmp(None, ci=(0.02, 0.08))])

    def test_bh_step_up_on_a_known_example(self) -> None:
        """p = (0.01, 0.04, 0.03, 0.5): BH keeps only the first at q = 0.05."""
        result = apply_fdr_correction(
            [self._cmp(p) for p in (0.01, 0.04, 0.03, 0.5)], q=0.05)
        assert [r["initially_significant"] for r in result] == [True, True, True, False]
        assert [r["fdr_significant"] for r in result] == [True, False, False, False]
        assert [r["fdr_adjusted_p"] for r in result] == pytest.approx(
            [0.04, 0.0533333, 0.0533333, 0.5], abs=1e-6)

    def test_q_value_affects_threshold(self) -> None:
        """At q = 0.10 the same four comparisons give three discoveries."""
        result = apply_fdr_correction(
            [self._cmp(p) for p in (0.01, 0.04, 0.03, 0.5)], q=0.10)
        assert sum(r["fdr_significant"] for r in result) == 3

    def test_ci_reading_is_descriptive_only(self) -> None:
        """A CI excluding zero does not make a large p significant."""
        result = apply_fdr_correction([self._cmp(0.4, ci=(0.001, 0.05))])
        assert result[0]["ci_excludes_zero"] is True
        assert result[0]["fdr_significant"] is False

    def test_preserves_original_fields(self) -> None:
        """FDR correction preserves every field it was given."""
        cmp = self._cmp(0.01, ci=(0.02, 0.08))
        cmp.update({
            "precision_difference": {"mean": 0.03, "ci_lower": 0.01, "ci_upper": 0.05},
            "recall_difference": {"mean": 0.07, "ci_lower": 0.04, "ci_upper": 0.10},
            "n_tiles": 60,
            "n_iterations": 1000,
        })
        result = apply_fdr_correction([cmp], q=0.05)
        assert result[0]["condition_a"] == "A"
        assert result[0]["precision_difference"]["mean"] == 0.03
        assert result[0]["recall_difference"]["mean"] == 0.07
        assert result[0]["n_tiles"] == 60
        assert result[0]["n_iterations"] == 1000

    def test_adds_significance_fields(self) -> None:
        """The correction adds boolean flags and the adjusted p."""
        result = apply_fdr_correction([self._cmp(0.02)], q=0.05)
        assert isinstance(result[0]["initially_significant"], bool)
        assert isinstance(result[0]["fdr_significant"], bool)
        assert isinstance(result[0]["fdr_adjusted_p"], float)

    def test_identical_multi_run_conditions_give_p_one(self) -> None:
        """End to end: identical runs on both arms give a permutation p of 1."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=3, n_tiles=8, detections_per_tile=2, seed=5,
        )
        effect = bootstrap_multi_run_effect_size_ci(
            run_gdfs, run_gdfs, gdf_ref, gdf_bounds,
            n_iterations=50, random_seed=42, return_p_values=True,
        )
        assert effect["f1_difference"]["p_value"] == 1.0
        assert effect["permutation"]["n_runs"] == 3
        assert "run blocks swap" in effect["permutation"]["statistic"]

@pytest.mark.tier1
class TestApplyFdrCorrectionEdgeCases:
    """Edge cases for the permutation-p FDR correction (D42)."""

    def test_missing_f1_difference_key_is_refused(self) -> None:
        """A comparison with no f1_difference has no p: refused."""
        with pytest.raises(ValueError):
            apply_fdr_correction([{"condition_a": "A", "condition_b": "B"}], q=0.05)

    def test_missing_ci_bounds(self) -> None:
        """A p-value without CI bounds is tested; the CI reading is False."""
        result = apply_fdr_correction([{
            "condition_a": "A", "condition_b": "B",
            "f1_difference": {"mean": 0.05, "p_value": 0.001},
        }], q=0.05)
        assert result[0]["fdr_significant"] is True
        assert result[0]["ci_excludes_zero"] is False

    def test_p_exactly_at_alpha_is_not_initially_significant(self) -> None:
        """The raw threshold is strict: p = 0.05 is not below 0.05."""
        result = apply_fdr_correction([{
            "condition_a": "A", "condition_b": "B",
            "f1_difference": {"mean": 0.02, "p_value": 0.05},
        }], q=0.05)
        assert result[0]["initially_significant"] is False
        assert result[0]["fdr_significant"] is True  # BH uses adjusted <= q

    def test_very_large_number_of_comparisons(self) -> None:
        """100 comparisons: BH never finds more than the raw threshold."""
        pairwise = [{
            "condition_a": f"A{i}", "condition_b": f"B{i}",
            "f1_difference": {"mean": 0.03, "p_value": (i + 1) / 1000 if i < 50 else 0.5},
        } for i in range(100)]
        result = apply_fdr_correction(pairwise, q=0.05)
        assert len(result) == 100
        n_raw = sum(r["initially_significant"] for r in result)
        n_fdr = sum(r["fdr_significant"] for r in result)
        assert n_fdr <= n_raw
        assert n_raw == 49  # (i+1)/1000 < 0.05 for i < 49

# Import check
def test_import_apply_fdr_correction() -> None:
    """Verify that apply_fdr_correction can be imported."""
    from scripts.analyse_phase2_results import apply_fdr_correction as imported_fn
    assert callable(imported_fn)


def _make_detection_geojson(features: list[dict]) -> dict:
    """Create a minimal GeoJSON FeatureCollection for testing.

    Args:
        features: List of GeoJSON Feature dictionaries.

    Returns:
        GeoJSON FeatureCollection dictionary.
    """
    return {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:EPSG::32635"},
        },
        "features": features,
    }


def _make_detection_feature(
    tile_name: str = "K-35-052-4_32635_tile_001.png",
) -> dict:
    """Create a minimal GeoJSON detection Feature for testing.

    Args:
        tile_name: Source tile identifier for the detection.

    Returns:
        GeoJSON Feature dictionary.
    """
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [500000, 4700000],
                    [500020, 4700000],
                    [500020, 4700020],
                    [500000, 4700020],
                    [500000, 4700000],
                ]
            ],
        },
        "properties": {
            "source_tile": tile_name,
            "label": "mound",
            "subtype": "burial_mound",
            "confidence": "high",
        },
    }


@pytest.mark.tier1
class TestLoadConditionResults:
    """Tests for load_condition_results() per-run file discovery."""

    def test_missing_condition_dir_returns_empty(self, tmp_path: Path) -> None:
        """Missing condition directory should return empty list."""
        result = load_condition_results(tmp_path, "nonexistent")
        assert result == []

    def test_no_run_dirs_returns_empty(self, tmp_path: Path) -> None:
        """Condition dir with no run_* subdirectories should return empty."""
        (tmp_path / "image-only").mkdir()
        result = load_condition_results(tmp_path, "image-only")
        assert result == []

    def test_discovers_files_without_geojson_extension(
        self, tmp_path: Path
    ) -> None:
        """Detection files without .geojson extension should be loaded."""
        cond_dir = tmp_path / "image-only" / "run_1"
        cond_dir.mkdir(parents=True)

        # Create detection file without .geojson extension (as produced
        # by the runner)
        det_file = cond_dir / "detections_image-only_run01"
        geojson_data = _make_detection_geojson([_make_detection_feature()])
        det_file.write_text(json.dumps(geojson_data))

        result = load_condition_results(tmp_path, "image-only")

        assert len(result) == 1
        run_num, gdf = result[0]
        assert run_num == 1
        assert len(gdf) == 1

    def test_excludes_meta_fp_fn_files(self, tmp_path: Path) -> None:
        """Should exclude .meta.json, _fp.*, and _fn.* files."""
        cond_dir = tmp_path / "image-only" / "run_1"
        cond_dir.mkdir(parents=True)

        geojson_data = _make_detection_geojson([_make_detection_feature()])

        # Main detection file
        (cond_dir / "detections_image-only_run01").write_text(
            json.dumps(geojson_data)
        )
        # Files that should be excluded
        (cond_dir / "detections_image-only_run01.meta.json").write_text("{}")
        (cond_dir / "detections_image-only_run01_fp.geojson").write_text(
            json.dumps(geojson_data)
        )
        (cond_dir / "detections_image-only_run01_fn.geojson").write_text(
            json.dumps(geojson_data)
        )

        result = load_condition_results(tmp_path, "image-only")

        assert len(result) == 1
        _, gdf = result[0]
        assert len(gdf) == 1  # Only from the main file

    def test_returns_sorted_by_run_number(self, tmp_path: Path) -> None:
        """Results should be sorted by run number."""
        geojson_data = _make_detection_geojson([_make_detection_feature()])

        for run_num in [3, 1, 2]:
            run_dir = tmp_path / "image-only" / f"run_{run_num}"
            run_dir.mkdir(parents=True)
            det_file = run_dir / f"detections_image-only_run{run_num:02d}"
            det_file.write_text(json.dumps(geojson_data))

        result = load_condition_results(tmp_path, "image-only")

        assert len(result) == 3
        assert [r[0] for r in result] == [1, 2, 3]

    def test_adds_run_column_to_geodataframe(self, tmp_path: Path) -> None:
        """Each GeoDataFrame should have a 'run' column with the run number."""
        cond_dir = tmp_path / "image-only" / "run_5"
        cond_dir.mkdir(parents=True)

        geojson_data = _make_detection_geojson([_make_detection_feature()])
        (cond_dir / "detections_image-only_run05").write_text(
            json.dumps(geojson_data)
        )

        result = load_condition_results(tmp_path, "image-only")

        assert len(result) == 1
        run_num, gdf = result[0]
        assert run_num == 5
        assert (gdf["run"] == 5).all()

    def test_no_pass_subdirectory_iteration(self, tmp_path: Path) -> None:
        """Should NOT look for pass_N subdirectories inside run dirs."""
        run_dir = tmp_path / "image-only" / "run_1"
        run_dir.mkdir(parents=True)

        # Put detection file in a pass_1 subdir — should NOT be found
        pass_dir = run_dir / "pass_1"
        pass_dir.mkdir()
        geojson_data = _make_detection_geojson([_make_detection_feature()])
        (pass_dir / "detections_image-only_run01.geojson").write_text(
            json.dumps(geojson_data)
        )

        result = load_condition_results(tmp_path, "image-only")

        # Should be empty — pass_1 subdir is not searched
        assert len(result) == 0


@pytest.mark.tier1
class TestLoadConditionResultsIntegration:
    """Integration test against existing image-only runs (if available)."""

    @pytest.mark.skipif(
        not _phase2a_image_only_detections_present(),
        reason="Existing Phase 2a image-only detection files not available",
    )
    def test_loads_existing_image_only_runs(self) -> None:
        """Load existing image-only runs from outputs/phase2a/."""
        study_dir = PROJECT_ROOT / "outputs" / "phase2a"
        result = load_condition_results(study_dir, "image-only")

        assert len(result) >= 3, "Expected at least 3 image-only runs"

        for run_num, gdf in result:
            assert run_num > 0
            assert len(gdf) > 0, f"Run {run_num} has 0 features"
            assert "source_tile" in gdf.columns
            assert "run" in gdf.columns


# ============================================================================
# Multi-Run Bootstrap Tests
# ============================================================================

def _make_synthetic_runs(
    n_runs: int = 3,
    n_tiles: int = 10,
    detections_per_tile: int = 2,
    seed: int = 42,
) -> tuple[
    list[tuple[int, gpd.GeoDataFrame]],
    gpd.GeoDataFrame,
    gpd.GeoDataFrame,
]:
    """
    Create synthetic per-run detection data for bootstrap testing.

    Args:
        n_runs: Number of runs to generate.
        n_tiles: Number of tiles per run.
        detections_per_tile: Number of detections per tile.
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (run_gdfs, gdf_ref, gdf_bounds) for bootstrap functions.
    """
    rng = np.random.RandomState(seed)

    # Create tile names and bounds
    tile_names = [f"K-35-052-4_32635_tile_{i:03d}.png" for i in range(n_tiles)]

    bounds_rows = []
    for i, tname in enumerate(tile_names):
        x0 = 500000 + i * 100
        y0 = 4700000
        geom = box(x0, y0, x0 + 100, y0 + 100)
        bounds_rows.append({"tile_name": tname, "geometry": geom})
    gdf_bounds = gpd.GeoDataFrame(bounds_rows, crs="EPSG:32635")

    # Create reference points (one per tile for simplicity)
    ref_rows = []
    for i, _tname in enumerate(tile_names):
        x0 = 500000 + i * 100 + 50
        y0 = 4700050
        ref_rows.append({
            "geometry": Point(x0, y0),
            "Map": "K-35-052-4_32635",
            "Symbol": "Burial Mound",
        })
    gdf_ref = gpd.GeoDataFrame(ref_rows, crs="EPSG:32635")

    # Create per-run detections
    run_gdfs = []
    for run_num in range(1, n_runs + 1):
        det_rows = []
        for i, tname in enumerate(tile_names):
            for _d in range(detections_per_tile):
                # Add some noise so runs differ
                x0 = 500000 + i * 100 + 50 + rng.normal(0, 5)
                y0 = 4700050 + rng.normal(0, 5)
                det_rows.append({
                    "source_tile": tname,
                    "geometry": box(x0 - 5, y0 - 5, x0 + 5, y0 + 5),
                    "label": "mound",
                    "subtype": "burial_mound",
                })
        gdf_det = gpd.GeoDataFrame(det_rows, crs="EPSG:32635")
        gdf_det["run"] = run_num
        run_gdfs.append((run_num, gdf_det))

    return run_gdfs, gdf_ref, gdf_bounds


@pytest.mark.tier1
class TestBootstrapMultiRunCi:
    """Tests for bootstrap_multi_run_ci() with synthetic data."""

    def test_returns_expected_structure(self) -> None:
        """Output should have f1, precision, recall dicts with CIs."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(n_runs=3)

        result = bootstrap_multi_run_ci(
            run_gdfs, gdf_ref, gdf_bounds,
            n_iterations=50,
            random_seed=42,
        )

        for metric in ["f1", "precision", "recall"]:
            assert metric in result, f"Missing '{metric}' in result"
            assert "mean" in result[metric]
            assert "ci_lower" in result[metric]
            assert "ci_upper" in result[metric]
            # CI lower should be <= mean <= CI upper (with floating-point tolerance)
            assert result[metric]["ci_lower"] <= result[metric]["mean"] + 1e-12
            assert result[metric]["mean"] <= result[metric]["ci_upper"] + 1e-12

        assert result["n_runs"] == 3
        assert result["n_tiles"] == 10

    def test_empty_run_list_returns_empty(self) -> None:
        """Empty run list should return empty dict."""
        _, gdf_ref, gdf_bounds = _make_synthetic_runs()
        result = bootstrap_multi_run_ci(
            [], gdf_ref, gdf_bounds,
            n_iterations=10,
        )
        assert result == {}

    def test_single_run_comparable_to_standard_bootstrap(self) -> None:
        """With K=1 run, multi-run CI should approximate standard bootstrap CI."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(n_runs=1)

        result = bootstrap_multi_run_ci(
            run_gdfs, gdf_ref, gdf_bounds,
            n_iterations=100,
            random_seed=42,
        )

        # Just check it produces reasonable values
        assert 0 <= result["f1"]["mean"] <= 1
        assert result["f1"]["ci_lower"] >= 0

    def test_reproducibility_with_seed(self) -> None:
        """Same seed should produce identical results."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs()

        result1 = bootstrap_multi_run_ci(
            run_gdfs, gdf_ref, gdf_bounds,
            n_iterations=50,
            random_seed=123,
        )
        result2 = bootstrap_multi_run_ci(
            run_gdfs, gdf_ref, gdf_bounds,
            n_iterations=50,
            random_seed=123,
        )

        assert result1["f1"]["mean"] == result2["f1"]["mean"]
        assert result1["f1"]["ci_lower"] == result2["f1"]["ci_lower"]


@pytest.mark.tier1
class TestBootstrapMultiRunEffectSizeCi:
    """Tests for bootstrap_multi_run_effect_size_ci() with synthetic data."""

    def test_returns_expected_structure(self) -> None:
        """Output should have f1_difference, precision_difference, recall_difference."""
        run_gdfs_a, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=3, seed=42,
        )
        run_gdfs_b, _, _ = _make_synthetic_runs(
            n_runs=3, seed=99,
        )

        result = bootstrap_multi_run_effect_size_ci(
            run_gdfs_a, run_gdfs_b,
            gdf_ref, gdf_bounds,
            n_iterations=50,
            random_seed=42,
        )

        for key in ["f1_difference", "precision_difference", "recall_difference"]:
            assert key in result, f"Missing '{key}' in result"
            assert "mean" in result[key]
            assert "ci_lower" in result[key]
            assert "ci_upper" in result[key]

        assert result["n_tiles"] == 10
        assert result["n_runs_a"] == 3
        assert result["n_runs_b"] == 3

    def test_identical_conditions_yield_zero_difference(self) -> None:
        """Same data for both conditions should yield ~0 difference."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(n_runs=3)

        result = bootstrap_multi_run_effect_size_ci(
            run_gdfs, run_gdfs,
            gdf_ref, gdf_bounds,
            n_iterations=50,
            random_seed=42,
        )

        # Mean difference should be exactly 0 (same data)
        assert result["f1_difference"]["mean"] == pytest.approx(0, abs=1e-10)
        # CI should contain 0
        assert result["f1_difference"]["ci_lower"] <= 0
        assert result["f1_difference"]["ci_upper"] >= 0

    def test_empty_condition_returns_error(self) -> None:
        """Empty run list for one condition should return error."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs()
        result = bootstrap_multi_run_effect_size_ci(
            run_gdfs, [],
            gdf_ref, gdf_bounds,
            n_iterations=10,
        )
        assert "error" in result


# ============================================================================
# Bootstrap CI Bias Regression Tests (Errata E26)
# ============================================================================

@pytest.mark.tier1
class TestBootstrapMeanApproximatesPointEstimate:
    """Regression tests verifying bootstrap mean ≈ point estimate.

    The key invariant: the mean of the bootstrap distribution should
    approximate the point estimate computed from all tiles. A systematic
    deflation would indicate the duplicate-tile de-duplication bias
    that E26 fixes.
    """

    def test_single_run_bootstrap_mean_near_point_estimate(self) -> None:
        """Bootstrap mean F1 should be within 0.02 of point estimate (K=1)."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=1, n_tiles=10, detections_per_tile=2, seed=42,
        )
        _run_num, gdf_det = run_gdfs[0]

        # Point estimate
        _p, _r, f1_point = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=20,
        )

        # Bootstrap CI
        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=500,
            random_seed=42,
        )

        assert abs(ci["f1"]["mean"] - f1_point) < 0.02, (
            f"Bootstrap mean F1 ({ci['f1']['mean']:.4f}) deviates from "
            f"point estimate ({f1_point:.4f}) by more than 0.02"
        )

    def test_multi_run_bootstrap_mean_near_point_estimate(self) -> None:
        """Multi-run bootstrap mean F1 ≈ mean of per-run point estimates."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=3, n_tiles=10, detections_per_tile=2, seed=42,
        )

        # Per-run point estimates, then average
        run_f1s = []
        for _rn, gdf_det in run_gdfs:
            _p, _r, f1 = calculate_f1_internal(
                gdf_det, gdf_ref, gdf_bounds, buffer_metres=20,
            )
            run_f1s.append(f1)
        mean_f1_point = float(np.mean(run_f1s))

        # Multi-run bootstrap CI
        ci = bootstrap_multi_run_ci(
            run_gdfs, gdf_ref, gdf_bounds,
            n_iterations=500,
            random_seed=42,
        )

        assert abs(ci["f1"]["mean"] - mean_f1_point) < 0.02, (
            f"Multi-run bootstrap mean F1 ({ci['f1']['mean']:.4f}) deviates "
            f"from mean of per-run point estimates ({mean_f1_point:.4f}) "
            f"by more than 0.02"
        )

    def test_bootstrap_ci_contains_point_estimate(self) -> None:
        """The 95% bootstrap CI should contain the point estimate."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=1, n_tiles=10, detections_per_tile=2, seed=42,
        )
        _run_num, gdf_det = run_gdfs[0]

        _p, _r, f1_point = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=20,
        )

        ci = bootstrap_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=500,
            random_seed=42,
        )

        assert ci["f1"]["ci_lower"] <= f1_point <= ci["f1"]["ci_upper"], (
            f"Point estimate F1={f1_point:.4f} outside bootstrap CI "
            f"[{ci['f1']['ci_lower']:.4f}, {ci['f1']['ci_upper']:.4f}]"
        )


@pytest.mark.tier1
class TestPerTileMetrics:
    """Tests for compute_per_tile_tp_fp_fn() and aggregate_tile_metrics()."""

    def test_per_tile_sum_matches_global(self) -> None:
        """Sum of per-tile TP/FP/FN should match calculate_f1_internal().

        For synthetic data with well-separated tiles (100m apart, 20m buffer),
        per-tile and per-map matching produce identical results.
        """
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=1, n_tiles=10, detections_per_tile=2, seed=42,
        )
        _run_num, gdf_det = run_gdfs[0]

        # Per-tile metrics
        tile_metrics = compute_per_tile_tp_fp_fn(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=20,
        )
        tile_tp = tile_metrics['tp'].sum()
        tile_fp = tile_metrics['fp'].sum()
        tile_fn = tile_metrics['fn'].sum()

        # Compute metrics from tile sums
        precision_tile = tile_tp / (tile_tp + tile_fp) if (tile_tp + tile_fp) > 0 else 0
        recall_tile = tile_tp / (tile_tp + tile_fn) if (tile_tp + tile_fn) > 0 else 0
        if (precision_tile + recall_tile) > 0:
            f1_tile = 2 * precision_tile * recall_tile / (precision_tile + recall_tile)
        else:
            f1_tile = 0

        # Global point estimate
        p_global, r_global, f1_global = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=20,
        )

        # Should match exactly for well-separated tiles
        assert f1_tile == pytest.approx(f1_global, abs=1e-6), (
            f"Per-tile F1={f1_tile:.6f} != global F1={f1_global:.6f}"
        )
        assert precision_tile == pytest.approx(p_global, abs=1e-6)
        assert recall_tile == pytest.approx(r_global, abs=1e-6)

    def test_aggregate_with_duplicate_tiles(self) -> None:
        """A tile sampled 3× should contribute 3× its TP/FP/FN."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=1, n_tiles=10, detections_per_tile=2, seed=42,
        )
        _run_num, gdf_det = run_gdfs[0]

        tile_metrics = compute_per_tile_tp_fp_fn(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=20,
        )

        tiles = gdf_bounds['tile_name'].unique()
        first_tile = tiles[0]
        first_row = tile_metrics[tile_metrics['tile_name'] == first_tile].iloc[0]

        # Sample the first tile 3 times
        sample = np.array([first_tile, first_tile, first_tile])
        p, r, f1 = aggregate_tile_metrics(tile_metrics, sample)

        # With all-same tiles, TP/FP/FN scale by 3 but ratios are unchanged
        expected_tp = int(first_row['tp']) * 3
        expected_fp = int(first_row['fp']) * 3
        expected_fn = int(first_row['fn']) * 3

        if (expected_tp + expected_fp) > 0:
            expected_p = expected_tp / (expected_tp + expected_fp)
        else:
            expected_p = 0
        if (expected_tp + expected_fn) > 0:
            expected_r = expected_tp / (expected_tp + expected_fn)
        else:
            expected_r = 0

        assert p == pytest.approx(expected_p, abs=1e-10)
        assert r == pytest.approx(expected_r, abs=1e-10)

    def test_aggregate_all_tiles_matches_point_estimate(self) -> None:
        """Aggregating all tiles (no duplicates) should match point estimate."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=1, n_tiles=10, detections_per_tile=2, seed=42,
        )
        _run_num, gdf_det = run_gdfs[0]

        tile_metrics = compute_per_tile_tp_fp_fn(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=20,
        )
        tiles = gdf_bounds['tile_name'].unique()

        p_agg, r_agg, f1_agg = aggregate_tile_metrics(tile_metrics, tiles)
        p_pt, r_pt, f1_pt = calculate_f1_internal(
            gdf_det, gdf_ref, gdf_bounds, buffer_metres=20,
        )

        assert f1_agg == pytest.approx(f1_pt, abs=1e-6)
        assert p_agg == pytest.approx(p_pt, abs=1e-6)
        assert r_agg == pytest.approx(r_pt, abs=1e-6)


@pytest.mark.tier1
class TestEffectSizePValuesArePermutation:
    """bootstrap_effect_size_ci's p-values come from the permutation test (D42)."""

    def test_identical_conditions_give_p_one(self) -> None:
        """Identical detection sets: p = 1 on every metric, never a floor."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=1, n_tiles=10, detections_per_tile=2, seed=42,
        )
        _n, gdf_det = run_gdfs[0]
        res = bootstrap_effect_size_ci(
            gdf_det, gdf_bounds, gdf_det, gdf_bounds, gdf_ref,
            n_iterations=200, random_seed=42, return_p_values=True,
        )
        for key in ("f1_difference", "precision_difference", "recall_difference"):
            assert res[key]["p_value"] == 1.0
            assert "permutation" in res[key]["p_method"]
        assert res["permutation"]["n_discordant_tiles"] == 0

    def test_p_equals_the_kernel_on_sorted_tile_arrays(self) -> None:
        """The p-value is the kernel's, on tiles in sorted order."""
        from scripts.lib_advanced_metrics import _tile_count_arrays
        from scripts.lib_permutation import paired_permutation_test

        runs_a, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=1, n_tiles=10, detections_per_tile=2, seed=1,
        )
        runs_b, _ref, _bounds = _make_synthetic_runs(
            n_runs=1, n_tiles=10, detections_per_tile=2, seed=2,
        )
        det_a, det_b = runs_a[0][1], runs_b[0][1]
        res = bootstrap_effect_size_ci(
            det_a, gdf_bounds, det_b, gdf_bounds, gdf_ref,
            n_iterations=100, random_seed=42, return_p_values=True,
        )
        tiles = sorted(gdf_bounds["tile_name"].unique())
        want = paired_permutation_test(
            _tile_count_arrays(compute_per_tile_tp_fp_fn(det_a, gdf_ref, gdf_bounds), tiles),
            _tile_count_arrays(compute_per_tile_tp_fp_fn(det_b, gdf_ref, gdf_bounds), tiles),
        )
        assert res["f1_difference"]["p_value"] == want["metrics"]["f1"]["p_value"]
        assert res["recall_difference"]["p_value"] == want["metrics"]["recall"]["p_value"]

    def test_no_p_value_unless_asked(self) -> None:
        """Without return_p_values the result carries CIs only."""
        run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
            n_runs=1, n_tiles=6, detections_per_tile=2, seed=3,
        )
        _n, gdf_det = run_gdfs[0]
        res = bootstrap_effect_size_ci(
            gdf_det, gdf_bounds, gdf_det, gdf_bounds, gdf_ref,
            n_iterations=50, random_seed=42,
        )
        assert "p_value" not in res["f1_difference"]
        assert "permutation" not in res
