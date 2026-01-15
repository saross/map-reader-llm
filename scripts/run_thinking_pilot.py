#!/usr/bin/env python3
"""
Thinking Level Calibration Pilot Runner
========================================

Runs the thinking level pilot to determine optimal reasoning depth for
Gemini 3 before the main experiment. Executes 30 detection runs:
3 thinking levels × 10 replications.

Uses parallel execution (default 10 concurrent) with exponential backoff
on API rate limits.

Usage:
    python scripts/run_thinking_pilot.py
    python scripts/run_thinking_pilot.py --dry-run
    python scripts/run_thinking_pilot.py --parallel 5
    python scripts/run_thinking_pilot.py --resume

Outputs:
    outputs/results/pilot_thinking-{level}/
        pilot_thinking-{level}_run{01-10}.geojson
        pilot_thinking-{level}_run{01-10}.meta.json

Author: Shawn Ross, Claude Code
Version: 1.0.0
Licence: Apache 2.0
"""

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

# Script version
__version__ = "1.0.0"

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Pilot configuration
CONFIGS = [
    "pilot_thinking-minimal.json",
    "pilot_thinking-low.json",
    "pilot_thinking-high.json",
]
K_RUNS = 10  # Replications per condition
MANIFEST = "inputs/tiles/calibration_manifest.json"

# Default parallelism (safe for Gemini API)
DEFAULT_PARALLEL = 10

# Backoff configuration for rate limits
INITIAL_BACKOFF_SECONDS = 5
MAX_BACKOFF_SECONDS = 120
BACKOFF_MULTIPLIER = 2


class RunSpec(NamedTuple):
    """Specification for a single detection run."""

    config_file: str
    thinking_level: str
    run_number: int
    output_name: str


def generate_run_specs() -> list[RunSpec]:
    """
    Generate all run specifications for the pilot.

    Returns:
        List of 30 RunSpec objects (3 configs × 10 runs)
    """
    specs = []
    for config_file in CONFIGS:
        # Extract thinking level from config filename
        # e.g., "pilot_thinking-minimal.json" -> "minimal"
        thinking_level = config_file.replace("pilot_thinking-", "").replace(".json", "")

        for run_num in range(1, K_RUNS + 1):
            output_name = f"pilot_thinking-{thinking_level}_run{run_num:02d}"
            specs.append(
                RunSpec(
                    config_file=config_file,
                    thinking_level=thinking_level,
                    run_number=run_num,
                    output_name=output_name,
                )
            )

    return specs


def run_detection(spec: RunSpec, dry_run: bool = False) -> tuple[RunSpec, bool, str]:
    """
    Execute a single detection run with exponential backoff.

    Args:
        spec: RunSpec defining the run parameters
        dry_run: If True, print command without executing

    Returns:
        Tuple of (spec, success, message)
    """
    config_path = PROJECT_ROOT / "prompts" / "configs" / spec.config_file
    manifest_path = PROJECT_ROOT / MANIFEST

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "4_detect_mounds_batch.py"),
        "--config",
        str(config_path),
        "--manifest",
        str(manifest_path),
        "--output",
        spec.output_name,
    ]

    if dry_run:
        return spec, True, f"[DRY RUN] {' '.join(cmd)}"

    # Retry loop with exponential backoff
    backoff = INITIAL_BACKOFF_SECONDS
    max_retries = 5

    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute timeout per run
            )

            if result.returncode == 0:
                return spec, True, "success"

            # Check for rate limit errors (429 or quota exceeded)
            error_output = (result.stderr or "") + (result.stdout or "")
            if "429" in error_output or "quota" in error_output.lower():
                if attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff = min(backoff * BACKOFF_MULTIPLIER, MAX_BACKOFF_SECONDS)
                    continue

            # Other error - don't retry
            error_msg = result.stderr[:300] if result.stderr else "Unknown error"
            return spec, False, f"exit_code_{result.returncode}: {error_msg}"

        except subprocess.TimeoutExpired:
            return spec, False, "timeout"
        except Exception as e:
            return spec, False, f"exception: {str(e)}"

    return spec, False, "max_retries_exceeded"


def load_checkpoint(checkpoint_path: Path) -> set[str]:
    """
    Load set of completed output names from checkpoint.

    Args:
        checkpoint_path: Path to checkpoint JSON file

    Returns:
        Set of completed output names
    """
    if checkpoint_path.exists():
        with open(checkpoint_path, "r") as f:
            data = json.load(f)
            return set(data.get("completed", []))
    return set()


def save_checkpoint(checkpoint_path: Path, completed: set[str], failed: list[dict]) -> None:
    """
    Save checkpoint to file.

    Args:
        checkpoint_path: Path to checkpoint JSON file
        completed: Set of completed output names
        failed: List of failed run details
    """
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "completed": sorted(completed),
        "failed": failed,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    with open(checkpoint_path, "w") as f:
        json.dump(checkpoint, f, indent=2)


def run_pilot(
    parallel: int = DEFAULT_PARALLEL,
    dry_run: bool = False,
    resume: bool = False,
    verbose: bool = True,
) -> dict:
    """
    Execute the thinking level pilot.

    Args:
        parallel: Number of concurrent workers
        dry_run: If True, print commands without executing
        resume: If True, skip already-completed runs
        verbose: If True, print progress information

    Returns:
        Summary dictionary with results
    """
    # Generate all run specifications
    all_specs = generate_run_specs()

    if verbose:
        print("=" * 70)
        print("Thinking Level Calibration Pilot")
        print("=" * 70)
        print(f"Conditions: {len(CONFIGS)} thinking levels")
        print(f"Replications: {K_RUNS} runs per condition")
        print(f"Total runs: {len(all_specs)}")
        print(f"Parallel workers: {parallel}")
        print(f"Manifest: {MANIFEST}")
        print("=" * 70)
        print()

    # Set up output directory and checkpoint
    output_dir = PROJECT_ROOT / "outputs" / "results"
    checkpoint_path = output_dir / "pilot_thinking_checkpoint.json"

    completed = set()
    failed = []

    # Handle resume
    if resume:
        completed = load_checkpoint(checkpoint_path)
        if verbose and completed:
            print(f"Resuming: {len(completed)} runs already completed")

    # Filter to pending runs
    pending_specs = [s for s in all_specs if s.output_name not in completed]

    if not pending_specs:
        if verbose:
            print("All runs already completed!")
        return {"completed": len(completed), "failed": 0, "skipped": len(all_specs)}

    if verbose:
        print(f"Pending runs: {len(pending_specs)}")
        print()

    # Execute with parallel workers
    results = {"completed": [], "failed": [], "skipped": list(completed)}
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=parallel) as executor:
        # Submit all jobs
        futures = {
            executor.submit(run_detection, spec, dry_run): spec for spec in pending_specs
        }

        # Process as they complete
        for i, future in enumerate(as_completed(futures), 1):
            spec, success, message = future.result()

            if success:
                completed.add(spec.output_name)
                results["completed"].append(spec.output_name)
                if verbose:
                    print(f"[{i}/{len(pending_specs)}] {spec.output_name}: OK")
            else:
                failed.append({"run": spec.output_name, "error": message})
                results["failed"].append({"run": spec.output_name, "error": message})
                if verbose:
                    print(f"[{i}/{len(pending_specs)}] {spec.output_name}: FAILED - {message}")

            # Checkpoint every 5 completions
            if i % 5 == 0:
                save_checkpoint(checkpoint_path, completed, failed)

    # Final checkpoint
    save_checkpoint(checkpoint_path, completed, failed)

    # Summary
    elapsed = time.time() - start_time
    if verbose:
        print()
        print("=" * 70)
        print("Pilot Complete")
        print("=" * 70)
        print(f"Completed: {len(results['completed'])}")
        print(f"Failed: {len(results['failed'])}")
        print(f"Previously completed: {len(results['skipped'])}")
        print(f"Elapsed time: {elapsed:.1f}s")
        print(f"Checkpoint: {checkpoint_path}")
        print()

    return results


def main():
    """Main entry point for thinking pilot runner."""
    parser = argparse.ArgumentParser(
        description="Run thinking level calibration pilot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pilot with default parallelism (10)
  python scripts/run_thinking_pilot.py

  # Dry run (show commands without executing)
  python scripts/run_thinking_pilot.py --dry-run

  # Run with 5 parallel workers
  python scripts/run_thinking_pilot.py --parallel 5

  # Resume from checkpoint
  python scripts/run_thinking_pilot.py --resume
        """,
    )

    parser.add_argument(
        "--parallel",
        type=int,
        default=DEFAULT_PARALLEL,
        help=f"Number of parallel workers (default: {DEFAULT_PARALLEL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint, skipping completed runs",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    results = run_pilot(
        parallel=args.parallel,
        dry_run=args.dry_run,
        resume=args.resume,
        verbose=not args.quiet,
    )

    # Exit code based on results
    if results.get("failed"):
        sys.exit(2)  # Partial failure
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
