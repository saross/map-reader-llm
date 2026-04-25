#!/bin/bash
# ---------------------------------------------------------------------------
# finalise_per_arch_leaderboard.sh
# ---------------------------------------------------------------------------
# After the main per-architecture tier build completes (from
# run_per_arch_leaderboards.sh), this script:
#
#   1. Augments each stratum's tier JSON with tile-level MCC @ 20 m.
#   2. Enriches the per-buffer markdown tables with metadata columns.
#   3. Builds the cross-architecture comparison at 20 m.
#   4. Runs a spot-check verification pass on random rows per stratum.
#
# Intended to run locally (amd-tower) or on sapphire — both work, but
# amd-tower is fine because the MCC augmentation is <60 s total.
#
# Usage:
#   bash scripts/finalise_per_arch_leaderboard.sh
# ---------------------------------------------------------------------------

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON="${REPO_ROOT}/.venv/bin/python"
OUT_ROOT="${REPO_ROOT}/results/leaderboard/per-architecture"
GIT_COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo uncommitted)"

echo "=== Step 1: Augment tier JSONs with tile-level MCC @ 20 m ==="
"$PYTHON" scripts/augment_per_arch_with_mcc.py --root "$OUT_ROOT" --workers 8

echo ""
echo "=== Step 2: Enrich per-buffer markdown tables ==="
"$PYTHON" scripts/enrich_per_arch_markdown.py \
    --root "$OUT_ROOT" \
    --inventory planning/condition-inventory-with-s78.json \
    --git-commit "$GIT_COMMIT"

echo ""
echo "=== Step 3: Cross-architecture comparison at 20 m ==="
"$PYTHON" scripts/build_cross_arch_comparison.py \
    --root "$OUT_ROOT" \
    --buffer 20

echo ""
echo "=== Step 4: Per-stratum headlines ==="
"$PYTHON" scripts/summarise_per_arch_headlines.py

echo ""
echo "=== Step 5: Spot-check verification ==="
"$PYTHON" scripts/verify_per_arch_leaderboard.py --n 2

echo ""
echo "ALL POST-PROCESSING COMPLETE"
