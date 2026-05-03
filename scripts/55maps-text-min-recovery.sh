#!/bin/bash
# 55-Map Text-MIN Generalisation — Single-round recovery for proposer failures
# ============================================================================
#
# Recovers the 124 tile-pass failures (113 unique tiles) from the original
# 2026-04-18 text-MIN generalisation run (22 + 25 + 32 + 26 + 19 across runs
# 1-5). This is the MIN-thinking sibling of `55maps-t0.7-recovery.sh` (which
# itself recovered the 160 text-HIGH T=0.7 failures).
#
# Single-round only (per Shawn's directive — stubborn failures are accepted).
# Re-runs the proposer per-pass via the resume logic in
# `4_detect_mounds_batch.py` (full manifest; the script auto-skips already-
# processed tiles), then merges the per-pass meta.json back into the original
# to preserve cost data. Then runs `run_pv.py cleanup` on the verifier output
# (single attempt).
#
# Key differences from the T=0.7 (text-HIGH) driver:
#   - Output dir:           outputs/55maps-text-min-generalisation/
#   - thinking_level:       minimal (was: high) — much lower per-tile cost
#   - Aggregate-cost YAML:  configs/run-configs/55maps_text_min_generalisation.yaml
#   - Recovery log path:    outputs/55maps-text-min-generalisation/recovery.log
#   - Evaluation label:     55maps-text-min-generalisation
#
# Note: in practice this driver is documented intent. The orchestrating
# Claude Code agent executes the stages individually with an N=10K BCa
# bootstrap re-evaluation (Stage 8) and dispatches the downstream
# §9-10 single-side and multi-side analyses separately.
#
# Usage:
#   nohup bash scripts/55maps-text-min-recovery.sh \
#     > outputs/55maps-text-min-generalisation/recovery.log 2>&1 &

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate
export PYTHONUNBUFFERED=1

OUTDIR="outputs/55maps-text-min-generalisation"
TILES_DIR="inputs/tiles_384_55maps"
MANIFEST="$TILES_DIR/full_evaluation_manifest.json"
PROP_CONFIG="prompts/configs/detect_brief-text.json"
VERIFY_CONFIG="prompts/configs/verify_adversarial-text.json"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%S")

echo "============================================="
echo "Text-MIN-thinking Recovery (single round)"
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
        --thinking-level minimal \
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
    --vote-threshold 4 \
    --prob-threshold 0.15 \
    --output "$OUTDIR/verified/verified_detections.geojson"

python3 scripts/evaluate_detections.py \
    --detections "$OUTDIR/verified/verified_detections.geojson" \
    --buffers 20 30 40 50 \
    --bootstrap 10000 --seed 42 \
    --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --output-dir "$OUTDIR/evaluation" \
    --label "55maps-text-min-generalisation" \
    --mcc

# ---------------------------------------------------------------------------
# Phase 6: Update cost_manifest
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "Phase 6: Updating cost_manifest"
echo "============================================="
python3 scripts/run_generalisation.py aggregate-cost \
    --config configs/run-configs/55maps_text_min_generalisation.yaml \
    --resolved-config "$OUTDIR/resolved_config.yaml"

echo ""
echo "============================================="
echo "Recovery complete: $(date -u)"
echo "============================================="
