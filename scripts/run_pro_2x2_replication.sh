#!/usr/bin/env bash
# ============================================================================
# run_pro_2x2_replication.sh
# ----------------------------------------------------------------------------
# Same-day genuine Gemini 3.1 Pro replication of h6 A-06's thinking x
# temperature 2x2 at gold-standard (GS) scale (ruling D64 in
# planning/pi-decisions-2026-09-20.md).
#
# WHY: A-06 reads "temperature is the driver" from corners run on three
# dates in two modes: HIGH T 0.0 (June, real-time), HIGH T 0.7 (March,
# batch, thinking unrecorded), MEDIUM T 0.0 (March and June), MEDIUM T 0.7
# (June). Pro HIGH delivered no thinking (invoice-confirmed, Obs 509), and
# the 2026-10-12 probe found none at T 0.0, 0.7, or 1.0. Running all eight
# corners on one day, in one mode, on one model version, with thinking
# booked per pass, removes the date, mode, and thinking confounds.
#
# PARAMETER CONTROL: the A-06 corners' own configs (detect_brief-text.json
# for text, library_plus-hp.json for image; both unchanged since June), the
# model override gemini-3.1-pro (resolved to gemini-3.1-pro-preview), 384 px
# tiles, all 487 GS tiles. Only thinking level and temperature vary between
# corners within a modality. --allow-inert-fields reproduces the text
# payload as June sent it (the text config lists examples that a text-only
# request never transmits). Batch API with explicit context caching for
# image; per-pass usage, thought tokens included, is booked by
# lib_batch_api.aggregate_batch_usage. --service-tier sets only the tier of
# synchronous parse-failure retries.
#
# PASSES: 5 per text corner, 3 per image corner (phase gate: the text MEDIUM
# cell's A-06 delta, +0.0366, sits inside the replicate floor of the 0.03
# rule at 3 passes).
#
# BUDGET: PI cap US$100 (with the thinking-budget probe). Estimate about
# US$37-55, assuming Pro delivers no thinking. STOP RULE: wave 1 runs each
# corner's first pass alone; the main session halts for the PI if any pass
# costs more than twice its estimate (text about US$0.93, image about
# US$1.50-3.00) or shows real thinking (more than 100 thought tokens per
# request on average). Wave 2 is launched only after that check.
#
# Usage (repository root; writes its own pid file and per-pass logs):
#   nohup bash scripts/run_pro_2x2_replication.sh smoke > /dev/null 2>&1 < /dev/null &
#   nohup bash scripts/run_pro_2x2_replication.sh wave1 > /dev/null 2>&1 < /dev/null &
#   nohup bash scripts/run_pro_2x2_replication.sh wave2 > /dev/null 2>&1 < /dev/null &
#
# Author: Shawn Ross & Claude (Anthropic), Session 163, 2026-10-13
# ============================================================================
set -uo pipefail

cd "$(dirname "$0")/.."  # repo root
PY=.venv/bin/python
MODEL=gemini-3.1-pro
BASE=outputs/pro-2x2-replication-2026-10-13
FULL_MANIFEST=inputs/tiles_384/full_evaluation_manifest.json
SMOKE_MANIFEST="$BASE/tiles-10-smoke-seed42.json"
TILES_DIR=inputs/tiles_384
STAGE=${1:?usage: run_pro_2x2_replication.sh smoke|wave1|wave2}
LOG="$BASE/_run_log_${STAGE}.txt"
mkdir -p "$BASE"
echo $$ > "$BASE/${STAGE}.pid"

# corner -> "config temperature thinking passes"
declare -A CORNERS=(
  [text-high-t0.0]="detect_brief-text.json 0.0 high 5"
  [text-high-t0.7]="detect_brief-text.json 0.7 high 5"
  [text-medium-t0.0]="detect_brief-text.json 0.0 medium 5"
  [text-medium-t0.7]="detect_brief-text.json 0.7 medium 5"
  [image-high-t0.0]="library_plus-hp.json 0.0 high 3"
  [image-high-t0.7]="library_plus-hp.json 0.7 high 3"
  [image-medium-t0.0]="library_plus-hp.json 0.0 medium 3"
  [image-medium-t0.7]="library_plus-hp.json 0.7 medium 3"
)

run_pass() {  # corner manifest outdir run
  local corner=$1 manifest=$2 outdir=$3 run=$4
  read -r config temp think _ <<< "${CORNERS[$corner]}"
  # Context caching for image only. The batch path reads
  # include_example_images from a config dict that lacks it and defaults to
  # True (lib_batch_api.run_batch_unit, called with the runner's
  # batch_config), so a cached TEXT request carries the 17 example images:
  # the 2026-10-13 smoke run measured 20,020 input tokens per text request
  # against June's 1,502. Text has nothing worth caching (the real-time
  # cache is refused as too small), so text runs uncached, as June did.
  local cache_flag="--use-cache"
  [[ "$config" == detect_brief-text.json ]] && cache_flag=""
  echo "=== $(date -u +%FT%TZ) START $corner run_$run (T=$temp think=$think) ===" >> "$LOG"
  "$PY" scripts/4_detect_mounds_batch.py \
    --config "prompts/configs/$config" \
    --model "$MODEL" --temperature "$temp" --thinking-level "$think" \
    --manifest "$manifest" --tiles-dir "$TILES_DIR" --tile-size 384 \
    --output-dir "$outdir" --mode batch --run "$run" \
    $cache_flag --skip-intent-check --allow-inert-fields \
    --service-tier flex --workers 4 \
    > "$outdir.run_$run.log" 2>&1 < /dev/null
  local rc=$?
  echo "=== $(date -u +%FT%TZ) END   $corner run_$run exit=$rc ===" >> "$LOG"
}

echo "=== $(date -u +%FT%TZ) $STAGE LAUNCH (model=$MODEL, batch) ===" >> "$LOG"
case "$STAGE" in
  smoke)
    for corner in ${SMOKE_CORNERS:-text-high-t0.0 image-high-t0.0}; do
      mkdir -p "$BASE/smoke"
      run_pass "$corner" "$SMOKE_MANIFEST" "$BASE/smoke/$corner" "${SMOKE_RUN:-1}" &
    done
    wait ;;
  wave1)
    for corner in "${!CORNERS[@]}"; do
      run_pass "$corner" "$FULL_MANIFEST" "$BASE/$corner" 1 &
    done
    wait ;;
  wave2)
    for corner in "${!CORNERS[@]}"; do
      read -r _ _ _ passes <<< "${CORNERS[$corner]}"
      ( for run in $(seq 2 "$passes"); do
          run_pass "$corner" "$FULL_MANIFEST" "$BASE/$corner" "$run"
        done ) &
    done
    wait ;;
  *) echo "unknown stage $STAGE" >> "$LOG"; rm -f "$BASE/${STAGE}.pid"; exit 2 ;;
esac
echo "=== $(date -u +%FT%TZ) $STAGE COMPLETE ===" >> "$LOG"
rm -f "$BASE/${STAGE}.pid"
