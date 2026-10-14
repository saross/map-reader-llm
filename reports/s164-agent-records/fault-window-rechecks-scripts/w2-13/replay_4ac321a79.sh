#!/usr/bin/env bash
# replay_4ac321a79.sh -- W2-13 fault-window re-check (Session 164, 2026-10-14).
# Replays the June image pool grid committed in 4ac321a79 (saross, sapphire)
# at that commit, in a detached replay worktree: --stage gate, --stage sweep
# (1 worker; the original used the documented 12, and pool.map's results are
# re-sorted, so the worker count cannot reorder rows), --stage materialise.
# The score stage (cb12de12b) is NOT replayed: the census already reproduces
# its four evaluation.json files.  Zero API.
# Usage: replay_4ac321a79.sh <replay-tree> <out-dir>
set -uo pipefail
TREE="$1"; OUT="$2"
PY=~/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$TREE"
git checkout -q --force --detach 4ac321a79
echo "HEAD $(git rev-parse --short HEAD)"
R=results/im-june-pool-grid-2026-09-20
for stage in gate sweep materialise; do
  echo "== $stage $(date -u +%FT%TZ)"
  $PY scripts/im_june_pool_grid.py --stage "$stage" --workers 1
  echo "exit=$?"
done
echo "== done $(date -u +%FT%TZ)"
mkdir -p "$OUT"
cp -r "$R" "$OUT/"
git status --short | head -20
