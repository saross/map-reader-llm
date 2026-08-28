#!/usr/bin/env bash
# Image-on-B GS driver: one cell, K = 10 passes, MINIMAL, cached.
#
# Card: planning/image-b-gs-2026-08-28.md (PI-approved design; launch
# gated on the pricing probe + /audit-config). Mirrors the Phase-B
# overnight pattern: idempotent .done resume, one bad pass does not
# kill the night, per-pass metas are the cost/coverage record.
#
# 13,980 proposer calls (1,398 tiles x 10 passes), gemini-3-flash
# (resolves -preview), detect_brief-text-image (17 example images, the
# byte-identical sibling of the leading text config), --temperature
# 0.7 CLI override (config default 1.0 — parameter-control audit
# point, same as every stride/grid run), real-time FLEX, explicit
# context cache per pass (--use-cache: system instruction + examples).
set -uo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
CONFIG=prompts/configs/detect_brief-text-image.json
MANIFEST=inputs/grid-2026-08-18/grid_384_ov192_manifest.json
TILES=inputs/tiles_384_ov192
OUTROOT=${OUTROOT:-outputs/image-b-gs-2026-08-28/g384_ov192_image}
# THINKING_ARGS="--thinking-level high" selects the §5a HIGH cell.
THINKING_ARGS=${THINKING_ARGS:-}

for run in 1 2 3 4 5 6 7 8 9 10; do
  out=$OUTROOT/run_$run
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
      --mode realtime \
      --service-tier flex \
      --temperature 0.7 \
      --use-cache $THINKING_ARGS \
      --workers "${WORKERS:-12}"; then
    touch "$out/.done"
    echo "=== run_$run done $(date -Is)"
  else
    echo "FAILED run_$run $(date -Is)"
  fi
done
echo "ALL PASSES DONE $(date -Is)"
