"""
Integration tests for Phase 4 (H6: Flash→Pro Transfer Testing).

Tests end-to-end workflows including:
- Study YAML loading and validation
- Tile selection and manifest generation
- Transfer decision workflow integration
"""

import pytest
import sys
from pathlib import Path

import yaml

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib_phase4_transfer import (
    evaluate_baseline_transfer,
    evaluate_factor_sensitivity,
    evaluate_voting_threshold_transfer,
    classify_transfer_outcome,
    TransferClassification,
    FactorSensitivityResult,
    VotingTransferResult,
)
from select_tiles_phase4 import (
    select_stratified_subset,
    get_density_distribution,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def phase4_yaml_path() -> Path:
    """Path to Phase 4 study YAML."""
    return Path(__file__).parent.parent / "studies" / "phase4-transfer.yaml"


@pytest.fixture
def sample_phase2_results() -> dict:
    """
    Simulated Phase 2-3 results for integration testing.

    These represent the Flash-optimal configuration that would be
    carried forward to Phase 4.
    """
    return {
        "optimal_me_config": "prompts/configs/detect_brief-text-image.json",
        "optimal_me_instruction": "prompts/system-instructions/detect_brief-text-image.md",
        "optimal_temperature": 1.0,
        "optimal_library": "prompts/configs/library_scale-8.json",
        "optimal_h5_level": "minimal",
        "optimal_ordering": "canonical-first",
        "flash_optimal_n": 5,
        "flash_optimal_threshold": 2,
        "flash_f1": 0.82,
    }


@pytest.fixture
def sample_holdout_tiles() -> list[dict]:
    """
    Create sample holdout tiles for integration testing.

    Mimics the 60-tile holdout set with realistic distribution.
    """
    tiles = []

    # Empty tiles (30)
    for i in range(30):
        tiles.append({
            "filename": f"empty_tile_{i:03d}.png",
            "map": f"K-35-05{i // 10}-{i % 10}",
            "mound_count": 0,
            "density": "empty",
        })

    # Sparse tiles (18) - 1-2 mounds
    for i in range(18):
        tiles.append({
            "filename": f"sparse_tile_{i:03d}.png",
            "map": f"K-35-06{i // 6}-{i % 6}",
            "mound_count": 1 + (i % 2),
            "density": "sparse",
        })

    # Dense tiles (12) - 3+ mounds
    for i in range(12):
        tiles.append({
            "filename": f"dense_tile_{i:03d}.png",
            "map": f"K-35-07{i // 3}-{i % 3}",
            "mound_count": 3 + i,
            "density": "dense",
        })

    return tiles


# =============================================================================
# Tests: Study YAML Loading
# =============================================================================

class TestStudyYAMLIntegration:
    """Integration tests for Phase 4 study YAML."""

    @pytest.mark.tier2
    def test_study_yaml_exists(self, phase4_yaml_path: Path) -> None:
        """Phase 4 study YAML file should exist."""
        assert phase4_yaml_path.exists(), f"Missing: {phase4_yaml_path}"

    @pytest.mark.tier2
    def test_study_yaml_parses(self, phase4_yaml_path: Path) -> None:
        """Phase 4 study YAML should parse without errors."""
        with open(phase4_yaml_path) as f:
            data = yaml.safe_load(f)

        assert data is not None
        assert "study" in data
        assert "subphases" in data

    @pytest.mark.tier2
    def test_study_yaml_has_required_sections(self, phase4_yaml_path: Path) -> None:
        """Phase 4 study YAML should have all required sections."""
        with open(phase4_yaml_path) as f:
            data = yaml.safe_load(f)

        required_sections = [
            "study",
            "carried_forward",
            "model",
            "subphases",
            "fixed",
            "inputs",
            "execution",
            "analysis",
            "outputs",
            "estimates",
            "outcome",
        ]

        for section in required_sections:
            assert section in data, f"Missing section: {section}"

    @pytest.mark.tier2
    def test_study_yaml_subphases_complete(self, phase4_yaml_path: Path) -> None:
        """Phase 4 study YAML should define all sub-phases."""
        with open(phase4_yaml_path) as f:
            data = yaml.safe_load(f)

        subphases = data["subphases"]
        required_subphases = ["phase4a", "phase4b", "phase4c", "phase4d"]

        for subphase in required_subphases:
            assert subphase in subphases, f"Missing sub-phase: {subphase}"

    @pytest.mark.tier2
    def test_study_yaml_decision_thresholds(self, phase4_yaml_path: Path) -> None:
        """Phase 4 study YAML should define decision thresholds."""
        with open(phase4_yaml_path) as f:
            data = yaml.safe_load(f)

        thresholds = data["analysis"]["decision_thresholds"]

        assert thresholds["baseline_transfer"] == 0.05
        assert thresholds["baseline_investigate"] == 0.10
        assert thresholds["factor_adjustment"] == 0.03
        assert thresholds["voting_threshold"] == 0.10


# =============================================================================
# Tests: Tile Selection Integration
# =============================================================================

class TestTileSelectionIntegration:
    """Integration tests for Phase 4 tile selection."""

    @pytest.mark.tier2
    def test_selection_preserves_stratification(
        self, sample_holdout_tiles: list[dict]
    ) -> None:
        """Selected subset should preserve density stratification."""
        # Select 20 tiles (Phase 4 target)
        selected = select_stratified_subset(sample_holdout_tiles, 20, seed=42)

        # Get distributions
        original_dist = get_density_distribution(sample_holdout_tiles)
        selected_dist = get_density_distribution(selected)

        # Check each density has representation
        for density in ["empty", "sparse", "dense"]:
            assert selected_dist[density] > 0, f"No {density} tiles selected"

        # Check proportions are roughly maintained
        total_orig = len(sample_holdout_tiles)
        total_sel = len(selected)

        for density in ["empty", "sparse", "dense"]:
            orig_prop = original_dist[density] / total_orig
            sel_prop = selected_dist[density] / total_sel
            # Allow 20% deviation for small samples
            assert abs(orig_prop - sel_prop) <= 0.25, (
                f"{density}: {orig_prop:.1%} vs {sel_prop:.1%}"
            )

    @pytest.mark.tier2
    def test_selection_generates_valid_manifest(
        self, sample_holdout_tiles: list[dict]
    ) -> None:
        """Selected tiles should form a valid manifest structure."""
        selected = select_stratified_subset(sample_holdout_tiles, 20, seed=42)

        # All selected tiles should have required fields
        required_fields = ["filename", "density"]
        for tile in selected:
            for field in required_fields:
                assert field in tile, f"Missing field: {field}"

        # Filenames should be unique
        filenames = [t["filename"] for t in selected]
        assert len(filenames) == len(set(filenames)), "Duplicate filenames"


# =============================================================================
# Tests: Transfer Decision Workflow
# =============================================================================

class TestTransferWorkflowIntegration:
    """Integration tests for complete transfer decision workflow."""

    @pytest.mark.tier2
    def test_full_transfer_workflow(self, sample_phase2_results: dict) -> None:
        """
        Test complete Phase 4 workflow with full transfer scenario.

        Simulates: Pro performs similarly to Flash across all factors.
        """
        flash_f1 = sample_phase2_results["flash_f1"]

        # Phase 4a: Baseline comparison (Pro matches Flash)
        baseline_result = evaluate_baseline_transfer(
            flash_f1=flash_f1,
            pro_f1=0.80,  # Within 0.05 threshold
        )
        assert baseline_result.decision == "proceed"

        # Phase 4b: Factor sensitivity (no flags)
        factor_results = []

        # M/E factor - no significant improvement
        me_result = evaluate_factor_sensitivity(
            factor_name="M/E",
            flash_optimal_level="brief-text-image",
            baseline_f1=0.80,
            alternatives=[
                {"level": "verbose-text-image", "f1": 0.81, "ci_lower": -0.02, "ci_upper": 0.04},
            ],
        )
        factor_results.append(me_result)
        assert me_result.flagged is False

        # H5 factor - no significant improvement
        h5_result = evaluate_factor_sensitivity(
            factor_name="H5",
            flash_optimal_level="minimal",
            baseline_f1=0.80,
            alternatives=[
                {"level": "terse", "f1": 0.79, "ci_lower": -0.04, "ci_upper": 0.02},
            ],
        )
        factor_results.append(h5_result)
        assert h5_result.flagged is False

        # Phase 4c: Voting threshold (transfers)
        voting_result = evaluate_voting_threshold_transfer(
            flash_optimal_n=5,
            flash_optimal_threshold=2,
            pro_optimal_n=5,
            pro_optimal_threshold=2,  # Same threshold
        )
        assert voting_result.flagged is False

        # Classify overall outcome
        outcome = classify_transfer_outcome(
            factor_results=factor_results,
            voting_result=voting_result,
        )

        assert outcome.classification == TransferClassification.FULL_TRANSFER
        assert len(outcome.factors_flagged) == 0
        assert outcome.voting_flagged is False

    @pytest.mark.tier2
    def test_partial_transfer_workflow(self, sample_phase2_results: dict) -> None:
        """
        Test complete Phase 4 workflow with partial transfer scenario.

        Simulates: Pro needs adjustment for one factor (H5).
        """
        flash_f1 = sample_phase2_results["flash_f1"]

        # Phase 4a: Baseline comparison (marginal but acceptable)
        baseline_result = evaluate_baseline_transfer(
            flash_f1=flash_f1,
            pro_f1=0.76,  # Within investigate threshold
        )
        assert baseline_result.decision == "proceed_with_caution"

        # Phase 4b: Factor sensitivity (one flag)
        factor_results = []

        # M/E factor - no significant improvement
        me_result = evaluate_factor_sensitivity(
            factor_name="M/E",
            flash_optimal_level="brief-text-image",
            baseline_f1=0.76,
            alternatives=[
                {"level": "verbose-text-image", "f1": 0.77, "ci_lower": -0.02, "ci_upper": 0.04},
            ],
        )
        factor_results.append(me_result)

        # H5 factor - FLAGGED: terse significantly better for Pro
        h5_result = evaluate_factor_sensitivity(
            factor_name="H5",
            flash_optimal_level="minimal",
            baseline_f1=0.76,
            alternatives=[
                {"level": "terse", "f1": 0.80, "ci_lower": 0.01, "ci_upper": 0.07},  # CI excludes 0
            ],
        )
        factor_results.append(h5_result)
        assert h5_result.flagged is True
        assert h5_result.recommended_level == "terse"

        # Phase 4c: Voting threshold (minor difference)
        voting_result = evaluate_voting_threshold_transfer(
            flash_optimal_n=5,
            flash_optimal_threshold=2,
            pro_optimal_n=5,
            pro_optimal_threshold=2,  # Same
        )

        # Classify overall outcome
        outcome = classify_transfer_outcome(
            factor_results=factor_results,
            voting_result=voting_result,
        )

        assert outcome.classification == TransferClassification.PARTIAL_TRANSFER
        assert "H5" in outcome.factors_flagged
        assert outcome.pro_adjustments["H5"] == "terse"

    @pytest.mark.tier2
    def test_poor_transfer_workflow(self, sample_phase2_results: dict) -> None:
        """
        Test complete Phase 4 workflow with poor transfer scenario.

        Simulates: Pro needs adjustment for multiple factors.
        """
        # Phase 4b: Multiple factors flagged
        factor_results = []

        # M/E flagged
        me_result = FactorSensitivityResult(
            factor_name="M/E",
            flash_optimal_level="brief-text-image",
            tested_levels=[],
            flagged=True,
            recommended_level="verbose-text-image",
            message="",
        )
        factor_results.append(me_result)

        # H5 flagged
        h5_result = FactorSensitivityResult(
            factor_name="H5",
            flash_optimal_level="minimal",
            tested_levels=[],
            flagged=True,
            recommended_level="verbose",
            message="",
        )
        factor_results.append(h5_result)

        # T (temperature) flagged
        t_result = FactorSensitivityResult(
            factor_name="T",
            flash_optimal_level="1.0",
            tested_levels=[],
            flagged=True,
            recommended_level="0.7",
            message="",
        )
        factor_results.append(t_result)

        # Voting also differs
        voting_result = VotingTransferResult(
            flash_optimal_n=5,
            flash_optimal_threshold=2,
            pro_optimal_n=5,
            pro_optimal_threshold=3,
            relative_difference=0.50,
            flagged=True,
            needs_extended_test=True,
            message="",
        )

        # Classify overall outcome
        outcome = classify_transfer_outcome(
            factor_results=factor_results,
            voting_result=voting_result,
        )

        assert outcome.classification == TransferClassification.POOR_TRANSFER
        assert len(outcome.factors_flagged) == 3
        assert outcome.voting_flagged is True
        assert "voting_threshold" in outcome.pro_adjustments

    @pytest.mark.tier2
    def test_investigate_baseline_triggers_stop(
        self, sample_phase2_results: dict
    ) -> None:
        """
        Test that large baseline degradation triggers investigation.

        Per decision rule: If |Δ F1| > 0.10 → STOP, investigate.
        """
        flash_f1 = sample_phase2_results["flash_f1"]

        # Phase 4a: Large degradation
        baseline_result = evaluate_baseline_transfer(
            flash_f1=flash_f1,
            pro_f1=0.68,  # Δ = -0.14, beyond investigate threshold
        )

        assert baseline_result.decision == "investigate"
        assert abs(baseline_result.delta_f1) > 0.10
        assert "Large degradation" in baseline_result.message


# =============================================================================
# Tests: Cross-Component Integration
# =============================================================================

class TestCrossComponentIntegration:
    """Tests for integration between Phase 4 components."""

    @pytest.mark.tier2
    def test_tile_selection_to_workflow(
        self, sample_holdout_tiles: list[dict]
    ) -> None:
        """
        Test that selected tiles can be used in transfer workflow.

        Verifies the pipeline from tile selection → results simulation → decision.
        """
        # Step 1: Select tiles
        selected = select_stratified_subset(sample_holdout_tiles, 20, seed=42)
        assert len(selected) == 20

        # Step 2: Simulate results (would come from actual API calls)
        # This simulates what analyse_phase4_transfer.py would compute
        simulated_pro_f1 = 0.78
        simulated_flash_f1 = 0.82

        # Step 3: Evaluate baseline
        baseline_result = evaluate_baseline_transfer(
            flash_f1=simulated_flash_f1,
            pro_f1=simulated_pro_f1,
        )

        # Step 4: Verify workflow proceeds
        assert baseline_result.decision in ["proceed", "proceed_with_caution"]

    @pytest.mark.tier2
    def test_study_yaml_thresholds_match_constants(
        self, phase4_yaml_path: Path
    ) -> None:
        """
        Verify YAML thresholds match lib_phase4_transfer constants.

        Ensures consistency between configuration and implementation.
        """
        from lib_phase4_transfer import (
            BASELINE_TRANSFER_THRESHOLD,
            BASELINE_INVESTIGATE_THRESHOLD,
            FACTOR_ADJUSTMENT_THRESHOLD,
            VOTING_THRESHOLD_DIFFERENCE,
        )

        with open(phase4_yaml_path) as f:
            data = yaml.safe_load(f)

        thresholds = data["analysis"]["decision_thresholds"]

        assert thresholds["baseline_transfer"] == BASELINE_TRANSFER_THRESHOLD
        assert thresholds["baseline_investigate"] == BASELINE_INVESTIGATE_THRESHOLD
        assert thresholds["factor_adjustment"] == FACTOR_ADJUSTMENT_THRESHOLD
        assert thresholds["voting_threshold"] == VOTING_THRESHOLD_DIFFERENCE
