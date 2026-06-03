#!/usr/bin/env bash
# ============================================================================
# run_n1_pro_rerun.sh
# ----------------------------------------------------------------------------
# Re-run the four n1-outstanding-384 "Pro" cells as GENUINE Gemini 3.1 Pro.
#
# WHY: the original n1-outstanding "pro-*" pools were dispatched as Flash, not
# Pro (E57 billing reconciliation, Session 97 / 2026-06-03 — confirmed by the
# Gemini API response model_version = gemini-3-flash-preview across all ~3,896
# tile responses). The study YAMLs intended `model: gemini-3.1-pro` but the
# runner never threaded it into the --model flag. This script completes the
# genuine-Pro thinking x temperature 2x2 by re-running with the override
# actually applied.
#
# PARAMETER CONTROL: configs are byte-identical to the flash originals AND to
# the genuine pv-diag Pro grid partners (library_hash + system_instruction_hash
# audited, Session 97). ONLY the model changes (Flash -> gemini-3.1-pro, which
# _resolve_model_name maps to gemini-3.1-pro-preview, matching pv-diag). Prompt
# assembly is byte-equivalent between batch (originals) and realtime (this run)
# for both config types (_build_reference_parts returns [] for text;
# include_images-guarded image loop). One-tile tests confirmed model_version =
# gemini-3.1-pro-preview before launch.
#
# API: real-time + flex service tier (50% discount = batch cost), context
# caching on (engages for image; text prefix < 1024 tokens so it skips, as
# expected). Output to a NEW run dir; the flash originals are preserved
# (archive-never-delete; they become correctly-labelled Flash cells).
#
# Replicates 3/3/1/1 match the flash originals. 8 passes x 487 tiles = 3,896
# calls. Estimated ~$20-30 (flex, with image caching).
#
# Author: Shawn Ross & Claude (Anthropic) — Session 97, 2026-06-03
# ============================================================================
set -uo pipefail

cd "$(dirname "$0")/.."  # repo root
PY=.venv/bin/python
MODEL=gemini-3.1-pro
MANIFEST=inputs/tiles_384/full_evaluation_manifest.json
TILES_DIR=inputs/tiles_384
BASE=outputs/h11/n1-pro-rerun-384
WORKERS=24
LOG="$BASE/_run_log.txt"
mkdir -p "$BASE"

echo "=== $(date -u +%FT%TZ) n1-pro-rerun LAUNCH (model=$MODEL, flex, workers=$WORKERS) ===" | tee -a "$LOG"

run_pass() {
  local pool=$1 config=$2 temp=$3 think=$4 run=$5
  local outdir="$BASE/$pool/run_$run"
  echo "=== $(date -u +%FT%TZ) START $pool run_$run (temp=$temp think=$think) ===" | tee -a "$LOG"
  "$PY" scripts/4_detect_mounds_batch.py \
    --config "prompts/configs/$config" \
    --model "$MODEL" --temperature "$temp" --thinking-level "$think" \
    --manifest "$MANIFEST" --tiles-dir "$TILES_DIR" --tile-size 384 \
    --output-dir "$outdir" \
    --mode realtime --service-tier flex --use-cache --skip-intent-check \
    --workers "$WORKERS" >> "$LOG" 2>&1
  local rc=$?
  echo "=== $(date -u +%FT%TZ) END   $pool run_$run exit=$rc ===" | tee -a "$LOG"
}

# pool                  config                  temp think   run
run_pass pro-text-high-t0     detect_brief-text.json 0.0 high   1
run_pass pro-text-high-t0     detect_brief-text.json 0.0 high   2
run_pass pro-text-high-t0     detect_brief-text.json 0.0 high   3
run_pass pro-image-high-t0    library_plus-hp.json   0.0 high   1
run_pass pro-image-high-t0    library_plus-hp.json   0.0 high   2
run_pass pro-image-high-t0    library_plus-hp.json   0.0 high   3
run_pass pro-text-medium-t07  detect_brief-text.json 0.7 medium 1
run_pass pro-image-medium-t07 library_plus-hp.json   0.7 medium 1

echo "=== $(date -u +%FT%TZ) ALL 8 PASSES COMPLETE ===" | tee -a "$LOG"
