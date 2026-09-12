"""
Content-anchor tests for the evaluation and detection-resume guards.

Guards the Findings 6 and 12 fixes of
``reports/name-keyed-cache-audit-2026-09-12.md``:

* ``evaluate_detections._build_metadata`` recorded a state WORD per input
  (``clean`` / ``modified`` / …) plus the repository HEAD, never the inputs'
  own bytes — so nothing bound an evaluation to the detections file it scored
  (the blob-hash assertions live in
  ``tests/test_evaluate_detections_metadata.py``, beside the rest of that
  module's metadata tests).
* ``lib_experiment_intent`` compared ``instruction_file`` by FILENAME, so an
  in-place edit of the instruction markdown left all eight compared fields
  agreeing and a resume silently mixed tiles answered under two prompts inside
  one pass file.
* ``r2_score_cells.Job.done`` tested PRESENCE of an ``evaluation.json``, so a
  cell whose detections were re-materialised after scoring resumed as "already
  done" and kept the earlier file's evaluation.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import lib_experiment_intent as lei  # noqa: E402
from scripts.lib_content_anchor import git_blob_hash  # noqa: E402

pytestmark = pytest.mark.tier1


# ---------------------------------------------------------------------------
# The intent check compares the instruction file's hash, not its name
# ---------------------------------------------------------------------------


def _instruction(tmp_path: Path, text: str) -> Path:
    """Write a stand-in system-instruction markdown file."""
    path = tmp_path / "detect_test.md"
    path.write_text(text, encoding="utf-8")
    return path


def _config(instruction: Path) -> dict:
    """A minimal variant config naming *instruction* by absolute path."""
    return {
        "version": "detect_test-v1",
        "hypothesis": "H1",
        "model": "gemini-3-flash",
        "instruction_file": str(instruction),
        "include_example_images": False,
        "temperature": 0.3,
        "thinking_level": "high",
    }


def test_instruction_file_hash_tracks_content(tmp_path: Path) -> None:
    """The hash follows the file's bytes, not its name."""
    instruction = _instruction(tmp_path, "Find the mounds.\n")
    config = _config(instruction)
    assert lei.instruction_file_hash(config) == hashlib.sha256(
        b"Find the mounds.\n",
    ).hexdigest()

    instruction.write_text("Find the mounds. Be conservative.\n", encoding="utf-8")
    assert lei.instruction_file_hash(config) != hashlib.sha256(
        b"Find the mounds.\n",
    ).hexdigest()


def test_instruction_file_hash_is_none_when_unresolvable(tmp_path, caplog) -> None:
    """An unresolvable instruction file is unknown, and says so."""
    assert lei.instruction_file_hash({}) is None
    with caplog.at_level("WARNING"):
        assert lei.instruction_file_hash(
            {"instruction_file": "does-not-exist.md"},
        ) is None
    assert "not found" in caplog.text


def test_intent_records_the_instruction_hash_row(tmp_path: Path) -> None:
    """The written intent carries the instruction file's content hash."""
    instruction = _instruction(tmp_path, "Find the mounds.\n")
    config = _config(instruction)
    path, is_consistent, _diffs = lei.write_experiment_intent(
        experiment_root=tmp_path / "run",
        config=config,
        config_path=tmp_path / "config.json",
        dry_run=False,
    )
    assert is_consistent is True
    text = path.read_text(encoding="utf-8")
    assert f"| `{lei.INSTRUCTION_HASH_FIELD}` |" in text
    assert lei.instruction_file_hash(config) in text


def test_edited_instruction_file_makes_the_intent_inconsistent(
    tmp_path: Path,
) -> None:
    """The defect, directly: same filename, edited prompt, now detected."""
    instruction = _instruction(tmp_path, "Find the mounds.\n")
    config = _config(instruction)
    root = tmp_path / "run"
    lei.write_experiment_intent(
        experiment_root=root, config=config,
        config_path=tmp_path / "config.json", dry_run=False,
    )

    # Edit the instruction markdown in place — every other compared field
    # (version, hypothesis, temperature, thinking_level, filename, model)
    # is untouched, which is exactly why the pre-fix check passed.
    instruction.write_text("Find every ring feature.\n", encoding="utf-8")

    _path, is_consistent, _diffs = lei.write_experiment_intent(
        experiment_root=root, config=config,
        config_path=tmp_path / "config.json", dry_run=False,
    )
    assert is_consistent is False


def test_unedited_instruction_file_stays_consistent(tmp_path: Path) -> None:
    """No edit, no complaint — behaviour preserved for unchanged inputs."""
    instruction = _instruction(tmp_path, "Find the mounds.\n")
    config = _config(instruction)
    root = tmp_path / "run"
    lei.write_experiment_intent(
        experiment_root=root, config=config,
        config_path=tmp_path / "config.json", dry_run=False,
    )
    _path, is_consistent, _diffs = lei.write_experiment_intent(
        experiment_root=root, config=config,
        config_path=tmp_path / "config.json", dry_run=False,
    )
    assert is_consistent is True


def test_legacy_intent_without_the_hash_row_is_not_a_mismatch(
    tmp_path: Path,
) -> None:
    """An intent file written before the row existed must not start failing."""
    instruction = _instruction(tmp_path, "Find the mounds.\n")
    config = _config(instruction)
    legacy = "\n".join([
        "# Experiment Intent",
        "",
        "## Hypothesis",
        "",
        "- **ID**: H1",
        "- **Variant version**: `detect_test-v1`",
        "",
        "## Verified values",
        "",
        "| Field | Value |",
        "|---|---|",
        "| `model` | gemini-3-flash |",
        f"| `instruction_file` | {instruction} |",
        "| `include_example_images` | **false** |",
        "| `temperature` | 0.3 |",
        "| `thinking_level` | high |",
        "",
    ])
    is_consistent, mismatches = lei._existing_intent_matches(legacy, config)
    assert is_consistent is True
    assert mismatches == []


# ---------------------------------------------------------------------------
# r2_score_cells.Job.done verifies the evaluation against the detections
# ---------------------------------------------------------------------------


def _job(tmp_path: Path, monkeypatch):
    """A Job whose detections and out_dir live under *tmp_path*."""
    from scripts import r2_score_cells as r2

    monkeypatch.setattr(r2, "PROJECT_ROOT", tmp_path)
    detections = tmp_path / "detections.geojson"
    detections.write_text(
        json.dumps({"type": "FeatureCollection", "features": []}),
        encoding="utf-8",
    )
    out_dir = tmp_path / "cell"
    out_dir.mkdir()
    return r2, r2.Job("TEST-k3", detections, out_dir, "TEST-k3-r2-gt")


def _write_evaluation(job, *, blob: str | None, key: str = "detections.geojson"):
    """Write an ``evaluation.json`` whose anchor is *blob* (None = legacy)."""
    state: dict = {"head": "abc123", "inputs": {key: "clean"}}
    if blob is not None:
        state["blob_hashes"] = {key: blob}
    (job.out_dir / "evaluation.json").write_text(
        json.dumps({"_metadata": {"input_git_state": state}}),
        encoding="utf-8",
    )


def test_job_done_verifies_a_matching_anchor(tmp_path, monkeypatch) -> None:
    """An evaluation scored from today's detections is done."""
    r2, job = _job(tmp_path, monkeypatch)
    _write_evaluation(job, blob=git_blob_hash(job.detections))
    verdict, _detail = job.evaluation_provenance()
    assert verdict == r2.PROVENANCE_VERIFIED
    assert job.done is True


def test_job_done_rejects_a_rematerialised_detections_file(
    tmp_path, monkeypatch, caplog,
) -> None:
    """The defect, directly: detections re-materialised after scoring."""
    r2, job = _job(tmp_path, monkeypatch)
    _write_evaluation(job, blob=git_blob_hash(job.detections))

    job.detections.write_text(
        json.dumps({
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": None, "properties": {}}],
        }),
        encoding="utf-8",
    )

    verdict, detail = job.evaluation_provenance()
    assert verdict == r2.PROVENANCE_MISMATCH
    assert "but that file is now" in detail
    with caplog.at_level("ERROR"):
        assert job.done is False
    assert "will re-score" in caplog.text


def test_job_done_treats_a_legacy_evaluation_as_unknown_but_done(
    tmp_path, monkeypatch, caplog,
) -> None:
    """A pre-anchor evaluation still resumes, with a warning — never a match."""
    r2, job = _job(tmp_path, monkeypatch)
    _write_evaluation(job, blob=None)
    verdict, detail = job.evaluation_provenance()
    assert verdict == r2.PROVENANCE_UNKNOWN
    assert "no content anchor" in detail
    with caplog.at_level("WARNING"):
        assert job.done is True
    assert "UNKNOWN" in caplog.text


def test_job_done_is_false_without_an_evaluation(tmp_path, monkeypatch) -> None:
    """No evaluation file at all is still simply not done."""
    _r2, job = _job(tmp_path, monkeypatch)
    assert job.done is False


def test_job_done_handles_an_unparseable_evaluation(
    tmp_path, monkeypatch, caplog,
) -> None:
    """A corrupt evaluation is unknown provenance, not a crash."""
    r2, job = _job(tmp_path, monkeypatch)
    (job.out_dir / "evaluation.json").write_text("{not json", encoding="utf-8")
    verdict, _detail = job.evaluation_provenance()
    assert verdict == r2.PROVENANCE_UNKNOWN
    with caplog.at_level("WARNING"):
        assert job.done is True
