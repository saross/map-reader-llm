#!/bin/bash
# Overnight Pro Verifier Runs (Waves 2 + 4)
# ==========================================
# Wave 2: 1 Pro verifier run on pro-high-image-1of5 (841 candidates)
# Wave 4: 9 Pro/mixed verifier matrix runs (14,958 candidates)
# Total: 15,799 candidates, ~$5.99 via Batch API.
# Expected runtime: 8-16 hours total (sequential).
#
# Usage:
#   nohup bash scripts/overnight-pro-verifier-all.sh \
#       > outputs/h11/pv-diag-384/wave2-4-pro-verifier.log 2>&1 &

set -euo pipefail
cd /home/shawn/Code/map-reader-llm
source .venv/bin/activate

CROPS_BASE="outputs/h11/pv-diag-384/crops"
VERIFIED_BASE="outputs/h11/pv-diag-384/verified"
VERIFIER_CONFIG="prompts/configs/verify_adversarial-text.json"

echo "=== Waves 2+4: Pro Verifier Runs ==="
echo "Started: $(date)"
echo ""

# --- Wave 2: Pro PV Baseline ---

# W2. pro-high-image-1of5 + Pro verifier (841 candidates)
echo "--- [W2] pro-high-image-1of5 + Pro medium (841 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/pro-high-image-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/pro-high-image-1of5-pro-verifier" \
    --model gemini-3.1-pro --thinking-level medium \
    --mode batch
echo "Completed: $(date)"
echo ""

# --- Wave 4: Pro Verifier Matrix ---

# W4.1. text-baseline + Pro verifier (1,047 candidates)
echo "--- [W4.1] text-baseline + Pro medium (1,047 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/text-baseline" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/text-baseline-pro-verifier" \
    --model gemini-3.1-pro --thinking-level medium \
    --mode batch
echo "Completed: $(date)"
echo ""

# W4.2. image-baseline + Pro verifier (746 candidates)
echo "--- [W4.2] image-baseline + Pro medium (746 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/image-baseline" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/image-baseline-pro-verifier" \
    --model gemini-3.1-pro --thinking-level medium \
    --mode batch
echo "Completed: $(date)"
echo ""

# W4.3. pro-medium-text-baseline + Pro verifier (430 candidates)
echo "--- [W4.3] pro-medium-text-baseline + Pro medium (430 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/pro-medium-text-baseline" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/pro-medium-text-baseline-pro-verifier" \
    --model gemini-3.1-pro --thinking-level medium \
    --mode batch
echo "Completed: $(date)"
echo ""

# W4.4. pro-medium-image-baseline + Pro verifier (519 candidates)
echo "--- [W4.4] pro-medium-image-baseline + Pro medium (519 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/pro-medium-image-baseline" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/pro-medium-image-baseline-pro-verifier" \
    --model gemini-3.1-pro --thinking-level medium \
    --mode batch
echo "Completed: $(date)"
echo ""

# W4.5. flash-high-text-1of5 + Pro verifier (3,736 candidates)
echo "--- [W4.5] flash-high-text-1of5 + Pro medium (3,736 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/flash-high-text-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/flash-high-text-1of5-pro-verifier" \
    --model gemini-3.1-pro --thinking-level medium \
    --mode batch
echo "Completed: $(date)"
echo ""

# W4.6. flash-high-text-1of5 + Flash medium verifier (3,736 candidates)
echo "--- [W4.6] flash-high-text-1of5 + Flash medium (3,736 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/flash-high-text-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/flash-high-text-1of5-flash-medium-verifier" \
    --thinking-level medium \
    --mode batch
echo "Completed: $(date)"
echo ""

# W4.7. pro-high-text-1of5 + Pro verifier (504 candidates)
echo "--- [W4.7] pro-high-text-1of5 + Pro medium (504 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/pro-high-text-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/pro-high-text-1of5-pro-verifier" \
    --model gemini-3.1-pro --thinking-level medium \
    --mode batch
echo "Completed: $(date)"
echo ""

# W4.8. pro-high-text-1of5 + Flash minimal verifier (504 candidates)
echo "--- [W4.8] pro-high-text-1of5 + Flash minimal (504 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/pro-high-text-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/pro-high-text-1of5-flash-minimal-verifier" \
    --mode batch
echo "Completed: $(date)"
echo ""

# W4.9. flash-high-text-1of5 + Flash HIGH verifier (3,736 candidates)
echo "--- [W4.9] flash-high-text-1of5 + Flash HIGH (3,736 candidates) ---"
echo "Started: $(date)"
python3 scripts/run_pv.py verify \
    --crops-dir "$CROPS_BASE/flash-high-text-1of5" \
    --verifier-config "$VERIFIER_CONFIG" \
    --output-dir "$VERIFIED_BASE/flash-high-text-1of5-flash-high-verifier" \
    --thinking-level high \
    --mode batch
echo "Completed: $(date)"
echo ""

echo "=== Waves 2+4 complete: $(date) ==="
