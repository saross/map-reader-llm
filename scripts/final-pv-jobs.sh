#!/bin/bash
# Final PV Jobs — Sequential Small + Parallel Large
# ===================================================
# Phase 1: W4.7 + W4.8 sequentially (504 candidates each, fast)
# Phase 2: W4.6 + W4.9 in parallel (3,736 candidates each)
#
# Usage:
#   nohup bash scripts/final-pv-jobs.sh \
#       > outputs/h11/pv-diag-384/final-pv-jobs.log 2>&1 &

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate

CROPS_BASE="outputs/h11/pv-diag-384/crops"
VERIFIED_BASE="outputs/h11/pv-diag-384/verified"
VERIFIER_CONFIG="prompts/configs/verify_adversarial-text.json"

echo "============================================="
echo "Final PV Jobs"
echo "Started: $(date)"
echo "============================================="
echo ""

# -----------------------------------------------
# Phase 1: Small jobs sequentially
# -----------------------------------------------

# W4.7. pro-high-text-1of5 + Pro verifier (504 candidates)
echo "--- [W4.7] pro-high-text-1of5 + Pro medium (504 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/pro-high-text-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/pro-high-text-1of5-pro-verifier" \
    --model gemini-3.1-pro --thinking-level medium \
    --mode batch \
    --no-strict
echo "Completed: $(date)"
echo ""

# W4.8. pro-high-text-1of5 + Flash minimal verifier (504 candidates)
echo "--- [W4.8] pro-high-text-1of5 + Flash minimal (504 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/pro-high-text-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/pro-high-text-1of5-flash-minimal-verifier" \
    --mode batch \
    --no-strict
echo "Completed: $(date)"
echo ""

echo "=== Phase 1 (small jobs) complete: $(date) ==="
echo ""

# -----------------------------------------------
# Phase 2: Large jobs in parallel
# -----------------------------------------------
echo "=== Phase 2: Launching large jobs in parallel ==="
echo ""

# W4.6. flash-high-text-1of5 + Flash medium verifier (3,736 candidates)
echo "--- [W4.6] flash-high-text-1of5 + Flash medium (3,736 candidates) ---"
echo "Launching in background: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/flash-high-text-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/flash-high-text-1of5-flash-medium-verifier" \
    --thinking-level medium \
    --mode batch \
    --no-strict &
W46_PID=$!
echo "W4.6 PID: $W46_PID"

# Small delay to avoid upload collision
sleep 10

# W4.9. flash-high-text-1of5 + Flash HIGH verifier (3,736 candidates)
echo "--- [W4.9] flash-high-text-1of5 + Flash HIGH (3,736 candidates) ---"
echo "Launching in background: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/flash-high-text-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/flash-high-text-1of5-flash-high-verifier" \
    --thinking-level high \
    --mode batch \
    --no-strict &
W49_PID=$!
echo "W4.9 PID: $W49_PID"

echo ""
echo "Waiting for both parallel jobs to complete..."
wait $W46_PID
W46_EXIT=$?
echo "W4.6 exit code: $W46_EXIT ($(date))"

wait $W49_PID
W49_EXIT=$?
echo "W4.9 exit code: $W49_EXIT ($(date))"

echo ""
if [ $W46_EXIT -eq 0 ] && [ $W49_EXIT -eq 0 ]; then
    echo "============================================="
    echo "All final PV jobs complete: $(date)"
    echo "============================================="
else
    echo "WARNING: One or more jobs failed!"
    echo "  W4.6 exit: $W46_EXIT"
    echo "  W4.9 exit: $W49_EXIT"
fi

# Clean up JSONL files immediately to save disk space
echo ""
echo "Cleaning up verifier JSONL files..."
for d in pro-high-text-1of5-pro-verifier pro-high-text-1of5-flash-minimal-verifier \
         flash-high-text-1of5-flash-medium-verifier flash-high-text-1of5-flash-high-verifier; do
    jsonl="$VERIFIED_BASE/$d/verifier_requests.jsonl"
    if [ -f "$jsonl" ] && [ -f "$VERIFIED_BASE/$d/probabilities.json" ]; then
        size=$(du -m "$jsonl" 2>/dev/null | cut -f1)
        rm "$jsonl"
        echo "  Cleaned $d ($size MB)"
    fi
done
echo "Cleanup done: $(date)"
