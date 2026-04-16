#!/usr/bin/env python3
"""
Build Consensus GeoJSON for All Experimental Conditions
========================================================

Orchestrates the construction of greedy consensus GeoJSON files across all
experimental conditions that require multi-pass voting. Reads the condition
inventory (JSON = JavaScript Object Notation), filters by status, hypothesis,
or condition ID, and shells out to ``merge_passes.py --sweep`` for each
qualifying condition.

Each invocation of ``merge_passes.py --sweep`` produces a full threshold sweep
(``consensus_t1.geojson`` through ``consensus_tK.geojson``) plus a
``voting_summary.json`` summarising the vote distribution across thresholds.

Usage::

    # Build consensus for all NEEDS_CONSENSUS conditions (default)
    python scripts/build_all_consensus.py

    # Dry run — preview what would be processed, no execution
    python scripts/build_all_consensus.py --dry-run

    # Filter by hypothesis
    python scripts/build_all_consensus.py --hypothesis H3 H9

    # Force rebuild for specific conditions
    python scripts/build_all_consensus.py \\
        --condition h1-brief-text h7-track1-image-T0.3 --force

    # Parallel processing with 4 workers on sapphire
    python scripts/build_all_consensus.py --workers 4

    # Build + update inventory in one step
    python scripts/build_all_consensus.py --workers 4 --update-inventory

Inputs:
    - planning/condition-inventory.json — structured condition metadata
      (produced by ``build_condition_inventory.py``)
    - outputs/**/run_*/ — per-condition detection pass directories containing
      GeoJSON detection files from the VLM pipeline

Outputs:
    - {condition_path}/consensus/consensus_t1..tK.geojson — per-threshold
      consensus detections (GeoJSON, EPSG:4326)
    - {condition_path}/consensus/voting_summary.json — vote distribution
    - results/consensus-build-manifest_{timestamp}.json — run manifest

Exit Codes:
    0 - All conditions succeeded or were skipped
    1 - Some conditions failed (partial success)
    2 - Fatal error (bad configuration, missing paths)

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-16
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY = PROJECT_ROOT / "planning" / "condition-inventory.json"
DEFAULT_OUTPUT_SUBDIR = "consensus"
MERGE_PASSES_SCRIPT = PROJECT_ROOT / "scripts" / "merge_passes.py"
PYTHON_EXECUTABLE = sys.executable

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def setup_logging(
    log_file: Path | None = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> Path:
    """Configure dual-output logging to console (INFO) and file (DEBUG).

    Args:
        log_file: Path for the log file. If ``None``, auto-generates a
            timestamped path under ``logs/``.
        console_level: Logging level for the console handler.
        file_level: Logging level for the file handler.

    Returns:
        Resolved log file path.
    """
    if log_file is None:
        logs_dir = PROJECT_ROOT / "logs"
        logs_dir.mkdir(exist_ok=True)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        log_file = logs_dir / f"build_all_consensus_{timestamp}.log"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Prevent duplicate handlers on repeated calls (e.g., in tests)
    root.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(console_level)
    console.setFormatter(fmt)
    root.addHandler(console)

    log_file.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(file_level)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    return log_file


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_git_commit() -> str:
    """Return short git commit hash, or ``'(unknown)'`` on failure."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=str(PROJECT_ROOT),
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "(unknown)"


# ---------------------------------------------------------------------------
# Inventory loading and filtering
# ---------------------------------------------------------------------------


def load_inventory(inventory_path: Path) -> list[dict]:
    """Load the condition inventory JSON.

    Args:
        inventory_path: Path to condition-inventory.json.

    Returns:
        List of condition dictionaries.

    Raises:
        FileNotFoundError: If the inventory file does not exist.
        json.JSONDecodeError: If the file is malformed JSON.
    """
    logger.info("Loading inventory from %s", inventory_path)
    with open(inventory_path, encoding="utf-8") as f:
        inventory = json.load(f)
    logger.info("Loaded %d conditions", len(inventory))
    return inventory


def filter_conditions(
    conditions: list[dict],
    *,
    status_filter: str | None = "NEEDS_CONSENSUS",
    condition_ids: list[str] | None = None,
    hypothesis_filter: list[str] | None = None,
) -> list[dict]:
    """Filter conditions by status, ID, and/or hypothesis.

    When ``--condition`` is specified it overrides ``--status`` — the user is
    explicitly selecting conditions regardless of their current status. When
    ``--hypothesis`` is specified alongside ``--status``, both filters apply
    (intersection).

    Args:
        conditions: Full inventory list.
        status_filter: Status to match (e.g., ``'NEEDS_CONSENSUS'``).
            Ignored when *condition_ids* is provided.
        condition_ids: Explicit list of condition IDs to select.
        hypothesis_filter: List of hypothesis codes (e.g., ``['H3', 'H9']``).

    Returns:
        Filtered list, sorted by ``id`` for deterministic ordering.
    """
    if condition_ids is not None:
        # Explicit selection overrides status filter
        id_set = set(condition_ids)
        result = [c for c in conditions if c["id"] in id_set]
        found_ids = {c["id"] for c in result}
        missing = id_set - found_ids
        if missing:
            logger.warning(
                "Requested condition IDs not found in inventory: %s",
                sorted(missing),
            )
    elif status_filter:
        result = [c for c in conditions if c.get("status") == status_filter]
    else:
        result = list(conditions)

    # Apply hypothesis filter as intersection
    if hypothesis_filter:
        hyp_set = {h.upper() for h in hypothesis_filter}
        result = [
            c for c in result
            if c.get("hypothesis", "").upper() in hyp_set
        ]

    result.sort(key=lambda c: c["id"])
    logger.info(
        "Filtered to %d conditions (status=%s, ids=%s, hypotheses=%s)",
        len(result),
        status_filter if condition_ids is None else "(overridden)",
        condition_ids,
        hypothesis_filter,
    )
    return result


# ---------------------------------------------------------------------------
# Path validation and consensus detection
# ---------------------------------------------------------------------------


def validate_condition_path(condition: dict) -> tuple[bool, str]:
    """Pre-flight validation: check that the condition's run directories exist.

    Args:
        condition: Condition dict from the inventory.

    Returns:
        Tuple of ``(valid, message)``.
    """
    cond_dir = PROJECT_ROOT / condition["path"]
    if not cond_dir.is_dir():
        return False, f"Directory does not exist: {cond_dir}"

    run_dirs = sorted(cond_dir.glob("run_*"))
    pass_dirs = sorted(cond_dir.glob("pass_*"))
    all_dirs = run_dirs + pass_dirs

    if not all_dirs:
        return False, f"No run_* or pass_* directories in {cond_dir}"

    # Verify at least one pass directory contains GeoJSON files
    has_data = any(
        list(d.glob("*.geojson"))
        for d in all_dirs
        if not any(".meta" in f.name for f in d.glob("*.geojson"))
    )
    if not has_data:
        # Double-check: look for any geojson at all (including .meta)
        any_geojson = any(list(d.glob("*.geojson")) for d in all_dirs)
        if not any_geojson:
            return False, (
                f"{len(all_dirs)} pass directories found but none "
                f"contain GeoJSON files"
            )

    return True, f"{len(all_dirs)} pass directories found"


def validate_all_paths(conditions: list[dict]) -> list[tuple[dict, str]]:
    """Pre-flight: validate all condition paths. Returns list of failures.

    Args:
        conditions: Filtered condition list.

    Returns:
        List of ``(condition, error_message)`` for conditions that failed
        validation. Empty list means all passed.
    """
    failures: list[tuple[dict, str]] = []
    for cond in conditions:
        valid, msg = validate_condition_path(cond)
        if not valid:
            failures.append((cond, msg))
            logger.error("Pre-flight FAIL: %s — %s", cond["id"], msg)
        else:
            logger.debug("Pre-flight OK: %s — %s", cond["id"], msg)
    return failures


def resolve_consensus_dir(
    condition: dict,
    output_subdir: str = DEFAULT_OUTPUT_SUBDIR,
) -> Path:
    """Determine the consensus output directory for a condition.

    Most conditions use ``{condition_path}/{output_subdir}/``. For h8-v2 and
    h12-v2 conditions, the existing convention places consensus in a separate
    ``greedy/`` tree — but those conditions are already ``READY`` in the
    inventory and will not normally be selected. If explicitly requested,
    consensus goes into the standard in-place subdirectory.

    Args:
        condition: Condition dict from the inventory.
        output_subdir: Subdirectory name for consensus output.

    Returns:
        Resolved output directory path (absolute).
    """
    return PROJECT_ROOT / condition["path"] / output_subdir


def check_existing_consensus(consensus_dir: Path) -> tuple[bool, str]:
    """Check whether consensus outputs already exist in a directory.

    Detects standard ``merge_passes.py --sweep`` output
    (``consensus_t*.geojson`` + ``voting_summary.json``) and partial builds
    (threshold files without the summary).

    Args:
        consensus_dir: Directory to check for existing consensus files.

    Returns:
        Tuple of ``(exists, description)`` where *description* explains what
        was found.
    """
    if not consensus_dir.is_dir():
        return False, "no consensus directory"

    threshold_files = sorted(consensus_dir.glob("consensus_t*.geojson"))
    has_summary = (consensus_dir / "voting_summary.json").is_file()

    if not threshold_files:
        return False, "consensus directory exists but is empty"

    n = len(threshold_files)
    if has_summary:
        return True, f"complete: {n} threshold files + voting_summary.json"

    return True, f"partial: {n} threshold files, missing voting_summary.json"


# ---------------------------------------------------------------------------
# Subprocess execution
# ---------------------------------------------------------------------------


def build_merge_command(condition: dict, consensus_dir: Path) -> list[str]:
    """Construct the ``merge_passes.py --sweep`` subprocess command.

    Args:
        condition: Condition dict from the inventory.
        consensus_dir: Target output directory.

    Returns:
        Command list suitable for ``subprocess.run()``.
    """
    return [
        PYTHON_EXECUTABLE,
        str(MERGE_PASSES_SCRIPT),
        "--input-dir", str(PROJECT_ROOT / condition["path"]),
        "--output-dir", str(consensus_dir),
        "--sweep",
    ]


def process_single_condition(
    condition: dict,
    *,
    output_subdir: str = DEFAULT_OUTPUT_SUBDIR,
    force: bool = False,
    dry_run: bool = False,
    timeout: int = 300,
) -> dict:
    """Process a single condition: validate, check existing, run merge_passes.

    This is the unit of work for both sequential and parallel modes.

    Args:
        condition: Condition dict from the inventory.
        output_subdir: Consensus output subdirectory name.
        force: If ``True``, rebuild even if consensus already exists.
        dry_run: If ``True``, report what would happen without executing.
        timeout: Subprocess timeout in seconds.

    Returns:
        Result dict with keys: ``id``, ``path``, ``status``
        (``'success'``/``'failure'``/``'skipped'``/``'dry_run'``), ``K``,
        ``thresholds_generated``, ``consensus_dir``, ``message``,
        ``duration_seconds``.
    """
    cond_id = condition["id"]
    k_value = condition.get("K", 0)
    start = time.monotonic()

    # Base result dict
    result: dict = {
        "id": cond_id,
        "path": condition["path"],
        "K": k_value,
        "thresholds_generated": [],
        "consensus_dir": "",
        "status": "",
        "message": "",
        "duration_seconds": 0.0,
    }

    # Skip K=1 conditions even if explicitly requested
    if k_value <= 1:
        result["status"] = "skipped"
        result["message"] = (
            "K=1: single-pass conditions do not support consensus voting"
        )
        result["duration_seconds"] = time.monotonic() - start
        logger.info("[%s] Skipped — %s", cond_id, result["message"])
        return result

    consensus_dir = resolve_consensus_dir(condition, output_subdir)
    result["consensus_dir"] = str(
        consensus_dir.relative_to(PROJECT_ROOT)
    )

    # Check for existing consensus
    exists, description = check_existing_consensus(consensus_dir)
    if exists and not force:
        result["status"] = "skipped"
        result["message"] = f"existing consensus: {description}"
        result["duration_seconds"] = time.monotonic() - start
        logger.info("[%s] Skipped — %s", cond_id, result["message"])
        return result

    if exists and force:
        logger.info(
            "[%s] Force rebuild — clearing existing: %s",
            cond_id,
            description,
        )
        # Remove stale files to prevent leftover thresholds from a
        # previous run with a different K contaminating the directory
        for stale in consensus_dir.glob("consensus_t*.geojson"):
            stale.unlink()
        stale_summary = consensus_dir / "voting_summary.json"
        if stale_summary.is_file():
            stale_summary.unlink()

    # Dry-run mode
    cmd = build_merge_command(condition, consensus_dir)
    if dry_run:
        result["status"] = "dry_run"
        result["message"] = f"would execute: {' '.join(cmd)}"
        result["duration_seconds"] = time.monotonic() - start
        logger.info("[%s] DRY RUN — %s", cond_id, result["message"])
        return result

    # Create output directory
    consensus_dir.mkdir(parents=True, exist_ok=True)

    # Execute merge_passes.py --sweep
    logger.info("[%s] Running merge_passes.py --sweep (K=%d)...", cond_id, k_value)
    logger.debug("[%s] Command: %s", cond_id, " ".join(cmd))

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        result["status"] = "failure"
        result["message"] = f"timeout after {timeout}s"
        result["duration_seconds"] = time.monotonic() - start
        logger.error("[%s] TIMEOUT after %ds", cond_id, timeout)
        return result
    except Exception as exc:
        result["status"] = "failure"
        result["message"] = f"exception: {exc}"
        result["duration_seconds"] = time.monotonic() - start
        logger.error("[%s] EXCEPTION: %s", cond_id, exc)
        return result

    if proc.returncode != 0:
        stderr_snippet = proc.stderr[:500] if proc.stderr else "(no stderr)"
        result["status"] = "failure"
        result["message"] = (
            f"exit code {proc.returncode}: {stderr_snippet}"
        )
        result["duration_seconds"] = time.monotonic() - start
        logger.error(
            "[%s] FAILED (exit %d): %s",
            cond_id, proc.returncode, stderr_snippet,
        )
        return result

    # Success — read voting_summary.json for threshold info
    summary_path = consensus_dir / "voting_summary.json"
    thresholds: list[int] = []
    if summary_path.is_file():
        try:
            with open(summary_path, encoding="utf-8") as f:
                summary = json.load(f)
            thresholds = sorted(int(t) for t in summary.get("thresholds", {}))
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning(
                "[%s] Could not parse voting_summary.json: %s", cond_id, exc
            )

    result["status"] = "success"
    result["thresholds_generated"] = thresholds
    result["message"] = (
        f"{len(thresholds)} thresholds generated "
        f"(t={min(thresholds)}..{max(thresholds)})"
        if thresholds
        else "completed but no thresholds in summary"
    )
    result["duration_seconds"] = round(time.monotonic() - start, 2)
    logger.info(
        "[%s] SUCCESS in %.1fs — %s", cond_id, result["duration_seconds"],
        result["message"],
    )
    return result


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_all_conditions(
    conditions: list[dict],
    *,
    output_subdir: str = DEFAULT_OUTPUT_SUBDIR,
    force: bool = False,
    dry_run: bool = False,
    workers: int = 1,
    timeout: int = 300,
) -> list[dict]:
    """Process all conditions, sequentially or in parallel.

    Args:
        conditions: Filtered, sorted list of conditions.
        output_subdir: Consensus output subdirectory name.
        force: Rebuild existing consensus.
        dry_run: Report without executing.
        workers: Number of parallel workers (1 = sequential).
        timeout: Per-condition subprocess timeout in seconds.

    Returns:
        List of per-condition result dicts, in the same order as *conditions*.
    """
    total = len(conditions)

    if workers <= 1:
        # Sequential mode — simple loop with progress counter
        results: list[dict] = []
        for i, cond in enumerate(conditions, 1):
            logger.info("[%d/%d] Processing %s...", i, total, cond["id"])
            result = process_single_condition(
                cond,
                output_subdir=output_subdir,
                force=force,
                dry_run=dry_run,
                timeout=timeout,
            )
            results.append(result)
        return results

    # Parallel mode — ThreadPoolExecutor
    logger.info(
        "Launching %d workers for %d conditions...", workers, total,
    )
    results_by_id: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_id = {
            executor.submit(
                process_single_condition,
                cond,
                output_subdir=output_subdir,
                force=force,
                dry_run=dry_run,
                timeout=timeout,
            ): cond["id"]
            for cond in conditions
        }
        completed = 0
        for future in as_completed(future_to_id):
            cond_id = future_to_id[future]
            completed += 1
            try:
                result = future.result()
            except Exception as exc:
                result = {
                    "id": cond_id,
                    "path": "",
                    "K": 0,
                    "thresholds_generated": [],
                    "consensus_dir": "",
                    "status": "failure",
                    "message": f"executor exception: {exc}",
                    "duration_seconds": 0.0,
                }
                logger.error(
                    "[%d/%d] %s — executor exception: %s",
                    completed, total, cond_id, exc,
                )
            results_by_id[cond_id] = result
            logger.info(
                "[%d/%d] %s — %s",
                completed, total, cond_id, result["status"],
            )

    # Return in original sorted order
    return [results_by_id[c["id"]] for c in conditions]


# ---------------------------------------------------------------------------
# Manifest and inventory update
# ---------------------------------------------------------------------------


def write_manifest(
    results: list[dict],
    *,
    manifest_path: Path,
    inventory_path: Path,
    filters_applied: dict,
) -> None:
    """Write the summary manifest JSON.

    Args:
        results: List of per-condition result dicts.
        manifest_path: Output path for the manifest file.
        inventory_path: Path to the inventory that was used (for provenance).
        filters_applied: Dict describing CLI filters used.
    """
    from collections import Counter

    status_counts = Counter(r["status"] for r in results)
    manifest = {
        "script": "build_all_consensus.py",
        "version": __version__,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "inventory_path": str(inventory_path),
        "filters_applied": filters_applied,
        "statistics": {
            "total": len(results),
            "success": status_counts.get("success", 0),
            "failure": status_counts.get("failure", 0),
            "skipped": status_counts.get("skipped", 0),
            "dry_run": status_counts.get("dry_run", 0),
        },
        "conditions": results,
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Manifest written to %s", manifest_path)


def update_inventory(
    inventory_path: Path,
    results: list[dict],
) -> int:
    """Update condition-inventory.json with consensus build results.

    For each successful build, sets ``consensus_built=True``, populates
    ``consensus_files``, and changes status from ``NEEDS_CONSENSUS`` to
    ``READY``.

    Args:
        inventory_path: Path to condition-inventory.json.
        results: Per-condition result dicts from :func:`run_all_conditions`.

    Returns:
        Number of conditions updated.
    """
    # Build lookup of successful results
    success_map = {
        r["id"]: r for r in results if r["status"] == "success"
    }
    if not success_map:
        logger.info("No successful builds — inventory unchanged")
        return 0

    with open(inventory_path, encoding="utf-8") as f:
        inventory = json.load(f)

    updated = 0
    for cond in inventory:
        if cond["id"] not in success_map:
            continue

        result = success_map[cond["id"]]
        cond["consensus_built"] = True
        cond["consensus_files"] = (
            [f"consensus_t{t}.geojson" for t in result["thresholds_generated"]]
            + ["voting_summary.json"]
        )
        if cond.get("status") == "NEEDS_CONSENSUS":
            cond["status"] = "READY"
        updated += 1

    with open(inventory_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)
        f.write("\n")  # Trailing newline

    logger.info(
        "Updated %d conditions in %s", updated, inventory_path,
    )
    return updated


# ---------------------------------------------------------------------------
# Summary display
# ---------------------------------------------------------------------------


def print_summary(results: list[dict]) -> None:
    """Print a human-readable summary table to the console.

    Args:
        results: Per-condition result dicts.
    """
    from collections import Counter

    counts = Counter(r["status"] for r in results)
    total_time = sum(r.get("duration_seconds", 0) for r in results)

    print("\n" + "=" * 72)
    print("CONSENSUS BUILD SUMMARY")
    print("=" * 72)
    print(f"  Total conditions:  {len(results)}")
    print(f"  Success:           {counts.get('success', 0)}")
    print(f"  Failed:            {counts.get('failure', 0)}")
    print(f"  Skipped:           {counts.get('skipped', 0)}")
    print(f"  Dry run:           {counts.get('dry_run', 0)}")
    print(f"  Total time:        {total_time:.1f}s")
    print("-" * 72)

    # Show failures prominently
    failures = [r for r in results if r["status"] == "failure"]
    if failures:
        print("\nFAILED CONDITIONS:")
        for r in failures:
            print(f"  {r['id']}: {r['message']}")
        print()

    # Compact table for all results
    print(f"{'ID':<45} {'Status':<10} {'K':>3} {'Time':>7}")
    print("-" * 72)
    for r in results:
        t = f"{r.get('duration_seconds', 0):.1f}s"
        print(f"{r['id']:<45} {r['status']:<10} {r.get('K', '?'):>3} {t:>7}")
    print("=" * 72)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_cli_parser() -> argparse.ArgumentParser:
    """Construct the argument parser.

    Returns:
        Configured ``ArgumentParser``.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Build greedy consensus GeoJSON for all experimental conditions. "
            "Reads the condition inventory, filters by status/hypothesis/ID, "
            "and runs merge_passes.py --sweep for each qualifying condition."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Input
    parser.add_argument(
        "--inventory",
        type=Path,
        default=DEFAULT_INVENTORY,
        help=(
            "Path to condition-inventory.json "
            f"(default: {DEFAULT_INVENTORY.relative_to(PROJECT_ROOT)})"
        ),
    )

    # Filtering
    parser.add_argument(
        "--status",
        default="NEEDS_CONSENSUS",
        help=(
            "Filter conditions by status field. "
            "Ignored when --condition is used (default: NEEDS_CONSENSUS)"
        ),
    )
    parser.add_argument(
        "--condition",
        nargs="+",
        metavar="ID",
        help="Process only these condition IDs (overrides --status)",
    )
    parser.add_argument(
        "--hypothesis",
        nargs="+",
        metavar="H",
        help=(
            "Filter by hypothesis code, e.g. H3 H9 "
            "(intersects with --status)"
        ),
    )

    # Output
    parser.add_argument(
        "--output-subdir",
        default=DEFAULT_OUTPUT_SUBDIR,
        help=(
            "Subdirectory name for consensus output within each condition "
            f"(default: {DEFAULT_OUTPUT_SUBDIR})"
        ),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help=(
            "Path for the output manifest JSON "
            "(default: results/consensus-build-manifest_{timestamp}.json)"
        ),
    )

    # Execution control
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild consensus even if it already exists",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be processed without executing",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parallel workers (default: 1, sequential)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Per-condition subprocess timeout in seconds (default: 300)",
    )

    # Post-processing
    parser.add_argument(
        "--update-inventory",
        action="store_true",
        help=(
            "Update condition-inventory.json after building "
            "(set consensus_built=True, status=READY)"
        ),
    )

    # Logging
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Log file path (default: auto-timestamped in logs/)",
    )

    # Meta
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point: parse arguments, validate, orchestrate, report.

    Returns:
        Exit code: 0 = all succeeded/skipped, 1 = some failures, 2 = fatal.
    """
    parser = build_cli_parser()
    args = parser.parse_args()

    # Set up logging
    log_file = setup_logging(log_file=args.log_file)
    logger.info(
        "build_all_consensus.py v%s — git %s",
        __version__, get_git_commit(),
    )
    logger.info("Log file: %s", log_file)

    # Verify merge_passes.py exists
    if not MERGE_PASSES_SCRIPT.is_file():
        logger.error(
            "merge_passes.py not found at %s", MERGE_PASSES_SCRIPT,
        )
        return 2

    # Load and filter inventory
    try:
        inventory = load_inventory(args.inventory)
    except FileNotFoundError:
        logger.error("Inventory not found: %s", args.inventory)
        return 2
    except json.JSONDecodeError as exc:
        logger.error("Malformed inventory JSON: %s", exc)
        return 2

    conditions = filter_conditions(
        inventory,
        status_filter=args.status,
        condition_ids=args.condition,
        hypothesis_filter=args.hypothesis,
    )

    if not conditions:
        logger.info("No conditions match the specified filters — nothing to do")
        return 0

    # Log K distribution
    from collections import Counter

    k_dist = Counter(c.get("K", 0) for c in conditions)
    logger.info(
        "K distribution: %s",
        ", ".join(f"K={k}: {n}" for k, n in sorted(k_dist.items())),
    )

    # Pre-flight validation — exclude failing conditions with warning
    logger.info("Pre-flight: validating %d condition paths...", len(conditions))
    failures = validate_all_paths(conditions)
    if failures:
        failed_ids = {cond["id"] for cond, _ in failures}
        for cond, msg in failures:
            logger.warning("Pre-flight SKIP: %s — %s", cond["id"], msg)
        conditions = [c for c in conditions if c["id"] not in failed_ids]
        if not conditions:
            logger.error(
                "Pre-flight: ALL %d conditions failed validation — aborting",
                len(failures),
            )
            return 2
        logger.warning(
            "Pre-flight: excluded %d condition(s), continuing with %d",
            len(failures), len(conditions),
        )
    else:
        logger.info("Pre-flight: all %d paths validated", len(conditions))

    # Run
    results = run_all_conditions(
        conditions,
        output_subdir=args.output_subdir,
        force=args.force,
        dry_run=args.dry_run,
        workers=args.workers,
        timeout=args.timeout,
    )

    # Write manifest
    if args.manifest:
        manifest_path = args.manifest
    else:
        results_dir = PROJECT_ROOT / "results"
        results_dir.mkdir(exist_ok=True)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        manifest_path = (
            results_dir / f"consensus-build-manifest_{timestamp}.json"
        )

    filters_applied = {
        "status": args.status if args.condition is None else "(overridden)",
        "condition_ids": args.condition,
        "hypothesis": args.hypothesis,
        "force": args.force,
        "dry_run": args.dry_run,
    }
    write_manifest(
        results,
        manifest_path=manifest_path,
        inventory_path=args.inventory,
        filters_applied=filters_applied,
    )

    # Update inventory if requested
    if args.update_inventory:
        updated = update_inventory(args.inventory, results)
        logger.info("Updated %d inventory entries", updated)

    # Print summary
    print_summary(results)

    # Exit code
    has_failures = any(r["status"] == "failure" for r in results)
    if has_failures:
        logger.warning("Some conditions failed — exit code 1")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
