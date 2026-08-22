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


def _multirun_doc() -> dict:
    """A multi-run cell with the D41 mis-aggregation: summary = run 1's point."""
    doc = _doc("1.2")
    doc["summary"]["tile_classification"] = {
        "mcc": {"point": 0.3065, "mean": 0.3053},
        "confusion": {"tp": 227, "tn": 52, "fp": 206, "fn": 2},
    }
    doc["per_run"] = [
        {"tile_classification": {"mcc": {"point": 0.3065}}},
        {"tile_classification": {"mcc": {"point": 0.2934}}},
        {"tile_classification": {"mcc": {"point": 0.316}}},
    ]
    return doc


def test_d41_reaggregation_accepted_when_per_run_reproduces(monkeypatch, tmp_path):
    """Summary tile point moves to the defined-pass mean -> accepted, flagged."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _multirun_doc()
    _materialise(tmp_path, "cell/evaluation.json", committed)
    replayed = json.loads(json.dumps(committed))
    replayed["_metadata"]["metadata_version"] = "1.3"
    replayed["summary"]["tile_classification"]["mcc"]["point"] = 0.3053
    replayed["summary"]["buffers"][0]["f1_ci_lower"] = 0.3
    replayed["summary"]["buffers"][0]["f1_ci_upper"] = 0.7
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "ok"
    assert row["summary_tile_point_reaggregated"] == {"mcc": [0.3065, 0.3053]}


def test_d41_exception_requires_per_run_reproduction(monkeypatch, tmp_path):
    """A moved PER-RUN point is a real failure, never re-aggregation."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _multirun_doc()
    _materialise(tmp_path, "cell/evaluation.json", committed)
    replayed = json.loads(json.dumps(committed))
    replayed["per_run"][1]["tile_classification"]["mcc"]["point"] = 0.30
    replayed["summary"]["tile_classification"]["mcc"]["point"] = 0.3088
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    assert "run1/mcc" in str(row["attempts"][0]["moved"])


def test_d41_exception_requires_the_exact_defined_pass_mean(monkeypatch, tmp_path):
    """A summary point moving to anything BUT the mean stays a failure."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _multirun_doc()
    _materialise(tmp_path, "cell/evaluation.json", committed)
    replayed = json.loads(json.dumps(committed))
    replayed["summary"]["tile_classification"]["mcc"]["point"] = 0.3100
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"


# ── C1 label-keyed comparison + D writer-exact mean (PI ruling 2026-08-22;
#    evidence: reports/e82-d41-widening-inspection-2026-08-22.md) ──────────

# The real 10-pass pool behind inspection § 1.5 (outputs/h11/pv-diag-384/
# image-n5/image-t0.7): its per-run mcc mean sits on a 4 dp half-boundary,
# so np.mean (pairwise summation) rounds to 0.3295 in lexicographic order
# and 0.3296 in numeric order, while a naive sum()/len() gives 0.3296 in
# both — the defect PI ruling D fixes.
_BOUNDARY_POOL = {
    "run1": 0.3232, "run2": 0.3430, "run3": 0.3396, "run4": 0.3396,
    "run5": 0.3267, "run6": 0.3151, "run7": 0.3232, "run8": 0.3257,
    "run9": 0.3302, "run10": 0.3292,
}
# An order-insensitive pool for the pure-permutation cases: mean 0.55 in
# any order, nowhere near a rounding boundary.
_STABLE_POOL = {f"run{i}": round(0.1 * i, 1) for i in range(1, 11)}

_LEX = sorted(_BOUNDARY_POOL)                          # run1, run10, run2, ...
_NUM = sorted(_BOUNDARY_POOL, key=lambda s: int(s[3:]))  # run1, run2, ... run10


def _labelled_pool_doc(pool: dict, order: list, summary_mcc: float,
                       buffer_f1: dict | None = None,
                       summary_buffer_f1: float | None = None) -> dict:
    """A >= 10-run cell whose labelled per_run blocks sit in a given order.

    ``buffer_f1`` optionally maps label -> per-run f1 at the 20 m buffer,
    with ``summary_buffer_f1`` the summary 20 m f1 (the writer's mean).
    """
    doc = _doc("1.2")
    doc["summary"]["tile_classification"] = {
        "mcc": {"point": summary_mcc},
        "confusion": {"tp": 227, "tn": 52, "fp": 206, "fn": 2},
    }
    doc["per_run"] = [
        {"label": lab, "tile_classification": {"mcc": {"point": pool[lab]}}}
        for lab in order
    ]
    if buffer_f1 is not None:
        for run in doc["per_run"]:
            run["buffers"] = [
                {"buffer_metres": 20, "f1": buffer_f1[run["label"]]}]
    if summary_buffer_f1 is not None:
        doc["summary"]["buffers"][0]["f1"] = summary_buffer_f1
    return doc


def test_c1_lexicographic_pool_normalised_by_label(monkeypatch, tmp_path):
    """A >= 10-run pool committed in lexicographic order passes when the
    canonical resolver replays it numerically: same labelled measurements,
    permuted indices (PI ruling C1 regression test 1)."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _labelled_pool_doc(_STABLE_POOL, _LEX, 0.55)
    _materialise(tmp_path, "cell/evaluation.json", committed)
    replayed = _labelled_pool_doc(_STABLE_POOL, _NUM, 0.55)
    replayed["_metadata"]["metadata_version"] = "1.3"
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "ok"
    assert row["per_run_order_normalised"]["per_run_labels"] == {
        "committed": _LEX, "replayed": _NUM}
    assert "summary_tile_point" not in row["per_run_order_normalised"]
    assert "summary_tile_point_reaggregated" not in row


def test_c1_moved_measurement_fails_by_its_own_label(monkeypatch, tmp_path):
    """Label-keying loosens nothing: a genuinely moved measurement in a
    permuted pool still fails, attributed to its label."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _labelled_pool_doc(_STABLE_POOL, _LEX, 0.55)
    _materialise(tmp_path, "cell/evaluation.json", committed)
    replayed = _labelled_pool_doc(dict(_STABLE_POOL, run7=0.71), _NUM, 0.55)
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    assert "run7/mcc" in str(row["attempts"][0]["moved"])


def test_c1_changed_pool_fails_as_label_set_mismatch(monkeypatch, tmp_path):
    """A replay that resolves a DIFFERENT pool fails on the label sets."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _labelled_pool_doc(_STABLE_POOL, _LEX, 0.55)
    _materialise(tmp_path, "cell/evaluation.json", committed)
    swapped = {("run11" if k == "run10" else k): v
               for k, v in _STABLE_POOL.items()}
    replayed = _labelled_pool_doc(
        swapped, sorted(swapped, key=lambda s: int(s[3:])), 0.55)
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    moved = row["attempts"][0]["moved"]
    assert moved["labels"] == [["run10"], ["run11"]] or \
        moved["labels"] == (["run10"], ["run11"])


def test_d_reaggregated_mean_matches_writer_at_half_boundary(monkeypatch, tmp_path):
    """The exception helper must agree with the writer's np.mean at a 4 dp
    half-boundary (PI ruling D regression test 2): the real D41 cell
    mcc/384px/flash-image-minimal-t-0-7 re-failed because sum()/len() gave
    0.3296 where the writer emitted 0.3295."""
    lex_doc = _labelled_pool_doc(_BOUNDARY_POOL, _LEX, 0.3232)
    num_doc = _labelled_pool_doc(_BOUNDARY_POOL, _NUM, 0.3232)
    assert rc._reaggregated_mean(lex_doc, "mcc") == 0.3295
    assert rc._reaggregated_mean(num_doc, "mcc") == 0.3296

    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    _materialise(tmp_path, "cell/evaluation.json", lex_doc)  # D41: summary = run 1
    replayed = _labelled_pool_doc(_BOUNDARY_POOL, _LEX, 0.3295)
    replayed["_metadata"]["metadata_version"] = "1.3"
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "ok"
    assert row["summary_tile_point_reaggregated"] == {"mcc": [0.3232, 0.3295]}
    assert "per_run_order_normalised" not in row


# The real per-run f1@20m-equivalent pool behind the live 2026-08-22
# failure of n1/384px-14buf-mcc/flash-text-minimal-t-0-0 (its 40 m
# buffer): raw mean 0.52045 — np.mean rounds to 0.5204 in lexicographic
# order and 0.5205 in numeric order.
_BUFFER_F1_POOL = {
    "run1": 0.5236, "run2": 0.5162, "run3": 0.5129, "run4": 0.5233,
    "run5": 0.5236, "run6": 0.5185, "run7": 0.5205, "run8": 0.5256,
    "run9": 0.5236, "run10": 0.5167,
}


def test_order_artefact_buffer_mean_shift_forgiven(monkeypatch, tmp_path):
    """A summary BUFFER value that flips one 4 dp step purely through the
    replay's pass order is forgiven and filed under order-normalisation:
    evaluate_multi_run_mean aggregates buffer metrics with the same
    order-sensitive np.mean as the tile block (live failure 2026-08-22)."""
    lex_doc = _labelled_pool_doc(_STABLE_POOL, _LEX, 0.55,
                                 buffer_f1=_BUFFER_F1_POOL,
                                 summary_buffer_f1=0.5204)
    num_doc = _labelled_pool_doc(_STABLE_POOL, _NUM, 0.55,
                                 buffer_f1=_BUFFER_F1_POOL,
                                 summary_buffer_f1=0.5205)
    assert rc._buffer_mean(lex_doc, (20, "f1")) == 0.5204
    assert rc._buffer_mean(num_doc, (20, "f1")) == 0.5205

    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    _materialise(tmp_path, "cell/evaluation.json", lex_doc)
    replayed = json.loads(json.dumps(num_doc))
    replayed["_metadata"]["metadata_version"] = "1.3"
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "ok"
    norm = row["per_run_order_normalised"]
    assert norm["summary_buffer_points"] == {"20m/f1": [0.5204, 0.5205]}
    assert "summary_tile_point_reaggregated" not in row


def test_buffer_forgiveness_requires_per_run_buffer_reproduction(
        monkeypatch, tmp_path):
    """A genuinely moved per-run BUFFER measurement blocks the buffer-mean
    forgiveness even when the summary values match their own means."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    lex_doc = _labelled_pool_doc(_STABLE_POOL, _LEX, 0.55,
                                 buffer_f1=_BUFFER_F1_POOL,
                                 summary_buffer_f1=0.5204)
    _materialise(tmp_path, "cell/evaluation.json", lex_doc)
    doctored = dict(_BUFFER_F1_POOL, run7=0.5301)  # a real measurement moved
    replayed = _labelled_pool_doc(
        _STABLE_POOL, _NUM, 0.55, buffer_f1=doctored,
        summary_buffer_f1=rc._buffer_mean(
            _labelled_pool_doc(_STABLE_POOL, _NUM, 0.55, buffer_f1=doctored),
            (20, "f1")))
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "failed"
    assert "20m/f1" in str(row["attempts"][0]["moved"])


def test_order_artefact_summary_shift_filed_as_order_not_d41(monkeypatch, tmp_path):
    """The n1-tree twin of the boundary cell: BOTH summaries are correct
    writer means of identical measurements, differing only through
    summation order. Accepted as an order artefact — never counted as a
    D41 re-aggregation, so the contract's n_reaggregated = 19 stays exact."""
    monkeypatch.setattr(rc, "PROJECT_ROOT", tmp_path)
    _no_frozen(monkeypatch)
    committed = _labelled_pool_doc(_BOUNDARY_POOL, _LEX, 0.3295)
    _materialise(tmp_path, "cell/evaluation.json", committed)
    replayed = _labelled_pool_doc(_BOUNDARY_POOL, _NUM, 0.3296)
    replayed["_metadata"]["metadata_version"] = "1.3"
    _fake_replay(monkeypatch, lambda out, n:
                 (out / "evaluation.json").write_text(json.dumps(replayed)))
    row = rc.process_one("cell/evaluation.json")
    assert row["status"] == "ok"
    assert "summary_tile_point_reaggregated" not in row
    norm = row["per_run_order_normalised"]
    assert norm["per_run_labels"] == {"committed": _LEX, "replayed": _NUM}
    assert norm["summary_tile_point"] == {"mcc": [0.3295, 0.3296]}
