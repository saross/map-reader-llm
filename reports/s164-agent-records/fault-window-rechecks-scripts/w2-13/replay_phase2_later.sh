#!/usr/bin/env bash
# replay_phase2_later.sh -- W2-13 fault-window re-check (Session 164, 2026-10-14).
# Replays the two later sapphire regenerations of the K-ladder Phase 2 tables
# that today's committed files come from: 2e0c2941d (source commit 5eaa8cb9f,
# builder v1.2.0) and 32d0c6445 (source commit 9cab57ad9, builder v1.2.1).
# Each runs at the source commit stamped in its own ladder-tables.md, in a
# detached replay worktree, single-threaded.  Zero API.
# Usage: replay_phase2_later.sh <replay-tree> <out-base>
set -euo pipefail
TREE="$1"; OUTBASE="$2"
PY=~/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$TREE"
for SRC in 5eaa8cb9f 9cab57ad9; do
  git checkout -q --force --detach "$SRC"
  echo "== HEAD $(git rev-parse --short HEAD) $(date -u +%FT%TZ)"
  $PY scripts/build_k_ladder_phase2_tables.py
  OUT="$OUTBASE/phase2-at-$SRC"
  for f in results/k-ladder-2026-09-12/phase2/ladders.json \
           results/k-ladder-2026-09-12/phase2/ladders-compat.json \
           results/k-ladder-2026-09-12/phase2/ladder-tables.md \
           results/k-ladder-2026-09-12/figures/k-ladder-pareto-phase2.png; do
    mkdir -p "$OUT/$(dirname "$f")"; cp "$f" "$OUT/$f"
  done
  git status --short
done
echo "== done $(date -u +%FT%TZ)"
