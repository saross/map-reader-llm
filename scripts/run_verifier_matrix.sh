#!/bin/bash
# Full-Matrix Verifier Pipeline: 9 N=10 + 7 N=5 Proposer Configurations
# ======================================================================
#
# Runs text-only adversarial v1 verifier across all proposer configs
# from the Phase 3a image matrix + scale-4 optimal run.
#
# Pipeline per config: extract crops → verify → 2D sweep
#
# Estimated: ~32,600 candidates, ~$15 at Flex, ~1-2 hours
#
# Usage:
#   nohup bash scripts/run_verifier_matrix.sh > /tmp/verifier-matrix.log 2>&1 &

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON=".venv/bin/python"
PV="scripts/run_pv.py"
SWEEP="scripts/sweep_f1_greedy_pv.py"
VERIFIER_CONFIG="prompts/configs/verify_adversarial-text.json"
BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

export PYTHONUNBUFFERED=1

echo "Full-Matrix Verifier Pipeline"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# ---------------------------------------------------------------------------
# Helper: run full pipeline for one proposer config
# ---------------------------------------------------------------------------
run_verifier_pipeline() {
    local label="$1"
    local consensus_geojson="$2"
    local output_base="$3"

    local crops_dir="$output_base/crops"
    local verified_dir="$output_base"

    echo ""
    echo "================================================================"
    echo "  CONFIG: $label"
    echo "  Consensus: $consensus_geojson"
    echo "  Output: $output_base"
    echo "  Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "================================================================"

    # Step 1: Extract crops
    if [ -f "$crops_dir/candidate_manifest.json" ]; then
        echo "  [extract] Cached — skipping"
    else
        echo "  [extract] Extracting crops..."
        $PYTHON $PV extract \
            --proposer "$consensus_geojson" \
            --output-dir "$crops_dir" \
            --padding 75
        echo "  [extract] Done"
    fi

    # Step 2: Verify
    if [ -f "$verified_dir/probabilities.json" ]; then
        echo "  [verify] Cached — skipping"
    else
        echo "  [verify] Verifying candidates..."
        local rc=0
        $PYTHON $PV verify \
            --crops-dir "$crops_dir" \
            --verifier-config "$VERIFIER_CONFIG" \
            --output-dir "$verified_dir" \
            --mode realtime \
            --workers 20 \
            --service-tier flex \
            --no-strict || rc=$?
        if [ "$rc" -ne 0 ]; then
            echo "  [verify] WARNING: exit code $rc"
        fi
        echo "  [verify] Done"
    fi

    # Step 3: 2D sweep at all buffers
    local sweep_file="$output_base/sweep_2d.json"
    if [ -f "$sweep_file" ]; then
        echo "  [sweep] Cached — skipping"
    else
        echo "  [sweep] Running 2D sweep..."
        $PYTHON $SWEEP \
            --config "$label" \
            --crops-dir "$crops_dir" \
            --verified-dir "$verified_dir" \
            --output "$sweep_file" \
            --bounds "$BOUNDS" \
            --buffer-m 20 30 40 50
        echo "  [sweep] Done"
    fi

    echo "  CONFIG COMPLETE: $label ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
}

# ---------------------------------------------------------------------------
# N=10 configurations (9 proposers)
# ---------------------------------------------------------------------------
echo "=== N=10 VERIFIER RUNS (9 configs) ==="

HIGH_ROOT="outputs/h11/pv-diag-384/flash-high-image-n5"
MINIMAL_ROOT="outputs/h11/pv-diag-384/image-n5"

# HIGH thinking
for temp in t0.0 t0.3 t0.7 t1.0; do
    run_verifier_pipeline \
        "high-${temp}-n10" \
        "$HIGH_ROOT/image-${temp}/consensus/consensus_t1.geojson" \
        "$HIGH_ROOT/image-${temp}/verified-v1-n10"
done

# MINIMAL thinking
for temp in t0.3 t0.7 t1.0; do
    run_verifier_pipeline \
        "minimal-${temp}-n10" \
        "$MINIMAL_ROOT/image-${temp}/consensus/consensus_t1.geojson" \
        "$MINIMAL_ROOT/image-${temp}/verified-v1-n10"
done

# MINIMAL T=0.0 baseline
run_verifier_pipeline \
    "minimal-t0.0-n3" \
    "outputs/h11/n1-outstanding-384/image-t0/consensus/consensus_t1.geojson" \
    "outputs/h11/n1-outstanding-384/image-t0/verified-v1-n3"

# Scale-4 optimal
run_verifier_pipeline \
    "scale4-high-t0.7-n10" \
    "outputs/h11/pv-diag-384/scale-4-optimal-487/consensus/consensus_t1.geojson" \
    "outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10"

# ---------------------------------------------------------------------------
# N=5 configurations (7 proposers)
# ---------------------------------------------------------------------------
echo ""
echo "=== N=5 VERIFIER RUNS (7 configs) ==="

# HIGH thinking N=5
for temp in t0.3 t0.7 t1.0; do
    run_verifier_pipeline \
        "high-${temp}-n5" \
        "$HIGH_ROOT/image-${temp}/consensus-n5/consensus_t1.geojson" \
        "$HIGH_ROOT/image-${temp}/verified-v1-n5"
done

# MINIMAL thinking N=5
for temp in t0.3 t0.7 t1.0; do
    run_verifier_pipeline \
        "minimal-${temp}-n5" \
        "$MINIMAL_ROOT/image-${temp}/consensus-n5/consensus_t1.geojson" \
        "$MINIMAL_ROOT/image-${temp}/verified-v1-n5"
done

# Scale-4 optimal N=5
run_verifier_pipeline \
    "scale4-high-t0.7-n5" \
    "outputs/h11/pv-diag-384/scale-4-optimal-487/consensus-n5/consensus_t1.geojson" \
    "outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n5"

echo ""
echo "================================================================"
echo "  ALL VERIFIER RUNS COMPLETE"
echo "  Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"
