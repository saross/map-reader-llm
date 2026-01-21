#!/usr/bin/env python3
"""
Pre-Flight Check Script
=======================

Validates that all required inputs are in place before running detection experiments.

Usage:
    python scripts/preflight_check.py
    python scripts/preflight_check.py --phase 1
    python scripts/preflight_check.py --config prompts/configs/detect_image-only.json
    python scripts/preflight_check.py --verbose

Checks:
    - API key configured
    - Tile directories exist
    - Ground truth files present
    - Region bounds files present
    - Example library images present
    - Config files valid

Exit Codes:
    0 - All checks passed
    1 - One or more checks failed

Author: Shawn Ross, Claude Code
Version: 1.0.0
Licence: Apache 2.0
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Script version
__version__ = "1.0.0"

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent


def check_api_key(verbose: bool = False) -> tuple[bool, str]:
    """
    Check if Google API key is configured.

    Returns:
        Tuple of (passed: bool, message: str)
    """
    # Check environment variable first
    api_key = os.environ.get("GOOGLE_API_KEY", "")

    if not api_key:
        # Try loading from config.py
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from config import GOOGLE_API_KEY
            api_key = GOOGLE_API_KEY or ""
        except ImportError:
            pass

    if api_key:
        # Show first few characters for verification
        preview = api_key[:10] + "..." if len(api_key) > 10 else api_key
        return True, f"API key configured ({preview})"
    else:
        return False, "GOOGLE_API_KEY not set in environment or config.py"


def check_directory_exists(
    path: Path, description: str, min_files: int = 0, pattern: str = "*"
) -> tuple[bool, str]:
    """
    Check if a directory exists and optionally has minimum files.

    Args:
        path: Directory path to check
        description: Human-readable description
        min_files: Minimum number of files expected (0 = just check exists)
        pattern: Glob pattern for counting files

    Returns:
        Tuple of (passed: bool, message: str)
    """
    if not path.exists():
        return False, f"{description}: Directory not found ({path})"

    if min_files > 0:
        files = list(path.glob(pattern))
        if len(files) < min_files:
            return False, f"{description}: Found {len(files)} files, expected {min_files}+ ({path})"
        return True, f"{description}: OK ({len(files)} files)"

    return True, f"{description}: OK"


def check_file_exists(path: Path, description: str) -> tuple[bool, str]:
    """
    Check if a file exists.

    Args:
        path: File path to check
        description: Human-readable description

    Returns:
        Tuple of (passed: bool, message: str)
    """
    if path.exists():
        return True, f"{description}: OK"
    else:
        return False, f"{description}: File not found ({path})"


def check_example_library(verbose: bool = False) -> list[tuple[bool, str]]:
    """
    Check that example library images exist.

    Returns:
        List of (passed, message) tuples
    """
    results = []
    examples_dir = PROJECT_ROOT / "inputs" / "examples" / "neutral-naming"

    # Required examples for baseline
    baseline_examples = [
        ("example_01.png", "Canon+ (burial mound)"),
        ("example_02.png", "Canon+ (settlement mound)"),
        ("example_03.png", "Canon+ (triangulation on mound)"),
        ("example_04.png", "Canon+ (benchmark on mound)"),
        ("example_15.png", "Null (empty tile 1)"),
        ("example_16.png", "Null (empty tile 2)"),
        ("example_17.png", "Null (empty tile 3)"),
    ]

    # Additional examples for Scale-8 library
    scale8_examples = [
        ("example_05.png", "HP (hard positive 1)"),
        ("example_06.png", "HP (hard positive 2)"),
        ("example_07.png", "HP (hard positive 3)"),
        ("example_08.png", "HP (hard positive 4)"),
        ("example_09.png", "Canon- (triangulation alone)"),
        ("example_10.png", "Canon- (benchmark alone)"),
        ("example_11.png", "HN (hard negative 1)"),
        ("example_12.png", "HN (hard negative 2)"),
        ("example_13.png", "HN (hard negative 3)"),
        ("example_14.png", "HN (hard negative 4)"),
    ]

    # Check baseline examples
    for filename, desc in baseline_examples:
        path = examples_dir / filename
        if path.exists():
            results.append((True, f"Example {filename}: OK ({desc})"))
        else:
            results.append((False, f"Example {filename}: MISSING ({desc})"))

    # Check Scale-8 examples (warn but don't fail - created in Phase 1)
    missing_scale8 = []
    for filename, desc in scale8_examples:
        path = examples_dir / filename
        if not path.exists():
            missing_scale8.append(filename)

    if missing_scale8:
        results.append((
            True,  # Don't fail - these are created during Phase 1
            f"Scale-8 examples: {len(missing_scale8)} pending (created in Phase 1)"
        ))

    return results


def check_config(config_path: Path, verbose: bool = False) -> list[tuple[bool, str]]:
    """
    Validate a config file and check its referenced files exist.

    Args:
        config_path: Path to config JSON file
        verbose: If True, show detailed checks

    Returns:
        List of (passed, message) tuples
    """
    results = []

    # Check config exists
    if not config_path.exists():
        results.append((False, f"Config file not found: {config_path}"))
        return results

    # Load and parse config
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        results.append((True, f"Config syntax: OK ({config_path.name})"))
    except json.JSONDecodeError as e:
        results.append((False, f"Config JSON invalid: {e}"))
        return results

    # Check required fields
    required_fields = ["version", "model", "instruction_file"]
    for field in required_fields:
        if field not in config:
            results.append((False, f"Config missing field: {field}"))
        elif verbose:
            results.append((True, f"Config field '{field}': {config[field]}"))

    # Check instruction file exists
    instruction_file = config.get("instruction_file", "")
    if instruction_file:
        instruction_path = (
            PROJECT_ROOT / "prompts" / "system-instructions" / instruction_file
        )
        if instruction_path.exists():
            results.append((True, f"System instruction: OK ({instruction_file})"))
        else:
            results.append((False, f"System instruction not found: {instruction_path}"))

    # Check example images
    examples = config.get("examples", [])
    examples_dir = PROJECT_ROOT / "inputs" / "examples"
    missing_examples = []

    for ex in examples:
        ex_path = ex.get("path", "")
        if ex_path:
            full_path = examples_dir / ex_path
            if not full_path.exists():
                missing_examples.append(ex_path)

    if missing_examples:
        results.append((
            False,
            f"Config examples missing: {len(missing_examples)} ({', '.join(missing_examples[:3])}...)"
        ))
    elif examples:
        results.append((True, f"Config examples: OK ({len(examples)} images)"))

    return results


def run_preflight_checks(
    phase: int | None = None,
    config_path: Path | None = None,
    verbose: bool = False,
) -> tuple[int, int]:
    """
    Run all pre-flight checks.

    Args:
        phase: Optional phase number to check (1, 2, 3, 4)
        config_path: Optional specific config to validate
        verbose: If True, show all check details

    Returns:
        Tuple of (passed_count, failed_count)
    """
    all_results = []

    print("=" * 60)
    print("PRE-FLIGHT CHECKS")
    print("=" * 60)
    print()

    # 1. API Key
    print("1. API Configuration")
    print("-" * 40)
    passed, msg = check_api_key(verbose)
    all_results.append((passed, msg))
    status = "OK" if passed else "FAIL"
    print(f"   [{status}] {msg}")
    print()

    # 2. Tile Directories
    print("2. Tile Directories")
    print("-" * 40)
    tiles_dir = PROJECT_ROOT / "inputs" / "tiles"
    passed, msg = check_directory_exists(tiles_dir, "Tiles base directory")
    all_results.append((passed, msg))
    status = "OK" if passed else "FAIL"
    print(f"   [{status}] {msg}")

    # Check for map subdirectories
    if tiles_dir.exists():
        map_dirs = [d for d in tiles_dir.iterdir() if d.is_dir()]
        if map_dirs:
            print(f"   [OK] Found {len(map_dirs)} map directories")
            for d in map_dirs[:5]:
                tiles = list(d.glob("*.png"))
                print(f"        - {d.name}: {len(tiles)} tiles")
            if len(map_dirs) > 5:
                print(f"        ... and {len(map_dirs) - 5} more")
        else:
            all_results.append((False, "No map directories found in tiles/"))
            print("   [FAIL] No map directories found")
    print()

    # 3. Ground Truth
    print("3. Ground Truth")
    print("-" * 40)
    gt_path = PROJECT_ROOT / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
    passed, msg = check_file_exists(gt_path, "Mounds reference")
    all_results.append((passed, msg))
    status = "OK" if passed else "FAIL"
    print(f"   [{status}] {msg}")
    print()

    # 4. Region Bounds
    print("4. Region Bounds")
    print("-" * 40)
    bounds_files = [
        ("calibration_bounds.geojson", "Calibration bounds"),
        ("validation_bounds.geojson", "Validation bounds"),
    ]
    for filename, desc in bounds_files:
        bounds_path = PROJECT_ROOT / "inputs" / "vectors" / "bounds" / filename
        passed, msg = check_file_exists(bounds_path, desc)
        all_results.append((passed, msg))
        status = "OK" if passed else "FAIL"
        print(f"   [{status}] {msg}")
    print()

    # 5. Manifests
    print("5. Tile Manifests")
    print("-" * 40)
    manifest_files = [
        ("calibration_manifest.json", "Calibration manifest"),
        ("validation_manifest.json", "Validation manifest"),
    ]
    for filename, desc in manifest_files:
        manifest_path = PROJECT_ROOT / "inputs" / "tiles" / filename
        passed, msg = check_file_exists(manifest_path, desc)
        all_results.append((passed, msg))
        status = "OK" if passed else "FAIL"
        print(f"   [{status}] {msg}")
    print()

    # 6. Example Library
    print("6. Example Library")
    print("-" * 40)
    example_results = check_example_library(verbose)
    for passed, msg in example_results:
        all_results.append((passed, msg))
        status = "OK" if passed else "FAIL"
        if verbose or not passed:
            print(f"   [{status}] {msg}")
    # Summary if not verbose
    if not verbose:
        passed_examples = sum(1 for p, _ in example_results if p)
        print(f"   [OK] {passed_examples}/{len(example_results)} example checks passed")
    print()

    # 7. Config Validation (if specified)
    if config_path:
        print("7. Config Validation")
        print("-" * 40)
        config_results = check_config(config_path, verbose)
        for passed, msg in config_results:
            all_results.append((passed, msg))
            status = "OK" if passed else "FAIL"
            print(f"   [{status}] {msg}")
        print()

    # Summary
    passed_count = sum(1 for p, _ in all_results if p)
    failed_count = len(all_results) - passed_count

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Checks passed: {passed_count}")
    print(f"Checks failed: {failed_count}")

    if failed_count == 0:
        print("\nAll pre-flight checks PASSED. Ready to run experiments.")
    else:
        print("\nSome checks FAILED. Please resolve issues before proceeding.")

    return passed_count, failed_count


def main():
    """Main entry point for pre-flight checks."""
    parser = argparse.ArgumentParser(
        description="Pre-flight validation for detection experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all checks
  python scripts/preflight_check.py

  # Validate specific config
  python scripts/preflight_check.py --config prompts/configs/detect_image-only.json

  # Verbose output
  python scripts/preflight_check.py --verbose
        """,
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4],
        help="Check requirements for specific phase",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Validate specific config file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed check output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    passed, failed = run_preflight_checks(
        phase=args.phase,
        config_path=args.config,
        verbose=args.verbose,
    )

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
