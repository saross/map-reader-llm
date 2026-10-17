#!/usr/bin/env bash
# Two independent runs of the twin origin-route driver (D65 (4)): each in its
# own fresh sparse clone at REF, all 19 grid-common union twins, origin-sheet
# source_tile, the committed evaluate_detections.py arguments. Sequential (each
# run is the driver plus one evaluate_detections.py child). Lane-uplift, S164.
# Usage: twins_both.sh <ref>
LANE=$HOME/scratch/s164-restate-2026-10-15/lane-uplift
PY=$HOME/Code/map-reader-llm/.venv/bin/python
for run in A B; do
  rm -rf "$LANE/twins/$run"; mkdir -p "$LANE/twins/$run"
  "$LANE/bin/twin_setup.sh" "$1" "$LANE/twins/$run/repo" || { echo "$run setup failed"; continue; }
  t0=$(date +%s)
  "$PY" -B "$LANE/bin/twin_origin_driver.py" --repo "$LANE/twins/$run/repo" \
    --record "$LANE/twins/$run/record.json" --source-tile origin \
    > "$LANE/logs/twins-$run.log" 2>&1
  echo "$run rc $? seconds $(( $(date +%s) - t0 ))"
  git -C "$LANE/twins/$run/repo" status --porcelain --untracked-files=all \
    > "$LANE/twins/$run/status-after.txt"
done
echo BOTH_DONE
