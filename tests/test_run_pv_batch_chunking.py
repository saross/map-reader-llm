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

from scripts.run_pv import (  # noqa: E402
    DEFAULT_MAX_BATCH_CANDIDATES,
    chunk_manifest,
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
    results = run_batch_jobs(None, "m", paths, "leg", **fns,
                             log=logging.getLogger("t"))
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
    results = run_batch_jobs(None, "m", paths, "leg", **fns,
                             log=logging.getLogger("t"))
    assert len(results) == 4
    assert not any("leg-c1" in r["key"] for r in results)
