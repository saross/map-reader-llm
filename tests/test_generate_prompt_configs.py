"""Tier 1 unit tests for generate_prompt_configs.py.

Tests config generation, example ordering, and image copying.
Uses temporary directories with synthetic config and pool files.
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from generate_prompt_configs import generate_config  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def setup_dirs(tmp_path):
    """Create synthetic base config, pool, and output directories.

    Base config has 4 canonical pos, 2 canonical neg, 3 nulls,
    4 hard pos, 4 hard neg = 17 examples (matching real config).
    Pool has 2 HP + 3 HN with crop files.
    """
    # Base config
    config_dir = tmp_path / "prompts" / "configs"
    config_dir.mkdir(parents=True)
    examples_root = tmp_path / "prompts" / "examples" / "neutral-naming"
    examples_root.mkdir(parents=True)

    examples = []
    idx = 1
    for cat, label, count in [
        ("canonical_positive", "Positive", 4),
        ("hard_positive", "Positive", 4),
        ("canonical_negative", "Negative", 2),
        ("hard_negative", "Negative", 4),
        ("null", "Negative", 3),
    ]:
        for _ in range(count):
            name = f"example_{idx:02d}.png"
            (examples_root / name).write_bytes(b"PNG_FAKE")
            examples.append({
                "path": f"neutral-naming/{name}",
                "label": label,
                "category": cat,
            })
            idx += 1

    config = {
        "version": "detect_brief-text",
        "description": "Test baseline config.",
        "hypothesis": "H10",
        "model": "gemini-3-flash",
        "instruction_file": "detect_brief-text.md",
        "temperature": 0.0,
        "max_output_tokens": 8192,
        "include_example_images": True,
        "examples": examples,
        "ordering_note": "canonical-first",
        "thinking_level": "minimal",
    }

    config_path = config_dir / "detect_brief-text.json"
    config_path.write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8",
    )

    # Pool directory with selected examples
    pool_dir = tmp_path / "pool"
    crops_dir = pool_dir / "crops"
    crops_dir.mkdir(parents=True)

    hp_crops = []
    for i in range(2):
        crop = crops_dir / f"hp_{i + 1:02d}.png"
        crop.write_bytes(b"HP_CROP_FAKE")
        hp_crops.append({
            "x": 100 + i * 100,
            "y": 200,
            "difficulty_score": 0.9 - i * 0.1,
            "map_name": "TestMap",
            "crop_path": str(crop),
        })

    hn_crops = []
    for i in range(3):
        crop = crops_dir / f"hn_{i + 1:02d}.png"
        crop.write_bytes(b"HN_CROP_FAKE")
        hn_crops.append({
            "x": 500 + i * 100,
            "y": 600,
            "difficulty_score": 0.8 - i * 0.1,
            "map_name": "TestMap",
            "crop_path": str(crop),
        })

    pool_examples = {
        "hard_positives": hp_crops,
        "hard_negatives": hn_crops,
    }
    (pool_dir / "selected_examples.json").write_text(
        json.dumps(pool_examples, indent=2) + "\n", encoding="utf-8",
    )

    output_dir = tmp_path / "output"

    return config_path, pool_dir, output_dir


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.tier1
class TestGenerateConfig:
    """Tests for prompt config generation."""

    def test_config_file_created(self, setup_dirs):
        """Output config JSON file should exist."""
        config_path, pool_dir, output_dir = setup_dirs
        result = generate_config(
            config_path, pool_dir, output_dir,
            condition_name="test_pool",
        )
        assert result.exists()
        assert result.suffix == ".json"

    def test_preserved_examples_kept(self, setup_dirs):
        """Canonical positives, canonical negatives, and nulls should
        be preserved from the base config."""
        config_path, pool_dir, output_dir = setup_dirs
        result = generate_config(
            config_path, pool_dir, output_dir,
            condition_name="test_pool",
        )

        with open(result) as f:
            config = json.load(f)

        cats = [e["category"] for e in config["examples"]]
        assert cats.count("canonical_positive") == 4
        assert cats.count("canonical_negative") == 2
        assert cats.count("null") == 3

    def test_hard_examples_replaced(self, setup_dirs):
        """Hard positives and negatives should come from the pool,
        not the base config."""
        config_path, pool_dir, output_dir = setup_dirs
        result = generate_config(
            config_path, pool_dir, output_dir,
            condition_name="test_pool",
        )

        with open(result) as f:
            config = json.load(f)

        cats = [e["category"] for e in config["examples"]]
        # Pool has 2 HP + 3 HN (not the base's 4+4)
        assert cats.count("hard_positive") == 2
        assert cats.count("hard_negative") == 3

    def test_total_example_count(self, setup_dirs):
        """Total examples = preserved + pool HP + pool HN."""
        config_path, pool_dir, output_dir = setup_dirs
        result = generate_config(
            config_path, pool_dir, output_dir,
            condition_name="test_pool",
        )

        with open(result) as f:
            config = json.load(f)

        # 4 canonical_pos + 2 canonical_neg + 3 null + 2 HP + 3 HN = 14
        assert len(config["examples"]) == 14

    def test_version_includes_condition(self, setup_dirs):
        """Config version should include the condition name."""
        config_path, pool_dir, output_dir = setup_dirs
        result = generate_config(
            config_path, pool_dir, output_dir,
            condition_name="pool_160_hp4hn4",
        )

        with open(result) as f:
            config = json.load(f)

        assert "pool_160_hp4hn4" in config["version"]

    def test_base_config_fields_preserved(self, setup_dirs):
        """Non-example fields from base config should be preserved."""
        config_path, pool_dir, output_dir = setup_dirs
        result = generate_config(
            config_path, pool_dir, output_dir,
            condition_name="test_pool",
        )

        with open(result) as f:
            config = json.load(f)

        assert config["model"] == "gemini-3-flash"
        assert config["temperature"] == 0.0
        assert config["instruction_file"] == "detect_brief-text.md"
        assert config["thinking_level"] == "minimal"

    def test_example_images_copied(self, setup_dirs):
        """Crop images should be copied to the neutral-naming dir."""
        config_path, pool_dir, output_dir = setup_dirs
        generate_config(
            config_path, pool_dir, output_dir,
            condition_name="test_pool",
        )

        examples_dir = (
            output_dir / "examples" / "test_pool" / "neutral-naming"
        )
        assert examples_dir.exists()
        png_files = list(examples_dir.glob("*.png"))
        # 4 canonical_pos + 2 canonical_neg + 3 null + 2 HP + 3 HN = 14
        assert len(png_files) == 14

    def test_sequential_numbering(self, setup_dirs):
        """Example paths should use sequential numbering."""
        config_path, pool_dir, output_dir = setup_dirs
        result = generate_config(
            config_path, pool_dir, output_dir,
            condition_name="test_pool",
        )

        with open(result) as f:
            config = json.load(f)

        for i, e in enumerate(config["examples"]):
            expected = f"neutral-naming/example_{i + 1:02d}.png"
            assert e["path"] == expected, (
                f"Example {i}: expected {expected}, got {e['path']}"
            )

    def test_pool_source_recorded(self, setup_dirs):
        """Config should record where the pool came from."""
        config_path, pool_dir, output_dir = setup_dirs
        result = generate_config(
            config_path, pool_dir, output_dir,
            condition_name="test_pool",
        )

        with open(result) as f:
            config = json.load(f)

        assert "pool_source" in config
