#!/usr/bin/env python3
"""
Launch-time configuration validation: an inert field is an error, not a no-op.

Why this module exists
----------------------
A prompt configuration can carry a field that, under its other settings,
never reaches the model. The pipeline then runs without complaint, the
configuration file says one thing, and the request says another. That is the
text-track transmission gap (erratum E90; tracker
``planning/text-track-transmission-2026-10-05.md`` § W6.2): every text-only
proposer configuration lists an exemplar library in ``examples``, and sets
``include_example_images: false``. With that flag false the detection
pipeline transmits NOTHING from the library — not the images and not their
labels:

- real-time: ``scripts/4_detect_mounds_batch.py`` ``detect_mounds_versioned``
  skips the whole example loop ("Text-only modality: skipping example
  images");
- batch: ``scripts/lib_batch_api.py`` ``_build_reference_parts`` returns an
  empty list;
- in-batch retries: ``scripts/lib_batch_api.py`` ``_retry_tile_sync`` skips
  the loop the same way.

So a reader of ``detect_brief-text.json`` sees seventeen exemplars, and the
model saw none. The rule below turns that silence into a launch error.

What it checks
--------------
:data:`INERT_FIELD_RULES` is a table of ``(field, silencing setting, test)``
rules. The first (and so far only) rule is the E90 case: a non-empty
``examples`` list together with ``include_example_images`` explicitly false.
A missing ``include_example_images`` is NOT a finding: the pipeline defaults
it to true (``4_detect_mounds_batch.py``), so the examples are sent.

Further rules belong in the same table (a natural next one: an example
ordering override under the same flag, which is inert for the same reason).

How to use it
-------------
Call :func:`validate_no_inert_fields` on the EFFECTIVE configuration (after
any command-line overrides) before any API client is created::

    from scripts.lib_config_validation import validate_no_inert_fields
    validate_no_inert_fields(config, source=str(config_path),
                             allow_inert_fields=args.allow_inert_fields)

It raises :class:`InertConfigurationError`, naming each inert field and the
setting that silences it. The entry points (``4_detect_mounds_batch.py`` and
``run_phase2.py``) expose ``--allow-inert-fields`` for HISTORICAL
REPRODUCTION runs, which must re-send exactly what the original runs sent
(i.e. nothing from the library); with it the findings are logged loudly as
warnings and the launch proceeds. The configuration itself is not changed,
so a reproduction's recorded ``configuration`` block stays byte-comparable
with the original's.

Examples
--------
    >>> cfg = {"version": "t", "include_example_images": False,
    ...        "examples": [{"path": "a.png", "label": "Positive"}]}
    >>> [f.field for f in find_inert_fields(cfg)]
    ['examples']
    >>> find_inert_fields({"examples": [{"path": "a.png"}]})
    []
"""

from __future__ import annotations

import dataclasses
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

#: The command-line switch that downgrades the error to a loud warning.
OPT_OUT_FLAG = "--allow-inert-fields"


@dataclasses.dataclass(frozen=True)
class InertField:
    """One configuration field that cannot reach the model.

    Attributes:
        field: The inert field's key (e.g. ``"examples"``).
        silenced_by: The setting that silences it, as it appears in the
            configuration (e.g. ``"include_example_images: false"``).
        explanation: Why the field cannot reach the model, with the count
            or value that makes it non-trivial.
    """

    field: str
    silenced_by: str
    explanation: str

    def message(self) -> str:
        """A one-line, human-readable statement of the finding.

        Returns:
            ``"<field> is inert under <setting>: <explanation>"``.

        Examples:
            >>> InertField("examples", "include_example_images: false",
            ...            "3 examples, none sent").message()
            'examples is inert under include_example_images: false: 3 examples, none sent'
        """
        return f"{self.field} is inert under {self.silenced_by}: {self.explanation}"


@dataclasses.dataclass(frozen=True)
class InertFieldRule:
    """A rule naming a field that a setting silences.

    Attributes:
        field: The field the rule inspects.
        silenced_by: The silencing setting, for the message.
        check: Returns an explanation when the rule fires on a configuration,
            or None when it does not.
    """

    field: str
    silenced_by: str
    check: Callable[[dict[str, Any]], str | None]


def _examples_without_images(config: dict[str, Any]) -> str | None:
    """Fire when an example list is configured but example images are off.

    ``include_example_images`` must be explicitly false: absent, the pipeline
    defaults it to true and the examples are sent.

    Args:
        config: An effective prompt configuration.

    Returns:
        An explanation naming the example count, or None.

    Examples:
        >>> _examples_without_images({"include_example_images": False,
        ...                           "examples": [{}, {}]}) is not None
        True
        >>> _examples_without_images({"include_example_images": False,
        ...                           "examples": []}) is None
        True
    """
    examples = config.get("examples") or []
    if config.get("include_example_images", True) is False and examples:
        return (f"{len(examples)} example(s) are configured, but with example images "
                "off the pipeline transmits nothing from the library — neither the "
                "images nor their labels (E90, the text-track transmission gap)")
    return None


#: Every rule checked at launch. Extend here; each rule names its field and
#: the setting that silences it, so the error message can name both.
INERT_FIELD_RULES: tuple[InertFieldRule, ...] = (
    InertFieldRule(
        field="examples",
        silenced_by="include_example_images: false",
        check=_examples_without_images,
    ),
)


class InertConfigurationError(ValueError):
    """A configuration carries fields that cannot reach the model.

    Attributes:
        findings: The inert fields found.
        source: Where the configuration came from (a path or a name).
    """

    def __init__(self, findings: list[InertField], source: str) -> None:
        """Build the error message from the findings.

        Args:
            findings: The inert fields found (at least one).
            source: Where the configuration came from.
        """
        self.findings = findings
        self.source = source
        lines = [f"Configuration {source} carries field(s) that cannot reach the model:"]
        lines += [f"  - {f.message()}" for f in findings]
        lines.append(
            "Remove the inert field(s), or change the setting that silences them. "
            f"To reproduce a historical run exactly as it was sent, pass {OPT_OUT_FLAG} "
            "(logged as a warning).")
        super().__init__("\n".join(lines))


def find_inert_fields(config: dict[str, Any]) -> list[InertField]:
    """Apply every rule in :data:`INERT_FIELD_RULES` to a configuration.

    Args:
        config: The EFFECTIVE prompt configuration (after any overrides).

    Returns:
        One :class:`InertField` per rule that fired, in rule order.
    """
    findings: list[InertField] = []
    for rule in INERT_FIELD_RULES:
        explanation = rule.check(config)
        if explanation is not None:
            findings.append(InertField(rule.field, rule.silenced_by, explanation))
    return findings


def validate_no_inert_fields(
    config: dict[str, Any],
    source: str = "configuration",
    allow_inert_fields: bool = False,
    warn: Callable[[str], None] | None = print,
) -> list[InertField]:
    """Refuse a configuration with inert fields, unless explicitly allowed.

    Args:
        config: The EFFECTIVE prompt configuration (after any overrides).
        source: Where it came from, for the message (a path or a name).
        allow_inert_fields: The historical-reproduction opt-out. When true
            the findings are logged as warnings (and printed, through
            ``warn``) and returned instead of raised.
        warn: Where the opt-out's banner is printed besides the log
            (``print`` by default, so it shows in a run's own log); None
            logs only.

    Returns:
        The findings (empty when the configuration is clean).

    Raises:
        InertConfigurationError: Any rule fired and ``allow_inert_fields``
            is false.

    Examples:
        >>> validate_no_inert_fields({"examples": [{}]})
        []
        >>> bad = {"include_example_images": False, "examples": [{}]}
        >>> len(validate_no_inert_fields(bad, allow_inert_fields=True, warn=None))
        1
    """
    findings = find_inert_fields(config)
    if not findings:
        return findings
    if not allow_inert_fields:
        raise InertConfigurationError(findings, source)
    banner = (f"WARNING: {OPT_OUT_FLAG} — launching {source} with "
              f"{len(findings)} inert field(s) (historical reproduction):")
    logger.warning(banner)
    for f in findings:
        logger.warning("  %s", f.message())
    if warn is not None:
        rule = "!" * 70
        warn(rule)
        warn(banner)
        for f in findings:
            warn(f"  - {f.message()}")
        warn(rule)
    return findings
