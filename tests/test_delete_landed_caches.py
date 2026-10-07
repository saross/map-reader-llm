#!/usr/bin/env python3
"""
Tier-1 tests for ``scripts/delete_landed_caches.py``.

The deleter must never remove a cache a live or in-flight pass may read,
must leave young caches alone (a lodge creates its cache before it writes
its request file), and must free the caches of landed passes and of lodges
that exited without submitting. All tests are offline.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import delete_landed_caches as dlc  # noqa: E402

pytestmark = pytest.mark.tier1

T0 = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)
GRACE = timedelta(minutes=90)


def _cache(name: str, age_h: float, display: str = dlc.DETECTOR_CACHE_DISPLAY_NAME) -> dict:
    """A cache listing entry created ``age_h`` hours before T0 + 6 h."""
    return {"name": name, "display_name": display,
            "create_time": T0 + timedelta(hours=6) - timedelta(hours=age_h)}


def _state(cache: str | None, protects: bool) -> dlc.PassState:
    return dlc.PassState("p", cache, protects, "test")


def test_only_caches_finished_passes_name_are_deleted() -> None:
    caches = [_cache("c/landed", 3), _cache("c/live", 3), _cache("c/orphan", 3)]
    states = [_state("c/landed", False), _state("c/live", True)]
    got = dlc.select_deletable(caches, states, T0, T0 + timedelta(hours=6), GRACE)
    # c/orphan is named by no pass: it may be another job's, so it stays.
    assert got == ["c/landed"]


def test_a_relodged_passes_old_cache_is_kept() -> None:
    """An orphaned job may still read the cache its re-lodge no longer names."""
    caches = [_cache("c/old", 3), _cache("c/new", 3), _cache("c/refused", 3),
              _cache("c/foreign", 3)]
    states = [_state("c/new", True), _state("c/refused", False)]
    got = dlc.select_deletable(caches, states, T0, T0 + timedelta(hours=6), GRACE)
    assert got == ["c/refused"]


def test_young_foreign_and_old_caches_are_never_touched() -> None:
    caches = [_cache("c/young", 1), _cache("c/foreign", 3, display="other"),
              _cache("c/before-since", 7)]
    got = dlc.select_deletable(caches, [], T0, T0 + timedelta(hours=6), GRACE)
    assert got == []


def test_a_live_pass_without_a_readable_cache_blocks_everything() -> None:
    caches = [_cache("c/a", 3)]
    got = dlc.select_deletable(caches, [_state(None, True)], T0,
                               T0 + timedelta(hours=6), GRACE)
    assert got == []


def test_submission_is_read_after_the_latest_lodge_only() -> None:
    log = ("=== 2026-10-07T12:00:00+00:00 LODGE g3-image-run1: x\n"
           "  Submitted batch job: batches/1\n"
           "=== 2026-10-07T14:00:00+00:00 LODGE g3-image-run1: x\n"
           "refused\n")
    assert not dlc.submitted_since_latest_lodge(log, "g3-image-run1")
    assert dlc.submitted_since_latest_lodge(log + "  Submitted batch job: b/2\n",
                                            "g3-image-run1")


def _pass(out: Path, arm: str, run: int, cache: str, *, landed: bool, log: str,
          rd: int | None = None) -> None:
    root = out / arm / (f"recovery_rd{rd}" if rd else "") / "detect_brief-text-image"
    d = root / f"run_{run}"
    (d / "batch_working").mkdir(parents=True)
    line = {"key": "t.png", "request": {"cached_content": cache, "contents": []}}
    (d / "batch_working" / "req.jsonl").write_text(json.dumps(line) + "\n")
    if landed:
        (d / f"detections_detect_brief-text-image_run{run:02d}.geojson").write_text("{}")
    name = f"{arm}-run{run}" + (f"_rd{rd}" if rd else "")
    (out / "logs").mkdir(exist_ok=True)
    (out / "logs" / f"{name}.log").write_text(log.replace("NAME", name))


def test_pass_states_reads_the_launcher_layout(tmp_path: Path) -> None:
    lodged = "=== 2026-10-07T12:00:00+00:00 LODGE NAME: x\n  Submitted batch job: b/1\n"
    _pass(tmp_path, "g3-image", 1, "c/landed", landed=True, log=lodged)
    _pass(tmp_path, "g3-image-temp1", 2, "c/flight", landed=False, log=lodged)
    _pass(tmp_path, "g37-image-cache", 3, "c/refused", landed=False,
          log="=== 2026-10-07T12:00:00+00:00 LODGE NAME: x\nrefused\n")
    _pass(tmp_path, "g3-image", 4, "c/frag", landed=False, log=lodged, rd=1)
    got = {s.name: (s.cache, s.protects) for s in dlc.pass_states(tmp_path)}
    assert got == {
        "g3-image-run1": ("c/landed", False),
        "g3-image-temp1-run2": ("c/flight", True),
        "g37-image-cache-run3": ("c/refused", False),
        "g3-image-run4_rd1": ("c/frag", True),
    }
