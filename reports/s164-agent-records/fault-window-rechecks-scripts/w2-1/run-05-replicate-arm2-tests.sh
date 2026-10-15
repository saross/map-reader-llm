#!/usr/bin/env bash
# W2-1 replay 05: the arm 2 K = 5 replicate's four paired tests
# (tests.json, generating commit 7351bcce8, run on amd-tower), replayed on
# sapphire in the same tree moved to 7351bcce8 (only cca6ccda5, board
# carried-analogue cells the tests never read, lies between). Same
# root-patched driver as replay 04. 10,000 permutations, seed 42. Run under
# two PYTHONHASHSEED values: the driver fills its cell cache from a Python
# set, so the KEY ORDER of n_detections / tile_confusion follows the hash
# seed while no value can. Zero API.
set -euo pipefail
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-0569b0d2f
OUT=~/scratch/s164-fw-recheck-2026-10-14/w2-1-out
PY=~/Code/map-reader-llm/.venv/bin/python
H=results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20
S=$H/replicate_k5_arm2.py
cd "$TREE"
git checkout -- results/
git checkout --detach 7351bcce8
echo "start $(date -u +%FT%TZ) HEAD $(git rev-parse HEAD)"
git status --porcelain
for seed in ${SEEDS:-0 12345}; do
  echo "== PYTHONHASHSEED=$seed $(date -u +%FT%TZ)"
  PYTHONHASHSEED=$seed "$PY" "$S" --stage tests
  cp "$H/tests.json" "$OUT/replicate-arm2-tests.hashseed$seed.json"
  sha256sum "$H/tests.json"
done
git show 7351bcce8:"$H/tests.json" | sha256sum
echo "end $(date -u +%FT%TZ)"
