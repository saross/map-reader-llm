#!/usr/bin/env python3
"""
Phase 1 Runner: Library Construction
====================================

Executes Phase 1 of the preregistered study, which constructs the hard example
library through repeated baseline detection and failure analysis.

Usage:
    python scripts/run_phase1.py
    python scripts/run_phase1.py --dry-run
    python scripts/run_phase1.py --resume
    python scripts/run_phase1.py --passes 3  # Run fewer passes for testing

Inputs:
    - Study definition: studies/phase1-library.yaml
    - Config: prompts/configs/library_pure-positive-canon.json
    - Manifest: inputs/tiles/calibration_manifest.json

Outputs:
    - Per-pass detections: outputs/phase1-library/pass_0{N}/
    - Merged detections: outputs/phase1-library/merged_detections.geojson
    - Hard examples: outputs/phase1-library/hard-positives/, hard-negatives/

Exit Codes:
    0 - Success: All passes completed successfully
    1 - Error: Configuration or execution error
    2 - Partial: Some passes completed, others failed

Author: Shawn Ross, Claude Code
Version: 1.0.0
Licence: Apache 2.0
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Script version
__version__ = "1.0.0"

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent


def load_study_config(yaml_path: Path) -> dict:
    """
    Load Phase 1 study configuration from YAML file.

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
    required = ["study", "config", "inputs", "execution"]
    for section in required:
        if section not in config:
            raise ValueError(f"Missing required section: {section}")

    return config


def load_checkpoint(checkpoint_path: Path) -> dict:
    """
    Load checkpoint file if it exists.

    Args:
        checkpoint_path: Path to checkpoint JSON file

    Returns:
        Checkpoint dictionary with completed passes, or empty structure
    """
    if checkpoint_path.exists():
        with open(checkpoint_path, "r") as f:
            return json.load(f)
    return {
        "completed_passes": [],
        "failed_passes": [],
        "last_updated": None,
        "merge_complete": False,
        "evaluation_complete": False,
    }


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


def run_detection_pass(
    pass_num: int,
    config: dict,
    output_dir: Path,
    dry_run: bool = False,
    timeout: int = 1800,
) -> tuple[bool, str]:
    """
    Execute a single detection pass.

    Args:
        pass_num: Pass number (1-indexed)
        config: Study configuration dictionary
        output_dir: Base output directory
        dry_run: If True, print command without executing
        timeout: Maximum seconds to wait for completion

    Returns:
        Tuple of (success: bool, message: str)
    """
    config_file = PROJECT_ROOT / config["config"]["file"]
    manifest = PROJECT_ROOT / config["inputs"]["manifest"]
    pass_dir = output_dir / f"pass_{pass_num:02d}"

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "4_detect_mounds_batch.py"),
        "--config", str(config_file),
        "--manifest", str(manifest),
        "--output-dir", str(pass_dir),
        "--workers", str(config["execution"].get("workers", 1)),
    ]

    if dry_run:
        print(f"  [DRY RUN] Would execute: {' '.join(cmd)}")
        return True, "dry_run"

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
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


def run_merge(
    config: dict,
    output_dir: Path,
    passes: int,
    dry_run: bool = False,
    timeout: int = 300,
) -> tuple[bool, str]:
    """
    Merge detection passes into single GeoJSON.

    Args:
        config: Study configuration dictionary
        output_dir: Base output directory
        passes: Number of passes to merge
        dry_run: If True, print command without executing
        timeout: Maximum seconds to wait for completion

    Returns:
        Tuple of (success: bool, message: str)
    """
    merge_script = PROJECT_ROOT / "scripts" / "merge_passes.py"

    if not merge_script.exists():
        return False, f"merge script not found: {merge_script}"

    cmd = [
        sys.executable,
        str(merge_script),
        "--input-dir", str(output_dir),
        "--output", str(output_dir / "merged_detections.geojson"),
        "--passes", str(passes),
        "--tolerance", "20.0",
    ]

    if dry_run:
        print(f"  [DRY RUN] Would execute: {' '.join(cmd)}")
        return True, "dry_run"

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
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


def run_evaluation(
    config: dict,
    output_dir: Path,
    dry_run: bool = False,
    timeout: int = 300,
) -> tuple[bool, str]:
    """
    Run accuracy evaluation against ground truth.

    Args:
        config: Study configuration dictionary
        output_dir: Base output directory
        dry_run: If True, print command without executing
        timeout: Maximum seconds to wait for completion

    Returns:
        Tuple of (success: bool, message: str)
    """
    eval_script = PROJECT_ROOT / "scripts" / "6_accuracy_report.py"

    if not eval_script.exists():
        return False, f"evaluation script not found: {eval_script}"

    merged_file = output_dir / "merged_detections.geojson"
    bounds = PROJECT_ROOT / config["inputs"]["bounds"]
    ground_truth = PROJECT_ROOT / config["inputs"]["ground_truth"]

    cmd = [
        sys.executable,
        str(eval_script),
        "--pred", str(merged_file),
        "--bounds", str(bounds),
        "--template", str(ground_truth),
    ]

    if dry_run:
        print(f"  [DRY RUN] Would execute: {' '.join(cmd)}")
        return True, "dry_run"

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
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


def preflight_check(config: dict, verbose: bool = True) -> tuple[bool, list[str]]:
    """
    Verify all required inputs exist before execution.

    Args:
        config: Study configuration dictionary
        verbose: If True, print check results

    Returns:
        Tuple of (all_ok: bool, missing: list[str])
    """
    missing = []

    checks = [
        ("Config file", PROJECT_ROOT / config["config"]["file"]),
        ("Manifest", PROJECT_ROOT / config["inputs"]["manifest"]),
        ("Ground truth", PROJECT_ROOT / config["inputs"]["ground_truth"]),
        ("Bounds", PROJECT_ROOT / config["inputs"]["bounds"]),
    ]

    if verbose:
        print("Pre-flight checks:")

    for name, path in checks:
        exists = path.exists()
        status = "OK" if exists else "MISSING"
        if verbose:
            print(f"  [{status}] {name}: {path}")
        if not exists:
            missing.append(str(path))

    # Check example library
    examples_dir = PROJECT_ROOT / "inputs" / "examples" / "neutral-naming"
    required_examples = ["example_01.png", "example_02.png", "example_03.png",
                        "example_04.png", "example_15.png", "example_16.png",
                        "example_17.png"]

    for example in required_examples:
        example_path = examples_dir / example
        if not example_path.exists():
            missing.append(str(example_path))
            if verbose:
                print(f"  [MISSING] Example: {example_path}")

    if verbose and not missing:
        print("  All required inputs present.")

    return len(missing) == 0, missing


def run_phase1(
    study_path: Path,
    dry_run: bool = False,
    resume: bool = False,
    passes: int | None = None,
    verbose: bool = True,
    timeout: int = 1800,
) -> dict:
    """
    Execute Phase 1 library construction study.

    Args:
        study_path: Path to study YAML file
        dry_run: If True, print commands without executing
        resume: If True, skip already-completed passes
        passes: Override number of passes (default: from config)
        verbose: If True, print progress information
        timeout: Maximum seconds per pass (default: 1800)

    Returns:
        Summary dictionary with results
    """
    # Load configuration
    config = load_study_config(study_path)
    study_info = config["study"]

    if verbose:
        print("=" * 70)
        print(f"Study: {study_info['name']}")
        print(f"Version: {study_info.get('version', 'unknown')}")
        print(f"Description: {study_info.get('description', '').strip()}")
        print("=" * 70)
        print()

    # Pre-flight checks
    all_ok, missing = preflight_check(config, verbose=verbose)
    if not all_ok and not dry_run:
        print(f"\nERROR: Missing {len(missing)} required input(s). Cannot proceed.")
        return {"error": "preflight_failed", "missing": missing}

    print()

    # Set up output directory
    output_dir = PROJECT_ROOT / config["execution"]["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine number of passes
    num_passes = passes or config["execution"].get("passes", 5)

    # Load checkpoint if resuming
    checkpoint_path = output_dir / "checkpoint.json"
    checkpoint = load_checkpoint(checkpoint_path) if resume else {
        "completed_passes": [],
        "failed_passes": [],
        "last_updated": None,
        "merge_complete": False,
        "evaluation_complete": False,
    }

    completed_passes = set(checkpoint.get("completed_passes", []))

    if verbose:
        print(f"Output directory: {output_dir}")
        print(f"Passes: {num_passes}")
        if resume and completed_passes:
            print(f"Resuming: {len(completed_passes)} passes already complete")
        print()

    # Run detection passes
    results = {"completed_passes": [], "failed_passes": []}

    print("Phase 1.1: Detection Passes")
    print("-" * 40)

    for i in range(1, num_passes + 1):
        if i in completed_passes:
            if verbose:
                print(f"[{i}/{num_passes}] Pass {i:02d}: SKIPPED (already complete)")
            results["completed_passes"].append(i)
            continue

        if verbose:
            print(f"[{i}/{num_passes}] Pass {i:02d}: Running...")

        success, message = run_detection_pass(
            pass_num=i,
            config=config,
            output_dir=output_dir,
            dry_run=dry_run,
            timeout=timeout,
        )

        if success:
            results["completed_passes"].append(i)
            checkpoint["completed_passes"].append(i)
            if verbose:
                print(f"           Status: OK ({message})")
        else:
            results["failed_passes"].append({"pass": i, "error": message})
            checkpoint["failed_passes"].append({"pass": i, "error": message})
            if verbose:
                print(f"           Status: FAILED ({message})")

        # Save checkpoint after each pass
        save_checkpoint(checkpoint_path, checkpoint)

    print()

    # Run merge if all passes completed
    if len(results["completed_passes"]) == num_passes:
        print("Phase 1.2: Merge Passes")
        print("-" * 40)

        if checkpoint.get("merge_complete") and resume:
            print("Merge: SKIPPED (already complete)")
        else:
            success, message = run_merge(
                config=config,
                output_dir=output_dir,
                passes=num_passes,
                dry_run=dry_run,
            )

            if success:
                checkpoint["merge_complete"] = True
                print(f"Merge: OK ({message})")
            else:
                print(f"Merge: FAILED ({message})")
                results["merge_failed"] = message

        save_checkpoint(checkpoint_path, checkpoint)
        print()

        # Run evaluation if merge completed
        if checkpoint.get("merge_complete"):
            print("Phase 1.3: Evaluation")
            print("-" * 40)

            if checkpoint.get("evaluation_complete") and resume:
                print("Evaluation: SKIPPED (already complete)")
            else:
                success, message = run_evaluation(
                    config=config,
                    output_dir=output_dir,
                    dry_run=dry_run,
                )

                if success:
                    checkpoint["evaluation_complete"] = True
                    print(f"Evaluation: OK ({message})")
                else:
                    print(f"Evaluation: FAILED ({message})")
                    results["evaluation_failed"] = message

            save_checkpoint(checkpoint_path, checkpoint)
            print()

    # Summary
    print("=" * 70)
    print("Phase 1 Summary")
    print("=" * 70)
    print(f"Detection passes: {len(results['completed_passes'])}/{num_passes} complete")
    print(f"Failed passes: {len(results['failed_passes'])}")
    print(f"Merge: {'Complete' if checkpoint.get('merge_complete') else 'Pending'}")
    print(f"Evaluation: {'Complete' if checkpoint.get('evaluation_complete') else 'Pending'}")
    print(f"Checkpoint: {checkpoint_path}")
    print()

    if checkpoint.get("evaluation_complete"):
        print("Next steps:")
        print("  1. Review accuracy report in outputs/phase1-library/")
        print("  2. Run hard example extraction (see studies/phase1-library.yaml)")
        print("  3. Create symlinks in inputs/examples/neutral-naming/")
        print()

    return results


def main():
    """Main entry point for Phase 1 runner."""
    parser = argparse.ArgumentParser(
        description="Run Phase 1: Library Construction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full Phase 1
  python scripts/run_phase1.py

  # Dry run (show commands without executing)
  python scripts/run_phase1.py --dry-run

  # Resume from checkpoint
  python scripts/run_phase1.py --resume

  # Run fewer passes for testing
  python scripts/run_phase1.py --passes 2
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint, skipping completed passes",
    )
    parser.add_argument(
        "--passes",
        type=int,
        help="Override number of passes (default: 5)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Timeout in seconds per pass (default: 1800)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Locate study file
    study_path = PROJECT_ROOT / "studies" / "phase1-library.yaml"

    if not study_path.exists():
        print(f"ERROR: Study file not found: {study_path}")
        sys.exit(1)

    # Run study
    results = run_phase1(
        study_path=study_path,
        dry_run=args.dry_run,
        resume=args.resume,
        passes=args.passes,
        verbose=not args.quiet,
        timeout=args.timeout,
    )

    # Exit code based on results
    if results.get("error"):
        sys.exit(1)
    elif results.get("failed_passes"):
        sys.exit(2)  # Partial failure
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
