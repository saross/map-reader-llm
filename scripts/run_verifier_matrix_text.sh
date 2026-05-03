#!/bin/bash
# Text-Track Verifier Matrix: 8 N=10 + 6 N=5 Proposer Configurations
# ====================================================================
#
# Mirrors the image-track verifier matrix for the Phase 3a text matrix.
# Uses the same text-only adversarial v1 verifier as the image track (the
# verifier is modality-agnostic by design — it re-examines candidate crops
# regardless of which proposer produced them).
#
# Pipeline per config: extract crops → verify → 2D sweep
#
# N=10 proposers (8 configs): HIGH/MIN × T=0.0(n3)/0.3/0.7/1.0
# N=5 proposers  (6 configs): HIGH/MIN × T=0.3/0.7/1.0
#
# Estimated: ~20,000 candidates, ~$10 at Flex, ~1-1.5 hours
#
# Usage:
#   nohup bash scripts/run_verifier_matrix_text.sh > /tmp/verifier-matrix-text.log 2>&1 &

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON=".venv/bin/python"
PV="scripts/run_pv.py"
SWEEP="scripts/sweep_f1_greedy_pv.py"
VERIFIER_CONFIG="prompts/configs/verify_adversarial-text.json"
BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

export PYTHONUNBUFFERED=1

echo "Text-Track Verifier Matrix"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# ---------------------------------------------------------------------------
# Helper: full pipeline for one proposer config
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
# Output roots
# ---------------------------------------------------------------------------
HIGH_ROOT="outputs/h11/pv-diag-384/flash-high-text-n5"
MINIMAL_ROOT="outputs/h11/pv-diag-384/flash-minimal-text-n30-t07"

# ---------------------------------------------------------------------------
# N=10 configurations (for K=10/K=30 conditions use full consensus at T≠0.7;
# for T=0.7 use the consensus-n10 subset; for T=0.0 K=3 use the base consensus)
# ---------------------------------------------------------------------------
echo "=== N=10 VERIFIER RUNS (8 configs) ==="

# HIGH thinking — T=0.0 (K=3 baseline)
run_verifier_pipeline \
    "high-text-t0.0-n3" \
    "$HIGH_ROOT/text-t0.0/consensus/consensus_t1.geojson" \
    "$HIGH_ROOT/text-t0.0/verified-v1-n3"

# HIGH thinking — T=0.3, T=1.0 (K=10 full)
for temp in t0.3 t1.0; do
    run_verifier_pipeline \
        "high-text-${temp}-n10" \
        "$HIGH_ROOT/text-${temp}/consensus/consensus_t1.geojson" \
        "$HIGH_ROOT/text-${temp}/verified-v1-n10"
done

# HIGH thinking — T=0.7 (use N=10 subset of K=30)
run_verifier_pipeline \
    "high-text-t0.7-n10" \
    "$HIGH_ROOT/text-t0.7/consensus-n10/consensus_t1.geojson" \
    "$HIGH_ROOT/text-t0.7/verified-v1-n10"

# MINIMAL thinking — T=0.0 (K=3 baseline)
run_verifier_pipeline \
    "minimal-text-t0.0-n3" \
    "$MINIMAL_ROOT/text-t0.0/consensus/consensus_t1.geojson" \
    "$MINIMAL_ROOT/text-t0.0/verified-v1-n3"

# MINIMAL thinking — T=0.3, T=1.0 (K=10 full)
for temp in t0.3 t1.0; do
    run_verifier_pipeline \
        "minimal-text-${temp}-n10" \
        "$MINIMAL_ROOT/text-${temp}/consensus/consensus_t1.geojson" \
        "$MINIMAL_ROOT/text-${temp}/verified-v1-n10"
done

# MINIMAL thinking — T=0.7 (use N=10 subset of K=30)
run_verifier_pipeline \
    "minimal-text-t0.7-n10" \
    "$MINIMAL_ROOT/text-t0.7/consensus-n10/consensus_t1.geojson" \
    "$MINIMAL_ROOT/text-t0.7/verified-v1-n10"

# ---------------------------------------------------------------------------
# N=5 configurations (6 configs: HIGH/MIN × T=0.3, T=0.7, T=1.0)
# ---------------------------------------------------------------------------
echo ""
echo "=== N=5 VERIFIER RUNS (6 configs) ==="

for temp in t0.3 t0.7 t1.0; do
    run_verifier_pipeline \
        "high-text-${temp}-n5" \
        "$HIGH_ROOT/text-${temp}/consensus-n5/consensus_t1.geojson" \
        "$HIGH_ROOT/text-${temp}/verified-v1-n5"
done

for temp in t0.3 t0.7 t1.0; do
    run_verifier_pipeline \
        "minimal-text-${temp}-n5" \
        "$MINIMAL_ROOT/text-${temp}/consensus-n5/consensus_t1.geojson" \
        "$MINIMAL_ROOT/text-${temp}/verified-v1-n5"
done

echo ""
echo "================================================================"
echo "  ALL VERIFIER RUNS COMPLETE"
echo "  Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"
