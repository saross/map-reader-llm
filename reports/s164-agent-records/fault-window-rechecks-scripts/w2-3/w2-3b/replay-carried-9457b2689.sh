#!/usr/bin/env bash
# Replay of 9457b2689 (carried point for the committed K = 5 / 10 rungs).
# The original ran derive_k_ladder_committed_carried.py prepare in sapphire's
# LIVE checkout (HEAD f724b7a10, with the script rsynced in from the branch;
# its third and final version, committed as 9457b2689) at
# 2026-09-12T06:36:03Z (transcript, agent-ae87367bcee3e0e5c), then scored the
# 52 cells (census-verified, not re-run here). Replayed at 9457b2689. Also
# confirmed in W2 itself: stage 5 of final_downstream.sh (08:41Z) re-ran
# prepare and left all 52 materialised files and the jobs file unchanged in
# git (their last change is 9457b2689).
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
TREE=$ROOT/w2-3b-9457b2689
source "$ROOT/env.sh"
cd "$TREE" || exit 1
echo "start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) PYTHONHASHSEED=${PYTHONHASHSEED:-unset}"
C=results/k-ladder-2026-09-12/phase2/committed-carried
rm -rf "$C"/materialised; rm -f "$C"/operating-points.json results/k-ladder-2026-09-12/phase2/committed-carried-jobs.txt
$PY scripts/derive_k_ladder_committed_carried.py prepare
echo "exit=$? end $(date -u +%FT%TZ)"
