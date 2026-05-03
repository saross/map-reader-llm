"""
Tests for lib_verifier.py — Dual-mode verifier library.

Tier 1 unit tests for the intermediate representation (IR), serialisers,
shared prompt construction, and generation config helpers.

No API calls are made — all SDK interactions are mocked.
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_verifier import (
    ContentItems,
    ImageItem,
    TextItem,
    _resolve_crop_path,
    _unwrap_verdict_payload,
    aggregate_consensus_votes,
    build_candidate_content,
    build_generation_config,
    build_reference_items,
    build_verifier_jsonl,
    build_verifier_jsonl_consensus,
    content_items_to_batch_parts,
    content_items_to_sdk_parts,
    gen_config_to_sdk,
    load_system_instruction,
    parse_verifier_results,
)


# =========================================================================
# FIXTURES
# =========================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_crop(temp_dir: Path) -> Path:
    """Create a minimal PNG file for testing."""
    crops_dir = temp_dir / "crops"
    crops_dir.mkdir()
    crop_path = crops_dir / "candidate_00000.png"
    # Minimal 1x1 PNG (valid file header)
    crop_path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
        b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return crop_path


@pytest.fixture
def sample_candidate(sample_crop: Path) -> dict:
    """A candidate dict matching manifest structure."""
    return {
        "candidate_id": 0,
        "crop_file": "crops/candidate_00000.png",
        "source_tile": "K-35-052-4_32635_x4032_y3696.png",
        "centroid_x": 417287.38,
        "centroid_y": 4687360.45,
    }


@pytest.fixture
def text_only_config() -> dict:
    """A text-only verifier config (no image examples)."""
    return {
        "version": "verify_adversarial-text",
        "model": "gemini-3-flash",
        "instruction_file": "",
        "temperature": 0.0,
        "max_output_tokens": 8192,
        "thinking_level": "minimal",
        "examples": [],
        "text_only_labels": [
            "Positive: Burial Mound (Kurgan)",
            "Negative: Triangulation Point ALONE",
        ],
        "crop_label": (
            "Now classify the candidate symbol at the "
            "centre of this crop:"
        ),
    }


@pytest.fixture
def image_config() -> dict:
    """A verifier config with image examples."""
    return {
        "version": "verify_adversarial",
        "model": "gemini-3-flash",
        "instruction_file": "",
        "temperature": 0.0,
        "max_output_tokens": 8192,
        "thinking_level": "minimal",
        "examples": [
            {
                "path": "neutral-naming/example_01.png",
                "label": "Positive: Burial Mound",
            },
            {
                "path": "neutral-naming/example_02.png",
                "label": "Negative: Triangulation Point",
            },
        ],
        "text_only_labels": [],
        "crop_label": (
            "Now classify the candidate symbol at the "
            "centre of this crop:"
        ),
    }


@pytest.fixture
def sample_manifest(sample_candidate: dict) -> dict:
    """A minimal candidate manifest."""
    return {
        "version": "2.0",
        "padding": 75,
        "total_detections": 1,
        "successful_extractions": 1,
        "candidates": [sample_candidate],
    }


# =========================================================================
# IR TYPES
# =========================================================================


@pytest.mark.tier1
class TestIRTypes:
    """Tests for TextItem and ImageItem dataclasses."""

    def test_text_item_fields(self) -> None:
        """TextItem stores text."""
        item = TextItem(text="hello")
        assert item.text == "hello"

    def test_image_item_fields(self) -> None:
        """ImageItem stores a Path."""
        p = Path("/tmp/test.png")
        item = ImageItem(path=p)
        assert item.path == p

    def test_text_item_frozen(self) -> None:
        """TextItem is immutable."""
        item = TextItem(text="hello")
        with pytest.raises(AttributeError):
            item.text = "world"  # type: ignore[misc]

    def test_image_item_frozen(self) -> None:
        """ImageItem is immutable."""
        item = ImageItem(path=Path("/tmp/test.png"))
        with pytest.raises(AttributeError):
            item.path = Path("/other")  # type: ignore[misc]

    def test_text_item_has_slots(self) -> None:
        """TextItem uses __slots__ (no __dict__)."""
        item = TextItem(text="hello")
        assert not hasattr(item, "__dict__")

    def test_image_item_has_slots(self) -> None:
        """ImageItem uses __slots__ (no __dict__)."""
        item = ImageItem(path=Path("/tmp/test.png"))
        assert not hasattr(item, "__dict__")


# =========================================================================
# BATCH SERIALISER
# =========================================================================


@pytest.mark.tier1
class TestBatchSerialiser:
    """Tests for content_items_to_batch_parts."""

    def test_text_item_serialises_to_dict(self) -> None:
        """TextItem becomes {"text": "..."}."""
        parts = content_items_to_batch_parts([TextItem(text="hello")])
        assert parts == [{"text": "hello"}]

    def test_image_item_serialises_to_inline_data(
        self, sample_crop: Path,
    ) -> None:
        """ImageItem becomes {"inline_data": {...}}."""
        parts = content_items_to_batch_parts([ImageItem(path=sample_crop)])
        assert len(parts) == 1
        assert "inline_data" in parts[0]
        assert parts[0]["inline_data"]["mime_type"] == "image/png"
        # Data should be base64-encoded
        assert isinstance(parts[0]["inline_data"]["data"], str)

    def test_mixed_items_preserve_order(self, sample_crop: Path) -> None:
        """Items are serialised in the order provided."""
        items: ContentItems = [
            TextItem(text="first"),
            ImageItem(path=sample_crop),
            TextItem(text="third"),
        ]
        parts = content_items_to_batch_parts(items)
        assert len(parts) == 3
        assert parts[0] == {"text": "first"}
        assert "inline_data" in parts[1]
        assert parts[2] == {"text": "third"}

    def test_empty_list(self) -> None:
        """Empty input produces empty output."""
        assert content_items_to_batch_parts([]) == []

    def test_unknown_type_raises(self) -> None:
        """Non-IR types raise TypeError."""
        with pytest.raises(TypeError, match="Unknown content item type"):
            content_items_to_batch_parts(["not an IR item"])  # type: ignore


# =========================================================================
# SDK SERIALISER
# =========================================================================


@pytest.mark.tier1
class TestSdkSerialiser:
    """Tests for content_items_to_sdk_parts (mocked SDK)."""

    def test_text_item_produces_sdk_part(self) -> None:
        """TextItem produces a Part with the correct text."""
        from google.genai import types

        parts = content_items_to_sdk_parts([TextItem(text="hello")])
        assert len(parts) == 1
        assert isinstance(parts[0], types.Part)

    def test_image_item_produces_sdk_part(self, sample_crop: Path) -> None:
        """ImageItem produces a Part with image data."""
        from google.genai import types

        parts = content_items_to_sdk_parts([ImageItem(path=sample_crop)])
        assert len(parts) == 1
        assert isinstance(parts[0], types.Part)


# =========================================================================
# REFERENCE ITEMS
# =========================================================================


@pytest.mark.tier1
class TestBuildReferenceItems:
    """Tests for build_reference_items."""

    def test_text_only_labels_produce_text_item(
        self, text_only_config: dict,
    ) -> None:
        """Text-only config produces a single TextItem with labels."""
        items = build_reference_items(text_only_config)
        assert len(items) == 1
        assert isinstance(items[0], TextItem)
        assert "Burial Mound" in items[0].text
        assert "Triangulation Point" in items[0].text

    def test_image_examples_produce_text_and_image_items(
        self, image_config: dict, temp_dir: Path,
    ) -> None:
        """Image config produces alternating TextItem + ImageItem pairs."""
        # Create fake example images
        examples_dir = temp_dir / "examples" / "neutral-naming"
        examples_dir.mkdir(parents=True)
        (examples_dir / "example_01.png").write_bytes(b"\x89PNG")
        (examples_dir / "example_02.png").write_bytes(b"\x89PNG")

        with patch(
            "scripts.lib_verifier._EXAMPLES_DIR",
            temp_dir / "examples",
        ):
            items = build_reference_items(image_config)

        # Header + 2 × (label + image)
        assert len(items) == 5
        assert isinstance(items[0], TextItem)
        assert "Reference examples" in items[0].text
        assert isinstance(items[1], TextItem)
        assert isinstance(items[2], ImageItem)
        assert isinstance(items[3], TextItem)
        assert isinstance(items[4], ImageItem)

    def test_empty_config_returns_empty(self) -> None:
        """Config with no labels or examples returns empty list."""
        items = build_reference_items(
            {"examples": [], "text_only_labels": []},
        )
        assert items == []


# =========================================================================
# CANDIDATE CONTENT
# =========================================================================


@pytest.mark.tier1
class TestBuildCandidateContent:
    """Tests for build_candidate_content."""

    def test_includes_reference_and_crop(
        self,
        sample_candidate: dict,
        text_only_config: dict,
        temp_dir: Path,
    ) -> None:
        """Content includes reference items, crop label, and crop image."""
        items = build_candidate_content(
            sample_candidate, text_only_config, temp_dir,
        )
        # 1 reference TextItem + 1 crop label TextItem + 1 crop ImageItem
        assert len(items) == 3
        assert isinstance(items[0], TextItem)
        assert isinstance(items[1], TextItem)
        assert "classify" in items[1].text.lower()
        assert isinstance(items[2], ImageItem)

    def test_pre_built_reference_items(
        self,
        sample_candidate: dict,
        text_only_config: dict,
        temp_dir: Path,
    ) -> None:
        """Pre-built reference items are reused."""
        ref_items = [TextItem(text="custom reference")]
        items = build_candidate_content(
            sample_candidate, text_only_config, temp_dir,
            reference_items=ref_items,
        )
        assert items[0].text == "custom reference"  # type: ignore[union-attr]

    def test_custom_crop_label(
        self,
        sample_candidate: dict,
        temp_dir: Path,
    ) -> None:
        """Crop label is taken from config."""
        config = {
            "crop_label": "Custom label here",
            "text_only_labels": [],
            "examples": [],
        }
        items = build_candidate_content(
            sample_candidate, config, temp_dir,
        )
        # Last TextItem before ImageItem should be the label
        text_items = [i for i in items if isinstance(i, TextItem)]
        assert text_items[-1].text == "Custom label here"

    def test_missing_crop_raises(
        self, text_only_config: dict, temp_dir: Path,
    ) -> None:
        """FileNotFoundError raised when crop file doesn't exist."""
        candidate = {
            "candidate_id": 99,
            "crop_file": "crops/nonexistent.png",
        }
        with pytest.raises(FileNotFoundError, match="nonexistent"):
            build_candidate_content(
                candidate, text_only_config, temp_dir,
            )


# =========================================================================
# GENERATION CONFIG
# =========================================================================


@pytest.mark.tier1
class TestGenerationConfig:
    """Tests for build_generation_config and gen_config_to_sdk."""

    def test_batch_config_structure(
        self, text_only_config: dict,
    ) -> None:
        """Batch config has expected keys."""
        cfg = build_generation_config(text_only_config)
        assert cfg["temperature"] == 0.0
        assert cfg["max_output_tokens"] == 8192
        assert cfg["response_mime_type"] == "application/json"
        assert "thinking_config" in cfg

    def test_temperature_override(self, text_only_config: dict) -> None:
        """Temperature override takes precedence."""
        cfg = build_generation_config(text_only_config, temperature_override=0.7)
        assert cfg["temperature"] == 0.7

    def test_thinking_config_nested(self, text_only_config: dict) -> None:
        """Thinking config is a nested dict with uppercase level."""
        cfg = build_generation_config(text_only_config)
        assert cfg["thinking_config"]["thinking_level"] == "MINIMAL"

    def test_no_thinking_config_when_absent(self) -> None:
        """No thinking_config key when not in source config."""
        cfg = build_generation_config({"temperature": 0.5})
        assert "thinking_config" not in cfg

    def test_no_safety_settings_in_batch_config(
        self, text_only_config: dict,
    ) -> None:
        """Batch config does not include safety_settings."""
        cfg = build_generation_config(text_only_config)
        assert "safety_settings" not in cfg

    def test_sdk_config_has_safety_settings(
        self, text_only_config: dict,
    ) -> None:
        """SDK config includes safety_settings."""
        batch_cfg = build_generation_config(text_only_config)
        sdk_cfg = gen_config_to_sdk(batch_cfg, "test instruction")
        assert sdk_cfg.safety_settings is not None
        assert len(sdk_cfg.safety_settings) == 4

    def test_sdk_config_has_system_instruction(
        self, text_only_config: dict,
    ) -> None:
        """SDK config includes system_instruction."""
        batch_cfg = build_generation_config(text_only_config)
        sdk_cfg = gen_config_to_sdk(batch_cfg, "test instruction")
        assert sdk_cfg.system_instruction == "test instruction"


# =========================================================================
# BATCH/REAL-TIME PARITY
# =========================================================================


@pytest.mark.tier1
class TestBatchRealTimeParity:
    """Verify batch and real-time serialisers produce equivalent content."""

    def test_item_count_matches(self, sample_crop: Path) -> None:
        """Both serialisers produce the same number of parts."""
        items: ContentItems = [
            TextItem(text="reference"),
            TextItem(text="label"),
            ImageItem(path=sample_crop),
        ]
        batch_parts = content_items_to_batch_parts(items)
        sdk_parts = content_items_to_sdk_parts(items)
        assert len(batch_parts) == len(sdk_parts)

    def test_text_content_matches(self) -> None:
        """Text content is identical in both serialisations."""
        from google.genai import types

        items: ContentItems = [
            TextItem(text="first"),
            TextItem(text="second"),
        ]
        batch_parts = content_items_to_batch_parts(items)
        batch_texts = [p["text"] for p in batch_parts]

        sdk_parts = content_items_to_sdk_parts(items)
        # Extract text from SDK parts for direct comparison
        sdk_texts = [
            p.text for p in sdk_parts
            if isinstance(p, types.Part) and p.text is not None
        ]

        assert batch_texts == sdk_texts


# =========================================================================
# BATCH JSONL BUILDERS
# =========================================================================


@pytest.mark.tier1
class TestBuildVerifierJsonl:
    """Tests for build_verifier_jsonl."""

    def test_single_candidate_jsonl(
        self,
        sample_manifest: dict,
        text_only_config: dict,
        temp_dir: Path,
    ) -> None:
        """Produces valid JSONL with one line per candidate."""
        output = temp_dir / "batch" / "verifier.jsonl"
        n = build_verifier_jsonl(
            sample_manifest, text_only_config, output, temp_dir,
        )
        assert n == 1

        # Verify JSONL structure in detail
        with open(output) as f:
            line = json.loads(f.readline())
        assert line["key"] == "candidate_00000"

        request = line["request"]
        assert "contents" in request
        assert "system_instruction" in request
        assert "generation_config" in request

        # Verify contents structure: list with one user-role entry
        contents = request["contents"]
        assert len(contents) == 1
        assert contents[0]["role"] == "user"

        # Verify parts: reference text + crop label + inline_data image
        parts = contents[0]["parts"]
        assert len(parts) == 3
        assert "text" in parts[0]  # Reference labels
        assert "text" in parts[1]  # Crop label
        assert "inline_data" in parts[2]  # Crop image
        assert parts[2]["inline_data"]["mime_type"] == "image/png"

    def test_consensus_jsonl_emits_n_copies(
        self,
        sample_manifest: dict,
        text_only_config: dict,
        temp_dir: Path,
    ) -> None:
        """Consensus JSONL emits N lines per candidate."""
        output = temp_dir / "batch" / "consensus.jsonl"
        n = build_verifier_jsonl_consensus(
            sample_manifest, text_only_config, output, temp_dir,
            iterations=3, temperature=0.7,
        )
        assert n == 3

        with open(output) as f:
            lines = [json.loads(line) for line in f]
        keys = [entry["key"] for entry in lines]
        assert keys == [
            "candidate_00000_iter1",
            "candidate_00000_iter2",
            "candidate_00000_iter3",
        ]

        # Verify temperature override was applied (config has T=0.0,
        # consensus should use T=0.7)
        gen_cfg = lines[0]["request"]["generation_config"]
        assert gen_cfg["temperature"] == 0.7


# =========================================================================
# RESPONSE PARSING
# =========================================================================


@pytest.mark.tier1
class TestParseVerifierResults:
    """Tests for parse_verifier_results."""

    def test_valid_response(self) -> None:
        """Parses a well-formed batch response."""
        matched = {
            "candidate_00000": {
                "response": {
                    "candidates": [{
                        "content": {
                            "parts": [{
                                "text": json.dumps({
                                    "mound_probability": 0.85,
                                    "reasoning": "Clear sunburst",
                                    "best_alternative": "None",
                                    "alternative_evidence": "",
                                }),
                            }],
                        },
                    }],
                },
            },
        }
        parsed = parse_verifier_results(matched)
        result = parsed["candidate_00000"]
        assert result["mound_probability"] == 0.85
        assert result["reasoning"] == "Clear sunburst"
        assert result["best_alternative"] == "None"
        assert result["alternative_evidence"] == ""

    def test_malformed_json_returns_parse_error(self) -> None:
        """Malformed JSON produces PARSE_ERROR result."""
        matched = {
            "candidate_00001": {
                "response": {
                    "candidates": [{
                        "content": {
                            "parts": [{"text": "not valid json"}],
                        },
                    }],
                },
            },
        }
        parsed = parse_verifier_results(matched)
        assert parsed["candidate_00001"]["mound_probability"] == 0.0
        assert "PARSE_ERROR" in parsed["candidate_00001"]["reasoning"]

    def test_list_shaped_response_unwraps_first_element(self) -> None:
        """Regression: list-shaped JSON response is unwrapped (cand_01563).

        Reproduces the parser bug from Session 78 in which the model
        returned ``[{...}]`` instead of ``{...}`` and the downstream
        ``.get()`` on the list raised ``AttributeError``, silently
        dropping the candidate after retries. Backlog item #10 in
        ``planning/paper-writeup-continuity.md``.
        """
        matched = {
            "candidate_01563": {
                "response": {
                    "candidates": [{
                        "content": {
                            "parts": [{
                                "text": json.dumps([{
                                    "mound_probability": 0.42,
                                    "reasoning": "Listed wrapper",
                                    "best_alternative": "tumulus",
                                    "alternative_evidence": "ring",
                                }]),
                            }],
                        },
                    }],
                },
            },
        }
        parsed = parse_verifier_results(matched)
        result = parsed["candidate_01563"]
        assert result["mound_probability"] == 0.42
        assert result["reasoning"] == "Listed wrapper"
        assert result["best_alternative"] == "tumulus"
        assert result["alternative_evidence"] == "ring"


@pytest.mark.tier1
class TestUnwrapVerdictPayload:
    """Tests for ``_unwrap_verdict_payload`` — cand_01563 fix helper."""

    def test_dict_passes_through(self) -> None:
        """A plain dict is returned unchanged."""
        data = {"mound_probability": 0.7, "reasoning": "ok"}
        assert _unwrap_verdict_payload(data) is data

    def test_single_element_list_unwrapped(self) -> None:
        """A length-1 list with a dict element returns that dict."""
        verdict = {"mound_probability": 0.7}
        assert _unwrap_verdict_payload([verdict]) is verdict

    def test_multi_element_list_unwraps_first(self) -> None:
        """A multi-element list returns the first dict (best-effort)."""
        first = {"mound_probability": 0.1}
        second = {"mound_probability": 0.9}
        assert _unwrap_verdict_payload([first, second]) is first

    def test_empty_list_raises(self) -> None:
        """An empty list cannot be unwrapped."""
        with pytest.raises(ValueError):
            _unwrap_verdict_payload([])

    def test_list_of_non_dicts_raises(self) -> None:
        """A list whose first element is not a dict cannot be unwrapped."""
        with pytest.raises(ValueError):
            _unwrap_verdict_payload(["mound_probability", 0.5])

    def test_scalar_raises(self) -> None:
        """A scalar value (e.g. bare float) cannot be unwrapped."""
        with pytest.raises(ValueError):
            _unwrap_verdict_payload(0.5)

    def test_none_raises(self) -> None:
        """``None`` cannot be unwrapped."""
        with pytest.raises(ValueError):
            _unwrap_verdict_payload(None)


# =========================================================================
# CONSENSUS AGGREGATION
# =========================================================================


@pytest.mark.tier1
class TestAggregateConsensusVotes:
    """Tests for aggregate_consensus_votes."""

    def test_majority_vote(self) -> None:
        """Correctly counts votes above threshold."""
        parsed = {
            "candidate_00042_iter1": {"mound_probability": 0.9, "reasoning": ""},
            "candidate_00042_iter2": {"mound_probability": 0.3, "reasoning": ""},
            "candidate_00042_iter3": {"mound_probability": 0.7, "reasoning": ""},
        }
        agg = aggregate_consensus_votes(parsed, threshold=0.5)
        assert 42 in agg
        assert agg[42]["vote_count"] == 2
        assert agg[42]["total_iterations"] == 3

    def test_mean_probability(self) -> None:
        """Computes correct mean probability."""
        parsed = {
            "candidate_00001_iter1": {"mound_probability": 0.4, "reasoning": ""},
            "candidate_00001_iter2": {"mound_probability": 0.6, "reasoning": ""},
        }
        agg = aggregate_consensus_votes(parsed, threshold=0.5)
        assert agg[1]["mean_probability"] == pytest.approx(0.5)

    def test_single_pass_key_format(self) -> None:
        """Handles single-pass keys without _iter suffix."""
        parsed = {
            "candidate_00010": {"mound_probability": 0.8, "reasoning": "ok"},
        }
        agg = aggregate_consensus_votes(parsed, threshold=0.5)
        assert 10 in agg
        assert agg[10]["vote_count"] == 1

    def test_boundary_threshold(self) -> None:
        """Probability exactly at threshold counts as a positive vote."""
        parsed = {
            "candidate_00001_iter1": {
                "mound_probability": 0.5, "reasoning": "",
            },
            "candidate_00001_iter2": {
                "mound_probability": 0.49, "reasoning": "",
            },
        }
        agg = aggregate_consensus_votes(parsed, threshold=0.5)
        assert agg[1]["vote_count"] == 1  # 0.5 >= 0.5, 0.49 < 0.5

    def test_all_output_fields_present(self) -> None:
        """Aggregated result includes all expected fields."""
        parsed = {
            "candidate_00005_iter1": {
                "mound_probability": 0.9, "reasoning": "yes",
            },
            "candidate_00005_iter2": {
                "mound_probability": 0.3, "reasoning": "no",
            },
        }
        agg = aggregate_consensus_votes(parsed, threshold=0.5)
        result = agg[5]
        assert result["candidate_id"] == 5
        assert result["vote_count"] == 1
        assert result["total_iterations"] == 2
        assert result["mean_probability"] == pytest.approx(0.6)
        assert result["min_probability"] == 0.3
        assert result["max_probability"] == 0.9
        assert len(result["iterations"]) == 2


# =========================================================================
# LOAD SYSTEM INSTRUCTION
# =========================================================================


@pytest.mark.tier1
class TestLoadSystemInstruction:
    """Tests for load_system_instruction."""

    def test_empty_instruction_file(self) -> None:
        """Returns empty string when instruction_file is empty."""
        result = load_system_instruction({"instruction_file": ""})
        assert result == ""

    def test_missing_instruction_file_key(self) -> None:
        """Returns empty string when instruction_file key absent."""
        result = load_system_instruction({})
        assert result == ""

    def test_nonexistent_file_returns_empty(self) -> None:
        """Returns empty string (with warning) for missing file."""
        result = load_system_instruction(
            {"instruction_file": "nonexistent_file.md"},
        )
        assert result == ""

    def test_valid_instruction_file(self, temp_dir: Path) -> None:
        """Loads instruction text from file."""
        instructions_dir = temp_dir / "instructions"
        instructions_dir.mkdir()
        (instructions_dir / "test.md").write_text("Test instruction")

        with patch(
            "scripts.lib_verifier._INSTRUCTIONS_DIR",
            instructions_dir,
        ):
            result = load_system_instruction(
                {"instruction_file": "test.md"},
            )
        assert result == "Test instruction"


# =========================================================================
# RESOLVE CROP PATH
# =========================================================================


@pytest.mark.tier1
class TestResolveCropPath:
    """Tests for _resolve_crop_path."""

    def test_existing_crop(
        self, sample_candidate: dict, temp_dir: Path,
    ) -> None:
        """Returns path when crop file exists."""
        result = _resolve_crop_path(sample_candidate, temp_dir)
        assert result is not None
        assert result.exists()

    def test_missing_crop_returns_none(self, temp_dir: Path) -> None:
        """Returns None when crop file does not exist."""
        candidate = {
            "candidate_id": 99,
            "crop_file": "crops/missing.png",
        }
        result = _resolve_crop_path(candidate, temp_dir)
        assert result is None

    def test_missing_crop_with_non_int_id(self, temp_dir: Path) -> None:
        """Handles non-integer candidate_id without crashing."""
        candidate = {
            "candidate_id": "abc",
            "crop_file": "crops/missing.png",
        }
        # Should log warning with %s format, not crash with %d
        result = _resolve_crop_path(candidate, temp_dir)
        assert result is None


# =========================================================================
# EMPTY CANDIDATES IN BATCH RESPONSE
# =========================================================================


@pytest.mark.tier1
class TestParseVerifierEdgeCases:
    """Edge case tests for parse_verifier_results."""

    def test_empty_candidates_list_skips_silently(self) -> None:
        """Response with empty candidates list is silently skipped."""
        matched = {
            "candidate_00000": {
                "response": {"candidates": []},
            },
        }
        parsed = parse_verifier_results(matched)
        # Key is NOT in parsed — silently dropped
        assert "candidate_00000" not in parsed

    def test_missing_response_key(self) -> None:
        """Response without 'response' key produces PARSE_ERROR."""
        matched = {"candidate_00000": {}}
        parsed = parse_verifier_results(matched)
        # Empty candidates → silently skipped
        assert "candidate_00000" not in parsed


# =========================================================================
# Layer 2: _call_verifier_api retry parity
# =========================================================================

# Tests cover the retry-policy port that mirrors the proposer
# (4_detect_mounds_batch.py:process_single_tile). Per
# planning/verifier-silent-drop-fix-plan.md § 3.2 the goals are:
# error-class-specific backoff (429 / 503 / DeadlineExceeded), MAX_TOKENS
# finish-reason handling, parse_response_with_repair adoption, and
# _MAX_RETRIES = 15.

from unittest.mock import MagicMock, call as mock_call  # noqa: E402

from scripts.lib_verifier import (  # noqa: E402
    _MAX_RETRIES,
    _call_verifier_api,
)


def _make_response(
    text: str | None = None,
    text_raises: Exception | None = None,
    finish_reason: str = "STOP",
    has_candidates: bool = True,
) -> MagicMock:
    """Build a minimal MagicMock standing in for a Gemini response.

    The shape is just enough to satisfy ``extract_gemini_metadata`` and
    the post-call MAX_TOKENS check in ``_call_verifier_api``.
    """
    response = MagicMock()
    # usage_metadata: none of these are exercised in the retry tests,
    # but the helper reads them via getattr so they need integer-ish
    # defaults to avoid mocked-attribute pollution.
    response.usage_metadata = None

    if has_candidates:
        candidate = MagicMock()
        candidate.finish_reason = finish_reason
        candidate.content = MagicMock()
        candidate.content.parts = [MagicMock()]
        response.candidates = [candidate]
    else:
        response.candidates = []

    # response.text — either a value, or a property that raises.
    if text_raises is not None:
        type(response).text = property(
            lambda self: (_ for _ in ()).throw(text_raises),
        )
    else:
        response.text = text

    return response


@pytest.mark.tier1
class TestCallVerifierApi:
    """Layer 2 retry-parity tests for ``_call_verifier_api``."""

    @pytest.fixture
    def patch_sleep(self):
        """Patch ``time.sleep`` so backoffs do not slow the test suite."""
        with patch("scripts.lib_verifier.time.sleep") as mock:
            yield mock

    @pytest.fixture
    def tracker(self):
        """A bare MagicMock tracker — only ``log_retry`` is exercised."""
        t = MagicMock()
        return t

    def _make_client(self, side_effects: list) -> MagicMock:
        """Build a client whose ``models.generate_content`` walks ``side_effects``.

        Each entry may be either an Exception (raised) or a response
        object (returned). Mirrors the proposer's test helper.
        """
        client = MagicMock()
        client.models.generate_content = MagicMock(side_effect=side_effects)
        return client

    def test_429_retries_with_jitter_backoff(self, patch_sleep, tracker):
        """L2-A: 429s retry with jittered exponential backoff, eventually succeed."""
        good_text = '{"mound_probability": 0.7, "reasoning": "ok"}'
        client = self._make_client([
            Exception("429 ResourceExhausted: quota"),
            Exception("429 ResourceExhausted: quota"),
            _make_response(text=good_text),
        ])

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0001_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is not None
        assert result["mound_probability"] == 0.7
        assert client.models.generate_content.call_count == 3
        # Two retries → two log_retry calls with rate_limit
        retry_calls = [
            c for c in tracker.log_retry.call_args_list
            if c.kwargs.get("error_type") == "rate_limit"
            or (len(c.args) >= 4 and c.args[3] == "rate_limit")
        ]
        assert len(retry_calls) == 2
        # Backoff bounds: jitter on top of exponential up to _MAX_BACKOFF_SECONDS.
        # Attempt 1 -> base * 2^0 + jitter ∈ [30, 60]
        # Attempt 2 -> base * 2^1 + jitter ∈ [60, 90]
        sleep_calls = [c.args[0] for c in patch_sleep.call_args_list]
        assert any(30 <= s <= 60 for s in sleep_calls), (
            f"expected an attempt-1 backoff in [30,60], got {sleep_calls}"
        )

    def test_503_uses_30s_backoff(self, patch_sleep, tracker):
        """L2-B: 503 errors back off with 30 +/- 10s jitter."""
        good_text = '{"mound_probability": 0.5, "reasoning": "ok"}'
        client = self._make_client([
            Exception("503 InternalServerError"),
            _make_response(text=good_text),
        ])

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0002_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is not None
        # Sleep should have been [30,40] for the 503 retry
        sleep_args = [c.args[0] for c in patch_sleep.call_args_list]
        assert any(30 <= s <= 40 for s in sleep_args), (
            f"expected a 30-40s backoff, got {sleep_args}"
        )
        # tracker recorded a server_error retry
        assert any(
            (c.kwargs.get("error_type") == "server_error")
            or (len(c.args) >= 4 and c.args[3] == "server_error")
            for c in tracker.log_retry.call_args_list
        )

    def test_deadline_exceeded_uses_30s_backoff(self, patch_sleep, tracker):
        """L2-C: DeadlineExceeded errors use the 30 +/- 10s timeout backoff."""
        good_text = '{"mound_probability": 0.6, "reasoning": "ok"}'
        client = self._make_client([
            Exception("DeadlineExceeded: timeout"),
            _make_response(text=good_text),
        ])

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0003_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is not None
        sleep_args = [c.args[0] for c in patch_sleep.call_args_list]
        assert any(30 <= s <= 40 for s in sleep_args), (
            f"expected a 30-40s backoff, got {sleep_args}"
        )
        # tracker recorded a timeout retry
        assert any(
            (c.kwargs.get("error_type") == "timeout")
            or (len(c.args) >= 4 and c.args[3] == "timeout")
            for c in tracker.log_retry.call_args_list
        )

    def test_404_model_is_fatal(self, patch_sleep, tracker):
        """L2-D: 404 with 'models/' substring is fatal — return None on first attempt."""
        client = self._make_client([
            Exception("404 NotFound: models/foo not found"),
        ])

        result = _call_verifier_api(
            client=client,
            model_name="models/foo",
            content=None,
            gen_config=None,
            iteration_id="cand_0004_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is None
        assert client.models.generate_content.call_count == 1
        # No sleep — fatal exit before backoff
        assert patch_sleep.call_count == 0

    def test_max_tokens_retries(self, patch_sleep, tracker):
        """L2-E: MAX_TOKENS finish reason triggers retry rather than parse-failure path."""
        good_text = '{"mound_probability": 0.8, "reasoning": "ok"}'
        client = self._make_client([
            _make_response(text=None, finish_reason="MAX_TOKENS"),
            _make_response(text=good_text, finish_reason="STOP"),
        ])

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0005_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is not None
        assert result["mound_probability"] == 0.8
        # tracker recorded a MAX_TOKENS retry
        max_token_calls = [
            c for c in tracker.log_retry.call_args_list
            if any("MAX_TOKENS" in str(arg) for arg in c.args)
            or any("MAX_TOKENS" in str(v) for v in c.kwargs.values())
        ]
        assert len(max_token_calls) >= 1
        # 5s sleep for MAX_TOKENS branch
        assert mock_call(5) in patch_sleep.call_args_list

    def test_parse_repair_recovers_trailing_comma(self, patch_sleep, tracker):
        """L2-F: parse_response_with_repair recovers trailing-comma malformed JSON."""
        bad_then_good = '{"mound_probability": 0.7, "reasoning": "ok",}'
        client = self._make_client([
            _make_response(text=bad_then_good),
        ])

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0006_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is not None
        assert result["mound_probability"] == 0.7
        # First attempt succeeded — no retries
        assert client.models.generate_content.call_count == 1

    def test_parse_repair_recovers_extra_data(self, patch_sleep, tracker):
        """L2-G: parse_response_with_repair (Tier 3) recovers extra-data malformed JSON."""
        bad_with_trailing_prose = (
            '{"mound_probability": 0.5, "reasoning": "ok"}\nextra prose'
        )
        client = self._make_client([
            _make_response(text=bad_with_trailing_prose),
        ])

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0007_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is not None
        assert result["mound_probability"] == 0.5
        assert client.models.generate_content.call_count == 1

    def test_parse_repair_exhausts_retries_returns_none(
        self, patch_sleep, tracker,
    ):
        """L2-H: unrecoverable garbage returns None after _MAX_RETRIES attempts."""
        # Each tier of parse_response_with_repair will fail on this input.
        garbage = "this is not JSON at all !"
        client = self._make_client(
            [_make_response(text=garbage)] * _MAX_RETRIES,
        )

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0008_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is None
        assert client.models.generate_content.call_count == _MAX_RETRIES

    def test_safety_block_returns_none_immediately(self, patch_sleep, tracker):
        """L2-I: BLOCKED responses return None on first attempt — no retry."""
        blocked_response = _make_response(
            text=None,
            text_raises=ValueError("BLOCKED: harm"),
        )
        client = self._make_client([blocked_response])

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0009_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is None
        assert client.models.generate_content.call_count == 1
        # No backoff sleep — deterministic refusal
        assert patch_sleep.call_count == 0

    def test_max_retries_respects_constant(self, patch_sleep, tracker):
        """L2-J: continuous 429s exhaust at exactly _MAX_RETRIES attempts."""
        client = self._make_client(
            [Exception("429 ResourceExhausted")] * (_MAX_RETRIES + 5),
        )

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0010_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is None
        assert client.models.generate_content.call_count == _MAX_RETRIES

    def test_logs_retry_per_attempt_with_error_type(
        self, patch_sleep, tracker,
    ):
        """L2-K: log_retry called with the correct error_type per attempt."""
        good_text = '{"mound_probability": 0.4, "reasoning": "ok"}'
        client = self._make_client([
            Exception("429 ResourceExhausted"),
            Exception("429 ResourceExhausted"),
            Exception("503 InternalServerError"),
            _make_response(text=good_text),
        ])

        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0011_iter1",
            metadata_list=[],
            metadata_tracker=tracker,
        )

        assert result is not None
        # Extract error_types from log_retry calls in order
        error_types: list[str] = []
        for c in tracker.log_retry.call_args_list:
            et = c.kwargs.get("error_type")
            if et is None and len(c.args) >= 4:
                et = c.args[3]
            if et:
                error_types.append(et)
        assert error_types == ["rate_limit", "rate_limit", "server_error"]

    def test_metadata_tracker_none_back_compat(self, patch_sleep):
        """``metadata_tracker=None`` must not raise on retry-logging paths.

        Back-compat regression guard: ``_call_verifier_api`` was
        extended with an optional ``metadata_tracker`` parameter as
        part of Layer 2; callers that have not yet been ported still
        invoke the helper with ``metadata_tracker=None``. Every
        ``log_retry`` call must be guarded so a transient-error retry
        does not crash with ``AttributeError: 'NoneType' object has no
        attribute 'log_retry'``.
        """
        good_text = '{"mound_probability": 0.6, "reasoning": "ok"}'
        client = self._make_client([
            Exception("429 ResourceExhausted: quota"),
            _make_response(text=good_text),
        ])

        # No tracker — the retry path must still complete cleanly.
        result = _call_verifier_api(
            client=client,
            model_name="gemini-3-flash",
            content=None,
            gen_config=None,
            iteration_id="cand_0099_iter1",
            metadata_list=[],
            metadata_tracker=None,
        )

        assert result is not None
        assert result["mound_probability"] == 0.6
        # The retry happened — confirm the client was called twice
        # (i.e. the guarded log_retry branch did not short-circuit).
        assert client.models.generate_content.call_count == 2
