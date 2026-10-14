#!/usr/bin/env bash
# W2-1 replay 01: the Gemini 3.7 image 55-map K = 1 / K = 3 sweep and
# materialisation (generating commit e0f9a4d03), replayed in a detached
# worktree at b9d4032bb. b9d4032bb carries e0f9a4d03's code unchanged
# (scripts/gemini37_image_55map_r2.py at 7ed157a32's blob) plus the
# verifier inputs (crops_k{1,3}/candidate_manifest.json and
# verify_k{1,3}_arm{1,2}/probabilities.json) that were on disk but
# untracked when e0f9a4d03 ran and were committed 35 minutes later.
# Zero API: the sweep and materialise stages read local JSON/GeoJSON only.
# Outputs overwrite the tracked files in the replay tree; compare with
# git status / cmp against `git show e0f9a4d03:<path>` afterwards.
set -euo pipefail
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-b9d4032bb
PY=~/Code/map-reader-llm/.venv/bin/python
cd "$TREE"
echo "start $(date -u +%FT%TZ) HEAD $(git rev-parse HEAD)"
"$PY" scripts/gemini37_image_55map_r2.py --stage sweep --workers 2
echo "sweep done $(date -u +%FT%TZ)"
"$PY" scripts/gemini37_image_55map_r2.py --stage materialise
echo "materialise done $(date -u +%FT%TZ)"
git status --porcelain
echo "end $(date -u +%FT%TZ)"
