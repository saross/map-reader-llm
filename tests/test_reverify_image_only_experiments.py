"""
Tier 1 unit tests for reverify_image_only_experiments.py.

Tests core logic functions with synthetic data — no API calls, no file
I/O, no network dependencies. Verifies probability merging, temperature
aggregation, and content-part assembly ordering.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Mark all tests in this module as tier1
pytestmark = pytest.mark.tier1

# Add scripts dir to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from reverify_image_only_experiments import (  # noqa: E402
    aggregate_temperature_passes,
    build_comparative_content_parts,
    build_content_parts,
    filter_passing_candidates,
    merge_probabilities,
)


# ---------------------------------------------------------------------------
# Tests: merge_probabilities
# ---------------------------------------------------------------------------

class TestMergeProbabilities:
    """Test merging experiment probabilities into baseline map."""

    def test_overwrites_matching_keys(self):
        """Experiment values replace baseline values for overlapping keys."""
        baseline = {"a": 0.1, "b": 0.2, "c": 0.3, "d": 0.4, "e": 0.5}
        experiment = {"b": 0.9, "d": 0.8}

        merged = merge_probabilities(baseline, experiment)

        assert merged["b"] == 0.9
        assert merged["d"] == 0.8

    def test_preserves_non_overlapping_keys(self):
        """Keys not in experiment remain unchanged from baseline."""
        baseline = {"a": 0.1, "b": 0.2, "c": 0.3, "d": 0.4, "e": 0.5}
        experiment = {"b": 0.9, "d": 0.8}

        merged = merge_probabilities(baseline, experiment)

        assert merged["a"] == 0.1
        assert merged["c"] == 0.3
        assert merged["e"] == 0.5

    def test_total_keys_unchanged(self):
        """Merged dict has same number of keys as baseline when
        experiment keys are a subset."""
        baseline = {"a": 0.1, "b": 0.2, "c": 0.3, "d": 0.4, "e": 0.5}
        experiment = {"b": 0.9, "d": 0.8}

        merged = merge_probabilities(baseline, experiment)

        assert len(merged) == len(baseline)

    def test_does_not_mutate_baseline(self):
        """Original baseline dict must not be modified."""
        baseline = {"a": 0.1, "b": 0.2}
        experiment = {"b": 0.9}

        merge_probabilities(baseline, experiment)

        assert baseline["b"] == 0.2  # unchanged

    def test_none_values_propagate(self):
        """None in experiment overwrites a valid baseline value."""
        baseline = {"a": 0.5, "b": 0.3}
        experiment = {"a": None}

        merged = merge_probabilities(baseline, experiment)

        assert merged["a"] is None
        assert merged["b"] == 0.3

    def test_empty_experiment_returns_copy(self):
        """Empty experiment dict returns an exact copy of baseline."""
        baseline = {"a": 0.1, "b": 0.2}
        experiment = {}

        merged = merge_probabilities(baseline, experiment)

        assert merged == baseline
        assert merged is not baseline  # must be a copy

    def test_new_keys_from_experiment_added(self):
        """Keys in experiment but not in baseline are added."""
        baseline = {"a": 0.1}
        experiment = {"b": 0.9}

        merged = merge_probabilities(baseline, experiment)

        assert merged == {"a": 0.1, "b": 0.9}


# ---------------------------------------------------------------------------
# Tests: aggregate_temperature_passes
# ---------------------------------------------------------------------------

class TestAggregateTemperaturePasses:
    """Test multi-pass temperature aggregation logic."""

    def test_mean_of_valid_values(self):
        """Mean computed correctly from multiple valid passes."""
        passes = [
            {"cand_1": 0.8, "cand_2": 0.2},
            {"cand_1": 0.6, "cand_2": 0.4},
            {"cand_1": 0.7, "cand_2": 0.3},
        ]
        means = aggregate_temperature_passes(passes)

        assert abs(means["cand_1"] - 0.7) < 1e-9
        assert abs(means["cand_2"] - 0.3) < 1e-9

    def test_none_values_filtered(self):
        """None values are excluded from mean computation."""
        passes = [
            {"cand_1": 0.8},
            {"cand_1": None},
            {"cand_1": 0.6},
        ]
        means = aggregate_temperature_passes(passes)

        # Mean of [0.8, 0.6] = 0.7
        assert abs(means["cand_1"] - 0.7) < 1e-9

    def test_all_none_returns_none(self):
        """If all passes returned None, the mean is None."""
        passes = [
            {"cand_1": None},
            {"cand_1": None},
        ]
        means = aggregate_temperature_passes(passes)

        assert means["cand_1"] is None

    def test_single_value(self):
        """Single pass returns that value as the mean."""
        passes = [{"cand_1": 0.42}]
        means = aggregate_temperature_passes(passes)

        assert means["cand_1"] == 0.42

    def test_empty_passes_list(self):
        """Empty passes list returns empty dict."""
        means = aggregate_temperature_passes([])
        assert means == {}

    def test_candidate_missing_in_some_passes(self):
        """Candidate present in only some passes uses available values."""
        passes = [
            {"cand_1": 0.8, "cand_2": 0.5},
            {"cand_1": 0.6},  # cand_2 missing entirely
        ]
        means = aggregate_temperature_passes(passes)

        # cand_1: mean of [0.8, 0.6] = 0.7
        assert abs(means["cand_1"] - 0.7) < 1e-9
        # cand_2: only value is None (missing = not in dict = None via .get)
        # Actually, cand_2 is only in pass 0, so its value from pass 1
        # is None via .get(). Mean of [0.5, None] → filtered to [0.5]
        assert means["cand_2"] == 0.5


# ---------------------------------------------------------------------------
# Tests: build_content_parts
# ---------------------------------------------------------------------------

class TestBuildContentParts:
    """Test content-part assembly and ordering for each experiment."""

    @pytest.fixture
    def mock_types(self):
        """
        Mock google.genai.types to avoid import dependency.

        Returns a mock where Part.from_text and Part.from_bytes return
        distinguishable mock objects with a ._type attribute for
        introspection.
        """
        mock_module = MagicMock()

        def make_text_part(text=""):
            part = MagicMock()
            part._type = "text"
            part._text = text
            return part

        def make_bytes_part(data=b"", mime_type=""):
            part = MagicMock()
            part._type = "bytes"
            part._mime_type = mime_type
            return part

        mock_module.Part.from_text = MagicMock(side_effect=make_text_part)
        mock_module.Part.from_bytes = MagicMock(side_effect=make_bytes_part)

        return mock_module

    @pytest.fixture
    def dummy_crop(self, tmp_path):
        """Create a minimal dummy crop file."""
        crop = tmp_path / "crop_001.png"
        crop.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        return crop

    def _count_parts_by_type(self, parts, part_type):
        """Count parts of a given type in the parts list."""
        return sum(1 for p in parts if p._type == part_type)

    def test_baseline_no_preamble_no_images(
        self, mock_types, dummy_crop,
    ):
        """Baseline: text-only examples, no preamble.

        Expected parts:
            1. Text-only example descriptions
            2. Classification prompt text
            3. Crop image bytes
        Total: 3 parts (1 text-only examples + 1 prompt + 1 image)
        """
        with patch.dict(
            "sys.modules", {"google.genai.types": mock_types}
        ):
            parts = build_content_parts(
                dummy_crop,
                include_examples=False,
                provenance_preamble=False,
            )

        # 3 parts: example text + classify prompt + crop image
        assert len(parts) == 3
        assert parts[0]._type == "text"  # text-only examples
        assert parts[1]._type == "text"  # classify prompt
        assert parts[2]._type == "bytes"  # crop image

    def test_provenance_adds_preamble(self, mock_types, dummy_crop):
        """Experiment A: provenance preamble prepended.

        Expected parts:
            1. Provenance preamble text
            2. Text-only example descriptions
            3. Classification prompt text
            4. Crop image bytes
        Total: 4 parts (1 extra vs baseline)
        """
        with patch.dict(
            "sys.modules", {"google.genai.types": mock_types}
        ):
            parts = build_content_parts(
                dummy_crop,
                include_examples=False,
                provenance_preamble=True,
            )

        # 4 parts: preamble + example text + classify prompt + crop
        assert len(parts) == 4
        assert parts[0]._type == "text"  # preamble (first!)
        assert parts[-1]._type == "bytes"  # crop always last

    def test_examples_adds_image_parts(self, mock_types, dummy_crop):
        """Experiment B: visual examples include image bytes.

        Expected parts:
            1. "Reference examples for comparison:" header
            2–13. Label text + image bytes for each of 6 examples
            14. Classification prompt text
            15. Crop image bytes
        Total: 15 parts (1 header + 6×2 examples + 1 prompt + 1 crop)

        Note: requires example image files to exist on disk. If they
        don't exist, only labels are added (no bytes parts for missing
        images).
        """
        # Create fake example images so the file existence check passes
        from reverify_image_only_experiments import (
            EXAMPLES_DIR,
            VERIFIER_EXAMPLES,
        )

        existing_count = sum(
            1 for ex in VERIFIER_EXAMPLES
            if (EXAMPLES_DIR / ex["path"]).exists()
        )

        with patch.dict(
            "sys.modules", {"google.genai.types": mock_types}
        ):
            parts = build_content_parts(
                dummy_crop,
                include_examples=True,
                provenance_preamble=False,
            )

        # Structure: header + (label + image) × existing_count
        #            + classify prompt + crop
        expected_count = 1 + (existing_count * 2) + 1 + 1
        assert len(parts) == expected_count

        # First part is the header text
        assert parts[0]._type == "text"
        # Last two parts are always classify prompt + crop
        assert parts[-2]._type == "text"
        assert parts[-1]._type == "bytes"

    def test_provenance_preamble_is_first_part(
        self, mock_types, dummy_crop,
    ):
        """When provenance preamble is set, it must be the very first
        content part, before any examples or prompts."""
        with patch.dict(
            "sys.modules", {"google.genai.types": mock_types}
        ):
            parts = build_content_parts(
                dummy_crop,
                include_examples=False,
                provenance_preamble=True,
            )

        # Verify the preamble text content
        from reverify_image_only_experiments import PROVENANCE_PREAMBLE
        mock_types.Part.from_text.assert_any_call(
            text=PROVENANCE_PREAMBLE
        )
        # First part should be the preamble
        assert parts[0]._text == PROVENANCE_PREAMBLE

    def test_crop_image_always_last(self, mock_types, dummy_crop):
        """Crop image is always the last part regardless of experiment."""
        for kwargs in [
            {"include_examples": False, "provenance_preamble": False},
            {"include_examples": False, "provenance_preamble": True},
            {"include_examples": True, "provenance_preamble": False},
        ]:
            with patch.dict(
                "sys.modules", {"google.genai.types": mock_types}
            ):
                parts = build_content_parts(dummy_crop, **kwargs)

            assert parts[-1]._type == "bytes", (
                f"Last part should be bytes (crop image) for {kwargs}"
            )


# ---------------------------------------------------------------------------
# Tests: filter_passing_candidates
# ---------------------------------------------------------------------------

class TestFilterPassingCandidates:
    """Test first-stage threshold filtering for cascaded experiment."""

    def _make_candidates(self, n: int) -> list[dict]:
        """Create a list of n synthetic candidate dicts."""
        return [{"candidate_id": i} for i in range(n)]

    def test_filters_above_threshold(self):
        """Candidates with prob >= threshold pass."""
        candidates = self._make_candidates(5)
        indices = [0, 1, 2, 3, 4]
        baseline = {"0": 0.5, "1": 0.3, "2": 0.8, "3": 0.1, "4": 0.9}

        result = filter_passing_candidates(
            indices, candidates, baseline, threshold=0.4
        )

        assert sorted(result) == [0, 2, 4]

    def test_excludes_below_threshold(self):
        """Candidates with prob < threshold are excluded."""
        candidates = self._make_candidates(3)
        indices = [0, 1, 2]
        baseline = {"0": 0.05, "1": 0.01, "2": 0.09}

        result = filter_passing_candidates(
            indices, candidates, baseline, threshold=0.11
        )

        assert result == []

    def test_excludes_none_values(self):
        """Candidates with None probability are excluded."""
        candidates = self._make_candidates(3)
        indices = [0, 1, 2]
        baseline = {"0": 0.5, "1": None, "2": 0.8}

        result = filter_passing_candidates(
            indices, candidates, baseline, threshold=0.11
        )

        assert sorted(result) == [0, 2]

    def test_includes_exact_threshold(self):
        """Candidates at exactly the threshold boundary pass."""
        candidates = self._make_candidates(2)
        indices = [0, 1]
        baseline = {"0": 0.11, "1": 0.10}

        result = filter_passing_candidates(
            indices, candidates, baseline, threshold=0.11
        )

        assert result == [0]

    def test_empty_input(self):
        """Empty indices list returns empty result."""
        candidates = self._make_candidates(5)
        baseline = {"0": 0.5, "1": 0.8}

        result = filter_passing_candidates(
            [], candidates, baseline, threshold=0.11
        )

        assert result == []

    def test_custom_threshold(self):
        """Different threshold values filter correctly."""
        candidates = self._make_candidates(4)
        indices = [0, 1, 2, 3]
        baseline = {"0": 0.2, "1": 0.5, "2": 0.7, "3": 0.9}

        # High threshold — only 2 pass
        result = filter_passing_candidates(
            indices, candidates, baseline, threshold=0.6
        )
        assert sorted(result) == [2, 3]

        # Low threshold — all pass
        result = filter_passing_candidates(
            indices, candidates, baseline, threshold=0.1
        )
        assert sorted(result) == [0, 1, 2, 3]


# ---------------------------------------------------------------------------
# Tests: build_comparative_content_parts
# ---------------------------------------------------------------------------

class TestBuildComparativeContentParts:
    """Test comparative content-part assembly for Experiment D."""

    @pytest.fixture
    def mock_types(self):
        """
        Mock google.genai.types to avoid import dependency.

        Returns a mock where Part.from_text and Part.from_bytes return
        distinguishable mock objects with a ._type attribute.
        """
        mock_module = MagicMock()

        def make_text_part(text=""):
            part = MagicMock()
            part._type = "text"
            part._text = text
            return part

        def make_bytes_part(data=b"", mime_type=""):
            part = MagicMock()
            part._type = "bytes"
            part._mime_type = mime_type
            return part

        mock_module.Part.from_text = MagicMock(
            side_effect=make_text_part
        )
        mock_module.Part.from_bytes = MagicMock(
            side_effect=make_bytes_part
        )

        return mock_module

    @pytest.fixture
    def dummy_crop(self, tmp_path):
        """Create a minimal dummy crop file."""
        crop = tmp_path / "crop_001.png"
        crop.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        return crop

    def test_reference_header_is_first(self, mock_types, dummy_crop):
        """First part is the reference examples header text."""
        with patch.dict(
            "sys.modules", {"google.genai.types": mock_types}
        ):
            parts = build_comparative_content_parts(dummy_crop)

        assert parts[0]._type == "text"
        assert "reference" in parts[0]._text.lower()

    def test_four_reference_images_included(
        self, mock_types, dummy_crop,
    ):
        """Four confirmed mound reference images are included."""
        from reverify_image_only_experiments import (
            COMPARATIVE_EXAMPLES,
            EXAMPLES_DIR,
        )

        existing_count = sum(
            1 for ex in COMPARATIVE_EXAMPLES
            if (EXAMPLES_DIR / ex["path"]).exists()
        )

        with patch.dict(
            "sys.modules", {"google.genai.types": mock_types}
        ):
            parts = build_comparative_content_parts(dummy_crop)

        # Count image (bytes) parts — should be existing refs + 1 crop
        image_parts = [p for p in parts if p._type == "bytes"]
        assert len(image_parts) == existing_count + 1

    def test_candidate_crop_is_last(self, mock_types, dummy_crop):
        """Candidate crop image is always the last part."""
        with patch.dict(
            "sys.modules", {"google.genai.types": mock_types}
        ):
            parts = build_comparative_content_parts(dummy_crop)

        assert parts[-1]._type == "bytes"

    def test_total_part_count(self, mock_types, dummy_crop):
        """Total parts = 11 when all 4 reference images exist.

        Structure: 1 header + 4×(label + image) + 1 separator + 1 crop
        = 1 + 8 + 1 + 1 = 11
        """
        from reverify_image_only_experiments import (
            COMPARATIVE_EXAMPLES,
            EXAMPLES_DIR,
        )

        existing_count = sum(
            1 for ex in COMPARATIVE_EXAMPLES
            if (EXAMPLES_DIR / ex["path"]).exists()
        )

        with patch.dict(
            "sys.modules", {"google.genai.types": mock_types}
        ):
            parts = build_comparative_content_parts(dummy_crop)

        # header + (label + image) × existing + missing labels
        # + separator + crop
        n_missing = len(COMPARATIVE_EXAMPLES) - existing_count
        expected = (
            1                       # header
            + existing_count * 2    # label + image per existing
            + n_missing             # label-only for missing
            + 1                     # separator prompt
            + 1                     # candidate crop
        )
        assert len(parts) == expected


# ---------------------------------------------------------------------------
# Tests: cascaded merge strategy
# ---------------------------------------------------------------------------

class TestCascadedMergeStrategy:
    """Test the cascaded output merge strategy.

    In the cascaded experiment, non-passing candidates retain baseline
    values while passing candidates get second-stage values. This is
    tested using merge_probabilities with the expected inputs.
    """

    def test_non_passing_retain_baseline(self):
        """Candidates that didn't pass first stage keep baseline values."""
        # Simulate: IDs 0-3 are image-only, 0 and 2 passed second stage
        baseline_all = {
            "0": 0.5, "1": 0.05, "2": 0.8, "3": 0.02,
            "4": 0.9, "5": 0.7,  # non-image-only candidates
        }
        # Cascaded output for all 4 image-only candidates
        cascaded_output = {
            "0": 0.3,   # passed → got new value
            "1": 0.05,  # didn't pass → kept baseline
            "2": 0.6,   # passed → got new value
            "3": 0.02,  # didn't pass → kept baseline
        }

        merged = merge_probabilities(baseline_all, cascaded_output)

        # Non-passing retain baseline
        assert merged["1"] == 0.05
        assert merged["3"] == 0.02

    def test_passing_overwritten(self):
        """Candidates that passed get second-stage values."""
        baseline_all = {
            "0": 0.5, "1": 0.05, "2": 0.8, "3": 0.02,
        }
        cascaded_output = {
            "0": 0.3,   # second-stage value
            "1": 0.05,  # baseline retained
            "2": 0.6,   # second-stage value
            "3": 0.02,  # baseline retained
        }

        merged = merge_probabilities(baseline_all, cascaded_output)

        assert merged["0"] == 0.3
        assert merged["2"] == 0.6

    def test_output_has_all_keys(self):
        """Merged output contains all baseline keys plus experiment keys."""
        baseline = {str(i): i * 0.1 for i in range(10)}
        # Cascaded output for 4 image-only candidates
        cascaded = {"2": 0.5, "5": 0.3, "7": 0.1, "9": 0.8}

        merged = merge_probabilities(baseline, cascaded)

        assert len(merged) == 10
        for key in baseline:
            assert key in merged
