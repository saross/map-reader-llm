#!/usr/bin/env python3
"""
Phase 2 Runner: One-Factor-At-a-Time (OFAT) Sequential Experiments
===================================================================

Executes Phase 2 sub-phases (2a-2e) of the preregistered study. Each sub-phase
tests one factor at a time, carrying optimal parameters forward from prior phases.

Parses the OFAT YAML (Yet Another Markup Language) structure (single factor with
named levels, each pointing to a config file), then loops condition x run, calling
4_detect_mounds_batch.py via subprocess for each execution unit (one pass per run,
per preregistration section 3.8).

Usage:
    python scripts/run_phase2.py studies/phase2a-h1-modality.yaml
    python scripts/run_phase2.py studies/phase2a-h1-modality.yaml --dry-run
    python scripts/run_phase2.py studies/phase2a-h1-modality.yaml --resume
    python scripts/run_phase2.py studies/phase2a-h1-modality.yaml --condition image-only --runs 3
    python scripts/run_phase2.py studies/phase2a-h1-modality.yaml --limit 3
    python scripts/run_phase2.py studies/phase2a-h1-modality.yaml --resume --parallel-units 4

Inputs:
    - Study definition YAML file (OFAT structure with factors/levels)
    - Prompt configs from prompts/configs/
    - Tile manifest from inputs/tiles/

Outputs:
    - Per-run detection results: {output_dir}/{condition_name}/run_{K}/
    - JSON (JavaScript Object Notation) checkpoint file for resumption
    - Study manifest documenting all execution units

Exit Codes:
    0 - Success: All execution units completed
    1 - Error: Configuration or execution error
    2 - Partial failure: Some units failed but execution completed

Author: Shawn Ross, Claude Code
Version: 1.1.0
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml

__version__ = "1.1.0"

# Resolve project root as parent of the scripts/ directory
PROJECT_ROOT = Path(__file__).parent.parent


def load_study_config(yaml_path: Path) -> dict:
    """
    Load and validate Phase 2 OFAT study configuration from YAML.

    Expects the OFAT YAML structure with 'study', 'factors', 'inputs',
    and 'execution' sections. Validates that the single factor has named
    levels with config paths.

    Args:
        yaml_path: Path to study YAML file

    Returns:
        Parsed study configuration dictionary

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        ValueError: If required fields are missing or malformed
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Study config not found: {yaml_path}")

    with open(yaml_path) as f:
        config = yaml.safe_load(f)

    # Validate required sections
    required_sections = ["study", "factors", "inputs", "execution"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section: {section}")

    # Validate factors structure
    factors = config["factors"]
    if not factors:
        raise ValueError("'factors' section is empty")

    # Validate inputs
    inputs = config["inputs"]
    if "manifest" not in inputs:
        raise ValueError("'inputs' section must contain 'manifest'")

    # Validate execution
    execution = config["execution"]
    if "runs" not in execution:
        raise ValueError("'execution' section must contain 'runs'")
    if "output_dir" not in execution:
        raise ValueError("'execution' section must contain 'output_dir'")

    return config


def extract_conditions(config: dict) -> list[dict]:
    """
    Extract experimental conditions from the OFAT YAML factor levels.

    Each level in the single factor becomes one condition. Supports two
    YAML structures:

    1. Standard OFAT (phases 2a, 2b, 2c, 2e): 'factors' section with
       named levels, each having 'name' and 'config'.
    2. Pre-enumerated conditions (phase 2d): 'conditions' section with
       explicit condition list (supports 'reuse_from' to skip reused cells).

    Args:
        config: Study configuration dictionary

    Returns:
        List of condition dictionaries, each containing:
        - name: Condition name (e.g., 'image-only')
        - config: Path to prompt config JSON (relative to project root)
        - description: Human-readable description
        - temperature: Temperature override (if applicable)
        - ordering: Ordering override (if applicable)
    """
    conditions = []

    # Check for pre-enumerated conditions (Phase 2d style)
    if "conditions" in config:
        for cond in config["conditions"]:
            # Skip conditions reused from earlier phases
            if cond.get("reuse_from"):
                continue
            if cond.get("run") is False:
                continue

            conditions.append({
                "name": cond["name"],
                "config": cond["config"],
                "description": cond.get("description", ""),
                "temperature": None,
                "ordering": None,
            })
        return conditions

    # Standard OFAT: extract from factors
    factors = config["factors"]
    carried = config.get("carried_forward", {})

    for factor_name, factor_def in factors.items():
        for level in factor_def.get("levels", []):
            # Skip levels explicitly marked as not running in this phase
            if level.get("run_in_phase2d") is False:
                continue

            # Determine config path
            config_path = level.get("config")
            if not config_path:
                # For temperature/ordering factors, use carried-forward config
                config_path = carried.get("optimal_me_config", "")

            # Determine temperature override
            temperature = level.get("value") if factor_name == "temperature" else None

            # Determine ordering override
            ordering = level.get("value") if factor_name == "ordering" else None

            conditions.append({
                "name": level["name"],
                "config": config_path,
                "description": level.get("description", ""),
                "temperature": temperature,
                "ordering": ordering,
            })

    return conditions


def generate_execution_units(
    conditions: list[dict],
    num_runs: int,
    seed: int = 20260205,
) -> list[dict]:
    """
    Generate the full list of execution units (condition x run).

    Units are randomised with a fixed seed to distribute temporal effects
    (Application Programming Interface (API) latency, model version changes)
    evenly across conditions.

    Args:
        conditions: List of condition dictionaries
        num_runs: Number of independent runs per condition (K)
        seed: Random seed for unit ordering

    Returns:
        List of execution unit dictionaries, each containing:
        - condition_name: Name of the condition
        - run: Run number (1-indexed)
        - config: Path to config file
        - temperature: Temperature override (or None)
        - ordering: Ordering override (or None)
    """
    units = []

    for condition in conditions:
        for run in range(1, num_runs + 1):
            units.append({
                "condition_name": condition["name"],
                "run": run,
                "config": condition["config"],
                "temperature": condition.get("temperature"),
                "ordering": condition.get("ordering"),
            })

    # Randomise unit order with fixed seed
    rng = random.Random(seed)
    rng.shuffle(units)

    return units


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

    for condition in conditions:
        config_path = PROJECT_ROOT / condition["config"]
        if config_path.exists():
            valid.append(condition)
        else:
            missing.append(condition)

    return valid, missing


def load_checkpoint(checkpoint_path: Path) -> dict:
    """
    Load checkpoint file if it exists.

    The checkpoint tracks completed (condition, run) tuples so that
    execution can be resumed after interruption.

    Args:
        checkpoint_path: Path to checkpoint JSON file

    Returns:
        Checkpoint dictionary with completed/failed units
    """
    if checkpoint_path.exists():
        with open(checkpoint_path) as f:
            return json.load(f)
    return {
        "completed": [],
        "failed": [],
        "total_cost_usd": 0.0,
        "last_updated": None,
    }


def save_checkpoint(
    checkpoint_path: Path,
    checkpoint: dict,
    lock: threading.Lock | None = None,
) -> None:
    """
    Save checkpoint to file, optionally under a threading lock.

    When parallel_units > 1, a lock is required to prevent race
    conditions on both the in-memory checkpoint dict and the file.

    Args:
        checkpoint_path: Path to checkpoint JSON file
        checkpoint: Checkpoint dictionary to save
        lock: Optional threading lock for thread-safe writes
    """
    def _write() -> None:
        checkpoint["last_updated"] = datetime.now(timezone.utc).isoformat()
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint, f, indent=2)

    if lock:
        with lock:
            _write()
    else:
        _write()


def unit_key(unit: dict) -> str:
    """
    Generate a unique string key for an execution unit.

    Args:
        unit: Execution unit dictionary

    Returns:
        String key in format 'condition_name/run_N'
    """
    return f"{unit['condition_name']}/run_{unit['run']}"


def read_meta_cost(meta_path: Path) -> float:
    """
    Read estimated cost from a .meta.json file.

    Args:
        meta_path: Path to .meta.json file

    Returns:
        Estimated cost in United States Dollars (USD), or 0.0 if unavailable
    """
    if not meta_path.exists():
        return 0.0

    try:
        with open(meta_path) as f:
            meta = json.load(f)
        # The LLMMetadataTracker nests cost under 'cost_estimate.total_cost_usd'
        cost_estimate = meta.get("cost_estimate", {})
        return float(cost_estimate.get("total_cost_usd", 0.0))
    except (json.JSONDecodeError, ValueError, TypeError):
        return 0.0


def read_meta_failures(meta_path: Path) -> int:
    """
    Read items_failed count from a .meta.json file.

    Belt-and-braces validation: even if the batch script exits 0,
    a non-zero items_failed count means the run is partial.

    Args:
        meta_path: Path to .meta.json file

    Returns:
        Number of failed items, or 0 if unavailable
    """
    if not meta_path.exists():
        return 0

    try:
        with open(meta_path) as f:
            meta = json.load(f)
        return int(
            meta.get("execution_stats", {}).get("items_failed", 0)
        )
    except (json.JSONDecodeError, ValueError, TypeError):
        return 0


def run_execution_unit(
    unit: dict,
    config: dict,
    output_dir: Path,
    dry_run: bool = False,
    limit: int | None = None,
    timeout: int = 3600,
    workers_override: int | None = None,
    log_file: Path | None = None,
) -> tuple[bool, str, float]:
    """
    Execute a single (condition, run) unit via 4_detect_mounds_batch.py.

    Each unit is one pass of the batch detector over all tiles (or a
    limited subset) for one condition at one run.

    Args:
        unit: Execution unit dictionary
        config: Full study configuration
        output_dir: Base output directory
        dry_run: If True, print command without executing
        limit: Process only first N tiles (for sanity checks)
        timeout: Maximum seconds to wait for completion
        workers_override: If set, override YAML workers count for parallelism
        log_file: If set, redirect subprocess output to this file
            instead of inheriting the terminal. Used in parallel mode
            to prevent interleaved output from concurrent units.

    Returns:
        Tuple of (success, message, cost_usd)
    """
    inputs = config["inputs"]

    # Build output path: {output_dir}/{condition_name}/run_{K}/
    run_dir = output_dir / unit["condition_name"] / f"run_{unit['run']}"

    # Determine output filename
    output_name = f"detections_{unit['condition_name']}_run{unit['run']:02d}"

    # CLI override or default; YAML workers field is ignored per CLAUDE.md
    # (parallelisation is the governor's job, not the study definition's)
    workers = workers_override or 12

    # Build command
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "4_detect_mounds_batch.py"),
        "--config", str(PROJECT_ROOT / unit["config"]),
        "--manifest", str(PROJECT_ROOT / inputs["manifest"]),
        "--output-dir", str(run_dir),
        "--output", output_name,
        "--workers", str(workers),
    ]

    # Add temperature override if specified
    if unit.get("temperature") is not None:
        cmd.extend(["--temperature", str(unit["temperature"])])

    # Add ordering override if specified
    if unit.get("ordering") is not None:
        cmd.extend(["--ordering", str(unit["ordering"])])

    # Add tile limit for sanity checks
    if limit and limit > 0:
        cmd.extend(["--limit", str(limit)])

    if dry_run:
        print(f"  [DRY RUN] {' '.join(cmd)}")
        return True, "dry_run", 0.0

    try:
        # When log_file is provided (parallel mode), redirect output
        # to avoid interleaved terminal output from concurrent units.
        # When None (sequential mode), inherit terminal for live output.
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "w") as lf:
                result = subprocess.run(
                    cmd,
                    cwd=str(PROJECT_ROOT),
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=timeout,
                )
        else:
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                stdout=None,  # inherit — stream to terminal
                stderr=None,  # inherit — stream to terminal
                text=True,
                timeout=timeout,
            )

        meta_path = run_dir / f"{output_name}.meta.json"
        cost = read_meta_cost(meta_path)
        items_failed = read_meta_failures(meta_path)

        if result.returncode == 0 and items_failed == 0:
            return True, "success", cost

        # Exit code 2 = partial failure (some tiles failed).
        # Accept runs where only a small number of tiles failed
        # (e.g. 1 tile with a known JSON parse issue out of 60).
        max_acceptable_failures = 2
        if result.returncode in (0, 2) and items_failed <= max_acceptable_failures:
            if items_failed > 0:
                print(
                    f"  Accepting partial result: {items_failed} tile(s) "
                    f"failed (≤ {max_acceptable_failures} threshold)"
                )
            return True, "success", cost

        if items_failed > 0:
            return (
                False,
                f"partial_failure_{items_failed}_tiles",
                cost,
            )
        return False, f"exit_code_{result.returncode}", cost

    except subprocess.TimeoutExpired:
        return False, "timeout", 0.0
    except Exception as e:
        return False, f"exception: {str(e)}", 0.0


def run_phase2(
    study_path: Path,
    dry_run: bool = False,
    resume: bool = False,
    runs: int | None = None,
    limit: int | None = None,
    condition_filter: str | None = None,
    verbose: bool = True,
    timeout: int = 3600,
    workers_override: int | None = None,
    parallel_units: int = 1,
) -> dict:
    """
    Execute a Phase 2 OFAT study from YAML definition.

    Args:
        study_path: Path to study YAML file
        dry_run: If True, print commands without executing
        resume: If True, skip already-completed units
        runs: Override number of runs (default: from YAML)
        limit: Process only first N tiles per unit (for sanity checks)
        condition_filter: If specified, run only this condition name
        verbose: If True, print progress information
        timeout: Maximum seconds per execution unit
        workers_override: If set, override YAML workers count for parallelism
        parallel_units: Number of execution units to run concurrently.
            Default 1 = sequential (backward compatible). When > 1,
            units are dispatched via ThreadPoolExecutor with per-unit
            log files to prevent interleaved terminal output.

    Returns:
        Summary dictionary with results
    """
    # Load configuration
    config = load_study_config(study_path)
    study_info = config["study"]
    execution = config["execution"]

    if verbose:
        print("=" * 70)
        print(f"Study: {study_info['name']}")
        print(f"Phase: {study_info.get('phase', 'unknown')}")
        print(f"Hypothesis: {study_info.get('hypothesis', 'unknown')}")
        print(f"Version: {study_info.get('version', 'unknown')}")
        print(f"Description: {study_info.get('description', '').strip()}")
        print("=" * 70)
        print()

    # Extract conditions
    conditions = extract_conditions(config)

    if not conditions:
        print("ERROR: No conditions extracted from YAML.")
        return {"error": "no_conditions"}

    # Validate configs exist
    valid_conditions, missing_conditions = validate_configs(conditions)

    if missing_conditions:
        print(f"\nWARNING: {len(missing_conditions)} config file(s) not found:")
        for cond in missing_conditions:
            print(f"  - {cond['config']} ({cond['name']})")
        print()

        if not valid_conditions:
            print("ERROR: No valid conditions to run. Create missing configs first.")
            return {"error": "no_valid_conditions"}

        conditions = valid_conditions

    # Apply condition filter
    if condition_filter:
        conditions = [c for c in conditions if c["name"] == condition_filter]
        if not conditions:
            print(f"ERROR: Condition '{condition_filter}' not found")
            all_names = [c["name"] for c in extract_conditions(config)]
            print(f"Available conditions: {', '.join(all_names)}")
            return {"error": "condition_not_found"}

    # Determine number of runs
    num_runs = runs if runs is not None else execution.get("runs", 10)

    if verbose:
        print(f"Conditions: {len(conditions)}")
        for c in conditions:
            print(f"  - {c['name']}: {c['config']}")
            extras = []
            if c.get("temperature") is not None:
                extras.append(f"T={c['temperature']}")
            if c.get("ordering") is not None:
                extras.append(f"ordering={c['ordering']}")
            if extras:
                print(f"    Overrides: {', '.join(extras)}")
        print(f"Runs per condition: {num_runs}")
        tiles_str = "ALL" if not limit else str(limit)
        print(f"Tiles per run: {tiles_str}")
        total_units = len(conditions) * num_runs
        print(f"Total execution units: {total_units}")
        print()

    # Generate execution units
    units = generate_execution_units(conditions, num_runs)

    # Set up output directory
    output_dir = PROJECT_ROOT / execution["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load checkpoint if resuming
    checkpoint_path = output_dir / "checkpoint.json"
    checkpoint = load_checkpoint(checkpoint_path) if resume else {
        "completed": [],
        "failed": [],
        "total_cost_usd": 0.0,
        "last_updated": None,
    }

    # Filter out already-completed units if resuming
    if resume:
        completed_keys = set(checkpoint.get("completed", []))
        original_count = len(units)
        units = [u for u in units if unit_key(u) not in completed_keys]
        if verbose:
            skipped = original_count - len(units)
            print(f"Resuming: {skipped} units already completed, {len(units)} remaining")
            print()

    # Apply condition filter to units
    if condition_filter:
        units = [u for u in units if u["condition_name"] == condition_filter]

    # Write study manifest
    manifest = {
        "study": study_info,
        "generated": datetime.now(timezone.utc).isoformat(),
        "conditions": [c["name"] for c in conditions],
        "runs_per_condition": num_runs,
        "total_units": len(units),
        "tile_limit": limit,
        "execution_order": [unit_key(u) for u in units],
    }
    manifest_path = output_dir / "study_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    if verbose:
        print(f"Manifest: {manifest_path}")
        print()

    # Cost monitoring
    estimated_cost = config.get("estimates", {}).get("cost_usd", 0)
    cost_warn_threshold = (
        estimated_cost * 1.2 if estimated_cost else float("inf")
    )
    running_cost = checkpoint.get("total_cost_usd", 0.0)

    # Execute units
    results = {"completed": [], "failed": []}

    # Cap parallel_units and warn about high combined concurrency
    max_parallel = 8
    if parallel_units > max_parallel:
        print(
            f"  WARNING: --parallel-units {parallel_units} exceeds "
            f"cap of {max_parallel}. Clamping to {max_parallel}."
        )
        parallel_units = max_parallel

    effective_workers = workers_override or 12
    if parallel_units > 1 and parallel_units * effective_workers > 60:
        print(
            f"  WARNING: {parallel_units} parallel units x "
            f"{effective_workers} workers = "
            f"{parallel_units * effective_workers} concurrent API "
            f"calls. Consider reducing to avoid rate limits."
        )

    # Dry-run always runs sequentially (no benefit from parallelism)
    use_parallel = parallel_units > 1 and not dry_run

    if use_parallel:
        results, running_cost = _execute_units_parallel(
            units=units,
            config=config,
            output_dir=output_dir,
            checkpoint=checkpoint,
            checkpoint_path=checkpoint_path,
            limit=limit,
            timeout=timeout,
            workers_override=workers_override,
            parallel_units=parallel_units,
            running_cost=running_cost,
            cost_warn_threshold=cost_warn_threshold,
            verbose=verbose,
        )
    else:
        results, running_cost = _execute_units_sequential(
            units=units,
            config=config,
            output_dir=output_dir,
            checkpoint=checkpoint,
            checkpoint_path=checkpoint_path,
            dry_run=dry_run,
            limit=limit,
            timeout=timeout,
            workers_override=workers_override,
            running_cost=running_cost,
            cost_warn_threshold=cost_warn_threshold,
            verbose=verbose,
        )

    # Summary
    if verbose:
        print("=" * 70)
        print(f"Phase {study_info.get('phase', '?')} Complete")
        print("=" * 70)
        total_completed = len(checkpoint.get("completed", []))
        total_failed = len(results["failed"])
        print(f"Completed: {total_completed} units")
        print(f"Failed: {total_failed} units")
        print(f"Running cost: ${running_cost:.4f}")
        print(f"Checkpoint: {checkpoint_path}")
        if use_parallel:
            log_dir = output_dir / "logs"
            print(f"Per-unit logs: {log_dir}/")
        print()

    return results


def _execute_units_sequential(
    units: list[dict],
    config: dict,
    output_dir: Path,
    checkpoint: dict,
    checkpoint_path: Path,
    dry_run: bool,
    limit: int | None,
    timeout: int,
    workers_override: int | None,
    running_cost: float,
    cost_warn_threshold: float,
    verbose: bool,
) -> tuple[dict, float]:
    """
    Execute units one at a time (original behaviour).

    Returns:
        Tuple of (results dict, updated running_cost)
    """
    results: dict = {"completed": [], "failed": []}

    for i, unit in enumerate(units, 1):
        key = unit_key(unit)

        if verbose:
            extras = []
            if unit.get("temperature") is not None:
                extras.append(f"T={unit['temperature']}")
            if unit.get("ordering") is not None:
                extras.append(f"ordering={unit['ordering']}")
            extra_str = f" ({', '.join(extras)})" if extras else ""
            print(f"[{i}/{len(units)}] {key}{extra_str}")

        success, message, cost = run_execution_unit(
            unit, config, output_dir,
            dry_run=dry_run,
            limit=limit,
            timeout=timeout,
            workers_override=workers_override,
        )

        running_cost += cost

        if success:
            results["completed"].append(key)
            if verbose:
                cost_str = f" (${cost:.4f})" if cost > 0 else ""
                print(f"         Status: OK{cost_str}")
        else:
            results["failed"].append({"unit": key, "error": message})
            if verbose:
                print(f"         Status: FAILED ({message})")

        # Only update checkpoint for real (non-dry-run) executions
        # Dry runs must not modify the checkpoint — doing so corrupts
        # the resume state (see errata E24)
        if not dry_run:
            if success:
                checkpoint["completed"].append(key)
            else:
                checkpoint["failed"].append(
                    {"unit": key, "error": message}
                )
            checkpoint["total_cost_usd"] = running_cost
            save_checkpoint(checkpoint_path, checkpoint)

        # Cost warning
        if running_cost > cost_warn_threshold and not dry_run:
            print(
                f"\n  WARNING: Running cost ${running_cost:.2f} "
                f"exceeds budget threshold "
                f"${cost_warn_threshold:.2f}. "
                f"Review before continuing.\n"
            )

        if verbose:
            print()

    return results, running_cost


def _execute_units_parallel(
    units: list[dict],
    config: dict,
    output_dir: Path,
    checkpoint: dict,
    checkpoint_path: Path,
    limit: int | None,
    timeout: int,
    workers_override: int | None,
    parallel_units: int,
    running_cost: float,
    cost_warn_threshold: float,
    verbose: bool,
) -> tuple[dict, float]:
    """
    Execute units concurrently via ThreadPoolExecutor.

    Each unit's subprocess output is redirected to a per-unit log file
    under {output_dir}/logs/ to prevent interleaved terminal output.
    Checkpoint writes are protected by a threading lock.

    Returns:
        Tuple of (results dict, updated running_cost)
    """
    results: dict = {"completed": [], "failed": []}
    lock = threading.Lock()
    log_dir = output_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    completed_count = 0

    if verbose:
        print(
            f"Parallel execution: {parallel_units} units concurrently"
        )
        print(f"Per-unit logs: {log_dir}/")
        print()

    def _run_one(unit: dict) -> tuple[str, bool, str, float]:
        """Worker: execute one unit and return its result."""
        key = unit_key(unit)
        unit_log = log_dir / f"{key.replace('/', '_')}.log"
        success, message, cost = run_execution_unit(
            unit, config, output_dir,
            dry_run=False,
            limit=limit,
            timeout=timeout,
            workers_override=workers_override,
            log_file=unit_log,
        )
        return key, success, message, cost

    try:
        with ThreadPoolExecutor(
            max_workers=parallel_units
        ) as executor:
            future_to_unit = {
                executor.submit(_run_one, unit): unit
                for unit in units
            }

            for future in as_completed(future_to_unit):
                key, success, message, cost = future.result()

                with lock:
                    running_cost += cost
                    completed_count += 1

                    if success:
                        results["completed"].append(key)
                        checkpoint["completed"].append(key)
                    else:
                        results["failed"].append(
                            {"unit": key, "error": message}
                        )
                        checkpoint["failed"].append(
                            {"unit": key, "error": message}
                        )
                    checkpoint["total_cost_usd"] = running_cost
                    save_checkpoint(
                        checkpoint_path, checkpoint, lock=None
                    )

                # Print progress outside the lock
                status = "OK" if success else f"FAILED ({message})"
                cost_str = f" (${cost:.4f})" if cost > 0 else ""
                if verbose:
                    print(
                        f"[{completed_count}/{len(units)}] "
                        f"{key}: {status}{cost_str}"
                    )

                if (
                    running_cost > cost_warn_threshold
                ):
                    print(
                        f"\n  WARNING: Running cost "
                        f"${running_cost:.2f} exceeds budget.\n"
                    )

    except KeyboardInterrupt:
        print(
            "\nInterrupted. Checkpoint saved for completed units. "
            "Re-run with --resume to continue."
        )

    return results, running_cost


def main() -> None:
    """Main entry point for Phase 2 OFAT runner."""
    parser = argparse.ArgumentParser(
        description="Run Phase 2 OFAT experiments from YAML study definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full Phase 2a execution
  python scripts/run_phase2.py studies/phase2a-h1-modality.yaml

  # Dry run (validate without API calls)
  python scripts/run_phase2.py studies/phase2a-h1-modality.yaml --dry-run

  # Resume from checkpoint
  python scripts/run_phase2.py studies/phase2a-h1-modality.yaml --resume

  # Single condition, limited tiles (sanity check)
  python scripts/run_phase2.py studies/phase2a-h1-modality.yaml \\
      --condition image-only --runs 1 --limit 1

  # All conditions, 3 tiles each (small batch test)
  python scripts/run_phase2.py studies/phase2a-h1-modality.yaml \\
      --runs 1 --limit 3

  # Resume with 4 parallel units and 8 workers each
  python scripts/run_phase2.py studies/phase2a-h1-modality.yaml \\
      --resume --parallel-units 4 --workers 8
        """,
    )

    parser.add_argument(
        "study_file",
        type=Path,
        help="Path to Phase 2 study YAML file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and print commands without executing",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint, skipping completed units",
    )
    parser.add_argument(
        "--runs",
        type=int,
        help="Override number of runs per condition (default: from YAML)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Process only first N tiles per run (for sanity checks)",
    )
    parser.add_argument(
        "--condition",
        type=str,
        help="Run only this specific condition name",
    )
    parser.add_argument(
        "--workers",
        type=int,
        help="Override worker count for parallelism (default: from YAML)",
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
        help="Timeout in seconds per execution unit (default: 3600)",
    )
    parser.add_argument(
        "--parallel-units",
        type=int,
        default=1,
        help=(
            "Number of execution units to run concurrently "
            "(default: 1 = sequential)"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    results = run_phase2(
        study_path=args.study_file,
        dry_run=args.dry_run,
        resume=args.resume,
        runs=args.runs,
        limit=args.limit,
        condition_filter=args.condition,
        verbose=not args.quiet,
        timeout=args.timeout,
        workers_override=args.workers,
        parallel_units=args.parallel_units,
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
