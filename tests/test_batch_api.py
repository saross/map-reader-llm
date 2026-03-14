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

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from google.genai.types import JobState

from scripts.lib_batch_api import (
    BatchUnitContext,
    _get_state_name,
    _parse_detections_from_response,
    _resolve_tile_paths,
    audit_file_storage,
    build_jsonl_file,
    cleanup_batch_files,
    complete_batch_unit,
    parse_detections_to_geojson,
    poll_all_batch_jobs,
    prepare_batch_unit,
    run_batch_unit,
    submit_batch_unit,
    sweep_stale_files,
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
            # Config stores lowercase; JSONL uppercases for protobuf
            assert gen_config["thinking_config"]["thinking_level"] == "MINIMAL"

    def test_jsonl_safety_settings_excluded(self) -> None:
        """Safety settings must NOT be in batch JSONL.

        The Gemini Batch API rejects requests containing
        safety_settings with INVALID_ARGUMENT. Verified
        empirically 2026-02.
        """
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

            assert "safety_settings" not in line["request"]


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
                    "uploaded_file_name": "files/up_001",
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
        assert pending["cond_a/run_1"]["uploaded_file_name"] == "files/up_001"

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
                "files/up_001",
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


# ═════════════════════════════════════════════════════════════════════
# Tests: prepare_batch_unit()
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestPrepareBatchUnit:
    """Tests for prepare_batch_unit() context creation."""

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=5)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    def test_returns_context_with_correct_fields(
        self,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """Should return a BatchUnitContext with all fields populated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)

            tiles = [_make_tile_image(tmp, f"tile_{i}.png") for i in range(5)]
            mock_resolve.return_value = tiles

            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config = _make_prompt_config()
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(json.dumps(prompt_config))

            unit = _make_unit()
            unit["config"] = str(
                prompt_config_path.relative_to(tmp)
            )

            ctx = prepare_batch_unit(
                unit=unit,
                config=config,
                output_dir=tmp / "output",
                model_name="gemini-3-flash",
                system_instruction="Test instruction",
                examples=[],
                config_version="test_v1",
            )

            assert ctx is not None
            assert isinstance(ctx, BatchUnitContext)
            assert ctx.unit_key == "cond_a/run_1"
            assert ctx.model_name == "gemini-3-flash"
            assert ctx.system_instruction == "Test instruction"
            assert ctx.config_version == "test_v1"
            assert ctx.line_count == 5
            assert len(ctx.submitted_keys) == 5
            assert len(ctx.tile_paths) == 5

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=2)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    def test_temperature_override_applied(
        self,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """Temperature from unit should override prompt config value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)

            tiles = [_make_tile_image(tmp, f"tile_{i}.png") for i in range(2)]
            mock_resolve.return_value = tiles

            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config = _make_prompt_config()
            prompt_config["temperature"] = 1.0  # Original value
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(json.dumps(prompt_config))

            unit = _make_unit()
            unit["config"] = str(
                prompt_config_path.relative_to(tmp)
            )
            unit["temperature"] = 0.3  # Override

            ctx = prepare_batch_unit(
                unit=unit,
                config=config,
                output_dir=tmp / "output",
                model_name="gemini-3-flash",
                system_instruction="Test",
                examples=[],
                config_version="test_v1",
            )

            assert ctx is not None
            assert ctx.prompt_config["temperature"] == 0.3

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=2)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    def test_tile_limit_applied(
        self,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """Tile limit should truncate the tile list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)

            tiles = [
                _make_tile_image(tmp, f"tile_{i}.png")
                for i in range(10)
            ]
            mock_resolve.return_value = tiles

            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config = _make_prompt_config()
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(json.dumps(prompt_config))

            unit = _make_unit()
            unit["config"] = str(
                prompt_config_path.relative_to(tmp)
            )

            ctx = prepare_batch_unit(
                unit=unit,
                config=config,
                output_dir=tmp / "output",
                model_name="gemini-3-flash",
                system_instruction="Test",
                examples=[],
                config_version="test_v1",
                limit=3,
            )

            assert ctx is not None
            assert len(ctx.tile_paths) == 3
            assert len(ctx.submitted_keys) == 3

    @patch("scripts.lib_batch_api._resolve_tile_paths")
    def test_returns_none_when_no_tiles(
        self,
        mock_resolve: MagicMock,
    ) -> None:
        """Should return None when no tiles are found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)
            mock_resolve.return_value = []

            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(
                json.dumps(_make_prompt_config())
            )

            unit = _make_unit()
            unit["config"] = str(
                prompt_config_path.relative_to(tmp)
            )

            ctx = prepare_batch_unit(
                unit=unit,
                config=config,
                output_dir=tmp / "output",
                model_name="gemini-3-flash",
                system_instruction="Test",
                examples=[],
                config_version="test_v1",
            )

            assert ctx is None


# ═════════════════════════════════════════════════════════════════════
# Tests: submit_batch_unit()
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestSubmitBatchUnit:
    """Tests for submit_batch_unit() upload and submission."""

    @patch("scripts.lib_batch_api.upload_jsonl", return_value="files/up")
    @patch("scripts.lib_batch_api.submit_batch_job")
    def test_upload_and_create_called(
        self,
        mock_submit: MagicMock,
        mock_upload: MagicMock,
    ) -> None:
        """Should call upload_jsonl and submit_batch_job."""
        mock_job = MagicMock()
        mock_job.name = "batches/new_123"
        mock_submit.return_value = mock_job

        ctx = BatchUnitContext(
            unit_key="cond_a/run_1",
            unit=_make_unit(),
            output_file=Path("/tmp/out.geojson"),
            jsonl_path=Path("/tmp/batch.jsonl"),
            submitted_keys=["tile_001.png"],
            tile_paths=[Path("/tmp/tile_001.png")],
            prompt_config=_make_prompt_config(),
            model_name="gemini-3-flash",
            system_instruction="Test",
            config_version="test_v1",
            line_count=1,
        )

        job_name, uploaded_name = submit_batch_unit(ctx, MagicMock())

        assert job_name == "batches/new_123"
        assert uploaded_name == "files/up"
        mock_upload.assert_called_once()
        mock_submit.assert_called_once()

    @patch("scripts.lib_batch_api.upload_jsonl", return_value="files/up")
    @patch("scripts.lib_batch_api.submit_batch_job")
    def test_on_submit_fires_with_correct_args(
        self,
        mock_submit: MagicMock,
        mock_upload: MagicMock,
    ) -> None:
        """on_submit callback should receive job_name and tile keys."""
        mock_job = MagicMock()
        mock_job.name = "batches/xyz"
        mock_submit.return_value = mock_job

        ctx = BatchUnitContext(
            unit_key="cond_a/run_1",
            unit=_make_unit(),
            output_file=Path("/tmp/out.geojson"),
            jsonl_path=Path("/tmp/batch.jsonl"),
            submitted_keys=["a.png", "b.png"],
            tile_paths=[Path("/tmp/a.png"), Path("/tmp/b.png")],
            prompt_config=_make_prompt_config(),
            model_name="gemini-3-flash",
            system_instruction="Test",
            config_version="test_v1",
            line_count=2,
        )

        callback = MagicMock()
        submit_batch_unit(ctx, MagicMock(), on_submit=callback)

        callback.assert_called_once_with(
            "batches/xyz", ["a.png", "b.png"], "files/up",
        )

    @patch("scripts.lib_batch_api.upload_jsonl")
    def test_upload_error_propagates(
        self,
        mock_upload: MagicMock,
    ) -> None:
        """Upload failure should raise to the caller."""
        mock_upload.side_effect = RuntimeError("upload failed")

        ctx = BatchUnitContext(
            unit_key="cond_a/run_1",
            unit=_make_unit(),
            output_file=Path("/tmp/out.geojson"),
            jsonl_path=Path("/tmp/batch.jsonl"),
            submitted_keys=["tile.png"],
            tile_paths=[Path("/tmp/tile.png")],
            prompt_config=_make_prompt_config(),
            model_name="gemini-3-flash",
            system_instruction="Test",
            config_version="test_v1",
            line_count=1,
        )

        with pytest.raises(RuntimeError, match="upload failed"):
            submit_batch_unit(ctx, MagicMock())


# ═════════════════════════════════════════════════════════════════════
# Tests: complete_batch_unit()
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestCompleteBatchUnit:
    """Tests for complete_batch_unit() result processing."""

    @patch("scripts.lib_batch_api.retrieve_batch_results")
    @patch("scripts.lib_batch_api.write_batch_outputs")
    def test_success_path(
        self,
        mock_write: MagicMock,
        mock_retrieve: MagicMock,
    ) -> None:
        """Successful job should return (True, 'success', cost)."""
        mock_retrieve.return_value = [
            _make_batch_response("tile_001.png", detections=[]),
        ]
        mock_write.return_value = {"total_cost_usd": 0.005}

        completed_job = MagicMock()
        completed_job.state = JobState.JOB_STATE_SUCCEEDED
        completed_job.usage_metadata = None

        ctx = BatchUnitContext(
            unit_key="cond_a/run_1",
            unit=_make_unit(),
            output_file=Path("/tmp/out.geojson"),
            jsonl_path=Path("/tmp/batch.jsonl"),
            submitted_keys=["tile_001.png"],
            tile_paths=[Path("/tmp/tile_001.png")],
            prompt_config=_make_prompt_config(),
            model_name="gemini-3-flash",
            system_instruction="Test",
            config_version="test_v1",
            line_count=1,
        )

        success, message, cost = complete_batch_unit(
            ctx, MagicMock(), completed_job,
        )

        assert success is True
        assert message == "success"
        assert cost == 0.005

    def test_failed_state_returns_failure(self) -> None:
        """Non-success terminal state should return failure."""
        completed_job = MagicMock()
        completed_job.state = JobState.JOB_STATE_FAILED

        ctx = BatchUnitContext(
            unit_key="cond_a/run_1",
            unit=_make_unit(),
            output_file=Path("/tmp/out.geojson"),
            jsonl_path=Path("/tmp/batch.jsonl"),
            submitted_keys=["tile.png"],
            tile_paths=[Path("/tmp/tile.png")],
            prompt_config=_make_prompt_config(),
            model_name="gemini-3-flash",
            system_instruction="Test",
            config_version="test_v1",
            line_count=1,
        )

        success, message, cost = complete_batch_unit(
            ctx, MagicMock(), completed_job,
        )

        assert success is False
        assert "JOB_STATE_FAILED" in message
        assert cost == 0.0

    @patch("scripts.lib_batch_api.retrieve_batch_results")
    @patch("scripts.lib_batch_api.write_batch_outputs")
    def test_partial_success_accepted(
        self,
        mock_write: MagicMock,
        mock_retrieve: MagicMock,
    ) -> None:
        """PARTIALLY_SUCCEEDED with ≤2 failures should be accepted."""
        # 59 tiles succeed, 1 tile has error
        keys = [f"tile_{i:03d}.png" for i in range(60)]
        responses = [
            _make_batch_response(k, detections=[]) for k in keys[:59]
        ]
        responses.append(
            _make_batch_response(keys[59], error="model_error")
        )
        mock_retrieve.return_value = responses
        mock_write.return_value = {"total_cost_usd": 0.01}

        completed_job = MagicMock()
        completed_job.state = JobState.JOB_STATE_PARTIALLY_SUCCEEDED
        completed_job.usage_metadata = None

        ctx = BatchUnitContext(
            unit_key="cond_a/run_1",
            unit=_make_unit(),
            output_file=Path("/tmp/out.geojson"),
            jsonl_path=Path("/tmp/batch.jsonl"),
            submitted_keys=keys,
            tile_paths=[Path(f"/tmp/{k}") for k in keys],
            prompt_config=_make_prompt_config(),
            model_name="gemini-3-flash",
            system_instruction="Test",
            config_version="test_v1",
            line_count=60,
        )

        success, message, cost = complete_batch_unit(
            ctx, MagicMock(), completed_job,
        )

        # 1 failure ≤ 2 threshold → accepted
        assert success is True
        assert message == "success"

    @patch("scripts.lib_batch_api.retrieve_batch_results")
    def test_retrieve_error_returns_failure(
        self,
        mock_retrieve: MagicMock,
    ) -> None:
        """Retrieval failure should return a clean failure tuple."""
        mock_retrieve.side_effect = RuntimeError("download failed")

        completed_job = MagicMock()
        completed_job.state = JobState.JOB_STATE_SUCCEEDED

        ctx = BatchUnitContext(
            unit_key="cond_a/run_1",
            unit=_make_unit(),
            output_file=Path("/tmp/out.geojson"),
            jsonl_path=Path("/tmp/batch.jsonl"),
            submitted_keys=["tile.png"],
            tile_paths=[Path("/tmp/tile.png")],
            prompt_config=_make_prompt_config(),
            model_name="gemini-3-flash",
            system_instruction="Test",
            config_version="test_v1",
            line_count=1,
        )

        success, message, cost = complete_batch_unit(
            ctx, MagicMock(), completed_job,
        )

        assert success is False
        assert "retrieve_error" in message
        assert cost == 0.0


# ═════════════════════════════════════════════════════════════════════
# Tests: poll_all_batch_jobs()
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestPollAllBatchJobs:
    """Tests for poll_all_batch_jobs() unified polling loop."""

    def test_single_job_completes(self) -> None:
        """Single job reaching terminal state should be returned."""
        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.state = JobState.JOB_STATE_SUCCEEDED
        mock_job.name = "batches/123"
        mock_client.batches.get.return_value = mock_job

        result = poll_all_batch_jobs(
            mock_client,
            {"unit_a": "batches/123"},
            interval_seconds=0.01,
            max_hours=1.0,
        )

        assert "unit_a" in result
        assert (
            _get_state_name(result["unit_a"].state)
            == "JOB_STATE_SUCCEEDED"
        )

    def test_incremental_completion(self) -> None:
        """Jobs completing at different times should all be returned."""
        mock_client = MagicMock()

        # First cycle: job_a completes, job_b still pending
        # Second cycle: job_b completes
        call_count = {"n": 0}

        def _mock_get(name: str) -> MagicMock:
            call_count["n"] += 1
            job = MagicMock()
            job.name = name
            if name == "batches/a":
                job.state = JobState.JOB_STATE_SUCCEEDED
            elif name == "batches/b":
                if call_count["n"] <= 2:
                    # First cycle: still running
                    job.state = JobState.JOB_STATE_RUNNING
                else:
                    job.state = JobState.JOB_STATE_SUCCEEDED
            return job

        mock_client.batches.get.side_effect = _mock_get

        result = poll_all_batch_jobs(
            mock_client,
            {"unit_a": "batches/a", "unit_b": "batches/b"},
            interval_seconds=0.01,
            max_hours=1.0,
        )

        assert len(result) == 2
        assert "unit_a" in result
        assert "unit_b" in result

    def test_mixed_terminal_states(self) -> None:
        """Jobs with different terminal states should all be returned."""
        mock_client = MagicMock()

        def _mock_get(name: str) -> MagicMock:
            job = MagicMock()
            job.name = name
            if name == "batches/ok":
                job.state = JobState.JOB_STATE_SUCCEEDED
            elif name == "batches/fail":
                job.state = JobState.JOB_STATE_FAILED
            elif name == "batches/expired":
                job.state = JobState.JOB_STATE_EXPIRED
            return job

        mock_client.batches.get.side_effect = _mock_get

        result = poll_all_batch_jobs(
            mock_client,
            {
                "ok_unit": "batches/ok",
                "fail_unit": "batches/fail",
                "expired_unit": "batches/expired",
            },
            interval_seconds=0.01,
            max_hours=1.0,
        )

        assert len(result) == 3
        assert (
            _get_state_name(result["ok_unit"].state)
            == "JOB_STATE_SUCCEEDED"
        )
        assert (
            _get_state_name(result["fail_unit"].state)
            == "JOB_STATE_FAILED"
        )
        assert (
            _get_state_name(result["expired_unit"].state)
            == "JOB_STATE_EXPIRED"
        )

    def test_on_complete_callback_invoked(self) -> None:
        """on_complete should be called for each terminal job."""
        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.state = JobState.JOB_STATE_SUCCEEDED
        mock_job.name = "batches/123"
        mock_client.batches.get.return_value = mock_job

        callback = MagicMock()
        poll_all_batch_jobs(
            mock_client,
            {"unit_a": "batches/123"},
            interval_seconds=0.01,
            max_hours=1.0,
            on_complete=callback,
        )

        callback.assert_called_once()
        call_args = callback.call_args[0]
        assert call_args[0] == "unit_a"
        assert call_args[1] == "batches/123"

    def test_timeout_raises_with_pending_keys(self) -> None:
        """TimeoutError should list pending unit keys."""
        mock_client = MagicMock()
        mock_job = MagicMock()
        mock_job.state = JobState.JOB_STATE_RUNNING
        mock_job.name = "batches/stuck"
        mock_client.batches.get.return_value = mock_job

        with pytest.raises(
            TimeoutError, match="did not complete"
        ):
            poll_all_batch_jobs(
                mock_client,
                {"stuck_unit": "batches/stuck"},
                interval_seconds=0.01,
                max_hours=0.0001,
            )

    def test_empty_jobs_dict_returns_empty(self) -> None:
        """Empty input should return empty dict without polling."""
        mock_client = MagicMock()
        result = poll_all_batch_jobs(
            mock_client, {}, interval_seconds=0.01,
        )
        assert result == {}
        mock_client.batches.get.assert_not_called()


# ═════════════════════════════════════════════════════════════════════
# Tests: File Storage Management
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestCleanupBatchFiles:
    """Tests for cleanup_batch_files() file deletion."""

    def test_deletes_all_files(self) -> None:
        """Should delete all given files and return correct counts."""
        mock_client = MagicMock()

        deleted, errors = cleanup_batch_files(
            mock_client, ["files/a", "files/b", "files/c"],
        )

        assert deleted == 3
        assert errors == 0
        assert mock_client.files.delete.call_count == 3

    def test_continues_on_error(self) -> None:
        """Should continue deleting after individual failures."""
        mock_client = MagicMock()
        mock_client.files.delete.side_effect = [
            None,  # files/a succeeds
            RuntimeError("delete failed"),  # files/b fails
            None,  # files/c succeeds
        ]

        deleted, errors = cleanup_batch_files(
            mock_client, ["files/a", "files/b", "files/c"],
        )

        assert deleted == 2
        assert errors == 1
        assert mock_client.files.delete.call_count == 3

    def test_skips_empty_names(self) -> None:
        """Should skip empty or falsy file names."""
        mock_client = MagicMock()

        deleted, errors = cleanup_batch_files(
            mock_client, ["", "files/a", None, "files/b"],
        )

        assert deleted == 2
        assert errors == 0
        assert mock_client.files.delete.call_count == 2

    def test_empty_list_returns_zeros(self) -> None:
        """Empty input should return (0, 0) without API calls."""
        mock_client = MagicMock()

        deleted, errors = cleanup_batch_files(mock_client, [])

        assert deleted == 0
        assert errors == 0
        mock_client.files.delete.assert_not_called()

    def test_label_does_not_affect_behaviour(self) -> None:
        """Label parameter is for logging only — should not affect logic."""
        mock_client = MagicMock()

        deleted, errors = cleanup_batch_files(
            mock_client, ["files/a"], label="test-label",
        )

        assert deleted == 1
        assert errors == 0


@pytest.mark.tier1
class TestAuditFileStorage:
    """Tests for audit_file_storage() storage enumeration."""

    def test_sums_file_sizes(self) -> None:
        """Should return correct count and total GB."""
        mock_client = MagicMock()

        # Simulate 3 files, 1 GB each
        file_a = MagicMock()
        file_a.size_bytes = 1024 ** 3  # 1 GB
        file_b = MagicMock()
        file_b.size_bytes = 1024 ** 3  # 1 GB
        file_c = MagicMock()
        file_c.size_bytes = 1024 ** 3  # 1 GB

        mock_client.files.list.return_value = [file_a, file_b, file_c]

        count, total_gb = audit_file_storage(mock_client)

        assert count == 3
        assert abs(total_gb - 3.0) < 0.01

    def test_empty_storage(self) -> None:
        """No files should return (0, 0.0)."""
        mock_client = MagicMock()
        mock_client.files.list.return_value = []

        count, total_gb = audit_file_storage(mock_client)

        assert count == 0
        assert total_gb == 0.0

    def test_handles_missing_size_bytes(self) -> None:
        """Files without size_bytes should be counted but contribute 0."""
        mock_client = MagicMock()

        file_a = MagicMock(spec=[])  # No attributes
        file_b = MagicMock()
        file_b.size_bytes = 1024 ** 3

        mock_client.files.list.return_value = [file_a, file_b]

        count, total_gb = audit_file_storage(mock_client)

        assert count == 2
        assert abs(total_gb - 1.0) < 0.01


@pytest.mark.tier1
class TestSweepStaleFiles:
    """Tests for sweep_stale_files() orphan cleanup."""

    def test_deletes_stale_files(self) -> None:
        """Should delete files not in the active set."""
        mock_client = MagicMock()

        file_a = MagicMock()
        file_a.name = "files/active_1"
        file_a.size_bytes = 100_000_000  # 100 MB

        file_b = MagicMock()
        file_b.name = "files/stale_1"
        file_b.size_bytes = 200_000_000  # 200 MB

        file_c = MagicMock()
        file_c.name = "files/stale_2"
        file_c.size_bytes = 300_000_000  # 300 MB

        mock_client.files.list.return_value = [file_a, file_b, file_c]

        active = {"files/active_1"}
        deleted, freed_gb = sweep_stale_files(mock_client, active)

        assert deleted == 2
        assert freed_gb > 0

    def test_no_stale_files(self) -> None:
        """Should return (0, 0.0) when all files are active."""
        mock_client = MagicMock()

        file_a = MagicMock()
        file_a.name = "files/active_1"
        file_a.size_bytes = 100_000_000

        mock_client.files.list.return_value = [file_a]

        active = {"files/active_1"}
        deleted, freed_gb = sweep_stale_files(mock_client, active)

        assert deleted == 0
        assert freed_gb == 0.0
        # delete should not have been called
        mock_client.files.delete.assert_not_called()

    def test_handles_list_failure(self) -> None:
        """Should return (0, 0.0) if files.list() fails."""
        mock_client = MagicMock()
        mock_client.files.list.side_effect = RuntimeError("quota exceeded")

        deleted, freed_gb = sweep_stale_files(mock_client, set())

        assert deleted == 0
        assert freed_gb == 0.0

    def test_empty_storage(self) -> None:
        """Empty file list should return (0, 0.0)."""
        mock_client = MagicMock()
        mock_client.files.list.return_value = []

        deleted, freed_gb = sweep_stale_files(mock_client, set())

        assert deleted == 0
        assert freed_gb == 0.0


# ═════════════════════════════════════════════════════════════════════
# Tests: run_batch_unit() backward-compat wrapper
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestRunBatchUnitWrapper:
    """Tests verifying the wrapper composes the decomposed functions."""

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=1)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    @patch("scripts.lib_batch_api.upload_jsonl", return_value="files/up")
    @patch("scripts.lib_batch_api.submit_batch_job")
    @patch("scripts.lib_batch_api.poll_batch_job")
    @patch("scripts.lib_batch_api.retrieve_batch_results")
    @patch("scripts.lib_batch_api.write_batch_outputs")
    def test_wrapper_calls_all_phases(
        self,
        mock_write: MagicMock,
        mock_retrieve: MagicMock,
        mock_poll: MagicMock,
        mock_submit: MagicMock,
        mock_upload: MagicMock,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """Wrapper should call prepare, submit, poll, and complete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config = _make_study_config(tmp)

            tile = _make_tile_image(tmp, "tile_001.png")
            mock_resolve.return_value = [tile]

            mock_job = MagicMock()
            mock_job.name = "batches/wrapper_test"
            mock_submit.return_value = mock_job

            completed_job = MagicMock()
            completed_job.state = JobState.JOB_STATE_SUCCEEDED
            completed_job.usage_metadata = None
            mock_poll.return_value = completed_job

            mock_retrieve.return_value = [
                _make_batch_response("tile_001.png", detections=[]),
            ]
            mock_write.return_value = {"total_cost_usd": 0.002}

            prompt_dir = tmp / "prompts" / "configs"
            prompt_dir.mkdir(parents=True)
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(
                json.dumps(_make_prompt_config())
            )

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
            )

            assert success is True
            assert message == "success"
            assert cost == 0.002

            # All lifecycle functions should have been called
            mock_resolve.assert_called_once()
            mock_build.assert_called_once()
            mock_upload.assert_called_once()
            mock_submit.assert_called_once()
            mock_poll.assert_called_once()
            mock_retrieve.assert_called_once()
            mock_write.assert_called_once()

    @patch("scripts.lib_batch_api.build_jsonl_file", return_value=1)
    @patch("scripts.lib_batch_api._resolve_tile_paths")
    @patch("scripts.lib_batch_api.poll_batch_job")
    @patch("scripts.lib_batch_api.retrieve_batch_results")
    @patch("scripts.lib_batch_api.write_batch_outputs")
    def test_wrapper_resume_path(
        self,
        mock_write: MagicMock,
        mock_retrieve: MagicMock,
        mock_poll: MagicMock,
        mock_resolve: MagicMock,
        mock_build: MagicMock,
    ) -> None:
        """Resume should skip upload/submit, prepare context, then poll."""
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
            prompt_config_path = prompt_dir / "detect_image-only.json"
            prompt_config_path.write_text(
                json.dumps(_make_prompt_config())
            )

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
                resume_job_name="batches/resume_test",
            )

            assert success is True
            # Preparation should still happen (for context)
            mock_resolve.assert_called_once()
            mock_build.assert_called_once()
            # Poll should use the resume job name
            mock_poll.assert_called_once()
            poll_args = mock_poll.call_args
            assert (
                poll_args[0][1] == "batches/resume_test"
                or poll_args[1].get("job_name") == "batches/resume_test"
            )


# ═════════════════════════════════════════════════════════════════════
# Helpers: GeoTIFF creation for georeferencing tests
# ═════════════════════════════════════════════════════════════════════


def _make_geotiff(
    path: Path,
    tile_size: int = 512,
    origin_x: float = 500000.0,
    origin_y: float = 4700000.0,
    pixel_size: float = 0.5,
) -> Path:
    """
    Create a minimal single-band GeoTIFF with a known affine transform.

    The transform places the tile at (origin_x, origin_y) in UTM zone 35N
    with the given pixel size. This enables deterministic coordinate
    assertions in georeferencing tests.

    Args:
        path: Output file path.
        tile_size: Tile dimension in pixels (width and height).
        origin_x: Easting of the top-left corner (metres).
        origin_y: Northing of the top-left corner (metres).
        pixel_size: Ground distance per pixel (metres).

    Returns:
        The path to the created GeoTIFF.
    """
    transform = from_origin(origin_x, origin_y, pixel_size, pixel_size)
    data = np.zeros((1, tile_size, tile_size), dtype=np.uint8)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=tile_size,
        width=tile_size,
        count=1,
        dtype="uint8",
        crs="EPSG:32635",
        transform=transform,
    ) as dst:
        dst.write(data)

    return path


# ═════════════════════════════════════════════════════════════════════
# Tests: parse_detections_to_geojson()
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestParseDetectionsToGeojson:
    """Tests for parse_detections_to_geojson() — coordinate conversion
    from normalised [0, 1000] space to geographic coordinates via
    rasterio transforms."""

    def test_basic_georeferencing_512(self) -> None:
        """A detection at known normalised coords should produce the
        correct geographic coordinates for a 512-pixel tile."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile_size = 512
            origin_x = 500000.0
            origin_y = 4700000.0
            pixel_size = 0.5

            tile_path = _make_geotiff(
                tmp / "tile_001.png", tile_size=tile_size,
                origin_x=origin_x, origin_y=origin_y,
                pixel_size=pixel_size,
            )

            # Detection at normalised [0, 0, 1000, 1000] = full tile
            matched = {
                "tile_001.png": _make_batch_response(
                    "tile_001.png",
                    detections=[{
                        "label": "mound",
                        "subtype": "burial_mound",
                        "box_2d": [0, 0, 1000, 1000],
                    }],
                ),
            }

            features, total, failures = parse_detections_to_geojson(
                matched_results=matched,
                tile_paths_by_name={"tile_001.png": tile_path},
                config_version="test_v1",
                model_name="gemini-test",
                tile_size=tile_size,
            )

            assert len(features) == 1
            assert total == 1
            assert failures == 0

            # Full tile should span origin to origin + tile_size * pixel_size
            bbox = features[0]["geometry"]["coordinates"][0]
            xs = [c[0] for c in bbox]
            ys = [c[1] for c in bbox]
            expected_width = tile_size * pixel_size  # 256.0m
            assert min(xs) == pytest.approx(origin_x, abs=0.01)
            assert max(xs) == pytest.approx(origin_x + expected_width, abs=0.01)
            # Y axis is inverted (north-up raster: origin_y is top)
            assert min(ys) == pytest.approx(
                origin_y - expected_width, abs=0.01,
            )
            assert max(ys) == pytest.approx(origin_y, abs=0.01)

    def test_tile_size_384_produces_different_coordinates(self) -> None:
        """The same normalised coords should map to a smaller geographic
        extent when tile_size=384 (with same pixel size)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pixel_size = 0.5
            origin_x = 500000.0
            origin_y = 4700000.0

            # Create two tiles with different sizes but same origin/pixel_size
            tile_512 = _make_geotiff(
                tmp / "tile_512.png", tile_size=512,
                origin_x=origin_x, origin_y=origin_y,
                pixel_size=pixel_size,
            )
            tile_384 = _make_geotiff(
                tmp / "tile_384.png", tile_size=384,
                origin_x=origin_x, origin_y=origin_y,
                pixel_size=pixel_size,
            )

            detection = [{
                "label": "mound",
                "subtype": "burial_mound",
                "box_2d": [500, 500, 600, 600],  # centre-ish detection
            }]

            # Parse with tile_size=512
            features_512, _, _ = parse_detections_to_geojson(
                matched_results={
                    "tile_512.png": _make_batch_response(
                        "tile_512.png", detections=detection,
                    ),
                },
                tile_paths_by_name={"tile_512.png": tile_512},
                config_version="test",
                model_name="test",
                tile_size=512,
            )

            # Parse with tile_size=384
            features_384, _, _ = parse_detections_to_geojson(
                matched_results={
                    "tile_384.png": _make_batch_response(
                        "tile_384.png", detections=detection,
                    ),
                },
                tile_paths_by_name={"tile_384.png": tile_384},
                config_version="test",
                model_name="test",
                tile_size=384,
            )

            # Both should produce one feature
            assert len(features_512) == 1
            assert len(features_384) == 1

            # The 384 feature should have a smaller geographic extent
            # (384/512 = 0.75× the pixel coordinates, same pixel_size)
            bbox_512 = features_512[0]["geometry"]["coordinates"][0]
            bbox_384 = features_384[0]["geometry"]["coordinates"][0]

            xs_512 = [c[0] for c in bbox_512]
            xs_384 = [c[0] for c in bbox_384]

            width_512 = max(xs_512) - min(xs_512)
            width_384 = max(xs_384) - min(xs_384)

            assert width_384 == pytest.approx(width_512 * 384 / 512, abs=0.01)

    def test_wrong_tile_size_gives_wrong_coordinates(self) -> None:
        """Using tile_size=512 on a 384-pixel tile should produce
        coordinates that overshoot the tile's actual extent — verifying
        that tile_size matters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pixel_size = 0.5

            # Create a 384-pixel tile
            tile_path = _make_geotiff(
                tmp / "tile.png", tile_size=384, pixel_size=pixel_size,
            )
            tile_extent = 384 * pixel_size  # 192.0m

            # Parse with WRONG tile_size=512
            features, _, _ = parse_detections_to_geojson(
                matched_results={
                    "tile.png": _make_batch_response(
                        "tile.png",
                        detections=[{
                            "label": "mound",
                            "box_2d": [0, 0, 1000, 1000],
                        }],
                    ),
                },
                tile_paths_by_name={"tile.png": tile_path},
                config_version="test",
                model_name="test",
                tile_size=512,  # WRONG — should be 384
            )

            bbox = features[0]["geometry"]["coordinates"][0]
            xs = [c[0] for c in bbox]
            geo_width = max(xs) - min(xs)

            # With wrong tile_size, computed extent overshoots
            assert geo_width == pytest.approx(512 * pixel_size, abs=0.01)
            assert geo_width > tile_extent  # proves mismatch

    def test_multiple_detections_per_tile(self) -> None:
        """Multiple detections in one tile should produce multiple features."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile_path = _make_geotiff(tmp / "tile.png")

            matched = {
                "tile.png": _make_batch_response(
                    "tile.png",
                    detections=[
                        {"label": "mound", "box_2d": [100, 100, 200, 200]},
                        {"label": "mound", "box_2d": [300, 300, 400, 400]},
                        {"label": "mound", "box_2d": [600, 600, 700, 700]},
                    ],
                ),
            }

            features, total, failures = parse_detections_to_geojson(
                matched_results=matched,
                tile_paths_by_name={"tile.png": tile_path},
                config_version="test",
                model_name="test",
            )

            assert len(features) == 3
            assert total == 3
            assert failures == 0

    def test_missing_tile_path_counts_as_failure(self) -> None:
        """Tile present in results but missing from tile_paths_by_name
        should increment parse_failures."""
        matched = {
            "missing_tile.png": _make_batch_response(
                "missing_tile.png",
                detections=[{"label": "mound", "box_2d": [0, 0, 100, 100]}],
            ),
        }

        features, total, failures = parse_detections_to_geojson(
            matched_results=matched,
            tile_paths_by_name={},  # tile not found
            config_version="test",
            model_name="test",
        )

        assert len(features) == 0
        assert failures == 1

    def test_malformed_box_2d_skipped(self) -> None:
        """Detections with invalid box_2d should be silently skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile_path = _make_geotiff(tmp / "tile.png")

            matched = {
                "tile.png": _make_batch_response(
                    "tile.png",
                    detections=[
                        {"label": "mound", "box_2d": [100, 200]},  # too short
                        {"label": "mound", "box_2d": "not_a_list"},  # wrong type
                        {"label": "mound"},  # no box_2d at all
                        {"label": "mound", "box_2d": [0, 0, 100, 100]},  # valid
                    ],
                ),
            }

            features, total, failures = parse_detections_to_geojson(
                matched_results=matched,
                tile_paths_by_name={"tile.png": tile_path},
                config_version="test",
                model_name="test",
            )

            # Only the one valid detection should produce a feature
            assert len(features) == 1
            assert total == 4  # all 4 were counted as detections
            assert failures == 0  # tile itself didn't fail

    def test_feature_properties_populated(self) -> None:
        """GeoJSON features should carry source_tile, label, method, model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile_path = _make_geotiff(tmp / "tile.png")

            matched = {
                "tile.png": _make_batch_response(
                    "tile.png",
                    detections=[{
                        "label": "mound",
                        "subtype": "burial_mound",
                        "box_2d": [100, 200, 300, 400],
                    }],
                ),
            }

            features, _, _ = parse_detections_to_geojson(
                matched_results=matched,
                tile_paths_by_name={"tile.png": tile_path},
                config_version="detect_brief-text",
                model_name="gemini-3-flash",
            )

            props = features[0]["properties"]
            assert props["source_tile"] == "tile.png"
            assert props["label"] == "mound"
            assert props["subtype"] == "burial_mound"
            assert props["method"] == "detect_brief-text"
            assert props["model"] == "gemini-3-flash"

    def test_empty_detections_returns_no_features(self) -> None:
        """A tile with zero detections should produce no features."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tile_path = _make_geotiff(tmp / "tile.png")

            matched = {
                "tile.png": _make_batch_response(
                    "tile.png", detections=[],
                ),
            }

            features, total, failures = parse_detections_to_geojson(
                matched_results=matched,
                tile_paths_by_name={"tile.png": tile_path},
                config_version="test",
                model_name="test",
            )

            assert len(features) == 0
            assert total == 0
            assert failures == 0

    def test_default_tile_size_is_512(self) -> None:
        """When tile_size is not specified, should default to 512 (TILE_SIZE)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pixel_size = 0.5
            tile_path = _make_geotiff(
                tmp / "tile.png", tile_size=512, pixel_size=pixel_size,
            )

            # Detection at [0, 0, 1000, 1000] without explicit tile_size
            matched = {
                "tile.png": _make_batch_response(
                    "tile.png",
                    detections=[{
                        "label": "mound",
                        "box_2d": [0, 0, 1000, 1000],
                    }],
                ),
            }

            features_default, _, _ = parse_detections_to_geojson(
                matched_results=matched,
                tile_paths_by_name={"tile.png": tile_path},
                config_version="test",
                model_name="test",
                # tile_size not specified — should use default
            )

            features_explicit, _, _ = parse_detections_to_geojson(
                matched_results=matched,
                tile_paths_by_name={"tile.png": tile_path},
                config_version="test",
                model_name="test",
                tile_size=512,
            )

            # Both should produce identical coordinates
            bbox_default = features_default[0]["geometry"]["coordinates"][0]
            bbox_explicit = features_explicit[0]["geometry"]["coordinates"][0]
            assert bbox_default == bbox_explicit


# ═════════════════════════════════════════════════════════════════════
# Tests: _resolve_tile_paths()
# ═════════════════════════════════════════════════════════════════════


@pytest.mark.tier1
class TestResolveTilePaths:
    """Tests for _resolve_tile_paths() — manifest-driven tile discovery."""

    def _setup_tiles_dir(
        self, tmpdir: Path, map_name: str, tile_names: list[str],
    ) -> Path:
        """Create a tiles directory with map subdirectories and tile files.

        Args:
            tmpdir: Temporary directory root.
            map_name: Name of the map subdirectory.
            tile_names: List of tile filenames to create.

        Returns:
            Path to the tiles directory.
        """
        tiles_dir = tmpdir / "tiles"
        map_dir = tiles_dir / map_name
        map_dir.mkdir(parents=True)
        for name in tile_names:
            (map_dir / name).write_bytes(b"fake-png")
        return tiles_dir

    def test_resolves_tiles_from_manifest(self) -> None:
        """Should return paths for all tiles listed in the manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tiles_dir = self._setup_tiles_dir(
                tmp, "map_A", ["tile_001.png", "tile_002.png", "tile_003.png"],
            )

            manifest = tmp / "manifest.json"
            manifest.write_text(
                json.dumps(["tile_001.png", "tile_002.png"]),
            )

            paths = _resolve_tile_paths(manifest, tiles_dir=tiles_dir)

            assert len(paths) == 2
            assert all(p.exists() for p in paths)
            names = {p.name for p in paths}
            assert names == {"tile_001.png", "tile_002.png"}

    def test_tiles_dir_override(self) -> None:
        """When tiles_dir is specified, should search that directory
        instead of the default TILES_DIR."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # Create tiles in a non-default directory
            custom_dir = self._setup_tiles_dir(
                tmp, "map_A", ["tile_384_001.png"],
            )

            manifest = tmp / "manifest.json"
            manifest.write_text(json.dumps(["tile_384_001.png"]))

            paths = _resolve_tile_paths(manifest, tiles_dir=custom_dir)

            assert len(paths) == 1
            assert paths[0].name == "tile_384_001.png"
            assert str(custom_dir) in str(paths[0])

    def test_missing_tile_logged_and_skipped(self) -> None:
        """Tiles in manifest but not on disc should be skipped with a
        warning (not raise an error)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tiles_dir = self._setup_tiles_dir(
                tmp, "map_A", ["tile_001.png"],
            )

            manifest = tmp / "manifest.json"
            manifest.write_text(
                json.dumps(["tile_001.png", "tile_missing.png"]),
            )

            paths = _resolve_tile_paths(manifest, tiles_dir=tiles_dir)

            # Only the existing tile should be returned
            assert len(paths) == 1
            assert paths[0].name == "tile_001.png"

    def test_multiple_map_directories(self) -> None:
        """Should discover tiles across multiple map subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tiles_dir = tmp / "tiles"

            # Create two map directories with different tiles
            (tiles_dir / "map_A").mkdir(parents=True)
            (tiles_dir / "map_A" / "tileA.png").write_bytes(b"png")
            (tiles_dir / "map_B").mkdir(parents=True)
            (tiles_dir / "map_B" / "tileB.png").write_bytes(b"png")

            manifest = tmp / "manifest.json"
            manifest.write_text(json.dumps(["tileA.png", "tileB.png"]))

            paths = _resolve_tile_paths(manifest, tiles_dir=tiles_dir)

            assert len(paths) == 2
            names = {p.name for p in paths}
            assert names == {"tileA.png", "tileB.png"}

    def test_empty_manifest_returns_empty(self) -> None:
        """An empty manifest should return an empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tiles_dir = self._setup_tiles_dir(
                tmp, "map_A", ["tile_001.png"],
            )

            manifest = tmp / "manifest.json"
            manifest.write_text(json.dumps([]))

            paths = _resolve_tile_paths(manifest, tiles_dir=tiles_dir)

            assert paths == []

    def test_default_tiles_dir_used_when_none(self) -> None:
        """When tiles_dir is None, should fall back to TILES_DIR from
        config (tested via mock to avoid filesystem dependency)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            manifest = tmp / "manifest.json"
            manifest.write_text(json.dumps(["tile_001.png"]))

            # Mock TILES_DIR to point to our temp directory
            mock_tiles_dir = self._setup_tiles_dir(
                tmp, "map_A", ["tile_001.png"],
            )

            with patch(
                "scripts.lib_batch_api.TILES_DIR", mock_tiles_dir,
            ):
                paths = _resolve_tile_paths(manifest)  # no tiles_dir arg

            assert len(paths) == 1
            assert paths[0].name == "tile_001.png"
