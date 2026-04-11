#!/usr/bin/env python3
"""Assemble prompt config JSONs from example pools.

Takes a base config (e.g., ``detect_brief-text.json``) and replaces the
hard-positive and hard-negative examples with those selected by
``build_example_pool.py``, while keeping canonical positives, canonical
negatives, and null tiles unchanged.

Also copies the cropped example images into the neutral-naming directory
expected by the detection pipeline.

Usage:
    python scripts/generate_prompt_configs.py \\
        --pool outputs/h10/example-pools/pool_160_hp4hn4/ \\
        --base-config prompts/configs/detect_brief-text.json \\
        --output-dir prompts/configs/h10/

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

logger = logging.getLogger(__name__)

# =========================================================================
# Constants
# =========================================================================

_REPO_ROOT = _SCRIPT_DIR.parent

# Categories that are replaced by the pool builder
_REPLACEABLE_CATEGORIES = {"hard_positive", "hard_negative"}

# Categories preserved from the base config
_PRESERVED_CATEGORIES = {"canonical_positive", "canonical_negative", "null"}


# =========================================================================
# Config generation
# =========================================================================


def generate_config(
    base_config_path: Path,
    pool_dir: Path,
    output_dir: Path,
    condition_name: str | None = None,
) -> Path:
    """Generate a new prompt config from a base config and example pool.

    Reads the base config, keeps all non-hard examples (canonical
    positives, canonical negatives, nulls), and replaces hard positives
    and hard negatives with those from the pool. Copies crop images
    into a neutral-naming directory under the output config location.

    Args:
        base_config_path: Path to the base prompt config JSON.
        pool_dir: Path to the example pool directory (must contain
            ``selected_examples.json`` and ``crops/``).
        output_dir: Target directory for the generated config and
            example images.
        condition_name: Optional name for the condition (used in the
            config ``version`` and ``description`` fields). Defaults
            to the pool directory name.

    Returns:
        Path to the generated config JSON file.
    """
    # Load base config
    with open(base_config_path, encoding="utf-8") as f:
        base_config = json.load(f)

    # Load pool examples
    pool_examples_path = pool_dir / "selected_examples.json"
    with open(pool_examples_path, encoding="utf-8") as f:
        pool_data = json.load(f)

    hp_selected = pool_data.get("hard_positives", [])
    hn_selected = pool_data.get("hard_negatives", [])

    cond = condition_name or pool_dir.name

    # Set up neutral-naming directory for images
    output_dir.mkdir(parents=True, exist_ok=True)
    examples_dir = output_dir / "examples" / cond / "neutral-naming"
    examples_dir.mkdir(parents=True, exist_ok=True)

    # Preserve canonical and null examples from base config
    preserved = [
        e for e in base_config.get("examples", [])
        if e.get("category") in _PRESERVED_CATEGORIES
    ]

    # Copy preserved example images to new location
    base_examples_root = base_config_path.parent.parent / "examples"
    new_examples: list[dict] = []
    example_idx = 1

    for entry in preserved:
        src_path = base_examples_root / entry["path"]
        new_name = f"example_{example_idx:02d}.png"
        dst_path = examples_dir / new_name
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
        else:
            logger.warning(
                "Preserved example not found: %s", src_path,
            )
        new_examples.append({
            "path": f"neutral-naming/{new_name}",
            "label": entry["label"],
            "category": entry["category"],
        })
        example_idx += 1

    # Add hard positives from pool
    for hp in hp_selected:
        new_name = f"example_{example_idx:02d}.png"
        dst_path = examples_dir / new_name
        src_crop = hp.get("crop_path")
        if src_crop and Path(src_crop).exists():
            shutil.copy2(src_crop, dst_path)
        else:
            logger.warning(
                "HP crop not found: %s (will use placeholder)",
                src_crop,
            )
        new_examples.append({
            "path": f"neutral-naming/{new_name}",
            "label": "Positive",
            "category": "hard_positive",
        })
        example_idx += 1

    # Add hard negatives from pool
    for hn in hn_selected:
        new_name = f"example_{example_idx:02d}.png"
        dst_path = examples_dir / new_name
        src_crop = hn.get("crop_path")
        if src_crop and Path(src_crop).exists():
            shutil.copy2(src_crop, dst_path)
        else:
            logger.warning(
                "HN crop not found: %s (will use placeholder)",
                src_crop,
            )
        new_examples.append({
            "path": f"neutral-naming/{new_name}",
            "label": "Negative",
            "category": "hard_negative",
        })
        example_idx += 1

    # Build the new config
    new_config = dict(base_config)
    new_config["version"] = f"{base_config['version']}_{cond}"
    new_config["description"] = (
        f"Auto-generated from {base_config['version']} with pool "
        f"{cond}: {len(hp_selected)} HP + {len(hn_selected)} HN."
    )
    new_config["examples"] = new_examples
    new_config["pool_source"] = str(pool_dir)

    # Write config
    config_filename = f"detect_{cond}.json"
    config_path = output_dir / config_filename
    config_path.write_text(
        json.dumps(new_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info(
        "Generated config %s: %d examples "
        "(%d preserved + %d HP + %d HN)",
        config_filename, len(new_examples),
        len(preserved), len(hp_selected), len(hn_selected),
    )

    return config_path


# =========================================================================
# CLI
# =========================================================================


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate prompt configs from example pools.",
    )
    parser.add_argument(
        "--pool", type=Path, required=True,
        help="Path to example pool directory (from build_example_pool.py)",
    )
    parser.add_argument(
        "--base-config", type=Path, required=True,
        help="Path to base prompt config JSON",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for generated config and examples",
    )
    parser.add_argument(
        "--condition-name", type=str, default=None,
        help="Condition name (default: pool directory name)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config_path = generate_config(
        base_config_path=args.base_config,
        pool_dir=args.pool,
        output_dir=args.output_dir,
        condition_name=args.condition_name,
    )

    print(f"\nGenerated config: {config_path}")


if __name__ == "__main__":
    main()
