"""
Tier-1 tests: every writer of a ``cost_estimate`` block prices through the
one cost function at the tier the leg ran at, and records that tier.

The defects these pin were found by the cost accounting investigation of
2026-09-21 (``planning/cost-accounting-fix-plan-2026-09-21.md`` § 1.3): the
verifier path passed no tier and recorded list price for flex and Batch API
legs; the realtime proposer applied the flex discount unconditionally; the
batch chunk merge summed chunk dollars into a block whose other fields were
chunk 0's; recovery merges added dollars and dropped the basis.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import lib_cost as lc
from scripts.lib_llm_metadata import AggregatedUsage, merge_cost_blocks, merge_meta

pytestmark = pytest.mark.tier1


def _usage(**kw) -> AggregatedUsage:
    u = AggregatedUsage()
    for k, v in kw.items():
        setattr(u, k, v)
    return u


# --- The verifier writer -----------------------------------------------------

def _write_verifier(tmp_path: Path, *, mode: str, service_tier: str | None,
                    model: str = "gemini-3.7-flash") -> dict:
    """Drive run_pv's output writer with a one-candidate result at a tier."""
    from scripts import run_pv
    from scripts.lib_llm_metadata import LLMMetadataTracker

    tracker = LLMMetadataTracker(
        config={"model": model, "version": "test", "temperature": 0.0},
        system_instruction="x", script_name="test", script_version="0",
        model_override=model)
    tracker.usage = _usage(total_input_tokens=1_000_000, total_output_tokens=100_000,
                           total_tokens=1_100_000)
    stage = tmp_path / mode
    stage.mkdir()
    run_pv._write_verification_outputs(
        parsed_results={"0": {"candidate_id": 0, "probability": 0.9, "iterations": 1,
                              "votes": 1, "raw_probabilities": [0.9]}},
        manifest={"candidates": [{"candidate_id": 0}]},
        config={"model": model, "version": "test"},
        output_dir=stage, iterations=1, mode=mode, metadata_tracker=tracker,
        model_name=model, strict=False, service_tier=service_tier,
    )
    return json.loads((stage / "run.meta.json").read_text())


def test_a_batch_verifier_leg_is_priced_and_recorded_at_the_batch_tier(tmp_path) -> None:
    meta = _write_verifier(tmp_path, mode="batch", service_tier=None)
    pu = meta["cost_estimate"]["pricing_used"]
    assert meta["billing"]["service_tier"] == "batch" and pu["tier"] == "batch"
    assert meta["cost_estimate"]["total_cost_usd"] == pytest.approx(0.375 + 0.1875)
    assert meta["cost_estimate"]["schema"] == "cost/2"


def test_a_flex_verifier_leg_is_priced_at_flex_and_a_bare_one_at_standard(tmp_path) -> None:
    flex = _write_verifier(tmp_path, mode="realtime", service_tier="flex")
    (tmp_path / "b").mkdir()
    bare = _write_verifier(tmp_path / "b", mode="realtime", service_tier=None)
    assert flex["billing"] == {"service_tier": "flex", "tier_source": "cli --service-tier"}
    assert flex["cost_estimate"]["total_cost_usd"] == pytest.approx(0.375 + 0.1875)
    assert bare["billing"]["service_tier"] == "standard"
    assert bare["cost_estimate"]["total_cost_usd"] == pytest.approx(0.75 + 0.375)
    # The old defect: list price recorded for a flex leg, exactly double.
    assert bare["cost_estimate"]["total_cost_usd"] == pytest.approx(
        2 * flex["cost_estimate"]["total_cost_usd"])


# --- Merges re-price, never add ---------------------------------------------

def _block(usage: dict, **kw) -> dict:
    return lc.price_usage(usage, kw.get("model", "gemini-3.7-flash"), kw.get("tier", "flex"),
                          at="2026-09-20", tier_source="test")


def test_two_audited_blocks_on_one_terms_are_repriced_from_summed_tokens() -> None:
    a = {"total_input_tokens": 1_000_000, "total_cached_tokens": 900_000,
         "total_output_tokens": 0, "total_thoughts_tokens": 0}
    b = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
         "total_output_tokens": 0, "total_thoughts_tokens": 0}
    merged_usage = {k: a[k] + b[k] for k in a}
    merged = merge_cost_blocks(_block(a), _block(b), merged_usage)
    assert merged["cost_basis"] == "audited"
    assert merged["tokens_billed"]["input_cached"] == 900_000
    assert merged["total_cost_usd"] == pytest.approx(
        0.1 * 0.375 + 0.9 * 0.0375 + 1.0 * 0.375)
    assert merged["input_cost_usd"] + merged["cached_input_cost_usd"] + \
        merged["output_cost_usd"] == pytest.approx(merged["total_cost_usd"], abs=2e-6)


def test_two_audited_blocks_on_different_terms_are_summed_and_say_so() -> None:
    u = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
         "total_output_tokens": 0, "total_thoughts_tokens": 0}
    merged = merge_cost_blocks(_block(u, model="gemini-3.7-flash"),
                               _block(u, model="gemini-3-flash-preview"),
                               {k: 2 * v for k, v in u.items()})
    assert merged["cost_basis"] == "audited-summed"
    assert merged["total_cost_usd"] == pytest.approx(0.375 + 0.25)
    assert [s["model"] for s in merged["summed_from"]] == [
        "gemini-3.7-flash", "gemini-3-flash-preview"]


def test_a_legacy_block_keeps_the_additive_path_and_is_labelled() -> None:
    legacy = {"input_cost_usd": 1.0, "output_cost_usd": 2.0, "total_cost_usd": 3.0,
              "pricing_used": {"model": "gemini-3.7-flash"}}
    merged = merge_cost_blocks(legacy, dict(legacy), {"total_input_tokens": 0})
    assert merged["total_cost_usd"] == pytest.approx(6.0)
    assert merged["cost_basis"] == "summed-legacy"
    assert "schema" not in merged


def test_merge_meta_reprices_a_recovery_on_the_same_terms() -> None:
    def meta(cached: int) -> dict:
        usage = {"total_input_tokens": 1_000_000, "total_cached_tokens": cached,
                 "total_output_tokens": 0, "total_thoughts_tokens": 0, "total_tokens": 1_000_000}
        return {"run_id": "x", "usage_stats": usage, "cost_estimate": _block(usage),
                "execution_stats": {"items_processed": 1, "completed_items": ["a"]},
                "timestamp": {"duration_seconds": 1.0}}
    merged = merge_meta(meta(1_000_000), meta(0))
    assert merged["cost_estimate"]["cost_basis"] == "audited"
    assert merged["cost_estimate"]["total_cost_usd"] == pytest.approx(0.0375 + 0.375)


# --- The batch chunk merge ---------------------------------------------------

def test_chunk_merge_reprices_summed_tokens_and_keeps_the_block_consistent(tmp_path) -> None:
    from scripts.lib_batch_api import merge_chunk_metadata

    def chunk(i: int, cached: int) -> Path:
        usage = {"total_input_tokens": 1_000_000, "total_cached_tokens": cached,
                 "total_output_tokens": 10_000, "total_thoughts_tokens": 0,
                 "total_tokens": 1_010_000}
        meta = {"run_id": f"c{i}", "configuration": {"model": "gemini-3.7-flash"},
                "usage_stats": usage,
                "cost_estimate": lc.price_usage(usage, "gemini-3.7-flash", "batch",
                                                at="2026-09-17", tier_source="test"),
                "execution_stats": {"items_processed": 5, "items_failed": 0},
                "results_summary": {"total_detections": 1, "total_tiles": 5},
                "batch_api": {"execution_mode": "batch"}}
        p = tmp_path / f"detections.chunk{i}.meta.json"
        p.write_text(json.dumps(meta))
        (tmp_path / f"detections.chunk{i}.tiles.json").write_text(
            json.dumps({"tiles": [f"t{i}-{j}" for j in range(5)], "total_tiles": 5}))
        return p
    paths = [chunk(0, 0), chunk(1, 1_000_000), chunk(2, 1_000_000)]
    tiles = [tmp_path / f"detections.chunk{i}.tiles.json" for i in range(3)]
    merged = merge_chunk_metadata(paths, tiles, tmp_path / "detections.meta.json",
                                  tmp_path / "detections.tiles.json")
    ce = merged["cost_estimate"]
    assert ce["cost_basis"] == "audited"
    assert ce["tokens_billed"]["input_cached"] == 2_000_000
    assert ce["input_cost_usd"] + ce["cached_input_cost_usd"] + ce["output_cost_usd"] == \
        pytest.approx(ce["total_cost_usd"], abs=2e-6)
    assert ce["total_cost_usd"] == pytest.approx(
        1.0 * 0.375 + 2.0 * 0.0375 + 0.03 * 1.875)
