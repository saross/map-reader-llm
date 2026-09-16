#!/usr/bin/env python3
"""Probe whether the Batch API serves a model, reports usage, and caches.

Three questions must be answered BEFORE a bulk batch leg, because each one
independently decides whether the leg is affordable or auditable:

1. **Does Batch serve `gemini-3.7-flash`?** Its flex capacity has been
   returning 503 since 2026-09-16; batch is a separate pool and may not be.
2. **Does Batch report usage metadata?** On this project's 2026-04-15 Pro
   stages it did not, leaving those passes permanently unauditable
   (``outputs/verifier-meta-recovery-2026-09-14.json``).
3. **Does Batch get IMPLICIT prefix caching?** The real-time legs cache about
   81 % of input tokens without any explicit cache object. If batch does not,
   the 3.7 runs 4-5 cost about US$381 instead of about US$155.

The probe sends N copies of a realistic prompt — the real system instruction
and example images, so the cacheable prefix is the production one — and reads
the usage each response reports. Prompts are identical by design: implicit
caching keys on a shared prefix, so identical prompts are the most favourable
case. A cache miss HERE is decisive; a cache hit here is necessary but not
sufficient for the full leg.

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
    requests = []
    for tile in tiles:
        parts = [types.Part.from_bytes(data=tile.read_bytes(), mime_type="image/png")]
        requests.append({
            "contents": [{"role": "user", "parts": [p.model_dump() for p in parts]}],
            "config": {"system_instruction": instr,
                       "temperature": cfg.get("temperature", 0.7),
                       "max_output_tokens": cfg.get("max_output_tokens", 8192)},
        })

    print("\nsubmitting batch ...")
    t0 = time.time()
    job = client.batches.create(model=args.model, src=requests)
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
