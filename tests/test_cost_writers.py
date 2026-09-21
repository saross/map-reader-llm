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
from datetime import datetime, timezone
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

class _FrozenDatetime(datetime):
    """A datetime whose ``now`` is 2026-09-20: writers price at the pass's end
    time, and a test that read the wall clock would cross the 2027-01-01 step."""

    @classmethod
    def now(cls, tz=None):  # noqa: D102
        return datetime(2026, 9, 20, 12, 0, tzinfo=tz or timezone.utc)


@pytest.fixture(autouse=True)
def _frozen_clock(monkeypatch):
    from scripts import lib_llm_metadata
    monkeypatch.setattr(lib_llm_metadata, "datetime", _FrozenDatetime)


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


# --- The batch proposer writer, end to end ---------------------------------

def _batch_write(tmp_path: Path, usage_stats: dict | None) -> tuple[dict, dict]:
    from scripts.lib_batch_api import write_batch_outputs

    config = {"version": "detect_test", "model": "gemini-3.7-flash",
              "instruction_file": "detect_image-only.md", "temperature": 1.0,
              "thinking_level": "low", "max_output_tokens": 8192}
    out = tmp_path / "detections.geojson"
    block = write_batch_outputs(features=[], processed_tiles=set(), failed_tiles=[],
                                output_file=out, config=config, model_name="gemini-3.7-flash",
                                system_instruction="Test", total_detections=0,
                                usage_stats=usage_stats)
    meta = json.loads(out.with_suffix(".meta.json").read_text())
    return block, meta


def test_the_batch_proposer_writer_prices_at_the_batch_tier_and_says_so(tmp_path) -> None:
    block, meta = _batch_write(tmp_path, {
        "total_input_tokens": 1_000_000, "total_cached_tokens": 800_000,
        "total_output_tokens": 100_000, "total_thoughts_tokens": 0,
        "total_tokens": 1_100_000, "n_responses_with_usage": 5})
    assert block["pricing_used"]["tier"] == "batch"
    assert block["total_cost_usd"] == pytest.approx(0.2 * 0.375 + 0.8 * 0.0375 + 0.1 * 1.875)
    assert block["pricing_used"]["batch_discount"] == 0.5  # legacy key kept for readers
    assert meta["billing"]["service_tier"] == "batch"
    assert meta["cost_estimate"]["pricing_used"]["priced_at"] == "2026-09-20"


def test_a_batch_pass_with_no_reported_usage_is_unrecorded_not_zero(tmp_path) -> None:
    block, meta = _batch_write(tmp_path, {"total_input_tokens": 0, "total_output_tokens": 0,
                                          "total_tokens": 0, "n_responses_with_usage": 0})
    assert block["cost_basis"] == "unrecorded" and block["total_cost_usd"] is None
    assert lc.fmt_usd(block["total_cost_usd"]) == "unrecorded"
    assert lc.fmt_usd(1.23456) == "$1.2346"


# --- The tier helper the writers share ---------------------------------------

def test_tier_from_cli_is_the_one_rule_for_every_writer() -> None:
    assert lc.tier_from_cli(None) == ("standard", "no --service-tier given: standard tier")
    assert lc.tier_from_cli("flex") == ("flex", "cli --service-tier")
    assert lc.tier_from_cli("flex", batch=True) == ("batch", "Batch API path")
    with pytest.raises(lc.RateCardError):
        lc.tier_from_cli("priority")
    # The two writers no test can drive end to end (they call the live API)
    # must use the helper and the non-raising path; pinned at the source.
    for script in ("scripts/4_detect_mounds_batch.py", "scripts/5_verify_crops.py"):
        src = (Path(__file__).resolve().parent.parent / script).read_text()
        assert "tier_from_cli(" in src and "strict=False" in src, script
        assert 'meta["billing"]' in src, script


# --- Merge cases the audit of 2026-09-21 found ------------------------------

def test_a_stub_or_empty_block_contributes_nothing_to_a_merge() -> None:
    u = {"total_input_tokens": 1_000_000, "total_cached_tokens": 800_000,
         "total_output_tokens": 0, "total_thoughts_tokens": 0}
    audited = lc.price_usage(u, "gemini-3.7-flash", "flex", at="2026-09-20")
    for stub in ({}, None, {"input_cost_usd": 0.0, "output_cost_usd": 0.0, "total_cost_usd": 0.0}):
        merged = lc.merge_cost_blocks([audited, stub], u)
        assert merged["cost_basis"] == "audited"
        assert merged["cached_input_cost_usd"] == audited["cached_input_cost_usd"]
    assert lc.merge_cost_blocks([{}, None], u)["cost_basis"] == "unrecorded"


def test_a_legacy_chunk_among_audited_chunks_is_not_double_counted() -> None:
    """Folding whole-pass totals into a legacy sum inflated the result by the
    number of preceding chunks; the merge now sums each block's own dollars."""
    u = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
         "total_output_tokens": 0, "total_thoughts_tokens": 0}
    a = lc.price_usage(u, "gemini-3.7-flash", "batch", at="2026-09-17")
    legacy = {"input_cost_usd": 0.375, "output_cost_usd": 0.0, "total_cost_usd": 0.375}
    merged = lc.merge_cost_blocks([a, a, legacy], {k: 3 * v for k, v in u.items()})
    assert merged["cost_basis"] == "summed-legacy"
    assert merged["total_cost_usd"] == pytest.approx(3 * 0.375)


def test_passes_on_different_card_rows_are_summed_not_repriced_at_one_row() -> None:
    """A cleanup across the 2027-01-01 step must not be priced at the 2026 row."""
    u = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
         "total_output_tokens": 0, "total_thoughts_tokens": 0}
    before = lc.price_usage(u, "gemini-3.7-flash", "flex", at="2026-12-30")
    after = lc.price_usage(u, "gemini-3.7-flash", "flex", at="2027-01-02")
    merged = lc.merge_cost_blocks([before, after], {k: 2 * v for k, v in u.items()})
    assert merged["cost_basis"] == "audited-summed"
    assert merged["total_cost_usd"] == pytest.approx(0.375 + 0.75)
    assert [s["row_valid_from"] for s in merged["summed_from"]] == ["2026-08-01", "2027-01-01"]
    assert merged["pricing_used"]["model"] is None


def test_the_chunk_merge_prices_the_pass_once_from_summed_tokens(tmp_path) -> None:
    """The fold that inflated a mixed pass is gone: every chunk's block goes in
    together, and the pass is priced once."""
    from scripts.lib_batch_api import merge_chunk_metadata

    def chunk(i: int, block: dict) -> Path:
        usage = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
                 "total_output_tokens": 0, "total_thoughts_tokens": 0, "total_tokens": 1_000_000}
        meta = {"run_id": f"c{i}", "configuration": {"model": "gemini-3.7-flash"},
                "usage_stats": usage, "cost_estimate": block,
                "execution_stats": {"items_processed": 5, "items_failed": 0},
                "results_summary": {"total_detections": 0, "total_tiles": 5}}
        (tmp_path / f"d.chunk{i}.meta.json").write_text(json.dumps(meta))
        (tmp_path / f"d.chunk{i}.tiles.json").write_text(
            json.dumps({"tiles": [f"t{i}{j}" for j in range(5)], "total_tiles": 5}))
        return tmp_path / f"d.chunk{i}.meta.json"
    u = {"total_input_tokens": 1_000_000, "total_cached_tokens": 0,
         "total_output_tokens": 0, "total_thoughts_tokens": 0}
    audited = lc.price_usage(u, "gemini-3.7-flash", "batch", at="2026-09-17")
    legacy = {"input_cost_usd": 0.375, "output_cost_usd": 0.0, "total_cost_usd": 0.375}
    paths = [chunk(0, audited), chunk(1, audited), chunk(2, legacy)]
    tiles = [tmp_path / f"d.chunk{i}.tiles.json" for i in range(3)]
    merged = merge_chunk_metadata(paths, tiles, tmp_path / "d.meta.json", tmp_path / "d.tiles.json")
    assert merged["cost_estimate"]["total_cost_usd"] == pytest.approx(3 * 0.375)
    assert merged["cost_estimate"]["cost_basis"] == "summed-legacy"


# --- The wrapper's guards ----------------------------------------------------

def test_a_model_the_card_lacks_is_recorded_unpriceable_by_a_writer_and_refused_by_an_auditor() -> None:
    from scripts.lib_llm_metadata import estimate_cost
    u = _usage(total_input_tokens=1_000_000, total_tokens=1_000_000)
    with pytest.raises(lc.UnknownModelError):
        estimate_cost(u, "google_gemini", "gemini-9-flash", tier="flex", at="2026-09-20")
    block = estimate_cost(u, "google_gemini", "gemini-9-flash", tier="flex",
                          at="2026-09-20", strict=False)
    assert block["cost_basis"] == "unpriceable" and block["total_cost_usd"] is None
    assert block["tokens_billed"]["input_fresh"] == 1_000_000
    assert "gemini-9-flash" in block["reason"]
    assert block["pricing_used"]["tier"] == "flex"


def test_a_non_gemini_provider_is_refused() -> None:
    from scripts.lib_llm_metadata import estimate_cost
    with pytest.raises(lc.RateCardError, match="Gemini only"):
        estimate_cost(_usage(), "openai", "gpt-5", tier="standard")


def test_the_list_price_includes_the_cached_class_at_standard() -> None:
    u = {"total_input_tokens": 1_000_000, "total_cached_tokens": 1_000_000,
         "total_output_tokens": 0, "total_thoughts_tokens": 0}
    b = lc.price_usage(u, "gemini-3.7-flash", "flex", at="2026-09-20")
    assert b["list_input_cost_usd"] == pytest.approx(0.075)
    assert b["list_total_cost_usd"] == pytest.approx(0.075)
    assert b["pricing_used"]["discount"] == pytest.approx(0.0375 / 0.075)


def test_the_discount_is_the_billed_over_list_ratio_not_the_input_headline() -> None:
    """Gemini 3 halves input and output on flex but not the cache read."""
    u = {"total_input_tokens": 1_000_000, "total_cached_tokens": 800_000,
         "total_output_tokens": 0, "total_thoughts_tokens": 0}
    b = lc.price_usage(u, "gemini-3-flash-preview", "flex", at="2026-09-20")
    assert b["total_cost_usd"] == pytest.approx(b["list_total_cost_usd"] * b["pricing_used"]["discount"])
    assert b["pricing_used"]["discount"] > 0.5


def test_a_card_edited_in_place_is_re_read_with_its_new_hash(tmp_path) -> None:
    import time
    card = json.loads(lc.DEFAULT_RATE_CARD.read_text())
    p = tmp_path / "card.json"
    p.write_text(json.dumps(card))
    first = lc.rate_card_identity(p)
    card["version"] = "edited"
    time.sleep(0.01)
    p.write_text(json.dumps(card))
    second = lc.rate_card_identity(p)
    assert second["version"] == "edited" and second["sha256"] != first["sha256"]
    assert second["path"] == "external:card.json"
