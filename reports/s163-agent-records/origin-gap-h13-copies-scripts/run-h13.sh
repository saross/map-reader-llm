#!/usr/bin/env bash
# run-h13.sh -- D62 (1) step 1: re-score the H13 chain in three trees.
#
#   old   git archive of origin/main (the pre-fix route), once
#   new1  the branch clone at the fix commit
#   new2  git archive of the fix commit (a second, independent run)
#
# Jobs per tree: the tier-0 aggregation sweep, the K-sensitivity
# diagnostic, the tile-size x overlap grid, and the overlap analysis on
# the committed prepared sets; new1/new2 also rewrite the prepared sets
# on today's code (reprep.py) and re-run the overlap analysis on them.
# At most four processes at once (the brief's worker budget). Each job
# writes its log, and its exit code to pids/<job>.rc; the driver writes
# its own pid file and, last, pids/run_h13.done.
set -u
BASE=~/scratch/origin-gap-h13-copies-2026-10-13
PY=~/Code/map-reader-llm/.venv/bin/python
CLONE=~/scratch/d60-1-input-vintage-2026-10-12/repo
echo $$ > "$BASE/pids/run_h13.pid"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

declare -A TREE=( [old]="$BASE/trees/old" [new1]="$CLONE" [new2]="$BASE/trees/new2" )

job() {  # $1 = job name, $2 = tree dir, rest = command
  local name=$1 tree=$2; shift 2
  ( cd "$tree" && "$@" ) > "$BASE/logs/$name.log" 2>&1 < /dev/null
  echo $? > "$BASE/pids/$name.rc"
}

launch() {  # throttle to four concurrent jobs
  while [ "$(jobs -rp | wc -l)" -ge 4 ]; do wait -n; done
  job "$@" &
}

for t in old new1 new2; do
  tree=${TREE[$t]}; out=$BASE/out/$t; mkdir -p "$out"
  launch "$t-tier0" "$tree" $PY scripts/h13_aggregation_sweep.py \
      --scoring-dir "$tree/outputs/h13/scoring" --output-dir "$out/tier0"
  launch "$t-ksens" "$tree" $PY scripts/h13_k_sensitivity.py --output-dir "$out/ksens"
  launch "$t-tilesize" "$tree" $PY scripts/h13_tilesize_overlap_grid.py \
      --output-dir "$out/tilesize"
  launch "$t-overlap" "$tree" $PY scripts/h13_overlap_analysis.py \
      --scoring-dir "$tree/outputs/h13/scoring" --output-dir "$out/overlap"
  if [ "$t" != old ]; then
    launch "$t-reprep" "$tree" bash "$BASE/bin/reprep-overlap.sh" "$t" "$tree"
  fi
done
wait
date -u +%FT%TZ > "$BASE/pids/run_h13.done"
