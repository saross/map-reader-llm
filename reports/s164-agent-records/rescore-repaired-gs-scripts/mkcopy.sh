#!/usr/bin/env bash
# =============================================================================
# mkcopy.sh — one disposable, real-file copy of what the S164 re-score reads
# =============================================================================
# Code (scripts, config) comes from CODE_REF; data (inputs, outputs, results)
# from DATA_REF. ORIGIN copies take their data from main as it was before
# PR #43 (0e8a1fa7a^1), so no re-verified row exists anywhere in them; the
# REPAIRED copies take everything from the branch head. The gitignored
# prepared-pass directories the Gemini 3.7 image and bridge cells need are
# copied, read only, from sapphire's shared checkout (the chain's row-for-row
# union gate checks them against the committed unions).
#
# Usage: mkcopy.sh <code_ref> <data_ref> <dest>
# =============================================================================
set -euo pipefail
CODE_REF=$1; DATA_REF=$2; DEST=$3
REPO=$HOME/scratch/s164-merges-2026-10-13/wt
SHARED=$HOME/Code/map-reader-llm
mkdir -p "$DEST"
git -C "$REPO" archive "$CODE_REF" -- scripts config.py pyproject.toml pytest.ini \
  | tar -x -C "$DEST"
git -C "$REPO" archive "$DATA_REF" -- \
  inputs/vectors inputs/grid-2026-08-18 inputs/stride-phaseb-2026-08-25 \
  inputs/image-b-gs-2026-08-28 \
  outputs/grid-2026-08-18 outputs/stride-phaseb-2026-08-25 outputs/stride-phasec-2026-08-25 \
  outputs/image-b-gs-2026-08-28 outputs/era1-pv-stage-d/384-consensus-text-high \
  outputs/gemini37-screen-2026-08-28 outputs/gemini37-image-gs-2026-09-01 \
  outputs/modality-bridge-2026-10-07 outputs/temperature-probe-2026-10-07 \
  results/grid-2026-08-18 results/stride-2026-08-25 results/image-b-gs-2026-08-28 \
  results/verifier-robustness results/gemini37-screen-2026-08-28 \
  results/gemini37-image-gs-2026-09-01 results/gemini37-fourth-cell \
  results/gemini38-screen-2026-09-04 results/modality-bridge-2026-10-07 \
  | tar -x -C "$DEST"
# Gitignored prepared passes (read only from the shared checkout).
for d in outputs/gemini37-image-gs-2026-09-01/scoring \
         outputs/modality-bridge-2026-10-07/g3-text/scoring \
         outputs/modality-bridge-2026-10-07/g3-image/scoring \
         outputs/modality-bridge-2026-10-07/g37-text/scoring \
         outputs/modality-bridge-2026-10-07/g37-image/scoring \
         outputs/modality-bridge-2026-10-07/g37-image-cache/scoring \
         outputs/modality-bridge-2026-10-07/g3-text-temp1/scoring \
         outputs/modality-bridge-2026-10-07/g3-image-temp1/scoring; do
  mkdir -p "$DEST/$d"
  cp -a "$SHARED/$d/." "$DEST/$d/"
done
# The venv's interpreter is shared; scripts call `.venv/bin/python` relative
# to the repository root, so give the copy a real path to it.
mkdir -p "$DEST/.venv/bin"
ln -sf "$SHARED/.venv/bin/python" "$DEST/.venv/bin/python"
printf 'code %s\ndata %s\n' "$(git -C "$REPO" rev-parse "$CODE_REF")" \
  "$(git -C "$REPO" rev-parse "$DATA_REF")" > "$DEST/.source-commits"
