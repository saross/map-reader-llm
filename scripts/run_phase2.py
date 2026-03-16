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
    python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml --mode batch
    python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml --reconcile

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
Version: 1.2.0
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

__version__ = "1.6.0"


# ── Token Ledger for Batch API queue management ──────────────
# The Gemini Batch API enforces an "enqueued tokens per model"
# quota (e.g. 3M tokens at Tier 1). This ledger tracks estimated
# enqueued tokens across active batch jobs so we can gate
# submissions and avoid 429 RESOURCE_EXHAUSTED errors.

# Default quota for Gemini 3 Flash Preview (Tier 1)
DEFAULT_BATCH_TOKEN_QUOTA = 3_000_000


class BatchTokenLedger:
    """Track estimated enqueued tokens across active batch jobs.

    The Gemini Batch API limits the total input tokens that can be
    enqueued across all active (PENDING + RUNNING) batch jobs for a
    given model. This ledger maintains a self-tracked estimate so
    that ``_execute_units_batch()`` can gate submissions without
    exceeding the quota.

    Token estimates are obtained via the free ``countTokens`` API
    during Phase 1 (preparation), then recorded/released as jobs
    are submitted/completed.

    Attributes:
        quota: Maximum enqueued tokens allowed.
        jobs: Dict mapping job_name → estimated_tokens.
    """

    def __init__(self, quota: int = DEFAULT_BATCH_TOKEN_QUOTA) -> None:
        self.quota = quota
        self.jobs: dict[str, int] = {}

    # Reserve 10% headroom to account for server-side propagation delay
    # when releasing tokens from completed jobs
    SAFETY_MARGIN = 0.90

    def can_submit(self, estimated_tokens: int) -> bool:
        """Check whether a new job would fit within the token quota.

        Uses a 90% safety margin to account for server-side propagation
        delay when releasing tokens from completed jobs.
        """
        effective_quota = int(self.quota * self.SAFETY_MARGIN)
        return (self.current_enqueued + estimated_tokens) <= effective_quota

    def record(self, job_name: str, estimated_tokens: int) -> None:
        """Record a newly submitted job's estimated token usage."""
        self.jobs[job_name] = estimated_tokens

    def release(self, job_name: str) -> None:
        """Release tokens when a job reaches a terminal state."""
        self.jobs.pop(job_name, None)

    @property
    def current_enqueued(self) -> int:
        """Total estimated tokens currently enqueued."""
        return sum(self.jobs.values())

    @property
    def headroom(self) -> int:
        """Remaining token capacity before hitting quota."""
        return max(0, self.quota - self.current_enqueued)

    def __repr__(self) -> str:
        return (
            f"BatchTokenLedger("
            f"enqueued={self.current_enqueued:,}/"
            f"{self.quota:,}, "
            f"jobs={len(self.jobs)})"
        )

# Resolve project root as parent of the scripts/ directory
PROJECT_ROOT = Path(__file__).parent.parent

# Ensure project root is on sys.path so that lazy imports
# (e.g. `from config import ...` in batch mode) can resolve
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _reorder_examples_for_batch(
    examples: list, ordering: str, seed: int | None = None,
) -> list:
    """Reorder examples for batch mode — mirrors reorder_examples() in
    4_detect_mounds_batch.py. Extracted here because the detection script
    cannot be imported as a Python module (numeric filename prefix).

    Args:
        examples: List of example dicts with 'category' field.
        ordering: One of 'config-default', 'canonical-first',
            'canonical-last', 'random'.
        seed: Random seed for 'random' ordering.

    Returns:
        Reordered list of examples.
    """
    import random as rand_module

    if ordering == "config-default":
        return examples

    if ordering == "canonical-first":
        canonical = [e for e in examples
                     if e.get("category", "").startswith("canonical")]
        hard = [e for e in examples
                if e.get("category", "").startswith("hard")]
        null = [e for e in examples if e.get("category") == "null"]
        return canonical + hard + null

    if ordering == "canonical-last":
        canonical = [e for e in examples
                     if e.get("category", "").startswith("canonical")]
        hard = [e for e in examples
                if e.get("category", "").startswith("hard")]
        null = [e for e in examples if e.get("category") == "null"]
        return null + hard + canonical

    if ordering == "random":
        shuffled = list(examples)
        rand_module.Random(seed).shuffle(shuffled)
        return shuffled

    return examples


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
    required_sections = ["study", "inputs", "execution"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section: {section}")

    # Validate that either 'factors' or 'conditions' is present
    if "factors" not in config and "conditions" not in config:
        raise ValueError(
            "Must have either 'factors' or 'conditions' section"
        )

    # Validate factors structure (if using OFAT format)
    if "factors" in config:
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
                "temperature": cond.get("temperature"),
                "ordering": cond.get("ordering"),
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

            # Determine overrides based on which factor is under test.
            # Factor-level values take precedence; fixed-section values
            # provide defaults for non-target parameters.
            fixed = config.get("fixed") or {}

            temperature = (
                level.get("value") if factor_name == "temperature"
                else fixed.get("temperature")
            )
            ordering = (
                level.get("value") if factor_name == "ordering"
                else fixed.get("ordering")
            )
            thinking_level = (
                level.get("value") if factor_name == "thinking_level"
                else fixed.get("thinking_level")
            )

            conditions.append({
                "name": level["name"],
                "config": config_path,
                "description": level.get("description", ""),
                "temperature": temperature,
                "ordering": ordering,
                "thinking_level": thinking_level,
            })

    return conditions


def generate_execution_units(
    conditions: list[dict],
    num_runs: int,
    seed: int = 20260205,
    random_seed_base: int | None = None,
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
        random_seed_base: Base seed for random ordering conditions. When set,
            units with ordering='random' receive a per-run seed computed as
            base + (run - 1), ensuring reproducible but distinct orderings.

    Returns:
        List of execution unit dictionaries, each containing:
        - condition_name: Name of the condition
        - run: Run number (1-indexed)
        - config: Path to config file
        - temperature: Temperature override (or None)
        - ordering: Ordering override (or None)
        - ordering_seed: Per-run seed for random ordering (or None)
    """
    units = []

    for condition in conditions:
        for run in range(1, num_runs + 1):
            # Compute per-run ordering seed for random conditions
            ordering_seed = None
            if (
                condition.get("ordering") == "random"
                and random_seed_base is not None
            ):
                ordering_seed = random_seed_base + (run - 1)

            units.append({
                "condition_name": condition["name"],
                "run": run,
                "config": condition["config"],
                "temperature": condition.get("temperature"),
                "thinking_level": condition.get("thinking_level"),
                "ordering": condition.get("ordering"),
                "ordering_seed": ordering_seed,
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


def reconcile_checkpoint(
    output_dir: Path,
    checkpoint_path: Path,
    verbose: bool = True,
) -> dict:
    """
    Rebuild checkpoint from disk, correcting drift between the
    checkpoint file and the actual output directory contents.

    Scans {output_dir}/{condition}/run_{N}/ for completed runs.
    A run is considered complete if it has a ``.meta.json`` file
    with ``items_failed <= 2``, matching the acceptance threshold
    used by the concurrent execution path (see
    ``run_execution_unit()``, line ~626).

    Runs without a ``.meta.json`` are treated as incomplete
    (e.g. the worker was killed mid-execution before writing
    metadata).

    This handles two scenarios:
      1. Runs completed on disk but missing from checkpoint (e.g.
         orchestrator killed before checkpoint write).
      2. Runs listed in checkpoint but missing or incomplete on
         disk (e.g. output directory deleted or run was partial).

    Args:
        output_dir: Base output directory containing condition
            subdirectories (e.g. outputs/phase3a/track2-text/).
        checkpoint_path: Path to the checkpoint JSON file.
        verbose: Print detailed reconciliation report.

    Returns:
        Updated checkpoint dictionary.
    """
    # Match the acceptance threshold from run_execution_unit()
    max_acceptable_failures = 2

    checkpoint = load_checkpoint(checkpoint_path)
    tracked = set(checkpoint.get("completed", []))

    # Scan disk for completed runs
    on_disk: set[str] = set()
    incomplete: list[tuple[str, str]] = []

    for condition_dir in sorted(output_dir.iterdir()):
        # Skip non-directories and metadata files
        if not condition_dir.is_dir():
            continue
        condition_name = condition_dir.name
        # Skip internal directories (logs, checkpoints, batch_working)
        if condition_name in {"logs", "checkpoints", "batch_working"}:
            continue

        for run_dir in sorted(condition_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            if not run_dir.name.startswith("run_"):
                continue

            key = f"{condition_name}/{run_dir.name}"

            # Look for any .meta.json file in the run directory
            meta_files = list(run_dir.glob("*.meta.json"))
            if not meta_files:
                incomplete.append((key, "no meta file"))
                continue

            meta_path = meta_files[0]
            items_failed = read_meta_failures(meta_path)

            if items_failed > max_acceptable_failures:
                incomplete.append(
                    (key, f"{items_failed} tiles failed")
                )
                continue

            on_disk.add(key)

    # Compute differences
    added = on_disk - tracked
    removed = tracked - on_disk

    if verbose:
        print(f"Reconcile: {output_dir}")
        print(f"  Checkpoint tracked:  {len(tracked)}")
        print(f"  Completed on disk:   {len(on_disk)}")
        print(
            f"  Acceptance threshold: "
            f"items_failed <= {max_acceptable_failures}"
        )
        if incomplete:
            print(f"  Incomplete (skipped): {len(incomplete)}")
            for key, reason in sorted(incomplete):
                print(f"    - {key} ({reason})")
        if added:
            print(f"  Added to checkpoint: {len(added)}")
            for a in sorted(added):
                print(f"    + {a}")
        if removed:
            print(f"  Removed from checkpoint: {len(removed)}")
            for r in sorted(removed):
                print(f"    - {r}")
        if not added and not removed:
            print("  Checkpoint is already consistent with disk.")

    # Update checkpoint — also clean stale batch_pending entries
    # for units now confirmed completed on disk, so that a subsequent
    # --resume doesn't try to poll already-finished jobs.
    checkpoint["completed"] = sorted(on_disk)
    batch_pending = checkpoint.get("batch_pending", {})
    stale_pending = {k for k in batch_pending if k in on_disk}
    for k in stale_pending:
        del batch_pending[k]
    if batch_pending:
        checkpoint["batch_pending"] = batch_pending
    elif "batch_pending" in checkpoint:
        del checkpoint["batch_pending"]
    save_checkpoint(checkpoint_path, checkpoint)

    if verbose and stale_pending:
        print(
            f"  Cleared stale batch_pending: {len(stale_pending)}"
        )
        for s in sorted(stale_pending):
            print(f"    ~ {s}")
    if verbose and (added or removed):
        print(
            f"  Checkpoint updated: {len(on_disk)} completed units"
        )

    return checkpoint


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

    # Add thinking level override if specified
    if unit.get("thinking_level") is not None:
        cmd.extend(["--thinking-level", str(unit["thinking_level"])])

    # Add ordering override if specified
    if unit.get("ordering") is not None:
        cmd.extend(["--ordering", str(unit["ordering"])])

    # Add ordering seed for reproducible random orderings
    if unit.get("ordering_seed") is not None:
        cmd.extend(["--ordering-seed", str(unit["ordering_seed"])])

    # Add tile size override if specified in study config
    if inputs.get("tile_size") is not None:
        cmd.extend(["--tile-size", str(inputs["tile_size"])])

    # Add tiles directory override if specified in study config
    if inputs.get("tiles_dir") is not None:
        cmd.extend(["--tiles-dir", str(PROJECT_ROOT / inputs["tiles_dir"])])

    # Add tile limit for sanity checks
    if limit and limit > 0:
        cmd.extend(["--limit", str(limit)])

    if dry_run:
        print(f"  [DRY RUN] {' '.join(cmd)}")
        return True, "dry_run", 0.0

    # Grace period (seconds) between SIGTERM and SIGKILL on timeout.
    # Gives the batch script time to finish its incremental save.
    grace_seconds = 30

    try:
        # When log_file is provided (parallel mode), redirect output
        # to avoid interleaved terminal output from concurrent units.
        # When None (sequential mode), inherit terminal for live output.
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            lf = open(log_file, "w")  # noqa: SIM115
            proc = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT),
                stdout=lf,
                stderr=subprocess.STDOUT,
                text=True,
            )
        else:
            lf = None
            proc = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT),
                stdout=None,  # inherit — stream to terminal
                stderr=None,  # inherit — stream to terminal
                text=True,
            )

        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            # Graceful shutdown: SIGTERM first so the batch script can
            # finish its incremental save, then SIGKILL if it lingers.
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=grace_seconds)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            return False, "timeout", 0.0
        finally:
            if lf:
                lf.close()

        meta_path = run_dir / f"{output_name}.meta.json"
        cost = read_meta_cost(meta_path)
        items_failed = read_meta_failures(meta_path)

        if proc.returncode == 0 and items_failed == 0:
            return True, "success", cost

        # Exit code 2 = partial failure (some tiles failed).
        # Accept runs where only a small number of tiles failed
        # (e.g. 1 tile with a known JSON parse issue out of 60).
        max_acceptable_failures = 2
        if proc.returncode in (0, 2) and items_failed <= max_acceptable_failures:
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
        return False, f"exit_code_{proc.returncode}", cost

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
    mode: str = "concurrent",
    max_batch_jobs: int = 50,
    poll_interval: int = 30,
    max_poll_hours: float = 25.0,
    token_quota: int = DEFAULT_BATCH_TOKEN_QUOTA,
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
        mode: Execution mode — 'concurrent' (default, existing pipeline
            via subprocess) or 'batch' (Gemini Batch API via
            lib_batch_api). Batch mode bypasses the subprocess model
            and rate limiter, submitting all tiles per unit as a single
            JSONL file.
        max_batch_jobs: Maximum concurrent batch API jobs in flight
            (default: 50). The Gemini Batch API supports up to 100
            concurrent jobs; this cap prevents RESOURCE_EXHAUSTED
            errors when running large experiments.
        poll_interval: Seconds between batch API poll cycles (default: 30).
            Use higher values (e.g. 3600) for overnight runs.
        max_poll_hours: Maximum hours to poll before timing out
            (default: 25). Pending jobs remain in checkpoint for
            future --resume.

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
    random_seed_base = execution.get("random_seed_base")
    units = generate_execution_units(
        conditions, num_runs, random_seed_base=random_seed_base,
    )

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

    # Cost monitoring — handle non-numeric values like "TBD"
    raw_cost = config.get("estimates", {}).get("cost_usd", 0)
    try:
        estimated_cost = float(raw_cost)
    except (TypeError, ValueError):
        estimated_cost = 0
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

    if mode == "batch":
        results, running_cost = _execute_units_batch(
            units=units,
            config=config,
            output_dir=output_dir,
            checkpoint=checkpoint,
            checkpoint_path=checkpoint_path,
            dry_run=dry_run,
            limit=limit,
            running_cost=running_cost,
            cost_warn_threshold=cost_warn_threshold,
            verbose=verbose,
            max_batch_jobs=max_batch_jobs,
            poll_interval=poll_interval,
            max_poll_hours=max_poll_hours,
            token_quota=token_quota,
        )
    elif use_parallel:
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
                ordering_str = f"ordering={unit['ordering']}"
                if unit.get("ordering_seed") is not None:
                    ordering_str += f", seed={unit['ordering_seed']}"
                extras.append(ordering_str)
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


def _execute_units_batch(
    units: list[dict],
    config: dict,
    output_dir: Path,
    checkpoint: dict,
    checkpoint_path: Path,
    dry_run: bool,
    limit: int | None,
    running_cost: float,
    cost_warn_threshold: float,
    verbose: bool,
    max_batch_jobs: int = 50,
    poll_interval: int = 30,
    max_poll_hours: float = 25.0,
    token_quota: int = DEFAULT_BATCH_TOKEN_QUOTA,
) -> tuple[dict, float]:
    """
    Execute units via the Gemini Batch API — throttled submission.

    Submits units in waves, gated by **two** constraints:

    1. **Concurrent jobs** — capped at ``max_batch_jobs`` (API limit: 100).
    2. **Enqueued tokens** — capped at ``token_quota`` (Tier 1: 3M).
       Token estimates are obtained via the free ``countTokens`` API
       during Phase 1, cached per config, and tracked by a
       :class:`BatchTokenLedger`.

    Three-phase approach:
        1. **Prepare** — Build JSONL files and estimate tokens per unit.
        2. **Submit + Poll** — Interleaved loop: submit if both job
           count and token budget allow; poll and release on completion.
        3. **Summary** — Report totals.

    Batch-pending jobs are recorded in the checkpoint immediately after
    submission (write-ahead pattern). On crash and resume, pending entries
    skip submission and go directly to polling.

    Args:
        units: List of execution unit dicts.
        config: Full study configuration.
        output_dir: Base output directory.
        checkpoint: Checkpoint dict (may contain batch_pending).
        checkpoint_path: Path to checkpoint file.
        dry_run: If True, build JSONL without submitting.
        limit: Optional tile limit per unit.
        running_cost: Accumulated cost so far.
        cost_warn_threshold: Cost warning threshold.
        verbose: Print progress information.
        max_batch_jobs: Maximum concurrent batch API jobs in flight
            (default: 50). Capped at 95 to leave headroom below the
            Batch API's hard 100-job limit.
        poll_interval: Seconds between batch API poll cycles.
        max_poll_hours: Maximum hours to poll before timing out.
        token_quota: Maximum enqueued tokens across all active batch
            jobs (default: 3,000,000 for Tier 1).

    Returns:
        Tuple of (results dict, updated running_cost).
    """
    # Lazy import — only needed in batch mode, avoids import errors
    # when google-genai batch features are not available
    from google import genai

    from config import BASE_DIR, GOOGLE_API_KEY
    from scripts.lib_batch_api import (
        cleanup_batch_files,
        complete_batch_unit,
        prepare_batch_unit,
        submit_batch_unit,
        sweep_stale_files,
    )

    results: dict = {"completed": [], "failed": []}

    if verbose:
        print(
            "Execution mode: BATCH "
            "(Gemini Batch API — parallel submission)"
        )
        print()

    # Initialise Gemini client
    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not found.")
        return (
            {
                "completed": [],
                "failed": [{"unit": "all", "error": "no_api_key"}],
            },
            running_cost,
        )

    client = genai.Client(
        api_key=GOOGLE_API_KEY,
        http_options={"api_version": "v1alpha"},
    )

    # Initialise batch_pending in checkpoint (backward-compatible)
    batch_pending = checkpoint.get("batch_pending", {})

    if batch_pending and verbose:
        print(
            f"Found {len(batch_pending)} pending batch job(s) "
            f"from previous run"
        )

    # Inject project root into config so lib_batch_api can resolve paths
    config_with_root = dict(config)
    config_with_root["_project_root"] = str(PROJECT_ROOT)

    # Cache available models for name resolution — avoids one
    # models.list() call per unit. Configs use marketing names
    # (e.g. 'gemini-3-flash') but the API may require '-preview'.
    available_models: set[str] | None = None
    try:
        available_models = {
            m.name.removeprefix("models/")
            for m in client.models.list()
        }
    except Exception as e:
        logger.warning("Could not list models for resolution: %s", e)

    # Factory for write-ahead checkpoint callbacks. Each unit gets its
    # own closure that captures the unit key and writes the batch job
    # name to the checkpoint immediately after submission — before the
    # long polling phase begins.
    def _make_on_submit(key: str):
        """Create an on_submit callback that persists job metadata."""
        def _on_submit(
            job_name: str,
            tile_keys: list[str],
            uploaded_file_name: str,
        ) -> None:
            batch_pending[key] = {
                "batch_job_name": job_name,
                "uploaded_file_name": uploaded_file_name,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "tile_count": len(tile_keys),
            }
            checkpoint["batch_pending"] = batch_pending
            save_checkpoint(checkpoint_path, checkpoint)
            logger.info(
                "Write-ahead checkpoint: persisted %s → %s "
                "(input file: %s)",
                key, job_name, uploaded_file_name,
            )
        return _on_submit

    # ── Initialise token ledger ─────────────────────────────────
    token_ledger = BatchTokenLedger(quota=token_quota)
    # Per-unit token estimates (unit_key → estimated_tokens)
    unit_token_estimates: dict[str, int] = {}
    # Cache: config_path → tokens_per_tile (avoid redundant countTokens)
    _token_cache: dict[str, int] = {}

    if verbose:
        print(f"Token quota: {token_quota:,} enqueued tokens")
        print()

    # ── Phase 1: Prepare all units (sequential, fast) ───────────
    contexts: dict = {}  # unit_key → BatchUnitContext

    # Extract optional tile parameters from study config — these are
    # study-level (not condition-level), so read once before the loop.
    # When absent, lib_batch_api defaults to TILE_SIZE=512 / TILES_DIR.
    inputs = config.get("inputs", {})
    study_tile_size = inputs.get("tile_size")       # None → use default 512
    tiles_dir_str = inputs.get("tiles_dir")         # None → use default TILES_DIR
    study_tiles_dir = (
        Path(PROJECT_ROOT / tiles_dir_str) if tiles_dir_str else None
    )

    if verbose:
        print(f"Phase 1: Preparing {len(units)} execution units...")
        if study_tile_size is not None:
            print(f"  Tile size override: {study_tile_size}")
        if study_tiles_dir is not None:
            print(f"  Tiles directory override: {study_tiles_dir}")
        print()

    for i, unit in enumerate(units, 1):
        key = unit_key(unit)

        if verbose:
            extras = []
            if unit.get("temperature") is not None:
                extras.append(f"T={unit['temperature']}")
            if unit.get("thinking_level") is not None:
                extras.append(f"thinking={unit['thinking_level']}")
            if unit.get("ordering") is not None:
                extras.append(f"ordering={unit['ordering']}")
            extra_str = f" ({', '.join(extras)})" if extras else ""
            print(f"[{i}/{len(units)}] {key}{extra_str}")

        # Load the prompt config to get system instruction and examples
        prompt_config_path = PROJECT_ROOT / unit["config"]
        try:
            with open(prompt_config_path) as f:
                prompt_config = json.load(f)
        except Exception as e:
            results["failed"].append(
                {"unit": key, "error": f"config_load: {e}"}
            )
            if verbose:
                print(f"         Status: FAILED (config load: {e})")
                print()
            continue

        # Load system instruction
        instruction_file = prompt_config.get(
            "instruction_file", "detect_image-only.md",
        )
        instruction_path = (
            Path(BASE_DIR) / "prompts" / "system-instructions"
            / instruction_file
        )
        try:
            with open(instruction_path) as f:
                system_instruction = f.read()
        except Exception as e:
            results["failed"].append(
                {"unit": key, "error": f"instruction_load: {e}"}
            )
            if verbose:
                print(
                    f"         Status: FAILED "
                    f"(instruction load: {e})"
                )
                print()
            continue

        model_name = prompt_config.get("model", "gemini-3-flash")

        # Resolve model name via cached available models list
        if available_models and model_name not in available_models:
            preview_name = f"{model_name}-preview"
            if preview_name in available_models:
                if verbose:
                    print(
                        f"  Model '{model_name}' not found; "
                        f"resolved to '{preview_name}'"
                    )
                model_name = preview_name

        config_version = prompt_config.get("version", "vX")
        examples = prompt_config.get("examples", [])

        # Apply example reordering if specified (matches real-time
        # pathway's reorder_examples() call in 4_detect_mounds_batch.py)
        ordering = unit.get("ordering")
        if ordering and ordering != "config-default" and examples:
            examples = _reorder_examples_for_batch(
                examples, ordering, unit.get("ordering_seed"),
            )
            if verbose:
                seed = unit.get("ordering_seed")
                print(f"  Reordered examples: {ordering}"
                      f"{f' (seed={seed})' if seed else ''}")

        ctx = prepare_batch_unit(
            unit=unit,
            config=config_with_root,
            output_dir=output_dir,
            model_name=model_name,
            system_instruction=system_instruction,
            examples=examples,
            config_version=config_version,
            limit=limit,
            tile_size=study_tile_size,
            tiles_dir=study_tiles_dir,
        )

        if ctx is None:
            results["failed"].append(
                {"unit": key, "error": "no_tiles_found"}
            )
            if verbose:
                print("         Status: FAILED (no tiles found)")
                print()
            continue

        if verbose:
            print(
                f"  Built JSONL: {ctx.line_count} lines "
                f"({ctx.jsonl_path})"
            )

        # Estimate tokens for this unit via countTokens (cached per config).
        # countTokens only counts TEXT tokens — image tokens use a fixed
        # rate of 258 tokens per image (for images ≤ 768×768 pixels).
        # We add image token overhead separately.
        #
        # Per-tile composition:
        #   text_tokens (from countTokens) + tile_image (258) +
        #   example_images (n × 258 if include_example_images=True)
        config_path = unit["config"]
        if config_path not in _token_cache:
            has_images = prompt_config.get(
                "include_example_images", True,
            )
            n_examples = len(examples)
            # Fixed image token overhead (258 tokens per image ≤ 768×768)
            image_tokens = (
                258  # tile image (always present)
                + (258 * n_examples if has_images else 0)
            )

            try:
                # Count TEXT tokens via the free countTokens API
                sample_parts = [system_instruction]
                for ex in examples:
                    sample_parts.append(f"Example: {ex.get('label', '')}")
                sample_parts.append("Analyse this map tile.")

                count_result = client.models.count_tokens(
                    model=model_name,
                    contents=sample_parts,
                )
                text_tokens = count_result.total_tokens
                tokens_per_tile = text_tokens + image_tokens
                _token_cache[config_path] = tokens_per_tile
                if verbose:
                    print(
                        f"  Token estimate: {tokens_per_tile:,}/tile "
                        f"(text={text_tokens:,} + "
                        f"images={image_tokens:,})"
                    )
            except Exception as e:
                # Fallback: estimate text at ~50 tokens per label + 200
                text_tokens = 50 * n_examples + 200
                tokens_per_tile = text_tokens + image_tokens
                _token_cache[config_path] = tokens_per_tile
                if verbose:
                    print(
                        f"  Token estimate: {tokens_per_tile:,}/tile "
                        f"(fallback; countTokens failed: {e})"
                    )
        else:
            tokens_per_tile = _token_cache[config_path]

        estimated_tokens = tokens_per_tile * ctx.line_count
        unit_token_estimates[key] = estimated_tokens

        if verbose:
            print(
                f"  Unit total: {estimated_tokens:,} tokens "
                f"({ctx.line_count} tiles × "
                f"{tokens_per_tile:,}/tile)"
            )

        if dry_run:
            if verbose:
                print(
                    f"  [DRY RUN] Would submit batch job for "
                    f"{ctx.line_count} tiles"
                )
                print("         Status: OK")
                print()
            results["completed"].append(key)
            continue

        contexts[key] = ctx

        if verbose:
            print()

    # If dry_run or nothing to submit, return early
    if dry_run or not contexts:
        if dry_run and verbose and unit_token_estimates:
            total_est = sum(unit_token_estimates.values())
            print(
                f"\n  Total estimated tokens: {total_est:,} "
                f"(quota: {token_quota:,}, "
                f"max concurrent: "
                f"{token_quota // max(unit_token_estimates.values()):,} "
                f"jobs)"
            )
        return results, running_cost

    # ── Phase 2: Throttled submit + poll loop ─────────────────
    # Interleaves submission and polling to keep in-flight jobs
    # at or below max_batch_jobs. This replaces the old
    # "submit all, then poll all" pattern that could exceed the
    # Batch API's 100-concurrent-job limit.

    # Hard-cap at 95 to leave headroom below the API's 100 limit
    effective_cap = min(max_batch_jobs, 95)

    # Separate already-pending (from resume) vs new submissions
    already_pending_keys: list[str] = []
    submission_queue: list[str] = []  # keys to submit, in order

    for key in contexts:
        if key in batch_pending:
            already_pending_keys.append(key)
        else:
            submission_queue.append(key)

    # Track all in-flight jobs: unit_key → job_name
    in_flight: dict[str, str] = {}

    # Re-register already-pending jobs (skip submission, go to poll)
    for key in already_pending_keys:
        job_name = batch_pending[key]["batch_job_name"]
        in_flight[key] = job_name
        if verbose:
            print(f"  {key}: resuming pending job {job_name}")

    total_units = len(contexts)
    n_submitted = len(already_pending_keys)
    n_completed = 0  # completed + failed (terminal)

    if verbose:
        print(
            f"Phase 2: {len(submission_queue)} new job(s) to "
            f"submit, {len(already_pending_keys)} already "
            f"pending (cap: {effective_cap} concurrent)"
        )
        print()

    # Retry settings for transient submission failures
    max_submit_retries = 4
    # Delay between consecutive submissions to avoid burst-submitting
    # faster than the server releases quota (seconds)
    submit_spacing_seconds = 3

    def _submit_one(key: str) -> bool:
        """Submit a single unit with retry/backoff. Returns True on success."""
        ctx = contexts[key]
        est_tokens = unit_token_estimates.get(key, 0)
        for attempt in range(max_submit_retries):
            try:
                job_name, _uploaded = submit_batch_unit(
                    ctx, client, _make_on_submit(key),
                )
                in_flight[key] = job_name
                token_ledger.record(job_name, est_tokens)
                return True
            except Exception as e:
                err_str = str(e)
                is_retryable = (
                    "RESOURCE_EXHAUSTED" in err_str
                    or "429" in err_str
                    or "file_storage_bytes" in err_str
                )
                if is_retryable and attempt < max_submit_retries - 1:
                    # Backoff: 10s, 30s, 60s
                    backoff = [10, 30, 60][
                        min(attempt, 2)
                    ]
                    if "file_storage_bytes" in err_str:
                        # Storage quota — sweep orphaned files
                        if verbose:
                            print(
                                f"  {key}: storage quota hit "
                                f"(attempt {attempt + 1}/"
                                f"{max_submit_retries}), "
                                f"sweeping stale files..."
                            )
                        active = {
                            v["uploaded_file_name"]
                            for v in batch_pending.values()
                            if "uploaded_file_name" in v
                        }
                        swept, freed = sweep_stale_files(
                            client, active,
                        )
                        if verbose:
                            print(
                                f"  Swept {swept} stale files "
                                f"({freed:.2f} GB freed)"
                            )
                    else:
                        if verbose:
                            print(
                                f"  {key}: quota exceeded "
                                f"(attempt {attempt + 1}/"
                                f"{max_submit_retries}), "
                                f"backing off {backoff}s..."
                            )
                    time.sleep(backoff)
                    continue
                # Non-retryable error or retries exhausted
                results["failed"].append(
                    {"unit": key, "error": f"submit: {e}"}
                )
                if verbose:
                    print(f"  {key}: FAILED (submit: {e})")
                return False
        return False

    def _handle_completion(
        key: str, job_name: str, batch_job: object,
    ) -> None:
        """Process a completed batch job and update checkpoint.

        Exceptions from ``complete_batch_unit()`` (e.g. rasterio
        I/O errors, filesystem permission errors) are caught and
        recorded as failures rather than propagated — this prevents
        a single unit's processing error from killing the polling
        loop for all remaining jobs.
        """
        nonlocal running_cost, n_completed
        ctx = contexts[key]
        try:
            success, message, cost = complete_batch_unit(
                ctx, client, batch_job,
            )
        except Exception as e:
            logger.error(
                "Unhandled error processing %s: %s", key, e,
                exc_info=True,
            )
            success, message, cost = (
                False, f"processing_error: {e}", 0.0,
            )
        running_cost += cost

        # Clean up Files API storage — delete input and output
        # files now that results are downloaded locally. Errors
        # are logged but do not affect completion status; files
        # auto-expire after 48h as a fallback.
        files_to_delete: list[str] = []
        pending_info = batch_pending.get(key, {})
        uploaded_name = pending_info.get(
            "uploaded_file_name", "",
        )
        if uploaded_name:
            files_to_delete.append(uploaded_name)
        # Output file from the completed batch job
        try:
            output_file_name = batch_job.dest.file_name
            if output_file_name:
                files_to_delete.append(output_file_name)
        except (AttributeError, TypeError):
            pass  # No output file (job failed before producing)
        if files_to_delete:
            deleted, errors = cleanup_batch_files(
                client, files_to_delete, label=key,
            )
            if verbose and (deleted or errors):
                print(
                    f"    Cleaned up {deleted} file(s)"
                    + (
                        f" ({errors} errors)"
                        if errors else ""
                    )
                )

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

        # Remove from pending/in-flight, release tokens, persist checkpoint
        job_name_for_release = in_flight.get(key)
        if job_name_for_release:
            token_ledger.release(job_name_for_release)
        batch_pending.pop(key, None)
        in_flight.pop(key, None)
        n_completed += 1
        checkpoint["batch_pending"] = batch_pending
        checkpoint["total_cost_usd"] = running_cost
        save_checkpoint(checkpoint_path, checkpoint)

        if verbose:
            status = "OK" if success else f"FAILED ({message})"
            cost_str = f" (${cost:.4f})" if cost > 0 else ""
            print(
                f"  [{n_completed}/{total_units}] {key}: "
                f"{status}{cost_str}"
            )

        if running_cost > cost_warn_threshold:
            print(
                f"\n  WARNING: Running cost "
                f"${running_cost:.2f} exceeds budget "
                f"threshold "
                f"${cost_warn_threshold:.2f}.\n"
            )

    # ── Initial submission wave ───────────────────────────────
    # Fill up to effective_cap, gated by both job count and token budget.
    # Space submissions to avoid burst-submitting faster than the
    # server can process quota changes.
    initial_submitted = 0
    while submission_queue:
        if len(in_flight) >= effective_cap:
            break  # Job count limit
        next_key = submission_queue[0]
        est = unit_token_estimates.get(next_key, 0)
        if not token_ledger.can_submit(est) and len(in_flight) > 0:
            break  # Token budget full (but always allow at least 1 job)
        submission_queue.pop(0)
        if _submit_one(next_key):
            n_submitted += 1
            initial_submitted += 1
            # Brief pause between submissions
            if submission_queue:
                time.sleep(submit_spacing_seconds)

    if verbose and initial_submitted:
        print(
            f"  Submitted initial wave: {initial_submitted} "
            f"job(s), {len(in_flight)} in flight, "
            f"{len(submission_queue)} queued"
        )
        print(f"  {token_ledger}")
        print()

    # ── Interleaved poll + submit loop ────────────────────────
    # Poll in-flight jobs; as they complete, submit more from
    # the queue until all units are processed.

    max_seconds = max_poll_hours * 3600
    loop_start = time.monotonic()

    try:
        while in_flight or submission_queue:
            # Poll each in-flight job once per cycle
            for key, job_name in list(in_flight.items()):
                try:
                    job = client.batches.get(name=job_name)
                except Exception as e:
                    logger.warning(
                        "Transient error polling %s (%s), "
                        "will retry: %s",
                        job_name, key, e,
                    )
                    continue

                state_name = getattr(
                    job.state, "name",
                    str(job.state),
                ).upper()

                terminal_states = {
                    "JOB_STATE_SUCCEEDED",
                    "JOB_STATE_FAILED",
                    "JOB_STATE_CANCELLED",
                    "SUCCEEDED", "FAILED", "CANCELLED",
                }

                if state_name in terminal_states:
                    logger.info(
                        "Batch job %s (%s) reached: %s",
                        job_name, key, state_name,
                    )
                    _handle_completion(key, job_name, job)

            # Submit more if both job count and token budget allow
            newly_submitted = 0
            while submission_queue and len(in_flight) < effective_cap:
                next_key = submission_queue[0]
                est = unit_token_estimates.get(next_key, 0)
                if (
                    not token_ledger.can_submit(est)
                    and len(in_flight) > 0
                ):
                    break  # Token budget full
                submission_queue.pop(0)
                if _submit_one(next_key):
                    n_submitted += 1
                    newly_submitted += 1
                    # Brief pause between submissions
                    if submission_queue:
                        time.sleep(submit_spacing_seconds)

            if verbose and newly_submitted > 0:
                print(
                    f"  Submitted {newly_submitted} more "
                    f"job(s), {len(in_flight)} in flight, "
                    f"{len(submission_queue)} queued "
                    f"({token_ledger})"
                )

            # Exit if nothing left to process
            if not in_flight and not submission_queue:
                break

            # Progress report
            elapsed = time.monotonic() - loop_start
            if verbose:
                hours = elapsed / 3600
                print(
                    f"  ... {n_completed}/{total_units} "
                    f"complete, {len(in_flight)} in flight, "
                    f"{len(submission_queue)} queued "
                    f"({hours:.1f}h elapsed) "
                    f"[tokens: {token_ledger.current_enqueued:,}"
                    f"/{token_ledger.quota:,}]",
                    flush=True,
                )

            # Timeout check
            if elapsed >= max_seconds:
                pending_keys = list(in_flight.keys())
                raise TimeoutError(
                    f"{len(in_flight)} batch job(s) did not "
                    f"complete within {max_poll_hours} hours: "
                    f"{pending_keys[:5]}"
                )

            # Sleep before next poll cycle
            remaining = max_seconds - elapsed
            sleep_time = min(poll_interval, remaining)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except TimeoutError as e:
        if verbose:
            print(f"\n  TIMEOUT: {e}")
            print(
                "  Remaining jobs saved in checkpoint for "
                "future --resume"
            )
        checkpoint["batch_pending"] = batch_pending
        save_checkpoint(checkpoint_path, checkpoint)
    except KeyboardInterrupt:
        print(
            "\nInterrupted. Checkpoint saved for completed "
            "jobs. Re-run with --resume to continue polling "
            "remaining batch jobs."
        )
        checkpoint["batch_pending"] = batch_pending
        save_checkpoint(checkpoint_path, checkpoint)

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

  # Batch mode (Gemini Batch API — 50%% cost reduction)
  python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml \\
      --mode batch

  # Batch mode: overnight with conservative concurrency
  python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml \\
      --mode batch --max-batch-jobs 30 --poll-interval 3600

  # Batch mode: quick status check (poll once, then exit)
  python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml \\
      --mode batch --resume --max-poll-hours 0.01

  # Reconcile checkpoint with disk (no API calls)
  python scripts/run_phase2.py studies/phase3a-h3-voting-track1.yaml \\
      --reconcile
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
        "--mode",
        type=str,
        choices=["batch", "concurrent"],
        default="concurrent",
        help=(
            "Execution mode: 'concurrent' (default, per-tile via "
            "subprocess) or 'batch' (Gemini Batch API, 50%% cost "
            "reduction)"
        ),
    )
    parser.add_argument(
        "--max-batch-jobs",
        type=int,
        default=50,
        help=(
            "Maximum concurrent batch API jobs in flight "
            "(default: 50). The Gemini Batch API supports up to "
            "100 concurrent jobs; this cap prevents "
            "RESOURCE_EXHAUSTED errors when running large "
            "experiments. Set lower for safety margin, higher "
            "for throughput."
        ),
    )
    parser.add_argument(
        "--token-quota",
        type=int,
        default=DEFAULT_BATCH_TOKEN_QUOTA,
        help=(
            "Maximum enqueued tokens across all active batch "
            f"jobs (default: {DEFAULT_BATCH_TOKEN_QUOTA:,}). "
            "Tier 1 = 3M, Tier 2 = 400M. The ledger gates "
            "submissions to stay within this limit, avoiding "
            "429 RESOURCE_EXHAUSTED errors from the enqueued "
            "tokens quota."
        ),
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help=(
            "Seconds between batch API poll cycles (default: 30). "
            "Use higher values (e.g. 3600) for overnight runs."
        ),
    )
    parser.add_argument(
        "--max-poll-hours",
        type=float,
        default=25.0,
        help=(
            "Maximum hours to poll before timing out (default: 25). "
            "Pending jobs remain in checkpoint for future --resume."
        ),
    )
    parser.add_argument(
        "--reconcile",
        action="store_true",
        help=(
            "Scan the output directory and rebuild the checkpoint "
            "from disk. Corrects drift when runs completed outside "
            "the orchestrator or after a process crash. Does not "
            "execute any API calls."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # --reconcile: rebuild checkpoint from disk and exit
    if args.reconcile:
        config = load_study_config(args.study_file)
        output_dir = PROJECT_ROOT / config["execution"]["output_dir"]
        checkpoint_path = output_dir / "checkpoint.json"
        if not output_dir.exists():
            print(f"ERROR: Output directory does not exist: {output_dir}")
            sys.exit(1)
        reconcile_checkpoint(
            output_dir=output_dir,
            checkpoint_path=checkpoint_path,
            verbose=not args.quiet,
        )
        sys.exit(0)

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
        mode=args.mode,
        max_batch_jobs=args.max_batch_jobs,
        poll_interval=args.poll_interval,
        max_poll_hours=args.max_poll_hours,
        token_quota=args.token_quota,
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
