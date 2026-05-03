#!/bin/bash
# Gold-Standard v2 T=0.7 — Single-round recovery for proposer failures
# ====================================================================
#
# Recovers the 13 unrecovered proposer tile-pass failures from the
# 2026-04-10 GS-v2 production run on the 4-GS-map corpus
# (`outputs/h11/gold-standard-v2/`):
#
#     run_1: 2 failures (JSON parse errors)
#     run_2: 4 failures
#     run_3: 2 failures (1 retries-exhausted, 1 parse)
#     run_4: 0 failures
#     run_5: 5 failures (1 retries-exhausted, 4 parse)
#     ───────────────
#     total: 13 / 2,435 attempts (0.534 % unrecovered rate)
#
# This is the gold-standard production companion to
# `55maps-t0.7-recovery.sh`. Same proposer config (`detect_brief-text`,
# T=0.7, HIGH thinking, K=5), smaller corpus (487 tiles per pass × 5),
# but distinct downstream pipeline:
#
#   - GS-v2 verifier output is a single `verified-v1/` directory using
#     `probabilities.json` + `verified_detections_full-scope.geojson`
#     (not the per-pass scheme used on 55maps).
#   - Ground truth is `mounds-reference.geojson` (NOT the student GT).
#   - Bounds are `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`
#     (487-tile Era 2 — the canonical 384 px scope per Shawn's preference).
#   - Rasters dir is `inputs/rasters/` (flat — 4-map structure differs
#     from 55-map's `Russian1981_32635/` subdir).
#
# Single-round only (per Shawn's directive on the T=0.7 sibling — stubborn
# failures are accepted). Re-runs proposer per-pass via the resume logic
# in `4_detect_mounds_batch.py` (full manifest; the script auto-skips
# already-processed tiles), then merges the per-pass meta.json back into
# the original to preserve cost data.
#
# As with the 55maps drivers, this is the documented intent. The
# orchestrating Claude Code agent executes the stages individually with
# auto-proceed gates and per-stage commits + pushes.
#
# Usage:
#   nohup bash scripts/gs-v2-t0.7-recovery.sh \
#     > outputs/h11/gold-standard-v2/recovery.log 2>&1 &

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate
# Load .env so GOOGLE_API_KEY is exported for the API client.
set -a
source .env
set +a
export PYTHONUNBUFFERED=1

OUTDIR="outputs/h11/gold-standard-v2"
TILES_DIR="inputs/tiles_384"
MANIFEST="$TILES_DIR/full_evaluation_manifest.json"
RASTERS_DIR="inputs/rasters"
PROP_CONFIG="prompts/configs/detect_brief-text.json"
VERIFY_CONFIG="prompts/configs/verify_adversarial-text.json"
GT_FILE="inputs/vectors/references/mounds-reference.geojson"
BOUNDS_FILE="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%S")

echo "============================================="
echo "GS-v2 T=0.7 Recovery (single round)"
echo "Started: $(date -u)"
echo "============================================="

# ---------------------------------------------------------------------------
# Phase 1: Proposer recovery (per-pass)
# ---------------------------------------------------------------------------
for run in 1 2 3 4 5; do
    run_dir="$OUTDIR/proposer/detect_brief-text/run_$run"
    geojson_file=$(ls "$run_dir"/detections-detect_brief-text-3-flash-*.geojson | head -1)
    geojson_basename=$(basename "$geojson_file")
    meta_file="${geojson_file%.geojson}.meta.json"

    echo ""
    echo "--- Pass $run / 5: backing up meta.json ---"
    cp "$meta_file" "${meta_file}.pre-recovery-${TIMESTAMP}.backup"

    echo "--- Pass $run / 5: resuming with full manifest ---"
    python3 scripts/4_detect_mounds_batch.py \
        --config "$PROP_CONFIG" \
        --manifest "$MANIFEST" \
        --tiles-dir "$TILES_DIR" \
        --tile-size 384 \
        --temperature 0.7 \
        --thinking-level high \
        --mode realtime \
        --service-tier flex \
        --workers 30 \
        --max-retries 15 \
        --base-wait 30 \
        --output-dir "$run_dir" \
        --output "$geojson_basename" \
        --skip-intent-check \
        || echo "WARNING: Pass $run resume exited non-zero (residual failures expected)"

    echo "--- Pass $run / 5: merging recovery meta into backup ---"
    python3 scripts/merge_recovery_meta.py \
        --backup "${meta_file}.pre-recovery-${TIMESTAMP}.backup" \
        --recovery "$meta_file" \
        --output "$meta_file"
done

# ---------------------------------------------------------------------------
# Phase 2: Re-run consensus
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Phase 2: Re-running consensus (4-of-5)"
echo "============================================="
python3 scripts/merge_passes.py \
    --input-dir "$OUTDIR/proposer/detect_brief-text" \
    --output "$OUTDIR/consensus/consensus-4of5.geojson" \
    --threshold 4

# ---------------------------------------------------------------------------
# Phase 3: Extract crops for any NEW candidates
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Phase 3: Extracting crops for NEW candidates"
echo "============================================="
# Generic extractor (despite the t0.3 name) — re-extracts and merges into
# the existing crops/ directory and manifest. Note: GS-v2 rasters live
# in inputs/rasters/ (flat), unlike 55maps' Russian1981_32635/ subdir.
python3 scripts/55maps-t0.3-extract-new-candidates.py \
    --consensus "$OUTDIR/consensus/consensus-4of5.geojson" \
    --crops-dir "$OUTDIR/crops" \
    --rasters-dir "$RASTERS_DIR" \
    --tiles-dir "$TILES_DIR" \
    --padding 75

# ---------------------------------------------------------------------------
# Phase 4: Verifier cleanup (single attempt)
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Phase 4: Verifier cleanup (single attempt)"
echo "============================================="
python3 scripts/run_pv.py cleanup \
    --crops-dir "$OUTDIR/crops" \
    --verified-dir "$OUTDIR/verified-v1" \
    --verifier-config "$VERIFY_CONFIG" \
    --service-tier flex \
    --workers 20 \
    --max-attempts 1 \
    || echo "WARNING: verifier cleanup exited non-zero (residual failures expected)"

# ---------------------------------------------------------------------------
# Phase 5: Re-evaluate with --mcc (N=10K BCa)
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Phase 5: Re-evaluating with --mcc (N=10K BCa)"
echo "============================================="

# Rebuild verified_detections geojson from the (possibly extended)
# candidate manifest + (possibly patched) probabilities.json.
# Note: the GS-v2 verified file is `verified_detections_full-scope.geojson`
# (not `verified_detections.geojson` as on 55maps).
python3 scripts/55maps-t0.3-rebuild-verified-geojson.py \
    --crops-dir "$OUTDIR/crops" \
    --verified-dir "$OUTDIR/verified-v1" \
    --vote-threshold 4 \
    --prob-threshold 0.15 \
    --output "$OUTDIR/verified-v1/verified_detections_full-scope.geojson"

python3 scripts/evaluate_detections.py \
    --detections "$OUTDIR/verified-v1/verified_detections_full-scope.geojson" \
    --buffers 5 10 15 20 25 30 35 40 45 50 \
    --bootstrap 10000 --seed 42 \
    --ground-truth "$GT_FILE" \
    --bounds "$BOUNDS_FILE" \
    --output-dir "results/gold-standard-extended-buffer-sweep-era2" \
    --label "gold-standard-text-high-era2" \
    --mcc

echo ""
echo "============================================="
echo "Recovery complete: $(date -u)"
echo "============================================="
