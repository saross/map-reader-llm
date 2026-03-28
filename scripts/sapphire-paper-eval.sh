#!/bin/bash
# Sapphire Paper Evaluation
# ==========================
# Comprehensive multi-buffer evaluation of all paper-critical conditions.
# Computes F1, Precision, Recall with 95% bootstrap CIs at 20, 30, 40, 50 m
# spatial buffer distances. All conditions evaluated on full 487-tile bounds
# (435 reference mounds) for consistency.
#
# Usage:
#   ssh sapphire 'cd ~/Code/map-reader-llm && source .venv/bin/activate && \
#       nohup bash scripts/sapphire-paper-eval.sh \
#       > results/paper-eval/sapphire-eval.log 2>&1 &'
#
# Estimated runtime: ~20-30 minutes on sapphire (24 cores).

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate

BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
OUT_DIR="results/paper-eval"
BOOTSTRAP=1000
SEED=42

mkdir -p "$OUT_DIR"

echo "============================================="
echo "Sapphire Paper Evaluation"
echo "Started: $(date)"
echo "Bounds: $BOUNDS (487 tiles, 435 mounds)"
echo "Bootstrap: $BOOTSTRAP iterations, seed=$SEED"
echo "============================================="
echo ""

# ─────────────────────────────────────────────────
# Section A: Consensus Sweep Evaluations
# ─────────────────────────────────────────────────
# Each condition is evaluated at 4 buffer distances.
# Format: study_dir|label|temperatures|pool_sizes
echo "=== Section A: Consensus Sweeps ==="
echo ""

declare -a CONSENSUS_CONDITIONS=(
    "outputs/h11/pv-diag-384/flash-high-text-n5|flash-high-text|text-t0.7|5 10 30"
    "outputs/h11/pv-diag-384/flash-high-image-n5|flash-high-image|image-t0.7|5 10"
    "outputs/h11/pv-diag-384/pro-high-text-n5|pro-high-text|text-t0.7|5"
    "outputs/h11/pv-diag-384/pro-high-image-n5|pro-high-image|image-t0.7|5"
    "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07|flash-min-text-t07|text-t0.7|5 10 30"
    "outputs/h11/consensus-384-UNINTENDED-T1.0|flash-min-text-t10|384|5 10 30"
    "outputs/h11/pv-diag-384/image-n5|flash-min-image|image-t0.7|5 10"
    "outputs/retest/h11-single-pass-384-t0|single-pass-t0|brief-text-t0|5 10"
)

BUFFERS=(20 30 40 50)

total_consensus=$(( ${#CONSENSUS_CONDITIONS[@]} * ${#BUFFERS[@]} ))
current=0

for cond_spec in "${CONSENSUS_CONDITIONS[@]}"; do
    IFS='|' read -r study_dir cond_name temps pools <<< "$cond_spec"

    for buffer in "${BUFFERS[@]}"; do
        current=$((current + 1))
        out_dir="${OUT_DIR}/${cond_name}-${buffer}m"
        echo "[$current/$total_consensus] ${cond_name} @ ${buffer}m"
        echo "  Study dir: ${study_dir}"
        echo "  Started: $(date)"

        # shellcheck disable=SC2086
        python3 scripts/analyse_consensus_sweep.py \
            --study-dir "$study_dir" \
            --output-dir "$out_dir" \
            --temperatures $temps \
            --pool-sizes $pools \
            --bounds "$BOUNDS" \
            --buffer-metres "$buffer" \
            --bootstrap "$BOOTSTRAP" \
            --seed "$SEED" \
            --quiet

        echo "  Completed: $(date)"
        echo ""
    done
done

echo "=== Section A complete: $(date) ==="
echo ""

# ─────────────────────────────────────────────────
# Section B: PV Buffer Sensitivity
# ─────────────────────────────────────────────────
# Evaluates ~8 PV conditions at all 4 buffer distances.
echo "=== Section B: PV Buffer Sensitivity ==="
echo "Started: $(date)"

python3 scripts/analyse_pv_buffer_sensitivity.py \
    --batch configs/pv-paper-conditions.yaml \
    --output-dir "${OUT_DIR}/pv" \
    --buffers 20 30 40 50 \
    --bounds "$BOUNDS" \
    --bootstrap "$BOOTSTRAP" \
    --seed "$SEED"

echo "=== Section B complete: $(date) ==="
echo ""

echo "============================================="
echo "All evaluations complete: $(date)"
echo "Results in: $OUT_DIR"
echo "============================================="
