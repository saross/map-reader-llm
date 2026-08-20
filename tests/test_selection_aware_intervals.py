"""Tests for scripts/selection_aware_intervals.py — the MCB/selection instrument.

Added 2026-08-20 as part of the Session 137 audit remediation. The instrument
sits under all fourteen register tie sets (erratum E83) and previously had no
tests at all. Three groups:

* ``run()`` invariants on synthetic counts — properties the docstrings promise
  (the empirical best is always admissible; Hsu is a membership subset of the
  two-sided band; theta is Hsu's quantity, ties and NaNs included; undefined
  candidates are dropped, never read as 0.0).
* Buffer threading on the ``--evals`` path (audit finding F17a: ``--buffer``
  was silently ignored there while being stamped into the filename).
* Override recording on the ``--board`` path (audit finding F9: the four
  55-map artefacts were not reproducible from their own metadata because the
  mandatory ``--ground-truth`` override was never recorded).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Point, box

import scripts.selection_aware_intervals as sai

pytestmark = pytest.mark.tier1


# ── run() invariants ──────────────────────────────────────────────────


def _synthetic_counts() -> np.ndarray:
    """Three candidates over 30 tiles with a clear best (candidate 0)."""
    rng = np.random.default_rng(7)
    counts = np.zeros((3, 30, 3))
    # Candidate 0: strong (many TP, few FP/FN); 1: middling; 2: weak.
    counts[0, :, 0] = rng.integers(1, 4, 30)
    counts[0, :, 1] = rng.integers(0, 2, 30)
    counts[0, :, 2] = rng.integers(0, 2, 30)
    counts[1] = counts[0] * 0.7
    counts[1, :, 2] += 1
    counts[2] = counts[0] * 0.4
    counts[2, :, 1] += 2
    counts[2, :, 2] += 2
    return counts


def test_best_is_always_hsu_admissible():
    """The empirical best can never be ruled out as best — by construction.

    theta_best = best - second >= 0 and w_upper >= 0, so the decision rule
    theta + w_upper > 0 must retain the best. An empty admissible set is the
    signature of a NaN critical value, which must never happen on defined
    statistics.
    """
    res = sai.run(_synthetic_counts(), b=200, m_frac=1.0, seed=0)
    assert res["selected_index"] in res["hsu_not_ruled_out"]
    assert res["selected_index"] in res["mcb_not_ruled_out"]
    assert len(res["hsu_not_ruled_out"]) >= 1


def test_hsu_is_membership_subset_of_band():
    """Hsu's one-sided constrained set never admits outside the two-sided band.

    The band spends confidence on the lower tail the admissibility question
    never uses, so it is weakly wider. Verified on all 22 committed candidate
    sets during the Session 137 audit; this pins the property.
    """
    res = sai.run(_synthetic_counts(), b=200, m_frac=1.0, seed=0)
    assert set(res["hsu_not_ruled_out"]) <= set(res["mcb_not_ruled_out"])


def test_theta_is_hsus_quantity():
    """theta_i = stat_i - max_{j != i} stat_j, including the best's own row."""
    counts = _synthetic_counts()
    res = sai.run(counts, b=50, m_frac=1.0, seed=0)
    f1 = sai.f1_from_counts(counts)
    order = np.argsort(f1)[::-1]
    best, second = f1[order[0]], f1[order[1]]
    expect = f1 - best
    expect[order[0]] = best - second
    assert np.allclose(res["mcb_theta"], expect)


def test_undefined_mcc_candidate_dropped_not_zeroed():
    """A candidate with an undefined statistic is dropped and counted (E81)."""
    counts = _synthetic_counts()
    # Candidates 0 and 1: detections on the first 20 tiles only, so both
    # margins of their tile confusion matrices are populated (defined MCC).
    counts[0, 20:, :2] = 0
    counts[1, 20:, :2] = 0
    counts[2, :, 0] = 0  # no detections at all -> TP+FP = 0 -> MCC undefined
    counts[2, :, 1] = 0
    has_mounds = np.array([True] * 20 + [False] * 10)
    res = sai.run(counts, b=50, m_frac=1.0, seed=0, has_mounds=has_mounds,
                  metric="mcc")
    assert res["n_candidates_dropped_undefined"] == 1
    assert res["n_candidates"] == 2
    assert 2 not in res["kept_indices"]


# ── buffer threading on the --evals path (audit F17a) ─────────────────


def _write_scope_fixtures(root: Path) -> tuple[str, str]:
    """Write a tiny bounds + reference pair under a fake PROJECT_ROOT."""
    bounds = gpd.GeoDataFrame(
        {"tile_name": ["t1", "t2"]},
        geometry=[box(0, 0, 10, 10), box(10, 0, 20, 10)],
        crs="EPSG:32635",
    )
    ref = gpd.GeoDataFrame(
        {"id": [1]}, geometry=[Point(5, 5)], crs="EPSG:32635",
    )
    (root / "inputs").mkdir(parents=True, exist_ok=True)
    bounds_rel, gt_rel = "inputs/bounds.geojson", "inputs/ref.geojson"
    bounds.to_file(root / bounds_rel, driver="GeoJSON")
    ref.to_file(root / gt_rel, driver="GeoJSON")
    return bounds_rel, gt_rel


def _write_eval(root: Path, name: str, bounds_rel: str, gt_rel: str) -> None:
    d = root / "evals" / name
    d.mkdir(parents=True, exist_ok=True)
    doc = {
        "_metadata": {"cli_args": {"bounds": bounds_rel,
                                   "ground_truth": gt_rel}},
        "summary": {"buffers": [
            {"buffer_metres": 20, "f1": 0.2},
            {"buffer_metres": 50, "f1": 0.5},
        ]},
    }
    (d / "evaluation.json").write_text(json.dumps(doc))


def test_evals_path_threads_buffer(monkeypatch, tmp_path):
    """--evals scores AND reads eval_f1 at the requested buffer, not 20 m."""
    bounds_rel, gt_rel = _write_scope_fixtures(tmp_path)
    _write_eval(tmp_path, "cellA", bounds_rel, gt_rel)
    _write_eval(tmp_path, "cellB", bounds_rel, gt_rel)
    monkeypatch.setattr(sai, "PROJECT_ROOT", tmp_path)

    seen_buffers: list[int] = []

    def fake_cell_per_tile(cli_args, gdf_ref, gdf_bounds, tile_order,
                           buffer_metres=20):
        seen_buffers.append(buffer_metres)
        n = len(tile_order)
        return (np.ones(n), np.zeros(n), np.zeros(n), 1)

    import scripts.era1_leaderboard_tiering as tiering
    monkeypatch.setattr(tiering, "cell_per_tile", fake_cell_per_tile)

    specs, counts, has_mounds, scope = sai.build_evals_tile_counts(
        str(tmp_path / "evals" / "*" / "evaluation.json"), buffer_metres=50)

    assert seen_buffers == [50, 50]
    assert [s["eval_f1"] for s in specs] == [0.5, 0.5]
    assert scope == {"bounds": bounds_rel, "ground_truth": gt_rel}
    assert counts.shape == (2, 2, 3)


# ── override recording on the --board path (audit F9) ─────────────────


def _run_main(monkeypatch, tmp_path, extra_args: list[str]) -> dict:
    """Drive main() with a stubbed board loader; return the written JSON."""
    counts = _synthetic_counts()
    has_mounds = np.ones(30, dtype=bool)
    specs = [{"ref": f"c{i}", "label": f"c{i}", "eval_f1": None}
             for i in range(3)]

    def fake_board(analysis_id, gt_override, bounds_override, buffer_metres):
        return specs, counts, has_mounds

    monkeypatch.setattr(sai, "build_board_tile_counts", fake_board)
    argv = ["selection_aware_intervals.py", "--board", "fake-board",
            "--bootstrap", "50", "--out", str(tmp_path), *extra_args]
    monkeypatch.setattr(sys, "argv", argv)
    assert sai.main() == 0
    out_files = list(tmp_path.glob("fake-board*.json"))
    assert len(out_files) == 1
    return json.loads(out_files[0].read_text())


def test_board_overrides_recorded_when_given(monkeypatch, tmp_path):
    res = _run_main(monkeypatch, tmp_path, [
        "--ground-truth", "inputs/vectors/references/some-gt.geojson",
        "--bounds", "inputs/vectors/bounds/some-bounds.geojson",
        "--buffer", "50",
    ])
    assert res["ground_truth_override"] == (
        "inputs/vectors/references/some-gt.geojson")
    assert res["bounds_override"] == (
        "inputs/vectors/bounds/some-bounds.geojson")
    assert res["buffer_metres"] == 50


def test_board_overrides_omitted_when_absent(monkeypatch, tmp_path):
    res = _run_main(monkeypatch, tmp_path, [])
    assert "ground_truth_override" not in res
    assert "bounds_override" not in res
