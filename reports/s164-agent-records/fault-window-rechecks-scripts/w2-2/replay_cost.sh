#!/usr/bin/env bash
# ============================================================================
# replay_cost.sh -- W2-2: replay scripts/final_board_cost_refresh.py --write at
# b044c486e (the last commit to touch the board's cost axis; amd-tower,
# 2026-10-05) from the board JSON/MD as committed at b044c486e^, then compare
# with `git show b044c486e:<path>`. Reads the pricing register only.
# Usage: replay_cost.sh <full-tree-at-b044c486e> <outdir>
# Zero API, seconds. Author: Claude (Opus 5.5), S164 W2-2 sub-agent, 2026-10-14.
# ============================================================================
set -euo pipefail
tree=$1; outdir=$2; c=b044c486e
PY=$HOME/Code/map-reader-llm/.venv/bin/python
FB=results/55map-final-board-r2-2026-09-06
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
cd "$tree"
echo "tree head $(git rev-parse --short HEAD); inputs from ${c}^ ($(git rev-parse --short ${c}^))"
git show "${c}^:$FB/final_board_50m.json" > "$FB/final_board_50m.json"
git show "${c}^:$FB/final-board-50m.md" > "$FB/final-board-50m.md"
"$PY" scripts/final_board_cost_refresh.py --write
mkdir -p "$outdir"
cp "$FB/final_board_50m.json" "$FB/final-board-50m.md" "$outdir/"
for f in final_board_50m.json final-board-50m.md; do
  if git show "$c:$FB/$f" | cmp -s - "$FB/$f"; then echo "$f: IDENTICAL to $c"; else echo "$f: DIFFERS from $c"; fi
done
git checkout -q -- "$FB"
