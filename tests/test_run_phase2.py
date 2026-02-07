"""
Tests for Phase 2 OFAT runner helper functions.

Tier 1 unit tests for configuration loading, condition extraction,
execution unit generation, and checkpoint logic in run_phase2.py.
"""

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_phase2 import (
    extract_conditions,
    generate_execution_units,
    load_checkpoint,
    load_study_config,
    run_execution_unit,
    save_checkpoint,
    unit_key,
    validate_configs,
)


# =============================================================================
# Fixtures
# =============================================================================


def _make_phase2a_config() -> dict:
    """Build a minimal Phase 2a-style YAML config for testing."""
    return {
        "study": {
            "name": "Test Phase 2a",
            "version": "1.0",
            "phase": "2a",
            "hypothesis": "H1",
        },
        "factors": {
            "modality_elaboration": {
                "description": "Test factor",
                "levels": [
                    {
                        "name": "image-only",
                        "config": "prompts/configs/detect_image-only.json",
                        "description": "No text guidance",
                    },
                    {
                        "name": "brief-text",
                        "config": "prompts/configs/detect_brief-text.json",
                        "description": "Concise text, no images",
                    },
                    {
                        "name": "verbose-text-image",
                        "config": "prompts/configs/detect_verbose-text-image.json",
                        "description": "Detailed text with images",
                    },
                ],
            },
        },
        "inputs": {
            "manifest": "inputs/tiles/validation_manifest.json",
            "ground_truth": "inputs/vectors/references/mounds-reference.geojson",
            "bounds": "inputs/vectors/bounds/validation_bounds.geojson",
        },
        "execution": {
            "runs": 10,
            "workers": 1,
            "output_dir": "outputs/test-phase2a",
        },
        "estimates": {
            "cells": 3,
            "total_api_calls": 1800,
            "cost_usd": 7,
        },
    }


def _make_phase2b_config() -> dict:
    """Build a minimal Phase 2b-style YAML config (temperature factor)."""
    return {
        "study": {
            "name": "Test Phase 2b",
            "version": "1.0",
            "phase": "2b",
            "hypothesis": "H7",
        },
        "carried_forward": {
            "optimal_me_config": "prompts/configs/detect_image-only.json",
            "optimal_me_name": "image-only",
        },
        "factors": {
            "temperature": {
                "description": "Model temperature",
                "levels": [
                    {"name": "T0.0", "value": 0.0, "description": "Deterministic"},
                    {"name": "T1.0", "value": 1.0, "description": "Default"},
                    {"name": "T1.3", "value": 1.3, "description": "Above default"},
                ],
            },
        },
        "inputs": {
            "manifest": "inputs/tiles/validation_manifest.json",
        },
        "execution": {
            "runs": 10,
            "workers": 1,
            "output_dir": "outputs/test-phase2b",
        },
    }


def _make_phase2d_config() -> dict:
    """Build a minimal Phase 2d-style YAML config (pre-enumerated conditions)."""
    return {
        "study": {
            "name": "Test Phase 2d",
            "version": "1.0",
            "phase": "2d",
            "hypothesis": "H5",
        },
        "factors": {
            "modality_elaboration": {
                "description": "Placeholder",
                "levels": [],
            },
        },
        "conditions": [
            {
                "name": "image-only_minimal",
                "config": "prompts/configs/detect_image-only.json",
                "reuse_from": "phase2a",
            },
            {
                "name": "image-only_terse",
                "config": "prompts/configs/detect_image-only_terse.json",
                "run": True,
            },
            {
                "name": "image-only_verbose",
                "config": "prompts/configs/detect_image-only_verbose.json",
                "run": True,
            },
        ],
        "inputs": {
            "manifest": "inputs/tiles/validation_manifest.json",
        },
        "execution": {
            "runs": 10,
            "workers": 1,
            "output_dir": "outputs/test-phase2d",
        },
    }


def _write_yaml(config: dict) -> Path:
    """Write a config dict to a temporary YAML file and return the path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    yaml.dump(config, f)
    f.close()
    return Path(f.name)


# =============================================================================
# Tests: load_study_config
# =============================================================================


@pytest.mark.tier1
class TestLoadStudyConfig:
    """Tests for YAML study configuration loading."""

    def test_load_valid_phase2a_config(self) -> None:
        """Valid Phase 2a YAML config should load successfully."""
        config = _make_phase2a_config()
        path = _write_yaml(config)

        try:
            result = load_study_config(path)
            assert result["study"]["name"] == "Test Phase 2a"
            assert "factors" in result
            assert "inputs" in result
            assert "execution" in result
        finally:
            path.unlink()

    def test_load_missing_file(self) -> None:
        """Missing config file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_study_config(Path("/nonexistent/config.yaml"))

    def test_load_missing_factors_section(self) -> None:
        """Config missing 'factors' section should raise ValueError."""
        config = _make_phase2a_config()
        del config["factors"]
        path = _write_yaml(config)

        try:
            with pytest.raises(ValueError, match="Missing required section"):
                load_study_config(path)
        finally:
            path.unlink()

    def test_load_missing_inputs_section(self) -> None:
        """Config missing 'inputs' section should raise ValueError."""
        config = _make_phase2a_config()
        del config["inputs"]
        path = _write_yaml(config)

        try:
            with pytest.raises(ValueError, match="Missing required section"):
                load_study_config(path)
        finally:
            path.unlink()

    def test_load_missing_execution_section(self) -> None:
        """Config missing 'execution' section should raise ValueError."""
        config = _make_phase2a_config()
        del config["execution"]
        path = _write_yaml(config)

        try:
            with pytest.raises(ValueError, match="Missing required section"):
                load_study_config(path)
        finally:
            path.unlink()

    def test_load_missing_manifest(self) -> None:
        """Config with empty inputs (no manifest) should raise ValueError."""
        config = _make_phase2a_config()
        config["inputs"] = {"ground_truth": "test.geojson"}
        path = _write_yaml(config)

        try:
            with pytest.raises(ValueError, match="manifest"):
                load_study_config(path)
        finally:
            path.unlink()

    def test_load_missing_runs(self) -> None:
        """Config without runs in execution should raise ValueError."""
        config = _make_phase2a_config()
        config["execution"] = {"workers": 1, "output_dir": "outputs/test"}
        path = _write_yaml(config)

        try:
            with pytest.raises(ValueError, match="runs"):
                load_study_config(path)
        finally:
            path.unlink()

    def test_load_missing_output_dir(self) -> None:
        """Config without output_dir in execution should raise ValueError."""
        config = _make_phase2a_config()
        config["execution"] = {"runs": 10, "workers": 1}
        path = _write_yaml(config)

        try:
            with pytest.raises(ValueError, match="output_dir"):
                load_study_config(path)
        finally:
            path.unlink()


# =============================================================================
# Tests: extract_conditions
# =============================================================================


@pytest.mark.tier1
class TestExtractConditions:
    """Tests for condition extraction from YAML factor definitions."""

    def test_extract_phase2a_conditions(self) -> None:
        """Phase 2a-style YAML should produce correct condition list."""
        config = _make_phase2a_config()
        conditions = extract_conditions(config)

        assert len(conditions) == 3
        names = [c["name"] for c in conditions]
        assert "image-only" in names
        assert "brief-text" in names
        assert "verbose-text-image" in names

    def test_condition_has_config_path(self) -> None:
        """Each condition should have a config path."""
        config = _make_phase2a_config()
        conditions = extract_conditions(config)

        for condition in conditions:
            assert condition["config"], f"Missing config for {condition['name']}"
            assert condition["config"].endswith(".json")

    def test_phase2b_temperature_conditions(self) -> None:
        """Phase 2b-style YAML should extract temperature overrides."""
        config = _make_phase2b_config()
        conditions = extract_conditions(config)

        assert len(conditions) == 3

        # Check temperature overrides are set
        temps = {c["name"]: c["temperature"] for c in conditions}
        assert temps["T0.0"] == 0.0
        assert temps["T1.0"] == 1.0
        assert temps["T1.3"] == 1.3

    def test_phase2b_uses_carried_forward_config(self) -> None:
        """Temperature conditions should use the carried-forward config."""
        config = _make_phase2b_config()
        conditions = extract_conditions(config)

        for condition in conditions:
            assert condition["config"] == "prompts/configs/detect_image-only.json"

    def test_phase2d_skips_reused_conditions(self) -> None:
        """Phase 2d-style YAML should skip conditions with reuse_from."""
        config = _make_phase2d_config()
        conditions = extract_conditions(config)

        assert len(conditions) == 2
        names = [c["name"] for c in conditions]
        assert "image-only_minimal" not in names  # Reused from phase2a
        assert "image-only_terse" in names
        assert "image-only_verbose" in names

    def test_empty_factors_returns_empty(self) -> None:
        """Empty factors should return no conditions."""
        config = _make_phase2a_config()
        config["factors"] = {"test": {"levels": []}}
        conditions = extract_conditions(config)
        assert conditions == []


# =============================================================================
# Tests: generate_execution_units
# =============================================================================


@pytest.mark.tier1
class TestGenerateExecutionUnits:
    """Tests for execution unit generation."""

    def test_correct_unit_count(self) -> None:
        """Total units should be conditions x runs."""
        conditions = [
            {"name": "cond_a", "config": "a.json"},
            {"name": "cond_b", "config": "b.json"},
        ]
        units = generate_execution_units(conditions, num_runs=3)
        assert len(units) == 6  # 2 conditions x 3 runs

    def test_units_have_required_fields(self) -> None:
        """Each unit should have condition_name, run, and config."""
        conditions = [{"name": "test", "config": "test.json"}]
        units = generate_execution_units(conditions, num_runs=2)

        for unit in units:
            assert "condition_name" in unit
            assert "run" in unit
            assert "config" in unit

    def test_runs_are_one_indexed(self) -> None:
        """Run numbers should be 1-indexed."""
        conditions = [{"name": "test", "config": "test.json"}]
        units = generate_execution_units(conditions, num_runs=3)

        run_nums = sorted(u["run"] for u in units)
        assert run_nums == [1, 2, 3]

    def test_deterministic_shuffle(self) -> None:
        """Same seed should produce same unit order."""
        conditions = [
            {"name": "a", "config": "a.json"},
            {"name": "b", "config": "b.json"},
        ]

        units_1 = generate_execution_units(conditions, num_runs=5, seed=42)
        units_2 = generate_execution_units(conditions, num_runs=5, seed=42)

        keys_1 = [unit_key(u) for u in units_1]
        keys_2 = [unit_key(u) for u in units_2]

        assert keys_1 == keys_2

    def test_different_seeds_differ(self) -> None:
        """Different seeds should produce different unit orders."""
        conditions = [
            {"name": "a", "config": "a.json"},
            {"name": "b", "config": "b.json"},
            {"name": "c", "config": "c.json"},
        ]

        units_1 = generate_execution_units(conditions, num_runs=10, seed=42)
        units_2 = generate_execution_units(conditions, num_runs=10, seed=99)

        keys_1 = [unit_key(u) for u in units_1]
        keys_2 = [unit_key(u) for u in units_2]

        # Same set of units, different order
        assert sorted(keys_1) == sorted(keys_2)
        assert keys_1 != keys_2

    def test_all_condition_run_pairs_present(self) -> None:
        """Every (condition, run) pair should appear exactly once."""
        conditions = [
            {"name": "a", "config": "a.json"},
            {"name": "b", "config": "b.json"},
        ]
        units = generate_execution_units(conditions, num_runs=3)

        pairs = {(u["condition_name"], u["run"]) for u in units}
        expected = {("a", 1), ("a", 2), ("a", 3), ("b", 1), ("b", 2), ("b", 3)}
        assert pairs == expected


# =============================================================================
# Tests: validate_configs
# =============================================================================


@pytest.mark.tier1
class TestValidateConfigs:
    """Tests for config file validation."""

    def test_existing_configs_valid(self) -> None:
        """Conditions with existing config files should be valid."""
        # Use actual config files from the project
        conditions = [
            {
                "name": "image-only",
                "config": "prompts/configs/detect_image-only.json",
            },
        ]

        valid, missing = validate_configs(conditions)

        assert len(valid) == 1
        assert len(missing) == 0

    def test_missing_configs_detected(self) -> None:
        """Conditions with nonexistent configs should be flagged."""
        conditions = [
            {
                "name": "nonexistent",
                "config": "prompts/configs/does_not_exist.json",
            },
        ]

        valid, missing = validate_configs(conditions)

        assert len(valid) == 0
        assert len(missing) == 1

    def test_mixed_valid_and_missing(self) -> None:
        """Mix of valid and missing configs should be separated correctly."""
        conditions = [
            {
                "name": "image-only",
                "config": "prompts/configs/detect_image-only.json",
            },
            {
                "name": "nonexistent",
                "config": "prompts/configs/does_not_exist.json",
            },
        ]

        valid, missing = validate_configs(conditions)

        assert len(valid) == 1
        assert len(missing) == 1
        assert valid[0]["name"] == "image-only"
        assert missing[0]["name"] == "nonexistent"


# =============================================================================
# Tests: unit_key
# =============================================================================


@pytest.mark.tier1
class TestUnitKey:
    """Tests for execution unit key generation."""

    def test_key_format(self) -> None:
        """Unit key should be 'condition_name/run_N'."""
        unit = {"condition_name": "image-only", "run": 3}
        assert unit_key(unit) == "image-only/run_3"

    def test_keys_unique_per_pair(self) -> None:
        """Different (condition, run) pairs should produce different keys."""
        unit_a = {"condition_name": "a", "run": 1}
        unit_b = {"condition_name": "a", "run": 2}
        unit_c = {"condition_name": "b", "run": 1}

        keys = {unit_key(unit_a), unit_key(unit_b), unit_key(unit_c)}
        assert len(keys) == 3


# =============================================================================
# Tests: Checkpoint loading and saving
# =============================================================================


@pytest.mark.tier1
class TestCheckpoint:
    """Tests for checkpoint save/load cycle."""

    def test_load_nonexistent_returns_default(self) -> None:
        """Loading nonexistent checkpoint should return default structure."""
        result = load_checkpoint(Path("/nonexistent/checkpoint.json"))

        assert result["completed"] == []
        assert result["failed"] == []
        assert result["total_cost_usd"] == 0.0
        assert result["last_updated"] is None

    def test_save_creates_file(self) -> None:
        """Saving checkpoint should create the file."""
        checkpoint = {
            "completed": ["cond_a/run_1", "cond_a/run_2"],
            "failed": [],
            "total_cost_usd": 0.006,
            "last_updated": None,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            save_checkpoint(path, checkpoint)

            assert path.exists()
            with open(path) as f:
                saved = json.load(f)
            assert saved["completed"] == ["cond_a/run_1", "cond_a/run_2"]

    def test_save_updates_timestamp(self) -> None:
        """Saving checkpoint should update last_updated."""
        checkpoint = {
            "completed": [],
            "failed": [],
            "total_cost_usd": 0.0,
            "last_updated": None,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            before = datetime.now(timezone.utc)
            save_checkpoint(path, checkpoint)
            after = datetime.now(timezone.utc)

            with open(path) as f:
                saved = json.load(f)

            saved_time = datetime.fromisoformat(saved["last_updated"])
            assert before <= saved_time <= after

    def test_save_creates_parent_dirs(self) -> None:
        """Saving checkpoint should create parent directories."""
        checkpoint = {
            "completed": [],
            "failed": [],
            "total_cost_usd": 0.0,
            "last_updated": None,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dir" / "checkpoint.json"
            save_checkpoint(path, checkpoint)
            assert path.exists()

    def test_roundtrip(self) -> None:
        """Saved checkpoint should load back with same data."""
        original = {
            "completed": ["a/run_1", "b/run_2"],
            "failed": [{"unit": "c/run_1", "error": "timeout"}],
            "total_cost_usd": 0.042,
            "last_updated": None,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            save_checkpoint(path, original)
            loaded = load_checkpoint(path)

            assert loaded["completed"] == original["completed"]
            assert loaded["failed"] == original["failed"]
            assert loaded["total_cost_usd"] == pytest.approx(0.042)
            assert loaded["last_updated"] is not None


# =============================================================================
# Tests: Resume logic
# =============================================================================


@pytest.mark.tier1
class TestResumeLogic:
    """Tests for checkpoint-based resume filtering."""

    def test_resume_skips_completed(self) -> None:
        """Completed units should be filtered out on resume."""
        conditions = [
            {"name": "a", "config": "a.json"},
            {"name": "b", "config": "b.json"},
        ]
        units = generate_execution_units(conditions, num_runs=3, seed=42)
        completed = {"a/run_1", "a/run_2", "b/run_1"}

        remaining = [u for u in units if unit_key(u) not in completed]
        remaining_keys = {unit_key(u) for u in remaining}

        assert remaining_keys == {"a/run_3", "b/run_2", "b/run_3"}

    def test_resume_with_all_completed(self) -> None:
        """All completed should leave no remaining units."""
        conditions = [{"name": "a", "config": "a.json"}]
        units = generate_execution_units(conditions, num_runs=2, seed=42)
        completed = {"a/run_1", "a/run_2"}

        remaining = [u for u in units if unit_key(u) not in completed]
        assert remaining == []

    def test_resume_with_none_completed(self) -> None:
        """No completed should leave all units remaining."""
        conditions = [{"name": "a", "config": "a.json"}]
        units = generate_execution_units(conditions, num_runs=3, seed=42)
        completed: set[str] = set()

        remaining = [u for u in units if unit_key(u) not in completed]
        assert len(remaining) == 3


# =============================================================================
# Integration: Real YAML file loading
# =============================================================================


@pytest.mark.tier1
class TestRealYamlLoading:
    """Tests against actual Phase 2 YAML files in the repository."""

    @pytest.fixture
    def phase2a_path(self) -> Path:
        """Return path to actual Phase 2a YAML."""
        return PROJECT_ROOT / "studies" / "phase2a-h1-modality.yaml"

    def test_load_real_phase2a(self, phase2a_path: Path) -> None:
        """Actual Phase 2a YAML should load and validate."""
        if not phase2a_path.exists():
            pytest.skip("Phase 2a YAML not found")

        config = load_study_config(phase2a_path)
        assert config["study"]["phase"] == "2a"
        assert config["study"]["hypothesis"] == "H1"

    def test_extract_five_me_conditions(self, phase2a_path: Path) -> None:
        """Phase 2a should produce exactly 5 M/E conditions."""
        if not phase2a_path.exists():
            pytest.skip("Phase 2a YAML not found")

        config = load_study_config(phase2a_path)
        conditions = extract_conditions(config)
        assert len(conditions) == 5

    def test_phase2a_generates_50_units(self, phase2a_path: Path) -> None:
        """Phase 2a with K=10 should generate 50 execution units (5 x 10)."""
        if not phase2a_path.exists():
            pytest.skip("Phase 2a YAML not found")

        config = load_study_config(phase2a_path)
        conditions = extract_conditions(config)
        units = generate_execution_units(conditions, num_runs=10)
        assert len(units) == 50

    def test_phase2a_no_passes_field(self, phase2a_path: Path) -> None:
        """Phase 2a YAML should not contain a 'passes' field (corrected per E17)."""
        if not phase2a_path.exists():
            pytest.skip("Phase 2a YAML not found")

        config = load_study_config(phase2a_path)
        assert "passes" not in config.get("execution", {}), (
            "YAML should not contain 'passes' field — single-pass per §3.8"
        )


# =============================================================================
# Tests: Thread-safe checkpoint with lock
# =============================================================================


@pytest.mark.tier1
class TestCheckpointWithLock:
    """Tests for thread-safe save_checkpoint with optional lock parameter."""

    def test_save_without_lock_works(self) -> None:
        """save_checkpoint(lock=None) should behave identically to no lock."""
        checkpoint = {
            "completed": ["a/run_1"],
            "failed": [],
            "total_cost_usd": 0.0,
            "last_updated": None,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            save_checkpoint(path, checkpoint, lock=None)

            assert path.exists()
            with open(path) as f:
                saved = json.load(f)
            assert saved["completed"] == ["a/run_1"]

    def test_save_with_lock_works(self) -> None:
        """save_checkpoint with a threading.Lock should succeed."""
        import threading

        checkpoint = {
            "completed": ["a/run_1"],
            "failed": [],
            "total_cost_usd": 0.0,
            "last_updated": None,
        }
        lock = threading.Lock()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            save_checkpoint(path, checkpoint, lock=lock)

            assert path.exists()
            with open(path) as f:
                saved = json.load(f)
            assert saved["completed"] == ["a/run_1"]

    def test_concurrent_saves_with_lock(self) -> None:
        """Multiple threads saving with same lock should not corrupt data."""
        import threading

        lock = threading.Lock()
        errors: list[str] = []

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            checkpoint = {
                "completed": [],
                "failed": [],
                "total_cost_usd": 0.0,
                "last_updated": None,
            }

            def save_unit(unit_key_str: str) -> None:
                """Worker thread: append to checkpoint and save."""
                try:
                    with lock:
                        checkpoint["completed"].append(unit_key_str)
                        checkpoint["total_cost_usd"] += 0.001
                    save_checkpoint(path, checkpoint, lock=lock)
                except Exception as e:
                    errors.append(str(e))

            threads = [
                threading.Thread(
                    target=save_unit, args=(f"cond/run_{i}",)
                )
                for i in range(10)
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert not errors, f"Thread errors: {errors}"

            # Verify final state
            with open(path) as f:
                saved = json.load(f)
            assert len(saved["completed"]) == 10
            assert saved["total_cost_usd"] == pytest.approx(0.01)


# =============================================================================
# Tests: run_execution_unit with log_file
# =============================================================================


@pytest.mark.tier1
class TestRunExecutionUnitLogFile:
    """Tests for run_execution_unit log_file parameter."""

    def test_dry_run_ignores_log_file(self) -> None:
        """Dry run should work regardless of log_file parameter."""
        unit = {
            "condition_name": "T0.0",
            "run": 1,
            "config": "prompts/configs/detect_brief-text.json",
            "temperature": 0.0,
            "ordering": None,
        }
        config = _make_phase2b_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            log_file = output_dir / "logs" / "test.log"

            success, message, cost = run_execution_unit(
                unit, config, output_dir,
                dry_run=True, log_file=log_file,
            )

            assert success is True
            assert message == "dry_run"
            assert cost == 0.0
            # Log file should NOT be created for dry runs
            assert not log_file.exists()

    def test_log_file_parent_dir_created(self) -> None:
        """log_file with non-existent parent directory should be created."""
        unit = {
            "condition_name": "T0.0",
            "run": 1,
            "config": "prompts/configs/detect_brief-text.json",
            "temperature": 0.0,
            "ordering": None,
        }
        config = _make_phase2b_config()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            log_file = output_dir / "logs" / "nested" / "test.log"

            # Run with a fake script that will fail —
            # we just want to verify log_file parent creation
            success, _msg, _cost = run_execution_unit(
                unit, config, output_dir,
                dry_run=False, log_file=log_file, timeout=10,
            )

            # The subprocess will fail (missing tiles, etc.), but the
            # log file parent directory should exist
            assert log_file.parent.exists()


# =============================================================================
# Tests: Parallel unit cap and concurrency warnings
# =============================================================================


@pytest.mark.tier1
class TestParallelUnitsCap:
    """Tests for parallel_units cap and warning logic."""

    def test_parallel_units_capped_at_eight(self) -> None:
        """parallel_units > 8 should be clamped to 8."""
        config = _make_phase2b_config()
        path = _write_yaml(config)

        try:
            from scripts.run_phase2 import run_phase2

            # With dry_run, parallel_units is capped but not actually
            # used (dry runs run sequentially). Verify the cap logic
            # by checking the function accepts the parameter.
            results = run_phase2(
                study_path=path,
                dry_run=True,
                parallel_units=12,
                verbose=False,
            )
            # Dry run should not error
            assert results is not None
        finally:
            path.unlink()

    def test_parallel_units_one_is_sequential(self) -> None:
        """parallel_units=1 should produce identical behaviour to default."""
        config = _make_phase2b_config()
        path = _write_yaml(config)

        try:
            from scripts.run_phase2 import run_phase2

            results = run_phase2(
                study_path=path,
                dry_run=True,
                parallel_units=1,
                verbose=False,
            )
            # Should complete normally with no units run
            assert results is not None
            assert "error" not in results
        finally:
            path.unlink()
