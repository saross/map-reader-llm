#!/usr/bin/env bash
# Replay of d10137595 (K-ladder tile-MCC test, board instrument): the
# original ran k_ladder_mcc_test.py --output-dir results/k-ladder-2026-09-12/mcc-test
# at 156bddf36 in a sapphire worktree on 2026-09-12T06:10:59Z (transcript,
# agent-abd98f8d810855618). d10137595 changes no script and no input relative
# to 156bddf36, so the replay runs at d10137595. Round-robin tile-swap,
# 10,000 permutations, seed 42 (the driver defaults), one process.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
TREE=$ROOT/w2-3b-d10137595
source "$ROOT/env.sh"
cd "$TREE" || exit 1
echo "start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) PYTHONHASHSEED=${PYTHONHASHSEED:-unset}"
rm -rf results/k-ladder-2026-09-12/mcc-test
$PY scripts/k_ladder_mcc_test.py --output-dir results/k-ladder-2026-09-12/mcc-test
echo "exit=$? end $(date -u +%FT%TZ)"
