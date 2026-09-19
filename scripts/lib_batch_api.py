"""
Gemini Batch API Module
=======================

Description:
    Standalone module for Google Gemini Batch API interaction. Provides
    functions to build JSONL request files, upload them, submit batch jobs,
    poll for completion, retrieve and parse results, and write output files
    that match the concurrent pipeline's output contract exactly.

    The Batch API offers 50% cost reduction over synchronous requests with
    separate (higher) rate limits. Each batch job processes one execution
    unit (60 tiles), submitted as a single JSONL file via the Files API.

Batch API Lifecycle:
    1. Build JSONL → upload via Files API → create batch job
    2. Poll batches.get() until terminal state
    3. Download results file → parse JSONL response lines
    4. Convert to GeoJSON features → write output files

States: PENDING → RUNNING → SUCCEEDED / FAILED / CANCELLED / EXPIRED

Usage:
    from scripts.lib_batch_api import run_batch_unit

    result = run_batch_unit(
        unit=unit_dict,
        config=study_config,
        output_dir=output_path,
        client=genai_client,
        model_name="gemini-3-flash",
        system_instruction="...",
        examples=[...],
        config_version="detect_image-only",
    )

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import base64
import dataclasses
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Callable, Sequence
from typing import Any

import geojson
import rasterio
from shapely.geometry import box, mapping

from config import BASE_DIR, EXAMPLES_DIR, TILE_SIZE, TILES_DIR
from scripts.lib_llm_metadata import (  # noqa: E402
    BATCH_API_DISCOUNT,
    AggregatedUsage,
    LLMMetadataTracker,
    LLMProvider,
    estimate_cost,
    merge_meta,
    merge_meta_into_existing,
)

logger = logging.getLogger(__name__)

# Terminal states for batch jobs — polling stops when job reaches one of these.
# Values must match JobState enum .name / .value (not str(), which prepends
# the class name — e.g. "JobState.JOB_STATE_SUCCEEDED").
_TERMINAL_STATES = frozenset({
    "JOB_STATE_SUCCEEDED",
    "JOB_STATE_FAILED",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_EXPIRED",
    "JOB_STATE_PARTIALLY_SUCCEEDED",
})

# Script metadata for metadata tracker
__version__ = "1.5.0"

# Maximum tile-level failure RATE before a batch unit is rejected.
# Expressed as a fraction of submitted tiles. Individual failed tiles
# can be patched later via --patch-tiles mode. With HIGH thinking,
# ~14% of tiles produce truncated JSON; consensus voting (K=5)
# provides redundancy so per-pass failures are acceptable.
MAX_ACCEPTABLE_TILE_FAILURE_RATE = 0.20  # 20% tolerance

# Legacy absolute threshold — used as a floor so small batches
# (e.g., 60 tiles) still tolerate a few failures.
MIN_ACCEPTABLE_TILE_FAILURES = 10

# Maximum synchronous retry attempts for tiles that fail JSON parsing
# after a batch job completes. Empirically, ~74% resolve on attempt 1,
# ~98% by attempt 3. Set to 0 to skip retries entirely and defer to
# --patch-tiles or cleanup subcommand (recommended for large runs
# where consensus voting provides redundancy).
MAX_SYNC_RETRIES = 3

# Reduced max_output_tokens for safe-mode retries via --patch-tiles.
# Failures are caused by output truncation: the model's thinking
# tokens consume most of the 8192 budget, leaving ~188 tokens for
# visible JSON. Reducing to 2048 constrains thinking, preventing
# truncation. Only used as a last resort to preserve detection quality.
SAFE_MODE_MAX_OUTPUT_TOKENS = 2048


@dataclasses.dataclass
class BatchUnitContext:
    """
    Per-unit state carried between prepare/submit/complete phases.

    Created by ``prepare_batch_unit()`` and consumed by ``submit_batch_unit()``
    and ``complete_batch_unit()``. Decouples the three lifecycle phases so
    they can be orchestrated independently — e.g. prepare all units first,
    submit all, then poll all in a unified loop.
    """

    unit_key: str               # "T1.0/run_21"
    unit: dict                  # Original execution unit dict
    output_file: Path           # Target .geojson path
    jsonl_path: Path            # Built JSONL file path
    submitted_keys: list[str]   # Tile filenames (keys in batch response)
    tile_paths: list[Path]      # Full tile paths (for georeferencing)
    prompt_config: dict         # Prompt config with temperature overrides applied
    model_name: str             # Resolved model name
    system_instruction: str     # System instruction text
    config_version: str         # Config version string (for GeoJSON properties)
    line_count: int             # Lines written to JSONL
    tile_size: int = 512        # Tile dimension for normalised→pixel conversion
    examples: list[dict] = dataclasses.field(
        default_factory=list,
    )                           # Prompt examples (for parse-failure retry)


def _get_state_name(state: Any) -> str:
    """
    Extract the state name string from a JobState enum or string.

    The google-genai SDK returns ``JobState`` enum objects whose ``str()``
    representation includes the class name (e.g. ``"JobState.JOB_STATE_SUCCEEDED"``).
    This helper normalises to the bare name (``"JOB_STATE_SUCCEEDED"``) for
    comparison against ``_TERMINAL_STATES``.

    Args:
        state: A ``JobState`` enum member or plain string.

    Returns:
        The state name as a plain string.
    """
    # Enum objects have .name; plain strings (e.g. from mocks) do not
    if hasattr(state, "name"):
        return state.name
    return str(state)


# ─────────────────────────────────────────────────────────────────────
# File Storage Management
# ─────────────────────────────────────────────────────────────────────

# The Files API caps TOTAL stored bytes per project, and an uploaded
# request JSONL is retained for 30 days — so a campaign's uploads
# accumulate across legs whether or not the jobs that consumed them have
# finished. On 2026-09-19 14:05 UTC a 12-chunk verifier leg lodged 4
# chunks and then lost the remaining 8 to::
#
#     429 RESOURCE_EXHAUSTED ... Quota exceeded for metric:
#     generativelanguage.googleapis.com/file_storage_bytes,
#     limit: 21474836480 (quotaId: FileStorageBytesPerProject)
#
# against 45 stored uploads totalling 21.4 GB. The cap below is the
# limit that 429 reported: 21,474,836,480 bytes = 20 GiB.
FILE_STORAGE_QUOTA_METRIC = (
    "generativelanguage.googleapis.com/file_storage_bytes"
)
FILE_STORAGE_QUOTA_ID = "FileStorageBytesPerProject"
FILE_STORAGE_CAP_BYTES = 21_474_836_480

# Head-room withheld from the cap. The audit enumerates files at one
# instant and another process may upload between the audit and the
# lodge, so the preflight budgets against 95% of the cap rather than
# racing it to the last byte.
FILE_STORAGE_SAFETY_MARGIN = 0.05
FILE_STORAGE_BUDGET_BYTES = int(
    FILE_STORAGE_CAP_BYTES * (1.0 - FILE_STORAGE_SAFETY_MARGIN),
)

# Bytes per gibibyte — the unit audit_file_storage() reports in.
_GIB = 1024 ** 3

# The shared active-file registry every process on this project writes to.
# run_phase2.py builds the same path independently; keeping the canonical
# expression here means the uploads this module registers and the sweeps it
# runs address one file rather than two.
FILE_REGISTRY_PATH = BASE_DIR / "outputs" / ".active_files.json"


class FileStorageCapExceeded(RuntimeError):
    """
    Projected Files API usage would breach the per-project storage cap.

    Raised by :func:`preflight_file_storage` *before* any upload, so a
    leg that cannot fit fails without committing spend. The numbers are
    carried as attributes as well as in the message, so a caller can
    report them without re-parsing the string.

    Attributes:
        projected_bytes: Stored bytes plus the bytes about to be uploaded.
        budget_bytes: The cap less :data:`FILE_STORAGE_SAFETY_MARGIN`.
        cap_bytes: The quota limit itself.
    """

    def __init__(
        self,
        message: str,
        *,
        projected_bytes: int,
        budget_bytes: int = FILE_STORAGE_BUDGET_BYTES,
        cap_bytes: int = FILE_STORAGE_CAP_BYTES,
    ) -> None:
        super().__init__(message)
        self.projected_bytes = projected_bytes
        self.budget_bytes = budget_bytes
        self.cap_bytes = cap_bytes


def is_file_storage_quota_error(exc: BaseException) -> bool:
    """
    Recognise the Files API storage-quota 429 from any raised exception.

    The SDK surfaces quota breaches as a generic error whose message
    carries the metric name, so the message is the only reliable
    discriminator. Both the metric and the quota id are matched because
    the two appear in different parts of the same 429 body.

    Args:
        exc: Any exception raised by an upload or submission call.

    Returns:
        True when the exception names the file-storage quota — i.e. the
        failure is "the project is full", not a transient error.

    Examples:
        >>> is_file_storage_quota_error(RuntimeError(
        ...     "429 RESOURCE_EXHAUSTED ... metric: "
        ...     "generativelanguage.googleapis.com/file_storage_bytes"))
        True
        >>> is_file_storage_quota_error(RuntimeError("503 UNAVAILABLE"))
        False
    """
    text = str(exc)
    return (
        "file_storage_bytes" in text
        or FILE_STORAGE_QUOTA_ID in text
    )


def _largest_stored_files(
    client: Any,
    top_n: int = 5,
) -> list[tuple[str, int]]:
    """
    Enumerate the largest files currently held by the Files API.

    Called only on the failure path of :func:`preflight_file_storage`, to
    name the files an operator would delete first. Any enumeration error
    is swallowed: a diagnostic must never mask the quota error it exists
    to explain.

    Args:
        client: Initialised ``google.genai.Client``.
        top_n: How many files to name.

    Returns:
        ``(name, size_bytes)`` pairs, largest first, at most *top_n* long.
        Empty when the listing fails.
    """
    try:
        files = [
            (
                getattr(f, "name", "") or "<unnamed>",
                int(getattr(f, "size_bytes", 0) or 0),
            )
            for f in client.files.list()
        ]
    except Exception as exc:  # noqa: BLE001 - diagnostics are best-effort
        logger.debug("Could not enumerate files for diagnostics: %s", exc)
        return []

    files.sort(key=lambda item: item[1], reverse=True)
    return files[:top_n]


def preflight_file_storage(
    client: Any,
    jsonl_paths: Sequence[Path],
    *,
    log: logging.Logger | None = None,
    sweep: Callable[[], tuple[int, float]] | None = None,
) -> int | None:
    """
    Check projected Files API storage before a leg's first upload.

    Sums the local sizes of every request JSONL about to be uploaded,
    adds the bytes the project already holds (via
    :func:`audit_file_storage`), and compares the projection against
    :data:`FILE_STORAGE_BUDGET_BYTES`. The audit is logged at INFO on
    every call, so the run log always records what the leg believed the
    storage state to be.

    Over budget, an optional *sweep* is given one chance to free space
    and the storage is re-audited; still over, the call raises rather
    than letting the lodging loop discover the cap chunk by chunk (the
    2026-09-19 14:05 UTC incident, where 4 of 12 chunks lodged and 8
    died on a 429).

    **Build the sweep with** :func:`make_safe_sweep`. Its
    :func:`sweep_stale_files_safe` consults batch job state before it
    deletes anything, so no file that is the source of a non-terminal job
    can be swept, whichever process lodged it; and it aborts without
    deleting when it cannot see the jobs at all. Until 2026-09-20 the
    sweep protected only registry-listed and young files, and nothing on
    the verifier path registered its uploads — so passing it here would
    have deleted a concurrent leg's in-flight input (audit finding M6).
    Any other *sweep* must carry the same guarantee.

    An audit that cannot run (e.g. ``files.list()`` itself errors) is a
    warning, not a failure: the preflight is a guard on spend, not a
    gate on API health, and the per-chunk quota guard in the lodging
    loop still covers the blind case. This holds for the re-audit after
    a sweep as well — the pre-sweep numbers describe storage that no
    longer exists, so they are never used to refuse a leg.

    Args:
        client: Initialised ``google.genai.Client``.
        jsonl_paths: Every request file the leg is about to upload.
            Paths that do not exist contribute zero.
        log: Logger for the audit line (default: this module's logger).
        sweep: Optional zero-argument callable returning
            ``(deleted_count, freed_gb)``, invoked once when the
            projection is over budget. See the caveat above.

    Returns:
        The projected usage in bytes, or ``None`` when the audit could
        not be performed.

    Raises:
        FileStorageCapExceeded: When the projection is over budget and
            no sweep (or an insufficient sweep) brought it back under.
            Raised before any upload, so no spend is committed.

    Examples:
        >>> preflight_file_storage(client, [Path("chunk0.jsonl")])
        21474836  # projected bytes; INFO line written to the run log
    """
    log = log or logger

    pending_bytes = 0
    for path in jsonl_paths:
        try:
            pending_bytes += path.stat().st_size
        except OSError:
            # A chunk that is not on disk cannot be uploaded either; the
            # caller's own build step reports it.
            continue

    def _audit() -> tuple[int, int] | None:
        """Return ``(file_count, stored_bytes)``, or None if unavailable."""
        try:
            count, total_gb = audit_file_storage(client)
        except Exception as exc:  # noqa: BLE001 - audit must not be fatal
            log.warning(
                "File storage preflight skipped — could not audit the "
                "Files API (%s). Lodging proceeds unguarded; a %s 429 "
                "will be reported per chunk.",
                exc, FILE_STORAGE_QUOTA_METRIC,
            )
            return None
        # total_gb is stored_bytes / 2**30 — a power-of-two rescale, so
        # multiplying back recovers the byte count exactly.
        return count, int(round(total_gb * _GIB))

    audited = _audit()
    if audited is None:
        return None
    file_count, stored_bytes = audited
    projected = stored_bytes + pending_bytes

    log.info(
        "File storage preflight: %d file(s) stored (%.2f GB) + %d chunk(s) "
        "to upload (%.2f GB) = %.2f GB projected against a %.2f GB budget "
        "(%.2f GB cap less a %.0f%% margin)",
        file_count, stored_bytes / _GIB, len(jsonl_paths),
        pending_bytes / _GIB, projected / _GIB,
        FILE_STORAGE_BUDGET_BYTES / _GIB, FILE_STORAGE_CAP_BYTES / _GIB,
        FILE_STORAGE_SAFETY_MARGIN * 100,
    )

    if projected <= FILE_STORAGE_BUDGET_BYTES:
        return projected

    if sweep is not None:
        deleted, freed_gb = sweep()
        log.warning(
            "File storage over budget (%.2f GB projected) — swept %d "
            "file(s), freeing %.2f GB; re-auditing",
            projected / _GIB, deleted, freed_gb,
        )
        audited = _audit()
        if audited is None:
            # The re-audit is the only account of what the sweep freed.
            # Without it the pre-sweep numbers describe storage that no
            # longer exists, so refusing on them would be a lie; warn and
            # proceed, exactly as an unavailable first audit does.
            return None
        file_count, stored_bytes = audited
        projected = stored_bytes + pending_bytes
        log.info(
            "File storage after sweep: %d file(s), %.2f GB projected",
            file_count, projected / _GIB,
        )
        if projected <= FILE_STORAGE_BUDGET_BYTES:
            return projected

    largest = _largest_stored_files(client)
    if largest:
        largest_text = "; largest stored files: " + ", ".join(
            f"{name} ({size / _GIB:.2f} GB)" for name, size in largest
        )
    else:
        largest_text = ""
    message = (
        f"Files API storage cap would be exceeded — nothing uploaded, no "
        f"spend committed. Metric {FILE_STORAGE_QUOTA_METRIC} "
        f"(quotaId {FILE_STORAGE_QUOTA_ID}): projected {projected:,} bytes "
        f"({projected / _GIB:.2f} GB) = {file_count} stored file(s) "
        f"({stored_bytes / _GIB:.2f} GB) + {len(jsonl_paths)} chunk(s) to "
        f"upload ({pending_bytes / _GIB:.2f} GB), against a cap of "
        f"{FILE_STORAGE_CAP_BYTES:,} bytes "
        f"({FILE_STORAGE_CAP_BYTES / _GIB:.2f} GB) and a preflight budget "
        f"of {FILE_STORAGE_BUDGET_BYTES:,} bytes "
        f"({FILE_STORAGE_BUDGET_BYTES / _GIB:.2f} GB){largest_text}. "
        f"Uploads are retained for 30 days: delete the stale ones "
        f"(cleanup_batch_files) and re-run; audit_file_storage() reports "
        f"current usage."
    )
    log.error("%s", message)
    raise FileStorageCapExceeded(message, projected_bytes=projected)


def register_upload(
    file_name: str,
    *,
    registry_path: Path | None = None,
    unit_key: str = "",
    study_name: str = "",
) -> None:
    """
    Record an upload in the shared registry, best-effort.

    The registry is the *belt* of the two-part sweep guard (the braces are
    batch job state — see :func:`active_batch_input_files`), so a registry
    that cannot be written must never fail an upload that has already
    succeeded and is already billing storage. Every failure is logged and
    swallowed.

    Args:
        file_name: Files API resource name, e.g. ``"files/abc123"``.
        registry_path: Registry to write (default
            :data:`FILE_REGISTRY_PATH`).
        unit_key: Execution unit that owns the upload, for diagnostics.
        study_name: Study name, for diagnostics.
    """
    if not file_name:
        return
    path = Path(registry_path) if registry_path is not None else FILE_REGISTRY_PATH
    try:
        from scripts.lib_file_registry import register_file

        register_file(path, file_name, unit_key=unit_key, study_name=study_name)
    except Exception as exc:  # noqa: BLE001 - registration is best-effort
        logger.warning(
            "Could not register uploaded file %s in %s: %s — a concurrent "
            "sweep now relies on batch job state alone to protect it",
            file_name, path, exc,
        )


def deregister_upload(
    file_name: str,
    *,
    registry_path: Path | None = None,
) -> None:
    """
    Remove a file from the shared registry, best-effort.

    Called as a file is deleted, so a stale entry cannot outlive the file
    it protects. Deregistering *before* the delete attempt is deliberate
    and matches ``run_phase2``'s ordering: if the delete fails the file
    auto-expires, whereas a registry entry for a deleted file would block
    every later sweep from reclaiming its name.

    Args:
        file_name: Files API resource name.
        registry_path: Registry to write (default
            :data:`FILE_REGISTRY_PATH`).
    """
    if not file_name:
        return
    path = Path(registry_path) if registry_path is not None else FILE_REGISTRY_PATH
    try:
        from scripts.lib_file_registry import deregister_file

        deregister_file(path, file_name)
    except Exception as exc:  # noqa: BLE001 - deregistration is best-effort
        logger.warning(
            "Could not deregister file %s from %s: %s", file_name, path, exc,
        )


def cleanup_batch_files(
    client: Any,
    file_names: list[str],
    label: str = "",
    *,
    registry_path: Path | None = None,
) -> tuple[int, int]:
    """
    Delete files from the Gemini Files API.

    Iterates the given file names and deletes each one. Exceptions are
    caught per file (logged and continued) so that a single deletion
    failure does not prevent cleanup of the remaining files. Files that
    fail to delete will auto-expire after 48 hours as a fallback.

    Known issue (#1759): some output file IDs exceed the 40-character
    limit for ``files.delete()``. These are caught and logged rather
    than crashing.

    Args:
        client: Initialised ``google.genai.Client``.
        file_names: List of file resource names (e.g. ``"files/abc123"``).
        label: Optional label for log messages (e.g. ``"input"``
            or ``"output"``).
        registry_path: Shared registry to deregister each deleted file
            from (default :data:`FILE_REGISTRY_PATH`). Deregistration is
            best-effort and never blocks a deletion.

    Returns:
        Tuple of ``(deleted_count, error_count)``.
    """
    prefix = f"[{label}] " if label else ""
    deleted = 0
    errors = 0

    for name in file_names:
        if not name:
            continue
        # Deregister first: a registry entry that outlives its file would
        # protect a name that no longer exists from every future sweep.
        deregister_upload(name, registry_path=registry_path)
        try:
            client.files.delete(name=name)
            deleted += 1
            logger.debug("%sDeleted file: %s", prefix, name)
        except Exception as e:
            errors += 1
            logger.warning(
                "%sFailed to delete file %s: %s", prefix, name, e,
            )

    if deleted or errors:
        logger.info(
            "%sFile cleanup: %d deleted, %d errors",
            prefix, deleted, errors,
        )

    return deleted, errors


def audit_file_storage(client: Any) -> tuple[int, float]:
    """
    Query current file storage usage from the Gemini Files API.

    Iterates ``files.list()`` and sums ``size_bytes`` for each file.
    There is no dedicated API endpoint for querying storage usage, so
    this enumeration approach is the only option.

    Args:
        client: Initialised ``google.genai.Client``.

    Returns:
        Tuple of ``(file_count, total_gb)``.

    Raises:
        Exception: If ``files.list()`` fails (e.g. when quota is
            already exceeded). Callers should handle this gracefully.
    """
    total_bytes = 0
    count = 0

    for f in client.files.list():
        count += 1
        total_bytes += getattr(f, "size_bytes", 0) or 0

    total_gb = total_bytes / (1024 ** 3)
    logger.info(
        "File storage audit: %d files, %.2f GB", count, total_gb,
    )
    return count, total_gb


def sweep_stale_files(
    client: Any,
    active_file_names: set[str],
) -> tuple[int, float]:
    """
    Delete files not in the active set — orphan cleanup.

    .. deprecated::
        Use :func:`sweep_stale_files_safe` instead. This function builds
        the active set from a single process's ``batch_pending`` dict,
        which causes 404 errors when multiple processes share the same
        Google Files API account (each process sees other processes'
        files as orphans).

    Lists all files via the Files API and deletes any whose name is
    not in ``active_file_names``. This cleans up files from previous
    runs, failed submissions, or downloaded-but-not-deleted outputs.

    Args:
        client: Initialised ``google.genai.Client``.
        active_file_names: Set of file names that are still needed
            (e.g. input files for pending batch jobs).

    Returns:
        Tuple of ``(deleted_count, freed_gb)``.
    """
    stale_names: list[str] = []
    stale_bytes = 0

    try:
        for f in client.files.list():
            name = getattr(f, "name", "")
            if name and name not in active_file_names:
                stale_names.append(name)
                stale_bytes += getattr(f, "size_bytes", 0) or 0
    except Exception as e:
        logger.warning("Could not list files for sweep: %s", e)
        return 0, 0.0

    if not stale_names:
        logger.info("Sweep: no stale files found")
        return 0, 0.0

    freed_gb = stale_bytes / (1024 ** 3)
    logger.info(
        "Sweep: found %d stale files (%.2f GB), deleting...",
        len(stale_names), freed_gb,
    )

    deleted, _errors = cleanup_batch_files(
        client, stale_names, label="sweep",
    )
    return deleted, freed_gb


def active_batch_input_files(client: Any) -> set[str]:
    """
    Enumerate the input files of every batch job that has not finished.

    A batch job reads its request JSONL from the Files API for as long as
    it is alive, and the Files API offers no back-reference from a file to
    the job consuming it. The only way to know that a file is in use is to
    ask the batches service which jobs are still running and what each
    one's source file is.

    This is the **primary** guard on :func:`sweep_stale_files_safe`, and it
    is independent of the shared registry: it sees jobs lodged by any
    process on the project, whether or not that process registered its
    upload. A job in any non-terminal state protects its source file; a
    job in one of :data:`_TERMINAL_STATES` protects nothing, because its
    input is exactly what a sweep exists to reclaim.

    Args:
        client: Initialised ``google.genai.Client``.

    Returns:
        The Files API resource names (``"files/abc123"``) that are the
        source of at least one non-terminal batch job.

    Raises:
        Exception: Whatever ``client.batches.list()`` raises. A caller
            that cannot see the jobs cannot tell an idle file from an
            in-flight one and must delete nothing — see
            :func:`sweep_stale_files_safe`.
    """
    protected: set[str] = set()
    for job in client.batches.list():
        if _get_state_name(getattr(job, "state", "")) in _TERMINAL_STATES:
            continue
        src = getattr(job, "src", None)
        # SDK shape (google-genai 1.73.1): ``BatchJob.src`` is a
        # ``BatchJobSource`` whose ``file_name`` is the uploaded request
        # JSONL. Submission passes the resource name as a bare string
        # (see submit_batch_job), so tolerate both spellings.
        file_name = src if isinstance(src, str) else getattr(src, "file_name", None)
        if file_name:
            protected.add(str(file_name))
    return protected


def sweep_stale_files_safe(
    client: Any,
    registry_path: Path,
    grace_minutes: float = 5.0,
) -> tuple[int, float]:
    """
    Concurrency-safe orphan cleanup, guarded by batch job state.

    Safe to call from any process. A file is deleted only when all three
    of the following hold:

    1. **No live job is reading it.** ``client.batches.list()`` is
       consulted first and the source file of every non-terminal job is
       protected (:func:`active_batch_input_files`). This is the guard
       that does not depend on anyone's bookkeeping, and it is why the
       sweep is safe to pass to :func:`preflight_file_storage`.
    2. **It is not in the shared registry** at ``registry_path``, which
       every upload through :func:`upload_jsonl` writes to.
    3. **It is older than** ``grace_minutes``, which covers the window
       between an upload completing and its job being lodged — a file
       that exists but has no job yet is invisible to guard (1).

    If the batches listing itself fails the sweep **deletes nothing** and
    says so: a sweep that cannot see the jobs cannot tell an idle file
    from an in-flight one, and the failure mode it would otherwise
    produce — a concurrent leg's input deleted underneath a running job,
    which fails server-side with no local error — is far worse than a
    storage cap hit (audit finding M6, 2026-09-20).

    Args:
        client: Initialised ``google.genai.Client``.
        registry_path: Path to the shared ``.active_files.json``.
        grace_minutes: Files younger than this are always preserved,
            regardless of registry state. Default 5 minutes.

    Returns:
        Tuple of ``(deleted_count, freed_gb)``. ``(0, 0.0)`` when the
        sweep aborted without deleting anything.
    """
    from datetime import datetime, timezone

    from scripts.lib_file_registry import get_registered_files

    # Guard 1 — batch job state. Independent of every process's
    # bookkeeping, so it protects uploads nobody registered.
    try:
        in_flight = active_batch_input_files(client)
    except Exception as e:
        logger.warning(
            "Safe sweep aborted — could not list batch jobs (%s), so an "
            "in-flight job's input cannot be told from an orphan. "
            "Nothing deleted.", e,
        )
        return 0, 0.0

    # Guard 2 — the set of files registered by all processes.
    try:
        registered = get_registered_files(
            registry_path, prune_stale=True,
        )
    except Exception as e:
        logger.warning(
            "Could not read file registry for sweep: %s", e,
        )
        return 0, 0.0

    now = datetime.now(timezone.utc)
    grace_seconds = grace_minutes * 60
    stale_names: list[str] = []
    stale_bytes = 0

    try:
        for f in client.files.list():
            name = getattr(f, "name", "")
            if not name:
                continue

            # A live job is reading this file — never delete it
            if name in in_flight:
                continue

            # Registered files are always preserved
            if name in registered:
                continue

            # Recent files are preserved (grace period).
            # Ensure timezone-aware comparison — API may return
            # naive or aware datetimes depending on SDK version.
            create_time = getattr(f, "create_time", None)
            if create_time:
                if create_time.tzinfo is None:
                    create_time = create_time.replace(
                        tzinfo=timezone.utc,
                    )
                age_seconds = (now - create_time).total_seconds()
                if age_seconds < grace_seconds:
                    continue

            stale_names.append(name)
            stale_bytes += getattr(f, "size_bytes", 0) or 0
    except Exception as e:
        logger.warning(
            "Could not list files for safe sweep: %s", e,
        )
        return 0, 0.0

    if not stale_names:
        logger.info("Safe sweep: no stale files found")
        return 0, 0.0

    freed_gb = stale_bytes / (1024 ** 3)
    logger.info(
        "Safe sweep: found %d stale files (%.2f GB), "
        "%d in-flight and %d registered (protected), deleting...",
        len(stale_names), freed_gb, len(in_flight), len(registered),
    )

    deleted, _errors = cleanup_batch_files(
        client, stale_names, label="safe-sweep",
        registry_path=registry_path,
    )
    return deleted, freed_gb


def make_safe_sweep(
    client: Any,
    registry_path: Path | None = None,
    grace_minutes: float = 5.0,
) -> Callable[[], tuple[int, float]]:
    """
    Build the zero-argument sweep callable :func:`preflight_file_storage` takes.

    The preflight's ``sweep=`` hook is deliberately zero-argument so the
    guard itself knows nothing about registries or job state. This factory
    is the one blessed way to fill it: it binds
    :func:`sweep_stale_files_safe`, which never deletes the input of a
    live batch job, to this project's shared registry.

    Args:
        client: Initialised ``google.genai.Client``.
        registry_path: Shared registry (default
            :data:`FILE_REGISTRY_PATH`).
        grace_minutes: Passed through to the sweep.

    Returns:
        A callable returning ``(deleted_count, freed_gb)``.

    Examples:
        >>> preflight_file_storage(client, paths, sweep=make_safe_sweep(client))
        18253611008
    """
    path = Path(registry_path) if registry_path is not None else FILE_REGISTRY_PATH

    def _sweep() -> tuple[int, float]:
        """Free provably idle Files API storage; see the factory's docstring."""
        return sweep_stale_files_safe(client, path, grace_minutes=grace_minutes)

    return _sweep


# ─────────────────────────────────────────────────────────────────────
# JSONL Construction
# ─────────────────────────────────────────────────────────────────────


def _encode_image_base64(image_path: Path) -> str:
    """
    Read an image file and return its base64-encoded contents.

    Args:
        image_path: Path to the image file.

    Returns:
        Base64-encoded string of the image bytes.
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _mime_type_for(path: Path) -> str:
    """Return the MIME type for an image path based on its suffix."""
    return "image/png" if path.suffix.lower() == ".png" else "image/jpeg"


def _build_reference_parts(
    examples: list[dict],
    include_images: bool = True,
) -> list[dict]:
    """
    Build the reference example content parts for a JSONL request line.

    Mirrors the reference_parts construction in
    ``4_detect_mounds_batch.py:detect_mounds_versioned()`` but serialises
    to JSON dicts (for JSONL) rather than SDK ``types.Part`` objects.

    Args:
        examples: List of example dicts from the prompt config, each
            with 'path', 'label', and 'category' fields.
        include_images: Whether to include example images (False for
            text-only conditions like H1 brief-text/verbose-text).

    Returns:
        List of content part dicts suitable for JSONL serialisation.
    """
    if not include_images:
        return []

    parts: list[dict] = []
    for ex in examples:
        label = ex.get("label", "Example")
        path_str = ex.get("path", "")
        img_path = EXAMPLES_DIR / path_str

        if img_path.exists():
            parts.append({"text": label})
            parts.append({
                "inline_data": {
                    "mime_type": _mime_type_for(img_path),
                    "data": _encode_image_base64(img_path),
                }
            })
        else:
            logger.warning("Reference image not found: %s", path_str)

    return parts


#: Minimum tokens an EXPLICIT context cache accepts, measured 2026-09-17 from
#: the API's own rejection: "Cached content is too small. total_token_count=387,
#: min_total_token_count=1024". Implicit caching's floor is four times higher
#: (4,096 on Gemini 3.5-3.8 Flash, per the caching documentation), which is why
#: the explicit route can cache prompts the implicit one ignores.
EXPLICIT_CACHE_MIN_TOKENS = 1024

#: Lines a DRY RUN writes per chunk. The rehearsal exists to prove the request
#: shape, and a few lines prove it as well as 4,000 do; writing the real file
#: cost 1.34 GB per chunk and 7.6 GB per pass before this cap.
DRY_RUN_JSONL_LINES = 5

#: Implicit caching's floor on the Gemini 3.5-3.8 Flash line, for comparison.
IMPLICIT_CACHE_MIN_TOKENS = 4096


def create_shared_context_cache(
    client: Any,
    model_name: str,
    system_instruction: str,
    examples: list[dict],
    include_images: bool = True,
    ttl_seconds: int = 86400,
) -> tuple[str | None, int]:
    """Create an explicit context cache holding the prompt's shared prefix.

    Every request in a detection batch repeats the same preamble — the system
    instruction, the "Reference Symbols" line and the example images — and
    only the transition text and the tile image differ. Caching that prefix
    once and referencing it per request is the arrangement the Batch API
    documents: "Context caching is supported for batch requests. Reuse cached
    content by specifying the cached_content resource name in the
    configuration of individual requests within your batch."

    Pricing, per the same documentation: a cache hit bills at the standard
    context-caching rate and the 50 % batch discount does NOT apply on top of
    it, while tokens that miss the cache do get the batch discount. The two
    are complementary rather than multiplicative, which
    ``scripts/audit_proposer_cost.py`` already models by leaving the cache
    rate undiscounted by tier.

    TTL matters more here than in the real-time path. Batch jobs target a
    24-hour turnaround, so the one-hour TTL used by
    ``4_detect_mounds_batch.py`` would expire mid-job and silently revert the
    remaining requests to the full input rate — the failure would show up only
    as a bill. The default is therefore 24 hours. Storage is billed per token
    per hour but the prefix is small (of order 16k tokens), so a day of
    storage costs well under a dollar against the tens of dollars the cache
    saves.

    The cache's contents MIRROR the inline assembly in
    :func:`build_jsonl_file` exactly, so a cached request and an inline one
    present the model with the same context in the same order.

    Args:
        client: A ``google.genai`` client.
        model_name: Model the cache is bound to. A cache is model-specific.
        system_instruction: System instruction text.
        examples: Example dicts from the prompt config.
        include_images: Whether example IMAGES are transmitted (text-only
            conditions still send the labels).
        ttl_seconds: Cache lifetime. Must exceed the expected job duration.

    Returns:
        ``(cache_resource_name, cached_token_count)``, or ``(None, 0)`` if the
        cache could not be created — the caller should then fall back to
        inline assembly rather than submit requests naming a cache that does
        not exist.
    """
    from google.genai import types

    reference_parts = _build_reference_parts(examples, include_images)
    cache_parts: list[dict] = [
        {"text": "Here are the Reference Symbols you must find:"},
    ]
    cache_parts.extend(reference_parts)

    # Size check BEFORE the call, so a prefix that cannot be cached is a
    # logged decision rather than a caught exception. Measured floors
    # (2026-09-17): explicit caching needs >= 1,024 tokens — the API rejects
    # less with "Cached content is too small. min_total_token_count=1024" —
    # while implicit caching on Gemini 3.5-3.8 Flash needs >= 4,096. A prefix
    # between the two is cached ONLY if asked for explicitly, which is the
    # main reason to prefer the explicit route.
    #
    # This project's own prefixes sit at the extremes: the image config's is
    # 18,909 tokens and caches under either scheme; the text-only config's is
    # 393 and can be cached by neither, because the whole shared prefix is one
    # short instruction. Text-only legs therefore run uncached by nature, not
    # by oversight, and their audits correctly show cache=0.000.
    try:
        prefix_tokens = client.models.count_tokens(
            model=model_name,
            contents=[types.Content(parts=[{"text": system_instruction}], role="user"),
                      types.Content(parts=cache_parts, role="user")],
        ).total_tokens
    except Exception:                                          # noqa: BLE001
        prefix_tokens = None
    if not isinstance(prefix_tokens, int):
        # A non-integer count tells us nothing; proceed and let the API decide
        # rather than block on an unusable measurement.
        prefix_tokens = None

    if prefix_tokens is not None and prefix_tokens < EXPLICIT_CACHE_MIN_TOKENS:
        logger.info(
            "shared prefix is %s tokens, below the %s-token explicit-cache "
            "minimum — running uncached (inline assembly); this is expected "
            "for text-only configs",
            f"{prefix_tokens:,}", f"{EXPLICIT_CACHE_MIN_TOKENS:,}",
        )
        return None, 0

    try:
        cached = client.caches.create(
            model=model_name,
            config=types.CreateCachedContentConfig(
                system_instruction=system_instruction,
                contents=[types.Content(parts=cache_parts, role="user")],
                display_name="batch-detect-shared-prefix",
                ttl=f"{ttl_seconds}s",
            ),
        )
    except Exception as exc:                                   # noqa: BLE001
        logger.warning("context cache creation failed (%s): %s",
                       type(exc).__name__, exc)
        return None, 0

    um = getattr(cached, "usage_metadata", None)
    tokens = getattr(um, "total_token_count", 0) if um else 0
    logger.info("context cache created: %s (%s tokens, ttl %ss)",
                cached.name, f"{tokens:,}", ttl_seconds)
    return cached.name, tokens


def build_jsonl_file(
    tile_paths: list[Path],
    config: dict,
    system_instruction: str,
    examples: list[dict],
    output_path: Path,
    cached_content: str | None = None,
) -> int:
    """
    Build a JSONL request file for one execution unit.

    Each line contains one tile's complete request. By default the shared
    preamble — system instruction, the "Reference Symbols" line and the
    example images — is duplicated on every line. Passing *cached_content*
    instead names a context cache holding that preamble, and each line then
    carries only its transition text and tile image.

    (An earlier version of this docstring stated that "the Batch API has no
    shared-context mechanism". That is no longer true, and was the reason this
    path duplicated a ~16k-token prefix on every request: the API documents
    "Context caching is supported for batch requests. Reuse cached content by
    specifying the cached_content resource name in the configuration of
    individual requests within your batch.")

    Args:
        tile_paths: List of tile image paths to process.
        config: Prompt config dict (temperature, max_output_tokens, etc.).
        system_instruction: System instruction text. Omitted from each line
            when *cached_content* is given, because it lives in the cache.
        examples: List of example dicts from prompt config.
        output_path: Where to write the JSONL file.
        cached_content: Resource name of a context cache created by
            :func:`create_shared_context_cache`, or None for inline assembly.
            The cache must be bound to the SAME model the batch names.

    Returns:
        Number of lines written.

    JSONL line format:
        {"key": "tile_name.png", "request": {"contents": [...],
         "system_instruction": {...}, "generation_config": {...}}}
    """
    include_images = config.get("include_example_images", True)
    reference_parts = _build_reference_parts(examples, include_images)

    # Build generation config matching the concurrent pipeline's settings
    generation_config: dict[str, Any] = {
        "temperature": config.get("temperature", 0.1),
        "max_output_tokens": config.get("max_output_tokens", 8192),
        "response_mime_type": "application/json",
    }

    # Thinking config: must be nested INSIDE generation_config for
    # batch JSONL (unlike the standard SDK where it's a sibling).
    # Empirically verified 2026-02-15: request-level placement is
    # rejected with INVALID_ARGUMENT, but generation_config nesting
    # is accepted and produces thoughtsTokenCount in the response.
    # Config files store lowercase (e.g. "minimal"); the JSONL
    # protobuf schema requires uppercase enum names ("MINIMAL").
    thinking_level = config.get("thinking_level")
    if thinking_level:
        # Validated here rather than at submission: this is the last point at
        # which the model and the level are both in hand before 24,561
        # requests are written to disk.
        validate_thinking_level(config.get("model", ""), thinking_level)
        generation_config["thinking_config"] = {
            "thinking_level": thinking_level.upper(),
        }

    # Note: safety_settings are NOT included in batch JSONL.
    # The Gemini Batch API rejects requests containing
    # safety_settings with INVALID_ARGUMENT. The batch backend
    # applies default safety settings (no blocking). The
    # concurrent pipeline sets safety_settings via the SDK, but
    # the batch path cannot.

    line_count = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for tile_path in tile_paths:
            # Build content parts for this tile — mirrors the concurrent
            # pipeline's prompt assembly in 4_detect_mounds_batch.py
            # process_single_tile() (lines 312-322). The preamble is
            # always included, even for text-only conditions where
            # reference_parts is empty, to maintain prompt parity.
            content_parts: list[dict] = []

            # Reference examples preamble. Skipped when a context cache holds
            # it: repeating it here would both defeat the cache and present
            # the model with the preamble twice.
            if cached_content is None:
                content_parts.append({
                    "text": "Here are the Reference Symbols you must find:",
                })
                content_parts.extend(reference_parts)

            # Transition text
            content_parts.append({
                "text": (
                    "Now, find detection instances that visually match "
                    "ANY of the above Reference Examples in the Target "
                    "Map Tile below:"
                ),
            })

            # Tile image
            content_parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": _encode_image_base64(tile_path),
                }
            })

            # Assemble the JSONL line
            request: dict[str, Any] = {
                "contents": [
                    {
                        "parts": content_parts,
                        "role": "user",
                    }
                ],
                "generation_config": generation_config,
            }
            if cached_content is None:
                request["system_instruction"] = {
                    "parts": [{"text": system_instruction}],
                }
            else:
                # The cache carries the system instruction; naming both is
                # rejected by the API.
                request["cached_content"] = cached_content
            line = {"key": tile_path.name, "request": request}

            f.write(json.dumps(line) + "\n")
            line_count += 1

    logger.info("Built JSONL with %d lines: %s", line_count, output_path)
    return line_count


# ─────────────────────────────────────────────────────────────────────
# Batch Job Lifecycle
# ─────────────────────────────────────────────────────────────────────


def upload_jsonl(
    client: Any,
    jsonl_path: Path,
    display_name: str | None = None,
    *,
    registry_path: Path | None = None,
    unit_key: str = "",
    study_name: str = "",
) -> str:
    """
    Upload a JSONL file via the Google Files API and register it.

    Every upload is recorded in the shared active-file registry before
    this returns, so a sweep run by any other process on the project sees
    the file as in use during the window between the upload completing
    and its batch job being lodged — the one window batch job state
    cannot cover. Registration is best-effort: a registry that cannot be
    written is logged, not raised, because the upload has already
    happened and is already consuming the storage cap.

    Args:
        client: Initialised ``google.genai.Client``.
        jsonl_path: Path to the local JSONL file.
        display_name: Optional human-readable name for the upload.
        registry_path: Shared registry to record the upload in (default
            :data:`FILE_REGISTRY_PATH`).
        unit_key: Execution unit that owns the upload, recorded in the
            registry for diagnostics.
        study_name: Study name, recorded in the registry for diagnostics.

    Returns:
        The uploaded file's name (resource identifier for batch creation).
    """
    if display_name is None:
        display_name = jsonl_path.stem

    uploaded = client.files.upload(
        file=jsonl_path,
        config={"display_name": display_name, "mime_type": "jsonl"},
    )
    logger.info("Uploaded JSONL as: %s", uploaded.name)
    register_upload(
        uploaded.name, registry_path=registry_path,
        unit_key=unit_key or display_name, study_name=study_name,
    )
    return uploaded.name


def submit_batch_job(
    client: Any,
    model: str,
    uploaded_file_name: str,
    display_name: str | None = None,
) -> Any:
    """
    Create a batch job from an uploaded JSONL file.

    Args:
        client: Initialised ``google.genai.Client``.
        model: Model name (e.g., 'gemini-3-flash').
        uploaded_file_name: Resource name from ``upload_jsonl()``.
        display_name: Optional display name for the batch job.

    Returns:
        BatchJob object from the API.
    """
    # SDK v1.x accepts the uploaded file name directly as src,
    # inferring JSONL format from the file metadata. The older
    # BatchJobSource(format="JSONL") was removed in recent SDK
    # versions — passing the string is the current API contract.
    batch_job = client.batches.create(
        model=model,
        src=uploaded_file_name,
        config={"display_name": display_name or "batch-unit"},
    )
    logger.info("Submitted batch job: %s", batch_job.name)
    return batch_job


def poll_batch_job(
    client: Any,
    job_name: str,
    interval_seconds: float = 30.0,
    max_hours: float = 25.0,
    progress_callback: Any | None = None,
    max_consecutive_errors: int = 20,
) -> Any:
    """
    Poll a batch job until it reaches a terminal state.

    Args:
        client: Initialised ``google.genai.Client``.
        job_name: Batch job resource name (e.g., 'batches/123456').
        interval_seconds: Seconds between poll attempts.
        max_hours: Maximum hours to poll before giving up.
        progress_callback: Optional callable invoked with the BatchJob
            object on each poll iteration (for logging/progress bars).
        max_consecutive_errors: Transient errors from the polling endpoint
            tolerated in a row before the error propagates.

    Returns:
        The BatchJob in its terminal state.

    Raises:
        TimeoutError: If ``max_hours`` exceeded without reaching
            a terminal state.
    """
    max_seconds = max_hours * 3600
    start = time.monotonic()
    consecutive_errors = 0

    while True:
        # A 503 (or any transient error) on the POLLING endpoint says nothing
        # about the job, which keeps running on the service side. Until
        # 2026-09-19 it propagated and the caller wrote the chunk off; the
        # S154 note that "a 503 while polling does not mean the job failed"
        # was learnt the expensive way. Tolerate up to max_consecutive_errors
        # in a row (20 x 30 s = 10 min of a dead endpoint) before giving up.
        try:
            job = client.batches.get(name=job_name)
        except Exception as exc:  # noqa: BLE001 - transient endpoint errors
            consecutive_errors += 1
            if consecutive_errors > max_consecutive_errors:
                raise
            logger.warning("poll of %s failed (%d/%d in a row): %s — retrying",
                           job_name, consecutive_errors, max_consecutive_errors, exc)
            time.sleep(interval_seconds)
            continue
        consecutive_errors = 0
        state = _get_state_name(job.state)

        if progress_callback:
            progress_callback(job)

        if state in _TERMINAL_STATES:
            logger.info(
                "Batch job %s reached terminal state: %s",
                job_name, state,
            )
            return job

        elapsed = time.monotonic() - start
        if elapsed >= max_seconds:
            raise TimeoutError(
                f"Batch job {job_name} did not complete within "
                f"{max_hours} hours (state: {state})"
            )

        remaining = max_seconds - elapsed
        sleep_time = min(interval_seconds, remaining)
        if sleep_time > 0:
            time.sleep(sleep_time)


def poll_all_batch_jobs(
    client: Any,
    jobs: dict[str, str],
    interval_seconds: float = 30.0,
    max_hours: float = 25.0,
    on_complete: Callable[[str, str, Any], None] | None = None,
    progress_callback: Callable[[int, int, float], None] | None = None,
) -> dict[str, Any]:
    """
    Poll multiple batch jobs in a unified loop until all reach terminal states.

    This is the core of the parallel batch approach — instead of polling one
    job at a time (blocking), it checks all pending jobs each cycle and
    processes completions incrementally via the ``on_complete`` callback.

    Rate limit safety: 70 jobs × ~200ms per ``get()`` ≈ 14s per cycle.
    With 30s sleep, ~95 Requests Per Minute (RPM) for ``batches.get()``
    — well within API limits.

    Args:
        client: Initialised ``google.genai.Client``.
        jobs: Mapping of unit_key → batch job resource name.
        interval_seconds: Seconds between poll cycles.
        max_hours: Maximum hours before raising ``TimeoutError``.
        on_complete: Callback invoked when a job reaches a terminal state.
            Signature: ``(unit_key, job_name, batch_job) → None``.
            Called once per job, in the order jobs complete.
        progress_callback: Optional callback for cycle-level reporting.
            Signature: ``(n_completed, n_total, elapsed_seconds) → None``.

    Returns:
        Dict mapping unit_key → terminal ``BatchJob`` object for all jobs.

    Raises:
        TimeoutError: If ``max_hours`` exceeded with jobs still pending.
            Unfinished jobs remain in the caller's checkpoint for resume.
    """
    if not jobs:
        return {}

    max_seconds = max_hours * 3600
    start = time.monotonic()

    pending = dict(jobs)  # Copy — entries removed as they complete
    completed: dict[str, Any] = {}

    while pending:
        # Poll each pending job once per cycle. Transient API errors
        # (503, network timeout, etc.) are logged and the job is treated
        # as still pending — it will be retried next cycle rather than
        # crashing the entire polling loop.
        for key, job_name in list(pending.items()):
            try:
                job = client.batches.get(name=job_name)
            except Exception as e:
                logger.warning(
                    "Transient error polling %s (%s), will retry: %s",
                    job_name, key, e,
                )
                continue

            state = _get_state_name(job.state)

            if state in _TERMINAL_STATES:
                completed[key] = job
                del pending[key]
                logger.info(
                    "Batch job %s (%s) reached terminal state: %s",
                    job_name, key, state,
                )
                if on_complete:
                    on_complete(key, job_name, job)

        # If all done after this cycle, exit before sleeping
        if not pending:
            break

        # Progress report
        elapsed = time.monotonic() - start
        if progress_callback:
            progress_callback(
                len(completed), len(completed) + len(pending), elapsed,
            )

        # Timeout check
        if elapsed >= max_seconds:
            pending_keys = list(pending.keys())
            raise TimeoutError(
                f"{len(pending)} batch job(s) did not complete within "
                f"{max_hours} hours: {pending_keys[:5]}"
            )

        remaining = max_seconds - elapsed
        sleep_time = min(interval_seconds, remaining)
        if sleep_time > 0:
            time.sleep(sleep_time)

    return completed


def retrieve_batch_results(client: Any, batch_job: Any) -> list[dict]:
    """
    Download and parse the results JSONL from a completed batch job.

    Args:
        client: Initialised ``google.genai.Client``.
        batch_job: The BatchJob object (must be in SUCCEEDED state).

    Returns:
        List of response dicts parsed from the results JSONL. Each dict
        has a ``key`` field matching the submitted tile filename.
    """
    # The response file is available via batch_job.dest.file_name
    dest_file = batch_job.dest.file_name
    result_bytes = client.files.download(file=dest_file)

    # Parse JSONL — each line is a JSON object with key + response
    results = []
    for line in result_bytes.decode("utf-8").strip().split("\n"):
        if line.strip():
            results.append(json.loads(line))

    logger.info("Retrieved %d result lines from batch job", len(results))
    return results


# ─────────────────────────────────────────────────────────────────────
# Result Validation and Parsing
# ─────────────────────────────────────────────────────────────────────


def validate_batch_results(
    submitted_keys: list[str],
    results: list[dict],
) -> tuple[dict[str, dict], list[str], list[str]]:
    """
    Verify every submitted tile has a response and categorise outcomes.

    Args:
        submitted_keys: List of tile filenames that were submitted.
        results: Parsed result dicts from ``retrieve_batch_results()``.

    Returns:
        Tuple of:
        - matched: Dict mapping tile key → result dict (successful responses)
        - missing: List of tile keys with no response (silent data loss)
        - errored: List of tile keys whose response contains an error
    """
    # Build response lookup by key
    response_by_key: dict[str, dict] = {}
    for result in results:
        key = result.get("key", "")
        response_by_key[key] = result

    matched: dict[str, dict] = {}
    missing: list[str] = []
    errored: list[str] = []

    for key in submitted_keys:
        if key not in response_by_key:
            missing.append(key)
            continue

        result = response_by_key[key]
        # Check if the response contains an error
        if "error" in result:
            errored.append(key)
        else:
            matched[key] = result

    # Warn about unexpected extra keys in results
    submitted_set = set(submitted_keys)
    extra_keys = [
        r.get("key", "?") for r in results
        if r.get("key", "") not in submitted_set
    ]
    if extra_keys:
        logger.warning(
            "Batch results contain %d unexpected keys: %s",
            len(extra_keys), extra_keys[:5],
        )

    return matched, missing, errored


#: Model families whose FLEX capacity has proved unreliable, and for which
#: batch is the better default. Flex and batch bill identically — both are
#: half of list, and a cache hit bills at the cache rate under either — so
#: preferring batch costs nothing and buys capacity.
#:
#: Evidence, 2026-09-16/17: `gemini-3.7-flash` returned 503 UNAVAILABLE
#: ("This model is currently experiencing high demand") on flex for over
#: twelve hours and 37 consecutive checks, while a batch job for the same
#: model on the same account completed in 104 seconds. The newer and more
#: in-demand the model, the likelier this is.
FLEX_UNRELIABLE_FAMILIES: tuple[str, ...] = ("gemini-3.7", "gemini-3.8")


def recommend_execution_mode(model_name: str, requested_mode: str) -> str | None:
    """Return a warning when flex is a poor choice for this model, else None.

    Advisory rather than automatic: batch is asynchronous with a 24-hour
    turnaround target, so switching a caller's mode under it would change the
    shape of the run, not just its price. The operator decides; this makes the
    trade visible at the point of choosing.

    Args:
        model_name: Model about to be dispatched.
        requested_mode: ``"realtime"`` or ``"batch"``.

    Returns:
        A human-readable recommendation, or None when nothing is amiss.
    """
    if requested_mode == "batch":
        return None
    if any(model_name.startswith(f) for f in FLEX_UNRELIABLE_FAMILIES):
        return (
            f"{model_name} is a high-demand family whose FLEX capacity has "
            f"returned 503 for hours at a stretch (2026-09-16/17: 37 "
            f"consecutive failures on flex; a batch job for the same model "
            f"finished in 104 s). Batch bills identically to flex and does "
            f"not compete for the same capacity — prefer --mode batch, or "
            f"switch to it early if flex under-delivers."
        )
    return None


#: What each model family calls its FLOOR — the lowest thinking setting it
#: offers. This project's experiments target "the lowest available setting",
#: not any particular name, and the families spell that differently: the
#: Gemini 3 line calls it `minimal`, the 3.7/3.8 line calls it `low`. Holding
#: the floor constant across models is what makes a cross-model comparison a
#: model comparison rather than a thinking-budget comparison.
#:
#: Evidenced by what this project has actually dispatched (results/passes-manifest.json,
#: 2026-09-17): 680 Gemini-3-line passes at `minimal` and none at `low`; 31
#: 3.7/3.8 passes at `low` and none at `minimal`.
THINKING_FLOOR_BY_FAMILY: dict[str, str] = {
    "gemini-3.7": "low",
    "gemini-3.8": "low",
    "gemini-3-flash": "minimal",
    "gemini-3.5": "minimal",
}

#: Combinations MEASURED to be rejected by the API, with the date measured.
#: Deliberately short: it records observation, not inference. A rejected pair
#: fails EVERY request while the enclosing batch job still reports SUCCEEDED,
#: so the operator sees a completed job and an empty output — which is what a
#: 100-request probe did on 2026-09-17 before this guard existed.
#:
#: Membership is NOT extrapolated between families. That 3.7 refuses `minimal`
#: is no evidence about what the Gemini 3 line does with `low`, which this
#: project has never sent and therefore cannot claim either way.
MEASURED_REJECTED_THINKING: dict[tuple[str, str], str] = {
    ("gemini-3.7", "minimal"): "measured 2026-09-17: INVALID_ARGUMENT per request",
}


def validate_thinking_level(model_name: str, thinking_level: str | None) -> None:
    """Raise on a MEASURED-bad model/thinking pair; warn on an unattested one.

    Two tiers, because the evidence comes in two strengths:

    * A pair in :data:`MEASURED_REJECTED_THINKING` has been observed failing
      against the live API, so it raises.
    * A level that is neither the family's floor nor one this project has
      dispatched before is merely unattested — it may be perfectly valid.
      That warns, because blocking it would make this guard an obstacle to
      running anything new, and an allow-list of levels nobody has tested
      would be a guess dressed as a constraint.

    Args:
        model_name: Model the request will name.
        thinking_level: Level from config or CLI override, or None.

    Raises:
        ValueError: The pair is one measured to fail.
    """
    if not thinking_level:
        return
    level = thinking_level.lower()
    for family, reason in (
        (f, r) for (f, lv), r in MEASURED_REJECTED_THINKING.items()
        if lv == level for f in [f]
    ):
        if model_name.startswith(family):
            floor = THINKING_FLOOR_BY_FAMILY.get(family, "?")
            raise ValueError(
                f"thinking_level {thinking_level!r} is rejected by "
                f"{model_name} ({reason}). This family's floor is {floor!r}. "
                f"The families name the lowest setting differently — "
                f"`minimal` on the Gemini 3 line, `low` on 3.7/3.8 — so a "
                f"config written for one model needs the other's floor, not "
                f"its own default. The wrong one fails every request while "
                f"the batch job still reports SUCCEEDED."
            )

    for family, floor in THINKING_FLOOR_BY_FAMILY.items():
        if model_name.startswith(family) and level != floor:
            logger.warning(
                "thinking_level %r is not %s's floor (%r) and has not been "
                "dispatched for this family before — valid as far as we know, "
                "but unattested; check it is what the experiment intends",
                thinking_level, model_name, floor,
            )
            return


def locate_pass_files(unit_dir: Path) -> tuple[Path, Path, Path] | None:
    """The one geojson, tiles sidecar and meta that ARE the pass in *unit_dir*.

    Until 2026-09-19 ``patch_failed_tiles`` took ``glob(...)[0]`` three times
    independently — directory order, with chunk files as candidates — so on
    a chunked run it could read one chunk's failed list and write the
    recovered features into another chunk's geojson (audit lens A). The
    rule now lives in ``normalise_pass_layout.select_pass_file``: chunk
    files are never candidates, a chunk-only or ambiguous directory is
    refused.

    Args:
        unit_dir: The pass directory.

    Returns:
        ``(geojson, tiles, meta)`` or ``None`` when any of the three is
        absent, chunk-only or ambiguous (the caller skips the unit).
    """
    from scripts.normalise_pass_layout import select_pass_file

    picked: list[Path] = []
    for suffix in (".geojson", ".tiles.json", ".meta.json"):
        hits = sorted(p for p in unit_dir.glob(f"*{suffix}")
                      if p.is_file() and "batch_working" not in p.parts)
        if suffix == ".geojson":
            hits = [h for h in hits if "detections" in h.name]
        try:
            chosen = select_pass_file(hits, suffix, unit_dir)
        except (FileNotFoundError, ValueError) as exc:
            logger.warning("%s", exc)
            return None
        if chosen is None:
            return None
        picked.append(chosen)
    return picked[0], picked[1], picked[2]


def _chunk_sort_key(path: Path | str) -> tuple[int, str]:
    """Sort chunk files by chunk NUMBER: ``_chunk10`` after ``_chunk2``.

    Lexicographic order put chunk 10 before chunk 2, which decided which
    chunk became ``base`` in :func:`merge_chunk_metadata` (audit lens A,
    2026-09-19). Harmless for sums; wrong for anything that reads chunk 0
    as the first chunk.
    """
    name = Path(path).name
    m = re.search(r"_chunk(\d+)", name)
    return (int(m.group(1)) if m else -1, name)


def merge_chunk_metadata(chunk_metas: list[Path], chunk_tiles: list[Path],
                         meta_out: Path, tiles_out: Path) -> dict:
    """Merge a chunked batch run's per-chunk metas and tile lists into one pass.

    A large batch run is split into chunks of at most ``MAX_BATCH_TILES``, and
    the geojsons are merged back into one file. The METADATA was not: each
    chunk kept its own ``.meta.json`` and ``.tiles.json``, so a chunked pass
    had no single record of what it cost or which tiles it covered.

    That is not a cosmetic gap. Anything reading a pass directory — the cost
    auditor, the completeness check, the layout normaliser — takes the file it
    finds, which for a chunked run is chunk 0. A seven-chunk pass would report
    one seventh of its tokens and one seventh of its coverage, and both would
    look like ordinary numbers rather than errors.

    Token counts are SUMMED; the configuration is taken from the first chunk
    and asserted identical across the rest, because a pass whose chunks ran
    under different configurations is not one pass.

    Args:
        chunk_metas: Per-chunk ``.meta.json`` paths.
        chunk_tiles: Per-chunk ``.tiles.json`` paths.
        meta_out: Where to write the merged meta.
        tiles_out: Where to write the merged tile list.

    Returns:
        The merged meta dict.

    Raises:
        ValueError: The chunks disagree on model, temperature or thinking
            level — they are not rungs of one pass.
    """
    metas = [json.loads(Path(m).read_text())
             for m in sorted(chunk_metas, key=_chunk_sort_key)]
    if not metas:
        raise ValueError("no chunk metadata to merge")

    base = json.loads(json.dumps(metas[0]))
    cfg0 = base.get("configuration") or {}
    for i, m in enumerate(metas[1:], start=1):
        cfg = m.get("configuration") or {}
        for field in ("model", "temperature", "thinking_level",
                      "instruction_hash", "library_hash"):
            if cfg.get(field) != cfg0.get(field):
                raise ValueError(
                    f"chunk {i} disagrees on {field}: "
                    f"{cfg.get(field)!r} != {cfg0.get(field)!r}; "
                    "these chunks are not one pass")

    usage: dict[str, int] = {}
    cost = 0.0
    for m in metas:
        for k, v in (m.get("usage_stats") or {}).items():
            if isinstance(v, int):
                usage[k] = usage.get(k, 0) + v
        cost += float((m.get("cost_estimate") or {}).get("total_cost_usd") or 0)
    inp = usage.get("total_input_tokens", 0)
    usage["cached_share"] = (usage.get("total_cached_tokens", 0) / inp
                             if inp else None)
    usage["usage_source"] = f"merged from {len(metas)} chunk metas"
    base["usage_stats"] = usage

    # execution_stats and results_summary must be summed too, not inherited
    # from chunk 0. `audit_proposer_cost.py` reads
    # execution_stats.items_processed as the pass's item count, so leaving
    # chunk 0's value made a seven-chunk pass report 4,000 items against its
    # own correctly-summed 491M tokens — the tokens and therefore the total
    # cost were right, but the per-item rate was out by the chunk count.
    for section, fields in (
        ("execution_stats", ("items_processed", "items_failed", "items_skipped",
                             "retries_total", "retries_rate_limit",
                             "retries_server_error", "retries_timeout")),
        ("results_summary", ("total_detections",)),
    ):
        merged_section = dict(base.get(section) or {})
        for field in fields:
            total = 0
            present = False
            for m in metas:
                v = (m.get(section) or {}).get(field)
                if isinstance(v, int):
                    total += v
                    present = True
            if present:
                merged_section[field] = total
        if merged_section:
            base[section] = merged_section
    if not isinstance(base.get("cost_estimate"), dict):
        base["cost_estimate"] = {}
    base["cost_estimate"]["total_cost_usd"] = cost
    base["chunked_run"] = {"n_chunks": len(metas),
                           "chunk_metas": [Path(m).name for m in
                                           sorted(chunk_metas, key=_chunk_sort_key)]}

    # Each chunk's ``total_tiles`` is the size of THAT chunk, so the pass's
    # total is their SUM. Taking the max (as this did until 2026-09-18) wrote
    # ``total_tiles: 4000`` against 24,561 completed tiles for a seven-chunk
    # pass — a sidecar that says the pass is six times over-complete, which
    # `derive_recovery_worklists.py` reads as "not a whole corpus" and skips.
    completed: set[str] = set()
    total = 0
    for t in sorted(chunk_tiles, key=_chunk_sort_key):
        d = json.loads(Path(t).read_text())
        completed |= set(d.get("completed", []))
        total += int(d.get("total_tiles", 0) or 0)
    tiles_out.write_text(json.dumps(
        {"total_tiles": total, "completed": sorted(completed)}, indent=1) + "\n")
    meta_out.write_text(json.dumps(base, indent=2) + "\n")
    logger.info("merged %d chunk metas: %s input tokens, %s tiles completed",
                len(metas), f"{inp:,}", f"{len(completed):,}")
    return base


def aggregate_batch_usage(results: list[dict]) -> dict:
    """Sum per-response usage across a batch's results file.

    The Batch API reports usage PER RESPONSE, not on the job: a completed
    ``BatchJob`` carries no ``usage_metadata`` at all. Reading the job alone
    therefore yields nothing, which is why this project's 2026-04-15 Pro
    stages were recorded as having run with zero tokens and are described in
    ``outputs/verifier-meta-recovery-2026-09-14.json`` as having "ran through
    the Batch API, which returns no per-response usage". Measured 2026-09-17,
    that is not so — the usage is there, in the results file, and includes
    both counts that decide cost:

        {'promptTokenCount': 19999, 'candidatesTokenCount': 10,
         'cachedContentTokenCount': 18909, 'thoughtsTokenCount': 271}

    Field names in the output are those the REAL-TIME path records
    (``scripts/lib_llm_metadata.py``), so one auditor reads both modes.

    Args:
        results: Parsed result dicts from :func:`retrieve_batch_results`.

    Returns:
        A usage dict in real-time field naming, plus ``n_responses_with_usage``
        so a partial report can be told from a complete one. ``cached_share``
        is None when no response reported usage, which is distinct from a
        share of zero.
    """
    totals = {
        "total_input_tokens": 0,
        "total_cached_tokens": 0,
        "total_output_tokens": 0,
        "total_thoughts_tokens": 0,
        "total_tokens": 0,
    }
    field_map = {
        "promptTokenCount": "total_input_tokens",
        "cachedContentTokenCount": "total_cached_tokens",
        "candidatesTokenCount": "total_output_tokens",
        "thoughtsTokenCount": "total_thoughts_tokens",
        "totalTokenCount": "total_tokens",
    }
    n_with_usage = 0
    for result in results:
        response = result.get("response") or {}
        usage = response.get("usageMetadata") or response.get("usage_metadata")
        if not usage:
            continue
        n_with_usage += 1
        for api_name, our_name in field_map.items():
            value = usage.get(api_name)
            if isinstance(value, int):
                totals[our_name] += value

    totals["n_responses_with_usage"] = n_with_usage
    totals["usage_source"] = (
        "batch results file (per-response usageMetadata)" if n_with_usage
        else "ABSENT — no response carried usageMetadata"
    )
    totals["cached_share"] = (
        totals["total_cached_tokens"] / totals["total_input_tokens"]
        if totals["total_input_tokens"] else None
    )
    return totals


def parse_response_with_repair(response_text: str) -> dict | list:
    """
    Parse a Gemini response with three tiers of malformed-JSON recovery.

    Audit of three production runs (``outputs/55maps-text-min-generalisation/``,
    ``outputs/55maps-image-generalisation/``, ``outputs/gs/gold-standard-v2/``)
    showed 92 % of 163 lost tiles match patterns this pipeline handles:

    Tier 1 (regex):
        Strip trailing commas before closing brackets/braces — handles
        ~52 % of historical failures (84 of 163 tiles). Mirrors the
        in-line repair already present at ``lib_batch_api.py`` line 920.

    Tier 2 (json5):
        Retry with the permissive ``json5`` parser — handles delimiter
        and value errors that strict ``json`` rejects (e.g. unquoted
        keys, single-quoted strings, embedded comments).

    Tier 3 (longest-valid-prefix scan):
        Scan from the end of the text for the longest prefix that parses
        as valid JSON — handles ``Extra data`` errors where valid JSON
        is followed by garbage. Linear from-the-end scan rather than a
        true binary search because validity is not monotonic over
        prefix length, and typical "Extra data" suffixes are short.

    The combined three-tier pipeline is expected to recover ~92 % of
    historical realtime parse failures, saving roughly USD 20–50 per
    full-corpus generalisation run.

    Args:
        response_text: Raw model response (the SDK's ``response.text``).

    Returns:
        Parsed object — ordinarily a ``dict`` (e.g. ``{"detections": [...]}``)
        but may be a ``list`` when the model returns a bare array.

    Raises:
        ValueError: If all three tiers fail. The exception message
            identifies which tiers were attempted; the underlying parser
            error is chained via ``raise ... from``.

    Examples:
        >>> parse_response_with_repair('{"detections": [1, 2, 3,]}')
        {'detections': [1, 2, 3]}
        >>> parse_response_with_repair('{"a": 1}\\nextra garbage')
        {'a': 1}
    """
    # Tier 1: trailing-comma repair, then strict json.
    # Mirrors the canonical in-line repair at lib_batch_api.py:920.
    repaired = re.sub(r",\s*([}\]])", r"\1", response_text)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError as tier1_err:
        last_err: Exception = tier1_err

    # Tier 2: permissive json5 parser. Imported lazily so the helper
    # can be imported in environments where json5 is not installed —
    # callers see the import error only when Tier 1 fails.
    try:
        import json5
        return json5.loads(repaired)
    except ImportError as tier2_err:
        last_err = tier2_err
    except Exception as tier2_err:
        last_err = tier2_err

    # Tier 3: scan for the longest prefix that parses as valid JSON.
    # Walks from the end of the (Tier-1-repaired) text downward so the
    # *first* successful parse is the longest valid prefix. Catches
    # "Extra data" errors where the model emits a valid object then
    # appends free-form prose, code fences, or a second object.
    for end in range(len(repaired), 0, -1):
        try:
            return json.loads(repaired[:end])
        except json.JSONDecodeError:
            continue

    raise ValueError(
        "Could not parse response after Tier 1 (trailing-comma), Tier 2 "
        "(json5), or Tier 3 (longest-valid-prefix) repair"
    ) from last_err


def _parse_detections_from_response(result: dict) -> list[dict]:
    """
    Extract detections from a single batch response line.

    Follows the same parsing logic as ``process_single_tile()`` in
    ``4_detect_mounds_batch.py``.

    Args:
        result: A single result dict from the batch response JSONL.

    Returns:
        List of detection dicts (may be empty for zero-detection tiles).

    Raises:
        ValueError: If the response text cannot be parsed as JSON.
    """
    # Navigate the response structure:
    # result.response.candidates[0].content.parts[0].text
    response = result.get("response", {})
    candidates = response.get("candidates", [])

    if not candidates:
        raise ValueError("No candidates in batch response")

    content = candidates[0].get("content", {})
    parts = content.get("parts", [])

    if not parts:
        raise ValueError("No parts in batch response content")

    text = parts[0].get("text", "")
    if not text:
        return []

    # Strip trailing commas before closing brackets/braces —
    # common LLM output malformation (e.g. [{...},])
    text = re.sub(r",\s*([}\]])", r"\1", text)

    json_response = json.loads(text)

    if isinstance(json_response, list):
        # Handle case where model returns [{\"detections\": [...]}]
        if (
            len(json_response) > 0
            and isinstance(json_response[0], dict)
            and "detections" in json_response[0]
        ):
            return json_response[0]["detections"]
        return json_response

    return json_response.get("detections", [])


def parse_detections_to_geojson(
    matched_results: dict[str, dict],
    tile_paths_by_name: dict[str, Path],
    config_version: str,
    model_name: str,
    tile_size: int = TILE_SIZE,
) -> tuple[list[dict], int, list[str]]:
    """
    Convert batch responses to GeoJSON features.

    Reuses the same coordinate transformation logic as
    ``process_single_tile()`` — normalised [0, 1000] coordinates
    mapped to pixel space via ``tile_size``, then georeferenced via
    the tile's rasterio transform.

    Args:
        matched_results: Dict of tile_key → result dict.
        tile_paths_by_name: Dict of tile_filename → Path for rasterio.
        config_version: Version string from config (for feature properties).
        model_name: Model name string (for feature properties).
        tile_size: Tile dimension in pixels for coordinate conversion.
            Defaults to TILE_SIZE (512) for backward compatibility.

    Returns:
        Tuple of:
        - features: List of GeoJSON Feature dicts
        - total_detections: Count of detections extracted
        - parse_failed_keys: List of tile keys that failed JSON parsing
    """
    features: list[dict] = []
    total_detections = 0
    parse_failed_keys: list[str] = []

    for tile_key, result in matched_results.items():
        try:
            detections = _parse_detections_from_response(result)
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            logger.warning(
                "Failed to parse detections for %s: %s", tile_key, e,
            )
            parse_failed_keys.append(tile_key)
            continue

        total_detections += len(detections)

        # Skip georeferencing if no detections to process
        if not detections:
            continue

        # Get tile transform for georeferencing
        tile_path = tile_paths_by_name.get(tile_key)
        if tile_path is None or not tile_path.exists():
            logger.warning("Tile path not found for %s", tile_key)
            parse_failed_keys.append(tile_key)
            continue

        with rasterio.open(tile_path) as src:
            transform = src.transform

        for det in detections:
            if "box_2d" not in det:
                continue

            box_coords = det["box_2d"]
            if not isinstance(box_coords, (list, tuple)) or len(box_coords) != 4:
                logger.warning(
                    "Malformed box_2d in %s: %s", tile_key, box_coords,
                )
                continue

            # Cast to float — Gemini occasionally returns string
            # coordinates (e.g., "123" instead of 123) which would
            # cause TypeError on the division below.
            try:
                ymin_n, xmin_n, ymax_n, xmax_n = [
                    float(v) for v in box_coords
                ]
            except (ValueError, TypeError) as e:
                logger.warning(
                    "Non-numeric box_2d in %s: %s (%s)",
                    tile_key, box_coords, e,
                )
                continue
            px_min_x = (xmin_n / 1000.0) * tile_size
            px_max_x = (xmax_n / 1000.0) * tile_size
            px_min_y = (ymin_n / 1000.0) * tile_size
            px_max_y = (ymax_n / 1000.0) * tile_size

            geo_x1, geo_y1 = transform * (px_min_x, px_min_y)
            geo_x2, geo_y2 = transform * (px_max_x, px_max_y)

            min_geo_x = min(geo_x1, geo_x2)
            max_geo_x = max(geo_x1, geo_x2)
            min_geo_y = min(geo_y1, geo_y2)
            max_geo_y = max(geo_y1, geo_y2)

            geom = box(min_geo_x, min_geo_y, max_geo_x, max_geo_y)
            feature = geojson.Feature(
                geometry=mapping(geom),
                properties={
                    "source_tile": tile_key,
                    "label": det.get("label", "mound"),
                    "subtype": det.get("subtype", "unknown"),
                    "confidence": "high",
                    "method": config_version,
                    "model": model_name,
                },
            )
            features.append(feature)

    return features, total_detections, parse_failed_keys


# ─────────────────────────────────────────────────────────────────────
# Parse-Failure Retry
# ─────────────────────────────────────────────────────────────────────


def _retry_tile_sync(
    client: Any,
    tile_path: Path,
    model_name: str,
    system_instruction: str,
    prompt_config: dict,
    examples: list[dict],
    max_output_tokens_override: int | None = None,
    service_tier: str | None = None,
) -> dict | None:
    """
    Retry a single parse-failed tile via synchronous API call.

    Reconstructs the same prompt used in the batch request and makes
    one synchronous ``generate_content()`` call. Returns the response
    in the same dict format as batch response lines so it can be fed
    back through ``_parse_detections_from_response()``.

    Args:
        client: Initialised ``google.genai.Client``.
        tile_path: Path to the tile image file.
        model_name: Model name string (e.g. ``"gemini-3-flash"``).
        system_instruction: System instruction text.
        prompt_config: Prompt config dict (temperature, etc.).
        examples: List of example dicts from prompt config.
        max_output_tokens_override: If provided, overrides the
            ``max_output_tokens`` from prompt_config. Used by
            safe-mode retries to constrain thinking budget and
            prevent output truncation.
        service_tier: Optional service tier for the call (``"flex"``
            for the 50 % off-peak tier). ``None`` uses standard.

    Returns:
        A result dict matching the batch response format, or ``None``
        if the retry itself fails.
    """
    try:
        from google.genai import types  # Lazy import — only on retry path
    except ImportError:
        logger.error("google.genai SDK not available for sync retry")
        return None

    try:
        include_images = prompt_config.get("include_example_images", True)

        # Build content parts mirroring 4_detect_mounds_batch.py's
        # process_single_tile() prompt assembly
        content_parts: list[types.Part] = []

        # Reference examples preamble
        content_parts.append(types.Part.from_text(
            text="Here are the Reference Symbols you must find:",
        ))

        # Reference example images/labels (if image-inclusive)
        if include_images:
            for ex in examples:
                label = ex.get("label", "Example")
                path_str = ex.get("path", "")
                img_path = EXAMPLES_DIR / path_str
                if img_path.exists():
                    content_parts.append(
                        types.Part.from_text(text=label),
                    )
                    with open(img_path, "rb") as f:
                        image_bytes = f.read()
                    suffix = img_path.suffix.lower()
                    mime = (
                        "image/png" if suffix == ".png" else "image/jpeg"
                    )
                    content_parts.append(
                        types.Part.from_bytes(
                            data=image_bytes, mime_type=mime,
                        ),
                    )

        # Transition text
        content_parts.append(types.Part.from_text(
            text="Now, find detection instances that visually match "
            "ANY of the above Reference Examples in the Target "
            "Map Tile below:",
        ))

        # Tile image
        with open(tile_path, "rb") as f:
            tile_bytes = f.read()
        content_parts.append(
            types.Part.from_bytes(data=tile_bytes, mime_type="image/png"),
        )

        # Generation config — mirror batch JSONL settings including
        # thinking_config when present (Finding 1 from debug audit)
        gen_config_kwargs: dict[str, Any] = {
            "temperature": prompt_config.get("temperature", 0.1),
            "max_output_tokens": max_output_tokens_override or (
                prompt_config.get("max_output_tokens", 8192)
            ),
            "response_mime_type": "application/json",
            "system_instruction": system_instruction,
        }
        thinking_level = prompt_config.get("thinking_level")
        if thinking_level:
            gen_config_kwargs["thinking_config"] = types.ThinkingConfig(
                thinking_level=thinking_level.upper(),
            )
        # Flex processing (50% discount, off-peak capacity) — standing PI
        # instruction 2026-07-30: always run in flex mode.
        if service_tier is not None:
            gen_config_kwargs["service_tier"] = service_tier
        gen_config = types.GenerateContentConfig(**gen_config_kwargs)

        response = client.models.generate_content(
            model=model_name,
            contents=content_parts,
            config=gen_config,
        )

        # Convert SDK response to batch-format dict for reuse by
        # _parse_detections_from_response()
        return {
            "key": tile_path.name,
            "response": {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": response.text}],
                            "role": "model",
                        },
                        "finish_reason": "STOP",
                    }
                ],
            },
        }
    except Exception as e:
        logger.warning(
            "Sync retry failed for %s: %s", tile_path.name, e,
        )
        return None


# ─────────────────────────────────────────────────────────────────────
# Output Writers
# ─────────────────────────────────────────────────────────────────────


def _save_geojson(
    features: list[dict],
    output_file: Path,
    processed_tiles: set[str],
) -> None:
    """
    Write features to a GeoJSON FeatureCollection.

    Output format matches ``4_detect_mounds_batch.py:_save_geojson()``
    exactly — same CRS, same ``processed_tiles`` top-level property.

    Args:
        features: List of GeoJSON Feature dicts.
        output_file: Path to write the FeatureCollection.
        processed_tiles: Set of tile filenames that were processed.
    """
    collection = geojson.FeatureCollection(features)
    collection["crs"] = {
        "type": "name",
        "properties": {"name": "urn:ogc:def:crs:EPSG::32635"},
    }
    collection["processed_tiles"] = sorted(processed_tiles)
    with open(output_file, "w") as f:
        geojson.dump(collection, f)


def write_batch_outputs(
    features: list[dict],
    processed_tiles: set[str],
    failed_tiles: list[str],
    output_file: Path,
    config: dict,
    model_name: str,
    system_instruction: str,
    total_detections: int,
    usage_stats: dict | None = None,
) -> dict[str, float]:
    """
    Write GeoJSON, .meta.json, and .tiles.json files.

    Produces output identical to the concurrent pipeline so downstream
    analysis scripts (``run_phase2.py:read_meta_cost()``, etc.) work
    without modification.

    Args:
        features: GeoJSON Feature dicts.
        processed_tiles: Set of successfully processed tile filenames.
        failed_tiles: List of tile filenames that failed.
        output_file: Path for the GeoJSON file.
        config: Prompt config dict.
        model_name: Model name string.
        system_instruction: System instruction text.
        total_detections: Total detection count.
        usage_stats: Optional token usage dict from batch job metadata.

    Returns:
        Cost estimate dict with ``total_cost_usd``.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 1. Write GeoJSON
    _save_geojson(features, output_file, processed_tiles)

    # 2. Write tile manifest (.tiles.json)
    tiles_manifest_path = output_file.with_suffix(".tiles.json")
    tile_manifest = {
        "total_tiles": len(processed_tiles) + len(failed_tiles),
        "completed": sorted(processed_tiles),
        "failed": sorted(failed_tiles),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(tiles_manifest_path, "w") as f:
        json.dump(tile_manifest, f, indent=2)

    # 3. Write metadata (.meta.json) — using LLMMetadataTracker for
    #    format compatibility with read_meta_cost() / read_meta_failures()
    tracker = LLMMetadataTracker(
        config=config,
        system_instruction=system_instruction,
        script_name="lib_batch_api.py",
        script_version=__version__,
        model_override=model_name,
    )

    # Record processed/failed counts
    for tile in processed_tiles:
        tracker.log_success(tile)
    for tile in failed_tiles:
        tracker.log_failure(tile, "batch_api_error")

    # Add results summary
    tracker.update_results_summary({
        "total_detections": total_detections,
        "execution_mode": "batch",
    })

    # Build usage from the aggregated per-response stats.
    #
    # Field names are the REAL-TIME ones, which is what `aggregate_batch_usage`
    # emits and what `audit_proposer_cost.py` reads. They were previously read
    # as `input_tokens` / `output_tokens`, so once the producer moved to the
    # shared naming every count silently landed as 0 — a batch leg's meta said
    # it had used no tokens at all.
    #
    # CACHED and THINKING are carried too. Both decide the bill: cached input
    # bills at a tenth of the input rate, and thinking tokens bill at the
    # OUTPUT rate. Dropping them is what made earlier batch legs unauditable.
    usage = AggregatedUsage()
    if usage_stats:
        usage.total_input_tokens = usage_stats.get("total_input_tokens", 0)
        usage.total_cached_tokens = usage_stats.get("total_cached_tokens", 0)
        usage.total_output_tokens = usage_stats.get("total_output_tokens", 0)
        usage.total_thoughts_tokens = usage_stats.get("total_thoughts_tokens", 0)
        usage.total_tokens = usage_stats.get("total_tokens", 0)
    tracker.usage = usage

    # The discount is now a parameter of the cost model rather than a
    # post-hoc multiply here, so batch and real-time flex share one code path
    # and one recorded convention. ``batch_discount`` is retained in
    # pricing_used for backwards compatibility with readers of older metadata.
    cost_estimate = estimate_cost(
        usage=usage,
        provider=LLMProvider.GEMINI.value,
        model=model_name,
        discount=BATCH_API_DISCOUNT,
        discount_reason="Google async Batch API (50 % of list)",
    )
    cost_estimate["pricing_used"]["batch_discount"] = BATCH_API_DISCOUNT

    meta = tracker.finalise(include_per_item=False)
    meta["cost_estimate"] = cost_estimate
    if usage_stats:
        # Provenance of the counts: how many responses reported usage, and
        # whether any did. "0 tokens" and "nobody told us" must not read alike.
        for key in ("n_responses_with_usage", "usage_source", "cached_share"):
            if key in usage_stats:
                meta.setdefault("usage_stats", {})[key] = usage_stats[key]
    meta["batch_api"] = {
        "execution_mode": "batch",
        "batch_discount_applied": True,
    }

    meta_path = output_file.with_suffix(".meta.json")

    # Resume-mode merge: if a meta file already exists from a prior pass,
    # merge the fresh stats into it rather than overwriting. This keeps
    # downstream cost aggregation accurate for resumed batch runs.
    meta = merge_meta_into_existing(meta_path, meta)

    # Atomic write to avoid leaving a truncated meta on kill mid-write.
    tmp_meta = meta_path.with_suffix(meta_path.suffix + ".tmp")
    with open(tmp_meta, "w") as f:
        json.dump(meta, f, indent=2)
    tmp_meta.replace(meta_path)

    logger.info(
        "Wrote batch outputs: %s, %s, %s",
        output_file.name, tiles_manifest_path.name, meta_path.name,
    )

    return cost_estimate


# ─────────────────────────────────────────────────────────────────────
# Unit Orchestrator
# ─────────────────────────────────────────────────────────────────────


def _resolve_tile_paths(
    manifest_path: Path,
    tiles_dir: Path | None = None,
) -> list[Path]:
    """
    Resolve tile paths from a manifest file.

    Args:
        manifest_path: Path to JSON manifest listing tile filenames.
        tiles_dir: Directory containing tile subdirectories. Defaults to
            ``TILES_DIR`` from config when not specified.

    Returns:
        List of Path objects for each tile found on disc.
    """
    with open(manifest_path) as f:
        target_filenames = json.load(f)

    # Build lookup of all available tiles
    effective_dir = tiles_dir if tiles_dir is not None else TILES_DIR
    all_tiles: dict[str, Path] = {}
    for map_dir in effective_dir.iterdir():
        if map_dir.is_dir():
            for t in map_dir.rglob("*.png"):
                all_tiles[t.name] = t

    paths = []
    for fname in target_filenames:
        if fname in all_tiles:
            paths.append(all_tiles[fname])
        else:
            logger.warning("Tile from manifest not found on disc: %s", fname)

    return paths


def prepare_batch_unit(
    unit: dict,
    config: dict,
    output_dir: Path,
    model_name: str,
    system_instruction: str,
    examples: list[dict],
    config_version: str,
    limit: int | None = None,
    offset: int = 0,
    tile_size: int | None = None,
    tiles_dir: Path | None = None,
    output_name_suffix: str = "",
    cached_content: str | None = None,
) -> BatchUnitContext | None:
    """
    Prepare one execution unit for batch submission (Phase 1).

    Handles path resolution, tile manifest loading, prompt config loading
    with temperature overrides, and JSONL file construction. No API calls
    — pure filesystem I/O.

    Args:
        unit: Execution unit dict with condition_name, run, config, etc.
        config: Full study configuration dict (must include ``_project_root``).
        output_dir: Base output directory.
        model_name: Resolved model name for the batch job.
        system_instruction: System instruction text.
        examples: List of example dicts from prompt config.
        config_version: Version string from prompt config.
        limit: Optional tile limit for testing.
        offset: Number of tiles to skip from the start of the manifest.
            Used with ``limit`` for chunked batch submission when the
            full tile set exceeds the Batch API file size limit (2 GB).
        tile_size: Tile dimension in pixels for coordinate conversion.
            Defaults to TILE_SIZE (512) when not specified.
        tiles_dir: Directory containing tile subdirectories. Defaults to
            TILES_DIR from config when not specified.
        output_name_suffix: Optional suffix appended to output filenames
            (e.g., ``"_chunk0"``). Used for chunked submissions to avoid
            overwriting earlier chunks' output files.

    Returns:
        A ``BatchUnitContext`` carrying all state needed for submission
        and completion, or ``None`` if no tiles were found.
    """
    inputs = config["inputs"]
    manifest_path = Path(config.get("_project_root", ".")) / inputs["manifest"]

    # Build output path: {output_dir}/{condition_name}/run_{K}/
    run_dir = output_dir / unit["condition_name"] / f"run_{unit['run']}"
    output_name = (
        f"detections_{unit['condition_name']}_run{unit['run']:02d}"
        f"{output_name_suffix}"
    )
    output_file = run_dir / f"{output_name}.geojson"

    # Resolve tiles (use overridden tiles_dir if provided)
    tile_paths = _resolve_tile_paths(manifest_path, tiles_dir=tiles_dir)
    if offset > 0:
        tile_paths = tile_paths[offset:]
    if limit and limit > 0:
        tile_paths = tile_paths[:limit]

    if not tile_paths:
        return None

    # Use provided tile_size or fall back to config default
    effective_tile_size = tile_size if tile_size is not None else TILE_SIZE

    # Validate tile dimensions match configured tile_size BEFORE the
    # expensive JSONL build. A mismatch silently corrupts coordinate
    # conversion (e.g., 512 on 384px tiles → 300–500m offsets).
    from PIL import Image as _PILImage
    _sample = _PILImage.open(tile_paths[0])
    _actual_w, _actual_h = _sample.size
    _sample.close()
    if _actual_w != effective_tile_size or _actual_h != effective_tile_size:
        logger.error(
            "Tile dimensions (%d×%d) do not match tile_size (%d). "
            "Pass tile_size=%d to fix coordinate conversion.",
            _actual_w, _actual_h, effective_tile_size, _actual_w,
        )
        return None

    # Load prompt config for generation settings
    prompt_config_path = (
        Path(config.get("_project_root", ".")) / unit["config"]
    )
    with open(prompt_config_path) as f:
        prompt_config = json.load(f)

    # Apply overrides from the execution unit
    if unit.get("temperature") is not None:
        prompt_config["temperature"] = unit["temperature"]
    if unit.get("thinking_level") is not None:
        prompt_config["thinking_level"] = unit["thinking_level"]
    # The RESOLVED model, not the config file's default. Without this the
    # config keeps whatever model its file names — `gemini-3-flash` for the
    # shared image config — while the batch is submitted against
    # `model_name`. That mismatch is not cosmetic: it made
    # validate_thinking_level() check the wrong family, so the guard against
    # `minimal`-on-3.7 would have PASSED the very submission it exists to
    # refuse, and it is the same class as erratum E42, where a CLI `--model`
    # override reached the API but never the recorded metadata.
    prompt_config["model"] = model_name

    # Build JSONL
    jsonl_dir = run_dir / "batch_working"
    jsonl_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = jsonl_dir / f"{output_name}.jsonl"

    submitted_keys = [t.name for t in tile_paths]
    line_count = build_jsonl_file(
        tile_paths=tile_paths,
        config=prompt_config,
        system_instruction=system_instruction,
        examples=examples,
        output_path=jsonl_path,
        cached_content=cached_content,
    )

    key = f"{unit['condition_name']}/run_{unit['run']}"

    return BatchUnitContext(
        unit_key=key,
        unit=unit,
        output_file=output_file,
        jsonl_path=jsonl_path,
        submitted_keys=submitted_keys,
        tile_paths=tile_paths,
        prompt_config=prompt_config,
        model_name=model_name,
        system_instruction=system_instruction,
        config_version=config_version,
        line_count=line_count,
        tile_size=effective_tile_size,
        examples=examples,
    )


def submit_batch_unit(
    ctx: BatchUnitContext,
    client: Any,
    on_submit: Callable[[str, list[str], str], None] | None = None,
) -> tuple[str, str]:
    """
    Upload JSONL and submit a batch job for one execution unit (Phase 2).

    Args:
        ctx: Context from ``prepare_batch_unit()``.
        client: Initialised ``google.genai.Client``.
        on_submit: Optional write-ahead callback invoked with
            ``(job_name, tile_keys, uploaded_file_name)`` immediately
            after successful submission. Used to persist the job name
            and uploaded file name to a checkpoint before the long
            polling phase begins.

    Returns:
        Tuple of ``(job_name, uploaded_file_name)`` — the batch job
        resource name and the Files API resource name for the uploaded
        input JSONL.

    Raises:
        Exception: On upload or submission failure (caller handles).
    """
    display_name = f"{ctx.unit['condition_name']}_run{ctx.unit['run']:02d}"
    uploaded_name = upload_jsonl(
        client, ctx.jsonl_path, display_name, unit_key=ctx.unit_key,
    )
    batch_job = submit_batch_job(
        client, ctx.model_name, uploaded_name, display_name,
    )
    job_name = batch_job.name
    print(f"  Submitted batch job: {job_name}")

    # Write-ahead checkpoint: persist job name and file name before polling
    if on_submit:
        on_submit(job_name, ctx.submitted_keys, uploaded_name)

    return job_name, uploaded_name


def complete_batch_unit(
    ctx: BatchUnitContext,
    client: Any,
    completed_job: Any,
) -> tuple[bool, str, float]:
    """
    Process results from a completed batch job (Phase 3 completion).

    Given a terminal ``BatchJob`` object, retrieves results, validates
    tile coverage, parses detections to GeoJSON, and writes output files.

    Args:
        ctx: Context from ``prepare_batch_unit()``.
        client: Initialised ``google.genai.Client``.
        completed_job: The ``BatchJob`` in a terminal state.

    Returns:
        Tuple of ``(success, message, cost_usd)``.
    """
    # Check terminal state
    job_state = _get_state_name(completed_job.state)
    if job_state not in (
        "JOB_STATE_SUCCEEDED", "JOB_STATE_PARTIALLY_SUCCEEDED",
    ):
        return False, f"batch_job_{job_state}", 0.0

    if job_state == "JOB_STATE_PARTIALLY_SUCCEEDED":
        print(
            "  WARNING: Batch job partially succeeded "
            "— some tiles may have failed"
        )

    # Retrieve and parse results
    try:
        results = retrieve_batch_results(client, completed_job)
    except Exception as e:
        return False, f"retrieve_error: {e}", 0.0

    # Validate — detect silent data loss
    matched, missing_tiles, errored = validate_batch_results(
        ctx.submitted_keys, results,
    )

    if missing_tiles:
        print(
            f"  WARNING: {len(missing_tiles)} tiles missing from "
            f"batch results: {missing_tiles[:5]}"
        )

    # Build tile path lookup for georeferencing
    tile_paths_by_name = {t.name: t for t in ctx.tile_paths}

    # Parse detections to GeoJSON (use tile_size from context for
    # correct normalised→pixel coordinate conversion)
    features, total_detections, parse_failed_keys = (
        parse_detections_to_geojson(
            matched_results=matched,
            tile_paths_by_name=tile_paths_by_name,
            config_version=ctx.config_version,
            model_name=ctx.model_name,
            tile_size=ctx.tile_size,
        )
    )

    # Retry parse failures via synchronous API (up to MAX_SYNC_RETRIES
    # attempts per tile). Failures are typically stochastic JSON parse
    # errors — the model produces valid detections wrapped in malformed
    # JSON. Empirically, ~74% resolve on the first retry, ~98% by
    # attempt 3, and ~99.9% by attempt 5. Deterministic failures (tiles
    # where the model consistently exceeds output token limits) will not
    # resolve and are recorded for later diagnosis.
    #
    # Cost is negligible: ~$0.0003 per text retry, ~$0.0005 per image
    # retry. Even 5 retries × 30 tiles ≈ $0.05.
    retried_keys: list[str] = []
    if parse_failed_keys:
        pending_retries = list(parse_failed_keys)
        logger.info(
            "Retrying %d parse-failed tile(s) synchronously "
            "(up to %d attempts each): %s",
            len(pending_retries), MAX_SYNC_RETRIES, pending_retries,
        )

        # Remove tiles with unresolvable paths before retrying —
        # these will never succeed and should not be retried.
        unresolvable = [
            k for k in pending_retries
            if tile_paths_by_name.get(k) is None
        ]
        if unresolvable:
            logger.warning(
                "Skipping %d tile(s) with no local path: %s",
                len(unresolvable), unresolvable,
            )
            pending_retries = [
                k for k in pending_retries if k not in unresolvable
            ]

        for attempt in range(1, MAX_SYNC_RETRIES + 1):
            if not pending_retries:
                break

            attempt_successes: list[str] = []
            for tile_key in pending_retries:
                tile_path = tile_paths_by_name[tile_key]

                try:
                    retry_result = _retry_tile_sync(
                        client=client,
                        tile_path=tile_path,
                        model_name=ctx.model_name,
                        system_instruction=ctx.system_instruction,
                        prompt_config=ctx.prompt_config,
                        examples=ctx.examples,
                    )

                    if retry_result is not None:
                        # Feed through the same parse pipeline
                        retry_matched = {tile_key: retry_result}
                        retry_features, retry_dets, retry_failures = (
                            parse_detections_to_geojson(
                                matched_results=retry_matched,
                                tile_paths_by_name=tile_paths_by_name,
                                config_version=ctx.config_version,
                                model_name=ctx.model_name,
                                tile_size=ctx.tile_size,
                            )
                        )
                        if not retry_failures:
                            features.extend(retry_features)
                            total_detections += retry_dets
                            retried_keys.append(tile_key)
                            attempt_successes.append(tile_key)
                            logger.info(
                                "Retry attempt %d succeeded for %s",
                                attempt, tile_key,
                            )
                except Exception as e:
                    logger.warning(
                        "Retry attempt %d error for %s: %s",
                        attempt, tile_key, e,
                    )

            # Remove successes from pending list for next attempt
            pending_retries = [
                k for k in pending_retries
                if k not in attempt_successes
            ]

            if attempt_successes:
                logger.info(
                    "Retry attempt %d: %d/%d resolved, %d remaining",
                    attempt, len(attempt_successes),
                    len(attempt_successes) + len(pending_retries),
                    len(pending_retries),
                )

    if retried_keys:
        print(
            f"  Retried {len(retried_keys)}/{len(parse_failed_keys)} "
            f"parse-failed tile(s) successfully"
            + (
                f" ({MAX_SYNC_RETRIES} attempts max)"
                if len(retried_keys) < len(parse_failed_keys)
                else ""
            )
        )

    # Tiles that failed parse even after all retry attempts are
    # recorded as true failures — likely deterministic (e.g., model
    # output exceeds token limit for this tile/config combination).
    still_failed = [
        k for k in parse_failed_keys if k not in retried_keys
    ]
    if still_failed:
        print(
            f"\n  {'─' * 56}\n"
            f"  Tile Failure Report: {len(still_failed)} tile(s) "
            f"failed all {MAX_SYNC_RETRIES} retry attempts"
        )
        for tile_name in sorted(still_failed):
            print(f"    {tile_name}")
        print(
            f"\n  These tiles likely hit output truncation "
            f"(thinking tokens exhaust max_output_tokens)."
            f"\n  To patch later with reduced output budget:"
            f"\n    python scripts/run_phase2.py <study.yaml> "
            f"--patch-tiles"
            f"\n  {'─' * 56}"
        )

    # Build processed/failed tile sets
    processed_tiles = set(matched.keys()) - set(still_failed)
    failed_tiles = missing_tiles + errored + still_failed

    # Usage comes from the RESULTS FILE, not the job. A completed BatchJob
    # carries no usage_metadata; the per-response usageMetadata does, and it
    # includes `cachedContentTokenCount` and `thoughtsTokenCount` — the two
    # counts that decide the bill. Reading the job instead is what left the
    # 2026-04-15 Pro stages recorded as zero-token and unauditable.
    usage_stats = aggregate_batch_usage(results)
    if usage_stats.get("n_responses_with_usage"):
        logger.info(
            "batch usage: %s input (%s cached, share %.3f), %s output, "
            "%s thinking, from %d/%d responses",
            f"{usage_stats['total_input_tokens']:,}",
            f"{usage_stats['total_cached_tokens']:,}",
            usage_stats["cached_share"] or 0.0,
            f"{usage_stats['total_output_tokens']:,}",
            f"{usage_stats['total_thoughts_tokens']:,}",
            usage_stats["n_responses_with_usage"], len(results),
        )
    else:
        logger.warning(
            "batch reported NO per-response usage — this leg cannot be "
            "audited from its metadata; see aggregate_batch_usage()",
        )

    # Write outputs
    cost_estimate = write_batch_outputs(
        features=features,
        processed_tiles=processed_tiles,
        failed_tiles=failed_tiles,
        output_file=ctx.output_file,
        config=ctx.prompt_config,
        model_name=ctx.model_name,
        system_instruction=ctx.system_instruction,
        total_detections=total_detections,
        usage_stats=usage_stats,
    )

    cost = cost_estimate.get("total_cost_usd", 0.0)

    print(
        f"  Batch complete: {len(processed_tiles)} tiles, "
        f"{total_detections} detections, "
        f"{len(failed_tiles)} failed, "
        f"${cost:.4f}"
    )

    # Accept if failure count is within tolerance — partial results are
    # preserved on disk and missing tiles can be patched later via
    # --patch-tiles. Threshold scales with batch size (percentage-based)
    # with a minimum floor for small batches.
    total_submitted = len(processed_tiles) + len(failed_tiles)
    max_failures = max(
        MIN_ACCEPTABLE_TILE_FAILURES,
        int(total_submitted * MAX_ACCEPTABLE_TILE_FAILURE_RATE),
    )
    if len(failed_tiles) <= max_failures:
        if failed_tiles:
            print(
                f"  Accepting partial result: "
                f"{len(failed_tiles)} tile(s) failed "
                f"(≤ {max_failures} threshold = "
                f"{MAX_ACCEPTABLE_TILE_FAILURE_RATE:.0%} of "
                f"{total_submitted})"
            )
        return True, "success", cost

    return False, f"partial_failure_{len(failed_tiles)}_tiles", cost


def run_batch_unit(
    unit: dict,
    config: dict,
    output_dir: Path,
    client: Any,
    model_name: str,
    system_instruction: str,
    examples: list[dict],
    config_version: str,
    poll_interval: float = 30.0,
    max_poll_hours: float = 25.0,
    # OPT-IN. Defaulting this on would change the request shape of every
    # existing batch caller, including any re-run of a completed study, which
    # is exactly the retro-fitting the PI ruled out on 2026-09-17. New legs
    # ask for it explicitly.
    use_context_cache: bool = False,
    cache_ttl_seconds: int = 86400,
    limit: int | None = None,
    offset: int = 0,
    dry_run: bool = False,
    on_submit: Callable[[str, list[str], str], None] | None = None,
    resume_job_name: str | None = None,
    tile_size: int | None = None,
    tiles_dir: Path | None = None,
    output_name_suffix: str = "",
) -> tuple[bool, str, float]:
    """
    Orchestrate the full batch lifecycle for one execution unit.

    Backward-compatible wrapper that composes ``prepare_batch_unit()``,
    ``submit_batch_unit()``, ``poll_batch_job()``, and
    ``complete_batch_unit()`` into a single blocking call. This preserves
    the original serial interface while the decomposed functions enable
    parallel orchestration in ``_execute_units_batch()``.

    Args:
        unit: Execution unit dict with condition_name, run, config, etc.
        config: Full study configuration dict.
        output_dir: Base output directory.
        client: Initialised ``google.genai.Client``.
        model_name: Resolved model name for the batch job.
        system_instruction: System instruction text.
        examples: List of example dicts from prompt config.
        config_version: Version string from prompt config.
        poll_interval: Seconds between poll attempts.
        max_poll_hours: Maximum hours to poll.
        limit: Optional tile limit for testing.
        offset: Number of tiles to skip from the start of the manifest.
        dry_run: If True, build JSONL but don't submit.
        on_submit: Optional callback invoked with
            ``(job_name, tile_keys, uploaded_file_name)`` immediately
            after successful submission, before polling begins. Used by
            the caller to persist the job name and uploaded file name to
            a checkpoint (write-ahead pattern) so the job can be
            recovered on crash.
        resume_job_name: If provided, skip upload and submission — go
            straight to polling this existing batch job. Used on resume
            after a crash during the polling phase.
        tile_size: Override tile dimension in pixels for coordinate
            conversion. Forwarded to ``prepare_batch_unit()``.
        tiles_dir: Override tiles directory. Forwarded to
            ``prepare_batch_unit()``.
        output_name_suffix: Suffix for output filenames (e.g.,
            ``"_chunk0"``). Forwarded to ``prepare_batch_unit()``.

    Returns:
        Tuple of (success, message, cost_usd).
    """
    # Phase 1: Prepare
    # One context cache per unit, created before the JSONL is written so the
    # preamble is stored once rather than repeated on every line. Falls back
    # to inline assembly when the prefix is below the explicit-cache minimum
    # (text-only configs) or when creation fails, so caching can never turn a
    # runnable leg into a failed one.
    cached_content = None
    if use_context_cache and dry_run:
        # A dry run must not touch the API. Creating a cache is a billable,
        # persistent resource — an earlier dry run of this leg left eight
        # live caches on the account, one per chunk. A placeholder keeps the
        # request SHAPE inspectable, which is the point of the rehearsal.
        cached_content = "cachedContents/DRY-RUN-PLACEHOLDER"
        logger.info("dry run: using a placeholder cache name, creating none")
    elif use_context_cache:
        cached_content, cache_tokens = create_shared_context_cache(
            client=client,
            model_name=model_name,
            system_instruction=system_instruction,
            examples=examples,
            include_images=config.get("include_example_images", True),
            ttl_seconds=cache_ttl_seconds,
        )
        if cached_content:
            logger.info("batch unit will reference cache %s (%s tokens)",
                        cached_content, f"{cache_tokens:,}")

    ctx = prepare_batch_unit(
        unit=unit,
        config=config,
        output_dir=output_dir,
        model_name=model_name,
        system_instruction=system_instruction,
        examples=examples,
        config_version=config_version,
        # A dry run proves the request SHAPE, which a handful of lines shows
        # as well as all of them. Writing the full file cost 1.34 GB per
        # chunk and 7.6 GB per pass on 2026-09-17, for a rehearsal.
        limit=DRY_RUN_JSONL_LINES if dry_run else limit,
        offset=offset,
        tile_size=tile_size,
        tiles_dir=tiles_dir,
        output_name_suffix=output_name_suffix,
        cached_content=cached_content,
    )
    if ctx is None:
        return False, "no_tiles_found", 0.0

    if dry_run:
        true_total = len(_resolve_tile_paths(unit.get("manifest_path"),
                                             tiles_dir=tiles_dir)) \
            if unit.get("manifest_path") else None
        print(f"  Built SAMPLE JSONL: {ctx.line_count} lines "
              f"(dry run writes at most {DRY_RUN_JSONL_LINES}; "
              f"{ctx.jsonl_path})")
        print(
            f"  [DRY RUN] Would submit batch job for "
            f"{true_total if true_total else 'the full'} tiles; "
            f"no cache created, nothing uploaded, no API call made"
        )
        try:
            ctx.jsonl_path.unlink()
            print("  [DRY RUN] sample JSONL removed")
        except OSError:
            pass
        return True, "dry_run", 0.0

    print(f"  Built JSONL: {ctx.line_count} lines ({ctx.jsonl_path})")

    # Phase 2: Submit (or resume existing job)
    if resume_job_name:
        job_name = resume_job_name
        print(f"  Resuming batch job: {job_name}")
    else:
        try:
            # Pre-lodge storage check. A proposer chunk's JSONL is ~1.3 GB
            # and the Files API caps stored bytes per project (30-day
            # retention), so a chunk that cannot fit must fail before the
            # upload rather than on a 429 part-way through — the same hole
            # that cost the verifier leg of 2026-09-19 14:05 UTC 8 of its
            # 12 chunks. One chunk is in flight here, so the projection
            # covers this chunk only. Over budget, the sweep frees files
            # that no live batch job is reading and the storage is
            # re-audited before the unit is refused.
            preflight_file_storage(
                client, [ctx.jsonl_path], sweep=make_safe_sweep(client),
            )
            job_name, _uploaded_name = submit_batch_unit(
                ctx, client, on_submit,
            )
        except Exception as e:
            return False, f"submit_error: {e}", 0.0

    # Poll until terminal state
    try:
        def _log_progress(job: Any) -> None:
            state = _get_state_name(job.state)
            print(f"  Polling {job.name}: {state}", flush=True)

        completed_job = poll_batch_job(
            client, job_name,
            interval_seconds=poll_interval,
            max_hours=max_poll_hours,
            progress_callback=_log_progress,
        )
    except TimeoutError as e:
        return False, f"poll_timeout: {e}", 0.0
    except Exception as e:
        return False, f"poll_error: {e}", 0.0

    # Phase 3: Complete
    return complete_batch_unit(ctx, client, completed_job)


# ─────────────────────────────────────────────────────────────────────
# Post-Hoc Tile Patching
# ─────────────────────────────────────────────────────────────────────


def patch_failed_tiles(
    unit_dir: Path,
    client: Any,
    max_output_tokens: int = SAFE_MODE_MAX_OUTPUT_TOKENS,
    max_attempts: int = MAX_SYNC_RETRIES,
    dry_run: bool = False,
    tiles_dir: Path | None = None,
    service_tier: str | None = "flex",
) -> dict:
    """
    Patch failed tiles in a completed execution unit.

    Reads ``.tiles.json`` to identify failed tiles, reconstructs the
    prompt configuration from ``.meta.json``, and retries each tile
    via the synchronous API. Uses a two-tier approach:

    1. **Tier 1**: Retry with original parameters (preserves experimental
       conditions). Most failures are stochastic and resolve here.
    2. **Tier 2**: Retry with reduced ``max_output_tokens`` (constrains
       thinking budget to prevent output truncation). Only used when
       tier 1 exhausts all attempts.

    On success, the existing GeoJSON is updated with new detections and
    the ``.tiles.json`` / ``.meta.json`` are amended to reflect recovery.

    Args:
        unit_dir: Path to the unit directory (contains ``.geojson``,
            ``.tiles.json``, and ``.meta.json``).
        client: Initialised ``google.genai.Client``.
        max_output_tokens: Reduced output token limit for tier 2
            safe-mode retries. Defaults to ``SAFE_MODE_MAX_OUTPUT_TOKENS``.
        max_attempts: Maximum retry attempts per tier.
        dry_run: If ``True``, report what would be patched without
            making API calls.
        tiles_dir: Directory containing tile subdirectories. Defaults
            to ``TILES_DIR`` from config when not specified. Override
            for studies using non-default tile sizes (e.g. 384px).
        service_tier: Service tier for the sync retries. Defaults to
            ``"flex"`` (50 % discount, off-peak capacity — standing PI
            instruction 2026-07-30); pass ``None`` for standard tier.

    Returns:
        Dictionary with ``recovered``, ``recovered_safe_mode``,
        ``still_failed``, and ``total_patched`` keys.
    """
    # ── Locate output files ───────────────────────────────────
    located = locate_pass_files(unit_dir)
    if located is None:
        logger.warning("Incomplete or ambiguous unit at %s — skipping", unit_dir)
        return {
            "recovered": [], "recovered_safe_mode": [],
            "still_failed": [], "total_patched": 0,
        }
    geojson_path, tiles_path, meta_path = located

    # ── Read failed tiles ─────────────────────────────────────
    with open(tiles_path) as f:
        tiles_data = json.load(f)

    failed_tiles = tiles_data.get("failed", [])
    if not failed_tiles:
        return {
            "recovered": [], "recovered_safe_mode": [],
            "still_failed": [], "total_patched": 0,
        }

    # ── Extract config from .meta.json ────────────────────────
    with open(meta_path) as f:
        meta_data = json.load(f)

    config_section = meta_data.get("configuration", {})
    snapshot = config_section.get("full_config_snapshot", {})
    system_instruction = config_section.get("system_instruction_text", "")
    model_name = config_section.get("model", "gemini-3-flash")
    examples = snapshot.get("examples", [])
    include_images = config_section.get("include_example_images", True)

    # Resolve model name — configs use marketing names (e.g.
    # 'gemini-3-flash') but the sync API may require '-preview'.
    try:
        available_models = {
            m.name.removeprefix("models/")
            for m in client.models.list()
        }
        if model_name not in available_models:
            preview_name = f"{model_name}-preview"
            if preview_name in available_models:
                logger.info(
                    "Model '%s' not found; resolved to '%s'",
                    model_name, preview_name,
                )
                model_name = preview_name
    except Exception as e:
        logger.warning("Could not resolve model name: %s", e)

    # Reconstruct prompt_config from snapshot
    prompt_config = {
        "temperature": config_section.get("temperature", 0.0),
        "max_output_tokens": config_section.get(
            "max_output_tokens", 8192,
        ),
        "thinking_level": config_section.get("thinking_level"),
        "include_example_images": include_images,
        "examples": examples,
    }

    # Resolve tile size from meta. Use `or` rather than dict.get()
    # default because tile_size may be present but None (not
    # recorded in some configs). Tile size is resolved after tile
    # paths are discovered — see below.

    print(f"  {len(failed_tiles)} failed tile(s) to patch")
    if dry_run:
        for t in sorted(failed_tiles):
            print(f"    [DRY RUN] Would retry: {t}")
        return {
            "recovered": [], "recovered_safe_mode": [],
            "still_failed": failed_tiles, "total_patched": 0,
        }

    # ── Resolve tile paths ────────────────────────────────────
    effective_tiles_dir = tiles_dir if tiles_dir is not None else TILES_DIR
    tile_paths_by_name: dict[str, Path] = {}
    for tile_name in failed_tiles:
        # Search in subdirectories of tiles_dir
        matches = list(effective_tiles_dir.rglob(tile_name))
        if matches:
            tile_paths_by_name[tile_name] = matches[0]
        else:
            logger.warning(
                "Tile file not found: %s", tile_name,
            )

    # ── Resolve tile size ─────────────────────────────────────
    # Use `or` rather than dict.get() default because tile_size
    # may be present but None in meta. When missing, infer from
    # the first resolved tile to avoid assuming 512px default for
    # studies using different tile sizes (e.g. 384px).
    tile_size = config_section.get("tile_size")
    if tile_size is None and tile_paths_by_name:
        first_tile = next(iter(tile_paths_by_name.values()))
        with rasterio.open(first_tile) as src:
            tile_size = src.width
        logger.info("Inferred tile_size=%d from %s", tile_size, first_tile)
    if tile_size is None:
        tile_size = TILE_SIZE

    # ── Tier 1: Retry with original parameters ────────────────
    recovered: list[str] = []
    all_new_features: list[dict] = []
    config_version = snapshot.get("version", "patched")
    pending = [
        t for t in failed_tiles if t in tile_paths_by_name
    ]

    if pending:
        print(f"  Tier 1: retrying {len(pending)} tile(s) "
              f"with original parameters...")
        for attempt in range(1, max_attempts + 1):
            if not pending:
                break
            successes: list[str] = []
            for tile_name in pending:
                try:
                    result = _retry_tile_sync(
                        client=client,
                        tile_path=tile_paths_by_name[tile_name],
                        model_name=model_name,
                        system_instruction=system_instruction,
                        prompt_config=prompt_config,
                        examples=examples,
                        service_tier=service_tier,
                    )
                    if result is not None:
                        retry_matched = {tile_name: result}
                        new_features, dets, failures = (
                            parse_detections_to_geojson(
                                matched_results=retry_matched,
                                tile_paths_by_name=tile_paths_by_name,
                                config_version=config_version,
                                model_name=model_name,
                                tile_size=tile_size,
                            )
                        )
                        if not failures:
                            all_new_features.extend(new_features)
                            recovered.append(tile_name)
                            successes.append(tile_name)
                except Exception as e:
                    logger.warning(
                        "Tier 1 attempt %d error for %s: %s",
                        attempt, tile_name, e,
                    )
            pending = [t for t in pending if t not in successes]

        if recovered:
            print(f"  Tier 1 recovered: {len(recovered)} tile(s)")

    # ── Tier 2: Safe-mode retry (reduced max_output_tokens) ───
    recovered_safe: list[str] = []
    if pending:
        print(
            f"  Tier 2: retrying {len(pending)} tile(s) "
            f"with max_output_tokens={max_output_tokens}..."
        )
        for attempt in range(1, max_attempts + 1):
            if not pending:
                break
            successes = []
            for tile_name in pending:
                try:
                    result = _retry_tile_sync(
                        client=client,
                        tile_path=tile_paths_by_name[tile_name],
                        model_name=model_name,
                        system_instruction=system_instruction,
                        prompt_config=prompt_config,
                        examples=examples,
                        max_output_tokens_override=max_output_tokens,
                        service_tier=service_tier,
                    )
                    if result is not None:
                        retry_matched = {tile_name: result}
                        new_features, dets, failures = (
                            parse_detections_to_geojson(
                                matched_results=retry_matched,
                                tile_paths_by_name=tile_paths_by_name,
                                config_version=config_version,
                                model_name=model_name,
                                tile_size=tile_size,
                            )
                        )
                        if not failures:
                            all_new_features.extend(new_features)
                            recovered_safe.append(tile_name)
                            successes.append(tile_name)
                except Exception as e:
                    logger.warning(
                        "Tier 2 attempt %d error for %s: %s",
                        attempt, tile_name, e,
                    )
            pending = [t for t in pending if t not in successes]

        if recovered_safe:
            print(
                f"  Tier 2 recovered: {len(recovered_safe)} tile(s) "
                f"(safe mode)"
            )

    # ── Merge recovered features into existing GeoJSON ────────
    all_recovered = recovered + recovered_safe
    total_new_detections = len(all_new_features)
    if all_recovered and all_new_features:
        with open(geojson_path) as f:
            existing = json.load(f)
        existing_features = existing.get("features", [])
        existing_features.extend(all_new_features)

        # Update processed_tiles (top-level property, matching
        # _save_geojson which writes collection["processed_tiles"])
        processed = set(existing.get("processed_tiles", []))
        processed.update(all_recovered)
        existing["processed_tiles"] = sorted(processed)
        existing["features"] = existing_features

        with open(geojson_path, "w") as f:
            json.dump(existing, f)

    # ── Update .tiles.json ────────────────────────────────────
    if all_recovered:
        completed_set = set(tiles_data.get("completed", []))
        completed_set.update(all_recovered)
        tiles_data["completed"] = sorted(completed_set)
        tiles_data["failed"] = sorted(pending)
        tiles_data["patched"] = sorted(all_recovered)
        tiles_data["patch_timestamp"] = (
            datetime.now(timezone.utc).isoformat()
        )
        with open(tiles_path, "w") as f:
            json.dump(tiles_data, f, indent=2)

    # ── Update .meta.json with patch results ──────────────────
    if all_recovered:
        # Build a fresh "recovery" meta that represents only this
        # patch pass. ``merge_meta`` then sums it into the original on
        # disc — recording a recovery_history entry, retaining the
        # original token counts / cost / duration, and keeping the
        # original ``items_failed`` arithmetic correct (the merged
        # ``items_failed`` is taken from the recovery's residual list,
        # which is ``pending``).
        patch_completed = list(all_recovered)
        # Pre-existing summary detection count is preserved by
        # ``merge_meta`` (originals win on results_summary). We still
        # update the on-disc original's summary so cost/detection
        # totals continue to match the GeoJSON feature count.
        summary = dict(meta_data.get("results_summary", {}) or {})
        if "total_detections" in summary:
            summary["total_detections"] = (
                summary["total_detections"] + total_new_detections
            )
            meta_data["results_summary"] = summary

        # ``merge_meta`` rebuilds ``completed_items`` as the dedup union
        # of original and recovery's ``completed_items``. The fresh
        # recovery dict below only lists the freshly-patched tiles, so
        # the union correctly equals existing + patched.
        fresh_meta: dict[str, Any] = {
            "execution_stats": {
                "items_processed": len(patch_completed),
                "items_failed": 0,
                "completed_items": patch_completed,
                "failed_items": list(pending),
            },
            "timestamp": {
                "start": datetime.now(timezone.utc).isoformat(),
                "end": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": 0.0,
            },
            "cost_estimate": {
                "input_cost_usd": 0.0,
                "output_cost_usd": 0.0,
                "total_cost_usd": 0.0,
            },
        }

        # Use the already-loaded ``meta_data`` (the on-disc original)
        # as the merge base — no need to re-read.
        merged = merge_meta(meta_data, fresh_meta)

        # Atomic write — rename a .tmp sibling to avoid truncation on kill.
        tmp_meta = meta_path.with_suffix(meta_path.suffix + ".tmp")
        with open(tmp_meta, "w") as f:
            json.dump(merged, f, indent=2)
        tmp_meta.replace(meta_path)

    # ── Report ────────────────────────────────────────────────
    if pending:
        print(f"  Still failed: {len(pending)} tile(s)")
        for t in sorted(pending):
            print(f"    {t}")

    return {
        "recovered": recovered,
        "recovered_safe_mode": recovered_safe,
        "still_failed": pending,
        "total_patched": len(all_recovered),
    }
