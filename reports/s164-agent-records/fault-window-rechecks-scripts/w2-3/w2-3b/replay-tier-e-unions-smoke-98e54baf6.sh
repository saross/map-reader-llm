#!/usr/bin/env bash
# Replay of 98e54baf6 (tier E unions and smoke artefacts). The original ran,
# in the sapphire worktree claude-closeout (inputs/rasters and the tile
# directories symlinked from the live checkout), on 2026-09-12 (transcript,
# agent-ae1e65fd9508397ec):
#   13:36:17Z  run_k_ladder_tier_e.py unions        (driver of 98b43e3be)
#   13:37:30Z  run_k_ladder_tier_e.py smoke         (extract + a 5-candidate
#              real-time verify, i.e. an API call)
# The union code, merge_passes.py and run_pv.py extract are identical at
# 98e54baf6, so the replay runs there. The smoke stage is replayed with
# --plan-only (union slice and crop extraction only, NO API call); the smoke
# record smoke.json is re-derived offline from the committed probabilities
# and meta by rederive_tier_e_records.py. Inputs the replay needs that are
# untracked on sapphire (the four gold-standard rasters and the 384 px / 192 px
# stride tiles) are COPIED in, read-only from the live checkout.
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
TREE=$ROOT/w2-3b-98e54baf6
LIVE=$HOME/Code/map-reader-llm
source "$ROOT/env.sh"
cd "$TREE" || exit 1
echo "start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) PYTHONHASHSEED=${PYTHONHASHSEED:-unset}"
mkdir -p inputs/rasters
cp -p "$LIVE"/inputs/rasters/K-35-0*.tif "$LIVE"/inputs/rasters/K-35-0*.tif.aux.xml inputs/rasters/
cp -rp "$LIVE"/inputs/tiles_384_ov192 inputs/
sha256sum inputs/rasters/K-35-0*.tif
P=outputs/grid-2026-08-18/g384_ov192
rm -rf "$P"/consensus-n1 "$P"/consensus-n3 "$P"/consensus-n5
rm -f results/k-ladder-2026-09-12/tier-e/unions.json
rm -rf results/k-ladder-2026-09-12/tier-e/smoke/crops results/k-ladder-2026-09-12/tier-e/smoke/union_first5.geojson
$PY scripts/run_k_ladder_tier_e.py unions
echo "unions exit=$?"
$PY scripts/run_k_ladder_tier_e.py smoke --plan-only
echo "smoke exit=$? end $(date -u +%FT%TZ)"
