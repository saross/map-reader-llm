#!/usr/bin/env bash
# W2-1 replay 03: the declared five-test family
# tests_IMG-ARM2-K3-carried.json (generating commit 392a06933), replayed
# in the b9d4032bb tree, whose driver blob (70ee84c4a2), cell detections,
# cells_manifest and comparator inputs equal 392a06933's. Run 01's
# regenerated files are first copied aside and the tracked tree restored,
# so the tests read exactly the committed detections. 10,000 permutations,
# seed 42 (constants in the driver). Run twice, under two PYTHONHASHSEED
# values, to show the output does not depend on the hash seed. Zero API.
set -euo pipefail
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-b9d4032bb
OUT=~/scratch/s164-fw-recheck-2026-10-14/w2-1-out
PY=~/Code/map-reader-llm/.venv/bin/python
F=results/gemini37-image-55map-2026-09-13/tests_IMG-ARM2-K3-carried.json
cd "$TREE"
echo "start $(date -u +%FT%TZ) HEAD $(git rev-parse HEAD)"
git checkout -- results/gemini37-image-55map-2026-09-13
git status --porcelain
for seed in 0 12345; do
  echo "== PYTHONHASHSEED=$seed $(date -u +%FT%TZ)"
  PYTHONHASHSEED=$seed "$PY" scripts/gemini37_image_55map_r2.py --stage tests
  cp "$F" "$OUT/tests_IMG-ARM2-K3-carried.hashseed$seed.json"
  sha256sum "$F"
done
git show 392a06933:"$F" | sha256sum
git status --porcelain
echo "end $(date -u +%FT%TZ)"
