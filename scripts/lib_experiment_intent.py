#!/usr/bin/env python3
# ============================================================================
# lib_experiment_intent.py
# ----------------------------------------------------------------------------
# Launch-time experiment-intent writer and config-diff guard.
#
# Implements Fixes #2 and #3 from the 2026-04-14 Obs 235 retrospective:
#
#   Fix #2 — write_experiment_intent(): before any API calls, write an
#            experiment_intent.md file to the experiment output directory
#            that records hypothesis, varied factor, transmission
#            mechanism, and verified modality values. Serves as
#            documentation and as a self-audit (a later reader can
#            compare the intent against the actual run.meta.json).
#
#   Fix #3 — run_launch_checks(): combined launch-time guard. Writes (or
#            verifies) the intent markdown, diffs the variant config
#            against its base, applies the NO_OP_RULES table from
#            lib_hypothesis_requirements, and prompts the user to confirm
#            if any of the changed fields would not reach the API.
#
# Consumed by scripts/4_detect_mounds_batch.py from both the realtime and
# batch dispatch paths.
#
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0
# ============================================================================

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------------
# Path setup — allow imports from scripts/
# ----------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lib_hypothesis_requirements import (  # noqa: E402
    HYPOTHESIS_REQUIREMENTS,
    ConfigDiffEntry,
    diff_configs,
)

logger = logging.getLogger(__name__)

_INTENT_FILENAME = "experiment_intent.md"

# Fields we cross-check when deciding whether a pre-existing
# experiment_intent.md is consistent with the current config.
_KEY_FIELDS_FOR_CONSISTENCY: tuple[str, ...] = (
    "version",
    "hypothesis",
    "include_example_images",
    "temperature",
    "thinking_level",
    "instruction_file",
    "model",
    "base_config",
)


# ============================================================================
# Experiment-intent markdown writer
# ============================================================================


def _get_git_commit() -> str:
    """Return short git commit hash, or ``"(unknown)"`` on failure."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=2,
            cwd=str(_REPO_ROOT),
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "(unknown)"


def _format_field_value(value: Any) -> str:
    """Format a config value for the verified-values table."""
    if value is None:
        return "(absent)"
    if isinstance(value, bool):
        return "**true**" if value else "**false**"
    return str(value)


def _resolve_base_config(
    config: dict[str, Any],
) -> tuple[Path | None, dict[str, Any] | None]:
    """Resolve the base config referenced by the ``base_config`` field.

    Returns ``(path, config_dict)`` on success, ``(None, None)`` if the
    variant has no ``base_config`` field, and ``(path, None)`` if the
    field is present but the file cannot be loaded.
    """
    base_rel = config.get("base_config")
    if not base_rel:
        return None, None
    base_path = _REPO_ROOT / base_rel
    if not base_path.exists():
        logger.warning(
            "base_config path does not exist: %s (skipping diff)",
            base_path,
        )
        return base_path, None
    try:
        with open(base_path, encoding="utf-8") as f:
            return base_path, json.load(f)
    except (OSError, json.JSONDecodeError) as err:
        logger.warning(
            "Failed to read base_config %s: %s (skipping diff)",
            base_path, err,
        )
        return base_path, None


def _looks_like_no_op_misconfiguration(
    diff_entries: list[ConfigDiffEntry],
) -> bool:
    """Return True if any diff entry is flagged as a no-op change."""
    return any(e.is_no_op for e in diff_entries)


def _build_intent_markdown(
    config: dict[str, Any],
    config_path: Path,
    base_config_path: Path | None,
    base_config: dict[str, Any] | None,
    diff_entries: list[ConfigDiffEntry],
) -> str:
    """Render the experiment_intent.md content."""
    hypothesis_id = config.get("hypothesis", "(unknown)")
    requirement = HYPOTHESIS_REQUIREMENTS.get(hypothesis_id)
    description = (
        requirement.description
        if requirement is not None else "(no requirements registered)"
    )
    varied_field = (
        requirement.varied_field
        if requirement is not None else None
    )

    # Verified values — apply pipeline default for include_example_images
    include_images = config.get("include_example_images", True)

    lines: list[str] = []
    lines.append("# Experiment Intent")
    lines.append("")
    lines.append(
        "Written at launch time by "
        "`scripts/4_detect_mounds_batch.py` via "
        "`scripts/lib_experiment_intent.py`."
    )
    lines.append("")
    lines.append("## Hypothesis")
    lines.append("")
    lines.append(f"- **ID**: {hypothesis_id}")
    lines.append(f"- **Description**: {description}")
    if varied_field:
        lines.append(f"- **Factor being varied**: `{varied_field}`")
    lines.append("")
    lines.append("## Configs")
    lines.append("")
    try:
        variant_rel = config_path.resolve().relative_to(_REPO_ROOT)
    except ValueError:
        variant_rel = config_path.resolve()
    lines.append(f"- **Variant config**: `{variant_rel}`")
    if base_config_path is not None:
        lines.append(f"- **Base config**: `{config.get('base_config')}`")
    else:
        lines.append("- **Base config**: `(not recorded)`")
    lines.append(f"- **Variant version**: `{config.get('version', '(unknown)')}`")
    lines.append("")
    lines.append("## Verified values")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    for field_name in (
        "model",
        "instruction_file",
        "include_example_images",
        "temperature",
        "thinking_level",
        "max_output_tokens",
    ):
        if field_name == "include_example_images":
            value = include_images
        else:
            value = config.get(field_name)
        lines.append(f"| `{field_name}` | {_format_field_value(value)} |")
    lines.append("")

    lines.append("## Transmission check")
    lines.append("")
    if varied_field is None:
        lines.append(
            "- No registered varied factor for this hypothesis; "
            "transmission check skipped."
        )
    elif _looks_like_no_op_misconfiguration(diff_entries):
        no_op_fields = sorted({
            e.field for e in diff_entries if e.is_no_op
        })
        lines.append(f"- The varied factor is `{varied_field}`.")
        lines.append(
            f"- `include_example_images` is "
            f"{_format_field_value(include_images)}."
        )
        lines.append(
            "- **The varied factor will NOT reach the API payload.**"
        )
        lines.append(
            f"- Fields flagged as no-op: "
            f"{', '.join(f'`{f}`' for f in no_op_fields)}"
        )
        lines.append(
            f"- This configuration is inconsistent with hypothesis "
            f"`{hypothesis_id}` as declared in "
            f"`docs/methodology/preregistration/hypothesis-tracking.md`."
        )
        lines.append(
            "- See `docs/notes/reflections/"
            "2026-04-14-h10-h12-config-intent-retrospective.md` for "
            "the class of failure this check prevents."
        )
    else:
        lines.append(f"- The varied factor is `{varied_field}`.")
        lines.append(
            f"- `include_example_images` is "
            f"{_format_field_value(include_images)}."
        )
        lines.append(
            "- The varied factor is expected to reach the API payload."
        )
    lines.append("")

    lines.append("## Config diff vs base")
    lines.append("")
    if base_config is None:
        lines.append(
            "Diff skipped: no `base_config` field in the variant (legacy "
            "config), or the base config file could not be loaded."
        )
    elif not diff_entries:
        lines.append(
            "No fields differ between the variant and its base (after "
            "ignoring version, description, and example list)."
        )
    else:
        lines.append("| Field | Base | Variant | No-op? |")
        lines.append("|---|---|---|---|")
        for e in diff_entries:
            no_op_col = "**YES**" if e.is_no_op else "no"
            if e.is_no_op and e.no_op_reason:
                no_op_col = f"**YES** — {e.no_op_reason}"
            lines.append(
                f"| `{e.field}` | {e.base_value} | {e.variant_value} "
                f"| {no_op_col} |"
            )
    lines.append("")

    lines.append("## Provenance")
    lines.append("")
    lines.append(f"- Git commit: `{_get_git_commit()}`")
    lines.append(
        f"- Launched at: {datetime.now(timezone.utc).isoformat()}"
    )
    lines.append(f"- Python: {sys.version.split()[0]}")
    lines.append(f"- User: {os.environ.get('USER', '(unknown)')}")
    lines.append("")

    return "\n".join(lines)


def _extract_intent_fields(intent_text: str) -> dict[str, str]:
    """Parse key fields from an existing experiment_intent.md.

    The markdown file contains two tables — a "Verified values" table and a
    "Config diff vs base" table — and both start with ``| `field` |`` rows.
    This parser is section-aware: it only extracts table rows while inside
    the Verified values section, so diff-table rows (which record the
    BASE's value in their second column) do not overwrite the verified
    (variant) values.
    """
    fields: dict[str, str] = {}
    current_section: str | None = None
    for line in intent_text.splitlines():
        stripped = line.strip()

        # Section header tracking
        if stripped.startswith("## "):
            current_section = stripped[3:].strip()
            continue

        # Verified-values table rows only
        if (
            current_section == "Verified values"
            and stripped.startswith("| `")
            and stripped.endswith("|")
        ):
            parts = [p.strip() for p in stripped.strip("|").split("|")]
            if len(parts) >= 2:
                key = parts[0].strip(" `")
                value = parts[1].strip(" `*")
                fields[key] = value

        # Hypothesis ID (outside tables; in ## Hypothesis section)
        if stripped.startswith("- **ID**:"):
            fields["hypothesis"] = stripped.split(":", 1)[1].strip()
        if stripped.startswith("- **Variant version**:"):
            fields["version"] = stripped.split(":", 1)[1].strip().strip("`")
    return fields


def _existing_intent_matches(
    existing_text: str,
    current_config: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Compare an existing intent file's fields against the current config.

    Returns ``(is_consistent, mismatched_field_names)``.
    """
    existing = _extract_intent_fields(existing_text)
    mismatches: list[str] = []
    for field_name in _KEY_FIELDS_FOR_CONSISTENCY:
        if field_name == "include_example_images":
            cur_val = current_config.get(field_name, True)
            cur_str = "true" if cur_val else "false"
        else:
            cur_val = current_config.get(field_name)
            cur_str = (
                "(absent)" if cur_val is None else str(cur_val)
            )
        if field_name not in existing:
            continue
        if existing[field_name] != cur_str:
            mismatches.append(field_name)
    return (len(mismatches) == 0, mismatches)


def write_experiment_intent(
    experiment_root: Path,
    config: dict[str, Any],
    config_path: Path,
    dry_run: bool,
) -> tuple[Path | None, bool, list[ConfigDiffEntry]]:
    """Write or verify experiment_intent.md at the experiment root.

    Args:
        experiment_root: Directory where intent-md lives. One file per
            experiment, shared across all runs of the same config.
        config: The loaded variant config dict.
        config_path: Path to the variant config file.
        dry_run: When True, print a preview to stdout and do not write.

    Returns:
        ``(written_path, is_consistent, diff_entries)``.
        - ``written_path`` is the path to the file (or None in dry-run).
        - ``is_consistent`` is True on a fresh write, True on rerun with
          matching content, False on rerun with a mismatch.
        - ``diff_entries`` is the list from diff_configs, for the caller
          to feed into run_launch_checks without re-computing.
    """
    base_config_path, base_config = _resolve_base_config(config)
    diff_entries: list[ConfigDiffEntry] = []
    if base_config is not None:
        diff_entries = diff_configs(config, base_config)

    intent_md = _build_intent_markdown(
        config=config,
        config_path=config_path,
        base_config_path=base_config_path,
        base_config=base_config,
        diff_entries=diff_entries,
    )

    if dry_run:
        print("\n=== experiment_intent.md (dry-run preview) ===")
        print(intent_md)
        print("=== end preview ===\n")
        return None, True, diff_entries

    intent_path = experiment_root / _INTENT_FILENAME
    if intent_path.exists():
        existing = intent_path.read_text(encoding="utf-8")
        is_consistent, mismatches = _existing_intent_matches(existing, config)
        if is_consistent:
            logger.info(
                "%s exists and matches current config; not overwriting",
                intent_path,
            )
        else:
            logger.warning(
                "%s exists but key fields differ from current config: %s",
                intent_path, ", ".join(mismatches),
            )
            logger.warning("Existing file left in place; will not overwrite.")
        return intent_path, is_consistent, diff_entries

    experiment_root.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(intent_md, encoding="utf-8")
    logger.info("Wrote %s", intent_path)
    return intent_path, True, diff_entries


# ============================================================================
# Diff-and-warn gate
# ============================================================================


def _render_diff_table(diff_entries: list[ConfigDiffEntry]) -> str:
    """Render a plain-text table of diff entries for stdout."""
    if not diff_entries:
        return "  (no fields differ)"
    header = f"  {'field':<28} {'base':<24} {'variant':<24} no-op?"
    sep = "  " + "-" * (28 + 24 + 24 + 8)
    lines = [header, sep]
    for e in diff_entries:
        base_str = str(e.base_value)[:23]
        variant_str = str(e.variant_value)[:23]
        no_op_col = (
            f"YES ({e.no_op_reason})"
            if e.is_no_op else "no"
        )
        lines.append(
            f"  {e.field:<28} {base_str:<24} {variant_str:<24} {no_op_col}"
        )
    return "\n".join(lines)


def _prompt_confirm() -> bool:
    """Prompt the user with [y/N]. EOF or non-y returns False."""
    try:
        response = input("Continue anyway? [y/N]: ").strip().lower()
    except EOFError:
        return False
    return response in ("y", "yes")


def run_launch_checks(
    config: dict[str, Any],
    config_path: Path,
    experiment_root: Path,
    dry_run: bool,
    skip_intent_check: bool,
) -> bool:
    """Unified launch-time guard for the detection pipeline.

    Called once per experiment launch, before any API calls. Writes or
    verifies the experiment_intent.md file, computes and prints a diff
    of the variant config against its base (if a ``base_config`` field
    is present), and prompts the user to confirm if any changed fields
    are flagged as no-ops under the current modality gate.

    Args:
        config: Loaded variant config dict.
        config_path: Path to the variant config file.
        experiment_root: Experiment output directory. The intent-md is
            written here (not inside per-run subdirectories).
        dry_run: When True, intent-md is previewed rather than written
            and the confirmation gate is downgraded to a warning
            (dry-runs never block).
        skip_intent_check: When True, no interactive prompt fires; the
            check logs findings and returns True.

    Returns:
        True to proceed with API calls, False if the user aborted at
        the confirmation prompt.
    """
    intent_path, is_consistent, diff_entries = write_experiment_intent(
        experiment_root=experiment_root,
        config=config,
        config_path=config_path,
        dry_run=dry_run,
    )

    # Report the diff in a concise way to stdout
    print()
    print(
        f"[intent-check] config diff vs base "
        f"({config.get('version', '(unknown)')}):"
    )
    if diff_entries:
        print(_render_diff_table(diff_entries))
    else:
        print("  (no base_config recorded, or no differing fields)")
    print()

    # Consistency-on-rerun check (write_experiment_intent already logged
    # the mismatch details; we only gate on it here).
    if not is_consistent and not dry_run and not skip_intent_check:
        print(
            "WARNING: experiment_intent.md already exists at "
            f"{intent_path} and key fields disagree with the current "
            "config. This may indicate that the experiment is being "
            "re-run with a modified config."
        )
        if not _prompt_confirm():
            print("Aborted by user at launch-time intent check.")
            return False

    # No-op gate
    if _looks_like_no_op_misconfiguration(diff_entries):
        print(
            "WARNING: this experiment varies fields that will NOT reach "
            "the API payload. The varied factor is gated by "
            "`include_example_images=False`."
        )
        print(
            "This matches the H10/H12 failure class described in Obs "
            "227, Obs 234, and the formal retraction in Obs 235 "
            "(docs/notes/reflections/"
            "2026-04-14-h10-h12-config-intent-retrospective.md)."
        )
        if dry_run:
            print(
                "[intent-check] --dry-run set; warning logged but the "
                "launch would proceed in a non-dry-run."
            )
            return True
        if skip_intent_check:
            print(
                "[intent-check] --skip-intent-check set; proceeding "
                "despite no-op findings."
            )
            return True
        if not _prompt_confirm():
            print("Aborted by user at launch-time intent check.")
            return False
        return True

    print("[intent-check] all fields that differ from the base will "
          "reach the API payload. OK.")
    return True
