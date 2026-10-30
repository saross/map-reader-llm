#!/usr/bin/env bash
# =============================================================================
# stage.sh -- one stage of the S166 clipped tile-MCC job, on sapphire
# =============================================================================
# Runs in ~/scratch/clipped-tile-mcc-2026-10-30. Each stage writes its own pid
# file from inside the job, a state file (RUNNING, then DONE or FAILED <rc>)
# and a log, so a watcher reads terminal state or log staleness, never pgrep.
#
#   copy        whole-tree copy of REF (git archive; real files) at wt/, the
#               venv linked (an interpreter, not data)
#   prepare     k_ladder_clipped_cells.py prepare (area gate, clip, pre-gate)
#   evals       every jobs.tsv line through evaluate_detections.py, at most
#               $WORKERS at once, single-threaded each
#   collect     k_ladder_clipped_cells.py collect (the evaluation gate)
#   mcc         k_ladder_mcc_test.py on the clipped inventory
#   mcb         k_ladder_mcb.py --registry on the clipped ladders
#   report      k_ladder_clipped_cells.py report
#
# Usage: stage.sh <stage> [REF]          (launched detached; see the record)
# No API calls.
# =============================================================================
set -uo pipefail
STAGE=$1; REF=${2:-}
ROOT=$HOME/scratch/clipped-tile-mcc-2026-10-30
WT=$ROOT/wt; LOGS=$ROOT/logs; OUT=results/k-ladder-2026-09-12/clipped-mcc-2026-10-30
WORKERS=${WORKERS:-6}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg
mkdir -p "$LOGS"; echo $$ > "$LOGS/$STAGE.pid"; echo RUNNING > "$LOGS/$STAGE.state"
date -u +%FT%TZ > "$LOGS/$STAGE.started"
finish() { echo "$(date -u +%FT%TZ) rc=$1" >> "$LOGS/$STAGE.times"
           if [ "$1" -eq 0 ]; then echo DONE > "$LOGS/$STAGE.state"
           else echo "FAILED $1" > "$LOGS/$STAGE.state"; fi; exit "$1"; }
PY=$WT/.venv/bin/python
case $STAGE in
  copy)
    [ -e "$WT" ] && { echo "refusing: $WT exists"; finish 2; }
    mkdir -p "$WT"
    git -C "$HOME/Code/map-reader-llm" archive "$REF" | tar -x -C "$WT" || finish 3
    ln -s "$HOME/Code/map-reader-llm/.venv" "$WT/.venv"
    printf 'ref %s\n' "$(git -C "$HOME/Code/map-reader-llm" rev-parse "$REF")" > "$WT/.source-commit"
    echo "files: $(find "$WT" -type f | wc -l); symlinks: $(find "$WT" -type l | wc -l)"
    finish 0 ;;
  prepare|collect|report)
    cd "$WT" || finish 9
    "$PY" scripts/k_ladder_clipped_cells.py "$STAGE"; finish $? ;;
  evals)
    cd "$WT" || finish 9
    : > "$LOGS/evals-times.tsv"; mkdir -p "$LOGS/evals"
    run_one() {
      local cell=$1 argv=$2 t0 t1 rc name
      name=$(basename "$cell")
      mapfile -t ARGS < <(printf '%s' "$argv" | "$PY" -c \
        'import json,sys; print("\n".join(json.load(sys.stdin)))')
      t0=$(date +%s.%N)
      "$PY" scripts/evaluate_detections.py "${ARGS[@]}" > "$LOGS/evals/$name.log" 2>&1
      rc=$?; t1=$(date +%s.%N)
      printf '%s\t%s\t%s\n' "$cell" "$rc" "$(echo "$t1 - $t0" | bc)" >> "$LOGS/evals-times.tsv"
      return $rc
    }
    export -f run_one; export PY LOGS
    fails=0
    while IFS=$'\t' read -r cell argv; do
      [ -z "$cell" ] && continue
      while [ "$(jobs -rp | wc -l)" -ge "$WORKERS" ]; do sleep 2; done
      run_one "$cell" "$argv" &
    done < "$OUT/jobs.tsv"
    for pid in $(jobs -rp); do wait "$pid" || fails=$((fails + 1)); done
    wait
    bad=$(awk -F'\t' '$2 != 0' "$LOGS/evals-times.tsv" | wc -l)
    echo "evaluations: $(wc -l < "$LOGS/evals-times.tsv") run, $bad non-zero"
    [ "$bad" -eq 0 ] || finish 4
    finish 0 ;;
  mcc)
    cd "$WT" || finish 9
    "$PY" scripts/k_ladder_mcc_test.py --ladders "$OUT/ladders-clipped.json" \
      --conditions "$OUT/tiering-input/run-conditions.json" \
      --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \
      --output-dir "$OUT/mcc-test"; finish $? ;;
  mcb)
    cd "$WT" || finish 9
    "$PY" scripts/k_ladder_mcb.py --registry "$OUT/mcb-registry.json" \
      --output-dir "$OUT/mcb"; finish $? ;;
  *) echo "unknown stage $STAGE"; finish 64 ;;
esac
