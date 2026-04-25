#!/bin/bash
# ---------------------------------------------------------------------------
# run_per_arch_leaderboards.sh
# ---------------------------------------------------------------------------
# Orchestrate the per-architecture leaderboard build across 12 (era, arch)
# strata × 5 buffers (20, 30, 40, 50, 100 m).
#
# Runs `build_tiered_leaderboard.py` once per stratum, writing to
# `results/leaderboard/per-architecture/era<N>/<arch>/`.
#
# Inputs:
#   planning/condition-inventory-with-s78.json  (204 conditions)
#
# Bounds:
#   Era 1: inputs/vectors/bounds/full_evaluation_bounds.geojson   (340 tiles)
#   Era 2: inputs/vectors/bounds/384/full_evaluation_bounds.geojson (487 tiles)
#   Era 3: inputs/vectors/bounds/384/h10_test_bounds.geojson      (327 tiles)
#
# Each per-stratum invocation runs:
#   - Evaluation at 5 buffers (20/30/40/50/100 m), 1000 bootstrap iters
#   - Threshold selection at 20 m primary buffer
#   - Top-20 filter (union across buffers)
#   - 10,000 pairwise permutation tests at 20 m
#   - BH-FDR correction at q=0.05
#   - Tier grouping
#
# Usage:
#   bash scripts/run_per_arch_leaderboards.sh
#
# Run on sapphire. Total wall-clock ~2-3 hours for the full matrix.
# ---------------------------------------------------------------------------

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON="${REPO_ROOT}/.venv/bin/python"
INVENTORY="${REPO_ROOT}/planning/condition-inventory-with-s78.json"
SCRIPT="${REPO_ROOT}/scripts/build_tiered_leaderboard.py"
OUT_ROOT="${REPO_ROOT}/results/leaderboard/per-architecture"
LOG_DIR="${REPO_ROOT}/logs/per-arch-leaderboards"

mkdir -p "$OUT_ROOT" "$LOG_DIR"

BOUNDS_E1="${REPO_ROOT}/inputs/vectors/bounds/full_evaluation_bounds.geojson"
BOUNDS_E2="${REPO_ROOT}/inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
BOUNDS_E3="${REPO_ROOT}/inputs/vectors/bounds/384/h10_test_bounds.geojson"

BUFFERS="20 30 40 50 100"
PRIMARY_BUFFER=20
WORKERS=8
N_PERMUTATIONS=10000
BOOTSTRAP=1000

# Which status values to accept per architecture:
#   consensus       -> READY
#   single-pass     -> SINGLE_PASS_ONLY
#   single-pass+PV  -> PV_READY (excludes QUARANTINED v2 cells)
#   pv              -> READY

run_stratum() {
    local era="$1"
    local arch="$2"
    local status="$3"
    local bounds="$4"

    local out_dir="${OUT_ROOT}/era${era}/${arch}"
    local log="${LOG_DIR}/era${era}-${arch}.log"

    mkdir -p "$out_dir"

    echo "=========================================="
    echo "Era ${era} × ${arch} (status=${status})"
    echo "Bounds: $(basename "$bounds")"
    echo "Output: ${out_dir}"
    echo "Log:    ${log}"
    echo "=========================================="

    # Dry run first to show the condition list
    "$PYTHON" "$SCRIPT" \
        --inventory "$INVENTORY" \
        --era "$era" --architecture "$arch" --status "$status" \
        --bounds "$bounds" \
        --buffers $BUFFERS \
        --primary-buffer "$PRIMARY_BUFFER" \
        --bootstrap "$BOOTSTRAP" \
        --n-permutations "$N_PERMUTATIONS" \
        --workers "$WORKERS" \
        --output-dir "$out_dir" \
        --dry-run 2>&1 | head -60 | tee -a "$log"

    # Full run
    "$PYTHON" "$SCRIPT" \
        --inventory "$INVENTORY" \
        --era "$era" --architecture "$arch" --status "$status" \
        --bounds "$bounds" \
        --buffers $BUFFERS \
        --primary-buffer "$PRIMARY_BUFFER" \
        --bootstrap "$BOOTSTRAP" \
        --n-permutations "$N_PERMUTATIONS" \
        --workers "$WORKERS" \
        --output-dir "$out_dir" 2>&1 | tee -a "$log"

    echo "DONE: era${era}-${arch}"
    echo ""
}

# Era 1 — 512 px, 340 tiles
# Strata already complete are skipped automatically via their tier-JSON
# presence check (or just re-running leverages the cache).
run_stratum 1 "consensus"       "READY" "$BOUNDS_E1"
run_stratum 1 "single-pass"     "SINGLE_PASS_ONLY" "$BOUNDS_E1"
# Era 1 has no single-pass+PV or pv conditions — stubs will be written post-hoc.

# Era 2 — 384 px, 487 tiles
run_stratum 2 "consensus"       "READY" "$BOUNDS_E2"
run_stratum 2 "single-pass"     "SINGLE_PASS_ONLY" "$BOUNDS_E2"
run_stratum 2 "single-pass+PV"  "PV_READY" "$BOUNDS_E2"
run_stratum 2 "pv"              "READY" "$BOUNDS_E2"

# Era 3 — 384 px, 327 tiles
run_stratum 3 "consensus"       "READY" "$BOUNDS_E3"
# Era 3 has no single-pass, single-pass+PV, or pv conditions — stubs will be
# written post-hoc.

echo "ALL STRATA COMPLETE"
