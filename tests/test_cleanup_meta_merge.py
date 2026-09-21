"""
Tier-1 tests for the cleanup metadata merge and its configuration gate.

Guards the fix recorded in ``reports/cleanup-meta-fix-2026-09-14.md``:
``run_pv.py cleanup`` used to write ``run.meta.json`` with the retry pass's
``usage_stats`` and ``execution_stats`` only, replacing the main pass's. The
fourth cell's verifier stage
(``outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/verify_37``)
records ``items_processed: 29`` against a 57,482-candidate load because of
it, and with no backup taken that load is unrecoverable from metadata
(``reports/r7-gaps-deltas-2026-09-11.md`` section 2.5).

Test groups:

1. **Merge arithmetic** — usage, execution counts and cost sum across the
   main pass and every cleanup pass.
2. **Preservation** — ``main_pass`` verbatim, indexed sidecars never
   overwritten, a second cleanup extending rather than rewriting.
3. **Regression** — a stage that never sees a second pass is written
   exactly as it was before the merge machinery existed.
4. **The configuration gate** — refusal, the ``--allow-config-change``
   override, the resolved-model tolerance, and that a refusal happens
   before any API call.

No API calls are made.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib_llm_metadata import (  # noqa: E402
    PASS_MERGE_SCHEMA,
    LLMMetadataTracker,
    merge_cleanup_meta,
    next_pass_sidecar_path,
    write_merged_pass_meta,
)
from scripts.run_pv import (  # noqa: E402
    _cleanup_configuration_gate,
    _save_probabilities_incremental,
    _write_verification_outputs,
    cmd_cleanup,
)

pytestmark = pytest.mark.tier1


# ─────────────────────────────────────────────────────────────────────
# Fixture builders
# ─────────────────────────────────────────────────────────────────────


def _make_meta(
    *,
    run_id: str = "main-run",
    items_processed: int = 6972,
    items_failed: int = 13,
    input_tokens: int = 20_000_000,
    output_tokens: int = 500_000,
    thoughts_tokens: int = 100_000,
    cost_usd: float = 15.375,
    model: str = "gemini-3.7-flash",
    thinking_level: str = "low",
    max_output_tokens: int = 8192,
    instruction_hash: str = "a" * 64,
) -> dict[str, Any]:
    """Build a finalised-meta-shaped dict for merge arithmetic tests."""
    return {
        "run_id": run_id,
        "timestamp": {
            "start": "2026-09-13T15:20:00+00:00",
            "end": "2026-09-13T18:37:00+00:00",
            "duration_seconds": 11820.0,
        },
        "environment": {"git_commit": "deadbeef", "script": "run_pv.py"},
        "configuration": {
            "version": "verify-adversarial-text-v1",
            "model": model,
            "instruction_file": "verify_adversarial-text.md",
            "system_instruction_hash": instruction_hash,
            "system_instruction_text": "irrelevant to the fingerprint",
            "library_hash": "no_examples",
            "temperature": 0.0,
            "max_output_tokens": max_output_tokens,
            "thinking_level": thinking_level,
            "full_config_snapshot": {"version": "verify-adversarial-text-v1"},
        },
        "execution_stats": {
            "items_processed": items_processed,
            "items_failed": items_failed,
            "items_skipped": 0,
            "retries_total": 12_247,
            "completed_items": [f"candidate_{i:05d}" for i in range(3)],
            "failed_items": [
                {"item_id": "candidate_01460", "reason": "503"},
            ],
            "finish_reason_counts": {"STOP": items_processed},
        },
        "usage_stats": {
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens,
            "total_thoughts_tokens": thoughts_tokens,
            "total_cached_tokens": 0,
            "total_requests": items_processed,
        },
        "cost_estimate": {
            "input_cost_usd": cost_usd * 0.8,
            "output_cost_usd": cost_usd * 0.2,
            "total_cost_usd": cost_usd,
            "pricing_used": {"input_per_1m": 0.75, "output_per_1m": 3.75},
        },
    }


def _make_cleanup_meta(**overrides: Any) -> dict[str, Any]:
    """Build a small cleanup-pass meta (13 candidates recovered)."""
    defaults: dict[str, Any] = {
        "run_id": "cleanup-run-1",
        "items_processed": 13,
        "items_failed": 0,
        "input_tokens": 40_000,
        "output_tokens": 1_000,
        "thoughts_tokens": 200,
        "cost_usd": 0.0306,
    }
    defaults.update(overrides)
    meta = _make_meta(**defaults)
    meta["timestamp"] = {
        "start": "2026-09-13T23:02:00+00:00",
        "end": "2026-09-13T23:02:45+00:00",
        "duration_seconds": 45.0,
    }
    meta["execution_stats"]["failed_items"] = []
    meta["execution_stats"]["completed_items"] = ["candidate_01460"]
    return meta


def _make_config(
    version: str = "verify-adversarial-text-v1",
    model: str = "gemini-3.7-flash",
    thinking_level: str = "low",
    max_output_tokens: int = 8192,
) -> dict[str, Any]:
    """Build a verifier config dict matching :func:`_make_meta`."""
    return {
        "version": version,
        "model": model,
        "temperature": 0.0,
        "max_output_tokens": max_output_tokens,
        "thinking_level": thinking_level,
        "instruction_file": "verify_adversarial-text.md",
    }


def _stage_with_main_meta(
    tmp_path: Path, meta: dict[str, Any] | None = None,
) -> Path:
    """Create a verifier stage directory holding a main-pass meta."""
    stage = tmp_path / "verify_k1_arm2"
    stage.mkdir(parents=True, exist_ok=True)
    with open(stage / "run.meta.json", "w") as f:
        json.dump(meta or _make_meta(), f, indent=2)
    return stage


def _tracker(config: dict[str, Any] | None = None) -> LLMMetadataTracker:
    """Build a tracker whose ``configuration`` block matches _make_config."""
    return LLMMetadataTracker(
        config=config or _make_config(),
        system_instruction="verifier instruction text",
        script_name="run_pv.py",
        script_version="1.0.0",
        model_override="gemini-3.7-flash",
    )


def _cleanup_args(**kwargs: Any) -> argparse.Namespace:
    """Namespace mimicking parsed ``cleanup`` CLI arguments."""
    defaults: dict[str, Any] = {
        "crops_dir": None,
        "verified_dir": None,
        "verifier_config": None,
        "service_tier": "flex",
        "workers": 5,
        "iterations": 1,
        "temperature": None,
        "model": None,
        "thinking_level": None,
        "max_attempts": 1,
        "safe_mode_tokens": None,
        "allow_config_change": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ─────────────────────────────────────────────────────────────────────
# 1. Merge arithmetic
# ─────────────────────────────────────────────────────────────────────


class TestMergeArithmetic:
    """The merged meta's totals span the main pass and every cleanup."""

    def test_usage_is_summed(self) -> None:
        """Token counts sum; neither pass's load is lost."""
        merged = merge_cleanup_meta(_make_meta(), _make_cleanup_meta())
        usage = merged["usage_stats"]
        assert usage["total_input_tokens"] == 20_000_000 + 40_000
        assert usage["total_output_tokens"] == 500_000 + 1_000
        assert usage["total_thoughts_tokens"] == 100_000 + 200

    def test_execution_counts_are_summed(self) -> None:
        """``items_processed`` is the main pass plus the cleanup."""
        merged = merge_cleanup_meta(_make_meta(), _make_cleanup_meta())
        assert merged["execution_stats"]["items_processed"] == 6972 + 13
        # The residual failure set is the cleanup's, not the main pass's.
        assert merged["execution_stats"]["items_failed"] == 0

    def test_cost_estimate_is_summed(self) -> None:
        """The stage's recorded cost is the sum of both passes."""
        merged = merge_cleanup_meta(_make_meta(), _make_cleanup_meta())
        assert merged["cost_estimate"]["total_cost_usd"] == pytest.approx(
            15.375 + 0.0306,
        )

    def test_cleanup_pass_entry_records_its_own_usage(self) -> None:
        """Each entry carries the pass's own block, not the running total."""
        merged = merge_cleanup_meta(_make_meta(), _make_cleanup_meta())
        assert merged["meta_merge_schema"] == PASS_MERGE_SCHEMA
        entries = merged["cleanup_passes"]
        assert len(entries) == 1
        entry = entries[0]
        assert entry["pass_index"] == 1
        assert entry["kind"] == "cleanup"
        assert entry["candidates_verified"] == 13
        assert entry["candidates_failed"] == 0
        assert entry["candidates_attempted"] == 13
        assert entry["usage_stats"]["total_input_tokens"] == 40_000
        assert entry["cost_estimate"]["total_cost_usd"] == pytest.approx(0.0306)
        assert entry["configuration_differs_from_main_pass"] is False

    def test_pass_record_fields_are_recorded(self) -> None:
        """Caller evidence lands on the entry."""
        merged = merge_cleanup_meta(
            _make_meta(),
            _make_cleanup_meta(),
            pass_record={"verifier_config_sha256": "b" * 64},
        )
        assert (
            merged["cleanup_passes"][0]["verifier_config_sha256"] == "b" * 64
        )

    def test_configuration_difference_is_flagged_on_the_entry(self) -> None:
        """A cleanup under a changed ceiling says so on its own entry."""
        merged = merge_cleanup_meta(
            _make_meta(),
            _make_cleanup_meta(max_output_tokens=2048),
        )
        entry = merged["cleanup_passes"][0]
        assert entry["configuration_differs_from_main_pass"] is True
        assert "max_output_tokens" in entry["changed_configuration_fields"]


# ─────────────────────────────────────────────────────────────────────
# 2. Preservation
# ─────────────────────────────────────────────────────────────────────


class TestPreservation:
    """The main pass survives verbatim, on disc and in the meta."""

    def test_main_pass_block_is_verbatim(self) -> None:
        """``main_pass`` holds the original numbers, unsummed."""
        main = _make_meta()
        merged = merge_cleanup_meta(main, _make_cleanup_meta())
        block = merged["main_pass"]
        assert block["run_id"] == "main-run"
        assert block["execution_stats"]["items_processed"] == 6972
        assert block["usage_stats"]["total_input_tokens"] == 20_000_000
        assert block["cost_estimate"]["total_cost_usd"] == 15.375
        # The instruction text is dropped from the fingerprint; its hash
        # is what identifies the configuration.
        assert "system_instruction_text" not in block["configuration"]

    def test_second_cleanup_extends_without_rewriting_main_pass(self) -> None:
        """A second cleanup adds an entry and keeps the first pass intact."""
        once = merge_cleanup_meta(_make_meta(), _make_cleanup_meta())
        twice = merge_cleanup_meta(
            once,
            _make_cleanup_meta(
                run_id="cleanup-run-2",
                items_processed=2,
                input_tokens=5_000,
                output_tokens=100,
                thoughts_tokens=10,
                cost_usd=0.004,
            ),
        )
        assert twice["main_pass"] == once["main_pass"]
        assert [e["pass_index"] for e in twice["cleanup_passes"]] == [1, 2]
        assert twice["usage_stats"]["total_input_tokens"] == (
            20_000_000 + 40_000 + 5_000
        )
        assert twice["execution_stats"]["items_processed"] == 6972 + 13 + 2
        assert twice["cost_estimate"]["total_cost_usd"] == pytest.approx(
            15.375 + 0.0306 + 0.004,
        )

    def test_sidecar_index_advances_and_never_overwrites(
        self, tmp_path: Path,
    ) -> None:
        """Every pre-merge state survives under its own index."""
        stage = _stage_with_main_meta(tmp_path)
        meta_path = stage / "run.meta.json"
        original_bytes = meta_path.read_bytes()

        merged, sidecar_1 = write_merged_pass_meta(
            meta_path, _make_cleanup_meta(), kind="cleanup",
        )
        assert sidecar_1 is not None
        assert sidecar_1.name == "run.meta.pre-cleanup-1.json"
        assert sidecar_1.read_bytes() == original_bytes
        with open(meta_path, "w") as f:
            json.dump(merged, f, indent=2)

        _, sidecar_2 = write_merged_pass_meta(
            meta_path, _make_cleanup_meta(run_id="cleanup-run-2"),
            kind="cleanup",
        )
        assert sidecar_2 is not None
        assert sidecar_2.name == "run.meta.pre-cleanup-2.json"
        # The first sidecar is untouched by the second merge.
        assert sidecar_1.read_bytes() == original_bytes
        assert (
            json.loads(sidecar_2.read_text())["execution_stats"][
                "items_processed"
            ]
            == 6972 + 13
        )
        assert (
            merged["cleanup_passes"][0]["previous_meta_sidecar"]
            == "run.meta.pre-cleanup-1.json"
        )

    def test_sidecar_name_derives_from_the_meta_stem(
        self, tmp_path: Path,
    ) -> None:
        """The helper works for any ``*.meta.json``, not only run.meta."""
        path = tmp_path / "detections_x.meta.json"
        assert (
            next_pass_sidecar_path(path, "resume").name
            == "detections_x.meta.pre-resume-1.json"
        )

    def test_absent_meta_returns_fresh_unchanged(
        self, tmp_path: Path,
    ) -> None:
        """A first pass is not touched by the merge machinery."""
        fresh = _make_meta()
        returned, sidecar = write_merged_pass_meta(
            tmp_path / "run.meta.json", fresh, kind="cleanup",
        )
        assert returned is fresh
        assert sidecar is None
        assert "main_pass" not in returned

    def test_rerun_preserves_without_summing(self, tmp_path: Path) -> None:
        """A whole-set rerun keeps a sidecar but does not double-count."""
        stage = _stage_with_main_meta(tmp_path)
        fresh = _make_meta(run_id="second-batch-pass")
        returned, sidecar = write_merged_pass_meta(
            stage / "run.meta.json",
            fresh,
            kind="rerun",
            merge_previous=False,
        )
        assert sidecar is not None
        assert sidecar.name == "run.meta.pre-rerun-1.json"
        assert returned is fresh
        assert "cleanup_passes" not in returned


# ─────────────────────────────────────────────────────────────────────
# 3. Regression — a stage with no cleanup is unchanged
# ─────────────────────────────────────────────────────────────────────


class TestNoCleanupRegression:
    """A stage that never sees a second pass is written as before."""

    def test_single_pass_meta_has_no_merge_blocks(
        self, tmp_path: Path,
    ) -> None:
        """No ``main_pass``, no ``cleanup_passes``, no sidecar, indent=2.

        Byte identity is asserted structurally: the file's key set is the
        finalised tracker's plus ``cost_estimate``, its formatting is
        ``json.dumps(..., indent=2)`` with no trailing newline, and no
        sidecar exists. The timestamp block's ``end``/``duration_seconds``
        are recomputed on each ``finalise()``, so an exact byte comparison
        against a second finalise would fail on those two fields alone.
        """
        stage = tmp_path / "verified"
        tracker = _tracker()
        _write_verification_outputs(
            parsed_results={"candidate_00000": {"mound_probability": 0.7}},
            manifest={"candidates": [{"candidate_id": 0}]},
            config=_make_config(),
            output_dir=stage,
            iterations=1,
            mode="realtime",
            metadata_tracker=tracker,
            model_name="gemini-3.7-flash",
            strict=False,
        )
        raw = (stage / "run.meta.json").read_text()
        written = json.loads(raw)

        for key in ("main_pass", "cleanup_passes", "meta_merge_schema"):
            assert key not in written
        expected_keys = set(tracker.finalise(include_per_item=False)) | {
            "cost_estimate",
            "billing",  # the tier the leg ran at, recorded since 2026-09-21
        }
        assert set(written) == expected_keys
        assert raw == json.dumps(written, indent=2)
        assert not list(stage.glob("run.meta.pre-*.json"))
        assert not list(stage.glob("*.tmp"))

    def test_cleanup_pass_merges_into_the_stage_meta(
        self, tmp_path: Path,
    ) -> None:
        """Two writes into one stage give summed totals and a sidecar."""
        stage = tmp_path / "verified"
        common = {
            "manifest": {"candidates": [{"candidate_id": 0}]},
            "config": _make_config(),
            "output_dir": stage,
            "iterations": 1,
            "mode": "realtime",
            "model_name": "gemini-3.7-flash",
            "strict": False,
        }
        main_tracker = _tracker()
        main_tracker.stats.items_processed = 500
        main_tracker.usage.total_input_tokens = 1_000_000
        _write_verification_outputs(
            parsed_results={"candidate_00000": {"mound_probability": 0.7}},
            metadata_tracker=main_tracker,
            **common,
        )
        cleanup_tracker = _tracker()
        cleanup_tracker.stats.items_processed = 3
        cleanup_tracker.usage.total_input_tokens = 6_000
        _write_verification_outputs(
            parsed_results={"candidate_00000": {"mound_probability": 0.7}},
            metadata_tracker=cleanup_tracker,
            pass_kind="cleanup",
            pass_record={"cleanup_attempt": 1},
            **common,
        )
        written = json.loads((stage / "run.meta.json").read_text())
        assert written["execution_stats"]["items_processed"] == 503
        assert written["usage_stats"]["total_input_tokens"] == 1_006_000
        assert written["main_pass"]["execution_stats"]["items_processed"] == 500
        assert len(written["cleanup_passes"]) == 1
        assert written["cleanup_passes"][0]["cleanup_attempt"] == 1
        assert (stage / "run.meta.pre-cleanup-1.json").exists()


class TestCleanupHistoryCarry:
    """``cleanup_history`` in ``probabilities.json`` survives a later pass.

    Both writers of the results file rebuild it from scratch, so a resume
    used to erase the record of every cleanup the stage had had. The fourth
    cell's stage holds a 29-item meta and no history left to explain it,
    which is why that overwrite cannot even be attributed to a subcommand.
    """

    def _write(
        self,
        stage: Path,
        *,
        pass_kind: str = "resume",
    ) -> dict[str, Any]:
        """Write verification outputs into *stage* and return the results file."""
        _write_verification_outputs(
            parsed_results={"candidate_00000": {"mound_probability": 0.7}},
            manifest={"candidates": [{"candidate_id": 0}]},
            config=_make_config(),
            output_dir=stage,
            iterations=1,
            mode="realtime",
            metadata_tracker=None,
            model_name="gemini-3.7-flash",
            strict=False,
            pass_kind=pass_kind,
        )
        return json.loads((stage / "probabilities.json").read_text())

    def test_history_is_carried_forward(self, tmp_path: Path) -> None:
        """A pass over a stage with history preserves every entry."""
        stage = tmp_path / "verified"
        self._write(stage)
        probs = json.loads((stage / "probabilities.json").read_text())
        probs["cleanup_history"] = [
            {"initial_missing": 13, "recovered": 13, "still_missing": 0},
        ]
        with open(stage / "probabilities.json", "w") as f:
            json.dump(probs, f)

        rewritten = self._write(stage, pass_kind="cleanup")
        assert rewritten["cleanup_history"] == probs["cleanup_history"]

    def test_no_history_key_is_added_when_there_is_none(
        self, tmp_path: Path,
    ) -> None:
        """A first pass's results file keeps its original key set."""
        probs = self._write(tmp_path / "verified")
        assert "cleanup_history" not in probs
        assert list(probs) == [
            "version",
            "mode",
            "verifier_config",
            "iterations",
            "total_results",
            "results",
        ]

    def test_incremental_save_also_carries_history(
        self, tmp_path: Path,
    ) -> None:
        """The mid-pass writer must not erase it either."""
        stage = tmp_path / "verified"
        stage.mkdir()
        history = [{"initial_missing": 2, "recovered": 2}]
        with open(stage / "probabilities.json", "w") as f:
            json.dump({"results": {}, "cleanup_history": history}, f)
        _save_probabilities_incremental(
            {"candidate_00000": {"mound_probability": 0.1}},
            stage,
            "verify-adversarial-text-v1",
            "realtime",
            1,
        )
        probs = json.loads((stage / "probabilities.json").read_text())
        assert probs["cleanup_history"] == history


# ─────────────────────────────────────────────────────────────────────
# 5. The configuration gate
# ─────────────────────────────────────────────────────────────────────


class TestConfigurationGate:
    """A cleanup under a changed configuration is refused by default."""

    def _gate(
        self,
        tmp_path: Path,
        *,
        config: dict[str, Any] | None = None,
        allow: bool = False,
        model_override: str | None = "gemini-3.7-flash",
        meta: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Run the gate against a stage whose main pass is _make_meta()."""
        stage = _stage_with_main_meta(tmp_path, meta)
        config_path = tmp_path / "verify_adversarial-text.json"
        with open(config_path, "w") as f:
            json.dump(config or _make_config(), f)
        return _cleanup_configuration_gate(
            verified_dir=stage,
            config_path=config_path,
            effective_config=config or _make_config(),
            model_override=model_override,
            cli_overrides={"model": model_override},
            allow_config_change=allow,
        )

    def test_identical_configuration_passes(self, tmp_path: Path) -> None:
        """The campaign's byte-identical cleanup is allowed through."""
        main = _make_meta(instruction_hash=_instruction_hash())
        may_run, record = self._gate(tmp_path, meta=main)
        assert may_run is True
        assert record["configuration_gate"] == "matches-main-pass"
        assert record["configuration_differences"] == {}
        assert record["verifier_config_sha256"]

    def test_changed_thinking_level_is_refused(self, tmp_path: Path) -> None:
        """The parameter-control rule, enforced before any API call."""
        main = _make_meta(instruction_hash=_instruction_hash())
        may_run, record = self._gate(
            tmp_path,
            config=_make_config(thinking_level="high"),
            meta=main,
        )
        assert may_run is False
        assert record["configuration_gate"] == "differs-refused"
        assert "thinking_level" in record["configuration_differences"]
        assert record["configuration_differences"]["thinking_level"] == {
            "main_pass": "low",
            "this_pass": "high",
        }

    def test_safe_mode_ceiling_is_a_configuration_change(
        self, tmp_path: Path,
    ) -> None:
        """``--safe-mode-tokens`` lowers the ceiling, so the gate sees it."""
        main = _make_meta(instruction_hash=_instruction_hash())
        may_run, record = self._gate(
            tmp_path,
            config=_make_config(max_output_tokens=2048),
            meta=main,
        )
        assert may_run is False
        assert "max_output_tokens" in record["configuration_differences"]

    def test_override_allows_and_records(self, tmp_path: Path) -> None:
        """``--allow-config-change`` warns, proceeds, and leaves a record."""
        main = _make_meta(instruction_hash=_instruction_hash())
        may_run, record = self._gate(
            tmp_path,
            config=_make_config(thinking_level="high"),
            allow=True,
            meta=main,
        )
        assert may_run is True
        assert record["configuration_gate"] == "differs-allowed"
        assert record["configuration_change_allowed"] is True
        assert "thinking_level" in record["configuration_differences"]

    def test_resolved_preview_model_is_not_a_change(
        self, tmp_path: Path,
    ) -> None:
        """A meta records the resolved name; the operator types the short one."""
        main = _make_meta(
            model="gemini-3-flash-preview",
            instruction_hash=_instruction_hash(),
        )
        may_run, record = self._gate(
            tmp_path,
            config=_make_config(model="gemini-3-flash"),
            model_override="gemini-3-flash",
            meta=main,
        )
        assert may_run is True
        assert "model" not in record["configuration_differences"]

    def test_missing_meta_does_not_block(self, tmp_path: Path) -> None:
        """A legacy stage with no meta cannot be held to a comparison."""
        stage = tmp_path / "verified"
        stage.mkdir()
        config_path = tmp_path / "cfg.json"
        with open(config_path, "w") as f:
            json.dump(_make_config(), f)
        may_run, record = _cleanup_configuration_gate(
            verified_dir=stage,
            config_path=config_path,
            effective_config=_make_config(),
            model_override=None,
            cli_overrides={},
            allow_config_change=False,
        )
        assert may_run is True
        assert record["configuration_gate"] == "no-previous-meta"

    def test_cmd_cleanup_refuses_before_any_api_call(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The refusal short-circuits ``_verify_realtime`` entirely."""
        crops_dir = tmp_path / "crops"
        crops_dir.mkdir()
        with open(crops_dir / "candidate_manifest.json", "w") as f:
            json.dump({"candidates": [{"candidate_id": i} for i in range(5)]}, f)

        stage = _stage_with_main_meta(
            tmp_path, _make_meta(instruction_hash=_instruction_hash()),
        )
        with open(stage / "probabilities.json", "w") as f:
            json.dump(
                {"results": {"candidate_00000": {"mound_probability": 0.4}}}, f,
            )

        config_path = tmp_path / "cfg.json"
        with open(config_path, "w") as f:
            json.dump(_make_config(thinking_level="high"), f)

        calls: list[str] = []

        def _fail(*args: Any, **kwargs: Any) -> int:
            calls.append("called")
            raise AssertionError("cleanup must not reach the API")

        monkeypatch.setattr("scripts.run_pv._verify_realtime", _fail)

        exit_code = cmd_cleanup(
            _cleanup_args(
                crops_dir=crops_dir,
                verified_dir=stage,
                verifier_config=config_path,
            ),
        )
        assert exit_code == 1
        assert calls == []
        # Nothing was backed up or rewritten by the refused run.
        assert not list(stage.glob("*.backup"))
        assert not list(stage.glob("run.meta.pre-*.json"))


def _instruction_hash() -> str:
    """SHA-256 of the instruction text :func:`_tracker` records.

    The gate builds its candidate fingerprint through a real
    ``LLMMetadataTracker``, which hashes the instruction text it is given.
    ``_cleanup_configuration_gate`` loads that text from the config's
    ``instruction_file``, which does not exist under ``tmp_path``, so the
    text is the empty string — and the main pass's recorded hash must
    match it for the "identical configuration" cases to be identical.
    """
    import hashlib

    return hashlib.sha256(b"").hexdigest()
