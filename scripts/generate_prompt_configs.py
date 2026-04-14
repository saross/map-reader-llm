#!/usr/bin/env python3
"""Assemble prompt config JSONs from example pools.

Takes a base config (e.g., ``detect_brief-text.json``) and replaces the
hard-positive and hard-negative examples with those selected by
``build_example_pool.py``, while keeping canonical positives, canonical
negatives, and null tiles unchanged.

Also copies the cropped example images into the neutral-naming directory
expected by the detection pipeline.

Usage:
    python scripts/generate_prompt_configs.py \\
        --pool outputs/h10/example-pools/pool_160_hp4hn4/ \\
        --base-config prompts/configs/detect_brief-text.json \\
        --output-dir prompts/configs/h10/

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from lib_hypothesis_requirements import (  # noqa: E402
    HYPOTHESIS_REQUIREMENTS,
    HypothesisRequirement,
    format_validation_report,
    validate_config_against_hypothesis,
)

logger = logging.getLogger(__name__)

# =========================================================================
# Constants
# =========================================================================

_REPO_ROOT = _SCRIPT_DIR.parent

# Categories that are replaced by the pool builder
_REPLACEABLE_CATEGORIES = {"hard_positive", "hard_negative"}

# Categories preserved from the base config
_PRESERVED_CATEGORIES = {"canonical_positive", "canonical_negative", "null"}


# =========================================================================
# Errors and helpers
# =========================================================================


class ConfigIntentMismatchError(Exception):
    """Raised when a generated config fails hypothesis validation.

    Carries the rendered refusal report as its message so that the CLI
    entry point can print it verbatim and exit with a non-zero status.
    """


# Empty-requirement sentinel used when looking up an unknown hypothesis
# for the "0 required fields" log line in the success path. Uses a real
# frozen HypothesisRequirement instance rather than a bare class with a
# mutable class attribute — the frozen-ness prevents a future maintainer
# from accidentally mutating the shared default and introducing a
# state-sharing bug.
_EMPTY_REQUIREMENT = HypothesisRequirement(
    hypothesis_id="(none)",
    description="(placeholder for unknown hypothesis)",
)


def _preflight_validate_hypothesis(
    base_config: dict,
    base_config_path: Path,
    hypothesis: str,
) -> None:
    """Validate the base config against a hypothesis BEFORE any file writes.

    The generator only copies modality, temperature, thinking level, and
    instruction file verbatim from the base. The hypothesis's required
    fields are almost always among these, so the base config is a faithful
    proxy for the would-be generated config for validation purposes.

    Raises:
        ConfigIntentMismatchError: on failure, with a structured report.
    """
    # Augment the base with the fields the generator will add, so that
    # validation sees the final shape without the generator having to
    # write any files yet.
    preview = dict(base_config)
    try:
        base_rel = str(base_config_path.resolve().relative_to(_REPO_ROOT))
    except ValueError:
        base_rel = str(base_config_path.resolve())
    preview["base_config"] = base_rel

    findings = validate_config_against_hypothesis(
        preview, hypothesis, base_config=base_config,
    )
    if findings:
        report = format_validation_report(findings, hypothesis)
        raise ConfigIntentMismatchError(report)


# =========================================================================
# Config generation
# =========================================================================


def generate_config(
    base_config_path: Path,
    pool_dir: Path,
    output_dir: Path,
    condition_name: str | None = None,
    hypothesis: str | None = None,
) -> Path:
    """Generate a new prompt config from a base config and example pool.

    Reads the base config, keeps all non-hard examples (canonical
    positives, canonical negatives, nulls), and replaces hard positives
    and hard negatives with those from the pool. Copies crop images
    into a neutral-naming directory under the output config location.

    Writes a ``base_config`` field into the generated config recording the
    repo-relative path of the base, so that downstream launch-time
    verification tools (``lib_experiment_intent``) can diff the variant
    against its base.

    When ``hypothesis`` is provided, validates the generated config against
    the preregistered hypothesis's required fields (see
    ``lib_hypothesis_requirements.HYPOTHESIS_REQUIREMENTS``) and refuses
    with an explanatory report if the config is inconsistent. This is the
    structural check motivated by the 2026-04-14 Obs 235 retraction: it
    catches cases like cloning a text-only base for an H12 library test.

    Args:
        base_config_path: Path to the base prompt config JSON.
        pool_dir: Path to the example pool directory (must contain
            ``selected_examples.json`` and ``crops/``).
        output_dir: Target directory for the generated config and
            example images.
        condition_name: Optional name for the condition (used in the
            config ``version`` and ``description`` fields). Defaults
            to the pool directory name.
        hypothesis: Optional preregistered hypothesis ID (e.g. ``"H12"``).
            When provided, the generated config is validated against the
            hypothesis's required fields before being written. On failure,
            the function raises ``ConfigIntentMismatchError`` with a
            structured report.

    Returns:
        Path to the generated config JSON file.

    Raises:
        ConfigIntentMismatchError: When ``hypothesis`` is provided and the
            generated config does not satisfy the hypothesis's required
            fields. The error message is a multi-line report naming the
            misaligned fields and suggested fixes.
    """
    # Load base config
    with open(base_config_path, encoding="utf-8") as f:
        base_config = json.load(f)

    # Preflight hypothesis validation — run BEFORE any file writes so a
    # refusal leaves no partial artefacts on disk. The base config's
    # modality, temperature, thinking, and instruction fields are copied
    # verbatim into the generated config, so validating the base is a
    # faithful proxy for validating the final output at this stage.
    if hypothesis is not None:
        _preflight_validate_hypothesis(
            base_config=base_config,
            base_config_path=base_config_path,
            hypothesis=hypothesis,
        )

    # Load pool examples
    pool_examples_path = pool_dir / "selected_examples.json"
    with open(pool_examples_path, encoding="utf-8") as f:
        pool_data = json.load(f)

    hp_selected = pool_data.get("hard_positives", [])
    hn_selected = pool_data.get("hard_negatives", [])

    cond = condition_name or pool_dir.name

    # Set up neutral-naming directory for images (post-validation only)
    output_dir.mkdir(parents=True, exist_ok=True)
    examples_dir = output_dir / "examples" / cond / "neutral-naming"
    examples_dir.mkdir(parents=True, exist_ok=True)

    # Preserve canonical and null examples from base config
    preserved = [
        e for e in base_config.get("examples", [])
        if e.get("category") in _PRESERVED_CATEGORIES
    ]

    # Copy preserved example images from the canonical examples directory
    base_examples_root = _REPO_ROOT / "inputs" / "examples"
    new_examples: list[dict] = []
    example_idx = 1

    for entry in preserved:
        src_path = base_examples_root / entry["path"]
        new_name = f"example_{example_idx:02d}.png"
        dst_path = examples_dir / new_name
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
        else:
            logger.warning(
                "Preserved example not found: %s", src_path,
            )
        new_examples.append({
            "path": f"neutral-naming/{new_name}",
            "label": entry["label"],
            "category": entry["category"],
        })
        example_idx += 1

    # Add hard positives from pool
    for hp in hp_selected:
        new_name = f"example_{example_idx:02d}.png"
        dst_path = examples_dir / new_name
        src_crop = hp.get("crop_path")
        if src_crop and Path(src_crop).exists():
            shutil.copy2(src_crop, dst_path)
        else:
            logger.warning(
                "HP crop not found: %s (will use placeholder)",
                src_crop,
            )
        new_examples.append({
            "path": f"neutral-naming/{new_name}",
            "label": "Positive",
            "category": "hard_positive",
        })
        example_idx += 1

    # Add hard negatives from pool
    for hn in hn_selected:
        new_name = f"example_{example_idx:02d}.png"
        dst_path = examples_dir / new_name
        src_crop = hn.get("crop_path")
        if src_crop and Path(src_crop).exists():
            shutil.copy2(src_crop, dst_path)
        else:
            logger.warning(
                "HN crop not found: %s (will use placeholder)",
                src_crop,
            )
        new_examples.append({
            "path": f"neutral-naming/{new_name}",
            "label": "Negative",
            "category": "hard_negative",
        })
        example_idx += 1

    # Build the new config
    new_config = dict(base_config)
    new_config["version"] = f"{base_config['version']}_{cond}"
    new_config["description"] = (
        f"Auto-generated from {base_config['version']} with pool "
        f"{cond}: {len(hp_selected)} HP + {len(hn_selected)} HN."
    )
    new_config["examples"] = new_examples
    new_config["pool_source"] = str(pool_dir)

    # Record the base config path as a repo-relative string so that
    # launch-time diff tools can resolve the base later. See
    # ``lib_experiment_intent.run_launch_checks`` for the consumer.
    try:
        base_rel = base_config_path.resolve().relative_to(_REPO_ROOT)
        new_config["base_config"] = str(base_rel)
    except ValueError:
        # Base config lives outside the repo — record as absolute path
        new_config["base_config"] = str(base_config_path.resolve())

    # Preflight validation already ran if a hypothesis was provided. Here
    # we stamp the hypothesis onto the generated config so that downstream
    # loaders and the launch-time checks can cross-reference it.
    if hypothesis is not None:
        new_config["hypothesis"] = hypothesis
        # Defensive re-validation of the final new_config — catches the
        # rare case where a generator bug drops a required field after the
        # preflight. This is a cheap second check; it will never fail for
        # a well-behaved generator run.
        findings = validate_config_against_hypothesis(
            new_config, hypothesis, base_config=base_config,
        )
        if findings:
            report = format_validation_report(findings, hypothesis)
            raise ConfigIntentMismatchError(report)
        logger.info(
            "Hypothesis validation passed for %s: %d required fields checked",
            hypothesis, len(HYPOTHESIS_REQUIREMENTS.get(
                hypothesis, _EMPTY_REQUIREMENT,
            ).required_fields),
        )

    # Write config
    config_filename = f"detect_{cond}.json"
    config_path = output_dir / config_filename
    config_path.write_text(
        json.dumps(new_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info(
        "Generated config %s: %d examples "
        "(%d preserved + %d HP + %d HN)",
        config_filename, len(new_examples),
        len(preserved), len(hp_selected), len(hn_selected),
    )

    return config_path


# =========================================================================
# CLI
# =========================================================================


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate prompt configs from example pools.",
    )
    parser.add_argument(
        "--pool", type=Path, required=True,
        help="Path to example pool directory (from build_example_pool.py)",
    )
    parser.add_argument(
        "--base-config", type=Path, required=True,
        help="Path to base prompt config JSON",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for generated config and examples",
    )
    parser.add_argument(
        "--condition-name", type=str, default=None,
        help="Condition name (default: pool directory name)",
    )
    parser.add_argument(
        "--hypothesis", type=str, default=None,
        help=(
            "Preregistered hypothesis ID that this config is intended to "
            "test (e.g. 'H12'). When provided, the generator validates "
            "the generated config against the hypothesis's required "
            "fields from scripts/lib_hypothesis_requirements.py and "
            "refuses to emit a config that fails the check, with a "
            "structured explanatory report. Omit for backwards-compatible "
            "generation without validation."
        ),
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.hypothesis is None:
        logger.info(
            "--hypothesis not provided; skipping hypothesis validation. "
            "The generated config will still carry a base_config field."
        )

    try:
        config_path = generate_config(
            base_config_path=args.base_config,
            pool_dir=args.pool,
            output_dir=args.output_dir,
            condition_name=args.condition_name,
            hypothesis=args.hypothesis,
        )
    except ConfigIntentMismatchError as err:
        print(str(err), file=sys.stderr)
        sys.exit(2)

    print(f"\nGenerated config: {config_path}")


if __name__ == "__main__":
    main()
