#!/usr/bin/env bash
# run-probe.sh <label> <cache dir> -- one run of probe_w27_scope.py in the W2.7 clone.
B=~/scratch/origin-gap-h13-copies-2026-10-13
C=~/scratch/d60-w27-fastscorer-2026-10-12/repo
echo $$ > $B/w27/pids/probe-$1.pid
cd $C || exit 1
export REPO=$C PYTHONPATH=$C PYTHONPYCACHEPREFIX=$B/w27/pyc-probe-$1 W27_CACHE=$2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "START $1 $(date -u +%FT%TZ) head $(git rev-parse HEAD)"
~/Code/map-reader-llm/.venv/bin/python $B/bin/probe_w27_scope.py --out $B/w27/probe-$1.json
echo $? > $B/w27/pids/probe-$1.rc
echo "EXIT $1 $(date -u +%FT%TZ)"
