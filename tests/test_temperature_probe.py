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


def test_contrast_zero_for_identical_families() -> None:
    """Two families with the same per-candidate values contrast to exactly 0."""
    v = [0.0, 0.1, 0.5, 0.0] * 25
    stat = tp._bootstrap_contrast([v], [list(v)], reps=500, seed=1)
    assert stat["contrast"] == 0.0
    assert stat["ci_low"] == 0.0 and stat["ci_high"] == 0.0


def test_contrast_averages_within_family_first() -> None:
    """Family means are taken per candidate before subtracting."""
    stat = tp._bootstrap_contrast([[0.2] * 4, [0.4] * 4], [[0.1] * 4], reps=200, seed=1)
    assert stat["contrast"] == pytest.approx(0.2)


def test_followup_verdict_rule() -> None:
    """The fixed rule: both above 0 → effect; both straddle 0 → none; else inconclusive."""
    above = {"ci_low": 0.01, "ci_high": 0.03}
    straddle = {"ci_low": -0.01, "ci_high": 0.02}
    assert tp._followup_verdict(above, above) == "residual effect"
    assert tp._followup_verdict(straddle, straddle) == "no residual effect"
    assert tp._followup_verdict(above, straddle) == "inconclusive"
    assert tp._followup_verdict(straddle, above) == "inconclusive"


def _write_leg(root: Path, leg: str, probs: list[float]) -> None:
    """Write a minimal ``g37-<leg>/probabilities.json``."""
    d = root / f"g37-{leg}"
    d.mkdir(parents=True)
    results = {str(i): {"mound_probability": p} for i, p in enumerate(probs)}
    (d / "probabilities.json").write_text(json.dumps({"results": results}))


def test_followup_detects_a_temperature_effect(tmp_path: Path) -> None:
    """T max legs that move every candidate give a positive verdict."""
    base = [0.1, 0.2, 0.3, 0.9] * 25
    for leg in tp.FOLLOWUP_T0:
        _write_leg(tmp_path, leg, base)
    for leg in tp.FOLLOWUP_TMAX:
        _write_leg(tmp_path, leg, [p + 0.05 for p in base])
    tp.followup(tmp_path, tmp_path / "f.json", reps=200, seed=1)
    rec = json.loads((tmp_path / "f.json").read_text())
    assert rec["n_common"] == 100
    assert rec["pooled_mad_contrast"]["contrast"] == pytest.approx(0.05)
    assert rec["verdict"] == "residual effect"


def test_followup_null_when_legs_exchangeable(tmp_path: Path) -> None:
    """Five identical legs give a zero contrast and the null verdict."""
    base = [0.1, 0.2, 0.3, 0.9] * 25
    for leg in (*tp.FOLLOWUP_T0, *tp.FOLLOWUP_TMAX):
        _write_leg(tmp_path, leg, base)
    tp.followup(tmp_path, tmp_path / "f.json", reps=200, seed=1)
    rec = json.loads((tmp_path / "f.json").read_text())
    assert rec["verdict"] == "no residual effect"
