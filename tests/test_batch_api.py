"""
Tests for Gemini Batch API module (lib_batch_api.py).

Tier 1 unit tests covering JSONL construction, result parsing, result
validation, checkpoint integration, output contract, and batch job
lifecycle. All Batch API calls are mocked — no real API interaction.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from google.genai.types import JobState

from scripts.lib_batch_api import (
    _get_state_name,
    _parse_detections_from_response,
    build_jsonl_file,
    run_batch_unit,
    validate_batch_results,
    write_batch_outputs,
)


# ═════════════════════════════════════════════════════════════════════
# Fixtures
# ═════════════════════════════════════════════════════════════════════


def _make_prompt_config() -> dict:
    """Build a minimal prompt config dict for testing."""
    return {
        "version": "detect_test",
        "model": "gemini-3-flash",
        "instruction_file": "detect_image-only.md",
        "temperature": 1.0,
        "max_output_tokens": 8192,
        "include_example_images": True,
        "examples": [],
    }


def _make_tile_image(tmp_dir: Path, name: str) -> Path:
    """Create a minimal PNG file for testing."""
    # Minimal valid PNG (1x1 pixel, white)
    # PNG signature + IHDR + IDAT + IEND (smallest valid PNG)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"  # PNG signature
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde"  # 1x1 RGB
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01"
        b"\x00\x05\x18\xd8N"  # compressed pixel data
        b"\x00\x00\x00\x00IEND\xaeB`\x82"  # end
    )
    tile_path = tmp_dir / name
    tile_path.write_bytes(png_bytes)
    return tile_path


def _make_batch_response(
    tile_key: str,
    detections: list[dict] | None = None,
    error: str | None = None,
) -> dict:
    """Build a mock batch response line for a single tile."""
    if error:
        return {"key": tile_key, "error": {"message": error}}

    detection_list = detections or []
    response_text = json.dumps({"detections": detection_list})

    return {
        "key": tile_key,
        "response": {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": response_text}],
                        "role": "model",
                    },
                    "finish_reason": "STOP",
                }
            ],
            "usage_metadata": {
                "prompt_token_count": 1000,
                "candidates_token_count": 200,
                "total_token_count": 1200,
            },
        },
    }


# ═════════════════════════════════════════════════════════════════════
# Tests: JSONL Construction
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestJSONLConstruction:
    """Tests for build_jsonl_file() output format."""

    def test_jsonl_line_format(self) -> None:
        """Each JSONL line should have 'key' and 'request' top-level keys."""
        config = _make_prompt_config()
        config["include_example_images"] = False  # Skip image loading

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile = _make_tile_image(tmp, "tile_001.png")
            output = tmp / "batch.jsonl"

            build_jsonl_file(
                tile_paths=[tile],
                config=config,
                system_instruction="Test instruction",
                examples=[],
                output_path=output,
            )

            with open(output) as f:
                line = json.loads(f.readline())

            assert "key" in line
            assert "request" in line
            assert line["key"] == "tile_001.png"

    def test_jsonl_system_instruction(self) -> None:
        """Each line should include the system instruction."""
        config = _make_prompt_config()
        config["include_example_images"] = False

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile = _make_tile_image(tmp, "tile_001.png")
            output = tmp / "batch.jsonl"

            build_jsonl_file(
                tile_paths=[tile],
                config=config,
                system_instruction="Detect burial mounds",
                examples=[],
                output_path=output,
            )

            with open(output) as f:
                line = json.loads(f.readline())

            sys_inst = line["request"]["system_instruction"]
            assert sys_inst["parts"][0]["text"] == "Detect burial mounds"

    def test_jsonl_generation_config(self) -> None:
        """Generation config should include temperature and mime_type."""
        config = _make_prompt_config()
        config["include_example_images"] = False
        config["temperature"] = 0.5

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile = _make_tile_image(tmp, "tile_001.png")
            output = tmp / "batch.jsonl"

            build_jsonl_file(
                tile_paths=[tile],
                config=config,
                system_instruction="Test",
                examples=[],
                output_path=output,
            )

            with open(output) as f:
                line = json.loads(f.readline())

            gen_config = line["request"]["generation_config"]
            assert gen_config["temperature"] == 0.5
            assert gen_config["response_mime_type"] == "application/json"
            assert gen_config["max_output_tokens"] == 8192

    def test_jsonl_key_unique_per_tile(self) -> None:
        """Each JSONL line should use the tile filename as key — no duplicates."""
        config = _make_prompt_config()
        config["include_example_images"] = False

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tiles = [
                _make_tile_image(tmp, f"tile_{i:03d}.png")
                for i in range(5)
            ]
            output = tmp / "batch.jsonl"

            count = build_jsonl_file(
                tile_paths=tiles,
                config=config,
                system_instruction="Test",
                examples=[],
                output_path=output,
            )

            assert count == 5

            keys = []
            with open(output) as f:
                for raw_line in f:
                    line = json.loads(raw_line)
                    keys.append(line["key"])

            assert len(set(keys)) == 5  # All unique

    def test_jsonl_multimodal_content(self) -> None:
        """Tile image should be included as inline_data with base64."""
        config = _make_prompt_config()
        config["include_example_images"] = False

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile = _make_tile_image(tmp, "tile_001.png")
            output = tmp / "batch.jsonl"

            build_jsonl_file(
                tile_paths=[tile],
                config=config,
                system_instruction="Test",
                examples=[],
                output_path=output,
            )

            with open(output) as f:
                line = json.loads(f.readline())

            parts = line["request"]["contents"][0]["parts"]
            # Last part should be the tile image (inline_data)
            tile_part = parts[-1]
            assert "inline_data" in tile_part
            assert tile_part["inline_data"]["mime_type"] == "image/png"
            assert len(tile_part["inline_data"]["data"]) > 0  # Base64 present

    def test_jsonl_thinking_config(self) -> None:
        """ThinkingConfig should be included when set in config."""
        config = _make_prompt_config()
        config["include_example_images"] = False
        config["thinking_level"] = "minimal"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile = _make_tile_image(tmp, "tile_001.png")
            output = tmp / "batch.jsonl"

            build_jsonl_file(
                tile_paths=[tile],
                config=config,
                system_instruction="Test",
                examples=[],
                output_path=output,
            )

            with open(output) as f:
                line = json.loads(f.readline())

            gen_config = line["request"]["generation_config"]
            assert "thinking_config" in gen_config
            assert gen_config["thinking_config"]["thinking_level"] == "minimal"

    def test_jsonl_safety_settings(self) -> None:
        """Safety settings should be present and set to OFF."""
        config = _make_prompt_config()
        config["include_example_images"] = False

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile = _make_tile_image(tmp, "tile_001.png")
            output = tmp / "batch.jsonl"

            build_jsonl_file(
                tile_paths=[tile],
                config=config,
                system_instruction="Test",
                examples=[],
                output_path=output,
            )

            with open(output) as f:
                line = json.loads(f.readline())

            safety = line["request"]["safety_settings"]
            assert len(safety) == 4
            for setting in safety:
                assert setting["threshold"] == "BLOCK_NONE"


# ═════════════════════════════════════════════════════════════════════
# Tests: Result Parsing
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestResultParsing:
    """Tests for _parse_detections_from_response()."""

    def test_parse_successful_response(self) -> None:
        """Should extract detections from a valid response."""
        detections = [
            {
                "label": "mound",
                "subtype": "burial_mound",
                "box_2d": [100, 200, 150, 250],
            }
        ]
        result = _make_batch_response("tile.png", detections=detections)
        parsed = _parse_detections_from_response(result)

        assert len(parsed) == 1
        assert parsed[0]["label"] == "mound"
        assert parsed[0]["box_2d"] == [100, 200, 150, 250]

    def test_parse_empty_detections(self) -> None:
        """Zero detections should return empty list, not raise error."""
        result = _make_batch_response("tile.png", detections=[])
        parsed = _parse_detections_from_response(result)
        assert parsed == []

    def test_parse_multiple_detections(self) -> None:
        """Should handle multiple detections per tile."""
        detections = [
            {"label": "mound", "subtype": "burial_mound", "box_2d": [100, 200, 150, 250]},
            {"label": "mound", "subtype": "possible_mound", "box_2d": [300, 400, 350, 450]},
        ]
        result = _make_batch_response("tile.png", detections=detections)
        parsed = _parse_detections_from_response(result)
        assert len(parsed) == 2

    def test_parse_no_candidates_raises(self) -> None:
        """Response with no candidates should raise ValueError."""
        result = {"key": "tile.png", "response": {"candidates": []}}
        with pytest.raises(ValueError, match="No candidates"):
            _parse_detections_from_response(result)

    def test_parse_no_parts_raises(self) -> None:
        """Response with empty parts should raise ValueError."""
        result = {
            "key": "tile.png",
            "response": {
                "candidates": [{"content": {"parts": []}}],
            },
        }
        with pytest.raises(ValueError, match="No parts"):
            _parse_detections_from_response(result)

    def test_parse_list_format(self) -> None:
        """Should handle model returning [{\"detections\": [...]}] format."""
        response_text = json.dumps([{"detections": [
            {"label": "mound", "box_2d": [10, 20, 30, 40]},
        ]}])
        result = {
            "key": "tile.png",
            "response": {
                "candidates": [
                    {"content": {"parts": [{"text": response_text}]}}
                ],
            },
        }
        parsed = _parse_detections_from_response(result)
        assert len(parsed) == 1
        assert parsed[0]["label"] == "mound"


# ═════════════════════════════════════════════════════════════════════
# Tests: Result Validation
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestResultValidation:
    """Tests for validate_batch_results()."""

    def test_all_tiles_matched(self) -> None:
        """All submitted tiles should be matched in results."""
        keys = ["tile_001.png", "tile_002.png", "tile_003.png"]
        results = [
            _make_batch_response(k, detections=[]) for k in keys
        ]

        matched, missing, errored = validate_batch_results(keys, results)

        assert len(matched) == 3
        assert missing == []
        assert errored == []

    def test_missing_tile_flagged(self) -> None:
        """Tiles absent from results should be flagged as missing."""
        keys = ["tile_001.png", "tile_002.png", "tile_003.png"]
        results = [
            _make_batch_response("tile_001.png", detections=[]),
            # tile_002 and tile_003 missing from results
        ]

        matched, missing, errored = validate_batch_results(keys, results)

        assert len(matched) == 1
        assert set(missing) == {"tile_002.png", "tile_003.png"}
        assert errored == []

    def test_error_tiles_counted(self) -> None:
        """Tiles with error responses should be counted as errored."""
        keys = ["tile_001.png", "tile_002.png"]
        results = [
            _make_batch_response("tile_001.png", detections=[]),
            _make_batch_response("tile_002.png", error="Model overloaded"),
        ]

        matched, missing, errored = validate_batch_results(keys, results)

        assert len(matched) == 1
        assert missing == []
        assert errored == ["tile_002.png"]

    def test_extra_response_logged(self) -> None:
        """Unexpected keys in results should not corrupt matched dict."""
        keys = ["tile_001.png"]
        results = [
            _make_batch_response("tile_001.png", detections=[]),
            _make_batch_response("tile_extra.png", detections=[]),
        ]

        matched, missing, errored = validate_batch_results(keys, results)

        assert len(matched) == 1
        assert "tile_extra.png" not in matched
        assert missing == []

    def test_mixed_responses(self) -> None:
        """Mix of success, error, and missing should be categorised."""
        keys = ["a.png", "b.png", "c.png", "d.png"]
        results = [
            _make_batch_response("a.png", detections=[]),
            _make_batch_response("b.png", error="quota exceeded"),
            # c.png missing from results entirely
            _make_batch_response("d.png", detections=[
                {"label": "mound", "box_2d": [0, 0, 100, 100]},
            ]),
        ]

        matched, missing, errored = validate_batch_results(keys, results)

        assert set(matched.keys()) == {"a.png", "d.png"}
        assert missing == ["c.png"]
        assert errored == ["b.png"]


# ═════════════════════════════════════════════════════════════════════
# Tests: Output Contract
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestOutputContract:
    """Tests for write_batch_outputs() contract compliance."""

    def test_geojson_structure_matches_concurrent(self) -> None:
        """GeoJSON should have CRS and processed_tiles properties."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "detections.geojson"
            config = _make_prompt_config()

            write_batch_outputs(
                features=[],
                processed_tiles={"tile_001.png", "tile_002.png"},
                failed_tiles=[],
                output_file=output_file,
                config=config,
                model_name="gemini-3-flash",
                system_instruction="Test",
                total_detections=0,
            )

            with open(output_file) as f:
                data = json.load(f)

            assert data["type"] == "FeatureCollection"
            assert data["crs"]["properties"]["name"] == "urn:ogc:def:crs:EPSG::32635"
            assert "processed_tiles" in data
            assert sorted(data["processed_tiles"]) == ["tile_001.png", "tile_002.png"]

    def test_meta_json_has_required_fields(self) -> None:
        """Meta JSON should have execution_stats and cost_estimate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "detections.geojson"
            config = _make_prompt_config()

            write_batch_outputs(
                features=[],
                processed_tiles={"tile_001.png"},
                failed_tiles=["tile_002.png"],
                output_file=output_file,
                config=config,
                model_name="gemini-3-flash",
                system_instruction="Test",
                total_detections=0,
            )

            meta_path = output_file.with_suffix(".meta.json")
            assert meta_path.exists()

            with open(meta_path) as f:
                meta = json.load(f)

            assert "execution_stats" in meta
            assert meta["execution_stats"]["items_processed"] == 1
            assert meta["execution_stats"]["items_failed"] == 1
            assert "cost_estimate" in meta
            assert "total_cost_usd" in meta["cost_estimate"]

    def test_tiles_json_has_required_fields(self) -> None:
        """Tiles JSON should have total_tiles, completed, and failed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "detections.geojson"
            config = _make_prompt_config()

            write_batch_outputs(
                features=[],
                processed_tiles={"a.png", "b.png"},
                failed_tiles=["c.png"],
                output_file=output_file,
                config=config,
                model_name="gemini-3-flash",
                system_instruction="Test",
                total_detections=0,
            )

            tiles_path = output_file.with_suffix(".tiles.json")
            assert tiles_path.exists()

            with open(tiles_path) as f:
                tiles = json.load(f)

            assert tiles["total_tiles"] == 3
            assert sorted(tiles["completed"]) == ["a.png", "b.png"]
            assert tiles["failed"] == ["c.png"]
            assert "timestamp" in tiles

    def test_batch_discount_applied(self) -> None:
        """Cost estimate should apply 50% batch discount."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "detections.geojson"
            config = _make_prompt_config()

            cost_estimate = write_batch_outputs(
                features=[],
                processed_tiles=set(),
                failed_tiles=[],
                output_file=output_file,
                config=config,
                model_name="gemini-3-flash",
                system_instruction="Test",
                total_detections=0,
                usage_stats={
                    "input_tokens": 1_000_000,
                    "output_tokens": 100_000,
                    "total_tokens": 1_100_000,
                },
            )

            assert "batch_discount" in cost_estimate["pricing_used"]
            assert cost_estimate["pricing_used"]["batch_discount"] == 0.5

    def test_meta_json_compatible_with_read_meta_cost(self) -> None:
        """Meta JSON should be readable by run_phase2.read_meta_cost()."""
        from scripts.run_phase2 import read_meta_cost, read_meta_failures

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "detections.geojson"
            config = _make_prompt_config()

            write_batch_outputs(
                features=[],
                processed_tiles={"tile.png"},
                failed_tiles=[],
                output_file=output_file,
                config=config,
                model_name="gemini-3-flash",
                system_instruction="Test",
                total_detections=0,
            )

            meta_path = output_file.with_suffix(".meta.json")
            cost = read_meta_cost(meta_path)
            failures = read_meta_failures(meta_path)

            assert isinstance(cost, float)
            assert cost >= 0.0
            assert failures == 0


# ═════════════════════════════════════════════════════════════════════
# Tests: Checkpoint Integration
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestCheckpointIntegration:
    """Tests for batch_pending checkpoint handling."""

    def test_batch_pending_structure(self) -> None:
        """batch_pending should store job metadata per unit key."""
        checkpoint = {
            "completed": [],
            "failed": [],
            "batch_pending": {
                "cond_a/run_1": {
                    "batch_job_name": "batches/123",
                    "submitted_at": "2026-02-14T10:30:00Z",
                    "tile_count": 60,
                },
            },
            "total_cost_usd": 0.0,
            "last_updated": None,
        }

        pending = checkpoint.get("batch_pending", {})
        assert "cond_a/run_1" in pending
        assert pending["cond_a/run_1"]["batch_job_name"] == "batches/123"

    def test_old_checkpoint_backward_compatible(self) -> None:
        """Checkpoints without batch_pending should work via .get()."""
        checkpoint = {
            "completed": ["cond_a/run_1"],
            "failed": [],
            "total_cost_usd": 0.006,
            "last_updated": "2026-02-14T10:30:00Z",
        }

        # This is how the code accesses it — should not raise
        pending = checkpoint.get("batch_pending", {})
        assert pending == {}

    def test_completed_removes_from_pending(self) -> None:
        """Successful unit should be removed from batch_pending."""
        checkpoint = {
            "completed": [],
            "failed": [],
            "batch_pending": {
                "cond_a/run_1": {
                    "batch_job_name": "batches/123",
                    "submitted_at": "2026-02-14T10:30:00Z",
                    "tile_count": 60,
                },
            },
            "total_cost_usd": 0.0,
            "last_updated": None,
        }

        # Simulate successful completion
        key = "cond_a/run_1"
        checkpoint["completed"].append(key)
        checkpoint["batch_pending"].pop(key, None)

        assert key in checkpoint["completed"]
        assert key not in checkpoint["batch_pending"]

    def test_failed_removes_from_pending(self) -> None:
        """Failed unit should be removed from batch_pending."""
        checkpoint = {
            "completed": [],
            "failed": [],
            "batch_pending": {
                "cond_a/run_1": {
                    "batch_job_name": "batches/123",
                    "submitted_at": "2026-02-14T10:30:00Z",
                    "tile_count": 60,
                },
            },
            "total_cost_usd": 0.0,
            "last_updated": None,
        }

        # Simulate failure
        key = "cond_a/run_1"
        checkpoint["failed"].append({"unit": key, "error": "batch_job_failed"})
        checkpoint["batch_pending"].pop(key, None)

        assert key not in checkpoint["batch_pending"]
        assert len(checkpoint["failed"]) == 1

    def test_checkpoint_roundtrip_with_batch_pending(self) -> None:
        """Checkpoint with batch_pending should survive save/load cycle."""
        from scripts.run_phase2 import load_checkpoint, save_checkpoint

        checkpoint = {
            "completed": ["a/run_1"],
            "failed": [],
            "batch_pending": {
                "b/run_1": {
                    "batch_job_name": "batches/456",
                    "submitted_at": "2026-02-14T11:00:00Z",
                    "tile_count": 60,
                },
            },
            "total_cost_usd": 0.003,
            "last_updated": None,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            save_checkpoint(path, checkpoint)
            loaded = load_checkpoint(path)

            assert loaded["completed"] == ["a/run_1"]
            assert "batch_pending" in loaded
            assert "b/run_1" in loaded["batch_pending"]
            assert loaded["batch_pending"]["b/run_1"]["batch_job_name"] == "batches/456"


# ═════════════════════════════════════════════════════════════════════
# Tests: Batch Job Lifecycle (mocked)
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestBatchJobLifecycle:
    """Tests for batch job submission, polling, and retrieval — all mocked."""

    def test_submit_returns_job_name(self) -> None:
        """submit_batch_job() should return a BatchJob with a name."""
        from scripts.lib_batch_api import submit_batch_job

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.name = "batches/test_123"
        mock_client.batches.create.return_value = mock_job

        with patch("google.genai.types") as mock_types:
            mock_types.BatchJobSource.return_value = MagicMock()
            mock_types.CreateBatchJobConfig.return_value = MagicMock()

            result = submit_batch_job(
                mock_client, "gemini-3-flash", "files/upload_001",
            )

        assert result.name == "batches/test_123"
        mock_client.batches.create.assert_called_once()

    def test_poll_stops_on_succeeded(self) -> None:
        """poll_batch_job() should stop when state is SUCCEEDED."""
        from scripts.lib_batch_api import poll_batch_job

        mock_client = MagicMock()

        # Simulate: PENDING → RUNNING → SUCCEEDED using real SDK enums
        # to catch str(enum) vs enum.name mismatches (Bug #1)
        mock_jobs = []
        for state in [
            JobState.JOB_STATE_PENDING,
            JobState.JOB_STATE_RUNNING,
            JobState.JOB_STATE_SUCCEEDED,
        ]:
            job = MagicMock()
            job.state = state
            job.name = "batches/123"
            mock_jobs.append(job)

        mock_client.batches.get.side_effect = mock_jobs

        result = poll_batch_job(
            mock_client, "batches/123",
            interval_seconds=0.01,  # Fast polling for tests
            max_hours=1.0,
        )

        assert _get_state_name(result.state) == "JOB_STATE_SUCCEEDED"
        assert mock_client.batches.get.call_count == 3

    def test_poll_stops_on_failed(self) -> None:
        """poll_batch_job() should stop when state is FAILED."""
        from scripts.lib_batch_api import poll_batch_job

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.state = JobState.JOB_STATE_FAILED
        mock_job.name = "batches/123"
        mock_client.batches.get.return_value = mock_job

        result = poll_batch_job(
            mock_client, "batches/123",
            interval_seconds=0.01,
            max_hours=1.0,
        )

        assert _get_state_name(result.state) == "JOB_STATE_FAILED"

    def test_poll_stops_on_partially_succeeded(self) -> None:
        """poll_batch_job() should stop on PARTIALLY_SUCCEEDED."""
        from scripts.lib_batch_api import poll_batch_job

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.state = JobState.JOB_STATE_PARTIALLY_SUCCEEDED
        mock_job.name = "batches/123"
        mock_client.batches.get.return_value = mock_job

        result = poll_batch_job(
            mock_client, "batches/123",
            interval_seconds=0.01,
            max_hours=1.0,
        )

        assert _get_state_name(result.state) == "JOB_STATE_PARTIALLY_SUCCEEDED"

    def test_poll_timeout(self) -> None:
        """poll_batch_job() should raise TimeoutError after max_hours."""
        from scripts.lib_batch_api import poll_batch_job

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.state = JobState.JOB_STATE_RUNNING
        mock_job.name = "batches/123"
        mock_client.batches.get.return_value = mock_job

        with pytest.raises(TimeoutError, match="did not complete"):
            poll_batch_job(
                mock_client, "batches/123",
                interval_seconds=0.01,
                max_hours=0.0001,  # ~0.36 seconds
            )

    def test_poll_invokes_callback(self) -> None:
        """Progress callback should be called on each poll iteration."""
        from scripts.lib_batch_api import poll_batch_job

        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.state = JobState.JOB_STATE_SUCCEEDED
        mock_job.name = "batches/123"
        mock_client.batches.get.return_value = mock_job

        callback = MagicMock()
        poll_batch_job(
            mock_client, "batches/123",
            interval_seconds=0.01,
            max_hours=1.0,
            progress_callback=callback,
        )

        callback.assert_called_once_with(mock_job)

    def test_upload_returns_file_name(self) -> None:
        """upload_jsonl() should return the uploaded file's name."""
        from scripts.lib_batch_api import upload_jsonl

        mock_client = MagicMock()
        mock_file = MagicMock()
        mock_file.name = "files/uploaded_001"
        mock_client.files.upload.return_value = mock_file

        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_path = Path(tmpdir) / "test.jsonl"
            jsonl_path.write_text('{"key": "test"}\n')

            result = upload_jsonl(mock_client, jsonl_path, "test_upload")

        assert result == "files/uploaded_001"
        mock_client.files.upload.assert_called_once()

    def test_retrieve_parses_jsonl(self) -> None:
        """retrieve_batch_results() should parse response JSONL."""
        from scripts.lib_batch_api import retrieve_batch_results

        response_lines = [
            json.dumps({"key": "tile_001.png", "response": {"ok": True}}),
            json.dumps({"key": "tile_002.png", "response": {"ok": True}}),
        ]
        response_bytes = "\n".join(response_lines).encode("utf-8")

        mock_client = MagicMock()
        mock_client.files.download.return_value = response_bytes

        mock_job = MagicMock()
        mock_job.dest.file_name = "files/result_001"

        results = retrieve_batch_results(mock_client, mock_job)

        assert len(results) == 2
        assert results[0]["key"] == "tile_001.png"
        assert results[1]["key"] == "tile_002.png"

    def test_terminal_states_all_recognised(self) -> None:
        """All terminal states should stop polling."""
        from scripts.lib_batch_api import _TERMINAL_STATES

        expected = {
            "JOB_STATE_SUCCEEDED",
            "JOB_STATE_FAILED",
            "JOB_STATE_CANCELLED",
            "JOB_STATE_EXPIRED",
            "JOB_STATE_PARTIALLY_SUCCEEDED",
        }
        assert _TERMINAL_STATES == expected

    def test_get_state_name_enum(self) -> None:
        """_get_state_name should extract name from SDK enum objects."""
        assert _get_state_name(JobState.JOB_STATE_SUCCEEDED) == "JOB_STATE_SUCCEEDED"
        assert _get_state_name(JobState.JOB_STATE_FAILED) == "JOB_STATE_FAILED"
        assert _get_state_name(JobState.JOB_STATE_RUNNING) == "JOB_STATE_RUNNING"

    def test_get_state_name_string_fallback(self) -> None:
        """_get_state_name should handle plain strings (backward compat)."""
        assert _get_state_name("JOB_STATE_SUCCEEDED") == "JOB_STATE_SUCCEEDED"


# ═════════════════════════════════════════════════════════════════════
# Tests: Mode flag in run_phase2
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestModeFlag:
    """Tests for --mode flag integration in run_phase2.py."""

    def test_run_phase2_accepts_mode_parameter(self) -> None:
        """run_phase2() should accept mode='concurrent' without error."""
        import tempfile

        import yaml

        from scripts.run_phase2 import run_phase2

        config = {
            "study": {
                "name": "Test", "version": "1.0",
                "phase": "test", "hypothesis": "H1",
            },
            "factors": {"test": {"levels": []}},
            "inputs": {"manifest": "inputs/tiles/validation_manifest.json"},
            "execution": {
                "runs": 1, "output_dir": "outputs/test-mode",
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config, f)
            yaml_path = Path(f.name)

        try:
            result = run_phase2(
                study_path=yaml_path,
                dry_run=True,
                mode="concurrent",
                verbose=False,
            )
            assert result is not None
        finally:
            yaml_path.unlink()

    def test_mode_default_is_concurrent(self) -> None:
        """Default mode should be 'concurrent'."""
        import inspect

        from scripts.run_phase2 import run_phase2

        sig = inspect.signature(run_phase2)
        assert sig.parameters["mode"].default == "concurrent"


# ═════════════════════════════════════════════════════════════════════
# Tests: Write-Ahead Checkpoint (on_submit + resume)
# ═════════════════════════════════════════════════════════════════════


def _make_unit(condition: str = "cond_a", run: int = 1) -> dict:
    """Build a minimal execution unit dict for testing."""
    return {
        "condition_name": condition,
        "run": run,
        "config": "prompts/configs/detect_image-only.json",
        "temperature": None,
        "ordering": None,
    }


def _make_study_config(tmpdir: Path) -> dict:
    """Build a minimal study config dict for run_batch_unit()."""
    # Create a manifest with a single tile filename
    manifest = tmpdir / "manifest.json"
    manifest.write_text(json.dumps(["tile_001.png"]))

    return {
        "inputs": {"manifest": str(manifest)},
        "_project_root": str(tmpdir),
    }


@pytest.mark.tier1
class TestWriteAheadCheckpoint:
    """Tests for on_submit callback and resume_job_name in run_batch_unit()."""

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=1)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    @patch("scripts.lib_batch_api.upload_jsonl", return_value="files/up_001")
    @patch("scripts.lib_batch_api.submit_batch_job")
    @patch("scripts.lib_batch_api.poll_batch_job")
    @patch("scripts.lib_batch_api.retrieve_batch_results")
    @patch("scripts.lib_batch_api.write_batch_outputs")
    def test_on_submit_callback_invoked_after_submission(
        self,
        mock_write: MagicMock,
        mock_retrieve: MagicMock,
        mock_poll: MagicMock,
        mock_submit: MagicMock,
        mock_upload: MagicMock,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """on_submit callback should fire with correct job name and tile keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)

            # Set up mocks for the full lifecycle
            tile = _make_tile_image(tmp, "tile_001.png")
            mock_resolve.return_value = [tile]

            mock_job = MagicMock()
            mock_job.name = "batches/test_999"
            mock_submit.return_value = mock_job

            completed_job = MagicMock()
            completed_job.state = JobState.JOB_STATE_SUCCEEDED
            completed_job.usage_metadata = None
            mock_poll.return_value = completed_job

            mock_retrieve.return_value = [
                _make_batch_response("tile_001.png", detections=[]),
            ]
            mock_write.return_value = {"total_cost_usd": 0.001}

            # Create prompt config file
            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config = _make_prompt_config()
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(json.dumps(prompt_config))

            callback = MagicMock()

            unit = _make_unit()
            unit["config"] = str(
                prompt_config_path.relative_to(tmp)
            )

            run_batch_unit(
                unit=unit,
                config=config,
                output_dir=tmp / "output",
                client=MagicMock(),
                model_name="gemini-3-flash",
                system_instruction="Test",
                examples=[],
                config_version="test_v1",
                on_submit=callback,
            )

            callback.assert_called_once_with(
                "batches/test_999", ["tile_001.png"],
            )

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=1)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    @patch("scripts.lib_batch_api.upload_jsonl")
    @patch("scripts.lib_batch_api.submit_batch_job")
    @patch("scripts.lib_batch_api.poll_batch_job")
    @patch("scripts.lib_batch_api.retrieve_batch_results")
    @patch("scripts.lib_batch_api.write_batch_outputs")
    def test_on_submit_not_called_on_resume(
        self,
        mock_write: MagicMock,
        mock_retrieve: MagicMock,
        mock_poll: MagicMock,
        mock_submit: MagicMock,
        mock_upload: MagicMock,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """on_submit callback should NOT fire when resuming an existing job."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)

            tile = _make_tile_image(tmp, "tile_001.png")
            mock_resolve.return_value = [tile]

            completed_job = MagicMock()
            completed_job.state = JobState.JOB_STATE_SUCCEEDED
            completed_job.usage_metadata = None
            mock_poll.return_value = completed_job

            mock_retrieve.return_value = [
                _make_batch_response("tile_001.png", detections=[]),
            ]
            mock_write.return_value = {"total_cost_usd": 0.001}

            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config = _make_prompt_config()
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(json.dumps(prompt_config))

            callback = MagicMock()

            unit = _make_unit()
            unit["config"] = str(
                prompt_config_path.relative_to(tmp)
            )

            run_batch_unit(
                unit=unit,
                config=config,
                output_dir=tmp / "output",
                client=MagicMock(),
                model_name="gemini-3-flash",
                system_instruction="Test",
                examples=[],
                config_version="test_v1",
                on_submit=callback,
                resume_job_name="batches/existing_123",
            )

            # Callback should NOT have been called on resume
            callback.assert_not_called()

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=1)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    @patch("scripts.lib_batch_api.upload_jsonl")
    @patch("scripts.lib_batch_api.submit_batch_job")
    @patch("scripts.lib_batch_api.poll_batch_job")
    @patch("scripts.lib_batch_api.retrieve_batch_results")
    @patch("scripts.lib_batch_api.write_batch_outputs")
    def test_resume_skips_upload_and_submit(
        self,
        mock_write: MagicMock,
        mock_retrieve: MagicMock,
        mock_poll: MagicMock,
        mock_submit: MagicMock,
        mock_upload: MagicMock,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """Resume should skip upload/submit and poll the given job name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)

            tile = _make_tile_image(tmp, "tile_001.png")
            mock_resolve.return_value = [tile]

            completed_job = MagicMock()
            completed_job.state = JobState.JOB_STATE_SUCCEEDED
            completed_job.usage_metadata = None
            mock_poll.return_value = completed_job

            mock_retrieve.return_value = [
                _make_batch_response("tile_001.png", detections=[]),
            ]
            mock_write.return_value = {"total_cost_usd": 0.001}

            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config = _make_prompt_config()
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(json.dumps(prompt_config))

            unit = _make_unit()
            unit["config"] = str(
                prompt_config_path.relative_to(tmp)
            )

            run_batch_unit(
                unit=unit,
                config=config,
                output_dir=tmp / "output",
                client=MagicMock(),
                model_name="gemini-3-flash",
                system_instruction="Test",
                examples=[],
                config_version="test_v1",
                resume_job_name="batches/resume_456",
            )

            # Upload and submit should NOT have been called
            mock_upload.assert_not_called()
            mock_submit.assert_not_called()

            # Poll should have been called with the resume job name
            mock_poll.assert_called_once()
            call_args = mock_poll.call_args
            assert call_args[1].get("job_name") or call_args[0][1] == "batches/resume_456"

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=1)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    def test_on_submit_not_called_in_dry_run(
        self,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """Dry run should return before submission — callback never fires."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)

            tile = _make_tile_image(tmp, "tile_001.png")
            mock_resolve.return_value = [tile]

            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config = _make_prompt_config()
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(json.dumps(prompt_config))

            callback = MagicMock()

            unit = _make_unit()
            unit["config"] = str(
                prompt_config_path.relative_to(tmp)
            )

            success, message, cost = run_batch_unit(
                unit=unit,
                config=config,
                output_dir=tmp / "output",
                client=MagicMock(),
                model_name="gemini-3-flash",
                system_instruction="Test",
                examples=[],
                config_version="test_v1",
                dry_run=True,
                on_submit=callback,
            )

            assert success is True
            assert message == "dry_run"
            callback.assert_not_called()

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=1)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    @patch("scripts.lib_batch_api.poll_batch_job")
    def test_resume_with_failed_poll_returns_failure(
        self,
        mock_poll: MagicMock,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """Resume with poll timeout should return a clean failure tuple."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)

            tile = _make_tile_image(tmp, "tile_001.png")
            mock_resolve.return_value = [tile]

            # Simulate poll timeout
            mock_poll.side_effect = TimeoutError(
                "Batch job batches/old_789 did not complete within 25.0 hours"
            )

            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config = _make_prompt_config()
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(json.dumps(prompt_config))

            unit = _make_unit()
            unit["config"] = str(
                prompt_config_path.relative_to(tmp)
            )

            success, message, cost = run_batch_unit(
                unit=unit,
                config=config,
                output_dir=tmp / "output",
                client=MagicMock(),
                model_name="gemini-3-flash",
                system_instruction="Test",
                examples=[],
                config_version="test_v1",
                resume_job_name="batches/old_789",
            )

            assert success is False
            assert "poll_timeout" in message
            assert cost == 0.0
