"""Audit fixes of 2026-09-19 (lens A and B): the pass-file rule everywhere,
safe usage summing, and the resume branch of the chunked proposer.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.audit_proposer_cost import read_fragments  # noqa: E402
from scripts.lib_batch_api import locate_pass_files  # noqa: E402
from scripts.lib_llm_metadata import _sum_dicts  # noqa: E402

pytestmark = pytest.mark.tier1

STEM = "detections_detect_brief-text-image_run01"


def _chunked_unit(d: Path, merged: bool, n_chunks: int = 3) -> None:
    d.mkdir(parents=True, exist_ok=True)
    for i in range(n_chunks):
        (d / f"{STEM}_chunk{i}.geojson").write_text('{"type":"FeatureCollection","features":[]}')
        (d / f"{STEM}_chunk{i}.tiles.json").write_text('{"total_tiles":10,"completed":[],"failed":["f.png"]}')
        (d / f"{STEM}_chunk{i}.meta.json").write_text(json.dumps({
            "usage_stats": {"total_input_tokens": 100, "total_cached_tokens": 0},
            "execution_stats": {"items_processed": 10}, "cost_estimate": {"total_cost_usd": 1.0}}))
    if merged:
        (d / f"{STEM}.geojson").write_text('{"type":"FeatureCollection","features":[]}')
        (d / f"{STEM}.tiles.json").write_text('{"total_tiles":30,"completed":[],"failed":[]}')
        (d / f"{STEM}.meta.json").write_text(json.dumps({
            "usage_stats": {"total_input_tokens": 300, "total_cached_tokens": 0},
            "execution_stats": {"items_processed": 30}, "cost_estimate": {"total_cost_usd": 3.0}}))


# --- locate_pass_files (patch_failed_tiles) ---------------------------------

def test_patch_tiles_locates_the_merged_pass_not_a_chunk(tmp_path):
    _chunked_unit(tmp_path, merged=True)
    gj, tiles, meta = locate_pass_files(tmp_path)
    assert (gj.name, tiles.name, meta.name) == (f"{STEM}.geojson", f"{STEM}.tiles.json", f"{STEM}.meta.json")


def test_patch_tiles_refuses_a_chunk_only_unit(tmp_path):
    _chunked_unit(tmp_path, merged=False)
    assert locate_pass_files(tmp_path) is None


def test_patch_tiles_refuses_an_incomplete_unit(tmp_path):
    (tmp_path / f"{STEM}.geojson").write_text("{}")
    assert locate_pass_files(tmp_path) is None


# --- read_fragments (audit_proposer_cost) -----------------------------------

def test_cost_auditor_prices_a_chunked_pass_from_its_merged_meta(tmp_path):
    _chunked_unit(tmp_path / "run_1", merged=True)
    frags = read_fragments(str(tmp_path))
    assert len(frags) == 1
    assert frags[0]["items"] == 30 and frags[0]["input_tokens"] == 300
    assert frags[0]["meta"].endswith(f"{STEM}.meta.json")


def test_cost_auditor_refuses_an_unmerged_chunked_pass(tmp_path):
    """Pricing chunk 0 as the pass at a budget gate reported one seventh of
    a run with no sign anything was wrong (lens B ran it on a real staging
    directory: US$10.21 for a 24,561-tile pass)."""
    _chunked_unit(tmp_path / "run_1", merged=False)
    with pytest.raises(FileNotFoundError, match="not been merged"):
        read_fragments(str(tmp_path))


# --- _sum_dicts -------------------------------------------------------------

def test_sum_dicts_sums_counts_and_keeps_strings():
    a = {"total_input_tokens": 100, "usage_source": "batch results file"}
    b = {"total_input_tokens": 50, "usage_source": "batch results file",
         "total_output_tokens": 7}
    out = _sum_dicts(a, b)
    assert out["total_input_tokens"] == 150
    assert out["total_output_tokens"] == 7
    assert out["usage_source"] == "batch results file"


def test_sum_dicts_survives_a_pre_s154_meta_without_the_string_field():
    """int + str crashed the meta write at the end of a paid batch unit."""
    out = _sum_dicts({"total_input_tokens": 100}, {"usage_source": "x", "total_input_tokens": 1})
    assert out == {"total_input_tokens": 101, "usage_source": "x"}


def test_sum_dicts_clears_ratios_instead_of_adding_them():
    """A cached_share of 1.58 was written into a cost artefact."""
    out = _sum_dicts({"cached_share": 0.79, "total_cost_usd": 1.5},
                     {"cached_share": 0.79, "total_cost_usd": 2.0})
    assert out["cached_share"] is None
    assert out["total_cost_usd"] == 3.5


def test_sum_dicts_nested_and_none_values():
    out = _sum_dicts({"by_provider": {"gemini": {"n": 1}}, "x": None},
                     {"by_provider": {"gemini": {"n": 2}}, "x": 3})
    assert out["by_provider"]["gemini"]["n"] == 3
    assert out["x"] == 3


# --- resume branch of the chunked proposer ---------------------------------

def test_resume_branch_treats_a_geojson_without_sidecar_as_failed():
    src = (ROOT / "scripts" / "4_detect_mounds_batch.py").read_text()
    i = src.index("SKIPPING (output exists")
    block = src[i:i + 1500]
    assert "tally_chunk(run_dir, suffix, chunk_limit, True)" in block
    assert "chunk_failed = True" in block
    assert "total_failed += chunk_limit" in block


def test_tally_module_still_importable():
    spec = importlib.util.spec_from_file_location(
        "detect_mounds_batch", ROOT / "scripts" / "4_detect_mounds_batch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.tally_chunk)
