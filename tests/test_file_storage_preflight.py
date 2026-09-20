"""Pre-lodge Files API storage guard for batch legs.

On 2026-09-19 14:05 UTC a 12-chunk verifier leg lodged 4 chunks and then
lost the remaining 8, each to::

    429 RESOURCE_EXHAUSTED ... Quota exceeded for metric:
    generativelanguage.googleapis.com/file_storage_bytes,
    limit: 21474836480 (quotaId: FileStorageBytesPerProject)

The project was holding 45 uploads totalling 21.4 GB — uploaded request
JSONLs are retained for 30 days — and nothing checked storage before the
lodging loop began. These tests pin the guard without an API: the
projection under the cap proceeds untouched, an over-cap projection that
a sweep rescues proceeds, an over-cap projection that nothing rescues
fails before a single byte is uploaded, and a storage 429 reaching the
lodging loop anyway is reported specifically without abandoning the
chunks already lodged and billing.

Section (g) pins the sweep the preflight is now allowed to run (audit
finding M6, 2026-09-20). Until then no call site passed one, because the
only candidate deleted any file that was neither registered nor young —
and nothing on the verifier path registered its uploads, so a Phase 2
sweep could delete a concurrent verifier leg's in-flight input. The sweep
now asks the batches service which jobs are alive and protects their
source files, whoever lodged them.
"""
from __future__ import annotations

import ast
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib_batch_api import (  # noqa: E402
    FILE_STORAGE_BUDGET_BYTES,
    FILE_STORAGE_CAP_BYTES,
    FILE_STORAGE_QUOTA_METRIC,
    FILE_STORAGE_SAFETY_MARGIN_BYTES,
    MAX_CHUNK_BYTES,
    FileStorageCapExceeded,
    is_file_storage_quota_error,
    make_safe_sweep,
    preflight_file_storage,
    sweep_stale_files_safe,
    upload_jsonl,
)
from scripts.lib_file_registry import (  # noqa: E402
    get_registered_files,
    register_file,
)
from scripts.run_pv import run_batch_jobs  # noqa: E402

pytestmark = pytest.mark.tier1

_GIB = 1024 ** 3

# Older than sweep_stale_files_safe's five-minute grace period, so only the
# registry or a live job can protect a file carrying this timestamp.
_STALE = datetime.now(timezone.utc) - timedelta(hours=1)

# The 429 body the incident produced, abbreviated but keeping every token
# the guard is allowed to match on.
_STORAGE_429 = (
    "429 RESOURCE_EXHAUSTED. Quota exceeded for metric: "
    "generativelanguage.googleapis.com/file_storage_bytes, "
    "limit: 21474836480 (quotaId: FileStorageBytesPerProject)"
)


# ─────────────────────────────────────────────────────────────────────
# Fakes
# ─────────────────────────────────────────────────────────────────────


class _FakeFile:
    """One entry in the fake Files API listing.

    ``create_time`` defaults to *now*, which is what the API reports for a
    file that has just been uploaded — and what the sweep's grace period
    protects. A test that wants a file the sweep may reclaim passes
    ``create_time=_STALE``.

    ``size_bytes=None`` is what the API reports for an upload it is still
    ingesting (state ``PROCESSING``) — a concurrent lodger's chunk, in
    practice.
    """

    def __init__(self, name: str, size_bytes: int | None,
                 create_time: datetime | None = None) -> None:
        self.name = name
        self.size_bytes = size_bytes
        self.create_time = create_time or datetime.now(timezone.utc)


class _FakeFilesApi:
    """``client.files`` — records every call so the tests can assert on it."""

    def __init__(self, files: list[_FakeFile]) -> None:
        self._files = list(files)
        self.list_calls = 0
        self.uploads: list[str] = []
        self.deleted: list[str] = []

    def list(self) -> list[_FakeFile]:
        self.list_calls += 1
        return list(self._files)

    def upload(self, *, file, config=None):  # noqa: ANN001 - SDK shape
        self.uploads.append(str(file))
        return _FakeFile(f"files/{Path(file).stem}", 0)

    def delete(self, *, name: str) -> None:
        self.deleted.append(name)
        self._files = [f for f in self._files if f.name != name]


def _job(name: str, state: str, src_file: str | None):
    """A fake ``BatchJob``, shaped like google-genai 1.73.1's.

    ``BatchJob.state`` is a ``JobState`` enum (read through ``.name``) and
    ``BatchJob.src`` is a ``BatchJobSource`` whose ``file_name`` is the
    uploaded request JSONL.
    """
    return SimpleNamespace(
        name=name,
        state=SimpleNamespace(name=state),
        src=SimpleNamespace(file_name=src_file),
    )


class _FakeBatchesApi:
    """``client.batches`` — the sweep's independent source of truth."""

    def __init__(self, jobs: list[object] | None = None,
                 error: Exception | None = None) -> None:
        self._jobs = list(jobs or [])
        self.error = error
        self.list_calls = 0

    def list(self) -> list[object]:
        self.list_calls += 1
        if self.error is not None:
            raise self.error
        return list(self._jobs)


class _FakeClient:
    """Minimal stand-in for ``google.genai.Client``."""

    def __init__(self, files: list[_FakeFile] | None = None,
                 jobs: list[object] | None = None,
                 batches_error: Exception | None = None) -> None:
        self.files = _FakeFilesApi(files or [])
        self.batches = _FakeBatchesApi(jobs, batches_error)


def _chunk(tmp_path: Path, name: str, size_bytes: int = 1024) -> Path:
    """Write a request-JSONL stand-in of a known size on disk."""
    path = tmp_path / name
    path.write_bytes(b"x" * size_bytes)
    return path


def _sweep_deleting(client: _FakeClient, names: list[str]):
    """Build a sweep callable that really removes *names* from the fake."""

    def _sweep() -> tuple[int, float]:
        freed = sum(f.size_bytes for f in client.files.list()
                    if f.name in names)
        for name in names:
            client.files.delete(name=name)
        return len(names), freed / _GIB

    return _sweep


# ─────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────


def test_the_cap_is_the_limit_the_429_reported():
    """21,474,836,480 bytes = 20 GiB, less a one-maximum-chunk margin.

    The margin was 5% until 2026-09-20 (audit finding M4). Five per cent
    of the cap is 1 GiB — less than the ~1.3 GB a proposer chunk reaches —
    so two legs lodging in parallel could both clear the preflight and the
    second still take the 429 it exists to prevent. The head-room now
    holds one whole chunk at the documented 2 GB maximum.
    """
    assert FILE_STORAGE_CAP_BYTES == 21_474_836_480
    assert FILE_STORAGE_SAFETY_MARGIN_BYTES == MAX_CHUNK_BYTES
    assert FILE_STORAGE_BUDGET_BYTES < FILE_STORAGE_CAP_BYTES
    assert FILE_STORAGE_BUDGET_BYTES == (
        FILE_STORAGE_CAP_BYTES - FILE_STORAGE_SAFETY_MARGIN_BYTES
    )


def test_the_margin_is_at_least_one_maximum_chunk():
    """The property the percentage failed, stated as a property.

    A future edit that returns the margin to a fraction of the cap has to
    clear this: the head-room must still hold a whole chunk, because the
    race it covers is exactly one concurrent lodge.
    """
    margin = FILE_STORAGE_CAP_BYTES - FILE_STORAGE_BUDGET_BYTES
    assert margin >= MAX_CHUNK_BYTES
    # The old 5% margin did not, which is the finding in one line.
    assert FILE_STORAGE_CAP_BYTES - int(FILE_STORAGE_CAP_BYTES * 0.95) \
        < MAX_CHUNK_BYTES


def test_the_maximum_chunk_is_the_documented_batch_file_limit():
    """2 GB is the Batch API per-file ceiling both chunkers size below."""
    assert MAX_CHUNK_BYTES == 2_000_000_000


# ─────────────────────────────────────────────────────────────────────
# (a) Under the cap
# ─────────────────────────────────────────────────────────────────────


def test_under_the_cap_proceeds_without_sweeping(tmp_path):
    client = _FakeClient([_FakeFile("files/old", 2 * _GIB)])
    chunks = [_chunk(tmp_path, "c0.jsonl", 1024),
              _chunk(tmp_path, "c1.jsonl", 2048)]
    swept: list[str] = []

    def _sweep() -> tuple[int, float]:
        swept.append("called")
        return 0, 0.0

    projected = preflight_file_storage(client, chunks, sweep=_sweep)

    assert projected == 2 * _GIB + 1024 + 2048
    assert swept == []
    assert client.files.deleted == []
    assert client.files.uploads == []


def test_the_audit_is_logged_at_info_on_every_lodging(tmp_path, caplog):
    """Requirement: the run log always records the storage state."""
    client = _FakeClient([_FakeFile("files/old", 3 * _GIB)])
    with caplog.at_level(logging.INFO):
        preflight_file_storage(client, [_chunk(tmp_path, "c0.jsonl")])

    info = "\n".join(r.getMessage() for r in caplog.records
                     if r.levelno == logging.INFO)
    assert "File storage preflight" in info
    assert "1 file(s) stored" in info
    assert "3.00 GB" in info


def test_missing_chunk_files_contribute_nothing(tmp_path):
    """A chunk not on disk cannot be uploaded; it must not crash the guard."""
    client = _FakeClient([_FakeFile("files/old", _GIB)])
    projected = preflight_file_storage(client, [tmp_path / "absent.jsonl"])
    assert projected == _GIB


def test_an_unavailable_audit_warns_and_lets_the_leg_proceed(tmp_path, caplog):
    """The preflight guards spend; it is not a gate on API health.

    The WARNING is load-bearing, not decoration: when the audit cannot
    run the leg lodges unguarded, and that line is the operator's only
    signal that it did. Pinning the return value alone would let the
    warning be deleted silently.
    """
    client = _FakeClient()

    def _boom():
        raise RuntimeError("files.list unavailable")

    client.files.list = _boom  # type: ignore[method-assign]

    with caplog.at_level(logging.WARNING):
        result = preflight_file_storage(
            client, [_chunk(tmp_path, "c0.jsonl")],
        )

    assert result is None
    warnings = "\n".join(r.getMessage() for r in caplog.records
                         if r.levelno == logging.WARNING)
    assert "preflight skipped" in warnings
    assert "unguarded" in warnings
    assert "files.list unavailable" in warnings


# ─────────────────────────────────────────────────────────────────────
# (a2) An upload still PROCESSING reports no size (audit finding m10)
# ─────────────────────────────────────────────────────────────────────


def test_a_processing_upload_is_charged_at_one_maximum_chunk(tmp_path):
    """``size_bytes=None`` counted as zero under-counted the race itself.

    The file with no size is, in practice, a concurrent leg's chunk part
    way through its upload — the exact event the head-room exists for. It
    now contributes a whole maximum chunk to the projection.
    """
    client = _FakeClient([
        _FakeFile("files/done", 3 * _GIB),
        _FakeFile("files/in_flight", None),
    ])
    chunk = _chunk(tmp_path, "c0.jsonl", 1024)

    projected = preflight_file_storage(client, [chunk])

    assert projected == 3 * _GIB + MAX_CHUNK_BYTES + 1024


def test_a_leg_that_only_fits_by_ignoring_a_processing_upload_is_refused(
    tmp_path,
):
    """The failure mode m10 describes, end to end.

    Stored bytes plus this leg sit just under budget — but only if the
    in-flight upload is counted as nothing. Charged properly, the leg
    does not fit and is refused before a byte is sent.
    """
    pending = 1024
    sized = FILE_STORAGE_BUDGET_BYTES - pending
    client = _FakeClient([
        _FakeFile("files/done", sized),
        _FakeFile("files/in_flight", None),
    ])
    chunk = _chunk(tmp_path, "c0.jsonl", pending)

    with pytest.raises(FileStorageCapExceeded) as excinfo:
        preflight_file_storage(client, [chunk])

    assert excinfo.value.projected_bytes == (
        sized + MAX_CHUNK_BYTES + pending
    )
    assert client.files.uploads == []


def test_the_processing_charge_is_announced(tmp_path, caplog):
    """An operator reading a high projection must be able to see why."""
    client = _FakeClient([
        _FakeFile("files/done", _GIB),
        _FakeFile("files/in_flight", None),
    ])
    with caplog.at_level(logging.WARNING):
        preflight_file_storage(client, [_chunk(tmp_path, "c0.jsonl")])

    warnings = "\n".join(r.getMessage() for r in caplog.records
                         if r.levelno == logging.WARNING)
    assert "PROCESSING" in warnings
    assert "1 of 2" in warnings


def test_sized_uploads_are_charged_at_their_real_size(tmp_path):
    """The charge must not leak onto files that did report a size."""
    client = _FakeClient([_FakeFile("files/done", 2 * _GIB)])
    projected = preflight_file_storage(
        client, [_chunk(tmp_path, "c0.jsonl", 1024)],
    )
    assert projected == 2 * _GIB + 1024


# ─────────────────────────────────────────────────────────────────────
# (b) Over the cap, sweep frees enough
# ─────────────────────────────────────────────────────────────────────


def test_over_the_cap_proceeds_when_a_sweep_frees_enough(tmp_path):
    client = _FakeClient([
        _FakeFile("files/stale", 12 * _GIB),
        _FakeFile("files/live", 8 * _GIB),
    ])
    chunks = [_chunk(tmp_path, "c0.jsonl")]
    assert 20 * _GIB > FILE_STORAGE_BUDGET_BYTES  # the leg starts over budget

    projected = preflight_file_storage(
        client, chunks, sweep=_sweep_deleting(client, ["files/stale"]),
    )

    assert client.files.deleted == ["files/stale"]
    assert projected == 8 * _GIB + 1024
    assert projected <= FILE_STORAGE_BUDGET_BYTES


# ─────────────────────────────────────────────────────────────────────
# (c) Over the cap, nothing frees enough
# ─────────────────────────────────────────────────────────────────────


def test_over_the_cap_fails_fast_with_no_upload_attempted(tmp_path):
    client = _FakeClient([
        _FakeFile("files/huge", 19 * _GIB),
        _FakeFile("files/big", 2 * _GIB),
    ])
    chunks = [_chunk(tmp_path, f"c{i}.jsonl") for i in range(12)]

    with pytest.raises(FileStorageCapExceeded) as excinfo:
        preflight_file_storage(client, chunks)

    message = str(excinfo.value)
    assert FILE_STORAGE_QUOTA_METRIC in message
    assert f"{21 * _GIB + 12 * 1024:,} bytes" in message
    assert f"{FILE_STORAGE_CAP_BYTES:,} bytes" in message
    assert "files/huge (19.00 GB)" in message
    assert "files/big (2.00 GB)" in message
    assert excinfo.value.projected_bytes == 21 * _GIB + 12 * 1024
    assert excinfo.value.cap_bytes == FILE_STORAGE_CAP_BYTES
    # Nothing was uploaded and nothing was deleted: no spend committed.
    assert client.files.uploads == []
    assert client.files.deleted == []


def test_a_sweep_that_cannot_free_enough_still_fails_fast(tmp_path):
    client = _FakeClient([
        _FakeFile("files/huge", 19 * _GIB),
        _FakeFile("files/small", 2 * _GIB),
    ])

    with pytest.raises(FileStorageCapExceeded):
        preflight_file_storage(
            client, [_chunk(tmp_path, "c0.jsonl")],
            sweep=_sweep_deleting(client, ["files/small"]),
        )

    assert client.files.deleted == ["files/small"]
    assert client.files.uploads == []


# ─────────────────────────────────────────────────────────────────────
# (d) The per-chunk guard in the lodging loop
# ─────────────────────────────────────────────────────────────────────


def test_is_file_storage_quota_error_matches_only_the_storage_429():
    assert is_file_storage_quota_error(RuntimeError(_STORAGE_429))
    assert is_file_storage_quota_error(
        RuntimeError("quotaId: FileStorageBytesPerProject"))
    assert not is_file_storage_quota_error(RuntimeError("503 UNAVAILABLE"))
    assert not is_file_storage_quota_error(
        RuntimeError("429 RESOURCE_EXHAUSTED: requests per minute"))


class _Job:
    def __init__(self, name: str) -> None:
        self.name = name
        self.state = type("S", (), {"name": "JOB_STATE_SUCCEEDED"})()


def _lifecycle(upload_fails_on: dict[str, Exception]):
    """Fake lifecycle functions; named chunks raise on upload."""

    def upload(client, path, name):
        if name in upload_fails_on:
            raise upload_fails_on[name]
        return f"files/{name}"

    def submit(client, model, uploaded, name):
        return _Job(f"batches/{name}")

    def poll(client, job_name):
        return _Job(job_name)

    def retrieve(client, job):
        return [{"key": f"{job.name}:r1"}, {"key": f"{job.name}:r2"}]

    return dict(upload=upload, submit=submit, poll=poll, retrieve=retrieve)


def test_a_storage_429_is_reported_specifically_and_the_loop_continues(
    tmp_path, caplog,
):
    """The incident's failure, seen from inside the loop.

    The generic "failed to lodge" line said nothing about why eight
    chunks died in a row. The specific line must name the cap, point at
    ``audit_file_storage``, and say the remaining chunks will not lodge —
    while the loop still finishes the chunks that did lodge.
    """
    fns = _lifecycle({"leg-c1": RuntimeError(_STORAGE_429)})
    paths = [tmp_path / f"c{i}.jsonl" for i in range(3)]

    with caplog.at_level(logging.ERROR):
        results, failed = run_batch_jobs(
            None, "m", paths, "leg", **fns, log=logging.getLogger("t"),
        )

    assert failed == [1]
    assert len(results) == 4  # chunks 0 and 2 still polled and retrieved
    errors = "\n".join(r.getMessage() for r in caplog.records
                       if r.levelno >= logging.ERROR)
    assert "storage cap" in errors
    assert FILE_STORAGE_QUOTA_METRIC in errors
    assert "audit_file_storage" in errors
    assert "remaining chunks will not lodge" in errors
    # The generic line must NOT be what this chunk got.
    assert "failed to lodge" not in errors


def test_a_non_storage_lodging_error_keeps_the_generic_message(
    tmp_path, caplog,
):
    """Guard against the storage matcher swallowing ordinary failures."""
    fns = _lifecycle({"leg-c1": RuntimeError("503 UNAVAILABLE")})
    paths = [tmp_path / f"c{i}.jsonl" for i in range(3)]

    with caplog.at_level(logging.ERROR):
        _results, failed = run_batch_jobs(
            None, "m", paths, "leg", **fns, log=logging.getLogger("t"),
        )

    assert failed == [1]
    errors = "\n".join(r.getMessage() for r in caplog.records
                       if r.levelno >= logging.ERROR)
    assert "failed to lodge" in errors
    assert "storage cap" not in errors


def test_the_record_keeps_the_storage_429_verbatim(tmp_path):
    """``batch_jobs.json`` must still carry the underlying error text."""
    import json

    fns = _lifecycle({"leg-c1": RuntimeError(_STORAGE_429)})
    paths = [tmp_path / f"c{i}.jsonl" for i in range(3)]
    record_path = tmp_path / "batch_jobs.json"

    run_batch_jobs(None, "m", paths, "leg", **fns,
                   log=logging.getLogger("t"), record_path=record_path)

    record = json.loads(record_path.read_text())
    assert record["chunks"][1]["state"].startswith("lodging failed:")
    assert "file_storage_bytes" in record["chunks"][1]["state"]
    assert record["chunks"][0]["state"] == "JOB_STATE_SUCCEEDED"


# ─────────────────────────────────────────────────────────────────────
# (e) The boundary
# ─────────────────────────────────────────────────────────────────────


def test_a_projection_exactly_on_the_budget_proceeds(tmp_path):
    """The budget is inclusive — ``<=``, not ``<``.

    Pins the boundary operator. Without a case sitting exactly on it,
    flipping ``projected <= FILE_STORAGE_BUDGET_BYTES`` to ``<`` would
    refuse a leg that fits and leave the suite green.
    """
    pending = 4096
    client = _FakeClient(
        [_FakeFile("files/old", FILE_STORAGE_BUDGET_BYTES - pending)],
    )
    chunk = _chunk(tmp_path, "c0.jsonl", pending)

    assert preflight_file_storage(client, [chunk]) == FILE_STORAGE_BUDGET_BYTES
    assert client.files.uploads == []


def test_one_byte_over_the_budget_is_refused(tmp_path):
    """The other side of the same boundary."""
    pending = 4096
    client = _FakeClient(
        [_FakeFile("files/old", FILE_STORAGE_BUDGET_BYTES - pending + 1)],
    )
    chunk = _chunk(tmp_path, "c0.jsonl", pending)

    with pytest.raises(FileStorageCapExceeded):
        preflight_file_storage(client, [chunk])
    assert client.files.uploads == []


# ─────────────────────────────────────────────────────────────────────
# (f) The wiring — the guard is only worth what its call sites are
# ─────────────────────────────────────────────────────────────────────


def test_verify_batch_checks_storage_before_the_first_upload(
    tmp_path, monkeypatch,
):
    """The verifier wiring, not the helper.

    Until this test existed, deleting
    ``preflight_file_storage(client, jsonl_paths, log=logger)`` from
    ``run_pv._verify_batch`` left every test in the suite green — the
    guard was unit-tested but never proved to be *called*. The assertion
    that matters is the consequence: a full project uploads nothing.
    """
    import scripts.run_pv as run_pv

    client = _FakeClient([_FakeFile("files/huge", 20 * _GIB)])

    def _build(*, manifest, config, output_path, crops_base_dir,
               temperature_override=None):
        """Stand in for the JSONL builder; writes a chunk of known size."""
        output_path.write_bytes(b"x" * 4096)
        return len(manifest.get("candidates", []))

    monkeypatch.setattr(run_pv, "build_verifier_jsonl", _build)
    monkeypatch.setattr(run_pv, "load_system_instruction", lambda cfg: "sys")
    monkeypatch.setattr(run_pv, "_get_api_key", lambda: "test-key")
    monkeypatch.setattr(run_pv, "_resolve_model_name", lambda c, m: m)
    monkeypatch.setattr("google.genai.Client", lambda **kwargs: client)

    output_dir = tmp_path / "leg"
    rc = run_pv._verify_batch(
        manifest={"candidates": [{"candidate_id": 1}, {"candidate_id": 2}]},
        config={"model": "gemini-3-flash"},
        crops_base_dir=tmp_path,
        output_dir=output_dir,
        iterations=1,
        temperature=None,
        dry_run=False,
    )

    assert rc == 1
    # Nothing lodged, so nothing is billing and no outputs were booked.
    assert client.files.uploads == []
    assert not (output_dir / "probabilities.json").exists()
    assert not (output_dir / "batch_jobs.json").exists()


def test_run_batch_unit_checks_storage_before_submitting(
    tmp_path, monkeypatch,
):
    """The proposer wiring, the same way.

    ``run_batch_unit`` must refuse the unit before ``submit_batch_unit``
    uploads its ~1.3 GB chunk. Deleting the call site left the existing
    ``run_batch_unit`` tests green because their ``MagicMock`` client
    makes the audit unavailable, so the guard was inert there and
    nothing asserted on it.
    """
    import scripts.lib_batch_api as lba

    client = _FakeClient([_FakeFile("files/huge", 20 * _GIB)])
    ctx = lba.BatchUnitContext(
        unit_key="T1.0/run_1",
        unit={},
        output_file=tmp_path / "unit.geojson",
        jsonl_path=_chunk(tmp_path, "unit.jsonl", 4096),
        submitted_keys=["tile_001.png"],
        tile_paths=[tmp_path / "tile_001.png"],
        prompt_config={},
        model_name="gemini-3-flash",
        system_instruction="sys",
        config_version="v1",
        line_count=1,
    )
    submitted: list[object] = []

    def _submit(*args, **kwargs):
        submitted.append(args)
        return "batches/should-not-happen", "files/should-not-happen"

    def _poll(*args, **kwargs):
        """Never reached. Present so that a regression fails fast.

        Without it, removing the guard would send the unit into
        ``poll_batch_job``, whose new transient-error tolerance retries a
        broken client for 20 x 30 s before propagating — a twenty-minute
        hang instead of a red test.
        """
        raise AssertionError("polled a unit that should not have lodged")

    monkeypatch.setattr(lba, "prepare_batch_unit", lambda **kwargs: ctx)
    monkeypatch.setattr(lba, "submit_batch_unit", _submit)
    monkeypatch.setattr(lba, "poll_batch_job", _poll)

    success, message, cost = lba.run_batch_unit(
        unit={},
        config={},
        output_dir=tmp_path / "out",
        client=client,
        model_name="gemini-3-flash",
        system_instruction="sys",
        examples=[],
        config_version="v1",
    )

    assert success is False
    assert message.startswith("submit_error:")
    assert FILE_STORAGE_QUOTA_METRIC in message
    assert cost == 0.0
    # The consequence: no submission attempted, nothing uploaded.
    assert submitted == []
    assert client.files.uploads == []


def test_a_dry_run_unit_never_reaches_the_storage_check(tmp_path, monkeypatch):
    """A dry run uploads nothing, so a full project must not block it.

    Pins the ordering of the ``dry_run`` early return against the
    preflight: moving the check above it would make every rehearsal fail
    on a project that happens to be full.
    """
    import scripts.lib_batch_api as lba

    client = _FakeClient([_FakeFile("files/huge", 20 * _GIB)])
    ctx = lba.BatchUnitContext(
        unit_key="T1.0/run_1",
        unit={},
        output_file=tmp_path / "unit.geojson",
        jsonl_path=_chunk(tmp_path, "dry.jsonl", 4096),
        submitted_keys=["tile_001.png"],
        tile_paths=[tmp_path / "tile_001.png"],
        prompt_config={},
        model_name="gemini-3-flash",
        system_instruction="sys",
        config_version="v1",
        line_count=1,
    )
    monkeypatch.setattr(lba, "prepare_batch_unit", lambda **kwargs: ctx)

    success, message, _cost = lba.run_batch_unit(
        unit={},
        config={},
        output_dir=tmp_path / "out",
        client=client,
        model_name="gemini-3-flash",
        system_instruction="sys",
        examples=[],
        config_version="v1",
        dry_run=True,
    )

    assert success is True
    assert message == "dry_run"
    assert client.files.list_calls == 0
    assert client.files.uploads == []


def test_the_quota_error_is_recognised_from_the_metric_alone(tmp_path):
    """The metric clause must carry its own weight.

    `_STORAGE_429` contains BOTH the metric and the quota id, so it could
    not tell the two branches apart: reducing the matcher to
    `FILE_STORAGE_QUOTA_ID in text` left the whole suite green. A 429 body
    that names the metric without the `quotaId` suffix would then fall back
    to the generic "failed to lodge" message — straight back to the
    2026-09-19 symptom, where eight chunks died in a row and the log never
    said why.
    """
    metric_only = (
        "429 RESOURCE_EXHAUSTED. Quota exceeded for metric: "
        "generativelanguage.googleapis.com/file_storage_bytes, "
        "limit: 21474836480"
    )
    assert FILE_STORAGE_QUOTA_METRIC.split("/")[-1] in metric_only
    assert "FileStorageBytesPerProject" not in metric_only
    assert is_file_storage_quota_error(RuntimeError(metric_only))


def test_the_failure_names_the_largest_files_first(tmp_path):
    """The message exists to tell an operator what to delete FIRST.

    With only two stored files and `top_n = 5` the ordering was
    unobservable, so reversing the sort left the suite green while the
    message named the smallest files to delete.
    """
    client = _FakeClient([
        _FakeFile("files/small", 1 * _GIB),
        _FakeFile("files/biggest", 9 * _GIB),
        _FakeFile("files/medium", 5 * _GIB),
        _FakeFile("files/tiny", 1024),
        _FakeFile("files/large", 7 * _GIB),
        _FakeFile("files/never-named", 512),
    ])

    with pytest.raises(FileStorageCapExceeded) as excinfo:
        preflight_file_storage(client, [_chunk(tmp_path, "c0.jsonl")])

    message = str(excinfo.value)
    named = [n for n in ("files/biggest", "files/large", "files/medium",
                         "files/small", "files/tiny") if n in message]
    assert named == ["files/biggest", "files/large", "files/medium",
                     "files/small", "files/tiny"]
    assert message.index("files/biggest") < message.index("files/large")
    # top_n = 5, so the sixth-largest is not named at all.
    assert "files/never-named" not in message


# ─────────────────────────────────────────────────────────────────────
# (g) The sweep — job state first, the registry second
# ─────────────────────────────────────────────────────────────────────


def _registry(tmp_path: Path) -> Path:
    """Path to an empty per-test copy of the shared registry."""
    return tmp_path / ".active_files.json"


def test_a_live_jobs_input_survives_the_sweep(tmp_path):
    """The M6 data-loss path, closed.

    A verifier leg uploads its request JSONL through ``upload_jsonl`` and
    lodges a batch job that runs for hours. Before 2026-09-20 nothing on
    that path registered the upload, so a concurrent Phase 2 sweep saw an
    unregistered file older than five minutes and deleted it — killing
    the job server-side with no local error. Job state is now consulted
    first, so the file survives however old and however unregistered it
    is, while a genuine orphan beside it still goes.
    """
    client = _FakeClient(
        files=[
            _FakeFile("files/in-flight", 3 * _GIB, create_time=_STALE),
            _FakeFile("files/orphan", 1 * _GIB, create_time=_STALE),
        ],
        jobs=[_job("batches/live", "JOB_STATE_RUNNING", "files/in-flight")],
    )

    deleted, freed_gb = sweep_stale_files_safe(client, _registry(tmp_path))

    assert client.files.deleted == ["files/orphan"]
    assert deleted == 1
    assert freed_gb == pytest.approx(1.0)


def test_a_finished_jobs_input_is_swept(tmp_path):
    """The other side: a terminal job protects nothing.

    Its input has already been read, and reclaiming it is the whole point
    of the sweep — a guard that protected every file named by any job
    would free nothing and the preflight could not use it.
    """
    client = _FakeClient(
        files=[_FakeFile("files/done", 4 * _GIB, create_time=_STALE)],
        jobs=[_job("batches/done", "JOB_STATE_SUCCEEDED", "files/done")],
    )

    deleted, _freed = sweep_stale_files_safe(client, _registry(tmp_path))

    assert client.files.deleted == ["files/done"]
    assert deleted == 1


def test_every_non_terminal_state_protects_its_input(tmp_path):
    """PENDING and an unrecognised state are live too, not just RUNNING.

    Terminal membership is the test, not a list of live states: a state
    the SDK adds later must protect its file by default rather than have
    its input swept the moment it is not one of the states this code
    happened to know about.
    """
    client = _FakeClient(
        files=[
            _FakeFile("files/pending", _GIB, create_time=_STALE),
            _FakeFile("files/unknown-state", _GIB, create_time=_STALE),
            _FakeFile("files/cancelled", _GIB, create_time=_STALE),
        ],
        jobs=[
            _job("batches/p", "JOB_STATE_PENDING", "files/pending"),
            _job("batches/u", "JOB_STATE_SOMETHING_NEW", "files/unknown-state"),
            _job("batches/c", "JOB_STATE_CANCELLED", "files/cancelled"),
        ],
    )

    sweep_stale_files_safe(client, _registry(tmp_path))

    assert client.files.deleted == ["files/cancelled"]


def test_a_sweep_that_cannot_see_the_jobs_deletes_nothing(tmp_path, caplog):
    """A sweep that cannot see the jobs is not a safe sweep.

    The listing is the only way to tell an in-flight input from an
    orphan. Falling back to the registry alone would reinstate exactly
    the hazard this guard exists to close, so the sweep aborts — and says
    so, because the caller will then report a storage cap it might
    otherwise have cleared.
    """
    client = _FakeClient(
        files=[_FakeFile("files/orphan", 4 * _GIB, create_time=_STALE)],
        batches_error=RuntimeError("batches.list unavailable"),
    )

    with caplog.at_level(logging.WARNING):
        deleted, freed_gb = sweep_stale_files_safe(client, _registry(tmp_path))

    assert (deleted, freed_gb) == (0, 0.0)
    assert client.files.deleted == []
    warnings = "\n".join(r.getMessage() for r in caplog.records
                         if r.levelno == logging.WARNING)
    assert "Nothing deleted" in warnings
    assert "batches.list unavailable" in warnings


def test_a_registered_file_survives_before_its_job_exists(tmp_path):
    """The registry is the belt: it covers the upload-to-lodge window.

    Between an upload completing and its batch job being created there is
    no job to protect the file, so job state alone would leave it exposed
    once the grace period lapsed. This is why ``upload_jsonl`` registers.
    """
    registry = _registry(tmp_path)
    register_file(registry, "files/just-uploaded", unit_key="leg-c0")
    client = _FakeClient(
        files=[_FakeFile("files/just-uploaded", 2 * _GIB, create_time=_STALE)],
    )

    deleted, _freed = sweep_stale_files_safe(client, registry)

    assert (deleted, client.files.deleted) == (0, [])


def test_upload_jsonl_registers_what_it_uploaded(tmp_path):
    """The registration M6 asked for, at the one site every path shares.

    ``run_pv``'s lodging loop and ``submit_batch_unit`` both upload
    through this function; before 2026-09-20 neither registered, so only
    ``run_phase2``'s own uploads were protected.
    """
    client = _FakeClient()
    registry = _registry(tmp_path)

    name = upload_jsonl(
        client, _chunk(tmp_path, "c0.jsonl"), "leg-c0", registry_path=registry,
    )

    assert name == "files/c0"
    assert get_registered_files(registry, prune_stale=False) == {"files/c0"}


def test_an_unwritable_registry_does_not_fail_the_upload(tmp_path, caplog):
    """Registration is best-effort — the upload has already happened.

    Raising here would turn a bookkeeping failure into a lost upload that
    is already consuming the storage cap, with the caller believing
    nothing was lodged.
    """
    client = _FakeClient()
    blocked = tmp_path / "not-a-dir"
    blocked.write_text("this is a file, so a registry cannot live under it\n")

    with caplog.at_level(logging.WARNING):
        name = upload_jsonl(
            client, _chunk(tmp_path, "c0.jsonl"), "leg-c0",
            registry_path=blocked / ".active_files.json",
        )

    assert name == "files/c0"
    assert "Could not register uploaded file" in "\n".join(
        r.getMessage() for r in caplog.records if r.levelno == logging.WARNING
    )


def test_cleanup_deregisters_what_it_deletes(tmp_path):
    """A registry entry must not outlive its file.

    A stale entry protects a name that no longer exists from every future
    sweep, and after 30 days of a campaign that is how a registry becomes
    useless.
    """
    from scripts.lib_batch_api import cleanup_batch_files

    registry = _registry(tmp_path)
    register_file(registry, "files/done", unit_key="leg-c0")
    client = _FakeClient(files=[_FakeFile("files/done", _GIB)])

    deleted, errors = cleanup_batch_files(
        client, ["files/done"], label="leg", registry_path=registry,
    )

    assert (deleted, errors) == (1, 0)
    assert get_registered_files(registry, prune_stale=False) == set()


def test_the_preflight_sweep_frees_an_idle_file_and_proceeds(tmp_path):
    """The wiring M6 unlocked, end to end.

    An over-cap projection now frees the input of a leg that has
    finished, re-audits, and lodges — where before the guard could only
    refuse, because the sweep it had was not safe to run.
    """
    client = _FakeClient(
        files=[
            _FakeFile("files/finished", 14 * _GIB, create_time=_STALE),
            _FakeFile("files/live", 6 * _GIB, create_time=_STALE),
        ],
        jobs=[
            _job("batches/done", "JOB_STATE_SUCCEEDED", "files/finished"),
            _job("batches/live", "JOB_STATE_RUNNING", "files/live"),
        ],
    )
    chunk = _chunk(tmp_path, "c0.jsonl", 4096)
    assert 20 * _GIB + 4096 > FILE_STORAGE_BUDGET_BYTES  # starts over budget

    projected = preflight_file_storage(
        client, [chunk], sweep=make_safe_sweep(client, _registry(tmp_path)),
    )

    assert client.files.deleted == ["files/finished"]
    assert projected == 6 * _GIB + 4096
    assert projected <= FILE_STORAGE_BUDGET_BYTES


def test_the_preflight_refuses_when_only_live_files_remain(tmp_path):
    """Nothing idle to free, so the leg fails fast with nothing deleted.

    This is the case that would have been a data-loss event with the old
    sweep: both files are in-flight inputs of other processes' jobs, and
    freeing space by deleting them would have killed those jobs to lodge
    this one.
    """
    client = _FakeClient(
        files=[
            _FakeFile("files/live-a", 14 * _GIB, create_time=_STALE),
            _FakeFile("files/live-b", 6 * _GIB, create_time=_STALE),
        ],
        jobs=[
            _job("batches/a", "JOB_STATE_RUNNING", "files/live-a"),
            _job("batches/b", "JOB_STATE_PENDING", "files/live-b"),
        ],
    )

    with pytest.raises(FileStorageCapExceeded):
        preflight_file_storage(
            client, [_chunk(tmp_path, "c0.jsonl", 4096)],
            sweep=make_safe_sweep(client, _registry(tmp_path)),
        )

    assert client.files.deleted == []
    assert client.files.uploads == []


def test_an_unavailable_re_audit_after_a_sweep_warns_and_proceeds(
    tmp_path, caplog,
):
    """The post-sweep re-audit honours the same warn-and-proceed contract.

    Falling through to the refusal would report the *pre-sweep* file
    count and byte total — numbers describing storage that no longer
    exists, after the operator was told files had just been deleted.
    """
    client = _FakeClient(
        files=[_FakeFile("files/huge", 20 * _GIB, create_time=_STALE)],
    )
    calls = {"n": 0}
    real_list = client.files.list

    def _list_once():
        calls["n"] += 1
        if calls["n"] > 1:
            raise RuntimeError("files.list unavailable after the sweep")
        return real_list()

    client.files.list = _list_once  # type: ignore[method-assign]

    with caplog.at_level(logging.WARNING):
        result = preflight_file_storage(
            client, [_chunk(tmp_path, "c0.jsonl", 4096)],
            sweep=lambda: (0, 0.0),
        )

    assert result is None
    warnings = "\n".join(r.getMessage() for r in caplog.records
                         if r.levelno == logging.WARNING)
    assert "preflight skipped" in warnings
    assert client.files.uploads == []


def _called_names(tree: ast.AST) -> set[str]:
    """Every call in *tree*, as a dotted name (``client.files.delete``)."""

    def dotted(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{dotted(node.value)}.{node.attr}"
        return "?"

    return {dotted(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}


def test_phase2s_sweeps_inherit_the_job_state_guard():
    """Phase 2 owns no file deletion of its own, so it inherits the guard.

    ``run_phase2`` sweeps twice — reactively in ``_submit_one`` when a
    lodge hits the storage quota, and proactively between waves — and
    both are closures inside ``_execute_units_batch``, reachable only by
    standing up the whole batch pipeline. What makes them safe is
    structural and can be pinned directly: every sweep Phase 2 performs
    is ``sweep_stale_files_safe``, the function the rest of this section
    tests, and no line of ``run_phase2`` deletes a file itself. A new
    hand-rolled sweep, or a revert to the deprecated and unguarded
    ``sweep_stale_files``, fails here.
    """
    source = Path(__file__).resolve().parent.parent / "scripts" / "run_phase2.py"
    called = _called_names(ast.parse(source.read_text(encoding="utf-8")))

    assert "sweep_stale_files_safe" in called
    assert "sweep_stale_files" not in called
    assert not [name for name in called if name.endswith("files.delete")]


def test_verify_batch_sweeps_before_it_refuses(tmp_path, monkeypatch):
    """The verifier call site passes the sweep, not just the check.

    The wiring is what M6 unlocked, and section (f)'s lesson applies
    again: deleting ``sweep=make_safe_sweep(client)`` from
    ``run_pv._verify_batch`` leaves a guard that can only refuse, and a
    leg is lost to a project full of finished legs' inputs. The
    consequence asserted here is that the finished leg's input is
    reclaimed and this leg's chunk is uploaded.
    """
    import scripts.run_pv as run_pv

    client = _FakeClient(
        files=[_FakeFile("files/finished", 20 * _GIB, create_time=_STALE)],
        jobs=[_job("batches/done", "JOB_STATE_SUCCEEDED", "files/finished")],
    )

    def _build(*, manifest, config, output_path, crops_base_dir,
               temperature_override=None):
        output_path.write_bytes(b"x" * 4096)
        return len(manifest.get("candidates", []))

    monkeypatch.setattr(run_pv, "build_verifier_jsonl", _build)
    monkeypatch.setattr(run_pv, "load_system_instruction", lambda cfg: "sys")
    monkeypatch.setattr(run_pv, "_get_api_key", lambda: "test-key")
    monkeypatch.setattr(run_pv, "_resolve_model_name", lambda c, m: m)
    monkeypatch.setattr("google.genai.Client", lambda **kwargs: client)

    output_dir = tmp_path / "leg"
    run_pv._verify_batch(
        manifest={"candidates": [{"candidate_id": 1}]},
        config={"model": "gemini-3-flash"},
        crops_base_dir=tmp_path,
        output_dir=output_dir,
        iterations=1,
        temperature=None,
        dry_run=False,
        strict=False,
    )

    assert client.files.deleted == ["files/finished"]
    assert client.files.uploads == [str(output_dir / "verifier_requests.jsonl")]


def test_run_batch_unit_sweeps_before_it_refuses(tmp_path, monkeypatch):
    """The proposer call site, the same way.

    Without the sweep the unit is refused with the quota message; with it
    the idle input is freed and the unit reaches submission — here a
    sentinel that proves how far it got.
    """
    import scripts.lib_batch_api as lba

    client = _FakeClient(
        files=[_FakeFile("files/finished", 20 * _GIB, create_time=_STALE)],
        jobs=[_job("batches/done", "JOB_STATE_SUCCEEDED", "files/finished")],
    )
    ctx = lba.BatchUnitContext(
        unit_key="T1.0/run_1",
        unit={},
        output_file=tmp_path / "unit.geojson",
        jsonl_path=_chunk(tmp_path, "unit.jsonl", 4096),
        submitted_keys=["tile_001.png"],
        tile_paths=[tmp_path / "tile_001.png"],
        prompt_config={},
        model_name="gemini-3-flash",
        system_instruction="sys",
        config_version="v1",
        line_count=1,
    )

    def _submit(*args, **kwargs):
        raise RuntimeError("reached the submit step")

    monkeypatch.setattr(lba, "prepare_batch_unit", lambda **kwargs: ctx)
    monkeypatch.setattr(lba, "submit_batch_unit", _submit)
    monkeypatch.setattr(lba, "FILE_REGISTRY_PATH", _registry(tmp_path))

    success, message, _cost = lba.run_batch_unit(
        unit={}, config={}, output_dir=tmp_path / "out", client=client,
        model_name="gemini-3-flash", system_instruction="sys",
        examples=[], config_version="v1",
    )

    assert success is False
    assert message == "submit_error: reached the submit step"
    assert FILE_STORAGE_QUOTA_METRIC not in message
    assert client.files.deleted == ["files/finished"]
