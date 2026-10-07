#!/usr/bin/env python3
"""
Tier-1 tests for ``scripts/temperature_probe_2026_10_07.py``.

The probe's verdict rests on two numbers: exact agreement between paired
probability vectors, and the bootstrap of the drop from T0/T0 agreement to
T0/Tmax agreement. Both are checked on synthetic vectors whose answers are
known by construction. ``prepare`` is checked for a seeded, reproducible,
non-overwriting subset that records its own provenance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import temperature_probe_2026_10_07 as tp  # noqa: E402

pytestmark = pytest.mark.tier1


def test_agreement_identical_vectors() -> None:
    """Identical vectors agree exactly, with no flips and zero mean difference."""
    a = [0.1, 0.9, 0.5, 0.9]
    stats = tp._agreement(a, list(a))
    assert stats["exact"] == 1.0
    assert stats["mean_abs_diff"] == 0.0
    assert all(stats[f"flips_at_{t:.2f}"] == 0.0 for t in tp.FLIP_THRESHOLDS)


def test_agreement_counts_flips_and_large_moves() -> None:
    """A 0.1 → 0.9 change flips at 0.5 and counts as a move above 0.5."""
    stats = tp._agreement([0.1, 0.9], [0.9, 0.9])
    assert stats["exact"] == 0.5
    assert stats["flips_at_0.50"] == 0.5
    assert stats["share_abs_diff_gt_0.5"] == 0.5
    assert stats["mean_abs_diff"] == pytest.approx(0.4)


def test_bootstrap_drop_zero_when_temperature_ignored() -> None:
    """If Tmax reproduces T0 as well as T0 reproduces itself, the drop is 0."""
    t0 = [0.1, 0.2, 0.3, 0.9] * 25
    drop = tp._bootstrap_drop(t0, list(t0), list(t0), reps=500, seed=1)
    assert drop["drop"] == 0.0
    assert drop["ci_low"] == 0.0 and drop["ci_high"] == 0.0


def test_bootstrap_drop_positive_when_temperature_honoured() -> None:
    """A Tmax leg that disagrees everywhere gives a drop of 1 with a tight CI."""
    t0 = [0.1, 0.2, 0.3, 0.9] * 25
    tmax = [p + 0.05 for p in t0]
    drop = tp._bootstrap_drop(t0, list(t0), tmax, reps=500, seed=1)
    assert drop["drop"] == pytest.approx(1.0)
    assert drop["ci_low"] == pytest.approx(1.0)


def _write_source(tmp_path: Path, n: int) -> Path:
    """Build a fake crops directory with ``n`` candidates."""
    src = tmp_path / "src"
    (src / "crops").mkdir(parents=True)
    cands = []
    for i in range(n):
        name = f"crops/candidate_{i:05d}.png"
        (src / name).write_bytes(b"png" + bytes([i % 256]))
        cands.append({"candidate_id": i, "crop_file": name})
    (src / "candidate_manifest.json").write_text(json.dumps({
        "version": "2.0", "source_geojson": "union.geojson",
        "total_detections": n, "successful_extractions": n, "candidates": cands,
    }))
    return src


def test_prepare_is_seeded_and_records_provenance(tmp_path: Path) -> None:
    """Same seed, same subset; the manifest names its source and its draw."""
    src = _write_source(tmp_path, 40)
    tp.prepare(src, tmp_path / "a", n=10, seed=42)
    tp.prepare(src, tmp_path / "b", n=10, seed=42)
    ma = json.loads((tmp_path / "a" / "candidate_manifest.json").read_text())
    mb = json.loads((tmp_path / "b" / "candidate_manifest.json").read_text())
    assert ma["probe_subset"]["candidate_ids"] == mb["probe_subset"]["candidate_ids"]
    assert len(ma["candidates"]) == 10 and ma["total_detections"] == 10
    assert ma["probe_subset"]["n_source"] == 40
    for cand in ma["candidates"]:
        assert (tmp_path / "a" / cand["crop_file"]).exists()


def test_prepare_refuses_to_overwrite(tmp_path: Path) -> None:
    """An existing probe directory is never overwritten."""
    src = _write_source(tmp_path, 5)
    tp.prepare(src, tmp_path / "out", n=3, seed=1)
    with pytest.raises(FileExistsError):
        tp.prepare(src, tmp_path / "out", n=3, seed=1)
