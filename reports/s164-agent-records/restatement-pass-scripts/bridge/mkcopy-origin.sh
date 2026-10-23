#!/usr/bin/env bash
# mkcopy-origin.sh — ORIGIN control copy: code at the pass worktree's 540e66680,
# bridge and original-leg data at be252e57b (before PR #43 booked the 2026-10-13
# re-verified rows), committed bridge cells (unchanged since be252e57b).
# Usage: mkcopy-origin.sh <dest>
set -euo pipefail
DEST=$1
WT=$HOME/scratch/s164-restate-2026-10-15/wt
SHARED=$HOME/Code/map-reader-llm
mkdir -p "$DEST"
git -C "$WT" archive 540e66680 -- scripts config.py pyproject.toml pytest.ini | tar -x -C "$DEST"
git -C "$WT" archive be252e57b -- inputs/vectors inputs/grid-2026-08-18 inputs/stride-phaseb-2026-08-25 \
  inputs/image-b-gs-2026-08-28 \
  outputs/grid-2026-08-18 outputs/image-b-gs-2026-08-28 outputs/gemini37-screen-2026-08-28 \
  outputs/gemini37-image-gs-2026-09-01 outputs/modality-bridge-2026-10-07 \
  results/modality-bridge-2026-10-07 \
  reports/w27-replicate-floors-2026-10-06-scripts/gs_consensus_pairs.csv | tar -x -C "$DEST"
for a in g3-text g3-image g37-text g37-image g37-image-cache g3-text-temp1 g3-image-temp1; do
  d=outputs/modality-bridge-2026-10-07/$a/scoring
  mkdir -p "$DEST/$d"; cp -a "$SHARED/$d/." "$DEST/$d/"
done
d=outputs/gemini37-image-gs-2026-09-01/scoring
mkdir -p "$DEST/$d"; cp -a "$SHARED/$d/." "$DEST/$d/"
printf 'code 540e66680\ndata be252e57b\n' > "$DEST/.source-commits"
echo COPY-DONE
