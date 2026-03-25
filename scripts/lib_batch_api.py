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
import time
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Callable
from typing import Any

import geojson
import rasterio
from shapely.geometry import box, mapping

from config import EXAMPLES_DIR, TILE_SIZE, TILES_DIR
from scripts.lib_llm_metadata import (
    AggregatedUsage,
    LLMMetadataTracker,
    LLMProvider,
    estimate_cost,
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

# Maximum tile-level failures before a batch unit is rejected.
# At 340 tiles, 10 failures = ~3% — acceptable for consensus voting
# studies (K=30 runs, each tile gets many chances). Individual failed
# tiles can be patched later via --patch-tiles mode.
MAX_ACCEPTABLE_TILE_FAILURES = 10

# Maximum synchronous retry attempts for tiles that fail JSON parsing
# after a batch job completes. Empirically, ~74% resolve on attempt 1,
# ~98% by attempt 3. At 10 attempts, even 60% per-attempt failure
# rates resolve with P(all fail) = 0.6%. No observed tile exceeds
# 60% failure rate.
MAX_SYNC_RETRIES = 10

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


def cleanup_batch_files(
    client: Any,
    file_names: list[str],
    label: str = "",
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

    Returns:
        Tuple of ``(deleted_count, error_count)``.
    """
    prefix = f"[{label}] " if label else ""
    deleted = 0
    errors = 0

    for name in file_names:
        if not name:
            continue
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


def sweep_stale_files_safe(
    client: Any,
    registry_path: Path,
    grace_minutes: float = 5.0,
) -> tuple[int, float]:
    """
    Concurrency-safe orphan cleanup using a shared file registry.

    Safe to call from any process — uses the shared registry at
    ``registry_path`` to determine which files are actively in use
    across all concurrent processes. Files not in the registry and
    older than ``grace_minutes`` are deleted.

    The grace period covers the window between a file being uploaded
    and being registered (typically < 1 second, but 5 minutes
    provides a generous safety margin).

    Args:
        client: Initialised ``google.genai.Client``.
        registry_path: Path to the shared ``.active_files.json``.
        grace_minutes: Files younger than this are always preserved,
            regardless of registry state. Default 5 minutes.

    Returns:
        Tuple of ``(deleted_count, freed_gb)``.
    """
    from datetime import datetime, timezone

    from scripts.lib_file_registry import get_registered_files

    # Get the set of files registered by all processes
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
        "%d registered (protected), deleting...",
        len(stale_names), freed_gb, len(registered),
    )

    deleted, _errors = cleanup_batch_files(
        client, stale_names, label="safe-sweep",
    )
    return deleted, freed_gb


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


def build_jsonl_file(
    tile_paths: list[Path],
    config: dict,
    system_instruction: str,
    examples: list[dict],
    output_path: Path,
) -> int:
    """
    Build a JSONL request file for one execution unit.

    Each line contains one tile's complete request, including all
    reference images (duplicated per line since the Batch API has no
    shared-context mechanism).

    Args:
        tile_paths: List of tile image paths to process.
        config: Prompt config dict (temperature, max_output_tokens, etc.).
        system_instruction: System instruction text.
        examples: List of example dicts from prompt config.
        output_path: Where to write the JSONL file.

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

            # Reference examples preamble (always present)
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
            line = {
                "key": tile_path.name,
                "request": {
                    "contents": [
                        {
                            "parts": content_parts,
                            "role": "user",
                        }
                    ],
                    "system_instruction": {
                        "parts": [{"text": system_instruction}],
                    },
                    "generation_config": generation_config,
                },
            }

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
) -> str:
    """
    Upload a JSONL file via the Google Files API.

    Args:
        client: Initialised ``google.genai.Client``.
        jsonl_path: Path to the local JSONL file.
        display_name: Optional human-readable name for the upload.

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

    Returns:
        The BatchJob in its terminal state.

    Raises:
        TimeoutError: If ``max_hours`` exceeded without reaching
            a terminal state.
    """
    max_seconds = max_hours * 3600
    start = time.monotonic()

    while True:
        job = client.batches.get(name=job_name)
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

    # Build usage from batch job stats if available
    usage = AggregatedUsage()
    if usage_stats:
        usage.total_input_tokens = usage_stats.get("input_tokens", 0)
        usage.total_output_tokens = usage_stats.get("output_tokens", 0)
        usage.total_tokens = usage_stats.get("total_tokens", 0)
    tracker.usage = usage

    # Estimate costs (batch API gets 50% discount)
    cost_estimate = estimate_cost(
        usage=usage,
        provider=LLMProvider.GEMINI.value,
        model=model_name,
    )
    # Apply 50% batch discount
    cost_estimate["input_cost_usd"] = round(
        cost_estimate["input_cost_usd"] * 0.5, 6
    )
    cost_estimate["output_cost_usd"] = round(
        cost_estimate["output_cost_usd"] * 0.5, 6
    )
    cost_estimate["total_cost_usd"] = round(
        cost_estimate["input_cost_usd"] + cost_estimate["output_cost_usd"], 6
    )
    cost_estimate["pricing_used"]["batch_discount"] = 0.5

    meta = tracker.finalise(include_per_item=False)
    meta["cost_estimate"] = cost_estimate
    meta["batch_api"] = {
        "execution_mode": "batch",
        "batch_discount_applied": True,
    }

    meta_path = output_file.with_suffix(".meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

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
            for t in map_dir.glob("*.png"):
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
    tile_size: int | None = None,
    tiles_dir: Path | None = None,
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
        tile_size: Tile dimension in pixels for coordinate conversion.
            Defaults to TILE_SIZE (512) when not specified.
        tiles_dir: Directory containing tile subdirectories. Defaults to
            TILES_DIR from config when not specified.

    Returns:
        A ``BatchUnitContext`` carrying all state needed for submission
        and completion, or ``None`` if no tiles were found.
    """
    inputs = config["inputs"]
    manifest_path = Path(config.get("_project_root", ".")) / inputs["manifest"]

    # Build output path: {output_dir}/{condition_name}/run_{K}/
    run_dir = output_dir / unit["condition_name"] / f"run_{unit['run']}"
    output_name = f"detections_{unit['condition_name']}_run{unit['run']:02d}"
    output_file = run_dir / f"{output_name}.geojson"

    # Resolve tiles (use overridden tiles_dir if provided)
    tile_paths = _resolve_tile_paths(manifest_path, tiles_dir=tiles_dir)
    if limit and limit > 0:
        tile_paths = tile_paths[:limit]

    if not tile_paths:
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
    )

    key = f"{unit['condition_name']}/run_{unit['run']}"

    # Use provided tile_size or fall back to config default
    effective_tile_size = tile_size if tile_size is not None else TILE_SIZE

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
    uploaded_name = upload_jsonl(client, ctx.jsonl_path, display_name)
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

    # Extract usage stats from batch job metadata if available
    usage_stats = None
    if hasattr(completed_job, "usage_metadata"):
        um = completed_job.usage_metadata
        usage_stats = {
            "input_tokens": getattr(um, "prompt_token_count", 0) or 0,
            "output_tokens": (
                getattr(um, "candidates_token_count", 0) or 0
            ),
            "total_tokens": getattr(um, "total_token_count", 0) or 0,
        }

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

    # Accept with small failure count — partial results are preserved
    # on disk and missing tiles can be patched later via --patch-tiles.
    if len(failed_tiles) <= MAX_ACCEPTABLE_TILE_FAILURES:
        if failed_tiles:
            print(
                f"  Accepting partial result: "
                f"{len(failed_tiles)} tile(s) "
                f"failed (≤ {MAX_ACCEPTABLE_TILE_FAILURES} threshold)"
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
    limit: int | None = None,
    dry_run: bool = False,
    on_submit: Callable[[str, list[str], str], None] | None = None,
    resume_job_name: str | None = None,
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

    Returns:
        Tuple of (success, message, cost_usd).
    """
    # Phase 1: Prepare
    ctx = prepare_batch_unit(
        unit=unit,
        config=config,
        output_dir=output_dir,
        model_name=model_name,
        system_instruction=system_instruction,
        examples=examples,
        config_version=config_version,
        limit=limit,
    )
    if ctx is None:
        return False, "no_tiles_found", 0.0

    print(f"  Built JSONL: {ctx.line_count} lines ({ctx.jsonl_path})")

    if dry_run:
        print(
            f"  [DRY RUN] Would submit batch job for "
            f"{ctx.line_count} tiles"
        )
        return True, "dry_run", 0.0

    # Phase 2: Submit (or resume existing job)
    if resume_job_name:
        job_name = resume_job_name
        print(f"  Resuming batch job: {job_name}")
    else:
        try:
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

    Returns:
        Dictionary with ``recovered``, ``recovered_safe_mode``,
        ``still_failed``, and ``total_patched`` keys.
    """
    # ── Locate output files ───────────────────────────────────
    geojson_files = list(unit_dir.glob("*.geojson"))
    tiles_files = list(unit_dir.glob("*.tiles.json"))
    meta_files = list(unit_dir.glob("*.meta.json"))

    if not geojson_files or not tiles_files or not meta_files:
        logger.warning("Incomplete unit at %s — skipping", unit_dir)
        return {
            "recovered": [], "recovered_safe_mode": [],
            "still_failed": [], "total_patched": 0,
        }

    geojson_path = geojson_files[0]
    tiles_path = tiles_files[0]
    meta_path = meta_files[0]

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

    # Resolve tile size from meta (default 512)
    tile_size = config_section.get("tile_size", TILE_SIZE)

    print(f"  {len(failed_tiles)} failed tile(s) to patch")
    if dry_run:
        for t in sorted(failed_tiles):
            print(f"    [DRY RUN] Would retry: {t}")
        return {
            "recovered": [], "recovered_safe_mode": [],
            "still_failed": failed_tiles, "total_patched": 0,
        }

    # ── Resolve tile paths ────────────────────────────────────
    tile_paths_by_name: dict[str, Path] = {}
    for tile_name in failed_tiles:
        # Search in subdirectories of TILES_DIR
        matches = list(TILES_DIR.rglob(tile_name))
        if matches:
            tile_paths_by_name[tile_name] = matches[0]
        else:
            logger.warning(
                "Tile file not found: %s", tile_name,
            )

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

    # ── Update .meta.json failure count ───────────────────────
    if all_recovered:
        exec_stats = meta_data.get("execution_stats", {})
        items_failed = exec_stats.get("items_failed", 0)
        items_processed = exec_stats.get("items_processed", 0)
        exec_stats["items_failed"] = max(
            0, items_failed - len(all_recovered),
        )
        exec_stats["items_processed"] = (
            items_processed + len(all_recovered)
        )
        meta_data["execution_stats"] = exec_stats

        # Update total_detections to include recovered tiles'
        # detections (the GeoJSON features have already been extended)
        summary = meta_data.get("results_summary", {})
        if "total_detections" in summary:
            summary["total_detections"] = (
                summary["total_detections"] + total_new_detections
            )
            meta_data["results_summary"] = summary

        with open(meta_path, "w") as f:
            json.dump(meta_data, f, indent=2)

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
