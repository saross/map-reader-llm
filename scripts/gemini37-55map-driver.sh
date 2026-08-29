#!/usr/bin/env bash
# Gemini 3.7 55-map deployment proposer driver — K=5 on B geometry.
#
# Card: planning/gemini37-55map-2026-08-29.md (PI ruling 2026-08-29:
# B geometry K=5, all-in ceiling $200). Probe PASSED same day (stamps
# model gemini-3.7-flash / thinking low / T=0.7; thinking 275.6
# t/tile; implied all-in $125-190). /audit-config READY (config
# byte-identical, manifest 24,561 = tree exactly, dims 384, dry-run
# validation PASSED, output root clean).
#
# Runbook (pre-run-review substance, the Phase-B pattern):
#   Artefacts:  outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/
#               run_<N>/ for N in 1..5 — detections geojson + meta +
#               tiles.json + experiment_intent.md; .done per pass.
#   Finished:   five .done markers; "ALL PASSES DONE" on stdout.
#   Stop:       non-zero pass logs "FAILED run_<N>", driver CONTINUES
#               (no set -e); re-run skips .done passes (idempotent).
#   Dependency: passes independent; union derived at scoring time.
#   Partial:    missing tiles are the runner's retry problem (15
#               retries); residual gaps get recovery fragments at the
#               coverage gate before any union.
#   Verify:     interactive session reconciles per-pass meta cost and
#               coverage BEFORE the verifier launch (verifier priced
#               at the MEASURED union, within the card ceiling).
set -uo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
CONFIG=prompts/configs/detect_brief-text.json
MANIFEST=inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json
TILES=inputs/tiles_384_ov192_55maps
OUTROOT=outputs/gemini37-55map-2026-08-29
MODEL_ARGS="--model gemini-3.7-flash --thinking-level low"

for run in 1 2 3 4 5; do
  out=$OUTROOT/g384_ov192_55map_g37/run_$run
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
      $MODEL_ARGS --workers "${WORKERS:-40}"; then
    touch "$out/.done"
    echo "=== run_$run done $(date -Is)"
  else
    echo "FAILED run_$run $(date -Is)"
  fi
done
echo "ALL PASSES DONE $(date -Is)"
