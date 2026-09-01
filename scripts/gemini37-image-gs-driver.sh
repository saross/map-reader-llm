#!/usr/bin/env bash
# Gemini 3.7 image-GS screen driver — K=5 on B geometry, GS corpus.
#
# Card: planning/gemini37-image-gs-2026-08-30.md (PI go 2026-08-31;
# launch approved at the probed cost 2026-09-01: ~$34-36 token-basis
# / ~$20-22 billed-expected; cache fraction ~54-65% measured, the
# I5 >=90% expectation runs as a registered prediction).
# Probe PASSED stamps (gemini-3.7-flash / low / T=0.7); /audit-config
# delta clean (config md5 9ff5e64d..., manifest 1,398 = tree, output
# root clean). Prefix warmed by the 20 probe calls; launch follows
# immediately to maximise implicit-cache hits (PI: "please use
# caching").
#
# Phase-B pattern: idempotent .done per pass, failures non-fatal,
# re-run skips completed passes.
set -uo pipefail
cd "$(dirname "$0")/.."

# Image mode attaches 17 example images per call; at WORKERS=400 the
# concurrent open-file load blew the default ulimit of 1024 (fd/SSL
# storms killed passes 2-5 on 2026-09-01 — Bad file descriptor,
# UNEXPECTED_EOF, BAD_RECORD_MAC). Raise the ceiling and cap image
# concurrency at 150 (throughput was governor-bound anyway).
ulimit -n 8192 || true

PY=.venv/bin/python
CONFIG=prompts/configs/detect_brief-text-image.json
MANIFEST=inputs/grid-2026-08-18/grid_384_ov192_manifest.json
TILES=inputs/tiles_384_ov192
OUTROOT=outputs/gemini37-image-gs-2026-09-01
MODEL_ARGS="--model gemini-3.7-flash --thinking-level low"

for run in 1 2 3 4 5; do
  out=$OUTROOT/g384_ov192_g37img/run_$run
  if [ -f "$out/.done" ]; then
    echo "=== run_$run already done, skipping"
    continue
  fi
  echo "=== run_$run start $(date -Is)"
  if $PY scripts/4_detect_mounds_batch.py \
      --config "$CONFIG" \
      --manifest "$MANIFEST" \
      --tiles-dir "$TILES" \
      --output-dir "$out" \
      --mode realtime --service-tier flex --temperature 0.7 \
      $MODEL_ARGS --workers "${WORKERS:-150}"; then
    touch "$out/.done"
    echo "=== run_$run done $(date -Is)"
  else
    echo "FAILED run_$run $(date -Is)"
  fi
done
echo "ALL PASSES DONE $(date -Is)"
