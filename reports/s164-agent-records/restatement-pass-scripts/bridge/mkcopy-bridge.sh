#!/usr/bin/env bash
# mkcopy-bridge.sh — disposable copy for the bridge floors / verifier-SD trial
# Code and committed data from the pass worktree HEAD (git archive, read only);
# gitignored prepared passes from the shared checkout (read only); the REPAIRED
# bridge cell outputs and gap tests overlaid from the S164 rescore's repairedA.
# Usage: mkcopy-bridge.sh <dest>
set -euo pipefail
DEST=$1
WT=$HOME/scratch/s164-restate-2026-10-15/wt
SHARED=$HOME/Code/map-reader-llm
RA=$HOME/scratch/s164-rescore-2026-10-13/copies/repairedA
mkdir -p "$DEST"
git -C "$WT" archive HEAD -- scripts config.py pyproject.toml pytest.ini | tar -x -C "$DEST"
git -C "$WT" archive HEAD -- inputs/vectors inputs/grid-2026-08-18 inputs/stride-phaseb-2026-08-25 \
  inputs/image-b-gs-2026-08-28 \
  outputs/grid-2026-08-18 outputs/image-b-gs-2026-08-28 outputs/gemini37-screen-2026-08-28 \
  outputs/gemini37-image-gs-2026-09-01 outputs/modality-bridge-2026-10-07 \
  results/modality-bridge-2026-10-07 \
  reports/w27-replicate-floors-2026-10-06-scripts/gs_consensus_pairs.csv | tar -x -C "$DEST"
for a in g3-text g3-image g37-text g37-image g37-image-cache g3-text-temp1 g3-image-temp1; do
  d=outputs/modality-bridge-2026-10-07/$a/scoring
  mkdir -p "$DEST/$d"; cp -a "$SHARED/$d/." "$DEST/$d/"
done
# The 3.7 image GS cell's prepared passes (gitignored; the trial's origin step reads them).
d=outputs/gemini37-image-gs-2026-09-01/scoring
mkdir -p "$DEST/$d"; cp -a "$SHARED/$d/." "$DEST/$d/"
# Overlay the REPAIRED cells and gap tests (not floors/, verifier-sd/, logs/, findings.md).
R=results/modality-bridge-2026-10-07
for c in g3-text-g3v g3-image-g3v g37-text-g3v g37-text-g37v g37-image-g3v g37-image-g37v \
         g37-image-cache-g3v g37-image-cache-g37v g3-text-temp1-g3v g3-image-temp1-g3v k5 additions; do
  rm -rf "$DEST/$R/$c"; cp -a "$RA/$R/$c" "$DEST/$R/$c"
done
cp -a "$RA/$R/gap_test.json" "$DEST/$R/gap_test.json"
mkdir -p "$DEST/.venv/bin"; ln -sf "$SHARED/.venv/bin/python" "$DEST/.venv/bin/python"
printf 'code+data %s (worktree HEAD)\ncells %s\n' "$(git -C "$WT" rev-parse HEAD)" "$RA" > "$DEST/.source-commits"
echo COPY-DONE
