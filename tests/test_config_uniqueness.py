"""
Tests for prompt configuration file integrity.

Tier 1 tests verifying that all configuration files:
1. Load without errors
2. Contain required fields (execution configs only)
3. Have distinct parameter signatures (no accidental duplicates)

Note: "library_*.json" files are example library definitions, not execution
configs. They define example sets without model/temperature because they're
meant to be composed with other configs.
"""

import hashlib
import json
from pathlib import Path

import pytest

# Minimum number of config files expected
MINIMUM_CONFIG_COUNT = 36

# Execution config prefixes (configs that run experiments)
EXECUTION_CONFIG_PREFIXES = ("detect_", "pilot_", "propose_", "verify_")

# Required fields in execution config files
REQUIRED_FIELDS = {"model", "temperature"}


@pytest.mark.tier1
class TestConfigLoading:
    """Tests for config file loading."""

    def test_configs_load_without_error(self, configs_dir: Path) -> None:
        """Verify all config JSON files load without parse errors.

        Ensures no malformed JSON exists in the configs directory.
        """
        config_files = list(configs_dir.glob("*.json"))

        assert len(config_files) >= MINIMUM_CONFIG_COUNT, (
            f"Expected at least {MINIMUM_CONFIG_COUNT} config files, "
            f"found {len(config_files)}"
        )

        errors = []
        for config_file in config_files:
            try:
                with open(config_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"{config_file.name}: {e}")

        assert not errors, f"Config files with JSON errors:\n" + "\n".join(errors)


@pytest.mark.tier1
class TestConfigSchema:
    """Tests for config file schema compliance."""

    def test_configs_have_required_fields(self, configs_dir: Path) -> None:
        """Verify execution config files have required fields: model, temperature.

        These fields are essential for VLM experiment execution.

        Note: Library configs (library_*.json) are excluded as they define
        example sets without execution parameters.
        """
        # Only check execution configs, not library configs
        config_files = [
            f for f in configs_dir.glob("*.json")
            if f.name.startswith(EXECUTION_CONFIG_PREFIXES)
        ]
        missing_fields = []

        for config_file in config_files:
            with open(config_file) as f:
                config = json.load(f)

            file_missing = REQUIRED_FIELDS - set(config.keys())
            if file_missing:
                missing_fields.append(f"{config_file.name}: missing {file_missing}")

        assert not missing_fields, (
            f"Config files missing required fields:\n" + "\n".join(missing_fields)
        )


@pytest.mark.tier1
class TestConfigUniqueness:
    """Tests for config parameter uniqueness."""

    def test_configs_have_distinct_parameters(self, configs_dir: Path) -> None:
        """Verify no two execution config files have identical parameter signatures.

        Creates a signature from key experimental parameters to detect
        accidental duplicates that could waste experimental runs.

        Signature components:
        - version: Config identifier (includes ordering info)
        - model: The VLM model to use
        - temperature: Sampling temperature
        - instruction_file: System instruction file
        - thinking_level: Extended thinking configuration (if present)
        - example_order_hash: Hash of example paths to capture ordering

        Note: Different example orderings (canonical-first, random-order, etc.)
        are intentional experimental variations and should be considered unique.
        Library configs are excluded from this test.
        """
        # Only check execution configs
        config_files = [
            f for f in configs_dir.glob("*.json")
            if f.name.startswith(EXECUTION_CONFIG_PREFIXES)
        ]
        signatures: dict[str, list[str]] = {}

        for config_file in config_files:
            with open(config_file) as f:
                config = json.load(f)

            # Create hash of example ordering to capture this experimental variable
            examples = config.get("examples", [])
            example_paths = [e.get("path", "") for e in examples]
            order_hash = hashlib.md5("|".join(example_paths).encode()).hexdigest()[:8]

            # Build signature from key parameters including version and ordering
            sig_parts = [
                f"version={config.get('version', 'unset')}",
                f"model={config.get('model', 'unset')}",
                f"temp={config.get('temperature', 'unset')}",
                f"instruction={config.get('instruction_file', 'unset')}",
                f"thinking={config.get('thinking_level', 'none')}",
                f"order={order_hash}",
            ]
            signature = "|".join(sig_parts)

            if signature not in signatures:
                signatures[signature] = []
            signatures[signature].append(config_file.name)

        # Find duplicates
        duplicates = {
            sig: files for sig, files in signatures.items()
            if len(files) > 1
        }

        assert not duplicates, (
            f"Found config files with identical signatures:\n"
            + "\n".join(
                f"  {sig}: {files}" for sig, files in duplicates.items()
            )
        )
