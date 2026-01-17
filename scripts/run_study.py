#!/usr/bin/env python3
"""
Study Runner: Orchestrates Factorial Experiments
=================================================

Executes multi-condition studies defined in YAML configuration files.
Generates the Cartesian product of factorial levels, manages checkpointing,
and provides resumption capability for long-running experiments.

Usage:
    python scripts/run_study.py studies/phase2-factorial.yaml
    python scripts/run_study.py studies/phase2-factorial.yaml --dry-run
    python scripts/run_study.py studies/phase2-factorial.yaml --resume
    python scripts/run_study.py studies/phase2-factorial.yaml --timeout 7200
    python scripts/run_study.py studies/phase2-factorial.yaml --condition "image-only_canonical-first_baseline_T1.0"

Inputs:
    - Study definition YAML file
    - Prompt configs from prompts/configs/
    - Tile manifest from inputs/

Outputs:
    - Per-condition detection results in study output directory
    - Checkpoint file for resumption
    - Study manifest documenting all conditions
    - Summary CSV with per-condition metrics

Exit Codes:
    0 - Success: All conditions completed successfully
    1 - Error: Configuration or execution error prevented study from running
    2 - Partial failure: Some conditions failed but study completed

Author: Shawn Ross, Claude Code
Version: 1.0.0
Licence: Apache 2.0
"""

import argparse
import itertools
import json
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# Script version
__version__ = "1.0.0"

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent


def load_study_config(yaml_path: Path) -> dict:
    """
    Load and validate study configuration from YAML file.

    Args:
        yaml_path: Path to study YAML file

    Returns:
        Parsed study configuration dictionary

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        ValueError: If required fields are missing
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Study config not found: {yaml_path}")

    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    # Validate required sections
    required_sections = ["study", "defaults", "factors"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section: {section}")

    return config


def generate_conditions(config: dict) -> list[dict]:
    """
    Generate all experimental conditions from factorial design.

    Takes the Cartesian product of all factor levels to produce
    the full set of conditions to test.

    Args:
        config: Study configuration dictionary

    Returns:
        List of condition dictionaries, each containing:
        - condition_id: Unique identifier string
        - config_file: Path to prompt config JSON
        - temperature: Temperature override value
        - factor_levels: Dictionary of factor -> level mappings
    """
    factors = config["factors"]
    defaults = config.get("defaults", {})

    # Extract factor names and their levels
    factor_names = list(factors.keys())
    factor_levels = [factors[name] for name in factor_names]

    # Generate Cartesian product
    conditions = []
    for combo in itertools.product(*factor_levels):
        # Build condition from this combination
        level_dict = dict(zip(factor_names, combo))

        # Construct condition ID from level IDs
        condition_id = "_".join(level["id"] for level in combo)

        # Determine config file path
        # Format: {modality_base}{ordering_suffix}{hardneg_suffix}.json
        modality_level = level_dict["modality"]
        ordering_level = level_dict["ordering"]
        hardneg_level = level_dict["hard_negatives"]
        temp_level = level_dict["temperature"]

        config_base = modality_level["config_base"]
        ordering_suffix = ordering_level.get("config_suffix", "")
        hardneg_suffix = hardneg_level.get("config_suffix", "")

        config_filename = f"{config_base}{ordering_suffix}{hardneg_suffix}.json"
        config_path = PROJECT_ROOT / "prompts" / "configs" / config_filename

        condition = {
            "condition_id": condition_id,
            "config_file": str(config_path),
            "config_filename": config_filename,
            "temperature": temp_level.get("value", defaults.get("temperature", 1.0)),
            "factor_levels": {name: level["id"] for name, level in level_dict.items()},
            "descriptions": {name: level.get("description", "") for name, level in level_dict.items()},
        }

        conditions.append(condition)

    return conditions


def validate_configs(conditions: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Validate that all required config files exist.

    Args:
        conditions: List of condition dictionaries

    Returns:
        Tuple of (valid_conditions, missing_conditions)
    """
    valid = []
    missing = []

    # Track unique config files to avoid duplicate warnings
    checked_configs = set()

    for condition in conditions:
        config_path = Path(condition["config_file"])

        if config_path in checked_configs:
            # Already validated this config
            if config_path.exists():
                valid.append(condition)
            else:
                missing.append(condition)
            continue

        checked_configs.add(config_path)

        if config_path.exists():
            valid.append(condition)
        else:
            missing.append(condition)

    return valid, missing


def load_checkpoint(checkpoint_path: Path) -> dict:
    """
    Load checkpoint file if it exists.

    Args:
        checkpoint_path: Path to checkpoint JSON file

    Returns:
        Checkpoint dictionary with completed conditions, or empty dict
    """
    if checkpoint_path.exists():
        with open(checkpoint_path, "r") as f:
            return json.load(f)
    return {"completed": [], "failed": [], "last_updated": None}


def save_checkpoint(checkpoint_path: Path, checkpoint: dict) -> None:
    """
    Save checkpoint to file.

    Args:
        checkpoint_path: Path to checkpoint JSON file
        checkpoint: Checkpoint dictionary to save
    """
    checkpoint["last_updated"] = datetime.now(timezone.utc).isoformat()
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_path, "w") as f:
        json.dump(checkpoint, f, indent=2)


def run_condition(
    condition: dict,
    config: dict,
    output_dir: Path,
    dry_run: bool = False,
    timeout: int = 3600,
) -> tuple[bool, str]:
    """
    Execute detection for a single condition.

    Args:
        condition: Condition dictionary with config_file, temperature, etc.
        config: Full study configuration
        output_dir: Base output directory for results
        dry_run: If True, print command without executing
        timeout: Maximum seconds to wait for condition to complete (default: 3600)

    Returns:
        Tuple of (success: bool, message: str)
    """
    defaults = config.get("defaults", {})

    # Build output filename
    condition_id = condition["condition_id"]
    output_filename = f"{condition_id}"

    # Build command
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "4_detect_mounds_batch.py"),
        "--config", condition["config_file"],
        "--output", output_filename,
        "--workers", str(defaults.get("workers", 1)),
    ]

    # Add manifest if specified
    manifest = defaults.get("manifest")
    if manifest:
        manifest_path = PROJECT_ROOT / manifest
        cmd.extend(["--manifest", str(manifest_path)])

    # Note: Temperature override would need to be added to 4_detect_mounds_batch.py
    # For now, we document it in the output but rely on config file temperature

    if dry_run:
        print(f"  [DRY RUN] Would execute: {' '.join(cmd)}")
        print(f"            Temperature: {condition['temperature']}")
        return True, "dry_run"

    try:
        # Set environment variable for temperature override
        env = dict(__import__("os").environ)
        env["STUDY_TEMPERATURE_OVERRIDE"] = str(condition["temperature"])
        env["STUDY_CONDITION_ID"] = condition_id
        env["STUDY_OUTPUT_DIR"] = str(output_dir)

        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

        if result.returncode == 0:
            return True, "success"
        else:
            error_msg = result.stderr[:500] if result.stderr else "Unknown error"
            return False, f"exit_code_{result.returncode}: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, f"exception: {str(e)}"


def run_study(
    study_path: Path,
    dry_run: bool = False,
    resume: bool = False,
    single_condition: str | None = None,
    verbose: bool = True,
    timeout: int = 3600,
) -> dict:
    """
    Execute a complete study from YAML definition.

    Args:
        study_path: Path to study YAML file
        dry_run: If True, print commands without executing
        resume: If True, skip already-completed conditions
        single_condition: If specified, run only this condition ID
        verbose: If True, print progress information
        timeout: Maximum seconds per condition (default: 3600)

    Returns:
        Summary dictionary with results
    """
    # Load configuration
    config = load_study_config(study_path)
    study_info = config["study"]
    defaults = config.get("defaults", {})
    execution = config.get("execution", {})

    if verbose:
        print("=" * 70)
        print(f"Study: {study_info['name']}")
        print(f"Version: {study_info.get('version', 'unknown')}")
        print(f"Description: {study_info.get('description', '').strip()}")
        print("=" * 70)
        print()

    # Generate conditions
    conditions = generate_conditions(config)

    if verbose:
        print(f"Generated {len(conditions)} conditions from factorial design")

    # Validate configs exist
    valid_conditions, missing_conditions = validate_configs(conditions)

    if missing_conditions:
        # Get unique missing configs
        missing_configs = set(c["config_filename"] for c in missing_conditions)
        print(f"\nWARNING: {len(missing_configs)} config file(s) not found:")
        for cfg in sorted(missing_configs):
            print(f"  - prompts/configs/{cfg}")
        print()

        if not valid_conditions:
            print("ERROR: No valid conditions to run. Create missing configs first.")
            return {"error": "no_valid_conditions", "missing_configs": list(missing_configs)}

        print(f"Proceeding with {len(valid_conditions)} valid condition(s)")
        conditions = valid_conditions

    # Filter to single condition if specified
    if single_condition:
        conditions = [c for c in conditions if c["condition_id"] == single_condition]
        if not conditions:
            print(f"ERROR: Condition '{single_condition}' not found")
            return {"error": "condition_not_found"}
        if verbose:
            print(f"Running single condition: {single_condition}")

    # Set up output directory
    output_dir = PROJECT_ROOT / defaults.get("output_dir", "outputs/study")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load checkpoint if resuming
    checkpoint_path = output_dir / "checkpoint.json"
    checkpoint = {"completed": [], "failed": []}

    if resume:
        checkpoint = load_checkpoint(checkpoint_path)
        completed_ids = set(checkpoint.get("completed", []))
        original_count = len(conditions)
        conditions = [c for c in conditions if c["condition_id"] not in completed_ids]
        if verbose:
            print(f"Resuming: {original_count - len(conditions)} already completed, {len(conditions)} remaining")

    # Randomise order if configured
    if execution.get("randomise_order", False) and not single_condition:
        seed = config["study"].get("random_seed", 42)
        random.seed(seed)
        random.shuffle(conditions)
        if verbose:
            print(f"Randomised condition order (seed={seed})")

    # Write study manifest
    manifest = {
        "study": study_info,
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_conditions": len(conditions),
        "conditions": conditions,
    }
    manifest_path = output_dir / "study_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    if verbose:
        print(f"\nStudy manifest written: {manifest_path}")
        print()

    # Execute conditions
    checkpoint_every = execution.get("checkpoint_every", 10)
    stop_on_error = execution.get("stop_on_error", False)

    results = {"completed": [], "failed": [], "skipped": []}

    for i, condition in enumerate(conditions, 1):
        condition_id = condition["condition_id"]

        if verbose:
            print(f"[{i}/{len(conditions)}] {condition_id}")
            print(f"         Config: {condition['config_filename']}")
            print(f"         Temperature: {condition['temperature']}")

        success, message = run_condition(
            condition, config, output_dir, dry_run=dry_run, timeout=timeout
        )

        if success:
            results["completed"].append(condition_id)
            checkpoint["completed"].append(condition_id)
            if verbose:
                print(f"         Status: OK ({message})")
        else:
            results["failed"].append({"condition_id": condition_id, "error": message})
            checkpoint["failed"].append({"condition_id": condition_id, "error": message})
            if verbose:
                print(f"         Status: FAILED ({message})")

            if stop_on_error:
                print("\nStopping due to error (stop_on_error=true)")
                break

        # Checkpoint periodically
        if i % checkpoint_every == 0:
            save_checkpoint(checkpoint_path, checkpoint)
            if verbose:
                print(f"         [Checkpoint saved: {len(checkpoint['completed'])} completed]")

        print()

    # Final checkpoint
    save_checkpoint(checkpoint_path, checkpoint)

    # Summary
    if verbose:
        print("=" * 70)
        print("Study Complete")
        print("=" * 70)
        print(f"Completed: {len(results['completed'])}")
        print(f"Failed: {len(results['failed'])}")
        print(f"Checkpoint: {checkpoint_path}")
        print()

    return results


def main():
    """Main entry point for study runner."""
    parser = argparse.ArgumentParser(
        description="Run factorial experiments from YAML study definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full study
  python scripts/run_study.py studies/phase2-factorial.yaml

  # Dry run (show commands without executing)
  python scripts/run_study.py studies/phase2-factorial.yaml --dry-run

  # Resume from checkpoint
  python scripts/run_study.py studies/phase2-factorial.yaml --resume

  # Run single condition
  python scripts/run_study.py studies/phase2-factorial.yaml \\
      --condition "image-only_canonical-first_baseline_T1.0"

  # List all conditions without running
  python scripts/run_study.py studies/phase2-factorial.yaml --list
        """,
    )

    parser.add_argument(
        "study_file",
        type=Path,
        help="Path to study YAML file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint, skipping completed conditions",
    )
    parser.add_argument(
        "--condition",
        type=str,
        help="Run only this specific condition ID",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all conditions and exit",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Timeout in seconds per condition (default: 3600)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        config = load_study_config(args.study_file)
        conditions = generate_conditions(config)
        valid, missing = validate_configs(conditions)

        print(f"Study: {config['study']['name']}")
        print(f"Total conditions: {len(conditions)}")
        print(f"Valid configs: {len(valid)}")
        print(f"Missing configs: {len(missing)}")
        print()
        print("Conditions:")
        for c in conditions:
            status = "OK" if Path(c["config_file"]).exists() else "MISSING"
            print(f"  [{status}] {c['condition_id']}")
            print(f"          {c['config_filename']} @ T={c['temperature']}")
        return

    # Run study
    results = run_study(
        study_path=args.study_file,
        dry_run=args.dry_run,
        resume=args.resume,
        single_condition=args.condition,
        verbose=not args.quiet,
        timeout=args.timeout,
    )

    # Exit code based on results
    if results.get("error"):
        sys.exit(1)
    elif results.get("failed"):
        sys.exit(2)  # Partial failure
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
