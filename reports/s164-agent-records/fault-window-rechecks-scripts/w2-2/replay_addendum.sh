#!/usr/bin/env bash
# ============================================================================
# replay_addendum.sh -- W2-2: replay scripts/final_board_addendum_render.py at
# commit C (de009ed5d, then 892633660; both sapphire, 2026-09-20) starting from
# the board JSON/MD as committed at C^ (the renderer's input state), then
# compare the regenerated JSON/MD with `git show C:<path>`.
# Usage: replay_addendum.sh <sparse-tree> <commit> <outdir>
# Zero API, seconds. Author: Claude (Opus 5.5), S164 W2-2 sub-agent, 2026-10-14.
# ============================================================================
set -euo pipefail
tree=$1; c=$2; outdir=$3
PY=$HOME/Code/map-reader-llm/.venv/bin/python
FB=results/55map-final-board-r2-2026-09-06
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
cd "$tree"
git checkout -q --force "$c"
echo "tree head $(git rev-parse --short HEAD); inputs from ${c}^ ($(git rev-parse --short ${c}^))"
git show "${c}^:$FB/final_board_50m.json" > "$FB/final_board_50m.json"
git show "${c}^:$FB/final-board-50m.md" > "$FB/final-board-50m.md"
"$PY" scripts/final_board_addendum_render.py --reference r2
mkdir -p "$outdir"
cp "$FB/final_board_50m.json" "$FB/final-board-50m.md" "$outdir/"
for f in final_board_50m.json final-board-50m.md; do
  if git show "$c:$FB/$f" | cmp -s - "$FB/$f"; then echo "$f: IDENTICAL to $c"; else echo "$f: DIFFERS from $c"; fi
done
git checkout -q --force "$c"   # restore the tree to the commit
