"""
Tests for ``scripts/modality_bridge_verifier_sd.py`` — Run C's verifier SD and floors.

The script's scoring is gated against the committed Run B cells when it runs
(replicate 1 must reproduce every committed set exactly); these tests pin the
pure functions it rests on: which directory each replicate is read from, the
SD with its chi-square interval, the pooled SD, the floor with the verifier
variance in quadrature, the break-even verifier SD, and the flip counts.
All synthetic; nothing is read from disk.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.modality_bridge_floors import ARMS, Z, contrast_floor  # noqa: E402
from scripts.modality_bridge_verifier_sd import (  # noqa: E402
    break_even_sd,
    chi2_sd_interval,
    flip_rates,
    floor_with_verifier,
    identical_share,
    pooled_sd,
    raw_dir,
    rep_dir,
    response_text_digests,
    sd_summary,
)

pytestmark = pytest.mark.tier1


def test_replicate_one_is_read_where_the_floors_read_it() -> None:
    for arm in ARMS.values():
        for _leg, base in arm.legs:
            assert rep_dir(base, 1) == base
            v = "g37" if "g37" in base else "g3"
            assert rep_dir(base, 2) == f"verify_{v}_rep2_repaired"
            assert rep_dir(base, 3) == f"verify_{v}_rep3_repaired"


def test_raw_dir_drops_the_repaired_suffix() -> None:
    for arm in ARMS.values():
        for _leg, base in arm.legs:
            v = "g37" if "g37" in base else "g3"
            assert raw_dir(base, 1) == f"verify_{v}"
            assert raw_dir(base, 3) == f"verify_{v}_rep3"


def test_response_texts_compare_by_digest(tmp_path: Path) -> None:
    rows = [{"key": "candidate_00000", "response": {"candidates": [
                {"content": {"parts": [{"text": "same"}]}}]}},
            {"key": "candidate_00001", "response": {"candidates": [
                {"content": {"parts": [{"text": "a"}]}}]}},
            {"key": "candidate_00002", "error": {"code": 500}}]
    other = [dict(rows[0]), {"key": "candidate_00001", "response": {"candidates": [
                {"content": {"parts": [{"text": "b"}]}}]}}, dict(rows[2])]
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    a.write_text("".join(json.dumps(r) + "\n" for r in rows))
    b.write_text("".join(json.dumps(r) + "\n" for r in other))
    da, db = response_text_digests(a), response_text_digests(b)
    assert set(da) == {"candidate_00000", "candidate_00001", "candidate_00002"}
    assert identical_share(da, db) == pytest.approx(2 / 3)  # a row with no text hashes ""
    assert identical_share(da, da) == 1.0


def test_chi2_interval_for_two_degrees_of_freedom() -> None:
    lo, hi = chi2_sd_interval(0.004, 2)
    # chi2(0.975, 2) = 7.3778, chi2(0.025, 2) = 0.050636
    assert lo == pytest.approx(0.004 * math.sqrt(2 / 7.377759), rel=1e-5)
    assert hi == pytest.approx(0.004 * math.sqrt(2 / 0.0506356), rel=1e-5)
    assert lo < 0.004 < hi


def test_chi2_interval_narrows_with_more_degrees_of_freedom() -> None:
    w2 = np.subtract(*chi2_sd_interval(1.0, 2)[::-1])
    w14 = np.subtract(*chi2_sd_interval(1.0, 14)[::-1])
    assert w14 < w2


def test_sd_summary_uses_n_minus_one() -> None:
    s = sd_summary([0.88, 0.89, 0.90])
    assert s["sd"] == pytest.approx(0.01)
    assert s["df"] == 2 and s["n"] == 3
    assert s["mean"] == pytest.approx(0.89)
    assert s["range"] == pytest.approx(0.02)
    zero = sd_summary([0.9, 0.9, 0.9])
    assert zero["sd"] == 0.0 and zero["sd_ci95"] == [0.0, 0.0]


def test_pooled_sd_weights_by_degrees_of_freedom() -> None:
    p = pooled_sd([0.002, 0.004, 0.006], [2, 2, 2])
    assert p["sd"] == pytest.approx(math.sqrt((0.002 ** 2 + 0.004 ** 2 + 0.006 ** 2) / 3))
    assert p["df"] == 6
    q = pooled_sd([0.002, 0.004], [2, 6])
    assert q["sd"] == pytest.approx(math.sqrt((2 * 0.002 ** 2 + 6 * 0.004 ** 2) / 8))


def test_floor_with_verifier_adds_both_variances_in_quadrature() -> None:
    assert floor_with_verifier([0.003, 0.004], [0.0, 0.0]) == pytest.approx(
        contrast_floor([0.003, 0.004], 1, band=0.0))
    assert floor_with_verifier([0.003, 0.0], [0.0, 0.004]) == pytest.approx(Z * 0.005)
    with pytest.raises(ValueError):
        floor_with_verifier([0.003, 0.004], [0.001])


def test_break_even_sd_round_trips_through_the_floor() -> None:
    p = [0.0089, 0.0071, 0.0056, 0.0164]  # the primary gap change's proposer SDs
    s = break_even_sd(-0.0529, p)
    assert floor_with_verifier(p, [s] * 4) == pytest.approx(0.0529)
    assert 0.0085 < s < 0.0089  # the brief's "about 0.009"
    assert break_even_sd(0.001, p) == 0.0


def test_flip_rates_count_pairs_and_splits() -> None:
    a = np.array([True, True, False, False, True])
    b = np.array([True, False, False, False, True])
    c = np.array([True, True, False, True, True])
    r = flip_rates([a, b, c])
    assert r["n"] == 5
    assert r["pairwise"]["1-2"] == {"count": 1, "rate": 0.2}
    assert r["pairwise"]["1-3"] == {"count": 1, "rate": 0.2}
    assert r["pairwise"]["2-3"] == {"count": 2, "rate": 0.4}
    assert r["split"] == {"count": 2, "rate": 0.4}
    assert r["pairwise_mean_rate"] == pytest.approx(0.8 / 3)
    same = flip_rates([a, a, a])
    assert same["split"]["count"] == 0 and same["pairwise_mean_rate"] == 0.0


def test_load_floors_reads_the_three_files_from_the_directory_given(tmp_path: Path) -> None:
    from scripts.modality_bridge_verifier_sd import load_floors

    for i, name in enumerate(("floors.json", "gates.json", "gap_change.json")):
        (tmp_path / name).write_text(json.dumps({"which": i}))
    assert load_floors(tmp_path) == ({"which": 0}, {"which": 1}, {"which": 2})


def test_main_reads_the_floors_from_floors_dir_and_defaults_to_the_committed(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``--floors-dir`` is what ``main`` reads, before anything heavy is loaded."""
    from scripts import modality_bridge_floors as fl
    from scripts import modality_bridge_verifier_sd as vsd

    seen: list[Path] = []

    class Stop(Exception):
        pass

    def fake_load(floors_dir: Path):
        seen.append(floors_dir)
        raise Stop

    monkeypatch.setattr(vsd, "load_floors", fake_load)
    with pytest.raises(Stop):
        vsd.main(["--floors-dir", str(tmp_path), "--gate-only"])
    with pytest.raises(Stop):
        vsd.main(["--gate-only"])
    assert seen == [tmp_path, fl.RESULTS / "floors"]
