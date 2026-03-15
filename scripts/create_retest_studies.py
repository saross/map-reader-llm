#!/usr/bin/env python3
"""
Generate retest study YAMLs from original study definitions.

Reads each original study YAML, applies full-corpus retest transformations
(340-tile manifest, updated bounds, adjusted K values), and writes a
retest version to studies/retest/.

Usage::

    python scripts/create_retest_studies.py
    python scripts/create_retest_studies.py --dry-run

Created: 2026-03-15
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
from copy import deepcopy
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
RETEST_DIR = PROJECT_ROOT / "studies" / "retest"
ORIGINAL_DIR = PROJECT_ROOT / "studies"

# New manifest and bounds for full-corpus evaluation
RETEST_MANIFEST = "inputs/tiles/full_evaluation_manifest.json"
RETEST_BOUNDS = "inputs/vectors/bounds/full_evaluation_bounds.geojson"

# Studies to transform, with stage assignment and K override.
# K is determined by temperature regime:
#   - T=0.0 only → K=1
#   - T>0 (or mixed) → K=3
#   - Consensus voting → K=30
#   - Diversity → K=5 (deferred)
STUDY_TRANSFORMS = [
    # Stage 1: Single-pass phases
    {
        "source": "phase2a-h1-modality.yaml",
        "stage": 1,
        "runs": 3,  # All conditions at T=1.0
        "notes": "H1 modality/elaboration. All conditions at T=1.0.",
    },
    {
        "source": "phase2b-h7-temperature.yaml",
        "stage": 1,
        "runs": 3,  # Mix of T=0.0–1.3; accept redundant T=0.0 runs
        "notes": "H7 temperature Track 1 (image-using). T=0.0 runs redundant but cheap.",
    },
    {
        "source": "phase2b-h7-temperature-text-only.yaml",
        "stage": 1,
        "runs": 3,
        "notes": "H7 temperature Track 2 (text-only). T=0.0 runs redundant but cheap.",
    },
    {
        "source": "phase2c-h8-library.yaml",
        "stage": 1,
        "runs": 1,  # All conditions at T=0.0
        "notes": "H8 library composition Track 1 (image-using). All at T=0.0.",
    },
    {
        "source": "phase2c-h8-library-text-only.yaml",
        "stage": 1,
        "runs": 1,
        "notes": "H8 library composition Track 2 (text-only). All at T=0.0.",
    },
    {
        "source": "phase2c-exploratory-pure-positive-hp.yaml",
        "stage": 1,
        "runs": 1,
        "notes": "H8/H12 pure-positive HP scaling (exploratory). All at T=0.0.",
    },
    {
        "source": "phase2d-h5-negtext.yaml",
        "stage": 1,
        "runs": 1,
        "notes": "H5 negative text Track 1 (image-using). All at T=0.0.",
    },
    {
        "source": "phase2d-h5-negtext-text-only.yaml",
        "stage": 1,
        "runs": 1,
        "notes": "H5 negative text Track 2 (text-only). All at T=0.0.",
    },
    {
        "source": "phase2e-h4-ordering.yaml",
        "stage": 1,
        "runs": 1,
        "notes": "H4 example ordering (image-using). All at T=0.0.",
    },
    # Stage 2: Consensus voting
    {
        "source": "phase3a-h3-voting-track1.yaml",
        "stage": 2,
        "runs": 30,
        "notes": "H3 consensus voting Track 1 (image-using). K=30 for full threshold sweep.",
    },
    {
        "source": "phase3a-h3-voting-track2.yaml",
        "stage": 2,
        "runs": 30,
        "notes": "H3 consensus voting Track 2 (text-only). K=30 for full threshold sweep.",
    },
    {
        "source": "phase3a-replication.yaml",
        "stage": 2,
        "runs": 30,
        "notes": "Thinking level replication (minimal vs HIGH). K=30 at T=0.7.",
    },
    # Stage 4: Diversity (deferred — created but not run immediately)
    {
        "source": "phase3c-h9-diversity-track1.yaml",
        "stage": 4,
        "runs": 5,
        "notes": "H9 diversity Track 1 (image-using). K=5 replications. DEFERRED.",
    },
    {
        "source": "phase3c-h9-diversity-track2.yaml",
        "stage": 4,
        "runs": 5,
        "notes": "H9 diversity Track 2 (text-only). K=5 replications. DEFERRED.",
    },
]


def transform_study(source_path: Path, runs: int, notes: str) -> dict:
    """Read an original study YAML and apply retest transformations.

    Transformations:
      - inputs.manifest → full_evaluation_manifest.json
      - inputs.bounds → full_evaluation_bounds.geojson
      - execution.output_dir → outputs/retest/{original_subdir}
      - execution.runs → K value from plan
      - study.name → prepend 'Retest: '
      - study.version → '2.0-retest'
      - Add retest_notes field

    Args:
        source_path: Path to original study YAML.
        runs: Number of runs (K) for this retest.
        notes: Descriptive notes about the retest configuration.

    Returns:
        Transformed study configuration dictionary.
    """
    with open(source_path) as f:
        config = yaml.safe_load(f)

    config = deepcopy(config)

    # Update study metadata
    config["study"]["name"] = f"Retest: {config['study']['name']}"
    config["study"]["version"] = "2.0-retest"
    config["study"]["retest_notes"] = notes

    # Update inputs
    config["inputs"]["manifest"] = RETEST_MANIFEST
    config["inputs"]["bounds"] = RETEST_BOUNDS

    # Update execution
    original_output = config["execution"]["output_dir"]
    # Extract the relative part after 'outputs/'
    if original_output.startswith("outputs/"):
        relative = original_output[len("outputs/"):]
    else:
        relative = original_output
    config["execution"]["output_dir"] = f"outputs/retest/{relative}"
    config["execution"]["runs"] = runs

    # Update estimates for 340 tiles
    if "estimates" in config:
        original_calls = config["estimates"].get("api_calls_per_cell", 0)
        if original_calls > 0:
            # Scale: original was based on 60 tiles per run
            new_tiles_per_run = 340
            original_runs = config["estimates"].get(
                "total_api_calls", 0
            ) / max(original_calls, 1)

            new_calls_per_cell = int(runs * new_tiles_per_run)
            cells = config["estimates"].get("cells", 1)
            config["estimates"]["api_calls_per_cell"] = new_calls_per_cell
            config["estimates"]["total_api_calls"] = cells * new_calls_per_cell
            config["estimates"]["original_runs"] = int(original_runs)
            config["estimates"]["retest_runs"] = runs
            config["estimates"]["retest_tiles"] = new_tiles_per_run

    return config


def extract_all_conditions(config: dict, source_name: str) -> list[dict]:
    """Extract conditions from a study config for overlap analysis.

    Args:
        config: Study configuration dictionary.
        source_name: Source study filename.

    Returns:
        List of condition dictionaries with config path, temperature, etc.
    """
    conditions = []

    if "conditions" in config:
        for cond in config["conditions"]:
            if cond.get("reuse_from") or cond.get("run") is False:
                continue
            conditions.append({
                "study": source_name,
                "name": cond["name"],
                "config": cond["config"],
                "temperature": cond.get("temperature"),
                "ordering": cond.get("ordering"),
                "thinking_level": cond.get("thinking_level"),
            })
    elif "factors" in config:
        carried = config.get("carried_forward") or {}
        fixed = config.get("fixed") or {}
        for factor_name, factor_def in config["factors"].items():
            for level in factor_def.get("levels", []):
                if level.get("run_in_phase2d") is False:
                    continue
                config_path = level.get(
                    "config", carried.get("optimal_me_config", "")
                )
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
                    "study": source_name,
                    "name": level["name"],
                    "config": config_path,
                    "temperature": temperature,
                    "ordering": ordering,
                    "thinking_level": thinking_level,
                })

    return conditions


def find_overlaps(all_conditions: list[dict]) -> list[tuple]:
    """Identify duplicate conditions across studies.

    Two conditions overlap when they share the same config path,
    temperature, ordering, and thinking level.

    Args:
        all_conditions: List of all conditions across all studies.

    Returns:
        List of (condition_key, list_of_studies) tuples for duplicates.
    """
    from collections import defaultdict
    key_to_studies: dict[tuple, list[str]] = defaultdict(list)

    for cond in all_conditions:
        key = (
            cond["config"],
            cond.get("temperature"),
            cond.get("ordering"),
            cond.get("thinking_level"),
        )
        entry = f"{cond['study']}:{cond['name']}"
        key_to_studies[key].append(entry)

    overlaps = [
        (key, studies)
        for key, studies in sorted(
            key_to_studies.items(),
            key=lambda x: tuple(str(v) for v in x[0]),
        )
        if len(studies) > 1
    ]
    return overlaps


def main() -> None:
    """Generate retest study YAMLs and report overlaps."""
    parser = argparse.ArgumentParser(
        description="Generate retest study YAMLs from originals",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be created without writing files",
    )
    args = parser.parse_args()

    RETEST_DIR.mkdir(parents=True, exist_ok=True)

    all_conditions: list[dict] = []
    created = 0

    print("=" * 70)
    print("Retest Study YAML Generation")
    print("=" * 70)

    for transform in STUDY_TRANSFORMS:
        source_path = ORIGINAL_DIR / transform["source"]
        if not source_path.exists():
            print(f"\n  WARNING: Source not found: {source_path}")
            continue

        dest_path = RETEST_DIR / transform["source"]

        print(f"\n  Stage {transform['stage']}: {transform['source']}")
        print(f"    K={transform['runs']}  →  {dest_path.name}")

        # Load and transform
        config = transform_study(
            source_path, transform["runs"], transform["notes"],
        )

        # Extract conditions for overlap analysis
        with open(source_path) as f:
            original = yaml.safe_load(f)
        conditions = extract_all_conditions(original, transform["source"])
        all_conditions.extend(conditions)
        print(f"    Conditions: {len(conditions)}")

        if not args.dry_run:
            with open(dest_path, "w") as f:
                yaml.dump(
                    config, f, default_flow_style=False, sort_keys=False,
                    allow_unicode=True, width=100,
                )
            created += 1

    # Report overlaps
    overlaps = find_overlaps(all_conditions)
    print("\n" + "=" * 70)
    print("Data Reuse Map (identical conditions across studies)")
    print("=" * 70)

    if overlaps:
        for key, studies in overlaps:
            config_path, temp, ordering, thinking = key
            print(f"\n  Config: {config_path}")
            print(f"  T={temp}, ordering={ordering}, thinking={thinking}")
            print("  Shared by:")
            for s in studies:
                print(f"    - {s}")
    else:
        print("\n  No overlapping conditions found.")

    # Summary
    total_conditions = len(all_conditions)
    unique_keys = len(set(
        (c["config"], c.get("temperature"), c.get("ordering"),
         c.get("thinking_level"))
        for c in all_conditions
    ))
    overlap_count = total_conditions - unique_keys

    print(f"\n{'=' * 70}")
    print("Summary")
    print(f"{'=' * 70}")
    print(f"  Studies processed: {len(STUDY_TRANSFORMS)}")
    print(f"  Files {'would be' if args.dry_run else ''} created: "
          f"{created if not args.dry_run else len(STUDY_TRANSFORMS)}")
    print(f"  Total conditions: {total_conditions}")
    print(f"  Unique conditions: {unique_keys}")
    print(f"  Overlapping conditions: {overlap_count}")
    print(f"  Potential savings: {overlap_count} duplicate runs can be "
          f"shared across studies")


if __name__ == "__main__":
    main()
