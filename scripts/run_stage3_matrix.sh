#!/usr/bin/env bash
# ============================================================================
# run_stage3_matrix.sh
# ----------------------------------------------------------------------------
# Session 110 Stage-3: complete the {T0.0,T0.3,T0.7} x {minimal,high} verifier
# matrix over the 384px >=3-of-5 band (855 cands, N=5). Runs the THREE new cells
# sequentially (the other three are already on disk: T0.0/T0.3 minimal from
# Stage 1/2, T0.0 high from the n=1 prior). Each cell = verify (gated API, flex)
# + analyse ($0). Held constant: model gemini-3-flash, band, N=5, text-only,
# flex; only temperature and thinking_level vary, one combo per run.
#
# Cost: T0.7 minimal $2.98 + T0.7 high $8.94 + T0.3 high $8.94 = ~$20.86 flex
# (Shawn-approved up to $35). Run on zbook (--workers 14; 16 cores, leave 2).
#
# Usage:  bash scripts/run_stage3_matrix.sh
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

SPEC="planning/verifier-robustness-stage3-384-cells.json"
RES="results/verifier-robustness"
PY=".venv/bin/python"
WORKERS=14

# (temperature, thinking) combos — the three NEW cells.
COMBOS=("0.7:minimal" "0.7:high" "0.3:high")

for combo in "${COMBOS[@]}"; do
  T="${combo%%:*}"; TH="${combo##*:}"
  echo "######################## RUN T=$T thinking=$TH ########################"
  if [ "$TH" = "minimal" ]; then
    "$PY" scripts/run_verifier_robustness.py --full --temperature "$T" \
        --workers "$WORKERS" --cells "$SPEC"
    "$PY" scripts/analyse_verifier_robustness.py --temperature "$T" \
        --cells "$SPEC" --out-dir "$RES"
  else
    "$PY" scripts/run_verifier_robustness.py --full --temperature "$T" \
        --thinking-level "$TH" --workers "$WORKERS" --cells "$SPEC"
    "$PY" scripts/analyse_verifier_robustness.py --temperature "$T" \
        --thinking-level "$TH" --cells "$SPEC" --out-dir "$RES"
  fi
done
echo "######################## STAGE-3 MATRIX COMPLETE ########################"
