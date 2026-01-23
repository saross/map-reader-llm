"""
Tests for Phase 2 and Phase 3 configuration validity.

Integration tests that verify study YAML files reference existing config
files and contain required fields. These tests prevent expensive API runs
from failing due to missing or misconfigured inputs.

Run before each phase to catch configuration errors early.
"""

import sys
from pathlib import Path

import pytest
import yaml

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

STUDIES_DIR = PROJECT_ROOT / "studies"
CONFIGS_DIR = PROJECT_ROOT / "prompts" / "configs"


def load_yaml(path: Path) -> dict:
    """Load YAML file and return contents."""
    with open(path) as f:
        return yaml.safe_load(f)


@pytest.mark.tier1
@pytest.mark.compliance
class TestPhase2YamlValidity:
    """Tests that Phase 2 YAML files are valid and reference existing configs."""

    @pytest.fixture
    def phase2_yamls(self) -> list[Path]:
        """Return list of Phase 2 study YAML files."""
        return sorted(STUDIES_DIR.glob("phase2*.yaml"))

    def test_phase2_yamls_exist(self, phase2_yamls: list[Path]) -> None:
        """Verify all 5 Phase 2 YAML files exist."""
        expected = [
            "phase2a-h1-modality.yaml",
            "phase2b-h7-temperature.yaml",
            "phase2c-h8-library.yaml",
            "phase2d-h5-negtext.yaml",
            "phase2e-h4-ordering.yaml",
        ]
        actual = [p.name for p in phase2_yamls]

        for name in expected:
            assert name in actual, f"Missing Phase 2 YAML: {name}"

    def test_phase2_yamls_parse_without_error(self, phase2_yamls: list[Path]) -> None:
        """Verify all Phase 2 YAML files parse without syntax errors."""
        for yaml_path in phase2_yamls:
            try:
                data = load_yaml(yaml_path)
                assert data is not None, f"{yaml_path.name} parsed as empty"
            except yaml.YAMLError as e:
                pytest.fail(f"YAML parse error in {yaml_path.name}: {e}")

    def test_phase2_yamls_have_required_sections(self, phase2_yamls: list[Path]) -> None:
        """Verify all Phase 2 YAML files have required top-level sections."""
        required_sections = ["study", "inputs", "execution"]

        for yaml_path in phase2_yamls:
            data = load_yaml(yaml_path)

            for section in required_sections:
                assert section in data, (
                    f"{yaml_path.name} missing required section: {section}"
                )

    def test_phase2_yamls_have_study_metadata(self, phase2_yamls: list[Path]) -> None:
        """Verify all Phase 2 YAML files have proper study metadata."""
        for yaml_path in phase2_yamls:
            data = load_yaml(yaml_path)
            study = data.get("study", {})

            assert "name" in study, f"{yaml_path.name} missing study.name"
            assert "phase" in study, f"{yaml_path.name} missing study.phase"
            assert "hypothesis" in study, f"{yaml_path.name} missing study.hypothesis"


@pytest.mark.tier1
@pytest.mark.compliance
class TestPhase2aConfigReferences:
    """Tests that Phase 2a references existing config files."""

    @pytest.fixture
    def phase2a_yaml(self) -> dict:
        """Load Phase 2a study definition."""
        return load_yaml(STUDIES_DIR / "phase2a-h1-modality.yaml")

    def test_phase2a_configs_exist(self, phase2a_yaml: dict) -> None:
        """Verify all config files referenced in Phase 2a exist."""
        factors = phase2a_yaml.get("factors", {})
        me_levels = factors.get("modality_elaboration", {}).get("levels", [])

        for level in me_levels:
            config_path = level.get("config")
            if config_path:
                full_path = PROJECT_ROOT / config_path
                assert full_path.exists(), (
                    f"Phase 2a references missing config: {config_path}\n"
                    f"  Level: {level.get('name')}"
                )


@pytest.mark.tier1
@pytest.mark.compliance
class TestPhase2cConfigReferences:
    """Tests that Phase 2c references existing library config files."""

    @pytest.fixture
    def phase2c_yaml(self) -> dict:
        """Load Phase 2c study definition."""
        return load_yaml(STUDIES_DIR / "phase2c-h8-library.yaml")

    def test_phase2c_library_configs_exist(self, phase2c_yaml: dict) -> None:
        """Verify all library config files referenced in Phase 2c exist."""
        factors = phase2c_yaml.get("factors", {})
        library_levels = factors.get("library_composition", {}).get("levels", [])

        for level in library_levels:
            config_path = level.get("config")
            if config_path:
                full_path = PROJECT_ROOT / config_path
                assert full_path.exists(), (
                    f"Phase 2c references missing library config: {config_path}\n"
                    f"  Level: {level.get('name')}"
                )


@pytest.mark.tier1
@pytest.mark.compliance
class TestPhase2dConfigReferences:
    """Tests that Phase 2d references existing H5 variant config files."""

    @pytest.fixture
    def phase2d_yaml(self) -> dict:
        """Load Phase 2d study definition."""
        return load_yaml(STUDIES_DIR / "phase2d-h5-negtext.yaml")

    def test_phase2d_h5_configs_exist(self, phase2d_yaml: dict) -> None:
        """Verify all H5 variant config files referenced in Phase 2d exist."""
        conditions = phase2d_yaml.get("conditions", [])

        for condition in conditions:
            config_path = condition.get("config")
            if config_path:
                full_path = PROJECT_ROOT / config_path
                assert full_path.exists(), (
                    f"Phase 2d references missing config: {config_path}\n"
                    f"  Condition: {condition.get('name')}"
                )


@pytest.mark.tier1
@pytest.mark.compliance
class TestInputFilesExist:
    """Tests that input files referenced in Phase 2 YAMLs exist."""

    def test_validation_manifest_exists(self) -> None:
        """Verify validation manifest file exists for Phase 2."""
        manifest_path = PROJECT_ROOT / "inputs" / "tiles" / "validation_manifest.json"

        # Check for legacy naming
        legacy_path = PROJECT_ROOT / "inputs" / "tiles" / "holdout_manifest.json"
        if not manifest_path.exists() and legacy_path.exists():
            pytest.skip(
                "validation_manifest.json not found, but holdout_manifest.json exists. "
                "Consider renaming to match calibration/validation nomenclature."
            )

        assert manifest_path.exists(), (
            f"Validation manifest not found: {manifest_path}\n"
            "Phase 2 requires validation tiles for evaluation."
        )

    def test_validation_bounds_exists(self) -> None:
        """Verify validation bounds file exists for Phase 2."""
        bounds_path = PROJECT_ROOT / "inputs" / "vectors" / "bounds" / "validation_bounds.geojson"
        assert bounds_path.exists(), (
            f"Validation bounds not found: {bounds_path}\n"
            "Phase 2 requires bounds for spatial scoping."
        )

    def test_ground_truth_exists(self) -> None:
        """Verify ground truth reference file exists."""
        ref_path = PROJECT_ROOT / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
        assert ref_path.exists(), (
            f"Ground truth not found: {ref_path}\n"
            "Phase 2 requires ground truth for accuracy evaluation."
        )


# =============================================================================
# PHASE 3 YAML VALIDITY TESTS
# =============================================================================


@pytest.mark.tier1
@pytest.mark.compliance
class TestPhase3YamlValidity:
    """Tests that Phase 3 YAML files are valid and have required structure."""

    @pytest.fixture
    def phase3_yamls(self) -> list[Path]:
        """Return list of Phase 3 study YAML files."""
        return sorted(STUDIES_DIR.glob("phase3*.yaml"))

    def test_phase3_yamls_exist(self, phase3_yamls: list[Path]) -> None:
        """Verify expected Phase 3 YAML files exist."""
        expected = [
            "phase3a-h3-voting.yaml",
            "phase3c-h9-diversity.yaml",
            "phase3d-h2-twostage.yaml",
        ]
        actual = [p.name for p in phase3_yamls]

        for name in expected:
            assert name in actual, f"Missing Phase 3 YAML: {name}"

    def test_phase3_yamls_parse_without_error(self, phase3_yamls: list[Path]) -> None:
        """Verify all Phase 3 YAML files parse without syntax errors."""
        for yaml_path in phase3_yamls:
            try:
                data = load_yaml(yaml_path)
                assert data is not None, f"{yaml_path.name} parsed as empty"
            except yaml.YAMLError as e:
                pytest.fail(f"YAML parse error in {yaml_path.name}: {e}")

    def test_phase3_yamls_have_required_sections(self, phase3_yamls: list[Path]) -> None:
        """Verify all Phase 3 YAML files have required top-level sections."""
        required_sections = ["study", "inputs", "execution", "analysis"]

        for yaml_path in phase3_yamls:
            data = load_yaml(yaml_path)

            for section in required_sections:
                assert section in data, (
                    f"{yaml_path.name} missing required section: {section}"
                )

    def test_phase3_yamls_have_study_metadata(self, phase3_yamls: list[Path]) -> None:
        """Verify all Phase 3 YAML files have proper study metadata."""
        for yaml_path in phase3_yamls:
            data = load_yaml(yaml_path)
            study = data.get("study", {})

            assert "name" in study, f"{yaml_path.name} missing study.name"
            assert "phase" in study, f"{yaml_path.name} missing study.phase"
            assert "hypothesis" in study, f"{yaml_path.name} missing study.hypothesis"

    def test_phase3_yamls_have_carried_forward(self, phase3_yamls: list[Path]) -> None:
        """Verify Phase 3 YAMLs have carried_forward section for Phase 2 dependencies."""
        for yaml_path in phase3_yamls:
            data = load_yaml(yaml_path)

            assert "carried_forward" in data, (
                f"{yaml_path.name} missing carried_forward section\n"
                "Phase 3 YAMLs must document Phase 2 dependencies."
            )

            carried = data.get("carried_forward", {})
            # All Phase 3 studies should at least reference optimal M/E config
            assert "optimal_me_config" in carried, (
                f"{yaml_path.name} missing carried_forward.optimal_me_config"
            )


@pytest.mark.tier1
@pytest.mark.compliance
class TestPhase3aStructure:
    """Tests for Phase 3a (H3 Voting) specific structure."""

    @pytest.fixture
    def phase3a_yaml(self) -> dict:
        """Load Phase 3a study definition."""
        return load_yaml(STUDIES_DIR / "phase3a-h3-voting.yaml")

    def test_phase3a_has_voting_factor(self, phase3a_yaml: dict) -> None:
        """Verify Phase 3a defines voting pool sizes as factor."""
        factors = phase3a_yaml.get("factors", {})
        assert "voting_pool_size" in factors, (
            "Phase 3a missing factors.voting_pool_size"
        )

        levels = factors["voting_pool_size"].get("levels", [])
        level_names = [lvl.get("name") for lvl in levels]

        # Should include at least N=5 and N=30
        assert any("5" in name for name in level_names), (
            "Phase 3a should include N=5 voting level"
        )
        assert any("30" in name for name in level_names), (
            "Phase 3a should include N=30 voting level"
        )

    def test_phase3a_analysis_is_threshold_sweep(self, phase3a_yaml: dict) -> None:
        """Verify Phase 3a uses threshold sweep analysis method."""
        analysis = phase3a_yaml.get("analysis", {})
        assert analysis.get("method") == "threshold_sweep", (
            "Phase 3a should use threshold_sweep analysis method"
        )


@pytest.mark.tier1
@pytest.mark.compliance
class TestPhase3dStructure:
    """Tests for Phase 3d (H2 Two-Stage) specific structure."""

    @pytest.fixture
    def phase3d_yaml(self) -> dict:
        """Load Phase 3d study definition."""
        return load_yaml(STUDIES_DIR / "phase3d-h2-twostage.yaml")

    def test_phase3d_has_architecture_factor(self, phase3d_yaml: dict) -> None:
        """Verify Phase 3d defines architecture as factor."""
        factors = phase3d_yaml.get("factors", {})
        assert "architecture" in factors, (
            "Phase 3d missing factors.architecture"
        )

        levels = factors["architecture"].get("levels", [])
        level_names = [lvl.get("name") for lvl in levels]

        assert "single_stage" in level_names, (
            "Phase 3d should include single_stage architecture"
        )
        assert "two_stage" in level_names, (
            "Phase 3d should include two_stage architecture"
        )
