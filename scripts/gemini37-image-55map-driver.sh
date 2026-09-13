#!/bin/bash
# Gemini 3.7 image proposer at deployment scale: storm-resilient K = 3 driver.
#
# Card: planning/gemini37-image-55map-2026-09-13.md (§ 2 the cells, § 5 run
# order and gates). Pattern: outputs/gemini37-image-gs-2026-09-01/
# image-gs-recovery-driver.sh, which survived the daily flex-storm window on
# the Gold Standard (GS) image run.
#
# Each pass is attempted as a main run, then completed by recovery fragments
# in rounds: every round rebuilds the pass's residual manifest (the pinned
# manifest minus every tile completed in the main file or ANY prior fragment)
# and re-runs only the residue. If a round clears less than a tenth of its
# starting residue the queue is storm-bound, so the driver naps 40 minutes
# before trying again. Fragments land in run_<N>_recovery_rd<R> directories,
# which the union chain folds into pass N.
#
# Invocation is byte-identical to the GS image run's proposer (that run's
# driver, lines 64-71): no --use-cache, so Gemini's IMPLICIT prefix caching
# does the work it did there (79-80 per cent of input tokens cached).
#
# PASS-SCALE GATES (the operator applies these; the driver only records):
#   * audited cost of pass 1 must not exceed US$110
#     (scripts/audit_proposer_cost.py, NOT run.meta.json's cost_estimate)
#   * running audited total must not exceed US$420
#   * cached share of input tokens on pass 1 must be at least 0.70
#
# Usage (from the repository root, on sapphire):
#     nohup bash scripts/gemini37-image-55map-driver.sh 1 > /dev/null 2>&1 &
#     nohup bash scripts/gemini37-image-55map-driver.sh 1 2 3 > /dev/null 2>&1 &
#
# Passes named on the command line run SEQUENTIALLY: concurrent Gemini 3.7
# runs inflate each other's 503 retries in the flex queue (PI rule,
# 2026-08-30, recorded in planning/gemini37-image-gs-2026-08-30.md).
#
# Created: 2026-09-13
# Author: Shawn Ross, Claude Code
# Licence: Apache 2.0

set -u

cd "$HOME/worktrees/map-reader-llm/claude-image55" || exit 1
ulimit -n 8192 || true

PY=.venv/bin/python
OUT=outputs/gemini37-image-55map-2026-09-13
CELL=$OUT/g384_ov192_55map_g37img
MANIFEST=inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json
TILES=inputs/tiles_384_ov192_55maps
CONFIG=prompts/configs/detect_brief-text-image.json
LOG=$OUT/driver.log
WORKERS=${WORKERS:-150}
MAX_ROUNDS=${MAX_ROUNDS:-24}

mkdir -p "$CELL"
PASSES=${*:-1}

# Residual tiles for one pass: the pinned manifest minus every tile any
# fragment of that pass completed.
residual_for() {
  $PY - "$1" <<'EOF'
import glob
import json
import sys

run = sys.argv[1]
cell = "outputs/gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img"
done: set[str] = set()
for tj in (glob.glob(f"{cell}/run_{run}/*.tiles.json")
           + glob.glob(f"{cell}/run_{run}_recovery*/*.tiles.json")):
    done |= set(json.load(open(tj))["completed"])
manifest = set(json.load(
    open("inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json")))
resid = sorted(manifest - done)
json.dump(resid, open(
    f"outputs/gemini37-image-55map-2026-09-13/residual_run_{run}.json", "w"))
print(len(resid))
EOF
}

for r in $PASSES; do
  echo "PASS $r: start $(date -Is)" >> "$LOG"

  # The main pass, if it has not already been attempted.
  if [ ! -d "$CELL/run_$r" ]; then
    echo "PASS $r: main run $(date -Is)" >> "$LOG"
    $PY scripts/4_detect_mounds_batch.py \
      --config "$CONFIG" \
      --manifest "$MANIFEST" \
      --tiles-dir "$TILES" \
      --output-dir "$CELL/run_$r" \
      --mode realtime --service-tier flex --temperature 0.7 \
      --model gemini-3.7-flash --thinking-level low --workers "$WORKERS" \
      >> "$LOG" 2>&1
  else
    echo "PASS $r: main run already present, going straight to recovery" \
      >> "$LOG"
  fi

  # Recovery rounds until the residue clears or the round budget runs out.
  round=0
  while true; do
    n=$(residual_for "$r")
    echo "PASS $r: round $round residual $n $(date -Is)" >> "$LOG"
    if [ "$n" -eq 0 ]; then
      echo "PASS $r COMPLETE $(date -Is)" >> "$LOG"
      break
    fi
    if [ "$round" -ge "$MAX_ROUNDS" ]; then
      echo "PASS $r GAVE UP at $n residual $(date -Is)" >> "$LOG"
      break
    fi
    round=$((round + 1))
    start_n=$n
    $PY scripts/4_detect_mounds_batch.py \
      --config "$CONFIG" \
      --manifest "$OUT/residual_run_$r.json" \
      --tiles-dir "$TILES" \
      --output-dir "$CELL/run_${r}_recovery_rd${round}" \
      --mode realtime --service-tier flex --temperature 0.7 \
      --model gemini-3.7-flash --thinking-level low --workers "$WORKERS" \
      >> "$LOG" 2>&1
    end_n=$(residual_for "$r")
    echo "PASS $r: round $round $start_n -> $end_n $(date -Is)" >> "$LOG"
    if [ $((start_n - end_n)) -lt $((start_n / 10)) ]; then
      echo "PASS $r: storm-bound, napping 40m $(date -Is)" >> "$LOG"
      sleep 2400
    fi
  done
done

echo "DRIVER FINISHED passes [$PASSES] $(date -Is)" >> "$LOG"
