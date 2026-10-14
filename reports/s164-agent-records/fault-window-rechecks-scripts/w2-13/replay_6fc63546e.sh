#!/usr/bin/env bash
# replay_6fc63546e.sh -- W2-13 fault-window re-check (Session 164, 2026-10-14).
# Replays the tile-presence cost regeneration committed in 6fc63546e (saross,
# sapphire) at that commit, in a detached replay worktree, single process:
#   1. the builder's own drift guard, --stage all --check (writes nothing);
#   2. a real write of --stage costs then --stage leaderboard, so the outputs
#      can be compared with `git show 6fc63546e:<path>` independently.
# Zero API (the cost auditor reads metas and the passes register only).
# Usage: replay_6fc63546e.sh <replay-tree> <out-dir>
set -uo pipefail
TREE="$1"; OUT="$2"
PY=~/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$TREE"
git checkout -q --force --detach 6fc63546e
echo "HEAD $(git rev-parse --short HEAD)"
echo "== --stage all --check $(date -u +%FT%TZ)"
$PY scripts/build_tile_presence_board.py --stage all --check
echo "check exit=$?"
for stage in costs leaderboard; do
  echo "== --stage $stage (write) $(date -u +%FT%TZ)"
  $PY scripts/build_tile_presence_board.py --stage "$stage"
  echo "exit=$?"
done
echo "== done $(date -u +%FT%TZ)"
mkdir -p "$OUT"
cp results/tile-presence-2026-09-21/verifier-costs.json results/tile-presence-2026-09-21/leaderboard.json \
   results/tile-presence-2026-09-21/leaderboard.md "$OUT/"
git status --short | head
