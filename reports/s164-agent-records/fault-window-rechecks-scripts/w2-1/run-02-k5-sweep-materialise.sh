#!/usr/bin/env bash
# W2-1 replay 02: the Gemini 3.7 image 55-map K = 5 rung sweep and
# materialisation, replayed at its generating commit 8d800f2d6 (driver
# blob 6be5b37bc9 = 336651e0b, invoked "--rungs 5" per the commit body).
# Inputs crops_k5 and verify_k5_arm{1,2} are tracked at 8d800f2d6
# (bd5de9f80, 4900288ff). The stages merge the K = 5 entries into the
# committed sweeps.json / cells_manifest.json in place, as the original
# run did onto e0f9a4d03's files. Zero API.
set -euo pipefail
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-8d800f2d6
PY=~/Code/map-reader-llm/.venv/bin/python
cd "$TREE"
echo "start $(date -u +%FT%TZ) HEAD $(git rev-parse HEAD)"
"$PY" scripts/gemini37_image_55map_r2.py --stage sweep --rungs 5 --workers 2
echo "sweep done $(date -u +%FT%TZ)"
"$PY" scripts/gemini37_image_55map_r2.py --stage materialise --rungs 5
echo "materialise done $(date -u +%FT%TZ)"
git status --porcelain
echo "end $(date -u +%FT%TZ)"
