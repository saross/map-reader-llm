"""Tier 1 unit tests for scripts.lib_hypothesis_requirements.

Verifies the hypothesis requirements table, no-op rule table, validation
logic, diff logic, and report formatting. No API calls, no large files.

Motivated by the 2026-04-14 Obs 235 retraction — see
``docs/notes/reflections/2026-04-14-h10-h12-config-intent-retrospective.md``.
"""

from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

# Make scripts/ importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from lib_hypothesis_requirements import (  # noqa: E402
    DIFFERS_FROM_BASE,
    HYPOTHESIS_REQUIREMENTS,
    NO_OP_RULES,
    ConfigDiffEntry,
    HypothesisRequirement,
    NoOpRule,
    ValidationFinding,
    diff_configs,
    format_validation_report,
    validate_config_against_hypothesis,
)


# ----------------------------------------------------------------------------
# HYPOTHESIS_REQUIREMENTS table structural checks
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestRequirementsTable:
    """The hand-authored requirements table must be internally consistent."""

    def test_table_is_non_empty(self):
        assert len(HYPOTHESIS_REQUIREMENTS) > 0

    def test_every_entry_is_well_formed(self):
        for key, req in HYPOTHESIS_REQUIREMENTS.items():
            assert isinstance(req, HypothesisRequirement)
            assert req.hypothesis_id == key, (
                f"Key {key!r} does not match hypothesis_id {req.hypothesis_id!r}"
            )
            assert req.description, f"Empty description for {key}"
            assert isinstance(req.required_fields, dict)

    def test_critical_hypotheses_are_present(self):
        """H8, H10, H12 — the primary targets of the retrospective."""
        for hid in ("H8", "H10", "H12"):
            assert hid in HYPOTHESIS_REQUIREMENTS, f"{hid} missing"
            req = HYPOTHESIS_REQUIREMENTS[hid]
            assert req.required_fields.get("include_example_images") is True, (
                f"{hid} must require include_example_images=True"
            )
            assert req.rationale, f"{hid} has empty rationale"

    def test_h5_uses_differs_from_base_sentinel(self):
        req = HYPOTHESIS_REQUIREMENTS["H5"]
        assert req.required_fields["instruction_file"] is DIFFERS_FROM_BASE

    def test_h7_uses_differs_from_base_sentinel(self):
        req = HYPOTHESIS_REQUIREMENTS["H7"]
        assert req.required_fields["temperature"] is DIFFERS_FROM_BASE


@pytest.mark.tier1
class TestNoOpRulesTable:
    """The NO_OP_RULES table must be well-formed."""

    def test_table_is_non_empty(self):
        assert len(NO_OP_RULES) > 0

    def test_every_rule_is_well_formed(self):
        for rule in NO_OP_RULES:
            assert isinstance(rule, NoOpRule)
            assert rule.changed_field
            assert rule.gated_by_field
            assert rule.explanation

    def test_examples_gated_by_modality_rule_exists(self):
        """The primary rule motivated by the retrospective."""
        matches = [
            r for r in NO_OP_RULES
            if r.changed_field == "examples"
            and r.gated_by_field == "include_example_images"
            and r.gated_value is False
        ]
        assert len(matches) == 1, (
            "Expected exactly one rule: examples gated by "
            "include_example_images=False"
        )


# ----------------------------------------------------------------------------
# validate_config_against_hypothesis
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestValidation:
    """Per-hypothesis validation cases for the retracted failure mode."""

    def test_h10_requires_image_modality_fails_on_text_only(self):
        config = {
            "version": "detect_brief-text_pool_160_hp4hn4",
            "include_example_images": False,
            "temperature": 0.7,
        }
        findings = validate_config_against_hypothesis(config, "H10")
        assert len(findings) == 1
        assert findings[0].field == "include_example_images"
        assert findings[0].actual is False
        assert findings[0].expected is True

    def test_h12_requires_image_modality_fails_on_text_only(self):
        config = {"include_example_images": False}
        findings = validate_config_against_hypothesis(config, "H12")
        assert len(findings) == 1
        assert findings[0].field == "include_example_images"

    def test_h8_requires_image_modality_fails_on_text_only(self):
        config = {"include_example_images": False}
        findings = validate_config_against_hypothesis(config, "H8")
        assert len(findings) == 1

    def test_h12_passes_on_image_config(self):
        config = {"include_example_images": True}
        findings = validate_config_against_hypothesis(config, "H12")
        assert findings == []

    def test_h3_has_no_entry_validator_passes(self):
        """Unknown hypothesis IDs return empty list (permissive default)."""
        findings = validate_config_against_hypothesis({}, "H3")
        assert findings == []

    def test_unknown_hypothesis_passes(self):
        findings = validate_config_against_hypothesis(
            {"temperature": 0.0}, "H99",
        )
        assert findings == []

    def test_h5_differs_from_base_detects_sameness(self):
        base = {"instruction_file": "detect_brief-text.md"}
        variant = {"instruction_file": "detect_brief-text.md"}
        findings = validate_config_against_hypothesis(
            variant, "H5", base_config=base,
        )
        assert len(findings) == 1
        assert findings[0].field == "instruction_file"

    def test_h5_differs_from_base_passes_when_different(self):
        base = {"instruction_file": "detect_brief-text.md"}
        variant = {"instruction_file": "detect_brief-text_verbose.md"}
        findings = validate_config_against_hypothesis(
            variant, "H5", base_config=base,
        )
        assert findings == []

    def test_h7_differs_from_base_detects_same_temperature(self):
        base = {"temperature": 0.7}
        variant = {"temperature": 0.7}
        findings = validate_config_against_hypothesis(
            variant, "H7", base_config=base,
        )
        assert len(findings) == 1

    def test_differs_from_base_without_base_produces_finding(self):
        variant = {"instruction_file": "any.md"}
        findings = validate_config_against_hypothesis(
            variant, "H5", base_config=None,
        )
        # Requires a base but none was provided — surface this as a finding
        assert len(findings) == 1
        assert "no base provided" in str(findings[0].expected).lower()


# ----------------------------------------------------------------------------
# format_validation_report
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestValidationReport:
    """The refusal report must be structured and informative."""

    def test_empty_findings_returns_ok_string(self):
        out = format_validation_report([], "H12")
        assert "OK" in out

    def test_h12_text_only_report_contains_key_elements(self):
        findings = [
            ValidationFinding(
                hypothesis_id="H12",
                field="include_example_images",
                actual=False,
                expected=True,
                suggested_fix="Set include_example_images: true in the variant.",
            )
        ]
        out = format_validation_report(findings, "H12")
        assert "REFUSED" in out
        assert "H12" in out
        assert "include_example_images" in out
        assert "False" in out
        assert "True" in out
        assert "suggested" in out.lower()
        assert "retrospective" in out.lower()

    def test_report_includes_rationale_for_known_hypothesis(self):
        findings = [
            ValidationFinding(
                hypothesis_id="H12",
                field="include_example_images",
                actual=False,
                expected=True,
                suggested_fix="x",
            )
        ]
        out = format_validation_report(findings, "H12")
        assert HYPOTHESIS_REQUIREMENTS["H12"].rationale in out


# ----------------------------------------------------------------------------
# diff_configs
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestDiffConfigs:
    """Per-field diff with no-op rule application."""

    def test_identical_configs_produce_empty_diff(self):
        config = {
            "version": "x",
            "temperature": 0.7,
            "thinking_level": "high",
        }
        entries = diff_configs(config, config)
        assert entries == []

    def test_temperature_change_is_not_no_op(self):
        base = {"temperature": 0.0, "include_example_images": False}
        variant = {"temperature": 0.7, "include_example_images": False}
        entries = diff_configs(variant, base)
        assert len(entries) == 1
        assert entries[0].field == "temperature"
        assert entries[0].is_no_op is False
        assert entries[0].no_op_reason is None

    def test_examples_change_with_text_only_is_no_op(self):
        base = {
            "include_example_images": False,
            "examples": [{"path": "a"}, {"path": "b"}],
        }
        variant = {
            "include_example_images": False,
            "examples": [{"path": "c"}, {"path": "d"}, {"path": "e"}],
        }
        entries = diff_configs(variant, base)
        assert len(entries) == 1
        assert entries[0].field == "examples"
        assert entries[0].is_no_op is True
        assert "not transmitted" in entries[0].no_op_reason

    def test_examples_change_with_image_mode_is_not_no_op(self):
        base = {
            "include_example_images": True,
            "examples": [{"path": "a"}],
        }
        variant = {
            "include_example_images": True,
            "examples": [{"path": "b"}, {"path": "c"}],
        }
        entries = diff_configs(variant, base)
        assert len(entries) == 1
        assert entries[0].field == "examples"
        assert entries[0].is_no_op is False

    def test_default_ignore_keys_skipped(self):
        base = {
            "version": "v1",
            "description": "old",
            "pool_source": "a",
            "temperature": 0.0,
        }
        variant = {
            "version": "v2",
            "description": "new",
            "pool_source": "b",
            "temperature": 0.0,
        }
        entries = diff_configs(variant, base)
        assert entries == []  # Only ignored fields changed

    def test_examples_summary_shows_counts(self):
        base = {
            "include_example_images": True,
            "examples": [{"path": f"e{i}"} for i in range(10)],
        }
        variant = {
            "include_example_images": True,
            "examples": [{"path": f"e{i}"} for i in range(17)],
        }
        entries = diff_configs(variant, base)
        assert len(entries) == 1
        assert "10" in entries[0].base_value
        assert "17" in entries[0].variant_value

    def test_h10_retrospective_reproducer(self):
        """End-to-end: the exact failure the retrospective describes.

        A config that varies examples and library_hash while
        include_example_images is false must produce no-op entries for both.
        """
        base = {
            "version": "detect_brief-text",
            "include_example_images": False,
            "temperature": 1.0,
            "library_hash": "8580ecb2",
            "examples": [{"path": f"e{i}"} for i in range(17)],
            "pool_source": "outputs/old-pool",
        }
        variant = {
            "version": "detect_brief-text_pool_160_hp4hn4",
            "include_example_images": False,
            "temperature": 1.0,
            "library_hash": "a168f1cc",
            "examples": [{"path": f"p{i}"} for i in range(17)],
            "pool_source": "outputs/h10/example-pools/pool_160_hp4hn4",
        }
        entries = diff_configs(variant, base)
        fields = {e.field for e in entries}
        # Expected: library_hash, examples (pool_source is in default
        # ignore_keys, version/description are ignored)
        assert "library_hash" in fields
        assert "examples" in fields
        # All flagged no-ops are the correct ones
        no_ops = {e.field for e in entries if e.is_no_op}
        assert no_ops == {"library_hash", "examples"}


# ----------------------------------------------------------------------------
# ConfigDiffEntry dataclass checks
# ----------------------------------------------------------------------------


@pytest.mark.tier1
class TestDataclassImmutability:
    """Frozen dataclasses prevent accidental mutation of the tables.

    Uses ``FrozenInstanceError`` specifically rather than a bare
    ``Exception`` so a future change that swaps the dataclass for a
    non-frozen one would fail these tests loudly instead of silently
    catching an unrelated error.
    """

    def test_hypothesis_requirement_is_frozen(self):
        req = HypothesisRequirement(
            hypothesis_id="HX",
            description="test",
        )
        with pytest.raises(FrozenInstanceError):
            req.hypothesis_id = "HY"  # type: ignore[misc]

    def test_no_op_rule_is_frozen(self):
        rule = NoOpRule(
            changed_field="a",
            gated_by_field="b",
            gated_value=False,
            explanation="c",
        )
        with pytest.raises(FrozenInstanceError):
            rule.changed_field = "x"  # type: ignore[misc]

    def test_config_diff_entry_is_frozen(self):
        entry = ConfigDiffEntry(
            field="a",
            base_value=1,
            variant_value=2,
            is_no_op=False,
            no_op_reason=None,
        )
        with pytest.raises(FrozenInstanceError):
            entry.field = "x"  # type: ignore[misc]

    def test_validation_finding_is_frozen(self):
        finding = ValidationFinding(
            hypothesis_id="H12",
            field="include_example_images",
            actual=False,
            expected=True,
            suggested_fix="Set to True.",
        )
        with pytest.raises(FrozenInstanceError):
            finding.field = "temperature"  # type: ignore[misc]
