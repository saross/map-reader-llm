#!/usr/bin/env bash
# NOTE (added after the run): this replay used the FIRST hashseed_search.py,
# which spawned interpreters under -I (implies -E, so PYTHONHASHSEED was
# ignored); its "seed 294" match was chance and the re-run stayed
# field-identical only (cmp-07-*.json). Superseded by replay 09.
# W2-1 replay 07: byte-for-byte reproduction of the arm 2 replicate's
# tests.json (7351bcce8). Replay 05 showed the file field-identical under
# two hash seeds with only the key order of n_detections / tile_confusion
# moving. Here hashseed_search.py finds a PYTHONHASHSEED whose set order
# matches the committed one, and the tests stage is re-run under it (same
# tree at 7351bcce8, same root-patched driver as replay 04). Zero API.
set -euo pipefail
REC=~/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w2-1
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-0569b0d2f
PY=~/Code/map-reader-llm/.venv/bin/python
H=results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20
cd "$TREE"
echo "start $(date -u +%FT%TZ) HEAD $(git rev-parse HEAD)"
SEED=$("$PY" "$REC/hashseed_search.py" --tree "$TREE" --spec "7351bcce8:$H/tests.json" | tee /dev/stderr | sed -n "s/^MATCH seed //p")
echo "seed found: $SEED"
SEEDS="$SEED" bash -c "cd $TREE; PYTHONHASHSEED=$SEED $PY $H/replicate_k5_arm2.py --stage tests"
sha256sum "$H/tests.json"
git show 7351bcce8:"$H/tests.json" | sha256sum
"$PY" "$REC/compare_files.py" --tree "$TREE" --out "$REC/cmp-07-replicate-arm2-tests-seed$SEED.json" --pair "7351bcce8:$H/tests.json" --pair "90294a283:$H/tests.json"
echo "end $(date -u +%FT%TZ)"
