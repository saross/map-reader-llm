#!/usr/bin/env python3
"""
Batch Job Monitor
=================

Standalone monitoring tool for Gemini Batch API jobs. Reads checkpoint
state and queries the Batch API to report job progress without running
the full pipeline.

This script is read-only — it never modifies the checkpoint or submits
new jobs. The sole exception is ``--auto-resume``, which exec's the
full pipeline as a subprocess when all pending jobs are terminal.

Usage:
    # One-shot status check
    python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml

    # Continuous monitoring (default: check every hour)
    python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml --watch

    # Custom interval (every 30 minutes)
    python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml \\
        --watch --interval 1800

    # Auto-trigger pipeline when all jobs complete
    python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml \\
        --watch --auto-resume

    # Machine-readable output
    python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml --json

Inputs:
    - Study definition YAML file (for output_dir and study metadata)
    - Checkpoint JSON file (for completed/pending unit state)
    - Gemini Batch API (for live job status queries)

Rate Limit Safety:
    Each check queries ``batches.get()`` once per pending job. With
    70 jobs at ~200ms each, one check takes ~14s. At the default
    3600s watch interval, this is ~1 Request Per Minute (RPM) for
    ``batches.get()`` — well within API limits.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Resolve project root as parent of the scripts/ directory
PROJECT_ROOT = Path(__file__).parent.parent

# Ensure project root is on sys.path for imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

__version__ = "1.0.0"


def _load_checkpoint(checkpoint_path: Path) -> dict:
    """
    Load checkpoint file if it exists.

    Args:
        checkpoint_path: Path to checkpoint JSON file.

    Returns:
        Checkpoint dictionary, or empty defaults if file missing.
    """
    if checkpoint_path.exists():
        with open(checkpoint_path) as f:
            return json.load(f)
    return {
        "completed": [],
        "failed": [],
        "batch_pending": {},
        "total_cost_usd": 0.0,
    }


def _parse_condition(unit_key: str) -> str:
    """
    Extract the condition name from a unit key.

    Args:
        unit_key: Key in format "condition_name/run_N".

    Returns:
        Condition name (e.g. "T0.3" from "T0.3/run_11").
    """
    return unit_key.split("/")[0]


def _format_elapsed(submitted_at: str) -> str:
    """
    Format the elapsed time since a submission timestamp.

    Args:
        submitted_at: ISO 8601 timestamp string.

    Returns:
        Human-readable elapsed time (e.g. "12.3h" or "45m").
    """
    try:
        submitted = datetime.fromisoformat(submitted_at)
        now = datetime.now(timezone.utc)
        elapsed = now - submitted
        hours = elapsed.total_seconds() / 3600
        if hours >= 1.0:
            return f"{hours:.1f}h"
        minutes = elapsed.total_seconds() / 60
        return f"{minutes:.0f}m"
    except (ValueError, TypeError):
        return "unknown"


def _query_batch_statuses(
    batch_pending: dict,
) -> dict[str, dict]:
    """
    Query the Batch API for current status of all pending jobs.

    Initialises a Gemini client and queries ``batches.get()`` for
    each pending job. Transient errors are logged and the job is
    reported with state "QUERY_ERROR".

    Args:
        batch_pending: Dict of unit_key → pending info (containing
            ``batch_job_name``).

    Returns:
        Dict of unit_key → status info dict with keys:
        - ``state``: Job state string (e.g. "JOB_STATE_SUCCEEDED")
        - ``batch_job_name``: The batch job resource name
        - ``submitted_at``: Original submission timestamp
        - ``tile_count``: Number of tiles in the job
    """
    # Lazy imports — only needed when querying API
    from google import genai

    from config import GOOGLE_API_KEY

    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not found in environment.")
        sys.exit(1)

    client = genai.Client(
        api_key=GOOGLE_API_KEY,
        http_options={"api_version": "v1alpha"},
    )

    statuses: dict[str, dict] = {}

    for key, info in batch_pending.items():
        job_name = info["batch_job_name"]
        try:
            job = client.batches.get(name=job_name)
            # Extract state name from enum or string
            state = (
                job.state.name
                if hasattr(job.state, "name")
                else str(job.state)
            )
        except Exception as e:
            print(f"  Warning: error querying {key} ({job_name}): {e}")
            state = "QUERY_ERROR"

        statuses[key] = {
            "state": state,
            "batch_job_name": job_name,
            "submitted_at": info.get("submitted_at", ""),
            "tile_count": info.get("tile_count", 0),
        }

    return statuses


def _is_terminal(state: str) -> bool:
    """Check if a batch job state is terminal."""
    return state in {
        "JOB_STATE_SUCCEEDED",
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_EXPIRED",
        "JOB_STATE_PARTIALLY_SUCCEEDED",
    }


def check_status(
    study_path: Path,
    output_json: bool = False,
) -> dict:
    """
    Perform a one-shot status check of all batch jobs.

    Reads the study YAML and checkpoint, queries the Batch API for
    pending jobs, and reports a summary.

    Args:
        study_path: Path to the study YAML file.
        output_json: If True, output machine-readable JSON instead
            of human-readable text.

    Returns:
        Status summary dict (also used for JSON output).
    """
    # Import study config loader from run_phase2
    from scripts.run_phase2 import load_study_config

    config = load_study_config(study_path)
    study_info = config["study"]
    execution = config["execution"]
    output_dir = PROJECT_ROOT / execution["output_dir"]
    checkpoint_path = output_dir / "checkpoint.json"

    # Load checkpoint
    checkpoint = _load_checkpoint(checkpoint_path)
    completed = checkpoint.get("completed", [])
    failed = checkpoint.get("failed", [])
    batch_pending = checkpoint.get("batch_pending", {})

    # Total units from study config
    num_runs = execution.get("runs", 10)
    # Count conditions from factors
    factors = config.get("factors", {})
    num_conditions = sum(
        len(f.get("levels", []))
        for f in factors.values()
    )
    # Fallback: count from pre-enumerated conditions
    if num_conditions == 0 and "conditions" in config:
        num_conditions = len([
            c for c in config["conditions"]
            if not c.get("reuse_from") and c.get("run") is not False
        ])
    total_units = num_conditions * num_runs

    # Query API for pending job statuses
    statuses: dict[str, dict] = {}
    if batch_pending:
        statuses = _query_batch_statuses(batch_pending)

    # Build per-condition progress
    condition_progress: dict[str, dict] = {}
    for key in completed:
        cond = _parse_condition(key)
        if cond not in condition_progress:
            condition_progress[cond] = {
                "completed": 0, "pending": 0,
                "states": Counter(),
            }
        condition_progress[cond]["completed"] += 1

    for key, status in statuses.items():
        cond = _parse_condition(key)
        if cond not in condition_progress:
            condition_progress[cond] = {
                "completed": 0, "pending": 0,
                "states": Counter(),
            }
        condition_progress[cond]["pending"] += 1
        condition_progress[cond]["states"][status["state"]] += 1

    # Aggregate state counts
    state_counts: Counter = Counter()
    for status in statuses.values():
        state_counts[status["state"]] += 1

    # Compute submission time range
    submission_times = [
        s.get("submitted_at", "")
        for s in statuses.values()
        if s.get("submitted_at")
    ]
    oldest_elapsed = ""
    newest_elapsed = ""
    if submission_times:
        oldest_elapsed = _format_elapsed(min(submission_times))
        newest_elapsed = _format_elapsed(max(submission_times))

    # All pending jobs terminal?
    all_terminal = all(
        _is_terminal(s["state"]) for s in statuses.values()
    ) if statuses else (len(batch_pending) == 0)

    # Build summary
    summary = {
        "study_name": study_info.get("name", "Unknown"),
        "checkpoint_path": str(checkpoint_path),
        "total_units": total_units,
        "completed": len(completed),
        "failed": len(failed),
        "pending": len(batch_pending),
        "state_counts": dict(state_counts),
        "condition_progress": {
            cond: {
                "completed": info["completed"],
                "pending": info["pending"],
                "total": num_runs,
                "states": dict(info["states"]),
            }
            for cond, info in sorted(condition_progress.items())
        },
        "oldest_submission": oldest_elapsed,
        "newest_submission": newest_elapsed,
        "all_terminal": all_terminal,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if output_json:
        print(json.dumps(summary, indent=2))
    else:
        _print_status(summary)

    return summary


def _print_status(summary: dict) -> None:
    """
    Print a human-readable status report.

    Args:
        summary: Status summary dict from ``check_status()``.
    """
    print(f"Batch Monitor: {summary['study_name']}")
    print(f"Checkpoint: {summary['checkpoint_path']}")
    print("\u2500" * 50)
    print()

    total = summary["total_units"]
    completed = summary["completed"]
    failed = summary["failed"]
    pending = summary["pending"]

    print(f"Completed:  {completed} / {total} units")
    if failed:
        print(f"Failed:     {failed}")
    if pending > 0:
        print(f"Pending:    {pending} batch job(s)")
    else:
        print("Pending:    0 (all done)")
    print()

    # State breakdown
    state_counts = summary.get("state_counts", {})
    if state_counts:
        print("Status breakdown:")
        for state, count in sorted(state_counts.items()):
            # Trim "JOB_STATE_" prefix for readability
            short = state.replace("JOB_STATE_", "")
            print(f"  {short:<20s} {count}")
        print()

    # Per-condition progress
    condition_progress = summary.get("condition_progress", {})
    if condition_progress:
        print("Per-condition progress:")
        for cond, info in condition_progress.items():
            cond_total = info.get("total", "?")
            cond_done = info["completed"]
            cond_pending = info["pending"]
            parts = [f"{cond_done}/{cond_total} completed"]
            if cond_pending > 0:
                parts.append(f"{cond_pending} pending")
            print(f"  {cond:<8s} {', '.join(parts)}")
        print()

    # Submission timing
    oldest = summary.get("oldest_submission", "")
    newest = summary.get("newest_submission", "")
    if oldest:
        print(f"Oldest submission: {oldest} ago")
    if newest:
        print(f"Newest submission: {newest} ago")
    if oldest:
        print()

    if summary.get("all_terminal"):
        if pending > 0:
            print(
                "All pending jobs have reached terminal states. "
                "Run with --auto-resume to trigger result download."
            )
        else:
            remaining = total - completed
            if remaining > 0:
                print(
                    f"{remaining} unit(s) not yet submitted. "
                    f"Run the pipeline with --mode batch to submit."
                )
            else:
                print("All units complete.")


def watch_loop(
    study_path: Path,
    interval: int = 3600,
    auto_resume: bool = False,
    output_json: bool = False,
) -> None:
    """
    Continuously monitor batch job status.

    Loops with ``time.sleep(interval)`` between checks. If
    ``auto_resume`` is True and all pending jobs reach terminal
    states, triggers the pipeline to download results.

    Args:
        study_path: Path to the study YAML file.
        interval: Seconds between status checks.
        auto_resume: If True, trigger pipeline when all jobs are
            terminal.
        output_json: If True, output JSON on each cycle.
    """
    cycle = 0
    try:
        while True:
            cycle += 1
            if not output_json:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n{'=' * 50}")
                print(f"Monitor cycle {cycle} — {now}")
                print(f"{'=' * 50}\n")

            summary = check_status(study_path, output_json=output_json)

            # Check if we should auto-resume
            if (
                auto_resume
                and summary.get("all_terminal")
                and summary.get("pending", 0) > 0
            ):
                if not output_json:
                    print()
                    print(
                        "All pending jobs are terminal. "
                        "Triggering pipeline resume..."
                    )
                    print()

                # Trigger the pipeline to download results
                cmd = [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "run_phase2.py"),
                    str(study_path),
                    "--mode", "batch",
                    "--resume",
                ]
                if not output_json:
                    print(f"Running: {' '.join(cmd)}")
                subprocess.run(cmd, cwd=str(PROJECT_ROOT))
                return

            # All done — no pending jobs remain
            if summary.get("pending", 0) == 0:
                if not output_json:
                    print("\nNo pending jobs to monitor. Exiting.")
                return

            if not output_json:
                next_time = datetime.fromtimestamp(
                    time.time() + interval
                ).strftime("%H:%M:%S")
                print(
                    f"Next check in {interval}s (at {next_time}). "
                    f"Press Ctrl+C to stop."
                )
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nMonitor stopped.")


def main() -> None:
    """Main entry point for the batch monitor."""
    parser = argparse.ArgumentParser(
        description=(
            "Monitor Gemini Batch API job status for a study. "
            "Reads checkpoint state and queries the API without "
            "modifying pipeline state."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # One-shot status check
  python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml

  # Continuous monitoring (default: hourly checks)
  python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml --watch

  # Watch with 30-minute interval
  python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml \\
      --watch --interval 1800

  # Auto-trigger pipeline when all jobs complete
  python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml \\
      --watch --auto-resume

  # Machine-readable JSON output
  python scripts/batch-monitor.py studies/phase3a-h3-voting-track2.yaml --json
        """,
    )

    parser.add_argument(
        "study_file",
        type=Path,
        help="Path to study YAML file",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help=(
            "Continuous monitoring mode. Checks status in a loop "
            "(default interval: 3600s)"
        ),
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help=(
            "Seconds between checks in --watch mode (default: 3600). "
            "Ignored without --watch."
        ),
    )
    parser.add_argument(
        "--auto-resume",
        action="store_true",
        help=(
            "When all pending jobs reach terminal states, "
            "automatically trigger the pipeline to download results. "
            "Requires --watch."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of formatted text",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    if args.auto_resume and not args.watch:
        parser.error("--auto-resume requires --watch")

    if args.watch:
        watch_loop(
            study_path=args.study_file,
            interval=args.interval,
            auto_resume=args.auto_resume,
            output_json=args.json,
        )
    else:
        check_status(args.study_file, output_json=args.json)


if __name__ == "__main__":
    main()
