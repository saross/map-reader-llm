# Plan: Concurrency-Safe File Storage Sweep via Shared Registry

## Context

The proactive sweep mechanism added to `run_phase2.py` caused 404 NOT_FOUND failures when running multiple batch processes concurrently. Each process builds its "active set" from its own `batch_pending` dict, so files uploaded by other processes appear as orphans and get deleted. This caused Config D and Config A run_9 to fail.

The sweep was disabled as a hotfix. We need a permanent solution that:

1. Prevents storage from filling with orphaned files
2. Is safe when multiple processes share the same Google Files API account
3. Works correctly during multi-day batch runs

## Approach: Shared File Registry

A single registry file (`outputs/.active_files.json`) acts as the source of truth for which files are in use across all processes. Processes register files on upload and deregister on deletion. The sweep deletes anything not in the registry (plus a 5-minute grace period for recent uploads to cover the upload→register race).

### Registry format

```json
{
  "version": 1,
  "files": {
    "files/abc123": {
      "registered_by": "text-t0.7/run_7",
      "registered_at": "2026-03-22T14:30:45+00:00",
      "study": "h11-384-pv-diag-text-n10"
    },
    "files/def456": {
      "registered_by": "h9-A-p1/run_1",
      "registered_at": "2026-03-22T14:31:02+00:00",
      "study": "phase3c-h9-diversity-track1"
    }
  }
}
```

### Concurrency protocol

- **Locking**: `fcntl.flock(fd, LOCK_EX)` for writes, `LOCK_SH` for reads. Advisory locks on Linux; released automatically on process crash.
- **Atomic writes**: Write to temp file, then `os.replace()` (atomic on POSIX).
- **Crash recovery**: If a process crashes, its registry entries remain (safe — files preserved). Entries older than 48 hours (the Google Files API auto-expiry window) are cleaned on next sweep.

### Sweep algorithm

```text
1. Read registry (shared lock)
2. List all files via client.files.list()
3. For each file:
   a. If in registry → keep
   b. If created < 5 minutes ago → keep (grace period)
   c. If not in registry and > 5 min old → delete
4. Clean registry entries older than 48h (stale crash remnants)
```

---

## Changes

### 1. New module: `scripts/lib_file_registry.py`

Three functions with file locking:

- **`register_file(registry_path, file_name, unit_key, study_name)`**
  Called after successful upload. Acquires exclusive lock, adds entry, writes atomically.

- **`deregister_file(registry_path, file_name)`**
  Called after successful deletion. Acquires exclusive lock, removes entry.

- **`get_registered_files(registry_path) → set[str]`**
  Called by sweep. Acquires shared lock, returns set of active file names. Also prunes entries older than 48 hours.

### 2. Update `scripts/lib_batch_api.py`

**`sweep_stale_files_safe()`** — new function replacing `sweep_stale_files()`:

```python
def sweep_stale_files_safe(
    client: Any,
    registry_path: Path,
    grace_minutes: float = 5.0,
) -> tuple[int, float]:
```

- Reads registered files via `get_registered_files()`
- Lists all files via `client.files.list()`
- Deletes files not registered AND older than grace period
- Returns `(deleted_count, freed_gb)`

Keep `sweep_stale_files()` with deprecation comment for reference.

### 3. Update `scripts/run_phase2.py`

**Registration points** (2 locations):

- After upload in `_submit_one()` (around line 1740): call `register_file()` with the uploaded file name
- After deletion in `_handle_completion()` cleanup (around line 1843): call `deregister_file()` for input and output files

**Sweep updates** (3 locations):

- `_proactive_sweep()`: call `sweep_stale_files_safe()` with registry path. Re-enable periodic sweep (every 10 cycles).
- Reactive sweep (quota-error path, ~line 1765): use `sweep_stale_files_safe()`
- Final sweep on exit: use `sweep_stale_files_safe()`

**Registry path**: Derive from the study's output_dir parent, defaulting to `outputs/.active_files.json`.

---

## Files to create

- `scripts/lib_file_registry.py` — registry read/write/prune with file locking

## Files to modify

- `scripts/lib_batch_api.py` — add `sweep_stale_files_safe()`, deprecate old `sweep_stale_files()`
- `scripts/run_phase2.py` — register/deregister calls at upload/delete points, update sweep calls, re-enable periodic sweep

## Verification

1. **Lint**: `ruff check scripts/lib_file_registry.py scripts/lib_batch_api.py scripts/run_phase2.py`
2. **Tests**: `pytest tests/ -m tier1`
3. **Code audit**: `/audit scripts/lib_file_registry.py scripts/lib_batch_api.py scripts/run_phase2.py` — all modified and new files
4. **Manual verification**:
   - Start two processes concurrently — registry should contain both processes' files
   - Kill one process — its files should remain registered (safe)
   - Sweep should only delete unregistered files older than 5 minutes
   - After both processes finish, final sweep should clean everything
