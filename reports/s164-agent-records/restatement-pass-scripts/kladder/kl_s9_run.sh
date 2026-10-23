#!/usr/bin/env bash
# =============================================================================
# kl_s9_run.sh -- re-score the eight S9 cells in two independent clones
# =============================================================================
# K-ladder lane, S164 restatement pass, part 1 step 4. Runs clone A's eight
# evaluations, then clone B's, each a fresh interpreter, one at a time (this
# script plus one scorer: two processes). Writes a pid file first; logs per
# cell and a TSV of wall seconds; reads the kernel bad-page count before and
# after. No API calls.
# Usage: kl_s9_run.sh   (launched detached; see the lane's launch.sh rule)
# =============================================================================
L=$HOME/scratch/s164-restate-2026-10-15/lane-kladder
PY=$HOME/Code/map-reader-llm/.venv/bin/python
P=$L/p1/s9; mkdir -p "$P/logs"
echo $$ > "$L/logs/s9run.pid"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1
echo "before $(journalctl -k -b 2>/dev/null | grep -c 'Bad page state')" > "$P/bad-page.txt"
for R in A B; do
  C=$L/p1/s9$R
  : > "$P/times-$R.tsv"
  while IFS=$'\t' read -r cell argv; do
    mapfile -t ARGS < <(printf '%s' "$argv" | $PY -c 'import json,sys; print("\n".join(json.load(sys.stdin)))')
    t0=$(date +%s.%N)
    ( cd "$C" && "$PY" scripts/evaluate_detections.py "${ARGS[@]}" ) > "$P/logs/$R-$(basename "$cell").log" 2>&1
    rc=$?
    t1=$(date +%s.%N)
    printf '%s\t%s\t%s\n' "$cell" "$rc" "$(echo "$t1 - $t0" | bc)" >> "$P/times-$R.tsv"
  done < "$P/cmds-$R.tsv"
done
echo "after $(journalctl -k -b 2>/dev/null | grep -c 'Bad page state')" >> "$P/bad-page.txt"
echo DONE > "$P/state"
