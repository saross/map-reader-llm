#!/usr/bin/env python3
"""Wait for a long-running job to reach a TERMINAL state, then say which one.

The contract this encodes (beacon S155, defect D1): a watcher keys on the job
having STOPPED, and only then reads HOW it stopped. It never keys on a success
string. The overnight chain of 2026-09-17 waited for ``"Tiles processed:"`` in
the run log; a PARTIAL failure never prints that line, so when run 5 failed one
chunk of seven the chain sat at its first step for the whole window while the
job it was waiting for had been finished for hours. A success marker cannot
distinguish "not yet" from "never", and a chain that cannot tell those apart
cannot hand a failure to anyone.

Terminal states, in the order they are checked each poll:

    success   the log carries a completion line and no failures
    partial   the log says the job finished with failures
    crashed   the log carries a Python traceback after its last progress
    stale     the log has not been written for ``--stale-seconds`` (a hang
              looks exactly like a death from outside; both are terminal)
    stopped   the watched process is gone and the log says nothing terminal

Exit status is the state, so a shell chain can branch on it::

    0 success   2 partial   3 crashed   4 stale   5 stopped

Everything except ``success`` is a stop-and-read for the operator. A chain
that proceeds on anything but 0 is repeating the defect this script exists to
close.

Usage::

    # wait on the log alone (staleness is the only liveness signal)
    python scripts/wait_for_run.py --log outputs/<run>/batch_run5.log

    # also watch the process, so a death is seen at once rather than after
    # the staleness window
    python scripts/wait_for_run.py --log ... --pid $! --stale-seconds 3600

    # in a chain
    python scripts/wait_for_run.py --log "$LOG" --pidfile "$PIDFILE" \\
        || { echo "run ended in state $?; not continuing"; exit 1; }

Markers are those printed by ``scripts/4_detect_mounds_batch.py`` in both
modes. Add ``--marker STATE=REGEX`` for a driver with its own vocabulary.

Created: 2026-09-18 (S155)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import os
import re
import time
from pathlib import Path

#: Exit status per terminal state. ``running`` is not terminal and has none.
EXIT_STATUS = {"success": 0, "partial": 2, "crashed": 3, "stale": 4,
               "stopped": 5}

#: Default markers, as regular expressions searched over the whole log. The
#: LAST marker by position decides, so a traceback from a retried chunk that
#: the driver then completed does not mask the completion — and a completion
#: line followed by a traceback is a crash on the way out, not a success.
DEFAULT_MARKERS: dict[str, list[str]] = {
    "success": [r"^Batch complete\.", r"^Tiles processed: \d+"],
    "partial": [r"^Batch partially failed"],
    "crashed": [r"^Traceback \(most recent call last\)"],
}

#: A real-time run prints ``Tiles processed`` AND ``Tiles failed`` on every
#: exit, so a non-zero failure count after the completion line downgrades
#: success to partial.
FAILED_COUNT = re.compile(r"^Tiles failed: (\d+)", re.MULTILINE)


def classify_log(text: str, markers: dict[str, list[str]] | None = None) -> str:
    """Return the terminal state a log describes, or ``"running"``.

    Args:
        text: The log's contents so far.
        markers: State name to list of regexes (multi-line mode); defaults to
            :data:`DEFAULT_MARKERS`.

    Returns:
        ``"success"``, ``"partial"``, ``"crashed"`` or ``"running"``.

    Examples:
        >>> classify_log("Batch complete. Estimated cost: $1\\nTiles processed: 9\\n")
        'success'
        >>> classify_log("...\\nBatch partially failed (some chunks errored)\\n")
        'partial'
        >>> classify_log("Tiles processed: 9\\nTiles failed: 2\\n")
        'partial'
        >>> classify_log("still going\\n")
        'running'
    """
    markers = markers or DEFAULT_MARKERS
    last_pos, last_state = -1, "running"
    for state, patterns in markers.items():
        for pat in patterns:
            for m in re.finditer(pat, text, re.MULTILINE):
                if m.start() > last_pos:
                    last_pos, last_state = m.start(), state
    if last_state == "success":
        # Any failure count reported after the completion line is a partial.
        for m in FAILED_COUNT.finditer(text):
            if m.start() > last_pos and int(m.group(1)) > 0:
                return "partial"
    return last_state


def pid_alive(pid: int) -> bool:
    """True if a process with *pid* exists (signal 0 probe)."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def log_age_seconds(log: Path, now: float | None = None) -> float | None:
    """Seconds since *log* was last written, or ``None`` if it does not exist."""
    try:
        mtime = log.stat().st_mtime
    except FileNotFoundError:
        return None
    return (now if now is not None else time.time()) - mtime


def wait_for_terminal(log: Path, pid: int | None = None,
                      stale_seconds: float = 3600.0, poll_seconds: float = 60.0,
                      markers: dict[str, list[str]] | None = None,
                      grace_seconds: float = 5.0,
                      sleep=time.sleep, clock=time.time) -> str:
    """Block until the job is in a terminal state and return that state.

    Args:
        log: The job's log file. Staleness is judged on its mtime. A log
            that has not APPEARED after ``stale_seconds`` is stale too —
            a mistyped path or a job that never started must not wait
            forever (audit lens A, 2026-09-19).
        pid: The job's process id, if known. A dead process is terminal at
            once; without a pid, only staleness or a marker ends the wait.
        stale_seconds: Silence on the log that counts as a hang.
        poll_seconds: Interval between checks.
        markers: Override for :data:`DEFAULT_MARKERS`.
        grace_seconds: After the process is seen dead, how long to allow the
            log to flush before classifying it.
        sleep: Injected for tests.
        clock: Injected for tests.

    Returns:
        One of the keys of :data:`EXIT_STATUS`.
    """
    started = clock()
    while True:
        text = log.read_text(errors="replace") if log.exists() else ""
        state = classify_log(text, markers)
        if state != "running":
            return state
        if pid is not None and not pid_alive(pid):
            sleep(grace_seconds)
            text = log.read_text(errors="replace") if log.exists() else ""
            state = classify_log(text, markers)
            return state if state != "running" else "stopped"
        age = log_age_seconds(log, clock())
        if age is None:
            age = clock() - started
        if age > stale_seconds:
            return "stale"
        sleep(poll_seconds)


def _parse_markers(specs: list[str]) -> dict[str, list[str]]:
    """Turn ``STATE=REGEX`` options into a marker table over the defaults."""
    table = {k: list(v) for k, v in DEFAULT_MARKERS.items()}
    for spec in specs:
        state, _, pattern = spec.partition("=")
        if state not in ("success", "partial", "crashed") or not pattern:
            raise SystemExit(f"--marker expects success|partial|crashed=REGEX, "
                             f"got {spec!r}")
        table[state].append(pattern)
    return table


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", required=True, type=Path, help="job log file")
    ap.add_argument("--pid", type=int, default=None, help="job process id")
    ap.add_argument("--pidfile", type=Path, default=None,
                    help="file holding the job process id")
    ap.add_argument("--stale-seconds", type=float, default=3600.0,
                    help="log silence that counts as a hang (default 3600)")
    ap.add_argument("--poll", type=float, default=60.0,
                    help="seconds between checks (default 60)")
    ap.add_argument("--marker", action="append", default=[],
                    metavar="STATE=REGEX",
                    help="extra terminal marker; repeatable")
    args = ap.parse_args(argv)

    pid = args.pid
    if args.pidfile is not None:
        pid = int(args.pidfile.read_text().strip())
    state = wait_for_terminal(args.log, pid=pid,
                              stale_seconds=args.stale_seconds,
                              poll_seconds=args.poll,
                              markers=_parse_markers(args.marker))
    print(f"STATE={state} log={args.log}"
          + (f" pid={pid}" if pid is not None else ""))
    return EXIT_STATUS[state]


if __name__ == "__main__":
    raise SystemExit(main())
