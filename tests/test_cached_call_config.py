"""Tier-1 tests: the detection runner's explicit-cache request keeps every lever.

From 2026-04-09 to 2026-10-03 the cached request config was rebuilt field by
field without ``service_tier``, so every ``--use-cache --service-tier flex`` run
was billed at standard (``planning/cost-accounting-fix-plan-2026-09-21.md``
§ 8.3). The cache and the tier are independent levers; these tests pin that a
cached call carries the run's tier, and every other field, unchanged.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from google.genai import types

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def runner():
    spec = importlib.util.spec_from_file_location(
        "detect_mounds_batch", ROOT / "scripts" / "4_detect_mounds_batch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _config(tier: str | None) -> types.GenerateContentConfig:
    kwargs = dict(temperature=0.3, max_output_tokens=4096,
                  response_mime_type="application/json", system_instruction="find mounds",
                  thinking_config=types.ThinkingConfig(thinking_level="high"),
                  safety_settings=[types.SafetySetting(category="HARM_CATEGORY_HARASSMENT",
                                                       threshold="OFF")])
    if tier:
        kwargs["service_tier"] = tier
    return types.GenerateContentConfig(**kwargs)


@pytest.mark.tier1
@pytest.mark.parametrize("tier", ["flex", "standard", None])
def test_a_cached_call_keeps_the_run_tier(runner, tier):
    # SENTINEL for the defect: the tier must survive the cache.
    call = runner.cached_call_config(_config(tier), "cachedContents/abc")
    assert call.service_tier == _config(tier).service_tier
    assert call.cached_content == "cachedContents/abc"


@pytest.mark.tier1
def test_a_cached_call_changes_nothing_but_the_cache(runner):
    base = _config("flex")
    call = runner.cached_call_config(base, "cachedContents/abc")
    assert call.system_instruction is None  # it lives in the cache
    before = base.model_dump(exclude={"cached_content", "system_instruction"})
    after = call.model_dump(exclude={"cached_content", "system_instruction"})
    assert before == after
    assert base.cached_content is None and base.system_instruction == "find mounds"


@pytest.mark.tier1
def test_the_runner_builds_cached_calls_through_the_helper():
    # Wiring: the generate_content call site must use the helper, not a
    # hand-built config that could drop a lever again.
    src = (ROOT / "scripts" / "4_detect_mounds_batch.py").read_text()
    assert "cached_call_config(gen_config, cache_name)" in src
    assert "types.GenerateContentConfig(\n                        cached_content" not in src
