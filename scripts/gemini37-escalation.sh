#!/usr/bin/env bash
# Gemini 3.7 Flash escalation — passes 6-10 (PI-APPROVED 2026-08-29).
#
# Card: planning/gemini37-screen-2026-08-28.md § Escalation. The K=5
# screen fired the G1 informative outcome (verified best 0.9139 @20 m,
# above the Gemini 3 plateau); the PI approved passes 6-10 at the SAME
# invocation as runs 1-5 (+~$6.5 flex expected). The later stages —
# union @ K=10, increment verification, sweeps/ladders, verifier-role
# swap — run GATED from the interactive session after this driver
# finishes; they are deliberately not chained here (grid/stride
# precedent: residual coverage gaps get recovery passes at the E72
# gate, and every verifier launch is reconciled against pass metas
# first).
#
# Runbook (pre-run-review substance, recorded in the header as the
# Phase-B driver did):
#   Artefacts:  outputs/gemini37-screen-2026-08-28/g384_ov192_g37/
#               run_<N>/ for N in 6..10 — one detections geojson +
#               meta + tiles.json + experiment_intent.md per pass,
#               plus a .done marker per completed pass.
#   Finished:   five .done markers (runs 6-10); "ALL PASSES DONE" on
#               stdout.
#   Stop:       a pass that exits non-zero logs "FAILED run_<N>" and
#               the driver CONTINUES (no set -e) — one bad pass must
#               not kill the run. Re-running the script skips .done
#               passes (idempotent resume).
#   Dependency: passes are independent; the union is derived at
#               scoring time.
#   Partial:    missing tiles within a pass are the runner's retry
#               problem (15 retries); residual gaps surface at the
#               coverage gate and get recovery passes (K=5 precedent:
#               run_1..4_recovery).
#   Verify:     the interactive session reconciles per-pass meta cost
#               and coverage against this header BEFORE the verifier
#               increment launch.
set -uo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
CONFIG=prompts/configs/detect_brief-text.json
MANIFEST=inputs/grid-2026-08-18/grid_384_ov192_manifest.json
TILES=inputs/tiles_384_ov192
OUTROOT=outputs/gemini37-screen-2026-08-28
MODEL_ARGS="--model gemini-3.7-flash --thinking-level low"

for run in 6 7 8 9 10; do
  out=$OUTROOT/g384_ov192_g37/run_$run
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
      $MODEL_ARGS --workers "${WORKERS:-12}"; then
    touch "$out/.done"
    echo "=== run_$run done $(date -Is)"
  else
    echo "FAILED run_$run $(date -Is)"
  fi
done
echo "ALL PASSES DONE $(date -Is)"
