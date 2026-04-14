#!/usr/bin/env python3
# ============================================================================
# lib_hypothesis_requirements.py
# ----------------------------------------------------------------------------
# Hypothesis-to-config-field requirements table, no-op rule table, and the
# helpers that validate a generated config against a target preregistered
# hypothesis and diff a variant config against its base.
#
# Motivated by the 2026-04-14 Obs 235 retraction: the H10/H12 pool sweep was
# run with a text-only proposer (`include_example_images: false`), so the
# pool-specific few-shot library never reached the API. ~$33 wasted on a
# tautological experiment. This module implements the structural check that
# would have prevented the launch.
#
# Full retrospective:
#     docs/notes/reflections/2026-04-14-h10-h12-config-intent-retrospective.md
#
# Public surface:
#     HYPOTHESIS_REQUIREMENTS   — dict[str, HypothesisRequirement]
#     NO_OP_RULES               — tuple[NoOpRule, ...]
#     DIFFERS_FROM_BASE         — sentinel for "must not equal the base value"
#     validate_config_against_hypothesis(config, hypothesis_id, base=None)
#     format_validation_report(findings, hypothesis_id)
#     diff_configs(variant, base, ignore_keys=...)
#
# Intended consumers:
#     scripts/generate_prompt_configs.py  — refuses to emit a misaligned
#                                           config with an explanatory report
#     scripts/lib_experiment_intent.py    — uses diff_configs + NO_OP_RULES at
#                                           launch time to warn the user
#
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ----------------------------------------------------------------------------
# Sentinel — "must differ from the corresponding field in the base config"
# ----------------------------------------------------------------------------


class _DiffersFromBase:
    """Marker value used in ``HypothesisRequirement.required_fields``.

    When a required field is set to ``DIFFERS_FROM_BASE`` instead of a
    literal, the validator checks that the variant config's value for the
    field does not equal the base config's value. Used for hypotheses like
    H5 (varies instruction file) and H7 (varies temperature) where the
    required manipulation is "something changed" rather than "a specific
    value is set".
    """

    _instance: "_DiffersFromBase | None" = None

    def __new__(cls) -> "_DiffersFromBase":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "<DIFFERS_FROM_BASE>"


DIFFERS_FROM_BASE = _DiffersFromBase()


# ----------------------------------------------------------------------------
# Dataclasses
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class HypothesisRequirement:
    """A preregistered hypothesis's config-field requirements.

    Attributes:
        hypothesis_id: Short identifier, e.g. ``"H12"``.
        description: One-sentence description pulled from the preregistration.
        required_fields: Mapping of config field names to required values.
            Values are either literals (``True``, numbers, strings) or the
            ``DIFFERS_FROM_BASE`` sentinel meaning "must not equal the base".
        varied_field: Canonical name of the factor being varied (for the
            experiment-intent report). ``None`` if the hypothesis does not
            identify a single varied field.
        rationale: Human-readable explanation used in the refusal report.
    """

    hypothesis_id: str
    description: str
    required_fields: dict[str, Any] = field(default_factory=dict)
    varied_field: str | None = None
    rationale: str = ""


@dataclass(frozen=True)
class NoOpRule:
    """Rule identifying when a changed config field has no effect on the API.

    A no-op rule says: "when ``gated_by_field`` has value ``gated_value`` in
    the variant config, a change to ``changed_field`` does not reach the
    API and is therefore a no-op". Used at launch time by
    ``lib_experiment_intent.run_launch_checks`` to flag misaligned diffs.

    Attributes:
        changed_field: The config field whose change is potentially a no-op.
        gated_by_field: The config field that gates transmission.
        gated_value: The value of ``gated_by_field`` that makes the change a
            no-op.
        explanation: Reason shown in the diff report (one sentence).
    """

    changed_field: str
    gated_by_field: str
    gated_value: Any
    explanation: str


@dataclass(frozen=True)
class ValidationFinding:
    """One validation failure detected by ``validate_config_against_hypothesis``."""

    hypothesis_id: str
    field: str
    actual: Any
    expected: Any
    suggested_fix: str


@dataclass(frozen=True)
class ConfigDiffEntry:
    """One field-level diff entry produced by ``diff_configs``.

    Attributes:
        field: Config field name.
        base_value: Value in the base config (or ``"(absent)"`` sentinel).
        variant_value: Value in the variant config.
        is_no_op: ``True`` when a ``NoOpRule`` matches the (field, gate)
            combination in the variant config, meaning the change will not
            reach the API payload.
        no_op_reason: Explanation from the matched rule, or ``None``.
    """

    field: str
    base_value: Any
    variant_value: Any
    is_no_op: bool
    no_op_reason: str | None


_ABSENT = "(absent)"


# ----------------------------------------------------------------------------
# Pipeline defaults
# ----------------------------------------------------------------------------
#
# Some config fields have implicit defaults in the detection pipeline code
# that must be mirrored here so the validator sees the same "effective
# config" the pipeline will send to the API. For example:
#
#     scripts/4_detect_mounds_batch.py:800
#         include_example_images = config.get("include_example_images", True)
#
# When the validator checks a config that omits ``include_example_images``,
# it should treat the value as ``True`` (the pipeline default) rather than
# absent. The table below is the authoritative list of such defaults.


_PIPELINE_DEFAULTS: dict[str, Any] = {
    "include_example_images": True,
}


def _apply_pipeline_defaults(config: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy of ``config`` with pipeline defaults filled in.

    Fields already present in the config are left untouched. Only fields
    in ``_PIPELINE_DEFAULTS`` that are missing from the config are added.
    """
    out = dict(config)
    for field_name, default_value in _PIPELINE_DEFAULTS.items():
        if field_name not in out:
            out[field_name] = default_value
    return out


# ----------------------------------------------------------------------------
# Hypothesis requirements table
# ----------------------------------------------------------------------------
#
# Intentionally sparse. Only hypotheses with modality-transmission or
# similar concrete field requirements have entries. Unknown hypothesis IDs
# return an empty finding list — a permissive default that does not block
# legitimate workflows.
#
# Descriptions are hand-authored pulls from
# ``docs/methodology/preregistration/hypothesis-tracking.md``. The file is
# narrative markdown and cannot be parsed reliably.


HYPOTHESIS_REQUIREMENTS: dict[str, HypothesisRequirement] = {
    "H1": HypothesisRequirement(
        hypothesis_id="H1",
        description=(
            "Modality and elaboration level — tests how text presence and "
            "detail level affect detection performance."
        ),
        required_fields={},
        varied_field="include_example_images",
        rationale=(
            "H1 legitimately varies modality across conditions (image-only, "
            "brief-text, brief-text-image, etc.). No field assertion is "
            "required; this entry exists for completeness."
        ),
    ),
    "H5": HypothesisRequirement(
        hypothesis_id="H5",
        description=(
            "Negative text treatment — varies the instruction file to test "
            "different levels of negative-example commentary."
        ),
        required_fields={"instruction_file": DIFFERS_FROM_BASE},
        varied_field="instruction_file",
        rationale=(
            "H5 requires a distinct instruction file per condition; cloning "
            "a base without overriding the instruction produces no "
            "manipulation."
        ),
    ),
    "H7": HypothesisRequirement(
        hypothesis_id="H7",
        description=(
            "Temperature sweep — varies sampling temperature across "
            "preregistered levels (0.0, 0.3, 0.7, 1.0, 1.3)."
        ),
        required_fields={"temperature": DIFFERS_FROM_BASE},
        varied_field="temperature",
        rationale=(
            "H7 requires a distinct temperature per condition; cloning a "
            "base without overriding the temperature produces no "
            "manipulation."
        ),
    ),
    "H8": HypothesisRequirement(
        hypothesis_id="H8",
        description=(
            "Library composition and scaling — tests whether the few-shot "
            "library's composition affects detection performance."
        ),
        required_fields={"include_example_images": True},
        varied_field="examples",
        rationale=(
            "H8 tests the visual few-shot library. The library reaches the "
            "API only when `include_example_images` is true. A text-only "
            "base would leave the library-composition factor "
            "untransmitted, as per Obs 235."
        ),
    ),
    "H10": HypothesisRequirement(
        hypothesis_id="H10",
        description=(
            "Training pool size — tests whether expanding the hard-example "
            "pool from which the few-shot library is drawn improves "
            "detection performance."
        ),
        required_fields={"include_example_images": True},
        varied_field="examples",
        rationale=(
            "H10 varies the pool from which the image library is mined. "
            "The pool affects the API only when `include_example_images` "
            "is true; a text-only base makes the pool-size factor "
            "unobservable, as per Obs 235."
        ),
    ),
    "H12": HypothesisRequirement(
        hypothesis_id="H12",
        description=(
            "Hard-positive to hard-negative ratio — tests whether the "
            "HP:HN balance in the few-shot library affects detection "
            "performance."
        ),
        required_fields={"include_example_images": True},
        varied_field="examples",
        rationale=(
            "H12 varies the HP:HN ratio in the image library. The ratio "
            "reaches the API only when `include_example_images` is true; "
            "a text-only base would make the ratio manipulation "
            "unobservable, as per Obs 235."
        ),
    ),
}


# ----------------------------------------------------------------------------
# No-op rule table
# ----------------------------------------------------------------------------
#
# Applied by ``diff_configs`` after the raw per-field diff is computed. A
# rule whose ``gated_by_field`` has value ``gated_value`` in the variant
# config flags the corresponding ``changed_field`` diff entry as a no-op.


NO_OP_RULES: tuple[NoOpRule, ...] = (
    NoOpRule(
        changed_field="examples",
        gated_by_field="include_example_images",
        gated_value=False,
        explanation=(
            "example images are not transmitted when "
            "include_example_images is false"
        ),
    ),
    NoOpRule(
        changed_field="pool_source",
        gated_by_field="include_example_images",
        gated_value=False,
        explanation=(
            "pool source affects examples only, which are not transmitted "
            "in text-only mode"
        ),
    ),
    NoOpRule(
        changed_field="library_hash",
        gated_by_field="include_example_images",
        gated_value=False,
        explanation=(
            "library hash records provenance of examples, which are not "
            "transmitted in text-only mode"
        ),
    ),
)


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------


def validate_config_against_hypothesis(
    config: dict[str, Any],
    hypothesis_id: str,
    base_config: dict[str, Any] | None = None,
) -> list[ValidationFinding]:
    """Check a config against a hypothesis's required fields.

    Returns an empty list on pass (including when the hypothesis has no
    registered requirements). Returns a non-empty list of findings on
    failure.

    Args:
        config: The variant config to validate.
        hypothesis_id: The target hypothesis, e.g. ``"H12"``.
        base_config: The base config, required only if the hypothesis's
            requirements include the ``DIFFERS_FROM_BASE`` sentinel.

    Returns:
        A list of ``ValidationFinding`` objects describing each mismatch.
    """
    requirement = HYPOTHESIS_REQUIREMENTS.get(hypothesis_id)
    if requirement is None:
        return []

    # Apply pipeline defaults so the validator sees the effective config
    # the detection pipeline will actually send to the API.
    effective_config = _apply_pipeline_defaults(config)
    effective_base = (
        _apply_pipeline_defaults(base_config)
        if base_config is not None else None
    )

    findings: list[ValidationFinding] = []
    for field_name, expected in requirement.required_fields.items():
        actual = effective_config.get(field_name, _ABSENT)

        if isinstance(expected, _DiffersFromBase):
            if effective_base is None:
                findings.append(ValidationFinding(
                    hypothesis_id=hypothesis_id,
                    field=field_name,
                    actual=actual,
                    expected="(must differ from base, but no base provided)",
                    suggested_fix=(
                        f"Pass a base_config when validating {hypothesis_id}, "
                        f"since it uses the DIFFERS_FROM_BASE sentinel on "
                        f"`{field_name}`."
                    ),
                ))
                continue
            base_value = effective_base.get(field_name, _ABSENT)
            if actual == base_value:
                findings.append(ValidationFinding(
                    hypothesis_id=hypothesis_id,
                    field=field_name,
                    actual=actual,
                    expected=f"(any value != base's {base_value!r})",
                    suggested_fix=(
                        f"Override `{field_name}` in the variant config to "
                        f"something other than the base value."
                    ),
                ))
            continue

        if actual != expected:
            findings.append(ValidationFinding(
                hypothesis_id=hypothesis_id,
                field=field_name,
                actual=actual,
                expected=expected,
                suggested_fix=(
                    f"Set `{field_name}: {expected!r}` in the variant config, "
                    f"or use a base config that already has this value (e.g. "
                    f"`detect_brief-text-image.json` for "
                    f"`include_example_images: true`)."
                ),
            ))

    return findings


def format_validation_report(
    findings: list[ValidationFinding],
    hypothesis_id: str,
) -> str:
    """Render a structured refusal report for a list of validation findings.

    The report names the hypothesis, lists each misaligned field with its
    actual and expected values, and includes the rationale from the
    hypothesis's requirement entry (if any).

    Args:
        findings: The non-empty list of findings from
            ``validate_config_against_hypothesis``.
        hypothesis_id: The target hypothesis, used for the header and
            rationale lookup.

    Returns:
        A multi-line string suitable for printing to stderr or stdout.
    """
    if not findings:
        return f"[validate] {hypothesis_id}: OK (no findings)"

    lines: list[str] = []
    lines.append("=" * 78)
    lines.append(
        f"REFUSED: config is inconsistent with preregistered hypothesis "
        f"{hypothesis_id}"
    )
    lines.append("=" * 78)

    requirement = HYPOTHESIS_REQUIREMENTS.get(hypothesis_id)
    if requirement is not None:
        lines.append(f"Hypothesis: {requirement.description}")
        if requirement.rationale:
            lines.append("")
            lines.append("Rationale:")
            lines.append(f"  {requirement.rationale}")

    lines.append("")
    lines.append(f"Findings ({len(findings)}):")
    lines.append("")

    for i, finding in enumerate(findings, start=1):
        lines.append(f"  [{i}] field: `{finding.field}`")
        lines.append(f"      actual:      {finding.actual!r}")
        lines.append(f"      expected:    {finding.expected!r}")
        lines.append(f"      suggested:   {finding.suggested_fix}")
        lines.append("")

    lines.append(
        "See docs/notes/reflections/"
        "2026-04-14-h10-h12-config-intent-retrospective.md for context."
    )
    lines.append("=" * 78)

    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Config diff
# ----------------------------------------------------------------------------


DEFAULT_IGNORE_KEYS: frozenset[str] = frozenset({
    "version",
    "description",
    "pool_source",
    "base_config",
})


def _examples_summary(examples: Any) -> str:
    """Return a short summary of an examples list for diff display."""
    if examples in (None, _ABSENT):
        return _ABSENT
    if not isinstance(examples, list):
        return f"(non-list: {type(examples).__name__})"
    return f"{len(examples)} entries"


def _examples_differ(base_examples: Any, variant_examples: Any) -> bool:
    """Return True when the examples lists differ structurally."""
    if base_examples == variant_examples:
        return False
    return True


def _apply_no_op_rules(
    changed_field: str,
    variant_config: dict[str, Any],
) -> tuple[bool, str | None]:
    """Check whether a changed field is a no-op given the variant's gates.

    Returns ``(is_no_op, reason)``. First matching rule wins. Pipeline
    defaults are applied to the gate lookup so a rule gated by a field
    that relies on an implicit default still fires correctly.
    """
    effective = _apply_pipeline_defaults(variant_config)
    for rule in NO_OP_RULES:
        if rule.changed_field != changed_field:
            continue
        gate_value = effective.get(rule.gated_by_field, _ABSENT)
        if gate_value == rule.gated_value:
            return True, rule.explanation
    return False, None


def diff_configs(
    variant: dict[str, Any],
    base: dict[str, Any],
    ignore_keys: frozenset[str] = DEFAULT_IGNORE_KEYS,
) -> list[ConfigDiffEntry]:
    """Diff a variant config against its base config.

    Iterates the union of keys, skipping ``ignore_keys`` (plus ``examples``,
    which is summarised into a single synthetic entry rather than
    element-by-element). Each returned entry carries a ``is_no_op`` flag
    computed from the ``NO_OP_RULES`` table against the variant.

    Args:
        variant: The variant (child) config.
        base: The base (parent) config.
        ignore_keys: Field names to exclude from the raw diff. Defaults to
            ``DEFAULT_IGNORE_KEYS``. ``examples`` is always handled specially
            and is not in this set.

    Returns:
        A list of ``ConfigDiffEntry`` objects, one per differing field.
    """
    entries: list[ConfigDiffEntry] = []

    keys = (set(variant.keys()) | set(base.keys())) - ignore_keys - {"examples"}

    for key in sorted(keys):
        base_value = base.get(key, _ABSENT)
        variant_value = variant.get(key, _ABSENT)
        if base_value == variant_value:
            continue
        is_no_op, reason = _apply_no_op_rules(key, variant)
        entries.append(ConfigDiffEntry(
            field=key,
            base_value=base_value,
            variant_value=variant_value,
            is_no_op=is_no_op,
            no_op_reason=reason,
        ))

    # Synthetic entry for examples (element-wise diff is noisy)
    base_examples = base.get("examples", _ABSENT)
    variant_examples = variant.get("examples", _ABSENT)
    if _examples_differ(base_examples, variant_examples):
        is_no_op, reason = _apply_no_op_rules("examples", variant)
        entries.append(ConfigDiffEntry(
            field="examples",
            base_value=_examples_summary(base_examples),
            variant_value=_examples_summary(variant_examples),
            is_no_op=is_no_op,
            no_op_reason=reason,
        ))

    return entries
