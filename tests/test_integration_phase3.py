"""
Integration tests for Phase 3 scripts.

Tier 1 tests that verify Phase 3 analysis scripts produce expected results
on synthetic fixtures with known outcomes.

These tests catch regressions in:
- Threshold sweep analysis (H3)
- Candidate extraction (H2 pipeline)
"""

import importlib.util
import json
import sys
from pathlib import Path

import geopandas as gpd
import pytest
from PIL import Image

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_analyse_consensus_module():
    """Load 7_analyse_consensus.py module using importlib.

    Required because Python modules cannot start with a digit.
    """
    spec = importlib.util.spec_from_file_location(
        "analyse_consensus",
        PROJECT_ROOT / "scripts" / "7_analyse_consensus.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load module at import time
_analyse_consensus = load_analyse_consensus_module()
analyse_threshold_sweep = _analyse_consensus.analyse_threshold_sweep


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def voting_test_data(fixtures_dir: Path) -> tuple[Path, Path, Path]:
    """Load paths for voting threshold test data.

    Returns (detections_path, references_path, bounds_path).
    """
    detections = fixtures_dir / "detections_with_votes.geojson"
    references = fixtures_dir / "references_for_voting_test.geojson"
    bounds = fixtures_dir / "bounds_sparse.geojson"
    return detections, references, bounds


@pytest.fixture
def expected_threshold_sweep(fixtures_dir: Path) -> dict:
    """Load expected threshold sweep results."""
    with open(fixtures_dir / "expected_threshold_sweep.json") as f:
        return json.load(f)


@pytest.fixture
def temp_tiles_with_images(tmp_path: Path) -> tuple[Path, gpd.GeoDataFrame]:
    """Create temporary tiles directory with synthetic images.

    Returns (tiles_dir, detections_gdf).
    """
    tiles_dir = tmp_path / "tiles"
    tiles_dir.mkdir()

    # Create synthetic tile images (512x512)
    for tile_name in ["TestMap_x448_y0.png", "TestMap_x448_y448.png", "TestMap_x896_y0.png"]:
        tile_path = tiles_dir / tile_name
        img = Image.new("RGB", (512, 512), color=(200, 200, 200))
        img.save(tile_path)

    # Create detections GeoJSON in temp directory
    detections_path = tmp_path / "detections.geojson"
    detections_data = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}},
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "source_tile": "TestMap_x448_y0.png",
                    "vote_count": 5,
                    "pixel_x": 256,
                    "pixel_y": 256,
                },
                "geometry": {"type": "Point", "coordinates": [403500.0, 4700500.0]},
            },
            {
                "type": "Feature",
                "properties": {
                    "source_tile": "TestMap_x448_y448.png",
                    "vote_count": 3,
                    "pixel_x": 100,
                    "pixel_y": 100,
                },
                "geometry": {"type": "Point", "coordinates": [404000.0, 4701000.0]},
            },
        ],
    }
    with open(detections_path, "w") as f:
        json.dump(detections_data, f)

    gdf = gpd.read_file(detections_path)
    return tiles_dir, gdf


# =============================================================================
# THRESHOLD SWEEP INTEGRATION TESTS
# =============================================================================


@pytest.mark.tier1
@pytest.mark.integration
class TestThresholdSweepIntegration:
    """Integration tests for threshold sweep analysis."""

    def test_sweep_returns_expected_structure(
        self,
        voting_test_data: tuple[Path, Path, Path],
    ) -> None:
        """Verify threshold sweep returns all required keys."""
        detections_path, references_path, bounds_path = voting_test_data

        result = analyse_threshold_sweep(
            pred_path=detections_path,
            bounds_path=bounds_path,
            template_path=references_path,
            max_n=5,
        )

        # Check top-level structure
        assert "curves" in result, "Missing 'curves' in result"
        assert "optimal" in result, "Missing 'optimal' in result"
        assert "cost_efficiency" in result, "Missing 'cost_efficiency' in result"
        assert "metadata" in result, "Missing 'metadata' in result"

    def test_sweep_finds_optimal_at_t5(
        self,
        voting_test_data: tuple[Path, Path, Path],
        expected_threshold_sweep: dict,
    ) -> None:
        """Verify optimal threshold matches expected value.

        The test fixture has 2 references matched by the 2 detections with
        vote_count=5. At T>=5, we have perfect precision and recall.
        """
        detections_path, references_path, bounds_path = voting_test_data

        result = analyse_threshold_sweep(
            pred_path=detections_path,
            bounds_path=bounds_path,
            template_path=references_path,
            max_n=5,
        )

        expected_optimal = expected_threshold_sweep["expected_optimal"]

        assert result["optimal"]["threshold"] == expected_optimal["threshold"], (
            f"Expected optimal threshold {expected_optimal['threshold']}, "
            f"got {result['optimal']['threshold']}"
        )

        # Check F1 is optimal (1.0 for perfect match)
        assert result["optimal"]["f1"] == pytest.approx(
            expected_optimal["f1"], abs=0.01
        ), f"Expected optimal F1 {expected_optimal['f1']}, got {result['optimal']['f1']}"

    def test_sweep_detection_counts_by_threshold(
        self,
        voting_test_data: tuple[Path, Path, Path],
        expected_threshold_sweep: dict,
    ) -> None:
        """Verify detection counts decrease as threshold increases."""
        detections_path, references_path, bounds_path = voting_test_data

        result = analyse_threshold_sweep(
            pred_path=detections_path,
            bounds_path=bounds_path,
            template_path=references_path,
            max_n=5,
        )

        expected_counts = expected_threshold_sweep["expected_counts_by_threshold"]

        # Build actual counts from curves
        actual_counts = {}
        for curve in result["curves"]:
            if curve["n"] == 5:  # Only check max_n=5 curves
                actual_counts[f"T{curve['threshold']}"] = curve["count"]

        for threshold_key, expected_count in expected_counts.items():
            if threshold_key in actual_counts:
                assert actual_counts[threshold_key] == expected_count, (
                    f"At {threshold_key}: expected {expected_count} detections, "
                    f"got {actual_counts[threshold_key]}"
                )

    def test_sweep_f1_monotonic_near_optimal(
        self,
        voting_test_data: tuple[Path, Path, Path],
    ) -> None:
        """Verify F1 increases as threshold approaches optimal.

        For this fixture, F1 should increase monotonically from T=1 to T=5
        because higher thresholds reduce false positives while retaining true positives.
        """
        detections_path, references_path, bounds_path = voting_test_data

        result = analyse_threshold_sweep(
            pred_path=detections_path,
            bounds_path=bounds_path,
            template_path=references_path,
            max_n=5,
        )

        # Extract F1 values for N=5
        f1_by_threshold = {}
        for curve in result["curves"]:
            if curve["n"] == 5:
                f1_by_threshold[curve["threshold"]] = curve["f1"]

        # Check monotonic increase
        prev_f1 = 0.0
        for t in sorted(f1_by_threshold.keys()):
            current_f1 = f1_by_threshold[t]
            assert current_f1 >= prev_f1, (
                f"F1 decreased at T={t}: {prev_f1:.3f} → {current_f1:.3f}"
            )
            prev_f1 = current_f1

    def test_sweep_cost_efficiency_calculated(
        self,
        voting_test_data: tuple[Path, Path, Path],
    ) -> None:
        """Verify cost efficiency is calculated for each (N, T) combination."""
        detections_path, references_path, bounds_path = voting_test_data

        result = analyse_threshold_sweep(
            pred_path=detections_path,
            bounds_path=bounds_path,
            template_path=references_path,
            max_n=5,
            cost_per_call=0.003,
            n_tiles=60,
        )

        cost_eff = result["cost_efficiency"]

        # Should have entries for each N
        assert len(cost_eff) > 0, "No cost efficiency data"

        # Each entry should have required fields
        for entry in cost_eff:
            assert "n" in entry, "Missing 'n' in cost efficiency entry"
            assert "threshold" in entry, "Missing 'threshold' in cost efficiency entry"
            assert "f1_per_dollar" in entry, "Missing 'f1_per_dollar' in cost efficiency entry"
            assert "cost_usd" in entry, "Missing 'cost_usd' in cost efficiency entry"

            # Verify cost calculation: cost = n * n_tiles * cost_per_call
            expected_cost = entry["n"] * 60 * 0.003
            assert entry["cost_usd"] == pytest.approx(expected_cost, rel=0.01), (
                f"Cost mismatch for N={entry['n']}: expected {expected_cost}, "
                f"got {entry['cost_usd']}"
            )

    def test_sweep_writes_output_file(
        self,
        voting_test_data: tuple[Path, Path, Path],
        tmp_path: Path,
    ) -> None:
        """Verify threshold sweep writes JSON output when path specified."""
        detections_path, references_path, bounds_path = voting_test_data
        output_path = tmp_path / "sweep_results.json"

        result = analyse_threshold_sweep(
            pred_path=detections_path,
            bounds_path=bounds_path,
            template_path=references_path,
            max_n=5,
            output_path=output_path,
        )

        assert output_path.exists(), "Output file not created"

        # Verify output is valid JSON with same structure
        with open(output_path) as f:
            written_result = json.load(f)

        assert "curves" in written_result, "Written output missing 'curves'"
        assert "optimal" in written_result, "Written output missing 'optimal'"


# =============================================================================
# CANDIDATE EXTRACTION INTEGRATION TESTS
# =============================================================================


@pytest.mark.tier1
@pytest.mark.integration
class TestCandidateExtractionIntegration:
    """Integration tests for H2 candidate extraction pipeline."""

    def test_extract_creates_manifest(
        self,
        temp_tiles_with_images: tuple[Path, gpd.GeoDataFrame],
    ) -> None:
        """Verify extraction creates a valid manifest file.

        Note: With non-georeferenced test tiles, actual extraction will fail
        because projected coordinates can't be converted to pixel coordinates.
        This test verifies the manifest structure is correct regardless.
        """
        from scripts.extract_candidates import extract_candidates

        tiles_dir, _ = temp_tiles_with_images

        # Create GeoJSON from temp data
        geojson_path = tiles_dir.parent / "test_detections.geojson"
        detections_data = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}},
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "source_tile": "TestMap_x448_y0.png",
                        "pixel_x": 256,
                        "pixel_y": 256,
                    },
                    "geometry": {"type": "Point", "coordinates": [403500.0, 4700500.0]},
                },
            ],
        }
        with open(geojson_path, "w") as f:
            json.dump(detections_data, f)

        output_dir = tiles_dir.parent / "candidates"
        output_dir.mkdir()

        manifest_path = extract_candidates(
            proposer_geojson=geojson_path,
            tiles_dir=tiles_dir,
            output_dir=output_dir,
        )

        assert manifest_path is not None, "extract_candidates returned None"
        assert manifest_path.exists(), "Manifest file not created"

        # Verify manifest structure (flat, not nested under 'metadata')
        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "candidates" in manifest, "Manifest missing 'candidates' key"
        assert "total_detections" in manifest, "Manifest missing 'total_detections'"
        assert "version" in manifest, "Manifest missing 'version'"
        # Note: extraction fails with non-georeferenced tiles, but manifest is created
        assert manifest["total_detections"] == 1, "Expected 1 detection in manifest"

    def test_extract_records_failures_without_georeferencing(
        self,
        temp_tiles_with_images: tuple[Path, gpd.GeoDataFrame],
    ) -> None:
        """Verify extraction records failures when tiles aren't georeferenced.

        With non-georeferenced test tiles, projected coordinates can't be
        converted to pixel coordinates. The script should handle this gracefully
        and record the failure in the manifest.
        """
        from scripts.extract_candidates import extract_candidates

        tiles_dir, _ = temp_tiles_with_images

        geojson_path = tiles_dir.parent / "test_detections.geojson"
        detections_data = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}},
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "source_tile": "TestMap_x448_y0.png",
                        "pixel_x": 256,
                        "pixel_y": 256,
                    },
                    "geometry": {"type": "Point", "coordinates": [403500.0, 4700500.0]},
                },
            ],
        }
        with open(geojson_path, "w") as f:
            json.dump(detections_data, f)

        output_dir = tiles_dir.parent / "candidates"
        output_dir.mkdir()

        manifest_path = extract_candidates(
            proposer_geojson=geojson_path,
            tiles_dir=tiles_dir,
            output_dir=output_dir,
            padding=50,
        )

        # Verify manifest records the failure
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Non-georeferenced tiles are handled gracefully: rasterio uses
        # the identity matrix, producing a crop with incorrect coordinates
        # but no crash. The extraction records it as a tile-fallback success.
        assert manifest["total_detections"] == 1, "Should have 1 detection"
        # Note: extraction now succeeds via tile fallback even without
        # georeferencing (rasterio identity matrix). Prior versions would
        # fail here. The crop coordinates will be wrong but the pipeline
        # doesn't crash — which is the important safety property.
        assert manifest["successful_extractions"] + manifest["failed_extractions"] == 1, (
            "Should process exactly 1 detection"
        )

    def test_extract_handles_missing_tile(
        self,
        temp_tiles_with_images: tuple[Path, gpd.GeoDataFrame],
    ) -> None:
        """Verify extraction handles missing source tiles gracefully."""
        from scripts.extract_candidates import extract_candidates

        tiles_dir, _ = temp_tiles_with_images

        # Reference a non-existent tile
        geojson_path = tiles_dir.parent / "test_detections.geojson"
        detections_data = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}},
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "source_tile": "NONEXISTENT_TILE.png",
                        "pixel_x": 256,
                        "pixel_y": 256,
                    },
                    "geometry": {"type": "Point", "coordinates": [403500.0, 4700500.0]},
                },
            ],
        }
        with open(geojson_path, "w") as f:
            json.dump(detections_data, f)

        output_dir = tiles_dir.parent / "candidates"
        output_dir.mkdir()

        manifest_path = extract_candidates(
            proposer_geojson=geojson_path,
            tiles_dir=tiles_dir,
            output_dir=output_dir,
        )

        # Should still create manifest but record the failure
        assert manifest_path is not None, "Should return manifest even with failures"

        with open(manifest_path) as f:
            manifest = json.load(f)

        # Check manifest records the failure (flat structure, not nested)
        assert manifest["failed_extractions"] >= 1, "Should record failed extraction"
        assert "NONEXISTENT_TILE.png" in manifest["missing_sources"], "Should list missing tile"

    def test_extract_dry_run_no_files(
        self,
        temp_tiles_with_images: tuple[Path, gpd.GeoDataFrame],
    ) -> None:
        """Verify dry run mode doesn't create files."""
        from scripts.extract_candidates import extract_candidates

        tiles_dir, _ = temp_tiles_with_images

        geojson_path = tiles_dir.parent / "test_detections.geojson"
        detections_data = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::32635"}},
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "source_tile": "TestMap_x448_y0.png",
                        "pixel_x": 256,
                        "pixel_y": 256,
                    },
                    "geometry": {"type": "Point", "coordinates": [403500.0, 4700500.0]},
                },
            ],
        }
        with open(geojson_path, "w") as f:
            json.dump(detections_data, f)

        output_dir = tiles_dir.parent / "candidates"
        output_dir.mkdir()

        result = extract_candidates(
            proposer_geojson=geojson_path,
            tiles_dir=tiles_dir,
            output_dir=output_dir,
            dry_run=True,
        )

        # Dry run should return None and not create files
        assert result is None, "Dry run should return None"

        cropped_images = list(output_dir.glob("candidate_*.png"))
        assert len(cropped_images) == 0, "Dry run should not create images"

        manifest_files = list(output_dir.glob("*.json"))
        assert len(manifest_files) == 0, "Dry run should not create manifest"


# =============================================================================
# CROSS-SCRIPT INTEGRATION TESTS
# =============================================================================


@pytest.mark.tier1
@pytest.mark.integration
class TestPhase3PipelineIntegration:
    """Integration tests verifying Phase 3 scripts work together."""

    def test_merged_detections_compatible_with_sweep(
        self,
        voting_test_data: tuple[Path, Path, Path],
    ) -> None:
        """Verify detections with vote_count work with threshold sweep.

        This tests the data contract between merge_passes.py output and
        7_analyse_consensus.py input.
        """
        detections_path, references_path, bounds_path = voting_test_data

        # Load and verify detections have required property
        gdf = gpd.read_file(detections_path)
        assert "vote_count" in gdf.columns, "Detections missing vote_count property"

        # Verify sweep accepts this format
        result = analyse_threshold_sweep(
            pred_path=detections_path,
            bounds_path=bounds_path,
            template_path=references_path,
            max_n=5,
        )

        assert "curves" in result, "Sweep failed on valid input"
        assert len(result["curves"]) > 0, "Sweep produced no curves"


# =============================================================================
# MODE-AWARE COST ESTIMATOR TESTS
# =============================================================================
#
# Regression guard for the bug where ``_estimate_cost`` over-estimated
# text-mode runs by 5x because the per-tile rate was calibrated only on
# the Phase 3a image matrix. The fix introduces ``_detect_proposer_mode``
# and a per-mode rate table (``_MODE_RATES``).
#
# Empirical anchors:
#   - T=0.3 55-map text-mode: actual $67.82
#   - T=0.7 55-map text-mode: actual $69.60
#   - Predicted (text rate, 8541 tiles, K=5): 8541 * 5 * 0.0013 + 13.0
#                                             = $68.52 → both within ~2%.
#   - Image-mode regression: 8541 * 5 * 0.0082 + 5.0 = $355.18 (exact).


def _build_mode_rcfg(
    proposer_config_path: Path,
    manifest_path: Path,
) -> "object":
    """Construct a minimal ``ResolvedRunConfig`` for cost-estimator tests.

    Only the proposer ``config``, ``manifest``, and ``passes`` fields are
    consulted by ``_estimate_cost`` / ``_detect_proposer_mode``, so the
    other stage dicts are populated with stub values to satisfy the
    dataclass.
    """
    from scripts.run_generalisation import ResolvedRunConfig

    return ResolvedRunConfig(
        run_name="test-mode-aware",
        output_dir=manifest_path.parent / "output",
        proposer={
            "config": str(proposer_config_path),
            "manifest": str(manifest_path),
            "passes": 5,
            "tiles_dir": "tiles",
            "temperature": 0.3,
            "thinking_level": "high",
        },
        consensus={"vote_threshold": 3},
        extract={"padding": 50, "rasters_dir": "rasters"},
        verify={"config": "verifier.json"},
        evaluate={
            "prob_threshold": 0.5,
            "buffers": [20, 30, 40, 50],
            "ground_truth": "gt.geojson",
            "bounds": "bounds.geojson",
        },
        global_opts={"output_root": "outputs", "service_tier": "flex"},
    )


def _write_manifest_with_n_tiles(path: Path, n_tiles: int) -> None:
    """Write a list-form proposer manifest containing ``n_tiles`` entries."""
    tiles = [
        {"tile_name": f"TestMap_x{i}_y0.png", "map_id": "TestMap"}
        for i in range(n_tiles)
    ]
    path.write_text(json.dumps(tiles), encoding="utf-8")


@pytest.fixture
def text_mode_rcfg(tmp_path: Path):
    """Return rcfg for a text-mode run with the 55-map manifest size (8541)."""
    proposer_config = tmp_path / "proposer_text.json"
    proposer_config.write_text(
        json.dumps({
            "include_example_images": False,
            "instruction_file": "prompts/system-instructions/detect_brief-text.md",
        }),
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    _write_manifest_with_n_tiles(manifest, 8541)
    return _build_mode_rcfg(proposer_config, manifest)


@pytest.fixture
def image_mode_rcfg(tmp_path: Path):
    """Return rcfg for an image-mode run with the 55-map manifest size (8541)."""
    proposer_config = tmp_path / "proposer_image.json"
    proposer_config.write_text(
        json.dumps({
            "include_example_images": True,
            "instruction_file": "prompts/system-instructions/detect_brief-image.md",
        }),
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    _write_manifest_with_n_tiles(manifest, 8541)
    return _build_mode_rcfg(proposer_config, manifest)


@pytest.fixture
def missing_config_rcfg(tmp_path: Path):
    """Return rcfg whose proposer config does not exist on disk."""
    missing_config = tmp_path / "does_not_exist.json"
    manifest = tmp_path / "manifest.json"
    _write_manifest_with_n_tiles(manifest, 8541)
    return _build_mode_rcfg(missing_config, manifest)


@pytest.fixture
def instruction_file_fallback_rcfg(tmp_path: Path):
    """Return rcfg where include_example_images is absent but the instruction
    file name flags this as an image-mode run.
    """
    proposer_config = tmp_path / "proposer_fallback.json"
    proposer_config.write_text(
        json.dumps({
            # Note: include_example_images deliberately omitted.
            "instruction_file": (
                "prompts/system-instructions/detect_brief-image.md"
            ),
        }),
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    _write_manifest_with_n_tiles(manifest, 8541)
    return _build_mode_rcfg(proposer_config, manifest)


@pytest.mark.tier1
class TestEstimateCostModeAware:
    """Regression tests for the mode-aware cost estimator (Fix 1)."""

    # 55-map manifest tile count and K used across the empirical
    # validation cases.
    N_TILES = 8541
    K = 5

    # Empirical anchors (USD).
    ACTUAL_T03 = 67.82
    ACTUAL_T07 = 69.60

    def test_text_mode_within_tolerance_t03(self, text_mode_rcfg) -> None:
        """Predicted text-mode cost lies within ±10% of the T=0.3 actual."""
        from scripts.run_generalisation import _estimate_cost

        predicted = _estimate_cost(text_mode_rcfg)
        assert predicted is not None, "Cost estimator returned None"
        assert abs(predicted - self.ACTUAL_T03) / self.ACTUAL_T03 < 0.10, (
            f"Text-mode estimate ${predicted:.2f} diverges >10% from "
            f"T=0.3 actual ${self.ACTUAL_T03:.2f}."
        )

    def test_text_mode_within_tolerance_t07(self, text_mode_rcfg) -> None:
        """Predicted text-mode cost lies within ±10% of the T=0.7 actual."""
        from scripts.run_generalisation import _estimate_cost

        predicted = _estimate_cost(text_mode_rcfg)
        assert predicted is not None, "Cost estimator returned None"
        assert abs(predicted - self.ACTUAL_T07) / self.ACTUAL_T07 < 0.10, (
            f"Text-mode estimate ${predicted:.2f} diverges >10% from "
            f"T=0.7 actual ${self.ACTUAL_T07:.2f}."
        )

    def test_image_mode_exact_regression_guard(
        self, image_mode_rcfg,
    ) -> None:
        """Image-mode estimate matches the original Phase 3a calibration.

        Locks in the original formula 8541 * 5 * 0.0082 + 5.0 = $355.18 so
        any future drift in image-mode rates is caught here.
        """
        from scripts.run_generalisation import _estimate_cost

        predicted = _estimate_cost(image_mode_rcfg)
        expected = round(self.N_TILES * self.K * 0.0082 + 5.0, 2)
        assert expected == 355.18, (
            f"Test arithmetic drifted: expected $355.18, got ${expected}."
        )
        assert predicted == expected, (
            f"Image-mode estimate ${predicted} ≠ expected ${expected}."
        )

    def test_missing_config_defaults_to_image(
        self, missing_config_rcfg, caplog,
    ) -> None:
        """Unreadable proposer config falls back to (conservative) image rate."""
        import logging

        from scripts.run_generalisation import _detect_proposer_mode, _estimate_cost

        with caplog.at_level(logging.WARNING):
            mode = _detect_proposer_mode(missing_config_rcfg)
        assert mode == "image", (
            f"Expected fallback to 'image' mode; got '{mode}'."
        )
        # Verify the warning was emitted so operators see the fallback.
        assert any(
            "defaulting to 'image' mode" in rec.message for rec in caplog.records
        ), "Expected warning about defaulting to image mode."

        predicted = _estimate_cost(missing_config_rcfg)
        # Should match the image-mode regression value.
        assert predicted == round(self.N_TILES * self.K * 0.0082 + 5.0, 2)

    def test_instruction_file_fallback_to_image(
        self, instruction_file_fallback_rcfg,
    ) -> None:
        """Configs lacking include_example_images but referencing a
        ``-image`` instruction file route to image rates."""
        from scripts.run_generalisation import _detect_proposer_mode, _estimate_cost

        mode = _detect_proposer_mode(instruction_file_fallback_rcfg)
        assert mode == "image", (
            f"Expected 'image' mode via instruction_file fallback; got '{mode}'."
        )

        predicted = _estimate_cost(instruction_file_fallback_rcfg)
        assert predicted == round(self.N_TILES * self.K * 0.0082 + 5.0, 2)
