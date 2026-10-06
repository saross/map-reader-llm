"""
Tests for ``scripts/lib_manipulation_signature.py`` (PR #24 review, findings 4 and 9).

The manipulation gate's harvester and signature moved out of the 2026-10-05
report's scratch scripts into this library, so archiving the report cannot
break the gate. These tests pin:

- the copy against its original: on a synthetic meta, :func:`harvest`
  returns every field the 2026-10-05 harvester returns, with the same value
  (skipped once that report directory is archived);
- the two fields the gate used to re-read each meta for
  (``max_output_tokens`` and ``dispatched_ids``), and that the gate now
  parses each meta once;
- that ``check_manipulation`` takes the harvester from this library, not
  from ``reports/``;
- that a gzipped meta, named ``.meta.json.gz`` or gzipped in place, is read
  like a plain one (finding 6: its pass was silently dropped).

Tier 1: synthetic metas in ``tmp_path``; no committed data is read.
"""

from __future__ import annotations

import gzip
import importlib.util
import json
from pathlib import Path

import pytest

from scripts import check_manipulation as cm
from scripts import lib_manipulation_signature as sig

pytestmark = pytest.mark.tier1

REPO = Path(__file__).resolve().parents[1]
ORIGINAL = REPO / "reports" / "manipulation-check-2026-10-05-scripts" / "harvest.py"


def _meta(path: Path) -> Path:
    """Write a synthetic proposer meta exercising most harvested fields.

    Args:
        path: Where to write it.

    Returns:
        The path.
    """
    path.write_text(json.dumps({
        "environment": {"script": "4_detect_mounds_batch.py", "git_commit": "abc"},
        "timestamp": {"start": "2026-04-15T04:39:00+00:00"},
        "configuration": {
            "version": "library_scale-8", "model": "gemini-3-flash-preview",
            "instruction_file": "detect_brief-text.md",
            "system_instruction_hash": "e169b7237b853eeaad990fc2e54f",
            "temperature": 0.7, "thinking_level": "high", "tile_size": 384,
            "full_config_snapshot": {
                "version": "library_scale-8", "include_example_images": True,
                "max_output_tokens": 8192, "pool": "pool_160",
                "examples": [{"path": "neutral-naming/example_01.png",
                              "label": "Positive", "category": "canonical_positive"}],
            },
        },
        "usage_stats": {"total_input_tokens": 40_038, "n_responses_with_usage": 2,
                        "by_provider": {"google_gemini": {"request_count": 2}}},
        "per_item_metadata": [{"tokens": {"input_tokens": 20_019, "cached_tokens": 0},
                               "model_version": "gemini-3-flash-preview"}] * 2,
        "execution_stats": {"items_processed": 2, "completed_items": ["t2.png", "t1.png"],
                            "failed_items": [{"item_id": "t3.png"}]},
        "cost_estimate": {"pricing_used": {"model": "gemini-3-flash-preview"}},
    }))
    return path


@pytest.mark.skipif(not ORIGINAL.exists(), reason="the 2026-10-05 report scripts are archived")
def test_the_copy_harvests_what_the_original_harvested(tmp_path) -> None:
    """Every field the 2026-10-05 harvester returns, the copy returns unchanged."""
    spec = importlib.util.spec_from_file_location("original_harvest", ORIGINAL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = str(_meta(tmp_path / "a.meta.json"))
    original, copy = module.harvest(path), sig.harvest(path)
    assert {k: copy[k] for k in original} == original
    assert set(copy) - set(original) == {"max_output_tokens", "dispatched_ids",
                                         "has_configuration"}


def test_a_document_without_a_configuration_is_not_a_meta(tmp_path) -> None:
    """The passes manifest cites results/run-conditions.json beside some
    passes' metas: it parses, but records no request, so the gate's reader
    marks it unreadable instead of harvesting an all-empty signature."""
    register = tmp_path / "run-conditions.json"
    register.write_text(json.dumps({"decomposition": {}}))
    assert sig.harvest(str(register))["has_configuration"] is False
    assert sig.harvest(str(_meta(tmp_path / "a.meta.json")))["has_configuration"] is True
    cm.meta_record.cache_clear()
    assert cm.meta_record(str(register))["error"] == "no configuration block: not a pass meta"
    cm.meta_record.cache_clear()


def test_the_harvest_carries_the_fields_the_gate_reread(tmp_path) -> None:
    """Finding 9: the output budget (from the snapshot here) and the
    dispatched ids, completed plus failed, sorted."""
    rec = sig.harvest(str(_meta(tmp_path / "a.meta.json")))
    assert rec["max_output_tokens"] == 8192
    assert rec["dispatched_ids"] == ["t1.png", "t2.png", "t3.png"]


def test_an_unreadable_meta_is_recorded_not_raised(tmp_path) -> None:
    """A missing or malformed meta yields an ``error`` record, as before."""
    bad = tmp_path / "bad.meta.json"
    bad.write_text("{not json")
    assert "error" in sig.harvest(str(bad))
    assert "error" in sig.harvest(str(tmp_path / "absent.meta.json"))
    (tmp_path / "list.meta.json").write_text("[]")
    assert sig.harvest(str(tmp_path / "list.meta.json"))["error"] == "not a dict"


def test_the_gate_parses_each_meta_once(tmp_path, monkeypatch) -> None:
    """Finding 9: ``meta_record`` no longer re-reads the file after harvesting."""
    calls = []
    real = sig.load_meta
    monkeypatch.setattr(sig, "load_meta", lambda p: calls.append(p) or real(p))
    rec = cm.meta_record(str(_meta(tmp_path / "once.meta.json")))
    assert len(calls) == 1
    assert rec["input_ids"] == frozenset({"t1.png", "t2.png", "t3.png"})
    assert rec["inputs"].endswith("/3")
    assert "dispatched_ids" not in rec


def test_the_gate_takes_its_harvester_from_this_library() -> None:
    """Finding 4: nothing under ``reports/`` is loaded by the gate."""
    assert cm.harvest is sig.harvest
    assert cm.signature is sig.signature
    assert not hasattr(cm, "HARVEST_SCRIPT")
    source = (REPO / "scripts" / "check_manipulation.py").read_text()
    assert "importlib" not in source


@pytest.mark.parametrize("name", ["g.meta.json.gz", "g.meta.json"])
def test_a_gzipped_meta_is_read_like_a_plain_one(tmp_path, name) -> None:
    """Finding 6: the passes manifest cites a ``.meta.json.gz``, and some
    archived metas are gzipped in place under their ``.json`` name. Both
    harvest exactly as the plain meta does, and the pass joins its arm."""
    plain = _meta(tmp_path / "plain.meta.json")
    gz = tmp_path / "gz" / name
    gz.parent.mkdir()
    gz.write_bytes(gzip.compress(plain.read_bytes()))
    drop = {"path", "bytes"}
    want = {k: v for k, v in sig.harvest(str(plain)).items() if k not in drop}
    got = sig.harvest(str(gz))
    assert "error" not in got
    assert {k: v for k, v in got.items() if k not in drop} == want
    arm = cm.arm_from_metas("A", [str(plain), str(gz)])
    assert arm["unreadable"] == []
    assert sorted(arm["meta_paths"]) == sorted([str(plain), str(gz)])


def test_a_truncated_gzip_meta_is_an_error_record(tmp_path) -> None:
    """A damaged gzip stream is recorded as unreadable, not raised."""
    bad = tmp_path / "bad.meta.json.gz"
    bad.write_bytes(gzip.compress(b'{"configuration": {}}')[:12])
    assert "error" in sig.harvest(str(bad))
