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


@pytest.mark.tier1
def test_a_cached_call_keeps_every_field_the_sdk_defines(runner):
    # Broad: set ten more fields beside the base ones, so a future
    # field-by-field rebuild that misses any of them turns this red (the
    # defect dropped exactly one: service_tier).
    base = _config("flex").model_copy(update={
        "top_p": 0.9, "top_k": 20, "candidate_count": 1, "seed": 7,
        "stop_sequences": ["END"], "presence_penalty": 0.1, "frequency_penalty": 0.2,
        "response_logprobs": False, "media_resolution": types.MediaResolution.MEDIA_RESOLUTION_HIGH,
        "labels": {"run": "x"}})
    call = runner.cached_call_config(base, "cachedContents/abc")
    dumped = call.model_dump(exclude_none=True)
    for key, value in base.model_dump(exclude_none=True).items():
        if key == "system_instruction":
            continue
        assert dumped.get(key) == value, key


@pytest.mark.tier1
@pytest.mark.parametrize("lever", ["tools", "tool_config"])
def test_tools_beside_a_cache_are_refused_not_dropped(runner, lever):
    value = ([types.Tool(google_search=types.GoogleSearch())] if lever == "tools"
             else types.ToolConfig(function_calling_config=types.FunctionCallingConfig(
                 mode="NONE")))
    with pytest.raises(ValueError, match="tools and tool_config"):
        runner.cached_call_config(_config("flex").model_copy(update={lever: value}),
                                  "cachedContents/abc")


@pytest.mark.tier1
def test_the_cached_config_is_the_one_sent():
    # Wiring: the config built for the call is the one passed to
    # generate_content (a later edit that sends gen_config would reopen the
    # defect with every helper test green), and the helper is preflighted
    # before the cache is created, outside the try whose fallback hides errors.
    import ast
    src = (ROOT / "scripts" / "4_detect_mounds_batch.py").read_text()
    calls = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "generate_content"]
    assert calls, "no generate_content call found"
    for call in calls:
        config = next(k.value for k in call.keywords if k.arg == "config")
        assert isinstance(config, ast.Name) and config.id == "call_config"
    pre = src.index('cached_call_config(gen_config, "cachedContents/preflight")')
    assert pre < src.index("client.caches.create(")
    assert src.rfind("try:", 0, src.index("client.caches.create(")) > pre
    # And no try of any kind encloses the preflight, or a handler could
    # swallow its refusal and run on without the lever.
    tree = ast.parse(src)
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    preflights = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                  and getattr(n.func, "id", None) == "cached_call_config"
                  and any(isinstance(a, ast.Constant) and a.value == "cachedContents/preflight"
                          for a in n.args)]
    assert len(preflights) == 1
    node = preflights[0]
    while node in parents:
        node = parents[node]
        # A try, an except* group, or a with block (contextlib.suppress) could
        # each swallow the refusal.
        assert not isinstance(node, (ast.Try, ast.TryStar, ast.With)), (
            f"the preflight sits inside a {type(node).__name__}")
