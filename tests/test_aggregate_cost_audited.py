"""
Audited-pricing tests for ``aggregate_cost_manifest`` in
``scripts/run_generalisation.py`` (token-load audit, 2026-06-12).

The audit (``reports/token-load-audit-2026-06-12.md``) found three
defects in the legacy manifests: recovery-merged metas double-counted
``usage_stats``; every meta priced at standard rates regardless of the
run's actual service tier; and thinking tokens were never billed. The
``--pricing-tier`` audited path fixes all three. Tests cover:

1. Per-item union dedup — a recovery-merged meta whose ``usage_stats``
   are 2× inflated but whose ``per_item_metadata`` is clean yields the
   clean token sums and flex-priced cost (no double-count).
2. Thinking tokens billed at the output rate; the cached subset of
   input billed at the cache rate.
3. Stub-verifier reconstruction — a cleanup-overwrite stub meta with a
   ``probabilities.json`` proving the real call count reconstructs the
   verifier leg at the measured per-call rate and flags it.
4. The legacy (``recorded``) default is unchanged (covered by the
   pre-existing test files; re-asserted here on the pricing block).

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_generalisation import (  # noqa: E402
    _VERIFIER_RECON_USD_PER_CALL,
    build_arg_parser,
    cmd_aggregate_cost,
)


def _item(item_id: str, *, inp: int, out: int, think: int = 0,
          cached: int = 0) -> dict[str, Any]:
    """One per_item_metadata entry with the token fields the union reads."""
    return {
        "item_id": item_id,
        "tokens": {
            "input_tokens": inp,
            "output_tokens": out,
            "thoughts_tokens": think,
            "cached_input_tokens": cached,
            "total_tokens": inp + out + think,
        },
    }


def _meta(*, cost: float, usage: dict[str, int],
          per_item: list[dict[str, Any]] | None = None,
          items_processed: int = 0,
          model: str = "gemini-3-flash-preview") -> dict[str, Any]:
    """A minimal meta dict for the aggregator (audited-path fields)."""
    out: dict[str, Any] = {
        "run_id": "test",
        "configuration": {"model": model},
        "timestamp": {"duration_seconds": 1.0},
        "execution_stats": {
            "items_processed": items_processed,
            "items_failed": 0,
            "completed_items": [],
            "failed_items": [],
        },
        "usage_stats": usage,
        "cost_estimate": {
            "total_cost_usd": cost,
            "pricing_used": {"model": model},
        },
    }
    if per_item is not None:
        out["per_item_metadata"] = per_item
    return out


@pytest.fixture
def run_factory(tmp_path: Path, monkeypatch):
    """Seed a run dir + config; return (args-builder, output_dir)."""
    monkeypatch.setattr(
        "scripts.run_generalisation.git_status",
        lambda: {"commit_sha": "test", "branch": "main",
                 "dirty": False, "untracked_file_count": 0},
    )
    output_root = tmp_path / "outputs"
    output_dir = output_root / "audited-run"

    def _build(*, proposer_meta: dict[str, Any],
               verifier_meta: dict[str, Any],
               probabilities: dict[str, Any] | None = None,
               pricing_tier: str = "flex"):
        proposer_config = tmp_path / "proposer_config.json"
        proposer_config.write_text(json.dumps(
            {"include_example_images": False,
             "instruction_file": "detect_brief-text.md"}))
        for name, payload in [
            ("manifest.json", []), ("gt.geojson",
             {"type": "FeatureCollection", "features": []}),
            ("bounds.geojson",
             {"type": "FeatureCollection", "features": []}),
            ("verifier_config.json", {}),
        ]:
            (tmp_path / name).write_text(json.dumps(payload))
        (tmp_path / "tiles").mkdir(exist_ok=True)
        (tmp_path / "rasters").mkdir(exist_ok=True)
        config_path = tmp_path / "run_config.yaml"
        config_path.write_text(yaml.safe_dump({
            "run_name": "audited-run",
            "output_root": str(output_root),
            "proposer": {"config": str(proposer_config),
                         "manifest": str(tmp_path / "manifest.json"),
                         "tiles_dir": str(tmp_path / "tiles"),
                         "temperature": 0.7,
                         "thinking_level": "minimal", "passes": 1},
            "consensus": {"vote_threshold": 3},
            "extract": {"padding": 50,
                        "rasters_dir": str(tmp_path / "rasters")},
            "verify": {"config": str(tmp_path / "verifier_config.json")},
            "evaluate": {"prob_threshold": 0.5, "buffers": [20],
                         "ground_truth": str(tmp_path / "gt.geojson"),
                         "bounds": str(tmp_path / "bounds.geojson")},
        }))
        run_dir = output_dir / "proposer" / "proposer_config" / "run_1"
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "detections.meta.json").write_text(
            json.dumps(proposer_meta))
        verified = output_dir / "verified"
        verified.mkdir(parents=True, exist_ok=True)
        (verified / "run.meta.json").write_text(json.dumps(verifier_meta))
        if probabilities is not None:
            (verified / "probabilities.json").write_text(
                json.dumps(probabilities))
        crops = output_dir / "crops"
        crops.mkdir(exist_ok=True)
        (crops / "candidate_manifest.json").write_text(
            json.dumps({"candidates": []}))
        parser = build_arg_parser()
        return parser.parse_args([
            "aggregate-cost", "--run-config", str(config_path),
            "--pricing-tier", pricing_tier, "--yes",
        ])

    return _build, output_dir


@pytest.mark.tier1
def test_per_item_union_beats_inflated_usage_stats(run_factory) -> None:
    """Audited tokens come from the per-item union, not the (2×-merged)
    usage_stats — the text-min/text-high double-count scenario."""
    build, output_dir = run_factory
    # Two items, 1,000 in / 100 out each; usage_stats record DOUBLE.
    proposer = _meta(
        cost=99.0,  # recorded cost is wrong on purpose; must be ignored
        usage={"total_input_tokens": 4000, "total_output_tokens": 400,
               "total_cached_tokens": 0, "total_thoughts_tokens": 0,
               "total_tokens": 4400},
        per_item=[_item("a.png", inp=1000, out=100),
                  _item("b.png", inp=1000, out=100)],
        items_processed=4,  # also inflated
    )
    verifier = _meta(cost=0.0, usage={
        "total_input_tokens": 0, "total_output_tokens": 0,
        "total_cached_tokens": 0, "total_thoughts_tokens": 0,
        "total_tokens": 0})
    args = build(proposer_meta=proposer, verifier_meta=verifier)
    assert cmd_aggregate_cost(args) == 0

    data = json.loads((output_dir / "cost_manifest.json").read_text())
    prop = data["by_stage"]["proposer"]
    assert prop["tokens"]["input_tokens"] == 2000, "union must dedup"
    assert prop["tiles_processed"] == 2
    # flex: 2000 in x $0.25/M + 200 out x $1.50/M
    expected = 2000 * 0.25 / 1e6 + 200 * 1.50 / 1e6
    assert abs(prop["cost_usd"] - expected) < 1e-9
    assert data["_metadata"]["pricing"]["pricing_tier"] == "flex"
    assert data["_metadata"]["pricing"]["thinking_billed_as_output"] is True


@pytest.mark.tier1
def test_thinking_billed_and_cache_rate_applied(run_factory) -> None:
    """Thinking tokens bill at the output rate; cached input at $0.05/M."""
    build, output_dir = run_factory
    proposer = _meta(
        cost=0.0,
        usage={"total_input_tokens": 0, "total_output_tokens": 0,
               "total_cached_tokens": 0, "total_thoughts_tokens": 0,
               "total_tokens": 0},
        per_item=[_item("a.png", inp=1_000_000, out=100_000,
                        think=2_000_000, cached=400_000)],
    )
    verifier = _meta(cost=0.0, usage={
        "total_input_tokens": 0, "total_output_tokens": 0,
        "total_cached_tokens": 0, "total_thoughts_tokens": 0,
        "total_tokens": 0})
    args = build(proposer_meta=proposer, verifier_meta=verifier)
    assert cmd_aggregate_cost(args) == 0

    data = json.loads((output_dir / "cost_manifest.json").read_text())
    # flex: (1M - 0.4M) x 0.25 + 0.4M x 0.05 (cache)
    #       + (0.1M out + 2M thinking) x 1.50
    expected = (0.6 * 0.25) + (0.4 * 0.05) + (2.1 * 1.50)
    assert abs(data["by_stage"]["proposer"]["cost_usd"] - expected) < 1e-6


@pytest.mark.tier1
def test_stub_verifier_reconstructed_from_probabilities(run_factory) -> None:
    """A cleanup-overwrite stub verifier meta is reconstructed from the
    probabilities.json call count at the measured per-call rate."""
    build, output_dir = run_factory
    proposer = _meta(
        cost=0.0,
        usage={"total_input_tokens": 0, "total_output_tokens": 0,
               "total_cached_tokens": 0, "total_thoughts_tokens": 0,
               "total_tokens": 0},
        per_item=[_item("a.png", inp=100, out=10)],
    )
    stub = _meta(
        cost=0.05,
        usage={"total_input_tokens": 5000, "total_output_tokens": 500,
               "total_cached_tokens": 0, "total_thoughts_tokens": 0,
               "total_tokens": 5500},
        items_processed=4,
    )
    probabilities = {"results": {
        f"candidate_{i:05d}": {"probability": 0.5} for i in range(100)
    }}
    args = build(proposer_meta=proposer, verifier_meta=stub,
                 probabilities=probabilities)
    assert cmd_aggregate_cost(args) == 0

    data = json.loads((output_dir / "cost_manifest.json").read_text())
    verifier = data["by_stage"]["verifier"]
    expected = 100 * _VERIFIER_RECON_USD_PER_CALL["flex"]
    assert abs(verifier["cost_usd"] - expected) < 1e-9
    assert verifier["reconstructed"] is True
    assert verifier["candidates_processed"] == 100
    assert verifier["reconstruction"]["n_calls"] == 100


@pytest.mark.tier1
def test_recorded_tier_keeps_legacy_pricing_block(run_factory) -> None:
    """``--pricing-tier recorded`` keeps meta-recorded costs and writes
    the legacy-warning pricing block."""
    build, output_dir = run_factory
    proposer = _meta(
        cost=7.5,
        usage={"total_input_tokens": 1000, "total_output_tokens": 100,
               "total_cached_tokens": 0, "total_thoughts_tokens": 0,
               "total_tokens": 1100},
        per_item=[_item("a.png", inp=1000, out=100)],
    )
    verifier = _meta(cost=2.5, usage={
        "total_input_tokens": 0, "total_output_tokens": 0,
        "total_cached_tokens": 0, "total_thoughts_tokens": 0,
        "total_tokens": 0})
    args = build(proposer_meta=proposer, verifier_meta=verifier,
                 pricing_tier="recorded")
    assert cmd_aggregate_cost(args) == 0

    data = json.loads((output_dir / "cost_manifest.json").read_text())
    assert data["by_stage"]["proposer"]["cost_usd"] == 7.5
    assert data["by_stage"]["verifier"]["cost_usd"] == 2.5
    assert data["_metadata"]["pricing"]["pricing_tier"] == "recorded"
