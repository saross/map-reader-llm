#!/bin/bash
# Sapphire PV Analysis — Wave 1 + Wave 3 Results
# ================================================
# Step 1: Derive vote threshold results from 1-of-N union verifier runs
# Step 2: Evaluate PV sweeps with bootstrap CIs
# Step 3: Evaluate single-pass T=0.0 rerun
#
# Usage:
#   ssh sapphire 'cd ~/Code/map-reader-llm && source .venv/bin/activate && \
#       nohup bash scripts/sapphire-pv-analysis.sh \
#       > results/sapphire-pv-analysis.log 2>&1 &'

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate

PV_BASE="outputs/h11/pv-diag-384"
RESULTS_BASE="results/h11-384-pv-diagnostic"
BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

echo "============================================="
echo "Sapphire PV Analysis"
echo "Started: $(date)"
echo "============================================="
echo ""

# -----------------------------------------------
# Step 1: Derive vote threshold results
# -----------------------------------------------
echo "=== Step 1: Derive Vote Threshold Results ==="
echo ""

# flash-high-image-1of5 (pool=5)
echo "--- flash-high-image (pool=5) ---"
echo "Started: $(date)"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$PV_BASE/consensus/flash-high-image-1of5.geojson" \
    --probabilities "$PV_BASE/verified/flash-high-image-1of5/probabilities.json" \
    --manifest "$PV_BASE/crops/flash-high-image-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$PV_BASE/verified" \
    --prefix flash-high-image
echo "Completed: $(date)"
echo ""

# flash-high-text-1of10 (pool=10)
echo "--- flash-high-text (pool=10) ---"
echo "Started: $(date)"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$PV_BASE/consensus/flash-high-text-1of10.geojson" \
    --probabilities "$PV_BASE/verified/flash-high-text-1of10/probabilities.json" \
    --manifest "$PV_BASE/crops/flash-high-text-1of10/candidate_manifest.json" \
    --pool-size 10 \
    --output-dir "$PV_BASE/verified" \
    --prefix flash-high-text
echo "Completed: $(date)"
echo ""

# flash-high-text-1of30 (pool=30)
echo "--- flash-high-text (pool=30) ---"
echo "Started: $(date)"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$PV_BASE/consensus/flash-high-text-1of30.geojson" \
    --probabilities "$PV_BASE/verified/flash-high-text-1of30/probabilities.json" \
    --manifest "$PV_BASE/crops/flash-high-text-1of30/candidate_manifest.json" \
    --pool-size 30 \
    --output-dir "$PV_BASE/verified" \
    --prefix flash-high-text
echo "Completed: $(date)"
echo ""

# flash-minimal-text-t07-1of5 (pool=5)
echo "--- flash-minimal-text-t07 (pool=5) ---"
echo "Started: $(date)"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$PV_BASE/consensus/flash-minimal-text-t07-1of5.geojson" \
    --probabilities "$PV_BASE/verified/flash-minimal-text-t07-1of5/probabilities.json" \
    --manifest "$PV_BASE/crops/flash-minimal-text-t07-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$PV_BASE/verified" \
    --prefix flash-minimal-text-t07
echo "Completed: $(date)"
echo ""

echo "=== Step 1 complete: $(date) ==="
echo ""

# -----------------------------------------------
# Step 2: Evaluate PV sweeps with bootstrap CIs
# -----------------------------------------------
echo "=== Step 2: PV Threshold Sweeps ==="
echo ""

# Evaluate each derived condition
# flash-high-image: 1-of-5 through 5-of-5
for x in 1 2 3 4 5; do
    dir="$PV_BASE/verified/flash-high-image-${x}of5"
    if [ -d "$dir" ] && [ -f "$dir/probabilities.json" ]; then
        echo "--- flash-high-image ${x}-of-5 ---"
        echo "Started: $(date)"
        python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
            --probabilities "$dir/probabilities.json" \
            --manifest "$dir/candidate_manifest.json" \
            --output-dir "$RESULTS_BASE/flash-high-image-${x}of5"
        echo "Completed: $(date)"
        echo ""
    fi
done

# flash-high-text: 1-of-10 through 10-of-10
for x in $(seq 1 10); do
    dir="$PV_BASE/verified/flash-high-text-${x}of10"
    if [ -d "$dir" ] && [ -f "$dir/probabilities.json" ]; then
        echo "--- flash-high-text ${x}-of-10 ---"
        echo "Started: $(date)"
        python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
            --probabilities "$dir/probabilities.json" \
            --manifest "$dir/candidate_manifest.json" \
            --output-dir "$RESULTS_BASE/flash-high-text-${x}of10"
        echo "Completed: $(date)"
        echo ""
    fi
done

# flash-high-text: 1-of-30 through 30-of-30
for x in $(seq 1 30); do
    dir="$PV_BASE/verified/flash-high-text-${x}of30"
    if [ -d "$dir" ] && [ -f "$dir/probabilities.json" ]; then
        echo "--- flash-high-text ${x}-of-30 ---"
        echo "Started: $(date)"
        python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
            --probabilities "$dir/probabilities.json" \
            --manifest "$dir/candidate_manifest.json" \
            --output-dir "$RESULTS_BASE/flash-high-text-${x}of30"
        echo "Completed: $(date)"
        echo ""
    fi
done

# flash-minimal-text-t07: 1-of-5 through 5-of-5
for x in 1 2 3 4 5; do
    dir="$PV_BASE/verified/flash-minimal-text-t07-${x}of5"
    if [ -d "$dir" ] && [ -f "$dir/probabilities.json" ]; then
        echo "--- flash-minimal-text-t07 ${x}-of-5 ---"
        echo "Started: $(date)"
        python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
            --probabilities "$dir/probabilities.json" \
            --manifest "$dir/candidate_manifest.json" \
            --output-dir "$RESULTS_BASE/flash-minimal-text-t07-${x}of5"
        echo "Completed: $(date)"
        echo ""
    fi
done

echo "=== Step 2 complete: $(date) ==="
echo ""

# -----------------------------------------------
# Step 3: Single-pass T=0.0 consensus analysis
# -----------------------------------------------
echo "=== Step 3: Single-Pass T=0.0 Analysis ==="
echo ""

echo "--- Consensus sweep (N=5, N=10 from 10 runs) ---"
echo "Started: $(date)"
python3 scripts/analyse_consensus_sweep.py \
    --study-dir outputs/retest/h11-single-pass-384-t0 \
    --output-dir results/h11-384-single-pass-t0-rerun \
    --temperatures brief-text-t0 \
    --pool-sizes 5 10 \
    --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson
echo "Completed: $(date)"
echo ""

echo "============================================="
echo "All PV analyses complete: $(date)"
echo "============================================="
