#!/usr/bin/env bash
# The 55-map deployment portfolio driver — Runs A and B.
#
# Card: planning/55map-portfolio-2026-08-25.md (the binding measurement
# contract). LAUNCH ONLY AFTER THE PI SIGNS OFF THE CARD'S § 6.
#
# Run A: 384/33.3 (stride 256), 14,160 tiles x 10 passes = 141,600 calls.
# Run B: 384/50   (stride 192), 24,561 tiles x 10 passes = 245,610 calls.
# gemini-3-flash (resolves -preview), realtime FLEX, T = 0.7 override,
# tile size inferred from tiles (S142 runner contract).
#
# Runbook (the S142-hardened pattern): idempotent .done resume; a failed
# pass logs FAILED and the driver continues; cheapest run first; residual
# one-tile gaps get recovery fragments before unions (next session);
# per-run meta cost/coverage reconciliation precedes the verifier stage,
# which is priced at MEASURED union sizes under the card's 2x ceiling.
set -uo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
CONFIG=prompts/configs/detect_brief-text.json
MANDIR=inputs/stride-55map-2026-08-25
OUTROOT=outputs/stride-55map-2026-08-25

CELLS="\
g384_ov128_55map:inputs/tiles_384_ov128_55maps \
g384_ov192_55map:inputs/tiles_384_ov192_55maps"

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
        --workers "${WORKERS:-20}"; then
      touch "$out/.done"
      echo "=== $cell run_$run done $(date -Is)"
    else
      echo "FAILED $cell run_$run $(date -Is)"
    fi
  done
done
echo "PORTFOLIO PROPOSERS DONE $(date -Is)"
