"""A failed chunk is counted and never merged over (audit lens A, S155).

Before 2026-09-19 a chunk that failed before writing its sidecar was skipped
past the tile count, so a run that lost 4,000 tiles could report
items_failed 0 and exit 0; and the chunk merge ran regardless, writing a
merged sidecar whose total_tiles summed only the chunks that existed — a
six-of-seven pass that read as complete.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.tier1


def _load():
    spec = importlib.util.spec_from_file_location(
        "detect_mounds_batch", ROOT / "scripts" / "4_detect_mounds_batch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sidecar(run_dir: Path, suffix: str, completed: int, failed: int) -> None:
    (run_dir / f"detections_x_run01{suffix}.tiles.json").write_text(json.dumps({
        "total_tiles": completed + failed,
        "completed": [f"c{i}.png" for i in range(completed)],
        "failed": [f"f{i}.png" for i in range(failed)],
    }))


def test_a_successful_chunk_is_counted_from_its_sidecar(tmp_path):
    mod = _load()
    _sidecar(tmp_path, "_chunk0", 3990, 10)
    assert mod.tally_chunk(tmp_path, "_chunk0", 4000, True) == (3990, 10)


def test_a_partially_failed_chunk_is_counted_from_its_sidecar(tmp_path):
    """partial_failure leaves a sidecar; its own failed list is the truth."""
    mod = _load()
    _sidecar(tmp_path, "_chunk2", 3000, 1000)
    assert mod.tally_chunk(tmp_path, "_chunk2", 4000, False) == (3000, 1000)


def test_a_chunk_that_left_no_sidecar_counts_every_tile_as_failed(tmp_path):
    """The S155 case: a submit/poll/retrieve error writes nothing."""
    mod = _load()
    _sidecar(tmp_path, "_chunk0", 4000, 0)          # a neighbour, not ours
    assert mod.tally_chunk(tmp_path, "_chunk3", 4000, False) == (0, 4000)


def test_a_successful_chunk_with_no_sidecar_is_not_invented(tmp_path):
    """Success without a sidecar is not a failure to be counted; it is a
    contract breach to be seen as zero, not as chunk_limit."""
    mod = _load()
    assert mod.tally_chunk(tmp_path, "_chunk3", 4000, True) == (0, 0)


def test_an_unchunked_run_ignores_stale_chunk_sidecars(tmp_path):
    mod = _load()
    _sidecar(tmp_path, "", 500, 1)
    _sidecar(tmp_path, "_chunk0", 4000, 0)
    assert mod.tally_chunk(tmp_path, "", 501, True) == (500, 1)


def test_the_merge_is_withheld_and_the_exit_is_partial_when_a_chunk_failed():
    """Wiring: the lifecycle must (a) not merge when chunk_failed and
    (b) report items_failed >= 1 so main() exits 2 — read from the source,
    since the lifecycle itself needs a live API client."""
    src = (ROOT / "scripts" / "4_detect_mounds_batch.py").read_text()
    assert "if needs_chunking and not args.dry_run and not chunk_failed:" in src
    assert '"items_failed": max(total_failed, 1)' in src
    assert "tally_chunk(run_dir, suffix, chunk_limit, success)" in src
