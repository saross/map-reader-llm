#!/usr/bin/env bash
# Replay of 326181bcd's phase2/mcc-test (13 gold-standard Phase 2 ladders,
# board tile-swap + MCC, 10,000 permutations, seed 42). The original was stage
# 12 of final_downstream.sh in sapphire's LIVE checkout (HEAD f724b7a10 with
# the branch's scripts rsynced in; committed as 326181bcd), 2026-09-12T08:51:23Z
# (transcript, agent-ae87367bcee3e0e5c):
#   k_ladder_mcc_test.py --ladders results/k-ladder-2026-09-12/phase2/ladders-compat.json \
#     --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \
#     --output-dir results/k-ladder-2026-09-12/phase2/mcc-test
# It resolved the rungs through results/run-conditions.json as stage 8 had just
# written it (08:51:04Z); those 46 rows were committed one commit later, in
# 3c5de3f23 (child of 326181bcd, which changes only the register, manifests
# and uplift files: no script, no K-ladder result). So the replay runs at
# 3c5de3f23. One process.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
TREE=$ROOT/w2-3b-3c5de3f23
source "$ROOT/env.sh"
cd "$TREE" || exit 1
echo "start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) PYTHONHASHSEED=${PYTHONHASHSEED:-unset}"
rm -rf results/k-ladder-2026-09-12/phase2/mcc-test
$PY scripts/k_ladder_mcc_test.py \
    --ladders results/k-ladder-2026-09-12/phase2/ladders-compat.json \
    --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \
    --output-dir results/k-ladder-2026-09-12/phase2/mcc-test
echo "exit=$? end $(date -u +%FT%TZ)"
