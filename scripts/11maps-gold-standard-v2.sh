#!/bin/bash
# Gold-Standard Pipeline Recreation with v2 Verifier
# ===================================================
# Recreates the gold-standard 4-of-5 consensus pipeline on the 11-map
# validation set and runs both v1 and v2 verifiers for comparison.
#
# Purpose: Test whether the v2 verifier improvements (spot height size
# criterion + water colour exclusion) transfer to the detect_brief-text
# proposer's optimal output, not just the propose_brief-text E47 data.
#
# Stages:
#   1. 5 proposer passes: detect_brief-text + HIGH + T=0.7 via Flex
#   2. Consensus merge: 4-of-5 voting, 20m clustering
#   3. Crop extraction: from 11-map rasters
#   4. v1 verifier: verify_adversarial-text (baseline)
#   5. v2 verifier: verify_adversarial-text_v2 (comparison)
#
# Usage:
#   nohup bash scripts/11maps-gold-standard-v2.sh \
#     > outputs/h11/gold-standard-v2/pipeline.log 2>&1 &

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate
export PYTHONUNBUFFERED=1

OUTDIR="outputs/h11/gold-standard-v2"
TILES_DIR="inputs/tiles_384"
MANIFEST="$TILES_DIR/full_evaluation_manifest.json"
PROPOSER_CONFIG="prompts/configs/detect_brief-text.json"
VERIFIER_V1="prompts/configs/verify_adversarial-text.json"
VERIFIER_V2="prompts/configs/verify_adversarial-text_v2.json"
# Note: 11-map rasters use a different directory structure than 55-map.
# The original rasters live in inputs/rasters/ directly.
RASTERS_DIR="inputs/rasters"

mkdir -p "$OUTDIR"

echo "============================================="
echo "Gold-Standard Pipeline Recreation + v2"
echo "Started: $(date)"
echo "============================================="
echo ""

# ─────────────────────────────────────────────────
# Stage 1: Proposer — 5 Flex Runs
# ─────────────────────────────────────────────────
echo "=== Stage 1: Proposer (5 runs via Flex) ==="

for run in 1 2 3 4 5; do
    echo ""
    echo "--- Proposer run $run/5 ---"
    echo "Started: $(date)"
    python3 scripts/4_detect_mounds_batch.py \
        --config "$PROPOSER_CONFIG" \
        --manifest "$MANIFEST" \
        --tiles-dir "$TILES_DIR" \
        --tile-size 384 \
        --temperature 0.7 \
        --thinking-level high \
        --mode realtime \
        --service-tier flex \
        --workers 30 \
        --max-retries 8 \
        --base-wait 10 \
        --output-dir "$OUTDIR/proposer/detect_brief-text/run_$run" \
        || echo "WARNING: Proposer run $run exited non-zero"
    echo "Completed: $(date)"
done

echo ""
echo "=== Stage 1 complete: $(date) ==="
echo ""

# ─────────────────────────────────────────────────
# Stage 2: Consensus Voting (4-of-5)
# ─────────────────────────────────────────────────
echo "=== Stage 2: Consensus (4-of-5 voting) ==="
mkdir -p "$OUTDIR/consensus"
python3 scripts/merge_passes.py \
    --input-dir "$OUTDIR/proposer/detect_brief-text" \
    --output "$OUTDIR/consensus/consensus-4of5.geojson" \
    --threshold 4
echo "=== Stage 2 complete: $(date) ==="
echo ""

# ─────────────────────────────────────────────────
# Stage 3: Crop Extraction
# ─────────────────────────────────────────────────
echo "=== Stage 3: Crop Extraction ==="
python3 scripts/run_pv.py extract \
    --proposer "$OUTDIR/consensus/consensus-4of5.geojson" \
    --output-dir "$OUTDIR/crops" \
    --rasters-dir "$RASTERS_DIR" \
    --tiles-dir "$TILES_DIR" \
    --padding 75
echo "=== Stage 3 complete: $(date) ==="
echo ""

# ─────────────────────────────────────────────────
# Stage 4: v1 Verifier
# ─────────────────────────────────────────────────
echo "=== Stage 4: v1 Verifier (adversarial-text, baseline) ==="
python3 scripts/run_pv.py verify \
    --crops-dir "$OUTDIR/crops" \
    --verifier-config "$VERIFIER_V1" \
    --output-dir "$OUTDIR/verified-v1" \
    --mode realtime \
    --service-tier flex \
    --workers 20 \
    --no-strict
echo "=== Stage 4 complete: $(date) ==="
echo ""

# ─────────────────────────────────────────────────
# Stage 5: v2 Verifier
# ─────────────────────────────────────────────────
echo "=== Stage 5: v2 Verifier (adversarial-text_v2, comparison) ==="
python3 scripts/run_pv.py verify \
    --crops-dir "$OUTDIR/crops" \
    --verifier-config "$VERIFIER_V2" \
    --output-dir "$OUTDIR/verified-v2" \
    --mode realtime \
    --service-tier flex \
    --workers 20 \
    --no-strict
echo "=== Stage 5 complete: $(date) ==="
echo ""

echo "============================================="
echo "Gold-Standard v2 Pipeline COMPLETE"
echo "Finished: $(date)"
echo "============================================="
