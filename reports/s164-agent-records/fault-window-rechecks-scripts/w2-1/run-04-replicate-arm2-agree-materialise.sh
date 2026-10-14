#!/usr/bin/env bash
# W2-1 replay 04: the arm 2 K = 5 batch replicate's agree and materialise
# stages (generating commit 0569b0d2f), replayed in a detached tree at
# 0569b0d2f. The driver is the first committed copy (2fcc7ef3e, committed
# 18 minutes after 0569b0d2f as "the four-stage script that produced
# every number"), dropped into the tree untracked, with ONE line changed:
# the hard-coded PROJECT_ROOT ("/home/shawn/Code/map-reader-llm") becomes
# Path(__file__).resolve().parents[3], exactly 55ff8a02e's later fix, so
# the replay reads and writes its own tree and not sapphire's shared
# checkout (patch-replicate_k5_arm2-root.diff). It imports
# scripts/gemini37_image_55map_r2.py at 0569b0d2f (blob 08bf247a59).
# Zero API.
set -euo pipefail
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-0569b0d2f
PY=~/Code/map-reader-llm/.venv/bin/python
S=results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20/replicate_k5_arm2.py
cd "$TREE"
echo "start $(date -u +%FT%TZ) HEAD $(git rev-parse HEAD)"
"$PY" "$S" --stage agree
echo "agree done $(date -u +%FT%TZ)"
"$PY" "$S" --stage materialise --workers 2
echo "materialise done $(date -u +%FT%TZ)"
git status --porcelain
echo "end $(date -u +%FT%TZ)"
