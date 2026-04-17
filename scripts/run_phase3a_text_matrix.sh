#!/bin/bash
# Phase 3a Text Track: Complete 2×4 Thinking × Temperature Matrix
# ================================================================
#
# Text mirror of the Phase 3a image matrix. Uses detect_brief-text.json
# (17 examples, Scale-8 metadata — the text-track carry-forward per
# Decision 17). Note: text-only mode sends NO examples (neither images
# nor text descriptions) — consensus voting carries the performance,
# matching all existing H11 text K=30 runs.
#
# Full matrix (HIGH/MINIMAL × T=0.0/0.3/0.7/1.0) at 384 px / 487 tiles:
#
# Existing data (NOT re-run):
#   HIGH    T=0.7  K=30  outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/
#   MINIMAL T=0.7  K=30  outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/
#
# New runs (this script):
#   HIGH    T=0.0  K=3   .../flash-high-text-n5/text-t0.0/
#   HIGH    T=0.3  K=10  .../flash-high-text-n5/text-t0.3/
#   HIGH    T=1.0  K=10  .../flash-high-text-n5/text-t1.0/
#   MINIMAL T=0.0  K=3   .../flash-minimal-text-n30-t07/text-t0.0/
#   MINIMAL T=0.3  K=10  .../flash-minimal-text-n30-t07/text-t0.3/
#   MINIMAL T=1.0  K=10  .../flash-minimal-text-n30-t07/text-t1.0/
#
# Config: detect_brief-text.json (17 examples, Scale-8 metadata, text-only)
# Model: gemini-3-flash (flex tier)
# Caching: DISABLED — text preamble is 393 tokens (below Flash's 1024
#          minimum for context caching). Small cost increase per run.
# Workers: 250 (Tier 3 production standard)
#
# Total: 46 runs × 487 tiles = 22,402 API calls, ~$40-50, ~2.5 hours
#
# Usage:
#   nohup bash scripts/run_phase3a_text_matrix.sh > /tmp/phase3a-text-matrix.log 2>&1 &

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON=".venv/bin/python"
SCRIPT="scripts/4_detect_mounds_batch.py"
CONFIG="prompts/configs/detect_brief-text.json"
MANIFEST="inputs/tiles_384/full_evaluation_manifest.json"
TILES_DIR="inputs/tiles_384"

# Common flags — mirror image matrix except --config
COMMON_FLAGS="--config $CONFIG --manifest $MANIFEST --tiles-dir $TILES_DIR --tile-size 384 --mode realtime --service-tier flex --use-cache --workers 250"

# Output roots — mirror existing H11 text K=30 directory structure
HIGH_ROOT="outputs/h11/pv-diag-384/flash-high-text-n5"
MINIMAL_ROOT="outputs/h11/pv-diag-384/flash-minimal-text-n30-t07"

export PYTHONUNBUFFERED=1

# ---------------------------------------------------------------------------
# Helper (identical to image matrix script)
# ---------------------------------------------------------------------------
run_block() {
    local thinking="$1"
    local temp="$2"
    local k="$3"
    local out_root="$4"
    local temp_dir="text-t${temp}"
    local out_dir="${out_root}/${temp_dir}"

    echo ""
    echo "================================================================"
    echo "  BLOCK: thinking=${thinking}  T=${temp}  K=${k}"
    echo "  Output: ${out_dir}"
    echo "  Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "================================================================"

    local block_failures=0
    for run in $(seq 1 "$k"); do
        local run_dir="${out_dir}/run_${run}"
        echo ""
        echo "--- [${thinking}/T${temp}] Run ${run}/${k} → ${run_dir} ---"

        local rc=0
        $PYTHON $SCRIPT \
            $COMMON_FLAGS \
            --output-dir "$run_dir" \
            --temperature "$temp" \
            --thinking-level "$thinking" || rc=$?

        if [ "$rc" -eq 1 ]; then
            echo "FATAL: Setup error in run ${run}. Aborting block."
            return 1
        elif [ "$rc" -eq 2 ]; then
            echo "WARNING: Partial failure in run ${run} (some tiles failed). Continuing."
            block_failures=$((block_failures + 1))
        elif [ "$rc" -ne 0 ]; then
            echo "WARNING: Unexpected exit code ${rc} in run ${run}. Continuing."
            block_failures=$((block_failures + 1))
        fi
    done

    if [ "$block_failures" -gt 0 ]; then
        echo "  NOTE: ${block_failures}/${k} runs had partial failures in this block."
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

echo "Phase 3a Text Track: 2×4 Thinking × Temperature Matrix"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Config: $CONFIG (17 examples, Scale-8 metadata)"
echo "Manifest: $MANIFEST (487 tiles)"
echo "Workers: 250"
echo ""

# HIGH thinking — T=0.0 (K=3 deterministic baseline)
run_block "high" "0.0" 3 "$HIGH_ROOT"

# HIGH thinking — T=0.3 (K=10)
run_block "high" "0.3" 10 "$HIGH_ROOT"

# HIGH thinking — T=1.0 (K=10)
run_block "high" "1.0" 10 "$HIGH_ROOT"

# MINIMAL thinking — T=0.0 (K=3)
run_block "minimal" "0.0" 3 "$MINIMAL_ROOT"

# MINIMAL thinking — T=0.3 (K=10)
run_block "minimal" "0.3" 10 "$MINIMAL_ROOT"

# MINIMAL thinking — T=1.0 (K=10)
run_block "minimal" "1.0" 10 "$MINIMAL_ROOT"

echo ""
echo "================================================================"
echo "  ALL BLOCKS COMPLETE"
echo "  Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"
echo ""
echo "Next steps:"
echo "  1. Verify 46 run directories + meta files"
echo "  2. Build consensus (N=10 full + N=5 subset) for K=10 conditions"
echo "  3. Run verifier matrix for new text configs"
echo "  4. Produce secondary-effects analysis parallel to image matrix"
