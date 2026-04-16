#!/bin/bash
# Phase 3a Image Track: Complete 2×4 Thinking × Temperature Matrix
# =================================================================
#
# Runs the missing cells in the Flash × {HIGH, MINIMAL} × {T0.0, T0.3, T1.0}
# image-track detection matrix at 384 px (487 tiles). T=0.7 already exists
# for both thinking levels (H11 PV-diag).
#
# Existing data (not re-run):
#   HIGH    T=0.7  K=10  outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/
#   MINIMAL T=0.7  K=10  outputs/h11/pv-diag-384/image-n5/image-t0.7/
#
# New runs (this script):
#   HIGH    T=0.0  K=3   outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/
#   HIGH    T=0.3  K=10  outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/
#   HIGH    T=1.0  K=10  outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/
#   MINIMAL T=0.3  K=10  outputs/h11/pv-diag-384/image-n5/image-t0.3/
#   MINIMAL T=1.0  K=10  outputs/h11/pv-diag-384/image-n5/image-t1.0/
#
# Config: library_plus-hp.json (13 examples, 4HP 0HN)
# Model: gemini-3-flash (flex tier + context caching)
# Tiles: inputs/tiles_384/full_evaluation_manifest.json (487 tiles)
# Workers: 250 (Tier 3 production standard, ~3.5 min per 487-tile pass)
#
# Total: 43 runs × 487 tiles = 20,941 API calls, ~$22, ~2.5 hours
#
# Usage:
#   nohup bash scripts/run_phase3a_image_matrix.sh > /tmp/phase3a-image-matrix.log 2>&1 &
#
# Erratum: E53 (Phase 3a-HIGH image track moved from 512px to 384px)

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON=".venv/bin/python"
SCRIPT="scripts/4_detect_mounds_batch.py"
CONFIG="prompts/configs/library_plus-hp.json"
MANIFEST="inputs/tiles_384/full_evaluation_manifest.json"
TILES_DIR="inputs/tiles_384"

# Common flags for all runs
COMMON_FLAGS="--config $CONFIG --manifest $MANIFEST --tiles-dir $TILES_DIR --tile-size 384 --mode realtime --service-tier flex --use-cache --workers 250"

# Output roots
HIGH_ROOT="outputs/h11/pv-diag-384/flash-high-image-n5"
MINIMAL_ROOT="outputs/h11/pv-diag-384/image-n5"

export PYTHONUNBUFFERED=1

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

run_block() {
    local thinking="$1"
    local temp="$2"
    local k="$3"
    local out_root="$4"
    local temp_dir="image-t${temp}"
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

        # Exit code 2 = partial failure (some tiles failed); continue the block.
        # Exit code 1 = setup error; abort.
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

    echo ""
    echo "  BLOCK COMPLETE: ${thinking} T=${temp} K=${k}"
    echo "  Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "================================================================"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

echo "Phase 3a Image Track: 2×4 Thinking × Temperature Matrix"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Config: $CONFIG"
echo "Manifest: $MANIFEST (487 tiles)"
echo "Workers: 250"
echo ""

# HIGH thinking — T=0.0 (K=3 deterministic baseline)
run_block "high" "0.0" 3 "$HIGH_ROOT"

# HIGH thinking — T=0.3 (K=10)
run_block "high" "0.3" 10 "$HIGH_ROOT"

# HIGH thinking — T=1.0 (K=10)
run_block "high" "1.0" 10 "$HIGH_ROOT"

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
echo "  1. Verify all 43 run directories have detections + meta files"
echo "  2. Run build_all_consensus.py for the 4 new K=10 conditions"
echo "  3. Run consensus analysis (N=5, N=10 sweeps)"
