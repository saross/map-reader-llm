#!/usr/bin/env python3
"""
Probe whether an explicit context cache and the service tier combine.

Why this script exists
----------------------
From 2026-04-09 to 2026-10-03 the detection runner rebuilt the request
config for a cached call without ``service_tier``, so every
``--use-cache --service-tier flex`` run was billed at standard
(``planning/cost-accounting-fix-plan-2026-09-21.md`` § 8.3). The fix
(``scripts/4_detect_mounds_batch.cached_call_config``) copies the full
config. Before relying on it, this probe checks that the API accepts every
combination of the two levers, and records what each response reports about
the tier that served it (``usage_metadata.traffic_type`` and any tier header),
so the billed tier can be read per request from now on.

It makes ONE explicit cache and FOUR ``generate_content`` calls, one per
combination (flex or standard, with or without the cache), on
``gemini-3-flash-preview`` with minimal thinking: a few thousand tokens, under
US$0.01. The PI approved the API spend for testing the fix on 2026-10-03.

Usage::

    python3 scripts/probe_cache_tier.py --out outputs/tier-cache-probe-2026-10-03/direct.json

Created: 2026-10-03 (Session 158)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from google import genai  # noqa: E402
from google.genai import types  # noqa: E402

from config import GOOGLE_API_KEY  # noqa: E402

MODEL = "gemini-3-flash-preview"

#: A prefix long enough to be cached (the API sets a minimum token count).
PREFIX = ("You classify map symbols. A burial mound is drawn as a small circle with "
          "radiating hachures; a benchmark is a dot inside a triangle. ") * 120


def _runner():
    """The detection runner module, for its ``cached_call_config``."""
    spec = importlib.util.spec_from_file_location(
        "detect_mounds_batch", ROOT / "scripts" / "4_detect_mounds_batch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tier_headers(response) -> dict[str, str]:
    """Response headers that mention a tier or traffic class, if exposed."""
    http = getattr(response, "sdk_http_response", None)
    headers = dict(getattr(http, "headers", None) or {})
    return {k: v for k, v in headers.items()
            if any(w in k.lower() for w in ("tier", "traffic", "priority"))}


def main(argv: list[str] | None = None) -> int:
    """Run the four combinations and write what each response reports."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if not GOOGLE_API_KEY:
        raise SystemExit("probe_cache_tier: GOOGLE_API_KEY is not set")
    client = genai.Client(api_key=GOOGLE_API_KEY)
    runner = _runner()
    cache = client.caches.create(
        model=MODEL,
        config=types.CreateCachedContentConfig(
            system_instruction="Answer in one word.",
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=PREFIX)])],
            ttl="300s"))
    results = []
    try:
        for tier in ("flex", "standard"):
            for use_cache in (True, False):
                base = types.GenerateContentConfig(
                    temperature=0.0, max_output_tokens=64,
                    system_instruction="Answer in one word.",
                    thinking_config=types.ThinkingConfig(thinking_level="minimal"),
                    service_tier=tier)
                call = runner.cached_call_config(base, cache.name) if use_cache else base
                prompt = "Is a circle with radiating hachures a mound or a benchmark?"
                if not use_cache:
                    prompt = PREFIX + "\n" + prompt
                record = {"tier_requested": tier, "explicit_cache": use_cache,
                          "config_service_tier": str(call.service_tier),
                          "config_cached_content": bool(call.cached_content)}
                try:
                    resp = client.models.generate_content(model=MODEL, contents=prompt,
                                                          config=call)
                    um = resp.usage_metadata
                    record.update(
                        ok=True,
                        traffic_type=str(getattr(um, "traffic_type", None)),
                        prompt_tokens=um.prompt_token_count,
                        cached_tokens=um.cached_content_token_count,
                        output_tokens=um.candidates_token_count,
                        thinking_tokens=um.thoughts_token_count,
                        tier_headers=_tier_headers(resp),
                        model_version=resp.model_version)
                except Exception as exc:  # noqa: BLE001 - the error IS the finding
                    record.update(ok=False, error=f"{type(exc).__name__}: {exc}"[:500])
                results.append(record)
                print(json.dumps(record))
    finally:
        client.caches.delete(name=cache.name)
    doc = {"probe": "explicit cache x service tier", "model": MODEL,
           "run_at": datetime.now(timezone.utc).isoformat(),
           "cache_tokens": getattr(cache.usage_metadata, "total_token_count", None),
           "results": results}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"wrote {args.out}")
    return 0 if all(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
