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
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib_batch_api import (  # noqa: E402
    FILE_STORAGE_BUDGET_BYTES,
    FILE_STORAGE_CAP_BYTES,
    FILE_STORAGE_QUOTA_METRIC,
    FILE_STORAGE_SAFETY_MARGIN,
    FileStorageCapExceeded,
    is_file_storage_quota_error,
    preflight_file_storage,
)
from scripts.run_pv import run_batch_jobs  # noqa: E402

pytestmark = pytest.mark.tier1

_GIB = 1024 ** 3

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
    """One entry in the fake Files API listing."""

    def __init__(self, name: str, size_bytes: int) -> None:
        self.name = name
        self.size_bytes = size_bytes


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


class _FakeClient:
    """Minimal stand-in for ``google.genai.Client``."""

    def __init__(self, files: list[_FakeFile] | None = None) -> None:
        self.files = _FakeFilesApi(files or [])


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
    """21,474,836,480 bytes = 20 GiB, with a 5% preflight margin."""
    assert FILE_STORAGE_CAP_BYTES == 21_474_836_480
    assert FILE_STORAGE_SAFETY_MARGIN == pytest.approx(0.05)
    assert FILE_STORAGE_BUDGET_BYTES < FILE_STORAGE_CAP_BYTES
    assert FILE_STORAGE_BUDGET_BYTES == int(FILE_STORAGE_CAP_BYTES * 0.95)


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
