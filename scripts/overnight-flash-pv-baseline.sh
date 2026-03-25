#!/bin/bash
# Overnight Flash PV Baseline Verifier Runs (Wave 1)
# ===================================================
# Runs 4 sequential Flash verifier jobs on existing crops.
# Total: 21,247 candidates, ~$0.80 via Batch API.
# Expected runtime: 2-4 hours total (sequential).
#
# Usage:
#   nohup bash scripts/overnight-flash-pv-baseline.sh \
#       > outputs/h11/pv-diag-384/wave1-flash-baseline.log 2>&1 &

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate

CROPS_BASE="outputs/h11/pv-diag-384/crops"
VERIFIED_BASE="outputs/h11/pv-diag-384/verified"
VERIFIER_CONFIG="prompts/configs/verify_adversarial-text.json"

echo "=== Wave 1: Flash PV Baseline ==="
echo "Started: $(date)"
echo ""

# 1. flash-high-image-1of5 (2,017 candidates)
echo "--- [1/4] flash-high-image-1of5 (2,017 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/flash-high-image-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/flash-high-image-1of5" \
    --mode batch
echo "Completed: $(date)"
echo ""

# 2. flash-high-text-1of10 (5,866 candidates)
echo "--- [2/4] flash-high-text-1of10 (5,866 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/flash-high-text-1of10" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/flash-high-text-1of10" \
    --mode batch
echo "Completed: $(date)"
echo ""

# 3. flash-high-text-1of30 (11,771 candidates)
echo "--- [3/4] flash-high-text-1of30 (11,771 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/flash-high-text-1of30" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/flash-high-text-1of30" \
    --mode batch
echo "Completed: $(date)"
echo ""

# 4. flash-minimal-text-t07-1of5 (1,593 candidates)
echo "--- [4/4] flash-minimal-text-t07-1of5 (1,593 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/flash-minimal-text-t07-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/flash-minimal-text-t07-1of5" \
    --mode batch
echo "Completed: $(date)"
echo ""

echo "=== Wave 1 complete: $(date) ==="
