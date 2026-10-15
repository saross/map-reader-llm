#!/usr/bin/env bash
# replay_61870d9e7.sh -- W2-13 fault-window re-check (Session 164, 2026-10-14).
# Replays the three frontier builders whose outputs 61870d9e7 committed
# (Pareto v2, K-ladder Phase 1, K-ladder Phase 2) at their source commit
# 61ab7a446 (the stamp in phase2/ladder-tables.md; scripts identical to
# 61870d9e7), in a detached replay worktree, single-threaded.  Zero API.
# Usage: replay_61870d9e7.sh <replay-tree> <out-dir>
set -euo pipefail
TREE="$1"; OUT="$2"
PY=~/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$TREE"
git checkout -q --detach 61ab7a446
echo "HEAD $(git rev-parse --short HEAD)"
mkdir -p "$OUT"
echo "== build_pareto_v2 $(date -u +%FT%TZ)"
$PY scripts/build_pareto_v2.py
echo "== build_k_ladder_tables $(date -u +%FT%TZ)"
$PY scripts/build_k_ladder_tables.py
echo "== build_k_ladder_phase2_tables $(date -u +%FT%TZ)"
$PY scripts/build_k_ladder_phase2_tables.py
echo "== done $(date -u +%FT%TZ)"
for f in results/verifier-robustness/pareto/pareto_v2.json results/verifier-robustness/pareto/pareto_v2.png \
         results/k-ladder-2026-09-12/ladders.json results/k-ladder-2026-09-12/figures/k-ladder-pareto.png \
         results/k-ladder-2026-09-12/phase2/ladders.json results/k-ladder-2026-09-12/phase2/ladders-compat.json \
         results/k-ladder-2026-09-12/phase2/ladder-tables.md results/k-ladder-2026-09-12/figures/k-ladder-pareto-phase2.png; do
  mkdir -p "$OUT/$(dirname $f)"; cp "$f" "$OUT/$f"
done
git status --short
