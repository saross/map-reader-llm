#!/usr/bin/env bash
# Make a disposable, real-file copy of the paths the chain reads, at a ref.
# Usage: mkcopy.sh <ref> <dest>
set -euo pipefail
REF=$1; DEST=$2
REPO=$HOME/scratch/scorer-restatement-sweep-2026-10-12/repo
mkdir -p "$DEST"
git -C "$REPO" archive "$REF" -- \
  scripts config.py pyproject.toml pytest.ini \
  inputs/vectors inputs/grid-2026-08-18 inputs/stride-phaseb-2026-08-25 inputs/image-b-gs-2026-08-28 \
  outputs/grid-2026-08-18 outputs/stride-phaseb-2026-08-25 outputs/stride-phasec-2026-08-25 \
  outputs/image-b-gs-2026-08-28 outputs/era1-pv-stage-d/384-consensus-text-high \
  results/grid-2026-08-18 results/stride-2026-08-25 results/image-b-gs-2026-08-28 \
  results/verifier-robustness \
  | tar -x -C "$DEST"
git -C "$REPO" rev-parse "$REF" > "$DEST/.source-commit"
