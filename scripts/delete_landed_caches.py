#!/usr/bin/env python3
"""Delete a batch campaign's context caches once no pass can still read them.

Why this exists
---------------
The detector's batch path (``lib_batch_api.run_batch_unit`` with
``use_context_cache``) creates one explicit context cache per pass with a
24-hour time to live and never deletes it, so every cache is billed for
storage for its full day after its job has finished. A refused or failed
lodge also leaves its cache behind (Run B pre-launch audit, finding F4:
about US$0.45 per Gemini 3 cache, US$0.23 per Gemini 3.7 cache). The PI
ruled on 2026-10-07 (D52): "yes, please do delete context caches when they
are no longer needed".

The rule
--------
A cache is deleted only when ALL of these hold:

1. its display name is the detector's (``batch-detect-shared-prefix``) and
   it was created at or after ``--since`` (so caches from other work are
   never touched);
2. it is older than ``--grace-minutes`` (default 90): a lodge creates its
   cache before it writes and uploads the request file, so a young cache
   may belong to a lodge still in progress;
3. no pass under ``--out`` that is still live or in flight names it in its
   request file. A pass is live when its pid file names a running process,
   and in flight when its log shows a submitted job since its latest lodge
   but its final GeoJSON has not landed. A landed pass, or a lodge that
   exited before submitting, protects nothing.

``--dry-run`` lists what would be deleted. It still lists the account's
caches (a metadata call, no tokens), but deletes nothing.

Usage (repository root, on the machine that runs the campaign)::

    python scripts/delete_landed_caches.py \\
        --out outputs/modality-bridge-2026-10-07 \\
        --since 2026-10-07T12:00:00Z --dry-run
    python scripts/delete_landed_caches.py \\
        --out outputs/modality-bridge-2026-10-07 --since 2026-10-07T12:00:00Z

Created: 2026-10-07 (Session 163)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

#: The display name ``create_shared_context_cache`` gives every cache.
DETECTOR_CACHE_DISPLAY_NAME = "batch-detect-shared-prefix"


@dataclass
class PassState:
    """What one pass (or recovery fragment) says about its cache.

    Attributes:
        name: The launcher's pass name (log stem), e.g. ``g3-image-run1``.
        cache: The cache its newest request file names, if any.
        protects: True when the pass is live or in flight.
        why: A short reason, for the report.
    """

    name: str
    cache: str | None
    protects: bool
    why: str


def request_cache(pass_dir: Path) -> str | None:
    """Return the cache named by the newest request file of a pass.

    Args:
        pass_dir: ``…/<version>/run_<N>`` (holds ``batch_working/``).

    Returns:
        The ``cached_content`` of the first request line, or ``None``.
    """
    files = sorted((pass_dir / "batch_working").glob("*.jsonl"),
                   key=lambda p: p.stat().st_mtime)
    if not files:
        return None
    with open(files[-1]) as fh:
        first = fh.readline()
    if not first.strip():
        return None
    return json.loads(first).get("request", {}).get("cached_content")


def pid_alive(pid_file: Path) -> bool:
    """True when the pid file names a running process (``kill -0``)."""
    try:
        os.kill(int(pid_file.read_text().strip()), 0)
    except (FileNotFoundError, ValueError, ProcessLookupError):
        return False
    except PermissionError:
        return True
    return True


def submitted_since_latest_lodge(log_text: str, name: str) -> bool:
    """True when the log shows a submitted job after the pass's latest lodge.

    Args:
        log_text: The pass's log.
        name: The pass name the launcher writes in its ``LODGE`` lines.

    Returns:
        Whether ``Submitted batch job`` follows the last ``LODGE <name>:``.
    """
    marks = [m.end() for m in re.finditer(rf"=== \S+ LODGE {re.escape(name)}:", log_text)]
    tail = log_text[marks[-1]:] if marks else log_text
    return "Submitted batch job" in tail


def pass_states(out: Path) -> list[PassState]:
    """Classify every pass with a log under ``out/logs``.

    The pass directory is found from the log name the launcher writes:
    ``<arm>-run<N>`` for a main pass, ``<arm>-run<N>_rd<R>`` for a recovery
    fragment under ``<arm>/recovery_rd<R>/``.

    Args:
        out: The campaign's output root.

    Returns:
        One :class:`PassState` per log.
    """
    states = []
    for log in sorted((out / "logs").glob("*.log")):
        name = log.stem
        arm, _, rest = name.rpartition("-run")
        run, _, rd = rest.partition("_rd")
        root = out / arm / f"recovery_rd{rd}" if rd else out / arm
        pass_dirs = list(root.glob(f"*/run_{run}"))
        cache = request_cache(pass_dirs[0]) if len(pass_dirs) == 1 else None
        landed = bool(pass_dirs) and any(
            p for p in pass_dirs[0].glob("detections_*.geojson") if "_chunk" not in p.name
        )
        live = pid_alive(out / "pids" / f"{name}.pid")
        in_flight = submitted_since_latest_lodge(log.read_text(errors="replace"), name)
        if live:
            states.append(PassState(name, cache, True, "process live"))
        elif in_flight and not landed:
            states.append(PassState(name, cache, True, "job submitted, not landed"))
        else:
            why = "landed" if landed else "exited without submitting"
            states.append(PassState(name, cache, False, why))
    return states


def select_deletable(
    caches: list[dict[str, Any]], states: list[PassState], since: datetime,
    now: datetime, grace: timedelta,
) -> list[str]:
    """Apply the module's rule to a cache listing.

    Args:
        caches: One dict per cache with ``name``, ``display_name`` and
            ``create_time`` (timezone-aware).
        states: The campaign's passes.
        since: Earliest creation time considered.
        now: The current time.
        grace: Minimum age before a cache may be deleted.

    Returns:
        The names of the caches to delete.

    Example:
        >>> t = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)
        >>> c = [{"name": "cachedContents/a", "display_name":
        ...       DETECTOR_CACHE_DISPLAY_NAME, "create_time": t}]
        >>> select_deletable(c, [], t, t + timedelta(hours=3), timedelta(minutes=90))
        ['cachedContents/a']
    """
    protected = {s.cache for s in states if s.protects and s.cache}
    unknown_live = any(s.protects and not s.cache for s in states)
    out = []
    for c in caches:
        if c.get("display_name") != DETECTOR_CACHE_DISPLAY_NAME:
            continue
        created = c.get("create_time")
        if created is None or created < since or now - created < grace:
            continue
        if c["name"] in protected:
            continue
        if unknown_live:
            # A live pass whose request file is not readable yet could be
            # using any cache: delete nothing until it is.
            return []
        out.append(c["name"])
    return out


def main() -> int:
    """Parse arguments, classify passes, list caches and delete the stale ones."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--since", required=True,
                        help="ISO time; caches created earlier are never touched")
    parser.add_argument("--grace-minutes", type=float, default=90.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    since = datetime.fromisoformat(args.since.replace("Z", "+00:00"))
    states = pass_states(args.out)
    for s in states:
        print(f"{s.name:24s} {'PROTECTS' if s.protects else 'free':8s} "
              f"{s.why:28s} {s.cache or '-'}")

    from google import genai

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from config import GOOGLE_API_KEY  # noqa: E402  (repository-root config)

    client = genai.Client(api_key=GOOGLE_API_KEY)
    caches = []
    for c in client.caches.list():
        created = getattr(c, "create_time", None)
        if created is not None and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        caches.append({"name": c.name, "display_name": getattr(c, "display_name", None),
                       "create_time": created})
    doomed = select_deletable(caches, states, since, datetime.now(timezone.utc),
                              timedelta(minutes=args.grace_minutes))
    print(f"{len(caches)} cache(s) listed; {len(doomed)} to delete"
          + (" (dry run)" if args.dry_run else ""))
    for name in doomed:
        if args.dry_run:
            print(f"  would delete {name}")
            continue
        try:
            client.caches.delete(name=name)
            print(f"  deleted {name}")
        except Exception as exc:  # noqa: BLE001 - one failure must not stop the rest
            print(f"  FAILED to delete {name}: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
