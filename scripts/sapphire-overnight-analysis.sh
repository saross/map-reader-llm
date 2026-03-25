#!/bin/bash
# Sapphire Overnight Analysis
# ============================
# Buffer distance sensitivity (30, 40, 50 m) + Phase 3c diversity analysis.
# Run on sapphire (24 cores, parallelised internally by each script).
#
# Usage:
#   ssh sapphire 'cd ~/Code/map-reader-llm && source .venv/bin/activate && \
#       nohup bash scripts/sapphire-overnight-analysis.sh \
#       > results/sapphire-analysis.log 2>&1 &'

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate

BOUNDS="inputs/vectors/bounds/384/validation_bounds.geojson"
FULL_BOUNDS="inputs/vectors/bounds/full_evaluation_bounds.geojson"
BUFFER_OUT="results/h11-384-buffer-sensitivity"

echo "============================================="
echo "Sapphire Overnight Analysis"
echo "Started: $(date)"
echo "============================================="
echo ""

# -----------------------------------------------
# Step 1: Buffer Distance Sensitivity
# -----------------------------------------------
echo "=== Step 1: Buffer Distance Sensitivity ==="
echo ""

mkdir -p "$BUFFER_OUT"

# Define conditions as arrays: study_dir, name, temperatures, pool_sizes
declare -a CONDITIONS=(
    "outputs/h11/pv-diag-384/flash-high-text-n5|flash-high-text|text-t0.7|5 10 30"
    "outputs/h11/pv-diag-384/flash-high-image-n5|flash-high-image|image-t0.7|5 10"
    "outputs/h11/pv-diag-384/pro-high-text-n5|pro-high-text|text-t0.7|5"
    "outputs/h11/pv-diag-384/pro-high-image-n5|pro-high-image|image-t0.7|5"
    "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07|flash-minimal-text-t07|text-t0.7|5 10 30"
)

BUFFERS=(30 40 50)

for cond_spec in "${CONDITIONS[@]}"; do
    IFS='|' read -r study_dir cond_name temps pools <<< "$cond_spec"

    for buffer in "${BUFFERS[@]}"; do
        out_dir="${BUFFER_OUT}/${cond_name}-${buffer}m"
        echo "--- ${cond_name} @ ${buffer}m ---"
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
            --quiet

        echo "  Completed: $(date)"
        echo ""
    done
done

echo "=== Step 1 complete: $(date) ==="
echo ""

# -----------------------------------------------
# Step 2: Phase 3c Diversity Analysis
# -----------------------------------------------
echo "=== Step 2: Phase 3c Diversity Analysis ==="
echo ""

# Track 1 (image) — just completed batch run
echo "--- Track 1 (image) ---"
echo "Started: $(date)"
python3 scripts/analyse_diversity.py \
    --study-yaml studies/retest/phase3c-h9-diversity-track1.yaml \
    --output-dir results/phase3c-diversity/track1-image \
    --bounds "$FULL_BOUNDS"
echo "Completed: $(date)"
echo ""

# Track 2 (text) — re-run for consistency
echo "--- Track 2 (text) ---"
echo "Started: $(date)"
python3 scripts/analyse_diversity.py \
    --study-yaml studies/retest/phase3c-h9-diversity-track2.yaml \
    --output-dir results/phase3c-diversity/track2-text \
    --bounds "$FULL_BOUNDS"
echo "Completed: $(date)"
echo ""

echo "=== Step 2 complete: $(date) ==="
echo ""

echo "============================================="
echo "All analyses complete: $(date)"
echo "============================================="
