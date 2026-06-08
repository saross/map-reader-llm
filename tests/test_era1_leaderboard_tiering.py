"""
Tests for ``scripts.era1_leaderboard_tiering`` — the generic Era-1
statistically-tiered leaderboard harness (Stage A + Stage B of
``planning/era1-leaderboard-plan-2026-06-08.md``).

The permutation, BH-FDR and greedy-clique tiering are imported VERBATIM from
``n1_baseline_leaderboard_tiering`` and are covered by its own tier-1 suite.
What is new here, and pinned below, is:

Tier 1 (synthetic, no I/O):
  1. ``read_tile_mcc`` — reads ``summary.tile_classification.mcc.point`` (the
     buffer-agnostic field), ``None`` when absent.
  2. ``load_board_refs`` — returns the named analysis's ``conditions_compared``;
     fails loud on an unknown analysis_id.
  3. ``resolve_condition`` — resolves a ``<run>::<label>`` ref; fails loud when
     the ref does not resolve.
  4. ``cell_per_tile`` — raises ``ValueError`` when the cli_args declare neither
     a detections set nor a detections_dir (the un-scoreable-cell guard).

Tier 2 (real GeoJSON data — the per-tile reproduction):
  5. ``cell_per_tile`` reproduces each eval's published F1@20 m for one cell of
     EACH of the three Era-1 shapes (single-pass replicate-mean, consensus
     single-set, phase3c dir-mode replicate-mean). This is the gate that the
     unified loader reproduces ``evaluate_detections.py`` exactly.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.era1_leaderboard_tiering import (  # noqa: E402
    cell_per_tile,
    load_board_refs,
    read_tile_mcc,
    resolve_condition,
)


# --------------------------------------------------------------------------- #
# 1. read_tile_mcc — the buffer-agnostic tile_classification field
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_read_tile_mcc_reads_tile_classification_point(tmp_path: Path) -> None:
    """MCC is read from summary.tile_classification.mcc.point."""
    eval_doc = {
        "summary": {
            "buffers": [{"buffer_metres": 20, "f1": 0.8, "mcc": None}],
            "tile_classification": {"mcc": {"point": 0.6204, "mean": 0.6204}},
        }
    }
    p = tmp_path / "evaluation.json"
    p.write_text(json.dumps(eval_doc))
    assert read_tile_mcc(p) == pytest.approx(0.6204)


@pytest.mark.tier1
def test_read_tile_mcc_absent_returns_none(tmp_path: Path) -> None:
    """A cell with no tile_classification block yields None, not a crash."""
    p = tmp_path / "evaluation.json"
    p.write_text(json.dumps({"summary": {"buffers": []}}))
    assert read_tile_mcc(p) is None


# --------------------------------------------------------------------------- #
# 2. load_board_refs — board membership from the named analysis
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_load_board_refs_returns_conditions_compared(tmp_path: Path) -> None:
    """The named analysis's conditions_compared list is returned verbatim."""
    doc = {
        "analyses": [
            {"analysis_id": "other", "conditions_compared": ["x::y"]},
            {"analysis_id": "era1-x", "conditions_compared": ["run-a::c1", "run-b::c2"]},
        ]
    }
    p = tmp_path / "run-analyses.json"
    p.write_text(json.dumps(doc))
    assert load_board_refs(p, "era1-x") == ["run-a::c1", "run-b::c2"]


@pytest.mark.tier1
def test_load_board_refs_unknown_id_fails_loud(tmp_path: Path) -> None:
    """An unknown analysis_id raises rather than silently returning nothing."""
    p = tmp_path / "run-analyses.json"
    p.write_text(json.dumps({"analyses": [{"analysis_id": "a", "conditions_compared": []}]}))
    with pytest.raises(StopIteration):
        load_board_refs(p, "does-not-exist")


# --------------------------------------------------------------------------- #
# 3. resolve_condition — ref -> decomposed condition
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_resolve_condition_finds_label(tmp_path: Path) -> None:
    """A <run>::<label> ref resolves to its condition dict."""
    doc = {
        "decomposition": {
            "run-a": {"conditions": [
                {"label": "c1", "detections": "d1"},
                {"label": "c2", "detections": "d2"},
            ]}
        }
    }
    p = tmp_path / "run-conditions.json"
    p.write_text(json.dumps(doc))
    cond = resolve_condition(p, "run-a::c2")
    assert cond["detections"] == "d2"


@pytest.mark.tier1
def test_resolve_condition_missing_label_fails_loud(tmp_path: Path) -> None:
    """A ref whose label is absent raises rather than dropping the cell."""
    doc = {"decomposition": {"run-a": {"conditions": [{"label": "c1"}]}}}
    p = tmp_path / "run-conditions.json"
    p.write_text(json.dumps(doc))
    with pytest.raises(StopIteration):
        resolve_condition(p, "run-a::nope")


# --------------------------------------------------------------------------- #
# 4. cell_per_tile — the un-scoreable-cell guard
# --------------------------------------------------------------------------- #


@pytest.mark.tier1
def test_cell_per_tile_no_detections_raises() -> None:
    """cli_args with neither detections nor detections_dir must fail loud."""
    with pytest.raises(ValueError, match="neither"):
        cell_per_tile({}, None, None, [])


# --------------------------------------------------------------------------- #
# 5. (tier 2) cell_per_tile reproduces each eval's published F1@20 m
# --------------------------------------------------------------------------- #

# One real condition per Era-1 cell shape, with its published F1@20 m. These
# pin that the unified loader reproduces evaluate_detections.py exactly:
#   single-pass (dir+glob, K-run replicate-mean), consensus single-set, and
#   phase3c dir-mode replicate-mean (5 replications).
_REPRO_CASES = [
    ("retest-phase2b", "text-t0.0", 0.6055),                       # single-pass avg
    ("retest-phase3a-high", "text-high-t1.0-n30-23of30", 0.7747),  # single-set
    ("retest-phase3c", "image-h9-a-diversity-3of5", 0.6640),       # dir replicate-mean
]


@pytest.mark.tier2
@pytest.mark.parametrize("run,label,published_f1", _REPRO_CASES)
def test_cell_per_tile_reproduces_published_f1(run: str, label: str,
                                               published_f1: float) -> None:
    """The recomputed micro-F1@20 m matches the eval's published F1 (~4 d.p.)."""
    import geopandas as gpd

    from scripts.era1_leaderboard_tiering import TARGET_CRS, micro_f1

    cond_doc = json.loads((PROJECT_ROOT / "results" / "run-conditions.json").read_text())
    cond = next(
        c for c in cond_doc["decomposition"][run]["conditions"] if c["label"] == label
    )
    cli = json.loads((PROJECT_ROOT / cond["eval_path"]).read_text())["_metadata"]["cli_args"]

    gt = gpd.read_file(PROJECT_ROOT / cli["ground_truth"]).to_crs(TARGET_CRS)
    bounds = gpd.read_file(PROJECT_ROOT / cli["bounds"]).to_crs(TARGET_CRS)
    tile_order = list(bounds["tile_name"].unique())

    tp, fp, fn, _n = cell_per_tile(cli, gt, bounds, tile_order)
    observed = micro_f1(tp.sum(), fp.sum(), fn.sum())
    assert observed == pytest.approx(published_f1, abs=5e-4)
