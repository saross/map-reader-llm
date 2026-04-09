#!/bin/bash
# 55-Map Generalisation Run — Overnight Pipeline
# ================================================
# Runs the full proposer-verifier pipeline for the 55-map generalisation
# study. Designed to run unattended overnight.
#
# Stages:
#   1. Proposer: 5 batch runs (42,705 API calls, ~$28 batch pricing)
#   2. Consensus: 4-of-5 voting, 20m clustering
#   3. Crop extraction: 150x150 px from Russian1981 rasters
#   4. Verifier: adversarial-text v1, batch mode (~$0.50-1.00)
#
# Usage:
#   nohup bash scripts/55maps-overnight.sh \
#       > outputs/55maps-generalisation/overnight.log 2>&1 &
#
# Configuration frozen to match gold standard (F1=0.864 at 20m):
#   Proposer: detect_brief-text.json, Flash HIGH, T=0.7
#   Verifier: verify_adversarial-text.json (v1), Flash minimal, T=0.0

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate

# Disable Python output buffering so log is readable in real time
export PYTHONUNBUFFERED=1

OUTDIR="outputs/55maps-generalisation"
TILES_DIR="inputs/tiles_384_55maps"
MANIFEST="$TILES_DIR/full_evaluation_manifest.json"
PROPOSER_CONFIG="prompts/configs/detect_brief-text.json"
VERIFIER_CONFIG="prompts/configs/verify_adversarial-text.json"
RASTERS_DIR="inputs/rasters/Russian1981_32635"

mkdir -p "$OUTDIR"

echo "============================================="
echo "55-Map Generalisation Run"
echo "Started: $(date)"
echo "Git commit: $(git rev-parse --short HEAD)"
echo "============================================="
echo ""

# ─────────────────────────────────────────────────
# Stage 1: Proposer — 5 Batch Runs
# ─────────────────────────────────────────────────
echo "=== Stage 1: Proposer (5 batch runs) ==="
echo ""

proposer_failed=0

for run in 1 2 3 4 5; do
    echo "--- Proposer run $run/5 ---"
    echo "Started: $(date)"
    if python3 scripts/4_detect_mounds_batch.py \
        --config "$PROPOSER_CONFIG" \
        --manifest "$MANIFEST" \
        --tiles-dir "$TILES_DIR" \
        --tile-size 384 \
        --temperature 0.7 \
        --thinking-level high \
        --mode batch \
        --run "$run" \
        --max-batch-tiles 4000 \
        --output-dir "$OUTDIR/proposer"; then
        echo "Completed run $run: $(date)"
    else
        echo "WARNING: Proposer run $run exited with error: $(date)"
        proposer_failed=$((proposer_failed + 1))
    fi
    echo ""
done

echo "=== Stage 1 complete: $(date) ==="
echo "Proposer runs failed: $proposer_failed"
echo ""

if [ "$proposer_failed" -ge 3 ]; then
    echo "ABORT: $proposer_failed/5 proposer runs failed. Stopping pipeline."
    exit 1
fi

# ─────────────────────────────────────────────────
# Stage 2: Consensus Voting (4-of-5)
# ─────────────────────────────────────────────────
echo "=== Stage 2: Consensus (4-of-5 voting) ==="
echo "Started: $(date)"

PROPOSER_DIR="$OUTDIR/proposer/detect_brief-text"
CONSENSUS_DIR="$OUTDIR/consensus"
mkdir -p "$CONSENSUS_DIR"

python3 scripts/merge_passes.py \
    --input-dir "$PROPOSER_DIR" \
    --output "$CONSENSUS_DIR/consensus-4of5.geojson" \
    --threshold 4

consensus_count=$(python3 -c "
import json
with open('$CONSENSUS_DIR/consensus-4of5.geojson') as f:
    data = json.load(f)
print(len(data.get('features', [])))
")
echo "Consensus candidates: $consensus_count"
echo "=== Stage 2 complete: $(date) ==="
echo ""

if [ "$consensus_count" -eq 0 ]; then
    echo "ABORT: Zero consensus candidates. Something is wrong."
    exit 1
fi

# ─────────────────────────────────────────────────
# Stage 3: Crop Extraction
# ─────────────────────────────────────────────────
echo "=== Stage 3: Crop Extraction ==="
echo "Started: $(date)"

python3 scripts/run_pv.py extract \
    --proposer "$CONSENSUS_DIR/consensus-4of5.geojson" \
    --output-dir "$OUTDIR/crops" \
    --rasters-dir "$RASTERS_DIR" \
    --tiles-dir "$TILES_DIR" \
    --padding 75

echo "=== Stage 3 complete: $(date) ==="
echo ""

# ─────────────────────────────────────────────────
# Stage 4: Verifier — Batch API
# ─────────────────────────────────────────────────
echo "=== Stage 4: Verifier (adversarial-text v1, batch) ==="
echo "Started: $(date)"

python3 scripts/run_pv.py verify \
    --crops-dir "$OUTDIR/crops" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$OUTDIR/verified" \
    --mode batch

echo "=== Stage 4 complete: $(date) ==="
echo ""

# ─────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────
echo "============================================="
echo "55-Map Generalisation Run COMPLETE"
echo "Finished: $(date)"
echo ""
echo "Outputs:"
echo "  Proposer: $PROPOSER_DIR/run_{1..5}/"
echo "  Consensus: $CONSENSUS_DIR/consensus-4of5.geojson ($consensus_count candidates)"
echo "  Crops: $OUTDIR/crops/"
echo "  Verified: $OUTDIR/verified/"
echo ""
echo "Next step: Run evaluation (Stage 5)"
echo "  python3 scripts/analyse_pv_buffer_sensitivity.py \\"
echo "    --probabilities $OUTDIR/verified/probabilities.json \\"
echo "    --manifest $OUTDIR/crops/candidate_manifest.json \\"
echo "    --threshold 0.15 \\"
echo "    --output-dir results/55maps-generalisation \\"
echo "    --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \\"
echo "    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \\"
echo "    --buffers 20 30 40 50 \\"
echo "    --bootstrap 1000 --seed 42"
echo "============================================="
