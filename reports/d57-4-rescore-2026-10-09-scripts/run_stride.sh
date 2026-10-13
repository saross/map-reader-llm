#!/usr/bin/env bash
# ============================================================================
# run_stride.sh
# ----------------------------------------------------------------------------
# D57 (4) re-score, 2026-10-09 (Session 163); plan § 3.2.
#
# Runs the two 55-map stride drivers IN ONE TREE, in order:
#   1. scripts/stride55_sweep_oracle.py  (writes the tree's own
#      results/stride55-2026-08-27/{<cell>/sweep_50m.csv, sweep_oracle.json};
#      replication gate at each primary point to 1e-6)
#   2. scripts/stride55_ladder.py        (writes <cell>/ladder_sweep_50m.csv and
#      ladder.json under the same directory; union and primary gates)
# The second runs only if the first exits 0 (set -e). Each driver derives its
# PROJECT_ROOT from its own __file__, so pointing this at the OLD tree
# (git archive of b3c52591d) writes only into that scratch tree, and at the
# NEW worktree writes in place there. No API call is made by either driver.
#
# Usage:
#   run_stride.sh <tree> <log-dir> <tag>
# The script writes <log-dir>/stride_<tag>.pid, one log per driver, and a
# final "STRIDE <tag> DONE" line in the ladder log.
# ============================================================================
set -euo pipefail
TREE="$1"
LOGS="$2"
TAG="$3"
PY="$HOME/Code/map-reader-llm/.venv/bin/python"
echo $$ > "$LOGS/stride_${TAG}.pid"
cd "$TREE"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
"$PY" scripts/stride55_sweep_oracle.py > "$LOGS/stride_${TAG}_sweep.log" 2>&1
"$PY" scripts/stride55_ladder.py > "$LOGS/stride_${TAG}_ladder.log" 2>&1
echo "STRIDE ${TAG} DONE" >> "$LOGS/stride_${TAG}_ladder.log"
