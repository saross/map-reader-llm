#!/usr/bin/env bash
# Stride overnight v2 — remainder chain after the --tile-size blocker.
#
# The v1 driver (stride-phaseb-overnight.sh) omitted --tile-size, which the
# runner requires for non-512 tiles; its two 384/256 cells fast-fail at the
# PRE-API dimension guard ($0 spent, no .done markers), while its two 512
# cells run correctly. This driver waits for v1 to finish, then runs:
#   1. the two Phase B cells v1 missed, WITH --tile-size (PI-approved spend);
#   2. the Phase C stride-144 cell g384_ov240 (PI approved "384/144 only
#      tonight", 2026-08-25; 24,830 calls ~= $14.9 flex, inside the <=$17).
# All non-512 dry-runs re-validated PASSED with the flag before this chain
# was armed. Same runbook semantics as v1: idempotent .done resume,
# per-pass failures logged and skipped, never fatal.
set -uo pipefail
cd "$(dirname "$0")/.."

until grep -q "ALL CELLS DONE" /tmp/stride_phaseb_overnight.log 2>/dev/null; do
  sleep 120
done

PY=.venv/bin/python
CONFIG=prompts/configs/detect_brief-text.json
MANDIR=inputs/stride-phaseb-2026-08-25

# cell : tile-size px : tiles dir : output root
CELLS="\
g384_ov128:384:inputs/tiles_384_ov128:outputs/stride-phaseb-2026-08-25 \
g256_ov064:256:inputs/tiles_256_ov064:outputs/stride-phaseb-2026-08-25 \
g384_ov240:384:inputs/tiles_384_ov240:outputs/stride-phasec-2026-08-25"

for spec in $CELLS; do
  IFS=: read -r cell px tiles outroot <<< "$spec"
  manifest=$MANDIR/${cell}_manifest.json
  for run in 1 2 3 4 5 6 7 8 9 10; do
    out=$outroot/$cell/run_$run
    if [ -f "$out/.done" ]; then
      echo "=== $cell run_$run already done, skipping"
      continue
    fi
    echo "=== $cell run_$run start $(date -Is)"
    if $PY scripts/4_detect_mounds_batch.py \
        --config "$CONFIG" \
        --manifest "$manifest" \
        --tiles-dir "$tiles" \
        --tile-size "$px" \
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
echo "V2 ALL DONE $(date -Is)"
