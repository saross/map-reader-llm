"""Chunked batch submission for verifier legs above the 2 GB file limit.

The Gemini 3 55-map unions (22,785 / 36,389 / 45,786 candidates at ~59 KB per
request) cannot be one batch job. These tests pin the orchestration without
an API: the manifest splits with ids preserved, every chunk is lodged before
any is polled, one failed chunk loses only its own results, and a single
chunk keeps the original filename and display name.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib_batch_api import poll_batch_job  # noqa: E402
from scripts.run_pv import (  # noqa: E402
    DEFAULT_MAX_BATCH_CANDIDATES,
    chunk_manifest,
    merge_raw_results,
    run_batch_jobs,
)

pytestmark = pytest.mark.tier1


def _manifest(n: int) -> dict:
    return {"tiles_dir": "x", "padding": 75, "total_detections": n,
            "candidates": [{"candidate_id": i, "crop_path": f"c{i}.png"}
                           for i in range(n)]}


def test_small_manifest_is_one_chunk_unchanged():
    m = _manifest(10)
    assert chunk_manifest(m, 4000) == [m]
    assert chunk_manifest(m, None) == [m]
    assert chunk_manifest(m, 0) == [m]


def test_large_manifest_splits_with_ids_and_header_preserved():
    m = _manifest(10)
    chunks = chunk_manifest(m, 4)
    assert [len(c["candidates"]) for c in chunks] == [4, 4, 2]
    ids = [c["candidate_id"] for ch in chunks for c in ch["candidates"]]
    assert ids == list(range(10))
    assert all(c["tiles_dir"] == "x" and c["padding"] == 75 for c in chunks)


def test_exact_multiple_has_no_empty_chunk():
    assert [len(c["candidates"]) for c in chunk_manifest(_manifest(8), 4)] == [4, 4]


def test_default_chunk_size_is_the_documented_one():
    assert DEFAULT_MAX_BATCH_CANDIDATES == 4000


class _Job:
    def __init__(self, name):
        self.name = name
        self.state = type("S", (), {"name": "JOB_STATE_SUCCEEDED"})()


def _fakes(fail_on: set[str] = frozenset()):
    calls: list[tuple[str, str]] = []

    def upload(client, path, name):
        calls.append(("upload", name))
        return f"files/{name}"

    def submit(client, model, uploaded, name):
        calls.append(("submit", name))
        return _Job(f"batches/{name}")

    def poll(client, job_name):
        calls.append(("poll", job_name))
        if job_name.split("/")[-1] in fail_on:
            raise RuntimeError("poll 503")
        return _Job(job_name)

    def retrieve(client, job):
        calls.append(("retrieve", job.name))
        return [{"key": f"{job.name}:r1"}, {"key": f"{job.name}:r2"}]

    return calls, dict(upload=upload, submit=submit, poll=poll, retrieve=retrieve)


def test_every_chunk_is_lodged_before_any_is_polled(tmp_path):
    calls, fns = _fakes()
    paths = [tmp_path / f"c{i}.jsonl" for i in range(3)]
    results, failed = run_batch_jobs(None, "m", paths, "leg", **fns,
                                     log=logging.getLogger("t"))
    assert failed == []
    kinds = [k for k, _ in calls]
    first_poll = kinds.index("poll")
    assert kinds[:first_poll].count("submit") == 3
    assert len(results) == 6
    assert [n for k, n in calls if k == "submit"] == ["leg-c0", "leg-c1", "leg-c2"]


def test_single_chunk_keeps_the_plain_display_name(tmp_path):
    calls, fns = _fakes()
    run_batch_jobs(None, "m", [tmp_path / "one.jsonl"], "leg", **fns,
                   log=logging.getLogger("t"))
    assert [n for k, n in calls if k == "submit"] == ["leg"]


def test_a_failed_chunk_loses_only_its_own_results(tmp_path):
    calls, fns = _fakes(fail_on={"leg-c1"})
    paths = [tmp_path / f"c{i}.jsonl" for i in range(3)]
    results, failed = run_batch_jobs(None, "m", paths, "leg", **fns,
                                     log=logging.getLogger("t"))
    assert len(results) == 4
    assert failed == [1]
    assert not any("leg-c1" in r["key"] for r in results)


def test_a_chunk_that_fails_to_lodge_does_not_abandon_the_lodged_ones(tmp_path):
    """Re-audit 2026-09-19: lodging was unguarded, so a failure on chunk k
    abandoned chunks 0..k-1 already lodged and billing."""
    calls, fns = _fakes()
    real_submit = fns["submit"]

    def submit(client, model, uploaded, name):
        if name == "leg-c1":
            raise RuntimeError("upload quota")
        return real_submit(client, model, uploaded, name)

    fns["submit"] = submit
    paths = [tmp_path / f"c{i}.jsonl" for i in range(3)]
    results, failed = run_batch_jobs(None, "m", paths, "leg", **fns,
                                     log=logging.getLogger("t"))
    assert failed == [1]
    assert len(results) == 4
    assert [n for k, n in calls if k == "retrieve"] == ["batches/leg-c0", "batches/leg-c2"]


def test_chunk_manifest_books_each_chunks_own_total():
    m = _manifest(10)
    m["total_detections"] = 10
    chunks = chunk_manifest(m, 4)
    assert [c["total_detections"] for c in chunks] == [4, 4, 2]


def test_iterations_divide_the_per_job_candidate_budget():
    """The 2 GB argument is in REQUESTS; --iterations K makes a candidate K
    requests. Pinned at the source since the division lives in _verify_batch."""
    src = (Path(__file__).resolve().parent.parent / "scripts" / "run_pv.py").read_text()
    assert "int(max_batch_candidates or 0) // max(1, iterations)" in src
    assert 'f"probabilities.json.pre-rerun-{stamp}.backup"' in src


def test_job_record_is_written_as_jobs_are_lodged_and_finished(tmp_path):
    """A chunk lost to a polling error must be retrievable by name later."""
    import json as _json
    calls, fns = _fakes(fail_on={"leg-c1"})
    paths = [tmp_path / f"c{i}.jsonl" for i in range(3)]
    rec = tmp_path / "batch_jobs.json"
    run_batch_jobs(None, "m", paths, "leg", **fns, log=logging.getLogger("t"),
                   record_path=rec)
    record = _json.loads(rec.read_text())
    assert [c["job"] for c in record["chunks"]] == ["batches/leg-c0", "batches/leg-c1", "batches/leg-c2"]
    assert record["chunks"][1]["state"].startswith("lost:")
    assert record["chunks"][0]["state"] == "JOB_STATE_SUCCEEDED"
    assert record["chunks"][0]["n_results"] == 2


def test_merge_raw_results_dedupes_by_key_newest_wins():
    old = [{"key": "a", "v": 1}, {"key": "b", "v": 1}]
    new = [{"key": "b", "v": 2}, {"key": "c", "v": 2}, {"nokey": True}]
    merged = {r["key"]: r["v"] for r in merge_raw_results(old, new)}
    assert merged == {"a": 1, "b": 2, "c": 2}


def test_poll_tolerates_transient_errors_then_returns_terminal():
    """A 503 on the polling endpoint says nothing about the job (S154 note);
    it lost a 4,000-candidate chunk on 2026-09-19 before this."""
    class _State:
        name = "JOB_STATE_SUCCEEDED"

    class _Done:
        state = _State()

    class _Batches:
        def __init__(self):
            self.n = 0

        def get(self, name):
            self.n += 1
            if self.n <= 3:
                raise RuntimeError("503 UNAVAILABLE")
            return _Done()

    class _Client:
        batches = _Batches()

    import scripts.lib_batch_api as lba
    slept = []
    orig = lba.time.sleep
    lba.time.sleep = slept.append
    try:
        job = poll_batch_job(_Client(), "batches/x", interval_seconds=7)
    finally:
        lba.time.sleep = orig
    assert job.state.name == "JOB_STATE_SUCCEEDED"
    assert slept == [7, 7, 7]


def test_poll_gives_up_after_too_many_consecutive_errors():
    class _Batches:
        def get(self, name):
            raise RuntimeError("503")

    class _Client:
        batches = _Batches()

    import scripts.lib_batch_api as lba
    orig = lba.time.sleep
    lba.time.sleep = lambda s: None
    try:
        with pytest.raises(RuntimeError):
            poll_batch_job(_Client(), "batches/x", interval_seconds=0, max_consecutive_errors=2)
    finally:
        lba.time.sleep = orig


def test_batch_recover_skips_an_unreachable_job_and_keeps_the_rest(
    tmp_path, monkeypatch,
):
    """One bad job name must not discard the jobs already fetched.

    ``batch-recover`` is the recovery path for a leg that has already lost
    data once. Job names come from ``batch_jobs.json`` and from repeatable
    ``--job`` flags, so an expired, mistyped, or foreign-project name is
    ordinary; before this guard it raised straight out of the loop and the
    leg stayed exactly as broken as it was.
    """
    import argparse
    import json as _json

    import scripts.lib_batch_api as lba
    import scripts.run_pv as run_pv

    crops_dir = tmp_path / "crops"
    crops_dir.mkdir()
    (crops_dir / "candidate_manifest.json").write_text(
        _json.dumps({"candidates": [{"candidate_id": 1}]}),
    )
    config_path = tmp_path / "verifier.json"
    config_path.write_text(_json.dumps({"model": "gemini-3-flash"}))

    leg = tmp_path / "leg"
    leg.mkdir()
    (leg / "batch_jobs.json").write_text(_json.dumps({"chunks": [
        {"index": 0, "job": "batches/gone"},
        {"index": 1, "job": "batches/good"},
    ]}))

    class _State:
        name = "JOB_STATE_SUCCEEDED"

    class _Job:
        state = _State()

    class _Batches:
        def get(self, name):
            if name == "batches/gone":
                raise RuntimeError("404 NOT_FOUND: batches/gone")
            return _Job()

    class _Client:
        batches = _Batches()

    monkeypatch.setattr(run_pv, "_get_api_key", lambda: "test-key")
    monkeypatch.setattr(run_pv, "load_system_instruction", lambda cfg: "sys")
    monkeypatch.setattr("google.genai.Client", lambda **kwargs: _Client())
    monkeypatch.setattr(
        lba, "retrieve_batch_results",
        lambda client, job: [{"key": "candidate_00001", "response": {}}],
    )

    booked: dict = {}

    def _finish(**kwargs):
        booked.update(kwargs)
        return 0

    monkeypatch.setattr(run_pv, "_finish_batch_outputs", _finish)

    args = argparse.Namespace(
        output_dir=leg, crops_dir=crops_dir, verifier_config=config_path,
        job=[], model=None, thinking_level=None, temperature=None,
        iterations=1, strict=True,
    )

    rc = run_pv.cmd_batch_recover(args)

    # The reachable job's result was still booked, despite the bad name.
    assert rc == 0
    assert [r["key"] for r in booked["raw_results"]] == ["candidate_00001"]


def test_batch_recover_reports_failure_when_no_job_is_reachable(
    tmp_path, monkeypatch,
):
    """Every job unreachable is a failure, not a silent zero-result booking."""
    import argparse
    import json as _json

    import scripts.run_pv as run_pv

    crops_dir = tmp_path / "crops"
    crops_dir.mkdir()
    (crops_dir / "candidate_manifest.json").write_text(
        _json.dumps({"candidates": [{"candidate_id": 1}]}),
    )
    config_path = tmp_path / "verifier.json"
    config_path.write_text(_json.dumps({"model": "gemini-3-flash"}))

    leg = tmp_path / "leg"
    leg.mkdir()
    (leg / "batch_jobs.json").write_text(
        _json.dumps({"chunks": [{"index": 0, "job": "batches/gone"}]}),
    )

    class _Batches:
        def get(self, name):
            raise RuntimeError("404 NOT_FOUND")

    class _Client:
        batches = _Batches()

    called: list[str] = []

    monkeypatch.setattr(run_pv, "_get_api_key", lambda: "test-key")
    monkeypatch.setattr(run_pv, "load_system_instruction", lambda cfg: "sys")
    monkeypatch.setattr("google.genai.Client", lambda **kwargs: _Client())
    monkeypatch.setattr(run_pv, "_finish_batch_outputs",
                        lambda **kwargs: called.append("booked") or 0)

    args = argparse.Namespace(
        output_dir=leg, crops_dir=crops_dir, verifier_config=config_path,
        job=[], model=None, thinking_level=None, temperature=None,
        iterations=1, strict=True,
    )

    assert run_pv.cmd_batch_recover(args) == 1
    # Nothing was booked, so no output file was overwritten.
    assert called == []


# ─────────────────────────────────────────────────────────────────────
# Polling tolerance — the semantics the parameter name promises
# ─────────────────────────────────────────────────────────────────────


def _polling_client(states):
    """A client whose ``batches.get`` walks *states*.

    Each entry is either an exception to raise or a state name to return.
    """
    class _State:
        def __init__(self, name):
            self.name = name

    class _Done:
        def __init__(self, name):
            self.state = _State(name)

    class _Batches:
        def __init__(self):
            self.calls = 0

        def get(self, name):
            self.calls += 1
            step = states[min(self.calls - 1, len(states) - 1)]
            if isinstance(step, Exception):
                raise step
            return _Done(step)

    class _Client:
        def __init__(self):
            self.batches = _Batches()

    return _Client()


def test_the_error_budget_is_consecutive_not_cumulative(monkeypatch):
    """`max_consecutive_errors` means in a row, as the name and docstring say.

    Deleting the `consecutive_errors = 0` reset turns the budget into a
    lifetime total, so a long leg that recovers fully from a handful of
    isolated 503s hours apart would abort anyway. Two errors, a successful
    non-terminal poll, then two more errors must survive a budget of two.
    """
    import scripts.lib_batch_api as lba

    monkeypatch.setattr(lba.time, "sleep", lambda s: None)
    client = _polling_client([
        RuntimeError("503 UNAVAILABLE"),
        RuntimeError("503 UNAVAILABLE"),
        "JOB_STATE_RUNNING",          # recovery — resets the counter
        RuntimeError("503 UNAVAILABLE"),
        RuntimeError("503 UNAVAILABLE"),
        "JOB_STATE_SUCCEEDED",
    ])

    job = poll_batch_job(client, "batches/x", interval_seconds=0,
                         max_consecutive_errors=2)

    assert job.state.name == "JOB_STATE_SUCCEEDED"
    assert client.batches.calls == 6


def test_the_documented_default_error_budget_is_twenty(monkeypatch):
    """20 x 30 s = the 10 minutes of dead endpoint the docstring promises.

    Both existing poll tests override `max_consecutive_errors`, so the
    default could be raised to any value and nothing would notice.
    """
    import scripts.lib_batch_api as lba

    monkeypatch.setattr(lba.time, "sleep", lambda s: None)
    client = _polling_client([RuntimeError("503 UNAVAILABLE")])

    with pytest.raises(RuntimeError):
        poll_batch_job(client, "batches/x", interval_seconds=0)

    # The budget is tolerated, the one after it propagates.
    assert client.batches.calls == 21


def test_the_job_record_carries_the_state_that_was_polled(tmp_path):
    """`batch_jobs.json` is what an operator reads after a bad leg.

    The shared fake hard-codes JOB_STATE_SUCCEEDED, so hard-coding the
    same constant into the writer was invisible — the record could claim
    success for a job that did not succeed.
    """
    import json as _json

    class _OtherJob:
        def __init__(self, name):
            self.name = name
            self.state = type("S", (), {"name": "JOB_STATE_EXPIRED"})()

    calls, fns = _fakes()
    fns["poll"] = lambda client, job_name: _OtherJob(job_name)
    paths = [tmp_path / "c0.jsonl"]
    rec = tmp_path / "batch_jobs.json"

    run_batch_jobs(None, "m", paths, "leg", **fns,
                   log=logging.getLogger("t"), record_path=rec)

    record = _json.loads(rec.read_text())
    assert record["chunks"][0]["state"] == "JOB_STATE_EXPIRED"


def test_batch_recover_does_not_merge_a_job_that_did_not_succeed(
    tmp_path, monkeypatch,
):
    """The SUCCEEDED gate, pinned.

    Both existing recover fakes return JOB_STATE_SUCCEEDED, so turning the
    gate into `if False:` was invisible — a FAILED or EXPIRED job's rows
    could be merged into the leg's probabilities.
    """
    import argparse
    import json as _json

    import scripts.lib_batch_api as lba
    import scripts.run_pv as run_pv

    crops_dir = tmp_path / "crops"
    crops_dir.mkdir()
    (crops_dir / "candidate_manifest.json").write_text(
        _json.dumps({"candidates": [{"candidate_id": 1}]}),
    )
    config_path = tmp_path / "verifier.json"
    config_path.write_text(_json.dumps({"model": "gemini-3-flash"}))
    leg = tmp_path / "leg"
    leg.mkdir()
    (leg / "batch_jobs.json").write_text(
        _json.dumps({"chunks": [{"index": 0, "job": "batches/failed"}]}),
    )

    class _Job:
        state = type("S", (), {"name": "JOB_STATE_FAILED"})()

    class _Batches:
        def get(self, name):
            return _Job()

    class _Client:
        batches = _Batches()

    retrieved: list[str] = []
    booked: list[str] = []

    monkeypatch.setattr(run_pv, "_get_api_key", lambda: "test-key")
    monkeypatch.setattr(run_pv, "load_system_instruction", lambda cfg: "sys")
    monkeypatch.setattr("google.genai.Client", lambda **kwargs: _Client())
    monkeypatch.setattr(
        lba, "retrieve_batch_results",
        lambda client, job: retrieved.append("fetched") or [{"key": "x"}],
    )
    monkeypatch.setattr(run_pv, "_finish_batch_outputs",
                        lambda **kwargs: booked.append("booked") or 0)

    args = argparse.Namespace(
        output_dir=leg, crops_dir=crops_dir, verifier_config=config_path,
        job=[], model=None, thinking_level=None, temperature=None,
        iterations=1, strict=True,
    )

    assert run_pv.cmd_batch_recover(args) == 1
    assert retrieved == []   # its results were never even fetched
    assert booked == []      # and nothing was written over the leg


def test_iterations_really_divide_the_per_job_candidate_budget(
    tmp_path, monkeypatch,
):
    """The division, pinned behaviourally rather than by source text.

    The existing test reads run_pv.py and asserts an expression is present
    in it, which a comment satisfies just as well: the division could be
    deleted outright and the suite would not move, and a K = 5 leg would
    then build chunks five times too large and breach the 2 GB per-file
    limit. This drives the real path instead and counts the candidates
    that actually reach the builder.
    """
    import scripts.run_pv as run_pv

    class _FakeFiles:
        def list(self):
            return []

    class _FakeClient:
        files = _FakeFiles()

    chunk_sizes: list[int] = []

    def _build_consensus(*, manifest, config, output_path, crops_base_dir,
                         iterations, temperature):
        chunk_sizes.append(len(manifest["candidates"]))
        output_path.write_bytes(b"x" * 16)
        return len(manifest["candidates"]) * iterations

    monkeypatch.setattr(run_pv, "build_verifier_jsonl_consensus",
                        _build_consensus)
    monkeypatch.setattr(run_pv, "load_system_instruction", lambda cfg: "sys")
    monkeypatch.setattr(run_pv, "_get_api_key", lambda: "test-key")
    monkeypatch.setattr(run_pv, "_resolve_model_name", lambda c, m: m)
    monkeypatch.setattr("google.genai.Client", lambda **kwargs: _FakeClient())
    monkeypatch.setattr(run_pv, "run_batch_jobs", lambda *a, **k: ([], []))
    monkeypatch.setattr(run_pv, "_finish_batch_outputs", lambda **kwargs: 0)

    run_pv._verify_batch(
        manifest={"candidates": [{"candidate_id": i} for i in range(10)]},
        config={"model": "gemini-3-flash"},
        crops_base_dir=tmp_path,
        output_dir=tmp_path / "leg",
        iterations=5,
        temperature=None,
        dry_run=False,
        max_batch_candidates=10,
    )

    # The limit is in REQUESTS: 10 requests per job at K = 5 is 2
    # candidates per job, so ten candidates make five chunks.
    assert chunk_sizes == [2, 2, 2, 2, 2]
