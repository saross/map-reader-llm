"""Tests for the terminal-state watcher (beacon S155, defect D1).

The contract under test: the watcher keys on the job having STOPPED, then
reads HOW it stopped. A partial failure, which prints no success line, must
be seen as terminal — that is exactly what the success-string wait of
2026-09-17 could not do.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.wait_for_run import (  # noqa: E402
    EXIT_STATUS,
    classify_log,
    main,
    wait_for_terminal,
)

BATCH_OK = "Merged 7 chunks\nBatch complete. Estimated cost: $81.93\nTiles processed: 24561\n"
BATCH_PARTIAL = "Merged 6 chunks\nBatch partially failed (some chunks errored)\n"
REALTIME_PARTIAL = "Finished. Saved to x\nTiles processed: 24000\nTiles failed: 561\n"
REALTIME_OK = "Finished. Saved to x\nTiles processed: 24561\nTiles failed: 0\n"
CRASH = "Chunk 3/7\nTraceback (most recent call last):\n  File x\nKeyError: 'y'\n"


@pytest.mark.tier1
@pytest.mark.parametrize("text,state", [
    (BATCH_OK, "success"),
    (REALTIME_OK, "success"),
    (BATCH_PARTIAL, "partial"),
    (REALTIME_PARTIAL, "partial"),
    (CRASH, "crashed"),
    ("Chunking: 24561 tiles into 7 batch jobs\n", "running"),
    ("", "running"),
])
def test_classify_log(text, state):
    assert classify_log(text) == state


@pytest.mark.tier1
def test_partial_failure_is_terminal_without_any_success_line():
    """The S154 case: run 5 failed one chunk, printed no 'Tiles processed:',
    and a success-string watcher waited on it all night."""
    assert "Tiles processed" not in BATCH_PARTIAL
    assert classify_log(BATCH_PARTIAL) != "running"


@pytest.mark.tier1
def test_last_marker_by_position_decides():
    """A retried chunk's traceback followed by completion is a success; a
    completion followed by a traceback on the way out is a crash."""
    assert classify_log(CRASH + BATCH_OK) == "success"
    assert classify_log(BATCH_OK + CRASH) == "crashed"


@pytest.mark.tier1
def test_extra_markers_extend_the_defaults():
    markers = {"success": ["^ALL ARMS DONE"], "partial": [], "crashed": []}
    assert classify_log("...\nALL ARMS DONE 2026-09-18\n", markers) == "success"
    assert classify_log(BATCH_OK, markers) == "running"


@pytest.mark.tier1
def test_marker_in_log_returns_at_once(tmp_path):
    log = tmp_path / "run.log"
    log.write_text(BATCH_PARTIAL)
    slept = []
    state = wait_for_terminal(log, sleep=slept.append)
    assert state == "partial"
    assert slept == []


@pytest.mark.tier1
def test_stale_log_is_terminal(tmp_path):
    """A hang looks exactly like a death from outside; both end the wait."""
    log = tmp_path / "run.log"
    log.write_text("Chunk 2/7 polling...\n")
    old = time.time() - 7200
    os.utime(log, (old, old))
    state = wait_for_terminal(log, stale_seconds=3600, sleep=lambda s: None)
    assert state == "stale"


@pytest.mark.tier1
def test_dead_process_with_silent_log_is_stopped(tmp_path):
    """The process is gone and the log says nothing terminal: that is a
    'stopped', reported at once, not a wait for the staleness window."""
    log = tmp_path / "run.log"
    log.write_text("Chunk 2/7 polling...\n")           # fresh mtime
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    dead_pid = proc.pid        # reaped: no process with this id exists now
    slept = []
    state = wait_for_terminal(log, pid=dead_pid, stale_seconds=10**9,
                              sleep=slept.append)
    assert state == "stopped"
    assert slept == [5.0]        # the flush grace only, no poll sleep


@pytest.mark.tier1
def test_live_process_keeps_waiting_until_marker(tmp_path):
    log = tmp_path / "run.log"
    log.write_text("Chunk 1/7\n")
    calls = []

    def fake_sleep(seconds):
        calls.append(seconds)
        if len(calls) == 2:
            log.write_text("Chunk 1/7\n" + BATCH_OK)

    state = wait_for_terminal(log, pid=os.getpid(), stale_seconds=10**9,
                              poll_seconds=7, sleep=fake_sleep)
    assert state == "success"
    assert calls == [7, 7]


@pytest.mark.tier1
def test_exit_status_maps_every_state():
    assert EXIT_STATUS == {"success": 0, "partial": 2, "crashed": 3,
                           "stale": 4, "stopped": 5}


@pytest.mark.tier1
def test_cli_exit_status_is_the_state(tmp_path, capsys):
    log = tmp_path / "run.log"
    log.write_text(REALTIME_PARTIAL)
    rc = main(["--log", str(log), "--poll", "0"])
    assert rc == 2
    assert "STATE=partial" in capsys.readouterr().out


@pytest.mark.tier1
def test_cli_rejects_a_malformed_marker(tmp_path):
    log = tmp_path / "run.log"
    log.write_text(BATCH_OK)
    with pytest.raises(SystemExit):
        main(["--log", str(log), "--marker", "done"])
