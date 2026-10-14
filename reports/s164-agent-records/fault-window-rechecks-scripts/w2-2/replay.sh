#!/usr/bin/env bash
# ============================================================================
# replay.sh -- W2-2 fault-window re-check: replay the three r2 board builders
# at their generating commit 22353e660 (step 4e) in a detached replay tree.
#
# Usage: replay.sh <job> <tree> <outdir> <pythonhashseed>
#   job  = final  -> scripts/final_board_build.py --reference r2
#          lbmcc  -> scripts/build_55map_leaderboard.py --reference r2, then
#                    scripts/mcc_tiering_55map.py --reference r2
#   tree = replay worktree root checked out at 22353e660 (script cwd)
#   outdir = where the regenerated outputs are copied after the run
#
# Zero API: all three builders read committed detections/evaluations and run
# local tile-swap permutations (10,000, seed 42). Single-threaded BLAS/OpenMP
# so each job holds one core (W2-2 budget: 2 workers in total).
# Author: Claude (Opus 5.5), Session 164 re-check sub-agent, 2026-10-14.
# ============================================================================
set -euo pipefail
job=$1; tree=$2; outdir=$3; seed=$4
PY=$HOME/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
       NUMEXPR_NUM_THREADS=1 PYTHONHASHSEED=$seed MPLBACKEND=Agg
cd "$tree"
echo "job=$job tree=$tree head=$(git rev-parse HEAD) PYTHONHASHSEED=$seed start=$(date -u +%FT%TZ)"
mkdir -p "$outdir"
case $job in
  final)
    "$PY" scripts/final_board_build.py --reference r2
    cp results/55map-final-board-r2-2026-09-06/final_board_50m.json \
       results/55map-final-board-r2-2026-09-06/final-board-50m.md \
       results/55map-final-board-r2-2026-09-06/significance-groups.png "$outdir/"
    ;;
  lbmcc)
    "$PY" scripts/build_55map_leaderboard.py --reference r2
    "$PY" scripts/mcc_tiering_55map.py --reference r2
    cp results/55map-leaderboard/55map_leaderboard_50m_r2.json \
       results/55map-leaderboard/55map-leaderboard-50m-r2.md \
       results/metric-leaderboards/55map-mcc-tiering-r2.json \
       results/metric-leaderboards/55map-mcc-tiering-r2.md "$outdir/"
    ;;
  *) echo "unknown job $job"; exit 64 ;;
esac
echo "job=$job DONE end=$(date -u +%FT%TZ)"
