"""
Pytest wrapper for preflight checks.

Tier 1 tests that run essential preflight validations as part of the test suite.
These tests catch configuration issues before expensive API runs.

Usage:
    pytest tests/test_preflight.py -v
    pytest tests/test_preflight.py -m tier1  # Run only tier1 tests
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from preflight_check import (
    check_api_key,
    check_directory_exists,
    check_file_exists,
)


# =============================================================================
# CORE INFRASTRUCTURE TESTS
# =============================================================================


@pytest.mark.tier1
@pytest.mark.compliance
class TestCoreInfrastructure:
    """Tests for core infrastructure required by all phases."""

    def test_tiles_directory_exists(self) -> None:
        """Verify the tiles directory exists."""
        tiles_dir = PROJECT_ROOT / "inputs" / "tiles"
        passed, msg = check_directory_exists(tiles_dir, "Tiles directory")
        assert passed, msg

    def test_ground_truth_exists(self) -> None:
        """Verify ground truth reference file exists."""
        gt_path = PROJECT_ROOT / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
        passed, msg = check_file_exists(gt_path, "Ground truth")
        assert passed, msg

    def test_calibration_bounds_exists(self) -> None:
        """Verify calibration region bounds file exists."""
        bounds_path = PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "calibration_bounds.geojson"
        passed, msg = check_file_exists(bounds_path, "Calibration bounds")
        assert passed, msg

    def test_validation_bounds_exists(self) -> None:
        """Verify validation region bounds file exists."""
        bounds_path = PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "validation_bounds.geojson"
        passed, msg = check_file_exists(bounds_path, "Validation bounds")
        assert passed, msg


@pytest.mark.tier1
@pytest.mark.compliance
class TestManifests:
    """Tests for tile manifest files."""

    def test_calibration_manifest_exists(self) -> None:
        """Verify calibration manifest file exists."""
        manifest_path = PROJECT_ROOT / "inputs" / "tiles" / "calibration_manifest.json"
        passed, msg = check_file_exists(manifest_path, "Calibration manifest")
        assert passed, msg

    def test_validation_manifest_exists(self) -> None:
        """Verify validation manifest file exists."""
        manifest_path = PROJECT_ROOT / "inputs" / "tiles" / "validation_manifest.json"

        # Check for legacy naming
        legacy_path = PROJECT_ROOT / "inputs" / "tiles" / "holdout_manifest.json"
        if not manifest_path.exists() and legacy_path.exists():
            pytest.skip(
                "validation_manifest.json not found, but holdout_manifest.json exists. "
                "Consider renaming to match calibration/validation nomenclature."
            )

        passed, msg = check_file_exists(manifest_path, "Validation manifest")
        assert passed, msg


@pytest.mark.tier1
@pytest.mark.compliance
class TestExampleLibrary:
    """Tests for example library images."""

    def test_baseline_examples_exist(self) -> None:
        """Verify baseline example library images exist.

        Baseline examples (required for all experiments):
        - example_01-04.png: Canon+ examples
        - example_15-17.png: Null examples
        """
        examples_dir = PROJECT_ROOT / "inputs" / "examples" / "neutral-naming"

        baseline_examples = [
            "example_01.png",  # Canon+ (burial mound)
            "example_02.png",  # Canon+ (settlement mound)
            "example_03.png",  # Canon+ (triangulation on mound)
            "example_04.png",  # Canon+ (benchmark on mound)
            "example_15.png",  # Null (empty tile 1)
            "example_16.png",  # Null (empty tile 2)
            "example_17.png",  # Null (empty tile 3)
        ]

        missing = []
        for filename in baseline_examples:
            path = examples_dir / filename
            if not path.exists():
                missing.append(filename)

        assert not missing, (
            f"Missing baseline examples: {', '.join(missing)}\n"
            f"Expected in: {examples_dir}"
        )


# =============================================================================
# CONFIG VALIDATION TESTS
# =============================================================================


@pytest.mark.tier1
@pytest.mark.compliance
class TestConfigValidation:
    """Tests for prompt configuration file validation.

    Note: Detect configs (detect_*.json) have model/instruction_file fields.
    Library configs (library_*.json) only define example composition.
    """

    @pytest.fixture
    def configs_dir(self) -> Path:
        """Return the configs directory path."""
        return PROJECT_ROOT / "prompts" / "configs"

    def test_detect_image_only_config_syntax(self, configs_dir: Path) -> None:
        """Verify detect_image-only.json parses as valid JSON."""
        import json
        config_path = configs_dir / "detect_image-only.json"
        assert config_path.exists(), f"Config not found: {config_path}"

        with open(config_path) as f:
            config = json.load(f)

        # Check required fields for detect configs
        assert "version" in config, "Missing required field: version"
        assert "model" in config, "Missing required field: model"
        assert "instruction_file" in config, "Missing required field: instruction_file"

    def test_detect_brief_text_image_config_syntax(self, configs_dir: Path) -> None:
        """Verify detect_brief-text-image.json parses as valid JSON."""
        import json
        config_path = configs_dir / "detect_brief-text-image.json"
        assert config_path.exists(), f"Config not found: {config_path}"

        with open(config_path) as f:
            config = json.load(f)

        # Check required fields for detect configs
        assert "version" in config, "Missing required field: version"
        assert "model" in config, "Missing required field: model"

    def test_library_canonical_config_syntax(self, configs_dir: Path) -> None:
        """Verify library_canonical.json parses and has correct structure.

        Library configs define example composition, not detection parameters.
        """
        import json
        config_path = configs_dir / "library_canonical.json"
        assert config_path.exists(), f"Config not found: {config_path}"

        with open(config_path) as f:
            config = json.load(f)

        # Check required fields for library configs
        assert "version" in config, "Missing required field: version"
        assert "composition" in config, "Missing required field: composition"
        assert "examples" in config, "Missing required field: examples"


# =============================================================================
# SMOKE TESTS (OPTIONAL - DEPEND ON ENVIRONMENT)
# =============================================================================


@pytest.mark.tier2
class TestAPIConfiguration:
    """Tests for API configuration (tier2 - may require environment setup)."""

    def test_api_key_configured(self) -> None:
        """Verify Google API key is configured.

        This test may be skipped in CI environments where API keys
        are not available. It's primarily useful for local pre-run checks.
        """
        passed, msg = check_api_key()
        if not passed:
            pytest.skip(f"API key not configured (expected in development): {msg}")
        assert passed, msg
