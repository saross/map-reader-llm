#!/bin/bash
# Sapphire Pro Verifier Analysis
# ================================
# Derive vote thresholds + evaluate sweeps for all 7 completed Pro verifier runs.
#
# Usage:
#   ssh sapphire 'cd ~/Code/map-reader-llm && source .venv/bin/activate && \
#       nohup bash scripts/sapphire-pro-verifier-analysis.sh \
#       > results/sapphire-pro-verifier-analysis.log 2>&1 &'

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate

PV_BASE="outputs/h11/pv-diag-384"
RESULTS_BASE="results/h11-384-pv-diagnostic"
BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

echo "============================================="
echo "Pro Verifier Analysis"
echo "Started: $(date)"
echo "============================================="
echo ""

# -----------------------------------------------
# Step 1: Derive vote thresholds for consensus conditions
# -----------------------------------------------
echo "=== Step 1: Derive Vote Thresholds ==="
echo ""

# flash-high-text-1of5 + Pro verifier (pool=5)
echo "--- derive flash-high-text + Pro verifier (pool=5) ---"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$PV_BASE/consensus/flash-high-text-1of5.geojson" \
    --probabilities "$PV_BASE/verified/flash-high-text-1of5-pro-verifier/probabilities.json" \
    --manifest "$PV_BASE/crops/flash-high-text-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$PV_BASE/verified" \
    --prefix flash-high-text-pro-verifier
echo ""

# pro-high-text-1of5 + Pro verifier (pool=5)
echo "--- derive pro-high-text + Pro verifier (pool=5) ---"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$PV_BASE/consensus/pro-high-text-1of5.geojson" \
    --probabilities "$PV_BASE/verified/pro-high-text-1of5-pro-verifier/probabilities.json" \
    --manifest "$PV_BASE/crops/pro-high-text-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$PV_BASE/verified" \
    --prefix pro-high-text-pro-verifier
echo ""

# pro-high-image-1of5 + Pro verifier (pool=5)
echo "--- derive pro-high-image + Pro verifier (pool=5) ---"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$PV_BASE/consensus/pro-high-image-1of5.geojson" \
    --probabilities "$PV_BASE/verified/pro-high-image-1of5-pro-verifier/probabilities.json" \
    --manifest "$PV_BASE/crops/pro-high-image-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$PV_BASE/verified" \
    --prefix pro-high-image-pro-verifier
echo ""

echo "=== Step 1 complete: $(date) ==="
echo ""

# -----------------------------------------------
# Step 2: Threshold sweeps — single-pass baselines
# -----------------------------------------------
echo "=== Step 2: Baseline Sweeps ==="
echo ""

for cond in text-baseline-pro-verifier image-baseline-pro-verifier \
            pro-medium-text-baseline-pro-verifier pro-medium-image-baseline-pro-verifier; do
    dir="$PV_BASE/verified/$cond"
    if [ -f "$dir/probabilities.json" ]; then
        echo "--- $cond ---"
        echo "Started: $(date)"
        python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
            --probabilities "$dir/probabilities.json" \
            --manifest "$dir/candidate_manifest.json" \
            --output-dir "$RESULTS_BASE/$cond"
        echo "Completed: $(date)"
        echo ""
    fi
done

echo "=== Step 2 complete: $(date) ==="
echo ""

# -----------------------------------------------
# Step 3: Threshold sweeps — consensus conditions (all x-of-5)
# -----------------------------------------------
echo "=== Step 3: Consensus Sweeps ==="
echo ""

# flash-high-text + Pro verifier: x=1 to 5
for x in 1 2 3 4 5; do
    dir="$PV_BASE/verified/flash-high-text-pro-verifier-${x}of5"
    if [ -d "$dir" ] && [ -f "$dir/probabilities.json" ]; then
        echo "--- flash-high-text-pro-verifier ${x}-of-5 ---"
        echo "Started: $(date)"
        python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
            --probabilities "$dir/probabilities.json" \
            --manifest "$dir/candidate_manifest.json" \
            --output-dir "$RESULTS_BASE/flash-high-text-pro-verifier-${x}of5"
        echo "Completed: $(date)"
        echo ""
    fi
done

# pro-high-text + Pro verifier: x=1 to 5
for x in 1 2 3 4 5; do
    dir="$PV_BASE/verified/pro-high-text-pro-verifier-${x}of5"
    if [ -d "$dir" ] && [ -f "$dir/probabilities.json" ]; then
        echo "--- pro-high-text-pro-verifier ${x}-of-5 ---"
        echo "Started: $(date)"
        python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
            --probabilities "$dir/probabilities.json" \
            --manifest "$dir/candidate_manifest.json" \
            --output-dir "$RESULTS_BASE/pro-high-text-pro-verifier-${x}of5"
        echo "Completed: $(date)"
        echo ""
    fi
done

# pro-high-image + Pro verifier: x=1 to 5
for x in 1 2 3 4 5; do
    dir="$PV_BASE/verified/pro-high-image-pro-verifier-${x}of5"
    if [ -d "$dir" ] && [ -f "$dir/probabilities.json" ]; then
        echo "--- pro-high-image-pro-verifier ${x}-of-5 ---"
        echo "Started: $(date)"
        python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
            --probabilities "$dir/probabilities.json" \
            --manifest "$dir/candidate_manifest.json" \
            --output-dir "$RESULTS_BASE/pro-high-image-pro-verifier-${x}of5"
        echo "Completed: $(date)"
        echo ""
    fi
done

echo "============================================="
echo "All Pro verifier analyses complete: $(date)"
echo "============================================="
