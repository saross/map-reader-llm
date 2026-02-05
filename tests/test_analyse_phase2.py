"""
Tests for Phase 2 multi-condition analysis functionality.

Tier 1 unit tests for the analyse_phase2_results.py script, covering:
- Benjamini-Hochberg FDR correction for multiple pairwise comparisons
- Per-run file discovery (no .geojson extension, no pass subdirectories)
- Per-run loading returning list of (run, GeoDataFrame) tuples
- Multi-run bootstrap with synthetic data
- Integration test against existing image-only runs (if available)
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from analyse_phase2_results import apply_fdr_correction, load_condition_results
from lib_advanced_metrics import (
    bootstrap_multi_run_ci,
    bootstrap_multi_run_effect_size_ci,
)


@pytest.mark.tier1
class TestApplyFdrCorrection:
    """Tests for the Benjamini-Hochberg FDR correction function."""

    def test_empty_list_returns_empty(self) -> None:
        """Empty pairwise results should return empty list."""
        result = apply_fdr_correction([])
        assert result == []

    def test_single_significant_comparison(self) -> None:
        """Single significant comparison should remain significant after FDR."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {
                    "mean": 0.05,
                    "ci_lower": 0.02,  # CI excludes zero
                    "ci_upper": 0.08,
                },
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        assert len(result) == 1
        assert result[0]["initially_significant"] is True
        assert result[0]["fdr_significant"] is True

    def test_single_non_significant_comparison(self) -> None:
        """Single non-significant comparison should remain non-significant."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {
                    "mean": 0.01,
                    "ci_lower": -0.02,  # CI includes zero
                    "ci_upper": 0.04,
                },
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        assert len(result) == 1
        assert result[0]["initially_significant"] is False
        assert result[0]["fdr_significant"] is False

    def test_negative_significant_effect(self) -> None:
        """Negative significant effect (B better than A) should be detected."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {
                    "mean": -0.05,
                    "ci_lower": -0.08,  # CI entirely negative
                    "ci_upper": -0.02,
                },
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        assert result[0]["initially_significant"] is True
        assert result[0]["fdr_significant"] is True

    def test_multiple_all_significant_preserved(self) -> None:
        """Multiple significant comparisons should mostly be preserved with FDR."""
        # All comparisons are strongly significant (CI far from zero)
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.10, "ci_lower": 0.07, "ci_upper": 0.13},
            },
            {
                "condition_a": "A",
                "condition_b": "C",
                "f1_difference": {"mean": 0.08, "ci_lower": 0.05, "ci_upper": 0.11},
            },
            {
                "condition_a": "B",
                "condition_b": "C",
                "f1_difference": {"mean": 0.06, "ci_lower": 0.03, "ci_upper": 0.09},
            },
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # All should be initially significant
        assert all(r["initially_significant"] for r in result)

        # Most should survive FDR (at least the strongest ones)
        n_fdr_sig = sum(1 for r in result if r["fdr_significant"])
        assert n_fdr_sig >= 1, "At least one comparison should survive FDR"

    def test_multiple_none_significant(self) -> None:
        """Multiple non-significant comparisons should all remain non-significant."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.01, "ci_lower": -0.02, "ci_upper": 0.04},
            },
            {
                "condition_a": "A",
                "condition_b": "C",
                "f1_difference": {"mean": -0.01, "ci_lower": -0.04, "ci_upper": 0.02},
            },
            {
                "condition_a": "B",
                "condition_b": "C",
                "f1_difference": {"mean": 0.00, "ci_lower": -0.03, "ci_upper": 0.03},
            },
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # None should be significant
        assert not any(r["initially_significant"] for r in result)
        assert not any(r["fdr_significant"] for r in result)

    def test_fdr_reduces_false_positives(self) -> None:
        """FDR correction should reduce the number of significant results.

        When many comparisons are borderline significant, FDR should
        be more conservative than uncorrected significance.
        """
        # Create 10 comparisons, some borderline significant
        pairwise = []
        for i in range(10):
            # Alternate between barely significant and barely non-significant
            if i % 2 == 0:
                # Barely significant (CI just excludes zero)
                ci_lower = 0.001  # Just above zero
            else:
                # Barely non-significant
                ci_lower = -0.001

            pairwise.append({
                "condition_a": f"A{i}",
                "condition_b": f"B{i}",
                "f1_difference": {
                    "mean": 0.02,
                    "ci_lower": ci_lower,
                    "ci_upper": 0.04,
                },
            })

        result = apply_fdr_correction(pairwise, q=0.05)

        n_initially_sig = sum(1 for r in result if r["initially_significant"])
        n_fdr_sig = sum(1 for r in result if r["fdr_significant"])

        # FDR should be equal or more conservative
        assert n_fdr_sig <= n_initially_sig, \
            "FDR should not increase number of significant results"

    def test_q_value_affects_threshold(self) -> None:
        """Higher q-value should allow more comparisons to pass FDR."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.03, "ci_lower": 0.001, "ci_upper": 0.06},
            },
            {
                "condition_a": "A",
                "condition_b": "C",
                "f1_difference": {"mean": 0.02, "ci_lower": 0.001, "ci_upper": 0.04},
            },
        ]

        result_strict = apply_fdr_correction(pairwise.copy(), q=0.01)
        result_lenient = apply_fdr_correction(pairwise.copy(), q=0.10)

        n_strict = sum(1 for r in result_strict if r["fdr_significant"])
        n_lenient = sum(1 for r in result_lenient if r["fdr_significant"])

        # Lenient q should allow at least as many
        assert n_lenient >= n_strict

    def test_preserves_original_fields(self) -> None:
        """FDR correction should preserve all original fields in results."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.05, "ci_lower": 0.02, "ci_upper": 0.08},
                "precision_difference": {"mean": 0.03, "ci_lower": 0.01, "ci_upper": 0.05},
                "recall_difference": {"mean": 0.07, "ci_lower": 0.04, "ci_upper": 0.10},
                "n_tiles": 60,
                "n_iterations": 1000,
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # All original fields should be preserved
        assert result[0]["condition_a"] == "A"
        assert result[0]["condition_b"] == "B"
        assert result[0]["precision_difference"]["mean"] == 0.03
        assert result[0]["recall_difference"]["mean"] == 0.07
        assert result[0]["n_tiles"] == 60
        assert result[0]["n_iterations"] == 1000

    def test_adds_significance_fields(self) -> None:
        """FDR correction should add initially_significant and fdr_significant fields."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.05, "ci_lower": 0.02, "ci_upper": 0.08},
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        assert "initially_significant" in result[0]
        assert "fdr_significant" in result[0]
        assert isinstance(result[0]["initially_significant"], bool)
        assert isinstance(result[0]["fdr_significant"], bool)


@pytest.mark.tier1
class TestApplyFdrCorrectionEdgeCases:
    """Edge case tests for FDR correction."""

    def test_missing_f1_difference_key(self) -> None:
        """Should handle missing f1_difference gracefully."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                # Missing f1_difference
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # Should not crash, should be marked non-significant
        assert len(result) == 1
        assert result[0]["initially_significant"] is False
        assert result[0]["fdr_significant"] is False

    def test_missing_ci_bounds(self) -> None:
        """Should handle missing CI bounds gracefully."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {"mean": 0.05},  # Missing ci_lower/ci_upper
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # Should not crash
        assert len(result) == 1

    def test_ci_exactly_at_zero(self) -> None:
        """CI bound exactly at zero should not be significant."""
        pairwise = [
            {
                "condition_a": "A",
                "condition_b": "B",
                "f1_difference": {
                    "mean": 0.02,
                    "ci_lower": 0.0,  # Exactly at zero
                    "ci_upper": 0.04,
                },
            }
        ]
        result = apply_fdr_correction(pairwise, q=0.05)

        # CI touching zero should not be significant
        assert result[0]["initially_significant"] is False

    def test_very_large_number_of_comparisons(self) -> None:
        """Should handle large number of comparisons efficiently."""
        # 100 comparisons (e.g., 15 conditions = 105 pairwise)
        pairwise = []
        for i in range(100):
            # Half significant, half not
            if i < 50:
                ci_lower = 0.01 + i * 0.001  # Increasingly significant
            else:
                ci_lower = -0.01  # Not significant

            pairwise.append({
                "condition_a": f"A{i}",
                "condition_b": f"B{i}",
                "f1_difference": {
                    "mean": 0.03,
                    "ci_lower": ci_lower,
                    "ci_upper": 0.05,
                },
            })

        result = apply_fdr_correction(pairwise, q=0.05)

        assert len(result) == 100
        # FDR should be conservative - not more than initially significant
        n_initially_sig = sum(1 for r in result if r["initially_significant"])
        n_fdr_sig = sum(1 for r in result if r["fdr_significant"])
        assert n_fdr_sig <= n_initially_sig, "FDR should not increase significant count"
        # All results should have the significance fields
        assert all("initially_significant" in r for r in result)
        assert all("fdr_significant" in r for r in result)


# Import check
def test_import_apply_fdr_correction() -> None:
    """Verify that apply_fdr_correction can be imported."""
    from analyse_phase2_results import apply_fdr_correction as imported_fn
    assert callable(imported_fn)


# ============================================================================
# File Discovery and Per-Run Loading Tests
# ============================================================================

def _make_detection_geojson(features: list[dict]) -> dict:
    """Create a minimal GeoJSON FeatureCollection for testing."""
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
    """Create a minimal detection Feature for testing."""
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
        not (PROJECT_ROOT / "outputs" / "phase2a" / "image-only" / "run_1").exists(),
        reason="Existing Phase 2a image-only runs not available",
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

    Returns:
        (run_gdfs, gdf_ref, gdf_bounds) for use with bootstrap functions.
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
    for i, tname in enumerate(tile_names):
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
            for d in range(detections_per_tile):
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
            # CI lower should be <= mean <= CI upper
            assert result[metric]["ci_lower"] <= result[metric]["mean"]
            assert result[metric]["mean"] <= result[metric]["ci_upper"]

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
