"""
Content-anchor tests for the run-metadata layer (``scripts/lib_llm_metadata.py``).

Guards the Finding 5 fixes of ``reports/name-keyed-cache-audit-2026-09-12.md``:

1. ``_compute_library_hash`` documented itself as an example-library
   fingerprint but hashed only the ``(path, label, category)`` triples from the
   config — the example images' FILENAMES. Replacing a crop under the same
   filename left the hash unchanged, while the sibling
   ``system_instruction_hash`` is a true content hash. The field is a
   ``changed_field`` in the no-op rule table that polices "only the target
   parameter changed" (the H10/H12 failure class), so a name-only hash weakened
   a live guard.
2. ``merge_meta`` started from ``merged = dict(original)`` and never re-set
   ``configuration``, so a pass resumed under an edited config recorded the
   FIRST launch's configuration — including its ``system_instruction_hash`` —
   for a file whose later tiles were produced under different instructions.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_llm_metadata import (  # noqa: E402
    LIBRARY_HASH_BASIS,
    LLMMetadataTracker,
    compare_configurations,
    merge_meta,
)

pytestmark = pytest.mark.tier1


# ---------------------------------------------------------------------------
# library_hash
# ---------------------------------------------------------------------------


def _example_config(paths: list[Path], *, labels: list[str] | None = None) -> dict:
    """A config whose examples are absolute paths to real image files."""
    labels = labels or ["Positive"] * len(paths)
    return {
        "version": "test-config",
        "examples": [
            {"path": str(p), "label": lab, "category": "canonical_positive"}
            for p, lab in zip(paths, labels, strict=True)
        ],
    }


def _write_image(path: Path, payload: bytes) -> Path:
    """Write a stand-in example image (bytes are all the hash reads)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def test_library_hash_changes_when_an_image_is_replaced(tmp_path: Path) -> None:
    """The defect, directly: same filename, different crop, different hash."""
    image = _write_image(tmp_path / "neutral-naming" / "example_08.png", b"crop-A")
    config = _example_config([image])

    before = LLMMetadataTracker._compute_library_hash(config)
    _write_image(image, b"crop-B")
    after = LLMMetadataTracker._compute_library_hash(config)

    assert before != after, (
        "replacing an example image under the same filename must change "
        "library_hash — the pre-fix hash covered filenames only"
    )


def test_library_hash_is_order_independent(tmp_path: Path) -> None:
    """Example ordering does not change the library's identity."""
    a = _write_image(tmp_path / "a.png", b"aaa")
    b = _write_image(tmp_path / "b.png", b"bbb")
    assert (
        LLMMetadataTracker._compute_library_hash(_example_config([a, b]))
        == LLMMetadataTracker._compute_library_hash(_example_config([b, a]))
    )


def test_library_hash_still_distinguishes_labels(tmp_path: Path) -> None:
    """The path/label/category triple remains inside the digest."""
    a = _write_image(tmp_path / "a.png", b"aaa")
    assert (
        LLMMetadataTracker._compute_library_hash(
            _example_config([a], labels=["Positive"]),
        )
        != LLMMetadataTracker._compute_library_hash(
            _example_config([a], labels=["Negative"]),
        )
    )


def test_library_hash_without_examples_is_unchanged() -> None:
    """A config with no examples keeps the legacy sentinel."""
    assert LLMMetadataTracker._compute_library_hash({}) == "no_examples"
    assert LLMMetadataTracker._compute_library_hash(
        {"examples": []},
    ) == "no_examples"


def test_missing_example_is_recorded_not_ignored(tmp_path: Path) -> None:
    """An unresolvable example hashes as "missing" and changes the digest."""
    real = _write_image(tmp_path / "a.png", b"aaa")
    absent = tmp_path / "gone.png"

    manifest = LLMMetadataTracker._example_library_manifest(
        _example_config([real, absent]),
    )
    digests = {e["path"]: e["sha256"] for e in manifest}
    assert digests[str(absent)] == "missing"
    assert digests[str(real)] == hashlib.sha256(b"aaa").hexdigest()

    assert (
        LLMMetadataTracker._compute_library_hash(_example_config([real, absent]))
        != LLMMetadataTracker._compute_library_hash(_example_config([real]))
    )


def test_repo_relative_example_paths_resolve(tmp_path: Path) -> None:
    """A path relative to ``inputs/examples`` resolves, as the pipeline does."""
    config = {
        "examples": [
            {"path": "neutral-naming/example_01.png", "label": "Positive",
             "category": "canonical_positive"},
        ],
    }
    manifest = LLMMetadataTracker._example_library_manifest(config)
    expected = PROJECT_ROOT / "inputs/examples/neutral-naming/example_01.png"
    if expected.is_file():
        assert manifest[0]["sha256"] == hashlib.sha256(
            expected.read_bytes(),
        ).hexdigest()
    else:  # pragma: no cover - committed corpus present in this repo
        pytest.skip("example corpus not present in this checkout")


def test_finalised_meta_records_the_manifest_and_basis(tmp_path: Path) -> None:
    """The artefact says what ``library_hash`` was computed over."""
    image = _write_image(tmp_path / "a.png", b"aaa")
    tracker = LLMMetadataTracker(
        config=_example_config([image]),
        system_instruction="instructions",
        script_name="test",
        script_version="0.0.1",
    )
    meta = tracker.finalise()
    cfg = meta["configuration"]
    assert cfg["library_hash_basis"] == LIBRARY_HASH_BASIS
    assert cfg["library_manifest"][0]["sha256"] == hashlib.sha256(
        b"aaa",
    ).hexdigest()
    assert cfg["library_hash"] == LLMMetadataTracker._compute_library_hash(
        _example_config([image]),
    )


# ---------------------------------------------------------------------------
# merge_meta: configuration_history
# ---------------------------------------------------------------------------


def _meta(*, run_id: str, instruction_hash: str, temperature: float = 0.3) -> dict:
    """A minimal per-pass meta with a configuration block."""
    return {
        "run_id": run_id,
        "timestamp": {
            "start": "2026-09-01T00:00:00+00:00",
            "end": "2026-09-01T01:00:00+00:00",
            "duration_seconds": 3600.0,
        },
        "configuration": {
            "version": "test-config",
            "system_instruction_hash": instruction_hash,
            "system_instruction_text": "the full text, excluded from the diff",
            "temperature": temperature,
            "full_config_snapshot": {"temperature": temperature},
        },
        "execution_stats": {"items_processed": 1, "completed_items": [run_id]},
        "usage_stats": {},
        "cost_estimate": {},
    }


def test_agreeing_configurations_record_history_without_a_difference() -> None:
    """A resume under the same config records the chain and flags no change."""
    original = _meta(run_id="a", instruction_hash="hash-1")
    recovery = _meta(run_id="b", instruction_hash="hash-1")

    merged = merge_meta(original, recovery)

    assert merged["configuration"] == original["configuration"]
    history = merged["configuration_history"]
    assert [h["source"] for h in history] == ["original", "resume"]
    assert history[-1]["differs_from_previous"] is False
    assert history[-1]["changed_fields"] == []


def test_disagreeing_configurations_are_recorded_and_warned(caplog) -> None:
    """An edited instruction file is named, not silently discarded."""
    original = _meta(run_id="a", instruction_hash="hash-1")
    recovery = _meta(run_id="b", instruction_hash="hash-2", temperature=0.7)

    with caplog.at_level("WARNING"):
        merged = merge_meta(original, recovery)

    # The original block still wins — downstream readers are unaffected.
    assert merged["configuration"]["system_instruction_hash"] == "hash-1"
    entry = merged["configuration_history"][-1]
    assert entry["differs_from_previous"] is True
    assert set(entry["changed_fields"]) == {
        "system_instruction_hash", "temperature", "full_config_snapshot_sha256",
    }
    assert "configuration_history" in caplog.text


def test_configuration_history_accumulates_across_chained_merges() -> None:
    """Three passes leave three entries, in order."""
    merged = merge_meta(
        _meta(run_id="a", instruction_hash="hash-1"),
        _meta(run_id="b", instruction_hash="hash-1"),
    )
    merged = merge_meta(merged, _meta(run_id="c", instruction_hash="hash-2"))

    history = merged["configuration_history"]
    assert [h["run_id"] for h in history] == ["a", "b", "c"]
    assert history[-1]["changed_fields"] == ["system_instruction_hash"]


def test_instruction_text_is_excluded_from_the_diff() -> None:
    """The text is covered by its hash; it must not double-report."""
    original = _meta(run_id="a", instruction_hash="hash-1")
    recovery = _meta(run_id="b", instruction_hash="hash-1")
    recovery["configuration"]["system_instruction_text"] = "different wording"
    assert compare_configurations(original, recovery) == []


def test_metas_without_configuration_blocks_are_untouched() -> None:
    """Legacy metas with no configuration block gain no history key."""
    original = {"execution_stats": {}, "usage_stats": {}, "timestamp": {}}
    recovery = {"execution_stats": {}, "usage_stats": {}, "timestamp": {}}
    merged = merge_meta(original, recovery)
    assert "configuration_history" not in merged
    assert compare_configurations(original, recovery) == []


def test_full_config_snapshot_difference_is_summarised_by_digest() -> None:
    """A snapshot change is named as one field, not dumped into the diff."""
    original = _meta(run_id="a", instruction_hash="hash-1")
    recovery = _meta(run_id="b", instruction_hash="hash-1")
    recovery["configuration"]["full_config_snapshot"] = {
        "temperature": 0.3, "examples": [{"path": "x.png"}],
    }
    changed = compare_configurations(original, recovery)
    assert changed == ["full_config_snapshot_sha256"]
    entry = merge_meta(original, recovery)["configuration_history"][-1]
    # Only the digest is carried; the snapshot itself is not duplicated.
    assert "full_config_snapshot" not in entry["configuration"]
    assert "full_config_snapshot_sha256" in entry["configuration"]
    assert "examples" not in json.dumps(entry["configuration"])
