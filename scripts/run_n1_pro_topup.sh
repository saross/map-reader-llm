#!/usr/bin/env bash
# ============================================================================
# run_n1_pro_topup.sh
# ----------------------------------------------------------------------------
# Bring the four MEDIUM-thinking genuine-Pro leaderboard cells from n=1 to n=3
# (minimal anti-noise step). Adds +2 replicate passes to each of:
#
#   pro-text-medium-t-0-0   (pv-diag-384/pro-medium-text-baseline/text-t0.0)
#   pro-image-medium-t-0-0  (pv-diag-384/pro-medium-image-baseline/image-t0.0)
#   pro-text-medium-t-0-7   (n1-pro-rerun-384/pro-text-medium-t07)
#   pro-image-medium-t-0-7  (n1-pro-rerun-384/pro-image-medium-t07)
#
# WHY: the four HIGH-thinking Pro cells already have n>=3 (10/5/3/3); the four
# MEDIUM cells were each n=1, so their leaderboard point estimate was a single
# (noisy) draw. T=0.0 is NOT deterministic for Gemini 3.1 Pro (Obs 338: 3 T=0.0
# replicates differ), so even the T=0.0 cells benefit from replication.
#
# PARAMETER CONTROL: byte-identical configs to each pool's existing pass —
# confirmed by hash audit (Session 98): all four share instruction_hash
# e169b72…; text library_hash 8580ecb…, image library_hash 3f7f028…. ONLY the
# model (-> gemini-3.1-pro -> gemini-3.1-pro-preview) and replicate index change;
# thinking=medium and the per-cell temperature match the existing pass. The
# pv-diag run_1 files are batch-style (detections_*.geojson); the new realtime
# passes are detections-*.geojson, so those two pools become MIXED — the eval +
# tiering use a union glob (*/detections*.geojson) to aggregate all three.
# One-tile end-to-end tests confirmed model_version=gemini-3.1-pro-preview and
# the instruction/library hashes for all four exact commands before launch.
#
# API: real-time + flex service tier (the path proven to thread --model; the
# batch path of this runner dropped it = E57), context caching on. 8 passes x
# 487 tiles = 3,896 calls. Estimated ~$70 standard-rate cost_estimate (image
# dominates: ~$15.7/pass vs ~$1.9 text); flex tier may bill lower.
#
# Existing passes are untouched (archive-never-delete). New passes land in
# run_2/ and run_3/ alongside the existing run_1/.
#
# Author: Shawn Ross & Claude (Anthropic) — Session 98, 2026-06-03
# ============================================================================
set -uo pipefail

cd "$(dirname "$0")/.."  # repo root
PY=.venv/bin/python
MODEL=gemini-3.1-pro
MANIFEST=inputs/tiles_384/full_evaluation_manifest.json
TILES_DIR=inputs/tiles_384
WORKERS=24
LOG=outputs/h11/n1-pro-rerun-384/_topup_run_log.txt

echo "=== $(date -u +%FT%TZ) n1-pro-topup LAUNCH (model=$MODEL, flex, cache, workers=$WORKERS) ===" | tee -a "$LOG"

run_pass() {
  local config=$1 temp=$2 outdir=$3
  echo "=== $(date -u +%FT%TZ) START $outdir (temp=$temp) ===" | tee -a "$LOG"
  "$PY" scripts/4_detect_mounds_batch.py \
    --config "prompts/configs/$config" \
    --model "$MODEL" --temperature "$temp" --thinking-level medium \
    --manifest "$MANIFEST" --tiles-dir "$TILES_DIR" --tile-size 384 \
    --output-dir "$outdir" \
    --mode realtime --service-tier flex --use-cache --skip-intent-check \
    --workers "$WORKERS" >> "$LOG" 2>&1
  echo "=== $(date -u +%FT%TZ) END   $outdir exit=$? ===" | tee -a "$LOG"
}

# config                  temp  output dir (+2 passes per cell)
run_pass detect_brief-text.json 0.0 outputs/h11/pv-diag-384/pro-medium-text-baseline/text-t0.0/run_2
run_pass detect_brief-text.json 0.0 outputs/h11/pv-diag-384/pro-medium-text-baseline/text-t0.0/run_3
run_pass library_plus-hp.json   0.0 outputs/h11/pv-diag-384/pro-medium-image-baseline/image-t0.0/run_2
run_pass library_plus-hp.json   0.0 outputs/h11/pv-diag-384/pro-medium-image-baseline/image-t0.0/run_3
run_pass detect_brief-text.json 0.7 outputs/h11/n1-pro-rerun-384/pro-text-medium-t07/run_2
run_pass detect_brief-text.json 0.7 outputs/h11/n1-pro-rerun-384/pro-text-medium-t07/run_3
run_pass library_plus-hp.json   0.7 outputs/h11/n1-pro-rerun-384/pro-image-medium-t07/run_2
run_pass library_plus-hp.json   0.7 outputs/h11/n1-pro-rerun-384/pro-image-medium-t07/run_3

echo "=== $(date -u +%FT%TZ) ALL 8 TOP-UP PASSES COMPLETE ===" | tee -a "$LOG"
