"""
Tier-1 tests for the verifier completeness surfacing fix (Layer 1).

Covers the fix for the silent-drop bug
(reports/verifier-silent-drop-root-cause-2026-05-03.md), which between
commits ``5d725930`` (March 2026) and 2026-05-03 allowed 30 verifier
cells to drop 835 candidates with empty ``failed_items[]`` arrays.

Tests verify:

- ``_verify_realtime`` calls ``log_failure`` / ``log_success`` per
  candidate (taxonomy modes 1–4, 6–9, 11, 13 from the root-cause
  report).
- ``_assert_completeness`` correctly compares manifest cardinality to
  results, backfills missing IDs into ``failed_items[]``, and is
  idempotent against pre-existing entries.
- The ``--no-strict`` CLI flag toggles between fail-loud (default) and
  permissive exit codes.
- ``cmd_cleanup`` propagates ``strict=False`` so its own audit trail
  is not short-circuited.
- ``_log_cleanup_failures_to_meta`` is idempotent.
- The end-to-end "gap=57 cell shape" regression case (the empirical
  bug shape) now produces a non-empty ``failed_items[]`` and a
  non-zero exit code.

No API calls are made — ``verify_candidate_realtime`` is mocked.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib_llm_metadata import (
    LLMMetadataTracker,
    LLMProvider,
    LLMResponseMetadata,
)
from scripts.run_pv import (  # noqa: E402
    _assert_completeness,
    _build_parser,
    _candidate_iteration_keys,
    _candidate_result_key,
    _compute_missing_candidates,
    _iteration_id_to_result_key,
    _log_cleanup_failures_to_meta,
    _summarise_failure_reason,
    _verify_realtime,
    _write_verification_outputs,
    cmd_cleanup,
)


# ─────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────


def _make_manifest(n_candidates: int) -> dict:
    """Build a minimal candidate manifest with ``n_candidates`` candidates."""
    return {
        "version": "1.0",
        "candidates": [
            {
                "candidate_id": i,
                "source_tile": f"tile_{i}.png",
                "centroid_x": 400000.0 + i,
                "centroid_y": 4700000.0 + i,
            }
            for i in range(n_candidates)
        ],
    }


def _make_config(version: str = "test-v1") -> dict:
    """Build a minimal verifier config dict."""
    return {
        "version": version,
        "model": "gemini-3-flash",
        "temperature": 0.0,
        "max_output_tokens": 8192,
        "instruction_file": "test.md",
    }


def _make_tracker(config: dict | None = None) -> LLMMetadataTracker:
    """Build a fresh ``LLMMetadataTracker`` for assertions."""
    return LLMMetadataTracker(
        config=config or _make_config(),
        system_instruction="test instruction",
        script_name="test",
        script_version="0.0.0",
        model_override="gemini-3-flash",
    )


def _make_response_metadata(
    item_id: str,
    parse_error: str | None = None,
    parse_success: bool = True,
) -> LLMResponseMetadata:
    """Build an ``LLMResponseMetadata`` for mock metadata_list returns."""
    return LLMResponseMetadata(
        provider=LLMProvider.GEMINI.value,
        model_requested="gemini-3-flash",
        item_id=item_id,
        attempt_number=1,
        parse_success=parse_success,
        parse_error=parse_error,
    )


def _make_args(**kwargs) -> argparse.Namespace:
    """Build a Namespace mimicking parsed CLI arguments for cmd_cleanup."""
    defaults = {
        "crops_dir": None,
        "verified_dir": None,
        "verifier_config": None,
        "service_tier": None,
        "workers": 5,
        "iterations": 1,
        "temperature": None,
        "model": None,
        "thinking_level": None,
        "max_attempts": 3,
        "safe_mode_tokens": None,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _setup_cleanup_dirs(
    tmp_path: Path,
    n_candidates: int = 5,
    verified_ids: list[int] | None = None,
) -> tuple[Path, Path, Path]:
    """Build a crops dir, verified dir, and config for cleanup tests."""
    if verified_ids is None:
        verified_ids = [0, 1]  # default: 2 of 5 verified

    crops_dir = tmp_path / "crops"
    crops_dir.mkdir()
    manifest = _make_manifest(n_candidates)
    with open(crops_dir / "candidate_manifest.json", "w") as f:
        json.dump(manifest, f)

    verified_dir = tmp_path / "verified"
    verified_dir.mkdir()
    probs = {
        "version": "1.0",
        "mode": "realtime",
        "verifier_config": "test-v1",
        "iterations": 1,
        "total_results": len(verified_ids),
        "results": {
            f"candidate_{cid:05d}": {"mound_probability": 0.5}
            for cid in verified_ids
        },
    }
    with open(verified_dir / "probabilities.json", "w") as f:
        json.dump(probs, f)

    config_path = tmp_path / "verifier.json"
    with open(config_path, "w") as f:
        json.dump(_make_config(), f)

    return crops_dir, verified_dir, config_path


def _patch_resolve_model_name():
    """Bypass the API client's model-name resolution in unit tests."""
    return patch(
        "scripts.run_pv._resolve_model_name",
        side_effect=lambda client, name: name,
    )


def _patch_genai_client():
    """Stub the google-genai client constructor."""
    class _StubClient:
        def __init__(self, *args, **kwargs):
            self.models = type("M", (), {"list": lambda self: []})()

    return patch("google.genai.Client", _StubClient)


def _patch_get_api_key():
    """Bypass the api-key lookup."""
    return patch("scripts.run_pv._get_api_key", return_value="test-key")


# ─────────────────────────────────────────────────────────────────────
# L1-A through L1-C: log_failure / log_success in _verify_realtime
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestVerifyRealtimeLogging:
    """``_verify_realtime`` records per-candidate success/failure."""

    def _run_realtime(
        self,
        tmp_path: Path,
        worker_side_effect,
        n_candidates: int = 3,
        iterations: int = 1,
        strict: bool = True,
    ) -> int:
        """Drive ``_verify_realtime`` against a mocked worker.

        Returns the exit code from ``_verify_realtime``.
        """
        manifest = _make_manifest(n_candidates)
        config = _make_config()
        crops_dir = tmp_path / "crops"
        crops_dir.mkdir()
        output_dir = tmp_path / "verified"

        with (
            _patch_get_api_key(),
            _patch_genai_client(),
            _patch_resolve_model_name(),
            patch(
                "scripts.run_pv.verify_candidate_realtime",
                side_effect=worker_side_effect,
            ),
            patch("scripts.run_pv.load_system_instruction", return_value=""),
            patch("scripts.run_pv.build_reference_items", return_value=[]),
            patch("scripts.run_pv.build_generation_config", return_value={}),
            patch("scripts.run_pv.gen_config_to_sdk", return_value=None),
        ):
            return _verify_realtime(
                manifest=manifest,
                config=config,
                crops_base_dir=crops_dir,
                output_dir=output_dir,
                workers=1,
                iterations=iterations,
                temperature=None,
                model_override="gemini-3-flash",
                strict=strict,
            )

    def test_logs_failure_on_empty_results(self, tmp_path: Path) -> None:
        """L1-A: empty cand_results triggers log_failure with canonical key."""
        captured: list[LLMMetadataTracker] = []

        original_init = LLMMetadataTracker.__init__

        def init_spy(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            captured.append(self)

        def worker(*, candidate, **kwargs):
            cid = candidate["candidate_id"]
            if cid == 1:
                # Simulate retry exhaustion: empty results, parse_error.
                meta = _make_response_metadata(
                    item_id=f"cand_{cid:04d}_iter1",
                    parse_error="EMPTY_RESPONSE",
                    parse_success=False,
                )
                return {}, [meta]
            return (
                {f"candidate_{cid:05d}": {"mound_probability": 0.5}},
                [_make_response_metadata(f"cand_{cid:04d}_iter1")],
            )

        with patch.object(LLMMetadataTracker, "__init__", init_spy):
            self._run_realtime(tmp_path, worker, n_candidates=3, strict=False)

        assert captured, "tracker not constructed"
        tracker = captured[0]
        failed_ids = {f["item_id"] for f in tracker.stats.failed_items}
        assert "candidate_00001" in failed_ids
        # Reason must reflect the parse_error from metadata_list
        match = next(
            f for f in tracker.stats.failed_items
            if f["item_id"] == "candidate_00001"
        )
        assert "EMPTY_RESPONSE" in match["reason"]

    def test_logs_success_on_results(self, tmp_path: Path) -> None:
        """L1-B: populated cand_results triggers log_success per candidate."""
        captured: list[LLMMetadataTracker] = []
        original_init = LLMMetadataTracker.__init__

        def init_spy(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            captured.append(self)

        def worker(*, candidate, **kwargs):
            cid = candidate["candidate_id"]
            return (
                {f"candidate_{cid:05d}": {"mound_probability": 0.5}},
                [_make_response_metadata(f"cand_{cid:04d}_iter1")],
            )

        with patch.object(LLMMetadataTracker, "__init__", init_spy):
            self._run_realtime(tmp_path, worker, n_candidates=3)

        tracker = captured[0]
        completed = set(tracker.stats.completed_items)
        assert completed == {
            "candidate_00000", "candidate_00001", "candidate_00002",
        }

    def test_logs_failure_on_worker_exception(self, tmp_path: Path) -> None:
        """L1-C: worker-raised exceptions hit the unhandled-driver path."""
        captured: list[LLMMetadataTracker] = []
        original_init = LLMMetadataTracker.__init__

        def init_spy(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            captured.append(self)

        def worker(*, candidate, **kwargs):
            cid = candidate["candidate_id"]
            if cid == 1:
                raise RuntimeError("simulated worker explosion")
            return (
                {f"candidate_{cid:05d}": {"mound_probability": 0.5}},
                [_make_response_metadata(f"cand_{cid:04d}_iter1")],
            )

        with patch.object(LLMMetadataTracker, "__init__", init_spy):
            self._run_realtime(tmp_path, worker, n_candidates=3, strict=False)

        tracker = captured[0]
        failed_ids = {f["item_id"] for f in tracker.stats.failed_items}
        assert "candidate_00001" in failed_ids
        match = next(
            f for f in tracker.stats.failed_items
            if f["item_id"] == "candidate_00001"
        )
        assert "unhandled in driver" in match["reason"]
        assert "RuntimeError" in match["reason"]


# ─────────────────────────────────────────────────────────────────────
# L1-D through L1-G: _assert_completeness behaviour
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestAssertCompleteness:
    """``_assert_completeness`` semantics — gap detection and backfill."""

    def test_no_gap(self, caplog) -> None:
        """L1-D: complete results return 0 with no warnings or backfill."""
        manifest = _make_manifest(5)
        tracker = _make_tracker()
        results = {
            f"candidate_{i:05d}": {"mound_probability": 0.5}
            for i in range(5)
        }

        with caplog.at_level(logging.WARNING, logger="scripts.run_pv"):
            gap = _assert_completeness(
                parsed_results=results,
                manifest=manifest,
                iterations=1,
                mode="realtime",
                metadata_tracker=tracker,
                strict=True,
            )

        assert gap == 0
        assert tracker.stats.failed_items == []
        assert "Completeness gap" not in caplog.text

    def test_gap_strict(self) -> None:
        """L1-E: missing IDs are backfilled and summary populated."""
        manifest = _make_manifest(5)
        tracker = _make_tracker()
        # Only 3 of 5 candidates present
        results = {
            f"candidate_{i:05d}": {"mound_probability": 0.5}
            for i in (0, 2, 4)
        }

        gap = _assert_completeness(
            parsed_results=results,
            manifest=manifest,
            iterations=1,
            mode="realtime",
            metadata_tracker=tracker,
            strict=True,
        )

        assert gap == 2
        failed_ids = {f["item_id"] for f in tracker.stats.failed_items}
        assert failed_ids == {"candidate_00001", "candidate_00003"}
        summary = tracker.results_summary["completeness_gap"]
        assert summary["expected"] == 5
        assert summary["actual"] == 3
        assert summary["missing_count"] == 2
        assert sorted(summary["missing_ids_sample"]) == [
            "candidate_00001", "candidate_00003",
        ]

    def test_gap_already_logged_no_dup(self) -> None:
        """L1-F: pre-existing failed_items entries are preserved, not duplicated."""
        manifest = _make_manifest(5)
        tracker = _make_tracker()
        # Pre-populate with one of the missing IDs
        tracker.log_failure("candidate_00001", "previously logged")
        results = {
            f"candidate_{i:05d}": {"mound_probability": 0.5}
            for i in (0, 2, 4)
        }

        _assert_completeness(
            parsed_results=results,
            manifest=manifest,
            iterations=1,
            mode="realtime",
            metadata_tracker=tracker,
            strict=True,
        )

        # Exactly two failed_items entries — original + one new
        ids = [f["item_id"] for f in tracker.stats.failed_items]
        assert ids.count("candidate_00001") == 1
        assert "candidate_00003" in ids
        # Original reason preserved
        original = next(
            f for f in tracker.stats.failed_items
            if f["item_id"] == "candidate_00001"
        )
        assert original["reason"] == "previously logged"

    def test_consensus_iterations(self) -> None:
        """L1-G: 3 candidates × 3 iterations expects 9 keys."""
        manifest = _make_manifest(3)
        tracker = _make_tracker()
        # Only 7 of the 9 expected iter-keys present
        results = {
            "candidate_00000_iter1": {"mound_probability": 0.5},
            "candidate_00000_iter2": {"mound_probability": 0.5},
            "candidate_00000_iter3": {"mound_probability": 0.5},
            "candidate_00001_iter1": {"mound_probability": 0.5},
            "candidate_00001_iter2": {"mound_probability": 0.5},
            "candidate_00002_iter1": {"mound_probability": 0.5},
            "candidate_00002_iter2": {"mound_probability": 0.5},
        }

        gap = _assert_completeness(
            parsed_results=results,
            manifest=manifest,
            iterations=3,
            mode="realtime",
            metadata_tracker=tracker,
            strict=True,
        )

        assert gap == 2
        failed_ids = {f["item_id"] for f in tracker.stats.failed_items}
        assert failed_ids == {
            "candidate_00001_iter3", "candidate_00002_iter3",
        }

    def test_metadata_tracker_none(self, caplog) -> None:
        """``metadata_tracker=None`` must not raise; gap is still surfaced.

        Defensive-branch coverage: ``_assert_completeness`` may be
        called from a code path that has no tracker (no future call
        site does today, but the optional parameter shape needs to be
        honoured). The function must still log the warning, return the
        gap count, and skip the per-tracker side effects (no AttributeError
        on tracker.stats / tracker.results_summary access).
        """
        manifest = _make_manifest(3)
        # Only 1 of 3 candidates present
        results = {"candidate_00000": {"mound_probability": 0.5}}

        with caplog.at_level(logging.ERROR, logger="scripts.run_pv"):
            gap = _assert_completeness(
                parsed_results=results,
                manifest=manifest,
                iterations=1,
                mode="realtime",
                metadata_tracker=None,
                strict=True,
            )

        assert gap == 2
        # Error log fired even without a tracker — completeness gap is
        # the primary user-visible signal.
        assert "Completeness gap" in caplog.text
        # No exception is enough — the assertion is the absence of one.

    def test_empty_manifest(self, caplog) -> None:
        """Zero candidates × zero results returns 0 with no side effects.

        Boundary case — an empty manifest could exercise the iteration
        helpers in unexpected ways (set-difference of empty sets, sample
        truncation, etc.). The helper must short-circuit with no warning
        log and no failed_items entries.
        """
        manifest = {"version": "1.0", "candidates": []}
        tracker = _make_tracker()

        with caplog.at_level(logging.ERROR, logger="scripts.run_pv"):
            gap = _assert_completeness(
                parsed_results={},
                manifest=manifest,
                iterations=1,
                mode="realtime",
                metadata_tracker=tracker,
                strict=True,
            )

        assert gap == 0
        assert tracker.stats.failed_items == []
        assert "Completeness gap" not in caplog.text


# ─────────────────────────────────────────────────────────────────────
# L1-H, L1-I: end-to-end strict / non-strict + on-disk meta
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestVerifyRealtimeStrictness:
    """End-to-end strict / non-strict exit codes from ``_verify_realtime``."""

    def _run(
        self,
        tmp_path: Path,
        n_candidates: int,
        worker_side_effect,
        strict: bool,
    ) -> tuple[int, Path]:
        manifest = _make_manifest(n_candidates)
        config = _make_config()
        crops_dir = tmp_path / "crops"
        crops_dir.mkdir()
        output_dir = tmp_path / "verified"

        with (
            _patch_get_api_key(),
            _patch_genai_client(),
            _patch_resolve_model_name(),
            patch(
                "scripts.run_pv.verify_candidate_realtime",
                side_effect=worker_side_effect,
            ),
            patch("scripts.run_pv.load_system_instruction", return_value=""),
            patch("scripts.run_pv.build_reference_items", return_value=[]),
            patch("scripts.run_pv.build_generation_config", return_value={}),
            patch("scripts.run_pv.gen_config_to_sdk", return_value=None),
        ):
            exit_code = _verify_realtime(
                manifest=manifest,
                config=config,
                crops_base_dir=crops_dir,
                output_dir=output_dir,
                workers=1,
                iterations=1,
                temperature=None,
                model_override="gemini-3-flash",
                strict=strict,
            )
        return exit_code, output_dir

    def test_strict_returns_nonzero_on_gap(self, tmp_path: Path) -> None:
        """L1-H: strict mode → exit 1 on gap; --no-strict → exit 0; both populate
        failed_items[].
        """
        def worker(*, candidate, **kwargs):
            cid = candidate["candidate_id"]
            if cid == 1:
                return {}, [_make_response_metadata(
                    f"cand_{cid:04d}_iter1",
                    parse_error="EMPTY_RESPONSE",
                    parse_success=False,
                )]
            return (
                {f"candidate_{cid:05d}": {"mound_probability": 0.5}},
                [_make_response_metadata(f"cand_{cid:04d}_iter1")],
            )

        # Strict: gap → exit 1
        strict_dir = tmp_path / "strict"
        strict_dir.mkdir()
        with (
            _patch_get_api_key(),
            _patch_genai_client(),
            _patch_resolve_model_name(),
            patch(
                "scripts.run_pv.verify_candidate_realtime",
                side_effect=worker,
            ),
            patch("scripts.run_pv.load_system_instruction", return_value=""),
            patch("scripts.run_pv.build_reference_items", return_value=[]),
            patch("scripts.run_pv.build_generation_config", return_value={}),
            patch("scripts.run_pv.gen_config_to_sdk", return_value=None),
        ):
            strict_code = _verify_realtime(
                manifest=_make_manifest(5),
                config=_make_config(),
                crops_base_dir=tmp_path / "crops",
                output_dir=strict_dir,
                workers=1,
                iterations=1,
                temperature=None,
                model_override="gemini-3-flash",
                strict=True,
            )
        assert strict_code == 1
        meta = json.load(open(strict_dir / "run.meta.json"))
        failed = meta["execution_stats"]["failed_items"]
        assert any(f["item_id"] == "candidate_00001" for f in failed)

        # Non-strict: gap → exit 0, but failed_items still populated
        permissive_dir = tmp_path / "permissive"
        permissive_dir.mkdir()
        with (
            _patch_get_api_key(),
            _patch_genai_client(),
            _patch_resolve_model_name(),
            patch(
                "scripts.run_pv.verify_candidate_realtime",
                side_effect=worker,
            ),
            patch("scripts.run_pv.load_system_instruction", return_value=""),
            patch("scripts.run_pv.build_reference_items", return_value=[]),
            patch("scripts.run_pv.build_generation_config", return_value={}),
            patch("scripts.run_pv.gen_config_to_sdk", return_value=None),
        ):
            permissive_code = _verify_realtime(
                manifest=_make_manifest(5),
                config=_make_config(),
                crops_base_dir=tmp_path / "crops",
                output_dir=permissive_dir,
                workers=1,
                iterations=1,
                temperature=None,
                model_override="gemini-3-flash",
                strict=False,
            )
        assert permissive_code == 0
        meta = json.load(open(permissive_dir / "run.meta.json"))
        failed = meta["execution_stats"]["failed_items"]
        assert any(f["item_id"] == "candidate_00001" for f in failed)

    def test_writes_failed_items_to_meta(self, tmp_path: Path) -> None:
        """L1-I: failed_items[] is persisted to run.meta.json on disk."""
        def worker(*, candidate, **kwargs):
            cid = candidate["candidate_id"]
            if cid == 0:
                return {}, [_make_response_metadata(
                    f"cand_{cid:04d}_iter1",
                    parse_error="JSONDecodeError: bad",
                    parse_success=False,
                )]
            return (
                {f"candidate_{cid:05d}": {"mound_probability": 0.5}},
                [_make_response_metadata(f"cand_{cid:04d}_iter1")],
            )

        exit_code, output_dir = self._run(
            tmp_path, n_candidates=3, worker_side_effect=worker, strict=False,
        )
        assert exit_code == 0  # non-strict
        meta = json.load(open(output_dir / "run.meta.json"))
        failed = meta["execution_stats"]["failed_items"]
        assert len(failed) >= 1
        assert failed[0]["item_id"] == "candidate_00000"


# ─────────────────────────────────────────────────────────────────────
# L1-J, L1-K: _summarise_failure_reason
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestSummariseFailureReason:
    """``_summarise_failure_reason`` extraction logic."""

    def test_extracts_parse_error(self) -> None:
        """L1-J: parse_error from the most recent metadata entry is returned."""
        metadata_list = [
            _make_response_metadata(
                "cand_0001_iter1",
                parse_error="JSONDecodeError: Expecting value",
                parse_success=False,
            ),
        ]
        reason = _summarise_failure_reason(metadata_list)
        assert "JSONDecodeError" in reason

    def test_handles_empty_list(self) -> None:
        """L1-K: empty metadata_list yields the generic fallback."""
        reason = _summarise_failure_reason([])
        assert reason == "no result returned (retries exhausted)"


# ─────────────────────────────────────────────────────────────────────
# L1-L: _log_cleanup_failures_to_meta idempotence
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestLogCleanupFailuresIdempotent:
    """``_log_cleanup_failures_to_meta`` does not duplicate existing entries."""

    def test_idempotent(self, tmp_path: Path) -> None:
        """L1-L: pre-existing failed_items[] entries are preserved exactly."""
        verified_dir = tmp_path / "verified"
        verified_dir.mkdir()
        meta_path = verified_dir / "run.meta.json"
        existing_meta = {
            "execution_stats": {
                "failed_items": [
                    {
                        "item_id": "candidate_00003",
                        "reason": "originally failed",
                        "timestamp": "2026-01-01T00:00:00Z",
                    },
                ],
            },
        }
        with open(meta_path, "w") as f:
            json.dump(existing_meta, f)

        _log_cleanup_failures_to_meta(
            verified_dir,
            {"candidate_00003", "candidate_00007"},
        )

        meta = json.load(open(meta_path))
        failed = meta["execution_stats"]["failed_items"]
        ids = [f["item_id"] for f in failed]
        # candidate_00003 appears exactly once (preserved)
        assert ids.count("candidate_00003") == 1
        # candidate_00007 is the new entry
        assert "candidate_00007" in ids
        # Total: original + 1 new = 2
        assert len(failed) == 2
        # Existing reason preserved
        original = next(f for f in failed if f["item_id"] == "candidate_00003")
        assert original["reason"] == "originally failed"

    def test_no_meta_file_is_noop(self, tmp_path: Path) -> None:
        """When run.meta.json does not exist, the helper silently no-ops."""
        verified_dir = tmp_path / "verified"
        verified_dir.mkdir()

        _log_cleanup_failures_to_meta(verified_dir, {"candidate_00001"})

        # Should not have created the file
        assert not (verified_dir / "run.meta.json").exists()


# ─────────────────────────────────────────────────────────────────────
# L1-M: cmd_cleanup propagates strict=False
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestCmdCleanupStrictPropagation:
    """``cmd_cleanup`` calls ``_verify_realtime`` with ``strict=False``."""

    def test_propagates_strict_false(self, tmp_path: Path) -> None:
        """L1-M: cmd_cleanup invokes _verify_realtime with strict=False."""
        crops_dir, verified_dir, config_path = _setup_cleanup_dirs(
            tmp_path, n_candidates=5, verified_ids=[0, 1, 2],
        )

        captured_kwargs: list[dict] = []

        def fake_verify(*args, **kwargs):
            captured_kwargs.append(dict(kwargs))
            return 0  # do nothing — leaves candidates 3, 4 missing

        with patch("scripts.run_pv._verify_realtime", side_effect=fake_verify):
            args = _make_args(
                crops_dir=crops_dir,
                verified_dir=verified_dir,
                verifier_config=config_path,
                max_attempts=1,
            )
            cmd_cleanup(args)

        assert captured_kwargs, "_verify_realtime was not called"
        assert captured_kwargs[0].get("strict") is False


# ─────────────────────────────────────────────────────────────────────
# L1-N: --no-strict CLI flag default
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestNoStrictCliFlag:
    """The ``--no-strict`` CLI flag toggles the ``strict`` namespace value."""

    def test_default_strict(self) -> None:
        """L1-N (a): default verify args have strict=True."""
        parser = _build_parser()
        args = parser.parse_args([
            "verify",
            "--crops-dir", ".",
            "--verifier-config", "x.json",
            "--output-dir", ".",
        ])
        assert args.strict is True

    def test_no_strict_flag(self) -> None:
        """L1-N (b): --no-strict yields strict=False."""
        parser = _build_parser()
        args = parser.parse_args([
            "verify",
            "--crops-dir", ".",
            "--verifier-config", "x.json",
            "--output-dir", ".",
            "--no-strict",
        ])
        assert args.strict is False


# ─────────────────────────────────────────────────────────────────────
# L1-R: regression — empirical gap=57 cell shape (canary)
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestRegressionGap57Shape:
    """Regression for the empirical gap=57 cell shape.

    Mirrors ``outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/
    run.meta.json``: every candidate produces ``({}, [meta with
    parse_error='EMPTY_RESPONSE'])``. Pre-fix this resulted in
    ``failed_items: []``; post-fix every candidate must appear.
    """

    def test_gap57_shape_surfaces(self, tmp_path: Path) -> None:
        """L1-R: failed_items[] populated; exit 1; completed_items empty."""
        n_candidates = 5

        def worker(*, candidate, **kwargs):
            cid = candidate["candidate_id"]
            return {}, [_make_response_metadata(
                f"cand_{cid:04d}_iter1",
                parse_error="EMPTY_RESPONSE",
                parse_success=False,
            )]

        manifest = _make_manifest(n_candidates)
        config = _make_config()
        crops_dir = tmp_path / "crops"
        crops_dir.mkdir()
        output_dir = tmp_path / "verified"

        with (
            _patch_get_api_key(),
            _patch_genai_client(),
            _patch_resolve_model_name(),
            patch(
                "scripts.run_pv.verify_candidate_realtime",
                side_effect=worker,
            ),
            patch("scripts.run_pv.load_system_instruction", return_value=""),
            patch("scripts.run_pv.build_reference_items", return_value=[]),
            patch("scripts.run_pv.build_generation_config", return_value={}),
            patch("scripts.run_pv.gen_config_to_sdk", return_value=None),
        ):
            exit_code = _verify_realtime(
                manifest=manifest,
                config=config,
                crops_base_dir=crops_dir,
                output_dir=output_dir,
                workers=1,
                iterations=1,
                temperature=None,
                model_override="gemini-3-flash",
                strict=True,
            )

        assert exit_code == 1, "strict-mode gap must exit 1"

        meta = json.load(open(output_dir / "run.meta.json"))
        stats = meta["execution_stats"]
        assert stats["completed_items"] == []
        assert len(stats["failed_items"]) == n_candidates
        for entry in stats["failed_items"]:
            assert entry["item_id"].startswith("candidate_")
            assert "EMPTY_RESPONSE" in entry["reason"]


# ─────────────────────────────────────────────────────────────────────
# Bonus: _write_verification_outputs strict return
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestWriteVerificationOutputsReturnsGap:
    """``_write_verification_outputs`` returns the completeness gap count."""

    def test_returns_zero_when_complete(self, tmp_path: Path) -> None:
        manifest = _make_manifest(3)
        results = {
            f"candidate_{i:05d}": {"mound_probability": 0.5}
            for i in range(3)
        }
        gap = _write_verification_outputs(
            parsed_results=results,
            manifest=manifest,
            config=_make_config(),
            output_dir=tmp_path / "out",
            iterations=1,
            mode="realtime",
            metadata_tracker=_make_tracker(),
            model_name="gemini-3-flash",
            strict=True,
        )
        assert gap == 0

    def test_returns_gap_count(self, tmp_path: Path) -> None:
        manifest = _make_manifest(5)
        results = {
            "candidate_00000": {"mound_probability": 0.5},
            "candidate_00001": {"mound_probability": 0.5},
        }
        tracker = _make_tracker()
        gap = _write_verification_outputs(
            parsed_results=results,
            manifest=manifest,
            config=_make_config(),
            output_dir=tmp_path / "out",
            iterations=1,
            mode="realtime",
            metadata_tracker=tracker,
            model_name="gemini-3-flash",
            strict=True,
        )
        assert gap == 3
        # Confirm completeness_gap summary is in results_summary
        assert "completeness_gap" in tracker.results_summary


# Helper test: _candidate_result_key sanity check
@pytest.mark.tier1
def test_candidate_result_key_single_iter() -> None:
    cand = {"candidate_id": 42}
    assert _candidate_result_key(cand, 1) == "candidate_00042"


@pytest.mark.tier1
def test_candidate_result_key_multi_iter() -> None:
    cand = {"candidate_id": 42}
    # Multi-iter resolves to the first iteration as the canonical proxy
    assert _candidate_result_key(cand, 5) == "candidate_00042_iter1"


# ─────────────────────────────────────────────────────────────────────
# Multi-iteration coverage (audit follow-up: C1 + C2 + C3 regression)
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.tier1
class TestMultiIterationKeyHandling:
    """Multi-iteration runs must surface iter2..iterN gaps end-to-end.

    These tests guard against the regression introduced by the original
    Layer 1 fix, where the resume filter, cleanup missing-set, and
    driver per-attempt logging all collapsed onto an iter1 proxy. The
    centralised ``_candidate_iteration_keys`` helper closes that gap;
    these tests verify each call site.
    """

    def _seed_probabilities(
        self,
        output_dir: Path,
        results: dict[str, dict],
        iterations: int = 3,
    ) -> None:
        """Pre-populate ``probabilities.json`` with a partial result set."""
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "probabilities.json", "w") as f:
            json.dump({
                "version": "1.0",
                "mode": "realtime",
                "verifier_config": "test-v1",
                "iterations": iterations,
                "total_results": len(results),
                "results": results,
            }, f)

    def _run_with_worker(
        self,
        tmp_path: Path,
        manifest: dict,
        worker,
        iterations: int,
        strict: bool = True,
        output_dir: Path | None = None,
    ) -> tuple[int, Path]:
        """Drive ``_verify_realtime`` against a mocked worker."""
        config = _make_config()
        crops_dir = tmp_path / "crops"
        crops_dir.mkdir(exist_ok=True)
        if output_dir is None:
            output_dir = tmp_path / "verified"

        with (
            _patch_get_api_key(),
            _patch_genai_client(),
            _patch_resolve_model_name(),
            patch(
                "scripts.run_pv.verify_candidate_realtime",
                side_effect=worker,
            ),
            patch("scripts.run_pv.load_system_instruction", return_value=""),
            patch("scripts.run_pv.build_reference_items", return_value=[]),
            patch("scripts.run_pv.build_generation_config", return_value={}),
            patch("scripts.run_pv.gen_config_to_sdk", return_value=None),
        ):
            exit_code = _verify_realtime(
                manifest=manifest,
                config=config,
                crops_base_dir=crops_dir,
                output_dir=output_dir,
                workers=1,
                iterations=iterations,
                temperature=None,
                model_override="gemini-3-flash",
                strict=strict,
            )
        return exit_code, output_dir

    def test_multi_iter_resume_complete_state_no_op(
        self, tmp_path: Path,
    ) -> None:
        """Fully-seeded multi-iter state → no worker calls, no gap, exit 0.

        Non-regression sanity check: when every (cid × iter) key is
        already present, the driver must not re-submit any candidate
        and must not surface a completeness gap. This case does NOT
        discriminate the C1 bug (both buggy iter1-only filter and
        fixed full-set filter produce ``worker_calls == []`` for fully
        seeded input); the discriminating case is covered by the
        sibling test ``test_multi_iter_resume_partial_iter_re_attempted``,
        which seeds iter1+iter2 only and asserts the candidate IS
        re-submitted (something the buggy iter1-only filter would not
        do because it considers iter1's presence sufficient).
        """
        manifest = _make_manifest(3)
        iterations = 3
        # Pre-populate every (cid × iter) key so no candidate should be
        # re-submitted by the worker.
        seeded = {
            f"candidate_{cid:05d}_iter{i}": {"mound_probability": 0.5}
            for cid in range(3) for i in range(1, iterations + 1)
        }
        output_dir = tmp_path / "verified"
        self._seed_probabilities(output_dir, seeded, iterations=iterations)

        worker_calls: list[int] = []

        def worker(*, candidate, **kwargs):
            worker_calls.append(candidate["candidate_id"])
            # If the resume filter is correct this branch is unreached.
            return {}, []

        exit_code, _ = self._run_with_worker(
            tmp_path, manifest, worker,
            iterations=iterations, strict=True, output_dir=output_dir,
        )

        assert exit_code == 0, "no gap in seeded results — exit must be 0"
        assert worker_calls == [], (
            "resume filter incorrectly re-submitted complete candidates: "
            f"{worker_calls}"
        )
        meta = json.load(open(output_dir / "run.meta.json"))
        assert meta["execution_stats"]["failed_items"] == []
        assert "completeness_gap" not in meta.get("results_summary", {})

    def test_multi_iter_resume_partial_iter_re_attempted(
        self, tmp_path: Path,
    ) -> None:
        """Partial coverage → candidate is re-submitted; missing iters recovered.

        Regression for C1: when iter1+iter2 exist but iter3 is missing,
        the candidate must be re-submitted (not skipped). The mocked
        worker confirms it received the candidate, and after the run
        every iter key is present.
        """
        manifest = _make_manifest(1)
        iterations = 3
        # Pre-populate iter1 + iter2 only.
        seeded = {
            "candidate_00000_iter1": {"mound_probability": 0.5},
            "candidate_00000_iter2": {"mound_probability": 0.5},
        }
        output_dir = tmp_path / "verified"
        self._seed_probabilities(output_dir, seeded, iterations=iterations)

        worker_calls: list[int] = []

        def worker(*, candidate, **kwargs):
            cid = candidate["candidate_id"]
            worker_calls.append(cid)
            # Worker re-runs *all* iterations idempotently; that is the
            # documented contract of ``verify_candidate_realtime``.
            return (
                {
                    f"candidate_{cid:05d}_iter{i}": {"mound_probability": 0.7}
                    for i in range(1, iterations + 1)
                },
                [
                    _make_response_metadata(f"cand_{cid:04d}_iter{i}")
                    for i in range(1, iterations + 1)
                ],
            )

        exit_code, _ = self._run_with_worker(
            tmp_path, manifest, worker,
            iterations=iterations, strict=True, output_dir=output_dir,
        )

        assert exit_code == 0, "all iters now present — exit must be 0"
        assert worker_calls == [0], (
            "candidate with partial coverage must be re-submitted; "
            f"worker_calls={worker_calls}"
        )
        # All 3 iter keys must be in the persisted probabilities.json.
        probs = json.load(open(output_dir / "probabilities.json"))
        for i in range(1, iterations + 1):
            assert f"candidate_00000_iter{i}" in probs["results"]

    def test_multi_iter_partial_success_logs_per_iter(
        self, tmp_path: Path,
    ) -> None:
        """iter1+iter2 succeed, iter3 fails → per-iter audit trail.

        Regression for C3: ``log_success`` and ``log_failure`` must be
        emitted per *iteration*, not once per candidate using an iter1
        proxy. The audit trail must show iter1+iter2 succeeded and
        iter3 failed with its own ``parse_error`` reason.
        """
        manifest = _make_manifest(1)
        iterations = 3

        def worker(*, candidate, **kwargs):
            cid = candidate["candidate_id"]
            return (
                # iter3 is silently absent (matches the gap=57 cell shape
                # for a single iter rather than the whole candidate).
                {
                    f"candidate_{cid:05d}_iter1": {"mound_probability": 0.5},
                    f"candidate_{cid:05d}_iter2": {"mound_probability": 0.5},
                },
                [
                    _make_response_metadata(f"cand_{cid:04d}_iter1"),
                    _make_response_metadata(f"cand_{cid:04d}_iter2"),
                    _make_response_metadata(
                        f"cand_{cid:04d}_iter3",
                        parse_error="EMPTY_RESPONSE",
                        parse_success=False,
                    ),
                ],
            )

        captured: list[LLMMetadataTracker] = []
        original_init = LLMMetadataTracker.__init__

        def init_spy(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            captured.append(self)

        with patch.object(LLMMetadataTracker, "__init__", init_spy):
            self._run_with_worker(
                tmp_path, manifest, worker,
                iterations=iterations, strict=False,
            )

        tracker = captured[0]
        completed = set(tracker.stats.completed_items)
        failed_ids = {f["item_id"] for f in tracker.stats.failed_items}

        # Per-iteration log_success calls — iter1 + iter2.
        assert "candidate_00000_iter1" in completed
        assert "candidate_00000_iter2" in completed
        # Per-iteration log_failure call — iter3 only.
        assert "candidate_00000_iter3" in failed_ids
        # iter1/iter2 must NOT appear in failed_items.
        assert "candidate_00000_iter1" not in failed_ids
        assert "candidate_00000_iter2" not in failed_ids
        # The failure reason must reflect iter3's parse_error rather
        # than collapsing under a generic candidate-level label.
        match = next(
            f for f in tracker.stats.failed_items
            if f["item_id"] == "candidate_00000_iter3"
        )
        assert "EMPTY_RESPONSE" in match["reason"]

    def test_multi_iter_cleanup_re_attempts_tail_iters(
        self, tmp_path: Path,
    ) -> None:
        """``cmd_cleanup`` must surface and re-attempt iter2..iterN gaps.

        Regression for C2: ``_compute_missing_candidates`` previously
        returned only iter1 gaps for multi-iter runs. After this fix the
        ``missing`` set must include the specific tail-iteration keys
        that are absent.
        """
        manifest = _make_manifest(1)
        iterations = 3
        # Pre-populate iter1 + iter3 (skipping iter2).
        seeded = {
            "candidate_00000_iter1": {"mound_probability": 0.5},
            "candidate_00000_iter3": {"mound_probability": 0.5},
        }
        verified_dir = tmp_path / "verified"
        self._seed_probabilities(
            verified_dir, seeded, iterations=iterations,
        )

        # Direct-test the missing-set helper — this is the call site
        # that ``cmd_cleanup`` consumes.
        missing, _ = _compute_missing_candidates(
            manifest, verified_dir / "probabilities.json", iterations,
        )
        assert missing == {"candidate_00000_iter2"}, (
            "iter2-specific gap must surface; "
            f"got missing={missing}"
        )

        # End-to-end through cmd_cleanup with a stub worker that "fixes"
        # iter2. The stub must receive candidate 0 even though iter1
        # exists — proving the cleanup loop is no longer iter1-only.
        crops_dir = tmp_path / "crops"
        crops_dir.mkdir()
        with open(crops_dir / "candidate_manifest.json", "w") as f:
            json.dump(manifest, f)
        config_path = tmp_path / "verifier.json"
        with open(config_path, "w") as f:
            json.dump(_make_config(), f)

        captured_calls: list[dict] = []

        def fake_verify(*args, **kwargs):
            captured_calls.append(dict(kwargs))
            # Simulate iter2 recovery: write the missing key into
            # probabilities.json so the cleanup loop's post-attempt
            # missing check sees zero gaps.
            probs_path = verified_dir / "probabilities.json"
            probs = json.load(open(probs_path))
            probs["results"]["candidate_00000_iter2"] = {
                "mound_probability": 0.42,
            }
            with open(probs_path, "w") as f:
                json.dump(probs, f)
            return 0

        with patch("scripts.run_pv._verify_realtime", side_effect=fake_verify):
            args = _make_args(
                crops_dir=crops_dir,
                verified_dir=verified_dir,
                verifier_config=config_path,
                iterations=iterations,
                max_attempts=2,
            )
            rc = cmd_cleanup(args)

        assert rc == 0, "cleanup must succeed once iter2 is recovered"
        assert captured_calls, "cmd_cleanup must invoke _verify_realtime"
        # Confirm the residual after recovery is empty.
        post, _ = _compute_missing_candidates(
            manifest, verified_dir / "probabilities.json", iterations,
        )
        assert post == set()

    def test_candidate_iteration_keys_single_pass(self) -> None:
        """The helper returns one key for single-iteration runs."""
        cand = {"candidate_id": 7}
        assert _candidate_iteration_keys(cand, 1) == ["candidate_00007"]

    def test_candidate_iteration_keys_consensus(self) -> None:
        """The helper expands to N keys for consensus runs."""
        cand = {"candidate_id": 7}
        keys = _candidate_iteration_keys(cand, 4)
        assert keys == [
            "candidate_00007_iter1",
            "candidate_00007_iter2",
            "candidate_00007_iter3",
            "candidate_00007_iter4",
        ]

    def test_candidate_iteration_keys_zero_raises(self) -> None:
        """``iterations=0`` must raise rather than silently coerce to 1.

        The CLI parser enforces a positive iteration count, so this
        branch is defensive — a future caller that bypasses the parser
        (e.g. a downstream library wrapper) should fail loud rather
        than receive a single-pass key for what it thinks is a
        zero-iteration request.
        """
        cand = {"candidate_id": 7}
        with pytest.raises(ValueError, match="iterations must be >= 1"):
            _candidate_iteration_keys(cand, 0)

    def test_candidate_iteration_keys_negative_raises(self) -> None:
        """Negative ``iterations`` must also raise."""
        cand = {"candidate_id": 7}
        with pytest.raises(ValueError, match="iterations must be >= 1"):
            _candidate_iteration_keys(cand, -3)


@pytest.mark.tier1
class TestIterationIdToResultKey:
    """Direct unit tests for ``_iteration_id_to_result_key``.

    Coverage was previously incidental via
    ``test_multi_iter_partial_success_logs_per_iter``; this class
    provides a dedicated set of cases for the well-formed-input,
    multi-iter, and malformed-input edge cases. The audit
    (2026-05-03) confirmed by inspection that the parser already
    returns ``None`` on every malformed shape exercised below — these
    tests pin that behaviour as a regression boundary.
    """

    # --- Well-formed inputs -----------------------------------------

    def test_single_iter_collapses_suffix(self) -> None:
        """Single-pass runs strip the ``_iterN`` suffix from the key."""
        assert (
            _iteration_id_to_result_key("cand_0042_iter1", iterations=1)
            == "candidate_00042"
        )

    def test_multi_iter_preserves_iter1_suffix(self) -> None:
        """Multi-iteration runs preserve the ``_iter1`` suffix."""
        assert (
            _iteration_id_to_result_key("cand_0042_iter1", iterations=3)
            == "candidate_00042_iter1"
        )

    def test_multi_iter_preserves_iter3_suffix(self) -> None:
        """Multi-iteration runs preserve arbitrary iter suffixes."""
        assert (
            _iteration_id_to_result_key("cand_0042_iter3", iterations=3)
            == "candidate_00042_iter3"
        )

    # --- Malformed inputs return None -------------------------------

    def test_none_input_returns_none(self) -> None:
        """``iteration_id=None`` must return ``None``."""
        assert _iteration_id_to_result_key(None, iterations=1) is None

    def test_empty_string_returns_none(self) -> None:
        """``iteration_id=""`` must return ``None``."""
        assert _iteration_id_to_result_key("", iterations=1) is None

    def test_two_part_string_returns_none(self) -> None:
        """A string with fewer than three ``_``-segments returns ``None``."""
        assert _iteration_id_to_result_key("foo_bar", iterations=1) is None

    def test_no_iter_suffix_returns_none(self) -> None:
        """Missing the ``_iterN`` segment entirely returns ``None``."""
        assert _iteration_id_to_result_key("cand_42", iterations=1) is None

    def test_non_integer_cid_returns_none(self) -> None:
        """A non-integer candidate-id segment returns ``None``."""
        assert (
            _iteration_id_to_result_key("cand_xx_iter1", iterations=1) is None
        )

    def test_alpha_cid_returns_none(self) -> None:
        """Alphabetic candidate-id (``cand_abc_iter1``) returns ``None``."""
        assert (
            _iteration_id_to_result_key("cand_abc_iter1", iterations=1)
            is None
        )

    def test_third_segment_missing_iter_prefix_returns_none(self) -> None:
        """Third segment lacking the ``iter`` prefix returns ``None``."""
        assert (
            _iteration_id_to_result_key("cand_42_blah1", iterations=1)
            is None
        )

    def test_iter_segment_without_integer_returns_none(self) -> None:
        """``cand_42_iter`` (no integer suffix) returns ``None``."""
        assert (
            _iteration_id_to_result_key("cand_42_iter", iterations=1) is None
        )
