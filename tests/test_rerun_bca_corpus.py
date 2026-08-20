"""Tests for the E82 corpus re-emission engine (contract Layer 1).

Revised 2026-08-20 after the fresh-context pre-launch audit: the
fault-injection probes that found blockers B1/B2 and majors M1–M4 are encoded
here as permanent tests, so the fixed holes cannot silently reopen.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import scripts.rerun_bca_corpus as rc

pytestmark = pytest.mark.tier1


def _doc(version: str, with_recipe: bool = True) -> dict:
    doc = {
        "_metadata": {
            "metadata_version": version,
            "generated_at_utc": "2026-05-01T00:00:00+00:00",
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


def _fixture_inputs(tmp_path: Path) -> None:
    for name in ("det.geojson", "gt.geojson", "bounds.geojson"):
        (tmp_path / name).write_text("{}")


def _no_frozen(monkeypatch) -> None:
    """Disable the vintage fallback for tests targeting attempt 1."""
    monkeypatch.setattr(rc, "vintage_assignments", lambda *a, **k: [])


def _fake_replay(monkeypatch, produce):
    """Monkeypatch the subprocess replay; ``produce(out_dir, n_call)``."""
    calls = {"n": 0}

    def fake_run(cmd, **kwargs):
        if cmd[0] == "git" or cmd[:1] == ["git"]:
            raise AssertionError("git not expected here")
        calls["n"] += 1
        out = Path(cmd[cmd.index("--output-dir") + 1])
        out.mkdir(parents=True, exist_ok=True)
        produce(out, calls["n"])

    monkeypatch.setattr(rc.subprocess, "run", fake_run)
    return calls


# ── selection and resume ──────────────────────────────────────────────


def test_selection_is_by_vintage_and_resume_skips_current(monkeypatch, tmp_path):
    """1.1/1.2 selected regardless of declared method; 1.3 skipped (resume);
    non-canonical basenames excluded (audit m6)."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _fixture_inputs(tmp_path)
    cases = {
        "a/evaluation.json": _doc("1.1"),
        "b/evaluation.json": _doc("1.2"),
        "c/evaluation.json": _doc("1.3"),
        "d/evaluation.json": _doc("1.0"),
        "e/evaluation.json": _doc("1.2", with_recipe=False),
        "archive/f/evaluation.json": _doc("1.1"),
        "g/phase2a-evaluation.json": _doc("1.2"),  # non-canonical basename
    }
    cases["b/evaluation.json"]["_metadata"]["bootstrap"] = {
        "n_iterations": 10000}  # method-silent — still selected
    for rel, doc in cases.items():
        _materialise(tmp_path, rel, doc)
    worklist, census, skips = rc.select_targets(sorted(cases))
    assert sorted(worklist) == ["a/evaluation.json", "b/evaluation.json"]
    assert census == {"selected": 2, "done_1.3": 1, "other_vintage": 1,
                      "unparseable": 0, "no_recipe": 1}
    assert skips == ["e/evaluation.json"]


def test_build_command_uses_measurements_not_declarations(tmp_path):
    doc = _doc("1.2")
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
    assert "--glob" not in joined
    assert "--buffers 20 50" in joined
    assert "--mcc" in joined
    assert "--seed 7" in joined
    assert f"--bootstrap {rc.TARGET_B}" in joined


# ── gates and tripwires ───────────────────────────────────────────────


def test_gate_failure_leaves_file_untouched(monkeypatch, tmp_path):
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _doc("1.2")
    _materialise(tmp_path, "cell/evaluation.json", committed)
    original = (tmp_path / "cell/evaluation.json").read_bytes()
    doctored = json.loads(json.dumps(committed))
    doctored["summary"]["buffers"][0]["f1"] = 0.51

    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(doctored)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    assert row["reason"] == "point estimates moved"
    assert (tmp_path / "cell/evaluation.json").read_bytes() == original


@pytest.mark.parametrize("lo,hi,expected_fragment", [
    (0.49, 0.51, "width ratio 0.100"),   # 10x narrowing — below the band
    (0.0, 0.0, "collapsed"),             # zero-width collapse (audit M3)
    (-4.5, 5.5, "width ratio 50.000"),   # 50x explosion (audit M3 upper hole)
])
def test_width_tripwire_closes_the_audit_holes(monkeypatch, tmp_path,
                                               lo, hi, expected_fragment):
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _doc("1.2")
    _materialise(tmp_path, "cell/evaluation.json", committed)
    replayed = json.loads(json.dumps(committed))
    replayed["summary"]["buffers"][0]["f1_ci_lower"] = lo
    replayed["summary"]["buffers"][0]["f1_ci_upper"] = hi
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    assert expected_fragment in row["reason"]


def test_width_uses_widest_buffer_when_20m_absent(monkeypatch, tmp_path):
    """Cells with no 20 m row are still guarded (audit M3: 91 such cells)."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _doc("1.2")
    committed["summary"]["buffers"] = [
        {"buffer_metres": 30, "f1": 0.5, "precision": 0.5, "recall": 0.5,
         "f1_ci_lower": 0.4, "f1_ci_upper": 0.6}]
    _materialise(tmp_path, "cell/evaluation.json", committed)
    replayed = json.loads(json.dumps(committed))
    replayed["summary"]["buffers"][0]["f1_ci_lower"] = 0.5
    replayed["summary"]["buffers"][0]["f1_ci_upper"] = 0.5
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    assert "30 m" in row["reason"]


def test_worker_exception_becomes_a_failure_row(monkeypatch, tmp_path):
    """A corrupt committed file must yield a row, not an exception (M1)."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    p = tmp_path / "cell/evaluation.json"
    p.parent.mkdir(parents=True)
    p.write_text("{ not json")
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    assert "worker exception" in row["reason"]


# ── the vintage-frozen fallback (audit B1) ────────────────────────────


def test_frozen_fallback_accepts_and_normalises_provenance(monkeypatch, tmp_path):
    """Attempt 1 fails the gate; the frozen attempt passes; the committed
    artefact records repo-relative inputs plus the pinned vintage."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    committed = _doc("1.2")
    _materialise(tmp_path, "cell/evaluation.json", committed)
    _fixture_inputs(tmp_path)

    moved = json.loads(json.dumps(committed))
    moved["summary"]["buffers"][0]["f1"] = 0.51
    good = json.loads(json.dumps(committed))
    good["_metadata"]["metadata_version"] = "1.3"
    good["_metadata"]["cli_args"]["detections"] = ["/tmp/frozen/det.geojson"]
    good["_metadata"]["cli_args"]["ground_truth"] = "/tmp/frozen/gt.geojson"
    good["summary"]["buffers"][0]["f1_ci_lower"] = 0.3
    good["summary"]["buffers"][0]["f1_ci_upper"] = 0.7

    def produce(out, n):
        payload = moved if n == 1 else good
        (out / "evaluation.json").write_text(json.dumps(payload))
        (out / "evaluation.csv").write_text("csv")

    _fake_replay(monkeypatch, produce)
    monkeypatch.setattr(rc, "vintage_assignments",
                        lambda *a, **k: [{"gt.geojson": "abc"}])
    monkeypatch.setattr(
        rc, "freeze_inputs",
        lambda recipe, assignment, work: (dict(recipe),
                                          {"gt.geojson": "abc123def"}))

    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "ok"
    assert row["attempt"] == "frozen"
    assert row["input_vintage"] == {"gt.geojson": "abc123def"}
    on_disk = json.loads((tmp_path / "cell/evaluation.json").read_text())
    assert on_disk["_metadata"]["metadata_version"] == "1.3"
    # Provenance normalised back to repo-relative paths (no temp paths).
    assert on_disk["_metadata"]["cli_args"]["detections"] == ["det.geojson"]
    assert on_disk["_metadata"]["cli_args"]["ground_truth"] == "gt.geojson"
    assert on_disk["_metadata"]["e82_input_vintage"] == {
        "gt.geojson": "abc123def"}
    assert (tmp_path / "cell/evaluation.csv").read_text() == "csv"


def test_passing_replay_replaces_siblings(monkeypatch, tmp_path):
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _doc("1.2")
    _materialise(tmp_path, "cell/evaluation.json", committed)
    widened = json.loads(json.dumps(committed))
    widened["summary"]["buffers"][0]["f1_ci_lower"] = 0.3
    widened["summary"]["buffers"][0]["f1_ci_upper"] = 0.7
    widened["_metadata"]["metadata_version"] = "1.3"

    def produce(out, n):
        (out / "evaluation.json").write_text(json.dumps(widened))
        (out / "evaluation.csv").write_text("csv")

    _fake_replay(monkeypatch, produce)
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "ok"
    assert row["attempt"] == "current"
    assert row["width_ratio"] == pytest.approx(2.0)
    assert row["bootstrap_after"] == rc.TARGET_B
    on_disk = json.loads((tmp_path / "cell/evaluation.json").read_text())
    assert on_disk["_metadata"]["metadata_version"] == "1.3"
    # No staging residue from the atomic replace (audit m1).
    assert not list((tmp_path / "cell").glob("*.e82tmp"))


# ── main()-level guards ───────────────────────────────────────────────


def _run_main(monkeypatch, tmp_path, argv, tracked, docs):
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _fixture_inputs(tmp_path)
    for rel, doc in docs.items():
        _materialise(tmp_path, rel, doc)

    real_run = rc.subprocess.run

    def fake_run(cmd, **kwargs):
        if cmd[:2] == ["git", "ls-files"]:
            class R:
                stdout = "\n".join(tracked)
            return R()
        return real_run(cmd, **kwargs)

    monkeypatch.setattr(rc.subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["rerun_bca_corpus.py", *argv])
    return rc.main()


def test_skip_census_mismatch_refuses_to_run(monkeypatch, tmp_path):
    """A checkout resolving different inputs must not start (audit M7)."""
    docs = {"a/evaluation.json": _doc("1.2")}
    code = _run_main(monkeypatch, tmp_path,
                     ["--dry-run", "--expect-skips", "4"],
                     list(docs), docs)
    assert code == 3


def test_pilot_zero_is_rejected(monkeypatch, tmp_path):
    """--pilot 0 must error out, not silently run the corpus (audit m2)."""
    docs = {"a/evaluation.json": _doc("1.2")}
    with pytest.raises(SystemExit) as exc:
        _run_main(monkeypatch, tmp_path,
                  ["--pilot", "0", "--expect-skips", "0"], list(docs), docs)
    assert exc.value.code == 2


def test_dry_run_reports_named_skips(monkeypatch, tmp_path, caplog):
    import logging as _logging
    caplog.set_level(_logging.INFO, logger="scripts.rerun_bca_corpus")
    docs = {"a/evaluation.json": _doc("1.2"),
            "b/evaluation.json": _doc("1.2", with_recipe=False)}
    code = _run_main(monkeypatch, tmp_path,
                     ["--dry-run", "--expect-skips", "1"], list(docs), docs)
    assert code == 0
    assert any("skip (no recipe): b/evaluation.json" in r.message
               for r in caplog.records)


def test_vintage_assignments_order_and_cap(monkeypatch):
    """Baseline first, then single flips, then all-after; capped (audit B1)."""
    cands = {"det.geojson": ["B1", "A1"], "gt.geojson": ["B2", "A2"],
             "bounds.geojson": ["B3"]}
    monkeypatch.setattr(rc, "adjacent_commits",
                        lambda path, as_of: cands[path])
    recipe = {"detections": ["det.geojson"], "ground_truth": "gt.geojson",
              "bounds": "bounds.geojson"}
    plans = rc.vintage_assignments(recipe, "2026-05-03T00:00:00+00:00")
    assert plans[0] == {"det.geojson": "B1", "gt.geojson": "B2",
                        "bounds.geojson": "B3"}
    assert {"det.geojson": "A1", "gt.geojson": "B2",
            "bounds.geojson": "B3"} in plans
    assert {"det.geojson": "B1", "gt.geojson": "A2",
            "bounds.geojson": "B3"} in plans
    assert plans[-1] == {"det.geojson": "A1", "gt.geojson": "A2",
                         "bounds.geojson": "B3"}
    assert len(plans) <= 6


def test_vintage_search_rescues_after_frozen_fails(monkeypatch, tmp_path):
    """The mixed-vintage state (pilot signature) is found by the search."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    committed = _doc("1.2")
    _materialise(tmp_path, "cell/evaluation.json", committed)
    _fixture_inputs(tmp_path)

    moved = json.loads(json.dumps(committed))
    moved["summary"]["buffers"][0]["f1"] = 0.51
    good = json.loads(json.dumps(committed))
    good["_metadata"]["metadata_version"] = "1.3"
    good["summary"]["buffers"][0]["f1_ci_lower"] = 0.3
    good["summary"]["buffers"][0]["f1_ci_upper"] = 0.7

    def produce(out, n):
        # current fails, frozen (all-before) fails, first flip passes
        payload = moved if n <= 2 else good
        (out / "evaluation.json").write_text(json.dumps(payload))

    _fake_replay(monkeypatch, produce)
    monkeypatch.setattr(rc, "vintage_assignments",
                        lambda *a, **k: [{"det.geojson": "BBB"},
                                         {"det.geojson": "AAA"}])
    monkeypatch.setattr(
        rc, "freeze_inputs",
        lambda recipe, assignment, work: (dict(recipe),
                                          {k: v[:9] for k, v
                                           in assignment.items()}))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "ok"
    assert row["attempt"] == "vintage-search-1"
    assert row["input_vintage"] == {"det.geojson": "AAA"}
