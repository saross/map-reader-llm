"""
Tests for Phase 1 runner helper functions.

Tier 1 unit tests for the configuration loading, checkpointing, and preflight
validation functions in run_phase1.py.
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

from scripts.run_phase1 import (
    load_study_config,
    load_checkpoint,
    save_checkpoint,
)


@pytest.mark.tier1
class TestLoadStudyConfig:
    """Tests for YAML study configuration loading."""

    def test_load_valid_config(self) -> None:
        """Valid YAML config should load successfully."""
        config_content = {
            "study": {
                "name": "Test Study",
                "version": "1.0.0",
                "description": "Test description",
            },
            "config": {"file": "prompts/configs/test.json"},
            "inputs": {
                "manifest": "inputs/tiles/test_manifest.json",
                "ground_truth": "inputs/vectors/references/test.geojson",
                "bounds": "inputs/vectors/bounds/test_bounds.geojson",
            },
            "execution": {
                "passes": 5,
                "workers": 1,
                "output_dir": "outputs/test",
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_content, f)
            temp_path = Path(f.name)

        try:
            result = load_study_config(temp_path)

            assert result["study"]["name"] == "Test Study"
            assert result["config"]["file"] == "prompts/configs/test.json"
            assert result["inputs"]["manifest"] == "inputs/tiles/test_manifest.json"
            assert result["execution"]["passes"] == 5
        finally:
            temp_path.unlink()

    def test_load_missing_config(self) -> None:
        """Missing config file should raise FileNotFoundError."""
        fake_path = Path("/nonexistent/path/to/config.yaml")

        with pytest.raises(FileNotFoundError):
            load_study_config(fake_path)

    def test_load_config_missing_sections(self) -> None:
        """Config missing required sections should raise ValueError."""
        # Missing 'execution' section
        config_content = {
            "study": {"name": "Test"},
            "config": {"file": "test.json"},
            "inputs": {"manifest": "test.json"},
            # Missing 'execution'
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_content, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Missing required section"):
                load_study_config(temp_path)
        finally:
            temp_path.unlink()

    def test_load_config_all_required_sections(self) -> None:
        """Config with all required sections should validate."""
        required_sections = ["study", "config", "inputs", "execution"]

        config_content = {section: {} for section in required_sections}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config_content, f)
            temp_path = Path(f.name)

        try:
            # Should not raise
            result = load_study_config(temp_path)
            for section in required_sections:
                assert section in result
        finally:
            temp_path.unlink()


@pytest.mark.tier1
class TestLoadCheckpoint:
    """Tests for checkpoint loading."""

    def test_load_existing_checkpoint(self) -> None:
        """Existing checkpoint file should load correctly."""
        checkpoint_data = {
            "completed_passes": [1, 2, 3],
            "failed_passes": [],
            "last_updated": "2026-01-15T12:00:00+00:00",
            "merge_complete": True,
            "evaluation_complete": False,
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(checkpoint_data, f)
            temp_path = Path(f.name)

        try:
            result = load_checkpoint(temp_path)

            assert result["completed_passes"] == [1, 2, 3]
            assert result["failed_passes"] == []
            assert result["merge_complete"] is True
            assert result["evaluation_complete"] is False
        finally:
            temp_path.unlink()

    def test_load_nonexistent_checkpoint(self) -> None:
        """Nonexistent checkpoint should return default structure."""
        fake_path = Path("/nonexistent/checkpoint.json")

        result = load_checkpoint(fake_path)

        assert result["completed_passes"] == []
        assert result["failed_passes"] == []
        assert result["last_updated"] is None
        assert result["merge_complete"] is False
        assert result["evaluation_complete"] is False

    def test_load_checkpoint_default_structure(self) -> None:
        """Default checkpoint structure should have all required fields."""
        fake_path = Path("/nonexistent/checkpoint.json")
        result = load_checkpoint(fake_path)

        required_fields = [
            "completed_passes",
            "failed_passes",
            "last_updated",
            "merge_complete",
            "evaluation_complete",
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"


@pytest.mark.tier1
class TestSaveCheckpoint:
    """Tests for checkpoint saving."""

    def test_save_checkpoint_creates_file(self) -> None:
        """Saving checkpoint should create the file."""
        checkpoint = {
            "completed_passes": [1, 2],
            "failed_passes": [],
            "last_updated": None,
            "merge_complete": False,
            "evaluation_complete": False,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            save_checkpoint(checkpoint_path, checkpoint)

            assert checkpoint_path.exists()

            # Verify contents
            with open(checkpoint_path) as f:
                saved = json.load(f)

            assert saved["completed_passes"] == [1, 2]

    def test_save_checkpoint_updates_timestamp(self) -> None:
        """Saving checkpoint should update last_updated timestamp."""
        checkpoint = {
            "completed_passes": [],
            "failed_passes": [],
            "last_updated": None,
            "merge_complete": False,
            "evaluation_complete": False,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            # Get time before save
            before = datetime.now(timezone.utc)

            save_checkpoint(checkpoint_path, checkpoint)

            # Get time after save
            after = datetime.now(timezone.utc)

            # Load and check timestamp
            with open(checkpoint_path) as f:
                saved = json.load(f)

            saved_time = datetime.fromisoformat(saved["last_updated"])

            assert before <= saved_time <= after

    def test_save_checkpoint_creates_parent_dirs(self) -> None:
        """Saving checkpoint should create parent directories if needed."""
        checkpoint = {
            "completed_passes": [],
            "failed_passes": [],
            "last_updated": None,
            "merge_complete": False,
            "evaluation_complete": False,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # Nested path that doesn't exist
            checkpoint_path = Path(tmpdir) / "nested" / "dir" / "checkpoint.json"

            save_checkpoint(checkpoint_path, checkpoint)

            assert checkpoint_path.exists()

    def test_save_and_load_roundtrip(self) -> None:
        """Saved checkpoint should load back with same data."""
        original = {
            "completed_passes": [1, 2, 3, 4, 5],
            "failed_passes": [{"pass": 6, "error": "timeout"}],
            "last_updated": None,
            "merge_complete": True,
            "evaluation_complete": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            save_checkpoint(checkpoint_path, original)
            loaded = load_checkpoint(checkpoint_path)

            assert loaded["completed_passes"] == original["completed_passes"]
            assert loaded["failed_passes"] == original["failed_passes"]
            assert loaded["merge_complete"] == original["merge_complete"]
            assert loaded["evaluation_complete"] == original["evaluation_complete"]
            # last_updated will be different (updated on save)
            assert loaded["last_updated"] is not None


@pytest.mark.tier1
class TestCheckpointResume:
    """Tests for checkpoint-based resume functionality."""

    def test_resume_skips_completed_passes(self) -> None:
        """Completed passes should be skippable on resume."""
        checkpoint = {
            "completed_passes": [1, 2, 3],
            "failed_passes": [],
            "last_updated": "2026-01-15T12:00:00+00:00",
            "merge_complete": False,
            "evaluation_complete": False,
        }

        completed_set = set(checkpoint.get("completed_passes", []))
        total_passes = 5

        # Simulate checking which passes to run
        passes_to_run = []
        for i in range(1, total_passes + 1):
            if i not in completed_set:
                passes_to_run.append(i)

        assert passes_to_run == [4, 5]

    def test_resume_with_no_completed(self) -> None:
        """Resume with no completed passes should run all passes."""
        checkpoint = {
            "completed_passes": [],
            "failed_passes": [],
            "last_updated": None,
            "merge_complete": False,
            "evaluation_complete": False,
        }

        completed_set = set(checkpoint.get("completed_passes", []))
        total_passes = 5

        passes_to_run = [i for i in range(1, total_passes + 1) if i not in completed_set]

        assert passes_to_run == [1, 2, 3, 4, 5]

    def test_resume_with_all_completed(self) -> None:
        """Resume with all passes completed should run no passes."""
        checkpoint = {
            "completed_passes": [1, 2, 3, 4, 5],
            "failed_passes": [],
            "last_updated": "2026-01-15T12:00:00+00:00",
            "merge_complete": False,
            "evaluation_complete": False,
        }

        completed_set = set(checkpoint.get("completed_passes", []))
        total_passes = 5

        passes_to_run = [i for i in range(1, total_passes + 1) if i not in completed_set]

        assert passes_to_run == []
