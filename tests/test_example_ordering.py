"""
Tests for example ordering functionality in the detection script.

Tier 1 unit tests for the reorder_examples() function that enables
H4 hypothesis testing (example ordering effect on detection performance).
"""

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.tier1

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Import module with numeric prefix using importlib
_spec = importlib.util.spec_from_file_location(
    "detect_mounds_batch",
    PROJECT_ROOT / "scripts" / "4_detect_mounds_batch.py"
)
_detect_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_detect_module)
reorder_examples = _detect_module.reorder_examples


# Sample example library matching the structure in config files
SAMPLE_EXAMPLES = [
    {"path": "example_01.png", "category": "canonical-positive", "label": "Positive"},
    {"path": "example_02.png", "category": "canonical-positive", "label": "Positive"},
    {"path": "example_03.png", "category": "canonical-negative", "label": "Negative"},
    {"path": "example_04.png", "category": "canonical-negative", "label": "Negative"},
    {"path": "example_05.png", "category": "hard-positive", "label": "Positive"},
    {"path": "example_06.png", "category": "hard-positive", "label": "Positive"},
    {"path": "example_07.png", "category": "hard-negative", "label": "Negative"},
    {"path": "example_08.png", "category": "hard-negative", "label": "Negative"},
    {"path": "example_15.png", "category": "null", "label": "Empty"},
]


@pytest.mark.tier1
class TestReorderExamples:
    """Tests for the reorder_examples function."""

    def test_canonical_first_preserves_order(self) -> None:
        """canonical-first ordering should preserve the original order.

        The canonical examples should remain at the beginning of the array.
        """
        result = reorder_examples(SAMPLE_EXAMPLES.copy(), "canonical-first")

        # Should be identical to input
        assert len(result) == len(SAMPLE_EXAMPLES)
        for i, (orig, res) in enumerate(zip(SAMPLE_EXAMPLES, result)):
            assert orig["path"] == res["path"], f"Position {i} differs"

    def test_canonical_last_moves_canonical_to_end(self) -> None:
        """canonical-last ordering should move canonical examples to the end.

        Non-canonical examples (hard-*, null) should come first,
        followed by canonical-positive and canonical-negative.
        """
        result = reorder_examples(SAMPLE_EXAMPLES.copy(), "canonical-last")

        # Check that non-canonical examples come first
        n_non_canonical = sum(
            1 for e in SAMPLE_EXAMPLES
            if not e["category"].startswith("canonical")
        )
        n_canonical = len(SAMPLE_EXAMPLES) - n_non_canonical

        # First n_non_canonical should be non-canonical
        for i in range(n_non_canonical):
            assert not result[i]["category"].startswith("canonical"), \
                f"Position {i} should be non-canonical, got {result[i]['category']}"

        # Last n_canonical should be canonical
        for i in range(n_non_canonical, len(result)):
            assert result[i]["category"].startswith("canonical"), \
                f"Position {i} should be canonical, got {result[i]['category']}"

    def test_random_changes_order(self) -> None:
        """random ordering should produce a different order (statistically).

        With a fixed seed, the order should be deterministic but different
        from the original.
        """
        result = reorder_examples(SAMPLE_EXAMPLES.copy(), "random", seed=42)

        # Should have same elements
        assert len(result) == len(SAMPLE_EXAMPLES)
        orig_paths = set(e["path"] for e in SAMPLE_EXAMPLES)
        result_paths = set(e["path"] for e in result)
        assert orig_paths == result_paths, "Random ordering lost or added elements"

        # Order should be different (extremely unlikely to be same with shuffle)
        result_order = [e["path"] for e in result]
        orig_order = [e["path"] for e in SAMPLE_EXAMPLES]
        assert result_order != orig_order, "Random ordering produced identical order"

    def test_random_is_reproducible_with_seed(self) -> None:
        """random ordering with same seed should produce identical results."""
        result1 = reorder_examples(SAMPLE_EXAMPLES.copy(), "random", seed=42)
        result2 = reorder_examples(SAMPLE_EXAMPLES.copy(), "random", seed=42)

        assert result1 == result2, "Same seed should produce identical ordering"

    def test_random_different_seeds_differ(self) -> None:
        """random ordering with different seeds should produce different results."""
        result1 = reorder_examples(SAMPLE_EXAMPLES.copy(), "random", seed=42)
        result2 = reorder_examples(SAMPLE_EXAMPLES.copy(), "random", seed=123)

        result1_order = [e["path"] for e in result1]
        result2_order = [e["path"] for e in result2]

        assert result1_order != result2_order, "Different seeds should produce different orderings"

    def test_unknown_ordering_returns_original(self) -> None:
        """Unknown ordering strategy should return original order with warning."""
        result = reorder_examples(SAMPLE_EXAMPLES.copy(), "unknown-strategy")

        # Should return original order
        for i, (orig, res) in enumerate(zip(SAMPLE_EXAMPLES, result)):
            assert orig["path"] == res["path"], f"Position {i} differs"

    def test_empty_list_returns_empty(self) -> None:
        """Empty example list should return empty list."""
        result = reorder_examples([], "canonical-last")
        assert result == []

    def test_no_canonical_examples(self) -> None:
        """canonical-last with no canonical examples should preserve order."""
        non_canonical_only = [
            {"path": "ex1.png", "category": "hard-positive", "label": "Positive"},
            {"path": "ex2.png", "category": "hard-negative", "label": "Negative"},
            {"path": "ex3.png", "category": "null", "label": "Empty"},
        ]
        result = reorder_examples(non_canonical_only.copy(), "canonical-last")

        # Should preserve order since no canonical to move
        for i, (orig, res) in enumerate(zip(non_canonical_only, result)):
            assert orig["path"] == res["path"]

    def test_only_canonical_examples(self) -> None:
        """canonical-last with only canonical examples should preserve order."""
        canonical_only = [
            {"path": "ex1.png", "category": "canonical-positive", "label": "Positive"},
            {"path": "ex2.png", "category": "canonical-negative", "label": "Negative"},
        ]
        result = reorder_examples(canonical_only.copy(), "canonical-last")

        # All are canonical, so they should all end up at the "end" (which is entire list)
        assert len(result) == len(canonical_only)
        for ex in result:
            assert ex["category"].startswith("canonical")

    def test_does_not_modify_original(self) -> None:
        """reorder_examples should not modify the original list."""
        original = SAMPLE_EXAMPLES.copy()
        original_copy = [dict(e) for e in original]  # Deep copy for comparison

        _ = reorder_examples(original, "canonical-last")

        # Original should be unchanged
        assert original == original_copy, "Original list was modified"

    def test_missing_category_treated_as_non_canonical(self) -> None:
        """Examples without category field should be treated as non-canonical."""
        examples_with_missing = [
            {"path": "ex1.png", "category": "canonical-positive", "label": "Positive"},
            {"path": "ex2.png", "label": "Unknown"},  # No category
            {"path": "ex3.png", "category": "hard-positive", "label": "Positive"},
        ]
        result = reorder_examples(examples_with_missing.copy(), "canonical-last")

        # The one without category should be in non-canonical group (first)
        # Canonical should be last
        assert result[-1]["path"] == "ex1.png", "Canonical should be last"


@pytest.mark.tier1
class TestReorderExamplesEdgeCases:
    """Edge case tests for reorder_examples."""

    def test_single_element(self) -> None:
        """Single element list should work for all orderings."""
        single = [{"path": "ex.png", "category": "canonical-positive", "label": "Positive"}]

        for ordering in ["canonical-first", "canonical-last", "random"]:
            result = reorder_examples(single.copy(), ordering, seed=42)
            assert len(result) == 1
            assert result[0]["path"] == "ex.png"

    def test_two_elements_swap(self) -> None:
        """Two elements (canonical + hard) should swap with canonical-last."""
        two = [
            {"path": "canonical.png", "category": "canonical-positive", "label": "Positive"},
            {"path": "hard.png", "category": "hard-positive", "label": "Positive"},
        ]
        result = reorder_examples(two.copy(), "canonical-last")

        assert result[0]["path"] == "hard.png", "Hard should be first"
        assert result[1]["path"] == "canonical.png", "Canonical should be last"


# Import check - ensure the function is importable
def test_import_reorder_examples() -> None:
    """Verify that reorder_examples can be imported from the detection script."""
    # This is a smoke test to ensure the import works using importlib
    # (module name starts with number so standard import doesn't work)
    spec = importlib.util.spec_from_file_location(
        "detect_mounds_batch",
        PROJECT_ROOT / "scripts" / "4_detect_mounds_batch.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.reorder_examples)
