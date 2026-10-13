#!/usr/bin/env bash
# ============================================================================
# run_pro_thinking_probe.sh
# ----------------------------------------------------------------------------
# Does Gemini 3.1 Pro think at thinking_level HIGH, and does temperature
# switch that thinking on or off?
#
# WHY: the genuine-Pro HIGH passes of 2026-06-03 (n1-pro-rerun-384,
# T = 0.0) record zero thought tokens, and the June 2026 invoice confirms
# the zeros are real (reports/manipulation-check-2026-10-05.md, section D,
# revised 2026-10-12). h6 A-06 reads "temperature is the driver" from a
# contrast of those T = 0.0 passes with March T = 0.7 Pro HIGH passes whose
# thinking was never recorded. This probe measures delivered thinking at
# each temperature on today's service (PI approval 2026-10-12, ruling D61
# (4) in planning/pi-decisions-2026-09-20.md).
#
# PARAMETER CONTROL: every flag below matches scripts/run_n1_pro_rerun.sh
# (the June run): same configs (detect_brief-text.json for text,
# library_plus-hp.json for image), same model override (gemini-3.1-pro,
# resolved to gemini-3.1-pro-preview), thinking HIGH, real-time on the
# flex tier, context caching on, 384 px tiles. Only temperature varies
# between arms within a modality. The tiles are a seeded sample of 50 of
# the 487 gold-standard 384 px tiles (random.Random(42).sample over the
# sorted manifest), the same 50 for every arm. --allow-inert-fields is
# the runner's documented switch for reproducing a historical run as sent:
# the text config lists examples that a text-only request never transmits
# (the guard postdates June); the payload is unchanged.
#
# LIMITS: this measures the model as served today (version
# 3.1-pro-preview-01-2026 on 2026-10-12), not as served in March or June;
# same-model drift is a standing condition (Obs 508). It can show whether
# temperature gates Pro's thinking now; it cannot prove what the March
# passes did.
#
# API: 5 arms x 50 tiles = 250 real-time flex calls. Worst case about
# US$8.50 if Pro thinks as much as Flash HIGH (about 4,100 thought tokens
# per request); well under US$3 if it does not.
#
# Usage (from the repository root; writes its own pid file and log):
#   nohup bash scripts/run_pro_thinking_probe.sh > /dev/null 2>&1 < /dev/null &
#
# Author: Shawn Ross & Claude (Anthropic), Session 163, 2026-10-12
# ============================================================================
set -uo pipefail

cd "$(dirname "$0")/.."  # repo root
PY=.venv/bin/python
MODEL=gemini-3.1-pro
BASE=outputs/pro-thinking-probe-2026-10-12
MANIFEST="$BASE/tiles-50-seed42.json"
TILES_DIR=inputs/tiles_384
WORKERS=10
LOG="$BASE/_run_log.txt"
mkdir -p "$BASE"
echo $$ > "$BASE/probe.pid"

echo "=== $(date -u +%FT%TZ) pro-thinking-probe LAUNCH (model=$MODEL, flex, workers=$WORKERS) ===" >> "$LOG"

run_arm() {
  local arm=$1 config=$2 temp=$3
  local outdir="$BASE/$arm"
  echo "=== $(date -u +%FT%TZ) START $arm (temp=$temp think=high) ===" >> "$LOG"
  "$PY" scripts/4_detect_mounds_batch.py \
    --config "prompts/configs/$config" \
    --model "$MODEL" --temperature "$temp" --thinking-level high \
    --manifest "$MANIFEST" --tiles-dir "$TILES_DIR" --tile-size 384 \
    --output-dir "$outdir" \
    --mode realtime --service-tier flex --use-cache --skip-intent-check \
    --allow-inert-fields \
    --workers "$WORKERS" >> "$LOG" 2>&1 < /dev/null
  local rc=$?
  echo "=== $(date -u +%FT%TZ) END   $arm exit=$rc ===" >> "$LOG"
}

# arm        config                  temp
run_arm text-t0.0  detect_brief-text.json 0.0
run_arm text-t0.7  detect_brief-text.json 0.7
run_arm text-t1.0  detect_brief-text.json 1.0
run_arm image-t0.0 library_plus-hp.json   0.0
run_arm image-t0.7 library_plus-hp.json   0.7

echo "=== $(date -u +%FT%TZ) ALL 5 ARMS COMPLETE ===" >> "$LOG"
rm -f "$BASE/probe.pid"
