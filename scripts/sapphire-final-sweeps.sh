#!/bin/bash
# Sapphire Final Sweeps — All New Verifier Conditions
# ====================================================
# 4 direct baseline sweeps + 6 derive operations + 30 consensus sweeps = 34 total.
#
# Usage:
#   ssh sapphire "cd ~/Code/map-reader-llm && source .venv/bin/activate && \
#       nohup bash scripts/sapphire-final-sweeps.sh \
#       > results/sapphire-final-sweeps.log 2>&1 & echo PID: \$!"

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate

PV_BASE="outputs/h11/pv-diag-384"
VERIFIED="$PV_BASE/verified"
CROPS="$PV_BASE/crops"
CONSENSUS="$PV_BASE/consensus"
RESULTS="results/h11-384-pv-diagnostic"
BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

echo "============================================="
echo "Final Evaluation Sweeps"
echo "Started: $(date)"
echo "============================================="
echo ""

# -----------------------------------------------
# Step 1: Direct sweeps — 4 single-pass baselines
# -----------------------------------------------
echo "=== Step 1: Baseline Sweeps (4 conditions) ==="
echo ""

declare -A BASELINES=(
    ["text-baseline-pro-verifier"]="text-baseline"
    ["image-baseline-pro-verifier"]="image-baseline"
    ["pro-medium-text-baseline-pro-verifier"]="pro-medium-text-baseline"
    ["pro-medium-image-baseline-pro-verifier"]="pro-medium-image-baseline"
)

for cond in "${!BASELINES[@]}"; do
    crops_name="${BASELINES[$cond]}"
    echo "--- $cond ---"
    echo "Started: $(date)"
    python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
        --probabilities "$VERIFIED/$cond/probabilities.json" \
        --manifest "$CROPS/$crops_name/candidate_manifest.json" \
        --output-dir "$RESULTS/$cond"
    echo "Completed: $(date)"
    echo ""
done

echo "=== Step 1 complete: $(date) ==="
echo ""

# -----------------------------------------------
# Step 2: Derive vote thresholds — 6 consensus conditions
# -----------------------------------------------
echo "=== Step 2: Derive Vote Thresholds (6 × 5 = 30 conditions) ==="
echo ""

# flash-high-text-1of5 + Pro verifier
echo "--- derive: flash-high-text + Pro verifier ---"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$CONSENSUS/flash-high-text-1of5.geojson" \
    --probabilities "$VERIFIED/flash-high-text-1of5-pro-verifier/probabilities.json" \
    --manifest "$CROPS/flash-high-text-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$VERIFIED" \
    --prefix flash-high-text-pro-vf
echo ""

# flash-high-text-1of5 + Flash medium verifier
echo "--- derive: flash-high-text + Flash medium verifier ---"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$CONSENSUS/flash-high-text-1of5.geojson" \
    --probabilities "$VERIFIED/flash-high-text-1of5-flash-medium-verifier/probabilities.json" \
    --manifest "$CROPS/flash-high-text-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$VERIFIED" \
    --prefix flash-high-text-medium-vf
echo ""

# flash-high-text-1of5 + Flash HIGH verifier
echo "--- derive: flash-high-text + Flash HIGH verifier ---"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$CONSENSUS/flash-high-text-1of5.geojson" \
    --probabilities "$VERIFIED/flash-high-text-1of5-flash-high-verifier/probabilities.json" \
    --manifest "$CROPS/flash-high-text-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$VERIFIED" \
    --prefix flash-high-text-high-vf
echo ""

# pro-high-text-1of5 + Pro verifier
echo "--- derive: pro-high-text + Pro verifier ---"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$CONSENSUS/pro-high-text-1of5.geojson" \
    --probabilities "$VERIFIED/pro-high-text-1of5-pro-verifier/probabilities.json" \
    --manifest "$CROPS/pro-high-text-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$VERIFIED" \
    --prefix pro-high-text-pro-vf
echo ""

# pro-high-text-1of5 + Flash minimal verifier
echo "--- derive: pro-high-text + Flash minimal verifier ---"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$CONSENSUS/pro-high-text-1of5.geojson" \
    --probabilities "$VERIFIED/pro-high-text-1of5-flash-minimal-verifier/probabilities.json" \
    --manifest "$CROPS/pro-high-text-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$VERIFIED" \
    --prefix pro-high-text-flash-min-vf
echo ""

# pro-high-image-1of5 + Pro verifier
echo "--- derive: pro-high-image + Pro verifier ---"
python3 scripts/derive_vote_threshold_results.py \
    --consensus "$CONSENSUS/pro-high-image-1of5.geojson" \
    --probabilities "$VERIFIED/pro-high-image-1of5-pro-verifier/probabilities.json" \
    --manifest "$CROPS/pro-high-image-1of5/candidate_manifest.json" \
    --pool-size 5 \
    --output-dir "$VERIFIED" \
    --prefix pro-high-image-pro-vf
echo ""

echo "=== Step 2 complete: $(date) ==="
echo ""

# -----------------------------------------------
# Step 3: Threshold sweeps — all 30 derived conditions
# -----------------------------------------------
echo "=== Step 3: Consensus Sweeps (30 conditions) ==="
echo ""

for prefix in flash-high-text-pro-vf flash-high-text-medium-vf flash-high-text-high-vf \
              pro-high-text-pro-vf pro-high-text-flash-min-vf pro-high-image-pro-vf; do
    for x in 1 2 3 4 5; do
        dir="$VERIFIED/${prefix}-${x}of5"
        if [ -d "$dir" ] && [ -f "$dir/probabilities.json" ]; then
            echo "--- ${prefix}-${x}of5 ---"
            echo "Started: $(date)"
            python3 scripts/evaluate_pv_results.py --bounds "$BOUNDS" sweep \
                --probabilities "$dir/probabilities.json" \
                --manifest "$dir/candidate_manifest.json" \
                --output-dir "$RESULTS/${prefix}-${x}of5"
            echo "Completed: $(date)"
            echo ""
        else
            echo "SKIP: ${prefix}-${x}of5 (not found)"
        fi
    done
done

echo "============================================="
echo "All sweeps complete: $(date)"
echo "============================================="
