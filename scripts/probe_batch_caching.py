#!/usr/bin/env python3
"""Probe whether the Batch API serves a model, reports usage, and caches.

Three questions must be answered BEFORE a bulk batch leg, because each one
independently decides whether the leg is affordable or auditable:

1. **Does Batch serve `gemini-3.7-flash`?** Its flex capacity has been
   returning 503 since 2026-09-16; batch is a separate pool and may not be.
2. **Does Batch report usage metadata?** On this project's 2026-04-15 Pro
   stages it did not, leaving those passes permanently unauditable
   (``outputs/verifier-meta-recovery-2026-09-14.json``).
3. **Does an EXPLICIT context cache actually bill as a cache hit?** The
   real-time legs get ~81 % of input tokens cached IMPLICITLY, with no cache
   object at all. The Batch API documents only the explicit route — "Reuse
   cached content by specifying the cached_content resource name" — and says
   nothing about implicit caching for batch. So the explicit route is what a
   production batch leg must use, and it is what this probe exercises.

The probe builds the production shared prefix — real system instruction, real
example library — as a context cache, then submits N requests that name it and
carry only their own tile. It reports the cached share the API actually bills,
which is the number that decides whether the leg costs ~US$155 or ~US$381.

Usage:
    python scripts/probe_batch_caching.py --n 100 --model gemini-3.7-flash
    python scripts/probe_batch_caching.py --n 100 --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=100,
                    help="requests in the probe batch (default 100)")
    ap.add_argument("--model", default="gemini-3.7-flash")
    ap.add_argument("--config", default="prompts/configs/detect_brief-text-image.json")
    ap.add_argument("--tiles-dir", default="inputs/tiles_384_ov192_55maps")
    ap.add_argument("--out", default="outputs/batch-probe-2026-09-17/probe.json")
    ap.add_argument("--ttl", type=int, default=86400,
                    help="context-cache TTL in seconds (default 24 h, to "
                         "outlast the batch turnaround target)")
    ap.add_argument("--no-cache", action="store_true",
                    help="submit WITHOUT a context cache, to measure whether "
                         "implicit caching fires for batch")
    ap.add_argument("--dry-run", action="store_true",
                    help="assemble and cost the probe, submit nothing")
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv(REPO / ".env")
    from google import genai
    from google.genai import types

    cfg = json.loads((REPO / args.config).read_text())
    instr = (REPO / "prompts/system-instructions" / cfg["instruction_file"]).read_text()
    examples = cfg.get("examples", [])
    print(f"model      : {args.model}")
    print(f"config     : {args.config}")
    print(f"instruction: {cfg['instruction_file']} ({len(instr):,} chars)")
    print(f"examples   : {len(examples)}  include_example_images={cfg.get('include_example_images')}")
    print(f"requests   : {args.n}")

    tiles = sorted((REPO / args.tiles_dir).rglob("*.png"))[: args.n]
    print(f"tiles found: {len(tiles)}")
    if len(tiles) < args.n:
        print("  ! fewer tiles than requested", file=sys.stderr)

    if args.dry_run:
        print("\nDRY RUN — nothing submitted.")
        print("Worst case (no caching), 3.7 at flex/batch rates, ~19k input tokens/tile:")
        print(f"  {args.n} x $0.007752 = ${args.n * 0.007752:.2f}")
        return 0

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    from scripts.lib_batch_api import build_jsonl_file, create_shared_context_cache

    cache_name, cache_tokens = None, 0
    if not args.no_cache:
        cache_name, cache_tokens = create_shared_context_cache(
            client=client, model_name=args.model, system_instruction=instr,
            examples=examples,
            include_images=cfg.get("include_example_images", True),
            ttl_seconds=args.ttl)
        if cache_name is None:
            print("  ! cache creation FAILED — aborting rather than submitting "
                  "requests that name a cache which does not exist",
                  file=sys.stderr)
            return 2
        print(f"cache      : {cache_name} ({cache_tokens:,} tokens, ttl {args.ttl}s)")

    jsonl = REPO / args.out
    jsonl = jsonl.with_suffix(".jsonl")
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    n_lines = build_jsonl_file(
        tile_paths=tiles, config=cfg, system_instruction=instr,
        examples=examples, output_path=jsonl, cached_content=cache_name)
    print(f"jsonl      : {jsonl} ({n_lines} lines, "
          f"{jsonl.stat().st_size/1e6:.1f} MB)")

    uploaded = client.files.upload(
        file=str(jsonl), config=types.UploadFileConfig(mime_type="application/jsonl"))
    print(f"uploaded   : {uploaded.name}")

    print("\nsubmitting batch ...")
    t0 = time.time()
    job = client.batches.create(model=args.model, src=uploaded.name)
    print(f"  job: {job.name}  state={job.state}")

    while True:
        job = client.batches.get(name=job.name)
        state = str(job.state)
        if "SUCCEEDED" in state or "FAILED" in state or "CANCELLED" in state:
            break
        print(f"  {time.time()-t0:7.0f}s  {state}")
        time.sleep(30)

    print(f"\nfinal state: {job.state} after {time.time()-t0:.0f}s")
    um = getattr(job, "usage_metadata", None)
    result = {"model": args.model, "n": args.n, "state": str(job.state),
              "elapsed_s": round(time.time() - t0, 1),
              "explicit_cache": cache_name, "cache_prefix_tokens": cache_tokens,
              "cache_ttl_s": None if args.no_cache else args.ttl,
              "job_usage_metadata_present": um is not None}
    if um is not None:
        inp = getattr(um, "prompt_token_count", 0) or 0
        cac = getattr(um, "cached_content_token_count", 0) or 0
        result.update({"input_tokens": inp, "cached_tokens": cac,
                       "output_tokens": getattr(um, "candidates_token_count", 0) or 0,
                       "thoughts_tokens": getattr(um, "thoughts_token_count", 0) or 0,
                       "cached_share": (cac / inp) if inp else None})
        print(f"  input {inp:,}  cached {cac:,}  share "
              f"{(cac/inp if inp else 0):.3f}")
    else:
        print("  NO job-level usage_metadata — the 2026-04-15 condition")

    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + "\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
