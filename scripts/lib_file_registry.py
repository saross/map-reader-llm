#!/usr/bin/env python3
"""
Shared file registry for concurrency-safe Google Files API storage management.

Provides a registry file (``outputs/.active_files.json``) that tracks which
uploaded files are currently in use across concurrent ``run_phase2.py``
processes. The sweep function uses this registry to determine which files
are safe to delete, avoiding the race condition where one process's sweep
deletes files uploaded by another process.

Concurrency protocol:
    - **Writes** (register/deregister): exclusive lock via ``fcntl.flock``
    - **Reads** (get_registered_files): shared lock via ``fcntl.flock``
    - **Atomic writes**: write to temp file, then ``os.replace()``
    - **Crash recovery**: locks released automatically; stale entries
      pruned after 48 hours (the Google Files API auto-expiry window)

Usage::

    from scripts.lib_file_registry import (
        register_file,
        deregister_file,
        get_registered_files,
    )

    # After uploading a file
    register_file(registry_path, "files/abc123", "text-t0.7/run_7", "my-study")

    # After deleting a file
    deregister_file(registry_path, "files/abc123")

    # During sweep — get set of protected file names
    active = get_registered_files(registry_path)

Created: 2026-03-22
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import fcntl
import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Stale registry entries are pruned after this many hours.
# Matches the Google Files API auto-expiry window.
_STALE_ENTRY_HOURS = 48.0

# Registry file format version — bump if the schema changes.
_REGISTRY_VERSION = 1


def _read_registry(registry_path: Path) -> dict:
    """
    Read the registry file, returning the parsed dict.

    Returns an empty registry structure if the file does not exist
    or cannot be parsed.

    Args:
        registry_path: Path to the registry JSON file.

    Returns:
        Registry dict with ``version`` and ``files`` keys.
    """
    if not registry_path.exists():
        return {"version": _REGISTRY_VERSION, "files": {}}

    try:
        with open(registry_path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "files" not in data:
            logger.warning(
                "Malformed registry at %s — resetting",
                registry_path,
            )
            return {"version": _REGISTRY_VERSION, "files": {}}
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(
            "Could not read registry %s: %s — resetting",
            registry_path, e,
        )
        return {"version": _REGISTRY_VERSION, "files": {}}


def _write_registry_atomic(registry_path: Path, data: dict) -> None:
    """
    Write the registry dict to disk atomically.

    Writes to a temporary file in the same directory, then uses
    ``os.replace()`` (atomic on POSIX) to swap it into place.
    This prevents partial writes from corrupting the registry.

    Args:
        registry_path: Path to the registry JSON file.
        data: Registry dict to write.
    """
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=registry_path.parent,
        prefix=".active_files_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
            f.write("\n")
        os.replace(tmp_path, registry_path)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def register_file(
    registry_path: Path,
    file_name: str,
    unit_key: str = "",
    study_name: str = "",
) -> None:
    """
    Register an uploaded file as active in the shared registry.

    Call this immediately after a successful ``client.files.upload()``.
    Uses exclusive file locking to prevent concurrent write corruption.

    Args:
        registry_path: Path to the registry JSON file.
        file_name: Google Files API resource name (e.g., ``"files/abc123"``).
        unit_key: Identifier for the execution unit (e.g., ``"text-t0.7/run_7"``).
        study_name: Study name for diagnostic logging.
    """
    if not file_name:
        return

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = registry_path.with_suffix(".lock")

    with open(lock_path, "a", encoding="utf-8") as lock_fd:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        try:
            data = _read_registry(registry_path)
            data["files"][file_name] = {
                "registered_by": unit_key,
                "registered_at": datetime.now(
                    timezone.utc,
                ).isoformat(),
                "study": study_name,
            }
            _write_registry_atomic(registry_path, data)
            logger.debug(
                "Registered file %s (unit=%s, study=%s)",
                file_name, unit_key, study_name,
            )
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)


def deregister_file(
    registry_path: Path,
    file_name: str,
) -> None:
    """
    Remove a file from the shared registry after deletion.

    Call this after successfully deleting a file from the Google
    Files API. Uses exclusive file locking.

    Args:
        registry_path: Path to the registry JSON file.
        file_name: Google Files API resource name to deregister.
    """
    if not file_name:
        return

    if not registry_path.exists():
        return

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = registry_path.with_suffix(".lock")

    with open(lock_path, "a", encoding="utf-8") as lock_fd:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        try:
            data = _read_registry(registry_path)
            if file_name in data["files"]:
                del data["files"][file_name]
                _write_registry_atomic(registry_path, data)
                logger.debug("Deregistered file %s", file_name)
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)


def get_registered_files(
    registry_path: Path,
    prune_stale: bool = True,
) -> set[str]:
    """
    Get the set of currently registered (active) file names.

    Optionally prunes entries older than 48 hours (the Google Files API
    auto-expiry window) — these are remnants from crashed processes
    whose files have already expired server-side.

    Uses shared file locking (multiple readers allowed).

    Args:
        registry_path: Path to the registry JSON file.
        prune_stale: If True, remove entries older than 48 hours.

    Returns:
        Set of file resource names (e.g., ``{"files/abc123", ...}``).
    """
    if not registry_path.exists():
        return set()

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = registry_path.with_suffix(".lock")

    with open(lock_path, "a", encoding="utf-8") as lock_fd:
        # Use exclusive lock if pruning (we'll write), shared otherwise
        lock_mode = fcntl.LOCK_EX if prune_stale else fcntl.LOCK_SH
        fcntl.flock(lock_fd, lock_mode)
        try:
            data = _read_registry(registry_path)
            files = data.get("files", {})

            if prune_stale and files:
                now = datetime.now(timezone.utc)
                stale_keys = []
                for name, info in files.items():
                    registered_at = info.get("registered_at", "")
                    try:
                        reg_time = datetime.fromisoformat(
                            registered_at,
                        )
                        age_hours = (
                            now - reg_time
                        ).total_seconds() / 3600
                        if age_hours > _STALE_ENTRY_HOURS:
                            stale_keys.append(name)
                    except (ValueError, TypeError):
                        # Malformed timestamp — prune it
                        stale_keys.append(name)

                if stale_keys:
                    for key in stale_keys:
                        del files[key]
                    _write_registry_atomic(registry_path, data)
                    logger.info(
                        "Pruned %d stale registry entries (>%dh)",
                        len(stale_keys),
                        int(_STALE_ENTRY_HOURS),
                    )

            return set(files.keys())
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
