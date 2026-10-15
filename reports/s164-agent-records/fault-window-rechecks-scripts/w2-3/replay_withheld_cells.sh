#!/usr/bin/env bash
# W2-3 (and two of W2-14's cells): re-score the two Gemini 3.7 K = 1 Phase 2
# cells whose census replay could not reproduce their intervals and tile MCC
# ("W-tile-join-withheld": the census's later code refuses the name-based tile
# join these cells were scored with). Replayed at 326181bcd, the commit that
# committed them; its scripts are the branch's scripts that the original run
# copied into sapphire's live checkout (HEAD f724b7a10, "dirty"), and neither
# commit has the tile-join invariant 7ba47b63b. Commands are the cells' lines
# of phase2/score-jobs.txt (lines 44 and 45), with --output-dir pointed at
# scratch. One process, PYTHONHASHSEED unset as originally.
# Usage: replay_withheld_cells.sh <out dir>
set -u
O=$1
S=$HOME/scratch/s164-fw-recheck2-2026-10-15
T=$S/w2-3-cells-326181bcd
source "$S/env.sh"
git -C "$HOME/Code/map-reader-llm" worktree add --detach "$T" 326181bcd > /dev/null 2>&1 \
  || { echo "worktree add failed"; exit 1; }
cd "$T" || exit 9
echo "=== $(date -u +%FT%TZ) at $(git rev-parse --short HEAD)"
for label in g37-text-k1-verified-opmax g37-text-k1-verified-carried-p0.10-k1; do
  cell=gemini37-screen-2026-08-28__${label//./_}
  "$PY" scripts/evaluate_detections.py \
    --detections "results/k-ladder-2026-09-12/phase2/materialised/$label.geojson" \
    --ground-truth inputs/vectors/references/mounds-reference.geojson \
    --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \
    --buffers 5 10 15 20 25 30 35 40 45 50 75 100 125 150 --bootstrap 10000 --seed 42 \
    --mcc --output-dir "$O/$cell" --label "$label" > "$O/$cell.log" 2>&1
  echo "$label rc=$?"
done
cd "$S" || exit 9
git -C "$HOME/Code/map-reader-llm" worktree remove --force "$T"
echo "=== $(date -u +%FT%TZ) DONE"
