#!/bin/bash
# 55-Map T=0.3 Generalisation — Single-round recovery for proposer + verifier failures
# =====================================================================================
#
# Recovers the residual failures from the T=0.3 generalisation run:
#
#   - Proposer: 18 tile-pass failures across runs 1-5 (5+2+4+5+2)
#   - Verifier: 1 unverified candidate (the original run's "629 errors" in
#     finish_reason_counts were transient API errors that retried successfully
#     within the run; only candidate_05396 was missing from probabilities.json).
#
# Single-round only (per Shawn's directive — stubborn failures are accepted).
# Re-runs proposer per-pass via the resume logic in 4_detect_mounds_batch.py
# (full manifest; the script auto-skips already-processed tiles), then merges
# the per-pass meta.json back into the original to preserve cost data.
# Then runs `run_pv.py cleanup` on the verifier output (single attempt).
#
# This driver was used as the documented intent for the 2026-04-27 recovery
# session; in practice the phases were executed manually with adjustments
# (e.g. parallel proposer passes, the new candidate from re-run consensus
# was extracted via 55maps-t0.3-extract-new-candidates.py before verifier
# cleanup picked it up alongside the missing original candidate).
#
# Usage:
#   nohup bash scripts/55maps-t0.3-recovery.sh \
#     > outputs/55maps-text-high-t0.3-generalisation/recovery.log 2>&1 &

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate
export PYTHONUNBUFFERED=1

OUTDIR="outputs/55maps-text-high-t0.3-generalisation"
TILES_DIR="inputs/tiles_384_55maps"
MANIFEST="$TILES_DIR/full_evaluation_manifest.json"
PROP_CONFIG="prompts/configs/detect_brief-text.json"
VERIFY_CONFIG="prompts/configs/verify_adversarial-text.json"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%S")

echo "============================================="
echo "T=0.3 Recovery (single round)"
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
        --temperature 0.3 \
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
# We re-run extract pointing to a temp dir, then merge new candidates into
# the existing crops/ directory and manifest.
python3 scripts/55maps-t0.3-extract-new-candidates.py \
    --consensus "$OUTDIR/consensus/consensus-4of5.geojson" \
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
# Phase 5: Re-evaluate with --mcc
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Phase 5: Re-evaluating with --mcc"
echo "============================================="

# Rebuild verified_detections.geojson from the patched probabilities
python3 scripts/55maps-t0.3-rebuild-verified-geojson.py \
    --crops-dir "$OUTDIR/crops" \
    --verified-dir "$OUTDIR/verified" \
    --vote-threshold 4 \
    --prob-threshold 0.15 \
    --output "$OUTDIR/verified/verified_detections.geojson"

python3 scripts/evaluate_detections.py \
    --detections "$OUTDIR/verified/verified_detections.geojson" \
    --buffers 20 30 40 50 \
    --bootstrap 1000 --seed 42 \
    --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --output-dir "$OUTDIR/evaluation" \
    --label "55maps-text-high-t0.3-generalisation" \
    --mcc

# ---------------------------------------------------------------------------
# Phase 6: Update cost_manifest
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Phase 6: Updating cost_manifest"
echo "============================================="
python3 scripts/run_generalisation.py aggregate-cost \
    --config configs/runs/55maps-text-high-t0.3-generalisation.yaml \
    --resolved-config "$OUTDIR/resolved_config.yaml"

echo ""
echo "============================================="
echo "Recovery complete: $(date -u)"
echo "============================================="
