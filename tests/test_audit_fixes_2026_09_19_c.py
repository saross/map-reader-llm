"""Audit fixes of 2026-09-19, third batch: chunk ordering by number, a None
cost block, the cached-share print, and the caching flag's default.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.lib_batch_api import _chunk_sort_key, merge_chunk_metadata  # noqa: E402

pytestmark = pytest.mark.tier1


def test_chunks_sort_by_number_not_lexically():
    names = ["d_chunk10.meta.json", "d_chunk2.meta.json", "d_chunk0.meta.json"]
    assert [Path(n).name for n in sorted(names, key=_chunk_sort_key)] == [
        "d_chunk0.meta.json", "d_chunk2.meta.json", "d_chunk10.meta.json"]


def test_merge_base_is_chunk_zero_even_with_ten_plus_chunks(tmp_path):
    cfg = {"model": "m", "temperature": 0.0}
    metas, tiles = [], []
    for i in range(11):
        m = tmp_path / f"d_chunk{i}.meta.json"
        m.write_text(json.dumps({"configuration": cfg, "usage_stats": {"total_input_tokens": 1},
                                 "cost_estimate": None, "marker": i}))
        t = tmp_path / f"d_chunk{i}.tiles.json"
        t.write_text(json.dumps({"total_tiles": 2, "completed": [f"t{i}.png"]}))
        metas.append(m)
        tiles.append(t)
    merged = merge_chunk_metadata(metas, tiles, tmp_path / "m.json", tmp_path / "t.json")
    assert merged["marker"] == 0
    # Chunks that carry no cost block merge to null, not to a confident 0.0
    # (PI ruling D12, 2026-09-21), on the legacy additive path.
    assert merged["cost_estimate"]["total_cost_usd"] is None
    assert merged["cost_estimate"]["cost_basis"] == "summed-legacy"
    assert json.loads((tmp_path / "t.json").read_text())["total_tiles"] == 22


def test_cached_share_zero_prints_as_zero_not_unknown():
    src = (ROOT / "scripts" / "4_detect_mounds_batch.py").read_text()
    assert 'if share is not None else " (cache share unknown)"' in src
    assert 'if share else ""' not in src


def test_context_caching_is_off_by_default_at_the_cli():
    """PI ruling 2026-09-17: caching is opt-in; the request shape of every
    existing caller must not change. Pinned at the flag, not only at the
    function default (audit lens B)."""
    src = (ROOT / "scripts" / "4_detect_mounds_batch.py").read_text()
    i = src.index('"--use-cache"')
    assert 'action="store_true"' in src[i:i + 80]
