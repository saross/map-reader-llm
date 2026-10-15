#!/usr/bin/env bash
# replay_3d6b47e33.sh -- W2-13 fault-window re-check (Session 164, 2026-10-14).
# Replays the tile-join audit committed in 3d6b47e33 (PI ruling 6) at that
# commit, in a detached replay worktree, single-threaded.  Zero API.
# The commit body does not record the three command lines; they are
# reconstructed from the committed JSON (every row's evaluation / detections
# / bounds paths, glob-sorted) and the script's own usage block:
#   board-era2:            --evaluation-glob over the signed Era-2 board's cells
#   k-ladder-phase2-cells: --evaluation-glob over phase2/cells/*/evaluation.json
#   k-ladder-phase2:       --detections-glob over phase2/materialised/*.geojson
#                          against era2_b_intersection_bounds (default GT)
# Usage: replay_3d6b47e33.sh <replay-tree> <out-dir>
set -uo pipefail
TREE="$1"; OUT="$2"
PY=~/Code/map-reader-llm/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$TREE"
git checkout -q --force --detach 3d6b47e33
echo "HEAD $(git rev-parse --short HEAD)"
mkdir -p "$OUT"
echo "== board-era2 $(date -u +%FT%TZ)"
$PY scripts/audit_tile_join_variants.py \
  --evaluation-glob 'results/leaderboard/era2/gs-era2-verified-board-2026-09-10/cells/*/evaluation.json' \
  --json-out "$OUT/board-era2-2026-09-12.json" --markdown-out "$OUT/board-era2-2026-09-12.md"
echo "exit=$?"
echo "== k-ladder-phase2-cells $(date -u +%FT%TZ)"
$PY scripts/audit_tile_join_variants.py \
  --evaluation-glob 'results/k-ladder-2026-09-12/phase2/cells/*/evaluation.json' \
  --json-out "$OUT/k-ladder-phase2-cells-2026-09-12.json" \
  --markdown-out "$OUT/k-ladder-phase2-cells-2026-09-12.md"
echo "exit=$?"
echo "== k-ladder-phase2 $(date -u +%FT%TZ)"
$PY scripts/audit_tile_join_variants.py \
  --detections-glob 'results/k-ladder-2026-09-12/phase2/materialised/*.geojson' \
  --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \
  --json-out "$OUT/k-ladder-phase2-2026-09-12.json" \
  --markdown-out "$OUT/k-ladder-phase2-2026-09-12.md"
echo "exit=$?"
echo "== done $(date -u +%FT%TZ)"
git status --short | head
