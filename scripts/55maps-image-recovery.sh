#!/bin/bash
# 55-Map Image Generalisation — Single-round recovery for proposer failures
# =========================================================================
#
# Recovers the 26 tile-pass failures from the original 2026-04-18 image-modality
# generalisation run (8 + 3 + 8 + 2 + 5 across runs 1-5). This is the
# image-modality sibling of `55maps-t0.7-recovery.sh` (which itself recovered
# 160 failures across the T=0.7 text-HIGH sweep).
#
# Both runs use temperature 0.7 + thinking_level high; image differs by:
#  - proposer config: `library_plus-hp.json` (image-modality, +HP library)
#  - consensus vote_threshold: 3-of-5 (image), vs 4-of-5 (text-HIGH)
#  - all 26 failures are JSON parse errors that the new 3-tier parser fix
#    (commit e3aef6fa) should now recover, so per-tile retry storms should
#    be far smaller than the unpatched T=0.7 run.
#
# Single-round only (per Shawn's directive — stubborn failures are accepted).
# Re-runs proposer per-pass via the resume logic in 4_detect_mounds_batch.py
# (full manifest; the script auto-skips already-processed tiles), then merges
# the per-pass meta.json back into the original to preserve cost data.
# Then runs `run_pv.py cleanup` on the verifier output (single attempt).
#
# Note: in practice this driver is documented intent. The orchestrating
# Claude Code agent executes the stages individually with an N=10K BCa
# bootstrap re-evaluation (Stage 8) and dispatches the downstream
# §9-10 single-side and multi-side analyses separately.
#
# Usage:
#   nohup bash scripts/55maps-image-recovery.sh \
#     > outputs/55maps-image-generalisation/recovery.log 2>&1 &

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate
export PYTHONUNBUFFERED=1

OUTDIR="outputs/55maps-image-generalisation"
TILES_DIR="inputs/tiles_384_55maps"
MANIFEST="$TILES_DIR/full_evaluation_manifest.json"
PROP_CONFIG="prompts/configs/library_plus-hp.json"
VERIFY_CONFIG="prompts/configs/verify_adversarial-text.json"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%S")

echo "============================================="
echo "Image Recovery (single round)"
echo "Started: $(date -u)"
echo "============================================="

# ---------------------------------------------------------------------------
# Phase 1: Proposer recovery (per-pass)
# ---------------------------------------------------------------------------
for run in 1 2 3 4 5; do
    run_dir="$OUTDIR/proposer/library_plus-hp/run_$run"
    geojson_file=$(ls "$run_dir"/detections-library_plus-hp-3-flash-*.geojson | head -1)
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
echo "Phase 2: Re-running consensus (3-of-5)"
echo "============================================="
python3 scripts/merge_passes.py \
    --input-dir "$OUTDIR/proposer/library_plus-hp" \
    --output "$OUTDIR/consensus/consensus-3of5.geojson" \
    --threshold 3

# ---------------------------------------------------------------------------
# Phase 3: Extract crops for any NEW candidates
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Phase 3: Extracting crops for NEW candidates"
echo "============================================="
# Generic extractor (despite the t0.3 name) — re-extracts and merges into
# the existing crops/ directory and manifest.
python3 scripts/55maps-t0.3-extract-new-candidates.py \
    --consensus "$OUTDIR/consensus/consensus-3of5.geojson" \
    --crops-dir "$OUTDIR/crops" \
    --rasters-dir "inputs/rasters/Russian1981_32635" \
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
    --verified-dir "$OUTDIR/verified" \
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

# Rebuild verified_detections.geojson from the patched probabilities
python3 scripts/55maps-t0.3-rebuild-verified-geojson.py \
    --crops-dir "$OUTDIR/crops" \
    --verified-dir "$OUTDIR/verified" \
    --vote-threshold 3 \
    --prob-threshold 0.15 \
    --output "$OUTDIR/verified/verified_detections.geojson"

python3 scripts/evaluate_detections.py \
    --detections "$OUTDIR/verified/verified_detections.geojson" \
    --buffers 20 30 40 50 \
    --bootstrap 10000 --seed 42 \
    --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --output-dir "$OUTDIR/evaluation" \
    --label "55maps-image-generalisation" \
    --mcc

# ---------------------------------------------------------------------------
# Phase 6: Update cost_manifest
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Phase 6: Updating cost_manifest"
echo "============================================="
python3 scripts/run_generalisation.py aggregate-cost \
    --config configs/run-configs/55maps_image_generalisation.yaml \
    --resolved-config "$OUTDIR/resolved_config.yaml"

echo ""
echo "============================================="
echo "Recovery complete: $(date -u)"
echo "============================================="
