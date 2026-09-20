"""Booking guards on the batch finisher (audit finding M2, 2026-09-20).

``run_pv.py batch-recover`` rebuilt a leg's expected-key set from an
``--iterations`` flag that defaulted to 1. On a K = 5 consensus leg those
keys carry an ``_iter{i}`` suffix, so an unsuffixed set matched nothing:
``validate_batch_results`` returned no rows, and the finisher wrote
``probabilities.json`` with ``"total_results": 0`` anyway. ``consensus.json``
was rewritten only at K > 1 and was never backed up, so the leg was left
with a **stale** K = 5 consensus beside a **zeroed** probabilities file.

These tests pin both halves of the PI's ruling:

(a) ``--iterations`` defaults from the leg's own ``probabilities.json``,
    an explicit flag still wins, and the fallback to 1 announces itself.
(b) A leg in which *every* expected key missed is refused rather than
    booked — no write, no rewrite, no backup, exit 1 — for both callers of
    the finisher, and both files are copied aside before any rewrite that
    does go ahead.

Everything runs against fakes: no API client, no network, no spend.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib_llm_metadata import LLMMetadataTracker  # noqa: E402
from scripts.run_pv import (  # noqa: E402
    _finish_batch_outputs,
    _resolve_recover_iterations,
    _verify_batch,
    cmd_batch_recover,
)

pytestmark = pytest.mark.tier1


# ─────────────────────────────────────────────────────────────────────
# Fakes and fixtures
# ─────────────────────────────────────────────────────────────────────


def _config() -> dict:
    """The minimal verifier config the finisher reads."""
    return {
        "version": "test-v1",
        "model": "gemini-3-flash",
        "temperature": 0.0,
        "max_output_tokens": 8192,
        "instruction_file": "test.md",
    }


def _manifest(n: int) -> dict:
    """A manifest of *n* candidates, ids 1..n."""
    return {
        "version": "1.0",
        "candidates": [{"candidate_id": i, "crop_path": f"c{i}.png"}
                       for i in range(1, n + 1)],
    }


def _tracker() -> LLMMetadataTracker:
    """A fresh metadata tracker, as the batch paths build one."""
    return LLMMetadataTracker(
        config=_config(),
        system_instruction="test instruction",
        script_name="test",
        script_version="0.0.0",
        model_override="gemini-3-flash",
    )


def _row(key: str, prob: float = 0.8) -> dict:
    """One retrieved Batch API row, shaped as ``retrieve_batch_results``."""
    text = json.dumps({"mound_probability": prob, "reasoning": "r"})
    return {
        "key": key,
        "response": {
            "candidates": [
                {"content": {"parts": [{"text": text}]}},
            ],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 5,
                "totalTokenCount": 15,
            },
        },
    }


def _consensus_rows(n_candidates: int, iterations: int) -> list[dict]:
    """Every ``candidate_XXXXX_iterI`` row a K > 1 leg returns."""
    return [
        _row(f"candidate_{cid:05d}_iter{i}")
        for cid in range(1, n_candidates + 1)
        for i in range(1, iterations + 1)
    ]


def _seed_leg(leg: Path, *, n_candidates: int, iterations: int) -> None:
    """Write the ``probabilities.json`` / ``consensus.json`` a K > 1 leg has.

    These stand for the good output an ill-formed recovery would overwrite.
    """
    leg.mkdir(parents=True, exist_ok=True)
    (leg / "probabilities.json").write_text(json.dumps({
        "version": "1.0",
        "mode": "batch",
        "verifier_config": "test-v1",
        "iterations": iterations,
        "total_results": n_candidates * iterations,
        "results": {
            f"candidate_{cid:05d}_iter{i}": {"mound_probability": 0.8}
            for cid in range(1, n_candidates + 1)
            for i in range(1, iterations + 1)
        },
    }))
    (leg / "consensus.json").write_text(json.dumps({
        "version": "1.0",
        "mode": "batch",
        "iterations": iterations,
        "total_candidates": n_candidates,
        "consensus": {str(cid): {"vote_count": iterations}
                      for cid in range(1, n_candidates + 1)},
    }))


def _backups(leg: Path) -> list[str]:
    """Every backup copy the finisher has taken in *leg*, by name."""
    return sorted(p.name for p in leg.glob("*.backup"))


# ─────────────────────────────────────────────────────────────────────
# (a) --iterations defaults from the leg's own probabilities.json
# ─────────────────────────────────────────────────────────────────────


def test_an_explicit_iterations_flag_wins_over_the_recorded_value(tmp_path):
    """The operator may be recovering a leg whose own file is wrong."""
    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)
    assert _resolve_recover_iterations(leg, 3) == 3


def test_iterations_defaults_from_the_legs_probabilities_file(tmp_path):
    """The K = 5 leg recovers as K = 5 without the operator remembering."""
    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)
    assert _resolve_recover_iterations(leg, None) == 5


def test_no_flag_and_no_file_falls_back_to_one_and_says_so(tmp_path, caplog):
    """The fallback is the old default; it must announce itself."""
    leg = tmp_path / "leg"
    leg.mkdir()
    with caplog.at_level(logging.WARNING):
        assert _resolve_recover_iterations(leg, None) == 1
    warnings = "\n".join(r.getMessage() for r in caplog.records
                         if r.levelno >= logging.WARNING)
    assert "--iterations" in warnings


def test_an_unreadable_probabilities_file_falls_back_rather_than_raising(
    tmp_path, caplog,
):
    """A truncated file is exactly what a leg that died mid-write leaves."""
    leg = tmp_path / "leg"
    leg.mkdir()
    (leg / "probabilities.json").write_text('{"iterations": 5')  # truncated
    with caplog.at_level(logging.WARNING):
        assert _resolve_recover_iterations(leg, None) == 1
    assert any(r.levelno >= logging.WARNING for r in caplog.records)


def test_a_file_recording_no_iterations_falls_back(tmp_path):
    """Older probabilities files predate the field."""
    leg = tmp_path / "leg"
    leg.mkdir()
    (leg / "probabilities.json").write_text(json.dumps({"results": {}}))
    assert _resolve_recover_iterations(leg, None) == 1


# ─────────────────────────────────────────────────────────────────────
# (b) The refusal gate
# ─────────────────────────────────────────────────────────────────────


def test_a_wholly_missed_key_shape_is_refused_not_booked(tmp_path, caplog):
    """The M2 shape itself: K = 5 rows re-booked as K = 1.

    Nothing may be written — the pre-existing probabilities and consensus
    must survive byte for byte — and the exit code must be non-zero.
    """
    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)
    before_prob = (leg / "probabilities.json").read_bytes()
    before_cons = (leg / "consensus.json").read_bytes()

    with caplog.at_level(logging.ERROR):
        rc = _finish_batch_outputs(
            manifest=_manifest(2), config=_config(), output_dir=leg,
            iterations=1, raw_results=_consensus_rows(2, 5),
            batch_metadata=_tracker(), model_name="gemini-3-flash",
            strict=True, backup_tag="recover",
        )

    assert rc == 1
    assert (leg / "probabilities.json").read_bytes() == before_prob
    assert (leg / "consensus.json").read_bytes() == before_cons
    assert _backups(leg) == []


def test_the_refusal_names_the_expected_shape_and_the_keys_seen(
    tmp_path, caplog,
):
    """The operator must be able to read the fix off the error line."""
    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)

    with caplog.at_level(logging.ERROR):
        _finish_batch_outputs(
            manifest=_manifest(2), config=_config(), output_dir=leg,
            iterations=1, raw_results=_consensus_rows(2, 5),
            batch_metadata=_tracker(), model_name="gemini-3-flash",
            strict=True,
        )

    errors = "\n".join(r.getMessage() for r in caplog.records
                       if r.levelno >= logging.ERROR)
    assert "candidate_00001" in errors          # the expected-key shape
    assert "_iter" in errors                     # the suffix that is missing
    assert "candidate_00001_iter1" in errors     # a key actually returned


def test_an_empty_result_set_is_refused_too(tmp_path):
    """Every chunk lost is the other route to a zeroed probabilities file."""
    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)
    before = (leg / "probabilities.json").read_bytes()

    rc = _finish_batch_outputs(
        manifest=_manifest(2), config=_config(), output_dir=leg,
        iterations=5, raw_results=[], batch_metadata=_tracker(),
        model_name="gemini-3-flash", strict=True,
    )

    assert rc == 1
    assert (leg / "probabilities.json").read_bytes() == before
    assert _backups(leg) == []


def test_the_right_shape_books_and_rewrites_both_files(tmp_path):
    """The gate must not stand in the way of a correct recovery."""
    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)

    rc = _finish_batch_outputs(
        manifest=_manifest(2), config=_config(), output_dir=leg,
        iterations=5, raw_results=_consensus_rows(2, 5),
        batch_metadata=_tracker(), model_name="gemini-3-flash",
        strict=True, backup_tag="recover",
    )

    assert rc == 0
    written = json.loads((leg / "probabilities.json").read_text())
    assert written["total_results"] == 10
    assert written["iterations"] == 5


def test_a_partial_miss_still_books(tmp_path):
    """Genuine losses are the completeness assertion's business, not the gate's.

    Half the rows present is a real, reportable gap — but the keys line up,
    so the leg is booked and the gap surfaces the way it always has.
    """
    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=4, iterations=1)
    rows = [_row(f"candidate_{cid:05d}") for cid in (1, 2)]

    rc = _finish_batch_outputs(
        manifest=_manifest(4), config=_config(), output_dir=leg,
        iterations=1, raw_results=rows, batch_metadata=_tracker(),
        model_name="gemini-3-flash", strict=True,
    )

    # strict mode, two of four missing: exit 1, but the leg WAS booked.
    assert rc == 1
    written = json.loads((leg / "probabilities.json").read_text())
    assert written["total_results"] == 2


# ─────────────────────────────────────────────────────────────────────
# (b, cont.) consensus.json is backed up the way probabilities.json is
# ─────────────────────────────────────────────────────────────────────


def test_consensus_is_copied_aside_before_it_is_rewritten(tmp_path):
    """M2's silent half: a stale consensus had nothing to restore it from."""
    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)
    stale_consensus = (leg / "consensus.json").read_bytes()

    _finish_batch_outputs(
        manifest=_manifest(2), config=_config(), output_dir=leg,
        iterations=5, raw_results=_consensus_rows(2, 5),
        batch_metadata=_tracker(), model_name="gemini-3-flash",
        strict=True, backup_tag="recover",
    )

    backups = _backups(leg)
    assert len(backups) == 2
    assert any(b.startswith("probabilities.json.pre-recover-") for b in backups)
    consensus_backup = next(
        b for b in backups if b.startswith("consensus.json.pre-recover-")
    )
    assert (leg / consensus_backup).read_bytes() == stale_consensus


def test_the_two_backups_share_one_timestamp(tmp_path):
    """A pair must be matchable by name after the fact."""
    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)

    _finish_batch_outputs(
        manifest=_manifest(2), config=_config(), output_dir=leg,
        iterations=5, raw_results=_consensus_rows(2, 5),
        batch_metadata=_tracker(), model_name="gemini-3-flash",
        strict=True, backup_tag="rerun",
    )

    stamps = {name.rsplit("-", 1)[-1] for name in _backups(leg)}
    assert len(stamps) == 1


def test_a_leg_with_no_prior_output_takes_no_backup(tmp_path):
    """A first-time pass has nothing to copy aside."""
    leg = tmp_path / "leg"
    leg.mkdir()

    rc = _finish_batch_outputs(
        manifest=_manifest(2), config=_config(), output_dir=leg,
        iterations=1, raw_results=[_row(f"candidate_{c:05d}") for c in (1, 2)],
        batch_metadata=_tracker(), model_name="gemini-3-flash", strict=True,
    )

    assert rc == 0
    assert _backups(leg) == []


# ─────────────────────────────────────────────────────────────────────
# (b, cont.) Both callers of the finisher
# ─────────────────────────────────────────────────────────────────────


def test_batch_recover_reads_k_from_the_leg_and_books_it(tmp_path, monkeypatch):
    """End to end: no --iterations, and a K = 5 leg still books as K = 5."""
    import scripts.lib_batch_api as lba
    import scripts.run_pv as run_pv

    crops = tmp_path / "crops"
    crops.mkdir()
    (crops / "candidate_manifest.json").write_text(json.dumps(_manifest(2)))
    config_path = tmp_path / "verifier.json"
    config_path.write_text(json.dumps(_config()))

    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)
    (leg / "batch_jobs.json").write_text(
        json.dumps({"chunks": [{"index": 0, "job": "batches/one"}]}),
    )

    class _Batches:
        def get(self, name):
            return type("J", (), {"state": type("S", (), {
                "name": "JOB_STATE_SUCCEEDED"})()})()

    class _Client:
        batches = _Batches()

    monkeypatch.setattr(run_pv, "_get_api_key", lambda: "test-key")
    monkeypatch.setattr(run_pv, "load_system_instruction", lambda cfg: "sys")
    monkeypatch.setattr("google.genai.Client", lambda **kwargs: _Client())
    monkeypatch.setattr(lba, "retrieve_batch_results",
                        lambda client, job: _consensus_rows(2, 5))

    args = argparse.Namespace(
        output_dir=leg, crops_dir=crops, verifier_config=config_path,
        job=[], model=None, thinking_level=None, temperature=None,
        iterations=None, strict=True,
    )

    assert cmd_batch_recover(args) == 0
    written = json.loads((leg / "probabilities.json").read_text())
    assert written["iterations"] == 5
    assert written["total_results"] == 10


def test_the_batch_verify_path_is_guarded_too(tmp_path, monkeypatch):
    """The gate lives in the shared finisher, so both callers inherit it."""
    import scripts.run_pv as run_pv

    leg = tmp_path / "leg"
    _seed_leg(leg, n_candidates=2, iterations=5)
    before_prob = (leg / "probabilities.json").read_bytes()
    before_cons = (leg / "consensus.json").read_bytes()

    class _FakeFiles:
        def list(self):
            return []

    class _FakeClient:
        files = _FakeFiles()

    def _build(*, manifest, config, output_path, crops_base_dir,
               temperature_override=None):
        output_path.write_bytes(b"x" * 16)
        return len(manifest["candidates"])

    monkeypatch.setattr(run_pv, "build_verifier_jsonl", _build)
    monkeypatch.setattr(run_pv, "load_system_instruction", lambda cfg: "sys")
    monkeypatch.setattr(run_pv, "_get_api_key", lambda: "test-key")
    monkeypatch.setattr(run_pv, "_resolve_model_name", lambda c, m: m)
    monkeypatch.setattr("google.genai.Client", lambda **kwargs: _FakeClient())
    # Every chunk came back under keys from some other leg's shape.
    monkeypatch.setattr(
        run_pv, "run_batch_jobs",
        lambda *a, **k: ([_row("candidate_00001_iter1")], []),
    )

    rc = _verify_batch(
        manifest=_manifest(2), config=_config(), crops_base_dir=tmp_path,
        output_dir=leg, iterations=1, temperature=None, dry_run=False,
        max_batch_candidates=None,
    )

    assert rc == 1
    assert (leg / "probabilities.json").read_bytes() == before_prob
    assert (leg / "consensus.json").read_bytes() == before_cons
    assert _backups(leg) == []
