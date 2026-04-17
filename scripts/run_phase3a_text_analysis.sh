#!/bin/bash
# Phase 3a Text Track: Comprehensive Consensus Analysis
# =====================================================
#
# Text mirror of run_phase3a_image_analysis.sh. Evaluates all consensus
# thresholds × 4 buffers × bootstrap CIs for the 2×4 text matrix.
# Consensus GeoJSONs are already built (by scripts/merge_passes.py via
# build_all_consensus.py).
#
# Output layout mirrors results/phase3a-image-matrix/:
#   results/phase3a-text-matrix/high-t{0.0,0.3,0.7,1.0}/{n10,n5,n3}/<slug>/evaluation.json
#   results/phase3a-text-matrix/minimal-t{0.0,0.3,0.7,1.0}/{n10,n5,n3}/<slug>/evaluation.json
#
# Usage:
#   nohup bash scripts/run_phase3a_text_analysis.sh > /tmp/phase3a-text-analysis.log 2>&1 &

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON=".venv/bin/python"
EVAL="scripts/evaluate_detections.py"

BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
GT="inputs/vectors/references/mounds-reference.geojson"
BUFFERS="20 30 40 50"
BOOTSTRAP=1000
SEED=42

HIGH_ROOT="outputs/h11/pv-diag-384/flash-high-text-n5"
MINIMAL_ROOT="outputs/h11/pv-diag-384/flash-minimal-text-n30-t07"
RESULTS_DIR="results/phase3a-text-matrix"

export PYTHONUNBUFFERED=1

echo "Phase 3a Text Track: Consensus Analysis"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

mkdir -p "$RESULTS_DIR"

evaluate_condition() {
    local geojson="$1"
    local label="$2"
    local output_dir="$3"

    local slug
    slug=$(echo "$label" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/^-//;s/-$//')
    local cond_dir="$output_dir/$slug"

    if [ -f "$cond_dir/evaluation.json" ]; then
        echo "    [$label] Cached — skipping"
        return 0
    fi

    echo "    [$label] Evaluating..."
    mkdir -p "$cond_dir"
    $PYTHON $EVAL \
        --detections "$geojson" \
        --buffers $BUFFERS \
        --bootstrap $BOOTSTRAP \
        --seed $SEED \
        --bounds "$BOUNDS" \
        --ground-truth "$GT" \
        --output-dir "$cond_dir" \
        --label "$label" 2>/dev/null

    echo "    [$label] Done"
}

# ---------------------------------------------------------------------------
# N=full sweeps (HIGH: K=3 for T=0.0, K=10 for T=0.3/1.0, K=30 for T=0.7)
# ---------------------------------------------------------------------------
for cfg in "HIGH:$HIGH_ROOT" "MINIMAL:$MINIMAL_ROOT"; do
    thinking="${cfg%%:*}"
    root="${cfg##*:}"
    thinking_slug=$(echo "$thinking" | tr '[:upper:]' '[:lower:]')

    for temp in t0.0 t0.3 t0.7 t1.0; do
        # Determine K for this condition
        case "$temp" in
            t0.0) k=3; pool_dir="n3" ;;
            t0.7) k=30; pool_dir="n30" ;;
            *)    k=10; pool_dir="n10" ;;
        esac

        consensus_dir="$root/text-${temp}/consensus"
        eval_dir="$RESULTS_DIR/${thinking_slug}-${temp}/${pool_dir}"
        mkdir -p "$eval_dir"
        echo "  ${thinking} ${temp} N=${k}:"
        for gj in "$consensus_dir"/consensus_t*.geojson; do
            [ -f "$gj" ] || continue
            t_val=$(basename "$gj" | sed 's/consensus_t\([0-9]*\).geojson/\1/')
            evaluate_condition "$gj" "${thinking}-${temp}-${t_val}of${k}" "$eval_dir"
        done
    done
done

# ---------------------------------------------------------------------------
# N=5 subsets (T=0.3, T=0.7, T=1.0 — T=0.0 is K=3, no N=5 possible)
# ---------------------------------------------------------------------------
echo ""
echo "=== N=5 sweeps ==="
for cfg in "HIGH:$HIGH_ROOT" "MINIMAL:$MINIMAL_ROOT"; do
    thinking="${cfg%%:*}"
    root="${cfg##*:}"
    thinking_slug=$(echo "$thinking" | tr '[:upper:]' '[:lower:]')

    for temp in t0.3 t0.7 t1.0; do
        consensus_dir="$root/text-${temp}/consensus-n5"
        [ -d "$consensus_dir" ] || continue
        eval_dir="$RESULTS_DIR/${thinking_slug}-${temp}/n5"
        mkdir -p "$eval_dir"
        echo "  ${thinking} ${temp} N=5:"
        for gj in "$consensus_dir"/consensus_t*.geojson; do
            [ -f "$gj" ] || continue
            t_val=$(basename "$gj" | sed 's/consensus_t\([0-9]*\).geojson/\1/')
            evaluate_condition "$gj" "${thinking}-${temp}-${t_val}of5" "$eval_dir"
        done
    done
done

# ---------------------------------------------------------------------------
# N=10 subsets for T=0.7 (K=30 runs have a consensus-n10 subset for parity)
# ---------------------------------------------------------------------------
echo ""
echo "=== N=10 subsets for T=0.7 ==="
for cfg in "HIGH:$HIGH_ROOT" "MINIMAL:$MINIMAL_ROOT"; do
    thinking="${cfg%%:*}"
    root="${cfg##*:}"
    thinking_slug=$(echo "$thinking" | tr '[:upper:]' '[:lower:]')

    consensus_dir="$root/text-t0.7/consensus-n10"
    [ -d "$consensus_dir" ] || continue
    eval_dir="$RESULTS_DIR/${thinking_slug}-t0.7/n10"
    mkdir -p "$eval_dir"
    echo "  ${thinking} t0.7 N=10:"
    for gj in "$consensus_dir"/consensus_t*.geojson; do
        [ -f "$gj" ] || continue
        t_val=$(basename "$gj" | sed 's/consensus_t\([0-9]*\).geojson/\1/')
        evaluate_condition "$gj" "${thinking}-t0.7-${t_val}of10" "$eval_dir"
    done
done

echo ""
echo "================================================================"
echo "  ALL EVALUATIONS COMPLETE"
echo "  Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"
