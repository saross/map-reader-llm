"""
Tier-1 tests for command-line overrides in the recorded configuration.

Until 2026-09-14 a ``--temperature`` override reached the API through
``build_generation_config`` as a separate argument and never touched the
``configuration`` block a run's ``run.meta.json`` records. The cleanup
configuration gate (``run_pv.py`` ``_cleanup_configuration_gate``) fingerprints
that block, so it could not see a temperature change between a main pass and a
later pass over the same stage — the one gate field that silently did nothing
(``reports/cleanup-meta-fix-2026-09-14.md`` section 2.2, "Known blind spot").

``LLMMetadataTracker`` now merges the configuration-valued overrides
(``lib_llm_metadata.CONFIG_OVERRIDE_KEYS``) over the config file and lists them
under ``configuration.cli_overrides``. These tests gate three things:

1. an override changes the configuration fingerprint;
2. the same override twice does not change it (the fingerprint is a function
   of the effective configuration, not of how it was reached);
3. a run with no overrides writes exactly the key set it always wrote.

No API calls are made and no file outside ``tmp_path`` is written.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_llm_metadata import (  # noqa: E402
    CLEANUP_GATE_FIELDS,
    CONFIG_OVERRIDE_KEYS,
    LLMMetadataTracker,
    compare_gate_fields,
    configuration_fingerprint,
)

pytestmark = pytest.mark.tier1

#: A verifier config as the repository stores them, trimmed to the fields the
#: gate compares.
BASE_CONFIG: dict[str, Any] = {
    "version": "verify_adversarial-text_v2",
    "model": "gemini-3-flash",
    "instruction_file": "verify_adversarial_v2.md",
    "temperature": 0.0,
    "max_output_tokens": 8192,
    "thinking_level": "high",
    "tile_size": 384,
}


def _configuration(
    overrides: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """The ``configuration`` block a run with these overrides would record."""
    tracker = LLMMetadataTracker(
        config=dict(config if config is not None else BASE_CONFIG),
        system_instruction="# verifier instructions\n",
        script_name="test",
        script_version="0.0.0",
        cli_overrides=overrides,
    )
    return tracker.finalise()["configuration"]


class TestEffectiveConfiguration:
    """The recorded block is the config file merged with the command line."""

    def test_a_temperature_override_is_recorded(self) -> None:
        """``configuration.temperature`` is the value the API was given."""
        block = _configuration({"temperature": 0.7})
        assert block["temperature"] == 0.7
        assert block["full_config_snapshot"]["temperature"] == 0.7

    def test_the_overrides_are_listed_separately(self) -> None:
        """``cli_overrides`` keeps the file and the command line legible."""
        block = _configuration({"temperature": 0.7})
        assert block["cli_overrides"] == {"temperature": 0.7}

    def test_none_valued_overrides_are_ignored(self) -> None:
        """An unused flag must not look like an override of its default."""
        block = _configuration({"temperature": None, "thinking_level": None})
        assert "cli_overrides" not in block
        assert block["temperature"] == 0.0

    def test_non_configuration_overrides_are_not_merged(self) -> None:
        """``--service-tier`` and friends are not configuration fields."""
        block = _configuration({
            "service_tier": "flex", "iterations": 5, "safe_mode_tokens": 2048,
        })
        assert "cli_overrides" not in block
        assert block["max_output_tokens"] == 8192

    def test_every_merged_key_is_a_gate_field(self) -> None:
        """An override that cannot block is an override the gate cannot see."""
        assert set(CONFIG_OVERRIDE_KEYS) <= set(CLEANUP_GATE_FIELDS)

    def test_a_run_without_overrides_records_the_same_keys_as_before(
        self,
    ) -> None:
        """Regression: no override, no new key, byte-identical metadata."""
        block = _configuration(None)
        assert "cli_overrides" not in block
        assert block == _configuration({})


class TestGateFingerprint:
    """The gate must refuse a changed temperature and allow an unchanged one."""

    def test_an_override_changes_the_fingerprint(self) -> None:
        """A main pass at T=0.0 and a cleanup at T=0.7 must differ."""
        main = configuration_fingerprint(_configuration(None))
        cleanup = configuration_fingerprint(_configuration({"temperature": 0.7}))
        assert main != cleanup
        assert "temperature" in compare_gate_fields(main, cleanup)

    def test_the_same_override_twice_does_not(self) -> None:
        """Two passes under the same override compare equal on gate fields."""
        first = configuration_fingerprint(_configuration({"temperature": 0.7}))
        second = configuration_fingerprint(_configuration({"temperature": 0.7}))
        assert compare_gate_fields(first, second) == {}

    def test_an_override_to_the_config_value_is_not_a_change(self) -> None:
        """Passing --temperature 0.0 over a T=0.0 config changes nothing."""
        main = configuration_fingerprint(_configuration(None))
        same = configuration_fingerprint(_configuration({"temperature": 0.0}))
        assert compare_gate_fields(main, same) == {}

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("temperature", 1.0),
            ("max_output_tokens", 2048),
            ("thinking_level", "minimal"),
        ],
    )
    def test_each_configuration_valued_override_blocks(
        self, field: str, value: Any,
    ) -> None:
        """Every key in CONFIG_OVERRIDE_KEYS is visible to the gate."""
        main = configuration_fingerprint(_configuration(None))
        changed = configuration_fingerprint(_configuration({field: value}))
        assert field in compare_gate_fields(main, changed)
