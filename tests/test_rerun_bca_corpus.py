"""Tests for the E82 corpus re-emission engine (contract Layer 1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.rerun_bca_corpus as rc

pytestmark = pytest.mark.tier1


def _doc(version: str, with_recipe: bool = True) -> dict:
    doc = {
        "_metadata": {
            "metadata_version": version,
            "bootstrap": {"n_iterations": 10000},
            "cli_args": {},
            "input_files": {},
        },
        "summary": {"label": "cell", "buffers": [
            {"buffer_metres": 20, "f1": 0.5, "precision": 0.5, "recall": 0.5,
             "f1_ci_lower": 0.4, "f1_ci_upper": 0.6},
            {"buffer_metres": 50, "f1": 0.6, "precision": 0.6, "recall": 0.6},
        ]},
    }
    if with_recipe:
        doc["_metadata"]["cli_args"] = {
            "detections": ["det.geojson"], "ground_truth": "gt.geojson",
            "bounds": "bounds.geojson", "seed": 42,
        }
    return doc


def _materialise(tmp_path: Path, rel: str, doc: dict) -> None:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc))


def test_selection_is_by_vintage_and_resume_skips_current(monkeypatch, tmp_path):
    """1.1/1.2 selected regardless of declared method; 1.3 skipped (resume)."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    for name in ("det.geojson", "gt.geojson", "bounds.geojson"):
        (tmp_path / name).write_text("{}")
    cases = {
        "a/evaluation.json": _doc("1.1"),
        "b/evaluation.json": _doc("1.2"),
        "c/evaluation.json": _doc("1.3"),          # already re-emitted
        "d/evaluation.json": _doc("1.0"),          # pre-BCa era
        "e/evaluation.json": _doc("1.2", with_recipe=False),  # no recipe
        "archive/f/evaluation.json": _doc("1.1"),  # archive excluded
    }
    # Method-silent 1.2 cell: no bootstrap.method anywhere — still selected.
    del cases["b/evaluation.json"]["_metadata"]["bootstrap"]
    cases["b/evaluation.json"]["_metadata"]["bootstrap"] = {"n_iterations": 10000}
    for rel, doc in cases.items():
        _materialise(tmp_path, rel, doc)
    worklist, census = rc.select_targets(sorted(cases))
    assert sorted(worklist) == ["a/evaluation.json", "b/evaluation.json"]
    assert census == {"selected": 2, "done_1.3": 1, "other_vintage": 1,
                      "unparseable": 0, "no_recipe": 1}


def test_build_command_uses_measurements_not_declarations(tmp_path):
    """Buffers from summary, --mcc from tile block, batch glob dropped."""
    doc = _doc("1.2")
    # Batch-vintage: cli_args names no detections, glob is the batch default.
    doc["_metadata"]["cli_args"] = {"glob": "*/detections_*.geojson",
                                   "buffers": [20], "seed": 7}
    doc["_metadata"]["input_files"] = {
        "detections": "pool_dir", "ground_truth": "gt.geojson",
        "bounds": "bounds.geojson",
    }
    doc["summary"]["tile_classification"] = {
        "mcc": {"point": 0.5}, "confusion": {"tp": 1, "tn": 1, "fp": 1, "fn": 1},
    }
    recipe = rc.recover_recipe(doc)
    cmd = rc.build_command(doc, recipe, tmp_path)
    joined = " ".join(cmd)
    assert "--detections-dir pool_dir" in joined
    assert "--glob" not in joined            # recovered row: canonical resolver
    assert "--buffers 20 50" in joined       # measured, not the recorded [20]
    assert "--mcc" in joined                 # measured from the tile block
    assert "--seed 7" in joined
    assert f"--bootstrap {rc.TARGET_B}" in joined


def test_gate_failure_leaves_file_untouched(monkeypatch, tmp_path):
    """A doctored point estimate must fail the gate and write nothing."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    for name in ("det.geojson", "gt.geojson", "bounds.geojson"):
        (tmp_path / name).write_text("{}")
    committed = _doc("1.2")
    _materialise(tmp_path, "cell/evaluation.json", committed)
    original_bytes = (tmp_path / "cell/evaluation.json").read_text()

    doctored = json.loads(json.dumps(committed))
    doctored["summary"]["buffers"][0]["f1"] = 0.51  # moved point

    def fake_run(cmd, **kwargs):
        out = Path(cmd[cmd.index("--output-dir") + 1])
        (out / "evaluation.json").write_text(json.dumps(doctored))

    monkeypatch.setattr(rc.subprocess, "run", fake_run)
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    assert row["reason"] == "point estimates moved"
    assert (tmp_path / "cell/evaluation.json").read_text() == original_bytes


def test_narrowing_interval_fails_the_width_tripwire(monkeypatch, tmp_path):
    """A pre-fix file whose interval NARROWS on replay is a failure."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    committed = _doc("1.2")
    _materialise(tmp_path, "cell/evaluation.json", committed)
    narrowed = json.loads(json.dumps(committed))
    narrowed["summary"]["buffers"][0]["f1_ci_lower"] = 0.49
    narrowed["summary"]["buffers"][0]["f1_ci_upper"] = 0.51  # width 0.2 -> 0.02

    def fake_run(cmd, **kwargs):
        out = Path(cmd[cmd.index("--output-dir") + 1])
        (out / "evaluation.json").write_text(json.dumps(narrowed))

    monkeypatch.setattr(rc.subprocess, "run", fake_run)
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    assert "width ratio" in row["reason"]


def test_passing_replay_replaces_siblings(monkeypatch, tmp_path):
    """Identical points with wider intervals pass and are written in place."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    committed = _doc("1.2")
    _materialise(tmp_path, "cell/evaluation.json", committed)
    widened = json.loads(json.dumps(committed))
    widened["summary"]["buffers"][0]["f1_ci_lower"] = 0.3
    widened["summary"]["buffers"][0]["f1_ci_upper"] = 0.7
    widened["_metadata"]["metadata_version"] = "1.3"

    def fake_run(cmd, **kwargs):
        out = Path(cmd[cmd.index("--output-dir") + 1])
        (out / "evaluation.json").write_text(json.dumps(widened))
        (out / "evaluation.csv").write_text("csv")

    monkeypatch.setattr(rc.subprocess, "run", fake_run)
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "ok"
    assert row["width_ratio"] == pytest.approx(2.0)
    on_disk = json.loads((tmp_path / "cell/evaluation.json").read_text())
    assert on_disk["_metadata"]["metadata_version"] == "1.3"
    assert (tmp_path / "cell/evaluation.csv").read_text() == "csv"
