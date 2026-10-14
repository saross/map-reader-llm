#!/usr/bin/env bash
# W2-1 replay 08 (lower priority): the arm 1 K = 5 batch replicate, each
# file at its generating commit, in the replicate tree:
#   82020b941 agree + materialise -> agreement.json (superseded), sweeps.json,
#             cells_manifest.json, sweep CSV, two detections
#   d1134a707 tests                -> tests.json (field-level + hash seed)
#   321dd4549 agree                -> agreement.json (today's)
# Each commit's own replicate_k5_arm1.py with the ONE-line root patch
# (55ff8a02e's fix). The untracked arm 2 driver copy from replays 04/05/07
# is removed first (it is tracked from 2fcc7ef3e on). Zero API.
set -uo pipefail
REC=~/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w2-1
TREE=~/scratch/s164-fw-recheck-2026-10-14/w2-1-0569b0d2f
OUT=~/scratch/s164-fw-recheck-2026-10-14/w2-1-out
PY=~/Code/map-reader-llm/.venv/bin/python
H=results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20
S=$H/replicate_k5_arm1.py
cd "$TREE"
rm -f results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20/replicate_k5_arm2.py
goto () {  # commit tag
  git checkout -- results/ && git checkout -q --detach "$1" || { echo "CHECKOUT $1 FAILED"; return 1; }
  sed -i "s#^PROJECT_ROOT = Path(\"/home/shawn/Code/map-reader-llm\")\$#PROJECT_ROOT = Path(__file__).resolve().parents[3]#" "$S"
  git diff -- "$S" > "$REC/patch-replicate_k5_arm1-root-$2.diff"
  echo "at $(git rev-parse HEAD) patch lines $(grep -c "^[-+]PROJECT_ROOT" "$REC/patch-replicate_k5_arm1-root-$2.diff") $(date -u +%FT%TZ)"
}
cmp () {  # tag commit files...
  local tag=$1 c=$2; shift 2; local pairs=()
  for f in "$@"; do pairs+=(--pair "$c:$H/$f" --pair "90294a283:$H/$f"); done
  "$PY" "$REC/compare_files.py" --tree "$TREE" --out "$REC/cmp-08$tag.json" "${pairs[@]}"
  echo "compare $tag rc=$?"
  mkdir -p "$OUT/arm1-$tag"; for f in "$@"; do cp --parents "$H/$f" "$OUT/arm1-$tag/"; done
}
goto 82020b941 A
"$PY" "$S" --arm arm1 --stage agree || echo "AGREE A FAILED"
"$PY" "$S" --arm arm1 --stage materialise --workers 2 || echo "MATERIALISE A FAILED"
git status --porcelain
cmp A 82020b941 agreement.json sweeps.json cells_manifest.json sweep_IMG-ARM1-K5-replicate.csv \
  cells/IMG-ARM1-K5-carried-replicate/detections.geojson cells/IMG-ARM1-K5-f1-oracle-replicate/detections.geojson
goto d1134a707 B
for seed in 0 12345; do
  PYTHONHASHSEED=$seed "$PY" "$S" --arm arm1 --stage tests || echo "TESTS B FAILED"
  cp "$H/tests.json" "$OUT/replicate-arm1-tests.hashseed$seed.json"; sha256sum "$H/tests.json"
  "$PY" "$REC/compare_files.py" --tree "$TREE" --out "$REC/cmp-08B-tests-hashseed$seed.json" --pair "d1134a707:$H/tests.json" --pair "90294a283:$H/tests.json"
done
SEED=$("$PY" "$REC/hashseed_search.py" --tree "$TREE" --spec "d1134a707:$H/tests.json" | sed -n "s/^MATCH seed //p")
echo "seed found: $SEED"
if [[ -n "$SEED" ]]; then
  PYTHONHASHSEED=$SEED "$PY" "$S" --arm arm1 --stage tests || echo "TESTS B FAILED"
  "$PY" "$REC/compare_files.py" --tree "$TREE" --out "$REC/cmp-08B-tests-seed$SEED.json" --pair "d1134a707:$H/tests.json" --pair "90294a283:$H/tests.json"
fi
goto 321dd4549 C
"$PY" "$S" --arm arm1 --stage agree || echo "AGREE C FAILED"
cmp C 321dd4549 agreement.json
git status --porcelain
echo "end $(date -u +%FT%TZ)"
