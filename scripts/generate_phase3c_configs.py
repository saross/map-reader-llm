#!/usr/bin/env python3
"""
Generate Phase 3c (H9 Diversity) config JSON files for both tracks.

This script produces the prompt config files needed for the 5-condition
H9 diversity experiment:
  A: Baseline (identical passes)
  B: Text diversity (V1-V5 instruction variants)
  C: Image diversity (HN rotation across passes) — Track 1 only
  D: Temperature diversity (T_opt +/- offsets, uses A config)
  E: Full diversity (text + image + temperature combined)

Track 1 (Image): library_plus-hp composition + HN core (Scale-8, 17 examples)
Track 2 (Text-only): Same composition, include_example_images=false

HN Rotation Design (Condition C / E):
  16 HN in pool: core [11-14] + expanded [18-29]
  Each pass gets 4 HN, each HN appears 1-2 times across 5 passes:
    Pass 1: HN {11, 18, 22, 26}
    Pass 2: HN {12, 19, 23, 27}
    Pass 3: HN {13, 20, 24, 28}
    Pass 4: HN {14, 21, 25, 29}
    Pass 5: HN {11, 19, 24, 29}

Usage:
    python scripts/generate_phase3c_configs.py
    python scripts/generate_phase3c_configs.py --dry-run
"""

import json
from pathlib import Path


# ── Constants ───────────────────────────────────────────────────────

CONFIGS_DIR = Path(__file__).parent.parent / "prompts" / "configs"

# Base instruction files
BASE_INSTRUCTION = "detect_brief-text-image.md"
VARIANT_INSTRUCTIONS = [
    "detect_brief-text-image_v1.md",
    "detect_brief-text-image_v2.md",
    "detect_brief-text-image_v3.md",
    "detect_brief-text-image_v4.md",
    "detect_brief-text-image_v5.md",
]

# Shared example categories (frozen across all conditions)
CANON_POSITIVES = [
    {"path": "neutral-naming/example_01.png", "label": "Positive", "category": "canonical_positive"},
    {"path": "neutral-naming/example_02.png", "label": "Positive", "category": "canonical_positive"},
    {"path": "neutral-naming/example_03.png", "label": "Positive", "category": "canonical_positive"},
    {"path": "neutral-naming/example_04.png", "label": "Positive", "category": "canonical_positive"},
]

HARD_POSITIVES = [
    {"path": "neutral-naming/example_05.png", "label": "Positive", "category": "hard_positive"},
    {"path": "neutral-naming/example_06.png", "label": "Positive", "category": "hard_positive"},
    {"path": "neutral-naming/example_07.png", "label": "Positive", "category": "hard_positive"},
    {"path": "neutral-naming/example_08.png", "label": "Positive", "category": "hard_positive"},
]

CANON_NEGATIVES = [
    {"path": "neutral-naming/example_09.png", "label": "Negative", "category": "canonical_negative"},
    {"path": "neutral-naming/example_10.png", "label": "Negative", "category": "canonical_negative"},
]

NULL_TILES = [
    {"path": "neutral-naming/example_15.png", "label": "Negative", "category": "null"},
    {"path": "neutral-naming/example_16.png", "label": "Negative", "category": "null"},
    {"path": "neutral-naming/example_17.png", "label": "Negative", "category": "null"},
]

# Hard negative sets for rotation
# Core HN (examples 11-14): used by Condition A baseline
HN_CORE = [
    {"path": "neutral-naming/example_11.png", "label": "Negative", "category": "hard_negative"},
    {"path": "neutral-naming/example_12.png", "label": "Negative", "category": "hard_negative"},
    {"path": "neutral-naming/example_13.png", "label": "Negative", "category": "hard_negative"},
    {"path": "neutral-naming/example_14.png", "label": "Negative", "category": "hard_negative"},
]

# Expanded HN pool (examples 18-29): used for diversity rotation
HN_POOL = {
    18: {"path": "neutral-naming/example_18.png", "label": "Negative", "category": "hard_negative"},
    19: {"path": "neutral-naming/example_19.png", "label": "Negative", "category": "hard_negative"},
    20: {"path": "neutral-naming/example_20.png", "label": "Negative", "category": "hard_negative"},
    21: {"path": "neutral-naming/example_21.png", "label": "Negative", "category": "hard_negative"},
    22: {"path": "neutral-naming/example_22.png", "label": "Negative", "category": "hard_negative"},
    23: {"path": "neutral-naming/example_23.png", "label": "Negative", "category": "hard_negative"},
    24: {"path": "neutral-naming/example_24.png", "label": "Negative", "category": "hard_negative"},
    25: {"path": "neutral-naming/example_25.png", "label": "Negative", "category": "hard_negative"},
    26: {"path": "neutral-naming/example_26.png", "label": "Negative", "category": "hard_negative"},
    27: {"path": "neutral-naming/example_27.png", "label": "Negative", "category": "hard_negative"},
    28: {"path": "neutral-naming/example_28.png", "label": "Negative", "category": "hard_negative"},
    29: {"path": "neutral-naming/example_29.png", "label": "Negative", "category": "hard_negative"},
}

# HN rotation schedule: which HN indices each pass receives
# Designed so each of 16 HN appears 1-2 times, no pass matches A's core set
HN_ROTATION = {
    1: [11, 18, 22, 26],
    2: [12, 19, 23, 27],
    3: [13, 20, 24, 28],
    4: [14, 21, 25, 29],
    5: [11, 19, 24, 29],
}

# Temperature diversity schedule (centred on T_opt = 0.7)
TEMP_SCHEDULE = [0.4, 0.55, 0.7, 0.85, 1.0]

# Optimal temperature from Phase 3a
T_OPT = 0.7


# ── Helper functions ────────────────────────────────────────────────

def _hn_examples(indices: list[int]) -> list[dict]:
    """Build HN example list from indices."""
    all_hn = {}
    for ex in HN_CORE:
        # Extract index from path
        idx = int(ex["path"].split("example_")[1].split(".")[0])
        all_hn[idx] = ex
    all_hn.update(HN_POOL)
    return [dict(all_hn[i]) for i in indices]


def _build_examples(hn_indices: list[int] | None = None) -> list[dict]:
    """Build full example list with specified HN set (default: core 11-14)."""
    if hn_indices is None:
        hn_indices = [11, 12, 13, 14]
    return (
        list(CANON_POSITIVES)
        + list(HARD_POSITIVES)
        + list(CANON_NEGATIVES)
        + _hn_examples(hn_indices)
        + list(NULL_TILES)
    )


def _build_config(
    *,
    version: str,
    description: str,
    hypothesis: str,
    instruction_file: str,
    examples: list[dict],
    include_images: bool = True,
    note: str = "",
) -> dict:
    """Build a complete config dictionary."""
    config = {
        "version": version,
        "description": description,
        "hypothesis": hypothesis,
        "model": "gemini-3-flash",
        "instruction_file": instruction_file,
        "temperature": T_OPT,
        "max_output_tokens": 8192,
        "thinking_level": "high",
    }
    if not include_images:
        config["include_example_images"] = False
    config["composition"] = {
        "canonical_positive": 4,
        "hard_positive": 4,
        "canonical_negative": 2,
        "hard_negative": 4,
        "null": 3,
    }
    config["total_examples"] = len(examples)
    config["examples"] = examples
    if note:
        config["note"] = note
    return config


# ── Config generators ───────────────────────────────────────────────

def generate_track1_configs() -> dict[str, dict]:
    """Generate all Track 1 (image) config files."""
    configs = {}

    # Condition A: baseline (identical passes) — also used by D with temp override
    configs["phase3c-t1-h9A.json"] = _build_config(
        version="phase3c-t1-h9A",
        description=(
            "Phase 3c H9-A — Track 1 (Image). Baseline: identical passes. "
            "Scale-8 composition with core HN. Also used by H9-D (temperature override)."
        ),
        hypothesis="H9-A",
        instruction_file=BASE_INSTRUCTION,
        examples=_build_examples(),
        note=(
            "Scale-8 composition (4 Canon+, 4 HP, 2 Canon-, 4 HN core, 3 null). "
            "Based on library_plus-hp with HN 11-14 added for fair H9 comparison."
        ),
    )

    # Condition B: text diversity (V1-V5 instruction variants)
    for i, instr in enumerate(VARIANT_INSTRUCTIONS, 1):
        configs[f"phase3c-t1-h9B-v{i}.json"] = _build_config(
            version=f"phase3c-t1-h9B-v{i}",
            description=(
                f"Phase 3c H9-B — Track 1 (Image). Text diversity: variant {i}."
            ),
            hypothesis="H9-B",
            instruction_file=instr,
            examples=_build_examples(),
        )

    # Condition C: image diversity (HN rotation)
    for pass_num, hn_indices in HN_ROTATION.items():
        hn_str = ", ".join(str(i) for i in hn_indices)
        configs[f"phase3c-t1-h9C-img{pass_num}.json"] = _build_config(
            version=f"phase3c-t1-h9C-img{pass_num}",
            description=(
                f"Phase 3c H9-C — Track 1 (Image). Image diversity: "
                f"HN rotation pass {pass_num} (HN {hn_str})."
            ),
            hypothesis="H9-C",
            instruction_file=BASE_INSTRUCTION,
            examples=_build_examples(hn_indices),
            note=f"HN rotation pass {pass_num}: examples {hn_str}.",
        )

    # Condition E: full diversity (text + image + temperature)
    for pass_num in range(1, 6):
        instr = VARIANT_INSTRUCTIONS[pass_num - 1]
        hn_indices = HN_ROTATION[pass_num]
        hn_str = ", ".join(str(i) for i in hn_indices)
        configs[f"phase3c-t1-h9E-p{pass_num}.json"] = _build_config(
            version=f"phase3c-t1-h9E-p{pass_num}",
            description=(
                f"Phase 3c H9-E — Track 1 (Image). Full diversity: "
                f"pass {pass_num} (V{pass_num} + HN {hn_str} + "
                f"T={TEMP_SCHEDULE[pass_num - 1]})."
            ),
            hypothesis="H9-E",
            instruction_file=instr,
            examples=_build_examples(hn_indices),
            note=(
                f"Full diversity pass {pass_num}: instruction V{pass_num}, "
                f"HN rotation [{hn_str}]. Temperature set via YAML override."
            ),
        )

    return configs


def generate_track2_configs() -> dict[str, dict]:
    """Generate all Track 2 (text-only) config files."""
    configs = {}

    # Condition A: baseline — also used by D (temp override) and C (degenerate)
    configs["phase3c-t2-h9A.json"] = _build_config(
        version="phase3c-t2-h9A",
        description=(
            "Phase 3c H9-A — Track 2 (Text-only). Baseline: identical passes. "
            "Also used by H9-D (temperature override). H9-C is degenerate for "
            "text-only track (no images sent)."
        ),
        hypothesis="H9-A",
        instruction_file=BASE_INSTRUCTION,
        examples=_build_examples(),
        include_images=False,
        note=(
            "Scale-8 composition with include_example_images=false. "
            "Images are listed for config consistency but not sent to the model."
        ),
    )

    # Condition B: text diversity (V1-V5) — also used by E (temp override)
    for i, instr in enumerate(VARIANT_INSTRUCTIONS, 1):
        configs[f"phase3c-t2-h9B-v{i}.json"] = _build_config(
            version=f"phase3c-t2-h9B-v{i}",
            description=(
                f"Phase 3c H9-B — Track 2 (Text-only). Text diversity: "
                f"variant {i}. Also used by H9-E (with temperature override)."
            ),
            hypothesis="H9-B",
            instruction_file=instr,
            examples=_build_examples(),
            include_images=False,
        )

    return configs


def main() -> None:
    """Generate and write all Phase 3c config files."""
    import sys

    dry_run = "--dry-run" in sys.argv

    t1_configs = generate_track1_configs()
    t2_configs = generate_track2_configs()

    all_configs = {**t1_configs, **t2_configs}

    print(f"Phase 3c config generation: {len(all_configs)} files")
    print(f"  Track 1 (Image):     {len(t1_configs)} configs")
    print(f"  Track 2 (Text-only): {len(t2_configs)} configs")
    print()

    for filename, config in sorted(all_configs.items()):
        path = CONFIGS_DIR / filename
        if dry_run:
            print(f"  [DRY RUN] Would write: {path}")
        else:
            with open(path, "w") as f:
                json.dump(config, f, indent=4)
                f.write("\n")  # Trailing newline
            print(f"  Wrote: {path.name}")

    print()
    if dry_run:
        print("Dry run complete. No files written.")
    else:
        print(f"Done. {len(all_configs)} config files written to {CONFIGS_DIR}/")

    # Summary of HN rotation
    print()
    print("HN Rotation Schedule (Conditions C and E, Track 1):")
    for pass_num, indices in sorted(HN_ROTATION.items()):
        print(f"  Pass {pass_num}: HN {indices}")

    # Verify constraints
    from collections import Counter
    all_hn_uses = Counter()
    for indices in HN_ROTATION.values():
        for idx in indices:
            all_hn_uses[idx] += 1
    print()
    print("HN frequency check (must be 1-3 each):")
    for idx in sorted(all_hn_uses):
        count = all_hn_uses[idx]
        status = "OK" if 1 <= count <= 3 else "VIOLATION"
        print(f"  HN {idx}: {count} appearances [{status}]")

    all_16 = set(range(11, 15)) | set(range(18, 30))
    used = set(all_hn_uses.keys())
    unused = all_16 - used
    if unused:
        print(f"  WARNING: Unused HN: {sorted(unused)}")
    else:
        print(f"  All 16 HN used. Total slots: {sum(all_hn_uses.values())}/20")


if __name__ == "__main__":
    main()
