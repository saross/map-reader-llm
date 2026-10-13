#!/usr/bin/env bash
# regen1013.sh <run label> -- the W2.7 floors-v2 regeneration of 2026-10-13
# (D62 (1) after PR #44, with PR #33's library via main), one full run.
#
# Stages, in order, each with START/EXIT lines in its own log (the format of
# the 2026-10-12 run_step.sh) and a stop on the first non-zero exit:
#   s6       w27_55map_subset_replicates.py (§ 6) with an EMPTY pass cache
#   gate     floors2_scorer_gate.py against this run's § 6 cells
#   s6b      floors2_55map.py --sims 200 against this run's gate (§ 6b)
#   gs       floors2_gs.py (gold-standard slices)
#   analysis floors2_analyse.py, floors2_rescreen.py, floors2_tables.py
#            (the two GS summary CSVs, which have no committed generator,
#            are carried over from the clone, as on 2026-10-12)
#
# The chain writes its own pid file and, per stage, a .rc file; RC_CHAIN
# holds the chain's final code. Launch detached with all three descriptors
# redirected and nothing after the '&'.
set -u
R=$1
S=/home/shawn/scratch/d60-w27-fastscorer-2026-10-12
CLONE=$S/repo
PY=/home/shawn/Code/map-reader-llm/.venv/bin/python
W=$CLONE/reports/w27-replicate-floors-2026-10-06-scripts
F=$W/floors-v2
O=$S/out/1013-$R
L=$S/logs/1013-$R
P=$S/pids/1013-$R
WORKERS=${WORKERS:-12}
mkdir -p "$O" "$L" "$P"
echo $$ > "$P/chain.pid"
export REPO=$CLONE PYTHONPATH=$CLONE PYTHONPYCACHEPREFIX=$S/pyc-1013-$R
export W27_CACHE=$S/w27-cache-1013-$R
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$CLONE" || { echo 90 > "$P/RC_CHAIN"; exit 90; }
if [ -e "$W27_CACHE" ] && [ -n "$(ls -A "$W27_CACHE")" ]; then
  echo "cache $W27_CACHE is not empty; refusing" > "$L/chain.log"
  echo 91 > "$P/RC_CHAIN"; exit 91
fi
mkdir -p "$W27_CACHE"

stage() {
  # stage <name> <command...>: run one stage with START/EXIT lines and an rc file.
  local name=$1; shift
  {
    echo "START $name $(date -u +%FT%TZ) head $(git rev-parse HEAD)" \
      "lib $(git hash-object scripts/lib_advanced_metrics.py)" \
      "dirty $(git status --porcelain --untracked-files=no | wc -l) cache $W27_CACHE" \
      "workers $WORKERS"
    "$@"
    local rc=$?
    echo "EXIT $name $rc $(date -u +%FT%TZ)"
    echo $rc > "$P/$name.rc"
    return $rc
  } >> "$L/$name.log" 2>&1
}

stage s6 $PY $W/w27_55map_subset_replicates.py --workers "$WORKERS" --out "$O/w27" \
  || { echo 1 > "$P/RC_CHAIN"; exit 1; }
stage gate $PY $F/floors2_scorer_gate.py --workers "$WORKERS" \
  --w27-cells "$O/w27/subset_cells.json" --out "$O/gate" \
  || { echo 2 > "$P/RC_CHAIN"; exit 2; }
stage s6b $PY $F/floors2_55map.py --workers "$WORKERS" --sims 200 \
  --scorer-gate "$O/gate" --out "$O/out55" \
  || { echo 3 > "$P/RC_CHAIN"; exit 3; }
stage gs $PY $F/floors2_gs.py --workers "$WORKERS" --out "$O/outgs" \
  || { echo 4 > "$P/RC_CHAIN"; exit 4; }

analysis() {
  # The floors analysis chain of 2026-10-12 (tools/run_analysis.sh), on this run's outputs.
  mkdir -p "$O/results"
  $PY $F/floors2_analyse.py --out55 "$O/out55" --outgs "$O/outgs" --res "$O/results" \
    || return 11
  cp -a $F/results/gs_validation_summary.csv $F/results/gs_k10_summary.csv "$O/results/"
  $PY $F/floors2_rescreen.py "$O/results" > "$O/rescreen.out" || return 12
  $PY $F/floors2_tables.py "$O/results" > "$O/results/tables.md" || return 13
}
stage analysis analysis || { echo 5 > "$P/RC_CHAIN"; exit 5; }
echo 0 > "$P/RC_CHAIN"
