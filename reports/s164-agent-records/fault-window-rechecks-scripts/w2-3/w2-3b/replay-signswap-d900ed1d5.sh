#!/usr/bin/env bash
# Replay of d900ed1d5 (per-map paired sign-swap on the two Gemini 3 stride
# ladders): the original ran, in a sapphire worktree at 156bddf36 with the
# then-uncommitted stride55_ladder.py and stride55_sweep_oracle.py copied in
# (committed as d900ed1d5), on 2026-09-12T06:17:05Z (transcript,
# agent-abd98f8d810855618):
#   stride55_ladder.py --reuse-oracles \
#     --output-dir results/k-ladder-2026-09-12/mcc-test/sign-swap/rebuild \
#     --pairs-output-dir results/k-ladder-2026-09-12/mcc-test/sign-swap
# Replayed at d900ed1d5. 10,000 permutations, seed 42 (constants). One process.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
TREE=$ROOT/w2-3b-d900ed1d5
source "$ROOT/env.sh"
cd "$TREE" || exit 1
echo "start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) PYTHONHASHSEED=${PYTHONHASHSEED:-unset}"
rm -rf results/k-ladder-2026-09-12/mcc-test/sign-swap
$PY scripts/stride55_ladder.py --reuse-oracles \
    --output-dir results/k-ladder-2026-09-12/mcc-test/sign-swap/rebuild \
    --pairs-output-dir results/k-ladder-2026-09-12/mcc-test/sign-swap
echo "exit=$? end $(date -u +%FT%TZ)"
