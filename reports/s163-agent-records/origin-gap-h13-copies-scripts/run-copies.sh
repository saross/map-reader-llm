#!/usr/bin/env bash
# run-copies.sh -- D62 (1) step 2: measure the library copies' fix, arm by
# arm, with three code trees (new1 = the branch clone, new2 = git archive
# of the branch head, old = git archive of origin/main) reading the same
# inputs. At most four processes; per-job logs and exit codes; the
# driver writes its own pid file and, last, pids/run_copies.done.
set -u
BASE=~/scratch/origin-gap-h13-copies-2026-10-13
PY=~/Code/map-reader-llm/.venv/bin/python
CLONE=~/scratch/d60-1-input-vintage-2026-10-12/repo
SC=~/cc-scratch/bootstrap-cis
echo $$ > "$BASE/pids/run_copies.pid"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
declare -A CODE=( [new1]="$CLONE" [new2]="$BASE/trees/code-new2" [old]="$BASE/trees/code-old" )
job() {  # $1 = job name, rest = command
  local name=$1; shift
  ( cd "$BASE" && "$@" ) > "$BASE/logs/$name.log" 2>&1 < /dev/null
  echo $? > "$BASE/pids/$name.rc"
}
launch() {
  while [ "$(jobs -rp | wc -l)" -ge 4 ]; do wait -n; done
  job "$@" &
}
for t in new1 new2 old; do
  mkdir -p "$BASE/copies/$t"
  for s in diversity-track1 diversity-track2 pes p3a; do
    launch "copies-$t-$s" $PY "$BASE/bin/measure_copies.py" --code "${CODE[$t]}" \
      --data "$CLONE" --sc "$SC" --march-sweeps "$BASE/march-sweeps" \
      --section "$s" --out "$BASE/copies/$t/$s.json"
  done
done
wait
date -u +%FT%TZ > "$BASE/pids/run_copies.done"
