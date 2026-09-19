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
