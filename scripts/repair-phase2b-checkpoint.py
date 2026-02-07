#!/usr/bin/env python3
"""
Phase 2b Checkpoint Repair Script
===================================

Description:
    One-off script to repair Phase 2b checkpoint files after the rate-limiting
    incident (Session 23). The original run at workers=60 overwhelmed the API's
    1M TPM limit, resulting in 82 of 100 runs being damaged (0–23 of 60 tiles
    processed). Checkpoint files incorrectly mark all 100 as "completed" because
    the batch script always exited 0 regardless of tile failures.

    This script:
    1. Scans all runs under both track directories
    2. Reads each .meta.json to check items_processed and items_failed
    3. Classifies runs as healthy (60 processed, 0 failed) or damaged
    4. Rewrites checkpoint.json to include only healthy runs
    5. Prints a summary of what was kept and what was removed

    After running this, use --resume on the study YAML to re-queue only
    the damaged runs.

Usage:
    python scripts/repair-phase2b-checkpoint.py
    python scripts/repair-phase2b-checkpoint.py --dry-run
    python scripts/repair-phase2b-checkpoint.py --expected-tiles 60

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Phase 2b track directories
TRACKS = {
    "track1-image": PROJECT_ROOT / "outputs" / "phase2b" / "track1-image",
    "track2-text": PROJECT_ROOT / "outputs" / "phase2b" / "track2-text",
}


def scan_track(
    track_dir: Path,
    expected_tiles: int = 60,
) -> tuple[list[str], list[dict]]:
    """
    Scan a track directory and classify runs as healthy or damaged.

    A run is healthy if items_processed == expected_tiles and
    items_failed == 0 in its .meta.json file.

    Args:
        track_dir: Path to track directory (e.g., outputs/phase2b/track1-image)
        expected_tiles: Expected number of tiles per run (from manifest)

    Returns:
        Tuple of (healthy_keys, damaged_runs) where healthy_keys are
        checkpoint-style keys ('T0.0/run_1') and damaged_runs contain
        diagnostic details.
    """
    healthy_keys = []
    damaged_runs = []

    if not track_dir.exists():
        print(f"  Track directory not found: {track_dir}")
        return healthy_keys, damaged_runs

    for cond_dir in sorted(track_dir.iterdir()):
        if not cond_dir.is_dir():
            continue
        # Skip non-condition directories
        if cond_dir.name in ("checkpoints",):
            continue

        for run_dir in sorted(cond_dir.iterdir()):
            if not run_dir.is_dir():
                continue

            # Find the meta.json file
            meta_files = list(run_dir.glob("*.meta.json"))
            if not meta_files:
                damaged_runs.append({
                    "key": f"{cond_dir.name}/{run_dir.name}",
                    "reason": "no_meta_json",
                    "processed": 0,
                    "failed": 0,
                })
                continue

            # Read the meta.json
            meta_path = meta_files[0]
            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                damaged_runs.append({
                    "key": f"{cond_dir.name}/{run_dir.name}",
                    "reason": f"meta_read_error: {e}",
                    "processed": 0,
                    "failed": 0,
                })
                continue

            stats = meta.get("execution_stats", {})
            processed = stats.get("items_processed", 0)
            failed = stats.get("items_failed", 0)

            key = f"{cond_dir.name}/{run_dir.name}"

            if processed == expected_tiles and failed == 0:
                healthy_keys.append(key)
            else:
                damaged_runs.append({
                    "key": key,
                    "reason": (
                        f"processed={processed}, failed={failed} "
                        f"(expected {expected_tiles})"
                    ),
                    "processed": processed,
                    "failed": failed,
                })

    return healthy_keys, damaged_runs


def repair_checkpoint(
    track_dir: Path,
    healthy_keys: list[str],
    dry_run: bool = False,
) -> None:
    """
    Rewrite checkpoint.json to include only healthy runs.

    Backs up the original checkpoint before overwriting.

    Args:
        track_dir: Path to track directory
        healthy_keys: List of checkpoint keys to keep
        dry_run: If True, print what would be done without writing
    """
    checkpoint_path = track_dir / "checkpoint.json"

    if not checkpoint_path.exists():
        print(f"  No checkpoint file found at {checkpoint_path}")
        return

    # Read original checkpoint
    with open(checkpoint_path, "r") as f:
        original = json.load(f)

    original_completed = len(original.get("completed", []))

    if dry_run:
        print(f"  [DRY RUN] Would rewrite {checkpoint_path}")
        print(f"  [DRY RUN] Original completed: {original_completed}")
        print(f"  [DRY RUN] New completed: {len(healthy_keys)}")
        print(
            f"  [DRY RUN] Removed: "
            f"{original_completed - len(healthy_keys)}"
        )
        return

    # Backup original
    backup_path = checkpoint_path.with_suffix(".json.bak")
    shutil.copy2(checkpoint_path, backup_path)
    print(f"  Backed up original to {backup_path}")

    # Write repaired checkpoint
    repaired = {
        "completed": sorted(healthy_keys),
        "failed": [],
        "total_cost_usd": original.get("total_cost_usd", 0.0),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "repair_note": (
            f"Repaired by repair-phase2b-checkpoint.py. "
            f"Original had {original_completed} completed, "
            f"reduced to {len(healthy_keys)} after audit."
        ),
    }

    with open(checkpoint_path, "w") as f:
        json.dump(repaired, f, indent=2)

    print(f"  Wrote repaired checkpoint: {checkpoint_path}")
    print(
        f"  Completed: {original_completed} → {len(healthy_keys)} "
        f"(removed {original_completed - len(healthy_keys)})"
    )


def main():
    """Main entry point for checkpoint repair."""
    parser = argparse.ArgumentParser(
        description="Repair Phase 2b checkpoints after rate-limiting incident",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script audits all Phase 2b runs and rewrites checkpoint.json files
to include only runs where all tiles were successfully processed. After
running this, use --resume on the study YAML to re-queue damaged runs.

Examples:
  # Audit and repair both tracks
  python scripts/repair-phase2b-checkpoint.py

  # Preview without modifying files
  python scripts/repair-phase2b-checkpoint.py --dry-run

  # Use a different expected tile count
  python scripts/repair-phase2b-checkpoint.py --expected-tiles 30
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without modifying files",
    )
    parser.add_argument(
        "--expected-tiles",
        type=int,
        default=60,
        help="Expected tiles per run from manifest (default: 60)",
    )

    args = parser.parse_args()

    print("Phase 2b Checkpoint Repair")
    print("=" * 50)
    print()

    total_healthy = 0
    total_damaged = 0

    for track_name, track_dir in TRACKS.items():
        print(f"Track: {track_name}")
        print("-" * 40)

        healthy_keys, damaged_runs = scan_track(
            track_dir, expected_tiles=args.expected_tiles
        )

        total_healthy += len(healthy_keys)
        total_damaged += len(damaged_runs)

        print(f"  Healthy: {len(healthy_keys)}")
        print(f"  Damaged: {len(damaged_runs)}")

        if damaged_runs:
            print("  Damaged runs:")
            for run in damaged_runs[:10]:
                print(f"    {run['key']}: {run['reason']}")
            if len(damaged_runs) > 10:
                print(f"    ... and {len(damaged_runs) - 10} more")

        print()
        repair_checkpoint(track_dir, healthy_keys, dry_run=args.dry_run)
        print()

    # Summary
    print("=" * 50)
    print("Summary")
    print(f"  Total healthy: {total_healthy}")
    print(f"  Total damaged: {total_damaged}")
    print(f"  Total runs: {total_healthy + total_damaged}")
    print()

    if args.dry_run:
        print("DRY RUN — no files were modified.")
        print("Run without --dry-run to apply repairs.")
    else:
        print("Checkpoints repaired. Use --resume to re-queue damaged runs:")
        print()
        print(
            "  .venv/bin/python3 scripts/run_phase2.py "
            "studies/phase2b-h7-temperature.yaml --resume"
        )
        print(
            "  .venv/bin/python3 scripts/run_phase2.py "
            "studies/phase2b-h7-temperature-text-only.yaml --resume"
        )

    # Exit code: 0 if all healthy, 1 if any damaged
    sys.exit(0 if total_damaged == 0 else 1)


if __name__ == "__main__":
    main()
