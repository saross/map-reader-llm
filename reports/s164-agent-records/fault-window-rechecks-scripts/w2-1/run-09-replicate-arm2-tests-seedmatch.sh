#!/usr/bin/env bash
# W2-1 replay 09: redo of replay 07 with the corrected hashseed_search.py
# (replay 07's search ran bare interpreters under -I, which implies -E and
# ignores PYTHONHASHSEED, so its "match" was chance under a random seed and
# the re-run stayed field-identical only; cmp-07-*.json records that).
# Moves the replicate tree back to 7351bcce8, re-creates the root-patched
# 2fcc7ef3e driver (untracked), finds a seed reproducing the committed set
# order, re-runs the tests under it, keeps the output, compares. Zero API.
set -euo pipefail
REC=~/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w2-1
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-0569b0d2f
OUT=~/scratch/s164-fw-recheck-2026-10-14/w2-1-out
PY=~/Code/map-reader-llm/.venv/bin/python
H=results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20
S=$H/replicate_k5_arm2.py
cd "$TREE"
git checkout -- results/
git checkout -q --detach 7351bcce8
git show 2fcc7ef3e:$S | sed "s#^PROJECT_ROOT = Path(\"/home/shawn/Code/map-reader-llm\")\$#PROJECT_ROOT = Path(__file__).resolve().parents[3]#" > "$S"
git show 2fcc7ef3e:$S | diff - "$S" || true
echo "start $(date -u +%FT%TZ) HEAD $(git rev-parse HEAD)"
SEED=$("$PY" "$REC/hashseed_search.py" --tree "$TREE" --spec "7351bcce8:$H/tests.json" | sed -n "s/^MATCH seed //p")
echo "seed found: $SEED"
PYTHONHASHSEED=$SEED "$PY" "$S" --stage tests
cp "$H/tests.json" "$OUT/replicate-arm2-tests.seed$SEED.json"
sha256sum "$H/tests.json"
git show 7351bcce8:"$H/tests.json" | sha256sum
"$PY" "$REC/compare_files.py" --tree "$TREE" --out "$REC/cmp-09-replicate-arm2-tests-seed$SEED.json" --pair "7351bcce8:$H/tests.json" --pair "90294a283:$H/tests.json" || true
git checkout -- results/
rm -f "$S"
echo "end $(date -u +%FT%TZ)"
