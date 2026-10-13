#!/usr/bin/env bash
# run-merged.sh -- re-run the H13 chain (NEW) and the library-copy
# measurement at the branch head after main (with PR #33) was merged in,
# twice: new3 in the clone, new4 in a git archive of the head. Four
# processes at most; per-job logs and exit codes; pid file; done marker.
set -u
BASE=~/scratch/origin-gap-h13-copies-2026-10-13
PY=~/Code/map-reader-llm/.venv/bin/python
CLONE=~/scratch/d60-1-input-vintage-2026-10-12/repo
SC=~/cc-scratch/bootstrap-cis
echo $$ > "$BASE/pids/run_merged.pid"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
declare -A TREE=( [new3]="$CLONE" [new4]="$BASE/trees/new4" )
job() {
  local name=$1 tree=$2; shift 2
  ( cd "$tree" && "$@" ) > "$BASE/logs/$name.log" 2>&1 < /dev/null
  echo $? > "$BASE/pids/$name.rc"
}
launch() {
  while [ "$(jobs -rp | wc -l)" -ge 4 ]; do wait -n; done
  job "$@" &
}
for t in new3 new4; do
  tree=${TREE[$t]}; out=$BASE/out/$t; mkdir -p "$out" "$BASE/copies/$t"
  launch "$t-tier0" "$tree" $PY scripts/h13_aggregation_sweep.py \
      --scoring-dir "$tree/outputs/h13/scoring" --output-dir "$out/tier0"
  launch "$t-ksens" "$tree" $PY scripts/h13_k_sensitivity.py --output-dir "$out/ksens"
  launch "$t-tilesize" "$tree" $PY scripts/h13_tilesize_overlap_grid.py \
      --output-dir "$out/tilesize"
  launch "$t-overlap" "$tree" $PY scripts/h13_overlap_analysis.py \
      --scoring-dir "$tree/outputs/h13/scoring" --output-dir "$out/overlap"
  launch "$t-reprep" "$tree" bash "$BASE/bin/reprep_overlap.sh" "$t" "$tree"
  for s in diversity-track1 diversity-track2 pes p3a; do
    launch "copies-$t-$s" "$BASE" $PY "$BASE/bin/measure_copies.py" --code "$tree" \
      --data "$CLONE" --sc "$SC" --march-sweeps "$BASE/march-sweeps" \
      --section "$s" --out "$BASE/copies/$t/$s.json"
  done
done
wait
date -u +%FT%TZ > "$BASE/pids/run_merged.done"
