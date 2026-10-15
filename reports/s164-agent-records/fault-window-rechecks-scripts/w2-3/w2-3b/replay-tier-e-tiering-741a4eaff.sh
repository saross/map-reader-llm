#!/usr/bin/env bash
# Replay of the tier E tiering committed in 741a4eaff (ladder.json,
# tiering-input/run-{analyses,conditions}.json, tiering/tiering_20m.{json,md}).
# The original ran in the sapphire worktree claude-closeout on 2026-09-12
# (transcript, agent-ae1e65fd9508397ec): register_and_regen.sh at 14:24:03Z
# wrote the tier E register rows, then tier_e_ladder_tiering.py ran three times
# as the script was fixed (14:26:30Z 2ca2484df, 14:27:48Z 777ddc67c, 14:28:43Z
# a881a9aca); the last run's outputs were committed in 741a4eaff at 14:35:57Z.
# 741a4eaff carries the a881a9aca script, the register rows that run read, and
# the other scripts and tier E inputs of 5167b9a5c unchanged, so the replay runs
# at 741a4eaff with the script defaults (10,000 permutations, seed 42,
# --permute-mcc). One process.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
TREE=$ROOT/w2-3b-741a4eaff
source "$ROOT/env.sh"
cd "$TREE" || exit 1
echo "start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) PYTHONHASHSEED=${PYTHONHASHSEED:-unset}"
T=results/k-ladder-2026-09-12/tier-e
rm -rf "$T"/tiering "$T"/tiering-input; rm -f "$T"/ladder.json
$PY scripts/tier_e_ladder_tiering.py
echo "exit=$? end $(date -u +%FT%TZ)"
