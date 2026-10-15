#!/usr/bin/env bash
# Replay of 5167b9a5c (tier E outputs, the tension analyses, the h10 rebuild)
# at 5167b9a5c. Every script these stages run (run_k_ladder_tier_e.py of
# b7b3e149b, k_ladder_tension_analyses.py of 95a2a3231, merge_passes.py,
# run_pv.py, sweep_f1_greedy_pv.py, materialise_pv_geojson.py) is the blob
# 5167b9a5c carries. The originals ran in the sapphire worktree claude-closeout
# on 2026-09-12 (transcript, agent-ae1e65fd9508397ec):
#   13:40:24Z  verify (per rung: run_pv.py extract, then a real-time verify:
#              API; only the extract is replayed, with the same arguments)
#   13:40:51Z  merge_passes.py --input-dir outputs/h10/evaluation-v2/pool_160_hp4hn4
#              --output-dir /tmp/h10-rebuild --sweep; t1, t2 and voting_summary
#              copied over the committed consensus
#   13:53:32Z  k_ladder_tension_analyses.py --all --draws 200 (code of 50e4a6845;
#              the subsample and grid-overlap code is unchanged at 95a2a3231)
#   13:58:58Z  k_ladder_tension_analyses.py --effect-sizes --grid-overlap (95a2a3231)
#              tier-e/scores.json did not exist yet, so it is held aside here
#   14:15:18Z  prepare (b7b3e149b), score jobs (census-verified, not re-run),
#              the in-place sed of score-jobs.txt, collect
set -u
ROOT=$HOME/scratch/s164-fw-recheck2-2026-10-15
TREE=$ROOT/w2-3b-5167b9a5c
LIVE=$HOME/Code/map-reader-llm
OUT=$ROOT/w2-3b-out/tier-e-5167b9a5c
source "$ROOT/env.sh"
cd "$TREE" || exit 1
echo "start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD) PYTHONHASHSEED=${PYTHONHASHSEED:-unset}"
mkdir -p inputs/rasters "$OUT"
cp -p "$LIVE"/inputs/rasters/K-35-0*.tif "$LIVE"/inputs/rasters/K-35-0*.tif.aux.xml inputs/rasters/
cp -rp "$LIVE"/inputs/tiles_384_ov192 inputs/
T=results/k-ladder-2026-09-12/tier-e

echo "=== 1. tension analyses (tier-e/scores.json held aside) $(date -u +%T)"
mv "$T"/scores.json "$OUT"/scores.json.held
rm -f results/k-ladder-2026-09-12/tension/*.json
$PY scripts/k_ladder_tension_analyses.py --all --draws 200
echo "tension exit=$?"
mv "$OUT"/scores.json.held "$T"/scores.json

echo "=== 2. h10 consensus rebuild $(date -u +%T)"
H=outputs/h10/evaluation-v2/pool_160_hp4hn4
rm -rf "$OUT"/h10-rebuild; mkdir -p "$OUT"/h10-rebuild
$PY scripts/merge_passes.py --input-dir "$H" --output-dir "$OUT"/h10-rebuild --sweep
echo "merge exit=$?"
cp -p "$OUT"/h10-rebuild/consensus_t1.geojson "$OUT"/h10-rebuild/consensus_t2.geojson \
    "$OUT"/h10-rebuild/voting_summary.json "$H"/consensus/

echo "=== 3. prepare: sweeps on both frames, operating points, materialise $(date -u +%T)"
for k in 1 3 5; do
    rm -f outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k$k/sweep_board.json \
          outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k$k/sweep_era2.json
done
rm -rf "$T"/materialised; rm -f "$T"/operating-points.json "$T"/score-jobs.txt
$PY scripts/run_k_ladder_tier_e.py prepare
echo "prepare exit=$?"
sed -i "s|^python |.venv/bin/python |" "$T"/score-jobs.txt

echo "=== 4. collect (reads the committed, census-verified evaluations) $(date -u +%T)"
rm -f "$T"/scores.json
$PY scripts/run_k_ladder_tier_e.py collect
echo "collect exit=$?"

echo "=== 5. crop extraction for the three verifier stages (no verify) $(date -u +%T)"
for k in 1 3 5; do
    C=outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k$k/crops
    rm -rf "$C"
    $PY scripts/run_pv.py extract \
        --proposer outputs/grid-2026-08-18/g384_ov192/consensus-n$k/consensus_t1.geojson \
        --output-dir "$C" --padding 75 --tiles-dir inputs/tiles_384_ov192
    echo "extract k$k exit=$?"
done
echo "end $(date -u +%FT%TZ)"
