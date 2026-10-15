#!/usr/bin/env bash
# Replay of b7e2821ba (per-family Hsu MCB sets for the 22 K ladders): the
# original ran k_ladder_mcb.py (all defaults) in the sapphire worktree
# claude-mcb at cebae7868 on 2026-09-13T02:37:43Z (transcript,
# agent-a024baa5a44063c67); b7e2821ba adds only its outputs and docs on top,
# plus a two-line change to build_k_ladder_phase2_tables.py, which the MCB
# driver does not import. 10,000 tile bootstrap resamples, seed 42. One process.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
TREE=$ROOT/w2-3b-cebae7868
source "$ROOT/env.sh"
cd "$TREE" || exit 1
echo "start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) PYTHONHASHSEED=${PYTHONHASHSEED:-unset}"
rm -rf results/k-ladder-2026-09-12/mcb
$PY scripts/k_ladder_mcb.py
echo "exit=$? end $(date -u +%FT%TZ)"
