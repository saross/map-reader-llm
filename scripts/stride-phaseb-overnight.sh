#!/usr/bin/env bash
# Stride-programme Phase B overnight proposer driver.
#
# PI approval 2026-08-25 (session): four iso-stride cells, K = 10 passes each,
# 41,250 proposer calls, ~$25.6 flex expected (~$51 list on the metas).
# Model gemini-3-flash (resolves to gemini-3-flash-preview), real-time FLEX,
# detect_brief-text config with the grid's --temperature 0.7 override
# (config default is 1.0; the grid ran 0.7 — parameter-control audit point).
#
# Pre-run runbook (pre-run-review substance; the interview was not possible —
# PI asleep — so the six sections are recorded here instead):
#   Artefacts:  outputs/stride-phaseb-2026-08-25/<cell>/run_<N>/ — one
#               detections geojson + meta + tiles.json per pass, plus
#               experiment_intent.md; a .done marker per completed pass.
#   Finished:   40 .done markers; "ALL CELLS DONE" on stdout.
#   Stop:       a pass that exits non-zero logs "FAILED <cell> run_<N>" and
#               the driver CONTINUES (no set -e) — one bad pass must not
#               kill the night. Ctrl-C / kill stops between passes.
#   Dependency: cells are independent; passes within a cell are independent
#               (consensus is derived at scoring time). Order: cheapest cell
#               first so an early systemic failure costs least.
#   Partial:    a re-run of this script skips .done passes (idempotent
#               resume). Missing tiles inside a pass are the runner's retry
#               problem (15 retries); residual gaps surface at the E72
#               coverage gate at scoring and get one-tile recovery passes,
#               the grid precedent.
#   Verify:     per-pass meta cost/coverage recorded by the runner; the
#               morning session reconciles call counts and spend against
#               this header before any verifier launch.
set -uo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
CONFIG=prompts/configs/detect_brief-text.json
OUTROOT=outputs/stride-phaseb-2026-08-25
MANDIR=inputs/stride-phaseb-2026-08-25

# Cheapest first (494 tiles/pass), densest last.
CELLS="g512_ov176:inputs/tiles_512_ov176 g384_ov128:inputs/tiles_384_ov128 g256_ov064:inputs/tiles_256_ov064 g512_ov320:inputs/tiles_512_ov320"

for spec in $CELLS; do
  cell=${spec%%:*}
  tiles=${spec##*:}
  manifest=$MANDIR/${cell}_manifest.json
  for run in 1 2 3 4 5 6 7 8 9 10; do
    out=$OUTROOT/$cell/run_$run
    if [ -f "$out/.done" ]; then
      echo "=== $cell run_$run already done, skipping"
      continue
    fi
    echo "=== $cell run_$run start $(date -Is)"
    if $PY scripts/4_detect_mounds_batch.py \
        --config "$CONFIG" \
        --manifest "$manifest" \
        --tiles-dir "$tiles" \
        --output-dir "$out" \
        --mode realtime \
        --service-tier flex \
        --temperature 0.7 \
        --workers "${WORKERS:-12}"; then
      touch "$out/.done"
      echo "=== $cell run_$run done $(date -Is)"
    else
      echo "FAILED $cell run_$run $(date -Is)"
    fi
  done
done
echo "ALL CELLS DONE $(date -Is)"
